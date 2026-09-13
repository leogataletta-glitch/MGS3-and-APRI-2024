"""Styles facultatifs : le rendu historique reste le choix par défaut."""
import html
import streamlit as st
import i18n
import assets
import accueil2_page as home
import carte_zoom
from i18n import T


def choix():
    return st.session_state.get("style_site", 1)


def _changer(cle):
    st.session_state["style_site"] = st.session_state[cle]


def selecteur(prefix):
    fr = i18n.get_lang() == "fr"
    labels = ({1: "Style 1 · Actuel", 2: "Style 2 · Vert tendre et forêt",
               3: "Style 3 · Vert foncé et blanc", 4: "Style 4 · Inspiration Wix",
               5: "Style 5 · Nature, vert et blanc", 6: "Style 6 · Panorama sombre", 7: "Style 7 · Tableau de bord pastel"} if fr else
              {1: "Style 1 · Original", 2: "Style 2 · Light green & forest",
               3: "Style 3 · Dark green & white", 4: "Style 4 · Wix inspired",
               5: "Style 5 · Nature, green & white", 6: "Style 6 · Dark panorama", 7: "Style 7 · Pastel dashboard"})
    cle = f"{prefix}_style_site"
    st.markdown('''<style>
        .st-key-zone_nav [data-testid="stExpander"] summary,
        .st-key-zone_nav [data-testid="stExpander"] summary p {
            background:#fff!important;color:#123d2c!important;}
        </style>''', unsafe_allow_html=True)
    with st.expander("Changer le style" if fr else "Change style"):
        st.session_state[cle] = choix()
        st.radio("Style visuel" if fr else "Visual style", [1, 2, 3, 4, 5, 6, 7],
                 format_func=labels.get, key=cle, on_change=_changer, args=(cle,))


def appliquer():
    if choix() == 7:
        import style_dashboard
        style_dashboard.appliquer()
        return
    if choix() == 1:
        return
    if choix() == 6:
        import style_panorama
        style_panorama.appliquer()
        return
    if choix() == 5:
        import style_nature
        style_nature.appliquer()
        return
    if choix() == 4:
        import style_wix
        style_wix.appliquer()
        return
    dark, light = (("#273b16", "#cce0ad") if choix() == 2 else
                   ("#123d2c", "#ffffff"))
    st.markdown(f"""<style>
    :root {{ --accent:{dark}; --accent-2:{dark}; --encre:{dark}; }}
    .st-key-zone_page h1,.st-key-zone_page h2,.st-key-zone_page h3,
    .st-key-zone_page .titre-bloc {{font-family:Arial,sans-serif!important;
        font-weight:400!important;color:{dark};}}
    .st-key-zone_nav {{background:{light}!important;}}
    .st-key-zone_nav button p {{font-family:Arial,sans-serif!important;}}
    .st-key-zone_nav [data-testid="stExpander"] {{background:#fff;color:{dark};}}
    .st-key-zone_page [data-testid="stTabs"] button[aria-selected="true"] {{color:{dark}!important;}}
    .st-key-zone_page button[kind="primary"] {{background:{dark}!important;border-color:{dark}!important;}}
    .st-key-zone_langue_h button p {{color:white!important;}}
    .st-key-zone_langue_h button {{color:white!important;}}
    .cmp-hero {{margin:0 -2.6rem 0 -2rem;padding:38px 44px 110px;
       background-size:cover;background-position:center 38%;color:white;}}
    .cmp-brand {{display:flex;gap:16px;align-items:center;padding-right:90px;
       margin-bottom:54px;font:15px/1.5 Arial,sans-serif;}}
    .cmp-brand img {{width:56px;height:56px;}}
    .cmp-title {{font:400 clamp(36px,4.4vw,66px)/1.04 Arial,sans-serif;
       letter-spacing:-1.8px;max-width:760px;color:#fff;}}
    .cmp-intro {{color:#fff!important;font:15px/1.75 Arial,sans-serif;
       max-width:510px;margin:38px 0 0!important;}}
    .cmp-credit {{font:11px/1.5 Arial,sans-serif;color:#fff;margin-top:18px;}}
    .st-key-cmp_cta {{margin:-88px 0 44px 14px!important;position:relative;}}
    .st-key-cmp_cta button {{background:transparent!important;border:1px solid #fff!important;
       border-radius:30px!important;color:#fff!important;box-shadow:none!important;}}
    .st-key-cmp_cta button p {{color:#fff!important;}}
    .st-key-zone_page .st-key-cmp_cta div[data-testid="stButton"] > button {{
        color:#fff!important;height:46px!important;min-height:46px!important;
        padding:10px 22px!important;}}
    .st-key-zone_page .st-key-cmp_cta div[data-testid="stButton"] > button p,
    .st-key-zone_page .st-key-cmp_actions div[data-testid="stButton"] > button p,
    .st-key-zone_page .st-key-cmp_actions div[data-testid="stButton"] > button em {{color:#fff!important;}}
    .st-key-cmp_discover {{background:{light};padding:40px 24px!important;}}
    .cmp-heading {{font:400 32px/1.12 Arial,sans-serif;letter-spacing:-.8px;
       color:{dark};margin:0 0 26px;}}
    .cmp-photo {{height:210px;background-size:cover;background-position:center;}}
    .st-key-cmp_discover button {{background:transparent!important;border:0!important;
       box-shadow:none!important;text-align:left!important;color:{dark}!important;}}
    .st-key-cmp_actions {{background:{dark};padding:40px 24px!important;}}
    .st-key-cmp_actions .cmp-heading {{color:#fff;}}
    .st-key-cmp_actions button {{background:transparent!important;border:1px solid #ffffff80!important;
       border-radius:0!important;color:white!important;min-height:160px;box-shadow:none!important;}}
    .st-key-cmp_actions button p,.st-key-cmp_actions button em {{color:#fff!important;}}
    .cmp-stats {{background:{dark};color:white;display:grid;grid-template-columns:repeat(4,1fr);
       gap:24px;padding:38px 24px;margin:0;}}
    .cmp-stats strong {{font:400 36px Arial,sans-serif;display:block;color:white;}}
    .cmp-stats span {{font:12px/1.6 Arial,sans-serif;}}
    .st-key-cmp_map {{padding:36px 24px!important;background:#fff;}}
    @media(max-width:1000px) {{.cmp-hero {{margin-left:-2.6rem;padding:82px 24px 118px;}}
       .cmp-brand {{padding-right:0;margin-bottom:32px;}}
       .cmp-stats {{grid-template-columns:repeat(2,1fr);}}
       .cmp-title {{font-size:38px;}}}}
    </style>""", unsafe_allow_html=True)


def _go(mode):
    st.session_state["app_mode"] = mode


def accueil():
    """Accueil Canva avec les vrais boutons, chiffres et carte du site."""
    if choix() == 7:
        import style_dashboard
        style_dashboard.accueil()
        return
    if choix() == 6:
        import style_panorama
        style_panorama.accueil()
        return
    if choix() == 5:
        import style_nature
        style_nature.accueil()
        return
    if choix() == 4:
        import style_wix
        style_wix.accueil()
        return
    fr = i18n.get_lang() == "fr"
    e = html.escape
    river = home._photo_b64(prefere="accueil2_hero.jpg")
    sea = home._photo_b64(prefere="accueil2_hero_b.jpg")
    dark = "#273b16" if choix() == 2 else "#123d2c"
    st.markdown(f"""<style>.st-key-cmp_actions {{
        background-image:linear-gradient(90deg,{dark}ee,{dark}99),url('data:image/jpeg;base64,{sea}');
        background-size:cover;background-position:center 60%;}}
        </style>""", unsafe_allow_html=True)
    title = ("Des paysages vivants.<br>Des populations<br>plus résilientes." if fr else
             "Living landscapes.<br>More resilient<br>communities.")
    inst = e(T("a2_inst")).replace("|", "<br>")
    st.markdown(f'''<div class="cmp-hero" style="background-color:{dark};
        background-image:linear-gradient(90deg,{dark}e6,{dark}44),url('data:image/jpeg;base64,{river}')">
        <div class="cmp-brand"><img src="data:image/png;base64,{assets.EMBLEME_APRI}" alt="APRI"><span>{inst}</span></div>
        <div class="cmp-title">{title}</div><p class="cmp-intro">{e(T('a2_intro'))}</p>
        <div class="cmp-credit">{'Vallée de la Voldrogue · Grand’Anse · Haïti, 2024' if fr else 'Voldrogue valley · Grand’Anse · Haiti, 2024'}</div></div>''', unsafe_allow_html=True)
    with st.container(key="cmp_cta"):
        st.button(T("a2_cta") + " ↗", key="cmp_results", on_click=_go, args=("dimensions",))
    with st.container(key="cmp_discover"):
        st.markdown('<div class="cmp-heading">' + ("Comprendre les liens<br>qui façonnent un territoire." if fr else
                    "Understand the connections<br>that shape a landscape.") + '</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        entries = [(river, "Les paysages" if fr else "Landscapes", "accueil"),
                   (sea, "Les populations" if fr else "Communities", "dimensions"),
                   (river, "La résilience" if fr else "Resilience", "boucles")]
        for i, (col, (photo, label, mode)) in enumerate(zip(cols, entries)):
            with col:
                st.markdown(f'<div class="cmp-photo" style="background-image:url(\'data:image/jpeg;base64,{photo}\');background-position:{20+i*30}% center"></div>', unsafe_allow_html=True)
                st.button(label + " ↗", key=f"cmp_tile_{i}", on_click=_go, args=(mode,), use_container_width=True)
    with st.container(key="cmp_actions"):
        st.markdown('<div class="cmp-heading">' + ("De la connaissance<br>aux possibilités d’action." if fr else
                    "From understanding<br>to opportunities for action.") + '</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for col, (mode, title_key, text_key) in zip(cols, [("dimensions", "a2_p1_t", "a2_p1_x"),
                  ("boucles", "a2_p3_t", "a2_p3_x"), ("actions", "a2_p4_t", "a2_p4_x")]):
            with col:
                st.button(f'{T(title_key)}  \n*{T(text_key)}*  \n↗', key=f"cmp_action_{mode}",
                          on_click=_go, args=(mode,), use_container_width=True)
    menages, sections = home._chiffres()
    stats = [(home._fmt(menages) + "+" if menages else "1 200+", T("a2_c1_x")),
             (str(sections or 10), T("a2_c2_x")), ("2", T("a2_c3_x")), (T("a2_c4_n"), T("a2_c4_x"))]
    st.markdown('<div class="cmp-stats">' + ''.join(f'<div><strong>{e(n)}</strong><span>{e(label)}</span></div>' for n, label in stats) + '</div>', unsafe_allow_html=True)
    with st.container(key="cmp_map"):
        st.markdown(f'<div class="cmp-heading">{e(T("a2_carte_t"))}</div>', unsafe_allow_html=True)
        if not carte_zoom.render():
            st.markdown(home._carte_svg(), unsafe_allow_html=True)
