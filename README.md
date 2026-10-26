# regles-jeu — plugin Claude Code

Deux skills qui s'enchaînent, pour jouer en français (ou en anglais) à des jeux venus d'ailleurs :

| Skill | Rôle | Appel direct |
|---|---|---|
| [rechercher](skills/rechercher/README.md) | trouve sur internet le livret de règles d'un jeu (Tokyo Game Market, BoardGameGeek, site de l'éditeur) et l'enregistre en PDF intégral | `/regles-jeu:rechercher <jeu>` |
| [traduire](skills/traduire/README.md) | traduit le livret en français (et en anglais si demandé) en conservant la mise en page ; gère aussi les scans | `/regles-jeu:traduire <livret.pdf>` |

Les skills se déclenchent aussi toutes seules : « trouve les règles de Cat in the Box », « traduis-moi ce PDF ».
Le plugin installe aussi les deux agents relecteurs de la traduction, `regles-jeu:relecteur-texte` et
`regles-jeu:relecteur-visuel`.

---

## Installation
Dans Claude Code :
```
/plugin marketplace add vinchy1/regles-jeu
/plugin install regles-jeu@regles-jeu
```
(en ligne de commande : `claude plugin marketplace add vinchy1/regles-jeu`, puis
`claude plugin install regles-jeu@regles-jeu`).

Puis les prérequis propres à chaque skill (Python et ses bibliothèques, dossier `A traduire`) : voir
[rechercher](skills/rechercher/README.md#installation) et [traduire](skills/traduire/README.md#installation).

### Pour modifier le plugin
Cloner le dépôt dans le dossier des skills : Claude Code le charge directement, sans copie, et chaque modification
est prise en compte à la session suivante (ou avec `/reload-plugins`).
```
git clone https://github.com/vinchy1/regles-jeu.git ~/.claude/skills/regles-jeu
```
Ne pas installer en plus la version de la boutique : les skills apparaîtraient en double.

---

## Mise à jour
- Installé depuis la boutique : `/plugin marketplace update regles-jeu`, puis `/plugin update regles-jeu@regles-jeu`
  (ou demander à Claude « mets à jour le plugin regles-jeu »).
- Cloné dans le dossier des skills : `git -C ~/.claude/skills/regles-jeu pull --ff-only`.

---

## Contenu du dépôt
```
.claude-plugin/   plugin.json (description du plugin) et marketplace.json (boutique d'installation)
agents/           relecteur-texte.md et relecteur-visuel.md (Sonnet), relecteurs de la traduction
skills/
├── rechercher/   recherche du livret (SKILL.md, references/, scripts/)
└── traduire/     traduction du livret (SKILL.md, references/, scripts/, exemples/)
```

## Historique
Réunion, avec tout leur historique, des anciens dépôts
[recherche-regles-jeu](https://github.com/vinchy1/recherche-regles-jeu) et
[traduction-regles-jeu](https://github.com/vinchy1/traduction-regles-jeu). La skill de traduction a été initiée par
[notoriousFabb](https://github.com/notoriousFabb/traduction-regles-jeu) ; ce dépôt évolue de façon indépendante, et
le dépôt d'origine reste noté comme source facultative, repris seulement à la demande
(`git fetch notoriousfabb`, puis `git merge -X subtree=skills/traduire notoriousfabb/main`).

**Usage personnel** : ne diffusez les livrets traduits qu'avec l'accord de l'éditeur du jeu.
