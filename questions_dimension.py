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

import filtres
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(APP_DIR, "data", "cache_national.pkl")

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

# Teinte par dimension, la même que dans la page d'indicateurs.
TEINTE = {"dim1": "#1a6bb0", "dim2": "#6b4fa8", "dim3": "#2a6b3f",
          "dim4": "#a8690a", "dim5": "#b4451f", "dim6": "#0f7b8a"}

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

    # UN MODULE = UN VOLET REPLIABLE. La dimension économique porte à elle
    # seule plus de trois cents questions — les batteries par culture et par
    # espèce pêchée, une question par culture. Déroulées d'un bloc, elles
    # noieraient les dix questions qui comptent. Les volets qui contiennent
    # une question reliée à un indicateur s'ouvrent d'office ; les autres
    # attendent qu'on les demande.
    #
    # TOUT LE MODULE EST ÉCRIT EN UN SEUL APPEL. Un appel par question — plus
    # de trois cents — ferait autant de conteneurs Streamlit, et la page
    # mettrait plusieurs secondes à se dessiner.
    for module, questions in groupes:
        ouvert = any(lg for _t, lg in questions)
        titre = f'{module}  ·  {T("q_n_questions", n=len(questions))}'
        with st.expander(titre, expanded=ouvert):
            st.markdown(
                "".join(_carte_question(t, lg, base, teinte)
                        for t, lg in questions),
                unsafe_allow_html=True)

    st.caption(T("q_note_rattachement"))
