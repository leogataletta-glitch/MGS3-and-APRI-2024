"""Unified APRI presentation, based on the approved Proposal design."""
import streamlit as st

KEY = 'apri_visual_version'


def active():
    return True


def selector():
    """Keep existing callers compatible without displaying a design switch."""
    st.session_state[KEY] = 2


def navigation(root):
    if not active():
        return
    st.markdown(f'''<style>
    {root} [role="radiogroup"]{{gap:8px!important;padding:4px!important;background:#f1f5f3!important;border-radius:16px!important;}}
    {root} [role="radiogroup"] label{{min-height:80px!important;padding:12px!important;border-radius:16px!important;background:transparent!important;}}
    {root} [role="radiogroup"] label p:first-child,{root} [role="radiogroup"] label strong{{font:700 14px/1.4 Georgia,serif!important;color:#104b3b!important;}}
    {root} [role="radiogroup"] label p:not(:first-child){{font:400 12px/1.5 Georgia,serif!important;color:#4b5550!important;}}
    {root} [role="radiogroup"] label:has(input:checked){{background:white!important;border:1px solid #dde3df!important;box-shadow:0 4px 14px #104b3b18,inset 0 -3px #104b3b!important;border-radius:16px!important;}}
    {root} [role="radiogroup"] label:hover{{background:#e4eee9!important;}}
    {root} [role="radiogroup"] label div:not(:has([data-testid="stMarkdownContainer"])):not([data-testid="stMarkdownContainer"]){{display:none!important;}}
    {root} [role="radiogroup"] label div:has([data-testid="stMarkdownContainer"]){{flex:1 1 0!important;width:100%!important;min-width:0!important;padding:0!important;}}
    {root} [role="radiogroup"] label [data-testid="stMarkdownContainer"]{{display:block!important;width:100%!important;min-width:0!important;}}
    @media(max-width:700px){{
      {root} [role="radiogroup"]{{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:4px!important;}}
      {root} [role="radiogroup"] label{{width:100%!important;min-width:0!important;min-height:64px!important;padding:8px!important;}}
      {root} [role="radiogroup"] label p:first-child,{root} [role="radiogroup"] label strong{{font-size:13px!important;}}
      {root} [role="radiogroup"] label p:not(:first-child){{font-size:11px!important;line-height:1.4!important;}}
    }}

    </style>''', unsafe_allow_html=True)


def apply():
    composition()
    root = '.stApp' * 32
    zone = root + ' .st-key-zone_page'
    if not active():
        return
    st.markdown(f'''<style>
    {root}{{--apri-green:#104b3b;--apri-text:#4b5550;--apri-muted:#4b5550;--apri-line:#dde3df;--apri-content-size:14px;}}
    {zone}{{background:white!important;}}
    {zone} :is(h1,.apri-page-title,.cad-page-title){{font:700 28px/1.3 Georgia,serif!important;color:#104b3b!important;}}
    {zone} :is(h2,h3,.titre-bloc,.cad-h,.cad-model-title,.ap-h,.ex-titre){{font:700 20px/1.4 Georgia,serif!important;color:#104b3b!important;}}
    {zone} :is(p,li){{line-height:1.6!important;}}
    {zone} [data-testid="stCaptionContainer"] :is(p,span),{zone} [data-testid="stWidgetLabel"] p{{font:400 12px/1.5 Georgia,serif!important;color:#4b5550!important;}}
    {zone} :is([data-baseweb="select"]>div,[data-baseweb="input"],[data-baseweb="textarea"]){{background:#f1f5f3!important;border:1px solid #dde3df!important;border-radius:8px!important;min-height:44px!important;box-shadow:none!important;}}
    {zone} [data-testid="stMetric"]{{background:white!important;border:1px solid #dde3df!important;border-radius:8px!important;padding:16px!important;text-align:center!important;}}
    {zone} [data-testid="stMetricLabel"]{{justify-content:center!important;}}
    {zone} [data-testid="stMetricValue"] :is(div,span){{font:700 28px/1.3 Georgia,serif!important;color:#104b3b!important;text-align:center!important;}}
    {zone} :is(th,td){{font:14px/1.5 Georgia,serif!important;padding:10px 16px!important;border:0!important;border-bottom:1px solid #dde3df!important;}}
    {zone} th{{font-weight:700!important;background:#f1f5f3!important;color:#104b3b!important;}}
    {zone} :is(.stButton,.stDownloadButton) button{{border-radius:8px!important;}}
    {zone} [data-testid="stExpander"] details{{border:1px solid #dde3df!important;border-radius:8px!important;}}
    {zone} :is(p,li,h2,h3,td,th):hover,{zone} :is(p,li,h2,h3,td,th):active{{background:transparent!important;transform:none!important;box-shadow:none!important;}}
    {zone} [data-testid="stPlotlyChart"],{zone} [data-testid="stVegaLiteChart"]{{border:1px solid #dde3df!important;border-radius:8px!important;padding:12px!important;}}
    @media(max-width:700px){{{zone} :is(h1,.apri-page-title,.cad-page-title){{font-size:24px!important;}}}}
    </style>''', unsafe_allow_html=True)


def composition():
    """Shared page geometry; map and homepage retain their dedicated canvas."""
    root = '.stApp' * 32
    zone = root + ' .st-key-zone_page'
    page = st.session_state.get('app_mode', 'portail')
    if page in ('portail', 'accueil'):
        return
    st.markdown(COMPOSITION.replace('__ZONE__', zone), unsafe_allow_html=True)
    st.markdown(CONTENT_LAYOUT.replace('__ZONE__', zone), unsafe_allow_html=True)


COMPOSITION = """<style>
__ZONE__{width:100%!important;max-width:1440px!important;margin-inline:auto!important;padding:12px 24px 40px!important;box-sizing:border-box!important;}
__ZONE__>[data-testid="stVerticalBlock"]{gap:20px!important;}
__ZONE__ [data-testid="stHorizontalBlock"]{gap:20px!important;align-items:stretch;}
__ZONE__ [data-testid="stColumn"]{min-width:0!important;}
__ZONE__ [data-testid="stMarkdownContainer"]>p:not(:has(img)):not([role="radiogroup"] p):not(button p):not([data-testid="stWidgetLabel"] p),
__ZONE__ :is(.ap-p,.cad-note,.cad-so-x,.cad-c-x,.int-x,.int-paq-x,.sx-note){max-width:76ch!important;text-align:left!important;line-height:1.65!important;hyphens:none!important;margin:0 0 12px!important;font-family:Georgia,serif!important;font-size:14px!important;}
__ZONE__ :is(h2,h3,.ap-h,.cad-h,.titre-bloc,.cad-model-title,.int-section-t){text-align:left!important;margin:0 0 12px!important;letter-spacing:0!important;text-transform:none!important;}
__ZONE__ .ap-h span{display:none!important;}
__ZONE__ [data-testid="stVerticalBlockBorderWrapper"]{border-color:#dde3df!important;border-radius:12px!important;}
__ZONE__ [data-testid="stVerticalBlockBorderWrapper"]>[data-testid="stVerticalBlock"]{padding:18px!important;gap:16px!important;}
__ZONE__ :is(.cad-so,.ap-def,.ap-pay,.ap-b){display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:20px!important;margin:0!important;}
__ZONE__ :is(.cad-so-b,.ap-def>div,.ap-pay>div,.ap-c,.int-box,.int-paq,.int-perf){padding:20px!important;background:#fff!important;border:1px solid #dde3df!important;border-radius:12px!important;box-shadow:none!important;margin:0!important;min-width:0!important;}
__ZONE__ .cad-so-h{justify-content:flex-start!important;margin-bottom:12px!important;}
__ZONE__ :is(.cad-so-t,.ap-c-t,.ap-def .m,.ap-pay .t,.int-box-t,.int-paq-t,.dl-t){font:700 18px/1.4 Georgia,serif!important;color:#104b3b!important;text-align:left!important;letter-spacing:0!important;text-transform:none!important;margin-bottom:8px!important;}
__ZONE__ :is(.ap-c-x,.ap-def .x,.ap-pay .x,.dl-s,.cad-so-l li){font:400 14px/1.65 Georgia,serif!important;color:#4b5550!important;text-align:left!important;}
__ZONE__ :is(.ap-def .s,.ap-pay .s,.dl-m,.cad-c-n){font:400 12px/1.5 Georgia,serif!important;color:#4b5550!important;letter-spacing:0!important;}
__ZONE__ .cad-so-k{display:flex!important;flex-wrap:wrap;gap:12px;margin:16px 0!important;}
__ZONE__ .cad-so-k>div{flex:1 1 100px;display:block!important;padding:12px!important;background:#f1f5f3;border-radius:8px;}
__ZONE__ .cad-so-k b{display:block;font:700 24px/1.3 Georgia,serif!important;color:#104b3b;}
__ZONE__ .cad-so-k span{font-size:12px!important;}
__ZONE__ :is(.ap-todo,.cad-note,.sx-note){padding:12px 16px!important;border-left:3px solid #104b3b!important;background:#f1f5f3!important;color:#4b5550!important;border-radius:0 8px 8px 0!important;}
__ZONE__ .st-key-about_context .ap-pay{grid-template-columns:1fr!important;}
__ZONE__ .ap-l{max-width:76ch;margin:0!important;}
__ZONE__ .ap-l li{padding:12px 0!important;gap:16px!important;}
__ZONE__ [data-testid="stVerticalBlock"][class*="st-key-dl_"]{padding:20px!important;border:1px solid #dde3df!important;border-radius:12px!important;margin:0!important;height:100%;}
__ZONE__ :is(table,.cad-dh,.cad-dl){width:100%;font-variant-numeric:tabular-nums;}
__ZONE__ table{border-collapse:collapse!important;}
__ZONE__ [data-testid="stExpander"] summary{padding:12px 16px!important;min-height:44px!important;}
__ZONE__ [data-testid="stExpander"] details>div{padding:16px!important;}
__ZONE__ :is(.st-key-about_intro,.st-key-about_context,.st-key-about_action){padding:20px!important;border:1px solid #dde3df!important;border-radius:12px!important;}
@media(max-width:800px){
__ZONE__{padding:8px 12px 24px!important;}
__ZONE__>[data-testid="stVerticalBlock"]{gap:16px!important;}
__ZONE__ [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:16px!important;}
__ZONE__ [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]{flex:1 1 100%!important;width:100%!important;}
__ZONE__ :is(.cad-so,.ap-def,.ap-pay,.ap-b){grid-template-columns:1fr!important;gap:16px!important;}
__ZONE__ :is(.cad-so-b,.ap-def>div,.ap-pay>div,.ap-c,.int-box,.int-paq,.int-perf){padding:16px!important;}
}
</style>"""


# Content geometry is shared across the framework, results and action pages.
# Semantic chart colours and data values are deliberately left to their renderers.
CONTENT_LAYOUT = """<style>
__ZONE__ :is(.stButton,.stDownloadButton) button{min-height:38px!important;height:auto!important;padding:8px 14px!important;font:400 13px/1.5 Georgia,serif!important;}
__ZONE__ :is(.stButton,.stDownloadButton) button p{font:inherit!important;margin:0!important;}
__ZONE__ .model-dimensions li span{text-align:left!important;}
__ZONE__ .cad-ch{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:16px!important;margin:16px 0 24px!important;}
__ZONE__ .cad-ch-fl{display:none!important;}
__ZONE__ .cad-ch-e{padding:18px!important;background:#f1f5f3!important;border:1px solid #dde3df!important;border-radius:12px!important;min-width:0!important;}
__ZONE__ .cad-ch-h{border:0!important;margin-bottom:14px!important;}
__ZONE__ .cad-ch-n{color:#104b3b!important;border:1px solid #dde3df!important;border-radius:6px!important;padding:3px 7px!important;background:white!important;}
__ZONE__ .cad-ch-t{font:700 14px/1.5 Georgia,serif!important;}
__ZONE__ .cad-ch-v{font:700 24px/1.4 Georgia,serif!important;color:#104b3b!important;}
__ZONE__ :is(.cad-ch-x,.cad-ch-s){font:400 12px/1.6 Georgia,serif!important;text-align:left!important;}
__ZONE__ :is(.ex-kpi,.cx-kpi){display:flex!important;flex-wrap:wrap!important;gap:16px!important;margin:20px 0!important;}
__ZONE__ :is(.ex-k,.cx-k){flex:1 1 180px!important;padding:18px!important;background:#f1f5f3!important;border:1px solid #dde3df!important;border-radius:12px!important;}
__ZONE__ :is(.ex-k-v,.cx-k-v){font:700 26px/1.4 Georgia,serif!important;color:#104b3b!important;}
__ZONE__ :is(.ex-k-l,.cx-k-l,.ev-lab,.ev-t){font:700 14px/1.5 Georgia,serif!important;color:#104b3b!important;letter-spacing:0!important;text-transform:none!important;}
__ZONE__ :is(.ev-x,.ev-puce li){font:400 14px/1.65 Georgia,serif!important;max-width:76ch!important;text-align:left!important;}
__ZONE__ :is(.ev-n,.ev-verdict){padding:16px!important;background:#f1f5f3!important;border-radius:10px!important;}
__ZONE__ :is(.st-key-ex_brut,.st-key-ex_brut_s,.st-key-ex_brut_c){padding:20px!important;border:1px solid #dde3df!important;border-radius:14px!important;}
__ZONE__ [data-testid="stMarkdownContainer"]:has(>svg){padding:16px!important;border:1px solid #dde3df!important;border-radius:12px!important;overflow-x:auto!important;}
__ZONE__ :is(.cad-so-b,.ap-c,.int-paq){border-top:3px solid #104b3b!important;}
__ZONE__ :is(.cad-flo,.ec-kpi,.sx-kpi){display:flex!important;gap:16px!important;align-items:stretch!important;margin:20px 0!important;}
__ZONE__ :is(.cad-flo-e,.ec-k,.sx-k){flex:1 1 0!important;min-width:0!important;padding:18px!important;background:#f1f5f3!important;border:1px solid #dde3df!important;border-radius:12px!important;text-align:left!important;}
__ZONE__ .cad-flo-f{align-self:center!important;flex:0 0 12px!important;}
__ZONE__ :is(.cad-flo-t,.ec-k-l,.sx-k-l,.int-lab,.sx-leg-h,.ec-sec){font:700 14px/1.5 Georgia,serif!important;color:#104b3b!important;letter-spacing:0!important;text-transform:none!important;}
__ZONE__ :is(.cad-flo-v,.ec-k-v,.sx-k-v){font:700 26px/1.4 Georgia,serif!important;margin:8px 0!important;}
__ZONE__ :is(.cad-flo-x,.ec-k-s,.sx-k-s,.sx-th-x){font:400 12px/1.6 Georgia,serif!important;color:#4b5550!important;}
__ZONE__ .cad-nrm{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:20px!important;}
__ZONE__ .cad-nrm>div{padding:20px!important;border:1px solid #dde3df!important;border-radius:12px!important;min-width:0!important;}
__ZONE__ :is(.ex-etape,.cad-ex-t){margin:24px 0 12px!important;padding:0 0 10px!important;border-bottom:1px solid #dde3df!important;}
__ZONE__ .ex-etape .l{display:none!important;}
__ZONE__ .ex-etape .n{background:#f1f5f3!important;color:#104b3b!important;border-radius:8px!important;}
__ZONE__ :is(.ex-tab,.ec-tab,.sx-tab,.cad-it){border:1px solid #dde3df!important;border-radius:10px!important;overflow:hidden!important;}
__ZONE__ :is(.ex-tab,.ec-tab,.sx-tab,.cad-it) tbody tr:nth-child(even){background:#f7f9f8!important;}
__ZONE__ :is(.ex-tab,.ec-tab,.sx-tab) td.n{text-align:right!important;font-variant-numeric:tabular-nums!important;}
__ZONE__ :is(.ex-note,.ec-note,.ex-pan-x,.ex-etape-x,.sx-leg-x){font:400 13px/1.65 Georgia,serif!important;color:#4b5550!important;max-width:80ch!important;}
__ZONE__ :is(.sx-leg,.int-perf){padding:20px!important;border:1px solid #dde3df!important;border-radius:12px!important;background:#f1f5f3!important;}
__ZONE__ .apri-step{display:flex;align-items:center;gap:10px;font:700 18px/1.5 Georgia,serif;color:#104b3b;margin:20px 0 12px;}
__ZONE__ .apri-step span{font-size:12px;background:#f1f5f3;border:1px solid #dde3df;border-radius:8px;padding:6px 10px;}
__ZONE__ :is(.st-key-correlation_definition,.st-key-correlation_profiles){padding:20px!important;border:1px solid #dde3df!important;border-radius:14px!important;}
__ZONE__ [data-testid="stDataFrame"]{border:1px solid #dde3df;border-radius:10px;overflow:hidden;}
@media(max-width:1000px){
__ZONE__ .cad-ch{grid-template-columns:repeat(2,minmax(0,1fr))!important;}
__ZONE__ .cad-flo{flex-wrap:wrap!important;}
__ZONE__ .cad-flo-e{flex-basis:40%!important;}
__ZONE__ .cad-flo-f{display:none!important;}
}
@media(max-width:700px){
__ZONE__ .cad-ch{grid-template-columns:1fr!important;}
__ZONE__ .cad-nrm{grid-template-columns:1fr!important;}
__ZONE__ :is(.ec-kpi,.sx-kpi){flex-direction:column!important;}
__ZONE__ .cad-flo-e{flex-basis:100%!important;}
}
</style>"""
