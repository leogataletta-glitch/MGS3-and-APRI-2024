"""
APRI — Accueil
Deux onglets uniquement :
1. The study area
2. Methodology

Navigation via st.tabs(): aucun changement d'URL et aucune nouvelle page.
"""

import os
import math
import streamlit as st
import i18n
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

TEXTES = {
    "mode_portail": {"en": "Home", "fr": "Accueil"},
    "e1": {"en": "The study area", "fr": "Le territoire"},
    "e2": {"en": "Methodology", "fr": "Méthodologie"},
    "study_title": {"en": "The study area", "fr": "Le territoire d'étude"},
    "b1": {"en": "Two pilot areas: Grand'Anse and Sud", "fr": "Deux zones pilotes : Grand'Anse et Sud"},
    "b2": {"en": "10 communal sections selected within them", "fr": "10 sections communales sélectionnées en leur sein"},
    "b3": {"en": "1 211 households surveyed", "fr": "1 211 ménages enquêtés"},
    "sections": {"en": "THE TEN COMMUNAL SECTIONS", "fr": "LES DIX SECTIONS COMMUNALES"},
    "note": {"en": "The figure beside each name is the number of households surveyed there.", "fr": "Le chiffre indiqué à côté de chaque nom correspond au nombre de ménages enquêtés."},
    "map_note": {"en": "The surveyed area, in the far south-west of the country.", "fr": "La zone enquêtée, à l'extrême sud-ouest du pays."},
    "method_title": {"en": "Methodology of the survey", "fr": "Méthodologie de l'enquête"},
    "house": {"en": "Household survey", "fr": "Enquête ménage"},
    "house1": {"en": "The household survey is the main source of information on living conditions, livelihoods, risk perception and families' capacity to anticipate shocks.", "fr": "L'enquête ménage constitue la principale source d'information sur les conditions de vie, les moyens d'existence, la perception des risques et la capacité d'anticipation des familles."},
    "house2": {"en": "A stratified sampling plan was established to ensure balanced representation of different areas, landscape types and socio-economic contexts.", "fr": "Un plan d'échantillonnage stratifié a été mis en place pour assurer une représentation équilibrée des différentes zones, des types de paysage et des contextes socio-économiques."},
    "house3": {"en": "Within each stratum, households were selected through random geolocation from a georeferenced building database, ensuring objectivity and representativeness.", "fr": "À l'intérieur de chaque strate, la sélection des ménages a été réalisée par localisation aléatoire à partir d'une base de bâtiments géoréférencés, garantissant l'objectivité et la représentativité de l'échantillon."},
    "sat": {"en": "Satellite imagery", "fr": "Imagerie satellitaire"},
    "sat1": {"en": "High-resolution multispectral satellite imagery was used to characterise land cover and land use, track vegetation dynamics and identify landscape changes over time.", "fr": "Des images satellitaires multispectrales à haute résolution ont été utilisées pour caractériser l'occupation et l'utilisation des terres, suivre l'évolution du couvert végétal et les changements paysagers au cours du temps."},
    "sat2": {"en": "Spatial analysis produced objective environmental indicators at the scale of communal sections and landscapes.", "fr": "L'analyse spatiale a permis de produire des indicateurs environnementaux objectifs à l'échelle des sections communales et des paysages."},
    "bio": {"en": "In-situ biodiversity measurements", "fr": "Mesures in situ de la biodiversité"},
    "bio1": {"en": "Field surveys were conducted to document biodiversity through flora and fauna inventories, habitat observations and key ecological measurements.", "fr": "Des relevés de terrain ont été réalisés pour documenter la biodiversité à travers des inventaires de flore et de faune, des observations d'habitats et des mesures écologiques clés."},
    "bio2": {"en": "These in-situ data complement information from other sources and make it possible to assess the condition and dynamics of biodiversity in the study territories.", "fr": "Ces données in situ viennent compléter les informations issues des autres sources et permettent d'évaluer l'état et la dynamique de la biodiversité dans les territoires étudiés."},
    "previous": {"en": "Previous", "fr": "Précédent"},
    "next": {"en": "Next", "fr": "Suivant"},
}
for k, v in TEXTES.items():
    i18n.DICO.setdefault(k, v)

st.markdown("""
<style>
.block-container{max-width:1450px;padding-top:.6rem;padding-bottom:2rem}

/* Native tabs: no card, no radio circles */
.stTabs [data-baseweb="tab-list"]{
    gap:48px;
    border-bottom:1px solid #dfe5e2;
}
.stTabs [data-baseweb="tab"]{
    height:50px;
    padding:12px 4px 9px;
    background:transparent !important;
    border:0 !important;
    border-radius:0 !important;
    box-shadow:none !important;
    color:#182132;
    font:600 15px Arial,sans-serif;
}
.stTabs [data-baseweb="tab"]:hover{
    background:transparent !important;
    color:#155c37;
}
.stTabs [data-baseweb="tab"][aria-selected="true"]{
    color:#155c37;
}
.stTabs [data-baseweb="tab-highlight"]{
    height:3px !important;
    background:#1c6349 !important;
}
.stTabs [data-baseweb="tab-border"]{display:none !important}

/* Typography */
.apri-title{
    font:400 30px/1.15 Georgia,"Times New Roman",serif;
    color:#101728;
    margin:0;
}
.apri-rule{
    width:42px;height:2px;background:#2f6b4f;margin:12px 0 22px;
}
.apri-bullet{
    margin:0 0 17px;
    font-size:14px;line-height:1.5;color:#263244;
}
.apri-square{color:#2f6b4f;margin-right:9px}
.apri-label{
    margin:26px 0 8px;
    font:700 10px/1.2 Arial,sans-serif;
    letter-spacing:.12em;color:#718096;
}
.apri-note{
    margin-top:9px;
    color:#718096;
    font-size:11.5px;
    line-height:1.4;
}

/* Clean section table */
.apri-table{
    width:100%;
    border-collapse:collapse;
    font-size:12.5px;
}
.apri-table td{
    padding:7px 0;
    border-top:1px solid #edf0f2;
    color:#263244;
}
.apri-table tr:first-child td{border-top:1px solid #dfe5e2}
.apri-table .num{text-align:right;color:#526174;width:42px}
.apri-table .name2{padding-left:28px}

/* Map has no surrounding card */
.apri-map svg{
    display:block;
    width:100%;
    height:auto;
    border-radius:10px;
}

/* Methodology */
.apri-method-title{
    color:#155c37;
    font:700 18px/1.25 Arial,sans-serif;
    margin-bottom:17px;
}
.apri-method-text{
    color:#182132;
    font:400 16px/1.55 Georgia,"Times New Roman",serif;
    text-align:justify;
    margin-bottom:18px;
}

/* Bottom */
.apri-bottom-left{text-align:left}
.apri-bottom-right{text-align:right}
</style>
""", unsafe_allow_html=True)

def _e(x):
    return str(x).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

DR = [
    (-71.95,18.62),(-71.70,18.79),(-71.62,19.17),(-71.71,19.71),
    (-71.59,19.88),(-70.81,19.88),(-70.21,19.62),(-69.95,19.65),
    (-69.77,19.29),(-69.22,19.31),(-69.25,19.02),(-68.81,18.98),
    (-68.32,18.61),(-68.69,18.21),(-69.16,18.42),(-69.62,18.38),
    (-69.95,18.43),(-70.13,18.25),(-70.52,18.18),(-70.67,18.43),
    (-71.00,18.28),(-71.40,17.60),(-71.66,17.76),(-71.71,18.04),
    (-71.69,18.32),(-71.95,18.62)
]

def _project(rings, width=760, height=420, margin=20):
    pts=[p for r in rings for p in r]
    lat=sum(p[1] for p in pts)/len(pts)
    k=math.cos(math.radians(lat))
    xs=[p[0]*k for p in pts]
    ys=[p[1] for p in pts]
    x0,x1=min(xs),max(xs); y0,y1=min(ys),max(ys)
    dx=max(x1-x0,1e-9); dy=max(y1-y0,1e-9)
    s=min((width-2*margin)/dx,(height-2*margin)/dy)
    ox=(width-dx*s)/2; oy=(height-dy*s)/2
    return lambda lon,lat:(ox+(lon*k-x0)*s, oy+(y1-lat)*s)

def _path(ring,xy):
    return "".join(
        ("M" if i==0 else "L")+f"{xy(lon,lat)[0]:.1f} {xy(lon,lat)[1]:.1f}"
        for i,(lon,lat) in enumerate(ring)
    )+"Z"

def _hispaniola_map():
    try:
        import territoire_page
        geo=territoire_page._geo()
        if not geo["pays"]:
            return None
        w,h=760,420
        xy=_project(list(geo["pays"])+[DR],w,h)
        parts=[f'<rect width="{w}" height="{h}" rx="10" fill="#edf4fb"/>']
        for ring in geo["pays"]:
            parts.append(f'<path d="{_path(ring,xy)}" fill="#f4f5f1" stroke="#cbd4dd" stroke-width="1.1"/>')
        parts.append(f'<path d="{_path(DR,xy)}" fill="#f4f5f1" stroke="#cbd4dd" stroke-width="1.1"/>')
        sx=[]; sy=[]
        for sec in geo["sections"]:
            for ring in sec["anneaux"]:
                parts.append(f'<path d="{_path(ring,xy)}" fill="#28734f" stroke="#28734f" stroke-width="1"/>')
                for lon,lat in ring:
                    x,y=xy(lon,lat); sx.append(x); sy.append(y)
        if sx:
            cx=(min(sx)+max(sx))/2; cy=(min(sy)+max(sy))/2
            r=max(max(sx)-min(sx),max(sy)-min(sy))/2+16
            parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="#28734f" stroke-width="1.5" stroke-dasharray="5 4"/>')
        hx,hy=xy(-72.15,19.25); dx,dy=xy(-69.05,19.55)
        parts.append(f'<text x="{hx:.1f}" y="{hy:.1f}" font-size="12" font-weight="700" fill="#8a93a5" letter-spacing="2">HAÏTI</text>')
        parts.append(f'<text x="{dx:.1f}" y="{dy:.1f}" font-size="10.5" font-weight="700" fill="#8a93a5">RÉPUBLIQUE DOMINICAINE</text>')
        return f'<div class="apri-map"><svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg></div>'
    except Exception:
        return None

def _study_area():
    counts={"Anse à Drick":121,"Dumont":122,"Barbois":121,"Débouchette":120,"Beaulieu":121,"Quentin":116,"Blactote":120,"Trichet":120,"Dalmette":125,"Mouline":120}
    left=["Anse à Drick","Barbois","Beaulieu","Blactote","Dalmette"]
    right=["Dumont","Débouchette","Quentin","Trichet","Mouline"]
    c1,c2=st.columns([1.02,1.18],gap="large")
    with c1:
        st.markdown(f'<div class="apri-title">{_e(T("study_title"))}</div><div class="apri-rule"></div>',unsafe_allow_html=True)
        for k in ("b1","b2","b3"):
            st.markdown(f'<div class="apri-bullet"><span class="apri-square">■</span>{_e(T(k))}</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="apri-label">{_e(T("sections"))}</div>',unsafe_allow_html=True)
        rows=[]
        for a,b in zip(left,right):
            rows.append(f"<tr><td>{_e(a)}</td><td class='num'>{counts[a]}</td><td class='name2'>{_e(b)}</td><td class='num'>{counts[b]}</td></tr>")
        st.markdown(f"<table class='apri-table'>{''.join(rows)}</table><div class='apri-note'>{_e(T('note'))}</div>",unsafe_allow_html=True)
    with c2:
        svg=_hispaniola_map()
        if svg:
            st.markdown(svg,unsafe_allow_html=True)
            st.markdown(f'<div class="apri-note">{_e(T("map_note"))}</div>',unsafe_allow_html=True)

def _methodology():
    st.markdown(f'<div class="apri-title">{_e(T("method_title"))}</div><div class="apri-rule"></div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3,gap="large")
    with c1:
        st.markdown(f'<div class="apri-method-title">{_e(T("house"))}</div>',unsafe_allow_html=True)
        for k in ("house1","house2","house3"):
            st.markdown(f'<div class="apri-method-text">{_e(T(k))}</div>',unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="apri-method-title">{_e(T("sat"))}</div>',unsafe_allow_html=True)
        for k in ("sat1","sat2"):
            st.markdown(f'<div class="apri-method-text">{_e(T(k))}</div>',unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="apri-method-title">{_e(T("bio"))}</div>',unsafe_allow_html=True)
        for k in ("bio1","bio2"):
            st.markdown(f'<div class="apri-method-text">{_e(T(k))}</div>',unsafe_allow_html=True)

def render():
    tab1,tab2=st.tabs([T("e1"),T("e2")])
    with tab1:
        _study_area()
    with tab2:
        _methodology()
