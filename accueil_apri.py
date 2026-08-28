"""
APRI — Home / Accueil

Two-step landing page only:
1. The study area
2. Methodology

Important:
- The two tabs use Streamlit session_state: no URL navigation.
- No Key results / Action pathways.
- No surrounding rectangular cards.
- The methodology uses native Streamlit columns/Markdown, not nested HTML,
  so HTML cannot accidentally appear as visible source code.
"""

import os
import math
import streamlit as st
import i18n
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")


# ================================================================
# TEXTS
# ================================================================

TEXTES = {
    "mode_portail": {"en": "Home", "fr": "Accueil"},
    "e1": {"en": "The study area", "fr": "Le territoire"},
    "e2": {"en": "Methodology", "fr": "Méthodologie"},
    "study_title": {"en": "The study area", "fr": "Le territoire d'étude"},
    "study_b1": {
        "en": "Two pilot areas: Grand'Anse and Sud",
        "fr": "Deux zones pilotes : Grand'Anse et Sud",
    },
    "study_b2": {
        "en": "10 communal sections selected within them",
        "fr": "10 sections communales sélectionnées en leur sein",
    },
    "study_b3": {
        "en": "1 211 households surveyed",
        "fr": "1 211 ménages enquêtés",
    },
    "sections": {
        "en": "THE TEN COMMUNAL SECTIONS",
        "fr": "LES DIX SECTIONS COMMUNALES",
    },
    "section_note": {
        "en": "The figure beside each name is the number of households surveyed there.",
        "fr": "Le chiffre indiqué à côté de chaque nom correspond au nombre de ménages enquêtés.",
    },
    "map_caption": {
        "en": "The surveyed area, in the far south-west of the country.",
        "fr": "La zone enquêtée, à l'extrême sud-ouest du pays.",
    },
    "method_title": {
        "en": "Methodology of the survey",
        "fr": "Méthodologie de l'enquête",
    },
    "method_house_title": {
        "en": "Household survey",
        "fr": "Enquête ménage",
    },
    "method_house_p1": {
        "en": (
            "The household survey is the main source of information on living "
            "conditions, livelihoods, risk perception and families' capacity "
            "to anticipate shocks."
        ),
        "fr": (
            "L'enquête ménage constitue la principale source d'information "
            "sur les conditions de vie, les moyens d'existence, la perception "
            "des risques et la capacité d'anticipation des familles."
        ),
    },
    "method_house_p2": {
        "en": (
            "A stratified sampling plan was established to ensure balanced "
            "representation of different areas, landscape types and "
            "socio-economic contexts."
        ),
        "fr": (
            "Un plan d'échantillonnage stratifié a été mis en place pour "
            "assurer une représentation équilibrée des différentes zones, "
            "des types de paysage et des contextes socio-économiques."
        ),
    },
    "method_house_p3": {
        "en": (
            "Within each stratum, households were selected through random "
            "geolocation from a georeferenced building database, ensuring "
            "objectivity and representativeness."
        ),
        "fr": (
            "À l'intérieur de chaque strate, la sélection des ménages a été "
            "réalisée par localisation aléatoire à partir d'une base de "
            "bâtiments géoréférencés, garantissant l'objectivité et la "
            "représentativité de l'échantillon."
        ),
    },
    "method_sat_title": {
        "en": "Satellite imagery",
        "fr": "Imagerie satellitaire",
    },
    "method_sat_p1": {
        "en": (
            "High-resolution multispectral satellite imagery was used to "
            "characterise land cover and land use, track vegetation dynamics "
            "and identify landscape changes over time."
        ),
        "fr": (
            "Des images satellitaires multispectrales à haute résolution ont "
            "été utilisées pour caractériser l'occupation et l'utilisation "
            "des terres, suivre l'évolution du couvert végétal et des "
            "changements paysagers au cours du temps."
        ),
    },
    "method_sat_p2": {
        "en": (
            "Spatial analysis produced objective environmental indicators "
            "at the scale of communal sections and landscapes."
        ),
        "fr": (
            "L'analyse spatiale a permis de produire des indicateurs "
            "environnementaux objectifs à l'échelle des sections communales "
            "et des paysages."
        ),
    },
    "method_bio_title": {
        "en": "In-situ biodiversity measurements",
        "fr": "Mesures in situ de la biodiversité",
    },
    "method_bio_p1": {
        "en": (
            "Field surveys were conducted to document biodiversity through "
            "flora and fauna inventories, habitat observations and key "
            "ecological measurements."
        ),
        "fr": (
            "Des relevés de terrain ont été réalisés pour documenter la "
            "biodiversité à travers des inventaires de flore et de faune, "
            "des observations d'habitats et des mesures écologiques clés."
        ),
    },
    "method_bio_p2": {
        "en": (
            "These in-situ data complement information from other sources "
            "and make it possible to assess the condition and dynamics of "
            "biodiversity in the study territories."
        ),
        "fr": (
            "Ces données in situ viennent compléter les informations issues "
            "des autres sources et permettent d'évaluer l'état et la "
            "dynamique de la biodiversité dans les territoires étudiés."
        ),
    },
    "previous": {"en": "Previous", "fr": "Précédent"},
    "next": {"en": "Next", "fr": "Suivant"},
}

for key, value in TEXTES.items():
    i18n.DICO.setdefault(key, value)


# ================================================================
# CSS
# ================================================================

st.markdown(
    """
<style>
.block-container{
    max-width:1450px;
    padding-top:.7rem;
    padding-bottom:2rem;
}

/* ----- Two navigation tabs: NO boxes ----- */
.apri-tab-row{
    display:grid;
    grid-template-columns:1fr 1fr;
    column-gap:52px;
    margin:4px 0 22px;
}

.apri-tab-button + div{
    margin-top:-1px;
}

div[class*="st-key-apri_tab_"]{
    margin:0 !important;
    padding:0 !important;
}

div[class*="st-key-apri_tab_"] button{
    all:unset !important;
    box-sizing:border-box !important;
    width:100% !important;
    height:45px !important;
    display:block !important;
    padding:8px 4px 7px !important;
    text-align:center !important;
    cursor:pointer !important;
    color:#182132 !important;
    background:transparent !important;
    border:0 !important;
    border-radius:0 !important;
    box-shadow:none !important;
    font-family:Arial,sans-serif !important;
    font-size:15px !important;
    font-weight:600 !important;
}

div[class*="st-key-apri_tab_"] button:hover{
    color:#155c37 !important;
    background:transparent !important;
    border:0 !important;
}

.apri-line{
    width:100%;
    height:1px;
    background:#dfe5e2;
}

.apri-line.active{
    height:3px;
    background:#1c6349;
}

/* ----- Typography ----- */
.apri-title{
    font-family:Georgia,"Times New Roman",serif;
    font-size:30px;
    line-height:1.15;
    font-weight:400;
    color:#101728;
    margin:0;
}

.apri-rule{
    width:42px;
    height:2px;
    background:#2f6b4f;
    margin:12px 0 22px;
}

/* ----- Study area ----- */
.apri-study-bullet{
    margin:0 0 18px;
    font-size:14px;
    line-height:1.5;
    color:#263244;
}

.apri-bullet-square{
    color:#2f6b4f;
    font-size:11px;
    vertical-align:middle;
    margin-right:8px;
}

.apri-section-label{
    margin-top:27px;
    margin-bottom:8px;
    font-size:10px;
    font-weight:700;
    letter-spacing:.12em;
    color:#718096;
}

.apri-table-wrap{
    width:100%;
}

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

.apri-table tr:first-child td{
    border-top:1px solid #dfe5e2;
}

.apri-table .num{
    text-align:right;
    color:#526174;
    width:45px;
}

.apri-table .second-name{
    padding-left:26px;
}

/* ----- Map: no outer card ----- */
.apri-map{
    width:100%;
    padding:0;
    margin:0;
}

.apri-map-caption{
    margin-top:8px;
    color:#718096;
    font-size:11.5px;
    line-height:1.4;
}

/* ----- Methodology ----- */
.apri-method-col{
    min-height:360px;
}

.apri-method-col-left{
    padding-right:28px;
}

.apri-method-col-middle{
    padding:0 28px;
    border-left:1px solid #e3e8ec;
}

.apri-method-col-right{
    padding-left:28px;
    border-left:1px solid #e3e8ec;
}

.apri-method-title{
    color:#155c37;
    font-family:Arial,sans-serif;
    font-size:18px;
    font-weight:700;
    line-height:1.25;
    margin-bottom:18px;
}

.apri-method-text{
    color:#182132;
    font-family:Georgia,"Times New Roman",serif;
    font-size:16px;
    line-height:1.55;
    text-align:justify;
    margin:0 0 18px;
}

/* ----- Bottom navigation: no rectangular button ----- */
div[class*="st-key-apri_previous"],
div[class*="st-key-apri_next"]{
    margin:0 !important;
    padding:0 !important;
}

div[class*="st-key-apri_previous"] button,
div[class*="st-key-apri_next"] button{
    all:unset !important;
    cursor:pointer !important;
    color:#155c37 !important;
    font-family:Arial,sans-serif !important;
    font-size:15px !important;
    font-weight:600 !important;
    border-bottom:2px solid #1c6349 !important;
    padding:4px 2px 7px !important;
    background:transparent !important;
    box-shadow:none !important;
}

.apri-bottom-left{
    text-align:left;
}

.apri-bottom-right{
    text-align:right;
}

@media(max-width:900px){
    .apri-tab-row{column-gap:16px}
    .apri-method-col-left,
    .apri-method-col-middle,
    .apri-method-col-right{
        padding:20px 0;
        border-left:0;
        border-top:1px solid #e3e8ec;
    }
    .apri-method-col-left{
        border-top:0;
        padding-top:0;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# ================================================================
# SESSION / NAVIGATION
# ================================================================

def _set_step(step):
    st.session_state["portail_etape"] = step


def _current_step():
    return 2 if st.session_state.get("portail_etape", 1) == 2 else 1


def _render_tabs(current):
    left, right = st.columns(2, gap="large")

    with left:
        st.button(
            T("e1"),
            key="apri_tab_1",
            on_click=_set_step,
            args=(1,),
            use_container_width=True,
        )
        st.markdown(
            '<div class="apri-line active"></div>'
            if current == 1
            else '<div class="apri-line"></div>',
            unsafe_allow_html=True,
        )

    with right:
        st.button(
            T("e2"),
            key="apri_tab_2",
            on_click=_set_step,
            args=(2,),
            use_container_width=True,
        )
        st.markdown(
            '<div class="apri-line active"></div>'
            if current == 2
            else '<div class="apri-line"></div>',
            unsafe_allow_html=True,
        )


# ================================================================
# MAP
# ================================================================

# A simplified outline of the Dominican Republic, in lon/lat.
# The Haiti geometry and surveyed sections come from the project.
DR = [
    (-71.95, 18.62), (-71.70, 18.79), (-71.62, 19.17),
    (-71.71, 19.71), (-71.59, 19.88), (-70.81, 19.88),
    (-70.21, 19.62), (-69.95, 19.65), (-69.77, 19.29),
    (-69.22, 19.31), (-69.25, 19.02), (-68.81, 18.98),
    (-68.32, 18.61), (-68.69, 18.21), (-69.16, 18.42),
    (-69.62, 18.38), (-69.95, 18.43), (-70.13, 18.25),
    (-70.52, 18.18), (-70.67, 18.43), (-71.00, 18.28),
    (-71.40, 17.60), (-71.66, 17.76), (-71.71, 18.04),
    (-71.69, 18.32), (-71.95, 18.62)
]


def _projector(rings, width, height, margin=24):
    points = [p for ring in rings for p in ring]

    lat_mean = sum(p[1] for p in points) / len(points)
    k = math.cos(math.radians(lat_mean))

    xs = [p[0] * k for p in points]
    ys = [p[1] for p in points]

    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)

    dx = max(x1 - x0, 1e-9)
    dy = max(y1 - y0, 1e-9)

    scale = min(
        (width - 2 * margin) / dx,
        (height - 2 * margin) / dy,
    )

    ox = (width - dx * scale) / 2
    oy = (height - dy * scale) / 2

    def xy(lon, lat):
        return (
            ox + (lon * k - x0) * scale,
            oy + (y1 - lat) * scale,
        )

    return xy


def _svg_path(ring, xy):
    pts = []
    for i, (lon, lat) in enumerate(ring):
        x, y = xy(lon, lat)
        pts.append(("M" if i == 0 else "L") + f"{x:.1f} {y:.1f}")
    return "".join(pts) + "Z"


def _hispaniola_map():
    try:
        import territoire_page

        geo = territoire_page._geo()

        if not geo["pays"]:
            return None

        width, height = 760, 420
        rings = list(geo["pays"]) + [DR]
        xy = _projector(rings, width, height, margin=26)

        parts = [
            f'<rect width="{width}" height="{height}" rx="10" fill="#edf4fb"/>'
        ]

        # Haiti
        for ring in geo["pays"]:
            parts.append(
                f'<path d="{_svg_path(ring,xy)}" fill="#f4f5f1" '
                f'stroke="#cbd4dd" stroke-width="1.1"/>'
            )

        # Dominican Republic
        parts.append(
            f'<path d="{_svg_path(DR,xy)}" fill="#f4f5f1" '
            f'stroke="#cbd4dd" stroke-width="1.1"/>'
        )

        # Surveyed communes/sections
        xs, ys = [], []

        for section in geo["sections"]:
            for ring in section["anneaux"]:
                parts.append(
                    f'<path d="{_svg_path(ring,xy)}" fill="#28734f" '
                    f'stroke="#28734f" stroke-width="1"/>'
                )
                for lon, lat in ring:
                    x, y = xy(lon, lat)
                    xs.append(x)
                    ys.append(y)

        if xs and ys:
            cx = (min(xs) + max(xs)) / 2
            cy = (min(ys) + max(ys)) / 2
            radius = max(
                max(xs) - min(xs),
                max(ys) - min(ys),
            ) / 2 + 16

            parts.append(
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{radius:.1f}" '
                f'fill="none" stroke="#28734f" stroke-width="1.5" '
                f'stroke-dasharray="5 4"/>'
            )

        # Labels
        hx, hy = xy(-72.15, 19.25)
        dx, dy = xy(-69.05, 19.55)

        parts.append(
            f'<text x="{hx:.1f}" y="{hy:.1f}" font-size="12" '
            f'font-weight="700" fill="#8a93a5" letter-spacing="2">HAÏTI</text>'
        )
        parts.append(
            f'<text x="{dx:.1f}" y="{dy:.1f}" font-size="10.5" '
            f'font-weight="700" fill="#8a93a5" letter-spacing=".8">'
            f'RÉPUBLIQUE DOMINICAINE</text>'
        )

        return (
            f'<svg viewBox="0 0 {width} {height}" '
            f'xmlns="http://www.w3.org/2000/svg" '
            f'width="100%" style="display:block;border-radius:10px">'
            + "".join(parts)
            + "</svg>"
        )

    except Exception:
        return None


# ================================================================
# STUDY AREA
# ================================================================

def _study_area():
    counts = {
        "Anse à Drick": 121,
        "Barbois": 121,
        "Beaulieu": 121,
        "Blactote": 120,
        "Dalmette": 125,
        "Dumont": 122,
        "Débouchette": 120,
        "Quentin": 116,
        "Trichet": 120,
        "Mouline": 120,
    }

    left_names = [
        "Anse à Drick",
        "Barbois",
        "Beaulieu",
        "Blactote",
        "Dalmette",
    ]
    right_names = [
        "Dumont",
        "Débouchette",
        "Quentin",
        "Trichet",
        "Mouline",
    ]

    left, right = st.columns([1.0, 1.18], gap="large")

    with left:
        st.markdown(
            f'<div class="apri-title">{_e(T("study_title"))}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="apri-rule"></div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="apri-study-bullet">'
            f'<span class="apri-bullet-square">■</span>{_e(T("study_b1"))}'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="apri-study-bullet">'
            f'<span class="apri-bullet-square">■</span>{_e(T("study_b2"))}'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="apri-study-bullet">'
            f'<span class="apri-bullet-square">■</span>{_e(T("study_b3"))}'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="apri-section-label">{_e(T("sections"))}</div>',
            unsafe_allow_html=True,
        )

        # Native HTML table is confined to one explicit markdown block.
        rows = "".join(
            f"""
            <tr>
              <td>{_e(a)}</td>
              <td class="num">{counts[a]}</td>
              <td class="second-name">{_e(b)}</td>
              <td class="num">{counts[b]}</td>
            </tr>
            """
            for a, b in zip(left_names, right_names)
        )

        st.markdown(
            f"""
            <div class="apri-table-wrap">
              <table class="apri-table">
                {rows}
              </table>
            </div>
            <div class="apri-note">{_e(T("section_note"))}</div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        svg = _hispaniola_map()

        if svg:
            st.markdown(
                f"""
                <div class="apri-map">{svg}</div>
                <div class="apri-map-caption">{_e(T("map_caption"))}</div>
                """,
                unsafe_allow_html=True,
            )


# ================================================================
# METHODOLOGY
# ================================================================

def _methodology():
    st.markdown(
        f'<div class="apri-title">{_e(T("method_title"))}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="apri-rule"></div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3, gap="large")

    with c1:
        st.markdown(
            f'<div class="apri-method-col apri-method-col-left">'
            f'<div class="apri-method-title">{_e(T("method_house_title"))}</div>'
            f'<div class="apri-method-text">{_e(T("method_house_p1"))}</div>'
            f'<div class="apri-method-text">{_e(T("method_house_p2"))}</div>'
            f'<div class="apri-method-text">{_e(T("method_house_p3"))}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f'<div class="apri-method-col apri-method-col-middle">'
            f'<div class="apri-method-title">{_e(T("method_sat_title"))}</div>'
            f'<div class="apri-method-text">{_e(T("method_sat_p1"))}</div>'
            f'<div class="apri-method-text">{_e(T("method_sat_p2"))}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f'<div class="apri-method-col apri-method-col-right">'
            f'<div class="apri-method-title">{_e(T("method_bio_title"))}</div>'
            f'<div class="apri-method-text">{_e(T("method_bio_p1"))}</div>'
            f'<div class="apri-method-text">{_e(T("method_bio_p2"))}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ================================================================
# BOTTOM
# ================================================================

def _bottom(current):
    left, right = st.columns(2)

    with left:
        if current == 2:
            st.button(
                "← " + T("previous"),
                key="apri_previous",
                on_click=_set_step,
                args=(1,),
            )

    with right:
        if current == 1:
            st.button(
                T("next") + " →",
                key="apri_next",
                on_click=_set_step,
                args=(2,),
            )


# ================================================================
# MAIN
# ================================================================

def render():
    st.session_state.setdefault("portail_etape", 1)

    current = _current_step()

    _render_tabs(current)

    if current == 1:
        _study_area()
    else:
        _methodology()

    _bottom(current)
