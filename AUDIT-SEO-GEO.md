# Audit SEO et GEO · maquette v5 (20 novembre 2026)

SEO : référencement dans Google et Bing. GEO : présence dans les réponses des moteurs IA (ChatGPT, Perplexity,
Gemini, Claude, aperçus IA de Google). La maquette reste en **noindex** jusqu'au lancement : tout ce qui suit est
prêt à servir le jour où le site passe sur cirenza.com.

## Ce qui est en place dans la maquette

| Point | État |
|---|---|
| Titres | 53 pages, 53 titres uniques. Anglais et français distincts. Nom et année pour les retraites. |
| Descriptions | Une par page, 160 signes au plus. Les salles reprennent le texte de leur série. |
| Un seul `h1` par page | Vérifié sur toutes les pages, sur ordinateur et sur mobile. |
| Adresse de référence (`canonical`) | Sur chaque page, en adresse absolue. |
| Langues (`hreflang`) | `en`, `fr` et `x-default` (anglais) sur chaque page. Pas de redirection forcée : une invitation discrète propose l'autre langue. |
| Données structurées (schema.org) | Person (Lisa), ProfilePage, WebSite, ArtGallery et CafeOrCoffeeShop (l'Espace, avec horaires), Event (les trois retraites, prix et dates), FAQPage, ItemList de VisualArtwork (salles), BreadcrumbList. |
| Plan du site | `sitemap.xml` : 50 adresses avec leurs équivalents dans l'autre langue. |
| `robots.txt` | Autorise tout sauf l'outil des horaires ; indique le plan du site. |
| `llms.txt` | Résumé factuel pour les moteurs IA : bio courte, faits à ne pas déformer, Espace, retraites, pages. |
| FAQ visibles | Page des retraites (6 questions), Painting in Paradise. |
| Horaires | Une seule source : la page, les données structurées et `llms.txt` disent la même chose. |
| Images | Textes alternatifs décrits, images légères (WebP), chargement différé. Vidéos et podcast chargés au clic. |
| Anciennes adresses | 57 redirections depuis le site Wix actuel (voir plus bas). |

## Le jour du lancement

1. Dans `outils/generer.py`, `SITE_URL` passe à `https://www.cirenza.com`. Régénérer : les adresses de référence,
   le plan du site, les données structurées et `llms.txt` suivent.
2. Retirer le noindex : la balise `robots` des pages et l'en-tête `X-Robots-Tag` de `vercel.json`.
3. Passer les redirections en permanentes (`"permanent": true`, code 308 chez Vercel, équivalent d'un 301).
4. Google Search Console et Bing Webmaster Tools : valider le domaine, soumettre `sitemap.xml`, demander
   l'indexation des pages principales.
5. Fiche Google de l'Espace (Google Business Profile). Même nom, même adresse et même téléphone que le site :
   *Espace Créa-Tea-Vité, 27 Passage du Mont Blanc, 74220 La Clusaz, +33 7 49 09 54 92*. Mêmes horaires, et les
   fermetures exceptionnelles reportées.
6. Tests : outil « Résultats enrichis » de Google sur l'accueil, une retraite et une salle ; Lighthouse sur mobile.

## Plan de redirection de l'ancien site (sitemap de cirenza.com, 90 adresses lues le 20 novembre 2026)

Redirigées (`outils/seo.py`, `ANCIEN_SITE`, en anglais et sous `/fr`) :

| Ancienne adresse | Nouvelle page |
|---|---|
| /bio, /about-3 | L'artiste |
| /cvhighlights, /exhibitions | Parcours |
| /ft-article (/press garde son nom) | Presse |
| /artworks, /original-works | Œuvres |
| /commissions | Salle Commissions |
| /espace-crea-tea-vite, /salon | L'Espace |
| /privateclasses | Cours privés |
| /privatehire, /service-page/co-creating-sessions, /service-page/wine-tasting-art | Événements privés |
| /service-page/randonnez-observez-peignez | Cours |
| /june2027retreat, /service-page/juneregistration2027, /event-details/painting-in-paradise-2027-june(…) | Painting in Paradise |
| /sept2027alpinepause, /sept2027waxretreat, /service-page/registrationsept2027, /event-details/autumn-alpine-pause | Alpine Encaustics |
| /connect | Contact |
| /product-page/* | Boutique |

À trancher avec Lisa (aucune redirection devinée) :
- **Le blog :** 30 articles (`/single-post/…`) et `/feed`. Conseil : les reprendre dans Wix Blog avec les mêmes
  adresses. Ils ont de l'ancienneté et des liens entrants. À défaut, rediriger chaque article vers Notes d'atelier.
- **`/service-page/molten-may-invitational-residency-2027` :** une résidence en mai 2027 encore en ligne. Elle
  croise A Creative Pause (15 – 20 mai 2027) : existe-t-elle toujours ?
- **`/pricing-plans/plans-pricing` :** des formules d'abonnement, peut-être le cercle de mentorat en ligne. À garder ?
- **`/book-online`, `/service-page/regardscuban`, `/art-collection-and-care`, `/art-tech` :** pages de réservation,
  d'événement passé et catégories de blog.
- **`/website-terms-and-privacy-policy` :** à rediriger vers les futures mentions légales.
- **Pages techniques de Wix** (`/inquiry-services-page`, `/payment-request-page`, `/general-4`, `/single-project`) :
  à laisser disparaître.

## GEO : être cité juste par les moteurs IA

Les moteurs de réponse recoupent les sources. Ce qui compte, c'est que **tous les profils de Lisa disent la même
chose** et que le site donne des faits nets.

- **Déjà dans le site :**
  - les faits que le brief demande de ne pas déformer : chercheuse de terrain sur le champ de glace de Juneau (pas
    glaciologue) ; Personal Structures, European Cultural Centre, Palazzo Mora, pendant la 59e Biennale de Venise ;
    Talloires est une excursion ;
  - bio courte reprise mot pour mot ;
  - FAQ ;
  - `sameAs` vers Instagram, LinkedIn, Facebook et Artwork Archive.
- **À faire par Lisa :**
  - **Artwork Archive :** son profil public se présente encore comme *« Multimedia artist, exploring the delicate
    dynamics of human relationships… »*. Le brief écarte « Multimedia Artist » : reprendre la bio courte du site.
  - **Instagram, LinkedIn, Facebook, fiche Google de l'Espace :** même phrase d'accroche (*Painter of light, water,
    rock and time*), même lien vers le site.
  - **Partenaires :** les articles de presse et l'office de tourisme de La Clusaz doivent pointer vers le nouveau site.
- **À suivre après le lancement :** poser régulièrement aux moteurs IA les questions que se posent les visiteurs
  (« painting retreat French Alps », « galerie salon de thé La Clusaz », « Lisa Cirenza ») et corriger les sources
  quand une réponse est fausse.
