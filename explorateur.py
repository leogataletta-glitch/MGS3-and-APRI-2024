"""Explorateur de réponses — une question, une réponse, et qui répond quoi.

POURQUOI UN SECOND OUTIL À CÔTÉ DU CROISEMENT.
Le croisement libre construit un GROUPE : on empile des conditions — femme,
catégorie C, sans latrine — et on regarde le profil de résilience de ce
groupe. C'est puissant et c'est lent : il faut savoir quel groupe on cherche
avant de commencer.

L'explorateur pose la question inverse, et c'est la plus fréquente : « sur
CETTE question, qui répond CETTE réponse ? ». On choisit la question, la
réponse, l'axe de ventilation — les dix sections communales ou l'un des
quatre groupes d'intérêt — et la part se lit d'un coup, en barres ou en
radar, avec l'option de ne garder que les extrêmes.

LA PART EST CALCULÉE SUR LES RÉPONDANTS À LA QUESTION, PAS SUR L'ÉCHANTILLON.
Une question posée à six cents ménages sur mille deux cents donnerait des
parts deux fois trop basses si le dénominateur était l'échantillon entier :
on confondrait « peu de gens répondent ça » avec « peu de gens ont été
interrogés là-dessus ». Le dénominateur est donc, section par section, le
nombre de ménages de la section AYANT répondu à la question ; l'effectif est
affiché à côté de la part pour que le lecteur voie sur quoi elle porte.

LES EFFECTIFS TROP FAIBLES SONT SIGNALÉS, PAS CACHÉS. Une part calculée sur
huit répondants n'est pas fausse, elle est fragile : elle bouge de douze
points si un seul ménage change d'avis. Elle est donc affichée en pâle, avec
son effectif, plutôt que retirée — retirer une barre laisse croire qu'il n'y
a rien à cet endroit.
"""

import numpy as np
import itertools

import streamlit as st

import croisement_moteur as M
import i18n
import libelles_enquete
import map_render
import radar
from i18n import T

ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"
VERT_APRI = "#2a6b3f"
VERT, ROUGE, GRIS = "#1a8a4f", "#c33a24", "#8a93a5"

# LE SEUIL DE FRAGILITÉ EST CELUI DU MOTEUR. Deux seuils différents dans deux
# écrans du même site donneraient deux verdicts sur le même effectif.
N_FRAGILE = 20

# Les axes de ventilation. « section » est la localité ; les quatre autres
# sont les groupes d'intérêt, dans l'ordre où ils éclairent le plus souvent
# une différence.
# LA DIMENSION N'EST PLUS UN AXE, ELLE EST UNE MESURE. Tant que le score
# affiché était l'indice global, ventiler par dimension était la seule façon
# de voir les sept ; maintenant que la dimension — et même l'indicateur — se
# choisit comme on choisissait une question, la garder en axe donnerait deux
# chemins vers le même chiffre.
AXES = [("section", "ex_ax_section"),
        ("sexe", "ex_ax_sexe"),
        ("age", "ex_ax_age"),
        ("richesse", "ex_ax_richesse"),
        ("paysage", "ex_ax_paysage")]
_VALEURS = dict(M.REGISTRES)
# LES DIMENSIONS SONT DES CIBLES, PAS DES AXES : on les choisit comme on
# choisit une question, et le score obtenu se ventile ensuite sur les mêmes
# axes que tout le reste.
_DIMS = [c for c, _l in M.DIMENSIONS]

TEXTES = {
    "ex_titre": {"en": "Answer explorer", "fr": "Explorateur de réponses"},
    "ex_intro": {
        "en": "Pick a question, then an answer: the share of households "
              "giving that answer is broken down by communal section or by "
              "interest group. Shares are computed on the households who "
              "answered the question, never on the whole sample.",
        "fr": "Choisissez une question, puis une réponse : la part de ménages "
              "qui la donnent est ventilée par section communale ou par "
              "groupe d'intérêt. Les parts portent sur les ménages ayant "
              "répondu à la question, jamais sur l'échantillon entier."},
    "ex_question": {"en": "Question", "fr": "Question"},
    "ex_reponse": {"en": "Answer", "fr": "Réponse"},
    "ex_axe": {"en": "Project results by", "fr": "Projeter les résultats par"},
    "ex_axe2": {"en": "Then by", "fr": "Puis par"},
    "ex_dim_n": {"en": "Breakdown criterion {n}",
                 "fr": "Critère de ventilation {n}"},
    "ex_dim_cat": {"en": "Categories", "fr": "Catégories"},
    "ex_dim_plus": {"en": "Add a criterion", "fr": "Ajouter un critère"},
    "ex_tout_ech": {"en": "Whole sample", "fr": "Tout l'échantillon"},
    # --- comparer, et profiler
    "ex_c_sur": {"en": "Compare on", "fr": "Comparer sur"},
    "ex_c_scores": {"en": "Resilience scores", "fr": "Scores de résilience"},
    "ex_c_brut": {"en": "A survey answer", "fr": "Une réponse d'enquête"},
    "ex_c_sans_critere": {
        "en": "Add at least one breakdown criterion: a comparison needs "
              "groups to put side by side.",
        "fr": "Ajoutez au moins un critère de ventilation : une comparaison "
              "demande des groupes à mettre côte à côte."},
    "ex_p_qui": {"en": "Whose profile", "fr": "Le profil de qui"},
    "ex_p_tous": {"en": "All", "fr": "Tous"},
    "ex_p_forts": {"en": "Highest scores", "fr": "Les meilleurs scores"},
    "ex_p_faibles": {"en": "Lowest scores", "fr": "Les plus faibles scores"},
    "ex_p_n": {"en": "{n} households · overall index {s} / 10",
               "fr": "{n} ménages · indice global {s} / 10"},
    "ex_pourquoi_carte": {
        "en": "Map: available with the single criterion Communal section and "
              "one answer chosen.",
        "fr": "Carte : disponible avec le seul critère Section communale et "
              "une réponse choisie."},
    "ex_pourquoi_radar": {
        "en": "Radar: available with one answer chosen and at least three "
              "groups.",
        "fr": "Radar : disponible avec une réponse choisie et au moins trois "
              "groupes."},
    "ex_tout_x": {
        "en": "No breakdown: the result covers every household kept.",
        "fr": "Aucune ventilation : le résultat porte sur tous les ménages "
              "retenus."},
    "ex_dim_oter": {"en": "Remove", "fr": "Retirer"},
    "ex_dim_toutes": {"en": "All", "fr": "Toutes"},
    "ex_croiser_q": {"en": "Cross with a second question",
                     "fr": "Croiser avec une seconde question"},
    "ex_croiser_plus": {"en": "Cross with another question",
                        "fr": "Croiser avec une autre question"},
    "ex_croiser_n": {"en": "{n} crossed", "fr": "{n} croisées"},
    "ex_axe_non": {"en": "None", "fr": "Aucun"},
    "ex_ax_section": {"en": "Communal section", "fr": "Section communale"},
    "ex_ax_sexe": {"en": "Sex", "fr": "Sexe"},
    "ex_ax_age": {"en": "Age group", "fr": "Tranche d'âge"},
    "ex_ax_richesse": {"en": "Economic category", "fr": "Catégorie économique"},
    "ex_ax_paysage": {"en": "Landscape", "fr": "Paysage"},
    "ex_mesure": {"en": "Measure", "fr": "Mesure"},
    "ex_m_part": {"en": "Share of an answer", "fr": "Part d'une réponse"},
    "ex_m_score": {"en": "Resilience score", "fr": "Score de résilience"},
    # ---- l'explorateur de scores : filtres combinables, un seul dessin ----
    "ex_s_titre": {"en": "Resilience scores", "fr": "Scores de résilience"},
    "ex_s_dim": {"en": "Dimension", "fr": "Dimension"},
    "ex_s_ind": {"en": "Indicator", "fr": "Indicateur"},
    "ex_s_toutes": {"en": "All — overall index", "fr": "Toutes — indice global"},
    "ex_s_tous_i": {"en": "None — dimension score",
                    "fr": "Aucun — score de la dimension"},
    "ex_s_tous_i0": {"en": "None — overall index",
                     "fr": "Aucun — indice global"},
    "ex_s_axe": {"en": "Project results by",
                 "fr": "Projeter les résultats par"},
    "ex_s_aucun": {"en": "Nothing — the selection alone",
                   "fr": "Rien — la sélection seule"},
    "ex_s_ax_dim": {"en": "Dimension", "fr": "Dimension"},
    "ex_s_mode": {"en": "Analysis", "fr": "Analyse"},
    "ex_s_m_actuel": {"en": "Current score", "fr": "Score actuel"},
    "ex_s_m_bas": {"en": "Lowest scores", "fr": "Scores les plus bas"},
    "ex_s_m_haut": {"en": "Highest scores", "fr": "Scores les plus élevés"},
    "ex_s_m_ecarts": {"en": "Biggest differences between groups",
                      "fr": "Différences les plus fortes entre groupes"},
    "ex_s_combien": {"en": "How many", "fr": "Combien"},
    "ex_s_sel": {"en": "Selection", "fr": "Sélection"},
    "ex_s_ech": {"en": "Whole sample", "fr": "Échantillon entier"},
    "ex_s_ecart_ech": {"en": "Gap with the whole sample",
                       "fr": "Écart avec l'échantillon entier"},
    "ex_s_n": {"en": "{n} households of {t}",
               "fr": "{n} ménages sur {t}"},
    "ex_s_vide": {"en": "No household matches this combination. Widen one of "
                        "the filters.",
                  "fr": "Aucun ménage ne réunit cette combinaison. Élargissez "
                        "l'un des filtres."},
    "ex_s_rien": {"en": "This score cannot be computed on the selected "
                        "households.",
                  "fr": "Ce score ne peut pas être calculé sur les ménages "
                        "sélectionnés."},
    "ex_s_bas_i": {"en": "The lowest indicators on the selection",
                   "fr": "Les indicateurs les plus bas sur la sélection"},
    "ex_s_haut_i": {"en": "The highest indicators on the selection",
                    "fr": "Les indicateurs les plus hauts sur la sélection"},
    "ex_s_bas_a": {"en": "The lowest of the breakdown",
                   "fr": "Les plus bas de la ventilation"},
    "ex_s_haut_a": {"en": "The highest of the breakdown",
                    "fr": "Les plus hauts de la ventilation"},
    "ex_s_ec_t": {"en": "Group against group, ranked by the size of the gap",
                  "fr": "Groupe contre groupe, classés par la taille de "
                        "l'écart"},
    "ex_s_ec_x": {
        "en": "Every pair inside each register is compared — women against "
              "men, one age band against another, one locality against "
              "another — and the pairs are ranked by the size of the gap. The "
              "two groups compared are named on every row, so a gap is never "
              "read without knowing between whom it holds.",
        "fr": "Chaque paire à l'intérieur d'un registre est comparée — les "
              "femmes contre les hommes, une tranche d'âge contre une autre, "
              "une localité contre une autre — et les paires sont classées "
              "par la taille de l'écart. Les deux groupes comparés sont "
              "nommés sur chaque ligne : un écart ne se lit jamais sans "
              "savoir entre qui il tient."},
    "ex_s_ec_vs": {"en": "vs", "fr": "contre"},
    "ex_s_ec_col": {"en": "Comparison", "fr": "Comparaison"},
    "ex_s_ec_reg": {"en": "Register", "fr": "Registre"},
    "ex_s_ecart": {"en": "Gap", "fr": "Écart"},
    "ex_s_ec_rien": {"en": "No pair of groups can be compared on this score "
                           "within the selection.",
                     "fr": "Aucune paire de groupes n'est comparable sur ce "
                           "score dans la sélection."},
    "ex_s_carte_sec": {
        "en": "The map needs the communal sections: set the breakdown to "
              "Communal section.",
        "fr": "La carte demande les sections communales : mettez la "
              "ventilation sur Section communale."},
    "ex_score": {"en": "score out of 10", "fr": "score sur 10"},
    "ex_cible": {"en": "Resilience indicator",
                 "fr": "Indicateur de résilience"},
    "ex_c_global": {"en": "Overall resilience index",
                    "fr": "Indice de résilience global"},
    "ex_c_dims": {"en": "Dimensions", "fr": "Dimensions"},
    "ex_t_score": {"en": "Resilience score explorer",
                   "fr": "Explorateur des scores de résilience"},
    "ex_intro_score": {
        "en": "Pick the overall index, a dimension or a single indicator: its "
              "0–10 score is computed for every communal section, landscape "
              "and social group, on the households of each.",
        "fr": "Choisissez l'indice global, une dimension ou un indicateur : "
              "son score sur 10 est calculé pour chaque section communale, "
              "chaque paysage et chaque groupe social, sur les ménages de "
              "chacun."},
    "ex_tableau": {"en": "Table", "fr": "Tableau"},
    "ex_carte": {"en": "Map", "fr": "Carte"},
    "ex_carte_sec": {
        "en": "The map is drawn by communal section: it is available when "
              "the breakdown includes the communal sections.",
        "fr": "La carte se dessine par section communale : elle est "
              "disponible quand la ventilation contient les sections "
              "communales."},
    "ex_filtre": {"en": "Restrict to", "fr": "Restreindre à"},
    "ex_filtres_t": {"en": "Refine the population", "fr": "Affiner la population"},
    "ex_filtres_opt": {"en": "optional", "fr": "facultatif"},
    "ex_e2_t": {"en": "What do you want to explore?",
                "fr": "Qu'est-ce que vous voulez explorer ?"},
    "ex_e2_x": {"en": "Pick a question, an answer, and how to break down the "
                      "results.",
                "fr": "Choisissez une question, une réponse, et la façon dont "
                      "les résultats se ventilent."},
    "ex_e4_x": {"en": "{k} households match your selection, out of {n} "
                      "({p} %).",
                "fr": "{k} ménages correspondent à votre sélection, sur {n} "
                      "({p} %)."},
    "ex_voir": {"en": "View as", "fr": "Afficher en"},
    "ex_theme": {"en": "Theme", "fr": "Thème"},
    "ex_cond_t": {
        "en": "You can also keep only the households that gave a given "
              "answer to a second question — « both drinking water and "
              "improved sanitation » is that, and the count is read on the "
              "bars.",
        "fr": "Vous pouvez aussi ne garder que les ménages ayant donné une "
              "réponse à une seconde question — « à la fois l'eau potable et "
              "des sanitaires améliorés », c'est cela, et le compte se lit "
              "sur les barres."},
    "ex_cond_q": {"en": "Second question", "fr": "Seconde question"},
    "ex_cond_aucune": {"en": "No condition", "fr": "Aucune condition"},
    "ex_cond_r": {"en": "Answers kept", "fr": "Réponses retenues"},
    "ex_theme_tous": {"en": "All themes", "fr": "Tous les thèmes"},
    "ex_croise": {"en": "Crossed groups", "fr": "Groupes croisés"},
    "ex_s_comp": {"en": "Compare several indicators (optional)",
                  "fr": "Comparer plusieurs indicateurs (facultatif)"},
    "ex_s_comp_t": {"en": "The indicators compared, on the selected households",
                    "fr": "Les indicateurs comparés, sur les ménages retenus"},
    "ex_s_vent": {"en": "Project results by (optional)",
                  "fr": "Projeter les résultats par (facultatif)"},
    "ex_croise_x": {
        "en": "{k} crossed groups, out of {n} possible: the empty ones are "
              "left out. Crossing multiplies the groups and divides the "
              "numbers — read the count beside each bar.",
        "fr": "{k} groupes croisés, sur {n} possibles : les groupes vides "
              "sont écartés. Croiser multiplie les groupes et divise les "
              "effectifs — lisez le compte à côté de chaque barre."},
    "ex_dl": {"en": "Download results", "fr": "Télécharger les résultats"},
    "ex_filtres_x": {
        "en": "Several options can be picked in the same field: they add up. "
              "Two different fields narrow one after the other.",
        "fr": "Plusieurs options peuvent être retenues dans un même champ : "
              "elles s'additionnent. Deux champs différents restreignent l'un "
              "après l'autre."},
    "ex_raz": {"en": "Clear all", "fr": "Tout effacer"},
    "ex_res": {"en": "Results", "fr": "Résultats"},
    "ex_b_pop": {"en": "Population filters", "fr": "Filtres de population"},
    "ex_b_pop_n": {"en": "{n} active", "fr": "{n} actifs"},
    "ex_b_cond": {"en": "Add a condition", "fr": "Ajouter une condition"},
    "ex_b_cond_on": {"en": "Condition applied", "fr": "Condition appliquée"},
    "ex_b_raz": {"en": "Reset", "fr": "Réinitialiser"},
    "ex_b_moy": {"en": "Average", "fr": "Moyenne"},
    "ex_b_haut": {"en": "Highest", "fr": "Le plus haut"},
    "ex_b_bas": {"en": "Lowest", "fr": "Le plus bas"},
    "ex_b_ecart": {"en": "Widest gap", "fr": "Écart maximal"},
    "ex_b_source": {"en": "Source", "fr": "Source"},
    "ex_b_toutes": {"en": "All answers", "fr": "Toutes les réponses"},
    "ex_b_filtres": {"en": "Filters", "fr": "Filtres"},
    "ex_aucun_f": {"en": "No filter", "fr": "Aucun filtre"},
    "ex_f_section": {"en": "Communal section", "fr": "Section communale"},
    "ex_f_paysage": {"en": "Landscape", "fr": "Paysage"},
    "ex_f_tous": {"en": "All", "fr": "Tout"},
    "ex_filtre_n": {"en": "Restricted to {n} households of {t}.",
                    "fr": "Restreint à {n} ménages sur {t}."},
    "ex_filtre_vide": {
        "en": "No household matches all the restrictions at once.",
        "fr": "Aucun ménage ne réunit toutes les restrictions à la fois."},
    "ex_format": {"en": "Chart", "fr": "Graphique"},
    "ex_barres": {"en": "Bar chart", "fr": "Histogramme"},
    "ex_radar": {"en": "Radar chart", "fr": "Diagramme radar"},
    "ex_extremes": {"en": "Show", "fr": "Afficher"},
    "ex_tous": {"en": "All", "fr": "Tout"},
    "ex_top": {"en": "Highest three", "fr": "Les trois plus hauts"},
    "ex_flop": {"en": "Lowest three", "fr": "Les trois plus bas"},
    "ex_topflop": {"en": "Highest and lowest three",
                   "fr": "Les trois plus hauts et les trois plus bas"},
    "ex_ecart": {"en": "Biggest gap with the whole sample",
                 "fr": "Plus fort écart avec l'ensemble"},
    "ex_part": {"en": "share of respondents",
                "fr": "part des répondants"},
    "ex_ens": {"en": "All respondents", "fr": "Ensemble des répondants"},
    "ex_n": {"en": "{k} of {n} respondents",
             "fr": "{k} sur {n} répondants"},
    # L'INTITULÉ DE COLONNE N'EST PAS LA PHRASE. `ex_n` est un gabarit à deux
    # trous ; posé tel quel en tête de colonne, il s'affichait « {k} of {n}
    # respondents ». Une clé par usage.
    "ex_col_n": {"en": "respondents", "fr": "répondants"},
    "ex_c_nom": {"en": "group", "fr": "groupe"},
    "ex_c_k": {"en": "of which giving this answer",
               "fr": "dont donnant cette réponse"},
    "ex_fragile": {
        "en": "Bars in pale green rest on fewer than {n} respondents: they "
              "move by several points if one household answers differently.",
        "fr": "Les barres en vert pâle reposent sur moins de {n} répondants : "
              "elles bougent de plusieurs points si un seul ménage répond "
              "autrement."},
    "ex_vide": {"en": "No household answered this question in the selected "
                      "breakdown.",
                "fr": "Aucun ménage n'a répondu à cette question dans la "
                      "ventilation choisie."},
    "ex_radar_court": {
        "en": "A radar needs at least three points; this breakdown has "
              "fewer. Showing the bar chart.",
        "fr": "Un radar demande au moins trois sommets ; cette ventilation en "
              "compte moins. L'histogramme est affiché."},
    "ex_radar_ech": {
        "en": "The radar is drawn on a 0–10 scale: a share of {p} % sits at "
              "{v} on the web.",
        "fr": "Le radar est tracé sur une échelle de 0 à 10 : une part de "
              "{p} % se lit {v} sur la toile."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)

STYLE = """
<style>
  .ex-lab { font-size:10.5px; font-weight:700; letter-spacing:.09em;
            text-transform:uppercase; color:#8a93a5; margin:0 0 4px; }
  .ex-tab { width:100%; border-collapse:collapse; margin-top:14px; }
  .ex-tab th { font-size:10.5px; font-weight:700; letter-spacing:.09em;
            text-transform:uppercase; color:#8a93a5; text-align:left;
            padding:0 10px 7px 0; border-bottom:1px solid #e9eef4; }
  .ex-tab th.n, .ex-tab td.n { text-align:right;
            font-variant-numeric:tabular-nums; }
  .ex-tab td { font-size:12.5px; color:#3c4761; padding:7px 10px 7px 0;
            border-bottom:1px solid #f2f5f9; }
  .ex-tab td.v { font-weight:700; color:#101728; }
  .ex-note { font-size:11.5px; color:#8a93a5; line-height:1.5;
            margin:10px 0 0; text-align:left !important; }
  .ex-tab tr.pale td { opacity:.55; }
  .ex-kpi { display:flex; gap:14px; flex-wrap:wrap; margin:6px 0 4px; }
  .ex-k { flex:1 1 190px; background:#fff; border:1px solid #e3eaf3;
            border-radius:12px; padding:12px 15px; }
  .ex-k-l { font-size:10.5px; font-weight:700; letter-spacing:.08em;
            text-transform:uppercase; color:#8a93a5; }
  .ex-k-v { font-size:24px; font-weight:700; color:#101728; line-height:1.1;
            margin-top:4px; font-variant-numeric:tabular-nums; }
  .ex-k-u { font-size:13px; font-weight:400; color:#8a93a5; }
  .ex-k-s { font-size:11px; color:#8a93a5; margin-top:3px; }

  /* --- LA HIÉRARCHIE DE L'ÉCRAN, ÉCRITE PLUTÔT QUE SUGGÉRÉE --------------
     Cinq moments se suivent — la question, la réponse, la ventilation, les
     filtres, les résultats — et rien ne le disait : cinq rangées de menus
     de même graisse se lisaient comme un formulaire à remplir dans un ordre
     quelconque. Un numéro et un filet suffisent à dire l'ordre ; il n'y a
     ni pictogramme ni couleur de plus. */
  /* --- « AFFICHER EN » : QUATRE BOUTONS ACCOLÉS, PAS UN MENU ------------
     Le format de dessin n'est pas un réglage qu'on va chercher : on en
     change deux fois par lecture. Un menu déroulant demande d'ouvrir, viser
     et choisir ; quatre boutons côte à côte se cliquent d'un geste, et le
     format courant se voit sans être ouvert. */
  div[class*="st-key-ex_forme"] div[role="radiogroup"] {
      display:flex !important; gap:0 !important; flex-wrap:nowrap !important;
      border:1px solid #cddbd2; border-radius:9px; overflow:hidden;
      width:fit-content;
  }
  div[class*="st-key-ex_forme"] div[role="radiogroup"] > label {
      margin:0 !important; padding:7px 15px !important; cursor:pointer;
      background:#fff !important; border-right:1px solid #e4eae6 !important;
      border-radius:0 !important;
  }
  div[class*="st-key-ex_forme"] div[role="radiogroup"] > label:last-child {
      border-right:0 !important;
  }
  div[class*="st-key-ex_forme"] div[role="radiogroup"]
      > label > div > div > div:first-child { display:none !important; }
  div[class*="st-key-ex_forme"] div[role="radiogroup"] > label p {
      font-size:12px !important; font-weight:600 !important;
      color:#3c4761 !important; margin:0 !important; white-space:nowrap;
  }
  div[class*="st-key-ex_forme"] div[role="radiogroup"]
      > label:has(input:checked) { background:#1a6b52 !important; }
  div[class*="st-key-ex_forme"] div[role="radiogroup"]
      > label:has(input:checked) p { color:#fff !important; }
  div[class*="st-key-ex_forme"] div[role="radiogroup"] > label:hover {
      background:#eef5f1 !important;
  }
  div[class*="st-key-ex_forme"] div[role="radiogroup"]
      > label:has(input:checked):hover { background:#175c46 !important; }

  /* La ligne qui ouvre les résultats : l'effectif retenu à gauche, le
     téléchargement à droite. */
  .ex-res-x { font-size:12.5px; color:#6b7590; line-height:1.5;
            margin:0 0 10px 33px; }

  /* --- LE PANNEAU DES FILTRES --------------------------------------------
     Les menus se fondaient dans la page : rien ne disait où commençait la
     restriction ni ce qui était retenu. Le panneau leur donne un fond, un
     bord et un titre — assez pour qu'on le trouve d'un coup d'œil, assez peu
     pour qu'il ne pèse pas plus que les résultats qu'il commande. */
  /* UN TITRE DE RÉSULTAT, ET RIEN DE PLUS. Il ressemble à la pastille du
     site sans en porter la classe : celle-ci déclenche, sur le bloc qui la
     contient, la mise en carte générale — et le bloc, ici, c'est la page. */
  .ex-titre { display:inline-flex; align-items:center; gap:9px;
            font-weight:700; font-size:12px; letter-spacing:.06em;
            text-transform:uppercase; color:#1a6b52; background:#eaf5f0;
            padding:6px 13px; border-radius:999px; margin:0 0 4px; }
  .ex-pan-x { font-size:11.5px; color:#6b7590; line-height:1.5;
            margin:0 0 10px; max-width:92ch; text-align:left !important; }
  /* L'OPTION DÉJÀ RETENUE SE VOIT DANS LA LISTE OUVERTE. Sans quoi, rouvrir
     un champ chargé oblige à comparer la liste aux étiquettes pour savoir ce
     qui est déjà pris. La liste est posée par le navigateur hors du panneau :
     la règle ne peut pas être portée par la clé du conteneur. */
  [role="option"][aria-selected="true"] {
      background:#eef5f1 !important; color:#1a6b52 !important;
      font-weight:600 !important;
  }
  /* « SELECT ALL » EST RETIRÉ DE LA LISTE. Streamlit l'écrit en anglais quel
     que soit le site, et il ne dit rien de plus que le champ vide : ne rien
     retenir, c'est déjà tout retenir. Dix étiquettes pour dire « tout » ne
     seraient qu'une façon plus lourde de ne rien filtrer. */
  [role="option"][data-key="__select_all__"] { display:none !important; }
</style>
"""

# LA FEUILLE DU PANNEAU EST À PART, parce qu'elle vise des clés de conteneur
# que Streamlit ne pose qu'au moment du rendu : elle est émise une fois par
# panneau, avec la clé exacte, et n'a donc rien à faire dans la feuille
# générale.
_CSS_PANNEAU = """
<style>
  div[class*="st-key-KEY"] {
      background: linear-gradient(180deg,#f3f8f5 0%,#fbfcfb 100%);
      border: 1px solid #d5e2da; border-radius: 14px;
      padding: 14px 16px 6px; margin: 2px 0 4px;
  }
  /* LES INTITULÉS DE CHAMP SONT PLUS FRANCS QUE CEUX DE LA PAGE. Dans un
     panneau teinté, le gris pâle des libellés Streamlit devenait illisible ;
     ils passent en encre et en capitales espacées, comme les en-têtes de
     colonne des tableaux. */
  div[class*="st-key-KEY"] label p {
      font-size: 10.5px !important; font-weight: 700 !important;
      letter-spacing: .09em !important; text-transform: uppercase !important;
      color: #3c4761 !important;
  }
  /* LE CHAMP LUI-MÊME. Cette version de Streamlit ne dessine plus ses menus
     avec BaseWeb mais avec react-aria : le contrôle est le `div[role=group]`
     du champ, les options retenues sont des `span[data-tag]`, et une feuille
     écrite pour l'ancien jeu d'attributs ne toucherait rien du tout. */
  div[class*="st-key-KEY"] div[data-testid="stMultiSelect"] div[role="group"] {
      background: #fff !important; border: 1px solid #cddbd2 !important;
      border-radius: 9px !important; min-height: 38px;
      /* UN CHAMP CHARGÉ NE POUSSE PAS LA PAGE. Dix sections retenues
         donneraient un champ haut de quatre rangées et les cinq colonnes se
         désaligneraient ; au-delà de trois rangées, on fait défiler dans le
         champ. */
      max-height: 108px; overflow-y: auto !important;
  }
  /* LE CHAMP QUI PORTE UNE SÉLECTION SE VOIT DE LOIN : bord vert et halo. */
  div[class*="st-key-KEY"] div[data-testid="stMultiSelect"]
      div[role="group"]:has(span[data-tag]) {
      border-color: #1a6b52 !important;
      box-shadow: 0 0 0 1px rgba(26,107,82,.16) !important;
  }
  /* CHAQUE OPTION RETENUE EST UNE ÉTIQUETTE VERTE, AVEC SA CROIX. C\'est le
     seul endroit du site où le vert profond sert de fond à du texte : ici il
     dit « retenu », et la croix dit qu\'on peut le retirer sans rouvrir le
     menu. */
  div[class*="st-key-KEY"] span[data-tag] {
      background: #1a6b52 !important; border: none !important;
      border-radius: 7px !important;
      display: inline-flex !important; align-items: center !important;
      gap: 3px !important;
      margin: 2px 4px 2px 0 !important; padding: 2px 5px 2px 8px !important;
  }
  div[class*="st-key-KEY"] span[data-tag] > span {
      color: #fff !important; font-size: 11px !important;
      font-weight: 600 !important;
  }
  div[class*="st-key-KEY"] span[data-tag] button {
      color: #fff !important; opacity: .8; border-radius: 4px !important;
  }
  div[class*="st-key-KEY"] span[data-tag] button:hover {
      opacity: 1; background: rgba(255,255,255,.22) !important;
  }
  div[class*="st-key-KEY"] span[data-tag] svg { stroke: #fff !important; }
  /* LE BOUTON D\'EFFACEMENT EST UNE MENTION, PAS UNE ACTION PRINCIPALE. */
  div[class*="st-key-KEY"] div[data-testid="stButton"] > button {
      background: transparent !important; border: 1px solid #cddbd2 !important;
      color: #1a6b52 !important; border-radius: 8px !important;
      min-height: 30px !important; height: 30px !important;
      padding: 0 12px !important; width: 100% !important;
  }
  div[class*="st-key-KEY"] div[data-testid="stButton"] > button p {
      font-size: 11px !important; font-weight: 600 !important;
      color: #1a6b52 !important; letter-spacing: .02em !important;
  }
  div[class*="st-key-KEY"] div[data-testid="stButton"] > button:hover {
      background: #eaf2ed !important; border-color: #1a6b52 !important;
  }
</style>
"""


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _n(v):
    """Un effectif, avec sa séparation de milliers dans la langue du site."""
    s = f"{int(v):,}"
    return s.replace(",", "\u202f") if i18n.get_lang() == "fr" else s


def _f(v, dec=1):
    if v is None:
        return "—"
    s = f"{v:.{dec}f}"
    return s.replace(".", ",") if i18n.get_lang() == "fr" else s


def _lib(v):
    """Le libellé d'une valeur de segmentation, dans la langue courante."""
    cles = {"Homme": "hommes", "Femme": "femmes", "Cat A": "cat_a",
            "Cat B": "cat_b", "Cat C": "cat_c", "<25": "age_25",
            "25-39": "age_25_39", "40-59": "age_40_59", "60+": "age_60",
            "Littoral": "pay_Littoral", "Montagne": "pay_Montagne"}
    return T(cles[v]) if v in cles else v


def _masque_multi(cat, choix):
    """Le sous-échantillon retenu par des filtres à choix multiples.

    DEUX LOGIQUES, ET C'EST CE QUI REND LE PANNEAU UTILE. À l'intérieur d'un
    même champ, les options s'ADDITIONNENT : « Anse à Drick, Barbois, Dumont »
    retient les ménages des trois sections réunies, parce que personne n'a
    jamais voulu dire « les ménages qui sont à la fois dans trois sections »
    — la phrase n'a pas de sens. Entre deux champs, elles se CUMULENT :
    « ces trois sections » ET « les femmes » restreint deux fois de suite.
    Un champ vide ne restreint rien.
    """
    m = np.ones(cat["n"], dtype=bool)
    for _axe, vals in choix.items():
        vals = [v for v in (vals or []) if v]
        if not vals:
            continue
        ou = np.zeros(cat["n"], dtype=bool)
        for v in vals:
            g = cat["groupes"].get(v)
            if g is not None:
                ou |= g
        m &= ou
    return m


def _etape(n, cle, aide=None, note=None):
    """Un numéro cerclé, un intitulé, et la ligne qui dit quoi faire.

    LE NUMÉRO EST DANS UN DISQUE, ET IL COMPTE. Quatre moments se suivent —
    la source, la question, la population, le résultat — et un chiffre posé
    à plat dans une rangée de libellés se lisait comme un rang de colonne.
    Cerclé, il se lit comme une étape, et l'œil retrouve où il en est sans
    relire les titres.

    LA LIGNE D'AIDE EST SOUS LE TITRE, PAS DEDANS. Elle dit ce qu'on fait à
    cette étape ; le titre dit ce qu'elle est. Les deux sur la même ligne
    donnaient une phrase à rallonge dont on ne lisait que le début.
    """
    sup = (f'<span class="ex-etape-o">{_e(T(note))}</span>') if note else ""
    st.markdown(
        f'<div class="ex-etape"><span class="n">{n}</span>'
        f'<span class="t">{_e(T(cle))}</span>{sup}<span class="l"></span></div>'
        + (f'<p class="ex-etape-x">{_e(T(aide))}</p>' if aide else ""),
        unsafe_allow_html=True)


def _condition_question(cat, questions, filtre):
    """Une seconde question posée comme condition sur la population.

    POURQUOI UNE QUESTION PEUT ÊTRE UN FILTRE. « Combien de ménages ont à la
    fois l'eau potable ET des sanitaires améliorés » n'est pas une question
    de plus : c'est la première question posée sur la population de la
    seconde. Les cinq registres du panneau ne savent filtrer que sur le
    profil — section, sexe, âge, richesse, paysage — et aucune combinaison de
    profils ne dit « ceux qui ont répondu Oui à l'eau ».

    LE COMPTE DE L'INTERSECTION EST DÉJÀ À L'ÉCRAN. La barre affiche k/n : n
    est l'effectif qui remplit la condition et a répondu à la question, k
    ceux qui donnent en plus la réponse choisie. « À la fois l'un et
    l'autre », c'est k.
    """
    st.markdown(f'<p class="ex-etape-x" style="margin:14px 0 2px 0 !important">'
                f'{_e(T("ex_cond_t"))}</p>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.7, 1.3])
    with c1:
        themes = sorted({x.get("category") or "" for x in questions},
                        key=lambda c: _nom_theme(c).lower())
        th = st.selectbox(T("ex_theme"), [None] + themes, key="ex_c_th",
                          format_func=lambda c: (T("ex_theme_tous")
                                                 if c is None else _nom_theme(c)))
    vues = [x for x in questions if th is None or (x.get("category") or "") == th]
    with c2:
        qi = st.selectbox(
            T("ex_cond_q"), [None] + [x["i"] for x in vues],
            key=f"ex_c_q_{th or 'tous'}",
            format_func=lambda i: (T("ex_cond_aucune") if i is None
                                   else _libelle_question(
                                       next(x for x in vues if x["i"] == i),
                                       avec_theme=th is None)))
    if qi is None:
        return filtre, None
    q2 = next(x for x in vues if x["i"] == qi)
    with c3:
        reps = st.multiselect(T("ex_cond_r"), q2["modalites"],
                              key=f"ex_c_r_{qi}",
                              format_func=libelles_enquete.modalite)
    if not reps:
        return filtre, None
    m = np.zeros(cat["n"], dtype=bool)
    for r in reps:
        m |= cat["bits"][q2["debut"] + q2["modalites"].index(r)]
    return filtre & m, (q2, reps)


def _panneau_filtres(cat, cle, registres, num, titre_cle, note=None):
    """Le panneau des filtres : un champ à choix multiples par registre.

    POURQUOI UN PANNEAU ET PLUS UNE RANGÉE DE MENUS. Les cinq menus vivaient
    au milieu de la page, de la même couleur qu'elle et de la même graisse
    que les commandes d'affichage : on ne savait ni où commençait la
    restriction, ni ce qui était retenu, ni comment revenir en arrière. Le
    panneau répond aux trois d'un coup — un fond, un titre, et un bouton qui
    remet tout à zéro.

    LE BOUTON EST RENDU AVANT LES CHAMPS, ET C'EST LOAD-BEARING. Streamlit
    interdit d'écrire dans l'état d'un widget déjà construit : vider les
    sélections depuis un bouton posé APRÈS les champs lèverait une exception.
    Posé avant, il vide l'état pendant que les champs n'existent pas encore,
    et ils naissent vides dans la même passe — sans second aller-retour.
    """
    st.markdown(_CSS_PANNEAU.replace("KEY", cle), unsafe_allow_html=True)
    cles = {axe: f"{cle}_{axe}" for axe, _l in registres}
    with st.container(key=cle):
        h1, h2 = st.columns([5, 1], vertical_alignment="center")
        with h1:
            st.markdown(
                f'<div class="ex-etape" style="margin:0 0 3px">'
                f'<span class="n">{num}</span>'
                f'<span class="t">{_e(T(titre_cle))}</span>'
                + (f'<span class="ex-etape-o">{_e(T(note))}</span>'
                   if note else "")
                + f'<span class="l"></span></div>'
                f'<p class="ex-pan-x">{_e(T("ex_filtres_x"))}</p>',
                unsafe_allow_html=True)
        with h2:
            if st.button(T("ex_raz"), key=f"{cle}_raz"):
                for k in cles.values():
                    st.session_state[k] = []
        cols = st.columns(len(registres))
        choix = {}
        for (axe, lab), col in zip(registres, cols):
            with col:
                choix[axe] = st.multiselect(
                    T(lab), list(_VALEURS.get(axe, [])), key=cles[axe],
                    placeholder=T("ex_f_tous"), format_func=_lib)
    poses = [(a, v) for a, vs in choix.items() for v in (vs or [])]
    return _masque_multi(cat, choix), poses


# LES CINQ REGISTRES DE RESTRICTION, DANS L'ORDRE OÙ ON LES PENSE : où, puis
# qui. Ils étaient décrits deux fois — une liste ici, une autre pour les
# scores — et les deux écrans avaient fini par ne plus proposer tout à fait
# les mêmes intitulés.
_REGISTRES_F = [("section", "ex_f_section"), ("sexe", "ex_ax_sexe"),
                ("age", "ex_ax_age"), ("richesse", "ex_ax_richesse"),
                ("paysage", "ex_f_paysage")]


def _carte(lignes):
    """La part par section communale, portée sur la carte du territoire.

    LA CARTE NE MONTRE QUE LES SECTIONS. Les autres axes — sexe, âge,
    catégorie — n'ont pas de géographie : les porter sur une carte
    inventerait un territoire qu'ils n'ont pas.
    """
    vals = {l["cle"]: l["part"] for l in lignes
            if l.get("axe_code") == "section" and l["part"] is not None}
    if len(vals) < 2:
        return None
    dispo = list(vals.values())
    seuils = map_render.nice_thresholds(dispo)
    svg, seuils_ret, _m = map_render.render_map_svg(
        vals, {s: 1 for s in vals}, seuils, height=560,
        polarity="neutre", unite="%")
    legende = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:7px;'
        f'margin-right:16px"><span style="width:20px;height:11px;'
        f'border-radius:3px;background:{c}"></span>'
        f'<span style="font-size:11.5px;color:#52514e">{lab}</span></span>'
        for c, lab in map_render.legend_items(seuils_ret, "neutre", "%"))
    return (f'<div style="margin:6px 0 8px">{legende}</div>{svg}')


def _cases(cat, axe):
    """Les cases d'un axe : (clé technique, libellé affiché)."""
    return [(v, _lib(v)) for v in _VALEURS.get(axe, [])]


def _nom_ind(ind):
    return ((ind.get("nom_fr") or ind.get("nom")) if i18n.get_lang() == "fr"
            else (ind.get("nom") or ind.get("nom_fr")))


def _inds_tries(cat):
    """Les indicateurs calculables, rangés par dimension puis par nom."""
    return sorted(cat.get("indicateurs") or [],
                  key=lambda x: (x["dim"], _nom_ind(x)))


def _mesure_ind(ind, masque):
    """Le score d'UN indicateur sur UN masque, sans calculer les autres.

    `profil` calcule les soixante-six indicateurs d'un coup ; pour une
    ventilation en dix sections, en demander un seul par ce chemin ferait six
    cent soixante calculs pour n'en afficher que dix.
    """
    base = ind["base"] & masque
    nb = int(base.sum())
    if nb == 0:
        return 0, None
    val = 100.0 * float((ind["cible"] & masque).sum()) / nb
    return nb, M._score_de(val, ind["bornes"], ind["decroissant"])


def _cibles(cat):
    """Ce qu'on peut mesurer : l'indice, les dimensions, les indicateurs.

    LA CIBLE REMPLACE LA QUESTION, ELLE NE S'AJOUTE PAS À ELLE. Sur les
    résultats bruts on choisit une question puis une réponse ; sur les scores
    il n'y a rien à choisir dans les réponses — le score est déjà l'agrégat de
    toutes. Ce qui reste à choisir, c'est le NIVEAU : l'indice global, l'une
    des dimensions, ou l'un des indicateurs qui les composent.

    Les codes sont stables (`global`, `d:dim3`, `i:12`) parce qu'ils sont
    retenus en session : un index de liste changerait de cible dès que la
    langue change l'ordre alphabétique des indicateurs.
    """
    inds = _inds_tries(cat)
    opts = [("global", T("ex_c_global"), None)]
    for c in _DIMS:
        opts.append((f"d:{c}", f'{T("ex_c_dims")} · {T(c)}', None))
    for k, ind in enumerate(inds):
        opts.append((f"i:{k}", f'{T(ind["dim"])} · {_nom_ind(ind)}', ind))
    return opts


def _croisements(cat, axes):
    """Le produit des cases des registres retenus, cases vides écartées.

    CROISER, C'EST MULTIPLIER LES GROUPES ET DIVISER LES EFFECTIFS. « Section
    × sexe × âge » fait quatre-vingts groupes possibles sur mille deux cent
    onze ménages : beaucoup sont vides, et parmi ceux qui ne le sont pas,
    certains tiennent sur cinq répondants. Les vides sont écartés ici ; les
    petits restent, signalés en vert pâle par le graphique, parce que les
    cacher reviendrait à décider à la place du lecteur ce qu'il a le droit de
    regarder.

    L'ORDRE EST CELUI DES REGISTRES, dans l'ordre où ils ont été choisis : le
    premier registre varie le plus lentement, si bien que les groupes d'une
    même section restent groupés.
    """
    listes = []
    for axe in axes:
        cases = [(v, lib, cat["groupes"].get(v)) for v, lib in _cases(cat, axe)]
        listes.append([c for c in cases if c[2] is not None])
    if not listes or any(not l for l in listes):
        return []
    out = []
    for combo in itertools.product(*listes):
        m = combo[0][2].copy()
        for _v, _lib, g in combo[1:]:
            m &= g
        if not m.any():
            continue
        out.append((" · ".join(c[1] for c in combo),
                    "|".join(c[0] for c in combo), m))
    return out


def _croisements_choisis(cat, dims):
    """Le produit des CATÉGORIES RETENUES de chaque dimension, dans l'ordre.

    C'EST LE MÊME CROISEMENT QU'AVANT, MAIS SUR CE QU'ON A DEMANDÉ. La
    version précédente prenait toutes les cases de chaque registre : demander
    « section × sexe » donnait les vingt combinaisons, et il n'y avait aucun
    moyen de n'en garder que les femmes de deux sections. Les catégories
    retenues sont filtrées AVANT le produit, ce qui revient exactement à
    filtrer la population puis à grouper — dans cet ordre-là.

    `dims` est une liste ordonnée de couples (registre, valeurs retenues). La
    première dimension varie le plus lentement, si bien que les groupes d'une
    même section restent groupés.
    """
    listes = []
    for axe, gardees in dims:
        cases = [(v, lib, cat["groupes"].get(v)) for v, lib in _cases(cat, axe)
                 if not gardees or v in gardees]
        listes.append([c for c in cases if c[2] is not None])
    if not listes or any(not l for l in listes):
        return []
    out = []
    for combo in itertools.product(*listes):
        m = combo[0][2].copy()
        for _v, _lib, g in combo[1:]:
            m &= g
        if not m.any():
            continue
        out.append((" · ".join(c[1] for c in combo),
                    "|".join(c[0] for c in combo), m))
    return out


def _ventiler_dims(cat, q, modalite, dims, filtre):
    """Une ligne par groupe demandé : les dimensions servent de groupby.

    LA PROJECTION S'APPLIQUE MÊME SANS RÉPONSE CHOISIE, et c'est la seule
    lecture cohérente. « Section communale + sexe » demande les résultats de
    la question pour les femmes et pour les hommes DANS chaque section :
    sans réponse désignée, le résultat d'une question est la répartition de
    ses réponses, et c'est donc cette répartition qui est calculée dans
    chaque groupe. Une réponse désignée ramène chaque groupe à un seul
    chiffre — la part qui a répondu cela.

    LE DÉNOMINATEUR EST LE NOMBRE DE RÉPONDANTS À LA QUESTION dans le groupe.
    Sans lui, cent pour cent sur trois ménages et cent pour cent sur cent
    quarante se liraient pareil.
    """
    m_rep = np.zeros(cat["n"], dtype=bool)
    for j in range(len(q["modalites"])):
        m_rep |= cat["bits"][q["debut"] + j]
    m_rep &= filtre
    groupes = (_croisements_choisis(cat, dims) if dims
               else [(T("ex_tout_ech"), "tout",
                      np.ones(cat["n"], dtype=bool))])
    out = []
    if modalite is None:
        # UNE BARRE PAR RÉPONSE ET PAR GROUPE, le groupe servant d'intertitre :
        # dix sections et deux sexes donnent vingt blocs de deux barres, et
        # l'on compare les réponses à l'intérieur d'un groupe autant que les
        # groupes entre eux.
        for lib, cle, g in groupes:
            base = int((m_rep & g).sum())
            for j, mod in enumerate(q["modalites"]):
                k = int((cat["bits"][q["debut"] + j] & m_rep & g).sum())
                out.append({"nom": libelles_enquete.modalite(mod),
                            "cle": f"{cle}|{mod}", "axe": lib,
                            "axe_code": "groupe", "n": base, "k": k,
                            "part": (100 * k / base) if base else None})
        ens_base = int(m_rep.sum())
        return out, {"n": ens_base, "k": None, "part": None}

    m_mod = cat["bits"][q["debut"] + q["modalites"].index(modalite)] & filtre
    lib_axe = (T(dict(AXES)[dims[0][0]]) if len(dims) == 1
               else T("ex_croise") if dims else T("ex_tout_ech"))
    for lib, cle, g in groupes:
        base = int((m_rep & g).sum())
        k = int((m_mod & g).sum())
        out.append({"nom": lib, "cle": cle, "axe": lib_axe,
                    "axe_code": (dims[0][0] if len(dims) == 1
                                 else "croisement" if dims else "tout"),
                    "n": base, "k": k,
                    "part": (100 * k / base) if base else None})
    ens_base = int(m_rep.sum())
    return out, {"n": ens_base, "k": int(m_mod.sum()),
                 "part": (100 * int(m_mod.sum()) / ens_base)
                 if ens_base else None}


def _ventiler(cat, mesure, q, modalite, axes, filtre=None, cible=None):
    """Une ligne par case, pour tous les axes retenus, dans leur ordre.

    LES AXES S'ADDITIONNENT, ILS NE SE CROISENT PAS. Cumuler « localité » et
    « sexe » donne douze lignes — dix sections puis deux sexes — et non vingt
    croisements. Le croisement de deux axes divise l'effectif par vingt et
    produit des cases de trois ménages ; l'outil qui sert à cela est le
    constructeur libre, juste en dessous, qui affiche l'effectif de chaque
    condition posée.

    LE DÉNOMINATEUR EST LE NOMBRE DE RÉPONDANTS À LA QUESTION dans la case,
    et il est renvoyé avec la part : sans lui, 100 % sur trois ménages et
    100 % sur cent quarante se liraient pareil.
    """
    if filtre is None:
        filtre = np.ones(cat["n"], dtype=bool)
    if mesure == "score":
        return _ventiler_score(cat, axes, filtre, cible)

    m_rep = np.zeros(cat["n"], dtype=bool)          # a répondu à la question
    for j in range(len(q["modalites"])):
        m_rep |= cat["bits"][q["debut"] + j]
    m_rep &= filtre
    m_mod = cat["bits"][q["debut"] + q["modalites"].index(modalite)] & filtre

    out = []
    if len(axes) > 1:
        for lib, cle, g in _croisements(cat, axes):
            base = int((m_rep & g).sum())
            k = int((m_mod & g).sum())
            out.append({"nom": lib, "cle": cle, "axe": T("ex_croise"),
                        "axe_code": "croisement", "n": base, "k": k,
                        "part": (100 * k / base) if base else None})
    else:
        for axe in axes:
            for v, lib in _cases(cat, axe):
                g = cat["groupes"].get(v)
                if g is None:
                    continue
                base = int((m_rep & g).sum())
                out.append({"nom": lib, "cle": v, "axe": T(dict(AXES)[axe]),
                            "axe_code": axe,
                            "n": base, "k": int((m_mod & g).sum()),
                            "part": (100 * int((m_mod & g).sum()) / base)
                                    if base else None})
    ens_base = int(m_rep.sum())
    ens = {"n": ens_base, "k": int(m_mod.sum()),
           "part": (100 * int(m_mod.sum()) / ens_base) if ens_base else None}
    return out, ens


def _score_cible(cat, masque, cible, ind):
    """Le score de la cible choisie sur un sous-échantillon : (n, score).

    LES TROIS NIVEAUX SE CALCULENT SUR LES MÊMES MÉNAGES, jamais sur trois
    échantillons différents : l'indice global, la dimension et l'indicateur
    d'une même section portent sur la section, et se lisent donc l'un à côté
    de l'autre sur la même échelle de 0 à 10.

    L'EFFECTIF D'UN INDICATEUR EST SA BASE, pas la case entière. Un indicateur
    qui ne concerne que les ménages cultivateurs n'est pas calculé sur les
    autres ; annoncer l'effectif de la case laisserait croire que le score
    porte sur tout le monde.
    """
    nb = int(masque.sum())
    if not nb:
        return 0, None
    if ind is not None:
        return _mesure_ind(ind, masque)
    ag = M.agreger(M.profil(cat, masque))
    if cible == "global":
        return nb, ag["global"]
    return nb, ag["dimensions"].get(cible.split(":", 1)[1])


def _ventiler_score(cat, axes, filtre=None, cible=None):
    """Le score de la cible choisie, case par case, pour tous les axes.

    LA CIBLE EST CE QU'ON MESURE, L'AXE EST LÀ OÙ ON LE MESURE. Tant que le
    chiffre affiché était forcément l'indice global, la dimension devait être
    un axe pour qu'on puisse en voir sept ; maintenant qu'elle se choisit
    comme cible, elle sortirait deux fois du même écran.
    """
    tout = filtre if filtre is not None else np.ones(cat["n"], dtype=bool)
    cible = cible or "global"
    ind = None
    if cible.startswith("i:"):
        inds = _inds_tries(cat)
        k = int(cible.split(":", 1)[1])
        ind = inds[k] if k < len(inds) else None
        if ind is None:
            cible = "global"

    out = []
    if len(axes) > 1:
        for lib, cle, g in _croisements(cat, axes):
            nb, sc = _score_cible(cat, g & tout, cible, ind)
            out.append({"nom": lib, "cle": cle, "axe": T("ex_croise"),
                        "axe_code": "croisement", "n": nb,
                        "k": None, "part": sc, "score": sc})
    else:
        for axe in axes:
            for v, lib in _cases(cat, axe):
                g = cat["groupes"].get(v)
                if g is None:
                    continue
                nb, sc = _score_cible(cat, g & tout, cible, ind)
                out.append({"nom": lib, "cle": v, "axe": T(dict(AXES)[axe]),
                            "axe_code": axe, "n": nb,
                            "k": None, "part": sc, "score": sc})
    nb_t, sc_t = _score_cible(cat, tout, cible, ind)
    ens = {"n": nb_t, "k": None, "part": sc_t, "score": sc_t}
    return out, ens


def _filtrer(lignes, choix, ens=None):
    """Ne garder que les extrêmes, si on les a demandés.

    L'ORDRE D'ORIGINE EST CONSERVÉ. Trier les barres par valeur donnerait un
    classement ; ce n'en est pas un — les sections ont un ordre géographique
    et les tranches d'âge un ordre naturel, qu'un tri par part détruirait.

    L'ÉCART SE MESURE CONTRE L'ENSEMBLE DES RÉPONDANTS, et c'est le seul
    terme qui ait un sens ici : « la plus forte différence » sans dire avec
    quoi ne veut rien dire, et le repère déjà tracé en pointillés sur le
    graphique est justement celui-là. Une case à 62 % quand l'ensemble est à
    31 % s'écarte plus qu'une case à 90 % quand l'ensemble est à 88 %, même
    si la seconde est plus haute.
    """
    mesurees = [x for x in lignes if x["part"] is not None]
    if choix == "tous" or len(mesurees) <= 3:
        return lignes
    # LE RANG EST POSÉ SUR LA LIGNE, ET C'EST LUI QUE LA COULEUR LIRA. Trois
    # barres hautes et trois barres basses dans le même vert se ressemblent
    # trop : le lecteur doit recompter les valeurs pour savoir lesquelles
    # sont les meilleures. Le vert profond pour le haut, l'ambre pour le bas,
    # et la valeur reste écrite au bout de la barre — la couleur ne remplace
    # rien, elle prévient.
    if choix == "ecart":
        ref = (ens or {}).get("part")
        if ref is None:
            return lignes
        tri = sorted(mesurees, key=lambda x: -abs(x["part"] - ref))
        garder = {id(x) for x in tri[:3]}
        for x in tri[:3]:
            x["rang"] = "haut" if x["part"] >= ref else "bas"
        return [x for x in lignes if id(x) in garder]
    tri = sorted(mesurees, key=lambda x: x["part"])
    garder = set()
    if choix in ("top", "topflop"):
        garder |= {id(x) for x in tri[-3:]}
        for x in tri[-3:]:
            x["rang"] = "haut"
    if choix in ("flop", "topflop"):
        garder |= {id(x) for x in tri[:3]}
        for x in tri[:3]:
            x["rang"] = "bas"
    return [x for x in lignes if id(x) in garder]


def _barres(lignes, ens, mesure, mg=None):
    """L'histogramme, dessiné.

    LA MARGE DE GAUCHE EST RÉGLABLE, ET IL LE FAUT. Deux cent dix pixels
    suffisent à « Anse à Drick » ou « Femmes · Montagne » ; ils coupent
    « Exposure to Public Sector Corruption » par la gauche, hors du cadre du
    dessin. Les écrans qui alignent des noms d'indicateurs demandent donc
    une marge plus large, et eux seuls.

    LA LIGNE DE L'ENSEMBLE EST TRACÉE EN POINTILLÉS. Sans repère, une part de
    38 % ne dit rien ; comparée aux 31 % de l'ensemble des répondants, elle
    dit quelque chose. C'est la seule référence dont la barre a besoin.

    LES BARRES CHANGENT D'ÉCHELLE AVEC LA MESURE, jamais de forme : une part
    court de 0 à 100, un score de 0 à 10. Garder l'échelle des parts pour un
    score écraserait toutes les barres sur le premier dixième.
    """
    if not lignes:
        return ""
    vmax = 100.0 if mesure == "part" else 10.0
    dec = 0 if mesure == "part" else 2
    unite = "&#8201;%" if mesure == "part" else ""
    LARG, H_L, GAP, H_AXE = 1000, 30, 9, 26
    # LA MARGE SE MESURE SUR LE PLUS LONG DES NOMS. À douze pixels et demi,
    # un caractère occupe un peu plus de six pixels de large ; la marge suit,
    # entre deux cent dix — la largeur qui convenait aux noms de groupes — et
    # quatre cent trente, au-delà de quoi c'est la barre qui n'aurait plus de
    # place. Un plafond, pas une troncature : le nom reste entier.
    if mg is None:
        _long = max((len(l.get("nom") or "") for l in lignes), default=0)
        mg = min(430, max(210, int(6.4 * _long) + 14))
    MG_G, MG_H, MG_B = mg, 26, 30
    n_axes = len({l.get("axe") for l in lignes if l.get("axe")})
    H = (MG_H + len(lignes) * (H_L + GAP)
         + max(n_axes - 1, 0) * H_AXE + MG_B)
    # DEUX NOMBRES QUI SE TOUCHENT SE LISENT COMME UN SEUL. « 89 % » et
    # « 363/1208 » se suivaient à trois pixels : le pourcentage et son
    # effectif formaient une bouillie de chiffres. La réserve de droite passe
    # de quatre-vingt-seize à cent soixante pixels, la part se pose au bout de
    # la barre et l'effectif tient le bord droit ; entre les deux, du blanc.
    RESERVE, X_N = 160, LARG - 2
    utile = LARG - MG_G - RESERVE
    parts, axe_vu, y = [], None, MG_H

    if ens["part"] is not None:
        x = MG_G + utile * ens["part"] / vmax
        parts.append(
            f'<line x1="{x:.1f}" y1="{MG_H - 12}" x2="{x:.1f}" '
            f'y2="{H - MG_B + 6}" stroke="{ENCRE3}" stroke-width="1" '
            f'stroke-dasharray="3 4"/>'
            f'<text x="{x:.1f}" y="{MG_H - 17}" text-anchor="middle" '
            f'font-size="11" fill="{ENCRE3}">'
            f'{_e(T("ex_ens"))} {_f(ens["part"], dec)}{unite}</text>')

    for l in lignes:
        pale = mesure == "part" and l["n"] < N_FRAGILE
        coul = "#a8cbb6" if pale else VERT_APRI
        if l.get("rang") == "bas":
            coul = "#e6b98a" if pale else "#c2761a"
        elif l.get("rang") == "haut" and not pale:
            coul = "#1a6b52"
        # LE NOM DE L'AXE EST ÉCRIT AU-DESSUS DE SES RANGS, SUR SA PROPRE
        # LIGNE. Cumulées, dix sections et deux sexes se suivent sans rien qui
        # dise où l'on passe de l'un à l'autre ; posé dans la marge de la
        # première barre, l'intitulé venait buter contre son libellé.
        if l.get("axe") and l["axe"] != axe_vu:
            if axe_vu is not None:
                y += H_AXE
            axe_vu = l["axe"]
            parts.append(
                f'<text x="0" y="{y - 8}" font-size="9.5" font-weight="700" '
                f'letter-spacing="1.2" fill="{GRIS}">'
                f'{_e(l["axe"].upper())}</text>')
        parts.append(
            f'<text x="{MG_G - 12}" y="{y + 15}" text-anchor="end" '
            f'font-size="12.5" fill="{ENCRE}">{_e(l["nom"])}</text>'
            f'<rect x="{MG_G}" y="{y + 3}" width="{utile}" height="16" rx="8" '
            f'fill="#eef3f0"/>')
        if l["part"] is not None:
            w = max(utile * min(l["part"], vmax) / vmax, 2)
            parts.append(
                f'<rect x="{MG_G}" y="{y + 3}" width="{w:.1f}" height="16" '
                f'rx="8" fill="{coul}"/>'
                f'<text x="{MG_G + utile + 14}" y="{y + 15}" font-size="12.5" '
                f'font-weight="700" fill="{ENCRE}">'
                f'{_f(l["part"], dec)}{unite}</text>')
        if mesure == "part":
            parts.append(
                f'<text x="{X_N}" y="{y + 15}" font-size="11" '
                f'fill="{GRIS}" text-anchor="end">{l["k"]}/{l["n"]}</text>')
        y += H_L + GAP

    return (f'<svg viewBox="0 0 {LARG} {H}" width="100%" '
            f'style="max-width:{LARG}px;display:block" role="img" '
            f'font-family="Inter,system-ui,sans-serif">'
            + "".join(parts) + '</svg>')


def _tableau(lignes, ens, mesure):
    dec = 1 if mesure == "part" else 2
    unite = "&#8201;%" if mesure == "part" else " / 10"
    col = T("ex_part") if mesure == "part" else T("ex_score")
    r = ['<table class="ex-tab"><thead><tr>'
         f'<th>{_e(T("ex_axe"))}</th>'
         f'<th class="n">{_e(col)}</th>']
    if mesure == "part":
        r.append(f'<th class="n">{_e(T("ex_col_n"))}</th>')
    else:
        r.append(f'<th class="n">n</th>')
    r.append('</tr></thead><tbody>')
    for l in lignes:
        n = (f'{l["k"]} / {l["n"]}' if mesure == "part" else str(l["n"]))
        # LE TABLEAU PORTE LE MÊME CODE QUE LES BARRES : une pastille verte
        # devant les plus hauts, ambre devant les plus bas. Deux dessins du
        # même écran ne peuvent pas dire la même chose de deux façons.
        pt = ""
        if l.get("rang") in ("haut", "bas"):
            c = "#1a6b52" if l["rang"] == "haut" else "#c2761a"
            pt = (f'<span style="display:inline-block;width:7px;height:7px;'
                  f'border-radius:50%;background:{c};margin-right:8px;'
                  f'vertical-align:middle"></span>')
        r.append(f'<tr><td>{pt}{_e(l["nom"])}</td>'
                 f'<td class="n v">{_f(l["part"], dec)}{unite}</td>'
                 f'<td class="n">{n}</td></tr>')
    n = (f'{ens["k"]} / {ens["n"]}' if mesure == "part" else str(ens["n"]))
    r.append(f'<tr><td>{_e(T("ex_ens"))}</td>'
             f'<td class="n v">{_f(ens["part"], dec)}{unite}</td>'
             f'<td class="n">{n}</td></tr>')
    r.append('</tbody></table>')
    return "".join(r)


def _csv(lignes, mesure):
    """Ce qui est à l'écran, en une table à quatre colonnes.

    LE FICHIER SUIT L'ÉCRAN, IL NE LE DÉBORDE PAS. Télécharger « tout » a
    déjà sa page — les sept classeurs de la rubrique Données. Ici, on emporte
    exactement ce qu'on a sous les yeux : la ventilation choisie, sur la
    population choisie, avec les effectifs qui la portent.
    """
    import csv as _c
    import io as _io
    tampon = _io.StringIO()
    plume = _c.writer(tampon, delimiter=";")
    plume.writerow([T("ex_c_nom"), T("ex_part") if mesure == "part"
                    else T("ex_score"), T("ex_col_n"), T("ex_c_k")])
    for l in lignes:
        plume.writerow([l["nom"],
                        "" if l["part"] is None else f'{l["part"]:.2f}',
                        l["n"], "" if l.get("k") is None else l["k"]])
    return tampon.getvalue().encode("utf-8-sig")


def _nom_theme(cat):
    """Le nom du module, sans son code de lettre."""
    return libelles_enquete.module(cat or "").split(". ", 1)[-1]


def _libelle_question(q, avec_theme=True):
    return libelles_enquete.libelle(q, avec_module=avec_theme)


def render(cat, mode=None):
    """L'explorateur, dans l'ordre : mesure, question, ventilation, format.

    `mode` fige la mesure quand la page n'en propose qu'une : « brut » pour
    les résultats d'enquête, « score » pour les scores de résilience. Deux
    onglets qui traitent chacun d'une seule mesure ne doivent pas demander au
    lecteur de la choisir avant de commencer.

    L'ORDRE DES COMMANDES EST L'ORDRE DE LA PENSÉE. On ne choisit pas un
    format de graphique avant de savoir ce qu'on regarde : ce qu'on mesure
    vient d'abord, la ventilation ensuite, le dessin en dernier.
    """
    if not cat or not cat.get("questions"):
        return
    # LES RÉSULTATS BRUTS ONT LEUR PROPRE ÉCRAN. Ils partageaient celui-ci
    # avec les scores, et la mise en page numérotée qui convenait à l'un
    # noyait l'autre sous huit blocs de même poids. Voir `_render_brut`.
    if mode == "brut":
        return _render_brut(cat)
    st.markdown(STYLE, unsafe_allow_html=True)

    questions = cat["questions"]
    if mode == "brut":
        mesure = "part"
    elif mode == "score":
        mesure = "score"
    else:
        mesure = None

    # LE TITRE ET SON CHAPEAU NE SONT RENDUS QUE POUR LES SCORES. En mesure
    # brute, l'onglet au-dessus dit déjà « Questionnaire ménage » : répéter
    # « Explorateur de réponses » juste en dessous, avec un paragraphe qui
    # explique ce que les commandes montrent d'elles-mêmes, ne faisait
    # qu'éloigner les commandes du haut de l'écran.
    if mesure == "score":
        st.markdown(
            f'<div class="ex-titre">{_e(T("ex_t_score"))}</div>'
            f'<p class="ex-note" style="margin:0 0 12px;max-width:96ch">'
            f'{_e(T("ex_intro_score"))}</p>', unsafe_allow_html=True)

    if mesure is None:
        mesure = st.radio(
            T("ex_mesure"), ["part", "score"], horizontal=True, key="ex_mes",
            format_func=lambda m: T("ex_m_" + m))

    q, modalite, cible = None, None, None
    if mesure == "score":
        # ---- 1 · la cible : l'indice, une dimension ou un indicateur -----
        opts = _cibles(cat)
        libs = {c: lib for c, lib, _i in opts}
        cible = st.selectbox(T("ex_cible"), [c for c, _l, _i in opts],
                             key="ex_cible_sel",
                             format_func=lambda c: libs.get(c, c))
    if mesure == "part":
        # ---- 2 · la question, la réponse, la ventilation, le dessin ------
        # LE THÈME D'ABORD, LA QUESTION ENSUITE. Quatre cent quatre-vingt-
        # trois questions dans un seul menu se cherchent à l'aveugle : on
        # déroulait une liste de la hauteur de six écrans en espérant
        # reconnaître un intitulé au passage. Le questionnaire est déjà
        # découpé en modules — l'eau, l'élevage, la migration, le foncier —
        # et ce découpage-là est celui dans lequel on pense sa question. Un
        # thème choisi, il reste une dizaine de lignes ; aucun thème choisi,
        # la liste entière reste accessible pour qui sait ce qu'il cherche.
        _etape(2, "ex_e2_t", aide="ex_e2_x")
        _themes = sorted({x.get("category") or "" for x in questions},
                         key=lambda c: _nom_theme(c).lower())
        t1, t2, t3 = st.columns([1.15, 1.75, 1])
        with t1:
            theme = st.selectbox(
                T("ex_theme"), [None] + _themes, key="ex_theme",
                format_func=lambda c: (T("ex_theme_tous") if c is None
                                       else _nom_theme(c)))
        vues = [x for x in questions
                if theme is None or (x.get("category") or "") == theme]
        with t2:
            # LA CLÉ DÉPEND DU THÈME : sans cela, changer de thème garderait
            # la question du thème précédent, qui n'est plus dans la liste.
            qi = st.selectbox(
                T("ex_question"), [x["i"] for x in vues],
                key=f"ex_q_{theme or 'tous'}",
                format_func=lambda i: _libelle_question(
                    next(x for x in vues if x["i"] == i),
                    avec_theme=theme is None))
        q = next(x for x in vues if x["i"] == qi)
        with t3:
            # LA CLÉ DE LA RÉPONSE DÉPEND DE LA QUESTION : sans cela, changer
            # de question garderait l'index de l'ancienne réponse et
            # afficherait une modalité qui n'a rien à voir.
            # LA VALEUR RETENUE RESTE LE LIBELLÉ FRANÇAIS : c'est lui qui
            # indexe les masques binaires. Seul l'affichage est traduit.
            modalite = st.selectbox(T("ex_reponse"), q["modalites"],
                                    key=f"ex_m_{qi}",
                                    format_func=libelles_enquete.modalite)

    # ---- 2 · la ventilation, le format, les extrêmes ---------------------
    # UNE SEULE VENTILATION À LA FOIS, ET C'EST UN CHOIX, PAS UNE LIMITE. Le
    # menu à cocher permettait d'empiler les cinq registres : l'écran
    # affichait alors les dix sections, les deux sexes, les quatre tranches
    # d'âge, les trois catégories et les deux paysages — vingt-et-une barres
    # d'un coup, dont dix-neuf que personne n'avait demandées. On regarde un
    # registre, on en change d'un geste, et les autres servent à restreindre.
    dispo = [a for a, _ in AXES]
    c1, c2, c3 = st.columns([1.5, 1.1, 1.5], vertical_alignment="bottom")
    with c1:
        # LES REGISTRES SE CUMULENT, ET ILS SE CROISENT. Un seul registre
        # donne dix sections ou quatre tranches d'âge ; deux ou trois donnent
        # « les femmes du littoral », « les soixante ans et plus de la
        # montagne » — des groupes qu'aucun registre pris seul ne nomme, et
        # qui sont précisément ceux qu'on veut comparer entre eux. Trois au
        # maximum : au-delà, les effectifs tombent sous ce qu'on peut lire.
        st.session_state.setdefault(f"ex_axes_{mesure}", [dispo[0]])
        axes = st.multiselect(
            T("ex_axe"), dispo, key=f"ex_axes_{mesure}", max_selections=3,
            format_func=lambda a: T(dict(AXES)[a]))
        if not axes:
            axes = [dispo[0]]
    with c2:
        extremes = st.selectbox(
            T("ex_extremes"), ["tous", "top", "flop", "topflop", "ecart"],
            key="ex_ext",
            format_func=lambda c: T({"tous": "ex_tous", "top": "ex_top",
                                     "flop": "ex_flop",
                                     "topflop": "ex_topflop",
                                     "ecart": "ex_ecart"}[c]))
    with c3:
        # LE FORMAT SE CHOISIT D'UN CLIC, PAS D'UN MENU : quatre boutons
        # accolés, celui qui est actif en vert. C'est le réglage qu'on change
        # le plus souvent de tout l'écran.
        formes = ["barres", "tableau", "carte", "radar"]
        with st.container(key="ex_forme_zone"):
            forme = st.radio(T("ex_voir"), formes, key="ex_forme",
                             horizontal=True,
                             format_func=lambda f: T("ex_" + f))

    # ---- 4 · les cinq registres, cumulables ------------------------------
    filtre, poses = _panneau_filtres(cat, "ex_pan", _REGISTRES_F,
                                     3, "ex_filtres_t", note="ex_filtres_opt")
    if mesure == "part":
        filtre, cond = _condition_question(cat, questions, filtre)
    else:
        cond = None
    n_f = int(filtre.sum())
    if n_f == 0:
        st.info(T("ex_filtre_vide"))
        return
    if poses:
        st.markdown(
            f'<p class="ex-note" style="margin:2px 0 0">'
            f'{_e(T("ex_filtre_n", n=_n(n_f), t=_n(cat["n"])))}</p>',
            unsafe_allow_html=True)

    lignes, ens = _ventiler(cat, mesure, q, modalite, axes, filtre, cible)
    lignes = [l for l in lignes if l["n"] > 0]
    if not lignes:
        st.info(T("ex_vide"))
        return
    montrees = _filtrer(lignes, extremes, ens)

    # ---- 4 · le dessin, et ce sur quoi il porte --------------------------
    _etape(4, "ex_res")
    # L'EFFECTIF RETENU EST ANNONCÉ AVANT LE DESSIN, PAS APRÈS. Une part de
    # soixante pour cent ne veut pas dire la même chose sur mille deux cents
    # ménages et sur soixante ; le lecteur doit savoir sur quoi il regarde
    # avant de regarder. Le téléchargement est à côté : ce qui est à l'écran
    # est ce qui part dans le fichier.
    _g, _d = st.columns([3, 1], vertical_alignment="center")
    with _g:
        _p = 100.0 * n_f / cat["n"] if cat["n"] else 0
        _txt = _e(T("ex_e4_x", k=_n(n_f), n=_n(cat["n"]), p=_f(_p, 1)))
        if len(axes) > 1:
            # LE COMPTE DES GROUPES CROISÉS EST DIT, ET LE NOMBRE DE CASES
            # POSSIBLES AVEC : la différence entre les deux, ce sont les
            # combinaisons que personne n'habite — « les moins de 25 ans,
            # catégorie A, à Blactote » n'existe pas, et c'est en soi un
            # renseignement.
            _poss = 1
            for _a in axes:
                _poss *= max(1, len(_cases(cat, _a)))
            _txt += ('<br>' + _e(T("ex_croise_x", k=_n(len(lignes)),
                                   n=_n(_poss))))
        st.markdown(f'<p class="ex-res-x">{_txt}</p>', unsafe_allow_html=True)
    with _d:
        st.download_button(
            T("ex_dl"), data=_csv(montrees, mesure),
            file_name="resultats_apri.csv", mime="text/csv",
            key=f"ex_dl_{mesure}", use_container_width=True)
    # LE TABLEAU EST UN MODE, PAS UNE ANNEXE. Il était accroché sous chaque
    # dessin : on lisait la même colonne de chiffres deux fois, une fois au
    # bout des barres et une fois dessous, et l'écran doublait de hauteur pour
    # rien. Qui veut les chiffres choisit « Tableau ».
    if forme == "radar" and len(montrees) < 3:
        st.info(T("ex_radar_court"))
        forme = "barres"

    if forme == "carte":
        svg = _carte(montrees)
        if svg is None:
            st.info(T("ex_carte_sec"))
            forme = "barres"
        else:
            st.markdown(
                f'<div style="font-family:Inter,system-ui,sans-serif">{svg}'
                f'</div>', unsafe_allow_html=True)

    if forme == "radar":
        # LE RADAR EST GRADUÉ DE 0 À 10, comme tous les radars du site : le
        # même dessin ne peut pas porter deux échelles selon la page. Une
        # part y est donc divisée par dix, et la règle de lecture est écrite
        # sous le dessin plutôt que laissée à deviner.
        vals = [((l["part"] / 10 if mesure == "part" else l["part"])
                 if l["part"] is not None else None) for l in montrees]
        nom = (_e(libelles_enquete.modalite(modalite)) if mesure == "part"
               else {c: l for c, l, _i in _cibles(cat)}.get(
                   cible or "global", T("ex_m_score")))
        svg = radar.render_radar_svg(
            [l["nom"] for l in montrees], [(nom, vals, VERT_APRI)],
            taille=430)
        st.markdown(f'<div style="max-width:760px;margin:6px auto 0">{svg}'
                    f'</div>', unsafe_allow_html=True)
        if mesure == "part":
            st.markdown(
                '<p class="ex-note">'
                + _e(T("ex_radar_ech", p=_f(ens["part"], 0),
                       v=_f((ens["part"] or 0) / 10, 1))) + '</p>',
                unsafe_allow_html=True)
    elif forme == "tableau":
        st.markdown(_tableau(montrees, ens, mesure), unsafe_allow_html=True)
    else:
        st.markdown(_barres(montrees, ens, mesure), unsafe_allow_html=True)

    if mesure == "part" and any(l["n"] < N_FRAGILE for l in montrees):
        st.markdown(
            f'<p class="ex-note">{_e(T("ex_fragile", n=N_FRAGILE))}</p>',
            unsafe_allow_html=True)


# ==================================================== l'explorateur de scores
# CET ÉCRAN EST PILOTÉ PAR LA DEMANDE, PAS PAR L'INVENTAIRE. La version d'avant
# affichait, dès l'ouverture, les dix sections communales sur l'indice global :
# personne ne l'avait demandé, et il fallait défiler pour arriver à la question
# qu'on se posait. Ici rien ne se dessine avant qu'on ait dit quoi mesurer, sur
# qui, et comment le lire — et il ne se dessine qu'UNE chose.

_REGISTRES_S = [("section", "ex_ax_section"), ("sexe", "ex_ax_sexe"),
                ("age", "ex_ax_age"), ("richesse", "ex_ax_richesse"),
                ("paysage", "ex_ax_paysage")]


def _lignes_ventil_choisis(cat, dims, cible, ind, filtre):
    """Le score de la cible sur les groupes découpés par les critères retenus.

    C'EST EXACTEMENT LA GRAMMAIRE DES RÉSULTATS BRUTS. Les catégories gardées
    de chaque critère sont filtrées AVANT le regroupement, puis croisées dans
    l'ordre où les critères ont été posés. Sans critère, il reste un seul
    groupe — tout l'échantillon retenu — et c'est ce qui donne le score
    d'ensemble sans avoir à ruser avec les filtres.
    """
    if not dims:
        nb, sc = _score_cible(cat, filtre, cible, ind)
        return ([] if nb <= 0 else
                [{"nom": T("ex_tout_ech"), "cle": "tout",
                  "axe": T("ex_tout_ech"), "axe_code": "tout",
                  "n": nb, "k": None, "part": sc, "score": sc}])
    axe_lib = (T(dict(_REGISTRES_S)[dims[0][0]]) if len(dims) == 1
               else T("ex_croise"))
    axe_code = dims[0][0] if len(dims) == 1 else "croisement"
    out = []
    for lib, cle, g in _croisements_choisis(cat, dims):
        nb, sc = _score_cible(cat, g & filtre, cible, ind)
        out.append({"nom": lib, "cle": cle, "axe": axe_lib,
                    "axe_code": axe_code, "n": nb, "k": None,
                    "part": sc, "score": sc})
    return [l for l in out if l["n"] > 0]


def _lignes_ventil(cat, axes, cible, ind, filtre):
    """Le score de la cible sur les cases des registres retenus, croisées.

    UN REGISTRE DONNE DES CASES, DEUX EN DONNENT LE PRODUIT. « Section » donne
    dix lignes ; « section × sexe » en donne vingt, dont « les femmes de
    Dumont » — le groupe qu'on veut comparer aux autres et qu'aucun registre
    pris seul ne nomme.
    """
    axes = [a for a in axes if a]
    if not axes:
        return []
    if len(axes) == 1:
        return _lignes_axe(cat, axes[0], cible, ind, filtre)
    axes = [a for a in axes if a != "dimension"]
    out = []
    for lib, cle, g in _croisements(cat, axes):
        nb, sc = _score_cible(cat, g & filtre, cible, ind)
        out.append({"nom": lib, "cle": cle, "axe": T("ex_croise"),
                    "axe_code": "croisement", "n": nb, "k": None,
                    "part": sc, "score": sc})
    return [l for l in out if l["n"] > 0]


def _lignes_axe(cat, axe, cible, ind, filtre):
    """Le score de la cible sur chaque case d'un registre, ou par dimension."""
    out = []
    if axe == "dimension":
        for c in _DIMS:
            nb, sc = _score_cible(cat, filtre, f"d:{c}", None)
            out.append({"nom": T(c), "cle": c, "axe": T("ex_s_ax_dim"),
                        "axe_code": "dimension", "n": nb, "k": None,
                        "part": sc, "score": sc})
        return out
    for v, lib in _cases(cat, axe):
        g = cat["groupes"].get(v)
        if g is None:
            continue
        nb, sc = _score_cible(cat, g & filtre, cible, ind)
        out.append({"nom": lib, "cle": v, "axe": T(dict(_REGISTRES_S)[axe]),
                    "axe_code": axe, "n": nb, "k": None,
                    "part": sc, "score": sc})
    return [l for l in out if l["n"] > 0]


def _lignes_indicateurs(cat, inds, filtre):
    """Le score de chaque indicateur du périmètre, sur la sélection."""
    out = []
    for x in inds:
        nb, sc = _mesure_ind(x, filtre)
        if nb and sc is not None:
            out.append({"nom": _nom_ind(x), "cle": x["dim"],
                        "axe": T(x["dim"]), "axe_code": "indicateur",
                        "n": nb, "k": None, "part": sc, "score": sc})
    return out


def _paires_ecarts(cat, cible, ind, filtre, axe=None):
    """Toutes les paires de groupes d'un même registre, classées par écart.

    ON COMPARE À L'INTÉRIEUR D'UN REGISTRE, JAMAIS ENTRE DEUX REGISTRES. « Les
    femmes contre la montagne » n'est pas un écart, c'est une confusion : les
    deux ensembles se recouvrent et la différence mélange le sexe et le lieu.
    Femmes contre hommes, une tranche d'âge contre une autre, une localité
    contre une autre : là, les deux termes s'excluent et l'écart a un sens.

    LES SCORES SONT CALCULÉS UNE FOIS PAR GROUPE, PAS UNE FOIS PAR PAIRE. Les
    dix sections font quarante-cinq paires ; les calculer paire par paire
    ferait quatre-vingt-dix agrégations pour dix chiffres.
    """
    registres = [(a, l) for a, l in _REGISTRES_S if axe in (None, a)]
    lignes = []
    for a, lab in registres:
        scores = {}
        for v, lib in _cases(cat, a):
            g = cat["groupes"].get(v)
            if g is None:
                continue
            nb, sc = _score_cible(cat, g & filtre, cible, ind)
            if nb and sc is not None:
                scores[v] = (lib, sc, nb)
        vals = list(scores)
        for i in range(len(vals)):
            for j in range(i + 1, len(vals)):
                (la, sa, na), (lb, sb, nb) = scores[vals[i]], scores[vals[j]]
                # LE PREMIER NOMMÉ EST LE PLUS BAS. « Femmes 3,2 contre
                # hommes 6,1 → −2,9 » se lit dans le bon sens ; l'inverse
                # affiche un écart positif là où il y a un désavantage.
                if sb < sa:
                    la, sa, na, lb, sb, nb = lb, sb, nb, la, sa, na
                lignes.append({"registre": T(lab), "a": la, "b": lb,
                               "sa": sa, "sb": sb, "d": sa - sb,
                               "na": na, "nb": nb})
    lignes.sort(key=lambda x: x["d"])
    return lignes


def _table_paires(lignes):
    r = ['<table class="ex-tab"><thead><tr>'
         f'<th>{_e(T("ex_s_ec_col"))}</th>'
         f'<th>{_e(T("ex_s_ec_reg"))}</th>'
         f'<th class="n">{_e(T("ex_score"))}</th>'
         f'<th class="n">{_e(T("ex_col_n"))}</th>'
         f'<th class="n">{_e(T("ex_s_ecart"))}</th>'
         '</tr></thead><tbody>']
    for x in lignes:
        pale = ' class="pale"' if min(x["na"], x["nb"]) < N_FRAGILE else ""
        r.append(
            f'<tr{pale}><td><b>{_e(x["a"])}</b> '
            f'<span style="color:#8a93a5">{_e(T("ex_s_ec_vs"))}</span> '
            f'{_e(x["b"])}</td>'
            f'<td style="color:#8a93a5">{_e(x["registre"])}</td>'
            f'<td class="n"><b>{_f(x["sa"], 2)}</b> '
            f'<span style="color:#a7b0be">/ {_f(x["sb"], 2)}</span></td>'
            f'<td class="n" style="color:#8a93a5">{x["na"]} / {x["nb"]}</td>'
            f'<td class="n v" style="color:{ROUGE}">'
            f'{_f(x["d"], 2)}</td></tr>')
    r.append('</tbody></table>')
    return "".join(r)


def render_scores(cat):
    """Les scores de résilience : ce qu'on mesure, puis le résultat.

    MÊME GRAMMAIRE QUE LES RÉSULTATS BRUTS, ET C'EST TOUT L'INTÉRÊT. Les deux
    écrans posent la même question — qu'est-ce que je regarde, sur qui, et
    comment je le lis — et les posaient jusqu'ici dans deux mises en page
    différentes, l'une numérotée en quatre étapes, l'autre pas. Un lecteur
    qui passe d'un onglet à l'autre ne doit pas réapprendre l'outil : les
    décisions essentielles sont sur une rangée, ce qui est facultatif est
    replié, et les réglages d'affichage vivent dans l'en-tête du résultat.
    """
    if not cat or not cat.get("indicateurs"):
        return
    # DEUX APPELS, PAS UNE CONCATÉNATION. La règle qui masque les blocs de
    # style repose sur `style:only-child` : deux balises `<style>` dans le
    # même bloc ne matchent plus, le bloc reste dans le flux et laisse
    # soixante-dix pixels de blanc en tête d'écran.
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown(_CSS_BRUT, unsafe_allow_html=True)

    with st.container(key="ex_brut_s"):
        _h1, h2 = st.columns([4, 1], vertical_alignment="center")
        with h2:
            if st.button(T("ex_b_raz"), key="exs_raz", type="tertiary"):
                raz_scores()
                st.rerun()

        # ---- ce qu'on mesure, et ce qu'on compare -----------------------
        with st.container(key="exb_q_zone_s"):
            c1, c2, c3 = st.columns([1, 2, 1.3])
            with c1:
                dim = st.selectbox(
                    T("ex_s_dim"), [None] + _DIMS, key="exs_dim",
                    format_func=lambda c: (T("ex_s_toutes") if c is None
                                           else T(c)))
            inds = [x for x in _inds_tries(cat)
                    if dim is None or x["dim"] == dim]
            with c2:
                k = st.selectbox(
                    T("ex_s_ind"), [None] + list(range(len(inds))),
                    key=f"exs_ind_{dim}",
                    format_func=lambda i: (
                        T("ex_s_tous_i" if dim else "ex_s_tous_i0")
                        if i is None
                        else (_nom_ind(inds[i]) if dim
                              else f'{T(inds[i]["dim"])} · '
                                   f'{_nom_ind(inds[i])}')))
        # LA MÊME ZONE DE PROJECTION QUE LES RÉSULTATS BRUTS. L'écran des
        # scores avait gardé la cascade « puis par », plus une case à cocher
        # « Dimension » à côté d'elle : deux grammaires pour un même geste,
        # à deux onglets d'écart, et aucune des deux ne permettait de ne
        # garder que deux sections. Les critères de ventilation, chacun avec
        # ses catégories, font ici ce qu'ils font là-bas.
        dims = _zone_projection(cat, prefixe="exs")
        if k is not None:
            ind = inds[k]
            cible = f"i:{_inds_tries(cat).index(ind)}"
            lib_cible = _nom_ind(ind)
        elif dim is not None:
            ind, cible, lib_cible = None, f"d:{dim}", T(dim)
        else:
            ind, cible, lib_cible = None, "global", T("ex_c_global")

        # ---- les deux volets facultatifs --------------------------------
        filtre, poses = _filtres_population(cat, "exs_f_", _REGISTRES_S)
        # COMPARER PLUSIEURS INDICATEURS EST UNE QUESTION DE PLUS, pas une
        # façon de lire celle du dessus : mettre l'eau, l'assainissement et
        # l'électricité côte à côte remplace le score unique par une série.
        # Replié, ce champ ne coûte rien à qui ne s'en sert pas.
        _cmp_cle = f"exs_cmp_{dim}"
        _cmp_pose = bool(st.session_state.get(_cmp_cle))
        with st.expander(T("ex_s_comp"), expanded=_cmp_pose):
            compare = st.multiselect(
                T("ex_s_comp"), list(range(len(inds))), key=_cmp_cle,
                max_selections=8, label_visibility="collapsed",
                format_func=lambda i: _nom_ind(inds[i]))
        compares = [inds[i] for i in compare]

        n_f = int(filtre.sum())
        if n_f == 0:
            st.info(T("ex_s_vide"))
            return

        # ---- le résultat, et ses seuls réglages d'affichage -------------
        r1, r2, r3 = st.columns([1.1, 1.1, 2.2], vertical_alignment="center")
        with r1:
            st.markdown(f'<div class="exb-sec" style="margin:10px 0 0">'
                        f'{_e(T("ex_res"))}</div>', unsafe_allow_html=True)
        with r2:
            mode = st.selectbox(
                T("ex_s_mode"), ["actuel", "bas", "haut", "ecarts"],
                key="exs_mode", label_visibility="collapsed",
                format_func=lambda m: T("ex_s_m_" + m))
        # LA CARTE ET LE RADAR NE S'OFFRENT QUE S'ILS PEUVENT SE DESSINER,
        # comme sur les résultats bruts. La carte se trace par section
        # communale et par elle seule ; le radar demande au moins trois
        # sommets. Proposés hors de ces cas, ils renvoyaient un message
        # d'excuse à la place du graphique demandé.
        formes = ["barres"]
        if len(dims) == 1 and dims[0][0] == "section":
            formes.append("carte")
        formes += ["radar", "tableau"]
        with r3:
            with st.container(key="exb_vue_s"):
                forme = st.segmented_control(
                    T("ex_format"), formes,
                    key="exs_forme", default="barres",
                    label_visibility="collapsed",
                    format_func=lambda f: T("ex_" + f)) or "barres"
        if "carte" not in formes:
            st.markdown(f'<p class="ex-note" style="margin:2px 0 6px">'
                        f'{_e(T("ex_pourquoi_carte"))}</p>',
                        unsafe_allow_html=True)

        # ---- les écarts entre groupes ont leur propre tableau ------------
        if mode == "ecarts":
            st.markdown(f'<p class="ex-note" style="margin:2px 0 6px">'
                        f'{_e(T("ex_s_ec_x"))}</p>', unsafe_allow_html=True)
            combien = st.selectbox(T("ex_s_combien"), [5, 10, 20],
                                   key="exs_k_ec")
            paires = _paires_ecarts(cat, cible, ind, filtre, None)
            if not paires:
                st.info(T("ex_s_ec_rien"))
                return
            st.markdown(_table_paires(paires[:combien]),
                        unsafe_allow_html=True)
            return

        nb_sel, sc_sel = _score_cible(cat, filtre, cible, ind)
        _nb_e, sc_ech = _score_cible(cat, np.ones(cat["n"], dtype=bool),
                                     cible, ind)
        # LES TROIS CARTES DE TÊTE SONT PARTIES. « Sélection 3,32 / 10 »,
        # « Échantillon entier 3,32 / 10 » et « Écart 0,00 » disaient trois
        # fois le même chiffre tant qu'aucun filtre n'était posé, et
        # occupaient toute la largeur au-dessus du graphique qu'on vient
        # voir. Le score de la sélection est déjà au bout de sa barre, et la
        # référence de l'ensemble est le trait pointillé du graphique.

        if compares:
            titre = T("ex_s_comp_t")
            lignes = _lignes_indicateurs(cat, compares, filtre)
        elif dims:
            titre = (T("ex_s_bas_a") if mode == "bas"
                     else T("ex_s_haut_a") if mode == "haut" else lib_cible)
            lignes = _lignes_ventil_choisis(cat, dims, cible, ind, filtre)
        elif mode in ("bas", "haut"):
            titre = T("ex_s_bas_i" if mode == "bas" else "ex_s_haut_i")
            lignes = _lignes_indicateurs(cat, inds, filtre)
        else:
            if sc_sel is None:
                st.info(T("ex_s_rien"))
            if poses:
                st.markdown(f'<p class="ex-note" style="margin:8px 0 0">'
                            f'{_e(T("ex_s_n", n=_n(n_f), t=_n(cat["n"])))}</p>',
                            unsafe_allow_html=True)
            return
        if not lignes:
            st.info(T("ex_s_rien"))
            return

        if mode in ("bas", "haut"):
            combien = st.selectbox(T("ex_s_combien"), [5, 10, 20],
                                   key="exs_k")
            lignes = sorted(lignes, key=lambda x: x["score"],
                            reverse=(mode == "haut"))[:combien]

        st.markdown(f'<div class="ex-titre" style="margin-top:8px">'
                    f'{_e(titre)}</div>', unsafe_allow_html=True)
        ens = {"n": nb_sel, "k": None, "part": sc_sel, "score": sc_sel}

        if forme == "radar" and len(lignes) < 3:
            st.info(T("ex_radar_court"))
            forme = "barres"
        if forme == "carte":
            svg = (_carte(lignes)
                   if len(dims) == 1 and dims[0][0] == "section" else None)
            if svg is None:
                st.info(T("ex_s_carte_sec"))
                forme = "barres"
            else:
                st.markdown(
                    f'<div style="font-family:Inter,system-ui,sans-serif">'
                    f'{svg}</div>', unsafe_allow_html=True)
        if forme == "radar":
            svg = radar.render_radar_svg(
                [l["nom"] for l in lignes],
                [(lib_cible, [l["score"] for l in lignes], VERT_APRI)],
                taille=430)
            st.markdown(f'<div style="max-width:760px;margin:6px auto 0">'
                        f'{svg}</div>', unsafe_allow_html=True)
        elif forme == "tableau":
            st.markdown(_tableau(lignes, ens, "score"),
                        unsafe_allow_html=True)
        elif forme == "barres":
            st.markdown(_barres(lignes, ens, "score"), unsafe_allow_html=True)

        st.markdown(_synthese(lignes, "score"), unsafe_allow_html=True)
        if poses:
            st.markdown(f'<p class="ex-note" style="margin:6px 0 0">'
                        f'{_e(T("ex_s_n", n=_n(n_f), t=_n(cat["n"])))}</p>',
                        unsafe_allow_html=True)


def raz_scores():
    """Vide les filtres, la comparaison et l'affichage de l'écran des scores.

    LA CIBLE MESURÉE SURVIT, comme la question survit sur les résultats
    bruts : on enlève ses restrictions, on n'efface pas ce qu'on regardait.
    """
    for k in [k for k in list(st.session_state)
              if str(k).startswith(("exs_f_", "exs_cmp_", "exs_axe",
                                    "exs_dim", "exs_dims", "exs_cat_",
                                    "exs_forme", "exs_mode", "exs_k"))]:
        st.session_state.pop(k, None)


# ============================================================ résultats bruts
# POURQUOI CET ÉCRAN A ÉTÉ REFAIT À PART.
# `render()` servait deux mesures — les parts d'enquête et les scores — avec
# un seul jeu de commandes numérotées. Sur les parts, cela donnait quatre
# grands numéros verts, une rangée de quatre cartes de source, un panneau de
# filtres encadré, une zone de seconde question toujours dépliée et un
# sélecteur de dessin au milieu du formulaire : huit blocs de même poids
# visuel avant le premier graphique. Un lecteur ne savait pas où regarder, et
# la page se lisait comme un formulaire administratif à remplir dans l'ordre.
#
# CE N'EST PAS UN ASSISTANT, C'EST UN TABLEAU DE BORD. Trois décisions sont
# toujours visibles — la question, la réponse, ce qu'on compare — et rien
# n'impose de les prendre dans l'ordre : chacune se change à tout moment et
# le graphique se redessine. Ce qui est avancé est replié : les cinq filtres
# de population et la seconde condition. Ce qui est un réglage d'affichage
# vit dans l'en-tête du résultat, pas dans le formulaire.
#
# AUCUNE CAPACITÉ N'A ÉTÉ RETIRÉE. Les cinq registres cumulables, le
# croisement jusqu'à trois axes, la seconde question comme condition, les
# extrêmes, les quatre dessins, le téléchargement : tout est là, rangé
# autrement.

_CSS_BRUT = """
<style>
  /* UN INTITULÉ DE SECTION, PAS UNE ÉTAPE NUMÉROTÉE. Deux mots en petites
     capitales et un filet : assez pour découper l'écran en deux moments,
     trop peu pour ressembler à un parcours imposé. */
  div[class*="st-key-ex_brut"] .exb-sec {
      display:flex; align-items:center; gap:12px; margin:2px 0 2px;
      font-size:11.5px; font-weight:700; letter-spacing:.09em;
      text-transform:uppercase; color:#1f5b46; }
  div[class*="st-key-ex_brut"] .exb-sec span.l {
      flex:1 1 auto; height:1px; background:#e4eae6; }
  div[class*="st-key-ex_brut"] .exb-x {
      font-size:12.5px; color:#8a93a5; margin:0 0 10px;
      text-align:left !important; }
  /* LA QUESTION EST LE CONTRÔLE PRINCIPAL, et son libellé le dit : il est le
     seul de la page en encre pleine et en gras. Les autres commandes portent
     le gris des étiquettes secondaires. */
  div[class*="st-key-exb_q_zone"] label p {
      font-size:12.5px !important; font-weight:700 !important;
      color:#101728 !important; }
  /* LES DEUX VOLETS REPLIABLES SONT DISCRETS : pas de cadre, pas de fond, un
     simple filet haut. Ils annoncent une possibilité, ils ne réclament pas
     l'attention. */
  div[class*="st-key-ex_brut"] div[data-testid="stExpander"] details {
      border:0 !important; border-top:1px solid #eef2f7 !important;
      border-radius:0 !important; background:transparent !important;
      box-shadow:none !important; }
  div[class*="st-key-ex_brut"] div[data-testid="stExpander"] summary {
      padding:9px 2px !important; }
  div[class*="st-key-ex_brut"] div[data-testid="stExpander"] summary p {
      font-size:12.5px !important; font-weight:600 !important;
      color:#3c6b57 !important; }
  div[class*="st-key-ex_brut"] div[data-testid="stExpander"] summary:hover p {
      color:#1f5b46 !important; }
  /* LE SÉLECTEUR DE DESSIN, DANS L'EN-TÊTE DU RÉSULTAT : compact, aligné à
     droite, l'actif en vert plein. */
  div[class*="st-key-exb_vue"] div[data-baseweb="button-group"] {
      justify-content:flex-end !important; }
  div[class*="st-key-exb_vue"] button {
      font-size:12px !important; padding:3px 12px !important; }
  /* LES QUATRE CHIFFRES DE SYNTHÈSE : une ligne de texte, pas quatre cartes.
     Ils commentent le graphique, ils ne lui font pas concurrence. */
  div[class*="st-key-ex_brut"] .exb-st {
      display:flex; flex-wrap:wrap; gap:6px 26px; margin:12px 0 0;
      font-size:12px; color:#8a93a5; }
  div[class*="st-key-ex_brut"] .exb-st b {
      color:#101728; font-weight:700; font-variant-numeric:tabular-nums; }
  /* LA REMISE À ZÉRO EST UN LIEN, PAS UNE CARTE. Le style général du site
     encadre les boutons ; posé en tête de la zone d'analyse, ce cadre-là
     pesait plus que le titre à côté duquel il se trouve. */
  div[class*="st-key-ex_brut"] button[data-testid="stBaseButton-tertiary"] {
      border:0 !important; background:transparent !important;
      box-shadow:none !important; padding:2px 0 !important;
      min-height:0 !important; float:right; }
  div[class*="st-key-ex_brut"] button[data-testid="stBaseButton-tertiary"] p {
      font-size:12px !important; font-weight:600 !important;
      color:#8a93a5 !important; }
  div[class*="st-key-ex_brut"]
      button[data-testid="stBaseButton-tertiary"]:hover p {
      color:#1f5b46 !important; text-decoration:underline; }
</style>
"""


def raz_brut():
    """Remet l'écran des résultats bruts dans son état d'ouverture.

    ELLE EST APPELÉE AVANT QUE LES WIDGETS N'EXISTENT, et c'est la seule
    façon de faire : Streamlit refuse qu'on écrive la clé d'un widget déjà
    dessiné dans la même passe. Le bouton pose donc un drapeau et relance la
    page ; `app.py` consomme le drapeau en tête de la rubrique, avant le
    sélecteur de source et avant cet écran.

    LA QUESTION CHOISIE SURVIT. Réinitialiser veut dire « enlève mes filtres
    et remets l'affichage à plat », pas « oublie ce que je regardais ».
    """
    for k in [k for k in list(st.session_state)
              if str(k).startswith(("exb_f_", "exb_c_", "exb_axe", "exb_vue",
                                    "exb_ext", "exb_cat_", "exb_dim",
                                    "exb_q2", "exb_dims"))]:
        st.session_state.pop(k, None)


def _projection(cle, dispo, libelle, facultatif=False):
    """Un niveau, puis le suivant s'il est demandé : jamais de case orpheline.

    LE MENU SUIVANT N'EXISTE QUE SI LE PRÉCÉDENT EST POSÉ. Trois cases
    alignées dont la troisième n'avait pas d'intitulé et affichait « choisir
    une option » ne disaient pas ce qu'elles attendaient : on voyait trois
    réglages de même rang là où il y a un emboîtement. Le deuxième niveau
    n'apparaît qu'une fois le premier choisi, le troisième qu'une fois le
    deuxième choisi, et chacun porte son intitulé.

    UN NIVEAU NE PROPOSE JAMAIS CE QUI EST DÉJÀ PRIS au-dessus de lui : le
    même registre deux fois ne croiserait rien.
    """
    cols = st.columns(3)
    with cols[0]:
        a1 = st.selectbox(
            libelle, dispo, key=f"{cle}_1",
            index=None if facultatif else 0,
            placeholder=T("ex_axe_non"),
            format_func=lambda a: T(dict(AXES)[a]))
    a2 = a3 = None
    if a1 is not None:
        with cols[1]:
            a2 = st.selectbox(
                T("ex_axe2"), [a for a in dispo if a != a1], key=f"{cle}_2",
                index=None, placeholder=T("ex_axe_non"),
                format_func=lambda a: T(dict(AXES)[a]))
        if a2 is not None:
            with cols[2]:
                a3 = st.selectbox(
                    T("ex_axe2"), [a for a in dispo if a not in (a1, a2)],
                    key=f"{cle}_3", index=None, placeholder=T("ex_axe_non"),
                    format_func=lambda a: T(dict(AXES)[a]))
    return [a for a in (a1, a2, a3) if a is not None]


def _zone_projection(cat, prefixe="exb"):
    """Les dimensions de projection, et pour chacune ses catégories.

    DEUX GESTES DISTINCTS, ET C'EST TOUT L'OBJET DE CE BLOC. Choisir une
    dimension dit COMMENT le résultat est découpé — une valeur par section,
    puis une valeur par section et par sexe, et ainsi de suite. Choisir ses
    catégories dit CE QU'ON GARDE avant le découpage. Les deux étaient
    confondus : trois menus « puis par » empilaient des dimensions sans
    jamais permettre de dire « seulement Barbois et Dumont », et les cinq
    filtres de population, à côté, restreignaient sans découper. Une
    dimension porte maintenant ses catégories, et une catégorie retenue
    filtre avant le regroupement.

    TOUTES LES CATÉGORIES SONT RETENUES À L'AJOUT. Ajouter « Section
    communale » doit afficher les dix sections sans avoir à les cocher une à
    une ; ne garder qu'une section est le geste supplémentaire, pas le geste
    par défaut.

    UNE DIMENSION NE SE CHOISIT QU'UNE FOIS : elle disparaît de la liste des
    suivantes, faute de quoi « section × section » produirait des cases
    vides.
    """
    dispo = [a for a, _l in AXES]
    cle_dims = prefixe + "_dims"
    st.session_state.setdefault(cle_dims, [dispo[0]])
    dims = [a for a in st.session_state[cle_dims] if a in dispo]

    st.markdown(f'<div class="exb-sec" style="margin:6px 0 2px">'
                f'{_e(T("ex_axe"))}<span class="l"></span></div>',
                unsafe_allow_html=True)
    choisies = []
    for i, axe in enumerate(list(dims)):
        c1, c2, c3 = st.columns([1.3, 2.2, 0.5],
                                vertical_alignment="bottom")
        libres = [a for a in dispo if a == axe or a not in dims]
        with c1:
            nouveau = st.selectbox(
                T("ex_dim_n", n=i + 1), libres, index=libres.index(axe),
                key=f"{prefixe}_dim_{i}",
                format_func=lambda a: T(dict(AXES)[a]))
        if nouveau != axe:
            # LE CHANGEMENT DE DIMENSION EMPORTE SES CATÉGORIES : celles de
            # l'ancienne n'ont aucun sens sous la nouvelle.
            st.session_state[cle_dims][i] = nouveau
            st.session_state.pop(f"{prefixe}_cat_{axe}", None)
            st.rerun()
        vals = [v for v, _lib in _cases(cat, axe)]
        st.session_state.setdefault(f"{prefixe}_cat_{axe}", list(vals))
        with c2:
            gardees = st.multiselect(
                T("ex_dim_cat"), vals, key=f"{prefixe}_cat_{axe}",
                placeholder=T("ex_dim_toutes"), format_func=_lib)
        with c3:
            # LE DERNIER CRITÈRE S'ENLÈVE AUSSI, et c'est ce qui donne le
            # résultat sur tout l'échantillon : sans critère, il n'y a pas de
            # découpage, donc un seul groupe — tous les ménages retenus.
            if st.button("✕", key=f"{prefixe}_dim_x_{i}", type="tertiary",
                         help=T("ex_dim_oter")):
                st.session_state[cle_dims] = [
                    a for a in st.session_state[cle_dims] if a != axe]
                st.session_state.pop(f"{prefixe}_cat_{axe}", None)
                st.rerun()
        choisies.append((axe, gardees or vals))

    if not dims:
        st.markdown(f'<p class="exb-x" style="margin:0 0 4px">'
                    f'<b style="color:#101728">{_e(T("ex_tout_ech"))}</b> · '
                    f'{_e(T("ex_tout_x"))}</p>', unsafe_allow_html=True)
    if len(dims) < len(dispo):
        if st.button("＋ " + T("ex_dim_plus"), key=f"{prefixe}_dim_plus",
                     type="tertiary"):
            manque = [a for a in dispo if a not in dims]
            st.session_state[cle_dims] = list(dims) + [manque[0]]
            st.rerun()
    return choisies


def _croisement_questions(cat, questions, filtre):
    """Autant de secondes questions qu'on veut, croisées entre elles.

    CE N'EST PAS UNE DIMENSION DE PROJECTION, C'EST UNE POPULATION. « Ceux
    qui ont l'eau potable ET des sanitaires améliorés » se dit avec deux
    questions du questionnaire, pas avec un registre de profil : aucune
    combinaison de section, de sexe ou d'âge ne nomme ce groupe-là. Les
    conditions se cumulent en ET entre elles, et en OU entre les réponses
    d'une même question.
    """
    st.session_state.setdefault("exb_q2", [])
    posees = [i for i in st.session_state["exb_q2"]
              if any(x["i"] == i for x in questions)]
    n = sum(1 for i in posees
            if st.session_state.get(f"exb_q2_r_{i}"))
    lib = T("ex_croiser_q") + (" · " + T("ex_croiser_n", n=n) if n else "")
    with st.expander(lib, expanded=bool(posees)):
        for rang, qi in enumerate(list(posees)):
            q2 = next(x for x in questions if x["i"] == qi)
            c1, c2, c3 = st.columns([2.2, 1.6, 0.5],
                                    vertical_alignment="bottom")
            with c1:
                autres = [x["i"] for x in questions
                          if x["i"] == qi or x["i"] not in posees]
                nq = st.selectbox(
                    T("ex_cond_q"), autres, index=autres.index(qi),
                    key=f"exb_q2_s_{rang}",
                    format_func=lambda i: _libelle_question(
                        next(x for x in questions if x["i"] == i)))
            if nq != qi:
                st.session_state["exb_q2"][rang] = nq
                st.session_state.pop(f"exb_q2_r_{qi}", None)
                st.rerun()
            with c2:
                reps = st.multiselect(
                    T("ex_cond_r"), q2["modalites"], key=f"exb_q2_r_{qi}",
                    format_func=libelles_enquete.modalite)
            with c3:
                if st.button("✕", key=f"exb_q2_x_{rang}", type="tertiary",
                             help=T("ex_dim_oter")):
                    st.session_state["exb_q2"] = [
                        i for i in st.session_state["exb_q2"] if i != qi]
                    st.session_state.pop(f"exb_q2_r_{qi}", None)
                    st.rerun()
            if reps:
                m = np.zeros(cat["n"], dtype=bool)
                for r in reps:
                    m |= cat["bits"][q2["debut"] + q2["modalites"].index(r)]
                filtre = filtre & m
        libres = [x["i"] for x in questions if x["i"] not in posees]
        if libres and st.button("＋ " + T("ex_croiser_plus"),
                                key="exb_q2_plus", type="tertiary"):
            st.session_state["exb_q2"] = list(posees) + [libres[0]]
            st.rerun()
    return filtre


def _filtres_population(cat, prefixe="exb_f_", registres=None,
                        question=None):
    """Les cinq registres, repliés, cumulables, et vidables d'un geste.

    OU DANS UN REGISTRE, ET DANS L'AUTRE ENTRE REGISTRES. Deux sections
    cochées donnent les ménages de l'une OU de l'autre ; une section et un
    sexe donnent ceux qui sont dans la section ET de ce sexe. C'est la seule
    lecture qui rende « les femmes pauvres du littoral » exprimable.
    """
    registres = registres or _REGISTRES_F
    cles = {a: f"{prefixe}{a}" for a, _l in registres}
    n_actifs = sum(len(st.session_state.get(k) or []) for k in cles.values())
    # LA RÉPONSE EST UN FILTRE, PAS UNE ÉTAPE OBLIGÉE. Sans elle, l'écran
    # montre la répartition complète de la question ; avec elle, il compare
    # cette réponse-là entre groupes. C'est bien une restriction de plus,
    # elle a donc sa place avec les cinq autres.
    modalite = st.session_state.get(f"exb_m_{question['i']}") \
        if question is not None else None
    n_actifs += 1 if modalite else 0
    lib = T("ex_b_filtres") if question is not None else T("ex_b_pop")
    if n_actifs:
        lib += " · " + T("ex_b_pop_n", n=n_actifs)
    choix = {}
    with st.expander(lib, expanded=bool(n_actifs)):
        # PAS DE LIGNE QUI ÉNUMÈRE CE QUI SUIT. « Une réponse, section
        # communale, sexe, âge, catégorie économique, paysage » listait, en
        # gris, les intitulés des six champs posés juste dessous.
        # LE BOUTON DE VIDAGE VIENT AVANT LES CHAMPS : posé après, il
        # écrirait dans l'état de widgets déjà construits, ce que Streamlit
        # refuse. Avant, il les vide pendant qu'ils n'existent pas encore.
        if n_actifs and st.button(T("ex_raz"), key=f"{prefixe}raz",
                                  type="tertiary"):
            for k in cles.values():
                st.session_state[k] = []
        if question is not None:
            # LA RÉPONSE EST UN FILTRE COMME LES AUTRES, et elle en a la
            # forme : un champ de la même largeur que les cinq registres,
            # vide par défaut, avec « toutes les réponses » écrit en gris
            # dedans plutôt qu'une valeur qui aurait l'air d'être un choix.
            cr = st.columns(len(registres))
            with cr[0]:
                modalite = st.selectbox(
                    T("ex_reponse"), list(question["modalites"]),
                    key=f"exb_m_{question['i']}", index=None,
                    placeholder=T("ex_b_toutes"),
                    format_func=libelles_enquete.modalite)
        cols = st.columns(len(registres))
        for (axe, lab), col in zip(registres, cols):
            with col:
                choix[axe] = st.multiselect(
                    T(lab), list(_VALEURS.get(axe, [])), key=cles[axe],
                    placeholder=T("ex_f_tous"), format_func=_lib)
    poses = [(a, v) for a, vs in choix.items() for v in (vs or [])]
    if question is not None:
        return _masque_multi(cat, choix), poses, modalite
    return _masque_multi(cat, choix), poses


def _synthese(lignes, mesure):
    """Moyenne, extrêmes et écart, en une ligne de texte sous le graphique."""
    vals = [(l["nom"], l["part"]) for l in lignes if l["part"] is not None]
    if len(vals) < 2:
        return ""
    dec = 1 if mesure == "part" else 2
    u = "&#8201;%" if mesure == "part" else ""
    moy = sum(v for _n, v in vals) / len(vals)
    haut = max(vals, key=lambda x: x[1])
    bas = min(vals, key=lambda x: x[1])
    return (
        f'<div class="exb-st">'
        f'<span>{_e(T("ex_b_moy"))} <b>{_f(moy, dec)}{u}</b></span>'
        f'<span>{_e(T("ex_b_haut"))} <b>{_f(haut[1], dec)}{u}</b> '
        f'{_e(haut[0])}</span>'
        f'<span>{_e(T("ex_b_bas"))} <b>{_f(bas[1], dec)}{u}</b> '
        f'{_e(bas[0])}</span>'
        f'<span>{_e(T("ex_b_ecart"))} '
        f'<b>{_f(haut[1] - bas[1], dec)}{u}</b></span></div>')


def _render_brut(cat):
    """Question → filtres facultatifs → résultat, sur un seul écran."""
    questions = cat["questions"]
    mesure = "part"
    # DEUX APPELS, PAS UNE CONCATÉNATION. La règle qui masque les blocs de
    # style repose sur `style:only-child` : deux balises `<style>` dans le
    # même bloc ne matchent plus, le bloc reste dans le flux et laisse
    # soixante-dix pixels de blanc en tête d'écran.
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown(_CSS_BRUT, unsafe_allow_html=True)

    with st.container(key="ex_brut"):
        # PAS DE TITRE DE SECTION AU-DESSUS DES COMMANDES. « Que voulez-vous
        # analyser ? » posait une question dont la réponse était juste en
        # dessous, en toutes lettres, dans le menu des questions : une ligne
        # de plus avant le premier réglage, qui n'apprenait rien. La remise à
        # zéro n'a donc plus de rangée à elle : elle se range au bout de la
        # première, à hauteur du menu des questions.

        # LE THÈME RESTE, MAIS IL PASSE AU SECOND PLAN. Quatre cent
        # quatre-vingt-trois questions dans un menu unique se cherchent à
        # l'aveugle ; le module du questionnaire est le tri dans lequel on
        # pense sa question. Il est donc gardé, étroit, à côté de la question
        # — qui, elle, occupe le double de largeur et porte le seul libellé
        # en encre pleine de l'écran.
        with st.container(key="exb_q_zone"):
            c1, c2, c4, c0 = st.columns([1, 2.2, 1.1, 0.55],
                                        vertical_alignment="bottom")
            with c0:
                if st.button(T("ex_b_raz"), key="exb_raz", type="tertiary"):
                    st.session_state["ra_raz"] = True
                    st.rerun()
            with c1:
                themes = sorted({x.get("category") or "" for x in questions},
                                key=lambda c: _nom_theme(c).lower())
                theme = st.selectbox(
                    T("ex_theme"), [None] + themes, key="exb_theme",
                    format_func=lambda c: (T("ex_theme_tous") if c is None
                                           else _nom_theme(c)))
            vues = [x for x in questions
                    if theme is None or (x.get("category") or "") == theme]
            with c2:
                qi = st.selectbox(
                    T("ex_question"), [x["i"] for x in vues],
                    key=f"exb_q_{theme or 'tous'}",
                    format_func=lambda i: _libelle_question(
                        next(x for x in vues if x["i"] == i),
                        avec_theme=theme is None))
        q = next(x for x in vues if x["i"] == qi)
        with c4:
            # LA RÉPONSE APPARTIENT À LA QUESTION, PAS À LA POPULATION. Elle
            # était rangée avec les filtres de profil ; elle revient à côté
            # de la question dont elle est une modalité, vide par défaut —
            # sans réponse choisie, l'écran montre la répartition complète.
            modalite = st.selectbox(
                T("ex_reponse"), list(q["modalites"]), key=f"exb_m_{qi}",
                index=None, placeholder=T("ex_b_toutes"),
                format_func=libelles_enquete.modalite)

        # ---- comment le résultat est découpé, et sur quoi ---------------
        dims = _zone_projection(cat)
        axes = [a for a, _v in dims]
        filtre = _croisement_questions(cat, questions,
                                       np.ones(cat["n"], dtype=bool))
        n_f = int(filtre.sum())
        if n_f == 0:
            st.info(T("ex_filtre_vide"))
            return

        lignes, ens = _ventiler_dims(cat, q, modalite, dims, filtre)
        lignes = [l for l in lignes if l["n"] > 0]
        if not lignes:
            st.info(T("ex_vide"))
            return

        # ---- le résultat, et ses seuls réglages d'affichage -------------
        # UN DESSIN QUI NE PEUT PAS SE FAIRE N'EST PAS PROPOSÉ. La carte
        # colorie des sections communales : elle n'a de sens que si le
        # découpage EST la section et si une réponse est désignée, sans quoi
        # il n'y a pas un chiffre par section à porter dessus. Le radar tient
        # à partir de trois branches et demande lui aussi une réponse : sur
        # une répartition, chaque groupe porte plusieurs barres et le radar
        # n'a rien à tracer. Les proposer puis refuser de les dessiner avec
        # un message d'erreur revenait à faire cliquer pour rien.
        formes = ["barres"]
        if (modalite is not None and len(dims) == 1
                and dims[0][0] == "section"):
            formes.append("carte")
        if modalite is not None and len(lignes) >= 3:
            formes.append("radar")
        formes.append("tableau")
        r1, r2, r3 = st.columns([1.1, 1.1, 2.2],
                                vertical_alignment="center")
        with r1:
            st.markdown(f'<div class="exb-sec" style="margin:10px 0 0">'
                        f'{_e(T("ex_res"))}</div>', unsafe_allow_html=True)
        with r2:
            extremes = st.selectbox(
                T("ex_extremes"), ["tous", "top", "flop", "topflop", "ecart"],
                key="exb_ext", label_visibility="collapsed",
                format_func=lambda c: T("ex_extremes") + " : " + T(
                    {"tous": "ex_tous", "top": "ex_top", "flop": "ex_flop",
                     "topflop": "ex_topflop", "ecart": "ex_ecart"}[c]))
        with r3:
            with st.container(key="exb_vue"):
                forme = st.segmented_control(
                    T("ex_voir"), formes, key="exb_vue_sel",
                    default="barres", label_visibility="collapsed",
                    format_func=lambda f: T("ex_" + f)) or "barres"
        if forme not in formes:
            forme = "barres"
        # POURQUOI UNE VUE MANQUE, PLUTÔT QUE SON ABSENCE SILENCIEUSE. Retirer
        # la carte quand elle ne peut pas se dessiner évite un clic pour rien,
        # mais laisse le lecteur devant un sélecteur qui a changé sans
        # prévenir. Une ligne grise dit ce qu'il faut choisir pour la
        # retrouver ; elle ne s'affiche que lorsqu'il manque quelque chose.
        _manque = [T("ex_pourquoi_" + f) for f in ("carte", "radar")
                   if f not in formes]
        if _manque:
            st.markdown(f'<p class="ex-note" style="margin:2px 0 6px">'
                        f'{_e(" · ".join(_manque))}</p>',
                        unsafe_allow_html=True)

        montrees = _filtrer(lignes, extremes, ens)
        if forme == "radar" and len(montrees) < 3:
            forme = "barres"
        if forme == "carte":
            svg = _carte(montrees)
            if svg is None:
                st.info(T("ex_carte_sec"))
                forme = "barres"
            else:
                st.markdown(
                    f'<div style="font-family:Inter,system-ui,sans-serif">'
                    f'{svg}</div>', unsafe_allow_html=True)
        if forme == "radar":
            vals = [(l["part"] / 10 if l["part"] is not None else None)
                    for l in montrees]
            svg = radar.render_radar_svg(
                [l["nom"] for l in montrees],
                [(libelles_enquete.modalite(modalite) if modalite
                  else T("ex_b_toutes"), vals, VERT_APRI)],
                taille=430)
            st.markdown(f'<div style="max-width:760px;margin:6px auto 0">'
                        f'{svg}</div>', unsafe_allow_html=True)
            st.markdown('<p class="ex-note">'
                        + _e(T("ex_radar_ech", p=_f(ens["part"], 0),
                               v=_f((ens["part"] or 0) / 10, 1))) + '</p>',
                        unsafe_allow_html=True)
        elif forme == "tableau":
            st.markdown(_tableau(montrees, ens, mesure),
                        unsafe_allow_html=True)
        else:
            st.markdown(_barres(montrees, ens, mesure),
                        unsafe_allow_html=True)

        # ---- ce sur quoi porte le dessin, sous le dessin -----------------
        # L'EFFECTIF PASSE SOUS LE GRAPHIQUE. Au-dessus, il retardait le seul
        # objet qu'on vient voir ; en dessous, il répond à la question qui se
        # pose une fois la barre lue — « sur combien de ménages ? ».
        st.markdown(_synthese(montrees, mesure), unsafe_allow_html=True)
        # NI RAPPEL DE L'EFFECTIF NI MODE D'EMPLOI SOUS LE GRAPHIQUE. « 1 211
        # ménages sur 1 211 » se lit déjà au bout de chaque barre, où
        # l'effectif de la case est écrit ; et une phrase qui explique ce que
        # les commandes viennent de faire est un mode d'emploi, pas un
        # résultat. Ne restent que les deux avertissements qui changent la
        # lecture : le croisement, et les effectifs trop minces.
        _txt = ""
        if modalite is not None and len(axes) > 1:
            _poss = 1
            for _a in axes:
                _poss *= max(1, len(_cases(cat, _a)))
            _txt = _e(T("ex_croise_x", k=_n(len(lignes)), n=_n(_poss)))
        if any(l["n"] < N_FRAGILE for l in montrees):
            _txt += ("<br>" if _txt else "") + _e(T("ex_fragile",
                                                    n=N_FRAGILE))
        g, d = st.columns([3, 1], vertical_alignment="center")
        with g:
            if _txt:
                st.markdown(f'<p class="ex-note" style="margin:6px 0 0">'
                            f'{_txt}</p>', unsafe_allow_html=True)
        with d:
            st.download_button(
                T("ex_dl"), data=_csv(montrees, mesure),
                file_name="resultats_apri.csv", mime="text/csv",
                key="exb_dl", use_container_width=True)


# ====================================================== comparer et profiler
# POURQUOI CES DEUX ÉCRANS REMPLACENT « PAR PAYSAGE » ET « PAR GROUPE SOCIAL ».
# Les deux onglets retirés faisaient la même chose sur deux découpages figés :
# l'un comparait les paysages, l'autre les groupes sociaux, et aucun des deux
# ne savait comparer les femmes du littoral aux hommes de la montagne. Le
# découpage n'a pas à être écrit dans le nom d'un onglet : c'est une question
# que le lecteur pose, et les critères de ventilation la posent déjà mieux —
# un critère, deux, trois, chacun avec les catégories qu'on garde.
#
# COMPARER ET PROFILER SONT DEUX GESTES, PAS UN. Comparer met des groupes côte
# à côte sur UNE mesure : qui décroche, de combien. Profiler prend UN groupe
# et déroule ses mesures : ce qui va bien chez lui, ce qui va mal. La première
# question se lit en barres ou en radar, la seconde en deux listes — les
# meilleurs scores et les plus faibles. Les mêler dans un écran donnait la
# fiche interminable qu'on a retirée.

def _cible_scores(cat, prefixe):
    """Le choix de ce qu'on mesure : l'indice, une dimension, un indicateur."""
    c1, c2 = st.columns([1, 2])
    with c1:
        dim = st.selectbox(
            T("ex_s_dim"), [None] + _DIMS, key=f"{prefixe}_dim",
            format_func=lambda c: (T("ex_s_toutes") if c is None else T(c)))
    inds = [x for x in _inds_tries(cat) if dim is None or x["dim"] == dim]
    with c2:
        k = st.selectbox(
            T("ex_s_ind"), [None] + list(range(len(inds))),
            key=f"{prefixe}_ind_{dim}",
            format_func=lambda i: (
                T("ex_s_tous_i" if dim else "ex_s_tous_i0") if i is None
                else (_nom_ind(inds[i]) if dim
                      else f'{T(inds[i]["dim"])} · {_nom_ind(inds[i])}')))
    if k is not None:
        ind = inds[k]
        return ind, f"i:{_inds_tries(cat).index(ind)}", _nom_ind(ind)
    if dim is not None:
        return None, f"d:{dim}", T(dim)
    return None, "global", T("ex_c_global")


def render_comparaison(cat):
    """Comparer des groupes : sur quoi, lesquels, et sous quelle forme.

    TROIS DÉCISIONS, DANS L'ORDRE OÙ ELLES SE POSENT. Sur quoi on compare —
    une réponse du questionnaire ou un score de résilience ; quels groupes on
    met côte à côte — les critères de ventilation, cumulables ; et sous
    quelle forme on les lit — des barres, qui classent, ou un radar, qui
    donne la silhouette d'un groupe d'un coup d'œil.
    """
    if not cat:
        return
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown(_CSS_BRUT, unsafe_allow_html=True)

    # LA CLÉ COMMENCE PAR « ex_brut_ », ET C'EST LOAD-BEARING : la feuille de
    # style de l'écran vise `st-key-ex_brut`, et un conteneur nommé autrement
    # n'hériterait ni des intitulés de section, ni du bouton de remise à zéro
    # sans cadre, ni de la ligne de synthèse.
    with st.container(key="ex_brut_c"):
        _h1, h2 = st.columns([4, 1], vertical_alignment="center")
        with h2:
            if st.button(T("ex_b_raz"), key="exc_raz", type="tertiary"):
                raz_comparaison()
                st.rerun()

        with st.container(key="exb_q_zone_c"):
            st.markdown(f'<div class="exb-sec" style="margin:0 0 2px">'
                        f'{_e(T("ex_c_sur"))}<span class="l"></span></div>',
                        unsafe_allow_html=True)
            source = st.segmented_control(
                T("ex_c_sur"), ["scores", "brut"], key="exc_source",
                default="scores", label_visibility="collapsed",
                format_func=lambda c: T("ex_c_" + c)) or "scores"

            q = modalite = None
            if source == "brut":
                questions = cat["questions"]
                c1, c2, c3 = st.columns([1, 2.2, 1.1])
                with c1:
                    themes = sorted({x.get("category") or ""
                                     for x in questions},
                                    key=lambda c: _nom_theme(c).lower())
                    theme = st.selectbox(
                        T("ex_theme"), [None] + themes, key="exc_theme",
                        format_func=lambda c: (T("ex_theme_tous")
                                               if c is None
                                               else _nom_theme(c)))
                vues = [x for x in questions
                        if theme is None or (x.get("category") or "") == theme]
                with c2:
                    qi = st.selectbox(
                        T("ex_question"), [x["i"] for x in vues],
                        key=f"exc_q_{theme or 'tous'}",
                        format_func=lambda i: _libelle_question(
                            next(x for x in vues if x["i"] == i),
                            avec_theme=theme is None))
                q = next(x for x in vues if x["i"] == qi)
                with c3:
                    # UNE COMPARAISON PORTE SUR UNE RÉPONSE, et c'est ce qui
                    # la distingue des résultats bruts : comparer dix
                    # sections sur la répartition entière d'une question
                    # donne trente barres qui ne se comparent pas. La réponse
                    # est donc obligatoire ici, et la première est proposée.
                    modalite = st.selectbox(
                        T("ex_reponse"), list(q["modalites"]),
                        key=f"exc_m_{qi}",
                        format_func=libelles_enquete.modalite)
                ind = cible = None
                lib_cible = libelles_enquete.modalite(modalite)
            else:
                ind, cible, lib_cible = _cible_scores(cat, "exc")

        dims = _zone_projection(cat, prefixe="exc")
        filtre, poses = _filtres_population(cat, "exc_f_", _REGISTRES_S)
        n_f = int(filtre.sum())
        if n_f == 0:
            st.info(T("ex_s_vide"))
            return

        # ---- le résultat ------------------------------------------------
        r1, r3 = st.columns([1.6, 2.4], vertical_alignment="center")
        with r1:
            st.markdown(f'<div class="exb-sec" style="margin:10px 0 0">'
                        f'{_e(T("ex_res"))}</div>', unsafe_allow_html=True)
        with r3:
            with st.container(key="exb_vue_c"):
                forme = st.segmented_control(
                    T("ex_format"), ["barres", "radar"], key="exc_forme",
                    default="barres", label_visibility="collapsed",
                    format_func=lambda f: T("ex_" + f)) or "barres"

        if not dims:
            st.info(T("ex_c_sans_critere"))
            return
        if source == "brut":
            lignes = _ventiler_dims(cat, q, modalite, dims, filtre)
            mesure = "part"
            ens = None
        else:
            lignes = _lignes_ventil_choisis(cat, dims, cible, ind, filtre)
            mesure = "score"
            nb_sel, sc_sel = _score_cible(cat, filtre, cible, ind)
            ens = {"n": nb_sel, "k": None, "part": sc_sel, "score": sc_sel}
        if not lignes:
            st.info(T("ex_s_rien"))
            return

        st.markdown(f'<div class="ex-titre" style="margin-top:8px">'
                    f'{_e(lib_cible)}</div>', unsafe_allow_html=True)
        if forme == "radar" and len(lignes) < 3:
            st.info(T("ex_radar_court"))
            forme = "barres"
        if forme == "radar":
            svg = radar.render_radar_svg(
                [l["nom"] for l in lignes],
                [(lib_cible, [l[mesure] for l in lignes], VERT_APRI)],
                taille=430)
            st.markdown(f'<div style="max-width:760px;margin:6px auto 0">'
                        f'{svg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(_barres(lignes, ens, mesure), unsafe_allow_html=True)
        st.markdown(_synthese(lignes, mesure), unsafe_allow_html=True)
        if poses:
            st.markdown(f'<p class="ex-note" style="margin:6px 0 0">'
                        f'{_e(T("ex_s_n", n=_n(n_f), t=_n(cat["n"])))}</p>',
                        unsafe_allow_html=True)


def raz_comparaison():
    for k in [k for k in list(st.session_state)
              if str(k).startswith(("exc_f_", "exc_dim", "exc_dims",
                                    "exc_cat_", "exc_forme", "exc_source"))]:
        st.session_state.pop(k, None)


def render_profil(cat):
    """Un groupe, et ce qui va bien ou mal chez lui.

    UN SEUL GROUPE, ET TOUTES SES MESURES. Comparer met des groupes côte à
    côte sur une mesure ; profiler fait l'inverse — on désigne un groupe, si
    besoin croisé (les femmes de la montagne), et l'écran déroule ses
    indicateurs du mieux noté au plus faible. C'est la question qu'on pose
    quand on sait déjà où l'on intervient et qu'on cherche sur quoi.
    """
    if not cat:
        return
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown(_CSS_BRUT, unsafe_allow_html=True)

    with st.container(key="ex_brut_p"):
        _h1, h2 = st.columns([4, 1], vertical_alignment="center")
        with h2:
            if st.button(T("ex_b_raz"), key="exp_raz", type="tertiary"):
                raz_profil()
                st.rerun()

        with st.container(key="exb_q_zone_p"):
            st.markdown(f'<div class="exb-sec" style="margin:0 0 2px">'
                        f'{_e(T("ex_p_qui"))}<span class="l"></span></div>',
                        unsafe_allow_html=True)
            # LE GROUPE SE COMPOSE AVEC LES MÊMES REGISTRES QUE PARTOUT.
            # Un paysage, un groupe social, une tranche d'âge, ou les trois
            # à la fois : la composition est un ET, et c'est ce qui rend
            # « les femmes de la montagne » désignable.
            masque = np.ones(cat["n"], dtype=bool)
            nom = []
            cols = st.columns(len(_REGISTRES_S))
            for col, (axe, lab) in zip(cols, _REGISTRES_S):
                cases = _cases(cat, axe)
                with col:
                    v = st.selectbox(
                        T(lab), [None] + [c[0] for c in cases],
                        key=f"exp_g_{axe}", index=0,
                        format_func=lambda x: (T("ex_p_tous") if x is None
                                               else _lib(x)))
                if v is not None and cat["groupes"].get(v) is not None:
                    masque &= cat["groupes"][v]
                    nom.append(_lib(v))
        lib_groupe = " · ".join(nom) if nom else T("ex_tout_ech")

        n_f = int(masque.sum())
        if n_f == 0:
            st.info(T("ex_s_vide"))
            return

        c1, c2 = st.columns([1, 1])
        with c1:
            dim = st.selectbox(
                T("ex_s_dim"), [None] + _DIMS, key="exp_dim",
                format_func=lambda c: (T("ex_s_toutes") if c is None
                                       else T(c)))
        with c2:
            combien = st.selectbox(T("ex_s_combien"), [5, 10, 20],
                                   key="exp_k")

        inds = [x for x in _inds_tries(cat)
                if dim is None or x["dim"] == dim]
        lignes = [l for l in _lignes_indicateurs(cat, inds, masque)
                  if l["score"] is not None]
        if not lignes:
            st.info(T("ex_s_rien"))
            return
        classees = sorted(lignes, key=lambda x: x["score"], reverse=True)
        nb_g, sc_g = _score_cible(cat, masque, "global", None)
        ens = {"n": nb_g, "k": None, "part": sc_g, "score": sc_g}

        st.markdown(f'<div class="ex-titre" style="margin-top:10px">'
                    f'{_e(lib_groupe)}</div>'
                    f'<p class="ex-note" style="margin:0 0 10px">'
                    f'{_e(T("ex_p_n", n=_n(n_f), s=_f(sc_g, 2)))}</p>',
                    unsafe_allow_html=True)
        # LES DEUX LISTES SONT L'UNE SOUS L'AUTRE, EN PLEINE LARGEUR. Côte à
        # côte, chacune n'avait que la moitié de la page, et le nom d'un
        # indicateur — « Perception of security (SDG 16.1.4) » — se coupait
        # à gauche dans la marge de son libellé. Une liste de cinq lignes ne
        # coûte pas assez de hauteur pour justifier de tronquer ce qu'elle
        # nomme.
        st.markdown(f'<div class="exb-sec" style="margin:0 0 6px">'
                    f'{_e(T("ex_p_forts"))}<span class="l"></span></div>'
                    + _barres(classees[:combien], ens, "score"),
                    unsafe_allow_html=True)
        st.markdown(f'<div class="exb-sec" style="margin:22px 0 6px">'
                    f'{_e(T("ex_p_faibles"))}<span class="l"></span></div>'
                    + _barres(classees[::-1][:combien], ens, "score"),
                    unsafe_allow_html=True)


def raz_profil():
    for k in [k for k in list(st.session_state)
              if str(k).startswith(("exp_g_", "exp_dim", "exp_k"))]:
        st.session_state.pop(k, None)
