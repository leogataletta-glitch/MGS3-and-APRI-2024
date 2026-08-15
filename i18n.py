"""Bilingue anglais / français.

L'anglais est la langue par défaut. Le dictionnaire est indexé par une clé
courte ; chaque entrée porte les deux versions. Les textes qui contiennent des
valeurs (« 1211 répondants ») sont des gabarits à formater avec `.format()`,
jamais des morceaux de phrase recollés — l'ordre des mots n'est pas le même
d'une langue à l'autre.
"""

import streamlit as st

# Marqueur de version du dictionnaire. app.py le compare à ce qu'il attend :
# sans cela, un i18n.py resté sur une version antérieure ne se voit pas, il
# affiche simplement le nom des clés manquantes au milieu de la page.
VERSION = "2026-08-15-ocb-fiches2"

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
    "titre_site": {
        "en": "Household resilience survey 2024 — Sud and Grand'Anse, Haiti",
        "fr": "Enquête ménage résilience 2024 — Sud et Grand'Anse, Haïti"},
    "mode_questions": {"en": "Descriptive results",
                       "fr": "Résultats descriptifs"},
    "mode_resilience": {"en": "Resilience index (IRLA / APRI)",
                        "fr": "Indice de résilience (IRLA / APRI)"},
    "mode_croisement": {"en": "Cross-tabulation",
                        "fr": "Analyse croisée"},
    "mode_methodo": {"en": "Survey methodology",
                     "fr": "Méthodologie d'enquête"},
    "mode_donnees": {"en": "Data downloads",
                     "fr": "Téléchargement des données"},
    "mode_questions_sous": {
        "en": "Univariate distributions for the 503 survey items, disaggregated "
              "by sex, age, economic status and landscape",
        "fr": "Distributions univariées des 503 items du questionnaire, "
              "désagrégées par sexe, âge, catégorie économique et paysage"},
    "mode_resilience_sous": {
        "en": "Composite index and its indicators, by communal section, "
              "dimension and sub-population",
        "fr": "Indice composite et ses indicateurs, par section communale, "
              "dimension et sous-population"},
    "mode_croisement_sous": {
        "en": "Multi-criteria conditional analysis: co-occurrence of "
              "deprivations at household level",
        "fr": "Analyse conditionnelle multicritère : cumul de privations à "
              "l'échelle du ménage"},
    "mode_methodo_sous": {
        "en": "Sampling design, questionnaire, indicator construction and "
              "known limitations",
        "fr": "Plan de sondage, questionnaire, construction des indicateurs "
              "et limites reconnues"},
    "mode_donnees_sous": {
        "en": "Anonymised datasets and result tables, in Excel and CSV",
        "fr": "Jeux de données anonymisés et tables de résultats, en Excel "
              "et CSV"},
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

    "oui": {"en": "Yes", "fr": "Oui"},
    "non": {"en": "No", "fr": "Non"},

    # ------------------------------------------------------------ tissu associatif
    "mode_ocb": {"en": "Community organisations",
                 "fr": "Tissu associatif"},
    "mode_ocb_sous": {
        "en": "Density, partnerships, governance and inclusion of "
              "community-based organisations",
        "fr": "Densité, partenariats, gouvernance et inclusion des "
              "organisations communautaires de base"},
    "o_titre": {"en": "Community-based organisations",
                "fr": "Le tissu associatif"},
    "o_sous_titre": {
        "en": "OCB identity survey · Sud and Grand'Anse, Haiti",
        "fr": "Enquête d'identité des OCB · Sud et Grand'Anse, Haïti"},
    "o_intro": {
        "en": "This section draws on a survey distinct from the household "
              "survey: {n} identity records for community-based organisations, "
              "collected across {s} communal sections. The unit of analysis is "
              "the organisation, never the household — a percentage here is a "
              "share of organisations. These figures feed the institutional and "
              "social dimensions of the resilience index.",
        "fr": "Cette section s'appuie sur une enquête distincte de l'enquête "
              "ménage : {n} fiches d'identité d'organisations communautaires de "
              "base, recueillies dans {s} sections communales. L'unité "
              "d'analyse est l'organisation, jamais le foyer — un pourcentage "
              "porte ici sur des organisations. Ces chiffres alimentent les "
              "dimensions institutionnelle et sociale de l'indice de "
              "résilience."},
    "o_avert_absentes": {
        "en": "No organisation was recorded in {s}. For those sections the "
              "density indicator reads zero — a real measurement — while the "
              "nine percentage indicators stay empty, since there is no "
              "organisation to report on. Their final resilience score is "
              "therefore computed on fewer indicators than the other sections: "
              "read the comparison with that in mind.",
        "fr": "Aucune organisation n'a été recensée à {s}. Pour ces sections, "
              "l'indicateur de densité vaut zéro — c'est une mesure réelle — "
              "tandis que les neuf indicateurs en pourcentage restent vides, "
              "faute d'organisation à interroger. Leur score final de résilience "
              "est donc calculé sur moins d'indicateurs que celui des autres "
              "sections : la comparaison est à lire en gardant cela à l'esprit."},

    "et": {"en": "and", "fr": "et"},
    "o_court_partenariat": {"en": "Has a partnership",
                            "fr": "A un partenariat"},
    "o_court_prive": {"en": "Private-sector work",
                      "fr": "Travail avec le privé"},
    "o_court_autorites": {"en": "Communal authority link",
                          "fr": "Lien avec les autorités"},
    "o_court_soumet_rapports": {"en": "Submits activity reports",
                                "fr": "Soumet des rapports"},
    "o_court_cartographie": {"en": "Holds an actor map",
                             "fr": "Cartographie des acteurs"},
    "o_court_soutien": {"en": "External support received",
                        "fr": "A reçu un appui extérieur"},
    "o_court_ong_int": {"en": "International NGO link",
                        "fr": "Lien ONG internationales"},
    "o_court_femme_direction": {"en": "Woman in leadership",
                                "fr": "Femme à la direction"},
    "o_court_jeune_direction": {"en": "Young person in leadership",
                                "fr": "Jeune à la direction"},
    "o_bloc1": {"en": "1 · The associative fabric in figures",
                "fr": "1 · Le tissu associatif en chiffres"},
    "o_bloc2": {"en": "2 · Where, across the territory",
                "fr": "2 · Où, sur le territoire"},
    "o_bloc3": {"en": "3 · All indicators, all organisations combined",
                "fr": "3 · Tous les indicateurs, toutes organisations confondues"},
    "o_bloc4": {"en": "4 · The organisations one by one",
                "fr": "4 · Les organisations une à une"},

    "o_bloc5": {"en": "5 · Organisation profile",
                "fr": "5 · La fiche d'une organisation"},
    "o_bloc5_note": {
        "en": "Everything the survey records about a single organisation, on "
              "one page. Use the filter above to narrow the list first.",
        "fr": "Tout ce que l'enquête recense sur une organisation, sur une seule "
              "page. Le filtre ci-dessus restreint d'abord la liste."},
    "o_choisir_organisation": {"en": "Choose an organisation",
                               "fr": "Choisir une organisation"},
    "o_fiche_vide": {
        "en": "No organisation matches this filter.",
        "fr": "Aucune organisation ne correspond à ce filtre."},
    "o_f_femmes": {"en": "Share of women among members",
                   "fr": "Part de femmes parmi les membres"},
    "o_f_prive": {"en": "Contribution to private / civil-society initiatives",
                  "fr": "Contribution aux initiatives privées / société civile"},
    "o_f_partenariat": {"en": "Development partnership",
                        "fr": "Partenariat de développement"},
    "o_f_type_partenariat": {"en": "Type of partnership",
                             "fr": "Type de partenariat"},
    "o_f_duree": {"en": "Partnership age", "fr": "Ancienneté du partenariat"},
    "o_f_note": {"en": "Results rated by the organisation itself",
                 "fr": "Résultats notés par l'organisation elle-même"},
    "o_f_projets": {"en": "Areas covered by the partnerships",
                    "fr": "Domaines couverts par les partenariats"},
    "o_f_projets_autre": {"en": "Other areas, specified",
                          "fr": "Autres domaines, précisés"},
    "o_f_facteurs": {"en": "What holds back better results",
                     "fr": "Ce qui empêche de meilleurs résultats"},
    "o_f_soutien": {"en": "External support received",
                    "fr": "Appui extérieur reçu"},
    "o_f_femme_dir": {"en": "Women in leadership",
                      "fr": "Femmes à la direction"},
    "o_f_jeune_dir": {"en": "People aged 18-30 in leadership",
                      "fr": "Personnes de 18 à 30 ans à la direction"},
    "o_f_cartographie": {"en": "Holds an up-to-date map of local actors",
                         "fr": "Dispose d'une cartographie des acteurs à jour"},
    "o_f_recoit": {"en": "Receives reports from",
                   "fr": "Reçoit des rapports de"},
    "o_f_soumet": {"en": "Submits reports to",
                   "fr": "Soumet des rapports à"},
    "o_f_plateforme": {
        "en": "Takes part in a coordination platform bringing together",
        "fr": "Participe à une plateforme de coordination réunissant"},
    "o_f_consulte": {"en": "Consulted for decisions by",
                     "fr": "Consultée pour les décisions par"},
    "o_f_consulte_note": {
        "en": "This question came out of the collection tool inconsistently: "
              "only the list of actors mentioned can be relied on, not which "
              "answer belonged to which.",
        "fr": "Cette question est sortie de l'outil de collecte de façon "
              "incohérente : seule la liste des acteurs cités est fiable, pas "
              "l'appariement de chaque réponse à son acteur."},
    "o_c_organisations": {"en": "Organisations recorded",
                          "fr": "Organisations recensées"},
    "o_c_organisations_sous": {"en": "across {s} communal sections",
                               "fr": "dans {s} sections communales"},
    "o_c_femmes": {"en": "A woman in leadership",
                   "fr": "Une femme à la direction"},
    "o_c_femmes_sous": {"en": "of organisations", "fr": "des organisations"},
    "o_c_partenariat": {"en": "At least one partnership",
                        "fr": "Au moins un partenariat"},
    "o_c_partenariat_sous": {"en": "of organisations", "fr": "des organisations"},
    "o_c_note": {"en": "Partnership rated", "fr": "Partenariat noté"},
    "o_c_note_sous": {"en": "self-assessment, {n} organisations",
                      "fr": "auto-évaluation, {n} organisations"},

    "o_quoi_carto": {"en": "What to map", "fr": "Quoi cartographier"},
    "o_info_carte": {"en": "{n} organisations surveyed",
                     "fr": "{n} organisations interrogées"},
    "o_carte_note": {
        "en": "Sections in grey have no organisation recorded, so no percentage "
              "can be computed there.",
        "fr": "Les sections en gris n'ont aucune organisation recensée : aucun "
              "pourcentage ne peut y être calculé."},
    "o_bloc3_note": {
        "en": "Share of the 34 organisations answering yes, all sections "
              "combined. The APRI score in brackets places that share on the "
              "0-10 scale.",
        "fr": "Part des 34 organisations répondant oui, toutes sections "
              "confondues. Le score APRI entre parenthèses situe cette part sur "
              "l'échelle de 0 à 10."},
    "o_score_annot": {"en": "score {s} / 10", "fr": "score {s} / 10"},

    "o_col_nom": {"en": "Organisation", "fr": "Organisation"},
    "o_col_partenariat": {"en": "Partnership", "fr": "Partenariat"},
    "o_col_duree": {"en": "Duration", "fr": "Ancienneté"},
    "o_col_note": {"en": "Rating / 10", "fr": "Note / 10"},
    "o_col_soutien": {"en": "External support", "fr": "Appui extérieur"},
    "o_col_autorites": {"en": "Communal authorities", "fr": "Autorités communales"},
    "o_col_ong_int": {"en": "International NGOs", "fr": "ONG internationales"},
    "o_col_femme": {"en": "Woman in leadership", "fr": "Femme à la direction"},
    "o_col_jeune": {"en": "Young person in leadership",
                    "fr": "Jeune à la direction"},
    "o_table_note": {"en": "{n} organisations displayed. The locality name is "
                           "deliberately omitted: it is an identifying detail.",
                     "fr": "{n} organisations affichées. Le nom de la localité "
                           "est volontairement omis : c'est une donnée "
                           "identifiante."},
    "o_source": {
        "en": "Source: community-based organisation identity survey, UNEP, "
              "2024. 34 records, 8 of the 10 communal sections.",
        "fr": "Source : enquête d'identité des Organisations Communautaires de "
              "Base, PNUE, 2024. 34 fiches, 8 des 10 sections communales."},

    # ------------------------------------------------------------ méthodologie
    "m_titre": {"en": "Survey methodology",
                "fr": "Méthodologie d'enquête"},
    "m_sous_titre": {
        "en": "IRLA / APRI — Landscape Resilience Index · Greater South, Haiti",
        "fr": "IRLA / APRI — Indice de résilience des paysages · Grand Sud, Haïti"},
    "m_intro": {
        "en": "This section documents how the data behind the dashboard were "
              "produced: where the survey took place, how households were drawn, "
              "what the questionnaire covers, how answers become indicators and "
              "scores, and what the approach cannot claim. It is drawn from the "
              "IRLA methodological framework note.",
        "fr": "Cette section documente la production des données du tableau de "
              "bord : où l'enquête s'est déroulée, comment les ménages ont été "
              "tirés, ce que couvre le questionnaire, comment les réponses "
              "deviennent des indicateurs et des scores, et ce que la démarche "
              "ne prétend pas établir. Elle est tirée de la note de cadrage "
              "méthodologique IRLA."},
    "m_sommaire": {"en": "Contents", "fr": "Sommaire"},
    "m_notions": {"en": "Key concepts used in this section",
                  "fr": "Notions clés employées dans cette section"},
    "m_source": {
        "en": "Source: IRLA / APRI methodological framework note (UNEP), "
              "reproduced and condensed.",
        "fr": "Source : note de cadrage méthodologique IRLA / APRI (PNUE), "
              "reprise et condensée."},

    # ------------------------------------------------------------ téléchargements
    "d_titre": {"en": "Data downloads", "fr": "Téléchargement des données"},
    "d_sous_titre": {
        "en": "Anonymised datasets and result tables",
        "fr": "Jeux de données anonymisés et tables de résultats"},
    "d_intro": {
        "en": "Every file below is generated from the same computation engine "
              "as the dashboard, so figures always match what is displayed on "
              "screen. Excel files open directly; the raw dataset is provided "
              "as CSV in UTF-8.",
        "fr": "Chaque fichier ci-dessous est produit par le même moteur de "
              "calcul que le tableau de bord : les chiffres correspondent donc "
              "toujours à ce qui est affiché à l'écran. Les fichiers Excel "
              "s'ouvrent directement ; le jeu de données brut est fourni en CSV "
              "encodé en UTF-8."},
    "d_avert": {
        "en": "Personal data — respondent name, telephone number, enumerator "
              "name, precise GPS coordinates and locality name — have been "
              "removed from every file distributed here. The files remain "
              "internal working documents: please do not redistribute them "
              "outside the project.",
        "fr": "Les données personnelles — nom du répondant, numéro de téléphone, "
              "nom de l'enquêteur, coordonnées GPS précises et nom de la "
              "localité — ont été retirées de tous les fichiers diffusés ici. "
              "Ces fichiers restent des documents de travail internes : merci "
              "de ne pas les rediffuser hors du projet."},
    "d_preparer": {"en": "Preparing the file…", "fr": "Préparation du fichier…"},
    "d_bouton": {"en": "Download", "fr": "Télécharger"},
    "d_indispo": {
        "en": "This dataset is temporarily unavailable: a source file is "
              "missing from the deployment ({f}).",
        "fr": "Ce jeu de données est momentanément indisponible : un "
              "fichier source manque au déploiement ({f})."},
    "d_contenu": {"en": "Contents", "fr": "Contenu"},
    "d_format": {"en": "Format", "fr": "Format"},

    "d1_titre": {
        "en": "1 · Descriptive results — all 503 questions by sub-population",
        "fr": "1 · Résultats descriptifs — les 503 questions par sous-population"},
    "d1_desc": {
        "en": "One row per answer option for every question in the "
              "questionnaire, with counts (n) and percentages for the 12 "
              "reference sub-populations: total, sex, economic group A/B/C, "
              "four age brackets, coastal and mountain landscape.",
        "fr": "Une ligne par modalité de réponse pour chaque question du "
              "questionnaire, avec les effectifs (n) et les pourcentages pour "
              "les 12 sous-populations de référence : total, sexe, catégorie "
              "économique A/B/C, quatre tranches d'âge, paysage littoral et "
              "montagne."},
    "d2_titre": {
        "en": "2 · Resilience indicators — raw value and APRI score by "
              "communal section",
        "fr": "2 · Indicateurs de résilience — valeur brute et score APRI par "
              "section communale"},
    "d2_desc": {
        "en": "The 128 indicators of the index, with their dimension, weight, "
              "theoretical scale, measured value (in % of households) and "
              "resulting 0–10 score, for each of the 10 communal sections and "
              "each sub-population.",
        "fr": "Les 128 indicateurs de l'indice, avec leur dimension, leur "
              "pondération, leur échelle théorique, la valeur mesurée (en % de "
              "ménages) et le score 0–10 qui en découle, pour chacune des 10 "
              "sections communales et chaque sous-population."},
    "d3_titre": {
        "en": "3 · Cross-classification — indicator scores by communal section "
              "and sub-population",
        "fr": "3 · Ventilation croisée — scores des indicateurs par section "
              "communale et sous-population"},
    "d3_desc": {
        "en": "The full section × sub-population crossing: for each communal "
              "section, each indicator is broken down by sex, economic group "
              "and age bracket, with the base count for each cell.",
        "fr": "Le croisement complet section × sous-population : pour chaque "
              "section communale, chaque indicateur est ventilé par sexe, "
              "catégorie économique et tranche d'âge, avec l'effectif de base "
              "de chaque case."},
    "d4_titre": {
        "en": "4 · Weighted composite scores — synthesis by section and "
              "dimension",
        "fr": "4 · Scores composites pondérés — synthèse par section et "
              "dimension"},
    "d4_desc": {
        "en": "The summary table: final weighted score and score for each of "
              "the seven IRLA dimensions, for every communal section and every "
              "sub-population. This is the table behind the maps and radar "
              "charts.",
        "fr": "Le tableau de synthèse : score final pondéré et score de chacune "
              "des sept dimensions IRLA, pour chaque section communale et "
              "chaque sous-population. C'est la table qui alimente les cartes "
              "et les diagrammes radar."},
    "d5_titre": {
        "en": "5 · Anonymised individual dataset — 1211 households",
        "fr": "5 · Base individuelle anonymisée — 1211 ménages"},
    "d5_desc": {
        "en": "The household-level raw responses, one row per respondent, with "
              "all direct identifiers removed. Intended for analysts who wish "
              "to run their own computations rather than read published "
              "tables.",
        "fr": "Les réponses brutes au niveau du ménage, une ligne par "
              "répondant, débarrassées de tout identifiant direct. Destinée aux "
              "analystes souhaitant conduire leurs propres calculs plutôt que "
              "lire des tables publiées."},
    "d6_titre": {
        "en": "6 · Questionnaire dictionary — the 503 items",
        "fr": "6 · Dictionnaire du questionnaire — les 503 items"},
    "d7_titre": {
        "en": "7 · Community-based organisations — the 34 identity records",
        "fr": "7 · Organisations communautaires de base — les 34 fiches"},
    "d7_desc": {
        "en": "One row per organisation: communal section, partnership and its "
              "duration, external support received, ties with communal "
              "authorities and NGOs, presence of women and of people aged 18 to "
              "30 in leadership. The locality name is omitted, being an "
              "identifying detail.",
        "fr": "Une ligne par organisation : section communale, partenariat et "
              "son ancienneté, appui extérieur reçu, liens avec les autorités "
              "communales et les ONG, présence de femmes et de personnes de 18 "
              "à 30 ans à la direction. Le nom de la localité est omis, en tant "
              "que donnée identifiante."},
    "x_ocb_fiches": {"en": "Organisations", "fr": "Organisations"},
    "x_ocb_indic": {"en": "Indicators by section", "fr": "Indicateurs par section"},
    "x_d7_note": {
        "en": "The unit is the organisation, not the household: a percentage "
              "computed from this file is a share of organisations. Two "
              "communal sections, Blactote and Dalmette, have no record.",
        "fr": "L'unité est l'organisation, non le ménage : un pourcentage "
              "calculé depuis ce fichier est une part d'organisations. Deux "
              "sections communales, Blactote et Dalmette, n'ont aucune fiche."},
    # -- intitulés employés à l'intérieur des classeurs Excel --------------
    "x_lisezmoi": {"en": "Read me", "fr": "Lisez-moi"},
    "x_confid": {
        "en": "Confidentiality — this file contains no direct identifier "
              "(name, telephone, enumerator, precise GPS coordinates, "
              "locality). It remains an internal project working document.",
        "fr": "Confidentialité — ce fichier ne contient aucun identifiant "
              "direct (nom, téléphone, enquêteur, coordonnées GPS précises, "
              "localité). Il reste un document de travail interne au projet."},
    "x_resultats": {"en": "Results", "fr": "Résultats"},
    "x_effectifs": {"en": "Base counts", "fr": "Effectifs de base"},
    "x_indicateurs": {"en": "Indicators", "fr": "Indicateurs"},
    "x_ventilation": {"en": "Section x sub-population",
                      "fr": "Section x sous-population"},
    "x_par_section": {"en": "By communal section", "fr": "Par section communale"},
    "x_national": {"en": "National and sub-groups",
                   "fr": "National et sous-groupes"},
    "x_dictionnaire": {"en": "Questionnaire", "fr": "Questionnaire"},
    "x_section_thematique": {"en": "Thematic section", "fr": "Section thématique"},
    "x_question": {"en": "Question wording", "fr": "Libellé de la question"},
    "x_type_reponse": {"en": "Answer type", "fr": "Type de réponse"},
    "x_modalite": {"en": "Answer option", "fr": "Modalité de réponse"},
    "x_groupe": {"en": "Group", "fr": "Groupe"},
    "x_base_n": {"en": "Respondents (n)", "fr": "Répondants (n)"},
    "x_ligne": {"en": "Line", "fr": "Ligne"},
    "x_dimension": {"en": "IRLA dimension", "fr": "Dimension IRLA"},
    "x_indicateur": {"en": "Indicator", "fr": "Indicateur"},
    "x_ponderation": {"en": "Weight", "fr": "Pondération"},
    "x_sens": {"en": "Direction", "fr": "Sens"},
    "x_metrique": {"en": "Metric definition", "fr": "Définition de la mesure"},
    "x_echelle": {"en": "Theoretical scale", "fr": "Échelle théorique"},
    "x_section": {"en": "Communal section", "fr": "Section communale"},
    "x_sous_pop": {"en": "Sub-population", "fr": "Sous-population"},
    "x_score_final": {"en": "Final weighted score", "fr": "Score final pondéré"},
    "x_ordre": {"en": "Order", "fr": "Ordre"},
    "x_nb_modalites": {"en": "Answer options", "fr": "Nb de modalités"},
    "x_d1_note": {
        "en": "Each row is one answer option. Percentages are computed on the "
              "base count of the group concerned, shown on the 'Base counts' "
              "sheet. On multiple-answer questions the percentages of a same "
              "question add up to more than 100, since one household can be "
              "counted in several options.",
        "fr": "Chaque ligne est une modalité de réponse. Les pourcentages sont "
              "calculés sur l'effectif de base du groupe concerné, donné dans "
              "la feuille « Effectifs de base ». Sur les questions à réponses "
              "multiples, les pourcentages d'une même question dépassent 100, "
              "un même ménage pouvant être compté dans plusieurs modalités."},
    "x_d2_note": {
        "en": "The '%' column is the measured value on the ground; the 'score' "
              "column is its position on the 0-10 IRLA scale, obtained by "
              "applying the theoretical scale shown in the last column. An "
              "empty cell means the indicator could not be computed for that "
              "group. Three scales as published (destructive fishing, "
              "experience of violence, severe food insecurity) award the top "
              "score to the most degraded situation; they have been reversed "
              "so that 10 always denotes the most favourable situation, and "
              "the score obtained from the published scale is kept in the "
              "source file for audit.",
        "fr": "La colonne « % » est la valeur mesurée sur le terrain ; la "
              "colonne « score » est sa position sur l'échelle IRLA de 0 à 10, "
              "obtenue en appliquant l'échelle théorique donnée en dernière "
              "colonne. Une case vide signifie que l'indicateur n'a pas pu "
              "être calculé pour ce groupe. Trois échelles telles que publiées "
              "(pêche destructrice, violences subies, insécurité alimentaire "
              "sévère) attribuent le score le plus haut à la situation la plus "
              "dégradée : elles ont été inversées pour que 10 désigne toujours "
              "la situation la plus favorable, le score issu de l'échelle "
              "publiée restant conservé dans le fichier source pour audit."},
    "x_d3_note": {
        "en": "One row per communal section and per indicator. The 'n' column "
              "gives the number of households the cell rests on: below about "
              "30 respondents, a percentage should be read as an order of "
              "magnitude only.",
        "fr": "Une ligne par section communale et par indicateur. La colonne "
              "« n » donne le nombre de ménages sur lequel repose la case : "
              "en dessous d'une trentaine de répondants, un pourcentage ne se "
              "lit que comme un ordre de grandeur."},
    "x_d4_note": {
        "en": "Scores are weighted averages of the indicator scores, using the "
              "weights defined by the IRLA framework. Indicators that could "
              "not be computed are excluded from both numerator and "
              "denominator, so a score always reflects only what was actually "
              "measured.",
        "fr": "Les scores sont des moyennes des scores d'indicateurs pondérées "
              "par les pondérations définies par le cadre IRLA. Les "
              "indicateurs non calculables sont exclus du numérateur comme du "
              "dénominateur : un score ne reflète donc jamais que ce qui a "
              "réellement été mesuré."},
    "x_d6_note": {
        "en": "The order column matches the order in which the questions were "
              "administered, and is the key linking this dictionary to the "
              "other files.",
        "fr": "La colonne d'ordre correspond à l'ordre de passation des "
              "questions ; c'est la clé qui relie ce dictionnaire aux autres "
              "fichiers."},

    "d6_desc": {
        "en": "The list of survey items in their order of administration, with "
              "their thematic section, question wording and answer type "
              "(single or multiple choice). Use it as the key to the other "
              "files.",
        "fr": "La liste des items de l'enquête dans leur ordre de passation, "
              "avec leur section thématique, le libellé de la question et le "
              "type de réponse (choix unique ou multiple). Sert de clé de "
              "lecture aux autres fichiers."},

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
    "r_titre_court": {"en": "Resilience", "fr": "Résilience"},
    "r_score_mot": {"en": "score", "fr": "score"},
    "r_echelle_titre": {"en": "What 0 and 10 mean", "fr": "Ce que valent 0 et 10"},
    "r_expl_indic": {"en": "What this indicator says",
                     "fr": "Ce que dit cet indicateur"},
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


# ---------------------------------------------------------------------------
# Notions issues de l'article « The Integrated Resilient Landscape Approach
# (IRLA) », F. P. Léo, PNUE. Elles alimentent les bulles d'aide : le lecteur
# doit pouvoir comprendre ce que le score dit sans avoir lu l'article.
# ---------------------------------------------------------------------------
NOTIONS = {
    'resilience': {
        "terme_en": 'Resilience (as defined by IRLA)',
        "terme_fr": "Résilience (au sens de l'IRLA)",
        "en": 'Here resilience is not the ability to endure hardship. It is the capacity of a territory, where people and nature interact, to anticipate and absorb shocks while keeping its functions, its structures and its identity, and to reorganise and learn as conditions change. It is also measured as the amount of change a system can take before it tips into a different state in which it then tends to stay. The article is explicit that resilience is not a return to a single, supposedly stable equilibrium.',
        "fr": "Ici, la résilience n'est pas la capacité à endurer. C'est la capacité d'un territoire, où société et nature interagissent, à anticiper et absorber les chocs tout en conservant ses fonctions, ses structures et son identité, et à se réorganiser et apprendre face au changement. Elle se lit aussi comme l'ampleur de perturbation qu'un système peut encaisser avant de basculer dans un autre état où il se stabilisera ensuite. L'article insiste : ce n'est pas un retour à un équilibre unique supposé stable."},
    'resilience_critique': {
        "terme_en": 'Resilience as a "deadly compliment"',
        "terme_fr": 'La résilience comme « compliment mortel »',
        "en": 'The article warns against the way resilience is often used in Haiti, to praise people\'s ability to survive the worst. It quotes the writer Lyonel Trouillot (2025), for whom this is a "deadly compliment" that values continuation rather than rupture. IRLA therefore treats resilience as structural risk reduction and a change of territorial trajectory, not as an ability to endure.',
        "fr": "L'article met en garde contre l'usage courant du mot en Haïti, qui revient à féliciter la population de sa capacité à survivre au pire. Il cite l'écrivain Lyonel Trouillot (2025), pour qui il s'agit d'un « compliment mortel » qui valorise la continuation plutôt que la rupture. L'IRLA entend donc la résilience comme une réduction structurelle du risque et un changement de trajectoire du territoire, pas comme une aptitude à endurer."},
    'irla': {
        "terme_en": 'IRLA (Integrated Resilient Landscape Approach)',
        "terme_fr": 'IRLA (approche intégrée du paysage résilient)',
        "en": "IRLA is the overall method for analysing the resilience of a landscape seen as a socio-ecological system. It rests on two complementary components: a multidimensional composite index that maps capacities in place before a shock, and a participatory causal analysis, built with local stakeholders, that identifies lock-in mechanisms, leverage points and tipping points. It has been piloted in several landscapes of Haiti's Grand Sud, notably nine coastal municipalities of the Sud department. It is designed as a strategic framing tool for public policy and investment, not as a forecasting instrument.",
        "fr": "L'IRLA est la démarche d'ensemble pour analyser la résilience d'un paysage compris comme un système socio-écologique. Elle repose sur deux volets complémentaires : un indice composite multidimensionnel qui cartographie les capacités présentes avant le choc, et une analyse causale participative, construite avec les acteurs locaux, qui met au jour les mécanismes de blocage, les points de levier et les seuils de bascule. Elle a été testée dans plusieurs paysages du Grand Sud haïtien, notamment neuf communes côtières du département du Sud. C'est un outil de cadrage stratégique pour l'action publique et l'investissement, pas un outil de prévision."},
    'apri': {
        "terme_en": 'The composite resilience index (APRI)',
        "terme_fr": "L'indice composite de résilience (APRI)",
        "en": 'The index is the measurable half of IRLA: 50 indicators grouped into 7 dimensions and derived from roughly 200 underlying metrics, each scored from 0 to 10, weighted, then averaged into a score per dimension and an overall score. It allows landscapes to be compared and interventions prioritised. The approach is the whole framework; the index is one of its two components, and it says nothing on its own about why a situation persists, which is what the causal analysis is for.',
        "fr": "L'indice est la moitié mesurable de l'IRLA : 50 indicateurs regroupés en 7 dimensions et issus d'environ 200 métriques sous-jacentes, chacun noté de 0 à 10, pondéré, puis moyenné en un score par dimension et un score global. Il permet de comparer des paysages et de hiérarchiser les interventions. L'approche est le cadre complet ; l'indice n'en est qu'un volet, et il n'explique pas à lui seul pourquoi une situation se perpétue, ce qui relève de l'analyse causale."},
    'score_capacite_pas_resilience': {
        "terme_en": 'What the score actually measures',
        "terme_fr": 'Ce que le score mesure vraiment',
        "en": 'An IRLA score does not state that a territory "is resilient". It describes the quality of the structural foundations from which resilience may emerge, that is, the conditions more or less favourable to resilience that were in place before any shock. The article is explicit that this is a contributory capacity, not resilience itself.',
        "fr": "Un score IRLA ne dit pas qu'un territoire « est résilient ». Il décrit la qualité des fondations structurelles à partir desquelles la résilience peut émerger, c'est-à-dire des conditions plus ou moins favorables installées avant tout choc. L'article le précise : il s'agit d'une capacité contributive, et non de la résilience elle-même."},
    'echelle_0_10': {
        "terme_en": 'The 0 to 10 scale',
        "terme_fr": "L'échelle de 0 à 10",
        "en": 'Every indicator is converted into 11 ordered classes, from 0 to 10, each class corresponding to a described scenario: 0 is the worst scenario, 10 the best, and the highest score always marks the most desirable situation (unfavourable indicators such as unemployment are inverted). The scale expresses a relative position rather than a physical quantity, which is why results from very different indicators can be added up. It is not linear: class boundaries are set by position within a reference distribution, so the real-world gap between 1 and 2 is not the same as between 9 and 10.',
        "fr": "Chaque indicateur est converti en 11 classes ordonnées, de 0 à 10, chaque classe correspondant à un scénario décrit : 0 est le pire scénario, 10 le meilleur, et la note la plus haute désigne toujours la situation la plus souhaitable (les indicateurs défavorables comme le chômage sont inversés). L'échelle exprime une position relative et non une quantité physique, ce qui permet d'additionner des indicateurs très différents. Elle n'est pas linéaire : les bornes de classes sont fixées par la position dans une distribution de référence, si bien que l'écart réel entre 1 et 2 n'est pas celui entre 9 et 10."},
    'bareme_comparatif': {
        "terme_en": 'Comparative empirical scale (CE)',
        "terme_fr": 'Barème comparatif empirique (CE)',
        "en": 'When reliable data exist at international or regional level, the 11 classes are cut from the observed worldwide distribution of that indicator, using quantiles. A score then tells you where the territory stands compared with the rest of the world for that indicator, independently of its unit of measurement. Because countries are not evenly spread along the range, the classes are of unequal width in raw values.',
        "fr": "Quand des données fiables existent à l'échelle internationale ou régionale, les 11 classes sont découpées dans la distribution mondiale observée de l'indicateur, par quantiles. Le score indique alors où se situe le territoire par rapport au reste du monde pour cet indicateur, indépendamment de son unité de mesure. Comme les pays ne se répartissent pas régulièrement sur l'échelle, les classes ont des largeurs inégales en valeurs brutes."},
    'bareme_normatif': {
        "terme_en": 'Local normative scale (LN)',
        "terme_fr": 'Barème normatif local (LN)',
        "en": 'Some things have no credible international benchmark, for example mangrove extent or local ecological knowledge. In that case experts and stakeholders define the two ends of the scale directly: the scenario considered critical becomes 0, the scenario considered optimal for that socio-ecological system becomes 10, and the interval is cut into nine equal steps in between.',
        "fr": "Certaines réalités n'ont pas de référentiel international crédible, par exemple l'étendue des mangroves ou les savoirs écologiques locaux. Dans ce cas, les experts et les acteurs définissent directement les deux extrémités : le scénario jugé critique devient 0, le scénario jugé optimal pour ce système socio-écologique devient 10, et l'intervalle est découpé en neuf classes équidistantes."},
    'attributs_aaa': {
        "terme_en": 'The three core attributes',
        "terme_fr": 'Les trois attributs fondamentaux',
        "en": 'Rather than a long list of resilience properties, IRLA groups them into three complementary capacities: anticipating disturbances, absorbing or attenuating their impact, and transforming the system durably. Every one of the 50 indicators is tagged with the attribute or attributes it contributes to, so a dashboard can show whether a territory is strong at coping but weak at anticipating or at changing course.',
        "fr": "Plutôt qu'une longue liste de propriétés de la résilience, l'IRLA les regroupe en trois capacités complémentaires : anticiper les perturbations, absorber ou atténuer leur impact, et transformer durablement le système. Chacun des 50 indicateurs est rattaché à l'attribut ou aux attributs auxquels il contribue, ce qui permet de voir si un territoire encaisse bien mais anticipe mal ou peine à changer de trajectoire."},
    'anticipation': {
        "terme_en": 'Anticipation',
        "terme_fr": 'Anticipation',
        "en": 'Anticipation is the ability to detect a disturbance coming and to prepare a response before it hits. In the indicator set it covers things like receiving early warning messages, taking part in preparedness drills, having a contingency plan, vaccination coverage, or climate signals such as rainfall and temperature anomalies. A territory can be well equipped to cope and still score poorly here, which means it will always be reacting late.',
        "fr": "L'anticipation est la capacité à détecter l'arrivée d'une perturbation et à préparer la réponse avant qu'elle ne frappe. Dans les indicateurs, elle recouvre par exemple la réception des messages d'alerte précoce, la participation aux exercices de préparation, l'existence d'un plan de contingence, la couverture vaccinale, ou les signaux climatiques comme les anomalies de pluie et de température. Un territoire peut être bien outillé pour encaisser et mal noté ici : il réagira toujours trop tard."},
    'absorption': {
        "terme_en": 'Absorption',
        "terme_fr": 'Absorption',
        "en": 'Absorption, also called attenuation, is the ability to limit the damage when a shock occurs and to keep essential functions running. It is the attribute carried by most indicators in the framework: water, electricity, housing quality, health services, savings and safety nets, mutual aid between households, mangroves and vegetation cover that buffer storms and drought. Strong absorption keeps a territory alive through a crisis, but it does not by itself change the situation that made the crisis damaging.',
        "fr": "L'absorption, ou atténuation, est la capacité à limiter les dégâts au moment du choc et à maintenir les fonctions essentielles. C'est l'attribut porté par la majorité des indicateurs du cadre : eau, électricité, qualité du bâti, services de santé, épargne et filets de sécurité, entraide entre ménages, mangroves et couvert végétal qui amortissent tempêtes et sécheresses. Une forte absorption permet de traverser la crise, mais ne change pas à elle seule ce qui rendait la crise dévastatrice."},
    'transformation': {
        "terme_en": 'Transformation',
        "terme_fr": 'Transformation',
        "en": "Transformation is the ability to durably change the system when the current situation is no longer tenable, rather than restoring it as it was. It shows up in indicators such as secure land tenure, girls staying in school after 15, women's autonomy, civic participation and local governance bodies, protected areas, or confidence in the future. This is the attribute that matters most for leaving a degraded but stable regime, and the one that a purely emergency-oriented programme tends to neglect.",
        "fr": "La transformation est la capacité à changer durablement le système lorsque la situation n'est plus tenable, plutôt qu'à le rétablir à l'identique. Elle apparaît dans des indicateurs comme la sécurité foncière, la scolarisation des filles après 15 ans, l'autonomie des femmes, la participation civique et les instances de gouvernance locale, les aires protégées ou la confiance dans l'avenir. C'est l'attribut décisif pour sortir d'un régime dégradé mais stable, et celui qu'une intervention purement d'urgence a tendance à négliger."},
    'resilience_negative': {
        "terme_en": 'Negative (undesirable) resilience',
        "terme_fr": 'Résilience négative (indésirable)',
        "en": 'Resilience is not automatically a good thing: a harmful situation can be extremely resilient and resist every attempt to change it. The article quotes Brian Walker, who notes that cruel dictatorships or salinised landscapes can be highly resilient, and that the challenge is then to reduce their resilience. The goal is therefore not more resilience in general, but more resilience of desirable states, and less of the undesirable ones.',
        "fr": "La résilience n'est pas bonne en soi : une situation néfaste peut être extrêmement résiliente et résister à toutes les tentatives de changement. L'article cite Brian Walker, qui rappelle que des dictatures ou des paysages salinisés peuvent être très résilients, et que l'enjeu est alors de réduire leur résilience. L'objectif n'est donc pas plus de résilience en général, mais plus de résilience des états souhaitables et moins de celle des états indésirables."},
    'piege_socio_ecologique': {
        "terme_en": 'Socio-ecological trap',
        "terme_fr": 'Piège socio-écologique',
        "en": 'A socio-ecological trap is a situation where poverty, environmental degradation, weak institutions and climate hazards feed one another, so that the effects of the problem become the causes of its own reproduction. In Haiti the article traces this to decades of deforestation, land fragmentation and resource use without regeneration, compounded from the 1980s and 1990s by trade liberalisation, the collapse of rural value chains and the weakening of the state. Getting out requires crossing thresholds, not simply adding resources.',
        "fr": "Un piège socio-écologique désigne une situation où pauvreté, dégradation environnementale, faiblesse institutionnelle et aléas climatiques se renforcent mutuellement, au point que les effets du problème en deviennent les causes. En Haïti, l'article le rattache à des décennies de déforestation, de morcellement foncier et d'exploitation sans régénération, amplifiées à partir des années 1980 et 1990 par la libéralisation commerciale, l'effondrement des filières rurales et l'affaiblissement de l'État. En sortir suppose de franchir des seuils, pas seulement d'ajouter des ressources."},
    'regime_degrade_stable': {
        "terme_en": 'Stable degraded regime',
        "terme_fr": 'Régime dégradé stable',
        "en": "A stable degraded regime is a territory that has settled into a state which is poor and ecologically damaged, yet holds together and resists change. Haiti's degraded eco-social regime is the article's central example: nearly 60 percent of the population below the poverty line, 24 percent in extreme poverty, a Gini coefficient of 0.61 and a Human Development Index of 0.535. In such a regime, strengthening capacities without questioning the state being sustained can end up consolidating the lock-in.",
        "fr": "Un régime dégradé stable désigne un territoire installé dans un état pauvre et écologiquement abîmé, qui tient pourtant ensemble et résiste au changement. Le régime éco-social dégradé d'Haïti en est l'exemple central : près de 60 % de la population sous le seuil de pauvreté, 24 % en pauvreté extrême, un coefficient de Gini de 0,61 et un indice de développement humain de 0,535. Dans un tel régime, renforcer les capacités sans interroger l'état que l'on maintient peut finir par consolider le blocage."},
    'point_de_bascule': {
        "terme_en": 'Tipping point',
        "terme_fr": 'Point de bascule',
        "en": 'A tipping point is the threshold beyond which a system changes state abruptly and in a way that is hard to reverse. As long as the threshold is not crossed some absorption capacity remains, but one additional small disturbance can be enough to trigger the shift, as with a critical loss of forest cover. This is what makes landscapes non-linear: a minor pressure can produce a major systemic effect.',
        "fr": "Un point de bascule est le seuil au-delà duquel un système change d'état brutalement et de façon difficilement réversible. Tant que le seuil n'est pas franchi, une capacité d'absorption subsiste, mais une perturbation marginale supplémentaire peut suffire à déclencher le basculement, comme lors d'une perte critique de couvert forestier. C'est ce qui rend les paysages non linéaires : une pression minime peut produire un effet systémique majeur."},
    'dim_physique': {
        "terme_en": '1. Physical and infrastructural dimension',
        "terme_fr": '1. Dimension physique et infrastructurelle',
        "en": 'This dimension looks at how solid, redundant and reachable essential infrastructure is: water, sanitation, electricity, cooking fuel, mobile coverage, all-season roads, housing quality, schools, emergency shelters and health facilities within reach. These are the assets that decide whether a shock becomes a disaster: whether an alert can be received, an area evacuated, a sick person treated, a family sheltered. It also includes failure signals such as overcrowded housing and the human toll of past extreme events.',
        "fr": "Cette dimension examine la solidité, la redondance et l'accessibilité des infrastructures essentielles : eau, assainissement, électricité, combustible de cuisson, couverture mobile, routes praticables toute l'année, qualité du bâti, écoles, abris d'urgence et centres de santé à proximité. Ce sont ces équipements qui décident si un choc devient une catastrophe : pouvoir recevoir une alerte, évacuer, soigner, abriter une famille. Elle intègre aussi des signaux de défaillance comme la surpopulation des logements et le bilan humain des événements extrêmes passés."},
    'dim_institutionnelle': {
        "terme_en": '2. Institutional, technological and governance dimension',
        "terme_fr": '2. Dimension institutionnelle, technologique et de gouvernance',
        "en": 'This dimension goes beyond checking that bodies, plans and regulations exist, and looks at the quality of relations between public authorities, local government, community organisations, NGOs and the private sector. Trust, or its absence, is decisive: excessive mistrust produces blockages, conflict, non-compliance with rules and risk-averse organisations. Indicators include early warning access, existence of local risk management committees and emergency plans, civil registration, participation in local governance, satisfaction with public services, and exposure to corruption.',
        "fr": "Cette dimension ne se contente pas de vérifier l'existence d'instances, de plans et de règlements : elle porte sur la qualité des relations entre autorités publiques, collectivités, organisations communautaires, ONG et secteur privé. La confiance, ou son absence, y est décisive : une défiance excessive engendre blocages, conflits, non-respect des règles et cultures organisationnelles frileuses. Les indicateurs couvrent l'accès à l'alerte précoce, l'existence de comités locaux de gestion des risques et de plans d'urgence, l'état civil, la participation à la gouvernance locale, la satisfaction envers les services publics et l'exposition à la corruption."},
    'dim_environnementale': {
        "terme_en": '3. Environmental and ecological dimension',
        "terme_fr": '3. Dimension environnementale et écologique',
        "en": "This is the state and functioning of the natural base on which everything else rests. It combines three families of measures: the spatial structure of habitats (size, shape, fragmentation), numerical indices of richness and diversity of the landscape mosaic, and functional indicators of ecological connectivity and the landscape's ability to keep performing its roles. In practice it mixes satellite signals on vegetation, water, soil erosion and forest cover change with field biodiversity surveys and the extent of mangroves, seagrass and protected areas, all of which physically buffer storms, floods and drought.",
        "fr": "Il s'agit de l'état et du fonctionnement de la base naturelle sur laquelle tout le reste repose. Elle combine trois familles de mesures : la structure spatiale des habitats (taille, forme, fragmentation), des indices numériques de richesse et de diversité de la mosaïque paysagère, et des indicateurs fonctionnels de connectivité écologique et de maintien des fonctions du paysage. Concrètement, elle croise des signaux satellitaires sur la végétation, l'eau, l'érosion des sols et l'évolution du couvert forestier avec des relevés de biodiversité de terrain et l'étendue des mangroves, herbiers et aires protégées, qui amortissent physiquement tempêtes, inondations et sécheresses."},
    'dim_economique': {
        "terme_en": '4. Economic, livelihoods and food security dimension',
        "terme_fr": "4. Dimension économique, moyens d'existence et sécurité alimentaire",
        "en": 'This dimension captures how diversified productive activities are, how accessible economic resources are, and how stable incomes are. It covers access to accounts and financial services, employment, land tenure security, household debt, remittances, savings and safety nets, crop and fishing diversity, and losses of crops or livestock. Its logic is simple: a household with several sources of income and something to fall back on absorbs a shock; one whose reserves cover less than a week does not.',
        "fr": "Cette dimension saisit la diversification des activités productives, l'accès aux ressources économiques et la stabilité des revenus. Elle couvre l'accès à un compte et aux services financiers, l'emploi, la sécurité foncière, l'endettement des ménages, les transferts reçus, l'épargne et les filets de sécurité, la diversité des cultures et des espèces pêchées, ainsi que les pertes de récoltes ou de bétail. La logique est simple : un ménage à plusieurs sources de revenus et disposant d'une réserve absorbe un choc ; celui dont les réserves couvrent moins d'une semaine, non."},
    'dim_sociale': {
        "terme_en": '5. Social and community dimension',
        "terme_fr": '5. Dimension sociale et communautaire',
        "en": "This dimension measures social capital: relationships, reciprocity networks, shared norms, trust, collective participation and access to resources through others. It distinguishes three kinds of ties, within the close circle, between communities, and between communities and institutions. Concretely it tracks mutual aid given and received, peaceful conflict resolution, feeling safe, isolation, women's autonomy and girls' schooling. In a crisis these ties are often the first and fastest safety net available.",
        "fr": "Cette dimension mesure le capital social : relations, réseaux de réciprocité, normes partagées, confiance, participation collective et accès aux ressources par autrui. Elle distingue trois types de liens : à l'intérieur du cercle proche, entre communautés, et entre communautés et institutions. Concrètement, elle suit l'entraide donnée et reçue, la résolution pacifique des conflits, le sentiment de sécurité, l'isolement, l'autonomie des femmes et la scolarisation des filles. En cas de crise, ces liens constituent souvent le filet de sécurité le plus rapide."},
    'capital_social_liens': {
        "terme_en": 'Bonding, bridging and linking ties',
        "terme_fr": "Liens d'entraide, de passerelle et d'accès",
        "en": 'The article distinguishes three forms of social relations that do not play the same role. Bonding ties are those inside the close circle of family and relatives and provide immediate mutual aid. Bridging ties connect households across the village or between communities and allow resources and information to circulate more widely. Linking ties connect communities to public institutions, and are what turns local needs into institutional responses.',
        "fr": "L'article distingue trois formes de relations sociales qui ne jouent pas le même rôle. Les liens de proximité unissent la famille et les proches et assurent l'entraide immédiate. Les liens passerelles relient les ménages au sein du village ou entre communautés et font circuler plus largement ressources et informations. Les liens verticaux relient les communautés aux institutions publiques : ce sont eux qui transforment un besoin local en réponse institutionnelle."},
    'dim_humaine': {
        "terme_en": '6. Human dimension',
        "terme_fr": '6. Dimension humaine',
        "en": 'This dimension reflects the people themselves and their capacity to adapt, through education, health and access to essential services. It includes skilled birth attendance, child and maternal mortality, doctor, nurse and traditional health worker density, vaccination coverage, primary education completion and adults with no formal education, severe food insecurity, holding a national ID, and violent death rates. These are slow-moving assets: they take years to build and, once lost, they constrain everything else.',
        "fr": "Cette dimension traduit les personnes elles-mêmes et leur capacité d'adaptation, à travers l'éducation, la santé et l'accès aux services essentiels. Elle inclut les accouchements assistés, la mortalité infantile et maternelle, la densité de médecins, d'infirmières et de soignants traditionnels, la couverture vaccinale, l'achèvement du primaire et la part d'adultes sans instruction, l'insécurité alimentaire sévère, la possession d'une pièce d'identité et les taux de morts violentes. Ce sont des acquis lents : longs à construire et, une fois perdus, ils contraignent tout le reste."},
    'dim_culturelle': {
        "terme_en": '7. Cultural, identity-based and psychological dimension',
        "terme_fr": '7. Dimension culturelle, identitaire et psychologique',
        "en": "This dimension captures the intangible levers of collective mobilisation: attachment to place, trust, beliefs, the feeling of being able to act, and local knowledge. Culture, understood as shared values, practices and meaning systems, is treated as a genuine resource that helps a community interpret adversity, keep its identity and hold together. Its indicators include environmental awareness, confidence in the future, sense of belonging, traditional knowledge, mutual aid, awareness of rights, welcoming displaced people, and spiritual grounding. This dimension is usually missing from resilience frameworks, and it is one of IRLA's distinctive contributions.",
        "fr": "Cette dimension saisit les leviers immatériels de la mobilisation collective : attachement au lieu, confiance, croyances, sentiment de pouvoir agir et savoirs locaux. La culture, entendue comme valeurs, pratiques et systèmes de sens partagés, y est traitée comme une ressource véritable, qui aide une communauté à interpréter l'adversité, à maintenir son identité et à tenir ensemble. Ses indicateurs vont de la conscience environnementale à la confiance dans l'avenir, au sentiment d'appartenance, aux savoirs traditionnels, à l'entraide, à la connaissance de ses droits, à l'accueil des personnes déplacées et à l'ancrage spirituel. Rarement présente dans les cadres existants, elle constitue un apport propre à l'IRLA."},
    'ponderation': {
        "terme_en": 'Indicator weighting',
        "terme_fr": 'Pondération des indicateurs',
        "en": 'Not all indicators count the same. A panel of experts rated the importance of each one on a five-point scale from "not important at all" to "essential", and these ratings were converted into weights, deliberately amplifying the gap at the top of the scale, since the distinction between "very important" and "essential" is treated as more meaningful than distinctions between the lower levels. Weights are then expressed relative to the lowest-rated indicator, which is set at 1: a weight of 3 means the indicator counts three times as much as that reference. The purpose is a transparent and reproducible scheme anchored in the Haitian context, not an absolute truth about importance.',
        "fr": "Tous les indicateurs ne pèsent pas le même poids. Un panel d'experts a noté l'importance de chacun sur une échelle en cinq points, de « pas important du tout » à « essentiel », puis ces notes ont été converties en poids en amplifiant volontairement les écarts en haut de l'échelle, la distinction entre « très important » et « essentiel » étant jugée plus significative que celles du bas. Les poids sont ensuite exprimés par rapport à l'indicateur le moins bien noté, fixé à 1 : un poids de 3 signifie que l'indicateur compte trois fois plus que cette référence. L'objectif est un dispositif transparent, reproductible et ancré dans le contexte haïtien, non une mesure absolue de l'importance."},
    'agregation': {
        "terme_en": 'From indicators to a dimension score',
        "terme_fr": "Des indicateurs au score d'une dimension",
        "en": 'The score of a dimension is the weighted average of the 0 to 10 scores of the indicators it contains, so each dimension stays on the same 0 to 10 scale and remains directly comparable to the others. Indicators judged more critical by the expert panel simply pull the result more strongly. The article stresses that no single indicator can characterise resilience on its own: good sanitation coverage, for instance, says nothing about health resilience without water quality, density and service governance.',
        "fr": "Le score d'une dimension est la moyenne pondérée des notes de 0 à 10 des indicateurs qui la composent, ce qui maintient chaque dimension sur la même échelle de 0 à 10 et la rend directement comparable aux autres. Les indicateurs jugés plus critiques par le panel d'experts tirent simplement le résultat plus fortement. L'article rappelle qu'aucun indicateur ne peut à lui seul caractériser la résilience : un bon taux d'assainissement ne dit rien de la résilience sanitaire sans la qualité de l'eau, la densité de population et la gouvernance des services."},
    'section_communale': {
        "terme_en": 'Communal section',
        "terme_fr": 'Section communale',
        "en": 'The communal section is the local administrative unit at which the household survey is designed to be statistically representative. The sample targets at least around 120 households per communal section, for a 90 percent confidence level and a margin of error of 7.5 percent. This choice keeps the results close enough to lived realities to guide local action, while remaining robust enough to be compared and aggregated upward to municipality or landscape level.',
        "fr": "La section communale est l'unité administrative locale au niveau de laquelle l'enquête ménage est conçue pour être statistiquement représentative. L'échantillon vise au minimum environ 120 ménages par section communale, pour un niveau de confiance de 90 % et une marge d'erreur de 7,5 %. Ce choix garde les résultats assez proches des réalités vécues pour orienter l'action locale, tout en restant assez robustes pour être comparés et agrégés au niveau de la commune ou du paysage."},
    'echantillonnage': {
        "terme_en": 'Sampling design',
        "terme_fr": "Plan d'échantillonnage",
        "en": 'Households are drawn at random within strata that reproduce the make-up of the population: type of landscape (coastal or mountainous), age (15 to 30, or over 30), sex, and economic category (extreme poverty, poverty, non-poverty). Selection relies on a georeferenced building database derived from OpenStreetMap, which limits selection bias and ensures spatial coverage. Because each stratum is represented according to its real demographic weight, average scores can be read directly, with no further correction.',
        "fr": "Les ménages sont tirés au hasard à l'intérieur de strates qui reproduisent la composition de la population : type de paysage (côtier ou montagneux), âge (15-30 ans ou plus de 30 ans), sexe et catégorie économique (pauvreté extrême, pauvreté, non-pauvreté). La sélection s'appuie sur une base géoréférencée de bâtiments issue d'OpenStreetMap, ce qui limite les biais de sélection et assure la couverture spatiale. Chaque strate étant représentée selon son poids démographique réel, les scores moyens se lisent directement, sans correction supplémentaire."},
    'profils': {
        "terme_en": 'Disaggregated profiles',
        "terme_fr": 'Profils désagrégés',
        "en": 'Results can be read at household level or regrouped by age, sex, municipality or landscape, and also by combinations, for example women living in extreme poverty in mountain areas. This flexibility is what makes the tool operational: it reveals pockets of fragility and contrasting resilience profiles that a single territorial average would hide, and it points to who should be targeted first.',
        "fr": "Les résultats se lisent au niveau du ménage ou par regroupements selon l'âge, le sexe, la commune ou le paysage, et aussi par combinaisons, par exemple les femmes en pauvreté extrême en zone de montagne. Cette souplesse fait l'intérêt opérationnel de l'outil : elle révèle des poches de fragilité et des profils de résilience contrastés qu'une moyenne territoriale masquerait, et indique qui cibler en priorité."},
    'paysage': {
        "terme_en": 'Landscape as the unit of analysis',
        "terme_fr": "Le paysage comme unité d'analyse",
        "en": 'IRLA assesses resilience at the scale of the landscape, understood as a mosaic of ecosystems, settlements and land uses covering from a few hundred to several thousand square kilometres. Landscape boundaries do not necessarily follow administrative or sectoral divisions, and that is precisely the point: it is at this intermediate scale that the interactions between people, economic activity and ecosystems actually play out. A landscape is more than the sum of its parts, which is why resilience cannot be read from a single indicator or a single sector.',
        "fr": "L'IRLA évalue la résilience à l'échelle du paysage, entendu comme une mosaïque d'écosystèmes, d'habitats et d'usages du sol couvrant de quelques centaines à plusieurs milliers de kilomètres carrés. Les limites d'un paysage ne coïncident pas nécessairement avec les découpages administratifs ou sectoriels, et c'est justement l'intérêt : c'est à cette échelle intermédiaire que se jouent réellement les interactions entre populations, activités et écosystèmes. Un paysage vaut plus que la somme de ses parties, d'où l'impossibilité de lire sa résilience dans un seul indicateur ou un seul secteur."},
    'systeme_socio_ecologique': {
        "terme_en": 'Socio-ecological system (SES)',
        "terme_fr": 'Système socio-écologique (SSE)',
        "en": 'A socio-ecological system is a whole in which communities, institutions, economic activities, biodiversity and natural cycles evolve together and cannot be understood separately. Following Ostrom, it brings together resources, actors, governance arrangements, interactions and outcomes. Treating a territory this way means accepting that an action on one component, such as reforestation, will produce effects on all the others.',
        "fr": "Un système socio-écologique est un ensemble où communautés, institutions, activités économiques, biodiversité et cycles naturels évoluent ensemble et ne peuvent être compris séparément. Dans la lignée d'Ostrom, il réunit des ressources, des acteurs, des règles de gouvernance, des interactions et des résultats. Considérer un territoire ainsi, c'est admettre qu'une action sur une composante, la reforestation par exemple, produira des effets sur toutes les autres."},
    'vulnerabilite_structurelle': {
        "terme_en": 'Why structural vulnerability matters more than hazard intensity',
        "terme_fr": "Pourquoi la vulnérabilité structurelle pèse plus que l'intensité de l'aléa",
        "en": "Human losses in a disaster depend less on how violent the hazard is than on the conditions that existed beforehand. During Hurricane Melissa in October 2025, Haiti was outside the core of the system and mainly received several days of rain, yet recorded 43 deaths, close to Jamaica's 45 despite a direct Category 5 landfall there. The Dominican Republic, hit by comparable rainfall, recorded a single death. In Petit-Goâve most fatalities came from settlement on flood-prone riverbanks, an obstructed riverbed, inadequate infrastructure and late warnings.",
        "fr": "Les pertes humaines lors d'une catastrophe dépendent moins de la violence de l'aléa que des conditions préexistantes. Lors de l'ouragan Melissa en octobre 2025, Haïti se trouvait hors du cœur du système et n'a subi que plusieurs jours de pluie, mais a compté 43 morts, proche des 45 de la Jamaïque, pourtant frappée directement en catégorie 5. La République dominicaine, exposée à des pluies comparables, n'a déploré qu'un décès. À Petit-Goâve, l'essentiel des victimes tient à l'habitat en berge inondable, à l'obstruction du lit de la rivière, à des infrastructures inadaptées et à une alerte tardive."},
    'types_indicateurs': {
        "terme_en": 'The three types of indicators',
        "terme_fr": "Les trois types d'indicateurs",
        "en": 'The 50 indicators fall into three complementary families. Capacity and resource indicators describe what can be mobilised in the face of a disturbance. System failure outcomes, such as overcrowding, food insecurity or soil erosion, signal the structural pressures that limit or distort the use of those capacities. Adaptive social dynamics indicators, such as mutual aid, participation or confidence in the future, show whether capacities actually get turned into action. Together they treat resilience as a process linking potential, constraint and activation, rather than a stock of resources.',
        "fr": "Les 50 indicateurs se répartissent en trois familles complémentaires. Les indicateurs de capacités et de ressources décrivent ce qui peut être mobilisé face à une perturbation. Les indicateurs de défaillance du système, comme la surpopulation des logements, l'insécurité alimentaire ou l'érosion des sols, signalent les pressions structurelles qui limitent ou déforment l'usage de ces capacités. Les indicateurs de dynamiques sociales adaptatives, comme l'entraide, la participation ou la confiance dans l'avenir, montrent si les capacités se traduisent effectivement en actes. Ensemble, ils font de la résilience un processus liant potentiel, contrainte et activation, et non un stock de ressources."},
    'boucle_retroaction': {
        "terme_en": 'Feedback loops, trade-offs and synergies',
        "terme_fr": 'Boucles de rétroaction, arbitrages et synergies',
        "en": 'Landscape dynamics rarely move in straight lines. There are trade-offs, when gaining on one side costs on another, as when charcoal income intensifies deforestation; synergies, as when restoring biodiversity also improves food security; compensations, when a temporary gain masks a loss elsewhere; and reinforcing loops, when a disturbance feeds its own amplification, as when overexploiting mangroves reduces fish stocks and increases pressure on the mangroves. Reading these loops is what tells you whether an action will spread or backfire.',
        "fr": "Les dynamiques d'un paysage suivent rarement des lignes droites. Il existe des arbitrages, quand un gain d'un côté se paie de l'autre, par exemple lorsque le revenu du charbon intensifie la déforestation ; des synergies, quand restaurer la biodiversité améliore aussi la sécurité alimentaire ; des compensations, quand un gain temporaire masque une dégradation ailleurs ; et des boucles renforçantes, quand une perturbation alimente sa propre amplification, comme la surexploitation des mangroves qui réduit la ressource halieutique et accroît la pression sur les mangroves. Lire ces boucles indique si une action se diffusera ou se retournera."},
    'point_de_levier': {
        "terme_en": 'Leverage point',
        "terme_fr": 'Point de levier',
        "en": 'A leverage point is an upstream variable that appears in several feedback loops at once, so acting on it changes the structural causes rather than the visible symptoms. Isolated reforestation that ignores poverty or fodder shortages will not durably stop deforestation; combining alternatives to charcoal, better fodder systems, secure land tenure and stronger community governance can. Each leverage point identified is written up as an action sheet stating its objective, feasibility, actors involved, risks and expected resilience gains.',
        "fr": "Un point de levier est une variable en amont qui intervient dans plusieurs boucles de rétroaction à la fois : agir dessus modifie les causes structurelles plutôt que les symptômes visibles. Une reforestation isolée qui ignore la pauvreté ou le manque de fourrage n'arrêtera pas durablement la déforestation ; combiner alternatives au charbon, systèmes fourragers, sécurisation foncière et gouvernance communautaire le peut. Chaque point de levier identifié est traduit en fiche d'action précisant objectif, faisabilité, acteurs concernés, risques et gains de résilience attendus."},
    'resilience_generale': {
        "terme_en": 'General versus specified resilience',
        "terme_fr": 'Résilience générale et résilience spécifiée',
        "en": 'Specified resilience answers "resilience of what, to what": one component facing one identified hazard, for example a bridge facing flooding. General resilience is the capacity to cope with multiple, unknown or emerging disturbances at once. IRLA deliberately assesses general resilience, which fits a context where climatic, economic and institutional shocks arrive together and cannot be listed in advance.',
        "fr": "La résilience spécifiée répond à la question « résilience de quoi, face à quoi » : une composante face à un aléa identifié, par exemple un pont face aux crues. La résilience générale est la capacité à faire face à des perturbations multiples, inconnues ou émergentes. L'IRLA évalue délibérément la résilience générale, adaptée à un contexte où chocs climatiques, économiques et institutionnels surviennent ensemble et ne peuvent être listés à l'avance."},
    'pas_de_seuil': {
        "terme_en": 'Why there is no "resilient" threshold',
        "terme_fr": "Pourquoi il n'y a pas de seuil de « territoire résilient »",
        "en": 'It would be technically possible to declare a territory resilient above a given score, as some methods do at one third of the scale, but the article rejects this: no universal threshold exists that would justify such a conclusion from a single index value. Interpretation therefore relies on visual comparison, radar charts by dimension or by group, and maps with graded colours that reveal spatial gradients and hotspots. The score is a tool for comparing and prioritising, not for certifying.',
        "fr": "Il serait techniquement possible de déclarer un territoire résilient au-dessus d'un score donné, comme le font certaines méthodes au tiers de l'échelle, mais l'article s'y refuse : aucun seuil universel ne permet de conclure ainsi à partir d'une seule valeur d'indice. L'interprétation passe donc par la comparaison visuelle, les graphiques radar par dimension ou par groupe, et des cartes en couleurs graduées faisant apparaître gradients spatiaux et points chauds. Le score sert à comparer et à hiérarchiser, pas à certifier."},
    'limites': {
        "terme_en": 'Known limits of the index',
        "terme_fr": "Limites reconnues de l'indice",
        "en": 'The article states its own limits. Composite indices carry a circularity risk: resilience is defined through the very variables assumed to produce it, so a rising score may reflect improvement in what is measured rather than genuinely greater resilience. IRLA also situates itself at phase 4 of the OECD-UN scale, an operational index applied to a limited area; being validated against real observed shocks, phase 6, remains ahead. Its authors note that among more than 271 resilience tools identified in 2021, most have never been empirically validated.',
        "fr": "L'article énonce ses propres limites. Les indices composites comportent un risque de circularité : la résilience est définie par les variables mêmes censées la produire, si bien qu'un score en hausse peut refléter l'amélioration de ce qui est mesuré plutôt qu'un réel gain de résilience. L'IRLA se situe par ailleurs à la phase 4 de l'échelle OCDE-ONU, celle d'un indice opérationnel appliqué à un territoire limité ; la validation face à des chocs réellement observés, phase 6, reste à venir. Ses auteurs rappellent que, parmi plus de 271 outils de résilience recensés en 2021, la plupart n'ont jamais été validés empiriquement."},
    'appropriation': {
        "terme_en": 'Local ownership of the results',
        "terme_fr": 'Appropriation locale des résultats',
        "en": "Research on participatory modelling shows that simply handing a tool over to outside managers leads to little ownership and a technocratic perception of the exercise. The article therefore concludes that IRLA's future progress depends less on adding indicators than on sustaining spaces for dialogue: joint interpretation of results, facilitated foresight workshops and tailored training.",
        "fr": "Les travaux sur la modélisation participative montrent que transférer un outil à des gestionnaires extérieurs conduit à une faible appropriation et à une perception technocratique de la démarche. L'article conclut donc que le progrès de l'IRLA dépend moins de l'ajout d'indicateurs que du maintien d'espaces de dialogue : co-interprétation des résultats, animation d'ateliers prospectifs et cycles de formation adaptés."},
}


def notion(cle):
    """(terme, définition) dans la langue courante, ou (None, None)."""
    e = NOTIONS.get(cle)
    if not e:
        return None, None
    lg = get_lang()
    return (e.get(f"terme_{lg}") or e.get("terme_en"),
            e.get(lg) or e.get("en"))


# ----------------------------------------------------------------------
# Les réponses de l'enquête OCB ont été saisies en français. Les options
# fermées se traduisent, ce qui évite une fiche à moitié anglaise ; le texte
# libre saisi sur le terrain reste tel quel, on ne réécrit pas ce que les gens
# ont écrit. Le remplacement se fait du libellé le plus long au plus court :
# « Ressources humaines » ne doit pas être coupé par « Ressources ».
# ----------------------------------------------------------------------
REPONSES_EN = {
    "Oui, formellement (accord écrit)": "Yes, formally (written agreement)",
    "Oui, informellement": "Yes, informally",
    "Oui, un seul partenariat avec une organisation locale":
        "Yes, one partnership with a local organisation",
    "Oui, plusieurs partenariats avec organisations locales":
        "Yes, several partnerships with local organisations",
    "Oui, un seul partenariat avec une organisation externe":
        "Yes, one partnership with an external organisation",
    "Oui, plusieurs partenariats avec une organisation externe":
        "Yes, several partnerships with external organisations",
    "Oui, avec des organisations locales et organisations externes":
        "Yes, with both local and external organisations",
    "Oui, renforcement de capacités humaines": "Yes, capacity building",
    "Oui, soutien financier": "Yes, financial support",
    "Oui, matériels": "Yes, equipment",
    "Oui, une personne dans le passé": "Yes, one person in the past",
    "Oui, plusieurs dans le passé": "Yes, several in the past",
    "Oui, une personne actuellement": "Yes, one person currently",
    "Oui, plusieurs actuellement": "Yes, several currently",
    "5 ans et plus": "5 years and over",
    "1-5 ans": "1 to 5 years",
    "0-1 an": "under 1 year",
    "Adhésion de la communauté": "Community buy-in",
    "Ressources financières": "Financial resources",
    "Ressources humaines": "Human resources",
    "Gestion de déchets": "Waste management",
    "Infrastructures": "Infrastructure",
    "Communication": "Communication",
    "Education": "Education",
    "Sante": "Health",
    "Autorités communales": "Communal authorities",
    "Autorités départementales": "Departmental authorities",
    "Institutions techniques": "Technical institutions",
    "Sénateurs/députés": "Senators / deputies",
    "ONG internationales": "International NGOs",
    "ONG locales": "Local NGOs",
    "Délégation": "Delegation",
    "Autre": "Other",
    "Oui": "Yes",
    "Non": "No",
}
_REPONSES_ORDRE = sorted(REPONSES_EN, key=len, reverse=True)


def reponse(texte):
    """Traduit les options fermées d'une réponse d'enquête, en anglais seulement."""
    if texte is None or get_lang() != "en":
        return texte
    out = str(texte)
    for fr in _REPONSES_ORDRE:
        if fr in out:
            out = out.replace(fr, REPONSES_EN[fr])
    return out
