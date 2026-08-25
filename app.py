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
import croisement_resultats
import dimension_page
import environnement_page
import fiche_paysages
import filtres
import icones
import interventions_page
import i18n
import map_render
import methodologie_page
import note_bailleurs
import ondes_choc
import ocb_page
import radar_accueil
import rapport_donateur
import resilience_page
import saillants_page
import systeme_page
import synthese_page
import telechargements_page
import territoire_page
import trajectoires
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
  html { font-size: 14.5px; }
  :root { --z: .88; --dz: 1.1364; }
  section.stMain, div[data-testid="stMain"] { zoom: var(--z); }
  .block-container { max-width: 1240px; padding-top: 0; padding-bottom: 2.4rem; }
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
  section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
    display: flex !important; align-items: center !important;
    justify-content: flex-start !important;
    width: 100% !important; min-height: 46px !important; height: auto !important;
    padding: 11px 15px !important; border-radius: 10px !important;
    border: none !important;
    background: transparent !important; box-shadow: none !important;
    transition: background .15s ease, color .15s ease;
    margin-bottom: 2px;
  }
  section[data-testid="stSidebar"] div[data-testid="stButton"] > button > div,
  section[data-testid="stSidebar"] div[data-testid="stButton"] > button
    div[data-testid="stMarkdownContainer"] {
    width: 100% !important; text-align: left !important;
    display: block !important;
  }
  section[data-testid="stSidebar"] div[data-testid="stButton"] > button p {
    font-family: "Inter", system-ui, sans-serif !important;
    font-size: 14.5px !important; font-weight: 500 !important;
    line-height: 1.35 !important;
    color: var(--encre-2) !important;
    text-align: left !important; width: 100%; margin: 0 !important;
  }
  section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
    background: #f1f6f4 !important;
    transform: none !important;
  }
  section[data-testid="stSidebar"]
    div[data-testid="stButton"] > button:hover p {
    color: var(--encre) !important;
  }
  /* L'ENTRÉE ACTIVE : le même fond très clair que le survol, en un peu plus
     appuyé, et le libellé en vert gras. Une pastille pleine reviendrait à
     remettre dans la colonne la tache de couleur qu'on vient d'en retirer ;
     ici c'est la graisse du texte qui dit où l'on se trouve, et la teinte ne
     fait que la confirmer. */
  section[data-testid="stSidebar"]
    div[data-testid="stButton"] > button[kind="primary"] {
    background: #e9f2ee !important;
    border: none !important; box-shadow: none !important;
  }
  section[data-testid="stSidebar"]
    div[data-testid="stButton"] > button[kind="primary"] p {
    color: var(--accent) !important; font-weight: 700 !important;
  }
  section[data-testid="stSidebar"]
    div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #e2ece7 !important;
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
  .bandeau-haut {
    /* LES REPÈRES EN `vw` NE SUIVENT PAS LE ZOOM. Un `100vw` écrit dans une
       zone mise à l'échelle vaut toujours la largeur réelle de la fenêtre,
       si bien que la photo se retrouvait rétrécie d'autant et décollée du
       bord droit. On divise donc chaque terme en `vw` par le facteur, ce que
       fait `--dz`, son inverse. Les termes en pourcentage, eux, se réfèrent
       au conteneur déjà mis à l'échelle et n'ont rien à corriger. */
    width: calc((100vw - 310px) * var(--dz)) !important;
    max-width: calc((100vw - 310px) * var(--dz)) !important;
    margin-left: calc(50% - (100vw - 310px) * var(--dz) / 2);
    /* LES 32 PIXELS REPRIS. Chaque feuille de style injectée par st.markdown
       laisse un bloc vide en tête de page, et la gouttière de Streamlit
       s'ajoute par-dessus : la photo commençait 32 px sous le haut de la
       fenêtre, avec une bande blanche au-dessus d'elle. */
    margin-top: calc(-32px * var(--dz)); margin-bottom: 0;
  }
  /* L'enveloppe existe pour que le logo puisse se poser DANS la photo :
     un élément en position absolue se place par rapport au premier parent
     positionné, et l'image seule n'en est pas un. */
  .bandeau-enveloppe { position: relative; display: block; line-height: 0; }
  /* Le voile : sombre à gauche, éteint aux deux tiers. Il ne couvre pas
     l'image, il lui donne un coin lisible. */
  .bandeau-voile {
    position: absolute; top: 0; left: 0; bottom: 0;
    width: min(58%, 640px); pointer-events: none;
    background: linear-gradient(100deg, rgba(10,24,18,.66) 0%,
                rgba(10,24,18,.42) 38%, rgba(10,24,18,0) 100%);
  }
  .bandeau-logo {
    position: absolute; top: 24px; left: 34px; height: 62px;
    opacity: .95; filter: drop-shadow(0 1px 8px rgba(0,0,0,.35));
  }

  /* --- les deux langues, en tête de la colonne -------------------------
     DEUX PASTILLES, ET NON DEUX MOTS POSÉS. Écrites en simple texte, elles ne
     se donnaient pas pour cliquables, et la langue courante ne se distinguait
     que par une nuance de gris qu'il fallait chercher. Chacune porte
     maintenant son contour, la paire est centrée, et la langue en cours est
     sur fond vert : on voit d'un coup d'œil ce qu'on lit et ce qu'on peut
     demander à la place.

     Elles empruntent la classe `st-key-lang_*` de leur bouton : c'est le seul
     point d'accroche stable que Streamlit offre sur un widget précis. Tout ce
     que la colonne impose aux boutons est défait ici, explicitement, en
     !important. */
  section[data-testid="stSidebar"] div[class*="st-key-lang_"]
  div[data-testid="stButton"] > button,
  section[data-testid="stSidebar"] div[class*="st-key-lang_"]
  div[data-testid="stButton"] > button[kind="primary"] {
    background: #ffffff !important;
    border: 1px solid var(--bord) !important;
    border-radius: 999px !important;
    box-shadow: none !important; padding: 6px 4px !important;
    min-height: 0 !important; height: auto !important; width: 100% !important;
    justify-content: center !important; transform: none !important;
    transition: background .15s ease, border-color .15s ease;
  }
  section[data-testid="stSidebar"] div[class*="st-key-lang_"]
  div[data-testid="stButton"] > button p {
    font-size: 11.5px !important; font-weight: 700 !important;
    letter-spacing: .09em !important; text-transform: uppercase;
    color: var(--encre-3) !important; text-align: center !important;
    transition: color .15s ease;
  }
  section[data-testid="stSidebar"] div[class*="st-key-lang_"]
  div[data-testid="stButton"] > button:hover {
    background: #f1f6f4 !important; border-color: #cfe0d8 !important;
  }
  section[data-testid="stSidebar"] div[class*="st-key-lang_"]
  div[data-testid="stButton"] > button:hover p {
    color: var(--encre-2) !important;
  }
  section[data-testid="stSidebar"] div[class*="st-key-lang_"]
  div[data-testid="stButton"] > button[kind="primary"] {
    background: var(--accent) !important; border-color: var(--accent) !important;
  }
  section[data-testid="stSidebar"] div[class*="st-key-lang_"]
  div[data-testid="stButton"] > button[kind="primary"] p {
    color: #ffffff !important;
  }
  /* La rangée ouvre la colonne : la paire est resserrée au centre, avec un
     filet en dessous pour la séparer de la marque sans la souligner. */
  section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]:has(
      div[class*="st-key-lang_"]) {
    padding: 12px 2px 12px; margin: 0 auto 2px; max-width: 250px;
    gap: 8px !important;
    border-bottom: 1px solid var(--bord);
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
    "mode_bailleurs": {"en": "Donor briefing", "fr": "Note aux bailleurs"},
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
              "mode_boucles", "mode_croisement", "mode_rapport")
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
_sb_langue_haut = st.sidebar.container()
_sb_marque = st.sidebar.container()
_sb_nav = st.sidebar.container()
_sb_langue = st.sidebar.container()

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
_ruban = st.container()

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
    (MODE_METHODO, "bouclier"),
    (MODE_ACCUEIL, "epingle"),
    (MODE_DIMENSIONS, "barres"),
    (MODE_TRAJECTOIRES, "rafraichir"),
    (MODE_BOUCLES, "boucle"),
    (MODE_CROISEMENT, "loupe"),
    # TREIZE ENTRÉES, C'ÉTAIT TROP, ET DEUX D'ENTRE ELLES DISAIENT LA MÊME
    # CHOSE QUE CELLE-CI. « Diagramme radar » et « Fiche synthèse — paysages »
    # comparaient des profils, ce que fait déjà cette rubrique : elle propose
    # les sections, les groupes ET les deux paysages comme découpages. Elles
    # sont devenues ses deux autres onglets. Rien n'est perdu, on cesse
    # seulement de proposer trois portes vers la même pièce.
    (MODE_SYNTHESE, "personnes"),
    (MODE_ACTIONS, "fiche"),
    # LA NOTE AUX BAILLEURS VIENT APRÈS LES FICHES, ET AVANT LES DONNÉES.
    # Elle est la sortie de tout ce qui précède : elle ne se comprend qu'après
    # les fiches, dont elle reprend les chiffres, et elle doit rester au-dessus
    # des téléchargements, qui ferment toujours la marche.
    # LE RAPPORT PRÉCÈDE LA NOTE, PARCE QU'IL LA FONDE. Six chapitres qui
    # partent des volumes de terrain et finissent par ce qui reste après le
    # projet ; la note qui suit en est la page arrachée.
    (MODE_RAPPORT, "radar"),
    (MODE_BAILLEURS, "cible"),
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
def _rendre_ruban():
    """L'en-tête de page : la photo, et rien d'autre.

    IL N'Y A PLUS DE RUBAN. Cette barre blanche a porté successivement des
    onglets (retirés : la colonne de gauche les affichait déjà), la langue
    (montée en tête de cette colonne) et le logo du PNUE (posé sur la photo).
    Vidée de ses trois contenus, elle n'était plus qu'une bande de blanc en
    haut de chaque page ; la fonction ne s'en va pas, c'est le contenant qui
    disparaît. Reste ici la photo — sur la seule page d'entrée — et le rappel
    du filtre posé, quand il y en a un.
    """
    with _ruban:
        # LA PHOTO NE SERT QUE SUR DEUX PAGES, ET C'EST UN CHOIX DE FONCTION,
        # PAS DE GOÛT. Un bandeau de 300 px répété en tête de chaque page
        # repoussait chaque fois le premier chiffre sous la ligne de
        # flottaison, et une image qu'on revoit à chaque clic cesse d'être
        # regardée. Elle reste là où elle dit quelque chose : l'accueil, qui
        # est la porte d'entrée et doit porter la marque du PNUE dès la
        # première seconde, et le cadre de résilience, qui présente le paysage
        # qu'on mesure.
        photo = st.session_state.get("app_mode") in (MODE_PORTAIL, MODE_METHODO)
        # LE LOGO DU PNUE EST POSÉ SUR LA PHOTO, EN BLANC, ET IL LUI FAUT UN
        # VOILE. La photo est un dessin clair : un logo blanc posé dessus
        # disparaîtrait purement et simplement. Le voile est un dégradé sombre
        # qui s'éteint vers la droite — il fonce l'angle où se pose la marque
        # et laisse l'image intacte partout ailleurs. Sans lui, la seule autre
        # option aurait été de reprendre le logo bleu, c'est-à-dire de revenir
        # à ce qu'on cherchait à quitter.
        st.markdown(
            (f'<div class="bandeau-haut bandeau-enveloppe">'
             f'<img src="data:image/jpeg;base64,{assets.PAYSAGE_CAMP_PERRIN}" '
             f'style="width:100%;height:300px;object-fit:cover;'
             f'object-position:50% 62%;display:block">'
             f'<div class="bandeau-voile"></div>'
             f'<img class="bandeau-logo" alt="UNEP" '
             f'src="data:image/png;base64,{assets.LOGO_UNEP_BLANC}">'
             f'</div>' if photo else "")
            # RIEN D'ÉCRIT SOUS LE BANDEAU QUAND AUCUN FILTRE N'EST POSÉ.
            # Chaque page porte déjà son titre. Le rappel du filtre, lui, ne
            # disait rien tant qu'aucun filtre n'était choisi. Il n'apparaît
            # donc que lorsqu'un filtre est effectivement posé — le seul cas
            # où l'oublier fait mal lire un chiffre.
            + (f'<div class="bh-contexte">'
               f'<div class="bh-filtre">{filtres.resume()}</div></div>'
               if filtres.actif() else '<div class="bh-vide"></div>'),
            unsafe_allow_html=True)


# LES DEUX LANGUES, EN TÊTE DE LA COLONNE, FONDUES DANS LE VERT.
# Deux mots posés sur le fond, sans cadre ni pastille : la langue courante en
# blanc franc, l'autre en blanc estompé. C'est le seul endroit du site où un
# état se lit à la valeur du texte et non à sa couleur de fond — et c'est
# voulu : un choix de langue n'est pas une page, il ne doit pas se présenter
# comme un onglet.
with _sb_langue_haut:
    # DEUX COLONNES ÉGALES, ET PLUS DE TROISIÈME COLONNE VIDE. Le gabarit
    # [1.25, 1, 0.5] datait du temps où les langues étaient deux mots posés à
    # gauche : la colonne fantôme les y retenait, et la première était plus
    # large que la seconde, donc les deux pastilles n'auraient pas eu la même
    # taille. Deux colonnes égales, et la rangée se centre d'elle-même.
    _cl = st.columns(2)
    for _col, _code in zip(_cl, ("fr", "en")):
        with _col:
            st.button(i18n.LANGUES[_code], key=f"lang_{_code}",
                      on_click=_changer_langue, args=(_code,),
                      type=("primary"
                            if st.session_state["choix_langue"] == _code
                            else "secondary"))

with _sb_marque:
    st.markdown(
        f'<div class="apri-marque">'
        f'<img src="data:image/png;base64,{assets.EMBLEME_APRI}" alt="APRI">'
        f'<div class="apri-bloc-nom"><div class="apri-nom">APRI</div>'
        f'<div class="apri-filet"></div>'
        f'<div class="apri-baseline">{T("a_titre_court")}</div>'
        f'<div class="apri-lieu">{T("a_lieu")}</div></div></div>',
        unsafe_allow_html=True)

with _sb_nav:
    st.markdown(_CSS_ICONES_NAV, unsafe_allow_html=True)
    st.markdown(f'<div class="nav-groupe">{T("nav_titre")}</div>',
                unsafe_allow_html=True)
    # LA COLONNE DE GAUCHE NE SERT PLUS QU'À NAVIGUER. Les filtres d'analyse
    # en ont été retirés : posés à côté du contenu, ils obligeaient l'œil à
    # faire l'aller-retour entre la marge et le tableau, et rien ne disait
    # qu'ils s'appliquaient à ce qu'on lisait. Ils sont maintenant dans la page
    # elle-même, sous le titre de la rubrique, là où le résultat est affiché.
    for mode, icone in _NAV:
        _entree_nav(mode, icone)

    # UN RACCOURCI, PAS UN PANNEAU. Les trois sélecteurs sont dans la page,
    # sous le titre de la rubrique — c'est là qu'ils doivent être. Reste ici
    # la seule commande qu'on cherche depuis n'importe où : tout remettre à
    # zéro, avec l'état courant écrit dessous pour qu'on sache s'il y a
    # quelque chose à remettre à zéro.
    st.markdown(f'<div class="f-separateur"></div>'
                f'<div class="nav-groupe">{T("nav_filtres_rapides")}</div>',
                unsafe_allow_html=True)
    st.button(T("f_reinit_long"), key="f_reset_global",
              on_click=filtres.reinitialiser, use_container_width=True,
              disabled=not filtres.actif())
    st.markdown(
        f'<div class="nav-etat">{T("f_aucun") if not filtres.actif() else filtres.resume()}</div>',
        unsafe_allow_html=True)

with _sb_langue:
    # Le logo du PNUE est remonté dans le ruban, en haut à droite. Le
    # répéter ici n'ajouterait rien : la mention institutionnelle en toutes
    # lettres suffit en pied de colonne.
    st.markdown(
        f'<div class="apri-pied">{T("org")}<br><br>'
        f'{T("sous_titre_site")}</div>', unsafe_allow_html=True)

# Le ruban est peint maintenant, dans le conteneur réservé plus haut : il a
# besoin de la langue choisie et du résumé des filtres, tous deux fixés par
# la colonne de gauche qu'on vient de rendre.
_rendre_ruban()

app_mode = st.session_state["app_mode"]

# Les six onglets de dimension passent tous par le même module ; deux d'entre
# eux prolongent leur page avec un détail qui existait déjà, plutôt que d'en
# dupliquer la logique — l'environnement avec ses onze indicateurs
# satellitaires, le social avec les fiches d'organisations de base.
if app_mode == MODE_PORTAIL:
    # Quatre écrans : où, ce qu'on a mesuré, ce qu'on a trouvé, quoi faire.
    accueil_apri.render()

if app_mode == MODE_TRAJECTOIRES:
    # Quatre séries physiques — hectares, millimètres, degrés. Aucun score :
    # les scores vivent dans les autres rubriques.
    trajectoires.render()

if app_mode == MODE_ACCUEIL:
    territoire_page.render()

if app_mode == MODE_DIMENSIONS:
    # Deux dimensions prolongent leur page avec un détail qui existait déjà,
    # plutôt que d'en dupliquer la logique. Ce détail est passé à la page de
    # dimension, qui le place dans le bon sous-onglet — celui des indicateurs.
    _COMPLEMENT = {
        "dim3": lambda: environnement_page.render(entete=False),
        "dim5": lambda: ocb_page.render(entete=False),
    }

    # DES CARTES, PAS DES ONGLETS DE STREAMLIT.
    #
    # `st.tabs` donnait six intitulés en petit, soulignés, qu'il fallait
    # chercher — et surtout il RENDAIT LES SIX PAGES à chaque affichage, y
    # compris les trois cents questions de la dimension économique. Sept
    # secondes pour en montrer une.
    #
    # Une rangée de cartes rectangulaires règle les deux : la cible est
    # franche, l'onglet courant se distingue par un aplat de couleur, et seule
    # la dimension demandée est calculée.
    st.markdown('<div class="cartes-ancre"></div>', unsafe_allow_html=True)
    st.session_state.setdefault("dim_active", MODES_DIM[0])
    if st.session_state["dim_active"] not in MODES_DIM:
        st.session_state["dim_active"] = MODES_DIM[0]

    def _choisir_dim(m):
        st.session_state["dim_active"] = m

    _rangees = [MODES_DIM[:3], MODES_DIM[3:]]
    for _rangee in _rangees:
        for _col, _m in zip(st.columns(len(_rangee)), _rangee):
            with _col:
                _actif = st.session_state["dim_active"] == _m
                st.button(f'**{T(_m)}**\n\n{T(_m + "_carte")}',
                          key=f"carte_{_m}",
                          on_click=_choisir_dim, args=(_m,),
                          type="primary" if _actif else "secondary",
                          use_container_width=True)

    st.markdown('<div class="cartes-trait"></div>', unsafe_allow_html=True)

    _m = st.session_state["dim_active"]
    dimension_page.render(_m, complement=_COMPLEMENT.get(_m))

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

if app_mode == MODE_CROISEMENT:
    # L'outil d'exploration des reponses individuelles. Il ne lit pas les
    # filtres de la colonne : ses conditions SONT son filtre, et deux
    # mecanismes de selection sur la meme page se contrediraient.
    croisement_resultats.render()

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
    _VUES = {T("oc_titre"): "onde", T("sy_titre"): "systeme",
             T("bcl_vue_analyse"): "analyse"}
    _vue = st.radio("vue", list(_VUES), horizontal=True,
                    label_visibility="collapsed",
                    key=f"bcl_vue_{i18n.get_lang()}")
    if _VUES[_vue] == "onde":
        ondes_choc.render(entete=False)
    elif _VUES[_vue] == "systeme":
        systeme_page.render(entete=False)
    else:
        boucles_page.render(entete=False)

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

if app_mode == MODE_BAILLEURS:
    # La page de restitution : constats calculés, réponses classées par le
    # modèle, et ce que le modèle ne couvre pas. Aucun filtre — une note se
    # cite, et une note dont les chiffres dépendent d'un filtre posé ailleurs
    # ne se cite pas.
    note_bailleurs.render()

if app_mode == MODE_SYNTHESE:
    # TROIS FAÇONS DE COMPARER DES PROFILS, SOUS UNE SEULE ENTRÉE.
    #
    #   · par territoire ou par groupe — une section contre les neuf autres,
    #     les femmes contre l'ensemble ;
    #   · par paysage — la fiche littoral contre montagne, qui se lit d'une
    #     traite sans rien demander ;
    #   · par la figure elle-même — le radar, avec son mode d'emploi.
    #
    # C'étaient trois entrées de menu. Ce sont trois onglets, et le lecteur
    # qui cherche « comparer » n'a plus à deviner laquelle des trois portes
    # mène à ce qu'il veut.
    st.title(T("mode_synthese"))
    _o_prof, _o_pays, _o_radar = st.tabs(
        [T("syn_o_profils"), T("syn_o_paysages"), T("syn_o_radar")])
    with _o_prof:
        synthese_page.render(entete=False)
    with _o_pays:
        fiche_paysages.render(entete=False)
    with _o_radar:
        radar_accueil.render(entete=False)

if app_mode == MODE_DONNEES:
    telechargements_page.render()
    # Les livraisons récentes ont suivi les jeux de données : c'est ici
    # qu'on vient voir ce qui est disponible, et donc ce qui vient
    # d'arriver.
    actualites.rendre(_bascule)
