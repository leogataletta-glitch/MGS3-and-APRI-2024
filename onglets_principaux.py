"""Connected horizontal tabs and selected-description panel."""
from html import escape
from urllib.parse import quote
import streamlit as st


def render(key, codes, selected, description):
    root = '.stApp.stApp.stApp.stApp .st-key-zone_page .st-key-' + key
    document = '<path d="M5 2h9l5 5v15H5zM14 2v6h5M8 12h8m-8 4h5"/>'
    chart = '<path d="M3 21h19M5 17V9h3v8m4 0V5h3v12m4 0V2h3v15"/>'
    loop = '<path d="M20 9a8 8 0 0 0-14-4L3 8m0-5v5h5M4 15a8 8 0 0 0 14 4l3-3m0 5v-5h-5"/>'
    database = '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 4 16 4 16 0V5M4 12c0 4 16 4 16 0"/>'
    paths = {'sources':database,'brut':database,'indicateurs':chart,'scores':chart,
             'boucles':loop,'relations':loop,'simulation':'<path d="M3 3v18h19M6 16l5-6 4 3 6-8m-5 0h5v5"/>',
             'environnement':'<path d="M8 5h13M8 12h13M8 19h13M3 5h1M3 12h1M3 19h1"/>'}
    icons = ''
    for i, code in enumerate(codes, 1):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#244739" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'+paths.get(code,document)+'</svg>'
        icons += f'{root} [role="radiogroup"]>label:nth-child({i})::before{{background-image:url("data:image/svg+xml,{quote(svg)}")!important;}}'
    active = list(codes).index(selected)+1
    st.markdown(f'''<style>
    .stApp.stApp.stApp.stApp .st-key-zone_page:has(.st-key-{key}){{padding-top:0!important;}}
    @media(min-width:1001px){{
      .stApp.stApp.stApp.stApp .st-key-zone_page:has(.st-key-{key}) [data-testid="stElementContainer"]:has(.apri-page-heading){{display:none!important;}}
      {root}{{margin-top:-20px!important;}}
    }}
    {root} [role="radiogroup"]{{display:flex!important;flex-wrap:nowrap!important;gap:0!important;padding:0!important;margin:0!important;background:#eef2ed!important;border:0!important;border-radius:26px 26px 0 0!important;overflow-x:auto!important;}}
    {root} [role="radiogroup"]>label{{flex:1 0 140px!important;grid-column:auto!important;position:relative!important;min-height:76px!important;padding:18px 25px 18px 48px!important;margin:0!important;border:1px solid transparent!important;border-bottom:1px solid #d9dfe1!important;border-radius:20px 20px 0 0!important;background:transparent!important;box-shadow:none!important;}}
    {root} [role="radiogroup"]>label::before{{display:block!important;content:""!important;position:absolute!important;top:calc(50% - 13px)!important;left:15px!important;width:26px!important;height:26px!important;background-size:contain!important;background-repeat:no-repeat!important;}}
    {root} [role="radiogroup"]>label p:first-child,{root} [role="radiogroup"]>label strong{{font:400 14px/1.3 Arial,sans-serif!important;text-transform:none!important;letter-spacing:0!important;color:#263a35!important;}}
    {root} [role="radiogroup"]>label p:not(:first-child){{display:none!important;}}
    {root} [role="radiogroup"]>label:nth-child({active}){{background:white!important;border-color:#d9dfe1!important;border-bottom-color:white!important;box-shadow:inset 0 3px 0 #176344!important;}}
    {root} [role="radiogroup"]>label:nth-child({active}) :is(p,strong){{color:#176344!important;font-weight:700!important;}}
    {root} [role="radiogroup"]>label:nth-child({active})::after{{content:"";position:absolute;right:10px;top:calc(50% - 4px);width:8px;height:8px;background:#176344;border-radius:50%;}}
    {root} [data-testid="stElementContainer"]:has(.main-tab-description){{margin:0!important;}}
    {root} .main-tab-description{{background:white;border:1px solid #d9dfe1;border-top:0;border-radius:0 0 18px 18px;padding:25px 30px;margin:0 0 20px;}}
    {root} .main-tab-description p{{font:400 18px/1.5 Arial,sans-serif!important;color:#64716c!important;margin:0!important;}}
    {icons}
    </style>''',unsafe_allow_html=True)
    if description:
        st.markdown('<div class="main-tab-description"><p>'+escape(description)+'</p></div>',unsafe_allow_html=True)
