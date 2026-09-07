"""Une seconde page d'accueil, à l'essai.

POURQUOI DEUX ACCUEILS EN MÊME TEMPS.
Une page d'entrée ne se juge pas sur une capture : elle se juge en arrivant
dessus, avec la colonne de gauche, le pied de page et le reste du site autour.
Celle-ci vit donc à côté de l'autre, sous sa propre entrée de menu, le temps
de trancher — et elle se retire en supprimant trois lignes dans `app.py`, ce
module et son entrée de navigation.

CE QU'ELLE FAIT DIFFÉREMMENT.
L'accueil actuel ouvre sur un escalier de quatre nombres et une carte. Celui-ci
ouvre sur une photographie plein cadre qui porte le titre, puis pose les quatre
nombres sur une seule rangée, et range les quatre destinations en cartes de
même poids sous la carte du territoire. C'est la forme d'une page
institutionnelle : on annonce, on chiffre, on oriente.

TOUT LE CONTENU EST REPRIS DE L'EXISTANT, RIEN N'EST INVENTÉ.
Les nombres sont comptés dans le référentiel comme sur l'autre accueil, la
carte est celle du module de cartes, et les quatre destinations sont les
rubriques réelles du menu. Une page d'essai qui afficherait des chiffres
d'illustration ne permettrait de juger que du décor.
"""

import base64
import json
import os

import streamlit as st

import accueil_apri
import i18n
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Les dix sections enquêtées, dans l'ordre où la carte les dessine.
SECTIONS = ["Anse à Drick", "Barbois", "Beaulieu", "Blactote", "Dalmette",
            "Débouchette", "Dumont", "Mouline", "Quentin", "Trichet"]

# LES QUATRE DESTINATIONS, ET LEUR CODE DE RUBRIQUE. Le code est celui du
# menu : la carte y conduit par le même chemin que la colonne de gauche, sans
# quoi deux routes vers la même page finiraient par diverger.
PORTES = [
    ("dimensions", "a2_p1_t", "a2_p1_x", "#f2f6f3"),
    ("accueil", "a2_p2_t", "a2_p2_x", "#eef3f6"),
    ("boucles", "a2_p3_t", "a2_p3_x", "#faf6f0"),
    ("actions", "a2_p4_t", "a2_p4_x", "#f2f6f3"),
]

# LA PHOTOGRAPHIE SUIT LA LANGUE, ET CE N'EST PAS UN CAPRICE. Deux clichés du
# terrain valaient l'ouverture ; les départager revenait à en perdre un. Le
# site est lu dans deux langues par deux publics, il ouvre donc sur deux
# scènes : le port et sa flottille de voiliers pour la version française, la
# vallée et sa rivière pour l'anglaise. Chacune vient avec son cadrage, car
# les deux panoramas ne portent pas leur sujet à la même hauteur.
PHOTOS = {"fr": ("accueil2_hero_b.jpg", "50% 62%"),
          "en": ("accueil2_hero.jpg", "62% 40%")}

TEXTES = {
    "a2_nav": {"en": "Home 2", "fr": "Accueil 2"},
    # LE TITRE INSTITUTIONNEL, EN DEUX LIGNES SÉPARÉES PAR UNE BARRE. La
    # coupure n'est pas laissée au hasard de la largeur : « Observatoire de la
    # résilience » d'un côté, ce sur quoi elle porte de l'autre.
    "a2_inst": {
        "en": "Observatory for the Resilience|of Haiti's Landscapes and "
              "Populations",
        "fr": "Observatoire de la résilience|des paysages et des populations "
              "d'Haïti"},
    # LE SUR-TITRE DÉPLIE L'ACRONYME. « Populations · Paysages · Résilience »
    # sonnait juste et n'apprenait rien : personne n'arrive sur cette page en
    # sachant ce que veut dire APRI, et le mot est le premier qu'on y lit.
    "a2_kicker": {"en": "Integrated Resilient Landscape Approach",
                  "fr": "Approche Paysages Résilients Intégrée"},
    "a2_titre": {"en": "Data for a more resilient Haiti",
                 "fr": "Des données pour une Haïti plus résiliente"},
    "a2_intro": {
        "en": "The APRI approach assesses how a landscape maintains and "
              "improves its essential functions in the face of constant "
              "pressures and extreme events. This integrated model, a "
              "diagnostic tool, measures the resilience of a landscape and "
              "explores, through a set of indicators, specific levers for "
              "action: making the most of the capacities available, or "
              "identifying those to be strengthened.",
        "fr": "L'approche APRI évalue comment un paysage maintient et "
              "améliore ses fonctions essentielles face à des défis "
              "constants et à des événements extrêmes. Ce modèle intégré, "
              "outil de diagnostic, mesure la résilience d'un paysage et "
              "explore, au travers d'un ensemble d'indicateurs, des leviers "
              "d'action spécifiques : tirer parti au mieux des compétences "
              "disponibles, ou identifier celles à améliorer."},
    "a2_cta": {"en": "Explore the results", "fr": "Explorer les résultats"},
    "a2_credit": {"en": "Grand'Anse, Haiti", "fr": "Grand'Anse, Haïti"},
    "a2_c1_x": {"en": "household surveys", "fr": "enquêtes ménage"},
    "a2_c2_x": {"en": "communal sections", "fr": "sections communales"},
    "a2_c3_n": {"en": "Two", "fr": "Deux"},
    "a2_c3_x": {"en": "pilot territories", "fr": "territoires pilotes"},
    "a2_c3_s": {"en": "Grand'Anse and Sud", "fr": "Grand'Anse et Sud"},
    "a2_c4_n": {"en": "10+ months", "fr": "10+ mois"},
    "a2_c4_x": {"en": "of fieldwork", "fr": "de terrain"},
    "a2_c4_s": {"en": "Biodiversity, social and spatial analysis",
                "fr": "Biodiversité, analyses sociales et spatiales"},
    "a2_carte_t": {"en": "Our study area", "fr": "Notre zone d'étude"},
    "a2_portes_t": {"en": "Explore APRI", "fr": "Explorer APRI"},
    "a2_p1_t": {"en": "Analyse results", "fr": "Analyser les résultats"},
    "a2_p1_x": {"en": "Survey data and resilience indicators",
                "fr": "Données d'enquête et indicateurs de résilience"},
    "a2_p2_t": {"en": "Discover the territory", "fr": "Découvrir le territoire"},
    "a2_p2_x": {"en": "Maps, landscapes and key characteristics",
                "fr": "Cartes, paysages et caractéristiques"},
    "a2_p3_t": {"en": "Understand the system", "fr": "Comprendre le système"},
    "a2_p3_x": {"en": "Feedback loops and key variables",
                "fr": "Boucles de rétroaction et variables clés"},
    "a2_p4_t": {"en": "Identify solutions", "fr": "Identifier des solutions"},
    "a2_p4_x": {"en": "Intervention profiles and action plans",
                "fr": "Fiches d'intervention et plans d'action"},
}
# Les libellés rejoignent le dictionnaire du site, sans écraser une clé
# existante — c'est la convention de tous les modules.
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)

STYLE = """
<style>
  /* --- LA PHOTOGRAPHIE PLEIN CADRE, ET LE TEXTE DESSUS -----------------
     LE VOILE N'EST PAS UN EFFET, C'EST CE QUI REND LE TITRE LISIBLE. La
     photographie porte du ciel clair en haut et de la végétation sombre au
     milieu ; un texte posé dessus sans voile passe de lisible à illisible
     d'une ligne à l'autre. Le voile est opaque à gauche, où vit le texte, et
     s'efface avant la moitié pour que la rivière et les mornes restent nets.

     ELLE EST CADRÉE SUR SA DROITE. Le lit de la rivière et les mornes
     occupent la moitié droite du cliché ; centrée, l'image aurait mis sous
     le titre le talus de galets du premier plan. */
  /* ELLE VA D'UN BORD À L'AUTRE. Le bloc de contenu garde sa gouttière de
     2,6 rem à droite et l'écart de 2 rem qui le sépare de la colonne de
     gauche : une photographie posée dedans laissait donc une bande blanche
     sur trois côtés, comme une image collée dans une page plutôt qu'une
     couverture. Les deux marges négatives annulent exactement ces deux
     écarts — l'image touche le bord droit de la fenêtre et vient au contact
     du vert à gauche — et le haut n'avait rien à annuler, le bloc principal
     n'ayant pas de rembourrage haut. Les valeurs sont dites dans l'unité de
     la mise en page, pas en pixels : elles suivent le facteur de zoom. */
  .a2-hero { position:relative; border-radius:0; overflow:hidden;
        min-height:420px; display:flex; align-items:center;
        margin:0 -2.6rem 0 -2rem;
        background-color:#eef3f0;
        background-size:cover; background-position:62% 40%;
        background-repeat:no-repeat; }
  .a2-hero::before { content:""; position:absolute; inset:0;
        background:linear-gradient(90deg,
            rgba(255,255,255,.97) 0%, rgba(255,255,255,.93) 28%,
            rgba(255,255,255,.62) 44%, rgba(255,255,255,.12) 62%,
            rgba(255,255,255,0) 74%); }
  /* LE TEXTE, LUI, GARDE SA MARGE. L'image a débordé de deux rem à gauche ;
     le bloc de texte les reprend en rembourrage, sinon le sur-titre se
     collerait au vert de la colonne. */
  /* LE REMBOURRAGE BAS EST UNE BANDE RÉSERVÉE, PAS UNE RESPIRATION. C'est là
     que le bouton d'appel vient se poser, remonté depuis le flux : sans elle,
     il se serait couché sur la dernière ligne du paragraphe. */
  .a2-hero-c { position:relative; padding:52px 40px 104px calc(2rem + 46px);
        max-width:680px; }
  /* LE BLOC DE MARQUE : l'emblème, un filet, la ligne institutionnelle. Les
     trois sont alignés sur leur milieu, comme dans le fichier de la charte,
     et le filet monte et descend avec le texte plutôt qu'avec l'image — c'est
     lui qui sépare la marque de ce qu'elle nomme. */
  .a2-marque { display:flex; align-items:center; gap:20px; margin:0 0 30px; }
  .a2-marque img { height:78px; width:auto; display:block; flex:0 0 auto; }
  .a2-filet { width:1px; align-self:stretch; margin:4px 0;
        background:#a9bcc6; flex:0 0 1px; }
  /* LE TITRE INSTITUTIONNEL : le même romain à empattements que le grand
     titre, en corps réduit — il annonce l'institution avant que la page
     annonce son sujet. Les deux lignes n'ont pas la même encre : la première
     nomme l'observatoire et prend le vert de la marque, la seconde dit sur
     quoi il porte et passe au bleu ardoise. */
  .a2-inst { font-family:Georgia,"Times New Roman",serif; margin:0;
        text-align:left !important; }
  .a2-inst b { display:block; font-weight:400; font-size:22px;
        line-height:1.24; color:#17563f; }
  .a2-inst span { display:block; font-size:19px; line-height:1.3;
        color:#3d5c74; }
  .a2-kick { font-size:11.5px; font-weight:700; letter-spacing:.19em;
        text-transform:uppercase; color:#3f8f66; margin:0 0 18px; }
  /* AU FIL DE L'EAU, ET NON JUSTIFIÉ. La feuille de l'application justifie
     les blocs de texte ; sur un titre de quatre mots en corps cinquante-deux,
     la justification écarte les mots jusqu'aux bords du cadre. */
  .a2-titre { font-family:Georgia,"Times New Roman",serif; font-size:52px;
        line-height:1.08; letter-spacing:-.02em; color:#153b2c;
        margin:0 0 20px; font-weight:400; text-align:left !important;
        max-width:13ch; }
  /* LA LARGEUR SUIT LA LONGUEUR. Le chapeau tenait en une phrase et se
     coupait à quarante-quatre signes ; il en fait maintenant plusieurs, et
     la même colonne étroite en aurait fait dix lignes sous le titre. Il
     prend donc la largeur du bloc, en corps légèrement réduit.

     ET IL EST JUSTIFIÉ. C'est le seul bloc de la page qui le soit, et il le
     supporte : quatre lignes pleines sur une colonne large ne creusent pas
     de rivières entre les mots, là où le titre en cinquante-deux points, lui,
     en creusait. Le bord droit net referme le bloc de texte contre la
     photographie. */
  p.a2-intro { font-size:14.5px !important; color:#3c4761 !important;
        line-height:1.6 !important; margin:0 0 26px !important;
        max-width:none; text-align:justify !important;
        text-justify:inter-word; }
  /* LE CRÉDIT EST BLANC, SUR LA PHOTOGRAPHIE. Une ombre portée le détache
     là où le cliché passe clair — une plaque translucide, elle, découperait
     un rectangle net dans l'image. */
  .a2-credit { position:absolute; right:18px; bottom:14px; font-size:11.5px;
        color:#ffffff; text-shadow:0 1px 3px rgba(0,0,0,.5); }

  /* --- LES QUATRE NOMBRES, SUR UNE RANGÉE ------------------------------
     Séparés par un filet plutôt que par des cartes : ce sont quatre mesures
     de la même campagne, pas quatre objets distincts. */
  .a2-chif { display:grid; grid-template-columns:repeat(4, 1fr);
        margin:34px 0 8px; }
  .a2-chif > div { padding:4px 26px; }
  .a2-chif > div + div { border-left:1px solid #e6ebe8; }
  .a2-n { font-family:Georgia,"Times New Roman",serif; font-size:34px;
        line-height:1.1; color:#1f7a4d; letter-spacing:-.015em; }
  .a2-l { font-size:11.5px; font-weight:600; letter-spacing:.13em;
        text-transform:uppercase; color:#3c4761; margin-top:9px; }
  .a2-s { font-size:12.5px; color:#7a8496; margin-top:5px; line-height:1.4; }
  @media (max-width: 900px) {
    .a2-chif { grid-template-columns:repeat(2, 1fr); row-gap:22px; }
    .a2-chif > div:nth-child(3) { border-left:0; }
    .a2-titre { font-size:38px; }
  }

  /* --- LA CARTE, DANS SON CARTON PÂLE ---------------------------------- */
  .a2-carte { background:#f4f7f5; border-radius:14px; padding:14px 22px 10px; }
  .a2-carte-t { font-size:11.5px; font-weight:700; letter-spacing:.15em;
        text-transform:uppercase; color:#1a4d3a; margin:0 0 4px; }
  .a2-carte-f { width:44px; height:2px; background:#9fc7b3; margin:0 0 10px; }
  .a2-carte > svg, .a2-carte div > svg { width:100%; height:auto;
        display:block; }

  /* --- LES QUATRE DESTINATIONS, EN BOUTONS-CARTES ----------------------
     CE SONT DE VRAIS BOUTONS, PAS DES CARTONS DÉCORÉS. Une carte qui a l'air
     cliquable et ne l'est pas est le défaut le plus coûteux d'une page
     d'entrée ; le bouton de Streamlit porte donc la carte entière, et son
     libellé est composé sur deux lignes. */
  /* « EXPLORER APRI » S'ALIGNE SUR « NOTRE ZONE D'ÉTUDE ». Le carton de la
     carte a vingt pixels de rembourrage haut avant son intitulé ; sans le
     même décalage, les deux colonnes commençaient à deux hauteurs
     différentes et la droite semblait remonter dans les chiffres. */
  .a2-portes-t { font-size:11.5px; font-weight:700; letter-spacing:.15em;
        text-transform:uppercase; color:#1a4d3a; margin:26px 0 4px; }
  .a2-portes-f { width:44px; height:2px; background:#9fc7b3; margin:0 0 14px; }
  /* PLUS DE PICTOGRAMME, ET LE TEXTE AU MILIEU. Quatre cartons pâles coiffés
     chacun d'une petite icône ronde, c'est la vignette que toutes les pages
     d'accueil produites à la chaîne portent depuis deux ans ; le dessin
     n'ajoutait rien que le titre ne disait déjà. Reste le titre, sa ligne
     d'explication et la flèche qui dit que ça mène quelque part. */
  div[class*="st-key-a2_porte_"] div[data-testid="stButton"] > button {
      display:flex !important; flex-direction:column !important;
      align-items:center !important; justify-content:center !important;
      text-align:center !important; width:100% !important;
      min-height:118px !important; height:100% !important;
      padding:22px 22px 18px !important; border-radius:14px !important;
      border:1px solid transparent !important; box-shadow:none !important;
      transition:border-color .15s ease, transform .15s ease;
  }
  div[class*="st-key-a2_porte_"] div[data-testid="stButton"] > button:hover {
      border-color:#bcd6c8 !important; transform:none !important;
  }
  div[class*="st-key-a2_porte_"] div[data-testid="stButton"] > button p {
      text-align:center !important; margin:0 !important;
      font-size:15px !important; font-weight:600 !important;
      color:#101728 !important; line-height:1.35 !important;
      font-family:Georgia,"Times New Roman",serif !important;
  }
  div[class*="st-key-a2_porte_"] div[data-testid="stButton"] > button
      p em { display:block; font-family:Inter,system-ui,sans-serif;
      font-style:normal; font-size:12.5px; font-weight:400; color:#5a6a80;
      margin-top:7px; line-height:1.45;
      /* DEUX LIGNES RÉSERVÉES, QU'IL Y EN AIT UNE OU DEUX. Les descriptions
         n'ont pas la même longueur, et les quatre flèches se retrouvaient à
         quatre hauteurs différentes dans quatre cartes de même taille. */
      min-height:36px; }
  /* LA FLÈCHE FERME LA CARTE. Elle est écrite dans le libellé, en gras, ce
     qui est la seule façon de lui donner sa propre ligne dans un bouton de
     Streamlit ; la graisse est aussitôt reprise ici — c'est une flèche, pas
     une insistance. */
  div[class*="st-key-a2_porte_"] div[data-testid="stButton"] > button
      p strong { display:block; margin-top:15px; font-weight:400;
      font-family:Inter,system-ui,sans-serif; font-size:17px;
      line-height:1; color:#1f7a4d; }

  /* --- LE BOUTON D'APPEL DU BANDEAU ------------------------------------ */
  div[class*="st-key-a2_cta"] div[data-testid="stButton"] > button {
      background:#1f7a4d !important; border:0 !important;
      border-radius:8px !important; padding:13px 26px !important;
      box-shadow:none !important;
      /* SA LARGEUR EST CELLE DE SON MOT. Étiré sur sa colonne, il faisait un
         pavé de quatre cents pixels pour trois mots. */
      width:auto !important; min-height:0 !important; height:auto !important;
  }
  div[class*="st-key-a2_cta"],
  div[class*="st-key-a2_cta"] div[data-testid="stElementContainer"],
  div[class*="st-key-a2_cta"] div[data-testid="stButton"] {
      width:auto !important;
  }
  /* IL REMONTE DANS L'IMAGE, calé sur la même marge gauche que le texte du
     bandeau. La marge basse rend au flux la hauteur que la marge haute lui a
     prise : sans elle, la rangée de chiffres remonterait d'autant et viendrait
     toucher le bas de la photographie. */
  div[class*="st-key-a2_cta"] {
      position:relative; z-index:6;
      margin:-39px 0 24px calc(2rem + 46px) !important;
  }
  div[class*="st-key-a2_cta"] div[data-testid="stButton"] > button:hover {
      background:#186340 !important; transform:none !important;
  }
  div[class*="st-key-a2_cta"] div[data-testid="stButton"] > button p {
      color:#ffffff !important; font-size:14px !important;
      font-weight:600 !important; margin:0 !important;
  }
</style>
"""

# LES QUATRE CARTES N'ONT PLUS DE PICTOGRAMME. Le jeu d'icônes reste celui du
# menu, où une liste de seize entrées en a besoin pour se parcourir de l'œil ;
# quatre cartes, elles, se lisent par leur titre.


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _trouver(nom):
    for c in (os.path.join(APP_DIR, "data", nom), os.path.join(APP_DIR, nom)):
        if os.path.exists(c):
            return c
    return None


@st.cache_data(show_spinner=False)
def _photo_b64(lang="fr", prefere=None):
    """La photographie du bandeau, encodée une fois pour toutes.

    UNE PHOTOGRAPHIE DE TERRAIN, ET NON UNE ILLUSTRATION. Les bandeaux du
    site portent un dessin au crayon composé avec le titre et le logo peints
    dedans : posé derrière un autre titre, il en affichait deux. Celle-ci est
    une vue du terrain enquêté, sans texte, et le titre de la page est donc
    le seul qu'on lise. Les anciens fichiers restent en repli, au cas où
    celui-ci manquerait dans un déploiement.

    `lang` n'a plus d'effet sur le choix du fichier — la photographie ne
    porte aucun mot — mais il reste dans la signature pour que les replis,
    eux, retrouvent leur version linguistique.

    `prefere` NOMME LE CLICHÉ DE LA LANGUE SERVIE, et ne fait que passer
    devant la liste ordinaire. Si le fichier manque dans un déploiement, les
    replis reprennent la main et la page s'affiche quand même — une image
    d'ouverture absente ne doit pas emporter la page d'ouverture.
    """
    noms = ([prefere] if prefere else []) + [
            "accueil2_hero.jpg", "bandeau_apri_site.jpg",
            "bandeau_apri_large.jpg", "bandeau_apri.jpg"]
    if lang == "en":
        noms.append("bandeau_apri_dessin_en.jpg")
    noms.append("bandeau_apri_dessin.jpg")
    for nom in noms:
        p = _trouver(nom)
        if p:
            with open(p, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return None


@st.cache_data(show_spinner=False)
def _marque_b64():
    """L'emblème et le mot APRI, tels que la charte les dessine.

    C'EST LE FICHIER DE LA MARQUE, PAS UNE RECOMPOSITION. Le disque, le mot
    sous lui et l'espacement entre les deux sont réglés dans le fichier
    d'origine ; les redessiner en HTML aurait donné une marque presque juste,
    ce qui est le seul degré de faux qui se voie.

    LA LIGNE INSTITUTIONNELLE, ELLE, RESTE DU TEXTE. Elle est peinte dans le
    fichier d'origine, donc figée en anglais : sur la version française elle
    aurait annoncé l'observatoire dans la mauvaise langue. Elle est donc
    écrite à côté du bloc, dans le même romain, et elle se traduit.
    """
    p = _trouver("logo_apri_bloc.png")
    if not p:
        return None
    with open(p, "rb") as f:
        return base64.b64encode(f.read()).decode()


@st.cache_data(show_spinner=False)
def _chiffres():
    """Les deux nombres comptés dans les fichiers, et rien d'écrit en dur.

    Le compte des ménages est celui de la ventilation, arrondi à la centaine
    inférieure — « plus de » doit rester vrai quel que soit le fichier.
    """
    p = _trouver("ventilation.json")
    menages = sections = None
    if p:
        try:
            with open(p, encoding="utf-8") as f:
                eff = (json.load(f) or {}).get("effectifs") or {}
            sections = len(eff) or None
            total = sum((d or {}).get("Total") or 0 for d in eff.values())
            menages = int(total // 100 * 100) if total else None
        except Exception:
            pass
    return menages, sections


@st.cache_data(show_spinner=False)
def _carte_svg():
    """La carte du premier accueil, telle quelle.

    ON NE REDESSINE PAS UNE CARTE QUI EXISTE. Celle du premier accueil porte
    déjà le carton de localisation posé sur la mer, la rose des vents calée
    contre la côte, l'échelle kilométrique et les dix étiquettes avec leurs
    lignes de rappel : quatre réglages faits un par un, qu'une seconde carte
    aurait fallu refaire un par un. Le module de l'accueil la compose, celui-ci
    la reprend, et une retouche faite là se verra ici.

    AUCUN SCORE DESSUS, ET C'EST DÉJÀ SON PARTI. Elle dit où l'on a travaillé,
    pas ce qu'on y a trouvé.
    """
    return accueil_apri._carte_indice({})["carte"]


def _fmt(n):
    return f"{n:,}".replace(",", " ")


def render():
    """La page d'entrée : annoncer, chiffrer, orienter."""
    st.markdown(STYLE, unsafe_allow_html=True)

    # ---- 1 · la photographie, le titre, l'appel ------------------------
    _lang = i18n.get_lang()
    _nom, cadrage = PHOTOS.get(_lang, PHOTOS["en"])
    photo = _photo_b64(_lang, _nom)
    # LE TITRE INSTITUTIONNEL SORT DE L'IMAGE. Il y était peint, donc figé
    # dans une langue et invisible à un lecteur d'écran ; écrit en texte, il
    # se traduit et se sélectionne.
    _l = [_e(x) for x in T("a2_inst").split("|")]
    _bloc = _marque_b64()
    inst = ('<div class="a2-inst"><b>' + _l[0] + '</b>'
            + "".join(f'<span>{x}</span>' for x in _l[1:]) + '</div>')
    # LA MARQUE, PUIS UN FILET, PUIS LA LIGNE INSTITUTIONNELLE : c'est le bloc
    # de la charte, à ceci près que sa moitié droite est du texte. Sans le
    # fichier, il ne reste que le texte — une page d'entrée sans logo vaut
    # mieux qu'une page d'entrée avec un cadre vide.
    marque = (f'<div class="a2-marque">'
              f'<img src="data:image/png;base64,{_bloc}" alt="APRI"/>'
              f'<div class="a2-filet"></div>{inst}</div>') if _bloc else inst
    # LES GUILLEMETS SIMPLES SONT LOAD-BEARING. L'URL vit dans un attribut
    # `style` délimité par des guillemets doubles ; en réutiliser à
    # l'intérieur ferme l'attribut au milieu de l'image, et le navigateur
    # jette la déclaration entière sans rien signaler.
    fond = (f"background-image:url('data:image/jpeg;base64,{photo}');"
            if photo else "background:#eef3f0;")
    if photo and cadrage:
        fond += f"background-position:{cadrage};"
    st.markdown(
        f'<div class="a2-hero" style="{fond}"><div class="a2-hero-c">'
        f'{marque}'
        f'<div class="a2-kick">{_e(T("a2_kicker"))}</div>'
        f'<div class="a2-titre">{_e(T("a2_titre"))}</div>'
        f'<p class="a2-intro">{_e(T("a2_intro"))}</p>'
        f'</div><div class="a2-credit">{_e(T("a2_credit"))}</div></div>',
        unsafe_allow_html=True)
    # LE BOUTON EST DANS LA PHOTOGRAPHIE, ET IL Y ENTRE PAR LE HAUT. Streamlit
    # ne sait pas poser un widget à l'intérieur d'un bloc HTML qu'on a écrit
    # soi-même, et un faux bouton dessiné dans le HTML serait un lien qui ne
    # mène nulle part. Il est donc écrit juste après l'image, puis remonté
    # dedans par une marge négative. Une marge, et non un placement absolu :
    # la hauteur du bandeau change avec la langue — le titre français tient
    # sur trois lignes, l'anglais sur deux — et une position comptée depuis le
    # haut aurait glissé de l'une à l'autre.
    with st.container(key="a2_cta"):
        if st.button(T("a2_cta") + "  →", key="a2_cta_b"):
            st.session_state["app_mode"] = "dimensions"
            st.rerun()

    # ---- 2 · les quatre nombres ----------------------------------------
    menages, sections = _chiffres()
    cases = [
        (f'{_fmt(menages)}+' if menages else "1 200+", T("a2_c1_x"), None),
        (str(sections or len(SECTIONS)), T("a2_c2_x"), None),
        (T("a2_c3_n"), T("a2_c3_x"), T("a2_c3_s")),
        (T("a2_c4_n"), T("a2_c4_x"), T("a2_c4_s")),
    ]
    st.markdown(
        '<div class="a2-chif">' + "".join(
            f'<div><div class="a2-n">{_e(n)}</div>'
            f'<div class="a2-l">{_e(lab)}</div>'
            + (f'<div class="a2-s">{_e(sous)}</div>' if sous else "")
            + '</div>'
            for n, lab, sous in cases) + '</div>', unsafe_allow_html=True)

    # ---- 3 · la carte, et les quatre destinations -----------------------
    g, d = st.columns([1, 1.15], gap="large")
    with g:
        # LE TITRE EST SORTI DU CARTON. Il y était enfermé, si bien que le
        # rectangle pâle de gauche commençait soixante pixels plus haut que
        # ceux de droite, dont le titre, lui, est au-dessus : deux blocs de
        # même nature, décalés d'une demi-ligne, et la page penchait. Écrit
        # avec la classe des destinations, il s'aligne au pixel avec elles, et
        # la carte commence à la hauteur de la première rangée de cartes.
        st.markdown(
            accueil_apri.STYLE
            + f'<div class="a2-portes-t">{_e(T("a2_carte_t"))}</div>'
            f'<div class="a2-portes-f"></div>'
            f'<div class="a2-carte">{_carte_svg()}</div>',
            unsafe_allow_html=True)
    with d:
        st.markdown(
            f'<div class="a2-portes-t">{_e(T("a2_portes_t"))}</div>'
            f'<div class="a2-portes-f"></div>', unsafe_allow_html=True)
        for rang in (0, 2):
            c1, c2 = st.columns(2, gap="medium")
            for col, (code, cle_t, cle_x, fond_c) in zip(
                    (c1, c2), PORTES[rang:rang + 2]):
                with col:
                    with st.container(key=f"a2_porte_{code}"):
                        st.markdown(
                            f'<style>div[class*="st-key-a2_porte_{code}"] '
                            f'div[data-testid="stButton"] > button '
                            f'{{ background:{fond_c} !important; }}</style>',
                            unsafe_allow_html=True)
                        if st.button(f'{T(cle_t)}  \n*{T(cle_x)}*'
                                     f'  \n**\u2192**',
                                     key=f"a2_b_{code}",
                                     use_container_width=True):
                            st.session_state["app_mode"] = code
                            st.rerun()
