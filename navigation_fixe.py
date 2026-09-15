"""Desktop app shell: the right content scrolls independently of navigation."""
import streamlit as st


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
      /* Overlap the map and navigation without altering the sidebar width. */
      div[data-testid="stHorizontalBlock"]:has(.st-key-territory_map):has(> div[data-testid="stColumn"] .st-key-zone_nav){
        gap:0!important;
      }
      div[data-testid="stColumn"]:has(.st-key-territory_map){
        margin-left:-48px!important;flex-grow:1!important;
      }
      div[data-testid="stColumn"]:has(.st-key-zone_nav){z-index:3;}
    }
    /* Compact searchable dropdowns shared by all content pages. */
    .stApp.stApp.stApp.stApp.stApp.stApp .st-key-zone_page [data-testid="stSelectbox"]{background:white!important;border:1px solid #d4dce0!important;border-radius:9px!important;padding:6px 10px!important;}
    .stApp.stApp.stApp.stApp.stApp.stApp .st-key-zone_page [data-testid="stSelectbox"]:focus-within{border-color:#28745c!important;box-shadow:0 2px 7px #194b3220!important;}
    .stApp.stApp.stApp.stApp.stApp.stApp .st-key-zone_page [data-testid="stSelectbox"] label p{font:400 11px/1.3 Arial,sans-serif!important;color:#68758a!important;letter-spacing:0!important;text-transform:none!important;}
    .stApp.stApp.stApp.stApp.stApp.stApp .st-key-zone_page [data-testid="stSelectbox"] [data-baseweb="select"]>div{background:transparent!important;border:0!important;min-height:28px!important;border-radius:0!important;box-shadow:none!important;}
    .stApp.stApp.stApp.stApp.stApp.stApp .st-key-zone_page [data-testid="stSelectbox"] [role="combobox"]{font-size:14px!important;background:transparent!important;}
    .stApp.stApp.stApp.stApp.stApp.stApp [role="listbox"]{background:white!important;border:1px solid #dce2df!important;border-radius:10px!important;box-shadow:0 6px 18px #193c2520!important;padding:5px!important;}
    .stApp.stApp.stApp.stApp.stApp.stApp [role="option"]{border-radius:7px!important;font-size:14px!important;}
    .stApp.stApp.stApp.stApp.stApp.stApp [role="option"][aria-selected="true"]{background:#e8f1eb!important;color:#104b3b!important;}
    </style>''',unsafe_allow_html=True)
