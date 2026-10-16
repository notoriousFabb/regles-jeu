# Langue de départ

La déduire du texte (`preparer.py` la devine pour un livret à texte ; pour un scan, d'après l'OCR ou la
planche) et l'annoncer dès le début (« Livret en allemand, 12 pages… »). Ne demander que si c'est ambigu :
- livret **multilingue** (langues côte à côte ou par section) : demander laquelle traduire ; les autres
  restent telles quelles ou sont retirées, selon son choix ;
- livret déjà en partie en français : le signaler et demander quoi faire.

Conséquences :
- **Longueur** : depuis l'anglais, le français est ~15 % plus long ; depuis l'allemand, à peu près autant ;
  depuis l'espagnol ou l'italien, un peu plus long ; depuis le japonais / chinois / coréen, il demande beaucoup
  plus de place (souvent ×1,5 à ×2 en largeur) → traduire très concis, accepter une police réduite, prévenir.
- **Polices** : une police CJK ne donne pas de modèle pour les lettres latines → police latine libre de même
  esprit (`polices.md`). Une police embarquée latine a parfois quelques accents mais rarement tous ceux du
  français : `preparer.py` affiche les manques.
- **Texte vertical** (japonais, `d0.00,1.00` dans `blocks.txt`) : le build ne pose que du texte horizontal ;
  traduire en horizontal dans la même zone si la place le permet, sinon le signaler.
- **Glossaire** : `glossaire.md` a un tableau anglais et des équivalences par langue ; passer par le terme
  français retenu.
