"""Shared minimalist presentation for APRI's internal pages."""
import html
import streamlit as st

STYLE = """<style>
:root{--apri-green:#123d2c;--apri-text:#34483e;--apri-muted:#65756c;--apri-line:#dfe7e1;}
.stApp .st-key-zone_page h1,.stApp .st-key-zone_page .apri-page-title,.stApp .st-key-zone_page .cad-page-title{font:400 34px/1.25 Georgia,serif!important;color:var(--apri-green)!important;margin:28px 0 12px!important;letter-spacing:0!important;}
.stApp .st-key-zone_page h2,.stApp .st-key-zone_page h3,.stApp .st-key-zone_page .titre-bloc,.stApp .st-key-zone_page .cad-h,.stApp .st-key-zone_page .cad-model-title,.stApp .st-key-zone_page .ap-h,.stApp .st-key-zone_page .ex-titre{font:400 24px/1.35 Georgia,serif!important;color:var(--apri-green)!important;letter-spacing:0!important;text-transform:none!important;}
.stApp .st-key-zone_page .apri-page-intro,.stApp .st-key-zone_page p.cad-page-intro{font:15px/1.7 Arial,sans-serif!important;color:var(--apri-muted)!important;margin:0 0 24px!important;text-align:left!important;}
.stApp .st-key-zone_page p{line-height:1.7!important;text-align:left!important;hyphens:none!important;}
.stApp .st-key-zone_page :is(.cad-carte,.cad-c,.sx-carte,.sx-k,.ex-k,.int-box,.int-perf,.int-paq,.ap-c){background:transparent!important;border:0!important;border-top:1px solid var(--apri-line)!important;border-radius:0!important;box-shadow:none!important;padding:20px 0!important;}
.stApp .st-key-zone_page :is(.cad-carte-t,.cad-c-t,.int-box-t,.int-paq-t,.ap-c-t){font:400 20px/1.4 Georgia,serif!important;color:var(--apri-green)!important;letter-spacing:0!important;text-transform:none!important;}
.stApp .st-key-zone_page .cad-c-n{font:13px/1.5 Arial,sans-serif!important;color:var(--apri-muted)!important;}
.stApp .st-key-zone_page .ex-etape .n,.stApp .st-key-zone_page .cad-ch-n{background:transparent!important;color:var(--apri-muted)!important;border-radius:0!important;font-weight:400!important;}
.stApp .st-key-zone_page .ex-etape .t{font-size:14px!important;text-transform:none!important;letter-spacing:0!important;white-space:normal!important;}
.stApp .st-key-zone_page [data-testid="stWidgetLabel"] p{font-size:14px!important;font-weight:500!important;letter-spacing:0!important;text-transform:none!important;}
.stApp .st-key-zone_page :is([data-baseweb="select"]>div,[data-baseweb="input"],[data-baseweb="textarea"]){background:#fff!important;border-color:#cbd8cf!important;border-radius:4px!important;box-shadow:none!important;min-height:42px;}
.stApp .st-key-zone_page :is(.stButton,.stDownloadButton) button{border-radius:4px!important;box-shadow:none!important;min-height:42px;font-weight:500!important;}
.stApp .st-key-zone_page :is(.stButton,.stDownloadButton) button[kind="secondary"]{background:#fff!important;color:var(--apri-green)!important;border:1px solid #cbd8cf!important;}
.stApp .st-key-zone_page :is(.stButton,.stDownloadButton) button[kind="primary"]{background:var(--apri-green)!important;color:white!important;border:1px solid var(--apri-green)!important;}
.stApp .st-key-zone_page :is(button,input,textarea,summary):focus-visible,.stApp .st-key-zone_page [role="radiogroup"] label:has(input:focus-visible){outline:2px solid #26734f!important;outline-offset:3px!important;}
.stApp .st-key-zone_page [data-testid="stExpander"] details{background:white!important;border:0!important;border-top:1px solid var(--apri-line)!important;border-bottom:1px solid var(--apri-line)!important;border-radius:0!important;box-shadow:none!important;}
.stApp .st-key-zone_page [data-testid="stExpander"] summary{min-height:44px;padding:12px 4px!important;}
.stApp .st-key-zone_page table{border-collapse:collapse!important;}
.stApp .st-key-zone_page th,.stApp .st-key-zone_page td{padding-top:12px!important;padding-bottom:12px!important;border-bottom:1px solid #edf1ee!important;}
.stApp .st-key-zone_page [data-testid="stTabs"] [data-baseweb="tab"]{min-height:44px;background:transparent!important;border-radius:0!important;}
.stApp .st-key-zone_page [data-testid="stTabs"] [data-baseweb="tab"] p{font:500 14px/1.5 Arial,sans-serif!important;}
.stApp .st-key-zone_page [data-testid="stTabs"] [aria-selected="true"] p{color:var(--apri-green)!important;}
.stApp .st-key-zone_page [data-testid="stTabs"] [data-baseweb="tab-highlight"]{background:var(--apri-green)!important;height:2px!important;}
@media(max-width:700px){.stApp .st-key-zone_page .apri-page-title,.stApp .st-key-zone_page .cad-page-title{font-size:28px!important;}.stApp .st-key-zone_page :is(.stButton,.stDownloadButton) button{min-height:44px;}}
</style>"""

PAGES = {
    "accueil": ("Le territoire", "The territory", "Explorer les paysages et les sections communales.", "Explore the landscapes and communal sections."),
    "dimensions": ("Analyse des résultats", "Results analysis", "Choisir une vue, préciser les filtres, puis explorer les résultats.", "Choose a view, set the filters, then explore the results."),
    "boucles": ("Boucles de rétroaction", "Feedback loops", "Construire le système, examiner ses relations et tester les leviers d’action.", "Build the system, examine its relationships and test intervention levers."),
    "actions": ("Fiches d’intervention", "Intervention profiles", "Identifier les leviers et consulter les actions associées.", "Identify levers and explore the associated actions."),
    "donnees": ("Données et documents", "Data and documents", "Consulter et télécharger les ressources de l’observatoire.", "Browse and download the observatory’s resources."),
    "apropos": ("À propos d’APRI", "About APRI", "L’initiative, ses paysages et ses objectifs.", "The initiative, its landscapes and its objectives."),
    "contact": ("Nous contacter", "Contact us", "", ""),
}

def appliquer():
    st.markdown(STYLE, unsafe_allow_html=True)

def entete(page, fr=True):
    if page not in PAGES:
        return
    title_fr, title_en, intro_fr, intro_en = PAGES[page]
    title, intro = (title_fr, intro_fr) if fr else (title_en, intro_en)
    st.markdown(f'<h1 class="apri-page-title">{html.escape(title)}</h1>'
                + (f'<p class="apri-page-intro">{html.escape(intro)}</p>' if intro else ''), unsafe_allow_html=True)

