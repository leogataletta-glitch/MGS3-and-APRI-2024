"""Temporary per-page font comparison with one shared type scale."""
import streamlit as st
import i18n

FONTS = {
    'portail': ('Arial', 'Arial, sans-serif'),
    'methodologie': ('Georgia', 'Georgia, serif'),
    'dimensions': ('Verdana', 'Verdana, sans-serif'),
    'accueil': ('Trebuchet MS', '"Trebuchet MS", sans-serif'),
    'boucles': ('Arial', 'Arial, sans-serif'),
    'actions': ('Verdana', 'Verdana, sans-serif'),
    'donnees': ('Trebuchet MS', '"Trebuchet MS", sans-serif'),
    'apropos': ('Georgia', 'Georgia, serif'),
    'contact': ('Arial', 'Arial, sans-serif'),
}


def appliquer(mode):
    name, family = FONTS.get(mode, FONTS['portail'])
    root = '.stApp' * 12
    text = ':is(p,span,div,a,label,button,input,textarea,select,li,td,th,dt,dd,h1,h2,h3,h4,h5,h6,strong,em,b,small,summary)'
    exclude = ':not([data-testid="stIconMaterial"]):not([class*="material-icons"]):not([class*="material-symbols"]):not([aria-hidden="true"])'
    st.markdown(f'''<style>
    {root}{{ --apri-font:{family}; --apri-content-size:14px; --apri-tab-size:15px; --apri-nav-size:15px; }}
    {root} {text}{exclude}{{font-family:var(--apri-font)!important;}}
    {root} .st-key-zone_page {text}{exclude}{{font-size:var(--apri-content-size)!important;}}
    {root} .st-key-zone_nav {text}{exclude},
    {root} .st-key-menu_mobile {text}{exclude}{{font-size:var(--apri-nav-size)!important;}}
    {root} .st-key-zone_page :is([role="radiogroup"],[role="tablist"]) {text}{exclude}{{font-size:var(--apri-tab-size)!important;}}
    {root} .type-comparison{{color:#64766b!important;padding:8px 0 12px!important;margin:0!important;line-height:1.5!important;}}
    </style>''', unsafe_allow_html=True)
    lang = i18n.get_lang()
    message = {
        'fr': f'Police à comparer : {name} · Onglets 15 px · Bandeau latéral 15 px · Contenu 14 px',
        'en': f'Font comparison: {name} · Tabs 15 px · Sidebar 15 px · Content 14 px',
        'es': f'Comparación de fuente: {name} · Pestañas 15 px · Barra lateral 15 px · Contenido 14 px',
        'ht': f'Konpare polis: {name} · Onglè 15 px · Ba lateral 15 px · Kontni 14 px',
    }[lang]
    st.markdown(f'<p class="type-comparison">{message}</p>', unsafe_allow_html=True)
