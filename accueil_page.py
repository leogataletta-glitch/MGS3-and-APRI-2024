"""Page d'accueil — la vue d'ensemble de l'APRI.

L'entrée d'un tableau de bord institutionnel ne doit pas être un menu : elle
doit répondre, en un écran, à « de quoi parle ce site, sur quel territoire,
avec quelles données, et qu'est-ce que ça donne ». Le reste — le détail par
dimension, la méthode, les téléchargements — vient après, pour qui veut
creuser.

D'où l'ordre de cette page : le périmètre d'abord (combien de sections,
combien de ménages, combien d'indicateurs), les résultats saillants ensuite,
le classement des sections, et enfin la carte et les ressources.

TOUS LES CHIFFRES SONT CALCULÉS, AUCUN N'EST ÉCRIT EN DUR. Une page d'accueil
qui affiche des nombres figés devient fausse à la première mise à jour des
données, et personne ne s'en aperçoit — c'est le pire défaut possible pour une
vitrine.
"""

import json
import os

import streamlit as st
import streamlit.components.v1 as components

import assets
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
    hauteur = 430
    svg, seuils_ret, _m = map_render.render_map_svg(
        valeurs, {s: 1 for s in SECTIONS}, seuils, width=560, height=hauteur,
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


def _barres_sections_svg(scores, largeur=880):
    """Classement des sections, barres verticales, du meilleur au moins bon.

    Une seule teinte : il n'y a qu'une grandeur. Le score est écrit au-dessus
    de chaque barre — à cette hauteur, l'œil ne lit pas un écart de trois
    dixièmes, et c'est justement l'ordre de grandeur qui sépare ces
    territoires.
    """
    ordre = sorted(scores.items(), key=lambda kv: -kv[1])
    H, TOP, BAS, GAUCHE = 300, 26, 86, 40
    plot_h = H - TOP - BAS
    pas = (largeur - GAUCHE - 16) / max(len(ordre), 1)
    barre = pas * 0.56
    vmax = 10.0

    parts = []
    for g in (0, 2, 4, 6, 8, 10):
        y = TOP + plot_h * (1 - g / vmax)
        parts.append(f'<line x1="{GAUCHE}" y1="{y:.1f}" x2="{largeur - 16}" '
                     f'y2="{y:.1f}" stroke="#eef2f7" stroke-width="1"/>')
        parts.append(f'<text class="ag" x="{GAUCHE - 9}" y="{y + 4:.1f}" '
                     f'text-anchor="end">{g}</text>')

    for i, (sec, v) in enumerate(ordre):
        h = plot_h * v / vmax
        x = GAUCHE + i * pas + (pas - barre) / 2
        y = TOP + plot_h - h
        parts.append(
            f'<g><title>{_e(sec)} — {v:.2f} / 10</title>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{barre:.1f}" '
            f'height="{max(h, 1):.1f}" rx="3" fill="#1f7a5a"/></g>')
        parts.append(f'<text class="av" x="{x + barre / 2:.1f}" '
                     f'y="{y - 7:.1f}" text-anchor="middle">'
                     f'{v:.2f}</text>'.replace('.', ','))
        parts.append(
            f'<text class="al" transform="translate({x + barre / 2:.1f},'
            f'{H - BAS + 12}) rotate(-38)" text-anchor="end">'
            f'{_e(sec)}</text>')

    return f"""<svg viewBox="0 0 {largeur} {H}" width="100%"
     style="max-width:{largeur}px;display:block" role="img">
  <style>
    .ag{{font:11px system-ui,-apple-system,sans-serif;fill:#a9b0be;
        font-variant-numeric:tabular-nums}}
    .av{{font:700 12.5px system-ui,-apple-system,sans-serif;fill:#101728;
        font-variant-numeric:tabular-nums}}
    .al{{font:12px system-ui,-apple-system,sans-serif;fill:#52514e}}
  </style>
  {''.join(parts)}
</svg>"""


def _tuile(icone, lib, val, unite, sous):
    return (f'<div style="flex:1 1 190px;min-width:170px;background:#fff;'
            f'border:1px solid #e7ecf3;border-radius:14px;padding:15px 17px;'
            f'box-shadow:0 1px 2px rgba(16,23,40,.04)">'
            f'<div style="font-size:19px;line-height:1">{icone}</div>'
            f'<div style="font-size:29px;font-weight:700;color:#101728;'
            f'font-variant-numeric:tabular-nums;margin-top:6px;'
            f'letter-spacing:-.02em">{_e(val)}'
            + (f'<span style="font-size:15px;font-weight:600;color:#6b7590;'
               f'margin-left:3px">{_e(unite)}</span>' if unite else '')
            + f'</div>'
            f'<div style="font-size:13.5px;color:#3c4761;font-weight:600;'
            f'margin-top:2px">{_e(lib)}</div>'
            f'<div style="font-size:12px;color:#8a93a5;margin-top:1px">'
            f'{_e(sous)}</div></div>')


def render():
    res = _charger()

    # ------------------------------------------------------------- bandeau
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:18px;margin:2px 0 4px">'
        f'<img src="data:image/png;base64,{assets.LOGO_APRI}" '
        f'style="width:96px">'
        f'<div><div style="font-size:31px;font-weight:700;color:#101728;'
        f'letter-spacing:-.025em;line-height:1.15">{T("a_bienvenue")} '
        f'<span style="color:#1f7a5a">APRI</span></div>'
        f'<div style="font-size:15px;color:#6b7590;margin-top:2px">'
        f'{T("a_accroche")}</div></div></div>',
        unsafe_allow_html=True)

    if not res:
        st.info(T("e_absent"))
        st.stop()

    scores_sec = {s: score_pondere(res, s) for s in SECTIONS}
    scores_sec = {s: v for s, v in scores_sec.items() if v is not None}
    global_ = score_pondere(res, "Total")
    n_scores = sum(1 for r in res
                   if (r.get("scores_corriges") or {}).get("Total") is not None)
    base = max((r.get("n") or {}).get("Total") or 0 for r in res)

    # --------------------------------------------------------- le périmètre
    st.markdown(
        '<div style="display:flex;gap:13px;flex-wrap:wrap;margin:14px 0 4px">'
        + _tuile("◉", T("a_p_sections"), str(len(SECTIONS)), "",
                 T("a_p_sections_sous"))
        + _tuile("◈", T("a_p_departements"), "2", "",
                 T("a_p_departements_sous"))
        + _tuile("▤", T("a_p_indicateurs"), f"{n_scores}", f"/ {len(res)}",
                 T("a_p_indicateurs_sous"))
        + _tuile("◍", T("a_p_menages"), _fmt(base, 0), "",
                 T("a_p_menages_sous"))
        + _tuile("★", T("a_p_score"), _fmt(global_, 2), "/ 10",
                 T("a_p_score_sous"))
        + '</div>', unsafe_allow_html=True)

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

    # ------------------------------------------------ classement + carte
    gauche, droite = st.columns([3, 2], gap="medium")
    with gauche:
        with st.container(border=True):
            st.markdown(
                f'<div class="titre-bloc vert">{T("a_bloc_classement")}</div>',
                unsafe_allow_html=True)
            svg = _barres_sections_svg(scores_sec)
            components.html(
                '<div style="background:#ffffff;font-family:system-ui,'
                "-apple-system,'Segoe UI',sans-serif\">" + svg + "</div>",
                height=315, scrolling=False)
            st.caption(T("a_bloc_classement_note",
                         h=max(scores_sec, key=scores_sec.get),
                         b=min(scores_sec, key=scores_sec.get)))

    with droite:
        with st.container(border=True):
            st.markdown(f'<div class="titre-bloc">{T("a_bloc_carte")}</div>',
                        unsafe_allow_html=True)
            carte = _carte_vignette(res)
            if carte[0]:
                components.html(carte[0], height=carte[1] + 34,
                                scrolling=False)
            st.caption(T("a_bloc_carte_note"))

    # ---------------------------------------------------- par où commencer
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc ambre">{T("a_bloc_guide")}</div>',
                    unsafe_allow_html=True)
        pistes = [
            ("dim3", T("a_guide_env"), "#2a6b3f"),
            ("synthese", T("a_guide_synthese"), "#1a6bb0"),
            ("actions", T("a_guide_actions"), "#a8690a"),
            ("methodologie", T("a_guide_methodo"), "#6b4fa8"),
        ]
        st.markdown(
            '<div style="display:flex;gap:12px;flex-wrap:wrap">'
            + ''.join(
                f'<div style="flex:1 1 230px;min-width:210px;'
                f'border-left:3px solid {c};padding:2px 0 2px 13px">'
                f'<div style="font-size:12px;letter-spacing:.06em;'
                f'text-transform:uppercase;color:{c};font-weight:700">'
                f'{_e(T(cle))}</div>'
                f'<div style="font-size:14.5px;color:#3c4761;line-height:1.55;'
                f'margin-top:2px">{_e(txt)}</div></div>'
                for cle, txt, c in pistes)
            + '</div>', unsafe_allow_html=True)

    st.caption(T("e_source"))
    st.caption(T("credit"))
