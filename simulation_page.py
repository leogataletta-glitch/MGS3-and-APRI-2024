"""A fictional household decision game, independent of measured APRI scores."""
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
import i18n


def render():
    fr = i18n.get_lang() == 'fr'
    mode = st.radio('Jeu' if fr else 'Game', ['platform', 'decisions'],
                    format_func=lambda x: ('Parcours 2D' if fr else '2D platformer') if x == 'platform'
                    else ('Vivre du paysage' if fr else 'Living from the landscape'),
                    horizontal=True, key='simulation_game')
    name = 'simulation_platform.html' if mode == 'platform' else 'simulation.html'
    html = Path(__file__).with_name(name).read_text(encoding='utf-8')
    components.html(html.replace('__LANG__', i18n.get_lang()),
                    height=650 if mode == 'platform' else 1050, scrolling=True)
