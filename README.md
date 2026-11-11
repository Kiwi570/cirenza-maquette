# Lisa Cirenza · maquette v3 (direction « Strates »)

Site statique (HTML, CSS, JavaScript), sans étape de construction, prêt pour Vercel.
Adresse de la maquette : https://cirenza-maquette.vercel.app

- Anglais à la racine (version officielle), français sous `/fr/`.
- 45 pages : accueil, œuvres et 9 salles, l'artiste, parcours, presse, l'Espace Créa-Tea-Vité, cours, événements privés, retraites (Painting in Paradise, Autumn Alpine Pause), boutique, contact, 404.
- `vercel.json` : adresses propres (`cleanUrls`), noindex (`X-Robots-Tag`), en-têtes de sécurité de base, redirection des anciennes adresses Molten Magic vers Alpine Pause. Jamais de `X-Frame-Options` : la maquette s'affiche dans le module Wix « Intégrer un site ».
- Polices hébergées avec le site (`assets/polices`) : Fraunces et IBM Plex Mono, licence SIL OFL.
- Formulaires, paniers et paiements simulés : rien n'est envoyé ni débité.

## Une maison, deux côtés (réunion de cadrage)

Un seul site, deux univers clairement séparés, une couleur chacun :

| | Atelier · Lisa Cirenza Fine Art | Espace Créa-Tea-Vité |
|---|---|---|
| Forme | artiste-auteur, SIRET 888 534 534 00019 | SAS, SIRET 989 397 146 00014 |
| Pages | Œuvres et salles, L'artiste, Parcours, Presse | L'Espace, Cours, Retraites, Événements privés |
| Vend | originaux, éditions limitées (impression à la demande), commandes | séances d'atelier, places de retraite, boutique (matériel, cadeaux) |
| Paiement | compte Stripe n° 1 | compte Stripe n° 2 |
| Couleur | ambre de cire `#8a4f0e` | bleu des murs de l'Espace `#24486a` |

- En-tête : bascule « Atelier | Espace » ; les liens changent selon le côté où l'on se trouve.
- Pied de page : deux colonnes, une par entité, avec forme juridique, SIRET, courriel et réseaux propres.
- Boutique : deux comptoirs, deux paniers, deux encaissements. Une commande ne mélange jamais les deux entités. L'œuvre ajoutée s'envole vers le panier de son comptoir.

### Architecture proposée pour le site final (headless)

- **Wix** reste l'outil d'administration : textes, pages, retraites, cours, agenda (Wix CMS), boutique (Wix Stores), réservations (Wix Bookings). Lisa modifie les contenus elle-même ; la mise en page reste dans le code (dépôt GitHub au nom de Lisa).
- **Artwork Archive** reste la base maîtresse des œuvres (voir plus bas).
- **Domaine** : reste chez GoDaddy, pointé vers l'hébergement du site.
- **Deux comptes Stripe** : à vérifier dans la documentation Wix avant de choisir le montage, car un site Wix encaisse en principe sur un seul compte par moyen de paiement. Deux pistes : Wix Stores sur le compte de l'atelier et paiements Stripe directs (Checkout ou liens de paiement) pour l'Espace ; ou deux projets Wix headless, un par entité, derrière le même site.
- **SumUp** : terminaux de l'Espace, sans lien avec le site.

## Base des œuvres : Artwork Archive

Artwork Archive (https://www.artworkarchive.com/pieces) est la base de référence : titres, dimensions, années, techniques, prix, disponibilités et numéros d'inventaire y sont tenus par Lisa. `outils/catalogue.py` n'en est que le relevé de travail.

1. Dans Artwork Archive : Pieces, puis Export, au format CSV.
2. `python3 -I outils/artwork_archive.py export.csv --rapport` : rapproche chaque pièce par numéro d'inventaire (table `CORRESPONDANCES` du script) ou par titre, et écrit `outils/artwork_archive.json`.
3. `python3 -I outils/generer.py . --liens propres` : les données d'Artwork Archive l'emportent sur le relevé.

Les prix ne s'affichent que si `AFFICHER_PRIX = True` dans `outils/generer.py` (décision de Lisa) ; sinon « prix sur demande ».

**État au 11 novembre 2026.** La page privée (`/pieces`) demande la connexion de Lisa. Son profil public, https://www.artworkarchive.com/profile/lisa-cirenza (environ 40 œuvres), est protégé par une vérification anti-robot : il ne peut pas être lu par un script, et elle n'a pas été contournée. Ce que l'index d'un moteur de recherche en montre est consigné dans `outils/artwork_archive_index.json` (15 fiches, sans images) :
- appliqué au site : « The Grunge and the Glow of Havana » est vendue (titre exact d'Artwork Archive, retirée de la boutique) ; « Bank » est de 2016 (prix connu, non affiché) ;
- absentes du site et à importer avec l'export : Where the Mountains Breathe (2025, encaustique sur papier, 34 × 25,5 cm, 145 €), Light Across the Thaw (encaustique sur panneau, 30 × 30 cm, 240 €), Blissful Light (2024, 200 €), Doucement Entrelacés (2024, 80 €), The Silence of Thawing Waters, Talking to the Wild (2023), The Blues (2021), Lost in the trees, and missing the Forest (2019), Cycles, Heat Waves, Chasing the Ephemeral (240 €), UH-Huh (125 €), A moment in Havanna (150 €) ;
- certaines de ces œuvres sont sans doute parmi les 11 œuvres récentes sans titre de la maquette, mais sans les images rien ne permet de les rapprocher : aucun titre n'a été attribué au hasard.

## Sources de la v3

- Nouvelle page d'accueil de cirenza.com (novembre 2026) : « Painting light, water, rock and time », l'Anthropocène, « In a melting world, I paint hope as light », « I create to connect people… », photos « Me, learning to see » et « 17 year old me ».
- Pages actuelles des retraites : Painting in Paradise (prix, jour 6, navettes, témoignages) et Autumn Alpine Pause (6 – 11 septembre 2027), qui remplace Molten Magic.
- Wax Fusion, International Encaustic Artists, automne 2026, n° XIV, « Beyond the Surface » (p. 18 – 31), écrit par Lisa : citations, titres et techniques d'Emergence, Seaside Village and the Pink Flowers, Stand Tall and Face the Light, Rose Coloured Glasses, Dream Big ; cours en ligne Painting with Fire 6.
- Article M2616 (La Clusaz, à paraître début décembre 2026) : L'Ourson, la cloche du Népal, le piano, Salon d'Automne 2026, citations en français.
- Vidéo « Un petit tour de l'Espace » (Vimeo, non répertoriée) : chargée seulement au clic.
- Dossier de photos du 5 novembre 2026 : 11 œuvres récentes (salle « Light, Water, Rock and Time »), Emergence en haute définition, détails d'atelier.

## À fournir par Lisa (à compléter)

- **Artwork Archive (priorité)** : l'export de l'inventaire (Pieces, tout sélectionner, Export, CSV ou Excel), idéalement avec les images ; à défaut, des captures ou un PDF du profil public. Il donne les titres, dimensions, années et techniques des 11 œuvres récentes (affichées « titre à compléter ») et les petites encaustiques à vendre en boutique.
- **Google Doc (priorité)** des détails de la retraite : le lien répond « connexion requise » (erreur 401) sous toutes ses formes. Le passer en « Tous les utilisateurs disposant du lien : lecteur », ou envoyer son texte ou un export PDF.
- **Retraite de septembre** : nom définitif et équipe (le site dit « Autumn Alpine Pause » avec Lisa seule ; Wax Fusion annonce « Molten Mountains », co-animée avec Isabelle Gaborit).
- **Entité qui vend les retraites** (pour le bon compte Stripe) : la page Painting in Paradise indique Lisa Cirenza, 74290 Talloires, SIRET de l'atelier ; la page Alpine Pause indique l'Espace (SAS).
- **Painting in Paradise** : taille du groupe (« 10 au maximum » ou « cohorte de 6 ») ; la FAQ en PDF cite encore « le 31 août ».
- **Boutique** : partenaire d'impression à la demande, papiers, prix de chaque édition ; transporteur (Boxtal évoqué) et tarifs ; sélection de la boutique de l'Espace à vendre en ligne ; politique de prix des originaux.
- **Mentions légales, politique de confidentialité, conditions générales de vente** pour chacune des deux entités ; hébergeur ; assurances.
- **M2616** : nom exact du magazine, page et lien à la parution.
- **Horaires** : la version française du site actuel indique 19 h, l'anglaise 18 h 30.
- **Prochaine exposition** à l'Espace (La Gravité de la Grâce est terminée depuis le 31 octobre 2026).
- **Cours privé en plein air** : la page du site actuel est encore vide.
- **Photo de Lisa à 17 ans** : l'original (la maquette utilise un recadrage du bandeau du site, en basse définition).
- **Vidéo** : la version sous-titrée en anglais quand elle sera prête.

## Modifier les contenus

Les textes et données sont dans `outils/` (exclu du déploiement) : `contenu.py`, `retraites.py`, `catalogue.py`.
Puis, depuis le dossier du site :

```
python3 -I outils/images_partage.py .
python3 -I outils/generer.py . --liens propres
```

Nouvelles images : les déposer dans un dossier `oeuvres/<id>.jpg` et `photos/<dossier>/<nom>.jpg`, les déclarer dans `outils/ajouts_v3.json` (ou un nouveau manifeste), puis `python3 -I outils/ajouter_medias.py <dossier> .`. Les œuvres ne sont jamais recadrées ni retouchées : seul le redimensionnement est appliqué.

## À la mise en ligne définitive

- Retirer : noindex (balise `robots` des pages et `X-Robots-Tag` de `vercel.json`), mention « Maquette », formulaires, paniers et paiements simulés, mentions « à compléter ».
- Brancher : Wix (CMS, Stores, Bookings), les deux comptes Stripe, l'export Artwork Archive, la lettre d'information.
- Garder : les crédits des photos, la mention « Photo d'ambiance » sur les images d'ambiance générées.
