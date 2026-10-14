# traduction-regles-jeu — skill Claude Code

Traduit en français un livret de règles de jeu de société au format PDF (anglais → français) **en gardant
exactement la mise en page** : polices, illustrations, icônes dans le texte, encadrés, positions.
Le résultat est un `<nom>_FR.pdf` prêt à imprimer.

Testée sur des livrets de jeux de plis (Trick to the Future, Numberwang±, Fright Factor, Dr. Science,
Tricklings / Vazerneiros).

## Ce qu'elle fait
- retire le texte anglais du PDF sans toucher aux images ni aux dessins vectoriels ;
- pose le texte français au même endroit, avec des polices libres proches de l'originale (les polices
  embarquées n'ont presque jamais les accents), en réduisant légèrement la taille si le français est plus long ;
- replace les icônes intégrées au texte (symboles de couleur, étoiles, lettres cerclées…) au bon endroit dans
  la phrase française ;
- traduit aussi le texte des cartes reproduites dans le livret ;
- respecte la typographie française et un glossaire cohérent entre les jeux (pli, entamer, fournir, atout…) ;
- relit chaque page côte à côte avec l'original et signale les compromis.

## Installation
1. Copier le dossier `traduction-regles-jeu` dans `~/.claude/skills/` (Windows : `C:\Users\<vous>\.claude\skills\`).
2. Installer Python 3 et les bibliothèques : `pip install pymupdf fonttools`.
3. Dans Claude Code, déposer le PDF anglais dans votre dossier de travail et demander :
   « Traduis-moi ce livret de règles : MonJeu_rules.pdf ».

## Contenu
- `SKILL.md` — méthode et préférences de traduction
- `references/` — glossaire, choix des polices de remplacement, pièges connus et solutions
- `scripts/` — `build.py` (moteur de reconstruction), `spec_modele.py` (modèle de traduction),
  `dump.py` (inventaire du texte), `side.py` / `sheet.py` (images de relecture)

## Remarques
- Usage personnel : ne diffusez les livrets traduits qu'avec l'accord de l'éditeur du jeu.
- Une traduction complète consomme beaucoup de jetons (de l'ordre de 150 à 200 k pour 12-16 pages),
  surtout à cause des images de relecture.
