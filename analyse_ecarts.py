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
import map_render
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
    "ec_format": {"en": "Chart", "fr": "Graphique"},
    "ec_barres": {"en": "Bar chart", "fr": "Histogramme"},
    "ec_radar": {"en": "Radar chart", "fr": "Diagramme radar"},
    "ec_tableau": {"en": "Table", "fr": "Tableau"},
    "ec_carte": {"en": "Map", "fr": "Carte"},
    "ec_carte_sec": {
        "en": "The map is drawn by communal section: it is available when "
              "the comparison includes the communal sections.",
        "fr": "La carte se dessine par section communale : elle est "
              "disponible quand la comparaison contient les sections "
              "communales."},
    "ec_radar_court": {
        "en": "A radar needs at least three points; this comparison has "
              "fewer. Showing the bar chart.",
        "fr": "Un radar demande au moins trois sommets ; cette comparaison en "
              "compte moins. L'histogramme est affiché."},
    "ec_extremes": {"en": "Show", "fr": "Afficher"},
    "ec_tous": {"en": "All", "fr": "Tout"},
    "ec_top": {"en": "Best three", "fr": "Les trois meilleurs"},
    "ec_flop": {"en": "Worst three", "fr": "Les trois plus faibles"},
    "ec_topflop": {"en": "Best and worst three",
                   "fr": "Les trois meilleurs et les trois plus faibles"},
    "ec_i_pourcent": {
        "en": "Each bar carries its 0–10 score and, in grey, the raw value it "
              "comes from — the share of households concerned.",
        "fr": "Chaque barre porte son score sur 10 et, en gris, la valeur "
              "brute dont il vient — la part des ménages concernés."},

    "ec_combiner": {"en": "Combine with", "fr": "Combiner avec"},
    "ec_c_groupe": {"en": "Social group", "fr": "Groupe social"},
    "ec_c_section": {"en": "Communal section", "fr": "Section communale"},
    "ec_c_paysage": {"en": "Landscape", "fr": "Paysage"},
    "ec_c_tous": {"en": "All", "fr": "Tout"},
    "ec_c_vide": {"en": "No household matches this combination.",
                  "fr": "Aucun ménage ne réunit cette combinaison."},
    "ec_contre": {"en": "Compared with", "fr": "Comparé à"},
    "ec_c_note2": {
        "en": "Everything below compares these {n} households with {q} — "
              "{m} households.",
        "fr": "Tout ce qui suit compare ces {n} ménages à {q} — {m} ménages."},
    "ec_col_dim": {"en": "Dimension", "fr": "Dimension"},
    "ec_carte_grp": {
        "en": "The group's overall index, communal section by communal "
              "section. Sections where the group has no household are left "
              "blank.",
        "fr": "L'indice global du groupe, section communale par section "
              "communale. Les sections où le groupe n'a aucun ménage restent "
              "vides."},
    "ec_carte_vide": {
        "en": "This group is present in fewer than two communal sections: "
              "there is nothing to map.",
        "fr": "Ce groupe est présent dans moins de deux sections communales : "
              "il n'y a rien à cartographier."},
    "ec_tri": {"en": "Rank indicators by", "fr": "Classer les indicateurs par"},
    "ec_tri_ecart": {"en": "Biggest gap with everyone else",
                     "fr": "Plus grand écart avec les autres"},
    "ec_tri_haut": {"en": "Best scores in the group",
                    "fr": "Meilleurs scores du groupe"},
    "ec_tri_bas": {"en": "Weakest scores in the group",
                   "fr": "Scores les plus faibles du groupe"},
    "ec_tri_haut_x": {
        "en": "What this group does best, in its own right: the indicators on "
              "which it scores highest. The column beside shows everyone "
              "else, so a strength shared by the whole territory is not read "
              "as a specificity.",
        "fr": "Ce que ce groupe réussit le mieux, en valeur absolue : les "
              "indicateurs où son score est le plus haut. La colonne d'à côté "
              "donne tous les autres, pour qu'une force partagée par tout le "
              "territoire ne se lise pas comme une spécificité."},
    "ec_tri_bas_x": {
        "en": "Where this group stands lowest, in its own right: the "
              "indicators on which it scores worst, whatever the rest of the "
              "sample does.",
        "fr": "Là où ce groupe est le plus bas, en valeur absolue : les "
              "indicateurs où son score est le plus faible, quoi que fasse le "
              "reste de l'échantillon."},

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
    "al_titre": {"en": "Identifying the most alarming variables",
                 "fr": "Identification des variables les plus alarmantes"},
    "al_intro": {
        "en": "The five screens before this one answer questions that were "
              "put to them. This one asks nothing: it sweeps the whole "
              "framework and returns the indicators that score lowest — "
              "across the territory first, then group by group. These are "
              "the variables a causal loop diagram should be drawn around, "
              "and the levers come after the loops, not before them.",
        "fr": "Les cinq écrans précédents répondent aux questions qu'on leur "
              "pose. Celui-ci n'en pose aucune : il balaye le cadre entier et "
              "renvoie les indicateurs dont le score est le plus bas — sur le "
              "territoire d'abord, puis groupe par groupe. Ce sont les "
              "variables autour desquelles tracer un schéma de boucle "
              "causale, et les leviers viennent après les boucles, pas "
              "avant."},
    "al_t1": {"en": "The lowest indicators across the territory",
              "fr": "Les indicateurs les plus bas sur le territoire"},
    "al_x1": {
        "en": "Ranked by score, lowest first, on all {n} households. A low "
              "score here is a weakness of the whole landscape, not of one "
              "group in it.",
        "fr": "Classés par score, du plus bas au plus haut, sur les {n} "
              "ménages. Un score bas ici est une faiblesse du paysage "
              "entier, pas d'un groupe en particulier."},
    "al_t2": {"en": "The lowest indicator of each group, relative to the others",
              "fr": "L'indicateur le plus bas de chaque groupe, par rapport "
                    "aux autres"},
    "al_x2": {
        "en": "For every group, the indicator on which it falls furthest "
              "below everyone else. The gap is what makes it the group's own "
              "weakness rather than the territory's: an indicator that is low "
              "everywhere shows up in the table above, not in this one.",
        "fr": "Pour chaque groupe, l'indicateur sur lequel il décroche le "
              "plus par rapport à tous les autres. C'est l'écart qui en fait "
              "une faiblesse propre au groupe et non du territoire : un "
              "indicateur bas partout figure dans le tableau du dessus, pas "
              "dans celui-ci."},
    "al_combien": {"en": "Variables listed", "fr": "Variables listées"},
    "al_par_groupe": {"en": "Variables per group", "fr": "Variables par groupe"},
    "al_registres": {"en": "Groups swept", "fr": "Registres balayés"},
    "al_col_groupe": {"en": "Group", "fr": "Groupe"},
    "al_col_var": {"en": "Variable", "fr": "Variable"},
    "al_col_sien": {"en": "Its score", "fr": "Son score"},
    "al_col_autres": {"en": "The others", "fr": "Les autres"},
    "al_vide": {"en": "No group falls clearly below the others on any "
                      "indicator.",
                "fr": "Aucun groupe ne décroche nettement des autres sur un "
                      "indicateur."},
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
  .ec-lab { font-size:10.5px; font-weight:700; letter-spacing:.09em;
       text-transform:uppercase; color:#8a93a5; margin:10px 0 2px; }
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

    # LE DESSIN ET LES EXTRÊMES SE CHOISISSENT ICI, comme sur les deux
    # premiers onglets : un même geste doit donner un même résultat d'un écran
    # à l'autre, sinon le lecteur réapprend l'outil à chaque page.
    c1, c2 = st.columns(2)
    with c1:
        forme = st.selectbox(
            T("ec_format"), ["barres", "radar", "tableau", "carte"],
            key="ec_i_forme", format_func=lambda f: T("ec_" + f))
    with c2:
        extremes = st.selectbox(
            T("ec_extremes"), ["tous", "top", "flop", "topflop"],
            key="ec_i_ext",
            format_func=lambda c: T({"tous": "ec_tous", "top": "ec_top",
                                     "flop": "ec_flop",
                                     "topflop": "ec_topflop"}[c]))

    sens = T("ec_i_sens_bas") if ind.get("decroissant") else T("ec_i_sens_haut")
    st.markdown(f'<p class="ec-note" style="margin:0 0 6px">'
                f'{_e(T(ind["dim"]))} · {_e(sens)}</p>',
                unsafe_allow_html=True)

    lignes = []
    for axe in axes:
        for v, lib in _cases(cat, axe):
            m = _mesure(ind, cat["groupes"][v])
            if m["n"]:
                lignes.append({"axe": T(dict(AXES)[axe]), "nom": lib,
                               "cle": v, "axe_code": axe, **m})
    if not lignes:
        st.info(T("ec_rien"))
        return

    tout = _mesure(ind, np.ones(cat["n"], dtype=bool))
    scores = [l["score"] for l in lignes if l["score"] is not None]
    if len(scores) > 1:
        st.markdown(f'<p class="ec-note" style="margin:0 0 8px">'
                    f'{_e(T("ec_i_ecart", v=_f(max(scores) - min(scores), 1)))}'
                    f'</p>', unsafe_allow_html=True)

    montrees = _extremes(lignes, extremes)
    if forme == "radar" and len(montrees) < 3:
        st.info(T("ec_radar_court"))
        forme = "barres"
    if forme == "carte":
        svg = _carte(montrees)
        if svg is None:
            st.info(T("ec_carte_sec"))
            forme = "barres"
        else:
            st.markdown(f'<div style="font-family:Inter,system-ui,sans-serif">'
                        f'{svg}</div>', unsafe_allow_html=True)

    if forme == "radar":
        svg = radar.render_radar_svg(
            [l["nom"] for l in montrees],
            [(_nom(ind), [l["score"] for l in montrees], VERT_APRI)],
            taille=430)
        st.markdown(f'<div style="max-width:760px;margin:6px auto 0">{svg}'
                    f'</div>', unsafe_allow_html=True)
    elif forme == "barres":
        st.markdown(_barres(montrees, tout), unsafe_allow_html=True)
        st.markdown(f'<p class="ec-note">{_e(T("ec_i_pourcent"))}</p>',
                    unsafe_allow_html=True)

    st.markdown(_table_cases(montrees, tout), unsafe_allow_html=True)


def _extremes(lignes, choix):
    """Ne garder que les meilleurs et les plus faibles, si on l'a demandé.

    L'ORDRE D'ORIGINE EST CONSERVÉ : les sections ont un ordre géographique et
    les tranches d'âge un ordre naturel, qu'un tri par score détruirait. On
    retire des lignes, on ne les reclasse pas.
    """
    mesurees = [x for x in lignes if x["score"] is not None]
    if choix == "tous" or len(mesurees) <= 3:
        return lignes
    tri = sorted(mesurees, key=lambda x: x["score"])
    garder = set()
    if choix in ("top", "topflop"):
        garder |= {id(x) for x in tri[-3:]}
    if choix in ("flop", "topflop"):
        garder |= {id(x) for x in tri[:3]}
    return [x for x in lignes if id(x) in garder]


def _carte(lignes):
    """Le score par section communale, porté sur la carte du territoire.

    LA CARTE NE MONTRE QUE LES SECTIONS. Le sexe, l'âge et la catégorie
    économique n'ont pas de géographie : les colorier sur un territoire
    inventerait un lieu qu'ils n'ont pas.
    """
    vals = {l["cle"]: l["score"] for l in lignes
            if l.get("axe_code") == "section" and l["score"] is not None}
    if len(vals) < 2:
        return None
    seuils = map_render.nice_thresholds(list(vals.values()))
    svg, seuils_ret, _m = map_render.render_map_svg(
        vals, {s: 1 for s in vals}, seuils, height=560,
        polarity="eleve_bon", unite="/10")
    legende = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:7px;'
        f'margin-right:16px"><span style="width:20px;height:11px;'
        f'border-radius:3px;background:{c}"></span>'
        f'<span style="font-size:11.5px;color:#52514e">{lab}</span></span>'
        for c, lab in map_render.legend_items(seuils_ret, "eleve_bon", "/10"))
    return f'<div style="margin:6px 0 8px">{legende}</div>{svg}'


def _barres(lignes, ref):
    """Le score de chaque case, de 0 à 10, avec l'ensemble en repère."""
    LARG, H_L, GAP, H_AXE = 1000, 28, 8, 26
    MG_G, MG_H, MG_B = 230, 26, 26
    n_axes = len({l["axe"] for l in lignes})
    H = MG_H + len(lignes) * (H_L + GAP) + max(n_axes - 1, 0) * H_AXE + MG_B
    # LA GOUTTIÈRE DE DROITE PORTE DEUX CHIFFRES, pas un : le score et,
    # derrière lui, la valeur brute et l'effectif. Elle a été élargie en
    # conséquence, sans quoi les deux se chevauchent.
    utile = LARG - MG_G - 150
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
        # LA VALEUR BRUTE SUIT LE SCORE, EN GRIS ET EN PLUS PETIT. Un score de
        # 6,4 ne dit pas combien de ménages sont concernés ; la part dont il
        # est tiré le dit, et les deux ensemble se lisent d'un coup d'œil sans
        # descendre au tableau.
        val = (f'{_f(l["valeur"], 0)}&#8201;%' if l.get("valeur") is not None
               else "")
        parts.append(f'<text x="{LARG - 4}" y="{y + 14}" font-size="11" '
                     f'fill="{GRIS}" text-anchor="end">'
                     f'{val}{"  ·  " if val else ""}n={l["n"]}</text>')
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
def _profil_compare(cat, masque, autre=None):
    """Le groupe et son terme de comparaison, dimension par dimension et
    indicateur par indicateur.

    LE COMPLÉMENT, PAS L'ENSEMBLE. Comparer un groupe à un tout qui le
    contient dilue l'écart de moitié ; le complément ne se dilue pas. C'est
    la comparaison par défaut, et celle qui répond à « qu'est-ce que ce
    groupe a de particulier ».

    MAIS « PAR RAPPORT À QUI » EST UNE QUESTION À PART ENTIÈRE. Les femmes
    comparées à tout le reste de l'échantillon, ce sont les femmes contre un
    ensemble où les hommes se mêlent aux autres femmes qu'aucun filtre n'a
    retenues ; les femmes comparées aux hommes, c'est autre chose, et c'est
    souvent la question qu'on avait. Le terme de comparaison se choisit donc,
    et il est toujours rendu disjoint du groupe — sans quoi on comparerait un
    ensemble à lui-même en partie.
    """
    autre = (~masque) if autre is None else (autre & ~masque)
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
        ecarts.append({"nom": _nom(ind), "dim": T(ind["dim"]),
                       "g": a["score"], "a": b["score"],
                       "d": a["score"] - b["score"],
                       "gv": a["valeur"], "av": b["valeur"],
                       "dv": a["valeur"] - b["valeur"],
                       "n": a["n"]})
    return ag_g, ag_a, ecarts


def _classer(ecarts, tri):
    """Le même jeu d'indicateurs, rangé selon la question qu'on lui pose.

    TROIS QUESTIONS, TROIS CLASSEMENTS, ET ILS NE DONNENT PAS LA MÊME LISTE.
    « Qu'est-ce que la montagne a de particulier » se lit sur l'écart avec le
    reste ; « où la montagne est-elle le plus en difficulté » se lit sur son
    score à elle, écart ou pas — un indicateur bas partout est un problème de
    la montagne même s'il n'est pas SA spécificité. Confondre les deux fait
    passer une faiblesse générale pour une particularité locale, ou l'inverse.
    """
    if tri == "haut":
        return sorted(ecarts, key=lambda x: (-x["g"], -x["gv"]))
    if tri == "bas":
        return sorted(ecarts, key=lambda x: (x["g"], x["gv"]))
    # L'ÉCART SE FILTRE, LE SCORE NE SE FILTRE PAS. Un écart sous le seuil est
    # du bruit d'arrondi et n'a rien à faire dans un classement d'écarts ; un
    # score bas est un score bas, il reste dans le classement des scores.
    retenus = [x for x in ecarts
               if abs(x["d"]) >= ECART_MIN or abs(x["dv"]) >= VALEUR_MIN]
    return sorted(retenus, key=lambda x: (-abs(x["d"]), -abs(x["dv"])))


def _table_ecarts(ecarts, lib_g, lib_a=None):
    lib_a = lib_a or T("ec_col_reste")
    r = ['<table class="ec-tab"><thead><tr>'
         f'<th>{_e(T("ec_col_ind"))}</th>'
         f'<th class="n">{_e(lib_g)}</th>'
         f'<th class="n">{_e(lib_a)}</th>'
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


def _kpi(lib, n, sc_g, sc_a, lib_a=None, n_a=None):
    lib_a = lib_a or T("ec_col_reste")
    ecart = (sc_g - sc_a) if (sc_g is not None and sc_a is not None) else None
    coul = VERT if (ecart or 0) > 0 else ROUGE if (ecart or 0) < 0 else ENCRE3
    return (
        '<div class="ec-kpi">'
        f'<div class="ec-k"><div class="ec-k-l">{_e(lib)}</div>'
        f'<div class="ec-k-v">{_f(sc_g)}<span style="font-size:13px;'
        f'color:#8a93a5"> / 10</span></div>'
        f'<div class="ec-k-s">{_e(T("ec_effectif", n=n))}</div></div>'
        f'<div class="ec-k"><div class="ec-k-l">{_e(lib_a)}</div>'
        f'<div class="ec-k-v">{_f(sc_a)}<span style="font-size:13px;'
        f'color:#8a93a5"> / 10</span></div>'
        f'<div class="ec-k-s">'
        f'{_e(T("ec_effectif", n=n_a) if n_a is not None else T("ec_vs"))}'
        f'</div></div>'
        f'<div class="ec-k"><div class="ec-k-l">{_e(T("ec_col_ecart"))}</div>'
        f'<div class="ec-k-v" style="color:{coul}">{_f(ecart, 2, True)}</div>'
        f'<div class="ec-k-s">{_e(T("ec_indice"))}</div></div></div>')


def _combiner(cat, base, cle, avec_paysage=False):
    """Le groupe de départ, resserré par un groupe social et une localité.

    ON CROISE, ON N'EMPILE PAS DES PAGES. « Ce que la montagne a de spécial »
    est une question ; « ce que les femmes de la montagne ont de spécial » en
    est une autre, et elle n'a pas de page à elle. Deux menus suffisent à la
    poser, et l'effectif restant est annoncé — un profil calculé sur trente
    ménages doit se lire en sachant qu'ils sont trente.
    """
    st.markdown(f'<div class="ec-lab">{_e(T("ec_combiner"))}</div>',
                unsafe_allow_html=True)
    cols = st.columns(3 if avec_paysage else 2)
    masque, bouts = base.copy(), []

    soc = []
    for axe in GROUPES_SOCIAUX:
        for val, lib in _cases(cat, axe):
            soc.append((val, f'{T(dict(AXES)[axe])} · {lib}', lib))
    with cols[0]:
        k = st.selectbox(
            T("ec_c_groupe"), [None] + list(range(len(soc))),
            key=f"ec_cg_{cle}",
            format_func=lambda i: T("ec_c_tous") if i is None else soc[i][1])
    if k is not None:
        masque = masque & cat["groupes"][soc[k][0]]
        bouts.append(soc[k][2])

    with cols[1]:
        sec = st.selectbox(
            T("ec_c_section"),
            [None] + [v for v, _l in _cases(cat, "section")],
            key=f"ec_cs_{cle}",
            format_func=lambda v: T("ec_c_tous") if v is None else v)
    if sec is not None:
        masque = masque & cat["groupes"][sec]
        bouts.append(sec)

    if avec_paysage:
        with cols[2]:
            pay = st.selectbox(
                T("ec_c_paysage"),
                [None] + [v for v, _l in _cases(cat, "paysage")],
                key=f"ec_cp_{cle}",
                format_func=lambda v: T("ec_c_tous") if v is None
                else _lib(v))
        if pay is not None:
            masque = masque & cat["groupes"][pay]
            bouts.append(_lib(pay))
    return masque, bouts


def _terme(cat, cle):
    """Le terme de comparaison : tous les autres, ou un groupe nommé."""
    opts = [(None, T("ec_col_reste"))]
    for axe in GROUPES_SOCIAUX + ["paysage", "section"]:
        for val, lib in _cases(cat, axe):
            opts.append((val, f'{T(dict(AXES)[axe])} · {lib}'))
    libs = dict(opts)
    v = st.selectbox(T("ec_contre"), [k for k, _l in opts],
                     key=f"ec_ref_{cle}", format_func=lambda k: libs[k])
    if v is None:
        return None, T("ec_col_reste")
    return cat["groupes"][v], libs[v]


def _profil_carte(cat, masque):
    """L'indice du groupe, section communale par section communale."""
    vals = {}
    for v, _lib_ in _cases(cat, "section"):
        m = masque & cat["groupes"][v]
        if int(m.sum()) >= 5:
            sc = M.agreger(M.profil(cat, m))["global"]
            if sc is not None:
                vals[v] = sc
    if len(vals) < 2:
        return None
    seuils = map_render.nice_thresholds(list(vals.values()))
    svg, seuils_ret, _m = map_render.render_map_svg(
        vals, {s: 1 for s in vals}, seuils, height=560,
        polarity="eleve_bon", unite="/10")
    legende = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:7px;'
        f'margin-right:16px"><span style="width:20px;height:11px;'
        f'border-radius:3px;background:{c}"></span>'
        f'<span style="font-size:11.5px;color:#52514e">{lab}</span></span>'
        for c, lab in map_render.legend_items(seuils_ret, "eleve_bon", "/10"))
    return f'<div style="margin:6px 0 8px">{legende}</div>{svg}'


def _table_dims(ag_g, ag_a, lib, lib_a=None):
    lib_a = lib_a or T("ec_col_reste")
    r = ['<table class="ec-tab"><thead><tr>'
         f'<th>{_e(T("ec_col_dim"))}</th>'
         f'<th class="n">{_e(lib)}</th>'
         f'<th class="n">{_e(lib_a)}</th>'
         f'<th class="n">{_e(T("ec_col_ecart"))}</th>'
         '</tr></thead><tbody>']
    for c in _DIMS + ["__g"]:
        if c == "__g":
            a, b, nom = ag_g["global"], ag_a["global"], T("ec_indice")
        else:
            a = ag_g["dimensions"].get(c)
            b = ag_a["dimensions"].get(c)
            nom = T(c)
        d = (a - b) if (a is not None and b is not None) else None
        coul = VERT if (d or 0) > 0 else ROUGE if (d or 0) < 0 else ENCRE3
        r.append(f'<tr><td>{_e(nom)}</td>'
                 f'<td class="n v">{_f(a, 2)}</td>'
                 f'<td class="n">{_f(b, 2)}</td>'
                 f'<td class="n v" style="color:{coul}">{_f(d, 2, True)}</td>'
                 f'</tr>')
    r.append('</tbody></table>')
    return "".join(r)


def _rendre_profil(cat, base, lib, titre, avec_paysage=False):
    """Le profil d'un groupe : ses dimensions, puis ses indicateurs.

    LE DESSIN SE CHOISIT, LE CALCUL NE CHANGE PAS. Radar, barres, tableau et
    carte montrent les mêmes sept chiffres ; ce qui change est ce qu'on veut
    en voir — une forme, un classement, des décimales, une géographie.
    """
    if base is None:
        st.info(T("ec_rien"))
        return
    masque, bouts = _combiner(cat, base, titre, avec_paysage)
    if bouts:
        lib = " · ".join([lib] + bouts)
    n_g = int(masque.sum())
    if n_g == 0:
        st.info(T("ec_c_vide"))
        return
    # ---- par rapport à qui -----------------------------------------------
    ref, lib_ref = _terme(cat, titre)
    if ref is not None:
        ref = ref & ~masque
        if int(ref.sum()) == 0:
            st.info(T("ec_c_vide"))
            return
    n_a = int((~masque if ref is None else ref).sum())
    st.markdown(f'<p class="ec-note" style="margin:2px 0 10px">'
                f'{_e(T("ec_c_note2", n=n_g, m=n_a, q=lib_ref))}</p>',
                unsafe_allow_html=True)

    ag_g, ag_a, ecarts = _profil_compare(cat, masque, ref)
    st.markdown(_kpi(lib, n_g, ag_g["global"], ag_a["global"], lib_ref, n_a),
                unsafe_allow_html=True)

    # ---- le profil par dimension, dans la forme choisie -------------------
    axes = [T(c) for c in _DIMS]
    s_g = [ag_g["dimensions"].get(c) for c in _DIMS]
    s_a = [ag_a["dimensions"].get(c) for c in _DIMS]
    st.markdown(f'<div class="titre-bloc">{_e(T("ec_profil"))}</div>',
                unsafe_allow_html=True)
    forme = st.selectbox(T("ec_format"), ["radar", "barres", "tableau",
                                          "carte"],
                         key=f"ec_forme_{titre}",
                         format_func=lambda f: T("ec_" + f))
    if forme == "radar" and sum(1 for v in s_g if v is not None) < 3:
        st.info(T("ec_radar_court"))
        forme = "barres"

    if forme == "radar":
        # LE RADAR PORTE LES DEUX SÉRIES, jamais le groupe seul : un profil
        # sans terme de comparaison se lit comme une forme, pas comme un écart.
        series = [(lib, s_g, VERT_APRI), (lib_ref, s_a, "#8a93a5")]
        svg = radar.render_radar_svg(axes, series, taille=430)
        st.markdown(f'<div style="max-width:820px;margin:4px auto 0">{svg}'
                    f'</div>'
                    f'<div style="text-align:center;margin-top:6px">'
                    f'{radar.legende_html(series)}</div>',
                    unsafe_allow_html=True)
    elif forme == "barres":
        lignes = [{"axe": T("ec_profil"), "nom": T(c),
                   "score": ag_g["dimensions"].get(c), "valeur": None,
                   "n": n_g} for c in _DIMS]
        st.markdown(
            _barres(lignes, {"score": ag_a["global"], "n": n_g}),
            unsafe_allow_html=True)
    elif forme == "carte":
        svg = _profil_carte(cat, masque)
        if svg is None:
            st.info(T("ec_carte_vide"))
        else:
            st.markdown(f'<div style="font-family:Inter,system-ui,sans-serif">'
                        f'{svg}</div>'
                        f'<p class="ec-note">{_e(T("ec_carte_grp"))}</p>',
                        unsafe_allow_html=True)
    st.markdown(_table_dims(ag_g, ag_a, lib, lib_ref),
                unsafe_allow_html=True)

    # ---- les indicateurs, dans l'ordre demandé ---------------------------
    st.markdown(f'<div class="titre-bloc" style="margin-top:22px">'
                f'{_e(T("ec_ecarts"))}</div>', unsafe_allow_html=True)
    tri = st.selectbox(T("ec_tri"), ["ecart", "haut", "bas"],
                       key=f"ec_tri_{titre}",
                       format_func=lambda c: T("ec_tri_" + c))
    _x = {"ecart": "ec_ecarts_x", "haut": "ec_tri_haut_x",
          "bas": "ec_tri_bas_x"}[tri]
    st.markdown(f'<p class="ec-note" style="margin:0">{_e(T(_x))}</p>',
                unsafe_allow_html=True)
    classes = _classer(ecarts, tri)
    if not classes:
        st.info(T("ec_rien"))
        return
    combien = st.slider(T("ec_combien"), 5, min(40, len(classes)),
                        min(12, len(classes)), key=f"ec_n_{titre}")
    st.markdown(_table_ecarts(classes[:combien], lib, lib_ref),
                unsafe_allow_html=True)
    if any(x["n"] < N_MIN for x in classes[:combien]):
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
    _rendre_profil(cat, cat["groupes"].get(v), _lib(v), "pay")


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
    # LE PAYSAGE EST OFFERT EN PLUS SUR CETTE PAGE, et pas sur la précédente :
    # « les femmes de la montagne » se pose ici, « la montagne des femmes » se
    # pose là-bas, et proposer deux fois le même croisement dans les deux sens
    # ferait deux chemins vers le même tableau.
    _rendre_profil(cat, cat["groupes"].get(opts[k][0]), opts[k][2], "grp",
                   avec_paysage=True)


# ============================== les variables les plus alarmantes
def _table_bas(lignes, n_tot):
    """Les indicateurs les plus bas du territoire, du plus bas au plus haut."""
    r = ['<table class="ec-tab"><thead><tr>'
         f'<th>{_e(T("al_col_var"))}</th>'
         f'<th class="n">{_e(T("ec_col_score"))}</th>'
         f'<th class="n">{_e(T("ec_col_val"))}</th>'
         f'<th class="n">{_e(T("ec_col_n"))}</th></tr></thead><tbody>']
    for x in lignes:
        cl = ' class="pale"' if x["n"] < N_MIN else ""
        r.append(f'<tr{cl}><td>{_e(x["nom"])}<br>'
                 f'<span style="font-size:11px;color:#8a93a5">'
                 f'{_e(x["dim"])}</span></td>'
                 f'<td class="n v" style="color:{ROUGE}">'
                 f'{_f(x["score"], 1)}</td>'
                 f'<td class="n">{_f(x["valeur"], 1)}&#8201;%</td>'
                 f'<td class="n">{x["n"]}</td></tr>')
    r.append('</tbody></table>')
    return "".join(r)


def _table_bas_groupes(lignes):
    """Une ligne par groupe : là où il décroche le plus des autres."""
    r = ['<table class="ec-tab"><thead><tr>'
         f'<th>{_e(T("al_col_groupe"))}</th>'
         f'<th>{_e(T("al_col_var"))}</th>'
         f'<th class="n">{_e(T("al_col_sien"))}</th>'
         f'<th class="n">{_e(T("al_col_autres"))}</th>'
         f'<th class="n">{_e(T("ec_col_ecart"))}</th>'
         f'<th class="n">{_e(T("ec_col_n"))}</th></tr></thead><tbody>']
    vu = None
    for x in lignes:
        cl = ' class="pale"' if x["n"] < N_MIN else ""
        tete = "" if x["groupe"] == vu else (
            f'{_e(x["groupe"])}<br><span style="font-size:11px;'
            f'color:#8a93a5">{_e(x["registre"])}</span>')
        vu = x["groupe"]
        r.append(f'<tr{cl}><td>{tete}</td>'
                 f'<td>{_e(x["nom"])}<br><span style="font-size:11px;'
                 f'color:#8a93a5">{_e(x["dim"])}</span></td>'
                 f'<td class="n v" style="color:{ROUGE}">'
                 f'{_f(x["g"], 1)}</td>'
                 f'<td class="n">{_f(x["a"], 1)}</td>'
                 f'<td class="n v" style="color:{ROUGE}">'
                 f'{_f(x["d"], 1, True)}</td>'
                 f'<td class="n">{x["n"]}</td></tr>')
    r.append('</tbody></table>')
    return "".join(r)


def render_alarmes(cat):
    """Les variables sur lesquelles commencer, et rien d'autre.

    CE QUE CET ÉCRAN FAIT ET QUE LES CINQ AUTRES NE FONT PAS. Les précédents
    répondent à une question posée : cet indicateur-là, ce paysage-là, ce
    groupe-là. Celui-ci ne demande rien et balaye tout — les soixante-six
    indicateurs sur le territoire, puis les soixante-six sur chacun des vingt
    et un groupes — pour ne remonter que les scores les plus bas.

    DEUX TABLEAUX PARCE QU'IL Y A DEUX SORTES DE FAIBLESSE, et les confondre
    envoie une intervention au mauvais endroit. Une faiblesse du TERRITOIRE
    est basse partout : elle appelle une action de couverture, la même pour
    tous. Une faiblesse de GROUPE est basse pour lui et pas pour les autres :
    elle appelle un ciblage. Le premier tableau classe sur le score, le second
    sur l'écart au complément, et un indicateur bas partout ne peut donc pas
    apparaître dans le second.
    """
    if not cat or not cat.get("indicateurs"):
        return
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown(f'<div class="titre-bloc">{_e(T("al_titre"))}</div>'
                f'<p class="ec-note" style="margin:0 0 14px">'
                f'{_e(T("al_intro"))}</p>', unsafe_allow_html=True)

    tout = np.ones(cat["n"], dtype=bool)
    bas = []
    for ind in cat["indicateurs"]:
        m = _mesure(ind, tout)
        if m["score"] is not None:
            bas.append({"nom": _nom(ind), "dim": T(ind["dim"]), **m})
    if not bas:
        st.info(T("ec_rien"))
        return
    bas.sort(key=lambda x: (x["score"], x["valeur"]))

    # ---- 1 · le territoire ------------------------------------------------
    st.markdown(f'<div class="titre-bloc">{_e(T("al_t1"))}</div>'
                f'<p class="ec-note" style="margin:0">'
                f'{_e(T("al_x1", n=cat["n"]))}</p>', unsafe_allow_html=True)
    k1 = st.slider(T("al_combien"), 5, min(40, len(bas)),
                   min(15, len(bas)), key="al_k1")
    st.markdown(_table_bas(bas[:k1], cat["n"]), unsafe_allow_html=True)

    # ---- 2 · groupe par groupe -------------------------------------------
    st.markdown(f'<div class="titre-bloc" style="margin-top:26px">'
                f'{_e(T("al_t2"))}</div>'
                f'<p class="ec-note" style="margin:0">{_e(T("al_x2"))}</p>',
                unsafe_allow_html=True)
    g, d = st.columns([1.7, 1])
    with g:
        registres = st.multiselect(
            T("al_registres"), [a for a, _l in AXES],
            default=[a for a, _l in AXES], key="al_reg",
            format_func=lambda a: T(dict(AXES)[a]))
    with d:
        par = st.slider(T("al_par_groupe"), 1, 3, 1, key="al_par")
    if not registres:
        return

    lignes = []
    for axe in registres:
        for val, lib in _cases(cat, axe):
            m_g = cat["groupes"][val]
            autre = ~m_g
            pires = []
            for ind in cat["indicateurs"]:
                a, b = _mesure(ind, m_g), _mesure(ind, autre)
                if a["score"] is None or b["score"] is None:
                    continue
                d_ = a["score"] - b["score"]
                dv = a["valeur"] - b["valeur"]
                # SEUL UN DÉCROCHAGE COMPTE, pas un écart quelconque : c'est
                # un tableau de faiblesses, et un groupe qui fait MIEUX que
                # les autres n'y a rien à faire.
                if d_ >= 0 or (abs(d_) < ECART_MIN
                               and abs(dv) < VALEUR_MIN):
                    continue
                pires.append({"groupe": lib, "registre": T(dict(AXES)[axe]),
                              "nom": _nom(ind), "dim": T(ind["dim"]),
                              "g": a["score"], "a": b["score"], "d": d_,
                              "n": a["n"]})
            pires.sort(key=lambda x: x["d"])
            lignes += pires[:par]
    if not lignes:
        st.info(T("al_vide"))
        return
    st.markdown(_table_bas_groupes(lignes), unsafe_allow_html=True)
    if any(x["n"] < N_MIN for x in lignes):
        st.markdown(f'<p class="ec-note">{_e(T("ec_fragile", n=N_MIN))}</p>',
                    unsafe_allow_html=True)
