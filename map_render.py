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
# Le fichier de limites administratives est accepté dans data/ ou à la racine
# du projet — le premier trouvé gagne.
GEOJSON_CANDIDATES = [os.path.join(APP_DIR, 'data', 'sections_communales.geojson'),
                      os.path.join(APP_DIR, 'sections_communales.geojson')]


LAND_CANDIDATES = [os.path.join(APP_DIR, 'data', 'hti_terre.geojson'),
                   os.path.join(APP_DIR, 'hti_terre.geojson')]
CONTEXT_CANDIDATES = [os.path.join(APP_DIR, 'data', 'contexte_geo.geojson'),
                      os.path.join(APP_DIR, 'contexte_geo.geojson')]


def _context_layers():
    """Repères de situation : limites départementales et villes principales.
    Retourne (departements, villes) ou (None, None)."""
    for p in CONTEXT_CANDIDATES:
        if os.path.exists(p):
            try:
                gj = json.load(open(p, encoding='utf-8'))
            except Exception:
                return None, None
            deps, villes = [], []
            for feat in gj.get('features', []):
                props = feat.get('properties', {}) or {}
                g = feat.get('geometry') or {}
                if props.get('type') == 'departement':
                    rings = ([poly[0] for poly in g.get('coordinates', []) if poly]
                             if g.get('type') == 'MultiPolygon'
                             else [g['coordinates'][0]])
                    deps.append((props.get('nom', ''), rings))
                elif props.get('type') == 'ville':
                    villes.append((props.get('nom', ''), g.get('coordinates')))
            return (deps or None), (villes or None)
    return None, None


def _geojson_path():
    for p in GEOJSON_CANDIDATES:
        if os.path.exists(p):
            return p
    return None


def _land_rings():
    """Contour de la terre émergée (Haïti), pour distinguer la mer.
    Retourne une liste d'anneaux [(lon, lat), ...] ou None."""
    for p in LAND_CANDIDATES:
        if os.path.exists(p):
            try:
                gj = json.load(open(p, encoding='utf-8'))
            except Exception:
                return None
            rings = []
            for feat in gj.get('features', []):
                g = feat.get('geometry') or {}
                if g.get('type') == 'MultiPolygon':
                    for poly in g.get('coordinates', []):
                        if poly:
                            rings.append(poly[0])
                elif g.get('type') == 'Polygon':
                    c = g.get('coordinates') or []
                    if c:
                        rings.append(c[0])
            return rings or None
    return None

SECTIONS = ['Anse à Drick', 'Barbois', 'Dumont', 'Débouchette', 'Mouline',
            'Quentin', 'Beaulieu', 'Blactote', 'Dalmette', 'Trichet']

# Position de chaque section : centre de la zone enquêtée, en coordonnées déjà
# corrigées de la longitude (x = longitude × KX). Intégré ici plutôt que dans un
# fichier séparé pour que la carte fonctionne sans dépendance supplémentaire ;
# data/map_centroids.json, s'il existe, a la priorité.
KX = 0.9500035092
CENTROIDS = {
    'Anse à Drick': (-70.233651, 18.13974),
    'Barbois': (-70.198143, 18.107813),
    'Beaulieu': (-70.272203, 18.169772),
    'Blactote': (-70.644832, 18.314333),
    'Dalmette': (-70.563675, 18.312269),
    'Débouchette': (-70.17652, 18.046148),
    'Dumont': (-70.19615, 18.061282),
    'Mouline': (-70.303753, 18.45591),
    'Quentin': (-70.33944, 18.262254),
    'Trichet': (-70.11585, 18.043485),
}


def _geo():
    """(kx, centroids) — depuis le fichier s'il est présent, sinon les valeurs
    intégrées ci-dessus."""
    try:
        d = json.load(open(CENTROIDS_PATH, encoding='utf-8'))
        return d['kx'], {k: tuple(v) for k, v in d['centroids'].items()}
    except Exception:
        return KX, dict(CENTROIDS)

# --------------------------------------------------------------------------
# Trois rampes, choisies selon le sens de l'indicateur. Chaque entrée = (fond,
# encre du texte posé dessus), l'encre étant celle qui donne le meilleur
# contraste (toutes ≥ 4,5:1).
#
# 'neutre'  : rampe séquentielle bleue, une seule teinte — quand un pourcentage
#             élevé n'est ni bon ni mauvais (mois de semis, zone de pêche...).
# 'eleve_mauvais' / 'eleve_bon' : échelle de gravité vert → jaune → orange →
#             rouge, retournée selon le sens. Séparation vérifiée avec le
#             validateur de palette (pire paire adjacente : ΔE 17,2 en vision
#             daltonienne, 21,7 en vision normale) — nettement au-dessus des
#             seuils. La valeur reste écrite sur chaque section : la couleur
#             ne porte jamais l'information toute seule.
# --------------------------------------------------------------------------
RAMP_NEUTRAL = [('#86b6ef', '#0b0b0b'), ('#3987e5', '#0b0b0b'),
                ('#256abf', '#ffffff'), ('#104281', '#ffffff')]
RAMP_SEVERITY = [('#3d9e4f', '#0b0b0b'), ('#f0c419', '#0b0b0b'),
                 ('#dd6b0d', '#0b0b0b'), ('#98161c', '#ffffff')]

POLARITIES = ('eleve_mauvais', 'eleve_bon', 'neutre')


def ramp_for(polarity):
    if polarity == 'eleve_mauvais':
        return RAMP_SEVERITY                      # bas = vert, haut = rouge
    if polarity == 'eleve_bon':
        return RAMP_SEVERITY[::-1]                # bas = rouge, haut = vert
    return RAMP_NEUTRAL


def polarity_caption(polarity):
    if polarity == 'eleve_mauvais':
        return ("Lecture des couleurs : vert = situation la plus favorable, "
                "rouge = la plus préoccupante (ici, un pourcentage élevé est défavorable).")
    if polarity == 'eleve_bon':
        return ("Lecture des couleurs : vert = situation la plus favorable, "
                "rouge = la plus préoccupante (ici, un pourcentage élevé est favorable).")
    return ("Lecture des couleurs : du plus clair au plus foncé selon le pourcentage. "
            "Aucune couleur ne juge la situation — cet indicateur n'est ni bon ni mauvais en soi.")


# --- Faut-il lire un pourcentage élevé comme une mauvaise nouvelle ? --------
# Sur 503 questions, aucune règle automatique n'est fiable à 100 % : on ne
# propose qu'une valeur par défaut, que l'utilisateur peut corriger d'un clic.
# Dans le doute, on reste en neutre plutôt que de colorier à tort.
# Non-réponses et fourre-tout : jamais coloriés en bien/mal — testés en premier.
_MOD_NEUTRE = (
    'ne sait pas', 'ne souhaite pas répondre', 'non précisé', 'sans objet',
    'non applicable', 'autre', 'non classé', 'code ambigu', 'refus',
)
_MOD_MAUVAIS = (
    'aucun', 'aucune', 'sans dalle', 'air libre', 'non protég', 'non traité',
    'diminution', 'sécheresse', 'maladie', 'inondation', 'éboulement',
    'glissement', 'détérioration', 'déforestation', 'érosion', 'perte',
    'perdu', 'dégâts importants', 'jamais', 'pas de',
    "n'a pas", 'non scolaris', 'analphab', 'défécation',
)
_MOD_BON = (
    'protég', 'réseau', 'augmentation', 'amélior', 'avec dalle',
    'chasse d\'eau', 'vaccin', 'scolaris', 'irrig',
)
_Q_OUI_MAUVAIS = (
    'inquiet', "n'a pas pu", 'moins que', 'sans manger', 'peu variée',
    'faim', 'endommag', 'perte', 'perdu', 'mortalit', 'maladie', 'pot-de-vin',
    'pot de vin', 'violence', 'vol ', 'insécurit', 'a dû ', 'renoncé',
    'sauter un repas', 'épuisé', 'manqué',
)
_Q_OUI_BON = (
    'accès', 'a voté', 'participé', 'épargne', 'sécurité', 'assur',
    'formation', 'reçu une alerte', 'alerte', 'associat', 'entraide',
    'appartien', 'possède', 'sait lire',
)


def guess_polarity(question, modality):
    """Proposition de lecture : 'eleve_mauvais', 'eleve_bon' ou 'neutre'."""
    q, m = _norm(question), _norm(modality)
    for kw in _MOD_NEUTRE:
        if _norm(kw) in m:
            return 'neutre'
    for kw in _MOD_MAUVAIS:
        if _norm(kw) in m:
            return 'eleve_mauvais'
    for kw in _MOD_BON:
        if _norm(kw) in m:
            return 'eleve_bon'
    if m in ('oui', 'oui '):
        for kw in _Q_OUI_MAUVAIS:
            if _norm(kw) in q:
                return 'eleve_mauvais'
        for kw in _Q_OUI_BON:
            if _norm(kw) in q:
                return 'eleve_bon'
    if m == 'non':
        for kw in _Q_OUI_MAUVAIS:
            if _norm(kw) in q:
                return 'eleve_bon'
        for kw in _Q_OUI_BON:
            if _norm(kw) in q:
                return 'eleve_mauvais'
    return 'neutre'

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


def legend_items(T, polarity='neutre'):
    R = ramp_for(polarity)
    return [(R[0][0], f'moins de {fmt(T[0])} %'),
            (R[1][0], f'{fmt(T[0])} – {fmt(T[1])} %'),
            (R[2][0], f'{fmt(T[1])} – {fmt(T[2])} %'),
            (R[3][0], f'{fmt(T[2])} % et plus')]


def _norm(s):
    s = unicodedata.normalize('NFKD', str(s))
    return ''.join(c for c in s if not unicodedata.combining(c)).lower().strip()


# --------------------------------------------------------------------------
def _load_admin_polygons():
    """Retourne {section: [ [ (lon,lat), ... ], ... ]} ou None si pas de fichier."""
    path = _geojson_path()
    if not path:
        return None
    try:
        gj = json.load(open(path, encoding='utf-8'))
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
    kx, cent = _geo()
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
def _point_in_rings(x, y, rings):
    """Vrai si (x, y) est dans le polygone (règle pair-impair, trous compris)."""
    inside = False
    for ring in rings:
        n = len(ring)
        for i in range(n):
            x1, y1 = ring[i]
            x2, y2 = ring[(i + 1) % n]
            if (y1 > y) != (y2 > y):
                xin = (x2 - x1) * (y - y1) / ((y2 - y1) or 1e-12) + x1
                if x < xin:
                    inside = not inside
    return inside


def _dist_to_edges(x, y, rings):
    """Distance du point au bord le plus proche."""
    best = float('inf')
    for ring in rings:
        n = len(ring)
        for i in range(n):
            x1, y1 = ring[i]
            x2, y2 = ring[(i + 1) % n]
            dx, dy = x2 - x1, y2 - y1
            L2 = dx * dx + dy * dy
            t = 0.0 if L2 < 1e-12 else max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / L2))
            d = math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))
            if d < best:
                best = d
    return best


def _box_fits_inside(cx, cy, w, h, rings):
    """Le rectangle (w × h) centré en (cx, cy) tient-il dans le polygone ?
    On teste le contour du rectangle, pas seulement ses coins : un polygone
    concave peut mordre au milieu d'un côté."""
    hw, hh = w / 2.0, h / 2.0
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        for x, y in ((cx - hw + t * w, cy - hh), (cx - hw + t * w, cy + hh),
                     (cx - hw, cy - hh + t * h), (cx + hw, cy - hh + t * h)):
            if not _point_in_rings(x, y, rings):
                return False
    return True


def _pole_in_view(rings, width, height, margin=26):
    """Meilleur point pour poser une étiquette de zone : à l'intérieur du
    polygone ET confortablement dans le cadre. Indispensable pour un
    département qui n'affleure qu'au bord de la carte (sinon son nom part
    au large ou hors champ)."""
    best, best_score = None, -1.0
    nx, ny = 46, 34
    for i in range(nx):
        x = margin + (width - 2 * margin) * i / (nx - 1)
        for j in range(ny):
            y = margin + (height - 2 * margin) * j / (ny - 1)
            if not _point_in_rings(x, y, rings):
                continue
            # on maximise à la fois l'éloignement du bord du polygone
            # (donc de la côte) et l'éloignement du bord du cadre
            d_poly = _dist_to_edges(x, y, rings)
            d_view = min(x - margin, width - margin - x,
                         y - margin, height - margin - y)
            score = min(d_poly, d_view)
            if score > best_score:
                best, best_score = (x, y), score
    return best, best_score


def _pole_of_inaccessibility(rings):
    """Point intérieur le plus éloigné du bord, et sa distance au bord.

    Recherche sur grille puis raffinements successifs : suffisant ici (10
    polygones) et sans dépendance externe. C'est ce point qui permet de savoir
    s'il y a la place d'écrire le pourcentage à l'intérieur de la section.
    """
    pts = [p for ring in rings for p in ring]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    bx0, bx1, by0, by1 = min(xs), max(xs), min(ys), max(ys)
    best = (0.5 * (bx0 + bx1), 0.5 * (by0 + by1), -1.0)
    step = max((bx1 - bx0) / 24.0, (by1 - by0) / 24.0, 1e-6)
    x, y = bx0, by0
    while y <= by1:
        x = bx0
        while x <= bx1:
            if _point_in_rings(x, y, rings):
                d = _dist_to_edges(x, y, rings)
                if d > best[2]:
                    best = (x, y, d)
            x += step
        y += step
    for _ in range(4):                       # raffinement local
        cx, cy, cd = best
        step /= 3.0
        for i in (-2, -1, 0, 1, 2):
            for j in (-2, -1, 0, 1, 2):
                nx, ny = cx + i * step, cy + j * step
                if _point_in_rings(nx, ny, rings):
                    d = _dist_to_edges(nx, ny, rings)
                    if d > best[2]:
                        best = (nx, ny, d)
    if best[2] < 0:                          # polygone dégénéré : repli
        return (0.5 * (bx0 + bx1), 0.5 * (by0 + by1), 0.0)
    return best


# --------------------------------------------------------------------------
def render_map_svg(values, base_n, thresholds=None, width=920, height=660,
                   polarity='neutre'):
    """values : {section: pourcentage}. Retourne (svg, thresholds, mode)."""
    T = thresholds or nice_thresholds(list(values.values()))
    RAMP = ramp_for(polarity)
    admin = _load_admin_polygons()
    mode = 'admin' if admin else 'disques'

    kx, cent = _geo()

    if admin:
        pts = [(lon * kx, lat) for rings in admin.values()
               for ring in rings for lon, lat in ring]
    else:
        pts = list(cent.values())

    PAD, R, GAP = 86, 31, 16
    x0 = min(p[0] for p in pts); x1 = max(p[0] for p in pts)
    y0 = min(p[1] for p in pts); y1 = max(p[1] for p in pts)

    # Quand on affiche le fond de carte terre/mer, on élargit un peu la vue pour
    # que le littoral apparaisse autour des sections.
    land = _land_rings()
    deps, villes = _context_layers()
    if land:
        m = 0.07 * max(x1 - x0, y1 - y0)
        x0 -= m; x1 += m; y0 -= m; y1 += m
    # Les villes repères doivent entrer dans le cadre : elles élargissent la vue
    # (les limites départementales, elles, sont simplement rognées par le cadre).
    if villes:
        for _, (vlon, vlat) in villes:
            x0 = min(x0, vlon * kx - 0.012); x1 = max(x1, vlon * kx + 0.012)
            y0 = min(y0, vlat - 0.012); y1 = max(y1, vlat + 0.012)

    sc = min((width - 2 * PAD) / max(x1 - x0, 1e-9),
             (height - 2 * PAD) / max(y1 - y0, 1e-9))
    ox = (width - (x1 - x0) * sc) / 2
    oy = (height - (y1 - y0) * sc) / 2

    def proj(x, y):
        return (ox + (x - x0) * sc, oy + (y1 - y) * sc)

    body = []
    label_anchor = {}
    inner_room = {}          # rayon disponible à l'intérieur de chaque section
    polys_px = {}            # contours projetés, pour tester si un texte y tient

    # ---- fond : mer puis terre émergée ----
    if land:
        body.append(f'<rect class="sea" x="0" y="0" width="{width}" height="{height}"/>')
        d = ''
        for ring in land:
            pp = [proj(lon * kx, lat) for lon, lat in ring]
            d += 'M' + ' L'.join(f'{a:.1f},{b:.1f}' for a, b in pp) + ' Z'
        body.append(f'<path class="land" d="{d}"/>')

    # ---- limites départementales (repère de situation) ----
    dep_labels = []
    if deps:
        for nom, rings in deps:
            d = ''
            for ring in rings:
                pp = [proj(lon * kx, lat) for lon, lat in ring]
                d += 'M' + ' L'.join(f'{a:.1f},{b:.1f}' for a, b in pp) + ' Z'
            body.append(f'<path class="dep" d="{d}"/>')
            # étiquette posée dans la partie du département réellement visible
            # ET à terre — pas à la moyenne des sommets, qui tombe en mer quand
            # le département n'affleure qu'au bord du cadre (cas des Nippes)
            rings_px = [[proj(lon * kx, lat) for lon, lat in ring] for ring in rings]
            pt, room = _pole_in_view(rings_px, width, height)
            if pt and room > 16:
                dep_labels.append((nom, pt[0], pt[1]))

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
            tip = (f'{name} — {fmt_val(v)} % (base : {base_n.get(name, 0)})'
                   if v is not None else name)
            body.append(f'<path class="sec" d="{d}" fill="{fill}">'
                        f'<title>{tip}</title></path>')
            # Point d'ancrage = pôle d'inaccessibilité (le point le plus « au
            # large » à l'intérieur du polygone), et non le centroïde : sur une
            # forme concave ou en croissant, le centroïde tombe souvent dehors.
            rings_px = [[proj(lon * kx, lat) for lon, lat in ring] for ring in rings]
            px_, py_, rad = _pole_of_inaccessibility(rings_px)
            label_anchor[name] = (px_, py_)
            inner_room[name] = rad
            polys_px[name] = rings_px
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

    # ---- 1) le pourcentage à l'intérieur de la section quand il y tient ----
    val_inside = {}
    val_boxes = []
    if admin:
        # on sert d'abord les sections les plus spacieuses : en cas de conflit
        # entre deux valeurs voisines, c'est la plus à l'étroit qui sort
        order = sorted((n for n in SECTIONS if n in label_anchor),
                       key=lambda n: -inner_room.get(n, 0))
        for name in order:
            v = values.get(name)
            if v is None:
                continue
            txt = f'{fmt_val(v)}%'
            cx, cy = label_anchor[name]
            w = len(txt) * 7.6
            bx = (cx - w / 2 - 2, cy - 9, cx + w / 2 + 2, cy + 8)
            if any(not (bx[2] < o[0] or o[2] < bx[0] or bx[3] < o[1] or o[3] < bx[1])
                   for o in val_boxes):
                continue                      # chevaucherait une valeur voisine
            # La valeur est posée au cœur de la section (pôle d'inaccessibilité).
            # Si la section est trop étroite pour contenir la boîte du texte, on
            # garde quand même la valeur là : centrée sur SA section, elle reste
            # correctement attribuée, et un liseré blanc la détache du fond.
            # En dessous d'un seuil, la section est vraiment trop fine : la
            # valeur part alors à l'extérieur, accolée au nom.
            fits = _box_fits_inside(cx, cy, len(txt) * 7.2 + 2, 13,
                                    polys_px.get(name, []))
            if fits or inner_room.get(name, 0) >= 9:
                body.append(f'<text class="pv" x="{cx:.1f}" y="{cy + 5:.1f}">'
                            f'{txt}</text>')
                val_inside[name] = (w / 2 + 3, 11)   # demi-largeur / demi-hauteur
                val_boxes.append(bx)

    # ---- 2) les noms : à l'extérieur, reliés par un trait ----
    # Le nom seul est bien plus court que « nom + valeur » : beaucoup moins de
    # collisions, et l'association nom ↔ section est portée par le trait.
    CH, LH = 8.4, 15.0
    if admin:
        CANDS = []
        for rad in (46, 72, 100, 132, 168, 210):
            for ang_deg in (0, 180, 90, 270, 35, 145, 325, 215, 60, 120, 300, 240):
                a = math.radians(ang_deg)
                dx, dy = rad * math.cos(a), rad * math.sin(a)
                anchor = 'middle' if abs(dx) < rad * 0.35 else (
                    'start' if dx > 0 else 'end')
                CANDS.append((round(dx), round(dy), anchor))
    else:
        off = R
        CANDS = [(0, off + 18, 'middle'), (0, -off - 9, 'middle'),
                 (off + 9, 5, 'start'), (-off - 9, 5, 'end'),
                 (off + 7, -off + 4, 'start'), (-off - 7, -off + 4, 'end'),
                 (off + 7, off + 8, 'start'), (-off - 7, off + 8, 'end')]

    def label_text(name):
        """En mode contours, la valeur rejoint le nom si elle n'a pas tenu dedans."""
        if admin and not val_inside.get(name):
            v = values.get(name)
            return f'{name} — {fmt_val(v)}%' if v is not None else f'{name} — n.d.'
        return name

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

    def _seg_cross(p1, p2, p3, p4):
        """Les segments [p1p2] et [p3p4] se croisent-ils ?"""
        def side(a, b, c):
            return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        d1, d2 = side(p3, p4, p1), side(p3, p4, p2)
        d3, d4 = side(p1, p2, p3), side(p1, p2, p4)
        return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))

    def _leader_ends(name, dx, dy, anchor):
        cx, cy = label_anchor[name]
        ang = math.atan2(dy, dx)
        ca, sa = math.cos(ang), math.sin(ang)
        if admin and val_inside.get(name):
            # le trait part du bord de la valeur écrite, pas du centre :
            # sinon il barre le chiffre
            hw, hh = val_inside[name]
            start = min(hw / max(abs(ca), 1e-6), hh / max(abs(sa), 1e-6)) + 2
        elif admin:
            start = max(inner_room.get(name, 0) * 0.85, 4)
        else:
            start = R + 1
        p1 = (cx + ca * start, cy + sa * start)
        p2 = (cx + dx + (0 if anchor == 'middle' else (-5 if anchor == 'end' else 5)),
              cy + dy - 4)
        return p1, p2

    # obstacles : valeurs déjà posées, noms de départements, villes
    placed = [(b[0] - 3, b[1] - 3, b[2] + 3, b[3] + 3) for b in val_boxes]
    for nom, lx_, ly_ in dep_labels:
        w = len(nom) * 8.2
        placed.append((lx_ - w / 2 - 4, ly_ - 14, lx_ + w / 2 + 4, ly_ + 6))
    city_px = []
    if villes:
        for nom, (vlon, vlat) in villes:
            vx, vy = proj(vlon * kx, vlat)
            if 0 < vx < width and 0 < vy < height:
                city_px.append((nom, vx, vy))
                w = len(nom) * 7.0
                # le point ET son nom (posé au-dessus) sont à éviter
                placed.append((vx - w / 2 - 4, vy - 24, vx + w / 2 + 4, vy + 8))
    placed_leaders = []

    for name in sorted(label_anchor, key=crowd):
        cx, cy = label_anchor[name]
        txt = label_text(name)
        best, best_s = CANDS[0], None
        for rank, (dx, dy, anchor) in enumerate(CANDS):
            bx = box(cx, cy, dx, dy, anchor, txt)
            sco = sum(10 for b in placed if hit(bx, b))
            for m, (mx, my) in label_anchor.items():
                if m == name:
                    continue
                nx = max(bx[0], min(mx, bx[2]))
                ny = max(bx[1], min(my, bx[3]))
                # ne pas poser le nom d'une section sur le cœur d'une autre
                if math.hypot(mx - nx, my - ny) < (R + 1 if not admin else
                                                   inner_room.get(m, 0) * 0.9):
                    sco += 8
            # deux traits qui se croisent rendent l'association illisible
            p1, p2 = _leader_ends(name, dx, dy, anchor)
            for q1, q2 in placed_leaders:
                if _seg_cross(p1, p2, q1, q2):
                    sco += 14
            # un trait qui traverse une AUTRE section brouille aussi la lecture
            if admin:
                for m, rings_m in polys_px.items():
                    if m == name:
                        continue
                    for t in (0.35, 0.55, 0.75, 0.95):
                        sx_ = p1[0] + (p2[0] - p1[0]) * t
                        sy_ = p1[1] + (p2[1] - p1[1]) * t
                        if _point_in_rings(sx_, sy_, rings_m):
                            sco += 6
                            break
            if bx[0] < 4 or bx[2] > width - 4 or bx[1] < 4 or bx[3] > height - 4:
                sco += 40
            sco += rank * 0.12                     # préférer les positions proches
            if best_s is None or sco < best_s:
                best, best_s = (dx, dy, anchor), sco
        placed.append(box(cx, cy, *best, txt))
        dx, dy, anchor = best

        # trait de rappel : part du bord de la section, s'arrête au ras du texte
        (lx, ly), (tx, ty) = _leader_ends(name, dx, dy, anchor)
        leader = ''
        if math.hypot(tx - lx, ty - ly) > 6:
            placed_leaders.append(((lx, ly), (tx, ty)))
            # doublé d'un liseré clair, pour rester visible sur la terre
            # comme sur la mer
            leader = (f'<line class="ld-halo" x1="{lx:.1f}" y1="{ly:.1f}" '
                      f'x2="{tx:.1f}" y2="{ty:.1f}"/>'
                      f'<line class="ld" x1="{lx:.1f}" y1="{ly:.1f}" '
                      f'x2="{tx:.1f}" y2="{ty:.1f}"/>')
        body.append(f'{leader}<text class="pn" x="{cx + dx:.1f}" y="{cy + dy:.1f}" '
                    f'style="text-anchor:{anchor}">{txt}</text>')

    # ---- repères de situation : noms de départements puis villes ----
    for nom, lx_, ly_ in dep_labels:
        body.append(f'<text class="dept" x="{lx_:.0f}" y="{ly_:.0f}">{nom.upper()}</text>')
    for nom, vx, vy in city_px:
        body.append(f'<circle class="city" cx="{vx:.1f}" cy="{vy:.1f}" r="4"/>'
                    f'<text class="cityt" x="{vx:.1f}" y="{vy - 9:.1f}">{nom}</text>')

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
    .sea{{fill:#dde6ee}}
    .land{{fill:#f1efe9;stroke:#c9c6bc;stroke-width:0.8;stroke-linejoin:round}}
    .dep{{fill:none;stroke:#a8a49a;stroke-width:1.3;stroke-dasharray:7 4;
         stroke-linejoin:round}}
    .dept{{font:600 11px system-ui,sans-serif;fill:#9a968b;letter-spacing:.09em;
          text-anchor:middle;paint-order:stroke;stroke:{SURFACE};stroke-width:3px}}
    /* Villes : maigre, gris, légèrement espacé — les noms de sections sont
       eux en gras noir. Deux registres typographiques distincts, pour qu'on ne
       confonde jamais un repère de situation avec une unité d'analyse. */
    .city{{fill:none;stroke:{INK2};stroke-width:2}}
    .cityt{{font:400 11.5px system-ui,sans-serif;fill:{INK2};text-anchor:middle;
           letter-spacing:.06em;paint-order:stroke;stroke:{SURFACE};
           stroke-width:3.5px;stroke-linejoin:round}}
    .sec{{stroke:{SURFACE};stroke-width:2;stroke-linejoin:round}}
    .pv{{font:650 13.5px system-ui,-apple-system,"Segoe UI",sans-serif;
        text-anchor:middle;font-variant-numeric:tabular-nums;fill:{INK};
        paint-order:stroke;stroke:{SURFACE};stroke-width:3.5px;stroke-linejoin:round}}
    .pn{{font:600 13.5px system-ui,-apple-system,"Segoe UI",sans-serif;fill:{INK};
        paint-order:stroke;stroke:{SURFACE};stroke-width:4px;stroke-linejoin:round}}
    .pw{{font:650 14px system-ui,-apple-system,"Segoe UI",sans-serif;fill:{INK};
        font-variant-numeric:tabular-nums;
        paint-order:stroke;stroke:{SURFACE};stroke-width:4px;stroke-linejoin:round}}
    .ld{{stroke:#57554f;stroke-width:1.7;stroke-linecap:round}}
    .ld-halo{{stroke:{SURFACE};stroke-width:4;stroke-linecap:round;opacity:.9}}
    .cl{{stroke:{MUTED};stroke-width:1.5}} .ca{{fill:{MUTED}}}
    .ct{{font:600 13px system-ui,sans-serif;fill:{MUTED};text-anchor:middle;
        paint-order:stroke;stroke:{SURFACE};stroke-width:3px}}
    .ct2{{font:11.5px system-ui,sans-serif;fill:{MUTED};text-anchor:middle;
         paint-order:stroke;stroke:{SURFACE};stroke-width:3px}}
  </style>
  {''.join(body)}{chrome}
</svg>"""
    return svg, T, mode
