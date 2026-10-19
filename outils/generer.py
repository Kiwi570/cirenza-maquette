"""Génère les pages HTML (anglais à la racine, français sous fr/) et les données du site Lisa Cirenza.

Usage : python3 -I outils/generer.py <racine-site> [--liens html|propres] [--apercu]
  propres : liens absolus sans .html (Vercel, cleanUrls) — par défaut
  html    : liens relatifs avec .html (aperçu publié, ouverture locale)
"""
import datetime as DT
import html as H
import json
import math
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
import catalogue as CAT  # noqa: E402
import contenu as C  # noqa: E402
import retraites as R  # noqa: E402

SITE = Path(sys.argv[1]).resolve()
MODE = sys.argv[sys.argv.index("--liens") + 1] if "--liens" in sys.argv else "propres"
APERCU = "--apercu" in sys.argv
MED = json.loads((ICI / "medias.json").read_text())
VERSION = "2"
AUJ = DT.date(2026, 10, 19)
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
        "dims": o.get("dims"), "hcm": hcm, "lcm": lcm,
        "technique": o.get("technique"), "edition": o.get("edition"), "annee": o.get("annee"),
        "statut": o.get("statut"), "texte": o.get("texte"),
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
    return f'<span class="etiquette">{e(t["prix_demande"])}</span>'


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
            f'<span class="cartel__faits">{e(faits_courts(o, lang))}</span>{etat(o, lang)}</{balise}>')


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
def entete(lang, cle, prof, autre_href):
    t = C.T[lang]
    autre = "fr" if lang == "en" else "en"
    nav = ""
    for k in ("oeuvres", "artiste", "espace", "retraites", "contact"):
        cur = ' aria-current="page"' if k == cle or (k == "oeuvres" and cle == "salle") or (k == "retraites" and cle in ("pip", "molten")) or (k == "artiste" and cle in ("parcours", "presse")) or (k == "espace" and cle in ("cours", "evenements")) else ""
        nav += f'<li><a href="{lien(lang, k, prof)}"{cur}>{e(t["nav"][k])}</a></li>'

    def groupe(nom, items):
        lis = "".join(f'<li><a href="{h}"><span data-lettres>{e(x)}</span>{f"<small>{e(s)}</small>" if s else ""}</a></li>' for x, h, s in items)
        return f'<div class="menu__strate"><p class="menu__groupe">{e(nom)}</p><ul>{lis}</ul></div>'
    g_oeuvres = [(t["nav"]["oeuvres"], lien(lang, "oeuvres", prof), None)] + [(SERIES[s]["titre"][lang], lien_salle(lang, s, prof), None) for s in ORDRE]
    g_artiste = [(t["nav"]["artiste"], lien(lang, "artiste", prof), None), (t["nav"]["parcours"], lien(lang, "parcours", prof), None), (t["nav"]["presse"], lien(lang, "presse", prof), None)]
    g_espace = [(t["nav"]["espace"], lien(lang, "espace", prof), None), (t["nav"]["cours"], lien(lang, "cours", prof), None), (t["nav"]["evenements"], lien(lang, "evenements", prof), None), (t["nav"]["contact"], lien(lang, "contact", prof), None)]
    g_retraites = [(t["nav"]["retraites"], lien(lang, "retraites", prof), None), ("Painting in Paradise", lien(lang, "pip", prof), L(lang, R.PIP["dates"])), ("Molten Magic", lien(lang, "molten", prof), L(lang, R.MOLTEN["dates"]))]
    menu = (f'<div class="menu" id="menu" hidden><nav class="menu__grille" aria-label="{"Site" if lang == "en" else "Site"}">'
            f'{groupe(t["groupes_menu"]["oeuvres"], g_oeuvres)}{groupe(t["groupes_menu"]["artiste"], g_artiste)}{groupe(t["groupes_menu"]["espace"], g_espace)}{groupe(t["groupes_menu"]["retraites"], g_retraites)}</nav>'
            f'<div class="menu__bas">{statut(lang)}<p>{e(C.COORD["rue"])}, {e(C.COORD["ville"])}</p><a href="{autre_href}" hreflang="{autre}" lang="{autre}">{e(t["langue_autre"])}</a></div></div>')
    return f'''<header class="entete" data-entete>
  <a class="entete__marque" href="{lien(lang, "accueil", prof)}"><span class="signature" role="img" aria-label="Lisa Cirenza"></span><span class="vh"> – {e(t["nav"]["accueil"])}</span></a>
  <nav class="entete__nav" aria-label="{"Main navigation" if lang == "en" else "Navigation principale"}"><ul>{nav}</ul></nav>
  {statut(lang, "entete__statut")}
  <a class="entete__langue" href="{autre_href}" hreflang="{autre}" lang="{autre}"><span class="vh">{e(t["langue_autre"])}</span><span aria-hidden="true">{t["langue_autre_court"]}</span></a>
  <button class="entete__menu" type="button" aria-expanded="false" aria-controls="menu"><span class="entete__menu-texte">{e(t["menu"])}</span><span class="entete__menu-traits" aria-hidden="true"><i></i><i></i><i></i></span></button>
</header>
{menu}'''


def pied(lang, prof, autre_href):
    t = C.T[lang]
    c = C.COORD
    autre = "fr" if lang == "en" else "en"
    hor = "".join(f"<div><dt>{e(j)}</dt><dd>{e(h)}</dd></div>" for j, h in t["horaires_lignes"])
    plan = "".join(f'<li><a href="{lien(lang, k, prof)}">{e(t["nav"][k])}</a></li>' for k in ("accueil", "oeuvres", "artiste", "parcours", "presse", "espace", "cours", "evenements", "retraites", "contact"))
    return f'''<footer class="pied">
  <div class="pied__haut">
    <span class="signature signature--complete" role="img" aria-label="Lisa Cirenza"></span>
    <p class="pied__citation">{e(C.VEHICULE[lang][0])}</p>
  </div>
  <div class="pied__colonnes">
    <section><h2>{e(c["espace"])}</h2><address>{e(c["atelier"])}<br>{e(c["rue"])}<br>{e(c["ville"])}, {e(c["pays"][lang])}</address>{statut(lang)}</section>
    <section><h2>{e(t["horaires"])}</h2><dl class="horaires">{hor}</dl></section>
    <section><h2>{"Write, call" if lang == "en" else "Écrire, appeler"}</h2><p><a class="courriel" href="mailto:{c["courriel"]}">{c["courriel"]}</a></p><p><a href="tel:{c["tel_brut"]}">{e(c["tel"])}</a> · <a href="https://wa.me/{c["tel_brut"].lstrip("+")}">WhatsApp</a></p>
      <p class="pied__reseaux"><a href="{c["instagram"]}">Instagram</a> · <a href="{c["linkedin"]}">LinkedIn</a> · <a href="{c["facebook"]}">Facebook</a></p></section>
    <section><h2>{e(t["plan"])}</h2><ul class="pied__plan">{plan}</ul></section>
  </div>
  <p class="pied__bas"><span>{e(t["pied_droits"])} · SIRET {e(c["siret_atelier"])}</span><span>{e(c["espace"])} · SIRET {e(c["siret_espace"])}</span><span>{e(t["traduction"])}</span><span>{e(t["pied_maquette"])}</span><a href="{autre_href}" hreflang="{autre}" lang="{autre}">{e(t["langue_autre"])}</a></p>
</footer>'''


def polices():
    regles = [
        ("LC Fraunces", "fraunces.woff", "normal", "300 800"),
        ("LC Fraunces", "fraunces-italique.woff", "italic", "300 800"),
        ("LC Plex Mono", "plex-mono-regular.woff", "normal", "400"),
        ("LC Plex Mono", "plex-mono-medium.woff", "normal", "500"),
    ]
    return "<style>" + "".join(f'@font-face{{font-family:"{f}";src:url("{prefixe(0) if MODE == "propres" else "__P__"}assets/polices/{n}") format("woff");font-style:{s};font-weight:{w};font-display:swap}}' for f, n, s, w in regles) + "</style>"


def page(lang, cle, chemin, titre_page, corps, autre_chemin, donnees_page=None, classe_corps="", image_og=None, preload=None):
    t = C.T[lang]
    prof = prof_de(chemin)
    autre = "fr" if lang == "en" else "en"
    autre_href = autre_chemin
    titre_complet = f"{titre_page} · Lisa Cirenza" if cle != "accueil" else f"Lisa Cirenza · {t['metier']}"
    og = image_og or asset(prof, "img/oeuvres/dream-big-1600.webp")
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
<meta name="description" content="{e(t["description"])}">
<meta name="theme-color" content="#f2efe8">
<link rel="alternate" hreflang="{autre}" href="{autre_href}">
<link rel="icon" type="image/png" sizes="32x32" href="{asset(prof, "img/icones/icone-32.png")}">
<link rel="icon" type="image/png" sizes="192x192" href="{asset(prof, "img/icones/icone-192.png")}">
<link rel="apple-touch-icon" href="{asset(prof, "img/icones/apple-touch-icon.png")}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(titre_complet)}">
<meta property="og:description" content="{e(t["description"])}">
<meta property="og:image" content="{og}">
{pre}
{pol}
<link rel="stylesheet" href="{asset(prof, "css/site.css")}?v={VERSION}">
<script>(function(d){{d.classList.remove("no-js");d.classList.add("js");try{{if(matchMedia("(prefers-reduced-motion: reduce)").matches)d.classList.add("mouvement-reduit")}}catch(x){{}}}})(document.documentElement);</script>
{extra}
<script defer src="{asset(prof, f"js/donnees-{lang}.js")}?v={VERSION}"></script>
<script defer src="{asset(prof, "js/site.js")}?v={VERSION}"></script>
</head>
<body class="{classe_corps}">
<a class="evitement" href="#contenu">{e(t["aller_contenu"])}</a>
{'<p class="badge-maquette">' + ("Mock-up" if lang == "en" else "Maquette") + '</p>' if APERCU else ""}
<div class="grain" aria-hidden="true"></div>
{entete(lang, cle, prof, autre_href)}
<div class="altimetre" aria-hidden="true"><span class="altimetre__haut">{e(t["altitude"])}</span><span class="altimetre__piste"><i class="altimetre__curseur"></i></span><span class="altimetre__strate"></span></div>
<main id="contenu" tabindex="-1">
{corps}
</main>
{pied(lang, prof, autre_href)}
</body>
</html>
'''


def ecrire(chemin, texte):
    p = SITE / chemin
    p.parent.mkdir(parents=True, exist_ok=True)
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
def colonne(lang, prof, compacte=False):
    t = C.T[lang]
    lis = []
    for i, sid in enumerate(ORDRE):
        s = SERIES[sid]
        ids = [x for x in LISTES[sid]][:4]
        couleurs = [OEUVRES[x]["dominante"] for x in LISTES[sid]][:3]
        while len(couleurs) < 3:
            couleurs.append(couleurs[-1])
        periode = L(lang, s["periode"]) if s.get("periode") else ""
        vign = "".join(f'<span class="strate__mini" style="--ratio:{OEUVRES[x]["ratio"]}"><img src="{asset(prof, f"img/oeuvres/{x}-640.webp")}" alt="" loading="lazy" decoding="async" width="{OEUVRES[x]["t"]["640"][0]}" height="{OEUVRES[x]["t"]["640"][1]}"></span>' for x in ids)
        lis.append(f'''<li class="strate" style="--c1:{couleurs[0]};--c2:{couleurs[1]};--c3:{couleurs[2]};--i:{i};--bg:{-(i * 61) % 400}px">
  <a class="strate__lien" href="{lien_salle(lang, sid, prof)}" data-curseur="{e(t["voir"])}">
    <span class="strate__n">{i + 1:02d}</span>
    <span class="strate__titre">{e(s["titre"][lang])}</span>
    <span class="strate__meta">{e(n_oeuvres(len(LISTES[sid]), lang))}{(" · " + e(periode)) if periode else ""}</span>
    <span class="strate__minis" aria-hidden="true">{vign}</span>
  </a>
</li>''')
    return f'<ol class="colonne{" colonne--compacte" if compacte else ""}" data-colonne>{"".join(lis)}</ol>'


def page_accueil(lang):
    t = C.T[lang]
    chemin = fichier(lang, "accueil")
    prof = prof_de(chemin)
    hero = "dream-big"
    o = OEUVRES[hero]
    autre = href_autre(lang, "accueil", prof)
    sizes_hero = "(max-width: 900px) 70vw, 34vw"
    m = C.MANIFESTE[lang]
    pres = C.PRESSE
    cartes_presse = "".join(
        f'<li class="presse-carte" data-incline><a href="{p["url"] or lien(lang, "presse", prof)}"{" rel=\"noopener\"" if p["url"] else ""}>'
        f'<span class="presse-carte__img">{img_photo(prof, p["image"], "", "(max-width: 700px) 60vw, 20vw")}</span>'
        f'<span class="presse-carte__media">{e(p["media"])}</span><span class="presse-carte__titre">{e(p["titre"])}</span>'
        f'<span class="presse-carte__date">{e(L(lang, p["date"]) or "")}</span></a></li>' for p in pres[:6])
    wdib = OEUVRES["where-do-i-begin"]
    corps = f'''
<section class="ouverture" data-ouverture data-strate="{e("Lisa Cirenza")}">
  <canvas class="ouverture__gl" aria-hidden="true"></canvas>
  <div class="ouverture__strates" aria-hidden="true">{"".join(f'<i style="--k:{k}"></i>' for k in range(9))}</div>
  <div class="ouverture__grille">
    <div class="ouverture__texte">
      <p class="surtitre" data-apparait><span class="surtitre__n">1 040 m</span><span>{e("Atelier & Espace Créa-Tea-Vité · La Clusaz")}</span></p>
      <h1 class="ouverture__titre" id="titre-accueil"><span class="ouverture__prenom" data-lettres data-lettres-auto>Lisa</span> <span class="ouverture__nom" data-lettres data-lettres-auto>Cirenza</span></h1>
      <p class="ouverture__metier" data-apparait>{e(t["metier"])}</p>
      <p class="ouverture__actions" data-apparait>{bouton(t["nav"]["oeuvres"], lien(lang, "oeuvres", prof))}{bouton(t["nav"]["retraites"] + " 2027", lien(lang, "retraites", prof), "bouton bouton--ligne")}</p>
    </div>
    <figure class="ouverture__oeuvre" data-apparait>
      {bouton_oeuvre(prof, hero, lang, "beneath-the-surface", sizes_hero, "ouverture__toile", "eager", True)}
      <figcaption class="cartel cartel--clair"><span class="cartel__titre">{e(o["titre"])}</span><span class="cartel__faits">{e(faits_courts(o, lang))}</span></figcaption>
    </figure>
  </div>
  <button class="ouverture__passer" type="button" hidden>{"Skip" if lang == "en" else "Passer"}</button>
  <p class="ouverture__defiler" data-apparait aria-hidden="true"><span>{"Scroll down through the strata" if lang == "en" else "Descendez à travers les strates"}</span><i></i></p>
</section>

<section class="manifeste" data-strate="{e("Manifesto" if lang == "en" else "Manifeste")}">
  <div class="manifeste__texte">
    {surtitre("Manifesto" if lang == "en" else "Manifeste", 1)}
    <p class="manifeste__lignes" data-mots>{e(" ".join(m))}</p>
  </div>
  <div class="manifeste__fossiles">
    <figure class="manifeste__f manifeste__f--a" data-parallaxe="-0.14" data-revele><span class="fossile__cadre">{img_photo(prof, "artiste/lisa-a-4-ans", "Lisa Cirenza, four years old" if lang == "en" else "Lisa Cirenza à 4 ans", "(max-width: 700px) 46vw, 20vw")}</span><figcaption>{e(BIO_LEGENDE[lang])}</figcaption></figure>
    <figure class="manifeste__f manifeste__f--b" data-parallaxe="0.1" data-revele><span class="fossile__cadre">{img_photo(prof, "artiste/lisa-peint-grand-format-bleu", "Lisa Cirenza painting a large blue work" if lang == "en" else "Lisa Cirenza peignant un grand format bleu", "(max-width: 700px) 60vw, 30vw")}</span></figure>
  </div>
  <blockquote class="manifeste__nature" data-apparait><p>{e(C.NATURE[lang])}</p></blockquote>
</section>

<section class="geologie" data-strate="{e(C.DEMARCHE["titre"][lang])}">
  <div class="geologie__fond" aria-hidden="true">{img_decor(prof, "roche-strates-16x9", "", "100vw")}</div>
  <div class="geologie__grille">
    <div class="geologie__texte">
      {surtitre(C.DEMARCHE["titre"][lang], 2)}
      <h2 class="titre-section">{lettres("Beneath the surface" if lang == "en" else "Sous la surface")}</h2>
      <p data-apparait>{e(C.DEMARCHE["paragraphes"][lang][2])}</p>
      <p data-apparait>{bouton("The artist's statement" if lang == "en" else "La démarche de l'artiste", lien(lang, "artiste", prof, "#demarche"), "bouton bouton--ligne")}</p>
    </div>
    <div class="grattage" data-grattage style="--ratio:{OEUVRES["a-moment-in-time"]["ratio"]}">
      <figure class="grattage__oeuvre">
        {bouton_oeuvre(prof, "a-moment-in-time", lang, "layered-moments", "(max-width: 800px) 86vw, 40vw")}
        <canvas class="grattage__cire" aria-hidden="true"></canvas>
      </figure>
      <p class="grattage__aide"><span>{e(t["gratter"])}</span> <button type="button" class="lien-bouton" data-tout-reveler>{e(t["tout_reveler"])}</button></p>
      {cartel(OEUVRES["a-moment-in-time"], lang, "p")}
    </div>
  </div>
</section>

<section class="strates-accueil" data-strate="{e("The strata" if lang == "en" else "Les strates")}">
  <div class="strates-accueil__tete">
    {surtitre("The series, layer by layer" if lang == "en" else "Les séries, couche après couche", 3)}
    <h2 class="titre-section">{lettres("Eight strata" if lang == "en" else "Huit strates")}</h2>
    <p data-apparait>{e("From the London Underground to Havana, from iPad drawings to hot wax: each series is a layer of the same search for what lies beneath the surface." if lang == "en" else "Du métro de Londres à La Havane, du dessin sur iPad à la cire chaude : chaque série est une couche de la même recherche de ce qui se cache sous la surface.")}</p>
  </div>
  {colonne(lang, prof)}
</section>

<section class="tirage" data-strate="Where Do I Begin?">
  <div class="tirage__mur" data-mur-scene style="--ratio:{wdib["ratio"]}">
    {img_decor(prof, "voir-au-mur-chalet-16x9", "", "(max-width: 900px) 100vw, 60vw", "tirage__decor")}
    <span class="tirage__oeuvre" data-revele>{bouton_oeuvre(prof, "where-do-i-begin", lang, "hors-serie", "(max-width: 900px) 30vw, 14vw")}</span>
  </div>
  <div class="tirage__texte">
    {surtitre("Limited edition" if lang == "en" else "Édition limitée", 4)}
    <h2 class="titre-section">{lettres("Where Do I Begin?")}</h2>
    <p data-apparait>{e(wdib["edition"][lang])}. {e(t["prix_demande"])}.</p>
    <p class="note" data-apparait>{e(t["image_a_confirmer"])}{" — the image shown on the home page of the current site" if lang == "en" else " : image affichée sur l'accueil du site actuel"}</p>
    <p data-apparait>{bouton(t["demander"], lien(lang, "contact", prof) + "?oeuvre=where-do-i-begin")}</p>
  </div>
</section>

<section class="presse-accueil" data-strate="{e(t["nav"]["presse"])}">
  <div class="presse-accueil__tete">
    {surtitre(t["nav"]["presse"], 5)}
    <blockquote class="citation-ft"><p data-mots>“{e(C.FT_CITATION)}”</p><footer>Financial Times, 2017 · <cite>NYC Contrasts</cite></footer></blockquote>
    {figure_photo(prof, "presse/ft-nyc-contrasts", "NYC Contrasts as reproduced in the Financial Times" if lang == "en" else "NYC Contrasts reproduit dans le Financial Times", "", "fossile presse-accueil__ft", "(max-width: 800px) 70vw, 26vw")}
  </div>
  <ul class="presse-cartes">{cartes_presse}</ul>
  <p class="presse-accueil__tout">{bouton("All the press" if lang == "en" else "Toute la presse", lien(lang, "presse", prof), "bouton bouton--ligne")}</p>
</section>

<section class="espace-accueil" data-strate="Espace Créa-Tea-Vité">
  <div class="espace-accueil__images">
    {figure_photo(prof, "espace/facade-de-nuit", "The Espace Créa-Tea-Vité at night, its windows lit" if lang == "en" else "L'Espace Créa-Tea-Vité de nuit, vitrines allumées", "", "fossile espace-accueil__a", "(max-width: 800px) 92vw, 46vw", ' data-parallaxe="-0.06"')}
    {figure_photo(prof, "espace/table-vue-pistes", "A table by the window facing the ski slopes" if lang == "en" else "Une table à la fenêtre, face aux pistes", "", "fossile espace-accueil__b", "(max-width: 800px) 50vw, 22vw", ' data-parallaxe="0.12"')}
  </div>
  <div class="espace-accueil__texte">
    {surtitre("Gallery · Tea room · Studio" if lang == "en" else "Galerie · Salon de thé · Atelier", 6)}
    <h2 class="titre-section">{lettres("Espace Créa-Tea-Vité")}</h2>
    <p data-apparait>{e(C.ESPACE["intro"][lang])}</p>
    <p class="note" data-apparait>{e(C.ESPACE["ecran"][lang])}</p>
    <div class="vapeur-statut" data-apparait><span class="vapeur" aria-hidden="true"><i></i><i></i><i></i></span>{statut(lang, "statut--grand")}</div>
    <p data-apparait>{bouton(t["nav"]["espace"], lien(lang, "espace", prof))}{bouton(t["nav"]["cours"], lien(lang, "cours", prof), "bouton bouton--ligne")}</p>
  </div>
</section>

<section class="retraites-accueil" data-strate="{e(t["nav"]["retraites"])}">
  <div class="retraites-accueil__tete">
    {surtitre(t["nav"]["retraites"] + " 2027", 7)}
    <h2 class="titre-section">{lettres("Paint in paradise" if lang == "en" else "Peindre au paradis")}</h2>
  </div>
  <div class="retraites-accueil__panorama" data-panorama>{img_photo(prof, "paysages/lac-annecy-talloires-panorama", "Lake Annecy at Talloires, mountains and mist" if lang == "en" else "Le lac d'Annecy à Talloires, montagnes et brume", "100vw")}</div>
  <div class="retraites-cartes">
    {carte_retraite(lang, prof, R.PIP, "pip", "retraites/diner-coucher-de-soleil-parapentes")}
    {carte_retraite(lang, prof, R.MOLTEN, "molten", "retraites/atelier-cire-en-groupe")}
  </div>
</section>

<section class="vehicule" data-strate="{e("Art is my vehicle" if lang == "en" else "Véhicule")}">
  {figure_photo(prof, "artiste/lisa-peint-au-chevalet", "Lisa Cirenza painting at her easel" if lang == "en" else "Lisa Cirenza peignant au chevalet", "", "fossile vehicule__photo", "(max-width: 800px) 92vw, 44vw")}
  <blockquote class="vehicule__citation"><p class="vehicule__grand">{lettres(C.VEHICULE[lang][0])}</p><p data-apparait>{e(C.VEHICULE[lang][1])}</p><footer>— Lisa Cirenza</footer></blockquote>
</section>
{lettre_info(lang, prof)}
'''
    sizes = sizes_hero
    pre = (asset(prof, f"img/oeuvres/{hero}-1600.webp"), srcset_oeuvre(prof, hero), sizes)
    ecrire(chemin, page(lang, "accueil", chemin, t["metier"], corps, autre, {"accueil": True}, "page-accueil", preload=pre))


BIO_LEGENDE = {"en": "Lisa, aged four", "fr": "Lisa à 4 ans"}


def carte_retraite(lang, prof, r, cle, photo):
    t = C.T[lang]
    bientot = f'<span class="etiquette etiquette--cours">{e(L(lang, r["bientot"]))}</span>' if r.get("bientot") else ""
    return f'''<article class="carte-retraite" data-incline>
  <a href="{lien(lang, cle, prof)}">
    <span class="carte-retraite__img">{img_photo(prof, photo, "", "(max-width: 800px) 92vw, 40vw")}</span>
    <span class="carte-retraite__haut">{compte(lang, r["debut"])}{bientot}</span>
    <span class="carte-retraite__titre">{e(r["titre"])}</span>
    <span class="carte-retraite__dates">{e(L(lang, r["dates"]))} · {e(L(lang, r["lieu"]))}</span>
    <span class="carte-retraite__prix">{e(L(lang, r["prix"]))}</span>
  </a>
</article>'''


def lettre_info(lang, prof):
    t = C.T[lang]
    return f'''<section class="lettre" data-strate="{e("Newsletter" if lang == "en" else "Lettre d'information")}">
  <div class="lettre__fond" aria-hidden="true">{img_decor(prof, "village-nuit-etoiles-16x9", "", "100vw")}</div>
  <div class="lettre__contenu">
    <h2 class="titre-section">{lettres("Musings, Invites, and Updates" if lang == "en" else "Pensées, invitations et nouvelles")}</h2>
    <p data-apparait>{e("Courses, events and future programming: be the first to know." if lang == "en" else "Cours, événements et prochains rendez-vous : soyez informé en premier.")}</p>
    <form class="lettre__form" data-lettre novalidate>
      <label class="vh" for="lettre-email">Email</label>
      <input id="lettre-email" type="email" name="email" autocomplete="email" placeholder="{e("your@email.com" if lang == "en" else "votre@adresse.fr")}" required>
      <button class="bouton aimant" type="submit"><span>{e("Subscribe" if lang == "en" else "S'inscrire")}</span></button>
      <p class="lettre__merci" hidden tabindex="-1">{e("Thanks! (Mock-up: no email is sent.)" if lang == "en" else "Merci ! (Maquette : aucune adresse n'est envoyée.)")}</p>
    </form>
  </div>
</section>'''


# ================================================================ œuvres
def page_oeuvres(lang):
    t = C.T[lang]
    chemin = fichier(lang, "oeuvres")
    prof = prof_de(chemin)
    total = len([o for o in OEUVRES if o != "where-do-i-begin"])
    index = []
    for sid in ORDRE:
        s = SERIES[sid]
        vs = "".join(vignette(prof, oid, lang, sid) for oid in LISTES[sid])
        manque = ""
        if s.get("sans_image"):
            manque = "".join(f'<figure class="vignette vignette--vide"><span class="oeuvre__toile vide"><span>{e("Image to be requested" if lang == "en" else "Visuel à demander")}</span></span><figcaption><span class="cartel__titre">{e(x["titre"])}</span></figcaption></figure>' for x in s["sans_image"])
        index.append(f'<section class="index-serie" data-strate="{e(s["titre"][lang])}"><h3><a href="{lien_salle(lang, sid, prof)}">{e(s["titre"][lang])}</a> <small>{e(n_oeuvres(len(LISTES[sid]), lang))}</small></h3><div class="index-serie__grille">{vs}{manque}</div></section>')
    corps = f'''
{bandeau(lang, prof, None, n_oeuvres(total, lang) + (" · 8 series" if lang == "en" else " · 8 séries"), t["nav"]["oeuvres"], "Encaustic, oils, mixed media on aluminium, iPad drawings and limited edition prints. No prices are listed on the current site: every work is price on request." if lang == "en" else "Encaustique, huile, techniques mixtes sur aluminium, dessins sur iPad et tirages en édition limitée. Aucun prix n'est affiché sur le site actuel : chaque œuvre est sur demande.", f'<div class="bandeau__texture" aria-hidden="true">{img_decor(prof, "strates-cire-16x9", "", "50vw")}</div>', t["nav"]["oeuvres"], "bandeau--oeuvres")}
<section class="oeuvres-colonne" data-strate="{e("Stratigraphic column" if lang == "en" else "Colonne stratigraphique")}">
  {colonne(lang, prof)}
</section>
<section class="index-oeuvres" data-strate="{e("Index" if lang == "en" else "Index")}">
  <div class="index-oeuvres__tete">{surtitre("Every work" if lang == "en" else "Toutes les œuvres")}<h2 class="titre-section">{lettres("Index")}</h2></div>
  {"".join(index)}
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
    decor = {"london-tube": "metro-wagon-vide-16x9", "connections-and-constructions": "chantier-crepuscule-16x9"}.get(sid)
    if decor:
        contexte = figure_decor(prof, decor, "", "", "fossile salle__contexte salle__contexte--large", "(max-width: 800px) 70vw, 34vw") + contexte
    periode = L(lang, s["periode"]) if s.get("periode") else None
    meta = n_oeuvres(len(ids) + len(s.get("sans_image", [])), lang) + (f" · {periode}" if periode else "")
    sous = L(lang, s["sous_titre"]) if s.get("sous_titre") else ""
    valider = f'<p class="note">{e("This page is published on the current site but missing from its menu: to be validated with the artist." if lang == "en" else "Page publiée sur le site actuel mais absente de son menu : à valider avec l'artiste.")}</p>' if s.get("a_valider") else ""
    corps = f'''
<section class="salle" data-piste data-strate="{e(s["titre"][lang])}" style="--fond-salle:{OEUVRES[ids[0]]["fond"]}">
  <div class="salle__collant">
    <div class="salle__piste">
      <div class="salle__entree" data-fond="{OEUVRES[ids[0]]["fond"]}">
        {surtitre(f'{t["strate"]} {idx + 1:02d} · {meta}')}
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
    chemin = fichier(lang, "artiste")
    prof = prof_de(chemin)
    para = C.DEMARCHE["paragraphes"][lang]
    couches = []
    for i, b in enumerate(C.BIO):
        if b.get("decor"):
            img = figure_decor(prof, b["decor"], "", L(lang, b.get("legende", "")), "fossile carottage__img", "(max-width: 800px) 80vw, 30vw")
        else:
            img = figure_photo(prof, b["photo"], L(lang, b.get("legende", "")) or "", L(lang, b.get("legende", "")), "fossile carottage__img", "(max-width: 800px) 80vw, 30vw")
        if b.get("photo2"):
            img += figure_photo(prof, b["photo2"], "Lisa Cirenza painting" if lang == "en" else "Lisa Cirenza peignant", "", "fossile carottage__img carottage__img--2", "(max-width: 800px) 60vw, 20vw")
        couches.append(f'''<li class="carottage__couche" style="--i:{i}" data-strate="{e(b["titre"][lang])}">
  <div class="carottage__repere"><span class="carottage__n">{i + 1:02d}</span></div>
  <div class="carottage__texte"><h3>{e(b["titre"][lang])}</h3><p data-apparait>{e(b["texte"][lang])}</p></div>
  <div class="carottage__images">{img}</div>
</li>''')
    corps = f'''
<section class="bandeau bandeau--artiste" data-strate="{e(t["nav"]["artiste"])}">
  <div class="bandeau__texte">
    {surtitre(t["metier"])}
    <h1 class="bandeau__titre">{lettres("Lisa Cirenza")}</h1>
    <div class="bandeau__intro" data-apparait><p>{e(C.MANIFESTE[lang][0])} {e(C.MANIFESTE[lang][1])} {e(C.MANIFESTE[lang][2])}</p></div>
  </div>
  <div class="bandeau__image bandeau__image--glace" data-glace>{img_photo(prof, "artiste/lisa-portrait-fond-glacier", "Portrait of Lisa Cirenza in front of a glacier painting" if lang == "en" else "Portrait de Lisa Cirenza devant une peinture de glacier", "(max-width: 900px) 80vw, 40vw", "", "eager")}</div>
</section>

<section class="demarche" id="demarche" tabindex="-1" data-strate="{e(C.DEMARCHE["titre"][lang])}">
  <div class="demarche__fond" aria-hidden="true">{img_decor(prof, "roche-strates-16x9", "", "100vw")}</div>
  <div class="demarche__tete">
    {surtitre("Artist statement" if lang == "en" else "Démarche", 1)}
    <h2 class="titre-section">{lettres(C.DEMARCHE["titre"][lang])}</h2>
  </div>
  <p class="demarche__chapo" data-mots>{e(para[0])}</p>
  <div class="demarche__colonnes">
    <div>{"".join(f'<p data-apparait>{e(x)}</p>' for x in para[1:3])}</div>
    <div>{figure_decor(prof, "cire-fondue-1x1", "", "", "fossile demarche__cire", "(max-width: 800px) 80vw, 30vw")}{"".join(f'<p data-apparait>{e(x)}</p>' for x in para[3:])}</div>
  </div>
</section>

<section class="carottage" data-strate="{e("Biography" if lang == "en" else "Biographie")}">
  <div class="carottage__tete">{surtitre("Biography: a core sample" if lang == "en" else "Biographie, en carottage", 2)}<h2 class="titre-section">{lettres("Layers of a life" if lang == "en" else "Les couches d'une vie")}</h2></div>
  <ol class="carottage__liste" data-carottage>{"".join(couches)}</ol>
  <div class="carottage__fin">
    {"".join(f'<p data-apparait>{e(x)}</p>' for x in C.BIO_FIN[lang][:1])}
    <blockquote class="citation"><p>{lettres(C.BIO_FIN[lang][1])}</p><footer>— L. Cirenza</footer></blockquote>
  </div>
</section>

<section class="procede" data-strate="{e("Encaustic" if lang == "en" else "Encaustique")}">
  <div class="procede__texte">
    {surtitre("Process" if lang == "en" else "Le procédé", 3)}
    <h2 class="titre-section">{lettres("Painting with fire" if lang == "en" else "Peindre avec le feu")}</h2>
    <p data-apparait>{e(SERIES["encaustic-and-oils"]["texte"][lang])}</p>
    {"".join(f'<p data-apparait>{e(x)}</p>' for x in C.PROCEDE[lang])}
    <p data-apparait>{bouton("Encaustic and Oils" if lang == "en" else "Encaustique et huiles", lien_salle(lang, "encaustic-and-oils", prof), "bouton bouton--ligne")}</p>
  </div>
  <div class="procede__images">
    {figure_photo(prof, "atelier/chalumeau-encaustique", "A blowtorch flame used for encaustic" if lang == "en" else "La flamme du chalumeau utilisé pour l'encaustique", "Encaustic = painting with fire" if lang == "en" else "Encaustique = peindre avec le feu", "fossile procede__a", "(max-width: 800px) 80vw, 30vw", ' data-parallaxe="-0.08"')}
    {figure_photo(prof, "atelier/melange-resines-pigments-cire", "Lisa mixing resins, pigments and beeswax" if lang == "en" else "Lisa mélange résines, pigments et cire d'abeille", "Mixing resins, pigments and beeswax" if lang == "en" else "Mélange de résines, de pigments et de cire d'abeille", "fossile procede__b", "(max-width: 800px) 60vw, 22vw", ' data-parallaxe="0.1"')}
    {figure_photo(prof, "atelier/table-des-cires", "A table of melted waxes and tools" if lang == "en" else "Une table de cires fondues et d'outils", "", "fossile procede__c", "(max-width: 800px) 60vw, 22vw")}
  </div>
</section>

<section class="passions" data-strate="{e("Other passions" if lang == "en" else "Autres passions")}">
  {figure_photo(prof, "artiste/plongeon-eau-libre", "A swimmer diving into open water" if lang == "en" else "Un plongeon en eau libre", "", "fossile passions__img", "(max-width: 800px) 80vw, 32vw")}
  <div class="passions__texte">{surtitre("Other passions" if lang == "en" else "Autres passions", 4)}<p data-apparait>{e(C.PASSIONS[lang])}</p>
  <p data-apparait>{bouton(t["nav"]["parcours"], lien(lang, "parcours", prof))}{bouton(t["nav"]["presse"], lien(lang, "presse", prof), "bouton bouton--ligne")}</p></div>
</section>'''
    corps = avec_carnet(corps, lang, prof, "artiste")
    ecrire(chemin, page(lang, "artiste", chemin, t["nav"]["artiste"], corps, href_autre(lang, "artiste", prof), {}, "page-artiste"))


# ================================================================ parcours
def page_parcours(lang):
    t = C.T[lang]
    chemin = fichier(lang, "parcours")
    prof = prof_de(chemin)
    annees = sorted({a for a, *_ in C.EXPOSITIONS} | {a for a, *_ in C.CONFERENCES}, reverse=True)
    couches = []
    for i, a in enumerate(annees):
        ex = [x for x in C.EXPOSITIONS if x[0] == a]
        co = [x for x in C.CONFERENCES if x[0] == a]
        lis = "".join(f'<li class="fossile-txt{" fossile-txt--" + x[4] if x[4] else ""}"><strong>{e(x[1])}</strong><span>{e(x[2] if lang == "en" else x[3])}</span></li>' for x in ex)
        lis += "".join(f'<li class="fossile-txt fossile-txt--talk"><strong>{e(x[1])}</strong><span>{e(x[2] if lang == "en" else x[3])}</span></li>' for x in co)
        ph = C.PHOTOS_ANNEES.get(a)
        img = figure_photo(prof, ph, "", "", "fossile couche__img", "(max-width: 800px) 60vw, 18vw") if ph else ""
        couches.append(f'<li class="couche" style="--i:{i}" data-strate="{a}"><p class="couche__annee">{a}</p><ul class="couche__fossiles">{lis}</ul>{img}</li>')
    legende = ("Exhibition" if lang == "en" else "Exposition", "Residency" if lang == "en" else "Résidence", "Solo show" if lang == "en" else "Exposition personnelle", "Talk, workshop, performance" if lang == "en" else "Conférence, atelier, performance")
    corps = f'''
{bandeau(lang, prof, None, "CV highlights" if lang == "en" else "Temps forts du CV", t["nav"]["parcours"], "From Kyoto to Venice, from the Grand Palais to Kathmandu: twelve years of exhibitions, residencies and talks, read like a cliff face. The most recent layer sits on top." if lang == "en" else "De Kyoto à Venise, du Grand Palais à Katmandou : douze ans d'expositions, de résidences et de conférences, à lire comme une falaise. La couche la plus récente est en haut.", figure_photo(prof, "expositions/bermondsey-gallery-vitrine-nuit", "Bermondsey Gallery window at night, London" if lang == "en" else "La vitrine de la Bermondsey Gallery de nuit, à Londres", "Solo show, Bermondsey Gallery, London, 2018" if lang == "en" else "Exposition personnelle, Bermondsey Gallery, Londres, 2018", "fossile", "(max-width: 900px) 80vw, 40vw"), t["nav"]["parcours"])}
<section class="frise" data-strate="{e("Stratigraphy" if lang == "en" else "Stratigraphie")}">
  <ul class="frise__legende" aria-label="{e("Legend" if lang == "en" else "Légende")}"><li class="fossile-txt">{e(legende[0])}</li><li class="fossile-txt fossile-txt--residence">{e(legende[1])}</li><li class="fossile-txt fossile-txt--solo">{e(legende[2])}</li><li class="fossile-txt fossile-txt--talk">{e(legende[3])}</li></ul>
  <ol class="frise__couches" data-frise>{"".join(couches)}</ol>
  <p class="note">{e("Years with no line on the current site (2020, 2021, 2023) are not shown. The 2023 and 2024 PDF CVs list further shows." if lang == "en" else "Les années sans ligne sur le site actuel (2020, 2021, 2023) ne sont pas affichées. Les CV en PDF de 2023 et 2024 citent d'autres expositions.")}</p>
  <p>{bouton("Full CV 2024 (PDF)" if lang == "en" else "CV complet 2024 (PDF)", asset(prof, "docs/cv-2024.pdf"), "bouton bouton--ligne")}</p>
</section>'''
    corps = avec_carnet(corps, lang, prof, "parcours")
    ecrire(chemin, page(lang, "parcours", chemin, t["nav"]["parcours"], corps, href_autre(lang, "parcours", prof), {}, "page-parcours"))


# ================================================================ presse
def page_presse(lang):
    t = C.T[lang]
    chemin = fichier(lang, "presse")
    prof = prof_de(chemin)
    cartes = "".join(
        f'<li class="presse-carte" data-incline><a href="{p["url"] or "#ft"}"{" rel=\"noopener\"" if p["url"] else ""}>'
        f'<span class="presse-carte__img">{img_photo(prof, p["image"], "", "(max-width: 700px) 70vw, 24vw")}</span>'
        f'<span class="presse-carte__media">{e(p["media"])}</span><span class="presse-carte__titre">{e(p["titre"])}</span>'
        f'<span class="presse-carte__date">{e(L(lang, p["date"]) or "")}</span><span class="presse-carte__texte">{e(L(lang, p["texte"]))}</span></a></li>' for p in C.PRESSE)
    videos = "".join(f'<li><a href="{v["url"]}" rel="noopener"><strong>{e(v["titre"])}</strong><span>{e(v["auteur"])} · {e(L(lang, v["date"]))}</span></a></li>' for v in C.VIDEOS)
    corps = f'''
{bandeau(lang, prof, None, "Reviews, interviews, films" if lang == "en" else "Critiques, entretiens, films", t["nav"]["presse"], "From the Financial Times to the BBC, from Maison et Jardin to the App Whisperer podcast." if lang == "en" else "Du Financial Times à la BBC, de Maison et Jardin au podcast The App Whisperer.", figure_photo(prof, "presse/maison-et-jardin-2022", "Maison et Jardin article, May 2022" if lang == "en" else "Article de Maison et Jardin, mai 2022", "", "fossile", "(max-width: 900px) 70vw, 32vw"), t["nav"]["presse"])}
<section class="ft" id="ft" tabindex="-1" data-strate="Financial Times">
  {figure_photo(prof, "presse/financial-times", "Financial Times page with NYC Contrasts" if lang == "en" else "Page du Financial Times avec NYC Contrasts", "", "fossile ft__img", "(max-width: 800px) 80vw, 30vw")}
  <div class="ft__texte">{surtitre("Financial Times · “Best of the Rest”")}<blockquote class="citation-ft"><p data-mots>“{e(C.FT_CITATION)}”</p><footer>{e("October 7th weekend edition, 2017" if lang == "en" else "Édition du week-end du 7 octobre 2017")} · <cite>NYC Contrasts</cite></footer></blockquote>
  <p data-apparait>{e("NYC Contrasts, the print praised by the FT, is in the Beneath the Surface room." if lang == "en" else "NYC Contrasts, le tirage salué par le FT, est dans la salle Beneath the Surface.")}</p>
  <p data-apparait>{bouton("See the work" if lang == "en" else "Voir l'œuvre", lien_salle(lang, "beneath-the-surface", prof) + "?oeuvre=nyc-contrasts", "bouton bouton--ligne")}</p></div>
</section>
<section class="presse-mur" data-strate="{e("Press wall" if lang == "en" else "Revue de presse")}">
  <ul class="presse-cartes presse-cartes--mur">{cartes}</ul>
</section>
<section class="videos" data-strate="{e("Films" if lang == "en" else "Films")}">
  <div>{surtitre("Films")}<ul class="videos__liste">{videos}</ul></div>
  {figure_photo(prof, "atelier/video-encaustic-painting-process", "Lisa Cirenza at work in her encaustic studio" if lang == "en" else "Lisa Cirenza au travail dans son atelier d'encaustique", "", "fossile videos__img", "(max-width: 900px) 70vw, 26vw", ' data-parallaxe="-0.05"')}
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
<section class="offres" data-strate="{e("The space" if lang == "en" else "Le lieu")}">
  <div class="offres__tete">{surtitre("Create, connect, be inspired" if lang == "en" else "Créer, se rencontrer, s'inspirer", 1)}<h2 class="titre-section">{lettres(C.ESPACE["reve"][lang][0])}</h2><p data-apparait>{e(C.ESPACE["reve"][lang][1])}</p></div>
  <ul class="offres__liste">{offres}</ul>
</section>
<section class="carte-boissons" id="carte" tabindex="-1" data-strate="{e("Menu" if lang == "en" else "La carte")}">
  <div class="carte-boissons__image">{figure_decor(prof, "salon-de-the-tasses-4x5", "Two cups, a latte and a hot chocolate, by a snowy window" if lang == "en" else "Deux tasses, un latte et un chocolat chaud, devant une fenêtre enneigée", "Ambience photo" if lang == "en" else "Photo d'ambiance", "fossile", "(max-width: 800px) 80vw, 30vw")}</div>
  <div class="carte-boissons__texte">{surtitre("Tea room" if lang == "en" else "Salon de thé", 2)}<h2 class="titre-section">{lettres("The menu" if lang == "en" else "La carte")}</h2>{carte}<p class="note">{e(C.CARTE_NOTE[lang])}</p></div>
</section>
<section class="boutique" data-strate="{e("Boutique")}">
  {figure_decor(prof, "materiel-art-4x5", "Art supplies: wax blocks, pastels, watercolour pans, brushes and rice paper" if lang == "en" else "Matériel d'art : blocs de cire, pastels, godets d'aquarelle, pinceaux et papier de riz", "Ambience photo" if lang == "en" else "Photo d'ambiance", "fossile boutique__a", "(max-width: 800px) 70vw, 26vw", ' data-parallaxe="-0.08"')}
  <div class="boutique__texte">{surtitre("Boutique", 3)}<h2 class="titre-section">{lettres("Curated materials" if lang == "en" else "Matériel choisi")}</h2><p data-apparait>{e(C.ESPACE["offres"][2]["texte"][lang])}</p></div>
  {figure_photo(prof, "espace/atelier-rangements", "The studio's shelves of materials" if lang == "en" else "Les étagères de matériel de l'atelier", "", "fossile boutique__b", "(max-width: 800px) 70vw, 30vw", ' data-parallaxe="0.08"')}
</section>
<section class="expo" data-expo="{ex["fin"]}" data-strate="{e(ex["titre"])}">
  <div class="expo__tete">{surtitre(("Current exhibition" if lang == "en" else "Exposition en cours"), 4)}<p class="expo__etat"><span class="etiquette" data-expo-etat data-en-cours="{e("On now" if lang == "en" else "En cours")}" data-terminee="{e("Ended" if lang == "en" else "Terminée")}">{e("On now" if lang == "en" else "En cours")}</span> {e(ex["dates"][lang])}</p>
  <h2 class="titre-section">{lettres(ex["titre"])}</h2><p data-apparait>{e(ex["intro"][lang])}</p></div>
  <div class="expo__duo">
    <article>{figure_photo(prof, "exposition-en-cours/bnt-designs-soudure", "BNT Designs welding a steel sphere" if lang == "en" else "BNT Designs soude une sphère d'acier", "", "fossile", "(max-width: 800px) 80vw, 30vw")}<h3>BNT Designs</h3><p data-apparait>{e(ex["bnt"][lang])}</p></article>
    <article>{figure_photo(prof, "exposition-en-cours/collage-cuba", "Three of Lisa Cirenza's Cuba works" if lang == "en" else "Trois œuvres cubaines de Lisa Cirenza", "", "fossile", "(max-width: 800px) 80vw, 30vw")}<h3>Lisa Cirenza</h3><p data-apparait>{e(ex["lisa"][lang])}</p><p>{bouton("The Cuba room" if lang == "en" else "La salle Cuba", lien_salle(lang, "cuba", prof), "bouton bouton--ligne")}</p></article>
  </div>
  {figure_photo(prof, "exposition-en-cours/affiche-vernissage-bnt", "Opening poster for BNT Designs" if lang == "en" else "Affiche du vernissage de BNT Designs", "", "fossile expo__affiche", "(max-width: 800px) 60vw, 20vw")}
</section>
<section class="agenda" data-strate="{e("Calendar" if lang == "en" else "Agenda")}">
  <div class="agenda__corps">{surtitre("Calendar" if lang == "en" else "Agenda", 5)}<h2 class="titre-section">{lettres("Classes & gatherings" if lang == "en" else "Cours et rencontres")}</h2>
  <ul class="agenda__liste">{agenda}</ul>
  <p>{bouton(t["nav"]["cours"], lien(lang, "cours", prof))}{bouton(t["nav"]["evenements"], lien(lang, "evenements", prof), "bouton bouton--ligne")}</p></div>
  {figure_photo(prof, "evenements/verres-de-vin-galerie", "Glasses raised among the paintings of the gallery" if lang == "en" else "Verres levés au milieu des tableaux de la galerie", "", "fossile agenda__img", "(max-width: 900px) 80vw, 32vw", ' data-parallaxe="-0.05"')}
</section>
<section class="infos" data-strate="{e(t["horaires"])}">
  {figure_photo(prof, "espace/enseigne-rue-village", "The Créa-Tea-Vité sign in the village street" if lang == "en" else "L'enseigne Créa-Tea-Vité dans la rue du village", "", "fossile infos__img", "(max-width: 800px) 80vw, 30vw")}
  <div class="infos__texte">{surtitre(t["horaires"], 6)}<dl class="horaires horaires--grand">{"".join(f"<div><dt>{e(j)}</dt><dd>{e(h)}</dd></div>" for j, h in t["horaires_lignes"])}</dl>{statut(lang, "statut--grand")}
  <p class="note">{e("The French version of the current site says 2:30 – 7 pm: to be confirmed. Exceptional closures are listed on Google Maps." if lang == "en" else "La version française du site actuel indique 14 h 30 – 19 h : à confirmer. Les fermetures exceptionnelles sont signalées sur Google Maps.")}</p>
  <address>{e(C.COORD["espace"])}<br>{e(C.COORD["rue"])}<br>{e(C.COORD["ville"])}</address><p><a href="mailto:{C.COORD["courriel_espace"]}">{C.COORD["courriel_espace"]}</a></p></div>
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
<section class="cocreation" data-strate="Co-Creating Sessions">
  {figure_photo(prof, "cours/table-aquarelle", "A workshop table covered in watercolour work" if lang == "en" else "Une table d'atelier couverte d'aquarelles", "", "fossile", "(max-width: 800px) 80vw, 30vw")}
  <div>{surtitre(L(lang, co["groupe"]), 3)}<h2 class="titre-section">{lettres(co["titre"])}</h2><p data-apparait>{e(L(lang, co["texte"]))}</p><p class="prix-grand" data-apparait>{co["prix"]} €</p>
  <p data-apparait>{bouton("Book a session" if lang == "en" else "Réserver une séance", lien(lang, "contact", prof) + "?objet=cours")}</p></div>
</section>'''
    corps = avec_carnet(corps, lang, prof, "cours")
    ecrire(chemin, page(lang, "cours", chemin, t["nav"]["cours"], corps, href_autre(lang, "cours", prof), {}, "page-cours"))


# ================================================================ événements privés
def page_evenements(lang):
    t = C.T[lang]
    chemin = fichier(lang, "evenements")
    prof = prof_de(chemin)
    ev = C.EVENEMENTS
    themes = "".join(f'<li data-incline><h3>{e(a[lang])}</h3><p>{e(b[lang])}</p></li>' for a, b in ev["themes"])
    corps = f'''
{bandeau(lang, prof, None, "Private, institutional or corporate gatherings" if lang == "en" else "Rencontres privées, institutionnelles ou d'entreprise", t["nav"]["evenements"], [ev["titre"][lang], ev["intro"][lang]], figure_photo(prof, "evenements/table-de-diner-dans-la-galerie", "A long dinner table set in the gallery" if lang == "en" else "Une longue table de dîner dressée dans la galerie", "", "fossile", "(max-width: 900px) 80vw, 36vw"), t["nav"]["evenements"])}
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
    "molten": {
        "intro": ("retraites/ouverture-des-boites-magiques", "Participants opening their boxes of materials around the studio table", "Les participants ouvrent leurs boîtes de matériel autour de la table de l'atelier"),
        "ingredients": ("atelier/melange-resines-pigments-cire", "Lisa Cirenza mixing resin, pigments and wax in the studio", "Lisa Cirenza mélange résine, pigments et cire à l'atelier"),
        "pour_qui": ("retraites/plein-air-en-foret", "Watercolour sketchbooks on a picnic table in the forest", "Carnets d'aquarelle sur une table de pique-nique en forêt"),
        "temoignages": ("paysages/oiseau-et-montagnes", "A bird above the mountains", "Un oiseau au-dessus des montagnes"),
        "inclus": ("retraites/aquarelle-sur-souche", "A watercolour palette and a small study on a tree stump", "Une palette d'aquarelle et une petite étude sur une souche"),
        "reserver": ("cours/pinceaux-bandeau", "", ""),
    },
}


def fig_retraite(lang, prof, cle, quoi, classe, sizes, attrs=""):
    src, en, fr = IMAGES_RETRAITE[cle][quoi]
    return figure_photo(prof, src, en if lang == "en" else fr, "", "fossile " + classe, sizes, attrs)


def page_retraite(lang, cle):
    t = C.T[lang]
    r = R.PIP if cle == "pip" else R.MOLTEN
    chemin = fichier(lang, cle)
    prof = prof_de(chemin)
    jours = []
    for i, j in enumerate(r["jours"]):
        ph = r["photos_jours"][i]
        img = figure_photo(prof, ph, "", "", "fossile jour__img", "(max-width: 800px) 86vw, 34vw")
        if i in r.get("decor_jour", {}):
            img += figure_decor(prof, r["decor_jour"][i], "", "Evocation" if lang == "en" else "Évocation", "fossile jour__img jour__img--2", "(max-width: 800px) 60vw, 22vw")
        items = "".join(f"<li>{e(x)}</li>" for x in j["items"][lang])
        jours.append(f'''<li class="jour" data-strate="{e(("Day " if lang == "en" else "Jour ") + str(i + 1))}">
  <p class="jour__n">{"Day" if lang == "en" else "Jour"} <span>{i + 1}</span></p>
  <div class="jour__texte"><h3>{e(j["titre"][lang])}</h3><ul class="liste-traits">{items}</ul><p class="jour__note" data-apparait>{e(j["note"][lang])}</p></div>
  <div class="jour__images">{img}</div>
</li>''')
    etapes = "".join(f'<li class="etape" data-etape="{i + 1}"><p class="etape__jour">{"Day" if lang == "en" else "Jour"} {et["jour"]}</p><h3>{e(L(lang, et["nom"]))}</h3><p>{e(et["texte"][lang])}</p><span class="etape__img">{img_photo(prof, r["photos_jours"][et["jour"] - 1], "", "(max-width: 900px) 60vw, 22vw")}</span></li>' for i, et in enumerate(r["etapes"]))
    temoins = "".join(f'<li data-incline><blockquote><p>“{e(x["texte"])}”</p><footer>{e(L(lang, x["nom"]))}{(" · " + e(x["source"])) if x.get("source") else ""}</footer></blockquote></li>' for x in r["temoignages"])
    faq = "".join(f'<details class="faq__item"><summary>{e(q[lang])}</summary><p>{e(rep[lang])}</p></details>' for q, rep in r.get("faq", []))
    coachs = ""
    if r.get("coachs"):
        coachs = '<section class="coachs" data-strate="' + e("Your creative coaches" if lang == "en" else "Vos coachs") + '">' + surtitre("Your creative coaches" if lang == "en" else "Vos coachs créatifs") + '<div class="coachs__grille">' + "".join(
            f'<article class="coach">{figure_photo(prof, c["photo"], c["nom"], "", "fossile coach__img", "(max-width: 800px) 70vw, 24vw")}<h3>{e(c["nom"])}</h3><p class="coach__role">{e(c["role"][lang])}</p><p data-apparait>{e(c["texte"][lang])}</p></article>' for c in r["coachs"]) + "</div></section>"
    ingredients = ""
    if r.get("ingredients"):
        ing = "".join(f'<li data-incline><h3>{e(a[lang])}</h3><p>{e(b[lang])}</p></li>' for a, b in r["ingredients"])
        rec = "".join(f'<li><strong>{e(a)}</strong> — {e(b)}</li>' for a, b in r["recettes"][lang])
        ingredients = f'''<section class="ingredients" data-strate="{e("The ingredients" if lang == "en" else "Les ingrédients")}">
  {surtitre("Two elements, one coherent dish" if lang == "en" else "Deux éléments, un seul plat", 2)}<h2 class="titre-section">{lettres("The ingredients" if lang == "en" else "Les ingrédients")}</h2>
  <ul class="ingredients__liste">{ing}</ul>
  <div class="ingredients__bas"><div class="recettes"><h3>{e("What you will write (and paint) in your Recipe Book" if lang == "en" else "Ce que vous écrirez (et peindrez) dans votre carnet")}</h3><ul class="liste-traits">{rec}</ul><p class="note-base" data-apparait>{e(r["base"][lang])}</p></div>
  {fig_retraite(lang, prof, cle, "ingredients", "ingredients__img", "(max-width: 900px) 80vw, 34vw", ' data-parallaxe="-0.04"')}</div>
</section>'''
    if cle == "pip":
        image_bandeau = f'<div class="bandeau__image bandeau__image--plein">{img_photo(prof, r["photo"], "Lake Annecy at Talloires" if lang == "en" else "Le lac d'Annecy à Talloires", "(max-width: 900px) 100vw, 60vw", "", "eager")}</div>'
    else:
        image_bandeau = f'<div class="bandeau__image bandeau__image--cire"><span class="bandeau__cire" aria-hidden="true">{img_decor(prof, r["decor"], "", "60vw")}</span>{img_photo(prof, r["photo"], "Participants working with hot wax in the studio" if lang == "en" else "Des participants travaillent la cire chaude à l'atelier", "(max-width: 900px) 90vw, 40vw", "bandeau__photo", "eager")}</div>'
    bientot = f'<p class="etiquette etiquette--cours">{e(L(lang, r["bientot"]))}</p>' if r.get("bientot") else ""
    corps = f'''
<section class="bandeau bandeau--retraite bandeau--{cle}" data-strate="{e(r["titre"])}">
  <div class="bandeau__texte">
    {surtitre(L(lang, r["dates"]) + " · " + L(lang, r["lieu"]))}
    <h1 class="bandeau__titre">{lettres(r["titre"])}</h1>
    <p class="bandeau__accroche" data-apparait>{e(L(lang, r["accroche"]))}</p>
    <p class="bandeau__cycle" data-apparait>{e(L(lang, r["cycle"]))}</p>
    <div class="bandeau__compte" data-apparait>{compte(lang, r["debut"])}{bientot}</div>
  </div>
  {image_bandeau}
</section>
<section class="retraite-intro" data-strate="{e("Welcome" if lang == "en" else "Bienvenue")}">
  <div class="retraite-intro__texte">{"".join(f'<p data-apparait>{e(x)}</p>' for x in r["intro"][lang])}{fig_retraite(lang, prof, cle, "intro", "retraite-intro__img", "(max-width: 900px) 92vw, 52vw")}</div>
  <dl class="fiche-pratique">
    <div><dt>{"Dates" if lang == "en" else "Dates"}</dt><dd>{e(L(lang, r["dates"]))}</dd></div>
    <div><dt>{"Place" if lang == "en" else "Lieu"}</dt><dd>{e(L(lang, r["lieu"]))}</dd></div>
    <div><dt>{"Group" if lang == "en" else "Groupe"}</dt><dd>{e(L(lang, r["groupe"]))}</dd></div>
    <div><dt>{"Price" if lang == "en" else "Tarif"}</dt><dd><strong>{e(L(lang, r["prix"]))}</strong> {e(L(lang, r["prix_note"]))}</dd></div>
  </dl>
</section>
{ingredients}
{coachs}
<section class="carte-retraite-topo" data-carte data-strate="{e("The route" if lang == "en" else "Le parcours")}">
  <div class="carte__collant">
    <div class="carte__svg">{carte_topo(lang, r)}</div>
    <div class="carte__panneau">{surtitre("The route" if lang == "en" else "Le parcours")}<ol class="etapes">{etapes}</ol><p class="note">{e("Schematic map, not to scale." if lang == "en" else "Carte schématique, sans échelle.")}</p></div>
    <div class="carte__progres" aria-hidden="true"><i></i></div>
  </div>
</section>
<section class="programme" data-strate="{e("Agenda" if lang == "en" else "Programme")}">
  <div class="programme__tete">{surtitre("Agenda" if lang == "en" else "Programme")}<h2 class="titre-section">{lettres("Five days" if lang == "en" else "Cinq jours")}</h2></div>
  <ol class="jours">{"".join(jours)}</ol>
</section>
<section class="pour-qui" data-strate="{e("Is this retreat right for me?" if lang == "en" else "Est-ce pour moi ?")}">
  {fig_retraite(lang, prof, cle, "pour_qui", "pour-qui__img", "(max-width: 900px) 80vw, 34vw", ' data-parallaxe="-0.05"')}
  <div>{surtitre("Anytime, anywhere" if lang == "en" else "N'importe quand, n'importe où")}<h2 class="titre-section">{lettres("Is this retreat right for me?" if lang == "en" else "Cette retraite est-elle pour moi ?")}</h2>
  <div class="pour-qui__texte">{"".join(f'<p data-apparait>{e(x)}</p>' for x in r["pour_qui"][lang])}</div></div>
</section>
<section class="temoignages" data-strate="{e("What people say" if lang == "en" else "Ils en parlent")}">
  {fig_retraite(lang, prof, cle, "temoignages", "temoignages__img", "100vw")}
  {surtitre("What people say" if lang == "en" else "Ce qu'ils en disent")}<ul class="temoignages__liste">{temoins}</ul>
  <p class="note">{e("Testimonials as published on the current site, in their original language." if lang == "en" else "Témoignages tels que publiés sur le site actuel, dans leur langue d'origine.")}</p>
</section>
<section class="inclus" data-strate="{e("What's included" if lang == "en" else "Ce qui est inclus")}">
  <div><h2 class="titre-section">{lettres("What's included" if lang == "en" else "Ce qui est inclus")}</h2><ul class="liste-traits liste-traits--oui">{"".join(f"<li>{e(x)}</li>" for x in R.INCLUS[lang])}</ul><p class="prix-grand">{e(L(lang, r["prix"]))}</p><p class="note">{e(L(lang, r["prix_note"]))}</p></div>
  <div><h2 class="titre-section">{lettres("Not included" if lang == "en" else "Non inclus")}</h2><ul class="liste-traits liste-traits--non">{"".join(f"<li>{e(x)}</li>" for x in R.NON_INCLUS[lang])}</ul></div>
  {fig_retraite(lang, prof, cle, "inclus", "inclus__img", "(max-width: 1100px) 80vw, 26vw", ' data-incline')}
</section>
{f'<section class="faq" data-strate="FAQ"><div>{surtitre("FAQ")}<h2 class="titre-section">{lettres("Questions")}</h2><div class="faq__liste">{faq}</div></div>{fig_retraite(lang, prof, cle, "faq", "faq__img", "(max-width: 900px) 70vw, 30vw")}</section>' if faq else ""}
<section class="reserver reserver--image" data-strate="{e("Book" if lang == "en" else "Réserver")}">
  <div class="reserver__fond" aria-hidden="true" data-parallaxe="0.08">{img_photo(prof, IMAGES_RETRAITE[cle]["reserver"][0], "", "100vw")}</div>
  <h2 class="titre-section">{lettres("Let’s make sure our creative dynamics align" if lang == "en" else "Vérifions que nos élans créatifs s'accordent")}</h2>
  <p data-apparait>{e("Book a brief, casual discovery call to talk about your practice." if lang == "en" else "Réservez un court échange découverte pour parler de votre pratique.")}</p>
  <p>{bouton("Discovery call" if lang == "en" else "Échange découverte", lien(lang, "contact", prof) + "?objet=retraite&retraite=" + cle)}<a class="bouton bouton--ligne aimant" href="https://wa.me/{C.COORD["tel_brut"].lstrip("+")}"><span>WhatsApp</span></a><a class="bouton bouton--ligne aimant" href="mailto:{C.COORD["courriel"]}"><span>{C.COORD["courriel"]}</span></a></p>
  <p class="note">{e("The current page lists the organiser's address as 74290 Talloires, while the atelier is at 74220 La Clusaz: to be checked." if lang == "en" else "La page actuelle indique l'adresse 74290 Talloires, alors que l'atelier est au 74220 La Clusaz : à vérifier.")}</p>
</section>'''
    ecrire(chemin, page(lang, cle, chemin, r["titre"], corps, href_autre(lang, cle, prof), {"retraite": cle}, "page-retraite page-retraite--" + cle))


def page_retraites(lang):
    t = C.T[lang]
    chemin = fichier(lang, "retraites")
    prof = prof_de(chemin)
    corps = f'''
{bandeau(lang, prof, None, "La Clusaz · Lake Annecy · 2027" if lang == "en" else "La Clusaz · lac d'Annecy · 2027", t["nav"]["retraites"], "Five days of creative thinking and activities, designed to inspire not only your painting, but everything you create—whether you photograph, cook, write, dance, code, build, or simply reflect." if lang == "en" else "Cinq jours d'activités et de réflexion créatives, pour nourrir votre peinture et tout ce que vous créez : photographier, cuisiner, écrire, danser, coder, construire, ou simplement réfléchir.", figure_photo(prof, "retraites/groupe-painters-in-paradise", "Painting in Paradise participants in front of the mountains" if lang == "en" else "Les participants de Painting in Paradise devant les montagnes", "Painters in Paradise, 2026", "fossile", "(max-width: 900px) 80vw, 36vw"), t["nav"]["retraites"])}
<section class="retraites-accueil retraites-accueil--page" data-strate="2027">
  <div class="retraites-cartes">
    {carte_retraite(lang, prof, R.PIP, "pip", "retraites/diner-coucher-de-soleil-parapentes")}
    {carte_retraite(lang, prof, R.MOLTEN, "molten", "retraites/atelier-cire-en-groupe")}
  </div>
</section>'''
    corps = avec_carnet(corps, lang, prof, "retraites")
    ecrire(chemin, page(lang, "retraites", chemin, t["nav"]["retraites"], corps, href_autre(lang, "retraites", prof), {}, "page-retraites"))


# ================================================================ contact
def page_contact(lang):
    t = C.T[lang]
    chemin = fichier(lang, "contact")
    prof = prof_de(chemin)
    c = C.COORD
    objets = [("oeuvre", "A work" if lang == "en" else "Une œuvre"), ("commande", "A commission" if lang == "en" else "Une commande"), ("cours", "A class" if lang == "en" else "Un cours"),
              ("evenement", "A private event" if lang == "en" else "Un événement privé"), ("retraite", "A retreat" if lang == "en" else "Une retraite"), ("autre", "Something else" if lang == "en" else "Autre chose")]
    radios = "".join(f'<label class="choix"><input type="radio" name="objet" value="{v}"{" checked" if i == 0 else ""}><span>{e(l)}</span></label>' for i, (v, l) in enumerate(objets))
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
      <div class="champ" data-pour="retraite" hidden><label for="f-retraite">{"Which retreat?" if lang == "en" else "Quelle retraite ?"}</label><select id="f-retraite" name="retraite"><option value="pip">Painting in Paradise · {e(L(lang, R.PIP["dates"]))}</option><option value="molten">Molten Magic · {e(L(lang, R.MOLTEN["dates"]))}</option></select></div>
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
  {figure_decor(0, "glacier-crevasse-4x5", "", "", "fossile erreur__img", "(max-width: 800px) 70vw, 30vw")}
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
         "espace": {"horaires": C.HORAIRES, "courriel": C.COORD["courriel"]},
         "retraites": {"pip": {"debut": R.PIP["debut"], "titre": R.PIP["titre"]}, "molten": {"debut": R.MOLTEN["debut"], "titre": R.MOLTEN["titre"]}}}
    (SITE / "assets" / "js" / f"donnees-{lang}.js").write_text("window.LC_DONNEES=" + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


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
    page_cours(lang)
    page_evenements(lang)
    page_retraites(lang)
    page_retraite(lang, "pip")
    page_retraite(lang, "molten")
    page_contact(lang)
    donnees_js(lang)
page_404()
(SITE / "vercel.json").write_text(json.dumps({"cleanUrls": True, "trailingSlash": False, "headers": [{"source": "/assets/img/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=604800"}]}]}, indent=2) + "\n")
print("pages générées, liens :", MODE, "· œuvres :", len(OEUVRES))
