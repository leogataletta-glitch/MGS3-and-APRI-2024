"""Les questions de l'enquête, rangées sous la dimension qu'elles servent.

POURQUOI CET ONGLET

Une page de dimension montrait jusqu'ici des indicateurs : des scores sur dix,
construits à partir des réponses. C'est le produit fini. Mais quelqu'un du
terrain qui lit « assainissement : 2/10 » veut savoir ce qu'on a demandé aux
ménages, et ce qu'ils ont répondu — pas la note, la matière. C'est ce que cet
onglet donne : la question mot pour mot, ses modalités, et la répartition des
réponses sous le filtre courant.

COMMENT LES QUESTIONS SONT RATTACHÉES À UNE DIMENSION

Deux niveaux, et l'écran dit lequel s'applique à chaque question.

  1. LIEN CERTAIN — la question alimente un indicateur de cette dimension.
     Ce lien n'est pas une opinion : il est écrit dans `resultats.json`, où
     chaque indicateur porte le texte de la question dont il est tiré. Ces
     questions portent la pastille du numéro de ligne.

  2. RATTACHEMENT THÉMATIQUE — la question appartient au même module du
     questionnaire qu'une question du premier groupe. Les modules sont
     attribués par le tableau ci-dessous, obtenu en comptant, pour chaque
     module, les dimensions des indicateurs qui y puisent, puis complété à la
     main pour les modules dont aucun indicateur ne se sert encore.

Ce second niveau est un choix éditorial, et il est dit comme tel à l'écran :
mieux vaut annoncer un classement discutable que le faire passer pour une
propriété des données.

LE FILTRE DE LA COLONNE DE GAUCHE S'APPLIQUE

Le fichier de cache porte les effectifs pour chaque section, chaque paysage et
chaque sous-population. Un filtre simple se lit donc directement, sans
recalcul. Le cas croisé — une section ET un groupe — n'existe pas dans ce
fichier : on retombe sur la section, et on le dit.
"""

import os
import pickle

import streamlit as st

import cadre_page
import filtres
import i18n
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(APP_DIR, "data", "cache_national.pkl")

# ---------------------------------------------------------------------------
# LES TEXTES DE CET ONGLET VOYAGENT AVEC LUI.
#
# Deux fois de suite, une mise à jour est arrivée en ligne sans son `i18n.py`,
# et le site s'est arrêté sur « il manque des clés de traduction » — alors que
# le seul fichier réellement neuf était celui-ci. Les fichiers sont poussés à
# la main, un par un ; en oublier un est normal, et l'architecture doit y
# survivre.
#
# Un module qui apporte une fonction apporte donc désormais ses propres
# textes. Ils sont versés dans le dictionnaire commun À L'IMPORT, et seulement
# si la clé n'y est pas déjà : un `i18n.py` à jour reste maître, un `i18n.py`
# en retard ne casse plus rien. Les mêmes clés figurent aussi dans `i18n.py`,
# qui garde son rôle de catalogue complet — mais elles n'y sont plus
# indispensables au fonctionnement.
# ---------------------------------------------------------------------------
TEXTES = {
    "d_onglet_questions": {"en": "Questions asked, and the answers",
                           "fr": "Les questions posées, et les réponses"},
    "d_onglet_indicateurs": {"en": "Resilience indicators",
                             "fr": "Indicateurs de résilience"},
    "q_intro": {
        "en": "{n} questions from the household survey relate to this "
              "dimension. {lien} of them directly feed one of its indicators "
              "and carry the line number; the others belong to the same "
              "questionnaire module.",
        "fr": "{n} questions de l'enquête ménage relèvent de cette dimension. "
              "{lien} d'entre elles alimentent directement un de ses "
              "indicateurs et en portent le numéro de ligne ; les autres "
              "appartiennent au même module du questionnaire."},
    "q_base": {"en": "Percentages of {cible} — base: {n} respondents.",
               "fr": "Pourcentages sur {cible} — base : {n} répondants."},
    "q_croise": {
        "en": "A section crossed with a group is not available at question "
              "level: the figures below are those of the section alone.",
        "fr": "Le croisement d'une section et d'un groupe n'existe pas au "
              "niveau des questions : les chiffres ci-dessous sont ceux de la "
              "section seule."},
    "q_ligne": {"en": "L{n}", "fr": "L{n}"},
    "q_n_questions": {"en": "{n} questions", "fr": "{n} questions"},
    "q_1_question": {"en": "1 question", "fr": "1 question"},
    "q_base_nulle": {"en": "No respondent under this filter.",
                     "fr": "Aucun répondant sous ce filtre."},
    "q_absent": {"en": "The survey answer cache is missing from the "
                       "repository (data/cache_national.pkl).",
                 "fr": "Le cache des réponses est absent du dépôt "
                       "(data/cache_national.pkl)."},
    "q_aucune_dim": {
        "en": "This dimension is measured by satellite, not by questionnaire: "
              "forest cover, rainfall, vegetation, surface temperature and "
              "aridity are observed, not declared. The few survey questions "
              "that touch the environment — irrigation, inputs, causes of "
              "crop loss — are listed here as soon as they are attached.",
        "fr": "Cette dimension est mesurée par satellite, pas par "
              "questionnaire : couvert forestier, pluie, végétation, "
              "température de surface et aridité sont observés, non déclarés. "
              "Les quelques questions d'enquête qui touchent à "
              "l'environnement — irrigation, intrants, causes de perte de "
              "récolte — apparaissent ici dès qu'elles sont rattachées."},
    "q_titre": {"en": "Survey results", "fr": "Résultats du questionnaire"},
    "q_avert_niveau": {
        "en": "**These are raw survey answers, not resilience indicators.** A "
              "questionnaire module is a group of questions asked together — "
              "it is not an indicator of the framework. The indicators, "
              "computed from these answers and scored out of ten, are in the "
              "first tab.",
        "fr": "**Ce sont des réponses brutes, pas des indicateurs de "
              "résilience.** Un module de questionnaire est un groupe de "
              "questions posées ensemble — ce n'est pas un indicateur du "
              "référentiel. Les indicateurs, calculés à partir de ces réponses "
              "et notés sur dix, sont dans le premier onglet."},
    "q_chercher": {"en": "Search a topic or a question",
                   "fr": "Rechercher un thème ou une question"},
    "q_rien": {"en": "No question matches this search.",
               "fr": "Aucune question ne correspond à cette recherche."},
    "q_note_rattachement": {
        "en": "Questions carrying a line number are linked to the dimension "
              "by the data itself: the indicator states which question it is "
              "drawn from. The others are attached through their "
              "questionnaire module — that grouping is an editorial choice, "
              "and a debatable one for modules that serve several dimensions.",
        "fr": "Les questions qui portent un numéro de ligne sont rattachées à "
              "la dimension par la donnée elle-même : l'indicateur dit de "
              "quelle question il est tiré. Les autres le sont par leur "
              "module de questionnaire — ce regroupement est un choix "
              "éditorial, discutable pour les modules qui servent plusieurs "
              "dimensions."},
}

for _cle, _val in TEXTES.items():
    i18n.DICO.setdefault(_cle, _val)


# Module du questionnaire -> dimension. Voir l'en-tête pour la méthode.
# Les modules marqués « (auto) » ont été attribués par le vote des indicateurs ;
# les autres à la main, faute d'indicateur qui y puise à ce jour.
MODULE_DIMENSION = {
    # ---- I. physique et infrastructures
    "AI. LOGEMENT / HABITAT": "dim1",                                  # auto
    "AJ. EAU, ASSAINISSEMENT ET HYGIÈNE (WASH)": "dim1",               # auto
    "C. ÉNERGIE DOMESTIQUE": "dim1",                                   # auto
    "D. CONNECTIVITÉ / COMMUNICATION": "dim1",                         # auto
    "E. GESTION DES DÉCHETS SOLIDES": "dim1",                          # auto
    "G. ACCÈS AUX INFRASTRUCTURES DE SANTÉ ET D'ÉDUCATION": "dim1",    # auto
    # ---- II. institutions, technologie et gouvernance
    "F. ACCÈS AUX SERVICES ADMINISTRATIFS": "dim2",
    "H. ENFANTS NÉS DANS LA SECTION COMMUNALE": "dim2",                # auto
    "I. GOUVERNANCE ET INTÉGRITÉ": "dim2",                             # auto
    "J. GESTION DES RISQUES ET DES CATASTROPHES": "dim2",              # auto
    "K. PARTICIPATION COMMUNAUTAIRE ET CITOYENNE": "dim2",             # auto
    # ---- III. environnement et écologie
    # La dimension environnementale est mesurée par satellite, pas par
    # questionnaire. Les seules questions qui la concernent sont celles où le
    # ménage décrit la pression qu'il exerce sur le milieu, ou celle qu'il
    # subit.
    "AO. AGRICULTURE — QUANTITÉ D'INTRANTS APPLIQUÉE": "dim3",
    "AP. AGRICULTURE — IRRIGATION": "dim3",
    "AN. AGRICULTURE — NOMBRE DE PIEDS D'ARBRES FRUITIERS PLANTÉS": "dim3",
    "AR. AGRICULTURE — FACTEURS D'ÉVOLUTION DES RENDEMENTS": "dim3",
    "W. AGRICULTURE — CIRCONSTANCES DE PERTE DE PRODUCTION PAR CULTURE": "dim3",
    # ---- IV. économie, moyens d'existence et sécurité alimentaire
    # « N. SÉCURITÉ ALIMENTAIRE » était à égalité entre la dimension physique
    # et la dimension humaine dans le vote automatique. Elle est rangée ici :
    # la sécurité alimentaire est nommée dans l'intitulé même de la dimension.
    "N. SÉCURITÉ ALIMENTAIRE (12 DERNIERS MOIS)": "dim4",
    "AG. SOURCES DE REVENUS DU FOYER": "dim4",
    "AH. ÉLEVAGE (PROXY DE RICHESSE — MODULE DE SCORING)": "dim4",
    "Q. EMPLOI ET REVENUS": "dim4",                                    # auto
    "R. FONCIER AGRICOLE": "dim4",                                     # auto
    "S. ÉPARGNE, CRÉDIT ET RÉSILIENCE FINANCIÈRE": "dim4",             # auto
    "T. AGRICULTURE — PRATIQUES GÉNÉRALES": "dim4",                    # auto
    "AL. AGRICULTURE — SUPERFICIE DÉDIÉE PAR CULTURE": "dim4",
    "AM. AGRICULTURE — MOMENT DE SEMIS PAR CULTURE": "dim4",
    "U. AGRICULTURE — RENDEMENTS ANNUELS PAR CULTURE": "dim4",
    "V. AGRICULTURE — ÉVOLUTION DES RENDEMENTS (5 ANS) PAR CULTURE": "dim4",
    "X. AGRICULTURE — POURCENTAGE DE PRODUCTION PERDUE PAR CULTURE": "dim4",
    "Y. PÊCHE — PRATIQUES GÉNÉRALES": "dim4",                          # auto
    "Z. PÊCHE — ESPÈCES PÊCHÉES ET ZONE": "dim4",
    "AA. PÊCHE — MONTANT PAR SORTIE ET PAR ESPÈCE": "dim4",
    "AB. PÊCHE — MOMENT LE PLUS RENTABLE PAR ESPÈCE": "dim4",
    "AC. ÉLEVAGE — GÉNÉRALITÉS": "dim4",
    "AD. ÉLEVAGE — MORTALITÉ": "dim4",
    "AE. FACTEUR LIMITANT LES BÉNÉFICES (PÊCHE / AGRICULTURE / ÉLEVAGE)": "dim4",
    # ---- V. social et communautaire
    "AK. ENTRAIDE COMMUNAUTAIRE (6 DERNIERS MOIS)": "dim5",            # auto
    "L. VIE SOCIALE ET CAPITAL COMMUNAUTAIRE": "dim5",                 # auto
    # ---- VI. humaine
    "M. ÉDUCATION ET SOUTIEN SOCIAL": "dim6",                          # auto
    "AF. COMPOSITION DU FOYER": "dim6",
    "AQ. PROFIL DU RÉPONDANT": "dim6",
    "O. MIGRATION": "dim6",
    "P. MIGRATION ÉCONOMIQUE ET ASPIRATIONS": "dim6",
}

# ---------------------------------------------------------------------------
# LES CODES DU QUESTIONNAIRE NE SORTENT PAS DU BACKEND.
#
# « AQ. PROFIL DU RÉPONDANT », « AF. COMPOSITION DU FOYER » : ces préfixes
# servent à l'enquêteur et au fichier de données, pas au lecteur. Ils restent
# les clés du dictionnaire — c'est par eux que les questions sont rattachées —
# mais l'écran affiche un intitulé analytique.
#
# Un module absent de ce tableau ne fait pas réapparaître son code : la
# fonction `libelle_module` retire le préfixe et remet la casse normale. Le
# tableau est là pour la qualité de l'intitulé, pas pour la sécurité de
# l'affichage.
# ---------------------------------------------------------------------------
MODULE_LABEL = {
    "AI. LOGEMENT / HABITAT":
        ("Housing and shelter", "Logement et habitat"),
    "AJ. EAU, ASSAINISSEMENT ET HYGIÈNE (WASH)":
        ("Water, sanitation and hygiene", "Eau, assainissement et hygiène"),
    "C. ÉNERGIE DOMESTIQUE":
        ("Household energy", "Énergie domestique"),
    "D. CONNECTIVITÉ / COMMUNICATION":
        ("Connectivity and communication", "Connectivité et communication"),
    "E. GESTION DES DÉCHETS SOLIDES":
        ("Solid waste management", "Gestion des déchets solides"),
    "G. ACCÈS AUX INFRASTRUCTURES DE SANTÉ ET D'ÉDUCATION":
        ("Access to health and education facilities",
         "Accès aux infrastructures de santé et d'éducation"),
    "F. ACCÈS AUX SERVICES ADMINISTRATIFS":
        ("Access to administrative services",
         "Accès aux services administratifs"),
    "H. ENFANTS NÉS DANS LA SECTION COMMUNALE":
        ("Births and civil registration",
         "Naissances et enregistrement à l'état civil"),
    "I. GOUVERNANCE ET INTÉGRITÉ":
        ("Governance and integrity", "Gouvernance et intégrité"),
    "J. GESTION DES RISQUES ET DES CATASTROPHES":
        ("Disaster risk management", "Gestion des risques et des catastrophes"),
    "K. PARTICIPATION COMMUNAUTAIRE ET CITOYENNE":
        ("Community and civic participation",
         "Participation communautaire et citoyenne"),
    "AO. AGRICULTURE — QUANTITÉ D'INTRANTS APPLIQUÉE":
        ("Agricultural inputs applied", "Intrants agricoles appliqués"),
    "AP. AGRICULTURE — IRRIGATION":
        ("Irrigation", "Irrigation"),
    "AN. AGRICULTURE — NOMBRE DE PIEDS D'ARBRES FRUITIERS PLANTÉS":
        ("Fruit trees planted", "Arbres fruitiers plantés"),
    "AR. AGRICULTURE — FACTEURS D'ÉVOLUTION DES RENDEMENTS":
        ("Drivers of yield change", "Facteurs d'évolution des rendements"),
    "W. AGRICULTURE — CIRCONSTANCES DE PERTE DE PRODUCTION PAR CULTURE":
        ("Causes of crop loss", "Circonstances de perte de production"),
    "N. SÉCURITÉ ALIMENTAIRE (12 DERNIERS MOIS)":
        ("Food security over the past year",
         "Sécurité alimentaire sur les douze derniers mois"),
    "AG. SOURCES DE REVENUS DU FOYER":
        ("Household income sources", "Sources de revenus du foyer"),
    "AH. ÉLEVAGE (PROXY DE RICHESSE — MODULE DE SCORING)":
        ("Livestock as a wealth proxy", "Élevage, indicateur de richesse"),
    "Q. EMPLOI ET REVENUS":
        ("Employment and income", "Emploi et revenus"),
    "R. FONCIER AGRICOLE":
        ("Agricultural land tenure", "Foncier agricole"),
    "S. ÉPARGNE, CRÉDIT ET RÉSILIENCE FINANCIÈRE":
        ("Savings, credit and financial resilience",
         "Épargne, crédit et résilience financière"),
    "T. AGRICULTURE — PRATIQUES GÉNÉRALES":
        ("Farming practices", "Pratiques agricoles"),
    "AL. AGRICULTURE — SUPERFICIE DÉDIÉE PAR CULTURE":
        ("Area cultivated, by crop", "Superficie cultivée, par culture"),
    "AM. AGRICULTURE — MOMENT DE SEMIS PAR CULTURE":
        ("Planting calendar, by crop", "Calendrier de semis, par culture"),
    "U. AGRICULTURE — RENDEMENTS ANNUELS PAR CULTURE":
        ("Annual yields, by crop", "Rendements annuels, par culture"),
    "V. AGRICULTURE — ÉVOLUTION DES RENDEMENTS (5 ANS) PAR CULTURE":
        ("Five-year yield trend, by crop",
         "Évolution des rendements sur cinq ans, par culture"),
    "X. AGRICULTURE — POURCENTAGE DE PRODUCTION PERDUE PAR CULTURE":
        ("Share of production lost, by crop",
         "Part de production perdue, par culture"),
    "Y. PÊCHE — PRATIQUES GÉNÉRALES":
        ("Fishing practices", "Pratiques de pêche"),
    "Z. PÊCHE — ESPÈCES PÊCHÉES ET ZONE":
        ("Species caught and fishing grounds", "Espèces pêchées et zones"),
    "AA. PÊCHE — MONTANT PAR SORTIE ET PAR ESPÈCE":
        ("Revenue per fishing trip, by species",
         "Revenu par sortie, par espèce"),
    "AB. PÊCHE — MOMENT LE PLUS RENTABLE PAR ESPÈCE":
        ("Most profitable season, by species",
         "Saison la plus rentable, par espèce"),
    "AC. ÉLEVAGE — GÉNÉRALITÉS":
        ("Livestock holdings", "Cheptel"),
    "AD. ÉLEVAGE — MORTALITÉ":
        ("Livestock mortality", "Mortalité du cheptel"),
    "AE. FACTEUR LIMITANT LES BÉNÉFICES (PÊCHE / AGRICULTURE / ÉLEVAGE)":
        ("Constraints on livelihood returns",
         "Facteurs limitant les revenus d'activité"),
    "AK. ENTRAIDE COMMUNAUTAIRE (6 DERNIERS MOIS)":
        ("Community mutual aid", "Entraide communautaire"),
    "L. VIE SOCIALE ET CAPITAL COMMUNAUTAIRE":
        ("Social life and community capital",
         "Vie sociale et capital communautaire"),
    "M. ÉDUCATION ET SOUTIEN SOCIAL":
        ("Education and social support", "Éducation et soutien social"),
    "AF. COMPOSITION DU FOYER":
        ("Household composition", "Composition du foyer"),
    "AQ. PROFIL DU RÉPONDANT":
        ("Respondent profile", "Profil du répondant"),
    "O. MIGRATION":
        ("Migration", "Migration"),
    "P. MIGRATION ÉCONOMIQUE ET ASPIRATIONS":
        ("Economic migration and aspirations",
         "Migration économique et aspirations"),
}

_PREFIXE = None


def libelle_module(cat):
    """L'intitulé lisible d'un module. Jamais son code."""
    import re
    couple = MODULE_LABEL.get(cat)
    if couple:
        return couple[1] if i18n.get_lang() == "fr" else couple[0]
    # Repli : on retire le préfixe alphabétique et on rétablit la casse. Un
    # module oublié dans le tableau s'affiche proprement, pas en « AB. ».
    nu = re.sub(r"^[A-Z]{1,3}\.\s*", "", cat or "").strip()
    nu = re.sub(r"\s*\((?:proxy|module)[^)]*\)", "", nu, flags=re.I).strip()
    return (nu[:1].upper() + nu[1:].lower()) if nu else cat


# Teinte par dimension, la même que dans la page d'indicateurs.
# Palette VALIDÉE, importée de cadre_page — cinq contrôles passés :
# bande de clarté, plancher de saturation, séparation des paires
# voisines en vision déficiente, plancher en vision normale, contraste
# sur le fond. Une seule définition pour tout le site : deux palettes
# recopiées finissent toujours par diverger.
TEINTE = dict(cadre_page.TEINTES)

# Recopié plutôt qu'importé de resilience_page : cet import-là entraînerait
# pandas et tout le module de cartographie pour un dictionnaire de sept lignes.
DIM_CLE = {
    "I. PHYSICAL AND INFRASTRUCTURAL DIMENSION": "dim1",
    "II. INSTITUTIONAL, TECHNOLOGICAL, AND GOVERNANCE  DIMENSION": "dim2",
    "III.  ENVIRONMENTAL AND ECOLOGICAL DIMENSION": "dim3",
    "IV. ECONOMIC, LIVELIHOODS, AND FOOD SECURITY DIMENSION": "dim4",
    "V. SOCIAL AND COMMUNITY DIMENSION": "dim5",
    "VI. HUMAN DIMENSION": "dim6",
    "VII. CULTURAL, IDENTITY-BASED, AND PSYCHOLOGICAL DIMENSION": "dim7",
}


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _fmt(v, dec=1):
    if v is None:
        return "—"
    return f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")


@st.cache_data(show_spinner=False)
def _charger():
    if not os.path.exists(CACHE):
        return None
    with open(CACHE, "rb") as f:
        return pickle.load(f)


@st.cache_data(show_spinner=False)
def _index_indicateurs():
    """question (en minuscules) -> [(ligne, dimension), …].

    Sert à poser la pastille « alimente la ligne 4 » sur les questions dont un
    indicateur est tiré, et à rattacher ces questions à coup sûr.
    """
    import json
    p = os.path.join(APP_DIR, "data", "resultats.json")
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as f:
        res = json.load(f)
    res = res["indicateurs"] if isinstance(res, dict) and "indicateurs" in res \
        else res
    idx = {}
    for r in res:
        q = (r.get("question") or "").strip().lower()
        if not q:
            continue
        idx.setdefault(q, []).append(
            (r["ligne"], DIM_CLE.get(r.get("dimension", ""), "")))
    return idx


def questions_de(cle_dim):
    """Les questions de cette dimension, groupées par module du questionnaire.

    Rend une liste de (module, [questions]), les modules dans l'ordre du
    questionnaire — c'est l'ordre dans lequel l'enquêteur les a posées, donc
    celui dans lequel elles s'éclairent l'une l'autre.
    """
    d = _charger()
    if not d:
        return []
    idx = _index_indicateurs()
    groupes, ordre = {}, []
    for t in d["themes"]:
        cat = t.get("category") or ""
        q = (t.get("question") or "").strip()
        lignes = [lg for lg, dim in idx.get(q.lower(), []) if dim == cle_dim]
        # Une question entre soit par le lien certain (elle alimente un
        # indicateur de la dimension), soit par son module.
        if not lignes and MODULE_DIMENSION.get(cat) != cle_dim:
            continue
        if cat not in groupes:
            groupes[cat] = []
            ordre.append(cat)
        groupes[cat].append((t, lignes))
    return [(c, groupes[c]) for c in ordre]


def _barres(rows, base, teinte):
    """Une modalité par ligne : libellé, barre, pourcentage, effectif.

    Barres horizontales et non un camembert : on compare des longueurs le long
    d'un axe commun, ce que l'œil fait bien, plutôt que des angles, ce qu'il
    fait mal. Une seule teinte, parce qu'il n'y a qu'une grandeur — la couleur
    ne code rien ici, elle appartient à la dimension.
    """
    if not base:
        return f'<div class="q-vide">{_e(T("q_base_nulle"))}</div>'
    lignes = []
    for label, grp in rows:
        n = (grp or {}).get(_CLE[0]) or 0
        pct = 100.0 * n / base
        lignes.append(
            f'<div class="q-ligne">'
            f'<div class="q-lab" title="{_e(label)}">{_e(label)}</div>'
            f'<div class="q-piste"><div class="q-barre" style="width:'
            f'{max(pct, 0.6):.2f}%;background:{teinte}"></div></div>'
            f'<div class="q-pct">{_fmt(pct)}&thinsp;%</div>'
            f'<div class="q-n">{_fmt(n, 0)}</div></div>')
    return "".join(lignes)


# Petit conteneur mutable : `_barres` a besoin de la clé de colonne courante,
# et la passer en argument à travers toute la chaîne d'affichage alourdirait
# quatre signatures pour une valeur qui ne change pas dans un rendu.
_CLE = ["Total"]


STYLE = """
<style>
  .q-mod   { font-size:11.5px; letter-spacing:.11em; text-transform:uppercase;
             font-weight:700; color:#8a93a5; margin:22px 0 2px; }
  .q-carte { border:1px solid #e7ecf3; border-radius:13px; padding:14px 17px;
             margin:10px 0 0; background:#fff;
             box-shadow:0 1px 2px rgba(16,23,40,.04); }
  .q-q     { font-size:15.5px; font-weight:600; color:#101728;
             line-height:1.45; }
  .q-meta  { font-size:12.5px; color:#8a93a5; margin:4px 0 11px; }
  .q-pastille { display:inline-block; font-size:11px; font-weight:700;
             border-radius:999px; padding:2px 9px; margin-left:7px;
             vertical-align:2px; color:#fff; }
  .q-ligne { display:grid; grid-template-columns:minmax(120px,2.1fr) 4fr 58px 52px;
             gap:10px; align-items:center; padding:3px 0; }
  .q-lab   { font-size:13.5px; color:#3c4761; line-height:1.35;
             overflow-wrap:break-word; }
  .q-piste { background:#f1f4f9; border-radius:5px; height:16px;
             overflow:hidden; }
  .q-barre { height:100%; border-radius:5px; }
  .q-pct   { font-size:13.5px; font-weight:600; color:#101728;
             text-align:right; font-variant-numeric:tabular-nums; }
  .q-n     { font-size:12.5px; color:#8a93a5; text-align:right;
             font-variant-numeric:tabular-nums; }
  .q-vide  { font-size:13px; color:#8a93a5; font-style:italic; }
</style>
"""


def _carte_question(t, lignes, base, teinte):
    past = "".join(
        f'<span class="q-pastille" style="background:{teinte}">'
        f'{_e(T("q_ligne", n=lg))}</span>' for lg in lignes)
    return (f'<div class="q-carte">'
            f'<div class="q-q">{_e(t.get("question") or "")}{past}</div>'
            f'<div class="q-meta">{_e(t.get("note") or "")}</div>'
            + _barres(t.get("rows") or [], base, teinte) + '</div>')


def rendre(cle_dim):
    d = _charger()
    if not d:
        st.info(T("q_absent"))
        return

    groupes = questions_de(cle_dim)
    teinte = TEINTE.get(cle_dim, "#1a6bb0")
    st.markdown(STYLE, unsafe_allow_html=True)

    if not groupes:
        # Le cas de la dimension environnementale si elle perdait ses
        # questions : le dire vaut mieux qu'afficher une page blanche.
        st.info(T("q_aucune_dim"))
        return

    # Quelle colonne du cache lire — exactement la même règle que pour les
    # indicateurs, pour que les deux onglets ne racontent jamais deux
    # histoires différentes sur le même filtre.
    cible = filtres.cible()
    croise = cible is None
    if croise:
        cible = filtres.section()
    _CLE[0] = cible if cible in d["base_n"] else "Total"
    base = d["base_n"].get(_CLE[0]) or 0

    n_q = sum(len(v) for _, v in groupes)
    n_lien = sum(1 for _, v in groupes for _t, lg in v if lg)

    # LE NIVEAU EST DIT AVANT TOUT LE RESTE. Un module de questionnaire n'est
    # pas un indicateur de résilience, et une page qui les empile sans le dire
    # laisse croire que si.
    st.warning(T("q_avert_niveau"))
    st.markdown(
        f'<p style="font-size:15px;color:#3c4761;line-height:1.6;'
        f'max-width:92ch;margin:2px 0 4px">'
        f'{_e(T("q_intro", n=n_q, lien=n_lien))}</p>',
        unsafe_allow_html=True)
    st.caption(T("q_base",
                 cible=(_CLE[0] if _CLE[0] != "Total"
                        else T("f_toutes_sections")),
                 n=_fmt(base, 0)))
    if croise:
        st.caption(T("q_croise"))

    cherche = (st.text_input(T("q_chercher"), key=f"q_rech_{cle_dim}",
                             placeholder="…") or "").strip().lower()
    if cherche:
        filtres_g = []
        for module, questions in groupes:
            gardees = [(t, lg) for t, lg in questions
                       if cherche in (t.get("question") or "").lower()
                       or cherche in libelle_module(module).lower()]
            if gardees:
                filtres_g.append((module, gardees))
        groupes = filtres_g
        if not groupes:
            st.info(T("q_rien"))
            return

    # UN MODULE = UN VOLET REPLIABLE, ET TOUS SONT FERMÉS.
    #
    # Ils s'ouvraient auparavant dès qu'ils contenaient une question reliée à
    # un indicateur, ce qui déroulait d'un coup des dizaines de graphiques et
    # rendait la page interminable. Le lecteur choisit maintenant ce qu'il
    # ouvre ; le nombre de questions et le nombre de liens sont écrits sur le
    # volet fermé, ce qui suffit à savoir où aller.
    #
    # TOUT LE MODULE EST ÉCRIT EN UN SEUL APPEL. Un appel par question — plus
    # de trois cents — ferait autant de conteneurs Streamlit, et la page
    # mettrait plusieurs secondes à se dessiner.
    for module, questions in groupes:
        n_l = sum(1 for _t, lg in questions if lg)
        combien = (T("q_1_question") if len(questions) == 1
                   else T("q_n_questions", n=len(questions)))
        titre = (f'{libelle_module(module)}  ·  {combien}'
                 + (f'  ·  {n_l} ↗' if n_l else ''))
        with st.expander(titre, expanded=bool(cherche)):
            st.markdown(
                "".join(_carte_question(t, lg, base, teinte)
                        for t, lg in questions),
                unsafe_allow_html=True)

    st.caption(T("q_note_rattachement"))


# ---------------------------------------------------------------------------
# LA DISTRIBUTION D'UNE QUESTION, RENDUE POUR LA PAGE DES INDICATEURS.
#
# Un indicateur d'enquête est un score tiré d'une question ; l'ouvrir sans
# montrer la répartition des réponses revient à demander de croire le calcul
# sur parole. Cette fonction est ici, et non dans la page des indicateurs,
# parce que c'est ici que vit le cache des réponses et la logique de filtre :
# deux implémentations finiraient par diverger.
# ---------------------------------------------------------------------------
def distribution(question, teinte):
    """Rend (html, base, question_trouvée) pour une question de l'enquête."""
    d = _charger()
    q = (question or "").strip().lower()
    if not d or not q:
        return None, 0, None
    cible = filtres.cible()
    if cible is None:
        cible = filtres.section()
    _CLE[0] = cible if cible in d["base_n"] else "Total"
    base = d["base_n"].get(_CLE[0]) or 0
    for t in d["themes"]:
        if (t.get("question") or "").strip().lower() == q:
            return _barres(t.get("rows") or [], base, teinte), base, t
    return None, base, None
