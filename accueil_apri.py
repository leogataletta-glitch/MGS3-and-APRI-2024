
import os
import json
import streamlit as st
import i18n
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

SECTIONS = [
    "Anse à Drick", "Barbois", "Dumont", "Débouchette", "Mouline",
    "Quentin", "Beaulieu", "Blactote", "Dalmette", "Trichet"
]

TEXTES = {
    "mode_portail": {"en": "Home", "fr": "Accueil"},
    "e1": {"en": "The study area", "fr": "Le territoire"},
    "e1s": {"en": "Where?", "fr": "Où ?"},
    "e2": {"en": "Methodology", "fr": "Méthodologie"},
    "e2s": {"en": "What was measured?", "fr": "Qu'a-t-on mesuré ?"},
    "study_title": {"en": "The study area", "fr": "Le territoire d'étude"},
    "study_b1": {"en": "Two pilot areas: Grand'Anse and Sud", "fr": "Deux zones pilotes : Grand'Anse et Sud"},
    "study_b2": {"en": "{n} communal sections selected within them", "fr": "{n} sections communales sélectionnées en leur sein"},
    "study_b3": {"en": "{n} households surveyed", "fr": "{n} ménages enquêtés"},
    "sections": {"en": "THE TEN COMMUNAL SECTIONS", "fr": "LES DIX SECTIONS COMMUNALES"},
    "section_note": {"en": "The figure beside each name is the number of households surveyed there.", "fr": "Le chiffre indiqué à côté de chaque nom correspond au nombre de ménages enquêtés."},
    "map_caption": {"en": "The surveyed area, in the far south-west of the country.", "fr": "La zone enquêtée, à l'extrême sud-ouest du pays."},
    "method_title": {"en": "Methodology of the survey", "fr": "Méthodologie de l'enquête"},
    "method_house_title": {"en": "Household survey", "fr": "Enquête ménage"},
    "method_house_p1": {"en": "The household survey is the main source of information on living conditions, livelihoods, risk perception and families' capacity to anticipate shocks.", "fr": "L'enquête ménage constitue la principale source d'information sur les conditions de vie, les moyens d'existence, la perception des risques et la capacité d'anticipation des familles."},
    "method_house_p2": {"en": "A stratified sampling plan was established to ensure balanced representation of different areas, landscape types and socio-economic contexts.", "fr": "Un plan d'échantillonnage stratifié a été mis en place pour assurer une représentation équilibrée des différentes zones, des types de paysage et des contextes socio-économiques."},
    "method_house_p3": {"en": "Within each stratum, households were selected through random geolocation from a georeferenced building database, ensuring objectivity and representativeness.", "fr": "À l'intérieur de chaque strate, la sélection des ménages a été réalisée par localisation aléatoire à partir d'une base de bâtiments géoréférencés, garantissant l'objectivité et la représentativité de l'échantillon."},
    "method_sat_title": {"en": "Satellite imagery", "fr": "Imagerie satellitaire"},
    "method_sat_p1": {"en": "High-resolution multispectral satellite imagery was used to characterise land cover and land use, track vegetation dynamics and identify landscape changes over time.", "fr": "Des images satellitaires multispectrales à haute résolution ont été utilisées pour caractériser l'occupation et l'utilisation des terres, suivre l'évolution du couvert végétal et des changements paysagers au cours du temps."},
    "method_sat_p2": {"en": "Spatial analysis produced objective environmental indicators at the scale of communal sections and landscapes.", "fr": "L'analyse spatiale a permis de produire des indicateurs environnementaux objectifs à l'échelle des sections communales et des paysages."},
    "method_bio_title": {"en": "In-situ biodiversity measurements", "fr": "Mesures in situ de la biodiversité"},
    "method_bio_p1": {"en": "Field surveys were conducted to document biodiversity through flora and fauna inventories, habitat observations and key ecological measurements.", "fr": "Des relevés de terrain ont été réalisés pour documenter la biodiversité à travers des inventaires de flore et de faune, des observations d'habitats et des mesures écologiques clés."},
    "method_bio_p2": {"en": "These in-situ data complement information from other sources and make it possible to assess the condition and dynamics of biodiversity in the study territories.", "fr": "Ces données in situ viennent compléter les informations issues des autres sources et permettent d'évaluer l'état et la dynamique de la biodiversité dans les territoires étudiés."},
    "previous": {"en": "Previous", "fr": "Précédent"},
    "next": {"en": "Next", "fr": "Suivant"},
}

for key, value in TEXTES.items():
    i18n.DICO.setdefault(key, value)

STYLE = """
<style>
/* Clean two-step navigation */
div[data-testid="stHorizontalBlock"] button[kind="primary"],
div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
    width:100%;
    min-height:72px;
    border:1px solid #e1e7ee;
    border-radius:10px 10px 0 0;
    background:#ffffff;
    color:#101728;
    font-family:Arial,sans-serif;
    font-size:16px;
    font-weight:600;
    box-shadow:none;
    transition:none;
}
div[data-testid="stHorizontalBlock"] button[kind="primary"] {
    border-bottom:3px solid #1c6349;
    color:#155c37;
    background:#ffffff;
}
div[data-testid="stHorizontalBlock"] button:hover {
    border-color:#d7e2dc;
    color:#155c37;
    background:#ffffff;
}
div[data-testid="stHorizontalBlock"] button p {
    margin:0;
}
.apri-panel {
    border:1px solid #e1e7ee;
    border-radius:10px;
    background:#fff;
    padding:24px 26px 22px;
    box-sizing:border-box;
}
.apri-title {
    font-family:Georgia,"Times New Roman",serif;
    font-size:29px;
    font-weight:400;
    color:#101728;
    margin:0;
}
.apri-rule {
    width:42px;
    height:2px;
    background:#2f6b4f;
    margin:12px 0 20px;
}
.apri-columns {
    display:grid;
    grid-template-columns:repeat(3,1fr);
}
.apri-column {
    padding:0 30px;
    border-left:1px solid #e2e8ef;
}
.apri-column:first-child {
    padding-left:0;
    border-left:none;
}
.apri-column:last-child {
    padding-right:0;
}
.apri-column h3 {
    color:#155c37;
    font-size:19px;
    margin:0 0 18px;
}
.apri-column p {
    color:#182132;
    font-family:Georgia,"Times New Roman",serif;
    font-size:16px;
    line-height:1.55;
    text-align:justify;
    margin:0 0 18px;
}
@media(max-width:900px) {
    .apri-columns {grid-template-columns:1fr}
    .apri-column {
        border-left:none;
        border-top:1px solid #e2e8ef;
        padding:20px 0;
    }
    .apri-column:first-child {border-top:none}
}
</style>
"""

def _e(value):
    return str(value).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def _find_file(name):
    for path in (os.path.join(DATA,name), os.path.join(APP_DIR,name)):
        if os.path.exists(path):
            return path
    return None

@st.cache_data(show_spinner=False)
def _households():
    path = _find_file("croisement_index.json")
    if path:
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            if data.get("n"):
                return int(data["n"])
        except Exception:
            pass
    return 1211

@st.cache_data(show_spinner=False)
def _section_counts():
    return {"Anse à Drick":121,"Barbois":121,"Beaulieu":121,"Blactote":120,"Dalmette":125,
            "Dumont":122,"Débouchette":120,"Mouline":120,"Quentin":116,"Trichet":120}

def _set_step(n):
    st.session_state["portail_etape"] = n

def _step_buttons():
    current = int(st.session_state.get("portail_etape", 1))
    cols = st.columns(2, gap="small")

    with cols[0]:
        st.button(
            T("e1"),
            key="apri_step_1",
            on_click=_set_step,
            args=(1,),
            type="primary" if current == 1 else "secondary",
            use_container_width=True,
        )

    with cols[1]:
        st.button(
            T("e2"),
            key="apri_step_2",
            on_click=_set_step,
            args=(2,),
            type="primary" if current == 2 else "secondary",
            use_container_width=True,
        )

def _study_area():
    households=_households()
    counts=_section_counts()
    left,right=st.columns([1.05,1.25],gap="large")
    with left:
        rows=[]
        a=["Anse à Drick","Barbois","Beaulieu","Blactote","Dalmette"]
        b=["Dumont","Débouchette","Quentin","Trichet","Mouline"]
        for x,y in zip(a,b):
            rows.append(f"<div style='display:grid;grid-template-columns:1fr 45px 1fr 45px;min-height:31px;align-items:center;border-top:1px solid #eef2f6;font-size:12.5px'><span>{_e(x)}</span><span style='text-align:right'>{counts[x]}</span><span style='padding-left:18px'>{_e(y)}</span><span style='text-align:right'>{counts[y]}</span></div>")
        html=f"""
        <div class="apri-panel">
        <div class="apri-title">{_e(T("study_title"))}</div><div class="apri-rule"></div>
        <ul style="list-style:none;padding:0;margin:0 0 24px">
        <li style="margin-bottom:18px;color:#2b3444;font-size:14px">■ &nbsp;{_e(T("study_b1"))}</li>
        <li style="margin-bottom:18px;color:#2b3444;font-size:14px">■ &nbsp;{_e(T("study_b2",n=10))}</li>
        <li style="color:#2b3444;font-size:14px">■ &nbsp;{_e(T("study_b3",n=f"{households:,}".replace(","," ")))}</li>
        </ul>
        <div style="font-size:10px;font-weight:700;letter-spacing:.12em;color:#8a93a5;margin-bottom:8px">{_e(T("sections"))}</div>
        {''.join(rows)}
        <div style="font-size:11.5px;color:#6b7590;margin-top:8px">{_e(T("section_note"))}</div>
        </div>
        """
        st.markdown(html,unsafe_allow_html=True)
    with right:
        try:
            import territoire_page
            vignette=territoire_page._vignette(territoire_page._geo(),520,370)
            st.markdown('<div class="apri-panel" style="padding:10px">'+(vignette or "")+
                        f'<div style="font-size:12px;color:#6b7590;margin-top:8px">{_e(T("map_caption"))}</div></div>',
                        unsafe_allow_html=True)
        except Exception:
            st.info(T("map_caption"))

def _methodology():
    st.markdown(f"""
    <div class="apri-panel">
    <div class="apri-title">{_e(T("method_title"))}</div>
    <div class="apri-rule"></div>
    <div class="apri-columns">
      <div class="apri-column">
        <h3>{_e(T("method_house_title"))}</h3>
        <p>{_e(T("method_house_p1"))}</p>
        <p>{_e(T("method_house_p2"))}</p>
        <p>{_e(T("method_house_p3"))}</p>
      </div>
      <div class="apri-column">
        <h3>{_e(T("method_sat_title"))}</h3>
        <p>{_e(T("method_sat_p1"))}</p>
        <p>{_e(T("method_sat_p2"))}</p>
      </div>
      <div class="apri-column">
        <h3>{_e(T("method_bio_title"))}</h3>
        <p>{_e(T("method_bio_p1"))}</p>
        <p>{_e(T("method_bio_p2"))}</p>
      </div>
    </div>
    </div>
    """,unsafe_allow_html=True)
    img=_find_file("carte_entretiens.jpg")
    if img:
        st.image(img,use_container_width=True)

def _footer(current):
    c1, c2 = st.columns(2, gap="small")
    with c1:
        if current == 2:
            st.button(
                "← " + T("previous"),
                key="apri_previous",
                on_click=_set_step,
                args=(1,),
                use_container_width=False,
            )
    with c2:
        if current == 1:
            st.button(
                T("next") + " →",
                key="apri_next",
                on_click=_set_step,
                args=(2,),
                use_container_width=False,
            )

def render():
    st.markdown(STYLE,unsafe_allow_html=True)
    st.session_state.setdefault("portail_etape",1)
    current=int(st.session_state["portail_etape"])
    if current not in (1,2):
        current=1
        st.session_state["portail_etape"]=1

    _step_buttons()

    if current == 1:
        _study_area()
    else:
        _methodology()

    _footer(current)
