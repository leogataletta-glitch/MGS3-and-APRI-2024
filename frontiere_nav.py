"""Temporary visual comparison of the navigation edge, shared by all pages."""
from urllib.parse import quote

import streamlit as st
import i18n


def render():
    fr = i18n.get_lang() == "fr"
    # Shared mosaic edge on every page, without a comparison selector.
    choice = "mosaic"
    selector = 'div[data-testid="stColumn"]:has(.st-key-zone_nav)'
    if choice == "original":
        effect = "display:none;"
    elif choice == "fade":
        effect = "background:linear-gradient(90deg,transparent 0%,#ffffff66 40%,white 100%);"
    else:
        if choice == "watercolor":
            shapes = '''<defs><filter id="soft"><feGaussianBlur stdDeviation="2.5"/></filter></defs>
            <path d="M48 0H29Q9 16 28 34T21 68T30 103T20 139T29 178T25 214T29 250H48Z" fill="white" opacity=".6" filter="url(#soft)"/>
            <path d="M48 0H39Q24 20 37 42T32 85T39 127T30 165T39 206T36 250H48Z" fill="white"/>
            <ellipse cx="24" cy="62" rx="8" ry="16" fill="white" opacity=".25"/>
            <ellipse cx="25" cy="180" rx="9" ry="20" fill="white" opacity=".3"/>'''
        else:
            shapes = '''<path d="M48 0H32V18H21V34H37V52H28V71H15V88H34V107H25V123H38V145H20V164H31V182H18V200H36V223H26V250H48Z" fill="white"/>
            <g fill="white" opacity=".5"><rect x="19" y="3" width="9" height="10"/><rect x="9" y="37" width="12" height="11"/><rect x="14" y="112" width="7" height="8"/><rect x="9" y="171" width="12" height="9"/><rect x="18" y="230" width="10" height="12"/></g>'''
        svg = '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="250" viewBox="0 0 48 250">' + shapes + '</svg>'
        effect = 'background:url("data:image/svg+xml,' + quote(svg) + '") right top / 48px 250px repeat-y;'
    border = "1px solid #d9e1da" if choice == "original" else "0"
    st.markdown(f'''<style>
    @media(min-width:1001px){{
      {selector}{{position:relative;border-right:{border}!important;}}
      {selector}::after{{content:"";position:absolute;right:0;top:0;bottom:0;width:48px;
        pointer-events:none;z-index:2;{effect}}}
      {selector}>div{{position:relative;z-index:1;}}
      /* On the map page, mosaic gaps reveal the actual map underneath. */
      .stApp:has(.st-key-territory_map) {selector}{{
        mask-image:linear-gradient(black,black),url("data:image/svg+xml,{quote(svg)}");
        mask-size:100% 100%,48px 250px;
        mask-position:left top,right top;
        mask-repeat:no-repeat,repeat-y;
        mask-composite:exclude;
      }}
      .stApp:has(.st-key-territory_map) {selector}::after{{display:none;}}
      /* One shared overlay cuts backgrounds at exactly the sidebar's mosaic edge. */
      {selector} .st-key-zone_nav div[data-testid="stButton"]>button{{
        border-top-right-radius:0!important;border-bottom-right-radius:0!important;
        padding-right:48px!important;
      }}
    }}
    .st-key-nav_edge_choice{{margin-top:16px;margin-right:14px;}}
    .st-key-nav_edge_choice label p{{font-size:12px!important;color:#526c5f!important;}}
    </style>''', unsafe_allow_html=True)
