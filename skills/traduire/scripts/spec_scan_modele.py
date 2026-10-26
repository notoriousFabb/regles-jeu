# -*- coding: utf-8 -*-
"""Traduction française d'un livret SCANNÉ de <JEU> — à copier en spec.py dans _outils/<Jeu>/ (moteur : scan.py).

MODE "recouvrir" : ZONES = rectangles de texte de l'image ; chacun est masqué par la couleur du fond mesurée tout
    autour, puis le français est posé dedans (police réduite automatiquement jusqu'à kmin pour tenir).
    Coordonnées en points PDF, origine en haut à gauche, lues sur les images de grille.py.
    Z(page, (x0, y0, x1, y1), html, **o) — options : size (taille de départ, défaut 7), kmin (réduction maximale,
        défaut 0.5), align ("left", "center", "right", "justify"), color ("#rrggbb", défaut noir), fam / bold / ital,
        lead (interligne en multiple de la taille, défaut 1.15), pad (marge intérieure, défaut 0.5 ; zone d'une
        seule ligne : lead 1.0 et pad -0.6 d'office),
        bg ("auto" = couleur du fond autour de la zone, "dominant" = couleur la plus fréquente DANS la zone, pour
            des encadrés semi-transparents sur fond texturé, "#rrggbb", None = ne pas masquer ; BG = défaut de toutes
            les zones),
        en ("texte d'origine", repris de zones.py : sert à relecture.py),
        rot (90, -90 ou 180 : texte tourné, pour une étiquette verticale ; la zone reste celle de l'image)
    M(page, (x0, y0, x1, y1), bg="auto") — masque seul (effacer un texte sans le remplacer)
    VECTEUR = True : livret dont les lettres sont des tracés vectoriels (texte vectorisé, pas une image) : les
        tracés de lettres de chaque zone sont supprimés au lieu d'être masqués par un aplat, le fond d'origine
        (dégradé, illustration) reste intact sous le français. Une zone avec bg="#rrggbb" reçoit en plus un aplat.
        VECTEUR_MARGE (défaut 1.2 pt) : marge autour de la zone ; VECTEUR_LETTRE (défaut 12 pt) : taille
        maximale d'un tracé pris pour une lettre (au-delà, morceau d'illustration gardé).
MODE "cote" : PAGES = {page: html} ; chaque page d'origine à gauche, sa traduction complète à droite.
    SIDE_WIDTH (largeur de la colonne française en multiple de la page, défaut 1.0), SIDE_STYLE (style du texte),
    SIDE_MARGIN, SIDE_GAP. Si la traduction est trop longue, elle continue sur une page de plus.
html : <b>, <i>, <br/>, <p>, <h3>, <ul><li>… ; la typographie française (espaces insécables) est posée par scan.py.
VERSION ANGLAISE (facultatif) : écrire chaque texte X("français", "english") ; `LANGUE=en python -X utf8 scan.py
  sortie_en.pdf` construit l'anglais (PowerShell : $env:LANGUE="en"), livrer.py livre alors aussi <nom>_EN.pdf."""

import os
SRC = r"CHEMIN/VERS/livret_scanne.pdf"  # A ADAPTER
MODE = "recouvrir"  # ou "cote"
BG = "auto"  # fond par défaut des masques : "auto" (autour de la zone) ou "dominant" (dans la zone)
LANGUE = os.environ.get("LANGUE", "fr")  # fr, ou en pour la version anglaise


def X(fr, en):
    """Texte dans la langue construite (spec bilingue)."""
    return fr if LANGUE == "fr" else en

CSS = """
@font-face{font-family:Av;src:url(AlegreyaSans-Regular.ttf);}
@font-face{font-family:Av;font-weight:bold;src:url(AlegreyaSans-Bold.ttf);}
@font-face{font-family:Av;font-style:italic;src:url(AlegreyaSans-Italic.ttf);}
@font-face{font-family:Sym;src:url(seguisym.ttf);}
"""
BODY = "Av"

ZONES = []


def Z(page, rect, html, **o):
    ZONES.append(dict(page=page, rect=rect, html=html, **o))


def M(page, rect, bg="auto"):
    ZONES.append(dict(page=page, rect=rect, html=None, bg=bg))


# ---------------------------------------------------------------- aides (supprimer celles qui ne servent pas)
def S(c, color=None):
    """①…⑳, ❶…❿, ◆, ★ : Segoe UI Symbol (copier C:/Windows/Fonts/seguisym.ttf dans ff/)."""
    return f'<span style="font-family:Sym;{f"color:{color};" if color else ""}">{c}</span>'


def I(name, h=7):
    """Icône dans le texte : ff/<name>.png, découpée dans l'original avec icone.py."""
    return f'<img src="{name}.png" style="height:{h}pt"/>'


def BANNER(page, rect, text, fam=BODY, size=9, bg="#000000", color="#ffffff", indent=6):
    """Bandeau de titre (texte clair sur aplat) ; le rectangle peut dépasser l'original pour l'élargir."""
    M(page, rect, bg=bg)
    Z(page, (rect[0] + indent,) + tuple(rect[1:]), text, fam=fam, size=size, color=color, bg=None)


def PILL(page, rect, text, bg, size=7.5, color="#ffffff"):
    """Titre sur pastille arrondie : garder le rectangle à l'intérieur des bouts arrondis."""
    Z(page, rect, f"<b>{text}</b>", size=size, color=color, bg=bg, align="center")


PAGES = {}
SIDE_WIDTH = 1.0
SIDE_STYLE = "font-family:Av;font-size:8pt;line-height:1.2;"

# ---------------------------------------------------------------- exemples (à remplacer)
# Z(0, (8, 78, 192, 96), "• Shinobi Blade est un jeu de cartes pour 3 à 5 joueurs, de la famille des "
#                        "« jeux de plis ». …", size=6)
# Z(0, (22, 70, 75, 78), "<b>Aperçu du jeu</b>", size=8, bg="#ffffff")
# PAGES[0] = "<h3>Aperçu du jeu</h3><p>…</p><h3>Mise en place</h3><ul><li>…</li></ul>"
