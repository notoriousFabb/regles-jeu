"""Fonctions partagées par build.py et dump.py (à copier avec eux dans _outils/<Jeu>/)."""
import pymupdf


def find_icons(page):
    """Petites icônes posées dans le texte : images (< 22×16) et grappes de tracés vectoriels pleins (< 14×14)."""
    icons = []
    for im in page.get_image_info(xrefs=True):
        r = pymupdf.Rect(im["bbox"])
        if r.width < 22 and r.height < 16 and im["xref"]:
            icons.append(dict(kind="img", rect=r, xref=im["xref"]))
    # small vector pictograms (suit symbols): clusters of overlapping filled paths
    small = [dr for dr in page.get_drawings() if dr.get("fill") and dr["rect"].width < 13 and dr["rect"].height < 13]
    clusters = []
    for dr in small:
        r = pymupdf.Rect(dr["rect"])
        hit = [c for c in clusters if c["rect"].intersects(r)]
        for c in hit:
            clusters.remove(c)
            r |= c["rect"]
        clusters.append(dict(rect=r, drs=[dr] + [d for c in hit for d in c["drs"]]))
    for c in clusters:
        if 1.5 < c["rect"].width < 14 and 1.5 < c["rect"].height < 14 and len(c["drs"]) >= 2:
            icons.append(dict(kind="vec", rect=c["rect"], drs=c["drs"]))
    return icons


def icons_on_line(icons, line_bbox, x0, x1):
    """Icônes dont le centre est sur la bande d'une ligne, entre x0 et x1 (même règle que build.py)."""
    r = pymupdf.Rect(line_bbox)
    out = []
    for ic in icons:
        c = (ic["rect"].tl + ic["rect"].br) / 2
        if r.y0 - 1 <= c.y <= r.y1 + 1 and x0 <= c.x <= x1:
            out.append(ic)
    return out
