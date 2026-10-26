# Règle venue d'une page web

Cas : il n'y a pas de livret PDF de l'éditeur, les règles sont sur une page web (Google Sites, Notion, site de
l'éditeur), et le PDF du dossier de dépôt a été fait par la skill recherche-regles-jeu (`page_pdf.py`, ou
`notion_html.py` pour Notion). `NOTES.md` du jeu le dit (« page web mise en PDF », lien de la page) ; sinon
l'utilisateur donne directement le lien.

**Ne pas recouvrir ce PDF.** On traduit la page elle-même puis on la remet en PDF avec le même script : le
livret français a exactement la présentation du site (mêmes sections dans le même ordre, mêmes images à leur
place, mêmes couleurs et polices ; le navigateur prend une autre police pour les accents absents), sans
réduction de police ni débordement. L'utilisateur veut un calque du site : pas de schéma ajouté, pas de
texte condensé, pas d'image remplacée.

## Étapes
1. **Préparer le dossier** `_outils/<Jeu>/` (sans `preparer.py`, qui ne sert qu'au recouvrement) et y garder
   la page :
   - page ordinaire : relancer `page_pdf.py` de recherche-regles-jeu avec **les mêmes options que pour le PDF
     d'origine** (`--fidele` ou `--xpath "…"`, même `--largeur`) et `--garder "_outils/<Jeu>/web"` ; sortie dans
     le scratchpad (on garde le PDF du dossier de dépôt comme original). Depuis PowerShell (Git Bash abîme
     les arguments qui commencent par `//`).
   - Notion : `notion_html.py "<lien>" "_outils/<Jeu>/web/page_1.html"`.
   Plusieurs URL : un `page_N.html` par page, chacune traduite à part (`page_web.py` sur chaque fichier).
2. **Lister le texte** : `python -X utf8 <skill>/scripts/page_web.py liste web/page_1.html` →
   `web/page_1_segments.txt` (un morceau par ligne, dans l'ordre d'affichage). Le lire en entier.
3. **Traduire** dans `_outils/<Jeu>/traduction.py` : `TITRE = "<Nom du jeu>"` et `FR = [...]`, une chaîne par
   morceau, dans le même ordre, avec le numéro en commentaire (`# 12`). Un mot en gras au milieu d'une
   phrase coupe la phrase en trois morceaux : traduire en gardant ce découpage (déplacer le gras au mot
   français qui correspond, quitte à répartir la phrase autrement entre les morceaux). Menus et textes
   d'interface invisibles dans le PDF (« Passer au contenu principal », noms des autres langues) : les
   recopier tels quels. Liens vers les règles dans d'autres langues : les recopier aussi (sans objet en
   français, mais les retirer changerait la page). Typographie française posée par le script.
4. **Construire** : `page_web.py construire web/page_1.html traduction.py` → `web/page_1_fr.html`, puis
   `page_pdf.py "<sortie>_FR.pdf" "file:///<chemin complet>/web/page_1_fr.html"` avec les mêmes options
   qu'à l'étape 1 (sans `--garder`) et `--titre "<Nom du jeu>"`. Même nombre de pages ou presque : le
   français est plus long, la page s'allonge. Adresse `file:///` : encoder `#` (`%23`) et les espaces (`%20`)
   du chemin, sinon le navigateur coupe l'adresse au `#` (Python : `pathlib.Path(r"…").as_uri()`).
5. **Texte dans les images** (étiquettes de schémas) : reste dans la langue d'origine (compromis à
   signaler). Le réécrire seulement si l'utilisateur le demande (effacer l'étiquette dans une copie de
   l'image, `web/images/`, et réécrire avec la police du site, comme Cycle Tricks).
6. **Relire** : relecteur de texte avec `web/page_1_segments.txt` et `traduction.py` (pas de `spec.py` :
   lui dire de comparer chaque morceau à sa traduction au lieu de lancer `relecture.py`) ; relecteur visuel
   avec le PDF d'origine et le PDF français (`side.py` marche sur deux PDF quelconques).
7. **Livrer** : écrire `NOTES.md` (lien de la page, options de `page_pdf.py`, commandes des étapes 1, 2 et 4,
   vocabulaire, compromis), puis `livrer.py "<outils>" --original "<PDF d'origine>" --pdf "<sortie>_FR.pdf"
   --type "page web"` : original déplacé dans `<Jeu>/`, `<nom>_FR.pdf` copié (mention de langue retirée), ligne
   d'index.

## Page bilingue, version anglaise
- **Page en deux langues** (japonais + anglais sur la même page, billet de blog Game Market) : traduire d'après
  la langue d'origine, l'autre sert de contrôle ; vider les morceaux de la seconde langue (`""`) pour un livret
  français seul, sauf demande contraire.
- **Version anglaise aussi** : un second fichier de traduction (`traduction_en.py`, même découpage), construit
  de la même façon (`web/page_1_en.html` → `<sortie>_EN.pdf`), livré avec `--pdf-en "<sortie>_EN.pdf"`.

## Corriger plus tard
Modifier `traduction.py`, relancer `construire` puis `page_pdf.py` (étape 4). Si le site a changé, refaire
l'étape 1 dans un autre dossier et comparer les deux `_segments.txt` avant de toucher à la traduction.
