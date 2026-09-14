"""Compact, accessible language switch shared by desktop and mobile navigation."""
import streamlit as st


def render(callback, mobile=False):
    key = 'navigation_language_mobile' if mobile else 'navigation_language_desktop'
    st.markdown(f'''<style>
    .stApp .st-key-{key}.st-key-{key}{{
      width:82px!important;max-width:82px!important;margin:4px 48px 12px 12px;
      padding:0!important;border:0!important;border-radius:0;
      background:transparent!important;box-shadow:none!important;
    }}
    .stApp .st-key-{key}.st-key-{key} [data-testid="stHorizontalBlock"]{{gap:0!important;}}
    .stApp .st-key-{key}.st-key-{key} [data-testid="stColumn"]{{min-width:0!important;width:50%!important;flex:1 1 0!important;}}
    .stApp .st-key-{key}.st-key-{key} [data-testid="stElementContainer"]{{margin:0!important;}}
    .stApp .st-key-{key}.st-key-{key} div[data-testid="stButton"] button{{
      padding:5px 8px!important;min-height:30px!important;height:30px!important;width:100%!important;
      border:0!important;border-bottom:2px solid transparent!important;border-radius:0!important;justify-content:center!important;
      box-shadow:none!important;background:transparent!important;color:#58786a!important;
    }}
    .stApp .st-key-{key}.st-key-{key} div[data-testid="stButton"] button[kind="primary"]{{
      background:transparent!important;color:#17634e!important;border-bottom-color:#257c5d!important;
    }}
    .stApp .st-key-{key}.st-key-{key} div[data-testid="stButton"] button p{{
      font-size:12px!important;letter-spacing:.08em!important;font-weight:700!important;
      text-align:center!important;color:#58786a!important;margin:0!important;
    }}
    .stApp .st-key-{key}.st-key-{key} div[data-testid="stButton"] button[kind="primary"] :is(p,div){{color:#17634e!important;}}
    .stApp .st-key-{key}.st-key-{key} div[data-testid="stButton"] button:hover{{background:#dceae180!important;}}
    .stApp .st-key-{key}.st-key-{key} button:focus-visible{{outline:2px solid #679881!important;outline-offset:2px;}}
    </style>''', unsafe_allow_html=True)
    with st.container(key=key):
        cols = st.columns(2, gap='small')
        for col, code in zip(cols, ('en','fr')):
            with col:
                st.button(code.upper(),key=f'{key}_{code}',
                    on_click=callback,args=(code,),
                    type='primary' if st.session_state['choix_langue']==code else 'secondary')
