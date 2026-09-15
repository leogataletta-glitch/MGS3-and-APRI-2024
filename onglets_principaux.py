"""Shared compact white navigation for every main page."""
import streamlit as st


def render(key, codes, selected, description=None):
    root = '.stApp' * 24 + ' .st-key-zone_page .st-key-' + key
    active = list(codes).index(selected) + 1
    st.markdown(f'''<style>
    {root}{{position:relative!important;margin-top:8px!important;}}
    .stApp.stApp.stApp.stApp.stApp .st-key-zone_page:has(.st-key-{key}){{padding-top:0!important;}}
    @media(min-width:1001px){{
      .stApp.stApp.stApp.stApp.stApp .st-key-zone_page:has(.st-key-{key}) [data-testid="stElementContainer"]:has(.apri-page-heading){{display:none!important;}}
      {root}{{margin-top:16px!important;}}
    }}
    {root}::before,{root}::after{{display:none!important;}}
    .stApp.stApp.stApp.stApp.stApp .st-key-{key}_detail{{display:none!important;}}
    {root} [role="radiogroup"]{{display:flex!important;flex-wrap:wrap!important;gap:10px!important;padding:8px!important;margin:0!important;background:white!important;border:0!important;border-radius:0!important;box-shadow:none!important;}}
    {root} [role="radiogroup"]>label{{position:relative!important;flex:1 1 150px!important;grid-column:auto!important;min-width:0!important;min-height:88px!important;padding:14px 16px!important;margin:0!important;border:0!important;border-right:0!important;border-radius:20px!important;background:white!important;box-shadow:none!important;}}
    {root} [role="radiogroup"]>label{{justify-content:center!important;align-items:center!important;text-align:center!important;}}
    {root} [role="radiogroup"]>label::before{{display:none!important;}}
    {root} [role="radiogroup"]>label :is(div,p,span,strong){{font-family:Georgia,serif!important;font-size:12px!important;}}
    {root} [role="radiogroup"]>label p:first-child,{root} [role="radiogroup"]>label strong{{font:700 15px/1.3 Georgia,serif!important;text-transform:none!important;letter-spacing:0!important;color:#104b3b!important;text-align:center!important;}}
    {root} [role="radiogroup"]>label p:not(:first-child){{display:block!important;font:400 12px/1.45 Georgia,serif!important;color:#61708a!important;text-align:center!important;margin-top:4px!important;}}
    {root} [role="radiogroup"]>label:nth-child({active}){{background:white!important;box-shadow:0 5px 18px rgba(25,55,42,.13)!important;border:1px solid #e0e7e2!important;border-radius:20px!important;}}
    {root} [role="radiogroup"]>label:nth-child({active})::after{{display:none!important;content:"";position:absolute;bottom:7px;top:auto;left:calc(50% - 4px);right:auto;width:8px;height:8px;background:#176344;border-radius:50%;}}
    {root} [role="radiogroup"]>label{{cursor:pointer!important;transition:background-color .15s ease,box-shadow .15s ease!important;}}
    {root} [role="radiogroup"]>label :is(div,p,strong,span){{background:transparent!important;}}
    {root} [role="radiogroup"]>label:hover,
    {root} [role="radiogroup"]>label:nth-child({active}):hover{{background:#e8f1eb!important;}}
    {root} [role="radiogroup"]>label:last-child{{border-right:0!important;}}
    </style>''', unsafe_allow_html=True)
