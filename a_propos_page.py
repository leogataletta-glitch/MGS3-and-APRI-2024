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

CE QU'ELLE DIT, ET CE QU'ELLE LAISSE AU CADRE.
Elle présente l'initiative : ce qu'est APRI, pourquoi elle existe, sur quels
paysages elle travaille, ce qu'elle a déjà fait et ce qu'elle vise. La
méthode de mesure — les sept dimensions, les barèmes, les pondérations, ce
que l'indice ne prétend pas — appartient au cadre de résilience, qui l'expose
onglet par onglet. Deux exposés de la même méthode divergent toujours.
"""

import streamlit as st

import i18n
from i18n import T

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

    # LES DEUX MOTS DU TITRE, DÉFINIS AVANT D'ÊTRE EMPLOYÉS. « Paysage » et
    # « résilience » sont pris ici dans une acception précise, empruntée, et
    # qui n'est pas celle du langage courant : un paysage n'est pas un point
    # de vue, la résilience n'est ni la stabilité ni l'inverse de la
    # vulnérabilité. Les définir en tête coûte deux encadrés et évite deux
    # malentendus qui portent sur tout le reste du site.
    "ap_d_t": {"en": "The two words, as they are used here",
               "fr": "Les deux mots, au sens où ils sont pris ici"},
    "ap_d_pay": {
        "en": "A landscape|Beyond a mosaic, or a group of local ecosystems "
              "repeating in a similar form, a landscape is a particular "
              "configuration of topography, vegetation, land use and "
              "settlement pattern which marks out a certain coherence of "
              "natural, historical and cultural processes and activities."
              "|After McNeely and Scherr (2003), p. 275",
        "fr": "Un paysage|Au-delà d'une mosaïque ou d'un groupe d'écosystèmes "
              "locaux qui se répète sous une forme similaire, il s'agit d'une "
              "configuration particulière de topographie, de végétation, "
              "d'utilisation des terres et de schéma d'implantation qui "
              "délimite une certaine cohérence des processus et activités "
              "naturels, historiques et culturels."
              "|D'après McNeely et Scherr (2003), p. 275"},
    "ap_d_res": {
        "en": "Resilience|A holistic concept, rooted in Holling's founding "
              "work of 1973, distinct from stability and from vulnerability, "
              "and one that includes social principles. It is to be "
              "understood as the ability of a system exposed to hazards to "
              "resist, absorb, adapt to and recover from the effects of a "
              "hazard in a timely and efficient manner, including through "
              "the preservation, restoration and improvement of its "
              "essential basic structures and functions."
              "|UNDRR, building on Holling (1973)",
        "fr": "La résilience|Un concept holistique, issu des travaux "
              "fondateurs de Holling (1973), distinct de la stabilité comme "
              "de la vulnérabilité, et qui inclut des principes sociaux. Il "
              "faut l'entendre comme la capacité d'un système exposé aux "
              "risques à résister aux effets d'un aléa, à les absorber, à "
              "s'y adapter et à s'en remettre de manière opportune et "
              "efficace, y compris par la préservation, la restauration et "
              "l'amélioration de ses structures et fonctions de base "
              "essentielles."
              "|UNDRR, sur les travaux de Holling (1973)"},
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

    "ap_r_t": {"en": "Milestones since the launch",
               "fr": "Réalisations depuis le lancement"},
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

    # CE SONT DES CHOSES FAITES, PAS DES CHOSES VOULUES. La liste était
    # intitulée « objectifs 2025 » et se lisait donc comme une promesse ;
    # elle porte des réalisations de 2025 et 2026.
    "ap_o_t": {"en": "Delivered in 2025 and 2026",
               "fr": "Réalisations 2025 et 2026"},
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
  /* LE TEXTE PREND LA LARGEUR DE LA PAGE. Il se coupait à quatre-vingt-deux
     signes, ce qui laissait la moitié droite de l'écran vide sur un grand
     moniteur et faisait paraître la page inachevée. Justifié, le bord droit
     referme le bloc au lieu de s'effilocher. */
  .ap-p { font-size:14.5px; line-height:1.65; color:#3c4761;
       max-width:none; margin:0; text-align:justify !important; }
  .ap-b { display:flex; gap:14px; flex-wrap:wrap; margin:14px 0 0; }
  .ap-c { flex:1 1 260px; border:1px solid #e4eae6; border-radius:12px;
       background:#fff; padding:13px 16px; }
  .ap-c-t { font-size:11px; font-weight:700; letter-spacing:.07em;
       text-transform:uppercase; color:#1f5b46; margin-bottom:5px; }
  .ap-c-x { font-size:13.5px; line-height:1.55; color:#3c4761; }
  /* LES JALONS ET LES OBJECTIFS SE LISENT EN LISTE NUMÉROTÉE. Ce sont des
     éléments de même rang qu'on parcourt, pas un récit : le numéro donne le
     compte d'un coup d'œil, ce qu'un point ne fait pas. */
  .ap-l { list-style:none; padding:0; margin:12px 0 0; max-width:none; }
  .ap-l li { display:flex; gap:12px; align-items:flex-start;
       font-size:14px; line-height:1.6; color:#3c4761; padding:7px 0;
       border-top:1px solid #eef2ef; text-align:left; }
  .ap-l li:first-child { border-top:0; }
  .ap-l b { flex:0 0 auto; font-family:Georgia,"Times New Roman",serif;
       font-size:14px; font-weight:400; color:#7d9c8c; min-width:18px; }
  /* LES DEUX DÉFINITIONS : un mot, sa définition, sa source. Le fond pâle et
     le filet vert à gauche disent qu'on cite plutôt qu'on affirme. */
  .ap-def { display:grid; grid-template-columns:1fr 1fr; gap:14px;
       margin:14px 0 0; }
  .ap-def > div { border-left:3px solid #9fc7b3; background:#f7faf8;
       border-radius:0 12px 12px 0; padding:12px 16px; }
  .ap-def .m { font-family:Georgia,"Times New Roman",serif; font-size:16px;
       color:#101728; margin-bottom:5px; }
  .ap-def .x { font-size:13.5px; line-height:1.6; color:#3c4761;
       text-align:left !important; }
  .ap-def .s { font-size:11.5px; color:#7d8c84; margin-top:8px;
       font-style:italic; }
  @media (max-width: 900px) { .ap-def { grid-template-columns:1fr; } }
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


def _definitions():
    """Les deux mots du titre, définis et attribués."""
    cases = []
    for cle in ("ap_d_pay", "ap_d_res"):
        parts = (T(cle).split("|") + ["", "", ""])[:3]
        mot, texte, source = (p.strip() for p in parts)
        cases.append(f'<div><div class="m">{_e(mot)}</div>'
                     f'<div class="x">{_e(texte)}</div>'
                     f'<div class="s">{_e(source)}</div></div>')
    return '<div class="ap-def">' + "".join(cases) + '</div>'


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
    _section("ap_q_t", "ap_q_x")
    st.markdown(f'<div class="ap-h">{_e(T("ap_d_t"))}<span></span></div>',
                unsafe_allow_html=True)
    st.markdown(_definitions(), unsafe_allow_html=True)
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
    # LES CINQ SECTIONS SUR L'INDICE ONT ÉTÉ RETIRÉES. Ce qu'est le score,
    # d'où vient le cadre, ce que l'enquête a couvert et ce que l'indice ne
    # prétend pas : tout cela est exposé en entier dans « Cadre de
    # résilience », onglet par onglet, avec les barèmes et les pondérations.
    # Le redire ici en cinq paragraphes faisait de la page « À propos » un
    # résumé de méthode plutôt que la présentation de l'initiative.


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
