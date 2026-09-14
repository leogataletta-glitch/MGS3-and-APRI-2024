"""Desktop app shell: the right content scrolls independently of navigation."""
import streamlit as st


def appliquer():
    st.markdown('''<style>
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
      div[data-testid="stColumn"]:has(.st-key-zone_nav){
        height:calc(100dvh * var(--dz,1))!important;
        min-height:0!important;max-height:calc(100dvh * var(--dz,1))!important;
        margin-bottom:0!important;padding-bottom:0!important;
        align-self:stretch!important;
      }
      .st-key-zone_nav{
        position:relative!important;top:0!important;
        min-height:0!important;max-height:calc(100dvh * var(--dz,1))!important;
        overflow-y:auto!important;overscroll-behavior:contain!important;
      }
      div[data-testid="stColumn"]:has(.st-key-zone_page){
        height:calc(100dvh * var(--dz,1))!important;
        min-height:0!important;overflow-y:auto!important;overflow-x:hidden!important;
        overscroll-behavior-y:contain!important;scrollbar-gutter:stable;
        padding-bottom:32px!important;
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
