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
from urllib.parse import quote

import streamlit as st

import environnement_cadre
import trajectoires
import i18n
import onglets
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
# LE VERT DU SITE, ET LUI SEUL. La page portait quatre couleurs — bleu,
# orange, vert, plus les sept teintes de dimension. Aucune ne disait rien :
# c'étaient des couleurs de rangement, pas de sens. Une seule reste.
VERT_APRI = "#2a6b3f"

# ---------------------------------------------------------------------------
# Les textes voyagent avec le module : une page nouvelle ne doit pas dépendre
# d'un i18n.py envoyé séparément pour s'afficher. Ils sont versés dans le
# dictionnaire commun à l'import, sans écraser une clé déjà présente.
# ---------------------------------------------------------------------------
TEXTES = {
    "cad_titre": {"en": "Resilience Framework",
                  "fr": "Cadre de résilience"},

    # La ligne de description de chaque onglet, sous son titre.
    "cad_d1": {"en": "The three capacities the index is built on",
               "fr": "Les trois capacités sur lesquelles l'indice est bâti"},
    "cad_d2": {"en": "The four instruments the measurements come from",
               "fr": "Les quatre instruments dont viennent les mesures"},
    "cad_d3": {"en": "The seven dimensions and their weights",
               "fr": "Les sept dimensions et leurs pondérations"},
    "cad_d4": {"en": "How a raw measurement becomes a score out of 10",
               "fr": "Comment une mesure brute devient un score sur 10"},
    "cad_d5": {"en": "Why resilience is read as a system, not a list",
               "fr": "Pourquoi la résilience se lit comme un système, pas "
                     "comme une liste"},
    "cad_d6": {"en": "What a satellite measures, and what it cannot",
               "fr": "Ce qu'un satellite mesure, et ce qu'il ne peut pas"},
    "cad_d7": {"en": "The methodological document, in full",
               "fr": "Le document méthodologique, en entier"},

    # --- les trois cartouches d'ouverture
    "cad_quoi_t": {"en": "General resilience", "fr": "Résilience générale"},
    "cad_quoi": {
        "en": "The capacity to anticipate, absorb and adapt to multiple "
              "disturbances, not the response to one hazard.",
        "fr": "La capacité d'anticiper, d'absorber et de s'adapter à des "
              "perturbations multiples, pas la réponse à un aléa unique."},
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

    # --- LA PHRASE QUI OUVRE LE PREMIER ONGLET
    # --- le cadre AAA
    # L'INTITULÉ DIT CE QU'ON MESURE, PAS COMMENT C'EST RANGÉ. « Trois
    # attributs, lus sur chaque dimension » décrivait la structure du
    # référentiel ; la ligne de dessous ajoutait qu'un indicateur est rattaché
    # à l'attribut auquel il contribue — deux phrases de méthode, à l'endroit
    # où le lecteur cherche l'objet de la mesure. Il est dit en une ligne.
    "cad_aaa": {"en": "What is measured is the capacity to attain three "
                      "attributes",
                "fr": "Ce que l'on mesure, c'est la capacité à atteindre "
                      "trois attributs"},
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
              "computed to date, an uncomputed indicator is excluded from "
              "the mean, never counted as a zero.",
        "fr": "Le poids est la part de l'indice composite que porte chaque "
              "dimension. La couverture est la part de ce poids réellement "
              "calculée à ce jour, un indicateur non calculé est exclu de la "
              "moyenne, jamais compté comme un zéro."},
    "cad_col_dim": {"en": "Dimension", "fr": "Dimension"},
    "cad_col_poids": {"en": "Weight in the index", "fr": "Poids dans l'indice"},
    "cad_col_couv": {"en": "Coverage", "fr": "Couverture"},
    "cad_col_ind": {"en": "Indicators", "fr": "Indicateurs"},
    "cad_dim7_note": {
        "en": "The seventh dimension, cultural, identity-based and "
              "psychological, has no computed indicator to date. It is shown "
              "here so that an absence is not mistaken for a non-existence.",
        "fr": "La septième dimension, culturelle, identitaire et "
              "psychologique, n'a aucun indicateur calculé à ce jour. Elle "
              "figure ici pour qu'une absence ne passe pas pour une "
              "inexistence."},

    # --- LA MÉTHODE DE CALCUL, EN TROIS TEMPS
    # LES NOMBRES DE L'EXEMPLE SONT UN EXEMPLE, et l'onglet le dit. Quarante-
    # cinq minutes pour aller chercher l'eau, 3,5 sur 10, 6,1 en score global :
    # ce sont des valeurs de démonstration choisies pour que la chaîne se
    # suive. Publiées sans mention, elles se liraient comme des résultats —
    # et le score global réel n'est pas 6,1.
    "cad_ex": {"en": "Example", "fr": "Exemple"},

    "cad_p1_t": {"en": "From a raw measure to an indicator score",
                 "fr": "De la mesure brute au score d'un indicateur"},
    "cad_p1a_t": {"en": "Raw measure", "fr": "Mesure brute"},
    "cad_p1a_v": {"en": "45 min", "fr": "45 min"},
    "cad_p1a_x": {"en": "Time to collect water",
                  "fr": "Temps pour aller chercher l'eau"},
    "cad_p1b_t": {"en": "Direction", "fr": "Sens"},
    "cad_p1b_v": {"en": "Lower is better", "fr": "Moins, c'est mieux"},
    "cad_p1c_t": {"en": "Reference", "fr": "Référence"},
    "cad_p1c_v": {"en": "0 = ≥ 120 min", "fr": "0 = ≥ 120 min"},
    "cad_p1c_x": {"en": "10 = ≤ 15 min", "fr": "10 = ≤ 15 min"},
    "cad_p1d_t": {"en": "Normalisation", "fr": "Normalisation"},
    "cad_p1d_v": {"en": "Score = 3.5 / 10", "fr": "Score = 3,5 / 10"},
    "cad_p1e_t": {"en": "Indicator score", "fr": "Score de l'indicateur"},
    "cad_p1e_v": {"en": "3.5 / 10", "fr": "3,5 / 10"},

    "cad_p2_t": {"en": "Two normalisation methods",
                 "fr": "Deux méthodes de normalisation"},
    "cad_p2s_t": {"en": "Statistical normalisation",
                  "fr": "Normalisation statistique"},
    "cad_p2s_x": {"en": "Used when a continuous distribution of values is "
                        "available.",
                  "fr": "Utilisée quand on dispose d'une distribution "
                        "continue de valeurs."},
    "cad_p2h": {"en": "Higher is better", "fr": "Plus, c'est mieux"},
    "cad_p2l": {"en": "Lower is better", "fr": "Moins, c'est mieux"},
    "cad_p2b_t": {"en": "Threshold-based normalisation",
                  "fr": "Normalisation par seuils"},
    "cad_p2b_x": {"en": "Used when clear benchmarks or standards exist.",
                  "fr": "Utilisée quand il existe des repères ou des normes "
                        "clairs."},
    # Les paliers sont écrits « borne → score », séparés par des barres.
    "cad_p2b_r": {"en": "≥ 120 min→0|60–120 min→2.5|30–60 min→5|"
                        "15–30 min→7.5|≤ 15 min→10",
                  "fr": "≥ 120 min→0|60–120 min→2,5|30–60 min→5|"
                        "15–30 min→7,5|≤ 15 min→10"},
    "cad_p2b_n": {"en": "Thresholds may come from international standards, "
                        "national norms or expert consensus.",
                  "fr": "Les seuils peuvent venir de standards "
                        "internationaux, de normes nationales ou d'un "
                        "consensus d'experts."},

    "cad_p3_t": {"en": "From indicator scores to overall resilience",
                 "fr": "Des scores d'indicateurs à la résilience d'ensemble"},
    "cad_p3a_t": {"en": "Indicator scores", "fr": "Scores des indicateurs"},
    "cad_p3a_x": {"en": "Scores from 0 to 10", "fr": "Des scores de 0 à 10"},
    "cad_p3b_t": {"en": "Dimension score", "fr": "Score de dimension"},
    "cad_p3b_x": {"en": "Indicators within the same dimension are combined",
                  "fr": "Les indicateurs d'une même dimension sont combinés"},
    "cad_p3b_v": {"en": "Dimension score: 6.3 / 10",
                  "fr": "Score de dimension : 6,3 / 10"},
    # LA PONDÉRATION SE FAIT À L'INDICATEUR, PAS À LA DIMENSION. « Chaque
    # dimension est pondérée selon son importance relative » laissait croire
    # à un poids posé sur les sept dimensions ; il n'existe pas. Chaque
    # indicateur porte le sien, fixé par un groupe d'experts, et le poids
    # d'une dimension n'est que la somme de ceux de ses indicateurs —
    # c'est exactement ainsi qu'il est calculé dans le fichier de
    # résultats, et c'est ce que montre le tableau de l'onglet 3.
    "cad_p3c_t": {"en": "Expert weighting", "fr": "Pondération par expertise"},
    "cad_p3c_x": {"en": "Each indicator carries a weight set by a panel of "
                        "experts; a dimension's weight is the sum of its own",
                  "fr": "Chaque indicateur porte une pondération fixée par un "
                        "groupe d'experts ; le poids d'une dimension est la "
                        "somme des siennes"},
    "cad_p3d_t": {"en": "Overall resilience score",
                  "fr": "Score de résilience d'ensemble"},
    "cad_p3d_x": {"en": "Weighted dimension scores are aggregated",
                  "fr": "Les scores pondérés des dimensions sont agrégés"},
    "cad_p3d_v": {"en": "Overall score: 6.1 / 10",
                  "fr": "Score global : 6,1 / 10"},

    "cad_p4_t": {"en": "Why 0–10?", "fr": "Pourquoi 0–10 ?"},
    "cad_p4_x": {"en": "A common scale makes indicators expressed in "
                       "different units comparable and results easier to "
                       "interpret.",
                 "fr": "Une échelle commune rend comparables des indicateurs "
                       "exprimés dans des unités différentes, et les "
                       "résultats plus faciles à interpréter."},
    "cad_p4_lab": {"en": "resilience indicators across {d} dimensions",
                   "fr": "indicateurs de résilience sur {d} dimensions"},

    # --- le plan de sondage
    "cad_s1_t": {"en": "questionnaires", "fr": "questionnaires"},
    "cad_s1": {"en": "collected in 2024", "fr": "collectés en 2024"},
    "cad_s2_t": {"en": "communal sections", "fr": "sections communales"},
    "cad_s2": {"en": "each surveyed in full", "fr": "enquêtées en entier"},
    "cad_s4_t": {"en": "households minimum", "fr": "ménages au minimum"},
    "cad_s4": {"en": "per communal section", "fr": "par section communale"},

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
    "cad_dbc": {"en": "The second strand, causal loop diagrams",
                "fr": "Le second volet, les diagrammes de boucles causales"},
    "cad_dbc_x": {
        "en": "In a socio-ecological system, interactions are not linear: a "
              "cause becomes a consequence, and some effects feed themselves. "
              "Where a problem tree shows the visible chain of causes and "
              "effects, a causal loop diagram shows the internal feedbacks, "
              "why a system persists, degrades, or finds its balance again. "
              "That is the heart of resilience.",
        "fr": "Dans un système socio-écologique, les interactions ne sont pas "
              "linéaires : une cause devient une conséquence, et certains "
              "effets s'auto-renforcent. Là où l'arbre à problèmes montre la "
              "chaîne visible des causes et des effets, le diagramme de "
              "boucles causales montre les rétroactions internes, pourquoi "
              "un système persiste, se dégrade, ou retrouve son équilibre. "
              "C'est le cœur de la résilience."},
    "cad_dbc_1_t": {"en": "1 · The symptom", "fr": "1 · La variable symptôme"},
    "cad_dbc_1": {
        "en": "Start from the indicator in red, falling tree cover, dropping "
              "yields, rising erosion. It is the visible malfunction, and the "
              "entry point for going back up to causes and down to effects.",
        "fr": "Partir de l'indicateur en rouge, recul du couvert végétal, "
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
              "**reinforcing (R)**, it accelerates its own dynamic; an odd "
              "number makes it **balancing (B)**, it pulls the system back "
              "towards a resting point. Simpler still: raise A; if A ends up "
              "higher, the loop is R; if A ends up lower, it is B.",
        "fr": "Chaque flèche porte une polarité. **+** les deux variables "
              "changent dans le même sens ; **−** en sens opposé. On "
              "multiplie les signes le long de la boucle : un nombre pair de "
              "**−** la rend **renforçante (R)**, elle accélère sa propre "
              "dynamique ; un nombre impair la rend **équilibrante (B)**, "
              "elle ramène le système vers un point de repos. Plus simple "
              "encore : j'augmente A ; si A finit plus haut, la boucle est "
              "R ; si A finit plus bas, elle est B."},
    "cad_lecture_piege": {
        "en": "**The trap: « positive » does not mean « good ».** It says the "
              "variables move together. A reinforcing loop pushed upward is a "
              "virtuous spiral (R+); the same loop pushed downward is a "
              "vicious one (R−). And a balancing loop can lock a system into "
              "a degraded state (B−), falling yields drive out-migration, "
              "which eases pressure and lets the forest return, but through "
              "rural collapse.",
        "fr": "**Le piège : « positive » ne veut pas dire « bonne ».** Cela "
              "dit que les variables bougent ensemble. Une boucle renforçante "
              "poussée à la hausse est une spirale vertueuse (R+) ; la même "
              "poussée à la baisse est vicieuse (R−). Et une boucle "
              "équilibrante peut figer le système dans un état dégradé "
              "(B−), la baisse des rendements pousse à la migration, ce qui "
              "allège la pression et laisse la forêt revenir, mais par "
              "effondrement rural."},
    "cad_dbc_lien": {
        "en": "The tool is in the **Feedback Loops** tab: push a lever, watch "
              "the wave travel, isolate a loop.",
        "fr": "L'outil est dans l'onglet **Boucles de rétroaction** : "
              "poussez un levier, suivez l'onde, isolez une boucle."},
    # ================= LES QUATRE SOURCES ====================================
    # ELLES ÉTAIENT TROIS, ELLES SONT QUATRE. Le quatrième volet — les
    # entretiens structurés menés dans chaque paysage auprès des autorités
    # sanitaires, éducatives et politiques communales et des organisations de
    # la société civile — existait dans la collecte et pas sur la page. Une
    # source de données qu'on ne nomme pas est une source qu'on ne peut pas
    # contester : c'est le contraire de ce que fait une page de méthode.
    #
    # LES PUCES SONT UNE SEULE CHAÎNE, séparée par des barres verticales.
    # Seize clés de traduction pour seize puces se désynchronisent à la
    # première relecture ; une chaîne par langue se relit d'un coup.
    "cad_src": {"en": "The data sources", "fr": "Les sources de données"},
    "cad_src_note": {
        "en": "Resilience is measured using multiple, complementary data "
              "sources that capture the condition of households, ecosystems, "
              "institutions and the territories where people live.",
        "fr": "La résilience se mesure à partir de plusieurs sources de "
              "données complémentaires, qui saisissent l'état des ménages, "
              "des écosystèmes, des institutions et des territoires où vivent "
              "les gens."},

    "cad_so1_t": {"en": "Household survey", "fr": "Enquête ménage"},
    "cad_so1_x": {
        "en": "Information collected directly from households on "
              "livelihoods, assets, risk perception, preparedness and access "
              "to services.",
        "fr": "Informations recueillies directement auprès des ménages sur "
              "les moyens d'existence, les biens, la perception du risque, "
              "la préparation et l'accès aux services."},
    "cad_so1_p": {
        "en": "Structured questionnaires|Random draw within strata from a "
              "georeferenced building base (OpenStreetMap)|Four crossed "
              "strata: landscape, age, sex, economic category|"
              "Socio-economic and institutional data|Perceptions and "
              "behaviours",
        "fr": "Questionnaires structurés|Tirage aléatoire dans chaque strate "
              "à partir d'une base de bâtiments géoréférencés "
              "(OpenStreetMap)|Quatre strates croisées : paysage, âge, sexe, "
              "catégorie économique|Données socio-économiques et "
              "institutionnelles|Perceptions et comportements"},
    # LA PHRASE QUI JUSTIFIE L'ABSENCE DE REDRESSEMENT. Elle n'est pas un
    # détail de méthode : sans elle, un lecteur averti se demande pourquoi les
    # moyennes par profil ne sont pas repondérées, et doute du reste.
    "cad_so1_note": {
        "en": "Strata reproduce the population structure: means by profile "
              "are unbiased, with no post-stratification weighting.",
        "fr": "Les strates reproduisent la structure de la population : les "
              "moyennes par profil sont sans biais, sans redressement."},

    "cad_so2_t": {"en": "Geospatial data", "fr": "Données géospatiales"},
    "cad_so2_x": {
        "en": "Satellite and spatial data used to measure land cover, "
              "vegetation, environmental conditions and landscape "
              "characteristics.",
        "fr": "Données satellitaires et spatiales utilisées pour mesurer le "
              "couvert, la végétation, les conditions environnementales et "
              "les caractéristiques du paysage."},
    "cad_so2_p": {
        "en": "Satellite imagery (Sentinel, Landsat)|Land cover and land use|"
              "Vegetation indices (NDVI, EVI)|Environmental indicators "
              "(e.g. SPI)|Topography and hydrography",
        "fr": "Imagerie satellitaire (Sentinel, Landsat)|Couvert et usage des "
              "sols|Indices de végétation (NDVI, EVI)|Indicateurs "
              "environnementaux (SPI, etc.)|Topographie et hydrographie"},

    "cad_so3_t": {"en": "Biodiversity assessment",
                  "fr": "Évaluation de la biodiversité"},
    "cad_so3_x": {
        "en": "Field observations and inventories used to characterize "
              "biodiversity and ecological conditions.",
        "fr": "Observations et inventaires de terrain utilisés pour "
              "caractériser la biodiversité et l'état écologique."},
    "cad_so3_p": {
        "en": "Species inventories|Habitat and ecosystem assessments|"
              "Indicator species and functional groups|Ecological condition "
              "indices",
        "fr": "Inventaires d'espèces|Évaluation des habitats et des "
              "écosystèmes|Espèces indicatrices et groupes fonctionnels|"
              "Indices d'état écologique"},

    "cad_so4_t": {"en": "Institutional interviews",
                  "fr": "Entretiens institutionnels"},
    "cad_so4_x": {
        "en": "Structured interviews conducted in each landscape with the "
              "actors who deliver services, take decisions and organise "
              "collective action.",
        "fr": "Entretiens structurés menés dans chaque paysage auprès des "
              "acteurs qui délivrent les services, décident et organisent "
              "l'action collective."},
    "cad_so4_p": {
        "en": "Health authorities|Education authorities|Communal political "
              "authorities|Civil society organisations",
        "fr": "Autorités sanitaires|Autorités éducatives|Autorités "
              "politiques communales|Organisations de la société civile"},

    # ================= LA BANDE DE CLÔTURE ===================================
    # LE NOMBRE EST COMPTÉ DANS LE RÉFÉRENTIEL, jamais écrit. C'est le seul
    # chiffre de la bande, et un chiffre faux à cet endroit — juste après la
    # liste des sources — discrédite les sources elles-mêmes.
    "cad_band_t": {
        "en": "From these different sources, APRI compiles a set of "
              "resilience indicators.",
        "fr": "À partir de ces différentes sources, APRI constitue un "
              "ensemble d'indicateurs de résilience."},
    "cad_band_x": {
        "en": "These indicators are standardized and aggregated to produce "
              "resilience scores across the seven dimensions.",
        "fr": "Ces indicateurs sont normalisés puis agrégés pour produire les "
              "scores de résilience sur les sept dimensions."},

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
    "cad_v_boucles": {"en": "The second strand, causal loop diagrams",
                      "fr": "Le second volet, les diagrammes de boucles causales"},
    "cad_strate2": {"en": "Explore", "fr": "Explorer"},
    "cad_strate3": {"en": "Go deeper", "fr": "Approfondir"},
    "cad_strate3_note": {
        "en": "Nothing has been removed: the full method is here, folded. "
              "Open only what you need.",
        "fr": "Rien n'a été retiré : la méthode complète est ici, repliée. "
              "N'ouvrez que ce dont vous avez besoin."},

    "cad_doc": {"en": "The full methodological document",
                "fr": "Le document méthodologique complet"},
    # LE POIDS EST CALCULÉ, PAS ÉCRIT. Annoncé en dur, il aurait continué de
    # dire 7,7 Mo le jour où le document est remplacé par une version plus
    # lourde — et un poids faux avant un téléchargement de plusieurs méga
    # octets est exactement le genre de détail qui fait douter du reste.
    "cad_doc_tel": {
        "en": "Download the IRLA approach (Word, {t})",
        "fr": "Télécharger l'approche IRLA (Word, {t})"},
    "cad_doc_note": {
        "en": "Everything above, in full prose, with the sources and the "
              "detail of each choice.",
        "fr": "Tout ce qui précède, en texte suivi, avec les sources et le "
              "détail de chaque choix."},
    "cad_doc_lire": {"en": "Or read it on screen",
                     "fr": "Ou le lire à l'écran"},
    "cad_doc_absent": {
        "en": "The file is not in the repository yet: drop a Word document "
              "whose name contains IRLA into data/ and the download appears.",
        "fr": "Le fichier n'est pas encore dans le dépôt : déposez dans "
              "data/ un document Word dont le nom contient IRLA et le "
              "téléchargement apparaîtra."},

    # ================= LES SEPT ONGLETS DE LA PAGE ==========================
    # LES TITRES SONT CEUX DU COMMANDITAIRE, MOT POUR MOT. Un intitulé qu'on
    # « améliore » en le traduisant dans sa propre langue disparaît de la
    # table des matières que son auteur a en tête, et la page devient
    # introuvable pour la personne qui l'a commandée.
    "cad_o1": {"en": "What APRI Measures", "fr": "Ce que mesure APRI"},
    "cad_o2": {"en": "How Resilience Is Measured: Sources and Data",
               "fr": "Comment la résilience est mesurée : sources et données"},
    "cad_o3": {"en": "The Dimensions of Resilience",
               "fr": "Les dimensions de la résilience"},
    "cad_o4": {"en": "From Raw Measures to Resilience Scores",
               "fr": "Des mesures brutes aux scores de résilience"},
    "cad_o5": {"en": "Understanding Resilience Through Feedback Loops and "
                     "Complex Systems",
               "fr": "Comprendre la résilience par les boucles de rétroaction "
                     "et les systèmes complexes"},
    "cad_o6": {"en": "The Specific Case of Environmental Data",
               "fr": "Le cas particulier des données environnementales"},
    "cad_o7": {"en": "Download the Theoretical and Methodological Framework",
               "fr": "Télécharger le cadre théorique et méthodologique"},

    # LES LIBELLÉS COURTS DE LA BARRE NUMÉROTÉE. Sept titres complets sur une
    # rangée faisaient une barre de cent trente pixels, plus haute que le
    # contenu de certains onglets. La barre ne porte plus que des numéros ;
    # le titre court apparaît sous celui qu'on regarde. Le titre entier reste
    # celui des clés cad_o1 à cad_o7 — il n'a pas été remplacé, il est en
    # retrait.
    "cad_c1": {"en": "What APRI measures", "fr": "Ce que mesure APRI"},
    "cad_c2": {"en": "Sources and data", "fr": "Sources et données"},
    "cad_c3": {"en": "Dimensions", "fr": "Dimensions"},
    "cad_c4": {"en": "Measures to scores", "fr": "De la mesure au score"},
    "cad_c5": {"en": "Feedback loops", "fr": "Boucles de rétroaction"},
    "cad_c6": {"en": "Environmental data", "fr": "Données environnementales"},
    "cad_c7": {"en": "The full framework", "fr": "Le cadre complet"},
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


def _document_irla():
    """Le document de référence, sous quelque nom qu'il ait été déposé.

    LE FICHIER EST CHERCHÉ, PAS NOMMÉ. Le code attendait
    `IRLA_approche_complete.doc` ; le document a été déposé dans le dépôt sous
    son titre entier, parenthèses et numéro de version compris, et la carte de
    téléchargement est restée muette sans rien dire de pourquoi. Un nom de
    fichier est une convention entre deux personnes, et une convention se
    perd : on prend donc le premier document Word du dossier dont le nom
    porte « IRLA ». Le déposer suffit, le renommer n'est plus nécessaire.
    """
    for dossier in (DATA, APP_DIR):
        if not os.path.isdir(dossier):
            continue
        for nom in sorted(os.listdir(dossier)):
            bas = nom.lower()
            if bas.endswith((".doc", ".docx")) and "irla" in bas:
                return os.path.join(dossier, nom)
    return None


def _poids(chemin):
    """Le poids du fichier, dans la langue courante."""
    mo = os.path.getsize(chemin) / (1024 * 1024)
    if i18n.get_lang() == "en":
        return f"{mo:.1f} MB"
    return f"{mo:.1f} Mo".replace(".", ",")


def _fond_icone(nom, couleur="#2a6b3f", taille=22):
    """Une icône du module commun, prête à servir de `background-image`.

    LE MODULE N'ÉCRIT PAS L'ESPACE DE NOMS SVG, et un SVG en `data:` qui n'en
    a pas ne peint rien du tout — sans erreur, sans trace. On l'ajoute ici.
    """
    brut = icones.svg(nom, couleur, taille).replace(
        "<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
    return 'url("data:image/svg+xml,%s")' % quote(brut)


def _css_telechargement(poids):
    """La pièce jointe a la forme d'une pièce jointe.

    LE BOUTON EST LA CARTE ENTIÈRE, et non un bouton posé dans une carte :
    toute la surface se clique, ce qui est la promesse que fait un bloc
    encadré. Streamlit ne pose qu'un libellé sur un bouton, donc la flèche et
    la ligne du format sont écrites en CSS, dans ::before et ::after.
    """
    b = 'div[class*="st-key-cad_tel"] div[data-testid="stDownloadButton"] > button'
    return f"""<style>
    {b} {{
      display:grid !important;
      grid-template-columns:46px 1fr; grid-template-rows:auto auto;
      column-gap:16px; row-gap:0; align-items:center;
      text-align:left !important;
      padding:17px 22px !important; min-height:0 !important;
      background:#ffffff !important;
      border:1px solid #dde9e3 !important;
      border-left:4px solid {VERT_APRI} !important;
      border-radius:12px !important;
      box-shadow:none !important; transform:none !important;
      transition:border-color .15s ease, box-shadow .15s ease;
    }}
    {b}:hover {{
      border-color:#bcd6c7 !important;
      border-left-color:{VERT_APRI} !important;
      box-shadow:0 2px 14px rgba(16,23,40,.06) !important;
    }}
    {b}::before {{
      content:""; grid-column:1; grid-row:1 / span 2;
      width:46px; height:46px; border-radius:50%;
      background:#eaf3ed {_fond_icone("telecharger")} center/22px no-repeat;
    }}
    {b} > div {{ grid-column:2; grid-row:1; width:auto !important;
                 justify-self:start !important; }}
    {b} div[data-testid="stMarkdownContainer"] {{ text-align:left !important; }}
    {b} p {{
      font-size:15px !important; font-weight:700 !important;
      color:#12314c !important; margin:0 !important;
      text-align:left !important; line-height:1.3 !important;
    }}
    {b}::after {{
      content:"{_txt_css(T("cad_doc_tel", t=poids))} · {_txt_css(T("cad_doc_note"))}";
      grid-column:2; grid-row:2; margin-top:4px;
      font-size:12.5px; font-weight:500; color:#6b7590; line-height:1.5;
    }}
    </style>"""


def _txt_css(t):
    """Un texte prêt pour `content:` — les guillemets et les barres obliques
    inverses y sont des délimiteurs, pas des caractères."""
    return t.replace("\\", "\\\\").replace('"', '\\"')


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
  .cad-h    { font-size:17.5px; font-weight:700; color:#101728;
              letter-spacing:-.015em; margin:0 0 3px; }
  .cad-note { font-size:12.5px; color:#6b7590; line-height:1.5;
              max-width:96ch; margin:0 0 10px; }
  .cad-grille { display:flex; gap:14px; flex-wrap:wrap; }
  .cad-carte  { flex:1 1 250px; min-width:230px; background:#fff;
                border:1px solid #e3eaf3; border-radius:14px;
                padding:15px 17px; box-shadow:0 1px 2px rgba(16,23,40,.05); }
  .cad-carte-t{ font-size:11px; letter-spacing:.07em; text-transform:uppercase;
                font-weight:700; margin:0 0 6px; }
  .cad-carte-x{ font-size:13.5px; color:#3c4761; line-height:1.55; margin:0; }
  .cad-liste  { margin:0; padding:0; list-style:none; }
  .cad-liste li { font-size:13px; color:#3c4761; line-height:1.5;
                  padding:6px 0 6px 16px; position:relative; }
  .cad-liste li::before { content:""; position:absolute; left:0; top:13px;
                  width:6px; height:6px; border-radius:50%; background:#c3ccda; }

  .cad-etage{ font-size:11px; letter-spacing:.11em; text-transform:uppercase;
              font-weight:700; color:#a7b0be; margin:26px 0 8px; }
  /* LA JUSTIFICATION EST ANNULÉE DANS LES CARTES. La feuille de style du
     site justifie tous les paragraphes : c'est bon pour une colonne de
     texte, et cela défigure une carte de deux lignes — les mots s'écartent
     jusqu'à laisser des couloirs blancs au milieu. */
  .cad-carte-x { text-align:left !important; }

  /* --- les quatre sources, en deux colonnes de texte ----------------------
     LES CADRES ONT SAUTÉ. Quatre cartes blanches côte à côte tenaient dans
     l'écran mais imposaient à chacune la hauteur de la plus haute — celle de
     l'enquête ménage, qui porte le plan de sondage — et laissaient trois
     grands vides. Deux colonnes, deux rangées : chaque source prend la
     hauteur qu'elle demande, et le numéro suivi de son filet fait le travail
     que faisait le cadre, dire où commence un bloc.

     LES PUCES SONT DES TIRETS. Le rond plein appelle une liste d'items de
     même nature ; ce sont ici des précisions de protocole, de longueurs très
     inégales, que le tiret introduit sans les aligner de force. */
  /* DEUX COLONNES, ET PAS « AUTANT QUE ÇA RENTRE ». En `auto-fit`, un écran
     large en formait trois et renvoyait la quatrième source seule sur une
     seconde rangée — une source isolée se lit comme un ajout. */
  .cad-so   { display:grid; gap:28px 56px; margin-top:14px;
              grid-template-columns:repeat(2,1fr); }
  @media (max-width: 900px) { .cad-so { grid-template-columns:1fr; } }
  .cad-so-b { display:grid; grid-template-columns:104px 1fr;
              align-items:start; }
  .cad-so-i { position:relative; font-size:13px; font-weight:600;
              color:#8a93a5; padding-top:2px; letter-spacing:.02em; }
  .cad-so-i::after { content:""; position:absolute; left:30px; right:16px;
              top:11px; height:1px; background:#1a6b52; opacity:.45; }
  .cad-so-t { font-size:15.5px; font-weight:700; color:#1a6b52;
              letter-spacing:-.01em; margin:0 0 7px; }
  p.cad-so-x { font-size:12.5px !important; color:#3c4761 !important;
              line-height:1.5 !important; margin:0 0 9px !important;
              text-align:left !important; max-width:64ch; }
  /* Les compteurs de l'enquête ménage : c'est la seule source dont on
     connaisse l'effectif, le nombre de sections et le minimum par section. */
  .cad-so-k { margin:0 0 9px; }
  .cad-so-k > div { display:flex; align-items:baseline; gap:9px;
              padding:2px 0; }
  .cad-so-k b { flex:0 0 auto; min-width:44px; font-size:14.5px;
              font-weight:700; color:#101728; letter-spacing:-.02em;
              font-variant-numeric:tabular-nums; }
  .cad-so-k span { font-size:11.5px; color:#5a6a80; line-height:1.35;
              text-align:left !important; }
  .cad-so-l { margin:0; padding:0; list-style:none; }
  .cad-so-l li { font-size:12.5px; color:#3c4761; line-height:1.45;
              padding:3px 0 3px 20px; position:relative;
              text-align:left !important; }
  .cad-so-l li::before { content:"—"; position:absolute; left:0; top:3px;
              color:#a7b0be; font-size:11px; }

  /* --- la méthode de calcul, en trois temps -------------------------------
     TROIS SECTIONS NUMÉROTÉES, SÉPARÉES PAR UN FILET. Le calcul est une
     suite d'opérations : le lecteur doit voir où finit l'une et où commence
     la suivante, et un filet le dit mieux qu'un blanc.

     LES ÉTAPES SONT RELIÉES PAR DES FLÈCHES, et c'est le seul endroit du
     site où une flèche se justifie : ici l'ordre EST l'information — on ne
     normalise pas avant d'avoir fixé le sens et la référence. */
  .cad-p    { padding:16px 0 18px; border-bottom:1px solid #e9eef4; }
  .cad-p:last-of-type { border-bottom:0; }
  .cad-p-t  { font-size:14.5px; font-weight:700; color:#101728;
              margin:0 0 14px; letter-spacing:-.01em; }
  .cad-p-t b { color:#3c4761; font-weight:700; margin-right:7px; }
  .cad-ex   { display:inline-block; margin-left:10px; font-size:9.5px;
              font-weight:700; letter-spacing:.11em; text-transform:uppercase;
              color:#8a93a5; border:1px solid #e3eaf3; border-radius:99px;
              padding:2px 8px; vertical-align:2px; }
  .cad-flo  { display:flex; align-items:flex-start; gap:0; flex-wrap:wrap; }
  .cad-flo-e { flex:1 1 150px; min-width:130px; text-align:center;
              padding:0 6px; }
  .cad-flo-t { font-size:12.5px; font-weight:700; color:#1a6b52;
              line-height:1.3; margin-bottom:5px; }
  .cad-flo-v { font-size:12px; color:#101728; font-weight:600;
              line-height:1.45; }
  .cad-flo-x { font-size:11px; color:#8a93a5; line-height:1.4; margin-top:3px; }
  /* La flèche est dessinée, pas écrite : un caractère « → » change de dessin
     d'une police à l'autre et se retrouve trop haut ou trop bas. */
  .cad-flo-f { flex:0 1 70px; min-width:34px; height:1px; background:#c9d6cf;
              margin:16px 0 0; position:relative; }
  .cad-flo-f::after { content:""; position:absolute; right:0; top:-3px;
              border-left:6px solid #c9d6cf; border-top:3.5px solid transparent;
              border-bottom:3.5px solid transparent; }

  /* Les deux méthodes de normalisation, séparées par un filet vertical. */
  .cad-nrm  { display:grid; grid-template-columns:1fr 1fr; gap:34px; }
  .cad-nrm > div + div { border-left:1px solid #e9eef4; padding-left:34px; }
  .cad-nrm-t { font-size:12.5px; font-weight:700; color:#1a6b52;
              margin:0 0 4px; }
  .cad-nrm-x { font-size:11px; color:#8a93a5; line-height:1.45;
              margin:0 0 14px; text-align:left !important; }
  /* LES DEUX FORMULES NE S'ÉCARTENT PAS JUSQU'AUX BORDS. Étirées à parts
     égales dans leur colonne, elles se retrouvaient à quarante centimètres
     l'une de l'autre et cessaient de se lire comme une paire. */
  .cad-duo  { display:flex; gap:38px; flex-wrap:wrap;
              justify-content:flex-start; align-items:flex-start; }
  .cad-duo > div { flex:0 1 auto; max-width:100%; }
  .cad-duo-t { font-size:11.5px; font-weight:700; color:#3c4761;
              margin:0 0 8px; }
  .cad-eq   { display:flex; align-items:center; gap:6px; font-size:12px;
              color:#101728; }
  /* La fraction est composée, pas écrite avec une barre oblique : c'est la
     forme sous laquelle la formule est publiée dans le document de méthode,
     et une barre oblique se relit mal quand le numérateur est une
     soustraction. */
  .cad-fr   { display:inline-block; text-align:center; vertical-align:middle; }
  .cad-fr-n { display:block; padding:0 4px 2px;
              border-bottom:1px solid #101728; }
  .cad-fr-d { display:block; padding:2px 4px 0; }
  .cad-seu  { display:grid; grid-template-columns:auto 18px auto;
              justify-content:start; gap:5px 10px; align-items:center;
              font-size:11.5px; color:#3c4761; }
  .cad-seu i { color:#a7b0be; font-style:normal; text-align:center; }
  .cad-seu b { color:#101728; font-weight:700;
              font-variant-numeric:tabular-nums; }
  /* La spécificité compte : `.cad-duo > div` porte déjà un `max-width`, et
     un sélecteur de classe simple ne l'emporte pas sur un sélecteur d'enfant.
     La note est donc visée à travers son parent. */
  .cad-duo > .cad-seu-n { font-size:11px; color:#1a6b52; line-height:1.5;
              max-width:27ch; text-align:left !important; }

  /* Le pied : pourquoi l'échelle est de 0 à 10, et combien d'indicateurs. */
  .cad-pied { display:flex; align-items:flex-start; gap:26px; flex-wrap:wrap;
              border-top:1px solid #1a6b52; margin-top:6px; padding-top:14px; }
  .cad-pied-c { flex:1 1 380px; min-width:0; }
  .cad-pied-t { font-size:12.5px; font-weight:700; color:#1a6b52;
              margin:0 0 3px; }
  p.cad-pied-x { font-size:11.5px !important; color:#8a93a5 !important;
              line-height:1.5 !important; margin:0 !important;
              text-align:left !important; max-width:70ch; }
  .cad-pied-n { flex:0 0 auto; display:flex; align-items:baseline; gap:10px; }
  .cad-pied-v { font-size:30px; font-weight:700; color:#1a6b52; line-height:1;
              letter-spacing:-.02em; font-variant-numeric:tabular-nums; }
  .cad-pied-l { font-size:11px; color:#5a6a80; line-height:1.35;
              max-width:21ch; text-align:left !important; }

  /* --- la phrase de clôture ------------------------------------------------
     UN FILET, DEUX LIGNES, PAS D'ENCADRÉ. Elle ferme la liste des sources et
     dit ce qu'on en fait ; un bloc teinté en aurait fait un cinquième objet
     de même rang que les quatre sources. */
  .cad-fin  { border-top:1px solid #1a6b52; margin-top:24px;
              padding-top:14px; }
  .cad-fin-t { font-size:14.5px; font-weight:700; color:#1a6b52;
              margin:0 0 3px; line-height:1.4; }
  p.cad-fin-x { font-size:12.5px !important; color:#5a6a80 !important;
              line-height:1.5 !important; margin:0 !important;
              text-align:left !important; }

  /* --- les trois attributs, en colonnes numérotées ------------------------
     TROIS COLONNES ÉGALES, SÉPARÉES PAR UN FILET, ET AUCUNE CARTE. Un cadre
     annonce qu'on peut prendre l'objet, or il n'y a rien à cliquer ici. Le
     filet vertical suffit à dire que ce sont trois colonnes et non un
     paragraphe en trois morceaux.

     LE NUMÉRO EST MAIGRE ET GRAND. Gros et gras, il aurait pesé plus que le
     mot qu'il annonce ; maigre, il donne l'ordre sans le disputer. */
  .cad-aaa  { display:grid; grid-template-columns:repeat(3,1fr);
              margin-top:4px; }
  .cad-a    { padding:6px 30px 2px 0; }
  .cad-a + .cad-a { border-left:1px solid #e6ecf2; padding-left:30px; }
  .cad-a-h  { display:flex; align-items:center; gap:14px; margin-bottom:24px; }
  .cad-a-i  { width:50px; height:50px; border-radius:50%; background:#eef3ef;
              display:flex; align-items:center; justify-content:center;
              flex:0 0 auto; }
  /* Le trait s'arrête sur un point : une ligne qui se termine dans le vide
     se lit comme une ligne coupée. */
  .cad-a-l  { flex:1 1 auto; height:1px; background:#cfe0d6;
              position:relative; min-width:24px; }
  .cad-a-l::after { content:""; position:absolute; right:0; top:-2.5px;
              width:6px; height:6px; border-radius:50%; background:#1b5e3a; }
  .cad-a-t  { font-size:16px; font-weight:700; color:#1a6b52;
              letter-spacing:.055em; text-transform:uppercase;
              margin:0 0 9px; }
  p.cad-a-x { font-size:14.5px !important; color:#3c4761 !important;
              line-height:1.55 !important; margin:0 !important;
              text-align:left !important; max-width:36ch; }
  @media (max-width: 900px) {
    .cad-aaa { grid-template-columns:1fr; }
    .cad-a + .cad-a { border-left:0; border-top:1px solid #e6ecf2;
                      padding-left:0; padding-top:22px; margin-top:18px; }
  }

  /* La barre d'onglets vient de `onglets.py`, comme sur les autres pages. */

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
    """Une ligne par dimension : le nom, le poids, l'effectif calculé.

    LA PASTILLE DE COULEUR A SAUTÉ. Sept carrés teintés en tête de ligne
    annonçaient sept familles distinctes ; ils ne servaient qu'ici, et le
    chiffre romain qui ouvre déjà chaque nom fait le même travail sans
    demander au lecteur de retenir un code de couleurs. Le vert reste, et il
    ne dit qu'une chose : la part de l'indice.

    LA COLONNE « INDICATEURS » PORTE SA PROPRE BARRE. Le rapport « 10/16 »
    seul se lit mal en balayage — il faut diviser de tête, sept fois. Une
    barre sous le rapport donne l'avancement d'un coup d'œil, et le rapport
    reste au-dessus pour qui veut le compte exact.

    UNE DIMENSION SANS AUCUN INDICATEUR CALCULÉ RESTE À SA PLACE, en pâle.
    L'effacer donnerait à croire que le référentiel en compte six.
    """
    pmax = max(e["part"] for e in stats["dims"].values()) or 1
    col = ('grid-template-columns:minmax(190px,1.5fr) minmax(160px,3fr) '
           '64px 96px;gap:22px;align-items:center;')
    lignes = []
    for cle in ORDRE:
        e = stats["dims"].get(cle)
        if not e:
            continue
        vide = e["faits"] == 0
        pale = "opacity:.4" if vide else ""
        part_ind = 100 * e["faits"] / e["n"] if e["n"] else 0
        nom = _e(T(cle))
        num, _, reste = nom.partition(". ")
        lignes.append(
            f'<div style="display:grid;{col}padding:13px 0;'
            f'border-bottom:1px solid #eef2f7">'
            f'<div style="font-size:13.5px;line-height:1.35">'
            f'<span style="color:{VERT_APRI};font-weight:700">{num}.</span> '
            f'<span style="color:{ENCRE};font-weight:600">{reste}</span></div>'
            f'<div style="background:#e4efe8;border-radius:99px;height:9px;'
            f'overflow:hidden"><div style="height:100%;border-radius:99px;'
            f'width:{max(100 * e["part"] / pmax, 1.5):.1f}%;'
            f'background:{VERT_APRI};{pale}"></div></div>'
            f'<div style="font-size:12.5px;font-weight:600;color:{ENCRE};'
            f'text-align:right;font-variant-numeric:tabular-nums">'
            f'{_fmt(e["part"])}&thinsp;%</div>'
            f'<div><div style="font-size:12px;color:{ENCRE2};'
            f'font-variant-numeric:tabular-nums;margin-bottom:5px">'
            f'{e["faits"]}/{e["n"]}</div>'
            f'<div style="background:#eaeef3;border-radius:99px;height:3px;'
            f'overflow:hidden"><div style="height:100%;border-radius:99px;'
            f'width:{part_ind:.0f}%;background:{VERT_APRI};{pale}"></div>'
            f'</div></div></div>')
    entete = (
        f'<div style="display:grid;{col}padding:0 0 9px;font-size:10.5px;'
        f'letter-spacing:.1em;text-transform:uppercase;color:#8a93a5;'
        f'font-weight:700">'
        f'<div>{_e(T("cad_col_dim"))}</div>'
        f'<div style="grid-column:span 2">{_e(T("cad_col_poids"))}</div>'
        f'<div>{_e(T("cad_col_ind"))}</div></div>')
    return ('<div style="margin-top:14px">' + entete + "".join(lignes)
            + '</div>')


def _flot(etapes):
    """Une suite d'étapes reliées par des flèches.

    L'ORDRE EST L'INFORMATION. C'est le seul endroit du site où une flèche se
    justifie : on ne normalise pas avant d'avoir fixé le sens de lecture et
    la référence. Ailleurs, les flèches disaient une succession qui n'en
    était pas une.
    """
    blocs = []
    for i, (titre, valeur, note) in enumerate(etapes):
        if i:
            blocs.append('<div class="cad-flo-f"></div>')
        blocs.append(
            '<div class="cad-flo-e">'
            f'<div class="cad-flo-t">{_e(titre)}</div>'
            + (f'<div class="cad-flo-v">{_e(valeur)}</div>' if valeur else "")
            + (f'<div class="cad-flo-x">{_e(note)}</div>' if note else "")
            + '</div>')
    return '<div class="cad-flo">' + "".join(blocs) + '</div>'


def _fraction(haut, bas):
    """Une fraction composée : numérateur, filet, dénominateur."""
    return (f'<span class="cad-fr"><span class="cad-fr-n">{haut}</span>'
            f'<span class="cad-fr-d">{bas}</span></span>')


def _formule(sens, haut):
    """Score_i = 10 × (fraction), sous le sens de lecture qu'elle sert."""
    bas = 'x<sub>max</sub> &minus; x<sub>min</sub>'
    return ('<div><div class="cad-duo-t">' + _e(sens) + '</div>'
            '<div class="cad-eq">'
            '<span>Score<sub>i</sub> = 10 &times;</span>'
            + _fraction(haut, bas) + '</div></div>')


def _seuils(brut):
    """Le tableau des paliers, écrit « borne → score » dans la traduction."""
    lignes = []
    for p_ in brut.split("|"):
        if "→" not in p_:
            continue
        borne, _, val = p_.partition("→")
        lignes.append(f'<span>{_e(borne.strip())}</span><i>&rarr;</i>'
                      f'<b>{_e(val.strip())}</b>')
    return '<div class="cad-seu">' + "".join(lignes) + '</div>'


def _titre_p(rang, cle, exemple=False):
    """L'intitulé numéroté d'une des trois sections du calcul."""
    return (f'<div class="cad-p-t"><b>{rang}.</b>{_e(T(cle))}'
            + (f'<span class="cad-ex">{_e(T("cad_ex"))}</span>'
               if exemple else "") + '</div>')


def _attributs():
    """Les trois attributs, en trois colonnes numérotées.

    C'EST LE SEUL CONTENU DU PREMIER ONGLET, et il porte donc toute la
    définition. Les quatre cartouches d'ouverture et le schéma d'ensemble qui
    l'entouraient ont été retirés : ils répondaient à quatre questions à la
    fois, et aucune ne disait en une ligne ce qu'APRI mesure. La phrase le dit
    maintenant, au-dessus ; ces trois colonnes la déplient, et rien d'autre.

    PLUS DE NUMÉRO DEVANT LES TROIS. Un numéro promet un ordre obligatoire —
    faites 01, puis 02, puis 03. Ces trois-là ne sont pas des étapes : un
    territoire anticipe, absorbe et s'adapte en même temps, et le même
    indicateur peut servir deux d'entre eux. Le pictogramme et le trait
    tiennent la colonne aussi bien, sans rien promettre de faux.
    """
    cols = []
    for k, ic in (("cad_a1", "loupe"), ("cad_a2", "bouclier"),
                  ("cad_a3", "rafraichir")):
        cols.append(
            '<div class="cad-a">'
            '<div class="cad-a-h">'
            f'<span class="cad-a-i">'
            + icones.svg(ic, couleur=VERT_APRI, taille=21) + '</span>'
            '<span class="cad-a-l"></span></div>'
            f'<div class="cad-a-t">{_e(T(k + "_t"))}</div>'
            f'<p class="cad-a-x">{_e(T(k))}</p></div>')
    return '<div class="cad-aaa">' + "".join(cols) + '</div>'


def _sources(extras=None):
    """Les quatre sources, en deux colonnes de texte.

    LE PARCOURS EN CHEVRONS A DISPARU, PUIS LES CADRES. Les trois sources
    étaient d'abord reliées par des « › », comme des étapes ; elles n'en sont
    pas — les quatre dispositifs tournent en parallèle. Elles sont ensuite
    passées en cartes, ce qui disait bien la simultanéité mais alignait leur
    hauteur sur la plus haute et laissait trois grands vides. Deux colonnes
    de texte, numérotées : chaque source prend la hauteur qu'elle demande.

    CHAQUE SOURCE PORTE SA LISTE, et c'est elle qui la rend contestable :
    « données géospatiales » ne veut rien dire tant qu'on n'a pas lu
    Sentinel, Landsat, NDVI. Une source qu'on ne peut pas vérifier est une
    source qu'on doit croire.

    `extras` GLISSE UN BLOC SOUS LA DESCRIPTION. L'enquête ménage est la
    seule des quatre dont on connaisse l'effectif, le nombre de sections et
    le minimum par section.
    """
    extras = extras or {}
    blocs = []
    for i, k in enumerate(("cad_so1", "cad_so2", "cad_so3", "cad_so4"),
                          start=1):
        puces = [x.strip() for x in T(k + "_p").split("|") if x.strip()]
        if (k + "_note") in i18n.DICO:
            puces.append(T(k + "_note"))
        blocs.append(
            '<div class="cad-so-b">'
            f'<div class="cad-so-i">{i:02d}</div><div>'
            f'<div class="cad-so-t">{_e(T(k + "_t"))}</div>'
            f'<p class="cad-so-x">{_e(T(k + "_x"))}</p>'
            + extras.get(k, "")
            + '<ul class="cad-so-l">'
            + "".join(f'<li>{_e(p)}</li>' for p in puces)
            + '</ul></div></div>')
    return '<div class="cad-so">' + "".join(blocs) + '</div>'


def _compteurs(paires):
    """Une rangée compacte de chiffres, sous la description d'une source."""
    if not paires:
        return ""
    return ('<div class="cad-so-k">' + "".join(
        f'<div><b>{_e(v)}</b><span>{_e(lab)}, {_e(sous)}</span></div>'
        for v, lab, sous in paires) + '</div>')


def _fin():
    """La phrase qui ferme la liste des sources.

    LE NOMBRE D'INDICATEURS N'Y EST PLUS. Il était posé à droite, dans un
    bloc teinté, et faisait de la conclusion un cinquième objet de même rang
    que les quatre sources. Le compte reste dit — et détaillé dimension par
    dimension — dans l'onglet des dimensions.
    """
    return ('<div class="cad-fin">'
            f'<div class="cad-fin-t">{_e(T("cad_band_t"))}</div>'
            f'<p class="cad-fin-x">{_e(T("cad_band_x"))}</p></div>')


def _min_section():
    """Le plus petit effectif enquêté parmi les sections communales.

    LE CHIFFRE EST COMPTÉ, PAS ANNONCÉ. Un plan de sondage qui promet un
    minimum par section et qu'on ne recompte jamais finit par décrire un
    protocole plutôt que la collecte réellement faite.
    """
    p = _trouver("ventilation.json")
    if not p:
        return None
    try:
        with open(p, encoding="utf-8") as f:
            eff = (json.load(f) or {}).get("effectifs") or {}
        vals = [v for v in ((d or {}).get("Total") for d in eff.values()) if v]
        return min(vals) if vals else None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# LA PAGE, EN SEPT ONGLETS
# ---------------------------------------------------------------------------
# SEPT ONGLETS, SEPT QUESTIONS, dans l'ordre où elles se posent : ce que
# l'indice mesure, avec quoi on le mesure, sur quelles dimensions, comment on
# passe de la mesure au score, comment se lisent les rétroactions, ce que
# l'environnement a de particulier, et où se télécharge le cadre complet.
#
# UN SÉLECTEUR, ET NON `st.tabs`. `st.tabs` rend TOUS les onglets à chaque
# affichage : l'onglet environnemental — transects, séries satellitaires,
# trajectoires de couvert et de pluie — serait recalculé pour montrer une
# page de définitions. Le sélecteur ne rend que ce qu'on regarde.
#
# IL RETIENT UN CODE, JAMAIS UN LIBELLÉ. Le libellé change avec la langue ;
# une vue mémorisée par son libellé retomberait sur la première case au
# premier changement de langue, et le harnais de rendu croirait couvrir sept
# onglets en n'en rendant qu'un.
VUES = ("mesure", "sources", "dimensions", "score", "boucles",
        "environnement", "document")
_LIB = {"mesure": "cad_o1", "sources": "cad_o2", "dimensions": "cad_o3",
        "score": "cad_o4", "boucles": "cad_o5", "environnement": "cad_o6",
        "document": "cad_o7"}
_COURT = {"mesure": "cad_c1", "sources": "cad_c2", "dimensions": "cad_c3",
          "score": "cad_c4", "boucles": "cad_c5", "environnement": "cad_c6",
          "document": "cad_c7"}
_DESC = {"mesure": "cad_d1", "sources": "cad_d2", "dimensions": "cad_d3",
         "score": "cad_d4", "boucles": "cad_d5", "environnement": "cad_d6",
         "document": "cad_d7"}


def render(doc_complet=None):
    stats = _stats()
    st.markdown(STYLE, unsafe_allow_html=True)

    st.markdown(
        f'<h2 style="font-size:21.5px;font-weight:700;color:{ENCRE};'
        f'letter-spacing:-.02em;margin:2px 0 10px">{T("cad_titre")}</h2>',
        unsafe_allow_html=True)

    if not stats:
        st.info(T("e_absent"))
        return

    # LA BARRE EST CELLE DE TOUT LE SITE. Elle était recopiée ici avec sa
    # propre feuille de style ; à force de retouches faites d'un côté et pas
    # de l'autre, elle n'avait plus tout à fait la même graisse que celle des
    # résultats, et l'on changeait de site en changeant de page.
    vue = onglets.barre("cad_vue", list(VUES),
                        titre=lambda c: T(_COURT[c]),
                        description=lambda c: T(_DESC[c]),
                        defaut=VUES[0])

    if vue == "sources":
        _v_sources()
    elif vue == "dimensions":
        _v_dimensions(stats)
    elif vue == "score":
        _v_score(stats)
    elif vue == "boucles":
        _v_boucles()
    elif vue == "environnement":
        _v_environnement()
    elif vue == "document":
        _v_document(doc_complet)
    else:
        _v_mesure()


def _titre(cle, note=None, marge=4):
    """Un intitulé de bloc, et sa note s'il en a une."""
    h = (f'<div class="cad-h" style="margin-top:{marge}px">'
         f'{_e(T(cle))}</div>')
    return h + (f'<p class="cad-note">{_e(T(note))}</p>' if note else "")


# --- 1 · ce que mesure APRI -------------------------------------------------
def _v_mesure():
    """Une phrase, puis les trois attributs. Rien d'autre.

    L'ONGLET DISAIT TROP DE CHOSES À LA FOIS. Quatre cartouches d'ouverture,
    les trois attributs, puis un schéma d'ensemble en quatre pavés chiffrés :
    trois réponses empilées à la question « qu'est-ce qu'APRI mesure ? »,
    dont aucune ne la donnait en une ligne. La phrase la donne, et les trois
    attributs la déplient.
    """
    # LA DÉFINITION EST REMONTÉE À L'ACCUEIL, et elle n'a pas à être dite
    # deux fois : c'est la phrase qui ouvre le site, pas l'en-tête d'un
    # onglet de documentation. L'onglet commence donc directement par ce
    # qu'il apporte — les trois attributs.
    st.markdown(_titre("cad_aaa", marge=8) + _attributs(),
                unsafe_allow_html=True)


# --- 2 · comment la résilience est mesurée ----------------------------------
def _v_sources():
    """Les quatre sources et ce qui en sort. Tout tient dans l'écran.

    LA QUATRIÈME SOURCE MANQUAIT. Les entretiens structurés menés dans chaque
    paysage auprès des autorités sanitaires, éducatives et politiques
    communales et des organisations de la société civile existaient dans la
    collecte, et la page n'en disait rien.

    LE PLAN DE SONDAGE N'EST PLUS UN BLOC À PART. Il occupait le bas de
    l'onglet — trois grands nombres, quatre strates, un paragraphe — et il
    fallait faire défiler pour l'atteindre alors qu'il ne décrit qu'UNE des
    quatre sources. Ses chiffres sont entrés dans la carte de l'enquête
    ménage, ses strates dans une puce, et sa justification dans la note du
    bas. Rien n'a été perdu ; il n'y a plus rien sous les quatre blocs.
    """
    menages, n_sections = _menages()
    compteurs = []
    if menages:
        compteurs.append((_fmt(menages, 0), T("cad_s1_t"), T("cad_s1")))
    if n_sections:
        compteurs.append((str(n_sections), T("cad_s2_t"), T("cad_s2")))
    mini = _min_section()
    if mini:
        compteurs.append((_fmt(mini, 0), T("cad_s4_t"), T("cad_s4")))

    st.markdown(
        _titre("cad_src", "cad_src_note", marge=4)
        + _sources({"cad_so1": _compteurs(compteurs)})
        + _fin(), unsafe_allow_html=True)


# --- 3 · les dimensions -----------------------------------------------------
def _v_dimensions(stats):
    """Le tableau des sept dimensions, et la note sur la septième.

    LA NOTE N'EST PLUS UNE `st.caption`. Le composant de Streamlit la rendait
    dans un gris et un corps qui ne sont ceux d'aucun autre texte de la page ;
    elle prend maintenant le gris des notes du site, sous un filet qui la
    rattache au tableau.
    """
    st.markdown(_titre("cad_dims", "cad_dims_note", marge=4)
                + _tableau_dimensions(stats)
                + f'<p class="cad-note" style="margin:16px 0 0;'
                  f'max-width:92ch">{_e(T("cad_dim7_note"))}</p>',
                unsafe_allow_html=True)


# --- 4 · de la mesure brute au score ---------------------------------------
def _v_score(stats):
    """Comment on passe d'une mesure brute à un score, en trois temps.

    LA CHAÎNE TENAIT EN QUATRE PAVÉS ET NE MONTRAIT RIEN. « Métrique ›
    barème › pondération › agrégation » nommait les opérations sans en
    exécuter une seule : le lecteur savait qu'un barème existe, pas ce qu'il
    fait à quarante-cinq minutes de marche pour aller chercher l'eau. Les
    trois sections déroulent l'opération sur un cas, donnent les deux
    formules de normalisation, puis remontent jusqu'au score d'ensemble.

    LES VALEURS DE L'EXEMPLE PORTENT LA MENTION « EXEMPLE ». Elles sont
    choisies pour que la chaîne se suive, et le score global réel n'est pas
    celui-là ; sans la mention, elles se liraient comme un résultat.
    """
    st.markdown(
        '<div class="cad-p">'
        + _titre_p(1, "cad_p1_t", exemple=True)
        + _flot([
            (T("cad_p1a_t"), T("cad_p1a_v"), T("cad_p1a_x")),
            (T("cad_p1b_t"), T("cad_p1b_v"), ""),
            (T("cad_p1c_t"), T("cad_p1c_v"), T("cad_p1c_x")),
            (T("cad_p1d_t"), T("cad_p1d_v"), ""),
            (T("cad_p1e_t"), T("cad_p1e_v"), ""),
        ]) + '</div>'

        + '<div class="cad-p">' + _titre_p(2, "cad_p2_t")
        + '<div class="cad-nrm"><div>'
        + f'<div class="cad-nrm-t">{_e(T("cad_p2s_t"))}</div>'
        + f'<div class="cad-nrm-x">{_e(T("cad_p2s_x"))}</div>'
        + '<div class="cad-duo">'
        + _formule(T("cad_p2h"),
                   'x<sub>i</sub> &minus; x<sub>min</sub>')
        + _formule(T("cad_p2l"),
                   'x<sub>max</sub> &minus; x<sub>i</sub>')
        + '</div></div><div>'
        + f'<div class="cad-nrm-t">{_e(T("cad_p2b_t"))}</div>'
        + f'<div class="cad-nrm-x">{_e(T("cad_p2b_x"))}</div>'
        + '<div class="cad-duo">' + _seuils(T("cad_p2b_r"))
        + f'<div class="cad-seu-n">{_e(T("cad_p2b_n"))}</div>'
        + '</div></div></div></div>'

        + '<div class="cad-p">'
        + _titre_p(3, "cad_p3_t", exemple=True)
        + _flot([
            (T("cad_p3a_t"), "", T("cad_p3a_x")),
            (T("cad_p3b_t"), T("cad_p3b_v"), T("cad_p3b_x")),
            (T("cad_p3c_t"), "", T("cad_p3c_x")),
            (T("cad_p3d_t"), T("cad_p3d_v"), T("cad_p3d_x")),
        ]) + '</div>',
        unsafe_allow_html=True)

    # LE COMPTE D'INDICATEURS EST CELUI DU RÉFÉRENTIEL, dimensions comprises.
    st.markdown(
        '<div class="cad-pied"><div class="cad-pied-c">'
        f'<div class="cad-pied-t">{_e(T("cad_p4_t"))}</div>'
        f'<p class="cad-pied-x">{_e(T("cad_p4_x"))}</p></div>'
        '<div class="cad-pied-n">'
        f'<div class="cad-pied-v">{stats["n"]}</div>'
        f'<div class="cad-pied-l">'
        f'{_e(T("cad_p4_lab", d=len(stats["dims"])))}</div>'
        '</div></div>', unsafe_allow_html=True)

    # CE QUE L'INDICE NE PEUT PAS DIRE reste sur cet onglet : les limites ne
    # se comprennent qu'une fois le calcul connu — la circularité d'un indice
    # composite ne veut rien dire tant qu'on n'a pas vu qu'il agrège ses
    # propres variables explicatives.
    st.markdown(
        _titre("cad_limites", marge=34)
        + '<div class="cad-grille">'
        + "".join(_cartouche(T(k + "_t"), T(k), ENCRE3)
                  for k in ("cad_l1", "cad_l2", "cad_l3", "cad_l4"))
        + '</div>', unsafe_allow_html=True)


# --- 5 · les boucles de rétroaction ----------------------------------------
def _v_boucles():
    st.markdown(
        _titre("cad_dbc", marge=4)
        + f'<p class="cad-note" style="max-width:92ch">{_e(T("cad_dbc_x"))}</p>'
        '<div class="cad-grille">'
        + "".join(
            f'<div style="flex:1 1 220px;min-width:200px;'
            f'border-left:3px solid {c};padding:2px 0 2px 14px">'
            f'<div style="font-size:13.5px;font-weight:700;color:{ENCRE}">'
            f'{_e(T(k + "_t"))}</div>'
            f'<div style="font-size:12px;color:{ENCRE2};line-height:1.5;'
            f'margin-top:3px">{_e(T(k))}</div></div>'
            for k, c in (("cad_dbc_1", "#c33a24"), ("cad_dbc_2", "#d1730c"),
                         ("cad_dbc_3", "#2166ac"), ("cad_dbc_4", "#1a8a4f")))
        + '</div>', unsafe_allow_html=True)

    g, d = st.columns([1.15, 1])
    with g:
        st.markdown(_titre("cad_lecture", marge=28), unsafe_allow_html=True)
        st.markdown(T("cad_lecture_x"))
        st.warning(T("cad_lecture_piege"))
    with d:
        st.markdown('<div style="height:40px"></div>' + _schema_boucles(),
                    unsafe_allow_html=True)
    st.info(T("cad_dbc_lien"))


# --- 6 · le cas de l'environnement -----------------------------------------
def _v_environnement():
    """La dimension qui ne se mesure pas en interrogeant des ménages.

    Transects, images satellitaires et barèmes propres : fondue dans la page
    générale elle y tiendrait six lignes ; à part, elle garde son protocole
    entier — et les trajectoires, qui disent le même territoire dans le
    temps, la suivent.
    """
    environnement_cadre.render(
        complement=lambda: trajectoires.render(entete=False))


# --- 7 · le document de référence ------------------------------------------
def _v_document(doc_complet):
    """Le cadre complet, en pièce jointe.

    CE N'EST PAS UN VOLET REPLIÉ. Un volet demande un clic pour savoir ce
    qu'il contient et n'annonce rien de ce qu'on peut en faire. C'est une
    pièce jointe : elle en a la forme — une carte cliquable, une flèche de
    téléchargement, le format et le poids annoncés avant le clic. Le rendu à
    l'écran reste dessous, pour qui préfère lire sans télécharger.
    """
    chemin = _document_irla()
    if chemin:
        st.markdown(_css_telechargement(_poids(chemin)), unsafe_allow_html=True)
        with st.container(key="cad_tel"):
            with open(chemin, "rb") as f:
                st.download_button(
                    T("cad_doc"), f.read(),
                    file_name=os.path.basename(chemin),
                    mime="application/msword", use_container_width=True)
    else:
        st.info(T("cad_doc_absent"))
    if doc_complet is not None:
        with st.expander(T("cad_doc_lire")):
            doc_complet()
