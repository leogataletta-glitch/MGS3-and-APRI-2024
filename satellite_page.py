"""Les mesures satellitaires, section communale par section communale.

POURQUOI ELLES ONT LEUR PLACE DANS LES RÉSULTATS BRUTS, ET PAS AILLEURS.
Un résultat brut est une mesure avant tout barème : ce que les ménages ont
répondu, ou ce que le capteur a vu. La couverture forestière de Hansen et le
NDVI de Sentinel-2 sont exactement cela — des mesures, pas des scores. Les
tenir à l'écart des résultats bruts obligeait à les chercher dans la page
« environnement », deux clics plus loin, alors qu'on les compare aux réponses
des ménages de la même section.

ELLES NE SE VENTILENT PAS PAR SEXE, PAR ÂGE NI PAR RICHESSE, ET C'EST UNE
PROPRIÉTÉ DE LA MESURE, PAS UN MANQUE. Un pixel n'a pas de ménage : il a une
section communale. Proposer « le NDVI des femmes » afficherait un menu qui ne
peut rien produire. La seule ventilation offerte est donc géographique, et
elle est dite.

CHAQUE MESURE PORTE SA SOURCE, SON CAPTEUR ET SA PÉRIODE. Une couverture
forestière n'a pas de sens sans son seuil de couvert, un NDVI n'en a pas sans
sa saison : deux capteurs et deux fenêtres donnent deux chiffres différents
pour la même forêt, et le lecteur doit savoir lequel il lit.
"""

import json
import os

import streamlit as st

import i18n
import map_render
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

ENCRE, ENCRE3, GRIS = "#101728", "#6b7590", "#8a93a5"
VERT_APRI = "#2a6b3f"

# Les mesures offertes : (code, clé de libellé, fichier, chemin, unité,
# décimales, polarité de carte). `serie:<nom>` lit la dernière année de la
# série ; `serie:<nom>:delta` lit l'écart entre la première et la dernière.
MESURES = [
    ("foret2025_pct", "sat_m_couvert", "foret", "foret2025_pct",
     "%", 1, "eleve_bon"),
    ("foret2000_pct", "sat_m_couvert2000", "foret", "foret2000_pct",
     "%", 1, "eleve_bon"),
    ("perte_relative_pct", "sat_m_perte", "foret", "perte_relative_pct",
     "%", 1, "eleve_mauvais"),
    ("perte_totale_ha", "sat_m_perte_ha", "foret", "perte_totale_ha",
     "ha", 1, "eleve_mauvais"),
    ("taux_annuel_net", "sat_m_taux", "foret", "taux_annuel_net",
     "%/an", 3, "eleve_bon"),
    ("part_choc_pct", "sat_m_choc", "foret", "part_choc_pct",
     "%", 1, "eleve_mauvais"),
    ("ndvi", "sat_m_ndvi", "vege", "serie:serie_ndvi", "", 3, "eleve_bon"),
    ("ndvi_delta", "sat_m_ndvi_d", "vege", "serie:serie_ndvi:delta",
     "", 3, "eleve_bon"),
    ("ndmi", "sat_m_ndmi", "vege", "serie:serie_ndmi", "", 3, "eleve_bon"),
    ("evi", "sat_m_evi", "vege", "serie:serie_evi", "", 3, "eleve_bon"),
    ("fvc", "sat_m_fvc", "vege", "serie:serie_fvc", "", 3, "eleve_bon"),
    ("ndwi", "sat_m_ndwi", "vege", "serie:serie_ndwi", "", 3, "eleve_bon"),
]

TEXTES = {
    "sat_titre": {"en": "Satellite measurements",
                  "fr": "Mesures satellitaires"},
    "sat_intro": {
        "en": "Forest cover and vegetation indices, measured from orbit for "
              "each of the ten communal sections. These are raw measurements, "
              "not scores: no scale has been applied to them.",
        "fr": "Couverture forestière et indices de végétation, mesurés depuis "
              "l'orbite pour chacune des dix sections communales. Ce sont des "
              "mesures brutes, pas des scores : aucun barème ne leur a été "
              "appliqué."},
    "sat_source": {"en": "Source", "fr": "Source"},
    "sat_mesure": {"en": "Measurement", "fr": "Mesure"},
    "sat_annee": {"en": "Year", "fr": "Année"},
    "sat_ventile": {
        "en": "A pixel has no household: these measurements break down by "
              "communal section and by nothing else. The sex, age and wealth "
              "filters do not apply to them.",
        "fr": "Un pixel n'a pas de ménage : ces mesures se ventilent par "
              "section communale et par rien d'autre. Les filtres de sexe, "
              "d'âge et de richesse ne s'y appliquent pas."},
    "sat_ens": {"en": "Whole territory", "fr": "Territoire entier"},
    "sat_col_sec": {"en": "Communal section", "fr": "Section communale"},
    "sat_format": {"en": "Chart", "fr": "Graphique"},
    "sat_barres": {"en": "Bar chart", "fr": "Histogramme"},
    "sat_carte": {"en": "Map", "fr": "Carte"},
    "sat_tableau": {"en": "Table", "fr": "Tableau"},
    "sat_indispo": {
        "en": "This measurement is not available in the delivered data.",
        "fr": "Cette mesure n'est pas disponible dans les données livrées."},

    "sat_m_couvert": {"en": "Forest cover, {a} (% of area)",
                      "fr": "Couverture forestière, {a} (% de la surface)"},
    "sat_m_couvert2000": {"en": "Forest cover, {a} (% of area)",
                          "fr": "Couverture forestière, {a} (% de la surface)"},
    "sat_m_perte": {"en": "Forest lost since {a} (% of the {a} forest)",
                    "fr": "Forêt perdue depuis {a} (% de la forêt de {a})"},
    "sat_m_perte_ha": {"en": "Forest lost since {a} (hectares)",
                       "fr": "Forêt perdue depuis {a} (hectares)"},
    "sat_m_taux": {"en": "Net annual rate of forest change (%/year)",
                   "fr": "Taux annuel net d'évolution forestière (%/an)"},
    "sat_m_choc": {
        "en": "Share of the loss concentrated in its worst single year (%)",
        "fr": "Part de la perte concentrée sur sa pire année (%)"},
    "sat_m_ndvi": {"en": "NDVI — vegetation vigour, {a}",
                   "fr": "NDVI — vigueur de la végétation, {a}"},
    "sat_m_ndvi_d": {"en": "NDVI change, {d}",
                     "fr": "Évolution du NDVI, {d}"},
    "sat_m_ndmi": {"en": "NDMI — vegetation moisture, {a}",
                   "fr": "NDMI — humidité de la végétation, {a}"},
    "sat_m_evi": {"en": "EVI — enhanced vegetation index, {a}",
                  "fr": "EVI — indice de végétation amélioré, {a}"},
    "sat_m_fvc": {"en": "FVC — fraction of ground covered by vegetation, {a}",
                  "fr": "FVC — fraction du sol couverte de végétation, {a}"},
    "sat_m_ndwi": {"en": "NDWI — water index, {a}",
                   "fr": "NDWI — indice d'eau, {a}"},

    "sat_src_foret": {
        "en": "Hansen / UMD global forest change, {s}. Forest = at least "
              "{p} % tree cover. Period {d1}–{d2}.",
        "fr": "Hansen / UMD global forest change, {s}. Forêt = couvert "
              "arboré d'au moins {p} %. Période {d1}–{d2}."},
    "sat_src_vege": {
        "en": "Sentinel-2 surface reflectance ({s}), {sa} composites, "
              "{d1}–{d2}. Sections with fewer than {px} usable pixels are "
              "left out.",
        "fr": "Réflectance de surface Sentinel-2 ({s}), composites de "
              "{sa}, {d1}–{d2}. Les sections comptant moins de {px} pixels "
              "exploitables sont écartées."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)

STYLE = """
<style>
  .sat-lab { font-size:10.5px; font-weight:700; letter-spacing:.09em;
       text-transform:uppercase; color:#8a93a5; margin:10px 0 2px; }
  .sat-tab { width:100%; border-collapse:collapse; margin-top:12px; }
  .sat-tab th { font-size:10.5px; font-weight:700; letter-spacing:.09em;
       text-transform:uppercase; color:#8a93a5; text-align:left;
       padding:0 10px 7px 0; border-bottom:1px solid #e9eef4; }
  .sat-tab th.n, .sat-tab td.n { text-align:right;
       font-variant-numeric:tabular-nums; }
  .sat-tab td { font-size:12.5px; color:#3c4761; padding:7px 10px 7px 0;
       border-bottom:1px solid #f2f5f9; }
  .sat-tab td.v { font-weight:700; color:#101728; }
  .sat-note { font-size:11.5px; color:#8a93a5; line-height:1.5;
       margin:8px 0 0; text-align:left !important; max-width:96ch; }
</style>
"""


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _f(v, dec=1, signe=False):
    if v is None:
        return "—"
    s = f"{v:+.{dec}f}" if signe else f"{v:.{dec}f}"
    return s.replace(".", ",") if i18n.get_lang() == "fr" else s


@st.cache_data(show_spinner=False)
def _charger():
    """Les deux fichiers de mesures, tels qu'ils sont livrés.

    UN FICHIER ABSENT NE FAIT PAS TOMBER L'ÉCRAN : la mesure qui en dépend est
    simplement dite indisponible. Un dépôt sans données satellitaires doit
    pouvoir afficher les résultats d'enquête.
    """
    out = {}
    for cle, nom in (("foret", "foret.json"),
                     ("vege", "indices_vegetation.json")):
        p = os.path.join(DATA, nom)
        if not os.path.exists(p):
            p = os.path.join(APP_DIR, nom)
        try:
            with open(p, encoding="utf-8") as f:
                out[cle] = json.load(f)
        except Exception:
            out[cle] = None
    return out


def _annees(d, chemin):
    """Les années d'une série, triées."""
    if not d:
        return []
    for sec in (d.get("sections") or {}).values():
        s = sec.get(chemin)
        if isinstance(s, dict) and s:
            return sorted(s, key=lambda a: int(a))
    return []


def _valeurs(d, spec, annee=None):
    """La mesure demandée, section par section : {section: valeur}."""
    if not d:
        return {}, None, None
    out = {}
    if spec.startswith("serie:"):
        bouts = spec.split(":")
        champ = bouts[1]
        delta = len(bouts) > 2 and bouts[2] == "delta"
        for nom, sec in (d.get("sections") or {}).items():
            s = sec.get(champ)
            if not isinstance(s, dict) or not s:
                continue
            ans = sorted(s, key=lambda a: int(a))
            if delta:
                out[nom] = s[ans[-1]] - s[ans[0]]
            else:
                a = annee if annee in s else ans[-1]
                out[nom] = s[a]
        ans = _annees(d, champ)
        return out, (ans[0] if ans else None), (ans[-1] if ans else None)
    for nom, sec in (d.get("sections") or {}).items():
        v = sec.get(spec)
        if v is not None:
            out[nom] = v
    return out, None, None


def _libelle(cle_lib, mesure, d, annee):
    """Le libellé d'une mesure, avec l'année ou la fenêtre qu'elle couvre."""
    _c, _l, fichier, spec, _u, _dec, _p = mesure
    if fichier == "foret":
        base = (d or {}).get("periode") or [2000, 2025]
        a = base[0] if "2000" in spec else base[1]
        return T(cle_lib, a=a, d1=base[0], d2=base[1])
    ans = _annees(d, spec.split(":")[1]) if spec.startswith("serie:") else []
    if spec.endswith(":delta") and ans:
        return T(cle_lib, d=f"{ans[0]}–{ans[-1]}", a="")
    a = annee if annee in ans else (ans[-1] if ans else "")
    return T(cle_lib, a=a, d="")


def _source(fichier, d):
    if not d:
        return ""
    if fichier == "foret":
        per = d.get("periode") or [2000, 2025]
        return T("sat_src_foret", s=d.get("source", "—"),
                 p=d.get("seuil_couvert_pct", 30), d1=per[0], d2=per[1])
    per = d.get("periode_annees") or []
    return T("sat_src_vege", s=d.get("source", "—"),
             sa=d.get("saison", "—"),
             d1=(per[0] if per else "—"), d2=(per[-1] if per else "—"),
             px=d.get("pixels_mini", 50))


def _barres(vals, unite, dec, moy):
    """Une barre par section, l'ensemble du territoire en pointillés."""
    if not vals:
        return ""
    lignes = list(vals.items())
    bornes = list(vals.values()) + ([moy] if moy is not None else [])
    vmin, vmax = min(bornes + [0]), max(bornes + [0])
    etendue = (vmax - vmin) or 1.0
    LARG, H_L, GAP = 1000, 28, 9
    MG_G, MG_H, MG_B = 190, 30, 22
    H = MG_H + len(lignes) * (H_L + GAP) + MG_B
    utile = LARG - MG_G - 120
    x0 = MG_G + utile * (0 - vmin) / etendue        # l'abscisse du zéro
    parts, y = [], MG_H

    if moy is not None:
        x = MG_G + utile * (moy - vmin) / etendue
        parts.append(
            f'<line x1="{x:.1f}" y1="{MG_H - 14}" x2="{x:.1f}" '
            f'y2="{H - MG_B + 4}" stroke="{ENCRE3}" stroke-width="1" '
            f'stroke-dasharray="3 4"/>'
            f'<text x="{x:.1f}" y="{MG_H - 19}" text-anchor="middle" '
            f'font-size="11" fill="{ENCRE3}">{_e(T("sat_ens"))} '
            f'{_f(moy, dec)}{_e(unite)}</text>')

    for nom, v in lignes:
        xa = MG_G + utile * (min(v, 0) - vmin) / etendue
        xb = MG_G + utile * (max(v, 0) - vmin) / etendue
        parts.append(
            f'<text x="{MG_G - 12}" y="{y + 15}" text-anchor="end" '
            f'font-size="12.5" fill="{ENCRE}">{_e(nom)}</text>'
            f'<rect x="{xa:.1f}" y="{y + 3}" width="{max(xb - xa, 2):.1f}" '
            f'height="16" rx="4" fill="{VERT_APRI}"/>'
            f'<text x="{LARG - 4}" y="{y + 15}" text-anchor="end" '
            f'font-size="12.5" font-weight="700" fill="{ENCRE}">'
            f'{_f(v, dec)}{_e(unite)}</text>')
        y += H_L + GAP
    parts.append(f'<line x1="{x0:.1f}" y1="{MG_H - 2}" x2="{x0:.1f}" '
                 f'y2="{H - MG_B + 2}" stroke="#d8e0ea" stroke-width="1"/>')
    return (f'<svg viewBox="0 0 {LARG} {H}" width="100%" '
            f'style="max-width:{LARG}px;display:block" role="img" '
            f'font-family="Inter,system-ui,sans-serif">'
            + "".join(parts) + '</svg>')


def _tableau(vals, unite, dec, moy, lib):
    r = ['<table class="sat-tab"><thead><tr>'
         f'<th>{_e(T("sat_col_sec"))}</th>'
         f'<th class="n">{_e(lib)}</th></tr></thead><tbody>']
    for nom, v in vals.items():
        r.append(f'<tr><td>{_e(nom)}</td>'
                 f'<td class="n v">{_f(v, dec)}{_e(unite)}</td></tr>')
    if moy is not None:
        r.append(f'<tr><td>{_e(T("sat_ens"))}</td>'
                 f'<td class="n v">{_f(moy, dec)}{_e(unite)}</td></tr>')
    r.append('</tbody></table>')
    return "".join(r)


def _carte(vals, unite, polarite):
    if len(vals) < 2:
        return None
    seuils = map_render.nice_thresholds(list(vals.values()))
    svg, seuils_ret, _m = map_render.render_map_svg(
        vals, {s: 1 for s in vals}, seuils, height=560,
        polarity=polarite, unite=unite or "")
    legende = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:7px;'
        f'margin-right:16px"><span style="width:20px;height:11px;'
        f'border-radius:3px;background:{c}"></span>'
        f'<span style="font-size:11.5px;color:#52514e">{lab}</span></span>'
        for c, lab in map_render.legend_items(seuils_ret, polarite,
                                              unite or ""))
    return f'<div style="margin:6px 0 8px">{legende}</div>{svg}'


def render():
    """Une mesure, dix sections, un dessin — et sa source sous le dessin."""
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown(
        f'<div class="titre-bloc">{_e(T("sat_titre"))}</div>'
        f'<p class="sat-note" style="margin:0 0 10px">{_e(T("sat_intro"))}</p>',
        unsafe_allow_html=True)

    d = _charger()
    dispo = [m for m in MESURES if d.get(m[2])]
    if not dispo:
        st.info(T("sat_indispo"))
        return

    c1, c2, c3 = st.columns([2, 0.8, 1])
    with c1:
        k = st.selectbox(
            T("sat_mesure"), list(range(len(dispo))), key="sat_m",
            format_func=lambda i: _libelle(dispo[i][1], dispo[i],
                                           d[dispo[i][2]], None))
    mesure = dispo[k]
    _code, cle_lib, fichier, spec, unite, dec, polarite = mesure
    src = d[fichier]
    ans = _annees(src, spec.split(":")[1]) if spec.startswith("serie:") else []
    annee = None
    with c2:
        if ans and not spec.endswith(":delta"):
            annee = st.selectbox(T("sat_annee"), list(reversed(ans)),
                                 key="sat_a")
    with c3:
        forme = st.selectbox(T("sat_format"), ["barres", "carte", "tableau"],
                             key="sat_forme",
                             format_func=lambda f: T("sat_" + f))

    vals, _a0, _a1 = _valeurs(src, spec, annee)
    if not vals:
        st.info(T("sat_indispo"))
        return
    lib = _libelle(cle_lib, mesure, src, annee)
    # LA MOYENNE DU TERRITOIRE EST CELLE DES SECTIONS, PAS UN TOTAL. Additionner
    # des pourcentages n'a pas de sens ; pour les hectares, le fichier porte son
    # propre total et c'est celui-là qu'on affiche.
    ens = (src.get("ensemble") or {}).get(spec) if not \
        spec.startswith("serie:") else None
    moy = ens if ens is not None else (sum(vals.values()) / len(vals))

    if forme == "carte":
        svg = _carte(vals, unite, polarite)
        if svg is None:
            forme = "barres"
        else:
            st.markdown(f'<div style="font-family:Inter,system-ui,sans-serif">'
                        f'{svg}</div>', unsafe_allow_html=True)
    if forme == "barres":
        st.markdown(_barres(vals, unite, dec, moy), unsafe_allow_html=True)
    elif forme == "tableau":
        st.markdown(_tableau(vals, unite, dec, moy, lib),
                    unsafe_allow_html=True)

    st.markdown(f'<p class="sat-note">{_e(T("sat_ventile"))}</p>'
                f'<p class="sat-note"><b>{_e(T("sat_source"))}</b> · '
                f'{_e(_source(fichier, src))}</p>', unsafe_allow_html=True)
