"""Shared orientation and searchable page navigation."""
from html import escape
import streamlit as st
from publication_web import tr


def mobile_label(current):
    return '☰ ' + tr(('Menu', 'Menu', 'Menú', 'Meni')) + ' · ' + current


def render(current, labels, entries, go):
    codes = [code for code, _ in entries]
    with st.container(key='navigation_orientation'):
        left, right = st.columns([3, 2])
        with left:
            home = escape(labels['portail'])
            name = escape(labels.get(current, current))
            text = home if current == 'portail' else f'<a href="?page=portail" target="_self">{home}</a><span aria-hidden="true"> › </span><span aria-current="page">{name}</span>'
            st.markdown(f'<nav class="apri-breadcrumb" aria-label="{escape(tr(("Fil d’Ariane", "Breadcrumb", "Ruta de navegación", "Chemen navigasyon")))}">{text}</nav>', unsafe_allow_html=True)
        with right:
            with st.popover(tr(('Trouver une page', 'Find a page', 'Buscar una página', 'Jwenn yon paj')), use_container_width=True):
                destination = st.selectbox(tr(('Aller à', 'Go to', 'Ir a', 'Ale nan')), [''] + codes,
                    format_func=lambda code: labels[code] if code else tr(('Saisir un nom de page…', 'Type a page name…', 'Escribe el nombre de una página…', 'Tape non yon paj…')),
                    key='navigation_destination')
                if destination:
                    st.session_state['navigation_destination_pending'] = destination
                    go(destination)
                    st.rerun()
    st.markdown('''<style>
    .stApp .st-key-navigation_orientation{margin:0 0 8px!important;}
    .stApp .apri-breadcrumb{font:12px/1.5 Georgia,serif;color:#4b5550;padding:10px 0;}
    .stApp .apri-breadcrumb a{color:#104b3b;text-decoration:underline;text-underline-offset:3px;}
    .stApp .apri-breadcrumb [aria-current]{font-weight:bold;}
    .stApp .st-key-navigation_orientation button{min-height:36px!important;}
    .stApp .st-key-zone_nav button:focus-visible,.stApp .st-key-zone_page button:focus-visible,
    .stApp .st-key-zone_page [role="radiogroup"] label:focus-within{outline:2px solid #104b3b!important;outline-offset:3px!important;}
    @media(min-width:1001px){
      .stApp.stApp div[data-testid="stColumn"]:has(.st-key-zone_page){scrollbar-width:thin!important;scrollbar-color:#a8bcb1 transparent!important;}
      .stApp.stApp div[data-testid="stColumn"]:has(.st-key-zone_page)::-webkit-scrollbar{display:block!important;width:6px!important;}
      .stApp.stApp div[data-testid="stColumn"]:has(.st-key-zone_page)::-webkit-scrollbar-thumb{background:#a8bcb1;border-radius:4px;}
    }
    @media(max-width:700px){.st-key-navigation_orientation [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;}.st-key-navigation_orientation [data-testid="stColumn"]{min-width:0!important;}}
    </style>''', unsafe_allow_html=True)


def reset_destination():
    # Reset before widget creation; navigation occurs only on an explicit choice.
    if st.session_state.pop('navigation_destination_pending', None):
        st.session_state['navigation_destination'] = ''
