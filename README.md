# Lisa Cirenza · maquette v7 (direction « Strates », série « A Record of Time »)

Site statique (HTML, CSS, JavaScript), sans étape de construction, prêt pour Vercel.
Adresse de la maquette : https://cirenza-maquette.vercel.app

- Anglais à la racine (version officielle), français sous `/fr/`.
- 53 pages : accueil, œuvres (A Record of Time en tête, puis l'Archive), l'artiste, notes d'atelier, parcours, presse, l'Espace Créa-Tea-Vité, cours privés sur mesure, cours (hors navigation), événements privés, retraites (A Creative Pause, Painting in Paradise, Alpine Encaustics), boutique, contact, éditeur des horaires (outil de la maquette, hors menu), 404.
- Site final : **Wix Headless**. Notre code reste la vitrine (GitHub, hébergement comme la maquette, branches de prévisualisation et retour en arrière inchangés) ; Wix sert de coulisses (Wix Stores, paiements, collections CMS que Lisa modifie).
- `vercel.json` : adresses propres (`cleanUrls`), noindex (`X-Robots-Tag`), en-têtes de sécurité de base, redirection des anciennes adresses (Molten Magic et Alpine Pause vers Alpine Encaustics, l'ancienne salle récente vers A Record of Time). Jamais de `X-Frame-Options` : la maquette s'affiche dans le module Wix « Intégrer un site ».
- Polices hébergées avec le site (`assets/polices`) : Fraunces et IBM Plex Mono, licence SIL OFL.
- Formulaires, paniers et paiements simulés : rien n'est envoyé ni débité.

## Une maison, deux côtés (réunion de cadrage)

Un seul site, deux univers clairement séparés, une couleur chacun :

| | Atelier · Lisa Cirenza Fine Art | Espace Créa-Tea-Vité |
|---|---|---|
| Forme | artiste-auteur, SIRET 888 534 534 00019 | SAS, SIRET 989 397 146 00014 |
| Pages | Œuvres et salles, L'artiste, Notes d'atelier, Parcours, Presse | L'Espace, Cours privés, Retraites, Événements privés |
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

## v7 · deuxième liste de Lisa (20 novembre 2026)

Voir `REPONSES-LISA-2.md` (réponses point par point, en anglais, à envoyer à Lisa).
- **Portfolio** (ex-Works) avec « Enquire about this work » vers atelier@cirenza.com, sans prix ; **Commissions and Available Works** (ex-boutique) avec un bloc Commandes en tête et un prix sur chaque œuvre disponible.
- **Bouton « Read the story and watch the video »** par œuvre, seulement si un lien existe (`outils/contenu.py`, `HISTOIRES`).
- **Devises** (EUR, GBP, USD, JPY) dans le pied de page, prix indicatifs, paiement en euros (`DEVISES`).
- **Cookies** : choix gardé 6 mois ; vignette « hébergée par Vimeo / Wix » avec « Accept and play » sur chaque vidéo.
- **Pages légales** (EN/FR) : mentions, confidentialité, cookies, conditions d'utilisation, avec les faits vérifiés.
- **Recherche** plus visible : libellé dans l'en-tête, champ en tête du menu, lien dans le pied de page.

## v6 · retours de Lisa du 20 novembre 2026

Voir `REPONSES-LISA.md` (réponses point par point, à envoyer à Lisa) et `CHANGELOG.md`. Architecture retenue : un seul site (ce code), deux coulisses Wix.
- **Espace (SAS Atelier Truffle)** : le site Wix actuel de cirenza.com, avec ses formulaires d'inscription (juin `2ba9da25-…`, septembre `a0aeff52-…`), Wix Payments (compte Stripe de la SAS), Bookings, contacts, automatisations, blog (35 articles) et traductions.
- **Artiste (Lisa Cirenza, artiste-auteur)** : le site Wix headless créé le 20 novembre (`385612fb-…`, Wix Stores), pour Available Works, tirages creativehub et éditions, avec le second compte Stripe.

## v5 · ce qui a été ajouté après la réunion de suivi (novembre 2026)

- **Horaires, une seule source** : `assets/data/horaires.json` (semaine, fermetures, horaires spéciaux, annonces datées), lu par le générateur et relu par le navigateur à chaque visite. Éditeur pour Lisa : `/manage/opening-hours` (`/fr/gestion/horaires`), avec aperçu sur tout le site dans son navigateur et téléchargement du fichier. Sur le site final : deux collections Wix CMS, « Horaires » et « Exceptions », mêmes champs.
- **SEO et GEO** : titres et descriptions uniques, adresses de référence, `hreflang`, données structurées schema.org, `sitemap.xml`, `robots.txt`, `llms.txt`, FAQ des retraites, 57 redirections de l'ancien site Wix. Détail et liste du jour du lancement : `AUDIT-SEO-GEO.md`.
- **Retraites** : places restantes sur les cartes et les fiches (chiffres d'exemple), FAQ « Avant de réserver ».
- **Formulaire de contact** : champs propres à chaque demande (retraite, cours privé, événement), envoyés vers la bonne adresse (atelier ou Espace) en lignes « Libellé : valeur », lisibles par Lisa comme par un futur agent.
- **Cours privés** : catégories, expériences, durée, groupe et tarif par expérience, déroulé pour les hôtels et conciergeries (tout en exemples, en attendant la synthèse de Lisa).
- **Presse** : le podcast (lien à venir, lecteur chargé au clic).
- **Boutique** : tirages creativehub avec format, papier et référence (SKU) par variante (prix d'exemple).
- **Langue** : invitation discrète vers l'autre langue selon le navigateur, une seule fois, sans redirection.
- **Connexions** : `connecteurs/README.md` (Artwork Archive vers Wix par export CSV et script, mail de vente à Lisa, creativehub par sa connexion Wix officielle).

### Exemples à remplacer (marqués « example » sur le site)

| Où | Quoi | Fichier |
|---|---|---|
| Horaires | Fermeture de Noël et horaires des vacances | `assets/data/horaires.json` (`"exemple": true`) |
| Retraites | Places réservées (moitié pour juin et septembre, réunion) | `outils/retraites.py`, `PLACES` |
| Cours privés | Durées, groupes, tarifs, déroulé, tarifs partenaires | `outils/contenu.py`, `OFFRE_COURS_PRIVES`, `ETAPES_COURS_PRIVES` |
| Tirages | Formats, papiers, prix et références | `outils/generer.py`, `CH_FORMATS`, `CH_PAPIERS` (les vrais viennent de creativehub) |
| Presse | Podcast : émission, titre, lien | `outils/contenu.py`, `PRESSE` |

## Revenir en arrière

Chaque version publiée est gardée dans une branche du dépôt : `archive/v2`, `archive/v3`, `archive/v4`. Vercel garde aussi chaque déploiement.
- Le plus rapide : Vercel, onglet Deployments, choisir le déploiement voulu, puis « Promote to Production ».
- Ou dans GitHub : remettre `main` sur la branche d'archive voulue.

## Sources

- **v4** : « cirenza.com — content and design brief », de Lisa à Charles (novembre 2026) : source unique des textes de l'artiste (positionnement, déclaration, bios, notes d'atelier, CV sélectif, presse, retraites et prix). Textes anglais repris mot pour mot.
- **v3** : nouvelle page d'accueil de cirenza.com (novembre 2026), pages des retraites, Wax Fusion n° XIV (automne 2026, p. 18 – 31), article M2616 (à paraître), vidéo « Un petit tour de l'Espace » (Vimeo, chargée au clic), dossier de photos du 5 novembre 2026.

## Réponses aux questions de Lisa (brief, « My questions for you »)

- **Les éditions de collection dans la même boutique, avec leur filtre ou leur page ?** Oui. Elles sont vendues par l'atelier, donc sur le même compte Stripe que les œuvres. La maquette les montre dans la boutique (section « Collectors' editions », filtre de l'atelier) ; sur le site final, une collection « Collectors' editions » dans Wix Stores, avec sa propre page.
- **Quel format et quel hébergement pour les vidéos ?** Des clips courts (30 à 90 s) en MP4 H.264 1080p, hébergés sur Vimeo (déjà utilisé pour la visite de l'Espace), avec les sous-titres français en fichier `.vtt` ajouté à la vidéo ; le lecteur ne se charge qu'au clic, comme dans la maquette, pour que la page reste rapide. Pour de très courtes boucles muettes de procédé (chaleur, cire, eau), un MP4 de 2 à 4 Mo servi avec le site suffit.
- **Mettre à jour « In the studio now » soi-même en une ou deux minutes ?** Oui, sur le site final : une collection Wix CMS « À l'atelier » (une photo, une phrase, l'œuvre liée) que Lisa modifie depuis son téléphone. Dans la maquette, ce bloc se règle dans `outils/contenu.py` (`SERIE_ACTUELLE`) et `outils/catalogue.py` (groupe « On my easel »).
- **Est-ce que cela change le devis ?** Réponse de Charles. Ajouts de la v4 par rapport au cadrage : pages Studio notes, Private bespoke courses et A Creative Pause, grille de prix par chambre, éditions de collection en boutique, annonces de fermeture, CV restructuré, deux listes de lettre d'information.

## À fournir par Lisa (à compléter)

- **Depuis la réunion de suivi :** le lien du podcast (émission, titre), les articles M2616 et Wax Fusion parus, les horaires définitifs, la synthèse des cours privés (catégories, expériences, tarifs), l'accès à creativehub (ou la connexion faite ensemble), les chiffres de remplissage des retraites.
- **Artwork Archive (priorité)** : l'export de l'inventaire (Pieces, tout sélectionner, Export, CSV ou Excel), idéalement avec les images. Il donne titres, dimensions, années, techniques et prix des œuvres récentes (affichées « titre à compléter »), des œuvres sur le chevalet et des petites encaustiques de la boutique (affichées « photo à venir »).
- **Images annoncées dans le brief** : la montagne à facettes de l'ouverture (une œuvre récente la remplace en attendant), le visage qui se dissout dans l'eau et l'écume (déclaration), l'abstraction bleu pâle griffée et la montagne brumeuse sur l'eau sombre, Cool Reflections en entier et en détail à la lumière du jour, les photos d'expédition du champ de glace de Juneau, les blocs d'acrylique photographiés comme des objets, l'exposition des taxis de Londres.
- **PDF** : CV complet et dossier de presse (liens « à venir » sur la page de l'artiste).
- **A Creative Pause** : le programme jour par jour (la page annonce « programme à venir »).
- **Alpine Encaustics** : la maquette reprend les textes de l'ancienne page Alpine Pause (pourquoi ralentir, le poulet, la sauce et les épices, six jours) : à confirmer ou à remplacer.
- **À vérifier dans le brief** :
  - Financial Times : le brief cite « NYC Commuters » comme image d'ouverture de l'article, la légende de l'article dit « NYC Contrasts ».
  - Maisons et Jardins : 2021 dans le brief ; la version en ligne de l'article est datée de mai 2022.
  - Salles de bains : la grille dit « private shower and washbasin », la petite ligne explique « Private bathroom » ; harmoniser le libellé.
  - Wax Fusion et M2616 ne sont pas dans la liste de presse du brief ; la maquette les garde en tête, comme les plus récents.
  - Orthographe : « Jean-Pierre Braz » (brief) ou « Brazs » (ancien site).
  - BBC : titre et année du documentaire.
- **Boutique** : partenaire d'impression (creativehub), papiers et prix de chaque tirage ; prix des éditions de collection ; transporteur et tarifs ; politique de prix des originaux.
- **Cours privés** : durées, tailles de groupe et tarifs partenaires.
- **Mentions légales, politique de confidentialité, conditions générales de vente** pour chacune des deux entités ; hébergeur ; assurances.
- **Lettre d'information** : les deux listes Mailchimp (anglaise : collectionneurs et retraites ; française : l'Espace).
- **Prochaine exposition** à l'Espace et horaires définitifs (19 h ou 18 h 30).

## Modifier les contenus

Les textes et données sont dans `outils/` (exclu du déploiement) : `contenu.py`, `retraites.py`, `catalogue.py`.
Puis, depuis le dossier du site :

```
python3 -I outils/images_partage.py .
python3 -I outils/generer.py . --liens propres
```

Fermetures exceptionnelles : ajouter une ligne à `ANNONCES` dans `outils/contenu.py` (dates de début et de fin, texte anglais et français) ; elle s'affiche en haut de toutes les pages pendant ces dates seulement.

Nouvelles images : les déposer dans un dossier `oeuvres/<id>.jpg` et `photos/<dossier>/<nom>.jpg`, les déclarer dans `outils/ajouts_v3.json` (ou un nouveau manifeste), puis `python3 -I outils/ajouter_medias.py <dossier> .`. Les œuvres ne sont jamais recadrées ni retouchées : seul le redimensionnement est appliqué.

## À la mise en ligne définitive

- Retirer : noindex (balise `robots` des pages et `X-Robots-Tag` de `vercel.json`), mention « Maquette », formulaires, paniers et paiements simulés, mentions « à compléter ».
- Brancher : Wix (CMS, Stores, Bookings), les deux comptes Stripe, l'export Artwork Archive, la lettre d'information.
- Garder : les crédits des photos, la mention « Photo d'ambiance » sur les images d'ambiance générées.
