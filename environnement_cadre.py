"""Résilience environnementale — le cadre, ses trois sources, ses barèmes.

CE QUE CET ONGLET AJOUTE, ET POURQUOI IL EST À PART

La dimension environnementale est la seule du référentiel qui ne se mesure pas
en interrogeant des ménages. Elle se mesure en marchant sur un transect, en
lisant une image satellitaire, et — pour la part humaine — en demandant aux
familles ce qu'elles prélèvent. Trois façons de regarder qui ne voient pas la
même chose ; les mélanger dans la page générale du cadre les aurait toutes
aplaties.

LE CONTENU VIENT D'UNE NOTE DE CADRAGE, ET IL EN VIENT VERBATIM.

Les barèmes, les seuils, les scénarios de score 0 et de score 10 sont ceux de
la note « Monitoring de la résilience environnementale — scoping note /
protocole ». Ils sont lus dans `data/cadre_environnement.json`, extrait du
document, et affichés tels quels. DEUX CONSÉQUENCES ASSUMÉES :

  · ils restent en français dans l'interface anglaise. Un seuil traduit n'est
    plus le seuil du document source, et cette page est une annexe de méthode :
    on doit pouvoir la citer. Une mention le dit à l'écran ;
  · si la note évolue, c'est le JSON qu'on remplace, pas le code.

LA PAGE NE PROMET PAS CE QUI N'EST PAS FAIT. Le protocole décrit trente-neuf
indicateurs satellitaires et six indicateurs de terrain ; la plateforme en
calcule dix-sept à ce jour, tous satellitaires. L'écart est affiché, calculé
depuis `resultats.json`, et non commenté à l'avantage du dispositif.
"""

import json
import os

import streamlit as st

import i18n
import icones
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"
VERT, BLEU, AMBRE, ROUGE, GRIS = ("#1a8a4f", "#2166ac", "#d1730c",
                                  "#c33a24", "#8a93a5")
DIM_ENV = "III.  ENVIRONMENTAL AND ECOLOGICAL DIMENSION"

TEXTES = {
    "env_onglet": {"en": "Environmental resilience",
                   "fr": "Résilience environnementale"},
    "env_onglet_apri": {"en": "The APRI framework", "fr": "Le cadre APRI"},

    # ---------------- strate 1


    # ---------------- strate 2
    "env_s2": {"en": "The three sources", "fr": "Les trois sources"},
    "env_src1_t": {"en": "I · Field records", "fr": "I · Les relevés de terrain"},
    "env_src2_t": {"en": "II · Satellite imagery",
                   "fr": "II · L'imagerie satellitaire"},
    "env_src3_t": {"en": "III · Household survey", "fr": "III · L'enquête ménage"},
    "env_taxons": {"en": "Three taxa, chosen as proxies",
                   "fr": "Trois taxons, choisis comme proxys"},
    "env_tx_od": {"en": "Dragonflies", "fr": "Odonates"},
    "env_tx_oi": {"en": "Birds", "fr": "Oiseaux"},
    "env_tx_po": {"en": "Pollinators", "fr": "Pollinisateurs"},


    # ---------------- strate 3
    "env_s3": {"en": "The protocol in detail", "fr": "Le protocole en détail"},
    "env_v_terrain": {"en": "Field records, six indicators and their scale",
                      "fr": "Relevés de terrain, six indicateurs et leur barème"},
    "env_v_veg": {"en": "Vegetation and productivity, {n} indicators",
                  "fr": "Végétation et productivité, {n} indicateurs"},
    "env_v_frag": {"en": "Landscape fragmentation, {n} indicators",
                   "fr": "Fragmentation du paysage, {n} indicateurs"},
    "env_v_conn": {"en": "Connectivity, {n} indicators",
                   "fr": "Connectivité, {n} indicateurs"},
    "env_v_cot": {"en": "Coastal resilience, six families",
                  "fr": "Résilience côtière, six familles"},
    "env_v_hydro": {"en": "Anthropogenic pressure, hydrology and climate",
                    "fr": "Pressions anthropiques, hydrologie et climat"},
    "env_v_men": {"en": "Household proxies", "fr": "Les proxys d'enquête ménage"},
    # Les intitulés courts des quatre familles satellitaires, pour les pavés
    # chiffrés, un titre de volet ne fait pas une étiquette de pavé.
    "env_l_veg": {"en": "vegetation", "fr": "végétation"},
    "env_l_frag": {"en": "fragmentation", "fr": "fragmentation"},
    "env_l_conn": {"en": "connectivity", "fr": "connectivité"},
    "env_l_cot": {"en": "coastal", "fr": "littoral"},
    "env_c_ind": {"en": "Indicator", "fr": "Indicateur"},
    "env_c_mes": {"en": "What it measures", "fr": "Ce qu'il mesure"},
    "env_c_lien": {"en": "Link with resilience", "fr": "Lien avec la résilience"},
    "env_c_seuil": {"en": "0 and 10", "fr": "Le 0 et le 10"},
    "env_s0": {"en": "Score 0, degraded regime",
               "fr": "Score 0, régime dégradé"},
    "env_s10": {"en": "Score 10, reference regime",
                "fr": "Score 10, régime de référence"},
    "env_unite": {"en": "Unit of observation", "fr": "Unité d'observation"},
    "env_absent": {"en": "The framework file is missing.",
                   "fr": "Le fichier de cadrage est absent."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)

STYLE = """
<style>
  .ev-n    { flex:1 1 200px; min-width:186px; background:#fff;
             border:1px solid #e3eaf3; border-radius:14px; padding:16px 18px;
             box-shadow:0 1px 2px rgba(16,23,40,.05); }
  .ev-i    { width:34px; height:34px; border-radius:10px; display:flex;
             align-items:center; justify-content:center; margin-bottom:11px; }
  .ev-t    { font-size:13.5px; font-weight:700; color:#101728; margin:0 0 5px;
             line-height:1.25; }
  .ev-x    { font-size:12.5px; color:#3c4761; line-height:1.55; margin:0; }
  .ev-flux { display:flex; align-items:stretch; gap:4px; flex-wrap:wrap; }
  .ev-fl   { flex:1 1 150px; min-width:135px; text-align:center;
             padding:13px 10px; border:1px solid #e3eaf3; border-radius:13px;
             background:#fff; }
  .ev-fn   { font-size:21px; font-weight:700; color:#101728; line-height:1;
             letter-spacing:-.03em; font-variant-numeric:tabular-nums; }
  .ev-fl-l { font-size:11.5px; font-weight:700; color:#3c4761; margin-top:5px; }
  .ev-fl-x { font-size:11.5px; color:#8a93a5; margin-top:3px; line-height:1.4; }
  .ev-ch   { align-self:center; color:#c3ccda; font-size:16px; flex:0 0 auto; }
  .ev-tab  { width:100%; border-collapse:collapse; font-size:12px; }
  .ev-tab th { text-align:left; padding:8px 10px; border-bottom:2px solid #e6ecf4;
             font-size:10.5px; letter-spacing:.05em; text-transform:uppercase;
             color:#6b7590; font-weight:700; }
  .ev-tab td { padding:8px 10px; border-bottom:1px solid #f0f4f9;
             color:#3c4761; line-height:1.5; vertical-align:top; }
  .ev-tab td:first-child { font-weight:700; color:#101728; }
  .ev-seuil { font-variant-numeric:tabular-nums; white-space:nowrap;
              font-size:11.5px; color:#101728; font-weight:600; }
  .ev-sc   { border:1px solid #e3eaf3; border-radius:12px; padding:12px 14px;
             height:100%; }
  .ev-sc-t { font-size:11px; letter-spacing:.08em; text-transform:uppercase;
             font-weight:700; margin-bottom:6px; }
  .ev-sc p { font-size:12px; color:#3c4761; line-height:1.55; margin:0;
             white-space:pre-line; }
  .ev-puce { margin:0; padding:0; list-style:none; }
  .ev-puce li { font-size:12.5px; color:#3c4761; line-height:1.5;
                padding:5px 0 5px 15px; position:relative; }
  .ev-puce li::before { content:""; position:absolute; left:0; top:12px;
                width:5px; height:5px; border-radius:50%; background:#c3ccda; }
  .ev-lab  { font-size:11px; letter-spacing:.09em; text-transform:uppercase;
             font-weight:700; color:#8a93a5; margin:0 0 7px; }
  /* LE TEXTE EST JUSTIFIE ET PREND TOUTE LA LARGEUR. Les paragraphes
     etaient bornes a quatre-vingt-seize caracteres et alignes a gauche :
     sur un ecran large, ils laissaient un tiers de la page vide a leur
     droite, et le bord droit en dents de scie faisait paraitre la colonne
     plus etroite encore. */
  .ev-x, p.ev-x { max-width:none !important; text-align:justify !important;
       text-justify:inter-word; hyphens:auto; }
  .ev-etage{ font-size:11px; letter-spacing:.11em; text-transform:uppercase;
             font-weight:700; color:#a7b0be; margin:26px 0 8px; }
  .ev-verdict { font-size:11.5px; color:#1a8a4f; font-weight:600;
                margin-top:7px; }
  /* LA JUSTIFICATION EST ANNULÉE DANS LES CARTES ET LES TABLEAUX. La feuille
     de style du site justifie tous les paragraphes : c'est bon pour une
     colonne de texte, et cela défigure une carte de deux lignes ou une
     cellule étroite — les mots s'écartent jusqu'à laisser des couloirs
     blancs au milieu. */
  /* L'intitulé et les cellules de tableau gardent le fer à gauche : leur
     alignement porte un sens, et une cellule étroite ne se justifie pas.
     Le reste suit la justification du site. */
  .ev-t, .ev-tab td { text-align:left !important; }
  .ev-fl-l, .ev-fl-x, .ev-fn { text-align:center !important; }
</style>
"""


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _trouver(nom):
    for c in (os.path.join(DATA, nom), os.path.join(APP_DIR, nom)):
        if os.path.exists(c):
            return c
    return None


@st.cache_data(show_spinner=False)
def _contenu():
    p = _trouver("cadre_environnement.json")
    if not p:
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def _etat_dimension(lang):
    """LA LANGUE EST UN ARGUMENT, ET C'EST UN BOGUE QUE CELA CORRIGE.
    La fonction lisait `i18n.get_lang()` à l'intérieur et son résultat était
    mis en cache : la première langue affichée figeait les noms d'indicateurs
    pour l'autre. On voyait la liste en anglais dans la page française."""
    return _etat_calcul(lang)


def _etat_calcul(lang):
    """Ce que la plateforme calcule vraiment sur la dimension III.

    LU DANS LES RÉSULTATS, PAS DANS LA NOTE. La note décrit un protocole ; le
    fichier de résultats dit ce qui en est fait. Les deux chiffres doivent
    rester séparés, sans quoi la page annoncerait comme mesuré ce qui n'est
    qu'envisagé.
    """
    p = _trouver("resultats.json")
    if not p:
        return {"n": 0, "faits": [], "manquants": []}
    with open(p, encoding="utf-8") as f:
        res = json.load(f)
    res = res["indicateurs"] if isinstance(res, dict) and "indicateurs" in res \
        else res
    env = [r for r in res if (r.get("dimension") or "").startswith("III.")]
    faits, manq = [], []
    for r in env:
        nom = (r.get("indicateur_fr") if lang == "fr"
               else r.get("indicateur")) or r.get("indicateur", "")
        s = (r.get("scores_corriges") or {}).get("Total")
        (faits if s is not None else manq).append(
            {"nom": nom, "score": s, "poids": r.get("ponderation") or 0})
    return {"n": len(env), "faits": faits, "manquants": manq}


def _icone(nom, couleur):
    return (f'<div class="ev-i" style="background:{couleur}17;color:{couleur}">'
            + icones.svg(nom, couleur=couleur, taille=19) + '</div>')


def _tableau(lignes):
    """Les trois tableaux satellitaires ont la même forme : nom, ce qu'il
    mesure, lien avec la résilience, seuils du 0 et du 10."""
    li = [f'<table class="ev-tab"><tr><th>{_e(T("env_c_ind"))}</th>'
          f'<th>{_e(T("env_c_mes"))}</th><th>{_e(T("env_c_lien"))}</th>'
          f'<th style="text-align:right">{_e(T("env_c_seuil"))}</th></tr>']
    for e in lignes:
        li.append(
            f'<tr><td>{_e(e["nom"])}</td><td>{_e(e["mesure"])}</td>'
            f'<td>{_e(e["lien"])}</td>'
            f'<td class="ev-seuil" style="text-align:right;white-space:normal">'
            f'{_e(e["seuils"])}</td></tr>')
    return "".join(li) + "</table>"


def _bloc_terrain(c):
    """Chaque indicateur de terrain : son unité, puis les deux extrémités de
    son barème côte à côte. Le 0 et le 10 sont ce qui fait le barème ; les
    montrer face à face vaut mieux que les empiler."""
    for e in c["terrain"]:
        with st.container(border=True):
            st.markdown(
                f'<div style="font-size:14.5px;font-weight:700;color:{ENCRE}">'
                f'{_e(e["nom"])}</div>'
                f'<div class="ev-lab" style="margin:9px 0 4px">'
                f'{_e(T("env_unite"))}</div>'
                f'<p class="ev-x" style="white-space:pre-line">'
                f'{_e(e["unite"])}</p>', unsafe_allow_html=True)
            g, d = st.columns(2, gap="medium")
            with g:
                st.markdown(
                    f'<div class="ev-sc" style="border-left:4px solid {ROUGE}">'
                    f'<div class="ev-sc-t" style="color:{ROUGE}">'
                    f'{_e(T("env_s0"))}</div><p>{_e(e["s0"])}</p></div>',
                    unsafe_allow_html=True)
            with d:
                st.markdown(
                    f'<div class="ev-sc" style="border-left:4px solid {VERT}">'
                    f'<div class="ev-sc-t" style="color:{VERT}">'
                    f'{_e(T("env_s10"))}</div><p>{_e(e["s10"])}</p></div>',
                    unsafe_allow_html=True)


def _bloc_cotier(c):
    for i in range(0, len(c["cotier"]), 2):
        cols = st.columns(2, gap="medium")
        for col, b in zip(cols, c["cotier"][i:i + 2]):
            with col:
                with st.container(border=True):
                    st.markdown(
                        f'<div style="font-size:14px;font-weight:700;'
                        f'color:{ENCRE}">{_e(b["nom"])}</div>'
                        + (f'<p class="ev-x" style="color:{ENCRE3};'
                           f'font-size:11.5px;margin-top:4px">'
                           f'{_e(b["contexte"])}</p>' if b["contexte"] else "")
                        + '<ul class="ev-puce">'
                        + "".join(f'<li>{_e(p)}</li>' for p in b["points"])
                        + '</ul>'
                        + (f'<div class="ev-verdict">&rarr; {_e(b["verdict"])}'
                           f'</div>' if b["verdict"] else ""),
                        unsafe_allow_html=True)


def render(complement=None):
    """La resilience environnementale, en trois strates.

    LE COMPLEMENT S'INSERE ENTRE EXPLORER ET APPROFONDIR, et cette place est
    la bonne : les trajectoires sont des mesures de terrain dans le temps,
    donc elles appartiennent a ce qu'on explore, pas a la methode qu'on
    deplie ensuite.
    """
    c = _contenu()
    st.markdown(STYLE, unsafe_allow_html=True)
    # PAS DE TITRE DE PAGE : la barre d'onglets porte deja « Environmental
    # data », et la colonne de menu la rubrique.

    if not c:
        st.info(T("env_absent"))
        return

    # L'ENTREE EN MATIERE A ETE RETIREE. Elle occupait le haut de l'onglet
    # avec une note d'intention, quatre cartouches et un « protocole en un
    # coup d'oeil » : cinq facons d'annoncer ce que la page allait dire,
    # avant de le dire. Les trois sources et le detail du protocole, qui
    # suivent, le disent en entier — et le compte des indicateurs calcules
    # est deja donne, dimension par dimension, dans l'onglet des dimensions.
    # LE COMPTE DES INDICATEURS CALCULES A SUIVI. Il disait des resultats —
    # quatre scores sur dix — au milieu d'une page qui explique une methode.
    # Il reste lisible dimension par dimension dans l'onglet des dimensions,
    # et indicateur par indicateur dans l'analyse des resultats.
    #
    # ===================== STRATE 2 — EXPLORER ============================
    st.markdown(f'<div class="ev-etage">{_e(T("env_s2"))}</div>',
                unsafe_allow_html=True)

    # TOUT EST REPLIE, ET C'EST LA MEME REGLE POUR LES SIX. Trois sources
    # deroulees puis six volets, c'etait deux traitements pour un seul
    # contenu : une methode. Repliee, la page tient en une liste de titres
    # qu'on ouvre quand on veut la verifier — ce qui est exactement
    # l'usage d'un protocole.
    ta = c["intro"]["taxons"]
    with st.expander(T("env_src1_t")):
        st.markdown(
            f'<p class="ev-x" style="margin-top:2px">'
            f'{_e(c["intro"]["terrain"])}</p>'
            f'<div class="ev-lab" style="margin:14px 0 7px">'
            f'{_e(T("env_taxons"))}</div>'
            '<div style="display:flex;gap:14px;flex-wrap:wrap">'
            + "".join(
                f'<div class="ev-n" style="flex:1 1 240px;'
                f'border-top:3px solid {coul}">'
                f'<p class="ev-t">{_e(T(cle))}</p>'
                f'<p class="ev-x" style="font-size:12px">{_e(t)}</p></div>'
                for cle, coul, t in zip(("env_tx_od", "env_tx_oi", "env_tx_po"),
                                        (BLEU, VERT, AMBRE), ta))
            + '</div>', unsafe_allow_html=True)
        st.caption(c["intro"]["transects"])

    with st.expander(T("env_src2_t")):
        st.markdown(
            f'<p class="ev-x" style="margin-top:2px">'
            f'{_e(c["intro"]["geo"])}</p>'
            '<div class="ev-flux" style="margin-top:12px">'
            + "".join(
                f'<div class="ev-fl" style="flex:1 1 165px">'
                f'<div class="ev-fn">{n}</div>'
                f'<div class="ev-fl-l">{_e(lab)}</div></div>'
                for n, lab in ((len(c["vegetation"]), T("env_l_veg")),
                               (len(c["fragmentation"]), T("env_l_frag")),
                               (len(c["connectivite"]), T("env_l_conn")),
                               (sum(len(b["points"]) for b in c["cotier"]),
                                T("env_l_cot"))))
            + '</div>', unsafe_allow_html=True)
        st.caption(c["intro"]["geo_fin"])

    with st.expander(T("env_src3_t")):
        st.markdown(
            f'<p class="ev-x" style="margin-top:2px">'
            f'{_e(c["intro"]["menages"])}</p>'
            '<ul class="ev-puce" style="margin-top:8px">'
            + "".join(f'<li>{_e(p)}</li>' for p in c["menages"]) + '</ul>',
            unsafe_allow_html=True)

    # LE COMPLÉMENT N'EST PLUS APPELÉ PAR LE CADRE. Les trajectoires
    # donnaient les séries mesurées — des résultats — au milieu d'une page qui
    # explique une méthode. Le paramètre reste : la page est aussi rendue
    # depuis l'analyse des résultats, où un complément a du sens.
    if complement is not None:
        complement()

    # ===================== STRATE 3 — APPROFONDIR =========================
    # LE TITRE D'ÉTAGE SUFFIT. Les deux lignes qui le suivaient disaient que
    # ce qui vient est la note de cadrage repliée et que ses seuils sont
    # reproduits tels quels : la première décrit ce que les volets montrent
    # déjà d'eux-mêmes, la seconde s'excusait d'un français que le lecteur
    # voit sans qu'on le lui annonce.
    st.markdown(f'<div class="ev-etage">{_e(T("env_s3"))}</div>',
                unsafe_allow_html=True)

    with st.expander(T("env_v_terrain")):
        st.caption(c["intro"]["bareme"])
        _bloc_terrain(c)

    with st.expander(T("env_v_veg", n=len(c["vegetation"]))):
        st.markdown(_tableau(c["vegetation"]), unsafe_allow_html=True)

    with st.expander(T("env_v_frag", n=len(c["fragmentation"]))):
        st.caption(c["intro"]["fragmentation"])
        st.markdown(_tableau(c["fragmentation"]), unsafe_allow_html=True)

    with st.expander(T("env_v_conn", n=len(c["connectivite"]))):
        st.caption(c["intro"]["connectivite"])
        st.markdown(_tableau(c["connectivite"]), unsafe_allow_html=True)

    with st.expander(T("env_v_cot")):
        _bloc_cotier(c)

    with st.expander(T("env_v_hydro")):
        st.markdown(f'<p class="ev-x" style="max-width:96ch">'
                    f'{_e(c["intro"]["pression"])}</p>'
                    '<ul class="ev-puce" style="margin-top:8px">'
                    + "".join(f'<li>{_e(p)}</li>' for p in c["hydro"])
                    + '</ul>', unsafe_allow_html=True)

    with st.expander(T("env_v_men")):
        st.markdown(f'<p class="ev-x" style="max-width:96ch">'
                    f'{_e(c["intro"]["menages2"])}</p>'
                    '<ul class="ev-puce" style="margin-top:8px">'
                    + "".join(f'<li>{_e(p)}</li>' for p in c["menages"])
                    + '</ul>', unsafe_allow_html=True)
