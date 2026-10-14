# Polices de remplacement

Les polices embarquées sont des sous-ensembles : presque jamais d'accents, parfois même pas toutes les
lettres (Christmas Chalk n'avait ni A, ni B, ni F…). Vérifier les glyphes réellement dessinés, pas seulement
ceux listés dans la table :

```python
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
f = TTFont(fn); gs = f.getGlyphSet(); drawn = []
for cp, g in f.getBestCmap().items():
    bp = BoundsPen(gs); gs[g].draw(bp)
    if bp.bounds: drawn.append(chr(cp))
print("".join(drawn))
```

Extraire les polices : `doc.extract_font(xref)` → dossier `fonts/` (sert aussi au calcul des largeurs).
Chercher d'abord la police installée dans Windows (`C:/Windows/Fonts`, ex. Berlin Sans FB = BRLNSR.TTF) :
complète, avec accents.

Sinon, Google Fonts : `https://github.com/google/fonts/raw/main/ofl/<nom>/<Fichier>.ttf` (parfois `apache/`).
Télécharger 4 à 6 candidates dans un dossier à part, faire une planche comparative (extrait d'origine rendu à
côté de chaque candidate) et regarder l'image avant de choisir. Calculer le rapport de largeur avec la police
d'origine (`Font.text_length` sur une phrase du livret) → facteur `SIZE_K` dans build.py.
Vérifier aussi la largeur de l'espace (`glyph_advance(32)`) : au-delà de ~0,3 em le texte paraît justifié
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

Ces polices sont déjà dans `_outils/<jeu>/ff/` du dossier de travail : les copier plutôt que retélécharger.
Polices sans U+2011 (trait d'union insécable) : `white-space:nowrap` (le build le fait pour « 3-Physique »).
