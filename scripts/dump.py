"""Liste toutes les lignes de texte du PDF anglais, avec police, taille, couleur, position (-> blocks.txt).
Usage : python -X utf8 dump.py livret_EN.pdf [blocks.txt]
Les identifiants pXbY:L (page X, bloc Y, ligne L) sont ceux qu'utilise spec.py ("bY:L-M")."""
import pymupdf, sys

SRC = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else "blocks.txt"
doc = pymupdf.open(SRC)
out = []
for pno, page in enumerate(doc):
    out.append(f"################ PAGE {pno}  {page.rect}")
    for im in page.get_image_info(xrefs=True):
        r = pymupdf.Rect(im["bbox"])
        if r.width < 22 and r.height < 16:
            out.append(f"  IMG (icône possible) x{im['xref']} {[round(v, 1) for v in r]}")
    d = page.get_text("dict", flags=pymupdf.TEXT_PRESERVE_WHITESPACE)
    for bi, b in enumerate(d["blocks"]):
        if b["type"]:
            continue
        out.append(f"=== p{pno}b{bi} {[round(v) for v in b['bbox']]}")
        for li, l in enumerate(b["lines"]):
            s0 = l["spans"][0]
            txt = "".join(f"<{s['font'].split('+')[-1]}>{s['text']}" for s in l["spans"])
            out.append(f"  {li:2d} x{l['bbox'][0]:6.1f}-{l['bbox'][2]:6.1f} y{s0['origin'][1]:6.1f} "
                       f"s{s0['size']:<5.4g} #{s0['color']:06x} d{l['dir'][0]:.2f},{l['dir'][1]:.2f} {txt}")
open(OUT, "w", encoding="utf8").write("\n".join(out))
print(len(doc), "pages ->", OUT)
