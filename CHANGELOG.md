# Changelog

Toutes les évolutions notables du plugin. Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/),
numérotation [sémantique](https://semver.org/lang/fr/).

## [1.0.0] — 2026-10-27
### Ajouté
- Plugin `regles-jeu` : réunion des skills `recherche-regles-jeu` (devenue `rechercher`) et
  `traduction-regles-jeu` (devenue `traduire`), avec tout leur historique.
- Agents relecteurs fournis avec le plugin : `regles-jeu:relecteur-texte` et `regles-jeu:relecteur-visuel`.
- Boutique d'installation (`/plugin marketplace add vinchy1/regles-jeu`).

### Changé
- Commandes directes : `/regles-jeu:rechercher` et `/regles-jeu:traduire`.
- La skill de traduction évolue indépendamment du dépôt de notoriousFabb.

### Contenu repris des anciennes skills
- Version anglaise des livrets (`_EN.pdf`) depuis une seule spec bilingue.
- Rendu « recomposer » pour les scans froissés, fond « dominant » des masques.
- Livraison d'une traduction faite sans spec (`livrer.py --pdf`).
- Fichiers de travail allégés (moins de jetons).
