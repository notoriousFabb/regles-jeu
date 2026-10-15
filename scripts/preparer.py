"""Démarre la traduction d'un livret : un seul appel au lieu d'une dizaine d'étapes.
Usage : python -X utf8 preparer.py "<chemin du livret.pdf>" "<Nom du jeu>" [--langue-ocr en-US]

- nettoie le nom du jeu pour Windows (virgules, ! et caractères interdits retirés) ;
- crée <Ludothèque>/_outils/<Jeu>/ (Ludothèque = dossier parent de « A traduire », sinon dossier du PDF) ;
- détecte un livret scanné (pas de texte) et copie les bons scripts + le modèle de spec (SRC déjà rempli) ;
- livret à texte : planche d'aperçu, inventaire blocks.txt, extraction et contrôle des polices, devine la langue ;
- livret scanné : planche d'aperçu et lecture automatique du texte (ocr.py -> zones.py) si la langue est installée ;
- cherche dans l'index et les NOTES.md des jeux déjà traduits ceux qui utilisent les mêmes polices.
Affiche un résumé à lire avant d'écrire le spec."""
import os, re, shutil, subprocess, sys
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
TEXT_SCRIPTS = ["build.py", "commun.py", "controle.py", "dump.py", "polices.py", "side.py", "ranger.py",
                "livrer.py", "relecture.py"]
SCAN_SCRIPTS = ["scan.py", "controle.py", "grille.py", "bandes.py", "side.py", "ranger.py", "livrer.py", "ocr.py",
                "relecture.py"]
RESERVED = {"CON", "PRN", "AUX", "NUL"} | {f"COM{i}" for i in range(1, 10)} | {f"LPT{i}" for i in range(1, 10)}
STOP = {"anglais": "the and of to is you your player card cards each with".split(),
        "allemand": "der die das und ist den mit karten spieler eine".split(),
        "espagnol": "el la los las de que y cartas jugador una".split(),
        "italien": "il la le di che e carte giocatore una gli".split(),
        "français": "le la les des et est carte cartes joueur une".split()}


def clean_name(name):
    n = re.sub(r'[\\/:*?"<>|,!]', " ", name)
    n = re.sub(r"\s+", " ", n).strip().rstrip(". ")
    return n + " (jeu)" if n.upper() in RESERVED else n


def guess_lang(text):
    if len(re.findall(r"[぀-ヿ]", text)) > 20:
        return "japonais"
    if len(re.findall(r"[一-鿿]", text)) > 50:
        return "chinois"
    if len(re.findall(r"[가-힯]", text)) > 20:
        return "coréen"
    words = re.findall(r"[a-zA-ZÀ-ÿ]+", text.lower())
    score = {k: sum(words.count(w) for w in v) for k, v in STOP.items()}
    best = max(score, key=score.get)
    return best if score[best] else "inconnue"


def run(args, cwd):
    r = subprocess.run([sys.executable, "-X", "utf8"] + args, cwd=cwd, capture_output=True, text=True,
                       encoding="utf8")
    return (r.stdout + r.stderr).strip()


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    pdf = os.path.abspath(sys.argv[1])
    if not os.path.isfile(pdf):
        sys.exit(f"ERREUR : livret introuvable : {pdf}")
    jeu = clean_name(sys.argv[2])
    lang_ocr = sys.argv[sys.argv.index("--langue-ocr") + 1] if "--langue-ocr" in sys.argv else "en-US"
    folder = os.path.dirname(pdf)
    ludo = os.path.dirname(folder) if os.path.basename(folder).lower() in ("a traduire", "à traduire") else folder
    tools = os.path.join(ludo, "_outils", jeu)
    if os.path.isfile(os.path.join(tools, "spec.py")):
        sys.exit(f"ERREUR : {tools} contient déjà un spec.py (jeu déjà commencé ?) — rien n'a été modifié")
    os.makedirs(os.path.join(tools, "ff"), exist_ok=True)

    doc = pymupdf.open(pdf)
    text = "".join(p.get_text() for p in doc)
    covered = sum(1 for p in doc for i in p.get_image_info()
                  if (i["bbox"][2] - i["bbox"][0]) * (i["bbox"][3] - i["bbox"][1]) > 0.8 * p.rect.width * p.rect.height)
    scan = len(text.strip()) < 30 * len(doc) and covered >= len(doc)
    rel = os.path.relpath(pdf, tools).replace("\\", "/").split("/")
    src_line = "SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), " + \
               ", ".join(repr(x).replace("'", '"') for x in rel) + ")"

    for f in (SCAN_SCRIPTS if scan else TEXT_SCRIPTS):
        shutil.copy(os.path.join(HERE, f), tools)
    model = open(os.path.join(HERE, "spec_scan_modele.py" if scan else "spec_modele.py"), encoding="utf8").read()
    model = re.sub(r'^SRC = r"CHEMIN/VERS/[^"]*"  # A ADAPTER$', lambda m: "import os\n" + src_line, model,
                   flags=re.M)
    model = model.replace("de <JEU>", "de " + jeu)
    open(os.path.join(tools, "spec.py"), "w", encoding="utf8").write(model)

    print(f"Jeu : {jeu}\nOutils : {tools}\nLivret : {len(doc)} page(s), {doc[0].rect.width:.0f} × "
          f"{doc[0].rect.height:.0f} pt — " + ("SCANNÉ (pages-images)" if scan else "texte"))
    print(run([os.path.join(HERE, "sheet.py"), pdf, "planche", "80"], tools) or "planche*.png : aperçu créé")

    fonts_found = []
    if scan:
        print("\n--- lecture automatique (OCR) ---")
        print(run(["ocr.py", pdf, lang_ocr, "zones.py"], tools))
    else:
        print(f"Langue devinée : {guess_lang(text)}")
        print(run(["dump.py", pdf, "blocks.txt"], tools))
        print("\n--- polices du livret ---")
        print(run(["polices.py", "extraire", pdf, "fonts"], tools))
        fdir = os.path.join(tools, "fonts")
        files = [os.path.join("fonts", f) for f in sorted(os.listdir(fdir))
                 if not f.endswith(".txt")] if os.path.isdir(fdir) else []
        if files:
            out = run(["polices.py", "glyphes"] + files, tools)
            print("\n".join(l for l in out.splitlines() if l.startswith("==") or "français" in l))
        fonts_found = [os.path.splitext(os.path.basename(f))[0] for f in files]

    # jeux déjà traduits qui utilisent les mêmes polices
    notes = []
    base = os.path.join(ludo, "_outils")
    for d in sorted(os.listdir(base)):
        nf = os.path.join(base, d, "NOTES.md")
        if d != jeu and os.path.isfile(nf):
            t = open(nf, encoding="utf8").read().lower()
            hits = [f for f in fonts_found if re.sub(r"[-_ ]?(regular|bold|medium|light|std|pro).*$", "",
                                                     f.lower().replace(" ", "")) in t.replace(" ", "")]
            if hits:
                notes.append(f"  {d} : {', '.join(hits)}")
    if notes:
        print("\nJeux déjà traduits avec les mêmes polices (lire leur NOTES.md, recopier leurs polices ff/) :")
        print("\n".join(notes))
    print("\nÀ faire : regarder planche*.png, " + ("compléter zones.py → spec.py (traduire chaque Z)"
                                                   if scan else "lire blocks.txt, choisir les polices, écrire spec.py")
          + ", puis build/scan, relire, et livrer avec livrer.py.")


if __name__ == "__main__":
    main()
