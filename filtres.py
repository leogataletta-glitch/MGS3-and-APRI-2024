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

import icones
import i18n
from i18n import T

TEXTES = {
    "f_groupe_long": {"en": "Respondent group", "fr": "Groupe de répondants"},
    "f_auto": {
        "en": "Results update automatically as you change the filters.",
        "fr": "Les résultats se mettent à jour automatiquement selon vos "
              "filtres."},
    "f_reinit_long": {"en": "Reset the filters",
                      "fr": "Réinitialiser les filtres"},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)

SECTIONS = ["Anse à Drick", "Barbois", "Dumont", "Débouchette", "Mouline",
            "Quentin", "Beaulieu", "Blactote", "Dalmette", "Trichet"]
GROUPES = ["Femme", "Homme", "<25", "25-39", "40-59", "60+",
           "Cat A", "Cat B", "Cat C"]
GROUPE_CLE = {"Homme": "hommes", "Femme": "femmes", "Cat A": "cat_a",
              "Cat B": "cat_b", "Cat C": "cat_c", "<25": "age_25",
              "25-39": "age_25_39", "40-59": "age_40_59", "60+": "age_60"}

PAYSAGES = ["Littoral", "Montagne"]

# Une section communale appartient tout entière à un paysage : c'est une
# propriété du lieu, pas du répondant. Ce tableau reprend à l'identique
# `ventilation.json["paysage"]` ; il est recopié ici pour que le module des
# filtres n'ait pas à charger un fichier de données, et il est vérifié au
# démarrage par `verifier_paysages()` ci-dessous pour qu'il ne puisse pas
# diverger en silence.
SECTION_PAYSAGE = {
    "Anse à Drick": "Montagne", "Barbois": "Montagne", "Beaulieu": "Littoral",
    "Blactote": "Littoral", "Dalmette": "Littoral", "Débouchette": "Montagne",
    "Dumont": "Montagne", "Mouline": "Montagne", "Quentin": "Montagne",
    "Trichet": "Littoral"}

TOUTES = "__toutes__"
TOUS = "__tous__"
TOUS_P = "__tous_paysages__"


def _defaut():
    st.session_state.setdefault("f_section", TOUTES)
    st.session_state.setdefault("f_groupe", TOUS)
    st.session_state.setdefault("f_paysage", TOUS_P)


def section():
    _defaut()
    return st.session_state["f_section"]


def groupe():
    _defaut()
    return st.session_state["f_groupe"]


def paysage():
    _defaut()
    return st.session_state["f_paysage"]


def libelle_paysage(v):
    return T("f_tous_paysages") if v == TOUS_P else T("pay_" + v)


def actif():
    return (section() != TOUTES or groupe() != TOUS
            or paysage() != TOUS_P)


def libelle_section(v):
    return T("f_toutes_sections") if v == TOUTES else v


def libelle_groupe(v):
    return T("f_tous_groupes") if v == TOUS else T(GROUPE_CLE.get(v, v))


def reinitialiser():
    st.session_state["f_section"] = TOUTES
    st.session_state["f_groupe"] = TOUS
    st.session_state["f_paysage"] = TOUS_P


def incoherent():
    """Vrai quand la section demandée n'appartient pas au paysage demandé —
    Dumont est en montagne, la croiser avec « Littoral » ne désigne aucun
    répondant. On ne bloque pas le choix, on le dit à l'écran."""
    s, p = section(), paysage()
    if s == TOUTES or p == TOUS_P:
        return False
    return SECTION_PAYSAGE.get(s) != p


def cible():
    """La clé à lire dans `scores_corriges`, quand une seule dimension de
    filtre est posée. Rend None quand section ET groupe le sont — il faut
    alors passer par la ventilation croisée, ce dont `score()` se charge.

    Ordre de priorité, du plus précis au moins précis :

      1. la SECTION, si elle est posée. Une section est incluse tout entière
         dans un paysage ; demander « Dumont » et « Montagne » désigne le même
         ensemble de répondants que « Dumont » seul, et le score de la section
         est le plus fin des deux. Le paysage est donc ignoré ici — pas perdu :
         `resume()` le rappelle entre parenthèses.
      2. le PAYSAGE, s'il est posé sans section. Il prime sur le groupe parce
         qu'il est porté par TOUS les indicateurs, y compris satellitaires, là
         où le groupe n'est ventilé que dans l'enquête.
      3. le GROUPE.
    """
    s, g, p = section(), groupe(), paysage()
    if s != TOUTES:
        return s if g == TOUS else None
    if p != TOUS_P:
        return p
    if g != TOUS:
        return g
    return "Total"


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
    """Une phrase disant sur quoi porte l'affichage, pour le haut des pages.

    Elle suit exactement l'ordre de priorité de `cible()` : ce qui est écrit
    est ce qui est calculé. Quand un filtre est ignoré parce qu'un plus fin le
    recouvre, la phrase le dit plutôt que de le passer sous silence — sinon on
    lit un chiffre de section en croyant lire un chiffre de paysage.
    """
    s, g, p = section(), groupe(), paysage()
    if s != TOUTES:
        if g != TOUS:
            return T("f_resume_croise", s=s, g=libelle_groupe(g))
        if p != TOUS_P:
            return T("f_resume_section_pay", s=s,
                     p=libelle_paysage(SECTION_PAYSAGE.get(s, p)))
        return T("f_resume_section", s=s)
    if p != TOUS_P:
        if g != TOUS:
            return T("f_resume_paysage_groupe", p=libelle_paysage(p),
                     g=libelle_groupe(g))
        return T("f_resume_paysage", p=libelle_paysage(p))
    if g != TOUS:
        return T("f_resume_groupe", g=libelle_groupe(g))
    return T("f_resume_tout")


def avertissement():
    """Le message à afficher quand la combinaison demandée n'a pas de sens
    géographique. Rend None quand tout va bien."""
    if not incoherent():
        return None
    s, p = section(), paysage()
    return T("f_incoherent", s=s, p=libelle_paysage(p),
             vrai=libelle_paysage(SECTION_PAYSAGE.get(s, p)))


# ---------------------------------------------------------------- dans la page
_ICONE_DE = {"f_section": "maison", "f_paysage": "montagne",
             "f_groupe": "personnes"}


def _css_icones_selects():
    """Une icône dans chaque sélecteur, à gauche du texte.

    Streamlit ne laisse rien insérer dans un `selectbox` ; on peint donc
    l'icône en `::before` sur le conteneur du widget, repéré par sa classe
    `st-key-<clé>`, et on décale le texte d'autant. C'est le même procédé que
    pour les entrées de navigation.
    """
    out = []
    for cle, ico in _ICONE_DE.items():
        base = f'div[class*="st-key-{cle}"] div[data-baseweb="select"]'
        out.append(f'{base} {{ position:relative; }}')
        out.append(f'{base} > div:first-child {{ padding-left:38px; }}')
        out.append(
            f'{base}::before {{ content:""; position:absolute; left:13px; '
            f'top:50%; transform:translateY(-50%); width:18px; height:18px; '
            f'z-index:1; pointer-events:none; background-color:#5a7ea8; '
            f'-webkit-mask:{icones.masque(ico)} center/contain no-repeat; '
            f'mask:{icones.masque(ico)} center/contain no-repeat; }}')
    return "".join(out)


BARRE_STYLE = """
<style>
  div[data-testid="stHorizontalBlock"]:has(.f-ancre) {
      background:#f7fafd; border:1px solid #e3eaf3; border-radius:12px;
      padding:12px 16px 4px; margin:6px 0 2px; align-items:end; }
  div[data-testid="stHorizontalBlock"]:has(.f-ancre) label p {
      font-size:12.5px !important; letter-spacing:0; text-transform:none;
      font-weight:600 !important; color:#3c4761 !important; }
  /* Le bouton s'étirait sur toute la hauteur de la carte et pesait plus que
     les trois sélecteurs réunis, alors qu'il n'est qu'une sortie de secours. */
  div[data-testid="stHorizontalBlock"]:has(.f-ancre) button {
      height:40px; min-height:40px; margin-bottom:16px;
      font-size:13px !important; }
  .f-ancre { display:none; }
  .f-auto  { display:flex; align-items:center; gap:7px; font-size:12.5px;
             color:#6b7590; margin:2px 0 12px 4px; }
</style>
"""


def _select(cle, options, libelle, etiquette):
    """Un sélecteur dont l'affichage suit la langue, même changée en cours de
    route.

    LE BOGUE QUE CELA CORRIGE. Les options étaient rendues par `format_func`
    sur un widget dont la clé ne changeait jamais ; en basculant de l'anglais
    au français, les intitulés des trois listes restaient en anglais jusqu'au
    rechargement complet de la page. Le widget affiché porte donc une clé
    suffixée par la langue — il est recréé quand elle change — tandis que la
    VALEUR reste dans `f_section` / `f_paysage` / `f_groupe`, que tout le site
    lit. Le choix survit au changement de langue, l'étiquette non.
    """
    w = f"{cle}__{i18n.get_lang()}"
    courant = st.session_state[cle]

    def _repercuter():
        st.session_state[cle] = st.session_state[w]

    st.selectbox(etiquette, options, format_func=libelle,
                 index=options.index(courant) if courant in options else 0,
                 key=w, on_change=_repercuter)


def barre(cle="p"):
    """La zone de filtres, DANS LA PAGE, sous le titre de la rubrique.

    POURQUOI ELLE A QUITTÉ LA COLONNE DE GAUCHE. Un filtre posé dans la marge
    est un filtre qu'on oublie : il agit sur des chiffres qui se trouvent à
    quarante centimètres de lui, et rien à l'écran ne relie les deux. Ici, il
    est juste au-dessus du résultat qu'il commande, dans le sens de lecture.
    La colonne de gauche ne fait plus que naviguer.

    `cle` distingue les widgets si deux barres devaient coexister dans un même
    rendu ; l'état, lui, reste unique — `f_section`, `f_paysage`, `f_groupe` —
    de sorte que le choix suit l'utilisateur d'une rubrique à l'autre.
    """
    _defaut()
    st.markdown(BARRE_STYLE + "<style>" + _css_icones_selects() + "</style>",
                unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([3, 2.4, 2.6, 1.5],
                                vertical_alignment="bottom")
    with c1:
        st.markdown('<span class="f-ancre"></span>', unsafe_allow_html=True)
        _select("f_section", [TOUTES] + SECTIONS, libelle_section,
                T("f_section"))
    with c2:
        _select("f_paysage", [TOUS_P] + PAYSAGES, libelle_paysage,
                T("f_paysage"))
    with c3:
        _select("f_groupe", [TOUS] + GROUPES, libelle_groupe,
                T("f_groupe_long"))
    with c4:
        st.button(T("f_reinitialiser"), key=f"f_reset_{cle}",
                  on_click=reinitialiser, use_container_width=True,
                  disabled=not actif())

    # Dire que le recalcul est automatique évite qu'on cherche un bouton
    # « appliquer » qui n'existe pas — et qu'on croie, faute de l'avoir
    # trouvé, que rien ne s'est passé.
    st.markdown(
        f'<div class="f-auto">{icones.svg("rafraichir", "#5a7ea8", 15, 2)}'
        f'<span>{T("f_auto")}</span></div>', unsafe_allow_html=True)

    av = avertissement()
    if av:
        st.warning(av, icon="⚠")
    return resume()


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
        T("f_paysage"), [TOUS_P] + PAYSAGES, format_func=libelle_paysage,
        key="f_paysage", label_visibility="visible")
    st.selectbox(
        T("f_groupe"), [TOUS] + GROUPES, format_func=libelle_groupe,
        key="f_groupe", label_visibility="visible")

    # Les pastilles ne sont pas décoratives : elles répètent l'état du filtre
    # là où l'œil revient, en bas de colonne, pour qu'on ne lise jamais un
    # chiffre en croyant qu'il porte sur l'ensemble.
    chips = []
    if section() != TOUTES:
        chips.append((T("f_section"), section()))
    if paysage() != TOUS_P:
        chips.append((T("f_paysage"), libelle_paysage(paysage())))
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

    av = avertissement()
    if av:
        st.warning(av, icon="⚠")
