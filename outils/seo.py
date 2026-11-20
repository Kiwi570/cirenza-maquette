"""Référencement (SEO) et moteurs de réponse (GEO) : titres, descriptions, redirections de l'ancien site.

Chaque page a un titre et une description uniques, en anglais (version officielle) et en français.
Les faits cités sont ceux du site (brief de Lisa) : rien n'est inventé pour le référencement.
À la mise en ligne : SITE_URL passe à https://www.cirenza.com (outils/generer.py), le noindex est retiré,
et les redirections passent en permanentes (301).
"""

PAGES = {
    "mentions": {
        "titre": {"en": "Legal notice · Lisa Cirenza Fine Art and Espace Créa-Tea-Vité",
                  "fr": "Mentions légales · Lisa Cirenza Fine Art et Espace Créa-Tea-Vité"},
        "description": {"en": "Legal notice of cirenza.com: Lisa Cirenza Fine Art (artist-author) and Espace Créa-Tea-Vité (SAS Atelier Truffle), La Clusaz.",
                        "fr": "Mentions légales de cirenza.com : Lisa Cirenza Fine Art (artiste-auteur) et l'Espace Créa-Tea-Vité (SAS Atelier Truffle), La Clusaz."}},
    "confidentialite": {
        "titre": {"en": "Privacy policy · Lisa Cirenza", "fr": "Politique de confidentialité · Lisa Cirenza"},
        "description": {"en": "How cirenza.com handles your personal data: registrations, bookings, orders, newsletter and the providers involved.",
                        "fr": "Comment cirenza.com traite vos données personnelles : inscriptions, réservations, commandes, lettre d'information et prestataires."}},
    "politique_cookies": {
        "titre": {"en": "Cookie policy · Lisa Cirenza", "fr": "Politique cookies · Lisa Cirenza"},
        "description": {"en": "Cookies and browser storage on cirenza.com: what is stored, for how long, and how to change your choice.",
                        "fr": "Cookies et stockage du navigateur sur cirenza.com : ce qui est enregistré, pour combien de temps, et comment changer votre choix."}},
    "conditions_site": {
        "titre": {"en": "Website terms · Lisa Cirenza", "fr": "Conditions d'utilisation du site · Lisa Cirenza"},
        "description": {"en": "Terms of use of cirenza.com, the website of Lisa Cirenza Fine Art and Espace Créa-Tea-Vité.",
                        "fr": "Conditions d'utilisation de cirenza.com, le site de Lisa Cirenza Fine Art et de l'Espace Créa-Tea-Vité."}},
    "oeuvres": {
        "titre": {"en": "Portfolio: A Record of Time and the Archive · Lisa Cirenza",
                  "fr": "Portfolio : Strates du temps et l'Archive · Lisa Cirenza"},
        "description": {"en": "Paintings by Lisa Cirenza in encaustic, mixed media, oil and watercolour: A Record of Time (ice, water, rock and light in the French Alps), then the Archive of earlier series.",
                        "fr": "Peintures de Lisa Cirenza à l'encaustique, en technique mixte, à l'huile et à l'aquarelle : Strates du temps (glace, eau, roche et lumière des Alpes), puis l'Archive des séries précédentes."}},
    "artiste": {
        "titre": {"en": "Lisa Cirenza: artist statement and biography",
                  "fr": "Lisa Cirenza : déclaration d'artiste et biographie"},
        "description": {"en": "Painter in the French Alps, former field researcher on the Juneau Icefield, Stanford-trained: Lisa Cirenza's statement, long bio and short bio for press.",
                        "fr": "Peintre dans les Alpes, ancienne chercheuse de terrain sur le champ de glace de Juneau, formée à Stanford : déclaration, biographie longue et biographie courte pour la presse."}},
    "studio": {
        "titre": {"en": "Studio notes: A Record of Time in progress · Lisa Cirenza",
                  "fr": "Notes d'atelier : Strates du temps en cours · Lisa Cirenza"},
        "description": {"en": "Why Lisa Cirenza paints glaciers and melt: the story behind A Record of Time, the works on her easel, research and process in encaustic.",
                        "fr": "Pourquoi Lisa Cirenza peint les glaciers et la fonte : l'histoire de Strates du temps, les œuvres sur son chevalet, recherches et procédé à l'encaustique."}},
    "parcours": {
        "titre": {"en": "CV: education, collections and exhibitions · Lisa Cirenza",
                  "fr": "Parcours : formation, collections et expositions · Lisa Cirenza"},
        "description": {"en": "Selected CV of Lisa Cirenza: Stanford University, Juneau Icefield Research Program, Stanford Hospital collection, Grand Palais Paris, Personal Structures in Venice, art fairs and talks.",
                        "fr": "Parcours sélectif de Lisa Cirenza : Stanford, Juneau Icefield Research Program, collection du Stanford Hospital, Grand Palais à Paris, Personal Structures à Venise, foires et conférences."}},
    "presse": {
        "titre": {"en": "Press: Financial Times, Wax Fusion, M2616 · Lisa Cirenza",
                  "fr": "Presse : Financial Times, Wax Fusion, M2616 · Lisa Cirenza"},
        "description": {"en": "Lisa Cirenza in the press: Rachel Spence in the Financial Times, Wax Fusion (International Encaustic Artists), M2616, Maisons et Jardins (May 2022), a BBC documentary and a podcast.",
                        "fr": "Lisa Cirenza dans la presse : Rachel Spence dans le Financial Times, Wax Fusion (International Encaustic Artists), M2616, Maisons et Jardins, un documentaire de la BBC et un podcast."}},
    "espace": {
        "titre": {"en": "Espace Créa-Tea-Vité: gallery, tea room and studio in La Clusaz",
                  "fr": "Espace Créa-Tea-Vité : galerie, salon de thé et atelier à La Clusaz"},
        "description": None},
    "cours": {
        "titre": {"en": "Art classes and open studio in La Clusaz · Espace Créa-Tea-Vité",
                  "fr": "Cours d'art et atelier ouvert à La Clusaz · Espace Créa-Tea-Vité"},
        "description": {"en": "Watercolour, encaustic and mixed-media classes and open studio sessions with Lisa Cirenza at Espace Créa-Tea-Vité, La Clusaz, French Alps.",
                        "fr": "Cours d'aquarelle, d'encaustique et de techniques mixtes, et séances d'atelier ouvert avec Lisa Cirenza à l'Espace Créa-Tea-Vité, à La Clusaz."}},
    "cours_prives": {
        "titre": {"en": "Bespoke art courses and workshops in La Clusaz · Espace Créa-Tea-Vité",
                  "fr": "Cours et ateliers d'art sur mesure à La Clusaz · Espace Créa-Tea-Vité"},
        "description": {"en": "Bespoke art sessions with Lisa Cirenza for individuals, families, groups, teams and event planners in La Clusaz: wax and mixed media, monoprinting, the artist's eye, abstraction, iPad art.",
                        "fr": "Séances d'art sur mesure avec Lisa Cirenza pour particuliers, familles, groupes, équipes et organisateurs à La Clusaz : cire et techniques mixtes, monotype, regard d'artiste, abstraction, iPad."}},
    "evenements": {
        "titre": {"en": "Gather at the Espace: private venue hire in La Clusaz",
                  "fr": "Se réunir à l'Espace : location d'un lieu privé à La Clusaz"},
        "description": {"en": "Hire Espace Créa-Tea-Vité in La Clusaz for private events, dinners, receptions and art-thinking team building: up to 18 guests seated, 40 standing.",
                        "fr": "Privatisez l'Espace Créa-Tea-Vité à La Clusaz pour vos événements, dîners, réceptions et ateliers d'équipe : jusqu'à 18 personnes assises, 40 debout."}},
    "retraites": {
        "titre": {"en": "Painting retreats 2027 in La Clusaz, French Alps",
                  "fr": "Retraites de peinture 2027 à La Clusaz, dans les Alpes"},
        "description": {"en": "Two painting retreats with Lisa Cirenza in La Clusaz in 2027: Painting in Paradise (21 – 26 June) and Alpine Creative Pause (6 – 11 September). Small groups, from €2,450.",
                        "fr": "Deux retraites de peinture avec Lisa Cirenza à La Clusaz en 2027 : Peindre au paradis (21 – 26 juin) et Pause créative alpine (6 – 11 septembre). Petits groupes, dès 2 450 €."}},
    "boutique": {
        "titre": {"en": "Commissions and Available Works · Lisa Cirenza Fine Art",
                  "fr": "Commandes et œuvres disponibles · Lisa Cirenza Fine Art"},
        "description": {"en": "Available works by Lisa Cirenza: original encaustics, archival prints printed and shipped by creativehub, and collectors' editions in acrylic.",
                        "fr": "Les œuvres disponibles de Lisa Cirenza : encaustiques originales, tirages d'art imprimés et expédiés par creativehub, et éditions de collection en acrylique."}},
    "salon_the": {
        "titre": {"en": "Boutique & Tea Room · Espace Créa-Tea-Vité, La Clusaz",
                  "fr": "Boutique et salon de thé · Espace Créa-Tea-Vité, La Clusaz"},
        "description": {"en": "Visit the Espace Créa-Tea-Vité boutique and tea room in La Clusaz: art materials and local gifts, signature lattes, hot cocoa and teas. Opening hours, map and parking.",
                        "fr": "La boutique et le salon de thé de l'Espace Créa-Tea-Vité à La Clusaz : matériel d'art et cadeaux locaux, lattes signature, chocolat chaud et thés. Horaires, plan et stationnement."}},
    "cosessions": {
        "titre": {"en": "Co-Creating Sessions: open studio in La Clusaz · Espace Créa-Tea-Vité",
                  "fr": "Sessions de co-création : atelier ouvert à La Clusaz · Espace Créa-Tea-Vité"},
        "description": {"en": "Work on your own creative projects with personalised guidance from Lisa Cirenza, a warm drink included, at Espace Créa-Tea-Vité in La Clusaz. €30 per session.",
                        "fr": "Avancez sur vos projets créatifs avec les conseils personnalisés de Lisa Cirenza, boisson chaude comprise, à l'Espace Créa-Tea-Vité à La Clusaz. 30 € la séance."}},
    "expositions": {
        "titre": {"en": "Exhibitions & Events: La Gravité de la Grâce · Espace Créa-Tea-Vité",
                  "fr": "Expositions et événements : La Gravité de la Grâce · Espace Créa-Tea-Vité"},
        "description": {"en": "La Gravité de la Grâce, December 2026 – April 2027 at Espace Créa-Tea-Vité, La Clusaz: Lisa Cirenza's new series, photographs by Le Petit Lapin and steel sculptures by BNT Designs.",
                        "fr": "La Gravité de la Grâce, décembre 2026 – avril 2027 à l'Espace Créa-Tea-Vité, La Clusaz : la nouvelle série de Lisa Cirenza, les photographies du Petit Lapin et les sculptures d'acier de BNT Designs."}},
    "conditions": {
        "titre": {"en": "Retreat payment schedule and cancellation policy · Espace Créa-Tea-Vité",
                  "fr": "Échéancier de paiement et conditions d'annulation des retraites · Espace Créa-Tea-Vité"},
        "description": {"en": "The €200 deposit, the payment schedule, cancellation fees, transfers and travel insurance for the 2027 painting retreats in La Clusaz.",
                        "fr": "L'acompte de 200 €, l'échéancier, les frais d'annulation, la cession de place et l'assurance voyage des retraites de peinture 2027 à La Clusaz."}},
    "inscription_pip": {"titre": {"en": "Painting in Paradise Registration", "fr": "Inscription · Peindre au paradis"},
                        "description": {"en": "Registration form for Painting in Paradise 2027.", "fr": "Formulaire d'inscription à Peindre au paradis 2027."}},
    "inscription_encaustics": {"titre": {"en": "Alpine Creative Pause Registration", "fr": "Inscription · Pause créative alpine"},
                               "description": {"en": "Registration form for Alpine Creative Pause 2027.", "fr": "Formulaire d'inscription à la Pause créative alpine 2027."}},
    "recherche": {"titre": {"en": "Search · Lisa Cirenza", "fr": "Rechercher · Lisa Cirenza"},
                  "description": {"en": "Search the works, pages and press of Lisa Cirenza and Espace Créa-Tea-Vité.", "fr": "Rechercher dans les œuvres, les pages et la presse de Lisa Cirenza et de l'Espace Créa-Tea-Vité."}},
    "contact": {
        "titre": {"en": "Contact Lisa Cirenza and Espace Créa-Tea-Vité, La Clusaz",
                  "fr": "Contacter Lisa Cirenza et l'Espace Créa-Tea-Vité, La Clusaz"},
        "description": {"en": "Ask about a work, a retreat, a private course or an event: write to Lisa Cirenza or visit Espace Créa-Tea-Vité, 27 Passage du Mont Blanc, La Clusaz.",
                        "fr": "Une œuvre, une retraite, un cours privé ou un événement : écrivez à Lisa Cirenza ou passez à l'Espace Créa-Tea-Vité, 27 Passage du Mont Blanc, à La Clusaz."}},
    "horaires": {
        "titre": {"en": "Opening hours editor (mock-up tool)", "fr": "Éditeur des horaires (outil de la maquette)"},
        "description": {"en": "Mock-up tool to edit the opening hours of Espace Créa-Tea-Vité.", "fr": "Outil de la maquette pour modifier les horaires de l'Espace Créa-Tea-Vité."}},
}

SUFFIXE_SALLE = {"en": "Works · Lisa Cirenza", "fr": "Œuvres · Lisa Cirenza"}
SUFFIXE_RETRAITE = {"en": "Painting retreat in La Clusaz", "fr": "Retraite de peinture à La Clusaz"}

# Ancien site Wix : 90 adresses du plan du site et 80 adresses vues dans Search Console (16 mois, lus le 20 novembre 2026,
# dont certaines déjà en 404 sur le site actuel). Chaque adresse renvoie vers sa page la plus proche (demande de Lisa :
# aucune ancienne page ne doit finir en 404). Sur la maquette, redirections temporaires ; au lancement, permanentes (301).
# Le français de Wix vit sous /fr/ avec les mêmes chemins : la même table sert avec le préfixe /fr.
ANCIEN_SITE = {
    # artiste
    "/bio": "artiste", "/cvhighlights": "parcours", "/about-9": "parcours", "/press": "presse", "/ft-article": "presse",
    "/artworks": "oeuvres", "/original-works": "oeuvres", "/commissions": ("salle", "commissions"), "/salon": "studio",
    "/shop-1": "boutique", "/product-page/:slug*": "boutique", "/art-collection-and-care": "studio", "/art-tech": "studio",
    "/feed": "studio", "/feed/:path*": "studio", "/single-post/:path*": "studio",
    # Espace
    "/espace-crea-tea-vite": "espace", "/salon-de-crea-tea-vite": "salon_the", "/espace-crea-tea-vite/wineandart": "evenements",
    "/privateclasses": "cours_prives", "/privatecourses": "cours_prives", "/single-project": "cours_prives",
    "/privatehire": "evenements", "/service-page/co-creating-sessions": "cosessions", "/booking-calendar/co-creating-sessions": "cosessions",
    "/book-online": "cosessions", "/pricing-plans/plans-pricing": "cosessions", "/thebasicscourse": "cosessions",
    "/sansfrontiere": "cosessions", "/creativitesansfrontieres": "cosessions", "/boundlesscreativity": "cosessions",
    "/service-page/:slug*": "cosessions",
    "/service-page/wine-tasting-art": "evenements", "/service-page/regardscuban": "expositions", "/cubasoir%C3%A9e": "expositions",
    "/service-page/randonnez-observez-peignez": "cours_prives",
    "/exhibitions": "expositions", "/about-3": "expositions", "/connect": "contact",
    "/inquiry-services-page": "contact", "/payment-request-page": "contact",
    # retraites
    "/june2027retreat": "pip", "/service-page/juneregistration2027": "pip", "/service-page/painting-in-paradise-2027-june": "pip",
    "/event-details/painting-in-paradise-2027-june": "pip", "/event-details/painting-in-paradise-2027-june-2027-06-21-15-00": "pip",
    "/sept2027alpinepause": "encaustics", "/sept2027waxretreat": "encaustics", "/service-page/registrationsept2027": "encaustics",
    "/event-details/autumn-alpine-pause": "encaustics", "/service-page/molten-magic-september-2027": "encaustics",
    "/copy-of-website-terms-and-privacy-policy": "conditions",
    "/retreat": "retraites", "/retreat1": "retraites", "/aug2026retreat": "retraites", "/retreatlodging": "retraites",
    "/residencysupplies": "retraites", "/service-page/molten-may-invitational-residency-2027": "retraites",
    "/service-page/registration-2026": "retraites", "/service-page/registration-closed-for-2025": "retraites",
    # pages techniques et anciennes pages sans équivalent
    "/website-terms-and-privacy-policy": "conditions_site", "/general-4": "accueil", "/archived-pages": "accueil", "/ubu": "accueil",
}
# Ordre : les adresses précises d'abord, puis les motifs (Vercel applique la première règle qui correspond)
MOTIFS = ("/product-page/:slug*", "/feed/:path*", "/single-post/:path*", "/service-page/:slug*")
# Anciennes adresses de la maquette elle-même (v4 et v5)
ANCIENNES_MAQUETTE = {
    "/retreats/molten-magic": "encaustics", "/retreats/alpine-pause": "encaustics", "/retreats/alpine-encaustics": "encaustics",
    "/retreats/creative-pause": "retraites", "/works/light-water-rock-and-time": ("salle", "record-of-time"),
    "/private-courses": "cours_prives", "/private-events": "evenements", "/shop": "boutique", "/classes": "cosessions",
}
ANCIENNES_MAQUETTE_FR = {
    "/fr/retraites/molten-magic": "encaustics", "/fr/retraites/alpine-pause": "encaustics", "/fr/retraites/alpine-encaustics": "encaustics",
    "/fr/retraites/creative-pause": "retraites", "/fr/oeuvres/lumiere-eau-roche-et-temps": ("salle", "record-of-time"),
    "/fr/cours-prives": "cours_prives", "/fr/evenements-prives": "evenements", "/fr/boutique": "boutique", "/fr/cours": "cosessions",
}
A_DECIDER = [
    "Le blog : 35 articles (2015 – 2019) toujours dans Wix Blog avec leurs dates ; à afficher sur /blog/<adresse> (même contenu, sans migration), puis rediriger /single-post/<adresse> article par article.",
]
