"""Optional presentation; selecting version 1 leaves existing styles intact."""
import streamlit as st
import i18n

KEY = 'apri_visual_version'


def active():
    return st.session_state.get(KEY, 1) in (2, 3)


def selector():
    labels = {
        'fr': ('Actuel', 'Proposition', 'Aérien', 'Présentation'),
        'en': ('Current', 'Proposal', 'Airy', 'Appearance'),
        'es': ('Actual', 'Propuesta', 'Ligero', 'Presentación'),
        'ht': ('Aktyèl', 'Pwopozisyon', 'Lejè', 'Prezantasyon'),
    }.get(i18n.get_lang(), ('Current', 'Proposal', 'Airy', 'Appearance'))
    # Keep the preference separately: Streamlit removes widget keys when hidden.
    with st.container(key='visual_comparison'):
        choice = st.segmented_control(
            labels[3], [1, 2, 3], default=st.session_state.get(KEY, 1),
            format_func=lambda n: f'{n} · {labels[n - 1]}',
            selection_mode='single', key='visual_comparison_choice',
            label_visibility='collapsed',
        )
    st.session_state[KEY] = choice or 1


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
    </style>''', unsafe_allow_html=True)
    if st.session_state.get(KEY) == 3:
        st.markdown(f'''<style>
        {root} [role="radiogroup"]{{gap:16px!important;background:white!important;padding:0 0 16px!important;}}
        {root} [role="radiogroup"] label{{min-height:96px!important;padding:20px 16px!important;border-radius:12px!important;}}
        {root} [role="radiogroup"] label:has(input:checked){{background:#f1f5f3!important;border:0!important;box-shadow:inset 0 -2px #104b3b!important;border-radius:12px!important;}}
        {root} [role="radiogroup"] label p:not(:first-child){{margin-top:8px!important;}}
        @media(max-width:700px){{{root} [role="radiogroup"]{{gap:8px!important;}}{root} [role="radiogroup"] label{{min-height:80px!important;padding:12px!important;}}}}
        </style>''', unsafe_allow_html=True)


def apply():
    root = '.stApp' * 32
    zone = root + ' .st-key-zone_page'
    st.markdown(f'''<style>
    {root} .st-key-visual_comparison{{margin:0 0 12px!important;}}
    {root} .st-key-visual_comparison button{{min-height:32px!important;padding:4px 12px!important;}}
    {root} .st-key-visual_comparison button p{{font:12px/1.4 Georgia,serif!important;}}
    </style>''', unsafe_allow_html=True)
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

    if st.session_state.get(KEY) == 3:
        airy(zone)


def airy(zone):
    """More breathing room without increasing type or changing content."""
    st.markdown(f'''<style>
    {zone}{{padding-inline:28px!important;}}
    {zone}>[data-testid="stVerticalBlock"]{{gap:24px!important;}}
    {zone} :is(h2,h3,.titre-bloc,.cad-h,.cad-model-title,.ap-h,.ex-titre){{font-weight:400!important;margin-top:8px!important;margin-bottom:16px!important;}}
    {zone} :is([data-baseweb="select"]>div,[data-baseweb="input"],[data-baseweb="textarea"]){{background:white!important;border-radius:12px!important;min-height:48px!important;}}
    {zone} [data-testid="stMetric"]{{border:0!important;border-radius:16px!important;background:#f1f5f3!important;padding:24px!important;}}
    {zone} :is(th,td){{padding:14px 16px!important;}}
    {zone} th{{background:white!important;}}
    {zone} [data-testid="stExpander"] details{{border:0!important;border-bottom:1px solid #dde3df!important;border-radius:0!important;}}
    {zone} [data-testid="stPlotlyChart"],{zone} [data-testid="stVegaLiteChart"]{{border:0!important;padding:16px 0!important;}}
    {zone} :is(.stButton,.stDownloadButton) button{{border-radius:12px!important;}}
    @media(max-width:700px){{{zone}{{padding-inline:8px!important;}}{zone}>[data-testid="stVerticalBlock"]{{gap:16px!important;}}}}
    </style>''', unsafe_allow_html=True)
