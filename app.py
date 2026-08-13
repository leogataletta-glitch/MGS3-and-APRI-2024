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
import map_render
import resilience_page

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
    st.title("Enquête ménage 2024")
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
        row = {"Modalité": label}
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
        df.to_excel(writer, sheet_name="Résultat", index=False)
    buf.seek(0)
    return buf


# ----------------------------------------------------------------------
st.set_page_config(page_title="Enquête ménage 2024", layout="wide")

if not check_password():
    st.stop()

# Typographie de toute l'application. Deux principes : une seule famille
# (Roboto, la police institutionnelle du PNUE, avec repli système si la
# connexion aux polices Google échoue), et une largeur de ligne bornée —
# une phrase qui court sur 1400 px est illisible, c'est ce qui rendait les
# blocs de texte pénibles à lire.
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Roboto+Condensed:wght@600;700&display=swap');

  html, body, [class*="css"], .stApp {
    font-family: "Roboto", system-ui, -apple-system, "Segoe UI", sans-serif;
  }

  /* Une colonne de lecture, pas toute la largeur de l'écran. */
  .block-container {
    max-width: 1180px; padding-top: 2.2rem; padding-bottom: 4rem;
  }

  /* --- titres : condensé, serré, hiérarchie nette --- */
  h1, h2, h3 {
    font-family: "Roboto Condensed", "Segoe UI Semibold", "Arial Narrow",
                 system-ui, sans-serif !important;
    letter-spacing: -0.012em; color: #16161a;
  }
  h1 { font-weight: 700 !important; font-size: 2.4rem !important;
       padding-bottom: .1rem !important; }
  h2 { font-weight: 700 !important; font-size: 1.72rem !important;
       margin-top: 2.1rem !important; padding-bottom: .1rem !important; }
  h3 { font-weight: 700 !important; font-size: 1.34rem !important;
       margin-top: 1.7rem !important; }

  /* --- texte courant : plus grand, plus aéré, ligne bornée --- */
  [data-testid="stMarkdownContainer"] p {
    font-size: 16.5px; line-height: 1.62; color: #2b2b30;
  }
  [data-testid="stMarkdownContainer"] li {
    font-size: 16.5px; line-height: 1.6; color: #2b2b30; margin-bottom: .3rem;
  }

  /* --- légendes : le commentaire de lecture, pas le texte principal --- */
  [data-testid="stCaptionContainer"] p {
    font-size: 14.5px !important; line-height: 1.58 !important;
    color: #5c5c63 !important; max-width: 92ch;
  }

  /* --- libellés des menus : lisibles, pas minuscules --- */
  label[data-testid="stWidgetLabel"] p {
    font-size: 15px !important; font-weight: 600 !important; color: #2b2b30;
  }
  div[data-baseweb="select"] > div { font-size: 15.5px; }

  /* --- l'encadré « population filtrée » : un bandeau, pas une alerte --- */
  div[data-testid="stAlert"] {
    border-radius: 8px; border-left: 5px solid #1a6bb0;
    background: #f2f7fc; padding: 4px 6px;
  }
  div[data-testid="stAlert"] > div {
    background: transparent !important; border: none !important;
    padding: 10px 12px !important;
  }
  div[data-testid="stAlert"] p {
    font-size: 16px !important; color: #22303d !important; margin: 0;
  }

  /* --- volets dépliants --- */
  details summary p { font-size: 15.5px !important; font-weight: 600 !important; }

  .org-mention {
    font-size: 12.5px; color: #52514e; letter-spacing: .07em;
    text-transform: uppercase; margin: 0 0 2px 2px; font-weight: 500;
  }

  /* Les deux entrées du tableau de bord sont le premier choix de la page :
     deux grands pavés, pas un réglage secondaire. */
  div[data-testid="stButton"] > button {
    height: 78px; border-radius: 10px; border-width: 2px;
    font-size: 18.5px !important; font-weight: 700 !important;
    line-height: 1.3; white-space: normal; padding: 10px 18px;
    font-family: "Roboto Condensed", system-ui, sans-serif !important;
    letter-spacing: .005em;
  }
  div[data-testid="stButton"] > button p {
    font-size: 18.5px !important; font-weight: 700 !important;
  }
  /* Pavé actif : bleu PNUE assombri pour tenir 5,6:1 avec le texte blanc.
     Pavé inactif : fond clair, bordure nette — il doit rester cliquable à l'œil. */
  div[data-testid="stButton"] > button[kind="primary"] {
    background: #1a6bb0 !important; border-color: #1a6bb0 !important;
    color: #ffffff !important;
  }
  div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #15619f !important; border-color: #15619f !important;
  }
  div[data-testid="stButton"] > button[kind="secondary"] {
    background: #ffffff !important; border-color: #c9ccd1 !important;
    color: #0b0b0b !important;
  }
  div[data-testid="stButton"] > button[kind="secondary"]:hover {
    border-color: #1a6bb0 !important; color: #1a6bb0 !important;
  }
  /* Les radios internes (niveau de lecture, couche de la carte) restent
     lisibles mais discrets. */
  .stRadio > div[role="radiogroup"] > label > div:last-child p {
    font-size: 15px !important; font-weight: 600 !important;
  }

  /* --- barre latérale --- */
  section[data-testid="stSidebar"] { background: #f6f6f4; }
  section[data-testid="stSidebar"] h2 {
    font-size: 1.25rem !important; margin-top: .4rem !important;
  }
</style>
""", unsafe_allow_html=True)

# ---- bandeau : logo PNUE + les deux entrées du tableau de bord ----------
MODE_QUESTIONS = "Résultats de toutes les questions aux 1200 ménages"
MODE_RESILIENCE = "Indicateurs de résilience associés"

_logo, _entete = st.columns([1, 8])
with _logo:
    st.markdown(
        f'<img src="data:image/png;base64,{assets.LOGO_UNEP}" '
        f'style="width:96px;margin:2px 0 0 2px">', unsafe_allow_html=True)
with _entete:
    st.markdown(
        '<p class="org-mention">Programme des Nations Unies pour '
        "l'environnement — PNUE / UNEP</p>"
        '<p style="font-size:26px;font-weight:650;letter-spacing:-.015em;'
        'margin:2px 0 0 2px;color:#0b0b0b">Enquête ménage 2024 — '
        "Sud et Grand'Anse</p>", unsafe_allow_html=True)

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


_c1, _c2 = st.columns(2, gap="medium")
for _col, _mode, _sous in (
        (_c1, MODE_QUESTIONS,
         "Les 503 questions posées, filtrables par sexe, âge, "
         "niveau socio-économique et paysage"),
        (_c2, MODE_RESILIENCE,
         "Les indicateurs consolidés et leur score IRLA / APRI, "
         "par section communale et sous-population")):
    with _col:
        st.button(_mode, key=f"btn_{_mode[:12]}", on_click=_bascule, args=(_mode,),
                  type="primary" if st.session_state["app_mode"] == _mode
                  else "secondary",
                  use_container_width=True)
        st.markdown(
            f'<p style="font-size:12.5px;color:#898781;margin:-6px 0 0;'
            f'text-align:center;line-height:1.35">{_sous}</p>',
            unsafe_allow_html=True)

app_mode = st.session_state["app_mode"]
st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

if app_mode == MODE_RESILIENCE:
    resilience_page.render()
    st.stop()

st.subheader("Résultats de toutes les questions aux 1200 ménages")
st.caption(
    "Choisissez une ou plusieurs valeurs par filtre (les filtres se combinent : "
    "ex. Femmes ET Catégorie A ET section Quentin en même temps). "
    "Laissez un filtre vide pour ne pas restreindre sur ce critère."
)

with st.sidebar:
    st.header("Filtres")
    f_sexe = st.multiselect("Sexe", ["Homme", "Femme"])
    f_cat = st.multiselect("Catégorie économique", ["A", "B", "C"],
                            format_func=lambda x: {"A": "Cat A — pauvreté extrême",
                                                    "B": "Cat B — pauvreté",
                                                    "C": "Cat C — non pauvre"}[x])
    f_age = st.multiselect("Groupe d'âge", ["<25", "25-39", "40-59", "60+"])
    f_paysage = st.multiselect("Paysage", ["Littoral", "Montagne"])
    f_sections = st.multiselect("Section communale", list(SECTION_RAW.keys()))

data = compute_filtered(
    tuple(f_sexe), tuple(f_cat), tuple(f_age), tuple(f_paysage), tuple(f_sections)
)
base_n = data["base_n"]
themes = data["themes"]

st.info(f"Population filtrée : **{base_n['Total']} répondants** "
        f"(sur 1211 au total) — Hommes {base_n['Homme']} · Femmes {base_n['Femme']}")

if base_n["Total"] == 0:
    st.warning("Aucun répondant ne correspond à cette combinaison de filtres.")
    st.stop()

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

chosen = st.selectbox("Catégorie de questions", cat_display,
                      help="Les catégories suivent l'ordre du questionnaire.")
cat_choice = cat_of_display[chosen]
q_options = [q for q in index if q["category"] == cat_choice]
q_labels = [q["question"] for q in q_options]
q_choice_label = st.selectbox("Question", q_labels)
theme_i = next(q["i"] for q in q_options if q["question"] == q_choice_label)
theme = themes[theme_i]

st.subheader(theme["question"])
if theme.get("note"):
    st.caption(theme["note"])

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
                    f"soit {_n} répondants sur {_base_total}",
                    couleur=_teinte),
                unsafe_allow_html=True)
    st.caption(
        "Les trois réponses les plus fréquentes sur la population filtrée. "
        "Sur une question à choix multiples, un même foyer peut être compté "
        "dans plusieurs réponses : les pourcentages ne totalisent alors pas 100 %. "
        "Le détail complet est plus bas.")

# ---- graphique : répartition sur la population filtrée (colonne Total) ----
# Rendu maison plutôt que st.bar_chart : celui-ci impose une graduation d'axe
# très dense et une couleur peu maîtrisable. Ici la valeur est écrite au bout
# de chaque barre, donc aucun axe n'est nécessaire.
bar_rows = [(label, group_n.get("Total", 0)) for label, group_n in theme["rows"]]
bar_svg = map_render.render_bars_svg(bar_rows, base_n.get("Total", 0))
n_bars = len(bar_rows)
components.html(
    f'<div style="background:#fcfcfb;font-family:system-ui,-apple-system,'
    f'\'Segoe UI\',sans-serif">{bar_svg}</div>',
    height=n_bars * 28 + 26, scrolling=False)

# ---- carte : une couleur par seuil, une section communale par forme ----
st.markdown("### Carte par section communale")
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
        "Que cartographier",
        ["seuil", "liste"],
        format_func=lambda k: {"seuil": "Un seuil : « X et plus »",
                               "liste": "Une ou plusieurs valeurs précises"}[k],
        horizontal=True, key=f"mode_{theme_i}")

if mode == "seuil":
    paliers = sorted(bornes)[1:]            # la borne la plus basse ne filtre rien
    seuil = st.selectbox("Seuil", paliers, format_func=lambda v: f"{v} et plus",
                         key=f"seuil_{theme_i}")
    selection = [lab for lab in chiffrees if nums[lab] >= seuil]
    map_choice = f"{seuil} et plus"
    st.caption("Cumule : " + ", ".join(f"« {lab} »" for lab in selection))
    hors = [lab for lab in row_labels if nums[lab] is None]
    if hors:
        st.caption("Non comptées (réponses non chiffrées) : "
                   + ", ".join(f"« {lab} »" for lab in hors))
else:
    selection = st.multiselect(
        "Réponse(s) à cartographier", row_labels, default=[row_labels[0]],
        key=f"sel_{theme_i}",
        help="Sélectionnez-en plusieurs pour les cumuler "
             "(ex. « Latrines à fosse sans dalle » + « Aucun »).")
    map_choice = " + ".join(selection)

if not selection:
    st.info("Choisissez au moins une réponse pour afficher la carte.")
    st.stop()

if len(selection) > 1 and choix_multiple:
    st.warning(
        "Cette question accepte plusieurs réponses par foyer : en cumuler "
        "plusieurs compte deux fois les foyers qui en ont coché plus d'une. "
        "Le total affiché est donc un maximum, pas un effectif exact.")

map_counts = {g: sum(rows_dict[lab].get(g, 0) for lab in selection)
              for g in map_render.SECTIONS}
map_values = {
    s: (round(map_counts.get(s, 0) / base_n[s] * 100, 1) if base_n.get(s) else None)
    for s in map_render.SECTIONS
}
if mode != "seuil" and len(selection) > 1:
    st.caption("Cumule : " + ", ".join(f"« {lab} »" for lab in selection))

POLARITY_LABELS = {
    "eleve_mauvais": "Un pourcentage élevé est **défavorable** (vert → rouge)",
    "eleve_bon": "Un pourcentage élevé est **favorable** (rouge → vert)",
    "neutre": "Ni bon ni mauvais — dégradé de bleu",
}
suggestion = map_render.guess_polarity(theme["question"], selection[0])
pol_key = f"pol_{theme_i}_{map_choice}"
polarity = st.radio(
    "Sens de lecture des couleurs",
    list(POLARITY_LABELS.keys()),
    index=list(POLARITY_LABELS.keys()).index(suggestion),
    format_func=lambda k: POLARITY_LABELS[k],
    horizontal=True, key=pol_key,
    help="Proposé automatiquement d'après l'intitulé de la question. "
         "Aucune règle n'étant fiable sur les 503 questions, vérifiez-le et "
         "corrigez-le si besoin.")

with st.expander("Régler les seuils de couleur"):
    auto = st.checkbox("Seuils automatiques", value=True)
    auto_T = map_render.nice_thresholds([v for v in map_values.values() if v is not None])
    if auto:
        thresholds = auto_T
    else:
        c1, c2, c3 = st.columns(3)
        thresholds = [
            c1.number_input("Seuil 1", value=float(auto_T[0]), step=1.0),
            c2.number_input("Seuil 2", value=float(auto_T[1]), step=1.0),
            c3.number_input("Seuil 3", value=float(auto_T[2]), step=1.0),
        ]
        thresholds = sorted(thresholds)

map_height = 720
svg, T, mode = map_render.render_map_svg(
    map_values, base_n, thresholds, height=map_height, polarity=polarity)

legend_html = "".join(
    f'<span style="display:inline-flex;align-items:center;gap:7px;margin-right:18px">'
    f'<span style="width:22px;height:12px;border-radius:3px;background:{c};'
    f'box-shadow:inset 0 0 0 1px rgba(0,0,0,.12)"></span>'
    f'<span style="font-size:13px;color:#52514e">{lab}</span></span>'
    for c, lab in map_render.legend_items(T, polarity))

# Streamlit assainit le SVG inséré via st.markdown (il vide les <circle>/<text>) :
# on passe donc par un composant HTML isolé, qui rend le SVG tel quel.
components.html(
    f"""<div style="font-family:system-ui,-apple-system,'Segoe UI',sans-serif;
                    background:#fcfcfb">
      <div style="margin:0 0 8px"><span style="font-size:11.5px;color:#898781;
        letter-spacing:.05em;margin-right:14px">SEUILS</span>{legend_html}</div>
      {svg}
    </div>""",
    height=map_height + 46, scrolling=False)

st.caption(map_render.polarity_caption(polarity))

if mode == "disques":
    st.caption(
        "Chaque disque représente une section communale, placée à sa position "
        "géographique réelle (nord en haut, distances respectées) ; les disques qui se "
        "superposaient ont été légèrement écartés. Ce ne sont pas les limites "
        "administratives officielles — déposez un fichier "
        "`data/sections_communales.geojson` dans le projet et la carte affichera "
        "automatiquement les vrais contours.")
else:
    st.caption("Contours administratifs officiels des sections communales.")

# ---- tableau détaillé avec tous les sous-groupes ----
st.markdown("**Détail par sous-groupe**")
detail_df = rows_to_dataframe(theme, base_n)
st.dataframe(detail_df, use_container_width=True, hide_index=True)

st.download_button(
    "Télécharger ce tableau (Excel)",
    data=export_excel(theme, base_n),
    file_name="resultat_filtre.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.caption("Source : Données brutes V3, enquête ménage sept. 2024. "
           "Les pourcentages sont calculés sur la base du groupe filtré affiché ci-dessus, "
           "pas sur l'ensemble des 1211 répondants.")
st.caption("Travail réalisé par le Programme des Nations Unies pour "
           "l'environnement (PNUE / UNEP).")
