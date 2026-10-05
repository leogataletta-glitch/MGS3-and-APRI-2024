"""APRI Horizon: shared presentation of the real application, no sample data."""
import streamlit as st


def prepare():
    # Retire experimental layouts even for sessions that had a mockup selected.
    st.session_state['apri_structure_choice'] = 'horizon'
    st.session_state['apri_palette_choice'] = 'emerald'
    apply()


def apply():
    r = '#root ' + '.stApp' * 64
    z = r + ' .st-key-zone_page'
    css = CSS.replace('__R__', r).replace('__Z__', z).replace('\n', ' ')
    st.markdown('<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"><style>' + css + '</style>', unsafe_allow_html=True)


CSS = r'''
__R__ .st-key-zone_nav,__R__ div[data-testid="stColumn"]:has(.st-key-zone_nav){min-height:0!important;margin:0!important;}
__R__ .st-key-zone_nav>div:has(.st-key-navigation_language_desktop){flex:0 0 144px!important;}
__R__ .st-key-navigation_language_desktop button{padding:4px!important;width:100%!important;}

__R__{--apri-font:Inter,Arial,sans-serif;--apri-green:#087f6b;--apri-ink:#18333b;--apri-text:#18333b;--apri-muted:#586d74;--apri-line:#dce7e4;background:white!important;}
__R__ :is(p,span,div,a,label,button,input,textarea,select,li,td,th,dt,dd,h1,h2,h3,h4,h5,h6,strong,em,b,small,summary,text,tspan):not([data-testid="stIconMaterial"]):not([class*="material"]):not([aria-hidden="true"]){font-family:Inter,Arial,sans-serif!important;}
/* The viewport owns scrolling; auto-height children must not be clipped. */
__R__ [data-testid="stAppViewContainer"]{overflow-y:auto!important;overflow-x:hidden!important;overscroll-behavior-y:auto!important;}
__R__ section[data-testid="stMain"]{height:auto!important;overflow:visible!important;}

__R__ .block-container{max-width:none!important;padding:0!important;}
__R__ div[data-testid="stHorizontalBlock"]:has(>div[data-testid="stColumn"] .st-key-zone_nav){flex-direction:column!important;flex-wrap:nowrap!important;height:auto!important;gap:0!important;overflow:visible!important;}
__R__ div[data-testid="stColumn"]:has(.st-key-zone_nav){width:100%!important;max-width:none!important;min-width:0!important;flex:0 0 auto!important;height:auto!important;max-height:none!important;background:white!important;border:0!important;border-bottom:1px solid #dce7e4!important;padding:12px 3vw!important;}
__R__ div[data-testid="stColumn"]:has(.st-key-zone_page){width:100%!important;max-width:none!important;min-width:0!important;flex:1 1 auto!important;height:auto!important;margin:0!important;padding:0!important;overflow:visible!important;}
__R__ .st-key-zone_nav{display:flex!important;flex-direction:row!important;align-items:center!important;flex-wrap:wrap!important;gap:10px!important;position:static!important;height:auto!important;padding:0!important;background:white!important;overflow:visible!important;}
__R__ .st-key-zone_nav>div{width:auto!important;flex:0 0 auto!important;}
__R__ .st-key-zone_nav>div:has(.horizon-brand){margin-right:auto!important;}
__R__ .horizon-brand{font-size:23px!important;font-weight:700!important;letter-spacing:-1px;color:#18333b;}
__R__ .horizon-brand span{display:block;font-size:10px!important;font-weight:500!important;letter-spacing:2px;text-transform:uppercase;color:#087f6b;}
__R__ .st-key-zone_nav button{width:auto!important;min-height:40px!important;padding:8px 14px!important;background:white!important;border:0!important;border-radius:12px!important;box-shadow:none!important;}
__R__ .st-key-zone_nav button p{font-size:13px!important;color:#18333b!important;}
__R__ .st-key-navigation_language_desktop{margin:0 0 0 24px!important;width:144px!important;}
__R__ .st-key-zone_nav button[kind="primary"]{background:#e8f4ef!important;}
__R__ .st-key-zone_nav .st-key-navigation_language_desktop button{padding:4px!important;width:100%!important;min-width:0!important;}
__R__ .st-key-zone_nav .st-key-navigation_language_desktop button p{font-size:10px!important;}
__R__ .st-key-zone_ruban{display:none!important;}
__Z__{width:100%!important;max-width:none!important;padding:28px 3vw 48px!important;margin:0!important;background:white!important;}
__Z__>[data-testid="stVerticalBlock"]{gap:24px!important;}
__Z__ [data-testid="stHorizontalBlock"]{gap:24px!important;}
__Z__ :is(h1,.apri-page-title,.cad-page-title){font-size:32px!important;font-weight:600!important;line-height:1.2!important;letter-spacing:-.8px!important;color:#18333b!important;}
__Z__ :is(h2,h3,.titre-bloc,.cad-h,.cad-model-title,.ap-h,.ex-titre){font-size:21px!important;font-weight:600!important;line-height:1.4!important;letter-spacing:-.35px!important;color:#18333b!important;}
__Z__ :is(p,li){font-size:14px!important;line-height:1.7!important;}
__Z__ :is(p,li,h1,h2,h3,td,th):hover{transform:none!important;background:transparent!important;box-shadow:none!important;}
__Z__ .apri-page-heading{height:auto!important;padding:0!important;margin:0 0 12px!important;border:0!important;}
__Z__ .apri-page-heading h1{position:static!important;clip-path:none!important;width:auto!important;height:auto!important;overflow:visible!important;white-space:normal!important;margin:0!important;}
__Z__ :is([class*="st-key-ong_"],[class*="st-key-ong_"] [role="radiogroup"]){background:transparent!important;border:0!important;border-radius:0!important;box-shadow:none!important;}
__Z__ [class*="st-key-ong_"] [role="radiogroup"]{gap:8px!important;}
__Z__ [class*="st-key-ong_"] [role="radiogroup"] label{min-height:58px!important;padding:10px 16px!important;background:white!important;border:1px solid transparent!important;border-radius:14px!important;box-shadow:none!important;}
__Z__ [class*="st-key-ong_"] [role="radiogroup"] label:has(input:checked){background:#e8f4ef!important;border-color:#c9e3d9!important;}
__Z__ [class*="st-key-ong_"] label :is(p,strong){font-size:13px!important;color:#18333b!important;}
__Z__ [class*="st-key-ong_"] label p:not(:first-child){font-size:11px!important;color:#586d74!important;}
__Z__ :is([data-testid="stSelectbox"],[data-testid="stMultiSelect"],[data-testid="stTextInput"]){border:0!important;border-radius:0!important;padding:0!important;background:transparent!important;}
__Z__ :is([data-baseweb="select"]>div,[data-baseweb="input"],[data-rac][role="group"]:has(>[role="combobox"])){background:#f0f5f4!important;border:1px solid #dce7e4!important;border-radius:12px!important;min-height:44px!important;box-shadow:none!important;}
__Z__ [data-testid="stWidgetLabel"] p{font-size:12px!important;color:#586d74!important;}
__Z__ :is(.stButton,.stDownloadButton) button{border:1px solid #dce7e4!important;border-radius:12px!important;background:white!important;color:#18333b!important;min-height:42px!important;box-shadow:none!important;}
__Z__ :is(.stButton,.stDownloadButton) button[kind="primary"]{background:#087f6b!important;color:white!important;border-color:#087f6b!important;}
__Z__ button[kind="primary"] p{color:white!important;}
__Z__ :is(.stButton,.stDownloadButton) button:hover{border-color:#087f6b!important;background:#f0f5f4!important;}
__Z__ :is(.stButton,.stDownloadButton) button[kind="primary"]:hover{background:#066b59!important;}
__Z__ :is(.cad-so-b,.ap-c,.int-box,.int-perf,.int-paq,.ap-def>div,.ap-pay>div,.st-key-about_intro,.st-key-about_context,.st-key-about_action){border:0!important;border-top:1px solid #dce7e4!important;border-radius:0!important;padding:24px 0!important;box-shadow:none!important;background:white!important;}
__Z__ :is([data-testid="stMetric"],.ex-k,.cx-k,.ec-k,.sx-k,.cad-ch-e){border:0!important;border-radius:16px!important;background:#f0f5f4!important;padding:20px!important;text-align:left!important;}
__Z__ :is(.ex-k-v,.cx-k-v,.ec-k-v,.sx-k-v,.cad-ch-v){font-size:28px!important;color:#087f6b!important;font-weight:600!important;}
__Z__ :is([data-testid="stPlotlyChart"],[data-testid="stVegaLiteChart"]){border:0!important;padding:0!important;background:white!important;box-shadow:none!important;}
__Z__ :is(th,td){font-size:13px!important;padding:12px 16px!important;border:0!important;border-bottom:1px solid #dce7e4!important;}
__Z__ th{background:#f0f5f4!important;color:#18333b!important;}
__Z__ [data-testid="stExpander"] details{border:0!important;border-top:1px solid #dce7e4!important;border-radius:0!important;}
__Z__ .a2-brand-row{margin:0 0 20px!important;min-height:48px!important;border:0!important;}
__Z__ .st-key-a2_welcome{background:#f0f5f4!important;border-radius:24px!important;padding:28px!important;overflow:hidden!important;}
__Z__ .a2-welcome-title{font-size:clamp(28px,3vw,44px)!important;max-width:24ch!important;line-height:1.15!important;}
__Z__ .a2-welcome-art img{height:290px!important;object-fit:cover!important;border-radius:18px!important;}
__Z__ .a2-chif{background:transparent!important;border:0!important;border-radius:0!important;padding:24px 0!important;gap:32px!important;}
__Z__ .a2-n{font-size:30px!important;font-weight:600!important;color:#087f6b!important;}
__Z__ .a2-intro{max-width:62ch!important;}
__Z__ .a2-link-photo{border:0!important;box-shadow:none!important;}
__Z__ .apri-page-heading,__Z__ .st-key-a2_welcome{animation:horizon-arrive .35s ease both;}
@keyframes horizon-arrive{from{opacity:.6;transform:translateY(6px)}to{opacity:1;transform:none}}
@media(prefers-reduced-motion:reduce){__Z__ *{animation:none!important;transition:none!important;}}
@media(max-width:1000px){__R__ div[data-testid="stColumn"]:has(.st-key-zone_nav){display:none!important;}__Z__{padding:16px 18px 32px!important;}__R__ .st-key-menu_mobile{padding:8px 18px!important;}__Z__ .st-key-a2_welcome{padding:20px!important;}__Z__ .a2-welcome-art img{height:200px!important;}}

/* Compact home: one brand, partner retained, illustration fades into white. */
__Z__ .a2-brand-row{min-height:40px!important;margin:0 0 10px!important;padding:0!important;justify-content:flex-end!important;}
__Z__ .a2-brand-row .a2-marque,__Z__ .a2-brand-row>.a2-inst{display:none!important;}
__Z__ .a2-brand-row .a2-partner{height:40px!important;width:auto!important;margin-left:auto!important;}
__Z__:has(.st-key-a2_welcome){padding-top:12px!important;}
__Z__ .st-key-a2_welcome{background:white!important;padding:12px 0 24px!important;border-radius:0!important;margin:0!important;}
__Z__ .a2-welcome-title{font-size:clamp(28px,2.6vw,38px)!important;max-width:25ch!important;}
__Z__ .a2-welcome-art{background:white!important;overflow:hidden!important;}
__Z__ .a2-welcome-art img{height:250px!important;width:100%!important;object-fit:cover!important;border-radius:0!important;mask-image:linear-gradient(to right,transparent,black 14%),linear-gradient(to bottom,transparent,black 12%,black 85%,transparent);mask-composite:intersect;}
__Z__ .a2-intro{max-width:64ch!important;font-size:14px!important;line-height:1.65!important;}
__Z__ .a2-chif{padding:16px 0!important;margin:0 0 16px!important;}
@media(max-width:700px){__Z__ .a2-welcome-art img{height:180px!important;}__Z__ .st-key-a2_welcome{padding:8px 0 16px!important;}}

/* Navigation popovers are mounted outside .stApp, in the floating portal. */
@media(min-width:1001px){
#stFloatingOverlayPortal [class*="st-key-nav_"] button{min-height:36px!important;height:36px!important;padding:7px 12px!important;border:0!important;border-radius:6px!important;box-shadow:none!important;background:white!important;justify-content:flex-start!important;width:100%!important;}
#stFloatingOverlayPortal [class*="st-key-nav_"] button p{font:500 13px/1.4 Inter,Arial,sans-serif!important;color:#18333b!important;margin:0!important;}
#stFloatingOverlayPortal [class*="st-key-nav_"] button[kind="primary"],#stFloatingOverlayPortal [class*="st-key-nav_"] button:hover{background:#e8f4ef!important;}
#stFloatingOverlayPortal [data-testid="stPopoverBody"]:has([class*="st-key-nav_"]){padding:8px!important;min-width:220px!important;}
#stFloatingOverlayPortal [data-testid="stVerticalBlock"]:has(>[class*="st-key-nav_"]){gap:4px!important;}
}

__R__ .horizon-identity{display:flex;align-items:center;gap:16px;}
__R__ .horizon-apri{height:44px;width:auto;object-fit:contain;}
__R__ .horizon-partner{height:38px;width:auto;border-left:1px solid #dce7e4;padding-left:20px;filter:brightness(0) saturate(100%) invert(22%) sepia(21%) saturate(1030%) hue-rotate(101deg) brightness(85%);}
__Z__:has(.st-key-a2_welcome){padding-top:20px!important;}
__Z__ .st-key-a2_welcome{padding:0 0 14px!important;overflow:visible!important;}
__Z__ .a2-welcome-art{width:calc(100% + 3vw)!important;}
@media(max-width:1000px){__Z__ .a2-welcome-art{width:calc(100% + 18px)!important;}}
__Z__ .st-key-a2_welcome [data-testid="stHorizontalBlock"]{gap:16px!important;}
__Z__ .a2-welcome-copy{max-width:680px!important;}
__Z__ .a2-welcome-title{font-size:clamp(27px,2.1vw,34px)!important;max-width:29ch!important;margin:8px 0 14px!important;}
__Z__ .a2-intro{max-width:68ch!important;line-height:1.55!important;margin:0 0 12px!important;}
__Z__ .a2-welcome-art img{height:225px!important;object-fit:cover!important;mask-image:linear-gradient(to right,transparent,black 10%,black 100%),linear-gradient(to bottom,transparent,black 12%,black 82%,transparent);}
__Z__ .a2-chif{gap:16px!important;padding:12px 0!important;margin:0 0 12px!important;}
__Z__ .a2-n{font-size:26px!important;}
__Z__ .st-key-a2_photo_links div[data-testid="stButton"]>button{background:transparent!important;border:0!important;border-radius:0!important;box-shadow:none!important;min-height:60px!important;padding:6px 0!important;}
__Z__ .st-key-a2_photo_links div[data-testid="stButton"]>button:hover{background:#f0f5f4!important;border:0!important;box-shadow:none!important;}
__Z__ .st-key-a2_photo_links div[class*="st-key-a2_porte_"]{padding:0 10px!important;}
__Z__ .st-key-a2_photo_links button p{font-size:13px!important;}
__Z__ .st-key-a2_photo_links button p strong{margin-top:2px!important;}
@media(max-width:700px){__Z__ .a2-welcome-art img{height:160px!important;}__Z__ .a2-welcome-title{font-size:28px!important;}}
/* Framework: compact subnavigation and a continuous reading surface. */
__Z__:has(.st-key-ong_cad_vue){padding-top:12px!important;gap:8px!important;}
__Z__ .st-key-ong_cad_vue{margin:0 0 12px!important;}
__Z__ .st-key-ong_cad_vue [role="radiogroup"]{padding:0!important;gap:6px!important;}
__Z__ .st-key-ong_cad_vue [role="radiogroup"] label{min-height:48px!important;padding:8px 12px!important;border-radius:8px!important;}
__Z__ .st-key-ong_cad_vue [role="radiogroup"] label p{font-size:12px!important;line-height:1.45!important;margin:2px 0!important;}
__Z__ .st-key-ong_cad_vue [role="radiogroup"] label strong{font-size:13px!important;}

@media(min-width:1001px){
#stFloatingOverlayPortal [data-testid="stPopoverBody"]:has([class*="st-key-nav_"]){border-top:2px solid #087f6b!important;transform-origin:top center;animation:apri-menu-open .16s ease-out;box-shadow:0 8px 24px #18333b18!important;}
__R__ .st-key-zone_nav [data-testid="stPopover"]>button[aria-expanded="true"]{background:#e8f4ef!important;border-radius:8px!important;color:#087f6b!important;}
}
@keyframes apri-menu-open{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:translateY(0)}}
@media(prefers-reduced-motion:reduce){#stFloatingOverlayPortal [data-testid="stPopoverBody"]{animation:none!important;}}

__Z__ .st-key-cad_section_dropdown{max-width:360px!important;}
__Z__ .st-key-cad_section_dropdown [data-baseweb="select"]>div{background:#e8f4ef!important;border-color:#c9e3d9!important;min-height:40px!important;border-radius:8px!important;}
__Z__ .st-key-cad_section_dropdown label p{font-size:12px!important;font-weight:500!important;}
[data-baseweb="popover"]:has([role="listbox"]){animation:apri-menu-open .18s ease-out;transform-origin:top;}
@media(prefers-reduced-motion:reduce){[data-baseweb="popover"]:has([role="listbox"]){animation:none!important;}}

#stFloatingOverlayPortal .st-key-nav_framework_tree details{border:0!important;border-radius:6px!important;box-shadow:none!important;}
#stFloatingOverlayPortal .st-key-nav_framework_tree summary{padding:8px 12px!important;min-height:36px!important;}
#stFloatingOverlayPortal .st-key-nav_framework_tree summary p{font:500 13px/1.4 Inter,Arial,sans-serif!important;}
#stFloatingOverlayPortal .st-key-nav_framework_tree details[open]>div{border-left:2px solid #c9e3d9;margin-left:18px;padding:4px 0 4px 8px;animation:apri-menu-open .2s ease-out;}

__R__ .st-key-zone_nav{gap:6px!important;}
__R__ .st-key-zone_nav button p{font-size:12px!important;white-space:nowrap!important;}
__R__ .st-key-top_menu_dimensions button{background:#a63243!important;color:white!important;border-color:#a63243!important;border-radius:8px!important;}
__R__ .st-key-top_menu_dimensions button p{color:white!important;}
#stFloatingOverlayPortal [class*="st-key-top_section_"] button{min-height:36px!important;padding:8px 12px!important;border:0!important;box-shadow:none!important;background:white!important;justify-content:flex-start!important;}
#stFloatingOverlayPortal [class*="st-key-top_section_"] button p{font:500 13px/1.4 Inter,Arial,sans-serif!important;}
#stFloatingOverlayPortal [data-testid="stPopoverBody"]:has([class*="st-key-top_section_"]){min-width:250px!important;padding:8px!important;animation:apri-menu-open .18s ease-out;}

/* Reset legacy card heights in every top-level navigation popup. */
#stFloatingOverlayPortal [data-testid="stPopoverBody"]:has([class*="st-key-top_section_"], [class*="st-key-nav_"]){width:270px!important;min-width:240px!important;max-width:calc(100vw - 24px)!important;padding:6px!important;border:1px solid #e2e9e6!important;border-radius:10px!important;box-shadow:0 8px 24px #18333b14!important;}
#stFloatingOverlayPortal [data-testid="stVerticalBlock"]:has(>[class*="st-key-top_section_"], >[class*="st-key-nav_"]){gap:2px!important;height:auto!important;}
#stFloatingOverlayPortal :is([class*="st-key-top_section_"],[class*="st-key-nav_"]){height:auto!important;min-height:0!important;margin:0!important;}
#stFloatingOverlayPortal :is([class*="st-key-top_section_"],[class*="st-key-nav_"]) button{height:36px!important;min-height:36px!important;max-height:none!important;padding:8px 12px!important;display:flex!important;justify-content:flex-start!important;align-items:center!important;border-radius:5px!important;text-align:left!important;}
#stFloatingOverlayPortal :is([class*="st-key-top_section_"],[class*="st-key-nav_"]) button p{font:400 13px/1.4 Inter,Arial,sans-serif!important;text-align:left!important;margin:0!important;}
#stFloatingOverlayPortal :is([class*="st-key-top_section_"],[class*="st-key-nav_"]) button:hover{background:#edf5f2!important;color:#087f6b!important;}
@media(pointer:coarse){#stFloatingOverlayPortal :is([class*="st-key-top_section_"],[class*="st-key-nav_"]) button{height:44px!important;min-height:44px!important;}}

__Z__ .st-key-qa_workspace>[data-testid="stHorizontalBlock"],__Z__ .st-key-qa_workspace [data-testid="stHorizontalBlock"]:has(>.stColumn .st-key-qa_builder){gap:36px!important;}
__Z__ [data-testid="stColumn"]:has(>.stVerticalBlock .st-key-qa_builder){min-width:250px!important;}
__Z__ .st-key-qa_builder{background:#f3f7f6!important;border-radius:12px!important;padding:24px!important;gap:16px!important;}
__Z__ .st-key-qa_builder h3{font-size:19px!important;font-weight:600!important;line-height:1.3!important;}
__Z__ .st-key-qa_builder [data-testid="stHorizontalBlock"]{flex-direction:column!important;}
__Z__ .st-key-qa_builder [data-testid="stColumn"]{width:100%!important;flex:1 1 auto!important;}
__Z__ .st-key-qa_answer{padding:12px 0!important;min-height:400px!important;}
__Z__ .st-key-qa_answer h2{font-size:clamp(24px,2.2vw,34px)!important;line-height:1.25!important;max-width:40ch!important;margin:0 0 20px!important;}
__Z__ .st-key-qa_answer [data-testid="stMarkdownContainer"]>p{max-width:75ch;}
@media(max-width:760px){__Z__ .st-key-qa_workspace>[data-testid="stHorizontalBlock"]{flex-direction:column!important;}__Z__ .st-key-qa_builder{padding:16px!important;}__Z__ .st-key-qa_answer{min-height:0!important;}}
'''
