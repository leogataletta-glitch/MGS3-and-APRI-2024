"""Results-page presentation based on the approved visual reference."""
import streamlit as st


def choose_format():
    return st.radio(
        'Format', ['Format 1', 'Format 2'], horizontal=True,
        key='results_format_choice', label_visibility='collapsed',
    )


def render(active, fr, display_format='Format 1'):
    page = '.stApp.stApp.stApp.stApp.stApp .st-key-zone_page'
    main = page + ' .st-key-ong_ra_vue'
    theme = page + ' .st-key-ong_exb_theme_ong'
    source = page + ' .st-key-ra_source'
    background = 'white' if display_format == 'Format 2' else '#f3f6f3'
    border = '0' if display_format == 'Format 2' else '1px solid #d3dcd7'
    st.markdown(f'''<style>
    {main}{{margin-top:0!important;}}
    {main}::before,{main}::after{{display:none!important;}}
    {page} .st-key-results_format_choice [role="radiogroup"]{{justify-content:flex-end!important;gap:16px!important;}}
    {page} .st-key-results_format_choice p{{font:400 13px/1.4 Arial,sans-serif!important;}}
    {main} [role="radiogroup"]{{background:{background}!important;border:{border}!important;box-shadow:none!important;border-radius:30px!important;padding:8px!important;gap:10px!important;}}
    {main} [role="radiogroup"]>label{{flex:1 1 0!important;min-width:150px!important;min-height:116px!important;padding:16px 14px 25px!important;border:0!important;border-radius:25px!important;}}
    {main} [role="radiogroup"]>label::before{{display:none!important;}}
    {main} [role="radiogroup"]>label p:first-child,{main} [role="radiogroup"]>label strong{{font:700 17px/1.3 Georgia,serif!important;color:#104b3b!important;}}
    {main} [role="radiogroup"]>label p:not(:first-child){{display:block!important;font:400 14px/1.45 Arial,sans-serif!important;color:#61708a!important;margin-top:6px!important;}}
    {main} [role="radiogroup"]>label:nth-child({active}){{background:white!important;box-shadow:0 7px 20px #193c2526!important;border:0!important;}}
    {main} [role="radiogroup"]>label:nth-child({active})::after{{top:auto!important;bottom:9px!important;left:calc(50% - 4px)!important;right:auto!important;}}
    {page} .st-key-ong_ra_vue_detail,{page} .st-key-ong_ra_vue_description{{display:none!important;}}
    {page} .results-explore-title{{font:700 clamp(32px,3.8vw,56px)/1.2 Georgia,serif!important;text-align:center!important;color:#104b3b!important;margin:36px 0 8px!important;}}
    {page} .results-explore-subtitle{{font:400 22px/1.4 Georgia,serif!important;text-align:center!important;color:#61708a!important;margin:0 0 30px!important;}}
    {source} [role="radiogroup"]{{display:flex!important;flex-wrap:nowrap!important;border:1px solid #cdd7d1!important;border-radius:30px!important;padding:3px!important;background:white!important;gap:0!important;}}
    {source} [role="radiogroup"]>label{{flex:1 1 0!important;margin:0!important;padding:10px 14px!important;border:0!important;border-right:1px solid #e0e5e2!important;border-radius:0!important;justify-content:center!important;}}
    {source} [role="radiogroup"]>label>div:first-child{{display:none!important;}}
    {source} [role="radiogroup"]>label:has(input:checked){{background:#07543f!important;border-radius:26px!important;}}
    {source} [role="radiogroup"]>label:has(input:checked) p{{color:white!important;font-weight:600!important;}}
    {theme} [role="radiogroup"]{{display:grid!important;grid-template-columns:repeat(30,minmax(0,1fr))!important;gap:10px 0!important;background:white!important;}}
    {theme} [role="radiogroup"]>label{{grid-column:span 5!important;min-height:48px!important;padding:10px 12px!important;border:1px solid #d3dcd7!important;border-radius:0!important;}}
    {theme} [role="radiogroup"]>label:nth-child(n+7){{grid-column:span 6!important;}}
    {theme} [role="radiogroup"]>label:first-child,{theme} [role="radiogroup"]>label:nth-child(7){{border-radius:26px 0 0 26px!important;}}
    {theme} [role="radiogroup"]>label:nth-child(6),{theme} [role="radiogroup"]>label:last-child{{border-radius:0 26px 26px 0!important;}}
    {theme} [role="radiogroup"]>label p:first-child,{theme} [role="radiogroup"]>label strong{{font:400 14px/1.35 Arial,sans-serif!important;text-transform:none!important;letter-spacing:0!important;}}
    {theme} [role="radiogroup"]>label p:not(:first-child){{display:none!important;}}
    {theme} [role="radiogroup"]>label:has(input:checked){{background:#07543f!important;border-radius:26px!important;box-shadow:none!important;}}
    {theme} [role="radiogroup"]>label:has(input:checked) :is(p,strong){{color:white!important;font-weight:600!important;}}
    {page} .st-key-exb_q_zone [data-baseweb="select"]>div{{min-height:52px!important;border:1px solid #17513d!important;border-radius:12px!important;background:white!important;}}
    @media(max-width:760px){{
      {source} [role="radiogroup"]{{flex-wrap:wrap!important;}}
      {source} [role="radiogroup"]>label{{flex:1 1 40%!important;}}
      {theme} [role="radiogroup"]{{grid-template-columns:repeat(2,minmax(0,1fr))!important;}}
      {theme} [role="radiogroup"]>label:nth-child(n){{grid-column:span 1!important;border-radius:18px!important;}}
    }}
    </style>''',unsafe_allow_html=True)


def heading(fr):
    title = 'Explorer les résultats' if fr else 'Explore the results'
    subtitle = 'Choisissez une source, un thème et une question.' if fr else 'Choose a source, a theme and a question.'
    st.markdown(f'<h2 class="results-explore-title">{title}</h2><p class="results-explore-subtitle">{subtitle}</p>',unsafe_allow_html=True)
