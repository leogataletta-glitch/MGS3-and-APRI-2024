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
            structures = {
                'fr': ['Actuelle', 'Observatoire éditorial', 'Atelier d’analyse', 'Atlas immersif'],
                'en': ['Current', 'Editorial observatory', 'Analysis studio', 'Immersive atlas'],
                'es': ['Actual', 'Observatorio editorial', 'Taller de análisis', 'Atlas inmersivo'],
                'ht': ['Aktyèl', 'Obsèvatwa editoryal', 'Atelye analiz', 'Atlas imèsif'],
            }
            structure_labels = dict(zip(['current', 'editorial', 'studio', 'atlas'], structures.get(lang, structures['en'])))
            st.selectbox('Structure', list(structure_labels), format_func=structure_labels.get, key='apri_structure_choice')
            st.selectbox(title, list(PALETTES), format_func=labels.get, key='apri_palette_choice')
    st.markdown('''<style>
    .st-key-apri_palette_preview{position:fixed!important;right:18px!important;bottom:45px!important;width:auto!important;z-index:90!important;}
    .st-key-apri_palette_preview button{min-height:32px!important;padding:5px 10px!important;background:white!important;color:#34483e!important;border:1px solid #dfe7e1!important;}
    </style>''', unsafe_allow_html=True)


def apply():
    apply_structure()
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


def apply_structure():
    variant = st.session_state.get('apri_structure_choice', 'current')
    if variant not in ('editorial', 'studio', 'atlas'):
        return
    r = '#root ' + '.stApp' * 55
    z = r + ' .st-key-zone_page'
    n = r + ' .st-key-zone_nav'
    outer = r + ' div[data-testid="stHorizontalBlock"]:has(>div[data-testid="stColumn"] .st-key-zone_nav)'
    left = r + ' div[data-testid="stColumn"]:has(.st-key-zone_nav)'
    right = r + ' div[data-testid="stColumn"]:has(.st-key-zone_page)'
    tabs = z + ' [class*="st-key-ong_"]'
    css = f'''
    {z}{{background:white!important;--apri-ink:#213c46;--apri-body:#53646c;}}
    {z} :is(h1,h2,h3,p,li,button,select,th,td,strong){{font-family:'Source Sans 3',Arial,sans-serif!important;}}
    {z} :is(.cad-carte,.cad-c,.sx-carte,.sx-k,.ex-k,.int-box,.int-perf,.int-paq,.ap-c,.cad-so-b){{box-shadow:none!important;border:0!important;border-radius:0!important;}}
    {tabs} [role="radiogroup"] label p:not(:first-child){{display:none!important;}}
    {tabs} [role="radiogroup"] label{{min-height:48px!important;padding:12px 16px!important;border-radius:0!important;}}
    {tabs}{{width:100%!important;margin:0 0 24px!important;}}
    {tabs} [role="radiogroup"]{{border-radius:0!important;margin:0!important;}}
    {z} :is([data-testid="stPlotlyChart"],[data-testid="stVegaLiteChart"],[data-testid="stMetric"]){{border:0!important;box-shadow:none!important;border-radius:0!important;}}
    {z} .a2-hero{{margin:0!important;width:100%!important;min-height:310px!important;}}
    {z} .a2-chif{{margin:24px 0!important;}}
    '''
    if variant in ('editorial', 'atlas'):
        css += f'''
        @media(min-width:1001px){{
          {r} section[data-testid="stMain"],{r} div[data-testid="stMain"]{{overflow-y:auto!important;height:auto!important;}}
          {outer}{{flex-direction:column!important;height:auto!important;overflow:visible!important;gap:0!important;}}
          {left}{{width:100%!important;max-width:none!important;min-width:0!important;flex:0 0 auto!important;height:auto!important;max-height:none!important;background-image:none!important;padding:8px 24px!important;border-right:0!important;border-bottom:1px solid #dce5e9!important;}}
          {n}{{display:flex!important;flex-direction:row!important;align-items:center!important;flex-wrap:wrap!important;gap:4px!important;height:auto!important;max-height:none!important;overflow:visible!important;padding:0!important;}}
          {n}>div:has(button){{width:auto!important;flex:0 0 auto!important;}}
          {n} [data-testid="stButton"] button{{width:auto!important;padding:9px 12px!important;min-height:38px!important;border-radius:4px!important;}}
          {n} [data-testid="stButton"] button p{{font-size:13px!important;}}
          {n}>div:has(.nav-famille),{n} .st-key-apri_menu_toggle{{display:none!important;}}
          {n} .st-key-navigation_language_desktop{{margin-left:auto!important;order:20!important;}}
          {right}{{width:100%!important;max-width:none!important;height:auto!important;margin:0!important;overflow:visible!important;padding:0 0 40px!important;}}
          {z}{{max-width:1240px!important;margin:0 auto!important;padding:24px 36px 48px!important;}}
        }}
        '''
    if variant == 'studio':
        css += f'''
        @media(min-width:1001px){{
          {left}{{flex:0 0 220px!important;min-width:220px!important;max-width:220px!important;width:220px!important;background-image:none!important;}}
          {n}{{padding:12px!important;}}
          {n} button p{{font-size:13px!important;}}
          {z}{{max-width:none!important;padding:16px 28px 36px!important;}}
        }}
        {z} [data-testid="stHorizontalBlock"]{{gap:16px!important;}}
        {z} .a2-hero{{min-height:240px!important;}}
        {z} :is(.cad-note,.sx-note,.ap-note){{border-left:2px solid #b8cbd0!important;padding:10px 16px!important;}}
        '''
    if variant == 'atlas':
        css += f'''
        {z}:has(.a2-hero){{max-width:none!important;padding-left:0!important;padding-right:0!important;}}
        {z} .a2-hero{{min-height:410px!important;padding:40px!important;background-color:#f3f7f6!important;}}
        {z} .a2-chif{{padding:24px 40px!important;border-bottom:1px solid #dce5e9!important;}}
        {z} :is(.cad-so,.ap-def,.ap-pay){{gap:32px!important;}}
        '''
    st.markdown('<style>' + css + '</style>', unsafe_allow_html=True)
