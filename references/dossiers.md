# Dossiers, noms et index

Le `CLAUDE.md` de la ludothèque peut nommer autrement le dossier de dépôt ; ses chemins machine (python.exe…)
s'y notent aussi, pas dans la skill (dépôt git partagé).

- **dépôt** : les PDF à traduire sont déposés dans `<Ludothèque>/A traduire/`.
- **outils** : pendant le travail, tout ce qui sert au jeu va dans `<Ludothèque>/_outils/<Jeu>/` — jamais dans
  le dossier de dépôt ni dans le dossier du jeu. Après livraison il ne garde que `spec.py` (la traduction), les
  scripts, `ff/` (polices allégées) et `NOTES.md`.
- **livraison** : le PDF d'origine et `<nom>_FR.pdf` sont **déplacés** dans `<Ludothèque>/<Jeu>/` (créé si
  besoin) — `livrer.py` le fait. Les dossiers de jeu ne contiennent que les livrets et ce que l'utilisateur y a
  mis lui-même : ne rien y toucher d'autre, ne rien écraser sans demander.
- **index** : `<Ludothèque>/_outils/LISEZMOI.md`, une ligne par jeu (Jeu | Langue | Éditeur | Type |
  Polices | Date), tenue par `livrer.py`. Ne pas le lire en entier quand il est long : `grep -i` sur l'éditeur,
  la police ou la langue.
- **notes du jeu** : `_outils/<Jeu>/NOTES.md` (livrets, langue d'origine, éditeur, type, polices et leur origine,
  vocabulaire propre au jeu, choix et compromis, astuces du spec). Écrites à la main avant `livrer.py`, qui lit
  « Langue d'origine : » et « Éditeur : » pour l'index. Ne lire que celles des jeux proches.
- Sans dossier de dépôt (PDF posé ailleurs) : outils dans `_outils/<Jeu>/` à côté du PDF, rien n'est déplacé.

## Nom `<Jeu>`
Titre imprimé en lettres latines (titre anglais officiel ou romanisation pour un titre japonais, chinois…),
nettoyé pour Windows — `preparer.py` le fait :
- supprimer les virgules, les points d'exclamation et `\ / : * ? " < > |` (« After You, Betobeto-san » →
  « After You Betobeto-san », « Dune: Imperium » → « Dune Imperium ») ;
- garder accents, apostrophes, tirets et parenthèses ; une seule espace entre les mots, ni espace ni point final ;
- noms réservés de Windows (`CON`, `PRN`, `AUX`, `NUL`, `COM1`…, `LPT1`…) : ajouter « (jeu) ».
Si un dossier du jeu existe déjà (autre édition, extension, nom choisi par l'utilisateur), s'en servir tel quel
(passer ce nom à `preparer.py`). S'il est renommé après coup : relancer `livrer.py` n'est pas utile, mettre à
jour `SRC` dans `spec.py`, la ligne d'index et `NOTES.md`.
