"""Rendu de la carte des sections communales, colorée par seuils.

Deux modes, choisis automatiquement :

1. **Limites administratives** — si le fichier `data/sections_communales.geojson`
   existe, chaque section est dessinée avec son vrai contour officiel.
2. **Disques positionnés géographiquement** (repli par défaut) — chaque section
   est un disque placé au centre de la zone enquêtée. Utilisé tant qu'on n'a pas
   de fichier de limites : les points GPS des ménages suivent les routes et ne
   permettent pas de reconstituer un territoire.
"""
import json
import math
import os
import unicodedata

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CENTROIDS_PATH = os.path.join(APP_DIR, 'data', 'map_centroids.json')
GEOJSON_PATH = os.path.join(APP_DIR, 'data', 'sections_communales.geojson')

SECTIONS = ['Anse à Drick', 'Barbois', 'Dumont', 'Débouchette', 'Mouline',
            'Quentin', 'Beaulieu', 'Blactote', 'Dalmette', 'Trichet']

# rampe séquentielle bleue (une seule teinte, validée) : fond + encre du texte
RAMP = [('#86b6ef', '#0b0b0b'), ('#3987e5', '#0b0b0b'),
        ('#256abf', '#ffffff'), ('#104281', '#ffffff')]

INK, INK2, MUTED, SURFACE = '#0b0b0b', '#52514e', '#898781', '#fcfcfb'


# --------------------------------------------------------------------------
def nice_thresholds(vals):
    """4 classes aux bornes rondes : le minimum tombe en classe 1, le maximum
    en classe 4."""
    vals = [v for v in vals if v is not None]
    if not vals:
        return [25, 50, 75]
    lo, hi = min(vals), max(vals)
    if hi - lo < 0.05:            # toutes les sections au même niveau
        return [round(lo + 0.1, 1), round(lo + 0.2, 1), round(lo + 0.3, 1)]
    best = None
    for step in (1, 2, 2.5, 5, 10, 15, 20, 25):
        base = (lo // step) * step
        if base + 3 * step <= hi and base + step > lo:
            best = [base + step, base + 2 * step, base + 3 * step]
    if best is None:
        q = sorted(vals)
        best = [q[len(q) // 4], q[len(q) // 2], q[3 * len(q) // 4]]
        if len(set(best)) < 3:
            best = [lo + (hi - lo) * f for f in (0.25, 0.5, 0.75)]
    return [round(b, 1) for b in best]


def fmt(x):
    """Bornes de seuil : entier si possible, sinon une décimale."""
    return (f'{x:.0f}' if float(x).is_integer() else f'{x:.1f}').replace('.', ',')


def fmt_val(x):
    """Valeurs affichées sur la carte : toujours une décimale, pour l'homogénéité."""
    return f'{x:.1f}'.replace('.', ',')


def bin_of(v, T):
    if v < T[0]:
        return 0
    if v < T[1]:
        return 1
    if v < T[2]:
        return 2
    return 3


def legend_items(T):
    return [(RAMP[0][0], f'moins de {fmt(T[0])} %'),
            (RAMP[1][0], f'{fmt(T[0])} – {fmt(T[1])} %'),
            (RAMP[2][0], f'{fmt(T[1])} – {fmt(T[2])} %'),
            (RAMP[3][0], f'{fmt(T[2])} % et plus')]


def _norm(s):
    s = unicodedata.normalize('NFKD', str(s))
    return ''.join(c for c in s if not unicodedata.combining(c)).lower().strip()


# --------------------------------------------------------------------------
def _load_admin_polygons():
    """Retourne {section: [ [ (lon,lat), ... ], ... ]} ou None si pas de fichier."""
    if not os.path.exists(GEOJSON_PATH):
        return None
    try:
        gj = json.load(open(GEOJSON_PATH, encoding='utf-8'))
    except Exception:
        return None

    wanted = {_norm(s): s for s in SECTIONS}
    wanted.update({_norm(k): v for k, v in {
        'Anse e Drick': 'Anse à Drick', 'Anse a Drick': 'Anse à Drick',
        'Debouchette': 'Débouchette'}.items()})

    out = {}
    for feat in gj.get('features', []):
        props = feat.get('properties', {}) or {}
        name = None
        for val in props.values():
            if isinstance(val, str) and _norm(val) in wanted:
                name = wanted[_norm(val)]
                break
        if not name:
            continue
        geom = feat.get('geometry') or {}
        coords = geom.get('coordinates') or []
        rings = []
        if geom.get('type') == 'Polygon':
            rings = [coords[0]] if coords else []
        elif geom.get('type') == 'MultiPolygon':
            rings = [poly[0] for poly in coords if poly]
        if rings:
            out.setdefault(name, []).extend(rings)

    # Garde-fou : plusieurs communes d'Haïti peuvent avoir une section du même
    # nom. On écarte tout polygone situé à plus de ~0,6° (≈ 65 km) du centre de
    # la zone réellement enquêtée pour cette section.
    try:
        cent = json.load(open(CENTROIDS_PATH, encoding='utf-8'))['centroids']
        kx = json.load(open(CENTROIDS_PATH, encoding='utf-8'))['kx']
    except Exception:
        return out or None
    cleaned = {}
    for name, rings in out.items():
        ref = cent.get(name)
        if not ref:
            continue
        keep = []
        for ring in rings:
            cx = sum(lon for lon, _ in ring) / len(ring) * kx
            cy = sum(lat for _, lat in ring) / len(ring)
            if math.hypot(cx - ref[0], cy - ref[1]) <= 0.6:
                keep.append(ring)
        if keep:
            cleaned[name] = keep
    return cleaned or None


# --------------------------------------------------------------------------
def render_map_svg(values, base_n, thresholds=None, width=920, height=660):
    """values : {section: pourcentage}. Retourne (svg, thresholds, mode)."""
    T = thresholds or nice_thresholds(list(values.values()))
    admin = _load_admin_polygons()
    mode = 'admin' if admin else 'disques'

    kx = json.load(open(CENTROIDS_PATH, encoding='utf-8'))['kx']
    cent = json.load(open(CENTROIDS_PATH, encoding='utf-8'))['centroids']

    if admin:
        pts = [(lon * kx, lat) for rings in admin.values()
               for ring in rings for lon, lat in ring]
    else:
        pts = list(cent.values())

    PAD, R, GAP = 86, 31, 16
    x0 = min(p[0] for p in pts); x1 = max(p[0] for p in pts)
    y0 = min(p[1] for p in pts); y1 = max(p[1] for p in pts)
    sc = min((width - 2 * PAD) / max(x1 - x0, 1e-9),
             (height - 2 * PAD) / max(y1 - y0, 1e-9))
    ox = (width - (x1 - x0) * sc) / 2
    oy = (height - (y1 - y0) * sc) / 2

    def proj(x, y):
        return (ox + (x - x0) * sc, oy + (y1 - y) * sc)

    body = []
    label_anchor = {}

    if admin:
        for name in SECTIONS:
            rings = admin.get(name)
            if not rings:
                continue
            v = values.get(name)
            fill = RAMP[bin_of(v, T)][0] if v is not None else '#e1e0d9'
            d = ''
            allp = []
            for ring in rings:
                pp = [proj(lon * kx, lat) for lon, lat in ring]
                allp += pp
                d += 'M' + ' L'.join(f'{a:.1f},{b:.1f}' for a, b in pp) + ' Z'
            body.append(f'<path class="sec" d="{d}" fill="{fill}"/>')
            label_anchor[name] = (sum(p[0] for p in allp) / len(allp),
                                  sum(p[1] for p in allp) / len(allp))
    else:
        pos = {k: list(proj(*v)) for k, v in cent.items()}
        names = list(pos)
        for _ in range(600):                       # relaxation de Dorling
            moved = 0.0
            for i, a in enumerate(names):
                for b in names[i + 1:]:
                    dx = pos[b][0] - pos[a][0]
                    dy = pos[b][1] - pos[a][1]
                    dist = math.hypot(dx, dy) or 0.01
                    need = 2 * R + GAP
                    if dist < need:
                        push = (need - dist) / 2
                        ux, uy = dx / dist, dy / dist
                        pos[a][0] -= ux * push; pos[a][1] -= uy * push
                        pos[b][0] += ux * push; pos[b][1] += uy * push
                        moved += push
            if moved < 0.05:
                break
        pxs = [p[0] for p in pos.values()]; pys = [p[1] for p in pos.values()]
        sx = (width - (min(pxs) + max(pxs))) / 2
        sy = (height - (min(pys) + max(pys))) / 2
        for k in pos:
            pos[k][0] += sx; pos[k][1] += sy

        for name in SECTIONS:
            v = values.get(name)
            cx, cy = pos[name]
            if v is None:
                body.append(f'<circle class="sec" cx="{cx:.1f}" cy="{cy:.1f}" '
                            f'r="{R}" fill="#e1e0d9"/>')
            else:
                fill, ink = RAMP[bin_of(v, T)]
                body.append(
                    f'<circle class="sec" cx="{cx:.1f}" cy="{cy:.1f}" r="{R}" fill="{fill}">'
                    f'<title>{name} — {fmt_val(v)} % (base : {base_n.get(name, 0)})</title></circle>'
                    f'<text class="pv" x="{cx:.1f}" y="{cy + 6:.1f}" fill="{ink}">'
                    f'{fmt_val(v)}%</text>')
            label_anchor[name] = (cx, cy)

    # ---- étiquettes : 8 positions candidates, on garde la moins encombrée ----
    CH, LH = 8.4, 15.0
    off = R if not admin else 4
    CANDS = [(0, off + 18, 'middle'), (0, -off - 9, 'middle'),
             (off + 9, 5, 'start'), (-off - 9, 5, 'end'),
             (off + 7, -off + 4, 'start'), (-off - 7, -off + 4, 'end'),
             (off + 7, off + 8, 'start'), (-off - 7, off + 8, 'end')]

    def box(cx, cy, dx, dy, anchor, text):
        w = len(text) * CH
        x = cx + dx - (w / 2 if anchor == 'middle' else (w if anchor == 'end' else 0))
        return (x - 6, cy + dy - LH - 1, x + w + 6, cy + dy + 6)

    def hit(a, b):
        return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])

    def crowd(n):
        cx, cy = label_anchor[n]
        return sum(1 for m in label_anchor
                   if m != n and math.dist((cx, cy), label_anchor[m]) < 3.2 * max(R, 30))

    placed = []
    for name in sorted(label_anchor, key=crowd):
        cx, cy = label_anchor[name]
        best, best_s = CANDS[0], None
        for rank, (dx, dy, anchor) in enumerate(CANDS):
            bx = box(cx, cy, dx, dy, anchor, name)
            sco = sum(10 for b in placed if hit(bx, b))
            if not admin:
                for m, (mx, my) in label_anchor.items():
                    nx = max(bx[0], min(mx, bx[2]))
                    ny = max(bx[1], min(my, bx[3]))
                    if math.hypot(mx - nx, my - ny) < R + 1:
                        sco += 10
            if bx[0] < 4 or bx[2] > width - 4 or bx[1] < 4 or bx[3] > height - 4:
                sco += 40
            sco += rank * 0.1
            if best_s is None or sco < best_s:
                best, best_s = (dx, dy, anchor), sco
        placed.append(box(cx, cy, *best, name))
        dx, dy, anchor = best
        leader = ''
        if best != CANDS[0]:
            ang = math.atan2(dy, dx)
            lx = cx + math.cos(ang) * (R + 1 if not admin else 2)
            ly = cy + math.sin(ang) * (R + 1 if not admin else 2)
            tx = cx + dx + (0 if anchor == 'middle' else (-4 if anchor == 'end' else 4))
            leader = (f'<line class="ld" x1="{lx:.1f}" y1="{ly:.1f}" '
                      f'x2="{tx:.1f}" y2="{cy + dy - 4:.1f}"/>')
        v = values.get(name)
        extra = f' — {fmt_val(v)}%' if (admin and v is not None) else ''
        body.append(f'{leader}<text class="pn" x="{cx + dx:.1f}" y="{cy + dy:.1f}" '
                    f'style="text-anchor:{anchor}">{name}{extra}</text>')

    km_px = 111.32 / sc
    bar = 10 / km_px
    chrome = (f'<line class="cl" x1="60" y1="112" x2="60" y2="58"/>'
              f'<path class="ca" d="M60,52 L65.5,66 L60,62.5 L54.5,66 Z"/>'
              f'<text class="ct" x="60" y="130">N</text>'
              f'<line class="cl" x1="46" y1="{height - 42}" '
              f'x2="{46 + bar:.0f}" y2="{height - 42}"/>'
              f'<line class="cl" x1="46" y1="{height - 47}" x2="46" y2="{height - 37}"/>'
              f'<line class="cl" x1="{46 + bar:.0f}" y1="{height - 47}" '
              f'x2="{46 + bar:.0f}" y2="{height - 37}"/>'
              f'<text class="ct2" x="{46 + bar / 2:.0f}" y="{height - 22}">≈ 10 km</text>')

    svg = f"""<svg viewBox="0 0 {width} {height}" width="100%"
     style="max-width:{width}px;display:block;margin:0 auto" role="img"
     aria-label="Carte des sections communales colorées par seuil">
  <style>
    .sec{{stroke:{SURFACE};stroke-width:2;stroke-linejoin:round}}
    .pv{{font:650 15px system-ui,-apple-system,"Segoe UI",sans-serif;
        text-anchor:middle;font-variant-numeric:tabular-nums}}
    .pn{{font:600 13.5px system-ui,-apple-system,"Segoe UI",sans-serif;fill:{INK};
        paint-order:stroke;stroke:{SURFACE};stroke-width:4px;stroke-linejoin:round}}
    .ld{{stroke:{MUTED};stroke-width:1;opacity:.55}}
    .cl{{stroke:{MUTED};stroke-width:1.5}} .ca{{fill:{MUTED}}}
    .ct{{font:600 13px system-ui,sans-serif;fill:{MUTED};text-anchor:middle}}
    .ct2{{font:11.5px system-ui,sans-serif;fill:{MUTED};text-anchor:middle}}
  </style>
  {chrome}{''.join(body)}
</svg>"""
    return svg, T, mode
