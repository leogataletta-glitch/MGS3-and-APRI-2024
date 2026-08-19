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
    out = {"pays": [], "deps": [], "villes": [], "sections": []}
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


def _vignette(geo, larg=300, haut=330):
    """Haïti en entier, la zone enquêtée en vert. Elle ne dit que « où »."""
    if not geo["pays"] or not geo["sections"]:
        return None
    pr = _Proj(geo["pays"], larg, haut)
    parts = [f'<rect width="{larg}" height="{haut}" fill="{MER}"/>']
    for a in geo["pays"]:
        parts.append(f'<path d="{pr.chemin(a)}" fill="{TERRE}" '
                     f'stroke="{TRAIT}" stroke-width="1"/>')
    for _nom, anneaux in geo["deps"]:
        for a in anneaux:
            parts.append(f'<path d="{pr.chemin(a)}" fill="none" '
                         f'stroke="#dfe4ea" stroke-width=".8"/>')
    # La zone enquêtée, pleine, puis cerclée : à cette échelle les sections
    # font quelques pixels, et sans le cercle on ne les verrait pas.
    xs, ys = [], []
    for s in geo["sections"]:
        for a in s["anneaux"]:
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
    parts.append(f'<text x="{larg - 10}" y="20" text-anchor="end" '
                 f'font-size="12" font-weight="700" fill="#8a93a5" '
                 f'letter-spacing="2">HAÏTI</text>')
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
    li = ['<table style="width:100%;border-collapse:collapse;font-size:14px">'
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


def render():
    """La page entière : un titre, deux cartes, rien d'autre.

    Ce qui a quitté cette page — les chiffres de périmètre, les quatre
    résultats saillants, la carte des scores, les accès rapides — n'a pas
    disparu du site : les résultats sont dans « Analyse des résultats » et
    « Fiche synthèse », la navigation est dans la colonne de gauche, et les
    livraisons récentes sont passées dans « Données ».
    """
    st.markdown(
        f'<h2 style="font-size:27px;font-weight:700;color:{ENCRE};'
        f'letter-spacing:-.02em;margin:2px 0 0">{T("tr_titre")}</h2>'
        f'<p style="font-size:12.5px;color:{ENCRE3};letter-spacing:.06em;'
        f'text-transform:uppercase;margin:2px 0 14px;font-weight:600">'
        f'{T("tr_sous_titre")}</p>', unsafe_allow_html=True)
    cartes()
