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

import accueil_page
import actualites
import assets
import croisement_page
import dimension_page
import environnement_page
import filtres
import i18n
import map_render
import methodologie_page
import ocb_page
import pistes_page
import resilience_page
import saillants_page
import synthese_page
import telechargements_page
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
st.set_page_config(page_title="Household resilience survey — Sud & Grand'Anse, Haiti", layout="wide")

if not check_password():
    st.stop()

# Typographie de toute l'application. Deux principes : une seule famille
# (Roboto, la police institutionnelle du PNUE, avec repli système si la
# connexion aux polices Google échoue), et une largeur de ligne bornée —
# une phrase qui court sur 1400 px est illisible, c'est ce qui rendait les
# blocs de texte pénibles à lire.
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

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
    --accent:     #1a6bb0;
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
  /* padding-top nul : le ruban vert est le premier élément de chaque page
     et doit toucher le haut de la fenêtre. Le reste du contenu retrouve son
     air sous le bandeau, via la marge de .bh-contexte. */
  .block-container { max-width: 1240px; padding-top: 0; padding-bottom: 5rem; }

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

  /* --- titres --- */
  h1, h2, h3 {
    font-family: "Outfit", "Inter", system-ui, sans-serif !important;
    color: var(--encre); letter-spacing: -0.02em;
  }
  h1 { font-weight: 700 !important; font-size: 2.6rem !important;
       line-height: 1.12 !important; }
  h2 { font-weight: 700 !important; font-size: 1.7rem !important;
       margin-top: .2rem !important; padding-bottom: .2rem !important; }
  h3 { font-weight: 600 !important; font-size: 1.28rem !important;
       margin-top: .2rem !important; }

  /* --- texte : jamais minuscule, jamais délavé --- */
  [data-testid="stMarkdownContainer"] p,
  [data-testid="stMarkdownContainer"] li {
    font-size: 16px; line-height: 1.66; color: var(--encre-2);
  }
  [data-testid="stMarkdownContainer"] strong { color: var(--encre); }
  [data-testid="stCaptionContainer"] p {
    font-size: 15px !important; line-height: 1.62 !important;
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
    border-color: #cddcf0 !important;
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
    font-family: "Outfit", sans-serif; font-weight: 700; font-size: 13px;
    letter-spacing: .06em; text-transform: uppercase;
    color: var(--accent); background: #eaf3fb;
    padding: 6px 13px; border-radius: 999px; margin: 0 0 4px;
  }
  .titre-bloc.vert  { color: #0b7f74; background: #e5f6f3; }
  .titre-bloc.ambre { color: #a8690a; background: #fdf3e3; }

  /* --- menus : champs pleins, arrondis, réactifs --- */
  label[data-testid="stWidgetLabel"] p {
    font-size: 13px !important; font-weight: 700 !important;
    letter-spacing: .04em; color: var(--encre-3) !important;
    text-transform: uppercase;
  }
  div[data-baseweb="select"] > div {
    font-size: 15.5px; border-radius: 11px; border: 1.5px solid var(--bord);
    background: #f7fafd; transition: border-color .15s ease, box-shadow .15s ease;
  }
  div[data-baseweb="select"] > div:hover { border-color: #b9d3ea; }
  div[data-baseweb="select"] > div:focus-within {
    border-color: var(--accent); box-shadow: 0 0 0 3px rgba(26,107,176,.14);
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
    font-size: 16px !important; color: var(--encre-2) !important; margin: 0;
  }

  details {
    background: var(--carte); border: 1px solid var(--bord) !important;
    border-radius: 14px !important; box-shadow: var(--ombre);
  }
  details summary p {
    font-size: 15px !important; font-weight: 600 !important;
    color: var(--encre-2);
  }

  .org-mention {
    font-size: 11.5px; color: var(--encre-3); letter-spacing: .12em;
    text-transform: uppercase; margin: 0 0 3px 1px; font-weight: 700;
  }

  /* --- les trois entrées : grandes tuiles en relief --- */
  div[data-testid="stButton"] > button {
    height: 92px; border-radius: 16px; border: 1.5px solid var(--bord);
    font-family: "Outfit", sans-serif !important;
    font-size: 18px !important; font-weight: 600 !important;
    line-height: 1.3; white-space: normal; padding: 12px 20px;
    background: var(--carte); box-shadow: var(--ombre);
    transition: transform .18s cubic-bezier(.2,.7,.3,1), box-shadow .18s ease,
                background .18s ease, border-color .18s ease;
  }
  div[data-testid="stButton"] > button p {
    font-size: 18px !important; font-weight: 600 !important;
  }
  div[data-testid="stButton"] > button:hover {
    transform: translateY(-3px); box-shadow: var(--ombre-haut);
    border-color: #b9d3ea;
  }
  div[data-testid="stButton"] > button[kind="primary"],
  div[data-testid="stButton"] > button[kind="primary"] p,
  div[data-testid="stButton"] > button[kind="primary"] div { color: #fff !important; }
  div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #1f7ac4 0%, #15588f 100%) !important;
    border-color: transparent !important;
    box-shadow: 0 2px 6px rgba(21,88,143,.28), 0 14px 30px rgba(21,88,143,.24);
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
    border-color: #b9d3ea; background: #eaf3fb;
  }
  .stRadio > div[role="radiogroup"] > label > div:last-child p {
    font-size: 14.5px !important; font-weight: 600 !important;
    color: var(--encre-2);
  }

  /* --- barre latérale --- */
  section[data-testid="stSidebar"] {
    background: #fafcfe; border-right: 1px solid var(--bord);
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
    background: #eaf3fb !important; border: 1.5px solid #cfe2f3 !important;
    color: var(--accent) !important; font-weight: 600 !important;
    font-size: 14.5px !important; box-shadow: none;
  }
  div[data-testid="stDownloadButton"] > button:hover {
    background: #dcebf8 !important; transform: translateY(-1px);
  }

  /* --- iframes des graphiques : coins arrondis, fond blanc --- */
  iframe { border-radius: 12px; background: #ffffff; }

  /* ================= barre latérale : la navigation du site =============
     Vert profond plutôt que le gris par défaut : la navigation doit se
     détacher franchement du contenu, sinon l'œil hésite entre les deux à
     chaque changement de page. */
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #123c30 0%, #0d2f26 100%) !important;
    border-right: none;
    width: 310px !important; min-width: 310px !important;
  }
  section[data-testid="stSidebar"] > div { padding: 18px 14px 14px; }

  /* Le bloc de marque, sur le modèle de la charte : l'emblème détouré posé
     directement sur le vert — pas de carte blanche, qui faisait une tache —
     puis le nom en texte et un filet vert sous le sigle. L'emblème est
     l'image EMBLEME_APRI, découpée du logo complet : le verbal « IRLA/APRI »
     du fichier d'origine devenait illisible à cette taille. */
  .apri-marque {
    display: flex; align-items: center; gap: 14px;
    padding: 2px 2px 16px; margin-bottom: 2px;
    border-bottom: 1px solid rgba(255,255,255,.12);
  }
  .apri-marque img {
    width: 58px; height: 58px; flex: 0 0 58px; display: block;
  }
  .apri-bloc-nom { min-width: 0; }
  .apri-nom {
    font-family: "Outfit", sans-serif; font-size: 34px; font-weight: 700;
    color: #ffffff; letter-spacing: .01em; line-height: 1;
  }
  .apri-filet {
    width: 52px; height: 3px; border-radius: 2px; background: #7cb342;
    margin: 5px 0 0;
  }
  /* Deux niveaux dans l'accroche, comme sur la charte : ce qu'est
     l'observatoire, en vert clair, puis où il porte, en blanc. Une seule
     ligne grise disait les deux d'un même souffle et on ne lisait ni l'un ni
     l'autre. */
  .apri-baseline {
    font-size: 12px; color: #8cc63f; line-height: 1.3;
    margin-top: 6px; font-weight: 500;
  }
  .apri-lieu {
    font-size: 12.5px; color: rgba(255,255,255,.92); line-height: 1.3;
    margin-top: 3px; font-weight: 600;
  }
  /* Pied de colonne : le logo du PNUE y descend, puisque les logos ne
     doivent plus apparaître dans le contenu des pages. */
  .apri-org {
    display: flex; align-items: center; gap: 10px;
    margin-top: 14px; padding-top: 13px;
    border-top: 1px solid rgba(255,255,255,.12);
  }
  .apri-org img {
    width: 34px; height: 34px; flex: 0 0 34px; object-fit: contain;
    background: #ffffff; border-radius: 6px; padding: 2px;
  }
  .nav-groupe {
    font-size: 10.5px; letter-spacing: .14em; text-transform: uppercase;
    color: rgba(255,255,255,.40); font-weight: 700;
    margin: 18px 0 8px 4px;
  }
  .apri-pied {
    font-size: 10.5px; color: rgba(255,255,255,.38); line-height: 1.5;
    padding: 14px 4px 4px; margin-top: 10px;
    border-top: 1px solid rgba(255,255,255,.12);
  }
  /* Dans le bloc PNUE, la mention institutionnelle est déjà séparée par le
     filet de .apri-org : lui laisser le sien dessinait deux traits l'un sur
     l'autre. */
  .apri-org .apri-pied {
    border-top: none; padding: 0; margin: 0; font-size: 11px;
    color: rgba(255,255,255,.55);
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

     SURVOL — un fond qui s'éclaircit légèrement. Sans retour au survol, rien
     ne distingue une ligne cliquable d'un simple titre. */
  section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
    display: flex !important; align-items: center !important;
    justify-content: flex-start !important;
    width: 100% !important; min-height: 46px !important; height: auto !important;
    padding: 11px 15px !important; border-radius: 10px !important;
    border: 1px solid transparent !important;
    background: transparent !important; box-shadow: none !important;
    transition: background .15s ease, border-color .15s ease;
    margin-bottom: 3px;
  }
  section[data-testid="stSidebar"] div[data-testid="stButton"] > button > div,
  section[data-testid="stSidebar"] div[data-testid="stButton"] > button
    div[data-testid="stMarkdownContainer"] {
    width: 100% !important; text-align: left !important;
    display: block !important;
  }
  section[data-testid="stSidebar"] div[data-testid="stButton"] > button p {
    font-family: "Outfit", sans-serif !important;
    font-size: 15.5px !important; font-weight: 500 !important;
    line-height: 1.35 !important;
    color: rgba(255,255,255,.82) !important;
    text-align: left !important; width: 100%; margin: 0 !important;
  }
  section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
    background: rgba(255,255,255,.11) !important;
    border-color: rgba(255,255,255,.16) !important;
    transform: none !important;
  }
  section[data-testid="stSidebar"]
    div[data-testid="stButton"] > button:hover p {
    color: #ffffff !important;
  }
  section[data-testid="stSidebar"]
    div[data-testid="stButton"] > button[kind="primary"] {
    background: #1f7a5a !important; border-color: transparent !important;
    box-shadow: 0 2px 10px rgba(0,0,0,.26) !important;
  }
  section[data-testid="stSidebar"]
    div[data-testid="stButton"] > button[kind="primary"] p {
    color: #ffffff !important; font-weight: 600 !important;
  }
  section[data-testid="stSidebar"]
    div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #23895f !important;
  }

  /* Le sélecteur de langue, seul widget non bouton de la colonne */
  section[data-testid="stSidebar"] label,
  section[data-testid="stSidebar"] .stRadio label p {
    color: rgba(255,255,255,.72) !important;
  }
  section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background: rgba(255,255,255,.09); border-color: rgba(255,255,255,.18);
    color: #ffffff;
  }
  section[data-testid="stSidebar"] div[data-baseweb="select"] svg {
    fill: rgba(255,255,255,.7);
  }

  /* --- le bloc « filtres actifs » de la colonne ------------------------ */
  .f-separateur {
    height: 1px; background: rgba(255,255,255,.12); margin: 16px 2px 2px;
  }
  section[data-testid="stSidebar"] div[data-testid="stSelectbox"] label p {
    font-size: 11.5px !important; letter-spacing: .04em;
    color: rgba(255,255,255,.55) !important; font-weight: 600 !important;
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
    border: 1px solid rgba(255,255,255,.18) !important;
  }
  section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]
    div[data-testid="stButton"] > button p {
    font-size: 11.5px !important; font-weight: 600 !important;
    text-align: center !important;
    color: rgba(255,255,255,.70) !important;
  }
  section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]
    div[data-testid="stButton"] > button:disabled {
    opacity: .35; border-color: rgba(255,255,255,.10) !important;
  }
  .f-chips { display: flex; flex-direction: column; gap: 6px; margin-top: 11px; }
  .f-chip {
    display: flex; align-items: baseline; gap: 8px;
    background: rgba(255,255,255,.09); border: 1px solid rgba(255,255,255,.14);
    border-radius: 9px; padding: 7px 11px;
  }
  .f-chip-cle {
    font-size: 10px; letter-spacing: .1em; text-transform: uppercase;
    color: rgba(255,255,255,.50); font-weight: 700; white-space: nowrap;
  }
  .f-chip-val {
    font-size: 13.5px; color: #ffffff; font-weight: 600;
  }
  .f-vide {
    font-size: 11.5px; color: rgba(255,255,255,.42); line-height: 1.5;
    margin-top: 10px; padding: 0 3px;
  }

  /* ================= le bandeau du haut =================================
     Une barre vert profond qui court d'un bord à l'autre, dans le même vert
     que la colonne de gauche : les deux ne font plus qu'un cadre, et le
     contenu blanc s'y pose comme une feuille.

     ELLE PORTE DEUX CHOSES : la langue à gauche, le logo du PNUE à droite.
     Elle a d'abord repris les six entrées de navigation ; c'était une redite —
     la colonne de gauche les affiche en permanence.

     PLEINE LARGEUR. Le contenu du site reste borné à 1240 px — une ligne qui
     court sur 1900 px ne se lit pas. Le bandeau, lui, touche les deux bords :
     largeur = la fenêtre MOINS la colonne de gauche, fixe à 310 px. Si un jour
     vous changez cette largeur, changez les deux valeurs ensemble, sinon le
     bandeau dépasse à droite et le logo sort de l'écran.

     Streamlit ne donne pas de marqueur propre à une rangée de colonnes : on y
     glisse une ancre invisible et on habille la rangée qui la contient. */
  div[data-testid="stHorizontalBlock"]:has(.ruban-ancre) {
    width: calc(100vw - 310px) !important;
    max-width: calc(100vw - 310px) !important;
    margin-left: calc(-50vw + 50% + 155px);
    /* Les feuilles de style injectées par st.markdown occupent chacune un
       bloc vide en tête de page, et la gouttière verticale de Streamlit
       s'ajoute par-dessus : 32 px de blanc avant le bandeau. On les remonte. */
    margin-top: -32px; margin-bottom: 0;
    background: linear-gradient(180deg, #14402f 0%, #0f3327 100%);
    padding: 11px 24px 11px 22px; min-height: 70px;
    align-items: center; gap: 4px !important; flex-wrap: nowrap !important;
  }
  .ruban-ancre { display: none; }

  .ruban-globe {
    display: flex; align-items: center; justify-content: center;
    color: rgba(255,255,255,.62); height: 38px;
  }

  /* Les deux langues : des boutons Streamlit déguisés en pastilles. Au repos
     transparents — c'est le bandeau qui porte la couleur ; au survol un voile
     clair ; la langue courante prend la pastille verte. */
  div[data-testid="stHorizontalBlock"]:has(.ruban-ancre)
  div[data-testid="stButton"] > button {
    background: transparent !important; border: none !important;
    box-shadow: none !important;
    color: rgba(255,255,255,.80) !important;
    font-size: 13.5px !important; font-weight: 500 !important;
    line-height: 1.2 !important; white-space: nowrap !important;
    padding: 8px 12px !important; min-height: 38px !important;
    height: auto !important; border-radius: 999px !important;
    justify-content: center !important;
    transition: background .13s ease, color .13s ease;
  }
  div[data-testid="stHorizontalBlock"]:has(.ruban-ancre)
  div[data-testid="stButton"] > button:hover {
    background: rgba(255,255,255,.11) !important;
    color: #ffffff !important; transform: none !important;
  }
  div[data-testid="stHorizontalBlock"]:has(.ruban-ancre)
  div[data-testid="stButton"] > button[kind="primary"] {
    background: #5f9e3f !important; color: #ffffff !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,.20) !important;
  }
  div[data-testid="stHorizontalBlock"]:has(.ruban-ancre)
  div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #6cb047 !important;
  }
  .ruban-unep {
    display: flex; justify-content: flex-end; align-items: center;
    padding-right: 12px;
  }
  .ruban-unep img { height: 46px; display: block; }

  /* Le bandeau de paysage suit le ruban et déborde comme lui : les deux
     forment un seul en-tête, sans liseré blanc entre eux. */
  .bandeau-haut {
    width: calc(100vw - 310px) !important;
    max-width: calc(100vw - 310px) !important;
    margin-left: calc(-50vw + 50% + 155px);
    margin-top: 0; margin-bottom: 0;
  }

  /* La ligne de contexte, sous le ruban : la page courante à gauche, ce sur
     quoi porte l'affichage à droite. Un chiffre lu sans savoir qu'un filtre
     est posé est un chiffre mal lu. */
  .bh-contexte {
    display: flex; align-items: center; justify-content: flex-start;
    gap: 16px; flex-wrap: wrap; margin: 12px 0 10px;
  }
  /* Sans ligne de contenu, le bandeau collerait au titre de la page. */
  .bh-vide { height: 22px; }
  .bh-page {
    font-size: 16.5px; font-weight: 700; color: #101728;
    letter-spacing: -.01em;
  }
  .bh-filtre {
    font-size: 13px; color: #1f7a5a; font-weight: 600;
    background: #eaf6f0; border: 1px solid #cfe9dd; border-radius: 999px;
    padding: 5px 14px;
  }

  /* --- le panneau des dernières livraisons ---------------------------- */
  .n-item {
    display: flex; gap: 12px; align-items: flex-start;
    padding: 11px 0 3px;
  }
  .n-icone {
    flex: 0 0 34px; width: 34px; height: 34px; border-radius: 9px;
    background: #eaf6f0; color: #1f7a5a; font-size: 16px;
    display: flex; align-items: center; justify-content: center;
  }
  .n-corps { flex: 1 1 auto; min-width: 0; }
  .n-titre {
    font-size: 14.5px; font-weight: 700; color: #101728; line-height: 1.35;
  }
  .n-badge {
    display: inline-block; margin-left: 7px; vertical-align: middle;
    background: #eaf6f0; color: #1f7a5a; border: 1px solid #cfe9dd;
    border-radius: 999px; padding: 1px 8px;
    font-size: 10px; font-weight: 700; letter-spacing: .06em;
    text-transform: uppercase;
  }
  .n-texte {
    font-size: 13px; color: #6b7590; line-height: 1.5; margin-top: 3px;
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
    font-family: "Outfit", sans-serif !important;
    font-size: 15px !important; font-weight: 600 !important;
    color: var(--encre-2) !important; margin: 0;
  }
  .stTabs [data-baseweb="tab-list"] button[data-baseweb="tab"]:hover {
    transform: translateY(-2px); border-color: #b9d3ea; background: #f4f8fc;
    box-shadow: 0 2px 5px rgba(16,23,40,.07), 0 10px 22px rgba(16,23,40,.09);
  }
  .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    background: linear-gradient(135deg, #1f7ac4 0%, #15588f 100%);
    border-color: transparent;
    box-shadow: 0 2px 6px rgba(21,88,143,.26), 0 10px 22px rgba(21,88,143,.20);
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
    transform: translateY(-3px) !important; border-color: #cddcf0 !important;
    box-shadow: 0 3px 6px rgba(16,23,40,.07), 0 18px 38px rgba(16,23,40,.13) !important;
  }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Garde-fou : les fichiers sont poussés à la main sur GitHub, un par un. Si le
# dictionnaire de traduction est resté sur une version antérieure, l'application
# ne plante pas — elle affiche le nom des clés manquantes au milieu du texte, ce
# qui est beaucoup plus déroutant qu'une erreur franche. On préfère le dire.
# ----------------------------------------------------------------------
I18N_ATTENDU = "2026-08-18-questions"

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
LIBELLE_MODE = {m: T(m) for m in MODES_DIM}
LIBELLE_MODE.update({MODE_ACCUEIL: T("mode_accueil"),
                     "dimensions": T("mode_dimensions"),
                     MODE_METHODO: T("mode_methodo"),
                     MODE_DONNEES: T("mode_donnees"),
                     MODE_ACTIONS: T("mode_actions"),
                     MODE_SYNTHESE: T("mode_synthese")})

# L'état de navigation doit exister AVANT la barre du haut, qui affiche le nom
# de la page courante. L'initialiser plus bas laissait la barre lire une clé
# absente — et Streamlit lève alors une erreur qui masque toute la page.
if "app_mode" not in st.session_state:
    st.session_state["app_mode"] = MODE_ACCUEIL


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
_NAV = [
    (MODE_ACCUEIL, "◉"),
    (MODE_DIMENSIONS, "▦"),
    (MODE_SYNTHESE, "◐"),
    (MODE_ACTIONS, "➜"),
    (MODE_METHODO, "§"),
    (MODE_DONNEES, "⤓"),
]


def _entree_nav(mode, icone):
    actif = st.session_state["app_mode"] == mode
    st.button(f"{icone}\u2003{LIBELLE_MODE[mode]}", key=f"nav_{mode}",
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
    """Le bandeau vert du haut : les deux langues à gauche, le logo à droite.

    IL N'Y A PAS D'ONGLETS ICI. Les six entrées y étaient reprises mot pour mot
    depuis la colonne de gauche, qui les affiche déjà en permanence : deux
    menus identiques à quinze centimètres l'un de l'autre. La navigation vit
    dans la colonne ; le bandeau porte la langue et la marque.

    LA LANGUE EN DEUX MOTS, PAS EN MENU. « Français » et « English » côte à
    côte, avec le globe : on lit et on clique d'un seul geste, là où un menu
    déroulant demandait d'ouvrir, viser, choisir — pour deux choix.

    Streamlit n'encadre pas une rangée de boutons dans son propre HTML : chaque
    appel à st.markdown vit dans son conteneur. On glisse donc une ancre
    invisible dans la rangée, et le CSS habille la rangée QUI LA CONTIENT, via
    :has().
    """
    with _ruban:
        cols = st.columns([0.5, 1.15, 1.15, 6, 2.2],
                          vertical_alignment="center")
        with cols[0]:
            st.markdown(
                '<div class="ruban-ancre"></div>'
                '<div class="ruban-globe" title="Langue / Language">'
                # Globe dessiné en SVG plutôt qu'un émoji : l'émoji change de
                # dessin et de couleur selon le système, et rendait la barre
                # bariolée sur Windows.
                '<svg viewBox="0 0 24 24" width="19" height="19" fill="none" '
                'stroke="currentColor" stroke-width="1.7" '
                'stroke-linecap="round"><circle cx="12" cy="12" r="9"/>'
                '<path d="M3 12h18M12 3c2.6 2.7 2.6 15.3 0 18'
                'M12 3c-2.6 2.7-2.6 15.3 0 18"/></svg></div>',
                unsafe_allow_html=True)
        for col, code in zip(cols[1:3], ("fr", "en")):
            with col:
                st.button(i18n.LANGUES[code], key=f"lang_{code}",
                          on_click=_changer_langue, args=(code,),
                          type=("primary"
                                if st.session_state["choix_langue"] == code
                                else "secondary"),
                          use_container_width=True)
        with cols[-1]:
            st.markdown(
                f'<div class="ruban-unep"><img alt="UNEP" '
                f'src="data:image/png;base64,{assets.LOGO_UNEP_BLANC}"></div>',
                unsafe_allow_html=True)

        st.markdown(
            f'<img src="data:image/jpeg;base64,{assets.PAYSAGE_CAMP_PERRIN}" '
            f'class="bandeau-haut" '
            f'style="width:100%;height:300px;object-fit:cover;'
            f'object-position:50% 62%;display:block">'
            # RIEN D'ÉCRIT SOUS LE BANDEAU QUAND AUCUN FILTRE N'EST POSÉ.
            # Chaque page porte déjà son titre. Le rappel du filtre, lui, ne
            # disait rien tant qu'aucun filtre n'était choisi. Il n'apparaît
            # donc que lorsqu'un filtre est effectivement posé — le seul cas
            # où l'oublier fait mal lire un chiffre.
            + (f'<div class="bh-contexte">'
               f'<div class="bh-filtre">{filtres.resume()}</div></div>'
               if filtres.actif() else '<div class="bh-vide"></div>'),
            unsafe_allow_html=True)


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
    st.markdown(f'<div class="nav-groupe">{T("nav_general")}</div>',
                unsafe_allow_html=True)
    for mode, icone in _NAV:
        _entree_nav(mode, icone)
    st.markdown('<div class="f-separateur"></div>', unsafe_allow_html=True)
    filtres.rendre_panneau()

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
if app_mode == MODE_ACCUEIL:
    accueil_page.render(actualites=lambda: actualites.rendre(_bascule))

if app_mode == MODE_DIMENSIONS:
    # Deux dimensions prolongent leur page avec un détail qui existait déjà,
    # plutôt que d'en dupliquer la logique. Ce détail est passé à la page de
    # dimension, qui le place dans le bon sous-onglet — celui des indicateurs.
    # Avant l'apparition des sous-onglets il était rendu après la page, ce qui
    # le laissait désormais hors des deux onglets, en bas de l'écran.
    _COMPLEMENT = {
        "dim3": lambda: environnement_page.render(entete=False),
        "dim5": lambda: ocb_page.render(entete=False),
    }
    _onglets_dim = st.tabs([T(m) for m in MODES_DIM])
    for _i, _m in enumerate(MODES_DIM):
        with _onglets_dim[_i]:
            dimension_page.render(_m, complement=_COMPLEMENT.get(_m))

if app_mode == MODE_METHODO:
    methodologie_page.render()
    # Le croisement des questions entre elles n'a plus d'onglet propre : les
    # questions vivent désormais sous l'indicateur qu'elles alimentent, dans
    # chaque dimension. L'outil d'exploration libre reste néanmoins accessible
    # ici — une fonction qui marchait ne se supprime pas au motif qu'on a
    # réorganisé la façade.
    with st.expander(T("m_croisement_libre")):
        croisement_page.render(entete=False)

if app_mode == MODE_ACTIONS:
    pistes_page.render()

if app_mode == MODE_SYNTHESE:
    synthese_page.render()

if app_mode == MODE_DONNEES:
    telechargements_page.render()
