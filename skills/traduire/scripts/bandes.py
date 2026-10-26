"""Livret scanné : repère les lignes de texte (bandes d'encre) dans une zone de page, en points PDF.
Usage : python -X utf8 bandes.py livret.pdf page x0,y0,x1,y1
        python -X utf8 bandes.py livret.pdf --spec spec.py     (contrôle de toutes les zones Z() du spec)
Une ligne de texte = suite de rangées de pixels très contrastées (fonctionne sur fond clair, sombre ou coloré).
Avec --spec : pour chaque zone, les bandes trouvées autour (± 4 pt) et un rectangle conseillé qui les englobe ;
« ATTENTION » quand de l'encre dépasse du rectangle (texte d'origine qui resterait visible)."""
import importlib.util, os, sys
import pymupdf

K = 8  # pixels per point


def bands(page, rect, min_h=1.2):
    r = pymupdf.Rect(rect) & page.rect
    pix = page.get_pixmap(matrix=pymupdf.Matrix(K, K), clip=r, colorspace=pymupdf.csGRAY)
    w, h, s = pix.width, pix.height, pix.samples
    rows = []
    for y in range(h):
        line = s[y * w:(y + 1) * w]
        srt = sorted(line)
        mid = srt[len(srt) // 2]
        # pixels far from the row's median value = ink (dark text on light, or light text on dark)
        ink = sum(1 for v in line if abs(v - mid) > 90)
        rows.append(ink / w > 0.01)
    out, start = [], None
    for y, on in enumerate(rows + [False]):
        if on and start is None:
            start = y
        elif not on and start is not None:
            if (y - start) / K >= min_h:
                y0, y1 = r.y0 + start / K, r.y0 + y / K
                out.append((round(y0, 1), round(y1, 1)))
            start = None
    return out


def show(page, rect):
    for y0, y1 in bands(page, rect):
        print(f"  y {y0:6.1f} – {y1:6.1f}  (hauteur {y1 - y0:.1f})")


def check_spec(doc, path):
    spec = importlib.util.spec_from_file_location("spec_scan", path)
    mod = importlib.util.module_from_spec(spec)
    cwd = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(path)))
    spec.loader.exec_module(mod)
    os.chdir(cwd)
    for i, z in enumerate(mod.ZONES, 1):
        page = doc[z["page"]]
        x0, y0, x1, y1 = z["rect"]
        found = bands(page, (x0, y0 - 4, x1, y1 + 4))
        inside = [b for b in found if b[1] > y0 and b[0] < y1]
        tag = f"page {z['page']} zone {i} ({x0:g}, {y0:g}, {x1:g}, {y1:g})"
        if not inside:
            print(f"{tag} : aucune ligne d'encre dans la zone — mal placée ?")
            continue
        top, bot = min(b[0] for b in inside), max(b[1] for b in inside)
        over = top < y0 - 0.2 or bot > y1 + 0.2
        print(f"{tag} : {len(inside)} ligne(s) {top:.1f}–{bot:.1f}"
              + (f"  ATTENTION : dépasse, conseillé ({x0:g}, {top - 0.3:.1f}, {x1:g}, {bot + 0.3:.1f})" if over else ""))


if __name__ == "__main__":
    doc = pymupdf.open(sys.argv[1])
    if sys.argv[2] == "--spec":
        check_spec(doc, sys.argv[3])
    else:
        show(doc[int(sys.argv[2])], [float(v) for v in sys.argv[3].split(",")])
