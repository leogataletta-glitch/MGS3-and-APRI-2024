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


def render(entete=True):
    doc = _charger()
    st.markdown(_styles(), unsafe_allow_html=True)

    if entete:
        st.title(T("o_titre"))
        st.markdown(
            '<p style="font-size:11.5px;color:#6b7590;letter-spacing:.06em;'
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
        'solid #1a6bb0;border-radius:14px;padding:13px 17px;font-size:14.5px;'
        'color:#3c4761;box-shadow:0 1px 2px rgba(16,23,40,.05),'
        '0 8px 20px rgba(16,23,40,.06);margin:10px 0 6px">'
        + T("o_intro", n=d["n_fiches"], s=d["n_sections"]) + "</div>",
        unsafe_allow_html=True)

    if absentes:
        st.markdown(
            '<div style="background:#fdf7ec;border:1px solid #f0dcb8;'
            'border-left:5px solid #d99b28;border-radius:14px;padding:13px 17px;'
            'font-size:14.5px;color:#5b4a2b;margin:0 0 12px">'
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
            '<p style="font-size:14px;color:#3c4761;margin:10px 0 0">'
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
            f'rgba(0,0,0,.12)"></span><span style="font-size:12px;color:#52514e">'
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
            T("o_col_duree"): _rep(f["duree"]) or RIEN,
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

    # ------------------------------------------------------------ la fiche
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc vert">{T("o_bloc5")}</div>',
                    unsafe_allow_html=True)
        st.caption(T("o_bloc5_note"))
        if not fiches:
            st.info(T("o_fiche_vide"))
        else:
            index = st.selectbox(
                T("o_choisir_organisation"), list(range(len(fiches))),
                format_func=lambda i: f"{fiches[i]['nom']}  ·  {fiches[i]['section']}",
                key=f"ocb_fiche_{i18n.get_lang()}_{len(fiches)}")
            st.markdown(_fiche_html(fiches[index]), unsafe_allow_html=True)

    st.caption(T("o_source"))
    st.caption(T("credit"))


# ----------------------------------------------------------------------
# La fiche d'une organisation
# ----------------------------------------------------------------------
def _e(t):
    """Échappe le texte saisi sur le terrain avant de l'injecter dans le HTML."""
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _rep(t):
    """Traduit les options fermées de l'enquête, saisies en français."""
    fn = getattr(i18n, "reponse", None)
    return fn(t) if fn else t


def _puces(valeur):
    """Les questions à choix multiples sortent de KoBo en libellés recollés.

    « Oui, matériels Oui, renforcement de capacités humaines » est une seule
    chaîne : on la recoupe sur les débuts d'option connus plutôt que de
    l'afficher telle quelle, illisible.
    """
    if not valeur:
        return []
    texte = str(valeur).strip()
    for sep in ("Oui, ", "Non, "):
        if texte.count(sep) > 1:
            morceaux = [m.strip() for m in texte.split(sep) if m.strip()]
            return [sep + m for m in morceaux]
    return [texte]


def _ligne(libelle, valeur, pleine=False):
    """Une ligne de fiche : intitulé discret au-dessus, réponse lisible dessous."""
    if valeur in (None, "", [], "—"):
        return ""
    if isinstance(valeur, list):
        valeur = " · ".join(_e(_rep(v)) for v in valeur)
    else:
        valeur = _e(_rep(valeur))
    largeur = "100%" if pleine else "auto"
    return (f'<div style="margin:0 0 12px;width:{largeur}">'
            f'<div style="font-size:11.5px;letter-spacing:.06em;'
            f'text-transform:uppercase;color:#6b7590;font-weight:700;'
            f'margin-bottom:2px">{_e(libelle)}</div>'
            f'<div style="font-size:14.5px;color:#101728;line-height:1.5">'
            f'{valeur}</div></div>')


def _pastille(texte, actif):
    fond, bord, encre = (("#e8f4ec", "#bcdcc7", "#1f6b3d") if actif
                         else ("#f4f6f9", "#e2e7ee", "#8b93a3"))
    marque = "✓" if actif else "·"
    return (f'<span style="display:inline-flex;align-items:center;gap:6px;'
            f'background:{fond};border:1px solid {bord};border-radius:999px;'
            f'padding:5px 12px;margin:0 7px 7px 0;font-size:12.5px;'
            f'color:{encre}"><strong>{marque}</strong>{_e(_rep(texte))}</span>')


def _titre_partie(texte):
    return (f'<div style="display:flex;align-items:center;gap:10px;'
            f'margin:22px 0 12px"><span style="font-family:Inter,'
            f'system-ui,sans-serif;font-size:11px;font-weight:700;'
            f'letter-spacing:.08em;text-transform:uppercase;color:#1a6bb0;'
            f'background:#eaf3fb;padding:5px 12px;border-radius:999px">'
            f'{_e(texte)}</span><span style="flex:1;height:1px;'
            f'background:#e6ecf4"></span></div>')


def _colonnes(*blocs):
    utiles = [b for b in blocs if b]
    if not utiles:
        return ""
    cellules = "".join(f'<div style="flex:1;min-width:250px">{b}</div>'
                       for b in utiles)
    return f'<div style="display:flex;gap:34px;flex-wrap:wrap">{cellules}</div>'


def _fiche_html(f):
    OUI, NON = T("oui"), T("non")

    def trois(v):
        return None if v is None else (OUI if v else NON)

    note = f.get("note_partenariat")
    note_txt = (f'{note:.0f} / 10'.replace('.', ',') if note is not None
                else None)
    # Plusieurs organisations ont répondu à la question sur la part de femmes par
    # un effectif de membres. On n'affiche « % » que lorsque la réponse se lit
    # vraiment comme une proportion ; sinon on montre ce qui a été saisi, tel quel.
    femmes = f.get("femmes_pct")
    if femmes is not None:
        femmes_lib, femmes_txt = T("o_f_femmes"), f'{femmes:.0f} %'
    elif f.get("femmes_brut"):
        femmes_lib, femmes_txt = T("o_f_femmes_brut"), f["femmes_brut"]
    else:
        femmes_lib, femmes_txt = T("o_f_femmes"), None

    entete = (
        f'<div style="border-bottom:1px solid #e6ecf4;padding:0 0 14px">'
        f'<div style="font-size:11.5px;letter-spacing:.07em;'
        f'text-transform:uppercase;color:#1a6bb0;font-weight:700">'
        f'{_e(T("o_f_organisation"))}</div>'
        f'<div style="font-family:Inter,system-ui,sans-serif;'
        f'font-size:18.5px;font-weight:700;color:#101728;line-height:1.25;'
        f'margin-top:3px">{_e(f["nom"])}</div></div>')

    # -------------------------------------------------------- 2. où elle est
    localisation = _colonnes("".join([
        _ligne(T("o_f_localite"), f.get("localite")),
        _ligne(T("section_communale"), f.get("section")),
    ]))
    bloc_lieu = _titre_partie(T("o_f_p2")) + localisation if localisation else ""

    # ------------------------------------------- 3. comment elle est organisée
    structure = _colonnes(
        "".join([_ligne(femmes_lib, femmes_txt),
                 _ligne(T("o_f_femme_dir"),
                        f.get("femme_detail") or trois(f.get("femme_direction")))]),
        "".join([_ligne(T("o_f_jeune_dir"),
                        f.get("jeune_detail") or trois(f.get("jeune_direction"))),
                 _ligne(T("o_f_cartographie"), trois(f.get("cartographie")))]),
        "".join([_ligne(T("o_f_recoit"), f.get("recoit_qui")
                        or trois(f.get("recoit_rapports"))),
                 _ligne(T("o_f_soumet"), f.get("soumet_qui")
                        or trois(f.get("soumet_rapports")))]))
    bloc_structure = _titre_partie(T("o_f_p3")) + structure if structure else ""

    # ------------------------------------------------ 4. avec qui elle travaille
    partenariats = _colonnes(
        "".join([_ligne(T("o_f_partenariat"), trois(f.get("partenariat"))),
                 _ligne(T("o_f_type_partenariat"), _puces(f.get("prive_type")))]),
        "".join([_ligne(T("o_f_duree"), f.get("duree")),
                 _ligne(T("o_f_note"), note_txt)]),
        "".join([_ligne(T("o_f_soutien"), _puces(f.get("soutien_detail"))),
                 _ligne(T("o_f_facteurs"), f.get("facteurs"))]),
        "".join([_ligne(T("o_f_projets"), f.get("projets")),
                 _ligne(T("o_f_projets_autre"), f.get("projets_autre")),
                 _ligne(T("o_f_prive"), f.get("prive_detail"))]))

    ACTEURS = ["Autorités communales", "Autorités départementales", "Délégation",
               "Institutions techniques", "Sénateurs/députés", "ONG locales",
               "ONG internationales"]
    presents = set(f.get("plateforme_acteurs") or [])
    plateforme = "".join(_pastille(a, a in presents) for a in ACTEURS)
    consulte = f.get("consulte_par") or []

    bloc_reseau = (
        _titre_partie(T("o_f_p4")) + partenariats
        + f'<div style="margin-top:6px"><div style="font-size:11.5px;'
          f'letter-spacing:.06em;text-transform:uppercase;color:#6b7590;'
          f'font-weight:700;margin-bottom:7px">{_e(T("o_f_plateforme"))}</div>'
          f'{plateforme}</div>'
        + (f'<div style="margin-top:12px">'
           f'{_ligne(T("o_f_consulte"), consulte, pleine=True)}'
           f'<p style="font-size:11.5px;color:#8b93a3;margin:-6px 0 0">'
           f'{_e(T("o_f_consulte_note"))}</p></div>' if consulte else ''))

    return ('<div style="background:#fff;border:1px solid #e6ecf4;'
            'border-radius:16px;padding:20px 24px 22px;'
            'box-shadow:0 1px 2px rgba(16,23,40,.05),'
            '0 8px 22px rgba(16,23,40,.06)">'
            + entete + bloc_lieu + bloc_structure + bloc_reseau
            + '</div>')
