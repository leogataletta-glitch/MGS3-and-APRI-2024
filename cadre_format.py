"""Framework navigation and indicator explorer, styled from the user reference."""
import streamlit as st


def appliquer(active):
    root = '.stApp.stApp .st-key-zone_page .st-key-ong_cad_vue'
    st.markdown(f'''<style>
    {root} [role="radiogroup"]{{background:white!important;border-radius:18px!important;padding:8px!important;gap:6px!important;}}
    {root} [role="radiogroup"]>label{{position:relative;min-height:106px!important;padding:20px 16px!important;background:transparent!important;border:1px solid transparent!important;border-radius:14px!important;box-shadow:none!important;}}
    {root} [role="radiogroup"]>label::before{{display:none!important;content:none!important;}}
    {root} [role="radiogroup"]>label p:first-child{{font:700 16px/1.3 Arial,sans-serif!important;text-transform:none!important;letter-spacing:0!important;color:#18202c!important;}}
    {root} [role="radiogroup"]>label p:not(:first-child){{display:block!important;font:400 14px/1.5 Arial,sans-serif!important;color:#65736e!important;margin-top:8px!important;}}
    {root} [role="radiogroup"]>label:nth-child({active}){{background:white!important;border-color:#5b9665!important;box-shadow:none!important;}}
    .cad-explorer-title{{font:700 clamp(32px,4vw,64px)/1.15 Georgia,serif;color:#123d2c;margin:40px 0 22px;}}
    .stApp.stApp .st-key-zone_page .st-key-ong_cad_i_vue [role="radiogroup"]{{display:flex!important;width:440px;max-width:100%;background:white!important;border:1px solid #c9cdd1!important;border-radius:15px!important;padding:0!important;margin-bottom:28px!important;}}
    .stApp.stApp .st-key-zone_page .st-key-ong_cad_i_vue [role="radiogroup"]>label{{min-height:52px!important;padding:12px 16px!important;border-radius:14px!important;background:transparent!important;box-shadow:none!important;}}
    .stApp.stApp .st-key-zone_page .st-key-ong_cad_i_vue [role="radiogroup"]>label p:first-child{{font:400 18px/1.4 Arial,sans-serif!important;letter-spacing:0!important;text-transform:none!important;}}
    .stApp.stApp .st-key-zone_page .st-key-ong_cad_i_vue [role="radiogroup"]>label p:not(:first-child){{display:none!important;}}
    .stApp.stApp .st-key-zone_page .st-key-ong_cad_i_vue [role="radiogroup"]>label:has(input:checked){{background:white!important;}}
    .stApp.stApp .st-key-zone_page .st-key-ong_cad_i_vue [role="radiogroup"]>label:has(input:checked) :is(p,strong){{color:white!important;}}
    .stApp.stApp .st-key-cad_i_dim label p,.stApp.stApp .st-key-cad_i_ind label p{{font-size:18px!important;color:#18202c!important;}}
    .stApp.stApp :is(.st-key-cad_i_dim,.st-key-cad_i_ind) [data-baseweb="select"]>div{{min-height:56px!important;background:white!important;border:1px solid #aeb5bd!important;border-radius:10px!important;font-size:18px!important;}}
    @media(max-width:600px){{{root} [role="radiogroup"]>label p:first-child{{font-size:15px!important;}}}}
    </style>''', unsafe_allow_html=True)
    sub = '.stApp.stApp .st-key-zone_page .st-key-ong_cad_i_vue'
    st.markdown(f'''<style>
    {root} [role="radiogroup"]{{background:transparent!important;padding:0!important;gap:12px!important;}}
    {root} [role="radiogroup"]>label{{min-height:126px!important;border:1px solid #dce0e4!important;border-radius:9px!important;background:white!important;padding:20px 16px!important;}}
    {root} [role="radiogroup"]>label p:first-child strong{{font-weight:700!important;}}
    {root} [role="radiogroup"]>label:nth-child({active}){{background:white!important;border-color:#1f6549!important;box-shadow:inset 0 -5px 0 #176344!important;}}
    .stApp.stApp .cad-explorer-title{{font-size:clamp(30px,3vw,46px)!important;margin:35px 0 8px!important;}}
    .stApp.stApp p.cad-explorer-subtitle{{font-size:22px!important;color:#6b7280!important;line-height:1.5!important;margin:0 0 24px!important;text-align:left!important;}}
    {sub} [role="radiogroup"]{{border:0!important;background:white!important;border-radius:0!important;margin-bottom:0!important;}}
    {sub} [role="radiogroup"]>label{{border-radius:0!important;border-bottom:3px solid transparent!important;}}
    {sub} [role="radiogroup"]>label:has(input:checked){{background:white!important;border-bottom-color:#176344!important;}}
    {sub} [role="radiogroup"]>label:has(input:checked) :is(p,strong){{color:#176344!important;}}
    .stApp.stApp [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] .st-key-cad_i_dim){{background:white!important;border:1px solid #e7e9eb;border-radius:10px;padding:26px 28px!important;}}
    .stApp.stApp .st-key-cad_i_ind [data-baseweb="select"]>div:focus-within{{border-color:#176344!important;box-shadow:0 0 0 1px #176344!important;}}
    @media(max-width:600px){{.stApp.stApp p.cad-explorer-subtitle{{font-size:17px!important;}}}}
    </style>''', unsafe_allow_html=True)
