"""Outils communs de traitement des médias (WebP, couleurs OKLab).

Utilisés par preparer_medias.py (première préparation) et ajouter_medias.py (ajouts suivants).
Les œuvres ne sont jamais recadrées, recolorées ni filtrées : seul le redimensionnement est appliqué.
"""
import numpy as np
from PIL import Image, ImageOps

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
