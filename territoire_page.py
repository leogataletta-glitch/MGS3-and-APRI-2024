"""Le territoire — où l'enquête a eu lieu, et à quoi il ressemble.

CE QUE CETTE PAGE REMPLACE, ET POURQUOI

L'accueil ouvrait sur quatre paragraphes de récit et une barre de filtres. Le
récit était juste mais personne ne le lisait : arriver sur un mur de prose ne
donne pas envie d'entrer. Quant aux filtres, ils n'avaient rien à commander —
une page de présentation ne se filtre pas.

Ce qui manquait était plus simple, et c'est tout ce que la page fait
désormais : DIRE OÙ L'ON EST. Deux cartes, et rien d'autre.

AUCUNE DONNÉE D'ANALYSE ICI, ET C'EST UNE RÈGLE, PAS UN OUBLI. Pas de score,
pas d'indicateur, pas de pourcentage, pas de classement, pas même un effectif.
Une carte qui porte des couleurs de résultat répond à « combien » avant d'avoir
répondu à « où », et le lecteur qui cherchait simplement à se situer repart
avec un chiffre qu'il n'a pas demandé. Les résultats vivent dans les autres
rubriques, où ils sont attendus.

LES DEUX CARTES NE FONT PAS LE MÊME TRAVAIL

  · LA VIGNETTE situe. Elle montre le pays entier, la zone enquêtée en
    couleur, et rien d'autre — pas de valeur, pas d'échelle de couleur. Sa
    seule question est « où ? ».
  · LA CARTE DE SITUATION nomme. Les dix sections, leurs limites, les trois
    départements et les deux villes-repères. Sa question est « laquelle ? ».

Une carte qui répond à deux questions à la fois n'en répond bien à aucune :
c'est pour cela qu'elles sont deux, et qu'aucune ne porte de valeur.

LA PROJECTION EST FAITE ICI, VOLONTAIREMENT SIMPLE. Équirectangulaire, avec la
longitude corrigée du cosinus de la latitude moyenne — à cette échelle et sous
cette latitude, la déformation est invisible, et cela évite d'embarquer une
bibliothèque cartographique pour dessiner deux contours.
"""

import json
import math
import os

import streamlit as st
import streamlit.components.v1 as components

import carte_localisation
import i18n
import map_render
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"
VERT_APRI = "#2a6b3f"
MER = "#e8eef6"
TERRE = "#f1f3f0"
TRAIT = "#c9cfd8"

SECTIONS = ["Anse à Drick", "Barbois", "Dumont", "Débouchette", "Mouline",
            "Quentin", "Beaulieu", "Blactote", "Dalmette", "Trichet"]

TEXTES = {
    "tr_titre": {"en": "The territory", "fr": "Le territoire"},
    "tr_sous_titre": {
        "en": "Where the studied territories are",
        "fr": "Où se situent les territoires étudiés"},
    "tr_vignette": {"en": "Where it is", "fr": "Où c'est"},
    "tr_vignette_note": {
        "en": "Haiti in full; the surveyed area in green, in the far "
              "south-west of the country.",
        "fr": "Haïti en entier ; la zone enquêtée en vert, à l'extrême "
              "sud-ouest du pays."},
    "tr_situation": {"en": "The ten communal sections",
                     "fr": "Les dix sections communales"},
    "tr_situation_note": {
        "en": "Departmental boundaries dashed, the two reference towns marked. "
              "Each section carries its name; hover for its commune and "
              "department.",
        "fr": "Limites départementales en tirets, les deux villes-repères "
              "marquées. Chaque section porte son nom ; au survol, sa commune "
              "et son département."},
    "tr_liste": {"en": "Section by section", "fr": "Section par section"},
    "tr_c_section": {"en": "Communal section", "fr": "Section communale"},
    "tr_c_commune": {"en": "Commune", "fr": "Commune"},
    "tr_c_dep": {"en": "Department", "fr": "Département"},
    "tr_c_pays": {"en": "Landscape", "fr": "Paysage"},
    "tr_c_men": {"en": "Households surveyed", "fr": "Ménages enquêtés"},
    "tr_carte_score": {"en": "And where it holds up least well",
                       "fr": "Et où il tient le moins bien"},
    "tr_absent": {"en": "Map files missing.",
                  "fr": "Les fichiers cartographiques sont absents."},
    # --- la carte d'atelier des entretiens, sous la carte interactive
    "tr_qgis2": {"en": "Where the interviews were conducted",
                 "fr": "Où les entretiens ont été conduits"},
    "tr_qgis2_note": {
        "en": "Interviews carried out by FNGA (Mouline), PADI (Dumont, "
              "Barbois, Anse-à-Drick), MDE/DDS (Débouchette, Trichet), DDAS "
              "(Beaulieu, Quentin) and ORE (Blactote, Dalmette), against "
              "relief, rivers and roads.",
        "fr": "Les entretiens conduits par la FNGA (Mouline), PADI (Dumont, "
              "Barbois, Anse-à-Drick), MDE/DDS (Débouchette, Trichet), la DDAS "
              "(Beaulieu, Quentin) et ORE (Blactote, Dalmette), rapportés au "
              "relief, aux rivières et aux routes."},
    "tr_qgis2_meta": {
        "en": "Scale 1:250 000 · WGS 84 (EPSG:4326) · Sources OSM / HumData · "
              "GIS processing QGIS · Florent Léo, UNEP Haiti · March 2026",
        "fr": "Échelle 1:250 000 · WGS 84 (EPSG:4326) · Sources OSM / HumData · "
              "Traitements SIG QGIS · Florent Léo, PNUE Haïti · mars 2026"},
    "tr_l_sym": {"en": "Map symbols", "fr": "Symboles de la carte"},
    "tr_l_alt": {"en": "Elevation", "fr": "Altitude"},
    "tr_l_capitale": {"en": "Departmental capital",
                      "fr": "Capitale départementale"},
    "tr_l_riv": {"en": "Rivers", "fr": "Rivières"},
    "tr_l_ent_m": {"en": "Interviews, mountain", "fr": "Entretiens montagne"},
    "tr_l_ent_l": {"en": "Interviews, coast", "fr": "Entretiens littoral"},
    "tr_l_sec": {"en": "Communal section", "fr": "Section communale"},
    "tr_l_dep": {"en": "Departments", "fr": "Départements"},
    "tr_l_reseau": {"en": "Road network", "fr": "Réseau routier"},
    "tr_l_ocean": {"en": "Ocean", "fr": "Océan"},
    "tr_absent2": {"en": "Map image missing.", "fr": "Image de carte absente."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _trouver(nom):
    for c in (os.path.join(DATA, nom), os.path.join(APP_DIR, nom)):
        if os.path.exists(c):
            return c
    return None


def _anneaux(geom):
    """Les anneaux extérieurs d'une géométrie, polygone ou multipolygone."""
    t = (geom or {}).get("type")
    if t == "MultiPolygon":
        return [poly[0] for poly in geom.get("coordinates", []) if poly]
    if t == "Polygon":
        c = geom.get("coordinates") or []
        return [c[0]] if c else []
    return []


@st.cache_data(show_spinner=False)
def _geo():
    """Contour du pays, départements, villes et sections — une seule lecture."""
    out = {"pays": [], "voisin": [], "deps": [], "villes": [], "sections": []}
    # LE VOISIN EST LU À PART, ET IL PEUT MANQUER. Le contour dominicain a été
    # ajouté après coup ; les cartes doivent continuer de se dessiner sans lui
    # si le fichier n'est pas là.
    q = _trouver("dom_terre.geojson")
    if q:
        with open(q, encoding="utf-8") as f:
            for feat in json.load(f).get("features", []):
                out["voisin"] += _anneaux(feat.get("geometry"))
    p = _trouver("hti_terre.geojson")
    if p:
        with open(p, encoding="utf-8") as f:
            for feat in json.load(f).get("features", []):
                out["pays"] += _anneaux(feat.get("geometry"))
    p = _trouver("contexte_geo.geojson")
    if p:
        with open(p, encoding="utf-8") as f:
            for feat in json.load(f).get("features", []):
                pr = feat.get("properties") or {}
                if pr.get("type") == "departement":
                    out["deps"].append((pr.get("nom", ""),
                                        _anneaux(feat.get("geometry"))))
                elif pr.get("type") == "ville":
                    out["villes"].append((pr.get("nom", ""),
                                          (feat.get("geometry") or {})
                                          .get("coordinates")))
    p = _trouver("sections_communales.geojson")
    if p:
        with open(p, encoding="utf-8") as f:
            for feat in json.load(f).get("features", []):
                pr = feat.get("properties") or {}
                out["sections"].append({
                    "nom": pr.get("section") or pr.get("nom_cnigs") or "",
                    "commune": pr.get("commune") or "",
                    "departement": pr.get("departement") or "",
                    "anneaux": _anneaux(feat.get("geometry"))})
    return out


class _Proj:
    """Projection équirectangulaire ajustée à une boîte, en pixels SVG."""

    def __init__(self, anneaux, larg, haut, marge=8):
        pts = [p for r in anneaux for p in r]
        lat_moy = sum(p[1] for p in pts) / len(pts)
        self.k = math.cos(math.radians(lat_moy))
        xs = [p[0] * self.k for p in pts]
        ys = [p[1] for p in pts]
        self.x0, self.x1 = min(xs), max(xs)
        self.y0, self.y1 = min(ys), max(ys)
        dx, dy = (self.x1 - self.x0) or 1e-9, (self.y1 - self.y0) or 1e-9
        self.s = min((larg - 2 * marge) / dx, (haut - 2 * marge) / dy)
        # Centrage : la carte occupe le milieu de la toile, quel que soit son
        # rapport de forme.
        self.ox = (larg - dx * self.s) / 2
        self.oy = (haut - dy * self.s) / 2

    def xy(self, lon, lat):
        return (self.ox + (lon * self.k - self.x0) * self.s,
                self.oy + (self.y1 - lat) * self.s)

    def chemin(self, anneau):
        d = []
        for i, (lon, lat) in enumerate(anneau):
            x, y = self.xy(lon, lat)
            d.append(f'{"M" if i == 0 else "L"}{x:.1f} {y:.1f}')
        return "".join(d) + "Z"


def _plus_large(anneaux, pr, essais=90, evite=None):
    """Le milieu du plus long segment horizontal intérieur au contour.

    On balaie la hauteur par tranches, on croise chaque tranche avec toutes
    les arêtes, on trie les abscisses obtenues et on lit les intervalles deux
    par deux — la règle pair-impair, qui gère seule les trous et les îles.
    Le plus long de ces intervalles est le meilleur endroit pour poser un mot :
    il est intérieur par construction, et c'est là qu'il y a le plus de place.
    """
    pts = [pr.xy(lon, lat) for a in anneaux for lon, lat in a]
    if not pts:
        return None, None
    y0 = min(p[1] for p in pts)
    y1 = max(p[1] for p in pts)
    if y1 - y0 < 4:
        return None, None
    aretes = []
    for a in anneaux:
        proj = [pr.xy(lon, lat) for lon, lat in a]
        for i in range(len(proj)):
            aretes.append((proj[i - 1], proj[i]))
    meilleur = (0, None, None)
    for k in range(1, essais):
        y = y0 + (y1 - y0) * k / essais
        # ON N'ÉCRIT PAS SUR LE SUJET. La bande de hauteur occupée par la zone
        # enquêtée est écartée du balayage : la presqu'île du sud est le plus
        # long segment du pays, et le nom du pays serait venu se poser
        # exactement sur le cercle qu'on cherche à montrer.
        if evite and evite[0] <= y <= evite[1]:
            continue
        xs_ = []
        for (xa, ya), (xb, yb) in aretes:
            if (ya > y) != (yb > y) and yb != ya:
                xs_.append(xa + (y - ya) * (xb - xa) / (yb - ya))
        xs_.sort()
        for i in range(0, len(xs_) - 1, 2):
            large = xs_[i + 1] - xs_[i]
            if large > meilleur[0]:
                meilleur = (large, (xs_[i] + xs_[i + 1]) / 2, y)
    if meilleur[1] is None:
        return None, None
    return meilleur[1], meilleur[2] + 4


def _vignette(geo, larg=300, haut=330, mer=None):
    """L'île entière, la zone enquêtée en vert, le voisin nommé.

    HAÏTI SEULE FLOTTAIT SANS REPÈRE. Découpée sur un fond uni, la silhouette
    du pays ne dit pas qu'elle est la moitié d'une île : le lecteur qui ne
    connaît pas la région voit une forme, pas un lieu. La République
    dominicaine, dessinée en retrait et nommée, rend la frontière lisible et
    situe le pays d'un coup d'œil. Elle est en gris clair et sans contour
    marqué : elle sert de contexte, elle n'entre pas en concurrence avec le
    sujet.
    """
    if not geo["pays"] or not geo["sections"]:
        return None
    # LA PROJECTION EST CALÉE SUR L'ÎLE, PAS SUR HAÏTI. Cadrer sur Haïti seule
    # rejetterait le voisin hors de la vignette, et le repère disparaîtrait.
    pr = _Proj(geo["pays"] + geo.get("voisin", []), larg, haut)
    # LA MER PEUT ÊTRE PÂLIE PAR L'APPELANT. Sur la page d'accueil, le bleu
    # gris de la carte du territoire formait un rectangle plein au milieu
    # d'une page qu'on venait de débarrasser de ses boîtes : le fond y est
    # presque blanc, et seule l'île se voit.
    parts = [f'<rect width="{larg}" height="{haut}" fill="{mer or MER}"/>']
    for a in geo.get("voisin", []):
        parts.append(f'<path d="{pr.chemin(a)}" fill="#e9edf2" '
                     f'stroke="#dde3ea" stroke-width=".8"/>')
    for a in geo["pays"]:
        parts.append(f'<path d="{pr.chemin(a)}" fill="{TERRE}" '
                     f'stroke="{TRAIT}" stroke-width="1"/>')
    for _nom, anneaux in geo["deps"]:
        for a in anneaux:
            parts.append(f'<path d="{pr.chemin(a)}" fill="none" '
                         f'stroke="#dfe4ea" stroke-width=".8"/>')
    xs, ys = [], []
    for s_ in geo["sections"]:
        for a in s_["anneaux"]:
            parts.append(f'<path d="{pr.chemin(a)}" fill="{VERT_APRI}" '
                         f'stroke="{VERT_APRI}" stroke-width="1.2"/>')
            for lon, lat in a:
                x, y = pr.xy(lon, lat)
                xs.append(x)
                ys.append(y)
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    r = max(max(xs) - min(xs), max(ys) - min(ys)) / 2 + 12
    parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
                 f'fill="none" stroke="{VERT_APRI}" stroke-width="1.6" '
                 f'stroke-dasharray="4 3" opacity=".9"/>')

    # LE NOM DU PAYS SE POSE SUR LE PAYS, PAS DANS L'OCÉAN. Il était écrit au
    # coin haut-gauche de la vignette, c'est-à-dire en pleine mer, pendant que
    # le voisin, lui, portait son nom sur ses terres. On cherche donc le plus
    # long segment horizontal entièrement à l'intérieur du contour et on y
    # centre le mot : sur une forme en fer à cheval comme Haïti, le centre de
    # gravité tomberait dans le golfe de la Gonâve.
    hx, hy = _plus_large(geo["pays"], pr,
                         evite=(cy - r - 6, cy + r + 6))
    if hx is None:
        hx, hy = 12, 20
        ancre = "start"
    else:
        ancre = "middle"
    parts.append(f'<text x="{hx:.0f}" y="{hy:.0f}" text-anchor="{ancre}" '
                 f'font-size="12" font-weight="700" '
                 f'fill="#6b7a88" letter-spacing="2">HAÏTI</text>')
    if geo.get("voisin"):
        vx = [pr.xy(lon, lat)[0] for a in geo["voisin"] for lon, lat in a]
        vy = [pr.xy(lon, lat)[1] for a in geo["voisin"] for lon, lat in a]
        parts.append(
            f'<text x="{(min(vx) + max(vx)) / 2:.0f}" '
            f'y="{(min(vy) + max(vy)) / 2:.0f}" text-anchor="middle" '
            f'font-size="9" font-weight="700" fill="#a7b0bb" '
            f'letter-spacing="1.4">RÉPUBLIQUE</text>'
            f'<text x="{(min(vx) + max(vx)) / 2:.0f}" '
            f'y="{(min(vy) + max(vy)) / 2 + 12:.0f}" text-anchor="middle" '
            f'font-size="9" font-weight="700" fill="#a7b0bb" '
            f'letter-spacing="1.4">DOMINICAINE</text>')
    return (f'<svg viewBox="0 0 {larg} {haut}" width="100%" '
            f'style="max-width:{larg}px;display:block;border-radius:10px;'
            f'border:1px solid #e6ecf4" '
            f'font-family="Inter,system-ui,sans-serif">'
            + "".join(parts) + '</svg>')


def _situation(geo, larg=880, haut=560):
    """La zone, nommée : sections, départements, villes-repères."""
    if not geo["sections"]:
        return None
    tous = [a for s in geo["sections"] for a in s["anneaux"]]
    pr = _Proj(tous, larg, haut, marge=54)
    parts = [f'<rect width="{larg}" height="{haut}" fill="{MER}"/>']
    for a in geo["pays"]:
        parts.append(f'<path d="{pr.chemin(a)}" fill="{TERRE}" '
                     f'stroke="{TRAIT}" stroke-width="1"/>')
    for nom, anneaux in geo["deps"]:
        for a in anneaux:
            parts.append(f'<path d="{pr.chemin(a)}" fill="none" '
                         f'stroke="#b9c2cd" stroke-width="1.1" '
                         f'stroke-dasharray="6 4"/>')
    # Une teinte par département : c'est le regroupement que le lecteur
    # cherche des yeux, et il ne porte aucune valeur.
    teintes = {}
    palette = ["#2a6b3f", "#1a6bb0", "#7048b6"]
    for s in geo["sections"]:
        d = s["departement"] or ""
        if d not in teintes:
            teintes[d] = palette[len(teintes) % len(palette)]
    etiquettes = []
    for s in geo["sections"]:
        c = teintes.get(s["departement"] or "", VERT_APRI)
        for a in s["anneaux"]:
            parts.append(
                f'<path d="{pr.chemin(a)}" fill="{c}" fill-opacity=".72" '
                f'stroke="#ffffff" stroke-width="1.2">'
                f'<title>{_e(s["nom"])} — {_e(s["commune"])}, '
                f'{_e(s["departement"])}</title></path>')
        pts = [p for a in s["anneaux"] for p in a]
        if pts:
            cx = sum(p[0] for p in pts) / len(pts)
            cy = sum(p[1] for p in pts) / len(pts)
            etiquettes.append((pr.xy(cx, cy), s["nom"]))
    # DÉSEMPILEMENT DES ÉTIQUETTES. Cinq sections se touchent dans le coin
    # sud-est ; posées à leur centre, leurs noms se recouvraient et deux
    # d'entre eux devenaient illisibles. On les parcourt du nord au sud et on
    # décale vers le bas celles qui tomberaient sur la précédente — un
    # décalage vertical se lit encore comme « ce nom appartient à cette
    # tache », ce qui n'est plus vrai d'un nom déplacé latéralement.
    etiquettes.sort(key=lambda e: e[0][1])
    posees = []
    for (x, y), nom in etiquettes:
        for px, py in posees:
            if abs(x - px) < 78 and abs(y - py) < 14:
                y = py + 14
        posees.append((x, y))
        parts.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
            f'font-size="11" font-weight="700" fill="#ffffff" '
            f'stroke="#00000066" stroke-width="2.8" paint-order="stroke">'
            f'{_e(nom)}</text>')

    for nom, coords in geo["villes"]:
        if not coords:
            continue
        x, y = pr.xy(coords[0], coords[1])
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" '
                     f'fill="#ffffff" stroke="{ENCRE2}" stroke-width="1.6"/>')
        parts.append(f'<text x="{x + 7:.1f}" y="{y + 4:.1f}" font-size="11.5" '
                     f'fill="{ENCRE2}">{_e(nom)}</text>')
    for nom, anneaux in geo["deps"]:
        pts = [p for a in anneaux for p in a]
        if not pts:
            continue
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        x, y = pr.xy(cx, cy)
        if 0 < x < larg and 0 < y < haut:
            parts.append(
                f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
                f'font-size="12" font-weight="700" fill="#9aa4b5" '
                f'letter-spacing="2.5">{_e(nom.upper())}</text>')
    legende = "".join(
        f'<g transform="translate({14 + 150 * i},{haut - 16})">'
        f'<rect width="12" height="12" rx="3" fill="{c}" fill-opacity=".72"/>'
        f'<text x="18" y="10.5" font-size="11.5" fill="{ENCRE2}">'
        f'{_e(d)}</text></g>'
        for i, (d, c) in enumerate(teintes.items()) if d)
    return (f'<svg viewBox="0 0 {larg} {haut}" width="100%" '
            f'style="display:block;border-radius:10px;border:1px solid #e6ecf4" '
            f'font-family="Inter,system-ui,sans-serif">'
            + "".join(parts) + legende + '</svg>')


def cartes(geo=None):
    """Les deux cartes, côte à côte. Rendue à part pour pouvoir être appelée
    d'ailleurs sans emporter le reste de la page."""
    geo = geo or _geo()
    v = _vignette(geo)
    s = _situation(geo)
    if not v and not s:
        st.info(T("tr_absent"))
        return
    g, d = st.columns([1, 2.6])
    with g:
        st.markdown(f'<div class="titre-bloc">{T("tr_vignette")}</div>',
                    unsafe_allow_html=True)
        if v:
            st.markdown(v, unsafe_allow_html=True)
        st.caption(T("tr_vignette_note"))
    with d:
        st.markdown(f'<div class="titre-bloc vert">{T("tr_situation")}</div>',
                    unsafe_allow_html=True)
        if s:
            st.markdown(s, unsafe_allow_html=True)
        st.caption(T("tr_situation_note"))


def tableau(geo, effectifs, paysages):
    """Les dix sections, avec leur commune, leur département et leur effectif."""
    ent = [T("tr_c_section"), T("tr_c_commune"), T("tr_c_dep"),
           T("tr_c_pays"), T("tr_c_men")]
    li = ['<table style="width:100%;border-collapse:collapse;font-size:13px">'
          '<tr>' + "".join(
              f'<th style="text-align:{"left" if i < 4 else "right"};'
              f'padding:8px 10px;border-bottom:2px solid #e6ecf4;'
              f'font-size:10.5px;letter-spacing:.05em;text-transform:uppercase;'
              f'color:#6b7590;font-weight:700">{_e(h)}</th>'
              for i, h in enumerate(ent)) + '</tr>']
    par_nom = {s["nom"]: s for s in geo["sections"]}
    for nom in SECTIONS:
        s = par_nom.get(nom, {})
        p = paysages.get(nom, "")
        li.append(
            f'<tr><td style="padding:7px 10px;'
            f'border-bottom:1px solid #f0f4f9;font-weight:600;color:{ENCRE}">'
            f'{_e(nom)}</td>'
            f'<td style="padding:7px 10px;border-bottom:1px solid #f0f4f9;'
            f'color:{ENCRE2}">{_e(s.get("commune", ""))}</td>'
            f'<td style="padding:7px 10px;border-bottom:1px solid #f0f4f9;'
            f'color:{ENCRE2}">{_e(s.get("departement", ""))}</td>'
            f'<td style="padding:7px 10px;border-bottom:1px solid #f0f4f9;'
            f'color:{ENCRE3}">{_e(T("pay_" + p) if p else "")}</td>'
            f'<td style="padding:7px 10px;border-bottom:1px solid #f0f4f9;'
            f'text-align:right;font-variant-numeric:tabular-nums">'
            f'{effectifs.get(nom, "—")}</td></tr>')
    return "".join(li) + "</table>"


# ---------------------------------------------------------------------------
# LA CARTE D'ATELIER DES ENTRETIENS, ET SA LÉGENDE REFAITE
#
# Elle vient de QGIS et portait sa légende à l'intérieur de l'image, dans un
# bandeau de bas de page dessiné pour l'impression. À l'écran, ce bandeau
# tombait à 40 % de sa taille et devenait illisible. Il a donc été détaché de
# l'image et refait en HTML, où il suit la largeur de la page : les symboles
# avec leur figuré exact — trait tireté pour les départements, cercle blanc
# pour la capitale, carré plein pour les points d'entretien — et les six
# classes d'altitude avec leurs teintes relevées sur la carte elle-même.
#
# UNE SECONDE CARTE A ÉTÉ RETIRÉE DE CETTE PAGE : celle des paysages pilotes
# et des seize aires protégées. Son rendu écran ne tenait pas ses promesses —
# la mer occupait la moitié du cadre et le trait des aires protégées se
# perdait. Ce qu'elle apportait est dans la carte interactive du haut, où les
# aires protégées sont une couche qu'on allume.
# ---------------------------------------------------------------------------

RELIEF6 = [("#6aaaa3", "0 – 100"), ("#7caa4a", "100 – 500"),
           ("#bdce90", "500 – 1 000"), ("#e6e0bc", "1 000 – 1 500"),
           ("#c6aa74", "1 500 – 2 000"), ("#7f5b2e", "> 2 000 m")]

STYLE_CARTES = """
<style>
  .tr-leg { display:grid; gap:14px 26px; margin-top:10px; }
  .tr-lab { font-size:10.5px; letter-spacing:.09em; text-transform:uppercase;
            font-weight:700; color:#8a93a5; margin-bottom:6px; }
  .tr-ap  { display:grid; grid-template-columns:repeat(4, minmax(0,1fr));
            gap:4px 16px; }
  .tr-ap div { font-size:11.5px; color:#3c4761; line-height:1.4; }
  .tr-ap b { color:#101728; font-variant-numeric:tabular-nums;
             margin-right:5px; }
  .tr-sym { display:flex; flex-wrap:wrap; gap:6px 20px; }
  .tr-s   { display:flex; align-items:center; gap:7px; font-size:11.5px;
            color:#3c4761; }
  .tr-s i { flex:0 0 22px; height:12px; display:inline-block; }
  .tr-deg { height:14px; border-radius:4px; margin:2px 0 4px; }
  .tr-rep { display:flex; justify-content:space-between; font-size:11px;
            color:#6b7590; font-variant-numeric:tabular-nums; }
</style>
"""


def _sym(figure, couleur, tirets=False):
    if figure == "ligne":
        return (f'<i style="border-top:2.5px {"dashed" if tirets else "solid"} '
                f'{couleur};margin-top:5px"></i>')
    if figure == "carre":
        return (f'<i style="width:11px;height:11px;flex:0 0 11px;'
                f'background:{couleur};border:1px solid #ffffff;'
                f'box-shadow:0 0 0 1px #33415580;margin-left:5px"></i>')
    if figure == "cercle":
        return ('<i style="width:11px;height:11px;flex:0 0 11px;'
                'border-radius:50%;background:#ffffff;border:2px solid #101728;'
                'margin-left:5px"></i>')
    if figure == "point":
        return (f'<i style="width:9px;height:9px;flex:0 0 9px;border-radius:50%;'
                f'background:{couleur};margin-left:6px"></i>')
    return (f'<i style="background:{couleur}3d;border:1.5px '
            f'{"dashed" if tirets else "solid"} {couleur};'
            f'border-radius:3px"></i>')


def _ligne_sym(figure, couleur, texte, tirets=False):
    return (f'<div class="tr-s">{_sym(figure, couleur, tirets)}'
            f'<span>{_e(texte)}</span></div>')


def _image(nom):
    p = _trouver(nom)
    if not p:
        st.caption(T("tr_absent2"))
        return False
    st.image(p, use_container_width=True)
    return True


def carte_entretiens():
    st.markdown(f'<div class="titre-bloc">{_e(T("tr_qgis2"))}</div>',
                unsafe_allow_html=True)
    if not _image("carte_entretiens.jpg"):
        return
    st.caption(T("tr_qgis2_note"))
    g, d = st.columns([1.35, 1], gap="medium")
    with g:
        st.markdown(
            f'<div class="tr-lab">{_e(T("tr_l_sym"))}</div>'
            f'<div class="tr-sym">'
            + _ligne_sym("carre", "#8c5a2b", T("tr_l_ent_m"))
            + _ligne_sym("carre", "#2a6f9e", T("tr_l_ent_l"))
            + _ligne_sym("poly", "#101728", T("tr_l_sec"))
            + _ligne_sym("cercle", "#101728", T("tr_l_capitale"))
            + _ligne_sym("ligne", "#3f8fbd", T("tr_l_riv"))
            + _ligne_sym("ligne", "#c1521f", T("tr_l_reseau"))
            + _ligne_sym("ligne", "#101728", T("tr_l_dep"), tirets=True)
            + _ligne_sym("poly", "#aad3df", T("tr_l_ocean"))
            + '</div>', unsafe_allow_html=True)
    with d:
        st.markdown(
            f'<div class="tr-lab">{_e(T("tr_l_alt"))}</div>'
            + "".join(
                f'<div class="tr-s" style="margin-bottom:3px">'
                f'<i style="background:{c};border:1px solid #ffffff;'
                f'box-shadow:0 0 0 1px #dbe3ec;border-radius:2px"></i>'
                f'<span>{_e(t)}</span></div>' for c, t in RELIEF6),
            unsafe_allow_html=True)
    st.caption(T("tr_qgis2_meta"))


def render():
    """La page : la carte interactive, et rien d'autre.

    CE QUI EN A ÉTÉ RETIRÉ, ET POURQUOI. Trois objets se partageaient la page
    et répondaient tous à « où ? » : la vignette d'Haïti, la carte d'atelier
    des entretiens, et la carte interactive. La troisième fait ce que les deux
    autres font, et davantage — on y allume et éteint chaque couche, on y
    zoome, on y clique une section pour lire sa commune et son département.
    Les deux autres se dessinent toujours (`_vignette`, `carte_entretiens`) :
    l'accueil se sert de la première, et la seconde reste disponible pour un
    rapport. Elles ne sont simplement plus posées ici.
    """
    carte_localisation.render()
