# -*- coding: utf-8 -*-
"""Traduction d'un livret SCANNÉ (pages-images, sans texte sélectionnable) d'après spec.py (voir spec_scan_modele.py).

MODE "recouvrir" : chaque zone de texte de l'image est masquée (couleur du fond prise autour) et le français posé
                   dedans, police réduite automatiquement pour tenir.
MODE "cote"      : chaque page d'origine à gauche, sa traduction à droite (suite sur une page de plus si besoin).
Usage : python -X utf8 scan.py sortie.pdf      (journal affiché et enregistré dans <sortie>_journal.txt)"""
import io, os, re, statistics, sys
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
import spec


def fail(msg):
    sys.exit(f"ERREUR : {msg}")


for name in ("SRC", "CSS", "BODY", "MODE"):
    if not hasattr(spec, name):
        fail(f"réglage {name} absent de spec.py (voir spec_scan_modele.py)")
if spec.MODE not in ("recouvrir", "cote"):
    fail(f"MODE doit valoir \"recouvrir\" ou \"cote\", pas « {spec.MODE} »")
if not os.path.isfile(spec.SRC):
    fail(f"PDF source introuvable : {spec.SRC} (réglage SRC de spec.py)")
FF = os.path.join(HERE, "ff")
missing = [f for f in re.findall(r"url\(\s*['\"]?([^)'\"]+)", spec.CSS) if not os.path.isfile(os.path.join(FF, f))]
if missing:
    fail(f"polices absentes du dossier {FF} : {', '.join(missing)}")
ARCH = pymupdf.Archive(FF)
CSS = spec.CSS + "\n* {margin:0; padding:0;}\n"
OUT = sys.argv[1] if len(sys.argv) > 1 else "out_fr.pdf"
src = pymupdf.open(spec.SRC)
log = []


def typo(html):
    html = re.sub(r" ([:;!?»])", " \\1", html)
    html = html.replace("« ", "« ")
    html = re.sub(r"(?<=[A-Za-zÀ-ÿ])'", "’", html)
    html = re.sub(r"(?<=\b\d) (?=[a-zà-ÿ])", " ", html)
    return html


def check_page(pno, what):
    if not 0 <= pno < len(src):
        fail(f"{what} : page {pno} hors du livret ({len(src)} pages, numérotées 0 à {len(src) - 1})")


# ------------------------------------------------------------------ mode "recouvrir"
def ring_color(page, r, pix_cache={}):
    """Median colour of a thin ring just outside the zone = the background to paint over the original text."""
    if page.number not in pix_cache:
        pix_cache[page.number] = page.get_pixmap(dpi=144)
    pix = pix_cache[page.number]
    k = 144 / 72
    outer = (r + (-2, -2, 2, 2)) & page.rect
    px = []
    x0, y0, x1, y1 = (int(v * k) for v in outer)
    ix0, iy0, ix1, iy1 = (int(v * k) for v in r)
    for y in range(max(y0, 0), min(y1, pix.height)):
        for x in range(max(x0, 0), min(x1, pix.width)):
            if ix0 <= x < ix1 and iy0 <= y < iy1:
                continue
            px.append(pix.pixel(x, y)[:3])
    if not px:
        return (1, 1, 1)
    return tuple(statistics.median(p[i] for p in px) / 255 for i in range(3))


def hexcol(c):
    if isinstance(c, str):
        v = int(c.lstrip("#"), 16)
        return ((v >> 16) / 255, (v >> 8 & 255) / 255, (v & 255) / 255)
    return c


def recouvrir():
    doc = pymupdf.open(spec.SRC)
    zones = getattr(spec, "ZONES", [])
    if not zones:
        fail("ZONES est vide : rien à traduire (voir spec_scan_modele.py)")
    covers, texts = [], []
    for i, z in enumerate(zones):
        tag = f"page {z['page']} zone {i + 1} {tuple(round(v) for v in z['rect'])}"
        check_page(z["page"], tag)
        r = pymupdf.Rect(z["rect"])
        if r.is_empty or not r.intersects(src[z["page"]].rect):
            fail(f"{tag} : rectangle vide ou hors de la page {tuple(src[z['page']].rect)}")
        bg = z.get("bg", "auto")
        if bg:  # colours are measured on the untouched page, before any cover is painted
            covers.append((z["page"], r, ring_color(src[z["page"]], r) if bg == "auto" else hexcol(bg), bg != "auto"))
        if z.get("html") is not None:
            texts.append((tag, z, r))
    if getattr(spec, "VECTEUR", False):
        # texte dessiné en tracés vectoriels : on supprime les tracés entièrement dans la zone (agrandie de
        # VECTEUR_MARGE) au lieu de poser un aplat ; le fond d'origine reste intact sous le français
        # (zone étendue aux petits tracés — lettres — qu'elle touche ; une suppression à la fois : MuPDF
        # n'efface qu'en partie les tracés couverts par deux zones qui se chevauchent)
        marge = getattr(spec, "VECTEUR_MARGE", 1.2)
        lettre = getattr(spec, "VECTEUR_LETTRE", 12)  # taille maximale d'un tracé de lettre, en points
        for pno, r, col, explicite in covers:
            page = doc[pno]
            zone = pymupdf.Rect(r)
            for dr in page.get_drawings():
                b = dr["rect"]
                # lettre à moitié dans la zone au moins (une pièce d'illustration qui l'effleure n'est pas prise)
                if b.width <= lettre and b.height <= lettre and (b & r).get_area() >= 0.5 * max(b.get_area(), 1e-6):
                    zone |= b
            page.add_redact_annot(zone + (-marge, -marge, marge, marge), fill=False)
            page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE, text=pymupdf.PDF_REDACT_TEXT_NONE,
                                  graphics=pymupdf.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED)
        # couleur de fond donnée dans le spec : aplat posé en plus (un petit cadre plein entièrement dans la
        # zone, comme l'étiquette « Contact », est supprimé avec les lettres)
        covers = [c for c in covers if c[3]]
    for pno, r, col, _ in covers:
        doc[pno].draw_rect(r, color=None, fill=col, overlay=True)
    for tag, z, r in texts:
        page = doc[z["page"]]
        # zone d'une seule ligne : interligne 1.0 et marge négative, sinon la police est réduite pour rien
        one = r.height < 1.8 * z.get("size", 7) and not re.search(r"<br|<p\b|<li\b|<div\b", z["html"])
        pad = z.get("pad", -0.6 if one else 0.5)
        st = (f"font-family:{z.get('fam', spec.BODY)};font-size:{z.get('size', 7)}pt;"
              f"line-height:{z.get('lead', 1.0 if one else 1.15)};color:{z.get('color', '#000000')};"
              f"text-align:{z.get('align', 'left')};font-weight:{'bold' if z.get('bold') else 'normal'};"
              f"font-style:{'italic' if z.get('ital') else 'normal'};")
        html = f'<div style="{st}">{typo(z["html"])}</div>'
        kmin = z.get("kmin", 0.5)
        spare, scale = page.insert_htmlbox(r + (pad, pad, -pad, -pad), html, css=CSS, archive=ARCH,
                                           scale_low=kmin, rotate=z.get("rot", 0))
        if spare < 0:
            log.append(f"{tag} : DÉBORDE même à {kmin:.2f} × la taille — raccourcir ou agrandir la zone")
        elif scale < 0.999:
            log.append(f"{tag} : police réduite à {scale:.2f} ({z.get('size', 7) * scale:.1f} pt)")
    return doc


# ------------------------------------------------------------------ mode "cote"
def text_pages(html, w, h, m):
    buf = io.BytesIO()
    wr = pymupdf.DocumentWriter(buf)
    story = pymupdf.Story(html=html, user_css=CSS, archive=ARCH)
    story.write(wr, lambda n, filled: (pymupdf.Rect(0, 0, w, h), pymupdf.Rect(m, m, w - m, h - m), None))
    wr.close()
    return pymupdf.open("pdf", buf.getvalue())


def cote():
    pages = getattr(spec, "PAGES", {})
    if not pages:
        fail("PAGES est vide : rien à traduire (voir spec_scan_modele.py)")
    ratio = getattr(spec, "SIDE_WIDTH", 1.0)
    gap = getattr(spec, "SIDE_GAP", 8)
    m = getattr(spec, "SIDE_MARGIN", 10)
    st = getattr(spec, "SIDE_STYLE", f"font-family:{spec.BODY};font-size:8pt;line-height:1.2;")
    for pno in pages:
        check_page(pno, "PAGES")
    out = pymupdf.open()
    for pno in range(len(src)):
        W, H = src[pno].rect.width, src[pno].rect.height
        tw = W * ratio
        if pno not in pages:
            log.append(f"page {pno} : pas de traduction (PAGES), page d'origine seule")
            pg = out.new_page(width=W + gap + tw, height=H)
            pg.show_pdf_page(pymupdf.Rect(0, 0, W, H), src, pno)
            continue
        tp = text_pages(f'<div style="{st}">{typo(pages[pno])}</div>', tw, H, m)
        if len(tp) > 1:
            log.append(f"page {pno} : traduction sur {len(tp)} pages (page d'origine répétée)")
        for i in range(len(tp)):
            pg = out.new_page(width=W + gap + tw, height=H)
            pg.show_pdf_page(pymupdf.Rect(0, 0, W, H), src, pno)
            pg.show_pdf_page(pymupdf.Rect(W + gap, 0, W + gap + tw, H), tp, i)
            pg.draw_line((W + gap / 2, m), (W + gap / 2, H - m), color=(0.7, 0.7, 0.7), width=0.4)
    return out


doc = recouvrir() if spec.MODE == "recouvrir" else cote()
doc.subset_fonts()
doc.save(OUT, garbage=3, deflate=True)
if spec.MODE == "recouvrir":
    try:
        import controle
        controle.check_scan(src, getattr(spec, "ZONES", []), log)
    except ImportError:
        log.append("(controle.py absent : pas de contrôle des masques)")
log.append("")
log.append("Rappel : sur un scan, le texte oublié ne se détecte pas tout seul — comparer avec zones.py (ocr.py) et "
           "relire les pages (side.py), en priorité aux endroits signalés.")
journal = os.path.splitext(OUT)[0] + "_journal.txt"
open(journal, "w", encoding="utf8").write("\n".join(log) + "\n")
print("\n".join(log))
print("enregistré :", OUT, "— journal :", journal)
