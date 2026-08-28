"""
APRI — accueil
Version propre et stable :
- seulement 2 onglets : The study area / Methodology
- changement de page dans la même application Streamlit
- aucun grand rectangle autour des onglets
- carte de l'île d'Hispaniola avec Haïti + République dominicaine
- texte et tableau correctement espacés
"""

import os
import math
import json
import streamlit as st
import i18n
from i18n import T


APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")


# ================================================================
# TEXTES
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
# STYLE
# ================================================================

st.markdown(
    """
<style>
.block-container{
    padding-top:0.6rem;
    padding-bottom:2rem;
    max-width:1450px;
}

/* ---------------------------------------------------------------
   Onglets : texte simple + filet inférieur.
   Les widgets Streamlit sont rendus invisibles visuellement.
   --------------------------------------------------------------- */

.apri-tab-grid{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:56px;
    margin:4px 0 24px 0;
}

div[class*="st-key-apri_tab_1"],
div[class*="st-key-apri_tab_2"]{
    margin:0 !important;
    padding:0 !important;
}

div[class*="st-key-apri_tab_1"] button,
div[class*="st-key-apri_tab_2"] button{
    all:unset !important;
    box-sizing:border-box !important;
    display:block !important;
    width:100% !important;
    height:48px !important;
    padding:14px 4px 10px 4px !important;
    text-align:center !important;
    cursor:pointer !important;
    background:transparent !important;
    border:0 !important;
    border-radius:0 !important;
    box-shadow:none !important;
    color:#111827 !important;
    font-family:Arial,sans-serif !important;
    font-size:15px !important;
    font-weight:600 !important;
}

div[class*="st-key-apri_tab_1"] button:hover,
div[class*="st-key-apri_tab_2"] button:hover{
    color:#155c37 !important;
    background:transparent !important;
}

.apri-tab-line{
    height:1px;
    background:#dfe5e2;
    width:100%;
    margin-top:-1px;
}

.apri-tab-line.active{
    height:3px;
    background:#1c6349;
}

/* ---------------------------------------------------------------
   Page
   --------------------------------------------------------------- */

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

.apri-bullets{
    margin:0 0 29px 0;
    padding:0;
    list-style:none;
}

.apri-bullets li{
    position:relative;
    padding-left:17px;
    margin:0 0 17px 0;
    color:#263244;
    font-size:14px;
    line-height:1.45;
}

.apri-bullets li:before{
    content:"";
    position:absolute;
    left:0;
    top:0.58em;
    width:5px;
    height:5px;
    background:#2f6b4f;
}

.apri-section-label{
    font-size:10px;
    line-height:1.2;
    font-weight:700;
    letter-spacing:.12em;
    color:#718096;
    margin:0 0 9px 0;
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
    vertical-align:middle;
}

.apri-table tr:first-child td{
    border-top:1px solid #dfe5e2;
}

.apri-table .name2{
    padding-left:28px;
}

.apri-table .number{
    width:42px;
    text-align:right;
    color:#526174;
    font-variant-numeric:tabular-nums;
}

.apri-note{
    margin-top:9px;
    color:#718096;
    font-size:11.5px;
    line-height:1.4;
}

/* Aucun cadre autour de la carte */
.apri-map{
    width:100%;
    margin:0;
    padding:0;
}

.apri-map svg{
    display:block;
    width:100%;
    height:auto;
}

/* Méthodologie */
.apri-method{
    display:grid;
    grid-template-columns:repeat(3,1fr);
}

.apri-method-col{
    padding:0 30px;
    border-left:1px solid #e3e8ec;
}

.apri-method-col:first-child{
    padding-left:0;
    border-left:0;
}

.apri-method-col:last-child{
    padding-right:0;
}

.apri-method-col h3{
    margin:0 0 17px 0;
    color:#155c37;
    font-family:Arial,sans-serif;
    font-size:18px;
    line-height:1.25;
}

.apri-method-col p{
    margin:0 0 18px 0;
    color:#182132;
    font-family:Georgia,"Times New Roman",serif;
    font-size:16px;
    line-height:1.55;
    text-align:justify;
}

/* Navigation bas de page : texte, pas de rectangle */
.apri-bottom{
    display:flex;
    justify-content:space-between;
    margin-top:28px;
}

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
    font-size:15px !important;
    font-weight:600 !important;
    padding:4px 2px 7px !important;
    border-bottom:2px solid #1c6349 !important;
    background:transparent !important;
    box-shadow:none !important;
}

@media(max-width:900px){
    .apri-tab-grid{gap:18px}
    .apri-method{grid-template-columns:1fr}
    .apri-method-col{
        border-left:0;
        border-top:1px solid #e3e8ec;
        padding:22px 0;
    }
    .apri-method-col:first-child{
        border-top:0;
        padding-top:0;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# ================================================================
# OUTILS
# ================================================================

def _e(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _find_file(name):
    for path in (
        os.path.join(DATA, name),
        os.path.join(APP_DIR, name),
    ):
        if os.path.exists(path):
            return path
    return None


def _set_step(n):
    st.session_state["portail_etape"] = n


# ================================================================
# ONGLET
# ================================================================

def _tabs(current):
    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.button(
            T("e1"),
            key="apri_tab_1",
            on_click=_set_step,
            args=(1,),
            use_container_width=True,
        )
        st.markdown(
            '<div class="apri-tab-line active"></div>'
            if current == 1
            else '<div class="apri-tab-line"></div>',
            unsafe_allow_html=True,
        )

    with c2:
        st.button(
            T("e2"),
            key="apri_tab_2",
            on_click=_set_step,
            args=(2,),
            use_container_width=True,
        )
        st.markdown(
            '<div class="apri-tab-line active"></div>'
            if current == 2
            else '<div class="apri-tab-line"></div>',
            unsafe_allow_html=True,
        )


# ================================================================
# CARTE : HISPANIOLA
# ================================================================

# Géométrie réelle simplifiée de la République dominicaine.
# Source : countriesgeojson / GeoJSON.
DR = [
    (-71.712361,19.714456),
    (-71.587304,19.884911),
    (-70.806706,19.880286),
    (-70.214365,19.622885),
    (-69.950815,19.648000),
    (-69.769250,19.293267),
    (-69.222126,19.313214),
    (-69.254346,19.015196),
    (-68.809412,18.979074),
    (-68.317943,18.612198),
    (-68.689316,18.205142),
    (-69.164946,18.422648),
    (-69.623988,18.380713),
    (-69.952934,18.428307),
    (-70.133233,18.245915),
    (-70.517137,18.184291),
    (-70.669298,18.426886),
    (-70.999950,18.283329),
    (-71.400210,17.598564),
    (-71.657662,17.757573),
    (-71.708305,18.044997),
    (-71.687738,18.316660),
    (-71.945112,18.616900),
    (-71.701303,18.785417),
    (-71.624873,19.169838),
    (-71.712361,19.714456),
]


def _projector(rings, width, height, margin=24):
    pts = [p for ring in rings for p in ring]

    lat_mean = sum(p[1] for p in pts) / len(pts)
    k = math.cos(math.radians(lat_mean))

    xs = [p[0] * k for p in pts]
    ys = [p[1] for p in pts]

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
    commands = []

    for i, (lon, lat) in enumerate(ring):
        x, y = xy(lon, lat)
        commands.append(
            f'{"M" if i == 0 else "L"}{x:.1f} {y:.1f}'
        )

    return "".join(commands) + "Z"


def _hispaniola_map():
    try:
        import territoire_page

        geo = territoire_page._geo()

        if not geo["pays"] or not geo["sections"]:
            return None

        width = 760
        height = 430

        all_rings = list(geo["pays"]) + [DR]

        xy = _projector(
            all_rings,
            width,
            height,
            margin=30,
        )

        parts = [
            f'<rect width="{width}" height="{height}" '
            f'fill="#edf4fb"/>'
        ]

        # Haïti
        for ring in geo["pays"]:
            parts.append(
                f'<path d="{_svg_path(ring,xy)}" '
                f'fill="#f5f5f1" stroke="#cbd4dd" '
                f'stroke-width="1.1"/>'
            )

        # République dominicaine
        parts.append(
            f'<path d="{_svg_path(DR,xy)}" '
            f'fill="#f5f5f1" stroke="#cbd4dd" '
            f'stroke-width="1.1"/>'
        )

        # Limites départementales haïtiennes, très discrètes
        for _nom, rings in geo["deps"]:
            for ring in rings:
                parts.append(
                    f'<path d="{_svg_path(ring,xy)}" '
                    f'fill="none" stroke="#dfe4ea" '
                    f'stroke-width=".65"/>'
                )

        # Zone enquêtée
        sx = []
        sy = []

        for section in geo["sections"]:
            for ring in section["anneaux"]:
                parts.append(
                    f'<path d="{_svg_path(ring,xy)}" '
                    f'fill="#2f6b4f" stroke="#2f6b4f" '
                    f'stroke-width="1"/>'
                )

                for lon, lat in ring:
                    x, y = xy(lon, lat)
                    sx.append(x)
                    sy.append(y)

        # Cercle de localisation
        if sx and sy:
            cx = (min(sx) + max(sx)) / 2
            cy = (min(sy) + max(sy)) / 2
            radius = (
                max(
                    max(sx) - min(sx),
                    max(sy) - min(sy),
                ) / 2
                + 18
            )

            parts.append(
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" '
                f'r="{radius:.1f}" fill="none" '
                f'stroke="#2f6b4f" stroke-width="1.5" '
                f'stroke-dasharray="5 4"/>'
            )

        # Labels
        hx, hy = xy(-72.20, 19.25)
        dx, dy = xy(-68.90, 19.55)

        parts.append(
            f'<text x="{hx:.1f}" y="{hy:.1f}" '
            f'font-size="12" font-weight="700" '
            f'fill="#8a93a5" letter-spacing="2.2">'
            f'HAÏTI</text>'
        )

        parts.append(
            f'<text x="{dx:.1f}" y="{dy:.1f}" '
            f'font-size="11" font-weight="700" '
            f'fill="#8a93a5" letter-spacing="1.3">'
            f'RÉPUBLIQUE DOMINICAINE</text>'
        )

        return (
            f'<svg viewBox="0 0 {width} {height}" '
            f'xmlns="http://www.w3.org/2000/svg" '
            f'font-family="Inter,Arial,sans-serif">'
            + "".join(parts)
            + "</svg>"
        )

    except Exception:
        return None


# ================================================================
# PAGE 1
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

    rows = []

    for a, b in zip(left_names, right_names):
        rows.append(
            f"""
            <tr>
                <td>{_e(a)}</td>
                <td class="number">{counts[a]}</td>
                <td class="name2">{_e(b)}</td>
                <td class="number">{counts[b]}</td>
            </tr>
            """
        )

    left, right = st.columns(
        [1.02, 1.22],
        gap="large",
    )

    with left:
        st.markdown(
            f"""
            <div class="apri-title">
                {_e(T("study_title"))}
            </div>

            <div class="apri-rule"></div>

            <ul class="apri-bullets">
                <li>{_e(T("study_b1"))}</li>
                <li>{_e(T("study_b2"))}</li>
                <li>{_e(T("study_b3"))}</li>
            </ul>

            <div class="apri-section-label">
                {_e(T("sections"))}
            </div>

            <table class="apri-table">
                {''.join(rows)}
            </table>

            <div class="apri-note">
                {_e(T("section_note"))}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        svg = _hispaniola_map()

        if svg:
            st.markdown(
                f"""
                <div class="apri-map">
                    {svg}
                </div>

                <div class="apri-note">
                    {_e(T("map_caption"))}
                </div>
                """,
                unsafe_allow_html=True,
            )


# ================================================================
# PAGE 2
# ================================================================

def _methodology():

    st.markdown(
        f"""
        <div class="apri-title">
            {_e(T("method_title"))}
        </div>

        <div class="apri-rule"></div>

        <div class="apri-method">

            <div class="apri-method-col">
                <h3>{_e(T("method_house_title"))}</h3>

                <p>{_e(T("method_house_p1"))}</p>
                <p>{_e(T("method_house_p2"))}</p>
                <p>{_e(T("method_house_p3"))}</p>
            </div>

            <div class="apri-method-col">
                <h3>{_e(T("method_sat_title"))}</h3>

                <p>{_e(T("method_sat_p1"))}</p>
                <p>{_e(T("method_sat_p2"))}</p>
            </div>

            <div class="apri-method-col">
                <h3>{_e(T("method_bio_title"))}</h3>

                <p>{_e(T("method_bio_p1"))}</p>
                <p>{_e(T("method_bio_p2"))}</p>
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ================================================================
# NAVIGATION BAS
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
# ENTRY POINT
# ================================================================

def render():

    st.session_state.setdefault(
        "portail_etape",
        1,
    )

    current = (
        2
        if st.session_state["portail_etape"] == 2
        else 1
    )

    _tabs(current)

    if current == 1:
        _study_area()
    else:
        _methodology()

    _bottom(current)
