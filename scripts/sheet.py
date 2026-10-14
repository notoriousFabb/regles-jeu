"""Planche contact de tout le livret (aperçu rapide avant de commencer).
Usage : python -X utf8 sheet.py livret.pdf planche [dpi=90]  -> planche0.png, planche1.png..."""
import pymupdf, sys

doc = pymupdf.open(sys.argv[1]); out = sys.argv[2]; dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 90
W, H = doc[0].rect.width, doc[0].rect.height
cols = 3 if W < H else 2
per = cols * 2
for k in range(0, len(doc), per):
    s = pymupdf.open(); pg = s.new_page(width=W * cols, height=H * 2)
    for j, i in enumerate(range(k, min(k + per, len(doc)))):
        pg.show_pdf_page(pymupdf.Rect((j % cols) * W, (j // cols) * H, (j % cols + 1) * W, (j // cols + 1) * H), doc, i)
    pg.get_pixmap(dpi=dpi).save(f"{out}{k // per}.png")
