"""
Enquête ménage 2024 — explorateur interactif
=============================================
Filtres combinables (sexe, catégorie économique, groupe d'âge, paysage,
section communale) + résultats bruts (n / %) et graphique pour n'importe
quelle question de l'enquête, calculés à la volée sur la population filtrée.

Toute la logique de calcul vit dans compute_banner_data.py (déjà utilisée
pour produire les classeurs Excel du projet) : on la relance en sous-processus
avec les filtres choisis passés par variables d'environnement, on récupère
le résultat, et on l'affiche.
"""

import io
import json
import os
import pickle
import re
import subprocess
import sys

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# `accueil_page` n'est plus appelé : « Le territoire » ne porte plus que
# ses deux cartes, et son rendu vit dans `territoire_page`.
import accueil_apri
import actualites
import assets
import boucles_page
import cadre_page
import analyse_ecarts
import croisement_resultats
import dimension_page
import environnement_page
import explorateur
import fiche_paysages
import filtres
import icones
import interventions_page
import i18n
import map_render
import methodologie_page
import ondes_choc
import ocb_page
import rapport_donateur
import resilience_page
import saillants_page
import si_je_change
import systeme_page
import pistes_page
import synthese_page
import telechargements_page
import territoire_page
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_CSV = os.path.join(APP_DIR, "data", "donnees_anonymisees.csv")
QUESTIONS_INDEX = os.path.join(APP_DIR, "data", "questions_index.json")
CACHE_NATIONAL = os.path.join(APP_DIR, "data", "cache_national.pkl")

SUBCOLS = ["Total", "Homme", "Femme", "Cat A", "Cat B", "Cat C",
           "<25", "25-39", "40-59", "60+", "Littoral", "Montagne"]

SECTION_RAW = {
    "Anse à Drick": "Anse e Drick",
    "Barbois": "Barbois",
    "Dumont": "Dumont",
    "Débouchette": "Debouchette",
    "Mouline": "Mouline",
    "Quentin": "Quentin",
    "Beaulieu": "Beaulieu",
    "Blactote": "Blactote",
    "Dalmette": "Dalmette",
    "Trichet": "Trichet",
}
PAYSAGE_RAW = {"Littoral": "Littoral (ou plaene cotiere)", "Montagne": "Montagne"}

# ----------------------------------------------------------------------
# Accès protégé par mot de passe simple (voir le guide de déploiement pour
# configurer APP_PASSWORD dans les "Secrets" de Streamlit Cloud).
# ----------------------------------------------------------------------
def check_password():
    try:
        expected = st.secrets.get("APP_PASSWORD", None)
    except Exception:
        expected = None  # aucun fichier de secrets configuré -> accès libre (usage local)
    if not expected:
        return True  # pas de mot de passe configuré -> accès libre (usage local)
    if st.session_state.get("authed"):
        return True
    st.title("Household resilience survey 2024 — Haiti")
    pw = st.text_input("Mot de passe", type="password")
    if st.button("Entrer") or pw:
        if pw == expected:
            st.session_state["authed"] = True
            st.rerun()
        elif pw:
            st.error("Mot de passe incorrect.")
    return False


@st.cache_data(show_spinner=False)
def load_questions_index():
    with open(QUESTIONS_INDEX, encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner="Calcul en cours pour cette combinaison de filtres…")
def compute_filtered(sexe, cat, age, paysage, sections):
    """Run compute_banner_data.py in a subprocess with the given combinable
    filters and return {'base_n':..., 'themes':[...]}. Cached by the exact
    filter tuple, so repeat views are instant."""
    if not (sexe or cat or age or paysage or sections):
        with open(CACHE_NATIONAL, "rb") as f:
            return pickle.load(f)

    env = os.environ.copy()
    env["DATA_CSV_PATH"] = DATA_CSV
    if sexe:
        env["SEXE_FILTER"] = ",".join(sexe)
    if cat:
        env["CAT_FILTER"] = ",".join(cat)
    if age:
        env["AGE_FILTER"] = ",".join(age)
    if paysage:
        env["PAYSAGE_FILTER"] = ",".join(PAYSAGE_RAW[p] for p in paysage)
    if sections:
        env["SECTION_FILTER_MULTI"] = ",".join(SECTION_RAW[s] for s in sections)

    out_path = os.path.join(APP_DIR, "data", "_tmp_live.pkl")
    result = subprocess.run(
        [sys.executable, os.path.join(APP_DIR, "dump_theme_data.py"), out_path],
        cwd=APP_DIR, env=env, capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr[-2000:])
    with open(out_path, "rb") as f:
        data = pickle.load(f)
    os.remove(out_path)
    return data


def rows_to_dataframe(theme, base_n):
    recs = []
    for label, group_n in theme["rows"]:
        row = {T("q_modalite"): label}
        for g in SUBCOLS:
            n = group_n.get(g, 0)
            b = base_n.get(g, 0)
            row[f"{g} (n)"] = n
            row[f"{g} (%)"] = round(n / b * 100, 1) if b else 0.0
        recs.append(row)
    return pd.DataFrame(recs)


def export_excel(theme, base_n):
    buf = io.BytesIO()
    df = rows_to_dataframe(theme, base_n)
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=T("q_resultat")[:31], index=False)
    buf.seek(0)
    return buf


# ----------------------------------------------------------------------
# LA COLONNE DE GAUCHE EST OUVERTE, ET ELLE LE RESTE.
# Streamlit laisse replier sa barre latérale d'un clic, et il garde ce choix
# d'une visite à l'autre : un clic malheureux, et le site s'ouvre sans sa
# navigation à la visite suivante, sans que rien n'explique où elle est
# passée. Ici la colonne n'est pas un panneau d'options, c'est le seul chemin
# vers les onze rubriques. On l'ouvre au démarrage, et la feuille de style
# retire le bouton qui permettait de la fermer.
st.set_page_config(page_title="Household resilience survey — Sud & Grand'Anse, Haiti",
                   layout="wide", initial_sidebar_state="expanded")

if not check_password():
    st.stop()

# Typographie de toute l'application. Deux principes : une seule famille
# (Roboto, la police institutionnelle du PNUE, avec repli système si la
# connexion aux polices Google échoue), et une largeur de ligne bornée —
# une phrase qui court sur 1400 px est illisible, c'est ce qui rendait les
# blocs de texte pénibles à lire.
st.markdown(("""
<style>
  /* UNE SEULE FAMILLE, ET C'EST UN CHOIX DE SOBRIÉTÉ. Les titres étaient en
     Outfit, une géométrique aux formes rondes qui donnait au site un air de
     page produit ; le corps était en Inter. Deux dessins qui se répondaient
     mal, et un contraste qui attirait l'œil sur la police au lieu du chiffre.
     Inter porte maintenant tout : ses chiffres sont tabulaires, ses formes
     neutres, et un observatoire n'a pas à avoir de voix typographique. */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  /* ------------------------------------------------------------------
     Parti pris : une page web, pas un document. Fond teinté, contenu
     posé dessus en cartes blanches avec du relief, coins arrondis,
     survol qui répond. Aucun texte gris minuscule : les commentaires
     de lecture sont lisibles ou ils n'ont pas lieu d'être.
     ------------------------------------------------------------------ */
  :root {
    --encre:      #101728;
    --encre-2:    #3c4761;
    --encre-3:    #6b7590;
    --fond:       #ffffff;
    --fond-2:     #f4f8fc;
    --carte:      #ffffff;
    --bord:       #e6ecf4;
    /* L'ACCENT DU CONTENU EST VERT DEPUIS QUE LES ÉTATS SÉLECTIONNÉS LE
       SONT. Il restait bleu — hérité d'une charte antérieure — et servait la
       pastille de rubrique, le filet des encadrés d'information, le liseré de
       champ actif : trois pièces de chrome qui juraient avec un onglet actif
       vert à quelques centimètres. Les couleurs de données ne bougent pas :
       un graphique bleu reste bleu, c'est une donnée, pas un état. */
    --accent:     #1a6b52;
    --accent-2:   #0f9d8f;
    --accent-3:   #f0a02a;
    --ombre:      0 1px 2px rgba(16,23,40,.04), 0 6px 18px rgba(16,23,40,.05);
    --ombre-haut: 0 3px 6px rgba(16,23,40,.07), 0 20px 44px rgba(16,23,40,.14);
  }

  /* Fond de travail blanc : les graphiques sont dessinés sur blanc, et aucune
     teinte de page ne peut jurer avec eux. La compartimentation ne passe donc
     plus par la couleur mais par le relief — filet fin, ombre douce, et une
     élévation franche au survol. */
  .stApp { background: var(--papier); }
  html, body, [class*="css"], .stApp {
    font-family: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;
    color: var(--encre-2);
  }
  /* padding-top nul : la photo est le premier élément de la page d'entrée et
     doit toucher le haut de la fenêtre. Sur les autres pages, où il n'y a
     plus rien au-dessus du titre, c'est .bh-vide qui redonne l'air. */
  /* ================= LA DENSITÉ DE LA PAGE ==============================
     Le site se lisait en descendant sans arrêt : une page tenait rarement sur
     un écran, et le lecteur passait son temps à faire défiler pour retrouver
     ce qu'il venait de voir. La cause n'était pas seulement la taille des
     lettres, c'était surtout l'air entre les blocs.

     DEUX RÉGLAGES, ET LE SECOND FAIT L'ESSENTIEL :

     1. L'espace entre deux blocs empilés descend d'un cran, et le pied de
        page perd la moitié de son vide. Cinq rem de blanc sous le dernier
        élément, c'était un demi-écran pour rien.
     2. Le contenu est mis à l'échelle de `--z`, une fois pour toutes. Réduire
        seulement la taille des lettres n'aurait presque rien donné : les
        pages sont hautes à cause des marges, des rembourrages de carte et
        des hauteurs de graphique, tous écrits en pixels dans une vingtaine
        de fichiers. `zoom` les prend tous ensemble, dans la même proportion,
        sans qu'aucune valeur ait à être retouchée et sans rien déformer.

     LA COLONNE DE GAUCHE N'EST PAS MISE À L'ÉCHELLE : une navigation qui
     rétrécit avec le contenu devient moins facile à viser, alors qu'elle ne
     coûte rien en hauteur. Le zoom ne porte que sur la zone de contenu. */
  /* LA RACINE DESCEND DE 16 À 14,5 PIXELS. C'est le seul levier qui atteigne
     le corps de texte du site : la très grande majorité des paragraphes
     n'ont aucune taille écrite, ils héritent de la racine. Tout ce que
     Streamlit exprime en `rem` — gouttières, hauteurs de widget, marges de
     titre — suit dans la même proportion, ce qui évite qu'un texte plus petit
     flotte dans des blocs restés grands. */
  /* LA TAILLE REMONTE, MAINTENANT QUE LA PAGE EST PLEINE LARGEUR. Le corps
     avait été descendu à 14,5 px et le zoom à 0,88 pour faire tenir plus de
     contenu sur un écran, à une époque où la colonne était bornée à 1240 px.
     La borne ayant sauté, la largeur ne manque plus : c'est la lisibilité qui
     manquait. Le zoom porte l'essentiel de la reprise, parce qu'il agit sur
     tout — y compris les dizaines de composants dont la taille est écrite en
     pixels fixes — et conserve donc exactement les proportions entre les
     éléments. La racine suit d'un cran, pour le texte courant qui en hérite.
     Total : environ 12 % de plus qu'avant. */
  html { font-size: 15.2px; }
  :root { --z: .95; --dz: 1.0526; }
  section.stMain, div[data-testid="stMain"] { zoom: var(--z); }
  /* PLEINE LARGEUR. La colonne était bornée à 1240 px : sur un grand écran,
     un tiers de la page restait blanc à droite pendant que les tableaux se
     serraient. La borne saute, deux gouttières suffisent à empêcher le texte
     de toucher les bords. */
  .block-container { max-width: none; padding-top: 0; padding-bottom: 2.4rem;
                     padding-left: 2.6rem; padding-right: 2.6rem; }
  div[data-testid="stMainBlockContainer"] { padding-top: 1.2rem; }
  div[data-testid="stVerticalBlock"] { gap: .65rem; }
  div[data-testid="stElementContainer"] { margin-bottom: 0; }

  /* ================= la barre d'outils de Streamlit : SUPPRIMÉE ==========
     « Share », « Deploy », le menu ⋮, la barre colorée de chargement : ce sont
     les commandes de l'ATELIER Streamlit, pas du site. Elles se posaient en
     haut à droite, par-dessus le logo du PNUE, et n'ont rien à faire dans un
     tableau de bord institutionnel qu'on montre à des partenaires.

     Les rendre transparentes ne suffisait pas — le texte restait lisible sur
     le vert. Elles sont maintenant retirées de la mise en page, à tous les
     noms sous lesquels Streamlit les publie : le nom change d'une version à
     l'autre, et n'en viser qu'un revient à voir la barre revenir au prochain
     déploiement.

     Ce qui n'est PAS touché : le bouton de repli de la colonne de gauche, qui
     appartient à la barre latérale et non à cet en-tête. */
  header[data-testid="stHeader"],
  [data-testid="stToolbar"],
  [data-testid="stToolbarActions"],
  [data-testid="stStatusWidget"],
  [data-testid="stDecoration"],
  [data-testid="stAppDeployButton"],
  [data-testid="stMainMenu"],
  #MainMenu,
  .stDeployButton,
  .stAppDeployButton,
  footer {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
  }

  /* LES QUELQUES ENDROITS QUE STREAMLIT HABILLE LUI-MÊME. Les légendes, les
     libellés de widgets et le contenu des menus déroulants portent la police
     du thème — « Source Sans » — et non la nôtre : trois familles cohabitaient
     donc sur la même page sans que personne ne l'ait décidé. On les ramène à
     Inter, et on rend aux icônes leur propre fonte juste après, sinon elles
     s'affichent en toutes lettres. */
  [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] *,
  [data-testid="stWidgetLabel"] *, [data-testid="stRadio"] label *,
  [data-baseweb="select"] div, [data-baseweb="select"] span,
  [data-baseweb="popover"] li, [data-baseweb="tab"] *,
  [data-testid="stExpander"] summary p {
    font-family: "Inter", system-ui, -apple-system, sans-serif !important;
  }
  /* ET ON REND AUX ICÔNES LEUR FONTE. Une icône Streamlit est une ligature :
     le mot « arrow_right » dessiné par la fonte Material. Lui imposer Inter
     l'affiche en toutes lettres au milieu du titre — c'est arrivé sur les
     volets repliés, et la règle ci-dessus l'a causé avant de le corriger. */
  [data-testid="stIconMaterial"], span[class*="material-symbols"],
  [data-testid="stExpander"] summary svg + span:empty,
  .material-icons, .material-symbols-rounded, .material-symbols-outlined {
    font-family: "Material Symbols Rounded", "Material Icons" !important;
  }

  /* --- titres --- */
  h1, h2, h3 {
    font-family: "Inter", system-ui, -apple-system, sans-serif !important;
    color: var(--encre); letter-spacing: -0.02em;
  }
  /* Les trois niveaux de titre sont coupés en plus de la racine : c'est là
     que la taille se voyait le plus, un titre de page occupant à lui seul une
     bande de l'écran pour six mots. */
  h1 { font-weight: 700 !important; font-size: 2rem !important;
       line-height: 1.14 !important; }
  h2 { font-weight: 700 !important; font-size: 1.35rem !important;
       margin-top: .2rem !important; padding-bottom: .2rem !important; }
  h3 { font-weight: 600 !important; font-size: 1.1rem !important;
       margin-top: .2rem !important; }

  /* --- texte : jamais minuscule, jamais délavé --- */
  [data-testid="stMarkdownContainer"] p,
  [data-testid="stMarkdownContainer"] li {
    font-size: 14.5px; line-height: 1.66; color: var(--encre-2);
  }
  [data-testid="stMarkdownContainer"] strong { color: var(--encre); }
  [data-testid="stCaptionContainer"] p {
    font-size: 14px !important; line-height: 1.62 !important;
    color: var(--encre-2) !important; max-width: 92ch;
  }

  /* ------------------------------------------------------------------
     LES CARTES. Tout bloc encadré (st.container(border=True)) devient
     une carte blanche en relief qui se soulève au survol.
     ------------------------------------------------------------------ */
  /* Une carte = un bloc encadré qui contient une pilule de titre. On le cible
     par son contenu (:has), parce que Streamlit ne donne pas de marqueur propre
     aux conteneurs bordés — et que le nom technique de ces conteneurs change
     d'une version à l'autre. */
  div[data-testid="stVerticalBlock"]:has(
      > div[data-testid="stElementContainer"] .titre-bloc),
  div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--carte) !important;
    border: 1px solid var(--bord) !important;
    border-radius: 18px !important;
    box-shadow: var(--ombre);
    padding: 16px 20px 18px !important;
    transition: box-shadow .2s ease, transform .2s ease, border-color .2s ease;
    animation: apparition .5s cubic-bezier(.2,.7,.3,1) both;
  }
  div[data-testid="stVerticalBlock"]:has(
      > div[data-testid="stElementContainer"] .titre-bloc):hover,
  div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: var(--ombre-haut); transform: translateY(-3px) !important;
    border-color: #c3ded0 !important;
  }
  /* Les blocs des conditions du croisement, imbriqués, restent discrets. */
  div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"]
      .titre-bloc) div[data-testid="stVerticalBlock"][style*="border"] {
    box-shadow: none; animation: none;
  }

  @keyframes apparition {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: none; }
  }

  /* --- l'entête de section, en pilule colorée --- */
  .titre-bloc {
    display: inline-flex; align-items: center; gap: 9px;
    font-family: "Inter", system-ui, sans-serif; font-weight: 700; font-size: 12px;
    letter-spacing: .06em; text-transform: uppercase;
    color: var(--accent); background: #eaf5f0;
    padding: 6px 13px; border-radius: 999px; margin: 0 0 4px;
  }
  .titre-bloc.vert  { color: #0b7f74; background: #e5f6f3; }
  .titre-bloc.ambre { color: #a8690a; background: #fdf3e3; }

  /* --- menus : champs pleins, arrondis, réactifs --- */
  label[data-testid="stWidgetLabel"] p {
    font-size: 12px !important; font-weight: 700 !important;
    letter-spacing: .04em; color: var(--encre-3) !important;
    text-transform: uppercase;
  }
  div[data-baseweb="select"] > div {
    font-size: 14.5px; border-radius: 11px; border: 1.5px solid var(--bord);
    background: #f7fafd; transition: border-color .15s ease, box-shadow .15s ease;
  }
  div[data-baseweb="select"] > div:hover { border-color: #b6d8c6; }
  div[data-baseweb="select"] > div:focus-within {
    border-color: var(--accent); box-shadow: 0 0 0 3px rgba(26,107,82,.16);
  }

  /* --- bandeau d'info --- */
  div[data-testid="stAlert"] {
    border: 1px solid var(--bord); border-left: 5px solid var(--accent);
    border-radius: 14px; background: var(--carte); box-shadow: var(--ombre);
    padding: 3px 6px;
  }
  div[data-testid="stAlert"] > div {
    background: transparent !important; border: none !important;
    padding: 12px 14px !important;
  }
  div[data-testid="stAlert"] p {
    font-size: 14.5px !important; color: var(--encre-2) !important; margin: 0;
  }

  details {
    background: var(--carte); border: 1px solid var(--bord) !important;
    border-radius: 14px !important; box-shadow: var(--ombre);
  }
  details summary p {
    font-size: 14px !important; font-weight: 600 !important;
    color: var(--encre-2);
  }

  .org-mention {
    font-size: 11.5px; color: var(--encre-3); letter-spacing: .12em;
    text-transform: uppercase; margin: 0 0 3px 1px; font-weight: 700;
  }

  /* --- les trois entrées : grandes tuiles en relief --- */
  div[data-testid="stButton"] > button {
    height: 92px; border-radius: 16px; border: 1.5px solid var(--bord);
    font-family: "Inter", system-ui, sans-serif !important;
    font-size: 16.5px !important; font-weight: 600 !important;
    line-height: 1.3; white-space: normal; padding: 12px 20px;
    background: var(--carte); box-shadow: var(--ombre);
    transition: transform .18s cubic-bezier(.2,.7,.3,1), box-shadow .18s ease,
                background .18s ease, border-color .18s ease;
  }
  div[data-testid="stButton"] > button p {
    font-size: 16.5px !important; font-weight: 600 !important;
  }
  div[data-testid="stButton"] > button:hover {
    transform: translateY(-3px); box-shadow: var(--ombre-haut);
    border-color: #b6d8c6;
  }
  div[data-testid="stButton"] > button[kind="primary"],
  div[data-testid="stButton"] > button[kind="primary"] p,
  div[data-testid="stButton"] > button[kind="primary"] div { color: #fff !important; }
  /* L'ÉTAT SÉLECTIONNÉ EST VERT, PAS BLEU, ET IL L'EST PARTOUT.
     Le bleu venait d'une charte antérieure et ne se justifiait plus : la
     colonne de navigation, les pastilles de filtre et l'emblème sont verts,
     de sorte qu'un onglet actif en bleu était la seule pièce d'une autre
     couleur — l'œil y lisait un autre type d'objet. Même teinte pour tous
     les états sélectionnés, du bouton à l'onglet en passant par la carte de
     dimension. */
  div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #2b8663 0%, #1c6349 100%) !important;
    border-color: transparent !important;
    box-shadow: 0 2px 6px rgba(28,99,73,.28), 0 14px 30px rgba(28,99,73,.24);
  }
  div[data-testid="stButton"] > button[kind="secondary"],
  div[data-testid="stButton"] > button[kind="secondary"] p {
    color: var(--encre) !important;
  }

  /* --- LES SOUS-ONGLETS, EN BARRE NUMÉROTÉE ---------------------------
     C'est le format du cadre de résilience, repris ici : numéro en gras,
     titre à côté, filet sous la rangée, soulignement vert sur l'onglet
     ouvert. La pastille ronde du sélecteur est enfouie de trois niveaux et
     n'est ni le premier enfant du label ni un pseudo-élément — d'où le
     chemin complet ci-dessous.

     Chaque enveloppe que Streamlit interpose est forcée à la pleine largeur :
     les cases ne contiennent qu'un numéro et deux mots, et un `width:100%`
     calculé sur un parent ajusté au contenu ne donnerait rien. */
  div[class*="st-key-ra_nav"],
  div[class*="st-key-ra_nav"] div[data-testid="stElementContainer"],
  div[class*="st-key-ra_nav"] div[data-testid="stRadio"] {
      width: 100% !important;
  }
  div[class*="st-key-ra_nav"] div[role="radiogroup"] {
      display: flex !important; flex-wrap: nowrap !important; gap: 0 !important;
      width: 100% !important; align-items: stretch;
      border-bottom: 1px solid #e9eef4; margin: 2px 0 12px;
  }
  div[class*="st-key-ra_nav"] div[role="radiogroup"] > label {
      flex: 1 1 0 !important; min-width: 0 !important; margin: 0 !important;
      background: none !important; border: 0 !important;
      padding: 0 14px 11px 0 !important; position: relative; cursor: pointer;
  }
  div[class*="st-key-ra_nav"] div[role="radiogroup"]
      > label > div > div > div:first-child { display: none !important; }
  div[class*="st-key-ra_nav"] div[role="radiogroup"] > label > div > div {
      gap: 0 !important; width: 100% !important;
  }
  div[class*="st-key-ra_nav"] div[role="radiogroup"] > label > div:last-child p,
  div[class*="st-key-ra_nav"] div[role="radiogroup"] > label p {
      font-size: 12px !important; font-weight: 500 !important;
      color: #8a93a5 !important; margin: 0 !important;
      text-align: left !important; line-height: 1.35 !important;
  }
  div[class*="st-key-ra_nav"] div[role="radiogroup"] > label p strong {
      font-size: 13px; font-weight: 700; color: #a7b0be;
      font-variant-numeric: tabular-nums;
  }
  div[class*="st-key-ra_nav"] div[role="radiogroup"] > label:hover p,
  div[class*="st-key-ra_nav"] div[role="radiogroup"] > label:hover p strong {
      color: #3c4761 !important;
  }
  div[class*="st-key-ra_nav"] div[role="radiogroup"]
      > label:has(input:checked) p {
      color: #1a6b52 !important; font-weight: 700 !important;
  }
  div[class*="st-key-ra_nav"] div[role="radiogroup"]
      > label:has(input:checked) p strong { color: #1a6b52; }
  div[class*="st-key-ra_nav"] div[role="radiogroup"]
      > label:has(input:checked)::after {
      content: ""; position: absolute; left: 0; right: 14px; bottom: -1px;
      height: 2px; background: #1a6b52; border-radius: 2px;
  }
  @media (max-width: 900px) {
    div[class*="st-key-ra_nav"] div[role="radiogroup"] {
        flex-wrap: wrap !important; border-bottom: 0;
    }
    div[class*="st-key-ra_nav"] div[role="radiogroup"] > label {
        flex: 1 1 45% !important; padding-bottom: 8px !important;
    }
  }

  /* --- radios : pastilles cliquables --- */
  .stRadio > div[role="radiogroup"] { gap: 8px; flex-wrap: wrap; }
  .stRadio > div[role="radiogroup"] > label {
    background: #f4f8fc; border: 1.5px solid var(--bord);
    border-radius: 999px; padding: 7px 15px 7px 11px;
    transition: all .15s ease;
  }
  .stRadio > div[role="radiogroup"] > label:hover {
    border-color: #b6d8c6; background: #eef8f2;
  }
  .stRadio > div[role="radiogroup"] > label > div:last-child p {
    font-size: 13.5px !important; font-weight: 600 !important;
    color: var(--encre-2);
  }

  /* --- barre latérale --- */
  section[data-testid="stSidebar"] {
    background: #ffffff; border-right: 1px solid var(--bord);
  }
  section[data-testid="stSidebar"] h2 {
    font-size: 1.15rem !important; margin-top: .3rem !important;
  }

  /* --- tableaux --- */
  div[data-testid="stDataFrame"] {
    border: 1px solid var(--bord); border-radius: 12px; overflow: hidden;
  }

  /* --- téléchargements : bouton doux --- */
  div[data-testid="stDownloadButton"] > button {
    height: auto; padding: 9px 18px !important; border-radius: 999px;
    background: #eaf5f0 !important; border: 1.5px solid #cde4d9 !important;
    color: var(--accent) !important; font-weight: 600 !important;
    font-size: 13.5px !important; box-shadow: none;
  }
  div[data-testid="stDownloadButton"] > button:hover {
    background: #dcefe5 !important; transform: translateY(-1px);
  }

  /* --- iframes des graphiques : coins arrondis, fond blanc --- */
  iframe { border-radius: 12px; background: #ffffff; }

  /* ================= barre latérale : la navigation du site =============
     LE VERT PROFOND EST PARTI. Une colonne pleine de couleur sombre pesait
     sur toute la page : elle criait plus fort que le contenu qu'elle sert à
     atteindre, et il fallait tout écrire en blanc dessus, ce qui alourdit
     encore. La colonne est maintenant blanche, séparée du contenu par un
     simple filet, et le seul retour visuel est un fond très clair au
     survol. La navigation se voit quand on la cherche et se tait le reste
     du temps, ce qui est exactement son métier. */
  section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid var(--bord) !important;
    width: 310px !important; min-width: 310px !important;
  }
  /* LA COLONNE NE SE REPLIE PLUS, SUR ÉCRAN LARGE.
     Repliée, Streamlit ne la cache pas : il la fait glisser hors de l'écran
     par une translation, en passant `aria-expanded` à false. Deux règles
     suffisent donc, et il faut les deux : annuler la translation dans cet
     état-là, et retirer le chevron qui la déclenche. Sans la première, un
     état replié mémorisé par le navigateur rouvrirait la page sans
     navigation ; sans la seconde, le chevron resterait là à promettre une
     action qui ne se passe plus.

     LE SEUIL EST INDISPENSABLE. Sous mille pixels, Streamlit ne pousse plus
     le contenu à côté de la colonne : il la pose PAR-DESSUS. Forcer
     l'ouverture là aussi enfermerait le lecteur derrière un panneau qu'il ne
     pourrait plus refermer, ce qui est pire que le défaut qu'on corrige. En
     dessous du seuil, on ne touche à rien et le chevron revient. */
  @media (min-width: 1001px) {
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"][aria-expanded="false"] {
      transform: none !important; visibility: visible !important;
      margin-left: 0 !important;
    }
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {
      display: none !important;
    }
    /* CETTE BANDE VIDE EN HAUT DE LA COLONNE ÉTAIT LE LOGEMENT DU CHEVRON.
       Streamlit lui réserve une hauteur fixe qu'il occupait seul ; le chevron
       retiré, il ne restait qu'un rectangle de blanc au-dessus du choix de
       langue. Il disparaît avec lui, et le contenu remonte en haut de
       l'écran. Sous le seuil, le chevron revient : sa loge aussi. */
    [data-testid="stSidebarHeader"] {
      display: none !important;
    }
    section[data-testid="stSidebar"] > div,
    [data-testid="stSidebarContent"] { padding-top: 0 !important; }
    [data-testid="stSidebarUserContent"] { padding-top: 6px !important; }
  }
  /* Le bloc de marque remonte : dix-huit pixels de blanc au-dessus d'un
     logo, sur une colonne qui commence en haut de l'écran, ne servaient
     qu'à repousser l'identité vers le bas. */
  section[data-testid="stSidebar"] > div { padding: 0 14px 14px; }

  /* Le bloc de marque, sur le modèle de la charte : l'emblème détouré posé
     directement sur le vert — pas de carte blanche, qui faisait une tache —
     puis le nom en texte et un filet vert sous le sigle. L'emblème est
     l'image EMBLEME_APRI, découpée du logo complet : le verbal « IRLA/APRI »
     du fichier d'origine devenait illisible à cette taille. */
  .apri-marque {
    display: flex; align-items: center; gap: 15px;
    padding: 0 2px 14px; margin-bottom: 0;
    border-bottom: 1px solid var(--bord);
  }
  .apri-marque img {
    width: 76px; height: 76px; flex: 0 0 76px; display: block;
  }
  .apri-bloc-nom { min-width: 0; }
  .apri-nom {
    font-family: "Inter", system-ui, sans-serif; font-size: 33.5px; font-weight: 700;
    color: var(--encre); letter-spacing: .01em; line-height: 1;
  }
  .apri-filet {
    width: 64px; height: 3px; border-radius: 2px; background: #6ba03a;
    margin: 5px 0 0;
  }
  /* Deux niveaux dans l'accroche, comme sur la charte : ce qu'est
     l'observatoire, en vert clair, puis où il porte, en blanc. Une seule
     ligne grise disait les deux d'un même souffle et on ne lisait ni l'un ni
     l'autre. */
  .apri-baseline {
    font-size: 11px; color: #5d8c2b; line-height: 1.3;
    margin-top: 6px; font-weight: 500;
  }
  .apri-lieu {
    font-size: 11.5px; color: var(--encre-2); line-height: 1.3;
    margin-top: 3px; font-weight: 600;
  }
  /* Pied de colonne : le logo du PNUE y descend, puisque les logos ne
     doivent plus apparaître dans le contenu des pages. */
  .apri-org {
    display: flex; align-items: center; gap: 10px;
    margin-top: 14px; padding-top: 13px;
    border-top: 1px solid var(--bord);
  }
  /* Le logo institutionnel n'a plus besoin de sa plaque blanche : la colonne
     est blanche. Une plaque sur un fond de même couleur ne se voit pas, elle
     se devine, et une bordure devinée est une bordure de trop. */
  .apri-org img {
    width: 34px; height: 34px; flex: 0 0 34px; object-fit: contain;
  }
  .nav-groupe {
    font-size: 10.5px; letter-spacing: .14em; text-transform: uppercase;
    color: var(--encre-3); font-weight: 700;
    margin: 18px 0 8px 4px;
  }
  .apri-pied {
    font-size: 10.5px; color: var(--encre-3); line-height: 1.5;
    padding: 14px 4px 4px; margin-top: 10px;
    border-top: 1px solid var(--bord);
  }
  /* Dans le bloc PNUE, la mention institutionnelle est déjà séparée par le
     filet de .apri-org : lui laisser le sien dessinait deux traits l'un sur
     l'autre. */
  .apri-org .apri-pied {
    border-top: none; padding: 0; margin: 0; font-size: 11px;
    color: var(--encre-3);
  }

  /* --- les entrées de menu ---------------------------------------------
     Trois réglages qui comptent, et qui manquaient tous les trois au premier
     essai :

     ALIGNEMENT — le bouton de Streamlit centre son contenu par défaut, à
     trois niveaux imbriqués. Un libellé sur deux lignes se retrouvait alors
     indenté au premier rang et collé au bord au second. Il faut forcer
     l'alignement à gauche sur le bouton ET sur ses conteneurs internes, sinon
     l'un des trois reprend la main.

     TAILLE — 15,5 px et 46 px de hauteur minimale : un menu se vise au
     curseur sans regarder, il lui faut une cible franche.

     SURVOL — un fond très clair, et rien d'autre : ni contour, ni ombre, ni
     déplacement. Sans retour au survol, rien ne distingue une ligne
     cliquable d'un simple titre ; avec trois retours à la fois, la colonne
     s'agite. */
  /* LE MENU SUIT LA LECTURE, IL NE RESTE PAS EN HAUT DE PAGE.
     Il vivait dans une colonne aussi haute que son contenu : sur les pages
     longues — Données, Rapport donateur, Analyse des résultats — on le
     perdait de vue au troisième écran et il fallait remonter tout en haut
     pour changer de rubrique. La colonne se colle donc au haut de la fenêtre
     et y reste. `align-self: flex-start` est indispensable : sans lui,
     Streamlit étire la colonne sur toute la hauteur de la ligne, et un
     élément étiré ne peut pas coller. Si le menu dépasse la fenêtre, il
     défile pour son propre compte. */
  /* LA BARRE EST UNE RANGÉE, ET ELLE RESTE EN HAUT.
     Streamlit empile ses éléments : on met donc son bloc vertical en `flex`
     avec `flex-wrap`, et les boutons se rangent côte à côte. Chacun prend la
     largeur de son mot — plus de `width:100%` — et la rangée passe à la ligne
     quand la fenêtre se rétrécit. `position: sticky` la garde à l'écran quand
     la page défile, ce que la colonne de gauche faisait déjà. */
  /* LE CONTENEUR À CLÉ EST LUI-MÊME LE BLOC VERTICAL. Streamlit pose la
     classe `st-key-…` sur le `stVerticalBlock`, pas sur un parent : c'est
     donc lui qu'on met en `flex`, et ses enfants directs — les conteneurs
     d'élément — deviennent les cases de la rangée. */
  div[class*="st-key-zone_nav"] {
    display: flex !important; flex-direction: row !important;
    flex-wrap: wrap !important; align-items: center !important;
    gap: 0 2px !important;
    position: sticky; top: 0; z-index: 20;
    background: rgba(255,255,255,.97);
    backdrop-filter: saturate(1.4) blur(6px);
    border-bottom: 1px solid #eef2f7;
    margin: 0 calc(-2.6rem * var(--dz)) 0;
    padding: 3px calc(2.6rem * var(--dz)) 2px;
  }
  div[class*="st-key-zone_nav"] div[data-testid="stElementContainer"],
  div[class*="st-key-zone_nav"] div[data-testid="stButton"] {
    width: auto !important; flex: 0 0 auto !important;
  }
  div[class*="st-key-zone_nav"] div[data-testid="stButton"] > button {
    display: flex !important; align-items: center !important;
    justify-content: center !important;
    width: auto !important; min-height: 31px !important; height: auto !important;
    padding: 6px 9px !important; border-radius: 8px !important;
    border: none !important;
    background: transparent !important; box-shadow: none !important;
    transition: background .15s ease, color .15s ease;
    white-space: nowrap;
  }
  div[class*="st-key-zone_nav"] div[data-testid="stButton"] > button > div,
  div[class*="st-key-zone_nav"] div[data-testid="stButton"] > button
    div[data-testid="stMarkdownContainer"] {
    width: auto !important; text-align: center !important;
    display: block !important;
  }
  div[class*="st-key-zone_nav"] div[data-testid="stButton"] > button p {
    font-family: "Inter", system-ui, sans-serif !important;
    font-size: 12.5px !important; font-weight: 500 !important;
    line-height: 1.2 !important;
    color: var(--encre-2) !important;
    text-align: center !important; margin: 0 !important;
    white-space: nowrap;
  }
  div[class*="st-key-zone_nav"] div[data-testid="stButton"] > button:hover {
    background: #f1f6f4 !important; transform: none !important;
  }
  div[class*="st-key-zone_nav"]
    div[data-testid="stButton"] > button:hover p {
    color: var(--encre) !important;
  }
  /* L'ENTRÉE ACTIVE : un filet vert dessous et le mot en gras vert. Un fond
     plein, sur une rangée de quatorze, aurait fait une tache ; le filet dit
     la même chose sans peser. */
  div[class*="st-key-zone_nav"]
    div[data-testid="stButton"] > button[kind="primary"] {
    background: transparent !important;
    border: none !important; box-shadow: none !important;
    border-bottom: 2px solid var(--accent) !important;
    border-radius: 8px 8px 0 0 !important;
  }
  div[class*="st-key-zone_nav"]
    div[data-testid="stButton"] > button[kind="primary"] p {
    color: var(--accent) !important; font-weight: 700 !important;
  }
  div[class*="st-key-zone_nav"]
    div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #f1f6f4 !important;
  }
  /* Le sélecteur de langue, seul widget non bouton de la colonne */
  section[data-testid="stSidebar"] label,
  section[data-testid="stSidebar"] .stRadio label p {
    color: var(--encre-2) !important;
  }
  section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background: #fbfcfe; border-color: var(--bord);
    color: var(--encre);
  }
  section[data-testid="stSidebar"] div[data-baseweb="select"] svg {
    fill: var(--encre-3);
  }

  /* --- le raccourci « filtres rapides » de la colonne ------------------ */
  .f-separateur {
    height: 1px; background: var(--bord); margin: 16px 2px 2px;
  }
  .nav-etat {
    font-size: 11.5px; color: var(--encre-3); line-height: 1.45;
    padding: 6px 6px 0;
  }
  /* Le bouton de remise à zéro ne doit pas se lire comme une entrée de menu :
     il agit sur le filtre, pas sur la navigation. Contour discret, hauteur
     réduite, et son icône de rafraîchissement. */
  section[data-testid="stSidebar"] div[class*="st-key-f_reset_global"]
    div[data-testid="stButton"] > button {
    min-height: 38px !important; padding: 8px 13px !important;
    border: 1px solid var(--bord) !important;
    background: #fbfcfe !important;
    border-radius: 9px !important;
  }
  section[data-testid="stSidebar"] div[class*="st-key-f_reset_global"]
    div[data-testid="stButton"] > button p {
    font-size: 12.5px !important; font-weight: 500 !important;
  }
  section[data-testid="stSidebar"] div[class*="st-key-f_reset_global"]
    div[data-testid="stButton"] > button:disabled { opacity: .5; }
  __ICONE_RESET__
  section[data-testid="stSidebar"] div[data-testid="stSelectbox"] label p {
    font-size: 11.5px !important; letter-spacing: .04em;
    color: var(--encre-3) !important; font-weight: 600 !important;
    text-transform: uppercase;
  }
  /* Le bouton « Réinitialiser » ne doit pas ressembler à une entrée de menu :
     il agit sur le filtre, pas sur la navigation. C'est le seul bouton de la
     colonne placé dans une rangée de colonnes — on le cible par là, faute de
     pouvoir donner une classe à un bouton Streamlit. */
  section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]
    div[data-testid="stButton"] > button {
    min-height: 0 !important; padding: 4px 9px !important;
    justify-content: center !important; margin: 0;
    border: 1px solid var(--bord) !important;
  }
  section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]
    div[data-testid="stButton"] > button p {
    font-size: 11.5px !important; font-weight: 600 !important;
    text-align: center !important;
    color: var(--encre-2) !important;
  }
  section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]
    div[data-testid="stButton"] > button:disabled {
    opacity: .45; border-color: var(--bord) !important;
  }
  .f-chips { display: flex; flex-direction: column; gap: 6px; margin-top: 11px; }
  .f-chip {
    display: flex; align-items: baseline; gap: 8px;
    background: #f6f9fd; border: 1px solid var(--bord);
    border-radius: 9px; padding: 7px 11px;
  }
  .f-chip-cle {
    font-size: 10px; letter-spacing: .1em; text-transform: uppercase;
    color: var(--encre-3); font-weight: 700; white-space: nowrap;
  }
  .f-chip-val {
    font-size: 12.5px; color: var(--encre); font-weight: 600;
  }
  .f-vide {
    font-size: 11.5px; color: var(--encre-3); line-height: 1.5;
    margin-top: 10px; padding: 0 3px;
  }

  /* ================= l'en-tête de page ===================================
     IL N'Y A PLUS DE RUBAN, et les règles qui l'habillaient ont été retirées
     avec lui : une rangée pleine largeur, des boutons de langue déguisés en
     pastilles, un cadre pour le logo. Les trois contenus sont partis ailleurs
     — la langue en tête de la colonne verte, le logo sur la photo, les
     onglets dans la colonne depuis longtemps — et une feuille de style qui
     décrit un élément disparu est un piège pour la prochaine retouche. */

  /* La photo déborde la colonne de texte et touche les deux bords : c'est
     un en-tête, pas une illustration posée dans le contenu. */
  /* L'enveloppe existe pour que le logo puisse se poser DANS la photo :
     un élément en position absolue se place par rapport au premier parent
     positionné, et l'image seule n'en est pas un. */
  .bandeau-enveloppe { position: relative; display: block; line-height: 0; }
  /* L'ILLUSTRATION OCCUPE TOUTE LA LARGEUR, ET SON VOILE EST DANS LE FICHIER.
     Le dégradé blanc qui éclaircit le tiers gauche a été composé dans l'image
     elle-même plutôt qu'en CSS : il devait effacer une marque déjà incrustée
     dans l'illustration fournie, ce qu'un dégradé posé par-dessus n'aurait pas
     fait proprement aux jointures. */
  /* LES TROIS DÉCLARATIONS SONT FORCÉES. Streamlit impose à toute image un
     `object-fit: scale-down` : l'illustration se réduisait alors pour tenir
     entière dans le bandeau, et se retrouvait posée en petit au milieu d'une
     bande blanche au lieu de la remplir. */
  .bandeau-fond {
    width: 100% !important; height: 246px !important;
    object-fit: cover !important; object-position: 50% 56% !important;
    display: block !important; max-width: none !important;
  }
  /* LA MARQUE VIT DANS L'IMAGE. Elle occupait la tête de la colonne de
     gauche ; la colonne ayant disparu, elle serait devenue orpheline. Posée
     sur le tiers clair de l'illustration, elle redevient ce qu'elle est :
     l'enseigne du site, au même endroit sur toutes les pages. */
  .bandeau-marque {
    position: absolute; top: 50%; left: 42px; transform: translateY(-46%);
    display: flex; align-items: center; gap: 20px; pointer-events: none;
  }
  .bandeau-marque .bm-embleme { height: 92px; width: 92px; display: block; }
  .bandeau-marque .bm-nom {
    font-size: 40px; font-weight: 800; color: #16324a;
    letter-spacing: -.015em; line-height: 1;
  }
  .bandeau-marque .bm-filet {
    height: 3px; width: 100%; background: #2f6b4f; margin: 7px 0 8px;
    border-radius: 2px;
  }
  .bandeau-marque .bm-base {
    font-size: 15.5px; font-weight: 700; color: #2f6b4f; line-height: 1.25;
  }
  .bandeau-marque .bm-lieu {
    font-size: 15px; font-weight: 700; color: #16324a; margin-top: 4px;
  }
  /* LE LOGO EST BLANC ET POSÉ À MÊME L'IMAGE, SANS PLAQUE.
     Le cartouche blanc qu'il portait découpait un rectangle net dans le
     paysage. L'angle de l'illustration a été légèrement assombri à la place
     — un vignetage, pas une plaque — ce qui ramène la clarté du fond autour
     de 119 sur 255 : assez sombre pour qu'un logo blanc s'y détache, assez
     clair pour qu'on ne voie pas une tache. L'ombre portée finit le travail
     là où un nuage passe plus clair. */
  .bandeau-logo {
    position: absolute; top: 22px; right: 30px; height: 62px;
    filter: drop-shadow(0 1px 7px rgba(0,0,0,.45));
  }

  /* LES DEUX LANGUES SE POSENT SUR L'IMAGE, EN HAUT À GAUCHE.
     Ce sont de vrais boutons, donc ils ne peuvent pas vivre dans le HTML de
     l'illustration : on les sort du flux et on les place par-dessus. Le
     conteneur du bloc principal sert de repère, d'où sa position relative. */
  div[data-testid="stMainBlockContainer"] { position: relative; }
  /* LA COLONNE DE GAUCHE EST RETIRÉE, PAS SEULEMENT REPLIÉE. Streamlit garde
     sinon sa poignée d'ouverture en haut à gauche, posée en plein sur la
     marque. */
  section[data-testid="stSidebar"],
  div[data-testid="stSidebarCollapseButton"],
  button[data-testid="stBaseButton-headerNoPadding"] { display: none !important; }
  /* l'illustration reprend la largeur libérée par la colonne */
  .bandeau-haut {
    width: calc(100vw * var(--dz)) !important;
    max-width: calc(100vw * var(--dz)) !important;
    margin-left: calc(50% - 100vw * var(--dz) / 2);
  }
  /* LES TEXTES SONT JUSTIFIÉS.
     Un paragraphe au fer à gauche laisse un bord droit en dents de scie qui,
     sur une colonne large, fait paraître la page moins tenue qu'elle ne l'est.
     La règle ne touche que les paragraphes et les listes du contenu : les
     libellés, les cellules de tableau et les légendes gardent leur alignement,
     sans quoi une ligne de deux mots s'étirerait d'un bord à l'autre. */
  div[data-testid="stMarkdownContainer"] > p,
  div[data-testid="stMarkdownContainer"] > ul > li,
  div[data-testid="stMarkdownContainer"] > ol > li {
    text-align: justify; text-justify: inter-word;
  }
  .f-etiquette { height: 22px; }

  /* --- LES DEUX LANGUES, AU BOUT DE LA BARRE D'ONGLETS -----------------
     EN NOIR SUR BLANC, ET NON PLUS EN BLANC SUR LA PHOTO. L'illustration ne
     paraît plus que sur l'accueil ; un réglage qui n'existerait que sur une
     page n'est pas un réglage. Les pastilles reviennent donc dans la barre,
     poussées tout à droite par une marge automatique, à la même hauteur que
     les rubriques.

     LA LANGUE EN COURS SE MARQUE PAR SON CONTOUR, PAS PAR UN APLAT. Un fond
     plein, au bout d'une rangée d'onglets, se serait lu comme un onglet
     actif de plus — et il aurait fallu du blanc pour le texte, ce qu'on
     cherche justement à quitter. Le trait d'encre et la graisse suffisent :
     tout est noir, rien n'est peint.

     Elles empruntent la classe `st-key-lang_*` de leur bouton : c'est le seul
     point d'accroche stable que Streamlit offre sur un widget précis. Tout ce
     que la barre impose aux boutons est défait ici, explicitement. */
  /* STREAMLIT ENVELOPPE UN CONTENEUR À CLÉ DANS UN BLOC DE MISE EN PAGE, et
     c'est LUI le voisin des onglets dans la rangée. Réglé sur le seul bloc
     intérieur, le retrait automatique laissait l'enveloppe prendre toute la
     largeur : la paire tombait sur une deuxième ligne, à droite mais en
     dessous. Les deux reçoivent donc la même largeur et la même marge. */
  div[class*="st-key-zone_nav"] > div:has(div[class*="st-key-zone_langue"]),
  div[class*="st-key-zone_langue"] {
    margin-left: auto !important; width: 132px !important;
    flex: 0 0 auto !important; min-width: 0 !important;
  }
  /* Streamlit donne au conteneur du bouton la largeur de son mot : sans ces
     deux lignes, le `width:100%` du bouton vaut 100 % de vingt-cinq pixels,
     et la pastille se ferme en rond. La classe à clé est posée SUR le
     conteneur d'élément, pas sur un parent : elle se sélectionne donc
     directement. */
  div[class*="st-key-lang_"],
  div[class*="st-key-lang_"] div[data-testid="stButton"] {
    width: 100% !important;
  }
  div[class*="st-key-lang_"]
  div[data-testid="stButton"] > button,
  div[class*="st-key-lang_"]
  div[data-testid="stButton"] > button[kind="primary"] {
    background: #ffffff !important;
    border: 1px solid #dfe5ee !important;
    border-radius: 999px !important;
    box-shadow: none !important; padding: 3px 4px !important;
    min-height: 0 !important; height: auto !important; width: 100% !important;
    justify-content: center !important; transform: none !important;
    transition: border-color .15s ease, background .15s ease;
  }
  div[class*="st-key-lang_"]
  div[data-testid="stButton"] > button p {
    font-size: 11.5px !important; font-weight: 600 !important;
    letter-spacing: .08em !important; text-transform: uppercase;
    color: #6b7590 !important; text-align: center !important;
    transition: color .15s ease;
  }
  div[class*="st-key-lang_"]
  div[data-testid="stButton"] > button:hover {
    background: #f4f6fa !important; border-color: #c6cfdd !important;
  }
  div[class*="st-key-lang_"]
  div[data-testid="stButton"] > button:hover p {
    color: #101728 !important;
  }
  div[class*="st-key-lang_"]
  div[data-testid="stButton"] > button[kind="primary"] {
    background: #ffffff !important;
    border: 1.5px solid #101728 !important;
  }
  div[class*="st-key-lang_"]
  div[data-testid="stButton"] > button[kind="primary"] p {
    color: #101728 !important; font-weight: 800 !important;
  }
  div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-lang_"]) {
    padding: 0; margin: 0; max-width: 132px; gap: 7px !important;
  }

  /* La ligne de contexte, sous le ruban : la page courante à gauche, ce sur
     quoi porte l'affichage à droite. Un chiffre lu sans savoir qu'un filtre
     est posé est un chiffre mal lu. */
  .bh-contexte {
    display: flex; align-items: center; justify-content: flex-start;
    gap: 16px; flex-wrap: wrap; margin: 12px 0 10px;
  }
  /* Sans ligne de contenu, le bandeau collerait au titre de la page. */
  .bh-vide { height: 20px; }
  .bh-page {
    font-size: 15px; font-weight: 700; color: #101728;
    letter-spacing: -.01em;
  }
  .bh-filtre {
    font-size: 12px; color: #1f7a5a; font-weight: 600;
    background: #eaf6f0; border: 1px solid #cfe9dd; border-radius: 999px;
    padding: 5px 14px;
  }

  /* ================= les cartes des six dimensions ======================
     Le sélecteur de dimension de « Analyse des résultats ». Chaque carte porte
     le nom de la dimension et une ligne qui dit ce qu'on y trouve — comme sur
     une couverture de dossier. La carte courante prend un aplat plein ; les
     autres restent blanches, avec un filet et une ombre légère qui se
     renforcent au survol.

     Le libellé du bouton contient deux lignes séparées par un saut : Streamlit
     les rend dans un même paragraphe, d'où `white-space: pre-line` — sans lui,
     le saut serait avalé et les deux lignes se colleraient. */
  /* ================= justification du texte courant ====================
     Les paragraphes du contenu sont justifies : sur une colonne bornee a
     1240 px, un bord droit en dents de scie hache la lecture, et le site
     est fait de blocs de prose autant que de chiffres.

     CE QUI EN EST EXCLU, ET POURQUOI : les libelles de bouton (justifier
     deux mots ecarte les lettres), les legendes sous les figures (deux
     lignes justifiees creusent des rivieres blanches), et les cellules de
     tableau (leur alignement porte un sens — les nombres a droite). */
  /* LA JUSTIFICATION EST POSÉE SUR LE CONTENEUR, PAS SUR LES PARAGRAPHES.
     Visée sur `p` et `li`, elle laissait de côté tout ce que les pages
     injectent en HTML — les encadrés, les cartes, les fiches — dont le texte
     vit dans des `div` et des `span`. Posée sur le conteneur, elle descend
     par héritage dans tout ce qui n'a pas d'alignement à lui, et les
     alignements explicites, un nombre calé à droite, un intitulé centré,
     gardent le dessus sans qu'on ait à les rappeler un par un. */
  section[data-testid="stMain"] div[data-testid="stMarkdownContainer"] {
    text-align: justify; text-justify: inter-word; hyphens: auto;
  }
  section[data-testid="stMain"] div[data-testid="stButton"] p,
  section[data-testid="stMain"] div[data-testid="stCaptionContainer"] p,
  section[data-testid="stMain"] table p,
  section[data-testid="stMain"] td p, section[data-testid="stMain"] th p {
    text-align: inherit; hyphens: none;
  }
  section[data-testid="stMain"] div[data-testid="stButton"] p {
    text-align: left;
  }
  .cartes-ancre { display: none; }
  /* UN TRAIT SOUS LES SIX CARTES. Sans lui, la rangée de dimensions et le
     titre de la dimension ouverte se touchaient : on ne voyait pas où
     finissait le choix et où commençait le résultat. Le filet ferme le
     sélecteur, comme le bord bas d'une rangée d'onglets. */
  .cartes-trait {
    height: 1px; background: linear-gradient(90deg, #d7e0ec 0%,
      #e6ecf4 55%, rgba(230,236,244,0) 100%);
    margin: 18px 0 4px;
  }

  /* Les cartes sont visées par leur CLÉ : Streamlit pose une classe
     « st-key-<clé> » sur le conteneur de chaque widget. C'est la seule
     accroche stable — viser « tous les boutons de cette rangée » attraperait
     aussi ceux des pages rendues en dessous. */
  div[class*="st-key-carte_dim"] > div > button {
    display: flex !important; flex-direction: column !important;
    align-items: flex-start !important; justify-content: flex-start !important;
    text-align: left !important; white-space: pre-line !important;
    width: 100% !important; min-height: 104px !important; height: 100% !important;
    padding: 15px 17px !important; border-radius: 14px !important;
    background: #ffffff !important; border: 1px solid #e3eaf3 !important;
    color: #101728 !important;
    font-size: 14.5px !important; font-weight: 700 !important;
    line-height: 1.3 !important; letter-spacing: -.01em !important;
    box-shadow: 0 1px 2px rgba(16,23,40,.05) !important;
    transition: box-shadow .15s ease, transform .15s ease,
                border-color .15s ease !important;
  }
  div[class*="st-key-carte_dim"] > div > button:hover {
    border-color: #c3ded0 !important;
    box-shadow: 0 3px 6px rgba(16,23,40,.07),
                0 14px 30px rgba(16,23,40,.10) !important;
    transform: translateY(-2px) !important;
  }
  /* Le libellé porte le titre en gras markdown et la ligne descriptive en
     texte simple. Streamlit les rend dans un même paragraphe : le titre
     devient un <strong>, ce qui suffit à les habiller séparément.
     (Le premier essai passait par ::first-line — mais ce pseudo-élément vise
     la première ligne VISUELLE, si bien que le début du sous-titre héritait
     du gras dès que le titre tenait sur une seule ligne.) */
  div[class*="st-key-carte_dim"] > div > button p {
    font-size: 11.5px !important; font-weight: 400 !important;
    color: #6b7590 !important; line-height: 1.45 !important;
    text-align: left !important; margin: 0 !important;
  }
  div[class*="st-key-carte_dim"] > div > button p strong {
    display: block; margin-bottom: 7px;
    font-size: 14.5px; font-weight: 700; color: #101728;
    line-height: 1.3; letter-spacing: -.01em;
  }
  div[class*="st-key-carte_dim"] > div > button[kind="primary"] {
    background: #1c6349 !important; border-color: #1c6349 !important;
    box-shadow: 0 3px 8px rgba(28,99,73,.28) !important;
  }
  div[class*="st-key-carte_dim"] > div > button[kind="primary"] p {
    color: rgba(255,255,255,.84) !important;
  }
  div[class*="st-key-carte_dim"] > div > button[kind="primary"] p strong {
    color: #ffffff;
  }
  div[class*="st-key-carte_dim"] > div > button[kind="primary"]:hover {
    background: #237556 !important; border-color: #237556 !important;
  }

  /* --- le panneau des dernières livraisons ---------------------------- */
  .n-item {
    display: flex; gap: 12px; align-items: flex-start;
    padding: 11px 0 3px;
  }
  .n-icone {
    flex: 0 0 34px; width: 34px; height: 34px; border-radius: 9px;
    background: #eaf6f0; color: #1f7a5a; font-size: 14.5px;
    display: flex; align-items: center; justify-content: center;
  }
  .n-corps { flex: 1 1 auto; min-width: 0; }
  .n-titre {
    font-size: 13.5px; font-weight: 700; color: #101728; line-height: 1.35;
  }
  .n-badge {
    display: inline-block; margin-left: 7px; vertical-align: middle;
    background: #eaf6f0; color: #1f7a5a; border: 1px solid #cfe9dd;
    border-radius: 999px; padding: 1px 8px;
    font-size: 10px; font-weight: 700; letter-spacing: .06em;
    text-transform: uppercase;
  }
  .n-texte {
    font-size: 12px; color: #6b7590; line-height: 1.5; margin-top: 3px;
  }

  /* --- sous-onglets : mêmes codes que les tuiles d'entrée, en compact ---
     Les onglets natifs de Streamlit sont un soulignement discret ; à dix
     entrées, on ne voit plus lesquelles sont cliquables. On leur donne la
     forme des tuiles principales — bordure, relief, sélection pleine — pour
     qu'un sous-onglet se lise comme une navigation et non comme un titre. */
  .stTabs [data-baseweb="tab-list"] {
    gap: 8px; flex-wrap: wrap; border-bottom: none; margin-bottom: 6px;
  }
  .stTabs [data-baseweb="tab-list"] button[data-baseweb="tab"] {
    background: var(--carte); border: 1.5px solid var(--bord);
    border-radius: 12px; padding: 9px 16px; height: auto;
    box-shadow: 0 1px 2px rgba(16,23,40,.04);
    transition: transform .16s cubic-bezier(.2,.7,.3,1), box-shadow .16s ease,
                background .16s ease, border-color .16s ease;
  }
  .stTabs [data-baseweb="tab-list"] button[data-baseweb="tab"] p {
    font-family: "Inter", system-ui, sans-serif !important;
    font-size: 14px !important; font-weight: 600 !important;
    color: var(--encre-2) !important; margin: 0;
  }
  .stTabs [data-baseweb="tab-list"] button[data-baseweb="tab"]:hover {
    transform: translateY(-2px); border-color: #b6d8c6; background: #f2f9f5;
    box-shadow: 0 2px 5px rgba(16,23,40,.07), 0 10px 22px rgba(16,23,40,.09);
  }
  .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    background: linear-gradient(135deg, #2b8663 0%, #1c6349 100%);
    border-color: transparent;
    box-shadow: 0 2px 6px rgba(28,99,73,.26), 0 10px 22px rgba(28,99,73,.20);
  }
  .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] p {
    color: #ffffff !important;
  }
  .stTabs [data-baseweb="tab-highlight"],
  .stTabs [data-baseweb="tab-border"] { display: none; }

  /* --- les cartouches de chiffres se soulèvent aussi --- */
  .cartouche { transition: box-shadow .2s ease, transform .2s ease,
                           border-color .2s ease; }
  .cartouche:hover {
    transform: translateY(-3px) !important; border-color: #c3ded0 !important;
    box-shadow: 0 3px 6px rgba(16,23,40,.07), 0 18px 38px rgba(16,23,40,.13) !important;
  }
</style>
""").replace("__ICONE_RESET__", icones.regle_masque(
    'section[data-testid="stSidebar"] div[class*="st-key-f_reset_global"] '
    'div[data-testid="stButton"] > button', "rafraichir", 16, 10)),
    unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# APP.PY PORTE LES INTITULÉS DE SA PROPRE NAVIGATION.
#
# C'est le principe déjà appliqué à `questions_dimension.py`, et je ne l'avais
# pas suivi ici : les six noms de rubrique et les six lignes de carte vivaient
# dans `i18n.py` seul. Un `i18n.py` resté en arrière — ce qui arrive, les
# fichiers étant poussés à la main — et la page s'arrêtait sur « il manque des
# clés », alors que le fichier réellement neuf était app.py.
#
# DEUX TRAITEMENTS, ET LA DIFFÉRENCE COMPTE :
#   · les clés NOUVELLES (les lignes de carte) sont posées en setdefault — un
#     i18n.py à jour reste maître ;
#   · les clés RENOMMÉES (les six rubriques) sont ÉCRASÉES. Un setdefault ne
#     servirait à rien : la clé existe déjà dans l'ancien fichier, avec
#     l'ancien nom, et c'est précisément celui-là qu'il faut remplacer.
#
# `i18n.py` garde les mêmes valeurs et son rôle de catalogue complet.
# ---------------------------------------------------------------------------
TEXTES_NAV = {
    "mode_accueil": {"en": "The territory", "fr": "Le territoire"},
    "mode_methodo": {"en": "Resilience Framework",
                     "fr": "Cadre de résilience"},
    "mode_dimensions": {"en": "Results Analysis",
                        "fr": "Analyse des résultats"},
    "mode_synthese": {"en": "Territorial and Social Profiles",
                      "fr": "Profils territoriaux et sociaux"},
    "mode_actions": {"en": "Intervention Profiles",
                     "fr": "Fiches d'intervention"},
    "mode_donnees": {"en": "Data", "fr": "Données"},
    "dim1_carte": {
        "en": "Housing, water, sanitation, energy, roads, schools and health "
              "facilities",
        "fr": "Logement, eau, assainissement, énergie, routes, écoles et "
              "centres de santé"},
    "dim2_carte": {
        "en": "Civil registration, governance, early warning, disaster "
              "preparedness, participation",
        "fr": "État civil, gouvernance, alerte précoce, préparation aux "
              "catastrophes, participation"},
    "dim3_carte": {
        "en": "Forest cover, rainfall, vegetation, surface temperature and "
              "aridity, by satellite",
        "fr": "Couvert forestier, pluie, végétation, température de surface "
              "et aridité, par satellite"},
    "dim4_carte": {
        "en": "Employment, income, savings and credit, farming, fishing, "
              "food security",
        "fr": "Emploi, revenus, épargne et crédit, agriculture, pêche, "
              "sécurité alimentaire"},
    "dim5_carte": {
        "en": "Social capital, mutual aid, community organisations and their "
              "reach",
        "fr": "Capital social, entraide, organisations communautaires et "
              "leur portée"},
    "dim6_carte": {
        "en": "Education, health, support networks and access to essential "
              "services",
        "fr": "Éducation, santé, réseaux de soutien et accès aux services "
              "essentiels"},
    "mode_boucles": {"en": "Feedback Loops", "fr": "Boucles de rétroaction"},
    "mode_radar": {"en": "Resilience Radar",
                   "fr": "Diagramme radar de résilience"},
    "mode_croisement": {"en": "Cross-tabulation of results",
                        "fr": "Croisement des résultats"},
    "mode_fiche": {"en": "Landscape synthesis sheet",
                   "fr": "Fiche synthèse, paysages"},
    # Les trois onglets de « Profils territoriaux et sociaux », qui ont
    # absorbé le radar et la fiche paysages.
    "syn_o_profils": {"en": "By territory or group",
                      "fr": "Par territoire ou par groupe"},
    "syn_o_paysages": {"en": "Coast against mountain",
                       "fr": "Littoral contre montagne"},
    "syn_o_radar": {"en": "Resilience radar",
                    "fr": "Diagramme radar"},
    # Les deux lectures du graphe causal : l'onde, puis l'analyse.
    "bcl_vue_analyse": {"en": "Loops, levers, total effect",
                        "fr": "Boucles, leviers, effet total"},
    # « NOTE AUX BAILLEURS » EST DEVENU « ENSEIGNEMENTS CLÉS ». Le titre disait
    # à qui la page s'adresse ; celui-ci dit ce qu'on y trouve, ce qui est le
    # seul renseignement utile à quelqu'un qui parcourt un menu. La page
    # elle-même n'a pas bougé d'une ligne.
    "mode_bailleurs": {"en": "Key Lessons", "fr": "Enseignements clés"},
    # LES SIX VUES D'« ANALYSE DES RÉSULTATS », dans l'ordre de la lecture :
    # ce que les gens ont répondu, ce que le référentiel en fait, puis trois
    # façons de chercher les écarts, puis ce qu'on peut y faire.
    #
    # « PAR DIMENSION » N'EST PLUS UN ONGLET. Ce n'est pas une façon de
    # regarder les résultats à côté des autres : c'est la structure du score
    # lui-même. Elle est donc rangée là où le score se lit, dans le second
    # onglet, sous son propre sélecteur.
    #
    # « ENSEIGNEMENTS CLÉS » A ÉTÉ RETIRÉ de la rangée : une note de
    # restitution n'est pas une lecture des résultats, c'est un texte sur
    # eux.
    "ra_o_brut": {"en": "Raw Results", "fr": "Résultats bruts"},
    "ra_o_scores": {"en": "Resilience Scores",
                    "fr": "Scores de résilience"},
    "ra_o_indic": {"en": "By Indicator", "fr": "Par indicateur"},
    "ra_o_paysage": {"en": "By Landscape", "fr": "Par paysage"},
    "ra_o_groupe": {"en": "By Social Group", "fr": "Par groupe social"},
    # L'ONGLET NE PROPOSE PLUS DES SOLUTIONS, IL DÉSIGNE DES CIBLES. Une
    # piste d'action lue avant d'avoir nommé la variable qui décroche est une
    # opinion ; nommer la variable, c'est le point de départ des boucles.
    "ra_o_solutions": {"en": "Most alarming variables",
                       "fr": "Variables les plus alarmantes"},
    "mode_levier": {"en": "If I change one thing",
                    "fr": "Si je change une chose"},
    # LE RAPPORT ET LA NOTE NE FONT PAS LE MÊME MÉTIER. La note tient sur une
    # page et se cite ; le rapport se lit en six chapitres et raconte ce que
    # l'argent a produit comme connaissance. L'un est un extrait, l'autre le
    # récit dont il est extrait.
    "mode_rapport": {"en": "Donor report", "fr": "Rapport donateur"},
    "nav_titre": {"en": "Navigation", "fr": "Navigation"},
    "nav_filtres_rapides": {"en": "Quick filters", "fr": "Filtres rapides"},
    "f_reinit_long": {"en": "Reset the filters",
                      "fr": "Réinitialiser les filtres"},
    "f_groupe_long": {"en": "Respondent group", "fr": "Groupe de répondants"},
    "f_auto": {
        "en": "Results update automatically as you change the filters.",
        "fr": "Les résultats se mettent à jour automatiquement selon vos "
              "filtres."},
}
# Les sept rubriques : app.py est la source, puisqu'il est le seul à s'en servir
# et qu'il est toujours du voyage.
_RENOMMEES = ("mode_accueil", "mode_methodo", "mode_dimensions",
              "mode_synthese", "mode_actions", "mode_donnees",
              "mode_boucles", "mode_croisement", "mode_rapport",
              "mode_levier", "mode_bailleurs", "ra_o_brut", "ra_o_scores",
              "ra_o_indic", "ra_o_paysage", "ra_o_groupe", "ra_o_solutions")
for _c, _v in TEXTES_NAV.items():
    if _c in _RENOMMEES:
        i18n.DICO[_c] = _v
    else:
        i18n.DICO.setdefault(_c, _v)


# ----------------------------------------------------------------------
# Garde-fou : les fichiers sont poussés à la main sur GitHub, un par un. Si le
# dictionnaire de traduction est resté sur une version antérieure, l'application
# ne plante pas — elle affiche le nom des clés manquantes au milieu du texte, ce
# qui est beaucoup plus déroutant qu'une erreur franche. On préfère le dire.
# ----------------------------------------------------------------------
I18N_ATTENDU = "2026-08-18-cadre"

# CE QUI EST VÉRIFIÉ, C'EST LA PRÉSENCE DES CLÉS, PAS LA DATE.
#
# La première version du garde-fou comparait `i18n.VERSION` à la date attendue,
# et arrêtait l'application au moindre écart. C'était trop strict : une mise à
# jour qui ne touche qu'à la mise en page bloquait tout le site alors que rien
# n'était cassé, et le message envoyait renvoyer un fichier de 230 ko sans
# raison. Ce faux positif a coûté plus de temps que la panne qu'il prévient.
#
# Le vrai défaut à attraper est précis : une clé appelée par le code manque du
# dictionnaire, et son NOM s'affiche à la place du texte. C'est donc cela qu'on
# teste — les clés introduites par les mises à jour récentes. Manquantes, on
# arrête franchement ; présentes, on se tait, quelle que soit la date.
I18N_CLES_REQUISES = [
    "a_lieu", "a_titre_court", "a_localisation", "a_histoire",
    "a_h_origine", "a_h_mesure", "a_h_construction", "a_h_portee",
    "dim_sous_titre", "syn_sous_titre", "syn_intro",
    "f_paysage", "f_tous_paysages", "f_resume_paysage",
    "f_resume_section_pay", "f_resume_paysage_groupe", "f_incoherent",
    "s_mode_paysage", "s_note_paysage", "pay_Littoral", "pay_Montagne",
]
# Les textes de l'onglet « questions » ne figurent PAS dans cette liste, bien
# qu'ils soient nouveaux : `questions_dimension.py` les porte lui-même et les
# verse dans le dictionnaire à l'import, avant que ce contrôle ne s'exécute.
# C'est le principe qu'il faut suivre pour toute fonction nouvelle — un module
# qui apporte une fonction apporte ses textes — de sorte qu'un `i18n.py` resté
# en arrière ne puisse plus bloquer une page qui, elle, est complète.
_manquantes = [c for c in I18N_CLES_REQUISES if c not in getattr(i18n, "DICO", {})]
if _manquantes:
    st.error(
        f"**i18n.py n'est pas à jour** — il manque "
        f"{len(_manquantes)} clé(s) de traduction que le reste de "
        f"l'application appelle : `" + "`, `".join(_manquantes[:6]) + "`"
        + ("…" if len(_manquantes) > 6 else "") + ".\n\n"
        f"Version attendue `{I18N_ATTENDU}`, trouvée "
        f"`{getattr(i18n, 'VERSION', 'aucune')}`. Sans ces clés, les textes "
        f"s'affichent sous forme de noms (`mode_ocb`, `o_intro`…). Renvoyer "
        f"sur GitHub le `i18n.py` livré avec cette mise à jour, à la racine du "
        f"dépôt, corrige l'affichage.\n\n"
        f"*i18n.py is missing translation keys — re-upload the version "
        f"delivered with this update to the repository root.*")
    # On ARRÊTE ici. L'application continuait autrefois de se dessiner avec des
    # noms de clés en guise de textes, et le message rouge se perdait au-dessus
    # d'une page qui semblait fonctionner — au point qu'on a pris plusieurs
    # fois l'affichage cassé pour un défaut de mise en page. Une page vide sous
    # un message franc est plus honnête qu'une page à moitié juste.
    st.stop()

st.markdown(map_render.styles_bulle(), unsafe_allow_html=True)

# ---- choix de la langue, avant tout le reste ---------------------------
# Le menu est l'unique source de vérité : on recopie simplement son état dans
# `lang`, que toutes les pages lisent. Pas de rerun forcé — Streamlit relance
# déjà le script quand le menu change, et le reste de la page est construit
# après cette ligne.
# La colonne se construit en trois conteneurs réservés d'avance : le choix de
# la langue doit être LU avant tout appel à T(), mais AFFICHÉ en bas de la
# barre. Les conteneurs gardent leur place dans la page pendant qu'on les
# remplit dans un autre ordre — sans eux, la langue s'afficherait au-dessus du
# logo, ce qui n'a aucun sens dans un menu.
# LA LANGUE EST MONTÉE EN TÊTE DE LA COLONNE, AU-DESSUS DE LA MARQUE.
# Elle occupait le ruban blanc du haut, qui n'existait que pour elle et pour
# le logo ; les deux étant partis — la langue ici, le logo sur la photo — le
# ruban a disparu et chaque page commence par son titre.
# LA COLONNE DE GAUCHE A DISPARU, ET AVEC ELLE LA MOITIÉ DE SON CONTENU.
# Elle portait quatre choses : la langue, la marque, la navigation et le
# rappel des filtres. Les deux premières sont montées dans le bandeau, où
# elles identifient le site au lieu de border le contenu. La navigation
# devient un menu déroulant sous le bandeau : douze entrées empilées le long
# d'une page pleine largeur, c'était une colonne de trois cents pixels
# occupée à répéter ce qu'un seul champ suffit à dire. Les filtres restent
# à côté du menu, puisque c'est la seule commande qu'on cherche depuis
# n'importe quelle page.
# L'ORDRE DE CRÉATION EST L'ORDRE D'AFFICHAGE. Le bandeau doit être
# réservé en premier : créé plus bas, il se dessinait sous le menu.
# LA NAVIGATION EST UNE BARRE HORIZONTALE, ET ELLE OUVRE LA PAGE.
# Elle occupait une colonne de gauche : un sixième de la largeur, sur toute la
# hauteur, pour quatorze mots. Le contenu — cartes, tableaux, graphiques —
# était comprimé d'autant, alors que c'est lui qu'on vient voir. En haut, sur
# une seule ligne qui se replie si besoin, elle rend l'écran entier à la page.
_zone_nav = st.container(key="zone_nav")
_ruban = st.container(key="zone_ruban")
_zone_barre = st.container()

# LA LANGUE EST LUE ICI, AVANT TOUT APPEL À T(), ET CHANGÉE DANS LE BANDEAU.
# Le menu déroulant de la colonne de gauche a disparu : deux mots côte à côte
# se lisent et se cliquent d'un seul geste, là où un menu demandait d'ouvrir,
# viser, choisir. Le bouton n'écrit que dans l'état de session ; Streamlit
# relance le script derrière, et la langue est déjà bonne quand la première
# ligne de texte se dessine.
st.session_state.setdefault("choix_langue", i18n.DEFAUT)
i18n.set_lang(st.session_state["choix_langue"])


def _changer_langue(code):
    st.session_state["choix_langue"] = code

# ---- bandeau : logo PNUE + les deux entrées du tableau de bord ----------
# Le mode est stocké sous un code stable, pas sous son libellé : sinon un
# changement de langue laisserait dans la session une valeur qui ne correspond
# plus à aucun mode.
# Dix entrées : les six dimensions du cadre APRI, puis la méthode, les
# données, les fiches actions et la synthèse. La septième dimension du cadre —
# culturelle, identitaire et psychologique — n'a aucun indicateur calculé et
# n'a donc pas d'onglet ; elle reste listée dans la méthodologie, pour qu'une
# absence ne passe pas pour une inexistence.
MODE_ACCUEIL = "accueil"
MODES_DIM = ["dim1", "dim2", "dim3", "dim4", "dim5", "dim6"]
MODE_METHODO, MODE_DONNEES = "methodologie", "donnees"
MODE_ACTIONS = "actions"
MODE_SYNTHESE = "synthese"
MODE_BOUCLES = "boucles"
MODE_CROISEMENT = "croisement"
MODE_BAILLEURS = "bailleurs"
MODE_RAPPORT = "rapport"
MODE_LEVIER = "levier"
# LA PAGE D'ACCUEIL, ET C'EST ELLE QUI OUVRE LE SITE. On arrivait jusqu'ici
# sur le cadre méthodologique : avant d'apprendre quoi que ce soit du
# territoire, on apprenait comment on le mesure. C'est l'ordre d'un rapport,
# pas celui d'un tableau de bord.
MODE_PORTAIL = "portail"
# LE TEMPS, ENFIN MONTRÉ COMME DU TEMPS. Trois jeux satellitaires sont des
# séries — la forêt depuis 2000, la pluie depuis 1981, la température depuis
# 2001 — et le site les lisait comme des instantanés.
MODE_TRAJECTOIRES = "trajectoires"
LIBELLE_MODE = {m: T(m) for m in MODES_DIM}
LIBELLE_MODE.update({MODE_ACCUEIL: T("mode_accueil"),
                     "dimensions": T("mode_dimensions"),
                     MODE_METHODO: T("mode_methodo"),
                     MODE_DONNEES: T("mode_donnees"),
                     MODE_ACTIONS: T("mode_actions"),
                     MODE_BOUCLES: T("mode_boucles"),
                     MODE_SYNTHESE: T("mode_synthese"),
                     MODE_CROISEMENT: T("mode_croisement"),
                     MODE_BAILLEURS: T("mode_bailleurs"),
                     MODE_RAPPORT: T("mode_rapport"),
                     MODE_LEVIER: T("mode_levier"),
                     MODE_PORTAIL: T("mode_portail"),
                     MODE_TRAJECTOIRES: T("mode_trajectoires")})

# L'état de navigation doit exister AVANT la barre du haut, qui affiche le nom
# de la page courante. L'initialiser plus bas laissait la barre lire une clé
# absente — et Streamlit lève alors une erreur qui masque toute la page.
if "app_mode" not in st.session_state:
    st.session_state["app_mode"] = MODE_PORTAIL


def _bascule(mode):
    st.session_state["app_mode"] = mode


# L'identité APRI vit maintenant dans la barre latérale : la répéter en haut
# du contenu volerait un tiers d'écran avant le premier chiffre. Il reste ici
# une ligne institutionnelle — le commanditaire et le titre long, qu'une
# capture d'écran doit porter avec elle — et le bandeau, réduit de moitié pour
# rester un décor.
# Un SEUL bloc HTML : Streamlit isole chaque appel à st.markdown dans son
# propre conteneur, si bien qu'une balise ouverte dans l'un et fermée dans le
# suivant ne s'emboîte jamais — le style se perd sans qu'aucune erreur ne le
# signale.
# La barre du haut : à gauche le commanditaire et la page courante, à droite ce
# sur quoi porte l'affichage — un chiffre lu sans savoir qu'un filtre est posé
# est un chiffre mal lu.
# Plus aucun logo ici. Les deux marques sont réunies dans la colonne de gauche —
# APRI en tête, le PNUE en pied — et le contenu des pages n'en porte aucun : un
# logo répété à chaque en-tête mange la place du titre sans rien apprendre à
# personne, puisqu'il est déjà à l'écran en permanence.

# Les deux entrées sont mises au même niveau, en haut de page : ce sont deux
# lectures différentes de la même enquête, pas un mode principal et une option.
# Deux grands pavés cliquables plutôt qu'un bouton radio : l'entrée dans le
# tableau de bord doit se voir de loin.


# Trois entrées d'analyse sur la première rangée, les deux entrées documentaires
# sur la seconde : cinq pavés d'affilée deviendraient trop étroits pour que
# leur intitulé reste lisible.
# La navigation vit dans la barre latérale, groupée : l'entrée générale, les
# six dimensions du cadre, puis ce qui sert à agir et à vérifier. Onze entrées
# en pavés sur la page occupaient un écran entier avant le premier chiffre ;
# en colonne fixe, elles tiennent sans rien pousser vers le bas, et l'onglet
# courant reste visible où qu'on soit dans la page.
# Six entrées seulement dans la colonne. Les six dimensions n'y sont PAS :
# elles forment une famille homogène qu'on parcourt en comparant, et une
# rangée d'onglets se parcourt du regard alors qu'une liste verticale se lit
# une ligne après l'autre. Elles vivent donc sous l'entrée « Les six
# dimensions », en onglets, comme avant la refonte.
MODE_DIMENSIONS = "dimensions"
# L'ORDRE EST CELUI DE LA LECTURE, pas celui de la fabrication : on découvre le
# territoire (vue d'ensemble), on apprend ce qu'on mesure et comment (cadre de
# résilience), on lit les résultats par dimension, on compare les territoires
# et les groupes, on passe à l'action, et les données brutes ferment la marche
# pour qui veut refaire les calculs.
# L'ORDRE A CHANGÉ : le cadre de résilience ouvre la marche, le territoire
# vient juste après. On dit d'abord ce qu'on mesure, puis où on l'a mesuré ;
# les résultats suivent. L'accueil, devenu « Le territoire », n'a plus à porter
# le récit de la méthode, qui est passé dans le cadre.
_NAV = [
    (MODE_PORTAIL, "maison"),
    # LE TERRITOIRE PASSE DEVANT LE CADRE. On dit d'abord où l'on est, ensuite
    # comment on y mesure : c'est l'ordre des quatre cartes de l'accueil, et
    # le menu doit dire la même chose qu'elles.
    (MODE_ACCUEIL, "epingle"),
    (MODE_METHODO, "bouclier"),
    (MODE_DIMENSIONS, "barres"),
    # LES TRAJECTOIRES NE SONT PLUS UNE ENTREE : elles ont rejoint l'onglet
    # « Résilience environnementale » du cadre, dont elles disent la version
    # dans le temps. Une entrée de moins, et la barre tient sur une ligne.
    # « SI JE CHANGE UNE CHOSE » EST DEVENU UNE VUE DES BOUCLES. Les deux
    # lisent le même graphe causal : les boucles montrent que le système
    # propage, l'outil répond à la question qui vient juste après — ce
    # chiffre-là, d'où sort-il ? Deux entrées de menu pour un seul modèle
    # obligeaient à savoir laquelle des deux portes mène à quoi.
    (MODE_BOUCLES, "boucle"),
    # CROISEMENT, PROFILS ET ENSEIGNEMENTS SONT PASSÉS SOUS « ANALYSE DES
    # RÉSULTATS ». Les quatre lisent la même enquête et répondent à la même
    # question — que disent les résultats ? — par quatre découpages : la
    # dimension, le croisement de deux variables, le territoire ou le groupe,
    # et ce qu'il faut en retenir. Quatre entrées de menu pour un seul sujet,
    # c'était au lecteur de deviner qu'elles allaient ensemble.
    (MODE_ACTIONS, "fiche"),
    # LA NOTE AUX BAILLEURS VIENT APRÈS LES FICHES, ET AVANT LES DONNÉES.
    # Elle est la sortie de tout ce qui précède : elle ne se comprend qu'après
    # les fiches, dont elle reprend les chiffres, et elle doit rester au-dessus
    # des téléchargements, qui ferment toujours la marche.
    # LE RAPPORT PRÉCÈDE LA NOTE, PARCE QU'IL LA FONDE. Six chapitres qui
    # partent des volumes de terrain et finissent par ce qui reste après le
    # projet ; la note qui suit en est la page arrachée.
    (MODE_RAPPORT, "radar"),
    (MODE_DONNEES, "telecharger"),
]

# PLUS D'ICONE DEVANT LES ENTREES DE MENU.
# Chaque ligne en portait une, posee en `::before` par la feuille de style.
# Onze petits pictogrammes alignes en colonne ne disaient rien que le libelle
# ne disait deja : « Donnees » a cote d'une fleche de telechargement, « Le
# territoire » a cote d'une epingle. Ils meublaient, ils dataient, et ils
# ajoutaient onze regles CSS a entretenir. La colonne se lit maintenant comme
# une liste de titres, ce qu'elle est.
#
# Le second element du couple, dans `_NAV`, n'est plus utilise ici. Il reste
# en place : c'est la source unique dont d'autres vues se servent, et la
# vider par acquit de conscience casserait plus qu'elle ne nettoierait.
_CSS_ICONES_NAV = ""


def _entree_nav(mode, icone):
    actif = st.session_state["app_mode"] == mode
    st.button(LIBELLE_MODE[mode], key=f"nav_{mode}",
              on_click=_bascule, args=(mode,),
              type="primary" if actif else "secondary",
              use_container_width=True)


# ---------------------------------------------------------------- le ruban
# La m\u00eame navigation qu'\u00e0 gauche, en onglets horizontaux dans le ruban vert.
# DEUX CHEMINS VERS LES M\u00caMES PAGES, ET C'EST VOULU : la colonne se lit ligne
# \u00e0 ligne quand on cherche, le ruban se parcourt du regard quand on sait d\u00e9j\u00e0
# o\u00f9 l'on va. Ce qu'il ne faut surtout pas, c'est que les deux listes
# divergent \u2014 d'o\u00f9 la source unique `_NAV`, dont les deux se servent.
@st.cache_data(show_spinner=False)
def _bandeau_b64():
    """L'illustration du bandeau, encodée une fois pour toutes.

    Le fichier fait deux cent quarante kilo-octets : l'encoder à chaque
    réexécution de la page coûterait plus cher que de le garder en mémoire.
    """
    import base64 as _b64
    chemin = os.path.join(APP_DIR, "data", "bandeau_apri.jpg")
    if not os.path.exists(chemin):
        return None
    with open(chemin, "rb") as f:
        return _b64.b64encode(f.read()).decode()


def _rendre_ruban():
    """L'illustration, la marque APRI, le logo du PNUE — sur l'accueil seul.

    LE BANDEAU EST UNE PAGE DE COUVERTURE, PAS UN EN-TÊTE. Répété sur les
    quatorze pages, il coûtait cent cinquante pixels à chaque fois — la
    hauteur d'un tableau, ou d'une carte — pour redire une image que le
    lecteur a déjà vue en arrivant. Sur l'accueil il annonce le site ; ailleurs
    il ne fait que retarder le premier chiffre.

    CE QUI IDENTIFIE LE SITE EST DONC DANS LA BARRE, qui est partout : les
    rubriques, la rubrique courante, la langue. La marque et le logo du PNUE
    restent sur l'accueil, où l'on arrive et d'où l'on repart.

    LE LOGO DU PNUE EST POSÉ SUR UN CARTOUCHE BLANC, ET CE N'EST PAS QU'UNE
    QUESTION DE CONTRASTE. L'illustration fournie porte déjà un logo incrusté
    au même endroit. Le reconstruire à coups de ciel synthétique abîmait les
    arbres alentour pour un gain nul : le cartouche recouvre l'ancien et pose
    le vrai, net et à la bonne charte.
    """
    if st.session_state.get("app_mode") != MODE_PORTAIL:
        return
    with _ruban:
        img = _bandeau_b64()
        if not img:
            return
        st.markdown(
            f'<div class="bandeau-haut bandeau-enveloppe">'
            f'<img class="bandeau-fond" '
            f'src="data:image/jpeg;base64,{img}">'
            f'<div class="bandeau-marque">'
            f'<img class="bm-embleme" alt="APRI" '
            f'src="data:image/png;base64,{assets.EMBLEME_APRI}">'
            f'<div class="bm-texte">'
            f'<div class="bm-nom">APRI</div>'
            f'<div class="bm-filet"></div>'
            f'<div class="bm-base">{T("a_titre_court")}</div>'
            f'<div class="bm-lieu">{T("a_lieu")}</div>'
            f'</div></div>'
            f'<img class="bandeau-logo" alt="UNEP" '
            f'src="data:image/png;base64,{assets.LOGO_UNEP_BLANC}">'
            f'</div>', unsafe_allow_html=True)


with _zone_nav:
    # LES QUATORZE ENTRÉES SONT DES ONGLETS, PAS DES LIGNES DE LISTE.
    # La feuille de style met le bloc vertical de Streamlit en `flex` : les
    # boutons se rangent alors côte à côte, prennent la largeur de leur mot et
    # passent à la ligne suivante quand la fenêtre se rétrécit. Aucun n'est
    # tronqué, aucun n'est caché derrière un déroulant.
    st.markdown(_CSS_ICONES_NAV, unsafe_allow_html=True)
    for _mode, _icone in _NAV:
        _entree_nav(_mode, _icone)

    # LES DEUX LANGUES FERMENT LA BARRE, À DROITE.
    # Elles ont été un moment posées sur l'illustration, en blanc ; celle-ci
    # ne paraît plus que sur l'accueil, et un réglage du site ne peut pas
    # n'exister que sur une page. Dans la barre, qui est partout, elles sont
    # un élément de plus de la même rangée, poussé à droite par une marge
    # automatique : rien à recalculer si la barre se replie.
    #
    # DEUX CODES, ET NON DEUX NOMS. Le nom d'une langue lu dans cette langue
    # n'apprend rien à qui la cherche ; les deux codes ISO sont la convention
    # de tous les sites bilingues. `i18n.LANGUES` garde les noms complets, qui
    # restent le libellé juste partout ailleurs.
    with st.container(key="zone_langue"):
        _cl = st.columns(2)
        # L'ORDRE SUIT LA LANGUE PAR DÉFAUT : la langue servie est en tête.
        _ordre = ("en", "fr") if i18n.DEFAUT == "en" else ("fr", "en")
        for _col, _code in zip(_cl, _ordre):
            with _col:
                st.button(_code.upper(), key=f"lang_{_code}",
                          on_click=_changer_langue, args=(_code,),
                          type=("primary"
                                if st.session_state["choix_langue"] == _code
                                else "secondary"))


# LA PAGE OCCUPE TOUTE LA LARGEUR. Il n'y a plus de colonne de menu à sa
# gauche : le conteneur est ouvert ici, avant l'aiguillage, pour que chaque
# page se dessine dedans.
_c_contenu = st.container()

# Le ruban est peint maintenant, dans le conteneur réservé plus haut : il a
# besoin de la langue choisie et du résumé des filtres, tous deux fixés par
# la colonne de gauche qu'on vient de rendre.
_rendre_ruban()

app_mode = st.session_state["app_mode"]

# Les six onglets de dimension passent tous par le même module ; deux d'entre
# eux prolongent leur page avec un détail qui existait déjà, plutôt que d'en
# dupliquer la logique — l'environnement avec ses onze indicateurs
# satellitaires, le social avec les fiches d'organisations de base.
# TOUT L'AIGUILLAGE SE DESSINE DANS LA COLONNE DE DROITE.
# Chaque page reste écrite comme avant ; c'est le contexte qui change, en un
# seul endroit, plutôt que quarante modules qui devraient savoir où ils sont.
with _c_contenu:
    if app_mode == MODE_PORTAIL:
        # Quatre écrans : où, ce qu'on a mesuré, ce qu'on a trouvé, quoi faire.
        accueil_apri.render()

    if app_mode == MODE_ACCUEIL:
        territoire_page.render()

    if app_mode == MODE_DIMENSIONS:
        # QUATRE VUES SOUS UNE SEULE ENTRÉE, ET C'EST LA MÊME QUESTION.
        #
        #   · par dimension — les sept familles d'indicateurs, une à la fois ;
        #   · par croisement — deux variables l'une contre l'autre ;
        #   · par territoire ou par groupe — les profils comparés ;
        #   · les enseignements — ce qu'il faut retenir de tout cela.
        #
        # Elles étaient quatre entrées de menu voisines, ce qui laissait au
        # lecteur le soin de deviner qu'elles répondent à la même question.
        # Une seule entrée, quatre vues : la porte est unique, le découpage
        # se choisit après. Comme pour les boucles, un sélecteur plutôt que
        # `st.tabs` — seule la vue regardée est calculée.
        # LE SÉLECTEUR RETIENT UN CODE, PAS UN LIBELLÉ. Une valeur de session
        # égale au texte affiché change de langue avec lui : il faut alors une
        # clé par langue, et la vue choisie se perd au premier basculement.
        # `format_func` sépare ce qu'on stocke de ce qu'on montre.
        # LA BARRE PREND LE FORMAT DU CADRE DE RÉSILIENCE : numéro en gras,
        # titre à côté, filet sous la rangée et soulignement vert sur l'onglet
        # ouvert. Quatre pastilles rondes se lisaient comme un formulaire à
        # cocher ; ce sont des onglets, ils en ont la forme.
        # SIX ONGLETS, ET L'ORDRE EST CELUI DE LA LECTURE.
        #
        #   01 Raw Results      — ce que les ménages répondent, sans calcul ;
        #   02 Resilience Scores— ce que le référentiel en fait, dimension
        #                         par dimension ;
        #   03 By Indicator     — un indicateur, ses écarts sur le territoire ;
        #   04 By Landscape     — un paysage contre l'autre ;
        #   05 By Social Group  — un groupe contre tous les autres ;
        #   06 Solutions        — ce qu'on peut faire de tout cela.
        #
        # Les trois écrans du milieu répondent à la même question sous trois
        # angles : où sont les écarts, et quels indicateurs les font. Ils
        # partagent donc un seul moteur de calcul.
        _RA = {"brut": T("ra_o_brut"),
               "scores": T("ra_o_scores"),
               "indic": T("ra_o_indic"),
               "paysage": T("ra_o_paysage"),
               "groupe": T("ra_o_groupe"),
               "solutions": T("ra_o_solutions")}
        _CODES_RA = list(_RA)
        with st.container(key="ra_nav"):
            _ra = st.radio(
                "ra", _CODES_RA, horizontal=True,
                label_visibility="collapsed", key="ra_vue",
                format_func=lambda c: (f"**{_CODES_RA.index(c) + 1:02d}**"
                                       f"&nbsp; {_RA[c]}"))

        # LE CATALOGUE EST CHARGÉ UNE FOIS POUR LES CINQ PREMIERS ONGLETS.
        # C'est le même fichier de réponses individuelles ; le charger dans
        # chaque module en ferait cinq copies en mémoire.
        _cat = croisement_resultats._catalogue() \
            if _ra in ("brut", "scores", "indic", "paysage", "groupe",
                       "solutions") \
            else None

        if _ra == "brut":
            # LES RÉSULTATS BRUTS SONT CE QUE LES GENS ONT RÉPONDU, et rien
            # d'autre : aucun barème, aucune pondération. Une question, une
            # réponse, la part qui la donne — ventilée, filtrée, et portée sur
            # la carte quand la ventilation est géographique.
            explorateur.render(_cat, mode="brut")

        elif _ra == "scores":
            # LES SCORES, DANS LES DEUX SENS DE LECTURE : d'abord comparés
            # entre territoires, paysages et groupes ; ensuite dépliés
            # dimension par dimension, avec le détail de leurs indicateurs.
            explorateur.render(_cat, mode="score")
            st.markdown('<div style="height:30px"></div>',
                        unsafe_allow_html=True)
            _COMPLEMENT = {
                "dim3": lambda: environnement_page.render(entete=False),
                "dim5": lambda: ocb_page.render(entete=False),
            }
            st.session_state.setdefault("dim_active", MODES_DIM[0])
            if st.session_state["dim_active"] not in MODES_DIM:
                st.session_state["dim_active"] = MODES_DIM[0]
            st.selectbox(T("d_choix_dim"), MODES_DIM, key="dim_active",
                         format_func=lambda m: T(m))
            _m = st.session_state["dim_active"]
            dimension_page.render(_m, complement=_COMPLEMENT.get(_m))

        elif _ra == "indic":
            analyse_ecarts.render_indicateur(_cat)

        elif _ra == "paysage":
            # LA FICHE PAYSAGE EXISTAIT DÉJÀ et se lit d'une traite ; l'écran
            # d'écarts la prolonge par ce qu'elle ne disait pas — quels
            # indicateurs, précisément, séparent un paysage de l'autre.
            analyse_ecarts.render_paysage(_cat)
            st.markdown('<div style="height:30px"></div>',
                        unsafe_allow_html=True)
            fiche_paysages.render(entete=False)

        elif _ra == "groupe":
            analyse_ecarts.render_groupe(_cat)
            st.markdown('<div style="height:30px"></div>',
                        unsafe_allow_html=True)
            synthese_page.render(entete=False)

        else:
            # LES VARIABLES ALARMANTES SE LISENT APRÈS LES ÉCARTS, et c'est
            # la seule place qui leur convienne : elles sont le résultat des
            # cinq écrans précédents, et l'entrée des boucles causales.
            analyse_ecarts.render_alarmes(_cat)
            st.markdown('<div style="height:30px"></div>',
                        unsafe_allow_html=True)
            pistes_page.render()

    if app_mode == MODE_METHODO:
        # « Cadre de résilience » a remplacé la page de méthodologie : des schémas
        # à la place de sept blocs de texte. Le document complet n'est pas perdu —
        # il est rendu dans le volet replié du bas. Une fonction qui marchait ne se
        # supprime pas au motif qu'on a réorganisé la façade ; on la range.
        #
        # L'OUTIL DE « CROISEMENT LIBRE » A ÉTÉ RETIRÉ D'ICI, ET SUPPRIMÉ DU DÉPÔT.
        # Il empilait des conditions sur les mêmes 483 questions, avec la même
        # carte par section et la même ventilation par sexe, catégorie et âge que
        # « Croisement des résultats » — qui fait tout cela et davantage : profil
        # de résilience du sous-groupe, comparaison de deux groupes, effectif
        # attendu sous indépendance. Deux outils qui font la même chose divergent
        # tôt ou tard, et le lecteur ne sait jamais lequel fait autorité.
        def _document_methodologique():
            methodologie_page.render()

        cadre_page.render(doc_complet=_document_methodologique)

    if app_mode == MODE_BOUCLES:
        # DEUX LECTURES DU MÊME MODÈLE, ET UN SEUL RENDU À LA FOIS.
        #
        #   · l'onde — où passe le choc, vague après vague, et quand il revient
        #     sur ses pas ;
        #   · l'analyse — l'effet total une fois tout distribué, les boucles
        #     énumérées, les leviers classés.
        #
        # `st.tabs` rendrait les deux à chaque affichage : l'énumération des
        # trente-huit boucles et l'animation seraient calculées ensemble, pour
        # n'en montrer qu'une. Un sélecteur ne rend que ce qu'on regarde.
        st.markdown(
            f'<h2 style="font-size:21.5px;font-weight:700;color:#101728;'
            f'letter-spacing:-.02em;margin:2px 0 0">{T("mode_boucles")}</h2>',
            unsafe_allow_html=True)
        # QUATRE VUES, ET LA QUATRIÈME EST « SI JE CHANGE UNE CHOSE ».
        # Elle lit le même graphe causal que les trois autres : c'est la
        # question qu'on se pose juste après les avoir vues — ce chiffre-là,
        # d'où sort-il, et que devient-il si je le pousse ?
        # Ici aussi la session retient un code : une clé par langue laissait
        # la vue choisie se perdre au basculement.
        _VUES = {"onde": T("oc_titre"), "systeme": T("sy_titre"),
                 "analyse": T("bcl_vue_analyse"), "levier": T("mode_levier")}
        _vue = st.radio("vue", list(_VUES), horizontal=True,
                        label_visibility="collapsed", key="bcl_vue",
                        format_func=lambda c: _VUES[c])
        if _vue == "onde":
            ondes_choc.render(entete=False)
        elif _vue == "systeme":
            systeme_page.render(entete=False)
        elif _vue == "analyse":
            boucles_page.render(entete=False)
        else:
            # Aucun filtre : le modèle causal est le même pour tout le
            # territoire, et un filtre posé ailleurs ne changerait rien à ce
            # qu'il propage.
            si_je_change.render(entete=False)

    if app_mode == MODE_ACTIONS:
        # Les fiches descendent des leviers calculés par l'analyse des boucles.
        # Les anciennes pistes de travail, écrites avant cette analyse, ont été
        # retirées : elles ne commandaient plus rien et brouillaient la page.
        interventions_page.render()

    if app_mode == MODE_RAPPORT:
        # Aucun filtre non plus, et pour la même raison que la note : un rapport
        # se cite. Les chiffres y sont ceux de l'enquête entière, et chacun porte
        # son registre — donnée observée, interprétation, implication.
        rapport_donateur.render()

    if app_mode == MODE_DONNEES:
        telechargements_page.render()
        # Les livraisons récentes ont suivi les jeux de données : c'est ici
        # qu'on vient voir ce qui est disponible, et donc ce qui vient
        # d'arriver.
        actualites.rendre(_bascule)

