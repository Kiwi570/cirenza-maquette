"""Import complet de l'inventaire Artwork Archive dans le site (Portfolio, et Commissions and Available Works).

Artwork Archive n'a pas d'API et son profil public est protégé contre les robots : la source est l'export de Lisa
(Pieces > New Report > Export to CSV). Un export Excel s'enregistre d'abord en CSV (UTF-8).

Usage :
  python3 -I outils/import_artwork_archive.py <export.csv>                       analyse : rapport, rien n'est écrit
  python3 -I outils/import_artwork_archive.py <export.csv> --ecrire <sources>    écrit les fichiers et télécharge les images

Règles (proposées à Lisa le 20 novembre 2026, à confirmer par elle) :
  - Portfolio : pièce publique (si l'export a la colonne) avec au moins une image ; les pièces privées n'apparaissent jamais ;
  - Commissions and Available Works : pièce publique au statut Available ;
  - vendue, non disponible, prêtée, réservée : Portfolio seulement ;
  - étiquette « price on request » (ou prix vide) : « Price on request », pas d'ajout au panier ;
  - les collections d'Artwork Archive deviennent les salles du Portfolio (rapprochées par leur nom) ;
  - images : dans l'ordre d'Artwork Archive ; la première est l'image principale.

Avec --ecrire :
  outils/artwork_archive.json   faits des œuvres déjà au catalogue (le générateur les applique) ;
  outils/aa_nouvelles.json      nouvelles œuvres, avec leur salle (le générateur les ajoute) ;
  outils/ajouts_aa.json         manifeste des images pour outils/ajouter_medias.py ;
  <sources>/oeuvres/<id>.<ext>  images téléchargées (image principale ; les autres dans <sources>/details/).
Puis : python3 -I outils/ajouter_medias.py <sources> . outils/ajouts_aa.json && python3 -I outils/generer.py .
"""
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
import artwork_archive as AA  # noqa: E402
import catalogue as CAT  # noqa: E402

OUI = {"yes", "y", "true", "1", "public", "x", "oui", "visible"}
NON = {"no", "n", "false", "0", "private", "non", "privé", "prive", "hidden"}
SUR_DEMANDE = {"price on request", "prix sur demande", "por", "price-on-request"}


def slug(x):
    return re.sub(r"[^a-z0-9]+", "-", AA.norme(x)).strip("-")[:48] or "sans-titre"


def images(ligne):
    """Toutes les adresses d'images de la ligne, dans l'ordre, sans doublon."""
    vus, sortie = set(), []
    for k, v in ligne.items():
        if not k or not v:
            continue
        nom = k.strip().lower()
        if nom in [c.lower() for c in AA.COLONNES["images"]] or ("image" in nom and "url" in nom):
            for u in re.findall(r"https?://[^\s|,;\"']+", str(v)):
                if u not in vus:
                    vus.add(u)
                    sortie.append(u)
    return sortie


def est_public(ligne):
    v = (AA.valeur(ligne, "public") or "").strip().lower()
    if not v:
        return None  # colonne absente ou vide : on ne peut pas savoir
    if v in OUI:
        return True
    if v in NON:
        return False
    return None


def etiquettes(ligne):
    return [x.strip().lower() for x in re.split(r"[,;|]", AA.valeur(ligne, "etiquettes") or "") if x.strip()]


def salle(collection):
    """Rapproche une collection d'Artwork Archive d'une salle du site (titre anglais ou français, ou identifiant)."""
    if not collection:
        return None
    n = AA.norme(collection)
    for s in CAT.SERIES:
        noms = {AA.norme(s["titre"]["en"]), AA.norme(s["titre"]["fr"]), AA.norme(s["id"]), AA.norme(s["slug"]["en"])}
        if n in noms or any(n and (n in x or x in n) for x in noms if len(x) > 3):
            return s["id"]
    return None


def lire(chemin):
    lignes = list(csv.DictReader(open(chemin, encoding="utf-8-sig", newline="")))
    connues = {o["id"]: o for s in CAT.SERIES for o in s["oeuvres"]}
    connues.update({o["id"]: o for o in CAT.HORS_SERIE})
    par_titre = {AA.norme(o["titre"]): oid for oid, o in connues.items() if o.get("titre")}
    par_inv = {v: k for k, v in AA.CORRESPONDANCES.items()}
    pieces = []
    for ligne in lignes:
        titre = AA.valeur(ligne, "titre")
        if not titre:
            continue
        inv = AA.valeur(ligne, "inventaire")
        unite = AA.valeur(ligne, "unite")
        h, l, p = (AA.en_cm(AA.nombre(AA.valeur(ligne, k)), unite) for k in ("hauteur", "largeur", "profondeur"))
        an = re.search(r"(19|20)\d\d", AA.valeur(ligne, "annee") or "")
        tags = etiquettes(ligne)
        prix = AA.nombre(AA.valeur(ligne, "prix"))
        statut = AA.STATUTS.get((AA.valeur(ligne, "statut") or "").strip().lower(), "inconnu")
        pub = est_public(ligne)
        imgs = images(ligne)
        oid = par_inv.get(inv) or par_titre.get(AA.norme(titre))
        pieces.append({
            "ligne": ligne, "id_site": oid, "inventaire": inv, "titre": titre,
            "annee": an.group() if an else None, "technique": AA.valeur(ligne, "technique"),
            "dims": [x for x in (h, l) if x], "profondeur": p, "edition": AA.valeur(ligne, "edition"),
            "cadre": AA.valeur(ligne, "cadre"), "description": AA.valeur(ligne, "description"),
            "collection": AA.valeur(ligne, "collection"), "salle": salle(AA.valeur(ligne, "collection")),
            "statut": statut, "public": pub, "images": imgs, "etiquettes": tags,
            "prix": None if any(t in SUR_DEMANDE for t in tags) else prix,
            "sur_demande": any(t in SUR_DEMANDE for t in tags) or not prix,
            "devise": (AA.valeur(ligne, "devise") or "EUR").upper(),
        })
    return lignes, pieces


def classer(p):
    if p["public"] is False:
        return "privée"
    if not p["images"] and not p["id_site"]:
        return "sans image"
    if p["statut"] == "disponible":
        return "disponible"
    return "portfolio"


def rapport(lignes, pieces):
    cols = list(lignes[0].keys()) if lignes else []
    trouvees = {c: AA.valeur(lignes[0], c) is not None or any(AA.valeur(x, c) for x in lignes) for c in AA.COLONNES}
    out = [f"Export : {len(lignes)} lignes, {len(pieces)} pièces avec un titre.",
           "Colonnes de l'export : " + " | ".join(cols),
           "Champs reconnus : " + ", ".join(k for k, v in trouvees.items() if v),
           "Champs absents : " + (", ".join(k for k, v in trouvees.items() if not v) or "aucun")]
    groupes = {}
    for p in pieces:
        groupes.setdefault(classer(p), []).append(p)
    for g in ("disponible", "portfolio", "privée", "sans image"):
        out.append(f"\n{g.upper()} : {len(groupes.get(g, []))}")
        for p in groupes.get(g, []):
            ou = p["id_site"] or ("nouvelle → " + (p["salle"] or f"salle à choisir (collection « {p['collection'] or '—'} »)"))
            px = "prix sur demande" if p["sur_demande"] else f"{p['prix']:g} {p['devise']}"
            out.append(f"  {p['inventaire'] or '—':14s} {p['titre'][:40]:40s} {px:18s} {len(p['images'])} image(s) · {ou}")
    return "\n".join(out), groupes


def telecharger(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["curl", "-sS", "-L", "--fail", "--max-time", "120", "-o", str(dest), url], capture_output=True, text=True)
    return r.returncode == 0 and dest.exists() and dest.stat().st_size > 1000, r.stderr.strip()[:160]


def extension(url):
    m = re.search(r"\.(jpe?g|png|webp)(?:\?|$)", url, re.I)
    return "." + (m.group(1).lower().replace("jpeg", "jpg") if m else "jpg")


def ecrire(pieces, groupes, sources):
    connues, nouvelles, manifeste, echecs = {}, [], {"_note": "Images importées d'Artwork Archive (export de Lisa).", "oeuvres": {}}, []
    for p in pieces:
        g = classer(p)
        if g in ("privée", "sans image"):
            continue
        d = {"inventaire": p["inventaire"], "titre": p["titre"], "annee": p["annee"], "technique_en": p["technique"],
             "edition_en": p["edition"], "statut": p["statut"], "profondeur": p["profondeur"], "cadre": p["cadre"],
             "description_en": p["description"], "nb_images": len(p["images"]), "sur_demande": p["sur_demande"]}
        if len(p["dims"]) == 2:
            d["dims"] = p["dims"]
        if p["prix"]:
            d["prix"], d["devise"] = p["prix"], p["devise"]
        d = {k: v for k, v in d.items() if v not in (None, "", [])}
        if p["id_site"]:
            connues[p["id_site"]] = d
            continue
        oid = "aa-" + slug(p["inventaire"] or p["titre"])
        ok, err = telecharger(p["images"][0], Path(sources) / "oeuvres" / f"{oid}{extension(p['images'][0])}")
        if not ok:
            echecs.append(f"{oid} : {p['images'][0][:80]} ({err})")
            continue
        for i, u in enumerate(p["images"][1:], 2):
            telecharger(u, Path(sources) / "details" / f"{oid}-{i}{extension(u)}")
        manifeste["oeuvres"][oid] = f"Artwork Archive {p['inventaire'] or ''} · {p['images'][0]}"
        nouvelles.append(dict(d, id=oid, salle=p["salle"] or "hors-serie", collection=p["collection"]))
    (ICI / "artwork_archive.json").write_text(json.dumps(connues, ensure_ascii=False, indent=1))
    (ICI / "aa_nouvelles.json").write_text(json.dumps(nouvelles, ensure_ascii=False, indent=1))
    (ICI / "ajouts_aa.json").write_text(json.dumps(manifeste, ensure_ascii=False, indent=1))
    return connues, nouvelles, echecs


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    lignes, pieces = lire(sys.argv[1])
    texte, groupes = rapport(lignes, pieces)
    print(texte)
    if "--ecrire" in sys.argv:
        sources = sys.argv[sys.argv.index("--ecrire") + 1]
        connues, nouvelles, echecs = ecrire(pieces, groupes, sources)
        print(f"\nÉcrit : {len(connues)} œuvres connues mises à jour, {len(nouvelles)} nouvelles œuvres, {len(echecs)} image(s) introuvable(s).")
        for x in echecs:
            print("  image introuvable :", x)


if __name__ == "__main__":
    main()
