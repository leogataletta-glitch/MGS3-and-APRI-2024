"""Style 6 : panorama blanc, inspiré du modèle Wix wh-1176."""
import html
import streamlit as st
import accueil2_page as home
import assets
import carte_zoom
import i18n
from i18n import T


def appliquer():
    st.markdown('''<style>
    :root{--accent:#252c32;--accent-2:#697c90;}
    .st-key-zone_page h1,.st-key-zone_page h2,.st-key-zone_page h3{font-family:Arial,sans-serif!important;font-weight:700!important;}
    .st-key-zone_nav{background:#ffffff!important;}
    .st-key-zone_nav .nav-famille,.st-key-zone_nav .nav-devise{color:#525d64!important;}
    .stApp .st-key-zone_nav div[class*="st-key-nav_"] div[data-testid="stButton"] > button{background:transparent!important;color:#26343d!important;}
    .stApp .st-key-zone_nav div[class*="st-key-nav_"] div[data-testid="stButton"] > button p{color:#35424b!important;}
    .stApp .st-key-zone_nav div[class*="st-key-nav_"] div[data-testid="stButton"] > button::before{filter:brightness(.4);}
    .stApp .st-key-zone_nav div[class*="st-key-nav_"] div[data-testid="stButton"] > button[kind="primary"]{background:#e7edef!important;border-left-color:#587381!important;}
    .st-key-zone_nav [data-testid="stExpander"]{background:#fff;color:#111;}
    .st-key-zone_page button[kind="primary"]{background:#252c32!important;border-color:#252c32!important;}
    .st-key-p6_home{background:#ffffff;margin:0 -2.6rem 0 -2rem!important;padding:0 20px!important;gap:0!important;}
    .p6-brand{display:flex;align-items:center;gap:12px;color:#26343d;font:15px Arial,sans-serif;padding:20px 0;padding-right:125px;}
    .p6-brand img{width:30px;height:30px;}
    .p6-hero{min-height:450px;position:relative;isolation:isolate;padding:30px 24px 100px;background-size:cover;background-position:center 35%;}
    .p6-hero::after{content:"";position:absolute;inset:0;z-index:-1;pointer-events:none;
        background-image:radial-gradient(#ffffff33 .8px,transparent .9px),linear-gradient(0deg,#ffffff 0%,transparent 40%,#ffffff22 100%);background-size:4px 4px,100% 100%;}
    .st-key-p6_home .p6-title{font:700 clamp(35px,4.6vw,64px)/1.05 Arial,sans-serif!important;color:#20343f!important;letter-spacing:-1.4px!important;margin:0!important;max-width:830px;text-align:left!important;hyphens:none!important;word-break:normal!important;overflow-wrap:normal!important;}
    .p6-intro{max-width:520px;font:15px/1.8 Arial,sans-serif;color:#43545e!important;margin:0 0 20px!important;text-align:left!important;hyphens:none!important;}
    .st-key-p6_intro{background:#ffffff;padding:0 24px 24px!important;}
    .st-key-zone_page .st-key-p6_intro div[data-testid="stButton"] > button{border-radius:0!important;background:#e7eef1!important;border:1px solid #cad6dc!important;padding:11px 23px!important;min-height:44px!important;height:auto!important;box-shadow:none!important;}
    .st-key-zone_page .st-key-p6_intro div[data-testid="stButton"] > button p{color:#17191d!important;}
    .p6-row{display:grid;grid-template-columns:1fr 1fr;gap:45px;padding:50px 0;}
    .p6-label{font:12px/1.6 monospace;color:#35424b;text-transform:uppercase;letter-spacing:.5px;}
    .p6-subtitle{font:700 25px/1.22 Arial,sans-serif;color:#263b47;margin-bottom:21px;}
    .p6-copy{font:14px/1.8 Arial,sans-serif;color:#53616a!important;margin:0!important;hyphens:none!important;text-align:left!important;}
    .p6-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;}
    .p6-stat{min-height:185px;padding:30px 22px;display:flex;flex-direction:column;justify-content:flex-end;
        background:radial-gradient(#929baa11 .8px,transparent 1px),linear-gradient(140deg,#eaf0f3,#f5f7f8);background-size:5px 5px,100% 100%;}
    .p6-stat strong{font:700 52px/1.1 Arial,sans-serif;color:#263b47;letter-spacing:-1px;}
    .p6-stat span{font:12px/1.5 monospace;text-transform:uppercase;color:#53616a;margin-top:12px;}
    .st-key-p6_services{background:radial-gradient(ellipse at 10% 60%,#cfdee866,transparent 70%);padding:0 0 44px!important;}
    .st-key-p6_services [data-testid="stHorizontalBlock"]{gap:28px!important;}
    .p6-side-photo{height:420px;background-size:cover;background-position:center;filter:saturate(.65);}
    .st-key-p6_options{background:#f7f7f5;padding:12px 24px!important;}
    .st-key-zone_page .st-key-p6_options div[data-testid="stButton"] > button{background:transparent!important;border:0!important;border-bottom:1px solid #c7cbd0!important;border-radius:0!important;
        height:auto!important;min-height:115px!important;padding:22px 0!important;text-align:left!important;box-shadow:none!important;justify-content:flex-start!important;}
    .st-key-zone_page .st-key-p6_options div[data-testid="stButton"] > button p{color:#1b2026!important;font:700 19px/1.4 Arial,sans-serif!important;}
    .st-key-zone_page .st-key-p6_options div[data-testid="stButton"] > button em{color:#525b65!important;font:400 13px/1.6 Arial,sans-serif!important;}
    .st-key-p6_map{background:#f7f7f5;padding:30px 24px!important;}
    .st-key-p6_map .p6-subtitle{color:#181d23;margin-bottom:25px;}
    .p6-footer{background:#ffffff;color:#53616a;padding:26px 0;font:12px/1.7 Arial,sans-serif;}
    .st-key-zone_langue_h div[data-testid="stButton"] > button p{color:#263b47!important;text-shadow:none!important;}
    @media(max-width:1000px){.st-key-p6_home{margin-left:-2.6rem!important;padding:0 15px!important;}.p6-brand{padding:62px 10px 22px;}
        .p6-hero{min-height:390px;padding:26px 16px 80px;}.st-key-p6_home .p6-title{font-size:42px!important;}
        .p6-row{gap:25px;padding:38px 10px;}.p6-stat{padding:22px 16px;}.p6-stat strong{font-size:38px;}}
    @media(max-width:650px){.p6-row{grid-template-columns:1fr;gap:16px;}.p6-stats{grid-template-columns:1fr;}
        .p6-stat{min-height:130px;}.p6-side-photo{height:240px;}.st-key-p6_home .p6-title{font-size:36px!important;}}
    </style>''',unsafe_allow_html=True)


def _go(mode):
    st.session_state['app_mode']=mode


def accueil():
    fr=i18n.get_lang()=='fr'
    e=html.escape
    river=home._photo_b64(prefere='accueil2_hero.jpg')
    sea=home._photo_b64(prefere='accueil2_hero_b.jpg')
    with st.container(key='p6_home'):
        st.markdown(f'<div class="p6-brand"><img src="data:image/png;base64,{assets.EMBLEME_APRI}" alt="APRI">APRI · {"Paysages et résilience" if fr else "Landscapes and resilience"}</div>',unsafe_allow_html=True)
        title=('Comprendre aujourd’hui.<br>Renforcer la résilience de demain.' if fr else 'Understanding today.<br>Building tomorrow’s resilience.')
        st.markdown(f'''<div class="p6-hero" style="background-image:linear-gradient(90deg,#ffffffdd,#ffffff66),url('data:image/jpeg;base64,{river}')"><h1 class="p6-title">{title}</h1></div>''',unsafe_allow_html=True)
        with st.container(key='p6_intro'):
            st.markdown(f'<p class="p6-intro">{e(T("a2_intro"))}</p>',unsafe_allow_html=True)
            st.button(T('a2_cta')+' →',key='p6_results',on_click=_go,args=('dimensions',))
        label='NOTRE DÉMARCHE' if fr else 'OUR APPROACH'
        subtitle='Le paysage et les populations, une lecture commune.' if fr else 'Landscapes and communities, a shared perspective.'
        text=('APRI rapproche les observations de terrain, les conditions de vie des ménages et les caractéristiques des paysages. Le Sud et la Grand’Anse sont les deux territoires pilotes de cette approche intégrée.' if fr else 'APRI brings together field observations, household living conditions and landscape characteristics. Sud and Grand’Anse are the two pilot territories for this integrated approach.')
        st.markdown(f'<div class="p6-row"><div class="p6-label">{label}</div><div><div class="p6-subtitle">{subtitle}</div><p class="p6-copy">{e(text)}</p></div></div>',unsafe_allow_html=True)
        menages,sections=home._chiffres()
        stats=[(home._fmt(menages)+'+' if menages else '1 200+',T('a2_c1_x')),(str(sections or 10),T('a2_c2_x')),('2',T('a2_c3_x'))]
        st.markdown('<div class="p6-stats">'+''.join(f'<div class="p6-stat"><strong>{e(n)}</strong><span>{e(t)}</span></div>' for n,t in stats)+'</div>',unsafe_allow_html=True)
        st.markdown('<div class="p6-row"><div class="p6-label">'+('EXPLORER APRI' if fr else 'EXPLORE APRI')+'</div><div><div class="p6-subtitle">'+('Des données aux pistes d’action.' if fr else 'From data to opportunities for action.')+'</div><p class="p6-copy">'+('Choisissez une entrée pour découvrir les territoires, comprendre les interactions et consulter les fiches d’intervention.' if fr else 'Choose a starting point to discover the territories, understand interactions and explore intervention profiles.')+'</p></div></div>',unsafe_allow_html=True)
        with st.container(key='p6_services'):
            photo,links=st.columns([1,1],gap='large')
            with photo:
                st.markdown(f'<div class="p6-side-photo" role="img" aria-label="Baie de Corail, Grand’Anse" style="background-image:url(\'data:image/jpeg;base64,{sea}\')"></div>',unsafe_allow_html=True)
            with links:
                with st.container(key='p6_options'):
                    for mode,tk,xk in [('accueil','a2_p2_t','a2_p2_x'),('boucles','a2_p3_t','a2_p3_x'),('actions','a2_p4_t','a2_p4_x')]:
                        st.button(f'{T(tk)}  \n*{T(xk)}*  \n→',key=f'p6_{mode}',on_click=_go,args=(mode,),use_container_width=True)
        with st.container(key='p6_map'):
            st.markdown(f'<div class="p6-subtitle">{e(T("a2_carte_t"))}</div>',unsafe_allow_html=True)
            if not carte_zoom.render():
                st.markdown(home._carte_svg(),unsafe_allow_html=True)
        st.markdown(f'<div class="p6-footer">APRI · {e(T("a2_kicker"))}<br>Sud & Grand’Anse · Haïti, 2024</div>',unsafe_allow_html=True)
