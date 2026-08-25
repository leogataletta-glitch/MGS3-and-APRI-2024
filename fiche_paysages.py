"""Fiche synthèse — résilience des paysages. Une fiche de restitution.

CE QU'ELLE DOIT PERMETTRE

Qu'une personne qui n'a jamais entendu parler de l'APRI comprenne en quelques
secondes comment le littoral et la montagne se différencient, quelles sont
leurs forces et leurs faiblesses, et quels groupes sociaux s'en sortent le
mieux ou le moins bien. D'où l'ordre : le chiffre d'abord, l'écart ensuite, le
détail en dernier et replié.

AUCUNE CONCLUSION N'EST ÉCRITE À L'AVANCE. Les phrases de « ce qu'il faut
retenir » sont composées à partir des scores calculés le jour même : si les
données changent, la synthèse change avec elles. Une fiche de restitution dont
les conclusions sont figées dans le code devient fausse à la première mise à
jour, et personne ne s'en aperçoit.

=======================================================================
DEUX SOURCES DE SCORES, ET IL FAUT SAVOIR LAQUELLE ON LIT
=======================================================================

  · LE PAYSAGE SEUL — littoral contre montagne — est un découpage PUBLIÉ. Le
    référentiel donne le score de chaque indicateur pour chacun des deux, sur
    les 66 indicateurs scorés. C'est ce qui est affiché en tête et dans le
    classement des écarts : rien n'y est recalculé.

  · LE PAYSAGE CROISÉ AVEC UN GROUPE — « montagne × catégorie A » — n'existe
    dans aucun fichier. Le référentiel publie vingt-deux découpages, pas leurs
    croisements. Ces cases-là sont donc recalculées par le moteur de
    croisement, qui applique la même méthode — valeur de l'indicateur sur le
    sous-groupe, puis barème publié — mais seulement sur les indicateurs dont
    la définition se reproduit exactement à partir des réponses individuelles.

Les deux échelles ne sont donc pas comparables entre elles, et la fiche le dit
là où elles se touchent. Elles sont en revanche parfaitement comparables
CHACUNE AVEC ELLE-MÊME, ce qui est tout ce qu'un classement demande.
"""

import json
import os

import streamlit as st

import croisement_moteur as CM
import i18n
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"
VERT, ROUGE, AMBRE, BLEU, GRIS = "#1a8a4f", "#c33a24", "#d1730c", "#2a78d6", "#9aa4b5"
# Les deux paysages ont chacun leur couleur, et elle ne change nulle part dans
# la fiche : c'est ce qui permet de lire un graphique sans relire sa légende.
COUL = {"Littoral": "#1a6bb0", "Montagne": "#2a6b3f"}

PAYSAGES = ["Littoral", "Montagne"]
SECTIONS = CM.SECTIONS
DIMENSIONS = CM.DIMENSIONS

REGISTRES = [
    ("socio", ["Cat A", "Cat B", "Cat C"]),
    ("sexe", ["Homme", "Femme"]),
    ("age", ["<25", "25-39", "40-59", "60+"]),
    ("localite", SECTIONS),
]

TEXTES = {
    "fp_titre": {"en": "Landscape synthesis sheet",
                 "fr": "Fiche synthèse, résilience des paysages"},
    "fp_sous_titre": {"en": "Coastal plain against mountain interior",
                      "fr": "Plaine littorale contre intérieur montagneux"},
    "fp_intro": {
        "en": "The two landscapes of the survey area, side by side: which one "
              "holds up better, on what, and which social groups carry the "
              "difference. Every figure here is computed from the data, "
              "including the sentences.",
        "fr": "Les deux paysages de la zone d'enquête, côte à côte : lequel "
              "tient le mieux, sur quoi, et quels groupes sociaux portent la "
              "différence. Tous les chiffres de cette fiche sont calculés sur "
              "les données, y compris les phrases."},

    # ---- 1
    "fp_s1": {"en": "1 · The two landscapes, overall",
              "fr": "1 · Les deux paysages, d'ensemble"},
    "fp_global": {"en": "Overall resilience score",
                  "fr": "Score global de résilience"},
    "fp_ecart": {"en": "Gap", "fr": "Écart"},
    "fp_devant": {"en": "ahead", "fr": "en tête"},
    "fp_derriere": {"en": "behind", "fr": "en retrait"},
    "fp_publie": {
        "en": "Published scores, computed on all {n} scored indicators of the "
              "framework. Nothing is recomputed on this block.",
        "fr": "Scores publiés, calculés sur les {n} indicateurs scorés du "
              "référentiel. Rien n'est recalculé sur ce bloc."},
    "fp_dims": {"en": "Dimension by dimension", "fr": "Dimension par dimension"},
    "fp_dims_note": {
        "en": "Same fixed 0–10 scale on both sides. The rightmost column is "
              "the gap in points, coloured for the landscape it favours.",
        "fr": "Même échelle fixe de 0 à 10 des deux côtés. La colonne de "
              "droite est l'écart en points, colorée au profit du paysage "
              "qu'il avantage."},

    # ---- 2
    "fp_s2": {"en": "2 · What separates them most",
              "fr": "2 · Ce qui les sépare le plus"},
    "fp_s2_note": {
        "en": "Every scored indicator, ranked by the size of the gap between "
              "the two landscapes. Gaps are read on the score out of ten, not "
              "on the raw value: a score is comparable from one indicator to "
              "the next, a percentage of households is not comparable with a "
              "hectare of forest.",
        "fr": "Chaque indicateur scoré, classé par l'ampleur de l'écart entre "
              "les deux paysages. Les écarts se lisent sur le score sur dix, "
              "non sur la valeur brute : un score se compare d'un indicateur à "
              "l'autre, un pourcentage de ménages ne se compare pas à un "
              "hectare de forêt."},
    "fp_c_rang": {"en": "Rank", "fr": "Rang"},
    "fp_c_var": {"en": "Indicator", "fr": "Variable / Indicateur"},
    "fp_c_dim": {"en": "Dimension", "fr": "Dimension"},
    "fp_c_fav": {"en": "More favourable landscape",
                 "fr": "Paysage le plus favorable"},
    "fp_combien": {"en": "How many indicators to show",
                   "fr": "Combien d'indicateurs afficher"},
    "fp_visuel": {"en": "The same gaps, seen at once",
                  "fr": "Les mêmes écarts, vus d'un coup"},
    "fp_visuel_note": {
        "en": "Bars to the left favour the mountain, to the right the coast. "
              "Length is the gap in points of score.",
        "fr": "Les barres vers la gauche avantagent la montagne, vers la "
              "droite le littoral. La longueur est l'écart en points de "
              "score."},

    # ---- 3
    "fp_s3": {"en": "3 · The landscape as a social system",
              "fr": "3 · Le paysage comme système social"},
    "fp_s3_note": {
        "en": "A landscape is not only a place: the same coast is not lived "
              "the same way by every household. Crossing landscape with a "
              "social breakdown shows who carries the average.",
        "fr": "Un paysage n'est pas qu'un lieu : le même littoral n'est pas "
              "vécu de la même façon par tous les ménages. Croiser le paysage "
              "avec un découpage social montre qui porte la moyenne."},
    "fp_recalc": {
        "en": "**These scores are recomputed, not published.** No file holds "
              "the score of « mountain × category A »: the framework "
              "publishes twenty-two breakdowns, not their crossings. The same "
              "method is applied, indicator value on the subgroup, then the "
              "published scale, but only on the {k} indicators whose "
              "definition reproduces exactly from the individual answers, "
              "**{p} % of the framework's weight**. These figures are "
              "therefore comparable with one another, and not with the "
              "published scores of block 1.",
        "fr": "**Ces scores sont recalculés, non publiés.** Aucun fichier ne "
              "porte le score de « montagne × catégorie A » : le référentiel "
              "publie vingt-deux découpages, pas leurs croisements. La même "
              "méthode est appliquée, valeur de l'indicateur sur le "
              "sous-groupe, puis barème publié, mais sur les seuls {k} "
              "indicateurs dont la définition se reproduit exactement à partir "
              "des réponses individuelles, soit **{p} % du poids du "
              "référentiel**. Ces chiffres se comparent donc entre eux, et non "
              "aux scores publiés du bloc 1."},
    "fp_croiser": {"en": "Cross the landscape with",
                   "fr": "Croiser le paysage avec"},
    "fp_r_socio": {"en": "Socio-economic group",
                   "fr": "Groupe socio-économique"},
    "fp_r_sexe": {"en": "Sex", "fr": "Sexe"},
    "fp_r_age": {"en": "Age group", "fr": "Classe d'âge"},
    "fp_r_localite": {"en": "Locality", "fr": "Localité"},
    "fp_c_pays": {"en": "Landscape", "fr": "Paysage"},
    "fp_c_grp": {"en": "Group", "fr": "Groupe"},
    "fp_c_n": {"en": "Respondents", "fr": "Répondants"},
    "fp_c_score": {"en": "Partial index", "fr": "Indice partiel"},
    "fp_c_niv": {"en": "Vulnerability", "fr": "Niveau de vulnérabilité"},
    "fp_n_haute": {"en": "high", "fr": "élevée"},
    "fp_n_moyenne": {"en": "medium", "fr": "moyenne"},
    "fp_n_faible": {"en": "low", "fr": "faible"},
    "fp_niv_note": {
        "en": "The vulnerability level is not a judgement: the cells are cut "
              "in three equal parts between the lowest and the highest score "
              "of the table. Close scores keep their rank, no artificial "
              "difference is created.",
        "fr": "Le niveau de vulnérabilité n'est pas un jugement : les cases "
              "sont découpées en trois parts égales entre le score le plus bas "
              "et le plus haut du tableau. Des scores proches gardent leur "
              "rang, aucune différence artificielle n'est créée."},
    "fp_fragile": {
        "en": "Cells under {n} respondents are shown with their count: their "
              "score is an indication, not a measurement.",
        "fr": "Les cases sous {n} répondants sont affichées avec leur "
              "effectif : leur score est une indication, non une mesure."},

    # ---- 4 & 5
    "fp_s4": {"en": "4 · The two ends", "fr": "4 · Les deux extrémités"},
    "fp_plus_vuln": {"en": "Most vulnerable", "fr": "Le plus vulnérable"},
    "fp_plus_res": {"en": "Most resilient", "fr": "Le plus résilient"},
    "fp_dans": {"en": "in the {p}", "fr": "sur le {p}"},
    "fp_s5": {"en": "5 · The vulnerability matrix",
              "fr": "5 · La matrice des profils"},
    "fp_m_vuln": {"en": "Most vulnerable group", "fr": "Groupe le plus vulnérable"},
    "fp_m_inter": {"en": "Intermediate group", "fr": "Groupe intermédiaire"},
    "fp_m_res": {"en": "Most resilient group", "fr": "Groupe le plus résilient"},
    "fp_m_note": {
        "en": "One column per landscape, the groups ranked within each. When "
              "a breakdown has more than three groups, the intermediate row "
              "shows the median group.",
        "fr": "Une colonne par paysage, les groupes classés à l'intérieur de "
              "chacune. Quand un découpage compte plus de trois groupes, la "
              "ligne intermédiaire montre le groupe médian."},

    # ---- 6
    "fp_s6": {"en": "What to remember", "fr": "Ce qu'il faut retenir"},
    "fp_e1": {
        "en": "**{gagnant} is ahead overall**, {a} against {b} out of 10, a "
              "gap of {d} points.",
        "fr": "**Le {gagnant} est en tête d'ensemble**, {a} contre {b} sur "
              "10, soit {d} points d'écart."},
    "fp_e2": {"en": "**What separates them most:** {liste}.",
              "fr": "**Ce qui les sépare le plus :** {liste}."},
    "fp_e3": {
        "en": "**The most vulnerable group** is {g} in the {p}, at {s} out of "
              "10 on the partial index.",
        "fr": "**Le groupe le plus vulnérable** est {g} sur le {p}, à {s} sur "
              "10 de l'indice partiel."},
    "fp_e4": {
        "en": "**The best placed** is {g} in the {p}, at {s}, a spread of "
              "{d} points between the two ends.",
        "fr": "**Le mieux placé** est {g} sur le {p}, à {s}, soit {d} points "
              "d'amplitude entre les deux extrémités."},
    "fp_e5": {
        "en": "**{g} carries a penalty specific to one landscape:** it falls "
              "{d} points between the {p1} and the {p2}, more than any other "
              "group of this breakdown. A group vulnerable in one landscape "
              "is not necessarily vulnerable in the other.",
        "fr": "**{g} porte une pénalité propre à un paysage :** ce groupe perd "
              "{d} points entre le {p1} et le {p2}, plus que tout autre groupe "
              "de ce découpage. Un groupe vulnérable dans un paysage ne l'est "
              "pas nécessairement dans l'autre."},
    "fp_e5_non": {
        "en": "**No group is penalised by one landscape in particular:** the "
              "gap between the two landscapes is of the same order for every "
              "group of this breakdown, which points to a landscape effect "
              "rather than a social one.",
        "fr": "**Aucun groupe n'est pénalisé par un paysage en particulier :** "
              "l'écart entre les deux paysages est du même ordre pour tous les "
              "groupes de ce découpage, ce qui désigne un effet de paysage "
              "plutôt qu'un effet social."},
    "fp_detail": {"en": "The detailed figures", "fr": "Les chiffres détaillés"},
    "fp_absent": {"en": "Data files missing.", "fr": "Fichiers de données absents."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)

STYLE = """
<style>
  .fp-duel { display:grid; grid-template-columns:1fr auto 1fr; gap:18px;
             align-items:center; margin:8px 0 4px; }
  .fp-cote { border:1px solid #e6ecf4; border-radius:14px; padding:16px 18px;
             background:#fff; }
  .fp-nom  { font-size:12px; font-weight:700; letter-spacing:.06em;
             text-transform:uppercase; }
  .fp-sc   { font-size:35px; font-weight:700; letter-spacing:-.03em;
             line-height:1; font-variant-numeric:tabular-nums; }
  .fp-su   { font-size:11.5px; color:#8a93a5; margin-top:4px; }
  .fp-vs   { font-size:11px; font-weight:700; color:#8a93a5;
             letter-spacing:.1em; }
  .fp-bar  { display:grid; grid-template-columns:minmax(130px,1.4fr) 5fr 58px 58px 62px;
             gap:9px; align-items:center; padding:6px 0;
             border-bottom:1px solid #f0f4f9; }
  .fp-p    { position:relative; height:24px; }
  .fp-b1,.fp-b2 { position:absolute; left:0; height:10px; border-radius:4px; }
  .fp-b1 { top:1px; } .fp-b2 { top:13px; }
  .fp-n   { font-size:12px; font-weight:700; text-align:right;
            font-variant-numeric:tabular-nums; }
  .fp-t   { width:100%; border-collapse:collapse; font-size:12.5px; }
  .fp-t th{ text-align:right; padding:8px 10px; border-bottom:2px solid #e6ecf4;
            font-size:10.5px; letter-spacing:.05em; text-transform:uppercase;
            color:#6b7590; font-weight:700; }
  .fp-t th:first-child, .fp-t td:first-child,
  .fp-t th.g, .fp-t td.g { text-align:left; }
  .fp-t td{ text-align:right; padding:7px 10px;
            border-bottom:1px solid #f0f4f9;
            font-variant-numeric:tabular-nums; }
  .fp-pill{ display:inline-block; font-size:11px; font-weight:700;
            border-radius:999px; padding:2px 9px; }
  .fp-div { display:grid; grid-template-columns:minmax(150px,1.6fr) 1fr 1fr 62px;
            gap:8px; align-items:center; padding:4px 0; }
  .fp-g   { height:15px; background:#f4f7fb; border-radius:4px;
            position:relative; }
  .fp-gl  { position:absolute; right:0; height:100%; border-radius:4px 0 0 4px; }
  .fp-gr  { position:absolute; left:0; height:100%; border-radius:0 4px 4px 0; }
  .fp-ret li { margin-bottom:7px; }
</style>
"""


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _f(v, dec=2, signe=False):
    if v is None:
        return "—"
    s = f"{v:+.{dec}f}" if signe else f"{v:.{dec}f}"
    return s.replace(".", ",")


def _trouver(nom):
    for c in (os.path.join(DATA, nom), os.path.join(APP_DIR, nom)):
        if os.path.exists(c):
            return c
    return None


@st.cache_data(show_spinner=False)
def _resultats():
    p = _trouver("resultats.json")
    if not p:
        return []
    with open(p, encoding="utf-8") as f:
        r = json.load(f)
    return r["indicateurs"] if isinstance(r, dict) and "indicateurs" in r else r


@st.cache_data(show_spinner=False)
def _catalogue():
    return CM.charger()


def _nom(r):
    if i18n.get_lang() == "fr" and r.get("indicateur_fr"):
        return r["indicateur_fr"]
    return r.get("indicateur", "")


def _lib(v):
    cles = {"Homme": "hommes", "Femme": "femmes", "Cat A": "cat_a",
            "Cat B": "cat_b", "Cat C": "cat_c", "<25": "age_25",
            "25-39": "age_25_39", "40-59": "age_40_59", "60+": "age_60",
            "Littoral": "pay_Littoral", "Montagne": "pay_Montagne"}
    return T(cles[v]) if v in cles else v


def _pondere(res, cible, dimension=None):
    """Moyenne pondérée publiée, sur tout le référentiel ou une dimension.

    Les indicateurs non calculés sortent du dénominateur, jamais comptés
    comme des zéros — la règle du reste de la plateforme."""
    num = den = 0.0
    for r in res:
        if dimension and r["dimension"] != dimension:
            continue
        s = (r.get("scores_corriges") or {}).get(cible)
        if s is None:
            continue
        p = r.get("ponderation") or 1
        num += p * s
        den += p
    return (num / den) if den else None


def _ecarts(res):
    """Les indicateurs classés par l'ampleur de l'écart entre les paysages."""
    out = []
    for r in res:
        sc = r.get("scores_corriges") or {}
        li, mo = sc.get("Littoral"), sc.get("Montagne")
        if li is None or mo is None:
            continue
        out.append({"r": r, "littoral": float(li), "montagne": float(mo),
                    "ecart": float(li) - float(mo)})
    out.sort(key=lambda x: -abs(x["ecart"]))
    return out


def _score_croise(cat, valeurs):
    """Effectif et indice partiel d'un croisement, par le moteur."""
    clauses = [{"type": "groupe", "valeurs": [v]} for v in valeurs]
    m, _ = CM.evaluer(cat, clauses, "ET")
    return int(m.sum()), CM.agreger(CM.profil(cat, m))["global"]


def _niveau(score, bas, haut):
    """Trois parts égales entre le plus bas et le plus haut du tableau. Pas un
    jugement : un découpage, dit comme tel sous le tableau."""
    if score is None or haut is None or bas is None or haut <= bas:
        return "moyenne"
    t = (score - bas) / (haut - bas)
    return "haute" if t < 1 / 3 else ("moyenne" if t < 2 / 3 else "faible")


def _barres_dimensions(res):
    li = []
    for cle, long in DIMENSIONS:
        a = _pondere(res, "Littoral", long)
        b = _pondere(res, "Montagne", long)
        if a is None and b is None:
            continue
        d = (a - b) if (a is not None and b is not None) else None
        li.append(
            f'<div class="fp-bar"><div style="font-size:12px;color:{ENCRE}">'
            f'{_e(T(cle))}</div>'
            f'<div class="fp-p">'
            f'<div class="fp-b1" style="width:{10 * (a or 0):.1f}%;'
            f'background:{COUL["Littoral"]}"></div>'
            f'<div class="fp-b2" style="width:{10 * (b or 0):.1f}%;'
            f'background:{COUL["Montagne"]}"></div></div>'
            f'<div class="fp-n" style="color:{COUL["Littoral"]}">{_f(a)}</div>'
            f'<div class="fp-n" style="color:{COUL["Montagne"]}">{_f(b)}</div>'
            f'<div class="fp-n" style="color:'
            f'{COUL["Littoral"] if (d or 0) > 0 else COUL["Montagne"]}">'
            f'{_f(d, 2, True)}</div></div>')
    return "".join(li)


def _diverge(ecarts, n=12):
    """Un diagramme divergent : montagne à gauche, littoral à droite."""
    pris = ecarts[:n]
    vmax = max((abs(e["ecart"]) for e in pris), default=1) or 1
    li = []
    for e in pris:
        d = e["ecart"]
        larg = 100 * abs(d) / vmax
        barre = (f'<div class="fp-gr" style="width:{larg:.1f}%;'
                 f'background:{COUL["Littoral"]}"></div>' if d > 0 else
                 f'<div class="fp-gl" style="width:{larg:.1f}%;'
                 f'background:{COUL["Montagne"]}"></div>')
        li.append(
            f'<div class="fp-div">'
            f'<div style="font-size:11.5px;color:{ENCRE}">'
            f'L{e["r"]["ligne"]} · {_e(_nom(e["r"]))}</div>'
            f'<div class="fp-g">{barre if d < 0 else ""}</div>'
            f'<div class="fp-g">{barre if d > 0 else ""}</div>'
            f'<div class="fp-n" style="color:'
            f'{COUL["Littoral"] if d > 0 else COUL["Montagne"]}">'
            f'{_f(d, 1, True)}</div></div>')
    entete = (f'<div class="fp-div" style="padding-bottom:4px">'
              f'<div></div>'
              f'<div style="text-align:right;font-size:11px;font-weight:700;'
              f'letter-spacing:.06em;text-transform:uppercase;'
              f'color:{COUL["Montagne"]}">{_e(_lib("Montagne"))}</div>'
              f'<div style="font-size:11px;font-weight:700;letter-spacing:.06em;'
              f'text-transform:uppercase;color:{COUL["Littoral"]}">'
              f'{_e(_lib("Littoral"))}</div><div></div></div>')
    return entete + "".join(li)


def render(entete=True):
    st.markdown(STYLE, unsafe_allow_html=True)
    if entete:
        st.markdown(
            f'<h2 style="font-size:21.5px;font-weight:700;color:{ENCRE};'
            f'letter-spacing:-.02em;margin:2px 0 0">{T("fp_titre")}</h2>'
            f'<p style="font-size:11.5px;color:{ENCRE3};letter-spacing:.06em;'
            f'text-transform:uppercase;margin:2px 0 0;font-weight:600">'
            f'{T("fp_sous_titre")}</p>', unsafe_allow_html=True)

    res = _resultats()
    cat = _catalogue()
    if not res:
        st.info(T("fp_absent"))
        return
    st.info(T("fp_intro"))

    scores = {p: _pondere(res, p) for p in PAYSAGES}
    n_ind = sum(1 for r in res
                if (r.get("scores_corriges") or {}).get("Total") is not None)
    gagnant = max(PAYSAGES, key=lambda p: scores[p] or 0)
    perdant = min(PAYSAGES, key=lambda p: scores[p] or 0)
    ecarts = _ecarts(res)

    # ------------------------------------------------------------ 1 · duel
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("fp_s1")}</div>',
                    unsafe_allow_html=True)
        cotes = []
        for p in PAYSAGES:
            devant = p == gagnant
            cotes.append(
                f'<div class="fp-cote" style="border-color:{COUL[p]}55;'
                f'border-left:5px solid {COUL[p]}">'
                f'<div class="fp-nom" style="color:{COUL[p]}">'
                f'{_e(_lib(p))}</div>'
                f'<div class="fp-sc" style="color:{ENCRE}">{_f(scores[p])}'
                f'<span style="font-size:14.5px;color:#8a93a5"> / 10</span></div>'
                f'<div class="fp-su">{_e(T("fp_global"))} · '
                f'<b style="color:{VERT if devant else AMBRE}">'
                f'{_e(T("fp_devant") if devant else T("fp_derriere"))}</b>'
                f'</div></div>')
        ec = abs((scores["Littoral"] or 0) - (scores["Montagne"] or 0))
        st.markdown(
            f'<div class="fp-duel">{cotes[0]}'
            f'<div style="text-align:center"><div class="fp-vs">'
            f'{_e(T("fp_ecart")).upper()}</div>'
            f'<div style="font-size:17.5px;font-weight:700;color:{ENCRE2};'
            f'font-variant-numeric:tabular-nums">{_f(ec)}</div></div>'
            f'{cotes[1]}</div>', unsafe_allow_html=True)
        st.caption(T("fp_publie", n=n_ind))
        st.markdown(f'<div class="titre-bloc" style="margin-top:14px">'
                    f'{T("fp_dims")}</div>' + _barres_dimensions(res),
                    unsafe_allow_html=True)
        st.caption(T("fp_dims_note"))

    # --------------------------------------------------------- 2 · écarts
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc vert">{T("fp_s2")}</div>',
                    unsafe_allow_html=True)
        st.markdown(T("fp_s2_note"))
        combien = st.slider(T("fp_combien"), 5, min(30, len(ecarts)), 12,
                            key="fp_n")
        ent = [T("fp_c_rang"), T("fp_c_var"), T("fp_c_dim"), _lib("Littoral"),
               _lib("Montagne"), T("fp_ecart"), T("fp_c_fav")]
        li = ['<table class="fp-t"><tr>'
              + "".join(f'<th class="{"g" if i in (1, 2, 6) else ""}">'
                        f'{_e(h)}</th>' for i, h in enumerate(ent)) + "</tr>"]
        for k, e in enumerate(ecarts[:combien], 1):
            fav = "Littoral" if e["ecart"] > 0 else "Montagne"
            li.append(
                f'<tr><td style="color:{ENCRE3}">{k}</td>'
                f'<td class="g">L{e["r"]["ligne"]} · {_e(_nom(e["r"]))}</td>'
                f'<td class="g" style="color:{ENCRE3};font-size:11.5px">'
                f'{_e(T(CM.DIM_DE.get(e["r"]["dimension"], "")))}</td>'
                f'<td style="color:{COUL["Littoral"]};font-weight:600">'
                f'{_f(e["littoral"], 1)}</td>'
                f'<td style="color:{COUL["Montagne"]};font-weight:600">'
                f'{_f(e["montagne"], 1)}</td>'
                f'<td style="font-weight:700">{_f(abs(e["ecart"]), 1)}</td>'
                f'<td class="g"><span class="fp-pill" '
                f'style="background:{COUL[fav]}1a;color:{COUL[fav]}">'
                f'{_e(_lib(fav))}</span></td></tr>')
        st.markdown("".join(li) + "</table>", unsafe_allow_html=True)
        st.markdown(f'<div class="titre-bloc" style="margin-top:16px">'
                    f'{T("fp_visuel")}</div>' + _diverge(ecarts, combien),
                    unsafe_allow_html=True)
        st.caption(T("fp_visuel_note"))

    # ------------------------------------------------- 3 · paysage × groupe
    cellules, registre = [], "socio"
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("fp_s3")}</div>',
                    unsafe_allow_html=True)
        st.markdown(T("fp_s3_note"))
        if not cat:
            st.info(T("fp_absent"))
        else:
            couv = CM.couverture(cat)
            st.warning(T("fp_recalc", k=len(cat["indicateurs"]),
                         p=_f(100 * couv["global"], 0)))
            registre = st.radio(
                T("fp_croiser"), [r for r, _v in REGISTRES],
                format_func=lambda r: T("fp_r_" + r), horizontal=True,
                key="fp_reg")
            for p in PAYSAGES:
                for g in dict(REGISTRES)[registre]:
                    # Une localité appartient à un seul paysage : croiser
                    # « Littoral » avec une section de montagne ne désigne
                    # personne, et la case est simplement omise.
                    n, s = _score_croise(cat, [p, g])
                    if n == 0:
                        continue
                    cellules.append({"paysage": p, "groupe": g, "n": n,
                                     "score": s})
            dispo = [c["score"] for c in cellules if c["score"] is not None]
            bas, haut = (min(dispo), max(dispo)) if dispo else (None, None)
            rangs = sorted([c for c in cellules if c["score"] is not None],
                           key=lambda c: -c["score"])
            for i, c in enumerate(rangs, 1):
                c["rang"] = i
            ent = [T("fp_c_pays"), T("fp_c_grp"), T("fp_c_n"),
                   T("fp_c_score"), T("fp_c_rang"), T("fp_c_niv")]
            li = ['<table class="fp-t"><tr>'
                  + "".join(f'<th class="{"g" if i < 2 else ""}">{_e(h)}</th>'
                            for i, h in enumerate(ent)) + "</tr>"]
            for c in sorted(cellules, key=lambda x: (x["paysage"],
                                                     -(x["score"] or 0))):
                niv = _niveau(c["score"], bas, haut)
                cn = {"haute": ROUGE, "moyenne": AMBRE, "faible": VERT}[niv]
                li.append(
                    f'<tr><td class="g"><span class="fp-pill" '
                    f'style="background:{COUL[c["paysage"]]}1a;'
                    f'color:{COUL[c["paysage"]]}">{_e(_lib(c["paysage"]))}'
                    f'</span></td>'
                    f'<td class="g">{_e(_lib(c["groupe"]))}</td>'
                    f'<td style="color:{ENCRE3}">{c["n"]}</td>'
                    f'<td style="font-weight:700;font-size:14px">'
                    f'{_f(c["score"])}</td>'
                    f'<td style="color:{ENCRE3}">{c.get("rang", "—")}</td>'
                    f'<td><span class="fp-pill" style="background:{cn}1a;'
                    f'color:{cn}">{_e(T("fp_n_" + niv))}</span></td></tr>')
            st.markdown("".join(li) + "</table>", unsafe_allow_html=True)
            st.caption(T("fp_niv_note"))
            st.caption(T("fp_fragile", n=CM.N_FRAGILE))

    # ------------------------------------------------ 4 · les deux extrémités
    if cellules:
        valides = [c for c in cellules if c["score"] is not None]
        pire = min(valides, key=lambda c: c["score"])
        meilleur = max(valides, key=lambda c: c["score"])
        with st.container(border=True):
            st.markdown(f'<div class="titre-bloc vert">{T("fp_s4")}</div>',
                        unsafe_allow_html=True)
            g, d = st.columns(2)
            for col, c, lab, coul in ((g, pire, T("fp_plus_vuln"), ROUGE),
                                      (d, meilleur, T("fp_plus_res"), VERT)):
                with col:
                    st.markdown(
                        f'<div class="fp-cote" style="border-left:5px solid '
                        f'{coul}"><div class="fp-nom" style="color:{coul}">'
                        f'{_e(lab)}</div>'
                        f'<div class="fp-sc" style="color:{ENCRE};'
                        f'font-size:27px">{_f(c["score"])}'
                        f'<span style="font-size:14px;color:#8a93a5"> / 10'
                        f'</span></div>'
                        f'<div class="fp-su">{_e(_lib(c["groupe"]))} · '
                        f'{_e(T("fp_dans", p=_lib(c["paysage"])))} · '
                        f'{c["n"]} {_e(T("fp_c_n")).lower()}</div></div>',
                        unsafe_allow_html=True)

        # ----------------------------------------------------- 5 · matrice
        with st.container(border=True):
            st.markdown(f'<div class="titre-bloc">{T("fp_s5")}</div>',
                        unsafe_allow_html=True)
            ent = ["", _lib("Littoral"), _lib("Montagne")]
            li = ['<table class="fp-t"><tr>'
                  + "".join(f'<th class="{"g" if i == 0 else ""}">{_e(h)}</th>'
                            for i, h in enumerate(ent)) + "</tr>"]
            rangees = [("fp_m_vuln", 0), ("fp_m_inter", 1), ("fp_m_res", 2)]
            for cle, pos in rangees:
                cells = []
                for p in PAYSAGES:
                    dedans = sorted([c for c in valides if c["paysage"] == p],
                                    key=lambda c: c["score"])
                    if not dedans:
                        cells.append('<td>—</td>')
                        continue
                    # Le classement est conservé : le groupe médian pour la
                    # ligne intermédiaire, jamais une moyenne inventée.
                    c = (dedans[0] if pos == 0 else dedans[-1] if pos == 2
                         else dedans[len(dedans) // 2])
                    cells.append(
                        f'<td><b>{_f(c["score"])}</b>'
                        f'<span style="color:{ENCRE3};font-size:11.5px"> · '
                        f'{_e(_lib(c["groupe"]))}</span></td>')
                li.append(f'<tr><td class="g">{_e(T(cle))}</td>'
                          + "".join(cells) + '</tr>')
            st.markdown("".join(li) + "</table>", unsafe_allow_html=True)
            st.caption(T("fp_m_note"))

    # ---------------------------------------------------- 6 · à retenir
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc ambre">{T("fp_s6")}</div>',
                    unsafe_allow_html=True)
        points = []
        points.append(T("fp_e1", gagnant=_lib(gagnant),
                        a=_f(scores[gagnant]), b=_f(scores[perdant]),
                        d=_f(ec)))
        liste = " · ".join(
            f'{_nom(e["r"])} ({_f(abs(e["ecart"]), 1)} pts, '
            f'{_lib("Littoral" if e["ecart"] > 0 else "Montagne")})'
            for e in ecarts[:4])
        points.append(T("fp_e2", liste=liste))
        if cellules:
            points.append(T("fp_e3", g=_lib(pire["groupe"]),
                            p=_lib(pire["paysage"]), s=_f(pire["score"])))
            points.append(T("fp_e4", g=_lib(meilleur["groupe"]),
                            p=_lib(meilleur["paysage"]),
                            s=_f(meilleur["score"]),
                            d=_f(meilleur["score"] - pire["score"])))
            # Le groupe dont l'écart entre paysages est le plus grand : c'est
            # lui qui répond à « vulnérable ici mais pas là ».
            par_grp = {}
            for c in valides:
                par_grp.setdefault(c["groupe"], {})[c["paysage"]] = c["score"]
            duos = [(g, v["Littoral"] - v["Montagne"]) for g, v in par_grp.items()
                    if "Littoral" in v and "Montagne" in v]
            if duos:
                g, d = max(duos, key=lambda x: abs(x[1]))
                mediane = sorted(abs(x[1]) for x in duos)[len(duos) // 2]
                if abs(d) >= max(0.5, 1.6 * mediane):
                    points.append(T("fp_e5", g=_lib(g), d=_f(abs(d)),
                                    p1=_lib("Littoral" if d > 0 else "Montagne"),
                                    p2=_lib("Montagne" if d > 0 else "Littoral")))
                else:
                    points.append(T("fp_e5_non"))
        # Rendu en markdown et non en HTML injecté : les phrases portent des
        # **passages en gras**, que Streamlit ne convertit pas à l'intérieur
        # d'un bloc HTML — les astérisques s'affichaient tels quels.
        st.markdown("\n".join(f"- {p}" for p in points))
