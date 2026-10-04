"""Straight navigation edge and continuous desktop navigation bands."""
import streamlit as st


def render():
    st.markdown("""<style>
    /* Restrained shared surfaces: flat cards, one outline per control. */
    #root .stApp .st-key-zone_page :is(.cad-carte,.cad-c,.sx-carte,.sx-k,.ex-k,.int-box,.int-perf,.int-paq,.ap-c,.step-card){box-shadow:none!important;border-radius:0!important;background:transparent!important;border:0!important;padding:16px 0!important;}
    #root .stApp .st-key-zone_page :is([data-testid="stSelectbox"],[data-testid="stMultiSelect"]){border:0!important;border-radius:0!important;background:transparent!important;padding:0!important;box-shadow:none!important;}
    #root .stApp .st-key-zone_page :is([data-testid="stSelectbox"],[data-testid="stMultiSelect"]) :is([data-baseweb="select"]>div,[data-rac][role="group"]){border-radius:5px!important;box-shadow:none!important;}
    #root .stApp .st-key-zone_page :is(.stButton,.stDownloadButton)>button{box-shadow:none!important;border-radius:5px!important;}
    #root .stApp .st-key-zone_page :is(.cad-note,.sx-note,.ap-note){background:transparent!important;box-shadow:none!important;border:0!important;}
    #root .stApp .st-key-zone_page :is(.a2-chif,.a2-chif>div){box-shadow:none!important;border-radius:0!important;background:transparent!important;}
    #root .stApp :is(.st-key-ong_cad_vue,.st-key-ong_bcl_vue,.st-key-ong_ra_vue,.st-key-ong_int_vue) [role="radiogroup"]>label{box-shadow:none!important;padding:12px 14px!important;min-height:76px!important;}
    #root .stApp :is(.st-key-ong_cad_vue,.st-key-ong_bcl_vue,.st-key-ong_ra_vue,.st-key-ong_int_vue) [role="radiogroup"]>label p:not(:first-child){font-size:12px!important;line-height:1.4!important;margin-top:4px!important;}
    #root .stApp .st-key-zone_page table{box-shadow:none!important;}
    #root .stApp .st-key-zone_page table :is(th,td){border-left:0!important;border-right:0!important;}
    #root .stApp .st-key-zone_page :is(button,input,[role="combobox"]):focus-visible{outline:2px solid #28745c!important;outline-offset:2px!important;}
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
