"""Note aux bailleurs — six constats, huit réponses, ce qu'elles déplacent.

À QUOI SERT CETTE PAGE

À être lue par quelqu'un qui finance et qui n'ouvrira pas les autres onglets.
Elle doit tenir la promesse la plus difficile d'un tableau de bord : dire ce
qui ne va pas sans noyer, et dire quoi faire sans promettre.

TROIS RÈGLES, ÉCRITES ICI PARCE QU'ELLES SE VOIENT À L'ÉCRAN

  1. AUCUN CONSTAT N'EST CHOISI À LA MAIN. Les six constats sont, pour chacune
     des six dimensions mesurées, l'indicateur qui coûte le plus à l'indice
     global : pondération × (10 − score). Un constat par dimension, parce que
     le classement brut donnait quatre constats sur six dans la même dimension
     et qu'une note qui ne parle que d'eau et d'électricité laisse croire que
     le reste va bien. La règle est affichée au-dessus des cartes ; si les
     données changent, les constats changent.

  2. AUCUN CHIFFRE D'IMPACT N'EST POSÉ. Les effets attendus viennent du modèle
     causal — le même que celui des boucles de rétroaction et des fiches
     d'intervention — et le portefeuille complet est simulé D'UN SEUL TENANT,
     pas en additionnant les fiches. Deux fiches qui poussent le même
     indicateur ne le poussent qu'une fois, et le portefeuille déplace alors
     moins que la somme de ses parties. Sur le graphe actuel, les deux valeurs
     coïncident — les huit leviers atteignent des indicateurs disjoints — et
     la page le dit en toutes lettres plutôt que de laisser croire à une
     addition faite à la main. Elle changera de phrase toute seule le jour où
     un levier sera ajouté au graphe.

  3. CE QUE LE MODÈLE NE COUVRE PAS EST DIT AUSSI. La part de la pondération
     que la propagation n'atteint pas, les constats qu'aucune fiche ne traite,
     l'écart entre le gain simulé et les points qui manquent à l'indice : ces
     trois chiffres sont calculés et affichés. Une note aux bailleurs qui ne
     montre que ce qu'elle sait faire n'est pas une note, c'est une plaquette.
"""

import json
import os

import streamlit as st

import boucles_moteur as M
import i18n
import interventions_page as IP
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"
VERT, ROUGE, AMBRE, BLEU, GRIS = ("#1a8a4f", "#c33a24", "#d1730c",
                                  "#2a78d6", "#9aa4b5")

SECTIONS = ["Anse à Drick", "Barbois", "Dumont", "Débouchette", "Mouline",
            "Quentin", "Beaulieu", "Blactote", "Dalmette", "Trichet"]
GROUPES = ["Homme", "Femme", "Cat A", "Cat B", "Cat C",
           "<25", "25-39", "40-59", "60+", "Littoral", "Montagne"]
DIMS = ["dim1", "dim2", "dim3", "dim4", "dim5", "dim6"]

TEXTES = {
    "nb_titre": {"en": "Donor briefing", "fr": "Note aux bailleurs"},
    "nb_sous_titre": {
        "en": "Six findings, eight responses, and what they move",
        "fr": "Six constats, huit réponses, et ce qu'elles déplacent"},
    "nb_intro": {
        "en": "Everything on this page is computed — the findings, the "
              "figures, the ranking of the responses and their expected "
              "effect. Nothing is written in advance: change the survey or "
              "the causal model and this page changes with them. What the "
              "model does not cover is stated too, at the end.",
        "fr": "Tout ce qui figure sur cette page est calculé — les constats, "
              "les chiffres, le classement des réponses et leur effet "
              "attendu. Rien n'est écrit à l'avance : changez l'enquête ou le "
              "modèle causal, la page change avec eux. Ce que le modèle ne "
              "couvre pas est dit également, en fin de page."},

    # ---------------- les quatre chiffres
    "nb_k1": {"en": "Households surveyed", "fr": "Ménages enquêtés"},
    "nb_k1_x": {"en": "{s} communal sections, two departments",
                "fr": "{s} sections communales, deux départements"},
    "nb_k2": {"en": "Overall resilience index", "fr": "Indice global de résilience"},
    "nb_k2_x": {"en": "weighted mean of the {n} scored indicators",
                "fr": "moyenne pondérée des {n} indicateurs scorés"},
    "nb_k3": {"en": "Indicators at 0 or 1 out of 10",
              "fr": "Indicateurs à 0 ou 1 sur 10"},
    "nb_k3_x": {"en": "{p} % of the framework's weight",
                "fr": "{p} % du poids du référentiel"},
    "nb_k4": {"en": "Modelled effect of the full portfolio",
              "fr": "Effet modélisé du portefeuille complet"},
    "nb_k4_x": {"en": "eight sheets simulated together",
                "fr": "huit fiches simulées ensemble"},

    # ---------------- constats
    "nb_s1": {"en": "1 · What the survey establishes",
              "fr": "1 · Ce que l'enquête établit"},
    "nb_regle": {
        "en": "**One finding per dimension, and it is not chosen by hand:** "
              "for each of the six measured dimensions, the indicator that "
              "costs the index the most — its weight multiplied by the points "
              "it lacks out of ten. The raw ranking put four of the six "
              "findings in the same dimension, which would have suggested "
              "everything else was fine.",
        "fr": "**Un constat par dimension, et il n'est pas choisi à la main :** "
              "pour chacune des six dimensions mesurées, l'indicateur qui "
              "coûte le plus à l'indice — sa pondération multipliée par les "
              "points qui lui manquent sur dix. Le classement brut plaçait "
              "quatre constats sur six dans la même dimension, ce qui aurait "
              "laissé croire que tout le reste allait bien."},
    "nb_mesure": {"en": "Measured", "fr": "Valeur mesurée"},
    "nb_reste": {"en": "Not covered", "fr": "Part non couverte"},
    "nb_score": {"en": "Score", "fr": "Score"},
    "nb_poids": {"en": "Weight", "fr": "Pondération"},
    # LES INTITULÉS SONT COURTS PARCE QUE LA PLACE EST COMPTÉE : quatre
    # chiffres dans une colonne sur deux, et « part de l'écart total » à lui
    # seul passait la rangée à la ligne.
    "nb_part": {"en": "Share of shortfall", "fr": "Part de l'écart"},
    "nb_touche": {"en": "Hardest hit", "fr": "Le plus touché"},
    "nb_localite": {"en": "Locality", "fr": "Localité"},
    "nb_groupe": {"en": "Group", "fr": "Groupe"},
    "nb_base": {"en": "{n} responses", "fr": "{n} réponses"},
    "nb_dim_score": {"en": "dimension at {s} / 10", "fr": "dimension à {s} / 10"},
    "nb_autres": {"en": "The twelve heaviest shortfalls, all dimensions",
                  "fr": "Les douze écarts les plus lourds, toutes dimensions"},
    "nb_c_ind": {"en": "Indicator", "fr": "Indicateur"},
    "nb_c_dim": {"en": "Dimension", "fr": "Dimension"},
    "nb_c_val": {"en": "Value", "fr": "Valeur"},
    "nb_c_sc": {"en": "Score", "fr": "Score"},
    "nb_c_p": {"en": "Weight", "fr": "Poids"},
    "nb_c_part": {"en": "Share of shortfall", "fr": "Part de l'écart"},

    # ---------------- réponses
    "nb_s2": {"en": "2 · What is proposed",
              "fr": "2 · Ce que nous proposons"},
    "nb_s2_note": {
        "en": "Eight sheets, ranked by the effect the causal model gives "
              "them on the overall index. Each acts on one lever, raising it "
              "by a set number of points, and the model propagates the "
              "consequence through the chain. **The ranking is not a "
              "priority order:** feasibility and horizon are shown beside "
              "each effect, and section 4 draws the consequence.",
        "fr": "Huit fiches, classées par l'effet que le modèle causal leur "
              "donne sur l'indice global. Chacune agit sur un levier, qu'elle "
              "relève d'un nombre fixé de points, et le modèle propage la "
              "conséquence dans la chaîne. **Le classement n'est pas un ordre "
              "de priorité :** la faisabilité et l'horizon sont affichés à "
              "côté de chaque effet, et la section 4 en tire la conséquence."},
    "nb_effet": {"en": "Effect on the index", "fr": "Effet sur l'indice"},
    "nb_levier": {"en": "Lever: {a} → {b} / 10", "fr": "Levier : {a} → {b} / 10"},
    "nb_horizon": {"en": "Horizon", "fr": "Horizon"},
    "nb_fais": {"en": "Feasibility", "fr": "Faisabilité"},
    "nb_acteurs": {"en": "Actors", "fr": "Acteurs"},
    "nb_repond": {"en": "Answers finding no. {n}", "fr": "Répond au constat n° {n}"},
    "nb_repond_dim": {"en": "Same dimension as finding no. {n}, different problem",
                      "fr": "Même dimension que le constat n° {n}, autre problème"},
    "nb_repond_non": {"en": "Outside the six findings",
                      "fr": "Hors des six constats"},

    # ---------------- portefeuille
    "nb_s3": {"en": "3 · What the full portfolio moves",
              "fr": "3 · Ce que le portefeuille complet déplace"},
    "nb_avant": {"en": "Index today", "fr": "Indice aujourd'hui"},
    "nb_apres": {"en": "Index after the eight sheets",
                 "fr": "Indice après les huit fiches"},
    "nb_gain": {"en": "Modelled gain", "fr": "Gain modélisé"},
    "nb_somme": {
        "en": "The eight sheets taken together move the index by {c} points, "
              "where their isolated effects add up to {s}. The difference is "
              "not an error: several sheets push the same indicators, and the "
              "model counts that overlap once.",
        "fr": "Les huit fiches prises ensemble déplacent l'indice de {c} "
              "points, là où leurs effets isolés totalisent {s}. L'écart "
              "n'est pas une erreur : plusieurs fiches poussent les mêmes "
              "indicateurs, et le modèle ne compte ce recouvrement qu'une "
              "fois."},
    "nb_somme_egal": {
        "en": "The eight sheets taken together move the index by {c} points, "
              "which is exactly the sum of their isolated effects. That "
              "equality is checked, not assumed: it means the model finds no "
              "overlap between them — each pushes indicators the others do "
              "not reach. Were two sheets to act on the same indicator, the "
              "portfolio would move less than their sum, and this line would "
              "say so.",
        "fr": "Les huit fiches prises ensemble déplacent l'indice de {c} "
              "points, soit exactement la somme de leurs effets isolés. "
              "L'égalité est vérifiée, non supposée : elle signifie que le "
              "modèle ne trouve aucun recouvrement entre elles — chacune "
              "pousse des indicateurs que les autres n'atteignent pas. Si "
              "deux fiches agissaient sur le même indicateur, le portefeuille "
              "déplacerait moins que leur somme, et cette ligne le dirait."},
    "nb_orphelin": {
        "en": "{n} · **{ind}** — {dim}, scored {s} out of 10, {p} % of the "
              "total shortfall on its own.",
        "fr": "{n} · **{ind}** — {dim}, noté {s} sur 10, {p} % de l'écart "
              "total à lui seul."},
    "nb_manque": {
        "en": "**The honest proportion:** {g} points against the {m} points "
              "the index lacks to reach ten — {p} % of the way. The rest sits "
              "in indicators no household-level project moves: protected-area "
              "coverage at 0 %, forest cover change, marine pollution. Those "
              "call for public policy and enforcement, not a programme.",
        "fr": "**La proportion honnête :** {g} points contre les {m} points "
              "qui manquent à l'indice pour atteindre dix — soit {p} % du "
              "chemin. Le reste est dans des indicateurs qu'aucun projet "
              "conduit auprès des ménages ne déplace : couverture des aires "
              "protégées à 0 %, évolution du couvert forestier, pollution "
              "marine. Ceux-là relèvent de la politique publique et du "
              "contrôle, pas d'un programme."},
    "nb_couvert": {
        "en": "The propagation reaches indicators carrying {p} % of the "
              "framework's weight. The remaining {q} % is out of the model's "
              "reach — not out of reach in the field.",
        "fr": "La propagation atteint des indicateurs portant {p} % du poids "
              "du référentiel. Les {q} % restants sont hors de portée du "
              "modèle — pas hors de portée sur le terrain."},
    "nb_sans": {"en": "Findings no sheet addresses",
                "fr": "Les constats qu'aucune fiche ne traite"},
    "nb_sans_non": {"en": "Every finding has at least one sheet acting in its "
                          "dimension.",
                    "fr": "Chaque constat a au moins une fiche agissant dans "
                          "sa dimension."},

    # ---------------- séquencement
    "nb_s4": {"en": "4 · If the budget covers only part of it",
              "fr": "4 · Si le budget n'en couvre qu'une partie"},
    "nb_s4_note": {
        "en": "The first batch is not a choice either: it is every sheet that "
              "is both **highly feasible** and **short-horizon**. The second "
              "batch is the rest. Both figures are simulated as batches, not "
              "added up.",
        "fr": "Le premier lot n'est pas non plus un choix : ce sont toutes les "
              "fiches à la fois **de faisabilité haute** et **d'horizon "
              "court**. Le second lot est le reste. Les deux chiffres sont "
              "simulés par lot, non additionnés."},
    "nb_lot1": {"en": "First batch — feasible and short-term",
                "fr": "Premier lot — faisable et à court terme"},
    "nb_lot2": {"en": "Second batch — the rest", "fr": "Second lot — le reste"},
    "nb_lot_n": {"en": "{n} sheets", "fr": "{n} fiches"},
    "nb_lot_part": {
        "en": "{n} of the {t} sheets carry {p} % of the portfolio's modelled "
              "gain. This is the sentence to hold on to if the decision is "
              "about sequencing rather than scope.",
        "fr": "{n} des {t} fiches portent {p} % du gain modélisé du "
              "portefeuille. C'est la phrase à retenir si la décision porte "
              "sur un séquencement plutôt que sur un périmètre."},

    # ---------------- réserves
    "nb_s5": {"en": "5 · What this note does not promise",
              "fr": "5 · Ce que cette note ne promet pas"},
    "nb_r1": {
        "en": "**A simulated effect is not an evaluated impact.** The figures "
              "come from a causal graph calibrated on this survey, not from a "
              "before/after measurement. They rank the sheets against each "
              "other; they do not forecast a result.",
        "fr": "**Un effet simulé n'est pas un impact évalué.** Les chiffres "
              "viennent d'un graphe causal calibré sur cette enquête, non "
              "d'une mesure avant/après. Ils classent les fiches les unes par "
              "rapport aux autres ; ils ne prédisent pas un résultat."},
    "nb_r2": {
        "en": "**The target set for each lever is an assumption, and it is "
              "written down.** A sheet raises its lever by a fixed number of "
              "points; whether a programme achieves that is a question of "
              "budget and delivery, not of model.",
        "fr": "**La cible fixée à chaque levier est une hypothèse, et elle est "
              "écrite.** Une fiche relève son levier d'un nombre de points "
              "fixé ; qu'un programme y parvienne est affaire de budget et de "
              "mise en œuvre, pas de modèle."},
    "nb_r3": {
        "en": "**The environmental dimension is measured by satellite**, at "
              "the scale of the section and not of the household. It "
              "responds to land-use change over years, and no sheet in this "
              "portfolio moves it within its stated horizon.",
        "fr": "**La dimension environnementale est mesurée par satellite**, à "
              "l'échelle de la section et non du ménage. Elle répond à des "
              "changements d'usage des sols sur plusieurs années, et aucune "
              "fiche de ce portefeuille ne la déplace dans l'horizon "
              "annoncé."},
    "nb_r4": {
        "en": "**The seventh dimension of the framework — cultural, "
              "identity-based and psychological — has no scored indicator.** "
              "It is absent from every figure on this page. That absence is a "
              "gap in the instrument, not a finding about the territory.",
        "fr": "**La septième dimension du référentiel — culturelle, "
              "identitaire et psychologique — n'a aucun indicateur scoré.** "
              "Elle est absente de tous les chiffres de cette page. Cette "
              "absence est une lacune de l'instrument, pas un constat sur le "
              "territoire."},
    "nb_r5": {
        "en": "**Horizons are labels, not commitments.** Short, medium and "
              "long term qualify the nature of the change sought — a water "
              "point, a committee, a land title — not a delivery schedule.",
        "fr": "**Les horizons sont des qualifications, pas des engagements.** "
              "Court, moyen et long terme disent la nature du changement "
              "visé — un point d'eau, un comité, un titre foncier — non un "
              "calendrier de livraison."},
    "nb_ou": {
        "en": "The detailed sheets — activities, actors, calendar, risks — are "
              "in *Intervention Profiles*. The causal chains behind the "
              "figures are in *Feedback Loops*. The survey results, indicator "
              "by indicator, are in *Results Analysis*.",
        "fr": "Les fiches détaillées — activités, acteurs, calendrier, "
              "risques — sont dans *Fiches d'intervention*. Les chaînes "
              "causales derrière les chiffres sont dans *Boucles de "
              "rétroaction*. Les résultats de l'enquête, indicateur par "
              "indicateur, sont dans *Analyse des résultats*."},
    "nb_absent": {"en": "Data files missing.", "fr": "Fichiers de données absents."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)

STYLE = """
<style>
  .nb-k    { border:1px solid #e6ecf4; border-radius:14px; padding:14px 16px;
             background:#fff; height:100%; }
  .nb-kl   { font-size:10.5px; letter-spacing:.09em; text-transform:uppercase;
             font-weight:700; color:#8a93a5; line-height:1.35; }
  .nb-kv   { font-size:32px; font-weight:700; letter-spacing:-.03em;
             line-height:1.1; margin-top:4px; font-variant-numeric:tabular-nums; }
  .nb-kx   { font-size:12px; color:#6b7590; margin-top:3px; line-height:1.45; }
  .nb-num  { display:inline-flex; align-items:center; justify-content:center;
             width:26px; height:26px; border-radius:999px; background:#101728;
             color:#fff; font-size:13px; font-weight:700; }
  .nb-dim  { font-size:10.5px; letter-spacing:.09em; text-transform:uppercase;
             font-weight:700; color:#8a93a5; }
  .nb-t    { font-size:17px; font-weight:700; color:#101728;
             letter-spacing:-.015em; margin:2px 0 0; line-height:1.3; }
  .nb-fig  { display:flex; gap:17px; flex-wrap:wrap; align-items:flex-end;
             margin:10px 0 2px; }
  .nb-f    { }
  .nb-fv   { font-size:27px; font-weight:700; letter-spacing:-.03em;
             line-height:1; font-variant-numeric:tabular-nums; }
  .nb-fl   { font-size:9.5px; letter-spacing:.04em; text-transform:uppercase;
             font-weight:700; color:#8a93a5; margin-top:4px;
             white-space:nowrap; }
  .nb-jauge{ height:8px; background:#eef2f7; border-radius:4px; position:relative;
             margin:10px 0 2px; }
  .nb-jr   { position:absolute; left:0; top:0; height:100%; border-radius:4px; }
  .nb-p    { font-size:13.5px; color:#3c4761; line-height:1.65; margin:8px 0 0; }
  .nb-chip { display:inline-block; font-size:11.5px; font-weight:700;
             border-radius:999px; padding:3px 11px; margin:0 6px 6px 0; }
  .nb-tou  { font-size:12.5px; color:#3c4761; margin-top:8px;
             border-top:1px solid #eef2f7; padding-top:8px; }
  .nb-tou b{ color:#101728; }
  .nb-t2   { width:100%; border-collapse:collapse; font-size:13px; }
  .nb-t2 th{ text-align:right; padding:7px 9px; border-bottom:2px solid #e6ecf4;
             font-size:10.5px; letter-spacing:.05em; text-transform:uppercase;
             color:#6b7590; font-weight:700; }
  .nb-t2 th:first-child, .nb-t2 td:first-child { text-align:left; }
  .nb-t2 td{ text-align:right; padding:6px 9px; border-bottom:1px solid #f0f4f9;
             font-variant-numeric:tabular-nums; }
  .nb-bar  { display:grid; grid-template-columns:minmax(150px,2fr) 4fr 74px;
             gap:12px; align-items:center; padding:7px 0;
             border-bottom:1px solid #f0f4f9; }
  .nb-bp   { height:12px; background:#f4f7fb; border-radius:4px; position:relative; }
  .nb-bf   { position:absolute; left:0; top:0; height:100%; border-radius:4px; }
  .nb-r li { margin-bottom:8px; }
</style>
"""


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _gras(t):
    """`**gras**` en `<b>` — le markdown n'est pas interprété dans du HTML
    injecté, et une note aux bailleurs pleine d'astérisques est illisible."""
    out, morceaux = [], _e(t).split("**")
    for i, m in enumerate(morceaux):
        out.append(f"<b>{m}</b>" if i % 2 else m)
    return "".join(out)


def _f(v, dec=2, signe=False):
    if v is None:
        return "—"
    s = f"{v:+.{dec}f}" if signe else f"{v:.{dec}f}"
    return s.replace(".", ",") if i18n.get_lang() == "fr" else s


def _pc(v, dec=1):
    return _f(v, dec) + " %"


def _lang_fr():
    return i18n.get_lang() == "fr"


@st.cache_data(show_spinner=False)
def _n_repondants(defaut):
    """Le nombre de ménages enquêtés — 1 211, et pas le plus grand effectif.

    LE PIÈGE ÉVITÉ ICI : prendre le maximum des bases du référentiel donnait
    2 700, parce que certains indicateurs se comptent en personnes du foyer et
    non en foyers. Le chiffre juste est celui de l'index des croisements, qui
    est l'effectif de l'enquête elle-même. Le fichier absent, on retombe sur la
    base la plus fréquente du référentiel, qui en approche.
    """
    p = os.path.join(DATA, "croisement_index.json")
    if os.path.exists(p):
        try:
            with open(p, encoding="utf-8") as f:
                n = json.load(f).get("n")
            if n:
                return int(n)
        except Exception:
            pass
    return int(defaut or 0)


@st.cache_data(show_spinner=False)
def _tout():
    """Le graphe, l'enquête, les boucles et les fiches — une seule fois.

    Le calcul complet (propagation de huit scénarios, plus deux scénarios de
    lot) prend une fraction de seconde, mais il est refait à chaque clic de
    filtre si on ne le met pas en cache, et cette page n'a aucun filtre.
    """
    graphe, par_ligne = IP._charger()
    if not par_ligne:
        return None
    lst = M.boucles(graphe)
    fiches = IP.calculer(graphe, par_ligne, lst)

    def combine(ids):
        var = {f["levier"]: float(f["cible"]) for f in fiches if f["id"] in ids}
        if not var:
            return {"delta": 0.0, "part_couverte": 0.0}
        eff = M.propager(graphe, var)
        return M.effet_indice(graphe, eff, var, par_ligne)

    tous = [f["id"] for f in fiches]
    lot1 = [f["id"] for f in fiches
            if f["faisabilite"] == "haute" and f["horizon"] == "court"]
    lot2 = [i for i in tous if i not in lot1]
    return {
        "par_ligne": par_ligne,
        "fiches": fiches,
        "dims": IP.scores_dimensions(par_ligne),
        "indice": IP.moyenne_ponderee(par_ligne),
        "portefeuille": combine(tous),
        "lot1": {"ids": lot1, "eff": combine(lot1)},
        "lot2": {"ids": lot2, "eff": combine(lot2)},
    }


# ----------------------------------------------------------------- constats
def _polarite(r):
    """+1 si une valeur haute vaut un score haut, −1 sinon.

    LU SUR LES DONNÉES, PAS DÉCLARÉ. Le champ `sens` du référentiel dit
    « valeur haute = score haut » y compris pour l'insécurité alimentaire, où
    c'est l'inverse — le barème y est inversé par un autre champ. La
    covariance entre les valeurs et les scores des vingt-deux découpages
    tranche sans ambiguïté et sans dépendre d'aucune déclaration.
    """
    v, s = r.get("valeurs") or {}, r.get("scores_corriges") or {}
    ks = [k for k in v if k in s and isinstance(v[k], (int, float))
          and s[k] is not None]
    if len(ks) < 3:
        return 1
    mv = sum(v[k] for k in ks) / len(ks)
    ms = sum(s[k] for k in ks) / len(ks)
    cov = sum((v[k] - mv) * (s[k] - ms) for k in ks)
    return -1 if cov < 0 else 1


def _pire(r, clefs, pol):
    """La modalité la plus mal placée : d'abord le score, puis la valeur.

    Le score départage mal — sept modalités à 0 sur dix se valent — d'où le
    second critère, la valeur brute lue dans le bon sens. Si toutes les
    valeurs sont identiques (les indicateurs satellitaires ne varient pas
    d'un groupe social à l'autre), on ne renvoie rien : désigner « les
    hommes » comme les plus touchés par la perte de couvert forestier serait
    un artefact de tri.
    """
    v, s = r.get("valeurs") or {}, r.get("scores_corriges") or {}
    ks = [k for k in clefs if isinstance(v.get(k), (int, float))]
    if len(ks) < 2 or max(v[k] for k in ks) - min(v[k] for k in ks) < 1e-9:
        return None
    k = min(ks, key=lambda x: (s.get(x, 99), pol * v[x]))
    return (k, v[k])


def _deficit(r):
    s = (r.get("scores_corriges") or {}).get("Total")
    if s is None:
        return 0.0
    return (r.get("ponderation") or 1) * (10.0 - float(s))


def _classement(par_ligne):
    """Tous les indicateurs scorés, du plus coûteux au moins coûteux."""
    res = [r for r in par_ligne.values()
           if (r.get("scores_corriges") or {}).get("Total") is not None]
    manque = sum(_deficit(r) for r in res) or 1.0
    for r in res:
        r["_def"] = _deficit(r)
        r["_part"] = r["_def"] / manque * 100.0
    return sorted(res, key=lambda r: -r["_def"]), res, manque


def _constats(par_ligne):
    """Un constat par dimension : le plus lourd de chacune."""
    classe, _, _ = _classement(par_ligne)
    pris, out = set(), []
    for r in classe:
        d = IP.DIM_DE.get(r.get("dimension") or "")
        if d in DIMS and d not in pris:
            pris.add(d)
            out.append((d, r))
    return sorted(out, key=lambda x: DIMS.index(x[0]))


def _nom(r):
    if _lang_fr() and r.get("indicateur_fr"):
        return r["indicateur_fr"]
    return r.get("indicateur", "")


def _expl(r):
    return r.get("expl_fr" if _lang_fr() else "expl_en") or ""


def _unite(r):
    u = (r.get("unite") or "").strip()
    if u:
        return u
    return "%" if "%" in (r.get("metrique") or "") else ""


def _val(r, cle="Total"):
    v = (r.get("valeurs") or {}).get(cle)
    if not isinstance(v, (int, float)):
        return "—"
    u = _unite(r)
    return _f(v, 1) + (f" {u}" if u else "")


def _couleur_score(s):
    return ROUGE if s <= 2 else (AMBRE if s <= 5 else VERT)


def _carte_constat(i, dim, r, dims):
    pol = _polarite(r)
    s = float((r.get("scores_corriges") or {})["Total"])
    v = (r.get("valeurs") or {}).get("Total")
    u = _unite(r)
    reste = None
    if u == "%" and pol > 0 and isinstance(v, (int, float)) and 0 <= v <= 100:
        reste = 100.0 - v
    ps = _pire(r, SECTIONS, pol)
    pg = _pire(r, GROUPES, pol)
    n = (r.get("n") or {}).get("Total")
    sd = dims.get(dim)

    with st.container(border=True):
        st.markdown(
            f'<div style="display:flex;gap:12px;align-items:flex-start">'
            f'<div class="nb-num">{i}</div><div style="flex:1">'
            f'<div class="nb-dim">{_e(T(dim))}'
            f'{" · " + _e(T("nb_dim_score").format(s=_f(sd, 2))) if sd is not None else ""}'
            f'</div>'
            f'<div class="nb-t">{_e(_nom(r))}</div></div></div>',
            unsafe_allow_html=True)

        chiffres = [
            f'<div class="nb-f"><div class="nb-fv" style="color:{ENCRE}">'
            f'{_e(_val(r))}</div>'
            f'<div class="nb-fl">{_e(T("nb_mesure"))}</div></div>']
        if reste is not None:
            chiffres.append(
                f'<div class="nb-f"><div class="nb-fv" style="color:{ROUGE}">'
                f'{_e(_pc(reste))}</div>'
                f'<div class="nb-fl">{_e(T("nb_reste"))}</div></div>')
        chiffres.append(
            f'<div class="nb-f"><div class="nb-fv" '
            f'style="color:{_couleur_score(s)}">{_f(s, 0)}<span '
            f'style="font-size:15px;color:{GRIS}"> / 10</span></div>'
            f'<div class="nb-fl">{_e(T("nb_score"))}</div></div>')
        # LA PONDÉRATION N'EST PAS DANS LA CARTE. Cinq chiffres passaient à la
        # ligne dans une colonne sur deux, et c'est celui-ci qui se lit le
        # moins bien seul : « 3,06 » ne dit rien sans l'échelle des poids. Ce
        # qu'il sert à dire — le coût de l'écart pour l'indice — est déjà là,
        # en pourcentage. La pondération reste dans le tableau détaillé.
        chiffres.append(
            f'<div class="nb-f"><div class="nb-fv" style="color:{ENCRE2}">'
            f'{_pc(r.get("_part") or 0)}</div>'
            f'<div class="nb-fl">{_e(T("nb_part"))}</div></div>')
        st.markdown('<div class="nb-fig">' + "".join(chiffres) + "</div>",
                    unsafe_allow_html=True)

        st.markdown(
            f'<div class="nb-jauge"><div class="nb-jr" style="width:'
            f'{max(2.0, s * 10):.0f}%;background:{_couleur_score(s)}"></div>'
            f'</div>', unsafe_allow_html=True)

        if _expl(r):
            st.markdown(f'<p class="nb-p">{_e(_expl(r))}</p>',
                        unsafe_allow_html=True)

        bouts = []
        if ps:
            bouts.append(f'{_e(T("nb_localite"))} <b>{_e(ps[0])}</b> '
                         f'({_e(_f(ps[1], 1))}{" " + _unite(r) if _unite(r) else ""})')
        if pg:
            bouts.append(f'{_e(T("nb_groupe"))} <b>{_e(pg[0])}</b> '
                         f'({_e(_f(pg[1], 1))}{" " + _unite(r) if _unite(r) else ""})')
        if n:
            bouts.append(_e(T("nb_base").format(n=f"{int(n):,}".replace(",", " "))))
        if bouts:
            st.markdown(
                f'<div class="nb-tou">{_e(T("nb_touche"))} · '
                + " · ".join(bouts) + "</div>", unsafe_allow_html=True)


def _tableau_ecarts(classe):
    lignes = [
        f'<table class="nb-t2"><tr><th>{_e(T("nb_c_ind"))}</th>'
        f'<th>{_e(T("nb_c_dim"))}</th><th>{_e(T("nb_c_val"))}</th>'
        f'<th>{_e(T("nb_c_sc"))}</th><th>{_e(T("nb_c_p"))}</th>'
        f'<th>{_e(T("nb_c_part"))}</th></tr>']
    for r in classe[:12]:
        d = IP.DIM_DE.get(r.get("dimension") or "")
        s = float(r["scores_corriges"]["Total"])
        lignes.append(
            f'<tr><td>{_e(_nom(r))}</td>'
            f'<td style="text-align:left;font-size:12px;color:{ENCRE3}">'
            f'{_e(T(d) if d in DIMS else "—")}</td>'
            f'<td>{_e(_val(r))}</td>'
            f'<td style="color:{_couleur_score(s)};font-weight:700">'
            f'{_f(s, 0)}</td>'
            f'<td>{_f(r.get("ponderation") or 0, 2)}</td>'
            f'<td>{_pc(r.get("_part") or 0)}</td></tr>')
    lignes.append("</table>")
    st.markdown("".join(lignes), unsafe_allow_html=True)


# ----------------------------------------------------------------- réponses
def _rattachement(f, constats):
    """À quel constat une fiche répond — par la ligne, puis par la dimension."""
    for i, (d, r) in enumerate(constats, 1):
        if r["ligne"] == f.get("ligne_probleme"):
            return T("nb_repond").format(n=i), VERT
    for i, (d, r) in enumerate(constats, 1):
        if d and d == f.get("dim_probleme"):
            return T("nb_repond_dim").format(n=i), BLEU
    return T("nb_repond_non"), GRIS


def _carte_fiche(rang, f, emax, constats):
    lib = f["noeud"]["fr"] if _lang_fr() else f["noeud"]["en"]
    titre = T(f"int_{f['id']}_t")
    obj = T(f"int_{f['id']}_o")
    act = T(f"int_{f['id']}_ac")
    rat, coul = _rattachement(f, constats)
    dep = f.get("depart")
    with st.container(border=True):
        st.markdown(
            f'<div class="nb-dim">{rang:02d} · {_e(lib)}</div>'
            f'<div class="nb-t">{_e(titre)}</div>'
            f'<p class="nb-p" style="margin-top:6px">{_e(obj)}</p>',
            unsafe_allow_html=True)
        st.markdown(
            f'<div class="nb-fig" style="margin:12px 0 2px">'
            f'<div class="nb-f"><div class="nb-fv" style="color:{VERT}">'
            f'{_f(f["delta"], 3, signe=True)}</div>'
            f'<div class="nb-fl">{_e(T("nb_effet"))}</div></div>'
            f'<div class="nb-f"><div class="nb-fv" style="font-size:16px;'
            f'color:{ENCRE2}">{_e(T("int_h_" + f["horizon"]))}</div>'
            f'<div class="nb-fl">{_e(T("nb_horizon"))}</div></div>'
            f'<div class="nb-f"><div class="nb-fv" style="font-size:16px;'
            f'color:{ENCRE2}">{_e(T("int_f_" + f["faisabilite"]))}</div>'
            f'<div class="nb-fl">{_e(T("nb_fais"))}</div></div></div>',
            unsafe_allow_html=True)
        st.markdown(
            f'<div class="nb-jauge"><div class="nb-jr" style="width:'
            f'{max(3.0, abs(f["delta"]) / emax * 100):.0f}%;background:{VERT}">'
            f'</div></div>', unsafe_allow_html=True)
        bas = [f'<span class="nb-chip" style="background:{coul}18;color:{coul}">'
               f'{_e(rat)}</span>']
        if dep is not None:
            bas.append(
                f'<span class="nb-chip" style="background:#f1f4f9;color:{ENCRE2}">'
                f'{_e(T("nb_levier").format(a=_f(dep, 1), b=_f(min(10.0, dep + f["cible"]), 1)))}'
                f'</span>')
        st.markdown('<div style="margin-top:9px">' + "".join(bas) + "</div>",
                    unsafe_allow_html=True)
        if act:
            st.markdown(
                f'<div class="nb-tou">{_e(T("nb_acteurs"))} · {_e(act)}</div>',
                unsafe_allow_html=True)


# ----------------------------------------------------------------- la page
def render():
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown(
        f'<h2 style="font-size:27px;font-weight:700;color:{ENCRE};'
        f'letter-spacing:-.02em;margin:2px 0 0">{_e(T("nb_titre"))}</h2>'
        f'<p style="font-size:12.5px;color:{ENCRE3};letter-spacing:.06em;'
        f'text-transform:uppercase;margin:2px 0 0;font-weight:600">'
        f'{_e(T("nb_sous_titre"))}</p>', unsafe_allow_html=True)

    tout = _tout()
    if not tout:
        st.warning(T("nb_absent"))
        return

    par_ligne = tout["par_ligne"]
    fiches = tout["fiches"]
    dims = tout["dims"]
    indice = tout["indice"]
    classe, res, manque = _classement(par_ligne)
    constats = _constats(par_ligne)

    st.info(T("nb_intro"))

    # ---- les quatre chiffres
    bases = [int((r.get("n") or {}).get("Total") or 0) for r in res]
    bases = [b for b in bases if b]
    frequente = max(set(bases), key=bases.count) if bases else 0
    n_menages = _n_repondants(frequente)
    bas = [r for r in res if float(r["scores_corriges"]["Total"]) <= 1]
    poids_total = sum((r.get("ponderation") or 1) for r in res) or 1
    part_bas = sum((r.get("ponderation") or 1) for r in bas) / poids_total * 100
    pf = tout["portefeuille"]

    k = st.columns(4)
    cartes = [
        (T("nb_k1"), f"{int(n_menages):,}".replace(",", " "),
         T("nb_k1_x").format(s=len(SECTIONS)), ENCRE),
        (T("nb_k2"), _f(indice, 2) + " / 10",
         T("nb_k2_x").format(n=len(res)), _couleur_score(indice)),
        (T("nb_k3"), str(len(bas)),
         T("nb_k3_x").format(p=_f(part_bas, 0)), ROUGE),
        (T("nb_k4"), _f(pf["delta"], 3, signe=True), T("nb_k4_x"), VERT),
    ]
    for col, (lab, val, sub, coul) in zip(k, cartes):
        with col:
            st.markdown(
                f'<div class="nb-k"><div class="nb-kl">{_e(lab)}</div>'
                f'<div class="nb-kv" style="color:{coul}">{_e(val)}</div>'
                f'<div class="nb-kx">{_e(sub)}</div></div>',
                unsafe_allow_html=True)

    # ---- 1 · les constats
    st.markdown(f'<h3 style="font-size:19px;font-weight:700;color:{ENCRE};'
                f'margin:26px 0 2px">{_e(T("nb_s1"))}</h3>',
                unsafe_allow_html=True)
    st.markdown(f'<p class="nb-p">{_gras(T("nb_regle"))}</p>',
                unsafe_allow_html=True)

    for i in range(0, len(constats), 2):
        cols = st.columns(2, gap="medium")
        for j, (col, (d, r)) in enumerate(zip(cols, constats[i:i + 2])):
            with col:
                _carte_constat(i + j + 1, d, r, dims)

    with st.expander(T("nb_autres")):
        _tableau_ecarts(classe)

    # ---- 2 · les réponses
    st.markdown(f'<h3 style="font-size:19px;font-weight:700;color:{ENCRE};'
                f'margin:26px 0 2px">{_e(T("nb_s2"))}</h3>',
                unsafe_allow_html=True)
    st.markdown(f'<p class="nb-p">{_gras(T("nb_s2_note"))}</p>',
                unsafe_allow_html=True)
    emax = max((abs(f["delta"]) for f in fiches), default=1) or 1
    for i in range(0, len(fiches), 2):
        cols = st.columns(2, gap="medium")
        for j, (col, f) in enumerate(zip(cols, fiches[i:i + 2])):
            with col:
                _carte_fiche(i + j + 1, f, emax, constats)

    # ---- 3 · ce que le portefeuille déplace
    st.markdown(f'<h3 style="font-size:19px;font-weight:700;color:{ENCRE};'
                f'margin:26px 0 2px">{_e(T("nb_s3"))}</h3>',
                unsafe_allow_html=True)
    somme = sum(f["delta"] for f in fiches)
    apres = indice + pf["delta"]
    reste_pts = 10.0 - indice
    with st.container(border=True):
        c = st.columns(3)
        trio = [(T("nb_avant"), _f(indice, 2) + " / 10", ENCRE2),
                (T("nb_apres"), _f(apres, 2) + " / 10", ENCRE),
                (T("nb_gain"), _f(pf["delta"], 3, signe=True), VERT)]
        for col, (lab, val, coul) in zip(c, trio):
            with col:
                st.markdown(
                    f'<div class="nb-kl">{_e(lab)}</div>'
                    f'<div class="nb-kv" style="color:{coul}">{_e(val)}</div>',
                    unsafe_allow_html=True)
        st.markdown(
            f'<div class="nb-jauge" style="height:14px;margin-top:12px">'
            f'<div class="nb-jr" style="width:{indice * 10:.1f}%;'
            f'background:{ENCRE2}"></div>'
            f'<div class="nb-jr" style="left:{indice * 10:.1f}%;'
            f'width:{max(0.4, pf["delta"] * 10):.2f}%;background:{VERT}"></div>'
            f'</div>', unsafe_allow_html=True)
        # DEUX PHRASES, ET C'EST LE CALCUL QUI CHOISIT. Le portefeuille peut
        # déplacer moins que la somme de ses fiches — c'est le cas ordinaire,
        # quand deux fiches poussent le même indicateur — ou exactement autant,
        # ce qui est une information à part entière et qu'il aurait été faux
        # d'annoncer comme un recouvrement.
        if abs(somme - pf["delta"]) < 0.005:
            st.caption(T("nb_somme_egal").format(c=_f(pf["delta"], 3)))
        else:
            st.caption(T("nb_somme").format(c=_f(pf["delta"], 3),
                                            s=_f(somme, 3)))

    st.markdown(
        f'<p class="nb-p">{_gras(T("nb_manque").format(g=_f(pf["delta"], 2), m=_f(reste_pts, 2), p=_f(pf["delta"] / reste_pts * 100, 1)))}</p>',
        unsafe_allow_html=True)
    st.caption(T("nb_couvert").format(
        p=_f(pf["part_couverte"] * 100, 0),
        q=_f(100 - pf["part_couverte"] * 100, 0)))

    # LES CONSTATS ORPHELINS. C'est le bloc qu'une plaquette n'écrirait pas :
    # il dit quelle part du diagnostic reste sans réponse dans ce portefeuille.
    couverts = set()
    for f in fiches:
        for i, (d, r) in enumerate(constats, 1):
            if r["ligne"] == f.get("ligne_probleme") or d == f.get("dim_probleme"):
                couverts.add(i)
    orphelins = [(i, d, r) for i, (d, r) in enumerate(constats, 1)
                 if i not in couverts]
    with st.container(border=True):
        st.markdown(f'<div class="nb-kl">{_e(T("nb_sans"))}</div>',
                    unsafe_allow_html=True)
        if not orphelins:
            st.markdown(f'<p class="nb-p">{_e(T("nb_sans_non"))}</p>',
                        unsafe_allow_html=True)
        else:
            st.markdown("".join(
                f'<p class="nb-p" style="margin-top:6px">'
                + _gras(T("nb_orphelin").format(
                    n=i, ind=_nom(r), dim=T(d),
                    s=_f(float(r["scores_corriges"]["Total"]), 0),
                    p=_f(r.get("_part") or 0, 1))) + "</p>"
                for i, d, r in orphelins), unsafe_allow_html=True)

    # ---- 4 · séquencement
    st.markdown(f'<h3 style="font-size:19px;font-weight:700;color:{ENCRE};'
                f'margin:26px 0 2px">{_e(T("nb_s4"))}</h3>',
                unsafe_allow_html=True)
    st.markdown(f'<p class="nb-p">{_gras(T("nb_s4_note"))}</p>',
                unsafe_allow_html=True)
    par_id = {f["id"]: f for f in fiches}
    lots = [(T("nb_lot1"), tout["lot1"], VERT), (T("nb_lot2"), tout["lot2"], BLEU)]
    cols = st.columns(2, gap="medium")
    for col, (lab, lot, coul) in zip(cols, lots):
        with col:
            with st.container(border=True):
                noms = " · ".join(
                    _e(par_id[i]["noeud"]["fr" if _lang_fr() else "en"])
                    for i in lot["ids"] if i in par_id)
                st.markdown(
                    f'<div class="nb-kl">{_e(lab)}</div>'
                    f'<div class="nb-kv" style="color:{coul}">'
                    f'{_f(lot["eff"]["delta"], 3, signe=True)}</div>'
                    f'<div class="nb-kx">'
                    f'{_e(T("nb_lot_n").format(n=len(lot["ids"])))} — {noms}'
                    f'</div>', unsafe_allow_html=True)
    if pf["delta"]:
        st.caption(T("nb_lot_part").format(
            n=len(tout["lot1"]["ids"]), t=len(fiches),
            p=_f(tout["lot1"]["eff"]["delta"] / pf["delta"] * 100, 0)))

    # ---- 5 · les réserves
    st.markdown(f'<h3 style="font-size:19px;font-weight:700;color:{ENCRE};'
                f'margin:26px 0 2px">{_e(T("nb_s5"))}</h3>',
                unsafe_allow_html=True)
    with st.container(border=True):
        # En markdown, pas en HTML injecté : les puces et le gras doivent être
        # rendus par Streamlit, et cette liste est du texte, pas une mise en page.
        st.markdown("\n".join(
            f"- {T(k)}" for k in ("nb_r1", "nb_r2", "nb_r3", "nb_r4", "nb_r5")))
    st.caption(T("nb_ou"))
