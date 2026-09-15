"""Shared compact white navigation for every main page."""
import streamlit as st


def render(key, codes, selected, description=None):
    root = '.stApp.stApp.stApp.stApp.stApp .st-key-zone_page .st-key-' + key
    active = list(codes).index(selected) + 1
    st.markdown(f'''<style>
    {root}{{position:relative!important;margin-top:24px!important;}}
    .stApp.stApp.stApp.stApp.stApp .st-key-zone_page:has(.st-key-{key}){{padding-top:0!important;}}
    @media(min-width:1001px){{
      .stApp.stApp.stApp.stApp.stApp .st-key-zone_page:has(.st-key-{key}) [data-testid="stElementContainer"]:has(.apri-page-heading){{display:none!important;}}
      {root}{{margin-top:32px!important;}}
    }}
    {root}::before,{root}::after{{display:none!important;}}
    .stApp.stApp.stApp.stApp.stApp .st-key-{key}_detail{{display:none!important;}}
    {root} [role="radiogroup"]{{display:flex!important;flex-wrap:wrap!important;gap:0!important;padding:3px!important;margin:0!important;background:white!important;border:1px solid #a8c2b5!important;border-radius:6px!important;box-shadow:none!important;}}
    {root} [role="radiogroup"]>label{{position:relative!important;flex:1 1 150px!important;grid-column:auto!important;min-width:0!important;min-height:64px!important;padding:8px 14px!important;margin:0!important;border:0!important;border-right:1px solid #dce5df!important;border-radius:0!important;background:white!important;box-shadow:none!important;}}
    {root} [role="radiogroup"]>label::before{{display:none!important;}}
    {root} [role="radiogroup"]>label p:first-child,{root} [role="radiogroup"]>label strong{{font:700 14px/1.3 Arial,sans-serif!important;text-transform:none!important;letter-spacing:0!important;color:#104b3b!important;text-align:left!important;}}
    {root} [role="radiogroup"]>label p:not(:first-child){{display:block!important;font:400 12px/1.35 Arial,sans-serif!important;color:#61708a!important;text-align:left!important;margin-top:4px!important;}}
    {root} [role="radiogroup"]>label:nth-child({active}){{background:#eaf2ed!important;box-shadow:none!important;border:0!important;border-right:1px solid #dce5df!important;border-radius:4px!important;}}
    {root} [role="radiogroup"]>label:nth-child({active})::after{{display:none!important;content:"";position:absolute;bottom:7px;top:auto;left:calc(50% - 4px);right:auto;width:8px;height:8px;background:#176344;border-radius:50%;}}
    {root} [role="radiogroup"]>label{{cursor:pointer!important;transition:background-color .15s ease!important;}}
    {root} [role="radiogroup"]>label :is(div,p,strong,span){{background:transparent!important;}}
    {root} [role="radiogroup"]>label:hover,
    {root} [role="radiogroup"]>label:nth-child({active}):hover{{background:#e8f1eb!important;}}
    {root} [role="radiogroup"]>label:last-child{{border-right:0!important;}}
    </style>''', unsafe_allow_html=True)
