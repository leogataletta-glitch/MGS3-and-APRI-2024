"""Desktop app shell: the right content scrolls independently of navigation."""
import streamlit as st


def appliquer():
    st.markdown('''<style>
    /* Compensate the left bleed so the hero ends at the same right edge
       as the statistics and destination cards. */
    .stApp.stApp .a2-hero{margin-right:0!important;width:calc(100% + 2rem)!important;max-width:none!important;}
    .stApp.stApp .a2-unep{right:20px!important;max-width:78px!important;object-fit:contain;}
    .stApp.stApp .a2-chif>div:last-child{padding-right:20px!important;text-align:right;}
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
        /* Match the original 1:5 columns, accounting for the left bleed. */
        flex:0 0 calc(16.666667% + .3rem)!important;
      }
      .stApp.stApp .st-key-zone_nav{
        position:relative!important;top:0!important;
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
    </style>''',unsafe_allow_html=True)
