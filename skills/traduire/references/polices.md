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
| TsukuARdGothic Regular / Bold, KozGoPr6N (japonais arrondi) | Zen Maru Gothic Regular / Bold | facteur 1,0 |
| Grow-Year (titres manuscrits, numéros) | Chewy | facteur 1,1 |
| Source Han Sans JP Bold, Arimo | Arial Bold, Arial | Windows |
| Lato, MedievalSharp (embarquées complètes) | les mêmes, copiées depuis le PDF | |
| texte d'un scan, sans serif type Work Sans | Work Sans (graisses fixes extraites de la police variable) | fontTools instancer |
| texte japonais dense d'un scan | Arial Narrow + Segoe UI Symbol pour ①…⑦, ※ | Windows |
| symboles ①…⑳, ❶…❿, ◆, ★, ■ absents (ou minuscules) dans la police du texte | Segoe UI Symbol (`seguisym.ttf`), en `<span>` | Windows |
| linéale humaniste d'un scan anglais | Alegreya Sans | Google Fonts |
| titres rétro sur bandeau | Righteous | Google Fonts |
| Gotham Book / Medium (tracés vectoriels) | Montserrat 400 / 500 (instancer) | ×0,98 en largeur |
| géométrique à « a » simple (titres et texte d'un scan) | Outfit 400 / 600 (instancer) | Google Fonts |
| Myriad (scan) | Source Sans 3 400 / 600 (instancer) | Google Fonts |
| serif évasé type Trajan minuscule | Marcellus (pas de gras : Spectral SemiBold pour `<b>`) | Google Fonts |
| Arial Narrow / Palatino d'un scan | ARIALN*.TTF, pala*.ttf de Windows | corriger U+00A0 d'ARIALNB (pieges.md) |
| Yu Gothic Regular / Bold (aussi Aptos, MS Gothic des mêmes livrets) | Yu Gothic de Windows, extraite de `YuGothR.ttc` / `YuGothB.ttc` (fontTools `TTCollection`, la police « Yu Gothic », pas « UI ») | facteur 1,0, accents complets |
| Shin Retro Maru Gothic (japonais arrondi) | M PLUS Rounded 1c Medium / Bold | Google Fonts |
| Noto Sans KR (variable, un seul nom « Thin » pour toutes les graisses) | Noto Sans KR complète instanciée (fontTools `instancer`) en 300 / 700 ; faux italique des légendes : glyphes penchés de 11° (`TransformPen`) | voir pièges : gras invisible |
| Mochiy Pop One (titres) | la même, complète | Google Fonts |
| mincho d'un scan japonais (corps et titres) | Zen Old Mincho Regular / Bold | contient 【】※→ |
| texte recomposé à neuf (scan froissé) | Segoe UI + Segoe UI Symbol (⌖ ①–④) + Bahnschrift (logo) | Windows |
Polices téléchargées entières (plusieurs Mo, japonaises ou coréennes) : les réduire au latin + symboles utiles
(fontTools `subset`) avant de les mettre dans `ff/`.

Ces polices sont déjà dans le dossier `ff/` des jeux traduits (voir la colonne Polices de l'index `LISEZMOI.md`) : les
copier plutôt que retélécharger.
Polices sans U+2011 (trait d'union insécable) : `white-space:nowrap` (le build le fait pour « 3-Physique »).
