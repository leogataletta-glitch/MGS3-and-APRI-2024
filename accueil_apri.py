"""
APRI — Accueil (Design exact basé sur la maquette)
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

def _inject_css():
    st.markdown("""
    <style>
    /* Global Container */
    .block-container {
        max-width: 1400px;
        padding-top: 1rem;
        padding-bottom: 2rem;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* Top Banner Header */
    .header-banner {
        background: linear-gradient(90deg, rgba(255,255,255,1) 35%, rgba(255,255,255,0.7) 50%, rgba(255,255,255,0) 100%), 
                    url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1600&q=80');
        background-size: cover;
        background-position: center;
        border-radius: 12px;
        padding: 24px 32px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
    }

    .header-title-box {
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .header-logo {
        width: 60px;
        height: 60px;
        background-color: #1b4d3e;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 24px;
        font-weight: bold;
    }

    .header-text h1 {
        margin: 0;
        font-size: 32px;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.5px;
    }

    .header-text p {
        margin: 2px 0 0 0;
        font-size: 13px;
        color: #475569;
        font-weight: 500;
    }

    /* Styled Tabs like Cards */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        border-bottom: none !important;
        margin-bottom: 25px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 60px;
        background: #f8fafc !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 12px !important;
        box-shadow: none !important;
        color: #334155 !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        flex: 1;
        justify-content: center;
        transition: all 0.2s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        border-color: #1b4d3e !important;
        color: #1b4d3e !important;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: #e6f2ed !important;
        border: 2px solid #1b4d3e !important;
        color: #0f172a !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    /* Bullet points */
    .apri-bullet {
        margin: 0 0 12px 0;
        font-size: 14.5px;
        color: #334155;
        font-weight: 600;
    }

    .apri-square {
        color: #1b4d3e;
        margin-right: 10px;
        font-size: 12px;
    }

    .apri-label {
        margin: 28px 0 12px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.08em;
        color: #1b4d3e;
    }

    /* Table Grid Cards */
    .grid-table {
        display: grid;
        grid-template-columns: 1fr 60px 1fr 60px;
        gap: 6px 0px;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        overflow: hidden;
        background-color: #ffffff;
    }

    .grid-cell {
        padding: 10px 14px;
        font-size: 13.5px;
        color: #1e293b;
        border-bottom: 1px solid #f1f5f9;
        border-right: 1px solid #f1f5f9;
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
        margin-top: 12px;
        color: #64748b;
        font-size: 12px;
        line-height: 1.4;
    }

    /* Map Section */
    .apri-map svg {
        display: block;
        width: 100%;
        height: auto;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* Methodology Styling */
    .apri-method-title {
        color: #1b4d3e;
        font-weight: 700;
        font-size: 17px;
        margin-bottom: 12px;
    }

    .apri-method-text {
        color: #334155;
        font-size: 14px;
        line-height: 1.6;
        margin-bottom: 14px;
    }

    /* Next Button Style */
    .next-btn-container {
        display: flex;
        justify-content: center;
        margin-top: 35px;
    }
    
    .stButton > button {
        border-radius: 20px !important;
        padding: 8px 30px !important;
        border: 1px solid #cbd5e1 !important;
        background: #ffffff !important;
        color: #1b4d3e !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    
    .stButton > button:hover {
        background: #f8fafc !important;
        border-color: #1b4d3e !important;
    }
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
        xy = _project(list(geo["pays"]) + [DR], w, h)
        parts = [f'<rect width="{w}" height="{h}" rx="12" fill="#edf4fb"/>']
        for ring in geo["pays"]:
            parts.append(f'<path d="{_path(ring, xy)}" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>')
        parts.append(f'<path d="{_path(DR, xy)}" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>')
        sx, sy = [], []
        for sec in geo.get("sections", []):
            for ring in sec.get("anneaux", []):
                parts.append(f'<path d="{_path(ring, xy)}" fill="#28734f" stroke="#1b4d3e" stroke-width="1"/>')
                for lon, lat in ring:
                    x, y = xy(lon, lat)
                    sx.append(x); sy.append(y)
        if sx:
            cx = (min(sx) + max(sx)) / 2
            cy = (min(sy) + max(sy)) / 2
            r = max(max(sx) - min(sx), max(sy) - min(sy)) / 2 + 16
            parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="#1b4d3e" stroke-width="1.5" stroke-dasharray="5 4"/>')
        hx, hy = xy(-72.15, 19.25)
        parts.append(f'<text x="{hx:.1f}" y="{hy:.1f}" font-size="13" font-weight="800" fill="#1b4d3e" letter-spacing="2">HAÏTI</text>')
        return f'<div class="apri-map"><svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg></div>'
    except Exception:
        return None

def _render_header():
    st.markdown("""
    <div class="header-banner">
        <div class="header-title-box">
            <div class="header-logo">🌴</div>
            <div class="header-text">
                <h1>APRI</h1>
                <p>Landscape resilience observatory<br>Sud and Grand'Anse, Haiti</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
        for k in ("b1", "b2", "b3"):
            st.markdown(f'<div class="apri-bullet"><span class="apri-square">■</span>{_e(T(k))}</div>', unsafe_allow_html=True)
            
        st.markdown(f'<div class="apri-label">{_e(T("sections"))}</div>', unsafe_allow_html=True)
        
        # Grid styled like individual rounded cells
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
    _render_header()

    tab1, tab2 = st.tabs([T("e1"), T("e2")])
    with tab1:
        _study_area()
    with tab2:
        _methodology()

    # Next button in bottom center
    st.markdown('<div class="next-btn-container">', unsafe_allow_html=True)
    col_l, col_btn, col_r = st.columns([4, 1, 4])
    with col_btn:
        st.button(f"{T('next')} →")
    st.markdown('</div>', unsafe_allow_html=True)
