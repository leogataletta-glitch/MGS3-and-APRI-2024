"""Style 5 : modèle Wix 2500 adapté à APRI, en vert et blanc."""
import html
import streamlit as st
import accueil2_page as home
import assets
import carte_zoom
import i18n
from i18n import T


def appliquer():
    st.markdown('''<style>
    :root{--accent:#176b45;--accent-2:#176b45;--encre:#123d2c;}
    .st-key-zone_page h1,.st-key-zone_page h2,.st-key-zone_page h3{
        font-family:Georgia,"Times New Roman",serif!important;font-weight:400!important;}
    .st-key-zone_nav{background:#fff!important;}
    .st-key-zone_nav .nav-famille{color:#176b45!important;}
    .st-key-zone_page button[kind="primary"]{background:#176b45!important;border-color:#176b45!important;}
    .st-key-n5_home{margin:0 -2.6rem 0 -2rem!important;padding:0!important;gap:0!important;background:white;}
    .n5-brand{display:flex;align-items:center;gap:12px;padding:24px 44px;padding-right:145px;
        color:#123d2c;font:700 18px/1.3 Georgia,"Times New Roman",serif;}
    .n5-brand img{width:44px;height:44px;}
    .n5-brand small{display:block;font:11px/1.5 Arial,sans-serif;margin-top:4px;letter-spacing:1px;}
    .n5-hero{position:relative;padding:55px 44px 115px;min-height:540px;
        background-size:cover;background-position:center;}
    .n5-line{width:105px;height:15px;background:#176b45;margin-bottom:28px;}
    .st-key-n5_home .n5-title{color:#123d2c!important;font:400 clamp(36px,4.6vw,66px)/1.12 Georgia,"Times New Roman",serif!important;
        letter-spacing:-.5px!important;text-transform:none;text-align:left!important;hyphens:none!important;max-width:870px;margin:0!important;}
    .n5-title span{color:#176b45;}
    .n5-intro{color:#234b38!important;font:15px/1.85 Arial,sans-serif;max-width:440px;
        margin:28px 0 0!important;text-align:left!important;hyphens:none!important;}
    .n5-credit{font:11px/1.5 Arial,sans-serif;color:#345640;margin-top:18px;}
    .st-key-n5_cta{position:relative;margin:-85px 0 38px 44px!important;}
    .st-key-zone_page .st-key-n5_cta div[data-testid="stButton"] > button{
        background:#176b45!important;border:1px solid #176b45!important;border-radius:0!important;
        min-height:46px!important;height:auto!important;padding:12px 24px!important;box-shadow:none!important;}
    .st-key-zone_page .st-key-n5_cta div[data-testid="stButton"] > button p{color:#fff!important;font-weight:700!important;}
    .n5-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:25px;padding:48px 44px;background:white;}
    .n5-stats strong{display:block;font:600 40px/1.2 Arial,sans-serif;color:#176b45;letter-spacing:-1px;}
    .n5-stats span{font:14px/1.6 Arial,sans-serif;color:#123d2c;display:block;margin-top:10px;max-width:150px;}
    .st-key-n5_mosaic [data-testid="stHorizontalBlock"]{gap:0!important;align-items:stretch!important;}
    .st-key-n5_mosaic [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]{flex:1 1 0!important;min-width:0!important;}
    .st-key-n5_mosaic [data-testid="stColumn"]:has(.st-key-n5_about){background:#123d2c;min-height:350px;}
    .st-key-n5_mosaic [data-testid="stColumn"]:has(.st-key-n5_projects){background:#29835e;min-height:350px;}
    .st-key-n5_mosaic [data-testid="stColumn"]:has(.st-key-n5_photo){background-size:cover;background-position:center;min-height:350px;}
    .st-key-n5_about,.st-key-n5_projects,.st-key-n5_links{padding:34px 30px!important;height:100%;}
    .st-key-n5_about{background:#123d2c;}.st-key-n5_projects{background:#29835e;}
    .n5-heading{font:400 29px/1.25 Georgia,"Times New Roman",serif;color:#fff;margin:0 0 22px;letter-spacing:-.7px;}
    .n5-copy{font:14px/1.9 Arial,sans-serif;color:#fff!important;margin:0 0 26px!important;hyphens:none!important;text-align:left!important;}
    .n5-image{height:1px;}
    .st-key-zone_page .st-key-n5_mosaic div[data-testid="stButton"] > button{
        background:transparent!important;border:1px solid #ffffffb3!important;border-radius:0!important;
        height:auto!important;min-height:42px!important;padding:10px 18px!important;box-shadow:none!important;}
    .st-key-zone_page .st-key-n5_mosaic div[data-testid="stButton"] > button p{color:white!important;}
    .st-key-n5_help{background:#176b45;padding:48px 44px!important;}
    .st-key-n5_help [data-testid="stHorizontalBlock"]{align-items:center!important;}
    .n5-help-title{font:400 38px/1.2 Georgia,"Times New Roman",serif;color:white;letter-spacing:-1px;max-width:470px;}
    .st-key-zone_page .st-key-n5_help div[data-testid="stButton"] > button{
        background:white!important;border:1px solid white!important;border-radius:0!important;
        height:auto!important;min-height:46px!important;padding:12px 23px!important;box-shadow:none!important;}
    .st-key-zone_page .st-key-n5_help div[data-testid="stButton"] > button p{color:#123d2c!important;}
    .st-key-n5_map{padding:44px!important;background:#fff;}
    .st-key-n5_map .n5-heading{color:#123d2c;font-size:34px;text-transform:none;margin-bottom:25px;}
    .n5-footer{padding:27px 44px;background:#123d2c;color:white;font:12px/1.8 Arial,sans-serif;}
    .st-key-zone_langue_h div[data-testid="stButton"] > button p{color:#123d2c!important;text-shadow:none!important;}
    @media(max-width:1000px){.st-key-n5_home{margin-left:-2.6rem!important;}
        .n5-brand{padding:60px 24px 22px;padding-right:120px;font-size:15px;}
        .n5-hero{padding:40px 24px 110px;}.st-key-n5_cta{margin-left:24px!important;}
        .n5-stats{grid-template-columns:repeat(2,1fr);padding:30px 24px;}
        .st-key-n5_map,.st-key-n5_help{padding:30px 24px!important;}
        .st-key-n5_about,.st-key-n5_projects{padding:28px 22px!important;}}
    @media(max-width:700px){.st-key-n5_mosaic [data-testid="stHorizontalBlock"]{flex-direction:column!important;}
        .st-key-n5_mosaic [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]{width:100%!important;flex:1 1 auto!important;}
        .st-key-n5_mosaic [data-testid="stColumn"]:has(.st-key-n5_photo){min-height:230px;}
        .st-key-n5_mosaic [data-testid="stColumn"]:has(.st-key-n5_about),
        .st-key-n5_mosaic [data-testid="stColumn"]:has(.st-key-n5_projects){min-height:0;}
        .st-key-n5_home .n5-title{font-size:38px!important;letter-spacing:-1px!important;}
        .n5-help-title{font-size:34px;}.n5-heading{font-size:27px;}}
    </style>''', unsafe_allow_html=True)


def _go(mode):
    st.session_state['app_mode']=mode


def accueil():
    fr=i18n.get_lang()=='fr'
    e=html.escape
    river=home._photo_b64(prefere='accueil2_hero.jpg')
    sea=home._photo_b64(prefere='accueil2_hero_b.jpg')
    st.markdown(f'''<style>.st-key-n5_mosaic [data-testid="stColumn"]:has(.st-key-n5_photo){{background-image:url('data:image/jpeg;base64,{sea}');}}</style>''',unsafe_allow_html=True)
    with st.container(key='n5_home'):
        st.markdown(f'<div class="n5-brand"><img src="data:image/png;base64,{assets.EMBLEME_APRI}" alt="APRI"><div>APRI<small>{"PAYSAGES & RÉSILIENCE" if fr else "LANDSCAPES & RESILIENCE"}</small></div></div>',unsafe_allow_html=True)
        title=('Renforcer<br><span>la résilience.</span>' if fr else 'Strengthen<br><span>resilience.</span>')
        st.markdown(f'''<div class="n5-hero" style="background-image:linear-gradient(90deg,#ffffffed 0%,#ffffffc9 38%,#ffffff22 100%),url('data:image/jpeg;base64,{river}')">
        <div class="n5-line"></div><h1 class="n5-title">{title}</h1><p class="n5-intro">{e(T('a2_intro'))}</p>
        <div class="n5-credit">{'Vallée de la Voldrogue · Grand’Anse · Haïti, 2024' if fr else 'Voldrogue valley · Grand’Anse · Haiti, 2024'}</div></div>''',unsafe_allow_html=True)
        with st.container(key='n5_cta'):
            st.button(T('a2_cta')+' →',key='n5_results',on_click=_go,args=('dimensions',))
        menages,sections=home._chiffres()
        stats=[(home._fmt(menages)+'+' if menages else '1 200+',T('a2_c1_x')),
               (str(sections or 10),T('a2_c2_x')),('2',T('a2_c3_x')),('10+','mois de terrain' if fr else 'months of fieldwork')]
        st.markdown('<div class="n5-stats">'+''.join(f'<div><strong>{e(n)}</strong><span>{e(t)}</span></div>' for n,t in stats)+'</div>',unsafe_allow_html=True)
        with st.container(key='n5_mosaic'):
            left,photo,right=st.columns([1,1,1],gap='small')
            with left:
                with st.container(key='n5_about'):
                    st.markdown('<div class="n5-heading">'+('Comprendre<br>les territoires' if fr else 'Understand<br>the territories')+'</div><p class="n5-copy">'+('Paysages, populations et capacités locales : une lecture intégrée du Sud et de la Grand’Anse.' if fr else 'Landscapes, communities and local capacities: an integrated understanding of Sud and Grand’Anse.')+'</p>',unsafe_allow_html=True)
                    st.button(T('a2_p2_t')+' →',key='n5_territory',on_click=_go,args=('accueil',))
            with photo:
                with st.container(key='n5_photo'):
                    st.markdown('<div class="n5-image" role="img" aria-label="Baie de Corail, Grand’Anse"></div>',unsafe_allow_html=True)
            with right:
                with st.container(key='n5_projects'):
                    st.markdown('<div class="n5-heading">'+('Relier les<br>dimensions' if fr else 'Connect the<br>dimensions')+'</div><p class="n5-copy">'+('Explorer les boucles de rétroaction pour comprendre les interactions entre les dimensions de la résilience.' if fr else 'Explore feedback loops to understand the interactions between dimensions of resilience.')+'</p>',unsafe_allow_html=True)
                    st.button(T('a2_p3_t')+' →',key='n5_system',on_click=_go,args=('boucles',))
        with st.container(key='n5_help'):
            left,right=st.columns([1.1,1],gap='large')
            with left:
                st.markdown('<div class="n5-help-title">'+('Passer de la lecture<br>à l’action.' if fr else 'From understanding<br>to action.')+'</div>',unsafe_allow_html=True)
            with right:
                st.markdown('<p class="n5-copy">'+('Retrouver les fiches d’intervention et les pistes d’action éclairées par les observations et les résultats de l’enquête.' if fr else 'Explore intervention profiles and opportunities for action informed by field observations and survey results.')+'</p>',unsafe_allow_html=True)
                st.button(T('a2_p4_t')+' →',key='n5_actions',on_click=_go,args=('actions',))
        with st.container(key='n5_map'):
            st.markdown(f'<div class="n5-heading">{e(T("a2_carte_t"))}.</div>',unsafe_allow_html=True)
            if not carte_zoom.render():
                st.markdown(home._carte_svg(),unsafe_allow_html=True)
        st.markdown(f'<div class="n5-footer">APRI · {e(T("a2_kicker"))}<br>Sud & Grand’Anse · Haïti · 2024</div>',unsafe_allow_html=True)
