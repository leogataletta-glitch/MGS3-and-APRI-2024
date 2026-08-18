"""Onglet « Synthèse par groupe ou localité ».

Les six onglets de dimension répondent à « que vaut ce territoire sur l'eau,
sur la forêt, sur la santé ». Celui-ci répond à la question inverse, et c'est
souvent la vraie : « que vit ce groupe, ou cette section, sur l'ensemble des
dimensions ». Un même score d'ensemble peut recouvrir un territoire faible
partout ou un territoire effondré sur un seul volet, et ces deux situations
n'appellent pas la même réponse.

DEUX LECTURES, UN SEUL SÉLECTEUR

On choisit une SECTION COMMUNALE ou un GROUPE — femmes, jeunes, catégories
socio-économiques, plus de 60 ans. Les deux ne se lisent pas de la même façon
et le module le dit :

  · une section se compare aux neuf autres, sur des indicateurs dont
    beaucoup sont territoriaux — la forêt, la pluie, la température ne varient
    pas selon le sexe du répondant ;
  · un groupe se compare à l'ensemble des répondants, et seuls les
    indicateurs issus de l'enquête ménage ont quelque chose à en dire. Les
    indicateurs satellitaires sont identiques pour tous les groupes d'une même
    section, par construction : les afficher comme un écart nul serait
    trompeur, ils sont donc écartés de la lecture par groupe.

L'ÉCART EST NEUTRE

Un écart n'est pas coloré en bien ou en mal. Sur « part des ménages qui
utilisent le charbon », être au-dessus de la moyenne est mauvais ; sur « accès
à l'électricité », c'est bon. Le sens dépend de l'indicateur, et le score APRI
le porte déjà. Le graphique ne montre donc que la direction et l'ampleur.
"""

import json
import os

import streamlit as st
import streamlit.components.v1 as components

import filtres
import i18n
import map_render
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

SECTIONS = ["Anse à Drick", "Barbois", "Dumont", "Débouchette", "Mouline",
            "Quentin", "Beaulieu", "Blactote", "Dalmette", "Trichet"]
GROUPES = ["Femme", "Homme", "<25", "25-39", "40-59", "60+",
           "Cat A", "Cat B", "Cat C"]
# Le paysage est une troisième façon de couper la population, et la seule des
# trois qui soit AUSSI une propriété du lieu : les indicateurs satellitaires
# portent donc une valeur pour lui, contrairement au sexe ou à l'âge.
PAYSAGES = ["Littoral", "Montagne"]
GROUPE_CLE = {"Homme": "hommes", "Femme": "femmes", "Cat A": "cat_a",
              "Cat B": "cat_b", "Cat C": "cat_c", "<25": "age_25",
              "25-39": "age_25_39", "40-59": "age_40_59", "60+": "age_60"}

DIMENSIONS = [
    ("dim1", "I. PHYSICAL AND INFRASTRUCTURAL DIMENSION", "#1a6bb0"),
    ("dim2", "II. INSTITUTIONAL, TECHNOLOGICAL, AND GOVERNANCE  DIMENSION", "#6b4fa8"),
    ("dim3", "III.  ENVIRONMENTAL AND ECOLOGICAL DIMENSION", "#2a6b3f"),
    ("dim4", "IV. ECONOMIC, LIVELIHOODS, AND FOOD SECURITY DIMENSION", "#a8690a"),
    ("dim5", "V. SOCIAL AND COMMUNITY DIMENSION", "#0b7f74"),
    ("dim6", "VI. HUMAN DIMENSION", "#b4451f"),
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


def _libelle(cible, mode):
    if mode == "section":
        return cible
    if mode == "paysage":
        return T("pay_" + cible)
    return T(GROUPE_CLE.get(cible, cible))


def _score(lignes, cible):
    num = den = 0.0
    for r in lignes:
        sc = (r.get("scores_corriges") or {}).get(cible)
        if sc is None:
            continue
        p = r.get("ponderation") or 1
        num += sc * p
        den += p
    return (num / den) if den else None


def _profil(res, cible, mode):
    """Score de chaque dimension pour la cible, et pour l'ensemble.

    En lecture par groupe, les indicateurs territoriaux sont écartés : ils
    portent la même valeur pour tous les groupes, et un écart nul affiché à
    côté d'écarts réels ferait croire à une égalité mesurée là où il n'y a
    qu'une absence de ventilation.
    """
    out = []
    for cle, dim, coul in DIMENSIONS:
        lignes = [r for r in res if r["dimension"] == dim]
        # Seule la lecture par GROUPE écarte les indicateurs territoriaux.
        # Par paysage, ils gardent tout leur sens : littoral et montagne ne
        # reçoivent ni la même pluie ni le même couvert.
        if mode == "groupe":
            lignes = [r for r in lignes if (r.get("source") or "menage") == "menage"]
        v = _score(lignes, cible)
        ref = _score(lignes, "Total")
        n = sum(1 for r in lignes
                if (r.get("scores_corriges") or {}).get(cible) is not None)
        out.append({"cle": cle, "couleur": coul, "valeur": v,
                    "reference": ref, "n": n})
    return out


# ----------------------------------------------------------------- graphique
def _haltere_svg(profil, mode, largeur=1000):
    """Un graphique en haltères : la référence, la cible, et le trait entre.

    Deux points reliés plutôt que deux barres côte à côte. Des barres
    appariées obligent l'œil à comparer deux longueurs partant du même bord ;
    l'haltère montre directement ce qu'on cherche — la distance, et de quel
    côté elle penche. Le trait EST l'écart.
    """
    lignes = [p for p in profil if p["valeur"] is not None
              and p["reference"] is not None]
    if not lignes:
        return ""
    H_LIGNE, TOP, BAS, GAUCHE, DROITE = 46, 34, 40, 250, 40
    H = TOP + BAS + H_LIGNE * len(lignes)
    x0, x1 = GAUCHE, largeur - DROITE

    def x_de(v):
        return x0 + (x1 - x0) * max(0.0, min(v, 10.0)) / 10.0

    parts = []
    for g in range(0, 11, 2):
        x = x_de(g)
        parts.append(f'<line x1="{x:.1f}" y1="{TOP - 12}" x2="{x:.1f}" '
                     f'y2="{H - BAS + 6}" stroke="#eef2f7" stroke-width="1"/>')
        parts.append(f'<text class="sg" x="{x:.1f}" y="{TOP - 18}" '
                     f'text-anchor="middle">{g}</text>')

    for i, p in enumerate(lignes):
        y = TOP + H_LIGNE * i + H_LIGNE / 2
        xr, xv = x_de(p["reference"]), x_de(p["valeur"])
        ecart = p["valeur"] - p["reference"]
        parts.append(f'<text class="sl" x="{GAUCHE - 16}" y="{y + 5:.1f}" '
                     f'text-anchor="end">{_e(T(p["cle"]))}</text>')
        parts.append(f'<line x1="{min(xr, xv):.1f}" y1="{y:.1f}" '
                     f'x2="{max(xr, xv):.1f}" y2="{y:.1f}" '
                     f'stroke="{p["couleur"]}" stroke-width="3" '
                     f'stroke-opacity="0.34" stroke-linecap="round"/>')
        parts.append(f'<circle cx="{xr:.1f}" cy="{y:.1f}" r="5.5" '
                     f'fill="#ffffff" stroke="#8a93a5" stroke-width="2">'
                     f'<title>{_e(T("s_reference"))} — {p["reference"]:.2f}'
                     f'</title></circle>')
        parts.append(f'<circle cx="{xv:.1f}" cy="{y:.1f}" r="7" '
                     f'fill="{p["couleur"]}"><title>{p["valeur"]:.2f}</title>'
                     f'</circle>')
        signe = "+" if ecart > 0 else ""
        parts.append(f'<text class="se" x="{x1 + 8}" y="{y + 5:.1f}">'
                     f'{signe}{ecart:.2f}</text>')

    return f"""<svg viewBox="0 0 {largeur} {H}" width="100%"
     style="max-width:{largeur}px;display:block" role="img">
  <style>
    .sg{{font:11px system-ui,-apple-system,sans-serif;fill:#a9b0be;
        font-variant-numeric:tabular-nums}}
    .sl{{font:600 14px system-ui,-apple-system,sans-serif;fill:#3c4761}}
    .se{{font:700 13px system-ui,-apple-system,sans-serif;fill:#6b7590;
        font-variant-numeric:tabular-nums}}
  </style>
  {''.join(parts)}
</svg>"""


def _tableau_ecarts(res, cible, mode, sens, limite=12):
    """Les indicateurs où la cible s'écarte le plus de l'ensemble.

    L'écart est affiché SANS couleur de valeur. Sur « part des ménages qui
    utilisent le charbon », être au-dessus de la moyenne est mauvais ; sur
    « accès à l'électricité », c'est bon. Le sens dépend de l'indicateur, et
    le score APRI le porte déjà — le tableau ne montre que la direction.
    """
    lot = []
    for r in res:
        if mode == "groupe" and (r.get("source") or "menage") != "menage":
            continue
        sc = (r.get("scores_corriges") or {}).get(cible)
        ref = (r.get("scores_corriges") or {}).get("Total")
        if sc is None or ref is None:
            continue
        lot.append((sc - ref, r, sc, ref))
    lot.sort(key=lambda t: t[0])
    choisis = lot[:limite] if sens == "bas" else lot[::-1][:limite]
    if not choisis:
        return ""
    entetes = [T("d_col_ligne"), T("d_col_indicateur"), T("s_col_cible"),
               T("s_col_ref"), T("s_col_ecart")]
    out = ['<div style="overflow-x:auto"><table style="width:100%;'
           'border-collapse:collapse;font-size:14.5px">',
           '<tr>' + ''.join(
               f'<th style="text-align:{"left" if i < 2 else "right"};'
               f'padding:9px 10px;border-bottom:2px solid #e6ecf4;'
               f'font-size:11.5px;letter-spacing:.05em;text-transform:uppercase;'
               f'color:#6b7590;font-weight:700">{_e(h)}</th>'
               for i, h in enumerate(entetes)) + '</tr>']
    C = ('padding:9px 10px;border-bottom:1px solid #f0f4f9;text-align:right;'
         'font-variant-numeric:tabular-nums')
    for ecart, r, sc, ref in choisis:
        signe = "+" if ecart > 0 else ""
        out.append(
            f'<tr><td style="padding:9px 10px;border-bottom:1px solid #f0f4f9;'
            f'color:#8a93a5;font-variant-numeric:tabular-nums">{r["ligne"]}</td>'
            f'<td style="padding:9px 10px;border-bottom:1px solid #f0f4f9">'
            f'{_e(nom_indic(r))}</td>'
            f'<td style="{C};font-weight:700">{sc}</td>'
            f'<td style="{C};color:#8a93a5">{ref}</td>'
            f'<td style="{C};font-weight:700;color:#3c4761">'
            f'{signe}{_fmt(ecart, 1)}</td></tr>')
    out.append('</table></div>')
    return ''.join(out)


def render():
    res, _vent = _charger()

    st.title(T("mode_synthese"))
    st.markdown(
        '<p style="font-size:12.5px;color:#6b7590;letter-spacing:.06em;'
        'text-transform:uppercase;margin:-8px 0 0 2px;font-weight:600">'
        + T("syn_sous_titre") + "</p>", unsafe_allow_html=True)

    if not res:
        st.info(T("e_absent"))
        st.stop()

    st.markdown(
        '<div style="background:#fff;border:1px solid #e3eaf3;border-left:5px '
        'solid #1a6bb0;border-radius:14px;padding:13px 17px;font-size:16px;'
        'color:#3c4761;box-shadow:0 1px 2px rgba(16,23,40,.05),'
        '0 8px 20px rgba(16,23,40,.06);margin:10px 0 6px;max-width:96ch">'
        + T("syn_intro") + "</div>", unsafe_allow_html=True)

    # Le filtre de la colonne pré-remplit le sélecteur : on arrive ici avec ce
    # qu'on regardait ailleurs, sans avoir à le rechoisir. Le sélecteur reste
    # néanmoins, parce que cette page-ci sert précisément à comparer plusieurs
    # cibles d'affilée.
    _modes = ["section", "groupe", "paysage"]
    _pref_mode = ("paysage" if filtres.paysage() != filtres.TOUS_P
                  else "groupe" if filtres.groupe() != filtres.TOUS
                  else "section")
    c1, c2 = st.columns([1, 2])
    with c1:
        mode = st.radio(T("s_mode"), _modes,
                        format_func=lambda m: T("s_mode_" + m),
                        horizontal=True,
                        index=_modes.index(_pref_mode),
                        key=f"syn_mode_{i18n.get_lang()}")
    with c2:
        options = (SECTIONS if mode == "section"
                   else PAYSAGES if mode == "paysage" else GROUPES)
        _pref = (filtres.section() if mode == "section"
                 else filtres.paysage() if mode == "paysage"
                 else filtres.groupe())
        _idx = options.index(_pref) if _pref in options else 0
        cible = st.selectbox(T("s_cible"), options, index=_idx,
                             format_func=lambda c: _libelle(c, mode),
                             key=f"syn_cible_{mode}_{i18n.get_lang()}")

    if mode == "groupe":
        st.caption(T("s_note_groupe"))
    elif mode == "paysage":
        st.caption(T("s_note_paysage"))

    profil = _profil(res, cible, mode)
    dispo = [p for p in profil if p["valeur"] is not None]
    global_cible = (sum(p["valeur"] for p in dispo) / len(dispo)
                    if dispo else None)
    global_ref = (sum(p["reference"] for p in dispo) / len(dispo)
                  if dispo else None)

    # -------------------------------------------------------- vue d'ensemble
    with st.container(border=True):
        st.markdown(
            f'<div class="titre-bloc">{T("syn_bloc_profil", c=_libelle(cible, mode))}</div>',
            unsafe_allow_html=True)
        forts = sorted(dispo, key=lambda p: p["valeur"] - p["reference"])
        for col, lib, val, unite, sous, coul in zip(
                st.columns(4),
                [T("s_c_score"), T("s_c_ecart"), T("s_c_faible"),
                 T("s_c_fort")],
                [_fmt(global_cible, 2),
                 (("+" if global_cible and global_ref
                   and global_cible > global_ref else "")
                  + _fmt((global_cible - global_ref)
                         if (global_cible and global_ref) else None, 2)),
                 T(forts[0]["cle"] + "_court") if forts else "—",
                 T(forts[-1]["cle"] + "_court") if forts else "—"],
                ["/ 10", "", "", ""],
                [T("s_c_score_sous"), T("s_c_ecart_sous"),
                 T("s_c_faible_sous",
                   v=_fmt(forts[0]["valeur"] - forts[0]["reference"], 2))
                 if forts else "",
                 T("s_c_fort_sous",
                   v=_fmt(forts[-1]["valeur"] - forts[-1]["reference"], 2))
                 if forts else ""],
                ["#1a6bb0", "#6b7590", "#b4451f", "#2a6b3f"]):
            with col:
                st.markdown(
                    map_render.cartouche_html(lib, val, unite, sous,
                                              couleur=coul),
                    unsafe_allow_html=True)

        svg = _haltere_svg(profil, mode)
        if svg:
            components.html(
                '<div style="background:#ffffff;font-family:system-ui,'
                "-apple-system,'Segoe UI',sans-serif\">" + svg + "</div>",
                height=TOPHAUT(profil), scrolling=False)
        st.caption(T("s_haltere_note", c=_libelle(cible, mode)))

    # ------------------------------------------------------- les écarts
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc ambre">{T("s_bloc_bas")}</div>',
                    unsafe_allow_html=True)
        st.caption(T("s_bloc_bas_note"))
        st.markdown(_tableau_ecarts(res, cible, mode, "bas"),
                    unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc vert">{T("s_bloc_haut")}</div>',
                    unsafe_allow_html=True)
        st.caption(T("s_bloc_haut_note"))
        st.markdown(_tableau_ecarts(res, cible, mode, "haut"),
                    unsafe_allow_html=True)

    st.caption(T("e_source"))
    st.caption(T("credit"))


def TOPHAUT(profil):
    """Hauteur de l'iframe : elle suit le nombre de lignes réellement tracées."""
    n = len([p for p in profil if p["valeur"] is not None
             and p["reference"] is not None])
    return 34 + 40 + 46 * max(n, 1) + 16
