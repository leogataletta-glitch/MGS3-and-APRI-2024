"""La carte d'entrée : trois cadrages, de l'île aux sections communales.

CE QU'ELLE RÉPOND, ET POURQUOI UNE CARTE FIXE NE LE FAISAIT PAS

Un lecteur qui arrive ne sait pas où sont les dix sections enquêtées. Une carte
cadrée sur le Sud et la Grand'Anse lui montre des contours qu'il ne peut
rattacher à rien : ni au pays, ni à l'île. Une carte cadrée sur l'île, à
l'inverse, réduit les sections à des points invisibles. Il faut les deux, et
c'est le passage de l'une à l'autre qui informe — l'échelle se comprend en la
parcourant.

TROIS CADRAGES, DANS CET ORDRE

  1. L'île entière : Haïti et la République dominicaine côte à côte. C'est
     l'échelle où l'on se situe.
  2. La péninsule du sud : Grand'Anse, Sud, Nippes, avec Jérémie et Les Cayes.
     C'est l'échelle des départements où le projet travaille.
  3. Les dix sections communales enquêtées. C'est l'échelle de la donnée.

ELLE TOURNE EN BOUCLE, ET LA BOUCLE S'ARRÊTE. Le déroulé rejoue toutes les
neuf secondes : quatre et demie de mouvement, quatre et demie arrêté sur les
dix sections. Le bouton d'arrêt le suspend, et choisir un cadrage l'arrête
aussi — sans quoi le cadrage qu'on vient de demander serait balayé au tour
suivant. Le lecteur qui prend la main l'a prise.

`prefers-reduced-motion` EST RESPECTÉ. Ni boucle ni transition : la carte
ouvre directement sur les sections, et les boutons sautent d'un cadrage à
l'autre. C'est un réglage système, pas une préférence esthétique :
certains lecteurs en ont besoin.

POURQUOI UN COMPOSANT ET NON UN SVG POSÉ DANS LA PAGE. L'animation demande du
JavaScript, que Streamlit n'exécute pas dans un `st.markdown`. Le composant
vit donc dans son cadre, et tout ce qu'il lui faut — géométries, libellés,
styles — y est écrit avec lui : il ne fait aucun appel au réseau.
"""

import json
import math
import os

import streamlit as st
import streamlit.components.v1 as components

import i18n
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

# La palette est celle du site : le vert APRI pour ce qui est enquêté, des
# gris-verts pour le contexte, un bleu très pâle pour la mer.
MER = "#dce8f2"
TERRE_ETR = "#eceae4"
TERRE_HTI = "#e3e7e0"
DEPT = "#cfe0d2"
DEPT_TRAIT = "#8aa894"
SECTION = "#1f7a5a"
SECTION_TRAIT = "#12523c"
ENCRE = "#3c4761"

TEXTES = {
    "cz_t": {"en": "From the island to the ten communal sections",
             "fr": "De l'île aux dix sections communales"},
    "cz_e1": {"en": "The island", "fr": "L'île"},
    "cz_e2": {"en": "The southern peninsula", "fr": "La péninsule du sud"},
    "cz_e3": {"en": "The ten sections", "fr": "Les dix sections"},
    "cz_stop": {"en": "Stop", "fr": "Stop"},
    "cz_lire": {"en": "Loop", "fr": "En boucle"},
    "cz_haiti": {"en": "HAITI", "fr": "HAÏTI"},
    "cz_dom": {"en": "DOMINICAN REPUBLIC", "fr": "RÉPUBLIQUE DOMINICAINE"},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)


# --------------------------------------------------------------- géométrie
def _lire(nom):
    """Une géométrie, cherchée dans `data/` PUIS à la racine.

    LE DÉPÔT DÉPLOYÉ N'A PAS LA MÊME ARBORESCENCE QUE L'ATELIER. Trois des
    quatre géométries — le contour d'Haïti, les départements, les sections
    communales — y vivent à la racine et non dans `data/`, parce qu'elles y
    ont été déposées avant que le dossier existe. Ne chercher que dans
    `data/` renvoyait donc None en ligne, et la page d'accueil retombait
    silencieusement sur sa carte fixe : rien ne s'affichait de la nouvelle
    carte, et rien ne le signalait. C'est la règle du reste de la
    plateforme, et elle n'avait pas été suivie ici.
    """
    for c in (os.path.join(DATA, nom), os.path.join(APP_DIR, nom)):
        if os.path.exists(c):
            with open(c, encoding="utf-8") as f:
                return json.load(f)
    return None


def _anneaux(geom):
    """Les anneaux extérieurs d'un polygone ou d'un multipolygone."""
    t = geom.get("type")
    if t == "Polygon":
        return list(geom["coordinates"])
    if t == "MultiPolygon":
        out = []
        for poly in geom["coordinates"]:
            out.extend(poly)
        return out
    return []


def _simplifier(pts, tol):
    """Douglas-Peucker, écrit ici pour ne pas ajouter une dépendance.

    LE POIDS DU COMPOSANT EST LE SEUL ENJEU. Les contours de la République
    dominicaine n'ont pas besoin d'être fidèles au dixième de degré pour
    servir de décor, alors que ceux des sections enquêtées, eux, sont le
    sujet : chaque couche a donc sa tolérance, et le fichier envoyé au
    navigateur tient dans quelques dizaines de kilo-octets.
    """
    if len(pts) < 3 or tol <= 0:
        return pts
    a, b = pts[0], pts[-1]
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    imax, dmax = 0, -1.0
    for i in range(1, len(pts) - 1):
        p = pts[i]
        d = (abs(dx * (a[1] - p[1]) - dy * (a[0] - p[0])) / n if n
             else math.hypot(p[0] - a[0], p[1] - a[1]))
        if d > dmax:
            imax, dmax = i, d
    if dmax <= tol:
        return [a, b]
    return (_simplifier(pts[:imax + 1], tol)[:-1]
            + _simplifier(pts[imax:], tol))


class _Proj:
    """Une projection plate, suffisante à cette latitude.

    On ne monte pas une Mercator pour deux degrés de latitude : à 18° N, une
    simple mise à l'échelle des longitudes par le cosinus de la latitude tient
    les proportions à mieux qu'un demi pour cent sur toute l'étendue de la
    carte. Le nord est en haut, et un degré de latitude vaut mille unités.
    """

    def __init__(self, lat0):
        self.k = math.cos(math.radians(lat0))

    def __call__(self, lon, lat):
        return (lon * self.k * 1000.0, -lat * 1000.0)


def _chemin(anneaux, proj, tol):
    """Les anneaux d'une couche, en un seul attribut `d`."""
    bouts = []
    for ring in anneaux:
        pts = [proj(c[0], c[1]) for c in ring if len(c) >= 2]
        pts = _simplifier(pts, tol)
        if len(pts) < 3:
            continue
        bouts.append("M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z")
    return "".join(bouts)


def _cadre(anneaux, proj, marge):
    """Le rectangle qui contient une couche, avec sa marge, en unités
    projetées : c'est un `viewBox` prêt à poser."""
    xs, ys = [], []
    for ring in anneaux:
        for c in ring:
            if len(c) < 2:
                continue
            x, y = proj(c[0], c[1])
            xs.append(x)
            ys.append(y)
    if not xs:
        return None
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    mx, my = (x1 - x0) * marge, (y1 - y0) * marge
    return [x0 - mx, y0 - my, (x1 - x0) + 2 * mx, (y1 - y0) + 2 * my]


def _ajuster(cadre, ratio):
    """Le cadrage étendu au format du dessin.

    UN CADRAGE QUI N'A PAS LE FORMAT DE LA FENÊTRE EST UN CADRAGE QUI MENT :
    le navigateur le complète lui-même, et l'objet visé se retrouve décentré
    d'autant. On l'étend ici, autour de son propre centre.
    """
    x, y, w, h = cadre
    if w / h < ratio:
        nw = h * ratio
        x -= (nw - w) / 2.0
        w = nw
    else:
        nh = w / ratio
        y -= (nh - h) / 2.0
        h = nh
    return [x, y, w, h]


# ------------------------------------------------------------------- rendu
LARG, HAUT = 1000.0, 720.0


def _composer(lang):
    """Le composant entier — géométries, libellés, animation — en une chaîne.

    Rend `None` si les fichiers de géométrie manquent : l'appelant retombe
    alors sur la carte fixe, qui n'a besoin de rien.
    """
    hti = _lire("hti_terre.geojson")
    dom = _lire("dom_terre.geojson")
    ctx = _lire("contexte_geo.geojson")
    sec = _lire("sections_communales.geojson")
    if not (hti and sec):
        return None

    proj = _Proj(18.5)

    a_hti = _anneaux(hti["features"][0]["geometry"])
    a_dom = (_anneaux(dom["features"][0]["geometry"]) if dom else [])
    depts, villes = [], []
    for f in (ctx or {}).get("features", []):
        p = f.get("properties") or {}
        if p.get("type") == "departement":
            depts.append((p.get("nom", ""), _anneaux(f["geometry"])))
        elif p.get("type") == "ville":
            villes.append((p.get("nom", ""),
                           proj(*f["geometry"]["coordinates"][:2])))
    sections = [((f["properties"] or {}).get("section", ""),
                 _anneaux(f["geometry"])) for f in sec["features"]]

    # --- les trois cadrages
    # LES CADRAGES PARTENT D'ICI SANS FORMAT. C'est le navigateur qui connaît
    # la taille de la case où la carte est posée — elle change avec la largeur
    # de la fenêtre — et c'est donc lui qui étend chaque cadrage au format
    # utile. Le faire en Python obligeait à parier sur un format, et le pari
    # se voyait : une bande bleue à droite sur les écrans larges.
    tout = a_hti + a_dom
    c1 = _cadre(tout, proj, 0.06)
    c2 = _cadre([r for _n, rs in depts for r in rs], proj, 0.08) or c1
    c3 = _cadre([r for _n, rs in sections for r in rs], proj, 0.15)

    # --- les couches
    d_dom = _chemin(a_dom, proj, 45.0)
    d_hti = _chemin(a_hti, proj, 10.0)
    # LES LIMITES DE DÉPARTEMENT SONT UNE COUCHE, PAS UN LISERÉ. Le projet
    # travaille dans la Grand'Anse et le Sud : ces limites sont ce qui situe
    # les dix sections dans une géographie administrative que le lecteur
    # connaît. Elles sont donc tracées en tirets — la convention des limites
    # administratives — et restent visibles jusqu'au dernier cadrage.
    g_dept = "".join(
        f'<path d="{_chemin(rs, proj, 6.0)}" fill="{DEPT}" '
        f'fill-opacity=".5" stroke="{DEPT_TRAIT}" stroke-width="1.4" '
        f'stroke-dasharray="5 3.5" stroke-linejoin="round" '
        f'vector-effect="non-scaling-stroke"/>' for _n, rs in depts)
    g_sec = "".join(
        f'<path class="cz-s" data-nom="{i18n.echapper(nom) if hasattr(i18n, "echapper") else nom}" '
        f'd="{_chemin(rs, proj, 1.5)}" fill="{SECTION}" fill-opacity=".82" '
        f'stroke="{SECTION_TRAIT}" stroke-width="1.1" '
        f'vector-effect="non-scaling-stroke"/>' for nom, rs in sections)

    # --- les étiquettes, avec le cadrage où elles apparaissent
    etiq = []
    cx1 = _cadre(a_hti, proj, 0.0)
    if cx1:
        etiq.append({"t": T("cz_haiti"), "x": cx1[0] + cx1[2] * 0.30,
                     "y": cx1[1] + cx1[3] * 0.42, "e": 1, "c": "pays"})
    cxd = _cadre(a_dom, proj, 0.0) if a_dom else None
    if cxd:
        etiq.append({"t": T("cz_dom"), "x": cxd[0] + cxd[2] * 0.55,
                     "y": cxd[1] + cxd[3] * 0.45, "e": 1, "c": "pays"})
    for nom, rs in depts:
        c = _cadre(rs, proj, 0.0)
        if c:
            etiq.append({"t": nom.upper(), "x": c[0] + c[2] / 2,
                         "y": c[1] + c[3] / 2, "e": 2, "c": "dept"})
    for nom, pt in villes:
        etiq.append({"t": nom, "x": pt[0], "y": pt[1], "e": 2, "c": "ville"})
    for nom, rs in sections:
        c = _cadre(rs, proj, 0.0)
        if c:
            etiq.append({"t": nom, "x": c[0] + c[2] / 2,
                         "y": c[1] + c[3] / 2, "e": 3, "c": "sec"})

    g_villes = "".join(
        f'<circle class="cz-v" data-e="2" cx="{x:.1f}" cy="{y:.1f}" r="3" '
        f'fill="#fff" stroke="{ENCRE}" stroke-width="1.2" '
        f'vector-effect="non-scaling-stroke"/>' for _n, (x, y) in villes)

    cadres = json.dumps([c1, c2, c3])
    etiquettes = json.dumps(etiq, ensure_ascii=False)
    boutons = "".join(
        f'<button class="cz-b" data-e="{k}">{T(cle)}</button>'
        for k, cle in ((1, "cz_e1"), (2, "cz_e2"), (3, "cz_e3")))

    return f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
<style>
  :root {{ color-scheme: light; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; font-family:Inter,system-ui,-apple-system,sans-serif;
          background:transparent; }}
  html, body {{ height:100%; }}
  /* LA HAUTEUR EST DONNÉE, LA LARGEUR EST SUBIE. Le cadre de Streamlit a une
     hauteur fixe ; tant que la carte se dimensionnait sur sa largeur, elle
     dépassait ce cadre dès qu'on élargissait la fenêtre — à 2 560 pixels,
     elle demandait neuf cent dix pixels de haut pour six cent vingt
     disponibles, et les commandes se retrouvaient coupées. La carte prend
     donc la hauteur qui reste et s'étend en largeur. */
  .cz-cadre {{ background:#f4f7f5; border-radius:14px; padding:12px 14px 10px;
               overflow:hidden; height:100%; display:flex;
               flex-direction:column; }}
  .cz-zone {{ flex:1 1 auto; min-height:0; position:relative;
              border-radius:10px; overflow:hidden; background:{MER}; }}
  .cz-carte {{ position:absolute; inset:0; width:100%; height:100%;
               display:block; }}
  /* LES COMMANDES SONT SOUS LA CARTE, PAS DESSUS. Posées en surimpression
     elles auraient masqué la mer au nord de la péninsule, qui est
     précisément là où le regard part au premier cadrage. */
  .cz-cmd {{ display:flex; flex-wrap:wrap; gap:6px; align-items:center;
             margin:9px 0 0;
             /* AU-DESSUS DU DESSIN, sans discussion : une commande qu'un
                calque de carte recouvre d'un pixel ne répond plus. */
             position:relative; z-index:2; }}
  .cz-b {{ font:inherit; font-size:11.5px; font-weight:600; letter-spacing:.01em;
           color:{ENCRE}; background:#fff; border:1px solid #d7e0d9;
           border-radius:999px; padding:5px 11px; cursor:pointer;
           transition:background .15s, border-color .15s, color .15s; }}
  .cz-b:hover {{ background:#eaf2ec; border-color:#a9c8b5; }}
  .cz-b[aria-current="true"] {{ background:{SECTION}; border-color:{SECTION};
           color:#fff; }}
  .cz-r {{ margin-left:auto; }}
  .cz-s {{ transition:fill-opacity .15s; }}
  .cz-s:hover {{ fill-opacity:1; }}
  text {{ font-family:Inter,system-ui,sans-serif; paint-order:stroke;
          stroke:#fff; stroke-linejoin:round; }}
  .l-pays {{ fill:#6c7a8a; font-weight:700; letter-spacing:.18em; }}
  .l-dept {{ fill:#4a6555; font-weight:700; letter-spacing:.12em; }}
  .l-ville {{ fill:{ENCRE}; font-weight:600; }}
  .l-sec {{ fill:#0e3f2e; font-weight:700; }}
</style></head><body>
<div class="cz-cadre">
  <div class="cz-zone">
  <svg class="cz-carte" id="cz" viewBox="0 0 {LARG:.0f} {HAUT:.0f}"
       preserveAspectRatio="xMidYMid meet" role="img"
       aria-label="{T('cz_t')}">
    <g id="cz-monde">
      <path d="{d_dom}" fill="{TERRE_ETR}" stroke="#cfcbc2" stroke-width="1"
            vector-effect="non-scaling-stroke"/>
      <path d="{d_hti}" fill="{TERRE_HTI}" stroke="#b9c2b8" stroke-width="1.2"
            vector-effect="non-scaling-stroke"/>
      {g_dept}
      {g_sec}
      {g_villes}
      <g id="cz-fils"></g>
      <g id="cz-etiq"></g>
    </g>
  </svg>
  </div>
  <div class="cz-cmd">{boutons}
    <button class="cz-b cz-r" id="cz-boucle" aria-pressed="true"></button>
  </div>
</div>
<script>
(function () {{
  const BRUTS = {cadres};
  let CADRES = BRUTS.map(function (c) {{ return c.slice(); }});

  // ÉTENDRE UN CADRAGE AU FORMAT DE LA CASE. Un cadrage qui n'a pas ce
  // format est complété par le navigateur, et l'objet visé se retrouve
  // décentré d'autant. On l'étend autour de son propre centre, à chaque
  // changement de taille.
  function formater() {{
    const r = svg.getBoundingClientRect();
    const ratio = (r.width && r.height) ? r.width / r.height
                                        : {LARG:.0f} / {HAUT:.0f};
    svg.setAttribute('viewBox', '0 0 ' + {LARG:.0f} + ' '
                     + ({LARG:.0f} / ratio).toFixed(1));
    CADRES = BRUTS.map(function (c) {{
      let x = c[0], y = c[1], w = c[2], h = c[3];
      if (w / h < ratio) {{ const nw = h * ratio; x -= (nw - w) / 2; w = nw; }}
      else {{ const nh = w / ratio; y -= (nh - h) / 2; h = nh; }}
      return [x, y, w, h];
    }});
  }}
  const ETIQ = {etiquettes};
  const svg = document.getElementById('cz');
  const gEt = document.getElementById('cz-etiq');
  const fils = document.getElementById('cz-fils');
  const NS = 'http://www.w3.org/2000/svg';
  const doux = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // LES ÉTIQUETTES SONT DANS LE DESSIN, MAIS LEUR TAILLE N'EN EST PAS. Le
  // viewBox se resserre d'un facteur sept entre le premier et le
  // troisième cadrage : un texte dessiné à l'échelle de la carte y passerait
  // de illisible à énorme. Sa taille est donc recalculée à chaque image,
  // depuis l'échelle courante, ce qui la garde constante à l'écran.
  const TAILLE = {{ pays: 13, dept: 11, ville: 11.5, sec: 12 }};
  const noeuds = ETIQ.map(function (e) {{
    const t = document.createElementNS(NS, 'text');
    t.textContent = e.t;
    t.setAttribute('class', 'l-' + e.c);
    t.setAttribute('text-anchor', 'middle');
    t.setAttribute('x', e.x);
    t.setAttribute('y', e.y + (e.c === 'ville' ? -9 : 0));
    t.setAttribute('stroke-width', '3');
    t.style.opacity = '0';
    gEt.appendChild(t);
    return t;
  }});

  // CHAQUE FAMILLE D'ÉTIQUETTES A SA FENÊTRE. Les noms de pays ne servent
  // qu'au premier cadrage et gênent partout ailleurs ; les départements et
  // les deux villes, eux, doivent RESTER quand on descend sur les sections —
  // c'est ce qui dit au lecteur que Blactote est dans la Grand'Anse et
  // Trichet dans le Sud. Les noms de section, à l'inverse, n'apparaissent
  // qu'à l'approche, sans quoi ils s'empilent sur un point.
  function voile(classe, niv) {{
    if (classe === 'pays') {{
      const d = Math.abs(niv - 1);
      return d < 0.55 ? 1 - d / 0.55 : 0;
    }}
    if (classe === 'dept' || classe === 'ville') {{
      const a = classe === 'dept' ? 1.45 : 1.60;
      return niv <= a ? 0 : Math.min(1, (niv - a) / 0.45);
    }}
    const b = 2.35;
    return niv <= b ? 0 : Math.min(1, (niv - b) / 0.45);
  }}

  let vb = CADRES[0].slice();
  let etape = 1;

  function poser() {{
    svg.setAttribute('viewBox', vb.map(function (v) {{
      return v.toFixed(1); }}).join(' '));
    // Unités de carte par pixel d'écran : c'est ce rapport qui garde les
    // étiquettes à taille constante quand le cadrage se resserre.
    const k = vb[2] / Math.max(svg.getBoundingClientRect().width, 1);
    const niv = niveau();
    const visibles = [];
    noeuds.forEach(function (t, i) {{
      const e = ETIQ[i];
      t.setAttribute('font-size', (TAILLE[e.c] * k).toFixed(2));
      t.setAttribute('stroke-width', (2.6 * k).toFixed(2));
      // UNE ÉTIQUETTE PARAÎT À SON CADRAGE ET S'EFFACE APRÈS. Les dix noms de
      // section sur la vue de l'île seraient dix mots empilés sur un point ;
      // le nom du pays sur la vue des sections serait hors champ.
      t.style.opacity = String(voile(e.c, niv));
      t.setAttribute('x', e.x);
      t.setAttribute('y', e.y + (e.c === 'ville' ? -9 * k : 0));
      if (e.c === 'sec' && voile('sec', niv) > 0.05)
        visibles.push({{ t: t, e: e }});
    }});
    // CINQ SECTIONS SE TOUCHENT AU SUD-EST, ET LEURS NOMS SE SUPERPOSAIENT.
    // On les écarte le long de la verticale, du haut vers le bas, en gardant
    // une ligne de rappel vers la section quand l'écart devient visible :
    // une étiquette déplacée sans son fil ne désigne plus rien.
    visibles.sort(function (a, b) {{ return a.e.y - b.e.y; }});
    const ecart = 13.5 * k;
    let dernier = -1e9;
    while (fils.firstChild) fils.removeChild(fils.firstChild);
    visibles.forEach(function (v) {{
      let y = v.e.y;
      if (y - dernier < ecart) y = dernier + ecart;
      dernier = y;
      v.t.setAttribute('y', y);
      if (Math.abs(y - v.e.y) > 2 * k) {{
        const l = document.createElementNS(NS, 'line');
        l.setAttribute('x1', v.e.x); l.setAttribute('y1', v.e.y);
        l.setAttribute('x2', v.e.x); l.setAttribute('y2', y - 3.5 * k);
        l.setAttribute('stroke', '#0e3f2e');
        l.setAttribute('stroke-width', '1');
        l.setAttribute('vector-effect', 'non-scaling-stroke');
        l.setAttribute('opacity', v.t.style.opacity);
        fils.appendChild(l);
      }}
    }});
    document.querySelectorAll('.cz-v').forEach(function (c) {{
      c.setAttribute('r', (3 * k).toFixed(2));
      c.style.opacity = String(voile('ville', niv));
    }});
  }}

  // Le « niveau » est la position continue entre les trois cadrages, lue sur
  // la largeur du viewBox : c'est elle qui fait apparaître les étiquettes en
  // cours de route plutôt qu'à l'arrivée.
  function niveau() {{
    const l = Math.log(vb[2]);
    const a = Math.log(CADRES[0][2]), b = Math.log(CADRES[1][2]),
          c = Math.log(CADRES[2][2]);
    if (l >= b) return 1 + (a - l) / (a - b);
    return 2 + (b - l) / (b - c);
  }}

  function marquer(e) {{
    document.querySelectorAll('.cz-b[data-e]').forEach(function (b) {{
      b.setAttribute('aria-current', String(+b.dataset.e === e));
    }});
  }}

  let anim = null;
  function aller(e, ms, apres) {{
    const de = vb.slice(), vers = CADRES[e - 1];
    etape = e; marquer(e);
    if (anim) {{ cancelAnimationFrame(anim.id); anim = null; }}
    if (!doux || ms === 0) {{
      vb = vers.slice(); poser(); if (apres) apres(); return;
    }}
    const t0 = performance.now();
    anim = {{ id: 0 }};
    function pas(t) {{
      const u = Math.min(1, (t - t0) / ms);
      // Un fondu cubique aux deux bouts : le zoom démarre et s'arrête sans
      // saccade, ce qui est tout ce qu'on demande à une caméra.
      const f = u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2;
      for (let i = 0; i < 4; i++) vb[i] = de[i] + (vers[i] - de[i]) * f;
      poser();
      if (u < 1) {{ anim.id = requestAnimationFrame(pas); }}
      else {{ anim = null; if (apres) apres(); }}
    }}
    anim.id = requestAnimationFrame(pas);
  }}

  // --- LE DÉROULÉ TOURNE EN BOUCLE, ET LA BOUCLE S'ARRÊTE
  // Un cycle dure neuf secondes : quatre et demie de mouvement, quatre et
  // demie arrêté sur les dix sections. C'est ce temps d'arrêt qui compte —
  // une carte qui bouge sans cesse ne se lit pas, elle se subit.
  const CYCLE = 9000;
  let minuteurs = [];
  let boucle = true;

  function arreterMinuteurs() {{
    minuteurs.forEach(clearTimeout); minuteurs = [];
  }}

  function marquerBoucle() {{
    const b = document.getElementById('cz-boucle');
    b.innerHTML = boucle ? '&#9633; {T("cz_stop")}' : '&#9654; {T("cz_lire")}';
    b.setAttribute('aria-pressed', String(boucle));
  }}

  function cycle() {{
    arreterMinuteurs();
    // ELLE NE TOURNE PAS DANS LE VIDE. Onglet en arrière-plan ou carte
    // sortie de l'écran, le cycle passe son tour : le lecteur qui est en
    // train de lire les cartes du dessous n'a pas besoin qu'on lui rejoue
    // un zoom dans le coin de l'œil, et un onglet caché n'a pas besoin
    // qu'on l'anime.
    if (!document.hidden && visible) {{
      aller(1, 0);
      minuteurs.push(setTimeout(function () {{ aller(2, 1500); }}, 900));
      minuteurs.push(setTimeout(function () {{ aller(3, 1600); }}, 2900));
    }}
    if (boucle) minuteurs.push(setTimeout(cycle, CYCLE));
  }}

  // La carte est-elle à l'écran ? Sans `IntersectionObserver`, on suppose
  // que oui : mieux vaut une boucle qui tourne qu'une carte qui ne bouge
  // jamais.
  let visible = true;
  if (window.IntersectionObserver) {{
    new IntersectionObserver(function (es) {{
      visible = es[0].isIntersecting;
    }}, {{ threshold: 0.25 }}).observe(svg);
  }}

  document.querySelectorAll('.cz-b[data-e]').forEach(function (b) {{
    b.addEventListener('click', function () {{
      // PRENDRE LA MAIN, C'EST ARRÊTER LA BOUCLE. Sans cela, le cadrage
      // qu'on vient de demander serait balayé au tour suivant.
      boucle = false; marquerBoucle(); arreterMinuteurs();
      aller(+b.dataset.e, 900);
    }});
  }});

  document.getElementById('cz-boucle').addEventListener('click', function () {{
    boucle = !boucle;
    marquerBoucle();
    if (boucle) {{ cycle(); }} else {{ arreterMinuteurs(); }}
  }});

  formater();
  let taille = null;
  if (window.ResizeObserver) {{
    taille = new ResizeObserver(function () {{
      formater();
      const c = CADRES[etape - 1];
      for (let i = 0; i < 4; i++) vb[i] = c[i];
      poser();
    }});
    taille.observe(svg);
  }} else {{
    window.addEventListener('resize', function () {{
      formater();
      const c = CADRES[etape - 1];
      for (let i = 0; i < 4; i++) vb[i] = c[i];
      poser();
    }});
  }}

  vb = CADRES[0].slice();
  marquer(1); poser();
  // `prefers-reduced-motion` COUPE LA BOUCLE, PAS SEULEMENT LA TRANSITION.
  // Une carte qui se recadre toutes les quinze secondes est exactement ce
  // que ce réglage demande d'éviter : elle ouvre sur les sections et attend
  // qu'on la sollicite.
  if (doux) {{ cycle(); }} else {{ boucle = false; aller(3, 0); }}
  marquerBoucle();
}})();
</script></body></html>"""


def render(hauteur=560):
    """La carte animée, ou None si elle ne peut pas être composée.

    Rend True quand elle a été dessinée : l'appelant sait alors qu'il n'a pas
    à poser la carte fixe.
    """
    html = _composer(i18n.get_lang())
    if not html:
        return False
    components.html(html, height=hauteur, scrolling=False)
    return True
