"""Download controls for rendered result charts and tables."""

from traductions import component_html as _locale_html

from traductions import text as _locale_text
from pathlib import Path
import streamlit.components.v1 as components
import i18n

def activer(enabled=True):
    script = Path(__file__).with_suffix('.js').read_text(encoding='utf-8')
    script = script.replace('__FR__', _locale_text('true' if i18n.get_lang() == 'fr' else 'false'))
    script = script.replace('__ENABLED__', 'true' if enabled else 'false')
    components.html(_locale_html('<script>' + script + '</script>'), height=0, width=0)
