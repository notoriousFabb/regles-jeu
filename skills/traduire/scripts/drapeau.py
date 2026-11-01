# -*- coding: utf-8 -*-
"""Drapeau français posé à la place du drapeau de la langue d'origine (Royaume-Uni, États-Unis, Japon…), que les
éditeurs impriment souvent près du titre ou du nombre de joueurs pour dire la langue du livret.

Réglage DRAPEAUX de spec.py (build.py et scan.py) : [(page, (x0, y0, x1, y1), "rond" | "rect")], le rectangle étant
celui du drapeau d'origine, ou de son liseré quand un trait l'entoure (rectangle du tracé donné par
page.get_drawings()) : ce liseré est alors retrouvé et redessiné par-dessus. Le drapeau est peint sur l'ancien, en
aplats vectoriels : bleu, blanc, rouge en bandes verticales égales.
"""
import math

import pymupdf

BLEU, BLANC, ROUGE = (0 / 255, 0 / 255, 145 / 255), (1, 1, 1), (225 / 255, 0 / 255, 15 / 255)  # couleurs officielles


def _bande_ronde(cx, cy, r, a, b, n=48):
    """Contour de la partie d'un disque comprise entre les verticales x = a et x = b (polygone fin)."""
    xs = [a + (b - a) * i / n for i in range(n + 1)]
    haut = [(x, cy - math.sqrt(max(r * r - (x - cx) ** 2, 0))) for x in xs]
    bas = [(x, cy + math.sqrt(max(r * r - (x - cx) ** 2, 0))) for x in reversed(xs)]
    return haut + bas


def _ferme(g):
    """Contour fermé (cercle, cadre) : pas un simple trait, comme la diagonale d'un drapeau britannique."""
    items = g["items"]
    if any(it[0] in ("re", "qu") for it in items) or g.get("closePath"):
        return True
    debut, fin = items[0][1], items[-1][-1]
    return len(items) >= 3 and abs(debut.x - fin.x) < 0.5 and abs(debut.y - fin.y) < 0.5


def _lisere(page, rect, tol=2.5):
    """Traits d'origine (liseré) qui font le tour du drapeau : contours fermés dont le rectangle est celui donné."""
    r = pymupdf.Rect(rect)
    return [g for g in page.get_drawings() if g.get("color") and g.get("width") and "s" in g.get("type", "")
            and all(abs(a - b) <= tol for a, b in zip(g["rect"], r)) and _ferme(g)]


def _retracer(page, traits):
    """Redessine les traits d'origine par-dessus le drapeau français (même tracé, couleur et épaisseur)."""
    sh = page.new_shape()
    for g in traits:
        for it in g["items"]:
            if it[0] == "l":
                sh.draw_line(it[1], it[2])
            elif it[0] == "c":
                sh.draw_bezier(it[1], it[2], it[3], it[4])
            elif it[0] == "re":
                sh.draw_rect(it[1])
            elif it[0] == "qu":
                sh.draw_quad(it[1])
        sh.finish(color=g["color"], fill=None, width=g["width"], closePath=g.get("closePath", False),
                  lineCap=max(g.get("lineCap") or (0,)), lineJoin=g.get("lineJoin") or 0,
                  stroke_opacity=g.get("stroke_opacity") or 1)
    sh.commit(overlay=True)


def francais(page, rect, forme="rond", deborde=0.4):
    """Peint le drapeau français dans rect (rond : disque inscrit ; rect : rectangle entier). Un liseré tracé sur
    ce contour (trait d'origine du même rectangle) est couvert jusqu'à son bord extérieur puis redessiné
    par-dessus : rien de l'ancien drapeau ne dépasse entre les deux. deborde : marge en plus (anticrénelage)."""
    traits = _lisere(page, rect)
    if traits:  # jusque sous le liseré, sans dépasser de son bord extérieur
        deborde = max(g["width"] for g in traits) * 0.4
    r = pymupdf.Rect(rect) + (-deborde, -deborde, deborde, deborde)
    sh = page.new_shape()
    if forme == "rond":
        cx, cy, ray = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2, min(r.width, r.height) / 2
        tiers = 2 * ray / 3
        for i, col in enumerate((BLEU, BLANC, ROUGE)):
            a = cx - ray + i * tiers
            sh.draw_polyline(_bande_ronde(cx, cy, ray, a, a + tiers))
            sh.finish(color=None, fill=col, closePath=True)
    else:
        tiers = r.width / 3
        for i, col in enumerate((BLEU, BLANC, ROUGE)):
            sh.draw_rect(pymupdf.Rect(r.x0 + i * tiers, r.y0, r.x0 + (i + 1) * tiers, r.y1))
            sh.finish(color=None, fill=col)
    sh.commit(overlay=True)
    if traits:
        _retracer(page, traits)
    return len(traits)


def poser(doc, drapeaux, log, pages=None):
    """Pose les drapeaux du réglage DRAPEAUX (pages : seulement celles-là, si donné)."""
    for entree in drapeaux:
        pno, rect = entree[0], entree[1]
        forme = entree[2] if len(entree) > 2 else "rond"
        if pages is not None and pno not in pages:
            continue
        if not 0 <= pno < len(doc):
            log.append(f"ERREUR : drapeau de la page {pno} : le livret n'a que {len(doc)} pages")
            continue
        if forme not in ("rond", "rect"):
            log.append(f"ERREUR : drapeau de la page {pno} : forme « {forme} » inconnue (rond ou rect)")
            continue
        n = francais(doc[pno], rect, forme)
        log.append(f"page {pno} : drapeau français posé ({forme}, {[round(v) for v in rect]}"
                   f"{', liseré redessiné' if n else ''})")
