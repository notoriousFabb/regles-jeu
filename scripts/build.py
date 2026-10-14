# -*- coding: utf-8 -*-
"""Rebuild the Vazerneiros / Tricklings rulebook in French, keeping every image/vector in place.

Derived from _outils/Dr_Science/build.py (flows of paragraphs, inline icons put back on "{}").
Additions: duplicated text lines (printed twice) are merged, bullets inside spans ("•\t", "1.\t"),
Rumor cards translated automatically from spec_vz.CARDS, vertical centring for card texts."""
import os, re, sys
import pymupdf
import spec
FLOWS = spec.FLOWS
CARDS = getattr(spec, "CARDS", {})
CARD_PAGES = getattr(spec, "CARD_PAGES", {})

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
SRC = r"CHEMIN/VERS/livret_EN.pdf"  # A ADAPTER
OUT = sys.argv[1] if len(sys.argv) > 1 else "out_fr.pdf"
FF = os.path.join(HERE, "ff")
ARCH = pymupdf.Archive(FF)
MARK = "\u00a4"
FBODY = pymupdf.Font(fontfile=os.path.join(FF, "AlegreyaSans-Regular.ttf"))

CSS = """
@font-face{font-family:Av;src:url(AlegreyaSans-Regular.ttf);}
@font-face{font-family:Av;font-weight:bold;src:url(AlegreyaSans-Bold.ttf);}
@font-face{font-family:Av;font-style:italic;src:url(AlegreyaSans-Italic.ttf);}
@font-face{font-family:Av;font-weight:bold;font-style:italic;src:url(AlegreyaSans-BoldItalic.ttf);}
@font-face{font-family:BS;src:url(CaveatBrush-Regular.ttf);}
@font-face{font-family:BS;font-weight:bold;src:url(CaveatBrush-Regular.ttf);}
@font-face{font-family:H;src:url(Handlee-Regular.ttf);}
@font-face{font-family:HI;src:url(Kalam-Tight.ttf);}
* {margin:0; padding:0;}
b {font-weight:bold;}
.mk {font-family:Av; font-weight:normal; font-style:normal;}
"""
# original font -> (family, bold, italic)
CODE = {"Duper": ("Av", 0, 0), "Duper-Ita": ("Av", 0, 1), "Duper-Bold": ("Av", 1, 0), "Duper-BoldIta": ("Av", 1, 1),
        "ChristmasChalk": ("H", 0, 0), "ChristmasChalk-Italic": ("HI", 0, 0),
        "CCSignLanguage-Regular": ("BS", 0, 0), "CCSignLanguage-Bold": ("BS", 1, 0)}
SIZE_K = {"Av": 1.0, "BS": 1.17, "H": 1.15, "HI": 1.3}
BULLET = re.compile(r"^\s*(•|\d+\.)\s*")

src = pymupdf.open(SRC)
doc = pymupdf.open(SRC)
log = []


def fcode(s):
    return CODE.get(s["font"].split("+")[-1], ("Av", 0, 0))


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


def sel_lines(lines_of, sel):
    """'b12:2-4 b13' -> list of line dicts (duplicates printed twice are dropped later)."""
    out = []
    for s in sel.split():
        m = re.fullmatch(r"b(\d+)(?::(\d+)(?:-(\d+))?)?", s)
        bl = lines_of[int(m.group(1))]
        if m.group(2) is None:
            out += bl
        else:
            a = int(m.group(2))
            z = int(m.group(3)) if m.group(3) else a
            out += bl[a:z + 1]
    return out


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


def page_icons(pno):
    page = src[pno]
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


# ------------------------------------------------------------------ html helpers
def typo(html):
    html = re.sub(r" ([:;!?»])", "\u00a0\\1", html)
    html = html.replace("« ", "«\u00a0")
    html = re.sub(r"(?<=[A-Za-zÀ-ÿ])'", "’", html)
    html = html.replace(" {}", "\u00a0{}")
    html = re.sub(r"(?<=\b\d) (?=[a-zà-ÿ])", "\u00a0", html)
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
    fam = CODE.get(font, ("Av", 0, 0))[0]
    styles = [fcode(s) for l in lines for s in text_spans(l)]
    bold = int(all(st[1] for st in styles))
    ital = int(all(st[2] for st in styles))
    return fam, bold, ital, size, "#%06x" % color


def wrap(html, fam, bold, ital, size, color, lead, align):
    st = (f"font-family:{fam};font-size:{size:.2f}pt;color:{color};line-height:{lead:.2f}pt;"
          f"text-align:{align};font-weight:{'bold' if bold else 'normal'};"
          f"font-style:{'italic' if ital else 'normal'};")
    return f'<div style="{st}">{html}</div>'


def render(rect, html):
    tmp = pymupdf.open()
    pg = tmp.new_page(width=1000, height=2000)
    pg.insert_htmlbox(pymupdf.Rect(rect.x0, 100, rect.x1, 1900), html, css=CSS, archive=ARCH)
    spans = [s for b in pg.get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"]
             if s["text"].strip()]
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
            log.append(f"page {page.number}: icon {ic['rect']} NOT removed")


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


# ------------------------------------------------------------------ Rumor cards -> flows
def card_flows():
    flows = []
    for pno, nums in CARD_PAGES.items():
        lines_of = page_lines(pno)
        allines = [(bi, li, l) for bi, ls in lines_of.items() for li, l in enumerate(ls)
                   if abs(l["dir"][0] - 1) < 0.01 and ltext(l).strip()]
        anchors = [(int(ltext(l).strip()), l) for bi, li, l in allines
                   if l["spans"][0]["color"] == 0xc7c4b1 and ltext(l).strip().isdigit()]
        groups = {}
        for bi, li, l in allines:
            s = l["spans"][0]
            kind = "flav" if s["color"] == 0xffe2aa else (
                "eff" if s["color"] == 0 and "ChristmasChalk" in s["font"] and s["size"] < 4 else None)
            if not kind:
                continue
            x, y = l["bbox"][0], l["bbox"][1]

            def rel(a):  # position of the line in units of the card-number size
                sz = a[1]["spans"][0]["size"]
                return (x - a[1]["bbox"][0]) / sz, (y - a[1]["bbox"][1]) / sz

            cand = [a for a in anchors if 10 < rel(a)[0] < 40 and 0 < rel(a)[1] < 26]
            best = min(cand, key=lambda a: rel(a)[0] ** 2 + rel(a)[1] ** 2, default=None)
            if best is None:
                continue
            groups.setdefault((best[0], kind), []).append(f"b{bi}:{li}")
        for n in nums:
            flav, eff = CARDS[n]
            for kind, html in (("eff", eff), ("flav", flav)):
                src_ = groups.get((n, kind))
                if not src_:
                    log.append(f"p{pno} card {n}: no {kind} lines found")
                    continue
                flows.append(dict(page=pno, vcenter=True, kmin=0.7, slack=0.6,
                                  paras=[dict(src=" ".join(src_), html=html, align="center", wide=False,
                                              grow=1.5)]))
    return flows


# ------------------------------------------------------------------ main
by_page = {}
for f in FLOWS + card_flows():
    by_page.setdefault(f["page"], []).append(f)

for pno, flows in sorted(by_page.items()):
    page = doc[pno]
    XL, XR = (20, 297) if pno % 2 == 0 else (31, 307)  # text column of left / right pages
    lines_of = page_lines(pno)
    all_icons = page_icons(pno)
    lifted = []
    jobs = []
    # 1. collect lines and icons, redact the English
    for fl in flows:
        paras = []
        for p in fl["paras"]:
            raw = sel_lines(lines_of, p["src"])
            allrects = [pymupdf.Rect(l["bbox"]) for l in raw]
            lines = [l for l in dedupe(raw) if text_spans(l)]
            if not lines:
                log.append(f"p{pno} {p['src']}: no text lines")
                continue
            xs0 = min(l["bbox"][0] for l in lines) - 0.5
            xs1 = max(l["bbox"][2] for l in lines) + 0.5
            mine = []
            for ic in all_icons:
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
    for ic in vec:
        for dr in ic["drs"]:
            page.add_redact_annot(dr["rect"] + (-0.3, -0.3, 0.3, 0.3))
    if vec:
        page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE,
                              graphics=pymupdf.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED,
                              text=pymupdf.PDF_REDACT_TEXT_NONE)

    # 2. lay out the French text
    to_draw = []
    for fl, paras in jobs:
        if not paras:
            continue
        tag = f"p{pno} {paras[0]['src']}"
        k = 1.0
        while True:
            y_prev_bot = None
            placed = []
            for p in paras:
                lines = p["lines"]
                fam, bold, ital, size, color = para_style(lines)
                size *= SIZE_K.get(fam, 1.0)
                fam, size, color = p.get("fam", fam), p.get("size", size), p.get("color", color)
                bold, ital = p.get("bold", bold), p.get("ital", ital)
                bases = sorted({round(l["spans"][0]["origin"][1], 1) for l in lines})
                lead = p.get("lead") or ((bases[-1] - bases[0]) / (len(bases) - 1) if len(bases) > 1
                                         else size * 1.17)
                x0 = min(content_x0(l) if p.get("bullet") else l["bbox"][0] for l in lines)
                x1 = max(l["bbox"][2] for l in lines)
                align = p.get("align", "left")
                if align == "center":
                    cx = (x0 + x1) / 2
                    half = (x1 - x0) / 2
                    if p.get("wide", True):
                        half = max(half, min(cx - fl.get("x0", XL), fl.get("x1", XR) - cx))
                    half += p.get("grow", 0)
                    x0, x1 = cx - half, cx + half
                else:
                    x0 = p.get("x0", x0)
                    x1 = (p["x1"] if "x1" in p else max(x1, fl.get("x1", XR))) + p.get("grow", 0)
                rect = pymupdf.Rect(x0 - 0.5, 0, x1 + 0.5, 0)
                html = typo(p["html"])
                sz, ld = size * k, lead * k
                icons = list(p["icons"])
                if html.count("{}") != len(icons):
                    log.append(f"{tag}: {html.count('{}')} placeholders for {len(icons)} icons")

                def rep(m):
                    ic = icons.pop(0) if icons else None
                    w = ic["rect"].width * k if ic else 8
                    return marker(w + 1.0 * k, sz)

                html = re.sub(r"\{\}", rep, html)
                html = wrap(html, fam, bold, ital, sz, color, ld, align)
                fb, lb, n = render(rect, html)
                if y_prev_bot is None or p.get("fix"):  # fix: keep the English baseline
                    target = bases[0] + fl.get("dy", 0)
                else:
                    target = y_prev_bot + (bases[0] - prev_last_base) * k + p.get("gap", 0)
                placed.append(dict(rect=rect, html=html, dy=target - fb, icons=p["icons"], size=sz,
                                   base=target, n=n, bullet=p.get("bullet"), bul=p["bul"], ld=ld))
                y_prev_bot = target + (lb - fb)
                prev_last_base = bases[-1]
            first_base = paras[0]["lines"][0]["spans"][0]["origin"][1]
            if fl.get("vcenter"):
                old_h = prev_last_base - first_base
                new_h = y_prev_bot - placed[0]["base"]
                ok = new_h <= old_h + fl.get("slack", 0) * placed[0]["ld"] + 0.01
            else:
                limit = fl.get("maxy", prev_last_base) + 0.6
                ok = y_prev_bot <= limit
            if ok or k <= fl.get("kmin", 0.84):
                break
            k -= 0.02
        if fl.get("vcenter"):
            shift = ((first_base + prev_last_base) - (placed[0]["base"] + y_prev_bot)) / 2
            for pl in placed:
                pl["dy"] += shift
                pl["base"] += shift
        if k < 1 and not fl.get("vcenter"):
            log.append(f"{tag}: font scale {k:.2f}" + ("" if ok else "  OVERFLOW"))
        elif not ok:
            log.append(f"{tag}: card text OVERFLOW at scale {k:.2f}")
        to_draw += [(pl, k) for pl in placed]

    for pl, k in to_draw:
        r = pl["rect"]
        page.insert_htmlbox(pymupdf.Rect(r.x0, pl["dy"], r.x1, pl["dy"] + 1800), pl["html"],
                            css=CSS, archive=ARCH)
        if pl["bullet"]:
            b = pl["bul"]
            ff = "AlegreyaSans-Bold.ttf"
            page.insert_text((b["x"], pl["base"]), pl["bullet"],
                             fontsize=pl["size"] * (1.3 if pl["bullet"] == "•" else 1),
                             fontname="AB" if "Bold" in ff else "AR", fontfile=os.path.join(FF, ff),
                             color=(0, 0, 0))

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
            log.append(f"page {pno}: icon at {ic['rect']} not re-placed")

doc.subset_fonts()
doc.save(OUT, garbage=3, deflate=True)
print("\n".join(log))
print("saved", OUT)
