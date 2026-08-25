"""Analyse détaillée — ce qui s'ajoute EN TÊTE de « Analyse des résultats ».

Deux sections, dans l'ordre où la donnée se construit :

  1. LES RÉSULTATS DES QUESTIONS — la réponse brute, son effectif, sa part, et
     le groupe comme la localité qui s'en sortent le mieux et le moins bien ;
  2. LES INDICATEURS DE RÉSILIENCE — ce que le référentiel en fait : de quelle
     question chacun est tiré, quelle pondération il porte, quel score il
     produit, et là encore le meilleur et le pire groupe, la meilleure et la
     pire localité.

C'est la traçabilité qui relie les deux : la colonne « source » de la seconde
table nomme la question de la première.

=======================================================================
LE POINT DÉLICAT : « MEILLEUR » ET « PIRE » SUPPOSENT UN SENS
=======================================================================

Un pourcentage élevé n'est pas une bonne nouvelle en soi. « 80 % utilisent le
charbon de bois » est mauvais ; « 80 % ont accès à l'eau améliorée » est bon.
Nommer un « meilleur groupe » sans connaître le sens de la variable revient à
tirer à pile ou face et à l'écrire en gras.

Le sens n'est connu que là où la question ALIMENTE UN INDICATEUR du
référentiel : l'indicateur porte son barème, et un barème dont les bornes
descendent dit qu'une valeur haute vaut un score bas.

  · question reliée à un indicateur → les colonnes disent MEILLEUR et PIRE ;
  · question non reliée → elles disent PLUS HAUT et PLUS BAS, et la ligne
    porte un repère.

Deviner le sens des autres aurait produit un tableau qui a l'air complet et se
trompe une fois sur deux, sans que rien ne le signale.

LES CHIFFRES VIENNENT DU CACHE D'ENQUÊTE, qui porte l'effectif de chaque
modalité pour chaque groupe et chaque section — les mêmes nombres que le reste
du site. Les scores viennent de `resultats.json`, publiés pour les vingt-deux
découpages. Rien n'est recalculé ici, sauf le cas explicitement signalé de la
combinaison de plusieurs filtres, qui n'existe dans aucun fichier.
"""

import json
import os
import re
import unicodedata

import streamlit as st

import i18n
import questions_dimension as QD
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"
VERT, ROUGE, GRIS, BLEU = "#1a8a4f", "#c33a24", "#9aa4b5", "#2a78d6"

SECTIONS = ["Anse à Drick", "Barbois", "Dumont", "Débouchette", "Mouline",
            "Quentin", "Beaulieu", "Blactote", "Dalmette", "Trichet"]
GROUPES = ["Homme", "Femme", "<25", "25-39", "40-59", "60+",
           "Cat A", "Cat B", "Cat C", "Littoral", "Montagne"]

# Les registres proposés au filtre. « Tous » d'abord : on arrive sur
# l'ensemble, on restreint ensuite.
REGISTRES = [
    ("tous", []),
    ("sexe", ["Homme", "Femme"]),
    ("age", ["<25", "25-39", "40-59", "60+"]),
    ("socio", ["Cat A", "Cat B", "Cat C"]),
    ("paysage", ["Littoral", "Montagne"]),
    ("localite", SECTIONS),
]

DIM_CLE = {
    "I. PHYSICAL AND INFRASTRUCTURAL DIMENSION": "dim1",
    "II. INSTITUTIONAL, TECHNOLOGICAL, AND GOVERNANCE  DIMENSION": "dim2",
    "III.  ENVIRONMENTAL AND ECOLOGICAL DIMENSION": "dim3",
    "IV. ECONOMIC, LIVELIHOODS, AND FOOD SECURITY DIMENSION": "dim4",
    "V. SOCIAL AND COMMUNITY DIMENSION": "dim5",
    "VI. HUMAN DIMENSION": "dim6",
    "VII. CULTURAL, IDENTITY-BASED, AND PSYCHOLOGICAL DIMENSION": "dim7",
}

TEXTES = {
    # ---------------- section 1
    "qr_s1": {"en": "Survey questions, absolute results",
              "fr": "Résultats des questions, effectifs absolus"},
    "qr_s1_note": {
        "en": "Every question attached to this dimension, with the count and "
              "share of its reference answer, and the group and locality at "
              "each end. **The reference answer is the one the indicator "
              "retains** when the question feeds one, that is what makes the "
              "link with the table below traceable; otherwise it is the first "
              "modality, and you can change it.",
        "fr": "Chaque question rattachée à cette dimension, avec l'effectif et "
              "la part de sa réponse de référence, et le groupe comme la "
              "localité à chaque extrémité. **La réponse de référence est "
              "celle que retient l'indicateur** quand la question en alimente "
              "un : c'est ce qui rend le lien avec le tableau du dessous "
              "traçable ; sinon c'est la première modalité, et elle se "
              "change."},
    "qr_sens_note": {
        "en": "**A high percentage is not good news in itself.** The direction "
              "of a variable is known only where the question feeds an "
              "indicator, which carries its scale. Those rows read « best » "
              "and « worst »; the others, marked ○, read « highest » and "
              "« lowest », guessing their direction would produce a table "
              "that looks complete and is wrong half the time.",
        "fr": "**Un pourcentage élevé n'est pas une bonne nouvelle en soi.** "
              "Le sens d'une variable n'est connu que là où la question "
              "alimente un indicateur, qui porte son barème. Ces lignes-là "
              "disent « meilleur » et « pire » ; les autres, marquées ○, "
              "disent « plus haut » et « plus bas », deviner leur sens "
              "produirait un tableau qui a l'air complet et se trompe une fois "
              "sur deux."},
    "qr_pop": {"en": "Population shown", "fr": "Population affichée"},
    "qr_r_tous": {"en": "All respondents", "fr": "Tous les répondants"},
    "qr_r_sexe": {"en": "Sex", "fr": "Sexe"},
    "qr_r_age": {"en": "Age group", "fr": "Classe d'âge"},
    "qr_r_socio": {"en": "Socio-economic group",
                   "fr": "Groupe socio-économique"},
    "qr_r_paysage": {"en": "Landscape", "fr": "Paysage"},
    "qr_r_localite": {"en": "Locality", "fr": "Localité"},
    "qr_valeur": {"en": "Which one", "fr": "Laquelle"},
    "qr_chercher": {"en": "Search a question", "fr": "Rechercher une question"},
    "qr_rien": {"en": "No question matches this search.",
                "fr": "Aucune question ne correspond à cette recherche."},
    "qr_base": {"en": "Base: {n} respondents, {c}",
                "fr": "Base : {n} répondants, {c}"},
    "qr_c_question": {"en": "Question", "fr": "Question"},
    "qr_c_reponse": {"en": "Reference answer", "fr": "Réponse de référence"},
    "qr_c_n": {"en": "Count", "fr": "Effectif"},
    "qr_c_pct": {"en": "Share", "fr": "Part"},
    "qr_c_mg": {"en": "Best group", "fr": "Meilleur groupe"},
    "qr_c_pg": {"en": "Worst group", "fr": "Pire groupe"},
    "qr_c_ml": {"en": "Best locality", "fr": "Meilleure localité"},
    "qr_c_pl": {"en": "Worst locality", "fr": "Pire localité"},
    "qr_c_haut": {"en": "Highest", "fr": "Plus haut"},
    "qr_c_bas": {"en": "Lowest", "fr": "Plus bas"},
    "qr_alimente": {"en": "feeds line {n}", "fr": "alimente la ligne {n}"},

    # ---------------- comparaison visuelle
    "qr_s1b": {"en": "Compare one question across groups and localities",
               "fr": "Comparer une question entre groupes et localités"},
    "qr_quelle_q": {"en": "Question", "fr": "Question"},
    "qr_quelle_m": {"en": "Answer compared", "fr": "Réponse comparée"},
    "qr_comparer": {"en": "Compare by", "fr": "Comparer par"},
    "qr_par_groupe": {"en": "Group", "fr": "Groupe"},
    "qr_par_localite": {"en": "Locality", "fr": "Localité"},
    "qr_bar_note": {
        "en": "Sorted from the highest share. The dotted line is the whole "
              "sample. Green and red mark the two ends only where the "
              "direction of the variable is known.",
        "fr": "Classé de la part la plus élevée. Le trait pointillé est "
              "l'ensemble de l'échantillon. Le vert et le rouge ne marquent "
              "les deux extrémités que là où le sens de la variable est "
              "connu."},

    # ---------------- section 2
    "qr_s2": {"en": "Resilience indicators, weighting and scores",
              "fr": "Indicateurs de résilience, pondération et scores"},
    "qr_s2_note": {
        "en": "What the framework makes of those answers: which question each "
              "indicator is drawn from, the weight it carries in the "
              "dimension, the score it produces, and the two ends. Scores are "
              "the published ones, computed for each of the twenty-two "
              "breakdowns, not recomputed here.",
        "fr": "Ce que le référentiel fait de ces réponses : de quelle question "
              "chaque indicateur est tiré, quelle pondération il porte dans la "
              "dimension, quel score il produit, et les deux extrémités. Les "
              "scores sont ceux publiés, calculés pour chacun des vingt-deux "
              "découpages, non recalculés ici."},
    "qr_c_ind": {"en": "Indicator", "fr": "Indicateur"},
    "qr_c_dim": {"en": "Dimension", "fr": "Dimension"},
    "qr_c_src": {"en": "Source / questions", "fr": "Source / questions"},
    "qr_c_pond": {"en": "Weight", "fr": "Pondération"},
    "qr_c_score": {"en": "Score", "fr": "Score"},
    "qr_src_sat": {"en": "Satellite imagery", "fr": "Imagerie satellitaire"},
    "qr_src_ocb": {"en": "Community organisation census",
                   "fr": "Recensement des organisations de base"},
    "qr_src_reg": {"en": "Register", "fr": "Registre"},
    "qr_combine": {"en": "Combine several filters",
                   "fr": "Combiner plusieurs filtres"},
    "qr_combine_note": {
        "en": "**Scores below are recomputed, not published.** No file holds "
              "the score of « women × mountain × Cat C »: the framework "
              "publishes twenty-two breakdowns, not their crossings. Each "
              "indicator is therefore recalculated on the selected subgroup "
              "and the published scale applied, which is only possible for "
              "the indicators whose definition reproduces exactly from the "
              "individual answers ({k} of them, {p} % of the framework's "
              "weight). The others show no score under a combination.",
        "fr": "**Les scores ci-dessous sont recalculés, non publiés.** Aucun "
              "fichier ne porte le score de « femmes × montagne × Cat C » : le "
              "référentiel publie vingt-deux découpages, pas leurs "
              "croisements. Chaque indicateur est donc recalculé sur le "
              "sous-groupe sélectionné et le barème publié appliqué, ce qui "
              "n'est possible que pour les indicateurs dont la définition se "
              "reproduit exactement à partir des réponses individuelles ({k} "
              "d'entre eux, {p} % du poids du référentiel). Les autres "
              "n'affichent pas de score sous une combinaison."},
    "qr_combine_n": {"en": "Subgroup: {n} respondents ({p} % of the sample)",
                     "fr": "Sous-groupe : {n} répondants ({p} % de "
                           "l'échantillon)"},
    "qr_s2b": {"en": "Compare one indicator across groups and localities",
               "fr": "Comparer un indicateur entre groupes et localités"},
    "qr_quel_i": {"en": "Indicator", "fr": "Indicateur"},
    "qr_bar_note2": {
        "en": "Scores out of 10, published for each breakdown. Sorted from "
              "the highest; green is the best, red the worst, for a score, "
              "the direction is never ambiguous.",
        "fr": "Scores sur 10, publiés pour chaque découpage. Classé du plus "
              "élevé ; le vert est le meilleur, le rouge le pire, pour un "
              "score, le sens n'est jamais ambigu."},
    "qr_aucun_ind": {"en": "No scored indicator in this dimension.",
                     "fr": "Aucun indicateur scoré dans cette dimension."},
    "qr_aucune_q": {"en": "No survey question is attached to this dimension.",
                    "fr": "Aucune question d'enquête n'est rattachée à cette "
                          "dimension."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)

STYLE = """
<style>
  .qr-t   { width:100%; border-collapse:collapse; font-size:12.5px; }
  .qr-t th{ text-align:right; padding:8px 9px; border-bottom:2px solid #e6ecf4;
            font-size:10.5px; letter-spacing:.05em; text-transform:uppercase;
            color:#6b7590; font-weight:700; white-space:nowrap; }
  .qr-t th:first-child, .qr-t td:first-child,
  .qr-t th.g, .qr-t td.g { text-align:left; }
  .qr-t td{ text-align:right; padding:7px 9px; border-bottom:1px solid #f0f4f9;
            font-variant-numeric:tabular-nums; vertical-align:top; }
  .qr-q   { color:#101728; }
  .qr-m   { color:#6b7590; font-size:11.5px; }
  .qr-lien{ display:inline-block; font-size:10.5px; font-weight:700;
            color:#1a6bb0; background:#eaf3fb; border-radius:999px;
            padding:1px 7px; margin-left:6px; white-space:nowrap; }
  .qr-nc  { color:#b6bfcd; font-weight:700; margin-left:5px; }
  .qr-ext { font-size:11.5px; white-space:nowrap; }
  .qr-ext b { font-variant-numeric:tabular-nums; }
  .qr-bar { display:grid; grid-template-columns:minmax(120px,1.3fr) 5fr 74px;
            gap:10px; align-items:center; padding:4px 0; }
  .qr-p   { background:#f1f4f9; border-radius:5px; height:15px;
            overflow:hidden; position:relative; }
  .qr-f   { height:100%; border-radius:5px; }
  .qr-ref { position:absolute; top:-2px; bottom:-2px; width:0;
            border-left:2px dashed #6b7590; }
  .qr-v   { font-size:12px; font-weight:700; text-align:right;
            font-variant-numeric:tabular-nums; }
</style>
"""


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _f(v, dec=1):
    if v is None:
        return "—"
    return f"{v:.{dec}f}".replace(".", ",")


def _norm(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ",
                                      s.decode().lower())).strip()


def _trouver(nom):
    for c in (os.path.join(DATA, nom), os.path.join(APP_DIR, nom)):
        if os.path.exists(c):
            return c
    return None


@st.cache_data(show_spinner=False)
def _bits():
    """L'appartenance de chaque répondant à chaque modalité, en bits.

    POURQUOI CE DÉTOUR PLUTÔT QUE LA SOMME DES EFFECTIFS. Plusieurs questions
    acceptent plusieurs réponses — un foyer peut cocher deux sources d'eau
    améliorées. Additionner les effectifs des modalités retenues compte alors
    ce foyer deux fois, et le tableau affichait « Trichet 123,3 % ». L'union
    des bits le compte une fois, ce qui est la seule définition défendable
    d'une part de ménages.

    Repli sur la somme si le fichier de bits est absent : la page continue de
    fonctionner, avec la réserve écrite à l'écran.
    """
    try:
        import croisement_moteur as CM
        cat = CM.charger()
    except Exception:
        return None
    if not cat:
        return None
    par_q = {_norm(q["question"]): q for q in cat["questions"]}
    return {"cat": cat, "par_q": par_q}


def _compte(refs, col, question=None):
    """Le nombre de répondants de la colonne `col` ayant coché au moins une
    des modalités retenues. Union exacte quand les bits sont là."""
    b = _bits()
    if b and question:
        q = b["par_q"].get(_norm(question))
        grp = b["cat"]["groupes"].get(col if col != "Total" else "Total")
        if q is not None and grp is not None:
            import numpy as np
            u = np.zeros(b["cat"]["n"], dtype=bool)
            trouve = False
            for lab, _n in refs:
                if lab in q["modalites"]:
                    u |= b["cat"]["bits"][q["debut"] + q["modalites"].index(lab)]
                    trouve = True
            if trouve:
                return int((u & grp).sum())
    return sum((n.get(col) or 0) for _lab, n in refs)


@st.cache_data(show_spinner=False)
def _resultats():
    p = _trouver("resultats.json")
    if not p:
        return []
    with open(p, encoding="utf-8") as f:
        r = json.load(f)
    return r["indicateurs"] if isinstance(r, dict) and "indicateurs" in r else r


@st.cache_data(show_spinner=False)
def _par_question():
    """question normalisée -> indicateur qui en est tiré.

    C'est la table de traçabilité : elle porte le SENS de la variable, ses
    modalités de référence, et le numéro de ligne du référentiel.
    """
    out = {}
    for r in _resultats():
        q = _norm(r.get("question"))
        if not q or (r.get("scores_corriges") or {}).get("Total") is None:
            continue
        out.setdefault(q, r)
    return out


def _polarite(ind):
    """+1 si une valeur haute est une bonne nouvelle, −1 sinon, None si on ne
    sait pas. Le sens est LU sur le barème — bornes croissantes ou
    décroissantes — plutôt que sur un champ déclaratif, parce que c'est le
    barème qui décide du score."""
    if ind is None:
        return None
    if ind.get("bareme_inverse"):
        return -1
    s = str(ind.get("sens") or "").lower()
    if "haute" in s and "haut" in s.split("=")[-1]:
        return 1
    if "basse" in s or "inverse" in s:
        return -1
    return 1 if s else None


def _nom_indic(r):
    if i18n.get_lang() == "fr" and r.get("indicateur_fr"):
        return r["indicateur_fr"]
    return r.get("indicateur", "")


def _lib(v):
    cles = {"Homme": "hommes", "Femme": "femmes", "Cat A": "cat_a",
            "Cat B": "cat_b", "Cat C": "cat_c", "<25": "age_25",
            "25-39": "age_25_39", "40-59": "age_40_59", "60+": "age_60",
            "Littoral": "pay_Littoral", "Montagne": "pay_Montagne"}
    return T(cles[v]) if v in cles else v


def _extremes(valeurs, polarite):
    """(haut, bas) → (meilleur, pire) selon le sens. Rend deux couples
    (clé, valeur), ou (None, None) si rien n'est mesurable."""
    dispo = {k: v for k, v in valeurs.items() if v is not None}
    if not dispo:
        return None, None
    haut = max(dispo.items(), key=lambda kv: kv[1])
    bas = min(dispo.items(), key=lambda kv: kv[1])
    if polarite == -1:
        return bas, haut
    return haut, bas


def _cellule(couple, coul):
    if not couple:
        return '<td class="qr-ext">—</td>'
    return (f'<td class="qr-ext" style="color:{coul}">{_e(_lib(couple[0]))} '
            f'<b>{_f(couple[1])} %</b></td>')


# ---------------------------------------------------------------- section 1
def _selecteur_population(cle):
    """Le filtre de population : un registre, puis une valeur. Rend la clé de
    colonne du cache — « Total », « Femme », « Dumont »…"""
    c1, c2 = st.columns([1.6, 1.6])
    with c1:
        reg = st.selectbox(
            T("qr_pop"), [r for r, _v in REGISTRES],
            format_func=lambda r: T("qr_r_" + r), key=f"qr_reg_{cle}")
    vals = dict(REGISTRES)[reg]
    with c2:
        val = st.selectbox(T("qr_valeur"), vals, format_func=_lib,
                           key=f"qr_val_{cle}_{reg}") if vals else None
    return val or "Total", reg


def _tableau_questions(groupes, cible, cherche):
    """Une ligne par question. La modalité de référence est celle de
    l'indicateur quand il y en a un — c'est le lien traçable — sinon la
    première modalité de la question."""
    idx = _par_question()
    ent = [T("qr_c_question"), T("qr_c_reponse"), T("qr_c_n"), T("qr_c_pct"),
           T("qr_c_mg"), T("qr_c_pg"), T("qr_c_ml"), T("qr_c_pl")]
    li = ['<table class="qr-t"><tr>'
          + "".join(f'<th class="{"g" if i < 2 else ""}">{_e(h)}</th>'
                    for i, h in enumerate(ent)) + "</tr>"]
    d = QD._charger()
    base_n = d["base_n"]
    n_lignes = 0
    for module, questions in groupes:
        for t, _lg in questions:
            q = t.get("question") or ""
            if cherche and cherche not in q.lower() \
                    and cherche not in QD.libelle_module(module).lower():
                continue
            ind = idx.get(_norm(q))
            rows = t.get("rows") or []
            if not rows:
                continue
            # La modalité de référence : celle que l'indicateur retient, sinon
            # la première. Plusieurs modalités retenues sont cumulées, comme
            # le fait le référentiel.
            refs = []
            if ind:
                voulues = {_norm(m) for m in
                           (ind.get("modalites") or "").split(" + ") if m.strip()}
                refs = [r for r in rows if _norm(r[0]) in voulues]
            if not refs:
                refs = rows[:1]
            pol = _polarite(ind)

            def part(col):
                b = base_n.get(col) or 0
                if not b:
                    return None
                return 100.0 * _compte(refs, col, q) / b

            n_ref = _compte(refs, cible, q)
            pct = part(cible)
            mg, pg = _extremes({g: part(g) for g in GROUPES}, pol)
            ml, pl = _extremes({s: part(s) for s in SECTIONS}, pol)
            lien = (f'<span class="qr-lien">'
                    f'{_e(T("qr_alimente", n=ind["ligne"]))}</span>'
                    if ind else '<span class="qr-nc" title="sens inconnu">○</span>')
            li.append(
                f'<tr><td class="g"><span class="qr-q">{_e(q)}</span>{lien}'
                f'<div class="qr-m">{_e(QD.libelle_module(module))}</div></td>'
                f'<td class="g qr-m">{_e(" + ".join(r[0] for r in refs))}</td>'
                f'<td style="font-weight:600">{n_ref}</td>'
                f'<td style="font-weight:700">{_f(pct)} %</td>'
                + _cellule(mg, VERT if pol else ENCRE2)
                + _cellule(pg, ROUGE if pol else ENCRE2)
                + _cellule(ml, VERT if pol else ENCRE2)
                + _cellule(pl, ROUGE if pol else ENCRE2) + '</tr>')
            n_lignes += 1
    return ("".join(li) + "</table>") if n_lignes else None


def _barres(valeurs, reference, polarite, unite="%", dec=1):
    """Barres horizontales triées, avec le repère de l'ensemble en pointillé."""
    dispo = [(k, v) for k, v in valeurs.items() if v is not None]
    if not dispo:
        return ""
    dispo.sort(key=lambda kv: -kv[1])
    vmax = max(max(v for _k, v in dispo), reference or 0) or 1
    meilleur = dispo[0][0] if polarite != -1 else dispo[-1][0]
    pire = dispo[-1][0] if polarite != -1 else dispo[0][0]
    out = []
    for k, v in dispo:
        c = (VERT if (polarite and k == meilleur)
             else ROUGE if (polarite and k == pire) else BLEU)
        ref = (f'<div class="qr-ref" style="left:{100 * reference / vmax:.1f}%">'
               f'</div>') if reference else ''
        out.append(
            f'<div class="qr-bar"><div style="font-size:12px;color:{ENCRE}">'
            f'{_e(_lib(k))}</div>'
            f'<div class="qr-p"><div class="qr-f" style="width:'
            f'{100 * v / vmax:.1f}%;background:{c}"></div>{ref}</div>'
            f'<div class="qr-v" style="color:{c}">{_f(v, dec)}{unite}</div>'
            f'</div>')
    return "".join(out)


def _bloc_comparaison_question(groupes):
    """Le graphique en barres d'une question, par groupe ou par localité."""
    d = QD._charger()
    base_n = d["base_n"]
    paires = [(t, m) for m, qs in groupes for t, _l in qs if t.get("rows")]
    if not paires:
        return
    libs = [f'{QD.libelle_module(m)} · {t["question"]}'
            for m, qs in groupes for t, _l in qs if t.get("rows")]
    st.markdown(f'<div class="titre-bloc">{T("qr_s1b")}</div>',
                unsafe_allow_html=True)
    c1, c2, c3 = st.columns([3, 2, 1.6])
    with c1:
        choix = st.selectbox(T("qr_quelle_q"), range(len(libs)),
                             format_func=lambda i: libs[i], key="qr_bq")
    t, module = paires[choix]
    rows = t["rows"]
    ind = _par_question().get(_norm(t.get("question")))
    # `ind` peut être absent : la question n'alimente aucun indicateur. Le
    # garde doit précéder l'accès, sinon l'expression lève avant d'être
    # filtrée — c'est ce qui faisait tomber deux dimensions sur six.
    voulues = set()
    if ind:
        voulues = {_norm(m) for m in (ind.get("modalites") or "").split(" + ")
                   if m.strip()}
    defaut = [r[0] for r in rows if _norm(r[0]) in voulues] or [rows[0][0]]
    with c2:
        mods = st.multiselect(T("qr_quelle_m"), [r[0] for r in rows],
                              default=defaut, key=f"qr_bm_{choix}")
    with c3:
        par = st.radio(T("qr_comparer"), ["groupe", "localite"],
                       format_func=lambda k: T("qr_par_" + k),
                       key="qr_bpar", horizontal=True)
    if not mods:
        return
    retenues = [r for r in rows if r[0] in mods]
    cles = GROUPES if par == "groupe" else SECTIONS

    def part(col):
        b = base_n.get(col) or 0
        return (100.0 * _compte(retenues, col, t.get("question")) / b) \
            if b else None

    st.markdown(_barres({k: part(k) for k in cles}, part("Total"),
                        _polarite(ind)), unsafe_allow_html=True)
    st.caption(T("qr_bar_note"))


# ---------------------------------------------------------------- section 2
def _source_de(r):
    s = r.get("source")
    if s == "satellite":
        return T("qr_src_sat")
    if s == "OCB":
        return T("qr_src_ocb")
    q = (r.get("question") or "").strip()
    return q or T("qr_src_reg")


def _tableau_indicateurs(lignes, cible, scores_recalcules=None):
    ent = [T("qr_c_ind"), T("qr_c_dim"), T("qr_c_src"), T("qr_c_pond"),
           T("qr_c_score"), T("qr_c_mg"), T("qr_c_pg"), T("qr_c_ml"),
           T("qr_c_pl")]
    li = ['<table class="qr-t"><tr>'
          + "".join(f'<th class="{"g" if i < 3 else ""}">{_e(h)}</th>'
                    for i, h in enumerate(ent)) + "</tr>"]
    for r in sorted(lignes, key=lambda x: x["ligne"]):
        sc = (r.get("scores_corriges") or {})
        if scores_recalcules is not None:
            val = scores_recalcules.get(r["ligne"])
        else:
            val = sc.get(cible)
        mg, pg = _extremes({g: sc.get(g) for g in GROUPES}, 1)
        ml, pl = _extremes({s: sc.get(s) for s in SECTIONS}, 1)
        coul = ("#8a93a5" if val is None else "#b4451f" if val <= 3
                else "#c98a2e" if val <= 6 else "#2a6b3f")
        li.append(
            f'<tr><td class="g"><span class="qr-q">L{r["ligne"]} · '
            f'{_e(_nom_indic(r))}</span></td>'
            f'<td class="g qr-m">{_e(T(DIM_CLE.get(r["dimension"], "")))}</td>'
            f'<td class="g qr-m">{_e(_source_de(r))}</td>'
            f'<td style="color:{ENCRE3}">{_f(r.get("ponderation"), 2)}</td>'
            f'<td style="font-weight:700;font-size:14px;color:{coul}">'
            f'{_f(val, 1)}</td>'
            + _cellule_score(mg, VERT) + _cellule_score(pg, ROUGE)
            + _cellule_score(ml, VERT) + _cellule_score(pl, ROUGE) + '</tr>')
    return "".join(li) + "</table>"


def _cellule_score(couple, coul):
    if not couple:
        return '<td class="qr-ext">—</td>'
    return (f'<td class="qr-ext" style="color:{coul}">{_e(_lib(couple[0]))} '
            f'<b>{_f(couple[1], 1)}</b></td>')


def _scores_combines(lignes, valeurs):
    """Le cas explicitement signalé : plusieurs filtres à la fois.

    Aucun fichier ne porte le score de « femmes × montagne × Cat C ». On le
    recalcule donc avec le moteur de croisement, qui n'accepte que les
    indicateurs dont la définition se reproduit exactement — les autres
    restent vides plutôt que d'afficher une approximation muette.
    """
    try:
        import croisement_moteur as CM
    except Exception:
        return None, None, None
    cat = CM.charger()
    if not cat:
        return None, None, None
    clauses = [{"type": "groupe", "valeurs": [v]} for v in valeurs]
    masque, _ = CM.evaluer(cat, clauses, "ET")
    profil = {p["ligne"]: p["score"] for p in CM.profil(cat, masque)}
    return {r["ligne"]: profil.get(r["ligne"]) for r in lignes}, \
        int(masque.sum()), cat


# -------------------------------------------------------------------- rendu
def render(cle_dim, dimension):
    """Les deux sections, en tête de la page de dimension."""
    st.markdown(STYLE, unsafe_allow_html=True)
    groupes = QD.questions_de(cle_dim)
    res = _resultats()
    lignes = [r for r in res if r["dimension"] == dimension
              and (r.get("scores_corriges") or {}).get("Total") is not None]

    # ------------------------------------------------------- 1 · questions
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("qr_s1")}</div>',
                    unsafe_allow_html=True)
        st.markdown(T("qr_s1_note"))
        st.caption(T("qr_sens_note"))
        if not groupes:
            st.info(T("qr_aucune_q"))
        else:
            cible, _reg = _selecteur_population("q")
            d = QD._charger()
            st.caption(T("qr_base", n=(d["base_n"].get(cible) or 0),
                         c=_lib(cible) if cible != "Total"
                         else T("qr_r_tous")))
            cherche = (st.text_input(T("qr_chercher"), key=f"qr_ch_{cle_dim}",
                                     placeholder="…") or "").strip().lower()
            html = _tableau_questions(groupes, cible, cherche)
            if html:
                st.markdown(html, unsafe_allow_html=True)
            else:
                st.info(T("qr_rien"))

    # -------------------------------------------- 1b · comparaison visuelle
    if groupes:
        with st.container(border=True):
            _bloc_comparaison_question(groupes)

    # ---------------------------------------------------- 2 · indicateurs
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc vert">{T("qr_s2")}</div>',
                    unsafe_allow_html=True)
        st.markdown(T("qr_s2_note"))
        if not lignes:
            st.info(T("qr_aucun_ind"))
            return

        combine = st.toggle(T("qr_combine"), key=f"qr_comb_{cle_dim}")
        recalcules = None
        if combine:
            # Plusieurs registres à la fois : une valeur par registre au plus,
            # ce qui interdit les combinaisons vides comme « Homme ET Femme ».
            cols = st.columns(5)
            choisies = []
            for col, (reg, vals) in zip(cols, REGISTRES[1:]):
                with col:
                    v = st.selectbox(
                        T("qr_r_" + reg), ["—"] + vals, format_func=_lib,
                        key=f"qr_cb_{cle_dim}_{reg}")
                    if v != "—":
                        choisies.append(v)
            if choisies:
                recalcules, n_sg, cat = _scores_combines(lignes, choisies)
                if cat:
                    c = __import__("croisement_moteur").couverture(cat)
                    st.warning(T("qr_combine_note",
                                 k=len(cat["indicateurs"]),
                                 p=_f(100 * c["global"], 0)))
                    st.caption(T("qr_combine_n", n=n_sg,
                                 p=_f(100 * n_sg / cat["n"])))
            cible = "Total"
        else:
            cible, _r = _selecteur_population("i")

        st.markdown(_tableau_indicateurs(lignes, cible, recalcules),
                    unsafe_allow_html=True)

    # ------------------------------------------- 2b · comparaison indicateur
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("qr_s2b")}</div>',
                    unsafe_allow_html=True)
        c1, c2 = st.columns([3, 1.6])
        with c1:
            k = st.selectbox(T("qr_quel_i"), range(len(lignes)),
                             format_func=lambda i: f'L{lignes[i]["ligne"]} · '
                             f'{_nom_indic(lignes[i])}',
                             key=f"qr_bi_{cle_dim}")
        with c2:
            par = st.radio(T("qr_comparer"), ["groupe", "localite"],
                           format_func=lambda x: T("qr_par_" + x),
                           key=f"qr_bp_{cle_dim}", horizontal=True)
        sc = lignes[k].get("scores_corriges") or {}
        cles = GROUPES if par == "groupe" else SECTIONS
        st.markdown(_barres({c: sc.get(c) for c in cles}, sc.get("Total"), 1,
                            unite="", dec=1), unsafe_allow_html=True)
        st.caption(T("qr_bar_note2"))
