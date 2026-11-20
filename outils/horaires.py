"""Horaires de l'Espace : lecture de assets/data/horaires.json et mises en forme.

Le même fichier est lu par le générateur (pages statiques, données structurées) et par le
navigateur (statut ouvert ou fermé, annonces, aperçu depuis l'éditeur). Sur le site final
(Wix Headless), il est remplacé par deux collections du tableau de bord Wix : « Horaires »
et « Exceptions », avec les mêmes champs.
"""
import json
from pathlib import Path

JOURS = {"en": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
         "fr": ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"]}
JOURS_COURTS = {"en": ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
                "fr": ["dim", "lun", "mar", "mer", "jeu", "ven", "sam"]}
SCHEMA_JOURS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
ORDRE_SEMAINE = [1, 2, 3, 4, 5, 6, 0]
RDV = {"en": "by appointment", "fr": "sur rendez-vous"}


def charger(site):
    return json.loads((Path(site) / "assets" / "data" / "horaires.json").read_text(encoding="utf-8"))


def heure(hm, lang, suffixe=True):
    h, m = (int(x) for x in hm.split(":"))
    if lang == "fr":
        return f"{h} h {m:02d}" if m else f"{h} h"
    h12 = (h + 11) % 12 + 1
    txt = f"{h12}:{m:02d}" if m else f"{h12}"
    return txt + ((" pm" if h >= 12 else " am") if suffixe else "")


def plages(ligne):
    p = []
    if ligne.get("ouvert") and ligne.get("debut") and ligne.get("fin"):
        p.append((ligne["debut"], ligne["fin"]))
        if ligne.get("debut2") and ligne.get("fin2"):
            p.append((ligne["debut2"], ligne["fin2"]))
    return p


def texte_plages(p, lang, court=False):
    morceaux = []
    for d, f in p:
        if lang == "en" and court:
            meme = (int(d[:2]) >= 12) == (int(f[:2]) >= 12)
            morceaux.append(f"{heure(d, lang, not meme)} – {heure(f, lang)}")
        else:
            morceaux.append(f"{heure(d, lang)} – {heure(f, lang)}")
    return (", " if lang == "en" else ", ").join(morceaux)


def _groupes(H):
    par_jour = {l["jour"]: l for l in H["horaires"]}
    groupes = []
    for j in ORDRE_SEMAINE:
        l = par_jour.get(j, {"jour": j, "ouvert": False})
        cle = ("ouvert", tuple(plages(l))) if plages(l) else (("rdv",) if l.get("surRendezVous") else ("ferme",))
        if groupes and groupes[-1][0] == cle and ORDRE_SEMAINE.index(j) == ORDRE_SEMAINE.index(groupes[-1][1][-1]) + 1:
            groupes[-1][1].append(j)
        else:
            groupes.append((cle, [j]))
    return groupes


def _jours_txt(js, lang, court=False):
    noms = JOURS_COURTS[lang] if court else JOURS[lang]
    a, b = noms[js[0]], noms[js[-1]]
    a = a[0].upper() + a[1:]
    return a if len(js) == 1 else f"{a} – {b}"


def lignes(H, lang):
    """[(jours, heures)] pour les jours ouverts ou sur rendez-vous, du lundi au dimanche."""
    out = []
    for cle, js in _groupes(H):
        if cle[0] == "ouvert":
            out.append((_jours_txt(js, lang), texte_plages(cle[1], lang)))
        elif cle[0] == "rdv":
            out.append((_jours_txt(js, lang), RDV[lang]))
    return out


def court(H, lang):
    for cle, js in _groupes(H):
        if cle[0] == "ouvert":
            return f"{_jours_txt(js, lang, True)} · {texte_plages(cle[1], lang, True)}"
    return RDV[lang]


def schema_ouverture(H):
    """openingHoursSpecification de schema.org (semaine et exceptions datées)."""
    spec = []
    for l in H["horaires"]:
        for d, f in plages(l):
            spec.append({"@type": "OpeningHoursSpecification", "dayOfWeek": SCHEMA_JOURS[l["jour"]], "opens": d, "closes": f})
    for x in H.get("exceptions", []):
        base = {"@type": "OpeningHoursSpecification", "validFrom": x["du"], "validThrough": x["au"]}
        if x.get("ferme"):
            spec.append({**base, "opens": "00:00", "closes": "00:00"})
        elif x.get("debut") and x.get("fin"):
            spec.append({**base, "opens": x["debut"], "closes": x["fin"]})
    return spec
