# -*- coding: utf-8 -*-
"""Traduction française de <JEU> — à copier en spec.py dans le dossier du jeu.

FLOWS : chaque flux = paragraphes posés de haut en bas sur une page, en gardant les écarts d'origine.
  src   : lignes anglaises remplacées, "b12:2-4 b13" = bloc 12 lignes 2 à 4, puis tout le bloc 13 (voir blocks.txt)
  html  : texte français. <b> gras, <i> italique, <br/> retour forcé, {} = icône suivante (ordre de lecture anglais)
  options de paragraphe : align="center"|"left" (défaut left), bullet="•"|"1." (puce / numéro, retrait conservé),
          x0 / x1 (limites gauche / droite), size / color / fam / bold / ital (forcer le style), lead (interligne),
          fix=True (garder la ligne de base anglaise : paragraphe qui reprend sous une image), gap (écart en plus),
          wide=False + grow=N (paragraphe centré court : ne pas l'élargir à toute la colonne)
  options de flux : maxy (ligne de base la plus basse autorisée -> police réduite si dépassement), kmin (réduction
          maximale, défaut 0.84), x0 / x1 (colonne pour les paragraphes centrés), dy (décalage vertical)
CARDS / CARD_PAGES (facultatif) : textes imprimés sur les mini-cartes illustrées, voir build.card_flows."""
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
    """Titre de carte : nom anglais, nom français plus petit entre parenthèses, sur une ligne."""
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

CARDS = {}       # {numéro: (texte d'ambiance, effet)}
CARD_PAGES = {}  # {page: [numéros des cartes dont le texte est visible]}
