# Lisa Cirenza · maquette v2 (direction « Strates »)

Site statique (HTML, CSS, JavaScript), sans étape de construction, prêt pour Vercel.

- Anglais à la racine (version officielle), français sous `/fr/`.
- 41 pages : accueil, œuvres et 8 salles, l'artiste, parcours, presse, l'Espace Créa-Tea-Vité, cours, événements privés, retraites (Painting in Paradise, Molten Magic), contact, 404.
- `vercel.json` : adresses propres (`cleanUrls`), sans barre finale.
- Polices hébergées avec le site (`assets/polices`) : Fraunces et IBM Plex Mono, licence SIL OFL (fichiers joints).
- Formulaires simulés : aucun message n'est envoyé, le visiteur peut ouvrir un courriel prérempli.

## v2

- « Voir au mur » : toile, règle et silhouette tiennent toujours dans l'écran, à l'échelle réelle.
- Grattage de cire : légende alignée sur la toile.
- Six bandes de photos réelles qui glissent au défilement : cours, Espace, artiste, parcours, événements, retraites.

## Modifier les contenus

Les textes et données sont dans `outils/` (exclu du déploiement) : `contenu.py`, `retraites.py`, `catalogue.py`.
Puis, depuis le dossier du site : `python3 outils/generer.py . --liens propres`

Les informations absentes du site actuel sont marquées « à compléter » ou « prix sur demande ».
