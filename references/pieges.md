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
  par-dessus. Les couleurs qui distinguent numéro / ambiance / effet sont codées dans `card_flows` : à adapter.
- **Glyphe spécial pour un chiffre** (« Ä » ou � qui s'affiche « 0 ») : écrire simplement « 0 ».
- **Coupures indésirables** : le build met une insécable avant `{}` et après un nombre suivi d'un mot ; pour
  « p. 8 » ou « 1 - 2 = -1 » écrire `&#160;` dans le spec.
- **Titres longs** (nom anglais + français) : `T(...)` les garde sur une ligne ; s'ils touchent une image,
  raccourcir le français ou passer `size=`.
- **Modifier spec/build par script** : écrire le script Python dans le scratchpad avec l'outil Write ; les `\1`,
  `\'` et apostrophes dans un heredoc bash se corrompent facilement.
