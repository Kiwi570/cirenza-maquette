"""Référencement (SEO) et moteurs de réponse (GEO) : titres, descriptions, redirections de l'ancien site.

Chaque page a un titre et une description uniques, en anglais (version officielle) et en français.
Les faits cités sont ceux du site (brief de Lisa) : rien n'est inventé pour le référencement.
À la mise en ligne : SITE_URL passe à https://www.cirenza.com (outils/generer.py), le noindex est retiré,
et les redirections passent en permanentes (301).
"""

PAGES = {
    "oeuvres": {
        "titre": {"en": "Works: A Record of Time and the Archive · Lisa Cirenza",
                  "fr": "Œuvres : Strates du temps et l'Archive · Lisa Cirenza"},
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
        "description": {"en": "Lisa Cirenza in the press: Rachel Spence in the Financial Times, Wax Fusion (International Encaustic Artists), M2616, Maisons et Jardins, a BBC documentary and a podcast.",
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
        "titre": {"en": "Private art courses for hotels and concierges in La Clusaz",
                  "fr": "Cours d'art privés pour hôtels et conciergeries à La Clusaz"},
        "description": {"en": "Bespoke private art sessions for hotel guests, concierges and event planners in La Clusaz: wax and mixed media, monoprinting, the artist's eye, abstraction, iPad art, outdoors.",
                        "fr": "Séances d'art privées sur mesure pour les clients d'hôtels, conciergeries et organisateurs à La Clusaz : cire et techniques mixtes, monotype, regard d'artiste, abstraction, iPad, plein air."}},
    "evenements": {
        "titre": {"en": "Private events and team workshops · Espace Créa-Tea-Vité, La Clusaz",
                  "fr": "Événements privés et ateliers d'équipe · Espace Créa-Tea-Vité, La Clusaz"},
        "description": {"en": "Hire Espace Créa-Tea-Vité in La Clusaz for private events, aperitifs in the gallery and creative team workshops led by Lisa Cirenza.",
                        "fr": "Privatisez l'Espace Créa-Tea-Vité à La Clusaz : événements privés, apéritifs dans la galerie et ateliers créatifs d'équipe animés par Lisa Cirenza."}},
    "retraites": {
        "titre": {"en": "Painting retreats 2027 in La Clusaz, French Alps",
                  "fr": "Retraites de peinture 2027 à La Clusaz, dans les Alpes"},
        "description": {"en": "Three five-night painting retreats with Lisa Cirenza in La Clusaz in 2027: A Creative Pause (May), Painting in Paradise (June), Alpine Encaustics (September). Small groups, from €2,450.",
                        "fr": "Trois retraites de peinture de cinq nuits avec Lisa Cirenza à La Clusaz en 2027 : A Creative Pause (mai), Painting in Paradise (juin), Alpine Encaustics (septembre). Petits groupes, dès 2 450 €."}},
    "boutique": {
        "titre": {"en": "Shop: original works, prints and collectors' editions · Lisa Cirenza",
                  "fr": "Boutique : œuvres originales, tirages et éditions de collection · Lisa Cirenza"},
        "description": {"en": "Buy original encaustics, archival prints (printed and shipped by creativehub) and collectors' editions in acrylic by Lisa Cirenza, plus studio sessions at Espace Créa-Tea-Vité.",
                        "fr": "Œuvres originales à l'encaustique, tirages d'art (imprimés et expédiés par creativehub) et éditions de collection en acrylique de Lisa Cirenza, et séances d'atelier à l'Espace Créa-Tea-Vité."}},
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

# Ancien site Wix (sitemap de cirenza.com lu le 20 novembre 2026, 90 adresses) : où envoyer chaque adresse.
# Sur la maquette, redirections temporaires ; à la mise en ligne sur cirenza.com, permanentes (301).
# Le français de Wix vit sous /fr/ avec les mêmes chemins : la même table sert avec le préfixe /fr.
ANCIEN_SITE = {
    "/bio": "artiste", "/about-3": "artiste",
    "/cvhighlights": "parcours", "/exhibitions": "parcours",
    "/press": "presse", "/ft-article": "presse",
    "/artworks": "oeuvres", "/original-works": "oeuvres", "/commissions": ("salle", "commissions"),
    "/espace-crea-tea-vite": "espace", "/salon": "espace",
    "/privateclasses": "cours_prives", "/privatehire": "evenements",
    "/service-page/co-creating-sessions": "evenements", "/service-page/wine-tasting-art": "evenements",
    "/service-page/randonnez-observez-peignez": "cours",
    "/june2027retreat": "pip", "/service-page/juneregistration2027": "pip",
    "/event-details/painting-in-paradise-2027-june": "pip", "/event-details/painting-in-paradise-2027-june-2027-06-21-15-00": "pip",
    "/sept2027alpinepause": "encaustics", "/sept2027waxretreat": "encaustics", "/service-page/registrationsept2027": "encaustics",
    "/event-details/autumn-alpine-pause": "encaustics",
    "/connect": "contact",
    "/product-page/:slug": "boutique",
}
# Adresses à trancher avec Lisa (pas de redirection devinée) : voir AUDIT-SEO-GEO.md
A_DECIDER = [
    "/book-online", "/pricing-plans/plans-pricing", "/service-page/molten-may-invitational-residency-2027",
    "/service-page/regardscuban", "/art-collection-and-care", "/art-tech", "/feed et /feed/categories/*",
    "/single-post/* (30 articles de blog)", "/website-terms-and-privacy-policy",
    "/inquiry-services-page", "/payment-request-page", "/general-4", "/single-project",
]
