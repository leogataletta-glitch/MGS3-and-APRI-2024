"""Session-local palette previews; keep scientific colour encodings unchanged."""
import streamlit as st

PALETTES = {
    'original': ('#174e3e', '#eef2ed'),
    'white': ('#087f5b', '#ffffff'),
    'emerald': ('#087f5b', '#eefaf4'),
    'blue': ('#285d92', '#eff5fc'),
    'slate': ('#525e73', '#f3f4f7'),
    'plum': ('#795674', '#f8f2f7'),
}
NAMES = {
    'fr': ['Actuel', 'Blanc · trait vert', 'Émeraude', 'Bleu', 'Ardoise', 'Prune'],
    'en': ['Current', 'White · green line', 'Emerald', 'Blue', 'Slate', 'Plum'],
    'es': ['Actual', 'Blanco · línea verde', 'Esmeralda', 'Azul', 'Pizarra', 'Ciruela'],
    'ht': ['Aktyèl', 'Blan · liy vèt', 'Emwòd', 'Ble', 'Gri adwaz', 'Prinn'],
}


def selector():
    lang = st.session_state.get('choix_langue', st.session_state.get('lang', 'fr'))
    labels = dict(zip(PALETTES, NAMES.get(lang, NAMES['en'])))
    title = {'fr': 'Apparence', 'en': 'Appearance', 'es': 'Apariencia', 'ht': 'Aparans'}.get(lang, 'Appearance')
    with st.container(key='apri_palette_preview'):
        with st.popover(title, icon=':material/palette:'):
            st.selectbox(title, list(PALETTES), format_func=labels.get, key='apri_palette_choice')
    st.markdown('''<style>
    .st-key-apri_palette_preview{position:fixed!important;right:18px!important;bottom:45px!important;width:auto!important;z-index:90!important;}
    .st-key-apri_palette_preview button{min-height:32px!important;padding:5px 10px!important;background:white!important;color:#34483e!important;border:1px solid #dfe7e1!important;}
    </style>''', unsafe_allow_html=True)


def apply():
    choice = st.session_state.get('apri_palette_choice', 'original')
    if choice not in PALETTES or choice == 'original':
        return
    accent, soft = PALETTES[choice]
    root = '#root ' + '.stApp' * 48
    nav = root + ' .st-key-zone_nav'
    zone = root + ' .st-key-zone_page'
    tabs = root + ' [class*="st-key-ong_"]'
    css = f'''<style>
    {root}{{--apri-green:{accent};--apri-ink:{accent};--apri-soft:{soft};}}
    {zone}{{--apri-green:{accent};--apri-ink:{accent};--apri-soft:{soft};}}
    {root} div[data-testid="stColumn"]:has(.st-key-zone_nav){{background:{soft}!important;border-right:1px solid {accent}!important;}}
    {nav}{{background:transparent!important;}}
    {nav} .nav-famille{{color:#52606a!important;}}
    {nav} button:not([kind="primary"]),{nav} button:not([kind="primary"]) p{{color:#35434b!important;}}
    {nav} button[kind="primary"]{{background:{accent}14!important;border-left:2px solid {accent}!important;}}
    {nav} button[kind="primary"] p{{color:{accent}!important;}}
    {tabs},{tabs} [role="radiogroup"]{{background:{soft}!important;}}
    {tabs} [role="radiogroup"] label{{background:transparent!important;}}
    {tabs} [role="radiogroup"] label p,{tabs} [role="radiogroup"] label strong{{color:#35434b!important;}}
    {tabs} [role="radiogroup"] label:has(input:checked),{tabs} [role="radiogroup"] label:has([aria-checked="true"]),{tabs} [role="radiogroup"] label[aria-checked="true"]{{background:white!important;outline:1px solid {accent}!important;outline-offset:-1px!important;}}
    {zone} :is(h1,h2,h3,.cad-h,.ap-h,.cad-model-title,.cad-ch-v,.cad-so-t,.a2-n){{color:{accent}!important;}}
    {zone} :is([data-baseweb="select"]>div,[data-rac][role="group"]:has(>[role="combobox"]),th){{background:{soft}!important;}}
    {zone} :is(.stButton,.stDownloadButton) button{{color:{accent}!important;border-color:{accent}55!important;}}
    {zone} :is(.stButton,.stDownloadButton) button[kind="primary"]{{background:{accent}!important;color:white!important;}}
    {zone} :is(.stButton,.stDownloadButton) button[kind="primary"] p{{color:white!important;}}
    </style>'''
    st.markdown(css, unsafe_allow_html=True)
