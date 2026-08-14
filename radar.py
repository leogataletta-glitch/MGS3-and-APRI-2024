"""Diagramme radar pour les scores de résilience (échelle fixe 0-10).

Rendu en SVG pur, sans dépendance : le tableau de bord tourne déjà sans
bibliothèque graphique, et l'échelle 0-10 doit rester identique d'un radar à
l'autre pour que deux profils soient comparables à l'œil.

Palette catégorielle validée (validate_palette.js, mode clair, surface #ffffff) :
bleu #2a78d6, orange #eb6834, aqua #1baf7a — séparation CVD la plus faible
ΔE 9,2 (deutan), plancher vision normale ΔE 27,6. L'aqua passe sous 3:1 face à
la surface : la légende et le tableau qui accompagnent le radar tiennent lieu de
relief, conformément à la règle.
"""

import math

SURFACE = '#ffffff'
INK = '#0b0b0b'
INK2 = '#52514e'
INK3 = '#898781'
GRID = '#d8d7d0'
GRID_FAINT = '#e7e6e0'

SERIES = ['#2a78d6', '#eb6834', '#1baf7a']

VMAX = 10.0
ANNEAUX = (2, 4, 6, 8, 10)


def _wrap(texte, largeur=16):
    mots, lignes, cur = str(texte).split(), [], ''
    for m in mots:
        essai = (cur + ' ' + m).strip()
        if len(essai) <= largeur or not cur:
            cur = essai
        else:
            lignes.append(cur)
            cur = m
    if cur:
        lignes.append(cur)
    return lignes[:3]


def _fmt(x):
    return f'{x:.1f}'.replace('.', ',')


def render_radar_svg(axes, series, taille=620, titre_valeurs=True,
                     largeur=None, hauteur=None):
    """axes   : [libellé, ...] — un par sommet, dans l'ordre horaire.
    series : [(nom, [valeur|None, ...], couleur|None), ...] — 3 séries au plus.
    Les valeurs sont des scores de 0 à 10 ; None = non mesuré, le sommet est
    alors sauté et le contour passe en pointillés à cet endroit.
    """
    axes = list(axes)
    n = len(axes)
    if n < 3 or not series:
        return '<svg width="0" height="0"></svg>'

    # Les libellés d'axe est/ouest sont longs : la toile est plus large que
    # haute, sinon ils sortent du cadre.
    W = largeur or int(taille * 1.28)
    H = hauteur or taille
    cx, cy = W / 2, H / 2
    R = min(W / 2 - 132, H / 2 - 62)         # marge pour les libellés d'axe
    ang = [-math.pi / 2 + 2 * math.pi * i / n for i in range(n)]

    def pt(i, v):
        r = R * max(0.0, min(v, VMAX)) / VMAX
        return cx + r * math.cos(ang[i]), cy + r * math.sin(ang[i])

    parts = []

    # ---- toile : anneaux + rayons ------------------------------------
    for a in ANNEAUX:
        r = R * a / VMAX
        poly = ' '.join(f'{cx + r * math.cos(t):.1f},{cy + r * math.sin(t):.1f}'
                        for t in ang)
        tirets = '' if a == ANNEAUX[-1] else ' stroke-dasharray="4 4"'
        col = GRID if a == ANNEAUX[-1] else GRID_FAINT
        parts.append(f'<polygon points="{poly}" fill="none" stroke="{col}" '
                     f'stroke-width="1"{tirets}/>')
    for i in range(n):
        x, y = pt(i, VMAX)
        parts.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x:.1f}" y2="{y:.1f}" '
                     f'stroke="{GRID_FAINT}" stroke-width="1"/>')

    # ---- graduations sur l'axe du haut -------------------------------
    for a in ANNEAUX:
        r = R * a / VMAX
        parts.append(f'<text class="rg" x="{cx + 5:.1f}" y="{cy - r + 4:.1f}">{a}</text>')
    parts.append(f'<text class="rg" x="{cx + 5:.1f}" y="{cy + 4:.1f}">0</text>')

    # ---- séries -------------------------------------------------------
    for k, (nom, vals, coul) in enumerate(series[:3]):
        col = coul or SERIES[k % len(SERIES)]
        pts = [(i, v) for i, v in enumerate(vals) if v is not None]
        if len(pts) < 3:
            continue
        poly = ' '.join(f'{pt(i, v)[0]:.1f},{pt(i, v)[1]:.1f}' for i, v in pts)
        complet = len(pts) == n
        parts.append(
            f'<polygon points="{poly}" fill="{col}" fill-opacity="0.16" '
            f'stroke="{col}" stroke-width="2" stroke-linejoin="round"'
            + ('' if complet else ' stroke-dasharray="7 4"') + '/>')
        for i, v in pts:
            x, y = pt(i, v)
            parts.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{col}" '
                f'stroke="{SURFACE}" stroke-width="2">'
                f'<title>{nom} — {axes[i]} : {_fmt(v)} / 10</title></circle>')

    # ---- valeurs écrites : seulement quand il n'y a qu'une série ------
    if titre_valeurs and len(series) == 1:
        nom, vals, coul = series[0]
        for i, v in enumerate(vals):
            if v is None:
                continue
            x, y = pt(i, v)
            dx = 13 * math.cos(ang[i])
            dy = 13 * math.sin(ang[i]) + 4
            parts.append(f'<text class="rv" x="{x + dx:.1f}" y="{y + dy:.1f}">'
                         f'{_fmt(v)}</text>')

    # ---- libellés d'axe ------------------------------------------------
    for i, lab in enumerate(axes):
        x, y = pt(i, VMAX)
        ux, uy = math.cos(ang[i]), math.sin(ang[i])
        x += 16 * ux
        y += 16 * uy
        anchor = 'middle' if abs(ux) < 0.34 else ('start' if ux > 0 else 'end')
        lignes = _wrap(lab)
        y0 = y - (len(lignes) - 1) * 6.5 + (5 if uy > 0.4 else 0)
        for j, ligne in enumerate(lignes):
            parts.append(f'<text class="ra" x="{x:.1f}" y="{y0 + j * 13:.1f}" '
                         f'text-anchor="{anchor}">{ligne}</text>')

    return f"""<svg viewBox="0 0 {W} {H}" width="100%"
     style="max-width:{W}px;display:block;margin:0 auto" role="img"
     aria-label="Profil de résilience par dimension, scores de 0 à 10">
  <style>
    .ra{{font:12px system-ui,-apple-system,"Segoe UI",sans-serif;fill:{INK2}}}
    .rg{{font:11px system-ui,-apple-system,"Segoe UI",sans-serif;fill:{INK3};
        font-variant-numeric:tabular-nums}}
    .rv{{font:600 12.5px system-ui,-apple-system,"Segoe UI",sans-serif;fill:{INK};
        text-anchor:middle;font-variant-numeric:tabular-nums;
        paint-order:stroke;stroke:{SURFACE};stroke-width:3.5}}
  </style>
  {''.join(parts)}
</svg>"""


def legende_html(series):
    """Légende : toujours présente dès deux séries, jamais la couleur seule."""
    morceaux = []
    for k, (nom, _vals, coul) in enumerate(series[:3]):
        col = coul or SERIES[k % len(SERIES)]
        morceaux.append(
            f'<span style="display:inline-flex;align-items:center;gap:7px;'
            f'margin-right:20px">'
            f'<span style="width:13px;height:13px;border-radius:3px;background:{col};'
            f'opacity:.9;box-shadow:inset 0 0 0 1px rgba(0,0,0,.15)"></span>'
            f'<span style="font-size:13px;color:{INK2}">{nom}</span></span>')
    return ''.join(morceaux)
