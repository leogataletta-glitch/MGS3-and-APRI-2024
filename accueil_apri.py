"""
APRI — Home page
Landscape Resilience Observatory — Sud and Grand'Anse, Haiti
"""

import os
import json
import streamlit as st
import i18n
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

SECTIONS = [
    "Anse à Drick", "Barbois", "Dumont", "Débouchette", "Mouline",
    "Quentin", "Beaulieu", "Blactote", "Dalmette", "Trichet",
]

# These keys are also used by app.py for the left navigation.
TEXTES = {
    "mode_portail": {"en": "Home", "fr": "Accueil"},
    "home_step_1": {"en": "The study area", "fr": "Le territoire d'étude"},
    "home_step_1_sub": {"en": "Where?", "fr": "Où ?"},
    "home_step_2": {"en": "Methodology", "fr": "La méthodologie"},
    "home_step_2_sub": {"en": "What was measured?", "fr": "Qu'a-t-on mesuré ?"},
    "home_title": {"en": "The study area", "fr": "Le territoire d'étude"},
    "home_b1": {"en": "Two pilot areas: Grand'Anse and Sud",
                "fr": "Deux zones pilotes : Grand'Anse et Sud"},
    "home_b2": {"en": "{n} communal sections selected within them",
                "fr": "{n} sections communales sélectionnées en leur sein"},
    "home_b3": {"en": "{n} households surveyed",
                "fr": "{n} ménages enquêtés"},
    "home_sections": {"en": "THE TEN COMMUNAL SECTIONS",
                      "fr": "LES DIX SECTIONS COMMUNALES"},
    "home_note": {
        "en": "The figure beside each name is the number of households surveyed there.",
        "fr": "Le chiffre indiqué à côté de chaque nom correspond au nombre de ménages enquêtés."
    },
    "home_map_caption": {
        "en": "The surveyed area, in the far south-west of the country.",
        "fr": "La zone enquêtée, à l'extrême sud-ouest du pays."
    },
    "home_methodology_action": {"en": "Open methodology", "fr": "Ouvrir la méthodologie"},
}

for key, value in TEXTES.items():
    i18n.DICO.setdefault(key, value)


STYLE = """
<style>
/* Home step cards */
.home-steps-wrap {
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:14px;
    margin-bottom:12px;
}
.home-step-card {
    min-height:58px;
    border:1px solid #e5eaf0;
    border-radius:10px;
    padding:10px 14px;
    box-sizing:border-box;
    background:#fff;
    display:grid;
    grid-template-columns:32px 1fr;
    column-gap:12px;
    align-items:center;
}
.home-step-card.active {
    background:#f2f8f4;
    border-color:#cfe3d7;
    border-bottom:3px solid #2f6b4f;
}
.home-step-number {
    width:30px;
    height:30px;
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#f1f4f8;
    color:#7b8794;
    font-size:13px;
    font-weight:700;
}
.home-step-card.active .home-step-number {
    background:#dcebe2;
    color:#2f6b4f;
}
.home-step-title {
    font-size:14px;
    font-weight:600;
    color:#101728;
    line-height:1.2;
}
.home-step-sub {
    font-size:12px;
    font-weight:500;
    color:#6b7a88;
    margin-top:2px;
}
.home-step-card.active .home-step-sub { color:#2f6b4f; }

/* Remove Streamlit's default button box for the invisible methodology control */
div[class*="st-key-home_methodology"] button {
    position:absolute !important;
    inset:0 !important;
    width:100% !important;
    height:100% !important;
    opacity:0 !important;
    cursor:pointer !important;
    z-index:5 !important;
}
div[class*="st-key-home_methodology"] {
    position:relative !important;
    margin-top:-70px !important;
    height:58px !important;
}

/* Main content: one clean border, no nested rectangles */
.home-main {
    border:1px solid #e1e7ee;
    border-radius:10px;
    padding:18px 14px 12px;
    background:#fff;
    box-sizing:border-box;
}
.home-title {
    font-family:Georgia,"Times New Roman",serif;
    font-size:26px;
    font-weight:400;
    color:#101728;
    line-height:1.15;
    margin:0;
}
.home-line {
    width:40px;
    height:2px;
    background:#2f6b4f;
    margin:10px 0 17px;
}
.home-bullets {
    list-style:none;
    padding:0;
    margin:0;
}
.home-bullets li {
    position:relative;
    padding-left:19px;
    margin-bottom:20px;
    font-size:14px;
    line-height:1.5;
    color:#2b3444;
}
.home-bullets li:before {
    content:"";
    position:absolute;
    left:0;
    top:.55em;
    width:5px;
    height:5px;
    background:#4a8b68;
    border-radius:1px;
}
.home-section-label {
    margin-top:27px;
    margin-bottom:9px;
    font-size:10px;
    font-weight:700;
    letter-spacing:.12em;
    color:#8a93a5;
}
.home-section-table {
    width:100%;
    border-top:1px solid #e6ecf2;
}
.home-section-row {
    display:grid;
    grid-template-columns:1fr 55px 1fr 55px;
    column-gap:8px;
    min-height:31px;
    align-items:center;
    border-bottom:1px solid #eef2f6;
}
.home-section-name { font-size:12.5px; color:#273246; }
.home-section-n {
    font-size:12px;
    font-weight:600;
    color:#657186;
    text-align:right;
}
.home-note {
    font-size:11.5px;
    color:#6b7a88;
    margin-top:8px;
    line-height:1.4;
}
.home-map {
    border:1px solid #e5eaf0;
    border-radius:12px;
    padding:10px;
    background:#fbfcfd;
    box-sizing:border-box;
}
.home-map-caption {
    font-size:12px;
    color:#6b7a88;
    margin:8px 2px 0;
    line-height:1.45;
}
@media(max-width:850px) {
    .home-steps-wrap { grid-template-columns:1fr; }
    .home-section-row { grid-template-columns:1fr 45px 1fr 45px; }
}
</style>
"""


def _e(value):
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _find_file(name):
    for path in (os.path.join(DATA, name), os.path.join(APP_DIR, name)):
        if os.path.exists(path):
            return path
    return None


@st.cache_data(show_spinner=False)
def _get_household_count():
    path = _find_file("croisement_index.json")
    if path:
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            if data.get("n"):
                return int(data["n"])
        except Exception:
            pass

    path = _find_file("resultats.json")
    if path:
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                data = data.get("indicateurs", [])
            values = []
            for row in data:
                value = (row.get("n") or {}).get("Total")
                if value:
                    values.append(int(value))
            if values:
                return max(set(values), key=values.count)
        except Exception:
            pass

    return 1211


@st.cache_data(show_spinner=False)
def _get_section_counts():
    return {
        "Anse à Drick": 121,
        "Barbois": 121,
        "Beaulieu": 121,
        "Blactote": 120,
        "Dalmette": 125,
        "Dumont": 122,
        "Débouchette": 120,
        "Mouline": 120,
        "Quentin": 116,
        "Trichet": 120,
    }


def _go_methodology():
    # Keep the existing application navigation model.
    st.session_state["portail_etape"] = 2
    st.rerun()


def _render_steps():
    # The visual cards are HTML; the second card has a real Streamlit button
    # placed over it, so clicking it actually changes the application state.
    st.markdown(
        f"""
        <div class="home-steps-wrap">
          <div class="home-step-card active">
            <div class="home-step-number">1</div>
            <div>
              <div class="home-step-title">{_e(T("home_step_1"))}</div>
              <div class="home-step-sub">{_e(T("home_step_1_sub"))}</div>
            </div>
          </div>
          <div class="home-step-card">
            <div class="home-step-number">2</div>
            <div>
              <div class="home-step-title">{_e(T("home_step_2"))}</div>
              <div class="home-step-sub">{_e(T("home_step_2_sub"))}</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # The actual clickable widget is visually hidden but covers card 2.
    st.button(
        T("home_methodology_action"),
        key="home_methodology",
        on_click=_go_methodology,
        use_container_width=True,
    )


def _render_study_area():
    households = _get_household_count()
    counts = _get_section_counts()
    men = f"{households:,}".replace(",", " ")

    # One single HTML block for the left content prevents the broken
    # open-div / close-div behaviour visible in the previous version.
    left_sections = ["Anse à Drick", "Barbois", "Beaulieu", "Blactote", "Dalmette"]
    right_sections = ["Dumont", "Débouchette", "Quentin", "Trichet", "Mouline"]

    rows = []
    for a, b in zip(left_sections, right_sections):
        rows.append(
            f"""
            <div class="home-section-row">
              <div class="home-section-name">{_e(a)}</div>
              <div class="home-section-n">{counts.get(a, "—")}</div>
              <div class="home-section-name">{_e(b)}</div>
              <div class="home-section-n">{counts.get(b, "—")}</div>
            </div>
            """
        )

    left_html = f"""
    <div class="home-main">
      <div class="home-title">{_e(T("home_title"))}</div>
      <div class="home-line"></div>
      <ul class="home-bullets">
        <li>{_e(T("home_b1"))}</li>
        <li>{_e(T("home_b2", n=len(SECTIONS)))}</li>
        <li>{_e(T("home_b3", n=men))}</li>
      </ul>
      <div class="home-section-label">{_e(T("home_sections"))}</div>
      <div class="home-section-table">{''.join(rows)}</div>
      <div class="home-note">{_e(T("home_note"))}</div>
    </div>
    """

    left, right = st.columns([1.05, 1.25], gap="large")

    with left:
        st.markdown(left_html, unsafe_allow_html=True)

    with right:
        try:
            import territoire_page
            vignette = territoire_page._vignette(territoire_page._geo(), 520, 370)
            if vignette:
                st.markdown(
                    '<div class="home-map">'
                    + vignette
                    + f'<div class="home-map-caption">{_e(T("home_map_caption"))}</div>'
                    + '</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.info("Map unavailable.")
        except Exception:
            st.info("Map unavailable.")


def render():
    st.markdown(STYLE, unsafe_allow_html=True)
    _render_steps()
    _render_study_area()
