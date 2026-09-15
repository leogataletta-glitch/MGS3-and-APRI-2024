"""Compact, accessible language switch shared by desktop and mobile navigation."""
import streamlit as st


def render(callback, mobile=False):
    key = 'navigation_language_mobile' if mobile else 'navigation_language_desktop'
    root = ('.st-key-' + key) * 24
    st.markdown(f'''<style>
    {root}{{
      width:144px!important;max-width:calc(100% - 60px)!important;margin:8px 48px 16px auto!important;
      position:relative!important;flex-shrink:0!important;overflow:visible!important;
      padding:0!important;border:0!important;border-radius:0;
      background:transparent!important;box-shadow:none!important;
    }}
    {root} [data-testid="stHorizontalBlock"]{{display:flex!important;flex-direction:row!important;flex-wrap:nowrap!important;gap:0!important;}}
    {root} [data-testid="stColumn"]{{min-width:0!important;width:25%!important;max-width:25%!important;flex:0 0 25%!important;}}
    {root} [data-testid="stElementContainer"]{{margin:0!important;}}
    {root} div[data-testid="stButton"] button{{
      padding:6px 5px!important;min-height:32px!important;max-height:32px!important;height:32px!important;width:100%!important;
      border:0!important;border-bottom:2px solid transparent!important;border-radius:0!important;justify-content:center!important;
      box-shadow:none!important;background:transparent!important;color:#58786a!important;
    }}
    {root} div[data-testid="stButton"] button[kind="primary"]{{
      background:transparent!important;color:#17634e!important;border-bottom-color:#257c5d!important;
    }}
    {root} div[data-testid="stButton"] button :is(p,span,strong){{
      font-family:Georgia,serif!important;font-size:10px!important;line-height:1.2!important;letter-spacing:.04em!important;font-weight:700!important;
      text-align:center!important;color:#58786a!important;margin:0!important;
    }}
    {root} div[data-testid="stButton"] button[kind="primary"] :is(p,div){{color:#17634e!important;}}
    {root} div[data-testid="stButton"] button:hover{{background:#dceae180!important;}}
    {root} button:focus-visible{{outline:2px solid #679881!important;outline-offset:2px;}}
    {root}::before{{content:"";position:absolute;left:-22px;top:8px;width:16px;height:16px;background:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%2358786a%22%20stroke-width%3D%221.6%22%3E%3Ccircle%20cx%3D%2212%22%20cy%3D%2212%22%20r%3D%229%22%2F%3E%3Cellipse%20cx%3D%2212%22%20cy%3D%2212%22%20rx%3D%224%22%20ry%3D%229%22%2F%3E%3Cpath%20d%3D%22M3%2012h18M5%206h14M5%2018h14%22%2F%3E%3C%2Fsvg%3E") center/contain no-repeat;pointer-events:none;}}
    </style>''', unsafe_allow_html=True)
    with st.container(key=key):
        cols = st.columns(4, gap='small')
        for col, code in zip(cols, ('en','fr','es','ht')):
            with col:
                if st.button(code.upper(),key=f'{key}_{code}',
                    type='primary' if st.session_state['choix_langue']==code else 'secondary'):
                    callback(code)
                    st.rerun()
