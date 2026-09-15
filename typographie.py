"""Shared Georgia typography across all main pages."""
import streamlit as st


def appliquer(mode=None):
    root = '.stApp' * 12
    text = ':is(p,span,div,a,label,button,input,textarea,select,li,td,th,dt,dd,h1,h2,h3,h4,h5,h6,strong,em,b,small,summary)'
    exclude = ':not([data-testid="stIconMaterial"]):not([class*="material-icons"]):not([class*="material-symbols"]):not([aria-hidden="true"])'
    content_rule = '' if mode == 'portail' else f'{root} .st-key-zone_page {text}{exclude}{{font-size:var(--apri-content-size)!important;}}'
    st.markdown(f'''<style>
    {root}{{ --apri-font:Georgia, serif; --apri-content-size:14px; --apri-tab-size:13px; --apri-nav-size:14px; }}
    {root} {text}{exclude}{{font-family:var(--apri-font)!important;}}
    {content_rule}
    {root} .st-key-zone_page :is(.cad-ch,.cad-nrm){{ --apri-content-size:13px; }}
    {root} .st-key-zone_nav {text}{exclude},
    {root} .st-key-menu_mobile {text}{exclude}{{font-size:var(--apri-nav-size)!important;}}
    {root} .st-key-zone_nav {text}{exclude}.nav-famille{{font-size:12px!important;text-align:center!important;}}
    {root} .st-key-zone_page :is([role="radiogroup"],[role="tablist"]) {text}{exclude}{{font-size:var(--apri-tab-size)!important;}}
    {root} :is(.st-key-navigation_language_desktop,.st-key-navigation_language_mobile) button {text}{exclude}{{font-size:12px!important;}}
    </style>''', unsafe_allow_html=True)
