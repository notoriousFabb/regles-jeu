"""Relecture du texte seul (sans images) : moins cher que les images, et des contrôles que l'œil rate.
Usage : python -X utf8 relecture.py   (dans le dossier d'outils du jeu, après le build)

Écrit texte_fr.txt : pour chaque paragraphe, l'original (« < ») puis le français (« > »), page par page — à lire en
entier pour vérifier sens, oublis, ton et cohérence (bien moins de jetons que des images).
Signale (affiché et dans relecture.txt) :
- mots inconnus du dictionnaire français (fautes de frappe, accords, mots anglais restés) ;
- typographie : espaces doubles, espace avant virgule ou point, guillemets droits, mot anglais courant ;
- vocabulaire (original anglais) : terme du glossaire de la skill présent dans l'original, mais traduction attendue
  absente du français (« lead » sans « entam… ») ;
- longueur : paragraphe français beaucoup plus court (oubli ?) ou plus long (ajout ?) que l'original.
Livret scanné : l'original vient de Z(..., en="texte d'origine") s'il est donné (texte de zones.py).
Spec bilingue (X("fr", "en")) : `LANGUE=en python -X utf8 relecture.py` relit la version anglaise et écrit
texte_en.txt (orthographe anglaise ; contrôles propres au français et au glossaire laissés de côté)."""
import glob, html as htmlmod, os, re, runpy, sys
import pymupdf

HERE = os.getcwd()
LANG = os.environ.get("LANGUE", "fr")
SKILL_REFS = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references"),
              os.path.expanduser("~/.claude/skills/regles-jeu/skills/traduire/references")]
SKILL_REFS += sorted(glob.glob(os.path.expanduser(  # plugin installé depuis GitHub
    "~/.claude/plugins/cache/*/regles-jeu/*/skills/traduire/references")), reverse=True)
EN_COMMON = {"the", "and", "with", "your", "you", "player", "players", "card", "cards", "trick", "tricks", "round",
             "turn", "each", "must", "may", "this", "that", "from", "into", "when", "then", "their", "they", "have"}
AMBIGUOUS = {"game", "games", "score", "scores", "hand", "suit", "deck", "deal", "round", "rank", "set", "run",
             "turn", "play", "value", "draw"}  # sens trop variables pour un contrôle automatique
PRONOUNS = {"la", "le", "les", "lui", "leur", "nous", "vous", "en", "y", "moi", "toi", "t", "il", "elle", "on", "ils",
            "elles", "ce", "je", "tu", "là", "ci"}
EXTRA_OK = {"entameur", "entameurs", "défausse", "défausses", "défausser", "pioche", "pioches", "décompte", "atout",
            "atouts", "pli", "plis", "fournir", "joker", "jokers", "tuile", "tuiles", "meeple", "meeples", "solo",
            "re", "e", "er", "ème", "ci-dessous", "ci-dessus", "ci-après", "c'est-à-dire", "a-t-il", "peut-être",
            "contre-attaque"}


def text_of(h):
    h = re.sub(r"<br\s*/?>|</p>|</div>|</li>", "\n", h)
    h = re.sub(r"<img\b[^>]*>", "[icône]", h)
    h = re.sub(r"<[^>]+>", "", h).replace("{}", "[icône]")
    h = htmlmod.unescape(h).replace(" ", " ")
    return re.sub(r"[ \t]+", " ", re.sub(r"\n\s*", " / ", h)).strip(" /")


def lines_of(src, pno, cache={}):
    if pno not in cache:
        d = src[pno].get_text("rawdict", flags=pymupdf.TEXT_PRESERVE_WHITESPACE)
        cache[pno] = {bi: ["".join(c["c"] for s in l["spans"] for c in s["chars"]) for l in b["lines"]]
                      for bi, b in enumerate(d["blocks"]) if b["type"] == 0}
    return cache[pno]


def orig_text(src, pno, sel):
    lo, out = lines_of(src, pno), []
    for s in sel.split():
        m = re.fullmatch(r"b(\d+)(?::(\d+)(?:-(\d+))?)?", s)
        if not m or int(m.group(1)) not in lo:
            continue
        bl = lo[int(m.group(1))]
        a = int(m.group(2)) if m.group(2) else 0
        z = int(m.group(3)) if m.group(3) else (a if m.group(2) else len(bl) - 1)
        out += bl[a:z + 1]
    return re.sub(r"\s+", " ", " ".join(out)).strip()


def glossary():
    pairs = []
    for d in SKILL_REFS:
        f = os.path.join(d, "glossaire.md")
        if not os.path.isfile(f):
            continue
        for line in open(f, encoding="utf8"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) != 2 or cells[0] in ("Anglais", "---") or cells[0].startswith("-"):
                continue
            en = [re.sub(r"\(.*?\)", "", x).strip().lower() for x in cells[0].split("/")]
            fr = [re.sub(r"\(.*?\)|«|»", "", x).strip().lower() for x in cells[1].split("/")]
            if len(en) == len(fr):
                pairs += [(e, f_) for e, f_ in zip(en, fr) if e and f_ and len(e) > 2]
        break
    return pairs


def stem(fr):
    w = re.findall(r"[a-zà-ÿœ']+", fr)
    w = max(w, key=len) if w else fr
    return w[:max(4, len(w) - 2)] if len(w) > 4 else w


def main():
    spec = runpy.run_path(os.path.join(HERE, "spec.py"))
    src = pymupdf.open(spec["SRC"])
    items = []  # (page, tag, original, français)
    for fl in spec.get("FLOWS", []):
        for p in fl["paras"]:
            items.append((fl["page"], p["src"], orig_text(src, fl["page"], p["src"]), text_of(p["html"])))
    for i, z in enumerate(spec.get("ZONES", []), 1):
        if z.get("html"):
            items.append((z["page"], f"zone {i}", z.get("en", ""), text_of(z["html"])))
    for pno, h in sorted(spec.get("PAGES", {}).items()):
        items.append((pno, "page", "", text_of(h)))
    for n, c in spec.get("CARDS", {}).items():
        for t in (c.values() if isinstance(c, dict) else c):
            items.append((-1, f"carte {n}", "", text_of(t)))

    out, page = [], None
    for pno, tag, en, fr in items:
        if pno != page:
            out.append(f"\n======== page {pno}" if pno >= 0 else "\n======== cartes")
            page = pno
        out.append(f"[{tag}]")
        if en:
            out.append(f"  < {en}")
        out.append(f"  > {fr}")
    texte = f"texte_{LANG}.txt"
    open(texte, "w", encoding="utf8").write("\n".join(out).strip() + "\n")

    report = []
    # orthographe
    try:
        from spellchecker import SpellChecker
        sp = SpellChecker(language=LANG if LANG in ("fr", "en", "de", "es", "it", "pt") else "fr")
        notes = os.path.join(HERE, "NOTES.md")
        own = set(re.findall(r"[a-zà-ÿœ'-]+", open(notes, encoding="utf8").read().lower())) \
            if os.path.isfile(notes) else set()
        words = {}
        for pno, tag, en, fr in items:
            fr = re.sub(r"\S+://\S+|\S+@\S+|www\.\S+", " ", fr)  # adresses web et e-mails
            for w in re.findall(r"(?<![\w-])[a-zà-ÿœ][a-zà-ÿœ'-]*[a-zà-ÿœ](?![\w-])", fr):
                w2 = w.replace("’", "'")
                w2 = re.sub(r"^(?:[ldjmnstc]|qu|jusqu|lorsqu|puisqu)'", "", w2) if LANG == "fr" else \
                    re.sub(r"'(s|t|re|ll|ve|d|m)$", "", w2)
                if len(w2) > 2 and w2 not in EXTRA_OK and w2 not in own:
                    words.setdefault(w2, []).append(f"p{pno} {tag}")
        unknown = set()
        for w in sp.unknown(list(words)):
            parts = [x for x in w.split("-") if x and x not in PRONOUNS]  # ajoutez-la, couleur-valeur…
            if "-" in w and parts and not sp.unknown(parts):
                continue
            unknown.add(w)
        if unknown:
            report.append(f"MOTS INCONNUS du dictionnaire ({len(unknown)}) — faute, accord, ou mot du jeu à ignorer :")
            report += [f"  {w}  ({len(words[w])}× : {', '.join(words[w][:3])})" for w in sorted(unknown)]
    except ImportError:
        report.append("(orthographe non vérifiée : pip install pyspellchecker)")
    # typographie et anglais resté
    typo = []
    for pno, tag, en, fr in items:
        controles = [(r"  +", "espaces doubles"), (r" [,.](?!\d)", "espace avant , ou ."),
                     (r"[a-zà-ÿ][.!?] [a-zà-ÿ]", "minuscule après un point")]
        if LANG == "fr":  # en anglais, le moteur change lui-même " " en “ ”
            controles.append((r'"', "guillemet droit"))
        for pat, msg in controles:
            if re.search(pat, fr):
                typo.append(f"  p{pno} {tag} : {msg} — « {fr[:60]} »")
        eng = [w for w in re.findall(r"[A-Za-z]+", fr) if w.lower() in EN_COMMON]
        if LANG == "fr" and len(eng) >= 2:
            typo.append(f"  p{pno} {tag} : anglais resté ? ({', '.join(eng[:4])}) — « {fr[:60]} »")
    if typo:
        report.append(f"TYPOGRAPHIE / ANGLAIS RESTÉ ({len(typo)}) :")
        report += typo[:30]
    # vocabulaire
    voc = {}
    pairs = sorted((pr for pr in glossary() if pr[0] not in AMBIGUOUS), key=lambda pr: -len(pr[0])) \
        if LANG == "fr" else []  # le glossaire va de l'anglais au français
    masked = [en.lower() for _, _, en, _ in items]  # les expressions longues (« lead color ») passent d'abord
    for e, f_ in pairs:
        st = stem(f_)
        for k, (pno, tag, en, fr) in enumerate(items):
            pat = r"\b" + re.escape(e) + r"s?\b"
            if en and re.search(pat, masked[k]):
                if st not in fr.lower():
                    voc.setdefault((e, f_), []).append(f"p{pno} {tag}")
                masked[k] = re.sub(pat, " ", masked[k])
    if voc:
        report.append(f"VOCABULAIRE (glossaire) — terme d'origine présent, traduction attendue absente ({len(voc)}) :")
        report += [f"  « {e} » → « {f_} » : {', '.join(v[:4])}" + (f" (+{len(v) - 4})" if len(v) > 4 else "")
                   for (e, f_), v in sorted(voc.items())]
    # longueur
    lng = [f"  p{pno} {tag} : {len(fr)} car. pour {len(en)} à l'origine — « {fr[:50]} »"
           for pno, tag, en, fr in items if len(en) > 40 and not 0.7 <= len(fr) / len(en) <= 1.8
           and not re.search(r"[぀-ヿ一-鿿가-힯]", en)]  # pas de sens pour le CJK
    if lng:
        report.append(f"LONGUEUR inhabituelle ({len(lng)}) — oubli ou ajout ?")
        report += lng[:20]
    if not report:
        report.append("Relecture automatique : rien à signaler.")
    report.append(f"\nTexte complet (original et traduction) : {texte} ({sum(len(i[3]) for i in items)} caractères "
                  f"de traduction) — le lire en entier.")
    open("relecture.txt" if LANG == "fr" else f"relecture_{LANG}.txt", "w", encoding="utf8").write(
        "\n".join(report) + "\n")
    print("\n".join(report))


if __name__ == "__main__":
    main()
