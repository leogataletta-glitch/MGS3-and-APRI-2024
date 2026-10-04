"""Straight navigation edge and continuous desktop navigation bands."""
import streamlit as st


def render():
    st.markdown("""<style>
    /* Style-only elements must not consume flex gaps above navigation. */
    #root .stApp .st-key-zone_page > [data-testid="stElementContainer"]:has([data-testid="stMarkdownContainer"] > style):not(:has([data-testid="stMarkdownContainer"] > :not(style))){display:none!important;}
    @media(min-width:1001px){
      #root .stApp div[data-testid="stColumn"]:has(.st-key-zone_nav){
        background-color:#eef2ed!important;border-right:0!important;
        mask:none!important;-webkit-mask:none!important;
      }
      #root .stApp div[data-testid="stColumn"]:has(.st-key-zone_nav)::after{display:none!important;content:none!important;}
      #root .stApp .st-key-zone_nav{background:transparent!important;}
      #root .stApp .st-key-zone_nav div[data-testid="stButton"]>button{padding-right:14px!important;}
      #root .stApp div[data-testid="stHorizontalBlock"]:has(>div[data-testid="stColumn"] .st-key-zone_nav){gap:0!important;}
      #root .stApp div[data-testid="stColumn"]:has(.st-key-zone_page){container-type:inline-size;}
      #root .stApp .st-key-zone_page:has(:is(.st-key-ong_cad_vue,.st-key-ong_bcl_vue,.st-key-ong_ra_vue,.st-key-ong_int_vue)){padding-top:0!important;}
      #root .stApp :is(.st-key-ong_cad_vue,.st-key-ong_bcl_vue,.st-key-ong_ra_vue,.st-key-ong_int_vue){
        width:100cqw!important;max-width:none!important;
        margin-left:calc(50% - 50cqw)!important;margin-right:0!important;margin-top:0!important;
        background:#eef2ed!important;border-radius:0!important;
      }
      #root .stApp :is(.st-key-ong_cad_vue,.st-key-ong_bcl_vue,.st-key-ong_ra_vue,.st-key-ong_int_vue) [role="radiogroup"]{
        background:#eef2ed!important;border-radius:0!important;border:0!important;margin-top:0!important;
      }
      #root .stApp :is(.st-key-ong_cad_vue,.st-key-ong_bcl_vue,.st-key-ong_ra_vue,.st-key-ong_int_vue) [role="radiogroup"]>label{border-radius:0!important;}
    }
    </style>""",unsafe_allow_html=True)
