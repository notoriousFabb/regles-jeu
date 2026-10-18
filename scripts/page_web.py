# -*- coding: utf-8 -*-
"""Règle venue d'une page web (Google Sites, Notion, site d'éditeur) : traduire la page elle-même, puis la
remettre en PDF avec le même script que l'original, au lieu de recouvrir le PDF imprimé.

    python -X utf8 page_web.py liste web/page_1.html
        -> web/page_1_segments.txt : un morceau de texte par ligne, numéroté, dans l'ordre d'affichage
           (« 12  b  'texte' » : numéro, balise, texte d'origine ; un mot en gras au milieu d'une phrase
           coupe la phrase en trois morceaux)
    python -X utf8 page_web.py construire web/page_1.html traduction.py
        -> web/page_1_fr.html : chaque morceau remplacé par FR[n] de traduction.py (même nombre, même ordre),
           typographie française posée (insécables avant ; : ! ?, dans « », apostrophe courbe)

traduction.py : FR = ["…", "…", …] (un texte par morceau, "" pour vider un morceau) et, facultatif,
TITRE = "…" (titre de l'onglet et du PDF). Les morceaux de ponctuation seule de l'original (。 、 ！ « 」…)
ne sont pas listés : ils sont convertis d'office."""
import importlib.util, os, re, sys
import lxml.html

LETTRE = re.compile(r"[^\W\d_]")
NBSP = " "
PONCTUATION = {"。": ".", "、": ",", "，": ",", "！": "!", "？": "?", "：": ":", "；": ";", "（": "(", "）": ")",
               "「": "«", "」": "»", "『": "«", "』": "»", "～": "~"}  # ・ et espace idéographique gardés (séparateurs)
SAUTER = {"script", "style", "noscript", "template", "svg"}


def morceaux(corps):
    """(élément, "text" | "tail", texte) dans l'ordre d'affichage : texte de l'élément, enfants, puis la suite."""
    out = []

    def visite(el):
        if not isinstance(el.tag, str) or el.tag in SAUTER:
            return
        out.append((el, "text", el.text))
        for enfant in el:
            visite(enfant)
            out.append((enfant, "tail", enfant.tail))
    visite(corps)
    return [m for m in out if m[2] and m[2].strip()]


def typo(t):
    t = re.sub(r"(?<=\w)'(?=\w)", "’", t)
    t = re.sub(r"«\s*", "«" + NBSP, t)
    t = re.sub(r"\s*»", NBSP + "»", t)
    return re.sub(r"\s+([;:!?])", NBSP + r"\1", t)


def lire(page):
    doc = lxml.html.parse(page).getroot()
    corps = doc.find("body")
    if corps is None:
        sys.exit(f"ERREUR : pas de <body> dans {page}")
    return doc, morceaux(corps)


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("liste", "construire"):
        sys.exit(__doc__)
    page = sys.argv[2]
    base = os.path.splitext(page)[0]
    doc, ms = lire(page)
    texte = [m for m in ms if LETTRE.search(m[2])]
    if sys.argv[1] == "liste":
        with open(base + "_segments.txt", "w", encoding="utf-8") as f:
            for i, (el, attr, t) in enumerate(texte):
                f.write(f"{i}\t{el.tag if attr == 'text' else el.getparent().tag}\t{t.strip()!r}\n")
        print(f"{len(texte)} morceaux -> {base}_segments.txt")
        return
    if len(sys.argv) < 4:
        sys.exit("ERREUR : construire <page.html> <traduction.py>")
    spec = importlib.util.spec_from_file_location("traduction", sys.argv[3])
    tr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tr)
    if len(tr.FR) != len(texte):
        sys.exit(f"ERREUR : {len(tr.FR)} traductions dans FR pour {len(texte)} morceaux (relancer « liste »)")
    for (el, attr, t), fr in zip(texte, tr.FR):
        avant, apres = re.match(r"^\s*", t).group(), re.search(r"\s*$", t).group()
        setattr(el, attr, avant + typo(fr) + apres if fr else "")
    for el, attr, t in ms:  # ponctuation seule (。entre deux balises…)
        if not LETTRE.search(t):
            setattr(el, attr, "".join(PONCTUATION.get(c, c) for c in t))
    doc.set("lang", "fr")
    titre = getattr(tr, "TITRE", None)
    if titre:
        tete = doc.find("head")
        t = tete.find("title") if tete is not None else None
        if t is None and tete is not None:
            t = lxml.html.Element("title")
            tete.append(t)
        if t is not None:
            t.text = titre
    sortie = base + "_fr.html"
    with open(sortie, "w", encoding="utf-8") as f:
        f.write("<!doctype html>" + lxml.html.tostring(doc, encoding="unicode"))
    print(f"{len(texte)} morceaux traduits -> {sortie}")


if __name__ == "__main__":
    main()
