"""Accueil — la page d'atterrissage du site.

CE QU'ELLE ANNONCE, ET DANS QUEL ORDRE

Elle a d'abord été un sommaire méthodologique, puis un parcours en deux
écrans. Les deux écrans redisaient ce que « Le territoire » et « Cadre de
résilience » disent déjà en entier dans le menu, et la première chose qu'un
visiteur voyait du site était une pagination. Elle dit maintenant, de haut en
bas, les quatre choses qu'on vient y chercher :

    ce que fait le site  ›  par où entrer  ›  à quoi ça ressemble

Le titre et le bouton d'appel vivent dans l'illustration, en haut de page :
c'est le bandeau du site qui les porte, et seulement sur cette page — deux
images empilées, un bandeau puis un héros, auraient dit deux fois la même
chose l'une sous l'autre.

LA CARTE EST CALCULÉE, ET C'EST LA SEULE CHOSE CHIFFRÉE DE LA PAGE. La
couleur de chaque section vient des résultats, pas d'un fichier de
présentation. Une bande de quatre grands nombres et une rangée de logos
institutionnels ont été essayées puis retirées : la première répétait ce que
les rubriques disent mieux, la seconde affirmait des partenariats que rien
dans les données ne documente.

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
import re

import streamlit as st

import i18n
import map_render
# LA VIGNETTE DE LOCALISATION EXISTE DÉJÀ, ET ELLE EST BONNE. « Le
# territoire » la dessine depuis toujours : l'île entière, la République
# dominicaine nommée en retrait, la zone enquêtée en vert dans son cercle.
# La redessiner ici aurait donné deux dessins du même objet, qui auraient
# divergé au premier ajustement.
import territoire_page
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


    # --- LES CINQ PORTES. Chacune mène à une rubrique du menu, dans le même
    # ordre que lui ; la description dit ce qu'on y trouve, pas ce qu'elle
    # promet. Les libellés sont ceux du menu, à un mot près : « Télécharger
    # les données » annonce ce qu'on vient y faire, là où l'onglet se contente
    # de nommer la rubrique.
    "po_c1": {"en": "Explore the Territory", "fr": "Explorer le territoire"},
    "po_c1x": {"en": "Ten communal sections, their maps and landscapes.",
               "fr": "Dix sections communales, leurs cartes et leurs "
                     "paysages."},
    "po_c2": {"en": "Resilience Framework", "fr": "Cadre de résilience"},
    "po_c2x": {"en": "Seven dimensions and how each score is constructed.",
               "fr": "Sept dimensions et comment chaque score se construit."},
    "po_c3": {"en": "Results Analysis", "fr": "Analyse des résultats"},
    "po_c3x": {"en": "Scores, profiles and cross-tabulated results.",
               "fr": "Scores, profils et croisements de résultats."},
    "po_c4": {"en": "Feedback Loops", "fr": "Boucles de rétroaction"},
    "po_c4x": {"en": "Causal relationships and systemic leverage points.",
               "fr": "Relations causales et leviers systémiques."},
    "po_c5": {"en": "Download Data", "fr": "Télécharger les données"},
    "po_c5x": {"en": "Indicators, sources and downloadable datasets.",
               "fr": "Indicateurs, sources et jeux de données "
                     "téléchargeables."},

    # --- CE QU'APRI MESURE, EN UNE PHRASE
    "po_uma_x": {
        "en": "APRI measures resilience, that is a territory's capacity to "
              "anticipate, absorb and adapt, through a set of indicators "
              "grouped into seven dimensions and converted into a 0-to-10 "
              "score by the framework's scales. All of it at landscape "
              "scale, the landscape understood as a complex adaptive system.",
        "fr": "APRI mesure la résilience, c'est-à-dire la capacité d'un "
              "territoire à anticiper, absorber et s'adapter, au travers "
              "d'une série "
              "d'indicateurs regroupés en sept dimensions et convertis en un "
              "score de 0 à 10 par les barèmes du cadre. Le tout à l'échelle "
              "du paysage, entendu comme un système complexe adaptatif."},
    "po_uma_sur": {"en": "What APRI measures", "fr": "Ce que mesure APRI"},
    # LA CARTE NE PORTE PLUS DE SCORE : son titre dit donc ce qu'elle
    # montre, c'est-à-dire l'emprise de l'enquête et rien d'autre.
    "po_carte_cap": {
        "en": "The ten surveyed communal sections, in the Sud and "
              "Grand'Anse pilot landscape.",
        "fr": "Les dix sections communales enquêtées, dans le paysage "
              "pilote du Sud et de la Grand'Anse."},


    "po_absent": {
        "en": "The results file is missing; the home page cannot be built.",
        "fr": "Le fichier de résultats est absent ; la page d'accueil ne "
              "peut pas être construite."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)

STYLE = """
<style>
  /* ================ TOUT TIENT DANS UN ÉCRAN ==========================
     LA PAGE D'ACCUEIL NE DOIT PAS SE FAIRE DÉROULER. Elle est ce qu'on voit
     du site avant de savoir ce qu'il contient : si la carte — la seule chose
     qui montre un résultat — se trouve sous la ligne de flottaison, on part
     avec l'idée d'un sommaire, pas d'un observatoire. Chaque bloc est donc
     rétréci jusqu'à ce que l'ensemble tienne dans une fenêtre ordinaire.

     LES RÈGLES NE VALENT QUE SUR CETTE PAGE, sans qu'on ait à marquer le
     corps du document : cette feuille n'est écrite que par la page
     d'accueil, et arrive après celle de l'application, donc elle l'emporte.
     Les autres pages gardent le bandeau et les proportions d'origine. */
  .bandeau-fond { height: 152px !important; }
  .bandeau-marque { left: 34px !important; gap: 15px !important; }
  .bandeau-marque .bm-embleme { height: 66px !important; width: 66px !important; }
  .bandeau-marque .bm-nom { font-size: 29px !important; }
  .bandeau-marque .bm-filet { margin: 5px 0 6px !important; }
  .bandeau-marque .bm-base { font-size: 12.5px !important; }
  .bandeau-marque .bm-lieu { font-size: 12px !important; margin-top: 3px !important; }
  .bandeau-logo { top: 14px !important; right: 24px !important;
                  height: 44px !important; }

  /* ================ LA PAGE D'ATTERRISSAGE ============================
     Une seule règle gouverne tout : rien n'est encadré sauf ce qui se
     clique. Les quatre portes sont des cartes parce qu'on les prend ; la
     bande de chiffres est une surface parce qu'elle se lit d'un bloc ; le
     reste est du texte posé sur du blanc. */

  /* --- CE QU'APRI MESURE : LE MESSAGE PRINCIPAL DE LA PAGE --------------
     C'EST LA PHRASE QUI DOIT ÊTRE LUE, ET ELLE DOIT ÊTRE LA PLUS GROSSE.
     À 15,5 px elle avait la taille d'un paragraphe courant : posée à côté
     d'une carte, elle passait pour une légende. Elle monte à 20 px, sur une
     colonne de 42 signes — la largeur où l'œil retrouve seul le début de la
     ligne suivante — et devient ce qu'elle est : la définition qu'un
     visiteur doit avoir lue avant tout le reste.

     LE MOT « APRI » EST DÉTACHÉ EN VERT, en tête. Il ne s'agit pas d'un
     ornement : le nom du dispositif est le sujet de la phrase, et le lire
     d'abord met le reste en place. Le surtitre, lui, dit à quoi sert le
     paragraphe qui suit, ce qu'aucune mise en forme ne peut dire seule. */
  .uma-sur { font-size:11px; font-weight:700; color:#8a93a5;
             letter-spacing:.09em; text-transform:uppercase;
             margin:0 0 10px; }
  /* Le `!important` et la mesure en `em` ne sont pas des caprices : la
     feuille de l'application fixe 14,5 px à tous les paragraphes du contenu,
     avec une spécificité supérieure, et la largeur en `ch` se calcule sur la
     police du CADRE, pas sur celle du texte — d'où une boîte de 44 signes
     qui n'en tenait que trente. Le cadre porte donc lui aussi la taille. */
  p.uma-x  { font-size:20px !important; line-height:1.55 !important;
             color:#1c2b3a !important;
             margin:0; font-weight:450; letter-spacing:-.005em; }
  p.uma-x b { font-weight:800; color:#1a6b52; letter-spacing:0; }
  /* Le filet vert et le fond très pâle en font ce qu'elle est — la
     définition de référence, celle qu'on revient chercher. Le vert est celui
     du cadre de résilience, où la même définition se déplie en entier. */
  .uma-cadre { border:1px solid #dde9e3; border-left:4px solid #1a6b52;
               border-radius:12px; background:#f6faf8;
               font-size:20px;
               padding:24px 28px 26px; margin:2px 0 0; max-width:42ch; }
  /* LA CARTE N'A NI CADRE NI FOND, ET LA MER EST TRANSPARENTE.
     Encadrée sur un aplat bleu, elle formait une vignette collée au milieu
     d'une page blanche — un objet rapporté. Le rectangle marin est effacé
     (la règle `.sea` du SVG est neutralisée depuis ici) : il ne reste que
     l'île et ses couleurs, posées à même la page. La légende, du coup, n'a
     plus de fond sur lequel se poser : elle passe au-dessus de la carte, en
     une ligne de pastilles. */
  .uma-carte { position:relative; }
  /* LA CARTE PREND CE QUI RESTE DE LA FENÊTRE, ET PAS PLUS.
     Une hauteur fixe tient sur un écran et déborde sur le suivant. Le
     plafond est donc ce qui reste sous la barre, le bandeau et les quatre
     portes — d'où la constante retranchée. Le dessin garde ses proportions
     (`preserveAspectRatio` par défaut) : il rétrécit, il ne s'écrase pas.
     Le plancher de 205 px est le point où la carte cesse d'être lisible :
     en dessous, on préfère que la page défile. */
  .uma-carte svg { display:block; width:100%; height:auto;
                   margin:0 !important;
                   max-height: max(205px, calc(100vh - 418px)); }
  .uma-carte svg .sea { fill:transparent !important; }
  .uma-zone   { position:relative; }
  /* LA PHRASE EST AU-DESSUS DE LA CARTE, ET EN GRAS. Rangée dessous et en
     gris pâle, elle se lisait comme une mention légale — après le dessin,
     alors qu'elle dit ce qu'il faut savoir pour le lire. C'est un titre :
     elle prend donc la place et le poids d'un titre. Le `!important` est
     nécessaire — la feuille de l'application fixe la taille et l'alignement
     de tous les paragraphes du contenu, avec une spécificité supérieure. */
  p.uma-n  { font-size:13.5px !important; font-weight:700;
             color:#3c4761 !important; margin:0 0 12px;
             line-height:1.45 !important; max-width:52ch;
             text-align:left !important; }
  /* LA VIGNETTE RÉPOND À « OÙ EST-CE ? », que la carte détaillée ne peut pas
     dire : cadrée sur la presqu'île, elle montre dix sections sans montrer
     le pays. Le badge est large et bas — l'île l'est aussi — ce qui le fait
     tenir sous la définition sans pousser la page. */
  .uma-badge { margin:14px 0 0; max-width:300px; }

  @media (max-width:760px){ .uma-t{font-size:25px} }
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


def _aller(mode):
    st.session_state["app_mode"] = mode


# LES CINQ ENTRÉES DU SITE, ET RIEN QUE CINQ.
# La barre du haut en compte huit : c'est la table des matières, elle sert à
# qui sait déjà ce qu'il cherche. La page d'accueil s'adresse à qui ne le
# sait pas encore, et cinq portes se choisissent d'un coup d'œil là où huit
# se lisent une par une.
# L'ORDRE EST CELUI DU MENU, ET C'EST LE SEUL QUI SE DÉFENDE. Deux rangées
# d'entrées vers les mêmes rubriques, dans deux ordres différents, obligent à
# relire : le lecteur cherche « Analyse des résultats » en quatrième position
# parce qu'il l'a vue là-haut, et la trouve en troisième. Elles disent
# maintenant la même chose dans le même ordre.
#
# ET IL N'Y A PLUS DE PICTOGRAMME. Une pastille verte devant chaque titre
# annonçait une différence entre les portes ; les dessins —
# un globe, une pousse, des barres, une carte — ne disaient rien que le titre
# ne dise mieux, et coûtaient cinquante pixels de hauteur sur une page qui
# doit tenir dans un écran.
ENTREES = (("po_c1", "accueil"),
           ("po_c2", "methodologie"),
           ("po_c3", "dimensions"),
           ("po_c4", "boucles"),
           ("po_c5", "donnees"))


def _css_entrees():
    """La feuille des quatre cartes d'entrée, une règle par carte.

    Streamlit ne pose qu'un seul libellé sur un bouton : le texte de
    description est donc écrit en CSS, dans le pseudo-élément ::after, à
    partir d'un texte injecté depuis Python. La feuille étant régénérée à
    chaque rendu, la description suit la langue.
    """
    r = ["<style>"]
    for cle, _mode in ENTREES:
        b = f'div[class*="st-key-po_e_{cle}"] button'
        r.append(f"""
        {b}, {b}[kind="primary"] {{
          display:grid !important;
          grid-template-rows:auto auto; row-gap:0;
          justify-items:center; align-content:center;
          text-align:center !important;
          padding:16px 16px 17px !important;
          min-height:96px !important; height:100% !important;
          background:#ffffff !important;
          border:1px solid #e8edf3 !important; border-radius:12px !important;
          box-shadow:none !important; transform:none !important;
          transition:border-color .15s ease, box-shadow .15s ease;
        }}
        {b}:hover, {b}[kind="primary"]:hover {{
          border-color:#cfe3d7 !important;
          box-shadow:0 2px 14px rgba(16,23,40,.06) !important;
        }}
        {b} > div, {b}[kind="primary"] > div {{
          grid-row:1; justify-self:center !important; width:auto !important;
        }}
        {b} p, {b}[kind="primary"] p {{
          font-size:14px !important; font-weight:700 !important;
          color:#12314c !important; margin:0 !important;
          text-align:center !important; line-height:1.3 !important;
        }}
        {b}::after, {b}[kind="primary"]::after {{
          content:"{_txt_css(T(cle + 'x'))}"; grid-row:2;
          margin-top:7px; max-width:26ch;
          font-size:12px; font-weight:500; color:#6b7590;
          line-height:1.5; white-space:pre-wrap;
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
    for col, (cle, mode) in zip(cols, ENTREES):
        with col:
            st.button(T(cle), key=f"po_e_{cle}", on_click=_aller,
                      args=(mode,), use_container_width=True)


# ------------------------------------------------- comprendre, mesurer, agir
def _carte_indice(m):
    """La carte du territoire enquêté — dix sections, et aucun score.

    ELLE PORTAIT L'INDICE GLOBAL, ET C'ÉTAIT UNE ERREUR DE PLACE. La couleur
    de chaque section était juste, mais elle arrivait avant tout ce qui
    permet de la lire : ce qu'est APRI, ce qu'est un score sur dix, pourquoi
    les seuils sont découpés dans une fourchette de 3,6 à 5,3 et non sur
    l'échelle entière. Un visiteur qui découvre le site y voyait des couleurs
    qui semblent classer dix territoires, sans avoir de quoi comprendre ce
    qu'elles classent. Les scores n'ont pas disparu : ils sont dans « Analyse
    des résultats », derrière la porte qui les annonce.

    CE QU'ELLE MONTRE MAINTENANT EST CE QUE LA PAGE PROMET : où l'enquête a
    eu lieu. Les dix sections communales d'une seule couleur, dans le paysage
    pilote du Sud et de la Grand'Anse, dont les noms sont déjà portés par le
    fond de carte.
    """
    valeurs = {s: 1.0 for s in SECTIONS}
    # UNE SEULE COULEUR, ET TROIS SEUILS HORS D'ATTEINTE : toutes les sections
    # tombent dans la même classe, donc aucune ne se lit comme meilleure ou
    # pire qu'une autre. C'est le seul réglage du moteur de cartes qui donne
    # un aplat uniforme sans avoir à le réécrire.
    uni = ("#2f6b4f", "#ffffff")
    svg, _seuils, _ = map_render.render_map_svg(
        valeurs, {s: 1 for s in SECTIONS}, [9, 9.5, 10], height=400,
        ramp=[uni, uni, uni, uni], unite="")
    # LE DESSIN SE CALE À GAUCHE DE SA COLONNE. Le plafond de hauteur laisse
    # la boîte plus large que le dessin ; par défaut un SVG se centre alors
    # dans ce qui reste, et la carte partait à la dérive vers la droite.
    # `xMinYMid` la ramène contre le texte. La marge automatique du gabarit
    # est défaite dans la foulée.
    svg = svg.replace(
        "<svg ", '<svg preserveAspectRatio="xMinYMid meet" ', 1).replace(
        "margin:0 auto", "margin:0")
    svg = _sans_valeur(svg)
    return {"carte": f'<div class="uma-carte">{svg}</div>',
            "note": _e(T("po_carte_cap"))}


# LE MOTEUR DE CARTES ÉCRIT TOUJOURS LA VALEUR, et il n'a pas de réglage pour
# s'en abstenir : elle rejoint le nom dans l'étiquette (« Trichet · 5,3 ») et
# ouvre l'infobulle (« Trichet — 5,3 (base: 1) »). Les deux se retirent après
# coup, ici, plutôt qu'en ajoutant une option à un module dont sept autres
# pages dépendent. La valeur retirée est celle qu'on vient d'inventer pour
# obtenir un aplat : il n'y a rien à perdre.
_ETIQUETTE = re.compile(r'( · [\d]+,[\d]+)(?=</text>)')
_INFOBULLE = re.compile(r'(<title>)([^<—]+?) — [^<]*(</title>)')


def _sans_valeur(svg):
    """Retire le score des étiquettes et des infobulles."""
    return _INFOBULLE.sub(r'\1\2\3', _ETIQUETTE.sub('', svg))


def _badge():
    """Le badge de localisation : où se trouve la zone enquêtée dans Haïti.

    LA CARTE DÉTAILLÉE NE PEUT PAS RÉPONDRE À « OÙ EST-CE ? ». Cadrée sur la
    presqu'île du Sud, elle montre dix sections communales et trois noms de
    département ; qui ne connaît pas Haïti n'y reconnaît ni le pays, ni même
    l'île. Le badge le dit en une image : l'île entière, la République
    dominicaine nommée en retrait, et la zone d'étude cerclée de vert.

    IL EST LARGE ET BAS parce que l'île l'est, et il est PLUS LARGE QUE
    L'ÎLE : la boîte est volontairement plus étirée que le contour, de sorte
    que la hauteur cadre le dessin et laisse du jeu sur les côtés. Sans ce
    jeu, le cercle de la zone d'étude — qui déborde du contour, et qui tombe
    à l'extrême sud-ouest — sortait du cadre par la gauche.
    """
    geo = territoire_page._geo()
    # LA MER EST PRESQUE BLANCHE ICI. Le bleu gris de la page « Le territoire »
    # formerait un rectangle plein sur une page qu'on a débarrassée de ses
    # boîtes : seule l'île doit se voir.
    svg = territoire_page._vignette(geo, larg=300, haut=122, mer="#f7fafc")
    return f'<div class="uma-badge">{svg}</div>' if svg else ""


def _comprendre(m):
    # DE L'AIR ENTRE LES QUATRE PORTES ET CE QUI SUIT. Les cartes touchaient
    # le texte : deux blocs collés se lisent comme un seul, et la définition
    # semblait être la légende de la quatrième carte.
    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
    """Ce qu'APRI mesure, et la carte de ce que ça donne.

    LE TITRE ET LE BOUTON ONT ÉTÉ RETIRÉS. « Comprendre. Mesurer. Agir. »
    était une devise, pas une information : trois verbes que n'importe quelle
    institution pourrait afficher. À la place, la définition exacte de ce
    qu'on mesure — une seule phrase, mais qui dit l'objet, la méthode,
    l'échelle et l'unité. Le bouton « En savoir plus » menait au cadre de
    résilience, où les quatre cartes du dessus mènent déjà.
    """
    # TROIS COLONNES, ET LA DU MILIEU EST L'ÉCHELLE. La carte remonte alors
    # tout en haut de sa colonne : la barre et la mise en garde qui la
    # coiffaient sont parties ailleurs, et la hauteur qu'elles prenaient
    # revient au dessin. La mise en garde suit la définition, sous le cadre :
    # elle parle de l'échelle, qui est juste à côté.
    c = _carte_indice(m)
    g, d = st.columns([1.05, 1.6], gap="medium")
    with g:
        # LE PREMIER MOT EST DÉTACHÉ. Les deux langues commencent la phrase
        # par le nom du dispositif ; on le coupe donc du reste plutôt que de
        # le chercher dans le texte, ce qui casserait à la première
        # reformulation.
        _mot, _reste = _e(T("po_uma_x")).split(" ", 1)
        st.markdown(f'<div class="uma-cadre">'
                    f'<div class="uma-sur">{_e(T("po_uma_sur"))}</div>'
                    f'<p class="uma-x"><b>{_mot}</b> {_reste}</p></div>'
                    + _badge(), unsafe_allow_html=True)
    if not c:
        return
    with d:
        # LE TITRE EST AU-DESSUS DU DESSIN, PARCE QU'IL DIT CE QU'ON REGARDE.
        st.markdown(f'<div class="uma-zone">'
                    f'<p class="uma-n">{c["note"]}</p>{c["carte"]}</div>',
                    unsafe_allow_html=True)


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
