"""Génère les pages HTML (anglais à la racine, français sous fr/) et les données du site Lisa Cirenza.

Usage : python3 -I outils/generer.py <racine-site> [--liens html|propres] [--apercu]
  propres : liens absolus sans .html (Vercel, cleanUrls) — par défaut
  html    : liens relatifs avec .html (aperçu publié, ouverture locale)
"""
import datetime as DT
import html as H
import json
import math
import re
import sys
from pathlib import Path
from urllib.parse import quote

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
import catalogue as CAT  # noqa: E402
import contenu as C  # noqa: E402
import horaires as HOR  # noqa: E402
import seo as SEO  # noqa: E402
import retraites as R  # noqa: E402

SITE = Path(sys.argv[1]).resolve()
MODE = sys.argv[sys.argv.index("--liens") + 1] if "--liens" in sys.argv else "propres"
APERCU = "--apercu" in sys.argv
MED = json.loads((ICI / "medias.json").read_text())
VERSION = "6"
AUJ = DT.date.today()
# Horaires de l'Espace : une seule source, assets/data/horaires.json (futures collections Wix « Horaires » et « Exceptions »)
HEURES = HOR.charger(SITE)
for _l in ("en", "fr"):
    C.T[_l]["horaires_lignes"] = HOR.lignes(HEURES, _l)
    C.T[_l]["horaires_court"] = HOR.court(HEURES, _l)
# Base maîtresse des œuvres : Artwork Archive. Son export, une fois fusionné (outils/artwork_archive.py),
# s'applique par-dessus catalogue.py.
AA = json.loads((ICI / "artwork_archive.json").read_text()) if (ICI / "artwork_archive.json").exists() else {}
MAQUETTE = True  # au lancement : False (et retirer X-Robots-Tag de vercel.json)
AFFICHER_PRIX = True  # brief de Lisa : « prices where shown » ; les prix connus d'Artwork Archive s'affichent, les autres restent sur demande
# Côté de la maison de chaque page : l'atelier (Lisa Cirenza Fine Art, artiste-auteur) ou l'Espace (SAS)
UNIVERS = {"oeuvres": "atelier", "salle": "atelier", "artiste": "atelier", "parcours": "atelier", "presse": "atelier",
           "studio": "atelier", "espace": "espace", "cours": "espace", "cours_prives": "espace", "horaires": "espace", "evenements": "espace", "retraites": "espace",
           "pip": "espace", "encaustics": "espace", "salon_the": "espace", "cosessions": "espace", "expositions": "espace",
           "inscription_pip": "espace", "inscription_encaustics": "espace", "conditions": "espace", "recherche": "maison",
           "accueil": "maison", "boutique": "maison", "contact": "maison", "404": "maison"}
SITE_URL = "https://cirenza-maquette.vercel.app"
LANGS = ("en", "fr")


def e(s):
    return H.escape(str(s), quote=True)


def L(lang, d):
    """Choisit la langue dans un dict {en, fr} (ou renvoie la valeur telle quelle)."""
    if isinstance(d, dict) and lang in d:
        return d[lang]
    return d


def fmt(x, lang):
    s = str(int(x)) if float(x).is_integer() else str(x)
    return s.replace(".", ",") if lang == "fr" else s


# ================================================================ œuvres
SERIES = {s["id"]: s for s in CAT.SERIES}
ORDRE = [s["id"] for s in CAT.SERIES]
LEAD = "record-of-time"  # la série actuelle, en tête (brief de Lisa) ; les autres vont dans l'Archive
ARCHIVE = [sid for sid in ORDRE if SERIES[sid].get("archive")]
OEUVRES = {}
LISTES = {}


def ajouter(o, sid):
    oid = o["id"]
    m = MED["oeuvres"][oid]
    w, h = m["1600"]
    ratio = w / h
    hcm = lcm = None
    if o.get("dims"):
        a, b = o["dims"]
        longue, courte = max(a, b), min(a, b)
        if abs(w - h) / max(w, h) < 0.04:
            hcm, lcm = a, b
        elif w > h:
            hcm, lcm = courte, longue
        else:
            hcm, lcm = longue, courte
    OEUVRES[oid] = {
        "id": oid, "titre": o.get("titre"), "series": [sid], "src": o,
        "dims": o.get("dims"), "hcm": hcm, "lcm": lcm, "profondeur": o.get("profondeur"),
        "technique": o.get("technique"), "edition": o.get("edition"), "annee": o.get("annee"),
        "statut": o.get("statut"), "texte": o.get("texte"), "source": o.get("source"),
        "inventaire": None, "prix": None,
        "ratio": round(ratio, 4), "t": {k: m[k] for k in ("640", "1600")}, "loupe": "hd" in m,
        "fond": m["fond"], "accent": m["accent"], "dominante": m["dominante"],
        "alt": o["alt"], "situation": bool(o.get("photo_situation")), "a_confirmer": bool(o.get("image_a_confirmer")),
        "dims_a_verifier": bool(o.get("dims_a_verifier")),
    }


for s in CAT.SERIES:
    LISTES[s["id"]] = []
    for o in s["oeuvres"]:
        ajouter(o, s["id"])
        LISTES[s["id"]].append(o["id"])
for sid in ORDRE:
    for oid in SERIES[sid].get("aussi", []):
        OEUVRES[oid]["series"].append(sid)
        LISTES[sid].append(oid)
for o in CAT.HORS_SERIE:
    ajouter(o, "hors-serie")
    LISTES["hors-serie"] = [o["id"]]


def appliquer_artwork_archive():
    """Les données d'Artwork Archive l'emportent sur le relevé de catalogue.py."""
    for oid, d in AA.items():
        o = OEUVRES.get(oid)
        if not o:
            continue
        for k in ("titre", "annee", "statut", "inventaire", "profondeur"):
            if d.get(k):
                o[k] = d[k]
        if d.get("technique_en"):
            o["technique"] = {"en": d["technique_en"], "fr": (o["technique"] or {}).get("fr") or d["technique_en"]}
        if d.get("edition_en"):
            o["edition"] = {"en": d["edition_en"], "fr": (o["edition"] or {}).get("fr") or d["edition_en"]}
        if d.get("dims"):
            h, l = d["dims"]
            o["dims"], o["hcm"], o["lcm"] = (h, l), h, l
        if d.get("prix") and AFFICHER_PRIX:
            o["prix"] = (d["prix"], d.get("devise", "EUR"))


appliquer_artwork_archive()
OEUVRES["cuban-chess"]["dims"] = (42, 29.7)
OEUVRES["cuban-chess"]["hcm"], OEUVRES["cuban-chess"]["lcm"] = 42, 29.7
OEUVRES["cuban-chess"]["dims_txt_special"] = "A3"


def titre(o, lang):
    return o["titre"] or C.T[lang]["titre_a_completer"]


def dims_txt(o, lang):
    if not o["dims"]:
        return None
    a, b = o["dims"]
    if o.get("dims_txt_special"):
        return f"A3 ({fmt(29.7, lang)} × 42 cm)"
    if o.get("profondeur"):
        return f"{fmt(a, lang)} × {fmt(b, lang)} × {fmt(o['profondeur'], lang)} cm"
    return f"{fmt(a, lang)} × {fmt(b, lang)} cm"


def technique_txt(o, lang):
    if o["technique"]:
        return o["technique"][lang]
    if o["edition"]:
        return o["edition"][lang]
    return None


def faits_courts(o, lang):
    t = C.T[lang]
    morceaux = [dims_txt(o, lang) or (t["fiche_dims"] + " " + t["a_completer"]), technique_txt(o, lang) or (t["fiche_technique"] + " " + t["a_completer"])]
    return " · ".join(morceaux)


def etat(o, lang):
    t = C.T[lang]
    if o["statut"] == "vendu":
        return f'<span class="etiquette etiquette--vendu">{e(t["vendu"])}</span>'
    if o["statut"] == "en-cours":
        return f'<span class="etiquette etiquette--cours">{e(t["en_cours"])}</span>'
    if o["statut"] in ("non-disponible", "en-pret", "reserve"):
        cle = {"non-disponible": "non_disponible", "en-pret": "en_pret", "reserve": "reserve"}[o["statut"]]
        return f'<span class="etiquette etiquette--passe">{e(t[cle])}</span>'
    if o.get("prix"):
        montant, devise = o["prix"]
        return f'<span class="etiquette etiquette--prix">{e(prix_txt(montant, lang, devise))}</span>'
    return f'<span class="etiquette">{e(t["prix_demande"])}</span>'


def prix_txt(montant, lang, devise="EUR"):
    sym = {"EUR": "€", "GBP": "£", "USD": "$"}.get(devise, devise)
    n = f"{montant:,.0f}" if float(montant).is_integer() else f"{montant:,.2f}"
    if lang == "fr":
        return n.replace(",", " ").replace(".", ",") + " " + sym
    return sym + n


# ================================================================ chemins
def prefixe(prof):
    return "/" if MODE == "propres" else "../" * prof


def lien(lang, cle, prof, ancre=""):
    base = C.PAGES[cle][lang]
    if MODE == "html":
        if base == "index":
            return (prefixe(prof) or "./") + ancre if prof else "./" + ancre
        return f"{prefixe(prof)}{base}.html{ancre}"
    if base == "index":
        return "/" + ancre
    if base.endswith("/index"):
        return "/" + base[: -len("/index")] + ancre
    return "/" + base + ancre


def lien_salle(lang, sid, prof):
    chemin = f"{C.DOSSIER_SALLES[lang]}/{SERIES[sid]['slug'][lang]}"
    return f"{prefixe(prof)}{chemin}{'.html' if MODE == 'html' else ''}"


def asset(prof, chemin):
    return f"{prefixe(prof)}assets/{chemin}"


def fichier(lang, cle):
    return C.PAGES[cle][lang] + ".html"


def prof_de(chemin_fichier):
    return chemin_fichier.count("/")


# ================================================================ images
def srcset_oeuvre(prof, oid):
    o = OEUVRES[oid]
    return f'{asset(prof, f"img/oeuvres/{oid}-640.webp")} {o["t"]["640"][0]}w, {asset(prof, f"img/oeuvres/{oid}-1600.webp")} {o["t"]["1600"][0]}w'


def img_oeuvre(prof, oid, lang, sizes, chargement="lazy", classe="", priorite=False):
    o = OEUVRES[oid]
    w, h = o["t"]["1600"]
    pr = ' fetchpriority="high"' if priorite else ""
    taille = "1600" if priorite else "640"
    return (f'<img class="{classe}" src="{asset(prof, f"img/oeuvres/{oid}-{taille}.webp")}" srcset="{srcset_oeuvre(prof, oid)}" sizes="{sizes}" '
            f'width="{w}" height="{h}" loading="{chargement}" decoding="async"{pr} alt="{e(o["alt"][lang])}">')


def img_photo(prof, cle, alt, sizes="(max-width: 800px) 92vw, 50vw", classe="", chargement="lazy"):
    m = MED["photos"][cle]
    nom = cle.replace("/", "-")
    w, h = m["800"]
    ss = f'{asset(prof, f"img/photos/{nom}-800.webp")} {m["800"][0]}w'
    if "1600" in m:
        ss += f', {asset(prof, f"img/photos/{nom}-1600.webp")} {m["1600"][0]}w'
    return (f'<img class="{classe}" src="{asset(prof, f"img/photos/{nom}-800.webp")}" srcset="{ss}" sizes="{sizes}" width="{w}" height="{h}" '
            f'loading="{chargement}" decoding="async" alt="{e(alt)}">')


def img_decor(prof, nom, alt, sizes="(max-width: 800px) 92vw, 50vw", classe="", chargement="lazy"):
    m = MED["decors"][nom]
    w, h = m["full"]
    ss = f'{asset(prof, f"img/decors/{nom}-640.webp")} {m["640"][0]}w, {asset(prof, f"img/decors/{nom}.webp")} {w}w'
    return (f'<img class="{classe}" src="{asset(prof, f"img/decors/{nom}-640.webp")}" srcset="{ss}" sizes="{sizes}" width="{w}" height="{h}" '
            f'loading="{chargement}" decoding="async" alt="{e(alt)}">')


def figure_photo(prof, cle, alt, legende="", classe="fossile", sizes="(max-width: 800px) 92vw, 50vw", attrs=""):
    fig = f'<figcaption>{e(legende)}</figcaption>' if legende else ""
    return f'<figure class="{classe}" data-revele{attrs}><span class="fossile__cadre">{img_photo(prof, cle, alt, sizes)}</span>{fig}</figure>'


def figure_decor(prof, nom, alt, legende="", classe="fossile", sizes="(max-width: 800px) 92vw, 50vw", attrs=""):
    fig = f'<figcaption>{e(legende)}</figcaption>' if legende else ""
    return f'<figure class="{classe}" data-revele{attrs}><span class="fossile__cadre">{img_decor(prof, nom, alt, sizes)}</span>{fig}</figure>'


def bouton_oeuvre(prof, oid, lang, liste, sizes, classe_toile="", chargement="lazy", priorite=False):
    o = OEUVRES[oid]
    t = C.T[lang]
    voir = "View the work" if lang == "en" else "Voir l'œuvre"
    return (f'<button class="oeuvre__bouton" type="button" data-ouvrir="{oid}" data-liste="{liste}" data-curseur="{e(t["voir"])}">'
            f'<span class="vh">{voir} « {e(titre(o, lang))} »</span>'
            f'<span class="oeuvre__toile {classe_toile}" style="--ratio:{o["ratio"]}">{img_oeuvre(prof, oid, lang, sizes, chargement, priorite=priorite)}</span></button>')


def cartel(o, lang, balise="figcaption"):
    t = C.T[lang]
    tt = titre(o, lang)
    cls = "cartel__titre" + (" cartel__titre--vide" if not o["titre"] else "")
    return (f'<{balise} class="cartel"><span class="{cls}">{e(tt)}</span>'
            f'<span class="cartel__faits">{e(faits_courts(o, lang))}</span>{demande_oeuvre(o, lang)}</{balise}>')


def demande_oeuvre(o, lang):
    """Brief de Lisa (v6) : sur les pages d'œuvres, « Enquire about this work » vers son courriel ; la vente est dans Available Works."""
    t = C.T[lang]
    sujet = quote(("Enquiry: " if lang == "en" else "Demande : ") + titre(o, lang))
    return f'<a class="etiquette etiquette--demande" href="mailto:{C.COORD["courriel"]}?subject={sujet}">{e(t["demander"])}</a>'


def figure_oeuvre(prof, oid, lang, liste, sizes="(max-width: 700px) 80vw, 40vw"):
    o = OEUVRES[oid]
    s = math.sqrt(o["hcm"]) if o["hcm"] else 8.2
    style = f'--ratio:{o["ratio"]};--s:{s:.3f};--fond-oeuvre:{o["fond"]}'
    return (f'<figure class="oeuvre" style="{style}" data-fond="{o["fond"]}" data-oeuvre="{oid}">'
            f'{bouton_oeuvre(prof, oid, lang, liste, sizes, "cire-fond")}{cartel(o, lang)}</figure>')


def vignette(prof, oid, lang, liste, sizes="(max-width: 700px) 44vw, 18vw", classe="vignette"):
    o = OEUVRES[oid]
    return (f'<figure class="{classe}" style="--ratio:{o["ratio"]}">{bouton_oeuvre(prof, oid, lang, liste, sizes, "cire-fond")}'
            f'<figcaption><span class="cartel__titre{" cartel__titre--vide" if not o["titre"] else ""}">{e(titre(o, lang))}</span></figcaption></figure>')


def lettres(texte, balise="span", classe=""):
    c = f' class="{classe}"' if classe else ""
    return f'<{balise}{c} data-lettres>{e(texte)}</{balise}>'


def surtitre(texte, n=None):
    num = f'<span class="surtitre__n">{n:02d}</span>' if n is not None else ""
    return f'<p class="surtitre">{num}<span>{e(texte)}</span></p>'


def jours_avant(iso):
    d = DT.date.fromisoformat(iso)
    return (d - AUJ).days


def compte(lang, iso):
    t = C.T[lang]
    n = jours_avant(iso)
    txt = t["aujourdhui"] if n == 0 else (t["passe"] if n < 0 else (t["jour_restant"] if n == 1 else t["jours_restants"].format(n=n)))
    return f'<span class="compte" data-compte="{iso}">{e(txt)}</span>'


def statut(lang, classe=""):
    return (f'<p class="statut {classe}" data-statut><span class="statut__point" aria-hidden="true"></span>'
            f'<span class="statut__texte">{e(C.T[lang]["horaires_court"])}</span></p>')


def bouton(texte, href, classe="bouton", attrs=""):
    return f'<a class="{classe} aimant" href="{href}"{attrs}><span>{e(texte)}</span></a>'


# ================================================================ gabarit
NAV_UNIVERS = {
    "maison": ("oeuvres", "artiste", "espace", "retraites", "expositions"),
    "atelier": ("oeuvres", "artiste", "parcours", "presse", "boutique"),
    "espace": ("espace", "salon_the", "cosessions", "cours_prives", "evenements", "retraites"),
}
PARENT = {"salle": "oeuvres", "pip": "retraites", "encaustics": "retraites", "studio": "artiste", "salon_the": "espace", "cosessions": "espace",
          "inscription_pip": "pip", "inscription_encaustics": "encaustics", "conditions": "retraites"}
RETRAITES_ORDRE = ("pip", "encaustics")
INSCRIPTION = {"pip": "inscription_pip", "encaustics": "inscription_encaustics"}
# Formulaires Wix du site actuel (cirenza.com), lus le 20 novembre 2026 : les nouvelles pages enverront leurs réponses à ces mêmes formulaires
FORMULAIRES_WIX = {"pip": "2ba9da25-399e-45bb-bda7-4c2943805064", "encaustics": "a0aeff52-97e8-42de-abac-6993aecc8c4f"}
NOINDEX_TOUJOURS = {"inscription_pip", "inscription_encaustics", "horaires", "recherche"}


def nom_retraite(r, lang):
    """Nom de la retraite dans la langue de la page (demande de Lisa : noms en français sur les pages françaises)."""
    return r.get("titre_fr") if lang == "fr" and r.get("titre_fr") else r["titre"]


def bascule_univers(lang, cle, prof, classe=""):
    """Les deux côtés de la maison : l'atelier de l'artiste et l'Espace Créa-Tea-Vité."""
    t = C.T[lang]
    u = t["univers"]
    cote = UNIVERS.get(cle, "maison")
    a_cur = ' aria-current="true"' if cote == "atelier" else ""
    e_cur = ' aria-current="true"' if cote == "espace" else ""
    return (f'<nav class="univers {classe}" aria-label="{e(u["aria"])}" data-univers="{cote}">'
            f'<a class="univers__cote univers__cote--atelier" href="{lien(lang, "oeuvres", prof)}"{a_cur}><span class="univers__nom">{e(u["atelier"])}</span><span class="univers__sous">{e(u["atelier_long"])}</span></a>'
            f'<span class="univers__curseur" aria-hidden="true"></span>'
            f'<a class="univers__cote univers__cote--espace" href="{lien(lang, "espace", prof)}"{e_cur}><span class="univers__nom">{e(u["espace"])}</span><span class="univers__sous">Créa-Tea-Vité</span></a></nav>')


def entete(lang, cle, prof, autre_href):
    t = C.T[lang]
    autre = "fr" if lang == "en" else "en"
    nav = ""
    actif = PARENT.get(cle, cle)
    for k in NAV_UNIVERS[UNIVERS.get(cle, "maison")]:
        cur = ' aria-current="page"' if k == actif else ""
        nav += f'<li><a href="{lien(lang, k, prof)}"{cur}>{e(t.get("nav_court", {}).get(k, t["nav"][k]))}</a></li>'

    def groupe(nom, items, classe=""):
        lis = "".join(f'<li><a href="{h}"><span data-lettres>{e(x)}</span>{f"<small>{e(s)}</small>" if s else ""}</a></li>' for x, h, s in items)
        return f'<div class="menu__strate {classe}"><p class="menu__groupe">{e(nom)}</p><ul>{lis}</ul></div>'
    g_oeuvres = [(t["nav"]["oeuvres"], lien(lang, "oeuvres", prof), "Statement" if lang == "en" else "Déclaration"), (SERIES[LEAD]["titre"][lang], lien_salle(lang, LEAD, prof), t["nav"]["recent"] if lang == "en" else "Œuvres récentes"),
                 (t["nav"]["archive"], lien(lang, "oeuvres", prof, "#archive"), ", ".join(SERIES[x]["titre"][lang] for x in ("london-tube", "cuba", "beneath-the-surface"))),
                 (t["nav"]["boutique"], lien(lang, "boutique", prof), "Lisa Cirenza Fine Art"), (t["nav"]["editions"], lien(lang, "boutique", prof, "#editions"), "15 × 20 cm")]
    g_artiste = [(t["nav"]["artiste"], lien(lang, "artiste", prof), None), (t["nav"]["parcours"], lien(lang, "parcours", prof), None), (t["nav"]["presse"], lien(lang, "presse", prof), None),
                 (t["nav"]["studio"], lien(lang, "studio", prof), None)]
    g_espace = [(t["nav"]["espace"], lien(lang, "espace", prof), None), (t["nav"]["salon_the"], lien(lang, "salon_the", prof), "Visit in person" if lang == "en" else "Sur place"),
                (t["nav"]["cosessions"], lien(lang, "cosessions", prof), None), (t["nav"]["cours_prives"], lien(lang, "cours_prives", prof), None),
                (t["nav"]["evenements"], lien(lang, "evenements", prof), None), (t["nav"]["contact"], lien(lang, "contact", prof), None)]
    g_retraites = [(t["nav"]["retraites"], lien(lang, "retraites", prof), None)] + [(L(lang, RETRAITES[k]["menu"]), lien(lang, k, prof), L(lang, RETRAITES[k]["dates"])) for k in RETRAITES_ORDRE] + [(t["nav"]["conditions"], lien(lang, "conditions", prof), None)]
    g_expos = [(t["nav"]["expositions"], lien(lang, "expositions", prof), C.EXPO["titre"]), (t["nav"]["recherche"], lien(lang, "recherche", prof), None)]
    menu = (f'<div class="menu" id="menu" hidden>{bascule_univers(lang, cle, prof, "univers--menu")}<nav class="menu__grille" aria-label="{"Site" if lang == "en" else "Site"}">'
            f'{groupe(t["groupes_menu"]["oeuvres"], g_oeuvres, "menu__strate--atelier")}{groupe(t["groupes_menu"]["artiste"], g_artiste, "menu__strate--atelier")}{groupe(t["groupes_menu"]["espace"], g_espace, "menu__strate--espace")}{groupe(t["groupes_menu"]["retraites"], g_retraites, "menu__strate--espace")}{groupe(t["groupes_menu"]["expositions"], g_expos, "menu__strate--expos")}</nav>'
            f'<div class="menu__bas">{statut(lang)}<p>{e(C.COORD["rue"])}, {e(C.COORD["ville"])}</p><a href="{autre_href}" hreflang="{autre}" lang="{autre}">{e(t["langue_autre"])}</a></div></div>')
    annonces = '<p class="barre__annonce" data-annonce hidden></p>'
    return f'''<header class="entete" data-entete>
  <div class="entete__barre">
    <p class="barre__lieu"><a href="{lien(lang, "espace", prof)}">Espace Créa-Tea-Vité</a><span class="barre__adresse"> · {e(C.COORD["rue"])}, La Clusaz</span></p>
    {annonces}
    {statut(lang, "barre__statut")}
  </div>
  <div class="entete__rangee">
  <a class="entete__marque" href="{lien(lang, "accueil", prof)}"><span class="signature" role="img" aria-label="Lisa Cirenza"></span><span class="vh"> – {e(t["nav"]["accueil"])}</span></a>
  {bascule_univers(lang, cle, prof, "univers--entete")}
  <nav class="entete__nav" aria-label="{"Main navigation" if lang == "en" else "Navigation principale"}"><ul>{nav}</ul></nav>
  <button class="entete__panier" type="button" data-panier-ouvrir hidden aria-label="{"Open the baskets" if lang == "en" else "Ouvrir les paniers"}"><span class="entete__panier-a" data-compte-panier="atelier">0</span><span class="entete__panier-e" data-compte-panier="espace">0</span></button>
  <a class="entete__recherche" href="{lien(lang, "recherche", prof)}" aria-label="{e(t["nav"]["recherche"])}"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M15.5 15.5 21 21" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg></a>
  <a class="entete__langue" href="{autre_href}" hreflang="{autre}" lang="{autre}"><span class="vh">{e(t["langue_autre"])}</span><span aria-hidden="true">{t["langue_autre_court"]}</span></a>
  <button class="entete__menu" type="button" aria-expanded="false" aria-controls="menu"><span class="entete__menu-texte">{e(t["menu"])}</span><span class="entete__menu-traits" aria-hidden="true"><i></i><i></i><i></i></span></button>
  </div>
</header>
{menu}'''


def pied(lang, prof, autre_href):
    t = C.T[lang]
    c = C.COORD
    autre = "fr" if lang == "en" else "en"
    hor = "".join(f"<div><dt>{e(j)}</dt><dd>{e(h)}</dd></div>" for j, h in t["horaires_lignes"])
    plan_a = "".join(f'<li><a href="{lien(lang, k, prof)}">{e(t["nav"][k])}</a></li>' for k in ("oeuvres", "artiste", "parcours", "presse"))
    plan_e = "".join(f'<li><a href="{lien(lang, k, prof)}">{e(t["nav"][k])}</a></li>' for k in ("espace", "salon_the", "cosessions", "cours_prives", "evenements", "retraites", "expositions"))
    ext = ' target="_blank" rel="noopener"'
    a_completer = t["a_completer"]
    return f'''<footer class="pied">
  <div class="pied__haut">
    <span class="signature signature--complete" role="img" aria-label="Lisa Cirenza"></span>
    <p class="pied__citation">{e(C.POSITION["citation"][lang])}</p>
  </div>
  <div class="pied__maisons">
    <section class="pied__maison pied__maison--atelier">
      <h2>{e(t["univers"]["atelier_long"])}</h2>
      <p class="pied__forme">{e(c["forme_atelier"][lang])} · SIRET {e(c["siret_atelier"])}</p>
      <p>{e(t["pied_atelier"])}</p>
      <ul class="pied__plan">{plan_a}<li><a href="{lien(lang, "boutique", prof, "#atelier")}">{e(t["nav"]["boutique"])}</a></li></ul>
      <p><a class="courriel" href="mailto:{c["courriel"]}">{c["courriel"]}</a></p>
      <p class="pied__reseaux"><a href="{c["instagram"]}"{ext}>Instagram art.lc</a> · <a href="{c["linkedin"]}"{ext}>LinkedIn</a> · <a href="{c["facebook"]}"{ext}>Facebook</a></p>
    </section>
    <section class="pied__maison pied__maison--espace">
      <h2>{e(c["espace"])}</h2>
      <p class="pied__forme">{e(c["forme_espace"][lang])} · SIRET {e(c["siret_espace"])}</p>
      <p>{e(t["pied_espace"])}</p>
      <ul class="pied__plan">{plan_e}</ul>
      <p><a class="courriel" href="mailto:{c["courriel_espace"]}">{c["courriel_espace"]}</a></p>
      <p class="pied__reseaux"><a href="{c["instagram_espace"]}"{ext}>Instagram espacecreateavite</a></p>
    </section>
    <section class="pied__infos">
      <h2>{e(t["horaires"])}</h2><dl class="horaires" data-horaires-liste>{hor}</dl>{statut(lang)}
      <address>{e(c["rue"])}<br>{e(c["ville"])}, {e(c["pays"][lang])}</address>
      <p><a href="tel:{c["tel_brut"]}">{e(c["tel"])}</a> · <a href="https://wa.me/{c["tel_brut"].lstrip("+")}"{ext}>WhatsApp</a> · <a href="{lien(lang, "contact", prof)}">{e(t["nav"]["contact"])}</a></p>
    </section>
  </div>
  <p class="pied__bas"><span>{e(t["pied_droits"])}</span><span>{e("Legal notice · Privacy policy · Cookie policy · Website terms: Lisa's texts to come" if lang == "en" else "Mentions légales · Politique de confidentialité · Cookies · Conditions d'utilisation : textes de Lisa à venir")}</span><button class="pied__cookies" type="button" data-cookies-ouvrir>{e("Cookie settings" if lang == "en" else "Réglages des cookies")}</button><span>{e(t["traduction"])}</span><span>{e(t["pied_maquette"])}</span><a href="{autre_href}" hreflang="{autre}" lang="{autre}">{e(t["langue_autre"])}</a></p>
</footer>'''


def polices():
    regles = [
        ("LC Fraunces", "fraunces.woff", "normal", "300 800"),
        ("LC Fraunces", "fraunces-italique.woff", "italic", "300 800"),
        ("LC Plex Mono", "plex-mono-regular.woff", "normal", "400"),
        ("LC Plex Mono", "plex-mono-medium.woff", "normal", "500"),
    ]
    return "<style>" + "".join(f'@font-face{{font-family:"{f}";src:url("{prefixe(0) if MODE == "propres" else "__P__"}assets/polices/{n}") format("woff");font-style:{s};font-weight:{w};font-display:swap}}' for f, n, s, w in regles) + "</style>"


# ================================================================ v5 · SEO et GEO : adresses absolues, données structurées (schema.org)
LISA_ID, ESPACE_ID, SITE_ID = SITE_URL + "/#lisa", SITE_URL + "/#espace", SITE_URL + "/#site"


def url_abs(href):
    """Adresse absolue d'un lien interne (mode « propres » : les liens commencent par /)."""
    if not href or not href.startswith("/"):
        return None
    return SITE_URL + href


def url_page(lang, cle, salle=None):
    return url_abs(lien_salle(lang, salle, 0) if salle else lien(lang, cle, 0)) if MODE == "propres" else None


def img_abs(chemin_asset):
    return f"{SITE_URL}/assets/{chemin_asset}"


def adresse_schema():
    c = C.COORD
    return {"@type": "PostalAddress", "streetAddress": c["rue"], "postalCode": c["ville"].split()[0], "addressLocality": "La Clusaz",
            "addressRegion": "Haute-Savoie", "addressCountry": "FR"}


def schema_lisa(lang):
    c = C.COORD
    return {"@type": "Person", "@id": LISA_ID, "name": "Lisa Cirenza", "alternateName": "Lisa Gitkin",
            "jobTitle": "Painter" if lang == "en" else "Peintre", "description": C.POSITION["ligne"][lang],
            "url": url_page(lang, "artiste"), "image": img_abs("img/photos/artiste-lisa-portrait-fond-glacier-800.webp"),
            "address": {"@type": "PostalAddress", "addressLocality": "La Clusaz", "addressCountry": "FR"},
            "alumniOf": {"@type": "CollegeOrUniversity", "name": "Stanford University"},
            "memberOf": {"@type": "Organization", "name": "Salon d'Automne"},
            "knowsAbout": ["Encaustic painting", "Mixed media", "Oil painting", "Watercolour", "Glaciers", "Juneau Icefield"],
            "founder": {"@id": ESPACE_ID},
            "sameAs": [c["instagram"], c["linkedin"], c["facebook"], "https://www.artworkarchive.com/profile/lisa-cirenza"]}


def schema_espace(lang):
    c = C.COORD
    return {"@type": ["ArtGallery", "CafeOrCoffeeShop"], "@id": ESPACE_ID, "name": c["espace"],
            "description": C.DESCRIPTIONS["espace"][lang], "url": url_page(lang, "espace"),
            "image": img_abs("img/photos/espace-facade-de-nuit-800.webp"), "address": adresse_schema(),
            "telephone": c["tel_brut"], "email": c["courriel_espace"], "founder": {"@id": LISA_ID},
            "openingHoursSpecification": HOR.schema_ouverture(HEURES), "sameAs": [c["instagram_espace"]]}


def schema_site(lang):
    return {"@type": "WebSite", "@id": SITE_ID, "url": SITE_URL + "/", "name": "Lisa Cirenza",
            "inLanguage": ["en", "fr"], "publisher": {"@id": LISA_ID}}


def schema_retraite(lang, cle):
    r = RETRAITES[cle]
    prix = [p for _, p, note in R.PRIX_CHAMBRES if not note]
    photo = r["photo"]
    return {"@type": "Event", "name": nom_retraite(r, lang), "startDate": r["debut"], "endDate": r["fin"],
            "eventStatus": "https://schema.org/EventScheduled", "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "description": L(lang, r["groupe"]) + " " + R.LOGEMENT[lang],
            "image": img_abs(f'img/photos/{photo.replace("/", "-")}-800.webp') if isinstance(photo, str) else None,
            "location": {"@type": "Place", "name": C.COORD["espace"], "address": adresse_schema()},
            "organizer": {"@id": ESPACE_ID}, "performer": {"@id": LISA_ID},
            "offers": {"@type": "AggregateOffer", "lowPrice": min(prix), "highPrice": max(prix), "priceCurrency": "EUR",
                       "availability": "https://schema.org/LimitedAvailability", "url": url_page(lang, cle)},
            "url": url_page(lang, cle)}


def schema_faq(paires, lang):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q[lang], "acceptedAnswer": {"@type": "Answer", "text": rep[lang]}} for q, rep in paires]}


def schema_oeuvres(lang, sid):
    items = []
    for i, oid in enumerate(LISTES.get(sid, [])):
        o = OEUVRES[oid]
        if not o["titre"]:
            continue
        x = {"@type": "VisualArtwork", "name": titre(o, lang), "creator": {"@id": LISA_ID}, "artform": "Painting" if lang == "en" else "Peinture",
             "image": img_abs(f"img/oeuvres/{oid}-1600.webp"), "url": url_page(lang, "salle", sid) + f"?oeuvre={oid}" if url_page(lang, "salle", sid) else None}
        if o.get("technique"):
            x["artMedium"] = o["technique"].get(lang)
        if o.get("annee"):
            x["dateCreated"] = str(o["annee"])
        if o.get("hcm") and o.get("lcm"):
            x["height"] = {"@type": "Distance", "name": f'{fmt(o["hcm"], "en")} cm'}
            x["width"] = {"@type": "Distance", "name": f'{fmt(o["lcm"], "en")} cm'}
        items.append({"@type": "ListItem", "position": len(items) + 1, "item": x})
    return {"@type": "ItemList", "name": SERIES[sid]["titre"][lang], "itemListElement": items}


def schema_fil(lang, cle, titre_court, salle=None):
    etapes = [(C.T[lang]["nav"]["accueil"], url_page(lang, "accueil"))]
    parent = PARENT.get(cle)
    if parent and parent != cle:
        etapes.append((C.T[lang]["nav"][parent], url_page(lang, parent)))
    etapes.append((titre_court, url_page(lang, cle, salle)))
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(etapes) if u]}


def nettoyer_schema(x):
    if isinstance(x, dict):
        return {k: nettoyer_schema(v) for k, v in x.items() if v not in (None, "", [], {})}
    if isinstance(x, list):
        return [nettoyer_schema(v) for v in x]
    return x


def schema_page(lang, cle, titre_page, donnees_page):
    g = []
    d = donnees_page or {}
    if cle == "accueil":
        g += [schema_site(lang), schema_lisa(lang), schema_espace(lang)]
    elif cle in ("artiste", "parcours", "presse", "studio"):
        g.append({"@type": "ProfilePage", "mainEntity": schema_lisa(lang)} if cle == "artiste" else schema_lisa(lang))
    elif cle in ("espace", "contact", "cours", "cours_prives", "evenements"):
        g.append(schema_espace(lang))
    elif cle == "retraites":
        g.append({"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": schema_retraite(lang, k)} for i, k in enumerate(RETRAITES_ORDRE)]})
    elif cle in RETRAITES:
        g.append(schema_retraite(lang, cle))
        if RETRAITES[cle].get("faq"):
            g.append(schema_faq(RETRAITES[cle]["faq"], lang))
    elif cle == "salle" and d.get("salle"):
        g.append(schema_oeuvres(lang, d["salle"]))
    if cle != "accueil" and (cle in C.PAGES or cle == "salle"):
        court = SERIES[d["salle"]]["titre"][lang] if cle == "salle" and d.get("salle") else (nom_retraite(RETRAITES[cle], lang) if cle in RETRAITES else C.T[lang]["nav"].get(cle, titre_page))
        g.append(schema_fil(lang, cle, court, d.get("salle")))
    if not g:
        return ""
    data = nettoyer_schema({"@context": "https://schema.org", "@graph": g})
    txt = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/ld+json">{txt}</script>'


def page(lang, cle, chemin, titre_page, corps, autre_chemin, donnees_page=None, classe_corps="", image_og=None, preload=None, description=None):
    t = C.T[lang]
    prof = prof_de(chemin)
    autre = "fr" if lang == "en" else "en"
    autre_href = autre_chemin
    d_page = donnees_page or {}
    seo = SEO.PAGES.get(cle) or {}
    if cle == "accueil":
        titre_complet = C.POSITION["seo"][lang]
    elif cle == "salle":
        titre_complet = f"{titre_page} · {SEO.SUFFIXE_SALLE[lang]}"
    elif cle in RETRAITES:
        titre_complet = f"{nom_retraite(RETRAITES[cle], lang)} {RETRAITES[cle]['debut'][:4]} · {SEO.SUFFIXE_RETRAITE[lang]}"
    elif seo.get("titre"):
        titre_complet = seo["titre"][lang]
    else:
        titre_complet = f"{titre_page} · Lisa Cirenza"
    if not description:
        if cle == "salle" and d_page.get("salle"):
            description = SERIES[d_page["salle"]]["texte"][lang]
        elif cle in RETRAITES:
            r_ = RETRAITES[cle]
            description = f'{nom_retraite(r_, lang)}: {L(lang, r_["dates"])}, La Clusaz. {L(lang, r_["prix"])}. {L(lang, r_["accroche"])}'
        elif seo.get("description"):
            description = seo["description"][lang]
        else:
            description = C.DESCRIPTIONS["espace"][lang] if UNIVERS.get(cle) == "espace" else t["description"]
    if len(description) > 160:
        description = description[:157].rsplit(" ", 1)[0].rstrip(",;:") + "…"
    canon = url_abs(lien_salle(lang, d_page["salle"], 0)) if cle == "salle" and MODE == "propres" else (url_page(lang, cle) if cle in C.PAGES else None)
    url_autre = url_abs(autre_chemin) if MODE == "propres" else None
    alternes = ""
    if canon and url_autre:
        u_en, u_fr = (canon, url_autre) if lang == "en" else (url_autre, canon)
        alternes = (f'<link rel="canonical" href="{canon}">\n<link rel="alternate" hreflang="en" href="{u_en}">\n'
                    f'<link rel="alternate" hreflang="fr" href="{u_fr}">\n<link rel="alternate" hreflang="x-default" href="{u_en}">\n'
                    f'<meta property="og:url" content="{canon}">')
    og = image_og or asset(prof, "img/oeuvres/recente-01-1600.webp")
    partage = SITE / "assets" / "partage" / f"{chemin.replace('/', '-').replace('.html', '')}.jpg"
    if partage.exists():
        og = f"{SITE_URL}/assets/partage/{partage.name}"
    elif og.startswith("/"):
        og = SITE_URL + og
    univers = UNIVERS.get(cle, "maison")
    extra = f'<script>window.LC_PAGE={json.dumps(donnees_page or {}, ensure_ascii=False)};</script>'
    pre = ""
    if preload:
        pre = f'<link rel="preload" as="image" href="{preload[0]}" imagesrcset="{preload[1]}" imagesizes="{preload[2]}" fetchpriority="high">'
    pol = polices().replace("__P__", prefixe(prof))
    pol = f'<link rel="preload" as="font" type="font/woff" href="{prefixe(0) if MODE == "propres" else prefixe(prof)}assets/polices/fraunces.woff" crossorigin>' + pol
    return f'''<!doctype html>
<html lang="{lang}" class="no-js" data-racine="{prefixe(prof)}" data-page="{cle}" data-mode-liens="{MODE}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(titre_complet)}</title>
<meta name="robots" content="{"noindex, nofollow" if MAQUETTE or cle in NOINDEX_TOUJOURS else "index, follow"}">
<meta name="description" content="{e(description)}">
<meta name="theme-color" content="#f2efe8">
{alternes if alternes else f'<link rel="alternate" hreflang="{autre}" href="{autre_href}">'}
<link rel="icon" type="image/png" sizes="32x32" href="{asset(prof, "img/icones/icone-32.png")}">
<link rel="icon" type="image/png" sizes="192x192" href="{asset(prof, "img/icones/icone-192.png")}">
<link rel="apple-touch-icon" href="{asset(prof, "img/icones/apple-touch-icon.png")}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Lisa Cirenza">
<meta property="og:locale" content="{"en_US" if lang == "en" else "fr_FR"}">
<meta property="og:title" content="{e(titre_complet)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:image" content="{og}">
<meta property="og:image:alt" content="{e(titre_complet)}">
<meta name="twitter:card" content="summary_large_image">
{pre}
{pol}
<link rel="stylesheet" href="{asset(prof, "css/site.css")}?v={VERSION}">
<script>(function(d){{d.classList.remove("no-js");d.classList.add("js");try{{if(matchMedia("(prefers-reduced-motion: reduce)").matches)d.classList.add("mouvement-reduit")}}catch(x){{}}}})(document.documentElement);</script>
{schema_page(lang, cle, titre_page, d_page)}
{extra}
<script defer src="{asset(prof, f"js/donnees-{lang}.js")}?v={VERSION}"></script>
<script defer src="{asset(prof, "js/site.js")}?v={VERSION}"></script>
</head>
<body class="{classe_corps} univers-{univers}">
<a class="evitement" href="#contenu">{e(t["aller_contenu"])}</a>
{'<p class="badge-maquette">' + ("Mock-up" if lang == "en" else "Maquette") + '</p>' if APERCU else ""}
<div class="grain" aria-hidden="true"></div>
{entete(lang, cle, prof, autre_href)}
{panier_html(lang, prof)}
<div class="altimetre" aria-hidden="true"><span class="altimetre__haut">{e(t["altitude"])}</span><span class="altimetre__piste"><i class="altimetre__curseur"></i></span><span class="altimetre__strate"></span></div>
<main id="contenu" tabindex="-1">
{corps}
</main>
{pied(lang, prof, autre_href)}
</body>
</html>
'''


def typo_fr(t):
    """Espaces insécables du français : avant : ; ? ! », après «, entre un nombre et €."""
    t = re.sub(r"[ \u00a0]+([:;?!»])", "\u00a0\\1", t)
    t = re.sub(r"«[ \u00a0]*", "«\u00a0", t)
    t = re.sub(r"(\d) (€|cm|h\b|%)", "\\1\u00a0\\2", t)
    t = t.replace("n° ", "n°\u00a0")
    return t


def typo_html_fr(html_txt):
    """Applique typo_fr au HTML, hors scripts et styles, et sans toucher aux adresses."""
    morceaux = re.split(r"(<script\b.*?</script>|<style\b.*?</style>)", html_txt, flags=re.S)
    def hors_url(m):
        return m.group(0) if m.group(0).startswith(("http", "mailto", "tel")) else typo_fr(m.group(0))
    for i in range(0, len(morceaux), 2):
        morceaux[i] = re.sub(r"(?:https?://|mailto:|tel:)[^\s\"'<>]+|[^<>]+(?=<|$)", hors_url, morceaux[i])
    return "".join(morceaux)


def ecrire(chemin, texte):
    p = SITE / chemin
    p.parent.mkdir(parents=True, exist_ok=True)
    if chemin.startswith("fr/"):
        texte = typo_html_fr(texte)
    p.write_text(texte, encoding="utf-8")


def href_autre(lang, cle, prof, salle=None):
    autre = "fr" if lang == "en" else "en"
    if salle:
        return lien_salle(autre, salle, prof)
    return lien(autre, cle, prof)


def n_oeuvres(n, lang):
    t = C.T[lang]
    return t["oeuvre_1"] if n == 1 else t["oeuvres_n"].format(n=n)


def bandeau(lang, prof, n, sur, titre_txt, intro, image_html, strate, classe=""):
    intro_html = "".join(f"<p>{e(x)}</p>" for x in (intro if isinstance(intro, list) else [intro])) if intro else ""
    return f'''<section class="bandeau {classe}" data-strate="{e(strate)}">
  <div class="bandeau__texte">
    {surtitre(sur, n)}
    <h1 class="bandeau__titre">{lettres(titre_txt)}</h1>
    <div class="bandeau__intro" data-apparait>{intro_html}</div>
  </div>
  <div class="bandeau__image">{image_html}</div>
</section>'''


# ================================================================ accueil
def strate_li(lang, prof, sid, i, classe=""):
    t = C.T[lang]
    s = SERIES[sid]
    ids = [x for x in LISTES[sid]][:4]
    couleurs = [OEUVRES[x]["dominante"] for x in LISTES[sid]][:3]
    while len(couleurs) < 3:
        couleurs.append(couleurs[-1])
    periode = L(lang, s["periode"]) if s.get("periode") else ""
    sous = L(lang, s["sous_titre"]) if s.get("sous_titre") else ""
    vign = "".join(f'<span class="strate__mini" style="--ratio:{OEUVRES[x]["ratio"]}"><img src="{asset(prof, f"img/oeuvres/{x}-640.webp")}" alt="" loading="lazy" decoding="async" width="{OEUVRES[x]["t"]["640"][0]}" height="{OEUVRES[x]["t"]["640"][1]}"></span>' for x in ids)
    meta = n_oeuvres(len(LISTES[sid]), lang) + (" · " + periode if periode else "") + (" · " + sous if sous else "")
    return f'''<li class="strate {classe}" style="--c1:{couleurs[0]};--c2:{couleurs[1]};--c3:{couleurs[2]};--i:{i};--bg:{-(i * 61) % 400}px">
  <a class="strate__lien" href="{lien_salle(lang, sid, prof)}" data-curseur="{e(t["voir"])}">
    <span class="strate__n">{i + 1:02d}</span>
    <span class="strate__titre">{e(s["titre"][lang])}</span>
    <span class="strate__meta">{e(meta)}</span>
    <span class="strate__minis" aria-hidden="true">{vign}</span>
  </a>
</li>'''


def colonne(lang, prof, compacte=False):
    """La série actuelle en tête, puis l'Archive des séries plus anciennes."""
    t = C.T[lang]
    lis = [strate_li(lang, prof, LEAD, 0, "strate--tete")]
    lis.append(f'<li class="colonne__archive" id="archive-colonne"><span>{e(t["nav"]["archive"])}</span><small>{e(C.SERIE_ACTUELLE["archive"][lang])}</small></li>')
    lis += [strate_li(lang, prof, sid, i + 1) for i, sid in enumerate(ARCHIVE)]
    return f'<ol class="colonne{" colonne--compacte" if compacte else ""}" data-colonne>{"".join(lis)}</ol>'


def page_accueil(lang):
    t = C.T[lang]
    chemin = fichier(lang, "accueil")
    prof = prof_de(chemin)
    hero = "recente-01"
    autre = href_autre(lang, "accueil", prof)
    sizes_hero = "(max-width: 900px) 70vw, 34vw"
    P = C.POSITION
    S = C.SERIE_ACTUELLE
    E = C.EDITIONS_COLLECTION
    u = t["univers"]
    fr = lang == "fr"
    cartes_presse = "".join(carte_presse(lang, prof, p, "(max-width: 700px) 60vw, 20vw") for p in [x for x in C.PRESSE if not x.get("archive")][:5])
    lead = SERIES[LEAD]
    grat = "cool-reflections"
    editions = "".join(f'<li class="edition-serie"><span class="edition-serie__bloc{" edition-serie__bloc--vide" if not x["image"] else ""}">{img_oeuvre(prof, x["image"], lang, "(max-width: 700px) 40vw, 14vw") if x["image"] else ""}</span><span class="edition-serie__titre">{e(x["titre"][lang])}</span></li>' for x in E["series"])
    corps = f'''
<section class="ouverture" data-ouverture data-strate="{e("Lisa Cirenza")}">
  <canvas class="ouverture__gl" aria-hidden="true"></canvas>
  <div class="ouverture__strates" aria-hidden="true">{"".join(f'<i style="--k:{k}"></i>' for k in range(9))}</div>
  <div class="ouverture__grille">
    <div class="ouverture__texte">
      <p class="surtitre" data-apparait><span class="surtitre__n">1 040 m</span><span>{e(P["titre"][lang])}</span></p>
      <h1 class="ouverture__titre" id="titre-accueil"><span class="ouverture__prenom" data-lettres data-lettres-auto>Lisa</span> <span class="ouverture__nom" data-lettres data-lettres-auto>Cirenza</span></h1>
      <p class="ouverture__ligne" data-apparait>{e(P["ligne"][lang])}</p>
      <p class="ouverture__actions" data-apparait>{bouton(lead["titre"][lang], lien_salle(lang, LEAD, prof), "bouton bouton--atelier")}{bouton(t["nav"]["declaration"], lien(lang, "artiste", prof, "#declaration"), "bouton bouton--ligne")}</p>
    </div>
    <figure class="ouverture__oeuvre" data-apparait>
      {bouton_oeuvre(prof, hero, lang, LEAD, sizes_hero, "ouverture__toile", "eager", True)}
      <figcaption class="cartel cartel--clair"><span class="cartel__titre">{e(lead["titre"][lang])}</span><span class="cartel__faits">{e(("Recent work · " if not fr else "Œuvre récente · ") + (OEUVRES[hero]["titre"] or ("title from Artwork Archive to come" if not fr else "titre à venir d'Artwork Archive")))}</span></figcaption>
    </figure>
  </div>
  <button class="ouverture__passer" type="button" hidden>{"Skip" if not fr else "Passer"}</button>
  <p class="ouverture__defiler" data-apparait aria-hidden="true"><span>{"Scroll down through the strata" if not fr else "Descendez à travers les strates"}</span><i></i></p>
</section>

<section class="declaration-accueil" data-strate="{e(t["nav"]["declaration"])}">
  <div class="declaration-accueil__texte">
    {surtitre("Artist statement" if not fr else "Déclaration d'artiste", 1)}
    <blockquote class="declaration-accueil__citation"><p>{e(P["citation"][lang])}</p></blockquote>
    <p data-apparait>{e(C.DECLARATION[lang][0])}</p>
    <p data-apparait>{bouton("Read the full statement" if not fr else "Lire toute la déclaration", lien(lang, "artiste", prof, "#declaration"), "bouton bouton--ligne")}</p>
  </div>
  {figure_photo(prof, "artiste/lisa-a-17-ans-juneau-icefield", "Lisa at seventeen on skis with a heavy pack, crossing the Juneau Icefield" if not fr else "Lisa à dix-sept ans, à skis avec un lourd sac, sur le champ de glace de Juneau", "Juneau Icefield, expedition photograph" if not fr else "Champ de glace de Juneau, photo d'expédition", "fossile declaration-accueil__photo", "(max-width: 800px) 60vw, 24vw")}
</section>

<section class="geologie" data-strate="{e("The Geology of the Invisible" if not fr else "La géologie de l'invisible")}">
  <div class="geologie__grille">
    <div class="geologie__texte">
      {surtitre(lead["titre"][lang], 2)}
      <h2 class="titre-section">{lettres("The Geology of the Invisible" if not fr else "La géologie de l'invisible")}</h2>
      <p data-apparait>{e(C.MEMBRANE[lang])}</p>
      <p data-apparait>{e(C.DECLARATION[lang][2])}</p>
      <p data-apparait>{bouton(t["nav"]["artiste"], lien(lang, "artiste", prof), "bouton bouton--ligne")}</p>
    </div>
    <div class="grattage" data-grattage style="--ratio:{OEUVRES[grat]["ratio"]}">
      <figure class="grattage__oeuvre">
        {bouton_oeuvre(prof, grat, lang, LEAD, "(max-width: 800px) 86vw, 40vw")}
        <canvas class="grattage__cire" aria-hidden="true"></canvas>
      </figure>
      <p class="grattage__aide"><span>{e(t["gratter"])}</span> <button type="button" class="lien-bouton" data-tout-reveler>{e(t["tout_reveler"])}</button></p>
      {cartel(OEUVRES[grat], lang, "p")}
    </div>
  </div>
</section>

<section class="strates-accueil" data-strate="{e(lead["titre"][lang])}">
  <div class="strates-accueil__tete">
    {surtitre("The series, layer by layer" if not fr else "Les séries, couche après couche", 3)}
    <h2 class="titre-section">{lettres(lead["titre"][lang])}</h2>
    <p data-apparait>{e(S["texte"][lang])}</p>
    <p class="note" data-apparait>{e(S["sujets"][lang])}</p>
  </div>
  {colonne(lang, prof)}
</section>

<section class="atelier-maintenant" data-strate="{e("In the studio now" if not fr else "À l'atelier en ce moment")}">
  <div class="atelier-maintenant__images">
    {figure_photo(prof, "atelier/glacier-sur-le-chevalet", "A glacier painting on the easel, palette and brushes in the studio" if not fr else "Une peinture de glacier sur le chevalet, palette et pinceaux à l'atelier", "", "fossile atelier-maintenant__a", "(max-width: 800px) 60vw, 26vw")}
    <figure class="atelier-maintenant__b oeuvre" style="--ratio:{OEUVRES["en-cours-3"]["ratio"]}">{bouton_oeuvre(prof, "en-cours-3", lang, LEAD, "(max-width: 800px) 50vw, 20vw")}<figcaption class="cartel"><span class="cartel__titre">Emergence</span>{etat(OEUVRES["en-cours-3"], lang)}</figcaption></figure>
  </div>
  <div class="atelier-maintenant__texte">
    {surtitre("In the studio now" if not fr else "À l'atelier en ce moment", 4)}
    <p class="atelier-maintenant__chevalet" data-apparait>{e(S["chevalet"][lang])}</p>
    <p data-apparait><a class="lien-fleche" href="{lien(lang, "studio", prof)}">{e(t["nav"]["studio"])} →</a></p>
  </div>
</section>

<section class="editions-accueil" id="editions-accueil" data-strate="{e(E["titre"][lang])}">
  <div class="editions-accueil__texte">
    {surtitre(E["titre"][lang], 5)}
    <h2 class="titre-section">{lettres("Small blocks, held in acrylic" if not fr else "De petits blocs, pris dans l'acrylique")}</h2>
    <p data-apparait>{e(E["texte"][lang])}</p>
    <p class="note" data-apparait>{e(E["datation"][lang])}</p>
    <p data-apparait>{bouton(t["nav"]["editions"], lien(lang, "boutique", prof, "#editions"), "bouton bouton--atelier")}{bouton("Prints · creativehub" if not fr else "Tirages · creativehub", lien(lang, "boutique", prof, "#atelier"), "bouton bouton--ligne")}</p>
  </div>
  <ul class="editions-accueil__series">{editions}</ul>
  <p class="note editions-accueil__note">{e(E["a_venir"][lang])}</p>
</section>

<section class="presse-accueil" data-strate="{e(t["nav"]["presse"])}">
  <div class="presse-accueil__tete">
    {surtitre(t["nav"]["presse"], 6)}
    <blockquote class="citation-ft"><p data-mots>“{e(C.FT_CITATION)}”</p><footer>Rachel Spence, Financial Times, {"October" if not fr else "octobre"} 2017</footer></blockquote>
    {figure_photo(prof, "presse/ft-nyc-contrasts", "The Financial Times article with Lisa Cirenza's work" if not fr else "L'article du Financial Times avec l'œuvre de Lisa Cirenza", "", "fossile presse-accueil__ft", "(max-width: 800px) 70vw, 26vw")}
  </div>
  <ul class="presse-cartes">{cartes_presse}</ul>
  <p class="presse-accueil__tout">{bouton("All the press" if not fr else "Toute la presse", lien(lang, "presse", prof), "bouton bouton--ligne")}</p>
</section>

<section class="espace-accueil" data-strate="Espace Créa-Tea-Vité">
  <div class="espace-accueil__images">
    {figure_photo(prof, "espace/facade-de-nuit", "The Espace Créa-Tea-Vité at night, its windows lit" if not fr else "L'Espace Créa-Tea-Vité de nuit, vitrines allumées", "", "fossile espace-accueil__a", "(max-width: 800px) 92vw, 46vw")}
    {figure_photo(prof, "espace/table-vue-pistes", "A table by the window facing the ski slopes" if not fr else "Une table à la fenêtre, face aux pistes", "", "fossile espace-accueil__b", "(max-width: 800px) 50vw, 22vw")}
  </div>
  <div class="espace-accueil__texte">
    {surtitre(u["espace"] + (" · gallery · tea room · studio" if not fr else " · galerie · salon de thé · atelier"), 7)}
    <h2 class="titre-section">{lettres("Espace Créa-Tea-Vité")}</h2>
    <p data-apparait>{e(C.ESPACE["intro"][lang])}</p>
    <p class="note" data-apparait>{e(C.ESPACE["ecran"][lang])}</p>
    <div class="vapeur-statut" data-apparait><span class="vapeur" aria-hidden="true"><i></i><i></i><i></i></span>{statut(lang, "statut--grand")}</div>
    <p data-apparait>{bouton(t["nav"]["espace"], lien(lang, "espace", prof), "bouton bouton--espace")}{bouton(t["nav"]["cours_prives"], lien(lang, "cours_prives", prof), "bouton bouton--ligne")}</p>
  </div>
</section>

<section class="retraites-accueil" data-strate="{e(t["nav"]["retraites"])}">
  <div class="retraites-accueil__tete">
    {surtitre(u["espace"] + " · " + t["nav"]["retraites"].lower() + " 2027", 8)}
    <h2 class="titre-section">{lettres("Two retreats in 2027" if not fr else "Deux retraites en 2027")}</h2>
    <p data-apparait>{e(R.LOGEMENT[lang])}</p>
  </div>
  <div class="retraites-cartes retraites-cartes--deux">
    {"".join(carte_retraite(lang, prof, RETRAITES[k], k, RETRAITES[k]["photo_carte"]) for k in RETRAITES_ORDRE)}
  </div>
  <p class="retraites-accueil__prix" data-apparait>{e(R.REDUCTIONS[lang])} <a class="lien-fleche" href="{lien(lang, "conditions", prof)}">{e("Payment and cancellation" if not fr else "Paiement et annulation")} →</a></p>
</section>
{lettre_info(lang, prof)}
'''
    pre = (asset(prof, f"img/oeuvres/{hero}-1600.webp"), srcset_oeuvre(prof, hero), sizes_hero)
    ecrire(chemin, page(lang, "accueil", chemin, t["accroche"], corps, autre, {"accueil": True}, "page-accueil", preload=pre))


def carte_presse(lang, prof, p, sizes, avec_texte=False):
    url = p["url"]
    cible = f' href="{url}" target="_blank" rel="noopener"' if url else f' href="{lien(lang, "presse", prof, "#" + (p.get("ancre") or ("m2616" if p.get("a_paraitre") else "ft")))}"'
    neuf = f'<span class="presse-carte__neuf">{e("New" if lang == "en" else "Nouveau")}</span>' if p.get("nouveau") else ""
    texte = f'<span class="presse-carte__texte">{e(L(lang, p["texte"]))}</span>' if avec_texte else ""
    return (f'<li class="presse-carte" data-incline><a{cible}>'
            f'<span class="presse-carte__img">{img_photo(prof, p["image"], "", sizes)}{neuf}</span>'
            f'<span class="presse-carte__media">{e(p["media"])}</span><span class="presse-carte__titre">{e(p["titre"])}</span>'
            f'<span class="presse-carte__date">{e(L(lang, p["date"]) or "")}</span>{texte}</a></li>')


BIO_LEGENDE = {"en": "Lisa, aged four", "fr": "Lisa à 4 ans"}


def places(lang, cle, classe=""):
    """Jauge des places (exemples tant que Lisa n'a pas donné les chiffres ; sur le site final : collection Wix « Retraites »)."""
    p = R.PLACES.get(cle)
    if not p:
        return ""
    total, pris = p["total"], p["reservees"]
    reste = max(0, total - pris)
    fr = lang == "fr"
    if reste == 0:
        txt = "Full · waiting list" if not fr else "Complet · liste d'attente"
    elif pris == 0:
        txt = f"Bookings open · {total} places" if not fr else f"Inscriptions ouvertes · {total} places"
    elif reste <= 2:
        txt = (f"Last {reste} places" if reste > 1 else "Last place") if not fr else (f"Plus que {reste} places" if reste > 1 else "Dernière place")
    elif pris * 2 >= total:
        txt = f"Half full · {reste} places left" if not fr else f"À moitié complète · {reste} places restantes"
    else:
        txt = f"{reste} places left" if not fr else f"{reste} places restantes"
    ex = f'<span class="exemple">{"example" if not fr else "exemple"}</span>' if p.get("exemple") else ""
    return (f'<span class="places {classe}" data-places="{pris}/{total}" style="--rempli:{pris / total:.3f}">'
            f'<span class="places__jauge" aria-hidden="true"><i></i></span><span class="places__txt">{e(txt)}</span>{ex}</span>')


def carte_retraite(lang, prof, r, cle, photo):
    t = C.T[lang]
    bientot = f'<span class="etiquette etiquette--cours">{e(L(lang, r["bientot"]))}</span>' if r.get("bientot") else ""
    return f'''<article class="carte-retraite" data-incline>
  <a href="{lien(lang, cle, prof)}">
    <span class="carte-retraite__img">{img_photo(prof, photo, "", "(max-width: 800px) 92vw, 40vw")}</span>
    <span class="carte-retraite__haut">{compte(lang, r["debut"])}{bientot}</span>
    <span class="carte-retraite__titre">{e(nom_retraite(r, lang))}</span>
    <span class="carte-retraite__dates">{e(L(lang, r["dates"]))} · {e(L(lang, r["lieu"]))}</span>
    <span class="carte-retraite__prix">{e(L(lang, r["prix"]))}</span>
  </a>
</article>'''


def lettre_info(lang, prof):
    t = C.T[lang]
    return f'''<section class="lettre" data-strate="{e("Newsletter" if lang == "en" else "Lettre d'information")}">
  <div class="lettre__contenu">
    <h2 class="titre-section">{lettres("Musings, Invites, and Updates" if lang == "en" else "Pensées, invitations et nouvelles")}</h2>
    <p data-apparait>{e("New work, collectors' editions and retreats: be the first to know." if lang == "en" else "L'Espace, ses cours, ses événements et ses rendez-vous : soyez informé en premier.")}</p>
    <form class="lettre__form" data-lettre novalidate>
      <label class="vh" for="lettre-email">Email</label>
      <input id="lettre-email" type="email" name="email" autocomplete="email" placeholder="{e("your@email.com" if lang == "en" else "votre@adresse.fr")}" required>
      <input type="hidden" name="liste" value="{"en-collectionneurs-retraites" if lang == "en" else "fr-espace"}">
      <button class="bouton aimant" type="submit"><span>{e("Subscribe" if lang == "en" else "S'inscrire")}</span></button>
      <p class="lettre__liste">{e(C.LISTES_LETTRE[lang])}</p>
      <p class="lettre__merci" hidden tabindex="-1">{e("Thanks! (Mock-up: no email is sent; on the live site, Mailchimp.)" if lang == "en" else "Merci ! (Maquette : aucune adresse n'est envoyée ; sur le site en ligne, Mailchimp.)")}</p>
    </form>
  </div>
</section>'''


# ================================================================ œuvres
def page_oeuvres(lang):
    t = C.T[lang]
    fr = lang == "fr"
    chemin = fichier(lang, "oeuvres")
    prof = prof_de(chemin)

    def index_serie(sid):
        s = SERIES[sid]
        vs = "".join(vignette(prof, oid, lang, sid) for oid in LISTES[sid])
        manque = ""
        if s.get("sans_image"):
            manque = "".join(f'<figure class="vignette vignette--vide"><span class="oeuvre__toile vide"><span>{e("Image to be requested" if not fr else "Visuel à demander")}</span></span><figcaption><span class="cartel__titre">{e(x["titre"])}</span></figcaption></figure>' for x in s["sans_image"])
        return f'<section class="index-serie" data-strate="{e(s["titre"][lang])}"><h3><a href="{lien_salle(lang, sid, prof)}">{e(s["titre"][lang])}</a> <small>{e(n_oeuvres(len(LISTES[sid]), lang))}</small></h3><div class="index-serie__grille">{vs}{manque}</div></section>'
    lead = SERIES[LEAD]
    n_archive = sum(len(LISTES[x]) for x in ARCHIVE)
    corps = f'''
{bandeau(lang, prof, None, n_oeuvres(len(LISTES[LEAD]), lang) + " · " + lead["titre"][lang], t["nav"]["oeuvres"], [C.SERIE_ACTUELLE["texte"][lang], C.SERIE_ACTUELLE["sujets"][lang]], f'<div class="bandeau__texture">{bouton_oeuvre(prof, "recente-04", lang, LEAD, "(max-width: 900px) 80vw, 40vw")}</div>', t["nav"]["oeuvres"], "bandeau--oeuvres")}
<section class="declaration declaration--oeuvres" data-strate="{e(t["nav"]["declaration"])}">
  <div class="declaration__tete">{surtitre("Artist statement" if not fr else "Déclaration d'artiste")}<blockquote class="declaration__citation"><p>{e(C.POSITION["citation"][lang])}</p></blockquote></div>
  <div class="declaration__texte"><p data-apparait>{e(C.DECLARATION[lang][0])}</p><p><a class="lien-fleche" href="{lien(lang, "artiste", prof, "#declaration")}">{e("Read the full statement" if not fr else "Lire toute la déclaration")} →</a></p></div>
</section>
<section class="oeuvres-colonne" data-strate="{e("Stratigraphic column" if not fr else "Colonne stratigraphique")}">
  {colonne(lang, prof)}
</section>
<section class="index-oeuvres" data-strate="{e(lead["titre"][lang])}">
  <div class="index-oeuvres__tete">{surtitre(lead["titre"][lang] + (" · recent work" if not fr else " · œuvres récentes"), 1)}<h2 class="titre-section">{lettres(lead["titre"][lang])}</h2><p data-apparait>{e(C.SERIE_ACTUELLE["chevalet"][lang])}</p></div>
  {index_serie(LEAD)}
</section>
<section class="index-oeuvres index-oeuvres--archive" id="archive" tabindex="-1" data-strate="{e(t["nav"]["archive"])}">
  <div class="index-oeuvres__tete">{surtitre(t["nav"]["archive"] + " · " + n_oeuvres(n_archive, lang), 2)}<h2 class="titre-section">{lettres(t["nav"]["archive"])}</h2><p data-apparait>{e(C.SERIE_ACTUELLE["archive"][lang])}</p></div>
  {"".join(index_serie(sid) for sid in ARCHIVE)}
  <p class="note index-oeuvres__base">{e("Catalogue kept in Artwork Archive, the artist's inventory: titles, sizes, years, media, prices and availability come from it. Untitled works are awaiting their Artwork Archive entry." if not fr else "Catalogue tenu dans Artwork Archive, l'inventaire de l'artiste : titres, dimensions, années, techniques, prix et disponibilités en viennent. Les œuvres sans titre attendent leur fiche Artwork Archive.")}</p>
</section>'''
    ecrire(chemin, page(lang, "oeuvres", chemin, t["nav"]["oeuvres"], corps, href_autre(lang, "oeuvres", prof), {}, "page-oeuvres"))


def page_salle(lang, sid):
    t = C.T[lang]
    s = SERIES[sid]
    chemin = f"{C.DOSSIER_SALLES[lang]}/{s['slug'][lang]}.html"
    prof = prof_de(chemin)
    idx = ORDRE.index(sid)
    suivante = ORDRE[(idx + 1) % len(ORDRE)]
    ids = LISTES[sid]
    items = []
    groupes = {g["ids"][0]: g for g in s.get("groupes", [])}
    for oid in ids:
        if oid in groupes:
            g = groupes[oid]
            items.append(f'<div class="passage"><p class="passage__titre">{e(g[lang])}</p><p class="passage__n">{e(n_oeuvres(len(g["ids"]), lang))}</p></div>')
        items.append(figure_oeuvre(prof, oid, lang, sid))
    for x in s.get("sans_image", []):
        items.append(f'<figure class="oeuvre oeuvre--vide" style="--ratio:0.8;--s:8"><span class="oeuvre__toile vide"><span>{e("Image to be requested" if lang == "en" else "Visuel à demander")}</span></span><figcaption class="cartel"><span class="cartel__titre">{e(x["titre"])}</span><span class="cartel__faits">{e(t["a_completer"])}</span></figcaption></figure>')
    contexte = "".join(figure_photo(prof, c, "", "", "fossile salle__contexte", "(max-width: 800px) 60vw, 22vw") for c in s.get("contexte", [])[:1])
    periode = L(lang, s["periode"]) if s.get("periode") else None
    meta = n_oeuvres(len(ids) + len(s.get("sans_image", [])), lang) + (f" · {periode}" if periode else "")
    sous = L(lang, s["sous_titre"]) if s.get("sous_titre") else ""
    valider = f'<p class="note">{e("This page is published on the current site but missing from its menu: to be validated with the artist." if lang == "en" else "Page publiée sur le site actuel mais absente de son menu : à valider avec l'artiste.")}</p>' if s.get("a_valider") else ""
    corps = f'''
<section class="salle" data-piste data-strate="{e(s["titre"][lang])}" style="--fond-salle:{OEUVRES[ids[0]]["fond"]}">
  <div class="salle__collant">
    <div class="salle__piste">
      <div class="salle__entree" data-fond="{OEUVRES[ids[0]]["fond"]}">
        {surtitre((t["nav"]["archive"] + " · " if s.get("archive") else "") + f'{t["strate"]} {idx + 1:02d} · {meta}')}
        <h1 class="salle__titre">{lettres(s["titre"][lang])}</h1>
        {f'<p class="salle__sous">{e(sous)}</p>' if sous else ""}
        <p class="salle__texte" data-apparait>{e(s["texte"][lang])}</p>
        {valider}
        <div class="salle__contextes">{contexte}</div>
        <p class="salle__aide" aria-hidden="true">{"Keep scrolling: the room moves sideways" if lang == "en" else "Continuez à défiler : la salle glisse de côté"} <i></i></p>
      </div>
      {"".join(items)}
      <div class="salle__sortie">
        <p class="surtitre"><span>{e("Next stratum" if lang == "en" else "Strate suivante")}</span></p>
        <a class="salle__suivante aimant" href="{lien_salle(lang, suivante, prof)}"><span>{e(SERIES[suivante]["titre"][lang])}</span> →</a>
        <a class="lien-simple" href="{lien(lang, "oeuvres", prof)}">{e("All the series" if lang == "en" else "Toutes les séries")}</a>
      </div>
    </div>
    <div class="salle__progres" aria-hidden="true"><i></i></div>
  </div>
</section>'''
    ecrire(chemin, page(lang, "salle", chemin, s["titre"][lang], corps, href_autre(lang, "salle", prof, sid), {"salle": sid}, "page-salle", image_og=asset(prof, f"img/oeuvres/{ids[0]}-1600.webp")))


# ================================================================ l'artiste
def page_artiste(lang):
    t = C.T[lang]
    fr = lang == "fr"
    chemin = fichier(lang, "artiste")
    prof = prof_de(chemin)
    P = C.POSITION
    couches = []
    for i, b in enumerate(C.BIO_LONGUE):
        img = figure_photo(prof, b["photo"], L(lang, b.get("legende", "")), L(lang, b.get("legende", "")), "fossile carottage__img", "(max-width: 800px) 80vw, 30vw")
        couches.append(f'''<li class="carottage__couche" style="--i:{i}" data-strate="{e(b["titre"][lang])}">
  <div class="carottage__repere"><span class="carottage__n">{i + 1:02d}</span></div>
  <div class="carottage__texte"><h3>{e(b["titre"][lang])}</h3><p data-apparait>{e(b["texte"][lang])}</p></div>
  <div class="carottage__images">{img}</div>
</li>''')
    em = OEUVRES["en-cours-3"]
    corps = f'''
<section class="bandeau bandeau--artiste" data-strate="{e(t["nav"]["artiste"])}">
  <div class="bandeau__texte">
    {surtitre(P["titre"][lang])}
    <h1 class="bandeau__titre">{lettres("Lisa Cirenza")}</h1>
    <div class="bandeau__intro" data-apparait><p>{e(P["ligne"][lang])}</p><p class="bandeau__matieres">{e(P["matieres"][lang])}</p></div>
    <p class="bandeau__liens" data-apparait><a href="#declaration">{e(t["nav"]["declaration"])}</a> · <a href="#bio">{e(t["nav"]["bio"])}</a> · <a href="{lien(lang, "parcours", prof)}">{e(t["nav"]["parcours"])}</a> · <a href="{lien(lang, "presse", prof)}">{e(t["nav"]["presse"])}</a></p>
  </div>
  <figure class="bandeau__image bandeau__image--oeuvre" style="--ratio:{em["ratio"]}">{bouton_oeuvre(prof, "en-cours-3", lang, LEAD, "(max-width: 900px) 80vw, 36vw", "", "eager", True)}<figcaption class="cartel"><span class="cartel__titre">Emergence</span><span class="cartel__faits">{e(faits_courts(em, lang))}</span>{etat(em, lang)}</figcaption></figure>
</section>

<section class="declaration" id="declaration" tabindex="-1" data-strate="{e(t["nav"]["declaration"])}">
  <div class="declaration__tete">
    {surtitre("Artist statement" if not fr else "Déclaration d'artiste", 1)}
    <h2 class="titre-section">{lettres(t["nav"]["declaration"])}</h2>
    <blockquote class="declaration__citation"><p>{e(P["citation"][lang])}</p></blockquote>
  </div>
  <div class="declaration__texte">{"".join(f'<p data-apparait>{e(x)}</p>' for x in C.DECLARATION[lang])}</div>
  {figure_photo(prof, "atelier/detail-cire-blanche", "Detail of a glacier canvas: white and grey wax worked into ridges, with a pool of blue-green beneath" if not fr else "Détail d'une toile de glacier : cire blanche et grise travaillée en crêtes, avec une poche bleu-vert dessous", "Wax as a geological membrane, detail" if not fr else "La cire comme membrane géologique, détail", "fossile declaration__photo", "(max-width: 800px) 60vw, 22vw")}
</section>

<section class="carottage" id="bio" tabindex="-1" data-strate="{e(t["nav"]["bio"])}">
  <div class="carottage__tete">{surtitre("Long bio" if not fr else "Biographie", 2)}<h2 class="titre-section">{lettres("Layers of a life" if not fr else "Les couches d'une vie")}</h2></div>
  <ol class="carottage__liste" data-carottage>{"".join(couches)}</ol>
</section>

<section class="matieres" data-strate="{e("Water, pigments, heat and wax" if not fr else "L'eau, les pigments, la chaleur et la cire")}">
  <div class="matieres__texte">
    {surtitre("My materials" if not fr else "Mes matières", 3)}
    <h2 class="titre-section">{lettres(P["matieres"][lang].rstrip("."))}</h2>
    <p data-apparait>{e(C.MEMBRANE[lang])}</p>
    {videos_procede(lang)}
    <p class="note" data-apparait hidden>{e("Short videos of the process, in English with French captions: to come." if not fr else "Courtes vidéos du procédé, en anglais sous-titrées en français : à venir.")}</p>
  </div>
  <ul class="matieres__photos">
    <li>{figure_photo(prof, "atelier/chalumeau-encaustique", "The blowtorch flame fusing wax" if not fr else "La flamme du chalumeau qui fusionne la cire", "Heat" if not fr else "La chaleur", "fossile", "(max-width: 800px) 46vw, 20vw")}</li>
    <li>{figure_photo(prof, "atelier/melange-resines-pigments-cire", "Mixing resins, pigments and beeswax" if not fr else "Mélange de résines, de pigments et de cire d'abeille", "Pigments and wax" if not fr else "Les pigments et la cire", "fossile", "(max-width: 800px) 46vw, 20vw")}</li>
    <li>{figure_photo(prof, "atelier/detail-cire-blanche", "Close-up of a scraped white wax surface" if not fr else "Gros plan d'une surface de cire blanche grattée", "Surface" if not fr else "La surface", "fossile", "(max-width: 800px) 46vw, 20vw")}</li>
    <li>{figure_photo(prof, "atelier/encaustique-noir-et-blanc-sur-papier", "Black and white wax on paper" if not fr else "Cire en noir et blanc sur papier", "Wax on paper" if not fr else "Cire sur papier", "fossile", "(max-width: 800px) 46vw, 20vw")}</li>
  </ul>
</section>

<section class="dossier" data-strate="{e("Press kit" if not fr else "Dossier de presse")}">
  <div class="dossier__bio">
    {surtitre("Short bio · for press and applications" if not fr else "Bio courte · pour la presse et les candidatures", 4)}
    <p data-apparait>{e(C.BIO_COURTE[lang])}</p>
  </div>
  <div class="dossier__liens">
    <p class="note">{e(C.PDF_A_VENIR["presse"][lang])}</p>
    <p class="note">{e(C.PDF_A_VENIR["cv"][lang])}</p>
    <p class="note">{e("High-resolution images: on request." if not fr else "Images en haute définition : sur demande.")}</p>
    <p>{bouton(t["nav"]["parcours"], lien(lang, "parcours", prof))}{bouton(t["nav"]["presse"], lien(lang, "presse", prof), "bouton bouton--ligne")}{bouton(t["nav"]["contact"], lien(lang, "contact", prof), "bouton bouton--ligne")}</p>
  </div>
</section>'''
    corps = avec_carnet(corps, lang, prof, "artiste")
    ecrire(chemin, page(lang, "artiste", chemin, t["nav"]["artiste"], corps, href_autre(lang, "artiste", prof), {}, "page-artiste"))


def an(label):
    return int(label[:4]) if label[:4].isdigit() else 0


def page_parcours(lang):
    t = C.T[lang]
    fr = lang == "fr"
    chemin = fichier(lang, "parcours")
    prof = prof_de(chemin)
    CVd = C.CV
    entrees = ([(a, x[lang], "solo" if x["en"].startswith("Solo") else None) for a, x in CVd["expositions"]]
               + [(a, x[lang], "foire") for a, x in CVd["foires"]]
               + [(a, x[lang], "residence") for a, x in CVd["distinctions"]]
               + [(a, x[lang], "talk") for a, x in CVd["conferences"]])
    labels = sorted({a for a, *_ in entrees}, key=lambda a: (an(a), a), reverse=True)
    couches = []
    for i, a in enumerate(labels):
        lis = "".join(f'<li class="fossile-txt{" fossile-txt--" + k if k else ""}"><span>{e(x)}</span></li>' for b, x, k in entrees if b == a)
        ph = C.PHOTOS_ANNEES.get(an(a))
        img = figure_photo(prof, ph, "", "", "fossile couche__img", "(max-width: 800px) 60vw, 18vw") if ph and a == str(an(a)) else ""
        couches.append(f'<li class="couche" style="--i:{i}" data-strate="{e(a)}"><p class="couche__annee">{e(a)}</p><ul class="couche__fossiles">{lis}</ul>{img}</li>')
    legende = ("Exhibition" if not fr else "Exposition", "Solo exhibition" if not fr else "Exposition personnelle", "Art fair" if not fr else "Foire", "Honour, prize, residency" if not fr else "Distinction, prix, résidence", "Talk" if not fr else "Conférence")

    def bloc(titre_bloc, items):
        return f'<section class="cv-bloc"><h3>{e(titre_bloc)}</h3><ul class="liste-traits">{"".join(f"<li>{e(x[lang])}</li>" for x in items)}</ul></section>'
    corps = f'''
{bandeau(lang, prof, None, "CV highlights · newest first" if not fr else "Parcours sélectif · le plus récent d'abord", t["nav"]["parcours"], [C.BIO_LONGUE[0]["texte"][lang]], figure_photo(prof, "expositions/salon-beaux-arts-galerie", "A Salon exhibition hang in Paris" if not fr else "L'accrochage d'un Salon à Paris", "", "fossile", "(max-width: 900px) 80vw, 40vw"), t["nav"]["parcours"])}
<section class="cv-blocs" data-strate="{e("Education and collections" if not fr else "Formation et collections")}">
  {bloc("Education and research" if not fr else "Formation et recherche", CVd["formation"])}
  {bloc("Collections" if not fr else "Collections", CVd["collections"])}
  {bloc("Press" if not fr else "Presse", CVd["presse"])}
  {bloc("Publications" if not fr else "Publications", CVd["publications"])}
</section>
<section class="frise" data-strate="{e("Exhibitions, fairs, honours, talks" if not fr else "Expositions, foires, distinctions, conférences")}">
  {surtitre("Exhibitions, art fairs, honours and talks" if not fr else "Expositions, foires, distinctions et conférences")}
  <ul class="frise__legende" aria-label="{e("Legend" if not fr else "Légende")}"><li class="fossile-txt">{e(legende[0])}</li><li class="fossile-txt fossile-txt--solo">{e(legende[1])}</li><li class="fossile-txt fossile-txt--foire">{e(legende[2])}</li><li class="fossile-txt fossile-txt--residence">{e(legende[3])}</li><li class="fossile-txt fossile-txt--talk">{e(legende[4])}</li></ul>
  <p class="frise__avenir">{e(CVd["a_venir"][lang])}</p>
  <ol class="frise__couches" data-frise>{"".join(couches)}</ol>
  <p class="note">{e(C.PDF_A_VENIR["cv"][lang])}</p>
</section>'''
    corps = avec_carnet(corps, lang, prof, "parcours")
    ecrire(chemin, page(lang, "parcours", chemin, t["nav"]["parcours"], corps, href_autre(lang, "parcours", prof), {}, "page-parcours"))


def page_presse(lang):
    t = C.T[lang]
    chemin = fichier(lang, "presse")
    prof = prof_de(chemin)
    cartes = "".join(carte_presse(lang, prof, p, "(max-width: 700px) 70vw, 24vw", True) for p in C.PRESSE if not p.get("archive"))
    cartes_archive = "".join(carte_presse(lang, prof, p, "(max-width: 700px) 60vw, 18vw", True) for p in C.PRESSE if p.get("archive"))
    videos = "".join(f'<li><a href="{v["url"]}" target="_blank" rel="noopener"><strong>{e(v["titre"])}</strong><span>{e(v["auteur"])} · {e(L(lang, v["date"]))}</span></a></li>' for v in C.VIDEOS)
    WF, M = C.WAX_FUSION, C.M2616
    traduit = (lambda cle: "" if lang == "fr" else f'<p class="voix__trad" lang="en">{e(M[cle]["en"])}</p>')
    corps = f'''
{bandeau(lang, prof, None, "Reviews, features, films" if lang == "en" else "Critiques, articles, films", t["nav"]["presse"], ["The Financial Times, the BBC and Maisons et Jardins; in 2026, a feature in Wax Fusion and a portrait in M2616.", C.PDF_A_VENIR["presse"]["en"] + "."] if lang == "en" else ["Le Financial Times, la BBC et Maisons et Jardins ; en 2026, un dossier dans Wax Fusion et un portrait dans M2616.", C.PDF_A_VENIR["presse"]["fr"] + "."], figure_photo(prof, "presse/wax-fusion-fall-2026-article", "Opening page of Beyond the Surface by Lisa Cirenza in Wax Fusion, Fall 2026" if lang == "en" else "Première page de Beyond the Surface, de Lisa Cirenza, dans Wax Fusion, automne 2026", "Wax Fusion · " + ("Fall 2026, p. 18" if lang == "en" else "automne 2026, p. 18"), "fossile", "(max-width: 900px) 70vw, 32vw"), t["nav"]["presse"])}
<section class="podcast" id="podcast" tabindex="-1" data-strate="Podcast">
  <div class="podcast__texte">
    {surtitre("Podcast · " + ("November 2026" if lang == "en" else "novembre 2026"))}
    <h2 class="titre-section">{lettres("A new podcast interview" if lang == "en" else "Un nouvel entretien en podcast")}</h2>
    <p data-apparait>{e(C.PRESSE[0]["texte"][lang])}</p>
    <p class="podcast__lecteur"><span class="podcast__bouton" aria-hidden="true">▶</span><span>{e("The player will load here, on click only, once the link arrives (Spotify, Apple Podcasts or the show's own page)." if lang == "en" else "Le lecteur se chargera ici, au clic seulement, dès que le lien sera arrivé (Spotify, Apple Podcasts ou la page de l'émission).")}</span></p>
  </div>
</section>
<section class="wax-fusion" id="wax-fusion" tabindex="-1" data-strate="Wax Fusion">
  <div class="wax-fusion__couv">{figure_photo(prof, "presse/wax-fusion-fall-2026-couverture", "Cover of Wax Fusion, Fall 2026, issue XIV" if lang == "en" else "Couverture de Wax Fusion, automne 2026, n° XIV", "", "fossile", "(max-width: 800px) 70vw, 28vw", ' data-incline')}</div>
  <div class="wax-fusion__texte">
    {surtitre(WF["numero"][lang], 1)}
    <h2 class="titre-section">{lettres(WF["titre"])}</h2>
    <p class="wax-fusion__sous">{e(WF["sous_titre"])}</p>
    <blockquote class="voix__c voix__c--grand"><p data-mots>{e(WF["graines"][lang])}</p></blockquote>
    <p data-apparait>{e(WF["espace"][lang])}</p>
    <p data-apparait>{e("In the feature: Emergence, Seaside Village and the Pink Flowers, Stand Tall and Face the Light and Rose Coloured Glasses, with their materials and processes." if lang == "en" else "Dans l'article : Emergence, Seaside Village and the Pink Flowers, Stand Tall and Face the Light et Rose Coloured Glasses, avec leurs matériaux et leurs procédés.")}</p>
    <p data-apparait><a class="bouton aimant" href="{WF["url"]}" target="_blank" rel="noopener"><span>{e("Read the issue (from p. 18)" if lang == "en" else "Lire le numéro (dès la p. 18)")}</span></a>{bouton("See the works" if lang == "en" else "Voir les œuvres", lien_salle(lang, "hope-and-optimism", prof), "bouton bouton--ligne")}</p>
  </div>
</section>
<section class="m2616" id="m2616" tabindex="-1" data-strate="M2616">
  <div class="m2616__texte">
    {surtitre("M2616 · " + ("La Clusaz lifestyle magazine · December 2026, forthcoming" if lang == "en" else "magazine art de vivre de La Clusaz · décembre 2026, à paraître"), 2)}
    <h2 class="titre-section" lang="fr">{lettres(M["titre"])}</h2>
    <p class="m2616__portrait" lang="fr" data-apparait>{e(M["portrait"]["fr"])}</p>
    {"" if lang == "fr" else f'<p class="voix__trad">{e(M["portrait"]["en"])}</p>'}
    <blockquote class="voix__c voix__c--fr" lang="fr" data-apparait><p>«&nbsp;{e(M["sanctuaire"]["fr"])}&nbsp;»</p>{traduit("sanctuaire")}</blockquote>
    <blockquote class="voix__c voix__c--fr" lang="fr" data-apparait><p>«&nbsp;{e(M["village"]["fr"])}&nbsp;»</p>{traduit("village")}</blockquote>
    <p class="note">{e("Magazine name, page and link to be confirmed on publication. Quotes from the text sent by the artist." if lang == "en" else "Nom du magazine, page et lien à confirmer à la parution. Citations tirées du texte transmis par l'artiste.")}</p>
  </div>
  {figure_photo(prof, "espace/enseigne-rue-village", "The Créa-Tea-Vité sign in the village street" if lang == "en" else "L'enseigne Créa-Tea-Vité dans la rue du village", "", "fossile m2616__img", "(max-width: 800px) 80vw, 30vw", ' data-parallaxe="-0.05"')}
</section>
<section class="ft" id="ft" tabindex="-1" data-strate="Financial Times">
  {figure_photo(prof, "presse/financial-times", "The Financial Times page with Lisa Cirenza's work" if lang == "en" else "La page du Financial Times avec l'œuvre de Lisa Cirenza", "", "fossile ft__img", "(max-width: 800px) 80vw, 30vw")}
  <div class="ft__texte">{surtitre("Financial Times · Rachel Spence · " + ("October 2017" if lang == "en" else "octobre 2017"))}<h2 class="ft__titre">London's best satellite fairs: ‘different conversations and collegiate feel’</h2><blockquote class="citation-ft"><p data-mots>“{e(C.FT_CITATION)}”</p></blockquote>
  <p data-apparait>{e("The work reproduced in the article is in the Beneath the Surface room of the Archive." if lang == "en" else "L'œuvre reproduite dans l'article est dans la salle Beneath the Surface de l'Archive.")}</p>
  <p data-apparait>{bouton("See the work" if lang == "en" else "Voir l'œuvre", lien_salle(lang, "beneath-the-surface", prof) + "?oeuvre=nyc-contrasts", "bouton bouton--ligne")}</p></div>
</section>
<section class="presse-mur" data-strate="{e("Press wall" if lang == "en" else "Revue de presse")}">
  <ul class="presse-cartes presse-cartes--mur">{cartes}</ul>
  <details class="presse-archive">
    <summary>{e("Earlier press and films (archive)" if lang == "en" else "Presse et films plus anciens (archive)")}</summary>
    <ul class="presse-cartes presse-cartes--archive">{cartes_archive}</ul>
    <ul class="videos__liste">{videos}</ul>
  </details>
</section>'''
    ecrire(chemin, page(lang, "presse", chemin, t["nav"]["presse"], corps, href_autre(lang, "presse", prof), {}, "page-presse"))


# ================================================================ carnets de photos (bandes qui glissent au défilement)
CARNETS = {
    "cours": {
        "sur": ("Classes, as they happen", "Les cours, sur le vif"),
        "titre": ("In the studio", "À l'atelier"),
        "photos": [
            ("cours/atelier-cartes-de-voeux", "A participant painting small cards at the studio table", "Une participante peint de petites cartes à la table de l'atelier"),
            ("cours/groupe-cartes-de-voeux", "A group of participants holding up their painted cards", "Un groupe de participants montre ses cartes peintes"),
            ("cours/atelier-cartes-de-voeux-couple", "Two participants showing their painted cards", "Deux participants montrent leurs cartes peintes"),
            ("cours/eleves-montrent-leurs-toiles", "Participants showing their finished paintings", "Des participantes montrent leurs toiles terminées"),
            ("cours/table-aquarelle-2", "Watercolour palettes and sketches spread on the long table", "Palettes d'aquarelle et esquisses sur la grande table"),
            ("cours/eleve-aquarelle-montagne", "A participant painting a mountain in watercolour", "Une participante peint une montagne à l'aquarelle"),
            ("cours/demo-aquarelle-automne", "Autumn leaves in watercolour, palette and brushes", "Feuilles d'automne à l'aquarelle, palette et pinceaux"),
            ("cours/carnet-de-voyage-aquarelle", "A watercolour travel sketchbook with its paint box", "Un carnet de voyage à l'aquarelle et sa boîte de couleurs"),
            ("cours/atelier-fusain", "Charcoal drawings in progress around the table", "Dessins au fusain en cours autour de la table"),
            ("cours/table-dessin-cheminee", "A drawing table by the fireplace", "Une table à dessin près de la cheminée"),
            ("cours/eleve-theorie-des-couleurs", "A participant presenting colour studies at the easel", "Un participant présente ses études de couleur au chevalet"),
        ],
    },
    "espace": {
        "sur": ("Life at the Espace", "La vie de l'Espace"),
        "titre": ("Around the gallery", "Autour de la galerie"),
        "photos": [
            ("espace/collectionneur-et-sculpteur", "Two visitors in conversation at a gallery table", "Deux visiteurs en conversation à une table de la galerie"),
            ("espace/salon-vertical", "The lounge, fireplace and bookshelves", "Le salon, la cheminée et la bibliothèque"),
            ("espace/tournage-video", "A video interview being filmed in the gallery", "Une interview vidéo filmée dans la galerie"),
            ("paysages/office-de-tourisme-la-clusaz", "The La Clusaz tourist office in summer flowers", "L'office de tourisme de La Clusaz fleuri en été"),
            ("paysages/brume-sur-la-neige", "Mist over the snow above La Clusaz", "La brume sur la neige au-dessus de La Clusaz"),
            ("paysages/nuages-telesiege", "A chairlift above a sea of clouds", "Un télésiège au-dessus d'une mer de nuages"),
        ],
    },
    "artiste": {
        "sur": ("Studio notes", "Carnet d'atelier"),
        "titre": ("Behind the work", "Derrière les œuvres"),
        "photos": [
            ("artiste/lisa-peint-un-glacier", "Lisa Cirenza painting a large glacier canvas", "Lisa Cirenza peint une grande toile de glacier"),
            ("atelier/home-sur-chevalet", "A painting on the easel among paints in the studio", "Une toile sur le chevalet, au milieu des couleurs de l'atelier"),
            ("atelier/video-rose-coloured-glasses", "Yellow wax spread across a panel in the studio", "De la cire jaune étalée sur un panneau à l'atelier"),
            ("atelier/video-hot-surface", "Working on a hot surface, thermometer at hand", "Travail sur surface chauffante, thermomètre à portée de main"),
            ("artiste/lisa-et-grand-portrait", "Lisa Cirenza beside a large portrait", "Lisa Cirenza à côté d'un grand portrait"),
            ("artiste/lisa-cascade-avec-son-chien", "Lisa Cirenza with her dog below a waterfall", "Lisa Cirenza et son chien au pied d'une cascade"),
        ],
    },
    "parcours": {
        "sur": ("On the walls", "Aux cimaises"),
        "titre": ("Salons and openings", "Salons et vernissages"),
        "photos": [
            ("expositions/salon-beaux-arts-2018-affiche", "Lisa Cirenza in front of the Salon des Beaux Arts 2018 poster", "Lisa Cirenza devant l'affiche du Salon des Beaux Arts 2018"),
            ("expositions/salon-beaux-arts-2019-affiche", "Salon des Beaux Arts 2019 poster, Carrousel du Louvre", "Affiche du Salon des Beaux Arts 2019, Carrousel du Louvre"),
            ("expositions/vernissage-grand-portrait", "Visitors at an opening, a large portrait on the wall", "Des visiteurs à un vernissage, un grand portrait au mur"),
        ],
    },
    "evenements": {
        "sur": ("Talks, team days and soirées", "Conférences, séminaires et soirées"),
        "titre": ("Past gatherings", "Rencontres passées"),
        "photos": [
            ("teambuilding/conference-tables-rondes", "A corporate event with round tables", "Un événement d'entreprise autour de tables rondes"),
            ("conferences/atelier-zetland-cires-jaunes", "A hot-wax workshop set up in a conference room", "Un atelier de cire chaude installé dans une salle de conférence"),
            ("conferences/performance-numerique-ecran-geant", "A live digital art performance on a giant screen", "Une performance d'art numérique en direct sur écran géant"),
            ("conferences/stem-to-steam-cuba", "A talk titled STEM to STEAM", "Une conférence intitulée STEM to STEAM"),
            ("evenements/apero-rencontre-regards-sur-cuba-affiche", "Poster for the Apéro-Rencontre « Regards sur Cuba »", "Affiche de l'Apéro-Rencontre « Regards sur Cuba »"),
            ("evenements/cuba-musiciens", "Musicians performing in Cuba", "Des musiciens en concert à Cuba"),
        ],
    },
    "retraites": {
        "sur": ("Where the retreats take place", "Là où se passent les retraites"),
        "titre": ("La Clusaz and Lake Annecy", "La Clusaz et le lac d'Annecy"),
        "photos": [
            ("paysages/lac-annecy-parapentes", "Paragliders above Lake Annecy", "Des parapentes au-dessus du lac d'Annecy"),
            ("retraites/randonnee-sentier", "Walkers on a mountain trail", "Des marcheurs sur un sentier de montagne"),
            ("paysages/route-des-aravis-au-soir", "The Aravis road in the evening light", "La route des Aravis dans la lumière du soir"),
            ("paysages/vaches-alpage-lumiere-doree", "Cows grazing in golden alpine light", "Des vaches en alpage dans la lumière dorée"),
            ("retraites/viennoiseries-petit-dejeuner", "Pastries for breakfast", "Des viennoiseries pour le petit-déjeuner"),
        ],
    },
}


def carnet(lang, prof, cle):
    c = CARNETS[cle]
    i = 0 if lang == "en" else 1
    items = []
    for src, en, fr in c["photos"]:
        w, h = MED["photos"][src]["800"]
        items.append(f'<li class="carnet__item" style="--r:{w / h:.4f}">{figure_photo(prof, src, en if lang == "en" else fr, "", "fossile carnet__img", "(max-width: 900px) 70vw, 30vw")}</li>')
    return (f'<section class="carnet" data-strate="{e(c["titre"][i])}">'
            f'<div class="carnet__tete">{surtitre(c["sur"][i])}<h2 class="titre-section">{lettres(c["titre"][i])}</h2></div>'
            f'<div class="carnet__fenetre"><ul class="carnet__piste" data-defile>{"".join(items)}</ul></div></section>')


def avec_carnet(corps, lang, prof, cle):
    k = corps.rfind("<section")
    bloc = carnet(lang, prof, cle) + "\n"
    return corps[:k] + bloc + corps[k:] if k > 0 else corps + bloc


# ================================================================ l'Espace
def page_espace(lang):
    t = C.T[lang]
    chemin = fichier(lang, "espace")
    prof = prof_de(chemin)
    offres = "".join(f'<li class="offre" data-incline>{figure_photo(prof, o["photo"], "", "", "fossile offre__img", "(max-width: 800px) 86vw, 28vw")}<h3>{e(o["titre"][lang])}</h3><p>{e(o["texte"][lang])}</p></li>' for o in C.ESPACE["offres"])
    carte = ""
    for g in C.CARTE:
        lis = ""
        for nom, prix, desc in g["items"]:
            lis += f'<li><span class="boisson__nom">{e(L(lang, nom))}</span><span class="boisson__points" aria-hidden="true"></span><span class="boisson__prix">{e(prix if lang == "fr" else prix.replace(",", "."))} €</span>{f"<span class=boisson__desc>{e(L(lang, desc))}</span>" if desc else ""}</li>'
        carte += f'<div class="carte-boissons__groupe"><h3>{e(g["titre"][lang])}</h3><ul>{lis}</ul></div>'
    ex = C.EXPO
    V = C.VIDEO_ESPACE
    expo_finie = DT.date.fromisoformat(ex["fin"]) < AUJ
    agenda = ""
    for a in C.AGENDA:
        etat_txt = ("Booking open" if lang == "en" else "Réservations ouvertes") if a["etat"] == "ouvert" else ("Ended" if lang == "en" else "Terminé")
        date = f'<span class="agenda__date">{e(L(lang, a["date"]))}</span>' if a.get("date") else ""
        agenda += f'<li class="agenda__item agenda__item--{a["etat"]}"><span class="agenda__groupe">{e(L(lang, a["groupe"]))}</span><strong>{e(a["titre"])}</strong>{date}<span>{e(L(lang, a["texte"]))}</span><span class="agenda__bas"><span class="etiquette{" etiquette--passe" if a["etat"] != "ouvert" else ""}">{e(etat_txt)}</span><span class="agenda__prix">{e(a["prix"])} €</span></span></li>'
    corps = f'''
<section class="bandeau bandeau--espace" data-strate="Espace Créa-Tea-Vité">
  <div class="bandeau__texte">
    {surtitre("27 Passage du Mont Blanc · La Clusaz")}
    <h1 class="bandeau__titre">{lettres("Espace Créa-Tea-Vité")}</h1>
    <div class="bandeau__intro" data-apparait><p>{e(C.ESPACE["intro"][lang])}</p><p class="note">{e(C.ESPACE["ecran"][lang])}</p></div>
    <div class="vapeur-statut" data-apparait><span class="vapeur" aria-hidden="true"><i></i><i></i><i></i></span>{statut(lang, "statut--grand")}</div>
  </div>
  <div class="bandeau__image"><span class="logo-espace">{f'<img src="{asset(prof, "img/logos/espace.webp")}" width="{C_LOGO[0]}" height="{C_LOGO[1]}" alt="Créa-Tea-Vité">'}</span></div>
</section>
<section class="panorama" data-panorama-pin data-strate="{e("Inside" if lang == "en" else "À l'intérieur")}">
  <div class="panorama__collant"><div class="panorama__piste">{img_photo(prof, "espace/panorama-interieur", "Panoramic view inside the Espace: gallery, tea room and studio" if lang == "en" else "Vue panoramique de l'Espace : galerie, salon de thé et atelier", "300vw")}</div></div>
</section>
<section class="histoire-espace" data-strate="{e("From L'Ourson to Créa-Tea-Vité" if lang == "en" else "De L'Ourson à Créa-Tea-Vité")}">
  <div class="video" data-video="{V["id"]}" data-video-h="{V["h"]}" data-effet="video">
    <button class="video__bouton" type="button" aria-label="{e(("Play the video: " if lang == "en" else "Lire la vidéo : ") + V["legende"][lang])}">
      {img_photo(prof, V["image"], "", "(max-width: 900px) 92vw, 52vw", "video__affiche")}
      <span class="video__jouer" aria-hidden="true"><i></i></span>
      <span class="video__duree">{e("Tour of the Espace" if lang == "en" else "Visite de l'Espace")}</span>
    </button>
    <p class="video__legende">{e(V["legende"][lang])} <span class="note">Vimeo</span></p>
  </div>
  <div class="histoire-espace__texte">
    {surtitre("From L'Ourson to Créa-Tea-Vité" if lang == "en" else "De L'Ourson à Créa-Tea-Vité", 1)}
    <h2 class="titre-section">{lettres("A refuge, by design" if lang == "en" else "Un refuge, pensé comme une œuvre")}</h2>
    <p data-apparait>{e(C.M2616["lourson"][lang])}</p>
    <blockquote class="voix__c" data-apparait><p>{e(C.WAX_FUSION["espace"][lang])}</p><footer>— Lisa Cirenza, Wax Fusion, 2026</footer></blockquote>
    <ul class="histoire-espace__details">
      <li data-apparait><span class="histoire-espace__picto" aria-hidden="true">🔔</span>{e(C.M2616["cloche"][lang])}</li>
      <li data-apparait><span class="histoire-espace__picto" aria-hidden="true">♪</span>{e(C.M2616["musique"][lang])}</li>
      <li data-apparait><span class="histoire-espace__picto" aria-hidden="true">✶</span>{e(C.M2616["demonstrations"][lang])}</li>
      <li data-apparait><span class="histoire-espace__picto" aria-hidden="true">⛷</span>{e(C.M2616["jeunes"][lang])}</li>
    </ul>
    <p class="note">{e("From the M2616 article (December 2026, forthcoming) and Wax Fusion (Fall 2026)." if lang == "en" else "D'après l'article de M2616 (décembre 2026, à paraître) et Wax Fusion (automne 2026).")}</p>
  </div>
</section>
<section class="offres" data-strate="{e("The space" if lang == "en" else "Le lieu")}">
  <div class="offres__tete">{surtitre("Create, connect, be inspired" if lang == "en" else "Créer, se rencontrer, s'inspirer", 2)}<h2 class="titre-section">{lettres(C.ESPACE["reve"][lang][0])}</h2><p data-apparait>{e(C.ESPACE["reve"][lang][1])}</p></div>
  <ul class="offres__liste">{offres}</ul>
</section>
<section class="espace-portes" data-strate="{e("At the Espace" if lang == "en" else "À l'Espace")}">
  {surtitre("At the Espace" if lang == "en" else "À l'Espace", 3)}
  <ul class="espace-portes__liste">
    <li><a href="{lien(lang, "salon_the", prof)}"><strong>{e(t["nav"]["salon_the"])}</strong><span>{e("Visit in person: the boutique, the tea menu, hours, map and parking." if lang == "en" else "Sur place : la boutique, la carte du salon de thé, les horaires, le plan et le stationnement.")}</span></a></li>
    <li><a href="{lien(lang, "cosessions", prof)}"><strong>{e(t["nav"]["cosessions"])}</strong><span>{e("Work on your own creative projects with personalised guidance, €30." if lang == "en" else "Avancez sur vos projets créatifs avec un accompagnement personnalisé, 30 €.")}</span></a></li>
    <li><a href="{lien(lang, "cours_prives", prof)}"><strong>{e(t["nav"]["cours_prives"])}</strong><span>{e(C.COURS_PRIVES["pour"][lang])}</span></a></li>
    <li><a href="{lien(lang, "evenements", prof)}"><strong>{e(t["nav"]["evenements"])}</strong><span>{e(C.EVENEMENTS["titre"][lang])}</span></a></li>
    <li><a href="{lien(lang, "expositions", prof)}"><strong>{e(t["nav"]["expositions"])}</strong><span>{e(C.EXPO["titre"] + " · " + C.EXPO["dates"][lang])}</span></a></li>
    <li><a href="{lien(lang, "retraites", prof)}"><strong>{e(t["nav"]["retraites"])}</strong><span>{e(" · ".join(nom_retraite(RETRAITES[k], lang) for k in RETRAITES_ORDRE))}</span></a></li>
  </ul>
</section>
{lettre_info(lang, prof)}'''
    corps = avec_carnet(corps, lang, prof, "espace")
    ecrire(chemin, page(lang, "espace", chemin, "Espace Créa-Tea-Vité", corps, href_autre(lang, "espace", prof), {"expoFin": ex["fin"]}, "page-espace"))


C_LOGO = MED["logos"]["espace"]


# ================================================================ cours
def page_cours(lang):
    t = C.T[lang]
    chemin = fichier(lang, "cours")
    prof = prof_de(chemin)
    at = "".join(f'<li class="atelier" data-incline style="--i:{i}">{figure_photo(prof, ph, "", "", "fossile atelier__img", "(max-width: 800px) 86vw, 26vw")}<p class="atelier__n">{i + 1:02d}</p><h3>{e(a[lang])}</h3><p>{e(b[lang])}</p></li>' for i, (a, b, ph) in enumerate(C.COURS["ateliers"]))
    eq = "".join(f'<li><h3>{e(a[lang])}</h3><p>{e(b[lang])}</p></li>' for a, b in C.COURS["equipes"])
    co = C.AGENDA[0]
    corps = f'''
{bandeau(lang, prof, None, "Private classes & workshops" if lang == "en" else "Cours privés et ateliers", t["nav"]["cours"], C.COURS["citation"][lang], figure_photo(prof, "cours/in-the-studio", "Students painting watercolours in the studio" if lang == "en" else "Des élèves peignent à l'aquarelle dans l'atelier", "", "fossile", "(max-width: 900px) 80vw, 36vw"), t["nav"]["cours"])}
<section class="ateliers" data-strate="{e("Private Atelier Sessions" if lang == "en" else "Ateliers privés")}">
  {surtitre("Private Atelier Sessions" if lang == "en" else "Ateliers privés", 1)}<h2 class="titre-section">{lettres("Focus on process and medium" if lang == "en" else "Le geste et le médium")}</h2>
  <ul class="ateliers__liste">{at}</ul>
</section>
<section class="equipes" data-strate="{e("Teams" if lang == "en" else "Équipes")}">
  <div class="equipes__images">{figure_photo(prof, "teambuilding/atelier-cires-jaunes", "A team workshop in yellow aprons, painting dots" if lang == "en" else "Un atelier d'équipe en tabliers jaunes", "", "fossile", "(max-width: 800px) 86vw, 34vw", ' data-parallaxe="-0.06"')}{figure_photo(prof, "conferences/salle-de-conference", "A conference room during a talk" if lang == "en" else "Une salle pendant une conférence", "", "fossile equipes__b", "(max-width: 800px) 60vw, 20vw", ' data-parallaxe="0.1"')}</div>
  <div class="equipes__texte">{surtitre("Institutional & Team Innovation" if lang == "en" else "Institutions et équipes", 2)}<h2 class="titre-section">{lettres("The garden of creative thinking" if lang == "en" else "Le jardin de la pensée créative")}</h2><p data-apparait>{e(C.COURS["equipes_intro"][lang])}</p><ul class="equipes__liste">{eq}</ul>
  <p data-apparait>{bouton(t["nav"]["evenements"], lien(lang, "evenements", prof))}</p></div>
</section>
<section class="en-ligne" data-strate="{e("Online and outdoors" if lang == "en" else "En ligne et en plein air")}">
  <div class="en-ligne__carte en-ligne__carte--feu" data-incline>
    {figure_photo(prof, "atelier/video-hot-surface", "Working with wax on a hot surface" if lang == "en" else "Travail de la cire sur surface chauffante", "", "fossile", "(max-width: 800px) 86vw, 30vw")}
    <div>{surtitre(("Online course · " if lang == "en" else "Cours en ligne · ") + C.COURS_EN_LIGNE["organisateur"], 3)}<h2 class="titre-section">{lettres(C.COURS_EN_LIGNE["titre"])}</h2>
    <p data-apparait>{e(C.COURS_EN_LIGNE["texte"][lang])}</p><p class="note">{e(C.COURS_EN_LIGNE["dates"][lang])}</p>
    <p><a class="bouton aimant" href="{C.COURS_EN_LIGNE["url"]}" target="_blank" rel="noopener"><span>{e("Register with Essence of Mulranny" if lang == "en" else "S'inscrire chez Essence of Mulranny")}</span></a></p></div>
  </div>
  <div class="en-ligne__carte en-ligne__carte--air" data-incline>
    {figure_photo(prof, "retraites/participante-peint-en-plein-air", "A participant painting outdoors in a mountain meadow" if lang == "en" else "Une participante peint en plein air, dans un pré de montagne", "", "fossile", "(max-width: 800px) 86vw, 30vw")}
    <div>{surtitre("Private, outdoors" if lang == "en" else "Privé, en plein air", 4)}<h3>{e(C.PLEIN_AIR_PRIVE["titre"][lang])}</h3><p class="note">{e(C.PLEIN_AIR_PRIVE["texte"][lang])}</p>
    <p>{bouton("Ask about dates" if lang == "en" else "Demander des dates", lien(lang, "contact", prof) + "?objet=cours_prives", "bouton bouton--ligne")}</p></div>
  </div>
  <p class="en-ligne__cloche" data-apparait><span aria-hidden="true">🔔</span> {e(C.M2616["cloche"][lang])}</p>
</section>
<section class="cocreation" data-strate="Co-Creating Sessions">
  {figure_photo(prof, "cours/table-aquarelle", "A workshop table covered in watercolour work" if lang == "en" else "Une table d'atelier couverte d'aquarelles", "", "fossile", "(max-width: 800px) 80vw, 30vw")}
  <div>{surtitre(L(lang, co["groupe"]), 5)}<h2 class="titre-section">{lettres(co["titre"])}</h2><p data-apparait>{e(L(lang, co["texte"]))}</p><p class="prix-grand" data-apparait>{co["prix"]}{"\u00a0" if lang == "fr" else " "}€</p>
  <p data-apparait>{bouton("Book in the shop" if lang == "en" else "Réserver en boutique", lien(lang, "boutique", prof, "#espace"))}{bouton("Ask a question" if lang == "en" else "Poser une question", lien(lang, "contact", prof) + "?objet=cours_prives", "bouton bouton--ligne")}</p></div>
</section>'''
    corps = avec_carnet(corps, lang, prof, "cours")
    ecrire(chemin, page(lang, "cours", chemin, t["nav"]["cours"], corps, href_autre(lang, "cours", prof), {}, "page-cours"))


# ================================================================ cours privés sur mesure (hôtels, conciergeries, organisateurs)
def page_cours_prives(lang):
    t = C.T[lang]
    fr = lang == "fr"
    chemin = fichier(lang, "cours_prives")
    prof = prof_de(chemin)
    K = C.COURS_PRIVES
    ex = f'<span class="exemple">{"example" if not fr else "exemple"}</span>'
    contact = lien(lang, "contact", prof)

    def experience(x, n):
        if "ref" in x:
            a, b, ph = C.COURS["ateliers"][x["ref"]]
            titre_x, texte_x = a, b
        elif "ref_equipe" in x:
            titre_x, texte_x = C.COURS["equipes"][x["ref_equipe"]]
            ph = x["photo"]
        else:
            titre_x, texte_x, ph = x["titre"], x["texte"], x["photo"]
        demande = f'{contact}?objet=cours_prives&amp;seance={quote(titre_x["en"])}'
        return (f'<li class="experience" style="--i:{n}">{figure_photo(prof, ph, "", "", "fossile experience__img", "(max-width: 800px) 86vw, 24vw")}'
                f'<p class="experience__n">{n + 1:02d}</p><h4 class="experience__titre">{e(titre_x[lang])}</h4><p>{e(texte_x[lang])}</p>'
                f'<dl class="experience__faits"><div><dt>{"Length" if not fr else "Durée"}</dt><dd>{e(x["duree"][lang])}</dd></div>'
                f'<div><dt>{"Group" if not fr else "Groupe"}</dt><dd>{e(x["groupe"][lang])}</dd></div>'
                f'<div><dt>{"Price" if not fr else "Tarif"}</dt><dd>{e(x["prix"][lang])}</dd></div></dl>{ex}'
                f'<a class="lien-fleche" href="{demande}">{"Request this session" if not fr else "Demander cette séance"} →</a></li>')

    n = 0
    cats = ""
    for i, cat in enumerate(C.OFFRE_COURS_PRIVES):
        items = ""
        for x in cat["experiences"]:
            items += experience(x, n)
            n += 1
        cats += (f'<section class="offre" id="{cat["cle"]}" data-strate="{e(cat["titre"][lang])}">'
                 f'<div class="offre__tete">{surtitre(cat["titre"][lang], i + 1)}<h2 class="titre-section">{lettres(cat["titre"][lang])}</h2><p data-apparait>{e(cat["intro"][lang])}</p></div>'
                 f'<ul class="offre__liste">{items}</ul></section>')
    etapes = "".join(f'<li><p class="etape-cp__n">{i + 1}</p><h3>{e(a[lang])}</h3><p>{e(b[lang])}</p></li>' for i, (a, b) in enumerate(C.ETAPES_COURS_PRIVES))
    sommaire = " · ".join(f'<a href="#{cat["cle"]}">{e(cat["titre"][lang])}</a>' for cat in C.OFFRE_COURS_PRIVES)
    corps = f'''
{bandeau(lang, prof, None, "Hotels · concierges · event planners" if not fr else "Hôtels · conciergeries · organisateurs d'événements", K["titre"][lang], [K["pour"][lang], C.COURS["citation"][lang]], figure_photo(prof, "cours/in-the-studio", "Guests painting in the studio" if not fr else "Des participants peignent à l'atelier", "", "fossile", "(max-width: 900px) 80vw, 36vw"), K["titre"][lang], "bandeau--cours-prives")}
<p class="offre__sommaire">{sommaire} · <a href="#comment">{"How it works" if not fr else "Comment ça marche"}</a></p>
<p class="offre__avertissement">{ex} {e("Lengths, group sizes and prices on this page are examples, until Lisa sends her summary of categories, experiences and rates." if not fr else "Durées, tailles de groupe et prix de cette page sont des exemples, en attendant la synthèse de Lisa (catégories, expériences, tarifs).")}</p>
{cats}
<section class="comment-cp" id="comment" data-strate="{e("How it works" if not fr else "Comment ça marche")}">
  <div class="comment-cp__tete">{surtitre("For hotels and concierges" if not fr else "Pour les hôtels et conciergeries", len(C.OFFRE_COURS_PRIVES) + 1)}<h2 class="titre-section">{lettres("How it works" if not fr else "Comment ça marche")}</h2></div>
  <ol class="comment-cp__etapes">{etapes}</ol>
  <p class="comment-cp__partenaires">{e(C.PARTENAIRES_COURS_PRIVES[lang])}</p>
  <p class="note">{ex} {e("Steps, response time and what is included: examples to confirm with Lisa." if not fr else "Étapes, délai de réponse et prestations comprises : exemples à confirmer avec Lisa.")}</p>
  <p>{bouton("Enquire for your guests" if not fr else "Demander pour vos clients", contact + "?objet=cours_prives")}<a class="bouton bouton--ligne aimant" href="https://wa.me/{C.COORD["tel_brut"].lstrip("+")}" target="_blank" rel="noopener"><span>WhatsApp</span></a><a class="bouton bouton--ligne aimant" href="mailto:{C.COORD["courriel_espace"]}"><span>{C.COORD["courriel_espace"]}</span></a></p>
</section>'''
    corps = avec_carnet(corps, lang, prof, "cours")
    ecrire(chemin, page(lang, "cours_prives", chemin, K["titre"][lang], corps, href_autre(lang, "cours_prives", prof), {}, "page-cours page-cours-prives"))


# ================================================================ Studio notes : publié, hors menu (brief)
def page_studio(lang):
    t = C.T[lang]
    fr = lang == "fr"
    chemin = fichier(lang, "studio")
    prof = prof_de(chemin)
    intro = C.INTRO_SERIE[lang]
    chevalet = "".join(figure_oeuvre(prof, oid, lang, LEAD, "(max-width: 700px) 70vw, 26vw") for oid in ["en-cours-3", "en-cours-1", "en-cours-4", "en-cours-5", "en-cours-6"])
    corps = f'''
<section class="bandeau bandeau--studio" data-strate="{e(t["nav"]["studio"])}">
  <div class="bandeau__texte">
    {surtitre(SERIES[LEAD]["titre"][lang] + " · " + ("works in progress and research" if not fr else "œuvres en cours et recherches"))}
    <h1 class="bandeau__titre">{lettres(t["nav"]["studio"])}</h1>
    <div class="bandeau__intro" data-apparait><p class="studio__ouverture">{e(intro[0])}</p></div>
  </div>
  <div class="bandeau__image">{figure_photo(prof, "artiste/lisa-a-17-ans-juneau-icefield", "Lisa at seventeen on the Juneau Icefield" if not fr else "Lisa à dix-sept ans sur le champ de glace de Juneau", "Juneau Icefield, expedition photograph" if not fr else "Champ de glace de Juneau, photo d'expédition", "fossile", "(max-width: 900px) 70vw, 30vw")}</div>
</section>
<section class="studio-texte" data-strate="{e("Reading the ice" if not fr else "Lire la glace")}">
  <div class="studio-texte__colonne">{"".join(f'<p data-apparait>{e(x)}</p>' for x in intro[1:3])}
    <blockquote class="declaration__citation"><p>{e(C.POSITION["citation"][lang])}</p></blockquote>
    {"".join(f'<p data-apparait>{e(x)}</p>' for x in intro[3:])}
  </div>
</section>
<section class="studio-chevalet" data-strate="{e("On my easel" if not fr else "Sur mon chevalet")}">
  <div class="studio-chevalet__tete">{surtitre("On my easel" if not fr else "Sur mon chevalet", 1)}<p data-apparait>{e(C.SERIE_ACTUELLE["chevalet"][lang])}</p></div>
  <div class="studio-chevalet__oeuvres">{chevalet}</div>
</section>
<section class="studio-recherche" data-strate="{e("Research and process" if not fr else "Recherches et procédé")}">
  {surtitre("Research and process" if not fr else "Recherches et procédé", 2)}
  <ul class="matieres__photos">
    <li>{figure_photo(prof, "atelier/glacier-sur-le-chevalet", "A glacier painting on the easel" if not fr else "Une peinture de glacier sur le chevalet", "", "fossile", "(max-width: 800px) 46vw, 22vw")}</li>
    <li>{figure_photo(prof, "atelier/seaside-village-detail", "Detail of Seaside Village and the Pink Flowers" if not fr else "Détail de Seaside Village and the Pink Flowers", "Seaside Village and the Pink Flowers, " + ("detail" if not fr else "détail"), "fossile", "(max-width: 800px) 46vw, 22vw")}</li>
    <li>{figure_photo(prof, "atelier/video-hot-surface", "Working wax on a hot surface" if not fr else "Travail de la cire sur surface chauffante", "", "fossile", "(max-width: 800px) 46vw, 22vw")}</li>
    <li>{figure_photo(prof, "atelier/oeuvre-en-cours-pastels-sur-cire", "Pastels worked into wax on a painting in progress" if not fr else "Des pastels travaillés dans la cire, sur une œuvre en cours", "", "fossile", "(max-width: 800px) 46vw, 22vw")}</li>
  </ul>
  {videos_procede(lang)}
  <p class="note">{e("More to come: Juneau Icefield expedition photographs, Cool Reflections in daylight, close-ups of wax surfaces, process shots and short videos in English with French captions." if not fr else "À venir : photos d'expédition du champ de glace de Juneau, Cool Reflections à la lumière du jour, gros plans de surfaces de cire, images du procédé et courtes vidéos en anglais sous-titrées en français.")}</p>
</section>'''
    ecrire(chemin, page(lang, "studio", chemin, t["nav"]["studio"], corps, href_autre(lang, "studio", prof), {}, "page-studio"))


# ================================================================ événements privés
def page_evenements(lang):
    t = C.T[lang]
    chemin = fichier(lang, "evenements")
    prof = prof_de(chemin)
    ev = C.EVENEMENTS
    themes = "".join(f'<li data-incline><h3>{e(a[lang])}</h3><p>{e(b[lang])}</p></li>' for a, b in ev["themes"])
    corps = f'''
{bandeau(lang, prof, None, "Private, institutional or corporate gatherings · venue hire" if lang == "en" else "Rencontres privées, institutionnelles ou d'entreprise · location du lieu", t["nav"]["evenements"], [ev["titre"][lang], ev["intro"][lang]], figure_photo(prof, "evenements/table-de-diner-dans-la-galerie", "A long dinner table set in the gallery" if lang == "en" else "Une longue table de dîner dressée dans la galerie", "", "fossile", "(max-width: 900px) 80vw, 36vw"), t["nav"]["evenements"])}
<section class="jauges" data-strate="{e("Capacity" if lang == "en" else "Capacité")}">
  {figure_photo(prof, "espace/salon-canape", "The lounge of the gallery, with sofa and paintings" if lang == "en" else "Le salon de la galerie, canapé et tableaux", "", "fossile jauges__img", "(max-width: 900px) 80vw, 34vw", ' data-parallaxe="-0.05"')}
  <div>{surtitre("The venue" if lang == "en" else "Le lieu", 1)}
  <div class="jauges__grille">
    <div class="jauge" data-jauge="18"><p class="jauge__n" data-compteur="18">18</p><p>{e("guests seated" if lang == "en" else "personnes assises")}</p><div class="jauge__points" aria-hidden="true"></div></div>
    <div class="jauge" data-jauge="40"><p class="jauge__n" data-compteur="40">40</p><p>{e("guests standing" if lang == "en" else "personnes debout")}</p><div class="jauge__points" aria-hidden="true"></div></div>
  </div>
  <ul class="liste-traits">{"".join(f'<li data-apparait>{e(x)}</li>' for x in ev["equipements"][lang])}</ul>
  <p data-apparait>{e(ev["ambiance"][lang])}</p></div>
</section>
<section class="experiences" data-strate="{e("Creative experiences" if lang == "en" else "Expériences créatives")}">
  <div class="experiences__images">{figure_photo(prof, "evenements/apero-prive", "A private apéro in the gallery" if lang == "en" else "Un apéritif privé dans la galerie", "", "fossile", "(max-width: 800px) 86vw, 34vw")}{figure_photo(prof, "evenements/verres-de-vin-galerie", "Wine glasses ready for a group" if lang == "en" else "Des verres prêts pour un groupe", "", "fossile experiences__b", "(max-width: 800px) 60vw, 20vw", ' data-parallaxe="0.1"')}</div>
  <div>{surtitre("Private creative experiences" if lang == "en" else "Expériences créatives privées", 2)}<p data-apparait>{e(ev["experiences_intro"][lang])}</p><ul class="liste-traits">{"".join(f'<li data-apparait>{e(x)}</li>' for x in ev["experiences"][lang])}</ul></div>
</section>
<section class="art-thinking" data-strate="Art Thinking">
  {surtitre("Art Thinking team-building events" if lang == "en" else "Cohésion d'équipe « Art Thinking »", 3)}<h2 class="titre-section">{lettres("Past themes" if lang == "en" else "Thèmes déjà proposés")}</h2>
  <p data-apparait>{e(ev["art_thinking"][lang])}</p>
  <ul class="themes">{themes}</ul>
  {figure_photo(prof, "cours/atelier-groupe-grande-table", "A group workshop around a long table" if lang == "en" else "Un atelier de groupe autour d'une grande table", "", "fossile art-thinking__img", "(max-width: 800px) 92vw, 60vw")}
  <div class="fin-page"><p data-apparait>{e(ev["fin"][lang])}</p><p>{bouton("Let's work together" if lang == "en" else "Travaillons ensemble", lien(lang, "contact", prof) + "?objet=evenement")}</p></div>
</section>'''
    corps = avec_carnet(corps, lang, prof, "evenements")
    ecrire(chemin, page(lang, "evenements", chemin, t["nav"]["evenements"], corps, href_autre(lang, "evenements", prof), {}, "page-evenements"))


# ================================================================ retraites
LON0, LON1, LAT0, LAT1 = 6.05, 6.56, 45.76, 46.27
KX = math.cos(math.radians(46))
CW = 1000
CK = CW / ((LON1 - LON0) * KX)
CH = round((LAT1 - LAT0) * CK)
LAC = [(6.137, 45.904), (6.152, 45.899), (6.168, 45.887), (6.182, 45.870), (6.197, 45.858), (6.214, 45.846), (6.226, 45.828), (6.236, 45.808), (6.232, 45.792),
       (6.222, 45.787), (6.214, 45.800), (6.205, 45.818), (6.190, 45.834), (6.176, 45.848), (6.160, 45.863), (6.146, 45.879), (6.131, 45.893)]
GENEVE = (6.109, 46.238)


def proj(lon, lat):
    return ((lon - LON0) * KX * CK, (LAT1 - lat) * CK)


def carte_topo(lang, r):
    import random
    rnd = random.Random(7)
    sommets = [(6.47, 45.87, 9), (6.40, 45.95, 7), (6.30, 45.80, 6), (6.52, 45.93, 8), (6.25, 46.05, 5), (6.43, 46.12, 6), (6.20, 45.75, 5)]
    lignes = []
    for lon, lat, n in sommets:
        cx, cy = proj(lon, lat)
        for k in range(1, n + 1):
            rr = k * 26
            pts = []
            ph = rnd.random() * 6
            for a in range(0, 360, 12):
                ang = math.radians(a)
                d = rr * (1 + 0.18 * math.sin(3 * ang + ph) + 0.08 * math.sin(5 * ang + k))
                pts.append((cx + d * math.cos(ang), cy + d * math.sin(ang) * 0.82))
            dd = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
            lignes.append(f'<path class="topo__ligne{" topo__ligne--maitresse" if k % 4 == 0 else ""}" d="{dd}"/>')
    lac = "M" + " L".join(f"{proj(lo, la)[0]:.1f} {proj(lo, la)[1]:.1f}" for lo, la in LAC) + " Z"
    pts = [proj(GENEVE[0], GENEVE[1])] + [proj(et["lon"], et["lat"]) for et in r["etapes"]]
    seg = []
    longueurs = [0]
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    total = 0
    for i in range(1, len(pts)):
        x0, y0 = pts[i - 1]
        x1, y1 = pts[i]
        mx, my = (x0 + x1) / 2 + (y1 - y0) * 0.22, (y0 + y1) / 2 - (x1 - x0) * 0.22
        d += f" Q{mx:.1f} {my:.1f} {x1:.1f} {y1:.1f}"
        n = 40
        l = 0
        px, py = x0, y0
        for s in range(1, n + 1):
            tt = s / n
            qx = (1 - tt) ** 2 * x0 + 2 * (1 - tt) * tt * mx + tt * tt * x1
            qy = (1 - tt) ** 2 * y0 + 2 * (1 - tt) * tt * my + tt * tt * y1
            l += math.hypot(qx - px, qy - py)
            px, py = qx, qy
        total += l
        longueurs.append(round(total, 1))
    marques = []
    gx, gy = pts[0]
    marques.append(f'<g class="topo__lieu topo__lieu--depart" data-etape="0"><circle cx="{gx:.1f}" cy="{gy:.1f}" r="7"/><text x="{gx + 14:.1f}" y="{gy + 5:.1f}">{e("Geneva airport" if lang == "en" else "Aéroport de Genève")}</text></g>')
    for i, et in enumerate(r["etapes"]):
        x, y = pts[i + 1]
        nom = L(lang, et["nom"])
        gauche = x > CW * 0.62
        marques.append(f'<g class="topo__lieu" data-etape="{i + 1}"><circle cx="{x:.1f}" cy="{y:.1f}" r="9"/><text x="{x + (-14 if gauche else 14):.1f}" y="{y - 12:.1f}" text-anchor="{"end" if gauche else "start"}">{e(nom)}</text><text class="topo__jour" x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle">{et["jour"]}</text></g>')
    clip = f'<clipPath id="topo-cadre"><rect x="0" y="0" width="{CW}" height="{CH}" rx="28"/></clipPath>'
    return (f'<svg class="topo" viewBox="0 0 {CW} {CH}" role="img" aria-label="{e("Schematic map: Geneva, La Clusaz, Col des Aravis, Lake Annecy" if lang == "en" else "Carte schématique : Genève, La Clusaz, Col des Aravis, lac d'Annecy")}">'
            f'<defs>{clip}</defs><g clip-path="url(#topo-cadre)"><rect class="topo__fond" width="{CW}" height="{CH}"/>{"".join(lignes)}'
            f'<path class="topo__lac" d="{lac}"/>'
            f'<path class="topo__route topo__route--fond" d="{d}"/><path class="topo__route" data-route data-longueurs="{",".join(str(x) for x in longueurs)}" d="{d}"/>'
            f'{"".join(marques)}</g></svg>')


IMAGES_RETRAITE = {
    "pip": {
        "intro": ("retraites/peinture-en-plein-air", "Painting outdoors on a bench in the alpine meadow", "Peindre en plein air sur un banc, dans l'alpage"),
        "pour_qui": ("retraites/croquis-col-des-aravis", "Sketching on a bench above the Col des Aravis", "Croquis sur un banc au-dessus du col des Aravis"),
        "temoignages": ("paysages/aravis-chapelle-au-couchant", "A chapel below the Aravis range at sunset", "Une chapelle au pied de la chaîne des Aravis au couchant"),
        "inclus": ("retraites/journee-talloires-dejeuner", "Lunch and sketchbooks on a terrace above Lake Annecy", "Déjeuner et carnets sur une terrasse au-dessus du lac d'Annecy"),
        "faq": ("retraites/roc-de-chere", "Sketching at the Roc de Chère above Lake Annecy", "Croquis au Roc de Chère, au-dessus du lac d'Annecy"),
        "reserver": ("paysages/fleurs-alpage-bandeau", "", ""),
    },
    "encaustics": {
        "intro": ("retraites/ouverture-des-boites-magiques", "Participants opening their boxes of materials around the studio table", "Les participants ouvrent leurs boîtes de matériel autour de la table de l'atelier"),
        "pourquoi": ("paysages/brume-sur-la-neige", "Mist over the snow above La Clusaz", "La brume sur la neige au-dessus de La Clusaz"),
        "ingredients": ("atelier/melange-resines-pigments-cire", "Lisa Cirenza mixing resin, pigments and wax in the studio", "Lisa Cirenza mélange résine, pigments et cire à l'atelier"),
        "comment": ("cours/cours-encaustique-sur-papier", "Lisa and a participant holding up black and white encaustic works on paper", "Lisa et un participant montrent des encaustiques en noir et blanc sur papier"),
        "pour_qui": ("retraites/plein-air-en-foret", "Watercolour sketchbooks on a picnic table in the forest", "Carnets d'aquarelle sur une table de pique-nique en forêt"),
        "temoignages": ("paysages/oiseau-et-montagnes", "A bird above the mountains", "Un oiseau au-dessus des montagnes"),
        "inclus": ("retraites/aquarelle-sur-souche", "A watercolour palette and a small study on a tree stump", "Une palette d'aquarelle et une petite étude sur une souche"),
        "reserver": ("cours/pinceaux-bandeau", "", ""),
    },
}
RETRAITES = {"pip": R.PIP, "encaustics": R.ENCAUSTICS}
for _k, _ph in (("pip", "retraites/diner-coucher-de-soleil-parapentes"), ("encaustics", "retraites/atelier-cire-en-groupe")):
    RETRAITES[_k]["photo_carte"] = _ph


def grille_prix(lang, cle=None, prof=0):
    """v6 · sur les pages, la fourchette seule (demande de Lisa) ; le détail des logements est dans les formulaires d'inscription."""
    fr = lang == "fr"
    cles = (cle,) if cle else RETRAITES_ORDRE
    inscr = "".join(bouton(("Register · " if not fr else "S'inscrire · ") + nom_retraite(RETRAITES[k], lang), lien(lang, INSCRIPTION[k], prof), "bouton" if i == 0 else "bouton bouton--ligne") for i, k in enumerate(cles))
    return (f'<div class="prix" id="prix" tabindex="-1"><p class="prix__fourchette">{e(R.LOGEMENT[lang])}</p>'
            f'<p class="prix__reduc">{e(R.REDUCTIONS[lang])}</p><p class="prix__actions">{inscr}</p>'
            f'<p class="note"><a href="{lien(lang, "conditions", prof)}">{e("Payment schedule and cancellation policy" if not fr else "Échéancier de paiement et conditions d'annulation")}</a></p></div>')


def fig_retraite(lang, prof, cle, quoi, classe, sizes, attrs=""):
    src, en, fr = IMAGES_RETRAITE[cle][quoi]
    return figure_photo(prof, src, en if lang == "en" else fr, "", "fossile " + classe, sizes, attrs)


def paras(x, lang, attrs=" data-apparait"):
    v = x[lang] if isinstance(x, dict) else x
    return "".join(f"<p{attrs}>{e(p)}</p>" for p in (v if isinstance(v, list) else [v]))


def sections_pause(lang, prof, r):
    """Pourquoi, quoi, comment : la recette de l'Autumn Alpine Pause."""
    ing = "".join(f'<li class="ingredient ingredient--{k}" data-incline data-revele style="--i:{i}"><span class="ingredient__n">{i + 1}</span><h3>{e(a[lang])}</h3><p>{e(b[lang])}</p></li>'
                  for i, ((a, b), k) in enumerate(zip(r["ingredients"], ("poulet", "sauce", "epices"))))
    rec = "".join(f'<li><strong>{e(a)}</strong> — {e(b)}</li>' for a, b in r["recettes"][lang])
    tp = L(lang, r.get("titre_pourquoi")) or ("Why a pause?" if lang == "en" else "Pourquoi une pause ?")
    return f'''<section class="pourquoi" data-strate="{e(tp)}">
  {fig_retraite(lang, prof, r["id"], "pourquoi", "pourquoi__img", "100vw")}
  <div class="pourquoi__texte">{surtitre("Why" if lang == "en" else "Pourquoi", 1)}<h2 class="titre-section">{lettres(tp)}</h2>
  <p class="pourquoi__grand" data-mots>{e(r["pourquoi"][lang])}</p></div>
</section>
<section class="ingredients ingredients--trois" data-strate="{e("The ingredients" if lang == "en" else "Les ingrédients")}">
  <div class="ingredients__tete">{surtitre("What" if lang == "en" else "Quoi", 2)}<h2 class="titre-section">{lettres("The chicken, the sauce and the spices" if lang == "en" else "Le poulet, la sauce et les épices")}</h2>{paras(r["chef"], lang)}</div>
  <ul class="ingredients__liste ingredients__liste--trois" data-effet="recette">{ing}</ul>
  <p class="ingredients__equilibre" data-apparait>{e(r["equilibre"][lang])}</p>
</section>
<section class="comment" data-strate="{e("Our Creative Recipe Book" if lang == "en" else "Notre carnet de recettes")}">
  <div class="comment__texte">{surtitre("How" if lang == "en" else "Comment", 3)}<h2 class="titre-section">{lettres("Our Creative Recipe Book" if lang == "en" else "Notre carnet de recettes créatif")}</h2>{paras(r["comment"], lang)}
  <div class="recettes"><h3>{e(r["recettes_intro"][lang])}</h3><ul class="liste-traits">{rec}</ul></div>
  <p class="note-base" data-apparait>{e(r["base"][lang])}</p></div>
  {fig_retraite(lang, prof, r["id"], "comment", "comment__img", "(max-width: 900px) 80vw, 36vw")}
</section>'''


def page_retraite(lang, cle):
    t = C.T[lang]
    fr = lang == "fr"
    r = RETRAITES[cle]
    chemin = fichier(lang, cle)
    prof = prof_de(chemin)
    jours = []
    for i, j in enumerate(r["jours"]):
        ph = r["photos_jours"][i]
        img = figure_photo(prof, ph, "", "", "fossile jour__img", "(max-width: 800px) 86vw, 34vw")
        items = "".join(f"<li>{e(x)}</li>" for x in j["items"][lang])
        jours.append(f'''<li class="jour" data-strate="{e(("Day " if not fr else "Jour ") + str(i + 1))}">
  <p class="jour__n">{"Day" if not fr else "Jour"} <span>{i + 1}</span></p>
  <div class="jour__texte"><h3>{e(j["titre"][lang])}</h3><ul class="liste-traits">{items}</ul><p class="jour__note" data-apparait>{e(j["note"][lang])}</p></div>
  <div class="jour__images">{img}</div>
</li>''')
    etapes = "".join(f'<li class="etape" data-etape="{i + 1}"><p class="etape__jour">{"Day" if not fr else "Jour"} {et["jour"]}</p><h3>{e(L(lang, et["nom"]))}</h3><p>{e(et["texte"][lang])}</p><span class="etape__img">{img_photo(prof, r["photos_jours"][et["jour"] - 1], "", "(max-width: 900px) 60vw, 22vw")}</span></li>' for i, et in enumerate(r["etapes"]))
    temoins = "".join(f'<li data-incline><blockquote><p>“{e(x["texte"])}”</p><footer>{e(L(lang, x["nom"]))}{(" · " + e(x["source"])) if x.get("source") else ""}</footer></blockquote></li>' for x in r["temoignages"])
    faq = "".join(f'<details class="faq__item"><summary>{e(q[lang])}</summary><p>{e(rep[lang])}</p></details>' for q, rep in r.get("faq", []))
    a_sections = cle == "encaustics"
    n = 1
    def num():
        nonlocal n
        n += 1
        return n - 1
    milieu = sections_pause(lang, prof, r) if a_sections else ""
    if a_sections:
        n = 4
    coachs_liste = r.get("coachs") or [R.COACH_LISA]
    titre_coach = "Your creative coach" if not fr else "Votre coach créative"
    coachs = (f'<section class="coachs coachs--seule" data-strate="{e(titre_coach)}">' + surtitre(titre_coach, num()) + '<div class="coachs__grille">' + "".join(
        f'<article class="coach">{figure_photo(prof, c["photo"], c["nom"], "", "fossile coach__img", "(max-width: 800px) 70vw, 24vw")}<div><h3>{e(c["nom"])}</h3><p class="coach__role">{e(c["role"][lang])}</p>{paras(c["texte"], lang)}</div></article>' for c in coachs_liste) + "</div></section>")
    if cle == "pip":
        image_bandeau = f'<div class="bandeau__image bandeau__image--plein">{img_photo(prof, r["photo"], "Lake Annecy, the day excursion" if not fr else "Le lac d'Annecy, l'excursion de la journée", "(max-width: 900px) 100vw, 60vw", "", "eager")}</div>'
    else:
        image_bandeau = f'<div class="bandeau__image bandeau__image--plein">{img_photo(prof, r["photo"], ("Participants working with hot wax in the studio" if not fr else "Des participants travaillent la cire chaude à l'atelier"), "(max-width: 900px) 100vw, 50vw", "", "eager")}</div>'
    sections_programme = ""
    if r["etapes"]:
        sections_programme += f'''<section class="carte-retraite-topo" data-carte data-strate="{e("The route" if not fr else "Le parcours")}">
  <div class="carte__collant">
    <div class="carte__svg">{carte_topo(lang, r)}</div>
    <div class="carte__panneau">{surtitre("The route" if not fr else "Le parcours")}<ol class="etapes">{etapes}</ol><p class="note">{e("Schematic map, not to scale. Retreats are based in La Clusaz; lake days are excursions." if not fr else "Carte schématique, sans échelle. Les retraites sont basées à La Clusaz ; les journées au lac sont des excursions.")}</p></div>
    <div class="carte__progres" aria-hidden="true"><i></i></div>
  </div>
</section>'''
    if jours:
        sections_programme += f'''<section class="programme" data-strate="{e("Agenda" if not fr else "Programme")}">
  <div class="programme__tete">{surtitre("Agenda" if not fr else "Programme", num())}<h2 class="titre-section">{lettres("Day by day" if not fr else "Jour après jour")}</h2></div>
  <ol class="jours">{"".join(jours)}</ol>
</section>'''
    else:
        sections_programme += f'''<section class="programme programme--a-venir" data-strate="{e("Agenda" if not fr else "Programme")}">
  {surtitre("Agenda" if not fr else "Programme", num())}<h2 class="titre-section">{lettres("Day by day" if not fr else "Jour après jour")}</h2>
  <p class="note">{e(L(lang, r.get("programme_a_completer")) or "")}</p>
</section>'''
    if r.get("pour_qui"):
        sections_programme += f'''<section class="pour-qui" data-strate="{e("Is this retreat right for me?" if not fr else "Est-ce pour moi ?")}">
  {fig_retraite(lang, prof, cle, "pour_qui", "pour-qui__img", "(max-width: 900px) 80vw, 34vw")}
  <div>{surtitre("Anytime, anywhere" if not fr else "N'importe quand, n'importe où")}<h2 class="titre-section">{lettres("Is this retreat right for me?" if not fr else "Cette retraite est-elle pour moi ?")}</h2>
  <div class="pour-qui__texte">{"".join(f'<p data-apparait>{e(x)}</p>' for x in r["pour_qui"][lang])}</div></div>
</section>'''
    if temoins:
        sections_programme += f'''<section class="temoignages" data-strate="{e("What people say" if not fr else "Ils en parlent")}">
  {fig_retraite(lang, prof, cle, "temoignages", "temoignages__img", "100vw")}
  {surtitre("What people say" if not fr else "Ce qu'ils en disent")}<ul class="temoignages__liste">{temoins}</ul>
  <p class="note">{e("Testimonials as published on the current site, in their original language." if not fr else "Témoignages tels que publiés sur le site actuel, dans leur langue d'origine.")}</p>
</section>'''
    inclus = (f'<div><h2 class="titre-section">{lettres("What is included" if not fr else "Ce qui est inclus")}</h2><ul class="liste-traits liste-traits--oui">{"".join(f"<li>{e(x)}</li>" for x in R.INCLUS[lang])}</ul></div>'
              f'<div><h2 class="titre-section">{lettres("Not included" if not fr else "Non inclus")}</h2><ul class="liste-traits liste-traits--non">{"".join(f"<li>{e(x)}</li>" for x in R.NON_INCLUS[lang])}</ul></div>')
    corps = f'''
<section class="bandeau bandeau--retraite bandeau--{cle}" data-strate="{e(nom_retraite(r, lang))}">
  <div class="bandeau__texte">
    {surtitre(L(lang, r["dates"]) + " · " + L(lang, r["lieu"]))}
    <h1 class="bandeau__titre">{lettres(nom_retraite(r, lang))}</h1>
    <p class="bandeau__accroche" data-apparait>{e(L(lang, r["accroche"]))}</p>
    <p class="bandeau__cycle" data-apparait>{e(L(lang, r["cycle"]))}</p>
    <div class="bandeau__compte" data-apparait>{compte(lang, r["debut"])}<a class="bouton aimant bouton--petit" href="{lien(lang, "contact", prof) + "?objet=retraite&amp;retraite=" + cle}"><span>{e("Schedule a discovery call" if not fr else "Réserver un échange découverte")}</span></a></div>
  </div>
  {image_bandeau}
</section>
<section class="retraite-intro" data-strate="{e("Welcome" if not fr else "Bienvenue")}">
  <div class="retraite-intro__texte">{"".join(f'<p data-apparait>{e(x)}</p>' for x in r["intro"][lang])}{fig_retraite(lang, prof, cle, "intro", "retraite-intro__img", "(max-width: 900px) 92vw, 52vw")}</div>
  <dl class="fiche-pratique">
    <div><dt>{"Dates" if not fr else "Dates"}</dt><dd>{e(L(lang, r["dates"]))}</dd></div>
    <div><dt>{"Place" if not fr else "Lieu"}</dt><dd>{e(L(lang, r["lieu"]))}</dd></div>
    <div><dt>{"Group" if not fr else "Groupe"}</dt><dd>{e(L(lang, r["groupe"]))}</dd></div>
    <div><dt>{"Price" if not fr else "Tarif"}</dt><dd><strong>{e(L(lang, r["prix"]))}</strong> {e("depending on options indicated on the booking form" if not fr else "selon les options choisies sur le formulaire d'inscription")} · <a href="{lien(lang, INSCRIPTION[cle], prof)}">{e("registration form" if not fr else "formulaire d'inscription")}</a></dd></div>
  </dl>
</section>
{milieu}
{coachs}
{sections_programme}
<section class="inclus inclus--prix" data-strate="{e("Prices and rooms" if not fr else "Prix et chambres")}">
  {inclus}
  <div class="inclus__prix">{surtitre("Price" if not fr else "Prix")}{grille_prix(lang, cle, prof)}</div>
</section>
<section class="reserver reserver--image" data-strate="{e("Book" if not fr else "Réserver")}">
  <div class="reserver__fond" aria-hidden="true">{img_photo(prof, IMAGES_RETRAITE[cle]["reserver"][0], "", "100vw")}</div>
  <h2 class="titre-section">{lettres("Let’s see if we’re a good match" if not fr else "Voyons si nos élans créatifs s'accordent")}</h2>
  <p data-apparait>{e("Book a short, relaxed chat to talk about your needs, your room and whether this retreat is your next creative leap." if not fr else "Réservez un court échange, sans engagement, pour parler de vos envies, de votre chambre et voir si cette retraite est votre prochain élan créatif.")}</p>
  <p>{bouton("Schedule a discovery call" if not fr else "Réserver un échange découverte", lien(lang, "contact", prof) + "?objet=retraite&amp;retraite=" + cle)}{bouton("Register" if not fr else "S'inscrire", lien(lang, INSCRIPTION[cle], prof), "bouton bouton--ligne")}<a class="bouton bouton--ligne aimant" href="https://wa.me/{C.COORD["tel_brut"].lstrip("+")}" target="_blank" rel="noopener"><span>WhatsApp</span></a><a class="bouton bouton--ligne aimant" href="mailto:{C.COORD["courriel_espace"]}"><span>{C.COORD["courriel_espace"]}</span></a></p>
</section>'''
    ecrire(chemin, page(lang, cle, chemin, nom_retraite(r, lang), corps, href_autre(lang, cle, prof), {"retraite": cle}, "page-retraite page-retraite--" + cle))


def page_retraites(lang):
    t = C.T[lang]
    fr = lang == "fr"
    chemin = fichier(lang, "retraites")
    prof = prof_de(chemin)
    corps = f'''
{bandeau(lang, prof, None, "Espace Créa-Tea-Vité · La Clusaz · 2027", t["nav"]["retraites"], [R.LOGEMENT[lang]], figure_photo(prof, "retraites/groupe-painters-in-paradise", "Painting in Paradise participants in front of the mountains" if not fr else "Les participants de Painting in Paradise devant les montagnes", "Painters in Paradise, 2026", "fossile", "(max-width: 900px) 80vw, 36vw"), t["nav"]["retraites"])}
<section class="retraites-accueil retraites-accueil--page" data-strate="2027">
  <div class="retraites-cartes retraites-cartes--deux">
    {"".join(carte_retraite(lang, prof, RETRAITES[k], k, RETRAITES[k]["photo_carte"]) for k in RETRAITES_ORDRE)}
  </div>
</section>
<section class="inclus inclus--prix" data-strate="{e("Price" if not fr else "Prix")}">
  <div class="inclus__prix">{surtitre("Price" if not fr else "Prix", 1)}<h2 class="titre-section">{lettres("Registration" if not fr else "Inscription")}</h2>{grille_prix(lang, None, prof)}</div>
</section>'''
    corps = avec_carnet(corps, lang, prof, "retraites")
    ecrire(chemin, page(lang, "retraites", chemin, t["nav"]["retraites"], corps, href_autre(lang, "retraites", prof), {}, "page-retraites"))


# ================================================================ boutique (deux comptoirs, deux comptes de paiement)
# Petites encaustiques récentes relevées dans l'index public d'Artwork Archive (prix publics) ; photos à venir.
AA_RECENTES = [
    {"id": "aa-where-the-mountains-breathe", "titre": "Where the Mountains Breathe", "annee": "2025", "technique": {"en": "Encaustic on paper, black archival mat and frame", "fr": "Encaustique sur papier, passe-partout et cadre noirs d'archive"}, "dims": "34 × 25.5 cm", "prix": 145},
    {"id": "aa-light-across-the-thaw", "titre": "Light Across the Thaw", "annee": None, "technique": {"en": "Encaustics on board", "fr": "Encaustique sur panneau"}, "dims": "30 × 30 × 3.5 cm", "prix": 240},
    {"id": "aa-blissful-light", "titre": "Blissful Light", "annee": "2024", "technique": {"en": "Encaustics on board", "fr": "Encaustique sur panneau"}, "dims": "20 × 19.5 cm", "prix": 200},
    {"id": "aa-doucement-entrelaces", "titre": "Doucement Entrelacés", "annee": "2024", "technique": {"en": "Encaustic on paper, white archival mat and frame", "fr": "Encaustique sur papier, passe-partout et cadre blancs d'archive"}, "dims": "30 × 25.5 cm", "prix": 80},
    {"id": "aa-the-silence-of-thawing-waters", "titre": "The Silence of Thawing Waters", "annee": None, "technique": {"en": "Encaustic and inks on paper, black archival mat and frame", "fr": "Encaustique et encres sur papier, passe-partout et cadre noirs d'archive"}, "dims": "25.5 × 34 cm", "prix": None},
]


# v5 · tirages imprimés et expédiés par creativehub (theprintspace) : formats, papiers et prix d'EXEMPLE.
# La référence (SKU) est la clé de la connexion : la même dans Wix et dans creativehub (voir connecteurs/).
CH_FORMATS = [("A4", {"en": "A4 · 21 × 29.7 cm", "fr": "A4 · 21 × 29,7 cm"}, 95),
              ("A3", {"en": "A3 · 29.7 × 42 cm", "fr": "A3 · 29,7 × 42 cm"}, 145),
              ("A2", {"en": "A2 · 42 × 59.4 cm", "fr": "A2 · 42 × 59,4 cm"}, 245)]
CH_PAPIERS = [("HPR", "Hahnemühle Photo Rag 308 gsm", 0, "Photo Rag"), ("GE", "Hahnemühle German Etching 310 gsm", 10, "German Etching")]


def sku_tirage(oid, fmt, pap):
    return f"LC-{oid}-{fmt}-{pap}".upper()


def variantes_tirage(lang, oid, tt):
    opts = []
    for f_code, f_lib, f_prix in CH_FORMATS:
        for p_code, p_lib, p_sup, p_court in CH_PAPIERS:
            px = f_prix + p_sup
            opts.append({"sku": sku_tirage(oid, f_code, p_code), "lib": f"{f_lib[lang]} · {p_lib}", "court": f"{f_code} · {p_court}", "prix": px})
    return opts


def produit_oeuvre(lang, prof, oid, genre):
    t = C.T[lang]
    fr = lang == "fr"
    o = OEUVRES[oid]
    tt = titre(o, lang)
    prix = o["prix"][0] if o.get("prix") else None
    variantes = ""
    if genre == "tirage":
        detail = (o["edition"] or {}).get(lang) or ""
        opts = variantes_tirage(lang, oid, tt)
        prix = prix or opts[0]["prix"]
        prix_aff = ("from " if not fr else "à partir de ") + prix_txt(min(x["prix"] for x in opts), lang)
        bouton_txt = "Add to basket" if not fr else "Ajouter au panier"
        options = "".join(f'<option value="{x["sku"]}" data-prix="{x["prix"]}" data-lib="{e(x["lib"])}">{e(x["court"])} · {e(prix_txt(x["prix"], lang))}</option>' for x in opts)
        variantes = (f'<label class="produit__variante"><span class="vh">{"Size and paper" if not fr else "Format et papier"}</span>'
                     f'<select data-variante data-titre="{e(tt)}" data-oid="{oid}">{options}</select></label>'
                     f'<p class="produit__ch">{"Printed and shipped by creativehub" if not fr else "Imprimé et expédié par creativehub"} <span class="exemple">{"example prices" if not fr else "prix d'exemple"}</span></p>')
    else:
        detail = technique_txt(o, lang) or ""
        prix_aff = prix_txt(prix, lang) if prix else t["prix_demande"]
        bouton_txt = ("Add to basket" if not fr else "Ajouter au panier") if prix else ("Reserve" if not fr else "Réserver")
    dims = dims_txt(o, lang)
    donnees = {"id": oid, "comptoir": "atelier", "genre": genre, "titre": tt, "prix": prix, "image": f"img/oeuvres/{oid}-640.webp"}
    if genre == "tirage":
        v0 = variantes_tirage(lang, oid, tt)[0]
        donnees.update({"id": v0["sku"], "sku": v0["sku"], "titre": f'{tt} · {v0["lib"]}', "prix": v0["prix"], "fournisseur": "creativehub"})
    donnees = json.dumps(donnees, ensure_ascii=False)
    serie = SERIES[o["series"][0]]["titre"][lang] if o["series"][0] in SERIES else ""
    return f'''<li class="produit produit--{genre}" data-genre="{genre}">
  <div class="produit__visuel">{bouton_oeuvre(prof, oid, lang, o["series"][0], "(max-width: 700px) 44vw, 18vw", "produit__toile")}</div>
  <div class="produit__texte">
    <p class="produit__serie">{e(serie)}</p>
    <h3 class="produit__titre{" cartel__titre--vide" if not o["titre"] else ""}">{e(tt)}</h3>
    <p class="produit__detail">{e(detail)}{(" · " + e(dims)) if dims else ""}</p>
    <p class="produit__prix">{e(prix_aff)}</p>
    {variantes}
    <button class="produit__ajouter" type="button" data-ajouter='{e(donnees)}'><span>{e(bouton_txt)}</span></button>
  </div>
</li>'''


def produit_aa(lang, x):
    fr = lang == "fr"
    detail = x["technique"][lang] + " · " + (x["dims"].replace(".", ",") if fr else x["dims"]) + (" · " + x["annee"] if x["annee"] else "")
    prix_aff = prix_txt(x["prix"], lang) if x["prix"] else C.T[lang]["prix_demande"]
    donnees = json.dumps({"id": x["id"], "comptoir": "atelier", "genre": "recent", "titre": x["titre"], "prix": x["prix"], "image": "img/textures/cire-relief.webp"}, ensure_ascii=False)
    return f'''<li class="produit produit--recent produit--aa" data-genre="recent">
  <div class="produit__visuel produit__visuel--attente"><span>{e("Photo to come from Artwork Archive" if not fr else "Photo à venir d'Artwork Archive")}</span></div>
  <div class="produit__texte">
    <p class="produit__serie">{e("Encaustic · Artwork Archive" if not fr else "Encaustique · Artwork Archive")}</p>
    <h3 class="produit__titre">{e(x["titre"])}</h3>
    <p class="produit__detail">{e(detail)}</p>
    <p class="produit__prix">{e(prix_aff)}</p>
    <button class="produit__ajouter" type="button" data-ajouter='{e(donnees)}'><span>{e(("Add to basket" if not fr else "Ajouter au panier") if x["prix"] else ("Reserve" if not fr else "Réserver"))}</span></button>
  </div>
</li>'''


def produit_espace(lang, prof, cle, titre_p, texte, photo, prix, prix_aff, bouton_txt, lien_detail=None, genre="service"):
    donnees = json.dumps({"id": cle, "comptoir": "espace", "genre": genre, "titre": titre_p, "prix": prix, "image": "img/photos/" + photo.replace("/", "-") + "-800.webp"}, ensure_ascii=False)
    plus = f'<a class="lien-simple" href="{lien_detail}">{e("Details" if lang == "en" else "Détails")} →</a>' if lien_detail else ""
    return f'''<li class="produit produit--espace" data-genre="{genre}">
  <div class="produit__visuel produit__visuel--photo">{img_photo(prof, photo, "", "(max-width: 700px) 86vw, 26vw")}</div>
  <div class="produit__texte">
    <h3 class="produit__titre">{e(titre_p)}</h3>
    <p class="produit__detail">{e(texte)}</p>
    <p class="produit__prix">{e(prix_aff)}</p>
    <p class="produit__actions"><button class="produit__ajouter" type="button" data-ajouter='{e(donnees)}'><span>{e(bouton_txt)}</span></button>{plus}</p>
  </div>
</li>'''


def page_boutique(lang):
    t = C.T[lang]
    B = C.BOUTIQUE
    E = C.EDITIONS_COLLECTION
    c = C.COORD
    fr = lang == "fr"
    chemin = fichier(lang, "boutique")
    prof = prof_de(chemin)
    dispo = lambda oid: OEUVRES[oid]["statut"] not in ("vendu", "en-cours", "non-disponible", "en-pret")
    recentes = [oid for oid in LISTES[LEAD] if dispo(oid) and not OEUVRES[oid]["edition"]]
    tirages = list(dict.fromkeys(oid for sid in ORDRE + ["hors-serie"] for oid in LISTES.get(sid, []) if OEUVRES[oid]["edition"] and dispo(oid)))
    archive = [oid for sid in ARCHIVE if sid != "commissions" for oid in LISTES[sid] if not OEUVRES[oid]["edition"] and dispo(oid) and OEUVRES[oid]["series"][0] == sid]
    n_tout = len(AA_RECENTES) + len(recentes) + len(tirages) + len(archive)
    series_ed = "".join(f'''<li class="edition-serie edition-serie--boutique"><span class="edition-serie__bloc{" edition-serie__bloc--vide" if not x["image"] else ""}">{img_oeuvre(prof, x["image"], lang, "(max-width: 700px) 40vw, 14vw") if x["image"] else ""}</span>
  <span class="edition-serie__titre">{e(x["titre"][lang])}</span><span class="note">{e("Blocks, years and prices to come" if not fr else "Blocs, années et prix à venir")}</span></li>''' for x in E["series"])
    co = C.AGENDA[0]
    prix_co = int(co["prix"])
    espace_items = [produit_espace(lang, prof, "co-creating", co["titre"], L(lang, co["texte"]), "cours/atelier-libre-pastel", prix_co, prix_txt(prix_co, lang), "Add to basket" if not fr else "Ajouter au panier", lien(lang, "espace", prof))]
    espace_items += [produit_espace(lang, prof, k, RETRAITES[k]["titre"] + " · " + L(lang, RETRAITES[k]["dates"]), L(lang, RETRAITES[k]["accroche"]), RETRAITES[k]["photo_carte"], None,
                                    L(lang, RETRAITES[k]["prix"]) + (" per person" if not fr else " par personne"), "Request a place" if not fr else "Demander une place", lien(lang, k, prof), "retraite") for k in RETRAITES_ORDRE]

    def bouton_filtre(cle, libelle, n, actif=False):
        return f'<button type="button" class="filtre" aria-pressed="{"true" if actif else "false"}" data-filtre="{cle}">{e(libelle)} <small>{n}</small></button>'
    corps = f'''
<section class="bandeau bandeau--boutique" data-strate="{e(t["nav"]["boutique"])}">
  <div class="bandeau__texte">
    {surtitre("Lisa Cirenza Fine Art · artist-author" if not fr else "Lisa Cirenza Fine Art · artiste-auteur")}
    <h1 class="bandeau__titre">{lettres(t["nav"]["boutique"])}</h1>
    <div class="bandeau__intro" data-apparait><p>{e("Original works, collectors' editions and prints, sold by Lisa Cirenza Fine Art (artist-author, not VAT-registered). The checkout opens once the artist's payment account is ready; until then, your basket becomes a request." if not fr else "Œuvres originales, éditions de collection et tirages, vendus par Lisa Cirenza Fine Art (artiste-auteur, non assujettie à la TVA). Le paiement ouvrira quand le compte de paiement de l'artiste sera prêt ; d'ici là, votre panier devient une demande.")}</p></div>
    <p class="comptoirs__onglets" data-apparait><a class="bouton aimant bouton--atelier" href="#atelier"><span>{e(B["atelier_titre"][lang])}</span></a><a class="bouton bouton--ligne aimant" href="#editions"><span>{e(t["nav"]["editions"])}</span></a></p>
  </div>
  <div class="bandeau__image bandeau__image--duo">
    <span class="duo duo--atelier">{bouton_oeuvre(prof, "recente-09", lang, LEAD, "(max-width: 900px) 44vw, 20vw")}</span>
    <span class="duo duo--espace">{bouton_oeuvre(prof, "recente-01", lang, LEAD, "(max-width: 900px) 44vw, 20vw")}</span>
  </div>
</section>

<section class="comptoir comptoir--atelier" id="atelier" tabindex="-1" data-strate="{e(B["atelier_titre"][lang])}">
  <div class="comptoir__tete">
    {surtitre(t["univers"]["atelier_long"] + " · " + c["forme_atelier"][lang], 1)}
    <h2 class="titre-section">{lettres(B["atelier_titre"][lang])}</h2>
    <p data-apparait>{e("Recent work and small encaustics with their prices from Artwork Archive; prints printed on demand by creativehub; earlier originals from the Archive." if not fr else "Œuvres récentes et petites encaustiques avec leurs prix d'Artwork Archive ; tirages imprimés à la demande par creativehub ; originaux plus anciens de l'Archive.")}</p>
    <div class="filtres" role="group" aria-label="{e("Filter the atelier counter" if not fr else "Filtrer le comptoir de l'atelier")}" data-filtres>
      {bouton_filtre("tout", "Everything" if not fr else "Tout", n_tout, True)}{bouton_filtre("recent", SERIES[LEAD]["titre"][lang], len(AA_RECENTES) + len(recentes))}{bouton_filtre("tirage", "Prints · creativehub" if not fr else "Tirages · creativehub", len(tirages))}{bouton_filtre("archive", t["nav"]["archive"], len(archive))}
    </div>
  </div>
  <ul class="produits" data-produits>{"".join(produit_aa(lang, x) for x in AA_RECENTES)}{"".join(produit_oeuvre(lang, prof, oid, "recent") for oid in recentes)}{"".join(produit_oeuvre(lang, prof, oid, "tirage") for oid in tirages)}{"".join(produit_oeuvre(lang, prof, oid, "archive") for oid in archive)}</ul>
  <p class="note comptoir__note">{e("Prices shown come from Artwork Archive (public profile, 11 November 2026); the other works are price on request, and your basket becomes a reservation request. Prints: choose the size and paper; each choice has its own reference, printed and shipped by creativehub (example prices until creativehub access is set up)." if not fr else "Les prix affichés viennent d'Artwork Archive (profil public, 11 novembre 2026) ; les autres œuvres sont sur demande, et votre panier devient alors une demande de réservation. Tirages : choisissez le format et le papier ; chaque choix a sa référence, imprimée et expédiée par creativehub (prix d'exemple en attendant l'accès à creativehub).")}</p>
</section>

<section class="comptoir comptoir--editions" id="editions" tabindex="-1" data-strate="{e(E["titre"][lang])}">
  <div class="comptoir__tete">
    {surtitre(t["univers"]["atelier_long"] + " · " + ("archive line" if not fr else "ligne d'archive"), 2)}
    <h2 class="titre-section">{lettres(E["titre"][lang])}</h2>
    <div><p data-apparait>{e(E["texte"][lang])}</p><p class="note" data-apparait>{e(E["datation"][lang])} {e(E["note"][lang])}</p></div>
  </div>
  <ul class="editions-accueil__series editions-boutique">{series_ed}</ul>
  <p class="note comptoir__note">{e(E["a_venir"][lang])}</p>
</section>

<section class="livraison" data-strate="{e("Delivery" if not fr else "Livraison")}">
  {figure_photo(prof, "espace/facade-de-nuit", "The Espace Créa-Tea-Vité at night" if not fr else "L'Espace Créa-Tea-Vité de nuit", "", "fossile livraison__img", "(max-width: 800px) 80vw, 30vw")}
  <div class="livraison__texte">
    {surtitre("Delivery and pick-up" if not fr else "Livraison et retrait", 4)}
    <h2 class="titre-section">{lettres("From La Clusaz to the world" if not fr else "De La Clusaz au monde entier")}</h2>
    <p data-apparait>{e(E["tirages"][lang])}</p>
    <p data-apparait>{e(B["livraison"][lang])}</p>
    <p data-apparait>{e(B["retrait"][lang])}</p>
    <dl class="livraison__comptes">
      <div class="livraison__compte livraison__compte--atelier"><dt>{e(t["univers"]["atelier_long"])}</dt><dd>{e("Stripe account no. 1 · SIRET " if not fr else "Compte Stripe n° 1 · SIRET ")}{e(c["siret_atelier"])}</dd></div>
      <div class="livraison__compte livraison__compte--espace"><dt>{e(c["espace"])}</dt><dd>{e("Stripe account no. 2 · SIRET " if not fr else "Compte Stripe n° 2 · SIRET ")}{e(c["siret_espace"])}</dd></div>
    </dl>
    <p class="note">{e(B["simulation"][lang])} {e("On the live site, works, prices and sales are entered once in Artwork Archive." if not fr else "Sur le site en ligne, œuvres, prix et ventes se saisissent une seule fois dans Artwork Archive.")}</p>
  </div>
</section>'''
    ecrire(chemin, page(lang, "boutique", chemin, t["nav"]["boutique"], corps, href_autre(lang, "boutique", prof), {"boutique": True}, "page-boutique"))


def panier_html(lang, prof):
    t = C.T[lang]
    fr = lang == "fr"
    def compartiment(cle, nom, forme, compte):
        return f'''<section class="panier__comptoir panier__comptoir--{cle}" data-comptoir="{cle}">
      <h3><span>{e(nom)}</span><small>{e(forme)} · {e(compte)}</small></h3>
      <ul class="panier__liste" data-liste="{cle}"></ul>
      <p class="panier__vide">{e("Nothing here yet." if not fr else "Rien pour l'instant.")}</p>
      <p class="panier__total"><span>{e("Total")}</span><strong data-total="{cle}">—</strong></p>
      <button class="bouton panier__payer" type="button" data-payer="{cle}"><span>{e("Pay with Stripe" if not fr else "Payer avec Stripe")}</span></button>
      <p class="panier__recu" data-recu="{cle}" hidden tabindex="-1"></p>
    </section>'''
    return f'''<div class="panier" id="panier" hidden role="dialog" aria-modal="true" aria-labelledby="panier-titre">
  <div class="panier__voile" data-panier-fermer></div>
  <div class="panier__tiroir">
    <div class="panier__tete"><h2 id="panier-titre">{e("Your baskets" if not fr else "Vos paniers")}</h2><button class="panier__fermer" type="button" data-panier-fermer aria-label="{e(t["fermer"])}">×</button></div>
    <p class="panier__explication">{e("Two counters, two separate payments: nothing is ever mixed." if not fr else "Deux comptoirs, deux paiements séparés : rien n'est jamais mélangé.")}</p>
    {compartiment("atelier", t["univers"]["atelier_long"], C.COORD["forme_atelier"][lang], "Stripe 1")}
    {compartiment("espace", C.COORD["espace"], C.COORD["forme_espace"][lang], "Stripe 2")}
    <p class="note panier__note">{e(C.BOUTIQUE["simulation"][lang])}</p>
  </div>
</div>
<div class="panier-texte" hidden data-textes-panier='{e(json.dumps({"retirer": "Remove" if not fr else "Retirer", "sur_demande": t["prix_demande"], "a_completer": "Price to be completed" if not fr else "Prix à compléter", "demande": "Send the request" if not fr else "Envoyer la demande", "payer": "Pay with Stripe" if not fr else "Payer avec Stripe", "recu_paye": "Payment simulated for {n}. On the live site, Stripe would charge this account.", "recu_demande": "Request ready for {n}: Lisa will reply with price and availability.", "plus_a_completer": " + items at a price to be completed", "ajoute": "Added to the {n} basket", "fr": fr} if not fr else {"retirer": "Retirer", "sur_demande": t["prix_demande"], "a_completer": "Prix à compléter", "demande": "Envoyer la demande", "payer": "Payer avec Stripe", "recu_paye": "Paiement simulé pour {n}. Sur le site en ligne, Stripe encaisserait sur ce compte.", "recu_demande": "Demande prête pour {n} : Lisa répondra avec le prix et la disponibilité.", "plus_a_completer": " + articles au prix à compléter", "ajoute": "Ajouté au panier {n}", "fr": fr}, ensure_ascii=False))}'></div>'''


# ================================================================ contact
def page_contact(lang):
    t = C.T[lang]
    chemin = fichier(lang, "contact")
    prof = prof_de(chemin)
    c = C.COORD
    objets = [("oeuvre", "A work" if lang == "en" else "Une œuvre"), ("commande", "A commission" if lang == "en" else "Une commande"), ("cours_prives", "A bespoke course or workshop" if lang == "en" else "Un cours ou un atelier sur mesure"),
              ("evenement", "A private event" if lang == "en" else "Un événement privé"), ("retraite", "A retreat" if lang == "en" else "Une retraite"), ("autre", "Something else" if lang == "en" else "Autre chose")]
    maison = {"oeuvre": c["courriel"], "commande": c["courriel"], "autre": c["courriel"]}
    radios = "".join(f'<label class="choix"><input type="radio" name="objet" value="{v}" data-courriel="{maison.get(v, c["courriel_espace"])}"{" checked" if i == 0 else ""}><span>{e(l)}</span></label>' for i, (v, l) in enumerate(objets))
    fr = lang == "fr"

    def sel(nom, label, options, requis=False):
        o = "".join(f'<option value="{e(v)}">{e(x)}</option>' for v, x in options)
        return f'<div class="champ"><label for="f-{nom}">{e(label)}</label><select id="f-{nom}" name="{nom}"{" required" if requis else ""}>{o}</select></div>'

    def ent(nom, label, typ="text", attrs=""):
        return f'<div class="champ"><label for="f-{nom}">{e(label)} <small>({"optional" if not fr else "facultatif"})</small></label><input id="f-{nom}" name="{nom}" type="{typ}"{attrs}></div>'
    seances = [("", "—")] + [(a["en"], a[lang]) for a, b, ph in C.COURS["ateliers"]] + [(a["en"], a[lang]) for a, b in C.COURS["equipes"]] + [("To define together", "To define together" if not fr else "À définir ensemble")]
    bloc_retraite = (f'<div class="formulaire__deux">{ent("personnes", "Number of people" if not fr else "Nombre de personnes", "number", " min=\"1\" max=\"10\" inputmode=\"numeric\"")}</div>'
                     f'{sel("appel", "Best time for a discovery call (French time)" if not fr else "Moment préféré pour l'échange découverte (heure française)", [("", "—"), ("Morning", "Morning" if not fr else "Matin"), ("Afternoon", "Afternoon" if not fr else "Après-midi"), ("Evening", "Evening" if not fr else "Soir")])}')
    bloc_cours = (f'<div class="formulaire__deux">{sel("organisation", "You are" if not fr else "Vous êtes", [("Individual", "An individual" if not fr else "Un particulier"), ("Family", "A family" if not fr else "Une famille"), ("Group", "A group" if not fr else "Un groupe"), ("Team", "A team" if not fr else "Une équipe"), ("Event planner", "An event planner" if not fr else "Un organisateur d'événements")])}{ent("etablissement", "Company or organisation" if not fr else "Société ou organisme", "text", " autocomplete=\"organization\"")}</div>'
                  f'<div class="formulaire__deux">{ent("date_souhaitee", "Preferred date" if not fr else "Date souhaitée", "date")}{ent("groupe", "Group size" if not fr else "Taille du groupe", "number", " min=\"1\" max=\"40\" inputmode=\"numeric\"")}</div>'
                  f'<div class="formulaire__deux">{sel("seance", "Session" if not fr else "Séance", seances)}{ent("budget", "Budget per person or per group" if not fr else "Budget par personne ou par groupe")}</div>')
    bloc_evenement = (f'<div class="formulaire__deux">{sel("type_evenement", "Type of event" if not fr else "Type d'événement", [("Private hire", "Private hire of the Espace" if not fr else "Privatisation de l'Espace"), ("Aperitif in the gallery", "Aperitif in the gallery" if not fr else "Apéritif dans la galerie"), ("Team workshop", "Team workshop" if not fr else "Atelier d'équipe"), ("Other", "Other" if not fr else "Autre")])}{ent("date_evenement", "Preferred date" if not fr else "Date souhaitée", "date")}</div>'
                      f'{ent("invites", "Number of guests" if not fr else "Nombre d'invités", "number", " min=\"1\" max=\"80\" inputmode=\"numeric\"")}')
    opts = "".join(f'<option value="{oid}">{e(titre(OEUVRES[oid], lang))}{"" if OEUVRES[oid]["titre"] else " (" + oid + ")"}</option>' for sid in ORDRE for oid in LISTES[sid]) + f'<option value="where-do-i-begin">Where Do I Begin?</option>'

    def champ(nom, label, typ="text", requis=True, auto=""):
        a = f' autocomplete="{auto}"' if auto else ""
        r = " required" if requis else ""
        etoile = ' <span aria-hidden="true">*</span>' if requis else f' <small>({"optional" if lang == "en" else "facultatif"})</small>'
        if typ == "textarea":
            ctrl = f'<textarea id="f-{nom}" name="{nom}" rows="6"{r}></textarea>'
        else:
            ctrl = f'<input id="f-{nom}" name="{nom}" type="{typ}"{a}{r}>'
        return f'<div class="champ"><label for="f-{nom}">{e(label)}{etoile}</label>{ctrl}<p class="champ__erreur" aria-live="polite"></p></div>'
    corps = f'''
<section class="contact" data-strate="{e(t["nav"]["contact"])}">
  <div class="contact__tete">{surtitre("Let's connect" if lang == "en" else "Restons en lien")}<h1 class="bandeau__titre">{lettres("Let's connect…" if lang == "en" else "Écrivez-moi…")}</h1></div>
  <div class="contact__grille">
    <form class="formulaire" data-formulaire novalidate>
      <fieldset class="champ"><legend>{"About" if lang == "en" else "À propos de"}</legend><div class="choix-groupe">{radios}</div></fieldset>
      <div class="champ" data-pour="oeuvre"><label for="f-oeuvre">{"Which work?" if lang == "en" else "Quelle œuvre ?"}</label><select id="f-oeuvre" name="oeuvre"><option value="">—</option>{opts}</select></div>
      <div class="formulaire__bloc" data-pour="retraite" hidden><div class="champ"><label for="f-retraite">{"Which retreat?" if lang == "en" else "Quelle retraite ?"}</label><select id="f-retraite" name="retraite">{"".join(f'<option value="{k}">{e(RETRAITES[k]["titre"])} · {e(L(lang, RETRAITES[k]["dates"]))}</option>' for k in RETRAITES_ORDRE)}</select></div>{bloc_retraite}</div>
      <div class="formulaire__bloc" data-pour="cours_prives" hidden>{bloc_cours}</div>
      <div class="formulaire__bloc" data-pour="evenement" hidden>{bloc_evenement}</div>
      <div class="formulaire__deux">{champ("prenom", "First name" if lang == "en" else "Prénom", auto="given-name")}{champ("nom", "Last name" if lang == "en" else "Nom", auto="family-name")}</div>
      <div class="formulaire__deux">{champ("email", "Email" if lang == "en" else "Adresse électronique", "email", auto="email")}{champ("tel", "Phone" if lang == "en" else "Téléphone", "tel", False, "tel")}</div>
      {champ("message", "Message", "textarea")}
      <div class="champ champ--case"><label><input type="checkbox" name="accord" required> <span>{e("I agree that Lisa Cirenza may use these details to reply to me." if lang == "en" else "J'accepte que Lisa Cirenza utilise ces informations pour me répondre.")}</span></label><p class="champ__erreur" aria-live="polite"></p></div>
      <p class="formulaire__erreurs" hidden role="alert">{e("Please check the highlighted fields." if lang == "en" else "Vérifiez les champs signalés.")}</p>
      <p class="note">{e("Mock-up: this form sends nothing. It prepares an email for you to send." if lang == "en" else "Maquette : ce formulaire n'envoie rien. Il prépare un courriel que vous envoyez vous-même.")}</p>
      <button class="bouton aimant" type="submit"><span>{e("Prepare my message" if lang == "en" else "Préparer mon message")}</span></button>
    </form>
    <div class="formulaire__merci" hidden tabindex="-1"><h2>{e("Your message is ready" if lang == "en" else "Votre message est prêt")}</h2><p>{e("Nothing has been sent. Open your email app to send it:" if lang == "en" else "Rien n'a été envoyé. Ouvrez votre messagerie pour l'envoyer :")}</p><p><a class="bouton aimant" data-mailto href="mailto:{c["courriel"]}"><span>{e("Open my email" if lang == "en" else "Ouvrir ma messagerie")}</span></a></p></div>
    <aside class="contact__coord">
      {figure_photo(prof, "espace/facade-de-nuit", "The Espace Créa-Tea-Vité at night" if lang == "en" else "L'Espace Créa-Tea-Vité de nuit", "", "fossile", "(max-width: 800px) 86vw, 30vw")}
      <address><strong>{e(c["atelier"])}</strong><br>{e(c["espace"])}<br>{e(c["rue"])}<br>{e(c["ville"])}, {e(c["pays"][lang])}</address>
      <p><a class="courriel" href="mailto:{c["courriel"]}">{c["courriel"]}</a><br><a href="mailto:{c["courriel_espace"]}">{c["courriel_espace"]}</a></p>
      <p><a href="tel:{c["tel_brut"]}">{e(c["tel"])}</a> · <a href="https://wa.me/{c["tel_brut"].lstrip("+")}">WhatsApp</a></p>
      {statut(lang)}
      <p class="pied__reseaux"><a href="{c["instagram"]}">Instagram</a> · <a href="{c["linkedin"]}">LinkedIn</a> · <a href="{c["facebook"]}">Facebook</a></p>
      <p class="note">{e("Less than an hour from Geneva airport." if lang == "en" else "À moins d'une heure de l'aéroport de Genève.")}</p>
    </aside>
  </div>
</section>'''
    ecrire(chemin, page(lang, "contact", chemin, t["nav"]["contact"], corps, href_autre(lang, "contact", prof), {}, "page-contact"))


# ================================================================ 404
def page_404():
    global MODE
    ancien = MODE
    corps = f'''
<section class="erreur" data-strate="404">
  {figure_photo(0, "artiste/lisa-a-17-ans-juneau-icefield", "A figure on skis crossing a vast icefield", "", "fossile erreur__img", "(max-width: 800px) 70vw, 30vw")}
  <div><p class="surtitre"><span class="surtitre__n">404</span><span>Crevasse</span></p>
  <h1 class="bandeau__titre">{lettres("You fell into a crevasse")}</h1>
  <p lang="fr">Vous êtes tombé dans une crevasse : cette page n'existe pas.</p>
  <p>{bouton("Back to the surface", "/")} {bouton("Retour à la surface", "/fr", "bouton bouton--ligne")}</p></div>
</section>'''
    MODE = "propres"
    txt = page("en", "404", "404.html", "404", corps, "/fr", {}, "page-404")
    MODE = ancien
    ecrire("404.html", txt)


# ================================================================ données JS
def donnees_js(lang):
    t = C.T[lang]
    oe = {}
    for oid, o in OEUVRES.items():
        notes = []
        if o["situation"]:
            notes.append(t["photo_situation"])
        if o["a_confirmer"]:
            notes.append(t["image_a_confirmer"])
        if o["dims_a_verifier"]:
            notes.append(("Dimensions " if lang == "en" else "Dimensions ") + t["dims_a_verifier"])
        oe[oid] = {
            "titre": o["titre"], "titreAff": titre(o, lang), "dims": dims_txt(o, lang), "h": o["hcm"], "l": o["lcm"],
            "technique": (o["technique"] or {}).get(lang), "edition": (o["edition"] or {}).get(lang), "annee": o["annee"],
            "statut": o["statut"], "texte": (o["texte"] or {}).get(lang), "ratio": o["ratio"], "t": o["t"], "loupe": o["loupe"],
            "fond": o["fond"], "alt": o["alt"][lang], "series": o["series"], "notes": notes,
        }
    series = {sid: {"titre": SERIES[sid]["titre"][lang], "oeuvres": LISTES[sid]} for sid in ORDRE}
    series["hors-serie"] = {"titre": "", "oeuvres": LISTES["hors-serie"]}
    decors = {
        "chalet": {"src": "img/decors/voir-au-mur-chalet-16x9.webp", "w": 1168, "h": 784, "pxcm": 2.55, "sol": 634, "cx": 627, "basMin": 96},
        "chaletV": {"src": "img/decors/voir-au-mur-chalet-9x16.webp", "w": 784, "h": 1168, "pxcm": 2.75, "sol": 965, "cx": 400, "basMin": 100},
        "galerie": {"src": "img/decors/voir-au-mur-galerie-16x9.webp", "w": 1168, "h": 784, "pxcm": 2.0, "sol": 605, "cx": 584, "basMin": 70},
    }
    d = {"langue": lang, "textes": t, "oeuvres": oe, "series": series, "decors": decors,
         "pageContact": C.PAGES["contact"][lang] + (".html" if MODE == "html" else ""),
         "espace": {"horaires": HEURES, "courriel": C.COORD["courriel"]},
         "retraites": {"pip": {"debut": R.PIP["debut"], "titre": R.PIP["titre"]}, "encaustics": {"debut": R.ENCAUSTICS["debut"], "titre": R.ENCAUSTICS["titre"]}}}
    if lang == "fr":
        def corriger(x):
            if isinstance(x, str):
                return typo_fr(x)
            if isinstance(x, list):
                return [corriger(y) for y in x]
            if isinstance(x, dict):
                return {k: (v if k in ("src", "t", "series", "oeuvres", "decors") else corriger(v)) for k, v in x.items()}
            return x
        d = corriger(d)
    (SITE / "assets" / "js" / f"donnees-{lang}.js").write_text("window.LC_DONNEES=" + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")



# ================================================================ v5 · éditeur des horaires (outil de la maquette, hors menu)
EDITEUR = {
    "en": {"ferme": "Closed", "ouvert": "Open", "rdv": "By appointment", "de": "From", "a": "To", "de2": "2nd slot from", "a2": "To",
           "exception": "Exception", "exemple": "Example", "du": "First day", "au": "Last day", "afficher": "Show the message from",
           "genre": "On these days", "ferme_ex": "Closed", "special": "Special hours", "msg_en": "Message in English", "msg_fr": "Message in French",
           "supprimer": "Remove", "visible": "shown {du} → {au}", "aucune": "No announcement today",
           "etat_publie": "These are the published hours.", "etat_modifie": "Changes not yet previewed or published.",
           "apercu_actif": "Preview active in this browser: open any page of the site to see it.", "stockage": "This browser blocks the preview (private browsing?)."},
    "fr": {"ferme": "Fermé", "ouvert": "Ouvert", "rdv": "Sur rendez-vous", "de": "De", "a": "À", "de2": "2e plage de", "a2": "À",
           "exception": "Exception", "exemple": "Exemple", "du": "Premier jour", "au": "Dernier jour", "afficher": "Afficher le message dès le",
           "genre": "Ces jours-là", "ferme_ex": "Fermé", "special": "Horaires spéciaux", "msg_en": "Message en anglais", "msg_fr": "Message en français",
           "supprimer": "Supprimer", "visible": "affiché du {du} au {au}", "aucune": "Aucune annonce aujourd'hui",
           "etat_publie": "Ce sont les horaires publiés.", "etat_modifie": "Modifications pas encore prévisualisées ni publiées.",
           "apercu_actif": "Aperçu actif dans ce navigateur : ouvrez n'importe quelle page du site pour le voir.", "stockage": "Ce navigateur bloque l'aperçu (navigation privée ?)."},
}


def page_horaires(lang):
    fr = lang == "fr"
    chemin = fichier(lang, "horaires")
    prof = prof_de(chemin)
    titre_p = "Opening hours" if not fr else "Horaires d'ouverture"
    intro = (["Change the Espace's weekly hours, closures and announcements here, then preview them on the whole site before anything is published.",
              "On the final site, these same fields live in the Wix dashboard, in two collections: Opening hours and Exceptions. You edit them from the Wix app on your phone, and the site updates by itself."]
             if not fr else
             ["Modifiez ici les horaires de la semaine, les fermetures et les annonces de l'Espace, puis voyez-les sur tout le site avant toute publication.",
              "Sur le site final, ces mêmes champs sont dans le tableau de bord Wix, en deux collections : Horaires et Exceptions. Vous les modifiez depuis l'application Wix sur votre téléphone, et le site se met à jour tout seul."])
    corps = f'''
{bandeau(lang, prof, None, "Mock-up tool · for Lisa" if not fr else "Outil de la maquette · pour Lisa", titre_p, intro, figure_photo(prof, "espace/enseigne-rue-village", "The Espace Créa-Tea-Vité sign in the village street" if not fr else "L'enseigne de l'Espace Créa-Tea-Vité dans la rue du village", "", "fossile", "(max-width: 900px) 80vw, 30vw"), titre_p, "bandeau--horaires")}
<section class="editeur" data-editeur-horaires data-strate="{e("Editor" if not fr else "Éditeur")}">
  <div class="editeur__colonne">
    {surtitre("Every week" if not fr else "Chaque semaine", 1)}
    <div class="editeur__semaine" data-editeur-semaine></div>
    {surtitre("Closures, special hours and announcements" if not fr else "Fermetures, horaires spéciaux et annonces", 2)}
    <p class="note">{e("An exception replaces the usual hours between two dates. Its message appears in the bar at the top of every page, from the chosen date (ten days before by default) until the last day." if not fr else "Une exception remplace les horaires habituels entre deux dates. Son message s'affiche dans la barre en haut de toutes les pages, dès la date choisie (dix jours avant par défaut) et jusqu'au dernier jour.")}</p>
    <div class="editeur__exceptions" data-editeur-exceptions></div>
    <p><button class="bouton bouton--ligne" type="button" data-editeur-ajouter><span>{e("+ Add an exception" if not fr else "+ Ajouter une exception")}</span></button></p>
  </div>
  <aside class="editeur__apercu" aria-label="{e("Preview" if not fr else "Aperçu")}">
    <p class="surtitre"><span>{e("What visitors see" if not fr else "Ce que voient les visiteurs")}</span></p>
    <dl class="horaires horaires--grand" data-editeur-liste></dl>
    <p class="statut statut--grand"><span class="statut__point" aria-hidden="true"></span><span class="statut__texte" data-editeur-statut></span></p>
    <p class="editeur__annonce"><span>{e("Top bar today" if not fr else "Barre du haut aujourd'hui")}</span> <strong data-editeur-annonce></strong></p>
    <p class="editeur__sous">{e("Coming up" if not fr else "À venir")}</p>
    <ul class="editeur__prochaines" data-editeur-prochaines></ul>
    <p class="editeur__etat" data-editeur-etat role="status"></p>
    <div class="editeur__boutons">
      <button class="bouton" type="button" data-editeur-apercu><span>{e("Preview on the site" if not fr else "Voir sur le site")}</span></button>
      <button class="bouton bouton--ligne" type="button" data-editeur-arreter><span>{e("Back to the published hours" if not fr else "Revenir aux horaires publiés")}</span></button>
      <button class="bouton bouton--ligne" type="button" data-editeur-telecharger><span>{e("Download the file" if not fr else "Télécharger le fichier")}</span></button>
    </div>
    <p class="note">{e("For P'tit Kiwi: the downloaded file replaces assets/data/horaires.json, and the site reads it at every visit (no rebuild needed)." if not fr else "Pour P'tit Kiwi : le fichier téléchargé remplace assets/data/horaires.json, que le site relit à chaque visite (sans régénération).")}</p>
  </aside>
  <noscript><p class="note">{e("The editor needs JavaScript." if not fr else "L'éditeur a besoin de JavaScript.")}</p></noscript>
</section>'''
    ecrire(chemin, page(lang, "horaires", chemin, titre_p, corps, href_autre(lang, "horaires", prof), {"editeur": EDITEUR[lang]}, "page-horaires"))




# ================================================================ v6 · pages demandées par Lisa (20 novembre 2026)
# Les vidéos du procédé, en ligne sur la page /salon du site actuel (Wix Video) : chargées seulement au clic, après accord.
VIDEOS_PROCEDE = [
    {"titre": "Encaustic Painting Process", "fr": "Le procédé de la peinture à l'encaustique", "id": "47a93e_bc67f82a443c442e8b080df19df4092d", "q": "720p", "duree": "1:07"},
    {"titre": "Hot Surface Direct Encaustic Painting", "fr": "Peindre directement sur une surface chaude", "id": "47a93e_a7f40a63c3834beb9907c41a8561cfcd", "q": "360p", "duree": "1:00"},
    {"titre": "Rose Coloured Glasses Process", "fr": "Le procédé de Rose Coloured Glasses", "id": "47a93e_55a610a4583a4ea3a0d05110def02376", "q": "720p", "duree": "1:03"},
]


def videos_procede(lang):
    fr = lang == "fr"
    items = ""
    for v in VIDEOS_PROCEDE:
        affiche = f"https://static.wixstatic.com/media/{v['id']}f002.jpg/v1/fill/w_640,h_640,enc_auto/file.jpeg"
        src = f"https://video.wixstatic.com/video/{v['id']}/{v['q']}/mp4/file.mp4"
        nom = v["fr"] if fr else v["titre"]
        items += (f'<li class="video-procede" data-video-mp4="{src}"><button class="video-procede__bouton" type="button" aria-label="{e(("Play: " if not fr else "Lire : ") + nom)}">'
                  f'<img src="{affiche}" alt="" width="640" height="640" loading="lazy" decoding="async"><span class="video__jouer" aria-hidden="true"><i></i></span>'
                  f'<span class="video-procede__duree">{v["duree"]}</span></button><p>{e(nom)}</p></li>')
    return (f'<div class="videos-procede"><p class="surtitre"><span>{e("Wax process videos" if not fr else "Vidéos du procédé à la cire")}</span></p><ul class="videos-procede__liste">{items}</ul>'
            f'<p class="note">{e("The three videos already online on cirenza.com (Processes page), hosted by Wix. They load only when you play them." if not fr else "Les trois vidéos déjà en ligne sur cirenza.com (page Processes), hébergées par Wix. Elles ne se chargent que si vous les lancez.")}</p></div>')


ENTITE_ESPACE = {"en": "Espace Créa-Tea-Vité · SAS Atelier Truffle · SIRET 989 397 146 00014 · VAT-registered (VAT number to come) · 27 Passage du Mont Blanc, 74220 La Clusaz, France · atelier@cirenza.com",
                 "fr": "Espace Créa-Tea-Vité · SAS Atelier Truffle · SIRET 989 397 146 00014 · assujettie à la TVA (numéro de TVA à venir) · 27 Passage du Mont Blanc, 74220 La Clusaz, France · atelier@cirenza.com"}


def bloc_entite(lang):
    return f'<p class="entite"><span>{e("Organised and invoiced by" if lang == "en" else "Organisé et facturé par")}</span> {e(ENTITE_ESPACE[lang])}</p>'


# ---------------------------------------------------------------- Boutique & Tea Room : sur place, rien n'est vendu en ligne
def page_salon_the(lang):
    t = C.T[lang]
    fr = lang == "fr"
    chemin = fichier(lang, "salon_the")
    prof = prof_de(chemin)
    carte = ""
    for g in C.CARTE:
        lis = ""
        for nom, prix, desc in g["items"]:
            lis += f'<li><span class="boisson__nom">{e(L(lang, nom))}</span><span class="boisson__points" aria-hidden="true"></span><span class="boisson__prix">{e(prix if lang == "fr" else prix.replace(",", "."))} €</span>{f"<span class=boisson__desc>{e(L(lang, desc))}</span>" if desc else ""}</li>'
        carte += f'<div class="carte-boissons__groupe"><h3>{e(g["titre"][lang])}</h3><ul>{lis}</ul></div>'
    adresse = quote(f'{C.COORD["espace"]}, {C.COORD["rue"]}, {C.COORD["ville"]}, France')
    corps = f'''
{bandeau(lang, prof, None, "Visit in person · nothing is sold online" if not fr else "Sur place · rien n'est vendu en ligne", t["nav"]["salon_the"], [C.ESPACE["intro"][lang], C.ESPACE["ecran"][lang]], figure_photo(prof, "espace/salon-vertical", "The lounge of the Espace, fireplace and bookshelves" if not fr else "Le salon de l'Espace, la cheminée et la bibliothèque", "", "fossile", "(max-width: 900px) 80vw, 34vw"), t["nav"]["salon_the"])}
<section class="salon-boutique" data-strate="Boutique">
  {figure_photo(prof, "espace/atelier-rangements", "The shelves of art materials at the Espace" if not fr else "Les étagères de matériel d'art de l'Espace", "", "fossile salon-boutique__img", "(max-width: 800px) 80vw, 30vw")}
  <div>{surtitre("In the boutique" if not fr else "Dans la boutique", 1)}<h2 class="titre-section">{lettres("Boutique" if not fr else "La boutique")}</h2>
  <ul class="liste-traits">
    <li>{e("Gallery & Tea Room: Local artists & artisans, warm and cold signature beverages, and space to ponder." if not fr else "Galerie et salon de thé : artistes et artisans du pays, boissons signature chaudes et froides, et de l'espace pour rêver.")}</li>
    <li>{e("Creative Corner: Hands-on workshops and open studio time." if not fr else "Coin créatif : ateliers pratiques et temps d'atelier libre.")}</li>
    <li>{e("Boutique: Curated art materials and unique local gifts." if not fr else "Boutique : matériel d'art choisi et cadeaux locaux uniques.")}</li>
  </ul>
  <p class="note"><span class="exemple">{"to come" if not fr else "à venir"}</span> {e("The detailed list of what is in the boutique (brands of materials, kits, local makers and gifts): Lisa's list to come." if not fr else "La liste détaillée de la boutique (marques de matériel, kits, créateurs du pays et cadeaux) : liste de Lisa à venir.")}</p></div>
</section>
<section class="carte-boissons" id="carte" tabindex="-1" data-strate="{e("Menu" if not fr else "La carte")}">
  <div class="carte-boissons__image">{figure_photo(prof, "espace/salon-canape", "The lounge of the Espace, sofa and paintings" if not fr else "Le salon de l'Espace, canapé et tableaux", "", "fossile", "(max-width: 800px) 80vw, 30vw")}</div>
  <div class="carte-boissons__texte">{surtitre("Tea room" if not fr else "Salon de thé", 2)}<h2 class="titre-section">{lettres("The menu" if not fr else "La carte")}</h2>{carte}<p class="note">{e(C.CARTE_NOTE[lang])}</p></div>
</section>
<section class="infos" id="horaires" tabindex="-1" data-strate="{e(t["horaires"])}">
  {figure_photo(prof, "espace/enseigne-rue-village", "The Créa-Tea-Vité sign in the village street" if not fr else "L'enseigne Créa-Tea-Vité dans la rue du village", "", "fossile infos__img", "(max-width: 800px) 80vw, 30vw")}
  <div class="infos__texte">{surtitre(t["horaires"], 3)}<dl class="horaires horaires--grand" data-horaires-liste>{"".join(f"<div><dt>{e(j)}</dt><dd>{e(h)}</dd></div>" for j, h in t["horaires_lignes"])}</dl>{statut(lang, "statut--grand")}
  <address>{e(C.COORD["espace"])}<br>{e(C.COORD["rue"])}<br>{e(C.COORD["ville"])}, France</address>
  <p class="acces">{e("Map:" if not fr else "Plan :")} <a href="https://www.google.com/maps/search/?api=1&amp;query={adresse}" target="_blank" rel="noopener">Google Maps</a> · <a href="https://maps.apple.com/?q={adresse}" target="_blank" rel="noopener">Apple Plans</a> · <a href="https://www.openstreetmap.org/search?query={adresse}" target="_blank" rel="noopener">OpenStreetMap</a></p>
  <p class="note"><span class="exemple">{"to come" if not fr else "à venir"}</span> {e("Parking: where to park in the village, and how far it is on foot. Lisa's details to come." if not fr else "Stationnement : où se garer dans le village, et à combien de minutes à pied. Précisions de Lisa à venir.")}</p>
  <p><a href="mailto:{C.COORD["courriel_espace"]}">{C.COORD["courriel_espace"]}</a> · <a href="tel:{C.COORD["tel_brut"]}">{e(C.COORD["tel"])}</a></p></div>
</section>'''
    ecrire(chemin, page(lang, "salon_the", chemin, t["nav"]["salon_the"], corps, href_autre(lang, "salon_the", prof), {}, "page-salon-the"))


# ---------------------------------------------------------------- Co-Creating Sessions : texte de la page de réservation actuelle, mot pour mot
COSESSIONS = {
    "accroche": {"en": "A place to work on, and get advice on your personal creative projects ...", "fr": "Un lieu pour avancer sur vos projets créatifs personnels, et recevoir des conseils..."},
    "description": {"en": "Come paint, draw, write... Sip a warm drink (included) and enjoy personalised guidance from the artist to help refine  your next spark of inspiration. Bring your own materials, use some of our basics, or buy one of our kits. If you don't have a specific project, be inspired by our library of books and images. Water, table easels, and other accessories will be available to borrow.",
                    "fr": "Venez peindre, dessiner, écrire... Une boisson chaude (comprise) à la main, profitez de conseils personnalisés de l'artiste pour affiner votre prochaine étincelle d'inspiration. Apportez votre matériel, utilisez nos fournitures de base ou achetez l'un de nos kits. Sans projet précis, laissez-vous inspirer par notre bibliothèque de livres et d'images. Eau, chevalets de table et autres accessoires à emprunter sur place."},
    "annulation_en": "No refunds are available once the session has started. Any cancellation request must be submitted in writing to atelier@cirenza.com, at least 72 hours before the course begins. If your space can be filled after cancellation, 90% of your total payment will be refunded. If the space cannot be filled, the fee is non-refundable.",
    "annulation_fr": "Aucun remboursement n’est possible après le début du cours, ni en cas d’absence à une séance. Toute demande d’annulation doit être adressée par écrit à atelier@cirenza.com, au moins 72 heures avant le début du cours. Si votre place peut être comblée après une annulation, 90 % du montant total payé vous seront remboursés. Dans le cas contraire, les frais restent dus et ne sont pas remboursables.",
}


def page_cosessions(lang):
    t = C.T[lang]
    fr = lang == "fr"
    chemin = fichier(lang, "cosessions")
    prof = prof_de(chemin)
    K = COSESSIONS
    corps = f'''
{bandeau(lang, prof, None, "Open studio · €30" if not fr else "Atelier ouvert · 30 €", t["nav"]["cosessions"], [K["accroche"][lang], K["description"][lang]], figure_photo(prof, "cours/atelier-libre-pastel", "A participant working in the studio" if not fr else "Une participante au travail à l'atelier", "", "fossile", "(max-width: 900px) 80vw, 34vw"), t["nav"]["cosessions"])}
<section class="calendrier" data-strate="{e("Upcoming sessions" if not fr else "Prochaines séances")}">
  {surtitre("Upcoming sessions" if not fr else "Prochaines séances", 1)}<h2 class="titre-section">{lettres("Calendar" if not fr else "Calendrier")}</h2>
  <div class="calendrier__cadre"><p>{e("On the final site, this calendar shows the sessions from Wix Bookings on your current site (the same service, prices and bookings), and visitors book and pay here." if not fr else "Sur le site final, ce calendrier affiche les séances de Wix Bookings de votre site actuel (même service, mêmes prix, mêmes réservations), et les visiteurs réservent et paient ici.")}</p>
  <p>{bouton("Ask for the next dates" if not fr else "Demander les prochaines dates", lien(lang, "contact", prof) + "?objet=autre")}</p></div>
</section>
<section class="conditions-courtes" data-strate="{e("Cancellation policy" if not fr else "Conditions d'annulation")}">
  {surtitre("Cancellation policy" if not fr else "Conditions d'annulation", 2)}
  <div class="conditions-courtes__deux"><div lang="en"><h3>Cancellation Policy</h3><p>{e(K["annulation_en"])}</p></div><div lang="fr"><h3>Conditions d’annulation</h3><p>{e(K["annulation_fr"])}</p></div></div>
  {bloc_entite(lang)}
</section>'''
    ecrire(chemin, page(lang, "cosessions", chemin, t["nav"]["cosessions"], corps, href_autre(lang, "cosessions", prof), {}, "page-cosessions"))


# ---------------------------------------------------------------- Expositions et événements : l'exposition en cours, puis la suite
def page_expositions(lang):
    t = C.T[lang]
    fr = lang == "fr"
    chemin = fichier(lang, "expositions")
    prof = prof_de(chemin)
    ex = C.EXPO
    commence = DT.date.fromisoformat(ex["debut"]) <= AUJ
    etat_txt = ("On now" if not fr else "En cours") if commence else (("Opens " if not fr else "Ouverture le ") + ("3 December 2026" if not fr else "3 décembre 2026"))
    av = (C.CV.get("a_venir") or {}).get(lang)
    a_venir = "".join(f'<li>{e(x)}</li>' for x in ([av] if isinstance(av, str) else (av or [])))
    corps = f'''
<section class="bandeau bandeau--expo" data-strate="{e(ex["titre"])}">
  <div class="bandeau__texte">
    {surtitre(("Current exhibition" if commence else "Upcoming exhibition") if not fr else ("Exposition en cours" if commence else "Exposition à venir"))}
    <h1 class="bandeau__titre">{lettres(ex["titre"])}</h1>
    <p class="bandeau__accroche"><span class="etiquette">{e(etat_txt)}</span> {e(ex["dates"][lang])} · Espace Créa-Tea-Vité, La Clusaz</p>
    <div class="bandeau__intro" data-apparait><p>{e(ex["intro"][lang])}</p></div>
  </div>
  <div class="bandeau__image">{figure_photo(prof, "exposition-en-cours/bnt-designs-soudure", "BNT Designs welding a steel sphere" if not fr else "BNT Designs soude une sphère d'acier", "BNT Designs", "fossile", "(max-width: 900px) 80vw, 34vw")}</div>
</section>
<section class="expo-artistes" data-strate="{e("The artists" if not fr else "Les artistes")}">
  {surtitre("The artists" if not fr else "Les artistes", 1)}
  <div class="expo-artistes__grille">
    <article>{figure_photo(prof, "exposition-en-cours/bnt-designs-soudure", "", "", "fossile", "(max-width: 800px) 80vw, 26vw")}<h3>BNT Designs</h3><p>{e(ex["bnt"][lang])}</p></article>
    <article><figure class="oeuvre" style="--ratio:{OEUVRES["recente-01"]["ratio"]}">{bouton_oeuvre(prof, "recente-01", lang, LEAD, "(max-width: 800px) 80vw, 26vw")}</figure><h3>Lisa Cirenza</h3><p>{e(ex["lisa"][lang])}</p><p>{bouton(SERIES[LEAD]["titre"][lang], lien_salle(lang, LEAD, prof), "bouton bouton--ligne")}</p></article>
    <article><div class="expo-artistes__absent" aria-hidden="true"><span>Le Petit Lapin</span></div><h3>Le Petit Lapin</h3><p>{e(ex["lapin"][lang])}</p></article>
  </div>
</section>
<section class="evenements-liste" data-strate="{e("Events" if not fr else "Événements")}">
  {surtitre("Events" if not fr else "Événements", 2)}<h2 class="titre-section">{lettres("Coming up" if not fr else "À venir")}</h2>
  <ul class="liste-traits">{a_venir or "<li>" + e("Opening, talks and other events: dates to come from Lisa." if not fr else "Vernissage, rencontres et autres événements : dates à venir de Lisa.") + "</li>"}</ul>
  <p>{bouton(t["nav"]["evenements"], lien(lang, "evenements", prof), "bouton bouton--ligne")}{bouton(t["nav"]["cosessions"], lien(lang, "cosessions", prof), "bouton bouton--ligne")}</p>
</section>'''
    ecrire(chemin, page(lang, "expositions", chemin, t["nav"]["expositions"], corps, href_autre(lang, "expositions", prof), {"expoFin": ex["fin"]}, "page-expositions"))


# ---------------------------------------------------------------- échéancier et conditions d'annulation (texte de Lisa, coordonnées de la SAS)
CONDITIONS = {
    "en": [
        ("", "Think of this as the recipe card for the practical side: short, clear and no hidden ingredients. If anything is unclear, just write to me. I’d much rather answer a question than have you wonder."),
        ("1. Securing your place", "A deposit of €200 secures your place on the retreat. It is deducted from your first payment."),
        ("2. Payment schedule", "50% of the retreat fee is due six months before the retreat begins. The remaining 50% is due three months before the retreat begins. We’ll send you each payment request by email in good time. Any early-bird, returner or other reduction is taken off your final payment."),
        ("3. Right of withdrawal", "In accordance with Article L221-28 of the French Consumer Code, the 14-day right of withdrawal does not apply to accommodation and leisure services provided on a specific date or for a specific period. Your booking is therefore final once your deposit is paid."),
        ("4. If you cancel", "Our retreats are small and planned around each group, so most of our costs (lodging, materials and excursions) are committed well in advance. Please let us know in writing (by email) if you need to cancel. The following cancellation fees apply: More than six months before the retreat: the €200 deposit is retained. Between six and three months before the retreat: 50% of the retreat fee is retained. Less than three months before the retreat: 100% of the retreat fee is retained. If you cancel, you won’t be asked for any payment that isn’t yet due."),
        ("5. Transferring your place", "You may transfer your place to another person who meets the conditions of the retreat, provided you let us know in writing at least seven days before the retreat begins. If we find a replacement from our waiting list, the same applies. In either case, we’ll refund everything you’ve paid, less the actual costs of the transfer, up to a maximum of 5% of the amount paid. You and the person taking your place remain jointly responsible for any balance due and for these costs."),
        ("6. Exceptional circumstances", "If exceptional and unavoidable circumstances at or near the retreat location (for example a natural disaster or a public health emergency) significantly affect the retreat or your travel to it, you may cancel without any cancellation fee and receive a full refund."),
        ("7. If we cancel", "If we have to cancel the retreat for any reason, you’ll receive a full refund of everything you’ve paid, within 14 days."),
        ("8. Travel insurance", "We strongly recommend comprehensive travel insurance that covers cancellation. Past guests who had to cancel were very glad to have been fully insured."),
        ("Questions?", "Write to me at Atelier@cirenza.com"),
        ("", "Pack your curiosity and a sense of humour; I’ll handle the small print."),
    ],
    "fr": [
        ("", "Voyez ceci comme la fiche recette du côté pratique : courte, claire, sans ingrédient caché. Si quelque chose n'est pas clair, écrivez-moi. Je préfère de loin répondre à une question que vous laisser dans le doute."),
        ("1. Réserver votre place", "Un acompte de 200 € réserve votre place. Il est déduit de votre premier paiement."),
        ("2. Échéancier", "50 % du prix de la retraite sont dus six mois avant son début. Les 50 % restants sont dus trois mois avant son début. Nous vous envoyons chaque demande de paiement par courriel, en temps utile. Toute remise (inscription anticipée, participant déjà venu ou autre) est déduite de votre dernier paiement."),
        ("3. Droit de rétractation", "Conformément à l'article L221-28 du Code de la consommation, le délai de rétractation de 14 jours ne s'applique pas aux prestations d'hébergement et de loisirs fournies à une date ou pour une période déterminée. Votre réservation est donc ferme dès le paiement de l'acompte."),
        ("4. Si vous annulez", "Nos retraites sont petites et organisées autour de chaque groupe : la plupart de nos frais (logement, matériel, excursions) sont engagés longtemps à l'avance. Prévenez-nous par écrit (par courriel) si vous devez annuler. Les frais d'annulation sont les suivants : plus de six mois avant la retraite, l'acompte de 200 € est conservé ; entre six et trois mois avant, 50 % du prix de la retraite sont conservés ; moins de trois mois avant, 100 % du prix sont conservés. En cas d'annulation, aucun paiement non encore exigible ne vous sera demandé."),
        ("5. Céder votre place", "Vous pouvez céder votre place à une personne qui remplit les conditions de la retraite, à condition de nous prévenir par écrit au moins sept jours avant son début. Il en va de même si nous trouvons un remplaçant sur notre liste d'attente. Dans les deux cas, nous vous remboursons tout ce que vous avez payé, moins les frais réels de la cession, dans la limite de 5 % du montant payé. Vous et la personne qui prend votre place restez solidairement responsables du solde dû et de ces frais."),
        ("6. Circonstances exceptionnelles", "Si des circonstances exceptionnelles et inévitables sur le lieu de la retraite ou à proximité (par exemple une catastrophe naturelle ou une urgence de santé publique) affectent de façon importante la retraite ou votre voyage, vous pouvez annuler sans frais et être intégralement remboursé."),
        ("7. Si nous annulons", "Si nous devons annuler la retraite, pour quelque raison que ce soit, vous êtes intégralement remboursé de tout ce que vous avez payé, sous 14 jours."),
        ("8. Assurance voyage", "Nous recommandons vivement une assurance voyage complète couvrant l'annulation. Les participants qui ont dû annuler par le passé ont été bien contents d'être entièrement assurés."),
        ("Des questions ?", "Écrivez-moi à atelier@cirenza.com"),
        ("", "Emportez votre curiosité et votre sens de l'humour ; je m'occupe des petites lignes."),
    ],
}


def page_conditions(lang):
    t = C.T[lang]
    fr = lang == "fr"
    chemin = fichier(lang, "conditions")
    prof = prof_de(chemin)
    blocs = "".join((f'<h2>{e(h)}</h2>' if h else "") + f'<p>{e(x)}</p>' for h, x in CONDITIONS[lang])
    corps = f'''
<section class="texte-long" data-strate="{e(t["nav"]["conditions"])}">
  {surtitre(("2027 retreats: " if not fr else "Retraites 2027 : ") + " · ".join(nom_retraite(RETRAITES[k], lang) for k in RETRAITES_ORDRE))}
  <h1 class="bandeau__titre">{lettres("Retreat Payment Schedule and Cancellation Policy" if not fr else "Échéancier de paiement et conditions d'annulation des retraites")}</h1>
  <div class="texte-long__corps">{blocs}<p class="note">{e("Last updated: November 2026" if not fr else "Dernière mise à jour : novembre 2026")}</p>
  {'' if not fr else '<p class="note">Traduction de la version anglaise, qui fait foi ; à relire par Lisa.</p>'}</div>
  {bloc_entite(lang)}
</section>'''
    ecrire(chemin, page(lang, "conditions", chemin, t["nav"]["conditions"], corps, href_autre(lang, "conditions", prof), {}, "page-conditions"))


# ---------------------------------------------------------------- formulaires d'inscription : mêmes adresses, mêmes champs, mêmes formulaires Wix
LOGEMENTS = {
    "en": [
        "Exquisitely designed ensuite lodging in a 4-star apartment across from the Atelier, featuring a contemporary shared kitchen, sophisticated living area, and a serene outdoor terrace – private bedroom with sink & shower €3,295.00 per artist.",
        "Same as above– private bedroom, shared sink,shower room- €2850 per artist",
        "Same as above-- shared bedroom (separate single beds), shared sink/shower room, based on 2 artists that know each other ahead of time that book simultaneously, €2450 per artist",
        "Elegant couple’s accommodation for 2 artists, offering a private ensuite, a modern shared kitchen, and a sophisticated living area in the heart of the village, just 5 minutes from the Atelier. Limited to 2 couples; exclusive non-sharing upgrades available on request – €5500 per couple",
        "Elegant couple’s accommodation for one artist and a non-participating partner, offering a private ensuite, a modern shared kitchen, and a sophisticated living area in the heart of the village, just 5 minutes from the Atelier. Limited to 2 couples; exclusive non-sharing upgrades available on request – €4795 per couple",
    ],
    "fr": [
        "Logement raffiné avec salle d'eau dans un appartement 4 étoiles face à l'atelier, avec cuisine partagée contemporaine, salon élégant et terrasse paisible : chambre individuelle avec lavabo et douche, 3 295 € par artiste.",
        "Même logement : chambre individuelle, lavabo et douche partagés, 2 850 € par artiste",
        "Même logement : chambre partagée (lits simples séparés), lavabo et douche partagés, pour 2 artistes qui se connaissent et s'inscrivent en même temps, 2 450 € par artiste",
        "Logement élégant pour un couple de 2 artistes, avec salle d'eau privée, cuisine partagée moderne et salon élégant au cœur du village, à 5 minutes de l'atelier. Limité à 2 couples ; formules privatives sur demande, 5 500 € par couple",
        "Logement élégant pour un artiste et un partenaire non participant, avec salle d'eau privée, cuisine partagée moderne et salon élégant au cœur du village, à 5 minutes de l'atelier. Limité à 2 couples ; formules privatives sur demande, 4 795 € par couple",
    ],
}
NIVEAUX = {
    "en": ["Eager beaver, the last time I did anything creative was age 5, and it didn’t end well, but I’m ready to reconnect and have fun!",
           "Dabbler, I enjoy creating things, but find it hard to make the time, so this is me finally carving some out!",
           "Committed hobbyist, I make time to create regularly, take the odd class, and I’m ready to stretch beyond my comfort zone.",
           "Practising artist, I’ve built a real practice in one medium (and maybe show or sell my work), and I’m curious to explore others.",
           "Professional artist, I’m trained across many mediums, exhibit and/or teach, and I’m looking to refresh my eye and push my creative voice further.",
           "Unclassifiable, my creativity comes out in other ways (cooking, writing, gardening, spreadsheets…), and I’m eager to see where paint might take it."],
    "fr": ["Grand débutant : la dernière fois que j'ai créé quelque chose, j'avais 5 ans, et ça s'est mal fini, mais je suis prêt à renouer avec la création et à m'amuser !",
           "Touche-à-tout : j'aime créer, mais j'ai du mal à en trouver le temps ; cette fois, je le prends enfin !",
           "Amateur assidu : je crée régulièrement, je prends un cours de temps en temps, et je suis prêt à sortir de ma zone de confort.",
           "Artiste pratiquant : j'ai une vraie pratique dans un médium (j'expose ou je vends peut-être), et j'ai envie d'en explorer d'autres.",
           "Artiste professionnel : formé à de nombreux médiums, j'expose et/ou j'enseigne, et je veux rafraîchir mon regard et pousser ma voix créative plus loin.",
           "Inclassable : ma créativité passe par d'autres chemins (cuisine, écriture, jardin, tableurs…), et je suis curieux de voir où la peinture peut la mener."],
}
ACTIVITES = {
    "en": ["None, I plan to be in the studio as much as possible", "Yoga", "Hiking", "Massage/Spa visit", "Swimming in Lake Annecy", "Paddleboard or kayak in Lake Annecy",
           "Swimming in outdoor heated pool with spa facilities and gym in La Clusaz (with views to die for)"],
    "fr": ["Aucune, je compte passer le plus de temps possible à l'atelier", "Yoga", "Randonnée", "Massage ou spa", "Baignade dans le lac d'Annecy", "Paddle ou kayak sur le lac d'Annecy",
           "Piscine extérieure chauffée avec spa et salle de sport à La Clusaz (avec une vue à couper le souffle)"],
}


def page_inscription(lang, cle):
    t = C.T[lang]
    fr = lang == "fr"
    page_cle = INSCRIPTION[cle]
    chemin = fichier(lang, page_cle)
    prof = prof_de(chemin)
    r = RETRAITES[cle]
    # demande de Lisa : chambres de couple et partenaire non participant sur le formulaire de septembre seulement
    logements = LOGEMENTS[lang][:3] if cle == "pip" else LOGEMENTS[lang]
    titre_f = ("Painting in Paradise Registration" if cle == "pip" else "Alpine Creative Pause Registration") if not fr else f"Inscription · {nom_retraite(r, lang)}"
    sous = ("Register to Paint in Paradise" if cle == "pip" else "Alpine Creative Pause") if not fr else nom_retraite(r, lang)

    def champ(nom, lib, typ="text", requis=False, auto=""):
        a = f' autocomplete="{auto}"' if auto else ""
        etoile = ' <span aria-hidden="true">*</span>' if requis else ""
        return (f'<div class="champ"><label for="i-{nom}">{e(lib)}{etoile}</label>'
                f'<input id="i-{nom}" name="{nom}" type="{typ}"{a}{" required" if requis else ""}><p class="champ__erreur" aria-live="polite"></p></div>')
    opts = "".join(f'<label class="choix choix--long"><input type="radio" name="logement" value="{i + 1}" required><span>{e(x)}</span></label>' for i, x in enumerate(logements))
    niveaux = "".join(f'<label class="choix choix--long"><input type="radio" name="niveau" value="{i + 1}"><span>{e(x)}</span></label>' for i, x in enumerate(NIVEAUX[lang]))
    activites = "".join(f'<label class="choix choix--long"><input type="checkbox" name="activites" value="{i + 1}"><span>{e(x)}</span></label>' for i, x in enumerate(ACTIVITES[lang]))
    corps = f'''
<section class="inscription" data-strate="{e(titre_f)}">
  <div class="inscription__tete">
    {surtitre(L(lang, r["dates"]) + " · La Clusaz")}
    <h1 class="bandeau__titre">{lettres(titre_f)}</h1>
    <p class="bandeau__accroche">{e(sous)}</p>
    {bloc_entite(lang)}
  </div>
  <form class="formulaire inscription__form" data-inscription data-wix-form-id="{FORMULAIRES_WIX[cle]}" novalidate>
    <div class="formulaire__deux">{champ("prenom", "First name" if not fr else "Prénom", "text", True, "given-name")}{champ("nom", "Last name" if not fr else "Nom", "text", True, "family-name")}</div>
    <div class="formulaire__deux">{champ("email", "Email" if not fr else "Courriel", "email", True, "email")}{champ("tel", "Phone" if not fr else "Téléphone", "tel", False, "tel")}</div>
    <fieldset class="champ"><legend>{e("Address" if not fr else "Adresse")} <span aria-hidden="true">*</span></legend>
      <div class="formulaire__deux">{champ("pays", "Country/Region" if not fr else "Pays ou région", "text", True, "country-name")}{champ("adresse", "Address" if not fr else "Adresse", "text", True, "street-address")}</div>
      <div class="formulaire__deux">{champ("ville", "City" if not fr else "Ville", "text", True, "address-level2")}{champ("cp", "Zip / Postal code" if not fr else "Code postal", "text", True, "postal-code")}</div>
    </fieldset>
    <fieldset class="champ"><legend>{e("Preferred Lodging (first come first served)" if not fr else "Logement souhaité (premier arrivé, premier servi)")} <span aria-hidden="true">*</span></legend>
      <p class="note">{e("Please choose one" if not fr else "Choisissez une option")}</p>{opts}
      <p class="note">{e("If none of these options suit your needs please feel free to discuss, and we'll do our best to find suitable accommodations" if not fr else "Si aucune de ces options ne vous convient, parlons-en : nous ferons de notre mieux pour trouver un hébergement adapté")}</p><p class="champ__erreur" aria-live="polite"></p>
    </fieldset>
    <div class="champ"><label for="i-allergies">{e("Any Allergies, Medical Constraints, Food Restrictions? (NB, the village is located at 1100 meters/3500', and we may be going up to 1600meters/5400' for an activity.)" if not fr else "Allergies, contraintes médicales, régime alimentaire ? (NB : le village est à 1 100 mètres d'altitude, et nous pourrons monter jusqu'à 1 600 mètres pour une activité.)")}</label><textarea id="i-allergies" name="allergies" rows="4"></textarea></div>
    <div class="champ champ--case"><label><input type="checkbox" name="consentement_sante" data-sante> <span>[{e("Consent wording for health information: to come from Lisa" if not fr else "Texte de consentement pour les informations de santé : à venir de Lisa")}]</span></label><p class="note">{e("Required if you write anything in the box above: allergies and medical information are health data." if not fr else "Obligatoire si vous remplissez la case ci-dessus : allergies et informations médicales sont des données de santé.")}</p><p class="champ__erreur" aria-live="polite"></p></div>
    <fieldset class="champ"><legend>{e("Self assessed creative level:" if not fr else "Votre niveau créatif, selon vous :")}</legend>{niveaux}</fieldset>
    <fieldset class="champ"><legend>{e("Optional Interests/Activities" if not fr else "Activités facultatives")}</legend>
      <p class="note">{e("If there is a critical mass, I will do my best to arrange group alternatives to open guided studio times. (Costs not included) Please pick your TOP 3" if not fr else "S'il y a assez d'intéressés, je ferai de mon mieux pour organiser ces activités en groupe, en alternative aux temps d'atelier encadré. (Frais non compris) Choisissez vos 3 préférées")}</p>{activites}</fieldset>
    <div class="inscription__acompte"><p class="surtitre"><span>{e("Deposit" if not fr else "Acompte")}</span></p><p><strong>{e("Save my space with this deposit" if not fr else "Je réserve ma place avec cet acompte")}</strong> <span class="inscription__montant">{e(prix_txt(200, lang))}</span></p></div>
    <div class="champ champ--case"><label><input type="checkbox" name="conditions" required> <span>{e("I have read and agree with the terms and conditions." if not fr else "J'ai lu et j'accepte les conditions.")}</span></label>
      <p class="note">{e("Please do take the time to read the payment schedule and cancellation policy," if not fr else "Prenez le temps de lire l'échéancier de paiement et les conditions d'annulation,")} <a href="{lien(lang, "conditions", prof)}">{e("by clicking this link." if not fr else "en suivant ce lien.")}</a> {e("And don't hesitate to ask me questions." if not fr else "Et n'hésitez pas à me poser vos questions.")}</p><p class="champ__erreur" aria-live="polite"></p></div>
    <p class="formulaire__erreurs" hidden role="alert">{e("Please check the highlighted fields." if not fr else "Vérifiez les champs signalés.")}</p>
    <p class="note">{e("Mock-up: nothing is sent or charged. On the final site, this form sends your answers to the same Wix form as today, then takes the €200 deposit." if not fr else "Maquette : rien n'est envoyé ni débité. Sur le site final, ce formulaire envoie vos réponses au même formulaire Wix qu'aujourd'hui, puis encaisse l'acompte de 200 €.")}</p>
    <button class="bouton aimant" type="submit"><span>{e("Submit" if not fr else "Envoyer")}</span></button>
  </form>
  <div class="formulaire__merci inscription__merci" hidden tabindex="-1">
    <h2>{e("Thank you, your place is on its way!" if not fr else "Merci, votre place est en route !")}</h2>
    <p>{e("We have received your registration. You'll receive a confirmation email with your deposit receipt and the next steps." if not fr else "Nous avons bien reçu votre inscription. Vous allez recevoir un courriel de confirmation avec le reçu de votre acompte et les prochaines étapes.")}</p>
    <p class="note">{e("Confirmation wording to be confirmed by Lisa." if not fr else "Formulation à confirmer par Lisa.")}</p>
  </div>
</section>'''
    ecrire(chemin, page(lang, page_cle, chemin, titre_f, corps, href_autre(lang, page_cle, prof), {}, "page-inscription"))


# ---------------------------------------------------------------- recherche sur tout le site (index généré, sans service externe)
def index_recherche(lang, prof=0):
    t = C.T[lang]
    items = []
    for cle in C.PAGES:
        if cle in ("horaires", "recherche", "accueil") or cle.startswith("inscription_"):
            continue
        seo = SEO.PAGES.get(cle) or {}
        nom = t["nav"].get(cle) or cle
        if cle in RETRAITES:
            nom = nom_retraite(RETRAITES[cle], lang)
        desc = (seo.get("description") or {}).get(lang) if seo.get("description") else ""
        items.append({"t": nom, "d": desc or "", "u": lien(lang, cle, prof), "g": "page"})
    for sid in ORDRE:
        items.append({"t": SERIES[sid]["titre"][lang], "d": SERIES[sid]["texte"][lang][:160], "u": lien_salle(lang, sid, prof), "g": "serie"})
        for oid in LISTES[sid]:
            o = OEUVRES[oid]
            if o["titre"]:
                items.append({"t": titre(o, lang), "d": faits_courts(o, lang), "u": lien_salle(lang, sid, prof) + "?oeuvre=" + oid, "g": "oeuvre"})
    for x in C.PRESSE:
        items.append({"t": x["titre"], "d": x["media"] + " · " + (L(lang, x["date"]) or ""), "u": lien(lang, "presse", prof), "g": "presse"})
    return items


def page_recherche(lang):
    t = C.T[lang]
    fr = lang == "fr"
    chemin = fichier(lang, "recherche")
    prof = prof_de(chemin)
    (SITE / "assets" / "data" / f"recherche-{lang}.json").write_text(json.dumps(index_recherche(lang, prof), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    corps = f'''
<section class="recherche" data-strate="{e(t["nav"]["recherche"])}">
  {surtitre("Works, pages, press" if not fr else "Œuvres, pages, presse")}
  <h1 class="bandeau__titre">{lettres(t["nav"]["recherche"])}</h1>
  <form class="recherche__form" role="search" data-recherche action="">
    <label class="vh" for="q">{e(t["nav"]["recherche"])}</label>
    <input id="q" name="q" type="search" autocomplete="off" placeholder="{e("A work, a series, a retreat…" if not fr else "Une œuvre, une série, une retraite…")}">
    <button class="bouton" type="submit"><span>{e(t["nav"]["recherche"])}</span></button>
  </form>
  <p class="recherche__etat" role="status" aria-live="polite"></p>
  <ol class="recherche__resultats" data-recherche-resultats></ol>
</section>'''
    ecrire(chemin, page(lang, "recherche", chemin, t["nav"]["recherche"], corps, href_autre(lang, "recherche", prof), {"recherche": f"assets/data/recherche-{lang}.json"}, "page-recherche"))


# ================================================================ v5 · plan du site, robots, llms.txt (GEO), redirections de l'ancien site
def pages_publiques():
    """(cle, salle) de chaque page publique, dans les deux langues."""
    cles = [k for k in C.PAGES if k not in ("horaires",)]
    out = [(k, None) for k in cles]
    out += [("salle", sid) for sid in ORDRE]
    return out


def ecrire_plan_du_site():
    if MODE != "propres":
        return
    lignes = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for cle, sid in pages_publiques():
        u = {lg: url_page(lg, cle, sid) for lg in LANGS}
        for lg in LANGS:
            lignes.append(f"  <url><loc>{u[lg]}</loc><lastmod>{AUJ.isoformat()}</lastmod>"
                          f'<xhtml:link rel="alternate" hreflang="en" href="{u["en"]}"/>'
                          f'<xhtml:link rel="alternate" hreflang="fr" href="{u["fr"]}"/>'
                          f'<xhtml:link rel="alternate" hreflang="x-default" href="{u["en"]}"/></url>')
    lignes.append("</urlset>")
    (SITE / "sitemap.xml").write_text("\n".join(lignes) + "\n", encoding="utf-8")


def ecrire_llms():
    """llms.txt : résumé factuel pour les moteurs de réponse (ChatGPT, Perplexity, Gemini, Claude…)."""
    t = C.T["en"]
    lignes_h = "; ".join(f"{j}: {h}" for j, h in HOR.lignes(HEURES, "en"))
    retraites = "\n".join(f'- [{RETRAITES[k]["titre"]}]({url_page("en", k)}): {L("en", RETRAITES[k]["accroche"])}. {L("en", RETRAITES[k]["dates"])}, La Clusaz. {L("en", RETRAITES[k]["prix"])}, depending on options indicated on the booking form.'
                          for k in RETRAITES_ORDRE)
    pages_en = [("oeuvres", "Works: A Record of Time, then the Archive of earlier series"), ("artiste", "Artist statement, long bio and short bio"),
                ("studio", "Studio notes: the story behind A Record of Time"), ("parcours", "Selected CV"), ("presse", "Press"),
                ("espace", "Espace Créa-Tea-Vité: gallery, tea room and studio"), ("salon_the", "Boutique & Tea Room: visit in person, tea menu, hours, map"),
                ("cosessions", "Co-Creating Sessions: open studio with guidance, €30"), ("cours_prives", "Bespoke courses and workshops for individuals, families, groups, teams and event planners"),
                ("evenements", "Gather at the Espace: private venue hire"), ("expositions", "Exhibitions & Events: La Gravité de la Grâce, December 2026 – April 2027"),
                ("retraites", "Painting retreats 2027"), ("conditions", "Retreat payment schedule and cancellation policy"), ("boutique", "Available Works: originals, prints, collectors' editions"),
                ("contact", "Contact")]
    pages_fr = [("accueil", "Accueil"), ("oeuvres", "Œuvres"), ("artiste", "L'artiste"), ("espace", "L'Espace Créa-Tea-Vité"), ("retraites", "Retraites 2027"), ("contact", "Contact")]
    c = C.COORD
    txt = f"""# Lisa Cirenza

> {C.POSITION["ligne"]["en"]} She founded Espace Créa-Tea-Vité, a gallery, tea room and studio in La Clusaz (Haute-Savoie, France), where she teaches and hosts painting retreats. English is the official language of this site; a French version lives under /fr.

## About

{C.BIO_COURTE["en"]}

- Current series: A Record of Time. Earlier series (London Underground, refugees, digital work, Cuba) are in the Archive.
- Statement, in her words: "{C.POSITION["citation"]["en"]}"
- She was a field researcher on the Juneau Icefield, not a glaciologist.
- Venice: Personal Structures, European Cultural Centre, Palazzo Mora, during the 59th Venice Biennale.

## Espace Créa-Tea-Vité

- Address: {c["rue"]}, {c["ville"]}, France
- Opening hours: {lignes_h} (exceptional closures are announced on every page of the site)
- Phone and WhatsApp: {c["tel"]} · Email: {c["courriel_espace"]}
- Instagram: {c["instagram_espace"]}

## Retreats 2027 (all based in La Clusaz)

{retraites}

## Pages

{chr(10).join(f"- [{t['nav'].get(k, k)}]({url_page('en', k)}): {d}" for k, d in pages_en)}

## Français

{chr(10).join(f"- [{d}]({url_page('fr', k)})" for k, d in pages_fr)}

## Contact

- Artist and works (Lisa Cirenza Fine Art): {c["courriel"]}
- Espace, sessions, courses, retreats and events (Espace Créa-Tea-Vité, SAS Atelier Truffle): {c["courriel_espace"]}
"""
    (SITE / "llms.txt").write_text(txt, encoding="utf-8")


def redirections():
    """Anciennes adresses de la maquette, puis celles de l'ancien site Wix (anglais et /fr), précises d'abord, motifs ensuite."""
    def dest(lg, cible):
        return lien_salle(lg, cible[1], 0) if isinstance(cible, tuple) else lien(lg, cible, 0)
    r = []
    for ancien, cible in SEO.ANCIENNES_MAQUETTE.items():
        r.append({"source": ancien, "destination": dest("en", cible), "permanent": False})
    for ancien, cible in SEO.ANCIENNES_MAQUETTE_FR.items():
        r.append({"source": ancien, "destination": dest("fr", cible), "permanent": False})
    exacts = [(a, c) for a, c in SEO.ANCIEN_SITE.items() if a not in SEO.MOTIFS]
    motifs = [(a, SEO.ANCIEN_SITE[a]) for a in SEO.MOTIFS]
    for ancien, cible in exacts + motifs:
        for lg, pre in (("en", ""), ("fr", "/fr")):
            d = dest(lg, cible)
            if pre + ancien != d:  # ex. /press existe déjà sous le même nom
                r.append({"source": pre + ancien, "destination": d, "permanent": False})
    return r

# ================================================================ tout
for lang in LANGS:
    page_accueil(lang)
    page_oeuvres(lang)
    for sid in ORDRE:
        page_salle(lang, sid)
    page_artiste(lang)
    page_parcours(lang)
    page_presse(lang)
    page_espace(lang)
    page_evenements(lang)
    page_retraites(lang)
    page_retraite(lang, "pip")
    page_retraite(lang, "encaustics")
    page_boutique(lang)
    page_cours_prives(lang)
    page_studio(lang)
    page_contact(lang)
    page_horaires(lang)
    page_salon_the(lang)
    page_cosessions(lang)
    page_expositions(lang)
    page_conditions(lang)
    for _r in RETRAITES_ORDRE:
        page_inscription(lang, _r)
    page_recherche(lang)
    donnees_js(lang)
page_404()
# Maquette : pas d'indexation (le site actuel garde son référencement), en-têtes de sécurité de base,
# aucune règle Cache-Control (Vercel revérifie chaque fichier), jamais X-Frame-Options (affichage dans Wix).
(SITE / "vercel.json").write_text(json.dumps({
    "cleanUrls": True, "trailingSlash": False,
    "redirects": redirections(),
    "headers": [{"source": "/(.*)", "headers": [{"key": "X-Robots-Tag", "value": "noindex, nofollow"},
                                                {"key": "X-Content-Type-Options", "value": "nosniff"},
                                                {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"}]}],
}, indent=2) + "\n")
(SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /manage/\nDisallow: /fr/gestion/\n\nSitemap: {SITE_URL}/sitemap.xml\n")
ecrire_plan_du_site()
ecrire_llms()
print("pages générées, liens :", MODE, "· œuvres :", len(OEUVRES))
