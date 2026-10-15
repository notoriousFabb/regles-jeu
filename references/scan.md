# Livret scanné (pages-images sans texte)

`preparer.py` le détecte (« SCANNÉ ») et copie `scan.py`, `ocr.py`, `grille.py`, `bandes.py` et le modèle
`spec_scan_modele.py`. Il n'y a pas de texte à remplacer : `build.py` ne s'applique pas.

## Choisir le rendu (demander à l'utilisateur)
- **« recouvrir »** (ressemble à l'original) : chaque zone de texte de l'image est masquée par la couleur du fond
  mesurée autour, et le français est posé dedans, police réduite automatiquement pour tenir. Limites à
  annoncer : sur fond texturé ou dégradé le masque se voit (aplat), le texte écrit dans les illustrations reste
  en langue d'origine sauf zone dédiée, et le français est souvent très petit sur un livret dense.
- **« cote »** (le plus fiable) : chaque page d'origine à gauche, sa traduction complète à droite ; une page de
  plus si la traduction est longue (`PAGES[page] = "<h3>…</h3><p>…</p>"`).

## Méthode « recouvrir »
1. **Lecture automatique** : `preparer.py` lance `ocr.py` (reconnaissance de texte de Windows), qui écrit
   `zones.py` : un `Z(page, (x0, y0, x1, y1), "texte d'origine")` par paragraphe, la taille du texte et, en
   commentaire, le haut et le bas de chaque ligne. Langue de lecture : choisie seule (japonais si Windows sait
   le lire et que le livret en contient, sinon anglais) ; autre langue : `--langue-ocr de-DE`, `fr-FR`… ;
   `python -X utf8 ocr.py --langues` liste celles installées. Japonais, chinois… : module OCR de Windows à
   installer par l'utilisateur (terminal administrateur :
   `dism /Online /Add-Capability /CapabilityName:Language.OCR~~~ja-JP~0.0.1.0`) ; sinon, méthode manuelle
   ci-dessous. L'OCR japonais confond souvent les petits caractères (ボ/ポ, ソ/リ, げ/け, kanji rares) :
   corriger d'après le sens et vérifier les mots douteux sur la planche.
2. **Écrire `spec.py`** à partir de `zones.py` : traduire chaque texte, **élargir `x1` jusqu'au bord de la
   colonne** (l'OCR donne la largeur du texte anglais, le français est plus long), couper une zone qui mélange
   titre et paragraphe (repères y en commentaire), régler `size` (≈ celle indiquée), `bold`, `align`, `color`.
   Garder l'original dans la zone pour la relecture : `Z(page, rect, "français", en="texte de zones.py")`.
   Vérifier sur la planche que l'OCR n'a rien oublié (petits textes, texte sur fond coloré, titres décoratifs)
   et ne pas traduire le texte des illustrations sauf demande.
3. **Méthode manuelle** (langue non lisible par l'OCR) : lire sur des agrandissements
   (`grille.py livret.pdf <page> x0,y0,x1,y1 300`) ; ne pas déduire les hauteurs à l'œil (erreurs de plusieurs
   points) : mesurer les lignes avec `bandes.py livret.pdf <page> x0,y0,x1,y1` (fond clair, sombre ou coloré) ;
   pour couper une ligne en deux zones (étiquette + nom), mesurer les blancs horizontaux. Si l'image est trop
   floue pour lire sans deviner, le dire plutôt que d'inventer.
4. **Construire** : `python -X utf8 scan.py sortie.pdf`. Réglages utiles :
   - livret dense : `pad=-0.5` (le texte peut dépasser un peu du masque) et `lead=1.0` ;
   - zone d'une seule ligne : interligne 1.0 et `pad` plus négatif, sinon la police est réduite pour rien ;
   - agrandir chaque masque d'environ 1,5 pt vers le bas (jambages du texte d'origine) ; commencer les listes
     numérotées assez à gauche pour couvrir les numéros d'origine ;
   - fond sombre ou coloré mal deviné (bulle, encadré) : `bg="#rrggbb"` mesuré sur l'original ; `M(...)` pour
     effacer sans remplacer.
   Journal : « police réduite à … (N pt) », « DÉBORDE » (raccourcir ou agrandir la zone) ; en dessous de
   ~4,5 pt imprimé, prévenir l'utilisateur. **« À VÉRIFIER »** : masques d'où une ligne d'origine dépasse
   (fausses alertes possibles sur les bulles et les dessins).
5. **Relire** : comme pour un livret à texte, avec les deux agents relecteurs (SKILL.md, étape 5) ; dire au
   relecteur visuel que c'est un scan (masques visibles, texte d'origine qui dépasse) et lui donner les endroits
   signalés. Le texte oublié ne se détecte pas seul : comparer avec `zones.py`.
Coût : plus élevé qu'un livret à texte ; le dire avant de commencer un long livret.
