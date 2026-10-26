"""Liste toutes les lignes de texte du PDF d'origine, avec police, taille, couleur, position (-> blocks.txt).
Usage : python -X utf8 dump.py livret_original.pdf [blocks.txt]
Les identifiants pXbY:L (page X, bloc Y, ligne L) sont ceux qu'utilise spec.py ("bY:L-M").
Les icônes posées dans le texte sont listées en tête de page ; « [N icône(s)] » en fin de ligne = nombre de {}
à prévoir dans la traduction de cette ligne (même règle de détection que build.py).
Format compact (moins de jetons à la lecture) : taille s…, couleur #…, police <…> écrites seulement quand elles
changent dans le bloc ; orientation d… seulement si le texte n'est pas horizontal."""
import pymupdf, sys
from commun import find_icons, icons_on_line

SRC = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else "blocks.txt"
doc = pymupdf.open(SRC)
out = []
for pno, page in enumerate(doc):
    out.append(f"################ PAGE {pno}  {page.rect}")
    icons = find_icons(page)
    for ic in icons:
        kind = f"image x{ic['xref']}" if ic["kind"] == "img" else f"vectorielle ({len(ic['drs'])} tracés)"
        out.append(f"  ICÔNE {kind} {[round(v, 1) for v in ic['rect']]}")
    d = page.get_text("dict", flags=pymupdf.TEXT_PRESERVE_WHITESPACE)
    for bi, b in enumerate(d["blocks"]):
        if b["type"]:
            continue
        out.append(f"=== p{pno}b{bi} {[round(v) for v in b['bbox']]}")
        font = size = color = None
        for li, l in enumerate(b["lines"]):
            s0 = l["spans"][0]
            txt = ""
            for s in l["spans"]:
                f = s["font"].split("+")[-1]
                txt += (f"<{f}>" if f != font else "") + s["text"]
                font = f
            n = len(icons_on_line(icons, l["bbox"], b["bbox"][0] - 1, b["bbox"][2] + 1))
            sz, col = f"{round(s0['size'] * 4) / 4:g}", f"{s0['color']:06x}"  # 11.04 et 11.06 : même taille
            d_ = "" if (round(l["dir"][0], 2), round(l["dir"][1], 2)) == (1, 0) else \
                f" d{l['dir'][0]:.2f},{l['dir'][1]:.2f}"
            out.append(f"  {li} x{l['bbox'][0]:.1f}-{l['bbox'][2]:.1f} y{s0['origin'][1]:.1f}"
                       + (f" s{sz}" if sz != size else "") + (f" #{col}" if col != color else "")
                       + f"{d_} {txt}" + (f"  [{n} icône(s)]" if n else ""))
            size, color = sz, col
open(OUT, "w", encoding="utf8").write("\n".join(out))
print(len(doc), "pages ->", OUT)
