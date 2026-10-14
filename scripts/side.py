"""Images de relecture : original à gauche, traduction à droite (sideN.png).
Usage : python -X utf8 side.py livret_EN.pdf sortie_FR.pdf 0,1,2 [dpi=110]"""
import pymupdf, sys

a, b = pymupdf.open(sys.argv[1]), pymupdf.open(sys.argv[2])
pages = range(len(a)) if sys.argv[3] == "all" else [int(x) for x in sys.argv[3].split(",")]
dpi = int(sys.argv[4]) if len(sys.argv) > 4 else 110
for p in pages:
    W, H = a[p].rect.width, a[p].rect.height
    out = pymupdf.open()
    pg = out.new_page(width=2 * W + 6, height=H)
    pg.show_pdf_page(pymupdf.Rect(0, 0, W, H), a, p)
    pg.show_pdf_page(pymupdf.Rect(W + 6, 0, 2 * W + 6, H), b, p)
    pg.get_pixmap(dpi=dpi).save(f"side{p}.png")
