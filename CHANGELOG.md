# Changelog

Toutes les évolutions notables du plugin. Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/),
numérotation [sémantique](https://semver.org/lang/fr/).

## [1.2.0] — 2026-10-28
### Ajouté
- Version allégée d'un livret pour Discord (10 Mo) : `livrer.py` signale tout livret livré qui atteint 10 Mo,
  et `comprimer.py` (nouveau) écrit `<nom>_light.pdf` à côté du livret, qui reste intact en pleine qualité.
  Essais du plus doux au plus serré, arrêtés au premier qui passe ; le texte, vectoriel, n'est pas touché et
  l'égalité du texte est vérifiée après coup. Documentation : `skills/traduire/references/alleger.md`.

## [1.1.0] — 2026-10-27
### Ajouté
- Version économe en encre d'un livret à fond sombre, à la demande de l'utilisateur : `build.py --fond-clair`
  (nouveau `encre.py`), `noir.py --clair` pour un livret recomposé, `livrer.py --encre` pour livrer
  `<nom>_FR_encre.pdf` à côté du livret normal. Documentation : `skills/traduire/references/encre.md`.
  Le fond (image ou aplat) est retiré, les autres couleurs voient leur clarté inverser à teinte constante,
  le texte est assombri jusqu'à rester lisible, les illustrations gardent leurs couleurs. Les livrets scannés
  ne sont pas couverts.

### Corrigé
- `livrer.py` : la version anglaise n'est construite que si le spec appelle vraiment `X()`, et ne peut plus
  écraser le livret d'origine (correctif repris de notoriousFabb).

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
