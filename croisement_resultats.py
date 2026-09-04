"""Croisement des résultats — l'outil d'exploration des réponses individuelles.

CE QUE CETTE PAGE EST

Un constructeur de requêtes sur les 483 questions de l'enquête et les cinq
registres de segmentation, avec le profil de résilience du sous-groupe obtenu,
sa distribution territoriale, et la comparaison de deux groupes.

RIEN N'Y EST CODÉ QUESTION PAR QUESTION. Le catalogue vient du fichier
d'index ; ajoutez une question à l'enquête, régénérez l'index, elle apparaît
dans les listes sans qu'une ligne de cette page change.

TROIS PARTIS PRIS D'INTERFACE

  · LE CALCUL EST IMMÉDIAT. Pas de bouton « appliquer » : Streamlit recalcule
    à chaque modification, et la requête coûte un dixième de milliseconde. Un
    bouton laisserait croire qu'il se passe quelque chose de lourd.

  · LA NÉGATION EST UN CHOIX DE LA CONDITION, pas un opérateur séparé. « N'a
    pas de latrine améliorée » est la façon dont la question se pose sur le
    terrain ; obliger à écrire NON(a une latrine améliorée) est une syntaxe de
    programmeur.

  · LE CHIFFRE ATTENDU SOUS INDÉPENDANCE EST AFFICHÉ À CÔTÉ DU CUMUL. Un
    cumul de privations n'est jamais le produit des taux : si elles frappent
    les mêmes foyers, l'observé dépasse l'attendu, et c'est cet écart qui dit
    qu'on tient un profil et non trois problèmes séparés.

CE QUE LE SCORE AFFICHÉ EST — c'est écrit aussi à l'écran, en clair. Un indice
PARTIEL, calculé sur les seuls indicateurs dont la définition se reproduit
exactement à partir des réponses individuelles (voir `croisement_moteur`). Il
se compare d'un groupe à l'autre ; il ne se compare pas au score APRI publié.
"""

import numpy as np
import streamlit as st
import streamlit.components.v1 as components

import croisement_moteur as M
# L'EXPLORATEUR EST LE PREMIER ÉCRAN DE CETTE PAGE. Le constructeur libre qui
# suit répond à « quel est le profil de CE groupe ? » ; l'explorateur répond
# à « sur CETTE question, qui répond CETTE réponse ? », qui est la question
# qu'on se pose en arrivant.
import explorateur
import i18n
import libelles_enquete
import map_render
from i18n import T

ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"
BLEU, GRIS, VERT, ROUGE, AMBRE = "#2a78d6", "#9aa4b5", "#1a8a4f", "#c33a24", "#d1730c"
COUL_A, COUL_B = "#2a78d6", "#7048b6"

MAX_CLAUSES = 8

TEXTES = {
    "cx_titre": {"en": "Cross-tabulation of results",
                 "fr": "Croisement des résultats"},
    "cx_sous_titre": {
        "en": "Build a profile, measure it, locate it",
        "fr": "Construire un profil, le mesurer, le situer"},
    "cx_intro": {
        "en": "Combine any survey answers with sex, age, wealth stratum, "
              "landscape and communal section, and read what the resulting "
              "group is: how many, where, and how it scores. **Nothing is "
              "pre-coded**: all {n} survey questions are available, and a "
              "question added to the database tomorrow appears here on its "
              "own.",
        "fr": "Combinez n'importe quelles réponses de l'enquête avec le sexe, "
              "l'âge, la strate de richesse, le paysage et la section "
              "communale, et lisez ce qu'est le groupe obtenu : combien, où, "
              "et ce qu'il vaut. **Rien n'est pré-codé** : les {n} questions "
              "de l'enquête sont disponibles, et une question ajoutée demain "
              "à la base apparaîtra ici d'elle-même."},
    "cx_avert_indice": {
        "en": "**The resilience score shown here is a partial index.** There "
              "is no APRI score per respondent: scores are computed indicator "
              "by indicator on a population. To score a subgroup, each "
              "indicator is recomputed on it and the published scale applied "
              "which is only legitimate where the definition reproduces "
              "exactly. {k} indicators out of {t} pass that test, **{p} % of "
              "the framework's weight**, across five dimensions out of six. "
              "The environmental dimension is absent by nature: forest cover "
              "and rainfall are measured by satellite and do not vary with "
              "who answered. This index therefore compares one group with "
              "another, both sides use the same indicators, and does not "
              "compare with the published APRI score.",
        "fr": "**Le score de résilience affiché ici est un indice partiel.** "
              "Il n'existe pas de score APRI par répondant : les scores sont "
              "calculés indicateur par indicateur sur une population. Pour "
              "noter un sous-groupe, chaque indicateur est recalculé sur lui "
              "et le barème publié appliqué, ce qui n'est légitime que là où "
              "la définition se reproduit exactement. {k} indicateurs sur {t} "
              "passent ce test, soit **{p} % du poids du référentiel**, sur "
              "cinq dimensions sur six. La dimension environnementale est "
              "absente par nature : couvert forestier et pluie sont mesurés "
              "par satellite et ne varient pas selon le répondant. Cet indice "
              "compare donc un groupe à un autre, les deux côtés sont "
              "calculés sur les mêmes indicateurs, et ne se compare pas au "
              "score APRI publié."},

    # ---- constructeur
    "cx_zone1": {"en": "1 · Build the profile", "fr": "1 · Construire le profil"},
    "cx_groupe_a": {"en": "Group A", "fr": "Groupe A"},
    "cx_groupe_b": {"en": "Group B", "fr": "Groupe B"},
    "cx_comparer": {"en": "Compare with a second group",
                    "fr": "Comparer avec un second groupe"},
    "cx_liaison": {"en": "Combine the conditions with",
                   "fr": "Combiner les conditions par"},
    "cx_et": {"en": "AND, all of them at once",
              "fr": "ET, toutes en même temps"},
    "cx_ou": {"en": "OR, at least one of them",
              "fr": "OU, au moins l'une d'elles"},
    "cx_variable": {"en": "Variable", "fr": "Variable"},
    "cx_sens": {"en": "Condition", "fr": "Condition"},
    "cx_est": {"en": "is / has answered", "fr": "est / a répondu"},
    "cx_nest_pas": {"en": "is not / has not answered",
                    "fr": "n'est pas / n'a pas répondu"},
    "cx_valeurs": {"en": "Values", "fr": "Valeurs"},
    "cx_choisir": {"en": "Choose one or more values",
                   "fr": "Choisissez une ou plusieurs valeurs"},
    "cx_valeurs_aide": {
        "en": "Several values are combined with OR inside the condition.",
        "fr": "Plusieurs valeurs se combinent en OU à l'intérieur de la "
              "condition."},
    "cx_ajouter": {"en": "Add a condition", "fr": "Ajouter une condition"},
    "cx_vider": {"en": "Clear", "fr": "Tout effacer"},
    "cx_supprimer": {"en": "Remove", "fr": "Retirer"},
    "cx_seule": {"en": "This condition alone: {n} respondents ({p} %)",
                 "fr": "Cette condition seule : {n} répondants ({p} %)"},
    "cx_vide": {"en": "Add a condition to define the group. With none, the "
                      "group is the whole sample.",
                "fr": "Ajoutez une condition pour définir le groupe. Sans "
                      "aucune, le groupe est l'échantillon entier."},
    "cx_seg": {"en": "Segmentation", "fr": "Segmentation"},
    "cx_questions": {"en": "Survey questions", "fr": "Questions de l'enquête"},
    "cx_r_sexe": {"en": "Sex", "fr": "Sexe"},
    "cx_r_age": {"en": "Age group", "fr": "Tranche d'âge"},
    "cx_r_richesse": {"en": "Wealth stratum", "fr": "Strate de richesse"},
    "cx_r_paysage": {"en": "Landscape", "fr": "Paysage"},
    "cx_r_section": {"en": "Communal section", "fr": "Section communale"},

    # ---- résultats
    "cx_zone2": {"en": "2 · What this group is", "fr": "2 · Ce qu'est ce groupe"},
    "cx_effectif": {"en": "Selected population", "fr": "Population sélectionnée"},
    "cx_repondants": {"en": "respondents", "fr": "répondants"},
    "cx_part": {"en": "Share of the sample", "fr": "Part de l'échantillon"},
    "cx_indice": {"en": "Partial resilience index",
                  "fr": "Indice partiel de résilience"},
    "cx_ecart_ens": {"en": "Gap with the whole sample",
                     "fr": "Écart à l'ensemble"},
    "cx_sur": {"en": "out of {n}", "fr": "sur {n}"},
    "cx_attendu": {
        "en": "If the conditions were independent of one another, this profile "
              "would concern {p} % of households. It concerns {o} %, {mot}. "
              "A cumulation is never the product of the rates: the gap is what "
              "says the deprivations strike the same homes.",
        "fr": "Si les conditions étaient indépendantes les unes des autres, ce "
              "profil concernerait {p} % des ménages. Il en concerne {o} %, "
              "{mot}. Un cumul n'est jamais le produit des taux : c'est cet "
              "écart qui dit que les privations frappent les mêmes foyers."},
    "cx_davantage": {"en": "more", "fr": "davantage"},
    "cx_moins": {"en": "fewer", "fr": "moins"},
    "cx_fragile": {
        "en": "Fewer than {n} respondents: percentages computed on this group "
              "carry a wide margin of error, and its score should be read as "
              "an indication, not as a measurement.",
        "fr": "Moins de {n} répondants : les pourcentages calculés sur ce "
              "groupe portent une large marge d'erreur, et son score se lit "
              "comme une indication, non comme une mesure."},
    "cx_aucun": {"en": "No respondent matches these conditions.",
                 "fr": "Aucun répondant ne correspond à ces conditions."},

    # ---- graphiques
    "cx_barres": {"en": "Resilience by dimension, group against the whole "
                        "sample",
                  "fr": "Résilience par dimension, le groupe contre "
                        "l'ensemble"},
    "cx_barres_note": {
        "en": "Same scale, same indicators on both sides: the bar difference "
              "is the gap, not an artefact of the scale. A dimension without "
              "a bar has no indicator reproducible at respondent level.",
        "fr": "Même échelle, mêmes indicateurs des deux côtés : la différence "
              "de barre est l'écart, non un artefact d'échelle. Une dimension "
              "sans barre n'a aucun indicateur reproductible au niveau du "
              "répondant."},
    "cx_ensemble": {"en": "Whole sample", "fr": "Ensemble de l'échantillon"},
    "cx_carte": {"en": "Where this profile is concentrated",
                 "fr": "Où ce profil se concentre"},
    "cx_carte_mesure": {"en": "Show on the map", "fr": "Afficher sur la carte"},
    "cx_m_n": {"en": "Number of respondents", "fr": "Nombre de répondants"},
    "cx_m_groupe": {"en": "Share of the group", "fr": "Part du groupe"},
    "cx_m_section": {"en": "Share of the section concerned",
                     "fr": "Part de la section concernée"},
    "cx_m_score": {"en": "Partial resilience index",
                   "fr": "Indice partiel de résilience"},
    "cx_carte_note": {
        "en": "Aggregated by communal section, no individual location is "
              "ever shown. « Share of the section » is the reading that says "
              "where the phenomenon is intense; « share of the group » says "
              "only where people are numerous.",
        "fr": "Agrégé par section communale, aucune localisation "
              "individuelle n'est jamais affichée. « Part de la section » est "
              "la lecture qui dit où le phénomène est intense ; « part du "
              "groupe » ne dit que là où les gens sont nombreux."},
    "cx_tableau": {"en": "By communal section", "fr": "Par section communale"},
    "cx_c_territoire": {"en": "Territory", "fr": "Territoire"},
    "cx_c_n": {"en": "Respondents", "fr": "Répondants"},
    "cx_c_pg": {"en": "Share of group", "fr": "Part du groupe"},
    "cx_c_ps": {"en": "Share of section", "fr": "Part de la section"},
    "cx_c_score": {"en": "Partial index", "fr": "Indice partiel"},
    "cx_indicateurs": {"en": "Indicator by indicator",
                       "fr": "Indicateur par indicateur"},
    "cx_c_ind": {"en": "Indicator", "fr": "Indicateur"},
    "cx_c_val": {"en": "Group value", "fr": "Valeur du groupe"},
    "cx_c_val_ens": {"en": "Whole sample", "fr": "Ensemble"},
    "cx_c_sc": {"en": "Score", "fr": "Score"},

    # ---- comparaison
    "cx_comp": {"en": "3 · Group A against group B",
                "fr": "3 · Le groupe A contre le groupe B"},
    "cx_comp_note": {
        "en": "The difference is B minus A, in points of the partial index. "
              "Both groups are scored on the same indicators, so the "
              "difference is readable even where the absolute level is not "
              "the published APRI score.",
        "fr": "La différence est B moins A, en points de l'indice partiel. "
              "Les deux groupes sont notés sur les mêmes indicateurs : la "
              "différence est donc lisible même là où le niveau absolu n'est "
              "pas le score APRI publié."},
    "cx_c_dim": {"en": "Dimension", "fr": "Dimension"},
    "cx_c_diff": {"en": "Difference", "fr": "Différence"},
    "cx_ensemble_col": {"en": "Overall", "fr": "Ensemble"},

    # ---- suggestions
    "cx_sugg": {"en": "Take the analysis further",
                "fr": "Pousser l'analyse plus loin"},
    "cx_sugg_note": {
        "en": "Each button adds a segmentation variable to group A, already "
              "set on its most frequent value, change it right away if "
              "another interests you.",
        "fr": "Chaque bouton ajoute une variable de segmentation au groupe A, "
              "posée d'office sur sa valeur la plus fréquente, changez-la "
              "aussitôt si une autre vous intéresse."},
    "cx_sugg_ajouter": {"en": "Add {v}", "fr": "Ajouter {v}"},
    "cx_absent": {"en": "The cross-tabulation files are missing from the "
                        "repository (croisement.npz, croisement_index.json).",
                  "fr": "Les fichiers de croisement sont absents du dépôt "
                        "(croisement.npz, croisement_index.json)."},
    "cx_couverture": {"en": "{p} % of the framework", "fr": "{p} % du référentiel"},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)

STYLE = """
<style>
  .cx-lab  { font-size:11px; letter-spacing:.09em; text-transform:uppercase;
             font-weight:700; color:#8a93a5; margin:14px 0 5px; }
  .cx-kpi  { display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr));
             gap:14px; margin:6px 0 4px; }
  .cx-k    { background:#fff; border:1px solid #e6ecf4; border-radius:13px;
             padding:14px 16px; }
  .cx-k-l  { font-size:10.5px; letter-spacing:.08em; text-transform:uppercase;
             font-weight:700; color:#8a93a5; }
  .cx-k-v  { font-size:24px; font-weight:700; letter-spacing:-.025em;
             line-height:1.05; font-variant-numeric:tabular-nums; }
  .cx-k-s  { font-size:11px; color:#8a93a5; margin-top:3px; }
  .cx-bar  { display:grid; grid-template-columns:minmax(140px,1.5fr) 5fr 62px 62px;
             gap:10px; align-items:center; padding:7px 0;
             border-bottom:1px solid #f0f4f9; }
  .cx-piste{ position:relative; height:26px; }
  .cx-b1, .cx-b2 { position:absolute; left:0; height:11px; border-radius:4px; }
  .cx-b1  { top:1px; } .cx-b2 { top:14px; }
  .cx-num { font-size:12px; font-weight:700; text-align:right;
            font-variant-numeric:tabular-nums; }
  .cx-leg { display:flex; gap:18px; align-items:center; margin:2px 0 8px;
            font-size:11.5px; color:#3c4761; }
  .cx-leg span.p { width:13px; height:11px; border-radius:3px;
                   display:inline-block; margin-right:6px; }
  .cx-t   { width:100%; border-collapse:collapse; font-size:13px; }
  .cx-t th{ text-align:right; padding:8px 10px; border-bottom:2px solid #e6ecf4;
            font-size:11px; letter-spacing:.05em; text-transform:uppercase;
            color:#6b7590; font-weight:700; }
  .cx-t th:first-child, .cx-t td:first-child { text-align:left; }
  .cx-t td{ text-align:right; padding:7px 10px; border-bottom:1px solid #f0f4f9;
            font-variant-numeric:tabular-nums; }
</style>
"""


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _f(v, dec=1, signe=False):
    if v is None:
        return "—"
    s = f"{v:+.{dec}f}" if signe else f"{v:.{dec}f}"
    return s.replace(".", ",")


@st.cache_data(show_spinner=False)
def _catalogue():
    return M.charger()


def _nom_ind(l):
    return (l.get("nom_fr") or l.get("nom")) if i18n.get_lang() == "fr" \
        else (l.get("nom") or l.get("nom_fr"))


def _lib_valeur(v):
    """Le libellé d'une valeur de segmentation, dans la langue courante."""
    cles = {"Homme": "hommes", "Femme": "femmes", "Cat A": "cat_a",
            "Cat B": "cat_b", "Cat C": "cat_c", "<25": "age_25",
            "25-39": "age_25_39", "40-59": "age_40_59", "60+": "age_60",
            "Littoral": "pay_Littoral", "Montagne": "pay_Montagne"}
    return T(cles[v]) if v in cles else v


# --------------------------------------------------------------- constructeur
def _options(cat):
    """La liste déroulante des variables : segmentation d'abord, puis les
    questions de l'enquête, préfixées de leur module en clair."""
    opts, meta = [], {}
    for nom, _vals in M.REGISTRES:
        lib = f'▸ {T("cx_seg")} · {T("cx_r_" + nom)}'
        opts.append(lib)
        meta[lib] = ("groupe", nom)
    for q in cat["questions"]:
        lib = libelles_enquete.libelle(q)
        # Deux questions peuvent porter le même libellé dans deux modules :
        # on suffixe par l'indice pour que la clé reste unique et stable.
        if lib in meta:
            lib = f'{lib} ({q["i"]})'
        opts.append(lib)
        meta[lib] = ("question", q["i"])
    return opts, meta


def _clauses(cle):
    st.session_state.setdefault(f"cx_cl_{cle}", [])
    return st.session_state[f"cx_cl_{cle}"]


def _constructeur(cat, cle, couleur, titre):
    """Zone 1 pour un groupe. Rend (masque, clauses, liaison)."""
    opts, meta = _options(cat)
    clauses = _clauses(cle)

    st.markdown(
        f'<div style="font-size:14px;font-weight:700;color:{couleur};'
        f'margin:2px 0 6px">{_e(titre)}</div>', unsafe_allow_html=True)

    liaison = st.radio(
        T("cx_liaison"), ["ET", "OU"],
        format_func=lambda k: T("cx_et") if k == "ET" else T("cx_ou"),
        horizontal=True, key=f"cx_li_{cle}_{i18n.get_lang()}")

    a_retirer = None
    for k, cl in enumerate(clauses):
        with st.container(border=True):
            c1, c2, c3 = st.columns([3.4, 1.7, 0.9],
                                    vertical_alignment="bottom")
            with c1:
                courant = cl.get("libelle")
                idx = opts.index(courant) if courant in opts else 0
                choix = st.selectbox(T("cx_variable"), opts, index=idx,
                                     key=f"cx_v_{cle}_{k}_{i18n.get_lang()}")
            typ, ref = meta[choix]
            # Changer de variable vide les valeurs cochées : elles
            # appartenaient à l'ancienne, et les garder ferait disparaître la
            # condition en silence.
            if cl.get("libelle") != choix:
                cl.update({"libelle": choix, "type": typ,
                           "qi": ref if typ == "question" else None,
                           "registre": ref if typ == "groupe" else None,
                           "modalites": [], "valeurs": []})
            with c2:
                cl["non"] = st.selectbox(
                    T("cx_sens"), [False, True],
                    index=1 if cl.get("non") else 0,
                    format_func=lambda b: T("cx_nest_pas") if b
                    else T("cx_est"),
                    key=f"cx_n_{cle}_{k}_{i18n.get_lang()}")
            with c3:
                if st.button(T("cx_supprimer"), key=f"cx_del_{cle}_{k}",
                             use_container_width=True):
                    a_retirer = k

            if typ == "groupe":
                vals = dict(M.REGISTRES)[ref]
                cl["valeurs"] = st.multiselect(
                    T("cx_valeurs"), vals, default=[v for v in cl.get("valeurs", [])
                                                    if v in vals],
                    format_func=_lib_valeur,
                    key=f"cx_m_{cle}_{k}_{ref}_{i18n.get_lang()}",
                    placeholder=T("cx_choisir"), help=T("cx_valeurs_aide"))
            else:
                q = next(x for x in cat["questions"] if x["i"] == ref)
                cl["modalites"] = st.multiselect(
                    T("cx_valeurs"), q["modalites"],
                    format_func=libelles_enquete.modalite,
                    default=[m for m in cl.get("modalites", [])
                             if m in q["modalites"]],
                    key=f"cx_m_{cle}_{k}_{ref}_{i18n.get_lang()}",
                    placeholder=T("cx_choisir"), help=T("cx_valeurs_aide"))

            seule, _ = M.evaluer(cat, [cl], "ET")
            if (cl.get("modalites") or cl.get("valeurs")):
                nb = int(seule.sum())
                st.caption(T("cx_seule", n=nb, p=_f(100 * nb / cat["n"])))

    if a_retirer is not None:
        clauses.pop(a_retirer)
        st.rerun()

    c1, c2, _ = st.columns([1.3, 1, 3])
    with c1:
        if st.button(T("cx_ajouter"), key=f"cx_add_{cle}",
                     use_container_width=True,
                     disabled=len(clauses) >= MAX_CLAUSES):
            clauses.append({"libelle": None, "type": None, "modalites": [],
                            "valeurs": [], "non": False})
            st.rerun()
    with c2:
        if st.button(T("cx_vider"), key=f"cx_clr_{cle}",
                     use_container_width=True, disabled=not clauses):
            st.session_state[f"cx_cl_{cle}"] = []
            st.rerun()

    actives = [c for c in clauses if c.get("modalites") or c.get("valeurs")]
    if not actives:
        st.caption(T("cx_vide"))
    masque, _ = M.evaluer(cat, actives, liaison)
    return masque, actives, liaison


# ------------------------------------------------------------------ visuels
def _barres_dimensions(ag_grp, ag_ens, ag_b=None, coul_b=COUL_B):
    """Les dimensions, groupe contre ensemble, sur une échelle fixe 0–10."""
    lignes = []
    for cle, _long in M.DIMENSIONS:
        g = ag_grp["dimensions"].get(cle)
        e = ag_ens["dimensions"].get(cle)
        if g is None and e is None:
            continue
        b = ag_b["dimensions"].get(cle) if ag_b else None
        barres = (f'<div class="cx-b1" style="width:{10 * (g or 0):.1f}%;'
                  f'background:{COUL_A}"></div>'
                  f'<div class="cx-b2" style="width:{10 * (e or 0):.1f}%;'
                  f'background:{GRIS}"></div>')
        if b is not None:
            barres = (f'<div class="cx-b1" style="width:{10 * (g or 0):.1f}%;'
                      f'background:{COUL_A}"></div>'
                      f'<div class="cx-b2" style="width:{10 * b:.1f}%;'
                      f'background:{coul_b}"></div>')
        ref = b if b is not None else e
        ecart = (g - ref) if (g is not None and ref is not None) else None
        lignes.append(
            f'<div class="cx-bar"><div style="font-size:12.5px;color:{ENCRE}">'
            f'{_e(T(cle))}</div>'
            f'<div class="cx-piste">{barres}</div>'
            f'<div class="cx-num" style="color:{ENCRE}">{_f(g, 2)}</div>'
            f'<div class="cx-num" style="color:'
            f'{VERT if (ecart or 0) > 0 else ROUGE if (ecart or 0) < 0 else ENCRE3}">'
            f'{_f(ecart, 2, True)}</div></div>')
    return "".join(lignes)


def _carte(cat, sections, mesure):
    """La carte par section communale — jamais un point individuel."""
    if mesure == "n":
        vals = {s["section"]: float(s["n"]) for s in sections}
        unite, polarite = "", "neutre"
    elif mesure == "groupe":
        vals = {s["section"]: 100 * s["part_groupe"] for s in sections}
        unite, polarite = "%", "neutre"
    elif mesure == "section":
        vals = {s["section"]: 100 * s["part_section"] for s in sections}
        unite, polarite = "%", "neutre"
    else:
        vals = {s["section"]: s["score"] for s in sections}
        unite, polarite = "", "eleve_bon"
    dispo = [v for v in vals.values() if v is not None]
    if not dispo or max(dispo) == min(dispo) == 0:
        return None, 0
    seuils = map_render.nice_thresholds(dispo)
    hauteur = 620
    svg, seuils_ret, _m = map_render.render_map_svg(
        vals, {s: 1 for s in vals}, seuils, height=hauteur,
        polarity=polarite, unite=unite,
        infos={s["section"]: T("cx_seule", n=s["n"],
                               p=_f(100 * s["part_section"]))
               for s in sections})
    legende = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:7px;'
        f'margin-right:16px"><span style="width:20px;height:11px;'
        f'border-radius:3px;background:{c}"></span>'
        f'<span style="font-size:11.5px;color:#52514e">{lab}</span></span>'
        for c, lab in map_render.legend_items(seuils_ret, polarite, unite))
    return ('<div style="font-family:Inter,system-ui,sans-serif;'
            f'background:#fff"><div style="margin:0 0 8px">{legende}</div>'
            f'{svg}</div>'), hauteur


def _tableau_sections(sections):
    ent = [T("cx_c_territoire"), T("cx_c_n"), T("cx_c_pg"), T("cx_c_ps"),
           T("cx_c_score")]
    li = ['<table class="cx-t"><tr>' + "".join(f"<th>{_e(h)}</th>" for h in ent)
          + "</tr>"]
    for s in sorted(sections, key=lambda x: -x["part_section"]):
        li.append(
            f'<tr><td>{_e(s["section"])}</td>'
            f'<td>{s["n"]}</td>'
            f'<td style="color:{ENCRE3}">{_f(100 * s["part_groupe"])} %</td>'
            f'<td style="font-weight:700">{_f(100 * s["part_section"])} %</td>'
            f'<td>{_f(s["score"], 2)}</td></tr>')
    return "".join(li) + "</table>"


def _tableau_indicateurs(lignes_g, lignes_e):
    par_e = {l["ligne"]: l for l in lignes_e}
    ent = [T("cx_c_ind"), T("cx_c_val"), T("cx_c_val_ens"), T("cx_c_sc")]
    li = ['<table class="cx-t"><tr>' + "".join(f"<th>{_e(h)}</th>" for h in ent)
          + "</tr>"]
    for l in sorted(lignes_g, key=lambda x: (x["score"] is None, x["score"] or 0)):
        e = par_e.get(l["ligne"], {})
        d = ((l["valeur"] - e["valeur"])
             if l["valeur"] is not None and e.get("valeur") is not None else None)
        li.append(
            f'<tr><td>L{l["ligne"]} · {_e(_nom_ind(l))}</td>'
            f'<td style="font-weight:600">{_f(l["valeur"])} %'
            f'<span style="color:{VERT if (d or 0) > 0 else ROUGE if (d or 0) < 0 else ENCRE3};'
            f'font-size:11px"> ({_f(d, 1, True)})</span></td>'
            f'<td style="color:{ENCRE3}">{_f(e.get("valeur"))} %</td>'
            f'<td style="font-weight:700">{_f(l["score"], 0)}</td></tr>')
    return "".join(li) + "</table>"


# -------------------------------------------------------------------- rendu
def render():
    cat = _catalogue()
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown(
        f'<h2 style="font-size:21.5px;font-weight:700;color:{ENCRE};'
        f'letter-spacing:-.02em;margin:2px 0 0">{T("cx_titre")}</h2>'
        f'<p style="font-size:11.5px;color:{ENCRE3};letter-spacing:.06em;'
        f'text-transform:uppercase;margin:2px 0 0;font-weight:600">'
        f'{T("cx_sous_titre")}</p>', unsafe_allow_html=True)
    if not cat:
        st.error(T("cx_absent"))
        return

    # ---- l'explorateur : question, réponse, ventilation, format --------
    explorateur.render(cat)
    st.markdown('<div style="height:26px"></div>', unsafe_allow_html=True)

    couv = M.couverture(cat)
    st.info(T("cx_intro", n=len(cat["questions"])))
    st.warning(T("cx_avert_indice", k=len(cat["indicateurs"]),
                 t=cat["n_scores"],
                 p=_f(100 * couv["global"], 0)))

    tout = np.ones(cat["n"], dtype=bool)
    lignes_e = M.profil(cat, tout)
    ag_ens = M.agreger(lignes_e)

    # ------------------------------------------------------------- zone 1
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("cx_zone1")}</div>',
                    unsafe_allow_html=True)
        duo = st.toggle(T("cx_comparer"), key="cx_duo")
        if duo:
            ca, cb = st.columns(2)
            with ca:
                m_a, cl_a, _li = _constructeur(cat, "A", COUL_A,
                                               T("cx_groupe_a"))
            with cb:
                m_b, cl_b, _li2 = _constructeur(cat, "B", COUL_B,
                                                T("cx_groupe_b"))
        else:
            m_a, cl_a, _li = _constructeur(cat, "A", COUL_A, T("cx_groupe_a"))
            m_b, cl_b = None, []

    n_a = int(m_a.sum())
    if n_a == 0:
        st.error(T("cx_aucun"))
        return

    lignes_a = M.profil(cat, m_a)
    ag_a = M.agreger(lignes_a)
    ag_b = M.agreger(M.profil(cat, m_b)) if m_b is not None else None

    # ------------------------------------------------------------- zone 2
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc vert">{T("cx_zone2")}</div>',
                    unsafe_allow_html=True)
        ecart = ((ag_a["global"] - ag_ens["global"])
                 if ag_a["global"] is not None and ag_ens["global"] is not None
                 else None)
        st.markdown(
            '<div class="cx-kpi">'
            f'<div class="cx-k"><div class="cx-k-l">{_e(T("cx_effectif"))}'
            f'</div><div class="cx-k-v" style="color:{COUL_A}">{n_a}</div>'
            f'<div class="cx-k-s">{_e(T("cx_repondants"))} · '
            f'{_e(T("cx_sur", n=cat["n"]))}</div></div>'
            f'<div class="cx-k"><div class="cx-k-l">{_e(T("cx_part"))}</div>'
            f'<div class="cx-k-v" style="color:{ENCRE}">'
            f'{_f(100 * n_a / cat["n"])} %</div>'
            f'<div class="cx-k-s">{_e(T("cx_ensemble"))}</div></div>'
            f'<div class="cx-k"><div class="cx-k-l">{_e(T("cx_indice"))}</div>'
            f'<div class="cx-k-v" style="color:{ENCRE}">'
            f'{_f(ag_a["global"], 2)}<span style="font-size:13px;'
            f'color:#8a93a5"> / 10</span></div>'
            f'<div class="cx-k-s">'
            f'{_e(T("cx_couverture", p=_f(100 * couv["global"], 0)))}</div>'
            f'</div>'
            f'<div class="cx-k"><div class="cx-k-l">{_e(T("cx_ecart_ens"))}'
            f'</div><div class="cx-k-v" style="color:'
            f'{VERT if (ecart or 0) > 0 else ROUGE if (ecart or 0) < 0 else ENCRE3}">'
            f'{_f(ecart, 2, True)}</div>'
            f'<div class="cx-k-s">{_e(T("cx_ensemble"))} '
            f'{_f(ag_ens["global"], 2)}</div></div></div>',
            unsafe_allow_html=True)

        if n_a < M.N_FRAGILE:
            st.warning(T("cx_fragile", n=M.N_FRAGILE))

        # L'écart au produit des taux : ce qui distingue un profil cumulé
        # d'une addition de problèmes indépendants.
        if len(cl_a) > 1 and _li == "ET":
            parts = []
            for c in cl_a:
                m, _ = M.evaluer(cat, [c], "ET")
                parts.append(m.mean())
            attendu = 100 * float(np.prod(parts))
            obs = 100 * n_a / cat["n"]
            st.caption(T("cx_attendu", p=_f(attendu), o=_f(obs),
                         mot=T("cx_davantage") if obs > attendu
                         else T("cx_moins")))

    # -------------------------------------------------------- les barres
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("cx_barres")}</div>',
                    unsafe_allow_html=True)
        st.markdown(
            f'<div class="cx-leg"><span><span class="p" '
            f'style="background:{COUL_A}"></span>{_e(T("cx_groupe_a"))}</span>'
            f'<span><span class="p" style="background:'
            f'{COUL_B if ag_b else GRIS}"></span>'
            f'{_e(T("cx_groupe_b") if ag_b else T("cx_ensemble"))}</span>'
            f'</div>' + _barres_dimensions(ag_a, ag_ens, ag_b),
            unsafe_allow_html=True)
        st.caption(T("cx_barres_note"))

    # ---------------------------------------------------------- la carte
    sections = M.par_section(cat, m_a)
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc vert">{T("cx_carte")}</div>',
                    unsafe_allow_html=True)
        mesure = st.radio(
            T("cx_carte_mesure"), ["section", "n", "groupe", "score"],
            format_func=lambda k: {"n": T("cx_m_n"), "groupe": T("cx_m_groupe"),
                                   "section": T("cx_m_section"),
                                   "score": T("cx_m_score")}[k],
            horizontal=True, key=f"cx_carte_{i18n.get_lang()}")
        html, h = _carte(cat, sections, mesure)
        if html:
            components.html(html, height=h + 46, scrolling=False)
        st.caption(T("cx_carte_note"))
        st.markdown(f'<div class="cx-lab">{_e(T("cx_tableau"))}</div>'
                    + _tableau_sections(sections), unsafe_allow_html=True)

    # ----------------------------------------------------- la comparaison
    if ag_b is not None and m_b is not None and int(m_b.sum()) > 0:
        with st.container(border=True):
            st.markdown(f'<div class="titre-bloc">{T("cx_comp")}</div>',
                        unsafe_allow_html=True)
            n_b = int(m_b.sum())
            ent = [T("cx_c_dim"), T("cx_groupe_a"), T("cx_groupe_b"),
                   T("cx_c_diff")]
            li = ['<table class="cx-t"><tr>'
                  + "".join(f"<th>{_e(h)}</th>" for h in ent) + "</tr>"]
            paires = [(T(c), ag_a["dimensions"].get(c), ag_b["dimensions"].get(c))
                      for c, _l in M.DIMENSIONS]
            paires.append((T("cx_ensemble_col"), ag_a["global"], ag_b["global"]))
            for nom, a, b in paires:
                if a is None and b is None:
                    continue
                d = (b - a) if (a is not None and b is not None) else None
                li.append(
                    f'<tr><td>{_e(nom)}</td><td>{_f(a, 2)}</td>'
                    f'<td>{_f(b, 2)}</td>'
                    f'<td style="font-weight:700;color:'
                    f'{VERT if (d or 0) > 0 else ROUGE if (d or 0) < 0 else ENCRE3}">'
                    f'{_f(d, 2, True)}</td></tr>')
            st.markdown("".join(li) + "</table>", unsafe_allow_html=True)
            st.caption(T("cx_comp_note") + f'  ·  A : {n_a} · B : {n_b} '
                       + T("cx_repondants"))

    # ------------------------------------------------ indicateur par indicateur
    with st.expander(T("cx_indicateurs")):
        st.markdown(_tableau_indicateurs(lignes_a, lignes_e),
                    unsafe_allow_html=True)

    # ------------------------------------------------------- suggestions
    manquants = M.suggestions(cat, cl_a)
    if manquants:
        with st.container(border=True):
            st.markdown(f'<div class="titre-bloc">{T("cx_sugg")}</div>',
                        unsafe_allow_html=True)
            st.caption(T("cx_sugg_note"))
            cols = st.columns(min(len(manquants), 5))
            for col, nom in zip(cols, manquants[:5]):
                with col:
                    if st.button(T("cx_sugg_ajouter", v=T("cx_r_" + nom)),
                                 key=f"cx_sg_{nom}", use_container_width=True):
                        vals = dict(M.REGISTRES)[nom]
                        # La valeur la plus fréquente d'abord : elle donne un
                        # groupe assez grand pour être lisible, et c'est le
                        # point de départ le moins arbitraire.
                        meilleure = max(
                            vals, key=lambda v: int(cat["groupes"][v].sum())
                            if v in cat["groupes"] else 0)
                        lib = f'▸ {T("cx_seg")} · {T("cx_r_" + nom)}'
                        _clauses("A").append(
                            {"libelle": lib, "type": "groupe",
                             "registre": nom, "valeurs": [meilleure],
                             "modalites": [], "non": False})
                        st.rerun()
