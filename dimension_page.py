"""Une dimension de l'APRI, présentée pour elle-même.

Six onglets bâtis sur ce seul module. Chacun montre, pour sa dimension : le
score pondéré, la part du cadre effectivement couverte, la carte des sections,
et surtout — indicateur par indicateur — D'OÙ VIENT LA DONNÉE.

C'est le point de la refonte. Un score sans sa source est un chiffre qu'on ne
peut ni vérifier ni contester ; un tableau de bord institutionnel doit pouvoir
répondre à « d'où sortez-vous ça » sur chaque ligne, sans que le lecteur ait à
ouvrir un fichier annexe. Chaque indicateur porte donc ici sa question
d'enquête et ses modalités, ou son capteur satellitaire, ou son registre.

Les dimensions III et V délèguent une partie de leur contenu aux modules qui
existaient déjà — le détail environnemental et les fiches d'organisations —
plutôt que d'en dupliquer la logique.
"""

import json
import os

import streamlit as st
import streamlit.components.v1 as components

import assets
import cadre_page
import filtres
import questions_dimension
import questions_resultats
import radar_page
import i18n
import map_render
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

SECTIONS = ["Anse à Drick", "Barbois", "Dumont", "Débouchette", "Mouline",
            "Quentin", "Beaulieu", "Blactote", "Dalmette", "Trichet"]

# L'ordre est celui du cadre, pas celui de la couverture : une dimension mal
# documentée ne doit pas se retrouver reléguée en fin de liste, sinon le
# tableau de bord cache ses propres lacunes.
DIMENSIONS = [
    ("dim1", "I. PHYSICAL AND INFRASTRUCTURAL DIMENSION"),
    ("dim2", "II. INSTITUTIONAL, TECHNOLOGICAL, AND GOVERNANCE  DIMENSION"),
    ("dim3", "III.  ENVIRONMENTAL AND ECOLOGICAL DIMENSION"),
    ("dim4", "IV. ECONOMIC, LIVELIHOODS, AND FOOD SECURITY DIMENSION"),
    ("dim5", "V. SOCIAL AND COMMUNITY DIMENSION"),
    ("dim6", "VI. HUMAN DIMENSION"),
]
# La septième dimension du cadre n'a aucun indicateur calculé : elle n'a donc
# pas d'onglet. Elle reste listée dans les lacunes de la méthodologie, pour
# qu'une absence ne passe pas pour une inexistence.
DIM7 = "VII. CULTURAL, IDENTITY-BASED, AND PSYCHOLOGICAL DIMENSION"

# Palette VALIDÉE, importée de cadre_page — cinq contrôles passés :
# bande de clarté, plancher de saturation, séparation des paires
# voisines en vision déficiente, plancher en vision normale, contraste
# sur le fond. Une seule définition pour tout le site : deux palettes
# recopiées finissent toujours par diverger.
TEINTES = dict(cadre_page.TEINTES)

# ---------------------------------------------------------------------------
# LES TEXTES DE CETTE PAGE VOYAGENT AVEC ELLE — même règle que partout
# ailleurs depuis les trois pannes de déploiement : un module qui apporte une
# fonction apporte ses propres textes, versés dans le dictionnaire commun à
# l'import et seulement si la clé n'y est pas déjà.
# ---------------------------------------------------------------------------
TEXTES = {
    "d_indics_titre": {"en": "Indicators", "fr": "Indicateurs"},
    "d_indics_note": {
        "en": "The resilience indicators of this dimension, computed from the "
              "survey, from satellite imagery or from the registers, and "
              "scored out of ten. **Lowest score first**, a resilience "
              "dashboard is read by what is missing. Open one to see its "
              "figures, its source and its spread across the ten communal "
              "sections.",
        "fr": "Les indicateurs de résilience de cette dimension, calculés à "
              "partir de l'enquête, de l'imagerie satellitaire ou des "
              "registres, et notés sur dix. **Score le plus bas en tête**, un "
              "tableau de bord de résilience se lit par ce qui manque. Ouvrez-"
              "en un pour voir ses chiffres, sa source et sa dispersion entre "
              "les dix sections communales."},
    "d_chercher": {"en": "Search an indicator",
                   "fr": "Rechercher un indicateur"},
    "d_rien": {"en": "No indicator matches this search.",
               "fr": "Aucun indicateur ne correspond à cette recherche."},
    "d_n_indics": {"en": "{n} indicators", "fr": "{n} indicateurs"},
    "d_bloc_comparaison": {"en": "Across the ten communal sections",
                           "fr": "Entre les dix sections communales"},
    "d_bloc_distribution": {"en": "Answers to the survey question",
                            "fr": "Réponses à la question d'enquête"},
    "d_bloc_tableau": {"en": "Comparative table, every indicator at once",
                       "fr": "Tableau comparatif, tous les indicateurs d'un "
                             "coup"},
    "d_ferme_note": {
        "en": "Everything is closed by default: you open what you want to "
              "read.",
        "fr": "Tout est fermé par défaut : on ouvre ce qu'on veut lire."},
    "d_c_valeur": {"en": "Measured value", "fr": "Valeur mesurée"},
    "d_c_poids2": {"en": "Weight in the dimension",
                   "fr": "Poids dans la dimension"},
    "d_pas_de_section": {
        "en": "This indicator is not broken down by communal section.",
        "fr": "Cet indicateur n'est pas ventilé par section communale."},
    "d_choix_dim": {"en": "Dimension", "fr": "Dimension"},
    "d_onglet_ind2": {"en": "Indicators", "fr": "Indicateurs"},
    "d_onglet_q2": {"en": "Survey results", "fr": "Résultats du questionnaire"},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _fmt(v, dec=1):
    if v is None:
        return "—"
    return f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")


def _trouver(nom):
    for c in (os.path.join(DATA, nom), os.path.join(APP_DIR, nom)):
        if os.path.exists(c):
            return c
    return None


@st.cache_data(show_spinner=False)
def _charger():
    res = vent = None
    if _trouver("resultats.json"):
        with open(_trouver("resultats.json"), encoding="utf-8") as f:
            res = json.load(f)
    if _trouver("ventilation.json"):
        with open(_trouver("ventilation.json"), encoding="utf-8") as f:
            vent = json.load(f)
    return res, vent


def nom_indic(r):
    if i18n.get_lang() == "fr" and r.get("indicateur_fr"):
        return r["indicateur_fr"]
    return r["indicateur"]


def note_indic(r):
    return (r.get("note") if i18n.get_lang() == "fr" else r.get("note_en")) \
        or r.get("note") or ""


def expl_indic(r):
    return (r.get("expl_fr") if i18n.get_lang() == "fr"
            else r.get("expl_en")) or ""


def source_de(r):
    """Clé de source d'un indicateur — c'est elle qui décide de tout l'affichage.

    Le fichier de résultats ne porte de champ `source` que pour ce qui ne vient
    pas de l'enquête ménage. L'absence de champ vaut donc « enquête », et il
    vaut mieux l'écrire ici une fois que de le supposer à dix endroits.
    """
    s = r.get("source")
    if s == "satellite":
        return "satellite"
    if s == "OCB":
        return "ocb"
    if r.get("calculable") == "non":
        return "absente"
    return "menage"


BADGES = {
    "menage": ("#1a6bb0", "#eaf3fb"),
    "satellite": ("#2a6b3f", "#e8f4ec"),
    "ocb": ("#0b7f74", "#e5f6f3"),
    "absente": ("#8a93a5", "#f2f4f7"),
}


def _badge(cle):
    coul, fond = BADGES[cle]
    return (f'<span style="display:inline-block;padding:2px 9px;'
            f'border-radius:999px;background:{fond};color:{coul};'
            f'font-size:11px;font-weight:700;letter-spacing:.04em;'
            f'text-transform:uppercase;white-space:nowrap">'
            f'{_e(T("d_src_" + cle))}</span>')


def scores_de(r, cible):
    return (r.get("scores_corriges") or {}).get(cible)


def est_score(r):
    sc = r.get("scores_corriges") or {}
    return sc.get("Total") is not None or any(v is not None
                                              for v in sc.values())


# ------------------------------------------------------------------ agrégats
def score_dimension(lignes, cible):
    """Moyenne pondérée des indicateurs scorés de la dimension.

    Les indicateurs non calculés sont EXCLUS du dénominateur, jamais comptés
    comme des zéros. Un indicateur manquant n'est pas un indicateur mauvais :
    l'assimiler à zéro punirait le territoire pour une lacune du dispositif de
    mesure, et rendrait le score dépendant de l'avancement du projet plutôt
    que de l'état du paysage. La part réellement couverte est affichée à côté,
    c'est elle qui dit ce que vaut la moyenne.
    """
    num = den = 0.0
    for r in lignes:
        sc = scores_de(r, cible)
        if sc is None:
            continue
        p = r.get("ponderation") or 1
        num += sc * p
        den += p
    return (num / den) if den else None


def couverture(lignes):
    total = sum((r.get("ponderation") or 0) for r in lignes)
    faits = sum((r.get("ponderation") or 0) for r in lignes if est_score(r))
    n_faits = sum(1 for r in lignes if est_score(r))
    return n_faits, len(lignes), faits, total


# -------------------------------------------------------------------- rendu
def _tableau_indicateurs(lignes, cible, teinte, vent=None):
    entetes = [T("d_col_ligne"), T("d_col_indicateur"), T("d_col_source"),
               T("d_col_valeur"), T("d_col_score"), T("d_col_poids")]
    out = ['<div style="overflow-x:auto"><table style="width:100%;'
           'border-collapse:collapse;font-size:13.5px">',
           '<tr>' + ''.join(
               f'<th style="text-align:{"left" if i < 3 else "right"};'
               f'padding:9px 10px;border-bottom:2px solid #e6ecf4;'
               f'font-size:11.5px;letter-spacing:.05em;text-transform:uppercase;'
               f'color:#6b7590;font-weight:700">{_e(h)}</th>'
               for i, h in enumerate(entetes)) + '</tr>']
    C = ('padding:9px 10px;border-bottom:1px solid #f0f4f9;text-align:right;'
         'font-variant-numeric:tabular-nums')
    # Triés du score le plus bas : un tableau de bord de résilience se lit par
    # ce qui manque, pas par ce qui va bien.
    def _sc(r):
        return filtres.score(r, vent)

    ordre = sorted(lignes, key=lambda r: (_sc(r) is None, _sc(r) or 0,
                                          r["ligne"]))
    for r in ordre:
        sc = _sc(r)
        val = filtres.valeur(r, vent)
        coul = ("#8a93a5" if sc is None else
                "#b4451f" if sc <= 3 else "#c98a2e" if sc <= 6 else "#2a6b3f")
        unite = r.get("unite") or ("%" if source_de(r) == "menage" else "")
        aff = (f'{_fmt(val, 2)} {unite}'.strip()
               if isinstance(val, (int, float)) else "—")
        out.append(
            f'<tr><td style="padding:9px 10px;border-bottom:1px solid #f0f4f9;'
            f'color:#8a93a5;font-variant-numeric:tabular-nums">{r["ligne"]}</td>'
            f'<td style="padding:9px 10px;border-bottom:1px solid #f0f4f9">'
            f'{_e(nom_indic(r))}</td>'
            f'<td style="padding:9px 10px;border-bottom:1px solid #f0f4f9">'
            f'{_badge(source_de(r))}</td>'
            f'<td style="{C};color:#6b7590">{aff}</td>'
            f'<td style="{C};font-weight:700;color:{coul}">'
            f'{sc if sc is not None else "—"}</td>'
            f'<td style="{C};color:#a9b0be">'
            f'{_fmt(r.get("ponderation"), 2)}</td></tr>')
    out.append('</table></div>')
    return ''.join(out)


def _fiche_source(r):
    """D'où vient cette donnée — le cœur de la refonte.

    Trois cas seulement, et chacun se raconte différemment. L'enquête ménage
    doit citer sa question et ses modalités mot pour mot : c'est ce qui permet
    à quelqu'un du terrain de dire « cette question a été mal comprise ». Le
    satellite doit nommer son capteur et sa résolution. Un indicateur non
    calculé doit dire quelle source le débloquerait, faute de quoi il passe
    pour une négligence.
    """
    src = source_de(r)
    parts = []
    q = (r.get("question") or "").strip()
    mod = (r.get("modalites") or "").strip()

    if src == "menage" and q:
        parts.append((T("d_bloc_question"),
                      f'<em>« {_e(q)} »</em>'
                      + (f'<div style="margin-top:5px;color:#6b7590;'
                         f'font-size:13px">{_e(T("d_modalites"))} : '
                         f'{_e(mod)}</div>' if mod else '')))
    elif src in ("satellite", "ocb") and q:
        parts.append((T("d_bloc_origine"), _e(q)))

    if r.get("echelle"):
        parts.append((T("d_bloc_bareme"), _e(r["echelle"])))
    note = note_indic(r)
    if note:
        parts.append((T("d_bloc_note"), _e(note)))

    n = (r.get("n") or {}).get("Total")
    if n:
        parts.append((T("d_bloc_base"), T("d_base_texte", n=n)))

    return ''.join(
        f'<div style="margin:0 0 11px">'
        f'<div style="font-size:11.5px;letter-spacing:.06em;'
        f'text-transform:uppercase;color:#1a6bb0;font-weight:700">{_e(t)}</div>'
        f'<div style="font-size:13.5px;color:#3c4761;line-height:1.6;'
        f'margin-top:2px">{c}</div></div>' for t, c in parts)


def _carte_dimension(lignes, teinte, cle):
    valeurs = {s: score_dimension(lignes, s) for s in SECTIONS}
    valeurs = {s: (round(v, 2) if v is not None else None)
               for s, v in valeurs.items()}
    dispo = [v for v in valeurs.values() if v is not None]
    if not dispo:
        return None
    seuils = map_render.nice_thresholds(dispo)
    infos = {s: T("d_info_carte", n=sum(1 for r in lignes
                                        if scores_de(r, s) is not None))
             for s in SECTIONS}
    hauteur = 620
    svg, seuils_ret, _m = map_render.render_map_svg(
        valeurs, {s: 1 for s in SECTIONS}, seuils, height=hauteur,
        polarity="eleve_bon", unite="", infos=infos)
    legende = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:7px;'
        f'margin-right:18px"><span style="width:22px;height:12px;'
        f'border-radius:3px;background:{c};box-shadow:inset 0 0 0 1px '
        f'rgba(0,0,0,.12)"></span><span style="font-size:12px;'
        f'color:#52514e">{lab}</span></span>'
        for c, lab in map_render.legend_items(seuils_ret, "eleve_bon", ""))
    return (
        '<div style="font-family:system-ui,-apple-system,\'Segoe UI\','
        'sans-serif;background:#ffffff"><div style="margin:0 0 8px">'
        f'<span style="font-size:11.5px;color:#898781;letter-spacing:.05em;'
        f'margin-right:14px">{T("legende_seuils")}</span>{legende}</div>'
        f'{svg}</div>'), hauteur


def render(cle_dim, complement=None):
    """Rend l'onglet d'une dimension. `cle_dim` vaut dim1 … dim6.

    L'ORDRE DE LECTURE EST CELUI D'UN OUTIL D'ANALYSE, ET IL A CHANGÉ :

        dimension → description → filtres → liste d'indicateurs → détail

    Les filtres sont dans la page, sous le titre, et non plus dans la marge.
    La liste d'indicateurs est fermée : on ouvre celui qu'on veut lire, au lieu
    de recevoir trente graphiques d'un coup. Les indicateurs passent devant les
    questions parce que ce sont eux le produit de la plateforme ; les réponses
    brutes restent accessibles dans le second onglet, et cet onglet dit
    lui-même qu'un module de questionnaire n'est pas un indicateur.

    `complement` est une fonction rendue à la fin de l'onglet des indicateurs.
    Deux dimensions s'en servent — l'environnement pour ses onze indicateurs
    satellitaires, le social pour les fiches d'organisations de base — plutôt
    que de dupliquer ici une page qui existait déjà.
    """
    res, vent = _charger()
    dimension = dict(DIMENSIONS).get(cle_dim)
    teinte = TEINTES.get(cle_dim, "#1a6bb0")

    # NI TITRE NI SOUS-TITRE ICI. La liste déroulante juste au-dessus porte
    # déjà le nom de la dimension ; le répéter en 21 px poussait les filtres —
    # qui commandent tout ce qui suit — sous la ligne de flottaison.
    if not res:
        st.info(T("e_absent"))
        st.stop()

    filtres.barre(cle=cle_dim)

    st.markdown(
        f'<div style="background:#fff;border:1px solid #e3eaf3;border-left:5px '
        f'solid {teinte};border-radius:14px;padding:13px 17px;font-size:14.5px;'
        f'color:#3c4761;margin:6px 0 6px;max-width:96ch">'
        f'{T(cle_dim + "_intro")}</div>', unsafe_allow_html=True)

    # LA NOUVELLE ANALYSE DÉTAILLÉE VIENT EN TÊTE, AVANT L'EXISTANT.
    # Elle suit l'ordre dans lequel la donnée se construit : les réponses aux
    # questions et leurs effectifs bruts, puis ce que le référentiel en fait —
    # pondération, score, extrêmes. Rien n'a été retiré en dessous : les
    # onglets d'origine suivent, intacts.
    questions_resultats.render(cle_dim, dimension)

    _o_indicateurs, _o_questions = st.tabs(
        [T("d_onglet_ind2"), T("d_onglet_q2")])
    with _o_indicateurs:
        _rendre_indicateurs(cle_dim, res, vent, dimension, teinte, complement)
    with _o_questions:
        questions_dimension.rendre(cle_dim)


def _couleur_score(sc):
    return ("#8a93a5" if sc is None else
            "#b4451f" if sc <= 3 else "#c98a2e" if sc <= 6 else "#2a6b3f")


ACC_STYLE = """
<style>
  .ind-tete  { display:flex; gap:14px; align-items:baseline; flex-wrap:wrap;
               margin:0 0 10px; }
  .ind-kpi   { display:flex; flex-direction:column; }
  .ind-kpi-l { font-size:10.5px; letter-spacing:.08em; text-transform:uppercase;
               font-weight:700; color:#8a93a5; }
  .ind-kpi-v { font-size:16px; font-weight:700; color:#101728;
               font-variant-numeric:tabular-nums; line-height:1.2; }
  .ind-sec   { display:grid; grid-template-columns:minmax(96px,1.3fr) 5fr 46px;
               gap:10px; align-items:center; padding:3px 0; }
  .ind-sec-l { font-size:12px; color:#3c4761; }
  .ind-sec-p { background:#f1f4f9; border-radius:5px; height:14px;
               overflow:hidden; }
  .ind-sec-b { height:100%; border-radius:5px; }
  .ind-sec-v { font-size:12px; font-weight:700; text-align:right;
               font-variant-numeric:tabular-nums; }
  .ind-lab   { font-size:11px; letter-spacing:.08em; text-transform:uppercase;
               font-weight:700; color:#8a93a5; margin:14px 0 4px; }
</style>
"""


def _comparaison_sections(r, teinte):
    """La dispersion d'un indicateur entre les dix sections communales.

    C'est la comparaison que le lecteur cherche en ouvrant un indicateur :
    non pas « combien », mais « où ». Les sections sont classées du score le
    plus bas, comme le reste de la page.
    """
    sc = r.get("scores_corriges") or {}
    paires = [(s, sc.get(s)) for s in SECTIONS]
    paires = [(s, v) for s, v in paires if v is not None]
    if not paires:
        return None
    paires.sort(key=lambda kv: kv[1])
    return "".join(
        f'<div class="ind-sec"><div class="ind-sec-l">{_e(s)}</div>'
        f'<div class="ind-sec-p"><div class="ind-sec-b" style="width:'
        f'{max(10 * float(v), 1):.0f}%;background:{_couleur_score(v)}">'
        f'</div></div>'
        f'<div class="ind-sec-v" style="color:{_couleur_score(v)}">'
        f'{_fmt(v, 1)}</div></div>' for s, v in paires)


def _accordeon_indicateurs(lignes, vent, teinte, cle_dim):
    """La liste d'indicateurs, FERMÉE PAR DÉFAUT.

    Le reproche fait à l'ancienne page était juste : elle déroulait tout, et
    une page qui déroule tout ne se parcourt pas, elle se subit. Chaque
    indicateur est ici une ligne repliée qui porte l'essentiel — son nom, son
    score, sa source — et n'ouvre son détail que si on le lui demande.
    """
    st.markdown(ACC_STYLE, unsafe_allow_html=True)
    st.markdown(questions_dimension.STYLE, unsafe_allow_html=True)

    def _sc(r):
        return filtres.score(r, vent)

    ordre = sorted(lignes, key=lambda r: (_sc(r) is None, _sc(r) or 0,
                                          r["ligne"]))
    cherche = (st.text_input(T("d_chercher"), key=f"d_rech_{cle_dim}",
                             placeholder="…") or "").strip().lower()
    if cherche:
        ordre = [r for r in ordre if cherche in nom_indic(r).lower()
                 or cherche in (r.get("question") or "").lower()]
        if not ordre:
            st.info(T("d_rien"))
            return

    for r in ordre:
        sc = _sc(r)
        val = filtres.valeur(r, vent)
        # L'étiquette d'un volet Streamlit ne prend pas de HTML : le score y
        # est donc écrit en toutes lettres plutôt que peint. La couleur revient
        # à l'ouverture, où elle a la place d'exister.
        titre = (f'{nom_indic(r)}   ·   '
                 + (f'{_fmt(sc, 1)} / 10' if sc is not None
                    else T("d_non_calcule")))
        with st.expander(titre, expanded=bool(cherche) and len(ordre) == 1):
            unite = r.get("unite") or ("%" if source_de(r) == "menage" else "")
            aff = (f'{_fmt(val, 2)} {unite}'.strip()
                   if isinstance(val, (int, float)) else "—")
            st.markdown(
                f'<div class="ind-tete">'
                f'<div class="ind-kpi"><div class="ind-kpi-l">'
                f'{_e(T("d_col_score"))}</div><div class="ind-kpi-v" '
                f'style="color:{_couleur_score(sc)}">'
                f'{_fmt(sc, 1) if sc is not None else "—"}'
                f'<span style="font-size:11px;color:#8a93a5"> / 10</span>'
                f'</div></div>'
                f'<div class="ind-kpi"><div class="ind-kpi-l">'
                f'{_e(T("d_c_valeur"))}</div>'
                f'<div class="ind-kpi-v">{_e(aff)}</div></div>'
                f'<div class="ind-kpi"><div class="ind-kpi-l">'
                f'{_e(T("d_c_poids2"))}</div><div class="ind-kpi-v">'
                f'{_fmt(r.get("ponderation"), 2)}</div></div>'
                f'<div style="margin-left:auto">{_badge(source_de(r))}</div>'
                f'</div>', unsafe_allow_html=True)

            exp = expl_indic(r)
            if exp:
                st.markdown(
                    f'<p style="font-size:14px;color:#3c4761;line-height:1.6;'
                    f'margin:0 0 11px;max-width:92ch">{_e(exp)}</p>',
                    unsafe_allow_html=True)
            st.markdown(_fiche_source(r), unsafe_allow_html=True)

            # La comparaison entre sections — « où », et pas seulement
            # « combien ».
            comp = _comparaison_sections(r, teinte)
            st.markdown(
                f'<div class="ind-lab">{_e(T("d_bloc_comparaison"))}</div>'
                + (comp or f'<div style="font-size:12px;color:#8a93a5;'
                           f'font-style:italic">'
                           f'{_e(T("d_pas_de_section"))}</div>'),
                unsafe_allow_html=True)

            # La répartition des réponses, quand l'indicateur sort d'une
            # question d'enquête : un score sans sa distribution demande qu'on
            # le croie sur parole.
            if source_de(r) == "menage":
                html, base, _t = questions_dimension.distribution(
                    r.get("question"), teinte)
                if html:
                    st.markdown(
                        f'<div class="ind-lab">'
                        f'{_e(T("d_bloc_distribution"))}</div>' + html,
                        unsafe_allow_html=True)


def _rendre_indicateurs(cle_dim, res, vent, dimension, teinte, complement):
    """Le contenu de l'onglet « indicateurs »."""
    lignes = [r for r in res if r["dimension"] == dimension]
    n_faits, n_tot, p_faits, p_tot = couverture(lignes)
    score = score_dimension(lignes, "Total")

    # ------------------------------------------------------------ chiffres
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("d_bloc_chiffres")}</div>',
                    unsafe_allow_html=True)
        meilleures = [(s, score_dimension(lignes, s)) for s in SECTIONS]
        meilleures = [(s, v) for s, v in meilleures if v is not None]
        haut = max(meilleures, key=lambda kv: kv[1]) if meilleures else None
        bas = min(meilleures, key=lambda kv: kv[1]) if meilleures else None

        for col, lib, val, unite, sous, coul in zip(
                st.columns(4),
                [T("d_c_score"), T("d_c_couverture"), T("d_c_haut"),
                 T("d_c_bas")],
                [_fmt(score, 2), _fmt(100 * p_faits / p_tot, 0) if p_tot else "—",
                 haut[0] if haut else "—", bas[0] if bas else "—"],
                ["/ 10", "%", "", ""],
                [T("d_c_score_sous", n=n_faits),
                 T("d_c_couverture_sous", a=n_faits, b=n_tot),
                 T("d_c_haut_sous", v=_fmt(haut[1], 2)) if haut else "",
                 T("d_c_bas_sous", v=_fmt(bas[1], 2)) if bas else ""],
                [teinte, "#6b7590", "#2a6b3f", "#b4451f"]):
            with col:
                st.markdown(
                    map_render.cartouche_html(lib, val, unite, sous,
                                              couleur=coul),
                    unsafe_allow_html=True)
        st.caption(T("d_c_note"))

    # --------------------------------------------------------------- radar
    # « Indicateurs clés → graphiques → cartes » : le radar est le graphique,
    # et il arrive donc entre les quatre chiffres et la carte. Il compare la
    # dimension entre sections, entre paysages ou entre groupes — c'est la
    # figure qui manquait depuis la refonte de la navigation.
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("rd_titre")}</div>',
                    unsafe_allow_html=True)
        radar_page.render(dim=dimension, cle=cle_dim)

    # --------------------------------------------------------------- carte
    carte = _carte_dimension(lignes, teinte, cle_dim)
    if carte:
        html, hauteur = carte
        with st.container(border=True):
            st.markdown(f'<div class="titre-bloc vert">{T("d_bloc_carte")}</div>',
                        unsafe_allow_html=True)
            st.caption(T("d_bloc_carte_note"))
            components.html(html, height=hauteur + 46, scrolling=False)

    # --------------------------------------------- LA LISTE DES INDICATEURS
    # Une seule liste, fermée, à la place des deux blocs d'avant — un tableau
    # déroulé de tous les indicateurs, puis une seconde liste de leurs sources.
    # Rien n'est perdu : chiffres, source, question, barème, base et
    # comparaison entre sections se trouvent maintenant dans le volet de
    # l'indicateur concerné, et le tableau comparatif reste disponible plus
    # bas, replié.
    with st.container(border=True):
        st.markdown(
            f'<div class="titre-bloc">{T("d_indics_titre")} · '
            f'{T("d_n_indics", n=len(lignes))}</div>', unsafe_allow_html=True)
        st.markdown(T("d_indics_note"))
        st.caption(filtres.resume() + " — " + T("d_ferme_note"))
        _accordeon_indicateurs(lignes, vent, teinte, cle_dim)
        st.caption(T("d_bloc_indicateurs_note"))
        if filtres.groupe() != filtres.TOUS:
            st.caption(T("f_note_satellite"))

    # ------------------------------------------------ le tableau, en dernier
    # « Indicateurs clés → graphiques → cartes → comparaisons → tableaux
    # détaillés » : le tableau ferme la marche, replié, pour qui veut tout
    # voir d'un coup ou copier des chiffres.
    with st.expander(T("d_bloc_tableau")):
        cible = filtres.cible() or filtres.section()
        st.markdown(_tableau_indicateurs(lignes, cible, teinte, vent),
                    unsafe_allow_html=True)
        st.caption(T("d_bloc_sources_texte"))

    # Le détail propre à deux dimensions — environnement, organisations de
    # base — vient ici, à la fin des indicateurs, et non dans l'onglet des
    # questions : ce sont des mesures, pas des réponses de ménage.
    if complement is not None:
        complement()

    st.caption(T("e_source"))
    st.caption(T("credit"))
