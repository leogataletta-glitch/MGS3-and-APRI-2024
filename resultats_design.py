"""Results-page presentation based on the approved visual reference."""
import streamlit as st


def render(active, fr):
    page = '.stApp.stApp.stApp.stApp.stApp .st-key-zone_page'
    main = page + ' .st-key-ong_ra_vue'
    theme = page + ' .st-key-ong_exb_theme_ong'
    source = page + ' .st-key-ra_source'
    st.markdown(f'''<style>
    {source} [role="radiogroup"]{{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;width:min(100%,760px)!important;gap:0!important;padding:4px!important;border:1px solid #dce5df!important;border-radius:24px!important;background:white!important;}}
    {theme} [role="radiogroup"]{{position:relative!important;display:grid!important;grid-template-columns:repeat(30,minmax(0,1fr))!important;grid-template-rows:52px 52px!important;gap:12px 0!important;padding:0 4px!important;border:0!important;background:white!important;}}
    {theme} [role="radiogroup"]::before,{theme} [role="radiogroup"]::after{{content:"";position:absolute;left:0;right:0;height:52px;box-sizing:border-box;border:1px solid #cdd7d8;border-radius:22px;pointer-events:none;}}
    {theme} [role="radiogroup"]::before{{top:0;}}
    {theme} [role="radiogroup"]::after{{bottom:0;}}
    {theme} [role="radiogroup"]>label{{position:relative!important;z-index:1!important;align-self:center!important;}}
    {theme} [role="radiogroup"]>label{{grid-column:span 5!important;}}
    {theme} [role="radiogroup"]>label:nth-child(n+7){{grid-column:span 6!important;}}
    {source} [role="radiogroup"]>label,{theme} [role="radiogroup"]>label{{box-sizing:border-box!important;min-width:0!important;min-height:44px!important;margin:0!important;padding:9px 12px!important;border:0!important;border-radius:20px!important;background:white!important;box-shadow:none!important;justify-content:center!important;text-align:center!important;transition:background .15s,border-color .15s!important;}}
    {source} [role="radiogroup"]>label>div:first-child{{display:none!important;}}
    {source} [role="radiogroup"]>label p,{theme} [role="radiogroup"]>label :is(p,strong){{font:400 14px/1.35 Arial,sans-serif!important;color:#35594c!important;text-transform:none!important;letter-spacing:0!important;margin:0!important;}}
    {theme} [role="radiogroup"]>label p:not(:first-child){{display:none!important;}}
    {source} [role="radiogroup"]>label:hover,{theme} [role="radiogroup"]>label:hover{{background:#eef4ef!important;border-color:#9ab6a6!important;}}
    {source} [role="radiogroup"]>label:has(input:checked),{theme} [role="radiogroup"]>label:has(input:checked){{background:#07543f!important;border-color:#07543f!important;box-shadow:0 2px 5px #123c2514!important;}}
    {source} [role="radiogroup"]>label:has(input:checked) :is(p,strong),{theme} [role="radiogroup"]>label:has(input:checked) :is(p,strong){{color:white!important;font-weight:600!important;}}
    {source} [role="radiogroup"]>label:focus-within,{theme} [role="radiogroup"]>label:focus-within{{outline:2px solid #438d70!important;outline-offset:2px!important;}}
    {page} .st-key-exb_q_zone [data-baseweb="select"]>div{{min-height:50px!important;border:1px solid #cdd7d8!important;border-radius:12px!important;background:white!important;}}
    @media(max-width:760px){{
      {source} [role="radiogroup"]{{grid-template-columns:repeat(2,minmax(0,1fr))!important;}}
      {source} [role="radiogroup"]>label{{flex:1 1 40%!important;}}
      {theme} [role="radiogroup"]{{grid-template-columns:repeat(2,minmax(0,1fr))!important;grid-template-rows:none!important;gap:6px!important;}}
      {theme} [role="radiogroup"]::before,{theme} [role="radiogroup"]::after{{display:none!important;}}
      {theme} [role="radiogroup"]>label:nth-child(n){{grid-column:span 1!important;border-radius:12px!important;}}
    }}
    </style>''',unsafe_allow_html=True)

