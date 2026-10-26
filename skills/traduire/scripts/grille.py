"""Image d'une page avec une grille en points PDF, pour lire les coordonnées des zones de texte d'un scan.
Usage : python -X utf8 grille.py livret.pdf page [x0,y0,x1,y1] [dpi] [pas=10]
        -> grille<page>.png (page entière) ou grille<page>_<x0>_<y0>.png (zone : plusieurs zooms gardés)
Sans dpi : choisi pour que l'image ne dépasse pas 1 200 pixels (au plus 200 dpi) — au-delà, une image coûte
plus de jetons sans rien montrer de plus. Texte très fin dans une petite zone : dpi=300 à 350.
Traits fins tous les <pas> points, traits marqués et numérotés tous les 5 pas ; origine en haut à gauche."""
import pymupdf, sys

MAX_PX = 1200
doc = pymupdf.open(sys.argv[1])
pno = int(sys.argv[2])
args = sys.argv[3:]
clip = None
if args and "," in args[0]:
    clip = pymupdf.Rect([float(v) for v in args.pop(0).split(",")])
step = float(args[1]) if len(args) > 1 else 10.0

src = doc[pno]
area = (clip or src.rect) & src.rect  # sinon une zone hors page décale la grille
dpi = int(args[0]) if args else min(200, int(MAX_PX * 72 / max(area.width, area.height)))
out = pymupdf.open()
pg = out.new_page(width=area.width, height=area.height)
pg.show_pdf_page(pg.rect, doc, pno, clip=area)
fs = max(2.5, min(area.width, area.height) / 60)
x = (area.x0 // step + 1) * step
while x < area.x1:
    major = round(x / step) % 5 == 0
    pg.draw_line((x - area.x0, 0), (x - area.x0, area.height), color=(1, 0, 0) if major else (1, 0.6, 0.6),
                 width=0.25 if major else 0.1, stroke_opacity=0.8 if major else 0.5)
    if major:
        pg.insert_text((x - area.x0 + 0.5, fs + 0.5), f"{x:g}", fontsize=fs, color=(0.8, 0, 0))
    x += step
y = (area.y0 // step + 1) * step
while y < area.y1:
    major = round(y / step) % 5 == 0
    pg.draw_line((0, y - area.y0), (area.width, y - area.y0), color=(0, 0, 1) if major else (0.6, 0.6, 1),
                 width=0.25 if major else 0.1, stroke_opacity=0.8 if major else 0.5)
    if major:
        pg.insert_text((0.5, y - area.y0 - 0.5), f"{y:g}", fontsize=fs, color=(0, 0, 0.8))
    y += step
nom = f"grille{pno}.png" if clip is None else f"grille{pno}_{area.x0:.0f}_{area.y0:.0f}.png"
pix = pg.get_pixmap(dpi=dpi)
pix.save(nom)
print(f"{nom}  ({area}, {dpi} dpi, {pix.width}×{pix.height} px)")
