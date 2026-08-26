"""Le moteur du graphe causal : propagation, boucles, indice global.

SÉPARÉ DE L'AFFICHAGE À DESSEIN. Ce fichier ne dessine rien ; il calcule. On
peut donc le relire, le contester et le corriger sans toucher à une seule
balise, et c'est le seul endroit où se trouve la mécanique du modèle.

CE QUE FAIT LA PROPAGATION, EXACTEMENT

Le graphe est une matrice A où A[v, u] = signe × force de la relation u → v.
On pose une variation initiale sur un nœud, puis on la propage par vagues :

    vague₀ = variation initiale
    vague_{k+1} = A · vague_k
    effet total = Σ vagues  =  (I − A)⁻¹ · vague₀ − vague₀

C'est la série de Neumann, et elle est RÉSOLUE EXACTEMENT plutôt que tronquée.
La version tronquée à douze vagues convenait tant que le rayon spectral valait
0,746 ; l'ajout du sous-système de la déforestation l'a porté à 0,98, et il
restait alors 81 % de l'effet non distribué — des chiffres faux, sans que rien
ne le signale. Une inversion de matrice 45×45 coûte moins qu'un battement de
cil et donne la somme complète.

Le rayon spectral reste surveillé pour deux raisons : au-delà de 1 la série n'a
plus de somme et le modèle s'emballe ; au-dessus de 0,9 il est très bouclé —
une petite hausse de force suffirait à le faire basculer. `diagnostic()` rend
les deux, et l'interface les affiche.

Le passage par les boucles est donc pris en compte sans réglage particulier :
une boucle renforçante amplifie la vague suivante, une boucle équilibrante la
retourne. C'est tout le mécanisme, et il tient en trois lignes.

CE QUE CE MOTEUR N'EST PAS

Ce n'est pas un modèle estimé sur les données. Les forces sont posées par le
cadre IRLA et par la littérature, pas ajustées sur l'enquête. Les résultats
sont des scénarios exploratoires : ils disent ce que le modèle implique, pas ce
que le terrain fera. Les associations réellement observées entre sections
communales sont calculées à part, portées par le champ `rho` de chaque arête,
et ne servent JAMAIS au calcul — elles sont là pour être comparées au modèle,
y compris quand elles le contredisent.
"""

import json
import os

import numpy as np

APP_DIR = os.path.dirname(os.path.abspath(__file__))
GRAPHE = os.path.join(APP_DIR, "data", "graphe_causal.json")

SECTIONS = ["Anse à Drick", "Barbois", "Dumont", "Débouchette", "Mouline",
            "Quentin", "Beaulieu", "Blactote", "Dalmette", "Trichet"]

# Longueur maximale d'une boucle énumérée, et plafond du nombre de boucles.
# Sans bornes, l'énumération des cycles d'un graphe dense explose
# combinatoirement et bloque la page.
#
# LA BORNE A ÉTÉ RELEVÉE APRÈS VÉRIFICATION. À dix, elle coupait six boucles
# de onze à treize nœuds — l'algorithme était juste, la borne était trop
# basse, et la liste sortait incomplète sans le dire. Comparée à une
# implémentation de référence, l'énumération retrouve maintenant les
# trente-huit boucles du modèle, sans doublon ni cycle en trop.
#
# `boucles()` porte un drapeau `tronque` : le jour où quelqu'un densifiera le
# modèle au point de heurter ces bornes, la liste le dira au lieu de mentir
# par omission.
BOUCLE_MAX = 16
BOUCLES_MAX = 2000

SEUIL_NUL = 0.05     # sous 0,05 point sur 10, l'effet est dit négligeable
TENDU = 0.90         # au-delà, le système est fortement bouclé : on le dit

# MISE À L'ÉCHELLE DES FORCES — un choix de modélisation, pas un réglage.
#
# Les forces posées à dire d'expert donnent au graphe complet un rayon spectral
# de 0,98 : le système est presque à la limite de l'emballement, et une hausse
# de deux points sur un levier en produisait quinze sur un autre. Sur une
# échelle qui s'arrête à dix, c'est absurde.
#
# Ce n'est pas un défaut d'affichage. Un diagramme de boucles causales est un
# outil QUALITATIF : ses flèches disent un sens et un ordre de grandeur relatif,
# jamais une amplitude mesurée. On ramène donc l'ensemble des forces par un
# facteur unique, de sorte que le rayon spectral vaille RAYON_CIBLE.
#
# Ce que cela préserve : le signe de chaque effet, la structure des boucles,
# et l'ORDRE des indicateurs les plus touchés — tout ce que l'outil prétend
# montrer. Ce que cela abandonne : l'idée qu'un effet simulé serait un nombre
# de points crédible. Il ne l'était pas.
RAYON_CIBLE = 0.60


# ---------------------------------------------------------------------------
# LE MODÈLE VOYAGE AVEC LE CODE.
#
# Le graphe vivait dans `data/graphe_causal.json` seul. Le fichier n'est pas
# arrivé en ligne, et la page est tombée sur un FileNotFoundError — le même
# scénario que le dictionnaire de traduction, pour la même raison : les
# fichiers sont poussés à la main, un par un, et en oublier un est normal.
#
# Le modèle par défaut est donc écrit ici, en clair. Un fichier
# `data/graphe_causal.json` reste lu EN PRIORITÉ s'il existe : c'est ce qui
# permet de corriger le modèle en atelier, avec les acteurs, sans toucher au
# code. Mais son absence ne casse plus rien.
#
# Chaque arête porte son signe, sa force, son niveau de justification et sa
# source en clair — c'est fait pour être relu et contesté ligne à ligne.
# ---------------------------------------------------------------------------
GRAPHE_DEFAUT = {
    "noeuds": [
        {"id": "eau", "ligne": 4, "dim": "dim1", "fr": "Accès à l'eau de boisson", "en": "Access to drinking water"},
        {"id": "assain", "ligne": 3, "dim": "dim1", "fr": "Assainissement géré en sécurité", "en": "Safely managed sanitation"},
        {"id": "elec", "ligne": 5, "dim": "dim1", "fr": "Accès à l'électricité", "en": "Access to electricity"},
        {"id": "cuisson", "ligne": 6, "dim": "dim1", "fr": "Combustibles propres de cuisson", "en": "Clean cooking fuels"},
        {"id": "sante_acces", "ligne": 15, "dim": "dim1", "fr": "Centre de santé à moins de 30 min", "en": "Health facility within 30 min"},
        {"id": "ecole", "ligne": 16, "dim": "dim1", "fr": "École primaire à moins de 30 min", "en": "Primary school within 30 min"},
        {"id": "abris", "ligne": 14, "dim": "dim1", "fr": "Abris d'urgence opérationnels", "en": "Operational emergency shelters"},
        {"id": "logement", "ligne": 10, "dim": "dim1", "fr": "Qualité structurelle du logement", "en": "Housing structural quality"},
        {"id": "mobile", "ligne": 7, "dim": "dim1", "fr": "Couverture par un réseau mobile", "en": "Mobile network coverage"},
        {"id": "alerte", "ligne": 22, "dim": "dim2", "fr": "Accès aux messages d'alerte", "en": "Access to early warning"},
        {"id": "comites", "ligne": 28, "dim": "dim2", "fr": "Comités locaux de gestion des risques", "en": "Local disaster risk committees"},
        {"id": "prepa", "ligne": 23, "dim": "dim2", "fr": "Participation à la préparation", "en": "Participation in preparedness"},
        {"id": "services", "ligne": 30, "dim": "dim2", "fr": "Satisfaction des services publics", "en": "Satisfaction with public services"},
        {"id": "etat_civil", "ligne": 24, "dim": "dim2", "fr": "Enregistrement des naissances", "en": "Birth registration"},
        {"id": "foret", "ligne": 54, "dim": "dim3", "fr": "Couvert forestier", "en": "Forest cover"},
        {"id": "pluie", "ligne": 45, "dim": "dim3", "fr": "Pluie rapportée à la normale", "en": "Rainfall against normal"},
        {"id": "aridite", "ligne": 44, "dim": "dim3", "fr": "Absence d'aridité anormale", "en": "Absence of abnormal aridity"},
        {"id": "vegetation", "ligne": 36, "dim": "dim3", "fr": "Santé de la végétation (VHI)", "en": "Vegetation health (VHI)"},
        {"id": "emploi", "ligne": 76, "dim": "dim4", "fr": "Taux d'emploi", "en": "Employment rate"},
        {"id": "revenu", "ligne": 78, "dim": "dim4", "fr": "Revenu au-dessus du seuil", "en": "Income above the threshold"},
        {"id": "reserve", "ligne": 81, "dim": "dim4", "fr": "Réserve de revenu", "en": "Income reserve"},
        {"id": "transferts", "ligne": 79, "dim": "dim4", "fr": "Couverture par les transferts", "en": "Remittance coverage"},
        {"id": "compte", "ligne": 72, "dim": "dim4", "fr": "Compte financier", "en": "Financial account"},
        {"id": "foncier", "ligne": 74, "dim": "dim4", "fr": "Sécurité foncière", "en": "Land tenure security"},
        {"id": "entraide", "ligne": 95, "dim": "dim5", "fr": "Capital social d'entraide", "en": "Bonding social capital"},
        {"id": "passerelle", "ligne": 96, "dim": "dim5", "fr": "Capital social de passerelle", "en": "Bridging social capital"},
        {"id": "ocb", "ligne": 27, "dim": "dim5", "fr": "Appartenance à une organisation", "en": "Membership of an organisation"},
        {"id": "securite", "ligne": 90, "dim": "dim5", "fr": "Sentiment de sécurité", "en": "Sense of safety"},
        {"id": "alimentaire", "ligne": 108, "dim": "dim6", "fr": "Sécurité alimentaire", "en": "Food security"},
        {"id": "education", "ligne": 107, "dim": "dim6", "fr": "Achèvement du primaire", "en": "Primary education completed"},
        {"id": "identite", "ligne": 103, "dim": "dim6", "fr": "Carte d'identité nationale", "en": "National identity card"},
        {"id": "sante", "ligne": None, "dim": "dim6", "fr": "État de santé", "en": "Health status"},
        {"id": "travail", "ligne": None, "dim": "dim6", "fr": "Capacité de travail", "en": "Capacity to work"},
        {"id": "temps_eau", "ligne": None, "dim": "dim1", "fr": "Temps libéré de la corvée d'eau", "en": "Time freed from water collection"},
        {"id": "prod_agri", "ligne": None, "dim": "dim4", "fr": "Productivité agricole", "en": "Agricultural productivity"},
        {"id": "erosion", "ligne": None, "dim": "dim3", "fr": "Stabilité des sols", "en": "Soil stability"},
        {"id": "pression_bois", "ligne": None, "dim": "dim3", "fr": "Faible pression sur le bois-énergie", "en": "Low pressure on fuelwood"},
        {"id": "abondance_bois", "ligne": None, "dim": "dim3", "fr": "Ressource ligneuse disponible", "en": "Available woody resource"},
        {"id": "agro_durable", "ligne": None, "dim": "dim3", "fr": "Pratiques agricoles conservatrices", "en": "Conservation farming practices"},
        {"id": "fertilite", "ligne": None, "dim": "dim3", "fr": "Fertilité des sols", "en": "Soil fertility"},
        {"id": "infiltration", "ligne": None, "dim": "dim3", "fr": "Infiltration et recharge en eau", "en": "Infiltration and water recharge"},
        {"id": "biodiv", "ligne": None, "dim": "dim3", "fr": "Biodiversité", "en": "Biodiversity"},
        {"id": "controle", "ligne": None, "dim": "dim2", "fr": "Contrôle forestier", "en": "Forest law enforcement"},
        {"id": "sensib", "ligne": None, "dim": "dim5", "fr": "Sensibilisation et adaptation des pratiques", "en": "Awareness and practice change"},
        {"id": "ancrage", "ligne": None, "dim": "dim6", "fr": "Maintien de la population sur place", "en": "People staying in place"},
    ],
    "aretes": [
        {"de": "eau", "vers": "sante", "signe": 1, "force": 0.75, "just": "documentee", "ref_fr": "OMS : l'eau non améliorée est le premier facteur des maladies diarrhéiques", "ref_en": "WHO: unimproved water is the leading driver of diarrhoeal disease", "rho": None, "p": None},
        {"de": "assain", "vers": "sante", "signe": 1, "force": 0.7, "just": "documentee", "ref_fr": "ODD 6.2 : l'assainissement géré en sécurité réduit la charge de morbidité", "ref_en": "SDG 6.2: safely managed sanitation lowers disease burden", "rho": None, "p": None},
        {"de": "cuisson", "vers": "sante", "signe": 1, "force": 0.45, "just": "documentee", "ref_fr": "OMS : la combustion de biomasse en intérieur cause des infections respiratoires", "ref_en": "WHO: indoor biomass burning causes respiratory infection", "rho": None, "p": None},
        {"de": "sante_acces", "vers": "sante", "signe": 1, "force": 0.55, "just": "documentee", "ref_fr": "Distance au soin et recours effectif : relation établie en milieu rural", "ref_en": "Distance to care and effective use: established in rural settings", "rho": None, "p": None},
        {"de": "sante", "vers": "travail", "signe": 1, "force": 0.8, "just": "theorique", "ref_fr": "Cadre IRLA : la capacité de travail dépend de l'état de santé", "ref_en": "IRLA framework: capacity to work depends on health status", "rho": None, "p": None},
        {"de": "travail", "vers": "emploi", "signe": 1, "force": 0.55, "just": "theorique", "ref_fr": "Cadre IRLA : capacité de travail et participation à l'emploi", "ref_en": "IRLA framework: capacity to work and labour participation", "rho": None, "p": None},
        {"de": "emploi", "vers": "revenu", "signe": 1, "force": 0.7, "just": "theorique", "ref_fr": "Relation d'usage entre emploi et niveau de revenu", "ref_en": "Standard relation between employment and income level", "rho": 0.49, "p": 0.15},
        {"de": "revenu", "vers": "alimentaire", "signe": 1, "force": 0.65, "just": "documentee", "ref_fr": "FAO : le revenu est le premier déterminant de l'accès économique aux aliments", "ref_en": "FAO: income is the primary determinant of economic access to food", "rho": None, "p": None},
        {"de": "alimentaire", "vers": "sante", "signe": 1, "force": 0.5, "just": "documentee", "ref_fr": "L'insécurité alimentaire dégrade l'état nutritionnel et sanitaire", "ref_en": "Food insecurity degrades nutritional and health status", "rho": None, "p": None},
        {"de": "eau", "vers": "temps_eau", "signe": 1, "force": 0.65, "just": "documentee", "ref_fr": "Le temps de collecte chute quand la source est proche et améliorée", "ref_en": "Collection time drops when the source is nearby and improved", "rho": None, "p": None},
        {"de": "temps_eau", "vers": "travail", "signe": 1, "force": 0.4, "just": "hypothese", "ref_fr": "Hypothèse de modélisation : le temps libéré se reporte sur le travail", "ref_en": "Modelling assumption: freed time shifts to productive work", "rho": None, "p": None},
        {"de": "temps_eau", "vers": "education", "signe": 1, "force": 0.35, "just": "documentee", "ref_fr": "La corvée d'eau pèse sur la scolarisation, en particulier des filles", "ref_en": "Water collection weighs on schooling, girls in particular", "rho": None, "p": None},
        {"de": "revenu", "vers": "services", "signe": 1, "force": 0.3, "just": "hypothese", "ref_fr": "Hypothèse : un revenu plus élevé permet d'accéder aux services payants", "ref_en": "Assumption: higher income enables access to fee-based services", "rho": -0.42, "p": 0.229},
        {"de": "services", "vers": "eau", "signe": 1, "force": 0.45, "just": "theorique", "ref_fr": "Cadre IRLA : la qualité du service public conditionne l'accès à l'eau", "ref_en": "IRLA framework: public service quality conditions water access", "rho": 0.08, "p": 0.821},
        {"de": "compte", "vers": "revenu", "signe": 1, "force": 0.35, "just": "documentee", "ref_fr": "ODD 8.10 : l'inclusion financière soutient l'accumulation et l'investissement", "ref_en": "SDG 8.10: financial inclusion supports accumulation and investment", "rho": -0.38, "p": 0.277},
        {"de": "revenu", "vers": "compte", "signe": 1, "force": 0.4, "just": "theorique", "ref_fr": "Un revenu régulier est la condition d'ouverture d'un compte", "ref_en": "Regular income is the precondition for opening an account", "rho": -0.38, "p": 0.277},
        {"de": "pluie", "vers": "vegetation", "signe": 1, "force": 0.65, "just": "empirique", "ref_fr": "Année sèche 2021 : creux de NDVI dans 7 sections sur 10", "ref_en": "Dry year 2021: NDVI trough in 7 of 10 sections", "rho": -0.01, "p": 0.984},
        {"de": "aridite", "vers": "prod_agri", "signe": 1, "force": 0.55, "just": "documentee", "ref_fr": "L'indice d'aridité UNEP conditionne le potentiel agricole", "ref_en": "The UNEP aridity index conditions agricultural potential", "rho": None, "p": None},
        {"de": "vegetation", "vers": "prod_agri", "signe": 1, "force": 0.5, "just": "theorique", "ref_fr": "La santé de la végétation approche l'état des cultures", "ref_en": "Vegetation health approximates the state of crops", "rho": None, "p": None},
        {"de": "prod_agri", "vers": "revenu", "signe": 1, "force": 0.55, "just": "theorique", "ref_fr": "Cadre IRLA : la production agricole est une source de revenu dominante", "ref_en": "IRLA framework: agricultural output is a dominant income source", "rho": None, "p": None},
        {"de": "prod_agri", "vers": "alimentaire", "signe": 1, "force": 0.6, "just": "theorique", "ref_fr": "Autoconsommation : la production alimente directement le ménage", "ref_en": "Own consumption: production feeds the household directly", "rho": None, "p": None},
        {"de": "foncier", "vers": "prod_agri", "signe": 1, "force": 0.45, "just": "documentee", "ref_fr": "ODD 1.4.2 : la sécurité foncière soutient l'investissement de long terme", "ref_en": "SDG 1.4.2: tenure security supports long-term investment", "rho": None, "p": None},
        {"de": "mobile", "vers": "alerte", "signe": 1, "force": 0.6, "just": "theorique", "ref_fr": "Le message d'alerte passe par le réseau mobile", "ref_en": "The warning message travels over the mobile network", "rho": 0.3, "p": 0.402},
        {"de": "alerte", "vers": "prepa", "signe": 1, "force": 0.45, "just": "theorique", "ref_fr": "Recevoir l'alerte est la condition d'une réponse préparée", "ref_en": "Receiving the warning is the precondition of a prepared response", "rho": -0.41, "p": 0.242},
        {"de": "comites", "vers": "prepa", "signe": 1, "force": 0.55, "just": "theorique", "ref_fr": "Un comité local organise les exercices et l'évacuation", "ref_en": "A local committee organises drills and evacuation", "rho": 0.65, "p": 0.044},
        {"de": "prepa", "vers": "abris", "signe": 1, "force": 0.3, "just": "hypothese", "ref_fr": "Hypothèse : la préparation entretient les abris existants", "ref_en": "Assumption: preparedness maintains existing shelters", "rho": 0.46, "p": 0.18},
        {"de": "ocb", "vers": "comites", "signe": 1, "force": 0.5, "just": "theorique", "ref_fr": "Les comités se recrutent dans le tissu associatif existant", "ref_en": "Committees recruit from the existing associative fabric", "rho": 0.28, "p": 0.427},
        {"de": "etat_civil", "vers": "identite", "signe": 1, "force": 0.65, "just": "documentee", "ref_fr": "L'acte de naissance est la pièce d'entrée de l'état civil", "ref_en": "The birth certificate is the entry document of civil registration", "rho": 0.47, "p": 0.172},
        {"de": "identite", "vers": "compte", "signe": 1, "force": 0.55, "just": "documentee", "ref_fr": "L'identité légale conditionne l'ouverture d'un compte", "ref_en": "Legal identity conditions account opening", "rho": 0.3, "p": 0.404},
        {"de": "identite", "vers": "services", "signe": 1, "force": 0.4, "just": "theorique", "ref_fr": "Sans pièce d'identité, l'accès aux services publics est entravé", "ref_en": "Without identity papers, access to public services is impeded", "rho": 0.43, "p": 0.221},
        {"de": "ocb", "vers": "passerelle", "signe": 1, "force": 0.55, "just": "theorique", "ref_fr": "Putnam : l'appartenance associative construit le capital de passerelle", "ref_en": "Putnam: associational membership builds bridging capital", "rho": -0.15, "p": 0.67},
        {"de": "passerelle", "vers": "transferts", "signe": 1, "force": 0.3, "just": "hypothese", "ref_fr": "Hypothèse : les réseaux étendus portent les transferts", "ref_en": "Assumption: extended networks carry remittances", "rho": 0.19, "p": 0.593},
        {"de": "entraide", "vers": "alimentaire", "signe": 1, "force": 0.4, "just": "documentee", "ref_fr": "L'entraide de proximité amortit les chocs alimentaires courts", "ref_en": "Close-knit mutual aid cushions short food shocks", "rho": None, "p": None},
        {"de": "transferts", "vers": "reserve", "signe": 1, "force": 0.45, "just": "theorique", "ref_fr": "Les transferts alimentent la réserve de précaution", "ref_en": "Remittances feed the precautionary reserve", "rho": 0.78, "p": 0.007},
        {"de": "reserve", "vers": "alimentaire", "signe": 1, "force": 0.5, "just": "theorique", "ref_fr": "Une réserve permet de passer une soudure sans réduire les repas", "ref_en": "A reserve carries a lean season without cutting meals", "rho": None, "p": None},
        {"de": "securite", "vers": "passerelle", "signe": 1, "force": 0.35, "just": "hypothese", "ref_fr": "Hypothèse : l'insécurité restreint les déplacements et les liens", "ref_en": "Assumption: insecurity restricts movement and ties", "rho": 0.3, "p": 0.402},
        {"de": "entraide", "vers": "securite", "signe": 1, "force": 0.3, "just": "hypothese", "ref_fr": "Hypothèse : la densité des liens nourrit le sentiment de sécurité", "ref_en": "Assumption: density of ties feeds the sense of safety", "rho": 0.33, "p": 0.346},
        {"de": "ecole", "vers": "education", "signe": 1, "force": 0.55, "just": "documentee", "ref_fr": "La distance à l'école pèse sur l'achèvement du primaire", "ref_en": "Distance to school weighs on primary completion", "rho": None, "p": None},
        {"de": "education", "vers": "emploi", "signe": 1, "force": 0.45, "just": "documentee", "ref_fr": "Le niveau d'éducation conditionne l'accès à l'emploi formel", "ref_en": "Education level conditions access to formal employment", "rho": None, "p": None},
        {"de": "elec", "vers": "education", "signe": 1, "force": 0.3, "just": "documentee", "ref_fr": "L'éclairage domestique allonge le temps d'étude", "ref_en": "Domestic lighting extends study time", "rho": None, "p": None},
        {"de": "logement", "vers": "sante", "signe": 1, "force": 0.35, "just": "documentee", "ref_fr": "Un logement précaire expose aux intempéries et aux vecteurs", "ref_en": "Precarious housing exposes to weather and vectors", "rho": None, "p": None},
        {"de": "cuisson", "vers": "pression_bois", "signe": 1, "force": 0.6, "just": "documentee", "ref_fr": "Un ménage passé au gaz ou au solaire cesse d'acheter du charbon de bois", "ref_en": "A household on gas or solar stops buying charcoal", "rho": None, "p": None},
        {"de": "pression_bois", "vers": "foret", "signe": 1, "force": 0.65, "just": "documentee", "ref_fr": "La coupe pour le charbon est le premier moteur du recul du couvert", "ref_en": "Cutting for charcoal is the first driver of tree cover loss", "rho": None, "p": None},
        {"de": "foret", "vers": "abondance_bois", "signe": 1, "force": 0.7, "just": "theorique", "ref_fr": "Le couvert disponible détermine la ressource ligneuse", "ref_en": "Available cover determines the woody resource", "rho": None, "p": None},
        {"de": "abondance_bois", "vers": "pression_bois", "signe": 1, "force": 0.45, "just": "documentee", "ref_fr": "La raréfaction fait monter le prix, rend la coupe rentable et attire des producteurs", "ref_en": "Scarcity raises the price, makes cutting profitable and draws in producers", "rho": None, "p": None},
        {"de": "agro_durable", "vers": "fertilite", "signe": 1, "force": 0.6, "just": "documentee", "ref_fr": "Le brûlis répété détruit la matière organique et les racines", "ref_en": "Repeated slash-and-burn destroys organic matter and roots", "rho": None, "p": None},
        {"de": "fertilite", "vers": "prod_agri", "signe": 1, "force": 0.65, "just": "documentee", "ref_fr": "La fertilité commande le rendement", "ref_en": "Fertility governs yield", "rho": None, "p": None},
        {"de": "prod_agri", "vers": "agro_durable", "signe": 1, "force": 0.45, "just": "documentee", "ref_fr": "Une productivité faible pousse à ouvrir de nouvelles parcelles par le feu", "ref_en": "Low productivity pushes households to open new plots by fire", "rho": None, "p": None},
        {"de": "prod_agri", "vers": "foret", "signe": 1, "force": 0.4, "just": "documentee", "ref_fr": "Une productivité faible pousse au défrichement de nouvelles terres", "ref_en": "Low productivity pushes clearing of new land", "rho": None, "p": None},
        {"de": "erosion", "vers": "prod_agri", "signe": 1, "force": 0.6, "just": "documentee", "ref_fr": "La perte de sol arable réduit les rendements", "ref_en": "Loss of topsoil reduces yields", "rho": None, "p": None},
        {"de": "foret", "vers": "erosion", "signe": 1, "force": 0.7, "just": "documentee", "ref_fr": "Le couvert arboré retient les sols sur pente : RUSLE, facteur C", "ref_en": "Tree cover holds soil on slopes: RUSLE, C factor", "rho": None, "p": None},
        {"de": "foret", "vers": "infiltration", "signe": 1, "force": 0.6, "just": "documentee", "ref_fr": "Sans couvert, l'eau ruisselle au lieu de s'infiltrer", "ref_en": "Without cover, water runs off instead of infiltrating", "rho": None, "p": None},
        {"de": "infiltration", "vers": "aridite", "signe": 1, "force": 0.5, "just": "documentee", "ref_fr": "La perte d'humidité du sol aggrave la sécheresse", "ref_en": "Loss of soil moisture deepens drought", "rho": None, "p": None},
        {"de": "aridite", "vers": "vegetation", "signe": 1, "force": 0.55, "just": "theorique", "ref_fr": "L'aridité anormale dégrade l'état de la végétation", "ref_en": "Abnormal aridity degrades vegetation condition", "rho": -0.31, "p": 0.387},
        {"de": "vegetation", "vers": "foret", "signe": 1, "force": 0.35, "just": "theorique", "ref_fr": "Une végétation en mauvais état empêche la régénération du couvert", "ref_en": "Vegetation in poor condition prevents cover regeneration", "rho": -0.32, "p": 0.372},
        {"de": "foret", "vers": "revenu", "signe": 1, "force": 0.35, "just": "documentee", "ref_fr": "Le recul du couvert réduit les revenus agricoles et forestiers durables", "ref_en": "Cover loss reduces sustainable farm and forest income", "rho": 0.28, "p": 0.427},
        {"de": "revenu", "vers": "pression_bois", "signe": 1, "force": 0.45, "just": "documentee", "ref_fr": "À court de liquidités, le ménage coupe davantage pour vendre", "ref_en": "Short of cash, the household cuts more to sell", "rho": None, "p": None},
        {"de": "foret", "vers": "biodiv", "signe": 1, "force": 0.55, "just": "documentee", "ref_fr": "La perte du couvert fait disparaître les espèces qui régénèrent", "ref_en": "Cover loss removes the species that regenerate it", "rho": None, "p": None},
        {"de": "biodiv", "vers": "foret", "signe": 1, "force": 0.4, "just": "documentee", "ref_fr": "Dispersion des graines et pollinisation : la faune régénère le couvert", "ref_en": "Seed dispersal and pollination: wildlife regenerates cover", "rho": None, "p": None},
        {"de": "prod_agri", "vers": "ancrage", "signe": 1, "force": 0.5, "just": "documentee", "ref_fr": "La dégradation des conditions de vie pousse à migrer vers les villes ou l'étranger", "ref_en": "Deteriorating living conditions push migration to cities or abroad", "rho": None, "p": None},
        {"de": "ancrage", "vers": "pression_bois", "signe": -1, "force": 0.4, "just": "documentee", "ref_fr": "Le départ d'une partie de la population allège la pression locale sur la forêt", "ref_en": "Out-migration of part of the population eases local pressure on the forest", "rho": None, "p": None},
        {"de": "foret", "vers": "sensib", "signe": -1, "force": 0.35, "just": "documentee", "ref_fr": "Sécheresses et inondations sensibilisent les communautés à la valeur des forêts", "ref_en": "Droughts and floods make communities aware of the value of forests", "rho": None, "p": None},
        {"de": "sensib", "vers": "agro_durable", "signe": 1, "force": 0.5, "just": "documentee", "ref_fr": "Agroforesterie, compostage, charbon écologique : les pratiques s'adaptent", "ref_en": "Agroforestry, composting, eco-charcoal: practices adapt", "rho": None, "p": None},
        {"de": "abondance_bois", "vers": "cuisson", "signe": -1, "force": 0.4, "just": "documentee", "ref_fr": "Quand le charbon devient trop cher, les ménages se tournent vers le gaz ou le solaire", "ref_en": "When charcoal gets too expensive, households turn to gas or solar", "rho": None, "p": None},
        {"de": "controle", "vers": "pression_bois", "signe": 1, "force": 0.45, "just": "theorique", "ref_fr": "L'absence de contrôle forestier laisse la coupe se faire sans frein", "ref_en": "Absent enforcement leaves cutting unchecked", "rho": None, "p": None},
        {"de": "services", "vers": "controle", "signe": 1, "force": 0.4, "just": "theorique", "ref_fr": "Le contrôle forestier est un service public parmi d'autres", "ref_en": "Forest enforcement is one public service among others", "rho": None, "p": None},
    ],
}


def charger(chemin=None):
    """Le graphe : celui du fichier s'il existe, celui du module sinon."""
    p = chemin or GRAPHE
    try:
        with open(p, encoding="utf-8") as f:
            g = json.load(f)
        if g.get("noeuds") and g.get("aretes"):
            return g
    except (OSError, ValueError):
        pass
    return GRAPHE_DEFAUT


def matrice(graphe, brute=False):
    """A[v, u] = signe × force de u → v, et l'ordre stable des nœuds.

    `brute=True` rend la matrice des forces telles qu'elles sont écrites dans
    le fichier — c'est celle qu'il faut pour diagnostiquer le modèle. Par
    défaut la matrice est mise à l'échelle (voir RAYON_CIBLE) : c'est celle
    qui sert à propager.
    """
    ids = [n["id"] for n in graphe["noeuds"]]
    idx = {v: i for i, v in enumerate(ids)}
    A = np.zeros((len(ids), len(ids)))
    for e in graphe["aretes"]:
        A[idx[e["vers"]], idx[e["de"]]] = e["signe"] * e["force"]
    if not brute and len(ids):
        rayon = float(max(abs(np.linalg.eigvals(A))))
        if rayon > RAYON_CIBLE:
            A = A * (RAYON_CIBLE / rayon)
    return A, ids, idx


def diagnostic(graphe):
    """Le modèle converge-t-il ? À vérifier, pas à supposer.

    Si quelqu'un renforce une arête et fait passer le rayon spectral au-dessus
    de 1, la propagation part à l'infini et les chiffres deviennent absurdes
    sans prévenir. L'interface affiche ce diagnostic.
    """
    A, ids, _ = matrice(graphe, brute=True)
    rayon = float(max(abs(np.linalg.eigvals(A)))) if len(ids) else 0.0
    return {"rayon": rayon, "converge": rayon < 1, "tendu": rayon >= TENDU,
            "facteur": (RAYON_CIBLE / rayon) if rayon > RAYON_CIBLE else 1.0,
            "cible": RAYON_CIBLE,
            "noeuds": len(ids), "aretes": len(graphe["aretes"])}


def propager(graphe, variations):
    """Effet total sur chaque nœud, en points de score (échelle 0-10).

    `variations` : {id du nœud : variation posée}. L'effet rendu EXCLUT la
    variation posée elle-même sur les nœuds pilotés — c'est l'effet propagé,
    ce que l'utilisateur veut lire. La variation posée reste disponible dans
    `variations` pour l'affichage.
    """
    A, ids, idx = matrice(graphe)
    e0 = np.zeros(len(ids))
    for cle, v in (variations or {}).items():
        if cle in idx:
            e0[idx[cle]] = v
    I = np.eye(len(ids))
    try:
        total = np.linalg.solve(I - A, e0) - e0
    except np.linalg.LinAlgError:
        # (I − A) singulière : le modèle est exactement à la limite. On
        # retombe sur la somme tronquée, qui reste définie, et le diagnostic
        # affiché à l'écran dit au lecteur de s'en méfier.
        vague, total = e0.copy(), np.zeros(len(ids))
        for _ in range(200):
            vague = A.dot(vague)
            total += vague
    return {ids[i]: float(total[i]) for i in range(len(ids))}


def etat_courant(graphe, scores_par_ligne, cible="Total"):
    """Score de départ de chaque nœud mesuré, sous la cible demandée.

    Un nœud non mesuré — l'état de santé, la capacité de travail — n'a pas de
    score : il rend None, et l'interface le montre comme tel plutôt que
    d'inventer une valeur de départ.
    """
    etat = {}
    for n in graphe["noeuds"]:
        lg = n.get("ligne")
        r = scores_par_ligne.get(lg) if lg else None
        sc = (r.get("scores_corriges") or {}).get(cible) if r else None
        etat[n["id"]] = float(sc) if sc is not None else None
    return etat


def apres(etat, effets, variations):
    """État simulé, borné à l'échelle 0-10 — un score n'existe pas au-delà."""
    out = {}
    for cle, v in etat.items():
        if v is None:
            out[cle] = None
            continue
        out[cle] = max(0.0, min(10.0, v + effets.get(cle, 0.0)
                                + (variations or {}).get(cle, 0.0)))
    return out


def direction(delta):
    """↑ / ↓ / → selon le seuil de négligeabilité."""
    if delta > SEUIL_NUL:
        return "hausse"
    if delta < -SEUIL_NUL:
        return "baisse"
    return "nul"


def _cycles(succ, ids):
    """Énumère les cycles élémentaires du graphe, sans dépendance extérieure.

    ÉCRIT À LA MAIN PLUTÔT QU'IMPORTÉ. La première version appelait networkx,
    qui n'est pas dans `requirements.txt` : le site est tombé au déploiement
    sur un ModuleNotFoundError. Ajouter la dépendance aurait marché, mais
    ajouter un paquet entier pour une seule fonction de vingt lignes — et un
    fichier de plus à ne pas oublier d'envoyer — coûte plus que de l'écrire.

    Le principe est classique : une exploration en profondeur depuis chaque
    nœud de départ, en n'autorisant que les nœuds d'INDICE SUPÉRIEUR OU ÉGAL au
    départ. Chaque cycle n'est ainsi énuméré qu'une fois, à partir de son plus
    petit indice, au lieu d'une fois par nœud qu'il contient.
    """
    rang = {v: i for i, v in enumerate(ids)}
    trouves, coupe = [], False
    for depart in ids:
        r0 = rang[depart]
        pile = [(depart, [depart], {depart})]
        while pile:
            noeud, chemin, vus = pile.pop()
            if len(trouves) >= BOUCLES_MAX:
                coupe = True
                break
            for suiv in succ.get(noeud, ()):
                if suiv == depart:
                    trouves.append(list(chemin))
                elif (rang[suiv] > r0 and suiv not in vus
                      and len(chemin) < BOUCLE_MAX):
                    pile.append((suiv, chemin + [suiv], vus | {suiv}))
        if coupe:
            break
    return trouves, coupe


def boucles(graphe):
    """Les boucles du graphe, classées renforçante / équilibrante.

    Le signe d'une boucle est le PRODUIT des signes de ses arêtes : pair de
    liens négatifs → renforçante, impair → équilibrante. C'est la définition de
    la dynamique des systèmes, pas une convention d'affichage.

    La force d'une boucle est le produit de celles de ses arêtes — c'est elle
    qui décide de son poids réel dans la propagation.
    """
    succ, arc = {}, {}
    for e in graphe["aretes"]:
        succ.setdefault(e["de"], []).append(e["vers"])
        arc[(e["de"], e["vers"])] = (e["signe"], e["force"])
    ids = [n["id"] for n in graphe["noeuds"]]
    cycles, coupe = _cycles(succ, ids)
    out = []
    for cycle in cycles:
        signe, force = 1, 1.0
        for i, u in enumerate(cycle):
            v = cycle[(i + 1) % len(cycle)]
            sg, fo = arc[(u, v)]
            signe *= sg
            force *= fo
        out.append({"noeuds": cycle,
                    "type": "renforcante" if signe > 0 else "equilibrante",
                    "force": force, "n": len(cycle), "tronque": coupe})
    return sorted(out, key=lambda b: (b["n"], -b["force"]))


def aretes_de_boucle(boucle):
    """Les couples (de, vers) d'une boucle, pour l'isoler à l'écran."""
    c = boucle["noeuds"]
    return {(c[i], c[(i + 1) % len(c)]) for i in range(len(c))}


def effet_indice(graphe, effets, variations, scores_par_ligne):
    """Effet sur l'indice global, et la part de l'indice réellement touchée.

    LES DEUX CHIFFRES COMPTENT. L'effet seul se lirait comme une variation de
    l'indice complet, alors que le graphe ne couvre qu'une partie des
    indicateurs scorés : le reste ne bouge pas, faute de relation posée. On
    rend donc aussi la part de poids couverte, pour que l'interface puisse
    l'écrire à côté.
    """
    poids_total = sum((r.get("ponderation") or 1) for r in
                      scores_par_ligne.values()
                      if (r.get("scores_corriges") or {}).get("Total")
                      is not None)
    num, poids_couvert = 0.0, 0.0
    for n in graphe["noeuds"]:
        lg = n.get("ligne")
        r = scores_par_ligne.get(lg) if lg else None
        if not r or (r.get("scores_corriges") or {}).get("Total") is None:
            continue
        p = r.get("ponderation") or 1
        avant = float(r["scores_corriges"]["Total"])
        d = effets.get(n["id"], 0.0) + (variations or {}).get(n["id"], 0.0)
        num += p * (max(0.0, min(10.0, avant + d)) - avant)
        poids_couvert += p
    return {"delta": (num / poids_total) if poids_total else 0.0,
            "part_couverte": (poids_couvert / poids_total) if poids_total
            else 0.0}


def desaccords(graphe):
    """Relations dont la littérature vérifiée contredit le sens du modèle.

    CE N'EST PAS UNE ANOMALIE À CACHER, c'est le résultat le plus utile de la
    vérification des sources. Ces relations ont été posées dans un sens par le
    cadre, et la meilleure source trouvée dit l'inverse : la certification
    foncière au Mexique a fait PARTIR davantage de monde, la hausse des
    rendements agricoles s'accompagne de PLUS de déforestation sous les
    tropiques. Le modèle n'est pas corrigé en silence, parce que retourner une
    flèche est une décision de modélisation qui appartient à l'équipe : la
    contradiction est signalée, et le lecteur en juge.

    L'ancienne version de cette fonction comparait le signe du modèle à une
    corrélation calculée sur les dix moyennes de section. À n = 10, une
    corrélation n'a presque aucune puissance, et ces coefficients ont été
    retirés du fichier plutôt que d'être présentés comme des preuves.
    """
    return [e for e in graphe["aretes"] if e.get("conteste")]

def sous_type(boucle, sens):
    """R+ / R− / B+ / B−, selon la typologie du complément méthodologique.

    « Positive » ne veut pas dire « bonne ». Le mot dit que les variables
    bougent dans le même sens ; c'est le SENS DU DÉPART qui décide si la
    spirale est vertueuse ou vicieuse. Une boucle renforçante poussée à la
    hausse est une spirale vertueuse (R+) ; la MÊME boucle poussée à la baisse
    est une spirale vicieuse (R−).

    C'est pour cela que le sous-type est calculé ici avec `sens`, et non porté
    par la boucle elle-même : il n'appartient pas au graphe, il appartient au
    scénario qu'on est en train de jouer.
    """
    lettre = "R" if boucle["type"] == "renforcante" else "B"
    return lettre + ("+" if sens >= 0 else "−")


def leviers(graphe, lst_boucles=None):
    """Les points où une petite modification produit un grand changement.

    Trois critères, tirés du complément méthodologique, et tous calculés :

      · le DEGRÉ — un nœud très connecté participe à beaucoup de chemins ;
      · le NOMBRE DE BOUCLES auxquelles il appartient — il a un effet
        multiplicateur, pas seulement en cascade ;
      · l'APPARTENANCE À DES BOUCLES DE SENS OPPOSÉ — c'est le critère décisif.
        Un nœud présent à la fois dans une boucle renforçante et dans une
        boucle équilibrante est un point de bascule : c'est là qu'on peut
        faire passer le système d'une dynamique dégradante à une dynamique de
        résilience.
    """
    lst = lst_boucles if lst_boucles is not None else boucles(graphe)
    entrant, sortant = {}, {}
    for e in graphe["aretes"]:
        sortant[e["de"]] = sortant.get(e["de"], 0) + 1
        entrant[e["vers"]] = entrant.get(e["vers"], 0) + 1
    out = []
    for n in graphe["noeuds"]:
        cle = n["id"]
        dedans = [b for b in lst if cle in b["noeuds"]]
        renf = sum(1 for b in dedans if b["type"] == "renforcante")
        equi = len(dedans) - renf
        ent, sor = entrant.get(cle, 0), sortant.get(cle, 0)
        out.append({
            "id": cle, "entrant": ent, "sortant": sor, "degre": ent + sor,
            "boucles": len(dedans), "renforcantes": renf, "equilibrantes": equi,
            "bascule": renf > 0 and equi > 0,
            "poids_boucles": sum(b["force"] for b in dedans),
        })
    # Le nœud de bascule passe devant : c'est le critère qui compte le plus.
    return sorted(out, key=lambda x: (not x["bascule"], -x["boucles"],
                                      -x["degre"]))


def boucles_dominantes(graphe, lst_boucles=None, top=6):
    """Les relations partagées par le plus de boucles.

    Ce sont les croisements du système : agir sur une de ces relations touche
    plusieurs sous-systèmes à la fois. Le complément méthodologique les appelle
    des leviers de basculement, et c'est là qu'il faut chercher comment
    transformer une boucle dégradante en boucle régulatrice.
    """
    lst = lst_boucles if lst_boucles is not None else boucles(graphe)
    compte = {}
    for b in lst:
        for arc in aretes_de_boucle(b):
            e = compte.setdefault(arc, {"n": 0, "renf": 0, "equi": 0})
            e["n"] += 1
            e["renf" if b["type"] == "renforcante" else "equi"] += 1
    lignes = [{"de": k[0], "vers": k[1], **v} for k, v in compte.items()]
    return sorted(lignes, key=lambda x: -x["n"])[:top]
