---
name: traduction-regles-jeu
description: Traduit en français un livret de règles de jeu de société en PDF (anglais → français) en conservant exactement la mise en page — polices, images, icônes dans le texte, tableaux, positions — et produit un `*_FR.pdf`. À utiliser dès que l'utilisateur demande de traduire des règles, un livret, un rulebook ou un PDF de jeu (jeu de plis, jeu de cartes, jeu de société), même s'il ne dit que « traduis-moi ce PDF » ou donne juste un nom de fichier comme `xxx_rulebook.pdf` ou `Regles_EN.pdf` ; aussi pour corriger un mot ou une phrase dans une traduction déjà faite de cette façon.
---

# Traduction de livrets de règles (EN → FR, mise en page conservée)

L'utilisateur parle français, joue à des jeux de plis et ne touche pas aux scripts : il veut un PDF français
qui ressemble trait pour trait à l'original. Réponds-lui en français, sans jargon technique inutile.

## Préférences de l'utilisateur (importantes)
- Ne jamais traduire le titre du jeu ni les noms de variantes (Numberwang+, Tricklings…).
- Noms de cartes / personnages : anglais, avec le français entre parenthèses dans les titres
  (« The Bride (La Fiancée) ») ; nom anglais aussi dans le texte (« 0-Bride »).
- Vocabulaire cohérent entre jeux : pli, entamer, fournir, atout, manche, couleur, valeur, main, distribuer,
  paquet, décompte… → `references/glossaire.md` (le compléter à chaque jeu).
- Typographie française : « », espaces insécables avant ; : ! ? (le build les pose), décimales à virgule.
- Les polices embarquées n'ont généralement pas d'accents → polices libres proches (`references/polices.md`).
- Relire chaque page côte à côte (original / traduction) avant de livrer, et signaler les compromis : taille de
  police réduite, phrases condensées, textes dans les images non traduits, doublons de l'original.

## Environnement
- Python 3 avec pymupdf et fonttools (`pip install pymupdf fonttools`). Toujours lancer avec `-X utf8`.
  Sous Windows, si `python` ouvre le Microsoft Store, utiliser le chemin complet de python.exe
  (le noter ici une fois trouvé).
- Dossier de travail : celui où l'utilisateur dépose les PDF anglais ; les traductions y sont livrées
  (`<nom>_FR.pdf`). Les outils de chaque jeu traduit vont dans `_outils/<Jeu>/` (spec, build, polices `ff/`),
  avec un `_outils/LISEZMOI.md` à tenir à jour (polices et glossaire de chaque jeu).
- Scripts de la skill (`scripts/` à côté de ce fichier) : `build.py` (moteur générique), `spec_modele.py`,
  `dump.py`, `side.py`, `sheet.py`.

## Méthode
1. **Repérer le livret** : nombre de pages, polices (`page.get_fonts()`), texte brut ; `sheet.py` pour une
   planche d'aperçu, puis la regarder. Noter : icônes dans le texte, cartes illustrées contenant du texte,
   listes à puces, texte qui contourne des images, calques cachés.
2. **Créer `_outils/<Jeu>/`** et y copier `build.py`, `spec_modele.py` → `spec.py`, `side.py`, `dump.py`.
   Si un jeu déjà traduit est très proche, partir plutôt de son dossier (même éditeur, mêmes polices).
3. **Polices** : extraire les originales dans `fonts/`, vérifier leurs glyphes, choisir les remplaçantes dans
   `ff/` (planche comparative), régler en tête de `build.py` : `SRC`, `CSS` (@font-face), `CODE`
   (police d'origine → famille, gras, italique), `SIZE_K`, colonnes `XL/XR`.
4. **`dump.py livret.pdf`** → `blocks.txt` : chaque ligne avec police, taille, couleur, position. C'est la carte
   pour écrire le spec. Le lire en entier (les blocs PDF ne correspondent pas toujours aux paragraphes).
5. **Écrire `spec.py`** : un flux (`F`) par zone de texte, des paragraphes `P` / `C` (centré) / `L` (puce) /
   `T` (titre de carte), `{}` à l'emplacement de chaque icône, `maxy` = limite basse (image ou encadré
   suivant). Format détaillé dans l'en-tête de `spec_modele.py`. Traduire de façon concise : le français est
   ~15 % plus long et la place est comptée.
6. **Construire** : `python -X utf8 build.py sortie.pdf`. Lire le journal : « font scale » (police réduite),
   « OVERFLOW », « placeholders for N icons », « not re-placed » — chaque ligne mérite une correction ou un
   compromis assumé.
7. **Relire** : `side.py livret_EN.pdf sortie.pdf all` puis regarder chaque `sideN.png` ; zoomer
   (`get_pixmap(clip=…, dpi=300)`) sur les zones délicates. Corriger le spec (raccourcir, couper autrement,
   `fix=True`, `x1`…), reconstruire, relire. Vérifier qu'aucun marqueur « ¤ » ne reste dans le texte.
8. **Livrer** : copier vers `<nom>_FR.pdf` dans le dossier de travail, supprimer les images et fichiers
   temporaires, compléter `_outils/LISEZMOI.md` (polices, glossaire) et `references/glossaire.md`.
   Résumer à l'utilisateur : fichier, choix de vocabulaire, compromis.

`references/pieges.md` liste les difficultés déjà rencontrées (texte en double, pastilles numérotées,
texte autour des cartes, mini-cartes, calques cachés…) et leur solution : le lire avant d'écrire le spec.

## Économiser les jetons
Une traduction coûte ~170-200 k jetons, surtout à cause des images de relecture. Regarder les pages en
planches ou côte à côte à 100-110 dpi, ne zoomer que sur les problèmes, ne relire après correction que les
pages modifiées. Préférer modifier le spec par petits remplacements ciblés plutôt que tout réécrire.

## Correction d'une traduction existante
Ouvrir `_outils/<Jeu>/spec*.py`, changer le texte, relancer le `build.py` du dossier, relire la page,
recopier vers `<nom>_FR.pdf`.
