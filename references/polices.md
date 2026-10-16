# Polices de remplacement

Les polices embarquées sont des sous-ensembles : presque jamais d'accents, parfois même pas toutes les
lettres (Christmas Chalk n'avait ni A, ni B, ni F…). Vérifier les glyphes réellement dessinés, pas seulement
ceux listés dans la table. `scripts/polices.py` fait tout cela :

```
python -X utf8 polices.py extraire livret.pdf fonts          # polices embarquées -> fonts/
python -X utf8 polices.py glyphes fonts/*.ttf ff/*.ttf       # lettres dessinées, caractères français manquants
python -X utf8 polices.py largeur fonts/Orig.ttf ff/A.ttf ff/B.ttf --texte "phrase du livret"   # SIZE_K
python -X utf8 polices.py planche planche.png fonts/Orig.ttf ff/A.ttf ff/B.ttf --texte "phrase du livret"
```

`extraire` garde, pour chaque police, le plus complet de ses sous-ensembles (un PDF en contient souvent
un par page) et écrit à côté `<police>.caracteres.txt` : les caractères que le livret imprime avec elle.
`glyphes` s'en sert pour une police CID sans table de caractères ; `largeur` et `planche` ne peuvent pas
mesurer une telle police (comparer à l'œil avec `grille.py`). Les polices Type3 (dessinées dans le PDF)
ne s'extraient pas : choisir la remplaçante à l'œil.
Pour `largeur` et `planche`, prendre une phrase réellement imprimée dans le livret : l'originale est un
sous-ensemble et n'a pas les autres lettres (l'outil le signale).
Chercher d'abord la police installée dans Windows (`C:/Windows/Fonts`, ex. Berlin Sans FB = BRLNSR.TTF) :
complète, avec accents.

Sinon, Google Fonts : `https://github.com/google/fonts/raw/main/ofl/<nom>/<Fichier>.ttf` (parfois `apache/`).
Télécharger 4 à 6 candidates dans un dossier à part, faire une planche comparative (`polices.py planche`) et
regarder l'image avant de choisir. `polices.py largeur` donne le facteur `SIZE_K` (dans spec.py) et la largeur
de l'espace : au-delà de ~0,3 em le texte paraît justifié
→ patcher `hmtx` avec fontTools (cas de Kalam : 0,40 → 0,24 em).

## Correspondances déjà trouvées
| Original | Remplacement | Remarque |
|---|---|---|
| Avenir LT Std Light / Heavy / Black Oblique | Figtree Light / ExtraBold / Black Italic | largeurs identiques à 2 % près |
| Berlin Sans FB | Berlin Sans FB de Windows (BRLNSR.TTF) | |
| Duper (humanist sans) | Alegreya Sans | |
| CC Sign Language (titres BD) | Caveat Brush | facteur ×1,17 |
| Christmas Chalk / Italic | Handlee (×1,15) / Kalam à espaces resserrés (×1,3) | |
| Cholla Sans / Slab | Barlow Semi Condensed, Zilla Slab | |
| JUST Sans, Just for Fun, Peaches for Breakfast | Figtree, Patrick Hand, Shadows Into Light Two | |
| Adobe Garamond Pro, Poster Cut Neue | EB Garamond, Archivo Black | |
| alarm clock (LCD) | Alarm Clock complète, glyphe 6 corrigé | |
| HarenosoraMincho (japonais, sans latin) | Zen Old Mincho | |
| Rodin NTLG / Rodin Happy (japonais arrondi) | M PLUS Rounded 1c (Medium / Bold / ExtraBold / Black) | Google Fonts |
| VDL MegaMaru (japonais manuscrit arrondi) | Itim | |
| Source Han Sans JP Bold, Arimo | Arial Bold, Arial | Windows |
| Lato, MedievalSharp (embarquées complètes) | les mêmes, copiées depuis le PDF | |
| texte d'un scan, sans serif type Work Sans | Work Sans (graisses fixes extraites de la police variable) | fontTools instancer |
| texte japonais dense d'un scan | Arial Narrow + Segoe UI Symbol pour ①…⑦, ※ | Windows |

Ces polices sont déjà dans le dossier `ff/` des jeux traduits (voir la colonne Polices de l'index `LISEZMOI.md`) : les
copier plutôt que retélécharger.
Polices sans U+2011 (trait d'union insécable) : `white-space:nowrap` (le build le fait pour « 3-Physique »).
