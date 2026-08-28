"""
APRI — Home / Accueil
Two-step landing page: Study area + Methodology.
"""

import os
import streamlit as st
import i18n
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

TEXTES = {
    "mode_portail": {"en": "Home", "fr": "Accueil"},
    "e1": {"en": "The study area", "fr": "Le territoire"},
    "e1s": {"en": "Where?", "fr": "Où ?"},
    "e2": {"en": "Methodology", "fr": "Méthodologie"},
    "e2s": {"en": "What was measured?", "fr": "Qu'a-t-on mesuré ?"},
    "study_title": {"en": "The study area", "fr": "Le territoire d'étude"},
    "study_b1": {"en": "Two pilot areas: Grand'Anse and Sud", "fr": "Deux zones pilotes : Grand'Anse et Sud"},
    "study_b2": {"en": "10 communal sections selected within them", "fr": "10 sections communales sélectionnées en leur sein"},
    "study_b3": {"en": "1 211 households surveyed", "fr": "1 211 ménages enquêtés"},
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

st.markdown("""
<style>
.block-container{padding-top:.8rem;padding-bottom:2rem;max-width:1450px}
.apri-tabs{display:grid;grid-template-columns:1fr 1fr;gap:34px;margin:8px 0 26px}
.apri-tab{display:block;text-decoration:none!important;text-align:center;color:#111827!important;font-family:Arial,sans-serif;font-size:15px;font-weight:600;padding:13px 10px 15px;border-bottom:1px solid #dfe5e2;background:transparent}
.apri-tab:hover{color:#155c37!important}
.apri-tab-active{color:#155c37!important;border-bottom:3px solid #1c6349}
.apri-panel{background:transparent;border:none;padding:0;margin:0}
.apri-title{font-family:Georgia,"Times New Roman",serif;font-size:30px;font-weight:400;line-height:1.15;color:#101728;margin:0}
.apri-rule{width:42px;height:2px;background:#2f6b4f;margin:12px 0 22px}
.apri-bullets{list-style:none;padding:0;margin:0 0 28px}
.apri-bullets li{position:relative;padding-left:18px;margin-bottom:18px;color:#263244;font-size:14px;line-height:1.5}
.apri-bullets li:before{content:"";position:absolute;left:0;top:.62em;width:5px;height:5px;background:#2f6b4f}
.apri-section-label{font-size:10px;font-weight:700;letter-spacing:.12em;color:#718096;margin-bottom:8px}
.apri-table{width:100%;border-top:1px solid #dfe5e2}
.apri-row{display:grid;grid-template-columns:1fr 48px 1fr 48px;min-height:31px;align-items:center;border-bottom:1px solid #edf0f2;font-size:12.5px;color:#263244}
.apri-n{text-align:right;color:#526174}
.apri-name-right{padding-left:20px}
.apri-note{margin-top:8px;color:#718096;font-size:11.5px}
.apri-map-wrap{padding:0;margin:0;border:none;background:transparent}
.apri-method-columns{display:grid;grid-template-columns:repeat(3,1fr)}
.apri-method-column{padding:0 28px;border-left:1px solid #e3e8ec}
.apri-method-column:first-child{padding-left:0;border-left:none}
.apri-method-column:last-child{padding-right:0}
.apri-method-column h3{color:#155c37;font-family:Arial,sans-serif;font-size:18px;line-height:1.25;margin:0 0 18px}
.apri-method-column p{color:#182132;font-family:Georgia,"Times New Roman",serif;font-size:16px;line-height:1.55;text-align:justify;margin:0 0 18px}
.apri-bottom-nav{display:flex;justify-content:space-between;margin-top:28px}
.apri-bottom-link{color:#155c37!important;text-decoration:none!important;font-size:15px;font-weight:600;border-bottom:2px solid #1c6349;padding:5px 2px 7px}
@media(max-width:900px){.apri-method-columns{grid-template-columns:1fr}.apri-method-column{border-left:none;border-top:1px solid #e3e8ec;padding:22px 0}.apri-method-column:first-child{border-top:none;padding-top:0}.apri-tabs{gap:12px}}
</style>
""", unsafe_allow_html=True)

def _e(value):
    return str(value).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def _find_file(name):
    for path in (os.path.join(DATA,name), os.path.join(APP_DIR,name)):
        if os.path.exists(path):
            return path
    return None

def _current_step():
    try:
        return 2 if str(st.query_params.get("portail_etape","1")) == "2" else 1
    except Exception:
        return 1

def _tabs(current):
    st.markdown(f"""
    <div class="apri-tabs">
      <a class="apri-tab {'apri-tab-active' if current==1 else ''}" href="?portail_etape=1">{_e(T("e1"))}</a>
      <a class="apri-tab {'apri-tab-active' if current==2 else ''}" href="?portail_etape=2">{_e(T("e2"))}</a>
    </div>
    """, unsafe_allow_html=True)

def _study_area():
    counts={"Anse à Drick":121,"Barbois":121,"Beaulieu":121,"Blactote":120,"Dalmette":125,
            "Dumont":122,"Débouchette":120,"Quentin":116,"Trichet":120,"Mouline":120}
    left=["Anse à Drick","Barbois","Beaulieu","Blactote","Dalmette"]
    right=["Dumont","Débouchette","Quentin","Trichet","Mouline"]
    rows=[]
    for a,b in zip(left,right):
        rows.append(f"<div class='apri-row'><span>{_e(a)}</span><span class='apri-n'>{counts[a]}</span><span class='apri-name-right'>{_e(b)}</span><span class='apri-n'>{counts[b]}</span></div>")
    c1,c2=st.columns([1,1.18],gap="large")
    with c1:
        st.markdown(f"""
        <div class="apri-panel">
          <div class="apri-title">{_e(T("study_title"))}</div>
          <div class="apri-rule"></div>
          <ul class="apri-bullets">
            <li>{_e(T("study_b1"))}</li>
            <li>{_e(T("study_b2"))}</li>
            <li>{_e(T("study_b3"))}</li>
          </ul>
          <div class="apri-section-label">{_e(T("sections"))}</div>
          <div class="apri-table">{''.join(rows)}</div>
          <div class="apri-note">{_e(T("section_note"))}</div>
        </div>
        """,unsafe_allow_html=True)
    with c2:
        try:
            import territoire_page
            vignette=territoire_page._vignette(territoire_page._geo(),620,430)
            st.markdown(f'<div class="apri-map-wrap">{vignette or ""}<div class="apri-note">{_e(T("map_caption"))}</div></div>',unsafe_allow_html=True)
        except Exception:
            st.markdown(f'<div class="apri-map-wrap"><div class="apri-note">{_e(T("map_caption"))}</div></div>',unsafe_allow_html=True)

def _methodology():
    st.markdown(f"""
    <div class="apri-panel">
      <div class="apri-title">{_e(T("method_title"))}</div>
      <div class="apri-rule"></div>
      <div class="apri-method-columns">
        <div class="apri-method-column">
          <h3>{_e(T("method_house_title"))}</h3>
          <p>{_e(T("method_house_p1"))}</p>
          <p>{_e(T("method_house_p2"))}</p>
          <p>{_e(T("method_house_p3"))}</p>
        </div>
        <div class="apri-method-column">
          <h3>{_e(T("method_sat_title"))}</h3>
          <p>{_e(T("method_sat_p1"))}</p>
          <p>{_e(T("method_sat_p2"))}</p>
        </div>
        <div class="apri-method-column">
          <h3>{_e(T("method_bio_title"))}</h3>
          <p>{_e(T("method_bio_p1"))}</p>
          <p>{_e(T("method_bio_p2"))}</p>
        </div>
      </div>
    </div>
    """,unsafe_allow_html=True)

def _bottom(current):
    if current==1:
        st.markdown('<div class="apri-bottom-nav"><span></span><a class="apri-bottom-link" href="?portail_etape=2">Next →</a></div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="apri-bottom-nav"><a class="apri-bottom-link" href="?portail_etape=1">← Previous</a><span></span></div>',unsafe_allow_html=True)

def render():
    current=_current_step()
    _tabs(current)
    if current==1:
        _study_area()
    else:
        _methodology()
    _bottom(current)
