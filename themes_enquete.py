"""Les quarante-six modules du questionnaire, rangés en dix thématiques.

POURQUOI CE REGROUPEMENT EXISTE.
Le questionnaire est découpé en modules — AA, AB, AC… — et ce découpage est
celui de l'ENQUÊTEUR : il suit l'ordre de passation, il sépare « superficie
dédiée par culture » de « rendements annuels par culture » parce que ce sont
deux tableaux à remplir l'un après l'autre. C'est le bon découpage sur le
terrain, et c'est le mauvais pour chercher : quarante-six entrées dans une
barre d'onglets ne se lisent pas, et le lecteur qui veut « quelque chose sur
l'agriculture » doit savoir d'avance dans lequel des onze modules agricoles
regarder.

CE QUE FAIT CE MODULE. Il range les modules en dix thématiques — celles dans
lesquelles on PENSE une question, pas celles dans lesquelles on la POSE — et
rien d'autre. Aucune question n'est renommée, aucune n'est écartée : le module
d'origine reste écrit à côté de chaque question dans la liste, si bien qu'on
retrouve toujours d'où elle vient.

UN MODULE INCONNU N'EST PAS PERDU. Ajoutez demain un module au questionnaire :
il tombera dans « Autres », visible, plutôt que de disparaître d'un écran qui
ne l'attendait pas. C'est la seule façon de faire dont on soit sûr qu'elle ne
cache rien.

L'ORDRE DES THÉMATIQUES EST CELUI DU FOYER VERS LE DEHORS : qui vit là, dans
quoi, de quoi, puis ce qu'il cultive, élève et pêche, puis ce qu'il mange,
puis avec qui il vit, puis face à quoi.
"""

# (code, clé de libellé, [préfixes de module])
#
# LE PRÉFIXE EST LE CODE DE LETTRE DU MODULE, POINT COMPRIS. « A. » et
# « AA. » se distinguent par ce point : sans lui, « A » attraperait les vingt
# modules commençant par un A.
THEMES = [
    ("foyer", "th_foyer", ["AF.", "AQ.", "H."]),
    ("logement", "th_logement", ["AI.", "AJ.", "C.", "D.", "E."]),
    ("revenus", "th_revenus", ["AG.", "Q.", "S.", "R.", "AE.", "P."]),
    ("agriculture", "th_agriculture",
     ["T.", "AL.", "AM.", "AN.", "AO.", "AP.", "AR.", "U.", "V.", "W.",
      "X."]),
    ("elevage", "th_elevage", ["AC.", "AD.", "AH."]),
    ("peche", "th_peche", ["Y.", "Z.", "AA.", "AB."]),
    ("alimentation", "th_alimentation", ["N.", "G.", "M."]),
    ("social", "th_social", ["AK.", "K.", "L."]),
    ("risques", "th_risques", ["J.", "I.", "F."]),
    ("migration", "th_migration", ["O."]),
]

# LES INDICATEURS CALCULÉS N'ONT PAS DE CODE DE MODULE, et pour cause : ils
# n'ont pas été posés sur le terrain. Leur catégorie porte « (calculé) », et
# c'est à cela qu'on les reconnaît.
CALCULE = "calcul"
AUTRES = "autres"

TEXTES = {
    "th_foyer": {"en": "The household", "fr": "Le foyer"},
    "thd_foyer": {"en": "Who lives there, and where they come from",
                  "fr": "Qui y vit, et d'où il vient"},
    "th_logement": {"en": "Housing and services",
                    "fr": "Logement et services"},
    "thd_logement": {"en": "Dwelling, water, sanitation, energy, waste, "
                           "telephone",
                     "fr": "Habitat, eau, assainissement, énergie, déchets, "
                           "téléphone"},
    "th_revenus": {"en": "Income and livelihoods",
                   "fr": "Revenus et moyens d'existence"},
    "thd_revenus": {"en": "Sources of income, employment, savings, credit, "
                          "land rights",
                    "fr": "Sources de revenus, emploi, épargne, crédit, "
                          "droits fonciers"},
    "th_agriculture": {"en": "Farming", "fr": "Agriculture"},
    "thd_agriculture": {"en": "Practices, areas, sowing, yields, losses, "
                              "fruit trees, inputs",
                        "fr": "Pratiques, superficies, semis, rendements, "
                              "pertes, arbres fruitiers, intrants"},
    "th_elevage": {"en": "Livestock", "fr": "Élevage"},
    "thd_elevage": {"en": "Herds, feeding, mortality and its causes",
                    "fr": "Effectifs, alimentation, mortalité et ses causes"},
    "th_peche": {"en": "Fishing", "fr": "Pêche"},
    "thd_peche": {"en": "Gear, boats, species, grounds, earnings, seasons",
                  "fr": "Engins, embarcations, espèces, zones, revenus, "
                        "saisons"},
    "th_alimentation": {"en": "Food, health and school",
                        "fr": "Alimentation, santé et école"},
    "thd_alimentation": {"en": "Food security over twelve months, distance "
                               "to clinic and school",
                         "fr": "Sécurité alimentaire sur douze mois, "
                               "distance au dispensaire et à l'école"},
    "th_social": {"en": "Social and community life",
                  "fr": "Vie sociale et communautaire"},
    "thd_social": {"en": "Mutual aid, groups attended, participation, "
                         "trust, conflicts",
                   "fr": "Entraide, groupes fréquentés, participation, "
                         "confiance, conflits"},
    "th_risques": {"en": "Risks and institutions",
                   "fr": "Risques et institutions"},
    "thd_risques": {"en": "Hazards, alerts, preparedness, administrative "
                          "services, integrity",
                    "fr": "Aléas, alertes, préparation, services "
                          "administratifs, intégrité"},
    "th_migration": {"en": "Migration", "fr": "Migration"},
    "thd_migration": {"en": "Departures, destinations, remittances, "
                            "intention to leave",
                      "fr": "Départs, destinations, transferts, intention de "
                            "partir"},
    "th_calcul": {"en": "Computed indicators", "fr": "Indicateurs calculés"},
    "thd_calcul": {"en": "Not asked in the field: built by a rule from "
                         "several answers",
                   "fr": "Non posés sur le terrain : construits par une "
                         "règle à partir de plusieurs réponses"},
    "th_autres": {"en": "Other", "fr": "Autres"},
    "thd_autres": {"en": "Modules that fit none of the above",
                   "fr": "Les modules qui n'entrent dans aucune des "
                         "rubriques ci-dessus"},
}


import i18n  # noqa: E402

for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)


def theme_de(categorie):
    """La thématique d'un module du questionnaire."""
    c = (categorie or "").strip()
    if "(calculé)" in c or "(computed)" in c:
        return CALCULE
    for code, _lib, prefixes in THEMES:
        for p in prefixes:
            if c.upper().startswith(p):
                return code
    return AUTRES


def codes_presents(categories):
    """Les thématiques réellement portées par ce questionnaire, dans l'ordre.

    UNE THÉMATIQUE VIDE NE S'AFFICHE PAS : un onglet « Pêche » sur un jeu de
    données sans module de pêche promettrait un écran qui n'existe pas.
    """
    vus = {theme_de(c) for c in categories}
    ordre = [c for c, _l, _p in THEMES] + [CALCULE, AUTRES]
    return [c for c in ordre if c in vus]


def libelle(code):
    return "th_" + code


def description(code):
    return "thd_" + code
