"""Accueil — comprendre APRI en quatre écrans.

POURQUOI UN PARCOURS ET PAS UNE PAGE

Le site ouvrait sur le cadre méthodologique : avant d'apprendre quoi que ce
soit du territoire, on apprenait comment on le mesure. C'est l'ordre d'un
rapport, pas celui d'un tableau de bord. Cette page prend la première place et
pose les quatre questions dans l'ordre où on se les pose :

    Où ?  ›  Qu'a-t-on mesuré ?  ›  Qu'a-t-on trouvé ?  ›  Que faire ?

Un écran à la fois, avec un bouton pour avancer. Le pari est simple : quatre
petites pages qu'on parcourt valent mieux qu'une grande qu'on saute.

TOUS LES CHIFFRES SONT CALCULÉS. L'indice, l'amplitude entre sections, les
scores de dimension, les indicateurs les plus coûteux, l'effet du portefeuille
d'actions : rien n'est écrit en dur. Une page d'accueil qui annonce un chiffre
faux est pire qu'une page d'accueil absente, parce qu'on la croit.

L'AMPLITUDE EST CALCULÉE SUR UNE BASE COMMUNE, ET C'EST LA SEULE FAÇON HONNÊTE.
Comparer Trichet à Quentin sur les 66 indicateurs scorés serait injuste : deux
sections n'ont pas de valeur pour neuf d'entre eux, et leur indice porterait
alors sur un référentiel plus étroit. On ne retient donc, pour ce classement,
que les 57 indicateurs renseignés POUR LES DIX sections. L'indice global
publié, lui, reste celui du référentiel entier — les deux chiffres diffèrent,
et la page le dit plutôt que de les confondre.
"""

import json
import os

import streamlit as st

import i18n
import icones
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"
VERT, BLEU, AMBRE, ROUGE, GRIS = ("#1a8a4f", "#2166ac", "#d1730c",
                                  "#c33a24", "#8a93a5")

SECTIONS = ["Anse à Drick", "Barbois", "Dumont", "Débouchette", "Mouline",
            "Quentin", "Beaulieu", "Blactote", "Dalmette", "Trichet"]
DIM_CLE = {
    "I. PHYSICAL AND INFRASTRUCTURAL DIMENSION": "dim1",
    "II. INSTITUTIONAL, TECHNOLOGICAL, AND GOVERNANCE  DIMENSION": "dim2",
    "III.  ENVIRONMENTAL AND ECOLOGICAL DIMENSION": "dim3",
    "IV. ECONOMIC, LIVELIHOODS, AND FOOD SECURITY DIMENSION": "dim4",
    "V. SOCIAL AND COMMUNITY DIMENSION": "dim5",
    "VI. HUMAN DIMENSION": "dim6",
    "VII. CULTURAL, IDENTITY-BASED, AND PSYCHOLOGICAL DIMENSION": "dim7",
}
TEINTES = {"dim1": "#d1730c", "dim2": "#2166ac", "dim3": "#1a8a4f",
           "dim4": "#a02c8f", "dim5": "#0f8fa8", "dim6": "#c33a24",
           "dim7": "#7048b6"}

# DEUX ÉTAPES, PLUS QUATRE. « Les résultats clés » et « Les pistes d'action »
# ont été retirés du parcours d'accueil : leur contenu n'était pas au niveau du
# reste, et un écran à moitié fait sur la page d'entrée coûte plus cher en
# crédibilité qu'il ne rapporte en complétude. Les deux sujets restent traités
# en profondeur dans leurs propres rubriques — Analyse des résultats et Fiches
# d'intervention — qui sont dans le menu. Les listes commandent tout : la
# rangée d'onglets, la borne du bouton Suivant et le sommaire des écrans.
ETAPES = ("po_e1", "po_e2")

TEXTES = {
    "mode_portail": {"en": "Home", "fr": "Accueil"},
    "po_titre": {"en": "Landscape resilience observatory",
                 "fr": "Observatoire de la résilience des paysages"},
    "po_sous": {"en": "Sud and Grand'Anse, Haiti · survey 2024",
                "fr": "Sud et Grand'Anse, Haïti · enquête 2024"},
    # LES QUATRE ÉTAPES SE NOMMENT, ET LA QUESTION PASSE EN DESSOUS.
    # « Où ? » et « Qu'a-t-on mesuré ? » disaient l'intention sans dire le
    # contenu. Le nom vient donc en tête — le territoire, la méthodologie —
    # et la question reste en sous-titre, où elle garde son rôle : rappeler à
    # quoi cette étape répond. Les quatre sont construites pareil, sans quoi
    # la rangée aurait mélangé deux noms et deux questions.
    "po_e1": {"en": "The study area", "fr": "Le territoire d'étude"},
    "po_e2": {"en": "Methodology", "fr": "La méthodologie"},
    "po_e3": {"en": "Key results", "fr": "Les résultats clés"},
    "po_e4": {"en": "Action pathways", "fr": "Les pistes d'action"},
    # LE SOUS-TITRE DE CHAQUE ÉTAPE. La question dit ce qu'on cherche, le
    # sous-titre dit ce qu'on va voir : « Où ? » seul laisse le lecteur
    # deviner s'il aura une carte, une liste ou un tableau.
    "po_s3": {"en": "What was found?", "fr": "Qu'a-t-on trouvé ?"},
    "po_s4": {"en": "What can be done?", "fr": "Que faire ?"},

    # les trois faits de l'écran 1, en puces plutôt qu'en tuiles chiffrées
    "po_1_b1": {"en": "Two pilot areas: Grand'Anse and Sud",
                "fr": "Deux zones pilotes : Grand'Anse et Sud"},
    "po_1_b2": {"en": "{n} communal sections selected within them",
                "fr": "{n} sections communales sélectionnées en leur sein"},
    "po_1_b3": {"en": "{n} households surveyed",
                "fr": "{n} ménages enquêtés"},

    "po_1_sections": {"en": "The ten communal sections",
                      "fr": "Les dix sections communales"},
    "po_1_sections_x": {
        "en": "The figure beside each name is the number of households "
              "surveyed there.",
        "fr": "Le chiffre en regard de chaque nom est le nombre de ménages "
              "qui y ont été enquêtés."},

    "po_suivant": {"en": "Next", "fr": "Suivant"},
    "po_precedent": {"en": "Back", "fr": "Précédent"},
    "po_etape": {"en": "Step {n} of 4", "fr": "Étape {n} sur 4"},

    # ---------------- écran 1
    "po_1_t": {"en": "Ten communal sections in Haiti's Greater South",
               "fr": "Dix sections communales dans le Grand Sud d'Haïti"},
    "po_1_x": {
        "en": "A mountain landscape and a coastal one, across two "
              "departments. Households were drawn at random within strata, "
              "from a georeferenced building base, so that areas without a "
              "reliable administrative register are covered too.",
        "fr": "Un paysage de montagne et un paysage littoral, sur deux "
              "départements. Les ménages ont été tirés au sort dans des "
              "strates, à partir d'une base de bâtiments géoréférencés, pour "
              "que les zones sans registre administratif fiable soient "
              "couvertes aussi."},
    "po_1_c1": {"en": "households surveyed", "fr": "ménages enquêtés"},
    "po_1_c2": {"en": "communal sections", "fr": "sections communales"},
    "po_1_c3": {"en": "departments", "fr": "départements"},
    "po_1_c3x": {"en": "Sud and Grand'Anse", "fr": "Sud et Grand'Anse"},
    "po_1_carte": {"en": "The surveyed area, in the far south-west of the "
                         "country.",
                   "fr": "La zone enquêtée, à l'extrême sud-ouest du pays."},

    # ---------------- écran 2
    "po_2_t": {"en": "Resilience, in one number between 0 and 10",
               "fr": "La résilience, en un nombre entre 0 et 10"},
    "po_2_x": {
        "en": "APRI reads a territory as a system: its capacity to "
              "anticipate, absorb and adapt, measured **before** a shock "
              "rather than after it. It is not a damage report and not a "
              "forecast.",
        "fr": "APRI lit un territoire comme un système : sa capacité à "
              "anticiper, absorber et s'adapter, mesurée **avant** le choc et "
              "non après. Ce n'est ni un relevé de dégâts ni une prévision."},
    "po_2_a1": {"en": "Anticipate", "fr": "Anticiper"},
    "po_2_a1x": {"en": "see it coming and prepare",
                 "fr": "le voir venir et s'y préparer"},
    "po_2_a2": {"en": "Absorb", "fr": "Absorber"},
    "po_2_a2x": {"en": "take the hit without breaking",
                 "fr": "encaisser sans se rompre"},
    "po_2_a3": {"en": "Adapt", "fr": "S'adapter"},
    "po_2_a3x": {"en": "change rather than go back",
                 "fr": "changer plutôt que revenir en arrière"},
    "po_2_f1": {"en": "attributes", "fr": "attributs"},
    "po_2_f2": {"en": "dimensions", "fr": "dimensions"},
    "po_2_f3": {"en": "indicators", "fr": "indicateurs"},
    "po_2_f3x": {"en": "{f} scored to date", "fr": "{f} scorés à ce jour"},
    "po_2_f4": {"en": "one score", "fr": "un score"},
    "po_2_src": {"en": "Three sources, because one would leave a blind spot",
                 "fr": "Trois sources, parce qu'une seule laisserait un angle mort"},
    "po_2_s1": {"en": "Household survey", "fr": "Enquête ménage"},
    "po_2_s1x": {"en": "what families live through",
                 "fr": "ce que vivent les familles"},
    "po_2_s2": {"en": "Satellite imagery", "fr": "Imagerie satellitaire"},
    "po_2_s2x": {"en": "what no questionnaire sees",
                 "fr": "ce qu'aucun questionnaire ne voit"},
    "po_2_s3": {"en": "Community assessment", "fr": "Évaluation communautaire"},
    "po_2_s3x": {"en": "what holds the territory together",
                 "fr": "ce qui tient le territoire"},

    # ---------------- écran 3
    "po_3_t": {"en": "4.54 out of 10, and what that hides",
               "fr": "4,54 sur 10, et ce que cela cache"},
    "po_3_idx": {"en": "Overall index", "fr": "Indice global"},
    "po_3_idx_x": {"en": "weighted mean of the {n} scored indicators",
                   "fr": "moyenne pondérée des {n} indicateurs scorés"},
    "po_3_amp_t": {"en": "One average, ten very different places",
                   "fr": "Une moyenne, dix situations très différentes"},
    "po_3_amp": {
        "en": "Between the best-placed section and the least well placed, "
              "**{d} points of spread**, a third of the distance already "
              "covered. An average alone would have hidden it.",
        "fr": "Entre la section la mieux placée et la moins bien placée, "
              "**{d} points d'écart**, soit le tiers du chemin déjà parcouru. "
              "La moyenne seule l'aurait masqué."},
    "po_3_haut": {"en": "Best placed", "fr": "La mieux placée"},
    "po_3_bas": {"en": "Least well placed", "fr": "La moins bien placée"},
    "po_3_base": {
        "en": "Sections are compared on the {n} indicators available for all "
              "ten of them, and not on the full framework, which two sections "
              "do not cover entirely. This is why these figures differ "
              "slightly from the published index.",
        "fr": "Les sections sont comparées sur les {n} indicateurs "
              "disponibles pour les dix, et non sur le référentiel entier, "
              "que deux sections ne couvrent pas complètement. C'est pourquoi "
              "ces chiffres diffèrent un peu de l'indice publié."},
    "po_3_rep_t": {"en": "4.54 is not a middling territory, it is a "
                         "territory of extremes",
                   "fr": "4,54 n'est pas un territoire moyen, c'est un "
                         "territoire d'extrêmes"},
    "po_3_rep": {
        "en": "Spread the {n} scored indicators across the scale and the "
              "average dissolves: **{bas} % of the framework's weight sits at "
              "2 out of 10 or below**, while {haut} % sits at 9 or 10. Almost "
              "nothing is in the middle. An average of 4.54 describes no "
              "single indicator : it is the resultant of two opposite blocks, "
              "and that is what makes it actionable, since the low block is a "
              "list of things to build.",
        "fr": "Étalez les {n} indicateurs scorés sur l'échelle et la moyenne "
              "se dissout : **{bas} % du poids du référentiel est à 2 sur 10 "
              "ou moins**, quand {haut} % est à 9 ou 10. Presque rien n'est "
              "au milieu. Une moyenne de 4,54 ne décrit aucun indicateur : "
              "c'est la résultante de deux blocs opposés, et c'est ce qui la "
              "rend utile, puisque le bloc du bas est une liste de choses à "
              "construire."},
    "po_3_rep_ax": {"en": "share of the framework's weight",
                    "fr": "part du poids du référentiel"},
    "po_3_pay_t": {"en": "And two landscapes that do not hold up alike",
                   "fr": "Et deux paysages qui ne tiennent pas pareil"},
    "po_3_littoral": {"en": "Coastal", "fr": "Littoral"},
    "po_3_montagne": {"en": "Mountain", "fr": "Montagne"},
    "po_3_dims": {"en": "Where it holds, and where it does not",
                  "fr": "Où ça tient, et où ça ne tient pas"},
    "po_3_faits": {"en": "Three findings that carry the most weight",
                   "fr": "Trois constats qui pèsent le plus lourd"},
    "po_3_dim7": {
        "en": "The seventh dimension, cultural and psychological, has no "
              "computed indicator yet. It is shown at zero coverage rather "
              "than hidden.",
        "fr": "La septième dimension, culturelle et psychologique, n'a encore "
              "aucun indicateur calculé. Elle est montrée à couverture nulle "
              "plutôt que masquée."},
    "po_4_t": {"en": "Eight sheets, and what they would move",
               "fr": "Huit fiches, et ce qu'elles déplaceraient"},
    "po_4_x": {
        "en": "Each sheet acts on one lever of the causal model. Simulated "
              "together, the eight move the index from {a} to {b}. It is a "
              "modelled effect, not a promise, but it ranks what to do first.",
        "fr": "Chaque fiche agit sur un levier du modèle causal. Simulées "
              "ensemble, les huit portent l'indice de {a} à {b}. C'est un "
              "effet modélisé, pas une promesse, mais il dit par quoi "
              "commencer."},
    "po_4_gain": {"en": "Modelled gain", "fr": "Gain modélisé"},
    "po_4_lot": {
        "en": "**{n} of the {t} sheets carry {p} % of that gain**, the ones "
              "that are both feasible and short-term. If the decision is "
              "about sequencing rather than scope, this is the sentence to "
              "keep.",
        "fr": "**{n} des {t} fiches portent {p} % de ce gain**, celles qui "
              "sont à la fois faisables et à court terme. Si la décision "
              "porte sur un séquencement plutôt qu'un périmètre, c'est la "
              "phrase à retenir."},
    "po_4_portes": {"en": "Where to go from here", "fr": "Par où continuer"},
    "po_4_p1": {"en": "The donor briefing: findings and responses in full",
                "fr": "La note aux bailleurs : constats et réponses en entier"},
    "po_4_p2": {"en": "Intervention profiles: one sheet per lever",
                "fr": "Les fiches d'intervention : une fiche par levier"},
    "po_4_p3": {"en": "Results analysis, dimension by dimension",
                "fr": "L'analyse des résultats, dimension par dimension"},
    "po_4_p4": {"en": "The territory, where all this takes place",
                "fr": "Le territoire, où tout cela se passe"},
    # CHAQUE ÉCRAN A SA PORTE, PAS SEULEMENT LE DERNIER. Un parcours qui ne
    # donne la main qu'à la fin oblige à traverser les quatre écrans pour
    # arriver à la carte, alors que l'écran qui parle du territoire est
    # justement celui d'où l'on veut y aller.
    "po_porte_1": {"en": "Open the interactive map of the territory",
                   "fr": "Ouvrir la carte interactive du territoire"},
    "po_porte_2": {"en": "The resilience framework in detail",
                   "fr": "Le cadre de résilience en détail"},
    "po_porte_3": {"en": "The results, dimension by dimension",
                   "fr": "Les résultats, dimension par dimension"},
    "po_absent": {"en": "Result files missing.",
                  "fr": "Les fichiers de résultats sont absents."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)

STYLE = """
<style>
  /* ------------------------------------------------ l'écran « Où ? »
     LES PUCES SONT DE PETITS CARRÉS, PAS DES DISQUES. Un disque se confond
     avec les pastilles numérotées des étapes, juste au-dessus ; le carré s'en
     distingue et ne prétend pas être cliquable. */
  .po-puces { list-style:none; margin:6px 0 0; padding:0; max-width:46ch; }
  .po-puces li { position:relative; padding:0 0 0 20px; margin:0 0 20px;
                 font-size:14.5px; line-height:1.55; color:#2b3444; }
  .po-puces li::before { content:""; position:absolute; left:0; top:.52em;
                         width:6px; height:6px; background:#4a8b68;
                         border-radius:1px; }

  /* la carte, encadrée comme une planche, avec sa légende dessous */
  /* LES DIX SECTIONS, EN DEUX COLONNES DE DÉPARTEMENT.
     Une seule liste de dix lignes aurait allongé la colonne sans la remplir ;
     groupées par département, elles tiennent en deux blocs côte à côte et
     disent au passage comment l'échantillon se répartit entre Grand'Anse et
     Sud. */
  .po-lab   { font-size:10.5px; letter-spacing:.1em; text-transform:uppercase;
              color:#8a93a5; font-weight:700; margin:26px 0 11px; }
  .po-deps  { display:flex; flex-direction:column; gap:18px; }
  .po-dep-large ul { columns:2; column-gap:30px; }
  .po-dep-large li { break-inside:avoid; }
  .po-dep .dt .dn { font-weight:700; color:#a7b0bb; font-size:11.5px;
                    margin-left:5px; }
  .po-dep .dt { font-size:12.5px; font-weight:700; color:#2f6b4f;
                padding-bottom:6px; margin-bottom:5px;
                border-bottom:1px solid #e8edf3; }
  .po-dep ul { list-style:none; margin:0; padding:0; }
  .po-dep li { display:flex; align-items:baseline; gap:8px;
               font-size:13.5px; color:#2b3444; padding:3px 0; }
  .po-dep li .nm { flex:1; }
  .po-dep li .nb { font-variant-numeric:tabular-nums; font-weight:700;
                   color:#6b7a88; font-size:12.5px; }
  .po-note  { font-size:12px; color:#8a93a5; margin:13px 0 0; line-height:1.5; }

  /* LA CARTE N'EST PLUS ENCADRÉE. Un liseré et un fond gris autour d'une
     image qui a déjà ses propres contours ne délimitaient rien : ils
     ajoutaient une boîte de plus à une page qui en comptait trop. */
  .po-carte-cadre { padding:2px 0 0; }
  .po-carte-leg   { font-size:12.5px; color:#6b7a88; margin:9px 2px 0;
                    line-height:1.5; }

  .po-pas  { display:flex; gap:0; align-items:stretch; margin:16px 0 6px;
             border-bottom:1px solid #e6ecf4; }
  .po-p    { flex:1 1 0; padding:9px 4px 11px; text-align:center;
             font-size:12px; font-weight:600; color:#a7b0be;
             border-bottom:3px solid transparent; }
  .po-p b  { display:block; font-size:11px; letter-spacing:.09em;
             text-transform:uppercase; font-weight:700; margin-bottom:2px; }
  .po-p.on { color:#101728; border-bottom-color:#1c6349; }
  .po-p.vu { color:#3c4761; }
  .po-h    { font-size:20px; font-weight:700; color:#101728;
             letter-spacing:-.02em; margin:14px 0 6px; line-height:1.2; }
  .po-x    { font-size:14.5px; color:#3c4761; line-height:1.65; margin:0;
             max-width:82ch; }
  .po-g    { display:flex; gap:14px; flex-wrap:wrap; margin-top:16px; }
  .po-c    { flex:1 1 200px; min-width:180px; background:#fff;
             border:1px solid #e3eaf3; border-radius:14px; padding:16px 18px;
             box-shadow:0 1px 2px rgba(16,23,40,.05); }
  .po-n    { font-size:27px; font-weight:700; color:#101728; line-height:1;
             letter-spacing:-.03em; font-variant-numeric:tabular-nums; }
  .po-l    { font-size:12.5px; font-weight:600; color:#3c4761; margin-top:6px;
             text-align:left !important; }
  .po-s    { font-size:11px; color:#8a93a5; margin-top:2px;
             text-align:left !important; }
  .po-i    { width:34px; height:34px; border-radius:10px; display:flex;
             align-items:center; justify-content:center; margin-bottom:10px; }
  /* ÉCRAN 2 : DES FILETS, PAS DES BOÎTES. Deux rangées de grandes cartes se
     faisaient concurrence, et les titres en 27 px écrasaient tout le reste.
     Ici, une seule surface, des colonnes séparées par un filet, et une taille
     de texte qui laisse le chiffre être le seul élément saillant. */
  .e2-att  { display:grid; grid-template-columns:repeat(3,1fr); margin-top:18px;
             border-top:1px solid #e6ecf4; border-bottom:1px solid #e6ecf4; }
  .e2-a    { padding:14px 20px 15px; border-left:1px solid #e6ecf4; }
  .e2-a:first-child { border-left:none; padding-left:0; }
  .e2-a b  { display:block; font-size:14px; font-weight:700; color:#101728;
             letter-spacing:-.01em; }
  .e2-a span { display:block; font-size:12.5px; color:#6b7590; margin-top:3px;
               line-height:1.5; }
  .e2-ch   { display:flex; flex-wrap:wrap; align-items:baseline; gap:0 10px;
             margin:16px 0 2px; font-size:13px; color:#6b7590; }
  .e2-ch i { font-style:normal; color:#c8d0dc; }
  .e2-ch b { font-size:15.5px; font-weight:700; color:#101728;
             font-variant-numeric:tabular-nums; margin-right:4px; }
  .e2-ch em{ font-style:normal; font-size:11.5px; color:#8a93a5; }
  .e2-src  { margin-top:6px; }
  .e2-s    { display:grid; grid-template-columns:230px 1fr; gap:14px;
             padding:11px 0; border-top:1px solid #eef2f7; font-size:13px; }
  .e2-s:first-child { border-top:none; }
  .e2-s b  { font-weight:700; color:#101728; }
  .e2-s span { color:#6b7590; line-height:1.5; }
  @media (max-width:760px){ .e2-att{grid-template-columns:1fr}
    .e2-a{border-left:none;border-top:1px solid #e6ecf4;padding-left:0}
    .e2-a:first-child{border-top:none}
    .e2-s{grid-template-columns:1fr;gap:2px} }
  .po-flux { display:flex; align-items:stretch; gap:4px; flex-wrap:wrap;
             margin-top:14px; }
  .po-f    { flex:1 1 140px; min-width:125px; text-align:center;
             padding:14px 10px; border:1px solid #e3eaf3; border-radius:13px;
             background:#fff; }
  .po-f .po-n { font-size:21.5px; }
  .po-f .po-l, .po-f .po-s { text-align:center !important; }
  .po-ch   { align-self:center; color:#c3ccda; font-size:16px; flex:0 0 auto; }
  .po-j    { height:16px; background:#eef2f7; border-radius:8px;
             position:relative; margin:10px 0 4px; overflow:hidden; }
  .po-jr   { position:absolute; left:0; top:0; height:100%; border-radius:8px; }
  .po-bar  { display:grid; grid-template-columns:minmax(150px,2.2fr) 4fr 54px;
             gap:11px; align-items:center; padding:7px 0;
             border-bottom:1px solid #f0f4f9; }
  .po-bp   { height:13px; background:#f1f4f9; border-radius:5px; }
  .po-bf   { height:100%; border-radius:5px; }
  .po-nom  { font-size:12.5px; font-weight:600; color:#101728;
             text-align:left !important; }
  .po-val  { font-size:12.5px; font-weight:700; text-align:right;
             font-variant-numeric:tabular-nums; }
  .po-duel { display:grid; grid-template-columns:1fr auto 1fr; gap:16px;
             align-items:center; }
  .po-lab  { font-size:11px; letter-spacing:.09em; text-transform:uppercase;
             font-weight:700; color:#8a93a5; margin:22px 0 6px; }
  /* Trois chiffres à côté d'une carte : à 200 px de base ils passaient en
     deux lignes, dont une seule carte esseulée. */
  .po-serre .po-c { flex:1 1 140px; min-width:130px; padding:14px 15px; }
  .po-serre .po-n { font-size:21.5px; }

  /* LA SORTIE LATÉRALE PORTE LE MÊME HABIT QUE LES ÉTAPES. C'était le
     dernier pavé encadré de la page ; il devient un lien souligné, qui ne
     se colore qu'au survol. */
  div[class*="st-key-po_porte_"] button {
    background:transparent !important; border:none !important;
    border-bottom:1px solid #e6ecf4 !important; border-radius:0 !important;
    box-shadow:none !important; transform:none !important;
    padding:9px 2px 10px !important; min-height:0 !important;
    justify-content:flex-start !important;
    transition:border-color .15s ease; }
  div[class*="st-key-po_porte_"] button > div {
    justify-self:start !important; width:auto !important; }
  div[class*="st-key-po_porte_"] button p {
    font-size:14px !important; font-weight:600 !important;
    color:#3c4761 !important; margin:0 !important;
    text-align:left !important; transition:color .15s ease; }
  div[class*="st-key-po_porte_"] button:hover,
  div[class*="st-key-po_porte_"] button:focus {
    background:transparent !important;
    border-bottom:3px solid #2f6b4f !important; }
  div[class*="st-key-po_porte_"] button:hover p,
  div[class*="st-key-po_porte_"] button:focus p {
    color:#2f6b4f !important; font-weight:700 !important; }
</style>
"""


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _gras(t):
    out, morceaux = [], _e(t).split("**")
    for i, m in enumerate(morceaux):
        out.append(f"<b>{m}</b>" if i % 2 else m)
    return "".join(out)


def _f(v, dec=2, signe=False):
    if v is None:
        return "—"
    s = f"{v:+.{dec}f}" if signe else f"{v:.{dec}f}"
    return s.replace(".", ",") if i18n.get_lang() == "fr" else s


def _trouver(nom):
    for c in (os.path.join(DATA, nom), os.path.join(APP_DIR, nom)):
        if os.path.exists(c):
            return c
    return None


@st.cache_data(show_spinner=False)
def _mesures(lang):
    """Tout ce que la page affiche de chiffré, en une lecture.

    `lang` n'est pas décoratif : les noms d'indicateurs changent avec la
    langue, et sans lui le cache figerait la première langue affichée.
    """
    p = _trouver("resultats.json")
    if not p:
        return None
    with open(p, encoding="utf-8") as f:
        res = json.load(f)
    res = res["indicateurs"] if isinstance(res, dict) and "indicateurs" in res \
        else res
    scores = [r for r in res
              if (r.get("scores_corriges") or {}).get("Total") is not None]

    def moyenne(cle, lst):
        n = d = 0.0
        for r in lst:
            v = (r.get("scores_corriges") or {}).get(cle)
            if v is None:
                continue
            p_ = r.get("ponderation") or 1
            n += p_ * float(v)
            d += p_
        return (n / d) if d else None

    # base commune : les indicateurs renseignés POUR LES DIX sections
    commun = [r for r in scores
              if all((r.get("scores_corriges") or {}).get(s) is not None
                     for s in SECTIONS)]
    par_section = {s: moyenne(s, commun) for s in SECTIONS}
    ordre = sorted(par_section.items(), key=lambda kv: -(kv[1] or 0))

    # dimensions : score pondéré et poids, sur tout le référentiel
    dims = {}
    for r in res:
        cle = DIM_CLE.get(r.get("dimension") or "")
        if not cle:
            continue
        e = dims.setdefault(cle, {"num": 0.0, "den": 0.0, "n": 0, "faits": 0})
        e["n"] += 1
        v = (r.get("scores_corriges") or {}).get("Total")
        if v is not None:
            e["faits"] += 1
            p_ = r.get("ponderation") or 1
            e["num"] += p_ * float(v)
            e["den"] += p_
    for e in dims.values():
        e["score"] = (e["num"] / e["den"]) if e["den"] else None

    # les trois indicateurs qui coûtent le plus à l'indice
    def nom(r):
        if lang == "fr" and r.get("indicateur_fr"):
            return r["indicateur_fr"]
        return r.get("indicateur", "")

    couteux = sorted(
        scores,
        key=lambda r: -((r.get("ponderation") or 1)
                        * (10 - float(r["scores_corriges"]["Total"]))))[:3]
    faits = [{"nom": nom(r),
              "score": float(r["scores_corriges"]["Total"]),
              "valeur": (r.get("valeurs") or {}).get("Total"),
              "unite": (r.get("unite") or "").strip()
                       or ("%" if "%" in (r.get("metrique") or "") else ""),
              "dim": DIM_CLE.get(r.get("dimension") or "")}
             for r in couteux]

    # LA DISTRIBUTION SUR L'ÉCHELLE, EN PART DE POIDS ET NON EN NOMBRE.
    # Compter les indicateurs traiterait un indicateur pesant 4,6 comme un
    # indicateur pesant 1 ; c'est le poids qui fait la moyenne, c'est donc le
    # poids qu'il faut étaler.
    poids_total = sum((r.get("ponderation") or 1) for r in scores) or 1
    bandes = []
    for a_, b_, lab in ((0, 2, "0–2"), (3, 4, "3–4"), (5, 6, "5–6"),
                        (7, 8, "7–8"), (9, 10, "9–10")):
        g = [r for r in scores
             if a_ <= float(r["scores_corriges"]["Total"]) <= b_]
        bandes.append({"lab": lab, "n": len(g),
                       "part": sum((r.get("ponderation") or 1)
                                   for r in g) / poids_total * 100,
                       "milieu": (a_ + b_) / 2})

    paysages = {p_: moyenne(p_, scores) for p_ in ("Littoral", "Montagne")}

    bases = [int((r.get("n") or {}).get("Total") or 0) for r in scores]
    bases = [b for b in bases if b]
    p_idx = _trouver("croisement_index.json")
    menages = None
    if p_idx:
        try:
            with open(p_idx, encoding="utf-8") as f:
                menages = int(json.load(f).get("n") or 0)
        except Exception:
            menages = None
    if not menages and bases:
        menages = max(set(bases), key=bases.count)

    # L'EFFECTIF PAR SECTION SE PREND AU MODE, PAS AU MAXIMUM.
    # Chaque indicateur porte son propre effectif : certains ne concernent
    # qu'une partie des ménages — les enfants scolarisés, les parcelles
    # cultivées. Le maximum surestimerait donc l'échantillon ; la valeur la
    # plus fréquente est celle de la question posée à tout le monde, et les
    # modes des dix sections se somment bien au total de l'enquête.
    from collections import Counter
    sections_n = {}
    for sec in SECTIONS:
        vals = [(e.get("n") or {}).get(sec) for e in res]
        vals = [v for v in vals if v]
        if vals:
            sections_n[sec] = Counter(vals).most_common(1)[0][0]

    return {"sections_n": sections_n,
            "indice": moyenne("Total", scores), "n_scores": len(scores),
            "n_commun": len(commun), "sections": ordre, "dims": dims,
            "faits": faits, "menages": menages, "bandes": bandes,
            "paysages": paysages}


@st.cache_data(show_spinner=False)
def _actions():
    """L'effet du portefeuille, emprunté au moteur des fiches d'intervention.

    Importé ici et pas en tête de module : si le graphe causal manque, la page
    d'accueil doit continuer de s'afficher sans lui.
    """
    try:
        import note_bailleurs
        t = note_bailleurs._tout()
        if not t:
            return None
        return {"delta": t["portefeuille"]["delta"],
                "n": len(t["fiches"]),
                "lot1": len(t["lot1"]["ids"]),
                "part_lot1": (t["lot1"]["eff"]["delta"] / t["portefeuille"]["delta"]
                              * 100) if t["portefeuille"]["delta"] else 0}
    except Exception:
        return None


def _icone(nom, couleur):
    return (f'<div class="po-i" style="background:{couleur}17;color:{couleur}">'
            + icones.svg(nom, couleur=couleur, taille=19) + '</div>')


def _carte(icone, couleur, valeur, libelle, sous=""):
    return ('<div class="po-c">' + _icone(icone, couleur)
            + f'<div class="po-n">{_e(valeur)}</div>'
            + f'<div class="po-l">{_e(libelle)}</div>'
            + (f'<div class="po-s">{_e(sous)}</div>' if sous else "")
            + '</div>')


def _aller(mode):
    st.session_state["app_mode"] = mode


def _porte(cle, mode):
    """Un seul bouton, à gauche, qui mène à la rubrique correspondante.

    Il n'occupe pas toute la largeur : un bouton pleine largeur se lit comme
    l'action principale de l'écran, or l'action principale reste d'avancer
    dans le parcours. Celui-ci est une sortie latérale, il en a la taille.
    """
    g, _ = st.columns([1.7, 2.3])
    with g:
        st.button(T(cle) + "  →", key=f"po_porte_{mode}_{cle}",
                  on_click=_aller, args=(mode,), use_container_width=True)


def _bouger(delta):
    st.session_state["portail_etape"] = max(
        1, min(len(ETAPES),
               st.session_state.get("portail_etape", 1) + delta))


def _poser(n):
    st.session_state["portail_etape"] = n


# --------------------------------------------------------------- les écrans
def _ecran_1(m):
    """Où : le territoire, ses trois faits, ses dix sections et la carte.

    L'ÉCRAN ÉTAIT AUX DEUX TIERS VIDE. Trois puces à gauche, une petite carte
    en bas à droite, et entre les deux une hauteur de blanc que rien
    n'occupait. Le remède n'est pas d'étirer ce qu'il y avait : c'est de dire
    ce qui manquait. Les dix sections sont nommées, groupées par département,
    avec le nombre de ménages enquêtés dans chacune — l'information la plus
    demandée après « où », et celle qu'on allait chercher trois pages plus
    loin. La carte remonte en haut de sa colonne et grandit d'autant.
    """
    # LE TITRE DE L'ÉCRAN N'EST PLUS ÉCRIT ICI. Il est déjà dans la carte
    # d'étape sélectionnée, à deux centimètres au-dessus : le répéter en serif
    # faisait lire deux fois le même mot avant d'arriver au contenu.
    g, d = st.columns([1.08, 1], gap="large")
    with g:
        men = f'{m["menages"]:,}'.replace(",", " ") if m["menages"] else "—"
        st.markdown(
            '<ul class="po-puces">'
            f'<li>{_e(T("po_1_b1"))}</li>'
            f'<li>{_e(T("po_1_b2", n=len(SECTIONS)))}</li>'
            f'<li>{_e(T("po_1_b3", n=men))}</li>'
            '</ul>', unsafe_allow_html=True)
        _sections_par_departement(m)

    with d:
        try:
            import territoire_page
            v = territoire_page._vignette(territoire_page._geo(), 520, 400,
                                          mer="#f4f8fc")
        except Exception:
            v = None
        if v:
            st.markdown(f'<div class="po-carte-cadre">{v}</div>'
                        f'<p class="po-carte-leg">{_e(T("po_1_carte"))}</p>',
                        unsafe_allow_html=True)


def _sections_par_departement(m):
    """Les dix sections, groupées par département, avec leur effectif.

    LES EFFECTIFS VIENNENT DU FICHIER, PAS D'UNE LISTE ÉCRITE À LA MAIN.
    Une liste recopiée diverge du jour où une section change de nom ou de
    rattachement ; celle-ci se reconstruit à chaque lecture du contour des
    sections communales, qui porte déjà le département de chacune.
    """
    try:
        import territoire_page
        geo = territoire_page._geo()
    except Exception:
        return
    # LE NOM DU DÉPARTEMENT EST CORRIGÉ À L'AFFICHAGE, PAS DANS LA DONNÉE.
    # Le contour officiel écrit « Grande'Anse » ; le département s'appelle
    # Grand'Anse. On corrige au moment de l'écrire, sans toucher au fichier
    # source, qui doit rester tel qu'il a été reçu.
    CORR = {"Grande'Anse": "Grand'Anse"}
    par_dep = {}
    for s_ in geo.get("sections", []):
        nom = (s_.get("nom") or "").strip()
        dep = (s_.get("departement") or "").strip() or "—"
        dep = CORR.get(dep, dep)
        if nom:
            par_dep.setdefault(dep, []).append(nom)
    if not par_dep:
        return

    eff = m.get("sections_n") or {}
    blocs = []
    # LES DÉPARTEMENTS SONT RANGÉS DU PLUS FOURNI AU PLUS MAIGRE.
    # Neuf sections sur dix sont dans le Sud, une seule en Grand'Anse : deux
    # colonnes égales auraient laissé un grand vide en face du bloc court. Le
    # plus long passe donc en premier et se répartit lui-même sur deux
    # colonnes, le court se pose à la suite.
    for dep in sorted(par_dep, key=lambda d: (-len(par_dep[d]), d)):
        lignes = []
        for nom in sorted(par_dep[dep]):
            n = eff.get(nom)
            lignes.append(
                f'<li><span class="nm">{_e(nom)}</span>'
                + (f'<span class="nb">{n}</span>' if n else "") + '</li>')
        large = " po-dep-large" if len(lignes) >= 5 else ""
        blocs.append(f'<div class="po-dep{large}">'
                     f'<div class="dt">{_e(dep)} '
                     f'<span class="dn">{len(lignes)}</span></div>'
                     f'<ul>{"".join(lignes)}</ul></div>')

    st.markdown(f'<div class="po-lab">{_e(T("po_1_sections"))}</div>'
                f'<div class="po-deps">{"".join(blocs)}</div>'
                f'<p class="po-note">{_e(T("po_1_sections_x"))}</p>',
                unsafe_allow_html=True)


def _ecran_2(m):
    """L'écran qui dit ce qu'on mesure. Trois blocs, une seule surface.

    IL ÉTAIT FAIT DE SIX GRANDES CARTES et d'une rangée de chiffres encadrés,
    soit trois niveaux de boîtes emboîtées sur un écran qui n'a que trois
    choses à dire. Les titres en 27 px écrasaient les définitions qu'ils
    surmontaient, et deux rangées identiques se répondaient sans hiérarchie.

    Reste : les trois attributs séparés par un filet, la chaîne des chiffres en
    une ligne, les trois sources en trois lignes. Rien n'est retiré.
    """
    st.markdown(f'<div class="po-h">{_e(T("po_2_t"))}</div>'
                f'<p class="po-x">{_gras(T("po_2_x"))}</p>',
                unsafe_allow_html=True)

    st.markdown(
        '<div class="e2-att">' + "".join(
            f'<div class="e2-a"><b>{_e(T(k))}</b>'
            f'<span>{_e(T(k + "x"))}</span></div>'
            for k in ("po_2_a1", "po_2_a2", "po_2_a3"))
        + '</div>', unsafe_allow_html=True)

    # LA CHAÎNE EN UNE LIGNE. Quatre cartouches et trois chevrons pour dire
    # « 3, 7, 128, un score » : la ponctuation faisait tout le travail que le
    # texte pouvait faire seul.
    n_ind = sum(e["n"] for e in m["dims"].values())
    cases = [("3", T("po_2_f1"), ""),
             (str(len(m["dims"])), T("po_2_f2"), ""),
             (str(n_ind), T("po_2_f3"), T("po_2_f3x", f=m["n_scores"])),
             ("0–10", T("po_2_f4"), "")]
    morceaux = []
    for i, (v, lab, sous) in enumerate(cases):
        if i:
            morceaux.append('<i>·</i>')
        morceaux.append(f'<span><b>{_e(v)}</b>{_e(lab)}'
                        + (f' <em>{_e(sous)}</em>' if sous else "") + '</span>')
    st.markdown('<div class="e2-ch">' + "".join(morceaux) + '</div>',
                unsafe_allow_html=True)

    st.markdown(f'<div class="po-lab" style="margin-top:22px">'
                f'{_e(T("po_2_src"))}</div>'
                '<div class="e2-src">' + "".join(
                    f'<div class="e2-s"><b>{_e(T(k))}</b>'
                    f'<span>{_e(T(k + "x"))}</span></div>'
                    for k in ("po_2_s1", "po_2_s2", "po_2_s3"))
                + '</div>', unsafe_allow_html=True)
    _porte("po_porte_2", "methodologie")


def _couleur(v):
    return ROUGE if v < 3.5 else (AMBRE if v < 5 else VERT)


def _css_etapes(n):
    """La feuille des deux onglets d'étape, avec l'étape courante marquée."""
    r = ["<style>"]
    for i, cle in enumerate(ETAPES, 1):
        b = (f'div[class*="st-key-po_pas_{i}"] button,'
             f' div[class*="st-key-po_pas_{i}"] button[kind="primary"]')
        b1 = f'div[class*="st-key-po_pas_{i}"] button'
        actif = (i == n)
        r.append(f"""
        {b} {{
          display:grid !important;
          grid-template-columns:30px 1fr; grid-template-rows:auto;
          column-gap:11px;
          align-items:center; justify-items:start;
          text-align:left !important;
          padding:9px 2px 10px !important;
          min-height:0 !important; height:auto !important;
          background:transparent !important;
          border:none !important;
          border-bottom:{'3px' if actif else '1px'} solid
                        {'#2f6b4f' if actif else '#e6ecf4'} !important;
          border-radius:0 !important;
          box-shadow:none !important; transform:none !important;
          transition:border-color .15s ease;
        }}
        {b1}:hover {{
          background:transparent !important;
          border-bottom-color:#cfe3d7 !important;
        }}
        {b1}::before, {b1}[kind="primary"]::before {{
          content:"{i}";
          grid-column:1; grid-row:1;
          width:24px; height:24px; border-radius:50%;
          display:flex; align-items:center; justify-content:center;
          background:{'#dcebe2' if actif else '#f1f4f8'};
          color:{'#2f6b4f' if actif else '#7b8794'};
          font-size:12px; font-weight:700; font-variant-numeric:tabular-nums;
        }}
        /* LE VRAI ENFANT DE LA GRILLE EST UN DIV SANS NOM.
           Streamlit enveloppe le libellé d'un bouton dans un div dont la
           seule classe est un identifiant d'émotion, régénéré à chaque
           version : ni data-testid, ni nom stable. Placer le <p> dans la
           grille ne servait donc à rien — c'est ce div qui occupe la cellule,
           et il s'étalait sur toute la largeur en centrant son contenu. On le
           vise par sa position, `> div`, qui elle ne changera pas. */
        {b1} > div, {b1}[kind="primary"] > div {{
          grid-column:2; grid-row:1;
          justify-self:start !important; width:auto !important;
          text-align:left !important;
        }}
        {b1} p, {b1}[kind="primary"] p {{
          font-size:14.5px !important;
          font-weight:{'700' if actif else '600'} !important;
          color:{'#2f6b4f' if actif else '#3c4761'} !important;
          margin:0 !important;
          text-align:left !important; line-height:1.25 !important;
        }}""")
    # LES DEUX BOUTONS DE PARCOURS PORTENT LE MÊME HABIT QUE LES ÉTAPES.
    # « Suivant » était un pavé vert plein, seul élément de la page à crier
    # ainsi ; il attirait l'œil plus que le contenu qu'il sert à quitter. Il
    # devient une carte comme les autres, et ne se colore qu'au survol : un
    # filet vert dessous et le mot en gras vert, exactement comme l'étape en
    # cours au-dessus. La cohérence se voit, et la page se calme.
    for cle in ("po_suiv", "po_prec"):
        c = f'div[class*="st-key-{cle}"] button'
        r.append(f"""
        {c}, {c}[kind="primary"] {{
          background:transparent !important;
          border:none !important;
          border-bottom:1px solid #e6ecf4 !important;
          border-radius:0 !important;
          box-shadow:none !important; transform:none !important;
          padding:9px 2px 10px !important; min-height:0 !important;
          transition:border-color .15s ease;
        }}
        {c} p, {c}[kind="primary"] p {{
          font-size:14px !important; font-weight:600 !important;
          color:#3c4761 !important; margin:0 !important;
          transition:color .15s ease;
        }}
        {c}:hover, {c}[kind="primary"]:hover,
        {c}:focus, {c}[kind="primary"]:focus {{
          background:transparent !important;
          border-bottom:3px solid #2f6b4f !important;
        }}
        {c}:hover p, {c}[kind="primary"]:hover p,
        {c}:focus p, {c}[kind="primary"]:focus p {{
          color:#2f6b4f !important; font-weight:700 !important;
        }}""")

    r.append("</style>")
    return "".join(r)


def render():
    st.markdown(STYLE, unsafe_allow_html=True)
    st.session_state.setdefault("portail_etape", 1)
    # LE NUMÉRO D'ÉCRAN EST BORNÉ À CHAQUE RENDU, PAS SEULEMENT AU CLIC.
    # Le parcours comptait quatre écrans ; il en compte deux. Un lecteur dont
    # la session gardait « 3 » — parce qu'il y était au moment de la mise à
    # jour — arrivait sur une page en erreur. La borne se pose ici, où passe
    # tout le monde, et pas seulement dans les boutons qui font avancer.
    n = st.session_state["portail_etape"]
    if not isinstance(n, int) or n not in range(1, len(ETAPES) + 1):
        n = 1
        st.session_state["portail_etape"] = 1

    # LE TITRE DU SITE N'EST PLUS ÉCRIT ICI. Il est passé dans le bandeau,
    # sur l'illustration : le répéter juste en dessous aurait fait deux fois
    # la même enseigne à trois centimètres d'intervalle.

    # LES QUATRE BOUTONS SONT LA BARRE D'ÉTAPES, et on peut sauter directement
    # à l'un d'eux : un parcours qui ne se parcourt que dans l'ordre est une
    # prison, pas un guide. Le numéro est dans le libellé — un bandeau
    # décoratif au-dessus des mêmes quatre mots faisait doublon.
    # CHAQUE ÉTAPE EST UN ONGLET, PLUS UNE CARTE.
    # Le sous-titre — « Où ? », « Qu'a-t-on mesuré ? » — disait deux fois ce
    # que le nom disait déjà, et il fallait une boîte pour le tenir. Reste le
    # nom, une pastille numérotée écrite en CSS dans le pseudo-élément
    # ::before (Streamlit ne pose qu'un seul libellé sur un bouton), et un
    # filet dessous : vert et épais sur l'étape en cours, gris ailleurs.
    st.markdown(_css_etapes(n), unsafe_allow_html=True)
    cols = st.columns(len(ETAPES))
    for i, (col, cle) in enumerate(zip(cols, ETAPES), 1):
        with col:
            st.button(T(cle), key=f"po_pas_{i}",
                      on_click=_poser, args=(i,), use_container_width=True,
                      type="primary" if i == n else "secondary")

    m = _mesures(i18n.get_lang())
    if not m:
        st.info(T("po_absent"))
        return

    # PLUS DE CADRE AUTOUR DE L'ÉCRAN. Le contenu occupe déjà toute la
    # largeur : l'entourer d'un liseré gris ne le séparait de rien et donnait
    # à la page l'air d'un formulaire compartimenté.
    with st.container():
        (_ecran_1, _ecran_2)[n - 1](m)

    g, _milieu, d = st.columns([1.6, 4, 1.6])
    with g:
        if n > 1:
            st.button("← " + T("po_precedent"), key="po_prec",
                      on_click=_bouger, args=(-1,), use_container_width=True)
    with d:
        if n < len(ETAPES):
            st.button(T("po_suivant") + " →", key="po_suiv",
                      on_click=_bouger, args=(1,), use_container_width=True,
                      type="primary")
