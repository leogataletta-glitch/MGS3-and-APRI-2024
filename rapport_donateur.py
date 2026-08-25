"""Rapport donateur : ce que le financement a permis de découvrir.

CE QUE CETTE PAGE EST, ET CE QU'ELLE N'EST PAS
==============================================

Ce n'est pas un tableau de bord de plus. Le site en a déjà, et ils répondent à
« combien ». Celui-ci répond à une question que personne d'autre ne pose ici :
qu'est-ce que l'argent investi a produit comme CONNAISSANCE, et en quoi cette
connaissance change la façon d'investir ensuite.

D'où une lecture en six chapitres, dans l'ordre d'un raisonnement :
ce que nous avons fait, pourquoi il fallait le faire, ce que nous avons trouvé,
où le système bloque, ce que cela change pour l'argent, et ce qui reste après
la fin du projet.

LA RÈGLE QUI COMMANDE TOUT LE FICHIER
=====================================

Aucun chiffre n'est écrit en dur. Tout est relu à l'affichage depuis
`resultats.json`, `ocb.json`, `croisement_index.json` et le graphe causal. Là
où la donnée n'existe pas, la page l'écrit noir sur blanc au lieu de meubler :
il n'y a qu'une vague d'enquête, donc aucune comparaison « avant / après » sur
les ménages n'est possible, et la page le dit à l'endroit où un lecteur
s'attendrait à la trouver.

TROIS REGISTRES, JAMAIS MÉLANGÉS
================================

Chaque affirmation de la page appartient à l'un de trois registres, et porte sa
marque :

    DONNÉE OBSERVÉE   ce que l'enquête mesure, sans commentaire
    INTERPRÉTATION    ce que nous en déduisons, et qui peut se discuter
    IMPLICATION       ce que cela suggère pour la décision

Un bailleur qui lit doit pouvoir séparer d'un coup d'œil ce qui est mesuré de
ce qui est raisonné. C'est la seule protection contre le rapport d'impact qui
présente une opinion avec l'autorité d'un chiffre.

L'HISTOIRE DES COCHONS EST UN EXEMPLE, ET LA PAGE LE DIT
========================================================

Le chapitre 2 raconte une distribution d'animaux pour faire comprendre la
différence entre un indicateur d'activité et une trajectoire de résilience.
Cette histoire ne vient PAS de l'enquête : aucune donnée d'intervention n'a été
collectée ici. Elle est encadrée et étiquetée comme illustration, parce qu'un
exemple qu'on laisse passer pour un résultat est un mensonge par mise en page.
"""

import json
import os

import streamlit as st

import boucles_moteur as M
import filtres
import i18n
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"
BORD, PAPIER = "#e3eaf3", "#f7f9fc"
VERT, BLEU, AMBRE, ROUGE, GRIS = ("#1a8a4f", "#2166ac", "#d1730c",
                                  "#c33a24", "#9aa4b5")
OR = "#8a6d1f"

DIMS = [("dim1", "I. PHYSICAL AND INFRASTRUCTURAL DIMENSION"),
        ("dim2", "II. INSTITUTIONAL, TECHNOLOGICAL, AND GOVERNANCE  DIMENSION"),
        ("dim3", "III.  ENVIRONMENTAL AND ECOLOGICAL DIMENSION"),
        ("dim4", "IV. ECONOMIC, LIVELIHOODS, AND FOOD SECURITY DIMENSION"),
        ("dim5", "V. SOCIAL AND COMMUNITY DIMENSION"),
        ("dim6", "VI. HUMAN DIMENSION"),
        ("dim7", "VII. CULTURAL, IDENTITY-BASED, AND PSYCHOLOGICAL DIMENSION")]
COURT = {"dim1": ("Physical", "Physique"),
         "dim2": ("Institutional", "Institutions"),
         "dim3": ("Environment", "Environnement"),
         "dim4": ("Economy", "Économie"),
         "dim5": ("Social", "Social"),
         "dim6": ("Human", "Humain"),
         "dim7": ("Cultural", "Culturel")}
TEINTE = {"dim1": BLEU, "dim2": "#6a51a3", "dim3": VERT, "dim4": AMBRE,
          "dim5": "#b5451f", "dim6": "#0f7b8a", "dim7": GRIS}

GROUPES_SOC = ["Homme", "Femme", "Cat A", "Cat B", "Cat C",
               "<25", "25-39", "40-59", "60+"]
PAYSAGES = ["Littoral", "Montagne"]
SECTIONS = ["Anse à Drick", "Barbois", "Dumont", "Débouchette", "Mouline",
            "Quentin", "Beaulieu", "Blactote", "Dalmette", "Trichet"]

CHAPITRES = ("rap_c1", "rap_c2", "rap_c3", "rap_c4", "rap_c5", "rap_c6")

TEXTES = {
    "mode_rapport": {"en": "Donor Report", "fr": "Rapport donateur"},
    "rap_titre": {"en": "What your funding made it possible to find out",
                 "fr": "Ce que votre financement a permis de découvrir"},
    "rap_sous": {"en": "Sud and Grand'Anse, Haiti · 2024 household survey",
                "fr": "Sud et Grand'Anse, Haïti · enquête ménage 2024"},

    "rap_c1": {"en": "In two minutes", "fr": "En deux minutes"},
    "rap_c2": {"en": "The fieldwork", "fr": "Le travail de terrain"},
    "rap_c3": {"en": "Why it was needed", "fr": "Pourquoi il fallait le faire"},
    "rap_c4": {"en": "What the survey found", "fr": "Ce que l'enquête a trouvé"},
    "rap_c5": {"en": "Where it is blocked", "fr": "Où cela bloque"},
    "rap_c6": {"en": "What remains afterwards", "fr": "Ce qui reste après"},

    # --- registres
    "rap_obs": {"en": "Observed data", "fr": "Donnée observée"},
    "rap_int": {"en": "Interpretation", "fr": "Interprétation"},
    "rap_imp": {"en": "Implication for action",
               "fr": "Implication pour l'action"},
    "rap_exemple": {"en": "Illustration, not a survey result",
                   "fr": "Illustration, pas un résultat d'enquête"},
    "rap_absent": {"en": "Data not available", "fr": "Donnée non disponible"},

    # ---------------------------------------------------------- chapitre 1
    "rap_1_t": {"en": "Impact at a glance",
               "fr": "L'essentiel en un coup d'œil"},
    "rap_1_x": {
        "en": "One page for a programme director with five minutes. Every "
              "figure below is read from the survey files at display time.",
        "fr": "Une page pour un directeur de programme qui a cinq minutes. "
              "Chaque chiffre ci-dessous est relu dans les fichiers d'enquête "
              "au moment de l'affichage."},
    "rap_1_fait": {"en": "What was done", "fr": "Ce qui a été fait"},
    "rap_1_fait_x": {
        "en": "A full household survey across ten communal sections of two "
              "departments, scored against a {t}-indicator resilience "
              "framework covering {d} dimensions.",
        "fr": "Une enquête ménage complète sur dix sections communales de "
              "deux départements, notée contre un référentiel de résilience "
              "de {t} indicateurs couvrant {d} dimensions."},
    "rap_1_trois": {"en": "Three findings that were not visible before",
                   "fr": "Trois constats qui n'étaient pas visibles avant"},
    "rap_1_bloc": {"en": "Three binding constraints",
                  "fr": "Trois blocages qui commandent le reste"},
    "rap_1_suite": {"en": "What it changes for the next investment",
                   "fr": "Ce que cela change pour le prochain investissement"},

    # ---------------------------------------------------------- chapitre 2
    "rap_2_t": {"en": "What your investment made possible",
               "fr": "Ce que votre investissement a permis"},
    "rap_2_x": {
        "en": "Behind every chart on this platform there is fieldwork: "
              "households visited one by one, questionnaires administered "
              "face to face, community organisations interviewed on site. "
              "These are the volumes.",
        "fr": "Derrière chaque graphique de cette plateforme, il y a du "
              "terrain : des ménages visités un par un, des questionnaires "
              "administrés en face à face, des organisations communautaires "
              "rencontrées sur place. Voici les volumes."},
    "rap_2_men": {"en": "households surveyed", "fr": "ménages enquêtés"},
    "rap_2_sec": {"en": "communal sections", "fr": "sections communales"},
    "rap_2_dep": {"en": "departments", "fr": "départements"},
    "rap_2_pay": {"en": "pilot landscapes", "fr": "paysages pilotes"},
    "rap_2_que": {"en": "questions per questionnaire",
                 "fr": "questions par questionnaire"},
    "rap_2_rep": {"en": "questionnaire fields, at most",
                 "fr": "champs de questionnaire, au plus"},
    "rap_2_ocb": {"en": "community organisations profiled",
                 "fr": "organisations communautaires documentées"},
    "rap_2_ind": {"en": "framework indicators", "fr": "indicateurs du référentiel"},
    "rap_2_sco": {"en": "of them scored to date", "fr": "dont scorés à ce jour"},
    "rap_2_dim": {"en": "resilience dimensions", "fr": "dimensions de résilience"},
    "rap_2_dec": {"en": "published breakdowns", "fr": "découpages publiés"},
    "rap_2_grp": {"en": "social groups compared", "fr": "groupes sociaux comparés"},
    "rap_2_phr": {
        "en": "These results do not rest on {t} indicators. They rest on "
              "**{n} households** questioned across **{s} communal "
              "sections**, each answering up to {q} questions, which is "
              "at most **{r} questionnaire fields**. That is what makes it "
              "possible to compare lived realities rather than "
              "administrative counts.",
        "fr": "Ces résultats ne reposent pas sur {t} indicateurs. Ils "
              "reposent sur **{n} ménages** interrogés dans **{s} sections "
              "communales**, chacun répondant à un questionnaire de {q} "
              "questions, soit au plus **{r} champs remplis**. "
              "C'est ce qui permet de comparer des réalités vécues plutôt "
              "que des comptages administratifs."},
    "rap_2_ocb_x": {
        "en": "Alongside households, {n} community organisations were "
              "profiled in {s} of the ten sections. Two sections returned no "
              "organisation profile, and that gap is recorded rather than "
              "filled: {v}.",
        "fr": "À côté des ménages, {n} organisations communautaires ont été "
              "documentées dans {s} des dix sections. Deux sections n'ont "
              "rendu aucune fiche, et ce manque est consigné plutôt que "
              "comblé : {v}."},
    "rap_2_couv": {"en": "Geographic coverage", "fr": "Couverture géographique"},
    "rap_2_couv_x": {
        "en": "Ten communal sections, in the coastal plain and the mountain "
              "interior, across the Sud and Grand'Anse departments. Sample "
              "sizes per section run from {mn} to {mx} households.",
        "fr": "Dix sections communales, en plaine littorale et à l'intérieur "
              "montagneux, sur les départements du Sud et de la Grand'Anse. "
              "Les effectifs par section vont de {mn} à {mx} ménages."},

    # ---------------------------------------------------------- chapitre 3
    "rap_3_t": {"en": "Why this work was needed",
               "fr": "Pourquoi ce travail était nécessaire"},
    "rap_3_x": {
        "en": "A project can look successful on its indicator and leave no "
              "household more resilient. This is the problem the survey was "
              "built to solve.",
        "fr": "Un projet peut afficher un bon indicateur sans qu'aucun ménage "
              "ne soit plus résilient. C'est le problème que l'enquête a été "
              "conçue pour traiter."},
    "rap_3_hist_t": {"en": "Five hundred pigs", "fr": "Cinq cents cochons"},
    "rap_3_hist": {
        "en": "Imagine an organisation helping a Haitian community by "
              "distributing five hundred Duroc pigs to five hundred "
              "households. The result is easy to measure and easy to report: "
              "**500 pigs distributed, target met**.\n\nAnd then what? Were "
              "the pigs raised, sold, eaten? Was there feed? Was there a "
              "market? Did the households have land? Did disease strike? Was "
              "there credit? Did selling one animal actually improve the "
              "capacity to face a shock? Was the income reinvested? Did the "
              "community hold the conditions needed to turn a one-off "
              "delivery into a resilience trajectory?\n\nWithout that "
              "information it is easy to look at an isolated result and "
              "conclude too quickly that the project failed, or that "
              "beneficiaries did not know how to use the help.",
        "fr": "Imaginez une organisation qui aide une communauté haïtienne "
              "en distribuant cinq cents cochons de race Duroc à cinq cents "
              "ménages. Le résultat est facile à mesurer et facile à "
              "rapporter : **500 cochons distribués, cible atteinte**.\n\nEt "
              "ensuite ? Les cochons ont-ils été élevés, vendus, consommés ? "
              "Y avait-il de quoi les nourrir ? Existait-il un marché ? Les "
              "ménages avaient-ils de la terre ? La maladie a-t-elle frappé ? "
              "Y avait-il du crédit ? La vente d'un animal a-t-elle "
              "réellement amélioré la capacité à encaisser un choc ? Le "
              "revenu a-t-il été réinvesti ? La communauté réunissait-elle "
              "les conditions pour transformer une livraison ponctuelle en "
              "trajectoire de résilience ?\n\nSans cette information, il est "
              "facile de regarder un résultat isolé et de conclure trop vite "
              "que le projet n'a pas marché, ou que les bénéficiaires n'ont "
              "pas su se servir de l'aide."},
    "rap_3_quest": {
        "en": "The survey asks a different question: **what allowed, or "
              "prevented, a household from turning an intervention into "
              "resilience?**",
        "fr": "L'enquête pose une autre question : **qu'est-ce qui a permis, "
              "ou empêché, un ménage de transformer une intervention en "
              "résilience ?**"},
    "rap_3_deux_t": {"en": "From the isolated indicator to the system",
                    "fr": "De l'indicateur isolé au système"},
    "rap_3_trad": {"en": "Traditional approach", "fr": "Approche traditionnelle"},
    "rap_3_trad_x": {"en": "Intervention, indicator, result. The chain has "
                          "three links and stops at the delivery.",
                    "fr": "Intervention, indicateur, résultat. La chaîne a "
                          "trois maillons et s'arrête à la livraison."},
    "rap_3_pays": {"en": "Landscape approach", "fr": "Approche paysage"},
    "rap_3_pays_x": {
        "en": "The same intervention, followed through everything that has "
              "to hold for it to become resilience. A single weak link caps "
              "the whole chain, and it is rarely the intervention itself.",
        "fr": "La même intervention, suivie à travers tout ce qui doit tenir "
              "pour qu'elle devienne de la résilience. Un seul maillon faible "
              "plafonne toute la chaîne, et ce n'est presque jamais "
              "l'intervention elle-même."},
    "rap_3_concl": {
        "en": "Resilience is a system, not an indicator. An intervention can "
              "fail without being a bad intervention, simply because another "
              "link was weak. This platform exists to name that link.",
        "fr": "La résilience est un système, pas un indicateur. Une "
              "intervention peut échouer sans être mauvaise, simplement "
              "parce qu'un autre maillon était faible. Cette plateforme "
              "existe pour nommer ce maillon."},

    # ---------------------------------------------------------- chapitre 4
    "rap_4_t": {"en": "What we found in the field",
               "fr": "Ce que nous avons découvert sur le terrain"},
    "rap_4_ind": {"en": "Overall resilience index", "fr": "Indice global de résilience"},
    "rap_4_ind_x": {"en": "weighted mean of the {n} scored indicators",
                   "fr": "moyenne pondérée des {n} indicateurs scorés"},
    "rap_4_pay_t": {"en": "Two landscapes, two configurations",
                   "fr": "Deux paysages, deux configurations"},
    "rap_4_pay_avert": {
        "en": "Neither landscape is better than the other. They hold up "
              "differently, and it is the difference in configuration, not a "
              "ranking, that tells where to act.",
        "fr": "Aucun des deux paysages n'est meilleur que l'autre. Ils "
              "tiennent différemment, et c'est l'écart de configuration, pas "
              "un classement, qui dit où agir."},
    "rap_4_radar_t": {"en": "Compare two profiles", "fr": "Comparer deux profils"},
    "rap_4_radar_x": {
        "en": "Six dimensions, weighted mean out of ten. Pick any two of the "
              "published breakdowns: landscapes, communal sections, or "
              "social groups.",
        "fr": "Six dimensions, moyenne pondérée sur dix. Choisissez deux des "
              "découpages publiés : paysages, sections communales ou groupes "
              "sociaux."},
    "rap_4_a": {"en": "Profile A", "fr": "Profil A"},
    "rap_4_b": {"en": "Profile B", "fr": "Profil B"},
    "rap_4_ecart": {"en": "Largest gap", "fr": "Écart le plus grand"},
    "rap_4_dim7": {
        "en": "The seventh dimension, cultural and psychological, has no "
              "scored indicator yet and is left off the radar rather than "
              "drawn at zero.",
        "fr": "La septième dimension, culturelle et psychologique, n'a encore "
              "aucun indicateur scoré : elle est laissée hors du radar "
              "plutôt que dessinée à zéro."},
    "rap_4_grp_t": {"en": "Who is actually behind?",
                   "fr": "Qui reste réellement en retrait ?"},
    "rap_4_grp_x": {
        "en": "Social groups can only be compared on the {n} indicators that "
              "actually vary between them. The satellite indicators are "
              "identical for every group in a given section by construction, "
              "so including them would flatten the gaps and flatter the "
              "result.",
        "fr": "Les groupes sociaux ne peuvent être comparés que sur les {n} "
              "indicateurs qui varient réellement entre eux. Les indicateurs "
              "satellitaires sont identiques pour tous les groupes d'une même "
              "section par construction : les inclure aplatirait les écarts "
              "et embellirait le résultat."},
    "rap_4_temps_t": {"en": "And over time?", "fr": "Et dans le temps ?"},
    "rap_4_temps_x": {
        "en": "There is one survey wave. No before-and-after comparison of "
              "household indicators is possible, and none is shown. What does "
              "have a history is the satellite record: forest cover since "
              "2000, rainfall since 1981, surface temperature since 2001. "
              "Those trajectories are in the Trajectories section.",
        "fr": "Il n'y a qu'une vague d'enquête. Aucune comparaison avant "
              "après des indicateurs ménages n'est possible, et aucune n'est "
              "montrée. Ce qui a une histoire, c'est le relevé satellitaire : "
              "couvert forestier depuis 2000, pluie depuis 1981, température "
              "de surface depuis 2001. Ces trajectoires sont dans la rubrique "
              "Trajectoires."},
    "rap_4_sec_t": {"en": "Ten sections, one common base",
                   "fr": "Dix sections, une base commune"},
    "rap_4_sec_x": {
        "en": "Sections are compared on the {n} indicators available for all "
              "ten of them, which is why these figures differ slightly from "
              "the published index.",
        "fr": "Les sections sont comparées sur les {n} indicateurs "
              "disponibles pour les dix, ce qui explique que ces chiffres "
              "diffèrent un peu de l'indice publié."},

    # ---------------------------------------------------------- chapitre 5
    "rap_5_t": {"en": "Where resilience is blocked",
               "fr": "Où la résilience est bloquée"},
    "rap_5_x": {
        "en": "A low score is not automatically a bottleneck. What makes a "
              "constraint binding is the combination of two things: the "
              "variable is low **and** the causal model says a great deal "
              "passes through it. Both are computed here.",
        "fr": "Un score bas n'est pas automatiquement un blocage. Ce qui rend "
              "une contrainte bloquante, c'est la combinaison de deux "
              "choses : la variable est basse **et** le modèle causal dit "
              "qu'il passe beaucoup par elle. Les deux sont calculés ici."},
    "rap_5_col1": {"en": "Current level", "fr": "Niveau actuel"},
    "rap_5_col2": {"en": "What passes through it",
                  "fr": "Ce qui passe par elle"},
    "rap_5_col3": {"en": "Binding force", "fr": "Force de blocage"},
    "rap_5_inv_t": {"en": "What this implies for investment",
                    "fr": "Ce que cela implique pour l'investissement"},
    "rap_5_inv_x": {
        "en": "Two rankings, two different questions. One says where the "
              "shortfall weighs most in the index; the other says where the "
              "shortfall holds back the rest of the system. Neither is a "
              "recommendation: the arbitration stays with the funder.",
        "fr": "Deux classements, deux questions différentes. L'un dit où le "
              "retard pèse le plus lourd dans l'indice, l'autre dit où le "
              "retard retient le reste du système. Aucun des deux n'est une "
              "recommandation : l'arbitrage reste au bailleur."},
    "rap_5_inv_ref": {"en": "By weight in the framework",
                      "fr": "Au sens du référentiel"},
    "rap_5_inv_sys": {"en": "By position in the system",
                      "fr": "Au sens du système"},
    "rap_5_inv_deux": {
        "en": "These appear in both rankings: {v}. That is the only case "
              "where the budget argument and the systemic argument point to "
              "the same place.",
        "fr": "Ces variables figurent dans les deux classements : {v}. C'est "
              "le seul cas où l'argument budgétaire et l'argument systémique "
              "désignent le même endroit."},
    "rap_5_inv_sans": {
        "en": "No variable appears in both rankings. What weighs most in the "
              "index is not what holds back the system, and choosing one "
              "means choosing which of the two arguments to follow.",
        "fr": "Aucune variable ne figure dans les deux classements. Ce qui "
              "pèse le plus dans l'indice n'est pas ce qui retient le "
              "système, et choisir revient à décider lequel des deux "
              "arguments on suit."},
    "rap_5_pour": {"en": "Where is it blocked, and for whom?",
                   "fr": "Où est-ce que ça bloque, et pour qui ?"},
    "rap_5_cible_x": {
        "en": "Ranking recomputed with the levels measured for {c}. What each "
              "variable carries through the system comes from the causal "
              "model and does not change; the distance still to travel does.",
        "fr": "Classement refait avec les niveaux mesurés pour {c}. Ce que "
              "chaque variable fait circuler dans le système vient du modèle "
              "causal et ne change pas ; la distance qui reste, si."},
    "rap_5_leg": {
        "en": "Binding force is the propagated effect of one extra point on "
              "this variable, multiplied by the distance still to travel to "
              "the top of the scale. A variable already near ten cannot be a "
              "bottleneck however central it is.",
        "fr": "La force de blocage est l'effet propagé d'un point de plus sur "
              "cette variable, multiplié par la distance qui la sépare encore "
              "du haut de l'échelle. Une variable déjà proche de dix ne peut "
              "pas être un blocage, si centrale soit-elle."},
    "rap_5_haut_t": {"en": "High leverage, already high",
                    "fr": "Fort levier, déjà haut"},
    "rap_5_haut_x": {
        "en": "These variables carry a lot of the system but are already near "
              "the top of the scale. They are worth protecting, not "
              "improving.",
        "fr": "Ces variables portent beaucoup du système mais sont déjà "
              "hautes. Elles sont à protéger, pas à améliorer."},

    # ---------------------------------------------------------- chapitre 6
    "rap_6_t": {"en": "What your funding turned into",
               "fr": "Ce que votre financement a produit"},
    "rap_6_avant": {"en": "Before", "fr": "Avant"},
    "rap_6_avant_x": {
        "en": "Interventions were designed on fragmented information: "
              "administrative counts, project reports, and the experience of "
              "the teams on the ground.",
        "fr": "Les interventions se concevaient sur une information "
              "fragmentée : des comptages administratifs, des rapports de "
              "projet, et l'expérience des équipes de terrain."},
    "rap_6_pendant": {"en": "During", "fr": "Pendant"},
    "rap_6_pendant_x": {
        "en": "A systematic survey collected information directly from "
              "households, in their own words, on {q} questions, and scored "
              "it against a framework that holds the dimensions together "
              "instead of listing them.",
        "fr": "Une enquête systématique a recueilli l'information directement "
              "auprès des ménages, dans leurs propres mots, sur {q} "
              "questions, et l'a notée contre un référentiel qui tient les "
              "dimensions ensemble au lieu de les énumérer."},
    "rap_6_apres": {"en": "After", "fr": "Après"},
    "rap_6_apres_x": {
        "en": "There is now a base that separates landscapes, sections and "
              "social groups, names the binding constraints, and can be "
              "measured again the same way to see what moved.",
        "fr": "Il existe désormais une base qui sépare les paysages, les "
              "sections et les groupes sociaux, nomme les contraintes "
              "bloquantes, et peut être remesurée de la même façon pour voir "
              "ce qui a bougé."},
    "rap_6_phrase": {
        "en": "The value of the funding is not only in the activities "
              "carried out. It is in the knowledge produced, and in the "
              "capacity created to aim the next investment better.",
        "fr": "La valeur du financement ne tient pas seulement aux activités "
              "réalisées. Elle tient à la connaissance produite, et à la "
              "capacité créée pour mieux viser l'investissement suivant."},
    "rap_6_boucle_t": {"en": "A learning loop, not a one-off report",
                      "fr": "Une boucle d'apprentissage, pas un rapport ponctuel"},
    "rap_6_boucle_x": {
        "en": "Structured this way, the survey does not expire with the "
              "project. Each new measurement enters the same frame and "
              "becomes comparable with the last.",
        "fr": "Structurée ainsi, l'enquête ne périme pas avec le projet. "
              "Chaque nouvelle mesure entre dans le même cadre et devient "
              "comparable à la précédente."},
    "rap_6_b1": {"en": "Field data", "fr": "Données de terrain"},
    "rap_6_b2": {"en": "Diagnosis", "fr": "Diagnostic"},
    "rap_6_b3": {"en": "Constraints identified", "fr": "Blocages identifiés"},
    "rap_6_b4": {"en": "Targeted intervention", "fr": "Intervention ciblée"},
    "rap_6_b5": {"en": "New measurement", "fr": "Nouvelle mesure"},
    "rap_6_b6": {"en": "Comparison over time", "fr": "Comparaison dans le temps"},
    "rap_6_b7": {"en": "Learning", "fr": "Apprentissage"},
    "rap_6_meth_t": {"en": "Why these results can be trusted",
                    "fr": "Pourquoi ces résultats sont crédibles"},
    "rap_6_meth_couv": {"en": "Coverage", "fr": "Couverture"},
    "rap_6_meth_ech": {"en": "Sampling", "fr": "Échantillonnage"},
    "rap_6_meth_ech_x": {
        "en": "Households were drawn at random within strata, from a "
              "georeferenced building base rather than an administrative "
              "register, so that settlements missing from official lists are "
              "covered too.",
        "fr": "Les ménages ont été tirés au sort dans des strates, à partir "
              "d'une base de bâtiments géoréférencés plutôt que d'un registre "
              "administratif, pour que les habitats absents des listes "
              "officielles soient couverts aussi."},
    "rap_6_meth_cal": {"en": "How an indicator becomes a score",
                      "fr": "Comment un indicateur devient un score"},
    "rap_6_meth_cal_x": {
        "en": "Each indicator carries its own published scale from 0 to 10 "
              "and its own weight. An indicator that could not be computed "
              "leaves the denominator instead of counting as zero, which is "
              "why the number of scored indicators is stated everywhere "
              "beside the index.",
        "fr": "Chaque indicateur porte son barème publié de 0 à 10 et sa "
              "propre pondération. Un indicateur non calculé sort du "
              "dénominateur au lieu de compter zéro, et c'est pourquoi le "
              "nombre d'indicateurs scorés est rappelé partout à côté de "
              "l'indice."},
    "rap_6_meth_lim": {"en": "Limits, stated", "fr": "Limites, énoncées"},
    "rap_6_meth_lim_x": {
        "en": "One survey wave, so no trend on household indicators. {a} of "
              "the {t} framework indicators are not scored yet, including "
              "the whole seventh dimension. Two sections returned no "
              "community organisation profile. The causal model is an expert "
              "construct, not an estimation on this survey.",
        "fr": "Une seule vague d'enquête, donc aucune tendance sur les "
              "indicateurs ménages. {a} des {t} indicateurs du référentiel ne "
              "sont pas encore scorés, dont toute la septième dimension. Deux "
              "sections n'ont rendu aucune fiche d'organisation "
              "communautaire. Le modèle causal est une construction "
              "d'expert, pas une estimation sur cette enquête."},
    "rap_6_meth_qual": {"en": "Quantitative and qualitative",
                       "fr": "Quantitatif et qualitatif"},
    "rap_6_meth_qual_x": {
        "en": "The household questionnaire carries the quantitative side. "
              "The community organisation profiles carry the qualitative "
              "side: who holds the territory together, with what partners, "
              "and for how long.",
        "fr": "Le questionnaire ménage porte le versant quantitatif. Les "
              "fiches d'organisations communautaires portent le versant "
              "qualitatif : qui tient le territoire, avec quels partenaires, "
              "et depuis combien de temps."},
    "rap_6_suite_t": {"en": "What this base can be used for next",
                     "fr": "À quoi cette base servira ensuite"},

    "rap_1_p1": {
        "en": "Between {h} ({hv}) and {b} ({bv}) there are {d} points of "
              "spread, measured on the {n} indicators available for all ten "
              "sections.",
        "fr": "Entre {h} ({hv}) et {b} ({bv}), il y a {d} points d'écart, "
              "mesurés sur les {n} indicateurs disponibles pour les dix "
              "sections."},
    "rap_1_p2": {
        "en": "On the {n} indicators that actually vary between social "
              "groups, {a} reaches {av} while {b} stands at {bv}, a gap of "
              "{d} points.",
        "fr": "Sur les {n} indicateurs qui varient réellement entre groupes "
              "sociaux, {a} atteint {av} quand {b} reste à {bv}, soit {d} "
              "points d'écart."},
    "rap_1_p3": {
        "en": "The two landscapes do not hold up alike: {a} at {av}, {b} at "
              "{bv}.",
        "fr": "Les deux paysages ne tiennent pas pareil : {a} à {av}, {b} à "
              "{bv}."},
    "rap_1_bloc_x": {
        "en": "{a}, {b} and {c} combine a low level with a central position "
              "in the causal model. That combination, not the low score "
              "alone, is what makes a constraint binding.",
        "fr": "{a}, {b} et {c} cumulent un niveau bas et une position "
              "centrale dans le modèle causal. C'est cette combinaison, et "
              "non le score bas seul, qui fait une contrainte bloquante."},
    "rap_1_suite_x": {
        "en": "The base now separates landscapes, sections and social "
              "groups, and names what caps the rest. The next investment can "
              "be aimed at the binding constraints rather than spread evenly, "
              "and measured again in the same frame.",
        "fr": "La base sépare désormais les paysages, les sections et les "
              "groupes sociaux, et nomme ce qui plafonne le reste. "
              "L'investissement suivant peut viser les contraintes "
              "bloquantes plutôt que s'étaler uniformément, et se remesurer "
              "dans le même cadre."},
    "rap_2_rep_x": {"en": "households × questions, upper bound",
                   "fr": "ménages × questions, borne haute"},
    "rap_2_ech_sec": {"en": "households per section",
                     "fr": "ménages par section"},
    "rap_3_t1": {"en": "Intervention", "fr": "Intervention"},
    "rap_3_t2": {"en": "Indicator", "fr": "Indicateur"},
    "rap_3_t3": {"en": "Result", "fr": "Résultat"},
    "rap_3_m1": {"en": "Intervention", "fr": "Intervention"},
    "rap_3_m2": {"en": "Available resources", "fr": "Ressources disponibles"},
    "rap_3_m3": {"en": "Household capacity", "fr": "Capacités du ménage"},
    "rap_3_m4": {"en": "Market access", "fr": "Accès au marché"},
    "rap_3_m5": {"en": "Access to services", "fr": "Accès aux services"},
    "rap_3_m6": {"en": "Productive assets", "fr": "Actifs productifs"},
    "rap_3_m7": {"en": "Social capital", "fr": "Capital social"},
    "rap_3_m8": {"en": "Ability to save", "fr": "Capacité d'épargne"},
    "rap_3_m9": {"en": "Income diversification",
                "fr": "Diversification des revenus"},
    "rap_3_m10": {"en": "Absorbing a shock", "fr": "Absorption d'un choc"},
    "rap_3_m11": {"en": "Resilience trajectory",
                 "fr": "Trajectoire de résilience"},
    "rap_4_ens": {"en": "All respondents", "fr": "Ensemble des répondants"},
    "rap_4_ecart_x": {
        "en": "**Largest gap: {d}**, {v} points, in favour of {a}.",
        "fr": "**Écart le plus grand : {d}**, {v} points, en faveur de {a}."},
    "rap_4_grp_obs": {
        "en": "On these {n} indicators, {a} reaches {av} and {b} stands at "
              "{bv}: a gap of {d} points out of ten.",
        "fr": "Sur ces {n} indicateurs, {a} atteint {av} quand {b} reste à "
              "{bv} : {d} points d'écart sur dix."},
    "rap_4_grp_int": {
        "en": "A gap between groups is not in itself a targeting failure, "
              "since groups do not start from the same place. What it does "
              "show is where an intervention has to work harder to reach the "
              "same result, and which group would be left behind by an "
              "effort spread evenly.",
        "fr": "Un écart entre groupes n'est pas en soi un défaut de ciblage, "
              "puisque les groupes ne partent pas du même point. Il montre "
              "en revanche où une intervention devra fournir davantage pour "
              "obtenir le même résultat, et quel groupe serait laissé en "
              "arrière par un effort réparti uniformément."},
    "rap_5_obs": {
        "en": "{a} sits at {av} out of ten, {b} at {bv}, {c} at {cv}, and "
              "the causal model routes a large share of what circulates in "
              "the system through them.",
        "fr": "{a} est à {av} sur dix, {b} à {bv}, {c} à {cv}, et le modèle "
              "causal fait passer par elles une large part de ce qui circule "
              "dans le système."},
    "rap_5_int": {
        "en": "These variables are not merely low, they are low **and** "
              "central. Raising a variable that is already high, or one that "
              "is low but peripheral, produces an effect that stops where it "
              "started. Raising {a} or {b} moves things that were not "
              "targeted.",
        "fr": "Ces variables ne sont pas seulement basses : elles sont "
              "basses **et** centrales. Relever une variable déjà haute, ou "
              "une variable basse mais périphérique, produit un effet qui "
              "s'arrête là où il est né. Relever {a} ou {b} déplace des "
              "choses qui n'étaient pas visées."},
    "rap_5_imp": {
        "en": "An intervention acting on a single link, without lifting {a} "
              "or {b}, will see its benefit capped by what did not move. The "
              "model does not say which intervention to choose. It says "
              "which ones cap each other, and therefore which should travel "
              "together: {a}, {b} and {c} are candidates for a combined "
              "package rather than three separate projects.",
        "fr": "Une intervention qui n'agit que sur un maillon, sans lever "
              "{a} ni {b}, verra son bénéfice plafonné par ce qui n'a pas "
              "bougé. Le modèle ne dit pas quelle intervention choisir. Il "
              "dit lesquelles se plafonnent mutuellement, donc lesquelles "
              "devraient voyager ensemble : {a}, {b} et {c} sont candidates "
              "à un ensemble combiné plutôt qu'à trois projets séparés."},
    "rap_6_u1": {"en": "compare landscapes and sections on the same frame",
                "fr": "comparer paysages et sections dans le même cadre"},
    "rap_6_u2": {"en": "identify the groups left behind",
                "fr": "repérer les groupes laissés en arrière"},
    "rap_6_u3": {"en": "target interventions on the binding constraints",
                "fr": "cibler les interventions sur les contraintes bloquantes"},
    "rap_6_u4": {"en": "measure again the same way and see what moved",
                "fr": "remesurer de la même façon et voir ce qui a bougé"},
    "rap_6_u5": {"en": "compare intervention strategies on their modelled "
                      "effect before committing funds",
                "fr": "comparer des stratégies d'intervention sur leur effet "
                      "modélisé avant d'engager les fonds"},
    "rap_absent_page": {"en": "Survey files are missing.",
                       "fr": "Les fichiers d'enquête sont absents."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _gras(t):
    """`**gras**` en `<b>` : le markdown n'est pas interprété dans du HTML."""
    out, parts = [], _e(t).split("**")
    for i, p in enumerate(parts):
        out.append(f"<b>{p}</b>" if i % 2 else p)
    return "".join(out).replace("\n\n", "</p><p class='rd-x'>")


def _f(v, dec=2, signe=False):
    if v is None:
        return "—"
    s = f"{v:+.{dec}f}" if signe else f"{v:.{dec}f}"
    return s.replace(".", ",") if i18n.get_lang() == "fr" else s


def _n(v):
    return f"{int(v):,}".replace(",", " ")


# ---------------------------------------------------------------- les données
@st.cache_data(show_spinner=False)
def _mesures(lang):
    """Tout ce que la page affiche, relu dans les fichiers.

    UNE SEULE FONCTION, ET ELLE EST CACHÉE. Les chapitres partagent presque
    tous les mêmes agrégats : les recalculer par chapitre ferait diverger deux
    chiffres censés être le même. La langue est un argument parce que les
    libellés en dépendent, et qu'une fonction cachée qui lirait la langue à
    l'intérieur figerait à jamais la première affichée.
    """
    p = os.path.join(DATA, "resultats.json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        res = json.load(f)
    res = res["indicateurs"] if isinstance(res, dict) and "indicateurs" in res \
        else res
    scores = [r for r in res
              if (r.get("scores_corriges") or {}).get("Total") is not None]

    def moy(lignes, cible):
        num = den = 0.0
        for r in lignes:
            s = (r.get("scores_corriges") or {}).get(cible)
            if s is None:
                continue
            w = r.get("ponderation") or 1
            num += w * float(s)
            den += w
        return round(num / den, 2) if den else None

    # --- LES EFFECTIFS : LA VALEUR LA PLUS FRÉQUENTE, PAS LA PLUS GRANDE.
    # Un `n` d'indicateur ne compte pas toujours des ménages. « Enregistrement
    # des naissances à l'état civil » porte n = 2 700 parce qu'il compte des
    # enfants ; prendre le maximum faisait afficher 2 700 ménages enquêtés, ce
    # qui est faux. La valeur modale est le vrai effectif de l'échantillon, et
    # elle se vérifie : les modes des sous-groupes se somment exactement au
    # mode du Total (595 femmes + 616 hommes = 1 211 ; littoral + montagne
    # aussi ; les trois catégories de pauvreté aussi). Les valeurs plus hautes
    # sont des unités d'observation différentes, pas un échantillon plus large.
    compte = {}
    for r in res:
        for k, v in (r.get("n") or {}).items():
            if v:
                compte.setdefault(k, {})
                compte[k][int(v)] = compte[k].get(int(v), 0) + 1
    # à fréquence égale, on retient la valeur la plus haute
    n = {k: max(c.items(), key=lambda x: (x[1], x[0]))[0]
         for k, c in compte.items()}

    # --- l'index des questions, pour le volume de réponses
    q_total = None
    pq = os.path.join(DATA, "croisement_index.json")
    if os.path.exists(pq):
        with open(pq, encoding="utf-8") as f:
            idx = json.load(f)
        q_total = len(idx.get("questions") or [])

    # --- les organisations communautaires
    ocb_n, ocb_sections, ocb_absentes = None, None, []
    po = os.path.join(DATA, "ocb.json")
    if os.path.exists(po):
        with open(po, encoding="utf-8") as f:
            o = json.load(f)
        fiches = o.get("fiches") or []
        ocb_n = len(fiches)
        ocb_sections = len({x.get("section") for x in fiches if x.get("section")})
        ocb_absentes = o.get("sections_sans_donnee") or []

    # --- par dimension, pour chaque découpage
    par_dim = {}
    for cle, nom in DIMS:
        lignes = [r for r in scores if r.get("dimension") == nom]
        par_dim[cle] = {"n": len(lignes),
                        "total": sum(1 for r in res if r.get("dimension") == nom),
                        "scores": {}}
        for cible in ["Total"] + PAYSAGES + SECTIONS + GROUPES_SOC:
            par_dim[cle]["scores"][cible] = moy(lignes, cible)

    # --- LA BASE COMMUNE AUX GROUPES SOCIAUX.
    # Un indicateur satellitaire porte la même valeur pour les femmes et pour
    # les hommes d'une même section : le garder dans une comparaison de groupes
    # ajoute du poids identique des deux côtés et rapproche artificiellement
    # les deux profils. On ne garde que ce qui varie réellement.
    base_grp = []
    for r in scores:
        sc = r.get("scores_corriges") or {}
        vals = [sc.get(g) for g in GROUPES_SOC]
        if any(v is None for v in vals):
            continue
        if len({round(float(v), 3) for v in vals}) > 1:
            base_grp.append(r)
    groupes = {g: moy(base_grp, g) for g in GROUPES_SOC}
    groupes["Total"] = moy(base_grp, "Total")

    # --- la base commune aux dix sections
    base_sec = [r for r in scores
                if all((r.get("scores_corriges") or {}).get(s) is not None
                       for s in SECTIONS)]
    sections = {s: moy(base_sec, s) for s in SECTIONS}

    paysages = {p_: moy(scores, p_) for p_ in PAYSAGES}

    # --- LES BLOCAGES, PAR LE MODÈLE CAUSAL, ET POUR CHAQUE DÉCOUPAGE.
    # Ce que porte une variable — la somme des effets absolus qu'un point de
    # plus chez elle produit dans tout le système — ne dépend que de la
    # structure du graphe : elle est la même pour un littoral et pour une
    # montagne. Ce qui change d'un territoire à l'autre, c'est le niveau de
    # départ, donc la distance qui reste à parcourir. On calcule donc la
    # portée une seule fois, et on la repondère par le niveau de la cible
    # demandée. C'est ce qui permet à la page de répondre « où ça bloque »
    # pour l'ensemble, pour un paysage, pour une section ou pour un groupe,
    # sans jamais recalculer autre chose que ce qui a réellement bougé.
    blocages, proteger, portes = [], [], []
    try:
        g = M.charger()
        par_ligne = {r["ligne"]: r for r in res if r.get("ligne") is not None}
        noms = {x["id"]: (x.get(lang) or x.get("fr"), x.get("dim", ""))
                for x in g["noeuds"]}
        lignes_n = {x["id"]: x.get("ligne") for x in g["noeuds"]}
        etats = {c: M.etat_courant(g, par_ligne, c)
                 for c in ["Total"] + PAYSAGES + SECTIONS + GROUPES_SOC}
        for nid, sc in etats["Total"].items():
            eff = M.propager(g, {nid: 1.0})
            porte = sum(abs(v) for v in eff.values())
            portes.append(
                {"id": nid, "nom": noms[nid][0], "dim": noms[nid][1],
                 "ligne": lignes_n.get(nid), "porte": porte,
                 "scores": {c: e.get(nid) for c, e in etats.items()}})
            if sc is None:
                continue
            force = porte * (10.0 - float(sc)) / 10.0
            ligne = {"id": nid, "nom": noms[nid][0], "dim": noms[nid][1],
                     "score": float(sc), "porte": round(porte, 2),
                     "force": round(force, 2)}
            (blocages if sc < 7 else proteger).append(ligne)
        blocages.sort(key=lambda x: -x["force"])
        proteger.sort(key=lambda x: -x["porte"])
    except Exception:
        blocages, proteger, portes = [], [], []

    # --- les trois constats les plus coûteux, au sens du référentiel
    couteux = sorted(
        ({"nom": (r.get("indicateur_fr") if lang == "fr"
                  else r.get("indicateur")) or r.get("indicateur"),
          "ligne": r.get("ligne"),
          "score": float((r.get("scores_corriges") or {})["Total"]),
          "poids": float(r.get("ponderation") or 1),
          "dim": next((c for c, nm in DIMS if nm == r.get("dimension")), ""),
          "cout": float(r.get("ponderation") or 1)
                  * (10 - float((r.get("scores_corriges") or {})["Total"]))}
         for r in scores),
        key=lambda x: -x["cout"])

    return {
        "indice": moy(scores, "Total"),
        "n_scores": len(scores),
        "n_total": len(res),
        "n_dims": len(DIMS),
        "n_dims_scorees": sum(1 for c, _ in DIMS if par_dim[c]["n"]),
        "n": n,
        "menages": n.get("Total"),
        "sections_n": {s: n.get(s) for s in SECTIONS},
        "questions": q_total,
        "ocb_n": ocb_n, "ocb_sections": ocb_sections,
        "ocb_absentes": ocb_absentes,
        "decoupages": 1 + len(PAYSAGES) + len(SECTIONS) + len(GROUPES_SOC),
        "par_dim": par_dim,
        "base_grp": len(base_grp), "groupes": groupes,
        "base_sec": len(base_sec), "sections": sections,
        "paysages": paysages,
        "blocages": blocages, "proteger": proteger, "portes": portes,
        "couteux": couteux,
    }


# ---------------------------------------------------------------- le style
STYLE = """
<style>
  /* UN RAPPORT, PAS UN TABLEAU DE BORD. Peu de traits, beaucoup de blanc, une
     seule couleur d'accent, et des chiffres qui ont le droit d'être grands.
     Les encadrés narratifs portent un filet à gauche dont la couleur dit le
     REGISTRE : gris pour la donnée, bleu pour l'interprétation, vert pour
     l'implication. C'est la seule chose que la couleur code dans cette page. */
  .rd-cha  { display:flex; gap:0; margin:14px 0 4px; flex-wrap:wrap;
             border-bottom:1px solid #e6ecf4; }
  .rd-h    { font-size:27px; font-weight:700; color:#101728;
             letter-spacing:-.025em; margin:22px 0 4px; line-height:1.15; }
  .rd-h2   { font-size:18px; font-weight:700; color:#101728;
             letter-spacing:-.015em; margin:26px 0 6px; }
  .rd-x    { font-size:16px; color:#3c4761; line-height:1.7; margin:0 0 10px;
             max-width:78ch; text-align:left !important; }
  .rd-lab  { font-size:11px; letter-spacing:.1em; text-transform:uppercase;
             color:#8a93a5; font-weight:700; margin:26px 0 8px; }
  .rd-reg  { border-left:3px solid #c8d0dc; padding:2px 0 2px 15px;
             margin:14px 0; }
  .rd-reg .t { font-size:10.5px; letter-spacing:.1em; text-transform:uppercase;
               font-weight:700; color:#8a93a5; margin-bottom:3px; }
  .rd-reg p  { font-size:15.5px; color:#3c4761; line-height:1.65; margin:0;
               max-width:78ch; text-align:left !important; }
  .rd-obs  { border-left-color:#9aa4b5; }
  .rd-int  { border-left-color:#2166ac; }
  .rd-int .t { color:#2166ac; }
  .rd-imp  { border-left-color:#1a8a4f; }
  .rd-imp .t { color:#1a8a4f; }
  .rd-ex   { border:1px solid #e8dfc8; background:#fdfbf4; border-radius:12px;
             padding:16px 20px; margin:14px 0; }
  .rd-ex .t{ font-size:10.5px; letter-spacing:.1em; text-transform:uppercase;
             font-weight:700; color:#8a6d1f; margin-bottom:6px; }
  .rd-ex p { font-size:15.5px; color:#3c4761; line-height:1.7; margin:0 0 9px;
             max-width:76ch; text-align:left !important; }
  /* les grands chiffres du terrain */
  .rd-g    { display:grid; grid-template-columns:repeat(4,1fr); gap:0;
             border-top:1px solid #e6ecf4; margin-top:14px; }
  .rd-k    { padding:16px 18px 17px; border-bottom:1px solid #e6ecf4;
             border-left:1px solid #e6ecf4; }
  .rd-k:nth-child(4n+1) { border-left:none; padding-left:0; }
  .rd-k b  { display:block; font-size:32px; font-weight:700; color:#101728;
             line-height:1; letter-spacing:-.03em;
             font-variant-numeric:tabular-nums; }
  .rd-k span { display:block; font-size:13px; color:#3c4761; margin-top:6px; }
  .rd-k em { display:block; font-style:normal; font-size:11.5px;
             color:#8a93a5; margin-top:2px; }
  /* la chaîne des deux approches */
  .rd-ch   { display:flex; flex-wrap:wrap; gap:6px; align-items:center;
             margin:8px 0 4px; }
  .rd-ch i { font-style:normal; color:#c8d0dc; font-size:13px; }
  .rd-ch b { font-weight:600; font-size:13px; padding:5px 11px;
             border:1px solid #e3eaf3; border-radius:999px; color:#3c4761;
             background:#fff; white-space:nowrap; }
  .rd-ch b.on { border-color:#1c6349; color:#0f4f3a; background:#f2f8f5; }
  /* les blocages */
  .rd-b    { display:grid; grid-template-columns:1fr 92px 92px 132px; gap:12px;
             align-items:center; padding:10px 0;
             border-top:1px solid #eef2f7; font-size:14px; }
  .rd-b:first-child { border-top:none; }
  /* la variante resserrée, pour une rangée logée dans une demi-colonne */
  .rd-b.cp { grid-template-columns:1fr 96px 58px; }
  .rd-b.cp .ba { grid-column:2 / span 1 !important; }
  .rd-b .nm{ color:#101728; font-weight:600; }
  .rd-b .vv{ font-variant-numeric:tabular-nums; text-align:right;
             font-weight:700; }
  .rd-b .ba{ height:9px; border-radius:5px; background:#eef2f7;
             overflow:hidden; }
  .rd-b .ba i { display:block; height:100%; border-radius:5px; }
  .rd-tri  { display:grid; grid-template-columns:repeat(3,1fr); gap:0;
             border-top:1px solid #e6ecf4; border-bottom:1px solid #e6ecf4;
             margin:16px 0; }
  .rd-t    { padding:16px 20px 18px; border-left:1px solid #e6ecf4; }
  .rd-t:first-child { border-left:none; padding-left:0; }
  .rd-t b  { display:block; font-size:11px; letter-spacing:.1em;
             text-transform:uppercase; color:#8a93a5; margin-bottom:7px; }
  .rd-t p  { font-size:15px; color:#3c4761; line-height:1.6; margin:0;
             text-align:left !important; }
  /* LE SOMMAIRE : SIX BOUTONS DE MÊME HAUTEUR.
     Les titres de chapitre n'ont pas la même longueur, donc les uns tiennent
     sur une ligne et les autres sur deux : sans hauteur commune, la rangée
     ressemble à un escalier. On la cale, et on aligne le texte en haut pour
     que les numéros se lisent sur une même ligne. */
  div[class*="st-key-rap_pas_"] button { min-height:66px; align-items:flex-start;
             padding-top:12px; text-align:left; }
  div[class*="st-key-rap_pas_"] button p { text-align:left !important;
             font-size:14px; line-height:1.3; }
  @media (max-width:820px){
    .rd-g{grid-template-columns:repeat(2,1fr)}
    .rd-k:nth-child(4n+1){border-left:1px solid #e6ecf4;padding-left:18px}
    .rd-k:nth-child(2n+1){border-left:none;padding-left:0}
    .rd-tri{grid-template-columns:1fr}
    .rd-t{border-left:none;border-top:1px solid #e6ecf4;padding-left:0}
    .rd-t:first-child{border-top:none}
    .rd-b{grid-template-columns:1fr 70px 70px}
  }
</style>
"""


def _registre(cle_t, texte, classe):
    st.markdown(f'<div class="rd-reg {classe}"><div class="t">'
                f'{_e(T(cle_t))}</div><p>{_gras(texte)}</p></div>',
                unsafe_allow_html=True)


def _obs(t):
    _registre("rap_obs", t, "rd-obs")


def _interp(t):
    _registre("rap_int", t, "rd-int")


def _implic(t):
    _registre("rap_imp", t, "rd-imp")


def _chiffres(cases):
    """Une grille de grands chiffres. `cases` : (valeur, libellé, sous-titre)."""
    st.markdown('<div class="rd-g">' + "".join(
        f'<div class="rd-k"><b>{_e(v)}</b><span>{_e(lab)}</span>'
        + (f'<em>{_e(sous)}</em>' if sous else "") + '</div>'
        for v, lab, sous in cases) + '</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------- le radar
def _lib(c):
    """Le nom lisible d'un découpage publié, dans la langue courante."""
    if c == "Total":
        return T("rap_4_ens")
    if c in PAYSAGES:
        return filtres.libelle_paysage(c)
    if c in GROUPES_SOC:
        return filtres.libelle_groupe(c)
    return c


def _radar(m, a, b, lib_a, lib_b, larg=560):
    """Six axes, deux profils. Rien d'autre.

    UN RADAR DIT UNE FORME, PAS UN CLASSEMENT. Deux territoires de même
    moyenne peuvent être plats partout ou effondrés sur un seul axe, et ces
    deux situations n'appellent pas la même réponse. C'est pour cette
    différence-là que la figure est ici, et c'est pourquoi elle porte deux
    profils plutôt qu'un.
    """
    axes = [(c, COURT[c][0 if i18n.get_lang() == "en" else 1])
            for c, _ in DIMS if m["par_dim"][c]["n"]]
    k = len(axes)
    if k < 3:
        return ""
    import math
    cx = cy = larg / 2
    r = larg / 2 - 62
    parts = []
    for frac in (0.25, 0.5, 0.75, 1.0):
        pts = " ".join(
            f'{cx + r * frac * math.sin(2 * math.pi * i / k):.1f},'
            f'{cy - r * frac * math.cos(2 * math.pi * i / k):.1f}'
            for i in range(k))
        parts.append(f'<polygon points="{pts}" fill="none" stroke="#eef2f7" '
                     f'stroke-width="1"/>')
    for i, (cle, nom) in enumerate(axes):
        x = cx + r * math.sin(2 * math.pi * i / k)
        y = cy - r * math.cos(2 * math.pi * i / k)
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" '
                     f'stroke="#e6ecf4" stroke-width="1"/>')
        ex = cx + (r + 24) * math.sin(2 * math.pi * i / k)
        ey = cy - (r + 24) * math.cos(2 * math.pi * i / k)
        anc = "middle" if abs(ex - cx) < 12 else ("start" if ex > cx else "end")
        parts.append(f'<text x="{ex:.1f}" y="{ey + 4:.1f}" text-anchor="{anc}" '
                     f'font-size="11.5" font-weight="600" fill="{ENCRE2}">'
                     f'{_e(nom)}</text>')

    def trace(cible, coul, remplir):
        pts, marques = [], []
        for i, (cle, _) in enumerate(axes):
            v = m["par_dim"][cle]["scores"].get(cible)
            f = (float(v) / 10.0) if v is not None else 0.0
            x = cx + r * f * math.sin(2 * math.pi * i / k)
            y = cy - r * f * math.cos(2 * math.pi * i / k)
            pts.append(f"{x:.1f},{y:.1f}")
            marques.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" '
                           f'fill="{coul}"><title>{_e(COURT[cle][1])} : '
                           f'{_f(v, 1)}</title></circle>')
        return (f'<polygon points="{" ".join(pts)}" fill="{coul}" '
                f'fill-opacity="{0.14 if remplir else 0}" stroke="{coul}" '
                f'stroke-width="2" stroke-linejoin="round"/>'
                + "".join(marques))

    parts.append(trace(a, BLEU, True))
    if b and b != a:
        parts.append(trace(b, AMBRE, False))
    # LES NOMS D'AXES SORTENT DU CARRÉ, ET C'EST NORMAL : ils sont posés
    # au-delà du dernier anneau, ancrés vers l'extérieur. Un viewBox calé sur
    # le carré du radar les coupait net à droite et à gauche ; on lui donne
    # donc une marge horizontale, sans toucher au dessin lui-même.
    mx = 92
    return (f'<svg viewBox="{-mx} 0 {larg + 2 * mx} {larg}" width="100%" '
            f'style="max-width:{larg + 2 * mx}px;display:block;margin:0 auto" '
            f'font-family="Inter,system-ui,sans-serif">' + "".join(parts)
            + '</svg>')


def _barres(paires, coul=None, maxi=10.0, unite="", serre=False):
    """Un rang de barres horizontales, une par entité, avec sa valeur.

    `serre` sert quand la rangée vit dans une demi-colonne : la grille large
    n'y laisse plus assez de place au nom, qui se casse alors sur trois
    lignes. La variante resserre les colonnes chiffrées au lieu de rogner le
    libellé, parce qu'un nom d'indicateur illisible ne se remplace pas.
    """
    lignes = []
    cl = "rd-b cp" if serre else "rd-b"
    for nom, val in paires:
        f = 0 if val is None else max(min(float(val) / maxi, 1), 0)
        c = coul or (ROUGE if (val or 0) < 3.5
                     else (AMBRE if (val or 0) < 5 else VERT))
        lignes.append(
            f'<div class="{cl}"><div class="nm">{_e(nom)}</div>'
            f'<div class="ba" style="grid-column:2 / span 2">'
            f'<i style="width:{f * 100:.1f}%;background:{c}"></i></div>'
            f'<div class="vv" style="color:{c}">{_f(val, 2)}{_e(unite)}</div>'
            f'</div>')
    st.markdown("".join(lignes), unsafe_allow_html=True)


# ------------------------------------------------------------- chapitre 1
def _ch1(m):
    st.markdown(f'<div class="rd-h">{_e(T("rap_1_t"))}</div>'
                f'<p class="rd-x">{_e(T("rap_1_x"))}</p>',
                unsafe_allow_html=True)

    _chiffres([
        (_n(m["menages"]), T("rap_2_men"), None),
        (str(len(SECTIONS)), T("rap_2_sec"), T("rap_2_dep") + " : 2"),
        (str(m["n_scores"]), T("rap_2_sco"),
         f'{m["n_total"]} {T("rap_2_ind")}'),
        (_f(m["indice"]), T("rap_4_ind"), None),
    ])

    st.markdown(f'<div class="rd-lab">{_e(T("rap_1_fait"))}</div>',
                unsafe_allow_html=True)
    _obs(T("rap_1_fait_x", t=m["n_total"], d=m["n_dims"]))

    # --- trois constats, tous calculés
    st.markdown(f'<div class="rd-lab">{_e(T("rap_1_trois"))}</div>',
                unsafe_allow_html=True)
    ecart_g = None
    vals = {g: v for g, v in m["groupes"].items()
            if g != "Total" and v is not None}
    if vals:
        gmin = min(vals, key=vals.get)
        gmax = max(vals, key=vals.get)
        ecart_g = (gmin, vals[gmin], gmax, vals[gmax])
    secs = {s: v for s, v in m["sections"].items() if v is not None}
    smin = min(secs, key=secs.get) if secs else None
    smax = max(secs, key=secs.get) if secs else None
    pay = {p_: v for p_, v in m["paysages"].items() if v is not None}

    puces = []
    if smin and smax:
        puces.append(T("rap_1_p1", h=smax, hv=_f(secs[smax]),
                       b=smin, bv=_f(secs[smin]),
                       d=_f(secs[smax] - secs[smin]), n=m["base_sec"]))
    if ecart_g:
        puces.append(T("rap_1_p2", a=filtres.libelle_groupe(ecart_g[2]),
                       av=_f(ecart_g[3]),
                       b=filtres.libelle_groupe(ecart_g[0]),
                       bv=_f(ecart_g[1]),
                       d=_f(ecart_g[3] - ecart_g[1]), n=m["base_grp"]))
    if len(pay) == 2:
        puces.append(T("rap_1_p3", a=T("po_3_littoral"), av=_f(pay["Littoral"]),
                       b=T("po_3_montagne"), bv=_f(pay["Montagne"])))
    for p_ in puces:
        _obs(p_)

    # --- trois blocages
    if m["blocages"]:
        st.markdown(f'<div class="rd-lab">{_e(T("rap_1_bloc"))}</div>',
                    unsafe_allow_html=True)
        _barres([(b["nom"], b["force"]) for b in m["blocages"][:3]],
                coul=ROUGE, maxi=max(b["force"] for b in m["blocages"]) or 1)
        _interp(T("rap_1_bloc_x",
                  a=m["blocages"][0]["nom"], b=m["blocages"][1]["nom"],
                  c=m["blocages"][2]["nom"]))

    st.markdown(f'<div class="rd-lab">{_e(T("rap_1_suite"))}</div>',
                unsafe_allow_html=True)
    _implic(T("rap_1_suite_x"))


# ------------------------------------------------------------- chapitre 2
def _ch2(m):
    st.markdown(f'<div class="rd-h">{_e(T("rap_2_t"))}</div>'
                f'<p class="rd-x">{_e(T("rap_2_x"))}</p>',
                unsafe_allow_html=True)

    q = m["questions"]
    reponses = (m["menages"] * q) if (q and m["menages"]) else None
    _chiffres([
        (_n(m["menages"]), T("rap_2_men"), None),
        (str(len(SECTIONS)), T("rap_2_sec"), None),
        ("2", T("rap_2_dep"), "Sud, Grand'Anse"),
        ("2", T("rap_2_pay"), f'{T("po_3_littoral")}, {T("po_3_montagne")}'),
        (str(q) if q else T("rap_absent"), T("rap_2_que"), None),
        (_n(reponses) if reponses else T("rap_absent"), T("rap_2_rep"),
         T("rap_2_rep_x") if reponses else None),
        (str(m["ocb_n"]) if m["ocb_n"] else T("rap_absent"), T("rap_2_ocb"),
         None),
        (str(m["n_total"]), T("rap_2_ind"),
         f'{m["n_scores"]} {T("rap_2_sco")}'),
        (str(m["n_dims"]), T("rap_2_dim"),
         f'{m["n_dims_scorees"]} {T("rap_2_sco")}'),
        (str(m["decoupages"]), T("rap_2_dec"), None),
        (str(len(GROUPES_SOC)), T("rap_2_grp"), None),
        (f'{min(v for v in m["sections_n"].values() if v)}'
         f'–{max(v for v in m["sections_n"].values() if v)}',
         T("rap_2_ech_sec"), None),
    ])

    if q and m["menages"]:
        _obs(T("rap_2_phr", t=m["n_total"], n=_n(m["menages"]),
               s=len(SECTIONS), q=q, r=_n(reponses)))

    if m["ocb_n"]:
        _obs(T("rap_2_ocb_x", n=m["ocb_n"], s=m["ocb_sections"],
               v=", ".join(m["ocb_absentes"]) or T("rap_absent")))

    st.markdown(f'<div class="rd-lab">{_e(T("rap_2_couv"))}</div>',
                unsafe_allow_html=True)
    eff = {s: v for s, v in m["sections_n"].items() if v}
    _obs(T("rap_2_couv_x", mn=min(eff.values()), mx=max(eff.values())))
    _barres([(s, v) for s, v in eff.items()], coul=BLEU,
            maxi=max(eff.values()), unite="")


# ------------------------------------------------------------- chapitre 3
def _ch3(m):
    st.markdown(f'<div class="rd-h">{_e(T("rap_3_t"))}</div>'
                f'<p class="rd-x">{_e(T("rap_3_x"))}</p>',
                unsafe_allow_html=True)

    st.markdown(
        f'<div class="rd-ex"><div class="t">{_e(T("rap_exemple"))}</div>'
        f'<div class="rd-h2" style="margin:0 0 8px">{_e(T("rap_3_hist_t"))}</div>'
        f'<p>{_gras(T("rap_3_hist"))}</p></div>', unsafe_allow_html=True)

    _interp(T("rap_3_quest"))

    st.markdown(f'<div class="rd-h2">{_e(T("rap_3_deux_t"))}</div>',
                unsafe_allow_html=True)

    st.markdown(f'<div class="rd-lab" style="margin-top:12px">'
                f'{_e(T("rap_3_trad"))}</div>', unsafe_allow_html=True)
    st.markdown('<div class="rd-ch">' + '<i>›</i>'.join(
        f'<b>{_e(T(k))}</b>' for k in ("rap_3_t1", "rap_3_t2", "rap_3_t3"))
        + '</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="rd-x">{_e(T("rap_3_trad_x"))}</p>',
                unsafe_allow_html=True)

    st.markdown(f'<div class="rd-lab">{_e(T("rap_3_pays"))}</div>',
                unsafe_allow_html=True)
    maillons = ("rap_3_m1", "rap_3_m2", "rap_3_m3", "rap_3_m4", "rap_3_m5",
                "rap_3_m6", "rap_3_m7", "rap_3_m8", "rap_3_m9", "rap_3_m10",
                "rap_3_m11")
    st.markdown('<div class="rd-ch">' + '<i>›</i>'.join(
        f'<b class="on">{_e(T(k))}</b>' for k in maillons)
        + '</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="rd-x">{_e(T("rap_3_pays_x"))}</p>',
                unsafe_allow_html=True)

    _interp(T("rap_3_concl"))


# ------------------------------------------------------------- chapitre 4
def _ch4(m):
    st.markdown(f'<div class="rd-h">{_e(T("rap_4_t"))}</div>',
                unsafe_allow_html=True)

    _chiffres([
        (_f(m["indice"]), T("rap_4_ind"),
         T("rap_4_ind_x", n=m["n_scores"])),
        (_f(m["paysages"].get("Littoral")), T("po_3_littoral"),
         f'{_n(m["n"].get("Littoral", 0))} {T("rap_2_men")}'),
        (_f(m["paysages"].get("Montagne")), T("po_3_montagne"),
         f'{_n(m["n"].get("Montagne", 0))} {T("rap_2_men")}'),
        (str(m["n_dims_scorees"]) + " / " + str(m["n_dims"]),
         T("rap_2_dim"), T("rap_2_sco")),
    ])
    _obs(T("rap_4_pay_avert"))

    # ---- le radar comparatif
    st.markdown(f'<div class="rd-h2">{_e(T("rap_4_radar_t"))}</div>'
                f'<p class="rd-x">{_e(T("rap_4_radar_x"))}</p>',
                unsafe_allow_html=True)

    choix = (["Total"] + PAYSAGES + SECTIONS + GROUPES_SOC)
    lib = _lib

    ga, gb = st.columns(2)
    with ga:
        a = st.selectbox(T("rap_4_a"), choix, index=choix.index("Littoral"),
                         format_func=lib, key=f"rap_a_{i18n.get_lang()}")
    with gb:
        b = st.selectbox(T("rap_4_b"), choix, index=choix.index("Montagne"),
                         format_func=lib, key=f"rap_b_{i18n.get_lang()}")

    gauche, droite = st.columns([1.15, 1], gap="large")
    with gauche:
        st.markdown(_radar(m, a, b, lib(a), lib(b)), unsafe_allow_html=True)
        st.markdown(
            f'<div style="display:flex;gap:18px;justify-content:center;'
            f'font-size:13px;color:{ENCRE2};margin-top:2px">'
            f'<span><b style="color:{BLEU}">■</b> {_e(lib(a))}</span>'
            + (f'<span><b style="color:{AMBRE}">■</b> {_e(lib(b))}</span>'
               if b != a else "") + '</div>', unsafe_allow_html=True)
    with droite:
        lignes, ecarts = [], []
        for cle, _ in DIMS:
            if not m["par_dim"][cle]["n"]:
                continue
            va = m["par_dim"][cle]["scores"].get(a)
            vb = m["par_dim"][cle]["scores"].get(b)
            lignes.append((cle, va, vb))
            if va is not None and vb is not None:
                ecarts.append((cle, vb - va))
        for cle, va, vb in lignes:
            d = (vb - va) if (va is not None and vb is not None) else None
            coul = GRIS if d is None or abs(d) < 0.05 else (
                VERT if d > 0 else ROUGE)
            st.markdown(
                f'<div style="display:grid;grid-template-columns:1fr 52px 52px '
                f'62px;gap:8px;align-items:center;padding:7px 0;'
                f'border-top:1px solid #eef2f7;font-size:13.5px">'
                f'<span style="color:{ENCRE}">{_e(T(cle))}</span>'
                f'<b style="color:{BLEU};text-align:right;'
                f'font-variant-numeric:tabular-nums">{_f(va, 1)}</b>'
                f'<b style="color:{AMBRE};text-align:right;'
                f'font-variant-numeric:tabular-nums">'
                f'{_f(vb, 1) if b != a else ""}</b>'
                f'<b style="color:{coul};text-align:right;'
                f'font-variant-numeric:tabular-nums">'
                f'{_f(d, 2, True) if (d is not None and b != a) else ""}</b>'
                f'</div>', unsafe_allow_html=True)
        if ecarts and b != a:
            cle, d = max(ecarts, key=lambda x: abs(x[1]))
            st.markdown(f'<p class="rd-x" style="font-size:13.5px;'
                        f'margin-top:10px">{_gras(T("rap_4_ecart_x", d=T(cle), v=_f(abs(d), 2), a=lib(a) if d < 0 else lib(b)))}</p>',
                        unsafe_allow_html=True)
    st.caption(T("rap_4_dim7"))

    # ---- les groupes
    st.markdown(f'<div class="rd-h2">{_e(T("rap_4_grp_t"))}</div>'
                f'<p class="rd-x">{_e(T("rap_4_grp_x", n=m["base_grp"]))}</p>',
                unsafe_allow_html=True)
    paires = [(filtres.libelle_groupe(g), m["groupes"].get(g))
              for g in GROUPES_SOC if m["groupes"].get(g) is not None]
    _barres(sorted(paires, key=lambda x: -(x[1] or 0)))
    vals = {g: v for g, v in m["groupes"].items()
            if g != "Total" and v is not None}
    if vals:
        gmin, gmax = min(vals, key=vals.get), max(vals, key=vals.get)
        _obs(T("rap_4_grp_obs", a=filtres.libelle_groupe(gmax),
               av=_f(vals[gmax]), b=filtres.libelle_groupe(gmin),
               bv=_f(vals[gmin]), d=_f(vals[gmax] - vals[gmin]),
               n=m["base_grp"]))
        _interp(T("rap_4_grp_int"))

    # ---- les sections
    st.markdown(f'<div class="rd-h2">{_e(T("rap_4_sec_t"))}</div>'
                f'<p class="rd-x">{_e(T("rap_4_sec_x", n=m["base_sec"]))}</p>',
                unsafe_allow_html=True)
    _barres(sorted(((s, v) for s, v in m["sections"].items() if v is not None),
                   key=lambda x: -x[1]))

    # ---- le temps
    st.markdown(f'<div class="rd-h2">{_e(T("rap_4_temps_t"))}</div>',
                unsafe_allow_html=True)
    st.markdown(f'<div class="rd-reg rd-obs"><div class="t">'
                f'{_e(T("rap_absent"))}</div><p>{_e(T("rap_4_temps_x"))}</p>'
                f'</div>', unsafe_allow_html=True)


# ------------------------------------------------------------- chapitre 5
def _ch5(m):
    st.markdown(f'<div class="rd-h">{_e(T("rap_5_t"))}</div>'
                f'<p class="rd-x">{_gras(T("rap_5_x"))}</p>',
                unsafe_allow_html=True)

    if not m["blocages"] or not m["portes"]:
        st.info(T("rap_absent"))
        return

    # ---- OÙ EST-CE QUE ÇA BLOQUE, ET POUR QUI ?
    # La question n'a pas la même réponse partout : une variable centrale déjà
    # haute dans un paysage peut être au plancher dans l'autre. Le lecteur
    # choisit donc le découpage, et le classement se refait sous ses yeux avec
    # les scores de cette population-là. Rien n'est réestimé : seule la
    # distance au haut de l'échelle change.
    choix = ["Total"] + PAYSAGES + SECTIONS + GROUPES_SOC
    cible = st.selectbox(T("rap_5_pour"), choix, index=0, format_func=_lib,
                         key=f"rap_5_cible_{i18n.get_lang()}")

    rangs = []
    for x in m["portes"]:
        sc = x["scores"].get(cible)
        if sc is None:
            continue
        rangs.append({**x, "score": float(sc),
                      "force": round(x["porte"] * (10.0 - float(sc)) / 10.0, 2)})
    if not rangs:
        st.info(T("rap_absent"))
        return
    hauts = sorted([x for x in rangs if x["score"] >= 7],
                   key=lambda x: -x["porte"])
    rangs = sorted([x for x in rangs if x["score"] < 7],
                   key=lambda x: -x["force"])
    if not rangs:
        st.info(T("rap_absent"))
        return
    if cible != "Total":
        st.caption(T("rap_5_cible_x", c=_lib(cible)))

    st.markdown(
        f'<div class="rd-b" style="border:none;padding-bottom:4px">'
        f'<span style="font-size:11px;letter-spacing:.08em;'
        f'text-transform:uppercase;color:{ENCRE3};font-weight:700"></span>'
        f'<span style="font-size:10.5px;letter-spacing:.06em;'
        f'text-transform:uppercase;color:{ENCRE3};font-weight:700;'
        f'text-align:right">{_e(T("rap_5_col1"))}</span>'
        f'<span style="font-size:10.5px;letter-spacing:.06em;'
        f'text-transform:uppercase;color:{ENCRE3};font-weight:700;'
        f'text-align:right">{_e(T("rap_5_col2"))}</span>'
        f'<span style="font-size:10.5px;letter-spacing:.06em;'
        f'text-transform:uppercase;color:{ENCRE3};font-weight:700;'
        f'text-align:right">{_e(T("rap_5_col3"))}</span></div>',
        unsafe_allow_html=True)

    fmax = max(b["force"] for b in rangs) or 1
    for b in rangs[:10]:
        st.markdown(
            f'<div class="rd-b">'
            f'<span class="nm">{_e(b["nom"])}</span>'
            f'<span class="vv" style="color:{ROUGE if b["score"] < 3.5 else (AMBRE if b["score"] < 5 else ENCRE2)}">'
            f'{_f(b["score"], 1)}</span>'
            f'<span class="vv" style="color:{ENCRE2}">{_f(b["porte"], 2)}</span>'
            f'<span style="display:flex;align-items:center;gap:8px">'
            f'<span class="ba" style="flex:1"><i style="width:'
            f'{b["force"] / fmax * 100:.0f}%;background:{ROUGE}"></i></span>'
            f'<b style="font-variant-numeric:tabular-nums;font-size:13px;'
            f'color:{ROUGE};min-width:34px;text-align:right">'
            f'{_f(b["force"], 2)}</b></span></div>', unsafe_allow_html=True)
    st.caption(T("rap_5_leg"))

    a, b2, c = (x["nom"] for x in rangs[:3])
    _obs(T("rap_5_obs", a=a, av=_f(rangs[0]["score"], 1),
           b=b2, bv=_f(rangs[1]["score"], 1),
           c=c, cv=_f(rangs[2]["score"], 1)))
    _interp(T("rap_5_int", a=a, b=b2))
    _implic(T("rap_5_imp", a=a, b=b2, c=c))

    if hauts:
        st.markdown(f'<div class="rd-h2">{_e(T("rap_5_haut_t"))}</div>'
                    f'<p class="rd-x">{_e(T("rap_5_haut_x"))}</p>',
                    unsafe_allow_html=True)
        _barres([(x["nom"], x["porte"]) for x in hauts[:4]],
                coul=BLEU, maxi=max(x["porte"] for x in hauts) or 1)

    # ---- CE QUE CELA IMPLIQUE POUR L'INVESTISSEMENT.
    # Deux classements répondent à deux questions différentes, et les
    # confondre est l'erreur la plus commune d'un arbitrage budgétaire.
    #   · le référentiel dit où le retard pèse le plus lourd dans l'indice :
    #     pondération publiée × distance au haut de l'échelle ;
    #   · le modèle causal dit où le retard bloque le reste du système.
    # Une variable qui figure dans les deux listes n'est pas « deux fois
    # prioritaire » : elle est le seul cas où l'argument budgétaire et
    # l'argument systémique désignent le même endroit. La page les affiche
    # côte à côte et nomme l'intersection, sans la transformer en
    # recommandation : c'est un constat, l'arbitrage reste au bailleur.
    if m["couteux"]:
        st.markdown(f'<div class="rd-h2">{_e(T("rap_5_inv_t"))}</div>'
                    f'<p class="rd-x">{_e(T("rap_5_inv_x"))}</p>',
                    unsafe_allow_html=True)
        gauche, droite = st.columns(2, gap="large")
        with gauche:
            st.markdown(f'<div class="rd-lab">{_e(T("rap_5_inv_ref"))}</div>',
                        unsafe_allow_html=True)
            _barres([(x["nom"], x["cout"]) for x in m["couteux"][:5]],
                    coul=AMBRE, serre=True,
                    maxi=max(x["cout"] for x in m["couteux"]) or 1)
        with droite:
            st.markdown(f'<div class="rd-lab">{_e(T("rap_5_inv_sys"))}</div>',
                        unsafe_allow_html=True)
            _barres([(x["nom"], x["force"]) for x in rangs[:5]],
                    coul=ROUGE, maxi=fmax, serre=True)

        lc = {x["ligne"] for x in m["couteux"][:12] if x.get("ligne")}
        deux = [x["nom"] for x in rangs[:12]
                if x.get("ligne") and x["ligne"] in lc]
        _implic(T("rap_5_inv_deux", v=", ".join(deux[:4])) if deux
                else T("rap_5_inv_sans"))


# ------------------------------------------------------------- chapitre 6
def _ch6(m):
    st.markdown(f'<div class="rd-h">{_e(T("rap_6_t"))}</div>',
                unsafe_allow_html=True)

    st.markdown(
        '<div class="rd-tri">'
        + f'<div class="rd-t"><b>{_e(T("rap_6_avant"))}</b>'
          f'<p>{_e(T("rap_6_avant_x"))}</p></div>'
        + f'<div class="rd-t"><b>{_e(T("rap_6_pendant"))}</b>'
          f'<p>{_e(T("rap_6_pendant_x", q=m["questions"] or "—"))}</p></div>'
        + f'<div class="rd-t"><b>{_e(T("rap_6_apres"))}</b>'
          f'<p>{_e(T("rap_6_apres_x"))}</p></div>'
        + '</div>', unsafe_allow_html=True)

    _interp(T("rap_6_phrase"))

    # ---- la boucle d'apprentissage
    st.markdown(f'<div class="rd-h2">{_e(T("rap_6_boucle_t"))}</div>'
                f'<p class="rd-x">{_e(T("rap_6_boucle_x"))}</p>',
                unsafe_allow_html=True)
    etapes = ("rap_6_b1", "rap_6_b2", "rap_6_b3", "rap_6_b4", "rap_6_b5",
              "rap_6_b6", "rap_6_b7")
    st.markdown('<div class="rd-ch">' + '<i>›</i>'.join(
        f'<b class="on">{_e(T(k))}</b>' for k in etapes)
        + '<i>↻</i></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="rd-lab">{_e(T("rap_6_suite_t"))}</div>',
                unsafe_allow_html=True)
    for k in ("rap_6_u1", "rap_6_u2", "rap_6_u3", "rap_6_u4", "rap_6_u5"):
        # LA PUCE EST UN ÉLÉMENT, PAS UN CARACTÈRE COLLÉ AU TEXTE. Écrite
        # « · texte » dans une chaîne, l'espace se perd au rendu et la ligne
        # se lit « ·comparer ». On la pose donc dans sa propre colonne.
        st.markdown(f'<p class="rd-x" style="margin:0 0 6px;display:flex;'
                    f'gap:9px;align-items:baseline">'
                    f'<span style="color:{ENCRE3}">·</span>'
                    f'<span>{_e(T(k))}</span></p>', unsafe_allow_html=True)

    # ---- la méthodologie
    st.markdown(f'<div class="rd-h2">{_e(T("rap_6_meth_t"))}</div>',
                unsafe_allow_html=True)
    eff = {s: v for s, v in m["sections_n"].items() if v}
    _obs(T("rap_2_couv_x", mn=min(eff.values()), mx=max(eff.values())))
    st.markdown(f'<div class="rd-lab">{_e(T("rap_6_meth_ech"))}</div>',
                unsafe_allow_html=True)
    _obs(T("rap_6_meth_ech_x"))
    st.markdown(f'<div class="rd-lab">{_e(T("rap_6_meth_cal"))}</div>',
                unsafe_allow_html=True)
    _obs(T("rap_6_meth_cal_x"))
    st.markdown(f'<div class="rd-lab">{_e(T("rap_6_meth_qual"))}</div>',
                unsafe_allow_html=True)
    _obs(T("rap_6_meth_qual_x"))
    st.markdown(f'<div class="rd-lab">{_e(T("rap_6_meth_lim"))}</div>',
                unsafe_allow_html=True)
    _obs(T("rap_6_meth_lim_x", a=m["n_total"] - m["n_scores"], t=m["n_total"]))


# ------------------------------------------------------------------ la page
def _poser(n):
    st.session_state["rap_chapitre"] = n


def render(entete=True):
    st.markdown(STYLE, unsafe_allow_html=True)
    m = _mesures(i18n.get_lang())
    if not m:
        st.info(T("rap_absent_page"))
        return

    if entete:
        st.markdown(
            f'<h2 style="font-size:29px;font-weight:700;color:{ENCRE};'
            f'letter-spacing:-.025em;margin:2px 0 0;line-height:1.15">'
            f'{_e(T("rap_titre"))}</h2>'
            f'<p style="font-size:12.5px;color:{ENCRE3};letter-spacing:.06em;'
            f'text-transform:uppercase;margin:4px 0 0;font-weight:600">'
            f'{_e(T("rap_sous"))}</p>', unsafe_allow_html=True)

    st.session_state.setdefault("rap_chapitre", 1)
    n = st.session_state["rap_chapitre"]
    if n not in range(1, len(CHAPITRES) + 1):
        n = 1

    cols = st.columns(len(CHAPITRES))
    for i, (col, cle) in enumerate(zip(cols, CHAPITRES), 1):
        with col:
            st.button(f"{i} · {T(cle)}", key=f"rap_pas_{i}",
                      on_click=_poser, args=(i,), use_container_width=True,
                      type="primary" if i == n else "secondary")

    with st.container(border=True):
        (_ch1, _ch2, _ch3, _ch4, _ch5, _ch6)[n - 1](m)

    g, _mid, d = st.columns([1.6, 4, 1.6])
    with g:
        if n > 1:
            st.button("← " + T("po_precedent"), key="rap_prec",
                      on_click=_poser, args=(n - 1,),
                      use_container_width=True)
    with d:
        if n < len(CHAPITRES):
            st.button(T("po_suivant") + " →", key="rap_suiv",
                      on_click=_poser, args=(n + 1,),
                      use_container_width=True, type="primary")
