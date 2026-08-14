"""Bilingue anglais / français.

L'anglais est la langue par défaut. Le dictionnaire est indexé par une clé
courte ; chaque entrée porte les deux versions. Les textes qui contiennent des
valeurs (« 1211 répondants ») sont des gabarits à formater avec `.format()`,
jamais des morceaux de phrase recollés — l'ordre des mots n'est pas le même
d'une langue à l'autre.
"""

import streamlit as st

LANGUES = {"en": "English", "fr": "Français"}
DEFAUT = "en"


def get_lang():
    return st.session_state.get("lang", DEFAUT)


def set_lang(code):
    st.session_state["lang"] = code if code in LANGUES else DEFAUT


def T(cle, **kw):
    """Texte dans la langue courante. Les paramètres nommés sont formatés."""
    entree = DICO.get(cle)
    if entree is None:
        return cle
    texte = entree.get(get_lang()) or entree.get(DEFAUT) or cle
    return texte.format(**kw) if kw else texte


DICO = {
    # ------------------------------------------------------------ ossature
    "langue": {"en": "Language", "fr": "Langue"},
    "org": {"en": "United Nations Environment Programme — UNEP",
            "fr": "Programme des Nations Unies pour l'environnement — PNUE"},
    "titre_site": {"en": "Household survey 2024 — Sud and Grand'Anse",
                   "fr": "Enquête ménage 2024 — Sud et Grand'Anse"},
    "mode_questions": {"en": "Results of all questions asked to the 1200 households",
                       "fr": "Résultats de toutes les questions aux 1200 ménages"},
    "mode_resilience": {"en": "Associated resilience indicators",
                        "fr": "Indicateurs de résilience associés"},
    "mode_croisement": {"en": "Cross questions with one another",
                        "fr": "Croiser des questions entre elles"},
    "mode_questions_sous": {
        "en": "All 503 questions asked, filtered by sex, age, economic status "
              "and landscape",
        "fr": "Les 503 questions posées, filtrables par sexe, âge, niveau "
              "socio-économique et paysage"},
    "mode_resilience_sous": {
        "en": "Consolidated indicators and their IRLA / APRI score, by communal "
              "section and sub-population",
        "fr": "Les indicateurs consolidés et leur score IRLA / APRI, par section "
              "communale et sous-population"},
    "mode_croisement_sous": {
        "en": "Stack conditions: how many households face several deprivations "
              "at the same time",
        "fr": "Empiler des conditions : combien de foyers cumulent plusieurs "
              "privations en même temps"},
    "aide_modes": {
        "en": "On the left, the raw results of any of the 503 questions asked to "
              "1211 households, with the age / sex / economic status / landscape "
              "filters. On the right, the consolidated resilience indicators and "
              "their IRLA / APRI score.",
        "fr": "À gauche, les résultats bruts de n'importe laquelle des 503 "
              "questions posées aux 1211 ménages, avec les filtres âge / sexe / "
              "niveau socio-économique / paysage. À droite, les indicateurs de "
              "résilience consolidés et leur score IRLA / APRI."},
    "credit": {"en": "Produced by the United Nations Environment Programme (UNEP).",
               "fr": "Travail réalisé par le Programme des Nations Unies pour "
                     "l'environnement (PNUE)."},

    # ------------------------------------------------------------ filtres
    "filtres": {"en": "Filters", "fr": "Filtres"},
    "sexe": {"en": "Sex", "fr": "Sexe"},
    "homme": {"en": "Male", "fr": "Homme"},
    "femme": {"en": "Female", "fr": "Femme"},
    "hommes": {"en": "Men", "fr": "Hommes"},
    "femmes": {"en": "Women", "fr": "Femmes"},
    "categorie_eco": {"en": "Economic status", "fr": "Catégorie économique"},
    "cat_a": {"en": "Group A — extreme poverty", "fr": "Cat A — pauvreté extrême"},
    "cat_b": {"en": "Group B — poverty", "fr": "Cat B — pauvreté"},
    "cat_c": {"en": "Group C — not poor", "fr": "Cat C — non pauvre"},
    "groupe_age": {"en": "Age group", "fr": "Groupe d'âge"},
    "age_25": {"en": "Under 25", "fr": "Moins de 25 ans"},
    "age_25_39": {"en": "25 to 39", "fr": "25 à 39 ans"},
    "age_40_59": {"en": "40 to 59", "fr": "40 à 59 ans"},
    "age_60": {"en": "60 and over", "fr": "60 ans et plus"},
    "paysage": {"en": "Landscape", "fr": "Paysage"},
    "littoral": {"en": "Coastal", "fr": "Littoral"},
    "montagne": {"en": "Mountain", "fr": "Montagne"},
    "section_communale": {"en": "Communal section", "fr": "Section communale"},
    "tous_repondants": {"en": "All respondents", "fr": "Tous les répondants"},

    # ------------------------------------------------------------ onglet questions
    "q_consigne": {
        "en": "Pick one or more values per filter (filters combine: e.g. Women "
              "AND Group A AND Quentin section at the same time). Leave a filter "
              "empty to place no restriction on that criterion.",
        "fr": "Choisissez une ou plusieurs valeurs par filtre (les filtres se "
              "combinent : ex. Femmes ET Catégorie A ET section Quentin en même "
              "temps). Laissez un filtre vide pour ne pas restreindre sur ce "
              "critère."},
    "q_population": {
        "en": "Filtered population: <strong>{n} respondents</strong> (out of 1211) "
              "— Men {h} · Women {f}",
        "fr": "Population filtrée : <strong>{n} répondants</strong> (sur 1211 au "
              "total) — Hommes {h} · Femmes {f}"},
    "q_vide": {"en": "No respondent matches this combination of filters.",
               "fr": "Aucun répondant ne correspond à cette combinaison de filtres."},
    "q_bloc1": {"en": "1 · Choose the question", "fr": "1 · Choisir la question"},
    "q_bloc2": {"en": "2 · The answers", "fr": "2 · Les réponses"},
    "q_bloc3": {"en": "3 · Where, across the territory",
                "fr": "3 · Où, sur le territoire"},
    "q_bloc4": {"en": "4 · The detail, sub-group by sub-group",
                "fr": "4 · Le détail, sous-groupe par sous-groupe"},
    "q_categorie": {"en": "Question category", "fr": "Catégorie de questions"},
    "q_categorie_aide": {"en": "Categories follow the order of the questionnaire.",
                         "fr": "Les catégories suivent l'ordre du questionnaire."},
    "q_question": {"en": "Question", "fr": "Question"},
    "q_top3": {
        "en": "The three most frequent answers in the filtered population. On a "
              "multiple-choice question a household can be counted in several "
              "answers, so the percentages do not add up to 100 %. The full "
              "breakdown is further down.",
        "fr": "Les trois réponses les plus fréquentes sur la population filtrée. "
              "Sur une question à choix multiples, un même foyer peut être compté "
              "dans plusieurs réponses : les pourcentages ne totalisent alors pas "
              "100 %. Le détail complet est plus bas."},
    "q_soit": {"en": "that is {n} respondents out of {base}",
               "fr": "soit {n} répondants sur {base}"},
    "q_carte": {"en": "Map by communal section", "fr": "Carte par section communale"},
    "q_detail": {"en": "Breakdown by sub-group", "fr": "Détail par sous-groupe"},
    "q_telecharger_xlsx": {"en": "Download this table (Excel)",
                           "fr": "Télécharger ce tableau (Excel)"},
    "q_source": {
        "en": "Source: raw data V3, household survey Sept. 2024. Percentages are "
              "computed on the filtered group shown above, not on all 1211 "
              "respondents.",
        "fr": "Source : Données brutes V3, enquête ménage sept. 2024. Les "
              "pourcentages sont calculés sur la base du groupe filtré affiché "
              "ci-dessus, pas sur l'ensemble des 1211 répondants."},
    "q_modalite": {"en": "Answer", "fr": "Modalité"},
    "q_resultat": {"en": "Result", "fr": "Résultat"},

    # ---- cartographie d'une question
    "q_quoi_carto": {"en": "What to map", "fr": "Que cartographier"},
    "q_mode_seuil": {"en": "A threshold: “X and above”",
                     "fr": "Un seuil : « X et plus »"},
    "q_mode_liste": {"en": "One or more specific values",
                     "fr": "Une ou plusieurs valeurs précises"},
    "q_seuil": {"en": "Threshold", "fr": "Seuil"},
    "q_seuil_fmt": {"en": "{v} and above", "fr": "{v} et plus"},
    "q_cumule": {"en": "Adds up: ", "fr": "Cumule : "},
    "q_hors": {"en": "Not counted (non-numeric answers): ",
               "fr": "Non comptées (réponses non chiffrées) : "},
    "q_reponses_carto": {"en": "Answer(s) to map",
                         "fr": "Réponse(s) à cartographier"},
    "q_reponses_aide": {
        "en": "Select several to add them up (e.g. “Pit latrine without slab” + "
              "“None”).",
        "fr": "Sélectionnez-en plusieurs pour les cumuler (ex. « Latrines à fosse "
              "sans dalle » + « Aucun »)."},
    "q_choisir_reponse": {"en": "Pick at least one answer to display the map.",
                          "fr": "Choisissez au moins une réponse pour afficher la carte."},
    "q_avert_multi": {
        "en": "This question accepts several answers per household: adding up "
              "more than one double-counts households that ticked several. The "
              "total shown is a maximum, not an exact count.",
        "fr": "Cette question accepte plusieurs réponses par foyer : en cumuler "
              "plusieurs compte deux fois les foyers qui en ont coché plus d'une. "
              "Le total affiché est donc un maximum, pas un effectif exact."},
    "sens_couleurs": {"en": "How to read the colours",
                      "fr": "Sens de lecture des couleurs"},
    "pol_mauvais": {"en": "A high percentage is **unfavourable** (green → red)",
                    "fr": "Un pourcentage élevé est **défavorable** (vert → rouge)"},
    "pol_bon": {"en": "A high percentage is **favourable** (red → green)",
                "fr": "Un pourcentage élevé est **favorable** (rouge → vert)"},
    "pol_neutre": {"en": "Neither good nor bad — shades of blue",
                   "fr": "Ni bon ni mauvais — dégradé de bleu"},
    "pol_aide": {
        "en": "Suggested automatically from the wording of the question. No rule "
              "is reliable across 503 questions, so check it and correct it if "
              "needed.",
        "fr": "Proposé automatiquement d'après l'intitulé de la question. Aucune "
              "règle n'étant fiable sur les 503 questions, vérifiez-le et "
              "corrigez-le si besoin."},
    "regler_seuils": {"en": "Adjust the colour thresholds",
                      "fr": "Régler les seuils de couleur"},
    "seuils_auto": {"en": "Automatic thresholds", "fr": "Seuils automatiques"},
    "seuil_n": {"en": "Threshold {i}", "fr": "Seuil {i}"},
    "contours_officiels": {
        "en": "Official administrative boundaries of the communal sections.",
        "fr": "Contours administratifs officiels des sections communales."},
    "contours_disques": {
        "en": "Each disc is a communal section, placed at its real geographic "
              "position. These are not the official administrative boundaries.",
        "fr": "Chaque disque représente une section communale, placée à sa "
              "position géographique réelle. Ce ne sont pas les limites "
              "administratives officielles."},

    # ------------------------------------------------------------ résilience
    "r_titre": {"en": "Resilience indicators — APRI",
                "fr": "Indicateurs de résilience — APRI"},
    "r_sous_titre": {"en": "IRLA / APRI — Landscape Resilience Index",
                     "fr": "IRLA / APRI — Indice de résilience des paysages"},
    "r_intro": {
        "en": "Scores from 0 to 10, obtained by applying the theoretical "
              "framework's scales to values recomputed from the survey. A high "
              "score means a more favourable situation. {n} indicators out of 118 "
              "can be scored from a household questionnaire — see the note at the "
              "bottom of the page.",
        "fr": "Scores de 0 à 10 obtenus en appliquant les barèmes du cadre "
              "théorique aux valeurs recalculées depuis l'enquête. Un score élevé "
              "= situation plus favorable. {n} indicateurs sur 118 sont scorables "
              "depuis un questionnaire ménage — voir la note en bas de page."},
    "r_sous_pop": {"en": "Sub-population", "fr": "Sous-population"},
    "r_sous_pop_aide": {
        "en": "The score is recomputed on this sub-population within each communal "
              "section.",
        "fr": "Le score est recalculé sur cette sous-population à l'intérieur de "
              "chaque section communale."},
    "r_quoi_carto": {"en": "What to map", "fr": "Quoi cartographier"},
    "r_score_final": {"en": "Final score — all dimensions",
                      "fr": "Score final — toutes dimensions"},
    "r_dimension_prefix": {"en": "Dimension — ", "fr": "Dimension — "},
    "r_bloc1": {"en": "1 · The score at a glance", "fr": "1 · Le score en bref"},
    "r_bloc2": {"en": "2 · Where, across the territory",
                "fr": "2 · Où, sur le territoire"},
    "r_bloc3": {"en": "3 · Ranking of the sections",
                "fr": "3 · Le classement des sections"},
    "r_bloc4": {"en": "4 · The radar profile", "fr": "4 · Le profil en radar"},
    "r_bloc5": {"en": "5 · Compare sub-populations",
                "fr": "5 · Comparer les sous-populations"},
    "r_moyenne": {"en": "Average of the 10 sections",
                  "fr": "Moyenne des 10 sections"},
    "r_plus_haut": {"en": "Highest score — {s}", "fr": "Score le plus élevé — {s}"},
    "r_plus_bas": {"en": "Lowest score — {s}", "fr": "Score le plus faible — {s}"},
    "r_des_menages": {"en": "of households (raw measure)",
                      "fr": "des ménages (mesure brute)"},
    "r_note_score": {"en": "resilience score — {p} % of the APRI scale",
                     "fr": "score de résilience — {p} % de l'échelle APRI"},
    "r_ce_que_mesure": {"en": "What this indicator measures",
                        "fr": "Ce que mesure cet indicateur"},
    "r_definition": {"en": "<strong>Definition from the framework:</strong> ",
                     "fr": "<strong>Définition du cadre théorique :</strong> "},
    "r_bareme": {"en": "<strong>Scale:</strong> ", "fr": "<strong>Barème :</strong> "},
    "r_reserve": {"en": "<strong>Caveat:</strong> ", "fr": "<strong>Réserve :</strong> "},
    "r_question_enquete": {"en": "Survey question: {q}",
                           "fr": "Question de l'enquête : {q}"},
    "r_reponses_comptees": {"en": "Answers counted: {m}",
                            "fr": "Réponses comptées : {m}"},
    "r_deux_lectures": {
        "en": " and the ", "fr": " et le "},
    "r_deux_lectures_suite": {
        "en": " answer two different questions: the first says what is measured "
              "on the ground, the second says where that places the section on "
              "the international comparison scale. The scale converts one into "
              "the other — and it is not linear.",
        "fr": " répondent à deux questions différentes : la première dit ce qui "
              "est mesuré sur le terrain, le second dit où cela place la section "
              "sur l'échelle de comparaison internationale. C'est le barème qui "
              "fait le passage de l'un à l'autre — et il n'est pas linéaire."},
    "r_agregat": {
        "en": "Aggregate of several indicators: there is no single household "
              "percentage to show here. Pick a specific indicator under “What to "
              "map” to see the raw measure next to the score. The percentage "
              "shown is the position of the score on the APRI scale (5 out of 10 "
              "= 50 %).",
        "fr": "Agrégat de plusieurs indicateurs : il n'y a pas de pourcentage de "
              "ménages unique à afficher ici. Choisissez un indicateur précis dans "
              "« Quoi cartographier » pour voir la mesure brute à côté du score. "
              "Le pourcentage indiqué est la position du score sur l'échelle APRI "
              "(5 sur 10 = 50 %)."},
    "r_petits": {
        "en": "Fewer than {n} respondents in: {liste}. For those sections the "
              "order of magnitude holds, the exact figure does not.",
        "fr": "Moins de {n} répondants dans : {liste}. Sur ces sections, l'ordre "
              "de grandeur est utilisable, le chiffre exact ne l'est pas."},
    "r_colorier": {"en": "Colour the map by", "fr": "Colorier la carte selon"},
    "r_par_score": {"en": "The resilience score (0-10)",
                    "fr": "Le score de résilience (0-10)"},
    "r_par_brut": {"en": "The raw value (%)", "fr": "La valeur brute (%)"},
    "r_legende_apri": {
        "en": "APRI colour scale: one colour per score point, from red (0, "
              "weakest resilience) to dark green (10). The scale is fixed, which "
              "makes every map comparable with every other.",
        "fr": "Échelle de couleurs APRI : une couleur par point de score, du rouge "
              "(0, résilience la plus faible) au vert foncé (10). L'échelle est "
              "fixe, ce qui rend toutes les cartes comparables entre elles."},
    "r_rappel_echelle": {
        "en": "Reminder: 4.0 out of 10 = 40 % of the APRI scale. The table below "
              "gives both readings.",
        "fr": "Rappel : 4,0 sur 10 = 40 % de l'échelle APRI. Le tableau ci-dessous "
              "donne les deux lectures."},
    "r_niveau": {"en": "Level of detail", "fr": "Niveau de lecture"},
    "r_niveau1": {"en": "Level 1 — the dimensions", "fr": "Niveau 1 — les dimensions"},
    "r_niveau2": {"en": "Level 2 — the indicators of one dimension",
                  "fr": "Niveau 2 — les indicateurs d'une dimension"},
    "r_dim_detail": {"en": "Dimension to expand", "fr": "Dimension à détailler"},
    "r_trop_peu": {
        "en": "This dimension has only {n} scorable indicator(s): a radar needs at "
              "least three axes. Choose another one.",
        "fr": "Cette dimension ne compte que {n} indicateur(s) scorable(s) : un "
              "radar demande au moins trois axes. Choisissez-en une autre."},
    "r_comparer": {"en": "Compare (3 at most)", "fr": "Comparer (3 au maximum)"},
    "r_ensemble": {"en": "All 10 sections", "fr": "Ensemble des 10 sections"},
    "r_choisir_section": {"en": "Pick at least one section to display.",
                          "fr": "Choisissez au moins une section à afficher."},
    "r_radar_dim": {
        "en": "Fixed 0 to 10 scale on every axis: two radars overlay directly. A "
              "dashed outline flags a profile where at least one axis is not "
              "measured.",
        "fr": "Échelle fixe de 0 à 10 sur chaque axe : deux radars se superposent "
              "directement. Un contour en pointillés signale un profil dont un axe "
              "au moins n'est pas mesuré."},
    "r_radar_ind": {"en": "One axis per indicator of the dimension, on the same "
                          "0 to 10 scale.",
                    "fr": "Un axe par indicateur de la dimension, sur la même "
                          "échelle 0 à 10."},
    "r_axe": {"en": "Axis", "fr": "Axe"},
    "r_lecture_cellule": {
        "en": "Reading a cell: the raw measure on the ground, then the score the "
              "scale assigns to it and its position on the APRI scale.",
        "fr": "Lecture d'une cellule : la mesure brute sur le terrain, puis le "
              "score que le barème lui attribue et sa position sur l'échelle APRI."},
    "r_des_menages_court": {"en": "of households", "fr": "des ménages"},
    "r_comparaison": {
        "en": "Same selection, recomputed for each sub-population. Cells based on "
              "fewer than 30 respondents are flagged with “·”.",
        "fr": "Même sélection, recalculée pour chaque sous-population. Les cellules "
              "sur moins de 30 répondants sont signalées par « · »."},
    "r_telecharger_csv": {"en": "Download this table (CSV)",
                          "fr": "Télécharger ce tableau (CSV)"},
    "r_reserves_titre": {"en": "What these scores cover — and what they do not",
                         "fr": "Ce que ces scores couvrent — et ce qu'ils ne "
                               "couvrent pas"},
    "r_reserve_indic": {"en": "**Caveat specific to this indicator:** ",
                        "fr": "**Réserve propre à cet indicateur :** "},
    "r_reserves_texte": {
        "en": """
- **{n_score} indicators** out of the 118 in the framework receive a score here.
- **{n_non} cannot be computed** from a household questionnaire: 37 of the 38
  environmental indicators (NDVI, mangroves, habitat connectivity) require
  satellite imagery, and health-worker densities and vaccination coverage come
  from health registries.
- **9 indicators of the cultural dimension** have a value but no score: their
  scale is built on a composite 0-8 index, not on a percentage.
- As a result the final score does **not weigh the seven dimensions equally**.
  It is solid on infrastructure, governance, economy, social and human;
  silent on environment and culture.
- **Three scales are inverted in the framework** (FIES, population victim of
  violence, destructive fishing practices): they award a score of 10 to the
  worst value. They have been flipped here to stay consistent with the sixteen
  other negative indicators.
- On the **FIES** the score is 0 everywhere: severe food insecurity ranges from
  54 % to 73 % across sections, while the most degraded class of the scale stops
  at 29.2 %. The scale was calibrated on a less severe reality than this area.
""",
        "fr": """
- **{n_score} indicateurs** sur les 118 du cadre théorique reçoivent un score ici.
- **{n_non} ne sont pas calculables** depuis un questionnaire ménage : 37 des 38
  indicateurs environnementaux (NDVI, mangroves, connectivité des habitats)
  relèvent de l'imagerie satellitaire, les densités de personnel de santé et les
  couvertures vaccinales des registres sanitaires.
- **9 indicateurs de la dimension culturelle** ont une valeur mais pas de score :
  leur barème porte sur un indice composite de 0 à 8, pas sur un pourcentage.
- Conséquence : le score final ne pèse **pas les sept dimensions à parts
  égales**. Il est solide sur les infrastructures, la gouvernance, l'économie,
  le social et l'humain ; muet sur l'environnement et le culturel.
- **Trois barèmes sont inversés dans le cadre théorique** (FIES, population
  victime de violences, pratiques de pêche destructrices) : ils attribuent le
  score 10 à la pire valeur. Ils ont été retournés ici pour rester cohérents
  avec les seize autres indicateurs négatifs.
- Sur le **FIES**, le score vaut 0 partout : l'insécurité alimentaire sévère va
  de 54 % à 73 % selon les sections, alors que la classe la plus dégradée du
  barème s'arrête à 29,2 %. L'échelle a été calibrée sur une réalité moins
  sévère que celle de la zone.
"""},
    "r_source": {
        "en": "Source: household survey Sept. 2024 (1211 respondents), scales from "
              "the IRLA / APRI theoretical framework. Colour scale: “International "
              "comparative empirical scenarios”, APRI reference.",
        "fr": "Source : enquête ménage sept. 2024 (1211 répondants), barèmes du "
              "cadre théorique IRLA / APRI. Échelle de couleurs : « International "
              "comparative empirical scenarios », référentiel APRI."},
    "r_fichiers_absents": {
        "en": "Missing file(s) in the project: **{f}**.\n\nUpload them to GitHub "
              "in `data/` or at the root of the repository — both locations work. "
              "The app restarts on its own afterwards.",
        "fr": "Fichier(s) de données absent(s) du projet : **{f}**.\n\nDéposez-les "
              "sur GitHub dans `data/` ou à la racine du dépôt — les deux "
              "emplacements fonctionnent. L'application redémarre toute seule "
              "ensuite."},
    "r_autre_onglet": {
        "en": "The “Results of all questions” tab still works: switch back to it "
              "at the top of the page.",
        "fr": "Le mode « Résultats de toutes les questions » reste utilisable : "
              "rebasculez dessus en haut de page."},

    # ------------------------------------------------------------ croisement
    "c_titre": {"en": "Cross questions", "fr": "Croiser des questions"},
    "c_intro": {
        "en": "Stack conditions to count the households that meet all of them at "
              "the same time — for instance no improved sanitation, no improved "
              "water and no electricity. {n} of the 503 survey questions can be "
              "crossed.",
        "fr": "Empilez des conditions pour compter les foyers qui les remplissent "
              "toutes en même temps — par exemple sans toilettes améliorées, sans "
              "eau améliorée et sans électricité. {n} des 503 questions de "
              "l'enquête sont croisables."},
    "c_combiner": {"en": "How to combine the conditions",
                   "fr": "Comment combiner les conditions"},
    "c_et": {"en": "AND — the household meets ALL conditions (cumulative)",
             "fr": "ET — le foyer remplit TOUTES les conditions (cumul)"},
    "c_ou": {"en": "OR — the household meets AT LEAST ONE condition",
             "fr": "OU — le foyer remplit AU MOINS UNE condition"},
    "c_condition_q": {"en": "Condition {k} — question", "fr": "Condition {k} — question"},
    "c_le_foyer": {"en": "The household…", "fr": "Le foyer…"},
    "c_a_repondu": {"en": "answered…", "fr": "a répondu…"},
    "c_na_pas_repondu": {"en": "did NOT answer…", "fr": "n'a PAS répondu…"},
    "c_reponses": {"en": "Answer(s) concerned", "fr": "Réponse(s) concernée(s)"},
    "c_reponses_aide": {
        "en": "Several answers add up: the household counts if it ticked at least "
              "one of them.",
        "fr": "Plusieurs réponses se cumulent : le foyer compte s'il en a coché au "
              "moins une."},
    "c_ignoree": {"en": "Condition ignored: no answer selected.",
                  "fr": "Condition ignorée : aucune réponse choisie."},
    "c_seule": {"en": "This condition alone: **{n} households** ({p} %)",
                "fr": "Cette condition seule : **{n} foyers** ({p} %)"},
    "c_ajouter": {"en": "Add a condition", "fr": "Ajouter une condition"},
    "c_retirer": {"en": "Remove the last one", "fr": "Retirer la dernière"},
    "c_choisir": {"en": "Pick at least one answer to run the calculation.",
                  "fr": "Choisissez au moins une réponse pour lancer le calcul."},
    "c_bloc1": {"en": "1 · The conditions", "fr": "1 · Les conditions"},
    "c_bloc2": {"en": "2 · The result", "fr": "2 · Le résultat"},
    "c_bloc3": {"en": "3 · Where these households are",
                "fr": "3 · Où sont ces foyers"},
    "c_bloc4": {"en": "4 · Who these households are",
                "fr": "4 · Qui sont ces foyers"},
    "c_qui_en_meme_temps": {"en": "Households that, **at the same time**:",
                            "fr": "Foyers qui, **en même temps** :"},
    "c_qui_au_moins": {"en": "Households meeting **at least one** of these "
                             "conditions:",
                       "fr": "Foyers qui remplissent **au moins une** de ces "
                             "conditions :"},
    "c_a": {"en": "has", "fr": "a"},
    "c_na_pas": {"en": "does not have", "fr": "n'a pas"},
    "c_ou_mot": {"en": " or ", "fr": " ou "},
    "c_foyers_concernes": {"en": "Households concerned", "fr": "Foyers concernés"},
    "c_sur": {"en": "out of {n}", "fr": "sur {n}"},
    "c_effectif_brut": {"en": "raw count in the sample",
                        "fr": "effectif brut dans l'échantillon"},
    "c_part": {"en": "Share of the sample", "fr": "Part de l'échantillon"},
    "c_des_menages": {"en": "of the 1211 households surveyed",
                      "fr": "des 1211 ménages enquêtés"},
    "c_si_independantes": {"en": "If the conditions were independent",
                           "fr": "Si les conditions étaient indépendantes"},
    "c_plus_eleve": {
        "en": "observed higher: the situations pile up on the same households",
        "fr": "observé plus élevé : les situations se cumulent sur les mêmes foyers"},
    "c_plus_faible": {
        "en": "observed lower: the situations overlap little",
        "fr": "observé plus faible : les situations se recoupent peu"},
    "c_conditions_empilees": {"en": "Conditions stacked", "fr": "Conditions empilées"},
    "c_combinees": {"en": "combined with “{op}”", "fr": "combinées par « {op} »"},
    "c_pourquoi_independance": {
        "en": "Why compare with the “independent conditions” case",
        "fr": "Pourquoi comparer au cas « conditions indépendantes »"},
    "c_trop_peu": {
        "en": "Only {n} households match this combination. The national figure "
              "remains readable, but the breakdown by communal section and "
              "sub-population is no longer reliable — a handful of households per "
              "cell.",
        "fr": "Seulement {n} foyers correspondent à cette combinaison. Le chiffre "
              "national reste lisible, mais la répartition par section communale "
              "et par sous-population n'est plus fiable — quelques foyers par "
              "case."},
    "c_sous_population": {"en": "Sub-population", "fr": "Sous-population"},
    "c_foyers_col": {"en": "Households concerned", "fr": "Foyers concernés"},
    "c_base_col": {"en": "Base", "fr": "Base"},
    "c_part_col": {"en": "Share of the group (%)", "fr": "Part du groupe (%)"},
    "c_part_note": {
        "en": "“Share of the group” is the proportion of that group meeting the "
              "combination. That column is what compares from one row to the "
              "next, not the raw count: the groups are not the same size.",
        "fr": "« Part du groupe » = proportion de ce groupe qui remplit la "
              "combinaison. C'est cette colonne qui se compare d'une ligne à "
              "l'autre, pas l'effectif : les groupes n'ont pas la même taille."},
    "c_foyers_sur": {"en": "{n} households out of {base}",
                     "fr": "{n} foyers sur {base}"},
    "c_source": {
        "en": "Source: household survey Sept. 2024 (1211 respondents). "
              "Combinations are computed respondent by respondent, not from "
              "aggregated percentages.",
        "fr": "Source : enquête ménage sept. 2024 (1211 répondants). Les "
              "combinaisons sont calculées répondant par répondant, pas à partir "
              "des pourcentages agrégés."},
    "c_fichiers_absents": {
        "en": "Missing file(s) in the project: **{f}**.\n\nUpload them to GitHub "
              "in `data/` or at the root of the repository — both locations work.",
        "fr": "Fichier(s) absent(s) du projet : **{f}**.\n\nDéposez-les sur GitHub "
              "dans `data/` ou à la racine du dépôt — les deux emplacements "
              "fonctionnent."},

    # ------------------------------------------------------------ dimensions
    "dim1": {"en": "I. Physical and infrastructural",
             "fr": "I. Physique et infrastructures"},
    "dim2": {"en": "II. Institutional and governance",
             "fr": "II. Institutions et gouvernance"},
    "dim3": {"en": "III. Environmental and ecological",
             "fr": "III. Environnement et écologie"},
    "dim4": {"en": "IV. Economic, livelihoods and food security",
             "fr": "IV. Économie et sécurité alimentaire"},
    "dim5": {"en": "V. Social and community", "fr": "V. Social et communautaire"},
    "dim6": {"en": "VI. Human", "fr": "VI. Humain"},
    "dim7": {"en": "VII. Cultural and psychological",
             "fr": "VII. Culturel et psychologique"},

    # ------------------------------------------------------------ carte / barres
    "moins_de": {"en": "under {v}{u}", "fr": "moins de {v}{u}"},
    "et_plus": {"en": "{v}{u} and above", "fr": "{v}{u} et plus"},
    "intervalle": {"en": "{a} – {b}{u}", "fr": "{a} – {b}{u}"},
    "base_carte": {"en": "base: {n}", "fr": "base : {n}"},
    "km": {"en": "≈ 10 km", "fr": "≈ 10 km"},
    "legende_seuils": {"en": "THRESHOLDS", "fr": "SEUILS"},
    "legende_apri": {"en": "APRI SCORE", "fr": "SCORE APRI"},
    "cap_mauvais": {
        "en": "Reading the colours: green = most favourable situation, red = most "
              "concerning (here a high percentage is unfavourable).",
        "fr": "Lecture des couleurs : vert = situation la plus favorable, rouge = "
              "la plus préoccupante (ici, un pourcentage élevé est défavorable)."},
    "cap_bon": {
        "en": "Reading the colours: green = most favourable situation, red = most "
              "concerning (here a high percentage is favourable).",
        "fr": "Lecture des couleurs : vert = situation la plus favorable, rouge = "
              "la plus préoccupante (ici, un pourcentage élevé est favorable)."},
    "cap_neutre": {
        "en": "Reading the colours: from lightest to darkest by percentage. No "
              "colour judges the situation — this indicator is neither good nor "
              "bad in itself.",
        "fr": "Lecture des couleurs : du plus clair au plus foncé selon le "
              "pourcentage. Aucune couleur ne juge la situation — cet indicateur "
              "n'est ni bon ni mauvais en soi."},
    "aria_barres": {"en": "Distribution of answers, in percent",
                    "fr": "Répartition des réponses, en pourcentage"},
    "aria_comparaison": {"en": "Comparison of values", "fr": "Comparaison des valeurs"},
    "aria_radar": {"en": "Resilience profile by dimension, scores 0 to 10",
                   "fr": "Profil de résilience par dimension, scores de 0 à 10"},
    "foyers": {"en": "households", "fr": "foyers"},
}


# --------------------------------------------------------------- glossaire
GLOSSAIRE = {
    "score APRI": {
        "en": ("Mark from 0 to 10 given to a communal section on one indicator, "
               "by applying the scale of the IRLA / APRI framework. 0 = the most "
               "degraded situation observed internationally, 10 = the best. The "
               "step from measure to score is not linear: the lower classes of "
               "the scale are narrower."),
        "fr": ("Note de 0 à 10 attribuée à une section communale sur un "
               "indicateur, en appliquant le barème du cadre théorique IRLA / "
               "APRI. 0 = la situation la plus dégradée observée à l'échelle "
               "internationale, 10 = la meilleure. Le passage de la mesure au "
               "score n'est pas linéaire : les classes basses du barème sont plus "
               "resserrées.")},
    "pondération": {
        "en": ("Weight given to an indicator in the overall score, taken as is "
               "from the theoretical framework. An indicator weighted 3.61 counts "
               "three times as much as one weighted 1.20."),
        "fr": ("Poids donné à un indicateur dans le score d'ensemble, repris tel "
               "quel du cadre théorique. Un indicateur pondéré 3,61 pèse trois "
               "fois plus qu'un indicateur pondéré 1,20.")},
    "FIES": {
        "en": ("Food Insecurity Experience Scale. Measured here as the share of "
               "households reporting they ran out of food during the past twelve "
               "months."),
        "fr": ("Food Insecurity Experience Scale — échelle d'expérience de "
               "l'insécurité alimentaire. Mesure ici la part de foyers déclarant "
               "avoir manqué de nourriture au cours des douze derniers mois.")},
    "assainissement amélioré": {
        "en": ("Toilets that separate excreta from human contact: flush toilet "
               "connected to a sewer or septic tank, ventilated improved pit "
               "latrine, pit latrine with slab, composting toilet. Pit latrines "
               "without slab, buckets and open defecation are excluded."),
        "fr": ("Toilettes qui séparent les excreta du contact humain : chasse "
               "d'eau raccordée à un égout ou une fosse septique, latrine "
               "ventilée améliorée, latrine à fosse avec dalle, toilettes à "
               "compostage. Sont exclues les latrines sans dalle, les seaux et la "
               "défécation à l'air libre.")},
    "eau améliorée": {
        "en": ("Drinking water source protected from outside contamination: piped "
               "water, borehole, protected dug well, protected spring, rainwater, "
               "water kiosk, bottled or sachet water. Surface water and "
               "unprotected wells or springs are excluded."),
        "fr": ("Source d'eau de boisson protégée de la contamination extérieure : "
               "réseau, forage, puits creusé protégé, source protégée, eau de "
               "pluie, kiosque, eau en bouteille ou en sachet. Sont exclues les "
               "eaux de surface et les puits ou sources non protégés.")},
    "paysage": {
        "en": ("The setting of the communal section: coastal (or coastal plain) "
               "or mountain. Each section belongs to one of the two only."),
        "fr": ("Milieu dans lequel se trouve la section communale : littoral (ou "
               "plaine côtière) ou montagne. Chaque section relève d'un seul des "
               "deux.")},
    "section communale": {
        "en": ("The smallest administrative division in Haiti, below the commune. "
               "The survey covers ten of them, in the Sud and Grand'Anse "
               "departments."),
        "fr": ("Plus petite division administrative haïtienne, sous la commune. "
               "L'enquête en couvre dix, dans les départements du Sud et de la "
               "Grand'Anse.")},
    "mesure brute": {
        "en": ("The share of households actually measured on the ground, before "
               "any conversion into a score. That figure describes the situation; "
               "the score only says where it sits on the comparison scale."),
        "fr": ("Le pourcentage de foyers réellement mesuré sur le terrain, avant "
               "toute conversion en score. C'est ce chiffre qui décrit la "
               "situation ; le score dit seulement où il se situe sur l'échelle "
               "de comparaison.")},
    "indépendance": {
        "en": ("What stacking several conditions would give if they hit unrelated "
               "households — the plain product of the rates. An observed figure "
               "above it means the situations concentrate on the same households."),
        "fr": ("Ce que vaudrait le cumul de plusieurs conditions si elles "
               "frappaient des foyers sans rapport entre eux — le simple produit "
               "des taux. Un cumul observé supérieur signifie que les situations "
               "se concentrent sur les mêmes foyers.")},
    "base": {
        "en": ("Number of respondents a percentage is computed on. Below thirty "
               "respondents the order of magnitude still holds, but the exact "
               "figure does not."),
        "fr": ("Nombre de répondants sur lequel un pourcentage est calculé. Sous "
               "trente répondants, l'ordre de grandeur reste utilisable mais le "
               "chiffre exact ne l'est pas.")},
    "réponses multiples": {
        "en": ("A question where one household may tick several answers. The "
               "percentages then do not add up to 100 %, and adding two answers "
               "double-counts the households that ticked both."),
        "fr": ("Question où un même foyer peut cocher plusieurs réponses. Les "
               "pourcentages ne totalisent alors pas 100 %, et cumuler deux "
               "réponses compte deux fois les foyers qui ont coché les deux.")},
}

TERMES = {
    "score APRI": {"en": "APRI score", "fr": "score APRI"},
    "pondération": {"en": "weighting", "fr": "pondération"},
    "mesure brute": {"en": "raw measure", "fr": "mesure brute"},
    "base": {"en": "base", "fr": "base"},
    "réponses multiples": {"en": "multiple answers", "fr": "réponses multiples"},
    "indépendance": {"en": "independence", "fr": "indépendance"},
}


def terme(cle):
    """Le mot lui-même, dans la langue courante."""
    e = TERMES.get(cle)
    return (e.get(get_lang()) or e.get(DEFAUT)) if e else cle


def definition(cle):
    e = GLOSSAIRE.get(cle)
    return (e.get(get_lang()) or e.get(DEFAUT)) if e else ""
