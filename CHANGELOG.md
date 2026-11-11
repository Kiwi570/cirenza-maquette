# Historique

## v3 · 11 novembre 2026 · retours de Lisa

Construit en comparant la v2 (commit 4cbf194) et la v3, fichier par fichier.

**Une maison, deux côtés**
- Bascule « Atelier | Espace » dans l'en-tête et le menu ; liens et couleur selon le côté (ambre pour l'atelier de l'artiste-auteur, bleu pour l'Espace en SAS).
- Pied de page à deux colonnes : forme juridique, SIRET, courriel et réseaux de chaque entité ; « Mentions légales » et « Politique de confidentialité » en texte simple, à compléter.
- Nouvelle page Boutique (`/shop`, `/fr/boutique`) : comptoir de l'atelier (15 éditions limitées, 45 originaux sur demande, filtre gardé dans l'adresse) et comptoir de l'Espace (séances d'atelier ouvert à 30 €, places de retraite sur demande). Deux paniers, deux paiements simulés (Stripe 1 et Stripe 2), tampon de reçu, compteurs dans l'en-tête, l'œuvre s'envole vers le bon panier.

**Accueil, avec les mots de la nouvelle page d'accueil de Lisa**
- Accroche « Painting light, water, rock and time » ; œuvre d'ouverture : celle de son accueil (glacier qui se jette dans la mer).
- Section « Lire le temps » : l'Anthropocène, « In a melting world, I paint hope as light » (balayage de lumière), photos de Lisa à 4 ans, à 17 ans sur le champ de glace de Juneau, et aujourd'hui.
- « Sous la surface » reprend ses mots de Wax Fusion (le paradoxe, l'antidote au regard pressé).
- Nouvelle section « Portes d'entrée » : Collectionner, Créer, Visiter, Réunir (les publics de la réunion), « Ici, chacun trouve sa porte d'entrée » (M2616) ; les deux vantaux s'ouvrent au défilement.
- Presse : Wax Fusion et M2616 en tête. Retraites : Painting in Paradise et Autumn Alpine Pause.

**Œuvres**
- Nouvelle salle « Light, Water, Rock and Time » : 11 œuvres récentes du dossier de photos (titres à compléter depuis Artwork Archive).
- Titres et techniques tirés de Wax Fusion : Emergence (100 × 70 cm, nouvelle photo en haute définition, loupe), Seaside Village and the Pink Flowers (100 × 70 × 4 cm), Stand Tall and Face the Light (108 × 108 cm), Rose Coloured Glasses ; Dream Big devient « peinture numérique en couches sur Dibond ».
- Artwork Archive comme base maîtresse : `outils/artwork_archive.py` fusionne l'export CSV (titres, dimensions, années, techniques, statuts, prix masqués par défaut).
- Index public d'Artwork Archive (profil lisa-cirenza, lu à travers un moteur de recherche) : 15 fiches consignées dans `outils/artwork_archive_index.json` ; « The Grunge and the Glow of Havana » passe en vendue (et quitte la boutique), « Bank » datée de 2016.
- Where Do I Begin? : image confirmée (c'est celle que Lisa affiche avec ce titre sur sa nouvelle page d'accueil), mention « image à confirmer » retirée.

**L'artiste, presse, Espace, cours**
- L'artiste : section « Avec ses mots » (Wax Fusion, M2616) ; la photo réelle de Lisa à 17 ans remplace l'évocation générée ; nouvelle couche « À 50 ans, le grand saut ».
- Presse : dossier Wax Fusion (couverture, citations, lien vers le numéro à la p. 18) et article M2616 (à paraître).
- L'Espace : « De L'Ourson à Créa-Tea-Vité » (rénovation pensée par Lisa, cloche du Népal, piano, démonstrations, jeunes artistes, JO 2030) et la vidéo de visite, chargée au clic ; l'exposition La Gravité de la Grâce est présentée comme terminée.
- Cours : Painting with Fire 6 (cours en ligne, Essence of Mulranny) et cours privé en plein air (à compléter).
- Parcours : Salon d'Automne 2026 et La Gravité de la Grâce ajoutés à 2026.

**Retraites**
- Autumn Alpine Pause (6 – 11 septembre 2027, 8 participants, 2 450 – 3 295 €) remplace Molten Magic : pourquoi une pause, le poulet, la sauce et les épices, le carnet de recettes, deux recettes d'atelier, six jours, témoignages ; les anciennes adresses redirigent.
- Painting in Paradise : nouveaux prix (2 450 – 3 295 €), navettes, petit-déjeuner à l'atelier, jour 6, nouveaux témoignages, « A bit more about me ».

**Technique**
- Version 3 (`?v=3`), date du jour calculée à la génération.
- noindex dans chaque page et dans `vercel.json`, en-têtes nosniff et Referrer-Policy, plus de règle Cache-Control, `robots.txt` sans blocage.
- Images de partage 1200 × 630 en JPG, une par page et par langue (`assets/partage`), adresses absolues.
- Textes d'au moins 12 px partout.
- Nouveaux outils : `ajouter_medias.py` (ajout d'images sans tout repréparer), `medias_outils.py`, `images_partage.py`, `artwork_archive.py`.

## v2

- « Voir au mur » à l'échelle réelle, grattage de cire, six bandes de photos réelles qui glissent au défilement.

## v1

- Maquette « Strates » : 41 pages, anglais et français, salles d'exposition, fiche d'œuvre avec loupe, retraites, Espace.
