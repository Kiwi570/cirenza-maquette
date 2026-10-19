"""Contenus du site Lisa Cirenza (anglais, version officielle, et français).

Tout vient de cirenza.com (pages, PDF du CV et de la carte des boissons). Rien n'est inventé :
ce qui manque est marqué « à compléter ». Les textes anglais sont ceux du site, les textes
français en sont des traductions fidèles.
"""

PAGES = {
    "accueil": {"en": "index", "fr": "fr/index"},
    "oeuvres": {"en": "works", "fr": "fr/oeuvres"},
    "artiste": {"en": "artist", "fr": "fr/artiste"},
    "parcours": {"en": "cv", "fr": "fr/parcours"},
    "presse": {"en": "press", "fr": "fr/presse"},
    "espace": {"en": "espace", "fr": "fr/espace"},
    "cours": {"en": "classes", "fr": "fr/cours"},
    "evenements": {"en": "private-events", "fr": "fr/evenements-prives"},
    "retraites": {"en": "retreats", "fr": "fr/retraites"},
    "pip": {"en": "retreats/painting-in-paradise", "fr": "fr/retraites/painting-in-paradise"},
    "molten": {"en": "retreats/molten-magic", "fr": "fr/retraites/molten-magic"},
    "contact": {"en": "contact", "fr": "fr/contact"},
}
DOSSIER_SALLES = {"en": "works", "fr": "fr/oeuvres"}

COORD = {
    "atelier": "Atelier Lisa Cirenza",
    "espace": "Espace Créa-Tea-Vité",
    "rue": "27 Passage du Mont Blanc",
    "ville": "74220 La Clusaz",
    "pays": {"en": "France", "fr": "France"},
    "courriel": "art@cirenza.com",
    "courriel_espace": "atelier@cirenza.com",
    "tel": "+33 7 49 09 54 92",
    "tel_brut": "+33749095492",
    "siret_atelier": "888 534 534 00019",
    "siret_espace": "989 397 146 00014",
    "instagram": "https://www.instagram.com/art.lc/",
    "linkedin": "https://fr.linkedin.com/in/lisa-cirenza-3baa4913/fr",
    "facebook": "https://www.facebook.com/LisaCirenzaFineArt/",
}

# Horaires de l'Espace : version anglaise (officielle). La version française indique 19 h : à confirmer.
HORAIRES = {"jours": [4, 5, 6], "plages": [["14:30", "18:30"]], "dimanche_rdv": True}

T = {
    "en": {
        "metier": "Abstract Figurative Artist",
        "description": "Lisa Cirenza, abstract figurative artist working in encaustic, oils and digital media, and her creative space Espace Créa-Tea-Vité in La Clusaz, French Alps.",
        "nav": {"accueil": "Home", "oeuvres": "Works", "artiste": "The Artist", "parcours": "CV", "presse": "Press", "espace": "L'Espace", "cours": "Classes", "evenements": "Private events", "retraites": "Retreats", "pip": "Painting in Paradise", "molten": "Molten Magic", "contact": "Contact"},
        "menu": "Menu", "fermer": "Close", "aller_contenu": "Skip to content",
        "langue_autre": "Version française", "langue_autre_court": "FR",
        "groupes_menu": {"oeuvres": "Works", "artiste": "The artist", "espace": "Espace Créa-Tea-Vité", "retraites": "Retreats 2027"},
        "voir": "View", "agrandir": "Zoom", "a_completer": "to be completed", "titre_a_completer": "Title to be completed",
        "prix_demande": "Price on request", "vendu": "Sold", "en_cours": "Work in progress", "edition": "Edition",
        "photo_situation": "Photographed in situ",
        "image_a_confirmer": "Image to be confirmed",
        "fiche_dims": "Dimensions", "fiche_technique": "Medium", "fiche_annee": "Year", "fiche_etat": "Availability", "fiche_edition": "Edition",
        "dims_note": "as listed on the artist's site", "dims_a_verifier": "to be checked",
        "loupe": "Magnifier", "voir_au_mur": "View on a wall", "demander": "Enquire about this work", "demander_vendu": "Ask about similar works",
        "loupe_indispo": "The magnifier needs a high-resolution file: to be requested from the artist.",
        "loupe_aide": "Move over the work to look closely at the wax and the brush.", "loupe_aide_tactile": "Slide your finger over the work.", "loupe_chargement": "Loading the high-resolution image…",
        "precedente": "Previous work", "suivante": "Next work", "fermer_fiche": "Close", "sur": "of",
        "mur_titre": "View on a wall", "mur_chalet": "Chalet", "mur_galerie": "Gallery", "mur_silhouette": "1.70 m figure", "mur_fermer": "Back to the work",
        "mur_un_metre": "1 m", "mur_echelle": "Scale drawn from the dimensions listed on the site.", "mur_sans_dims": "Dimensions to be completed: approximate scale.",
        "statut_ouvert": "Open now", "statut_ferme": "Closed", "statut_ferme_a": "until {h}", "statut_ouvre": "opens {jour} at {h}", "statut_ouvre_auj": "opens today at {h}",
        "demain": "tomorrow", "jours": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        "horaires": "Opening hours", "horaires_lignes": [["Thursday – Saturday", "2:30 pm – 6:30 pm"], ["Sunday", "by appointment"]],
        "horaires_court": "Thu – Sat · 2:30 – 6:30 pm",
        "altitude": "La Clusaz · 1,040 m",
        "strate": "Stratum",
        "oeuvre_1": "1 work", "oeuvres_n": "{n} works",
        "jours_restants": "{n} days to go", "jour_restant": "1 day to go", "aujourdhui": "Today", "passe": "Past",
        "form_obligatoire": "This field is required.", "form_email_invalide": "Please check this email address.",
        "pied_droits": "All texts, images and works © Lisa Cirenza Fine Art",
        "pied_maquette": "Design mock-up — not the live site",
        "traduction": "The official text is the English version of the site.",
        "tout_reveler": "Reveal everything", "gratter": "Scrape the wax",
        "plan": "Site map",
    },
    "fr": {
        "metier": "Artiste figurative abstraite",
        "description": "Lisa Cirenza, artiste figurative abstraite (encaustique, huile, art numérique), et son lieu de création, l'Espace Créa-Tea-Vité, à La Clusaz.",
        "nav": {"accueil": "Accueil", "oeuvres": "Œuvres", "artiste": "L'artiste", "parcours": "Parcours", "presse": "Presse", "espace": "L'Espace", "cours": "Cours", "evenements": "Événements privés", "retraites": "Retraites", "pip": "Painting in Paradise", "molten": "Molten Magic", "contact": "Contact"},
        "menu": "Menu", "fermer": "Fermer", "aller_contenu": "Aller au contenu",
        "langue_autre": "English version", "langue_autre_court": "EN",
        "groupes_menu": {"oeuvres": "Œuvres", "artiste": "L'artiste", "espace": "Espace Créa-Tea-Vité", "retraites": "Retraites 2027"},
        "voir": "Voir", "agrandir": "Agrandir", "a_completer": "à compléter", "titre_a_completer": "Titre à compléter",
        "prix_demande": "Prix sur demande", "vendu": "Vendu", "en_cours": "En cours", "edition": "Édition",
        "photo_situation": "Photographiée en situation",
        "image_a_confirmer": "Image à confirmer",
        "fiche_dims": "Dimensions", "fiche_technique": "Technique", "fiche_annee": "Année", "fiche_etat": "Disponibilité", "fiche_edition": "Édition",
        "dims_note": "telles qu'indiquées sur le site", "dims_a_verifier": "à vérifier",
        "loupe": "Loupe", "voir_au_mur": "Voir au mur", "demander": "Se renseigner sur cette œuvre", "demander_vendu": "Demander des œuvres proches",
        "loupe_indispo": "La loupe demande un fichier en haute définition, à demander à l'artiste.",
        "loupe_aide": "Survolez l'œuvre pour voir la cire et le geste de près.", "loupe_aide_tactile": "Faites glisser le doigt sur l'œuvre.", "loupe_chargement": "Chargement de l'image en haute définition…",
        "precedente": "Œuvre précédente", "suivante": "Œuvre suivante", "fermer_fiche": "Fermer", "sur": "sur",
        "mur_titre": "Voir au mur", "mur_chalet": "Chalet", "mur_galerie": "Galerie", "mur_silhouette": "Silhouette 1,70 m", "mur_fermer": "Revenir à l'œuvre",
        "mur_un_metre": "1 m", "mur_echelle": "Échelle calculée d'après les dimensions indiquées sur le site.", "mur_sans_dims": "Dimensions à compléter : échelle approximative.",
        "statut_ouvert": "Ouvert", "statut_ferme": "Fermé", "statut_ferme_a": "jusqu'à {h}", "statut_ouvre": "ouvre {jour} à {h}", "statut_ouvre_auj": "ouvre aujourd'hui à {h}",
        "demain": "demain", "jours": ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"],
        "horaires": "Horaires", "horaires_lignes": [["Jeudi – samedi", "14 h 30 – 18 h 30"], ["Dimanche", "sur rendez-vous"]],
        "horaires_court": "Jeu – sam · 14 h 30 – 18 h 30",
        "altitude": "La Clusaz · 1 040 m",
        "strate": "Strate",
        "oeuvre_1": "1 œuvre", "oeuvres_n": "{n} œuvres",
        "jours_restants": "J – {n}", "jour_restant": "J – 1", "aujourdhui": "Aujourd'hui", "passe": "Passé",
        "form_obligatoire": "Ce champ est obligatoire.", "form_email_invalide": "Vérifiez cette adresse électronique.",
        "pied_droits": "Textes, images et œuvres © Lisa Cirenza Fine Art",
        "pied_maquette": "Maquette de travail, pas le site en ligne",
        "traduction": "Le texte officiel est la version anglaise du site.",
        "tout_reveler": "Tout révéler", "gratter": "Grattez la cire",
        "plan": "Plan du site",
    },
}

MANIFESTE = {"en": ["Fueled by nature,", "Perplexed by humanity,", "Finding joy, frustration and wonder in her bewilderment."],
             "fr": ["Nourrie par la nature,", "Perplexe face à l'humanité,", "Elle trouve dans son étonnement la joie, la frustration et l'émerveillement."]}

NATURE = {"en": "When we truly immerse ourselves in nature, the boundary between self and world dissolves. We sense a profound unity, an indivisible thread weaving us into the living fabric around us.",
          "fr": "Quand nous nous immergeons vraiment dans la nature, la frontière entre soi et le monde se dissout. Nous ressentons une unité profonde, un fil indivisible qui nous relie au tissu vivant qui nous entoure."}

VEHICULE = {"en": ["Art is my vehicle, not my destination.", "Through my work, I cultivate positive meaning—enriching my life, transforming the spaces I inhabit, and hopefully prompting reflection in those I encounter along the way…"],
            "fr": ["L'art est mon véhicule, pas ma destination.", "À travers mon travail, je cultive un sens positif : il enrichit ma vie, transforme les espaces que j'habite et, je l'espère, invite à la réflexion celles et ceux que je croise en chemin…"]}

DEMARCHE = {
    "titre": {"en": "The Geology of the Invisible", "fr": "La géologie de l'invisible"},
    "paragraphes": {
        "en": [
            "My practice is grounded in a geology of the invisible, where the human figure, light, and material emerge through layers, revealing an identity in continuous transformation. Working within a form of figurative destructuralism, I respond to a contemporary paradox: a technologically hyper-connected world in which human experience feels increasingly fragmented. My work searches for what remains beneath the surface — moments of wonder and raw beauty that persist despite emotional disconnection.",
            "My background in Earth sciences, shaped between Stanford and the École des Mines de Paris, deeply informs my visual language. Concepts of stratification, fracture, and sedimentation shape my understanding of time and memory: identity is not fixed, but layered, revealing and concealing itself simultaneously. Trained initially in oil painting and glazing techniques, I extended this logic of layering into digital practice, drawing and painting directly on the iPad and approaching the pixel as a luminous material. Seeking to move beyond the immaterial smoothness of the screen, I turned to encaustic as a physical grounding — a medium that allows me to fuse, excavate, and reactivate surfaces through touch.",
            "In my work, wax functions as a geological membrane: it preserves gestures while allowing them to be reopened, scraped back, or transformed. Pastels, watercolors, sumi ink, rice paper, and printed fragments of earlier digital images accumulate like sediments, bringing together different temporalities — those of the hand, the screen, and memory. Through processes of addition and excavation, I trace connections between visible surfaces and buried structures, revealing fragile links between humanity and the environment.",
            "The human figure becomes less a portrait than a porous terrain. Silhouettes dissolve into organic horizons and fields of light, creating interior landscapes where abstraction and figuration coexist. Destructuring is not an act of negation but a gesture of revelation: fractures expose hidden strata.",
            "My surfaces invite slow looking — a geological reading in which the eye moves through layers to discover fleeting forms. Whether composed through pixels or wax, each work explores the threshold between emergence and depth. Rather than representing the world, I seek to reveal the moments where matter, light, and memory shift and transform under the viewer’s gaze.",
        ],
        "fr": [
            "Ma pratique repose sur une géologie de l'invisible, où la figure humaine, la lumière et la matière émergent par couches et révèlent une identité en perpétuelle transformation. Dans une forme de déstructuralisme figuratif, je réponds à un paradoxe contemporain : un monde hyperconnecté par la technologie, où l'expérience humaine semble de plus en plus fragmentée. Mon travail cherche ce qui demeure sous la surface : des moments d'émerveillement et de beauté brute qui persistent malgré la déconnexion émotionnelle.",
            "Ma formation en sciences de la Terre, entre Stanford et l'École des Mines de Paris, nourrit profondément mon langage visuel. La stratification, la fracture et la sédimentation façonnent ma compréhension du temps et de la mémoire : l'identité n'est pas figée, elle est faite de couches, elle se révèle et se dissimule à la fois. Formée d'abord à la peinture à l'huile et aux glacis, j'ai prolongé cette logique de couches dans la pratique numérique, en dessinant et en peignant directement sur iPad, en abordant le pixel comme une matière lumineuse. Pour dépasser le lisse immatériel de l'écran, je me suis tournée vers l'encaustique comme ancrage physique : un médium qui permet de fusionner, de creuser et de réactiver les surfaces par le toucher.",
            "Dans mon travail, la cire agit comme une membrane géologique : elle conserve les gestes tout en permettant de les rouvrir, de les gratter ou de les transformer. Pastels, aquarelles, encre sumi, papier de riz et fragments imprimés d'images numériques plus anciennes s'accumulent comme des sédiments et rassemblent plusieurs temporalités : celle de la main, celle de l'écran et celle de la mémoire. Par l'ajout et l'excavation, je trace des liens entre les surfaces visibles et les structures enfouies, et je révèle les liens fragiles entre l'humanité et son environnement.",
            "La figure humaine devient moins un portrait qu'un terrain poreux. Les silhouettes se dissolvent dans des horizons organiques et des champs de lumière, et créent des paysages intérieurs où l'abstraction et la figuration coexistent. Déstructurer n'est pas nier, c'est révéler : les fractures mettent au jour des strates cachées.",
            "Mes surfaces invitent à un regard lent, une lecture géologique où l'œil traverse les couches pour découvrir des formes fugitives. Qu'elle soit faite de pixels ou de cire, chaque œuvre explore le seuil entre l'émergence et la profondeur. Plutôt que de représenter le monde, je cherche à révéler les moments où la matière, la lumière et la mémoire se déplacent et se transforment sous le regard.",
        ],
    },
}

PROCEDE = {
    "en": ["I love working in encaustic because I can layer, and carve, and remove, and find stories and histories organically in the wax--using so many different techniques. I use my science background to explore these processes, combining knowledge of the physics of light, the properties of pigments, the viscosities and porosities of mediums, and chemical concepts particularly when it comes to adhesion and archival processes."],
    "fr": ["J'aime travailler à l'encaustique parce que je peux superposer, graver, retirer, et trouver dans la cire des histoires, de façon organique, avec une multitude de techniques. Ma formation scientifique m'aide à explorer ces procédés : la physique de la lumière, les propriétés des pigments, la viscosité et la porosité des médiums, et la chimie, en particulier pour l'adhérence et la conservation."],
}

# Biographie en couches (texte du site, découpé ; chaque couche garde ses phrases)
BIO = [
    {"cle": "debut", "photo": "artiste/lisa-a-4-ans", "legende": {"en": "Lisa at four", "fr": "Lisa à 4 ans"},
     "titre": {"en": "Art and nature, early on", "fr": "L'art et la nature, très tôt"},
     "texte": {"en": "Lisa's passions for art and nature started early in life. She started oil painting at the age of 7, but was encouraged to devote her academic studies to \"something more practical\".",
               "fr": "La passion de Lisa pour l'art et la nature commence très tôt. Elle peint à l'huile dès 7 ans, mais on l'encourage à consacrer ses études à « quelque chose de plus concret »."}},
    {"cle": "alaska", "decor": "glacier-crevasse-4x5", "legende": {"en": "Evocation · no photograph of the expedition on the site", "fr": "Évocation · aucune photo de l'expédition sur le site"},
     "titre": {"en": "Age 17, the Juneau Icefield", "fr": "17 ans, le champ de glace de Juneau"},
     "texte": {"en": "At the age of 17, she was selected for a National Science Foundation scholarship to be part of a glaciological research expedition on the Juneau Icefields in Alaska. She spent two summers traversing the glaciers, drawing and researching the geological, and climatological histories embedded in their flows. Her photographs and accounts of these experiences were published in “The Power of Ice”, a book published by Chicago Children’s Press that she co-authored to encourage other youngsters to pursue field sciences.",
               "fr": "À 17 ans, elle obtient une bourse de la National Science Foundation pour participer à une expédition de recherche glaciologique sur le Juneau Icefield, en Alaska. Pendant deux étés, elle traverse les glaciers, dessine et étudie les histoires géologiques et climatiques inscrites dans leur écoulement. Ses photographies et ses récits sont publiés dans « The Power of Ice », un livre des éditions Chicago Children's Press qu'elle cosigne pour donner envie à d'autres jeunes de se lancer dans les sciences de terrain."}},
    {"cle": "stanford", "decor": "carnet-de-terrain-4x5", "legende": {"en": "Evocation", "fr": "Évocation"},
     "titre": {"en": "Stanford, Paris, New York", "fr": "Stanford, Paris, New York"},
     "texte": {"en": "At Stanford University, she pressed hard to be accepted into their Paris based studies program, knowing she might be able to combine her dream of studying art, whilst still pursuing her work in the earth sciences. She spent 8 months studying coursework at L’Ecole des Mines de Paris, and Sciences Po—but spent much of her time in the museums, and doing short courses in painting. She continued this pattern of short course work throughout her time as a master’s student at Stanford, and as a financial analyst, and later a management consultant in NYC; always with hopes of filling her toolbox with artistic skills, for the moment she could become the artist she’d dreamed of becoming.",
               "fr": "À Stanford, elle se bat pour intégrer le programme d'études à Paris, sachant qu'elle pourra y concilier son rêve d'étudier l'art et ses travaux en sciences de la Terre. Elle passe 8 mois à suivre des cours à l'École des Mines de Paris et à Sciences Po, mais passe une grande partie de son temps dans les musées et dans de courts stages de peinture. Elle garde cette habitude pendant son master à Stanford, puis comme analyste financière et consultante en management à New York : toujours remplir sa boîte à outils artistique, pour le jour où elle pourrait devenir l'artiste dont elle rêvait."}},
    {"cle": "formations", "decor": "sumi-e-nature-morte-4x5", "photo2": "artiste/lisa-peint-au-chevalet", "legende": {"en": "Evocation", "fr": "Évocation"},
     "titre": {"en": "Learning everywhere", "fr": "Apprendre partout"},
     "texte": {"en": "Whilst raising her 4 children in New Jersey, London, Tokyo, and Quebec, she studied constantly. Her schooling includes studies with a Master of Sumi-e in Tokyo, painting and drawing at Central St. Martins, and the Royal Drawing School in London, and the study of traditional oil techniques with the Jean Pierre Brazs Atelier in Paris, and the Norfolk Painting School. She acquired her love for, and many of her foundational techniques in encaustic art through Mulranny Arts in Ireland.",
               "fr": "En élevant ses quatre enfants dans le New Jersey, à Londres, à Tokyo et au Québec, elle ne cesse d'étudier : auprès d'un maître de sumi-e à Tokyo, en peinture et en dessin à Central Saint Martins et à la Royal Drawing School de Londres, en techniques traditionnelles de l'huile à l'atelier Jean-Pierre Brazs à Paris et à la Norfolk Painting School. C'est à Mulranny Arts, en Irlande, qu'elle découvre l'encaustique et en acquiert bien des techniques fondatrices."}},
    {"cle": "residences", "photo": "artiste/lisa-photographie-cuba",
     "titre": {"en": "Residencies", "fr": "Résidences"},
     "texte": {"en": "Artist residencies include time (and focuses) in Cuba (people, and colour), California (environment, and the sea), Kyoto (calligraphy and substrates), and the Tyrolean Alps (light and atmosphere in the Alps). Her works are united by her love of the environment, and her bewilderment at human behaviours. Humor is important, as is moving beyond the surface and mining the layers of moments and experiences for the truths hidden within.",
               "fr": "Ses résidences d'artiste l'ont menée à Cuba (les gens, la couleur), en Californie (l'environnement, la mer), à Kyoto (la calligraphie, les supports) et dans les Alpes tyroliennes (la lumière et l'atmosphère des Alpes). Ses œuvres sont unies par son amour de l'environnement et son étonnement devant les comportements humains. L'humour compte, tout comme le fait d'aller au-delà de la surface et de creuser les couches des moments et des expériences pour en extraire les vérités cachées."}},
    {"cle": "engagement", "photo": "conferences/atelier-blouses-blanches",
     "titre": {"en": "Creativity for everyone", "fr": "La créativité pour tous"},
     "texte": {"en": "She is passionate about the role of creativity in solving so many of the problems we humans face, and has run workshops on maximising creativity with many corporate and private entities. Having grown up in an environment without easy access, nor appreciation for the arts, she has and continues to do similar pro-bono work with disenfranchised communities including refugees, homeless mothers and children, and schools without the resources to include art in their curriculums.",
               "fr": "Convaincue que la créativité aide à résoudre bien des problèmes humains, elle anime des ateliers pour la stimuler auprès de nombreuses entreprises et structures privées. Ayant grandi dans un milieu où l'art était peu accessible et peu considéré, elle mène bénévolement le même travail auprès de communautés défavorisées : réfugiés, mères et enfants sans abri, écoles sans moyens pour enseigner l'art."}},
    {"cle": "alpes", "photo": "espace/enseigne-rue-village",
     "titre": {"en": "Full circle, in the French Alps", "fr": "La boucle bouclée, dans les Alpes"},
     "texte": {"en": "Having recently realised her dream of moving to the French Alps, Lisa has now come full circle and is combining her love for the earth with her responses to humanity. Her earth science degree, her Master's in International Policy Studies, her toolbox full of art techniques, and bewilderment at human behaviours are all to be found in the moments of pause, joy, tension, and light, in the many layers of her work.",
               "fr": "Après avoir réalisé son rêve de s'installer dans les Alpes françaises, Lisa boucle la boucle : elle réunit son amour de la Terre et son regard sur l'humanité. Son diplôme en sciences de la Terre, son master en politique internationale, sa boîte à outils pleine de techniques et son étonnement devant les comportements humains se retrouvent dans les moments de pause, de joie, de tension et de lumière, au fil des nombreuses couches de son travail."}},
]
BIO_FIN = {
    "en": ["She has exhibited widely in London, Paris, NY, Silicon Valley, Edinburgh, Xian, Dhaka, and Kyoto; in exhibitions including Miami Basel, Venice Biennale, Asian Biennale, and the historical Parisian Salons. Her works are held in corporate, state, and private collections in Japan, France, Sweden, China, Austria, the UK, Canada, and throughout the USA.",
           "Art needs to reflect the age and society it is created in and for, and will hopefully serve as a temporal testimony for future generations."],
    "fr": ["Elle a beaucoup exposé, à Londres, Paris, New York, dans la Silicon Valley, à Édimbourg, Xi'an, Dacca et Kyoto, notamment à Miami Basel, à la Biennale de Venise, à la Biennale asiatique et dans les Salons historiques parisiens. Ses œuvres figurent dans des collections d'entreprises, publiques et privées au Japon, en France, en Suède, en Chine, en Autriche, au Royaume-Uni, au Canada et dans tous les États-Unis.",
           "L'art doit refléter l'époque et la société pour lesquelles il est créé, et servir, je l'espère, de témoignage aux générations futures."],
}
PASSIONS = {"en": "Certified Canadian Ski Instructor, bilingual English/French, basic level Japanese, I love open water swimming, hiking, travel, my better half, my 4 adult kids, their spouses and kids, nerding out on all things art, and seizing life’s challenges and opportunities far and wide!",
            "fr": "Monitrice de ski certifiée au Canada, bilingue anglais-français, quelques bases de japonais. J'aime la nage en eau libre, la randonnée, les voyages, ma moitié, mes quatre enfants adultes, leurs conjoints et leurs enfants, me passionner pour tout ce qui touche à l'art, et saisir les défis et les occasions de la vie, partout où ils se présentent !"}

# Parcours : expositions et résidences (page CV Highlights du site)
EXPOSITIONS = [
    (2014, "The Other Art Fair", "London, UK", "Londres, Royaume-Uni", None),
    (2015, "Kyoto Museum of Art", "Kyoto, Japan", "Kyoto, Japon", None),
    (2015, "East West Art Prize Residency", "Kyoto, Japan", "Kyoto, Japon", "residence"),
    (2017, "The Other Art Fair", "London, UK", "Londres, Royaume-Uni", None),
    (2017, "Salon d'Automne, sociétaire (2017–2024)", "Paris, France", "Paris", None),
    (2018, "Aqua Miami – Miami Basel", "Miami, Florida, USA", "Miami, Floride, États-Unis", None),
    (2018, "Solo show, Bermondsey Gallery", "London, UK", "Londres, Royaume-Uni", "solo"),
    (2018, "RGNN", "Havana and Trinidad, Cuba", "La Havane et Trinidad, Cuba", "residence"),
    (2018, "The Other Art Fair", "London, UK", "Londres, Royaume-Uni", None),
    (2018, "Salon National des Beaux-Arts (2018–2019)", "Paris, France", "Paris", None),
    (2019, "Art Wynwood, Steidel Contemporary Gallery", "Palm Beach, Florida, USA", "Palm Beach, Floride, États-Unis", None),
    (2019, "Xi'an International Gallery, via the Salon d'Automne", "Xi'an, China", "Xi'an, Chine", None),
    (2019, "Art Ventures Gallery", "Half Moon Bay, California, USA", "Half Moon Bay, Californie, États-Unis", None),
    (2019, "Loruenser", "Zürs, Austria", "Zürs, Autriche", None),
    (2022, "Venice Biennale, ‘Personal Structures’, Palazzo Mora", "Venice, Italy", "Venise, Italie", None),
    (2022, "Asian Biennale", "Dhaka, Bangladesh", "Dacca, Bangladesh", None),
    (2024, "Salon Art & Déco (May 2024–2026)", "Annecy, France", "Annecy", None),
    (2025, "Salon des Artistes Français, Grand Palais", "Paris, France", "Paris", None),
    (2025, "Nepal Academy of Fine Arts", "Kathmandu, Nepal", "Katmandou, Népal", None),
    (2025, "Nayabazar Gallery", "Pokhara, Nepal", "Pokhara, Népal", None),
    (2026, "London Art in Motion, Public Art PLogix Gallery", "London, UK", "Londres, Royaume-Uni", None),
    (2026, "Mouvement, Masse, et Lumière, EC Gallery", "La Clusaz, France", "La Clusaz", None),
]
CONFERENCES = [
    (2016, "Burgh House Museum, workshop", "London, UK", "Londres"),
    (2016, "Apple Store, “From Painting to Pixels”, Covent Garden", "London, UK", "Londres"),
    (2017, "Live Digital Art Performance, Apple HQ, Union Square", "San Francisco, USA", "San Francisco"),
    (2017, "Casa Suraya Refugee Center, art workshop with refugees", "Milan, Italy", "Milan"),
    (2017, "Stanford Women's Network, “Wine, cheese, and an artist Q&A”", "London, UK", "Londres"),
    (2018, "Christopher Newport University, “From Pick Axes and Pipettes to Paints and Pixels: one scientist's journey from STEM to STEAM—and back”, plenary speech", "Virginia, USA", "Virginie, États-Unis"),
    (2018, "Tikehau, “Cultivate Your Creative Side and Instantly See the Forest; While others are still stuck in the trees”", "Paris, France", "Paris"),
    (2018, "Zetland Capital offsite, “Bananas and Bowties – The Role of Divergent Thinking in Creative Processes”, creative workshops", "London, UK", "Londres"),
    (2019, "Barclays HQ, series of talks and workshops", "London, UK", "Londres"),
    (2019, "Musée Maillol, “Disruptive Technologies, Impressionists, and the Parallels with Contemporary Digital Art Trends”", "Paris, France", "Paris"),
]
PHOTOS_ANNEES = {2016: "conferences/from-oil-paint-to-pixels-affiche", 2017: "expositions/vernissage-galerie-herrick", 2018: "expositions/the-other-art-fair-2018",
                 2019: "expositions/salon-automne-2019-paris", 2022: "expositions/art-below-affiche-regards", 2025: "expositions/salon-beaux-arts-galerie",
                 2015: "expositions/kyoto-rencontre", 2014: "expositions/bermondsey-gallery-salle", 2024: "espace/visiteuse-contemplation", 2026: "exposition-en-cours/affiche-vernissage-bnt"}

PRESSE = [
    {"titre": "Quand Art Nous Connecte", "media": "Maison et Jardin", "date": {"en": "May 2022", "fr": "mai 2022"},
     "texte": {"en": "“When Art Connects Us”: feature interview in the French magazine Maison et Jardin.", "fr": "« Quand l'art nous connecte » : grand entretien dans le magazine Maison et Jardin."},
     "url": "https://www.pressreader.com/france/maison-et-jardin-magazine/20220516/289794336701817", "image": "presse/maison-et-jardin-2022"},
    {"titre": "The App Whisperer Podcast", "media": "Apple Podcasts", "date": {"en": "March 2021", "fr": "mars 2021"},
     "texte": {"en": "The App Whisperer Podcast interviews award winning digital artist, Lisa Cirenza: her first ventures into digital art, her techniques, workflow, her style, her favourite apps, the future of mobile art.", "fr": "Le podcast The App Whisperer reçoit Lisa Cirenza, artiste numérique primée : ses débuts dans l'art numérique, ses techniques, sa méthode, son style, ses applications préférées, l'avenir de l'art mobile."},
     "url": "https://podcasts.apple.com/gb/podcast/podcast-with-lisa-cirenza-award-winning-digital-artist/id1050995756?i=1000514228545", "image": "presse/app-whisperer-podcast"},
    {"titre": "Lisa Cirenza, Collective Works", "media": "Art Rabbit", "date": {"en": "1 Dec 2018 – 6 Jan 2019", "fr": "1er déc. 2018 – 6 janv. 2019"},
     "texte": {"en": "Exhibition listing.", "fr": "Annonce de l'exposition."},
     "url": "https://www.artrabbit.com/events/lisa-cirenza-collective-works", "image": "presse/art-rabbit"},
    {"titre": "Etchr Labs Interview", "media": "Etchr Labs", "date": None, "texte": {"en": "Interview.", "fr": "Entretien."},
     "url": "https://etchrlab.com/blogs/news/cirenza", "image": "artiste/lisa-ipad-malecon-nuit-etchr"},
    {"titre": "BBC Documentary", "media": "BBC", "date": None,
     "texte": {"en": "The BBC documentary highlights “Dream Big”, a layered piece depicting the many layers of hope and challenges in Stockton, being transformed by Mayor Michael Tubbs (see 1:16 – 1:20).", "fr": "Le documentaire de la BBC met en avant « Dream Big », œuvre en couches sur les espoirs et les défis de Stockton, ville transformée par son maire Michael Tubbs (voir 1:16 – 1:20)."},
     "url": "http://bit.ly/DreamBigCommission", "image": "presse/bbc-documentaire"},
    {"titre": "Best of the Rest", "media": "Financial Times", "date": {"en": "October 7th weekend edition", "fr": "édition du week-end du 7 octobre"},
     "texte": {"en": "Review in the Financial Times.", "fr": "Critique dans le Financial Times."}, "url": None, "image": "presse/financial-times"},
    {"titre": "Just MARVELous: Art for the Comical", "media": "Rise Art", "date": {"en": "July 2017", "fr": "juillet 2017"},
     "texte": {"en": "Rise Art featured artist.", "fr": "Artiste à l'honneur sur Rise Art."},
     "url": "https://www.riseart.com/article/2017-07-12-art-collections-just-marvelous-art-for-the-comically-inclined", "image": "presse/riseart-just-marvelous"},
    {"titre": "Cirenza: I'm Not Who You Think I Am", "media": "Made In Shoreditch", "date": {"en": "28 May 2016", "fr": "28 mai 2016"},
     "texte": {"en": "Website article by Inez Ali.", "fr": "Article d'Inez Ali."},
     "url": "http://madeinshoreditch.co.uk/2016/05/28/lisa-cirenza-im-not-think-i/", "image": "presse/made-in-shoreditch"},
    {"titre": "Oil Paints to Pixels", "media": "London Visual Arts", "date": {"en": "October 2015", "fr": "octobre 2015"},
     "texte": {"en": "“Lisa Cirenza: Oil Paints to Pixels. A talk with Lisa Cirenza on her latest work.”", "fr": "« Lisa Cirenza : de la peinture à l'huile aux pixels. » Un entretien sur ses dernières œuvres."},
     "url": "https://lovarts.co.uk/2015/10/06/lisa-cirenza-oil-paints-to-pixels/", "image": "presse/london-visual-arts"},
    {"titre": "Stanford Arts Monthly Review", "media": "Stanford Arts", "date": {"en": "December 2014", "fr": "décembre 2014"},
     "texte": {"en": "Monthly bulletin of Stanford arts news.", "fr": "Bulletin mensuel des arts de Stanford."},
     "url": "http://us5.campaign-archive2.com/?u=a8e6569da943904e9ac369cde&id=a3a3a5fafb&e=f36716c760", "image": "presse/stanford-arts-monthly-review"},
    {"titre": "Mind the Gap!", "media": "Artslant", "date": {"en": "November 2014", "fr": "novembre 2014"},
     "texte": {"en": "Art historian Dr. Aust-Wegemund reviews Cirenza’s exhibit with Artvera's Art Gallery, Geneva, Switzerland.", "fr": "L'historienne de l'art Dr Aust-Wegemund commente l'exposition de Lisa Cirenza à la galerie Artvera, à Genève."},
     "url": "https://www.artslant.com/ew/events/show/364765-mind-the-gap---lisa-cirenzas-recent-works-at-artveras-art-gallery", "image": "presse/artslant"},
]
VIDEOS = [
    {"titre": "Balthazart Presents Lisa Cirenza — Collections", "auteur": "Balthazart Gallery", "date": {"en": "May 2016", "fr": "mai 2016"}, "url": "https://www.youtube.com/watch?v=6Z8H4XgFE6Q"},
    {"titre": "Take a Moment to Really Look: Lisa Cirenza at The Other Art Fair", "auteur": "Adriana Chavez", "date": {"en": "October 2014", "fr": "octobre 2014"}, "url": "https://www.youtube.com/watch?v=MhUZutFPpt8"},
]
# Citation courte de la critique du Financial Times (2017), reproduite sur le site de l'artiste
FT_CITATION = "it blends tradition and contemporary practice with authority"

ESPACE = {
    "intro": {"en": "A refuge* for genuine conviviality, warm drinks, and quiet inspiration. Step inside to slow down and recharge—whether you are here to savor a signature latte, take in the latest gallery exhibition, or pick up fine art supplies and gifts. Come to create, or simply sit back and enjoy a real break.",
              "fr": "Un refuge* de vraie convivialité, de boissons chaudes et d'inspiration tranquille. Entrez pour ralentir et vous ressourcer, que ce soit pour savourer un latte signature, découvrir la dernière exposition de la galerie ou trouver du beau matériel d'art et des cadeaux. Venez créer, ou simplement profiter d'une vraie pause."},
    "ecran": {"en": "*A screen-free zone: put down the phone, embrace the moment, and enjoy the company.", "fr": "*Un lieu sans écran : on pose le téléphone, on vit l'instant et on profite de la compagnie."},
    "offres": [
        {"titre": {"en": "Gallery & Tea Room", "fr": "Galerie et salon de thé"}, "texte": {"en": "Local artists & artisans, warm and cold signature beverages, and space to ponder.", "fr": "Artistes et artisans locaux, boissons signature chaudes et froides, et de la place pour rêver."}, "photo": "espace/salon-canape"},
        {"titre": {"en": "Creative Corner", "fr": "Coin créatif"}, "texte": {"en": "Hands-on workshops and open studio time.", "fr": "Ateliers pratiques et temps d'atelier libre."}, "photo": "cours/atelier-libre-pastel"},
        {"titre": {"en": "Boutique", "fr": "Boutique"}, "texte": {"en": "Curated art materials and unique local gifts.", "fr": "Matériel d'art choisi et cadeaux locaux uniques."}, "photo": "espace/atelier-rangements"},
    ],
    "reve": {"en": ["Welcome to Espace Créativité, a creative hub in one of the Alps' most stunning Savoyard villages!", "A vibrant space to create, connect, and be inspired. Join workshops, explore exhibitions, come to the events, and share your creativity—plus enjoy one of our signature Lattes, Hot Cocoa, or tea while collaborating with like-minded souls."],
             "fr": ["Bienvenue à l'Espace Créativité, un lieu de création dans l'un des plus beaux villages savoyards des Alpes !", "Un espace vivant pour créer, se rencontrer et s'inspirer. Participez aux ateliers, découvrez les expositions, venez aux événements et partagez votre créativité, autour d'un latte signature, d'un chocolat chaud ou d'un thé, avec des personnes qui vous ressemblent."]},
}
# Carte des boissons (PDF du site). Les allégations de santé du PDF ne sont pas reprises.
CARTE = [
    {"titre": {"en": "Signature lattes", "fr": "Nos signatures"}, "items": [
        ("Green Matcha Latte", "6,50", {"en": "Matcha green tea, coconut blossom sugar, steamed milk. Contains theine.", "fr": "Thé vert matcha, sucre de fleur de coco, lait fouetté à la vapeur. Contient de la théine."}),
        ("Golden Curcuma / Gingembre Latte", "6,50", {"en": "Turmeric and ginger, coconut blossom sugar, velvety milk. Caffeine free.", "fr": "Curcuma et gingembre, sucre de fleur de coco, lait velouté. Sans caféine."}),
        ("Rubis Betterave / Cacao Latte", "6,50", {"en": "Beetroot, cocoa and a hint of ginger, coconut blossom sugar, velvety milk. Caffeine free.", "fr": "Betterave, cacao et une pointe de gingembre, sucre de fleur de coco, lait velouté. Sans caféine."}),
        ("Violet Ube Latte", "6,50", {"en": "Purple yam from the Philippines, coconut blossom sugar, a hint of ginger; notes of vanilla and chestnut. Caffeine free.", "fr": "Igname violette des Philippines, sucre de fleur de coco, une pointe de gingembre ; notes de vanille et de châtaigne. Sans caféine."}),
        ("Ambre Pain d'épices Latte", "6,50", {"en": "Cinnamon, nutmeg and clove with organic Malongo coffee and velvety milk. Regular or decaf.", "fr": "Cannelle, muscade et girofle, café bio Malongo, lait velouté. Caféiné ou décaféiné."}),
        ("Ébène Chocolat chaud praliné", "6,50", {"en": "Venezuelan cocoa with velvety hazelnut milk. Allergens: nuts, gluten. Caffeine free.", "fr": "Cacao du Venezuela, lait de noisette velouté. Allergènes : fruits à coque, gluten. Sans caféine."}),
    ]},
    {"titre": {"en": "The classics", "fr": "Les classiques"}, "items": [
        ("Latte", "5,50", {"en": "Espresso with generous milk micro-foam. Regular or decaf.", "fr": "Espresso nappé d'une généreuse micro-mousse de lait. Caféiné ou décaféiné."}),
        ("Cappuccino", "5,00", {"en": "Espresso with dense, airy milk foam. Regular or decaf.", "fr": "Espresso et mousse de lait dense et aérée. Caféiné ou décaféiné."}),
        ("Noisette", "3,50", {"en": "Espresso with a dash of milk.", "fr": "Espresso tacheté de lait."}),
        ("Espresso", "3,00", {"en": "Regular or decaf.", "fr": "Caféiné ou décaféiné."}),
        ({"en": "Teas & herbal teas", "fr": "Thés et tisanes"}, "3,00", {"en": "Mariage Frères, Fortnum & Mason, Les 2 Marmottes.", "fr": "Mariage Frères, Fortnum & Mason, Les 2 Marmottes."}),
    ]},
    {"titre": {"en": "Cold drinks", "fr": "Boissons fraîches"}, "items": [
        ({"en": "Organic orange lemonade", "fr": "Limonade bio à l'orange"}, "5,00", None),
        ({"en": "Organic ginger lemonade", "fr": "Limonade bio au gingembre"}, "5,00", None),
        ({"en": "Iced ginger tea", "fr": "Thé glacé au gingembre"}, "5,00", None),
        ({"en": "Iced mint and peach tea", "fr": "Thé glacé menthe et pêche"}, "5,00", None),
        ({"en": "Sparkling pomegranate & blackcurrant", "fr": "Soda pétillant grenade, cassis"}, "5,00", None),
        ({"en": "Sparkling lemon & raspberry", "fr": "Soda pétillant citron, framboise"}, "5,00", None),
        ({"en": "Strawberry & banana smoothie", "fr": "Smoothie fraise, banane"}, "5,00", None),
        ({"en": "Orange, mango & passion fruit smoothie", "fr": "Smoothie orange, mangue, passion"}, "5,00", None),
        ({"en": "Kiwi, apple & pineapple smoothie", "fr": "Smoothie kiwi, pomme, ananas"}, "5,00", None),
    ]},
]
CARTE_NOTE = {"en": "All our coffees (except decaf) are organic Malongo, artisan roasted in France.",
              "fr": "Tous nos cafés (sauf les décaféinés) sont des cafés bio Malongo, torréfiés artisanalement en France."}

EXPO = {
    "titre": "La Gravité de la Grâce", "debut": "2026-07-01", "fin": "2026-10-31",
    "dates": {"en": "July – October 2026", "fr": "Juillet – octobre 2026"},
    "intro": {"en": "Gravité de la grâce captures the beautiful tension between weight and weightlessness. This exhibition unites two local artists who find soaring joy in seemingly opposing realms: BNT Designs, through fluid metal sculptures of local flight and motion, and Lisa Cirenza, through vibrant visual celebrations of human resilience in Cuba. Together, these metals, pigments, and pixels reveal grace as an active agent of transformation—proving that lightness can be found in the heaviest of mediums and circumstances.",
              "fr": "« La Gravité de la Grâce » saisit la belle tension entre le poids et l'apesanteur. L'exposition réunit deux artistes du pays qui trouvent une joie qui s'envole dans des mondes en apparence opposés : BNT Designs, avec des sculptures de métal fluides sur le vol et le mouvement, et Lisa Cirenza, avec des célébrations éclatantes de la résilience humaine à Cuba. Métaux, pigments et pixels y révèlent la grâce comme force de transformation, et montrent que la légèreté se trouve jusque dans les matières et les circonstances les plus lourdes."},
    "bnt": {"en": "BNT Designs transforms heavy, rigid industrial metal into fluid, weightless expressions of motion. Focusing on dynamic local subjects—from paragliders and cyclists to soaring montgolfières—these sculpted steel works actively defy physical gravity. By trapping high-energy movement in iron and steel, BNT Designs captures the fleeting, soaring grace of joy found in pure action and continuous transformation.",
            "fr": "BNT Designs transforme un métal industriel lourd et rigide en expressions fluides et légères du mouvement. Parapentistes, cyclistes, montgolfières : ces aciers sculptés défient la gravité. En figeant dans le fer et l'acier un mouvement plein d'énergie, BNT Designs saisit la grâce fugace de la joie que procurent l'action pure et la transformation continue."},
    "lisa": {"en": "Lisa Cirenza works across materials—waxes, pigments, aluminium, acrylics, inks, rice papers—building and breaking down images to reveal histories embedded within matter itself. Through this deeply tactile process, her work investigates an indomitable joy that persists despite the complex socio-political circumstances in Cuba. By layering texture and color, Cirenza transforms emotional and historical gravity into a vibrant visual celebration of human resilience and active grace.",
             "fr": "Lisa Cirenza travaille avec de nombreux matériaux (cires, pigments, aluminium, acryliques, encres, papiers de riz) : elle construit puis défait ses images pour révéler les histoires inscrites dans la matière. Par ce processus très tactile, elle explore une joie indomptable qui persiste malgré la situation sociopolitique complexe de Cuba. En superposant textures et couleurs, elle transforme le poids émotionnel et historique en une célébration éclatante de la résilience humaine et de la grâce."},
}

AGENDA = [
    {"titre": "Co-Creating Sessions", "groupe": {"en": "Open studios", "fr": "Ateliers ouverts"}, "prix": "30", "etat": "ouvert",
     "texte": {"en": "A place to work on, and get advice on your personal creative projects…", "fr": "Un lieu pour avancer sur vos projets créatifs personnels, et recevoir des conseils…"}},
    {"titre": "Jeudi soirs – Aquarelles sans frontières", "groupe": {"en": "Private classes", "fr": "Cours"}, "prix": "200", "etat": "termine",
     "texte": {"en": "Embark on an artistic journey where curiosity and exploration come first.", "fr": "Embarquez pour un voyage artistique où la curiosité et l'exploration sont primordiales."}},
    {"titre": "Apéro-Rencontre : « Regards sur Cuba »", "groupe": {"en": "Créa-Tea-Vité gatherings", "fr": "Rencontres Créa-Tea-Vité"}, "prix": "40", "etat": "termine", "date": {"en": "5 August, 6:30 – 9:30 pm", "fr": "5 août, 18 h 30 – 21 h 30"},
     "texte": {"en": "An intimate cultural salon: art, music, nibbles and discussion…", "fr": "Salon culturel intime : art, musique, grignotages et discussion…"}, "photo": "evenements/apero-rencontre-regards-sur-cuba-affiche"},
]

COURS = {
    "citation": {"en": "I don’t teach you how to paint a perfect flower; I teach you how to see and to express the garden.", "fr": "Je ne vous apprends pas à peindre une fleur parfaite ; je vous apprends à voir et à exprimer le jardin."},
    "ateliers": [
        ({"en": "Wax & Mixed Media", "fr": "Cire et techniques mixtes"}, {"en": "Exploration through texture, encaustic, and layered discovery.", "fr": "Explorer par la texture, l'encaustique et la découverte des couches."}, "cours/cours-encaustique-sur-papier"),
        ({"en": "Wax Monoprinting", "fr": "Monotype à la cire"}, {"en": "Immediate, intuitive mark-making through the fluidity of wax.", "fr": "Un geste immédiat et intuitif, porté par la fluidité de la cire."}, "atelier/table-des-cires"),
        ({"en": "The Artist’s Eye", "fr": "Le regard de l'artiste"}, {"en": "Moving beyond representation to truly see—the fundamental skill of visual intelligence.", "fr": "Dépasser la représentation pour vraiment voir : la compétence fondamentale de l'intelligence visuelle."}, "cours/atelier-libre-pastel"),
        ({"en": "Abstraction & The Creative Voice", "fr": "L'abstraction et la voix créative"}, {"en": "Breaking the habit of \"doing it right\" to find your authentic aesthetic language.", "fr": "Sortir de l'habitude de « bien faire » pour trouver votre propre langage esthétique."}, "cours/etudes-a-l-huile"),
        ({"en": "Digital Mastery (iPad Art)", "fr": "Maîtrise numérique (art sur iPad)"}, {"en": "Advanced digital workflows. Instruction refined through partnerships with Apple, Adobe, and Stanford University.", "fr": "Méthodes numériques avancées. Un enseignement affiné au fil de collaborations avec Apple, Adobe et l'université Stanford."}, "artiste/lisa-peint-sur-ipad"),
    ],
    "equipes_intro": {"en": "I don’t teach teams how to replicate a process; I teach them how to cultivate the garden of creative thinking.", "fr": "Je n'apprends pas aux équipes à reproduire un processus ; je leur apprends à cultiver le jardin de la pensée créative."},
    "equipes": [
        ({"en": "Creative Thinking for Institutions", "fr": "La pensée créative pour les institutions"}, {"en": "Leveraging the artist’s mindset to solve complex business challenges.", "fr": "Mettre l'état d'esprit de l'artiste au service de problèmes complexes d'entreprise."}),
        ({"en": "Fearless Collaboration", "fr": "Collaborer sans peur"}, {"en": "High-impact team building for forward-thinking organizations. Trusted by Barclays, ECSP, TKO Capital, and other global institutions.", "fr": "Une cohésion d'équipe à fort impact pour les organisations tournées vers l'avenir. Barclays, ECSP, TKO Capital et d'autres institutions internationales lui font confiance."}),
    ],
}

EVENEMENTS = {
    "titre": {"en": "A unique artistic venue for private events, cultural gatherings, and creative experiences in La Clusaz", "fr": "Un lieu artistique unique pour vos événements privés, rencontres culturelles et expériences créatives à La Clusaz"},
    "intro": {"en": "Located within an intimate contemporary gallery, Espace Créa-Tea-Vité offers a warm, inspiring environment designed for meaningful connection, creativity, and memorable moments. Whether you are planning a conference, private dinner, cultural event, or team-building experience, the space blends artistic atmosphere with practical flexibility.",
              "fr": "Installé dans une galerie d'art contemporain intime, l'Espace Créa-Tea-Vité offre un cadre chaleureux et inspirant, pensé pour les vraies rencontres, la créativité et les moments qui marquent. Conférence, dîner privé, événement culturel ou cohésion d'équipe : le lieu allie l'atmosphère d'une galerie à une grande souplesse pratique."},
    "equipements": {"en": ["A separate apéro / reception area distinct from the main gallery space", "Fully equipped kitchen: plates, dishes, glassware, and serving essentials included", "Small lit stage area also available"],
                    "fr": ["Un espace apéritif et réception distinct de la galerie", "Une cuisine entièrement équipée : assiettes, plats, verrerie et service compris", "Une petite scène éclairée, également disponible"]},
    "ambiance": {"en": "The gallery setting creates an intimate yet professional ambiance — ideal for gatherings that go beyond a traditional event space.", "fr": "Le cadre de la galerie crée une ambiance intime et professionnelle à la fois : idéale pour des rencontres qui sortent de l'ordinaire."},
    "experiences_intro": {"en": "In addition to venue rental, guests may book a private creative event led by the resident artist. These sessions are designed to spark imagination, encourage collaboration, and provide a memorable shared experience.", "fr": "En plus de la location du lieu, vous pouvez réserver un événement créatif privé animé par l'artiste en résidence. Ces séances éveillent l'imagination, encouragent la collaboration et offrent une expérience partagée mémorable."},
    "experiences": {"en": ["Guided artistic workshops", "Creative thinking sessions", "Custom cultural experiences tailored to your group"], "fr": ["Ateliers artistiques guidés", "Séances de pensée créative", "Expériences culturelles sur mesure pour votre groupe"]},
    "art_thinking": {"en": "Espace Créa-Tea-Vité specializes in creative workshops that combine artistic practice with innovative thinking. These experiences are ideal for offsites, leadership retreats, and team-building programs. The artist behind the space has led talks, workshops, and creative sessions for international institutions and organizations including Barclays, Stanford University, Apple, major financial institutions, and public and private cultural groups.",
                     "fr": "L'Espace Créa-Tea-Vité est spécialisé dans les ateliers créatifs qui associent pratique artistique et pensée innovante : idéal pour les séminaires, les retraites de direction et les programmes de cohésion. L'artiste à l'origine du lieu a animé conférences, ateliers et séances créatives pour des institutions internationales, dont Barclays, l'université Stanford, Apple, de grandes institutions financières et des structures culturelles publiques et privées."},
    "themes": [({"en": "Charcoal and the Big Picture", "fr": "Le fusain et la vue d'ensemble"}, {"en": "How to see the forest and not get lost in the trees", "fr": "Voir la forêt sans se perdre dans les arbres"}),
               ({"en": "Bananas and Brainstorming", "fr": "Bananes et remue-méninges"}, {"en": "Creative problem-solving", "fr": "Résoudre les problèmes avec créativité"}),
               ({"en": "Team Painting", "fr": "Peindre en équipe"}, {"en": "How to keep creativity flowing (and have fun in the process)", "fr": "Garder la créativité vivante (et s'amuser en chemin)"})],
    "fin": {"en": "To discuss availability, pricing, or to design a customized experience, please get in touch. We are happy to help you create an event that is both meaningful and unforgettable.", "fr": "Pour connaître les disponibilités et les tarifs, ou imaginer une expérience sur mesure, contactez-nous. Nous serons heureux de vous aider à créer un événement qui ait du sens et dont on se souvienne."},
}
