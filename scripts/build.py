# -*- coding: utf-8 -*-
"""Reconstruit un livret de règles en français en gardant chaque image et chaque tracé à sa place.

Moteur générique : tout ce qui est propre à un jeu (PDF source, polices, colonnes, mini-cartes) est dans spec.py
(voir spec_modele.py). Usage : python -X utf8 build.py sortie.pdf
Le journal (police réduite, débordements, icônes, texte non traduit) est affiché et enregistré dans
<sortie>_journal.txt."""
import os, re, sys
import pymupdf
from commun import find_icons

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
import spec


def fail(msg):
    sys.exit(f"ERREUR : {msg}")


def need(name):
    if not hasattr(spec, name):
        fail(f"réglage {name} absent de spec.py (voir spec_modele.py)")
    return getattr(spec, name)


FLOWS = spec.FLOWS
CARDS = getattr(spec, "CARDS", {})
CARD_PAGES = getattr(spec, "CARD_PAGES", {})
CARD_STYLE = getattr(spec, "CARD_STYLE", None)
SRC = need("SRC")
CODE = need("CODE")
SIZE_K = getattr(spec, "SIZE_K", {})
COLUMNS = getattr(spec, "COLUMNS", {})
IGNORE = getattr(spec, "IGNORE", {})
AVANT_TEXTE = getattr(spec, "AVANT_TEXTE", None)  # f(page, pno, log) : dessin sous le français (bandeau élargi…)
OUT = sys.argv[1] if len(sys.argv) > 1 else "out_fr.pdf"
FF = os.path.join(HERE, "ff")
MARK = "¤"
BULLET = re.compile(r"^\s*(•|\d+\.)\s*")

# ------------------------------------------------------------------ fonts (from the @font-face rules of spec.CSS)
FACES = {}
for m in re.finditer(r"@font-face\s*\{([^}]*)\}", need("CSS")):
    body = m.group(1)
    fam = re.search(r"font-family\s*:\s*([^;]+)", body)
    url = re.search(r"url\(\s*['\"]?([^)'\"]+)", body)
    if not fam or not url:
        fail(f"règle @font-face incomplète dans spec.CSS : {body.strip()}")
    key = (fam.group(1).strip().strip("'\""), bool(re.search(r"font-weight\s*:\s*bold", body)),
           bool(re.search(r"font-style\s*:\s*italic", body)))
    FACES[key] = url.group(1)
if not FACES:
    fail("spec.CSS ne déclare aucune police (@font-face)")
BODY = getattr(spec, "BODY", next(iter(FACES))[0])
FAMILIES = {k[0] for k in FACES}
missing = sorted({f for f in FACES.values() if not os.path.isfile(os.path.join(FF, f))})
if missing:
    fail(f"polices absentes du dossier {FF} : {', '.join(missing)}")
bad = sorted({v[0] for v in CODE.values()} - FAMILIES) + ([BODY] if BODY not in FAMILIES else [])
if bad:
    fail(f"familles utilisées dans CODE / BODY mais pas déclarées dans CSS : {', '.join(bad)}")
if not os.path.isfile(SRC):
    fail(f"PDF source introuvable : {SRC} (réglage SRC de spec.py)")


def face_file(fam, bold=False, ital=False):
    for k in ((fam, bold, ital), (fam, bold, False), (fam, False, ital), (fam, False, False), (BODY, False, False)):
        if k in FACES:
            return FACES[k]
    return next(iter(FACES.values()))


CSS = spec.CSS + f"""
* {{margin:0; padding:0;}}
b {{font-weight:bold;}}
.mk {{font-family:{BODY}; font-weight:normal; font-style:normal;}}
"""
ARCH = pymupdf.Archive(FF)
FBODY = pymupdf.Font(fontfile=os.path.join(FF, face_file(BODY)))

src = pymupdf.open(SRC)
doc = pymupdf.open(SRC)
log = []
used = set()  # (page, block, line) replaced by a translation


def fcode(s):
    return CODE.get(s["font"].split("+")[-1], (BODY, 0, 0))


# ------------------------------------------------------------------ source lines & icons
def page_lines(pno):
    d = src[pno].get_text("rawdict", flags=pymupdf.TEXT_PRESERVE_WHITESPACE)
    out = {}
    for bi, b in enumerate(d["blocks"]):
        if b["type"] == 0:
            for l in b["lines"]:
                for s in l["spans"]:
                    s["text"] = "".join(c["c"] for c in s["chars"])
            out[bi] = b["lines"]
    return out


def ltext(l):
    return "".join(s["text"] for s in l["spans"])


def sel_ids(lines_of, sel, pno, strict=True):
    """'b12:2-4 b13' -> [(block, line), ...]; stops with a clear message on a wrong selection."""
    out = []
    for s in sel.split():
        m = re.fullmatch(r"b(\d+)(?::(\d+)(?:-(\d+))?)?", s)
        if not m:
            fail(f"page {pno} : sélection « {s} » mal écrite (attendu b12, b12:3 ou b12:2-4)")
        bi = int(m.group(1))
        if bi not in lines_of:
            if not strict:
                continue
            fail(f"page {pno} : bloc b{bi} introuvable (blocs de texte de la page : "
                 f"{', '.join(f'b{k}' for k in sorted(lines_of))} — voir blocks.txt)")
        n = len(lines_of[bi])
        a = int(m.group(2)) if m.group(2) else 0
        z = int(m.group(3)) if m.group(3) else (a if m.group(2) else n - 1)
        if a > z or z >= n:
            if not strict:
                continue
            fail(f"page {pno} : « {s} » — le bloc b{bi} a {n} ligne(s), numérotées 0 à {n - 1}")
        out += [(bi, li) for li in range(a, z + 1)]
    return out


def sel_lines(lines_of, sel, pno):
    ids = sel_ids(lines_of, sel, pno)
    used.update((pno, bi, li) for bi, li in ids)
    return [lines_of[bi][li] for bi, li in ids]


def dedupe(lines):
    seen, out = [], []
    for l in lines:
        key = (ltext(l).strip(), round(l["spans"][0]["origin"][1]))
        if key[0] and key not in seen:
            seen.append(key)
            out.append(l)
    return out


def content_x0(l):
    """x of the first character after an optional bullet / number and blanks."""
    chars = [c for s in l["spans"] for c in s["chars"]]
    t = "".join(c["c"] for c in chars)
    m = BULLET.match(t)
    i = m.end() if m else len(t) - len(t.lstrip())
    i = min(i, len(chars) - 1)
    return chars[i]["bbox"][0]


def text_spans(l):
    out = []
    for s in l["spans"]:
        t = BULLET.sub("", s["text"]).strip()
        if t:
            out.append(s)
    return out


def column(pno, lines_of):
    """Text column of a page: spec.COLUMNS[page] or ["*"], else the extent of the long horizontal lines."""
    if pno in COLUMNS:
        return COLUMNS[pno]
    if "*" in COLUMNS:
        return COLUMNS["*"]
    hz = [l for ls in lines_of.values() for l in ls if abs(l["dir"][0] - 1) < 0.01 and ltext(l).strip()]
    long_ = [l for l in hz if l["bbox"][2] - l["bbox"][0] > 0.4 * src[pno].rect.width] or hz
    if not long_:
        r = src[pno].rect
        return r.x0 + 20, r.x1 - 20
    return min(l["bbox"][0] for l in long_), max(l["bbox"][2] for l in long_)


def segments(lines_of):
    """Text pieces (x0, x1, y0, y1) of a page; a PDF line holding two columns' titles is split at its wide blanks."""
    out = []
    for ls in lines_of.values():
        for l in ls:
            if abs(l["dir"][0] - 1) > 0.01:
                continue
            segs = []
            for s_ in l["spans"]:
                for c in s_["chars"]:
                    if not c["c"].strip():
                        continue
                    x0, x1 = c["bbox"][0], c["bbox"][2]
                    if segs and x0 - segs[-1][1] < 8:
                        segs[-1][1] = max(segs[-1][1], x1)
                    else:
                        segs.append([x0, x1])
            out += [(a, b, l["bbox"][1], l["bbox"][3]) for a, b in segs if b - a > 25]
    return sorted(out)


def gutters(segs, XL, XR, y0, y1):
    """Vertical white strips (>= 8 pt) between XL and XR that no text crosses near [y0, y1]: column separators."""
    out, x = [], XL
    for a, b, sy0, sy1 in segs:
        if sy1 < y0 - 15 or sy0 > y1 + 15:
            continue
        if a - x >= 8 and a < XR:
            out.append((x, min(a, XR)))
        x = max(x, b)
    return [g for g in out if g[0] > XL + 1 and g[1] < XR - 1]


def badges(pno):
    """Small filled shapes (5-15 pt) that the number of a step may sit on."""
    return [pymupdf.Rect(d["rect"]) for d in src[pno].get_drawings()
            if d.get("fill") and 5 <= d["rect"].width <= 15 and 5 <= d["rect"].height <= 15]


# ------------------------------------------------------------------ html helpers
NBSP_WORDS = (r"(?:[Jj]oueurs?|[Pp]ages?|[Éé]tapes?|[Mm]anches?|[Pp]lis|[Cc]artes?|[Tt]ours?|[Ff]igures?|"
              r"[Ee]xemples?|[Pp]oints?)")


def typo(html):
    html = re.sub(r" ([:;!?»])", " \\1", html)
    html = html.replace("« ", "« ")
    html = re.sub(r"(?<=[A-Za-zÀ-ÿ])'", "’", html)
    html = html.replace(" {}", " {}")
    html = re.sub(r"(?<=\b\d) (?=[a-zà-ÿ])", " ", html)
    # « Bleu 19 », « joueur A », « page 3 », « étape 2 » : pas de coupure entre le mot et son numéro
    html = re.sub(r"\b([A-ZÀ-Ý][a-zà-ÿ]{1,12}) (?=\d+\b)", "\\1 ", html)
    html = re.sub(r"\b(" + NBSP_WORDS + r") (?=(?:\d+|[A-Z])\b)", "\\1 ", html)
    return html


def marker(width, size):
    adv = FBODY.glyph_advance(ord(MARK))
    n = 1
    while width / (n * adv) > size * 0.95:
        n += 1
    return (f'<span class="mk" style="white-space:nowrap;font-size:{width / (n * adv):.2f}pt">'
            f'{MARK * n}</span>')


def para_style(lines):
    cnt = {}
    for l in lines:
        for s in text_spans(l):
            k = (s["font"].split("+")[-1], round(s["size"], 2), s["color"])
            cnt[k] = cnt.get(k, 0) + len(s["text"].strip())
    font, size, color = max(cnt, key=cnt.get)
    fam = CODE.get(font, (BODY, 0, 0))[0]
    styles = [fcode(s) for l in lines for s in text_spans(l)]
    bold = int(all(st[1] for st in styles))
    ital = int(all(st[2] for st in styles))
    return fam, bold, ital, size, "#%06x" % color


def wrap(html, fam, bold, ital, size, color, lead, align):
    st = (f"font-family:{fam};font-size:{size:.2f}pt;color:{color};line-height:{lead:.2f}pt;"
          f"text-align:{align};font-weight:{'bold' if bold else 'normal'};"
          f"font-style:{'italic' if ital else 'normal'};")
    return f'<div style="{st}">{html}</div>'


def render(rect, html, tag):
    tmp = pymupdf.open()
    pg = tmp.new_page(width=1000, height=2000)
    pg.insert_htmlbox(pymupdf.Rect(rect.x0, 100, rect.x1, 1900), html, css=CSS, archive=ARCH)
    spans = [s for b in pg.get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"]
             if s["text"].strip()]
    if not spans:
        fail(f"{tag} : le texte français ne produit rien à l'écran (vide, ou police sans ces caractères ?)")
    base = min(s["origin"][1] for s in spans) - 100
    bot = max(s["origin"][1] for s in spans) - 100
    nlines = len({round(s["origin"][1], 1) for s in spans})
    return base, bot, nlines


# ------------------------------------------------------------------ image removal
IMGDO = re.compile(rb"(-?[\d.]+) (-?[\d.]+) (-?[\d.]+) (-?[\d.]+) (-?[\d.]+) (-?[\d.]+) cm\s*(/[\w.]+ Do)")


def strip_icons(page, icons):
    """Remove the 'Do' of the lifted images (matched by the position of their cm matrix)."""
    H = page.rect.height
    done = set()
    for xref in page.get_contents():
        data = doc.xref_stream(xref)

        def rimg(m):
            a, b, c, d, e, f = (float(v) for v in m.groups()[:6])
            if abs(b) > 1e-3 or abs(c) > 1e-3:
                return m.group(0)
            r = pymupdf.Rect(e, H - (f + d), e + a, H - f)
            for i, ic in enumerate(icons):
                if i not in done and abs(r.x0 - ic["rect"].x0) < 0.4 and abs(r.y1 - ic["rect"].y1) < 0.4:
                    done.add(i)
                    return m.group(0)[:-len(m.group(7))]
            return m.group(0)

        new = IMGDO.sub(rimg, data)
        if new != data:
            doc.update_stream(xref, new)
    for i, ic in enumerate(icons):
        if ic["kind"] == "vec":
            continue
        if i not in done:
            log.append(f"page {page.number} : icône {ic['rect']} NON retirée de l'original")


def draw_icon(page, ic, cx, cy, k=1.0):
    w, h = ic["rect"].width * k, ic["rect"].height * k
    if ic["kind"] == "vec":
        c0 = (ic["rect"].tl + ic["rect"].br) / 2

        def mv(p):
            return pymupdf.Point(cx + (p.x - c0.x) * k, cy + (p.y - c0.y) * k)

        # paint in the original order (largest first: background disc, then the white symbol)
        for dr in sorted(ic["drs"], key=lambda d: d.get("seqno", 0)):
            sh = page.new_shape()
            for it in dr["items"]:
                if it[0] == "l":
                    sh.draw_line(mv(it[1]), mv(it[2]))
                elif it[0] == "c":
                    sh.draw_bezier(mv(it[1]), mv(it[2]), mv(it[3]), mv(it[4]))
                elif it[0] == "re":
                    sh.draw_rect(pymupdf.Rect(mv(it[1].tl), mv(it[1].br)))
                elif it[0] == "qu":
                    q = it[1]
                    sh.draw_quad(pymupdf.Quad(mv(q.ul), mv(q.ur), mv(q.ll), mv(q.lr)))
            sh.finish(fill=dr.get("fill"), color=dr.get("color"), width=(dr.get("width") or 0) * k,
                      even_odd=dr.get("even_odd", False), closePath=dr.get("closePath", False),
                      fill_opacity=dr.get("fill_opacity") or 1)
            sh.commit()
        return
    page.insert_image(pymupdf.Rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), xref=ic["xref"])


# ------------------------------------------------------------------ mini-cards -> flows (spec.CARD_STYLE)
def span_is(s, crit):
    return (("color" not in crit or s["color"] == crit["color"])
            and ("font" not in crit or crit["font"] in s["font"])
            and ("maxsize" not in crit or s["size"] < crit["maxsize"])
            and ("minsize" not in crit or s["size"] >= crit["minsize"]))


def card_flows():
    flows = []
    if CARD_PAGES and not CARD_STYLE:
        fail("CARD_PAGES est rempli mais CARD_STYLE manque dans spec.py (voir spec_modele.py)")
    if not CARD_PAGES:
        return flows
    kinds = CARD_STYLE["kinds"]
    zx0, zx1, zy0, zy1 = CARD_STYLE.get("zone", (10, 40, 0, 26))
    for pno, nums in CARD_PAGES.items():
        lines_of = page_lines(pno)
        allines = [(bi, li, l) for bi, ls in lines_of.items() for li, l in enumerate(ls)
                   if abs(l["dir"][0] - 1) < 0.01 and ltext(l).strip()]
        anchors = [(int(ltext(l).strip()), l) for bi, li, l in allines
                   if span_is(l["spans"][0], CARD_STYLE["number"]) and ltext(l).strip().isdigit()]
        groups = {}
        for bi, li, l in allines:
            s = l["spans"][0]
            kind = next((k for k, crit in kinds.items() if span_is(s, crit)), None)
            if not kind:
                continue
            x, y = l["bbox"][0], l["bbox"][1]

            def rel(a):  # position of the line in units of the card-number size
                sz = a[1]["spans"][0]["size"]
                return (x - a[1]["bbox"][0]) / sz, (y - a[1]["bbox"][1]) / sz

            cand = [a for a in anchors if zx0 < rel(a)[0] < zx1 and zy0 < rel(a)[1] < zy1]
            best = min(cand, key=lambda a: rel(a)[0] ** 2 + rel(a)[1] ** 2, default=None)
            if best is None:
                continue
            groups.setdefault((best[0], kind), []).append(f"b{bi}:{li}")
        for n in nums:
            if n not in CARDS:
                fail(f"page {pno} : la carte {n} est dans CARD_PAGES mais pas dans CARDS")
            texts = CARDS[n] if isinstance(CARDS[n], dict) else dict(zip(kinds, CARDS[n]))
            for kind, html in texts.items():
                src_ = groups.get((n, kind))
                if not src_:
                    log.append(f"page {pno} carte {n} : lignes « {kind} » introuvables")
                    continue
                flows.append(dict(page=pno, vcenter=True, kmin=0.7, slack=0.6,
                                  paras=[dict(src=" ".join(src_), html=html, align="center", wide=False,
                                              grow=1.5)]))
    return flows


# ------------------------------------------------------------------ main
by_page = {}
for f in FLOWS + card_flows():
    if not 0 <= f["page"] < len(src):
        fail(f"flux de la page {f['page']} : le livret n'a que {len(src)} pages (numérotées 0 à {len(src) - 1})")
    by_page.setdefault(f["page"], []).append(f)

for pno, flows in sorted(by_page.items()):
    page = doc[pno]
    lines_of = page_lines(pno)
    XL, XR = column(pno, lines_of)
    auto = pno not in COLUMNS and "*" not in COLUMNS
    SEGS = segments(lines_of) if auto else []
    page_gut = gutters(SEGS, XL, XR, src[pno].rect.y0, src[pno].rect.y1) if auto else []
    BADGES = badges(pno)
    log.append(f"page {pno} : colonne de texte {XL:.0f}–{XR:.0f}" + (" (auto, colonnes détectées par paragraphe)"
                                                                    if auto else ""))
    all_icons = find_icons(src[pno])
    thin = [pymupdf.Rect(d["rect"]) for d in src[pno].get_drawings()
            if d["rect"].height < 1.6 and d["rect"].width > 3]  # candidate underlines
    unders = []
    lifted = []
    jobs = []
    # 1. collect lines and icons, redact the original text
    for fl in flows:
        paras = []
        for p in fl["paras"]:
            raw = sel_lines(lines_of, p["src"], pno)
            allrects = [pymupdf.Rect(l["bbox"]) for l in raw]
            lines = [l for l in dedupe(raw) if text_spans(l)]
            if not lines:
                log.append(f"page {pno} {p['src']} : aucune ligne de texte")
                continue
            xs0 = min(l["bbox"][0] for l in lines) - 0.5
            xs1 = max(l["bbox"][2] for l in lines) + 0.5
            mine = []
            for ic in ([] if p.get("noicons") else all_icons):  # noicons: nearby pictures are not inline icons
                if ic.get("taken"):
                    continue
                c = (ic["rect"].tl + ic["rect"].br) / 2
                for l in lines:
                    r = pymupdf.Rect(l["bbox"])
                    if r.y0 - 1 <= c.y <= r.y1 + 1 and xs0 <= c.x <= xs1:
                        base = l["spans"][0]["origin"][1]
                        ic.update(taken=True, base=base, off=(c.y - base) / l["spans"][0]["size"])
                        mine.append(ic)
                        break
            mine.sort(key=lambda ic: (round(ic["base"]), ic["rect"].x0))
            lifted += mine
            for r in allrects:
                h = r.height
                page.add_redact_annot(r + (-0.3, h * 0.2, 0.3, -h * 0.2))
            for l in raw:  # underlines drawn just below the baseline of a replaced line
                base, size, bb = l["spans"][0]["origin"][1], l["spans"][0]["size"], l["bbox"]
                unders += [u for u in thin if u not in unders and base - 1 <= u.y0 <= base + 0.35 * size
                           and u.x0 < bb[2] and u.x1 > bb[0]]
            if "fix" not in p:  # numbered step drawn on a badge: keep it on its badge
                c0 = [c for s in lines[0]["spans"] for c in s["chars"] if c["c"].strip()][0]
                cc = (pymupdf.Rect(c0["bbox"]).tl + pymupdf.Rect(c0["bbox"]).br) / 2
                if any(b.contains(cc) for b in BADGES):
                    p = dict(p, fix=True)
            bul = None
            if p.get("bullet"):
                c0 = [c for s in lines[0]["spans"] for c in s["chars"] if c["c"].strip()][0]
                bul = dict(x=c0["bbox"][0], bold=fcode(lines[0]["spans"][0])[1])
            paras.append(dict(p, lines=lines, icons=mine, bul=bul))
        jobs.append((fl, paras))
    strip_icons(page, lifted)
    page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE,
                          graphics=pymupdf.PDF_REDACT_LINE_ART_NONE,
                          text=pymupdf.PDF_REDACT_TEXT_REMOVE)
    vec = [ic for ic in lifted if ic["kind"] == "vec"]
    for ic in vec:  # one zone per icon: overlapping zones (small one first) leave the big path in place
        page.add_redact_annot(ic["rect"] + (-0.3, -0.3, 0.3, 0.3))
    for u in unders:
        page.add_redact_annot(u + (-0.5, -0.8, 0.5, 0.8))
    if unders:
        log.append(f"page {pno} : {len(unders)} soulignement(s) d'origine retiré(s) — <u>…</u> dans le français "
                   f"pour souligner")
    if vec or unders:
        page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE,
                              graphics=pymupdf.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED,
                              text=pymupdf.PDF_REDACT_TEXT_NONE)

    if AVANT_TEXTE:  # spec hook, drawn after the redactions and under the French text
        AVANT_TEXTE(page, pno, log)

    # 2. lay out the French text
    to_draw = []
    for fl, paras in jobs:
        if not paras:
            continue
        tag = f"page {pno} {paras[0]['src']}"
        k = 1.0
        while True:
            y_prev_bot = None
            placed = []
            clash = False
            for p in paras:
                lines = p["lines"]
                fam, bold, ital, size, color = para_style(lines)
                size *= SIZE_K.get(fam, 1.0)
                fam, size, color = p.get("fam", fam), p.get("size", size), p.get("color", color)
                bold, ital = p.get("bold", bold), p.get("ital", ital)
                if fam not in FAMILIES:
                    fail(f"{tag} : famille « {fam} » inconnue (familles de spec.CSS : {', '.join(sorted(FAMILIES))})")
                bases = sorted({round(l["spans"][0]["origin"][1], 1) for l in lines})
                lead = p.get("lead") or ((bases[-1] - bases[0]) / (len(bases) - 1) if len(bases) > 1
                                         else size * 1.17)
                x0 = min(content_x0(l) if p.get("bullet") else l["bbox"][0] for l in lines)
                x1 = max(l["bbox"][2] for l in lines)
                # column of this paragraph: between the white separators around it, at its height
                GUT = gutters(SEGS, XL, XR, min(l["bbox"][1] for l in lines), max(l["bbox"][3] for l in lines))
                # a short line (title) leaves a wide blank after it: the column ends one usual gap before the
                # next column, not right after the title
                G = min([b - a for a, b in GUT if b - a < 40] + [b - a for a, b in page_gut if b - a < 40]
                        + [13])
                CL = min(max([a + G if b - a > 40 else b for a, b in GUT if a < x0], default=XL), x0)
                CR = max(min([b - G if b - a > 40 else a for a, b in GUT if b > x1], default=XR), x1)
                # the neighbouring column may hold only a picture at this height: look for its text higher or lower
                py0, py1 = min(l["bbox"][1] for l in lines), max(l["bbox"][3] for l in lines)
                near = [(a, b) for a, b, sy0, sy1 in SEGS if sy1 > py0 - 150 and sy0 < py1 + 150]
                right = [a for a, b in near if a > x1 + 8]
                left = [b for a, b in near if b < x0 - 8]
                if right:
                    CR = max(min(CR, min(right) - G), x1)
                if left:
                    CL = min(max(CL, max(left) + G), x0)
                align = p.get("align", "left")
                if align == "center":
                    cx = (x0 + x1) / 2
                    half = (x1 - x0) / 2
                    if p.get("wide", True):
                        half = max(half, min(cx - fl.get("x0", CL), fl.get("x1", CR) - cx))
                    half += p.get("grow", 0)
                    x0, x1 = cx - half, cx + half
                else:
                    x0 = p.get("x0", x0)
                    x1 = (p["x1"] if "x1" in p else max(x1, fl.get("x1", CR))) + p.get("grow", 0)
                rect = pymupdf.Rect(x0 - 0.5, 0, x1 + 0.5, 0)
                html = typo(p["html"])
                sz, ld = size * k, lead * k
                icons = list(p["icons"])
                if html.count("{}") != len(icons) and k == 1.0:
                    log.append(f"{tag} : {html.count('{}')} {{}} dans le texte pour {len(icons)} icône(s) "
                               f"dans l'original")

                def rep(m):
                    ic = icons.pop(0) if icons else None
                    w = ic["rect"].width * k if ic else 8
                    return marker(w + 1.0 * k, sz)

                html = re.sub(r"\{\}", rep, html)
                html = wrap(html, fam, bold, ital, sz, color, ld, align)
                fb, lb, n = render(rect, html, tag)
                if y_prev_bot is None or p.get("fix"):  # fix: keep the original baseline
                    target = bases[0] + fl.get("dy", 0)
                    if y_prev_bot is not None and y_prev_bot > target - 0.75 * ld:
                        clash = True  # the text above runs into this anchored paragraph
                else:
                    target = y_prev_bot + (bases[0] - prev_last_base) * k + p.get("gap", 0)
                placed.append(dict(rect=rect, html=html, dy=target - fb, icons=p["icons"], size=sz,
                                   base=target, n=n, bullet=p.get("bullet"), bul=p["bul"], ld=ld,
                                   fam=fam, color=color))
                y_prev_bot = target + (lb - fb)
                prev_last_base = bases[-1]
            first_base = paras[0]["lines"][0]["spans"][0]["origin"][1]
            if fl.get("vcenter"):
                old_h = prev_last_base - first_base
                new_h = y_prev_bot - placed[0]["base"]
                ok = new_h <= old_h + fl.get("slack", 0) * placed[0]["ld"] + 0.01
            else:
                limit = fl.get("maxy", prev_last_base) + 0.6
                ok = y_prev_bot <= limit and not clash
            if ok or k <= fl.get("kmin", 0.84):
                break
            k -= 0.02
        if fl.get("vcenter"):
            shift = ((first_base + prev_last_base) - (placed[0]["base"] + y_prev_bot)) / 2
            for pl in placed:
                pl["dy"] += shift
                pl["base"] += shift
        if k < 1 and not fl.get("vcenter"):
            log.append(f"{tag} : police réduite à {k:.2f}" + ("" if ok else "  DÉBORDE"))
        elif not ok:
            log.append(f"{tag} : texte de carte DÉBORDE (police à {k:.2f})")
        to_draw += [(pl, k) for pl in placed]

    for pl, k in to_draw:
        r = pl["rect"]
        page.insert_htmlbox(pymupdf.Rect(r.x0, pl["dy"], r.x1, pl["dy"] + 1800), pl["html"],
                            css=CSS, archive=ARCH)
        if pl["bullet"]:
            b = pl["bul"]
            ff = face_file(pl["fam"], bool(b["bold"]))
            col = int(pl["color"][1:], 16)
            page.insert_text((b["x"], pl["base"]), pl["bullet"],
                             fontsize=pl["size"] * (1.3 if pl["bullet"] == "•" else 1),
                             fontname="Bu" + re.sub(r"\W", "", os.path.splitext(ff)[0])[:20],
                             fontfile=os.path.join(FF, ff),
                             color=((col >> 16) / 255, (col >> 8 & 255) / 255, (col & 255) / 255))

    # 3. replace the markers by the icons
    raw = page.get_text("rawdict")
    groups = []
    for b in raw["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                cur = None
                for c in s["chars"]:
                    if c["c"] == MARK:
                        if cur is None:
                            cur = pymupdf.Rect(c["bbox"])
                            groups.append([cur, s["origin"][1], s["size"]])
                        else:
                            groups[-1][0] |= pymupdf.Rect(c["bbox"])
                    else:
                        cur = None
    for pl, k in to_draw:
        mine = [g for g in groups if pl["rect"].x0 - 1 <= g[0].x0 and g[0].x1 <= pl["rect"].x1 + 1 and
                pl["base"] - 1 <= g[1] <= pl["base"] + pl["n"] * pl["ld"] + 1]
        mine.sort(key=lambda g: (round(g[1], 1), g[0].x0))
        mine = mine[:len(pl["icons"])]
        for g, ic in zip(mine, pl["icons"]):
            groups.remove(g)
            r = g[0]
            page.add_redact_annot(pymupdf.Rect(r.x0 + 0.3, g[1] - g[2] * 0.35, r.x1 - 0.3, g[1] - g[2] * 0.1))
            ic["draw"] = (ic, (r.x0 + r.x1) / 2, g[1] + ic["off"] * pl["size"], k)
    page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE,
                          graphics=pymupdf.PDF_REDACT_LINE_ART_NONE,
                          text=pymupdf.PDF_REDACT_TEXT_REMOVE)
    for ic in lifted:
        if "draw" in ic:
            draw_icon(page, *ic["draw"])
        else:
            log.append(f"page {pno} : icône {ic['rect']} non replacée")

doc.subset_fonts()
doc.save(OUT, garbage=3, deflate=True)

# ------------------------------------------------------------------ report: forgotten text, leftover markers
LETTER = re.compile(r"[^\W\d_]")
forgot, numbers = [], 0
for pno in range(len(src)):
    lines_of = page_lines(pno)
    skip = set(sel_ids(lines_of, IGNORE[pno], pno, strict=False)) if pno in IGNORE else set()
    for bi, ls in lines_of.items():
        for li, l in enumerate(ls):
            t = ltext(l).strip()
            if not t or (pno, bi, li) in used or (bi, li) in skip:
                continue
            if LETTER.search(t):
                forgot.append(f"  page {pno} b{bi}:{li}  {t[:70]}")
            else:
                numbers += 1
log.append("")
if forgot:
    log.append(f"TEXTE NON TRADUIT ({len(forgot)} ligne(s)) — à traduire, ou à mettre dans IGNORE de spec.py "
               f"si c'est voulu (titre du jeu, calque caché…) :")
    log += forgot
else:
    log.append("Texte non traduit : aucun.")
if numbers:
    log.append(f"({numbers} ligne(s) sans lettres non remplacée(s) : numéros de page, chiffres, symboles.)")
out = pymupdf.open(OUT)
left = [str(p.number) for p in out if MARK in p.get_text()]
log.append(f"MARQUEUR ¤ RESTANT pages {', '.join(left)}" if left else "Marqueurs ¤ restants : aucun.")
try:
    import controle
    controle.check_text(OUT, SRC, controle.our_names(os.path.join(FF, f) for f in set(FACES.values())), log)
except ImportError:
    log.append("(controle.py absent : pas de contrôle de mise en page)")

journal = os.path.splitext(OUT)[0] + "_journal.txt"
open(journal, "w", encoding="utf8").write("\n".join(log) + "\n")
print("\n".join(log))
print("enregistré :", OUT, "— journal :", journal)
