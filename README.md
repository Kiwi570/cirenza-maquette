# Lisa Cirenza · maquette v1 (direction « Strates »)

Site statique (HTML, CSS, JavaScript), sans étape de construction, prêt pour Vercel.

- Anglais à la racine (version officielle), français sous `/fr/`.
- 41 pages : accueil, œuvres et 8 salles, l'artiste, parcours, presse, l'Espace Créa-Tea-Vité, cours, événements privés, retraites (Painting in Paradise, Molten Magic), contact, 404.
- `vercel.json` : adresses propres (`cleanUrls`), sans barre finale.
- Polices hébergées avec le site (`assets/polices`) : Fraunces et IBM Plex Mono, licence SIL OFL (fichiers joints).
- Formulaires simulés : aucun message n'est envoyé, le visiteur peut ouvrir un courriel prérempli.

## Effets

Ouverture « carotte de cire » qui fond (WebGL, version CSS sans WebGL), révélation des images en coulure de cire,
salles d'œuvres horizontales, fiche d'œuvre avec loupe HD et « Voir au mur » à l'échelle, grattage de cire,
colonne stratigraphique des séries, frise du parcours, carte des retraites tracée au défilement, statut ouvert ou fermé
de l'Espace (heure de Paris), comptes à rebours, curseur chalumeau, altimètre. Tout respecte « réduire les animations ».

## Modifier les contenus

Les textes et données sont dans `outils/` (exclu du déploiement) :

- `outils/contenu.py` : textes, coordonnées, horaires, presse, expositions, carte des boissons, agenda.
- `outils/retraites.py` : les deux retraites.
- `outils/catalogue.py` : œuvres (titre, dimensions, technique, année, statut).

Puis, depuis le dossier du site :

```
python3 outils/generer.py . --liens propres
```

Les informations absentes du site actuel sont marquées « à compléter » ou « prix sur demande ».
