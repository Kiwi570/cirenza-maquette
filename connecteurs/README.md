# Les deux connexions du site final (Wix Headless)

Le site final reste notre code (GitHub, hébergé comme la maquette). Wix sert de coulisses : catalogue (Wix Stores),
commandes et paiements, contenus que Lisa modifie (Wix CMS). Deux connexions relient Wix aux outils de Lisa.

```
Artwork Archive ──(export CSV, script)──► Wix Stores ◄──(connexion Wix officielle)── creativehub
   (originaux)                              │   ▲                                    (tirages)
        ▲                                   │   │ commande payée
        └──── « Register Sale » par Lisa ◄──┘ mail automatique à Lisa (Wix Automations)
```

## Le site Wix headless (créé le 20 novembre 2026)

| | |
|---|---|
| Nom | Lisa Cirenza – Atelier |
| Identifiant du site (`metaSiteId`, à passer dans `WIX_SITE_ID`) | `385612fb-fc04-4da0-bcba-17cc37b81cd4` |
| Client OAuth du site (`client_id`, public, pour les pages) | `00356f7b-4ff3-44e8-b1ee-2ddc8cf6ca6e` |
| Tableau de bord | https://manage.wix.com/dashboard/385612fb-fc04-4da0-bcba-17cc37b81cd4/ |
| Produits | https://manage.wix.com/dashboard/385612fb-fc04-4da0-bcba-17cc37b81cd4/wix-stores/products |
| Commandes | https://manage.wix.com/dashboard/385612fb-fc04-4da0-bcba-17cc37b81cd4/ecom-platform/orders-list |
| Automatisations (mail de vente) | https://manage.wix.com/dashboard/385612fb-fc04-4da0-bcba-17cc37b81cd4/triggers |
| Adresse de la copie de la maquette | https://headless-znxwbqojlvv-kiwixteam-1409.wix-site-host.com |
| Médiathèque | https://manage.wix.com/dashboard/385612fb-fc04-4da0-bcba-17cc37b81cd4/media-manager |

- **Installé :** Wix Stores (catalogue V3), sans contenu de démonstration.
- **Région :** euros, fuseau Europe/Paris, région France. La langue du site reste l'anglais, version officielle.
- **Adresses autorisées pour le retour du paiement :** `https://cirenza-maquette.vercel.app`, `https://www.cirenza.com`,
  `https://cirenza.com`, `http://localhost:4173`.
- **Vérifié :** un visiteur anonyme obtient un jeton et lit le catalogue (vide pour l'instant).
- **Le site est dans le compte Wix de P'tit Kiwi.** Pour que Lisa connecte creativehub et gère ses commandes, l'ajouter
  comme collaboratrice, ou lui transférer le site au lancement.

## La maquette hébergée sur le site headless (20 novembre 2026)

La maquette v6 est en ligne à l'identique sur le site headless :
https://headless-znxwbqojlvv-kiwixteam-1409.wix-site-host.com.
Le site en ligne de Lisa (cirenza.com, « Lisa Cirenza -Artist ») n'est jamais modifié : on y fait seulement des lectures.

- **Pages :** les 63 pages en anglais et en français, en version « html » (liens relatifs en `.html`, comme dans
  `outils/generer.py --liens html`). Toujours en noindex, comme la maquette.
- **Images :** Wix limite les fichiers d'un site hébergé à 20 Mio. Les 440 images des œuvres et les photos sont donc dans
  la médiathèque du site, identiques octet pour octet à celles de la maquette. `medias-wix.tsv` donne l'image Wix de
  chaque fichier ; `assets/js/medias.js` en fait une table pour les images chargées par `site.js`.
- **Ce qui ne vient pas de la maquette :** les redirections et en-têtes de `vercel.json`, `robots.txt` et `sitemap.xml`.
  Un site Wix hébergé sert des fichiers, sans règles de redirection.

**Mettre à jour la copie :**
1. Copier le dépôt dans un dossier de travail, puis `python3 -I outils/generer.py <copie> --liens html`.
2. `python3 -I outils/copie_wix.py <copie>`. Une nouvelle image doit d'abord être importée dans la médiathèque et
   ajoutée à `medias-wix.tsv`.
3. Zipper le contenu du dossier et l'envoyer sur le site headless (Wix CLI ou outil Wix « drop »), jamais sur cirenza.com.

## Connexion 1 · Artwork Archive (originaux)

**Constat.** Artwork Archive n'a pas d'API publique. Son aide le dit pour les ventes faites ailleurs :
*« external purchases don't automatically update your inventory »*. Il faut donc marquer l'œuvre vendue à la main avec
« Register Sale ». L'export CSV est disponible sur toutes les offres (Pieces > New Report > Export to CSV).

### a. Catalogue : Artwork Archive vers Wix

Script : `artwork_archive_vers_wix.py` (Python 3, sans dépendance).

```
python3 -I connecteurs/artwork_archive_vers_wix.py export.csv              # essai : écrit plan-wix.json, n'envoie rien
WIX_API_KEY=… WIX_SITE_ID=… python3 -I connecteurs/artwork_archive_vers_wix.py export.csv --envoyer
```

Règles appliquées :
- **Œuvre disponible avec un prix :** produit Wix créé, stock 1. Une seule vente est donc possible en ligne.
- **Œuvre vendue, prêtée, réservée ou non disponible :** produit masqué. Il n'est jamais supprimé.
- **Œuvre redevenue disponible :** produit visible à nouveau.
- **Référence (SKU) :** `AA-<numéro d'inventaire Artwork Archive>`. C'est la clé entre les deux bases.

Testé en essai avec `exemple-export-artwork-archive.csv` (cinq lignes d'exemple tirées de l'index public) :
3 créations, 1 vendue ignorée, 1 sans prix ignorée. Les appels Wix suivent les recettes officielles de Catalog V3
(création en lot avec stock, recherche par SKU, PATCH de `visible` avec révision).

**Quand le lancer :** après chaque nouvelle œuvre et après chaque vente faite hors du site (galerie, Espace), pour
que le site masque l'œuvre. Une fois par semaine suffit en temps normal.

### b. Vente sur le site : Wix vers Lisa vers Artwork Archive

Une automatisation Wix (tableau de bord > Automatisations), sans code :
- **Déclencheur :** commande payée (eCommerce).
- **Condition :** une ligne de la commande a une référence qui commence par `AA-`.
- **Action :** e-mail à Lisa (art@cirenza.com).

Modèle du mail (anglais, Lisa peut le traduire) :

> **Sold on cirenza.com: {nom du produit}**
> Reference {SKU} · {prix} · buyer {nom}, {e-mail}.
> In Artwork Archive: search the inventory number after « AA- », open the piece and click **Register Sale**
> (buyer as a new contact, price, date).

Le stock Wix passe à 0 tout seul : l'œuvre ne peut pas être vendue deux fois en ligne.

## Connexion 2 · creativehub (tirages imprimés à la demande)

**Constat (aide de creativehub, 6 novembre 2026).** creativehub se connecte nativement à Wix, comme à Shopify,
Squarespace, WooCommerce et Big Cartel. Il faut que l'application Wix Stores soit installée sur le site. creativehub
reste la source des produits : il crée les produits et leurs variantes (avec leurs références) dans Wix Stores,
crée le profil de livraison, reçoit les commandes, imprime, expédie et renvoie le suivi à Wix.

**Le site étant en headless, la connexion native suffit.** Les commandes passent par le panier et le paiement Wix,
comme sur un site Wix classique. Notre code n'a qu'à afficher les produits que creativehub a poussés.

Étapes :
1. Lisa : dans creativehub, Settings > Connections > Wix, puis autoriser le site. Wix Stores doit être installé.
2. Lisa : créer ou retrouver ses produits dans creativehub, puis « Push » vers Wix.
3. P'tit Kiwi : afficher ces produits dans la boutique, filtre « Tirages ». La maquette montre le parcours : format,
   papier, référence (SKU) par variante. Les prix et références de la maquette sont des exemples ; les vrais viennent
   de creativehub.
4. **À tester avant le lancement :** une commande réelle à petit prix, de bout en bout (paiement Wix, commande reçue
   par creativehub, suivi renvoyé).

Plan B si la connexion native ne voyait pas les commandes du site headless : l'API publique de creativehub
(`api.creativehub.io`, jeton créé dans creativehub > Settings > API tokens). Une fonction serveur recevrait la
commande payée (action « requête HTTP » d'une automatisation Wix) et la transmettrait par SKU. Le jeton ne doit
jamais passer par e-mail ni être écrit dans le dépôt.

## Ce que Lisa doit fournir

- **Artwork Archive :** l'export CSV. Les numéros d'inventaire doivent être remplis : ce sont les futures références.
- **creativehub :** l'accès au compte, ou la connexion faite par elle-même en visio avec P'tit Kiwi.
- **Wix :** un accès collaborateur au site Wix qui servira de coulisses (Wix Stores installé).

Sources : aide d'Artwork Archive (« Add an External Payment Link », « How to Register a Sale », « Exporting Your Data ») ;
aide de creativehub (« Which store platforms can I connect? », « Where do my products come from », « Can I connect
creativehub to a custom-coded / bespoke website? », « Shipping rates on connected stores »).
