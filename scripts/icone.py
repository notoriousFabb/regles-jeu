"""Découpe une icône d'un livret scanné pour la remettre dans le texte français (I("nom") dans spec.py).
Usage : python -X utf8 icone.py livret.pdf page x0,y0,x1,y1 nom   -> ff/<nom>.png (600 dpi)
Coordonnées en points PDF, lues sur grille.py ; serrer la zone autour de l'icône (le fond découpé reste visible)."""
import os, sys
import pymupdf

if len(sys.argv) != 5:
    sys.exit(__doc__)
doc = pymupdf.open(sys.argv[1])
page = doc[int(sys.argv[2])]
clip = pymupdf.Rect([float(v) for v in sys.argv[3].split(",")]) & page.rect
if clip.is_empty:
    sys.exit(f"ERREUR : zone vide ou hors de la page {tuple(page.rect)}")
os.makedirs("ff", exist_ok=True)
out = os.path.join("ff", sys.argv[4] + ".png")
page.get_pixmap(dpi=600, clip=clip).save(out)
print(f"{out}  ({clip.width:.1f} × {clip.height:.1f} pt)")
