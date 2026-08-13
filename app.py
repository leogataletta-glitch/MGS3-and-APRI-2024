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

import map_render

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

st.title("Enquête ménage 2024 — explorateur interactif")
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

# ---- graphique : répartition sur la population filtrée (colonne Total) ----
chart_rows = []
for label, group_n in theme["rows"]:
    n = group_n.get("Total", 0)
    b = base_n.get("Total", 0)
    pct = round(n / b * 100, 1) if b else 0.0
    chart_rows.append({"Modalité": label, "%": pct})
chart_df = pd.DataFrame(chart_rows).sort_values("%", ascending=True)

st.bar_chart(chart_df.set_index("Modalité"), horizontal=True, color="#2f6690")

# ---- carte : une couleur par seuil, une section communale par forme ----
st.markdown("### Carte par section communale")
row_labels = [lab for lab, _ in theme["rows"]]
map_choice = st.selectbox(
    "Modalité à cartographier", row_labels,
    help="La carte affiche, pour chaque section, la part de foyers ayant cette réponse.")
map_counts = dict(theme["rows"])[map_choice]
map_values = {
    s: (round(map_counts.get(s, 0) / base_n[s] * 100, 1) if base_n.get(s) else None)
    for s in map_render.SECTIONS
}

POLARITY_LABELS = {
    "eleve_mauvais": "Un pourcentage élevé est **défavorable** (vert → rouge)",
    "eleve_bon": "Un pourcentage élevé est **favorable** (rouge → vert)",
    "neutre": "Ni bon ni mauvais — dégradé de bleu",
}
suggestion = map_render.guess_polarity(theme["question"], map_choice)
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

map_height = 660
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
