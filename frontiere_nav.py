"""Straight navigation edge and continuous desktop navigation bands."""
import streamlit as st


def render():
    st.markdown("""<style>
    @media(min-width:1001px){
      .stApp.stApp.stApp div[data-testid="stColumn"]:has(.st-key-zone_nav){
        background:#eef2ed!important;border-right:0!important;
        mask:none!important;-webkit-mask:none!important;
      }
      .stApp.stApp.stApp div[data-testid="stColumn"]:has(.st-key-zone_nav)::after{display:none!important;content:none!important;}
      .stApp.stApp.stApp .st-key-zone_nav{background:transparent!important;}
      .stApp.stApp.stApp .st-key-zone_nav div[data-testid="stButton"]>button{padding-right:14px!important;}
      .stApp.stApp.stApp div[data-testid="stHorizontalBlock"]:has(>div[data-testid="stColumn"] .st-key-zone_nav){gap:0!important;}
      .stApp.stApp.stApp div[data-testid="stColumn"]:has(.st-key-zone_page){container-type:inline-size;}
      .stApp.stApp.stApp.stApp .st-key-zone_page:has(:is(.st-key-ong_cad_vue,.st-key-ong_bcl_vue,.st-key-ong_ra_vue,.st-key-ong_int_vue)){padding-top:0!important;}
      .stApp.stApp.stApp.stApp.stApp :is(.st-key-ong_cad_vue,.st-key-ong_bcl_vue,.st-key-ong_ra_vue,.st-key-ong_int_vue){
        width:100cqw!important;max-width:none!important;
        margin-left:calc(50% - 50cqw)!important;margin-right:0!important;
        background:#eef2ed!important;border-radius:0!important;
      }
      .stApp.stApp.stApp.stApp.stApp.stApp :is(.st-key-ong_cad_vue,.st-key-ong_bcl_vue,.st-key-ong_ra_vue,.st-key-ong_int_vue) [role="radiogroup"]{
        background:#eef2ed!important;border-radius:0!important;border:0!important;margin-top:0!important;
      }
      .stApp.stApp.stApp.stApp.stApp.stApp :is(.st-key-ong_cad_vue,.st-key-ong_bcl_vue,.st-key-ong_ra_vue,.st-key-ong_int_vue) [role="radiogroup"]>label{border-radius:0!important;}
    }
    </style>""",unsafe_allow_html=True)
