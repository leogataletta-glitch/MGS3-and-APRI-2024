"""Compact language menu with an explicit, always visible current language."""
import streamlit as st
LANGUAGES = {'fr': 'Français', 'en': 'English', 'es': 'Español', 'ht': 'Kreyòl ayisyen'}

def render(callback, mobile=False):
    key = 'navigation_language_mobile' if mobile else 'navigation_language_desktop'
    current = st.session_state.get('choix_langue', 'fr')
    with st.container(key=key):
        with st.popover('🌐 ' + LANGUAGES.get(current, 'Français'), use_container_width=True):
            for code, label in LANGUAGES.items():
                if st.button(label, key=key + '_option_' + code,
                             type='primary' if current == code else 'secondary', use_container_width=True):
                    callback(code)
                    st.rerun()
    root = '#root ' + '.stApp' * 70 + ' .st-key-' + key
    st.markdown('<style>' + root + '{width:170px!important;max-width:100%!important;margin:0!important;}' + root + ' [data-testid="stPopover"]>button{width:100%!important;min-height:38px!important;padding:6px 12px!important;border:1px solid #dce7e4!important;background:white!important;}' + root + ' [data-testid="stPopover"]>button p{font-size:12px!important;color:#18333b!important;white-space:nowrap!important;}</style>', unsafe_allow_html=True)

    option = '#root ' + '.stApp' * 80 + ' [class*="st-key-' + key + '_option_"] button'
    st.markdown('<style>' + option + '{min-height:36px!important;height:36px!important;padding:6px 12px!important;border:0!important;border-radius:6px!important;box-shadow:none!important;background:white!important;justify-content:flex-start!important;}' + option + ' p{font-size:13px!important;color:#18333b!important;margin:0!important;}' + option + '[kind="primary"]{background:#e8f4ef!important;}</style>', unsafe_allow_html=True)
