"""Fiches d'intervention — ce qu'on fait des leviers que les boucles désignent.

CETTE PAGE N'EST PAS ÉCRITE À CÔTÉ DE L'ANALYSE, ELLE EN DESCEND.

Elle suit le protocole d'intervention, dans son ordre :

  a) REPÉRAGE DES LEVIERS, sur trois critères — les nœuds qui agissent sur
     plusieurs causes, ceux qui appartiennent à une dimension faible, ceux dont
     le potentiel de mobilisation communautaire est fort. Les deux premiers
     sont CALCULÉS (degré et boucles pour l'un, scores pondérés par dimension
     pour l'autre) ; le troisième est POSÉ, mais sur des indicateurs mesurés du
     tissu associatif, affichés en clair pour qu'on puisse en discuter.

  b) CATÉGORISATION — structurel, technique, organisationnel, comportemental.

  c) ÉVALUATION de chaque levier : impact attendu sur le score, faisabilité,
     acteurs clés, horizon temporel. Livrable : le tableau
     « Problème → Score → Boucle → Levier ».

  d) FICHES D'ACTION : objectif spécifique, activités techniques ET sociales,
     indicateurs de performance avec objectif de score chiffré, acteurs et
     calendrier, risques et mesures d'atténuation.

D'OÙ VIENNENT LES CHIFFRES

L'impact affiché n'est pas un ordre de grandeur posé à la main. Chaque fiche
pousse son levier de sa cible propre, la variation traverse le graphe, et
l'effet sur l'indice vaut exactement :

    Σ ( pondération de l'indicateur × variation de son score ) ÷ poids total

Chaque fiche porte le détail de ce calcul — les indicateurs déplacés, leur
pondération, la part qui vient du levier lui-même et la part qui vient de la
cascade. Un chiffre de trois décimales sans son calcul n'est pas un résultat,
c'est une décoration ; le calcul est donc déplié sous chaque fiche.

POURQUOI LES CHIFFRES SONT PETITS

Parce que le dénominateur est le référentiel entier — 66 indicateurs scorés,
155,4 points de pondération. Une action qui déplace fortement quatre
indicateurs déplace faiblement l'indice d'ensemble, et c'est arithmétiquement
normal. Chaque fiche affiche donc aussi l'effet rapporté au seul périmètre
couvert par le graphe causal, qui est la lecture honnête de son ampleur.

CE QUE LE CLASSEMENT NE DIT PAS

L'ordre des fiches suit l'effet simulé, pas la priorité politique. Un effet
modélisé fort sur un levier infaisable vaut moins qu'un effet modeste sur un
levier qu'on sait mettre en œuvre : la faisabilité est donc affichée à côté, et
c'est à l'atelier de trancher. Le modèle propose, il ne décide pas.
"""

import json
import os

import streamlit as st

import boucles_moteur as M
import i18n
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"
HAUSSE, ALERTE, BAISSE = "#1a8a4f", "#d1730c", "#c33a24"
NIVEAU_COULEUR = {1: "#2166ac", 2: "#1a8a4f", 3: "#0f8fa8", 4: "#7048b6"}
CAT_COULEUR = {"structurel": "#7048b6", "technique": "#2166ac",
               "organisationnel": "#0f8fa8", "comportemental": "#1a8a4f"}

# UNE DIMENSION EST DITE FAIBLE QUAND ELLE PASSE SOUS LA MOYENNE PONDÉRÉE DU
# TERRITOIRE LUI-MÊME (4,54 sur 10), et non sous un seuil rond choisi à la
# main. Un seuil à 5 aurait fait tomber la dimension institutionnelle (4,83)
# du côté faible et dilué le critère ; un seuil à 4 l'aurait épargnée, mais
# uniquement parce qu'il aurait été ajusté pour cela. La référence est donc
# calculée sur les données : deux dimensions passent dessous, l'humaine (1,40)
# et la physique (2,93).

# ---------------------------------------------------------------------------
# LES FICHES, selon le protocole d'intervention.
#
# `levier` est l'identifiant d'un nœud du graphe causal : c'est lui qui fait le
# lien avec l'analyse des boucles, et tout ce qui se calcule — impact, boucles,
# indicateurs de performance — en est déduit.
#
# Seuls des leviers ACTIONNABLES portent une fiche. L'aridité et l'état de la
# végétation arrivent haut dans le classement des effets, mais on ne monte pas
# un projet « sur l'aridité » : ce sont des états résultants. Les fiches
# agissent sur ce qui se décide — un équipement, une pratique, une règle, un
# flux d'information.
#
# `cible` est l'objectif de score visé sur le levier, en points. Il suit la
# faisabilité plutôt qu'une valeur uniforme : viser +2,5 sur un levier dont on
# sait qu'il est difficile à bouger produirait un impact simulé flatteur et
# faux. C'est cette cible qui est propagée dans le graphe, et c'est elle qui
# devient l'indicateur de performance de la fiche.
#
# `ligne_probleme` est la ligne du référentiel qui ÉNONCE le problème que la
# fiche traite. Pour un levier mesuré c'est sa propre ligne ; pour un levier
# latent — les pratiques agricoles, le contrôle forestier — c'est la ligne
# mesurée immédiatement en aval. C'est la colonne « Score » du tableau
# Problème → Score → Boucle → Levier.
#
# `mobilisation` est le seul champ posé à dire d'expert. Le critère de
# mobilisation communautaire ne se calcule pas sur le graphe : la distance aux
# nœuds communautaires vaut 3 pour presque tous les leviers et ne discrimine
# rien. Il est donc jugé sur le canal de mise en œuvre de la fiche, et le bloc
# de repérage affiche l'état mesuré du tissu associatif à côté, pour que le
# jugement soit contestable.
# ---------------------------------------------------------------------------
FICHES = [
    {"id": "cuisson", "levier": "cuisson", "cat": "technique", "meadows": 2,
     "faisabilite": "moyenne", "horizon": "moyen", "cible": 2.0,
     "ligne_probleme": 6, "mobilisation": "haute"},
    {"id": "agro", "levier": "agro_durable", "cat": "comportemental",
     "meadows": 2, "faisabilite": "moyenne", "horizon": "long", "cible": 2.0,
     "ligne_probleme": 108, "mobilisation": "haute"},
    {"id": "eau", "levier": "eau", "cat": "technique", "meadows": 1,
     "faisabilite": "haute", "horizon": "court", "cible": 2.5,
     "ligne_probleme": 4, "mobilisation": "haute"},
    {"id": "finance", "levier": "compte", "cat": "structurel", "meadows": 2,
     "faisabilite": "moyenne", "horizon": "moyen", "cible": 2.0,
     "ligne_probleme": 72, "mobilisation": "moyenne"},
    {"id": "alerte", "levier": "comites", "cat": "organisationnel",
     "meadows": 3, "faisabilite": "haute", "horizon": "court", "cible": 2.5,
     "ligne_probleme": 28, "mobilisation": "haute"},
    {"id": "foncier", "levier": "foncier", "cat": "structurel", "meadows": 4,
     "faisabilite": "faible", "horizon": "long", "cible": 1.5,
     "ligne_probleme": 74, "mobilisation": "moyenne"},
    {"id": "controle", "levier": "controle", "cat": "structurel", "meadows": 4,
     "faisabilite": "faible", "horizon": "long", "cible": 1.5,
     "ligne_probleme": 54, "mobilisation": "moyenne"},
    # LE LEVIER A CHANGÉ, ET C'EST LE CALCUL QUI L'A IMPOSÉ. La fiche visait
    # l'enregistrement des naissances ; cette ligne est à 10/10. Le blocage
    # n'est pas là : il est un cran plus loin, sur la carte d'identité, à
    # 4/10 — et c'est elle qui conditionne le compte et les services. Pousser
    # une ligne déjà au maximum ne produit rien, la simulation le montrait
    # (+0,026 contre +0,064). La fiche a donc été recentrée sur la carte.
    {"id": "identite", "levier": "identite", "cat": "organisationnel",
     "meadows": 1, "faisabilite": "haute", "horizon": "court", "cible": 2.5,
     "ligne_probleme": 103, "mobilisation": "moyenne"},
]

# Les indicateurs qui disent l'état du tissu associatif du territoire. Ils
# servent à qualifier le potentiel de mobilisation communautaire — un critère
# du protocole — sur des chiffres plutôt que sur une impression. Ce qu'ils
# disent est net : le tissu associatif des MÉNAGES est très faible, mais les
# organisations qui existent sont bien structurées et déjà partenaires.
LIGNES_MOBILISATION = [27, 95, 96, 201, 206, 208]

DIM_DE = {
    "I. PHYSICAL AND INFRASTRUCTURAL DIMENSION": "dim1",
    "II. INSTITUTIONAL, TECHNOLOGICAL, AND GOVERNANCE  DIMENSION": "dim2",
    "III.  ENVIRONMENTAL AND ECOLOGICAL DIMENSION": "dim3",
    "IV. ECONOMIC, LIVELIHOODS, AND FOOD SECURITY DIMENSION": "dim4",
    "V. SOCIAL AND COMMUNITY DIMENSION": "dim5",
    "VI. HUMAN DIMENSION": "dim6",
    "VII. CULTURAL, IDENTITY-BASED, AND PSYCHOLOGICAL DIMENSION": "dim7",
}

TEXTES = {
    "int_titre": {"en": "Intervention Profiles", "fr": "Fiches d'intervention"},
    "int_sous_titre": {
        "en": "Action sheets built from the levers the loops identify",
        "fr": "Des fiches d'action construites sur les leviers que les boucles "
              "désignent"},
    "int_intro": {
        "en": "Each sheet acts on one lever of the causal graph. Expected "
              "impact, monitoring indicators and ranking are computed by the "
              "loop model, change a relation and the sheets reorder "
              "themselves. **The ranking follows the simulated effect, not "
              "political priority:** a strong modelled effect on an "
              "unfeasible lever is worth less than a modest one you can "
              "actually deliver. Feasibility is shown alongside; the workshop "
              "decides.",
        "fr": "Chaque fiche agit sur un levier du graphe causal. L'impact "
              "attendu, les indicateurs de suivi et le classement sont "
              "calculés par le modèle des boucles, changez une relation, les "
              "fiches se réordonnent. **Le classement suit l'effet simulé, "
              "pas la priorité politique :** un effet modélisé fort sur un "
              "levier infaisable vaut moins qu'un effet modeste sur un levier "
              "qu'on sait mettre en œuvre. La faisabilité est affichée à "
              "côté ; c'est l'atelier qui tranche."},

    # ---------------- le protocole
    "int_proto": {"en": "How these sheets were produced",
                  "fr": "Comment ces fiches ont été produites"},
    "int_proto_a": {"en": "Lever identification", "fr": "Repérage des leviers"},
    "int_proto_a_x": {
        "en": "Three criteria: nodes acting on several causes, nodes in a weak "
              "dimension, nodes with community-mobilisation potential.",
        "fr": "Trois critères : les nœuds qui agissent sur plusieurs causes, "
              "ceux associés à une dimension faible, ceux à fort potentiel de "
              "mobilisation communautaire."},
    "int_proto_b": {"en": "Categorisation", "fr": "Catégorisation"},
    "int_proto_b_x": {
        "en": "Structural, technical, organisational, behavioural.",
        "fr": "Structurels, techniques, organisationnels, comportementaux."},
    "int_proto_c": {"en": "Evaluation", "fr": "Évaluation"},
    "int_proto_c_x": {
        "en": "Expected impact on the score, feasibility, key actors, time "
              "horizon.",
        "fr": "Impact attendu sur le score, faisabilité, acteurs clés, horizon "
              "temporel."},
    "int_proto_d": {"en": "Action sheets", "fr": "Fiches d'action"},
    "int_proto_d_x": {
        "en": "Objective, technical and social activities, performance "
              "indicators, actors and calendar, risks and mitigation.",
        "fr": "Objectif, activités techniques et sociales, indicateurs de "
              "performance, acteurs et calendrier, risques et atténuation."},

    # ---------------- repérage
    "int_rep": {"en": "a) Lever identification, the three criteria",
                "fr": "a) Repérage des leviers, les trois critères"},
    "int_rep1": {"en": "Acting on several causes",
                 "fr": "Agir sur plusieurs causes"},
    "int_rep1_x": {
        "en": "Computed on the graph: how many relations leave the node, and "
              "how many loops it belongs to. A node in loops of **both signs** "
              "is a tipping lever, the only kind that can turn a degrading "
              "dynamic into a regulating one.",
        "fr": "Calculé sur le graphe : combien de relations partent du nœud, "
              "et à combien de boucles il appartient. Un nœud présent dans des "
              "boucles **des deux sens** est un levier de basculement, le "
              "seul type capable de retourner une dynamique dégradante en "
              "dynamique régulatrice."},
    "int_rep2": {"en": "Belonging to a weak dimension",
                 "fr": "Appartenir à une dimension faible"},
    "int_rep2_x": {
        "en": "Computed on the survey: weighted score of each dimension, "
              "against the weighted mean of the framework itself. Two fall "
              "below it, the human dimension and the physical one, and they "
              "carry most of the sheets.",
        "fr": "Calculé sur l'enquête : score pondéré de chaque dimension, "
              "comparé à la moyenne pondérée du référentiel lui-même. Deux "
              "passent dessous, la dimension humaine et la dimension "
              "physique, et ce sont elles qui portent l'essentiel des "
              "fiches."},
    "int_rep2_ref": {
        "en": "A dimension is called weak when it falls below the weighted "
              "mean of the framework itself, {v}/10, not below a round "
              "threshold chosen by hand. A threshold at 5 would have pulled "
              "the institutional dimension (4.83) into the weak group and "
              "diluted the criterion; a threshold at 4 would have spared it, "
              "but only because it had been adjusted to.",
        "fr": "Une dimension est dite faible quand elle passe sous la moyenne "
              "pondérée du référentiel lui-même, {v}/10, et non sous un seuil "
              "rond choisi à la main. Un seuil à 5 aurait fait basculer la "
              "dimension institutionnelle (4,83) du côté faible et dilué le "
              "critère ; un seuil à 4 l'aurait épargnée, mais uniquement parce "
              "qu'il aurait été ajusté pour cela."},
    "int_rep3": {"en": "Community-mobilisation potential",
                 "fr": "Potentiel de mobilisation communautaire"},
    "int_rep3_x": {
        "en": "**This one is not computed on the graph, and it should be "
              "said.** Distance to the community nodes is 3 for almost every "
              "lever and discriminates nothing. It is therefore judged on the "
              "delivery channel of each sheet, and the measured state of the "
              "associative fabric is shown here so the judgement can be "
              "argued with.",
        "fr": "**Celui-ci n'est pas calculé sur le graphe, et il faut le "
              "dire.** La distance aux nœuds communautaires vaut 3 pour "
              "presque tous les leviers et ne discrimine rien. Il est donc "
              "jugé sur le canal de mise en œuvre de chaque fiche, et l'état "
              "mesuré du tissu associatif est affiché ici pour qu'on puisse "
              "contester ce jugement."},
    "int_rep3_lect": {
        "en": "The reading is sharp: the associative fabric of **households** "
              "is very weak (membership 2/10, bonding and bridging social "
              "capital 1/10), while the organisations that do exist are "
              "**well structured and already partnered** (7/10 and 9/10). "
              "Mobilisation therefore does not mean creating a fabric, it "
              "means routing the sheets through the organisations already "
              "standing.",
        "fr": "La lecture est nette : le tissu associatif des **ménages** est "
              "très faible (appartenance 2/10, capital d'entraide et de "
              "passerelle 1/10), alors que les organisations qui existent sont "
              "**bien structurées et déjà partenaires** (7/10 et 9/10). "
              "Mobiliser ne veut donc pas dire créer un tissu, cela veut dire "
              "faire passer les fiches par les organisations déjà debout."},
    "int_dim_faible": {"en": "weak", "fr": "faible"},

    # ---------------- catégorisation
    "int_cat_t": {"en": "b) Categorisation of the levers",
                  "fr": "b) Catégorisation des leviers"},
    "int_cat": {"en": "Category", "fr": "Catégorie"},
    "int_cat_structurel": {"en": "Structural", "fr": "Structurel"},
    "int_cat_technique": {"en": "Technical", "fr": "Technique"},
    "int_cat_organisationnel": {"en": "Organisational", "fr": "Organisationnel"},
    "int_cat_comportemental": {"en": "Behavioural", "fr": "Comportemental"},
    "int_cat_structurel_x": {"en": "governance, rules",
                             "fr": "gouvernance, règles"},
    "int_cat_technique_x": {"en": "infrastructure, practices",
                            "fr": "infrastructures, pratiques"},
    "int_cat_organisationnel_x": {"en": "committees, networks",
                                  "fr": "comités, réseaux"},
    "int_cat_comportemental_x": {"en": "values, behaviours, cohesion",
                                 "fr": "valeurs, comportements, cohésion"},

    # ---------------- tableau livrable
    "int_tab": {"en": "c) Problem → Score → Loop → Lever",
                "fr": "c) Tableau « Problème → Score → Boucle → Levier »"},
    "int_tab_note": {
        "en": "The deliverable of the evaluation step. Each row reads: the "
              "problem as the framework states it, its measured score, the "
              "loop it sits in, and the lever the sheet acts on. A blank loop "
              "is not an omission, that lever sits in no cycle, its effect is "
              "a chain, direct and bounded.",
        "fr": "Le livrable de l'étape d'évaluation. Chaque ligne se lit : le "
              "problème tel que le référentiel l'énonce, son score mesuré, la "
              "boucle dans laquelle il se trouve, et le levier sur lequel la "
              "fiche agit. Une boucle vide n'est pas un oubli, ce levier "
              "n'appartient à aucun cycle, son effet est une chaîne, direct et "
              "borné."},
    "int_c_probleme": {"en": "Problem", "fr": "Problème"},
    "int_c_score": {"en": "Score", "fr": "Score"},
    "int_c_boucle": {"en": "Loop", "fr": "Boucle"},
    "int_c_levier": {"en": "Lever", "fr": "Levier"},
    "int_c_impact": {"en": "Impact", "fr": "Impact"},
    "int_hors_boucle": {"en": "chain, no loop", "fr": "chaîne, hors boucle"},

    "int_tension": {
        "en": "**The strongest immediate effect is not the strongest lever.** "
              "Water, the identity card and early warning move the index most "
              "in the simulation, but sit in few loops or none: their effect "
              "is direct and bounded. Conservation farming and forest "
              "enforcement move it ten times less, yet they are the two "
              "**tipping levers**, the only sheets that sit in loops of both "
              "signs, and so the only ones that can turn a degrading dynamic "
              "into a regulating one. A programme needs both: the first to "
              "show results within a season, the second to change what the "
              "system does to itself.",
        "fr": "**L'effet immédiat le plus fort n'est pas le levier le plus "
              "fort.** L'eau, la carte d'identité et l'alerte déplacent le "
              "plus l'indice dans la simulation, mais appartiennent à peu de "
              "boucles ou à aucune : leur effet est direct et borné. Les "
              "pratiques agricoles conservatrices et le contrôle forestier le "
              "déplacent dix fois moins, et ce sont pourtant les deux "
              "**leviers de basculement**, les seules fiches présentes dans "
              "des boucles des deux sens, donc les seules capables de "
              "retourner une dynamique dégradante en dynamique régulatrice. Un "
              "programme a besoin des deux : les premières pour montrer des "
              "résultats dans la saison, les secondes pour changer ce que le "
              "système se fait à lui-même."},
    "int_recap": {"en": "d) The eight sheets at a glance",
                  "fr": "d) Les huit fiches d'un coup d'œil"},
    "int_c_fiche": {"en": "Sheet", "fr": "Fiche"},
    "int_c_effet": {"en": "Effect", "fr": "Effet"},
    "int_c_niveau": {"en": "Level", "fr": "Niveau"},
    "int_c_portee": {"en": "Structural reach", "fr": "Portée structurelle"},
    "int_effet": {"en": "Simulated effect on the overall score",
                  "fr": "Effet simulé sur l'indice d'ensemble"},
    "int_effet_note": {
        "en": "Each sheet propagates its own score target through the whole "
              "graph. An exploratory scenario of the model, not a forecast.",
        "fr": "Chaque fiche propage sa propre cible de score dans tout le "
              "graphe. Un scénario exploratoire du modèle, pas une prévision."},

    # ---------------- la justification du chiffre
    "int_dou": {"en": "Where this figure comes from",
                "fr": "D'où vient ce chiffre"},
    "int_dou_f": {
        "en": "Effect on the index = Σ ( indicator weight × change in its "
              "score ) ÷ total weight of the framework.",
        "fr": "Effet sur l'indice = Σ ( pondération de l'indicateur × "
              "variation de son score ) ÷ poids total du référentiel."},
    "int_dou_pose": {"en": "Target applied to the lever",
                     "fr": "Cible appliquée au levier"},
    "int_dou_som": {"en": "Weighted points gained", "fr": "Points pondérés gagnés"},
    "int_dou_poids": {"en": "Total weight of the framework",
                      "fr": "Poids total du référentiel"},
    "int_dou_res": {"en": "Effect on the index", "fr": "Effet sur l'indice"},
    "int_dou_direct": {"en": "from the lever itself",
                       "fr": "vient du levier lui-même"},
    "int_dou_casc": {"en": "from the cascade through the graph",
                     "fr": "vient de la cascade dans le graphe"},
    "int_dou_peri": {
        "en": "Read on the covered perimeter alone",
        "fr": "Lu sur le seul périmètre couvert"},
    "int_dou_peri_x": {
        "en": "The graph covers {p} % of the framework's weight; the rest "
              "cannot move, for want of a posed relation. Related to that "
              "perimeter alone, the effect is {v}, which is the honest "
              "measure of its size.",
        "fr": "Le graphe couvre {p} % du poids du référentiel ; le reste ne "
              "peut pas bouger, faute de relation posée. Rapporté à ce seul "
              "périmètre, l'effet vaut {v} : c'est la mesure honnête de son "
              "ampleur."},
    "int_dou_det": {"en": "Indicator by indicator",
                    "fr": "Indicateur par indicateur"},
    "int_dou_c_ind": {"en": "Framework line", "fr": "Ligne du référentiel"},
    "int_dou_c_p": {"en": "Weight", "fr": "Pond."},
    "int_dou_c_av": {"en": "Before", "fr": "Avant"},
    "int_dou_c_ap": {"en": "After", "fr": "Après"},
    "int_dou_c_ct": {"en": "Contribution", "fr": "Contribution"},
    "int_dou_plaf": {
        "en": "Scores are capped at 10: an indicator already at the top "
              "contributes nothing, however hard the lever is pushed.",
        "fr": "Les scores sont plafonnés à 10 : un indicateur déjà au maximum "
              "ne contribue rien, quelle que soit la force appliquée au "
              "levier."},

    "int_depart": {"en": "Lever, current score", "fr": "Levier, score actuel"},
    "int_boucles": {"en": "Loops crossed", "fr": "Boucles traversées"},
    "int_bascule": {
        "en": "Tipping lever, sits in loops of both signs",
        "fr": "Levier de basculement, présent dans des boucles des deux sens"},
    "int_objectif": {"en": "Specific objective", "fr": "Objectif spécifique"},
    "int_probleme": {"en": "Problem addressed", "fr": "Problème traité"},
    "int_act_tech": {"en": "Technical activities", "fr": "Activités techniques"},
    "int_act_soc": {"en": "Social activities", "fr": "Activités sociales"},
    "int_perf": {"en": "Performance indicators",
                 "fr": "Indicateurs de performance"},
    "int_perf_cible": {"en": "Score target on the lever",
                       "fr": "Objectif de score sur le levier"},
    "int_perf_note": {
        "en": "The target is set by feasibility, not uniformly: aiming +2.5 on "
              "a lever known to be hard to move would produce a flattering, "
              "false simulated impact. It is this target that is propagated "
              "through the graph.",
        "fr": "La cible suit la faisabilité plutôt qu'une valeur uniforme : "
              "viser +2,5 sur un levier dont on sait qu'il est difficile à "
              "bouger produirait un impact simulé flatteur et faux. C'est "
              "cette cible qui est propagée dans le graphe."},
    "int_acteurs": {"en": "Key actors", "fr": "Acteurs clés"},
    "int_calendrier": {"en": "Calendar", "fr": "Calendrier"},
    "int_horizon": {"en": "Horizon", "fr": "Horizon"},
    "int_h_court": {"en": "short term", "fr": "court terme"},
    "int_h_moyen": {"en": "medium term", "fr": "moyen terme"},
    "int_h_long": {"en": "long term", "fr": "long terme"},
    "int_risques": {"en": "Risks and mitigation",
                    "fr": "Risques et mesures d'atténuation"},
    "int_risque": {"en": "Risk", "fr": "Risque"},
    "int_attenuation": {"en": "Mitigation", "fr": "Atténuation"},
    "int_mob": {"en": "Mobilisation", "fr": "Mobilisation"},
    "int_mob_haute": {"en": "high", "fr": "haute"},
    "int_mob_moyenne": {"en": "medium", "fr": "moyenne"},
    "int_mob_faible": {"en": "low", "fr": "faible"},
    "int_suivi": {"en": "Monitoring indicators",
                  "fr": "Indicateurs de suivi"},
    "int_suivi_note": {
        "en": "The framework lines the simulation moves most. They are already "
              "measured, so the monitoring is tooled the day the action "
              "starts.",
        "fr": "Les lignes du référentiel que la simulation déplace le plus. "
              "Elles sont déjà mesurées : le suivi est outillé le jour où "
              "l'action démarre."},
    "int_boucle_visee": {"en": "The loop this seeks to turn",
                         "fr": "La boucle qu'il s'agit de retourner"},
    "int_faisabilite": {"en": "Feasibility", "fr": "Faisabilité"},
    "int_f_haute": {"en": "high", "fr": "haute"},
    "int_f_moyenne": {"en": "medium", "fr": "moyenne"},
    "int_f_faible": {"en": "low", "fr": "faible"},
    "int_niveau": {"en": "Level of intervention", "fr": "Niveau d'intervention"},
    "int_n1": {"en": "Adjust a flow", "fr": "Ajuster un flux"},
    "int_n2": {"en": "Break or strengthen a loop",
               "fr": "Casser ou renforcer une boucle"},
    "int_n3": {"en": "Change the information flows",
               "fr": "Modifier les flux d'information"},
    "int_n4": {"en": "Change the rules", "fr": "Changer les règles"},
    "int_n_note": {
        "en": "After Meadows: the higher the level, the more structural the "
              "effect, and the harder to obtain.",
        "fr": "D'après Meadows : plus le niveau est élevé, plus l'effet est "
              "structurel, et plus il est difficile à obtenir."},
    # ---------------- fiche : cuisson
    "int_cuisson_t": {"en": "Break the poverty–charcoal link",
                      "fr": "Casser le lien pauvreté–charbon"},
    "int_cuisson_p": {
        "en": "Clean cooking scores 1/10 in the framework, almost every "
              "household cooks on wood or charcoal, and that is the entry "
              "point of the pressure on wood.",
        "fr": "La cuisson propre est notée 1/10 par le référentiel, presque "
              "tous les ménages cuisinent au bois ou au charbon, et c'est la "
              "porte d'entrée de la pression sur le bois."},
    "int_cuisson_o": {
        "en": "Take households off fuelwood, which is the first driver of "
              "cover loss and the demand end of the balancing loops that tie "
              "wood scarcity to cutting.",
        "fr": "Sortir les ménages du bois-énergie, premier moteur du recul du "
              "couvert et extrémité « demande » des boucles équilibrantes qui "
              "lient raréfaction du bois et coupe."},
    "int_cuisson_at": {
        "en": "Improved stoves at two efficiency levels · a supported "
              "eco-charcoal supply chain (carbonisation kilns, drying) · "
              "LPG starter kits where a distribution point exists · metering "
              "of household fuel consumption before and after",
        "fr": "Réchauds améliorés à deux niveaux de rendement · filière de "
              "charbon écologique accompagnée (fours de carbonisation, "
              "séchage) · kits GPL de démarrage là où un point de "
              "distribution existe · mesure de la consommation de combustible "
              "des ménages avant et après"},
    "int_cuisson_as": {
        "en": "Cooking demonstrations run by women's groups, in the "
              "organisations already standing · equipment microcredit "
              "distributed through those same organisations · agreement with "
              "charcoal producers on a conversion path rather than a ban · "
              "peer-to-peer follow-up of the first adopting households",
        "fr": "Démonstrations culinaires animées par des groupements de "
              "femmes, dans les organisations déjà debout · microcrédit "
              "d'équipement distribué par ces mêmes organisations · accord "
              "avec les producteurs de charbon sur une trajectoire de "
              "reconversion plutôt qu'une interdiction · suivi de pair à pair "
              "des premiers ménages équipés"},
    "int_cuisson_ac": {
        "en": "Ministry of Environment · microfinance institutions · "
              "community-based organisations · charcoal producers",
        "fr": "Ministère de l'Environnement · institutions de microfinance · "
              "organisations de base · producteurs de charbon"},
    "int_cuisson_cal": {
        "en": "Months 1–6 supply chain and stove supply · 7–18 rollout by "
              "communal section, starting where the associative fabric is "
              "strongest · 19–36 conversion of charcoal producers, follow-up "
              "survey at month 30",
        "fr": "Mois 1–6 filière et approvisionnement en réchauds · 7–18 "
              "déploiement par section communale, en commençant là où le "
              "tissu associatif est le plus solide · 19–36 reconversion des "
              "producteurs de charbon, enquête de suivi au mois 30"},
    "int_cuisson_r": {
        "en": "Equipment is bought and then abandoned, the classic failure of "
              "improved stove programmes · charcoal production is a cash "
              "income, and removing it without a replacement is refused",
        "fr": "L'équipement est acheté puis abandonné, l'échec classique des "
              "programmes de réchauds améliorés · la production de charbon est "
              "un revenu monétaire, et la supprimer sans substitut se heurte à "
              "un refus"},
    "int_cuisson_m": {
        "en": "Subsidy paid in two instalments, the second on proven use at "
              "month 6 · producers enter the eco-charcoal chain before any "
              "restriction, never after · monitoring on line 6 of the "
              "framework, which is already measured",
        "fr": "Subvention versée en deux fois, la seconde sur usage constaté "
              "au mois 6 · les producteurs entrent dans la filière de charbon "
              "écologique avant toute restriction, jamais après · suivi sur la "
              "ligne 6 du référentiel, déjà mesurée"},
    "int_cuisson_b": {
        "en": "Cover loss → wood scarcity → higher price → cutting becomes "
              "profitable → more cutting. An alternative fuel cuts the loop at "
              "its demand end.",
        "fr": "Recul du couvert → raréfaction → hausse du prix → la coupe "
              "devient rentable → coupe accrue. Une énergie alternative coupe "
              "la boucle du côté de la demande."},

    # ---------------- fiche : agro
    "int_agro_t": {"en": "Fertility without fire",
                   "fr": "La fertilité sans le feu"},
    "int_agro_p": {
        "en": "Food insecurity scores 0/10, the worst line of the whole "
              "framework, in the weakest dimension, the human one at 1.4/10.",
        "fr": "L'insécurité alimentaire est notée 0/10, la pire ligne du "
              "référentiel, dans la dimension la plus faible, la dimension "
              "humaine à 1,4/10."},
    "int_agro_o": {
        "en": "Replace slash-and-burn with practices that build soil, so that "
              "yields stop depending on opening new plots.",
        "fr": "Remplacer le brûlis par des pratiques qui construisent le sol, "
              "pour que le rendement cesse de dépendre de l'ouverture de "
              "nouvelles parcelles."},
    "int_agro_at": {
        "en": "Composting and green manure · live hedges and contour ditches "
              "on slopes · agroforestry combining fruit and timber species · "
              "improved seed adapted to a shorter rainy season · soil sampling "
              "at the start and at year three",
        "fr": "Compostage et engrais verts · haies vives et fossés en courbes "
              "de niveau sur pente · agroforesterie associant espèces "
              "fruitières et forestières · semences améliorées adaptées à une "
              "saison des pluies raccourcie · analyses de sol au départ et à "
              "la troisième année"},
    "int_agro_as": {
        "en": "Farmer field schools, one per communal section, run by farmers "
              "and not for them · demonstration plots held by respected "
              "farmers · work-exchange groups rebuilt around the new tasks · "
              "a burning ban negotiated at CASEC level and only once the "
              "alternative is available, never before",
        "fr": "Champs-écoles paysans, un par section communale, animés par des "
              "paysans et non pour eux · parcelles de démonstration tenues par "
              "des agriculteurs respectés · groupes d'entraide reconstitués "
              "autour des nouveaux travaux · interdiction du brûlis négociée "
              "au niveau du CASEC et seulement une fois l'alternative "
              "disponible, jamais avant"},
    "int_agro_ac": {
        "en": "Ministry of Agriculture · farmer organisations · CASEC · "
              "agricultural extension services",
        "fr": "Ministère de l'Agriculture · organisations paysannes · CASEC · "
              "services de vulgarisation agricole"},
    "int_agro_cal": {
        "en": "Months 1–12 field schools and demonstration plots · 13–36 "
              "spread by farmer-to-farmer contact · 37–60 negotiation of the "
              "burning rule, once yields on the demonstration plots can be "
              "shown",
        "fr": "Mois 1–12 champs-écoles et parcelles de démonstration · 13–36 "
              "diffusion de paysan à paysan · 37–60 négociation de la règle "
              "sur le brûlis, une fois les rendements des parcelles de "
              "démonstration démontrables"},
    "int_agro_r": {
        "en": "Soil-building pays back in three to five years, while the "
              "household needs to eat this season · tenure insecurity makes a "
              "long investment irrational on a plot one may lose",
        "fr": "Construire le sol se rembourse en trois à cinq ans, quand le "
              "ménage doit manger cette saison · l'insécurité foncière rend "
              "irrationnel un investissement long sur une parcelle qu'on peut "
              "perdre"},
    "int_agro_m": {
        "en": "Pair it with a quick-return activity, market gardening, small "
              "livestock, over the first two years · sequence it behind the "
              "tenure sheet wherever disputes are live · never a ban without "
              "a working alternative already in the field",
        "fr": "L'associer à une activité à retour rapide, maraîchage, petit "
              "élevage, sur les deux premières années · la séquencer derrière "
              "la fiche foncier là où les litiges sont vifs · jamais "
              "d'interdiction sans alternative déjà opérante au champ"},
    "int_agro_b": {
        "en": "Burning costs fertility → yields fall → new plots are opened by "
              "fire. Building soil turns the spiral the other way.",
        "fr": "Le brûlis coûte de la fertilité → les rendements chutent → on "
              "ouvre de nouvelles parcelles par le feu. Construire le sol "
              "retourne la spirale."},

    # ---------------- fiche : eau
    "int_eau_t": {"en": "Water, and the time it frees",
                  "fr": "L'eau, et le temps qu'elle libère"},
    "int_eau_p": {
        "en": "Access to improved drinking water scores 4/10, and it carries "
              "the heaviest weight of the whole framework (4.6), which is why "
              "it moves the index more than any other sheet.",
        "fr": "L'accès à une eau de boisson améliorée est noté 4/10, et il "
              "porte la pondération la plus lourde du référentiel (4,6), "
              "c'est pourquoi il déplace l'indice plus que toute autre fiche."},
    "int_eau_o": {
        "en": "Improve access to drinking water, the model's shortest path to "
              "health, and through it to the capacity to work.",
        "fr": "Améliorer l'accès à l'eau de boisson, le chemin le plus court "
              "du modèle vers la santé, et par elle vers la capacité de "
              "travail."},
    "int_eau_at": {
        "en": "Improved and protected water points within 30 minutes of "
              "dwellings · spring capping and gravity networks where the "
              "relief allows · household treatment where the source stays "
              "distant · bacteriological testing twice a year",
        "fr": "Points d'eau améliorés et protégés à moins de trente minutes "
              "des habitations · captage de sources et réseaux gravitaires là "
              "où le relief le permet · traitement à domicile là où la source "
              "reste éloignée · analyses bactériologiques deux fois par an"},
    "int_eau_as": {
        "en": "A water user committee per point, with a maintenance fund fed "
              "monthly · women trained on the pump and on the fund, since they "
              "carry the water · hygiene sessions attached to the point rather "
              "than delivered as a lecture · a repair rule written and posted "
              "before the point is handed over",
        "fr": "Un comité d'usagers par point d'eau, avec un fonds d'entretien "
              "alimenté mensuellement · femmes formées à la pompe et à la "
              "gestion du fonds, puisque ce sont elles qui portent l'eau · "
              "séances d'hygiène rattachées au point plutôt que délivrées en "
              "conférence · règle de réparation écrite et affichée avant la "
              "remise du point"},
    "int_eau_ac": {
        "en": "DINEPA · communal authorities · water user committees · NGOs",
        "fr": "DINEPA · autorités communales · comités d'usagers de l'eau · ONG"},
    "int_eau_cal": {
        "en": "Months 1–3 survey of existing points and of what broke them · "
              "4–15 rehabilitation and construction · 16–24 handover to the "
              "committees, with the fund proven to work over two dry seasons",
        "fr": "Mois 1–3 diagnostic des points existants et de ce qui les a "
              "cassés · 4–15 réhabilitation et construction · 16–24 remise aux "
              "comités, le fonds ayant fait ses preuves sur deux saisons "
              "sèches"},
    "int_eau_r": {
        "en": "The point breaks and stays broken, which is the ordinary fate "
              "of rural water infrastructure · seasonal drying of the "
              "resource, which the aridity indicator already signals",
        "fr": "Le point casse et reste cassé, sort ordinaire des ouvrages "
              "hydrauliques ruraux · tarissement saisonnier de la ressource, "
              "que l'indicateur d'aridité signale déjà"},
    "int_eau_m": {
        "en": "No handover without a funded maintenance account and a trained "
              "local repairer · spare parts held at communal level · siting "
              "checked against the aridity and vegetation indicators before "
              "any construction",
        "fr": "Aucune remise sans compte d'entretien approvisionné et "
              "réparateur local formé · pièces détachées stockées au niveau "
              "communal · implantation vérifiée au regard des indicateurs "
              "d'aridité et de végétation avant toute construction"},
    "int_eau_b": {
        "en": "Water → health → capacity to work → employment → income → "
              "satisfaction with public services. The loop closes back on "
              "itself.",
        "fr": "Eau → santé → capacité de travail → emploi → revenu → "
              "satisfaction des services publics. La boucle se referme sur "
              "elle-même."},

    # ---------------- fiche : finance
    "int_finance_t": {"en": "A financial account, and what it unlocks",
                      "fr": "Un compte, et ce qu'il débloque"},
    "int_finance_p": {
        "en": "Holding a financial account scores 1/10 and the income reserve "
              "3/10: a shock has nowhere to be absorbed except in trees cut or "
              "meals skipped.",
        "fr": "La détention d'un compte financier est notée 1/10 et la réserve "
              "de revenu 3/10 : un choc n'a nulle part où être absorbé, sinon "
              "en arbres coupés ou en repas sautés."},
    "int_finance_o": {
        "en": "Give households a place to hold a reserve, so that a shock "
              "stops being paid for by cutting trees or skipping meals.",
        "fr": "Donner aux ménages un endroit où tenir une réserve, pour qu'un "
              "choc cesse de se payer en arbres coupés ou en repas sautés."},
    "int_finance_at": {
        "en": "Mobile accounts opened on the strength of the national identity "
              "card · cash-in/cash-out agents at communal section level · "
              "productive microcredit tied to the clean cooking sheet · a "
              "savings product designed for the hurricane season",
        "fr": "Comptes mobiles ouverts sur présentation de la carte "
              "d'identité · agents de dépôt et de retrait au niveau de la "
              "section communale · microcrédit productif articulé à la fiche "
              "cuisson propre · produit d'épargne conçu pour la saison "
              "cyclonique"},
    "int_finance_as": {
        "en": "Existing tontines formalised rather than replaced · financial "
              "literacy through the community organisations, in Creole and in "
              "sessions of under an hour · group guarantee instead of "
              "collateral · women's groups first, since they hold the tontines",
        "fr": "Tontines existantes formalisées plutôt que remplacées · "
              "éducation financière par les organisations de base, en créole "
              "et en séances de moins d'une heure · caution solidaire à la "
              "place de la garantie matérielle · groupements de femmes en "
              "premier, puisque ce sont eux qui tiennent les tontines"},
    "int_finance_ac": {
        "en": "Central bank · microfinance institutions · mobile operators · "
              "community-based organisations",
        "fr": "Banque centrale · institutions de microfinance · opérateurs "
              "mobiles · organisations de base"},
    "int_finance_cal": {
        "en": "Months 1–6 agent network and product design · 7–18 opening "
              "campaign coupled with the identity card sheet · 19–30 "
              "productive credit, once the accounts have shown movement",
        "fr": "Mois 1–6 réseau d'agents et conception du produit · 7–18 "
              "campagne d'ouverture couplée à la fiche carte d'identité · "
              "19–30 crédit productif, une fois les comptes animés"},
    "int_finance_r": {
        "en": "Accounts opened and never used, the standard outcome of "
              "financial inclusion campaigns · over-indebtedness where credit "
              "arrives before income · no identity card, no account",
        "fr": "Des comptes ouverts et jamais utilisés, résultat habituel des "
              "campagnes d'inclusion financière · surendettement là où le "
              "crédit arrive avant le revenu · sans carte d'identité, pas de "
              "compte"},
    "int_finance_m": {
        "en": "Monitor active accounts, not opened accounts · credit only "
              "after two quarters of savings movement · sequence behind the "
              "identity card sheet, which conditions this one",
        "fr": "Suivre les comptes actifs et non les comptes ouverts · crédit "
              "seulement après deux trimestres de mouvements d'épargne · "
              "séquencer derrière la fiche carte d'identité, qui conditionne "
              "celle-ci"},
    "int_finance_b": {
        "en": "Income → account → income. A short reinforcing loop, which "
              "spins the right way as soon as it is entered.",
        "fr": "Revenu → compte → revenu. Une boucle renforçante courte, qui "
              "tourne dans le bon sens dès qu'on y entre."},

    # ---------------- fiche : alerte
    "int_alerte_t": {"en": "Warning that reaches, and a committee that acts",
                     "fr": "Une alerte qui arrive, un comité qui agit"},
    "int_alerte_p": {
        "en": "Local risk management committees score 1/10, in a territory "
              "that takes a hurricane season every year.",
        "fr": "Les comités locaux de gestion des risques sont notés 1/10, "
              "sur un territoire qui prend une saison cyclonique chaque année."},
    "int_alerte_o": {
        "en": "Turn a received message into an organised response, the "
              "cheapest lever of the framework, and the one with the shortest "
              "delay.",
        "fr": "Transformer un message reçu en réponse organisée, le levier le "
              "moins coûteux du référentiel, et celui dont le délai est le "
              "plus court."},
    "int_alerte_at": {
        "en": "One local risk committee per communal section · radio and SMS "
              "relay, with a fallback that works when the network is down · "
              "shelters inspected and repaired before each season · a mapped "
              "evacuation route per locality",
        "fr": "Un comité local de gestion des risques par section communale · "
              "relais radio et SMS, avec un dispositif de repli qui "
              "fonctionne réseau coupé · abris inspectés et réparés avant "
              "chaque saison · un itinéraire d'évacuation cartographié par "
              "localité"},
    "int_alerte_as": {
        "en": "Committees recruited inside the organisations already "
              "standing, not created from nothing · two drills a year, one "
              "before the season and one during · a named person per "
              "neighbourhood for the households nobody warns · debrief after "
              "every real alert, published locally",
        "fr": "Comités recrutés dans les organisations déjà debout, non créés "
              "à partir de rien · deux exercices par an, un avant la saison et "
              "un pendant · une personne nommée par quartier pour les ménages "
              "que personne ne prévient · débriefing après chaque alerte "
              "réelle, publié localement"},
    "int_alerte_ac": {
        "en": "Civil protection · CASEC · community-based organisations · "
              "community radios",
        "fr": "Protection civile · CASEC · organisations de base · radios "
              "communautaires"},
    "int_alerte_cal": {
        "en": "Months 1–4 committees set up before the season · 5–12 first "
              "drills and shelter repairs · annual cycle thereafter, "
              "re-anchored each year before June",
        "fr": "Mois 1–4 comités installés avant la saison · 5–12 premiers "
              "exercices et réparation des abris · cycle annuel ensuite, "
              "réamorcé chaque année avant juin"},
    "int_alerte_r": {
        "en": "A committee that exists on paper and not in a crisis · "
              "volunteer fatigue after two seasons without an event · the "
              "message arrives and nobody moves, which is what the framework "
              "actually measures",
        "fr": "Un comité qui existe sur le papier et pas dans la crise · "
              "essoufflement des bénévoles après deux saisons sans événement · "
              "le message arrive et personne ne bouge, ce que le référentiel "
              "mesure précisément"},
    "int_alerte_m": {
        "en": "Score the drill, not the committee's existence · rotate "
              "membership yearly and give the role a small allowance · "
              "monitoring on lines 22, 23 and 28 together, access, "
              "participation, committee, since only their combination proves "
              "the chain works",
        "fr": "Noter l'exercice et non l'existence du comité · renouveler les "
              "membres chaque année et rémunérer symboliquement la fonction · "
              "suivre ensemble les lignes 22, 23 et 28, accès, participation, "
              "comité, car seule leur combinaison prouve que la chaîne "
              "fonctionne"},
    "int_alerte_b": {
        "en": "This one does not turn a loop: it is a flow of information, "
              "Meadows' third level. Its effect is fast and narrow, which is "
              "exactly what a season of hurricanes demands.",
        "fr": "Celle-ci ne retourne pas une boucle : c'est un flux "
              "d'information, le troisième niveau de Meadows. Son effet est "
              "rapide et étroit, ce que réclame précisément une saison "
              "cyclonique."},

    # ---------------- fiche : foncier
    "int_foncier_t": {"en": "Tenure, and the horizon it opens",
                      "fr": "Le foncier, et l'horizon qu'il ouvre"},
    "int_foncier_p": {
        "en": "Tenure security scores 7/10, this sheet is **not** justified by "
              "a weak score. It is justified by its position: it is the "
              "upstream condition of every long agricultural investment, and "
              "the 7/10 hides sections where disputes are live.",
        "fr": "La sécurité foncière est notée 7/10, cette fiche n'est **pas** "
              "justifiée par un score faible. Elle l'est par sa position : "
              "elle est la condition amont de tout investissement agricole "
              "long, et le 7/10 masque des sections où les litiges sont vifs."},
    "int_foncier_o": {
        "en": "Secure land rights so that planting a tree becomes a rational "
              "act, nobody invests in ten years on a plot they may lose next "
              "season.",
        "fr": "Sécuriser les droits fonciers pour que planter un arbre "
              "redevienne un acte rationnel, personne n'investit à dix ans "
              "sur une parcelle qu'il peut perdre à la saison prochaine."},
    "int_foncier_at": {
        "en": "Participatory mapping of customary rights, plot by plot · "
              "recognition of occupancy documents by the communal authority · "
              "a local register that survives a change of mayor · tenure "
              "conditions attached to payments for ecosystem services",
        "fr": "Cartographie participative des droits coutumiers, parcelle par "
              "parcelle · reconnaissance des documents d'occupation par "
              "l'autorité communale · registre local qui survit à un "
              "changement de maire · conditions foncières attachées aux "
              "paiements pour services écosystémiques"},
    "int_foncier_as": {
        "en": "Mediation of disputes at CASEC level, with customary "
              "authorities sitting · public reading of the mapping so that "
              "objections are raised before the register closes · explicit "
              "attention to widows' and tenants' rights, which are the first "
              "to disappear in a formalisation",
        "fr": "Médiation des litiges au niveau du CASEC, autorités coutumières "
              "présentes · lecture publique de la cartographie pour que les "
              "objections sortent avant la clôture du registre · attention "
              "explicite aux droits des veuves et des métayers, les premiers à "
              "disparaître dans une formalisation"},
    "int_foncier_ac": {
        "en": "ONACA · CASEC · customary authorities · farmer organisations",
        "fr": "ONACA · CASEC · autorités coutumières · organisations paysannes"},
    "int_foncier_cal": {
        "en": "Months 1–12 mapping on two pilot sections · 13–36 extension and "
              "mediation · 37–60 recognition of the register, which depends on "
              "a political decision and not on the project",
        "fr": "Mois 1–12 cartographie sur deux sections pilotes · 13–36 "
              "extension et médiation · 37–60 reconnaissance du registre, qui "
              "dépend d'une décision politique et non du projet"},
    "int_foncier_r": {
        "en": "Formalisation dispossesses the weakest holders, the "
              "best-documented risk of every land programme · disputes "
              "reopened by the mapping itself · the register is not recognised "
              "and the work is worth nothing",
        "fr": "La formalisation dépossède les détenteurs les plus faibles, "
              "risque le mieux documenté de tout programme foncier · litiges "
              "rouverts par la cartographie elle-même · le registre n'est pas "
              "reconnu et le travail ne vaut rien"},
    "int_foncier_m": {
        "en": "Record secondary rights, grazing, gleaning, tenancy, as "
              "rights, not as gaps · mediation funded for two years beyond the "
              "mapping · start on the sections where disputes are fewest, to "
              "build a precedent rather than a conflict",
        "fr": "Consigner les droits secondaires, pâture, glanage, métayage, "
              "comme des droits et non comme des vides · médiation financée "
              "deux ans au-delà de la cartographie · commencer par les "
              "sections où les litiges sont les moins nombreux, pour "
              "construire un précédent plutôt qu'un conflit"},
    "int_foncier_b": {
        "en": "Tenure → agricultural productivity → less clearing → cover. "
              "A rule change, Meadows' fourth level: slow, contested, "
              "structural.",
        "fr": "Foncier → productivité agricole → moins de défrichement → "
              "couvert. Un changement de règle, quatrième niveau de Meadows : "
              "lent, disputé, structurel."},

    # ---------------- fiche : controle
    "int_controle_t": {"en": "Rules for the forest, and who holds them",
                       "fr": "Des règles pour la forêt, et qui les tient"},
    "int_controle_p": {
        "en": "Forest cover change scores 5/10, but the lever sits in 10 loops "
              "7 reinforcing and 3 balancing. It is one of the two tipping "
              "levers of the whole model.",
        "fr": "Le changement du couvert forestier est noté 5/10, mais le "
              "levier appartient à 10 boucles, 7 renforçantes et 3 "
              "équilibrantes. C'est l'un des deux leviers de basculement de "
              "tout le modèle."},
    "int_controle_o": {
        "en": "Put a brake on the relation the model finds most dominant, "
              "pressure on fuelwood against forest cover, present in 20 of the "
              "38 loops.",
        "fr": "Poser un frein sur la relation que le modèle trouve la plus "
              "dominante, la pression sur le bois contre le couvert "
              "forestier, présente dans 20 des 38 boucles."},
    "int_controle_at": {
        "en": "Felling permits tied to replanting · protection of the "
              "remaining mangrove, mapped before anything else · nurseries "
              "sized on the replanting obligation · satellite monitoring of "
              "cover, twice a year, on the same source as the framework",
        "fr": "Permis de coupe assortis de replantation · protection de la "
              "mangrove subsistante, cartographiée avant toute autre chose · "
              "pépinières dimensionnées sur l'obligation de replantation · "
              "suivi satellitaire du couvert, deux fois par an, sur la source "
              "même du référentiel"},
    "int_controle_as": {
        "en": "Community surveillance paid through payments for ecosystem "
              "services, because unpaid surveillance stops after one season · "
              "sanctions negotiated in assembly rather than imposed from "
              "outside · rules written with the charcoal producers who will "
              "have to live under them",
        "fr": "Surveillance communautaire rémunérée par des paiements pour "
              "services écosystémiques, parce qu'une surveillance non "
              "rémunérée s'arrête après une saison · sanctions négociées en "
              "assemblée plutôt qu'imposées de l'extérieur · règles écrites "
              "avec les producteurs de charbon qui devront vivre dessous"},
    "int_controle_ac": {
        "en": "Ministry of Environment · ANAP · CASEC · user associations",
        "fr": "Ministère de l'Environnement · ANAP · CASEC · associations "
              "d'usagers"},
    "int_controle_cal": {
        "en": "Months 1–9 rules negotiated and mangrove mapped · 10–30 paid "
              "surveillance and nurseries · 31–60 transfer of enforcement to "
              "the communal authority, if it holds",
        "fr": "Mois 1–9 règles négociées et mangrove cartographiée · 10–30 "
              "surveillance rémunérée et pépinières · 31–60 transfert du "
              "contrôle à l'autorité communale, si elle tient"},
    "int_controle_r": {
        "en": "Enforcement without an alternative fuel simply displaces the "
              "cutting · surveillance captured by local power · payments for "
              "ecosystem services stop and the surveillance stops with them",
        "fr": "Un contrôle sans énergie alternative ne fait que déplacer la "
              "coupe · surveillance captée par le pouvoir local · les "
              "paiements pour services écosystémiques cessent et la "
              "surveillance cesse avec eux"},
    "int_controle_m": {
        "en": "Never deploy this sheet alone: it is paired with the clean "
              "cooking sheet, which removes the demand rather than displacing "
              "it · surveillance roles rotated and publicly listed · the "
              "payment scheme secured for the full duration before the first "
              "rule is issued",
        "fr": "Ne jamais déployer cette fiche seule : elle va avec la fiche "
              "cuisson propre, qui supprime la demande au lieu de la déplacer · "
              "rôles de surveillance tournants et affichés publiquement · "
              "mécanisme de paiement sécurisé sur toute la durée avant la "
              "première règle édictée"},
    "int_controle_b": {
        "en": "Enforcement is the only lever that acts directly on the "
              "dominant relation. Alone it displaces the pressure; paired with "
              "the cooking sheet, it removes it.",
        "fr": "Le contrôle est le seul levier qui agisse directement sur la "
              "relation dominante. Seul, il déplace la pression ; associé à la "
              "fiche cuisson, il la supprime."},

    # ---------------- fiche : identite
    "int_identite_t": {"en": "The card, not the certificate",
                       "fr": "La carte, pas l'acte"},
    "int_identite_p": {
        "en": "**The calculation moved this sheet.** It targeted birth "
              "registration, that line scores 10/10, so pushing it yields "
              "almost nothing (+0.026). The blockage is one step further on: "
              "the national identity card, at 4/10, which conditions both the "
              "account and access to public services. Retargeted on the card, "
              "the same sheet is worth +0.064.",
        "fr": "**C'est le calcul qui a déplacé cette fiche.** Elle visait "
              "l'enregistrement des naissances, cette ligne est à 10/10, et "
              "la pousser ne rend donc presque rien (+0,026). Le blocage est "
              "un cran plus loin : la carte d'identité nationale, à 4/10, qui "
              "conditionne à la fois le compte et l'accès aux services "
              "publics. Recentrée sur la carte, la même fiche vaut +0,064."},
    "int_identite_o": {
        "en": "Get the identity card into the hands of adults who already have "
              "a birth certificate, closing a chain that is blocked at its "
              "second link, not its first.",
        "fr": "Mettre la carte d'identité entre les mains des adultes qui "
              "possèdent déjà un acte de naissance, débloquer une chaîne qui "
              "coince à son deuxième maillon, pas au premier."},
    "int_identite_at": {
        "en": "Mobile ONI enrolment sessions by communal section · late birth "
              "registration made free, for the minority still without a "
              "certificate · card delivery in the section rather than at the "
              "departmental capital · a shared list with the mobile operators "
              "so an account can be opened the same day",
        "fr": "Sessions d'enrôlement mobile de l'ONI par section communale · "
              "gratuité de l'enregistrement tardif, pour la minorité encore "
              "sans acte · remise de la carte dans la section plutôt qu'au "
              "chef-lieu · liste partagée avec les opérateurs mobiles pour "
              "qu'un compte s'ouvre le jour même"},
    "int_identite_as": {
        "en": "Enrolment announced through the community organisations and "
              "the churches, a week ahead · accompaniment of people who cannot "
              "read the forms · sessions timed outside market and planting "
              "days · systematic enrolment at schools and health facilities",
        "fr": "Enrôlement annoncé par les organisations de base et les "
              "églises, une semaine à l'avance · accompagnement des personnes "
              "qui ne peuvent pas lire les formulaires · sessions programmées "
              "hors jours de marché et de plantation · enrôlement "
              "systématique en centre de santé et à l'école"},
    "int_identite_ac": {
        "en": "ONI · civil registry offices · CASEC · schools and health "
              "facilities · mobile operators",
        "fr": "ONI · officiers d'état civil · CASEC · écoles et centres de "
              "santé · opérateurs mobiles"},
    "int_identite_cal": {
        "en": "Months 1–3 agreement with ONI and calendar by section · 4–15 "
              "enrolment rounds, two passes per section · 16–24 delivery and "
              "immediate coupling with the account sheet",
        "fr": "Mois 1–3 accord avec l'ONI et calendrier par section · 4–15 "
              "tournées d'enrôlement, deux passages par section · 16–24 "
              "remise des cartes et couplage immédiat avec la fiche compte"},
    "int_identite_r": {
        "en": "Cards produced centrally and never delivered, which is the "
              "usual failure point · a fee reappearing informally at the "
              "counter · people enrolled once and lost between the two passes",
        "fr": "Des cartes produites au centre et jamais remises, point de "
              "rupture habituel · des frais qui réapparaissent officieusement "
              "au guichet · des personnes enrôlées une fois et perdues entre "
              "les deux passages"},
    "int_identite_m": {
        "en": "Monitor cards **delivered**, not enrolments recorded · post the "
              "free-of-charge rule at the session and give a complaints "
              "number · receipt handed to every enrolled person, with the "
              "delivery date written on it",
        "fr": "Suivre les cartes **remises**, non les enrôlements enregistrés · "
              "afficher la gratuité sur place et donner un numéro de "
              "réclamation · récépissé remis à chaque personne enrôlée, avec "
              "la date de remise écrite dessus"},
    "int_identite_b": {
        "en": "Not a loop but a chain, and a blocked one: without a card, "
              "neither account nor services. Unblocking it costs little and "
              "opens two other sheets at once.",
        "fr": "Non pas une boucle mais une chaîne, et elle est bloquée : sans "
              "carte, ni compte ni services. La débloquer coûte peu et ouvre "
              "deux autres fiches à la fois."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _gras(t):
    """Échappe, puis rend les **doubles astérisques** en gras.

    Streamlit ne passe pas le markdown dans un bloc HTML injecté : sans cela,
    les astérisques s'affichent tels quels au milieu de la phrase.
    """
    out, morceaux = [], _e(t).split("**")
    for i, m in enumerate(morceaux):
        out.append(f"<b>{m}</b>" if i % 2 else m)
    return "".join(out)


def _fmt(v, dec=1, signe=False):
    if v is None:
        return "—"
    s = f"{v:+.{dec}f}" if signe else f"{v:.{dec}f}"
    return s.replace(".", ",")


@st.cache_data(show_spinner=False)
def _charger():
    g = M.charger()
    p = os.path.join(DATA, "resultats.json")
    res = None
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            res = json.load(f)
        res = res["indicateurs"] if isinstance(res, dict) \
            and "indicateurs" in res else res
    return g, {r["ligne"]: r for r in (res or [])}


def _libelle(n):
    return n["fr"] if i18n.get_lang() == "fr" else n["en"]


def _nom_indic(r):
    if i18n.get_lang() == "fr" and r.get("indicateur_fr"):
        return r["indicateur_fr"]
    return r.get("indicateur", "")


def scores_dimensions(par_ligne):
    """Score pondéré de chaque dimension — le critère « dimension faible ».

    Calculé ici plutôt que lu quelque part : la page doit pouvoir dire d'où
    vient le classement d'une dimension en faible, et le montrer.
    """
    num, den = {}, {}
    for r in par_ligne.values():
        s = (r.get("scores_corriges") or {}).get("Total")
        if s is None:
            continue
        d = DIM_DE.get(r.get("dimension") or "")
        if not d:
            continue
        p = r.get("ponderation") or 1
        num[d] = num.get(d, 0.0) + p * float(s)
        den[d] = den.get(d, 0.0) + p
    return {d: num[d] / den[d] for d in num if den[d]}


def moyenne_ponderee(par_ligne):
    """La moyenne pondérée du référentiel entier — la référence du critère
    « dimension faible ». Calculée, pas posée."""
    n = d = 0.0
    for r in par_ligne.values():
        s = (r.get("scores_corriges") or {}).get("Total")
        if s is None:
            continue
        p = r.get("ponderation") or 1
        n += p * float(s)
        d += p
    return (n / d) if d else 0.0


def _contributions(graphe, effets, variations, par_ligne):
    """Le détail arithmétique de l'effet sur l'indice.

    C'EST LA JUSTIFICATION DU CHIFFRE AFFICHÉ. Sans elle, « +0,069 » est une
    décoration à trois décimales ; avec elle, on voit quels indicateurs
    bougent, de combien, avec quelle pondération, et quelle part de l'effet
    vient du levier lui-même plutôt que de la cascade.
    """
    poids_total = sum((r.get("ponderation") or 1) for r in par_ligne.values()
                      if (r.get("scores_corriges") or {}).get("Total")
                      is not None)
    lignes, somme, direct = [], 0.0, 0.0
    for n in graphe["noeuds"]:
        lg = n.get("ligne")
        r = par_ligne.get(lg) if lg else None
        if not r or (r.get("scores_corriges") or {}).get("Total") is None:
            continue
        p = r.get("ponderation") or 1
        avant = float(r["scores_corriges"]["Total"])
        d = effets.get(n["id"], 0.0) + (variations or {}).get(n["id"], 0.0)
        apres = max(0.0, min(10.0, avant + d))
        ct = p * (apres - avant)
        if abs(ct) < 1e-6:
            continue
        somme += ct
        if n["id"] in (variations or {}):
            direct += ct
        lignes.append({"ligne": lg, "r": r, "p": p, "avant": avant,
                       "apres": apres, "ct": ct})
    lignes.sort(key=lambda x: -abs(x["ct"]))
    return {"lignes": lignes, "somme": somme, "poids_total": poids_total,
            "direct": direct,
            "part_directe": (direct / somme) if somme else 0.0}


def calculer(graphe, par_ligne, lst_boucles):
    """Enrichit chaque fiche de ce que le modèle en dit.

    Rien n'est écrit en dur : impact, indicateurs de suivi, boucles, critères
    de repérage, tout est déduit du graphe et de l'enquête.
    """
    par_id = {n["id"]: n for n in graphe["noeuds"]}
    etat = M.etat_courant(graphe, par_ligne)
    dims = scores_dimensions(par_ligne)
    ref = moyenne_ponderee(par_ligne)
    entrant, sortant = {}, {}
    for e in graphe["aretes"]:
        sortant[e["de"]] = sortant.get(e["de"], 0) + 1
        entrant[e["vers"]] = entrant.get(e["vers"], 0) + 1
    out = []
    for f in FICHES:
        cle = f["levier"]
        if cle not in par_id:
            continue
        var = {cle: float(f["cible"])}
        eff = M.propager(graphe, var)
        ei = M.effet_indice(graphe, eff, var, par_ligne)
        dec = _contributions(graphe, eff, var, par_ligne)

        # Les indicateurs de suivi : les lignes du référentiel les plus
        # déplacées par la simulation, hors le levier lui-même — celui-ci est
        # déjà l'indicateur de performance de la fiche.
        suivi = []
        for autre, d in sorted(eff.items(), key=lambda x: -abs(x[1])):
            n = par_id.get(autre)
            if not n or not n.get("ligne") or abs(d) <= M.SEUIL_NUL:
                continue
            if autre == cle:
                continue
            r = par_ligne.get(n["ligne"])
            if r:
                suivi.append((n, r, d))
            if len(suivi) >= 4:
                break

        dedans = [b for b in lst_boucles if cle in b["noeuds"]]
        renf = sum(1 for b in dedans if b["type"] == "renforcante")
        forte = max(dedans, key=lambda b: b["force"]) if dedans else None

        # Le problème traité, et son score mesuré : la colonne « Score » du
        # tableau Problème → Score → Boucle → Levier.
        rp = par_ligne.get(f["ligne_probleme"])
        score_p = (rp.get("scores_corriges") or {}).get("Total") if rp else None
        dim_p = DIM_DE.get((rp or {}).get("dimension") or "")
        out.append({
            **f, "noeud": par_id[cle], "depart": etat.get(cle),
            "delta": ei["delta"], "part_couverte": ei["part_couverte"],
            "dec": dec, "suivi": suivi,
            "boucles": len(dedans), "renforcantes": renf,
            "equilibrantes": len(dedans) - renf,
            "bascule": renf > 0 and len(dedans) - renf > 0,
            "boucle_forte": forte,
            "sortant": sortant.get(cle, 0), "entrant": entrant.get(cle, 0),
            "r_probleme": rp, "score_probleme": score_p, "dim_probleme": dim_p,
            "score_dim": dims.get(dim_p),
            "dim_faible": dim_p in dims and dims[dim_p] < ref,
        })
    return sorted(out, key=lambda x: -x["delta"])


STYLE = """
<style>
  .int-t   { font-size:16px; font-weight:700; color:#101728;
             letter-spacing:-.015em; margin:0; line-height:1.3; }
  .int-lab { font-size:11px; letter-spacing:.09em; text-transform:uppercase;
             font-weight:700; color:#8a93a5; margin:14px 0 3px; }
  .int-x   { font-size:13.5px; color:#3c4761; line-height:1.6; margin:0; }
  .int-chip{ display:inline-block; font-size:11.5px; font-weight:700;
             border-radius:999px; padding:3px 11px; margin:0 6px 6px 0; }
  .int-eff { font-size:21.5px; font-weight:700; letter-spacing:-.03em;
             font-variant-numeric:tabular-nums; line-height:1; }
  .int-num { font-variant-numeric:tabular-nums; }
  /* LES DEUX BLOCS QUE LE PROTOCOLE EXIGE, RENDUS IMPOSSIBLES À MANQUER.
     Ils étaient signalés par un simple label gris en capitales et se
     perdaient dans la fiche ; ils portent maintenant un encadré, un filet de
     couleur et un titre lisible. */
  .int-box { border:1px solid #e3e9f1; border-left:4px solid #c7d2e0;
             border-radius:8px; padding:11px 14px; height:100%;
             background:#fbfcfe; }
  .int-box-t { font-size:11.5px; font-weight:800; letter-spacing:.02em;
               margin:0 0 6px; }
  .int-box p { margin:0; font-size:12.5px; color:#3c4761; line-height:1.6; }
  .int-perf { border:1px solid #cfe6da; border-radius:8px; padding:12px 14px;
              background:#f3faf6; }
</style>
"""


def _bloc_reperage(fiches, par_ligne, dims, ref):
    """a) Le repérage des leviers, ses trois critères, et leurs chiffres."""
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{_e(T("int_rep"))}</div>',
                    unsafe_allow_html=True)

        # --- critère 1 : agir sur plusieurs causes
        st.markdown(
            f'<div class="int-lab" style="margin-top:2px">1 · '
            f'{_e(T("int_rep1"))}</div>'
            f'<p class="int-x" style="font-size:12.5px">{_gras(T("int_rep1_x"))}</p>',
            unsafe_allow_html=True)
        rangs = sorted(fiches, key=lambda x: (not x["bascule"], -x["boucles"],
                                              -(x["sortant"] + x["entrant"])))
        st.markdown("".join(
            f'<div style="display:grid;grid-template-columns:minmax(150px,2fr) '
            f'110px 130px 1fr;gap:10px;align-items:center;padding:5px 0;'
            f'border-bottom:1px solid #eef2f7;font-size:12px">'
            f'<div style="font-weight:600;color:{ENCRE}">'
            f'{_e(_libelle(f["noeud"]))}</div>'
            f'<div class="int-num" style="color:{ENCRE2}">'
            f'{f["sortant"]} → · {f["entrant"]} ←</div>'
            f'<div class="int-num" style="color:{ENCRE2}">{f["boucles"]} '
            f'<span style="color:{HAUSSE}">R{f["renforcantes"]}</span>/'
            f'<span style="color:{ALERTE}">B{f["equilibrantes"]}</span></div>'
            + (f'<div><span class="int-chip" style="background:#fdf3e3;'
               f'color:#a8560a;margin:0">{_e(T("int_bascule"))}</span></div>'
               if f["bascule"] else '<div></div>')
            + '</div>' for f in rangs), unsafe_allow_html=True)

        # --- critère 2 : dimensions faibles
        st.markdown(
            f'<div class="int-lab">2 · {_e(T("int_rep2"))}</div>'
            f'<p class="int-x" style="font-size:12.5px">{_gras(T("int_rep2_x"))}</p>',
            unsafe_allow_html=True)
        barres = []
        for d in sorted(dims, key=lambda k: dims[k]):
            v = dims[d]
            faible = v < ref
            c = BAISSE if faible else ENCRE3
            barres.append(
                f'<div style="display:grid;grid-template-columns:minmax(150px,'
                f'2fr) 3fr 54px 70px;gap:10px;align-items:center;padding:5px 0;'
                f'border-bottom:1px solid #eef2f7;font-size:12px">'
                f'<div style="font-weight:600;color:{ENCRE}">'
                f'{_e(T(d))}</div>'
                f'<div style="background:#f1f4f9;border-radius:5px;height:12px;'
                f'overflow:hidden"><div style="height:100%;border-radius:5px;'
                f'width:{max(v * 10, 1):.0f}%;background:{c}"></div></div>'
                f'<div class="int-num" style="text-align:right;font-weight:700;'
                f'color:{c}">{_fmt(v, 2)}</div>'
                + (f'<div style="font-size:11px;font-weight:700;color:{BAISSE};'
                   f'text-transform:uppercase;letter-spacing:.06em">'
                   f'{_e(T("int_dim_faible"))}</div>' if faible
                   else '<div></div>') + '</div>')
        st.markdown("".join(barres), unsafe_allow_html=True)
        st.caption(T("int_rep2_ref").replace("{v}", _fmt(ref, 2)))

        # --- critère 3 : mobilisation
        st.markdown(
            f'<div class="int-lab">3 · {_e(T("int_rep3"))}</div>',
            unsafe_allow_html=True)
        st.markdown(T("int_rep3_x"))
        mob = []
        for lg in LIGNES_MOBILISATION:
            r = par_ligne.get(lg)
            if not r:
                continue
            s = (r.get("scores_corriges") or {}).get("Total")
            if s is None:
                continue
            s = float(s)
            c = BAISSE if s <= 3 else (ALERTE if s < 6 else HAUSSE)
            mob.append(
                f'<div style="display:grid;grid-template-columns:1fr 3fr 44px;'
                f'gap:10px;align-items:center;padding:5px 0;'
                f'border-bottom:1px solid #eef2f7;font-size:12px">'
                f'<div style="color:{ENCRE}">L{lg} · '
                f'{_e(_nom_indic(r))}</div>'
                f'<div style="background:#f1f4f9;border-radius:5px;height:12px;'
                f'overflow:hidden"><div style="height:100%;border-radius:5px;'
                f'width:{max(s * 10, 1):.0f}%;background:{c}"></div></div>'
                f'<div class="int-num" style="text-align:right;font-weight:700;'
                f'color:{c}">{_fmt(s, 0)}/10</div></div>')
        st.markdown("".join(mob), unsafe_allow_html=True)
        st.markdown(T("int_rep3_lect"))


def _bloc_categories(fiches):
    """b) La catégorisation, en quatre colonnes."""
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{_e(T("int_cat_t"))}</div>',
                    unsafe_allow_html=True)
        cols = st.columns(4)
        for col, cat in zip(cols, ("structurel", "technique",
                                   "organisationnel", "comportemental")):
            c = CAT_COULEUR[cat]
            dedans = [f for f in fiches if f["cat"] == cat]
            with col:
                st.markdown(
                    f'<div style="border-top:3px solid {c};padding-top:8px">'
                    f'<div style="font-size:12.5px;font-weight:700;color:{c}">'
                    f'{_e(T("int_cat_" + cat))}</div>'
                    f'<div style="font-size:11.5px;color:{ENCRE3};'
                    f'margin-bottom:8px">{_e(T("int_cat_" + cat + "_x"))}</div>'
                    + "".join(
                        f'<div style="font-size:12px;color:{ENCRE};'
                        f'padding:4px 0;border-top:1px solid #eef2f7">'
                        f'{_e(T("int_" + f["id"] + "_t"))}</div>'
                        for f in dedans)
                    + '</div>', unsafe_allow_html=True)


def _bloc_tableau(fiches, par_id):
    """c) Le livrable : Problème → Score → Boucle → Levier."""
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{_e(T("int_tab"))}</div>',
                    unsafe_allow_html=True)
        gab = ("minmax(190px,2.6fr) 78px minmax(190px,2.6fr) "
               "minmax(140px,1.6fr) 86px")
        li = [f'<div style="display:grid;grid-template-columns:{gab};gap:12px;'
              f'padding:0 0 6px;font-size:11px;letter-spacing:.09em;'
              f'text-transform:uppercase;color:#8a93a5;font-weight:700">'
              f'<div>{_e(T("int_c_probleme"))}</div>'
              f'<div style="text-align:right">{_e(T("int_c_score"))}</div>'
              f'<div>{_e(T("int_c_boucle"))}</div>'
              f'<div>{_e(T("int_c_levier"))}</div>'
              f'<div style="text-align:right">{_e(T("int_c_impact"))}</div>'
              f'</div>']
        for f in fiches:
            r = f["r_probleme"]
            nom = _nom_indic(r) if r else "—"
            s = f["score_probleme"]
            cs = ENCRE3 if s is None else (
                BAISSE if float(s) <= 3 else
                (ALERTE if float(s) < 6 else HAUSSE))
            b = f["boucle_forte"]
            if b:
                ch = " → ".join(_libelle(par_id[x]) for x in b["noeuds"][:3])
                if len(b["noeuds"]) > 3:
                    ch += " → …"
                lettre = "R" if b["type"] == "renforcante" else "B"
                cb = HAUSSE if lettre == "R" else ALERTE
                bloc = (f'<div style="font-size:11.5px;color:{ENCRE2}">'
                        f'<span style="font-weight:700;color:{cb}">{lettre}</span> '
                        f'{_e(ch)}</div>')
            else:
                bloc = (f'<div style="font-size:11.5px;color:{ENCRE3};'
                        f'font-style:italic">{_e(T("int_hors_boucle"))}</div>')
            cc = CAT_COULEUR[f["cat"]]
            li.append(
                f'<div style="display:grid;grid-template-columns:{gab};'
                f'gap:12px;align-items:center;padding:8px 0;'
                f'border-bottom:1px solid #eef2f7">'
                f'<div style="font-size:12px;color:{ENCRE}">L'
                f'{f["ligne_probleme"]} · {_e(nom)}</div>'
                f'<div class="int-num" style="text-align:right;font-weight:700;'
                f'font-size:13px;color:{cs}">'
                f'{"—" if s is None else _fmt(float(s), 0) + "/10"}</div>'
                + bloc +
                f'<div style="font-size:12px;font-weight:600;color:{cc}">'
                f'{_e(T("int_" + f["id"] + "_t"))}</div>'
                f'<div class="int-num" style="text-align:right;font-size:12px;'
                f'font-weight:700;color:{HAUSSE}">'
                f'{_fmt(f["delta"], 3, True)}</div></div>')
        st.markdown("".join(li), unsafe_allow_html=True)
        st.caption(T("int_tab_note"))


def _bloc_justification(f):
    """D'où vient le chiffre — le calcul déplié, pas un ordre de grandeur."""
    d = f["dec"]
    with st.expander(f'{T("int_dou")} : {_fmt(f["delta"], 3, True)}'):
        st.caption(T("int_dou_f"))
        c1, c2, c3, c4 = st.columns(4)
        for col, lab, val in (
                (c1, T("int_dou_pose"),
                 _fmt(f["cible"], 1, True) + " pts"),
                (c2, T("int_dou_som"), _fmt(d["somme"], 2)),
                (c3, T("int_dou_poids"), _fmt(d["poids_total"], 1)),
                (c4, T("int_dou_res"), _fmt(f["delta"], 3, True))):
            with col:
                st.markdown(
                    f'<div style="font-size:10.5px;letter-spacing:.07em;'
                    f'text-transform:uppercase;color:#8a93a5;font-weight:700">'
                    f'{_e(lab)}</div><div class="int-num" style="font-size:17.5px;'
                    f'font-weight:700;color:{ENCRE}">{_e(val)}</div>',
                    unsafe_allow_html=True)

        pd_ = 100 * d["part_directe"]
        st.markdown(
            f'<p class="int-x" style="font-size:12.5px;margin-top:12px">'
            f'<b class="int-num">{pd_:.0f} %</b> {_e(T("int_dou_direct"))}, '
            f'<b class="int-num">{100 - pd_:.0f} %</b> '
            f'{_e(T("int_dou_casc"))}.</p>', unsafe_allow_html=True)

        pc = f["part_couverte"] or 0
        if pc:
            st.markdown(
                f'<p class="int-x" style="font-size:12.5px">'
                f'<b>{_e(T("int_dou_peri"))} : </b>'
                + _e(T("int_dou_peri_x")
                     .replace("{p}", f"{100 * pc:.0f}")
                     .replace("{v}", _fmt(f["delta"] / pc, 3, True)))
                + '</p>', unsafe_allow_html=True)

        st.markdown(f'<div class="int-lab">{_e(T("int_dou_det"))}</div>',
                    unsafe_allow_html=True)
        gab = "minmax(170px,3fr) 54px 54px 58px 104px"
        li = [f'<div style="display:grid;grid-template-columns:{gab};gap:8px;'
              f'padding:0 0 5px;font-size:10.5px;letter-spacing:.07em;'
              f'text-transform:uppercase;color:#8a93a5;font-weight:700">'
              f'<div>{_e(T("int_dou_c_ind"))}</div>'
              f'<div style="text-align:right">{_e(T("int_dou_c_p"))}</div>'
              f'<div style="text-align:right">{_e(T("int_dou_c_av"))}</div>'
              f'<div style="text-align:right">{_e(T("int_dou_c_ap"))}</div>'
              f'<div style="text-align:right">{_e(T("int_dou_c_ct"))}</div>'
              f'</div>']
        for x in d["lignes"][:8]:
            plaf = x["apres"] >= 9.999
            li.append(
                f'<div style="display:grid;grid-template-columns:{gab};gap:8px;'
                f'align-items:center;padding:4px 0;'
                f'border-bottom:1px solid #f2f5f9;font-size:11.5px">'
                f'<div style="color:{ENCRE}">L{x["ligne"]} · '
                f'{_e(_nom_indic(x["r"]))}</div>'
                f'<div class="int-num" style="text-align:right;color:{ENCRE3}">'
                f'{_fmt(x["p"], 2)}</div>'
                f'<div class="int-num" style="text-align:right;color:{ENCRE3}">'
                f'{_fmt(x["avant"], 1)}</div>'
                f'<div class="int-num" style="text-align:right;color:{ENCRE};'
                f'font-weight:600">{_fmt(x["apres"], 2)}'
                + ('&nbsp;⊤' if plaf else '') +
                f'</div>'
                f'<div class="int-num" style="text-align:right;font-weight:700;'
                f'color:{HAUSSE if x["ct"] > 0 else BAISSE}">'
                f'{_fmt(x["ct"], 3, True)}</div></div>')
        st.markdown("".join(li), unsafe_allow_html=True)
        if any(x["apres"] >= 9.999 for x in d["lignes"]):
            st.caption("⊤ — " + T("int_dou_plaf"))


def render(anciennes=None):
    # `anciennes` est accepté et IGNORÉ. Les anciennes pistes de travail ont été
    # retirées de la page : elles précédaient l'analyse causale et n'ajoutaient
    # rien à des fiches qui en descendent. L'argument reste dans la signature
    # pour qu'un app.py non encore mis à jour n'échoue pas au démarrage.
    del anciennes
    return _render()


def _render():
    graphe, par_ligne = _charger()
    par_id = {n["id"]: n for n in graphe["noeuds"]}
    st.markdown(STYLE, unsafe_allow_html=True)
    # PAS DE TITRE DE PAGE : la colonne de menu marque déjà la rubrique
    # courante. Le sous-titre part avec lui — il paraphrasait le titre.
    st.info(T("int_intro"))

    lst_boucles = M.boucles(graphe)
    fiches = calculer(graphe, par_ligne, lst_boucles)
    dims = scores_dimensions(par_ligne)
    ref = moyenne_ponderee(par_ligne)

    # LE PROTOCOLE, dit en tête : le lecteur doit savoir dans quel ordre les
    # fiches ont été produites avant de lire la première.
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{_e(T("int_proto"))}</div>',
                    unsafe_allow_html=True)
        cols = st.columns(4)
        for col, (let, cle) in zip(cols, (("a", "a"), ("b", "b"),
                                          ("c", "c"), ("d", "d"))):
            with col:
                st.markdown(
                    f'<div style="border-top:3px solid #d7dee9;padding-top:8px">'
                    f'<div style="font-size:11px;font-weight:700;color:#8a93a5;'
                    f'letter-spacing:.09em">{let.upper()}</div>'
                    f'<div style="font-size:12.5px;font-weight:700;'
                    f'color:{ENCRE};margin-top:2px">'
                    f'{_e(T("int_proto_" + cle))}</div>'
                    f'<div style="font-size:11px;color:{ENCRE3};margin-top:4px;'
                    f'line-height:1.5">{_e(T("int_proto_" + cle + "_x"))}</div>'
                    f'</div>', unsafe_allow_html=True)

    _bloc_reperage(fiches, par_ligne, dims, ref)
    _bloc_categories(fiches)
    _bloc_tableau(fiches, par_id)

    # LA TENSION EST LE CŒUR DE LA PAGE, pas une nuance de bas de page : les
    # fiches à effet immédiat et les leviers de basculement ne sont pas les
    # mêmes, et un programme qui ne retiendrait que les premières laisserait
    # la structure intacte.
    st.warning(T("int_tension"))

    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("int_recap")}</div>',
                    unsafe_allow_html=True)
        emax = max((abs(f["delta"]) for f in fiches), default=1) or 1
        recap = [
            f'<div style="display:grid;grid-template-columns:'
            f'minmax(180px,3fr) 3fr 76px 150px;gap:12px;padding:0 0 6px;'
            f'font-size:11px;letter-spacing:.09em;text-transform:uppercase;'
            f'color:#8a93a5;font-weight:700">'
            f'<div>{_e(T("int_c_fiche"))}</div>'
            f'<div style="grid-column:span 2">{_e(T("int_c_effet"))}</div>'
            f'<div>{_e(T("int_c_portee"))}</div></div>']
        for f in fiches:
            recap.append(
                f'<div style="display:grid;grid-template-columns:'
                f'minmax(180px,3fr) 3fr 76px 150px;gap:12px;align-items:center;'
                f'padding:7px 0;border-bottom:1px solid #eef2f7">'
                f'<div style="font-size:12.5px;font-weight:600;color:{ENCRE}">'
                f'{_e(T("int_" + f["id"] + "_t"))}</div>'
                f'<div style="background:#f1f4f9;border-radius:5px;height:14px;'
                f'overflow:hidden"><div style="height:100%;border-radius:5px;'
                f'width:{max(100 * f["delta"] / emax, 1):.0f}%;'
                f'background:{HAUSSE}"></div></div>'
                f'<div class="int-num" style="font-size:12px;font-weight:600;'
                f'color:{ENCRE};text-align:right">'
                f'{_fmt(f["delta"], 3, True)}</div>'
                + (f'<div><span class="int-chip" style="background:#fdf3e3;'
                   f'color:#a8560a;margin:0">{_e(T("int_bascule"))}</span>'
                   f'</div>' if f["bascule"] else
                   f'<div style="font-size:11px;color:{ENCRE3}">'
                   f'{f["boucles"]} {_e(T("int_boucles")).lower()}</div>')
                + '</div>')
        st.markdown("".join(recap), unsafe_allow_html=True)

    for f in fiches:
        with st.container(border=True):
            niv = f["meadows"]
            coul = NIVEAU_COULEUR[niv]
            cc = CAT_COULEUR[f["cat"]]
            g, d = st.columns([3.1, 1])
            with g:
                st.markdown(
                    f'<div class="int-t">{_e(T("int_" + f["id"] + "_t"))}</div>'
                    f'<div style="margin-top:8px">'
                    f'<span class="int-chip" style="background:{cc}1a;'
                    f'color:{cc}">{_e(T("int_cat_" + f["cat"]))}</span>'
                    f'<span class="int-chip" style="background:{coul}1a;'
                    f'color:{coul}">{niv} · {_e(T("int_n%d" % niv))}</span>'
                    f'<span class="int-chip" style="background:#f1f4f9;'
                    f'color:{ENCRE2}">{_e(T("int_faisabilite"))} : '
                    f'{_e(T("int_f_" + f["faisabilite"]))}</span>'
                    f'<span class="int-chip" style="background:#f1f4f9;'
                    f'color:{ENCRE2}">{_e(T("int_horizon"))} : '
                    f'{_e(T("int_h_" + f["horizon"]))}</span>'
                    f'<span class="int-chip" style="background:#f1f4f9;'
                    f'color:{ENCRE2}">{_e(T("int_mob"))} : '
                    f'{_e(T("int_mob_" + f["mobilisation"]))}</span>'
                    + (f'<span class="int-chip" style="background:#fdf3e3;'
                       f'color:#a8560a">{_e(T("int_bascule"))}</span>'
                       if f["bascule"] else '')
                    + '</div>', unsafe_allow_html=True)
            with d:
                c = HAUSSE if f["delta"] > 0 else ENCRE3
                st.markdown(
                    f'<div style="text-align:right">'
                    f'<div class="int-eff" style="color:{c}">'
                    f'{_fmt(f["delta"], 3, True)}</div>'
                    f'<div style="font-size:11.5px;color:{ENCRE3};'
                    f'margin-top:3px">{_e(T("int_effet"))}</div></div>',
                    unsafe_allow_html=True)

            _bloc_justification(f)

            st.markdown(
                f'<div class="int-lab">{_e(T("int_probleme"))}</div>',
                unsafe_allow_html=True)
            st.markdown(T("int_" + f["id"] + "_p"))
            st.markdown(
                f'<div class="int-lab">{_e(T("int_objectif"))}</div>'
                f'<p class="int-x">{_e(T("int_" + f["id"] + "_o"))}</p>',
                unsafe_allow_html=True)

            # ACTIVITÉS TECHNIQUES ET SOCIALES, dans deux encadrés distincts.
            # Le protocole demande les deux ; les fondre dans un même
            # paragraphe reviendrait à n'en montrer qu'une.
            at, asoc = st.columns(2)
            with at:
                st.markdown(
                    f'<div class="int-box" style="border-left-color:#2166ac">'
                    f'<div class="int-box-t" style="color:#2166ac">⚙ '
                    f'{_e(T("int_act_tech"))}</div>'
                    f'<p>{_e(T("int_" + f["id"] + "_at"))}</p></div>',
                    unsafe_allow_html=True)
            with asoc:
                st.markdown(
                    f'<div class="int-box" style="border-left-color:#0f8fa8">'
                    f'<div class="int-box-t" style="color:#0f8fa8">◍ '
                    f'{_e(T("int_act_soc"))}</div>'
                    f'<p>{_e(T("int_" + f["id"] + "_as"))}</p></div>',
                    unsafe_allow_html=True)

            # INDICATEURS DE PERFORMANCE : la cible chiffrée sur le levier, et
            # les lignes déjà mesurées qui la constateront.
            # INDICATEURS DE PERFORMANCE : l'objectif de score chiffré, en
            # gros, avec le point de départ mesuré et le point visé. C'est le
            # livrable du protocole ; il ne doit pas se lire comme une note.
            dep = (_fmt(f["depart"]) + " / 10") if f["depart"] is not None \
                else "—"
            vise = (_fmt(min(10.0, f["depart"] + f["cible"])) + " / 10") \
                if f["depart"] is not None else "—"
            st.markdown(
                f'<div class="int-perf">'
                f'<div class="int-box-t" style="color:{HAUSSE}">◎ '
                f'{_e(T("int_perf"))}</div>'
                f'<div style="display:flex;gap:28px;flex-wrap:wrap;'
                f'align-items:baseline">'
                f'<div><span class="int-num" style="font-size:24px;'
                f'font-weight:800;letter-spacing:-.02em;color:{HAUSSE}">'
                f'{_fmt(f["cible"], 1, True)} pt</span>'
                f'<span style="font-size:11.5px;color:{ENCRE2};'
                f'margin-left:9px">{_e(T("int_perf_cible"))} : '
                f'{_e(_libelle(f["noeud"]))}</span></div>'
                f'<div style="font-size:14px;color:{ENCRE2};font-weight:600" '
                f'class="int-num">{_e(dep)} → <b style="color:{ENCRE}">'
                f'{_e(vise)}</b></div></div></div>',
                unsafe_allow_html=True)
            if f["suivi"]:
                st.markdown("".join(
                    f'<div style="display:flex;gap:12px;align-items:baseline;'
                    f'padding:5px 0;border-bottom:1px solid #eef2f7">'
                    f'<div style="flex:1 1 auto;font-size:12.5px;'
                    f'color:{ENCRE}">L{r["ligne"]} · {_e(_nom_indic(r))}</div>'
                    f'<div class="int-num" style="font-size:12px;'
                    f'font-weight:700;color:{HAUSSE if dd > 0 else BAISSE};'
                    f'white-space:nowrap">'
                    f'{"↑" if dd > 0 else "↓"} {_fmt(dd, 2, True)}</div></div>'
                    for n, r, dd in f["suivi"]), unsafe_allow_html=True)
            st.caption(T("int_suivi_note"))

            ga, dr = st.columns(2)
            with ga:
                st.markdown(
                    f'<div class="int-lab">{_e(T("int_acteurs"))}</div>'
                    f'<p class="int-x" style="font-size:12.5px">'
                    f'{_e(T("int_" + f["id"] + "_ac"))}</p>',
                    unsafe_allow_html=True)
            with dr:
                st.markdown(
                    f'<div class="int-lab">{_e(T("int_calendrier"))} · '
                    f'{_e(T("int_h_" + f["horizon"]))}</div>'
                    f'<p class="int-x" style="font-size:12.5px">'
                    f'{_e(T("int_" + f["id"] + "_cal"))}</p>',
                    unsafe_allow_html=True)

            st.markdown(
                f'<div class="int-lab">{_e(T("int_risques"))}</div>'
                f'<p class="int-x" style="font-size:12.5px">'
                f'<b style="color:{BAISSE}">{_e(T("int_risque"))}</b> : '
                f'{_e(T("int_" + f["id"] + "_r"))}</p>'
                f'<p class="int-x" style="font-size:12.5px;margin-top:6px">'
                f'<b style="color:{HAUSSE}">{_e(T("int_attenuation"))}</b> : '
                f'{_e(T("int_" + f["id"] + "_m"))}</p>'
                f'<div class="int-lab">{_e(T("int_boucle_visee"))}</div>'
                f'<p class="int-x">{_e(T("int_" + f["id"] + "_b"))}</p>'
                f'<p class="int-x" style="font-size:11.5px;color:{ENCRE3};'
                f'margin-top:6px">{_e(T("int_depart"))} : '
                f'{_e(_libelle(f["noeud"]))} : <b>{_e(dep)}</b> · '
                f'{_e(T("int_boucles"))} : {f["boucles"]} '
                f'<span style="color:{HAUSSE}">R{f["renforcantes"]}</span> / '
                f'<span style="color:{ALERTE}">B{f["equilibrantes"]}</span>'
                f'</p>', unsafe_allow_html=True)

    st.caption(T("int_perf_note"))
    st.caption(T("int_effet_note"))
    st.caption(T("int_n_note"))
