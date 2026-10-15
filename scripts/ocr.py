"""Livret scanné : lit le texte des pages avec la reconnaissance de texte de Windows (OCR) et en tire les zones.
Usage : python -X utf8 ocr.py livret.pdf [langue=en-US] [zones.py]
Écrit zones.py (à recopier dans spec.py) : un Z(page, (x0, y0, x1, y1), "texte d'origine") par paragraphe, en
points PDF. Il reste à traduire chaque texte, à fusionner/couper les zones si besoin et à régler les tailles.
Langues installées : python -X utf8 ocr.py --langues. Le japonais demande le pack OCR de Windows
(PowerShell admin : Add-WindowsCapability -Online -Name "Language.OCR~~~ja-JP~0.0.1.0").
Prérequis : pip install winrt-runtime winrt-Windows.Media.Ocr winrt-Windows.Globalization
            winrt-Windows.Graphics.Imaging winrt-Windows.Storage.Streams winrt-Windows.Foundation
            winrt-Windows.Foundation.Collections"""
import asyncio, statistics, sys
import pymupdf

try:
    from winrt.windows.globalization import Language
    from winrt.windows.graphics.imaging import BitmapDecoder
    from winrt.windows.media.ocr import OcrEngine
    from winrt.windows.storage.streams import DataWriter, InMemoryRandomAccessStream
except ImportError:
    sys.exit("ERREUR : modules winrt absents — voir « Prérequis » en tête de ocr.py")

DPI = 300


async def bitmap(png):
    stream = InMemoryRandomAccessStream()
    w = DataWriter(stream)
    w.write_bytes(png)
    await w.store_async()
    stream.seek(0)
    dec = await BitmapDecoder.create_async(stream)
    return await dec.get_software_bitmap_async()


async def read_page(engine, page):
    k = DPI / 72
    pix = page.get_pixmap(dpi=DPI)
    res = await engine.recognize_async(await bitmap(pix.tobytes("png")))
    lines = []
    for ln in res.lines:
        rs = [w.bounding_rect for w in ln.words]
        x0 = min(r.x for r in rs) / k
        y0 = min(r.y for r in rs) / k
        x1 = max(r.x + r.width for r in rs) / k
        y1 = max(r.y + r.height for r in rs) / k
        lines.append(dict(text=ln.text, rect=pymupdf.Rect(x0, y0, x1, y1)))
    return lines


def paragraphs(lines):
    """Regroupe les lignes proches (même colonne, interligne normal) en paragraphes."""
    lines = sorted(lines, key=lambda l: (round(l["rect"].y0), l["rect"].x0))
    paras = []
    for l in lines:
        r = l["rect"]
        h = r.height
        best = None
        for p in paras:
            last = p["lines"][-1]["rect"]
            gap = r.y0 - last.y1
            overlap_x = min(r.x1, p["rect"].x1) - max(r.x0, p["rect"].x0)
            if -h * 0.3 < gap < h * 0.9 and overlap_x > 0.3 * min(r.width, p["rect"].width) \
                    and abs(h - last.height) < 0.45 * max(h, last.height) \
                    and abs(r.x0 - last.x0) < 2.5 * h:  # un titre centré ne rejoint pas le paragraphe
                best = p
        if best:
            best["lines"].append(l)
            best["rect"] |= r
        else:
            paras.append(dict(lines=[l], rect=pymupdf.Rect(r)))
    return paras


def main():
    if "--langues" in sys.argv:
        print([l.language_tag for l in OcrEngine.available_recognizer_languages])
        return
    src = sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else "en-US"
    out = sys.argv[3] if len(sys.argv) > 3 else "zones.py"
    engine = OcrEngine.try_create_from_language(Language(lang))
    if engine is None:
        sys.exit(f"ERREUR : langue OCR « {lang} » non installée dans Windows (installées : "
                 f"{[l.language_tag for l in OcrEngine.available_recognizer_languages]})")
    doc = pymupdf.open(src)
    res = ["# -*- coding: utf-8 -*-", f"# Zones lues par OCR ({lang}) dans {src} — texte d'origine à traduire.",
           "# Taille ≈ corps du texte d'origine (à ajuster) ; sous chaque zone, les lignes lues (pour couper si "
           "besoin).", ""]
    n = 0
    for page in doc:
        lines = asyncio.run(read_page(engine, page))
        res.append(f"# ================================================================ page {page.number}")
        for p in paragraphs(lines):
            r = p["rect"] + (-1, -1, 1, 1.5)
            hs = [l["rect"].height for l in p["lines"]]
            size = statistics.median(hs)
            text = " ".join(l["text"] for l in p["lines"]).replace('"', "'")
            res.append(f'Z({page.number}, ({r.x0:.1f}, {r.y0:.1f}, {r.x1:.1f}, {r.y1:.1f}), "{text}")'
                       f"  # {len(hs)} ligne(s), taille ≈ {size:.1f}")
            if len(hs) > 1:  # repères pour couper la zone (liste, légende…) : haut et bas de chaque ligne
                res += [f"#     y {l['rect'].y0:5.1f}-{l['rect'].y1:5.1f}  {l['text'][:60]}" for l in p["lines"]]
            n += 1
    open(out, "w", encoding="utf8").write("\n".join(res) + "\n")
    print(f"{len(doc)} page(s), {n} zone(s) -> {out}")


if __name__ == "__main__":
    main()
