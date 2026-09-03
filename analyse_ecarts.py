"""Trois lectures des écarts : par indicateur, par paysage, par groupe social.

CE QUE CES TROIS ÉCRANS CHERCHENT, ET QUE LES AUTRES NE DONNENT PAS.
Les résultats bruts disent ce que les gens répondent ; les scores disent où en
est chaque dimension. Ni l'un ni l'autre ne répond à la question qu'on se pose
en refermant un rapport : OÙ sont les écarts, et QUELS indicateurs les font.

C'est ce que font ces trois pages, avec le même calcul vu sous trois angles :

  · par indicateur — un indicateur, sa valeur et son score dans chaque
    section, chaque paysage, chaque groupe ;
  · par paysage    — un paysage contre l'autre, dimension par dimension, puis
    les indicateurs qui creusent le plus l'écart ;
  · par groupe     — un groupe contre le reste de l'échantillon, de même.

L'ÉCART EST CALCULÉ CONTRE LE COMPLÉMENT, PAS CONTRE L'ENSEMBLE. Comparer les
femmes à « tout le monde » compare un groupe à un ensemble qui le contient :
l'écart est mécaniquement réduit de moitié. Le complément — tous ceux qui ne
sont pas dans le groupe — est le seul terme de comparaison qui ne se dilue
pas.

UN INDICATEUR SANS BASE DANS UN GROUPE SORT DU CLASSEMENT, il n'est pas compté
zéro. Un indicateur que personne du groupe n'a pu renseigner ne dit rien sur
le groupe ; le traiter comme un score nul en ferait la première vulnérabilité
du classement, qui serait un artefact.
"""

import numpy as np
import streamlit as st

import croisement_moteur as M
import i18n
import radar
from i18n import T

ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"
VERT_APRI, VERT, ROUGE, GRIS = "#2a6b3f", "#1a8a4f", "#c33a24", "#8a93a5"

# LE SEUIL D'EFFECTIF EST CELUI DE L'EXPLORATEUR. Deux seuils différents dans
# deux écrans du même site donneraient deux verdicts sur le même effectif.
N_MIN = 20
# Un écart de moins d'un dixième de point sur dix n'est pas un écart : c'est
# le bruit d'un arrondi. Il ne mérite pas une ligne de classement.
ECART_MIN = 0.10
# Cinq points de pourcentage sur la valeur brute : en dessous, l'écart tient
# dans l'intervalle de confiance d'un sous-groupe de deux cents ménages.
VALEUR_MIN = 5.0

_VALEURS = dict(M.REGISTRES)
_DIMS = [c for c, _l in M.DIMENSIONS]

# Les axes de ventilation, dans l'ordre où ils éclairent une différence.
AXES = [("section", "ec_ax_section"), ("paysage", "ec_ax_paysage"),
        ("sexe", "ec_ax_sexe"), ("age", "ec_ax_age"),
        ("richesse", "ec_ax_richesse")]
# Les groupes sociaux : tout sauf la localité et le paysage, qui sont des
# lieux et ont leurs propres pages.
GROUPES_SOCIAUX = ["sexe", "age", "richesse"]

TEXTES = {
    "ec_ax_section": {"en": "Communal section", "fr": "Section communale"},
    "ec_ax_paysage": {"en": "Landscape", "fr": "Paysage"},
    "ec_ax_sexe": {"en": "Sex", "fr": "Sexe"},
    "ec_ax_age": {"en": "Age group", "fr": "Tranche d'âge"},
    "ec_ax_richesse": {"en": "Economic category",
                       "fr": "Catégorie économique"},

    "ec_i_titre": {"en": "One indicator, across the territory",
                   "fr": "Un indicateur, à travers le territoire"},
    "ec_i_intro": {
        "en": "Pick an indicator: its value and its 0–10 score are computed "
              "for every communal section, landscape and social group. The "
              "gap between the highest and the lowest is what an intervention "
              "would have to close.",
        "fr": "Choisissez un indicateur : sa valeur et son score sur 10 sont "
              "calculés pour chaque section communale, chaque paysage et "
              "chaque groupe social. L'écart entre le plus haut et le plus "
              "bas est ce qu'une intervention aurait à combler."},
    "ec_i_choix": {"en": "Indicator", "fr": "Indicateur"},
    "ec_i_axes": {"en": "Compare across", "fr": "Comparer sur"},
    "ec_i_sens_haut": {"en": "Higher is better", "fr": "Plus, c'est mieux"},
    "ec_i_sens_bas": {"en": "Lower is better", "fr": "Moins, c'est mieux"},
    "ec_i_ecart": {"en": "Spread between the highest and the lowest: {v} "
                         "points out of 10.",
                   "fr": "Écart entre le plus haut et le plus bas : {v} "
                         "points sur 10."},

    "ec_p_titre": {"en": "One landscape, and what sets it apart",
                   "fr": "Un paysage, et ce qui le distingue"},
    "ec_g_titre": {"en": "One social group, and what sets it apart",
                   "fr": "Un groupe social, et ce qui le distingue"},
    "ec_p_choix": {"en": "Landscape", "fr": "Paysage"},
    "ec_g_choix": {"en": "Social group", "fr": "Groupe social"},
    "ec_vs": {"en": "compared with everyone else",
              "fr": "comparé à tous les autres"},
    "ec_profil": {"en": "Profile by dimension", "fr": "Profil par dimension"},
    "ec_ecarts": {"en": "The indicators that make the difference",
                  "fr": "Les indicateurs qui font la différence"},
    "ec_ecarts_x": {
        "en": "Ranked by the size of the gap with everyone else, strongest "
              "first. A green gap is an advantage of the selected group, a "
              "red one a disadvantage.",
        "fr": "Classés par la taille de l'écart avec tous les autres, du plus "
              "grand au plus petit. Un écart vert est un avantage du groupe "
              "choisi, un écart rouge un désavantage."},
    "ec_col_ind": {"en": "Indicator", "fr": "Indicateur"},
    "ec_col_grp": {"en": "Group", "fr": "Groupe"},
    "ec_col_reste": {"en": "Everyone else", "fr": "Tous les autres"},
    "ec_col_ecart": {"en": "Gap", "fr": "Écart"},
    "ec_col_score": {"en": "Score / 10", "fr": "Score / 10"},
    "ec_col_val": {"en": "Value", "fr": "Valeur"},
    "ec_col_n": {"en": "n", "fr": "n"},
    "ec_indice": {"en": "Overall index", "fr": "Indice global"},
    "ec_effectif": {"en": "{n} households", "fr": "{n} ménages"},
    "ec_rien": {"en": "No indicator can be computed on this group.",
                "fr": "Aucun indicateur ne peut être calculé sur ce groupe."},
    "ec_combien": {"en": "Indicators shown", "fr": "Indicateurs affichés"},
    "ec_fragile": {
        "en": "Rows resting on fewer than {n} households are shown in pale "
              "type: a single answer moves them.",
        "fr": "Les lignes reposant sur moins de {n} ménages sont en pâle : "
              "une seule réponse les fait bouger."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)

STYLE = """
<style>
  .ec-tab { width:100%; border-collapse:collapse; margin-top:12px; }
  .ec-tab th { font-size:10.5px; font-weight:700; letter-spacing:.09em;
       text-transform:uppercase; color:#8a93a5; text-align:left;
       padding:0 10px 7px 0; border-bottom:1px solid #e9eef4; }
  .ec-tab th.n, .ec-tab td.n { text-align:right;
       font-variant-numeric:tabular-nums; }
  .ec-tab td { font-size:12.5px; color:#3c4761; padding:7px 10px 7px 0;
       border-bottom:1px solid #f2f5f9; vertical-align:top; }
  .ec-tab td.v { font-weight:700; color:#101728; }
  .ec-tab tr.pale td { opacity:.55; }
  .ec-note { font-size:11.5px; color:#8a93a5; line-height:1.5;
       margin:8px 0 0; text-align:left !important; max-width:96ch; }
  .ec-kpi { display:flex; gap:14px; flex-wrap:wrap; margin:2px 0 14px; }
  .ec-k { flex:1 1 170px; background:#fff; border:1px solid #e3eaf3;
       border-radius:12px; padding:12px 15px; }
  .ec-k-l { font-size:10.5px; font-weight:700; letter-spacing:.08em;
       text-transform:uppercase; color:#8a93a5; }
  .ec-k-v { font-size:22px; font-weight:700; color:#101728; line-height:1.1;
       margin-top:4px; font-variant-numeric:tabular-nums; }
  .ec-k-s { font-size:11px; color:#8a93a5; margin-top:2px; }
</style>
"""


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _f(v, dec=2, signe=False):
    if v is None:
        return "—"
    s = f"{v:+.{dec}f}" if signe else f"{v:.{dec}f}"
    return s.replace(".", ",") if i18n.get_lang() == "fr" else s


def _lib(v):
    cles = {"Homme": "hommes", "Femme": "femmes", "Cat A": "cat_a",
            "Cat B": "cat_b", "Cat C": "cat_c", "<25": "age_25",
            "25-39": "age_25_39", "40-59": "age_40_59", "60+": "age_60",
            "Littoral": "pay_Littoral", "Montagne": "pay_Montagne"}
    return T(cles[v]) if v in cles else v


def _nom(ind):
    return ((ind.get("nom_fr") or ind.get("nom")) if i18n.get_lang() == "fr"
            else (ind.get("nom") or ind.get("nom_fr")))


def _mesure(ind, masque):
    """Valeur et score d'UN indicateur sur UN masque.

    On ne passe pas par `profil`, qui calcule les soixante-six : pour une
    ventilation en dix sections, cela ferait six cent soixante calculs pour
    n'en afficher que dix.
    """
    base = ind["base"] & masque
    nb = int(base.sum())
    if nb == 0:
        return {"n": 0, "valeur": None, "score": None}
    val = 100.0 * float((ind["cible"] & masque).sum()) / nb
    return {"n": nb, "valeur": val,
            "score": M._score_de(val, ind["bornes"], ind["decroissant"])}


def _cases(cat, axe):
    return [(v, _lib(v)) for v in _VALEURS.get(axe, [])
            if cat["groupes"].get(v) is not None]


# =========================================================== par indicateur
def render_indicateur(cat):
    """Un indicateur, lu sur les sections, les paysages et les groupes."""
    if not cat or not cat.get("indicateurs"):
        return
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown(f'<div class="titre-bloc">{_e(T("ec_i_titre"))}</div>'
                f'<p class="ec-note" style="margin:0 0 12px">'
                f'{_e(T("ec_i_intro"))}</p>', unsafe_allow_html=True)

    inds = sorted(cat["indicateurs"], key=lambda x: (x["dim"], _nom(x)))
    g, d = st.columns([1.7, 1])
    with g:
        pos = st.selectbox(T("ec_i_choix"), list(range(len(inds))),
                           key="ec_i_sel",
                           format_func=lambda k: f'{T(inds[k]["dim"])} · '
                                                 f'{_nom(inds[k])}')
    ind = inds[pos]
    with d:
        axes = st.multiselect(T("ec_i_axes"), [a for a, _ in AXES],
                              default=["section"], key="ec_i_axes",
                              format_func=lambda a: T(dict(AXES)[a]))

    sens = T("ec_i_sens_bas") if ind.get("decroissant") else T("ec_i_sens_haut")
    st.markdown(f'<p class="ec-note" style="margin:0 0 6px">'
                f'{_e(T(ind["dim"]))} · {_e(sens)}</p>',
                unsafe_allow_html=True)

    lignes = []
    for axe in axes:
        for v, lib in _cases(cat, axe):
            m = _mesure(ind, cat["groupes"][v])
            if m["n"]:
                lignes.append({"axe": T(dict(AXES)[axe]), "nom": lib, **m})
    if not lignes:
        st.info(T("ec_rien"))
        return

    tout = _mesure(ind, np.ones(cat["n"], dtype=bool))
    scores = [l["score"] for l in lignes if l["score"] is not None]
    if len(scores) > 1:
        st.markdown(f'<p class="ec-note" style="margin:0 0 8px">'
                    f'{_e(T("ec_i_ecart", v=_f(max(scores) - min(scores), 1)))}'
                    f'</p>', unsafe_allow_html=True)
    st.markdown(_barres(lignes, tout), unsafe_allow_html=True)
    st.markdown(_table_cases(lignes, tout), unsafe_allow_html=True)


def _barres(lignes, ref):
    """Le score de chaque case, de 0 à 10, avec l'ensemble en repère."""
    LARG, H_L, GAP, H_AXE = 1000, 28, 8, 26
    MG_G, MG_H, MG_B = 230, 26, 26
    n_axes = len({l["axe"] for l in lignes})
    H = MG_H + len(lignes) * (H_L + GAP) + max(n_axes - 1, 0) * H_AXE + MG_B
    utile = LARG - MG_G - 96
    parts, axe_vu, y = [], None, MG_H

    if ref["score"] is not None:
        x = MG_G + utile * ref["score"] / 10
        parts.append(
            f'<line x1="{x:.1f}" y1="{MG_H - 12}" x2="{x:.1f}" '
            f'y2="{H - MG_B + 4}" stroke="{ENCRE3}" stroke-width="1" '
            f'stroke-dasharray="3 4"/>'
            f'<text x="{x:.1f}" y="{MG_H - 17}" text-anchor="middle" '
            f'font-size="11" fill="{ENCRE3}">{_e(T("ec_indice"))} '
            f'{_f(ref["score"], 1)}</text>')

    for l in lignes:
        if l["axe"] != axe_vu:
            if axe_vu is not None:
                y += H_AXE
            axe_vu = l["axe"]
            parts.append(
                f'<text x="0" y="{y - 8}" font-size="9.5" font-weight="700" '
                f'letter-spacing="1.2" fill="{GRIS}">'
                f'{_e(l["axe"].upper())}</text>')
        pale = l["n"] < N_MIN
        coul = "#a8cbb6" if pale else VERT_APRI
        parts.append(
            f'<text x="{MG_G - 12}" y="{y + 14}" text-anchor="end" '
            f'font-size="12.5" fill="{ENCRE}">{_e(l["nom"])}</text>'
            f'<rect x="{MG_G}" y="{y + 2}" width="{utile}" height="15" rx="7" '
            f'fill="#eef3f0"/>')
        if l["score"] is not None:
            w = max(utile * min(l["score"], 10) / 10, 2)
            parts.append(
                f'<rect x="{MG_G}" y="{y + 2}" width="{w:.1f}" height="15" '
                f'rx="7" fill="{coul}"/>'
                f'<text x="{MG_G + utile + 12}" y="{y + 14}" font-size="12.5" '
                f'font-weight="700" fill="{ENCRE}">{_f(l["score"], 1)}</text>')
        parts.append(f'<text x="{LARG - 4}" y="{y + 14}" font-size="11" '
                     f'fill="{GRIS}" text-anchor="end">n={l["n"]}</text>')
        y += H_L + GAP

    return (f'<svg viewBox="0 0 {LARG} {H}" width="100%" '
            f'style="max-width:{LARG}px;display:block" role="img" '
            f'font-family="Inter,system-ui,sans-serif">'
            + "".join(parts) + '</svg>')


def _table_cases(lignes, ref):
    r = ['<table class="ec-tab"><thead><tr>'
         f'<th>{_e(T("ec_col_grp"))}</th>'
         f'<th class="n">{_e(T("ec_col_score"))}</th>'
         f'<th class="n">{_e(T("ec_col_val"))}</th>'
         f'<th class="n">{_e(T("ec_col_n"))}</th></tr></thead><tbody>']
    for l in lignes:
        cl = ' class="pale"' if l["n"] < N_MIN else ""
        r.append(f'<tr{cl}><td>{_e(l["nom"])}</td>'
                 f'<td class="n v">{_f(l["score"], 1)}</td>'
                 f'<td class="n">{_f(l["valeur"], 1)}&#8201;%</td>'
                 f'<td class="n">{l["n"]}</td></tr>')
    r.append(f'<tr><td>{_e(T("ec_indice"))}</td>'
             f'<td class="n v">{_f(ref["score"], 1)}</td>'
             f'<td class="n">{_f(ref["valeur"], 1)}&#8201;%</td>'
             f'<td class="n">{ref["n"]}</td></tr></tbody></table>')
    return "".join(r)


# ================================================ par paysage / par groupe
def _profil_compare(cat, masque):
    """Le groupe et son complément, dimension par dimension et indicateur par
    indicateur.

    LE COMPLÉMENT, PAS L'ENSEMBLE. Comparer un groupe à un tout qui le
    contient dilue l'écart de moitié ; le complément ne se dilue pas.
    """
    autre = ~masque
    ag_g = M.agreger(M.profil(cat, masque))
    ag_a = M.agreger(M.profil(cat, autre))
    # LE SCORE EST UNE CLASSE ENTIÈRE, PAS UNE MESURE CONTINUE. Les barèmes
    # découpent chaque métrique en onze paliers : deux groupes peuvent
    # différer de dix points de pourcentage sur la valeur brute et tomber
    # dans le même palier, donc afficher le même score. Classer sur le seul
    # écart de score laisserait dehors des différences réelles. On garde donc
    # les deux — l'écart de score d'abord, l'écart de valeur ensuite — et on
    # retient une ligne dès que l'un des deux dit quelque chose.
    ecarts = []
    for ind in cat["indicateurs"]:
        a, b = _mesure(ind, masque), _mesure(ind, autre)
        if a["score"] is None or b["score"] is None:
            continue
        d = a["score"] - b["score"]
        dv = a["valeur"] - b["valeur"]
        if abs(d) < ECART_MIN and abs(dv) < VALEUR_MIN:
            continue
        ecarts.append({"nom": _nom(ind), "dim": T(ind["dim"]),
                       "g": a["score"], "a": b["score"], "d": d,
                       "gv": a["valeur"], "av": b["valeur"], "dv": dv,
                       "n": a["n"]})
    ecarts.sort(key=lambda x: (-abs(x["d"]), -abs(x["dv"])))
    return ag_g, ag_a, ecarts


def _table_ecarts(ecarts, lib_g):
    r = ['<table class="ec-tab"><thead><tr>'
         f'<th>{_e(T("ec_col_ind"))}</th>'
         f'<th class="n">{_e(lib_g)}</th>'
         f'<th class="n">{_e(T("ec_col_reste"))}</th>'
         f'<th class="n">{_e(T("ec_col_ecart"))}</th>'
         f'<th class="n">{_e(T("ec_col_val"))}</th>'
         f'<th class="n">{_e(T("ec_col_n"))}</th></tr></thead><tbody>']
    for x in ecarts:
        cl = ' class="pale"' if x["n"] < N_MIN else ""
        coul = VERT if x["d"] > 0 else ROUGE
        r.append(
            f'<tr{cl}><td>{_e(x["nom"])}<br>'
            f'<span style="font-size:11px;color:#8a93a5">{_e(x["dim"])}</span>'
            f'</td>'
            f'<td class="n v">{_f(x["g"], 1)}</td>'
            f'<td class="n">{_f(x["a"], 1)}</td>'
            f'<td class="n v" style="color:{coul}">{_f(x["d"], 1, True)}</td>'
            f'<td class="n">{_f(x["gv"], 0)}&#8201;% <span style="color:#a7b0be">'
            f'/ {_f(x["av"], 0)}&#8201;%</span></td>'
            f'<td class="n">{x["n"]}</td></tr>')
    r.append('</tbody></table>')
    return "".join(r)


def _kpi(lib, n, sc_g, sc_a):
    ecart = (sc_g - sc_a) if (sc_g is not None and sc_a is not None) else None
    coul = VERT if (ecart or 0) > 0 else ROUGE if (ecart or 0) < 0 else ENCRE3
    return (
        '<div class="ec-kpi">'
        f'<div class="ec-k"><div class="ec-k-l">{_e(lib)}</div>'
        f'<div class="ec-k-v">{_f(sc_g)}<span style="font-size:13px;'
        f'color:#8a93a5"> / 10</span></div>'
        f'<div class="ec-k-s">{_e(T("ec_effectif", n=n))}</div></div>'
        f'<div class="ec-k"><div class="ec-k-l">{_e(T("ec_col_reste"))}</div>'
        f'<div class="ec-k-v">{_f(sc_a)}<span style="font-size:13px;'
        f'color:#8a93a5"> / 10</span></div>'
        f'<div class="ec-k-s">{_e(T("ec_vs"))}</div></div>'
        f'<div class="ec-k"><div class="ec-k-l">{_e(T("ec_col_ecart"))}</div>'
        f'<div class="ec-k-v" style="color:{coul}">{_f(ecart, 2, True)}</div>'
        f'<div class="ec-k-s">{_e(T("ec_indice"))}</div></div></div>')


def _rendre_profil(cat, valeur, lib, titre):
    masque = cat["groupes"].get(valeur)
    if masque is None:
        st.info(T("ec_rien"))
        return
    ag_g, ag_a, ecarts = _profil_compare(cat, masque)
    st.markdown(_kpi(lib, int(masque.sum()), ag_g["global"], ag_a["global"]),
                unsafe_allow_html=True)

    # LE RADAR PORTE LES DEUX SÉRIES, jamais le groupe seul : un profil sans
    # terme de comparaison se lit comme une forme, pas comme un écart.
    axes = [T(c) for c in _DIMS]
    s_g = [ag_g["dimensions"].get(c) for c in _DIMS]
    s_a = [ag_a["dimensions"].get(c) for c in _DIMS]
    if sum(1 for v in s_g if v is not None) >= 3:
        st.markdown(f'<div class="titre-bloc">{_e(T("ec_profil"))}</div>',
                    unsafe_allow_html=True)
        svg = radar.render_radar_svg(
            axes, [(lib, s_g, VERT_APRI), (T("ec_col_reste"), s_a, "#8a93a5")],
            taille=430)
        st.markdown(f'<div style="max-width:820px;margin:4px auto 0">{svg}'
                    f'</div>'
                    f'<div style="text-align:center;margin-top:6px">'
                    f'{radar.legende_html([(lib, s_g, VERT_APRI), (T("ec_col_reste"), s_a, "#8a93a5")])}'
                    f'</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="titre-bloc" style="margin-top:22px">'
                f'{_e(T("ec_ecarts"))}</div>'
                f'<p class="ec-note" style="margin:0">{_e(T("ec_ecarts_x"))}'
                f'</p>', unsafe_allow_html=True)
    if not ecarts:
        st.info(T("ec_rien"))
        return
    combien = st.slider(T("ec_combien"), 5, min(40, len(ecarts)),
                        min(12, len(ecarts)), key=f"ec_n_{titre}")
    st.markdown(_table_ecarts(ecarts[:combien], lib), unsafe_allow_html=True)
    if any(x["n"] < N_MIN for x in ecarts[:combien]):
        st.markdown(f'<p class="ec-note">{_e(T("ec_fragile", n=N_MIN))}</p>',
                    unsafe_allow_html=True)


def render_paysage(cat):
    if not cat:
        return
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown(f'<div class="titre-bloc">{_e(T("ec_p_titre"))}</div>',
                unsafe_allow_html=True)
    vals = [v for v in _VALEURS["paysage"] if cat["groupes"].get(v) is not None]
    if not vals:
        st.info(T("ec_rien"))
        return
    v = st.selectbox(T("ec_p_choix"), vals, key="ec_p_sel",
                     format_func=_lib)
    _rendre_profil(cat, v, _lib(v), "pay")


def render_groupe(cat):
    if not cat:
        return
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown(f'<div class="titre-bloc">{_e(T("ec_g_titre"))}</div>',
                unsafe_allow_html=True)
    # LES TROIS REGISTRES SOCIAUX SONT APLATIS EN UNE SEULE LISTE, préfixée du
    # registre : « Sexe · Femmes » se choisit d'un geste, là où deux menus
    # emboîtés en demandent deux pour la même chose.
    opts = []
    for axe in GROUPES_SOCIAUX:
        for val, lib in _cases(cat, axe):
            opts.append((val, f'{T(dict(AXES)[axe])} · {lib}', lib))
    if not opts:
        st.info(T("ec_rien"))
        return
    k = st.selectbox(T("ec_g_choix"), list(range(len(opts))), key="ec_g_sel",
                     format_func=lambda i: opts[i][1])
    _rendre_profil(cat, opts[k][0], opts[k][2], "grp")
