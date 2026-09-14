"""Download controls for rendered result charts and tables."""
from pathlib import Path
import streamlit.components.v1 as components
import i18n

def activer(enabled=True):
    script = Path(__file__).with_suffix('.js').read_text(encoding='utf-8')
    script = script.replace('__FR__', 'true' if i18n.get_lang() == 'fr' else 'false')
    script = script.replace('__ENABLED__', 'true' if enabled else 'false')
    components.html('<script>' + script + '</script>', height=0, width=0)
