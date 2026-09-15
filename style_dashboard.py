"""Style 7 : tableau de bord pastel, fond ivoire et panneau anthracite."""

from traductions import text as _locale_text
import html
import json
import streamlit as st
import accueil2_page as home
import carte_zoom
import i18n
from i18n import T


def appliquer():
    st.markdown('''<style>
    :root{--accent:#303332;--accent-2:#459aa0;}
    .st-key-zone_page h1,.st-key-zone_page h2,.st-key-zone_page h3{font-family:Arial,sans-serif!important;color:#303332!important;font-weight:600!important;}
    .st-key-zone_nav{background:#fff!important;}
    .stApp .st-key-zone_nav div[class*="st-key-nav_"] div[data-testid="stButton"] > button{background:transparent!important;color:#303332!important;}
    .stApp .st-key-zone_nav div[class*="st-key-nav_"] div[data-testid="stButton"] > button p{color:#303332!important;font-family:Arial,sans-serif!important;}
    .stApp .st-key-zone_nav div[class*="st-key-nav_"] div[data-testid="stButton"] > button[kind="primary"]{background:#303332!important;border-left-color:#e7bb79!important;}
    .stApp .st-key-zone_nav div[class*="st-key-nav_"] div[data-testid="stButton"] > button[kind="primary"] p{color:white!important;}
    .stApp .st-key-zone_nav div[class*="st-key-nav_"] div[data-testid="stButton"] > button[kind="primary"]::before{filter:brightness(0) invert(1);}
    .st-key-zone_page{background:#faf7f2!important;}
    .st-key-d7_home{padding:30px 4px!important;gap:24px!important;}
    .d7-header{padding-right:100px;margin-bottom:16px;}
    .st-key-zone_page .d7-header h1{font:600 27px/1.2 Arial,sans-serif!important;margin:0 0 8px!important;text-align:left!important;hyphens:none!important;}
    .d7-muted{font:12px/1.7 Arial,sans-serif;color:#747675;}
    .d7-cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-bottom:22px;}
    .d7-card{background:white;border:1px solid #eeece9;border-radius:12px;padding:18px 14px;box-shadow:0 5px 18px #36302b06;min-height:150px;}
    .d7-icon{display:inline-flex;width:32px;height:32px;align-items:center;justify-content:center;border-radius:9px;margin-bottom:16px;color:#79512b;background:#ffe3bc;font:18px Arial;}
    .d7-card:nth-child(2) .d7-icon{background:#fbe0e4;color:#b55c70;}.d7-card:nth-child(3) .d7-icon{background:#d4f5f7;color:#2a8590;}
    .d7-number{font:400 30px/1.2 Arial,sans-serif;color:#303332;white-space:nowrap;}.d7-card small{display:block;color:#626765;font:12px/1.5 Arial;margin-top:7px;}
    .st-key-d7_chart,.st-key-d7_map{background:white;padding:22px!important;border:1px solid #eeece9;border-radius:12px;box-shadow:0 5px 18px #36302b06;}
    .d7-heading{font:600 16px/1.4 Arial,sans-serif;color:#303332;margin:0 0 12px;}
    .d7-chart{width:100%;height:auto;display:block;}.d7-legend{display:flex;gap:20px;font:11px Arial;color:#707472;margin-top:8px;}
    .st-key-d7_home [data-testid="stColumn"]:has(>div .st-key-d7_panel){background:#303332;border-radius:22px;padding:25px 22px!important;}
    .st-key-d7_panel{gap:18px!important;}
    .d7-panel-title{font:600 18px/1.4 Arial;color:#fff;margin-bottom:8px;}
    .d7-panel-copy{font:13px/1.75 Arial;color:#d0d2d0;text-align:left!important;hyphens:none!important;}
    .d7-badges{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:18px 0;}.d7-badges div{padding:14px 10px;border-radius:9px;background:#ffe3bc;font:12px/1.6 Arial;color:#38403d;}.d7-badges div+div{background:#d4f5f7;}
    .d7-photo{height:240px;border-radius:12px;background-size:cover;background-position:center;margin:8px 0 18px;}
    .st-key-zone_page .st-key-d7_panel div[data-testid="stButton"] > button{background:#424745!important;border:1px solid #626864!important;border-radius:9px!important;min-height:46px!important;height:auto!important;padding:12px!important;box-shadow:none!important;}
    .st-key-zone_page .st-key-d7_panel div[data-testid="stButton"] > button p{color:white!important;font:13px/1.5 Arial,sans-serif!important;}
    .st-key-zone_page .st-key-d7_links div[data-testid="stButton"] > button{background:#fff!important;border:1px solid #eae5de!important;border-radius:10px!important;min-height:48px!important;height:auto!important;box-shadow:none!important;}
    .st-key-zone_page .st-key-d7_links div[data-testid="stButton"] > button p{color:#303332!important;font:13px/1.5 Arial!important;}
    .st-key-zone_langue_h div[data-testid="stButton"] > button p{color:#303332!important;text-shadow:none!important;}
    @media(max-width:1000px){.st-key-d7_home{padding-top:65px!important;}.d7-header{padding-right:0;}.d7-cards{gap:8px;}.d7-card{padding:13px 9px;}.d7-number{font-size:25px;}}
    @media(max-width:650px){.d7-cards{grid-template-columns:1fr;}.d7-card{min-height:100px;}.d7-icon{float:right;}.d7-photo{height:190px;}}
    </style>''',unsafe_allow_html=True)


def _go(mode):
    st.session_state['app_mode']=mode


def _effectifs():
    p=home._trouver('ventilation.json')
    if not p:
        return {}
    with open(p,encoding='utf-8') as f:
        return json.load(f).get('effectifs',{})


def _chart(eff,fr):
    # Real survey counts, zero-based stacked columns; no illustrative trends.
    if not eff:
        return
    maximum=max(sum(d.get(k,0) or 0 for k in ('Homme','Femme')) for d in eff.values()) or 1
    top=((maximum//25)+1)*25
    svg=['<svg class="d7-chart" viewBox="0 0 620 280" role="img" aria-label="'+(_locale_text('Effectifs par section et sexe' if fr else 'Sample counts by section and sex'))+'">']
    for val in range(0,top+1,25):
        y=205-val/top*170
        svg.append(f'<path d="M38 {y}H610" stroke="#eeefed"/><text x="28" y="{y+4}" text-anchor="end" fill="#7b807c" font-size="10">{val}</text>')
    for i,(name,d) in enumerate(eff.items()):
        x=48+i*56
        h=(d.get('Homme',0) or 0)/top*170
        f=(d.get('Femme',0) or 0)/top*170
        label=html.escape(name)
        svg.append(f'<g><title>{label} : {d.get("Homme",0)} / {d.get("Femme",0)}</title><rect x="{x}" y="{205-h}" width="20" height="{h}" rx="3" fill="#499da4"/><rect x="{x}" y="{205-h-f}" width="20" height="{f}" rx="3" fill="#dc8192"/><text transform="translate({x+10},220) rotate(-35)" text-anchor="end" fill="#6e7570" font-size="10">{label}</text></g>')
    svg.append('</svg>')
    st.markdown(''.join(svg),unsafe_allow_html=True)


def accueil():
    fr=i18n.get_lang()=='fr'
    e=html.escape
    eff=_effectifs()
    total=sum(d.get('Total',0) or 0 for d in eff.values())
    with st.container(key='d7_home'):
        st.markdown('<div class="d7-header"><h1>'+(_locale_text('Vue d’ensemble des territoires' if fr else 'Territories at a glance'))+'</h1><div class="d7-muted">APRI · '+(_locale_text('Enquête ménage 2024 · Sud & Grand’Anse' if fr else 'Household survey 2024 · Sud & Grand’Anse'))+'</div></div>',unsafe_allow_html=True)
        left,right=st.columns([1.65,1],gap='large')
        with left:
            stats=[('▦',home._fmt(total) if eff else '—',T('a2_c1_x')),('⌖',str(len(eff)) if eff else '—',T('a2_c2_x')),('◉','2',T('a2_c3_x'))]
            st.markdown('<div class="d7-cards">'+''.join(f'<div class="d7-card"><span class="d7-icon">{icon}</span><div class="d7-number">{e(n)}</div><small>{e(label)}</small></div>' for icon,n,label in stats)+'</div>',unsafe_allow_html=True)
            with st.container(key='d7_chart'):
                st.markdown('<div class="d7-heading">'+(_locale_text('La participation à l’enquête' if fr else 'Survey participation'))+'</div><div class="d7-muted">'+(_locale_text('Ménages enquêtés par section · sexe de la personne répondante' if fr else 'Surveyed households by section · respondent sex'))+'</div>',unsafe_allow_html=True)
                _chart(eff,fr)
                st.markdown('<div class="d7-legend"><span><span style="color:#499da4">●</span> '+(_locale_text('Hommes' if fr else 'Men'))+'</span><span><span style="color:#dc8192">●</span> '+(_locale_text('Femmes' if fr else 'Women'))+'</span></div><div class="d7-muted">Source : APRI · 2024</div>',unsafe_allow_html=True)
            with st.container(key='d7_links'):
                st.button(_locale_text(T('a2_cta')+' →'),key='d7_results',on_click=_go,args=('dimensions',),use_container_width=True)
            with st.container(key='d7_map'):
                st.markdown(f'<div class="d7-heading">{e(T("a2_carte_t"))}</div>',unsafe_allow_html=True)
                if not carte_zoom.render():
                    st.markdown(home._carte_svg(),unsafe_allow_html=True)
        with right:
            with st.container(key='d7_panel'):
                st.markdown('<div class="d7-panel-title">'+(_locale_text('Comprendre la résilience' if fr else 'Understanding resilience'))+'</div><div class="d7-panel-copy">'+e(T('a2_intro'))+'</div><div class="d7-badges"><div>Sud<br><strong>'+(_locale_text('Territoire pilote' if fr else 'Pilot territory'))+'</strong></div><div>Grand’Anse<br><strong>'+(_locale_text('Territoire pilote' if fr else 'Pilot territory'))+'</strong></div></div>',unsafe_allow_html=True)
                photo=home._photo_b64(prefere='accueil2_hero_b.jpg')
                st.markdown(f'<div class="d7-photo" role="img" aria-label="Baie de Corail" style="background-image:url(\'data:image/jpeg;base64,{photo}\')"></div><div class="d7-panel-title">'+(_locale_text('Votre parcours APRI' if fr else 'Explore APRI'))+'</div>',unsafe_allow_html=True)
                for mode,tk in [('accueil','a2_p2_t'),('boucles','a2_p3_t'),('actions','a2_p4_t')]:
                    st.button(_locale_text(T(tk)+' →'),key=f'd7_{mode}',on_click=_go,args=(mode,),use_container_width=True)
