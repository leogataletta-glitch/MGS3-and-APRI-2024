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
.stApp .st-key-zone_page [data-testid="stTabs"] [data-baseweb="tab"]{min-height:64px;background:#fff!important;border-radius:0!important;border-right:1px solid #edf1ee!important;padding:12px 18px!important;}
.stApp .st-key-zone_page [data-testid="stTabs"] [data-baseweb="tab"] p{font:500 14px/1.5 Arial,sans-serif!important;}
.stApp .st-key-zone_page [data-testid="stTabs"] [aria-selected="true"] p{color:#35664b!important;}
.stApp .st-key-zone_page [data-testid="stTabs"] [aria-selected="true"]{background:#edf5ef!important;box-shadow:inset 0 3px 0 #78a58a!important;}
.stApp .st-key-zone_page [data-testid="stTabs"] [data-baseweb="tab-highlight"]{background:var(--apri-green)!important;height:2px!important;}
@media(max-width:700px){.stApp .st-key-zone_page .apri-page-title,.stApp .st-key-zone_page .cad-page-title{font-size:28px!important;}.stApp .st-key-zone_page :is(.stButton,.stDownloadButton) button{min-height:44px;}}
</style>"""

PAGES = {
    "methodologie": ("Le cadre de résilience", "The resilience framework", "", ""),
    "accueil": ("Le territoire", "The territory", "Explorer les paysages et les sections communales.", "Explore the landscapes and communal sections."),
    "dimensions": ("Analyse des résultats", "Results analysis", "Choisir une vue, préciser les filtres, puis explorer les résultats.", "Choose a view, set the filters, then explore the results."),
    "boucles": ("Boucles de rétroaction", "Feedback loops", "Construire le système, examiner ses relations et tester les leviers d’action.", "Build the system, examine its relationships and test intervention levers."),
    "actions": ("Fiches d’intervention", "Intervention profiles", "Identifier les leviers et consulter les actions associées.", "Identify levers and explore the associated actions."),
    "donnees": ("Données et documents", "Data and documents", "Consulter et télécharger les ressources de l’observatoire.", "Browse and download the observatory’s resources."),
    "apropos": ("À propos d’APRI", "About APRI", "L’initiative, ses paysages et ses objectifs.", "The initiative, its landscapes and its objectives."),
    "contact": ("Nous contacter", "Contact us", "", ""),
}

# Four layouts, one shared visual language. The homepage owns its hero.
MODELES = {
    "portail": "accueil",
    "dimensions": "donnees",
    "accueil": "presentation", "donnees": "presentation",
    "apropos": "presentation", "contact": "presentation",
    "methodologie": "methode", "boucles": "methode", "actions": "methode",
}

ERGONOMIE = """<style>
.stApp .st-key-zone_ruban{display:none!important;}
.apri-ruban{display:flex;align-items:center;gap:18px;min-height:112px;padding:20px 26px;background:#fff;border-bottom:1px solid #dfe7e1;}
.apri-ruban .apri-brand{width:62px;height:64px;object-fit:contain;flex-shrink:0;}
.apri-ruban .apri-institution{font:18px/1.4 Georgia,serif;color:#123d2c;padding-left:18px;border-left:1px solid #dfe7e1;margin-right:auto;max-width:560px;}
.apri-ruban .apri-institution span{display:block;font-size:16px;color:#65756c;}
.apri-ruban .apri-unep{width:70px;height:auto;margin-left:120px;flex-shrink:0;filter:brightness(0) saturate(100%) invert(22%) sepia(21%) saturate(1030%) hue-rotate(101deg) brightness(85%);}
.stApp .st-key-zone_langue_r{background:#909d96!important;border:0!important;border-radius:999px!important;backdrop-filter:none!important;top:16px!important;right:24px!important;}
.stApp .st-key-zone_langue_r div[class*="st-key-lang_"] div[data-testid="stButton"]>button p{color:#ffffff!important;text-shadow:none!important;}
.stApp .st-key-zone_langue_r div[class*="st-key-lang_"] div[data-testid="stButton"]>button[kind="primary"] p{color:#ffffff!important;font-weight:700!important;}
.stApp .st-key-zone_page:has(.apri-page-heading){padding:56px 24px 48px!important;}
.apri-page-heading:not(:has(p)){padding:0!important;border:0!important;margin:0!important;height:0!important;}
.apri-page-heading{position:relative;padding:8px 120px 12px 0;border-bottom:1px solid #dfe7e1;margin-bottom:16px;}
.stApp .st-key-zone_page .apri-page-heading h1{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;overflow:hidden!important;clip-path:inset(50%)!important;white-space:nowrap!important;border:0!important;}
.stApp .st-key-zone_page .apri-page-heading p{margin:0!important;max-width:780px;}
.stApp .st-key-zone_page:has([data-modele="presentation"]){max-width:1160px;margin-inline:auto;}
.stApp .st-key-zone_page:has([data-modele="methode"]){max-width:1360px;margin-inline:auto;}
.stApp .st-key-zone_page:has([data-modele="donnees"]){max-width:none;}
.stApp .st-key-zone_page :is(.sx-note,.cad-note,.ap-note){font-size:14px!important;line-height:1.7!important;color:#65756c!important;}
.stApp .st-key-zone_page :is(.sx-leg-h,.cad-section-t,.int-section-t){font:500 14px/1.5 Arial,sans-serif!important;letter-spacing:0!important;text-transform:none!important;color:#123d2c!important;}
.stApp .st-key-zone_page [data-testid="stTabs"] [data-baseweb="tab-list"]{gap:8px;border-bottom:1px solid #dfe7e1;}
@media(max-width:900px){.apri-ruban{padding:18px 16px 58px;gap:12px;min-height:156px;}.apri-ruban .apri-institution{font-size:16px;max-width:52%;}.apri-ruban .apri-institution span{font-size:14px;}.apri-ruban .apri-unep{width:56px;margin-left:auto;}.stApp .st-key-zone_langue_r{position:absolute!important;top:16px!important;right:16px!important;margin:0!important;}}
@media(max-width:600px){.apri-ruban .apri-brand{width:44px;height:48px;}.apri-ruban .apri-institution{font-size:14px;padding-left:10px;max-width:none;}.apri-ruban .apri-institution span{font-size:12px;}.apri-ruban .apri-unep{width:44px;}.stApp .st-key-zone_page:has(.apri-page-heading){padding:56px 8px 32px!important;}.apri-page-heading{margin-bottom:16px;}.stApp .st-key-zone_page h1{font-size:28px!important;}.stApp .st-key-zone_page h2,.stApp .st-key-zone_page h3{font-size:22px!important;}}
</style>"""

def ruban(marque, unep, institution):
    """Stable, compact branding for every internal route, in both languages."""
    parts = [html.escape(p) for p in institution.split("|")]
    brand = f'<img class="apri-brand" alt="APRI" src="data:image/png;base64,{marque}">' if marque else ''
    st.markdown(ERGONOMIE + '<header class="apri-ruban">' + brand
                + '<div class="apri-institution">' + parts[0]
                + ''.join(f'<span>{p}</span>' for p in parts[1:]) + '</div>'
                + f'<img class="apri-unep" alt="UNEP" src="data:image/png;base64,{unep}"></header>', unsafe_allow_html=True)

def appliquer():
    st.markdown(STYLE + ERGONOMIE, unsafe_allow_html=True)

def entete(page, fr=True):
    if page not in PAGES:
        return
    title_fr, title_en, intro_fr, intro_en = PAGES[page]
    title, intro = (title_fr, intro_fr) if fr else (title_en, intro_en)
    modele = MODELES.get(page, "presentation")
    st.markdown(f'<div class="apri-page-heading" data-modele="{modele}"><h1 class="apri-page-title">{html.escape(title)}</h1>'
                + (f'<p class="apri-page-intro">{html.escape(intro)}</p>' if intro else '') + '</div>', unsafe_allow_html=True)

