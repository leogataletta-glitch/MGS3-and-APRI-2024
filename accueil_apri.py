"""
APRI — Page d'accueil
Landscape Resilience Observatory
Sud and Grand'Anse, Haiti
"""

import os
import json
import streamlit as st
import i18n

from i18n import T


APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

SECTIONS = [
    "Anse à Drick",
    "Barbois",
    "Dumont",
    "Débouchette",
    "Mouline",
    "Quentin",
    "Beaulieu",
    "Blactote",
    "Dalmette",
    "Trichet",
]


# ============================================================
# TEXTES
# ============================================================

TEXTES = {
    "home_step_1": {
        "en": "The study area",
        "fr": "Le territoire d'étude",
    },
    "home_step_1_sub": {
        "en": "Where?",
        "fr": "Où ?",
    },
    "home_step_2": {
        "en": "Methodology",
        "fr": "La méthodologie",
    },
    "home_step_2_sub": {
        "en": "What was measured?",
        "fr": "Qu'a-t-on mesuré ?",
    },
    "home_title": {
        "en": "The study area",
        "fr": "Le territoire d'étude",
    },
    "home_b1": {
        "en": "Two pilot areas: Grand'Anse and Sud",
        "fr": "Deux zones pilotes : Grand'Anse et Sud",
    },
    "home_b2": {
        "en": "{n} communal sections selected within them",
        "fr": "{n} sections communales sélectionnées en leur sein",
    },
    "home_b3": {
        "en": "{n} households surveyed",
        "fr": "{n} ménages enquêtés",
    },
    "home_sections": {
        "en": "THE TEN COMMUNAL SECTIONS",
        "fr": "LES DIX SECTIONS COMMUNALES",
    },
    "home_map_caption": {
        "en": "The surveyed area, in the far south-west of the country.",
        "fr": "La zone enquêtée, à l'extrême sud-ouest du pays.",
    },
    "home_next": {
        "en": "Next",
        "fr": "Suivant",
    },
    "home_methodology_button": {
        "en": "Methodology",
        "fr": "Méthodologie",
    },
}


for key, value in TEXTES.items():
    i18n.DICO.setdefault(key, value)


# ============================================================
# CSS
# ============================================================

STYLE = """
<style>

/* =========================================================
   TOP STEP CARDS
   ========================================================= */

.home-steps {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    margin: 0 0 12px 0;
}

.home-step {
    min-height: 58px;
    background: #ffffff;
    border: 1px solid #e5eaf0;
    border-radius: 10px;
    padding: 10px 14px;
    display: grid;
    grid-template-columns: 32px 1fr;
    column-gap: 12px;
    align-items: center;
}

.home-step.active {
    background: #f2f8f4;
    border-color: #cfe3d7;
    border-bottom: 3px solid #2f6b4f;
}

.home-step-number {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f1f4f8;
    color: #7b8794;
    font-size: 13px;
    font-weight: 700;
}

.home-step.active .home-step-number {
    background: #dcebe2;
    color: #2f6b4f;
}

.home-step-title {
    font-size: 14px;
    font-weight: 600;
    color: #101728;
    line-height: 1.2;
}

.home-step-sub {
    font-size: 12px;
    font-weight: 500;
    color: #6b7a88;
    margin-top: 2px;
    line-height: 1.2;
}

.home-step.active .home-step-sub {
    color: #2f6b4f;
}


/* =========================================================
   MAIN CONTENT
   ========================================================= */

.home-panel {
    background: #ffffff;
    border: 1px solid #e1e7ee;
    border-radius: 10px;
    padding: 18px 14px 12px 14px;
}

.home-title {
    font-family: Georgia, "Times New Roman", serif;
    font-size: 26px;
    font-weight: 400;
    color: #101728;
    margin: 0;
    line-height: 1.15;
}

.home-line {
    width: 40px;
    height: 2px;
    background: #2f6b4f;
    margin: 10px 0 17px 0;
}


/* =========================================================
   BULLETS
   ========================================================= */

.home-bullets {
    list-style: none;
    padding: 0;
    margin: 0;
    max-width: 520px;
}

.home-bullets li {
    position: relative;
    padding-left: 19px;
    margin-bottom: 20px;
    font-size: 14px;
    line-height: 1.5;
    color: #2b3444;
}

.home-bullets li::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0.55em;
    width: 5px;
    height: 5px;
    background: #4a8b68;
    border-radius: 1px;
}


/* =========================================================
   SECTION LIST
   ========================================================= */

.home-section-label {
    margin-top: 27px;
    margin-bottom: 9px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .12em;
    color: #8a93a5;
}

.home-section-table {
    width: 100%;
    border-top: 1px solid #e6ecf2;
}

.home-section-row {
    display: grid;
    grid-template-columns: 1fr 55px 1fr 55px;
    column-gap: 8px;
    min-height: 31px;
    align-items: center;
    border-bottom: 1px solid #eef2f6;
}

.home-section-name {
    font-size: 12.5px;
    color: #273246;
}

.home-section-n {
    font-size: 12px;
    font-weight: 600;
    color: #657186;
    text-align: right;
}


/* =========================================================
   MAP
   ========================================================= */

.home-map {
    border: 1px solid #e5eaf0;
    border-radius: 12px;
    padding: 10px;
    background: #fbfcfd;
}

.home-map-caption {
    font-size: 12px;
    color: #6b7a88;
    margin: 8px 2px 0 2px;
    line-height: 1.45;
}


/* =========================================================
   NEXT BUTTON
   ========================================================= */

.home-next {
    margin-top: 14px;
}

@media (max-width: 850px) {
    .home-steps {
        grid-template-columns: 1fr;
    }

    .home-section-row {
        grid-template-columns: 1fr 45px 1fr 45px;
    }
}

</style>
"""


# ============================================================
# HELPERS
# ============================================================

def _e(value):
    """HTML escape simple."""
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _find_file(name):
    candidates = [
        os.path.join(DATA, name),
        os.path.join(APP_DIR, name),
    ]

    for path in candidates:
        if os.path.exists(path):
            return path

    return None


@st.cache_data(show_spinner=False)
def _get_household_count():
    """
    Récupère le nombre de ménages depuis croisement_index.json.
    Fallback sur resultats.json si nécessaire.
    """

    # ---------------------------------------------------------
    # Premier choix : croisement_index.json
    # ---------------------------------------------------------

    path = _find_file("croisement_index.json")

    if path:
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            n = data.get("n")

            if n:
                return int(n)

        except Exception:
            pass

    # ---------------------------------------------------------
    # Deuxième choix : resultats.json
    # ---------------------------------------------------------

    path = _find_file("resultats.json")

    if path:
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict):
                data = data.get("indicateurs", [])

            bases = []

            for row in data:
                n = row.get("n") or {}
                value = n.get("Total")

                if value:
                    bases.append(int(value))

            if bases:
                return max(set(bases), key=bases.count)

        except Exception:
            pass

    return 1211


@st.cache_data(show_spinner=False)
def _get_section_counts():

    counts = {
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

    return counts


def _go_methodology():
    st.session_state["app_mode"] = "methodologie"


# ============================================================
# TOP STEPS
# ============================================================

def _render_steps():

    col1, col2 = st.columns(2, gap="medium")

    with col1:

        st.markdown(
            f"""
            <div class="home-step active">
                <div class="home-step-number">1</div>
                <div>
                    <div class="home-step-title">
                        {_e(T("home_step_1"))}
                    </div>
                    <div class="home-step-sub">
                        {_e(T("home_step_1_sub"))}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            """
            <div class="home-step">
                <div class="home-step-number">2</div>
                <div>
                    <div class="home-step-title">
                        Methodology
                    </div>
                    <div class="home-step-sub">
                        What was measured?
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Open methodology",
            key="home_methodology_button",
            use_container_width=True,
        ):
            _go_methodology()


# ============================================================
# STUDY AREA
# ============================================================

def _render_study_area():

    households = _get_household_count()
    counts = _get_section_counts()

    households_display = f"{households:,}".replace(",", " ")

    st.markdown(
        '<div class="home-panel">',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="home-title">
            {_e(T("home_title"))}
        </div>
        <div class="home-line"></div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns(
        [1.05, 1.25],
        gap="large",
    )

    # ========================================================
    # LEFT
    # ========================================================

    with left:

        st.markdown(
            f"""
            <ul class="home-bullets">
                <li>{_e(T("home_b1"))}</li>
                <li>{_e(T("home_b2", n=len(SECTIONS)))}</li>
                <li>{_e(T("home_b3", n=households_display))}</li>
            </ul>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="home-section-label">
                {_e(T("home_sections"))}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Deux colonnes de sections, comme dans la référence.
        left_sections = [
            "Anse à Drick",
            "Barbois",
            "Beaulieu",
            "Blactote",
            "Dalmette",
        ]

        right_sections = [
            "Dumont",
            "Débouchette",
            "Quentin",
            "Trichet",
            "Mouline",
        ]

        rows = []

        for i in range(5):

            left_name = left_sections[i]
            right_name = right_sections[i]

            rows.append(
                f"""
                <div class="home-section-row">
                    <div class="home-section-name">
                        {_e(left_name)}
                    </div>

                    <div class="home-section-n">
                        {counts.get(left_name, "—")}
                    </div>

                    <div class="home-section-name">
                        {_e(right_name)}
                    </div>

                    <div class="home-section-n">
                        {counts.get(right_name, "—")}
                    </div>
                </div>
                """
            )

        st.markdown(
            '<div class="home-section-table">'
            + "".join(rows)
            + "</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="
                font-size:11.5px;
                color:#6b7a88;
                margin-top:8px;
                line-height:1.4;
            ">
                The figure beside each name is the number of households surveyed there.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ========================================================
    # RIGHT — MAP
    # ========================================================

    with right:

        try:

            import territoire_page

            vignette = territoire_page._vignette(
                territoire_page._geo(),
                520,
                370,
            )

            if vignette:

                st.markdown(
                    '<div class="home-map">',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    vignette,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"""
                    <div class="home-map-caption">
                        {_e(T("home_map_caption"))}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True,
                )

            else:
                st.info("Map unavailable.")

        except Exception:

            st.info("Map unavailable.")


# ============================================================
# MAIN RENDER
# ============================================================

def render():

    # CSS
    st.markdown(
        STYLE,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Two-step navigation
    # --------------------------------------------------------

    _render_steps()

    # --------------------------------------------------------
    # Main home content
    # --------------------------------------------------------

    _render_study_area()
