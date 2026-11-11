"""Fusionne l'inventaire Artwork Archive dans le catalogue du site.

Artwork Archive reste la base maîtresse des œuvres : Lisa y tient titres, dimensions, années,
techniques, prix, disponibilités et numéros d'inventaire. Ce script lit l'export CSV de son
inventaire (Artwork Archive > Pieces > Export) et écrit outils/artwork_archive.json, que le
générateur applique par-dessus catalogue.py à chaque génération.

Usage : python3 -I outils/artwork_archive.py <export.csv> [--rapport]

Rapprochement, dans cet ordre :
  1. le numéro d'inventaire déjà noté dans CORRESPONDANCES ci-dessous (id du site -> n° Artwork Archive) ;
  2. le titre, comparé sans accents, ponctuation ni majuscules.
Les pièces d'Artwork Archive sans correspondance sont listées dans le rapport, jamais publiées d'office.
"""
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
import catalogue as CAT  # noqa: E402

# id du site -> numéro d'inventaire Artwork Archive (à compléter avec Lisa pour les œuvres sans titre)
CORRESPONDANCES = {
    # "recente-01": "LC-2026-001",
}

# Les en-têtes de l'export varient selon les réglages du compte : on accepte plusieurs libellés.
COLONNES = {
    "inventaire": ["Inventory Number", "Inventory #", "Piece ID", "ID"],
    "titre": ["Title", "Piece Title", "Name"],
    "annee": ["Creation Date", "Date Created", "Year", "Creation Year"],
    "technique": ["Medium", "Media", "Materials"],
    "hauteur": ["Height"],
    "largeur": ["Width"],
    "profondeur": ["Depth"],
    "unite": ["Unit", "Units", "Dimension Unit", "Measurement Unit"],
    "prix": ["Price", "Retail Price", "Sale Price"],
    "devise": ["Currency"],
    "statut": ["Status", "Availability"],
    "collection": ["Collection", "Collections", "Series"],
    "description": ["Description", "Notes"],
    "edition": ["Edition", "Edition Info", "Edition Size"],
}
STATUTS = {"sold": "vendu", "available": "disponible", "not for sale": "non-disponible", "nfs": "non-disponible",
           "on loan": "en-pret", "in progress": "en-cours", "work in progress": "en-cours", "consigned": "disponible",
           "reserved": "reserve", "on hold": "reserve", "gifted": "non-disponible", "donated": "non-disponible"}


def norme(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def valeur(ligne, cle):
    for nom in COLONNES[cle]:
        for k, v in ligne.items():
            if k and k.strip().lower() == nom.lower() and str(v or "").strip():
                return str(v).strip()
    return None


def nombre(x):
    if not x:
        return None
    m = re.search(r"\d+(?:[.,]\d+)?", x)
    return float(m.group().replace(",", ".")) if m else None


def en_cm(v, unite):
    if v is None:
        return None
    u = (unite or "cm").strip().lower()
    if u in ("in", "in.", "inch", "inches", '"'):
        v *= 2.54
    elif u in ("mm",):
        v /= 10
    return round(v, 1)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    lignes = list(csv.DictReader(open(sys.argv[1], encoding="utf-8-sig", newline="")))
    site = {o["id"]: o for s in CAT.SERIES for o in s["oeuvres"]}
    site.update({o["id"]: o for o in CAT.HORS_SERIE})
    par_titre = {norme(o["titre"]): oid for oid, o in site.items() if o.get("titre")}
    par_inv = {v: k for k, v in CORRESPONDANCES.items()}
    sortie, orphelines = {}, []
    for ligne in lignes:
        inv, titre = valeur(ligne, "inventaire"), valeur(ligne, "titre")
        oid = par_inv.get(inv) or par_titre.get(norme(titre))
        if not oid:
            orphelines.append(f"{inv or '—'} · {titre or 'sans titre'}")
            continue
        unite = valeur(ligne, "unite")
        h, l, p = (en_cm(nombre(valeur(ligne, k)), unite) for k in ("hauteur", "largeur", "profondeur"))
        statut = STATUTS.get((valeur(ligne, "statut") or "").lower())
        d = {"inventaire": inv, "titre": titre}
        if h and l:
            d["dims"] = [h, l]
        if p:
            d["profondeur"] = p
        an = re.search(r"(19|20)\d\d", valeur(ligne, "annee") or "")
        if an:
            d["annee"] = an.group()
        if valeur(ligne, "technique"):
            d["technique_en"] = valeur(ligne, "technique")
        if valeur(ligne, "edition"):
            d["edition_en"] = valeur(ligne, "edition")
        if statut:
            d["statut"] = statut
        prix = nombre(valeur(ligne, "prix"))
        if prix:
            d["prix"] = prix
            d["devise"] = valeur(ligne, "devise") or "EUR"
        sortie[oid] = {k: v for k, v in d.items() if v is not None}
    (ICI / "artwork_archive.json").write_text(json.dumps(sortie, ensure_ascii=False, indent=1))
    print(f"{len(sortie)} œuvres rapprochées sur {len(lignes)} lignes ; {len(orphelines)} sans correspondance.")
    if "--rapport" in sys.argv or orphelines:
        for x in orphelines:
            print("  à rapprocher :", x)
    sans = [oid for oid in site if oid not in sortie]
    if "--rapport" in sys.argv:
        print("Œuvres du site absentes de l'export :", ", ".join(sans) or "aucune")


if __name__ == "__main__":
    main()
