"""Desktop app shell: the right content scrolls independently of navigation."""
import streamlit as st


def _toggle_menu():
    st.session_state['apri_menu_closed'] = not st.session_state.get('apri_menu_closed', False)


def _menu_toggle():
    """Keep a narrow, accessible handle when the desktop navigation is folded."""
    closed = st.session_state.get('apri_menu_closed', False)
    lang = st.session_state.get('choix_langue', 'en')
    labels = {
        'fr': ('Masquer le menu', 'Afficher le menu'),
        'en': ('Hide menu', 'Show menu'),
        'es': ('Ocultar menú', 'Mostrar menú'),
        'ht': ('Kache meni an', 'Montre meni an'),
    }
    label = labels.get(lang, labels['en'])[int(closed)]
    st.button(label, icon=':material/chevron_right:' if closed else ':material/chevron_left:',
              key='apri_menu_toggle', help=label, on_click=_toggle_menu)
    root = '.stApp' * 20
    folded = """
      ROOT div[data-testid="stColumn"]:has(.st-key-zone_nav){
        flex:0 0 52px!important;width:52px!important;min-width:52px!important;
        max-width:52px!important;padding-left:0!important;background:#f5f8f6!important;
      }
      ROOT .st-key-zone_nav > :not(:has(.st-key-apri_menu_toggle)):not(.st-key-apri_menu_toggle){display:none!important;}
      ROOT .st-key-zone_nav{padding:0!important;overflow:visible!important;}
      ROOT div[data-testid="stColumn"]:has(.st-key-territory_map){margin-left:0!important;}
    """ if closed else ''
    css = """<style>
    ROOT .st-key-apri_menu_toggle{display:none!important;}
    @media(min-width:1001px){
      ROOT .st-key-apri_menu_toggle{
        display:block!important;position:fixed!important;top:8px!important;left:8px!important;
        width:36px!important;height:36px!important;z-index:100!important;margin:0!important;
      }
      ROOT .st-key-apri_menu_toggle button{
        display:flex!important;align-items:center!important;justify-content:center!important;
        width:36px!important;min-width:36px!important;height:36px!important;min-height:36px!important;
        padding:0!important;border:1px solid #d5dfd9!important;border-radius:50%!important;
        background:#ffffff!important;color:#174e3e!important;box-shadow:none!important;
      }
      ROOT .st-key-apri_menu_toggle button p{
        position:absolute!important;width:1px!important;height:1px!important;
        padding:0!important;margin:-1px!important;overflow:hidden!important;
        clip:rect(0,0,0,0)!important;white-space:nowrap!important;
      }
      ROOT .st-key-apri_menu_toggle button:hover{background:#e8f1ec!important;}
      ROOT .st-key-apri_menu_toggle button:focus-visible{outline:2px solid #174e3e!important;outline-offset:3px!important;}
      FOLDED
    }
    </style>"""
    st.markdown(css.replace('FOLDED', folded).replace('ROOT', root), unsafe_allow_html=True)


def appliquer():
    st.markdown('''<style>
    /* Compensate the left bleed so the hero ends at the same right edge
       as the statistics and destination cards. */
    .stApp.stApp .a2-hero{margin-right:0!important;width:calc(100% + 2rem)!important;max-width:none!important;}
    .stApp.stApp .a2-unep{right:20px!important;max-width:78px!important;object-fit:contain;}
    .stApp.stApp .a2-chif>div{padding:4px 20px!important;text-align:center!important;min-width:0;}
    .stApp.stApp .a2-chif .a2-n{font-size:30px!important;}
    .stApp.stApp .a2-chif .a2-l{font-size:11px!important;}
    .stApp.stApp .a2-chif .a2-s{font-size:12px!important;}
    @media(max-width:1000px){.stApp.stApp .a2-hero{width:calc(100% + 2.6rem)!important;}}
    .stApp.stApp .st-key-navigation_language_desktop{flex-shrink:0!important;position:relative;z-index:4;}
    .stApp.stApp .st-key-zone_page:has(.st-key-territory_map){padding:0!important;}
    .st-key-zone_page:has(.st-key-territory_map) [data-testid="stElementContainer"]:has(.apri-page-heading){display:none!important;}
    @media(min-width:1001px){
      section[data-testid="stMain"],div[data-testid="stMain"]{
        height:calc(100dvh * var(--dz,1))!important;
        overflow:hidden!important;
      }
      div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"] .st-key-zone_nav){
        height:calc(100dvh * var(--dz,1))!important;
        min-height:0!important;align-items:stretch!important;
        overflow:visible!important;
      }
      .stApp.stApp div[data-testid="stColumn"]:has(.st-key-zone_nav){
        height:calc(100dvh * var(--dz,1))!important;
        min-height:0!important;max-height:calc(100dvh * var(--dz,1))!important;
        margin-bottom:0!important;padding-bottom:0!important;
        align-self:stretch!important;
        /* Leave room for long menu labels and the mosaic at normal zoom. */
        flex:0 0 max(340px, 19%)!important;
        min-width:340px!important;
        background-size:max(370px, 20vw) auto!important;
      }
      .stApp.stApp .st-key-zone_nav{
        position:relative!important;top:0!important;
        padding-top:8px!important;
        min-height:0!important;max-height:calc(100dvh * var(--dz,1))!important;
        overflow-y:auto!important;overscroll-behavior:contain!important;
      }
      div[data-testid="stColumn"]:has(.st-key-zone_page){
        height:calc(100dvh * var(--dz,1))!important;
        min-height:0!important;min-width:0!important;flex:1 1 0!important;overflow-y:auto!important;overflow-x:hidden!important;
        overscroll-behavior-y:contain!important;scrollbar-gutter:auto!important;
        scrollbar-width:none!important;
        /* The scroll viewport itself reaches the screen edge, so artwork
           no longer gets clipped at the main container's right padding. */
        margin-right:-2.6rem!important;
        padding-bottom:32px!important;
      }
      div[data-testid="stColumn"]:has(.st-key-zone_page)::-webkit-scrollbar{
        display:none!important;width:0!important;height:0!important;
      }
      .stApp .st-key-zone_ruban .bandeau-haut.bandeau-enveloppe{
        width:100%!important;max-width:100%!important;margin-right:0!important;
      }
      /* Keep a compact gutter between the sidebar and ordinary pages. */
      .stApp.stApp div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"] .st-key-zone_nav):not(:has(.st-key-territory_map)):not(:has(.a2-hero)){
        gap:12px!important;
      }
      /* Overlap the map and navigation without altering the sidebar width. */
      div[data-testid="stHorizontalBlock"]:has(.st-key-territory_map):has(> div[data-testid="stColumn"] .st-key-zone_nav){
        gap:0!important;
      }
      div[data-testid="stColumn"]:has(.st-key-territory_map){
        margin-left:-48px!important;flex-grow:1!important;
      }
      div[data-testid="stColumn"]:has(.st-key-zone_nav){z-index:3;}
    }
    /* One dropdown format for single and multiple selections on every page. */
    .stApp.stApp.stApp.stApp.stApp.stApp .st-key-zone_page :is([data-testid="stSelectbox"],[data-testid="stMultiSelect"]){background:white!important;border:1px solid #d4dce0!important;border-radius:10px!important;padding:8px 12px!important;}
    .stApp.stApp.stApp.stApp.stApp.stApp .st-key-zone_page :is([data-testid="stSelectbox"],[data-testid="stMultiSelect"]):focus-within{border-color:#28745c!important;box-shadow:0 2px 7px #194b3220!important;}
    .stApp.stApp.stApp.stApp.stApp.stApp .st-key-zone_page :is([data-testid="stSelectbox"],[data-testid="stMultiSelect"]) label p{font:400 11px/1.3 Arial,sans-serif!important;color:#68758a!important;letter-spacing:0!important;text-transform:none!important;}
    .stApp.stApp.stApp.stApp.stApp.stApp .st-key-zone_page :is([data-testid="stSelectbox"],[data-testid="stMultiSelect"]) :is([data-baseweb="select"]>div,[data-rac][role="group"]:has(> [role="combobox"])){background:#eef2ed!important;border:0!important;min-height:42px!important;border-radius:8px!important;box-shadow:none!important;}
    .stApp.stApp.stApp.stApp.stApp.stApp .st-key-zone_page :is([data-testid="stSelectbox"],[data-testid="stMultiSelect"]) [role="combobox"]{font-size:14px!important;background:transparent!important;}
    .stApp.stApp.stApp.stApp.stApp.stApp [role="listbox"]{background:white!important;border:1px solid #dce2df!important;border-radius:10px!important;box-shadow:0 6px 18px #193c2520!important;padding:5px!important;}
    .stApp.stApp.stApp.stApp.stApp.stApp [role="option"]{border-radius:7px!important;font-size:14px!important;}
    .stApp.stApp.stApp.stApp.stApp.stApp [role="option"][aria-selected="true"]{background:#e8f1eb!important;color:#104b3b!important;}
    .stApp.stApp.stApp.stApp.stApp.stApp .st-key-zone_page :is([data-testid="stSelectbox"],[data-testid="stMultiSelect"]) [role="combobox"]{min-height:32px!important;color:#3c4761!important;}
    .stApp.stApp.stApp.stApp.stApp.stApp .st-key-zone_page :is([data-testid="stSelectbox"],[data-testid="stMultiSelect"]) label{margin-bottom:6px!important;}
    </style>''',unsafe_allow_html=True)

    _menu_toggle()
