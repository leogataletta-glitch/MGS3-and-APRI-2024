"""Onglet « Données environnementales ».

Ce que l'enquête ménage ne peut pas dire et que le satellite dit : l'état du
couvert forestier, section par section, année par année.

L'onglet affiche aussi, sans détour, ce qui manque encore — les six autres
indicateurs environnementaux de l'indice sont vides, et leur source est connue.
Un tableau de bord qui ne montre que ce qu'il possède laisse croire que le reste
n'existe pas.
"""

import json
import os

import streamlit as st
import streamlit.components.v1 as components

import assets
import i18n
import map_render
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

SECTIONS = ["Anse à Drick", "Barbois", "Dumont", "Débouchette", "Mouline",
            "Quentin", "Beaulieu", "Blactote", "Dalmette", "Trichet"]

# Les indicateurs environnementaux encore vides, avec la source qui les
# débloquerait. Repris des notes de resultats.json, regroupés par source pour
# que la lecture soit celle d'un plan de travail et non d'une liste de manques.
A_VENIR = [
    ("sentinel", [33, 34, 35, 63]),
    ("modis", [36, 41, 42]),
    ("occupation", [37, 38, 39, 40, 59, 60, 64, 65, 66, 67, 68, 69, 70]),
    ("terrain", [47, 48, 49, 50, 51, 52]),
    ("registres", [55, 56, 57, 58, 61]),
    # Celui-ci ne demande aucune donnée nouvelle : il est calculable depuis
    # l'enquête ménage. C'est le moins coûteux de la liste, il mérite d'être
    # distingué des autres plutôt que noyé parmi eux.
    ("enquete", [53]),
]

# Ce qui se cartographie, et l'unité qui va avec.
CARTES = [
    ("foret2000_pct", "%", "eleve_bon"),
    ("foret2025_pct", "%", "eleve_bon"),
    ("perte_relative_pct", "%", "eleve_mauvais"),
    ("taux_annuel_net", "", "eleve_bon"),
    ("taux_annuel_hors_choc", "", "eleve_bon"),
    ("part_choc_pct", "%", "neutre"),
]


def _trouver(nom):
    for c in (os.path.join(DATA, nom), os.path.join(APP_DIR, nom)):
        if os.path.exists(c):
            return c
    return None


@st.cache_data(show_spinner=False)
def _charger():
    chemins = {n: _trouver(n)
               for n in ("foret.json", "resultats.json", "pluie.json",
                         "grille_deforestation.json", "pluie_saison.json",
                         "indices_vegetation.json")}
    foret = res = pluie = grille = saison = indices = None
    if chemins["foret.json"]:
        with open(chemins["foret.json"], encoding="utf-8") as f:
            foret = json.load(f)
    if chemins["resultats.json"]:
        with open(chemins["resultats.json"], encoding="utf-8") as f:
            res = json.load(f)
    if chemins["pluie.json"]:
        with open(chemins["pluie.json"], encoding="utf-8") as f:
            pluie = json.load(f)
    if chemins["grille_deforestation.json"]:
        with open(chemins["grille_deforestation.json"], encoding="utf-8") as f:
            grille = json.load(f)
    if chemins["pluie_saison.json"]:
        with open(chemins["pluie_saison.json"], encoding="utf-8") as f:
            saison = json.load(f)
    if chemins["indices_vegetation.json"]:
        with open(chemins["indices_vegetation.json"], encoding="utf-8") as f:
            indices = json.load(f)
    return foret, res, pluie, grille, saison, indices


def _bulle(cle):
    fn = getattr(map_render, "bulle_notion", None)
    return fn(cle) if fn else ""


def _styles():
    fn = getattr(map_render, "styles_bulle", None)
    return fn() if fn else ""


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _fmt(v, dec=1):
    return f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")


# Le sélecteur de tête vaut soit une section, soit ce jeton, qui demande la
# vue territoriale — cartes, classements, séries des dix. Un jeton plutôt que
# None : il traverse les widgets Streamlit sans ambiguïté.
ENSEMBLE = "__ensemble__"


def _libelle_focus(v):
    return T("e_focus_ensemble") if v == ENSEMBLE else v


def _rang(foret_sections, sec, cle, meilleur_haut=True):
    """Rang de la section parmi les dix sur une grandeur, 1 = la mieux placée.

    Rendu tel quel plutôt que sous forme de score : un rang ne se moyenne pas
    et ne se pondère pas, il situe. C'est exactement ce qu'on demande à une
    fiche — « où en est cette section par rapport aux autres », pas « combien
    vaut-elle ».
    """
    vals = [(s, d.get(cle)) for s, d in foret_sections.items()
            if d.get(cle) is not None]
    if not vals or sec not in dict(vals):
        return None, len(vals)
    vals.sort(key=lambda kv: kv[1], reverse=meilleur_haut)
    for i, (s, _v) in enumerate(vals, 1):
        if s == sec:
            return i, len(vals)
    return None, len(vals)


def _moyenne_series(sections, cle):
    """Moyenne des dix sections, année par année, pour la vue d'ensemble.

    Moyenne non pondérée par la surface : les dix sections sont les unités
    d'enquête, et c'est à cette échelle que tout le reste du tableau de bord
    raisonne. Une pondération par l'aire dirait autre chose — le territoire
    plutôt que l'échantillon — et mélangerait deux lectures.
    """
    series = [d[cle] for d in sections.values() if cle in d]
    if not series:
        return {}
    annees = sorted(series[0], key=int)
    return {a: sum(s.get(a, 0) for s in series) / len(series) for a in annees}


# ----------------------------------------------------------------------
def _serie_annuelle_svg(pertes, annee_pic=None, largeur=1040):
    """Perte annuelle en barres verticales.

    Une série temporelle se lit horizontalement : le temps sur l'axe des x, la
    grandeur en hauteur. Les barres horizontales de l'application conviennent à
    un classement, pas à une chronologie — d'où ce rendu dédié. Une seule teinte,
    parce qu'il n'y a qu'une grandeur ; l'année du pic est écrite en clair,
    sinon personne ne devine ce que raconte cette silhouette.
    """
    annees = sorted(pertes, key=int)
    vals = [pertes[a] for a in annees]
    vmax = max(vals) or 1
    H, TOP, BAS, GAUCHE = 210, 26, 30, 52
    plot_h = H - TOP - BAS
    pas = (largeur - GAUCHE - 16) / len(annees)
    barre = pas * 0.62

    parts = []
    # graduations horizontales, discrètes, sous les barres
    for frac in (0.25, 0.5, 0.75, 1.0):
        y = TOP + plot_h * (1 - frac)
        parts.append(f'<line x1="{GAUCHE}" y1="{y:.1f}" x2="{largeur - 16}" '
                     f'y2="{y:.1f}" stroke="#eef2f7" stroke-width="1"/>')
        parts.append(f'<text class="eg" x="{GAUCHE - 8}" y="{y + 4:.1f}" '
                     f'text-anchor="end">{vmax * frac:.0f}</text>')

    for i, (a, v) in enumerate(zip(annees, vals)):
        h = plot_h * v / vmax
        x = GAUCHE + i * pas + (pas - barre) / 2
        y = TOP + plot_h - h
        pic = (annee_pic is not None and int(a) == int(annee_pic))
        col = "#b5451f" if pic else "#7ba05b"
        parts.append(
            f'<g><title>{a} — {v:.1f} ha</title>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{barre:.1f}" '
            f'height="{max(h, 1):.1f}" rx="2" fill="{col}"/></g>')
        if int(a) % 5 == 1 or pic:
            parts.append(f'<text class="ea" x="{x + barre / 2:.1f}" '
                         f'y="{H - 12}" text-anchor="middle">{a}</text>')
        if pic:
            parts.append(f'<text class="ep" x="{x + barre / 2:.1f}" '
                         f'y="{y - 8:.1f}" text-anchor="middle">'
                         f'{v:.0f} ha</text>')

    return f"""<svg viewBox="0 0 {largeur} {H}" width="100%"
     style="max-width:{largeur}px;display:block" role="img">
  <style>
    .eg{{font:11px system-ui,-apple-system,sans-serif;fill:#898781;
        font-variant-numeric:tabular-nums}}
    .ea{{font:11.5px system-ui,-apple-system,sans-serif;fill:#6b7590;
        font-variant-numeric:tabular-nums}}
    .ep{{font:700 13px system-ui,-apple-system,sans-serif;fill:#b5451f;
        font-variant-numeric:tabular-nums}}
  </style>
  {''.join(parts)}
</svg>"""


# Rampe temporelle : du jaune pâle (2001) au brun profond (2025). Une seule
# progression, parce qu'il n'y a qu'une grandeur ordonnée — le temps. Les
# années du choc Matthew sont volontairement dans les rouges vifs, au milieu de
# la rampe, pour qu'on les repère sans les chercher.
RAMPE_ANNEES = [
    (2001, "#fee8a0"), (2004, "#fdd276"), (2007, "#fdb863"), (2010, "#f79044"),
    (2013, "#e8632c"), (2016, "#cf2f1e"), (2019, "#a01813"), (2022, "#6d1210"),
    (2025, "#3d0a09"),
]


def _couleur_annee(a):
    if a <= RAMPE_ANNEES[0][0]:
        return RAMPE_ANNEES[0][1]
    for (a1, c1), (a2, c2) in zip(RAMPE_ANNEES, RAMPE_ANNEES[1:]):
        if a1 <= a <= a2:
            t = (a - a1) / (a2 - a1)
            r1, g1, b1 = (int(c1[i:i + 2], 16) for i in (1, 3, 5))
            r2, g2, b2 = (int(c2[i:i + 2], 16) for i in (1, 3, 5))
            return "#%02x%02x%02x" % (round(r1 + t * (r2 - r1)),
                                      round(g1 + t * (g2 - g1)),
                                      round(b1 + t * (b2 - b1)))
    return RAMPE_ANNEES[-1][1]


def _bloc_grille(grille, foret, focus=ENSEMBLE):
    """Où la perte s'est concentrée, cellule de 300 m par cellule de 300 m."""
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc ambre">{T("e_bloc_grille")}</div>',
                    unsafe_allow_html=True)
        st.markdown(
            f'<p style="font-size:16px;line-height:1.65;color:#3c4761;'
            f'margin:4px 0 10px;max-width:92ch">'
            f'{T("e_bloc_grille_texte", n=grille["n_cellules"])}</p>',
            unsafe_allow_html=True)

        annees = sorted({c["a"] for c in grille["cellules"]})
        a0, a1 = min(annees), max(annees)
        bornes = st.slider(T("e_grille_periode"), a0, a1, (a0, a1),
                           key=f"env_grille_{i18n.get_lang()}")
        retenues = [c for c in grille["cellules"]
                    if bornes[0] <= c["a"] <= bornes[1]]
        # La carte garde ses dix polygones même quand une section est choisie :
        # une tache de déforestation se lit par rapport à ce qui l'entoure. Ce
        # sont les points qui se restreignent, pas le fond.
        if focus != ENSEMBLE:
            retenues = [c for c in retenues if c["s"] == focus]
        perdu = sum(c["ha"] for c in retenues)

        st.markdown(
            f'<p style="font-size:15.5px;color:#3c4761;margin:0 0 8px">'
            f'{T("e_grille_selection", n=len(retenues), h=_fmt(perdu, 0), a=bornes[0], b=bornes[1])}'
            f'</p>', unsafe_allow_html=True)

        # Le rayon suit la RACINE de la surface perdue : c'est l'aire du disque
        # qui doit être proportionnelle à la grandeur, pas son rayon — sinon une
        # cellule deux fois plus touchée paraît quatre fois plus grave.
        hmax = max((c["ha"] for c in retenues), default=1) or 1
        points = [(c["x"], c["y"], 1.6 + 4.6 * (c["ha"] / hmax) ** 0.5,
                   _couleur_annee(c["a"]),
                   f'{c["s"]} — {c["ha"]:.2f} ha en {c["a"]}')
                  for c in retenues]

        # La couche de fond reste le couvert de 2000 : on lit ainsi la perte
        # sur ce qu'il y avait à perdre.
        valeurs = {s: foret["sections"].get(s, {}).get("foret2000_pct")
                   for s in SECTIONS}
        hauteur = 700
        svg, seuils, _m = map_render.render_map_svg(
            valeurs, {s: 1 for s in SECTIONS},
            map_render.nice_thresholds([v for v in valeurs.values() if v]),
            height=hauteur, polarity="neutre", unite="%",
            infos={s: T("e_grille_info",
                        n=sum(1 for c in retenues if c["s"] == s),
                        h=_fmt(sum(c["ha"] for c in retenues if c["s"] == s), 0))
                   for s in SECTIONS},
            points=points)

        legende = "".join(
            f'<span style="display:inline-flex;align-items:center;gap:6px;'
            f'margin-right:15px"><span style="width:12px;height:12px;'
            f'border-radius:50%;background:{_couleur_annee(a)}"></span>'
            f'<span style="font-size:12.5px;color:#52514e">{a}</span></span>'
            for a in (2001, 2006, 2011, 2016, 2021, 2025))
        components.html(
            '<div style="font-family:system-ui,-apple-system,\'Segoe UI\','
            'sans-serif;background:#ffffff"><div style="margin:0 0 8px">'
            f'<span style="font-size:11.5px;color:#898781;letter-spacing:.05em;'
            f'margin-right:12px">{T("e_grille_legende")}</span>{legende}</div>'
            f'{svg}</div>', height=hauteur + 46, scrolling=False)
        st.caption(T("e_bloc_grille_note"))


def _serie_pluie_svg(serie, normale, largeur=1040,
                     cle_normale="e_normale_ligne"):
    """Cumul annuel de pluie, avec la normale tracée en référence.

    L'encodage est DIVERGENT autour de la normale — ocre en dessous, bleu
    au-dessus — parce que la grandeur qui compte n'est pas la pluie mais
    l'écart à ce que le territoire reçoit d'ordinaire. Une seule teinte
    laisserait croire que 2 000 mm est « beaucoup » dans l'absolu, alors que
    c'est peu à Mouline et considérable à Dumont.
    """
    annees = sorted(serie, key=int)
    vals = [serie[a] for a in annees]
    vmax = max(vals) * 1.05
    H, TOP, BAS, GAUCHE = 230, 22, 30, 58
    plot_h = H - TOP - BAS
    pas = (largeur - GAUCHE - 16) / len(annees)
    barre = pas * 0.66

    def y_de(v):
        return TOP + plot_h * (1 - v / vmax)

    parts = []
    for frac in (0.25, 0.5, 0.75, 1.0):
        y = TOP + plot_h * (1 - frac)
        parts.append(f'<line x1="{GAUCHE}" y1="{y:.1f}" x2="{largeur - 16}" '
                     f'y2="{y:.1f}" stroke="#eef2f7" stroke-width="1"/>')
        parts.append(f'<text class="eg" x="{GAUCHE - 8}" y="{y + 4:.1f}" '
                     f'text-anchor="end">{vmax * frac:.0f}</text>')

    for i, (a, v) in enumerate(zip(annees, vals)):
        x = GAUCHE + i * pas + (pas - barre) / 2
        y = y_de(v)
        col = "#2a78d6" if v >= normale else "#c98a2e"
        parts.append(
            f'<g><title>{a} — {v:.0f} mm ({100 * v / normale:.0f} % de la '
            f'normale)</title><rect x="{x:.1f}" y="{y:.1f}" '
            f'width="{barre:.1f}" height="{max(TOP + plot_h - y, 1):.1f}" '
            f'rx="2" fill="{col}"/></g>')
        if int(a) % 5 == 1:
            parts.append(f'<text class="ea" x="{x + barre / 2:.1f}" '
                         f'y="{H - 12}" text-anchor="middle">{a}</text>')

    yn = y_de(normale)
    parts.append(f'<line x1="{GAUCHE}" y1="{yn:.1f}" x2="{largeur - 16}" '
                 f'y2="{yn:.1f}" stroke="#101728" stroke-width="1.5" '
                 f'stroke-dasharray="5 4"/>')
    parts.append(f'<text class="en" x="{largeur - 18}" y="{yn - 7:.1f}" '
                 f'text-anchor="end">{_e(T(cle_normale, n=normale))}</text>')

    return f"""<svg viewBox="0 0 {largeur} {H}" width="100%"
     style="max-width:{largeur}px;display:block" role="img">
  <style>
    .eg{{font:11px system-ui,-apple-system,sans-serif;fill:#898781;
        font-variant-numeric:tabular-nums}}
    .ea{{font:11.5px system-ui,-apple-system,sans-serif;fill:#6b7590;
        font-variant-numeric:tabular-nums}}
    .en{{font:700 12px system-ui,-apple-system,sans-serif;fill:#101728;
        font-variant-numeric:tabular-nums}}
  </style>
  {''.join(parts)}
</svg>"""


def _tableau_pluie(pluie):
    """Les dix sections sur la pluie annuelle, triées de la plus sèche."""
    ordre = sorted(pluie["sections"].items(), key=lambda kv: kv[1]["normale_mm"])
    entetes = [T("e_sc_section"), T("e_pc_normale"), T("e_pc_recent"),
               T("e_sc_part"), T("e_pc_sec"), T("e_pc_humide")]
    out = ['<div style="overflow-x:auto"><table style="width:100%;'
           'border-collapse:collapse;font-size:14.5px">']
    out.append('<tr>' + ''.join(
        f'<th style="text-align:{"left" if i == 0 else "right"};'
        f'padding:9px 10px;border-bottom:2px solid #e6ecf4;font-size:11.5px;'
        f'letter-spacing:.05em;text-transform:uppercase;color:#6b7590;'
        f'font-weight:700">{_e(h)}</th>' for i, h in enumerate(entetes))
        + '</tr>')
    C = 'padding:9px 10px;border-bottom:1px solid #f0f4f9;text-align:right;' \
        'font-variant-numeric:tabular-nums'
    for sec, d in ordre:
        part = d["ratio_normale"]
        coul = "#b4451f" if part < 90 else ("#c98a2e" if part < 96 else "#2a6b3f")
        out.append(
            f'<tr><td style="padding:9px 10px;border-bottom:1px solid #f0f4f9">'
            f'{_e(sec)}</td>'
            f'<td style="{C};color:#6b7590">{_fmt(d["normale_mm"], 0)} mm</td>'
            f'<td style="{C}">{_fmt(d["pluie_courante_mm"], 0)} mm</td>'
            f'<td style="{C};color:{coul};font-weight:700">'
            f'{_fmt(part, 0)} %</td>'
            f'<td style="{C};color:#6b7590">{_fmt(d["minimum_mm"], 0)} mm '
            f'<span style="color:#a9b0be">({d["annee_min"]})</span></td>'
            f'<td style="{C};color:#6b7590">{_fmt(d["maximum_mm"], 0)} mm '
            f'<span style="color:#a9b0be">({d["annee_max"]})</span></td></tr>')
    out.append('</table></div>')
    return ''.join(out)


def _pluie_ensemble(pluie):
    """Un bloc « moyenne des dix » de même forme qu'une section, pour la vue
    territoriale. Les extrêmes sont pris sur la moyenne territoriale et non
    section par section : c'est l'année sèche du Grand Sud qu'on cherche, pas
    la juxtaposition de dix années sèches différentes."""
    secs = pluie["sections"]
    serie = _moyenne_series(secs, "serie_mm")
    ref = secs[next(iter(secs))]
    normale = sum(d["normale_mm"] for d in secs.values()) / len(secs)
    courant = sum(d["pluie_courante_mm"] for d in secs.values()) / len(secs)
    an_min = min(serie, key=lambda a: serie[a])
    an_max = max(serie, key=lambda a: serie[a])
    return {
        "normale_mm": normale, "pluie_courante_mm": courant,
        "ratio_normale": 100.0 * courant / normale,
        "minimum_mm": serie[an_min], "annee_min": an_min,
        "maximum_mm": serie[an_max], "annee_max": an_max,
        "normale_periode": ref["normale_periode"],
        "fenetre_ans": ref["fenetre_ans"], "serie_mm": serie,
    }


def _bloc_pluie(pluie, focus=ENSEMBLE):
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("e_bloc_pluie")}</div>',
                    unsafe_allow_html=True)
        st.markdown(
            f'<p style="font-size:16px;line-height:1.65;color:#3c4761;'
            f'margin:4px 0 10px;max-width:92ch">'
            f'{T("e_bloc_pluie_texte", a=pluie["annee_evaluee"], f=pluie["sections"][SECTIONS[0]]["fenetre_ans"])}'
            f'</p>', unsafe_allow_html=True)

        if focus == ENSEMBLE or focus not in pluie["sections"]:
            d = _pluie_ensemble(pluie)
            st.caption(T("e_vue_ensemble_note"))
        else:
            d = pluie["sections"][focus]

        c1, c2, c3, c4 = st.columns(4)
        for col, lib, val, unite, sous in [
                (c1, T("e_p_normale"), _fmt(d["normale_mm"], 0), "mm",
                 T("e_p_normale_sous", a=d["normale_periode"][0],
                   b=d["normale_periode"][1])),
                (c2, T("e_p_recent"), _fmt(d["pluie_courante_mm"], 0), "mm",
                 T("e_p_recent_sous", p=_fmt(d["ratio_normale"], 0))),
                (c3, T("e_p_sec"), _fmt(d["minimum_mm"], 0), "mm",
                 T("e_p_sec_sous", a=d["annee_min"])),
                (c4, T("e_p_humide"), _fmt(d["maximum_mm"], 0), "mm",
                 T("e_p_humide_sous", a=d["annee_max"]))]:
            with col:
                st.markdown(
                    map_render.cartouche_html(lib, val, unite, sous,
                                              couleur="#2a78d6"),
                    unsafe_allow_html=True)

        svg = _serie_pluie_svg(d["serie_mm"], d["normale_mm"])
        components.html(
            '<div style="background:#ffffff;font-family:system-ui,-apple-system,'
            "'Segoe UI',sans-serif\">" + svg + "</div>",
            height=245, scrolling=False)
        st.caption(T("e_bloc_pluie_note"))

        st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
        st.markdown(_tableau_pluie(pluie), unsafe_allow_html=True)
        st.caption(T("e_pc_note"))


def _tableau_saison(saison):
    """Les dix sections sur une ligne chacune, comparaisons dans les cellules.

    Séquences sèches et pluies extrêmes sont données en « ancien → récent »
    plutôt qu'en écart : l'écart seul (« +1,2 jour ») ne dit pas s'il faut le
    lire comme beaucoup ou comme peu. Deux nombres côte à côte le disent.
    """
    ordre = sorted(saison["sections"].items(),
                   key=lambda kv: kv[1]["ratio_normale"])
    entetes = [T("e_sc_section"), T("e_sc_normale"), T("e_sc_recent"),
               T("e_sc_part"), T("e_sc_secs"), T("e_sc_j50"),
               T("e_sc_install"), T("e_sc_ratees")]
    out = ['<div style="overflow-x:auto"><table style="width:100%;'
           'border-collapse:collapse;font-size:14.5px">']
    out.append('<tr>' + ''.join(
        f'<th style="text-align:{"left" if i == 0 else "right"};'
        f'padding:9px 10px;border-bottom:2px solid #e6ecf4;font-size:11.5px;'
        f'letter-spacing:.05em;text-transform:uppercase;color:#6b7590;'
        f'font-weight:700">{_e(h)}</th>' for i, h in enumerate(entetes))
        + '</tr>')

    for sec, d in ordre:
        part = d["ratio_normale"]
        # Un seul repère coloré dans la ligne, sur la part à la normale : c'est
        # elle qui porte le diagnostic. Colorer aussi les séquences sèches et
        # les pluies fortes ferait trois signaux concurrents par ligne.
        coul = "#b4451f" if part < 78 else ("#c98a2e" if part < 90 else "#2a6b3f")
        cells = [
            f'<td style="padding:9px 10px;border-bottom:1px solid #f0f4f9">'
            f'{_e(sec)}</td>',
            f'<td style="padding:9px 10px;border-bottom:1px solid #f0f4f9;'
            f'text-align:right;font-variant-numeric:tabular-nums;color:#6b7590">'
            f'{_fmt(d["mam_normale_mm"], 0)} mm</td>',
            f'<td style="padding:9px 10px;border-bottom:1px solid #f0f4f9;'
            f'text-align:right;font-variant-numeric:tabular-nums">'
            f'{_fmt(d["mam_courant_mm"], 0)} mm</td>',
            f'<td style="padding:9px 10px;border-bottom:1px solid #f0f4f9;'
            f'text-align:right;font-variant-numeric:tabular-nums;color:{coul};'
            f'font-weight:700">{_fmt(part, 0)} %</td>',
            f'<td style="padding:9px 10px;border-bottom:1px solid #f0f4f9;'
            f'text-align:right;font-variant-numeric:tabular-nums;color:#6b7590">'
            f'{_fmt(d["secs_mam_ancien"], 1)} <span style="color:#c3c9d4">'
            f'&rarr;</span> <span style="color:#101728">'
            f'{_fmt(d["secs_mam_recent"], 1)}</span></td>',
            f'<td style="padding:9px 10px;border-bottom:1px solid #f0f4f9;'
            f'text-align:right;font-variant-numeric:tabular-nums;color:#6b7590">'
            f'{_fmt(d["j50_ancien"], 1)} <span style="color:#c3c9d4">&rarr;</span> '
            f'<span style="color:#101728">{_fmt(d["j50_recent"], 1)}</span></td>',
            f'<td style="padding:9px 10px;border-bottom:1px solid #f0f4f9;'
            f'text-align:right">{_e(d["install_date_recent"] or "—")}</td>',
            f'<td style="padding:9px 10px;border-bottom:1px solid #f0f4f9;'
            f'text-align:right;font-variant-numeric:tabular-nums">'
            f'{d["install_ratees"]} / 45</td>',
        ]
        out.append('<tr>' + ''.join(cells) + '</tr>')
    out.append('</table></div>')
    return ''.join(out)


def _saison_ensemble(saison):
    """Moyenne des dix sections sur la campagne, même forme qu'une section."""
    secs = saison["sections"]
    n = len(secs)
    moy = lambda k: sum(d[k] for d in secs.values()) / n          # noqa: E731
    somme = lambda k: sum(d[k] for d in secs.values())            # noqa: E731
    serie = _moyenne_series(secs, "serie_mam")
    normale = moy("mam_normale_mm")
    courant = moy("mam_courant_mm")
    # La date d'installation est moyennée en JOUR DE L'ANNÉE puis reconvertie :
    # moyenner des libellés n'a pas de sens, et moyenner des dates de sections
    # dont certaines n'ont pas de départ net fausserait le résultat.
    jours = [d["install_jour_recent"] for d in secs.values()
             if d.get("install_jour_recent")]
    return {
        "mam_normale_mm": normale, "mam_courant_mm": courant,
        "ratio_normale": 100.0 * courant / normale,
        "j50_recent": moy("j50_recent"), "j50_ancien": moy("j50_ancien"),
        "secs_mam_recent": moy("secs_mam_recent"),
        "secs_mam_ancien": moy("secs_mam_ancien"),
        "install_date_recent": (_jour_vers_libelle(sum(jours) / len(jours))
                                if jours else None),
        "install_decalage_j": moy("install_decalage_j"),
        "install_ratees": round(somme("install_ratees") / n, 1),
        "serie_mam": serie,
    }


_MOIS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
            "août", "septembre", "octobre", "novembre", "décembre"]
_MOIS_EN = ["January", "February", "March", "April", "May", "June", "July",
            "August", "September", "October", "November", "December"]
_CUMUL = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]


def _jour_vers_libelle(j):
    j = int(round(j))
    mois = _MOIS_FR if i18n.get_lang() == "fr" else _MOIS_EN
    for m in range(12):
        if j <= _CUMUL[m + 1]:
            return (f"{j - _CUMUL[m]} {mois[m]}" if i18n.get_lang() == "fr"
                    else f"{mois[m]} {j - _CUMUL[m]}")
    return f"{j - 334} {mois[11]}"


def _bloc_saison(saison, focus=ENSEMBLE):
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc vert">{T("e_bloc_saison")}</div>',
                    unsafe_allow_html=True)
        st.markdown(
            f'<p style="font-size:16px;line-height:1.65;color:#3c4761;'
            f'margin:4px 0 10px;max-width:92ch">{T("e_bloc_saison_texte")}</p>',
            unsafe_allow_html=True)

        if focus == ENSEMBLE or focus not in saison["sections"]:
            d = _saison_ensemble(saison)
            st.caption(T("e_vue_ensemble_note"))
        else:
            d = saison["sections"][focus]
        norm = saison["normale_periode"]

        dec = d["install_decalage_j"]
        if dec is None:
            sous_inst = ""
        elif abs(dec) < 3:
            sous_inst = T("e_s_install_sous_stable")
        elif dec > 0:
            sous_inst = T("e_s_install_sous_tard", n=_fmt(dec, 0))
        else:
            sous_inst = T("e_s_install_sous_tot", n=_fmt(-dec, 0))

        c1, c2, c3, c4 = st.columns(4)
        for col, lib, val, unite, sous, coul in [
                (c1, T("e_s_normale"), _fmt(d["mam_normale_mm"], 0), "mm",
                 T("e_s_normale_sous", a=norm[0], b=norm[1]), "#2a78d6"),
                (c2, T("e_s_recent", f=saison["fenetre_ans"]),
                 _fmt(d["mam_courant_mm"], 0), "mm",
                 T("e_s_recent_sous", p=_fmt(d["ratio_normale"], 0)),
                 "#b4451f" if d["ratio_normale"] < 90 else "#2a78d6"),
                (c3, T("e_s_install"), d["install_date_recent"] or "—", "",
                 sous_inst, "#2a6b3f"),
                (c4, T("e_s_extreme"), _fmt(d["j50_recent"], 1), "",
                 T("e_s_extreme_sous", n=_fmt(d["j50_ancien"], 1)),
                 "#c98a2e")]:
            with col:
                st.markdown(
                    map_render.cartouche_html(lib, val, unite, sous,
                                              couleur=coul),
                    unsafe_allow_html=True)

        svg = _serie_pluie_svg(d["serie_mam"], d["mam_normale_mm"],
                               cle_normale="e_normale_mam_ligne")
        components.html(
            '<div style="background:#ffffff;font-family:system-ui,-apple-system,'
            "'Segoe UI',sans-serif\">" + svg + "</div>",
            height=245, scrolling=False)
        st.caption(T("e_bloc_saison_note"))

        st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
        st.markdown(_tableau_saison(saison), unsafe_allow_html=True)
        st.caption(T("e_s_tableau_note"))
        st.markdown(
            f'<div style="border-left:3px solid #cfe2f3;padding:2px 0 2px 14px;'
            f'margin:14px 0 0;font-size:14px;line-height:1.6;color:#6b7590;'
            f'max-width:92ch">{T("e_s_methode")}</div>',
            unsafe_allow_html=True)


def _tableau_sections(foret):
    lignes = sorted(foret["sections"].items(),
                    key=lambda kv: kv[1]["taux_annuel_net"])
    entetes = [T("e_col_section"), T("e_col_foret2000"), T("e_col_perte"),
               T("e_col_taux"), T("e_col_choc"), T("e_col_chronique")]
    out = ['<div style="overflow-x:auto"><table style="width:100%;'
           'border-collapse:collapse;font-size:14.5px">']
    out.append('<tr>' + ''.join(
        f'<th style="text-align:{"left" if i == 0 else "right"};'
        f'padding:9px 10px;border-bottom:2px solid #e6ecf4;font-size:11.5px;'
        f'letter-spacing:.05em;text-transform:uppercase;color:#6b7590;'
        f'font-weight:700">{_e(h)}</th>' for i, h in enumerate(entetes))
        + '</tr>')
    for sec, d in lignes:
        # une part de choc élevée dit « tempête », une part basse dit
        # « défrichement continu » : c'est la colonne qui distingue les deux
        # situations, on la teinte pour qu'elle se voie.
        part = d["part_choc_pct"]
        fond = "#fdeee9" if part >= 60 else ("#eef5fb" if part <= 20 else "")
        cells = [
            f'<td style="padding:9px 10px;border-bottom:1px solid #f1f4f8">'
            f'{_e(sec)}</td>',
            f'<td style="text-align:right;padding:9px 10px;'
            f'border-bottom:1px solid #f1f4f8;font-variant-numeric:tabular-nums">'
            f'{_fmt(d["foret2000_ha"], 0)} ha</td>',
            f'<td style="text-align:right;padding:9px 10px;'
            f'border-bottom:1px solid #f1f4f8;font-variant-numeric:tabular-nums">'
            f'{_fmt(d["perte_totale_ha"], 0)} ha</td>',
            f'<td style="text-align:right;padding:9px 10px;'
            f'border-bottom:1px solid #f1f4f8;font-variant-numeric:tabular-nums;'
            f'font-weight:700;color:#101728">{_fmt(d["taux_annuel_net"], 2)} %</td>',
            f'<td style="text-align:right;padding:9px 10px;'
            f'border-bottom:1px solid #f1f4f8;font-variant-numeric:tabular-nums;'
            f'background:{fond}">{_fmt(part, 0)} %</td>',
            f'<td style="text-align:right;padding:9px 10px;'
            f'border-bottom:1px solid #f1f4f8;font-variant-numeric:tabular-nums">'
            f'{_fmt(d["taux_annuel_hors_choc"], 2)} %</td>',
        ]
        out.append('<tr>' + ''.join(cells) + '</tr>')
    out.append('</table></div>')
    return ''.join(out)

def _onglet_foret(foret, focus):
    """Couvert forestier : les chiffres, la chronologie, la carte, le détail.

    En vue territoriale, les quatre cartouches portent l'agrégat des dix
    sections. Quand une section est choisie, ils portent ses chiffres à elle,
    et un rang s'affiche sous chacun — sans rang, un taux de −0,51 % ne dit
    pas si la section est parmi les plus atteintes ou parmi les plus épargnées.
    """
    ens = foret["ensemble"]
    d = ens if focus == ENSEMBLE else foret["sections"].get(focus, ens)
    secs = foret["sections"]

    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc vert">{T("e_bloc1")}</div>',
                    unsafe_allow_html=True)
        if focus != ENSEMBLE:
            st.caption(T("e_vue_section_note", s=focus))

        def sous(cle, meilleur_haut, base):
            if focus == ENSEMBLE:
                return base
            r, n = _rang(secs, focus, cle, meilleur_haut)
            return base if r is None else f"{base} · {T('e_rang', r=r, n=n)}"

        c1, c2, c3, c4 = st.columns(4)
        # Les valeurs sont mises en forme ici plutôt que laissées au cartouche :
        # une surface se lit en entiers avec une espace de millier, un taux
        # annuel demande deux décimales — à un dixième près, −0,5 et −0,54 se
        # confondent alors qu'ils ne sont pas dans la même classe de score.
        cartes = [
            (c1, T("e_c_foret2000"), _fmt(d["foret2000_ha"], 0), "ha",
             sous("foret2000_pct", True,
                  T("e_c_foret2000_sous", p=_fmt(d["foret2000_pct"]))),
             "#5b9c5a"),
            (c2, T("e_c_perte"), _fmt(d["perte_totale_ha"], 0), "ha",
             sous("perte_relative_pct", False,
                  T("e_c_perte_sous", p=_fmt(d["perte_relative_pct"]))),
             "#b5451f"),
            (c3, T("e_c_taux"), _fmt(d["taux_annuel_net"], 2), "%",
             sous("taux_annuel_net", True, T("e_c_taux_sous")), "#eb9d3a"),
            (c4, T("e_c_chronique"), _fmt(d["taux_annuel_hors_choc"], 2), "%",
             sous("taux_annuel_hors_choc", True, T("e_c_chronique_sous")),
             "#7ba05b"),
        ]
        for col, lib, val, unite, s_txt, coul in cartes:
            with col:
                st.markdown(
                    map_render.cartouche_html(lib, val, unite, s_txt,
                                              couleur=coul),
                    unsafe_allow_html=True)
        st.markdown(
            '<p style="font-size:15px;color:#3c4761;margin:10px 0 0">'
            + _bulle("boucle_retroaction") + " &nbsp;·&nbsp; "
            + _bulle("point_de_levier") + "</p>", unsafe_allow_html=True)

    # --------------------------------------------------- la série annuelle
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc ambre">{T("e_bloc2")}</div>',
                    unsafe_allow_html=True)
        st.markdown(
            f'<p style="font-size:16px;line-height:1.65;color:#3c4761;'
            f'margin:4px 0 10px;max-width:92ch">'
            f'{T("e_bloc2_texte", p=_fmt(d["part_choc_pct"], 0))}</p>',
            unsafe_allow_html=True)
        svg = _serie_annuelle_svg(d["pertes_annuelles_ha"], annee_pic=2016)
        components.html(
            '<div style="background:#ffffff;font-family:system-ui,-apple-system,'
            "'Segoe UI',sans-serif\">" + svg + "</div>",
            height=225, scrolling=False)
        st.caption(T("e_bloc2_note"))

    # ------------------------------------------------------------- la carte
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("e_bloc3")}</div>',
                    unsafe_allow_html=True)
        cle, unite, polarite = CARTES[
            st.selectbox(T("e_quoi_carto"), range(len(CARTES)),
                         format_func=lambda i: T("e_carte_" + CARTES[i][0]),
                         key=f"env_carte_{i18n.get_lang()}")]
        valeurs = {s: secs.get(s, {}).get(cle) for s in SECTIONS}
        seuils = map_render.nice_thresholds(
            [v for v in valeurs.values() if v is not None])
        infos = {s: T("e_info_carte", f=_fmt(secs[s]["foret2000_ha"], 0))
                 for s in SECTIONS if s in secs}
        hauteur = 660
        svg, seuils_ret, _mode = map_render.render_map_svg(
            valeurs, {s: 1 for s in SECTIONS}, seuils, height=hauteur,
            polarity=polarite, unite=unite, infos=infos)
        legende = "".join(
            f'<span style="display:inline-flex;align-items:center;gap:7px;'
            f'margin-right:18px"><span style="width:22px;height:12px;'
            f'border-radius:3px;background:{c};box-shadow:inset 0 0 0 1px '
            f'rgba(0,0,0,.12)"></span><span style="font-size:13px;'
            f'color:#52514e">{lab}</span></span>'
            for c, lab in map_render.legend_items(seuils_ret, polarite, unite))
        components.html(
            '<div style="font-family:system-ui,-apple-system,\'Segoe UI\','
            'sans-serif;background:#ffffff"><div style="margin:0 0 8px">'
            f'<span style="font-size:11.5px;color:#898781;letter-spacing:.05em;'
            f'margin-right:14px">{T("legende_seuils")}</span>{legende}</div>'
            f'{svg}</div>', height=hauteur + 46, scrolling=False)
        st.caption(T("e_carte_toujours_note"))

    # ------------------------------------------------------------ le détail
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc vert">{T("e_bloc4")}</div>',
                    unsafe_allow_html=True)
        st.caption(T("e_bloc4_note"))
        st.markdown(_tableau_sections(foret), unsafe_allow_html=True)


# ----------------------------------------------------------- fiche section
def _puce(lib, val, sous=""):
    return (f'<div style="flex:1 1 190px;min-width:170px;padding:11px 14px;'
            f'background:#fbfcfe;border:1px solid #eef2f7;border-radius:11px">'
            f'<div style="font-size:11px;letter-spacing:.05em;'
            f'text-transform:uppercase;color:#8a93a5;font-weight:700">'
            f'{_e(lib)}</div>'
            f'<div style="font-size:22px;font-weight:700;color:#101728;'
            f'font-variant-numeric:tabular-nums;margin-top:2px">{_e(val)}</div>'
            + (f'<div style="font-size:12.5px;color:#6b7590;margin-top:1px">'
               f'{_e(sous)}</div>' if sous else '') + '</div>')


def _groupe(titre, puces):
    return (f'<div style="margin:0 0 16px">'
            f'<div style="font-size:12px;letter-spacing:.06em;'
            f'text-transform:uppercase;color:#1a6bb0;font-weight:700;'
            f'margin:0 0 7px">{_e(titre)}</div>'
            f'<div style="display:flex;flex-wrap:wrap;gap:9px">'
            + ''.join(puces) + '</div></div>')


def _fiche_section(foret, pluie, saison, grille, res, focus):
    """Tout ce que le satellite dit d'une section, réuni sur une page.

    Les onglets thématiques servent à comparer les sections entre elles ; la
    fiche sert à comprendre une section. Ce sont deux lectures différentes, et
    c'est pourquoi les mêmes chiffres y reviennent sous une autre forme —
    groupés par sujet plutôt que par source, et accompagnés du rang.
    """
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("e_o_fiche")}</div>',
                    unsafe_allow_html=True)

        if focus == ENSEMBLE:
            st.markdown(
                f'<p style="font-size:16px;line-height:1.65;color:#3c4761;'
                f'margin:4px 0 12px;max-width:92ch">{T("e_fiche_invite")}</p>',
                unsafe_allow_html=True)
            st.markdown(_tableau_recap(foret, pluie, saison),
                        unsafe_allow_html=True)
            st.caption(T("e_fiche_recap_note"))
            return

        st.markdown(
            f'<h3 style="margin:6px 0 2px;font-size:25px;color:#101728">'
            f'{_e(focus)}</h3>', unsafe_allow_html=True)

        blocs = []
        f = foret["sections"].get(focus)
        if f:
            r_perte, n = _rang(foret["sections"], focus,
                               "perte_relative_pct", False)
            r_taux, _ = _rang(foret["sections"], focus, "taux_annuel_net", True)
            blocs.append(_groupe(T("e_fg_foret"), [
                _puce(T("e_c_foret2000"), f'{_fmt(f["foret2000_ha"], 0)} ha',
                      T("e_c_foret2000_sous", p=_fmt(f["foret2000_pct"]))),
                _puce(T("e_fp_foret2025"), f'{_fmt(f["foret2025_net_ha"], 0)} ha',
                      T("e_c_foret2000_sous", p=_fmt(f["foret2025_pct"]))),
                _puce(T("e_c_perte"), f'{_fmt(f["perte_totale_ha"], 0)} ha',
                      f'{_fmt(f["perte_relative_pct"])} % · '
                      + T("e_rang", r=r_perte, n=n)),
                _puce(T("e_c_taux"), f'{_fmt(f["taux_annuel_net"], 2)} %',
                      T("e_rang", r=r_taux, n=n)),
                _puce(T("e_fp_choc"), f'{_fmt(f["part_choc_pct"], 0)} %',
                      T("e_fp_choc_sous",
                        c=_fmt(f["taux_annuel_hors_choc"], 2))),
            ]))

        if grille:
            cel = [c for c in grille["cellules"] if c["s"] == focus]
            if cel:
                pire = max(cel, key=lambda c: c["ha"])
                par_an = {}
                for c in cel:
                    par_an[c["a"]] = par_an.get(c["a"], 0) + c["ha"]
                an_pire = max(par_an, key=par_an.get)
                blocs.append(_groupe(T("e_fg_grille"), [
                    _puce(T("e_fp_cellules"), f'{len(cel)}',
                          T("e_fp_cellules_sous")),
                    _puce(T("e_fp_annee_pire"), f'{an_pire}',
                          f'{_fmt(par_an[an_pire], 1)} ha'),
                    _puce(T("e_fp_cellule_pire"), f'{_fmt(pire["ha"], 2)} ha',
                          T("e_fp_cellule_pire_sous", a=pire["a"])),
                ]))

        p = (pluie or {}).get("sections", {}).get(focus)
        if p:
            blocs.append(_groupe(T("e_fg_pluie"), [
                _puce(T("e_p_normale"), f'{_fmt(p["normale_mm"], 0)} mm',
                      T("e_p_normale_sous", a=p["normale_periode"][0],
                        b=p["normale_periode"][1])),
                _puce(T("e_p_recent"), f'{_fmt(p["pluie_courante_mm"], 0)} mm',
                      T("e_p_recent_sous", p=_fmt(p["ratio_normale"], 0))),
                _puce(T("e_p_sec"), f'{_fmt(p["minimum_mm"], 0)} mm',
                      T("e_p_sec_sous", a=p["annee_min"])),
                _puce(T("e_p_humide"), f'{_fmt(p["maximum_mm"], 0)} mm',
                      T("e_p_humide_sous", a=p["annee_max"])),
            ]))

        s = (saison or {}).get("sections", {}).get(focus)
        if s:
            dec = s.get("install_decalage_j")
            if dec is None:
                sous_i = ""
            elif abs(dec) < 3:
                sous_i = T("e_s_install_sous_stable")
            elif dec > 0:
                sous_i = T("e_s_install_sous_tard", n=_fmt(dec, 0))
            else:
                sous_i = T("e_s_install_sous_tot", n=_fmt(-dec, 0))
            blocs.append(_groupe(T("e_fg_saison"), [
                _puce(T("e_s_normale"), f'{_fmt(s["mam_normale_mm"], 0)} mm',
                      T("e_s_normale_sous", a=saison["normale_periode"][0],
                        b=saison["normale_periode"][1])),
                _puce(T("e_s_recent", f=saison["fenetre_ans"]),
                      f'{_fmt(s["mam_courant_mm"], 0)} mm',
                      T("e_s_recent_sous", p=_fmt(s["ratio_normale"], 0))),
                _puce(T("e_s_install"), s["install_date_recent"] or "—", sous_i),
                _puce(T("e_fp_ratees"), f'{s["install_ratees"]} / 45',
                      T("e_fp_ratees_sous")),
                _puce(T("e_sc_secs"), f'{_fmt(s["secs_mam_recent"])} j',
                      T("e_fp_contre", n=_fmt(s["secs_mam_ancien"]))),
                _puce(T("e_s_extreme"), f'{_fmt(s["j50_recent"])}',
                      T("e_s_extreme_sous", n=_fmt(s["j50_ancien"]))),
            ]))

        st.markdown(''.join(blocs), unsafe_allow_html=True)

        if res:
            st.markdown(_tableau_scores(res, focus), unsafe_allow_html=True)
            st.caption(T("e_fiche_scores_note"))


def _tableau_scores(res, focus):
    """Les indicateurs environnementaux calculés, pour cette section."""
    lignes = [r for r in res
              if r["dimension"].startswith("III")
              and r.get("scores_corriges", {}).get(focus) is not None]
    if not lignes:
        return ""
    out = [f'<div style="font-size:12px;letter-spacing:.06em;'
           f'text-transform:uppercase;color:#1a6bb0;font-weight:700;'
           f'margin:16px 0 7px">{_e(T("e_fg_scores"))}</div>',
           '<div style="overflow-x:auto"><table style="width:100%;'
           'border-collapse:collapse;font-size:14.5px">']
    entetes = [T("e_fs_ligne"), T("e_fs_indicateur"), T("e_fs_valeur"),
               T("e_fs_score")]
    out.append('<tr>' + ''.join(
        f'<th style="text-align:{"left" if i < 2 else "right"};'
        f'padding:9px 10px;border-bottom:2px solid #e6ecf4;font-size:11.5px;'
        f'letter-spacing:.05em;text-transform:uppercase;color:#6b7590;'
        f'font-weight:700">{_e(h)}</th>' for i, h in enumerate(entetes))
        + '</tr>')
    for r in sorted(lignes, key=lambda x: x["ligne"]):
        sc = r["scores_corriges"][focus]
        val = r["valeurs"].get(focus)
        nom = (r.get("indicateur_fr") if i18n.get_lang() == "fr"
               and r.get("indicateur_fr") else r["indicateur"])
        # Un seul dégradé, du rouge au vert, sur la seule colonne de score :
        # la valeur brute ne se colore pas, faute d'échelle commune entre un
        # pourcentage de couvert et un indice standardisé.
        coul = ("#b4451f" if sc <= 3 else "#c98a2e" if sc <= 6 else "#2a6b3f")
        aff = (f'{_fmt(val, 2)} {r.get("unite", "")}'.strip()
               if isinstance(val, (int, float)) else "—")
        out.append(
            f'<tr><td style="padding:9px 10px;border-bottom:1px solid #f0f4f9;'
            f'color:#8a93a5;font-variant-numeric:tabular-nums">'
            f'{r["ligne"]}</td>'
            f'<td style="padding:9px 10px;border-bottom:1px solid #f0f4f9">'
            f'{_e(nom)}</td>'
            f'<td style="padding:9px 10px;border-bottom:1px solid #f0f4f9;'
            f'text-align:right;font-variant-numeric:tabular-nums;'
            f'color:#6b7590">{aff}</td>'
            f'<td style="padding:9px 10px;border-bottom:1px solid #f0f4f9;'
            f'text-align:right;font-variant-numeric:tabular-nums;'
            f'font-weight:700;color:{coul}">{sc} / 10</td></tr>')
    out.append('</table></div>')
    return ''.join(out)


def _tableau_recap(foret, pluie, saison):
    """Les dix sections, une ligne chacune, tous thèmes confondus."""
    entetes = [T("e_sc_section"), T("e_fr_foret"), T("e_fr_perte"),
               T("e_fr_taux"), T("e_fr_pluie"), T("e_fr_campagne"),
               T("e_fr_j50")]
    out = ['<div style="overflow-x:auto"><table style="width:100%;'
           'border-collapse:collapse;font-size:14.5px">']
    out.append('<tr>' + ''.join(
        f'<th style="text-align:{"left" if i == 0 else "right"};'
        f'padding:9px 10px;border-bottom:2px solid #e6ecf4;font-size:11.5px;'
        f'letter-spacing:.05em;text-transform:uppercase;color:#6b7590;'
        f'font-weight:700">{_e(h)}</th>' for i, h in enumerate(entetes))
        + '</tr>')
    C = 'padding:9px 10px;border-bottom:1px solid #f0f4f9;text-align:right;' \
        'font-variant-numeric:tabular-nums'
    ordre = sorted(foret["sections"].items(),
                   key=lambda kv: kv[1]["taux_annuel_net"])
    for sec, f in ordre:
        p = (pluie or {}).get("sections", {}).get(sec, {})
        s = (saison or {}).get("sections", {}).get(sec, {})
        part = s.get("ratio_normale")
        coul = ("#b4451f" if part is not None and part < 78
                else "#c98a2e" if part is not None and part < 90
                else "#2a6b3f")
        out.append(
            f'<tr><td style="padding:9px 10px;border-bottom:1px solid #f0f4f9">'
            f'{_e(sec)}</td>'
            f'<td style="{C};color:#6b7590">{_fmt(f["foret2000_pct"])} %</td>'
            f'<td style="{C}">{_fmt(f["perte_relative_pct"])} %</td>'
            f'<td style="{C};font-weight:700">'
            f'{_fmt(f["taux_annuel_net"], 2)} %</td>'
            f'<td style="{C};color:#6b7590">'
            f'{_fmt(p["normale_mm"], 0) + " mm" if p else "—"}</td>'
            f'<td style="{C};color:{coul};font-weight:700">'
            f'{_fmt(part, 0) + " %" if part is not None else "—"}</td>'
            f'<td style="{C};color:#6b7590">'
            f'{_fmt(s["j50_recent"]) if s else "—"}</td></tr>')
    out.append('</table></div>')
    return ''.join(out)


# --------------------------------------------- les quatre indices Sentinel
# Un onglet par indicateur, dans l'ordre où ils se lisent : la vigueur du
# couvert d'abord, l'eau qu'il contient ensuite, puis l'eau libre, puis ce
# qu'elle charrie. C'est la chaîne amont-aval de l'érosion.
INDICES = [
    ("ndvi", 33, "ndvi", "", "#2c6b34"),
    ("ndmi", 34, "ndmi", "", "#1d6f8e"),
    ("ndwi", 35, "ndwi", "", "#2a78d6"),
    ("ndti", 63, "ndti_eau", "", "#a86c2e"),
]


def _encart(cle_titre, corps, teinte="#cfe2f3"):
    return (f'<div style="border-left:3px solid {teinte};padding:2px 0 2px 14px;'
            f'margin:0 0 14px;max-width:92ch">'
            f'<div style="font-size:12px;letter-spacing:.06em;'
            f'text-transform:uppercase;color:#1a6bb0;font-weight:700">'
            f'{_e(T(cle_titre))}</div>'
            f'<div style="font-size:15.5px;color:#3c4761;line-height:1.6;'
            f'margin-top:3px">{corps}</div></div>')


def _onglet_indice(cle, ligne, champ, coul, res, indices, focus):
    """Un indicateur Sentinel-2 : ce qu'il mesure, comment le lire, ses pièges.

    L'interprétation est écrite avant les chiffres et non après. Un NDMI de
    0,18 ne dit rien à personne ; savoir qu'il chute avant le NDVI, et donc
    qu'il avertit, change ce qu'on regarde ensuite.
    """
    entree = next((r for r in (res or []) if r["ligne"] == ligne), None)
    with st.container(border=True):
        st.markdown(
            f'<div class="titre-bloc vert">{T("e_i_" + cle + "_titre")}</div>',
            unsafe_allow_html=True)
        st.markdown(
            f'<p style="font-size:12px;letter-spacing:.06em;'
            f'text-transform:uppercase;color:#8a93a5;font-weight:700;'
            f'margin:2px 0 12px">{T("e_i_ligne", n=ligne)}</p>',
            unsafe_allow_html=True)

        st.markdown(_encart("e_i_quoi", T("e_i_" + cle + "_quoi")),
                    unsafe_allow_html=True)
        st.markdown(_encart("e_i_lire", T("e_i_" + cle + "_lire"), coul),
                    unsafe_allow_html=True)
        st.markdown(_encart("e_i_gaffe", T("e_i_" + cle + "_gaffe"), "#f0d9a8"),
                    unsafe_allow_html=True)

        donnees = (indices or {}).get("sections") if indices else None
        if not donnees:
            st.markdown(
                f'<div style="background:#fdf8ee;border:1px solid #f0e2c4;'
                f'border-radius:12px;padding:14px 17px;margin:4px 0 0;'
                f'max-width:92ch">'
                f'<div style="font-size:12px;letter-spacing:.06em;'
                f'text-transform:uppercase;color:#a8690a;font-weight:700">'
                f'{_e(T("e_i_attente_titre"))}</div>'
                f'<p style="font-size:15.5px;color:#3c4761;line-height:1.6;'
                f'margin:4px 0 8px">{T("e_i_attente")}</p>'
                f'<p style="font-size:14px;color:#6b7590;line-height:1.7;'
                f'margin:0">{T("e_i_attente_etapes")}</p></div>',
                unsafe_allow_html=True)
            if entree and entree.get("echelle"):
                st.caption(f'{T("e_i_echelle")} — {entree["echelle"]}')
            st.caption(T("e_i_fenetre"))
            return

        _rendu_indice(cle, champ, coul, entree, indices, focus)


def _rendu_indice(cle, champ, coul, entree, indices, focus):
    """Chiffres, série et tableau, une fois l'export disponible."""
    secs = indices["sections"]
    annees = sorted(indices["periode_annees"], key=int)
    if focus == ENSEMBLE or focus not in secs:
        serie = _moyenne_series(secs, "serie_" + champ)
        st.caption(T("e_vue_ensemble_note"))
    else:
        serie = secs[focus]["serie_" + champ]

    ref = indices["reference"]
    dispo = [a for a in annees if str(a) in serie]
    if not dispo:
        st.info(T("e_absent"))
        return
    val_ref = [serie[str(a)] for a in dispo if a <= ref]
    val_rec = [serie[str(a)] for a in dispo if a > ref]
    m_ref = sum(val_ref) / len(val_ref) if val_ref else None
    m_rec = sum(val_rec) / len(val_rec) if val_rec else None
    variation = (100.0 * (m_rec - m_ref) / abs(m_ref)
                 if m_ref not in (None, 0) and m_rec is not None else None)

    c1, c2, c3 = st.columns(3)
    for col, lib, val, sous in [
            (c1, T("e_i_ref"), _fmt(m_ref, 3) if m_ref is not None else "—",
             T("e_i_ref_sous", a=dispo[0], b=ref)),
            (c2, T("e_i_recent"), _fmt(m_rec, 3) if m_rec is not None else "—",
             T("e_i_recent_sous", a=ref + 1, b=dispo[-1])),
            (c3, T("e_i_variation"),
             (f"{'+' if variation and variation > 0 else ''}"
              f"{_fmt(variation, 1)} %") if variation is not None else "—",
             T("e_i_variation_sous"))]:
        with col:
            st.markdown(map_render.cartouche_html(lib, val, "", sous,
                                                  couleur=coul),
                        unsafe_allow_html=True)

    svg = _serie_indice_svg(serie, m_ref, coul)
    components.html(
        '<div style="background:#ffffff;font-family:system-ui,-apple-system,'
        "'Segoe UI',sans-serif\">" + svg + "</div>",
        height=235, scrolling=False)
    st.caption(T("e_i_serie_note"))
    st.markdown(_tableau_indice(indices, champ, ref), unsafe_allow_html=True)
    if entree and entree.get("echelle"):
        st.caption(f'{T("e_i_echelle")} — {entree["echelle"]}')


def _serie_indice_svg(serie, reference, couleur, largeur=1040):
    """Série annuelle d'un indice, avec la moyenne de référence en pointillés.

    Une seule teinte : il n'y a qu'une grandeur, et elle n'a pas de « bon » ni
    de « mauvais » côté absolu — c'est l'écart à la référence qui compte, et il
    est tracé, pas colorié.
    """
    annees = sorted(serie, key=int)
    vals = [serie[a] for a in annees]
    vmin, vmax = min(vals + [reference]), max(vals + [reference])
    marge = (vmax - vmin) * 0.18 or 0.05
    vmin, vmax = vmin - marge, vmax + marge
    H, TOP, BAS, GAUCHE = 220, 22, 32, 62
    plot_h = H - TOP - BAS
    pas = (largeur - GAUCHE - 16) / max(len(annees), 1)
    barre = pas * 0.5

    def y_de(v):
        return TOP + plot_h * (1 - (v - vmin) / (vmax - vmin))

    parts = []
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        y = TOP + plot_h * (1 - frac)
        parts.append(f'<line x1="{GAUCHE}" y1="{y:.1f}" x2="{largeur - 16}" '
                     f'y2="{y:.1f}" stroke="#eef2f7" stroke-width="1"/>')
        parts.append(f'<text class="ig" x="{GAUCHE - 8}" y="{y + 4:.1f}" '
                     f'text-anchor="end">'
                     f'{vmin + (vmax - vmin) * frac:.2f}</text>')

    for i, (a, v) in enumerate(zip(annees, vals)):
        x = GAUCHE + i * pas + (pas - barre) / 2
        y = y_de(v)
        parts.append(
            f'<g><title>{a} — {v:.3f}</title><rect x="{x:.1f}" y="{y:.1f}" '
            f'width="{barre:.1f}" height="{max(y_de(vmin) - y, 1):.1f}" '
            f'rx="2" fill="{couleur}"/></g>')
        parts.append(f'<text class="ia" x="{x + barre / 2:.1f}" y="{H - 12}" '
                     f'text-anchor="middle">{a}</text>')

    if reference is not None:
        yr = y_de(reference)
        parts.append(f'<line x1="{GAUCHE}" y1="{yr:.1f}" x2="{largeur - 16}" '
                     f'y2="{yr:.1f}" stroke="#101728" stroke-width="1.5" '
                     f'stroke-dasharray="5 4"/>')
        parts.append(f'<text class="in" x="{largeur - 18}" y="{yr - 7:.1f}" '
                     f'text-anchor="end">'
                     f'{_e(T("e_i_ref_ligne", n=reference))}</text>')

    return f"""<svg viewBox="0 0 {largeur} {H}" width="100%"
     style="max-width:{largeur}px;display:block" role="img">
  <style>
    .ig{{font:11px system-ui,-apple-system,sans-serif;fill:#898781;
        font-variant-numeric:tabular-nums}}
    .ia{{font:11.5px system-ui,-apple-system,sans-serif;fill:#6b7590;
        font-variant-numeric:tabular-nums}}
    .in{{font:700 12px system-ui,-apple-system,sans-serif;fill:#101728;
        font-variant-numeric:tabular-nums}}
  </style>
  {''.join(parts)}
</svg>"""


def _tableau_indice(indices, champ, ref):
    """Les dix sections sur un indice : référence, récent, variation."""
    entetes = [T("e_sc_section"), T("e_i_ref"), T("e_i_recent"),
               T("e_i_variation"), T("e_i_eau")]
    out = ['<div style="overflow-x:auto"><table style="width:100%;'
           'border-collapse:collapse;font-size:14.5px">']
    out.append('<tr>' + ''.join(
        f'<th style="text-align:{"left" if i == 0 else "right"};'
        f'padding:9px 10px;border-bottom:2px solid #e6ecf4;font-size:11.5px;'
        f'letter-spacing:.05em;text-transform:uppercase;color:#6b7590;'
        f'font-weight:700">{_e(h)}</th>' for i, h in enumerate(entetes))
        + '</tr>')
    C = 'padding:9px 10px;border-bottom:1px solid #f0f4f9;text-align:right;' \
        'font-variant-numeric:tabular-nums'
    calcul = []
    for sec, d in indices["sections"].items():
        serie = d.get("serie_" + champ, {})
        av = [v for a, v in serie.items() if int(a) <= ref and v is not None]
        ap = [v for a, v in serie.items() if int(a) > ref and v is not None]
        if not av or not ap:
            calcul.append((sec, None, None, None, d.get("frac_eau_moy")))
            continue
        m_a, m_b = sum(av) / len(av), sum(ap) / len(ap)
        var = 100.0 * (m_b - m_a) / abs(m_a) if m_a else None
        calcul.append((sec, m_a, m_b, var, d.get("frac_eau_moy")))
    calcul.sort(key=lambda t: (t[3] is None, t[3]))
    for sec, m_a, m_b, var, eau in calcul:
        coul = ("#b4451f" if var is not None and var <= -15
                else "#c98a2e" if var is not None and var < -5 else "#2a6b3f")
        out.append(
            f'<tr><td style="padding:9px 10px;border-bottom:1px solid #f0f4f9">'
            f'{_e(sec)}</td>'
            f'<td style="{C};color:#6b7590">'
            f'{_fmt(m_a, 3) if m_a is not None else "—"}</td>'
            f'<td style="{C}">{_fmt(m_b, 3) if m_b is not None else "—"}</td>'
            f'<td style="{C};color:{coul};font-weight:700">'
            f'{(("+" if var > 0 else "") + _fmt(var, 1) + " %") if var is not None else "—"}</td>'
            f'<td style="{C};color:#8a93a5">'
            f'{_fmt(100 * eau, 2) + " %" if eau is not None else "—"}</td>'
            f'</tr>')
    out.append('</table></div>')
    return ''.join(out)


def _onglet_lacunes(res):
    manquants = {r["ligne"]: r for r in res
                 if r["calculable"] == "non"
                 and r["dimension"].startswith("III")}
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc ambre">{T("e_bloc5")}</div>',
                    unsafe_allow_html=True)
        st.markdown(
            f'<p style="font-size:16px;line-height:1.65;color:#3c4761;'
            f'margin:4px 0 12px;max-width:92ch">'
            f'{T("e_bloc5_texte", n=len(manquants))}</p>',
            unsafe_allow_html=True)
        for source, lignes in A_VENIR:
            presents = [manquants[lg] for lg in lignes if lg in manquants]
            if not presents:
                continue
            noms = " · ".join(
                _e(r.get("indicateur_fr") if i18n.get_lang() == "fr"
                   and r.get("indicateur_fr") else r["indicateur"])
                for r in presents)
            st.markdown(
                f'<div style="border-left:3px solid #cfe2f3;padding:2px 0 '
                f'2px 14px;margin:0 0 14px">'
                f'<div style="font-size:12px;letter-spacing:.06em;'
                f'text-transform:uppercase;color:#1a6bb0;font-weight:700">'
                f'{_e(T("e_src_" + source))} — {len(presents)}</div>'
                f'<div style="font-size:14.5px;color:#3c4761;'
                f'line-height:1.55;margin-top:3px">{noms}</div></div>',
                unsafe_allow_html=True)


def render():
    foret, res, pluie, grille, saison, indices = _charger()
    st.markdown(_styles(), unsafe_allow_html=True)

    col_logo, col_titre = st.columns([1, 6])
    with col_logo:
        st.markdown(
            f'<img src="data:image/png;base64,{assets.LOGO_APRI}" '
            f'style="width:118px;margin-top:6px">', unsafe_allow_html=True)
    with col_titre:
        st.title(T("e_titre"))
        st.markdown(
            '<p style="font-size:12.5px;color:#6b7590;letter-spacing:.06em;'
            'text-transform:uppercase;margin:-8px 0 0 2px;font-weight:600">'
            + T("e_sous_titre") + "</p>", unsafe_allow_html=True)

    if foret is None:
        st.info(T("e_absent"))
        st.stop()

    st.markdown(
        '<div style="background:#fff;border:1px solid #e3eaf3;border-left:5px '
        'solid #1a6bb0;border-radius:14px;padding:13px 17px;font-size:16px;'
        'color:#3c4761;box-shadow:0 1px 2px rgba(16,23,40,.05),'
        '0 8px 20px rgba(16,23,40,.06);margin:10px 0 6px">'
        + T("e_intro") + "</div>", unsafe_allow_html=True)

    # ------------------------------------------------- le sélecteur de tête
    # Un seul sélecteur pour tout l'onglet plutôt qu'un par bloc : on choisit
    # un territoire, puis on parcourt les thèmes sans avoir à le rechoisir à
    # chaque fois. « Ensemble » reste l'entrée par défaut — c'est la vue qui
    # permet de comparer, et les cartes n'ont de sens que là.
    dispo = [s for s in SECTIONS if s in foret["sections"]]
    col_sel, col_txt = st.columns([2, 3])
    with col_sel:
        focus = st.selectbox(T("e_focus"), [ENSEMBLE] + dispo,
                             format_func=_libelle_focus,
                             key=f"env_focus_{i18n.get_lang()}")
    with col_txt:
        st.markdown(
            f'<p style="font-size:13.5px;color:#6b7590;line-height:1.5;'
            f'margin:30px 0 0">{T("e_focus_aide")}</p>',
            unsafe_allow_html=True)

    # Un sous-onglet par indicateur, dans l'ordre de la chaîne physique :
    # le couvert, où il a disparu, ce qui reste vert, l'eau qu'il contient,
    # l'eau libre, ce qu'elle charrie, la pluie qui alimente tout cela.
    onglets = st.tabs(
        [T("e_o_foret"), T("e_o_defor")]
        + [T("e_o_" + cle) for cle, *_ in INDICES]
        + [T("e_o_pluie"), T("e_o_secheresse"), T("e_o_fiche"),
           T("e_o_lacunes")])

    with onglets[0]:
        _onglet_foret(foret, focus)

    with onglets[1]:
        if grille:
            _bloc_grille(grille, foret, focus)
        else:
            st.info(T("e_absent"))

    for i, (cle, ligne, champ, _u, coul) in enumerate(INDICES):
        with onglets[2 + i]:
            _onglet_indice(cle, ligne, champ, coul, res, indices, focus)

    n = 2 + len(INDICES)
    with onglets[n]:
        if pluie:
            _bloc_pluie(pluie, focus)
        else:
            st.info(T("e_absent"))

    with onglets[n + 1]:
        if saison:
            _bloc_saison(saison, focus)
        else:
            st.info(T("e_absent"))

    with onglets[n + 2]:
        _fiche_section(foret, pluie, saison, grille, res, focus)

    with onglets[n + 3]:
        if res:
            _onglet_lacunes(res)

    st.caption(T("e_source"))
    st.caption(T("credit"))
