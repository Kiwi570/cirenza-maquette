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


def ouvrir(chemin, fond=(255, 255, 255)):
    im = Image.open(chemin)
    icc = im.info.get("icc_profile")
    im = ImageOps.exif_transpose(im)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        if np.asarray(im)[..., 3].min() < 250:
            f = Image.new("RGB", im.size, fond)
            f.paste(im, mask=im.split()[-1])
            im = f
        else:
            im = im.convert("RGB")
    else:
        im = im.convert("RGB")
    return im, icc


def reduire(im, cote):
    w, h = im.size
    if max(w, h) <= cote:
        return im.copy()
    k = cote / max(w, h)
    return im.resize((max(1, round(w * k)), max(1, round(h * k))), Image.LANCZOS)


def enregistrer(im, chemin, qualite=82, icc=None):
    kw = {"quality": qualite, "method": 6}
    if icc:
        kw["icc_profile"] = icc
    im.save(chemin, "WEBP", **kw)
    return list(im.size)


# ---------------------------------------------------------------- couleurs (OKLab)
def srgb_lin(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055) * 255


M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566], [0.0883024619, 0.2817188376, 0.6299787005]])
M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099], [0.0259040371, 0.7827717662, -0.8086757660]])
M2i = np.array([[1.0, 0.3963377774, 0.2158037573], [1.0, -0.1055613458, -0.0638541728], [1.0, -0.0894841775, -1.2914855480]])
M1i = np.array([[4.0767416621, -3.3077115913, 0.2309699292], [-1.2684380046, 2.6097574011, -0.3413193965], [-0.0041960863, -0.7034186147, 1.7076147010]])


def oklab(rgb):
    return np.cbrt(srgb_lin(np.asarray(rgb, dtype=float)) @ M1.T) @ M2.T


def depuis_oklab(lab):
    return lin_srgb(((np.asarray(lab) @ M2i.T) ** 3) @ M1i.T)


def hexa(rgb):
    r, g, b = [int(round(max(0, min(255, v)))) for v in rgb]
    return f"#{r:02x}{g:02x}{b:02x}"


def dominante(im):
    px = np.asarray(im.resize((96, 96), Image.BILINEAR)).reshape(-1, 3).astype(float)
    lab = oklab(px)
    rng = np.random.default_rng(7)
    k = 6
    c = lab[rng.choice(len(lab), k, replace=False)]
    for _ in range(25):
        idx = ((lab[:, None, :] - c[None]) ** 2).sum(-1).argmin(1)
        for j in range(k):
            s = lab[idx == j]
            if len(s):
                c[j] = s.mean(0)
    part = np.bincount(idx, minlength=k) / len(lab)
    chroma = np.hypot(c[:, 1], c[:, 2])
    return c[int((part * (0.15 + chroma * 6)).argmax())]


def teinte(lab, L, cmax, k=0.32):
    c = np.hypot(lab[1], lab[2])
    h = np.arctan2(lab[2], lab[1])
    c2 = min(c * k, cmax)
    return hexa(depuis_oklab([L, c2 * np.cos(h), c2 * np.sin(h)]))


def accent(lab):
    c = np.hypot(lab[1], lab[2])
    h = np.arctan2(lab[2], lab[1])
    c2 = min(max(c, 0.06), 0.15)
    return hexa(depuis_oklab([min(max(lab[0], 0.42), 0.52), c2 * np.cos(h), c2 * np.sin(h)]))


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
