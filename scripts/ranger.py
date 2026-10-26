"""Range le dossier d'outils d'un jeu une fois la traduction livrée.
Usage : python -X utf8 ranger.py <dossier d'outils> [--essai]

- supprime ce qui est en double ou se recrée : sortie*.pdf, verif*.pdf, journaux, images de relecture (*.png),
  inventaire blocks.txt, polices d'origine extraites (fonts/), dossiers cand/ et vue/, __pycache__ ;
- allège les polices de ff/ : ne garde que les caractères utiles en français (latin, accents, ponctuation,
  symboles courants : ①…, ■, →, ※, （）…). Une police japonaise de plusieurs Mo tombe à quelques dizaines de Ko ;
- retire les ligatures (fi, ti…) pour que le texte du PDF se copie et se cherche correctement.
  À lancer AVANT le build final (la sortie livrée doit être construite avec les polices allégées).
Garde spec.py, les scripts et ff/. Avec --essai : affiche seulement ce qui serait fait."""
import os, shutil, sys

import logging
from fontTools import subset
from fontTools.ttLib import TTFont

logging.getLogger("fontTools").setLevel(logging.ERROR)
# ligatures (fi, ti…) : un seul glyphe pour deux lettres, mal décodé au copier-coller et à la recherche dans le PDF
NO_LIGA = ("liga", "clig", "dlig", "hlig")

KEEP_RANGES = [(0x20, 0x7E), (0xA0, 0x24F), (0x2B0, 0x36F), (0x1E00, 0x1EFF), (0x2000, 0x206F),
               (0x20A0, 0x20CF), (0x2100, 0x218F), (0x2190, 0x22FF), (0x2300, 0x23FF), (0x2460, 0x24FF),
               (0x2500, 0x27BF), (0x2B00, 0x2BFF), (0x3000, 0x303F), (0x30FB, 0x30FB), (0xFF01, 0xFF5E),
               (0xFFFD, 0xFFFD)]
JUNK_FILES = ("blocks.txt", "court.txt", "zones.py", "texte_fr.txt", "relecture.txt", "texte_en.txt",
              "relecture_en.txt")
JUNK_DIRS = ("fonts", "cand", "vue", "__pycache__")


def size(path):
    if os.path.isfile(path):
        return os.path.getsize(path)
    return sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(path) for f in fs)


def mo(n):
    return f"{n / 1e6:.1f} Mo" if n >= 1e5 else f"{n / 1e3:.0f} Ko"


def junk(folder):
    out = []
    for name in os.listdir(folder):
        p = os.path.join(folder, name)
        low = name.lower()
        if os.path.isdir(p):
            if name in JUNK_DIRS:
                out.append(p)
        elif (low.endswith(".png") or name in JUNK_FILES or low.endswith("_journal.txt")
              or (low.endswith(".pdf") and (low.startswith("sortie") or low.startswith("verif")))):
            out.append(p)
    return out


def slim(path, dry):
    before = os.path.getsize(path)
    font = TTFont(path)
    cmap = font.getBestCmap() or {}
    keep = [cp for cp in cmap if any(a <= cp <= b for a, b in KEEP_RANGES)]
    feats = {fr.FeatureTag for t in ("GSUB",) if t in font for fr in font[t].table.FeatureList.FeatureRecord}
    if len(keep) == len(cmap) and not feats & set(NO_LIGA):
        return before, before
    if dry:
        return before, None
    opts = subset.Options()
    gpos = {fr.FeatureTag for fr in font["GPOS"].table.FeatureList.FeatureRecord} if "GPOS" in font else set()
    opts.layout_features = sorted((feats | gpos) - set(NO_LIGA))
    opts.name_IDs = ["*"]
    opts.name_languages = ["*"]
    opts.notdef_outline = True
    opts.glyph_names = True
    opts.hinting = False
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=keep)
    sub.subset(font)
    tmp = path + ".tmp"
    font.save(tmp)
    os.replace(tmp, path)
    return before, os.path.getsize(path)


def main():
    folder = sys.argv[1]
    dry = "--essai" in sys.argv
    if not os.path.isfile(os.path.join(folder, "spec.py")):
        sys.exit(f"ERREUR : {folder} n'est pas un dossier d'outils de jeu (pas de spec.py)")
    total0 = size(folder)
    for p in junk(folder):
        print(f"  supprimé : {os.path.basename(p)} ({mo(size(p))})")
        if not dry:
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    ff = os.path.join(folder, "ff")
    if os.path.isdir(ff):
        for name in sorted(os.listdir(ff)):
            if not name.lower().endswith((".ttf", ".otf")):
                continue
            b, a = slim(os.path.join(ff, name), dry)
            if a is None:
                print(f"  allégée : {name} ({mo(b)} → à alléger)")
            elif a < b:
                print(f"  allégée : {name} ({mo(b)} → {mo(a)})")
    print(f"{os.path.basename(os.path.abspath(folder))} : {mo(total0)} → {mo(size(folder))}"
          + ("  (essai : rien n'a été modifié)" if dry else ""))


if __name__ == "__main__":
    main()
