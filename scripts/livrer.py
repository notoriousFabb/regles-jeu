"""Livre une traduction terminée : un seul appel pour toutes les étapes de rangement.
Usage : python -X utf8 livrer.py "<Ludothèque>/_outils/<Jeu>" [--langue X] [--editeur Y] [--remplacer]

1. crée <Ludothèque>/<Jeu>/ et y déplace le livret d'origine (s'il est encore dans « A traduire ») ;
2. fait pointer SRC de spec.py sur son nouvel emplacement ;
3. range et allège le dossier d'outils (ranger.py), reconstruit avec les polices allégées (build.py ou scan.py) ;
4. copie la sortie en <Jeu>/<nom>_FR.pdf (« Jeu_EN.pdf » → « Jeu_FR.pdf ») puis range de nouveau ;
5. ajoute ou met à jour la ligne du jeu dans l'index _outils/LISEZMOI.md (langue et éditeur : options, sinon lus
   dans NOTES.md) et signale un NOTES.md manquant.
N'écrase jamais un fichier existant dans le dossier du jeu sans --remplacer."""
import ast, datetime, os, re, shutil, subprocess, sys

HEADER = """# Index des livrets traduits (skill traduction-regles-jeu)

Une ligne par jeu. Le détail de chaque jeu (polices, vocabulaire, choix, particularités) est dans
`_outils/<Jeu>/NOTES.md` ; les livrets (original et `_FR.pdf`) sont dans `<Jeu>/`.
Pour reconstruire : `python -X utf8 build.py sortie.pdf` (Type « texte ») ou `scan.py` (Type « scan ») dans
`_outils/<Jeu>/`, puis copier vers `<Jeu>/<nom>_FR.pdf` et lancer `ranger.py`.
Chercher un jeu proche par éditeur ou par police : `grep -i "<éditeur ou police>" _outils/LISEZMOI.md`.

| Jeu | Langue | Éditeur | Type | Polices de remplacement | Date |
|---|---|---|---|---|---|
"""
LANG_SUFFIX = re.compile(r"[ _\-.](EN|ENG|JP|JA|JPN|DE|GER|ES|SP|IT|CN|ZH|KR|KO|PT|NL|PL|RU)$", re.I)


def fail(msg):
    sys.exit(f"ERREUR : {msg}")


def opt(name):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else None


def run(args, cwd):
    r = subprocess.run([sys.executable, "-X", "utf8"] + args, cwd=cwd, capture_output=True, text=True,
                       encoding="utf8")
    return r.returncode, (r.stdout + r.stderr).strip()


def read_src(spec_path):
    """Valeur de SRC (chemin absolu) et lignes de l'affectation dans spec.py."""
    code = open(spec_path, encoding="utf8").read()
    for node in ast.parse(code).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "SRC" for t in node.targets):
            ns = {"__file__": spec_path}
            exec("import os\n" + "\n".join(code.splitlines()[:node.end_lineno]), ns)
            return os.path.abspath(ns["SRC"]), node.lineno, node.end_lineno
    fail(f"SRC introuvable dans {spec_path}")


def font_families(ff):
    from fontTools.ttLib import TTFont
    names = []
    for f in sorted(os.listdir(ff)) if os.path.isdir(ff) else []:
        if f.lower().endswith((".ttf", ".otf")):
            try:
                n = TTFont(os.path.join(ff, f))["name"].getBestFamilyName()
            except Exception:
                n = os.path.splitext(f)[0]
            n = re.sub(r"\s+(Regular|Bold|Italic|Medium|Light|Black|ExtraBold|SemiBold|Narrow)\b.*$", "", n)
            if n not in names:
                names.append(n)
    return ", ".join(names)


def from_notes(notes, key):
    if not os.path.isfile(notes):
        return None
    m = re.search(key + r"\s*:\s*([^.\n(]+)", open(notes, encoding="utf8").read())
    return m.group(1).strip() if m else None


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    tools = os.path.abspath(sys.argv[1])
    spec_path = os.path.join(tools, "spec.py")
    if not os.path.isfile(spec_path):
        fail(f"{tools} n'est pas un dossier d'outils (pas de spec.py)")
    jeu = os.path.basename(tools)
    ludo = os.path.dirname(os.path.dirname(tools))
    target = os.path.join(ludo, jeu)
    scan = os.path.isfile(os.path.join(tools, "scan.py")) and not os.path.isfile(os.path.join(tools, "build.py"))
    engine = "scan.py" if scan else "build.py"
    replace = "--remplacer" in sys.argv

    src, l0, l1 = read_src(spec_path)
    if not os.path.isfile(src):
        fail(f"livret d'origine introuvable : {src}")
    stem = os.path.splitext(os.path.basename(src))[0]
    fr_name = (LANG_SUFFIX.sub("", stem) or stem) + "_FR.pdf"
    fr_path = os.path.join(target, fr_name)
    if os.path.exists(fr_path) and not replace:
        fail(f"{fr_path} existe déjà — relancer avec --remplacer pour l'écraser")

    # 1-2. dossier du jeu, livret d'origine, SRC
    os.makedirs(target, exist_ok=True)
    dest = os.path.join(target, os.path.basename(src))
    if os.path.normcase(os.path.dirname(src)) != os.path.normcase(target):
        if os.path.exists(dest) and not replace:
            fail(f"{dest} existe déjà — relancer avec --remplacer")
        shutil.move(src, dest)
        print(f"livret d'origine déplacé -> {dest}")
    rel = os.path.relpath(dest, tools).replace("\\", "/").split("/")
    new = "SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), " + \
          ", ".join('"' + x + '"' for x in rel) + ")"
    lines = open(spec_path, encoding="utf8").read().splitlines()
    lines[l0 - 1:l1] = [new]
    open(spec_path, "w", encoding="utf8").write("\n".join(lines) + "\n")

    # 3-4. ranger, reconstruire, copier, ranger
    print(run(["ranger.py", tools], tools)[1].splitlines()[-1])
    code, out = run([engine, "sortie.pdf"], tools)
    if code or "ERREUR" in out:
        fail("la reconstruction a échoué :\n" + out[-2000:])
    tail = out[out.find("À VÉRIFIER"):] if "À VÉRIFIER" in out else ""
    shutil.copy(os.path.join(tools, "sortie.pdf"), fr_path)
    print(f"traduction -> {fr_path}")
    print(run(["ranger.py", tools], tools)[1].splitlines()[-1])

    # 5. index
    notes = os.path.join(tools, "NOTES.md")
    langue = opt("--langue") or from_notes(notes, "Langue d'origine") or "?"
    editeur = opt("--editeur") or from_notes(notes, "Éditeur") or "?"
    row = (f"| {jeu} | {langue} | {editeur} | {'scan' if scan else 'texte'} | "
           f"{font_families(os.path.join(tools, 'ff'))} | {datetime.date.today().isoformat()} |")
    index = os.path.join(ludo, "_outils", "LISEZMOI.md")
    text = open(index, encoding="utf8").read() if os.path.isfile(index) else HEADER
    rows = [l for l in text.splitlines() if l.startswith(f"| {jeu} |")]
    text = text.replace(rows[0], row) if rows else text.rstrip("\n") + "\n" + row + "\n"
    open(index, "w", encoding="utf8").write(text)
    print(f"index : {row}")
    if not os.path.isfile(notes):
        print(f"ATTENTION : {notes} manque — l'écrire (langue, éditeur, polices, vocabulaire, choix, compromis)")
    if tail:
        print("\n" + tail)


if __name__ == "__main__":
    main()
