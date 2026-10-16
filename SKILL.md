---
name: traduction-regles-jeu
description: Traduit en français un livret de règles de jeu de société en PDF depuis n'importe quelle langue (anglais, allemand, espagnol, italien, japonais…) en conservant exactement la mise en page — polices, images, icônes dans le texte, tableaux, positions — et produit un `*_FR.pdf` ; gère aussi les livrets scannés (pages-images sans texte). À utiliser dès que l'utilisateur demande de traduire des règles, un livret, un rulebook ou un PDF de jeu (jeu de plis, jeu de cartes, jeu de société), même s'il ne dit que « traduis-moi ce PDF » ou donne juste un nom de fichier comme `xxx_rulebook.pdf`, `Regles_EN.pdf`, `Spielregel.pdf` ou `Reglas.pdf` ; aussi pour corriger un mot ou une phrase dans une traduction déjà faite de cette façon.
---

# Traduction de livrets de règles (toutes langues → FR, mise en page conservée)

L'utilisateur parle français, joue à des jeux de plis et ne touche pas aux scripts : il veut un PDF français
qui ressemble trait pour trait à l'original. Réponds-lui en français, sans jargon technique inutile.

## Préférences de l'utilisateur
- Ne jamais traduire le titre du jeu ni les noms de variantes.
- Noms de cartes / personnages : dans la langue d'origine, français entre parenthèses dans les titres
  (« The Bride (La Fiancée) ») ; nom d'origine aussi dans le texte. Alphabet non latin : nom imprimé en
  lettres latines s'il existe, sinon nom anglais officiel, sinon romanisation.
- Vocabulaire cohérent entre jeux (pli, entamer, fournir, atout, couleur demandée…) : `references/glossaire.md`.
- Typographie française : « », espaces insécables avant ; : ! ? (posées par le moteur), décimales à virgule.
- Signaler les compromis : police réduite, phrases condensées, texte des illustrations non traduit.

## Environnement
Python 3 avec pymupdf et fonttools (`-X utf8` toujours) ; winrt pour la lecture des scans (voir `ocr.py`).
Organisation de la ludothèque, noms de dossiers et index : `references/dossiers.md` (à lire au premier jeu
d'une session). En bref : dépôt `A traduire/`, outils `_outils/<Jeu>/`, livrets livrés dans `<Jeu>/`, index
`_outils/LISEZMOI.md` (une ligne par jeu, à chercher avec `grep`), détail d'un jeu dans `_outils/<Jeu>/NOTES.md`.
Scripts : `scripts/` à côté de ce fichier ; `preparer.py` copie ceux qu'il faut dans le dossier d'outils.

## Méthode
1. **Préparer** : `python -X utf8 <skill>/scripts/preparer.py "<livret.pdf>" "<Nom du jeu>"`. Il nettoie le
   nom, crée `_outils/<Jeu>/`, détecte texte ou scan, copie scripts et modèle de spec (SRC rempli), fait la
   planche d'aperçu, l'inventaire `blocks.txt`, extrait les polices et signale les accents manquants, devine
   la langue (`references/langues.md`), lit le texte des scans (OCR → `zones.py`) et liste les jeux déjà
   traduits qui ont les mêmes polices. Regarder la planche, annoncer langue, pages, type.
   **Scan** : demander le rendu puis suivre `references/scan.md`. Le reste ci-dessous concerne les livrets à texte.
2. **Polices** (`references/polices.md`) : réutiliser celles d'un jeu proche, sinon choisir des remplaçantes
   (`polices.py glyphes / planche / largeur`), les mettre dans `ff/` et régler en tête de `spec.py` : `CSS`,
   `BODY`, `CODE` (police d'origine → famille, gras, italique), `SIZE_K`, et si besoin `COLUMNS`.
3. **Écrire `spec.py`** d'après `blocks.txt` (le lire en entier ; « [N icône(s)] » = autant de `{}`) : un flux
   `F` par zone de texte, paragraphes `P` / `C` / `L` / `T`, `maxy` = limite basse ; format dans l'en-tête de
   `spec.py`. Le moteur trouve seul la colonne de chaque paragraphe (plusieurs colonnes par page), ancre les
   étapes numérotées posées sur une pastille et évite les coupures « Bleu | 19 », « joueur | A » ; `x1=`,
   `fix=` ou `COLUMNS` ne servent qu'à corriger un cas raté. Lire `references/pieges.md` avant.
   Modifier le spec avec l'outil d'édition (pas `sed` ni un script dans le terminal : les `\` et les
   apostrophes s'y abîment).
4. **Construire** : `python -X utf8 build.py sortie.pdf`. « ERREUR : » = spec à corriger. Journal : « police
   réduite », « DÉBORDE », « N {} … pour M icône(s) », « icône … non replacée », **« TEXTE NON TRADUIT »**
   (traduire, ou `IGNORE` si voulu), **« À VÉRIFIER »** (contrôles automatiques : français qui chevauche une
   image, un autre texte ou du texte d'origine, ou qui sort de la page).
5. **Relire** — confiée à deux agents sur un modèle moins coûteux, lancés **en parallèle** (un seul message,
   deux appels Agent), pour garder la traduction et les décisions sur le modèle principal et les longues
   lectures et images hors de son contexte :
   - `subagent_type: "relecteur-texte"` — message : dossier d'outils et dossier de la skill. Il lance
     `relecture.py`, lit tout `texte_fr.txt` (original et français) et rend sens, oublis, vocabulaire, langue ;
   - `subagent_type: "relecteur-visuel"` — message : dossier d'outils, PDF d'origine, PDF construit, journal,
     endroits à regarder en priorité. Il fait les vues côte à côte (`side.py`), zoome sur les endroits signalés
     et rend les défauts localisés.
   Agents non installés (`agents/` de la skill absent de `~/.claude/agents/`) : `subagent_type:
   "general-purpose"`, `model: "sonnet"`, avec pour message le contenu du fichier `agents/relecteur-….md`
   (sans l'en-tête) suivi des chemins.
   Les rapports sont des propositions : vérifier chaque point (lire le paragraphe, zoomer sur l'endroit)
   avant de corriger ; ne rien corriger « de mémoire ». Corriger, reconstruire, et pour une petite correction
   regarder soi-même la seule page modifiée plutôt que de relancer les agents.
6. **Livrer** : écrire `_outils/<Jeu>/NOTES.md` (langue d'origine, éditeur, type, polices, vocabulaire propre
   au jeu, choix, compromis, astuces du spec), puis
   `python -X utf8 livrer.py "<Ludothèque>/_outils/<Jeu>"` (`--remplacer` seulement si l'utilisateur l'a
   accepté). Il déplace l'original dans `<Jeu>/`, met `SRC` à jour, allège le dossier d'outils (`ranger.py` :
   polices réduites au français et sans ligatures), reconstruit, copie `<nom>_FR.pdf`, met l'index à jour.
   Reporter dans `references/glossaire.md` les seuls termes généraux nouveaux. Résumer à l'utilisateur :
   fichier, choix de vocabulaire, compromis.

## Économiser les jetons
Les images coûtent cher : planches à 80-110 dpi, zooms seulement sur ce qui est signalé ou douteux, pas de
relecture complète après une petite correction. Lire `blocks.txt` ou `zones.py` plutôt que des images pour le
texte. Index : `grep`, pas de lecture intégrale. Ne déléguer à un agent que la relecture (étape 5) : pour les
scripts courts, le coût de démarrage d'un agent dépasse le gain ; la traduction et le spec restent ici.

## Correction d'une traduction existante
Lire `_outils/<Jeu>/NOTES.md`, modifier `spec.py`, relancer `build.py` (ou `scan.py`) dans ce dossier, regarder
la page, puis `livrer.py … --remplacer` (avec l'accord de l'utilisateur pour remplacer le `_FR.pdf`).
