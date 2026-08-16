"""Onglet « Constats saillants » — ce que disent les 1211 enquêtes.

Trois niveaux de lecture, du plus synthétique au plus brut :

  1. huit constats thématiques, avec un texte qui relie les chiffres entre eux ;
  2. une fiche par section communale ou par profil — femmes, jeunes, catégorie
     économique, paysage — qui montre l'écart au national plutôt qu'un chiffre
     isolé ;
  3. la liste automatique, triée par score, sans aucun tri éditorial.

Tous les chiffres viennent de saillants.json, recalculé à chaque exécution de
compute_saillants.py depuis le cache d'enquête. Aucun n'est écrit en dur ici.
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

TEINTE = ["", "vert", "ambre", "", "vert", "ambre", "", "vert"]

PROFIL_CLE = {
    "Homme": "hommes", "Femme": "femmes", "Cat A": "cat_a", "Cat B": "cat_b",
    "Cat C": "cat_c", "<25": "age_25", "25-39": "age_25_39",
    "40-59": "age_40_59", "60+": "age_60", "Littoral": "littoral",
    "Montagne": "montagne",
}

# Les quatre chiffres mis en tête : les plus bas de tout l'indice, choisis par
# leur score et non à la main.
TETE = [("preparation", 0), ("energie", 0), ("alimentation", 3), ("education", 2)]


def _trouver(nom):
    for c in (os.path.join(DATA, nom), os.path.join(APP_DIR, nom)):
        if os.path.exists(c):
            return c
    return None


@st.cache_data(show_spinner=False)
def _charger():
    c = _trouver("saillants.json")
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


def _lib(o):
    return o.get(f"libelle_{i18n.get_lang()}") or o.get("libelle_en", "")


def _txt(c, champ):
    return c.get(f"{champ}_{i18n.get_lang()}") or c.get(f"{champ}_en", "")


def _profil_nom(code):
    return T(PROFIL_CLE[code]) if code in PROFIL_CLE else code


def _barres(figures, hauteur_min=0):
    """Les figures d'un constat, en barres, avec le score APRI en annotation."""
    rows, annot = [], {}
    for f in figures:
        lab = _lib(f)
        rows.append((lab, f["pct"]))
        if f.get("score") is not None:
            annot[lab] = T("s_score_annot", s=f["score"])
    svg = map_render.render_score_bars_svg(rows, vmax=100, width=1040,
                                           unite="%", annotations=annot)
    components.html(
        '<div style="background:#ffffff;font-family:system-ui,-apple-system,'
        "'Segoe UI',sans-serif\">" + svg + "</div>",
        height=max(len(rows) * 28 + 30, hauteur_min), scrolling=False)


def render():
    doc = _charger()
    st.markdown(_styles(), unsafe_allow_html=True)

    col_logo, col_titre = st.columns([1, 6])
    with col_logo:
        st.markdown(
            f'<img src="data:image/png;base64,{assets.LOGO_APRI}" '
            f'style="width:118px;margin-top:6px">', unsafe_allow_html=True)
    with col_titre:
        st.title(T("s_titre"))
        st.markdown(
            '<p style="font-size:12.5px;color:#6b7590;letter-spacing:.06em;'
            'text-transform:uppercase;margin:-8px 0 0 2px;font-weight:600">'
            + T("s_sous_titre") + "</p>", unsafe_allow_html=True)

    if doc is None:
        st.error("saillants.json")
        st.stop()

    constats = {c["cle"]: c for c in doc["constats"]}
    ordre = [c["cle"] for c in doc["constats"]]

    st.markdown(
        '<div style="background:#fff;border:1px solid #e3eaf3;border-left:5px '
        'solid #1a6bb0;border-radius:14px;padding:13px 17px;font-size:16px;'
        'color:#3c4761;box-shadow:0 1px 2px rgba(16,23,40,.05),'
        '0 8px 20px rgba(16,23,40,.06);margin:10px 0 6px">'
        + T("s_intro", n=doc["base"], q=doc["n_questions"]) + "</div>",
        unsafe_allow_html=True)

    # ---------------------------------------------------- les quatre en tête
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc ambre">{T("s_bloc0")}</div>',
                    unsafe_allow_html=True)
        cols = st.columns(4)
        for col, (cle, i) in zip(cols, TETE):
            f = constats[cle]["figures"][i]
            coul = map_render.RAMP_APRI[
                map_render.bin_of(f["score"] if f.get("score") is not None
                                  else 0, map_render.SEUILS_APRI)][0]
            with col:
                st.markdown(
                    map_render.cartouche_html(
                        _lib(f), round(f["pct"], 1), "%",
                        T("s_des_menages"), couleur=coul),
                    unsafe_allow_html=True)
        st.caption(T("s_bloc0_note"))

    # ------------------------------------------------- les huit constats
    for k, cle in enumerate(ordre):
        c = constats[cle]
        with st.container(border=True):
            st.markdown(
                f'<div class="titre-bloc {TEINTE[k % len(TEINTE)]}">'
                f'{k + 1} · {_txt(c, "titre")}</div>', unsafe_allow_html=True)
            st.markdown(
                f'<p style="font-size:16px;line-height:1.65;color:#3c4761;'
                f'margin:4px 0 12px;max-width:92ch">{_txt(c, "texte")}</p>',
                unsafe_allow_html=True)
            _barres(c["figures"])

    # ----------------------------------------- fiche d'un profil / d'une section
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc vert">{T("s_bloc_profil")}</div>',
                    unsafe_allow_html=True)
        st.caption(T("s_bloc_profil_note"))

        choix = st.selectbox(
            T("s_choisir_profil"), doc["profils"] + SECTIONS,
            format_func=lambda c: _profil_nom(c),
            key=f"saillants_profil_{i18n.get_lang()}")
        n_profil = doc["effectifs"].get(choix, 0)
        est_section = choix in SECTIONS
        st.markdown(
            f'<p style="font-size:15px;color:#3c4761;margin:0 0 10px">'
            f'{T("s_profil_base", g=_profil_nom(choix), n=n_profil, t=doc["base"])}'
            f'</p>', unsafe_allow_html=True)

        lignes = []
        for cle in ordre:
            for f in constats[cle]["figures"]:
                source = f["valeurs"] if est_section else f["profils"]
                v = source.get(choix)
                if v is None or f["pct"] is None:
                    continue
                lignes.append((_lib(f), v, v - f["pct"]))
        st.markdown(_tableau_ecarts(lignes), unsafe_allow_html=True)
        st.caption(T("s_profil_lecture"))

    # ---------------------------------------------------- liste automatique
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("s_bloc_auto")}</div>',
                    unsafe_allow_html=True)
        st.caption(T("s_bloc_auto_note"))
        combien = st.slider(T("s_combien"), 5, 40, 15,
                            key=f"saillants_n_{i18n.get_lang()}")
        indic = doc["auto_indicateurs"][:combien]
        rows = [(_lib(r), r["pct"]) for r in indic]
        annot = {_lib(r): T("s_score_annot", s=r["score"]) for r in indic}
        svg = map_render.render_score_bars_svg(
            rows, vmax=100, width=1040, unite="%", annotations=annot)
        components.html(
            '<div style="background:#ffffff;font-family:system-ui,-apple-system,'
            "'Segoe UI',sans-serif\">" + svg + "</div>",
            height=len(rows) * 28 + 30, scrolling=False)

        with st.expander(T("s_reponses_massives")):
            st.caption(T("s_reponses_massives_note"))
            for r in doc["auto_reponses"][:combien]:
                st.markdown(
                    f'<div style="border-bottom:1px solid #eef2f7;padding:7px 0">'
                    f'<span style="font-variant-numeric:tabular-nums;'
                    f'font-weight:700;color:#101728;font-size:16px">'
                    f'{r["pct"]:.1f} %</span> '
                    f'<span style="color:#3c4761;font-size:15px">'
                    f'{r["question"]} — « {r["modalite"]} »</span></div>',
                    unsafe_allow_html=True)

    st.caption(T("s_source", n=doc["base"], q=doc["n_questions"]))
    st.caption(T("credit"))


def _tableau_ecarts(lignes):
    """Chaque chiffre du profil, avec son écart au national en couleur.

    L'écart compte plus que la valeur : 76 % de ménages ayant sauté un repas ne
    dit rien tant qu'on ignore que la moyenne est à 67 %.
    """
    if not lignes:
        return f'<p style="color:#6b7590">{T("s_profil_vide")}</p>'
    out = ['<div style="display:grid;grid-template-columns:1fr auto auto;'
           'gap:0 18px;align-items:center">']
    for lab, v, ecart in lignes:
        if abs(ecart) < 2:
            coul, fond, fleche = "#6b7590", "#f4f6f9", "="
        elif ecart > 0:
            coul, fond, fleche = "#a8320f", "#fdeee9", "▲"
        else:
            coul, fond, fleche = "#1f6b3d", "#e8f4ec", "▼"
        out.append(
            f'<div style="font-size:15px;color:#3c4761;padding:8px 0;'
            f'border-bottom:1px solid #eef2f7">{lab}</div>'
            f'<div style="font-size:16px;font-weight:700;color:#101728;'
            f'font-variant-numeric:tabular-nums;padding:8px 0;'
            f'border-bottom:1px solid #eef2f7;text-align:right">'
            f'{v:.1f} %</div>'
            f'<div style="padding:8px 0;border-bottom:1px solid #eef2f7;'
            f'text-align:right"><span style="background:{fond};color:{coul};'
            f'border-radius:999px;padding:3px 10px;font-size:13.5px;'
            f'font-weight:600;font-variant-numeric:tabular-nums">'
            f'{fleche} {abs(ecart):.1f}</span></div>')
    out.append("</div>")
    return "".join(out)
