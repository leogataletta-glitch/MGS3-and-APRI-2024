
"""
APRI — Accueil
Version stable.

Deux vues uniquement :
    1. The study area
    2. Methodology

La navigation reste dans la même page via session_state.
Aucun lien URL, aucun changement de page Streamlit.
"""

import os
import math
import streamlit as st
import i18n
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")


# ============================================================
# TRADUCTIONS
# ============================================================

TEXTES = {
    "mode_portail": {"en": "Home", "fr": "Accueil"},

    "e1": {"en": "The study area", "fr": "Le territoire"},
    "e2": {"en": "Methodology", "fr": "Méthodologie"},

    "study_title": {"en": "The study area", "fr": "Le territoire d'étude"},
    "b1": {"en": "Two pilot areas: Grand'Anse and Sud",
           "fr": "Deux zones pilotes : Grand'Anse et Sud"},
    "b2": {"en": "10 communal sections selected within them",
           "fr": "10 sections communales sélectionnées en leur sein"},
    "b3": {"en": "1 211 households surveyed",
           "fr": "1 211 ménages enquêtés"},
    "sections": {"en": "THE TEN COMMUNAL SECTIONS",
                 "fr": "LES DIX SECTIONS COMMUNALES"},
    "note": {"en": "The figure beside each name is the number of households surveyed there.",
             "fr": "Le chiffre indiqué à côté de chaque nom correspond au nombre de ménages enquêtés."},
    "map_note": {"en": "The surveyed area, in the far south-west of the country.",
                 "fr": "La zone enquêtée, à l'extrême sud-ouest du pays."},

    "method_title": {"en": "Methodology of the survey",
                     "fr": "Méthodologie de l'enquête"},
    "house": {"en": "Household survey", "fr": "Enquête ménage"},
    "house1": {
        "en": "The household survey is the main source of information on living conditions, livelihoods, risk perception and families' capacity to anticipate shocks.",
        "fr": "L'enquête ménage constitue la principale source d'information sur les conditions de vie, les moyens d'existence, la perception des risques et la capacité d'anticipation des familles."
    },
    "house2": {
        "en": "A stratified sampling plan was established to ensure balanced representation of different areas, landscape types and socio-economic contexts.",
        "fr": "Un plan d'échantillonnage stratifié a été mis en place pour assurer une représentation équilibrée des différentes zones, des types de paysage et des contextes socio-économiques."
    },
    "house3": {
        "en": "Within each stratum, households were selected through random geolocation from a georeferenced building database, ensuring objectivity and representativeness.",
        "fr": "À l'intérieur de chaque strate, la sélection des ménages a été réalisée par localisation aléatoire à partir d'une base de bâtiments géoréférencés, garantissant l'objectivité et la représentativité de l'échantillon."
    },
    "sat": {"en": "Satellite imagery", "fr": "Imagerie satellitaire"},
    "sat1": {
        "en": "High-resolution multispectral satellite imagery was used to characterise land cover and land use, track vegetation dynamics and identify landscape changes over time.",
        "fr": "Des images satellitaires multispectrales à haute résolution ont été utilisées pour caractériser l'occupation et l'utilisation des terres, suivre l'évolution du couvert végétal et les changements paysagers au cours du temps."
    },
    "sat2": {
        "en": "Spatial analysis produced objective environmental indicators at the scale of communal sections and landscapes.",
        "fr": "L'analyse spatiale a permis de produire des indicateurs environnementaux objectifs à l'échelle des sections communales et des paysages."
    },
    "bio": {"en": "In-situ biodiversity measurements",
            "fr": "Mesures in situ de la biodiversité"},
    "bio1": {
        "en": "Field surveys were conducted to document biodiversity through flora and fauna inventories, habitat observations and key ecological measurements.",
        "fr": "Des relevés de terrain ont été réalisés pour documenter la biodiversité à travers des inventaires de flore et de faune, des observations d'habitats et des mesures écologiques clés."
    },
    "bio2": {
        "en": "These in-situ data complement information from other sources and make it possible to assess the condition and dynamics of biodiversity in the study territories.",
        "fr": "Ces données in situ viennent compléter les informations issues des autres sources et permettent d'évaluer l'état et la dynamique de la biodiversité dans les territoires étudiés."
    },
    "previous": {"en": "Previous", "fr": "Précédent"},
    "next": {"en": "Next", "fr": "Suivant"},
}

for key, value in TEXTES.items():
    i18n.DICO.setdefault(key, value)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>
/* ---------------- page ---------------- */
.apri-page{
    padding-top:2px;
}

/* ---------------- navigation ---------------- */
.apri-nav-title{
    display:none;
}

.apri-nav-spacer{
    height:1px;
}

/* radio as a simple two-tab selector */
div[data-testid="stRadio"]{
    margin:0 0 18px 0;
}

div[data-testid="stRadio"] > label{
    display:none !important;
}

div[data-testid="stRadio"] [role="radiogroup"]{
    display:grid !important;
    grid-template-columns:1fr 1fr !important;
    gap:40px !important;
    width:100% !important;
}

div[data-testid="stRadio"] [role="radio"]{
    width:100% !important;
    min-height:48px !important;
    padding:12px 8px 10px !important;
    border:0 !important;
    border-radius:0 !important;
    background:transparent !important;
    box-shadow:none !important;
    color:#182132 !important;
    justify-content:center !important;
    position:relative !important;
}

div[data-testid="stRadio"] [role="radio"]:hover{
    background:transparent !important;
    color:#155c37 !important;
}

div[data-testid="stRadio"] [role="radio"][aria-checked="true"]{
    color:#155c37 !important;
}

div[data-testid="stRadio"] [role="radio"] > div:first-child{
    display:none !important;
}

div[data-testid="stRadio"] [role="radio"] > div:last-child{
    width:100% !important;
    text-align:center !important;
    font-family:Arial,sans-serif !important;
    font-size:15px !important;
    font-weight:600 !important;
}

div[data-testid="stRadio"] [role="radio"][aria-checked="true"] > div:last-child::after{
    content:"";
    display:block;
    height:3px;
    background:#1c6349;
    margin:11px 0 -10px 0;
}

div[data-testid="stRadio"] [role="radio"]:not([aria-checked="true"]) > div:last-child::after{
    content:"";
    display:block;
    height:1px;
    background:#dfe5e2;
    margin:12px 0 -10px 0;
}

/* ---------------- titles ---------------- */
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
    margin:12px 0 23px 0;
}

/* ---------------- study area ---------------- */
.apri-bullet{
    color:#263244;
    font-size:14px;
    line-height:1.5;
    margin-bottom:17px;
}

.apri-square{
    color:#2f6b4f;
    margin-right:9px;
}

.apri-label{
    margin-top:26px;
    margin-bottom:8px;
    font-size:10px;
    font-weight:700;
    letter-spacing:.12em;
    color:#718096;
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

.apri-table td.num{
    width:42px;
    text-align:right;
    color:#526174;
}

.apri-table td.name2{
    padding-left:28px;
}

.apri-note{
    margin-top:9px;
    font-size:11.5px;
    line-height:1.4;
    color:#718096;
}

/* ---------------- map ---------------- */
.apri-map svg{
    display:block;
    width:100%;
    height:auto;
}

/* ---------------- methodology ---------------- */
.apri-method-title{
    color:#155c37;
    font-family:Arial,sans-serif;
    font-size:18px;
    font-weight:700;
    line-height:1.25;
    margin-bottom:17px;
}

.apri-method-text{
    color:#182132;
    font-family:Georgia,"Times New Roman",serif;
    font-size:16px;
    line-height:1.55;
    text-align:justify;
    margin-bottom:18px;
}

/* remove Streamlit card borders on this page only */
.apri-clean [data-testid="stVerticalBlockBorderWrapper"]{
    border:0 !important;
    box-shadow:none !important;
    background:transparent !important;
}

/* bottom */
.apri-bottom{
    display:flex;
    justify-content:space-between;
    margin-top:24px;
}

@media(max-width:850px){
    div[data-testid="stRadio"] [role="radiogroup"]{
        gap:12px !important;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# NAVIGATION
# ============================================================

def _step():
    st.session_state.setdefault("portail_etape", 1)

    value = st.radio(
        "APRI navigation",
        options=[1, 2],
        index=0 if st.session_state["portail_etape"] == 1 else 1,
        format_func=lambda x: T("e1") if x == 1 else T("e2"),
        horizontal=True,
        label_visibility="collapsed",
        key="apri_step_radio",
    )

    st.session_state["portail_etape"] = int(value)
    return int(value)


# ============================================================
# MAP
# ============================================================

DR = [
    (-71.95,18.62),(-71.70,18.79),(-71.62,19.17),(-71.71,19.71),
    (-71.59,19.88),(-70.81,19.88),(-70.21,19.62),(-69.95,19.65),
    (-69.77,19.29),(-69.22,19.31),(-69.25,19.02),(-68.81,18.98),
    (-68.32,18.61),(-68.69,18.21),(-69.16,18.42),(-69.62,18.38),
    (-69.95,18.43),(-70.13,18.25),(-70.52,18.18),(-70.67,18.43),
    (-71.00,18.28),(-71.40,17.60),(-71.66,17.76),(-71.71,18.04),
    (-71.69,18.32),(-71.95,18.62)
]

def _project(rings, width=760, height=420, margin=25):
    pts=[p for r in rings for p in r]
    lat=sum(p[1] for p in pts)/len(pts)
    k=math.cos(math.radians(lat))
    xs=[p[0]*k for p in pts]
    ys=[p[1] for p in pts]
    x0,x1=min(xs),max(xs)
    y0,y1=min(ys),max(ys)
    dx=max(x1-x0,1e-9)
    dy=max(y1-y0,1e-9)
    scale=min((width-2*margin)/dx,(height-2*margin)/dy)
    ox=(width-dx*scale)/2
    oy=(height-dy*scale)/2

    def xy(lon,lat):
        return ox+(lon*k-x0)*scale, oy+(y1-lat)*scale
    return xy

def _path(ring, xy):
    return "".join(
        ("M" if i == 0 else "L") + f"{xy(lon,lat)[0]:.1f} {xy(lon,lat)[1]:.1f}"
        for i,(lon,lat) in enumerate(ring)
    ) + "Z"

def _map():
    try:
        import territoire_page
        geo=territoire_page._geo()
        if not geo["pays"]:
            return None

        width,height=760,420
        xy=_project(list(geo["pays"])+[DR],width,height)

        parts=[f'<rect width="{width}" height="{height}" rx="10" fill="#edf4fb"/>']

        for ring in geo["pays"]:
            parts.append(
                f'<path d="{_path(ring,xy)}" fill="#f4f5f1" '
                f'stroke="#cbd4dd" stroke-width="1.1"/>'
            )

        parts.append(
            f'<path d="{_path(DR,xy)}" fill="#f4f5f1" '
            f'stroke="#cbd4dd" stroke-width="1.1"/>'
        )

        sx,sy=[],[]
        for section in geo["sections"]:
            for ring in section["anneaux"]:
                parts.append(
                    f'<path d="{_path(ring,xy)}" fill="#28734f" '
                    f'stroke="#28734f" stroke-width="1"/>'
                )
                for lon,lat in ring:
                    x,y=xy(lon,lat)
                    sx.append(x); sy.append(y)

        if sx:
            cx=(min(sx)+max(sx))/2
            cy=(min(sy)+max(sy))/2
            r=max(max(sx)-min(sx),max(sy)-min(sy))/2+16
            parts.append(
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
                f'fill="none" stroke="#28734f" stroke-width="1.5" '
                f'stroke-dasharray="5 4"/>'
            )

        hx,hy=xy(-72.15,19.25)
        dx,dy=xy(-69.05,19.55)

        parts.append(
            f'<text x="{hx:.1f}" y="{hy:.1f}" font-size="12" '
            f'font-weight="700" fill="#8a93a5" letter-spacing="2">HAÏTI</text>'
        )
        parts.append(
            f'<text x="{dx:.1f}" y="{dy:.1f}" font-size="10.5" '
            f'font-weight="700" fill="#8a93a5" letter-spacing=".7">'
            f'RÉP. DOMINICAINE</text>'
        )

        return (
            f'<svg viewBox="0 0 {width} {height}" '
            f'xmlns="http://www.w3.org/2000/svg" '
            f'font-family="Arial,sans-serif">'
            + "".join(parts)
            + "</svg>"
        )
    except Exception:
        return None


# ============================================================
# STUDY AREA
# ============================================================

def _study_area():
    counts={
        "Anse à Drick":121,"Barbois":121,"Beaulieu":121,"Blactote":120,
        "Dalmette":125,"Dumont":122,"Débouchette":120,"Quentin":116,
        "Trichet":120,"Mouline":120
    }

    left_names=["Anse à Drick","Barbois","Beaulieu","Blactote","Dalmette"]
    right_names=["Dumont","Débouchette","Quentin","Trichet","Mouline"]

    c1,c2=st.columns([1.0,1.18],gap="large")

    with c1:
        st.markdown(f'<div class="apri-title">{T("study_title")}</div>',unsafe_allow_html=True)
        st.markdown('<div class="apri-rule"></div>',unsafe_allow_html=True)

        for key in ("b1","b2","b3"):
            st.markdown(
                f'<div class="apri-bullet"><span class="apri-square">■</span>{T(key)}</div>',
                unsafe_allow_html=True
            )

        st.markdown(
            f'<div class="apri-label">{T("sections")}</div>',
            unsafe_allow_html=True
        )

        rows=[]
        for a,b in zip(left_names,right_names):
            rows.append(
                f"<tr><td>{a}</td><td class='num'>{counts[a]}</td>"
                f"<td class='name2'>{b}</td><td class='num'>{counts[b]}</td></tr>"
            )

        st.markdown(
            f'<table class="apri-table">{"".join(rows)}</table>'
            f'<div class="apri-note">{T("note")}</div>',
            unsafe_allow_html=True
        )

    with c2:
        svg=_map()
        if svg:
            st.markdown(
                f'<div class="apri-map">{svg}</div>'
                f'<div class="apri-map-caption">{T("map_note")}</div>',
                unsafe_allow_html=True
            )


# ============================================================
# METHODOLOGY
# ============================================================

def _methodology():
    st.markdown(
        f'<div class="apri-title">{T("method_title")}</div>'
        '<div class="apri-rule"></div>',
        unsafe_allow_html=True
    )

    c1,c2,c3=st.columns(3,gap="large")

    # Une seule chaîne HTML complète par colonne.
    # Cela évite que Streamlit affiche les balises HTML comme du texte.
    with c1:
        st.markdown(
            f'<div class="apri-method-col apri-method-col-left">'
            f'<div class="apri-method-title">{T("house")}</div>'
            f'<div class="apri-method-text">{T("house1")}</div>'
            f'<div class="apri-method-text">{T("house2")}</div>'
            f'<div class="apri-method-text">{T("house3")}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f'<div class="apri-method-col apri-method-col-middle">'
            f'<div class="apri-method-title">{T("sat")}</div>'
            f'<div class="apri-method-text">{T("sat1")}</div>'
            f'<div class="apri-method-text">{T("sat2")}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f'<div class="apri-method-col apri-method-col-right">'
            f'<div class="apri-method-title">{T("bio")}</div>'
            f'<div class="apri-method-text">{T("bio1")}</div>'
            f'<div class="apri-method-text">{T("bio2")}</div>'
            f'</div>',
            unsafe_allow_html=True
        )


# ============================================================
# BOTTOM
# ============================================================

def _bottom(current):
    left,right=st.columns(2)

    with left:
        if current==2:
            st.button(
                "← " + T("previous"),
                key="apri_previous",
                on_click=_set_step,
                args=(1,),
            )

    with right:
        if current==1:
            st.button(
                T("next") + " →",
                key="apri_next",
                on_click=_set_step,
                args=(2,),
            )


# ============================================================
# RENDER
# ============================================================

def render():
    current=_step()

    if current==1:
        _study_area()
    else:
        _methodology()

    _bottom(current)
