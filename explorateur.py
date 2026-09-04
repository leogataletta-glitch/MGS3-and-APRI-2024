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
    "ex_axe": {"en": "Break down by", "fr": "Ventiler par"},
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
    "ex_s_intro": {
        "en": "Nothing is shown until you ask for it. Narrow the sample with "
              "the filters, choose what to measure, then choose how to read "
              "it: one chart at a time, on exactly the combination you built.",
        "fr": "Rien ne s'affiche avant d'être demandé. Resserrez "
              "l'échantillon avec les filtres, choisissez ce qu'on mesure, "
              "puis comment le lire : un seul dessin à la fois, sur exactement "
              "la combinaison que vous avez construite."},
    "ex_s_quoi": {"en": "What is measured", "fr": "Ce qu'on mesure"},
    "ex_s_qui": {"en": "On which households", "fr": "Sur quels ménages"},
    "ex_s_comment": {"en": "How to read it", "fr": "Comment le lire"},
    "ex_s_dim": {"en": "Dimension", "fr": "Dimension"},
    "ex_s_ind": {"en": "Indicator", "fr": "Indicateur"},
    "ex_s_toutes": {"en": "All — overall index", "fr": "Toutes — indice global"},
    "ex_s_tous_i": {"en": "None — dimension score",
                    "fr": "Aucun — score de la dimension"},
    "ex_s_tous_i0": {"en": "None — overall index",
                     "fr": "Aucun — indice global"},
    "ex_s_axe": {"en": "Break down by", "fr": "Ventiler par"},
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
    "ex_theme_tous": {"en": "All themes", "fr": "Tous les thèmes"},
    "ex_dl": {"en": "Download results", "fr": "Télécharger les résultats"},
    "ex_filtres_x": {
        "en": "Several options can be picked in the same field: they add up. "
              "Two different fields narrow one after the other.",
        "fr": "Plusieurs options peuvent être retenues dans un même champ : "
              "elles s'additionnent. Deux champs différents restreignent l'un "
              "après l'autre."},
    "ex_raz": {"en": "Clear all", "fr": "Tout effacer"},
    "ex_res": {"en": "Results", "fr": "Résultats"},
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
    if choix == "ecart":
        ref = (ens or {}).get("part")
        if ref is None:
            return lignes
        tri = sorted(mesurees, key=lambda x: -abs(x["part"] - ref))
        garder = {id(x) for x in tri[:3]}
        return [x for x in lignes if id(x) in garder]
    tri = sorted(mesurees, key=lambda x: x["part"])
    garder = set()
    if choix in ("top", "topflop"):
        garder |= {id(x) for x in tri[-3:]}
    if choix in ("flop", "topflop"):
        garder |= {id(x) for x in tri[:3]}
    return [x for x in lignes if id(x) in garder]


def _barres(lignes, ens, mesure):
    """L'histogramme, dessiné.

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
    MG_G, MG_H, MG_B = 210, 26, 30
    n_axes = len({l.get("axe") for l in lignes if l.get("axe")})
    H = (MG_H + len(lignes) * (H_L + GAP)
         + max(n_axes - 1, 0) * H_AXE + MG_B)
    utile = LARG - MG_G - 96
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
                f'<text x="{MG_G + utile + 12}" y="{y + 15}" font-size="12.5" '
                f'font-weight="700" fill="{ENCRE}">'
                f'{_f(l["part"], dec)}{unite}</text>')
        if mesure == "part":
            parts.append(
                f'<text x="{LARG - 4}" y="{y + 15}" font-size="11" '
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
        r.append(f'<tr><td>{_e(l["nom"])}</td>'
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
        axe = st.selectbox(
            T("ex_axe"), dispo, key=f"ex_axe_{mesure}",
            format_func=lambda a: T(dict(AXES)[a]))
    axes = [axe]
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
        st.markdown(
            f'<p class="ex-res-x">'
            f'{_e(T("ex_e4_x", k=_n(n_f), n=_n(cat["n"]), p=_f(_p, 1)))}</p>',
            unsafe_allow_html=True)
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


def _zone_filtres(cat):
    """Les cinq restrictions des scores, dans le même panneau que les brutes.

    ELLES SE CUMULENT, ET PLUSIEURS OPTIONS TIENNENT DANS UN MÊME CHAMP.
    « Les femmes de 40 à 59 ans, catégorie C, en montagne, à Trichet OU
    Barbois » est une question légitime et elle n'a pas de page à elle : un
    panneau la pose. L'effectif restant est annoncé sous les champs, parce
    qu'un score calculé sur onze ménages doit se lire en sachant qu'ils sont
    onze.
    """
    return _panneau_filtres(cat, "exs_pan", _REGISTRES_S, 2, "ex_s_qui")


def _zone_cible(cat):
    """Dimension puis indicateur : deux menus, et le second suit le premier.

    LA DIMENSION FILTRE LA LISTE DES INDICATEURS, elle ne la double pas.
    Soixante-six indicateurs dans un seul menu déroulant se cherchent à
    l'aveugle ; choisir d'abord la dimension en laisse une dizaine, et si l'on
    n'en choisit aucun c'est le score de la dimension qui est mesuré. Les deux
    menus vides mesurent l'indice global : on part du plus général et on
    resserre, jamais l'inverse.
    """
    g, d = st.columns([1, 1.7])
    with g:
        dim = st.selectbox(
            T("ex_s_dim"), [None] + _DIMS, key="exs_dim",
            format_func=lambda c: T("ex_s_toutes") if c is None else T(c))
    inds = [x for x in _inds_tries(cat) if dim is None or x["dim"] == dim]
    with d:
        k = st.selectbox(
            T("ex_s_ind"), [None] + list(range(len(inds))), key=f"exs_ind_{dim}",
            format_func=lambda i: (
                T("ex_s_tous_i" if dim else "ex_s_tous_i0") if i is None
                else (_nom_ind(inds[i]) if dim
                      else f'{T(inds[i]["dim"])} · {_nom_ind(inds[i])}')))
    if k is not None:
        ind = inds[k]
        return f"i:{_inds_tries(cat).index(ind)}", _nom_ind(ind), ind, inds
    if dim is not None:
        return f"d:{dim}", T(dim), None, inds
    return "global", T("ex_c_global"), None, inds


def _kpi_score(lib, sc, n, tot, sc_ech):
    """Le score de la sélection, seul, quand on n'a rien demandé de plus."""
    ec = (sc - sc_ech) if (sc is not None and sc_ech is not None) else None
    coul = VERT if (ec or 0) > 0 else ROUGE if (ec or 0) < 0 else ENCRE3
    return (
        '<div class="ex-kpi">'
        f'<div class="ex-k"><div class="ex-k-l">{_e(T("ex_s_sel"))}</div>'
        f'<div class="ex-k-v">{_f(sc, 2)}<span class="ex-k-u"> / 10</span>'
        f'</div><div class="ex-k-s">{_e(lib)}</div></div>'
        f'<div class="ex-k"><div class="ex-k-l">{_e(T("ex_s_ech"))}</div>'
        f'<div class="ex-k-v">{_f(sc_ech, 2)}<span class="ex-k-u"> / 10</span>'
        f'</div><div class="ex-k-s">{_e(T("ex_s_n", n=_n(n), t=_n(tot)))}</div></div>'
        f'<div class="ex-k"><div class="ex-k-l">'
        f'{_e(T("ex_s_ecart_ech"))}</div>'
        f'<div class="ex-k-v" style="color:{coul}">{_f(ec, 2)}</div>'
        f'<div class="ex-k-s">{_e(T("ex_score"))}</div></div></div>')


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
    """Les scores de résilience : on demande, puis on voit — et une chose."""
    if not cat or not cat.get("indicateurs"):
        return
    st.markdown(STYLE, unsafe_allow_html=True)
    # PAS DE TITRE DE PAGE : l'onglet ouvert dit déjà « Scores de résilience »,
    # et le répéter dessous ajoutait une ligne pour ne rien apprendre. La
    # pastille avait de plus un effet de bord : la règle générale transforme
    # en carte tout bloc qui porte un `titre-bloc` en enfant direct, et c'est
    # la PAGE ENTIÈRE qui se retrouvait encadrée.
    st.markdown(
        f'<p class="ex-note" style="margin:0 0 12px;max-width:96ch">'
        f'{_e(T("ex_s_intro"))}</p>', unsafe_allow_html=True)

    # ---- 1 · ce qu'on mesure ---------------------------------------------
    _etape(1, "ex_s_quoi")
    cible, lib_cible, ind, inds = _zone_cible(cat)

    # ---- 2 · sur qui -----------------------------------------------------
    filtre, poses = _zone_filtres(cat)
    n_f = int(filtre.sum())
    if n_f == 0:
        st.info(T("ex_s_vide"))
        return
    if poses:
        st.markdown(f'<p class="ex-note" style="margin:2px 0 0">'
                    f'{_e(T("ex_s_n", n=_n(n_f), t=_n(cat["n"])))}</p>',
                    unsafe_allow_html=True)

    # ---- 3 · comment le lire ---------------------------------------------
    _etape(3, "ex_s_comment")
    c1, c2, c3 = st.columns([1.25, 1, 1.3])
    with c1:
        axe = st.selectbox(
            T("ex_s_axe"), [None] + [a for a, _l in _REGISTRES_S]
            + (["dimension"] if ind is None else []),
            key="exs_axe",
            format_func=lambda a: (T("ex_s_aucun") if a is None
                                   else T("ex_s_ax_dim") if a == "dimension"
                                   else T(dict(_REGISTRES_S)[a])))
    with c2:
        forme = st.selectbox(T("ex_format"),
                             ["barres", "radar", "tableau", "carte"],
                             key="exs_forme",
                             format_func=lambda f: T("ex_" + f))
    with c3:
        mode = st.selectbox(
            T("ex_s_mode"), ["actuel", "bas", "haut", "ecarts"],
            key="exs_mode", format_func=lambda m: T("ex_s_m_" + m))

    # ---- les écarts entre groupes ont leur propre tableau -----------------
    if mode == "ecarts":
        _etape(4, "ex_res")
        st.markdown(f'<div class="ex-titre" style="margin-top:16px">'
                    f'{_e(T("ex_s_ec_t"))}</div>'
                    f'<p class="ex-note" style="margin:0 0 4px">'
                    f'{_e(T("ex_s_ec_x"))}</p>', unsafe_allow_html=True)
        combien = st.selectbox(T("ex_s_combien"), [5, 10, 20],
                               key="exs_k_ec")
        paires = _paires_ecarts(cat, cible, ind, filtre,
                                axe if axe not in (None, "dimension") else None)
        if not paires:
            st.info(T("ex_s_ec_rien"))
            return
        st.markdown(_table_paires(paires[:combien]), unsafe_allow_html=True)
        return

    # ---- ce qui est mesuré, et sur quoi on le ventile ---------------------
    nb_sel, sc_sel = _score_cible(cat, filtre, cible, ind)
    _nb_e, sc_ech = _score_cible(cat, np.ones(cat["n"], dtype=bool),
                                 cible, ind)

    if axe is None and mode == "actuel":
        # RIEN N'A ÉTÉ DEMANDÉ DE PLUS QUE LE SCORE : on donne le score, et
        # pas dix barres par-dessus.
        if sc_sel is None:
            st.info(T("ex_s_rien"))
            return
        _etape(4, "ex_res")
        st.markdown(_kpi_score(lib_cible, sc_sel, nb_sel, cat["n"], sc_ech),
                    unsafe_allow_html=True)
        return

    if axe is None:
        titre = T("ex_s_bas_i" if mode == "bas" else "ex_s_haut_i")
        lignes = _lignes_indicateurs(cat, inds, filtre)
    else:
        titre = (T("ex_s_bas_a") if mode == "bas"
                 else T("ex_s_haut_a") if mode == "haut" else lib_cible)
        lignes = _lignes_axe(cat, axe, cible, ind, filtre)
    if not lignes:
        st.info(T("ex_s_rien"))
        return

    if mode in ("bas", "haut"):
        combien = st.selectbox(T("ex_s_combien"), [5, 10, 20], key="exs_k")
        lignes = sorted(lignes, key=lambda x: x["score"],
                        reverse=(mode == "haut"))[:combien]

    _etape(4, "ex_res")
    st.markdown(f'<div class="ex-titre" style="margin-top:4px">'
                f'{_e(titre)}</div>', unsafe_allow_html=True)
    ens = {"n": nb_sel, "k": None, "part": sc_sel, "score": sc_sel}

    if forme == "radar" and len(lignes) < 3:
        st.info(T("ex_radar_court"))
        forme = "barres"
    if forme == "carte":
        svg = _carte(lignes) if axe == "section" else None
        if svg is None:
            st.info(T("ex_s_carte_sec"))
            forme = "barres"
        else:
            st.markdown(f'<div style="font-family:Inter,system-ui,sans-serif">'
                        f'{svg}</div>', unsafe_allow_html=True)
    if forme == "radar":
        svg = radar.render_radar_svg(
            [l["nom"] for l in lignes],
            [(lib_cible, [l["score"] for l in lignes], VERT_APRI)], taille=430)
        st.markdown(f'<div style="max-width:760px;margin:6px auto 0">{svg}'
                    f'</div>', unsafe_allow_html=True)
    elif forme == "tableau":
        st.markdown(_tableau(lignes, ens, "score"), unsafe_allow_html=True)
    elif forme == "barres":
        st.markdown(_barres(lignes, ens, "score"), unsafe_allow_html=True)
