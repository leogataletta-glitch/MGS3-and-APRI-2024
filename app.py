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
import boucles_page
import cadre_page
import croisement_page
import croisement_resultats
import dimension_page
import environnement_page
import filtres
import icones
import interventions_page
import i18n
import map_render
import methodologie_page
import ocb_page
import radar_accueil
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
st.markdown(("""
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
    border-bottom: 1px solid rgba(255,255,255,.12);
  }
  .apri-marque img {
    width: 76px; height: 76px; flex: 0 0 76px; display: block;
  }
  .apri-bloc-nom { min-width: 0; }
  .apri-nom {
    font-family: "Outfit", sans-serif; font-size: 42px; font-weight: 700;
    color: #ffffff; letter-spacing: .01em; line-height: 1;
  }
  .apri-filet {
    width: 64px; height: 3px; border-radius: 2px; background: #7cb342;
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
  /* L'ENTRÉE ACTIVE : une pastille vert clair, encre foncée.
     Le vert profond d'avant se confondait avec le fond de la colonne dès que
     l'écran était mal réglé — on ne voyait plus où l'on se trouvait. Un fond
     clair sur fond sombre, c'est l'inverse du contenu, et l'œil le trouve
     sans chercher. */
  section[data-testid="stSidebar"]
    div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(180deg,#63c493 0%,#4fb383 100%) !important;
    border-color: transparent !important;
    box-shadow: 0 2px 12px rgba(0,0,0,.22) !important;
  }
  section[data-testid="stSidebar"]
    div[data-testid="stButton"] > button[kind="primary"] p {
    color: #0b2b22 !important; font-weight: 700 !important;
  }
  section[data-testid="stSidebar"]
    div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: linear-gradient(180deg,#6ecd9c 0%,#57bb8b 100%) !important;
  }

  /* La couleur du bouton lui-même sert aux icônes : elles sont peintes en
     `currentColor`, donc elles suivent l'état — repos, survol, actif — sans
     qu'on ait à écrire trois fois la même règle par icône. */
  section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
    color: rgba(255,255,255,.72) !important;
  }
  section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
    color: #ffffff !important;
  }
  section[data-testid="stSidebar"]
    div[data-testid="stButton"] > button[kind="primary"] {
    color: #0b2b22 !important;
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

  /* --- le raccourci « filtres rapides » de la colonne ------------------ */
  .f-separateur {
    height: 1px; background: rgba(255,255,255,.12); margin: 16px 2px 2px;
  }
  .nav-etat {
    font-size: 11.5px; color: rgba(255,255,255,.46); line-height: 1.45;
    padding: 6px 6px 0;
  }
  /* Le bouton de remise à zéro ne doit pas se lire comme une entrée de menu :
     il agit sur le filtre, pas sur la navigation. Contour discret, hauteur
     réduite, et son icône de rafraîchissement. */
  section[data-testid="stSidebar"] div[class*="st-key-f_reset_global"]
    div[data-testid="stButton"] > button {
    min-height: 38px !important; padding: 8px 13px !important;
    border: 1px solid rgba(255,255,255,.20) !important;
    background: rgba(255,255,255,.05) !important;
    border-radius: 9px !important;
  }
  section[data-testid="stSidebar"] div[class*="st-key-f_reset_global"]
    div[data-testid="stButton"] > button p {
    font-size: 13.5px !important; font-weight: 500 !important;
  }
  section[data-testid="stSidebar"] div[class*="st-key-f_reset_global"]
    div[data-testid="stButton"] > button:disabled { opacity: .5; }
  __ICONE_RESET__
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
    /* PLUS DE VERT ICI. La bande verte doublait la colonne de gauche, qui
       porte deja l'identite, et elle poussait le premier chiffre de chaque
       page sous la ligne de flottaison. Il reste une barre claire, la plus
       discrete possible : elle ne porte que la langue et le logo. */
    background: #ffffff; border-bottom: none;
    padding: 10px 24px 10px 22px; min-height: 78px;
    align-items: center; gap: 4px !important; flex-wrap: nowrap !important;
  }
  .ruban-ancre { display: none; }

  .ruban-globe {
    display: flex; align-items: center; justify-content: center;
    color: #8a93a5; height: 38px;
  }

  /* Les deux langues : des boutons Streamlit déguisés en pastilles. Au repos
     transparents — c'est le bandeau qui porte la couleur ; au survol un voile
     clair ; la langue courante prend la pastille verte. */
  div[data-testid="stHorizontalBlock"]:has(.ruban-ancre)
  div[data-testid="stButton"] > button {
    background: transparent !important; border: none !important;
    box-shadow: none !important;
    color: #3c4761 !important;
    font-size: 13.5px !important; font-weight: 500 !important;
    line-height: 1.2 !important; white-space: nowrap !important;
    padding: 8px 12px !important; min-height: 38px !important;
    height: auto !important; border-radius: 999px !important;
    justify-content: center !important;
    transition: background .13s ease, color .13s ease;
  }
  div[data-testid="stHorizontalBlock"]:has(.ruban-ancre)
  div[data-testid="stButton"] > button p {
    white-space: nowrap !important;
  }
  div[data-testid="stHorizontalBlock"]:has(.ruban-ancre)
  div[data-testid="stButton"] > button:hover {
    background: #eef3f9 !important;
    color: #101728 !important; transform: none !important;
  }
  /* La langue active en pastille bleue : le vert est la couleur de la
     navigation, et deux verts différents sur le même écran se lisaient comme
     deux états du même objet. */
  div[data-testid="stHorizontalBlock"]:has(.ruban-ancre)
  div[data-testid="stButton"] > button[kind="primary"] {
    background: #2f7fd6 !important; color: #ffffff !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,.22) !important;
  }
  div[data-testid="stHorizontalBlock"]:has(.ruban-ancre)
  div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #3d8ce0 !important;
  }
  .ruban-unep {
    display: flex; justify-content: flex-end; align-items: center;
    padding-right: 12px;
  }
  .ruban-unep img { height: 62px; display: block; }

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
  section[data-testid="stMain"] div[data-testid="stMarkdownContainer"] p,
  section[data-testid="stMain"] div[data-testid="stMarkdownContainer"] li {
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
    font-size: 15.5px !important; font-weight: 700 !important;
    line-height: 1.3 !important; letter-spacing: -.01em !important;
    box-shadow: 0 1px 2px rgba(16,23,40,.05) !important;
    transition: box-shadow .15s ease, transform .15s ease,
                border-color .15s ease !important;
  }
  div[class*="st-key-carte_dim"] > div > button:hover {
    border-color: #c9d8ea !important;
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
    font-size: 12.5px !important; font-weight: 400 !important;
    color: #6b7590 !important; line-height: 1.45 !important;
    text-align: left !important; margin: 0 !important;
  }
  div[class*="st-key-carte_dim"] > div > button p strong {
    display: block; margin-bottom: 7px;
    font-size: 15.5px; font-weight: 700; color: #101728;
    line-height: 1.3; letter-spacing: -.01em;
  }
  div[class*="st-key-carte_dim"] > div > button[kind="primary"] {
    background: #14508f !important; border-color: #14508f !important;
    box-shadow: 0 3px 8px rgba(20,80,143,.28) !important;
  }
  div[class*="st-key-carte_dim"] > div > button[kind="primary"] p {
    color: rgba(255,255,255,.84) !important;
  }
  div[class*="st-key-carte_dim"] > div > button[kind="primary"] p strong {
    color: #ffffff;
  }
  div[class*="st-key-carte_dim"] > div > button[kind="primary"]:hover {
    background: #175da4 !important; border-color: #175da4 !important;
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
    "mode_accueil": {"en": "Overview", "fr": "Vue d'ensemble"},
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
              "mode_boucles", "mode_croisement")
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
MODE_RADAR = "radar"
MODE_CROISEMENT = "croisement"
LIBELLE_MODE = {m: T(m) for m in MODES_DIM}
LIBELLE_MODE.update({MODE_ACCUEIL: T("mode_accueil"),
                     "dimensions": T("mode_dimensions"),
                     MODE_METHODO: T("mode_methodo"),
                     MODE_DONNEES: T("mode_donnees"),
                     MODE_ACTIONS: T("mode_actions"),
                     MODE_BOUCLES: T("mode_boucles"),
                     MODE_SYNTHESE: T("mode_synthese"),
                     MODE_RADAR: T("mode_radar"),
                     MODE_CROISEMENT: T("mode_croisement")})

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
# L'ORDRE EST CELUI DE LA LECTURE, pas celui de la fabrication : on découvre le
# territoire (vue d'ensemble), on apprend ce qu'on mesure et comment (cadre de
# résilience), on lit les résultats par dimension, on compare les territoires
# et les groupes, on passe à l'action, et les données brutes ferment la marche
# pour qui veut refaire les calculs.
_NAV = [
    (MODE_ACCUEIL, "grille"),
    (MODE_METHODO, "bouclier"),
    (MODE_DIMENSIONS, "barres"),
    (MODE_RADAR, "radar"),
    (MODE_BOUCLES, "boucle"),
    (MODE_CROISEMENT, "loupe"),
    (MODE_SYNTHESE, "personnes"),
    (MODE_ACTIONS, "fiche"),
    (MODE_DONNEES, "telecharger"),
]

# LES ICONES SONT PEINTES PAR LA FEUILLE DE STYLE, PAS ECRITES DANS LE LIBELLE.
# On ne peut rien inserer dans le contenu d'un bouton Streamlit ; en revanche
# chaque widget porte une classe `st-key-<cle>`, ce qui permet de viser un
# bouton precis et de lui poser son icone en `::before`. Les glyphes
# typographiques qui servaient jusqu'ici ne disaient rien, et leur graisse
# changeait d'une police systeme a l'autre.
_CSS_ICONES_NAV = "<style>" + "".join(
    icones.regle_masque(
        f'section[data-testid="stSidebar"] div[class*="st-key-nav_{_m}"] '
        f'div[data-testid="stButton"] > button', _i)
    for _m, _i in _NAV) + "</style>"


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
        # Les deux colonnes de langue sont plus larges depuis que le globe
        # a disparu : à 1,15 elles reprenaient sa place et coupaient
        # « Français » en deux lignes.
        cols = st.columns([1.6, 1.6, 5.2, 2.6],
                          vertical_alignment="center")
        # LE GLOBE A ÉTÉ RETIRÉ. « Français » et « English » sont écrits en
        # toutes lettres dans leur propre langue : un pictogramme devant deux
        # mots qui se lisent déjà n'ajoutait rien.
        #
        # L'ANCRE RESTE DANS LA PREMIÈRE COLONNE, ET C'EST ESSENTIEL : la
        # feuille de style habille la rangée QUI CONTIENT cette ancre, via
        # :has(). Sortie de la rangée, elle emporte tout le style avec elle —
        # les boutons redeviennent des cartes blanches et les libellés se
        # coupent en deux lignes.
        for col, code in zip(cols[0:2], ("fr", "en")):
            with col:
                st.button(i18n.LANGUES[code], key=f"lang_{code}",
                          on_click=_changer_langue, args=(code,),
                          type=("primary"
                                if st.session_state["choix_langue"] == code
                                else "secondary"),
                          use_container_width=True)
        with cols[-1]:
            st.markdown(
                f'<div class="ruban-ancre"></div>'
                f'<div class="ruban-unep"><img alt="UNEP" '
                f'src="data:image/png;base64,{assets.LOGO_UNEP_BLEU}"></div>',
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
if app_mode == MODE_ACCUEIL:
    accueil_page.render(actualites=lambda: actualites.rendre(_bascule))

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
    # il est rendu dans le volet replié du bas, avec l'outil de croisement
    # libre. Une fonction qui marchait ne se supprime pas au motif qu'on a
    # réorganisé la façade ; on la range.
    def _document_methodologique():
        methodologie_page.render()
        with st.expander(T("m_croisement_libre")):
            croisement_page.render(entete=False)

    cadre_page.render(doc_complet=_document_methodologique)

if app_mode == MODE_RADAR:
    # UNE RUBRIQUE À PART, PARCE QU'ON LA CHERCHE POUR ELLE-MÊME.
    # Le radar est aussi présent dans « Analyse des résultats » (celui de la
    # dimension ouverte) et dans « Profils territoriaux et sociaux » (celui
    # des six dimensions) — là, il commente ce qui l'entoure. Ici, il est
    # l'objet de la page : on y vient pour comparer, pas pour illustrer.
    radar_accueil.render()

if app_mode == MODE_CROISEMENT:
    # L'outil d'exploration des reponses individuelles. Il ne lit pas les
    # filtres de la colonne : ses conditions SONT son filtre, et deux
    # mecanismes de selection sur la meme page se contrediraient.
    croisement_resultats.render()

if app_mode == MODE_BOUCLES:
    boucles_page.render()

if app_mode == MODE_ACTIONS:
    # Les fiches descendent des leviers calculés par l'analyse des boucles.
    # Les anciennes pistes de travail, écrites avant cette analyse, ont été
    # retirées : elles ne commandaient plus rien et brouillaient la page.
    interventions_page.render()

if app_mode == MODE_SYNTHESE:
    synthese_page.render()

if app_mode == MODE_DONNEES:
    telechargements_page.render()
