"""Onglet « Tissu associatif » — Organisations Communautaires de Base.

Les données viennent d'une enquête distincte de l'enquête ménage : 34 fiches
d'identité d'organisations, recueillies dans 8 des 10 sections communales.
L'unité d'analyse est l'organisation, jamais le foyer — c'est rappelé partout,
parce qu'un pourcentage lu sur la mauvaise unité ne veut rien dire.
"""

import json
import os

import pandas as pd
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

DIM_CLE = {
    "II. INSTITUTIONAL, TECHNOLOGICAL, AND GOVERNANCE  DIMENSION": "dim2",
    "V. SOCIAL AND COMMUNITY DIMENSION": "dim5",
}


def _trouver(nom):
    for c in (os.path.join(DATA, nom), os.path.join(APP_DIR, nom)):
        if os.path.exists(c):
            return c
    return None


@st.cache_data(show_spinner=False)
def _charger():
    c = _trouver("ocb.json")
    if c is None:
        return None
    with open(c, encoding="utf-8") as f:
        return json.load(f)


def _bulle(cle):
    fn = getattr(map_render, "bulle_notion", None)
    return fn(cle) if fn else ""


def _styles():
    fn = getattr(map_render, "styles_bulle", None)
    return fn() if fn else ""


def _nom(ind):
    if i18n.get_lang() == "fr" and ind.get("indicateur_fr"):
        return ind["indicateur_fr"]
    return ind["indicateur"]


def _metrique(ind):
    if i18n.get_lang() == "fr" and ind.get("metrique_fr"):
        return ind["metrique_fr"]
    return ind.get("metrique", "")


def render():
    doc = _charger()
    st.markdown(_styles(), unsafe_allow_html=True)

    col_logo, col_titre = st.columns([1, 6])
    with col_logo:
        st.markdown(
            f'<img src="data:image/png;base64,{assets.LOGO_APRI}" '
            f'style="width:118px;margin-top:6px">', unsafe_allow_html=True)
    with col_titre:
        st.title(T("o_titre"))
        st.markdown(
            '<p style="font-size:12.5px;color:#6b7590;letter-spacing:.06em;'
            'text-transform:uppercase;margin:-8px 0 0 2px;font-weight:600">'
            + T("o_sous_titre") + "</p>", unsafe_allow_html=True)

    if doc is None:
        st.error("ocb.json")
        st.stop()

    d = doc["descriptif"]
    indicateurs = doc["indicateurs"]
    absentes = doc.get("sections_sans_donnee", [])

    st.markdown(
        '<div style="background:#fff;border:1px solid #e3eaf3;border-left:5px '
        'solid #1a6bb0;border-radius:14px;padding:13px 17px;font-size:16px;'
        'color:#3c4761;box-shadow:0 1px 2px rgba(16,23,40,.05),'
        '0 8px 20px rgba(16,23,40,.06);margin:10px 0 6px">'
        + T("o_intro", n=d["n_fiches"], s=d["n_sections"]) + "</div>",
        unsafe_allow_html=True)

    if absentes:
        st.markdown(
            '<div style="background:#fdf7ec;border:1px solid #f0dcb8;'
            'border-left:5px solid #d99b28;border-radius:14px;padding:13px 17px;'
            'font-size:15.5px;color:#5b4a2b;margin:0 0 12px">'
            + T("o_avert_absentes", s=f" {T('et')} ".join(absentes)) + "</div>",
            unsafe_allow_html=True)

    # ------------------------------------------------------------- chiffres
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("o_bloc1")}</div>',
                    unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        cartes = [
            (c1, T("o_c_organisations"), d["n_fiches"], "",
             T("o_c_organisations_sous", s=d["n_sections"]), "#2a78d6"),
            (c2, T("o_c_femmes"),
             next(i["valeurs"]["Total"] for i in indicateurs
                  if i["cle"] == "femme_direction"), "%",
             T("o_c_femmes_sous"), "#5b9c5a"),
            (c3, T("o_c_partenariat"),
             next(i["valeurs"]["Total"] for i in indicateurs
                  if i["cle"] == "partenariat"), "%",
             T("o_c_partenariat_sous"), "#2a78d6"),
            (c4, T("o_c_note"), d["note_moyenne"], "/ 10",
             T("o_c_note_sous", n=d["note_n"]), "#a8690a"),
        ]
        for col, libelle, valeur, unite, sous, coul in cartes:
            with col:
                st.markdown(
                    map_render.cartouche_html(libelle, valeur, unite, sous,
                                              couleur=coul),
                    unsafe_allow_html=True)
        st.markdown(
            '<p style="font-size:15px;color:#3c4761;margin:10px 0 0">'
            + _bulle("capital_social_liens") + " &nbsp;·&nbsp; "
            + _bulle("attributs_aaa") + "</p>", unsafe_allow_html=True)

    # ------------------------------------------------------------ la carte
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc ambre">{T("o_bloc2")}</div>',
                    unsafe_allow_html=True)
        densite = next(i for i in indicateurs if i["cle"] == "densite")
        choix = st.selectbox(
            T("o_quoi_carto"),
            [densite["ligne"]] + [i["ligne"] for i in indicateurs
                                  if i["cle"] != "densite"],
            format_func=lambda lg: _nom(
                next(i for i in indicateurs if i["ligne"] == lg)),
            key=f"ocb_carte_{i18n.get_lang()}")
        ind = next(i for i in indicateurs if i["ligne"] == choix)

        st.caption(_metrique(ind))
        valeurs = {s: ind["valeurs"].get(s) for s in SECTIONS}
        unite = "" if ind["cle"] == "densite" else "%"
        # Un effectif d'organisations se lit en entiers : des seuils à 2,5 ou
        # 7,5 n'auraient aucun sens pour un décompte.
        seuils = ([0.5, 2.5, 4.5] if ind["cle"] == "densite"
                  else map_render.nice_thresholds(
                      [v for v in valeurs.values() if v is not None]))
        infos = {s: T("o_info_carte", n=ind["n"].get(s, 0)) for s in SECTIONS}
        hauteur = 660
        svg, seuils_ret, mode = map_render.render_map_svg(
            valeurs, {s: ind["n"].get(s, 0) for s in SECTIONS}, seuils,
            height=hauteur, polarity="eleve_bon", unite=unite, infos=infos)
        legende = "".join(
            f'<span style="display:inline-flex;align-items:center;gap:7px;'
            f'margin-right:18px"><span style="width:22px;height:12px;'
            f'border-radius:3px;background:{c};box-shadow:inset 0 0 0 1px '
            f'rgba(0,0,0,.12)"></span><span style="font-size:13px;color:#52514e">'
            f'{lab}</span></span>'
            for c, lab in map_render.legend_items(seuils_ret, "eleve_bon", unite))
        components.html(
            '<div style="font-family:system-ui,-apple-system,\'Segoe UI\','
            'sans-serif;background:#ffffff"><div style="margin:0 0 8px">'
            f'<span style="font-size:11.5px;color:#898781;letter-spacing:.05em;'
            f'margin-right:14px">{T("legende_seuils")}</span>{legende}</div>'
            f'{svg}</div>', height=hauteur + 46, scrolling=False)
        st.caption(T("o_carte_note"))

    # -------------------------------------------------- tous les indicateurs
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc vert">{T("o_bloc3")}</div>',
                    unsafe_allow_html=True)
        st.caption(T("o_bloc3_note"))
        # Libellé court : le graphique en barres réserve une largeur fixe au
        # texte, et un nom d'indicateur complet y serait coupé au milieu.
        courts = [(T("o_court_" + i["cle"]), i["valeurs"]["Total"],
                   i["scores"]["Total"]) for i in indicateurs
                  if i["cle"] != "densite"]
        courts.sort(key=lambda x: -(x[1] or 0))
        rows = [(lab, v) for lab, v, _ in courts]
        annot = {lab: T("o_score_annot", s=sc) for lab, _, sc in courts}
        svg = map_render.render_score_bars_svg(
            rows, vmax=100, width=1040, unite="%", annotations=annot)
        components.html(
            '<div style="background:#ffffff;font-family:system-ui,'
            '-apple-system,\'Segoe UI\',sans-serif">' + svg + "</div>",
            height=len(rows) * 28 + 34, scrolling=False)

    # ---------------------------------------------------- les organisations
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("o_bloc4")}</div>',
                    unsafe_allow_html=True)
        sec_choix = st.multiselect(T("section_communale"), SECTIONS,
                                   key=f"ocb_sec_{i18n.get_lang()}")
        fiches = [f for f in doc["fiches"]
                  if not sec_choix or f["section"] in sec_choix]
        OUI, NON, RIEN = T("oui"), T("non"), "—"

        def trois(v):
            return RIEN if v is None else (OUI if v else NON)

        df = pd.DataFrame([{
            T("o_col_nom"): f["nom"],
            T("section_communale"): f["section"],
            T("o_col_partenariat"): trois(f["partenariat"]),
            T("o_col_duree"): f["duree"] or RIEN,
            T("o_col_note"): f["note_partenariat"] if f["note_partenariat"]
            is not None else None,
            T("o_col_soutien"): trois(f["soutien"]),
            T("o_col_autorites"): trois(f["autorites"]),
            T("o_col_ong_int"): trois(f["ong_int"]),
            T("o_col_femme"): trois(f["femme_direction"]),
            T("o_col_jeune"): trois(f["jeune_direction"]),
        } for f in fiches])
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(T("o_table_note", n=len(fiches)))

    st.caption(T("o_source"))
    st.caption(T("credit"))
