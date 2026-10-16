# -*- coding: utf-8 -*-
"""Traduction française d'un livret SCANNÉ de <JEU> — à copier en spec.py dans _outils/<Jeu>/ (moteur : scan.py).

MODE "recouvrir" : ZONES = rectangles de texte de l'image ; chacun est masqué par la couleur du fond mesurée tout
    autour, puis le français est posé dedans (police réduite automatiquement jusqu'à kmin pour tenir).
    Coordonnées en points PDF, origine en haut à gauche, lues sur les images de grille.py.
    Z(page, (x0, y0, x1, y1), html, **o) — options : size (taille de départ, défaut 7), kmin (réduction maximale,
        défaut 0.5), align ("left", "center", "right", "justify"), color ("#rrggbb", défaut noir), fam / bold / ital,
        lead (interligne en multiple de la taille, défaut 1.15), pad (marge intérieure, défaut 0.5),
        bg ("auto" = couleur du fond autour de la zone, "#rrggbb", None = ne pas masquer),
        en ("texte d'origine", repris de zones.py : sert à relecture.py)
    M(page, (x0, y0, x1, y1), bg="auto") — masque seul (effacer un texte sans le remplacer)
MODE "cote" : PAGES = {page: html} ; chaque page d'origine à gauche, sa traduction complète à droite.
    SIDE_WIDTH (largeur de la colonne française en multiple de la page, défaut 1.0), SIDE_STYLE (style du texte),
    SIDE_MARGIN, SIDE_GAP. Si la traduction est trop longue, elle continue sur une page de plus.
html : <b>, <i>, <br/>, <p>, <h3>, <ul><li>… ; la typographie française (espaces insécables) est posée par scan.py."""

SRC = r"CHEMIN/VERS/livret_scanne.pdf"  # A ADAPTER
MODE = "recouvrir"  # ou "cote"

CSS = """
@font-face{font-family:Av;src:url(AlegreyaSans-Regular.ttf);}
@font-face{font-family:Av;font-weight:bold;src:url(AlegreyaSans-Bold.ttf);}
@font-face{font-family:Av;font-style:italic;src:url(AlegreyaSans-Italic.ttf);}
"""
BODY = "Av"

ZONES = []


def Z(page, rect, html, **o):
    ZONES.append(dict(page=page, rect=rect, html=html, **o))


def M(page, rect, bg="auto"):
    ZONES.append(dict(page=page, rect=rect, html=None, bg=bg))


PAGES = {}
SIDE_WIDTH = 1.0
SIDE_STYLE = "font-family:Av;font-size:8pt;line-height:1.2;"

# ---------------------------------------------------------------- exemples (à remplacer)
# Z(0, (8, 78, 192, 96), "• Shinobi Blade est un jeu de cartes pour 3 à 5 joueurs, de la famille des "
#                        "« jeux de plis ». …", size=6)
# Z(0, (22, 70, 75, 78), "<b>Aperçu du jeu</b>", size=8, bg="#ffffff")
# PAGES[0] = "<h3>Aperçu du jeu</h3><p>…</p><h3>Mise en place</h3><ul><li>…</li></ul>"
