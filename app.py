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
import assets
import croisement_page
import dimension_page
import environnement_page
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
  .block-container { max-width: 1240px; padding-top: 1.6rem; padding-bottom: 5rem; }

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
     chaque changement de page. Les boutons y perdent leur relief de tuile —
     un menu ne se survole pas comme une carte à cliquer, il se parcourt. */
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #123c30 0%, #0d2f26 100%) !important;
    border-right: none;
    width: 288px !important;
  }
  section[data-testid="stSidebar"] > div { padding-top: 14px; }

  .apri-marque {
    display: flex; align-items: center; gap: 11px;
    padding: 4px 6px 16px; margin-bottom: 4px;
    border-bottom: 1px solid rgba(255,255,255,.10);
  }
  .apri-marque img {
    width: 46px; height: 46px; object-fit: contain;
    background: #ffffff; border-radius: 11px; padding: 4px;
  }
  .apri-nom {
    font-family: "Outfit", sans-serif; font-size: 25px; font-weight: 700;
    color: #ffffff; letter-spacing: .01em; line-height: 1;
  }
  .apri-baseline {
    font-size: 11px; color: rgba(255,255,255,.62); line-height: 1.35;
    margin-top: 3px;
  }
  .nav-groupe {
    font-size: 10.5px; letter-spacing: .13em; text-transform: uppercase;
    color: rgba(255,255,255,.42); font-weight: 700;
    margin: 15px 0 6px 7px;
  }
  .apri-pied {
    font-size: 10.5px; color: rgba(255,255,255,.40); line-height: 1.5;
    padding: 12px 7px 4px; margin-top: 6px;
    border-top: 1px solid rgba(255,255,255,.10);
  }

  /* Les boutons de la barre latérale : plats, alignés à gauche, sans ombre.
     Le mode courant est plein, les autres transparents — un seul repère
     visuel, celui qui répond à « où suis-je ». */
  section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
    height: auto !important; min-height: 0;
    padding: 9px 13px !important; border-radius: 9px;
    border: 1px solid transparent !important;
    background: transparent !important; box-shadow: none !important;
    text-align: left; justify-content: flex-start;
    transition: background .14s ease, color .14s ease;
    margin-bottom: 1px;
  }
  section[data-testid="stSidebar"] div[data-testid="stButton"] > button p {
    font-family: "Outfit", sans-serif !important;
    font-size: 14.5px !important; font-weight: 500 !important;
    color: rgba(255,255,255,.78) !important; text-align: left; margin: 0;
  }
  section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
    background: rgba(255,255,255,.07) !important; transform: none;
  }
  section[data-testid="stSidebar"]
    div[data-testid="stButton"] > button[kind="primary"] {
    background: #1f7a5a !important; border-color: transparent !important;
    box-shadow: 0 2px 8px rgba(0,0,0,.22) !important;
  }
  section[data-testid="stSidebar"]
    div[data-testid="stButton"] > button[kind="primary"] p {
    color: #ffffff !important; font-weight: 600 !important;
  }

  /* Le sélecteur de langue, seul widget non bouton de la colonne */
  section[data-testid="stSidebar"] label,
  section[data-testid="stSidebar"] .stRadio label p {
    color: rgba(255,255,255,.72) !important;
  }
  section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label {
    background: rgba(255,255,255,.07); border-color: rgba(255,255,255,.14);
  }
  section[data-testid="stSidebar"]
    .stRadio > div[role="radiogroup"] > label > div:last-child p {
    color: rgba(255,255,255,.86) !important;
  }
  section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background: rgba(255,255,255,.08); border-color: rgba(255,255,255,.16);
    color: #ffffff;
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
I18N_ATTENDU = "2026-08-17-ergonomie"
if getattr(i18n, "VERSION", None) != I18N_ATTENDU:
    st.error(
        f"**i18n.py est dans une version qui ne correspond pas au reste de "
        f"l'application** — attendue : `{I18N_ATTENDU}`, trouvée : "
        f"`{getattr(i18n, 'VERSION', 'aucune')}`.\n\n"
        f"Les textes vont s'afficher sous forme de noms de clés "
        f"(`mode_ocb`, `o_intro`…). Renvoyer sur GitHub le `i18n.py` livré "
        f"avec cette mise à jour, à la racine du dépôt, corrige l'affichage.\n\n"
        f"*i18n.py is out of date — re-upload the version delivered with this "
        f"update to the repository root.*")

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

with _sb_langue:
    _code = st.selectbox(
        T("langue"), list(i18n.LANGUES.keys()),
        format_func=lambda c: i18n.LANGUES[c], key="choix_langue",
        label_visibility="collapsed")
i18n.set_lang(_code)

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
                     MODE_METHODO: T("mode_methodo"),
                     MODE_DONNEES: T("mode_donnees"),
                     MODE_ACTIONS: T("mode_actions"),
                     MODE_SYNTHESE: T("mode_synthese")})

# L'identité APRI vit maintenant dans la barre latérale : la répéter en haut
# du contenu volerait un tiers d'écran avant le premier chiffre. Il reste ici
# une ligne institutionnelle — le commanditaire et le titre long, qu'une
# capture d'écran doit porter avec elle — et le bandeau, réduit de moitié pour
# rester un décor.
# Un SEUL bloc HTML : Streamlit isole chaque appel à st.markdown dans son
# propre conteneur, si bien qu'une balise ouverte dans l'un et fermée dans le
# suivant ne s'emboîte jamais — le style se perd sans qu'aucune erreur ne le
# signale.
st.markdown(
    f'<div style="display:flex;align-items:center;'
    f'justify-content:space-between;gap:16px;margin:0 0 8px;flex-wrap:wrap">'
    f'<div><span class="org-mention">{T("org")}</span>'
    f'<div style="font-size:15px;color:#3c4761;font-weight:600;'
    f'margin-top:-2px">{T("titre_site")}</div></div>'
    f'<img src="data:image/png;base64,{assets.LOGO_UNEP}" '
    f'style="height:38px"></div>'
    f'<img src="data:image/jpeg;base64,{assets.PAYSAGE_CAMP_PERRIN}" '
    f'style="width:100%;height:96px;object-fit:cover;object-position:50% 62%;'
    f'border-radius:10px;margin:2px 0 14px">', unsafe_allow_html=True)

# Les deux entrées sont mises au même niveau, en haut de page : ce sont deux
# lectures différentes de la même enquête, pas un mode principal et une option.
# Deux grands pavés cliquables plutôt qu'un bouton radio : l'entrée dans le
# tableau de bord doit se voir de loin.
if "app_mode" not in st.session_state:
    st.session_state["app_mode"] = MODE_ACCUEIL


def _bascule(mode):
    st.session_state["app_mode"] = mode


# Trois entrées d'analyse sur la première rangée, les deux entrées documentaires
# sur la seconde : cinq pavés d'affilée deviendraient trop étroits pour que
# leur intitulé reste lisible.
# La navigation vit dans la barre latérale, groupée : l'entrée générale, les
# six dimensions du cadre, puis ce qui sert à agir et à vérifier. Onze entrées
# en pavés sur la page occupaient un écran entier avant le premier chiffre ;
# en colonne fixe, elles tiennent sans rien pousser vers le bas, et l'onglet
# courant reste visible où qu'on soit dans la page.
_NAV = [
    ("nav_general", [(MODE_ACCUEIL, "◉")]),
    ("nav_dimensions", [(m, i) for m, i in zip(
        MODES_DIM, ["▤", "◈", "❦", "◍", "◎", "✚"])]),
    ("nav_agir", [(MODE_SYNTHESE, "◐"), (MODE_ACTIONS, "➜")]),
    ("nav_verifier", [(MODE_METHODO, "§"), (MODE_DONNEES, "⤓")]),
]


def _entree_nav(mode, icone):
    actif = st.session_state["app_mode"] == mode
    st.button(f"{icone}\u2003{LIBELLE_MODE[mode]}", key=f"nav_{mode}",
              on_click=_bascule, args=(mode,),
              type="primary" if actif else "secondary",
              use_container_width=True)


with _sb_marque:
    st.markdown(
        f'<div class="apri-marque">'
        f'<img src="data:image/png;base64,{assets.LOGO_APRI}">'
        f'<div><div class="apri-nom">APRI</div>'
        f'<div class="apri-baseline">{T("a_accroche")}</div></div></div>',
        unsafe_allow_html=True)

with _sb_nav:
    for cle_groupe, entrees in _NAV:
        st.markdown(f'<div class="nav-groupe">{T(cle_groupe)}</div>',
                    unsafe_allow_html=True)
        for mode, icone in entrees:
            _entree_nav(mode, icone)
    st.markdown('<div class="nav-groupe">' + T("nav_langue") + '</div>',
                unsafe_allow_html=True)

with _sb_langue:
    st.markdown(
        f'<div class="apri-pied">{T("org")}<br>{T("sous_titre_site")}</div>',
        unsafe_allow_html=True)

app_mode = st.session_state["app_mode"]

# Les six onglets de dimension passent tous par le même module ; deux d'entre
# eux prolongent leur page avec un détail qui existait déjà, plutôt que d'en
# dupliquer la logique — l'environnement avec ses onze indicateurs
# satellitaires, le social avec les fiches d'organisations de base.
if app_mode == MODE_ACCUEIL:
    accueil_page.render()

if app_mode in MODES_DIM:
    dimension_page.render(app_mode)
    if app_mode == "dim3":
        environnement_page.render(entete=False)
    elif app_mode == "dim5":
        ocb_page.render(entete=False)

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
