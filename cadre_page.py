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
    "cad_sous_titre": {
        "en": "What the index measures, how it is built, and what it cannot say",
        "fr": "Ce que l'indice mesure, comment il est construit, et ce qu'il "
              "ne peut pas dire"},

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
    "cad_uma": {
        "en": "APRI measures the resilience of a landscape, understood as a "
              "complex adaptive system.",
        "fr": "APRI mesure la résilience d'un paysage, compris comme un "
              "système complexe adaptatif."},

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
    "cad_e4": {"en": "Weighted mean of the scored indicators, uncomputed "
                     "ones are excluded from the denominator",
               "fr": "Moyenne pondérée des indicateurs scorés, les non "
                     "calculés sont exclus du dénominateur"},

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
    "cad_c4": {"en": "From measures to scores", "fr": "De la mesure au score"},
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
  .cad-a-n  { font-size:56px; font-weight:200; line-height:1;
              color:#1b5e3a; letter-spacing:.01em;
              font-variant-numeric:tabular-nums; flex:0 0 auto; }
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

  /* --- la phrase qui ouvre le premier onglet ------------------------------
     LE `!important` EST NÉCESSAIRE : la feuille de l'application fixe
     14,5 px et la justification à tout paragraphe du contenu, avec une
     spécificité supérieure à celle d'une classe. */
  p.cad-uma { font-size:19px !important; line-height:1.6 !important;
              font-family:Georgia,"Times New Roman",serif; font-style:italic;
              font-weight:400; color:#26364a !important;
              margin:18px 0 4px !important; max-width:62ch;
              border-left:3px solid #1a6b52; padding-left:22px;
              text-align:left !important; }

  /* --- la barre des sept onglets, en numéros ------------------------------
     ELLE PORTAIT SEPT TITRES ENTIERS ET FAISAIT CENT TRENTE PIXELS DE HAUT,
     plus que le contenu de certains onglets. Elle ne porte plus que des
     numéros reliés par un filet, et le titre court de l'onglet regardé
     s'inscrit sous son numéro. Le titre entier n'est pas perdu : c'est
     l'intitulé du bloc, juste en dessous.

     LE FILET EST TRACÉ PAR CHAQUE CASE, VERS LA DROITE, sauf la dernière.
     C'est la seule façon d'obtenir un trait qui s'étire entre deux numéros
     sans connaître à l'avance la largeur disponible : le pseudo-élément part
     après le numéro et va jusqu'au bord de sa propre case.

     LA PLACE DU LIBELLÉ EST RÉSERVÉE PAR LA BARRE, PAS PAR LA CASE. Le
     libellé est en position absolue — s'il poussait la hauteur de sa case,
     la rangée entière se décalerait au moindre changement d'onglet. */
  /* LA BARRE DOIT S'ÉTIRER, ET RIEN NE L'Y OBLIGE. Les cases ne contiennent
     plus que deux chiffres : la largeur naturelle du groupe est celle de
     quatorze caractères, et un `width:100%` calculé sur ce parent-là ne
     donne rien. Chaque enveloppe que Streamlit interpose est donc forcée à
     la pleine largeur. */
  div[class*="st-key-cad_nav"],
  div[class*="st-key-cad_nav"] div[data-testid="stElementContainer"],
  div[class*="st-key-cad_nav"] div[data-testid="stRadio"] {
      width:100% !important; }
  div[class*="st-key-cad_nav"] div[role="radiogroup"] {
      display:flex !important; flex-wrap:nowrap !important; gap:0 !important;
      width:100% !important; align-items:flex-start; padding:2px 0 22px; }
  div[class*="st-key-cad_nav"] div[role="radiogroup"] > label {
      flex:1 1 0 !important; min-width:0 !important; margin:0 !important;
      background:none !important; border:0 !important; padding:0 !important;
      position:relative; cursor:pointer; }
  div[class*="st-key-cad_nav"] div[role="radiogroup"]
      > label > div > div > div:first-child { display:none !important; }
  div[class*="st-key-cad_nav"] div[role="radiogroup"] > label > div > div {
      gap:0 !important; width:100% !important; }
  div[class*="st-key-cad_nav"] div[role="radiogroup"] > label p {
      font-size:13px !important; font-weight:600 !important;
      color:#a7b0be !important; margin:0 !important;
      text-align:left !important; letter-spacing:.02em;
      transition:color .12s ease; }
  div[class*="st-key-cad_nav"] div[role="radiogroup"] > label:hover p {
      color:#3c4761 !important; }
  div[class*="st-key-cad_nav"] div[role="radiogroup"] > label::before {
      content:""; position:absolute; left:30px; right:10px; top:9px;
      height:1px; background:#d6e2da; }
  div[class*="st-key-cad_nav"] div[role="radiogroup"]
      > label:last-of-type::before { display:none; }
  div[class*="st-key-cad_nav"] div[role="radiogroup"]
      > label:has(input:checked) p {
      font-size:19px !important; font-weight:600 !important;
      color:#1a6b52 !important; line-height:1 !important;
      margin:-4px 0 0 !important; }
  /* Le titre court, écrit par `_css_rail`, n'apparaît que sous l'actif. */
  div[class*="st-key-cad_nav"] div[role="radiogroup"] > label::after {
      position:absolute; left:0; top:22px; font-size:10.5px; font-weight:700;
      color:#1a6b52; letter-spacing:.02em; white-space:nowrap; }
  @media (max-width: 760px) {
    div[class*="st-key-cad_nav"] div[role="radiogroup"] {
        flex-wrap:wrap !important; }
    div[class*="st-key-cad_nav"] div[role="radiogroup"] > label {
        flex:0 0 14%; }
  }

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
                '<div style="align-self:center;color:#c3ccda;font-size:17.5px;'
                'flex:0 0 auto;padding:0 2px">›</div>')
        blocs.append(
            f'<div style="flex:1 1 190px;min-width:175px;background:#fff;'
            f'border:1px solid {BORD};border-radius:13px;padding:13px 15px">'
            f'<div style="font-size:11px;letter-spacing:.06em;'
            f'text-transform:uppercase;font-weight:700;color:#2166ac">'
            f'{_e(T(cle + "_t"))}</div>'
            f'<div style="font-size:12.5px;color:{ENCRE2};line-height:1.5;'
            f'margin-top:5px">{_e(T(cle, **kw))}</div></div>')
    return ('<div style="display:flex;gap:6px;flex-wrap:wrap;'
            'align-items:stretch">' + "".join(blocs) + '</div>')


def _attributs():
    """Les trois attributs, en trois colonnes numérotées.

    C'EST LE SEUL CONTENU DU PREMIER ONGLET, et il porte donc toute la
    définition. Les quatre cartouches d'ouverture et le schéma d'ensemble qui
    l'entouraient ont été retirés : ils répondaient à quatre questions à la
    fois, et aucune ne disait en une ligne ce qu'APRI mesure. La phrase le dit
    maintenant, au-dessus ; ces trois colonnes la déplient, et rien d'autre.

    LE NUMÉRO EST GROS ET MAIGRE, ET C'EST VOULU. Il donne l'ordre de lecture
    sans peser autant que le mot qu'il précède — anticiper vient avant
    absorber, qui vient avant s'adapter, parce que c'est l'ordre du temps.
    Le trait qui part du pictogramme et s'achève sur un point ne dit rien de
    plus : il tient la colonne et l'ouvre vers la droite.
    """
    cols = []
    for i, (k, ic) in enumerate((("cad_a1", "loupe"), ("cad_a2", "bouclier"),
                                 ("cad_a3", "rafraichir")), start=1):
        cols.append(
            '<div class="cad-a">'
            '<div class="cad-a-h">'
            f'<span class="cad-a-n">{i:02d}</span>'
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


def _css_rail():
    """Le libellé court de l'onglet actif, posé sous son numéro.

    STREAMLIT NE MET QU'UN LIBELLÉ PAR CASE, et c'est le numéro. Le titre
    court est donc écrit en CSS, dans un pseudo-élément que seule la case
    cochée affiche — une règle par rang, générée ici pour que le texte suive
    la langue.
    """
    b = 'div[class*="st-key-cad_nav"] div[role="radiogroup"] > label'
    r = ["<style>"]
    for i, code in enumerate(VUES, start=1):
        r.append(f'{b}:nth-of-type({i}):has(input:checked)::after '
                 f'{{ content:"{_txt_css(T(_COURT[code]))}"; }}')
    r.append("</style>")
    return "".join(r)


def render(doc_complet=None):
    stats = _stats()
    st.markdown(STYLE, unsafe_allow_html=True)

    st.markdown(
        f'<h2 style="font-size:21.5px;font-weight:700;color:{ENCRE};'
        f'letter-spacing:-.02em;margin:2px 0 0">{T("cad_titre")}</h2>'
        f'<p style="font-size:11.5px;color:{ENCRE3};letter-spacing:.06em;'
        f'text-transform:uppercase;margin:2px 0 10px;font-weight:600">'
        f'{T("cad_sous_titre")}</p>', unsafe_allow_html=True)

    if not stats:
        st.info(T("e_absent"))
        return

    st.markdown(_css_rail(), unsafe_allow_html=True)
    with st.container(key="cad_nav"):
        vue = st.radio(
            "cad", VUES, horizontal=True, label_visibility="collapsed",
            key="cad_vue",
            format_func=lambda c: f"{VUES.index(c) + 1:02d}")

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
    st.markdown(f'<p class="cad-uma">{_e(T("cad_uma"))}</p>',
                unsafe_allow_html=True)
    st.markdown(_titre("cad_aaa", marge=32) + _attributs(),
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
    """La chaîne de calcul, puis ce qu'elle ne permet pas de dire.

    LES LIMITES SUIVENT LA CHAÎNE, ET C'EST VOULU. Elles ne se comprennent
    qu'une fois le calcul connu : la circularité d'un indice composite ne
    veut rien dire tant qu'on n'a pas vu qu'il agrège ses propres variables
    explicatives. Elles avaient disparu de l'affichage à la refonte
    précédente ; les publier plus loin que le calcul serait les enterrer une
    seconde fois.
    """
    st.markdown(_titre("cad_chaine", marge=4)
                + _chaine(stats["poids_total"]), unsafe_allow_html=True)
    st.markdown(
        _titre("cad_limites", marge=30)
        + '<div class="cad-grille">'
        # UNE SEULE TEINTE, ET ELLE EST GRISE. Quatre couleurs sur quatre
        # limites laisseraient croire à quatre natures de limite ; elles sont
        # quatre façons de dire la même chose — l'indice cadre, il ne prédit
        # pas.
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
