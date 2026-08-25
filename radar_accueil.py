"""La rubrique « Diagramme radar de résilience » — le radar pour lui-même.

POURQUOI UNE RUBRIQUE À PART

Le radar est déjà présent à deux endroits, et il y a sa raison d'être : dans
« Analyse des résultats », il commente la dimension ouverte ; dans « Profils
territoriaux et sociaux », il accompagne la comparaison d'un territoire ou
d'un groupe. Mais on ne le trouve alors qu'en ouvrant autre chose.

Or c'est une figure qu'on cherche pour elle-même : « montre-moi le profil de
Dumont contre celui de Trichet », « où les femmes décrochent-elles par rapport
à l'ensemble ». Une figure qu'on demande par son nom mérite une entrée par son
nom.

CE QUE CETTE PAGE AJOUTE AUX DEUX AUTRES

Rien sur le fond — le moteur est le même, `radar_page`, et deux implémentations
finiraient par diverger. Elle ajoute le contexte : comment lire un radar, ce
qu'il permet, et surtout ce qu'il ne dit pas. C'est le genre de mode d'emploi
qu'on ne peut pas écrire au milieu d'une page de dimension sans l'alourdir, et
qui manque dès qu'on met la figure entre les mains de quelqu'un d'autre.
"""

import streamlit as st

import i18n
import radar_page
from i18n import T

ENCRE, ENCRE3 = "#101728", "#6b7590"

TEXTES = {
    "rda_titre": {"en": "Resilience Radar",
                  "fr": "Diagramme radar de résilience"},
    "rda_sous_titre": {
        "en": "Compare profiles, by dimension, by communal section, by group",
        "fr": "Comparer des profils, par dimension, par section communale, "
              "par groupe"},
    "rda_intro": {
        "en": "A radar shows a **shape**, not a ranking. Two territories with "
              "the same overall score can be flat everywhere or collapsed on a "
              "single axis, and those two situations call for entirely "
              "different responses. That difference is what this page is for.",
        "fr": "Un radar montre une **forme**, pas un classement. Deux "
              "territoires de même score d'ensemble peuvent être faibles "
              "partout ou effondrés sur un seul axe, et ces deux situations "
              "n'appellent pas la même réponse. C'est cette différence que "
              "cette page sert à voir."},
    "rda_lire": {"en": "How to read it", "fr": "Comment le lire"},
    "rda_l1_t": {"en": "The shape, not the area",
                 "fr": "La forme, pas l'aire"},
    "rda_l1": {
        "en": "A dent on one axis is a weak point; a regular polygon is a "
              "territory that is uniformly weak or uniformly strong. The area "
              "of the polygon means nothing, it depends on the order of the "
              "axes, which comes from the framework.",
        "fr": "Un creux sur un axe est un point faible ; un polygone régulier "
              "est un territoire uniformément faible ou uniformément solide. "
              "L'aire du polygone ne veut rien dire, elle dépend de l'ordre "
              "des axes, qui vient du cadre."},
    "rda_l2_t": {"en": "A fixed scale, always",
                 "fr": "Une échelle fixe, toujours"},
    "rda_l2": {
        "en": "Every axis runs from 0 to 10, in every view. A scale that "
              "adjusted to the highest value would turn a one-tenth gap into a "
              "chasm, and make the figure lie.",
        "fr": "Chaque axe va de 0 à 10, dans toutes les vues. Une échelle qui "
              "s'ajusterait au maximum observé transformerait un écart d'un "
              "dixième en gouffre, et ferait mentir la figure."},
    "rda_l3_t": {"en": "Three profiles at most",
                 "fr": "Trois profils au plus"},
    "rda_l3": {
        "en": "Beyond three overlaid polygons nothing is legible any more. The "
              "table under the figure carries the exact figures, to the "
              "hundredth, the eye reads a radius badly, and two close series "
              "are indistinguishable on the drawing.",
        "fr": "Au-delà de trois polygones superposés, plus rien n'est lisible. "
              "Le tableau sous la figure porte les valeurs exactes au "
              "centième, l'œil lit mal un rayon, et deux séries proches sont "
              "indiscernables sur le dessin."},
    "rda_l4_t": {"en": "What it cannot show",
                 "fr": "Ce qu'il ne peut pas montrer"},
    "rda_l4": {
        "en": "Satellite indicators have no breakdown by respondent: forest "
              "cover and rainfall do not vary with who answered. Compared by "
              "group, those axes carry the same value for everyone, a "
              "property of the source, not a measured equality.",
        "fr": "Les indicateurs satellitaires n'ont pas de ventilation par "
              "répondant : le couvert forestier et la pluie ne varient pas "
              "selon qui a répondu. Comparés par groupe, ces axes portent la "
              "même valeur pour tous, propriété de la source, pas égalité "
              "mesurée."},
    "rda_ailleurs": {
        "en": "The same figure also appears inside **Results Analysis**, for "
              "the dimension you have open, and inside **Territorial and "
              "Social Profiles**, beside the territory being compared. It is "
              "the same engine: change a score and the three views move "
              "together.",
        "fr": "La même figure apparaît aussi dans **Analyse des résultats**, "
              "pour la dimension ouverte, et dans **Profils territoriaux et "
              "sociaux**, à côté du territoire comparé. C'est le même "
              "moteur : un score qui change déplace les trois vues ensemble."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def render(entete=True):
    # `entete=False` quand la page est rendue dans un onglet : le titre de la
    # rubrique est déjà au-dessus, et deux titres empilés font perdre une
    # hauteur d'écran sans rien apprendre.
    if entete:
        st.markdown(
            f'<h2 style="font-size:21.5px;font-weight:700;color:{ENCRE};'
            f'letter-spacing:-.02em;margin:2px 0 0">{T("rda_titre")}</h2>'
            f'<p style="font-size:11.5px;color:{ENCRE3};letter-spacing:.06em;'
            f'text-transform:uppercase;margin:2px 0 0;font-weight:600">'
            f'{T("rda_sous_titre")}</p>', unsafe_allow_html=True)
    st.info(T("rda_intro"))

    # LA FIGURE D'ABORD, LE MODE D'EMPLOI ENSUITE. Qui arrive ici veut voir un
    # radar ; l'obliger à traverser quatre encadrés de méthode avant d'y
    # accéder inverserait l'ordre des priorités.
    with st.container(border=True):
        radar_page.render(cle="page")

    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{_e(T("rda_lire"))}</div>',
                    unsafe_allow_html=True)
        for gauche, droite in (("rda_l1", "rda_l2"), ("rda_l3", "rda_l4")):
            for col, cle in zip(st.columns(2), (gauche, droite)):
                with col:
                    st.markdown(
                        f'<div style="font-size:13.5px;font-weight:700;'
                        f'color:{ENCRE};margin:4px 0 3px">'
                        f'{_e(T(cle + "_t"))}</div>'
                        f'<p style="font-size:13px;color:#3c4761;'
                        f'line-height:1.6;margin:0 0 10px">{T(cle)}</p>',
                        unsafe_allow_html=True)
        st.caption(T("rda_ailleurs"))
