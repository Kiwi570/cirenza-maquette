"""Ajoute ou remplace quelques médias sans repréparer tout le site.

Usage : python3 -I outils/ajouter_medias.py <dossier-sources> <racine-site> [manifeste.json]

Le dossier de sources contient oeuvres/<id>.<ext> et photos/<dossier>/<nom>.<ext>.
Le manifeste (par défaut outils/ajouts_v3.json) liste ce qui est à traiter et d'où vient chaque fichier.
Les œuvres ne sont jamais recadrées, recolorées ni filtrées : seul le redimensionnement est appliqué.
"""
import json
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
from medias_outils import HD_MAX, accent, depuis_oklab, dominante, enregistrer, hexa, ouvrir, reduire, teinte  # noqa: E402

SRC = Path(sys.argv[1])
SITE = Path(sys.argv[2])
MANIFESTE = Path(sys.argv[3]) if len(sys.argv) > 3 else ICI / "ajouts_v3.json"
IMG = SITE / "assets" / "img"
META = ICI / "medias.json"

meta = json.loads(META.read_text())
plan = json.loads(MANIFESTE.read_text())


def trouver(dossier, nom):
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        f = dossier / f"{nom}{ext}"
        if f.exists():
            return f
    raise FileNotFoundError(dossier / nom)


for oid in plan.get("oeuvres", {}):
    im, icc = ouvrir(trouver(SRC / "oeuvres", oid))
    info = {"original": list(im.size)}
    info["640"] = enregistrer(reduire(im, 640), IMG / "oeuvres" / f"{oid}-640.webp", 80, icc)
    info["1600"] = enregistrer(reduire(im, 1600), IMG / "oeuvres" / f"{oid}-1600.webp", 82, icc)
    hd = IMG / "oeuvres" / f"{oid}-hd.webp"
    if max(im.size) >= 1400:
        info["hd"] = enregistrer(reduire(im, HD_MAX), hd, 82, icc)
    elif hd.exists():
        hd.unlink()
    lab = dominante(im)
    info["dominante"] = hexa(depuis_oklab(lab))
    info["fond"] = teinte(lab, 0.94, 0.032)
    info["accent"] = accent(lab)
    meta["oeuvres"][oid] = info
    print(f"œuvre {oid:28s} {str(im.size):14s} {info['dominante']}")

for cle in plan.get("photos", {}):
    dossier, nom = cle.split("/")
    im, icc = ouvrir(trouver(SRC / "photos" / dossier, nom))
    fichier = f"{dossier}-{nom}"
    info = {"original": list(im.size)}
    info["800"] = enregistrer(reduire(im, 800), IMG / "photos" / f"{fichier}-800.webp", 78, icc)
    if max(im.size) > 1000:
        info["1600"] = enregistrer(reduire(im, 1600), IMG / "photos" / f"{fichier}-1600.webp", 80, icc)
    info["fond"] = teinte(dominante(im), 0.94, 0.03)
    meta["photos"][cle] = info
    print(f"photo {cle:44s} {str(im.size):14s}")

META.write_text(json.dumps(meta, ensure_ascii=False, indent=1))
print("ok :", len(plan.get("oeuvres", {})), "œuvres,", len(plan.get("photos", {})), "photos")
