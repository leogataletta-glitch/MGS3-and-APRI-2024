"""Les mesures satellitaires, section communale par section communale.

POURQUOI ELLES ONT LEUR PLACE DANS LES RÉSULTATS BRUTS, ET PAS AILLEURS.
Un résultat brut est une mesure avant tout barème : ce que les ménages ont
répondu, ou ce que le capteur a vu. La couverture forestière de Hansen et le
NDVI de Sentinel-2 sont exactement cela — des mesures, pas des scores. Les
tenir à l'écart des résultats bruts obligeait à les chercher dans la page
« environnement », deux clics plus loin, alors qu'on les compare aux réponses
des ménages de la même section.

ELLES NE SE VENTILENT PAS PAR SEXE, PAR ÂGE NI PAR RICHESSE, ET C'EST UNE
PROPRIÉTÉ DE LA MESURE, PAS UN MANQUE. Un pixel n'a pas de ménage : il a une
section communale. Proposer « le NDVI des femmes » afficherait un menu qui ne
peut rien produire. La seule ventilation offerte est donc géographique, et
elle est dite.

CHAQUE MESURE PORTE SA SOURCE, SON CAPTEUR ET SA PÉRIODE. Une couverture
forestière n'a pas de sens sans son seuil de couvert, un NDVI n'en a pas sans
sa saison : deux capteurs et deux fenêtres donnent deux chiffres différents
pour la même forêt, et le lecteur doit savoir lequel il lit.
"""

import json
import os

import streamlit as st

import i18n
import map_render
import onglets
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

ENCRE, ENCRE3, GRIS = "#101728", "#6b7590", "#8a93a5"
VERT_APRI = "#2a6b3f"

# Les mesures offertes : (code, clé de libellé, fichier, chemin, unité,
# décimales, polarité de carte). `serie:<nom>` lit la dernière année de la
# série ; `serie:<nom>:delta` lit l'écart entre la première et la dernière.
# CHAQUE MESURE PORTE SA CATÉGORIE. Une liste déroulante de quarante entrées
# mélangeant la forêt, la pluie et la température obligeait à lire tous les
# intitulés pour trouver celui qu'on cherchait, et surtout elle cachait ce
# qu'elle contenait : on ne pouvait pas savoir que la pluie était mesurée sans
# dérouler jusqu'à elle. Les catégories sont donc des onglets, et la liste ne
# porte plus que les mesures de la catégorie ouverte.
#
# (catégorie, code, clé de libellé, fichier, chemin, unité, décimales,
#  polarité de carte). `serie:<nom>` lit la dernière année de la série ;
# `serie:<nom>:delta` lit l'écart entre la première et la dernière.
MESURES = [
    # --- la forêt
    ("foret", "foret2025_pct", "sat_m_couvert", "foret", "foret2025_pct",
     "%", 1, "eleve_bon"),
    ("foret", "foret2000_pct", "sat_m_couvert2000", "foret", "foret2000_pct",
     "%", 1, "eleve_bon"),
    ("foret", "perte_relative_pct", "sat_m_perte", "foret",
     "perte_relative_pct", "%", 1, "eleve_mauvais"),
    ("foret", "perte_totale_ha", "sat_m_perte_ha", "foret",
     "perte_totale_ha", "ha", 1, "eleve_mauvais"),
    ("foret", "taux_annuel_net", "sat_m_taux", "foret", "taux_annuel_net",
     "%/an", 3, "eleve_bon"),
    ("foret", "part_choc_pct", "sat_m_choc", "foret", "part_choc_pct",
     "%", 1, "eleve_mauvais"),
    # --- la végétation
    ("vege", "ndvi", "sat_m_ndvi", "vege", "serie:serie_ndvi", "", 3,
     "eleve_bon"),
    ("vege", "ndvi_delta", "sat_m_ndvi_d", "vege", "serie:serie_ndvi:delta",
     "", 3, "eleve_bon"),
    ("vege", "ndmi", "sat_m_ndmi", "vege", "serie:serie_ndmi", "", 3,
     "eleve_bon"),
    ("vege", "evi", "sat_m_evi", "vege", "serie:serie_evi", "", 3,
     "eleve_bon"),
    ("vege", "savi", "sat_m_savi", "vege", "serie:serie_savi", "", 3,
     "eleve_bon"),
    ("vege", "vari", "sat_m_vari", "vege", "serie:serie_vari", "", 3,
     "eleve_bon"),
    ("vege", "fvc", "sat_m_fvc", "vege", "serie:serie_fvc", "", 3,
     "eleve_bon"),
    # LA VARIABILITÉ INTERANNUELLE EST UNE MESURE À PART ENTIÈRE, et c'est
    # même celle qui dit la résilience : une végétation qui vaut la même
    # chose chaque année tient, une qui saute d'une année à l'autre dépend
    # de la pluie de l'année.
    ("vege", "var_ndvi", "sat_m_var_ndvi", "vege", "var_ndvi", "", 3,
     "eleve_mauvais"),
    ("vege", "var_ndmi", "sat_m_var_ndmi", "vege", "var_ndmi", "", 3,
     "eleve_mauvais"),
    ("vege", "vhi", "sat_m_vhi", "thermique", "vhi", "", 1, "eleve_bon"),
    ("vege", "vci", "sat_m_vci", "thermique", "vci", "", 1, "eleve_bon"),
    # --- l'eau de surface
    ("eau", "ndwi", "sat_m_ndwi", "vege", "serie:serie_ndwi", "", 3,
     "eleve_bon"),
    ("eau", "frac_eau", "sat_m_frac_eau", "vege", "serie:serie_frac_eau",
     "%", 2, "eleve_bon"),
    ("eau", "eau_ha", "sat_m_eau_ha", "vege", "eau_ha", "ha", 1,
     "eleve_bon"),
    ("eau", "ndti", "sat_m_ndti", "vege", "serie:serie_ndti_eau", "", 3,
     "eleve_mauvais"),
    ("eau", "var_eau", "sat_m_var_eau", "vege", "var_eau", "", 3,
     "eleve_mauvais"),
    # --- la pluie
    ("pluie", "pluie_courante", "sat_m_pl_courante", "pluie",
     "pluie_courante_mm", "mm", 0, "eleve_bon"),
    ("pluie", "pluie_normale", "sat_m_pl_normale", "pluie", "normale_mm",
     "mm", 0, "eleve_bon"),
    ("pluie", "ratio_normale", "sat_m_pl_ratio", "pluie", "ratio_normale",
     "%", 1, "eleve_bon"),
    ("pluie", "spi", "sat_m_pl_spi", "pluie", "spi", "", 2, "eleve_bon"),
    ("pluie", "pci", "sat_m_pl_pci", "pluie", "pci", "", 1, "eleve_bon"),
    ("pluie", "aai", "sat_m_pl_aai", "pluie", "aai", "", 3, "eleve_mauvais"),
    ("pluie", "pluie_serie", "sat_m_pl_serie", "pluie", "serie:serie_mm",
     "mm", 0, "eleve_bon"),
    ("pluie", "pl_min", "sat_m_pl_min", "pluie", "minimum_mm", "mm", 0,
     "eleve_bon"),
    ("pluie", "pl_max", "sat_m_pl_max", "pluie", "maximum_mm", "mm", 0,
     "eleve_bon"),
    # --- la saison des pluies, c'est-à-dire la variation intra-annuelle
    ("saison", "mam_courant", "sat_m_sa_mam", "saison", "mam_courant_mm",
     "mm", 0, "eleve_bon"),
    ("saison", "mam_normale", "sat_m_sa_mam_n", "saison", "mam_normale_mm",
     "mm", 0, "eleve_bon"),
    ("saison", "aso_courant", "sat_m_sa_aso", "saison", "aso_courant_mm",
     "mm", 0, "eleve_bon"),
    ("saison", "spi_mam", "sat_m_sa_spi", "saison", "spi", "", 2,
     "eleve_bon"),
    ("saison", "secs_mam", "sat_m_sa_secs", "saison", "secs_mam_courant",
     "j", 1, "eleve_mauvais"),
    ("saison", "secs_an", "sat_m_sa_secs_an", "saison", "secs_an_courant",
     "j", 1, "eleve_mauvais"),
    ("saison", "j50", "sat_m_sa_j50", "saison", "j50_courant", "j", 2,
     "eleve_bon"),
    ("saison", "install_recent", "sat_m_sa_install", "saison",
     "install_jour_recent", "j", 0, "eleve_mauvais"),
    ("saison", "install_decalage", "sat_m_sa_decalage", "saison",
     "install_decalage_j", "j", 1, "eleve_bon"),
    ("saison", "install_ratees", "sat_m_sa_ratees", "saison",
     "install_ratees", "", 0, "eleve_mauvais"),
    ("saison", "pci_mam", "sat_m_sa_pci", "saison", "pci", "", 1,
     "eleve_bon"),
    ("saison", "aai_mam", "sat_m_sa_aai", "saison", "aai", "", 3,
     "eleve_mauvais"),
    ("saison", "ratio_mam", "sat_m_sa_ratio", "saison", "ratio_normale",
     "%", 1, "eleve_bon"),
    ("saison", "mam_serie", "sat_m_sa_serie", "saison", "serie:serie_mam",
     "mm", 0, "eleve_bon"),
    # --- la température
    ("temp", "lst_courant", "sat_m_t_courant", "thermique", "lst_courant_c",
     "°C", 2, "eleve_mauvais"),
    ("temp", "lst_normale", "sat_m_t_normale", "thermique", "lst_normale_c",
     "°C", 2, "eleve_mauvais"),
    ("temp", "lst_anomalie", "sat_m_t_anomalie", "thermique",
     "lst_anomalie_pct", "%", 2, "eleve_mauvais"),
    ("temp", "lst_an", "sat_m_t_an", "thermique", "lst_an_moy_c", "°C", 2,
     "eleve_mauvais"),
    ("temp", "lst_nuit", "sat_m_t_nuit", "thermique", "lst_nuit_moy_c",
     "°C", 2, "eleve_mauvais"),
    # L'AMPLITUDE JOUR-NUIT EST LA VARIATION INTRA-ANNUELLE DE LA CHALEUR :
    # un sol nu chauffe le jour et se vide la nuit, un sol couvert amortit
    # les deux. C'est l'indicateur qui distingue un versant boisé d'un
    # versant pelé mieux que la moyenne annuelle.
    ("temp", "lst_amplitude", "sat_m_t_ampli", "thermique",
     "lst_amplitude_c", "°C", 2, "eleve_mauvais"),
    ("temp", "lst_max", "sat_m_t_max", "thermique", "lst_max_c", "°C", 2,
     "eleve_mauvais"),
    ("temp", "tci", "sat_m_t_tci", "thermique", "tci", "", 1, "eleve_bon"),
    ("temp", "lst_serie", "sat_m_t_serie", "thermique",
     "serie:serie_lst_saison", "°C", 2, "eleve_mauvais"),
    ("temp", "lst_serie_an", "sat_m_t_serie_an", "thermique",
     "serie:serie_lst_an", "°C", 2, "eleve_mauvais"),
    # --- le bilan hydrique
    ("aridite", "aridite", "sat_m_ar_indice", "thermique", "aridite", "",
     3, "eleve_bon"),
    ("aridite", "et", "sat_m_ar_et", "thermique", "et_mm", "mm", 0,
     "eleve_bon"),
    ("aridite", "pet", "sat_m_ar_pet", "thermique", "pet_mm", "mm", 0,
     "eleve_mauvais"),
    ("aridite", "pluie_bilan", "sat_m_ar_pluie", "thermique", "pluie_mm",
     "mm", 0, "eleve_bon"),
    # --- LA FRAGMENTATION ET LA CONNECTIVITÉ, calculées sur la couverture
    # du sol et non sur un indice spectral. Elles ne décrivent pas l'état de
    # la végétation mais la FORME de l'habitat : combien il en reste, en
    # combien de morceaux, et si ces morceaux se rejoignent. Sept d'entre
    # elles portent un barème du référentiel.
    ("frag", "habitat_pct", "sat_m_habitat", "frag", "habitat_pct",
     "%", 1, "eleve_bon"),
    ("frag", "taches_total", "sat_m_taches", "frag", "taches_total",
     "", 0, "eleve_mauvais"),
    ("frag", "densite_lisiere_m_ha", "sat_m_lisiere", "frag",
     "densite_lisiere_m_ha", " m/ha", 1, "eleve_mauvais"),
    ("frag", "core_pct", "sat_m_core", "frag", "core_pct", "%", 2,
     "eleve_bon"),
    ("frag", "core_ha", "sat_m_core_ha", "frag", "core_ha", " ha", 1,
     "eleve_bon"),
    ("frag", "ratio_core_move", "sat_m_ratio", "frag", "ratio_core_move",
     "", 3, "eleve_bon"),
    ("frag", "pc_d", "sat_m_pc", "frag", "pc_d", "", 3, "eleve_bon"),
    ("frag", "pc_d2", "sat_m_pc2", "frag", "pc_d2", "", 3, "eleve_bon"),
    ("frag", "iic", "sat_m_iic", "frag", "iic", "", 3, "eleve_bon"),
    ("frag", "iic_d", "sat_m_iic_d", "frag", "iic_d", "", 3, "eleve_bon"),
    ("frag", "aire_habitat_ha", "sat_m_hab_ha", "frag", "aire_habitat_ha",
     " ha", 1, "eleve_bon"),
    # --- L'ACCÈS ROUTIER. Ni orbite ni indice spectral : un réseau routier
    # ouvert et un raster de population. La mesure retenue par le
    # référentiel est la première ; les deux suivantes sont là parce que le
    # chiffre dépend d'une définition, et qu'un lecteur doit pouvoir voir de
    # combien.
    ("acces", "acces_axe", "sat_m_acces", "acces", "acces_axe", "%", 1,
     "eleve_bon"),
    ("acces", "acces_pistes", "sat_m_acces_p", "acces", "acces_pistes",
     "%", 1, "eleve_bon"),
    ("acces", "acces_classe", "sat_m_acces_c", "acces", "acces_classe",
     "%", 1, "eleve_bon"),
    ("acces", "pop", "sat_m_pop", "acces", "pop", "", 0, "eleve_bon"),
    # LA PART DE POPULATION SATURE, LA DISTANCE NON. Quatre sections sont à
    # 100 % parce que la section ENTIÈRE est à moins de deux kilomètres d'une
    # voie : le seuil du référentiel, taillé pour des statistiques
    # nationales, ne discrimine plus à l'échelle d'une section de vingt
    # kilomètres carrés. Ces deux mesures-là discriminent, et elles disent la
    # même chose sans plafonner.
    ("acces", "dist_med_m", "sat_m_dist", "acces", "dist_med_m", " m", 0,
     "eleve_mauvais"),
    ("acces", "aire_2km_pct", "sat_m_aire2", "acces", "aire_2km_pct", "%", 1,
     "eleve_bon"),
    ("acces", "dist_med_classe_m", "sat_m_dist_c", "acces",
     "dist_med_classe_m", " m", 0, "eleve_mauvais"),
    # --- LE SOL, ce qu'il perd et ce qui est déjà dégradé. Un modèle, pas une
    # mesure : chaque facteur du RUSLE porte sa propre incertitude, et elles
    # se multiplient. Les mesures brutes qui le composent — pente, pluie,
    # érodibilité — sont montrées à côté, parce qu'un résultat de modèle sans
    # ses entrées ne se discute pas.
    ("sol", "erosion_t_ha_an", "sat_m_erosion", "sol", "erosion_t_ha_an",
     " t/ha/an", 1, "eleve_mauvais"),
    ("sol", "degrade_pct", "sat_m_degrade", "deg", "degrade_pct", "%", 1,
     "eleve_mauvais"),
    ("sol", "erosion_mediane", "sat_m_erosion_med", "sol", "erosion_mediane",
     " t/ha/an", 1, "eleve_mauvais"),
    ("sol", "part_sup_10", "sat_m_ero10", "sol", "part_sup_10", "%", 1,
     "eleve_mauvais"),
    ("sol", "couvert_perdu_pct", "sat_m_perdu", "deg", "couvert_perdu_pct",
     "%", 1, "eleve_mauvais"),
    ("sol", "pente_moy_deg", "sat_m_pente", "sol", "pente_moy_deg", "°", 1,
     "eleve_mauvais"),
    ("sol", "K_moy", "sat_m_k", "sol", "K_moy", "", 3, "eleve_mauvais"),
    # --- LA MER DEVANT LA SECTION. Les seules mesures de cet écran qui ne
    # décrivent pas le sol de la section mais l'eau qui la borde : elles se
    # lisent donc autrement, et une section intérieure n'y figure pas — elle
    # n'a pas une chlorophylle nulle, elle n'a pas la question.
    ("marin", "chl_a", "sat_m_chl", "chl", "chl_a", " mg/m³", 3,
     "eleve_mauvais"),
    ("marin", "chl_a_evolution_pct", "sat_m_chl_evo", "chl",
     "chl_a_evolution_pct", "%", 1, "eleve_mauvais"),
    ("marin", "chl_a_debut", "sat_m_chl_debut", "chl", "chl_a_debut",
     " mg/m³", 3, "eleve_mauvais"),
    ("marin", "chl_a_saison_pluies", "sat_m_chl_pluies", "chl",
     "chl_a_saison_pluies", " mg/m³", 3, "eleve_mauvais"),
    ("marin", "chl_a_saison_seche", "sat_m_chl_seche", "chl",
     "chl_a_saison_seche", " mg/m³", 3, "eleve_mauvais"),
    ("marin", "chl_a_mediane", "sat_m_chl_med", "chl", "chl_a_mediane",
     " mg/m³", 3, "eleve_mauvais"),
    ("marin", "herbier_ha", "sat_m_herbier", "herb", "surface_ha", "ha", 2,
     "eleve_bon"),
    ("marin", "herbier_polygones", "sat_m_herbier_n", "herb", "polygones",
     "", 0, "eleve_bon"),
    # --- LE GUICHET LE PLUS PROCHE. Le compte d'agences vaut zéro dans les
    # dix sections, et un indicateur qui ne distingue rien ne dit pourtant
    # pas rien : c'est la DISTANCE qui porte l'information, et elle est ici
    # à côté de lui plutôt que dans une note qu'on n'ouvre pas.
    ("finance", "guichets_p100k", "sat_m_guichets", "fin", "guichets_p100k",
     "", 2, "eleve_bon"),
    ("finance", "dist_guichet_km", "sat_m_dist_guichet", "fin",
     "dist_guichet_km", " km", 1, "eleve_mauvais"),
    ("finance", "dist_point_financier_km", "sat_m_dist_fin", "fin",
     "dist_point_financier_km", " km", 1, "eleve_mauvais"),
    ("finance", "adultes_estimes", "sat_m_adultes", "fin",
     "adultes_estimes", "", 0, "eleve_bon"),
    ("finance", "poi_cartographies", "sat_m_poi", "fin",
     "poi_cartographies", "", 0, "eleve_bon"),
]

# LA MESURE BRUTE ET SA NOTE SONT LE MÊME OBJET, VU DEUX FOIS. Le référentiel
# porte, pour une partie de ces mesures, un barème publié, une note de source
# et une phrase de lecture : les cacher dans un autre écran obligeait à savoir
# qu'ils existaient. La table dit quelle ligne du référentiel correspond à
# quelle mesure ; celles qui n'y figurent pas restent des mesures brutes, et
# l'écran ne leur invente pas de note.
LIGNES = {
    "ndvi": 33, "ndmi": 34, "ndwi": 35, "vhi": 36, "evi": 37, "savi": 38,
    "vari": 39, "fvc": 40, "lst_anomalie": 41, "tci": 42,
    "pci_mam": 43, "aai_mam": 44, "ratio_mam": 45, "spi_mam": 46,
    "taux_annuel_net": 54, "ndti": 63,
    "pc_d": 64, "pc_d2": 65, "iic": 66, "iic_d": 67,
    "densite_lisiere_m_ha": 68, "ratio_core_move": 69, "core_pct": 70,
    "acces_axe": 8, "erosion_t_ha_an": 59, "degrade_pct": 60,
    "chl_a": 61, "herbier_ha": 58, "guichets_p100k": 73,
}

# LES ONGLETS, DANS L'ORDRE OÙ ON LES PARCOURT : ce qui couvre le sol, puis
# ce qui l'arrose, puis ce qui l'assèche.
CATEGORIES = ("foret", "frag", "sol", "vege", "eau", "marin", "pluie",
              "saison", "temp", "aridite", "acces", "finance")


TEXTES = {
    "sat_titre": {"en": "Satellite measurements",
                  "fr": "Mesures satellitaires"},
    # LE COMPTE EST CALCULÉ, PAS ÉCRIT EN LETTRES. « Cinquante-six mesures »
    # était juste le jour où la phrase a été écrite ; onze mesures de forme
    # d'habitat sont arrivées depuis, et la page annonçait toujours
    # cinquante-six.
    "sat_intro": {
        "en": "{n} measurements from imagery and open geodata for each of "
              "the ten communal sections: forest, the shape of the habitat, "
              "vegetation, surface water, the sea offshore, rainfall since "
              "1981, the rainy season, surface temperature since 2001, the "
              "water balance, road access and financial counters. These "
              "are raw measurements: where the "
              "framework publishes a scale, the score sits under the "
              "chart.",
        "fr": "{n} mesures tirées de l'imagerie et de données "
              "géographiques ouvertes, pour chacune des dix sections "
              "communales : forêt, forme de l'habitat, végétation, eau de "
              "surface, mer au large, pluie depuis 1981, saison des pluies, "
              "température de surface depuis 2001, bilan hydrique, accès "
              "routier et guichets financiers. Ce "
              "sont des mesures brutes : là où le référentiel publie un "
              "barème, la note est sous le graphique."},
    "sat_source": {"en": "Source", "fr": "Source"},
    "sat_mesure": {"en": "Measurement", "fr": "Mesure"},
    "sat_annee": {"en": "Year", "fr": "Année"},
    "sat_ventile": {
        "en": "A pixel has no household: these measurements break down by "
              "communal section and by nothing else. The sex, age and wealth "
              "filters do not apply to them.",
        "fr": "Un pixel n'a pas de ménage : ces mesures se ventilent par "
              "section communale et par rien d'autre. Les filtres de sexe, "
              "d'âge et de richesse ne s'y appliquent pas."},
    "sat_ens": {"en": "Whole territory", "fr": "Territoire entier"},
    "sat_col_sec": {"en": "Communal section", "fr": "Section communale"},
    "sat_format": {"en": "Chart", "fr": "Graphique"},
    "sat_barres": {"en": "Bar chart", "fr": "Histogramme"},
    "sat_carte": {"en": "Map", "fr": "Carte"},
    "sat_tableau": {"en": "Table", "fr": "Tableau"},
    "sat_indispo": {
        "en": "This measurement is not available in the delivered data.",
        "fr": "Cette mesure n'est pas disponible dans les données livrées."},

    "sat_m_couvert": {"en": "Forest cover, {a} (% of area)",
                      "fr": "Couverture forestière, {a} (% de la surface)"},
    "sat_m_couvert2000": {"en": "Forest cover, {a} (% of area)",
                          "fr": "Couverture forestière, {a} (% de la surface)"},
    "sat_m_perte": {"en": "Forest lost since {a} (% of the {a} forest)",
                    "fr": "Forêt perdue depuis {a} (% de la forêt de {a})"},
    "sat_m_perte_ha": {"en": "Forest lost since {a} (hectares)",
                       "fr": "Forêt perdue depuis {a} (hectares)"},
    "sat_m_taux": {"en": "Net annual rate of forest change (%/year)",
                   "fr": "Taux annuel net d'évolution forestière (%/an)"},
    "sat_m_choc": {
        "en": "Share of the loss concentrated in its worst single year (%)",
        "fr": "Part de la perte concentrée sur sa pire année (%)"},
    "sat_m_ndvi": {"en": "NDVI — vegetation vigour, {a}",
                   "fr": "NDVI — vigueur de la végétation, {a}"},
    "sat_m_ndvi_d": {"en": "NDVI change, {d}",
                     "fr": "Évolution du NDVI, {d}"},
    "sat_m_ndmi": {"en": "NDMI — vegetation moisture, {a}",
                   "fr": "NDMI — humidité de la végétation, {a}"},
    "sat_m_evi": {"en": "EVI — enhanced vegetation index, {a}",
                  "fr": "EVI — indice de végétation amélioré, {a}"},
    "sat_m_fvc": {"en": "FVC — fraction of ground covered by vegetation, {a}",
                  "fr": "FVC — fraction du sol couverte de végétation, {a}"},
    "sat_m_ndwi": {"en": "NDWI — water index, {a}",
                   "fr": "NDWI — indice d'eau, {a}"},

    # ---- les onglets de catégorie
    "sat_c_foret": {"en": "Forest", "fr": "Forêt"},
    "sat_c_vege": {"en": "Vegetation", "fr": "Végétation"},
    "sat_c_eau": {"en": "Surface water", "fr": "Eau de surface"},
    "sat_c_pluie": {"en": "Rainfall", "fr": "Pluie"},
    "sat_c_saison": {"en": "Rainy season", "fr": "Saison des pluies"},
    "sat_c_temp": {"en": "Temperature", "fr": "Température"},
    "sat_c_aridite": {"en": "Water balance", "fr": "Bilan hydrique"},
    "sat_c_sol": {"en": "Soil", "fr": "Sol"},
    "sat_c_marin": {"en": "The sea offshore", "fr": "La mer au large"},
    "sat_c_finance": {"en": "Financial counters",
                      "fr": "Guichets financiers"},
    "sat_cd_finance": {
        "en": "Bank branches and ATMs per 100,000 adults, and how far the "
              "nearest one is",
        "fr": "Agences et distributeurs pour 100 000 adultes, et la "
              "distance au plus proche"},
    "sat_m_guichets": {
        "en": "Bank branches and ATMs per 100,000 adults (SDG 8.10.1)",
        "fr": "Agences et distributeurs pour 100 000 adultes (ODD 8.10.1)"},
    "sat_m_dist_guichet": {
        "en": "Distance to the nearest branch or ATM",
        "fr": "Distance à l'agence ou au distributeur le plus proche"},
    "sat_m_dist_fin": {
        "en": "Distance to the nearest financial counter of any kind",
        "fr": "Distance au premier point financier, quel qu'il soit"},
    "sat_m_adultes": {
        "en": "Estimated adult population of the section",
        "fr": "Population adulte estimée de la section"},
    "sat_m_poi": {
        "en": "Ordinary points of interest mapped in the section (control)",
        "fr": "Points d'intérêt ordinaires cartographiés dans la section "
              "(contrôle)"},
    "sat_m_chl": {
        "en": "Chlorophyll-a offshore, 2021-2025 average",
        "fr": "Chlorophylle-a au large, moyenne 2021-2025"},
    "sat_m_chl_evo": {
        "en": "Change in chlorophyll-a, 2012-2016 to 2021-2025",
        "fr": "Évolution de la chlorophylle-a, 2012-2016 à 2021-2025"},
    "sat_m_chl_debut": {
        "en": "Chlorophyll-a offshore, 2012-2016 average",
        "fr": "Chlorophylle-a au large, moyenne 2012-2016"},
    "sat_m_chl_pluies": {
        "en": "Chlorophyll-a in the rainy months, May to October",
        "fr": "Chlorophylle-a aux mois pluvieux, mai à octobre"},
    "sat_m_chl_seche": {
        "en": "Chlorophyll-a in the dry months, December to April",
        "fr": "Chlorophylle-a aux mois secs, décembre à avril"},
    "sat_m_chl_med": {
        "en": "Chlorophyll-a, median cell",
        "fr": "Chlorophylle-a, maille médiane"},
    "sat_m_herbier": {
        "en": "Mapped seagrass area offshore",
        "fr": "Surface d'herbiers marins cartographiée au large"},
    "sat_m_herbier_n": {
        "en": "Number of mapped seagrass patches",
        "fr": "Nombre de taches d'herbier cartographiées"},
    "sat_cd_sol": {
        "en": "Soil lost each year, and the share of ground already degraded",
        "fr": "Ce que le sol perd chaque année, et la part déjà dégradée"},
    "sat_m_erosion": {"en": "Soil loss, RUSLE, section average",
                      "fr": "Perte de sol, RUSLE, moyenne de la section"},
    "sat_m_erosion_med": {"en": "Soil loss, median pixel",
                          "fr": "Perte de sol, pixel médian"},
    "sat_m_ero10": {
        "en": "Share of the section losing more than 10 t/ha/yr",
        "fr": "Part de la section qui perd plus de 10 t/ha/an"},
    "sat_m_degrade": {"en": "Degraded land, SDG 15.3.1 (lower bound)",
                      "fr": "Terres dégradées, SDG 15.3.1 (minorant)"},
    "sat_m_perdu": {"en": "Tree cover lost since 2000, share of the section",
                    "fr": "Couvert arboré perdu depuis 2000, part de la "
                          "section"},
    "sat_m_pente": {"en": "Mean slope", "fr": "Pente moyenne"},
    "sat_m_k": {"en": "Soil erodibility K, mean",
                "fr": "Érodibilité du sol K, moyenne"},
    "sat_c_acces": {"en": "Road access", "fr": "Accès routier"},
    "sat_cd_acces": {
        "en": "Population within 2 km of a road, distance to the nearest "
              "one, and what the definition of a road changes",
        "fr": "Population à moins de 2 km d'une route, distance à la plus "
              "proche, et ce que change la définition d'une route"},
    "sat_m_acces": {
        "en": "Population within 2 km of a drivable road, tracks excluded",
        "fr": "Population à moins de 2 km d'un axe carrossable, pistes "
              "exclues"},
    "sat_m_acces_p": {
        "en": "Same, counting tracks as roads",
        "fr": "La même, en comptant les pistes comme des routes"},
    "sat_m_acces_c": {
        "en": "Same, classified network only",
        "fr": "La même, réseau classé seulement"},
    "sat_m_pop": {"en": "Section population, WorldPop 2020",
                  "fr": "Population de la section, WorldPop 2020"},
    "sat_m_dist": {
        "en": "Median distance from an inhabitant to the nearest road",
        "fr": "Distance médiane d'un habitant à la route la plus proche"},
    "sat_m_dist_c": {
        "en": "Median distance to the classified network",
        "fr": "Distance médiane au réseau classé"},
    "sat_m_aire2": {
        "en": "Share of the section's AREA within 2 km of a road",
        "fr": "Part de la SUPERFICIE de la section à moins de 2 km d'une "
              "route"},
    "sat_c_frag": {"en": "Habitat shape", "fr": "Forme de l'habitat"},
    "sat_cd_frag": {
        "en": "How much habitat is left, in how many pieces, and whether "
              "those pieces connect",
        "fr": "Ce qu'il reste d'habitat, en combien de morceaux, et si ces "
              "morceaux se rejoignent"},
    # LES INTITULÉS DISENT LA GRANDEUR, PAS SON SIGLE. « PC(d*) » ne veut rien
    # dire à qui ouvre la page ; « probabilité que deux points d'habitat
    # soient reliés » se lit.
    "sat_m_habitat": {"en": "Natural habitat, share of the section",
                      "fr": "Habitat naturel, part de la section"},
    "sat_m_taches": {"en": "Habitat patches, count",
                     "fr": "Taches d'habitat, nombre"},
    "sat_m_lisiere": {"en": "Edge density, metres of habitat edge per hectare",
                      "fr": "Densité de lisière, mètres de bordure d'habitat "
                            "par hectare"},
    "sat_m_core": {"en": "Interior habitat, share of the section",
                   "fr": "Habitat intérieur, part de la section"},
    "sat_m_core_ha": {"en": "Interior habitat, area",
                      "fr": "Habitat intérieur, surface"},
    "sat_m_ratio": {"en": "Habitat that is core or corridor, share of all "
                          "habitat",
                    "fr": "Habitat de cœur ou de corridor, part de tout "
                          "l'habitat"},
    "sat_m_pc": {"en": "Functional connectivity, PC at 1 000 m",
                 "fr": "Connectivité fonctionnelle, PC à 1 000 m"},
    "sat_m_pc2": {"en": "Connectivity for low mobility, PC at 500 m",
                  "fr": "Connectivité pour faible mobilité, PC à 500 m"},
    "sat_m_iic": {"en": "Structural connectivity, IIC between touching "
                        "patches",
                  "fr": "Connectivité structurelle, IIC entre taches "
                        "jointives"},
    "sat_m_iic_d": {"en": "Structural connectivity, IIC at 1 000 m",
                    "fr": "Connectivité structurelle, IIC à 1 000 m"},
    "sat_m_hab_ha": {"en": "Natural habitat, area",
                     "fr": "Habitat naturel, surface"},
    "sat_cd_foret": {"en": "Cover, loss and its pace",
                     "fr": "Couvert, perte et rythme de la perte"},
    "sat_cd_vege": {"en": "Greenness, moisture and their year-to-year swing",
                    "fr": "Verdeur, humidité et leur écart d'une année à "
                          "l'autre"},
    "sat_cd_eau": {"en": "Open water and its turbidity",
                   "fr": "Eau libre et sa turbidité"},
    "sat_cd_marin": {
        "en": "Chlorophyll-a in the water offshore since 2012, and the "
              "seagrass mapped there",
        "fr": "La chlorophylle-a de l'eau au large depuis 2012, et les "
              "herbiers qui y sont cartographiés"},
    "sat_cd_pluie": {"en": "Annual totals, 1981 to 2025, against the normal",
                     "fr": "Cumuls annuels, 1981 à 2025, rapportés à la "
                           "normale"},
    "sat_cd_saison": {"en": "Spring and autumn rains, dry spells and onset",
                      "fr": "Pluies de printemps et d'automne, jours secs et "
                            "installation"},
    "sat_cd_temp": {"en": "Land surface temperature, day and night, 2001 to "
                          "2025",
                    "fr": "Température de surface, jour et nuit, 2001 à 2025"},
    "sat_cd_aridite": {"en": "Evapotranspiration against rainfall",
                       "fr": "Évapotranspiration rapportée à la pluie"},

    # ---- végétation
    "sat_m_savi": {"en": "SAVI — soil-adjusted vegetation index, {a}",
                   "fr": "SAVI — indice de végétation ajusté au sol, {a}"},
    "sat_m_vari": {"en": "VARI — atmospherically resistant index, {a}",
                   "fr": "VARI — indice résistant à l'atmosphère, {a}"},
    "sat_m_var_ndvi": {
        "en": "NDVI year-to-year swing (standard deviation of the series)",
        "fr": "Écart du NDVI d'une année à l'autre (écart-type de la série)"},
    "sat_m_var_ndmi": {
        "en": "NDMI year-to-year swing (standard deviation of the series)",
        "fr": "Écart du NDMI d'une année à l'autre (écart-type de la série)"},
    "sat_m_vhi": {"en": "VHI — vegetation health index",
                  "fr": "VHI — indice de santé de la végétation"},
    "sat_m_vci": {"en": "VCI — vegetation condition index",
                  "fr": "VCI — indice de condition de la végétation"},

    # ---- eau de surface
    "sat_m_frac_eau": {"en": "Share of the section under open water, {a} (%)",
                       "fr": "Part de la section en eau libre, {a} (%)"},
    "sat_m_eau_ha": {"en": "Open water (hectares)",
                     "fr": "Eau libre (hectares)"},
    "sat_m_ndti": {"en": "NDTI — water turbidity, {a}",
                   "fr": "NDTI — turbidité de l'eau, {a}"},
    "sat_m_var_eau": {
        "en": "Year-to-year swing of the water surface",
        "fr": "Écart de la surface en eau d'une année à l'autre"},

    # ---- pluie
    "sat_m_pl_courante": {"en": "Rainfall of the assessed year (mm)",
                          "fr": "Pluie de l'année évaluée (mm)"},
    "sat_m_pl_normale": {"en": "Normal annual rainfall, 1991–2020 (mm)",
                         "fr": "Normale pluviométrique annuelle, 1991-2020 "
                               "(mm)"},
    "sat_m_pl_ratio": {"en": "Rainfall against the normal (%)",
                       "fr": "Pluie rapportée à la normale (%)"},
    "sat_m_pl_spi": {"en": "SPI — standardised precipitation index",
                     "fr": "SPI — indice de précipitation standardisé"},
    "sat_m_pl_pci": {"en": "PCI — precipitation condition index",
                     "fr": "PCI — indice de condition pluviométrique"},
    "sat_m_pl_aai": {"en": "Anomalous aridity index",
                     "fr": "Indice d'aridité anormale"},
    "sat_m_pl_serie": {"en": "Annual rainfall, {a} (mm)",
                       "fr": "Pluie annuelle, {a} (mm)"},
    "sat_m_pl_min": {"en": "Driest year on record since 1981 (mm)",
                     "fr": "Année la plus sèche depuis 1981 (mm)"},
    "sat_m_pl_max": {"en": "Wettest year on record since 1981 (mm)",
                     "fr": "Année la plus arrosée depuis 1981 (mm)"},

    # ---- saison des pluies
    "sat_m_sa_mam": {"en": "Spring rains, March to May, current (mm)",
                     "fr": "Pluies de printemps, mars à mai, courantes (mm)"},
    "sat_m_sa_mam_n": {"en": "Spring rains, normal 1991–2020 (mm)",
                       "fr": "Pluies de printemps, normale 1991-2020 (mm)"},
    "sat_m_sa_aso": {"en": "Autumn rains, August to October, current (mm)",
                     "fr": "Pluies d'automne, août à octobre, courantes (mm)"},
    "sat_m_sa_spi": {"en": "SPI of the spring campaign",
                     "fr": "SPI de la campagne de printemps"},
    "sat_m_sa_secs": {"en": "Dry days in the spring campaign",
                      "fr": "Jours secs dans la campagne de printemps"},
    "sat_m_sa_secs_an": {"en": "Longest dry spell in the year (days)",
                         "fr": "Plus longue séquence sèche de l'année "
                               "(jours)"},
    "sat_m_sa_j50": {"en": "Days above 50 mm of rain in the year",
                     "fr": "Jours à plus de 50 mm de pluie dans l'année"},
    "sat_m_sa_install": {
        "en": "Onset of the rains, recent period (day of year)",
        "fr": "Installation des pluies, période récente (jour de l'année)"},
    "sat_m_sa_decalage": {
        "en": "Shift in the onset of the rains, recent minus older (days)",
        "fr": "Décalage de l'installation des pluies, récent moins ancien "
              "(jours)"},
    "sat_m_sa_ratees": {"en": "Failed onsets since 1981 (count)",
                        "fr": "Installations ratées depuis 1981 (nombre)"},
    "sat_m_sa_serie": {"en": "Spring rains, {a} (mm)",
                       "fr": "Pluies de printemps, {a} (mm)"},

    # ---- température
    "sat_m_t_courant": {"en": "Dry-season surface temperature, current (°C)",
                        "fr": "Température de surface en saison sèche, "
                              "courante (°C)"},
    "sat_m_t_normale": {"en": "Dry-season surface temperature, normal (°C)",
                        "fr": "Température de surface en saison sèche, "
                              "normale (°C)"},
    "sat_m_t_anomalie": {"en": "Temperature anomaly against the normal (%)",
                         "fr": "Anomalie de température par rapport à la "
                               "normale (%)"},
    "sat_m_t_an": {"en": "Annual mean surface temperature, day (°C)",
                   "fr": "Température de surface moyenne annuelle, jour "
                         "(°C)"},
    "sat_m_t_nuit": {"en": "Annual mean surface temperature, night (°C)",
                     "fr": "Température de surface moyenne annuelle, nuit "
                           "(°C)"},
    "sat_m_t_ampli": {"en": "Day-night temperature range (°C)",
                      "fr": "Amplitude thermique jour-nuit (°C)"},
    "sat_m_t_max": {"en": "Hottest season on record since 2001 (°C)",
                    "fr": "Saison la plus chaude depuis 2001 (°C)"},
    "sat_m_t_tci": {"en": "TCI — temperature condition index",
                    "fr": "TCI — indice de condition thermique"},
    "sat_m_t_serie": {"en": "Dry-season surface temperature, {a} (°C)",
                      "fr": "Température de surface en saison sèche, {a} "
                            "(°C)"},
    "sat_m_t_serie_an": {"en": "Annual mean surface temperature, {a} (°C)",
                         "fr": "Température de surface moyenne annuelle, {a} "
                               "(°C)"},

    # ---- bilan hydrique
    "sat_m_ar_indice": {"en": "Aridity index (rainfall over demand)",
                        "fr": "Indice d'aridité (pluie rapportée à la "
                              "demande)"},
    "sat_m_ar_et": {"en": "Actual evapotranspiration (mm/year)",
                    "fr": "Évapotranspiration réelle (mm/an)"},
    "sat_m_ar_pet": {"en": "Potential evapotranspiration (mm/year)",
                     "fr": "Évapotranspiration potentielle (mm/an)"},
    "sat_m_ar_pluie": {"en": "Rainfall used in the balance (mm/year)",
                       "fr": "Pluie retenue dans le bilan (mm/an)"},

    "sat_m_sa_pci": {"en": "PCI of the spring campaign",
                     "fr": "PCI de la campagne de printemps"},
    "sat_m_sa_aai": {"en": "Anomalous aridity of the spring campaign",
                     "fr": "Aridité anormale de la campagne de printemps"},
    "sat_m_sa_ratio": {"en": "Spring rains against their normal (%)",
                       "fr": "Pluies de printemps rapportées à leur normale "
                             "(%)"},

    # ---- ce que le référentiel dit d'une mesure
    "sat_ref_t": {"en": "Source, method and how to read it",
                  "fr": "Source, méthode et lecture"},
    "sat_ref_src": {"en": "Where it comes from, and how it was attributed to "
                          "each communal section",
                    "fr": "D'où elle vient, et comment elle a été attribuée à "
                          "chaque section communale"},
    "sat_ref_bar": {"en": "The published scale, and the score it gives",
                    "fr": "Le barème publié, et la note qu'il donne"},
    "sat_ref_lire": {"en": "How to read it", "fr": "Comment la lire"},
    "sat_ref_note": {"en": "APRI score", "fr": "Note APRI"},
    "sat_ref_grade": {
        "en": "What the scale grades is the referential\u2019s own quantity, "
              "«\u00a0{n}\u00a0», which is not always the level drawn above: "
              "several vegetation scales grade a change between two windows "
              "rather than the value of a year.",
        "fr": "Ce que le barème note est la grandeur du référentiel, "
              "«\u00a0{n}\u00a0», qui n\u2019est pas toujours le niveau "
              "dessiné plus haut : plusieurs barèmes de végétation notent une "
              "variation entre deux fenêtres plutôt que la valeur d\u2019une "
              "année."},
    "sat_ref_note_x": {
        "en": "The scale above turns this raw measurement into a mark out of "
              "ten. It is the same number that enters the resilience index; "
              "here it sits beside the measurement it comes from.",
        "fr": "Le barème ci-dessus transforme cette mesure brute en note sur "
              "dix. C'est le nombre qui entre dans l'indice de résilience ; "
              "il est ici à côté de la mesure dont il sort."},
    "sat_ref_zonal": {
        "en": "Every satellite figure is a zonal statistic: the pixels are "
              "averaged over the polygon of the communal section, and over "
              "nothing else. A section is therefore described by its own "
              "ground, not by the nearest station.",
        "fr": "Chaque chiffre satellitaire est une statistique zonale : les "
              "pixels sont moyennés sur le polygone de la section communale, "
              "et sur rien d'autre. Une section est donc décrite par son "
              "propre sol, non par la station la plus proche."},
    "sat_ref_absent": {
        "en": "This measurement carries no published scale: it is delivered "
              "raw, and enters no score.",
        "fr": "Cette mesure ne porte pas de barème publié : elle est livrée "
              "brute, et n'entre dans aucun score."},

    "sat_calc_t": {"en": "How the figure is computed",
                   "fr": "Comment le chiffre est calculé"},
    "sat_calc_frag": {
        "en": "ESA WorldCover 2021 gives the land cover of every 10 m pixel. "
              "Natural habitat is taken as tree cover, shrubland, herbaceous "
              "wetland and mangrove; grassland is excluded, because here it "
              "is grazed and degraded and counting it would make every "
              "section look connected. The section is reprojected to metres "
              "(UTM 18N), habitat pixels are grouped into patches by "
              "eight-neighbour connectivity, and patches under 0.1 ha are "
              "dropped. Edge density counts every habitat / non-habitat "
              "boundary between two pixels, ten metres each, divided by the "
              "area of the section; the section's own outline is not counted "
              "as edge, since nothing is known beyond it. Interior habitat "
              "is what survives a 100 m erosion, the usual edge depth for "
              "fragmented tropical forest. Distances between patches are "
              "edge to edge, in metres. IIC is the integral index of "
              "connectivity over the patch graph, with links between "
              "touching patches for the unconstrained version and links "
              "under 1 000 m for the constrained one; PC uses a dispersal "
              "probability of exp(-k d) with k set so that the probability "
              "is one half at the dispersal distance, and the maximum "
              "product path between every pair of patches. That dispersal "
              "distance, 1 000 m, is the one biological choice in the whole "
              "chain and it must be set per guild: a dragonfly, a bird and a "
              "freshwater fish do not cross the same gaps.",
        "fr": "ESA WorldCover 2021 donne la couverture du sol de chaque pixel "
              "de 10 m. L'habitat naturel retenu est l'arbre, l'arbuste, la "
              "zone humide herbacée et la mangrove ; la prairie est exclue, "
              "parce qu'elle est ici du pâturage dégradé et que la compter "
              "rendrait toutes les sections connectées. La section est "
              "reprojetée en mètres (UTM 18N), les pixels d'habitat sont "
              "regroupés en taches par voisinage à huit, et les taches de "
              "moins de 0,1 ha sont écartées. La densité de lisière compte "
              "chaque frontière habitat / non-habitat entre deux pixels, dix "
              "mètres chacune, divisée par la surface de la section ; le "
              "contour de la section n'est pas compté comme lisière, "
              "puisqu'on ne sait rien de ce qu'il y a au-delà. L'habitat "
              "intérieur est ce qui survit à une érosion de 100 m, la "
              "profondeur de lisière usuelle en forêt tropicale fragmentée. "
              "Les distances entre taches sont de bord à bord, en mètres. "
              "L'IIC est l'indice intégral de connectivité sur le graphe des "
              "taches, avec des liens entre taches jointives pour la version "
              "non contrainte et des liens sous 1 000 m pour la version "
              "contrainte ; le PC utilise une probabilité de dispersion en "
              "exp(-k d), k étant réglé pour que la probabilité vaille un "
              "demi à la distance de dispersion, et le chemin de probabilité "
              "maximale entre chaque paire de taches. Cette distance de "
              "dispersion, 1 000 m, est le seul choix biologique de toute la "
              "chaîne et elle doit être fixée par guilde : une libellule, un "
              "oiseau et un poisson d'eau douce ne franchissent pas les "
              "mêmes ruptures."},
    # LA PHRASE DE STATISTIQUE ZONALE NE VAUT PAS POUR CES MESURES, et la
    # laisser aurait été un contresens : on ne fait pas la moyenne de pixels,
    # on construit des taches. La vraie limite est ailleurs, et elle est dite.
    "sat_ref_zonal_frag": {
        "en": "These figures are not an average of pixels. The patches are "
              "built inside the section, and the statistics computed on "
              "them, so a habitat patch that straddles a boundary is cut at "
              "that boundary: connectivity across two neighbouring sections "
              "is not counted. Each section is therefore described as if it "
              "were alone, which understates connectivity for the sections "
              "that adjoin one another.",
        "fr": "Ces chiffres ne sont pas une moyenne de pixels. Les taches "
              "sont construites à l'intérieur de la section et les "
              "statistiques calculées sur elles : une tache d'habitat à "
              "cheval sur une limite est donc coupée à cette limite, et la "
              "connectivité entre deux sections voisines n'est pas comptée. "
              "Chaque section est décrite comme si elle était seule, ce qui "
              "sous-estime la connectivité des sections mitoyennes."},
    "sat_ref_zonal_marin": {
        "en": "This figure is not an average over the section's ground: it "
              "is measured at sea. Each section is given the sea cells "
              "lying within five kilometres of its territory — five, "
              "because the cell is four across. Two neighbouring sections "
              "may therefore share the same water, and they do: the sea off "
              "Tiburon does not divide into parcels. A section with no "
              "coast simply does not appear here — it has no chlorophyll "
              "reading, which is not the same as a reading of zero.",
        "fr": "Ce chiffre n'est pas une moyenne sur le sol de la section : "
              "il est mesuré en mer. Chaque section reçoit les mailles de "
              "mer situées à moins de cinq kilomètres de son territoire — "
              "cinq, parce que la maille en fait quatre. Deux sections "
              "voisines peuvent donc partager la même eau, et elles la "
              "partagent : la mer devant Tiburon ne se découpe pas en "
              "parcelles. Une section sans côte ne figure pas ici — elle "
              "n'a pas de mesure de chlorophylle, ce qui n'est pas la même "
              "chose qu'une mesure nulle."},
    "sat_ref_zonal_fin": {
        "en": "This figure counts what stands INSIDE the section, and it "
              "stands at zero in all ten: every branch and ATM mapped in "
              "the two departments is in Les Cayes, Jérémie, Camp-Perrin "
              "or Aquin, none of them inside a studied section. A zero can "
              "mean « there is nothing » or « nobody mapped it », so the "
              "control is published beside it: the ordinary points of "
              "interest — shops, schools, pharmacies, markets — mapped in "
              "each section. Seventy-eight across the ten, from one to "
              "twenty-six: the map is not blank, but it is thin, and the "
              "zero is a probable absence rather than a certified one. "
              "What separates the ten sections is the distance to the "
              "nearest counter, from 1.7 km to 39.2 km, and it carries no "
              "score because the referential does not grade it.",
        "fr": "Ce chiffre compte ce qui se trouve DANS la section, et il "
              "vaut zéro dans les dix : toutes les agences et tous les "
              "distributeurs cartographiés des deux départements sont aux "
              "Cayes, à Jérémie, à Camp-Perrin ou à Aquin, aucun dans une "
              "section étudiée. Un zéro peut vouloir dire « il n'y a "
              "rien » ou « personne ne l'a cartographié » : le contrôle "
              "est donc publié à côté, ce sont les points d'intérêt "
              "ordinaires — commerces, écoles, pharmacies, marchés — "
              "cartographiés dans chaque section. Soixante-dix-huit pour "
              "les dix, de un à vingt-six : la carte n'est pas vierge, "
              "mais elle est mince, et le zéro est une absence probable "
              "plutôt qu'une absence certifiée. Ce qui distingue les dix "
              "sections, c'est la distance au guichet le plus proche, de "
              "1,7 km à 39,2 km, et elle ne porte pas de note parce que le "
              "référentiel ne la note pas."},
    "sat_calc_fin": {
        "en": "SDG 8.10.1 counts COMMERCIAL BANK BRANCHES AND ATMs per "
              "100,000 adults: an infrastructure statistic, not a question "
              "put to households. What the survey knows — who holds an "
              "account — is SDG 8.10.2, and that is line 72 of the "
              "referential, already computed from the answers. The two do "
              "not replace each other: one says whether people have an "
              "account, the other whether there is a counter where they "
              "live. Positions come from OpenStreetMap, the only open "
              "source that gives them; money-transfer offices are "
              "recorded but left out of the scored count, since the "
              "indicator names branches and ATMs. Adults are estimated at "
              "65 % of the section's WorldPop population. AND THE ZERO "
              "DOES NOT MEAN THERE IS NO FINANCIAL LIFE: 369 surveyed "
              "households belong to a savings mutual or a community bank, "
              "and 350 would turn to a solidarity mutual for credit. Those "
              "are neither branches nor ATMs, and the scale decides that, "
              "not us.",
        "fr": "L'ODD 8.10.1 compte des AGENCES DE BANQUE COMMERCIALE ET "
              "DES DISTRIBUTEURS pour 100 000 adultes : une statistique "
              "d'infrastructure, pas une question posée aux ménages. Ce "
              "que l'enquête sait — qui possède un compte — est l'ODD "
              "8.10.2, et c'est la ligne 72 du référentiel, déjà calculée "
              "depuis les réponses. Les deux ne se remplacent pas : l'une "
              "dit si les gens ont un compte, l'autre s'il existe un "
              "guichet là où ils vivent. Les positions viennent "
              "d'OpenStreetMap, seule source ouverte à les donner ; les "
              "bureaux de transfert d'argent sont relevés mais laissés "
              "hors du compte noté, l'indicateur nommant les agences et "
              "les distributeurs. Les adultes sont estimés à 65 % de la "
              "population WorldPop de la section. ET LE ZÉRO NE VEUT PAS "
              "DIRE QU'IL N'Y A PAS DE VIE FINANCIÈRE : 369 ménages "
              "enquêtés sont membres d'une mutuelle d'épargne ou d'une "
              "banque communautaire, et 350 se tourneraient vers une "
              "mutuelle de solidarité pour un crédit. Ce ne sont ni des "
              "agences ni des distributeurs, et c'est le barème qui en "
              "décide, pas nous."},
    "sat_src_fin": {
        "en": "{s}. {n} financial points recorded on the peninsula, adults "
              "taken as {a} % of the WorldPop total, {p} control points of "
              "interest mapped across the ten sections.",
        "fr": "{s}. {n} points financiers relevés sur la presqu'île, "
              "adultes pris à {a} % de la population WorldPop, {p} points "
              "d'intérêt de contrôle cartographiés dans les dix sections."},
    "sat_p_guichets_p100k": {
        "en": "{s} has {v} branches or ATMs per 100,000 adults.",
        "fr": "{s} compte {v} agence ou distributeur pour 100 000 "
              "adultes."},
    "sat_p_dist_guichet_km": {
        "en": "The nearest branch or ATM to {s} is {v} km away.",
        "fr": "L'agence ou le distributeur le plus proche de {s} est à "
              "{v} km."},
    "sat_calc_chl": {
        "en": "NOAA CoastWatch, VIIRS SNPP, OCI algorithm, monthly 4 km "
              "composites. The scored value is the 2021-2025 mean, taken "
              "per cell and then across cells — the other order would give "
              "more weight to the least cloudy cells, which are the "
              "offshore ones, and would pull the coastal figure down. "
              "THREE CAVEATS, ALL IN THE SAME DIRECTION. At four "
              "kilometres the first cell straddles the shore, and near the "
              "coast a bright bottom, suspended sediment and dissolved "
              "organic matter are all read as pigment: the value is an "
              "upper bound and the score a lower bound. Monthly composites "
              "drop cloudy cells, so the rainy season — when runoff is "
              "strongest — is under-represented. And the referential does "
              "not say over what period to average, so the 2012-2016 "
              "window is computed alongside rather than hidden. Sentinel-3 "
              "OLCI would give 300 m, fourteen times finer along a narrow "
              "coast, but access needs a Copernicus account.",
        "fr": "NOAA CoastWatch, VIIRS SNPP, algorithme OCI, composites "
              "mensuels à 4 km. La valeur notée est la moyenne 2021-2025, "
              "prise par maille puis entre mailles — l'ordre inverse "
              "donnerait plus de poids aux mailles les moins nuageuses, "
              "c'est-à-dire au large, et tirerait le chiffre côtier vers le "
              "bas. TROIS RÉSERVES, ET TOUTES DANS LE MÊME SENS. À quatre "
              "kilomètres, la première maille est à cheval sur la côte, et "
              "près du rivage le fond clair, les sédiments en suspension et "
              "la matière organique dissoute sont lus comme du pigment : la "
              "valeur est un majorant, le score un minorant. Les composites "
              "mensuels perdent les mailles nuageuses, donc la saison des "
              "pluies, celle où le lessivage est le plus fort, est "
              "sous-représentée. Enfin le référentiel ne dit pas sur quelle "
              "période moyenner : la fenêtre 2012-2016 est donc calculée à "
              "côté plutôt que cachée. Sentinel-3 OLCI donnerait 300 m, "
              "quatorze fois mieux le long d'une côte étroite, mais son "
              "accès demande un compte Copernicus."},
    "sat_calc_herb": {
        "en": "Allen Coral Atlas global benthic layer: supervised "
              "classification of 10 m Planet Dove imagery, calibrated on "
              "field surveys, 2020-2021 vintage, read through its public "
              "WFS. A patch is assigned to a section when its centre lies "
              "within five kilometres of that section, and the territory "
              "total counts each patch once — which is why the sections do "
              "not add up to the total. THE AREA IS SHOWN, THE SCORE IS "
              "NOT: the published scale asks for a percentage of historical "
              "surface, hence two dates, and this mapping has one. Two "
              "further limits, both downward. Seagrass is the hardest of "
              "the five benthic classes to separate — over a dark bottom, "
              "sparse seagrass and an algal bed look alike — and satellite "
              "bottom mapping stops where light no longer returns, around "
              "fifteen metres in clear water and far less in turbid water.",
        "fr": "Allen Coral Atlas, couche benthique mondiale : "
              "classification supervisée d'images Planet Dove à 10 m, "
              "calibrée sur des relevés de terrain, millésime 2020-2021, "
              "lue par son WFS public. Une tache revient à une section "
              "quand son centre est à moins de cinq kilomètres d'elle, et "
              "le total du territoire ne compte chaque tache qu'une fois — "
              "c'est pourquoi les sections ne s'additionnent pas au total. "
              "LA SURFACE EST AFFICHÉE, LA NOTE NE L'EST PAS : le barème "
              "publié demande un pourcentage de la surface historique, donc "
              "deux dates, et cette cartographie n'en a qu'une. Deux "
              "limites de plus, toutes deux vers le bas. La classe herbier "
              "est la plus difficile des cinq benthos à séparer — sur un "
              "fond sombre, un herbier clairsemé et une algueraie se "
              "ressemblent — et la cartographie du fond s'arrête où la "
              "lumière ne revient plus, autour de quinze mètres en eau "
              "claire et bien moins en eau chargée."},
    "sat_src_chl": {
        "en": "{s}. Coastal strip of {r} km, {f1}-{f2} window, {n} sea "
              "cells over the whole coast.",
        "fr": "{s}. Bande côtière de {r} km, fenêtre {f1}-{f2}, {n} mailles "
              "de mer sur l'ensemble du littoral."},
    "sat_src_herb": {
        "en": "{s}. Patches assigned within {r} km of the section.",
        "fr": "{s}. Taches attribuées à moins de {r} km de la section."},
    "sat_p_chl_a": {
        "en": "Off {s}, the water carries {v} mg of chlorophyll-a per cubic "
              "metre.",
        "fr": "Devant {s}, l'eau porte {v} mg de chlorophylle-a par mètre "
              "cube."},
    "sat_p_chl_a_evolution_pct": {
        "en": "Off {s}, chlorophyll-a moved by {v} % between the 2012-2016 "
              "and the 2021-2025 window.",
        "fr": "Devant {s}, la chlorophylle-a a bougé de {v} % entre la "
              "fenêtre 2012-2016 et la fenêtre 2021-2025."},
    "sat_p_herbier_ha": {
        "en": "{v} ha of seagrass are mapped off {s} — an area, not a "
              "retention rate, so the line carries no score.",
        "fr": "{v} ha d'herbiers sont cartographiés devant {s} — une "
              "surface, pas un taux de conservation : la ligne ne porte "
              "donc pas de note."},
    "sat_calc_sol": {
        "en": "RUSLE: A = R x K x LS x C x P, on a 30 m grid. R is rainfall "
              "erosivity from CHIRPS 1981-2024 through Renard & Freimund "
              "(1994); K is soil erodibility from SoilGrids 250 m through "
              "the Williams (1995) EPIC equation; LS comes from the "
              "Copernicus 30 m DEM with slope length taken as the cell size; "
              "C is one value per ESA WorldCover class; P is 1. Every factor "
              "carries its own uncertainty and they multiply, so read the "
              "ranking between sections rather than the absolute tonnage. "
              "Two known biases, and they pull in opposite directions: "
              "without flow routing the long hillslopes of the Grand'Anse "
              "are understated, and with P = 1 any stone bund or live hedge "
              "already in place is ignored.",
        "fr": "RUSLE : A = R x K x LS x C x P, sur une grille de 30 m. R est "
              "l'érosivité des pluies, de CHIRPS 1981-2024 par Renard et "
              "Freimund (1994) ; K l'érodibilité du sol, de SoilGrids 250 m "
              "par l'équation EPIC de Williams (1995) ; LS vient du MNT "
              "Copernicus 30 m, la longueur de pente étant prise égale à la "
              "maille ; C est une valeur par classe ESA WorldCover ; P vaut "
              "1. Chaque facteur porte son incertitude et elles se "
              "multiplient : lisez le classement entre sections plutôt que "
              "le tonnage absolu. Deux biais connus, et ils tirent en sens "
              "contraire : sans routage d'écoulement, les longs versants de "
              "la Grand'Anse sont sous-estimés ; avec P = 1, les murets et "
              "les haies vives déjà en place sont ignorés."},
    "sat_calc_deg": {
        "en": "The SDG 15.3.1 « one out, all out » rule, pixel by pixel at "
              "30 m: ground counts as degraded if it loses more than "
              "10 t/ha/yr — the usual tolerance — OR if it lost its tree "
              "cover since 2000 in Hansen/UMD, at the 30 % cover threshold. "
              "The third official sub-indicator, land productivity dynamics, "
              "needs a fifteen-year per-pixel NDVI series and is not "
              "computed here: this figure is therefore a LOWER BOUND, and a "
              "documented approximation of 15.3.1 rather than the "
              "Trends.Earth computation.",
        "fr": "La règle « one out, all out » du SDG 15.3.1, pixel par pixel "
              "à 30 m : un sol est dégradé s'il perd plus de 10 t/ha/an — la "
              "tolérance usuelle — OU s'il a perdu son couvert arboré depuis "
              "2000 selon Hansen/UMD, au seuil de 30 % de couvert. Le "
              "troisième sous-indicateur officiel, la dynamique de "
              "productivité des terres, demande une série de NDVI par pixel "
              "sur quinze ans et n'est pas calculé ici : ce chiffre est donc "
              "un MINORANT, et une approximation documentée du 15.3.1 plutôt "
              "que le calcul de Trends.Earth."},
    "sat_src_sol": {
        "en": "CHIRPS 1981-2024, SoilGrids 250 m, Copernicus DEM 30 m, ESA "
              "WorldCover 2021. Model output on a {r} m grid, P = 1.",
        "fr": "CHIRPS 1981-2024, SoilGrids 250 m, MNT Copernicus 30 m, ESA "
              "WorldCover 2021. Résultat de modèle sur une grille de {r} m, "
              "P = 1."},
    "sat_src_deg": {
        "en": "RUSLE above plus Hansen/UMD GFC 2023 v1.11. Tolerance "
              "{t} t/ha/yr, {r} m grid. Productivity sub-indicator not "
              "included.",
        "fr": "Le RUSLE ci-dessus et Hansen/UMD GFC 2023 v1.11. Tolérance "
              "{t} t/ha/an, grille de {r} m. Sous-indicateur de productivité "
              "non compris."},
    "sat_calc_acces": {
        "en": "The road network comes from OpenStreetMap, the population "
              "from WorldPop 2020 UN-adjusted at 3 arcsec, about 92 m. The "
              "network is densified every 100 m, so the distance from a "
              "populated pixel to the nearest road is exact to within fifty "
              "metres against a threshold of two thousand. For each "
              "section, the population of the pixels inside the section and "
              "within 2 km of the network is divided by the section's total "
              "population. THE ALL-SEASON CONDITION IN THE FRAMEWORK'S "
              "TITLE IS NOT APPLIED: surface is tagged on only 11 % of the "
              "ways in OSM, and keeping it would have rested the indicator "
              "on the completeness of that tagging rather than on the state "
              "of the roads. What is applied instead is a definition of a "
              "road: classified network and access roads, 1,618 km. Counting "
              "tracks as well brings it to 3,129 km and the territory "
              "figure from 96.6 to 98.8 %; keeping only the classified "
              "network, 291 km, drops it to 74.6 %. The three are shown "
              "here because the choice is worth more score than the "
              "computation.",
        "fr": "Le réseau vient d'OpenStreetMap, la population de WorldPop "
              "2020 ajustée ONU à 3 secondes d'arc, environ 92 m. Le réseau "
              "est densifié tous les 100 m, si bien que la distance d'un "
              "pixel peuplé à la route la plus proche est juste à cinquante "
              "mètres près, pour un seuil de deux mille. Pour chaque "
              "section, la population des pixels situés dans la section et "
              "à moins de 2 km du réseau est divisée par la population "
              "totale de la section. LA CONDITION « PRATICABLE EN TOUTE "
              "SAISON » DU LIBELLÉ N'EST PAS APPLIQUÉE : la surface n'est "
              "renseignée que sur 11 % des voies dans OSM, et la retenir "
              "aurait fait reposer l'indicateur sur la complétude de "
              "l'étiquetage plutôt que sur l'état des routes. Ce qui est "
              "appliqué, en revanche, c'est une définition de la route : "
              "réseau classé et voies de desserte, 1 618 km. En comptant "
              "aussi les pistes, on passe à 3 129 km et le chiffre du "
              "territoire de 96,6 à 98,8 % ; en ne gardant que le réseau "
              "classé, 291 km, il tombe à 74,6 %. Les trois sont affichées "
              "ici parce que le choix vaut plus de points que le calcul."},
    "sat_src_acces": {
        "en": "{s}. Population: {p}. Threshold {d} m. Retained network "
              "{k:,.0f} km.",
        "fr": "{s}. Population : {p}. Seuil {d} m. Réseau retenu "
              "{k:,.0f} km."},
    "sat_ref_zonal_acces": {
        "en": "This figure is not an average of pixels: it is a share of "
              "population. A section whose people all live along the one "
              "road that crosses it scores high even if nine tenths of its "
              "ground is unreachable — which is the intent, since the "
              "indicator is about people, not about land.",
        "fr": "Ce chiffre n'est pas une moyenne de pixels : c'est une part "
              "de population. Une section dont tous les habitants vivent le "
              "long de la seule route qui la traverse est bien notée même "
              "si les neuf dixièmes de son sol sont inaccessibles — c'est "
              "voulu, l'indicateur parle des gens, pas du territoire."},
    "sat_src_frag": {
        "en": "{s}. Habitat: tree cover, shrubland, herbaceous wetland, "
              "mangrove; grassland excluded. Edge depth {l} m, dispersal "
              "distance {d} m, patches from {t} ha.",
        "fr": "{s}. Habitat : arbres, arbustes, zone humide herbacée, "
              "mangrove ; prairie exclue. Lisière {l} m, distance de "
              "dispersion {d} m, taches à partir de {t} ha."},
    "sat_calc_foret": {
        "en": "Hansen publishes, per 30 m pixel, the tree cover of 2000 and "
              "the year of loss if the pixel lost its cover. The forest of "
              "2000 is the area of the pixels above 30 % cover inside the "
              "section; the loss is the area of those same pixels flagged "
              "lost between 2001 and the last year; the relative loss is the "
              "second divided by the first, times a hundred; the annual rate "
              "is the compound rate taking the area from 2000 to the area "
              "remaining. Gain is only recorded up to 2012, so the net rate "
              "understates any regrowth after that date.",
        "fr": "Hansen publie, pour chaque pixel de 30 m, le couvert arboré de "
              "2000 et l\u2019année de perte si le pixel a perdu son couvert. "
              "La forêt de 2000 est la surface des pixels au-dessus de 30 % "
              "de couvert dans la section ; la perte est la surface de ces "
              "mêmes pixels signalés perdus entre 2001 et la dernière année ; "
              "la perte relative est la seconde divisée par la première, "
              "multipliée par cent ; le taux annuel est le taux composé qui "
              "mène de la surface de 2000 à la surface restante. Le gain "
              "n\u2019est enregistré que jusqu\u2019en 2012 : le taux net "
              "sous-estime donc toute reprise postérieure."},
    "sat_calc_vege": {
        "en": "For each dry season, the median of the Sentinel-2 pixels of "
              "the section is taken, clouds removed by the SCL band; the "
              "index is computed on that median, then averaged over the "
              "polygon. The change compares the 2019\u20132021 mean with the "
              "2023\u20132025 mean, the year 2022 acting as the hinge.",
        "fr": "Pour chaque saison sèche, on prend la médiane des pixels "
              "Sentinel-2 de la section, nuages retirés par la bande SCL ; "
              "l\u2019indice est calculé sur cette médiane, puis moyenné sur "
              "le polygone. La variation compare la moyenne 2019-2021 à la "
              "moyenne 2023-2025, l\u2019année 2022 servant de charnière."},
    "sat_calc_pluie": {
        "en": "CHIRPS gives a daily rainfall grid at 5.5 km since 1981. The "
              "daily values are summed over the year, then averaged over the "
              "section polygon. The normal is the 1991\u20132020 mean, the "
              "period the WMO recommends; the ratio divides the year by that "
              "normal; the SPI fits a gamma law on the 45 years and returns "
              "the rarity of the year in standard deviations.",
        "fr": "CHIRPS fournit une grille de pluie journalière à 5,5 km depuis "
              "1981. Les valeurs journalières sont sommées sur "
              "l\u2019année, puis moyennées sur le polygone de la section. La "
              "normale est la moyenne 1991-2020, période recommandée par "
              "l\u2019OMM ; le rapport divise l\u2019année par cette normale ; "
              "le SPI ajuste une loi gamma sur les 45 ans et rend la rareté "
              "de l\u2019année en écarts-types."},
    "sat_calc_saison": {
        "en": "Same source and same zonal averaging as the annual rainfall, "
              "but summed over two windows read from the 45-year "
              "climatology: March to May, and August to October. A dry day is "
              "a day below 1 mm; the onset of the rains is the first day of "
              "the first spell that accumulates enough without a long dry "
              "break after it, and a failed onset is a spell that starts and "
              "breaks.",
        "fr": "Même source et même moyenne zonale que la pluie annuelle, mais "
              "sommée sur deux fenêtres lues dans la climatologie de 45 ans : "
              "mars à mai, et août à octobre. Un jour sec est un jour sous "
              "1 mm ; l\u2019installation des pluies est le premier jour de la "
              "première séquence qui accumule assez sans longue rupture "
              "derrière, et une installation ratée est une séquence qui part "
              "et se casse."},
    "sat_calc_thermique": {
        "en": "MODIS gives the ground temperature twice a day at 1 km. The "
              "day and night values are averaged separately over the section "
              "polygon and over the season; the day-night range is their "
              "difference; the anomaly compares the season with the "
              "2001\u20132020 normal. Evapotranspiration comes from MOD16A2, "
              "and the aridity index divides rainfall by potential "
              "evapotranspiration.",
        "fr": "MODIS donne la température du sol deux fois par jour à 1 km. "
              "Les valeurs de jour et de nuit sont moyennées séparément sur "
              "le polygone de la section et sur la saison ; l\u2019amplitude "
              "est leur différence ; l\u2019anomalie compare la saison à la "
              "normale 2001-2020. L\u2019évapotranspiration vient de MOD16A2, "
              "et l\u2019indice d\u2019aridité divise la pluie par "
              "l\u2019évapotranspiration potentielle."},
    "sat_lecture": {"en": "What this says, section by section",
                    "fr": "Ce que cela dit, section par section"},

    # UNE PHRASE PAR MESURE, ET ELLE EST ÉCRITE, PAS DÉDUITE. « {s} » est le
    # nom de la section, « {v} » la valeur en valeur absolue, « {vs} » la
    # valeur signée, « {a} » et « {a2} » les bornes de la période du fichier.
    # Les mesures sans phrase n'en affichent pas : mieux vaut aucun
    # commentaire qu'un commentaire générique.
    "sat_p_foret2025_pct": {
        "en": "{s} had {v} % of its area under forest in {a2}.",
        "fr": "{s} avait {v} % de sa surface couverte de forêt en {a2}."},
    "sat_p_foret2000_pct": {
        "en": "{s} had {v} % of its area under forest in {a}.",
        "fr": "{s} avait {v} % de sa surface couverte de forêt en {a}."},
    "sat_p_perte_relative_pct": {
        "en": "{s} has lost {v} % of its {a} forest area since {a}.",
        "fr": "{s} a perdu {v} % de sa surface boisée depuis {a}."},
    "sat_p_perte_totale_ha": {
        "en": "{s} has lost {v} hectares of forest since {a}.",
        "fr": "{s} a perdu {v} hectares de forêt depuis {a}."},
    "sat_p_taux_annuel_net": {
        "en": "In {s}, forest area changes by {vs} % a year on average over "
              "{a}\u2013{a2}.",
        "fr": "Dans {s}, la surface boisée évolue de {vs} % par an en moyenne "
              "sur {a}-{a2}."},
    "sat_p_part_choc_pct": {
        "en": "In {s}, {v} % of all the forest lost since {a} went in a "
              "single year.",
        "fr": "Dans {s}, {v} % de toute la forêt perdue depuis {a} l\u2019a "
              "été en une seule année."},
    "sat_p_erosion_t_ha_an": {
        "en": "{s} loses on average {v} tonnes of soil per hectare per year.",
        "fr": "{s} perd en moyenne {v} tonnes de sol par hectare et par "
              "an."},
    "sat_p_erosion_mediane": {
        "en": "On the median pixel of {s}, the loss is {v} t/ha/yr — well "
              "under the average, which a few very steep pixels pull up.",
        "fr": "Sur le pixel médian de {s}, la perte est de {v} t/ha/an — "
              "bien sous la moyenne, que quelques pixels très pentus "
              "tirent vers le haut."},
    "sat_p_part_sup_10": {
        "en": "{v} % of {s} loses more than the 10 t/ha/yr tolerance.",
        "fr": "{v} % de {s} perd plus que la tolérance de 10 t/ha/an."},
    "sat_p_degrade_pct": {
        "en": "{v} % of the ground of {s} counts as degraded — and that is a "
              "lower bound, one of the three sub-indicators being missing.",
        "fr": "{v} % du sol de {s} compte comme dégradé — et c'est un "
              "minorant, l'un des trois sous-indicateurs manquant."},
    "sat_p_couvert_perdu_pct": {
        "en": "{v} % of {s} lost its tree cover since 2000.",
        "fr": "{v} % de {s} a perdu son couvert arboré depuis 2000."},
    "sat_p_pente_moy_deg": {
        "en": "The mean slope of {s} is {v} degrees.",
        "fr": "La pente moyenne de {s} est de {v} degrés."},
    "sat_p_dist_med_m": {
        "en": "Half the inhabitants of {s} live within {v} m of a road.",
        "fr": "La moitié des habitants de {s} vivent à moins de {v} m d'une "
              "route."},
    "sat_p_dist_med_classe_m": {
        "en": "From the classified network, that median distance is {v} m in "
              "{s}.",
        "fr": "Du réseau classé, cette distance médiane vaut {v} m dans "
              "{s}."},
    "sat_p_aire_2km_pct": {
        "en": "{v} % of the ground of {s} is within 2 km of a road — the "
              "figure to read next to the population share, which saturates.",
        "fr": "{v} % du sol de {s} est à moins de 2 km d'une route — c'est "
              "le chiffre à lire à côté de la part de population, qui "
              "sature."},
    "sat_p_acces_axe": {
        "en": "{v} % of the people of {s} live within 2 km of a drivable "
              "road.",
        "fr": "{v} % des habitants de {s} vivent à moins de 2 km d'un axe "
              "carrossable."},
    "sat_p_acces_pistes": {
        "en": "Counting tracks as roads, {v} % of {s}.",
        "fr": "En comptant les pistes comme des routes, {v} % pour {s}."},
    "sat_p_acces_classe": {
        "en": "On the classified network alone, {v} % of {s}.",
        "fr": "Sur le seul réseau classé, {v} % pour {s}."},
    "sat_p_pop": {
        "en": "{s} holds about {v} inhabitants.",
        "fr": "{s} compte environ {v} habitants."},
    "sat_p_habitat_pct": {
        "en": "{v} % of {s} is natural habitat: tree cover, shrubland, "
              "wetland or mangrove.",
        "fr": "{v} % de la section de {s} est de l'habitat naturel : arbres, "
              "arbustes, zone humide ou mangrove."},
    "sat_p_taches_total": {
        "en": "The habitat of {s} is broken into {v} separate patches.",
        "fr": "L'habitat de {s} est morcelé en {v} taches séparées."},
    "sat_p_densite_lisiere_m_ha": {
        "en": "{s} carries {v} metres of habitat edge per hectare; the "
              "framework's scale already gives its worst mark above a "
              "hundred.",
        "fr": "{s} porte {v} mètres de bordure d'habitat par hectare ; "
              "au-delà de cent, le barème du référentiel donne déjà sa note "
              "la plus basse."},
    "sat_p_core_pct": {
        "en": "Only {v} % of {s} is interior habitat, that is habitat more "
              "than a hundred metres from any edge.",
        "fr": "Seuls {v} % de la section de {s} sont de l'habitat intérieur, "
              "c'est-à-dire à plus de cent mètres de toute lisière."},
    "sat_p_core_ha": {
        "en": "{s} holds {v} hectares of interior habitat.",
        "fr": "{s} compte {v} hectares d'habitat intérieur."},
    "sat_p_ratio_core_move": {
        "en": "In {s}, {v} of the habitat still serves as core or as "
              "corridor; the rest is fragment dust, too small and too far to "
              "do either.",
        "fr": "Dans {s}, {v} de l'habitat sert encore de cœur ou de "
              "corridor ; le reste est de la poussière de fragments, trop "
              "petits et trop éloignés pour l'un comme pour l'autre."},
    "sat_p_pc_d": {
        "en": "In {s}, two points of habitat picked at random have a "
              "connection probability of {v} for a species dispersing over "
              "a kilometre.",
        "fr": "Dans {s}, deux points d'habitat pris au hasard ont une "
              "probabilité de connexion de {v} pour une espèce qui se "
              "disperse sur un kilomètre."},
    "sat_p_pc_d2": {
        "en": "In {s}, that probability falls to {v} for a species that only "
              "crosses five hundred metres.",
        "fr": "Dans {s}, cette probabilité tombe à {v} pour une espèce qui "
              "ne franchit que cinq cents mètres."},
    "sat_p_iic": {
        "en": "Counting only patches that touch, the structural connectivity "
              "of {s} is {v}.",
        "fr": "En ne comptant que les taches jointives, la connectivité "
              "structurelle de {s} vaut {v}."},
    "sat_p_iic_d": {
        "en": "Allowing jumps up to a kilometre, it rises to {v} in {s}.",
        "fr": "En autorisant des sauts jusqu'à un kilomètre, elle monte à "
              "{v} dans {s}."},
    "sat_p_aire_habitat_ha": {
        "en": "{s} holds {v} hectares of natural habitat.",
        "fr": "{s} compte {v} hectares d'habitat naturel."},
    "sat_p_pluie_courante": {
        "en": "{s} received {v} mm of rain over the assessed year.",
        "fr": "{s} a reçu {v} mm de pluie sur l\u2019année évaluée."},
    "sat_p_pluie_normale": {
        "en": "{s} receives {v} mm of rain in a normal year (1991\u20132020 "
              "average).",
        "fr": "{s} reçoit {v} mm de pluie une année normale (moyenne "
              "1991-2020)."},
    "sat_p_ratio_normale": {
        "en": "{s} received {v} % of its normal rainfall.",
        "fr": "{s} a reçu {v} % de sa pluie normale."},
    "sat_p_pl_min": {
        "en": "The driest year on record in {s} brought {v} mm.",
        "fr": "L\u2019année la plus sèche jamais enregistrée à {s} a apporté "
              "{v} mm."},
    "sat_p_pl_max": {
        "en": "The wettest year on record in {s} brought {v} mm.",
        "fr": "L\u2019année la plus arrosée jamais enregistrée à {s} a "
              "apporté {v} mm."},
    "sat_p_spi": {
        "en": "{s} scores an SPI of {vs}: below \u22121 the year counts as a "
              "drought.",
        "fr": "{s} affiche un SPI de {vs} : en dessous de \u22121, "
              "l\u2019année compte comme une sécheresse."},
    "sat_p_spi_mam": {
        "en": "For the spring campaign, {s} scores an SPI of {vs}: below "
              "\u22121 the season counts as a drought.",
        "fr": "Pour la campagne de printemps, {s} affiche un SPI de {vs} : en "
              "dessous de \u22121, la saison compte comme une sécheresse."},
    "sat_p_mam_courant": {
        "en": "{s} received {v} mm over the March-to-May campaign.",
        "fr": "{s} a reçu {v} mm sur la campagne de mars à mai."},
    "sat_p_mam_normale": {
        "en": "{s} receives {v} mm over a normal spring campaign.",
        "fr": "{s} reçoit {v} mm sur une campagne de printemps normale."},
    "sat_p_aso_courant": {
        "en": "{s} received {v} mm over the August-to-October campaign.",
        "fr": "{s} a reçu {v} mm sur la campagne d\u2019août à octobre."},
    "sat_p_secs_mam": {
        "en": "{s} counted {v} dry days during the spring campaign.",
        "fr": "{s} a compté {v} jours secs pendant la campagne de printemps."},
    "sat_p_secs_an": {
        "en": "The longest dry spell of the year in {s} lasted {v} days.",
        "fr": "La plus longue séquence sèche de l\u2019année à {s} a duré {v} "
              "jours."},
    "sat_p_j50": {
        "en": "{s} counted {v} days above 50 mm of rain in the year.",
        "fr": "{s} a compté {v} jours à plus de 50 mm de pluie dans "
              "l\u2019année."},
    "sat_p_install_decalage": {
        "en": "In {s}, the onset of the rains has moved by {vs} days against "
              "the earlier period: a negative figure means earlier.",
        "fr": "À {s}, l\u2019installation des pluies s\u2019est déplacée de "
              "{vs} jours par rapport à la période ancienne : un chiffre "
              "négatif veut dire plus tôt."},
    "sat_p_install_ratees": {
        "en": "{s} has counted {v} failed onsets of the rainy season since "
              "1981.",
        "fr": "{s} a compté {v} installations ratées de la saison des pluies "
              "depuis 1981."},
    "sat_p_lst_courant": {
        "en": "The ground of {s} reaches {v} \u00b0C on average over the dry "
              "season.",
        "fr": "Le sol de {s} atteint {v} \u00b0C en moyenne sur la saison "
              "sèche."},
    "sat_p_lst_anomalie": {
        "en": "The dry-season ground temperature of {s} departs by {vs} % "
              "from its normal.",
        "fr": "La température du sol de {s} en saison sèche s\u2019écarte de "
              "{vs} % de sa normale."},
    "sat_p_lst_nuit": {
        "en": "The ground of {s} falls back to {v} \u00b0C on average at "
              "night.",
        "fr": "Le sol de {s} retombe à {v} \u00b0C en moyenne la nuit."},
    "sat_p_lst_amplitude": {
        "en": "Between day and night, the ground of {s} swings by {v} "
              "\u00b0C: the wider the swing, the barer the soil.",
        "fr": "Entre le jour et la nuit, le sol de {s} varie de {v} \u00b0C : "
              "plus l\u2019écart est grand, plus le sol est nu."},
    "sat_p_lst_max": {
        "en": "The hottest season on record in {s} reached {v} \u00b0C.",
        "fr": "La saison la plus chaude enregistrée à {s} a atteint {v} "
              "\u00b0C."},
    "sat_p_aridite": {
        "en": "In {s}, rainfall covers {v} of the atmospheric demand: below "
              "0.65 the climate counts as dry sub-humid.",
        "fr": "À {s}, la pluie couvre {v} de la demande atmosphérique : en "
              "dessous de 0,65, le climat compte comme subhumide sec."},
    "sat_p_et": {
        "en": "{s} actually evaporates and transpires {v} mm a year.",
        "fr": "{s} évapore et transpire réellement {v} mm par an."},
    "sat_p_pet": {
        "en": "The atmosphere of {s} could draw {v} mm a year if water were "
              "unlimited.",
        "fr": "L\u2019atmosphère de {s} pourrait tirer {v} mm par an si "
              "l\u2019eau était illimitée."},
    "sat_p_eau_ha": {
        "en": "{s} carries {v} hectares of open water.",
        "fr": "{s} porte {v} hectares d\u2019eau libre."},
    "sat_p_vhi": {
        "en": "{s} scores {v} on the vegetation health index, where 100 is "
              "the healthiest state observed.",
        "fr": "{s} obtient {v} à l\u2019indice de santé de la végétation, où "
              "100 est le meilleur état observé."},
    "sat_p_var_ndvi": {
        "en": "The greenness of {s} swings by {v} from one year to the next: "
              "the smaller the swing, the steadier the cover.",
        "fr": "La verdeur de {s} varie de {v} d\u2019une année sur "
              "l\u2019autre : plus l\u2019écart est petit, plus le couvert "
              "est stable."},

    "sat_src_pluie": {
        "en": "CHIRPS daily ({s}), {d1}–{d2}, normal computed over {n1}–{n2}, "
              "year assessed {a}.",
        "fr": "CHIRPS journalier ({s}), {d1}-{d2}, normale calculée sur "
              "{n1}-{n2}, année évaluée {a}."},
    "sat_src_thermique": {
        "en": "{s}, {d1}–{d2}, normal computed over {n1}–{n2}, recent window "
              "{f1}–{f2}.",
        "fr": "{s}, {d1}-{d2}, normale calculée sur {n1}-{n2}, fenêtre "
              "récente {f1}-{f2}."},
    "sat_src_foret": {
        "en": "Hansen / UMD global forest change, {s}. Forest = at least "
              "{p} % tree cover. Period {d1}–{d2}.",
        "fr": "Hansen / UMD global forest change, {s}. Forêt = couvert "
              "arboré d'au moins {p} %. Période {d1}–{d2}."},
    "sat_src_vege": {
        "en": "Sentinel-2 surface reflectance ({s}), {sa} composites, "
              "{d1}–{d2}. Sections with fewer than {px} usable pixels are "
              "left out.",
        "fr": "Réflectance de surface Sentinel-2 ({s}), composites de "
              "{sa}, {d1}–{d2}. Les sections comptant moins de {px} pixels "
              "exploitables sont écartées."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)

STYLE = """
<style>
  .sat-lab { font-size:10.5px; font-weight:700; letter-spacing:.09em;
       text-transform:uppercase; color:#8a93a5; margin:10px 0 2px; }
  .sat-tab { width:100%; border-collapse:collapse; margin-top:12px; }
  /* AUCUN TRAIT DE COLONNE, SEULEMENT LES LIGNES. La feuille de style de
     base pose une bordure sur les quatre côtés de chaque cellule, et nos
     règles n'écrasaient que celle du bas : il restait un quadrillage
     vertical qui découpait en cases un tableau dont les colonnes se lisent
     déjà par leur alignement. On remet les quatre côtés à zéro, puis on ne
     redonne que le filet horizontal. */
  .sat-tab th, .sat-tab td { border: 0 !important; }
  .sat-tab th { font-size:10.5px; font-weight:700; letter-spacing:.09em;
       text-transform:uppercase; color:#8a93a5; text-align:left;
       padding:0 10px 7px 0;
       border-bottom:1px solid #e9eef4 !important; }
  .sat-tab th.n, .sat-tab td.n { text-align:right;
       font-variant-numeric:tabular-nums; }
  .sat-tab td { font-size:12.5px; color:#3c4761; padding:7px 10px 7px 0;
       border-bottom:1px solid #f2f5f9 !important; }
  .sat-tab td.v { font-weight:700; color:#101728; }
  .sat-note { font-size:11.5px; color:#8a93a5; line-height:1.5;
       margin:8px 0 0; text-align:left !important; max-width:96ch; }
  /* LES PUCES VONT D'UN BORD À L'AUTRE : ce sont des phrases de lecture, pas
     des notes de bas de tableau. */
  .sat-puces { margin:10px 0 0; padding-left:18px; max-width:none;
       list-style:disc; }
  .sat-puces li { font-size:12.5px; color:#3c4761; line-height:1.6;
       margin:0 0 4px; text-align:left !important; }
  .sat-puces li b { color:#3c4761; }
</style>
"""


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _f(v, dec=1, signe=False):
    if v is None:
        return "—"
    s = f"{v:+.{dec}f}" if signe else f"{v:.{dec}f}"
    return s.replace(".", ",") if i18n.get_lang() == "fr" else s


@st.cache_data(show_spinner=False)
def _charger():
    """Les deux fichiers de mesures, tels qu'ils sont livrés.

    UN FICHIER ABSENT NE FAIT PAS TOMBER L'ÉCRAN : la mesure qui en dépend est
    simplement dite indisponible. Un dépôt sans données satellitaires doit
    pouvoir afficher les résultats d'enquête.
    """
    out = {}
    for cle, nom in (("foret", "foret.json"),
                     ("vege", "indices_vegetation.json"),
                     ("pluie", "pluie.json"),
                     ("saison", "pluie_saison.json"),
                     ("thermique", "thermique.json"),
                     ("frag", "fragmentation.json"),
                     ("acces", "acces_routier.json"),
                     ("sol", "erosion.json"),
                     ("deg", "degradation.json"),
                     ("chl", "chlorophylle.json"),
                     ("herb", "herbiers.json"),
                     ("fin", "services_financiers.json")):
        p = os.path.join(DATA, nom)
        if not os.path.exists(p):
            p = os.path.join(APP_DIR, nom)
        try:
            with open(p, encoding="utf-8") as f:
                out[cle] = json.load(f)
        except Exception:
            out[cle] = None
    return out


@st.cache_data(show_spinner=False)
def _referentiel():
    """Les indicateurs du référentiel, rangés par numéro de ligne.

    C'EST LÀ QUE VIVENT LA SOURCE, LE BARÈME ET LA PHRASE DE LECTURE. Ils y
    sont depuis le début, mais seuls les écrans de score les affichaient : la
    page des mesures brutes renvoyait donc à un autre onglet pour savoir d'où
    venait un chiffre. Elle les lit maintenant elle-même.
    """
    p = os.path.join(DATA, "resultats.json")
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    lst = d["indicateurs"] if isinstance(d, dict) and "indicateurs" in d else d
    return {r.get("ligne"): r for r in (lst or []) if r.get("ligne")}


def _annees(d, chemin):
    """Les années d'une série, triées."""
    if not d:
        return []
    for sec in (d.get("sections") or {}).values():
        s = sec.get(chemin)
        if isinstance(s, dict) and s:
            return sorted(s, key=lambda a: int(a))
    return []


def _valeurs(d, spec, annee=None):
    """La mesure demandée, section par section : {section: valeur}."""
    if not d:
        return {}, None, None
    out = {}
    if spec.startswith("serie:"):
        bouts = spec.split(":")
        champ = bouts[1]
        delta = len(bouts) > 2 and bouts[2] == "delta"
        for nom, sec in (d.get("sections") or {}).items():
            s = sec.get(champ)
            if not isinstance(s, dict) or not s:
                continue
            ans = sorted(s, key=lambda a: int(a))
            if delta:
                out[nom] = s[ans[-1]] - s[ans[0]]
            else:
                a = annee if annee in s else ans[-1]
                out[nom] = s[a]
        ans = _annees(d, champ)
        return out, (ans[0] if ans else None), (ans[-1] if ans else None)
    for nom, sec in (d.get("sections") or {}).items():
        v = sec.get(spec)
        if v is not None:
            out[nom] = v
    return out, None, None


# L'ANNÉE QU'UN LIBELLÉ FORESTIER PORTE N'EST PAS TOUJOURS CELLE DE SON
# CHAMP. « Forêt perdue depuis … » compte la perte sur toute la période, elle
# se date donc de son DÉBUT ; « Couverture forestière … » décrit un état, elle
# se date de l'année de cet état. La règle tenait auparavant à la présence du
# nombre 2000 dans le nom du champ : `perte_relative_pct` ne le contient pas,
# et la plateforme annonçait « forêt perdue depuis 2025, en % de la forêt de
# 2025 » pour une perte mesurée de 2000 à 2025. Les deux familles sont donc
# nommées, une fois pour toutes.
_ANNEE_DEBUT = {"foret2000_pct", "perte_relative_pct", "perte_totale_ha"}


def _libelle(cle_lib, mesure, d, annee):
    """Le libellé d'une mesure, avec l'année ou la fenêtre qu'elle couvre."""
    _cat, code, _l, fichier, spec, _u, _dec, _p = mesure
    if fichier == "foret":
        base = (d or {}).get("periode") or [2000, 2025]
        a = base[0] if code in _ANNEE_DEBUT else base[1]
        return T(cle_lib, a=a, d1=base[0], d2=base[1])
    ans = _annees(d, spec.split(":")[1]) if spec.startswith("serie:") else []
    if spec.endswith(":delta") and ans:
        return T(cle_lib, d=f"{ans[0]}–{ans[-1]}", a="")
    a = annee if annee in ans else (ans[-1] if ans else "")
    return T(cle_lib, a=a, d="")


def _source(fichier, d):
    if not d:
        return ""
    if fichier == "foret":
        per = d.get("periode") or [2000, 2025]
        return T("sat_src_foret", s=d.get("source", "—"),
                 p=d.get("seuil_couvert_pct", 30), d1=per[0], d2=per[1])
    # LA PLUIE ET LA TEMPÉRATURE ONT LEUR PROPRE PHRASE DE SOURCE : une
    # normale de trente ans et une fenêtre récente ne se disent pas comme un
    # composite de saison sèche, et lire un SPI sans savoir sur quelle
    # période la normale a été calculée n'apprend rien.
    if fichier in ("pluie", "saison"):
        per = d.get("periode") or [1981, 2025]
        nor = d.get("normale_periode") or [1991, 2020]
        return T("sat_src_pluie", s=d.get("source", "—"),
                 d1=per[0], d2=per[1], n1=nor[0], n2=nor[1],
                 a=d.get("annee_evaluee", "—"))
    if fichier == "thermique":
        per = d.get("periode_annees") or [2001, 2025]
        nor = d.get("normale_periode") or [2001, 2020]
        fen = d.get("fenetre_recente") or [2021, 2025]
        return T("sat_src_thermique", s=d.get("source", "—"),
                 d1=per[0], d2=per[-1], n1=nor[0], n2=nor[1],
                 f1=fen[0], f2=fen[1])
    if fichier == "sol":
        return T("sat_src_sol",
                 r=(d.get("parametres") or {}).get("resolution_m", 30))
    if fichier == "deg":
        pa = d.get("parametres") or {}
        return T("sat_src_deg", r=pa.get("resolution_m", 30),
                 t=pa.get("tolerance_erosion_t_ha_an", 10))
    if fichier == "fin":
        return T("sat_src_fin", s=d.get("source", "—"),
                 a=int(100 * (d.get("part_adultes") or 0.65)),
                 n=len(d.get("releve") or []),
                 p=(d.get("total") or {}).get("poi_cartographies", "—"))
    if fichier == "chl":
        fen = d.get("fenetre") or [2021, 2025]
        return T("sat_src_chl", s=d.get("source", "—"),
                 r=int(d.get("rayon_m", 5000)) // 1000,
                 f1=fen[0], f2=fen[1],
                 n=(d.get("total") or {}).get("mailles", "—"))
    if fichier == "herb":
        return T("sat_src_herb", s=d.get("source", "—"),
                 r=int(d.get("rayon_m", 5000)) // 1000)
    if fichier == "acces":
        return T("sat_src_acces", s=d.get("source", "—"),
                 p=d.get("population", "—"), d=d.get("seuil_m", 2000),
                 k=(d.get("reseau_km") or {}).get("standard", 0))
    if fichier == "frag":
        pa = d.get("parametres") or {}
        return T("sat_src_frag", s=pa.get("source", "—"),
                 l=pa.get("profondeur_lisiere_m", 100),
                 d=pa.get("d_etoile_m", 1000),
                 t=pa.get("min_tache_ha", 0.1))
    per = d.get("periode_annees") or []
    return T("sat_src_vege", s=d.get("source", "—"),
             sa=d.get("saison", "—"),
             d1=(per[0] if per else "—"), d2=(per[-1] if per else "—"),
             px=d.get("pixels_mini", 50))


def _barres(vals, unite, dec, moy):
    """Une barre par section, l'ensemble du territoire en pointillés."""
    if not vals:
        return ""
    lignes = list(vals.items())
    bornes = list(vals.values()) + ([moy] if moy is not None else [])
    vmin, vmax = min(bornes + [0]), max(bornes + [0])
    etendue = (vmax - vmin) or 1.0
    LARG, H_L, GAP = 1000, 28, 9
    MG_G, MG_H, MG_B = 190, 30, 22
    H = MG_H + len(lignes) * (H_L + GAP) + MG_B
    utile = LARG - MG_G - 120
    x0 = MG_G + utile * (0 - vmin) / etendue        # l'abscisse du zéro
    parts, y = [], MG_H

    if moy is not None:
        x = MG_G + utile * (moy - vmin) / etendue
        parts.append(
            f'<line x1="{x:.1f}" y1="{MG_H - 14}" x2="{x:.1f}" '
            f'y2="{H - MG_B + 4}" stroke="{ENCRE3}" stroke-width="1" '
            f'stroke-dasharray="3 4"/>'
            f'<text x="{x:.1f}" y="{MG_H - 19}" text-anchor="middle" '
            f'font-size="11" fill="{ENCRE3}">{_e(T("sat_ens"))} '
            f'{_f(moy, dec)}{_e(unite)}</text>')

    for nom, v in lignes:
        xa = MG_G + utile * (min(v, 0) - vmin) / etendue
        xb = MG_G + utile * (max(v, 0) - vmin) / etendue
        parts.append(
            f'<text x="{MG_G - 12}" y="{y + 15}" text-anchor="end" '
            f'font-size="12.5" fill="{ENCRE}">{_e(nom)}</text>'
            f'<rect x="{xa:.1f}" y="{y + 3}" width="{max(xb - xa, 2):.1f}" '
            f'height="16" rx="4" fill="{VERT_APRI}"/>'
            f'<text x="{LARG - 4}" y="{y + 15}" text-anchor="end" '
            f'font-size="12.5" font-weight="700" fill="{ENCRE}">'
            f'{_f(v, dec)}{_e(unite)}</text>')
        y += H_L + GAP
    parts.append(f'<line x1="{x0:.1f}" y1="{MG_H - 2}" x2="{x0:.1f}" '
                 f'y2="{H - MG_B + 2}" stroke="#d8e0ea" stroke-width="1"/>')
    return (f'<svg viewBox="0 0 {LARG} {H}" width="100%" '
            f'style="max-width:{LARG}px;display:block" role="img" '
            f'font-family="Inter,system-ui,sans-serif">'
            + "".join(parts) + '</svg>')


def _tableau(vals, unite, dec, moy, lib):
    r = ['<table class="sat-tab"><thead><tr>'
         f'<th>{_e(T("sat_col_sec"))}</th>'
         f'<th class="n">{_e(lib)}</th></tr></thead><tbody>']
    for nom, v in vals.items():
        r.append(f'<tr><td>{_e(nom)}</td>'
                 f'<td class="n v">{_f(v, dec)}{_e(unite)}</td></tr>')
    if moy is not None:
        r.append(f'<tr><td>{_e(T("sat_ens"))}</td>'
                 f'<td class="n v">{_f(moy, dec)}{_e(unite)}</td></tr>')
    r.append('</tbody></table>')
    return "".join(r)


def _carte(vals, unite, polarite):
    if len(vals) < 2:
        return None
    seuils = map_render.nice_thresholds(list(vals.values()))
    svg, seuils_ret, _m = map_render.render_map_svg(
        vals, {s: 1 for s in vals}, seuils, height=560,
        polarity=polarite, unite=unite or "")
    legende = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:7px;'
        f'margin-right:16px"><span style="width:20px;height:11px;'
        f'border-radius:3px;background:{c}"></span>'
        f'<span style="font-size:11.5px;color:#52514e">{lab}</span></span>'
        for c, lab in map_render.legend_items(seuils_ret, polarite,
                                              unite or ""))
    return f'<div style="margin:6px 0 8px">{legende}</div>{svg}'


def render():
    """Une mesure, dix sections, un dessin — et sa source sous le dessin."""
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown(
        f'<div class="titre-bloc">{_e(T("sat_titre"))}</div>'
        f'<p class="sat-note" style="margin:0 0 10px">{_e(T("sat_intro", n=len(MESURES)))}</p>',
        unsafe_allow_html=True)

    d = _charger()
    dispo = [m for m in MESURES if d.get(m[3])]
    if not dispo:
        st.info(T("sat_indispo"))
        return

    # LES CATÉGORIES SONT DES ONGLETS, ET C'EST CE QUI REND LES MESURES
    # VISIBLES. Cinquante mesures dans une seule liste déroulante donnaient
    # une page qui paraissait ne porter que la forêt : il fallait dérouler
    # jusqu'au bout pour découvrir que la pluie de quarante-cinq ans et la
    # température de vingt-cinq ans étaient là. Un onglet par famille annonce
    # le contenu avant le clic — c'est tout ce qu'on demande à une barre.
    cats = [c for c in CATEGORIES if any(m[0] == c for m in dispo)]
    cat = onglets.barre("sat_cat", cats, titre=lambda c: T("sat_c_" + c),
                        description=lambda c: T("sat_cd_" + c),
                        defaut=cats[0])
    lot = [m for m in dispo if m[0] == cat]
    if not lot:
        st.info(T("sat_indispo"))
        return

    c1, c2, c3 = st.columns([2, 0.8, 1])
    with c1:
        k = st.selectbox(
            T("sat_mesure"), list(range(len(lot))), key=f"sat_m_{cat}",
            format_func=lambda i: _libelle(lot[i][2], lot[i],
                                           d[lot[i][3]], None))
    mesure = lot[k]
    _cat, _code, cle_lib, fichier, spec, unite, dec, polarite = mesure
    src = d[fichier]
    ans = _annees(src, spec.split(":")[1]) if spec.startswith("serie:") else []
    annee = None
    with c2:
        if ans and not spec.endswith(":delta"):
            annee = st.selectbox(T("sat_annee"), list(reversed(ans)),
                                 key="sat_a")
    with c3:
        forme = st.selectbox(T("sat_format"), ["barres", "carte", "tableau"],
                             key="sat_forme",
                             format_func=lambda f: T("sat_" + f))

    vals, _a0, _a1 = _valeurs(src, spec, annee)
    if not vals:
        st.info(T("sat_indispo"))
        return
    lib = _libelle(cle_lib, mesure, src, annee)
    # LA MOYENNE DU TERRITOIRE EST CELLE DES SECTIONS, PAS UN TOTAL. Additionner
    # des pourcentages n'a pas de sens ; pour les hectares, le fichier porte son
    # propre total et c'est celui-là qu'on affiche.
    ens = (src.get("ensemble") or {}).get(spec) if not \
        spec.startswith("serie:") else None
    moy = ens if ens is not None else (sum(vals.values()) / len(vals))

    if forme == "carte":
        svg = _carte(vals, unite, polarite)
        if svg is None:
            forme = "barres"
        else:
            st.markdown(f'<div style="font-family:Inter,system-ui,sans-serif">'
                        f'{svg}</div>', unsafe_allow_html=True)
    if forme == "barres":
        st.markdown(_barres(vals, unite, dec, moy), unsafe_allow_html=True)
    elif forme == "tableau":
        st.markdown(_tableau(vals, unite, dec, moy, lib),
                    unsafe_allow_html=True)

    # DEUX PUCES, PLEINE LARGEUR. Les deux notes sont de même nature — ce que
    # la mesure ne sait pas faire, et d'où elle vient — et elles se lisaient
    # comme deux paragraphes sans lien, sur une colonne de quatre-vingt-douze
    # signes au milieu d'une page vide.
    st.markdown(
        '<ul class="sat-puces">'
        f'<li>{_e(T("sat_ventile"))}</li>'
        f'<li><b>{_e(T("sat_source"))}</b> · {_e(_source(fichier, src))}</li>'
        '</ul>', unsafe_allow_html=True)

    _lecture(mesure, vals, dec, src)
    _dossier(mesure, vals, unite, dec)


def _lecture(mesure, vals, dec, src):
    """Ce que le chiffre veut dire, section par section, en une phrase.

    UN POURCENTAGE NE SE LIT PAS TOUT SEUL. « 22,2 » sous un intitulé anglais
    demande au lecteur de reconstituer la phrase : de quoi c'est le
    pourcentage, par rapport à quoi, sur quelle période. La phrase est donc
    écrite, une par section, avec le nombre dedans — c'est la même information
    que le graphique, mais dans l'ordre où on la dirait à quelqu'un.

    ELLES SONT RANGÉES DE LA PLUS FORTE À LA PLUS FAIBLE, en valeur absolue :
    on veut voir d'abord la section dont on va parler.
    """
    cle = "sat_p_" + mesure[1]
    if cle not in i18n.DICO or not vals:
        return
    per = (src or {}).get("periode") or (src or {}).get("periode_annees") or []
    a0 = per[0] if per else ""
    a1 = per[-1] if per else ""
    lignes = sorted(vals.items(), key=lambda kv: -abs(kv[1]))
    st.markdown(
        f'<div class="sat-lab">{_e(T("sat_lecture"))}</div>'
        '<ul class="sat-puces">'
        + "".join(
            '<li>' + _e(T(cle, s=s, v=_f(abs(v), dec), vs=_f(v, dec),
                          a=a0, a2=a1)) + '</li>'
            for s, v in lignes)
        + '</ul>', unsafe_allow_html=True)


def _dossier(mesure, vals, unite, dec):
    """D'où vient la mesure, comment elle a été rattachée à la section, et
    ce que son barème en fait.

    TROIS QUESTIONS, ET ELLES SE POSENT DANS CET ORDRE. D'où vient le chiffre :
    quel capteur, quelle période, quelle résolution. Comment il devient le
    chiffre d'une section communale : par moyenne zonale sur le polygone, ce
    qui est la seule opération faite et qu'il faut dire, parce qu'elle a ses
    limites — à cinq kilomètres de résolution, une petite section tient dans
    une poignée de pixels. Ce qu'on doit en conclure : le barème publié et la
    phrase de lecture, tels qu'ils sont écrits dans le référentiel.

    UNE MESURE SANS BARÈME LE DIT. La moitié de ces mesures n'entre dans aucun
    score : le taire laisserait croire que tout ce qui est affiché ici pèse
    dans l'indice.
    """
    lang = i18n.get_lang()
    ligne = LIGNES.get(mesure[1])
    r = _referentiel().get(ligne) if ligne else None
    zonal = {"frag": "sat_ref_zonal_frag",
             "acces": "sat_ref_zonal_acces",
             "chl": "sat_ref_zonal_marin",
             "herb": "sat_ref_zonal_marin",
             "fin": "sat_ref_zonal_fin"}.get(mesure[3], "sat_ref_zonal")
    if mesure[3] in ("sol", "deg"):
        zonal = "sat_ref_zonal"
    with st.expander(T("sat_ref_t")):
        cal0 = "sat_calc_" + mesure[3]
        if not r:
            st.markdown(
                (f'<div class="sat-lab">{_e(T("sat_calc_t"))}</div>'
                 f'<p class="sat-note" style="max-width:none">'
                 f'{_e(T(cal0))}</p>' if cal0 in i18n.DICO else "")
                + f'<p class="sat-note" style="max-width:none">'
                  f'{_e(T("sat_ref_absent"))}</p>'
                  f'<p class="sat-note" style="max-width:none">'
                  f'{_e(T(zonal))}</p>',
                unsafe_allow_html=True)
            return
        note = (r.get("note") if lang == "fr" else r.get("note_en")) \
            or r.get("note") or ""
        expl = (r.get("expl_fr") if lang == "fr" else r.get("expl_en")) \
            or r.get("metrique") or ""
        sco = r.get("scores") or {}
        cal = "sat_calc_" + mesure[3]
        if cal in i18n.DICO:
            st.markdown(
                f'<div class="sat-lab">{_e(T("sat_calc_t"))}</div>'
                f'<p class="sat-note" style="max-width:none">{_e(T(cal))}</p>',
                unsafe_allow_html=True)
        st.markdown(
            f'<div class="sat-lab">{_e(T("sat_ref_src"))}</div>'
            f'<p class="sat-note" style="max-width:none">{_e(note)}</p>'
            f'<p class="sat-note" style="max-width:none">'
            f'{_e(T(zonal))}</p>'
            + (f'<div class="sat-lab">{_e(T("sat_ref_lire"))}</div>'
               f'<p class="sat-note" style="max-width:none">{_e(expl)}</p>'
               if expl else "")
            + (f'<div class="sat-lab">{_e(T("sat_ref_bar"))}</div>'
               f'<p class="sat-note" style="max-width:none">'
               f'{_e(r.get("echelle"))}</p>' if r.get("echelle") else ""),
            unsafe_allow_html=True)
        # LA COLONNE NOTÉE EST CELLE DU RÉFÉRENTIEL, PAS CELLE DU DESSIN.
        # Le barème d'un indice de végétation note souvent une VARIATION entre
        # deux fenêtres, quand le graphique au-dessus montre le NIVEAU de
        # l'année : accoler la note au niveau aurait fait lire « NDVI 0,60 donc
        # 10 sur 10 », ce qui est faux. Le tableau reprend donc la grandeur que
        # le barème note, telle qu'elle est écrite dans le référentiel, et la
        # nomme.
        val_ref = r.get("valeurs") or {}
        nom_ref = (r.get("indicateur_fr") if lang == "fr" else None) \
            or r.get("indicateur") or ""
        u_ref = (r.get("unite") or "").strip()
        lignes = [(x, val_ref.get(x), sco.get(x)) for x in sorted(vals)
                  if sco.get(x) is not None]
        if lignes:
            st.markdown(
                f'<div class="sat-lab">{_e(T("sat_ref_note"))}</div>'
                f'<p class="sat-note" style="margin:0 0 4px">'
                f'{_e(T("sat_ref_grade", n=nom_ref))}</p>'
                '<table class="sat-tab"><thead><tr>'
                f'<th>{_e(T("sat_col_sec"))}</th>'
                f'<th class="n">{_e(nom_ref)}'
                f'{(" (" + _e(u_ref) + ")") if u_ref else ""}</th>'
                f'<th class="n">{_e(T("sat_ref_note"))}</th></tr></thead><tbody>'
                + "".join(
                    f'<tr><td>{_e(x)}</td>'
                    f'<td class="n">{_e(_f(v, 2) if v is not None else "—")}</td>'
                    f'<td class="n v">{_e(n)} / 10</td></tr>'
                    for x, v, n in lignes)
                + '</tbody></table>'
                f'<p class="sat-note">{_e(T("sat_ref_note_x"))}</p>',
                unsafe_allow_html=True)
