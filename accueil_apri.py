"""
APRI — Accueil (Clean Layout, Onglets 50/50 & Carte Haïti uniquement)
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
    "house1": {"en": "The household survey is the main source of information on living conditions, livelihoods, risk perception and families' capacity to anticipate shocks.", "fr": "L'enquête ménage constitue la principale source d'information sur les conditions de vie, les moyens d'existence, la perception des risques et la capacity d'anticipation des familles."},
    "house2": {"en": "A stratified sampling plan was established to ensure balanced representation of different areas, landscape types and socio-economic contexts.", "fr": "Un plan d'échantillonnage stratifié a été mis en place pour assurer une représentation équilibrée des différentes zones, des types de paysage et des contextes socio-économiques."},
    "house3": {"en": "Within each stratum, households were selected through random geolocation from a georeferenced building database, ensuring objectivity and representativeness.", "fr": "À l'intérieur de chaque strate, la sélection des ménages a été réalisée par localisation aléatoire à partir d'une base de bâtiments géoréférencés, garantissant l'objectivité et la représentativité de l'échantillon."},
    "sat": {"en": "Satellite imagery", "fr": "Imagerie satellitaire"},
    "sat1": {"en": "High-resolution multispectral satellite imagery was used to characterise land cover and land use, track vegetation dynamics and identify landscape changes over time.", "fr": "Des images satellitaires multispectrales à haute résolution ont été utilisées pour caractériser l'occupation et l'utilisation des terres, suivre l'évolution du couvert végétal et les changements paysagers au cours du temps."},
    "sat2": {"en": "Spatial analysis produced objective environmental indicators at the scale of communal sections and landscapes.", "fr": "L'analyse spatiale a permis de produire des indicateurs environnementaux objectifs à l'échelle des sections communales et des paysages."},
    "bio": {"en": "In-situ biodiversity measurements", "fr": "Mesures in situ de la biodiversité"},
    "bio1": {"en": "Field surveys were conducted to document biodiversity through flora and fauna inventories, habitat observations and key ecological measurements.", "fr": "Des relevés de terrain ont été réalisés pour documenter la biodiversité à travers des inventaires de flore et de faune, des observations d'habitats et des mesures écologiques clés."},
    "bio2": {"en": "These in-situ data complement information from other sources and make it possible to assess the condition and dynamics of biodiversity in the study territories.", "fr": "Ces données in situ viennent compléter les informations issues des autres sources et permettent d'évaluer l'état et la dynamique de la biodiversité dans les territoires étudiés."},
}

for k, v in TEXTES.items():
    i18n.DICO.setdefault(k, v)

def _inject_css():
    st.markdown("""
    <style>
    .block-container {
        max-width: 1400px;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    /* Force columns to split 50/50 exactly and buttons to fill them */
    div[data-testid="stHorizontalBlock"] > div {
        flex: 1 1 0% !important;
        width: 100% !important;
    }

    div[data-testid="stHorizontalBlock"] .stButton {
        width: 100% !important;
    }

    div[data-testid="stHorizontalBlock"] .stButton > button {
        width: 100% !important;
        height: 65px !important;
        border-radius: 12px !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        box-sizing: border-box !important;
    }

    .tab-active > button {
        background-color: #eaf4ee !important;
        border: 2px solid #1c6349 !important;
        color: #1c6349 !important;
    }

    .tab-inactive > button {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        color: #475569 !important;
    }

    .tab-inactive > button:hover {
        border-color: #1c6349 !important;
        color: #1c6349 !important;
    }

    /* Bullets */
    .apri-bullet {
        margin: 0 0 14px 0;
        font-size: 15px;
        color: #1e293b;
        font-weight: 600;
    }

    .apri-square {
        color: #1c6349;
        margin-right: 10px;
        font-size: 12px;
    }

    .apri-label {
        margin: 28px 0 12px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.08em;
        color: #1c6349;
    }

    /* Grid Table Cards */
    .grid-table {
        display: grid;
        grid-template-columns: 1fr 60px 1fr 60px;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        overflow: hidden;
        background-color: #ffffff;
    }

    .grid-cell {
        padding: 10px 14px;
        font-size: 13.5px;
        color: #1e293b;
        border-bottom: 1px solid #edf2f7;
        border-right: 1px solid #edf2f7;
        display: flex;
        align-items: center;
    }

    .grid-cell.num {
        font-weight: 700;
        justify-content: flex-end;
        color: #0f172a;
    }

    .grid-cell.last-col {
        border-right: none;
    }

    .apri-note {
        margin-top: 10px;
        color: #64748b;
        font-size: 12px;
        line-height: 1.4;
    }

    /* Map SVG */
    .apri-map svg {
        display: block;
        width: 100%;
        height: auto;
        border-radius: 14px;
    }

    /* Methodology Text */
    .apri-method-title {
        color: #1c6349;
        font-weight: 700;
        font-size: 18px;
        margin-bottom: 12px;
    }

    .apri-method-text {
        color: #334155;
        font-size: 14.5px;
        line-height: 1.6;
        margin-bottom: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

def _e(x):
    return str(x).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def _project(rings, width=760, height=420, margin=25):
    pts = [p for r in rings for p in r]
    if not pts:
        return lambda lon, lat: (0, 0)
    lat = sum(p[1] for p in pts) / len(pts)
    k = math.cos(math.radians(lat))
    xs = [p[0] * k for p in pts]
    ys = [p[1] for p in pts]
    x0, x1 = min(xs), max(xs); y0, y1 = min(ys), max(ys)
    dx = max(x1 - x0, 1e-9); dy = max(y1 - y0, 1e-9)
    s = min((width - 2 * margin) / dx, (height - 2 * margin) / dy)
    ox = (width - dx * s) / 2; oy = (height - dy * s) / 2
    return lambda lon, lat: (ox + (lon * k - x0) * s, oy + (y1 - lat) * s)

def _path(ring, xy):
    return "".join(
        ("M" if i == 0 else "L") + f"{xy(lon, lat)[0]:.1f} {xy(lon, lat)[1]:.1f}"
        for i, (lon, lat) in enumerate(ring)
    ) + "Z"

@st.cache_data
def _hispaniola_map():
    try:
        import territoire_page
        geo = territoire_page._geo()
        if not geo.get("pays"):
            return None
        w, h = 760, 420
        xy = _project(geo["pays"], w, h)
        
        parts = [f'<rect width="{w}" height="{h}" rx="14" fill="#edf4fb"/>']
        
        # Haïti Uniquement
        for ring in geo["pays"]:
            parts.append(f'<path d="{_path(ring, xy)}" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
        
        # Sections communales en vert
        sx, sy = [], []
        for sec in geo.get("sections", []):
            for ring in sec.get("anneaux", []):
                parts.append(f'<path d="{_path(ring, xy)}" fill="#28734f" stroke="#1c6349" stroke-width="1"/>')
                for lon, lat in ring:
                    x, y = xy(lon, lat)
                    sx.append(x); sy.append(y)
                    
        # Cercle pointillé vert sur la zone d'étude
        if sx:
            cx = (min(sx) + max(sx)) / 2
            cy = (min(sy) + max(sy)) / 2
            r = max(max(sx) - min(sx), max(sy) - min(sy)) / 2 + 18
            parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="#1c6349" stroke-width="1.5" stroke-dasharray="5 4"/>')
            
        hx, hy = xy(-72.30, 19.10)
        parts.append(f'<text x="{hx:.1f}" y="{hy:.1f}" font-size="15" font-weight="800" fill="#1c6349" letter-spacing="2">HAÏTI</text>')
        return f'<div class="apri-map"><svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg></div>'
    except Exception:
        return None

def _study_area():
    counts = {
        "Anse à Drick": 121, "Dumont": 122, "Barbois": 121, "Débouchette": 120,
        "Beaulieu": 121, "Quentin": 116, "Blactote": 120, "Trichet": 120,
        "Dalmette": 125, "Mouline": 120
    }
    left = ["Anse à Drick", "Barbois", "Beaulieu", "Blactote", "Dalmette"]
    right = ["Dumont", "Débouchette", "Quentin", "Trichet", "Mouline"]
    
    c1, c2 = st.columns([1.05, 1.15], gap="large")
    with c1:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        for k in ("b1", "b2", "b3"):
            st.markdown(f'<div class="apri-bullet"><span class="apri-square">■</span>{_e(T(k))}</div>', unsafe_allow_html=True)
            
        st.markdown(f'<div class="apri-label">{_e(T("sections"))}</div>', unsafe_allow_html=True)
        
        grid_html = '<div class="grid-table">'
        for a, b in zip(left, right):
            grid_html += f'<div class="grid-cell">{_e(a)}</div>'
            grid_html += f'<div class="grid-cell num">{counts[a]}</div>'
            grid_html += f'<div class="grid-cell">{_e(b)}</div>'
            grid_html += f'<div class="grid-cell num last-col">{counts[b]}</div>'
        grid_html += '</div>'
        
        st.markdown(grid_html, unsafe_allow_html=True)
        st.markdown(f'<div class="apri-note">{_e(T("note"))}</div>', unsafe_allow_html=True)

    with c2:
        svg = _hispaniola_map()
        if svg:
            st.markdown(svg, unsafe_allow_html=True)
            st.markdown(f'<div class="apri-note">{_e(T("map_note"))}</div>', unsafe_allow_html=True)

def _methodology():
    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        st.markdown(f'<div class="apri-method-title">{_e(T("house"))}</div>', unsafe_allow_html=True)
        for k in ("house1", "house2", "house3"):
            st.markdown(f'<div class="apri-method-text">{_e(T(k))}</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="apri-method-title">{_e(T("sat"))}</div>', unsafe_allow_html=True)
        for k in ("sat1", "sat2"):
            st.markdown(f'<div class="apri-method-text">{_e(T(k))}</div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="apri-method-title">{_e(T("bio"))}</div>', unsafe_allow_html=True)
        for k in ("bio1", "bio2"):
            st.markdown(f'<div class="apri-method-text">{_e(T(k))}</div>', unsafe_allow_html=True)

def render():
    _inject_css()

    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "study"

    col_t1, col_t2 = st.columns(2, gap="medium")
    
    with col_t1:
        t1_class = "tab-active" if st.session_state.current_tab == "study" else "tab-inactive"
        st.markdown(f'<div class="{t1_class}">', unsafe_allow_html=True)
        if st.button(T("e1"), key="btn_tab_study"):
            st.session_state.current_tab = "study"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_t2:
        t2_class = "tab-active" if st.session_state.current_tab == "method" else "tab-inactive"
        st.markdown(f'<div class="{t2_class}">', unsafe_allow_html=True)
        if st.button(T("e2"), key="btn_tab_method"):
            st.session_state.current_tab = "method"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    if st.session_state.current_tab == "study":
        _study_area()
    else:
        _methodology()
