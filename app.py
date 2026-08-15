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

import assets
import croisement_page
import i18n
import map_render
import methodologie_page
import ocb_page
import resilience_page
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

  /* --- les cartouches de chiffres se soulèvent aussi --- */
  .cartouche { transition: box-shadow .2s ease, transform .2s ease,
                           border-color .2s ease; }
  .cartouche:hover {
    transform: translateY(-3px) !important; border-color: #cddcf0 !important;
    box-shadow: 0 3px 6px rgba(16,23,40,.07), 0 18px 38px rgba(16,23,40,.13) !important;
  }
</style>
""", unsafe_allow_html=True)

st.markdown(map_render.styles_bulle(), unsafe_allow_html=True)

# ---- choix de la langue, avant tout le reste ---------------------------
# Le menu est l'unique source de vérité : on recopie simplement son état dans
# `lang`, que toutes les pages lisent. Pas de rerun forcé — Streamlit relance
# déjà le script quand le menu change, et le reste de la page est construit
# après cette ligne.
_l1, _l2 = st.columns([6, 1])
with _l2:
    _code = st.selectbox(
        T("langue"), list(i18n.LANGUES.keys()),
        format_func=lambda c: i18n.LANGUES[c], key="choix_langue",
        label_visibility="collapsed")
i18n.set_lang(_code)

# ---- bandeau : logo PNUE + les deux entrées du tableau de bord ----------
# Le mode est stocké sous un code stable, pas sous son libellé : sinon un
# changement de langue laisserait dans la session une valeur qui ne correspond
# plus à aucun mode.
MODE_QUESTIONS, MODE_RESILIENCE, MODE_CROISEMENT = "questions", "resilience", "croisement"
MODE_METHODO, MODE_DONNEES = "methodologie", "donnees"
MODE_OCB = "ocb"
LIBELLE_MODE = {MODE_QUESTIONS: T("mode_questions"),
                MODE_RESILIENCE: T("mode_resilience"),
                MODE_CROISEMENT: T("mode_croisement"),
                MODE_METHODO: T("mode_methodo"),
                MODE_DONNEES: T("mode_donnees"),
                MODE_OCB: T("mode_ocb")}

_logo, _entete = st.columns([1, 6])
with _logo:
    st.markdown(
        f'<img src="data:image/png;base64,{assets.LOGO_UNEP}" '
        f'style="width:168px;margin:2px 0 0 2px">', unsafe_allow_html=True)
with _entete:
    st.markdown(
        f'<p class="org-mention">{T("org")}</p>'
        f'<p style="font-size:27px;font-weight:700;letter-spacing:-.02em;'
        f'margin:2px 0 0 2px;color:#101728;line-height:1.2">'
        f'{T("titre_site")}</p>', unsafe_allow_html=True)

# Bandeau : le dessin est rogné en hauteur pour rester un décor, pas une page.
st.markdown(
    f'<img src="data:image/jpeg;base64,{assets.PAYSAGE_CAMP_PERRIN}" '
    f'style="width:100%;height:172px;object-fit:cover;object-position:50% 62%;'
    f'border-radius:10px;margin:8px 0 12px">', unsafe_allow_html=True)

# Les deux entrées sont mises au même niveau, en haut de page : ce sont deux
# lectures différentes de la même enquête, pas un mode principal et une option.
# Deux grands pavés cliquables plutôt qu'un bouton radio : l'entrée dans le
# tableau de bord doit se voir de loin.
if "app_mode" not in st.session_state:
    st.session_state["app_mode"] = MODE_QUESTIONS


def _bascule(mode):
    st.session_state["app_mode"] = mode


# Trois entrées d'analyse sur la première rangée, les deux entrées documentaires
# sur la seconde : cinq pavés d'affilée deviendraient trop étroits pour que
# leur intitulé reste lisible.
_ENTREES = (
    (MODE_QUESTIONS, T("mode_questions_sous")),
    (MODE_RESILIENCE, T("mode_resilience_sous")),
    (MODE_CROISEMENT, T("mode_croisement_sous")),
    (MODE_METHODO, T("mode_methodo_sous")),
    (MODE_OCB, T("mode_ocb_sous")),
    (MODE_DONNEES, T("mode_donnees_sous")),
)


def _pave(col, mode, sous):
    with col:
        st.button(LIBELLE_MODE[mode], key=f"btn_{mode}",
                  on_click=_bascule, args=(mode,),
                  type="primary" if st.session_state["app_mode"] == mode
                  else "secondary",
                  use_container_width=True)
        st.markdown(
            f'<p style="font-size:12.5px;color:#898781;margin:-6px 0 0;'
            f'text-align:center;line-height:1.35">{sous}</p>',
            unsafe_allow_html=True)


_r1 = st.columns(3, gap="medium")
for _col, (_mode, _sous) in zip(_r1, _ENTREES[:3]):
    _pave(_col, _mode, _sous)

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
_r2 = st.columns(3, gap="medium")
for _col, (_mode, _sous) in zip(_r2, _ENTREES[3:]):
    _pave(_col, _mode, _sous)

app_mode = st.session_state["app_mode"]
st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

if app_mode == MODE_RESILIENCE:
    resilience_page.render()
    st.stop()

if app_mode == MODE_CROISEMENT:
    croisement_page.render()
    st.stop()

if app_mode == MODE_METHODO:
    methodologie_page.render()
    st.stop()

if app_mode == MODE_OCB:
    ocb_page.render()
    st.stop()

if app_mode == MODE_DONNEES:
    telechargements_page.render()
    st.stop()

st.subheader(LIBELLE_MODE[MODE_QUESTIONS])
st.caption(T("q_consigne"))

with st.sidebar:
    st.header(T("filtres"))
    f_sexe = st.multiselect(T("sexe"), ["Homme", "Femme"],
                            format_func=lambda x: T("homme") if x == "Homme"
                            else T("femme"))
    f_cat = st.multiselect(T("categorie_eco"), ["A", "B", "C"],
                           format_func=lambda x: {"A": T("cat_a"), "B": T("cat_b"),
                                                  "C": T("cat_c")}[x])
    f_age = st.multiselect(T("groupe_age"), ["<25", "25-39", "40-59", "60+"],
                           format_func=lambda x: {"<25": T("age_25"),
                                                  "25-39": T("age_25_39"),
                                                  "40-59": T("age_40_59"),
                                                  "60+": T("age_60")}[x])
    f_paysage = st.multiselect(T("paysage"), ["Littoral", "Montagne"],
                               format_func=lambda x: T("littoral")
                               if x == "Littoral" else T("montagne"))
    f_sections = st.multiselect(T("section_communale"), list(SECTION_RAW.keys()))

data = compute_filtered(
    tuple(f_sexe), tuple(f_cat), tuple(f_age), tuple(f_paysage), tuple(f_sections)
)
base_n = data["base_n"]
themes = data["themes"]

st.markdown(
    '<div style="background:#fff;border:1px solid #e3eaf3;border-left:5px solid '
    '#1a6bb0;border-radius:14px;padding:13px 17px;font-size:16px;color:#3c4761;'
    'box-shadow:0 1px 2px rgba(16,23,40,.05),0 8px 20px rgba(16,23,40,.06)">'
    + T("q_population", n=base_n["Total"], h=base_n["Homme"], f=base_n["Femme"])
    + "&nbsp;" + map_render.bulle("base", texte="") + '</div>',
    unsafe_allow_html=True)

if base_n["Total"] == 0:
    st.warning(T("q_vide"))
    st.stop()

with st.container(border=True):
    st.markdown(f'<div class="titre-bloc">{T("q_bloc1")}</div>',
                unsafe_allow_html=True)
    index = load_questions_index()

    # Les catégories portent en interne un code de tri hérité des classeurs Excel
    # ("AJ. EAU, ASSAINISSEMENT…"). On ne l'affiche pas, et surtout on garde l'ordre
    # d'apparition dans le questionnaire plutôt qu'un tri alphabétique sur ce code —
    # qui ferait remonter la pêche en tête.
    CAT_CODE = re.compile(r"^[A-Z]{1,3}\.\s*")
    cats_raw = []
    for q in index:
        if q["category"] not in cats_raw:
            cats_raw.append(q["category"])
    cat_display = [CAT_CODE.sub("", c) for c in cats_raw]
    cat_of_display = dict(zip(cat_display, cats_raw))

    chosen = st.selectbox(T("q_categorie"), cat_display,
                          help=T("q_categorie_aide"))
    cat_choice = cat_of_display[chosen]
    q_options = [q for q in index if q["category"] == cat_choice]
    q_labels = [q["question"] for q in q_options]
    q_choice_label = st.selectbox(T("q_question"), q_labels)
    theme_i = next(q["i"] for q in q_options if q["question"] == q_choice_label)
    theme = themes[theme_i]

with st.container(border=True):
    st.markdown(f'<div class="titre-bloc vert">{T("q_bloc2")}</div>',
                unsafe_allow_html=True)
    st.subheader(theme["question"])
    if theme.get("note"):
        _note = theme["note"]
        if "multiple" in _note.lower():
            st.markdown(
                '<p style="font-size:15px;color:#3c4761;margin:0 0 6px">'
                + _note + '&nbsp;'
                + map_render.bulle("réponses multiples", texte="") + '</p>',
                unsafe_allow_html=True)
        else:
            st.caption(_note)

    # ---- les chiffres saillants, en gros, avant tout graphique ----------------
    # Même traitement que sur l'onglet Résilience : on lit d'abord un chiffre, pas
    # un graphique. Ici, les trois réponses les plus fréquentes sur la population
    # filtrée, avec l'effectif qui les porte.
    _base_total = base_n.get("Total", 0)
    _top = sorted(theme["rows"], key=lambda r: -r[1].get("Total", 0))[:3]
    _top = [(lab, g.get("Total", 0)) for lab, g in _top if g.get("Total", 0) > 0]
    if _top and _base_total:
        _teintes = ["#2a78d6", "#5b6b7a", "#898781"]
        _cols = st.columns(len(_top))
        for _c, (_lab, _n), _teinte in zip(_cols, _top, _teintes):
            _pourcent = round(_n / _base_total * 100, 1)
            with _c:
                st.markdown(
                    map_render.cartouche_html(
                        _lab, _pourcent, "%",
                        T("q_soit", n=_n, base=_base_total),
                        couleur=_teinte),
                    unsafe_allow_html=True)
        st.caption(T("q_top3"))

    # ---- graphique : répartition sur la population filtrée (colonne Total) ----
    # Rendu maison plutôt que st.bar_chart : celui-ci impose une graduation d'axe
    # très dense et une couleur peu maîtrisable. Ici la valeur est écrite au bout
    # de chaque barre, donc aucun axe n'est nécessaire.
    bar_rows = [(label, group_n.get("Total", 0)) for label, group_n in theme["rows"]]
    bar_svg = map_render.render_bars_svg(bar_rows, base_n.get("Total", 0))
    n_bars = len(bar_rows)
    components.html(
        f'<div style="background:#ffffff;font-family:system-ui,-apple-system,'
        f'\'Segoe UI\',sans-serif">{bar_svg}</div>',
        height=n_bars * 28 + 26, scrolling=False)

with st.container(border=True):
    st.markdown(f'<div class="titre-bloc ambre">{T("q_bloc3")}</div>',
                unsafe_allow_html=True)
    # ---- carte : une couleur par seuil, une section communale par forme ----
    st.markdown("### " + T("q_carte"))
    row_labels = [lab for lab, _ in theme["rows"]]
    rows_dict = dict(theme["rows"])


    # Bornes chiffrées des modalités. La référence est map_render.lower_bound —
    # la même fonction qui ordonne les barres, pour que graphique et carte ne
    # puissent pas diverger. Les deux définitions de secours ci-dessous ne servent
    # qu'au cas où map_render.py serait resté sur une version plus ancienne : sans
    # elles, l'app planterait au lieu de simplement perdre le tri des barres.
    _ESPACE_MILLIERS = re.compile(r"(?<=\d)[\s  ](?=\d)")
    _ZERO_DEBUT = ("aucun", "aucune", "moins de", "inférieur", "inferieur", "pas de")


    def _lower_bound_local(label):
        s = _ESPACE_MILLIERS.sub("", str(label).strip().lower())
        if s.startswith(_ZERO_DEBUT):
            return 0
        m = re.search(r"\d+", s)
        return int(m.group()) if m else None


    lower_bound = getattr(map_render, "lower_bound", _lower_bound_local)

    nums = {lab: lower_bound(lab) for lab in row_labels}
    chiffrees = [lab for lab in row_labels if nums[lab] is not None]
    bornes = [nums[lab] for lab in chiffrees]
    is_numeric = len(chiffrees) >= 3 and len(set(bornes)) == len(bornes)

    # Une question à choix unique répartit chaque foyer dans une seule modalité :
    # les cumuler est donc exact. Sur une question à choix multiples, un même foyer
    # peut apparaître dans plusieurs, et la somme dépasserait le compte réel.
    somme_pct = (sum(g.get("Total", 0) for _, g in theme["rows"]) / base_n["Total"] * 100
                 if base_n.get("Total") else 0)
    choix_multiple = somme_pct > 101

    mode = "liste"
    if is_numeric:
        mode = st.radio(
            T("q_quoi_carto"),
            ["seuil", "liste"],
            format_func=lambda k: {"seuil": T("q_mode_seuil"),
                                   "liste": T("q_mode_liste")}[k],
            horizontal=True, key=f"mode_{theme_i}_{i18n.get_lang()}")

    if mode == "seuil":
        paliers = sorted(bornes)[1:]            # la borne la plus basse ne filtre rien
        seuil = st.selectbox(T("q_seuil"), paliers,
                             format_func=lambda v: T("q_seuil_fmt", v=v),
                             key=f"seuil_{theme_i}")
        selection = [lab for lab in chiffrees if nums[lab] >= seuil]
        map_choice = T("q_seuil_fmt", v=seuil)
        st.caption(T("q_cumule") + ", ".join(f"« {lab} »" for lab in selection))
        hors = [lab for lab in row_labels if nums[lab] is None]
        if hors:
            st.caption(T("q_hors") + ", ".join(f"« {lab} »" for lab in hors))
    else:
        selection = st.multiselect(
            T("q_reponses_carto"), row_labels, default=[row_labels[0]],
            key=f"sel_{theme_i}", help=T("q_reponses_aide"))
        map_choice = " + ".join(selection)

    if not selection:
        st.info(T("q_choisir_reponse"))
        st.stop()

    if len(selection) > 1 and choix_multiple:
        st.warning(T("q_avert_multi"))

    map_counts = {g: sum(rows_dict[lab].get(g, 0) for lab in selection)
                  for g in map_render.SECTIONS}
    map_values = {
        s: (round(map_counts.get(s, 0) / base_n[s] * 100, 1) if base_n.get(s) else None)
        for s in map_render.SECTIONS
    }
    if mode != "seuil" and len(selection) > 1:
        st.caption(T("q_cumule") + ", ".join(f"« {lab} »" for lab in selection))

    POLARITY_LABELS = {
        "eleve_mauvais": T("pol_mauvais"),
        "eleve_bon": T("pol_bon"),
        "neutre": T("pol_neutre"),
    }
    suggestion = map_render.guess_polarity(theme["question"], selection[0])
    pol_key = f"pol_{theme_i}_{map_choice}_{i18n.get_lang()}"
    polarity = st.radio(
        T("sens_couleurs"),
        list(POLARITY_LABELS.keys()),
        index=list(POLARITY_LABELS.keys()).index(suggestion),
        format_func=lambda k: POLARITY_LABELS[k],
        horizontal=True, key=pol_key,
        help=T("pol_aide"))

    with st.expander(T("regler_seuils")):
        auto = st.checkbox(T("seuils_auto"), value=True)
        auto_T = map_render.nice_thresholds([v for v in map_values.values() if v is not None])
        if auto:
            thresholds = auto_T
        else:
            c1, c2, c3 = st.columns(3)
            thresholds = [
                c1.number_input(T("seuil_n", i=1), value=float(auto_T[0]), step=1.0),
                c2.number_input(T("seuil_n", i=2), value=float(auto_T[1]), step=1.0),
                c3.number_input(T("seuil_n", i=3), value=float(auto_T[2]), step=1.0),
            ]
            thresholds = sorted(thresholds)

    map_height = 720
    svg, seuils_ret, mode = map_render.render_map_svg(
        map_values, base_n, thresholds, height=map_height, polarity=polarity)

    legend_html = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:7px;margin-right:18px">'
        f'<span style="width:22px;height:12px;border-radius:3px;background:{c};'
        f'box-shadow:inset 0 0 0 1px rgba(0,0,0,.12)"></span>'
        f'<span style="font-size:13px;color:#52514e">{lab}</span></span>'
        for c, lab in map_render.legend_items(seuils_ret, polarity))

    # Streamlit assainit le SVG inséré via st.markdown (il vide les <circle>/<text>) :
    # on passe donc par un composant HTML isolé, qui rend le SVG tel quel.
    components.html(
        f"""<div style="font-family:system-ui,-apple-system,'Segoe UI',sans-serif;
                        background:#ffffff">
          <div style="margin:0 0 8px"><span style="font-size:11.5px;color:#898781;
            letter-spacing:.05em;margin-right:14px">{T("legende_seuils")}</span>{legend_html}</div>
          {svg}
        </div>""",
        height=map_height + 46, scrolling=False)

    st.caption(map_render.polarity_caption(polarity))

    if mode == "disques":
        st.caption(
            T("contours_disques"))
    else:
        st.caption(T("contours_officiels"))

with st.container(border=True):
    st.markdown(f'<div class="titre-bloc">{T("q_bloc4")}</div>',
                unsafe_allow_html=True)
    # ---- tableau détaillé avec tous les sous-groupes ----
    st.markdown("**" + T("q_detail") + "**")
    detail_df = rows_to_dataframe(theme, base_n)
    st.dataframe(detail_df, use_container_width=True, hide_index=True)

    st.download_button(
        T("q_telecharger_xlsx"),
        data=export_excel(theme, base_n),
        file_name="resultat_filtre.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

st.caption(T("q_source"))
st.caption(T("credit"))
