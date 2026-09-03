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
    "po_c1x": {"en": "Maps and landscapes across ten communal sections.",
               "fr": "Cartes et paysages des dix sections communales."},
    "po_c2": {"en": "Resilience Framework", "fr": "Cadre de résilience"},
    "po_c2x": {"en": "Dimensions, indicators and scoring methodology.",
               "fr": "Dimensions, indicateurs et méthode de notation."},
    "po_c3": {"en": "Results Analysis", "fr": "Analyse des résultats"},
    "po_c3x": {"en": "Compare resilience across territories and populations.",
               "fr": "Comparer la résilience entre territoires et "
                     "populations."},
    "po_c4": {"en": "Feedback Loops", "fr": "Boucles de rétroaction"},
    "po_c4x": {"en": "Understand systemic drivers and leverage points.",
               "fr": "Comprendre les moteurs systémiques et les leviers."},
    "po_c5": {"en": "Download Data", "fr": "Télécharger les données"},
    "po_c5x": {"en": "Access indicators, sources and datasets.",
               "fr": "Accéder aux indicateurs, aux sources et aux jeux de "
                     "données."},

    # --- LA PHRASE D'OUVERTURE, SOUS LE BANDEAU
    # ELLE A REMPLACÉ LA DÉFINITION EN CADRE. La définition longue disait la
    # même chose, en cinq lignes de 20 px posées à côté de la carte : elle
    # occupait le tiers de la page pour un contenu que le cadre de résilience
    # déplie en entier, onglet par onglet. Ici, une phrase suffit — elle dit
    # l'objet et l'ordre de grandeur, et elle laisse la carte respirer.
    #
    # LE NOMBRE D'INDICATEURS EST COMPTÉ, PAS ÉCRIT. Il est arrondi à la
    # dizaine inférieure et annoncé comme un minimum : une page d'accueil qui
    # promet un chiffre exact le dément le jour où un indicateur de plus est
    # calculé.
    "po_intro": {
        "en": "APRI assesses landscape and community resilience through "
              "three core capacities: anticipation, absorption and "
              "adaptation. Using {n}+ indicators across seven dimensions, it "
              "identifies negative loops to guide targeted intervention.",
        "fr": "APRI évalue la résilience des paysages et des communautés au "
              "travers de trois capacités fondamentales : anticipation, "
              "absorption et adaptation. À partir de plus de {n} indicateurs "
              "répartis en sept dimensions, il identifie les boucles "
              "négatives pour cibler l'intervention."},

    # --- LE SOCLE DE PREUVES, EN QUATRE MARCHES
    # CHAQUE MARCHE SE LIT « MOT D'AVANT · NOMBRE · MOT D'APRÈS ». Découper
    # ainsi plutôt que d'écrire une phrase entière est ce qui permet aux deux
    # langues de placer le nombre où leur syntaxe le veut : l'anglais dit
    # « across 10 communal sections », le français « dans 10 sections
    # communales », et le mot d'avant est vide sur la première marche.
    "po_socle_sur": {"en": "An unprecedented evidence base",
                     "fr": "Une base de preuves sans précédent"},
    "po_s1_z": {"en": "household surveys", "fr": "enquêtes ménage"},
    "po_s2_a": {"en": "across", "fr": "dans"},
    "po_s2_z": {"en": "communal sections", "fr": "sections communales"},
    "po_s3_a": {"en": "over several", "fr": "plusieurs"},
    "po_s3_n": {"en": "months", "fr": "mois"},
    "po_s3_z": {"en": "of biodiversity measurements and spatial analysis",
                "fr": "de mesures de biodiversité et d'analyses spatiales"},
    "po_s4_a": {"en": "with biologists, sociologists and economists "
                      "working across",
                "fr": "des biologistes, sociologues et économistes "
                      "mobilisés dans"},
    "po_s4_n": {"en": "two", "fr": "deux"},
    "po_s4_z": {"en": "pilot territories", "fr": "territoires pilotes"},
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
  /* LA PAGE REMONTE DE VINGT PIXELS. Le gabarit de l'application réserve
     1,2 rem au-dessus de la barre d'onglets : c'est juste sur les pages qui
     défilent, et c'est vingt pixels perdus sur celle qui doit tenir dans un
     écran. La carte les reprend. */
  div[data-testid="stMainBlockContainer"] { padding-top: 0.35rem !important; }
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

  /* --- LA PHRASE D'OUVERTURE, SOUS LE BANDEAU ---------------------------
     ELLE EST EN ITALIQUE ET EN ROMAIN À EMPATTEMENTS, et c'est le seul
     endroit du site qui l'est. Ce n'est pas un ornement : la page enchaîne
     ensuite cinq cartes, un surtitre, un paragraphe et une carte, tous en
     linéale. Une phrase qui doit se lire AVANT le reste doit d'abord se
     distinguer du reste ; le changement de casse fait ce travail sans
     grossir le corps ni prendre de hauteur.

     LE `!important` N'EST PAS UN CAPRICE : la feuille de l'application fixe
     14,5 px et la justification à tous les paragraphes du contenu, avec une
     spécificité supérieure à celle d'une classe. */
  /* LE MÊME FILET VERT QUE LE SOCLE, en haut et en bas de la page : les deux
     blocs de texte se répondent, et la marge gauche tient debout. Le texte
     est justifié, avec la césure — sur quatre-vingts signes, les blancs
     restent réguliers, et `lang` porté par le paragraphe dit au navigateur
     quel dictionnaire de coupure appliquer. */
  p.uma-i  { font-size:15.5px !important; line-height:1.62 !important;
             font-family:Georgia,"Times New Roman",serif; font-style:italic;
             font-weight:400; color:#26364a !important;
             /* DEUX LIGNES, PAS TROIS. Bornée à quatre-vingt-quatre
                signes, la phrase en prenait trois et repoussait tout le
                reste de la page d'une ligne entière. Elle court maintenant
                sur toute la colonne : à cette taille et dans cette casse,
                deux lignes se lisent sans que l'œil perde le retour. */
             margin:14px 0 6px !important; max-width:none;
             border-left:3px solid #1a6b52; padding-left:24px;
             text-align:justify !important;
             hyphens:auto; -webkit-hyphens:auto; }

  /* --- LE SOCLE DE PREUVES, EN ESCALIER ---------------------------------
     LE PARAGRAPHE EST DEVENU QUATRE CHIFFRES. Justifié dans son cadre, il
     disait la même chose, mais il fallait le lire en entier pour retrouver
     l'ampleur — mille deux cents, dix, plusieurs mois, deux. Ce sont ces
     quatre nombres qu'on doit emporter ; ils passent donc devant, en grand,
     et la phrase se réduit aux mots qui les relient.

     LE DÉCROCHEMENT EST CE QUI FAIT LIRE DANS L'ORDRE. Quatre lignes alignées
     à gauche se lisent comme une liste, où rien ne vient avant rien. Décalées
     l'une sous l'autre, elles se lisent comme un parcours : l'enquête, le
     territoire, la durée, les deux paysages. Le pointillé ne fait que suivre
     ce parcours ; c'est un décor, il ne porte aucune information.

     LE POINTILLÉ EST ÉTIRÉ, LE TRAIT NE L'EST PAS. Le tracé est posé en
     `preserveAspectRatio="none"` pour épouser le bloc quelle que soit la
     langue — le français prend une ligne de plus que l'anglais. Sans
     `vector-effect:non-scaling-stroke`, les pointillés seraient étirés avec
     lui et deviendraient des tirets inégaux. */
  .uma-sur { font-size:11px; font-weight:700; color:#8a93a5;
             letter-spacing:.09em; text-transform:uppercase;
             margin:0 0 10px; }
  .uma-socle { border-left:3px solid #1a6b52; padding:2px 0 4px 26px;
               margin:6px 0 0; }
  .uma-socle .uma-sur { color:#1a6b52; font-size:12px;
                        letter-spacing:.11em; margin:0 0 20px; }
  .uma-esc { position:relative; }
  /* Le tracé passe SOUS les mots : posé au-dessus, il barrerait les
     chiffres au premier changement de langue. */
  .uma-fil { position:absolute; left:0; top:0; width:100%; height:100%;
             pointer-events:none; z-index:0; overflow:visible; }
  .uma-pousse { position:absolute; left:2px; top:-4px; z-index:0; }
  .uma-e { position:relative; z-index:1; display:flex; align-items:baseline;
           gap:11px; margin:0 0 15px; }
  /* TOUT S'ALIGNE SUR LA PREMIÈRE LIGNE DE BASE, mots d'avant compris.
     `align-self:last baseline` avait l'air plus juste sur la quatrième
     marche — c'est sa seconde ligne qui doit venir sous le nombre — mais en
     flexbox les éléments alignés par la DERNIÈRE ligne de base forment un
     second groupe, plaqué contre le bas de la rangée : sur la troisième
     marche, dont le mot d'après tient sur deux lignes, « plusieurs »
     décrochait d'une ligne entière sous « mois ». Une règle qui corrige une
     marche et en casse une autre n'est pas une règle. */
  .uma-av { font-size:14.5px; color:#5a6a80; line-height:1.35;
            text-align:right; flex:0 0 auto; max-width:31ch; }
  /* LE MÊME ROMAIN À EMPATTEMENTS QUE LA PHRASE D'OUVERTURE. Les deux blocs
     se répondent en haut et en bas de la colonne ; une troisième police les
     aurait séparés sans raison. */
  .uma-nb { font-family:Georgia,"Times New Roman",serif; font-size:44px;
            line-height:1; color:#1f7a4d; letter-spacing:-.015em;
            white-space:nowrap; flex:0 0 auto; }
  .uma-ap { font-size:14.5px; color:#33455c; line-height:1.35;
            max-width:26ch; }

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
  /* LE SÉLECTEUR VISE L'ENFANT DIRECT, ET C'EST INDISPENSABLE. Le carton de
     situation est un SVG imbriqué dans celui de la carte : une règle en
     descendance lui imposait `width:100%`, ce qui écrase ses propres `x`,
     `y` et `width` — le carton prenait alors toute la carte et la couvrait
     entièrement. */
  /* La constante retranchée a grandi de la hauteur de la phrase
     d'ouverture : sans cela, la carte reprendrait à elle seule la place que
     la phrase vient de prendre, et la page se remettrait à défiler. */
  .uma-carte > svg { display:block; width:100%; height:auto;
                     margin:0 !important;
                     max-height: max(205px, calc(100vh - 428px)); }
  .uma-carte > svg > .sea, .uma-carte > svg .sea { fill:transparent !important; }
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
    svg = _pousser_reperes(svg)
    svg = _carton(svg)
    return {"carte": f'<div class="uma-carte">{svg}</div>',
            "note": _e(T("po_carte_cap"))}


# LA ROSE DES VENTS ET L'ÉCHELLE SONT DESSINÉES CONTRE LE BORD GAUCHE DU
# CANEVAS, à quarante-six points d'un dessin dont la côte commence vers 336 :
# elles flottaient au large, à trois cents points de la terre qu'elles
# servent à lire. On les ramène contre le rivage, et la place ainsi libérée
# revient au carton de situation. Les quatre repères portent des classes qui
# leur sont propres — `cl` pour les traits, `ca` pour la pointe de la flèche,
# `ct` et `ct2` pour les mots — donc rien d'autre ne bouge. LA POINTE COMPTE
# AUTANT QUE LE TRAIT : oubliée, elle reste en arrière et la flèche se coupe
# en deux.
_REPERE = re.compile(r'<(line|text|path)\b[^>]*class="(?:cl|ca|ct|ct2)"[^>]*>')
_ABSCISSE = re.compile(r'\b(x|x1|x2)="(-?[\d.]+)"')
_ORDONNEE = re.compile(r'\b(y|y1|y2)="(-?[\d.]+)"')
_TRACE = re.compile(r'\bd="([^"]*)"')


def _pousser_reperes(svg, dx=-210, dy=-26, plancher=200):
    """Décale la rose des vents et l'échelle kilométrique vers la côte.

    ET REMONTE L'ÉCHELLE DE VINGT-SIX POINTS. Le moteur de cartes pose le
    mot « ≈ 25 km » à vingt-deux points du bord bas du canevas. C'est
    suffisant partout ailleurs ; sur la page d'accueil, où la carte est
    plafonnée en hauteur et calée par `preserveAspectRatio`, la dernière
    ligne du canevas tombe hors de la boîte rendue et le mot disparaît — le
    trait de l'échelle restait seul, sans dire combien il mesure, ce qui est
    pire qu'une échelle absente. Seuls les repères du bas remontent : le
    `plancher` sépare l'échelle, en bas du canevas, de la rose des vents qui
    est en haut et n'a pas à bouger.
    """
    def _chemin(m):
        # Le tracé de la pointe est une suite « M x,y L x,y … » : seule
        # l'abscisse, en tête de chaque couple, se décale.
        return 'd="%s"' % re.sub(
            r'(-?[\d.]+),(-?[\d.]+)',
            lambda c: f'{float(c.group(1)) - dx:g},{c.group(2)}', m.group(1))

    def _un(m):
        t = _TRACE.sub(_chemin, _ABSCISSE.sub(
            lambda a: f'{a.group(1)}="{float(a.group(2)) - dx:g}"', m.group(0)))
        if any(float(v) > plancher for _c, v in _ORDONNEE.findall(t)):
            t = _ORDONNEE.sub(
                lambda o: f'{o.group(1)}="{float(o.group(2)) + dy:g}"', t)
        return t
    return _REPERE.sub(_un, svg)


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


# Le carton se pose dans le coin haut-gauche de la carte, sur la mer, en
# unités du canevas de la carte (920 par 400). Cette bande d'eau va jusqu'à
# la côte, qui commence vers x = 336 : le carton en prend la moitié gauche,
# la rose des vents et l'échelle kilométrique occupent l'autre, contre la
# terre.
_CARTON = (6, 8, 232, 95)          # x, y, largeur, hauteur
_OUVRE_SVG = re.compile(r'^<svg\b[^>]*>')


def _carton(svg_carte):
    """Pose la vignette de localisation DANS la carte, sur la mer.

    ELLE ÉTAIT SOUS LA DÉFINITION, ET ELLE COÛTAIT CENT CINQUANTE PIXELS DE
    HAUTEUR à une page qui doit tenir dans un écran — alors que la carte,
    elle, porte une large bande de mer vide à l'ouest de la presqu'île. Un
    carton de situation dans un coin d'eau est d'ailleurs la façon dont les
    atlas règlent la question depuis toujours : la vue générale et la vue de
    détail se lisent d'un seul regard, sans que la seconde ait à céder de la
    place à la première.

    UN SVG S'IMBRIQUE DANS UN SVG, avec ses propres `x`, `y` et `viewBox` :
    c'est du SVG 1.1, tous les navigateurs le rendent, et cela évite d'avoir
    à reprojeter l'île dans le repère de la carte. La vignette est donc
    dessinée à la taille exacte qu'elle occupera, et non réduite après coup :
    ses deux noms de pays gardent leur corps de texte.
    """
    geo = territoire_page._geo()
    x, y, larg, haut = _CARTON
    # LA MER EST PRESQUE BLANCHE ICI. Le bleu gris de la page « Le
    # territoire » ferait une tache sur une carte dont la mer est
    # transparente : seule l'île doit se voir.
    vignette = territoire_page._vignette(geo, larg=larg, haut=haut,
                                         mer="#ffffff")
    if not vignette:
        return svg_carte
    # LE CADRE EST REDESSINÉ EN SVG. Celui de la vignette est une bordure
    # CSS, qui n'existe pas à l'intérieur d'un SVG : on le remplace par un
    # rectangle arrondi, posé sous le dessin.
    dedans = _OUVRE_SVG.sub("", vignette)[:-len("</svg>")]
    dedans = dedans.replace(
        f'<rect width="{larg}" height="{haut}" fill="#ffffff"/>',
        f'<rect x=".5" y=".5" width="{larg - 1}" height="{haut - 1}" rx="8" '
        f'fill="#ffffff" stroke="#dfe7ef" stroke-width="1"/>', 1)
    imbrique = (f'<svg x="{x}" y="{y}" width="{larg}" height="{haut}" '
                f'viewBox="0 0 {larg} {haut}">{dedans}</svg>')
    return svg_carte.replace("</svg>", imbrique + "</svg>")


def _rond(v, pas):
    """Un ordre de grandeur, arrondi à la dizaine ou à la centaine INFÉRIEURE.

    LE SENS EST DANS LE MOT « PLUS DE ». Arrondir au plus proche donnerait
    « plus de 1 200 » pour 1 180 enquêtes, ce qui serait faux. Arrondir vers
    le bas rend la phrase vraie quel que soit le fichier de résultats.
    """
    if not v:
        return None
    return int(v) // pas * pas


def _nombre(v):
    """Un entier écrit avec le séparateur de milliers de la langue affichée."""
    t = f"{int(v):,}"
    return t.replace(",", " ") if i18n.get_lang() == "fr" else t


# LE TRACÉ EST UN DÉCOR, ET IL EST ÉCRIT UNE FOIS POUR TOUTES. Il relie les
# quatre marches dans l'ordre de lecture ; ses coordonnées sont posées dans un
# repère de 623 sur 225 que le navigateur étire au bloc réel. Le trait, lui,
# ne s'étire pas (`non-scaling-stroke`) : les pointillés restent ronds et
# réguliers quelle que soit la déformation.
_FIL = """<svg class="uma-fil" viewBox="0 0 623 225" preserveAspectRatio="none"
 aria-hidden="true" focusable="false">
  <path d="M14,6 C2,28 8,48 34,60 C62,72 92,64 110,80
           C126,96 142,116 160,140 C186,156 214,166 244,188"
        fill="none" stroke="#1f7a4d" stroke-width="1.6" stroke-linecap="round"
        stroke-dasharray="1.5 7" vector-effect="non-scaling-stroke"
        opacity=".62"/>
</svg>"""

# La pousse est dessinée à part, dans un SVG à ses propres proportions : mise
# dans le tracé étiré, elle serait écrasée avec lui.
_POUSSE = """<svg class="uma-pousse" width="26" height="26" viewBox="0 0 26 26"
 aria-hidden="true" focusable="false">
  <path d="M13,24 C13,16 13,10 13,5" fill="none" stroke="#1f7a4d"
        stroke-width="1.6" stroke-linecap="round"/>
  <path d="M13,11 C13,4 17,1 23,1 C23,7 19,11 13,11 Z" fill="#1f7a4d"
        opacity=".85"/>
  <path d="M13,16 C13,11 10,8 5,8 C5,13 8,16 13,16 Z" fill="#1f7a4d"
        opacity=".5"/>
</svg>"""


def _marche(avant, nombre, apres, decalage):
    """Une marche : le mot d'avant, le nombre en grand, le mot d'après."""
    return (f'<div class="uma-e" style="padding-left:{decalage}px">'
            + (f'<span class="uma-av">{_e(avant)}</span>' if avant else "")
            + f'<span class="uma-nb">{_e(nombre)}</span>'
            + f'<span class="uma-ap">{_e(apres)}</span></div>')


def _socle(m):
    """Les quatre nombres du socle, en escalier, reliés par un pointillé.

    LES NOMBRES SONT COMPTÉS DANS LES DONNÉES, les mots viennent des
    traductions. Le décalage de chaque marche est écrit ici plutôt que dans
    la feuille de style : il n'a de sens que par rapport aux trois autres, et
    quatre valeurs qui se règlent ensemble se lisent mieux côte à côte.
    """
    menages = _rond(m.get("menages"), 100)
    sections = len(m.get("sections_n") or {}) or len(SECTIONS)
    marches = [
        # La première marche n'a pas de mot d'avant : le nombre ouvre la
        # phrase dans les deux langues. On passe une chaîne vide plutôt
        # qu'une clé de traduction vide — une clé sans texte s'affiche
        # sous son propre nom.
        ("", (_nombre(menages) if menages else "1 200") + "+",
         T("po_s1_z"), 50),
        (T("po_s2_a"), str(sections), T("po_s2_z"), 76),
        (T("po_s3_a"), T("po_s3_n"), T("po_s3_z"), 96),
        (T("po_s4_a"), T("po_s4_n"), T("po_s4_z"), 32),
    ]
    return ('<div class="uma-esc">' + _FIL + _POUSSE
            + "".join(_marche(*x) for x in marches) + '</div>')


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
    # LA COLONNE DE GAUCHE S'ÉLARGIT POUR QUE LA JUSTIFICATION TIENNE.
    # Justifié sur trente-huit signes, le paragraphe creusait des couloirs
    # blancs verticaux — c'est le défaut classique d'une colonne trop
    # étroite, et il se voit d'autant plus que les chiffres en gras
    # découpent la ligne. Plus la ligne est longue, plus les blancs se
    # répartissent. La carte perd la largeur correspondante et rétrécit
    # d'autant en hauteur : la page y gagne même de l'air.
    g, d = st.columns([1.42, 1.5], gap="medium")
    with g:
        st.markdown(f'<div class="uma-socle">'
                    f'<div class="uma-sur">{_e(T("po_socle_sur"))}</div>'
                    f'{_socle(m)}</div>', unsafe_allow_html=True)
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
    # LA PHRASE D'OUVERTURE PASSE AVANT LES PORTES, et c'est tout son
    # intérêt : on lit ce que fait l'observatoire avant de choisir où aller.
    # Placée sous les cartes, elle aurait été lue par les seuls visiteurs qui
    # n'ont pas cliqué — c'est-à-dire par personne.
    # LE COMPTE EST CELUI DU RÉFÉRENTIEL, PAS CELUI DES SCORES CALCULÉS.
    # La phrase parle de l'étendue du cadre — ce qu'APRI regarde — et non de
    # l'avancement du chantier, qui a sa place dans le cadre de résilience où
    # il est dit dimension par dimension. Le nombre reste compté dans le
    # fichier et arrondi à la centaine inférieure : « plus de » doit rester
    # vrai quel que soit le référentiel.
    n_ind = _rond(sum(e["n"] for e in (m.get("dims") or {}).values()), 100)
    st.markdown(f'<p class="uma-i" lang="{i18n.get_lang()}">'
                f'{_e(T("po_intro", n=n_ind or 100))}</p>',
                unsafe_allow_html=True)
    _entrees()
    _comprendre(m)
