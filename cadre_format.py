"""Framework navigation and indicator explorer, styled from the user reference."""
from urllib.parse import quote
import streamlit as st


def appliquer(active):
    root = '.stApp.stApp .st-key-zone_page .st-key-ong_cad_vue'
    paths = [
        '<path d="M5 20v-7m7 7V4m7 16V9"/>',
        '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 4 16 4 16 0V5M4 12c0 4 16 4 16 0"/>',
        '<rect x="5" y="2" width="14" height="20" rx="2"/><path d="M8 7h8m-8 5h1m4 0h1m-6 5h1m4 0h1"/>',
        '<path d="M20 9a8 8 0 0 0-14-4L3 8m0-5v5h5M4 15a8 8 0 0 0 14 4l3-3m0 5v-5h-5"/>',
        '<path d="M13 3H4v18h12M8 7h4m-4 4h3m1 8 7-7 3 3-7 7-4 1z"/>',
        '<path d="M5 2h9l5 5v15H5zM14 2v6h5M8 12h8m-8 4h8"/>',
        '<path d="m5 3 16 9-16 9z"/>',
    ]
    icons = ''
    for i, path in enumerate(paths, 1):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="%23123d2c" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'+path+'</svg>'
        svg = svg.replace('%23', '#')
        icons += f'{root} [role="radiogroup"]>label:nth-child({i})::before{{background-image:url("data:image/svg+xml,{quote(svg)}");}}'
    st.markdown(f'''<style>
    {root} [role="radiogroup"]{{background:#f0f1f2!important;border-radius:18px!important;padding:8px!important;gap:6px!important;}}
    {root} [role="radiogroup"]>label{{position:relative;min-height:106px!important;padding:58px 10px 12px!important;background:transparent!important;border:1px solid transparent!important;border-radius:14px!important;box-shadow:none!important;}}
    {root} [role="radiogroup"]>label::before{{content:"";position:absolute;top:12px;left:calc(50% - 17px);width:34px;height:34px;background-size:contain;background-repeat:no-repeat;}}
    {root} [role="radiogroup"]>label p:first-child{{font:400 18px/1.3 Arial,sans-serif!important;text-transform:none!important;letter-spacing:0!important;color:#18202c!important;}}
    {root} [role="radiogroup"]>label p:not(:first-child){{display:none!important;}}
    {root} [role="radiogroup"]>label:nth-child({active}){{background:white!important;border-color:#5b9665!important;box-shadow:none!important;}}
    {icons}
    .cad-explorer-title{{font:700 clamp(32px,4vw,64px)/1.15 Georgia,serif;color:#123d2c;margin:40px 0 22px;}}
    .stApp.stApp .st-key-zone_page .st-key-ong_cad_i_vue [role="radiogroup"]{{display:flex!important;width:440px;max-width:100%;background:#f7f8f9!important;border:1px solid #c9cdd1!important;border-radius:15px!important;padding:0!important;margin-bottom:28px!important;}}
    .stApp.stApp .st-key-zone_page .st-key-ong_cad_i_vue [role="radiogroup"]>label{{min-height:52px!important;padding:12px 16px!important;border-radius:14px!important;background:transparent!important;box-shadow:none!important;}}
    .stApp.stApp .st-key-zone_page .st-key-ong_cad_i_vue [role="radiogroup"]>label p:first-child{{font:400 18px/1.4 Arial,sans-serif!important;letter-spacing:0!important;text-transform:none!important;}}
    .stApp.stApp .st-key-zone_page .st-key-ong_cad_i_vue [role="radiogroup"]>label p:not(:first-child){{display:none!important;}}
    .stApp.stApp .st-key-zone_page .st-key-ong_cad_i_vue [role="radiogroup"]>label:has(input:checked){{background:#204f34!important;}}
    .stApp.stApp .st-key-zone_page .st-key-ong_cad_i_vue [role="radiogroup"]>label:has(input:checked) :is(p,strong){{color:white!important;}}
    .stApp.stApp .st-key-cad_i_dim label p,.stApp.stApp .st-key-cad_i_ind label p{{font-size:18px!important;color:#18202c!important;}}
    .stApp.stApp :is(.st-key-cad_i_dim,.st-key-cad_i_ind) [data-baseweb="select"]>div{{min-height:56px!important;background:white!important;border:1px solid #aeb5bd!important;border-radius:10px!important;font-size:18px!important;}}
    @media(max-width:600px){{{root} [role="radiogroup"]>label p:first-child{{font-size:15px!important;}}}}
    </style>''', unsafe_allow_html=True)
    if st.session_state.get('cad_format_choice') == 'Format 2':
        sub = '.stApp.stApp .st-key-zone_page .st-key-ong_cad_i_vue'
        st.markdown(f'''<style>
        {root} [role="radiogroup"]{{background:transparent!important;padding:0!important;gap:12px!important;}}
        {root} [role="radiogroup"]>label{{min-height:126px!important;border:1px solid #dce0e4!important;border-radius:9px!important;background:white!important;padding-top:67px!important;}}
        {root} [role="radiogroup"]>label::before{{top:20px;}}
        {root} [role="radiogroup"]>label:nth-child({active}){{background:#eef4ef!important;border-color:#1f6549!important;}}
        .stApp.stApp .cad-explorer-title{{font-size:clamp(30px,3vw,46px)!important;margin:35px 0 8px!important;}}
        .stApp.stApp p.cad-explorer-subtitle{{font-size:22px!important;color:#6b7280!important;line-height:1.5!important;margin:0 0 24px!important;text-align:left!important;}}
        {sub} [role="radiogroup"]{{border:0!important;background:white!important;border-radius:0!important;margin-bottom:0!important;}}
        {sub} [role="radiogroup"]>label{{border-radius:0!important;border-bottom:3px solid transparent!important;}}
        {sub} [role="radiogroup"]>label:has(input:checked){{background:white!important;border-bottom-color:#176344!important;}}
        {sub} [role="radiogroup"]>label:has(input:checked) :is(p,strong){{color:#176344!important;}}
        .stApp.stApp [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] .st-key-cad_i_dim){{background:#f7f8f7!important;border:1px solid #e7e9eb;border-radius:10px;padding:26px 28px!important;}}
        .stApp.stApp .st-key-cad_i_ind [data-baseweb="select"]>div:focus-within{{border-color:#176344!important;box-shadow:0 0 0 1px #176344!important;}}
        @media(max-width:600px){{.stApp.stApp p.cad-explorer-subtitle{{font-size:17px!important;}}}}
        </style>''', unsafe_allow_html=True)
