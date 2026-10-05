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
    css = CSS.replace('__R__', r).replace('__Z__', z)
    st.markdown('<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"><style>' + css + '</style>', unsafe_allow_html=True)


CSS = r'''
__R__{--apri-font:Inter,Arial,sans-serif;--apri-green:#087f6b;--apri-ink:#18333b;--apri-text:#18333b;--apri-muted:#586d74;--apri-line:#dce7e4;background:white!important;}
__R__ :is(p,span,div,a,label,button,input,textarea,select,li,td,th,dt,dd,h1,h2,h3,h4,h5,h6,strong,em,b,small,summary,text,tspan):not([data-testid="stIconMaterial"]):not([class*="material"]):not([aria-hidden="true"]){font-family:Inter,Arial,sans-serif!important;}
__R__ section[data-testid="stMain"]{height:auto!important;overflow-y:auto!important;}
__R__ .block-container{max-width:none!important;padding:0!important;}
__R__ div[data-testid="stHorizontalBlock"]:has(>div[data-testid="stColumn"] .st-key-zone_nav){flex-direction:column!important;height:auto!important;gap:0!important;overflow:visible!important;}
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
'''
