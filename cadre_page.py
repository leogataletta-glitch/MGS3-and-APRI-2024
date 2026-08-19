"""Cadre de résilience — ce que mesure l'indice, et comment il est construit.

CETTE PAGE SE REGARDE, ELLE NE SE LIT PAS.

Elle a remplacé une page de méthodologie faite de sept longs blocs de texte.
Personne ne lit sept blocs de texte sur un tableau de bord ; le lecteur veut
savoir en trente secondes ce que le chiffre 4,54 signifie et d'où il sort. Tout
est donc porté par des schémas — la chaîne de calcul en quatre étapes, les sept
dimensions et leur poids réel, le plan de sondage en chiffres clés — et le
texte se limite à ce qu'un schéma ne peut pas dire.

Le document méthodologique complet n'est pas perdu : il est en bas de page,
replié, pour qui veut le détail.

TOUS LES CHIFFRES SONT CALCULÉS depuis `resultats.json`. Le poids d'une
dimension, sa couverture, le nombre d'indicateurs : rien n'est écrit en dur.
Une page de méthode qui annonce des poids faux est pire qu'une page absente,
parce qu'on la croit.

LES COULEURS SONT VALIDÉES, PAS CHOISIES À L'ŒIL. Les sept teintes de
dimension passent les cinq contrôles d'un validateur de palette : bande de
clarté, plancher de saturation, séparation des paires voisines en vision
déficiente (deutéranopie, protanopie, tritanopie), plancher en vision normale,
contraste sur le fond. Elles ne servent jamais seules : chaque pastille est
accompagnée du nom de la dimension en toutes lettres.
"""

import json
import os

import streamlit as st

import environnement_cadre
import i18n
import icones
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

DIM_CLE = {
    "I. PHYSICAL AND INFRASTRUCTURAL DIMENSION": "dim1",
    "II. INSTITUTIONAL, TECHNOLOGICAL, AND GOVERNANCE  DIMENSION": "dim2",
    "III.  ENVIRONMENTAL AND ECOLOGICAL DIMENSION": "dim3",
    "IV. ECONOMIC, LIVELIHOODS, AND FOOD SECURITY DIMENSION": "dim4",
    "V. SOCIAL AND COMMUNITY DIMENSION": "dim5",
    "VI. HUMAN DIMENSION": "dim6",
    "VII. CULTURAL, IDENTITY-BASED, AND PSYCHOLOGICAL DIMENSION": "dim7",
}
ORDRE = ["dim1", "dim2", "dim3", "dim4", "dim5", "dim6", "dim7"]

# Palette validée — voir l'en-tête du module. L'ordre n'est pas sémantique : il
# est contraint par la séparation des paires VOISINES, puisque les dimensions
# se lisent toujours dans l'ordre I → VII. Seul le vert de l'environnement est
# un choix de sens, et il a été conservé.
TEINTES = {"dim1": "#d1730c", "dim2": "#2166ac", "dim3": "#1a8a4f",
           "dim4": "#a02c8f", "dim5": "#0f8fa8", "dim6": "#c33a24",
           "dim7": "#7048b6"}

ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"
BORD, GRIS = "#e3eaf3", "#f1f4f9"

# ---------------------------------------------------------------------------
# Les textes voyagent avec le module : une page nouvelle ne doit pas dépendre
# d'un i18n.py envoyé séparément pour s'afficher. Ils sont versés dans le
# dictionnaire commun à l'import, sans écraser une clé déjà présente.
# ---------------------------------------------------------------------------
TEXTES = {
    "cad_titre": {"en": "Resilience Framework",
                  "fr": "Cadre de résilience"},
    "cad_sous_titre": {
        "en": "What the index measures, how it is built, and what it cannot say",
        "fr": "Ce que l'indice mesure, comment il est construit, et ce qu'il "
              "ne peut pas dire"},

    # --- les trois cartouches d'ouverture
    "cad_quoi_t": {"en": "General resilience", "fr": "Résilience générale"},
    "cad_quoi": {
        "en": "The capacity to anticipate, absorb and adapt to multiple "
              "disturbances — not the response to one hazard.",
        "fr": "La capacité d'anticiper, d'absorber et de s'adapter à des "
              "perturbations multiples — pas la réponse à un aléa unique."},
    "cad_quand_t": {"en": "Capacities held before the shock",
                    "fr": "Des capacités détenues avant le choc"},
    "cad_quand": {
        "en": "The index describes what a territory can mobilise, measured ex "
              "ante. It is not a record of damage after the event.",
        "fr": "L'indice décrit ce qu'un territoire peut mobiliser, mesuré "
              "ex ante. Ce n'est pas un relevé de dégâts après coup."},
    "cad_echelle_t": {"en": "A 0 to 10 scale", "fr": "Une échelle de 0 à 10"},
    "cad_echelle": {
        "en": "10 is the most favourable configuration, 0 the most critical. "
              "It is a relative position, not a probability.",
        "fr": "10 est la configuration la plus favorable, 0 la plus critique. "
              "C'est une position relative, pas une probabilité."},

    # --- le cadre AAA
    "cad_aaa": {"en": "Three attributes, read across every dimension",
                "fr": "Trois attributs, lus sur chaque dimension"},
    "cad_aaa_note": {
        "en": "Every indicator in the framework is attached to the attribute "
              "or attributes it contributes to.",
        "fr": "Chaque indicateur du référentiel est rattaché à l'attribut ou "
              "aux attributs auxquels il contribue."},
    "cad_a1_t": {"en": "Anticipate", "fr": "Anticiper"},
    "cad_a1": {"en": "Detect disturbances and prepare responses before they "
                     "arrive",
               "fr": "Détecter les perturbations et préparer les réponses "
                     "avant qu'elles n'arrivent"},
    "cad_a2_t": {"en": "Absorb", "fr": "Absorber"},
    "cad_a2": {"en": "Limit the impact of a shock as it happens",
               "fr": "Limiter l'impact d'un choc au moment où il survient"},
    "cad_a3_t": {"en": "Adapt", "fr": "S'adapter"},
    "cad_a3": {"en": "Transform the system durably rather than return to the "
                     "prior state",
               "fr": "Transformer durablement le système plutôt que revenir à "
                     "l'état antérieur"},

    # --- les sept dimensions
    "cad_dims": {"en": "Seven dimensions, and what each weighs",
                 "fr": "Sept dimensions, et ce que chacune pèse"},
    "cad_dims_note": {
        "en": "Weight is the share of the composite index each dimension "
              "carries. Coverage is the share of that weight actually "
              "computed to date — an uncomputed indicator is excluded from "
              "the mean, never counted as a zero.",
        "fr": "Le poids est la part de l'indice composite que porte chaque "
              "dimension. La couverture est la part de ce poids réellement "
              "calculée à ce jour — un indicateur non calculé est exclu de la "
              "moyenne, jamais compté comme un zéro."},
    "cad_col_dim": {"en": "Dimension", "fr": "Dimension"},
    "cad_col_poids": {"en": "Weight in the index", "fr": "Poids dans l'indice"},
    "cad_col_couv": {"en": "Coverage", "fr": "Couverture"},
    "cad_col_ind": {"en": "Indicators", "fr": "Indicateurs"},
    "cad_dim7_note": {
        "en": "The seventh dimension — cultural, identity-based and "
              "psychological — has no computed indicator to date. It is shown "
              "here so that an absence is not mistaken for a non-existence.",
        "fr": "La septième dimension — culturelle, identitaire et "
              "psychologique — n'a aucun indicateur calculé à ce jour. Elle "
              "figure ici pour qu'une absence ne passe pas pour une "
              "inexistence."},

    # --- la chaîne de calcul
    "cad_chaine": {"en": "From an answer to a score",
                   "fr": "De la réponse au score"},
    "cad_e1_t": {"en": "1 · Metric", "fr": "1 · Métrique"},
    "cad_e1": {"en": "Answers are aggregated at communal-section level, most "
                     "often as a percentage of households",
               "fr": "Les réponses sont agrégées à l'échelle de la section "
                     "communale, le plus souvent en pourcentage de ménages"},
    "cad_e2_t": {"en": "2 · Scale", "fr": "2 · Barème"},
    "cad_e2": {"en": "Each metric is cut into 11 ordinal classes, from 0 to "
                     "10, by a published threshold table",
               "fr": "Chaque métrique est découpée en 11 classes ordinales, "
                     "de 0 à 10, par une table de seuils publiée"},
    "cad_e3_t": {"en": "3 · Weight", "fr": "3 · Pondération"},
    "cad_e3": {"en": "Each indicator carries its own weight; the sum across "
                     "the framework is {ptot}",
               "fr": "Chaque indicateur porte son poids propre ; leur somme "
                     "sur le référentiel vaut {ptot}"},
    "cad_e4_t": {"en": "4 · Aggregation", "fr": "4 · Agrégation"},
    "cad_e4": {"en": "Weighted mean of the scored indicators — uncomputed "
                     "ones are excluded from the denominator",
               "fr": "Moyenne pondérée des indicateurs scorés — les non "
                     "calculés sont exclus du dénominateur"},

    # --- le plan de sondage
    "cad_sondage": {"en": "Sampling design", "fr": "Plan de sondage"},
    "cad_s1_t": {"en": "questionnaires", "fr": "questionnaires"},
    "cad_s1": {"en": "collected in 2024", "fr": "collectés en 2024"},
    "cad_s2_t": {"en": "communal sections", "fr": "sections communales"},
    "cad_s2": {"en": "each surveyed in full", "fr": "enquêtées en entier"},
    "cad_s3_t": {"en": "confidence", "fr": "de confiance"},
    "cad_s3": {"en": "for a 7.5 % margin of error",
               "fr": "pour une marge d'erreur de 7,5 %"},
    "cad_s4_t": {"en": "households minimum", "fr": "ménages au minimum"},
    "cad_s4": {"en": "per communal section", "fr": "par section communale"},
    "cad_strates": {"en": "Four crossed strata",
                    "fr": "Quatre critères de stratification"},
    "cad_st1": {"en": "Landscape — coastal or mountain",
                "fr": "Paysage — littoral ou montagne"},
    "cad_st2": {"en": "Age — 15-30 or over 30", "fr": "Âge — 15-30 ou plus de 30"},
    "cad_st3": {"en": "Sex — woman or man", "fr": "Sexe — femme ou homme"},
    "cad_st4": {"en": "Economic category — extreme poverty, poverty, "
                      "non-poverty",
                "fr": "Catégorie économique — extrême pauvreté, pauvreté, "
                      "non-pauvreté"},
    "cad_tirage": {
        "en": "Households are drawn at random within strata from a "
              "georeferenced building base (OpenStreetMap), so that areas "
              "without a reliable administrative register are still covered. "
              "The strata reproduce the population structure, which is why "
              "simple means by profile are unbiased estimators — no "
              "post-stratification weighting is applied.",
        "fr": "Les ménages sont tirés au sort dans chaque strate à partir "
              "d'une base de bâtiments géoréférencés (OpenStreetMap), pour "
              "que les zones sans registre administratif fiable soient "
              "couvertes malgré tout. Les strates reproduisent la structure "
              "de la population : les moyennes simples par profil sont donc "
              "des estimateurs sans biais, sans redressement."},

    # --- les limites
    "cad_limites": {"en": "What the index cannot say",
                    "fr": "Ce que l'indice ne peut pas dire"},
    "cad_l1_t": {"en": "Circularity", "fr": "Circularité"},
    "cad_l1": {"en": "Like any composite index, it defines resilience by the "
                     "variables assumed to produce it. A rising score first "
                     "means the measured dimensions moved.",
               "fr": "Comme tout indice composite, il définit la résilience "
                     "par les variables supposées la produire. Un score qui "
                     "monte signifie d'abord que les dimensions mesurées ont "
                     "bougé."},
    "cad_l2_t": {"en": "No empirical validation", "fr": "Pas de validation empirique"},
    "cad_l2": {"en": "Phase 4 on the OECD-UN scale: operational on a limited "
                     "territory, not yet confronted with trajectories "
                     "observed after a real shock.",
               "fr": "Phase 4 sur l'échelle OCDE-ONU : opérationnel sur un "
                     "territoire limité, pas encore confronté à des "
                     "trajectoires observées après un choc réel."},
    "cad_l3_t": {"en": "A static measure", "fr": "Une mesure statique"},
    "cad_l3": {"en": "It describes capacities at one moment. Feedback loops "
                     "and tipping points are the job of the participatory "
                     "causal analysis, not of the index.",
               "fr": "Il décrit des capacités à un instant donné. Les boucles "
                     "de rétroaction et les seuils de bascule relèvent de "
                     "l'analyse causale participative, pas de l'indice."},
    "cad_l4_t": {"en": "Framing, not forecasting", "fr": "Cadrage, pas prévision"},
    "cad_l4": {"en": "It ranks and prioritises. It does not predict what a "
                     "given hazard will cost a given section.",
               "fr": "Il hiérarchise et priorise. Il ne prédit pas ce qu'un "
                     "aléa donné coûtera à une section donnée."},

    # --- le second volet : l'analyse causale
    "cad_dbc": {"en": "The second strand — causal loop diagrams",
                "fr": "Le second volet — les diagrammes de boucles causales"},
    "cad_dbc_x": {
        "en": "In a socio-ecological system, interactions are not linear: a "
              "cause becomes a consequence, and some effects feed themselves. "
              "Where a problem tree shows the visible chain of causes and "
              "effects, a causal loop diagram shows the internal feedbacks — "
              "why a system persists, degrades, or finds its balance again. "
              "That is the heart of resilience.",
        "fr": "Dans un système socio-écologique, les interactions ne sont pas "
              "linéaires : une cause devient une conséquence, et certains "
              "effets s'auto-renforcent. Là où l'arbre à problèmes montre la "
              "chaîne visible des causes et des effets, le diagramme de "
              "boucles causales montre les rétroactions internes — pourquoi "
              "un système persiste, se dégrade, ou retrouve son équilibre. "
              "C'est le cœur de la résilience."},
    "cad_dbc_1_t": {"en": "1 · The symptom", "fr": "1 · La variable symptôme"},
    "cad_dbc_1": {
        "en": "Start from the indicator in red — falling tree cover, dropping "
              "yields, rising erosion. It is the visible malfunction, and the "
              "entry point for going back up to causes and down to effects.",
        "fr": "Partir de l'indicateur en rouge — recul du couvert végétal, "
              "baisse de productivité, érosion accrue. C'est le "
              "dysfonctionnement visible, et le point d'entrée pour remonter "
              "aux causes et descendre aux conséquences."},
    "cad_dbc_2_t": {"en": "2 · The circular chains",
                    "fr": "2 · Les enchaînements circulaires"},
    "cad_dbc_2": {
        "en": "Spot where an effect becomes a cause in turn. Slash-and-burn "
              "costs fertility, which pushes farmers to burn new land: the "
              "process feeds itself. That is a feedback loop.",
        "fr": "Repérer où un effet devient à son tour une cause. Le brûlis "
              "coûte de la fertilité, ce qui pousse à ouvrir de nouvelles "
              "terres par le feu : le processus s'auto-alimente. C'est une "
              "boucle de rétroaction."},
    "cad_dbc_3_t": {"en": "3 · The levers", "fr": "3 · Les leviers"},
    "cad_dbc_3": {
        "en": "Find the nodes with many links that sit in loops of opposite "
              "sign: acting there can tip the system from a degrading "
              "dynamic into a resilience one. The tool computes them.",
        "fr": "Trouver les nœuds très connectés qui appartiennent à des "
              "boucles de sens opposé : agir là peut faire basculer le "
              "système d'une dynamique dégradante vers une dynamique de "
              "résilience. L'outil les calcule."},
    "cad_dbc_4_t": {"en": "4 · The action sheet",
                    "fr": "4 · La fiche d'action"},
    "cad_dbc_4": {
        "en": "For each lever: expected effect on the score, feasibility, key "
              "actors, time horizon, and the performance indicators that will "
              "tell whether it worked.",
        "fr": "Pour chaque levier : effet attendu sur le score, faisabilité, "
              "acteurs clés, horizon de mise en œuvre, et les indicateurs de "
              "performance qui diront si cela a marché."},
    "cad_lecture": {"en": "How to read a loop", "fr": "Comment lire une boucle"},
    "cad_lecture_x": {
        "en": "Each arrow carries a polarity. **+** the two variables move "
              "the same way; **−** they move opposite ways. Multiply the "
              "signs around the loop: an even number of **−** makes it "
              "**reinforcing (R)** — it accelerates its own dynamic; an odd "
              "number makes it **balancing (B)** — it pulls the system back "
              "towards a resting point. Simpler still: raise A; if A ends up "
              "higher, the loop is R; if A ends up lower, it is B.",
        "fr": "Chaque flèche porte une polarité. **+** les deux variables "
              "changent dans le même sens ; **−** en sens opposé. On "
              "multiplie les signes le long de la boucle : un nombre pair de "
              "**−** la rend **renforçante (R)** — elle accélère sa propre "
              "dynamique ; un nombre impair la rend **équilibrante (B)** — "
              "elle ramène le système vers un point de repos. Plus simple "
              "encore : j'augmente A ; si A finit plus haut, la boucle est "
              "R ; si A finit plus bas, elle est B."},
    "cad_lecture_piege": {
        "en": "**The trap: « positive » does not mean « good ».** It says the "
              "variables move together. A reinforcing loop pushed upward is a "
              "virtuous spiral (R+); the same loop pushed downward is a "
              "vicious one (R−). And a balancing loop can lock a system into "
              "a degraded state (B−) — falling yields drive out-migration, "
              "which eases pressure and lets the forest return, but through "
              "rural collapse.",
        "fr": "**Le piège : « positive » ne veut pas dire « bonne ».** Cela "
              "dit que les variables bougent ensemble. Une boucle renforçante "
              "poussée à la hausse est une spirale vertueuse (R+) ; la même "
              "poussée à la baisse est vicieuse (R−). Et une boucle "
              "équilibrante peut figer le système dans un état dégradé "
              "(B−) — la baisse des rendements pousse à la migration, ce qui "
              "allège la pression et laisse la forêt revenir, mais par "
              "effondrement rural."},
    "cad_dbc_lien": {
        "en": "The tool is in the **Feedback Loops** tab: push a lever, watch "
              "the wave travel, isolate a loop.",
        "fr": "L'outil est dans l'onglet **Boucles de rétroaction** : "
              "poussez un levier, suivez l'onde, isolez une boucle."},
    # ================= STRATE 1 — les quatre cartouches de tête =============
    "cad_n1_t": {"en": "What APRI measures", "fr": "Ce que mesure APRI"},
    "cad_n1": {"en": "A territory's capacity to anticipate, absorb and adapt "
                     "to disturbances.",
               "fr": "La capacité d'un territoire à anticiper, absorber et "
                     "s'adapter aux perturbations."},
    "cad_n2_t": {"en": "What the index captures", "fr": "Ce que l'indice saisit"},
    "cad_n2": {"en": "The capacities a territory already holds before a shock, "
                     "across {n} dimensions of resilience.",
               "fr": "Les capacités que le territoire détient déjà avant le "
                     "choc, sur {n} dimensions de la résilience."},
    "cad_n3_t": {"en": "How it is measured", "fr": "Comment il est mesuré"},
    "cad_n3": {"en": "A 0 to 10 score built from {i} indicators and three "
                     "independent data sources.",
               "fr": "Un score de 0 à 10 construit sur {i} indicateurs et "
                     "trois sources de données indépendantes."},
    "cad_n4_t": {"en": "What it does NOT measure",
                 "fr": "Ce qu'il ne mesure PAS"},
    "cad_n4": {"en": "Not the damage suffered after an event, and not a "
                     "forecast of what a hazard will cost.",
               "fr": "Ni les dommages subis après un événement, ni une "
                     "prévision de ce que coûtera un aléa."},

    # ================= le schéma d'ensemble ==================================
    "cad_apercu": {"en": "APRI at a glance", "fr": "APRI en un coup d'œil"},
    "cad_ap_note": {
        "en": "Read left to right: the index is defined by three attributes, "
              "spread over dimensions, computed from indicators, and returned "
              "as one score. Every figure below is counted from the framework "
              "file, not written by hand.",
        "fr": "De gauche à droite : l'indice se définit par trois attributs, "
              "se déploie en dimensions, se calcule sur des indicateurs, et "
              "se rend en un score. Chaque chiffre ci-dessous est compté dans "
              "le fichier du référentiel, non écrit à la main."},
    "cad_ap_1": {"en": "attributes", "fr": "attributs"},
    "cad_ap_2": {"en": "dimensions", "fr": "dimensions"},
    "cad_ap_3": {"en": "indicators", "fr": "indicateurs"},
    "cad_ap_3x": {"en": "{f} scored to date", "fr": "{f} scorés à ce jour"},
    "cad_ap_4": {"en": "score", "fr": "score"},
    "cad_ap_4x": {"en": "0 = most critical, 10 = most favourable",
                  "fr": "0 = le plus critique, 10 = le plus favorable"},
    "cad_ap_1x": {"en": "anticipate · absorb · adapt",
                  "fr": "anticiper · absorber · s'adapter"},
    "cad_ap_2x": {"en": "{s} carrying a computed indicator",
                  "fr": "{s} portant un indicateur calculé"},

    # ================= les trois sources =====================================
    "cad_src": {"en": "How the index is built", "fr": "Comment l'indice est construit"},
    "cad_src_note": {
        "en": "Three sources, each answering what the others cannot reach. "
              "A single one would leave a blind spot.",
        "fr": "Trois sources, chacune répondant là où les autres n'atteignent "
              "pas. Une seule laisserait un angle mort."},
    "cad_src1_t": {"en": "Household survey", "fr": "Enquête ménage"},
    "cad_src1": {"en": "What families live through: water, energy, income, "
                       "food, health, mutual aid.",
                 "fr": "Ce que vivent les familles : eau, énergie, revenus, "
                       "alimentation, santé, entraide."},
    "cad_src1_c": {"en": "{n} questionnaires", "fr": "{n} questionnaires"},
    "cad_src2_t": {"en": "Geospatial data", "fr": "Données géospatiales"},
    "cad_src2": {"en": "What no questionnaire can see: forest cover, rainfall, "
                       "vegetation, surface temperature, aridity.",
                 "fr": "Ce qu'aucun questionnaire ne voit : couvert forestier, "
                       "pluie, végétation, température de surface, aridité."},
    "cad_src2_c": {"en": "25 years of imagery", "fr": "25 ans d'imagerie"},
    "cad_src3_t": {"en": "Community-based assessment",
                   "fr": "Évaluation communautaire"},
    "cad_src3": {"en": "What holds the territory together: the base "
                       "organisations, their reach and their capacity to act.",
                 "fr": "Ce qui tient le territoire : les organisations de "
                       "base, leur portée et leur capacité d'action."},
    "cad_src3_c": {"en": "{n} organisations surveyed",
                   "fr": "{n} organisations recensées"},

    # ================= les volets repliés ====================================
    "cad_v_pourquoi": {"en": "Why APRI?", "fr": "Pourquoi APRI ?"},
    "cad_v_mesure": {"en": "What exactly does APRI measure?",
                     "fr": "Que mesure exactement APRI ?"},
    "cad_v_dims": {"en": "The seven dimensions, and what each weighs",
                   "fr": "Les sept dimensions, et ce que chacune pèse"},
    "cad_v_meth": {"en": "Data sources and methodology",
                   "fr": "Sources de données et méthodologie"},
    "cad_v_limites": {"en": "What APRI cannot tell us",
                      "fr": "Ce qu'APRI ne peut pas dire"},
    "cad_v_boucles": {"en": "The second strand — causal loop diagrams",
                      "fr": "Le second volet — les diagrammes de boucles causales"},
    "cad_strate2": {"en": "Explore", "fr": "Explorer"},
    "cad_strate3": {"en": "Go deeper", "fr": "Approfondir"},
    "cad_strate3_note": {
        "en": "Nothing has been removed: the full method is here, folded. "
              "Open only what you need.",
        "fr": "Rien n'a été retiré : la méthode complète est ici, repliée. "
              "N'ouvrez que ce dont vous avez besoin."},

    "cad_doc": {"en": "The full methodological document",
                "fr": "Le document méthodologique complet"},
    "cad_doc_note": {
        "en": "Everything above, in full prose, with the sources and the "
              "detail of each choice.",
        "fr": "Tout ce qui précède, en texte suivi, avec les sources et le "
              "détail de chaque choix."},
}

for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _fmt(v, dec=1):
    if v is None:
        return "—"
    return f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")


def _trouver(nom):
    for c in (os.path.join(DATA, nom), os.path.join(APP_DIR, nom)):
        if os.path.exists(c):
            return c
    return None


@st.cache_data(show_spinner=False)
def _stats():
    """Poids, couverture et effectif de chaque dimension, calculés.

    Rien n'est écrit en dur : si un indicateur est calculé demain, la page le
    dit d'elle-même.
    """
    p = _trouver("resultats.json")
    if not p:
        return None
    with open(p, encoding="utf-8") as f:
        res = json.load(f)
    res = res["indicateurs"] if isinstance(res, dict) and "indicateurs" in res \
        else res
    st_ = {}
    for r in res:
        cle = DIM_CLE.get(r.get("dimension", ""))
        if not cle:
            continue
        e = st_.setdefault(cle, {"n": 0, "faits": 0, "poids": 0.0,
                                 "poids_faits": 0.0})
        poids = r.get("ponderation") or 1
        e["n"] += 1
        e["poids"] += poids
        if (r.get("scores_corriges") or {}).get("Total") is not None:
            e["faits"] += 1
            e["poids_faits"] += poids
    total = sum(e["poids"] for e in st_.values()) or 1
    for e in st_.values():
        e["part"] = 100 * e["poids"] / total
        e["couv"] = 100 * e["poids_faits"] / e["poids"] if e["poids"] else 0
    return {"dims": st_, "poids_total": total,
            "n": sum(e["n"] for e in st_.values()),
            "faits": sum(e["faits"] for e in st_.values())}


@st.cache_data(show_spinner=False)
def _menages():
    """Nombre de questionnaires, et nombre de sections communales.

    MÊME RÈGLE QUE LA PAGE D'ACCUEIL, et il faut qu'elle le reste : deux
    chiffres différents pour la même chose, à deux endroits du même site,
    ruinent la confiance plus sûrement qu'un chiffre absent.

    La somme des effectifs par section donne 1 206 — les questionnaires
    rattachés à une section. Le total collecté est de 1 211. On prend donc le
    maximum des effectifs de ligne, borné par cette somme majorée de 10 % :
    au-dessus, la ligne compte des individus (la ligne 24 compte 2 700
    enfants), pas des ménages.
    """
    pv, pr = _trouver("ventilation.json"), _trouver("resultats.json")
    if not pv:
        return None, None
    with open(pv, encoding="utf-8") as f:
        eff = (json.load(f) or {}).get("effectifs") or {}
    rattaches = sum((d or {}).get("Total") or 0 for d in eff.values())
    n_sections = len(eff) or None
    if not rattaches or not pr:
        return rattaches or None, n_sections
    with open(pr, encoding="utf-8") as f:
        res = json.load(f)
    res = res["indicateurs"] if isinstance(res, dict) and "indicateurs" in res \
        else res
    plafond = rattaches * 1.1
    plausibles = [n for n in ((r.get("n") or {}).get("Total") for r in res)
                  if n and n <= plafond]
    return (max(plausibles) if plausibles else rattaches), n_sections


STYLE = """
<style>
  .cad-h    { font-size:19px; font-weight:700; color:#101728;
              letter-spacing:-.015em; margin:0 0 3px; }
  .cad-note { font-size:13.5px; color:#6b7590; line-height:1.55;
              max-width:96ch; margin:0 0 14px; }
  .cad-grille { display:flex; gap:14px; flex-wrap:wrap; }
  .cad-carte  { flex:1 1 250px; min-width:230px; background:#fff;
                border:1px solid #e3eaf3; border-radius:14px;
                padding:15px 17px; box-shadow:0 1px 2px rgba(16,23,40,.05); }
  .cad-carte-t{ font-size:12px; letter-spacing:.07em; text-transform:uppercase;
                font-weight:700; margin:0 0 6px; }
  .cad-carte-x{ font-size:14.5px; color:#3c4761; line-height:1.55; margin:0; }
  .cad-chiffre{ font-size:31px; font-weight:700; color:#101728;
                letter-spacing:-.03em; font-variant-numeric:tabular-nums;
                line-height:1; }
  .cad-lab    { font-size:13.5px; color:#3c4761; font-weight:600;
                margin-top:5px; }
  .cad-sous   { font-size:12px; color:#8a93a5; margin-top:1px; }
  .cad-liste  { margin:0; padding:0; list-style:none; }
  .cad-liste li { font-size:14px; color:#3c4761; line-height:1.5;
                  padding:6px 0 6px 16px; position:relative; }
  .cad-liste li::before { content:""; position:absolute; left:0; top:13px;
                  width:6px; height:6px; border-radius:50%; background:#c3ccda; }

  /* --- STRATE 1 : les quatre cartouches de tête ------------------------- */
  /* LES QUATRE CARTES TIENNENT SUR UNE RANGÉE, ET C'EST LA CONDITION DE
     LEUR LECTURE : la quatrième dit ce que l'indice NE mesure PAS, et
     renvoyée seule à la ligne suivante elle se lisait comme une note de bas
     de page. À 235 px de base elles débordaient de douze pixels. */
  .cad-n    { flex:1 1 200px; min-width:186px; background:#fff;
              border:1px solid #e3eaf3; border-radius:14px; padding:16px 18px;
              box-shadow:0 1px 2px rgba(16,23,40,.05); }
  .cad-n-i  { width:34px; height:34px; border-radius:10px; display:flex;
              align-items:center; justify-content:center; margin-bottom:11px; }
  .cad-n-t  { font-size:14.5px; font-weight:700; color:#101728;
              letter-spacing:-.01em; margin:0 0 5px; line-height:1.25; }
  .cad-n-x  { font-size:13.5px; color:#3c4761; line-height:1.55; margin:0; }

  /* --- le schéma d'ensemble --------------------------------------------- */
  .cad-flux { display:flex; align-items:stretch; gap:4px; flex-wrap:wrap; }
  .cad-fl   { flex:1 1 150px; min-width:132px; text-align:center;
              padding:13px 10px; border:1px solid #e3eaf3; border-radius:13px;
              background:#fff; }
  .cad-fl-n { font-size:26px; font-weight:700; color:#101728; line-height:1;
              letter-spacing:-.03em; font-variant-numeric:tabular-nums; }
  .cad-fl-l { font-size:12.5px; font-weight:700; color:#3c4761; margin-top:5px;
              letter-spacing:.02em; }
  .cad-fl-x { font-size:11.5px; color:#8a93a5; margin-top:3px; line-height:1.4; }
  .cad-fl-c { align-self:center; color:#c3ccda; font-size:20px; flex:0 0 auto; }

  /* --- les trois sources ------------------------------------------------- */
  .cad-src  { flex:1 1 260px; min-width:230px; background:#fff;
              border:1px solid #e3eaf3; border-radius:14px; padding:15px 17px;
              position:relative; }
  .cad-src-c{ font-size:11.5px; font-weight:700; letter-spacing:.06em;
              text-transform:uppercase; }
  .cad-etage{ font-size:11px; letter-spacing:.11em; text-transform:uppercase;
              font-weight:700; color:#a7b0be; margin:26px 0 8px; }
  /* LA JUSTIFICATION EST ANNULÉE DANS LES CARTES. La feuille de style du site
     justifie tous les paragraphes : c'est bon pour une colonne de texte, et
     cela défigure une carte de deux lignes — les mots s'écartent jusqu'à
     laisser des couloirs blancs au milieu. */
  .cad-n-t, .cad-n-x, .cad-carte-x, .cad-liste li { text-align:left !important; }
  .cad-fl-n, .cad-fl-l, .cad-fl-x { text-align:center !important; }
</style>
"""


def _schema_boucles():
    """Les deux types de boucle, dessinés — la convention de Sterman.

    Deux cercles accolés, chacun portant sa lettre : R pour le renforcement,
    B pour l'amortissement. Les polarités sont posées sur les liens, parce que
    c'est leur produit qui décide du type — un schéma qui montrerait les
    cercles sans les signes ne servirait à rien.
    """
    return """<svg viewBox="0 0 360 190" width="100%" style="max-width:360px"
     font-family="Inter,system-ui,sans-serif">
  <circle cx="108" cy="95" r="56" fill="none" stroke="#1a8a4f"
          stroke-width="2"/>
  <circle cx="248" cy="95" r="56" fill="none" stroke="#d1730c"
          stroke-width="2"/>
  <path d="M96 66 a20 20 0 1 1 24 0" fill="none" stroke="#1a8a4f"
        stroke-width="1.6" marker-end="url(#fr)"/>
  <path d="M236 124 a20 20 0 1 0 24 0" fill="none" stroke="#d1730c"
        stroke-width="1.6" marker-end="url(#fa)"/>
  <defs>
    <marker id="fr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5"
            markerHeight="5" orient="auto-start-reverse">
      <path d="M0 0 L10 5 L0 10 z" fill="#1a8a4f"/></marker>
    <marker id="fa" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5"
            markerHeight="5" orient="auto-start-reverse">
      <path d="M0 0 L10 5 L0 10 z" fill="#d1730c"/></marker>
  </defs>
  <text x="108" y="101" text-anchor="middle" font-size="26" font-weight="700"
        fill="#1a8a4f">R</text>
  <text x="248" y="101" text-anchor="middle" font-size="26" font-weight="700"
        fill="#d1730c">B</text>
  <circle cx="46" cy="95" r="13" fill="#fff" stroke="#101728"
          stroke-width="1.6"/>
  <text x="46" y="100" text-anchor="middle" font-size="13"
        font-weight="700" fill="#101728">A</text>
  <circle cx="178" cy="95" r="13" fill="#fff" stroke="#101728"
          stroke-width="1.6"/>
  <text x="178" y="100" text-anchor="middle" font-size="13"
        font-weight="700" fill="#101728">B</text>
  <circle cx="310" cy="95" r="13" fill="#fff" stroke="#101728"
          stroke-width="1.6"/>
  <text x="310" y="100" text-anchor="middle" font-size="13"
        font-weight="700" fill="#101728">C</text>
  <text x="118" y="30" text-anchor="middle" font-size="15" font-weight="700"
        fill="#1a8a4f">+</text>
  <text x="238" y="30" text-anchor="middle" font-size="15" font-weight="700"
        fill="#d1730c">&#8722;</text>
  <text x="300" y="168" text-anchor="middle" font-size="15" font-weight="700"
        fill="#d1730c">+</text>
  <text x="56" y="168" text-anchor="middle" font-size="15" font-weight="700"
        fill="#1a8a4f">+</text>
  <text x="180" y="182" text-anchor="middle" font-size="10.5" fill="#6b7590">
    Sterman, 2000</text>
</svg>"""


def _cartouche(titre, texte, couleur):
    return (f'<div class="cad-carte" style="border-top:3px solid {couleur}">'
            f'<div class="cad-carte-t" style="color:{couleur}">{_e(titre)}</div>'
            f'<p class="cad-carte-x">{_e(texte)}</p></div>')


def _tableau_dimensions(stats):
    """Une ligne par dimension : pastille, nom, poids, couverture, effectif.

    DEUX GRANDEURS, DEUX COLONNES, JAMAIS SUPERPOSÉES. Le poids et la
    couverture ne se comparent pas entre eux — l'un est une part de l'indice,
    l'autre un état d'avancement. Les mettre sur la même barre laisserait
    croire à un rapport qui n'existe pas.

    Chaque barre est en teinte unique : il n'y a qu'une grandeur par colonne,
    et la couleur de la dimension appartient à sa pastille, pas à la mesure.
    """
    pmax = max(e["part"] for e in stats["dims"].values()) or 1
    lignes = []
    for cle in ORDRE:
        e = stats["dims"].get(cle)
        if not e:
            continue
        c = TEINTES[cle]
        vide = e["faits"] == 0
        lignes.append(
            f'<div style="display:grid;'
            f'grid-template-columns:14px minmax(150px,2.6fr) 3fr 62px 2fr 52px 74px;'
            f'gap:11px;align-items:center;padding:9px 0;'
            f'border-bottom:1px solid #eef2f7">'
            # pastille d'identité — jamais seule, le nom la suit
            f'<div style="width:11px;height:11px;border-radius:3px;'
            f'background:{c};{"opacity:.35" if vide else ""}"></div>'
            f'<div style="font-size:14px;font-weight:600;color:{ENCRE};'
            f'line-height:1.3">{_e(T(cle))}</div>'
            # poids
            f'<div style="background:{GRIS};border-radius:5px;height:15px;'
            f'overflow:hidden"><div style="height:100%;border-radius:5px;'
            f'width:{max(100 * e["part"] / pmax, 1.2):.1f}%;'
            f'background:#2166ac;{"opacity:.45" if vide else ""}"></div></div>'
            f'<div style="font-size:13.5px;font-weight:600;color:{ENCRE};'
            f'text-align:right;font-variant-numeric:tabular-nums">'
            f'{_fmt(e["part"])}&thinsp;%</div>'
            # couverture
            f'<div style="background:{GRIS};border-radius:5px;height:15px;'
            f'overflow:hidden"><div style="height:100%;border-radius:5px;'
            f'width:{max(e["couv"], 0.8):.1f}%;background:#1a8a4f"></div></div>'
            f'<div style="font-size:13.5px;color:{ENCRE2};text-align:right;'
            f'font-variant-numeric:tabular-nums">{_fmt(e["couv"], 0)}&thinsp;%</div>'
            f'<div style="font-size:13px;color:{ENCRE3};text-align:right;'
            f'font-variant-numeric:tabular-nums">{e["faits"]}/{e["n"]}</div>'
            f'</div>')
    entete = (
        f'<div style="display:grid;'
        f'grid-template-columns:14px minmax(150px,2.6fr) 3fr 62px 2fr 52px 74px;'
        f'gap:11px;padding:0 0 6px;font-size:11px;letter-spacing:.09em;'
        f'text-transform:uppercase;color:#8a93a5;font-weight:700">'
        f'<div></div><div>{_e(T("cad_col_dim"))}</div>'
        f'<div style="grid-column:span 2">{_e(T("cad_col_poids"))}</div>'
        f'<div style="grid-column:span 2">{_e(T("cad_col_couv"))}</div>'
        f'<div style="text-align:right">{_e(T("cad_col_ind"))}</div></div>')
    return entete + "".join(lignes)


def _chaine(ptot):
    """La chaîne de calcul, quatre étapes reliées par des chevrons.

    Un schéma plutôt qu'un paragraphe : l'ordre des opérations est ce qui
    compte, et un ordre se montre.
    """
    etapes = [("cad_e1", {}), ("cad_e2", {}),
              ("cad_e3", {"ptot": _fmt(ptot, 0)}), ("cad_e4", {})]
    blocs = []
    for i, (cle, kw) in enumerate(etapes):
        if i:
            blocs.append(
                '<div style="align-self:center;color:#c3ccda;font-size:22px;'
                'flex:0 0 auto;padding:0 2px">›</div>')
        blocs.append(
            f'<div style="flex:1 1 190px;min-width:175px;background:#fff;'
            f'border:1px solid {BORD};border-radius:13px;padding:13px 15px">'
            f'<div style="font-size:12px;letter-spacing:.06em;'
            f'text-transform:uppercase;font-weight:700;color:#2166ac">'
            f'{_e(T(cle + "_t"))}</div>'
            f'<div style="font-size:13.5px;color:{ENCRE2};line-height:1.5;'
            f'margin-top:5px">{_e(T(cle, **kw))}</div></div>')
    return ('<div style="display:flex;gap:6px;flex-wrap:wrap;'
            'align-items:stretch">' + "".join(blocs) + '</div>')


def _chiffre(val, lab, sous):
    return (f'<div class="cad-carte" style="flex:1 1 190px;min-width:165px">'
            f'<div class="cad-chiffre">{_e(val)}</div>'
            f'<div class="cad-lab">{_e(lab)}</div>'
            f'<div class="cad-sous">{_e(sous)}</div></div>')


def _icone(nom, couleur):
    return (f'<div class="cad-n-i" style="background:{couleur}17;color:{couleur}">'
            + icones.svg(nom, couleur=couleur, taille=19) + '</div>')


def _tete(stats, n_sec_avec):
    """STRATE 1 — quatre cartouches, et rien d'autre à lire.

    LES QUATRE QUESTIONS SONT CELLES QU'ON POSE DANS CET ORDRE : ce que
    l'indice mesure, ce qu'il saisit, comment il le mesure, et — la plus
    utile — ce qu'il ne mesure pas. La quatrième est traitée comme les trois
    autres, en carte pleine et non en note de bas de page : une limite qu'on
    lit après coup n'a jamais empêché personne de se tromper.
    """
    n = [("cad_n1", "cible", "#2166ac", {}),
         ("cad_n2", "bouclier", "#1a8a4f", {"n": len(stats["dims"])}),
         ("cad_n3", "barres", "#d1730c", {"i": stats["n"]}),
         ("cad_n4", "info", "#8a93a5", {})]
    fond = ' style="background:#fafbfd"'
    return ('<div class="cad-grille" style="margin:14px 0 2px">' + "".join(
        '<div class="cad-n"' + (fond if k == "cad_n4" else "") + '>'
        + _icone(ic, c)
        + f'<p class="cad-n-t">{_e(T(k + "_t"))}</p>'
        + f'<p class="cad-n-x">{_e(T(k, **kw))}</p></div>'
        for k, ic, c, kw in n) + '</div>')


def _apercu(stats, n_sec_avec):
    """Le schéma d'ensemble : APRI → attributs → dimensions → indicateurs → score.

    Quatre pavés chiffrés reliés par des chevrons. Les chiffres viennent du
    référentiel : sept dimensions parce qu'il en compte sept, cent vingt-huit
    indicateurs parce qu'il en liste cent vingt-huit. Un schéma de méthode qui
    annoncerait un compte faux se retournerait contre la méthode.
    """
    cases = [("3", T("cad_ap_1"), T("cad_ap_1x")),
             (str(len(stats["dims"])), T("cad_ap_2"),
              T("cad_ap_2x", s=n_sec_avec)),
             (str(stats["n"]), T("cad_ap_3"),
              T("cad_ap_3x", f=stats["faits"])),
             ("0–10", T("cad_ap_4"), T("cad_ap_4x"))]
    blocs = []
    for i, (v, lab, sous) in enumerate(cases):
        if i:
            blocs.append('<div class="cad-fl-c">&rsaquo;</div>')
        blocs.append(f'<div class="cad-fl"><div class="cad-fl-n">{_e(v)}</div>'
                     f'<div class="cad-fl-l">{_e(lab)}</div>'
                     f'<div class="cad-fl-x">{_e(sous)}</div></div>')
    return '<div class="cad-flux">' + "".join(blocs) + '</div>'


def _attributs():
    """Les trois attributs, en cartes égales — c'est la définition d'APRI."""
    return ('<div class="cad-grille">' + "".join(
        f'<div class="cad-n" style="flex:1 1 240px;border-top:3px solid {c}">'
        + _icone(ic, c)
        + f'<p class="cad-n-t" style="font-size:16px">{_e(T(k + "_t"))}</p>'
        + f'<p class="cad-n-x">{_e(T(k))}</p></div>'
        for k, ic, c in (("cad_a1", "loupe", "#2166ac"),
                         ("cad_a2", "bouclier", "#d1730c"),
                         ("cad_a3", "rafraichir", "#1a8a4f")))
        + '</div>')


def _sources(menages, n_ocb):
    """Les trois sources, en parcours : enquête → satellite → communautés."""
    src = [("cad_src1", "personnes", "#2166ac",
            T("cad_src1_c", n=_fmt(menages, 0)) if menages else ""),
           ("cad_src2", "carte", "#1a8a4f", T("cad_src2_c")),
           ("cad_src3", "maison", "#d1730c",
            T("cad_src3_c", n=n_ocb) if n_ocb else "")]
    blocs = []
    for i, (k, ic, c, chiffre) in enumerate(src):
        if i:
            blocs.append('<div class="cad-fl-c" style="align-self:center">'
                         '&rsaquo;</div>')
        blocs.append(
            f'<div class="cad-src" style="border-top:3px solid {c}">'
            + _icone(ic, c)
            + f'<p class="cad-n-t">{_e(T(k + "_t"))}</p>'
            + f'<p class="cad-n-x">{_e(T(k))}</p>'
            + (f'<div class="cad-src-c" style="color:{c};margin-top:9px">'
               f'{_e(chiffre)}</div>' if chiffre else "")
            + '</div>')
    return ('<div class="cad-flux" style="align-items:stretch">'
            + "".join(blocs) + '</div>')


def _n_ocb():
    p = _trouver("ocb.json")
    if not p:
        return None
    try:
        with open(p, encoding="utf-8") as f:
            return len(json.load(f).get("fiches") or [])
    except Exception:
        return None


def render(doc_complet=None):
    """La page en trois strates : comprendre, explorer, approfondir.

    POURQUOI TROIS STRATES, ET PAS UN TEXTE MIEUX ÉCRIT.
    La version précédente disait les mêmes choses, toutes à la fois, en huit
    blocs dépliés. Le contenu était juste et personne ne le lisait : sur un
    tableau de bord, un mur de prose se saute. Ce qui a changé n'est donc pas
    le fond mais la PROFONDEUR — quatre cartes et deux schémas pour
    comprendre en trente secondes, deux blocs pour explorer, six volets
    repliés pour la méthode. Rien n'a été supprimé : tout ce qui était visible
    est encore là, un cran plus bas.
    """
    stats = _stats()
    st.markdown(STYLE, unsafe_allow_html=True)

    st.markdown(
        f'<h2 style="font-size:27px;font-weight:700;color:{ENCRE};'
        f'letter-spacing:-.02em;margin:2px 0 0">{T("cad_titre")}</h2>'
        f'<p style="font-size:12.5px;color:{ENCRE3};letter-spacing:.06em;'
        f'text-transform:uppercase;margin:2px 0 0;font-weight:600">'
        f'{T("cad_sous_titre")}</p>', unsafe_allow_html=True)

    if not stats:
        st.info(T("e_absent"))
        return

    # DEUX ONGLETS, ET LE SECOND N'EST PAS UN SUPPLÉMENT.
    # La dimension environnementale est la seule qui ne se mesure pas en
    # interrogeant des ménages : elle demande des transects, des images
    # satellitaires et des barèmes qui leur sont propres. Fondue dans la page
    # générale, elle y aurait tenu six lignes ; à part, elle garde son
    # protocole entier.
    _ong_apri, _ong_env = st.tabs(
        [T("env_onglet_apri"), T("env_onglet")])
    with _ong_env:
        environnement_cadre.render()
    with _ong_apri:
        _cadre_apri(stats, doc_complet)


def _cadre_apri(stats, doc_complet):
    """L'onglet du cadre général, en trois strates : comprendre, explorer,
    approfondir. Détaché de `render()` pour tenir dans un onglet."""
    menages, n_sections = _menages()
    n_ocb = _n_ocb()
    n_sec_avec = sum(1 for e in stats["dims"].values() if e["faits"])

    # ================= STRATE 1 — COMPRENDRE ==============================
    st.markdown(_tete(stats, n_sec_avec), unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f'<div class="cad-h">{_e(T("cad_apercu"))}</div>'
                    f'<p class="cad-note">{_e(T("cad_ap_note"))}</p>'
                    + _apercu(stats, n_sec_avec), unsafe_allow_html=True)
        st.markdown(f'<div class="cad-h" style="font-size:15px;'
                    f'margin:22px 0 4px">{_e(T("cad_aaa"))}</div>'
                    f'<p class="cad-note" style="margin-bottom:11px">'
                    f'{_e(T("cad_aaa_note"))}</p>' + _attributs(),
                    unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f'<div class="cad-h">{_e(T("cad_src"))}</div>'
                    f'<p class="cad-note">{_e(T("cad_src_note"))}</p>'
                    + _sources(menages, n_ocb), unsafe_allow_html=True)

    # ================= STRATE 2 — EXPLORER ================================
    st.markdown(f'<div class="cad-etage">{_e(T("cad_strate2"))}</div>',
                unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(
            f'<div class="cad-h">{_e(T("cad_dims"))}</div>'
            f'<p class="cad-note">{_e(T("cad_dims_note"))}</p>'
            + _tableau_dimensions(stats), unsafe_allow_html=True)
        st.caption(T("cad_dim7_note"))

    with st.container(border=True):
        st.markdown(f'<div class="cad-h" style="margin-bottom:11px">'
                    f'{_e(T("cad_chaine"))}</div>' + _chaine(stats["poids_total"]),
                    unsafe_allow_html=True)

    # ================= STRATE 3 — APPROFONDIR =============================
    # TOUT CE QUI SUIT ÉTAIT DÉPLIÉ, ET C'ÉTAIT LÀ LE DÉFAUT. Rien n'en a été
    # retiré : le récit d'origine, la portée, le plan de sondage, les limites,
    # le second volet et le document complet sont intacts, mais fermés. Une
    # information qu'on doit ouvrir se lit mieux qu'une information qu'on doit
    # sauter.
    st.markdown(f'<div class="cad-etage">{_e(T("cad_strate3"))}</div>'
                f'<p class="cad-note" style="margin-top:-4px">'
                f'{_e(T("cad_strate3_note"))}</p>', unsafe_allow_html=True)

    with st.expander(T("cad_v_pourquoi")):
        st.markdown(
            "".join(
                f'<p style="font-size:15px;color:#3c4761;line-height:1.65;'
                f'max-width:92ch;margin:0 0 14px"><b style="color:#101728">'
                f'{T("a_h_" + c + "_t")}</b> {T("a_h_" + c)}</p>'
                for c in ("origine", "portee")), unsafe_allow_html=True)

    with st.expander(T("cad_v_mesure")):
        st.markdown(
            f'<p style="font-size:15px;color:#3c4761;line-height:1.65;'
            f'max-width:92ch;margin:0 0 16px"><b style="color:#101728">'
            f'{T("a_h_mesure_t")}</b> {T("a_h_mesure")}</p>'
            '<div class="cad-grille">'
            + _cartouche(T("cad_quoi_t"), T("cad_quoi"), "#2166ac")
            + _cartouche(T("cad_quand_t"), T("cad_quand"), "#1a8a4f")
            + _cartouche(T("cad_echelle_t"), T("cad_echelle"), "#d1730c")
            + '</div>', unsafe_allow_html=True)

    with st.expander(T("cad_v_meth")):
        st.markdown(
            f'<p style="font-size:15px;color:#3c4761;line-height:1.65;'
            f'max-width:92ch;margin:0 0 16px"><b style="color:#101728">'
            f'{T("a_h_construction_t")}</b> {T("a_h_construction")}</p>'
            f'<div class="cad-h" style="font-size:15px;margin-bottom:11px">'
            f'{_e(T("cad_sondage"))}</div>'
            '<div class="cad-grille">'
            + _chiffre(_fmt(menages, 0) if menages else "—",
                       T("cad_s1_t"), T("cad_s1"))
            + _chiffre(str(n_sections or "—"), T("cad_s2_t"), T("cad_s2"))
            + _chiffre("90 %", T("cad_s3_t"), T("cad_s3"))
            + _chiffre("120", T("cad_s4_t"), T("cad_s4"))
            + '</div>'
            f'<div class="cad-h" style="font-size:15px;margin:18px 0 4px">'
            f'{_e(T("cad_strates"))}</div>'
            '<ul class="cad-liste">'
            + "".join(f'<li>{_e(T(k))}</li>'
                      for k in ("cad_st1", "cad_st2", "cad_st3", "cad_st4"))
            + '</ul>', unsafe_allow_html=True)
        st.caption(T("cad_tirage"))

    with st.expander(T("cad_v_limites")):
        st.markdown(
            '<div class="cad-grille">'
            + "".join(_cartouche(T(k + "_t"), T(k), "#8a93a5")
                      for k in ("cad_l1", "cad_l2", "cad_l3", "cad_l4"))
            + '</div>', unsafe_allow_html=True)

    with st.expander(T("cad_v_boucles")):
        st.markdown(
            f'<p class="cad-note" style="max-width:92ch">{_e(T("cad_dbc_x"))}</p>'
            '<div class="cad-grille">'
            + "".join(
                f'<div style="flex:1 1 220px;min-width:200px;'
                f'border-left:3px solid {c};padding:2px 0 2px 14px">'
                f'<div style="font-size:14.5px;font-weight:700;color:{ENCRE}">'
                f'{_e(T(k + "_t"))}</div>'
                f'<div style="font-size:13px;color:{ENCRE2};line-height:1.5;'
                f'margin-top:3px">{_e(T(k))}</div></div>'
                for k, c in (("cad_dbc_1", "#c33a24"), ("cad_dbc_2", "#d1730c"),
                             ("cad_dbc_3", "#2166ac"), ("cad_dbc_4", "#1a8a4f")))
            + '</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="cad-h" style="font-size:15px;'
                    f'margin:20px 0 6px">{_e(T("cad_lecture"))}</div>',
                    unsafe_allow_html=True)
        g, d = st.columns([1.15, 1])
        with g:
            st.markdown(T("cad_lecture_x"))
            st.warning(T("cad_lecture_piege"))
        with d:
            st.markdown(_schema_boucles(), unsafe_allow_html=True)
        st.caption(T("cad_dbc_lien"))

    if doc_complet is not None:
        with st.expander(T("cad_doc")):
            st.caption(T("cad_doc_note"))
            doc_complet()
