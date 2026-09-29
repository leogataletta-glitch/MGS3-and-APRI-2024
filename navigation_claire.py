"""Shared orientation and searchable page navigation."""
import streamlit as st
from publication_web import tr


def mobile_label(current):
    return '☰ ' + tr(('Menu', 'Menu', 'Menú', 'Meni')) + ' · ' + current


def render(current, labels, entries, go):
    st.markdown('''<style>
    .stApp .st-key-zone_nav button:focus-visible,.stApp .st-key-zone_page button:focus-visible,
    .stApp .st-key-zone_page [role="radiogroup"] label:focus-within{outline:2px solid #104b3b!important;outline-offset:3px!important;}
    @media(min-width:1001px){
      .stApp.stApp div[data-testid="stColumn"]:has(.st-key-zone_page){scrollbar-width:thin!important;scrollbar-color:#a8bcb1 transparent!important;}
      .stApp.stApp div[data-testid="stColumn"]:has(.st-key-zone_page)::-webkit-scrollbar{display:block!important;width:6px!important;}
      .stApp.stApp div[data-testid="stColumn"]:has(.st-key-zone_page)::-webkit-scrollbar-thumb{background:#a8bcb1;border-radius:4px;}
    }
    </style>''', unsafe_allow_html=True)


def reset_destination():
    # Reset before widget creation; navigation occurs only on an explicit choice.
    if st.session_state.pop('navigation_destination_pending', None):
        st.session_state['navigation_destination'] = ''
