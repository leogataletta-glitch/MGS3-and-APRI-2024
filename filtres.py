"""Les filtres actifs — une seule source de vérité pour tout le site.

Jusqu'ici chaque page portait son propre sélecteur : on choisissait Dumont
dans la dimension environnementale, puis on passait à la dimension économique
et on retombait sur l'ensemble. Ce module remonte le choix d'un cran : il est
posé une fois dans la colonne de gauche, et toutes les pages le lisent.

DEUX FILTRES, ET LEUR COMBINAISON

  · une SECTION COMMUNALE, ou les dix ;
  · un GROUPE — femmes, hommes, tranches d'âge, catégories — ou tous.

Les deux ensemble ne se lisent pas dans le même fichier que chacun pris
seul. `resultats.json` porte les scores par section OU par groupe ;
`ventilation.json` porte le croisement section × groupe. La fonction
`score()` ci-dessous choisit la bonne source selon ce qui est demandé — c'est
tout l'intérêt d'avoir un module dédié plutôt que le même branchement recopié
dans cinq pages, où il finirait par diverger.

CE QUE LE FILTRE NE PEUT PAS FAIRE, ET QUI EST DIT À L'ÉCRAN

Un indicateur satellitaire n'a pas de ventilation par sexe : la forêt et la
pluie ne varient pas selon le répondant. Filtrer sur « femmes » ne change donc
rien à ces lignes-là, et le module le signale plutôt que d'afficher un chiffre
identique en laissant croire à une égalité mesurée.
"""

import streamlit as st

import i18n
from i18n import T

SECTIONS = ["Anse à Drick", "Barbois", "Dumont", "Débouchette", "Mouline",
            "Quentin", "Beaulieu", "Blactote", "Dalmette", "Trichet"]
GROUPES = ["Femme", "Homme", "<25", "25-39", "40-59", "60+",
           "Cat A", "Cat B", "Cat C"]
GROUPE_CLE = {"Homme": "hommes", "Femme": "femmes", "Cat A": "cat_a",
              "Cat B": "cat_b", "Cat C": "cat_c", "<25": "age_25",
              "25-39": "age_25_39", "40-59": "age_40_59", "60+": "age_60"}

TOUTES = "__toutes__"
TOUS = "__tous__"


def _defaut():
    st.session_state.setdefault("f_section", TOUTES)
    st.session_state.setdefault("f_groupe", TOUS)


def section():
    _defaut()
    return st.session_state["f_section"]


def groupe():
    _defaut()
    return st.session_state["f_groupe"]


def actif():
    return section() != TOUTES or groupe() != TOUS


def libelle_section(v):
    return T("f_toutes_sections") if v == TOUTES else v


def libelle_groupe(v):
    return T("f_tous_groupes") if v == TOUS else T(GROUPE_CLE.get(v, v))


def reinitialiser():
    st.session_state["f_section"] = TOUTES
    st.session_state["f_groupe"] = TOUS


def cible():
    """La clé à lire dans `scores_corriges`, quand une seule dimension de
    filtre est posée. Rend None quand les deux le sont — il faut alors passer
    par la ventilation, ce dont `score()` se charge."""
    s, g = section(), groupe()
    if s == TOUTES and g == TOUS:
        return "Total"
    if s != TOUTES and g == TOUS:
        return s
    if s == TOUTES and g != TOUS:
        return g
    return None


def score(indic, vent=None):
    """Score de l'indicateur sous le filtre courant.

    Quand une section ET un groupe sont demandés, la valeur vient de la
    ventilation croisée ; elle n'existe que pour les indicateurs d'enquête, et
    on retombe alors sur le score de la section — pas sur celui de
    l'ensemble, qui serait plus faux encore.
    """
    sc = indic.get("scores_corriges") or {}
    c = cible()
    if c is not None:
        return sc.get(c)
    s, g = section(), groupe()
    bloc = ((vent or {}).get("sections", {}).get(s, {})
            .get(str(indic["ligne"])) or {})
    v = (bloc.get("scores") or {}).get(g)
    return v if v is not None else sc.get(s)


def valeur(indic, vent=None):
    """La valeur brute, sous la même logique que `score`."""
    vals = indic.get("valeurs") or {}
    c = cible()
    if c is not None:
        return vals.get(c)
    s, g = section(), groupe()
    bloc = ((vent or {}).get("sections", {}).get(s, {})
            .get(str(indic["ligne"])) or {})
    v = (bloc.get("valeurs") or {}).get(g)
    return v if v is not None else vals.get(s)


def resume():
    """Une phrase disant sur quoi porte l'affichage, pour le haut des pages."""
    s, g = section(), groupe()
    if s == TOUTES and g == TOUS:
        return T("f_resume_tout")
    if s != TOUTES and g == TOUS:
        return T("f_resume_section", s=s)
    if s == TOUTES and g != TOUS:
        return T("f_resume_groupe", g=libelle_groupe(g))
    return T("f_resume_croise", s=s, g=libelle_groupe(g))


# ------------------------------------------------------------------ colonne
def rendre_panneau():
    """Le bloc « Filtres actifs » de la colonne de gauche."""
    _defaut()
    lang = i18n.get_lang()

    entete = st.columns([3, 2])
    with entete[0]:
        st.markdown(f'<div class="nav-groupe" style="margin-top:2px">'
                    f'{T("f_titre")}</div>', unsafe_allow_html=True)
    with entete[1]:
        st.button(T("f_reinitialiser"), key="f_reset", on_click=reinitialiser,
                  type="secondary", use_container_width=True,
                  disabled=not actif())

    st.selectbox(
        T("f_section"), [TOUTES] + SECTIONS, format_func=libelle_section,
        key="f_section", label_visibility="visible")
    st.selectbox(
        T("f_groupe"), [TOUS] + GROUPES, format_func=libelle_groupe,
        key="f_groupe", label_visibility="visible")

    # Les pastilles ne sont pas décoratives : elles répètent l'état du filtre
    # là où l'œil revient, en bas de colonne, pour qu'on ne lise jamais un
    # chiffre en croyant qu'il porte sur l'ensemble.
    chips = []
    if section() != TOUTES:
        chips.append((T("f_section"), section()))
    if groupe() != TOUS:
        chips.append((T("f_groupe"), libelle_groupe(groupe())))
    if chips:
        st.markdown(
            '<div class="f-chips">' + ''.join(
                f'<div class="f-chip"><span class="f-chip-cle">{c}</span>'
                f'<span class="f-chip-val">{v}</span></div>'
                for c, v in chips) + '</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="f-vide">{T("f_aucun")}</div>',
                    unsafe_allow_html=True)
