"""Compact, accessible language switch shared by desktop and mobile navigation."""
import streamlit as st


def render(callback, mobile=False):
    key = 'lang_mobile' if mobile else 'lang_sidebar'
    st.markdown(f'''<style>
    .stApp .st-key-{key}.st-key-{key}{{
      width:126px!important;max-width:126px!important;margin:8px 48px 22px 12px;
      padding:3px!important;border:1px solid #aac7b7;border-radius:24px;
      background:#f8fbf7;box-shadow:0 2px 7px #244d4210;
    }}
    .stApp .st-key-{key}.st-key-{key} [data-testid="stHorizontalBlock"]{{gap:0!important;}}
    .stApp .st-key-{key}.st-key-{key} [data-testid="stColumn"]{{min-width:0!important;width:50%!important;flex:1 1 0!important;}}
    .stApp .st-key-{key}.st-key-{key} [data-testid="stElementContainer"]{{margin:0!important;}}
    .stApp .st-key-{key}.st-key-{key} div[data-testid="stButton"]>button{{
      padding:7px 12px!important;min-height:32px!important;width:100%!important;
      border:0!important;border-radius:19px!important;justify-content:center!important;
      box-shadow:none!important;background:transparent!important;color:#58786a!important;
    }}
    .stApp .st-key-{key}.st-key-{key} div[data-testid="stButton"]>button[kind="primary"]{{
      background:#245d49!important;color:white!important;
    }}
    .stApp .st-key-{key}.st-key-{key} div[data-testid="stButton"]>button p{{
      font-size:12px!important;letter-spacing:.08em!important;font-weight:700!important;
      text-align:center!important;color:inherit!important;margin:0!important;
    }}
    .stApp .st-key-{key}.st-key-{key} button:focus-visible{{outline:2px solid #679881!important;outline-offset:2px;}}
    </style>''', unsafe_allow_html=True)
    with st.container(key=key):
        cols = st.columns(2, gap='small')
        for col, code in zip(cols, ('en','fr')):
            with col:
                st.button(code.upper(),key=f'{key}_{code}',
                    help='English' if code=='en' else 'Français',
                    on_click=callback,args=(code,),
                    type='primary' if st.session_state['choix_langue']==code else 'secondary')
