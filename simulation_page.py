"""A fictional household decision game, independent of measured APRI scores."""
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
import i18n


def render():
    html = Path(__file__).with_name('simulation_landscape.html').read_text(encoding='utf-8')
    components.html(html.replace('__LANG__', i18n.get_lang()),
                    height=1150, scrolling=True)
