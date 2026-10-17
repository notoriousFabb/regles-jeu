# -*- coding: utf-8 -*-
"""Traduction française de <JEU> — à copier en spec.py dans le dossier du jeu.

FLOWS : chaque flux = paragraphes posés de haut en bas sur une page, en gardant les écarts d'origine.
  src   : lignes d'origine remplacées, "b12:2-4 b13" = bloc 12 lignes 2 à 4, puis tout le bloc 13 (voir blocks.txt)
  html  : texte français. <b> gras, <i> italique, <br/> retour forcé, {} = icône suivante (ordre de lecture de l'original)
  options de paragraphe : align="center"|"left" (défaut left), bullet="•"|"1." (puce / numéro, retrait conservé),
          x0 / x1 (limites gauche / droite), size / color / fam / bold / ital (forcer le style), lead (interligne),
          fix=True (garder la ligne de base d'origine : paragraphe qui reprend sous une image), gap (écart en plus),
          wide=False + grow=N (paragraphe centré court : ne pas l'élargir à toute la colonne)
          noicons=True (bouts d'illustration qui touchent les lignes : ne pas les traiter comme icônes)
  options de flux : maxy (ligne de base la plus basse autorisée -> police réduite si dépassement), kmin (réduction
          maximale, défaut 0.84), x0 / x1 (colonne pour les paragraphes centrés), dy (décalage vertical)
CARDS / CARD_PAGES / CARD_STYLE (facultatif) : textes imprimés sur les mini-cartes illustrées (voir en bas).
AVANT_TEXTE (facultatif) : fonction (page, pno, log) appelée après l'effacement du texte d'origine et avant
  le français, pour dessiner dessous : redessiner plus large le rectangle arrondi d'un titre devenu trop long
  (même couleur, retrouvé avec page.get_drawings()), recouvrir un drapeau par un autre…
IGNORE (facultatif) : lignes volontairement non traduites, pour que le rapport « texte non traduit » ne les liste pas."""

# ---------------------------------------------------------------- réglages du jeu (build.py n'a rien à modifier)
SRC = r"CHEMIN/VERS/livret_original.pdf"  # A ADAPTER

# Polices de remplacement, dans le dossier ff/ (une famille courte par police : Av, H…)
CSS = """
@font-face{font-family:Av;src:url(AlegreyaSans-Regular.ttf);}
@font-face{font-family:Av;font-weight:bold;src:url(AlegreyaSans-Bold.ttf);}
@font-face{font-family:Av;font-style:italic;src:url(AlegreyaSans-Italic.ttf);}
@font-face{font-family:Av;font-weight:bold;font-style:italic;src:url(AlegreyaSans-BoldItalic.ttf);}
@font-face{font-family:H;src:url(Handlee-Regular.ttf);}
"""
BODY = "Av"  # famille du texte courant (polices inconnues, marqueurs d'icônes)
# police d'origine (nom sans le préfixe ABCDEF+) -> (famille, gras, italique)
CODE = {"Duper": ("Av", 0, 0), "Duper-Ita": ("Av", 0, 1), "Duper-Bold": ("Av", 1, 0), "Duper-BoldIta": ("Av", 1, 1),
        "ChristmasChalk": ("H", 0, 0)}
SIZE_K = {"Av": 1.0, "H": 1.15}  # facteur de taille par famille (polices.py largeur)
# Colonne de texte {page: (x0, x1)}, "*" = toutes les pages. Facultatif : sinon calculée sur les lignes longues
# de chaque page (le journal l'indique). Sert aux paragraphes centrés et à la largeur des paragraphes.
COLUMNS = {}
IGNORE = {}  # {page: "b0:1 b7"} lignes à ne pas traduire (titre du jeu, calque caché…)

FLOWS = []


def F(page, *paras, **o):
    FLOWS.append(dict(page=page, paras=list(paras), **o))


def P(src, html, **o):
    return dict(src=src, html=html, **o)


def C(src, html, **o):
    return dict(src=src, html=html, align="center", **o)


def L(src, html, bullet="•", **o):
    return dict(src=src, html=html, bullet=bullet, **o)


def T(src, en, fr, **o):
    """Titre de carte : nom d'origine, nom français plus petit entre parenthèses, sur une ligne."""
    return dict(src=src, html=f'<span style="white-space:nowrap">{en} '
                             f'<span style="font-size:0.8em">({fr})</span></span>', **o)


# ---------------------------------------------------------------- exemples (à remplacer)
# F(0, C("b0:1", "Règles", wide=False, grow=10))
# F(3, P("b1", "MISE EN PLACE"),
#   P("b2", "Mélangez les cartes et distribuez-en 11 à chaque joueur."),
#   L("b5:0", "<b>3 joueurs :</b> 13 cartes"),
#   P("b8:1-3", "<b>Pour la première partie :</b> retirez les cartes 16 à 18 (avec le symbole « {} »)."),
#   maxy=234)
# F(8, T("b5", "1 - The Unexpected Challenger", "Le Challenger inattendu"), P("b9", "...", fix=True), maxy=243)

# ---------------------------------------------------------------- mini-cartes (facultatif)
# Le numéro de chaque carte sert d'ancre ; les lignes autour sont rangées par sorte (kinds) d'après leur style.
# Critères possibles : color (0xRRGGBB), font (morceau du nom), maxsize / minsize (taille en points).
# zone = où chercher le texte par rapport au numéro, en tailles de numéro : (x min, x max, y min, y max).
# Exemple Vazerneiros : CARD_STYLE = dict(number=dict(color=0xc7c4b1),
#     kinds={"eff": dict(color=0x000000, font="ChristmasChalk", maxsize=4), "flav": dict(color=0xffe2aa)},
#     zone=(10, 40, 0, 26))
CARD_STYLE = None
CARDS = {}       # {numéro: {"eff": "effet", "flav": "texte d'ambiance"}} (ou un tuple dans l'ordre de kinds)
CARD_PAGES = {}  # {page: [numéros des cartes dont le texte est visible]}
