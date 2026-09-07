"""« À propos » et « Contact » : d'où vient cet indice, et à qui écrire.

POURQUOI UNE PAGE « À PROPOS » SUR UN TABLEAU DE BORD.
Le site montre des chiffres sur un territoire habité, et il les montre à des
gens qui n'étaient pas dans la salle quand la méthode a été arrêtée. Un
lecteur qui trouve un score de 3,4 sur l'accès à l'eau a le droit de savoir
qui l'a produit, à partir de quoi, dans quel cadre, et vers qui se tourner
s'il le conteste. Sans cette page, l'indice arrive de nulle part et il faut
le croire sur parole ; avec elle, il est attribuable.

CE QUE CETTE PAGE NE FAIT PAS.
Elle ne répète pas la méthode — le cadre de résilience l'expose déjà en
détail, avec ses sept dimensions, ses barèmes et ses pondérations. Elle
raconte l'histoire et nomme les responsables, ce qu'aucun autre écran ne
fait.

LES NOMBRES SONT LUS DANS LES FICHIERS, PAS ÉCRITS DANS LA PHRASE.
« Cent vingt-huit indicateurs » saisi en toutes lettres devient faux le jour
où le référentiel en gagne un, et rien ne le signale. Ils sont donc comptés
à l'ouverture, dans les mêmes fichiers que le reste du site.
"""

import csv
import json
import os

import streamlit as st

import i18n
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"
VERT, VERT_PALE = "#1f5b46", "#eef4f0"
# L'ADRESSE À LAQUELLE ON ÉCRIT, EN UN SEUL ENDROIT. Une adresse recopiée dans
# deux libellés de langue se corrige un jour dans l'un et pas dans l'autre, et
# la version anglaise du site continue d'envoyer le courrier au mauvais
# endroit ; celle-ci ne se traduit pas, elle est la même partout.
COURRIEL = "florent.leo@un.org"
BORD = "#e4eae6"

TEXTES = {
    "ap_titre": {"en": "About APRI", "fr": "À propos d'APRI"},

    # ---- L'INITIATIVE, AVANT L'INDICE. La page ouvrait sur « ce qu'est cet
    # indice » : elle expliquait l'instrument de mesure à qui ne savait pas
    # encore ce qu'on mesurait ni pour qui. Le texte institutionnel d'APRI
    # passe donc devant, et la partie technique reste dessous, à sa place.
    "ap_q_t": {"en": "What is APRI?", "fr": "Qu'est-ce qu'APRI ?"},
    "ap_q_x": {
        "en": "The Integrated Resilient Landscape Approach (APRI) is an "
              "initiative led by the United Nations Environment Programme "
              "(UNEP) which aims to establish effective models of "
              "multi-dimensional resilience against household vulnerability. "
              "This integrated approach rests on harmonising ecological, "
              "human and productive dynamics, so as to foster a balanced and "
              "resilient development of the territories concerned. In line "
              "with the UNSDCF, that integration also runs through better "
              "coordination between humanitarian and development actors "
              "alongside local actors, in order to align and multiply their "
              "actions, and to create operational synergies and concrete "
              "leverage.",
        "fr": "L'Approche Paysages Résilients Intégrée (APRI) est une "
              "initiative portée par le Programme des Nations unies pour "
              "l'environnement (PNUE) qui vise à établir des modèles "
              "efficaces de résilience multidimensionnelle face à la "
              "vulnérabilité des ménages. Cette approche intégrée repose sur "
              "une harmonisation des dynamiques écologiques, humaines et "
              "productives afin de favoriser un développement équilibré et "
              "résilient des territoires ciblés. En alignement avec l'UNSDCF, "
              "cette intégration passe aussi par une meilleure coordination "
              "des actions des acteurs humanitaires et de développement "
              "auprès des acteurs locaux, pour aligner et multiplier les "
              "actions afin de créer des synergies opérationnelles et des "
              "effets de levier concrets."},

    "ap_p_t": {"en": "Why APRI?", "fr": "Pourquoi APRI ?"},
    "ap_p_x": {
        "en": "The communities we work with face a singular combination of "
              "socio-economic vulnerability, environmental degradation and "
              "fragile governance systems. Recurrent natural disasters and "
              "climate change compound these challenges, which often traps "
              "these communities in cycles of poverty. The interconnected "
              "nature of these problems is at the heart of the case for "
              "APRI: fragmented approaches, each focused on one issue in "
              "isolation, fail to address the root causes of those "
              "vulnerabilities. Integration makes it possible to answer "
              "several challenges at once, and so to produce lasting impact.",
        "fr": "Les communautés avec lesquelles nous travaillons sont "
              "confrontées à une combinaison unique de vulnérabilités "
              "socio-économiques, de dégradation environnementale et de "
              "systèmes de gouvernance fragiles. Les catastrophes naturelles "
              "récurrentes et les changements climatiques exacerbent ces "
              "défis, ce qui piège souvent ces communautés dans des cycles de "
              "pauvreté. La nature interconnectée de ces problèmes est au "
              "cœur de la justification d'APRI : les approches fragmentées, "
              "qui se concentrent sur des problématiques isolées, échouent à "
              "traiter les causes profondes de ces vulnérabilités. "
              "L'intégration permet de répondre simultanément aux défis, "
              "créant ainsi un impact durable."},

    "ap_y_t": {"en": "Which pilot landscapes", "fr": "Quels paysages pilotes"},
    "ap_y_x": {
        "en": "The approach is piloted by UNEP in two territories, called "
              "landscapes, of the Grand-Sud region, designated as priority "
              "areas in the Integrated Recovery Plan for the Southern "
              "Peninsula (PRIPS). These landlocked territories, highly "
              "exposed to climate hazards, hold one of the country's last "
              "biodiversity hotspots and offer a diversity of ecosystems "
              "suited to integrated solutions for sustainable, resilient "
              "development. That the selected communes appear on the target "
              "list of the 2024 Humanitarian Response Plan testifies to the "
              "urgent needs of local communities. Rich in environmental "
              "services, these landscapes offer the opportunity to develop "
              "and scale up endogenous solutions fitted to local realities. "
              "The presence of several development and humanitarian partners "
              "active in the region is a further asset for mobilising "
              "complementary resources and expertise.",
        "fr": "Cette approche est pilotée par le PNUE dans deux territoires "
              "dits « paysages » de la région du Grand-Sud, désignés comme "
              "zones prioritaires dans le Plan de relèvement intégré de la "
              "péninsule sud (PRIPS). Ces territoires enclavés, très exposés "
              "aux aléas climatiques, abritent l'un des derniers points "
              "chauds de biodiversité du pays et offrent une diversité "
              "d'écosystèmes propice à des solutions intégrées pour un "
              "développement durable et résilient. La présence des communes "
              "sélectionnées sur la liste des zones cibles du Plan de réponse "
              "humanitaire 2024 témoigne des besoins urgents des communautés "
              "locales. Riches en services environnementaux, ces paysages "
              "offrent l'opportunité de développer et de mettre à l'échelle "
              "des solutions endogènes adaptées aux réalités locales. La "
              "présence de plusieurs partenaires de développement et "
              "humanitaires actifs dans la région constitue un atout majeur "
              "pour mobiliser des ressources et des expertises "
              "complémentaires."},
    # Les deux paysages : superficie, arrondissements, communes. Le format
    # « titre | surface | détail » est découpé au rendu.
    "ap_y_ga": {
        "en": "Grand'Anse landscape|767 km²|The arrondissement of Corail and "
              "four communes: Roseaux, Corail, Beaumont, Pestel (including "
              "the Cayemites islands).",
        "fr": "Paysage Grand'Anse|767 km²|L'arrondissement de Corail et "
              "quatre communes : Roseaux, Corail, Beaumont, Pestel (y compris "
              "les îles des Cayemites)."},
    "ap_y_sud": {
        "en": "Sud landscape|740 km²|Three arrondissements — Port-Salut, "
              "Coteaux, Chardonnières — and nine communes: Tiburon, "
              "Chardonnières, Les Anglais, Port-à-Piment, Les Coteaux, "
              "Roche-à-Bateaux, Arniquet, Port-Salut, Saint-Jean-du-Sud.",
        "fr": "Paysage Sud|740 km²|Trois arrondissements — Port-Salut, "
              "Coteaux, Chardonnières — et neuf communes : Tiburon, "
              "Chardonnières, Les Anglais, Port-à-Piment, Les Coteaux, "
              "Roche-à-Bateaux, Arniquet, Port-Salut, Saint-Jean-du-Sud."},

    "ap_k_t": {"en": "A capital-based approach to resilience",
               "fr": "Une approche de la résilience fondée sur les capitaux"},
    "ap_k_x": {
        "en": "APRI embodies this vision by adopting a definition of "
              "resilience built on seven dimensions. This multidimensional "
              "framework brings together the tangible and the intangible "
              "factors that shape how communities adapt and recover. Each "
              "dimension carries its own indicators, its own scales and its "
              "own weights, all of them set out in the Resilience Framework.",
        "fr": "APRI incarne cette vision en adoptant une définition de la "
              "résilience fondée sur sept dimensions. Ce cadre "
              "multidimensionnel intègre à la fois les facteurs tangibles et "
              "intangibles qui influencent l'adaptabilité et la capacité de "
              "récupération des communautés. Chaque dimension porte ses "
              "indicateurs, ses barèmes et ses pondérations, tous exposés "
              "dans le cadre de résilience."},

    "ap_pi_t": {"en": "Four pillars for effective implementation",
                "fr": "Quatre piliers pour une mise en œuvre efficace"},
    "ap_pi_x": {
        "en": "Implementing APRI rests on four strategic axes, at national "
              "and local level.",
        "fr": "La mise en œuvre d'APRI s'appuie sur quatre axes stratégiques, "
              "au niveau national et local."},
    "ap_pi_todo": {
        "en": "The four axes themselves are still to be filled in: they were "
              "not in the text this page was written from, and naming them "
              "wrongly would be worse than leaving the slot open.",
        "fr": "Les quatre axes eux-mêmes restent à renseigner : ils ne "
              "figuraient pas dans le texte d'où vient cette page, et les "
              "nommer de travers serait pire que de laisser la place vide."},

    "ap_r_t": {"en": "Milestones reached", "fr": "Réalisations"},
    "ap_r_x": {
        "en": "Since it began, APRI has already reached several milestones.",
        "fr": "Depuis son lancement, la mise en œuvre d'APRI a déjà atteint "
              "plusieurs jalons importants."},
    "ap_r_l": {
        "en": "An APRI steering committee has been set up, currently "
              "bringing together 16 members, of which 10 are UN agencies."
              "@@A baseline study has been carried out in 10 communal "
              "sections, providing the data needed to steer interventions."
              "@@An indicator matrix has been drawn up for an APRI "
              "monitoring framework; consultations with partners are under "
              "way for its finalisation and validation."
              "@@An innovative project has been approved to pilot payment "
              "for environmental services (PES) mechanisms, jointly with "
              "UNEP, WFP, ILO and The Nature Conservancy.",
        "fr": "Lancement d'un comité de pilotage APRI, qui rassemble "
              "actuellement 16 membres, dont 10 agences des Nations unies."
              "@@Réalisation d'une étude de ligne de base dans 10 sections "
              "communales, fournissant des données essentielles pour orienter "
              "les interventions."
              "@@Élaboration d'une matrice d'indicateurs pour l'établissement "
              "d'un cadre de suivi APRI ; les consultations avec les "
              "partenaires sont en cours pour sa finalisation et sa "
              "validation."
              "@@Approbation d'un projet novateur pour piloter des mécanismes "
              "de paiement pour services environnementaux (PSE), en "
              "collaboration entre le PNUE, le PAM, l'OIT et The Nature "
              "Conservancy."},

    "ap_o_t": {"en": "2025 objectives", "fr": "Objectifs 2025"},
    "ap_o_l": {
        "en": "Setting up an APRI information system."
              "@@Drawing up a harmonised methodology for community resilience "
              "planning."
              "@@Establishing multisectoral governance platforms in 10 pilot "
              "communal sections."
              "@@Drawing up 10 resilience plans, one for each pilot communal "
              "section."
              "@@Establishing an APRI operational committee in each landscape."
              "@@Extending the baseline study."
              "@@Launching an economic study on blue, green and circular "
              "potential in the landscapes.",
        "fr": "Mise en place d'un système d'information APRI."
              "@@Élaboration d'une méthodologie harmonisée pour une "
              "planification communautaire de la résilience."
              "@@Établissement de plateformes de gouvernance multisectorielles "
              "dans 10 sections communales pilotes."
              "@@Élaboration de 10 plans de résilience, un par section "
              "communale pilote."
              "@@Établissement d'un comité opérationnel APRI dans chaque "
              "paysage."
              "@@Expansion de l'étude de ligne de base."
              "@@Lancement d'une étude économique sur les potentialités "
              "bleues, vertes et circulaires dans les paysages."},
    "ap_t1": {"en": "What this index is",
              "fr": "Ce qu'est cet indice"},
    "ap_x1": {
        "en": "APRI turns what a landscape and its households can be observed "
              "doing into a score out of ten, on {i} indicators grouped in "
              "seven dimensions. It does not rank places for the sake of "
              "ranking them: a score is only useful next to the measurement "
              "it comes from, which is why every indicator on this site "
              "carries its raw value, its scale and its weight.",
        "fr": "APRI transforme ce qu'on peut observer d'un paysage et de ses "
              "ménages en un score sur dix, sur {i} indicateurs répartis en "
              "sept dimensions. Il ne classe pas des lieux pour le plaisir de "
              "les classer : un score ne vaut qu'à côté de la mesure dont il "
              "sort, et c'est pourquoi chaque indicateur du site porte sa "
              "valeur brute, son barème et sa pondération."},
    "ap_t2": {"en": "Where it comes from", "fr": "D'où il vient"},
    "ap_x2": {
        "en": "APRI is the measurement arm of the Integrated Resilient "
              "Landscape Approach (IRLA), a framework that reads a landscape "
              "as a system rather than as a list of sectors. IRLA sets the "
              "seven dimensions, the three attributes — anticipate, absorb, "
              "adapt — and the rule that a resilience score must be traceable "
              "back to a field measurement. APRI is what happens when that "
              "framework is applied to a real territory and has to produce "
              "numbers.",
        "fr": "APRI est le bras de mesure de l'approche intégrée des paysages "
              "résilients (IRLA), un cadre qui lit un paysage comme un "
              "système plutôt que comme une liste de secteurs. IRLA pose les "
              "sept dimensions, les trois attributs — anticiper, absorber, "
              "s'adapter — et la règle qu'un score de résilience doit pouvoir "
              "être remonté jusqu'à une mesure de terrain. APRI est ce que "
              "devient ce cadre quand on l'applique à un territoire réel et "
              "qu'il faut produire des chiffres."},
    "ap_t3": {"en": "The 2024 assessment", "fr": "L'évaluation de 2024"},
    "ap_x3": {
        "en": "The figures on this site come from a household survey carried "
              "out in 2024 across {s} communal sections of Sud and "
              "Grand'Anse, in Haiti: {m} households, {q} questions each. "
              "Three other sources complete it — structured interviews with "
              "communal health, education and political authorities, "
              "identity records for {o} community-based organisations, and "
              "satellite series on forest cover, rainfall and land surface "
              "temperature.",
        "fr": "Les chiffres de ce site viennent d'une enquête ménage conduite "
              "en 2024 dans {s} sections communales du Sud et de la "
              "Grand'Anse, en Haïti : {m} ménages, {q} questions chacun. "
              "Trois autres sources la complètent — des entretiens "
              "structurés avec les autorités sanitaires, éducatives et "
              "politiques communales, les fiches d'identité de {o} "
              "organisations communautaires de base, et des séries "
              "satellitaires sur le couvert forestier, la pluie et la "
              "température de surface."},
    "ap_t4": {"en": "What it does not claim", "fr": "Ce qu'il ne prétend pas"},
    "ap_x4": {
        "en": "A composite index carries a circularity it should say out "
              "loud: resilience is defined by the variables assumed to "
              "produce it. The causal links this site draws are posed by the "
              "framework and the literature, not estimated on the survey — "
              "and they are shown with their evidence and their source so "
              "that they can be argued with. Of the {i} indicators, some "
              "carry no measured value yet, and the site says so where the "
              "number is missing rather than filling the gap.",
        "fr": "Un indice composite porte une circularité qu'il vaut mieux "
              "dire tout haut : la résilience y est définie par les "
              "variables supposées la produire. Les liens causaux dessinés "
              "sur ce site sont posés par le cadre et la littérature, non "
              "estimés sur l'enquête — et ils sont montrés avec leur niveau "
              "de preuve et leur source, pour qu'on puisse les discuter. Sur "
              "les {i} indicateurs, certains ne portent pas encore de valeur "
              "mesurée, et le site le dit là où le nombre manque plutôt que "
              "de combler le trou."},
    "ap_t5": {"en": "Who is behind it", "fr": "Qui le porte"},
    "ap_x5": {
        "en": "The assessment is carried out by the United Nations "
              "Environment Programme (UNEP) with its field partners in Sud "
              "and Grand'Anse. The survey was administered on the ground by "
              "local enumerators; the framework, the index and this site are "
              "produced by the project team.",
        "fr": "L'évaluation est conduite par le Programme des Nations unies "
              "pour l'environnement (PNUE) avec ses partenaires de terrain "
              "du Sud et de la Grand'Anse. L'enquête a été administrée sur "
              "place par des enquêteurs locaux ; le cadre, l'indice et ce "
              "site sont produits par l'équipe du projet."},
    "ap_equipe": {"en": "The team", "fr": "L'équipe"},
    "ap_equipe_x": {
        "en": "Names and roles to be added.",
        "fr": "Noms et fonctions à compléter."},
    "ap_c_titre": {"en": "Contact us", "fr": "Nous contacter"},
    "ap_c_x": {
        "en": "For a question on the method, a figure you want to check, a "
              "correction, or a request for data that is not published here.",
        "fr": "Pour une question de méthode, un chiffre à vérifier, une "
              "correction, ou une demande de données qui ne sont pas "
              "publiées ici."},
    "ap_c_mail": {"en": "By email", "fr": "Par courriel"},
    "ap_c_qui": {"en": "Who answers", "fr": "Qui répond"},
    "ap_c_qui_x": {
        "en": "The UNEP project team in charge of the assessment.",
        "fr": "L'équipe du projet PNUE en charge de l'évaluation."},
    "ap_c_donnees": {"en": "Data requests", "fr": "Demandes de données"},
    "ap_c_donnees_x": {
        "en": "The seven published datasets are on the Data page, ready to "
              "download. The raw file with direct identifiers is never "
              "published: requests for it are handled case by case.",
        "fr": "Les sept jeux publiés sont sur la page Données, prêts à "
              "télécharger. Le fichier brut portant les identifiants directs "
              "n'est jamais publié : les demandes le concernant se traitent "
              "au cas par cas."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)

_STYLE = """
<style>
  /* UNE COLONNE DE TEXTE, PAS UNE GRILLE DE CARTES. Cette page se lit d'un
     bout à l'autre : elle raconte. Une mise en cartes découperait le récit
     en morceaux qu'on picore, ce qui est exactement ce qu'il ne faut pas
     faire d'une page qui explique d'où viennent les chiffres. */
  .ap-h { font-size:12px; font-weight:700; letter-spacing:.09em;
       text-transform:uppercase; color:#1f5b46; margin:26px 0 8px;
       display:flex; align-items:center; gap:12px; }
  .ap-h span { flex:1 1 auto; height:1.5px; background:#cfe0d6; }
  .ap-p { font-size:14.5px; line-height:1.65; color:#3c4761;
       max-width:82ch; margin:0; text-align:left !important; }
  .ap-b { display:flex; gap:14px; flex-wrap:wrap; margin:14px 0 0; }
  .ap-c { flex:1 1 260px; border:1px solid #e4eae6; border-radius:12px;
       background:#fff; padding:13px 16px; }
  .ap-c-t { font-size:11px; font-weight:700; letter-spacing:.07em;
       text-transform:uppercase; color:#1f5b46; margin-bottom:5px; }
  .ap-c-x { font-size:13.5px; line-height:1.55; color:#3c4761; }
  /* LES JALONS ET LES OBJECTIFS SE LISENT EN LISTE NUMÉROTÉE. Ce sont des
     éléments de même rang qu'on parcourt, pas un récit : le numéro donne le
     compte d'un coup d'œil, ce qu'un point ne fait pas. */
  .ap-l { list-style:none; padding:0; margin:12px 0 0; max-width:82ch; }
  .ap-l li { display:flex; gap:12px; align-items:flex-start;
       font-size:14px; line-height:1.6; color:#3c4761; padding:7px 0;
       border-top:1px solid #eef2ef; text-align:left; }
  .ap-l li:first-child { border-top:0; }
  .ap-l b { flex:0 0 auto; font-family:Georgia,"Times New Roman",serif;
       font-size:14px; font-weight:400; color:#7d9c8c; min-width:18px; }
  /* LES DEUX PAYSAGES, CÔTE À CÔTE : ils se comparent, donc ils se posent
     l'un à côté de l'autre plutôt que l'un sous l'autre. */
  .ap-pay { display:grid; grid-template-columns:1fr 1fr; gap:14px;
       margin:14px 0 0; }
  .ap-pay > div { border:1px solid #e4eae6; border-radius:12px;
       background:#f7faf8; padding:14px 16px; }
  .ap-pay .t { font-size:15px; font-weight:600; color:#101728;
       font-family:Georgia,"Times New Roman",serif; }
  .ap-pay .s { font-size:12px; font-weight:700; letter-spacing:.06em;
       color:#1f7a4d; margin:2px 0 7px; }
  .ap-pay .x { font-size:13px; line-height:1.55; color:#3c4761;
       text-align:left !important; }
  @media (max-width: 900px) { .ap-pay { grid-template-columns:1fr; } }
  /* CE QUI RESTE À COMPLÉTER LE DIT, en ambre, plutôt que de se faire passer
     pour du contenu. Un bloc vide qu'on oublie de remplir se publie ; un
     bloc qui se signale, non. */
  .ap-todo { font-size:13px; color:#a8690a; background:#fdf3e3;
       border:1px solid #f0dcb8; border-radius:10px; padding:9px 13px;
       margin:10px 0 0; }
</style>
"""


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


@st.cache_data(show_spinner=False)
def _chiffres():
    """Les cinq nombres de la page, comptés dans les fichiers du site."""
    def _j(nom):
        c = os.path.join(DATA, nom)
        if not os.path.exists(c):
            return None
        with open(c, encoding="utf-8") as f:
            return json.load(f)

    n = {}
    r = _j("resultats.json") or []
    n["i"] = len(r["indicateurs"] if isinstance(r, dict) else r)
    n["q"] = len(_j("questions_index.json") or [])
    n["o"] = len((_j("ocb.json") or {}).get("fiches") or [])
    try:
        with open(os.path.join(DATA, "donnees_anonymisees.csv"),
                  encoding="utf-8", errors="replace") as f:
            n["m"] = max(0, sum(1 for _ in csv.reader(f)) - 1)
    except Exception:
        n["m"] = None
    n["s"] = 10
    return n


def _nb(v):
    if v is None:
        return "—"
    return (f"{v:,}".replace(",", " ") if i18n.get_lang() == "fr"
            else f"{v:,}")


def _section(cle_t, cle_x, **kw):
    st.markdown(f'<div class="ap-h">{_e(T(cle_t))}<span></span></div>'
                f'<p class="ap-p">{_e(T(cle_x, **kw))}</p>',
                unsafe_allow_html=True)


def _liste(cle):
    """Une liste numérotée, écrite en une chaîne et coupée aux doubles arobases.

    UN SEUL LIBELLÉ POUR TOUTE LA LISTE. Sept clés pour sept objectifs
    auraient fait sept entrées de dictionnaire à tenir alignées entre deux
    langues ; une chaîne coupée garde la liste entière sous les yeux du
    traducteur, dans son ordre.
    """
    lignes = [x.strip() for x in T(cle).split("@@") if x.strip()]
    return ('<ul class="ap-l">' + "".join(
        f'<li><b>{i:02d}</b><span>{_e(x)}</span></li>'
        for i, x in enumerate(lignes, start=1)) + '</ul>')


def _paysages():
    """Les deux paysages pilotes, côte à côte : nom, superficie, communes."""
    cases = []
    for cle in ("ap_y_ga", "ap_y_sud"):
        parts = (T(cle).split("|") + ["", "", ""])[:3]
        nom, surface, detail = (p.strip() for p in parts)
        cases.append(f'<div><div class="t">{_e(nom)}</div>'
                     f'<div class="s">{_e(surface)}</div>'
                     f'<div class="x">{_e(detail)}</div></div>')
    return '<div class="ap-pay">' + "".join(cases) + '</div>'


def render():
    """La page « À propos » : l'initiative, ses paysages, puis l'indice.

    L'INITIATIVE PASSE DEVANT L'INSTRUMENT. La page ouvrait sur « ce qu'est
    cet indice » : elle décrivait un outil de mesure à qui ne savait pas
    encore ce qu'on mesurait, où, ni pour qui. APRI est d'abord un programme
    du PNUE sur deux paysages du Grand-Sud ; l'indice vient après, et il en
    est le bras de mesure.
    """
    st.markdown(_STYLE, unsafe_allow_html=True)
    n = _chiffres()
    _section("ap_q_t", "ap_q_x")
    _section("ap_p_t", "ap_p_x")
    _section("ap_y_t", "ap_y_x")
    st.markdown(_paysages(), unsafe_allow_html=True)
    _section("ap_k_t", "ap_k_x")
    _section("ap_pi_t", "ap_pi_x")
    st.markdown(f'<div class="ap-todo">{_e(T("ap_pi_todo"))}</div>',
                unsafe_allow_html=True)
    _section("ap_r_t", "ap_r_x")
    st.markdown(_liste("ap_r_l"), unsafe_allow_html=True)
    st.markdown(f'<div class="ap-h">{_e(T("ap_o_t"))}<span></span></div>',
                unsafe_allow_html=True)
    st.markdown(_liste("ap_o_l"), unsafe_allow_html=True)
    _section("ap_t1", "ap_x1", i=_nb(n["i"]))
    _section("ap_t2", "ap_x2")
    _section("ap_t3", "ap_x3", s=_nb(n["s"]), m=_nb(n["m"]), q=_nb(n["q"]),
             o=_nb(n["o"]))
    _section("ap_t4", "ap_x4", i=_nb(n["i"]))
    _section("ap_t5", "ap_x5")
    st.markdown(f'<div class="ap-b"><div class="ap-c">'
                f'<div class="ap-c-t">{_e(T("ap_equipe"))}</div>'
                f'<div class="ap-c-x ap-todo" style="margin:0">'
                f'{_e(T("ap_equipe_x"))}</div></div></div>',
                unsafe_allow_html=True)


def render_contact():
    """La page « Nous contacter » : à qui écrire, et pour quoi."""
    st.markdown(_STYLE, unsafe_allow_html=True)
    st.markdown(f'<p class="ap-p">{_e(T("ap_c_x"))}</p>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="ap-b">'
        f'<div class="ap-c"><div class="ap-c-t">{_e(T("ap_c_mail"))}</div>'
        f'<div class="ap-c-x"><a href="mailto:{COURRIEL}" '
        f'style="color:#1f5b46;font-weight:600;text-decoration:none">'
        f'{COURRIEL}</a></div></div>'
        f'<div class="ap-c"><div class="ap-c-t">{_e(T("ap_c_qui"))}</div>'
        f'<div class="ap-c-x">{_e(T("ap_c_qui_x"))}</div></div>'
        f'<div class="ap-c"><div class="ap-c-t">{_e(T("ap_c_donnees"))}</div>'
        f'<div class="ap-c-x">{_e(T("ap_c_donnees_x"))}</div></div>'
        '</div>', unsafe_allow_html=True)
