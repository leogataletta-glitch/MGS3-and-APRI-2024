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
import re
import unicodedata

try:
    import i18n
except Exception:      # rendu hors application (export PNG)
    i18n = None


def _t(cle, **kw):
    return i18n.T(cle, **kw) if i18n else cle

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

# Échelle APRI des scores de résilience : onze classes, une par point de score,
# reprises telles quelles du référentiel « International comparative empirical
# scenarios » (0 = rouge, 10 = vert foncé). Les couleurs sont celles du document
# de référence ; l'encre noire garde un contraste d'au moins 4,5:1 sur chacune.
RAMP_APRI = [('#e9665d', '#0b0b0b'), ('#f39d76', '#0b0b0b'),
             ('#f9c082', '#0b0b0b'), ('#fcd486', '#0b0b0b'),
             ('#fded9a', '#0b0b0b'), ('#d3e3b7', '#0b0b0b'),
             ('#b1d094', '#0b0b0b'), ('#94c37f', '#0b0b0b'),
             ('#6bb672', '#0b0b0b'), ('#5b9c5a', '#0b0b0b'),
             ('#4c864f', '#0b0b0b')]
SEUILS_APRI = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5]

POLARITIES = ('eleve_mauvais', 'eleve_bon', 'neutre')


def ramp_for(polarity):
    if polarity == 'eleve_mauvais':
        return RAMP_SEVERITY                      # bas = vert, haut = rouge
    if polarity == 'eleve_bon':
        return RAMP_SEVERITY[::-1]                # bas = rouge, haut = vert
    return RAMP_NEUTRAL


def polarity_caption(polarity):
    if polarity == 'eleve_mauvais':
        return _t('cap_mauvais')
    if polarity == 'eleve_bon':
        return _t('cap_bon')
    return _t('cap_neutre')


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

INK, INK2, MUTED, SURFACE = '#0b0b0b', '#52514e', '#898781', '#ffffff'

# Gris ardoise des barres : 5,3:1 sur le fond clair, donc parfaitement lisible,
# et volontairement neutre — la couleur ne porte du sens que sur la carte.
BAR_COLOR = '#5b6b7a'


_ESPACE_MILLIERS = re.compile(r"(?<=\d)[\s  ](?=\d)")
_ZERO_DEBUT = ("aucun", "aucune", "moins de", "inférieur", "inferieur", "pas de")


def lower_bound(label):
    """Borne inférieure d'une modalité chiffrée, ou None si non chiffrée.

    Les modalités de l'enquête sont rarement des entiers purs : « 1-5 »,
    « 5 et plus », « Aucun », « Entre 25 et 50 », « Moins de 50 kg »,
    « 750-1 000 kg ». Attention aux formes « moins de X » / « inférieur à X »,
    dont la borne basse est 0 et non X.
    """
    s = _ESPACE_MILLIERS.sub("", str(label).strip().lower())
    if s.startswith(_ZERO_DEBUT):
        return 0
    m = re.search(r"\d+", s)
    return int(m.group()) if m else None


def is_ordinal(labels):
    """L'ensemble des modalités forme-t-il une échelle chiffrée exploitable ?"""
    bounds = [lower_bound(l) for l in labels]
    chiffrees = [b for b in bounds if b is not None]
    return len(chiffrees) >= 3 and len(set(chiffrees)) == len(chiffrees)


# Dégradé séquentiel d'une seule teinte (bleu), du clair au foncé : la
# valeur la plus forte porte la teinte la plus dense. Une seule teinte parce
# que les modalités d'une même question ne sont pas des catégories
# indépendantes — les colorier chacune d'une couleur différente inventerait
# une distinction qui n'existe pas.
RAMPE_BARRES = ['#a8cbe6', '#8bb8dd', '#6da3d0', '#5088bd', '#3a70a6',
                '#2a5b8c', '#1e4c7c']


def couleurs_barres(valeurs):
    """Une teinte par barre, d'autant plus dense que la valeur est forte."""
    if not valeurs:
        return {}
    vmax = max(valeurs.values()) or 1
    n = len(RAMPE_BARRES)
    return {k: RAMPE_BARRES[min(n - 1, int(v / vmax * (n - 1) + 1e-9))]
            for k, v in valeurs.items()}


def render_bars_svg(rows, base_total, width=880, color=BAR_COLOR):
    """Diagramme en barres horizontales, une barre par modalité.

    Pas d'axe ni de grille : la valeur est écrite au bout de chaque barre. Une
    graduation dense n'apporte rien quand chaque barre porte déjà son chiffre —
    elle ne fait qu'ajouter du bruit.

    Ordre des barres : sur une échelle chiffrée (0, 1, 2, 3… ou 1-5, 6-10…),
    on suit l'ordre de l'échelle, du plus petit au plus grand — trier par
    fréquence casserait la progression et rendrait la lecture fausse. Sur des
    catégories sans ordre naturel (types de toilettes, sources de revenus),
    on trie de la plus fréquente à la plus rare.
    """
    labels = [lab for lab, _ in rows]
    if is_ordinal(labels):
        data = sorted(rows, key=lambda r: (lower_bound(r[0]) is None,
                                           lower_bound(r[0]) or 0))
    else:
        data = sorted(rows, key=lambda r: -r[1])
    if not data or not base_total:
        return '<svg width="0" height="0"></svg>'

    BAR_H, GAP, LAB_W, VAL_W, TOP = 18, 10, 320, 62, 8
    # largeur moyenne d'un caractère à 13 px, estimée large pour ne jamais
    # laisser un libellé déborder du cadre (il serait rogné à gauche)
    MAX_CHARS = max(int((LAB_W - 14) / 6.9), 12)
    plot_w = max(width - LAB_W - VAL_W - 16, 60)
    vmax = max(max(n / base_total * 100 for _, n in data), 1e-9)
    height = TOP * 2 + len(data) * (BAR_H + GAP) - GAP

    teintes = couleurs_barres({lab: n / base_total * 100 for lab, n in data})
    _ARIA_BARRES = _t('aria_barres')

    parts = []
    y = TOP
    for lab, n in data:
        pct = n / base_total * 100
        w = max(plot_w * pct / vmax, 2)
        col = teintes.get(lab, color)
        short = lab if len(lab) <= MAX_CHARS else lab[:MAX_CHARS - 1] + '…'
        parts.append(
            f'<g><title>{lab} — {fmt_val(pct)} % ({n} ' + _t('foyers') + ')</title>'
            f'<text class="bl" x="{LAB_W - 10}" y="{y + BAR_H - 4.5}">{short}</text>'
            f'<rect class="br" x="{LAB_W}" y="{y}" width="{w:.1f}" height="{BAR_H}" '
            f'rx="5" fill="{col}"/>'
            f'<text class="bv" x="{LAB_W + w + 8:.1f}" y="{y + BAR_H - 4.5}">'
            f'{fmt_val(pct)} %</text></g>')
        y += BAR_H + GAP

    return f"""<svg viewBox="0 0 {width} {height}" width="100%"
     style="max-width:{width}px;display:block" role="img"
     aria-label="{_ARIA_BARRES}">
  <style>
    .bl{{font:13px system-ui,-apple-system,"Segoe UI",sans-serif;fill:{INK2};
        text-anchor:end}}
    .bv{{font:600 13px system-ui,-apple-system,"Segoe UI",sans-serif;fill:{INK};
        font-variant-numeric:tabular-nums}}
  </style>
  {''.join(parts)}
</svg>"""


def render_score_bars_svg(rows, vmax=10.0, width=880, unite='', colors=None,
                          annotations=None):
    """Barres horizontales pour des valeurs déjà calculées (score sur 10,
    pourcentage…). `rows` = [(libellé, valeur)], triées telles quelles par
    l'appelant. `colors` = {libellé: couleur} pour teinter chaque barre.
    """
    data = [(lab, v) for lab, v in rows if v is not None]
    if not data:
        return '<svg width="0" height="0"></svg>'

    BAR_H, GAP, LAB_W, VAL_W, TOP = 18, 10, 200, 62, 8
    MAX_CHARS = max(int((LAB_W - 14) / 6.9), 12)
    plot_w = max(width - LAB_W - VAL_W - 16, 60)
    vmax = max(vmax, max(v for _, v in data), 1e-9)
    height = TOP * 2 + len(data) * (BAR_H + GAP) - GAP

    _ARIA_CMP = _t('aria_comparaison')
    parts = []
    y = TOP
    for lab, v in data:
        w = max(plot_w * v / vmax, 2)
        col = (colors or {}).get(lab, BAR_COLOR)
        short = lab if len(lab) <= MAX_CHARS else lab[:MAX_CHARS - 1] + '…'
        note = (annotations or {}).get(lab, '')
        txt = f'{fmt_val(v)}{unite}'
        suite = (f'<tspan class="bn" dx="7">{note}</tspan>' if note else '')
        parts.append(
            f'<g><title>{lab} — {txt}{" · " + note if note else ""}</title>'
            f'<text class="bl" x="{LAB_W - 10}" y="{y + BAR_H - 4.5}">{short}</text>'
            f'<rect class="br" x="{LAB_W}" y="{y}" width="{w:.1f}" height="{BAR_H}" '
            f'rx="4" fill="{col}"/>'
            f'<text class="bv" x="{LAB_W + w + 8:.1f}" y="{y + BAR_H - 4.5}">'
            f'{txt}{suite}</text></g>')
        y += BAR_H + GAP

    return f"""<svg viewBox="0 0 {width} {height}" width="100%"
     style="max-width:{width}px;display:block" role="img"
     aria-label="{_ARIA_CMP}">
  <style>
    .bl{{font:13px system-ui,-apple-system,"Segoe UI",sans-serif;fill:{INK2};
        text-anchor:end}}
    .bv{{font:600 13px system-ui,-apple-system,"Segoe UI",sans-serif;fill:{INK};
        font-variant-numeric:tabular-nums}}
    .bn{{font:400 12.5px system-ui,-apple-system,"Segoe UI",sans-serif;fill:{INK2}}}
  </style>
  {''.join(parts)}
</svg>"""



# --------------------------------------------------------------------------
# Glossaire : les termes que le tableau de bord emploie et qui ne se devinent
# pas. Affichés dans une bulle au survol plutôt qu'en note de bas de page —
# la définition doit être là où le mot est lu.
# --------------------------------------------------------------------------
GLOSSAIRE = {
    'score APRI': (
        "Note de 0 à 10 attribuée à une section communale sur un indicateur, "
        "en appliquant le barème du cadre théorique IRLA / APRI. 0 = la "
        "situation la plus dégradée observée à l'échelle internationale, "
        "10 = la meilleure. Le passage de la mesure au score n'est pas "
        "linéaire : les classes basses du barème sont plus resserrées."),
    'pondération': (
        "Poids donné à un indicateur dans le score d'ensemble, repris tel quel "
        "du cadre théorique. Un indicateur pondéré 3,61 pèse trois fois plus "
        "qu'un indicateur pondéré 1,20 dans la moyenne."),
    'FIES': (
        "Food Insecurity Experience Scale — échelle d'expérience de "
        "l'insécurité alimentaire. Mesure ici la part de foyers déclarant "
        "avoir manqué de nourriture au cours des douze derniers mois."),
    'assainissement amélioré': (
        "Toilettes qui séparent les excreta du contact humain : chasse d'eau "
        "raccordée à un égout ou une fosse septique, latrine ventilée "
        "améliorée, latrine à fosse avec dalle, toilettes à compostage. Sont "
        "exclues les latrines sans dalle, les seaux et la défécation à l'air "
        "libre."),
    'eau améliorée': (
        "Source d'eau de boisson protégée de la contamination extérieure : "
        "réseau, forage, puits creusé protégé, source protégée, eau de pluie, "
        "kiosque, eau en bouteille ou en sachet. Sont exclues les eaux de "
        "surface et les puits ou sources non protégés."),
    'Cat A': "Catégorie économique A — foyers en situation de pauvreté extrême.",
    'Cat B': "Catégorie économique B — foyers en situation de pauvreté.",
    'Cat C': "Catégorie économique C — foyers non considérés comme pauvres.",
    'paysage': (
        "Milieu dans lequel se trouve la section communale : littoral (ou "
        "plaine côtière) ou montagne. Chaque section relève d'un seul des "
        "deux."),
    'section communale': (
        "Plus petite division administrative haïtienne, sous la commune. "
        "L'enquête en couvre dix, dans les départements du Sud et de la "
        "Grand'Anse."),
    'mesure brute': (
        "Le pourcentage de foyers réellement mesuré sur le terrain, avant "
        "toute conversion en score. C'est ce chiffre qui décrit la situation ; "
        "le score dit seulement où il se situe sur l'échelle de comparaison."),
    'indépendance': (
        "Ce que vaudrait le cumul de plusieurs conditions si elles frappaient "
        "des foyers sans rapport entre eux — le simple produit des taux. Un "
        "cumul observé supérieur signifie que les situations se concentrent "
        "sur les mêmes foyers."),
    'base': (
        "Nombre de répondants sur lequel un pourcentage est calculé. Sous "
        "trente répondants, l'ordre de grandeur reste utilisable mais le "
        "chiffre exact ne l'est pas."),
    'réponses multiples': (
        "Question où un même foyer peut cocher plusieurs réponses. Les "
        "pourcentages ne totalisent alors pas 100 %, et cumuler deux réponses "
        "compte deux fois les foyers qui ont coché les deux."),
}


def bulle_notion(cle, texte=None):
    """Bulle alimentée par les notions de l'article IRLA."""
    if i18n is None:
        return texte or cle
    terme, defi = i18n.notion(cle)
    if not defi:
        return texte or cle
    return bulle(cle, definition=defi, texte=texte if texte is not None else terme)


def bulle(terme, definition=None, texte=None):
    """Un terme suivi d'un « ? » qui révèle sa définition au survol.

    La définition vient du glossaire si elle n'est pas fournie. Rendu en HTML
    pur (pas de JavaScript) : la bulle est un simple frère en position
    absolue, affiché au survol du conteneur.
    """
    d = definition or (i18n.definition(terme) if i18n else GLOSSAIRE.get(terme, ''))
    # texte='' est un choix délibéré : la pastille seule, sans mot répété.
    libelle = ((i18n.terme(terme) if i18n else terme)
               if texte is None else texte)
    if not d:
        return libelle
    d = d.replace('"', '&quot;')
    return (
        f'<span style="position:relative;display:inline-block" '
        f'class="bulle-hote">{libelle}'
        f'<span class="bulle-marque">?</span>'
        f'<span class="bulle-texte">{d}</span></span>')


def styles_bulle():
    """Feuille de style des bulles — à injecter une fois par page."""
    return """<style>
      .bulle-marque {
        display:inline-flex;align-items:center;justify-content:center;
        width:15px;height:15px;margin-left:5px;border-radius:50%;
        background:#e3eefa;color:#1a6bb0;font-size:10.5px;font-weight:700;
        vertical-align:middle;cursor:help;transition:background .15s ease;
      }
      .bulle-hote:hover .bulle-marque { background:#1a6bb0;color:#fff; }
      .bulle-texte {
        visibility:hidden;opacity:0;position:absolute;z-index:999;
        bottom:calc(100% + 9px);left:50%;transform:translateX(-50%) translateY(4px);
        width:330px;max-width:80vw;background:#101728;color:#f2f5fa;
        font-size:12.5px;font-weight:400;line-height:1.5;letter-spacing:0;
        text-transform:none;padding:11px 14px;border-radius:10px;
        box-shadow:0 10px 30px rgba(16,23,40,.28);
        transition:opacity .16s ease, transform .16s ease, visibility .16s;
      }
      .bulle-texte::after {
        content:"";position:absolute;top:100%;left:50%;margin-left:-6px;
        border:6px solid transparent;border-top-color:#101728;
      }
      .bulle-hote:hover .bulle-texte {
        visibility:visible;opacity:1;transform:translateX(-50%) translateY(0);
      }
    </style>"""


# --------------------------------------------------------------------------
def cartouche_html(libelle, valeur, unite='%', sous_titre='',
                   valeur2=None, unite2='', sous_titre2='', couleur='#5b6b7a'):
    """Un chiffre mis en page comme dans une publication, pas comme un widget.

    Pas de boîte colorée : un filet en haut, une pastille de couleur qui porte
    l'information de classe (score APRI, sens de lecture), et le chiffre en
    grande serif. Sert aux trois onglets — pourcentage de foyers, score de
    résilience, effectif d'un croisement. Le HTML tient sur une seule ligne :
    Streamlit bascule en bloc de code dès qu'une ligne commence par quatre
    espaces.
    """
    def _bloc(v, u, note, taille):
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            txt = str(v)
            # Un cartouche est dimensionné pour un NOMBRE. Quand on y met un
            # nom — « II. Institutions et gouvernance » — les 46 px le
            # coupent au milieu d'un mot. On rétrécit donc la casse à mesure
            # que le texte s'allonge, au lieu de laisser la boîte se déformer.
            # Les paliers sont calés sur la colonne la plus étroite où ce
            # cartouche est utilisé : un quart de la largeur de contenu, soit
            # environ 200 px de texte utile. « Mouline » — sept caractères,
            # dont un M large — y débordait encore à pleine casse et se
            # coupait en « Moulin / e ». D'où le palier à six caractères : dès
            # qu'un nom apparaît à la place d'un nombre, on rétrécit.
            if len(txt) > 26:
                taille = max(17, int(taille * 0.40))
            elif len(txt) > 16:
                taille = max(20, int(taille * 0.50))
            elif len(txt) > 10:
                taille = max(24, int(taille * 0.62))
            elif len(txt) > 6:
                taille = max(28, int(taille * 0.78))
        elif isinstance(v, int):
            # Un effectif s'écrit sans décimale : « 627 », pas « 627,0 ».
            txt = f'{int(v):,}'.replace(',', '\u202f')
        else:
            txt = fmt_val(v)
        return (f'<div style="font-family:Inter,system-ui,sans-serif;'
                f'font-size:{taille}px;font-weight:600;color:{INK};'
                f'line-height:1.05;font-variant-numeric:tabular-nums;'
                f'letter-spacing:-0.02em;overflow-wrap:break-word;'
                f'word-break:normal;hyphens:auto">{txt}'
                f'<span style="font-size:{max(15, int(taille * 0.42))}px;'
                f'font-weight:400;color:{MUTED};letter-spacing:0"> {u}</span></div>'
                f'<div style="font-size:11.5px;color:{INK2};margin-top:3px;'
                f'line-height:1.4">{note}</div>')

    haut = _bloc(valeur, unite, sous_titre, 46 if valeur2 is None else 38)
    bas = ''
    if valeur2 is not None:
        bas = ('<div style="height:1px;background:#e4e3de;margin:13px 0 11px"></div>'
               + _bloc(valeur2, unite2, sous_titre2, 33))
    return (f'<div style="background:#ffffff;border:1px solid #e3eaf3;'
            f'border-top:4px solid {couleur};border-radius:14px;'
            f'box-shadow:0 1px 2px rgba(16,23,40,.05),0 8px 20px rgba(16,23,40,.06);'
            f'padding:15px 18px 16px;height:100%">'
            f'<div style="font-size:11px;color:{MUTED};letter-spacing:.11em;'
            f'text-transform:uppercase;font-weight:700;margin-bottom:11px;'
            f'min-height:28px;line-height:1.35">{libelle}</div>'
            f'{haut}{bas}</div>')


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
    """Indice de classe : 0 si v < T[0], puis une classe par seuil franchi.
    Fonctionne avec 3 seuils (4 classes) comme avec 10 (échelle APRI 0-10)."""
    i = 0
    for t in T:
        if v < t:
            return i
        i += 1
    return i


def legend_items(T, polarity='neutre', unite='%'):
    R = ramp_for(polarity)
    u = f' {unite}' if unite else ''
    return [(R[0][0], _t('moins_de', v=fmt(T[0]), u=u)),
            (R[1][0], _t('intervalle', a=fmt(T[0]), b=fmt(T[1]), u=u)),
            (R[2][0], _t('intervalle', a=fmt(T[1]), b=fmt(T[2]), u=u)),
            (R[3][0], _t('et_plus', v=fmt(T[2]), u=u))]


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
                   polarity='neutre', unite='%', ramp=None, infos=None,
                   points=None):
    """values : {section: valeur}. `unite` est le suffixe écrit sur la carte
    ('%' pour un pourcentage, '' pour un score sur 10).

    `points` permet de semer des marqueurs par-dessus les sections :
    [(lon, lat, rayon_px, couleur, titre), ...]. La projection vit ici, donc
    l'appelant fournit des degrés et n'a rien à savoir du cadrage.

    Retourne (svg, thresholds, mode)."""
    T = thresholds or nice_thresholds(list(values.values()))
    RAMP = ramp or ramp_for(polarity)
    INFOS = infos or {}          # {section: texte ajouté à l'infobulle}
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
            tip = (f'{name} — {fmt_val(v)}{" " + unite if unite else ""}'
                   + (f' · {INFOS[name]}' if name in INFOS else '')
                   + ' (' + _t('base_carte', n=base_n.get(name, 0)) + ')' 
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
                    f'<title>{name} — {fmt_val(v)}{" " + unite if unite else ""}'
                    + (f' · {INFOS[name]}' if name in INFOS else '')
                    + ' (' + _t('base_carte', n=base_n.get(name, 0))
                    + ')</title></circle>' 
                    f'<text class="pv" x="{cx:.1f}" y="{cy + 6:.1f}" fill="{ink}">'
                    f'{fmt_val(v)}{unite}</text>')
            label_anchor[name] = (cx, cy)

    # ---- marqueurs semés sur la carte ----
    # Dessinés APRÈS les sections et AVANT les étiquettes : ils doivent couvrir
    # l'aplat de couleur, mais jamais le nom d'une section ni son chiffre.
    if points:
        for lon, lat, r, coul, titre in points:
            px, py = proj(lon * kx, lat)
            if not (0 <= px <= width and 0 <= py <= height):
                continue
            body.append(
                f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.2f}" '
                f'fill="{coul}" fill-opacity="0.82" stroke="#ffffff" '
                f'stroke-width="0.4" stroke-opacity="0.5">'
                f'<title>{titre}</title></circle>')

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
            txt = f'{fmt_val(v)}{unite}'
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
            # UN POINT MÉDIAN, PAS UN TIRET CADRATIN. Le tiret long entre un
            # nom et un nombre se lisait comme une incise ; le point médian
            # sépare sans rien annoncer, et c'est le séparateur déjà employé
            # dans les cartouches et les légendes du site.
            return (f'{name} · {fmt_val(v)}{unite}' if v is not None
                    else f'{name} · n.d.')
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
              f'<text class="ct2" x="{46 + bar / 2:.0f}" y="{height - 22}">'
              + _t('km') + '</text>')

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
