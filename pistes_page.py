"""Onglet « Pistes d'action ».

Le cadre IRLA est net : les points de levier se construisent en atelier
participatif, à partir de diagrammes causaux, avec ceux qui vivent la situation.
Cet onglet ne prétend donc pas proposer des solutions. Il rassemble des
hypothèses de travail, chacune reliée au chiffre d'enquête qui la motive, au
levier systémique décrit par l'article, aux acteurs concernés et au risque
qu'elle porte — le format même de la « fiche d'action » de l'article, à ceci
près que l'atelier n'a pas encore eu lieu et que la page le dit.
"""

import json
import os

import streamlit as st

import assets
import i18n
import map_render
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

TEINTE = ["", "vert", "ambre"]


def _trouver(nom):
    for c in (os.path.join(DATA, nom), os.path.join(APP_DIR, nom)):
        if os.path.exists(c):
            return c
    return None


@st.cache_data(show_spinner=False)
def _charger():
    chemins = {n: _trouver(n) for n in ("pistes.json", "saillants.json")}
    if chemins["pistes.json"] is None:
        return None, None
    with open(chemins["pistes.json"], encoding="utf-8") as f:
        pistes = json.load(f)
    saillants = None
    if chemins["saillants.json"]:
        with open(chemins["saillants.json"], encoding="utf-8") as f:
            saillants = json.load(f)
    return pistes, saillants


def _bulle(cle):
    fn = getattr(map_render, "bulle_notion", None)
    return fn(cle) if fn else ""


def _styles():
    fn = getattr(map_render, "styles_bulle", None)
    return fn() if fn else ""


def _t(o, champ):
    return o.get(f"{champ}_{i18n.get_lang()}") or o.get(f"{champ}_en", "")


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _chiffres_du_constat(saillants, cle):
    """Les chiffres d'enquête qui motivent la piste, repris tels quels."""
    if not saillants or not cle:
        return []
    for c in saillants["constats"]:
        if c["cle"] == cle:
            return [(f.get(f"libelle_{i18n.get_lang()}") or f["libelle_en"],
                     f["pct"]) for f in c["figures"] if f["pct"] is not None]
    return []


def _encart(libelle, texte, couleur, fond):
    return (f'<div style="background:{fond};border-left:4px solid {couleur};'
            f'border-radius:10px;padding:11px 15px;margin:12px 0 0">'
            f'<div style="font-size:11.5px;letter-spacing:.06em;'
            f'text-transform:uppercase;color:{couleur};font-weight:700;'
            f'margin-bottom:3px">{_e(libelle)}</div>'
            f'<div style="font-size:15px;color:#3c4761;line-height:1.55">'
            f'{_e(texte)}</div></div>')


def render():
    pistes, saillants = _charger()
    st.markdown(_styles(), unsafe_allow_html=True)

    col_logo, col_titre = st.columns([1, 6])
    with col_logo:
        st.markdown(
            f'<img src="data:image/png;base64,{assets.LOGO_APRI}" '
            f'style="width:118px;margin-top:6px">', unsafe_allow_html=True)
    with col_titre:
        st.title(T("p_titre"))
        st.markdown(
            '<p style="font-size:12.5px;color:#6b7590;letter-spacing:.06em;'
            'text-transform:uppercase;margin:-8px 0 0 2px;font-weight:600">'
            + T("p_sous_titre") + "</p>", unsafe_allow_html=True)

    if pistes is None:
        st.error("pistes.json")
        st.stop()

    # ---- le cadre, avant toute piste --------------------------------------
    st.markdown(
        '<div style="background:#fdf7ec;border:1px solid #f0dcb8;border-left:5px '
        'solid #d99b28;border-radius:14px;padding:14px 18px;font-size:15.5px;'
        'color:#5b4a2b;line-height:1.6;margin:10px 0 8px">'
        + _t(pistes, "avert") + "</div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("p_bloc_cadre")}</div>',
                    unsafe_allow_html=True)
        st.markdown(
            f'<p style="font-size:16px;line-height:1.68;color:#3c4761;'
            f'margin:4px 0 8px;max-width:92ch">{_t(pistes, "cadre")}</p>',
            unsafe_allow_html=True)
        st.markdown(
            '<p style="font-size:15px;color:#3c4761;margin:6px 0 0">'
            + _bulle("point_de_levier") + " &nbsp;·&nbsp; "
            + _bulle("boucle_retroaction") + " &nbsp;·&nbsp; "
            + _bulle("appropriation") + "</p>", unsafe_allow_html=True)

    # ---- les pistes --------------------------------------------------------
    for k, p in enumerate(pistes["pistes"]):
        with st.container(border=True):
            st.markdown(
                f'<div class="titre-bloc {TEINTE[k % len(TEINTE)]}">'
                f'{T("p_piste_n", n=k + 1)}</div>', unsafe_allow_html=True)
            st.markdown(
                f'<h3 style="margin:2px 0 8px">{_e(_t(p, "titre"))}</h3>',
                unsafe_allow_html=True)
            st.markdown(
                f'<p style="font-size:16px;line-height:1.68;color:#3c4761;'
                f'margin:0 0 6px;max-width:92ch">{_t(p, "corps")}</p>',
                unsafe_allow_html=True)

            chiffres = _chiffres_du_constat(saillants, p.get("constat"))
            if chiffres:
                pastilles = "".join(
                    f'<span style="display:inline-flex;align-items:baseline;'
                    f'gap:7px;background:#f4f8fc;border:1px solid #e2e9f2;'
                    f'border-radius:10px;padding:7px 13px;margin:0 8px 8px 0">'
                    f'<strong style="font-size:16px;color:#101728;'
                    f'font-variant-numeric:tabular-nums">{v:.1f} %</strong>'
                    f'<span style="font-size:13.5px;color:#3c4761">'
                    f'{_e(lab)}</span></span>' for lab, v in chiffres)
                st.markdown(
                    f'<div style="margin-top:10px"><div style="font-size:11.5px;'
                    f'letter-spacing:.06em;text-transform:uppercase;'
                    f'color:#6b7590;font-weight:700;margin-bottom:7px">'
                    f'{_e(T("p_chiffres"))}</div>{pastilles}</div>',
                    unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(_encart(T("p_acteurs"), _t(p, "acteurs"),
                                    "#1a6bb0", "#eef5fb"),
                            unsafe_allow_html=True)
            with c2:
                st.markdown(_encart(T("p_risque"), _t(p, "risque"),
                                    "#a8690a", "#fdf7ec"),
                            unsafe_allow_html=True)

    st.caption(T("p_source"))
    st.caption(T("credit"))
