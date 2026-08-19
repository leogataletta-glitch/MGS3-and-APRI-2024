"""Le profil en radar — par dimension, par section communale, par groupe.

CE QUE CE MODULE REMET EN PLACE

Les diagrammes radar existaient : ils vivaient dans `resilience_page.py`, une
page devenue inaccessible quand la navigation a été refondue. Le code n'avait
pas été supprimé, seulement débranché — ce qui est pire, puisque rien ne le
signalait. Ce module le remet à sa place, et l'élargit à ce qui manquait.

DEUX NIVEAUX DE LECTURE, COMME DANS LE CADRE APRI

  · LES SIX DIMENSIONS — un axe par dimension, chaque axe portant la moyenne
    pondérée de ses indicateurs scorés. C'est le profil général : on voit d'un
    coup d'œil par où le territoire est fragile.
  · LES INDICATEURS D'UNE DIMENSION — un axe par indicateur. C'est le zoom :
    une dimension moyenne peut cacher un indicateur à zéro et un autre à dix.

TROIS FAÇONS DE COMPARER, ET C'EST LÀ QUE LE RADAR SERT VRAIMENT

Un radar seul est un joli dessin ; deux radars superposés sont un argument.
On peut donc comparer jusqu'à trois entités prises dans un même registre :

  · des SECTIONS COMMUNALES — où l'action se décide ;
  · des PAYSAGES — littoral contre montagne ;
  · des GROUPES DE RÉPONDANTS — femmes et hommes, tranches d'âge, catégories
    économiques.

L'échelle est FIXE de 0 à 10 sur tous les axes, dans tous les cas. C'est la
condition pour que deux profils se superposent honnêtement : une échelle qui
s'ajuste au maximum observé transforme un écart d'un dixième en écart visuel
énorme, et fait mentir la figure.

CE QUE LE RADAR NE DIT PAS

L'aire du polygone n'a aucun sens : elle dépend de l'ordre des axes, qui est
celui du cadre et non une propriété des données. On compare des rayons, pas des
surfaces — le tableau sous la figure porte les chiffres exacts, pour cela.
"""

import json
import os

import streamlit as st
import streamlit.components.v1 as components

import filtres
import i18n
import radar
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

DIMENSIONS = [
    ("dim1", "I. PHYSICAL AND INFRASTRUCTURAL DIMENSION"),
    ("dim2", "II. INSTITUTIONAL, TECHNOLOGICAL, AND GOVERNANCE  DIMENSION"),
    ("dim3", "III.  ENVIRONMENTAL AND ECOLOGICAL DIMENSION"),
    ("dim4", "IV. ECONOMIC, LIVELIHOODS, AND FOOD SECURITY DIMENSION"),
    ("dim5", "V. SOCIAL AND COMMUNITY DIMENSION"),
    ("dim6", "VI. HUMAN DIMENSION"),
]

# Un libellé court par dimension : « IV. Economic, livelihoods and food
# security » sur un sommet de radar déborde sur ses voisins.
COURT = {
    "dim1": ("Physical", "Physique"),
    "dim2": ("Institutional", "Institutionnel"),
    "dim3": ("Environmental", "Environnement"),
    "dim4": ("Economic", "Économie"),
    "dim5": ("Social", "Social"),
    "dim6": ("Human", "Humain"),
}

TOUT = "__ensemble__"

# Au-delà de douze sommets, les libellés se chevauchent et la figure ne se
# lit plus. Le plafond est affiché à l'écran, jamais appliqué en silence.
MAX_AXES = 12

TEXTES = {
    "rd_titre": {"en": "Radar profile", "fr": "Profil en radar"},
    "rd_intro": {
        "en": "Fixed 0–10 scale on every axis, so two profiles overlay "
              "honestly. Compare up to three at once. **The area of the "
              "polygon means nothing** — it depends on the order of the axes, "
              "which comes from the framework and not from the data. Compare "
              "the radii; the exact figures are in the table below.",
        "fr": "Échelle fixe de 0 à 10 sur chaque axe, pour que deux profils se "
              "superposent honnêtement. Trois comparaisons au plus à la fois. "
              "**L'aire du polygone ne veut rien dire** — elle dépend de "
              "l'ordre des axes, qui vient du cadre et non des données. On "
              "compare des rayons ; les chiffres exacts sont dans le tableau "
              "en dessous."},
    "rd_niveau": {"en": "Level", "fr": "Niveau"},
    "rd_n_dims": {"en": "The six dimensions", "fr": "Les six dimensions"},
    "rd_n_indic": {"en": "The indicators of one dimension",
                   "fr": "Les indicateurs d'une dimension"},
    "rd_dim": {"en": "Dimension", "fr": "Dimension"},
    "rd_registre": {"en": "Compare", "fr": "Comparer"},
    "rd_r_sections": {"en": "Communal sections", "fr": "Sections communales"},
    "rd_r_paysages": {"en": "Landscapes", "fr": "Paysages"},
    "rd_r_groupes": {"en": "Respondent groups", "fr": "Groupes de répondants"},
    "rd_choix": {"en": "Up to three, overlaid",
                 "fr": "Trois au plus, superposés"},
    "rd_ensemble": {"en": "Whole territory", "fr": "Ensemble du territoire"},
    "rd_vide": {"en": "Choose at least one to compare.",
                "fr": "Choisissez au moins un élément à comparer."},
    "rd_trop_peu": {
        "en": "This dimension has only {n} scored indicator(s): a radar needs "
              "at least three axes. The comparative table above carries the "
              "figures.",
        "fr": "Cette dimension n'a que {n} indicateur(s) scoré(s) : un radar "
              "demande au moins trois axes. Le tableau comparatif ci-dessus "
              "porte les chiffres."},
    "rd_axe": {"en": "Axis", "fr": "Axe"},
    "rd_coupe": {
        "en": "This dimension has {t} scored indicators; the radar shows the "
              "{n} lowest, because beyond that the labels overlap and the "
              "figure stops being readable. The full list is in the indicator "
              "accordion above.",
        "fr": "Cette dimension compte {t} indicateurs scorés ; le radar montre "
              "les {n} plus bas, au-delà les libellés se chevauchent et la "
              "figure cesse d'être lisible. La liste complète est dans "
              "l'accordéon des indicateurs, plus haut."},
    "rd_note_dims": {
        "en": "Each axis is the weighted mean of the scored indicators of that "
              "dimension. Indicators that are not calculated are excluded from "
              "the denominator, never counted as zeros.",
        "fr": "Chaque axe est la moyenne pondérée des indicateurs scorés de la "
              "dimension. Les indicateurs non calculés sont exclus du "
              "dénominateur, jamais comptés comme des zéros."},
    "rd_note_indic": {
        "en": "One axis per indicator of the dimension, on the same 0–10 "
              "scale as everywhere else on the platform.",
        "fr": "Un axe par indicateur de la dimension, sur la même échelle de 0 "
              "à 10 que partout ailleurs sur la plateforme."},
    "rd_note_groupe": {
        "en": "Satellite indicators have no breakdown by respondent: forest "
              "cover and rainfall do not vary with who answered. On those "
              "axes, the compared groups carry the same value — that is a "
              "property of the source, not a measured equality.",
        "fr": "Les indicateurs satellitaires n'ont pas de ventilation par "
              "répondant : le couvert forestier et la pluie ne varient pas "
              "selon qui a répondu. Sur ces axes, les groupes comparés portent "
              "la même valeur — c'est une propriété de la source, pas une "
              "égalité mesurée."},
    "rd_manque": {"en": "Results file missing.",
                  "fr": "Le fichier de résultats est absent."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)


def _trouver(nom):
    for c in (os.path.join(DATA, nom), os.path.join(APP_DIR, nom)):
        if os.path.exists(c):
            return c
    return None


@st.cache_data(show_spinner=False)
def _charger():
    p = _trouver("resultats.json")
    if not p:
        return None
    with open(p, encoding="utf-8") as f:
        res = json.load(f)
    return res["indicateurs"] if isinstance(res, dict) \
        and "indicateurs" in res else res


def _court(cle):
    en, fr = COURT.get(cle, (cle, cle))
    return fr if i18n.get_lang() == "fr" else en


def _nom_indic(r):
    if i18n.get_lang() == "fr" and r.get("indicateur_fr"):
        return r["indicateur_fr"]
    return r.get("indicateur", "")


def _moyenne(lignes, cible):
    """Moyenne pondérée des scores d'un groupe d'indicateurs, pour une cible.

    Même règle que partout ailleurs sur le site : un indicateur non calculé
    sort du dénominateur au lieu de compter zéro. Deux moyennes calculées
    différemment sur le même site finiraient par ne plus concorder, et
    personne ne saurait laquelle croire.
    """
    num = den = 0.0
    for r in lignes:
        sc = (r.get("scores_corriges") or {}).get(cible)
        if sc is None:
            continue
        p = r.get("ponderation") or 1
        num += p * float(sc)
        den += p
    return round(num / den, 2) if den else None


def _entites(registre):
    if registre == "sections":
        return list(filtres.SECTIONS), lambda c: c
    if registre == "paysages":
        return list(filtres.PAYSAGES), filtres.libelle_paysage
    return list(filtres.GROUPES), filtres.libelle_groupe


def render(dim=None, cle="r"):
    """Le bloc radar.

    `dim` fixe la dimension et force le niveau « indicateurs » : c'est ainsi
    qu'il est appelé depuis une page de dimension, où le niveau est déjà
    choisi par le contexte. Sans `dim`, les deux niveaux sont offerts.
    """
    res = _charger()
    if not res:
        st.info(T("rd_manque"))
        return

    st.markdown(T("rd_intro"))

    if dim is None:
        c1, c2 = st.columns([1.6, 1.4])
        with c1:
            niveau = st.radio(
                T("rd_niveau"), ["dims", "indic"],
                format_func=lambda k: T("rd_n_dims") if k == "dims"
                else T("rd_n_indic"),
                horizontal=True, key=f"rd_niv_{cle}")
        with c2:
            if niveau == "indic":
                dim = dict(DIMENSIONS)[st.selectbox(
                    T("rd_dim"), [d for d, _ in DIMENSIONS],
                    format_func=_court, key=f"rd_dim_{cle}")]
    else:
        niveau = "indic"

    # Les axes, et les indicateurs qui alimentent chacun.
    if niveau == "dims":
        axes, par_axe = [], {}
        for c, long in DIMENSIONS:
            lignes = [r for r in res if r["dimension"] == long]
            if not any((r.get("scores_corriges") or {}).get("Total")
                       is not None for r in lignes):
                continue
            axes.append(_court(c))
            par_axe[_court(c)] = lignes
    else:
        dedans = [r for r in res if r["dimension"] == dim
                  and (r.get("scores_corriges") or {}).get("Total") is not None]
        if len(dedans) < 3:
            st.info(T("rd_trop_peu", n=len(dedans)))
            return
        # PLAFOND D'AXES, ET IL EST DIT. La dimension environnementale porte
        # dix-sept indicateurs : à dix-sept sommets, les libellés se
        # chevauchent et la figure ne se lit plus. On garde les douze plus
        # bas — un tableau de bord de résilience se lit par ce qui manque — et
        # on écrit combien ont été laissés de côté, plutôt que de tronquer en
        # silence, ce qui laisserait croire à une couverture complète.
        total_dim = len(dedans)
        coupes = 0
        if len(dedans) > MAX_AXES:
            dedans = sorted(
                dedans,
                key=lambda r: (r.get("scores_corriges") or {}).get("Total", 10)
            )[:MAX_AXES]
            coupes = 1
        axes = [_nom_indic(r) for r in dedans]
        par_axe = {_nom_indic(r): [r] for r in dedans}

    # Le registre de comparaison — sections, paysages ou groupes. C'est ce
    # choix qui manquait : le radar d'avant ne comparait que des sections.
    g, d = st.columns([1.5, 2.5])
    with g:
        registre = st.radio(
            T("rd_registre"), ["sections", "paysages", "groupes"],
            format_func=lambda k: T("rd_r_" + k), horizontal=False,
            key=f"rd_reg_{cle}")
    options, libelle = _entites(registre)
    with d:
        choisies = st.multiselect(
            T("rd_choix"), [TOUT] + options,
            format_func=lambda c: T("rd_ensemble") if c == TOUT else libelle(c),
            default=[TOUT], max_selections=3, key=f"rd_sel_{registre}_{cle}")
    if not choisies:
        st.info(T("rd_vide"))
        return

    def _valeurs(ent):
        c = "Total" if ent == TOUT else ent
        return [_moyenne(par_axe[a], c) for a in axes]

    series = [((T("rd_ensemble") if e == TOUT else libelle(e)),
               _valeurs(e), None) for e in choisies]

    svg = radar.render_radar_svg(axes, series, taille=620)
    components.html(
        '<div style="background:#fff;font-family:Inter,system-ui,sans-serif">'
        f'<div style="margin:0 0 6px 8px">{radar.legende_html(series)}</div>'
        f'{svg}</div>', height=690, scrolling=False)

    st.caption(T("rd_note_dims") if niveau == "dims" else T("rd_note_indic"))
    if niveau == "indic" and coupes:
        st.caption(T("rd_coupe", t=total_dim, n=MAX_AXES))
    if registre == "groupes":
        st.caption(T("rd_note_groupe"))

    # LE TABLEAU N'EST PAS UN DOUBLON. L'œil lit mal un rayon ; deux séries
    # proches sur un axe sont indiscernables sur la figure et se distinguent
    # au centième dans le tableau.
    entete = ''.join(
        f'<th style="text-align:right;padding:7px 10px;'
        f'border-bottom:2px solid #e6ecf4;font-size:11.5px;'
        f'letter-spacing:.05em;text-transform:uppercase;color:#6b7590;'
        f'font-weight:700">{n}</th>' for n, _v, _c in series)
    corps = []
    for i, a in enumerate(axes):
        cells = ''.join(
            f'<td style="text-align:right;padding:7px 10px;'
            f'border-bottom:1px solid #f0f4f9;font-variant-numeric:'
            f'tabular-nums;font-weight:600;color:#101728">'
            + (f'{v[i]:.2f}'.replace('.', ',') if v[i] is not None else '—')
            + '</td>' for _n, v, _c in series)
        corps.append(
            f'<tr><td style="padding:7px 10px;'
            f'border-bottom:1px solid #f0f4f9;color:#3c4761">{a}</td>'
            + cells + '</tr>')
    st.markdown(
        '<div style="overflow-x:auto"><table style="width:100%;'
        'border-collapse:collapse;font-size:14px">'
        f'<tr><th style="text-align:left;padding:7px 10px;'
        f'border-bottom:2px solid #e6ecf4;font-size:11.5px;'
        f'letter-spacing:.05em;text-transform:uppercase;color:#6b7590;'
        f'font-weight:700">{T("rd_axe")}</th>{entete}</tr>'
        + ''.join(corps) + '</table></div>', unsafe_allow_html=True)
