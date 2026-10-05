"""One compact language dropdown, shared by desktop and mobile navigation."""
import streamlit as st

LANGUAGES = {'fr': 'Français', 'en': 'English', 'es': 'Español', 'ht': 'Kreyòl ayisyen'}


def render(callback, mobile=False):
    container = 'navigation_language_mobile' if mobile else 'navigation_language_desktop'
    key = container + '_select'
    current = st.session_state.get('choix_langue', 'fr')
    st.session_state[key] = current if current in LANGUAGES else 'fr'

    def change():
        callback(st.session_state[key])

    root = '#root ' + '.stApp' * 68 + ' .st-key-' + container
    css = f'''{root}{{width:170px!important;max-width:100%!important;margin:0 0 0 20px!important;padding:0!important;background:transparent!important;}}
    {root} [data-testid="stSelectbox"]{{padding:0!important;border:0!important;}}
    {root} [data-baseweb="select"]>div,{root} [data-rac][role="group"]{{min-height:38px!important;background:#f0f5f4!important;border:1px solid #dce7e4!important;border-radius:10px!important;}}
    {root} :is([role="combobox"],input,span,p){{font-family:Inter,Arial,sans-serif!important;font-size:12px!important;}}
    {root}::before{{display:none!important;}}'''
    st.markdown('<style>' + css.replace('\n', ' ') + '</style>', unsafe_allow_html=True)
    with st.container(key=container):
        st.selectbox('Langue / Language', list(LANGUAGES),
                     format_func=lambda code: '🌐 ' + LANGUAGES[code],
                     key=key, on_change=change, label_visibility='collapsed')
