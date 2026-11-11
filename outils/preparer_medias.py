"""Prépare les médias du site Lisa Cirenza : WebP en plusieurs tailles, couleurs dominantes,
textures et masques de l'effet « cire qui fond ».

Usage : python3 -I outils/preparer_medias.py <sources> <grok> <racine-site>
Les œuvres ne sont jamais recadrées, recolorées ni filtrées : seul le redimensionnement est appliqué.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps, ImageFilter

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
import catalogue as CAT  # noqa: E402

SRC = Path(sys.argv[1])
GROK = Path(sys.argv[2])
SITE = Path(sys.argv[3])
IMG = SITE / "assets" / "img"
for d in ("oeuvres", "photos", "decors", "masques", "textures", "icones", "logos"):
    (IMG / d).mkdir(parents=True, exist_ok=True)
Image.MAX_IMAGE_PIXELS = None
HD_MAX = 3200


from medias_outils import ouvrir, reduire, enregistrer, oklab, depuis_oklab, hexa, dominante, teinte, accent  # noqa: E402,F401


meta = {"oeuvres": {}, "photos": {}, "decors": {}, "logos": {}}

# ---------------------------------------------------------------- œuvres
toutes = [o for s in CAT.SERIES for o in s["oeuvres"]] + CAT.HORS_SERIE
for o in toutes:
    oid = o["id"]
    src = (SRC / "oeuvres" / o["src"]).resolve()
    im, icc = ouvrir(src)
    info = {"original": list(im.size)}
    info["640"] = enregistrer(reduire(im, 640), IMG / "oeuvres" / f"{oid}-640.webp", 80, icc)
    info["1600"] = enregistrer(reduire(im, 1600), IMG / "oeuvres" / f"{oid}-1600.webp", 82, icc)
    if max(im.size) >= 1400:
        info["hd"] = enregistrer(reduire(im, HD_MAX), IMG / "oeuvres" / f"{oid}-hd.webp", 82, icc)
    lab = dominante(im)
    info["dominante"] = hexa(depuis_oklab(lab))
    info["fond"] = teinte(lab, 0.94, 0.032)
    info["accent"] = accent(lab)
    meta["oeuvres"][oid] = info
    print(f"{oid:34s} {str(im.size):14s} {info['dominante']} {info['fond']}")

# ---------------------------------------------------------------- photos réelles
for f in sorted((SRC / "photos").rglob("*")):
    if not f.is_file() or f.suffix.lower() not in (".jpg", ".jpeg", ".png") or f.parent.name in ("logos", "oeuvres-a-confirmer"):
        continue
    cle = f"{f.parent.name}/{f.stem}"
    nom = f"{f.parent.name}-{f.stem}"
    im, icc = ouvrir(f)
    info = {"original": list(im.size)}
    info["800"] = enregistrer(reduire(im, 800), IMG / "photos" / f"{nom}-800.webp", 78, icc)
    if max(im.size) > 1000:
        info["1600"] = enregistrer(reduire(im, 1600), IMG / "photos" / f"{nom}-1600.webp", 80, icc)
    lab = dominante(im)
    info["fond"] = teinte(lab, 0.94, 0.03)
    meta["photos"][cle] = info

# ---------------------------------------------------------------- décors Grok
for f in sorted(GROK.glob("*.jpg")):
    im, icc = ouvrir(f)
    info = {"original": list(im.size)}
    info["full"] = enregistrer(im, IMG / "decors" / f"{f.stem}.webp", 84)
    info["640"] = enregistrer(reduire(im, 640), IMG / "decors" / f"{f.stem}-640.webp", 78)
    meta["decors"][f.stem] = info

# ---------------------------------------------------------------- logos (masques alpha, teintés par le CSS)
for nom, f in (("signature", SRC / "logos" / "logo-lisa-cirenza.png"), ("signature-complete", SRC / "photos" / "logos" / "signature-lisa-cirenza-or.png")):
    lg = Image.open(f).convert("RGBA")
    lg = lg.crop(lg.getbbox())
    a = lg.split()[-1]
    blanc = Image.new("RGBA", lg.size, (255, 255, 255, 0))
    blanc.putalpha(a)
    blanc = reduire(blanc, 1000)
    blanc.save(IMG / "logos" / f"{nom}.webp", "WEBP", lossless=True, method=6)
    meta["logos"][nom] = list(blanc.size)
esp, _ = ouvrir(SRC / "logos" / "logo-avec-signature.png", fond=(242, 239, 232))
meta["logos"]["espace"] = enregistrer(reduire(esp, 480), IMG / "logos" / "espace.webp", 86)

# ---------------------------------------------------------------- textures de l'effet cire
cf = Image.open(GROK / "cire-fondue-1x1.jpg").convert("L")
cf = ImageOps.autocontrast(cf, cutoff=1).filter(ImageFilter.GaussianBlur(1.2))
cf.resize((1024, 688), Image.LANCZOS).save(IMG / "textures" / "cire-relief.webp", "WEBP", quality=86)
for nom in ("strates-cire-16x9", "strates-cire-9x16"):
    im, _ = ouvrir(GROK / f"{nom}.jpg")
    enregistrer(im, IMG / "textures" / f"{nom}.webp", 86)


def coulure(larg=480, haut=2400, seed=5):
    """Sprite vertical : tiers haut opaque, tiers central = front de cire qui coule, tiers bas transparent."""
    rng = np.random.default_rng(seed)
    x = np.arange(larg)
    bas = np.convolve(rng.normal(0, 1, larg + 120), np.ones(60) / 60, "same")[60:60 + larg]
    gouttes = np.zeros(larg)
    for _ in range(9):
        c = rng.uniform(0, larg)
        w = rng.uniform(8, 26)
        l = rng.uniform(0.05, 0.16) * haut
        gouttes += l * np.exp(-((x - c) / w) ** 2 * 1.6)
    front = haut * 0.46 + bas * haut * 0.03 + gouttes
    y = np.arange(haut)[:, None]
    d = (front[None, :] - y) / (haut * 0.012)
    alpha = 1 / (1 + np.exp(-d * 2.2))
    alpha[: int(haut * 0.30)] = 1
    alpha[int(haut * 0.80):] = 0
    im = Image.new("RGBA", (larg, haut), (0, 0, 0, 0))
    im.putalpha(Image.fromarray((np.clip(alpha, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)))
    return im


coulure().save(IMG / "masques" / "coulure.webp", "WEBP", lossless=True, method=6)
coulure(seed=11).transpose(Image.ROTATE_90).save(IMG / "masques" / "coulure-h.webp", "WEBP", lossless=True, method=6)

# ---------------------------------------------------------------- icônes : trois strates
def icone(t):
    im = Image.new("RGBA", (t, t), (0, 0, 0, 0))
    a = np.zeros((t, t, 4), dtype=np.uint8)
    couleurs = [(242, 239, 232), (211, 139, 44), (143, 179, 196), (43, 42, 40)]
    bandes = [0, 0.34, 0.56, 0.78, 1]
    for i, c in enumerate(couleurs):
        y0, y1 = int(bandes[i] * t), int(bandes[i + 1] * t)
        a[y0:y1, :, :3] = c
        a[y0:y1, :, 3] = 255
    im = Image.fromarray(a)
    masque = Image.new("L", (t * 4, t * 4), 0)
    from PIL import ImageDraw
    ImageDraw.Draw(masque).rounded_rectangle([0, 0, t * 4 - 1, t * 4 - 1], radius=t * 4 * 0.22, fill=255)
    im.putalpha(masque.resize((t, t), Image.LANCZOS))
    return im


for t in (32, 180, 192, 512):
    icone(t).save(IMG / "icones" / f"icone-{t}.png")
icone(180).convert("RGB").save(IMG / "icones" / "apple-touch-icon.png")

(SITE / "outils" / "medias.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
print("ok", len(meta["oeuvres"]), "œuvres,", len(meta["photos"]), "photos,", len(meta["decors"]), "décors")
