# Historique

## v6 · 20 novembre 2026 · retours de Lisa (courriel du 20 novembre)

Réponses point par point : `REPONSES-LISA.md`.

**Retiré** : anciens postes en finance et en conseil (y compris dans les sources), retraite de mai 2027 (A Creative Pause), « places restantes », lien vers l'éditeur d'horaires, chalet privatif et remise pour participants déjà venus sur les pages, page modèle du cours en plein air, FAQ inventées (Lisa envoie la sienne), comptoir de l'Espace dans la boutique.

**Corrigé** :
- Alpine Creative Pause (septembre), noms des retraites et des séries en français sur les pages françaises.
- Maisons et Jardins mai 2022.
- Bio courte avec Dacca et le Salon d'Automne.
- La Gravité de la Grâce de décembre 2026 à avril 2027 (texte de la page en ligne, avec Le Petit Lapin).
- Prix en fourchette seule (phrase de Lisa) ; inscription anticipée de 100 € jusqu'au 5 décembre 2026.
- Programme jour par jour de juin repris mot pour mot de la page en ligne.
- Fermeture de saison jusqu'au 2 décembre dans les horaires.

**Ajouté** :
- Choix Artist | Espace ; menus de Lisa (Works avec la déclaration, Bio, CV, Press, Available Works ; L'Espace, Boutique & Tea Room, Co-Creating Sessions, Bespoke Courses & Workshops, Gather at the Espace, Contact ; Exhibitions & Events).
- Pages Boutique & Tea Room, Co-Creating Sessions, Exhibitions & Events, échéancier et conditions d'annulation (texte de Lisa, coordonnées de la SAS).
- Formulaires d'inscription /regjune27 et /septregistration : mêmes champs que les formulaires Wix en ligne, rattachés à leurs identifiants Wix, consentement santé, confirmation.
- « Enquire about this work » sur les pages d'œuvres et la fiche.
- Recherche sur tout le site.
- Bandeau cookies (« Refuser » aussi visible qu'« Accepter », rien de facultatif avant l'accord).
- Les trois vidéos du procédé du site actuel (chargées au clic, après accord).
- 145 redirections couvrant les 80 adresses vues dans Search Console.
- Les formulaires, la recherche et l'outil d'horaires restent en noindex après le lancement (`MAQUETTE = False` le jour J).

## v5 · novembre 2026 · réunion de suivi (horaires, SEO et GEO, connexions)

**Horaires**
- Une seule source, `assets/data/horaires.json`, au format des futures collections Wix « Horaires » et « Exceptions » : statut ouvert ou fermé, listes d'horaires, annonces de la barre du haut et données structurées en découlent.
- Éditeur pour Lisa (`/manage/opening-hours`, `/fr/gestion/horaires`, hors menu, lien en bas de page) : semaine, deuxième plage, fermetures et horaires spéciaux, messages anglais et français, aperçu sur tout le site, téléchargement du fichier.

**SEO et GEO**
- 53 titres et 52 descriptions uniques ; adresse de référence, `hreflang` (en, fr, x-default), `og:url`, `og:locale` sur chaque page.
- Données structurées : Person, ProfilePage, WebSite, ArtGallery et CafeOrCoffeeShop avec horaires, Event (trois retraites), FAQPage, ItemList de VisualArtwork, BreadcrumbList.
- `sitemap.xml`, `robots.txt` avec plan du site, `llms.txt` pour les moteurs de réponse.
- 57 redirections depuis les adresses de l'actuel site Wix (sitemap lu le 20 novembre 2026) ; le reste est à trancher (blog, résidence de mai, abonnements) : `AUDIT-SEO-GEO.md`.

**Pages**
- Retraites : places restantes (exemples), FAQ « Avant de réserver ».
- Cours privés : trois catégories, huit expériences avec durée, groupe et tarif (exemples), « Comment ça marche » pour les hôtels et conciergeries, lien « Demander cette séance » qui pré-remplit le formulaire.
- Presse : podcast (lien à venir).
- Boutique : tirages creativehub avec format, papier et référence (SKU) par variante, prix d'exemple.
- Contact : champs propres à chaque demande, envoi vers l'adresse de l'atelier ou de l'Espace selon l'objet.
- Invitation discrète vers l'autre langue selon la langue du navigateur, sans redirection.

**Connexions (site final en Wix Headless)**
- `connecteurs/artwork_archive_vers_wix.py` : export CSV d'Artwork Archive vers Wix Stores (création, masquage des œuvres vendues), mode essai par défaut, testé sur un export d'exemple.
- `connecteurs/README.md` : mail de vente à Lisa (automatisation Wix), connexion creativehub officielle à Wix, plan B par l'API.

## v4 · 11 novembre 2026 · brief de Lisa (« cirenza.com — content and design brief »)

Le brief de Lisa est la source unique des textes de l'artiste : textes anglais repris mot pour mot, traduits en français. La structure de la maquette est gardée (défilement en strates numérotées, fond crème, anglais officiel, horaires en haut, citation du FT, deux SIRET, comptes à rebours).

**Positionnement : « A Record of Time »**
- Titre : « Painter of light, water, rock and time » ; ligne d'accueil et description du brief ; citation : « Most people look up and see the Alps. I see a record of time being erased. »
- Accueil réordonné : ouverture (œuvre récente, en attendant la montagne à facettes), 01 Déclaration, 02 The Geology of the Invisible (Cool Reflections à gratter), 03 la série en tête puis l'Archive, 04 À l'atelier en ce moment, 05 Éditions de collection, 06 Presse, 07 L'Espace, 08 Trois retraites, lettre d'information.
- Calme visuel : plus de parallaxe ni de bandes qui glissent au défilement, plus de mots qui s'allument sur la citation, lettre d'information sans photo de fond.

**Œuvres**
- « A Record of Time » (`/works/a-record-of-time`, `/fr/oeuvres/strates-du-temps`) mène, en quatre groupes : sur le chevalet, glace-eau-roche, cire noir et blanc sur papier, Cool Reflections (Grand Palais 2025).
- Les séries anciennes (Cuba, London Tube, numérique, Hope and Optimism avec Dream Big…) passent sous « Archive », sur l'accueil, la page Œuvres et la boutique.

**L'artiste, parcours, presse, notes d'atelier**
- L'artiste : Emergence en ouverture, déclaration complète (`#declaration`), biographie longue en six couches (`#bio`), « Water, pigments, heat and wax », biographie courte pour la presse, liens PDF « à venir ».
- Parcours : CV sélectif du brief (formation, collections, expositions, à venir, foires, distinctions, presse, publications, conférences) ; « CV 2024 » et son PDF retirés.
- Presse : titre de l'article du FT (Rachel Spence, octobre 2017) ; anciennes parutions repliées dans « Archive ».
- Nouvelle page « Studio notes » (`/studio-notes`, `/fr/notes-d-atelier`) : le texte de Chamonix, le chevalet, recherches et procédé.

**Espace, cours, retraites**
- Nouvelle page « Private bespoke courses » (`/private-courses`, `/fr/cours-prives`) pour hôtels, conciergeries et organisateurs ; la page Cours reste en ligne mais sort de la navigation.
- Trois retraites 2027, toutes à La Clusaz : A Creative Pause (15 – 20 mai, programme à compléter), Painting in Paradise (21 – 26 juin, une journée au lac d'Annecy), Alpine Encaustics: Texture, Depth & Creative Voice (6 – 11 septembre, remplace Alpine Pause et Molten Magic, anciennes adresses redirigées).
- Grille de prix par chambre (2 450, 2 850, 3 295 €, chalet pour deux 5 500 €, partenaire non peintre 4 795 €), réductions, petite ligne sur les salles de bains.

**Boutique**
- Comptoir de l'atelier filtré en « A Record of Time », « Tirages · creativehub », « Archive » ; cinq petites encaustiques d'Artwork Archive avec leur prix (photo à venir).
- Éditions de collection : blocs d'acrylique 15 × 20 cm, trois séries.

**Technique**
- Barre du haut : Espace Créa-Tea-Vité, adresse, ouvert ou fermé ; annonces de fermeture datées (`ANNONCES` dans `outils/contenu.py`), affichées seulement pendant leurs dates.
- Lettre d'information : la langue de la page choisit la liste (anglaise ou française).
- Version 4 (`?v=4`), 51 pages, images de partage régénérées.

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
