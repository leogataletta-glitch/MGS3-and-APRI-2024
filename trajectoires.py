"""Trajectoires — ce que vingt-cinq ans de satellite disent du paysage.

POURQUOI CETTE PAGE EXISTE

Tout le reste du site est une photographie : l'enquête a eu lieu en 2024, les
indices décrivent un état. Or trois des jeux de données satellitaires sont des
SÉRIES — la forêt depuis 2000, la pluie depuis 1981, la température de surface
depuis 2001 — et le site les utilisait comme des instantanés. C'est le seul
endroit du dispositif où une trajectoire existe vraiment ; elle méritait sa
page.

CE QUE LA PAGE MONTRE, ET QUE RIEN D'AUTRE NE MONTRAIT

  · la perte de couvert forestier année par année, et son fait le plus dur :
    70 % de la perte de vingt-cinq ans s'est produite en TROIS ans, 2016 à
    2018 — l'ouragan Matthew d'octobre 2016 et ce qui a suivi ;
  · quarante-cinq ans de pluie, et l'écart à la normale 1991-2020 ;
  · vingt-cinq ans de température de surface en saison sèche ;
  · sept ans de vigueur végétale, la série la plus courte, et c'est dit.

AUCUNE DE CES COURBES N'EST UN SCORE. Ce sont des mesures physiques, en
hectares, en millimètres, en degrés. Les scores de résilience vivent ailleurs ;
ici on regarde ce qui bouge, et à quelle vitesse.

RÈGLES DE DESSIN, TENUES VOLONTAIREMENT COURTES
  · un seul axe par graphique, jamais deux échelles superposées ;
  · une seule teinte pour une grandeur ; la couleur ne sert à distinguer que
    ce qui est de nature différente — ici les années de choc ;
  · trait de 2 px, extrémités arrondies, grille discrète, étiquettes
    sélectives : on nomme les extrêmes et les repères, pas chaque point ;
  · chaque marque porte son année et sa valeur en infobulle native.
"""

import json
import os

import streamlit as st

import i18n
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"
VERT, BLEU, AMBRE, ROUGE, GRIS = ("#1a8a4f", "#2166ac", "#d1730c",
                                  "#c33a24", "#9aa4b5")
BORD, GRILLE = "#e3eaf3", "#eef2f7"

SECTIONS = ["Anse à Drick", "Barbois", "Dumont", "Débouchette", "Mouline",
            "Quentin", "Beaulieu", "Blactote", "Dalmette", "Trichet"]

TEXTES = {
    "mode_trajectoires": {"en": "Trajectories", "fr": "Trajectoires"},
    "tj_titre": {"en": "Twenty-five years of satellite imagery",
                 "fr": "Vingt-cinq ans d'imagerie satellitaire"},
    "tj_sous": {"en": "What moves, and how fast",
                "fr": "Ce qui bouge, et à quelle vitesse"},
    "tj_intro": {
        "en": "Everything else on this site is a snapshot: the survey took "
              "place in 2024. These four series are not, they run from 1981, "
              "2001 or 2019 to today. None of them is a resilience score: they "
              "are hectares, millimetres and degrees.",
        "fr": "Tout le reste du site est un instantané : l'enquête a eu lieu "
              "en 2024. Ces quatre séries ne le sont pas, elles courent "
              "depuis 1981, 2001 ou 2019 jusqu'à aujourd'hui. Aucune n'est un "
              "score de résilience : ce sont des hectares, des millimètres et "
              "des degrés."},
    "tj_perimetre": {"en": "Scope", "fr": "Périmètre"},
    "tj_toutes": {"en": "The ten sections together",
                  "fr": "Les dix sections réunies"},
    "tj_absent": {"en": "Satellite series are missing.",
                  "fr": "Les séries satellitaires sont absentes."},

    # ---------------- forêt
    "tj_f_t": {"en": "Forest cover, annual loss",
               "fr": "Le couvert forestier, perte annuelle"},
    "tj_f_x": {
        "en": "Hectares of tree cover lost each year, canopy threshold 30 %. "
              "Source: University of Maryland / Hansen, 2000–2025.",
        "fr": "Hectares de couvert arboré perdus chaque année, seuil de "
              "canopée 30 %. Source : université du Maryland / Hansen, "
              "2000-2025."},
    "tj_f_choc": {
        "en": "**{p} % of twenty-five years of loss happened in three years, "
              "{a}.** Hurricane Matthew struck in October 2016. Outside those "
              "three years the forest loses {hors} % a year; counting them, "
              "{avec} %. A shock does not only destroy houses: it is still "
              "legible in the canopy a decade later.",
        "fr": "**{p} % de la perte de vingt-cinq ans s'est produite en trois "
              "ans, {a}.** L'ouragan Matthew a frappé en octobre 2016. Hors "
              "ces trois années, la forêt perd {hors} % par an ; en les "
              "comptant, {avec} %. Un choc ne détruit pas que des maisons : il "
              "reste lisible dans la canopée dix ans après."},
    "tj_f_c1": {"en": "hectares lost since 2000", "fr": "hectares perdus depuis 2000"},
    "tj_f_c2": {"en": "of the 2000 forest", "fr": "de la forêt de 2000"},
    "tj_f_c3": {"en": "forest cover today", "fr": "de couvert forestier aujourd'hui"},
    "tj_f_choc_lab": {"en": "shock years", "fr": "années de choc"},
    "tj_f_ord": {"en": "hectares lost", "fr": "hectares perdus"},

    # ---------------- pluie
    "tj_p_t": {"en": "Rainfall, forty-five years",
               "fr": "La pluie, quarante-cinq ans"},
    "tj_p_x": {
        "en": "Annual total, and the 1991–2020 normal as a reference line. "
              "Source: CHIRPS, 1981–2025.",
        "fr": "Cumul annuel, et la normale 1991-2020 en ligne de référence. "
              "Source : CHIRPS, 1981-2025."},
    "tj_p_norm": {"en": "1991–2020 normal", "fr": "normale 1991-2020"},
    "tj_p_ord": {"en": "millimetres", "fr": "millimètres"},
    "tj_p_c1": {"en": "driest year", "fr": "année la plus sèche"},
    "tj_p_c2": {"en": "wettest year", "fr": "année la plus arrosée"},
    "tj_p_c3": {"en": "last five years vs normal",
                "fr": "cinq dernières années / normale"},

    # ---------------- température
    "tj_t_t": {"en": "Land surface temperature, dry season",
               "fr": "La température de surface, saison sèche"},
    "tj_t_x": {
        "en": "Daytime surface temperature over the dry season, °C. Source: "
              "MODIS, 2001–2025.",
        "fr": "Température de surface diurne sur la saison sèche, en °C. "
              "Source : MODIS, 2001-2025."},
    "tj_t_ord": {"en": "°C", "fr": "°C"},
    "tj_t_c1": {"en": "2001–2020 normal", "fr": "normale 2001-2020"},
    "tj_t_c2": {"en": "last five years", "fr": "cinq dernières années"},
    "tj_t_c3": {"en": "difference", "fr": "écart"},

    # ---------------- végétation
    "tj_v_t": {"en": "Vegetation vigour (NDVI), seven years",
               "fr": "La vigueur végétale (NDVI), sept ans"},
    "tj_v_x": {
        "en": "Dry-season median NDVI. **The shortest series on this page:** "
              "Sentinel-2 only covers 2019 onwards at this resolution, so "
              "seven points cannot carry a trend, they show a level and its "
              "wobble.",
        "fr": "NDVI médian de saison sèche. **La série la plus courte de cette "
              "page :** Sentinel-2 ne couvre 2019 et après à cette "
              "résolution, sept points ne portent donc pas une tendance, ils "
              "montrent un niveau et ses soubresauts."},
    "tj_v_ord": {"en": "NDVI", "fr": "NDVI"},
    "tj_lire": {"en": "Hover any mark for its year and value.",
                "fr": "Au survol, chaque marque donne son année et sa valeur."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)

STYLE = """
<style>
  .tj-h   { font-size:17.5px; font-weight:700; color:#101728;
            letter-spacing:-.015em; margin:0 0 3px; }
  .tj-x   { font-size:12.5px; color:#6b7590; line-height:1.55; margin:0 0 12px;
            max-width:96ch; }
  .tj-p   { font-size:14px; color:#3c4761; line-height:1.65; margin:12px 0 0;
            max-width:88ch; }
  .tj-g   { display:flex; gap:12px; flex-wrap:wrap; margin-top:12px; }
  .tj-c   { flex:1 1 170px; min-width:150px; border:1px solid #e3eaf3;
            border-radius:12px; padding:12px 14px; background:#fff; }
  .tj-n   { font-size:19px; font-weight:700; color:#101728; line-height:1;
            letter-spacing:-.02em; font-variant-numeric:tabular-nums; }
  .tj-l   { font-size:11.5px; color:#3c4761; margin-top:5px;
            text-align:left !important; line-height:1.4; }
</style>
"""


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _gras(t):
    out, morceaux = [], _e(t).split("**")
    for i, m in enumerate(morceaux):
        out.append(f"<b>{m}</b>" if i % 2 else m)
    return "".join(out)


def _f(v, dec=1, signe=False):
    if v is None:
        return "—"
    s = f"{v:+.{dec}f}" if signe else f"{v:,.{dec}f}"
    s = s.replace(",", " ")
    return s.replace(".", ",") if i18n.get_lang() == "fr" else s


def _trouver(nom):
    for c in (os.path.join(DATA, nom), os.path.join(APP_DIR, nom)):
        if os.path.exists(c):
            return c
    return None


@st.cache_data(show_spinner=False)
def _lire(nom):
    p = _trouver(nom)
    if not p:
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _serie(d, section, champ, ensemble_ok=True):
    """La série d'une section, ou celle des dix réunies.

    POUR L'ENSEMBLE, ON ADDITIONNE OU ON MOYENNE SELON LA GRANDEUR, et le
    choix n'est pas cosmétique : des hectares perdus s'additionnent, des
    millimètres de pluie et des degrés se moyennent. Additionner des degrés
    donnerait un nombre qui ne veut rien dire.
    """
    if not d:
        return {}
    if section != "__toutes__":
        return ((d.get("sections") or {}).get(section) or {}).get(champ) or {}
    if ensemble_ok and (d.get("ensemble") or {}).get(champ):
        return d["ensemble"][champ]
    somme = {}
    n = {}
    for s in SECTIONS:
        se = ((d.get("sections") or {}).get(s) or {}).get(champ) or {}
        for a, v in se.items():
            if v is None:
                continue
            somme[a] = somme.get(a, 0.0) + float(v)
            n[a] = n.get(a, 0) + 1
    return somme, n


def _moyenne_serie(d, section, champ):
    r = _serie(d, section, champ, ensemble_ok=False)
    if isinstance(r, dict):
        return {a: float(v) for a, v in r.items() if v is not None}
    somme, n = r
    return {a: somme[a] / n[a] for a in somme if n.get(a)}


def _somme_serie(d, section, champ):
    r = _serie(d, section, champ)
    if isinstance(r, dict):
        return {a: float(v) for a, v in r.items() if v is not None}
    somme, _n = r
    return somme


# --------------------------------------------------------------- graphiques
def _cadre(larg, haut, mg=(74, 16, 26, 10)):
    """Marges (gauche, haut, bas, droite) — la gauche porte l'échelle.

    LA MARGE GAUCHE FAIT 74 PX ET NON 48, ET C'EST UN DÉFAUT QUI L'A IMPOSÉ :
    les graduations sont alignées à droite depuis le bord du cadre, si bien
    qu'une valeur large — « 2 343 mm » — sortait du cadre SVG et se trouvait
    coupée. On lisait « 343 mm » là où l'axe disait 2 343.
    """
    g, h, b, d = mg
    return {"larg": larg, "haut": haut, "x0": g, "y0": h,
            "x1": larg - d, "y1": haut - b}


def _axes(c, vmin, vmax, reperes, unite=""):
    """Grille horizontale discrète et graduations. Un seul axe, toujours."""
    parts = []
    for v in reperes:
        y = c["y1"] - (v - vmin) / ((vmax - vmin) or 1) * (c["y1"] - c["y0"])
        parts.append(f'<line x1="{c["x0"]}" y1="{y:.1f}" x2="{c["x1"]}" '
                     f'y2="{y:.1f}" stroke="{GRILLE}" stroke-width="1"/>')
        parts.append(f'<text x="{c["x0"] - 6}" y="{y + 3.5:.1f}" '
                     f'text-anchor="end" font-size="10" fill="{GRIS}">'
                     f'{_e(_f(v, 0))}{_e(unite)}</text>')
    return "".join(parts)


def _annees(c, cles, pas=5):
    parts = []
    n = len(cles)
    for i, a in enumerate(cles):
        if int(a) % pas and i not in (0, n - 1):
            continue
        x = c["x0"] + (i / max(1, n - 1)) * (c["x1"] - c["x0"])
        parts.append(f'<text x="{x:.1f}" y="{c["y1"] + 15}" '
                     f'text-anchor="middle" font-size="10" fill="{GRIS}">'
                     f'{_e(a)}</text>')
    return "".join(parts)


def barres_annuelles(serie, chocs=(), larg=880, haut=230, unite="",
                     couleur=BLEU):
    """Une grandeur, une teinte.

    PUBLIQUE, ET APPELÉE D'AILLEURS. L'onglet « Environnement » de l'analyse
    des résultats traçait la même chronologie forestière avec sa propre
    implémentation : deux dessins du même objet, qui auraient divergé au
    premier réglage. Il appelle désormais celle-ci.

    Les années de choc changent de couleur parce qu'elles sont d'une autre
    nature — un événement, pas une année ordinaire."""
    if not serie:
        return ""
    cles = sorted(serie, key=int)
    vals = [serie[a] for a in cles]
    vmax = max(vals) or 1
    c = _cadre(larg, haut)
    reperes = [0, vmax / 2, vmax]
    parts = [_axes(c, 0, vmax, reperes, unite)]
    n = len(cles)
    pas = (c["x1"] - c["x0"]) / n
    l = max(3.0, pas * 0.62)
    for i, a in enumerate(cles):
        v = serie[a]
        h = (v / vmax) * (c["y1"] - c["y0"])
        x = c["x0"] + i * pas + (pas - l) / 2
        coul = ROUGE if a in chocs else couleur
        parts.append(
            f'<rect x="{x:.1f}" y="{c["y1"] - h:.1f}" width="{l:.1f}" '
            f'height="{max(h, 1):.1f}" rx="2" fill="{coul}">'
            f'<title>{_e(a)} — {_e(_f(v, 1))}{_e(unite)}</title></rect>')
    parts.append(_annees(c, cles))
    return (f'<svg viewBox="0 0 {larg} {haut}" width="100%" '
            f'style="display:block" font-family="Inter,system-ui,sans-serif">'
            + "".join(parts) + '</svg>')


def _ligne(serie, larg=880, haut=230, unite="", couleur=BLEU,
           normale=None, lab_normale=""):
    """Trait de 2 px, extrémités arrondies, points aux extrêmes seulement."""
    if not serie:
        return ""
    cles = sorted(serie, key=int)
    vals = [serie[a] for a in cles]
    vmin, vmax = min(vals), max(vals)
    if normale is not None:
        vmin, vmax = min(vmin, normale), max(vmax, normale)
    marge = (vmax - vmin) * 0.12 or 1
    vmin, vmax = vmin - marge, vmax + marge
    c = _cadre(larg, haut)
    reperes = [vmin + (vmax - vmin) * k / 2 for k in range(3)]
    parts = [_axes(c, vmin, vmax, reperes, unite)]

    def xy(i, v):
        return (c["x0"] + (i / max(1, len(cles) - 1)) * (c["x1"] - c["x0"]),
                c["y1"] - (v - vmin) / (vmax - vmin) * (c["y1"] - c["y0"]))

    if normale is not None:
        _x, y = xy(0, normale)
        parts.append(f'<line x1="{c["x0"]}" y1="{y:.1f}" x2="{c["x1"]}" '
                     f'y2="{y:.1f}" stroke="{ENCRE3}" stroke-width="1.4" '
                     f'stroke-dasharray="5 4"/>')
        if lab_normale:
            # À GAUCHE, PAS À DROITE : le dernier point de la série porte sa
            # valeur, et les deux étiquettes se chevauchaient au bord droit.
            parts.append(f'<text x="{c["x0"] + 6}" y="{y - 6:.1f}" '
                         f'text-anchor="start" font-size="10.5" '
                         f'fill="{ENCRE3}">{_e(lab_normale)}</text>')
    d = []
    for i, a in enumerate(cles):
        x, y = xy(i, serie[a])
        d.append(f'{"M" if i == 0 else "L"}{x:.1f} {y:.1f}')
    parts.append(f'<path d="{"".join(d)}" fill="none" stroke="{couleur}" '
                 f'stroke-width="2" stroke-linecap="round" '
                 f'stroke-linejoin="round"/>')
    # points : les extrêmes et le dernier, nommés ; les autres, muets mais
    # survolables — une valeur sur chaque point ferait un mur de chiffres.
    i_min = vals.index(min(vals))
    i_max = vals.index(max(vals))
    for i, a in enumerate(cles):
        x, y = xy(i, serie[a])
        gros = i in (i_min, i_max, len(cles) - 1)
        parts.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{4.5 if gros else 2.2}" '
            f'fill="{couleur if gros else "#ffffff"}" '
            f'stroke="{couleur}" stroke-width="1.6">'
            f'<title>{_e(a)} — {_e(_f(serie[a], 1))}{_e(unite)}</title>'
            f'</circle>')
        if gros:
            # LA DERNIÈRE VALEUR S'ANCRE À DROITE : centrée, elle débordait du
            # cadre et se lisait « 1 19 » au lieu de « 1 219 ».
            fin = i == len(cles) - 1
            parts.append(
                f'<text x="{x - (3 if fin else 0):.1f}" y="{y - 10:.1f}" '
                f'text-anchor="{"end" if fin else "middle"}" '
                f'font-size="10.5" font-weight="700" fill="{ENCRE2}">'
                f'{_e(_f(serie[a], 0 if max(vals) > 100 else 2))}</text>')
    parts.append(_annees(c, cles))
    return (f'<svg viewBox="0 0 {larg} {haut}" width="100%" '
            f'style="display:block" font-family="Inter,system-ui,sans-serif">'
            + "".join(parts) + '</svg>')


def _chiffre(val, lab):
    return (f'<div class="tj-c"><div class="tj-n">{_e(val)}</div>'
            f'<div class="tj-l">{_e(lab)}</div></div>')


# ------------------------------------------------------------------- blocs
def _bloc_foret(section):
    d = _lire("foret.json")
    if not d:
        return
    base = (d.get("ensemble") if section == "__toutes__"
            else (d.get("sections") or {}).get(section)) or {}
    serie = _somme_serie(d, section, "pertes_annuelles_ha")
    chocs = {str(a) for a in (base.get("annees_choc")
                              or (d.get("ensemble") or {}).get("annees_choc")
                              or [])}
    with st.container(border=True):
        st.markdown(f'<div class="tj-h">{_e(T("tj_f_t"))}</div>'
                    f'<p class="tj-x">{_e(T("tj_f_x"))}</p>'
                    + barres_annuelles(serie, chocs, unite=" ha", couleur=VERT),
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="tj-g">'
            + _chiffre(_f(base.get("perte_totale_ha"), 0), T("tj_f_ord"))
            + _chiffre(_f(base.get("perte_relative_pct"), 1) + " %",
                       T("tj_f_c2"))
            + _chiffre(_f(base.get("foret2025_pct"), 1) + " %", T("tj_f_c3"))
            + _chiffre(_f(base.get("part_choc_pct"), 0) + " %",
                       T("tj_f_choc_lab"))
            + '</div>', unsafe_allow_html=True)
        if base.get("part_choc_pct") and chocs:
            st.markdown(
                f'<p class="tj-p">{_gras(T("tj_f_choc", p=_f(base["part_choc_pct"], 0), a="-".join(sorted(chocs)[:1] + sorted(chocs)[-1:]), hors=_f(abs(base.get("taux_annuel_hors_choc") or 0), 2), avec=_f(abs(base.get("taux_annuel_net") or 0), 2)))}</p>',
                unsafe_allow_html=True)


def _bloc_pluie(section):
    d = _lire("pluie.json")
    if not d:
        return
    serie = _moyenne_serie(d, section, "serie_mm")
    base = ((d.get("sections") or {}).get(section) or {}) if section != "__toutes__" else {}
    if section == "__toutes__":
        normale = sum(((d.get("sections") or {}).get(s) or {}).get("normale_mm") or 0
                      for s in SECTIONS) / len(SECTIONS)
    else:
        normale = base.get("normale_mm")
    if not serie:
        return
    cles = sorted(serie, key=int)
    a_min = min(cles, key=lambda a: serie[a])
    a_max = max(cles, key=lambda a: serie[a])
    cinq = [serie[a] for a in cles[-5:]]
    rap = (sum(cinq) / len(cinq)) / normale * 100 if normale else None
    with st.container(border=True):
        st.markdown(f'<div class="tj-h">{_e(T("tj_p_t"))}</div>'
                    f'<p class="tj-x">{_e(T("tj_p_x"))}</p>'
                    + _ligne(serie, unite=" mm", couleur=BLEU,
                             normale=normale,
                             lab_normale=T("tj_p_norm")),
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="tj-g">'
            + _chiffre(f'{a_min} · {_f(serie[a_min], 0)} mm', T("tj_p_c1"))
            + _chiffre(f'{a_max} · {_f(serie[a_max], 0)} mm', T("tj_p_c2"))
            + _chiffre(_f(rap, 0) + " %" if rap else "—", T("tj_p_c3"))
            + '</div>', unsafe_allow_html=True)


def _bloc_thermique(section):
    d = _lire("thermique.json")
    if not d:
        return
    serie = _moyenne_serie(d, section, "serie_lst_saison")
    if not serie:
        return
    cles = sorted(serie, key=int)
    ref = [serie[a] for a in cles if 2001 <= int(a) <= 2020]
    rec = [serie[a] for a in cles[-5:]]
    n_ref = sum(ref) / len(ref) if ref else None
    n_rec = sum(rec) / len(rec) if rec else None
    with st.container(border=True):
        st.markdown(f'<div class="tj-h">{_e(T("tj_t_t"))}</div>'
                    f'<p class="tj-x">{_e(T("tj_t_x"))}</p>'
                    + _ligne(serie, unite=" °C", couleur=AMBRE,
                             normale=n_ref, lab_normale=T("tj_t_c1")),
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="tj-g">'
            + _chiffre(_f(n_ref, 2) + " °C", T("tj_t_c1"))
            + _chiffre(_f(n_rec, 2) + " °C", T("tj_t_c2"))
            + _chiffre(_f((n_rec - n_ref) if (n_ref and n_rec) else None, 2,
                          signe=True) + " °C", T("tj_t_c3"))
            + '</div>', unsafe_allow_html=True)


def _bloc_vegetation(section):
    d = _lire("indices_vegetation.json")
    if not d:
        return
    serie = _moyenne_serie(d, section, "serie_ndvi")
    if not serie:
        return
    with st.container(border=True):
        st.markdown(f'<div class="tj-h">{_e(T("tj_v_t"))}</div>'
                    f'<p class="tj-x">{_gras(T("tj_v_x"))}</p>'
                    + _ligne(serie, haut=200, couleur=VERT),
                    unsafe_allow_html=True)


# ------------------------------------------------------------------ la page
def render(entete=True):
    """Les quatre series physiques du territoire.

    ELLE N'EST PLUS UNE RUBRIQUE, ELLE EST UNE SECTION. Forets, pluies,
    temperatures : ce sont des mesures de l'environnement dans le temps, et
    leur place est dans la resilience environnementale, ou tout le reste de
    l'environnement se lit deja. Une quatorzieme entree de menu pour quatre
    courbes, c'etait une entree de trop ; `entete` permet a la page hote de
    poser son propre titre.
    """
    st.markdown(STYLE, unsafe_allow_html=True)
    if entete:
        st.markdown(
            f'<h2 style="font-size:21.5px;font-weight:700;color:{ENCRE};'
            f'letter-spacing:-.02em;margin:2px 0 0">{_e(T("tj_titre"))}</h2>'
            f'<p style="font-size:11.5px;color:{ENCRE3};letter-spacing:.06em;'
            f'text-transform:uppercase;margin:2px 0 0;font-weight:600">'
            f'{_e(T("tj_sous"))}</p>', unsafe_allow_html=True)

    if not _lire("foret.json") and not _lire("pluie.json"):
        st.info(T("tj_absent"))
        return

    st.info(T("tj_intro"))

    # UN SEUL SÉLECTEUR POUR LES QUATRE SÉRIES. Elles décrivent le même
    # territoire ; les filtrer séparément inviterait à comparer une section
    # avec une autre sans le savoir.
    choix = st.selectbox(T("tj_perimetre"),
                         ["__toutes__"] + SECTIONS,
                         format_func=lambda s: T("tj_toutes") if s == "__toutes__"
                         else s, key="tj_section")
    st.caption(T("tj_lire"))

    _bloc_foret(choix)
    _bloc_pluie(choix)
    _bloc_thermique(choix)
    _bloc_vegetation(choix)
