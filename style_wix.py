"""Composition grand écran inspirée du modèle Wix 3104, avec les contenus APRI."""

from traductions import text as _locale_text
import html
import streamlit as st
import accueil2_page as home
import assets
import carte_zoom
import i18n
from i18n import T


def appliquer():
    st.markdown('''<style>
    @import url('https://fonts.googleapis.com/css2?family=Caudex:wght@400;700&display=swap');
    :root {--accent:#2d3c27;--accent-2:#eabc80;--encre:#2d3c27;}
    .st-key-zone_page h1,.st-key-zone_page h2,.st-key-zone_page h3 {
        font-family:Caudex,Georgia,serif!important;font-weight:400!important;}
    .st-key-zone_nav {background:#2d3c27!important;}
    .st-key-zone_nav .nav-famille,.st-key-zone_nav .nav-devise {color:#eabc80!important;}
    .st-key-zone_nav div[data-testid="stButton"] > button,
    .st-key-zone_nav div[data-testid="stButton"] > button p {color:#fff!important;}
    .st-key-zone_nav div[data-testid="stButton"] > button {background:transparent!important;}
    .st-key-zone_nav div[data-testid="stButton"] > button:hover {background:#ffffff18!important;}
    .stApp .st-key-zone_nav div[class*="st-key-nav_"] div[data-testid="stButton"] > button p {
        color:#fff!important;}
    .stApp .st-key-zone_nav div[class*="st-key-nav_"] div[data-testid="stButton"] > button {
        background:transparent!important;color:#fff!important;}
    .stApp .st-key-zone_nav div[class*="st-key-nav_"] div[data-testid="stButton"] > button::before {
        filter:brightness(0) invert(1);}
    .stApp .st-key-zone_nav div[class*="st-key-nav_"] div[data-testid="stButton"] > button[kind="primary"] {
        background:#eabc80!important;border-left-color:#eabc80!important;}
    .stApp .st-key-zone_nav div[class*="st-key-nav_"] div[data-testid="stButton"] > button[kind="primary"] p {
        color:#2d3c27!important;}
    .stApp .st-key-zone_nav div[class*="st-key-nav_"] div[data-testid="stButton"] > button[kind="primary"]::before {
        filter:none;}
    .st-key-zone_nav [data-testid="stExpander"] {background:#fff;color:#2d3c27;}
    .st-key-zone_page button[kind="primary"] {background:#2d3c27!important;border-color:#2d3c27!important;}
    .st-key-wx_home {background:#2d3c27;margin:0 -2.6rem 0 -2rem!important;
        padding:0!important;gap:0!important;}
    .wx-brand {display:flex;align-items:center;gap:13px;color:#eabc80;
        font:20px/1.3 Caudex,Georgia,serif;padding:28px 46px; padding-right:150px;}
    .wx-brand img {width:38px;height:38px;}
    .wx-hero {position:relative;isolation:isolate;min-height:590px;
        padding:128px 46px 120px;color:#fff;}
    .wx-hero::before {content:"";position:absolute;z-index:-1;inset:0 0 0 32%;
        background-image:linear-gradient(90deg,#2d3c2780,#2d3c2722),var(--wx-photo);
        background-size:cover;background-position:center;}
    .wx-kicker {font:17px/1.5 Arial,sans-serif;color:#fff;margin-bottom:22px;max-width:650px;}
    .wx-title {font:400 clamp(42px,4.8vw,76px)/1.1 Caudex,Georgia,serif!important;
        color:#fff!important;letter-spacing:-1px;max-width:920px;margin:0!important;}
    .wx-lead {font:15px/1.85 Arial,sans-serif;color:#fff!important;
        max-width:445px;margin:28px 0 0!important;hyphens:none!important;text-align:left!important;}
    .wx-credit {font:11px/1.5 Arial,sans-serif;color:#e1e5dc;margin-top:22px;}
    .st-key-wx_cta {position:relative;margin:-95px 0 50px 46px!important;}
    .st-key-zone_page .st-key-wx_cta div[data-testid="stButton"] > button {
        border:1px solid #fff!important;border-radius:0!important;background:transparent!important;
        min-height:44px!important;height:auto!important;padding:10px 25px!important;box-shadow:none!important;}
    .st-key-zone_page .st-key-wx_cta div[data-testid="stButton"] > button p {color:#fff!important;}
    .st-key-wx_round {position:relative;margin:-470px 26px 355px auto!important;width:110px!important;}
    .st-key-zone_page .st-key-wx_round div[data-testid="stButton"] > button {
        border:0!important;border-radius:50%!important;background:#eabc80!important;
        width:110px!important;height:110px!important;min-height:110px!important;padding:12px!important;box-shadow:none!important;}
    .st-key-zone_page .st-key-wx_round div[data-testid="stButton"] > button p {
        font:18px Caudex,Georgia,serif!important;color:#2d3c27!important;}
    .st-key-wx_agenda,.st-key-wx_numbers {padding:52px 46px!important;background:#2d3c27;}
    .wx-heading {font:400 43px/1.14 Caudex,Georgia,serif;color:#fff;margin-bottom:34px;}
    .wx-topic {display:flex;gap:15px;font:22px/1.3 Caudex,Georgia,serif;color:#fff;margin:12px 0 20px;}
    .wx-topic span {color:#eabc80;}
    .wx-description {font:14px/1.9 Arial,sans-serif;color:#f1f3ee!important;margin:0 0 18px!important;}
    .st-key-zone_page .st-key-wx_agenda div[data-testid="stButton"] > button {
        border:0!important;border-bottom:1px solid #eabc8066!important;border-radius:0!important;
        background:transparent!important;min-height:42px!important;height:auto!important;padding:10px 0!important;
        box-shadow:none!important;justify-content:flex-start!important;}
    .st-key-zone_page .st-key-wx_agenda div[data-testid="stButton"] > button p {color:#eabc80!important;}
    .wx-about {display:grid;grid-template-columns:1fr 1fr;background:#eabc80;color:#2d3c27;}
    .wx-about-photo {min-height:365px;background-size:cover;background-position:center;}
    .wx-about-copy {padding:48px 38px;}
    .wx-about .wx-heading {color:#2d3c27;font-size:38px;margin-bottom:24px;}
    .wx-about p {font:14px/1.9 Arial,sans-serif;color:#2d3c27!important;}
    .wx-numbers {display:grid;grid-template-columns:repeat(4,1fr);gap:30px;}
    .wx-numbers strong {display:block;color:#eabc80;font:46px/1.2 Caudex,Georgia,serif;}
    .wx-numbers span {font:13px/1.7 Arial,sans-serif;color:#fff;}
    .st-key-wx_map {background:#fff;padding:45px 46px!important;}
    .st-key-wx_map .wx-heading {color:#2d3c27;}
    .wx-footer {padding:28px 46px;color:#eabc80;font:13px/1.7 Arial,sans-serif;background:#2d3c27;}
    .st-key-zone_langue_h div[data-testid="stButton"] > button p {color:#fff!important;text-shadow:none!important;}
    @media(max-width:1000px){.st-key-wx_home{margin-left:-2.6rem!important;}
        .wx-brand{padding:60px 24px 25px;padding-right:110px;font-size:16px;}
        .wx-hero{min-height:510px;padding:70px 24px 110px;}
        .wx-hero::before{left:15%;}.wx-title{font-size:46px!important;}
        .st-key-wx_round{display:none!important;}
        [data-testid="stLayoutWrapper"]:has(> .st-key-wx_round){display:none!important;}
        .st-key-wx_cta{margin-left:24px!important;}
        .st-key-wx_agenda,.st-key-wx_numbers,.st-key-wx_map{padding:35px 24px!important;}
        .wx-numbers{grid-template-columns:repeat(2,1fr);}.wx-about-copy{padding:32px 24px;}}
    @media(max-width:640px){.wx-about{grid-template-columns:1fr;}.wx-about-photo{min-height:230px;}
        .wx-title{font-size:38px!important;}.wx-heading{font-size:34px;}
        .wx-hero::before{left:0;opacity:.4;}.wx-hero{padding-top:45px;}}
    </style>''', unsafe_allow_html=True)


def _go(mode):
    st.session_state['app_mode'] = mode


def accueil():
    fr = i18n.get_lang() == 'fr'
    e = html.escape
    river = home._photo_b64(prefere='accueil2_hero.jpg')
    sea = home._photo_b64(prefere='accueil2_hero_b.jpg')
    with st.container(key='wx_home'):
        st.markdown(f'<div class="wx-brand"><img src="data:image/png;base64,{assets.EMBLEME_APRI}" alt="APRI"><span>APRI · {_locale_text("Paysages & résilience" if fr else "Landscapes & resilience")}</span></div>', unsafe_allow_html=True)
        title = (_locale_text('Comprendre les territoires.<br>Renforcer la résilience.' if fr else
                 'Understanding landscapes.<br>Strengthening resilience.'))
        st.markdown(f'''<div class="wx-hero" style="--wx-photo:url('data:image/jpeg;base64,{river}')">
            <div class="wx-kicker">{e(T('a2_inst')).replace('|', ' ')}</div>
            <h1 class="wx-title">{title}</h1><p class="wx-lead">{e(T('a2_intro'))}</p>
            <div class="wx-credit">{_locale_text('Vallée de la Voldrogue · Grand’Anse · Haïti, 2024' if fr else 'Voldrogue valley · Grand’Anse · Haiti, 2024')}</div></div>''', unsafe_allow_html=True)
        with st.container(key='wx_cta'):
            st.button(_locale_text(T('a2_cta')), key='wx_results', on_click=_go, args=('dimensions',))
        with st.container(key='wx_round'):
            st.button(_locale_text('Explorer ↗' if fr else 'Explore ↗'), key='wx_round_results', on_click=_go, args=('dimensions',))
        with st.container(key='wx_agenda'):
            st.markdown('<div class="wx-heading">' + (_locale_text('Au cœur de l’approche' if fr else 'At the heart of the approach')) + '</div>', unsafe_allow_html=True)
            cols=st.columns(3,gap='large')
            for col, (mode, tk, xk) in zip(cols,[('accueil','a2_p2_t','a2_p2_x'),('boucles','a2_p3_t','a2_p3_x'),('actions','a2_p4_t','a2_p4_x')]):
                with col:
                    st.markdown(f'<div class="wx-topic"><span>○</span>{e(T(tk))}</div><p class="wx-description">{e(T(xk))}</p>', unsafe_allow_html=True)
                    st.button(_locale_text('Découvrir →' if fr else 'Discover →'), key=f'wx_go_{mode}', on_click=_go, args=(mode,), use_container_width=True)
        about_title=_locale_text('Observer les paysages,<br>écouter les populations.' if fr else 'Observing landscapes.<br>Listening to communities.')
        about_text=(_locale_text('L’approche APRI met en relation les conditions de vie des ménages, les caractéristiques des paysages et les capacités locales. Le Sud et la Grand’Anse constituent les deux territoires pilotes de cette démarche.' if fr else 'APRI connects household living conditions, landscape characteristics and local capacities. Sud and Grand’Anse are the two pilot territories for this approach.'))
        st.markdown(f'''<div class="wx-about"><div class="wx-about-photo" role="img" aria-label="Baie de Corail, Grand’Anse" style="background-image:url('data:image/jpeg;base64,{sea}')"></div><div class="wx-about-copy"><div class="wx-heading">{about_title}</div><p>{e(about_text)}</p></div></div>''', unsafe_allow_html=True)
        with st.container(key='wx_numbers'):
            st.markdown('<div class="wx-heading">' + (_locale_text('Une enquête ancrée sur le terrain' if fr else 'An inquiry grounded in fieldwork')) + '</div>', unsafe_allow_html=True)
            households, sections=home._chiffres()
            stats=[(home._fmt(households)+'+' if households else '1 200+',T('a2_c1_x')),
                   (str(sections or 10),T('a2_c2_x')),('2',T('a2_c3_x')),(T('a2_c4_n'),T('a2_c4_x'))]
            st.markdown('<div class="wx-numbers">'+''.join(f'<div><strong>{e(n)}</strong><span>{e(t)}</span></div>' for n,t in stats)+'</div>',unsafe_allow_html=True)
        with st.container(key='wx_map'):
            st.markdown(f'<div class="wx-heading">{e(T("a2_carte_t"))}</div>', unsafe_allow_html=True)
            if not carte_zoom.render():
                st.markdown(home._carte_svg(), unsafe_allow_html=True)
        st.markdown(f'<div class="wx-footer">APRI · {e(T("a2_kicker"))}<br>Sud & Grand’Anse · Haïti · 2024</div>', unsafe_allow_html=True)
