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
import re
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
    # LA DÉFINITION REVIENT ICI, ET C'EST SA PLACE. Sur l'accueil elle
    # arrivait juste sous le sous-titre du bandeau, qui dit déjà ce qu'est le
    # site ; ici elle ouvre l'onglet qui porte son nom, et les trois attributs
    # en dessous la déplient.
    "cad_uma": {
        "en": "APRI measures the resilience of a landscape, understood as a "
              "complex adaptive system.",
        "fr": "APRI mesure la résilience d'un paysage, compris comme un "
              "système complexe adaptatif."},


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
    "cad_attr_x": {
        "en": "Resilience is measured through three attributes and seven "
              "dimensions.",
        "fr": "La résilience est mesurée à travers trois attributs et sept "
              "dimensions."},
    # LES DEUX FRAGMENTS QUE LA PHRASE MET EN AVANT. Ils sont écrits à part
    # pour être retrouvés dans la phrase et habillés de vert : les recopier
    # dans une chaîne HTML aurait fait deux versions du même texte à
    # maintenir, et la traduction aurait divergé au premier ajustement.
    "cad_attr_f1": {"en": "three attributes", "fr": "trois attributs"},
    "cad_attr_f2": {"en": "seven dimensions", "fr": "sept dimensions"},
    "cad_ec_pct": {"en": "Percentage", "fr": "Pourcentage"},
    "cad_ec_val": {"en": "Value", "fr": "Valeur"},
    "cad_ec_cro": {"en": "rising", "fr": "croissante"},
    "cad_ec_inv": {"en": "inverted", "fr": "inversée"},
    "cad_ec_pct_x": {
        "en": "The measure is a share of the population or of the cases.",
        "fr": "La mesure est une part de la population ou des cas."},
    "cad_ec_val_x": {
        "en": "The measure is not a percentage: an index, a count or a rate.",
        "fr": "La mesure n'est pas un pourcentage : un indice, un compte ou "
              "un taux."},
    "cad_ec_cro_x": {
        "en": "The score rises with the measured value.",
        "fr": "Le score monte avec la valeur mesurée."},
    "cad_ec_inv_x": {
        "en": "The score rises as the measured value falls.",
        "fr": "Le score monte quand la valeur mesurée baisse."},
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
    "cad_col_dim": {"en": "Dimension", "fr": "Dimension"},
    "cad_col_poids": {"en": "Weight in the index", "fr": "Poids dans l'indice"},
    "cad_col_couv": {"en": "Coverage", "fr": "Couverture"},
    "cad_col_ind": {"en": "Indicators", "fr": "Indicateurs"},

    # --- LA MÉTHODE DE CALCUL, EN TROIS TEMPS
    # LES NOMBRES DE L'EXEMPLE SONT UN EXEMPLE, et l'onglet le dit. Quarante-
    # cinq minutes pour aller chercher l'eau, 3,5 sur 10, 6,1 en score global :
    # ce sont des valeurs de démonstration choisies pour que la chaîne se
    # suive. Publiées sans mention, elles se liraient comme des résultats —
    # et le score global réel n'est pas 6,1.
    "cad_ex": {"en": "Example", "fr": "Exemple"},

    # --- la chaîne en cinq étapes ------------------------------------------
    "cad_e1_t": {"en": "Raw data", "fr": "Donnée brute"},
    "cad_e1_v": {"en": "45 min", "fr": "45 min"},
    "cad_e1_x": {"en": "Observed value, from surveys or spatial data.",
                 "fr": "Valeur observée, issue des enquêtes ou des données "
                       "spatiales."},
    # LA VALEUR EST CELLE DE TOUT L'ÉCHANTILLON, ET IL FAUT LE DIRE ICI.
    # « 72,8 % » posé seul sous « Donnée brute » se lit comme la valeur de
    # quelque chose qu'on aurait sélectionné ; c'est la mesure sur les mille
    # deux cent onze ménages, et l'écran ne porte aucun filtre qui pourrait
    # la restreindre.
    "cad_ex_ech": {
        "en": "Measured on the whole sample, {n} households.",
        "fr": "Mesurée sur tout l'échantillon, {n} ménages."},
    "cad_e2_t": {"en": "Normalise", "fr": "Normaliser"},
    "cad_e2_v": {"en": "Convert to a 0–10 scale",
                 "fr": "Ramener sur une échelle de 0 à 10"},
    "cad_e2_x": {"en": "The raw value is converted using statistical values "
                       "or reference thresholds.",
                 "fr": "La valeur brute est convertie à l'aide de valeurs "
                       "statistiques ou de seuils de référence."},
    "cad_e3_t": {"en": "Indicator score", "fr": "Score de l'indicateur"},
    "cad_e3_v": {"en": "3.5 / 10", "fr": "3,5 / 10"},
    "cad_e3_x": {"en": "Standardized score for this indicator.",
                 "fr": "Score normalisé de cet indicateur."},
    "cad_e4_t": {"en": "Weight & combine", "fr": "Pondérer et agréger"},
    "cad_e4_x": {"en": "Relative importance of this indicator.",
                 "fr": "Importance relative de cet indicateur."},
    "cad_e5_t": {"en": "Resilience score", "fr": "Score de résilience"},
    "cad_e5_v": {"en": "6.1 / 10", "fr": "6,1 / 10"},
    "cad_e5_x": {"en": "Weighted contribution to the dimension score.",
                 "fr": "Contribution pondérée au score de la dimension."},
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
    # LES DEUX LOGIQUES SONT CELLES DU CADRE, ET PAS UNE MISE À L'ÉCHELLE
    # QUELCONQUE. Cette colonne affichait la formule du min-max — le score
    # comme position entre la plus petite et la plus grande valeur observées
    # — que le référentiel n'emploie nulle part. Il en emploie deux autres,
    # et le choix entre elles tient à une seule chose : existe-t-il une
    # distribution empirique de référence à l'échelle internationale ? Si
    # oui, la valeur se situe dans cette distribution, par quantiles ; sinon,
    # deux scénarios locaux — l'optimal et le critique — bornent l'échelle,
    # découpée en neuf classes équidistantes.
    "cad_p2s_t": {"en": "Two normalisation logics",
                  "fr": "Deux logiques de normalisation"},
    "cad_p2s_x": {
        "en": "Which one applies depends on whether a robust comparative "
              "reference exists for the indicator.",
        "fr": "Laquelle s'applique dépend de l'existence, ou non, d'un cadre "
              "de référence comparatif robuste pour l'indicateur."},
    "cad_p2q_t": {"en": "Quantile-based discretization",
                  "fr": "Discrétisation par quantiles"},
    "cad_p2q_x": {
        "en": "When reliable empirical distributions exist at international "
              "or regional scale, the thresholds come from the indicator's "
              "empirical cumulative distribution at global level. The "
              "observed value becomes an ordinal score reflecting its "
              "position within that distribution, whatever its original "
              "unit.",
        "fr": "Quand des distributions empiriques fiables existent à "
              "l'échelle internationale ou régionale, les seuils viennent de "
              "la distribution cumulative empirique de l'indicateur au "
              "niveau mondial. La valeur observée devient un score ordinal "
              "qui dit sa position dans cette distribution, quelle qu'ait "
              "été son unité de départ."},
    "cad_p2n_t": {"en": "Local normative benchmark",
                  "fr": "Repère normatif local"},
    "cad_p2n_x": {
        "en": "When the attribute is highly context-specific and has no "
              "robust comparative reference, two locally defined scenarios "
              "bound the scale: the one considered optimal and the one "
              "considered critical for the socio-ecological system. The "
              "interval between them is cut into nine equidistant classes, "
              "which makes eleven ordinal scenarios.",
        "fr": "Quand l'attribut est très dépendant du contexte et n'a pas de "
              "cadre de référence comparatif robuste, deux scénarios définis "
              "localement bornent l'échelle : celui qu'on tient pour optimal "
              "et celui qu'on tient pour critique dans le système "
              "socio-écologique étudié. L'intervalle entre les deux est "
              "découpé en neuf classes équidistantes, ce qui fait onze "
              "scénarios ordinaux."},
    "cad_p2_sens": {
        "en": "A high score means a condition considered favourable or "
              "optimal in the local context; a low score, a condition likely "
              "to increase vulnerability.",
        "fr": "Un score élevé signale une situation tenue pour favorable ou "
              "optimale dans le contexte local ; un score bas, une situation "
              "de nature à accroître la vulnérabilité."},
    "cad_p2h": {"en": "Higher is better", "fr": "Plus, c'est mieux"},
    "cad_p2l": {"en": "Lower is better", "fr": "Moins, c'est mieux"},
    "cad_p2b_t": {"en": "The eleven ordinal scenarios",
                  "fr": "Les onze scénarios ordinaux"},
    "cad_p2b_x": {"en": "The scale this indicator is read against.",
                  "fr": "L'échelle sur laquelle cet indicateur se lit."},
    "cad_p2b_vide": {
        "en": "They appear once an indicator is chosen above.",
        "fr": "Ils apparaissent une fois un indicateur choisi ci-dessus."},
    # Les paliers sont écrits « borne → score », séparés par des barres.
    "cad_p2b_r": {"en": "≥ 120 min→0|60–120 min→2.5|30–60 min→5|"
                        "15–30 min→7.5|≤ 15 min→10",
                  "fr": "≥ 120 min→0|60–120 min→2,5|30–60 min→5|"
                        "15–30 min→7,5|≤ 15 min→10"},
    "cad_p2b_n": {
        "en": "Thresholds come either from the international empirical "
              "distribution or from the locally defined optimal and critical "
              "scenarios.",
        "fr": "Les seuils viennent soit de la distribution empirique "
              "internationale, soit des scénarios optimal et critique "
              "définis localement."},

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
    # --- les diagrammes de boucles causales, en quatre temps
    "cad_bt": {"en": "Causal loop diagrams",
               "fr": "Diagrammes de boucles causales"},
    "cad_b1_t": {"en": "The symptom", "fr": "Le symptôme"},
    "cad_b1_x": {"en": "Start from a critical indicator",
                 "fr": "Partir d'un indicateur critique"},
    "cad_b1_e": {"en": "Forest cover", "fr": "Couvert forestier"},
    "cad_b2_t": {"en": "The loop", "fr": "La boucle"},
    "cad_b2_x": {"en": "Understand what reinforces the problem",
                 "fr": "Comprendre ce qui renforce le problème"},
    "cad_b2_e": {"en": "Forest cover ↔ agricultural productivity",
                 "fr": "Couvert forestier ↔ productivité agricole"},
    "cad_b3_t": {"en": "The lever", "fr": "Le levier"},
    "cad_b3_x": {"en": "Identify where intervention can change the system",
                 "fr": "Repérer où une intervention change le système"},
    "cad_b3_e": {"en": "Clean cooking fuels",
                 "fr": "Combustibles propres de cuisson"},
    "cad_b4_t": {"en": "The action", "fr": "L'action"},
    "cad_b4_x": {"en": "Translate the lever into an intervention",
                 "fr": "Traduire le levier en intervention"},
    "cad_b4_e": {"en": "Action sheet + monitoring",
                 "fr": "Fiche d'action + suivi"},
    # LA MÉTHODE N'EST PAS DE NOUS, ET C'EST TOUT L'INTÉRÊT. Un diagramme de
    # boucles causales est un outil d'évaluation documenté, que le PNUD range
    # parmi ses méthodes ; le dire, références à l'appui, vaut mieux que de
    # laisser croire à une invention maison. Les quatre entrées sont celles qui
    # commandent réellement ce que fait cette page : la définition de la
    # méthode, la référence de construction, la construction à partir de
    # matériaux textuels, et un cas d'évaluation de politique publique.
    "cad_bm_t": {"en": "The method, and where it comes from",
                 "fr": "La méthode, et d'où elle vient"},
    "cad_bm_x": {
        "en": "A causal loop diagram is a documented evaluation method, not "
              "a house convention: UNDP lists it among the methods of its "
              "evaluation methods centre. Here it is built from relationships "
              "that each carry their source, not from opinions collected in a "
              "workshop.",
        "fr": "Un diagramme de boucles causales est une méthode d'évaluation "
              "documentée, et non une convention maison : le PNUD la range "
              "parmi les méthodes de son centre de méthodes d'évaluation. "
              "Elle est construite ici à partir de relations qui portent "
              "chacune leur source, et non d'avis recueillis en atelier."},
    # Chaque référence : auteur et année | ce qu'elle apporte | lien.
    "cad_bm_r": {
        "en": "UNDP, Causal Loop Diagrams, Evaluation Methods Centre|the "
              "method in an evaluation setting, and the questions it "
              "answers|https://erc.undp.org/methods-center/methods/"
              "evaluation-methods/causal-loop-diagrams"
              "@@Sterman (2000), Business Dynamics, McGraw-Hill|system "
              "boundary, time horizon, reading a loop|"
              "@@Kim and Andersen (2012), System Dynamics Review 28(3), "
              "311-328|building a causal map from textual material|"
              "https://doi.org/10.1002/sdr.1480"
              "@@Crabolu, Font and Eker (2023), Annals of Tourism Research "
              "100, 103572|a policy instrument evaluated with a causal loop "
              "diagram|https://doi.org/10.1016/j.annals.2023.103572",
        "fr": "PNUD, Causal Loop Diagrams, Centre de méthodes d'évaluation|"
              "la méthode en situation d'évaluation, et les questions "
              "auxquelles elle répond|https://erc.undp.org/methods-center/"
              "methods/evaluation-methods/causal-loop-diagrams"
              "@@Sterman (2000), Business Dynamics, McGraw-Hill|périmètre du "
              "système, horizon de temps, lecture d'une boucle|"
              "@@Kim et Andersen (2012), System Dynamics Review 28(3), "
              "311-328|construire une carte causale à partir de matériaux "
              "textuels|https://doi.org/10.1002/sdr.1480"
              "@@Crabolu, Font et Eker (2023), Annals of Tourism Research "
              "100, 103572|un instrument de politique publique évalué par un "
              "diagramme de boucles causales|"
              "https://doi.org/10.1016/j.annals.2023.103572"},
    "cad_bl_t": {"en": "How to read a loop", "fr": "Comment lire une boucle"},
    "cad_bl_p_t": {"en": "Same direction", "fr": "Même sens"},
    "cad_bl_p_x": {"en": "If A increases, B increases.",
                   "fr": "Si A augmente, B augmente."},
    "cad_bl_m_t": {"en": "Opposite direction", "fr": "Sens contraire"},
    "cad_bl_m_x": {"en": "If A increases, B decreases.",
                   "fr": "Si A augmente, B diminue."},
    "cad_bl_r": {"en": "R — Reinforcing", "fr": "R — Renforçante"},
    "cad_bl_r_x": {"en": "Amplifies change", "fr": "Amplifie le changement"},
    "cad_bl_b": {"en": "B — Balancing", "fr": "B — Équilibrante"},
    "cad_bl_b_x": {"en": "Counteracts change",
                   "fr": "Contrarie le changement"},
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

    "cad_so1_t": {"en": "Household survey", "fr": "Enquête ménage"},
    "cad_so1_x": {
        "en": "Information collected directly from households on "
              "livelihoods, assets, risk perception, preparedness and access "
              "to services.",
        "fr": "Informations recueillies directement auprès des ménages sur "
              "les moyens d'existence, les biens, la perception du risque, "
              "la préparation et l'accès aux services."},
    # DEUX PHRASES, ET NON SIX PUCES. « Questionnaires structurés », « Données
    # socio-économiques et institutionnelles », « Perceptions et
    # comportements » sont trois morceaux d'une seule et même phrase : ce que
    # le questionnaire couvre. « Quatre strates croisées », le tirage dans la
    # base de bâtiments et la justification de l'absence de redressement en
    # sont trois d'une autre : comment l'échantillon a été construit. Six
    # puces obligeaient le lecteur à faire lui-même ce raccord ; deux phrases
    # le lui donnent, et la seconde garde la réponse à la question que tout
    # lecteur averti pose, celle du redressement.
    "cad_so1_p": {
        "en": "Structured questionnaires covering socio-economic and "
              "institutional data, perceptions and behaviours."
              "|Four crossed strata (landscape, age, sex, economic "
              "category), drawn at random from a georeferenced building base "
              "(OpenStreetMap); the strata reproduce the population "
              "structure, so means by profile are unbiased and need no "
              "post-stratification weighting.",
        "fr": "Questionnaires structurés portant sur les données "
              "socio-économiques et institutionnelles, les perceptions et "
              "les comportements."
              "|Quatre strates croisées (paysage, âge, sexe, catégorie "
              "économique), tirées au hasard dans une base de bâtiments "
              "géoréférencés (OpenStreetMap) ; les strates reproduisent la "
              "structure de la population, si bien que les moyennes par "
              "profil sont sans biais et n'appellent aucun redressement."},

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
    "cad_c1": {"en": "Resilience model", "fr": "Modèle de résilience"},
    "cad_c2": {"en": "Sources and data", "fr": "Sources et données"},
    "cad_c3": {"en": "Dimensions", "fr": "Dimensions"},
    # L'ONGLET PORTE LE NOM DU CHEMIN, PAS CELUI DE SON INVENTAIRE. Depuis
    # qu'il déroule la chaîne de calcul sur l'indicateur ouvert, « Indicateurs
    # et pondérations » n'annonçait plus que la moitié de ce qu'on y trouve.
    "cad_c35": {"en": "From Indicators to Resilience Scores",
                "fr": "Des indicateurs aux scores de résilience"},
    "cad_ind_dim": {"en": "Dimension", "fr": "Dimension"},
    "cad_ind_all": {"en": "All seven", "fr": "Toutes les sept"},
    "cad_ind_q": {"en": "Search an indicator", "fr": "Chercher un indicateur"},
    "cad_ind_c_nom": {"en": "Indicator", "fr": "Indicateur"},
    "cad_ind_c_ech": {"en": "Normalisation scale, 0 to 10",
                      "fr": "Échelle de normalisation, de 0 à 10"},
    "cad_ind_c_p": {"en": "Weight", "fr": "Pondération"},
    "cad_ind_c_p_ech": {"en": "1 to 5", "fr": "de 1 à 5"},
    "cad_ind_haut": {"en": "higher is better", "fr": "plus, c'est mieux"},
    "cad_ind_bas": {"en": "lower is better", "fr": "moins, c'est mieux"},
    "cad_ind_sans": {"en": "no scale written in the reference file",
                     "fr": "aucune échelle écrite dans le référentiel"},
    # RIEN TANT QU'ON N'A RIEN DEMANDÉ. La ligne dit quoi faire, pas ce qui
    # manque : c'est un écran de départ, pas une erreur.
    "cad_ind_vide": {
        "en": "Pick an indicator to see its scale, its weight and the chain "
              "that turns its raw measure into a score.",
        "fr": "Choisissez un indicateur pour voir son barème, sa pondération "
              "et la chaîne qui transforme sa mesure brute en score."},
    "cad_ind_ind": {"en": "Indicator", "fr": "Indicateur"},
    "cad_ind_tous": {"en": "Choose an indicator",
                     "fr": "Choisir un indicateur"},
    # LES CINQ ÉTAPES, DITES SUR L'INDICATEUR QU'ON REGARDE. Les mêmes
    # intitulés que la chaîne d'exemple ; seules les valeurs changent.
    "cad_ex_seuils": {"en": "Using predefined thresholds.",
                      "fr": "À partir de seuils prédéfinis."},
    "cad_ex_stat": {"en": "Using the observed range of values.",
                    "fr": "À partir de l'étendue des valeurs observées."},
    "cad_ex_sc_non": {"en": "not computed", "fr": "non calculé"},
    "cad_ex_sc_non_x": {
        "en": "This indicator is measured but its score is not yet in the "
              "reference file.",
        "fr": "Cet indicateur est mesuré, mais son score ne figure pas "
              "encore dans le fichier de référence."},
    "cad_ex_p": {"en": "Weight {p} out of 5", "fr": "Pondération {p} sur 5"},
    "cad_ex_p_x": {"en": "Relative importance of this indicator.",
                   "fr": "Importance relative de cet indicateur."},
    "cad_ex_dim": {"en": "Score of the dimension",
                   "fr": "Score de la dimension"},
    "cad_ex_dim_x": {"en": "Weighted contribution to the dimension score.",
                     "fr": "Contribution pondérée au score de la "
                           "dimension."},
    "cad_ex_res": {"en": "Result:", "fr": "Résultat :"},
    "cad_ex_c_val": {"en": "Raw value", "fr": "Valeur brute"},
    "cad_ex_c_sc": {"en": "Score (0–10)", "fr": "Score (0–10)"},
    "cad_ex_p_v": {"en": "{p} / 5", "fr": "{p} / 5"},
    "cad_ex_titre": {
        "en": "From this measure to a resilience score",
        "fr": "De cette mesure à un score de résilience"},
    "cad_ex_gen": {
        "en": "From a raw measure to a resilience score",
        "fr": "De la mesure brute au score de résilience"},
    "cad_ex_seuils_i": {
        "en": "The eleven bands of this indicator",
        "fr": "Les onze paliers de cet indicateur"},
    "cad_ind_rien": {"en": "No indicator matches this search.",
                     "fr": "Aucun indicateur ne correspond à cette recherche."},
    "cad_ind_n": {"en": "{k} of {n} indicators shown.",
                  "fr": "{k} indicateurs affichés sur {n}."},
    "cad_ind_pds": {
        "en": "Weights run from {a} to {b}. They were set by a panel of "
              "experts, and a dimension's weight is the sum of its own "
              "indicators' — no dimension was weighted directly.",
        "fr": "Les pondérations vont de {a} à {b}. Elles ont été fixées par un "
              "groupe d'experts, et la pondération d'une dimension est la "
              "somme de celles de ses indicateurs — aucune dimension n'a été "
              "pondérée directement."},
    "cad_c5": {"en": "Feedback loops", "fr": "Boucles de rétroaction"},
    "cad_c6": {"en": "Environmental data", "fr": "Données environnementales"},
    "cad_c7": {"en": "The full framework", "fr": "Le cadre complet"},
    # LA LIGNE SOUS CHAQUE ONGLET DIT CE QU'ON Y TROUVE, pas comment il
    # s'appelle : « Sources et données » oblige à cliquer pour savoir,
    # « d'où viennent les mesures » laisse choisir depuis la barre.
    "cad_d1": {"en": "Three attributes, seven dimensions",
               "fr": "Trois attributs, sept dimensions"},
    "cad_d2": {"en": "Where the measures come from",
               "fr": "D'où viennent les mesures"},
    "cad_d35": {"en": "One indicator, its scale and what it becomes",
                "fr": "Un indicateur, son barème et ce qu'il devient"},
    "cad_d5": {"en": "Reading a system that answers itself",
               "fr": "Lire un système qui se répond à lui-même"},
    "cad_d6": {"en": "The dimension no household can answer for",
               "fr": "La dimension qu'aucun ménage ne peut décrire"},
    "cad_d7": {"en": "The reference document, in full",
               "fr": "Le document de référence, en entier"},
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



# LE CODE COULEUR DU RÉFÉRENTIEL, RECOPIÉ SCORE PAR SCORE. La planche des
# scénarios comparatifs internationaux pose onze aplats nommés, du rouge vif
# pour zéro au vert sombre pour dix, en passant par l'orange, le jaune et le
# tilleul. C'est ce nuancier-là que les lecteurs de la méthode ont sous les
# yeux ; une interpolation entre trois ancres en donnait une version plus
# terne, sans jaune franc au milieu, et la barre du site ne disait plus tout
# à fait la même chose que la planche. Les onze valeurs sont donc écrites
# telles quelles, dans l'ordre des scores.
_ECHELLE = ("#e92720", "#f45b1f", "#f9ac23", "#fdd019", "#fce829",
            "#c7db33", "#6fc63a", "#43932f", "#336b2b", "#2b5626",
            "#1f4019")


def _teinte(t):
    """La couleur d'un score, du rouge au vert sombre.

    L'ARGUMENT EST UNE FRACTION, PAS UN SCORE. Tous les barèmes ne vont pas
    jusqu'à dix — certains s'arrêtent à trois ou à cinq — et l'appelant
    divise déjà par son maximum. La fraction est ramenée sur les onze crans
    du nuancier, ce qui donne le rouge en bas, le vert sombre en haut, et les
    teintes intermédiaires réparties entre les deux quel que soit le nombre
    de crans du barème.
    """
    t = max(0.0, min(1.0, t))
    return _ECHELLE[int(round(t * (len(_ECHELLE) - 1)))]


def _encre(couleur):
    """L'encre lisible sur un aplat : blanche sur le sombre, sombre sur le clair.

    LE BLANC NE TIENT PAS SUR LE JAUNE. Les pastilles portaient leur chiffre
    en blanc quelle que soit la bande ; sur le rouge et les verts, cela se
    lit, mais sur l'orange clair, le jaune et le tilleul — les scores 2 à 5 —
    le chiffre disparaissait. La luminance décide, et non le rang.
    """
    r, v, b = (int(couleur[i:i + 2], 16) for i in (1, 3, 5))
    return "#22261a" if (0.299 * r + 0.587 * v + 0.114 * b) > 150 else "#fff"


_RE_NOMBRE = re.compile(r"\d+(?:[.,]\d+)?")

# UN BARÈME NE S'ÉCRIT PAS D'UNE SEULE FAÇON DANS LE RÉFÉRENTIEL, et la règle
# graduée ne doit pas dépendre de la ponctuation qu'un rédacteur a choisie.
# « 0 (≤5%), 1 (5–15%) », « 0: 0–5 % | 1: >5–15 % », « 0 (≥95,0%], 1
# (85,0–95,0%] », « 0 = 0, 1 > 0–0,40 » et « 0(0) 1(1) 2(2) » disent tous la
# même chose : un score, puis sa borne. Le repère est donc le SCORE lui-même
# — un entier de 0 à 10 en tête de segment, suivi d'une borne — et tout ce
# qui le sépare du suivant est cette borne, quelle qu'en soit la forme.
_RE_BORNE = re.compile(
    r"(?:^|[\s,;|:])\s*(10|\d)\s*[:=]?\s*(?=[(\[≥≤<>]|\s|$)")


def _bandes_css():
    """Les onze aplats de la règle graduée, dans l'ordre des scores.

    LA BARRE ET LES PASTILLES LISENT LE MÊME NUANCIER. Si `_ECHELLE` change
    un jour, les deux changent ensemble ; deux listes de couleurs séparées
    auraient divergé au premier ajustement.
    """
    p = 100.0 / len(_ECHELLE)
    return ", ".join(f"{c} {i * p:.4f}% {(i + 1) * p:.4f}%"
                     for i, c in enumerate(_ECHELLE))


def _bandes(txt):
    """Le barème lu comme une suite {score: borne}, quelle que soit sa forme.

    CINQ SCORES AU MOINS, ET LA MOITIÉ AVEC UNE BORNE. En dessous, ce n'est
    pas une règle graduée mais une définition en prose — « 0 : absence ou une
    seule espèce très tolérante ; 10 : richesse spécifique élevée » — et une
    prose ne se met pas en curseur : elle s'affiche telle quelle.
    """
    if not txt:
        return {}
    ms = list(_RE_BORNE.finditer(txt))
    out = {}
    for k, m in enumerate(ms):
        fin = ms[k + 1].start() if k + 1 < len(ms) else len(txt)
        out.setdefault(int(m.group(1)),
                       " ".join(txt[m.end():fin].split()).strip(",;|").strip())
    if len(out) < 5 or sum(1 for v in out.values() if v) < len(out) // 2:
        return {}
    return out


def _type_echelle(par):
    """De quelle sorte de barème il s'agit : son unité et son sens.

    DEUX BARÈMES DE MÊME FORME NE SE LISENT PAS PAREIL. « ≤ 15,8 % » pour le
    zéro et « ≥ 97 % » pour le dix : le score monte avec la mesure. « ≥ 100 »
    pour le zéro et « 0–9 » pour le dix : il monte quand elle baisse. Les
    deux règles se ressemblent trait pour trait à l'écran, et rien ne disait
    laquelle on lisait — d'où des indicateurs qu'on croyait mauvais alors
    qu'ils sont bons.

    LE SENS SE DÉDUIT DES BORNES, IL NE SE DÉCLARE PAS. Le fichier ne porte
    pas de champ « sens » ; le comparer serait une saisie de plus à tenir à
    jour. La borne du zéro et celle du dix suffisent : si la première est
    numériquement plus haute que la seconde, le barème est inversé.
    """
    bas, haut = par[min(par)], par[max(par)]
    unite = "pct" if "%" in bas + haut else "val"

    def _n(t):
        v = [float(x.replace(",", ".")) for x in _RE_NOMBRE.findall(t)]
        return sum(v) / len(v) if v else None

    a, b = _n(bas), _n(haut)
    sens = None if a is None or b is None else ("inv" if a > b else "cro")
    bouts = [(T("cad_ec_" + unite), T("cad_ec_" + unite + "_x"))]
    if sens:
        bouts.append((T("cad_ec_" + sens), T("cad_ec_" + sens + "_x")))
    return (f'<span class="cad-ec-t" title="'
            f'{_e(" ".join(x for _m, x in bouts))}">'
            + " · ".join(_e(mot) for mot, _x in bouts) + '</span>')


def _echelle_html(txt):
    """Le barème en règle glissante : on promène le curseur, le seuil suit.

    ONZE BORNES NE TIENNENT PAS DANS UNE CELLULE DE TABLEAU. Écrites côte à
    côte, elles débordaient sur quatre lignes et repoussaient la ligne
    suivante ; réduites à trois repères, elles n'en montraient plus que trois.
    La règle résout les deux : les onze seuils sont là, mais un seul à la
    fois — celui du score que l'on désigne.

    ZÉRO ET DIX RESTENT ÉCRITS, PARCE QU'ILS SONT LA QUESTION QU'ON SE POSE.
    « À partir de quand est-ce zéro, à partir de quand est-ce dix » est la
    lecture qu'on fait d'un barème neuf fois sur dix ; elle ne doit pas
    demander un geste. Les scores 1 à 9 se lisent en glissant dessus.

    TOUT EST EN CSS, ET C'EST LA CONTRAINTE QUI COMMANDE. Le tableau est
    rendu en HTML dans une page Streamlit, où aucun script ne s'exécute : le
    survol est donc le seul geste disponible, et onze zones transparentes
    posées sur la barre suffisent à le rendre continu comme un glissement.
    """
    if not txt:
        return f'<span style="color:#a7b0be">{_e(T("cad_ind_sans"))}</span>'
    par = _bandes(txt)
    if not par:
        return _e(txt)
    nmax = max(par) or 1
    scores = sorted(par)

    zones, lignes = [], []
    for k, i in enumerate(scores):
        g = 100.0 * k / len(scores)
        zones.append(f'<span class="cad-ec-z" data-i="{i}" '
                     f'style="left:{g:.3f}%;width:{100.0 / len(scores):.3f}%">'
                     f'</span>')
        _c = _teinte(i / nmax)
        lignes.append(f'<span class="cad-ec-v" data-i="{i}">'
                      f'<b style="background:{_c};color:{_encre(_c)}">{i}</b>'
                      f'{_e(par[i])}</span>')
    bas, haut = scores[0], scores[-1]
    _c0, _c1 = _teinte(0), _teinte(1)
    defaut = (f'<span class="cad-ec-d">'
              f'<span class="cad-ec-u"><b style="background:{_c0};'
              f'color:{_encre(_c0)}">'
              f'{bas}</b>{_e(par[bas])}</span>'
              f'<span class="cad-ec-u"><b style="background:{_c1};'
              f'color:{_encre(_c1)}">'
              f'{haut}</b>{_e(par[haut])}</span></span>')
    return (f'<span class="cad-ec">{_type_echelle(par)}'
            f'<span class="cad-ec-b"></span>{"".join(zones)}'
            f'<span class="cad-ec-l">{defaut}{"".join(lignes)}</span></span>')


@st.cache_data(show_spinner=False)
def _referentiel():
    """Les indicateurs du référentiel, tels qu'ils y sont écrits.

    ON NE RECOMPOSE RIEN. L'échelle de normalisation est reprise telle quelle
    du fichier : c'est le barème qui a servi au calcul, et le réécrire en plus
    joli, c'est risquer d'en publier un qui n'est pas celui qui a tourné.
    """
    p = _trouver("resultats.json")
    if not p:
        return []
    with open(p, encoding="utf-8") as f:
        res = json.load(f)
    res = res["indicateurs"] if isinstance(res, dict) and "indicateurs" in res \
        else res
    out = []
    for r in res:
        cle = DIM_CLE.get(r.get("dimension", ""))
        if not cle:
            continue
        ech = (r.get("echelle") or "").strip()
        # Le préfixe « CE : » est une convention de saisie, pas un contenu.
        for pre in ("CE :", "CE:"):
            if ech.startswith(pre):
                ech = ech[len(pre):].strip()
        out.append({
            "ligne": r.get("ligne"), "dim": cle,
            "nom": r.get("indicateur") or "",
            "metrique": (r.get("metrique") or "").strip(),
            "poids": float(r.get("ponderation") or 1),
            "echelle": ech,
            "sens": r.get("sens") or "",
            # LA VALEUR ET LE SCORE PUBLIÉS SUIVENT L'INDICATEUR. La chaîne
            # de calcul ne s'explique bien que sur un cas : sans eux, elle
            # resterait l'exemple des quarante-cinq minutes de marche.
            "valeur": (r.get("valeurs") or {}).get("Total"),
            "score": (r.get("scores_corriges") or {}).get("Total"),
            "metrique_fr": (r.get("expl_fr") or "").strip(),
            "nom_fr": (r.get("indicateur_fr") or "").strip(),
            "calcule": (r.get("scores_corriges") or {}).get("Total")
                       is not None})
    out.sort(key=lambda x: (ORDRE.index(x["dim"]) if x["dim"] in ORDRE else 99,
                            -x["poids"]))
    return out


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

  /* --- les quatre sources, en quatre colonnes séparées de filets ----------
     RIEN N'EST ENCADRÉ. Quatre cartes blanches se lisent comme quatre boutons
     et alignent leur hauteur sur la plus haute — celle de l'enquête ménage,
     qui porte le plan de sondage — ce qui laissait trois grands vides. Le
     filet vertical sépare sans encadrer, et chaque colonne prend la hauteur
     qu'elle demande.

     LES PUCES SONT DES TIRETS. Le rond plein appelle une liste d'items de
     même nature ; ce sont ici des précisions de protocole, de longueurs très
     inégales, que le tiret introduit sans les aligner de force. */
  .cad-so   { display:grid; gap:0; margin-top:6px;
              grid-template-columns:repeat(4,1fr); }
  .cad-so-b { padding:2px 26px 4px; border-left:1px solid #e9eef4; }
  .cad-so-b:first-child { border-left:0; padding-left:0; }
  @media (max-width: 1150px) {
    .cad-so { grid-template-columns:repeat(2,1fr); row-gap:26px; }
    .cad-so-b:nth-child(3) { border-left:0; padding-left:0; }
  }
  @media (max-width: 700px) {
    .cad-so { grid-template-columns:1fr; }
    .cad-so-b { border-left:0; padding-left:0; }
  }
  .cad-so-h { display:flex; align-items:center; gap:11px; margin:0 0 12px; }
  .cad-so-n { font-size:27px; font-weight:200; color:#1a6b52; line-height:1;
              font-variant-numeric:tabular-nums; }
  .cad-so-t { font-size:14px; font-weight:700; color:#1a6b52;
              letter-spacing:-.01em; line-height:1.25;
              padding-left:11px; border-left:1px solid #cfe0d6; }
  p.cad-so-x { font-size:12.5px !important; color:#3c4761 !important;
              line-height:1.55 !important; margin:0 0 12px !important;
              text-align:left !important; }
  .cad-so-l { list-style:none; padding:0; margin:10px 0 0; }
  /* AU FIL DE L'EAU, ET NON JUSTIFIÉ. Une phrase de quatre lignes dans une
     colonne de quatre creusait des rivières blanches entre les mots ; la
     colonne est trop étroite pour que la justification tienne. */
  .cad-so-l li { position:relative; padding-left:16px; margin-bottom:7px;
              font-size:12px; color:#3c4761; line-height:1.45;
              text-align:left; }
  .cad-so-l li::before { content:"–"; position:absolute; left:0;
              color:#8a93a5; }
  .cad-so-k { margin:0 0 9px; }
  .cad-so-k > div { display:flex; align-items:baseline; gap:9px;
              padding:2px 0; }
  .cad-so-k b { flex:0 0 auto; min-width:38px; font-size:14px;
              font-weight:700; color:#101728; letter-spacing:-.02em;
              font-variant-numeric:tabular-nums; }
  .cad-so-k span { font-size:11.5px; color:#5a6a80; line-height:1.35;
              text-align:left !important; }

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
  /* --- les diagrammes de boucles causales ---------------------------------
     LE PARCOURS EN QUATRE TEMPS, PUIS LA CONVENTION DE NOTATION, séparés par
     un filet. Le premier explique une démarche, la seconde une écriture :
     les mettre à la suite sans rien entre eux les ferait lire comme six
     étapes d'une même chose. */
  .cad-bt { font-size:27px; font-weight:700; color:#1a4d3a;
       font-family:Georgia,"Times New Roman",serif; letter-spacing:-.01em;
       margin:2px 0 4px; }
  .cad-bp { display:flex; align-items:flex-start; gap:0; margin:0 0 8px; }
  .cad-bp-e { flex:1 1 0; min-width:0; display:flex; flex-direction:column;
       align-items:center; text-align:center; padding:0 12px; }
  .cad-bp-fl { flex:0 0 46px; display:flex; justify-content:center;
       padding-top:44px; }
  .cad-bp-i { width:96px; height:96px; border-radius:50%; flex:0 0 96px;
       display:flex; align-items:center; justify-content:center; }
  .cad-bp-t { font-size:13px; font-weight:700; letter-spacing:.06em;
       line-height:1.3; margin-top:4px; }
  .cad-bp-x { font-size:13px; color:#101728; line-height:1.45; margin-top:9px;
       max-width:26ch; }
  .cad-bp-ex { font-size:12.5px; color:#5a6a80; font-style:italic;
       line-height:1.45; margin-top:9px; max-width:26ch; }
  @media (max-width: 1100px) {
    .cad-bp { flex-wrap:wrap; row-gap:26px; }
    .cad-bp-e { flex:1 1 44%; }
    .cad-bp-fl { display:none; }
  }
  .cad-bl { border-top:1px solid #e9eef4; margin-top:26px; padding-top:20px; }
  .cad-bl-h { font-size:12.5px; font-weight:700; letter-spacing:.09em;
       color:#101728; text-align:center; margin-bottom:20px; }
  .cad-bl-g { display:grid; gap:0 26px; align-items:center;
       grid-template-columns:1fr 1.15fr 1fr; }
  .cad-bl-g > div:nth-child(2) { border-left:1px solid #e9eef4;
       border-right:1px solid #e9eef4; padding:0 26px; }
  /* LA TROISIÈME CASE PORTE LA DÉFINITION. Elle était vide depuis que la
     grille compte trois colonnes ; la phrase qui ouvrait l'onglet s'y lit
     maintenant, en gris et en italique, comme la conclusion des deux
     dessins qui la précèdent. */
  .cad-bl-u { font-size:13.5px; color:#3c4761; line-height:1.6;
       font-style:italic; padding-left:4px; }
  /* LES RÉFÉRENCES DE LA MÉTHODE. Un filet les sépare de la lecture d'une
     boucle : ce n'est plus le mode d'emploi, c'est ce sur quoi il s'appuie.
     Deux colonnes tant que la page est large — quatre lignes empilées se
     lisent comme une bibliographie, deux colonnes comme un appui. */
  .cad-bm { border-top:1px solid #e9eef4; margin-top:24px; padding-top:18px; }
  .cad-bm-h { font-size:11.5px; font-weight:700; letter-spacing:.13em;
       text-transform:uppercase; color:#1a4d3a; margin-bottom:8px; }
  .cad-bm-x { font-size:13.5px; color:#3c4761; line-height:1.62;
       margin:0 0 14px; max-width:96ch; text-align:left !important; }
  .cad-bm-l { display:grid; grid-template-columns:1fr 1fr; gap:10px 32px; }
  .cad-bm-e { font-size:12.5px; line-height:1.5; color:#6b7590;
       padding-left:12px; border-left:2px solid #dbe6df; }
  .cad-bm-e b { display:block; font-weight:600; color:#101728;
       font-size:13px; }
  .cad-bm-e a { color:#1a6b52; text-decoration:none; }
  .cad-bm-e a:hover { text-decoration:underline; }
  @media (max-width: 1000px) { .cad-bm-l { grid-template-columns:1fr; } }
  @media (max-width: 1000px) {
    .cad-bl-g { grid-template-columns:1fr; row-gap:26px; }
    .cad-bl-g > div:nth-child(2) { border:0; padding:0; }
  }
  .cad-bs { display:flex; align-items:flex-start; gap:14px; margin-bottom:22px; }
  .cad-bs-p { width:46px; height:46px; flex:0 0 46px; border-radius:50%;
       display:flex; align-items:center; justify-content:center;
       font-size:19px; font-weight:700; }
  .cad-bs-t { font-size:13px; font-weight:700; }
  .cad-bs-x { font-size:12.5px; color:#3c4761; margin-top:3px;
       line-height:1.45; }
  .cad-bs-f { font-size:12.5px; color:#5a6a80; margin-top:5px;
       font-variant-numeric:tabular-nums; }
  .cad-bl-d { display:flex; gap:14px; }
  .cad-bl-d > div { flex:1 1 0; text-align:center; }
  .cad-bl-n { font-size:13px; font-weight:700; margin-top:6px; }
  .cad-bl-s { font-size:12px; color:#5a6a80; margin-top:3px; }

  /* --- la liste des indicateurs -------------------------------------------
     L'ÉCHELLE PREND LA COLONNE LA PLUS LARGE. Onze paliers écrits à la suite
     tiennent sur deux ou trois lignes ; le nom de l'indicateur, lui, tient
     sur une ou deux. C'est donc l'échelle qui commande la largeur. */
  .cad-it { width:100%; border-collapse:collapse; margin-top:14px; }
  /* PAS DE TRAITS ENTRE LES COLONNES. Streamlit encadre toute cellule de
     tableau écrite en markdown : trois colonnes se retrouvaient enfermées
     dans une grille alors qu'un filet horizontal sous chaque ligne suffit à
     les tenir. On ne laisse que celui-là. */
  .cad-it th, .cad-it td {
       border-left:0 !important; border-right:0 !important;
       border-top:0 !important; }
  .cad-it th { font-size:10.5px; font-weight:700; letter-spacing:.09em;
       text-transform:uppercase; color:#8a93a5; text-align:left;
       padding:0 14px 8px 0; border-bottom:1px solid #e9eef4; }
  .cad-it th.n, .cad-it td.n { text-align:right; }
  .cad-it td { padding:11px 14px 11px 0; border-bottom:1px solid #f2f5f9;
       vertical-align:top; }
  .cad-it td:first-child { width:30%; }
  .cad-it td:last-child { width:86px; }
  .cad-it-n { font-size:12.5px; font-weight:600; color:#101728;
       line-height:1.35; }
  .cad-it-d { font-size:11px; color:#8a93a5; margin-top:3px;
       line-height:1.35; }
  .cad-it-r { color:#2a6b3f; font-weight:700; }
  .cad-it-e { font-size:11.5px !important; color:#3c4761 !important;
       line-height:1.55 !important; text-align:left !important;
       font-variant-numeric:tabular-nums; }
  /* L'ÉCHELLE, SOUS L'INTITULÉ DE COLONNE : plus petite, en minuscules, et
     sans graisse — c'est une unité, pas un second titre. */
  .cad-it-ech { display:block; font-size:9.5px; font-weight:500;
        letter-spacing:.02em; text-transform:none; color:#a7b0be;
        margin-top:2px; }
  /* LA RÈGLE GRADUÉE : ONZE PASTILLES, CHACUNE AVEC SA BORNE À CÔTÉ. Le
     numéro seul dans une case colorée obligeait à survoler pour lire le
     seuil, et les trois repères écrits dessous n'en donnaient que trois sur
     onze. Chaque score porte donc sa borne, immédiatement à sa droite ; la
     couleur dit le sens, le chiffre dit le rang, le texte dit le seuil. */
  .cad-ec { position:relative; display:block; min-width:230px;
       padding:2px 0 2px; }
  /* LE TYPE DE BARÈME, AU-DESSUS DE LA RÈGLE : son unité, puis son sens. Deux
     règles de même forme ne se lisent pas pareil selon que le score monte
     avec la mesure ou contre elle. */
  .cad-ec-t { display:block; font-size:9.5px; font-weight:700;
       letter-spacing:.07em; text-transform:uppercase; color:#a7b0be;
       margin-bottom:5px; cursor:help; }
  /* ONZE APLATS, PAS UN DÉGRADÉ. Tant que la barre était continue, la
     couleur sous le trait du cran 7 n'était pas celle de la pastille 7 : le
     dégradé passait par des teintes intermédiaires qu'aucun score ne porte.
     Depuis que les crans découpent la barre, chaque segment doit être
     exactement la couleur de son score — c'est la même fonction `_teinte`
     qui peint la pastille et la bande. */
  .cad-ec-b { position:relative; display:block; height:9px; border-radius:5px;
       background:linear-gradient(90deg,__BANDES__); }
  /* ONZE SEGMENTS, DONC DIX TRAITS. Le dégradé seul ne dit pas où finit un
     score et où commence le suivant : on voyait une couleur continue et il
     fallait deviner que le curseur sautait par crans. Les traits blancs
     découpent la barre en onze parts égales, une par score, et le geste de
     glisser devient lisible avant même d'être fait. */
  .cad-ec-b::after { content:""; position:absolute; inset:0;
       border-radius:5px;
       background:repeating-linear-gradient(90deg,
           #fff 0 2px,
           transparent 2px calc(100% / 11)); }
  .cad-ec-z { position:absolute; top:2px; height:22px; cursor:ew-resize; }
  .cad-ec-z:hover::before { content:""; position:absolute; left:50%;
       transform:translateX(-50%); top:1px; width:4px; height:20px;
       border-radius:3px; background:#101728;
       box-shadow:0 0 0 2px #fff; }
  .cad-ec-l { display:flex; flex-wrap:wrap; gap:3px 14px; margin-top:7px;
       min-height:17px; }
  .cad-ec-d { display:flex; gap:14px; flex-wrap:wrap; }
  .cad-ec-u, .cad-ec-v { display:inline-flex; align-items:center; gap:5px;
       font-size:11px; color:#3c4761; white-space:nowrap;
       font-variant-numeric:tabular-nums; }
  .cad-ec-v { display:none; }
  .cad-ec-u b, .cad-ec-v b { display:inline-flex; align-items:center;
       justify-content:center; width:17px; height:17px; border-radius:4px;
       color:#fff; font-size:9.5px; font-weight:700; flex:0 0 17px; }
  /* ZÉRO ET DIX NE DISPARAISSENT PAS QUAND ON GLISSE. Ce sont les deux
     bornes qu'on lit sans y penser ; le score désigné vient s'ajouter à
     côté d'elles, il ne les remplace pas. Les deux seules exceptions sont
     le survol du zéro et celui du dix, où la valeur serait écrite deux
     fois. */
  .cad-ec-z[data-i="0"]:hover ~ .cad-ec-l > .cad-ec-d,
  .cad-ec-z[data-i="10"]:hover ~ .cad-ec-l > .cad-ec-d { display:none; }
  .cad-ec-z[data-i="0"]:hover ~ .cad-ec-l > .cad-ec-v[data-i="0"] { display:inline-flex; }
  .cad-ec-z[data-i="1"]:hover ~ .cad-ec-l > .cad-ec-v[data-i="1"] { display:inline-flex; }
  .cad-ec-z[data-i="2"]:hover ~ .cad-ec-l > .cad-ec-v[data-i="2"] { display:inline-flex; }
  .cad-ec-z[data-i="3"]:hover ~ .cad-ec-l > .cad-ec-v[data-i="3"] { display:inline-flex; }
  .cad-ec-z[data-i="4"]:hover ~ .cad-ec-l > .cad-ec-v[data-i="4"] { display:inline-flex; }
  .cad-ec-z[data-i="5"]:hover ~ .cad-ec-l > .cad-ec-v[data-i="5"] { display:inline-flex; }
  .cad-ec-z[data-i="6"]:hover ~ .cad-ec-l > .cad-ec-v[data-i="6"] { display:inline-flex; }
  .cad-ec-z[data-i="7"]:hover ~ .cad-ec-l > .cad-ec-v[data-i="7"] { display:inline-flex; }
  .cad-ec-z[data-i="8"]:hover ~ .cad-ec-l > .cad-ec-v[data-i="8"] { display:inline-flex; }
  .cad-ec-z[data-i="9"]:hover ~ .cad-ec-l > .cad-ec-v[data-i="9"] { display:inline-flex; }
  .cad-ec-z[data-i="10"]:hover ~ .cad-ec-l > .cad-ec-v[data-i="10"] { display:inline-flex; }
  .cad-it-p { font-size:13px; font-weight:700; color:#101728;
       font-variant-numeric:tabular-nums; }
  /* --- la chaîne de calcul en cinq étapes ---------------------------------
     UNE RANGÉE, CINQ COLONNES ÉGALES, DES CHEVRONS ENTRE ELLES. La chaîne se
     lit de gauche à droite comme une phrase : la donnée entre à gauche, le
     score sort à droite. Empilée, elle deviendrait une liste d'opérations —
     ce qu'elle était avant, et ce qui ne montrait rien.

     LE PICTOGRAMME EST DANS UN DISQUE PÂLE, ET LE DISQUE EST LE MÊME PARTOUT :
     c'est lui qui aligne les cinq colonnes à la même hauteur, quel que soit
     le nombre de lignes du texte au-dessus. */
  /* LE NUMÉRO EST DANS LA LIGNE DE TITRE, ET LE FILET COURT SOUS LES DEUX.
     Un intitulé centré, en petites capitales vertes, au-dessus d'un chiffre
     centré : la colonne se lisait comme une pastille de tableau de bord, et
     rien ne disait dans quel ordre les cinq se suivent. Le numéro dans sa
     pastille, le titre à côté de lui, un filet clair sous la ligne : c'est un
     en-tête d'étape, et l'ordre se lit sans compter les chevrons. */
  .cad-ch { display:flex; align-items:stretch; gap:0; margin:8px 0 30px; }
  .cad-ch-e { flex:1 1 0; min-width:0; display:flex; flex-direction:column;
              align-items:flex-start; text-align:left; padding:0 14px 0 0; }
  .cad-ch-fl { flex:0 0 44px; display:flex; align-items:flex-start;
               justify-content:center; padding-top:46px; }
  .cad-ch-h { display:flex; align-items:center; gap:9px; width:100%;
              padding-bottom:11px; margin-bottom:15px;
              border-bottom:1px solid #e4eae6; }
  .cad-ch-n { width:22px; height:22px; flex:0 0 22px; border-radius:50%;
              background:#eef3f0; color:#1a6b52; font-size:11.5px;
              font-weight:700; display:flex; align-items:center;
              justify-content:center; }
  .cad-ch-t { font-size:13px; font-weight:700; color:#101728;
              line-height:1.25; }
  .cad-ch-v { font-size:25px; font-weight:700; color:#101728;
              letter-spacing:-.02em; line-height:1.2; }
  /* LA CASE EN ATTENTE. Le tiret occupe la place du chiffre pour que la
     rangée garde sa hauteur, en gris pâle pour qu'on ne le lise pas comme
     une valeur mesurée. */
  .cad-ch-vide { color:#c3cbd4 !important; }
  /* LA DEUXIÈME ÉTAPE N'A PAS DE CHIFFRE À MONTRER, ELLE A UNE OPÉRATION À
     NOMMER. « Ramener sur une échelle de 0 à 10 » en corps vingt-cinq ferait
     une phrase géante entre deux nombres ; en corps quatorze, gras, elle
     tient le même rang sans crier. */
  .cad-ch-o { font-size:14px; font-weight:700; color:#101728;
              line-height:1.35; }
  .cad-ch-s { font-size:12px; color:#7a8496; line-height:1.45; margin-top:3px; }
  .cad-ch-x { font-size:12px !important; color:#5a6a80 !important;
              line-height:1.5 !important; text-align:left !important;
              margin:7px 0 0 !important; width:100%; }
  /* LE RÉSULTAT DE LA NORMALISATION, DANS SA PASTILLE. Il est produit par
     l'étape deux et lu par l'étape trois : posé à cheval, il montre que le
     score de l'indicateur n'est pas une donnée de plus mais la sortie de
     l'opération qui le précède. */
  .cad-ch-r { font-size:12px; color:#3c4761; background:#f2f5f3;
              border-radius:8px; padding:8px 12px; margin-top:12px; }
  .cad-ch-r b { color:#101728; font-weight:700;
              font-variant-numeric:tabular-nums; }
  /* SUR ÉCRAN ÉTROIT LA CHAÎNE SE PLIE EN DEUX RANGÉES, et les chevrons
     disparaissent : une flèche qui pointe vers le bord n'indique plus rien. */
  @media (max-width: 1150px) {
    .cad-ch { flex-wrap:wrap; row-gap:22px; }
    .cad-ch-e { flex:1 1 30%; }
    .cad-ch-fl { display:none; }
  }

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
  /* LES PALIERS SONT UN TABLEAU, PAS UNE LISTE DE FLÈCHES. Onze lignes
     « borne → score » se lisaient une par une ; en deux colonnes titrées, on
     balaie la colonne de gauche jusqu'à la valeur qu'on cherche et on lit le
     score en face. C'est ce que le lecteur vient faire. */
  /* LA SPÉCIFICITÉ COMPTE ICI AUSSI : `.cad-duo > div` porte un
     `max-width:100%` qui l'emporterait sur une classe simple, et le tableau
     s'étirerait jusqu'au bord en emportant la note sous lui. */
  .cad-duo > .cad-seu { display:grid; grid-template-columns:1fr auto;
              gap:0 26px; align-items:center; font-size:11.5px;
              color:#3c4761; flex:0 0 auto; width:270px; max-width:270px; }
  .cad-seu > span, .cad-seu > b { padding:4px 0;
              border-bottom:1px solid #f0f3f1; }
  .cad-seu b { color:#101728; font-weight:600; text-align:right;
              font-variant-numeric:tabular-nums; }
  .cad-seu-h { font-size:11px !important; font-weight:700; color:#5a6a80;
              letter-spacing:.02em; border-bottom:1px solid #dfe5e1 !important;
              padding-bottom:6px !important; }
  /* La spécificité compte : `.cad-duo > div` porte déjà un `max-width`, et
     un sélecteur de classe simple ne l'emporte pas sur un sélecteur d'enfant.
     La note est donc visée à travers son parent. */
  .cad-duo > .cad-seu-n { font-size:11px; color:#5a6a80; line-height:1.55;
              max-width:24ch; text-align:left !important; font-style:italic;
              padding-left:4px; }
  /* LA PHRASE QUI DIT CE QUE LES FORMULES FONT, dans son aplat, sous elles. */
  .cad-nrm-p { font-size:11.5px; color:#5a6a80; line-height:1.5;
              background:#f7f8f8; border-radius:10px; padding:11px 14px;
              margin-top:18px; }
  /* CHACUNE DES DEUX LOGIQUES : son nom en vert, sa condition d'emploi en
     dessous. Un filet très pâle les sépare, comme partout ailleurs. */
  .cad-log { padding:12px 0; border-bottom:1px solid #eef2f0; }
  .cad-log:first-of-type { padding-top:4px; }
  .cad-log-t { font-size:12.5px; font-weight:700; color:#1a6b52;
              margin:0 0 5px; }
  /* PAS DE LARGEUR MAXIMALE ICI. Soixante signes coupaient le paragraphe au
     milieu de sa colonne et laissaient la moitié droite vide : la colonne
     fait déjà la mesure, elle n'a pas besoin d'une seconde. */
  p.cad-log-x { font-size:12px !important; color:#3c4761 !important;
              line-height:1.55 !important; margin:0 !important;
              text-align:left !important; }

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
  /* LA CONCLUSION EST DANS UN BANDEAU TEINTÉ, ET C'EST SA FONCTION QUI LE
     VEUT : elle ne fait pas partie de la liste des quatre sources, elle dit
     ce qu'on en fait. Un filet l'aurait rattachée à la quatrième colonne ;
     le fond pâle la détache de toutes les quatre. */
  .cad-fin  { display:flex; align-items:flex-start; gap:15px;
              background:#f4f9f6; border:1px solid #dfeae3;
              border-radius:12px; margin-top:26px; padding:14px 18px; }
  .cad-fin-t { font-size:14px; font-weight:700; color:#1a6b52;
              margin:2px 0 3px; line-height:1.4; }
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
  /* EMPILÉS, ILS N'ONT PLUS DE FILET VERTICAL ENTRE EUX : c'est le filet
     vert au-dessus de chaque titre qui les sépare, et il est le même pour
     les trois. Sans cette remise à zéro, le deuxième et le troisième
     gardaient le bord gauche et le décalage prévus pour trois colonnes. */
  .cad-aaa.vertical .cad-a { padding:0 0 2px !important; }
  .cad-aaa.vertical .cad-a + .cad-a { border-left:0 !important;
        padding-left:0 !important; }
    /* --- LE MODÈLE DE RÉSILIENCE, EN DEUX MOITIÉS ----------------------- */
  /* LES DEUX NOMBRES DE LA PHRASE D'OUVERTURE, en vert : ils annoncent la
     colonne de gauche et celle de droite, à la place des deux sous-titres
     qui les redisaient. */
  .cad-attr-f { color:#1a6b52; font-weight:700; }

  /* LES TROIS CARTES : un numéro, un filet, un titre, une phrase. */
  /* NI CADRE NI FILET AUTOUR DU TEXTE. Trois cartes encadrées, un tableau
     encadré et une ligne de séparation entre chaque dimension faisaient
     quatre-vingts pixels de traits pour trois phrases et sept nombres. Le
     texte se tient tout seul : ce qui sépare les blocs est le blanc entre
     eux, et le numéro d'ordre suffit à ouvrir chaque attribut. */
  /* UN FILET ENTRE DEUX ATTRIBUTS, ET UN SOUS LE DERNIER. Trois blocs posés
     dans le blanc, à hauteur des sept lignes du tableau voisin, flottaient
     sans qu'on sache où l'un finit et où l'autre commence ; le filet très
     pâle qui sépare les lignes du tableau fait le même travail ici, et les
     deux moitiés se lisent enfin au même rythme. */
  /* LA COLONNE DES ATTRIBUTS DESCEND À HAUTEUR DE LA PREMIÈRE DIMENSION.
     Le tableau de droite ouvre par une ligne d'en-têtes ; sans décalage, le
     premier attribut se posait en face de cette ligne-là plutôt qu'en face
     de la première dimension, et les deux moitiés démarraient à deux
     hauteurs différentes pour aucune raison lisible. */
  .cad-cc { display:flex; flex-direction:column; gap:0; margin-top:40px; }
  .cad-c  { display:flex; align-items:stretch; gap:16px;
        border:0; border-radius:0; background:transparent;
        border-bottom:1px solid #eef2f0; padding:15px 0; }
  .cad-c:first-child { padding-top:6px; }
  .cad-c-n { font-size:22px; font-weight:700; color:#b9c6bf;
        font-variant-numeric:tabular-nums; line-height:1.1;
        padding-right:16px; border-right:0;
        display:flex; align-items:center; }
  .cad-c-b { flex:1 1 auto; }
  .cad-c-t { font-size:13px; font-weight:700; letter-spacing:.07em;
        text-transform:uppercase; color:#1a6b52; margin-bottom:5px; }
  p.cad-c-x { font-size:12.5px !important; color:#3c4761 !important;
        line-height:1.5 !important; margin:0 !important;
        text-align:left !important; }

  /* LE TABLEAU DES SEPT DIMENSIONS. */
  .cad-dt { border:0; border-radius:0; }
  /* LES DEUX COLONNES DE DROITE SONT ÉTROITES POUR LEUR INTITULÉ, PAS POUR
     LEUR CONTENU. « Poids dans l'indice » et « Indicateurs » passaient à la
     ligne dans quatre-vingt-deux pixels, et l'en-tête faisait trois lignes
     au-dessus de nombres à trois caractères. */
  .cad-dh, .cad-dl { display:grid;
        grid-template-columns:minmax(140px,1fr) 130px 108px;
        gap:16px; align-items:center; padding:11px 0; }
  .cad-dh { background:transparent; font-size:10px; font-weight:700;
        letter-spacing:.1em; text-transform:uppercase; color:#8a93a5;
        line-height:1.3; }
  /* LE FILET REVIENT ENTRE LES LIGNES, TRÈS PÂLE. Il avait été retiré avec
     les bordures du tableau, et sept lignes de trois colonnes sans repère
     horizontal obligeaient l'œil à traverser cent pixels de blanc pour
     rattacher un pourcentage à sa dimension. Ce filet-là n'encadre rien : il
     tient la ligne. */
  .cad-dl { border-top:0; border-bottom:1px solid #eef2f0; }
  .cad-dh { border-bottom:1px solid #dfe5e1; }
  .cad-dl:last-child { border-bottom:1px solid #eef2f0; }
  .cad-dl-n { font-size:13px; color:#101728; font-weight:600;
        line-height:1.35; }
  .cad-dl-r { color:#1a6b52; font-weight:700; }
  .cad-dl-v { font-size:12.5px; font-weight:600; color:#101728;
        text-align:right; font-variant-numeric:tabular-nums; }

  @media (max-width:1100px) {
    .cad-dh, .cad-dl { grid-template-columns:1fr 104px 88px; }
  }
  /* L'INTITULÉ QUI OUVRE LA CHAÎNE : il dit de quoi les cinq cases parlent,
     de l'indicateur ouvert ou de l'exemple. */
  .cad-ex-t { font-size:12px; font-weight:700; letter-spacing:.09em;
        text-transform:uppercase; color:#1a6b52; margin:14px 0 10px; }
  /* DE L'AIR SOUS LA PHRASE D'OUVERTURE. Dix-huit pixels la collaient aux
     deux colonnes : elle se lisait comme la première ligne du tableau plutôt
     que comme la phrase qui l'annonce. */
  p.cad-attr-x { font-size:15px !important; color:#3c4761 !important;
            line-height:1.55 !important; margin:2px 0 34px !important;
            max-width:96ch; }
  /* SANS PICTOGRAMME, C'EST LE TITRE QUI OUVRE LA COLONNE, et un filet vert
     sous lui remplace le disque : il tient le même rôle — dire où commence
     la colonne — sans rien dessiner de plus. */
  .cad-a    { border-top:2px solid #1a6b52; padding-top:14px; }
  .cad-a-i  { width:50px; height:50px; border-radius:50%; background:#eef3ef;
              display:flex; align-items:center; justify-content:center;
              flex:0 0 auto; }
  /* Le trait s'arrête sur un point : une ligne qui se termine dans le vide
     se lit comme une ligne coupée. */
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

  /* La phrase qui ouvre le premier onglet. Le `!important` est nécessaire :
     la feuille de l'application fixe 14,5 px et la justification à tout
     paragraphe du contenu, avec une spécificité supérieure à celle d'une
     classe. */
  p.cad-uma { font-size:17px !important; line-height:1.5 !important;
              font-family:Georgia,"Times New Roman",serif; font-style:italic;
              font-weight:400; color:#26364a !important;
              margin:2px 0 8px !important; max-width:none !important;
              border-left:3px solid #1a6b52; padding-left:20px;
              text-align:left !important; white-space:normal; }
  /* ELLE PASSE À LA LIGNE, ET C'EST LA MOITIÉ DE LARGEUR QUI L'IMPOSE.
     Tenue de force sur une ligne, elle se terminait par des points de
     suspension dans une colonne de six cents pixels — une phrase tronquée
     est pire que deux lignes. */
  @media (max-width: 1150px) {
    p.cad-uma { font-size:15.5px !important; }
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

    LA COLONNE « INDICATEURS » DONNE LE TOTAL DU RÉFÉRENTIEL, PAS L'AVANCEMENT.
    Elle affichait « 10/16 » sous une barre de progression : deux chiffres
    dont le premier dit l'état d'un chantier, pas la composition du cadre.
    Cet onglet décrit ce qu'APRI mesure — combien d'indicateurs porte chaque
    dimension — et l'avancement du calcul est une autre question, qui se lit
    indicateur par indicateur dans l'analyse des résultats.
    """
    # LA BARRE A SAUTÉ, LE POURCENTAGE RESTE. Une barre longue de trois cents
    # pixels pour dire ce qu'un nombre dit en quatre caractères : elle
    # occupait la moitié de la largeur du tableau, et c'est cette largeur-là
    # qui empêchait de poser le tableau à côté d'autre chose.
    lignes = []
    for cle in ORDRE:
        e = stats["dims"].get(cle)
        if not e:
            continue
        nom = _e(T(cle))
        num, _, reste = nom.partition(". ")
        lignes.append(
            '<div class="cad-dl">'
            f'<div class="cad-dl-n"><span class="cad-dl-r">{num}.</span> '
            f'{reste}</div>'
            f'<div class="cad-dl-v">{_fmt(e["part"])}&thinsp;%</div>'
            f'<div class="cad-dl-v">{e["n"]}</div></div>')
    # L'EN-TÊTE EST UNE BANDE, PAS UNE LIGNE DE PLUS. Un aplat très pâle sous
    # les trois intitulés sépare la légende des données mieux qu'un filet, et
    # c'est le format de la maquette.
    entete = (
        '<div class="cad-dh">'
        f'<div>{_e(T("cad_col_dim"))}</div>'
        f'<div class="cad-dl-v">{_e(T("cad_col_poids"))}</div>'
        f'<div class="cad-dl-v">{_e(T("cad_col_ind"))}</div></div>')
    return '<div class="cad-dt">' + entete + "".join(lignes) + '</div>'


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


def _seuils(brut, unite=""):
    """Le tableau des paliers : la valeur brute a gauche, le score a droite."""
    tete = T("cad_ex_c_val") + (f" ({unite})" if unite else "")
    lignes = [f'<span class="cad-seu-h">{_e(tete)}</span>'
              f'<b class="cad-seu-h">{_e(T("cad_ex_c_sc"))}</b>']
    for p_ in brut.split("|"):
        if "→" not in p_:
            continue
        borne, _, val = p_.partition("→")
        lignes.append(f'<span>{_e(borne.strip())}</span>'
                      f'<b>{_e(val.strip())}</b>')
    return '<div class="cad-seu">' + "".join(lignes) + '</div>'


def _titre_p(rang, cle, exemple=False):
    """L'intitulé numéroté d'une des trois sections du calcul."""
    return (f'<div class="cad-p-t"><b>{rang}.</b>{_e(T(cle))}'
            + (f'<span class="cad-ex">{_e(T("cad_ex"))}</span>'
               if exemple else "") + '</div>')


def _attributs():
    """Les trois attributs, en trois cartes numérotées.

    NI ORDRE NI PICTOGRAMME. Le numéro sert de repère, pas d'étape : un
    territoire anticipe, absorbe et s'adapte en même temps, et le même
    indicateur peut servir deux de ces attributs. Quant au pictogramme, une
    loupe, un bouclier et une flèche circulaire ne disent rien que les trois
    verbes ne disent déjà, en toutes lettres, à côté d'eux.
    """
    cartes = []
    for i, k in enumerate(("cad_a1", "cad_a2", "cad_a3"), start=1):
        cartes.append(
            '<div class="cad-c">'
            f'<div class="cad-c-n">{i:02d}</div>'
            '<div class="cad-c-b">'
            f'<div class="cad-c-t">{_e(T(k + "_t"))}</div>'
            f'<p class="cad-c-x">{_e(T(k))}</p></div></div>')
    return '<div class="cad-cc">' + "".join(cartes) + '</div>'


def _sources(extras=None):
    """Les quatre sources, en deux colonnes de texte.

    QUATRE COLONNES, SÉPARÉES PAR UN FILET, ET RIEN D'ENCADRÉ. Les quatre
    dispositifs tournent en parallèle : les mettre l'un sous l'autre en
    ferait des étapes, les encadrer en ferait quatre objets qu'on croit
    cliquables. Un simple filet vertical entre les colonnes dit « ceci n'est
    pas cela » sans rien promettre de plus, et les quatre se comparent d'un
    balayage horizontal — ce qu'on veut faire d'une liste de sources.

    LE PICTOGRAMME, LE NUMÉRO ET LE TITRE TIENNENT SUR UNE LIGNE. Le numéro
    est gros et maigre : il donne le rang sans peser autant que le mot qu'il
    précède, et le filet vertical qui le suit sépare le compte du nom.

    CHAQUE SOURCE PORTE SA LISTE, et c'est elle qui la rend contestable :
    « données géospatiales » ne veut rien dire tant qu'on n'a pas lu
    Sentinel, Landsat, NDVI. Une source qu'on ne peut pas vérifier est une
    source qu'on doit croire.

    `extras` GLISSE UN BLOC SOUS LA DESCRIPTION. L'enquête ménage est la
    seule des quatre dont on connaisse l'effectif, le nombre de sections et
    le minimum par section.
    """
    extras = extras or {}
    # PAS DE PICTOGRAMME. Une maison, un globe, une pousse et une fiche pour
    # « enquête ménage », « imagerie satellitaire », « relevés de terrain » et
    # « entretiens institutionnels » : le numéro et le titre disent déjà de
    # quelle source il s'agit, et le disque qui portait l'icône poussait le
    # titre de trente pixels vers la droite dans une colonne qui en compte
    # quatre.
    blocs = []
    for i, k in enumerate(("cad_so1", "cad_so2", "cad_so3", "cad_so4"),
                          start=1):
        puces = [x.strip() for x in T(k + "_p").split("|") if x.strip()]
        if (k + "_note") in i18n.DICO:
            puces.append(T(k + "_note"))
        blocs.append(
            '<div class="cad-so-b">'
            '<div class="cad-so-h">'
            f'<span class="cad-so-n">{i:02d}</span>'
            f'<span class="cad-so-t">{_e(T(k + "_t"))}</span></div>'
            f'<p class="cad-so-x">{_e(T(k + "_x"))}</p>'
            + extras.get(k, "")
            + '<ul class="cad-so-l">'
            + "".join(f'<li>{_e(p)}</li>' for p in puces)
            + '</ul></div>')
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
    # LA SECONDE PHRASE EST DESCENDUE D'UN ONGLET. « Ces indicateurs sont
    # normalisés puis agrégés pour produire les scores » annonce, sous la
    # liste des sources, une opération que la page ne montre pas encore ;
    # écrite sous la liste des indicateurs, elle dit ce qu'il advient de ce
    # qu'on vient de lire.
    return ('<div class="cad-fin">'
            '<div>'
            f'<div class="cad-fin-t">{_e(T("cad_band_t"))}</div>'
            '</div></div>')


# LE MINIMUM PAR SECTION EST CELUI DU PLAN DE SONDAGE. Le compteur affichait
# le plus petit effectif effectivement atteint, soit cent seize à Quentin ;
# les neuf autres sections sont à cent vingt ou au-delà. Cent seize décrit un
# incident de collecte dans une section, pas la règle sur laquelle l'enquête a
# été construite, et c'est la règle que le lecteur cherche à cet endroit.
MIN_SECTION = 120


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
# LES ATTRIBUTS ET LES DIMENSIONS TIENNENT DANS UN SEUL ONGLET. Trois
# colonnes de six lignes d'un côté, sept lignes de tableau de l'autre : ni
# l'un ni l'autre ne remplissait un écran, et l'on cliquait pour passer de ce
# qu'APRI mesure à ce en quoi il le découpe — deux moitiés de la même
# définition. Depuis que le tableau a perdu sa barre, les deux tiennent côte
# à côte, séparés par un filet.
# L'ONGLET DES MESURES BRUTES A ÉTÉ REPLIÉ DANS CELUI DES INDICATEURS. Il
# déroulait la chaîne de calcul sur un exemple — quarante-cinq minutes de
# marche pour aller chercher l'eau — pendant que l'onglet voisin montrait les
# barèmes réels sans dire ce qu'ils produisent. Les deux se lisent maintenant
# au même endroit, et la chaîne tourne sur l'indicateur qu'on a ouvert.
VUES = ("mesure", "sources", "indicateurs", "boucles",
        "environnement", "document")
# `_LIB` porte les intitulés longs ; ils ne sont plus rendus depuis que la
# barre a pris les titres courts, mais la table reste la carte des sept vues.
_LIB = {"mesure": "cad_o1", "sources": "cad_o2",
        "indicateurs": "cad_c35", "boucles": "cad_o5",
        "environnement": "cad_o6", "document": "cad_o7"}
_COURT = {"mesure": "cad_c1", "sources": "cad_c2",
          "indicateurs": "cad_c35", "boucles": "cad_c5",
          "environnement": "cad_c6", "document": "cad_c7"}
# LA LIGNE DE DESCRIPTION DE CHAQUE ONGLET, dans le format à deux lignes que
# portent désormais toutes les barres du site.
_DESC = {"mesure": "cad_d1", "sources": "cad_d2",
         "indicateurs": "cad_d35", "boucles": "cad_d5",
         "environnement": "cad_d6", "document": "cad_d7"}


def render(doc_complet=None):
    stats = _stats()
    st.markdown(STYLE.replace("__BANDES__", _bandes_css()),
                unsafe_allow_html=True)

    # PAS DE TITRE DE PAGE. La colonne de menu marque déjà la rubrique
    # courante d'un filet vert et d'un mot en gras ; le répéter en gros
    # au-dessus des onglets le disait une deuxième fois, et la description
    # sous l'onglet actif une troisième. La page commence donc par ce qu'elle
    # apporte.

    if not stats:
        st.info(T("e_absent"))
        return

    # LA BARRE EST CELLE DE TOUT LE SITE. Elle était recopiée ici avec sa
    # propre feuille de style ; à force de retouches faites d'un côté et pas
    # de l'autre, elle n'avait plus tout à fait la même graisse que celle des
    # résultats, et l'on changeait de site en changeant de page.
    # PAS DE DESCRIPTION SOUS CES SEPT-LÀ. Elle sert quand un titre est
    # ambigu — « Par paysage » n'annonce pas ce qu'on y trouve. Ici les sept
    # titres nomment déjà leur contenu, et la ligne en dessous ne faisait que
    # le reformuler : « Dimensions » suivi de « Les sept dimensions et leurs
    # pondérations ». Le composant accepte de n'en pas avoir.
    vue = onglets.barre("cad_vue", list(VUES),
                        titre=lambda c: T(_COURT[c]),
                        description=lambda c: T(_DESC[c]),
                        defaut=VUES[0])

    if vue == "sources":
        _v_sources()
    elif vue == "indicateurs":
        _v_indicateurs()
    elif vue == "boucles":
        _v_boucles()
    elif vue == "environnement":
        _v_environnement()
    elif vue == "document":
        _v_document(doc_complet)
    else:
        _v_mesure(stats)


def _titre(cle, note=None, marge=4):
    """Un intitulé de bloc, et sa note s'il en a une.

    `cle` peut valoir None : le bloc n'a alors que sa note. C'est le cas en
    tête d'onglet — voir ci-dessous.

    UN ONGLET NE REDIT PAS SON PROPRE NOM. Chaque onglet s'ouvrait sur un
    intitulé qui paraphrasait le titre qu'on venait de lire dans la barre —
    « Sources et données » puis « Les quatre sources des mesures », deux
    lignes à trente pixels d'écart pour un seul renseignement. Depuis que la
    barre porte une description sous chaque titre, la paraphrase est même
    dite trois fois. Les intitulés d'ouverture ont donc sauté ; ceux qui
    coiffent une section À L'INTÉRIEUR d'un onglet restent, eux : ils
    séparent deux choses, ce que ne faisait pas le premier.
    """
    h = (f'<div class="cad-h" style="margin-top:{marge}px">'
         f'{_e(T(cle))}</div>') if cle else ""
    return h + (f'<p class="cad-note">{_e(T(note))}</p>' if note else "")


# --- 1 · ce que mesure APRI, et en quoi il le découpe -----------------------
def _v_mesure(stats):
    """La définition en deux moitiés : les attributs, et les dimensions.

    LE FORMAT SUIT LA MAQUETTE FOURNIE. Deux colonnes, chacune ouverte par un
    intitulé vert souligné d'un filet et une ligne qui dit ce qu'on va lire ;
    à gauche trois cartes numérotées, à droite le tableau des sept
    dimensions ; en dessous, une note qui articule les deux — les attributs
    disent COMMENT la résilience fonctionne, les dimensions DE QUOI elle est
    faite. C'est la seule chose que ni la colonne de gauche ni celle de
    droite ne pouvaient dire seules.

    SANS PICTOGRAMME, ET C'EST LA CONSIGNE QUI TIENT. La maquette en porte un
    par carte et un par dimension ; ils ont été retirés de cet écran deux
    fois, parce qu'un œil, un bouclier et une pousse ne disent rien de plus
    que « anticiper », « absorber » et « s'adapter » écrits juste à côté. Le
    numéro et le filet tiennent la carte.
    """
    # LA DÉFINITION EST PARTIE OUVRIR LES BOUCLES. « Un paysage compris comme
    # un système complexe adaptatif » ne dit rien des attributs ni des
    # dimensions : elle annonce un système qui se répond à lui-même, ce qui
    # est le sujet de l'onglet des boucles. Elle y est maintenant, en tête.
    # LES DEUX SOUS-TITRES SONT PARTIS. « Attributs de résilience » au-dessus
    # de trois cartes qui portent chacune son attribut, « Dimensions de
    # résilience » au-dessus d'un tableau dont la première colonne s'appelle
    # « Dimension » : la phrase d'ouverture annonce déjà les trois et les
    # sept, et les deux colonnes se reconnaissent d'elles-mêmes. Ce sont les
    # deux nombres de cette phrase qui portent maintenant le repérage, en
    # vert : l'œil saute de « trois attributs » à la colonne de gauche et de
    # « sept dimensions » à celle de droite.
    _phrase = _e(T("cad_attr_x"))
    for _f in (T("cad_attr_f1"), T("cad_attr_f2")):
        _phrase = _phrase.replace(_e(_f),
                                  f'<b class="cad-attr-f">{_e(_f)}</b>', 1)
    st.markdown(f'<p class="cad-attr-x">{_phrase}</p>',
                unsafe_allow_html=True)
    g, d = st.columns([1, 1.3], gap="large")
    with g:
        st.markdown(_attributs(), unsafe_allow_html=True)
    with d:
        st.markdown(_tableau_dimensions(stats), unsafe_allow_html=True)
    # RIEN SOUS LES DEUX COLONNES. Le bandeau du bas redisait en une phrase ce
    # que les deux moitiés viennent de montrer : les attributs disent comment,
    # les dimensions disent quoi. Cette phrase-là se lit dans le dessin.


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
    mini = MIN_SECTION
    if mini:
        compteurs.append((_fmt(mini, 0), T("cad_s4_t"), T("cad_s4")))

    st.markdown(
        # LA PHRASE D'INTRODUCTION A SAUTÉ. Elle annonçait que la résilience
        # se mesure par plusieurs sources complémentaires ; les quatre
        # colonnes qui suivent le montrent, chacune nommée et détaillée. Une
        # annonce de ce qui vient juste après ne fait que retarder.
        _sources({"cad_so1": _compteurs(compteurs)})
        + _fin(), unsafe_allow_html=True)


# --- 4 · de la mesure brute au score ---------------------------------------
def _score_dimension(dim):
    """Le score publié d'une dimension : moyenne pondérée de ses indicateurs.

    C'EST LA RÈGLE DU RÉFÉRENTIEL, PAS UNE MOYENNE DE PLUS. Les indicateurs
    notés d'une dimension sont moyennés en pesant chacun de sa pondération —
    exactement ce que fait la page des scores publiés. Les indicateurs sans
    score n'entrent pas au dénominateur : les compter pour zéro reviendrait à
    pénaliser une dimension pour une mesure qui n'a pas été faite.
    """
    num = den = 0.0
    for x in _referentiel():
        if x["dim"] != dim or x["score"] is None:
            continue
        num += x["poids"] * x["score"]
        den += x["poids"]
    return round(num / den, 2) if den else None


def _case(rang, titre, valeur, phrase, sous=None, operation=False,
          resultat=None):
    """Une des cinq cases : un en-tete numerote, un chiffre, une phrase.

    `operation` compose la valeur en corps reduit : c'est le cas de la
    deuxieme case, qui nomme une operation la ou les autres portent un
    nombre. `resultat` ajoute la pastille de sortie sous la case.
    """
    corps = "cad-ch-o" if operation else "cad-ch-v"
    if valeur == "—":
        corps += " cad-ch-vide"
    out = ['<div class="cad-ch-e">'
           '<div class="cad-ch-h">'
           f'<span class="cad-ch-n">{rang}</span>'
           f'<span class="cad-ch-t">{_e(titre)}</span></div>'
           f'<div class="{corps}">{_e(valeur)}</div>']
    if sous:
        out.append(f'<div class="cad-ch-s">{_e(sous)}</div>')
    out.append(f'<p class="cad-ch-x">{_e(phrase)}</p>')
    if resultat:
        out.append(f'<div class="cad-ch-r">{_e(T("cad_ex_res"))} '
                   f'<b>{_e(resultat)}</b></div>')
    out.append('</div>')
    return "".join(out)


def _chaine(cases):
    """Les cinq cases mises bout à bout, un chevron entre deux."""
    out = []
    for i, c in enumerate(cases):
        if i:
            out.append('<div class="cad-ch-fl">'
                       + icones.svg("chevron", couleur="#8fb39c", taille=22)
                       + '</div>')
        out.append(c)
    return f'<div class="cad-ch">{"".join(out)}</div>'


def _chaine_generique():
    """Les cinq étapes, sans chiffres, tant qu'aucun indicateur n'est ouvert.

    UN CHIFFRE AFFICHÉ EST UN RÉSULTAT, MÊME QUAND C'EST UN EXEMPLE. « 45
    min », « 3,5 / 10 » et « 6,1 / 10 » sur un écran où rien n'a été choisi
    se lisaient comme la mesure de quelque chose : la mention « sur un
    exemple », en petites capitales au-dessus, ne suffisait pas à les
    désamorcer — on lit les grands nombres avant les titres. Les cases
    gardent donc leur intitulé et leur phrase, qui enseignent la méthode, et
    montrent un tiret à la place de la valeur, qui ne dirait rien de vrai.
    """
    RIEN = "—"
    return _chaine([
        _case(1, T("cad_e1_t"), RIEN, T("cad_e1_x")),
        _case(2, T("cad_e2_t"), T("cad_e2_v"), T("cad_e2_x"),
              operation=True),
        _case(3, T("cad_e3_t"), RIEN, T("cad_e3_x")),
        _case(4, T("cad_e4_t"), RIEN, T("cad_e4_x")),
        _case(5, T("cad_e5_t"), RIEN, T("cad_e5_x"))])


def _chaine_indicateur(x):
    """La même chaîne, déroulée sur l'indicateur que le lecteur regarde.

    LA CHAÎNE NE S'EXPLIQUE QUE SUR UN CAS. Cinq cases avec « 45 min » et
    « 3,5 / 10 » disent la mécanique sur une donnée qui n'est pas dans le
    fichier ; le lecteur venu vérifier UN indicateur devait faire lui-même la
    transposition. Les mêmes cinq cases, remplies de la mesure de cet
    indicateur, de son score, de sa pondération et du score de sa dimension,
    la lui donnent faite.

    CE QUI MANQUE EST DIT, JAMAIS INVENTÉ. Un indicateur mesuré dont le score
    n'est pas encore au fichier affiche « non calculé » : écrire un score
    plausible à cet endroit serait publier un chiffre qui n'a pas tourné.
    """
    par = _bandes(x["echelle"])
    pct = "%" in "".join(par.values()) if par else "%" in x["echelle"]
    val = ("—" if x["valeur"] is None
           else _fmt(x["valeur"], 1) + (" %" if pct else ""))
    norme_s = T("cad_ex_seuils") if par else T("cad_ex_stat")
    if x["score"] is None:
        sc_v, sc_x = T("cad_ex_sc_non"), T("cad_ex_sc_non_x")
    else:
        sc_v, sc_x = _fmt(x["score"], 1) + " / 10", T("cad_e3_x")
    dsc = _score_dimension(x["dim"])
    _n_ech = _menages()[0]
    _sous1 = (T("cad_ex_ech", n=_fmt(_n_ech, 0)) if _n_ech
              else T("cad_e1_x"))
    return _chaine([
        _case(1, T("cad_e1_t"), val, x["metrique"], sous=_sous1),
        _case(2, T("cad_e2_t"), T("cad_e2_v"), T("cad_e2_x"),
              sous=norme_s, operation=True,
              resultat=None if x["score"] is None else sc_v),
        _case(3, T("cad_e3_t"), sc_v, sc_x),
        _case(4, T("cad_e4_t"), T("cad_ex_p_v", p=_fmt(x["poids"], 1)),
              T("cad_ex_p_x")),
        _case(5, T("cad_e5_t"),
              "—" if dsc is None else _fmt(dsc, 2) + " / 10",
              T("cad_ex_dim_x"), sous=T(x["dim"]))])


def _normalisations(x=None):
    """Les deux façons de normaliser, sous la chaîne.

    LES PALIERS SONT CEUX DE L'INDICATEUR QUAND IL Y EN A UN. La colonne de
    droite montrait les cinq seuils de l'exemple ; quand un indicateur est
    ouvert, ce sont ses onze paliers à lui qui s'y écrivent, et la
    normalisation par seuils cesse d'être une notion pour devenir la sienne.
    """
    par = _bandes(x["echelle"]) if x else {}
    unite = ""
    if par:
        unite = "%" if "%" in "".join(par.values()) else ""
        # LES PARENTHÈSES DE SAISIE NE SE PUBLIENT PAS. Le référentiel écrit
        # ses bornes « (≤5%) » ; dans une colonne où chaque ligne est déjà un
        # palier, la parenthèse ne sépare plus rien.
        brut = "|".join(f"{par[i].strip('()[] ')}→{i}"
                        for i in sorted(par) if par[i])
        titre_b, sous_b = T("cad_p2b_t"), T("cad_ex_seuils_i")
    else:
        # RIEN À DROITE TANT QU'AUCUN INDICATEUR N'EST OUVERT. Les paliers de
        # l'exemple — « ≥ 120 min → 0 » — s'affichaient là, et se lisaient
        # comme l'échelle de quelque chose : c'est le même défaut que les
        # chiffres de la chaîne, réglé de la même façon.
        brut, titre_b, sous_b = "", T("cad_p2b_t"), T("cad_p2b_vide")
    return ('<div class="cad-nrm"><div>'
            + f'<div class="cad-nrm-t">{_e(T("cad_p2s_t"))}</div>'
            + f'<div class="cad-nrm-x">{_e(T("cad_p2s_x"))}</div>'
            # LES DEUX LOGIQUES, L'UNE SOUS L'AUTRE, CHACUNE AVEC SA
            # CONDITION D'EMPLOI. Elles ne sont pas deux variantes de goût :
            # c'est la disponibilité d'une distribution de référence qui
            # décide, et la phrase de chacune commence donc par « quand ».
            + f'<div class="cad-log"><div class="cad-log-t">'
            f'{_e(T("cad_p2q_t"))}</div>'
            f'<p class="cad-log-x">{_e(T("cad_p2q_x"))}</p></div>'
            + f'<div class="cad-log"><div class="cad-log-t">'
            f'{_e(T("cad_p2n_t"))}</div>'
            f'<p class="cad-log-x">{_e(T("cad_p2n_x"))}</p></div>'
            + f'<div class="cad-nrm-p">{_e(T("cad_p2_sens"))}</div>'
            + '</div><div>'
            + f'<div class="cad-nrm-t">{_e(titre_b)}</div>'
            + f'<div class="cad-nrm-x">{_e(sous_b)}</div>'
            + ('<div class="cad-duo">' + _seuils(brut, unite)
               + f'<div class="cad-seu-n">{_e(T("cad_p2b_n"))}</div>'
               + '</div>' if brut else '')
            + '</div></div>')


# --- les indicateurs, leur échelle et leur pondération ----------------------
def _v_indicateurs():
    """La liste du référentiel : un indicateur, son barème, son poids.

    CET ONGLET EXISTE PARCE QUE LES DEUX PRÉCÉDENTS S'ARRÊTENT AVANT LUI. Le
    tableau des dimensions dit combien d'indicateurs chacune porte ; la chaîne
    de calcul dit comment une mesure devient un score, sur un exemple. Ni l'un
    ni l'autre ne dit QUELS indicateurs, ni avec QUEL barème chacun a été
    converti. Ce sont les deux choses qu'on vient vérifier quand on conteste
    un score, et elles n'étaient nulle part.

    L'ÉCHELLE EST REPRODUITE MOT POUR MOT. Onze paliers par indicateur, écrits
    dans le référentiel : les remettre en forme, c'est risquer de publier un
    barème qui n'est pas celui qui a tourné. Le seul retrait est le préfixe de
    saisie.

    UN INDICATEUR À LA FOIS, ET LA DIMENSION NE SERT QU'À LE TROUVER. Cent
    vingt-huit lignes s'ouvraient d'elles-mêmes, chacune avec sa règle
    graduée : quatre écrans de défilement avant d'atteindre les contrôles
    qui, seuls, permettaient d'y entrer, et le lecteur venu vérifier UN
    indicateur devait d'abord traverser les cent vingt-sept autres. La
    dimension restreint la liste déroulante ; c'est l'indicateur choisi qui
    se déplie, et lui seul.

    ET LA CHAÎNE DE CALCUL LE SUIT. Savoir qu'un indicateur porte tel barème
    et telle pondération ne dit pas encore ce qu'il devient : les cinq étapes
    qui mènent de sa mesure à un score de dimension se déroulent juste en
    dessous, sur ses chiffres à lui. Tant qu'aucun indicateur n'est ouvert,
    les mêmes cinq étapes se lisent sur un exemple, de sorte que l'onglet
    enseigne la méthode même à qui ne cherche rien de précis.
    """
    tous = _referentiel()
    if not tous:
        st.info(T("e_absent"))
        return
    g, d = st.columns([1, 2])
    with g:
        dim = st.selectbox(T("cad_ind_dim"), [None] + ORDRE, key="cad_i_dim",
                           format_func=lambda c: (T("cad_ind_all") if c is None
                                                  else T(c)))
    # LA LISTE SUIT LA DIMENSION, ET LA SÉLECTION NE SURVIT PAS À UN
    # CHANGEMENT DE DIMENSION. Streamlit garde la valeur d'un selectbox même
    # quand elle a quitté ses options ; sans ce nettoyage, choisir une
    # dimension après un indicateur laissait à l'écran un indicateur qui n'en
    # fait pas partie.
    choix = [x for x in tous if dim is None or x["dim"] == dim]
    cles = [x["ligne"] for x in choix]
    if st.session_state.get("cad_i_ind") not in cles:
        st.session_state["cad_i_ind"] = None
    par_cle = {x["ligne"]: x for x in choix}
    with d:
        cle = st.selectbox(T("cad_ind_ind"), cles, key="cad_i_ind",
                           index=None, placeholder=T("cad_ind_tous"),
                           format_func=lambda k: par_cle[k]["nom"])

    if cle is None:
        st.markdown(f'<p class="cad-attr-x" style="margin:10px 0 18px">'
                    f'{_e(T("cad_ind_vide"))}</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="cad-ex-t">{_e(T("cad_ex_gen"))}</div>'
                    + _chaine_generique() + _normalisations(),
                    unsafe_allow_html=True)
        return

    vus = [par_cle[cle]]

    # LA BARRE A SAUTÉ, ET L'ÉCHELLE EST ÉCRITE. Une barre de quatre-vingts
    # pixels disait la même chose que le nombre à côté d'elle, en moins
    # précis ; ce qui manquait vraiment, c'était de savoir sur quoi ce nombre
    # se lit — il court de 1 à 5, et l'en-tête de colonne le dit maintenant.
    lignes = ['<table class="cad-it"><thead><tr>'
              f'<th>{_e(T("cad_ind_c_nom"))}</th>'
              f'<th>{_e(T("cad_ind_c_ech"))}</th>'
              f'<th class="n">{_e(T("cad_ind_c_p"))}'
              f'<span class="cad-it-ech">{_e(T("cad_ind_c_p_ech"))}</span>'
              '</th></tr></thead><tbody>']
    # LE SENS DE LECTURE NE SE RÉPÈTE PLUS. « Plus c'est haut, mieux c'est »
    # sous cent vingt-huit lignes sur cent vingt-huit : la mention était vraie
    # partout sauf pour une poignée d'indicateurs, et une mention portée par
    # toutes les lignes n'en distingue aucune. L'échelle, ligne par ligne, dit
    # déjà dans quel sens elle monte.
    for x in vus:
        num, _, court = T(x["dim"]).partition(". ")
        ech = _echelle_html(x["echelle"])
        lignes.append(
            '<tr><td>'
            f'<div class="cad-it-n">{_e(x["nom"])}</div>'
            f'<div class="cad-it-d"><span class="cad-it-r">{_e(num)}</span> '
            f'{_e(court)}</div></td>'
            f'<td class="cad-it-e">{ech}</td>'
            '<td class="n"><div class="cad-it-p">'
            f'{_fmt(x["poids"])}</div></td></tr>')
    lignes.append('</tbody></table>')
    st.markdown("".join(lignes), unsafe_allow_html=True)

    # CE QU'IL ADVIENT DE CET INDICATEUR, SOUS SA LIGNE. La phrase fermait
    # l'onglet des sources, où elle annonçait une opération sur des
    # indicateurs qui n'avaient pas encore été montrés. Ici, elle ouvre les
    # cinq étapes qui l'exécutent, sur les chiffres de l'indicateur ouvert.
    st.markdown(f'<p class="cad-attr-x" style="margin:16px 0 4px">'
                f'{_e(T("cad_band_x"))}</p>'
                f'<div class="cad-ex-t">{_e(T("cad_ex_titre"))}</div>'
                + _chaine_indicateur(vus[0])
                + _normalisations(vus[0]), unsafe_allow_html=True)


# --- 5 · les boucles de rétroaction ----------------------------------------
def _boucle_svg(sens):
    """Un cercle, deux variables, une flèche : la boucle réduite à sa forme.

    DEUX DESSINS PLUTÔT QU'UNE DÉFINITION. « Renforçante » et « équilibrante »
    sont des mots qu'on croit comprendre et qu'on confond dès la première
    boucle réelle. Deux cercles côte à côte, l'un vert marqué « + » et l'autre
    orange marqué « − », montrent la différence sans qu'on ait à retenir
    laquelle est laquelle : c'est le signe posé sur l'arc qui la porte.
    """
    coul = "#1a6b52" if sens == "R" else "#d1730c"
    signe = "+" if sens == "R" else "−"
    L, H, cx, cy, r = 230, 190, 115, 100, 62
    # Les deux sommets sont aux extrémités horizontales du cercle.
    ax, bx = cx - r, cx + r
    return (
        f'<svg viewBox="0 0 {L} {H}" width="100%" '
        f'style="max-width:{L}px;display:block;margin:0 auto" role="img" '
        f'font-family="Inter,system-ui,sans-serif">'
        f'<defs><marker id="fb{sens}" viewBox="0 0 10 10" refX="8" refY="5" '
        f'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">'
        f'<path d="M0,1 L9,5 L0,9 z" fill="{coul}"/></marker></defs>'
        # l'arc du haut porte la flèche et le signe ; celui du bas ferme
        f'<path d="M{ax},{cy} A{r},{r} 0 0 1 {bx},{cy}" fill="none" '
        f'stroke="{coul}" stroke-width="1.8" marker-end="url(#fb{sens})"/>'
        f'<path d="M{bx},{cy} A{r},{r} 0 0 1 {ax},{cy}" fill="none" '
        f'stroke="{coul}" stroke-width="1.8" marker-end="url(#fb{sens})"/>'
        f'<text x="{cx}" y="{cy - r - 10}" text-anchor="middle" '
        f'font-size="20" font-weight="700" fill="{coul}">{signe}</text>'
        f'<text x="{cx}" y="{cy + 11}" text-anchor="middle" font-size="30" '
        f'font-weight="800" fill="{coul}">{sens}</text>'
        + "".join(
            f'<circle cx="{x}" cy="{cy}" r="16" fill="#fff" stroke="{coul}" '
            f'stroke-width="1.6"/>'
            f'<text x="{x}" y="{cy + 5}" text-anchor="middle" font-size="13" '
            f'font-weight="600" fill="{coul}">{lab}</text>'
            for x, lab in ((ax, "A"), (bx, "B")))
        + '</svg>')


def _v_boucles():
    """Le parcours en quatre temps, puis la lecture d'une boucle.

    LE PARCOURS EST LE MÊME QUE CELUI DE LA SECTION « FEEDBACK LOOPS », et
    c'est voulu : cet onglet-ci l'explique, l'autre l'exécute. Symptôme,
    boucle, levier, action — quatre étapes numérotées, chacune avec son
    exemple en italique, parce qu'une méthode décrite sans un cas ne se
    retient pas.

    LA LECTURE D'UNE BOUCLE EST EN DESSOUS, ET SÉPARÉE PAR UN FILET. Elle ne
    fait pas partie du parcours : c'est la convention de notation, celle qu'il
    faut connaître avant de regarder le premier schéma. Le piège du « + » lu
    comme « bon » est dit à part, dans son propre cartouche.
    """
    # PAS DE TITRE : l'onglet ouvert dit déjà « Boucles de rétroaction », et
    # « Diagrammes de boucles causales » juste en dessous nommait la même
    # chose une seconde fois. La ligne qui suit, elle, apprend quelque chose.
    # LA DÉFINITION A QUITTÉ LE HAUT DE LA PAGE POUR LA TROISIÈME CASE. Elle
    # annonce un paysage « compris comme un système complexe adaptatif » ;
    # posée avant le parcours en quatre temps, elle était une seconde annonce
    # là où le lecteur cherchait la première chose à regarder. La grille du
    # bas comptait trois colonnes pour deux contenus, et sa case de droite
    # restait vide : la définition s'y lit après les signes et les deux
    # boucles, comme la conclusion de ce qu'ils viennent de montrer.

    # UN SEUL VERT POUR LES QUATRE. Rouge, ambre, bleu, vert : quatre teintes
    # pour quatre étapes du MÊME parcours laissaient croire à quatre natures
    # différentes — un danger, un avertissement, une information, une réussite
    # — là où il n'y a qu'un ordre de lecture. Le numéro le donne déjà. La
    # couleur, elle, redevient ce qu'elle est ailleurs sur le site : celle du
    # site, et rien de plus.
    # LE FILET AU-DESSUS DE CHAQUE TEMPS EST PARTI. Quatre traits verts en
    # tête de colonne dessinaient quatre en-têtes de tableau au-dessus d'un
    # parcours qui n'en est pas un : le numéro et le chevron disent déjà
    # l'ordre, et le titre vert dit déjà où commence chaque temps.
    ETAPES = ("cad_b1", "cad_b2", "cad_b3", "cad_b4")
    VERT = "#1a6b52"
    cases = []
    for i, k in enumerate(ETAPES, start=1):
        coul = VERT
        if i > 1:
            cases.append('<div class="cad-bp-fl">'
                         + icones.svg("chevron", couleur="#c8cfd8", taille=22)
                         + '</div>')
        cases.append(
            '<div class="cad-bp-e">'
            f'<div class="cad-bp-t" style="color:{coul}">'
            f'{i}. {_e(T(k + "_t")).upper()}</div>'
            f'<div class="cad-bp-x">{_e(T(k + "_x"))}</div>'
            f'<div class="cad-bp-ex">{_e(T(k + "_e"))}</div></div>')
    st.markdown(f'<div class="cad-bp">{"".join(cases)}</div>',
                unsafe_allow_html=True)

    # ---- comment lire une boucle -----------------------------------------
    signes = "".join(
        f'<div class="cad-bs">'
        f'<div class="cad-bs-p" style="background:{fond};color:{coul}">'
        f'{s}</div><div>'
        f'<div class="cad-bs-t" style="color:{coul}">{s}&nbsp; '
        f'{_e(T(k + "_t"))}</div>'
        f'<div class="cad-bs-x">{_e(T(k + "_x"))}</div>'
        f'<div class="cad-bs-f">A &uarr; &rarr; B {fl}</div></div></div>'
        for k, s, fl, coul, fond in
        (("cad_bl_p", "+", "&uarr;", "#1a6b52", "#eef3f0"),
         ("cad_bl_m", "&minus;", "&darr;", "#d1730c", "#fdf1e3")))

    st.markdown(
        '<div class="cad-bl">'
        f'<div class="cad-bl-h">{_e(T("cad_bl_t")).upper()}</div>'
        '<div class="cad-bl-g">'
        f'<div>{signes}</div>'
        '<div class="cad-bl-d">'
        f'<div>{_boucle_svg("R")}'
        f'<div class="cad-bl-n" style="color:#1a6b52">'
        f'{_e(T("cad_bl_r"))}</div>'
        f'<div class="cad-bl-s">{_e(T("cad_bl_r_x"))}</div></div>'
        f'<div>{_boucle_svg("B")}'
        f'<div class="cad-bl-n" style="color:#d1730c">'
        f'{_e(T("cad_bl_b"))}</div>'
        f'<div class="cad-bl-s">{_e(T("cad_bl_b_x"))}</div></div></div>'
        # L'AVERTISSEMENT EST PARTI, LA DÉFINITION PREND SA PLACE. « + ne veut
        # pas dire bon » posé sous deux pastilles qui portent chacune sa
        # phrase redisait en négatif ce que les deux disaient déjà en clair.
        f'<div class="cad-bl-u">{_e(T("cad_uma"))}</div>'
        '</div></div>', unsafe_allow_html=True)

    # ---- la méthode, et ses références -----------------------------------
    refs = []
    for bloc in T("cad_bm_r").split("@@"):
        parts = (bloc.split("|") + ["", "", ""])[:3]
        titre, apport, lien = (p.strip() for p in parts)
        if not titre:
            continue
        # LE LIEN EST POSÉ SUR LE TITRE QUAND IL Y EN A UN. Un ouvrage
        # imprimé n'a pas d'URL, et une URL inventée pour faire nombre est
        # pire que pas d'URL du tout.
        nom = (f'<a href="{_e(lien)}" target="_blank" rel="noopener">'
               f'{_e(titre)}</a>') if lien else _e(titre)
        refs.append(f'<div class="cad-bm-e"><b>{nom}</b>{_e(apport)}</div>')
    st.markdown(
        '<div class="cad-bm">'
        f'<div class="cad-bm-h">{_e(T("cad_bm_t")).upper()}</div>'
        f'<p class="cad-bm-x">{_e(T("cad_bm_x"))}</p>'
        f'<div class="cad-bm-l">{"".join(refs)}</div></div>',
        unsafe_allow_html=True)


# --- 6 · le cas de l'environnement -----------------------------------------
def _v_environnement():
    """La dimension qui ne se mesure pas en interrogeant des ménages.

    Transects, images satellitaires et barèmes propres : fondue dans la page
    générale elle y tiendrait six lignes ; à part, elle garde son protocole
    entier — et les trajectoires, qui disent le même territoire dans le
    temps, la suivent.
    """
    # LA MÉTHODE, ET PAS LES RÉSULTATS. Cet onglet appartient au cadre : il
    # dit comment on mesure l'environnement — transects, capteurs, barèmes.
    # Les trajectoires qui le suivaient donnaient les séries mesurées, donc
    # des résultats, dans la section qui explique la méthode ; elles se lisent
    # dans l'analyse des résultats, avec tout le reste de ce qui a été trouvé.
    environnement_cadre.render()


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
    # LE VOLET « OU LE LIRE À L'ÉCRAN » A SAUTÉ. Le document se télécharge, et
    # c'est ce que la carte au-dessus propose ; en proposer en plus une
    # transcription repliée mettait deux fois le même contenu sur la page,
    # dont une derrière un clic qui n'annonce rien.
