# Pièges rencontrés et solutions

La plupart sont déjà gérés par `scripts/build.py` ; ce qui reste à faire dans le spec est indiqué.

- **Texte imprimé deux fois** (faux gras / surimpression) : lignes identiques au même endroit → dédoublonnées
  automatiquement.
- **Calques cachés** (version dans une autre langue, texte tourné d0,-1) : ne pas les mettre dans le spec.
  Vérifier sur le rendu ce qui est réellement visible (couverture : « Regras » invisible, « Rules » visible).
- **Icônes dans le texte** : petites images (<22×16) ou grappes de tracés vectoriels (<14×14) sur la bande d'une
  ligne traduite → retirées puis replacées sur `{}`. Le nombre de `{}` doit égaler le nombre d'icônes (le build
  signale tout écart). Lettres cerclées A/B/C (cercle vectoriel + lettre texte) : voir la version de
  `_outils/Dr_Science/build.py`.
- **Puces dans le texte** (« •\t », « 1.\t » dans la même span) : `bullet="•"` ou `bullet="1."`, le retrait
  est conservé.
- **Numéros dans des pastilles** dessinées à gauche (étapes 1-5) : un flux par étape, ancré à sa position
  d'origine (maxy = début de l'étape suivante), sinon les pastilles ne suivent plus le texte.
- **Texte qui contourne une image** (lignes à côté d'une carte, puis pleine largeur) : couper le français en
  deux paragraphes (`b3:0-1` à côté, `b3:2` dessous) en choisissant la coupure pour que la 1re partie remplisse
  ses lignes ; le premier paragraphe pleine largeur après l'image prend `fix=True` pour ne pas remonter dessus.
- **Paragraphe en double dans l'original** : fusionner les sources dans un seul paragraphe (`lead=` pour forcer
  l'interligne) et le signaler.
- **Mini-cartes illustrées** (texte de 1 à 4 pt) : table `CARDS` + `CARD_PAGES` ; ne traduire que les cartes
  dont le texte est visible (cartes empilées : seulement celle de devant), sinon le français s'affiche
  par-dessus. Les styles qui distinguent numéro / ambiance / effet se
  règlent dans `CARD_STYLE` (voir `spec_modele.py`).
- **Mots soulignés** (traits dessinés sous la ligne, pas du texte) : le build retire ceux qui sont sous une
  ligne remplacée (journal : « soulignement(s) d'origine retiré(s) ») ; souligner le français avec
  `<u>…</u>` et `u {text-decoration:underline;}` dans le CSS du spec.
- **Polices du livret complètes** : si `polices.py glyphes` ne signale aucun manque (police embarquée en
  entier), copier simplement l'originale dans `ff/`.
- **Plusieurs colonnes par page** : détectées seules (blancs verticaux à la hauteur du paragraphe, texte de la
  colonne voisine jusqu'à 150 pt plus haut ou plus bas) ; si un paragraphe déborde quand même (signalé « À
  VÉRIFIER »), lui donner `x1=` ou `COLUMNS`.
- **Étapes numérotées sur pastilles** : le moteur ancre seul un paragraphe dont le premier caractère est posé
  sur une petite forme pleine (`fix=True` implicite, `fix=False` pour l'empêcher) et réduit le texte qui
  précéderait trop bas. Le chiffre, s'il est du texte (blanc), reste à réécrire au début du français avec un
  retrait suspendu (`<div style="margin-left:8pt;text-indent:-8pt">`).
- **Bouts d'illustration pris pour des icônes** (journal : « {} pour N icône(s) » sur un paragraphe sans
  icône) : `noicons=True` sur le paragraphe.
- **Insécables** : « Bleu 19 », « joueur A », « page 3 », « étape 2 » sont protégés par le moteur (mot à
  majuscule + nombre, et joueur / page / étape / manche / carte… + nombre ou lettre). Autre cas : `&#160;`.
- **Glyphe spécial pour un chiffre** (« Ä » ou � qui s'affiche « 0 ») : écrire simplement « 0 ».
- **Coupures indésirables** : le build met une insécable avant `{}` et après un nombre suivi d'un mot ; pour
  « p. 8 » ou « 1 - 2 = -1 » écrire `&#160;` dans le spec.
- **Titres longs** (nom d'origine + français) : `T(...)` les garde sur une ligne ; s'ils touchent une image,
  raccourcir le français ou passer `size=`.
- **Modifier spec/build par script** : écrire le script Python dans le scratchpad avec l'outil Write ; les `\1`,
  `\'` et apostrophes dans un heredoc bash se corrompent facilement.
