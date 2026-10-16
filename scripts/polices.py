"""Outils pour choisir les polices de remplacement (voir references/polices.md).

  python -X utf8 polices.py extraire livret.pdf [fonts]
      extrait les polices embarquées du PDF dans le dossier fonts/
  python -X utf8 polices.py glyphes police.ttf [autre.otf ...]
      lettres réellement dessinées et caractères français manquants (accents, « », ’, œ…)
  python -X utf8 polices.py largeur originale.ttf candidate.ttf [autre.ttf ...] [--texte "phrase du livret"]
      facteur de taille SIZE_K pour que la candidate prenne la même largeur, et largeur de l'espace
  python -X utf8 polices.py planche planche.png originale.ttf candidate.ttf [...] [--texte "phrase du livret"]
      image comparative : la même phrase dans chaque police, à regarder avant de choisir
"""
import argparse, os, sys
import pymupdf

FRENCH = "àâäæçéèêëîïôöœùûüÿÀÂÄÆÇÉÈÊËÎÏÔÖŒÙÛÜŸ«»’"
BASIC = ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
         ".,;:!?'\"()-–—/%+=&")
SAMPLE = "Le premier joueur entame le pli ; chacun doit fournir la couleur demandée."


USED = ".caracteres.txt"  # written by "extraire" next to each font: characters the booklet prints with it
MODES = {"dessin": "", "table": "  (table seule : dessins non vérifiés)",
         "livret": "  (police CID sans table de caractères : caractères d'après le texte du livret)"}


def drawn_chars(path):
    """(caractères, mode) : glyphes réellement dessinés ; à défaut la table de caractères ; pour une police CID
    extraite d'un PDF (pas de table), les caractères que le livret imprime avec elle (fichier .caracteres.txt)."""
    out, mode = set(), "dessin"
    try:
        from fontTools.ttLib import TTFont
        from fontTools.pens.boundsPen import BoundsPen
        f = TTFont(path, fontNumber=0)
        gs = f.getGlyphSet()
        for cp, g in (f.getBestCmap() or {}).items():
            bp = BoundsPen(gs)
            gs[g].draw(bp)
            if bp.bounds:
                out.add(chr(cp))
    except Exception:  # Type 1, CFF nu… : on se contente de la table de caractères
        font = pymupdf.Font(fontfile=path)
        out, mode = {chr(c) for c in range(32, 0x2030) if font.has_glyph(c)}, "table"
    side = os.path.splitext(path)[0] + USED
    if len(out) < 5 and os.path.isfile(side):
        out, mode = set(open(side, encoding="utf8").read()) - {"\n"}, "livret"
    return out, mode


def norm(name):
    return "".join(ch for ch in name.lower() if ch.isalnum())


def extraire(a):
    doc = pymupdf.open(a.pdf)
    os.makedirs(a.dossier, exist_ok=True)
    fonts, type3, absent = {}, set(), set()  # one file per font name: the largest of its subsets
    for page in doc:
        for xref, ext, typ, name, *_ in page.get_fonts():
            clean = name.split("+")[-1]
            if typ == "Type3":
                type3.add(xref)
                continue
            if xref == 0 or any(xref in v["xrefs"] for v in fonts.values()):
                continue
            fname, fext, ftype, data = doc.extract_font(xref)
            if not data:
                absent.add(f"{clean} ({typ})")
                continue
            cur = fonts.setdefault(clean, dict(xrefs=set(), data=b"", ext=fext, typ=typ))
            cur["xrefs"].add(xref)
            if len(data) > len(cur["data"]):
                cur.update(data=data, ext=fext)
    used = {}
    for page in doc:
        for b in page.get_text("rawdict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    used.setdefault(s["font"].split("+")[-1], set()).update(c["c"] for c in s["chars"])
    for clean, v in sorted(fonts.items()):
        path = os.path.join(a.dossier, f"{clean}.{v['ext']}")
        open(path, "wb").write(v["data"])
        # span font names may differ from the font's name ("Lato-Regular" / "Lato Regular", truncated names)
        key = norm(clean)
        mine = set().union(*[c for f, c in used.items() if norm(f) and (key.startswith(norm(f))
                                                                         or norm(f).startswith(key))] or [set()])
        chars = "".join(sorted(mine - {" ", "　"}))
        open(os.path.join(a.dossier, clean + USED), "w", encoding="utf8").write(chars)
        n = len(v["xrefs"])
        print(f"  {clean} ({v['typ']}) -> {path}" + (f"  [{n} sous-ensembles, le plus complet gardé]" if n > 1 else "")
              + f"  — {len(chars)} caractères utilisés dans le livret")
    for name in sorted(absent):
        print(f"  {name} : non embarquée (police système, à chercher telle quelle)")
    if type3:
        print(f"  {len(type3)} police(s) Type3 : glyphes dessinés dans le PDF, rien à extraire — "
              f"choisir une remplaçante à l'œil")


def glyphes(a):
    for path in a.polices:
        chars, mode = drawn_chars(path)
        miss_fr = "".join(c for c in FRENCH if c not in chars)
        miss_basic = "".join(c for c in BASIC if c not in chars)
        print(f"== {os.path.basename(path)}{MODES[mode]}")
        print(f"  {len(chars)} caractères " + ("utilisés" if mode == "livret" else "dessinés"))
        print(f"  français manquants : {miss_fr or 'aucun'}")
        print(f"  de base manquants  : {miss_basic or 'aucun'}")


def unreadable(path):
    """True for a CID font without a character table: its widths cannot be measured from text."""
    if drawn_chars(path)[1] == "livret":
        print(f"attention : {os.path.basename(path)} est une police CID sans table de caractères — "
              f"impossible de mesurer ou d'afficher du texte avec elle ; comparer à l'œil sur un agrandissement "
              f"du livret (grille.py) et garder SIZE_K = 1.0 au départ")
        return True
    return False


def warn_absent(path, text):
    chars, _ = drawn_chars(path)
    absent = sorted({c for c in text if c not in chars and c != " "})
    if absent:
        print(f"attention : l'originale n'a pas « {''.join(absent)} » — prendre une phrase du livret (--texte)")


def largeur(a):
    if unreadable(a.originale):
        return
    orig = pymupdf.Font(fontfile=a.originale)
    warn_absent(a.originale, a.texte)
    w0 = orig.text_length(a.texte, 1)
    print(f"== {os.path.basename(a.originale)} (originale) : espace {orig.glyph_advance(32):.2f} em")
    for path in a.candidates:
        f = pymupdf.Font(fontfile=path)
        k = w0 / f.text_length(a.texte, 1)
        sp = f.glyph_advance(32)
        warn = "  (espace large : texte qui paraît justifié, voir polices.md)" if sp > 0.3 else ""
        print(f"  {os.path.basename(path)} : SIZE_K = {k:.2f}, espace {sp:.2f} em{warn}")


def planche(a):
    fonts = ([] if unreadable(a.originale) else [a.originale]) + a.candidates
    if fonts[0] == a.originale:
        warn_absent(a.originale, a.texte)
    size, gap = 16, 34
    W = max(pymupdf.Font(fontfile=p).text_length(a.texte, size) for p in fonts) + 40
    doc = pymupdf.open()
    page = doc.new_page(width=max(W, 400), height=gap * (2 * len(fonts)) + 20)
    y = 24
    for i, path in enumerate(fonts):
        label = os.path.basename(path) + (" (originale)" if path == a.originale else "")
        page.insert_text((20, y), label, fontsize=9, color=(0.4, 0.4, 0.4))
        page.insert_text((20, y + 22), a.texte, fontsize=size, fontname=f"F{i}", fontfile=path)
        y += 2 * gap
    page.get_pixmap(dpi=110).save(a.sortie)
    print("planche ->", a.sortie)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("extraire"); p.add_argument("pdf"); p.add_argument("dossier", nargs="?", default="fonts")
    p.set_defaults(fn=extraire)
    p = sub.add_parser("glyphes"); p.add_argument("polices", nargs="+"); p.set_defaults(fn=glyphes)
    p = sub.add_parser("largeur"); p.add_argument("originale"); p.add_argument("candidates", nargs="+")
    p.add_argument("--texte", default=SAMPLE); p.set_defaults(fn=largeur)
    p = sub.add_parser("planche"); p.add_argument("sortie"); p.add_argument("originale")
    p.add_argument("candidates", nargs="+"); p.add_argument("--texte", default=SAMPLE); p.set_defaults(fn=planche)
    a = ap.parse_args()
    for path in [getattr(a, k) for k in ("pdf", "originale") if hasattr(a, k)] + \
            list(getattr(a, "polices", []) or []) + list(getattr(a, "candidates", []) or []):
        if not os.path.isfile(path):
            sys.exit(f"ERREUR : fichier introuvable : {path}")
    a.fn(a)


if __name__ == "__main__":
    main()
