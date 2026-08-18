"""Page d'accueil — la vue d'ensemble de l'APRI.

L'entrée d'un tableau de bord institutionnel ne doit pas être un menu : elle
doit répondre, en un écran, à « de quoi parle ce site, sur quel territoire,
avec quelles données, et qu'est-ce que ça donne ». Le reste — le détail par
dimension, la méthode, les téléchargements — vient après, pour qui veut
creuser.

D'où l'ordre de cette page : trois chiffres de périmètre et la localisation,
l'histoire du projet ensuite — ce qu'est APRI, d'où cela vient, ce que l'indice
ne prétend pas dire — puis les résultats saillants, la carte et les livraisons
récentes.

AUCUN LOGO DANS LE CONTENU. La marque APRI et celle du PNUE vivent dans la
colonne de gauche, où elles sont visibles en permanence ; les répéter en tête
de chaque page vole la place du titre sans rien apprendre à personne.

TOUS LES CHIFFRES SONT CALCULÉS, AUCUN N'EST ÉCRIT EN DUR. Une page d'accueil
qui affiche des nombres figés devient fausse à la première mise à jour des
données, et personne ne s'en aperçoit — c'est le pire défaut possible pour une
vitrine.
"""

import json
import os

import streamlit as st
import streamlit.components.v1 as components

import i18n
import map_render
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

SECTIONS = ["Anse à Drick", "Barbois", "Dumont", "Débouchette", "Mouline",
            "Quentin", "Beaulieu", "Blactote", "Dalmette", "Trichet"]

# Les cinq chiffres de tête. Chacun pointe une ligne réelle de l'indice : la
# valeur affichée est relue du fichier de résultats, jamais recopiée.
VEDETTES = [
    (4, "eau", "#2a78d6", False),          # accès à l'eau de boisson
    (3, "assainissement", "#6b4fa8", False),
    (5, "electricite", "#c98a2e", False),
    (108, "alimentaire", "#b4451f", True),  # insécurité : le haut est mauvais
]


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
    res = None
    if _trouver("resultats.json"):
        with open(_trouver("resultats.json"), encoding="utf-8") as f:
            res = json.load(f)
    return res


def nom_indic(r):
    if i18n.get_lang() == "fr" and r.get("indicateur_fr"):
        return r["indicateur_fr"]
    return r["indicateur"]


def score_pondere(res, cible):
    """Moyenne pondérée de tous les indicateurs scorés, pour une cible.

    Les indicateurs non calculés sont exclus du dénominateur, jamais comptés
    comme des zéros — même règle que dans les pages de dimension, et elle doit
    le rester : deux moyennes calculées différemment sur le même site
    finiraient par ne plus concorder, et personne ne saurait laquelle croire.
    """
    num = den = 0.0
    for r in res:
        sc = (r.get("scores_corriges") or {}).get(cible)
        if sc is None:
            continue
        p = r.get("ponderation") or 1
        num += sc * p
        den += p
    return (num / den) if den else None


def _carte_vignette(res):
    valeurs = {s: score_pondere(res, s) for s in SECTIONS}
    valeurs = {s: (round(v, 2) if v is not None else None)
               for s, v in valeurs.items()}
    dispo = [v for v in valeurs.values() if v is not None]
    if not dispo:
        return None, 0
    seuils = map_render.nice_thresholds(dispo)
    hauteur = 620
    svg, seuils_ret, _m = map_render.render_map_svg(
        valeurs, {s: 1 for s in SECTIONS}, seuils, width=1040, height=hauteur,
        polarity="eleve_bon", unite="")
    legende = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:6px;'
        f'margin-right:14px"><span style="width:18px;height:11px;'
        f'border-radius:3px;background:{c};box-shadow:inset 0 0 0 1px '
        f'rgba(0,0,0,.12)"></span><span style="font-size:12px;'
        f'color:#52514e">{lab}</span></span>'
        for c, lab in map_render.legend_items(seuils_ret, "eleve_bon", ""))
    return ('<div style="font-family:system-ui,-apple-system,\'Segoe UI\','
            'sans-serif;background:#ffffff"><div style="margin:0 0 6px">'
            f'{legende}</div>{svg}</div>'), hauteur


def _menages_enquetes(res):
    """Le nombre de ménages enquêtés.

    Pas de `@st.cache_data` ici : le cache devrait hacher `res`, une liste de
    128 dictionnaires, ce qui coûterait plus cher que le calcul lui-même.

    L'ancienne version affichait `max(n)` sur toutes les lignes de résultat,
    soit 2 700 — qui est le nombre d'ENFANTS de la ligne 24 (enregistrement
    des naissances), pas de ménages. Le site annonçait donc en vitrine plus du
    double du vrai chiffre.

    Toutes les lignes ne comptent pas la même chose : la plupart comptent des
    ménages, quelques-unes comptent des individus. On borne donc le max par
    les effectifs par section communale, qui, eux, comptent des questionnaires
    et rien d'autre. Une ligne qui déclare nettement plus que ce total ne
    compte pas des ménages, et sort du calcul.

    Reste l'écart entre les deux : 1 211 questionnaires collectés, 1 206
    rattachés à une section communale. C'est le premier chiffre — le nombre de
    foyers réellement interrogés — qui est annoncé ici.
    """
    p = _trouver("ventilation.json")
    if not p or not res:
        return None
    with open(p, encoding="utf-8") as f:
        eff = (json.load(f) or {}).get("effectifs") or {}
    rattaches = sum((d or {}).get("Total") or 0 for d in eff.values())
    if not rattaches:
        return None
    plafond = rattaches * 1.1
    plausibles = [n for n in ((r.get("n") or {}).get("Total") for r in res)
                  if n and n <= plafond]
    return max(plausibles) if plausibles else rattaches


_STYLE_PERIMETRE = """
<style>
  .a-perimetre { display:flex; gap:34px; flex-wrap:wrap; margin:16px 0 6px;
                 padding:0 0 2px; }
  .a-per-item  { display:flex; align-items:baseline; gap:9px; }
  .a-per-val   { font-size:30px; font-weight:700; color:#101728;
                 letter-spacing:-.025em; font-variant-numeric:tabular-nums;
                 line-height:1; }
  .a-per-lib   { font-size:14.5px; color:#5a6478; }
  .a-local     { font-size:15.5px; color:#3c4761; line-height:1.6;
                 max-width:88ch; margin:6px 0 4px; }
  .a-hist-t    { font-size:13px; letter-spacing:.06em; text-transform:uppercase;
                 font-weight:700; color:#1f7a5a; margin:0 0 4px; }
  .a-hist-p    { font-size:15.5px; color:#3c4761; line-height:1.65;
                 max-width:92ch; margin:0 0 15px; }
  .a-hist-p:last-child { margin-bottom:2px; }
  .a-hist-p b  { color:#101728; font-weight:650; }
</style>
"""


def render(actualites=None):
    res = _charger()
    st.markdown(_STYLE_PERIMETRE, unsafe_allow_html=True)

    # ------------------------------------------------------------- bandeau
    # Ni logo ni pavé de bienvenue : la marque est en permanence dans la
    # colonne de gauche, et un écran d'accueil qui commence par se présenter
    # lui-même repousse le premier fait vers le bas de page.
    st.markdown(
        f'<div style="font-size:31px;font-weight:700;color:#101728;'
        f'letter-spacing:-.025em;line-height:1.15;margin:2px 0 2px">'
        f'<span style="color:#1f7a5a">APRI</span> — {T("a_titre_court")}</div>',
        unsafe_allow_html=True)

    if not res:
        st.info(T("e_absent"))
        st.stop()

    scores_sec = {s: score_pondere(res, s) for s in SECTIONS}
    scores_sec = {s: v for s, v in scores_sec.items() if v is not None}

    # --------------------------------------------------------- le périmètre
    # Cinq tuiles disaient cinq chiffres dont trois n'apprenaient rien à qui
    # arrive sur le site. Il en reste trois, sur une ligne, suivis de la
    # localisation : de quel territoire parle-t-on, et sur quelle base.
    #
    # ATTENTION AU NOMBRE DE MÉNAGES. L'ancienne tuile affichait le maximum
    # des effectifs de toutes les lignes, soit 2 700 — qui est le nombre
    # d'ENFANTS de la ligne 24 (enregistrement des naissances), pas de
    # ménages. Le bon dénominateur est le nombre de questionnaires, lu dans
    # les effectifs par section : ne pas revenir à un max() sur les lignes.
    st.markdown(
        '<div class="a-perimetre">'
        + ''.join(
            f'<div class="a-per-item"><span class="a-per-val">{_e(v)}</span>'
            f'<span class="a-per-lib">{_e(l)}</span></div>'
            for v, l in [(str(len(SECTIONS)), T("a_p_sections")),
                         ("2", T("a_p_departements")),
                         (_fmt(_menages_enquetes(res), 0), T("a_p_menages"))])
        + '</div>'
        f'<p class="a-local">{T("a_localisation")}</p>',
        unsafe_allow_html=True)

    # -------------------------------------------------------- l'histoire
    # Quatre volets « quoi / où / comment / pourquoi » disaient les mêmes
    # choses en trop peu de mots pour qu'on comprenne de quoi il s'agit. Un
    # récit court les remplace : d'où vient la démarche, ce qu'elle mesure,
    # comment elle est construite, et ce qu'elle ne prétend pas dire — cette
    # dernière partie n'est pas une précaution de style, c'est la condition
    # pour que les chiffres soient utilisés correctement.
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc ambre">{T("a_histoire")}</div>',
                    unsafe_allow_html=True)
        st.markdown(
            ''.join(f'<p class="a-hist-p"><b>{_e(T("a_h_" + c + "_t"))}</b> '
                    f'{T("a_h_" + c)}</p>'
                    for c in ("origine", "mesure", "construction", "portee")),
            unsafe_allow_html=True)

    # ------------------------------------------------- résultats saillants
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("a_bloc_saillants")}</div>',
                    unsafe_allow_html=True)
        st.markdown(
            f'<p style="font-size:15.5px;line-height:1.6;color:#3c4761;'
            f'margin:4px 0 12px;max-width:92ch">{T("a_bloc_saillants_texte")}'
            f'</p>', unsafe_allow_html=True)
        par_ligne = {r["ligne"]: r for r in res}
        cartes = []
        for lg, cle, coul, inverse in VEDETTES:
            r = par_ligne.get(lg)
            if not r:
                continue
            val = (r.get("valeurs") or {}).get("Total")
            sc = (r.get("scores_corriges") or {}).get("Total")
            cartes.append(
                f'<div style="flex:1 1 210px;min-width:190px;background:#fff;'
                f'border:1px solid #e7ecf3;border-left:4px solid {coul};'
                f'border-radius:13px;padding:14px 16px">'
                f'<div style="font-size:34px;font-weight:700;color:{coul};'
                f'font-variant-numeric:tabular-nums;letter-spacing:-.03em;'
                f'line-height:1.05">{_fmt(val)}'
                f'<span style="font-size:17px;margin-left:2px">%</span></div>'
                f'<div style="font-size:13.5px;color:#3c4761;font-weight:600;'
                f'margin-top:5px;line-height:1.35">{_e(T("a_v_" + cle))}</div>'
                f'<div style="font-size:12px;color:#8a93a5;margin-top:3px">'
                f'{_e(T("a_v_score", s=sc))} · {_e(T("a_v_ligne", n=lg))}'
                f'</div></div>')
        st.markdown('<div style="display:flex;gap:12px;flex-wrap:wrap">'
                    + ''.join(cartes) + '</div>', unsafe_allow_html=True)
        st.caption(T("a_bloc_saillants_note"))

    # ------------------------------------------------------------- la carte
    # Le diagramme en barres est retiré. Il disait la même chose que la carte
    # — le classement des dix sections — mais sans dire OÙ, et son échelle
    # arrondissait des écarts de trois dixièmes en barres identiques. La carte
    # porte le score ET la géographie ; deux vues du même chiffre, dont l'une
    # en dit moins, ne valent pas deux blocs.
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc vert">{T("a_bloc_carte")}</div>',
                    unsafe_allow_html=True)
        carte = _carte_vignette(res)
        if carte[0]:
            components.html(carte[0], height=carte[1] + 40, scrolling=False)
        st.caption(T("a_bloc_carte_note",
                     h=max(scores_sec, key=scores_sec.get),
                     b=min(scores_sec, key=scores_sec.get)))

    if actualites is not None:
        actualites()

    st.caption(T("e_source"))
    st.caption(T("credit"))
