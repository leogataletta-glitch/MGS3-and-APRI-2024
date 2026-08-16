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
    ("chirps", [43, 44, 45, 46]),
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
    chemins = {n: _trouver(n) for n in ("foret.json", "resultats.json")}
    foret = res = None
    if chemins["foret.json"]:
        with open(chemins["foret.json"], encoding="utf-8") as f:
            foret = json.load(f)
    if chemins["resultats.json"]:
        with open(chemins["resultats.json"], encoding="utf-8") as f:
            res = json.load(f)
    return foret, res


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


def render():
    foret, res = _charger()
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

    ens = foret["ensemble"]
    st.markdown(
        '<div style="background:#fff;border:1px solid #e3eaf3;border-left:5px '
        'solid #1a6bb0;border-radius:14px;padding:13px 17px;font-size:16px;'
        'color:#3c4761;box-shadow:0 1px 2px rgba(16,23,40,.05),'
        '0 8px 20px rgba(16,23,40,.06);margin:10px 0 6px">'
        + T("e_intro") + "</div>", unsafe_allow_html=True)

    # ------------------------------------------------------------ chiffres
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc vert">{T("e_bloc1")}</div>',
                    unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        # Les valeurs sont mises en forme ici plutôt que laissées au cartouche :
        # une surface se lit en entiers avec une espace de millier, un taux
        # annuel demande deux décimales — à un dixième près, −0,5 et −0,54 se
        # confondent alors qu'ils ne sont pas dans la même classe de score.
        cartes = [
            (c1, T("e_c_foret2000"), _fmt(ens["foret2000_ha"], 0), "ha",
             T("e_c_foret2000_sous", p=_fmt(ens["foret2000_pct"])), "#5b9c5a"),
            (c2, T("e_c_perte"), _fmt(ens["perte_totale_ha"], 0), "ha",
             T("e_c_perte_sous", p=_fmt(ens["perte_relative_pct"])), "#b5451f"),
            (c3, T("e_c_taux"), _fmt(ens["taux_annuel_net"], 2), "%",
             T("e_c_taux_sous"), "#eb9d3a"),
            (c4, T("e_c_chronique"), _fmt(ens["taux_annuel_hors_choc"], 2), "%",
             T("e_c_chronique_sous"), "#7ba05b"),
        ]
        for col, lib, val, unite, sous, coul in cartes:
            with col:
                st.markdown(
                    map_render.cartouche_html(lib, val, unite, sous,
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
            f'{T("e_bloc2_texte", p=_fmt(ens["part_choc_pct"], 0))}</p>',
            unsafe_allow_html=True)
        svg = _serie_annuelle_svg(ens["pertes_annuelles_ha"], annee_pic=2016)
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
        valeurs = {s: foret["sections"].get(s, {}).get(cle) for s in SECTIONS}
        seuils = map_render.nice_thresholds(
            [v for v in valeurs.values() if v is not None])
        infos = {s: T("e_info_carte",
                      f=_fmt(foret["sections"][s]["foret2000_ha"], 0))
                 for s in SECTIONS if s in foret["sections"]}
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

    # ------------------------------------------------------------ le détail
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc vert">{T("e_bloc4")}</div>',
                    unsafe_allow_html=True)
        st.caption(T("e_bloc4_note"))
        st.markdown(_tableau_sections(foret), unsafe_allow_html=True)

    # -------------------------------------------------- ce qui manque encore
    if res:
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

    st.caption(T("e_source"))
    st.caption(T("credit"))
