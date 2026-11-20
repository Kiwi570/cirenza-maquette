"""Connexion 1 · Artwork Archive -> Wix Stores (site final en Wix Headless).

Artwork Archive n'a pas d'API publique (aide officielle, vérifiée le 20 novembre 2026). Lisa exporte donc
son inventaire en CSV (Pieces > New Report > Export to CSV) et ce script met le catalogue Wix à jour :

  - une œuvre disponible avec un prix  -> produit Wix (création ou mise à jour du prix), stock 1 ;
  - une œuvre vendue ou non disponible -> produit masqué (jamais supprimé, la page reste dans l'historique) ;
  - une œuvre redevenue disponible     -> produit à nouveau visible.

La clé qui relie les deux bases est la référence (SKU) : « AA-<numéro d'inventaire Artwork Archive> ».
C'est elle que le mail de vente rappelle à Lisa (voir vente-vers-artwork-archive.md).

Usage :
  python3 -I connecteurs/artwork_archive_vers_wix.py <export.csv>             essai : rien n'est envoyé, le plan est écrit
  python3 -I connecteurs/artwork_archive_vers_wix.py <export.csv> --envoyer   applique le plan sur le site Wix

Pour --envoyer : variables d'environnement WIX_API_KEY (clé API du compte Wix, droits Wix Stores) et
WIX_SITE_ID. Ne jamais écrire la clé dans un fichier du dépôt.
Appels utilisés (Catalog V3, recettes officielles Wix « Create Product », « Find Products », « Update Product ») :
  GET   /stores/v3/provision/version
  POST  /stores/v3/products/search                         (par SKU, filtre $matchItems)
  POST  /stores/v3/bulk/products-with-inventory/create     (jusqu'à 100 produits par appel)
  GET   /stores/v3/products/{id}                           (révision avant modification)
  PATCH /stores/v3/products/{id}                           (visible, prix)
"""
import csv
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI.parent / "outils"))
import artwork_archive as AA  # noqa: E402  (mêmes colonnes et mêmes statuts que l'import du site)

API = "https://www.wixapis.com"
VENDABLES = {"disponible"}
MASQUES = {"vendu", "non-disponible", "reserve", "en-pret"}


def sku(inventaire, titre):
    base = inventaire or AA.norme(titre).replace(" ", "-")[:40]
    return "AA-" + re.sub(r"[^A-Za-z0-9-]+", "-", base).strip("-").upper()


def lire_export(chemin):
    lignes = list(csv.DictReader(open(chemin, encoding="utf-8-sig", newline="")))
    pieces = []
    for ligne in lignes:
        titre = AA.valeur(ligne, "titre")
        if not titre:
            continue
        inv = AA.valeur(ligne, "inventaire")
        unite = AA.valeur(ligne, "unite")
        h, l, p = (AA.en_cm(AA.nombre(AA.valeur(ligne, k)), unite) for k in ("hauteur", "largeur", "profondeur"))
        an = re.search(r"(19|20)\d\d", AA.valeur(ligne, "annee") or "")
        pieces.append({
            "sku": sku(inv, titre), "inventaire": inv, "titre": titre,
            "technique": AA.valeur(ligne, "technique"), "annee": an.group() if an else None,
            "dims": [x for x in (h, l, p) if x], "prix": AA.nombre(AA.valeur(ligne, "prix")),
            "devise": (AA.valeur(ligne, "devise") or "EUR").upper(),
            "statut": AA.STATUTS.get((AA.valeur(ligne, "statut") or "").lower(), "inconnu"),
        })
    return pieces


def description(p):
    morceaux = [p["technique"], " × ".join(f"{x:g}" for x in p["dims"]) + " cm" if p["dims"] else None, p["annee"],
                f"Artwork Archive {p['inventaire']}" if p["inventaire"] else None]
    return " · ".join(m for m in morceaux if m)


def produit_wix(p):
    """Produit physique Catalog V3, une variante, stock suivi à 1 (une œuvre originale est unique)."""
    return {
        "name": p["titre"],
        "productType": "PHYSICAL",
        "physicalProperties": {},
        "plainDescription": description(p),
        "visible": True,
        "variantsInfo": {"variants": [{
            "sku": p["sku"],
            "price": {"actualPrice": {"amount": f"{p['prix']:.2f}"}},
            "inventoryItem": {"quantity": 1},
            "physicalProperties": {},
            "visible": True,
        }]},
    }


class Wix:
    def __init__(self, cle, site):
        self.entetes = {"Authorization": cle, "wix-site-id": site, "Content-Type": "application/json"}

    def appel(self, methode, chemin, corps=None):
        donnees = json.dumps(corps).encode() if corps is not None else None
        req = urllib.request.Request(API + chemin, data=donnees, method=methode, headers=self.entetes)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            raise SystemExit(f"Wix {methode} {chemin} : {e.code} {e.read()[:400]!r}")

    def par_sku(self, s):
        r = self.appel("POST", "/stores/v3/products/search", {"search": {"filter": {"variantsInfo.variants": {"$matchItems": [{"sku": s}]}}}})
        return (r.get("products") or [None])[0]


def plan(pieces, existants):
    """existants : {sku: {"id", "visible"}} lus sur Wix (vide en mode essai)."""
    actions = {"creer": [], "masquer": [], "montrer": [], "ignorer": []}
    for p in pieces:
        deja = existants.get(p["sku"])
        if p["statut"] in VENDABLES and p["prix"]:
            if not deja:
                actions["creer"].append(p)
            elif not deja.get("visible", True):
                actions["montrer"].append({**p, "id": deja["id"]})
        elif p["statut"] in MASQUES and deja and deja.get("visible", True):
            actions["masquer"].append({**p, "id": deja["id"]})
        else:
            raison = "pas de prix" if p["statut"] in VENDABLES else f"statut {p['statut']}"
            actions["ignorer"].append({**p, "raison": raison})
    return actions


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    envoyer = "--envoyer" in sys.argv
    pieces = lire_export(sys.argv[1])
    existants, wix = {}, None
    if envoyer:
        cle, site = os.environ.get("WIX_API_KEY"), os.environ.get("WIX_SITE_ID")
        if not cle or not site:
            raise SystemExit("WIX_API_KEY et WIX_SITE_ID sont nécessaires pour --envoyer.")
        wix = Wix(cle, site)
        version = wix.appel("GET", "/stores/v3/provision/version").get("catalogVersion")
        if version != "V3_CATALOG":
            raise SystemExit(f"Catalogue Wix {version} : ce script suit Catalog V3.")
        for p in pieces:
            trouve = wix.par_sku(p["sku"])
            if trouve:
                existants[p["sku"]] = {"id": trouve["id"], "visible": trouve.get("visible", True)}
    a = plan(pieces, existants)
    resume = {k: [{"sku": x["sku"], "titre": x["titre"], **({"raison": x["raison"]} if "raison" in x else {})} for x in v] for k, v in a.items()}
    (ICI / "plan-wix.json").write_text(json.dumps({"produits_a_creer": [produit_wix(p) for p in a["creer"]], "resume": resume}, ensure_ascii=False, indent=1) + "\n")
    for k, v in resume.items():
        print(f"{k:8} {len(v):3}  " + ", ".join(x["titre"] for x in v[:6]) + (" …" if len(v) > 6 else ""))
    if not envoyer:
        print("Essai : rien n'a été envoyé. Plan détaillé : connecteurs/plan-wix.json")
        return
    for i in range(0, len(a["creer"]), 100):
        lot = [produit_wix(p) for p in a["creer"][i:i + 100]]
        r = wix.appel("POST", "/stores/v3/bulk/products-with-inventory/create", {"products": lot, "returnEntity": False})
        pm, im = r.get("productResults", {}).get("bulkActionMetadata", {}), r.get("inventoryResults", {}).get("bulkActionMetadata", {})
        erreur = r.get("inventoryResults", {}).get("error")
        print(f"création : {pm.get('totalSuccesses', 0)} produits, {pm.get('totalFailures', 0)} échecs ; stock : {im.get('totalSuccesses', 0)} ; erreur de stock : {erreur}")
    for cle_action, visible in (("masquer", False), ("montrer", True)):
        for p in a[cle_action]:
            rev = wix.appel("GET", f"/stores/v3/products/{p['id']}")["product"]["revision"]
            r = wix.appel("PATCH", f"/stores/v3/products/{p['id']}", {"product": {"id": p["id"], "revision": rev, "visible": visible}})
            print(f"{cle_action} : {p['titre']} -> visible={r['product'].get('visible')}")


if __name__ == "__main__":
    main()
