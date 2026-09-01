"""Accueil — la page d'atterrissage du site.

CE QU'ELLE ANNONCE, ET DANS QUEL ORDRE

Elle a d'abord été un sommaire méthodologique, puis un parcours en deux
écrans. Les deux écrans redisaient ce que « Le territoire » et « Cadre de
résilience » disent déjà en entier dans le menu, et la première chose qu'un
visiteur voyait du site était une pagination. Elle dit maintenant, de haut en
bas, les quatre choses qu'on vient y chercher :

    ce que fait le site  ›  par où entrer  ›  à quoi ça ressemble  ›  sa taille

Le titre et le bouton d'appel vivent dans l'illustration, en haut de page :
c'est le bandeau du site qui les porte, et seulement sur cette page — deux
images empilées, un bandeau puis un héros, auraient dit deux fois la même
chose l'une sous l'autre.

TOUS LES CHIFFRES SONT CALCULÉS. Les dimensions, les indicateurs, les
sections, les ménages, et la couleur de chaque section sur la carte : rien
n'est écrit en dur. La maquette annonçait « 70+ indicateurs, 40+ sources,
20+ territoires » — des chiffres ronds d'illustration. Le site en a de vrais,
et un « 20+ territoires » sur une enquête qui en couvre dix se voit du premier
coup d'œil : ce qu'on perdrait alors n'est pas l'effet d'annonce, c'est la
confiance.

L'AMPLITUDE EST CALCULÉE SUR UNE BASE COMMUNE, ET C'EST LA SEULE FAÇON
HONNÊTE. Comparer Trichet à Quentin sur les 66 indicateurs scorés serait
injuste : deux sections n'ont pas de valeur pour neuf d'entre eux, et leur
indice porterait alors sur un référentiel plus étroit. On ne retient donc,
pour la carte et pour le classement, que les 57 indicateurs renseignés POUR
LES DIX sections. L'indice global publié, lui, reste celui du référentiel
entier.
"""

import json
import os
from urllib.parse import quote

import streamlit as st

import assets
import i18n
import icones
import map_render
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"
VERT, BLEU, AMBRE, ROUGE, GRIS = ("#1a8a4f", "#2166ac", "#d1730c",
                                  "#c33a24", "#8a93a5")

SECTIONS = ["Anse à Drick", "Barbois", "Dumont", "Débouchette", "Mouline",
            "Quentin", "Beaulieu", "Blactote", "Dalmette", "Trichet"]
DIM_CLE = {
    "I. PHYSICAL AND INFRASTRUCTURAL DIMENSION": "dim1",
    "II. INSTITUTIONAL, TECHNOLOGICAL, AND GOVERNANCE  DIMENSION": "dim2",
    "III.  ENVIRONMENTAL AND ECOLOGICAL DIMENSION": "dim3",
    "IV. ECONOMIC, LIVELIHOODS, AND FOOD SECURITY DIMENSION": "dim4",
    "V. SOCIAL AND COMMUNITY DIMENSION": "dim5",
    "VI. HUMAN DIMENSION": "dim6",
    "VII. CULTURAL, IDENTITY-BASED, AND PSYCHOLOGICAL DIMENSION": "dim7",
}
TEINTES = {"dim1": "#d1730c", "dim2": "#2166ac", "dim3": "#1a8a4f",
           "dim4": "#a02c8f", "dim5": "#0f8fa8", "dim6": "#c33a24",
           "dim7": "#7048b6"}

# DEUX ÉTAPES, PLUS QUATRE. « Les résultats clés » et « Les pistes d'action »
# ont été retirés du parcours d'accueil : leur contenu n'était pas au niveau du
# reste, et un écran à moitié fait sur la page d'entrée coûte plus cher en
# crédibilité qu'il ne rapporte en complétude. Les deux sujets restent traités
# en profondeur dans leurs propres rubriques — Analyse des résultats et Fiches
# d'intervention — qui sont dans le menu. Les listes commandent tout : la
# rangée d'onglets, la borne du bouton Suivant et le sommaire des écrans.
TEXTES = {
    "mode_portail": {"en": "Home", "fr": "Accueil"},
    "po_titre": {"en": "Landscape resilience observatory",
                 "fr": "Observatoire de la résilience des paysages"},
    "po_sous": {"en": "Sud and Grand'Anse, Haiti · survey 2024",
                "fr": "Sud et Grand'Anse, Haïti · enquête 2024"},

    # --- LE HÉROS. Il est écrit ici et lu par le bandeau, dans app.py :
    # le texte d'une page appartient à la page, même quand c'est l'en-tête
    # du site qui le dessine.
    "po_hero_t": {"en": "Building resilient landscapes, together.",
                  "fr": "Construire des paysages résilients, ensemble."},
    "po_hero_x": {
        "en": "APRI brings together survey data, satellite records and "
              "community knowledge to measure the resilience of a territory "
              "and support the decisions that follow.",
        "fr": "APRI réunit les données d'enquête, les relevés satellitaires "
              "et la connaissance des communautés pour mesurer la résilience "
              "d'un territoire et éclairer les décisions qui en découlent."},
    "po_hero_b": {"en": "Explore the territory",
                  "fr": "Explorer le territoire"},

    # --- LES QUATRE PORTES. Chacune mène à une rubrique qui existe déjà ;
    # la description dit ce qu'on y trouve, pas ce qu'elle promet.
    "po_c1": {"en": "Explore the territory", "fr": "Explorer le territoire"},
    "po_c1x": {"en": "The ten communal sections, their maps and their "
                     "landscapes.",
               "fr": "Les dix sections communales, leurs cartes et leurs "
                     "paysages."},
    "po_c2": {"en": "Resilience framework", "fr": "Cadre de résilience"},
    "po_c2x": {"en": "The seven dimensions, and how a score is built.",
               "fr": "Les sept dimensions, et comment un score se construit."},
    "po_c3": {"en": "Indicators & data", "fr": "Indicateurs et données"},
    "po_c3x": {"en": "Every indicator, its source and its raw values.",
               "fr": "Chaque indicateur, sa source et ses valeurs brutes."},
    "po_c4": {"en": "Maps & results", "fr": "Cartes et résultats"},
    "po_c4x": {"en": "Scores dimension by dimension, section by section.",
               "fr": "Les scores dimension par dimension, section par "
                     "section."},

    # --- COMPRENDRE, MESURER, AGIR
    "po_uma_t": {"en": "Understand. Measure. Act.",
                 "fr": "Comprendre. Mesurer. Agir."},
    "po_uma_x": {
        "en": "APRI reads a territory as a system and measures it across "
              "seven dimensions, before a shock rather than after it. The "
              "result is not a ranking but a map of where a landscape holds "
              "and where it gives way.",
        "fr": "APRI lit un territoire comme un système et le mesure sur sept "
              "dimensions, avant le choc et non après. Ce qui en sort n'est "
              "pas un classement mais la carte de ce qui tient et de ce qui "
              "cède dans un paysage."},
    "po_uma_b": {"en": "Learn more about APRI", "fr": "En savoir plus sur APRI"},
    "po_uma_leg": {"en": "Overall resilience score",
                   "fr": "Indice global de résilience"},

    # --- LA BANDE DE CHIFFRES, tous comptés dans les fichiers
    "po_ch1": {"en": "Resilience dimensions", "fr": "Dimensions de résilience"},
    "po_ch2": {"en": "Indicators", "fr": "Indicateurs"},
    "po_ch3": {"en": "Communal sections", "fr": "Sections communales"},
    "po_ch4": {"en": "Households surveyed", "fr": "Ménages enquêtés"},

    # --- LE PIED
    "po_pied_p": {"en": "Produced by", "fr": "Réalisé par"},
    "po_pied_c": {"en": "APRI · Survey 2024", "fr": "APRI · Enquête 2024"},

    "po_absent": {
        "en": "The results file is missing; the home page cannot be built.",
        "fr": "Le fichier de résultats est absent ; la page d'accueil ne "
              "peut pas être construite."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)

STYLE = """
<style>
  /* ================ LA PAGE D'ATTERRISSAGE ============================
     Une seule règle gouverne tout : rien n'est encadré sauf ce qui se
     clique. Les quatre portes sont des cartes parce qu'on les prend ; la
     bande de chiffres est une surface parce qu'elle se lit d'un bloc ; le
     reste est du texte posé sur du blanc. */

  /* --- comprendre, mesurer, agir --- */
  .uma-t   { font-size:31px; font-weight:800; color:#12314c;
             letter-spacing:-.025em; line-height:1.15; margin:8px 0 0; }
  .uma-x   { font-size:14.5px; line-height:1.68; color:#4a5b70;
             margin:18px 0 22px; max-width:46ch; text-align:left !important; }
  /* LA CARTE PORTE SA LÉGENDE DANS SON COIN, pas au-dessus d'elle. Une
     légende posée en surtitre oblige à faire l'aller-retour ; posée sur le
     fond marin, à gauche, elle est dans le même regard que les couleurs
     qu'elle explique. */
  .uma-carte { position:relative; border-radius:12px; overflow:hidden;
               border:1px solid #e8edf3; background:#f4f8fc; }
  .uma-carte svg { display:block; width:100%; height:auto; }
  .uma-leg { position:absolute; left:16px; top:16px; background:#ffffff;
             border:1px solid #e8edf3; border-radius:9px; padding:11px 13px;
             box-shadow:0 2px 10px rgba(16,23,40,.06); }
  .uma-leg b { display:block; font-size:11px; font-weight:700; color:#3c4761;
               margin-bottom:8px; max-width:15ch; line-height:1.35; }
  .uma-lg  { display:flex; align-items:center; gap:8px; font-size:11px;
             color:#6b7590; margin-top:4px; }
  .uma-lg span { width:16px; height:11px; border-radius:2px;
                 box-shadow:inset 0 0 0 1px rgba(0,0,0,.10); }
  div[class*="st-key-po_uma_lien"] button {
    background:transparent !important; border:none !important;
    box-shadow:none !important; transform:none !important;
    padding:2px 0 4px !important; min-height:0 !important;
    border-bottom:2px solid transparent !important; border-radius:0 !important;
  }
  /* LA SPÉCIFICITÉ EST DOUBLÉE À DESSEIN. La règle générale des boutons,
     dans app.py, a exactement le même poids ; à égalité c'est l'ordre qui
     tranche, et l'ordre dépend de l'endroit où Streamlit insère le bloc.
     Répéter l'attribut fait pencher la balance une fois pour toutes. */
  div[class*="st-key-po_uma_lien"][class*="st-key-po_uma_lien"] button p {
    font-size:14px !important; font-weight:700 !important;
    color:#2f6b4f !important; margin:0 !important;
    text-align:left !important;
  }
  div[class*="st-key-po_uma_lien"] button:hover {
    border-bottom-color:#2f6b4f !important; background:transparent !important;
  }

  /* --- la bande de chiffres --- */
  .po-bande { display:grid; grid-template-columns:repeat(4,1fr);
              background:#f7faf8; border-radius:14px; margin:42px 0 0;
              padding:6px 0; }
  .po-bc   { display:flex; align-items:center; gap:14px;
             padding:24px 26px; border-left:1px solid #e6eeea; }
  .po-bc:first-child { border-left:none; }
  .po-bn   { font-size:27px; font-weight:800; color:#12314c; line-height:1;
             letter-spacing:-.03em; font-variant-numeric:tabular-nums; }
  .po-bl   { font-size:12.5px; color:#5c6b7e; margin-top:7px;
             text-align:left !important; }

  /* --- le pied --- */
  .po-pied { display:flex; align-items:center; justify-content:space-between;
             gap:26px; flex-wrap:wrap; margin:40px 0 6px; padding:26px 2px 0;
             border-top:1px solid #eef2f7; }
  .po-pm   { display:flex; align-items:center; gap:13px; }
  .po-pm img { height:42px; width:42px; display:block; }
  .po-pm b { display:block; font-size:19px; font-weight:800; color:#12314c;
             letter-spacing:-.02em; line-height:1; }
  .po-pm span { display:block; font-size:11.5px; color:#6b7590; margin-top:4px;
                max-width:30ch; line-height:1.4; text-align:left !important; }
  .po-pp   { display:flex; align-items:center; gap:14px; }
  .po-pp span { font-size:11.5px; color:#8a93a5; }
  .po-pp img { height:34px; display:block; }
  .po-pc   { font-size:11.5px; color:#8a93a5; }

  @media (max-width:1100px){ .po-bande{grid-template-columns:repeat(2,1fr)}
    .po-bc:nth-child(3){border-left:none} }
  @media (max-width:760px){ .po-bande{grid-template-columns:1fr}
    .po-bc{border-left:none} .uma-t{font-size:25px} }
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
def _mesures(lang):
    """Tout ce que la page affiche de chiffré, en une lecture.

    `lang` n'est pas décoratif : les noms d'indicateurs changent avec la
    langue, et sans lui le cache figerait la première langue affichée.
    """
    p = _trouver("resultats.json")
    if not p:
        return None
    with open(p, encoding="utf-8") as f:
        res = json.load(f)
    res = res["indicateurs"] if isinstance(res, dict) and "indicateurs" in res \
        else res
    scores = [r for r in res
              if (r.get("scores_corriges") or {}).get("Total") is not None]

    def moyenne(cle, lst):
        n = d = 0.0
        for r in lst:
            v = (r.get("scores_corriges") or {}).get(cle)
            if v is None:
                continue
            p_ = r.get("ponderation") or 1
            n += p_ * float(v)
            d += p_
        return (n / d) if d else None

    # base commune : les indicateurs renseignés POUR LES DIX sections
    commun = [r for r in scores
              if all((r.get("scores_corriges") or {}).get(s) is not None
                     for s in SECTIONS)]
    par_section = {s: moyenne(s, commun) for s in SECTIONS}
    ordre = sorted(par_section.items(), key=lambda kv: -(kv[1] or 0))

    # dimensions : score pondéré et poids, sur tout le référentiel
    dims = {}
    for r in res:
        cle = DIM_CLE.get(r.get("dimension") or "")
        if not cle:
            continue
        e = dims.setdefault(cle, {"num": 0.0, "den": 0.0, "n": 0, "faits": 0})
        e["n"] += 1
        v = (r.get("scores_corriges") or {}).get("Total")
        if v is not None:
            e["faits"] += 1
            p_ = r.get("ponderation") or 1
            e["num"] += p_ * float(v)
            e["den"] += p_
    for e in dims.values():
        e["score"] = (e["num"] / e["den"]) if e["den"] else None

    # les trois indicateurs qui coûtent le plus à l'indice
    def nom(r):
        if lang == "fr" and r.get("indicateur_fr"):
            return r["indicateur_fr"]
        return r.get("indicateur", "")

    couteux = sorted(
        scores,
        key=lambda r: -((r.get("ponderation") or 1)
                        * (10 - float(r["scores_corriges"]["Total"]))))[:3]
    faits = [{"nom": nom(r),
              "score": float(r["scores_corriges"]["Total"]),
              "valeur": (r.get("valeurs") or {}).get("Total"),
              "unite": (r.get("unite") or "").strip()
                       or ("%" if "%" in (r.get("metrique") or "") else ""),
              "dim": DIM_CLE.get(r.get("dimension") or "")}
             for r in couteux]

    # LA DISTRIBUTION SUR L'ÉCHELLE, EN PART DE POIDS ET NON EN NOMBRE.
    # Compter les indicateurs traiterait un indicateur pesant 4,6 comme un
    # indicateur pesant 1 ; c'est le poids qui fait la moyenne, c'est donc le
    # poids qu'il faut étaler.
    poids_total = sum((r.get("ponderation") or 1) for r in scores) or 1
    bandes = []
    for a_, b_, lab in ((0, 2, "0–2"), (3, 4, "3–4"), (5, 6, "5–6"),
                        (7, 8, "7–8"), (9, 10, "9–10")):
        g = [r for r in scores
             if a_ <= float(r["scores_corriges"]["Total"]) <= b_]
        bandes.append({"lab": lab, "n": len(g),
                       "part": sum((r.get("ponderation") or 1)
                                   for r in g) / poids_total * 100,
                       "milieu": (a_ + b_) / 2})

    paysages = {p_: moyenne(p_, scores) for p_ in ("Littoral", "Montagne")}

    bases = [int((r.get("n") or {}).get("Total") or 0) for r in scores]
    bases = [b for b in bases if b]
    p_idx = _trouver("croisement_index.json")
    menages = None
    if p_idx:
        try:
            with open(p_idx, encoding="utf-8") as f:
                menages = int(json.load(f).get("n") or 0)
        except Exception:
            menages = None
    if not menages and bases:
        menages = max(set(bases), key=bases.count)

    # L'EFFECTIF PAR SECTION SE PREND AU MODE, PAS AU MAXIMUM.
    # Chaque indicateur porte son propre effectif : certains ne concernent
    # qu'une partie des ménages — les enfants scolarisés, les parcelles
    # cultivées. Le maximum surestimerait donc l'échantillon ; la valeur la
    # plus fréquente est celle de la question posée à tout le monde, et les
    # modes des dix sections se somment bien au total de l'enquête.
    from collections import Counter
    sections_n = {}
    for sec in SECTIONS:
        vals = [(e.get("n") or {}).get(sec) for e in res]
        vals = [v for v in vals if v]
        if vals:
            sections_n[sec] = Counter(vals).most_common(1)[0][0]

    return {"sections_n": sections_n,
            "indice": moyenne("Total", scores), "n_scores": len(scores),
            "n_commun": len(commun), "sections": ordre, "dims": dims,
            "faits": faits, "menages": menages, "bandes": bandes,
            "paysages": paysages}


def _fond_icone(nom, couleur="#2f6b4f", taille=26):
    """Une icône du module commun, prête à servir de `background-image`.

    POURQUOI UN FOND ET NON UN MASQUE. Le masque du module `icones` colore le
    dessin avec la couleur de fond de l'élément — parfait pour une icône seule,
    inutilisable pour une icône POSÉE DANS une pastille : la pastille et le
    tracé demanderaient deux couleurs de fond au même élément. En image de
    fond, la pastille garde son vert pâle et le tracé porte la sienne.
    """
    # L'ESPACE DE NOMS EST OBLIGATOIRE DANS UNE URL DE DONNÉES.
    # Un SVG écrit dans du HTML hérite de l'espace de noms du document ;
    # chargé comme image, il est un document à lui seul, et sans
    # `xmlns` le navigateur ne le dessine pas — sans erreur, juste un
    # fond vide.
    brut = icones.svg(nom, couleur, taille).replace(
        "<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
    return 'url("data:image/svg+xml,%s")' % quote(brut)


def _aller(mode):
    st.session_state["app_mode"] = mode


# LES QUATRE ENTRÉES DU SITE, ET RIEN QUE QUATRE.
# Le menu de gauche en compte douze : c'est la table des matières, elle sert
# à qui sait déjà ce qu'il cherche. La page d'accueil s'adresse à qui ne le
# sait pas encore, et quatre portes se choisissent d'un coup d'œil là où
# douze se lisent une par une.
ENTREES = (("po_c1", "monde", "accueil"),
           ("po_c2", "pousse", "methodologie"),
           ("po_c3", "barres", "donnees"),
           ("po_c4", "carte", "dimensions"))


def _css_entrees():
    """La feuille des quatre cartes d'entrée, une règle par carte.

    Streamlit ne pose qu'un seul libellé sur un bouton : la pastille et le
    texte de description sont donc écrits en CSS, dans les pseudo-éléments
    ::before et ::after, à partir de textes injectés depuis Python. La feuille
    étant régénérée à chaque rendu, la description suit la langue.
    """
    r = ["<style>"]
    for cle, ic, _mode in ENTREES:
        b = f'div[class*="st-key-po_e_{cle}"] button'
        r.append(f"""
        {b}, {b}[kind="primary"] {{
          display:grid !important;
          grid-template-rows:auto auto auto; row-gap:0;
          justify-items:center; align-content:start;
          text-align:center !important;
          padding:26px 20px 24px !important;
          min-height:236px !important; height:100% !important;
          background:#ffffff !important;
          border:1px solid #e8edf3 !important; border-radius:12px !important;
          box-shadow:none !important; transform:none !important;
          transition:border-color .15s ease, box-shadow .15s ease;
        }}
        {b}:hover, {b}[kind="primary"]:hover {{
          border-color:#cfe3d7 !important;
          box-shadow:0 2px 14px rgba(16,23,40,.06) !important;
        }}
        {b}::before, {b}[kind="primary"]::before {{
          content:""; grid-row:1;
          width:64px; height:64px; border-radius:50%;
          background:#eaf3ed {_fond_icone(ic)} center/26px no-repeat;
          margin-bottom:18px;
        }}
        {b} > div, {b}[kind="primary"] > div {{
          grid-row:2; justify-self:center !important; width:auto !important;
        }}
        {b} p, {b}[kind="primary"] p {{
          font-size:15px !important; font-weight:700 !important;
          color:#12314c !important; margin:0 !important;
          text-align:center !important; line-height:1.3 !important;
        }}
        {b}::after, {b}[kind="primary"]::after {{
          content:"{_txt_css(T(cle + 'x'))}"; grid-row:3;
          margin-top:11px; max-width:24ch;
          font-size:12.5px; font-weight:500; color:#6b7590;
          line-height:1.55; white-space:pre-wrap;
        }}""")
    r.append("</style>")
    return "".join(r)


def _txt_css(t):
    """Un texte prêt pour `content:` — les guillemets et les barres obliques
    inverses y sont des délimiteurs, pas des caractères."""
    return t.replace("\\", "\\\\").replace('"', '\\"')


def _entrees():
    st.markdown(_css_entrees(), unsafe_allow_html=True)
    cols = st.columns(len(ENTREES), gap="medium")
    for col, (cle, _ic, mode) in zip(cols, ENTREES):
        with col:
            st.button(T(cle), key=f"po_e_{cle}", on_click=_aller,
                      args=(mode,), use_container_width=True)


# ------------------------------------------------- comprendre, mesurer, agir
def _carte_indice(m):
    """La carte des dix sections, colorée par l'indice global.

    C'EST LA SEULE CARTE DU SITE QUI PORTE UN SCORE SUR LA PAGE D'ACCUEIL, et
    c'est délibéré : la promesse de la page est « on mesure la résilience d'un
    territoire », et une carte muette ne la tient pas. Les valeurs sont celles
    du référentiel commun aux dix sections — le seul qui permette de les
    comparer entre elles.
    """
    valeurs = {s: (round(v, 2) if v is not None else None)
               for s, v in m["sections"]}
    dispo = [v for v in valeurs.values() if v is not None]
    if not dispo:
        return None
    seuils = map_render.nice_thresholds(dispo)
    svg, seuils_ret, _ = map_render.render_map_svg(
        valeurs, {s: 1 for s in SECTIONS}, seuils, height=430,
        polarity="eleve_bon", unite="")
    paves = "".join(
        f'<div class="uma-lg"><span style="background:{c}"></span>{_e(lab)}'
        f'</div>'
        for c, lab in map_render.legend_items(seuils_ret, "eleve_bon", ""))
    return (f'<div class="uma-carte">{svg}'
            f'<div class="uma-leg"><b>{_e(T("po_uma_leg"))}</b>{paves}</div>'
            f'</div>')


def _comprendre(m):
    g, d = st.columns([1, 1.35], gap="large")
    with g:
        st.markdown(f'<div class="uma-t">{_e(T("po_uma_t"))}</div>'
                    f'<p class="uma-x">{_e(T("po_uma_x"))}</p>',
                    unsafe_allow_html=True)
        st.button(T("po_uma_b") + "   →", key="po_uma_lien",
                  on_click=_aller, args=("methodologie",))
    with d:
        c = _carte_indice(m)
        if c:
            st.markdown(c, unsafe_allow_html=True)


# ------------------------------------------------------- la bande de chiffres
def _chiffres(m):
    """Quatre nombres, et tous les quatre sont comptés dans les fichiers.

    LA MAQUETTE ANNONÇAIT « 70+ indicateurs, 40+ sources, 20+ territoires ».
    Ce sont des chiffres ronds d'illustration, et le site en a de vrais : 128
    indicateurs, dix sections, 1 211 ménages. Un « 20+ territoires » sur une
    enquête qui en couvre dix se voit du premier coup d'œil, et ce qu'on perd
    alors n'est pas l'effet d'annonce, c'est la confiance.
    """
    n_ind = sum(e["n"] for e in m["dims"].values())
    men = f'{m["menages"]:,}'.replace(",", " ") if m["menages"] else "—"
    cases = (("couches", str(len(m["dims"])), T("po_ch1")),
             ("points", str(n_ind), T("po_ch2")),
             ("epingle", str(len(SECTIONS)), T("po_ch3")),
             ("personnes", men, T("po_ch4")))
    st.markdown(
        '<div class="po-bande">' + "".join(
            f'<div class="po-bc">{icones.svg(ic, "#2f6b4f", 27)}'
            f'<div><div class="po-bn">{_e(v)}</div>'
            f'<div class="po-bl">{_e(lab)}</div></div></div>'
            for ic, v, lab in cases)
        + '</div>', unsafe_allow_html=True)


# ------------------------------------------------------------- le pied de page
def _pied():
    """Le pied : le commanditaire, et lui seul.

    LA MAQUETTE ALIGNE QUATRE LOGOS — FEM, PNUE, FAO, PNUD. Je n'ai que celui
    du PNUE, et surtout je n'ai aucune source disant que les trois autres
    institutions sont partenaires de CETTE enquête. Afficher un logo est une
    affirmation ; celle-là, il faut que tu me la confirmes avant que je
    l'écrive. La ligne reste donc au PNUE, et la place des autres est prête.
    """
    st.markdown(
        f'<div class="po-pied">'
        f'<div class="po-pm">'
        f'<img alt="APRI" src="data:image/png;base64,{assets.EMBLEME_APRI}">'
        f'<div><b>APRI</b><span>{_e(T("a_titre_court"))}</span></div>'
        f'</div>'
        f'<div class="po-pp"><span>{_e(T("po_pied_p"))}</span>'
        f'<img alt="UNEP" src="data:image/png;base64,'
        f'{assets.LOGO_UNEP_BLEU}"></div>'
        f'<div class="po-pc">{_e(T("po_pied_c"))}</div>'
        f'</div>', unsafe_allow_html=True)


def render():
    """La page d'accueil : une page d'atterrissage, plus un parcours.

    ELLE A CESSÉ D'ÊTRE UN SOMMAIRE EN DEUX ÉTAPES. Les deux écrans — le
    territoire d'étude, la méthodologie — redisaient ce que « Le territoire »
    et « Cadre de résilience » disent déjà en entier dans le menu, et la
    première chose qu'on voyait du site était une pagination. La page annonce
    maintenant ce que le site fait, ouvre quatre portes, montre une carte
    portant un résultat, et donne les quatre nombres qui disent la taille du
    travail. Le titre et le bouton d'appel vivent dans l'illustration, en
    haut : c'est le bandeau du site qui les porte, sur cette page seulement.
    """
    st.markdown(STYLE, unsafe_allow_html=True)
    m = _mesures(i18n.get_lang())
    if not m:
        st.info(T("po_absent"))
        return
    _entrees()
    _comprendre(m)
    _chiffres(m)
    _pied()
