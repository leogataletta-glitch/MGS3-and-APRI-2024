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
}

# LES ONGLETS, DANS L'ORDRE OÙ ON LES PARCOURT : ce qui couvre le sol, puis
# ce qui l'arrose, puis ce qui l'assèche.
CATEGORIES = ("foret", "vege", "eau", "pluie", "saison", "temp", "aridite")


TEXTES = {
    "sat_titre": {"en": "Satellite measurements",
                  "fr": "Mesures satellitaires"},
    "sat_intro": {
        "en": "Fifty-six measurements taken from orbit for each of the ten "
              "communal sections: forest, vegetation, surface water, "
              "rainfall since 1981, the rainy season, surface temperature "
              "since 2001 and the water balance. These are raw measurements, "
              "not scores: no scale has been applied to them.",
        "fr": "Cinquante-six mesures prises depuis l'orbite pour chacune des "
              "dix sections communales : forêt, végétation, eau de surface, "
              "pluie depuis 1981, saison des pluies, température de surface "
              "depuis 2001 et bilan hydrique. Ce sont des mesures brutes, "
              "pas des scores : aucun barème ne leur a été appliqué."},
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
    "sat_cd_foret": {"en": "Cover, loss and its pace",
                     "fr": "Couvert, perte et rythme de la perte"},
    "sat_cd_vege": {"en": "Greenness, moisture and their year-to-year swing",
                    "fr": "Verdeur, humidité et leur écart d'une année à "
                          "l'autre"},
    "sat_cd_eau": {"en": "Open water and its turbidity",
                   "fr": "Eau libre et sa turbidité"},
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
  .sat-tab th { font-size:10.5px; font-weight:700; letter-spacing:.09em;
       text-transform:uppercase; color:#8a93a5; text-align:left;
       padding:0 10px 7px 0; border-bottom:1px solid #e9eef4; }
  .sat-tab th.n, .sat-tab td.n { text-align:right;
       font-variant-numeric:tabular-nums; }
  .sat-tab td { font-size:12.5px; color:#3c4761; padding:7px 10px 7px 0;
       border-bottom:1px solid #f2f5f9; }
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
                     ("thermique", "thermique.json")):
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
        f'<p class="sat-note" style="margin:0 0 10px">{_e(T("sat_intro"))}</p>',
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
                  f'{_e(T("sat_ref_zonal"))}</p>',
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
            f'{_e(T("sat_ref_zonal"))}</p>'
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
