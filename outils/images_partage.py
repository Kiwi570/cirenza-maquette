"""Images de partage (og:image) : une carte 1200 × 630 en JPG par page et par langue.

Usage : python3 -I outils/images_partage.py <racine-site>   (puis relancer generer.py, qui les référence)
Œuvre ou photo de la page à gauche (œuvres jamais recadrées : posées entières sur le fond calcaire),
signature de Lisa et titre de la page à droite.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
import catalogue as CAT  # noqa: E402
import contenu as C  # noqa: E402
import retraites as R  # noqa: E402

SITE = Path(sys.argv[1]).resolve()
IMG = SITE / "assets" / "img"
OUT = SITE / "assets" / "partage"
OUT.mkdir(parents=True, exist_ok=True)
W, H = 1200, 630
CALCAIRE, GRANITE, AMBRE, ESPACE = (242, 239, 232), (43, 42, 40), (138, 79, 14), (36, 72, 106)


def police(taille, italique=False):
    for f in (SITE / "assets" / "polices" / ("fraunces-italique.woff" if italique else "fraunces.woff"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf")):
        try:
            return ImageFont.truetype(str(f), taille)
        except OSError:
            continue
    return ImageFont.load_default()


def oeuvre(oid):
    return ("oeuvre", IMG / "oeuvres" / f"{oid}-1600.webp")


def photo(cle):
    nom = cle.replace("/", "-")
    f = IMG / "photos" / f"{nom}-1600.webp"
    return ("photo", f if f.exists() else IMG / "photos" / f"{nom}-800.webp")


SERIES = {s["id"]: s for s in CAT.SERIES}
PAGES = {
    "accueil": (oeuvre("recente-01"), {"en": C.T["en"]["accroche"], "fr": C.T["fr"]["accroche"]}, "maison"),
    "oeuvres": (oeuvre("dream-big"), {"en": "Works", "fr": "Œuvres"}, "atelier"),
    "artiste": (photo("artiste/lisa-portrait-fond-glacier"), {"en": "The artist", "fr": "L'artiste"}, "atelier"),
    "parcours": (photo("expositions/bermondsey-gallery-vitrine-nuit"), {"en": "CV highlights", "fr": "Parcours"}, "atelier"),
    "presse": (photo("presse/wax-fusion-fall-2026-couverture"), {"en": "Press", "fr": "Presse"}, "atelier"),
    "espace": (photo("espace/visite-video-vignette"), {"en": "Espace Créa-Tea-Vité", "fr": "Espace Créa-Tea-Vité"}, "espace"),
    "cours": (photo("cours/in-the-studio"), {"en": "Classes & workshops", "fr": "Cours et ateliers"}, "espace"),
    "evenements": (photo("evenements/table-de-diner-dans-la-galerie"), {"en": "Private events", "fr": "Événements privés"}, "espace"),
    "retraites": (photo("paysages/lac-annecy-talloires-panorama"), {"en": "Retreats 2027", "fr": "Retraites 2027"}, "espace"),
    "pip": (photo("paysages/lac-annecy-talloires-panorama"), {"en": "Painting in Paradise · " + R.PIP["dates"]["en"], "fr": "Painting in Paradise · " + R.PIP["dates"]["fr"]}, "espace"),
    "pause": (photo("retraites/pause-face-aux-montagnes"), {"en": R.PAUSE["titre"] + " · " + R.PAUSE["dates"]["en"], "fr": R.PAUSE["titre"] + " · " + R.PAUSE["dates"]["fr"]}, "espace"),
    "boutique": (oeuvre("habanero"), {"en": "Shop · two counters", "fr": "Boutique · deux comptoirs"}, "maison"),
    "contact": (photo("espace/facade-de-nuit"), {"en": "Let's connect", "fr": "Écrivez-moi"}, "maison"),
}


def lignes(draw, texte, f, largeur):
    mots, out, cur = texte.split(), [], ""
    for m in mots:
        t = (cur + " " + m).strip()
        if draw.textlength(t, font=f) <= largeur:
            cur = t
        else:
            out.append(cur)
            cur = m
    out.append(cur)
    return out


def carte(source, titre, univers, nom_fichier, lang="en"):
    genre, f = source
    fond = Image.new("RGB", (W, H), CALCAIRE)
    im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
    zone = (0, 0, 690, H)
    if genre == "oeuvre":
        im.thumbnail((zone[2] - 80, H - 80), Image.LANCZOS)
        fond.paste(im, ((zone[2] - im.width) // 2, (H - im.height) // 2))
    else:
        im = ImageOps.fit(im, (zone[2], H), Image.LANCZOS, centering=(0.5, 0.4))
        fond.paste(im, (0, 0))
    d = ImageDraw.Draw(fond)
    accent = {"atelier": AMBRE, "espace": ESPACE}.get(univers, GRANITE)
    d.rectangle([690, 0, 698, H], fill=accent)
    sig = Image.open(IMG / "logos" / "signature.webp").convert("RGBA")
    sig.thumbnail((300, 120), Image.LANCZOS)
    teinte = Image.new("RGBA", sig.size, GRANITE + (255,))
    teinte.putalpha(sig.split()[-1])
    fond.paste(teinte, (750, 70), teinte)
    ft = police(46)
    y = 250
    for ligne in lignes(d, titre, ft, 400)[:4]:
        d.text((750, y), ligne, font=ft, fill=GRANITE)
        y += 58
    d.text((750, H - 80), "La Clusaz · " + ("French Alps" if lang == "en" else "Alpes françaises"), font=police(22, True), fill=accent)
    fond.save(OUT / nom_fichier, "JPEG", quality=84, optimize=True, progressive=True)


n = 0
for cle, (src, titres, univers) in PAGES.items():
    for lang in ("en", "fr"):
        chemin = C.PAGES[cle][lang]
        carte(src, titres[lang], univers, chemin.replace("/", "-") + ".jpg", lang)
        n += 1
for s in CAT.SERIES:
    for lang in ("en", "fr"):
        dossier = "works" if lang == "en" else "fr/oeuvres"
        chemin = f"{dossier}/{s['slug'][lang]}"
        carte(oeuvre(s["oeuvres"][0]["id"]), s["titre"][lang], "atelier", chemin.replace("/", "-") + ".jpg", lang)
        n += 1
print("images de partage :", n)
