"""Public session count, backed by CounterAPI v2; no browser tracking script."""
from datetime import date
from html import escape
import json
import re
from urllib.request import Request, urlopen

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError
import i18n


def configuration():
    try:
        raw = st.secrets.get('public_counter', {})
        workspace = str(raw.get('workspace', ''))
        name = str(raw.get('name', ''))
        token = str(raw.get('token', ''))
        since = str(raw.get('since', ''))
        if not raw.get('enabled', False):
            return None
        if not all(re.fullmatch(r'[A-Za-z0-9_-]+', x) for x in (workspace, name)):
            return None
        if not token or date.fromisoformat(since) > date.today():
            return None
        return workspace, name, token, since
    except (StreamlitSecretNotFoundError, ValueError, TypeError):
        return None


def request(workspace, name, token, operation):
    # Only the server contacts the provider. No visitor IP, answers, URL,
    # browser identifier or session identifier is forwarded.
    if operation not in ('up', 'stats'):
        raise ValueError('Unsupported counter operation')
    req = Request(
        f'https://api.counterapi.dev/v2/{workspace}/{name}/{operation}',
        headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/json'},
    )
    with urlopen(req, timeout=3) as response:
        return json.load(response)


def parse_total(payload):
    data = payload['data']
    up, down = data['up_count'], data['down_count']
    if type(up) is not int or type(down) is not int or min(up, down) < 0 or down > up:
        raise ValueError('Invalid counter total')
    return up - down


def register_once(state, config, sender=request):
    identity = (config[0], config[1], config[3])
    if state.get('_public_counter_attempt') == identity:
        return
    # Mark BEFORE sending: a timed-out request may already have incremented.
    # No blind retry on a filter rerun. Outages can undercount visits.
    state['_public_counter_attempt'] = identity
    try:
        sender(*config[:3], 'up')
    except Exception:
        # Provider errors must neither break APRI nor disclose credentials.
        pass


@st.cache_data(ttl=60, show_spinner=False)
def read_total(workspace, name, _token):
    try:
        return parse_total(request(workspace, name, _token, 'stats'))
    except Exception:
        return None


LABELS = {
    'fr': ('visites', 'depuis le', 'Compteur temporairement indisponible',
           'Une visite par session de navigation. Une nouvelle session ou un rechargement peut compter à nouveau. Ce ne sont pas des visiteurs uniques. Total indicatif, actualisé avec un léger délai.'),
    'en': ('visits', 'since', 'Visit counter temporarily unavailable',
           'One visit per browsing session. A new session or reload may count again. These are not unique visitors. Indicative total, updated with a short delay.'),
    'es': ('visitas', 'desde el', 'Contador temporalmente no disponible',
           'Una visita por sesión de navegación. Una nueva sesión o recarga puede contar de nuevo. No son visitantes únicos. Total orientativo, actualizado con un breve retraso.'),
    'ht': ('vizit', 'depi', 'Kontè a pa disponib pou kounye a',
           'Yon vizit pou chak sesyon navigasyon. Yon nouvo sesyon oswa rechaj ka konte ankò. Sa pa reprezante vizitè inik. Total la se yon endikasyon; li mete ajou ak yon ti reta.'),
}


def markup(total, since, lang):
    label, from_label, unavailable, help_text = LABELS.get(lang, LABELS['en'])
    when = date.fromisoformat(since)
    formatted_date = when.strftime('%d/%m/%Y') if lang != 'en' else when.isoformat()
    text = unavailable if total is None else (
        f'{total:,}'.replace(',', '\u202f') + f' {label} · {from_label} {formatted_date}')
    return (f'<div class="apri-public-counter" title="{escape(help_text, quote=True)}">'
            f'{escape(text)}</div>')


def render():
    config = configuration()
    if config is None:
        return  # Never show a fictional zero or count only this server's uptime.
    register_once(st.session_state, config)
    total = read_total(*config[:3])
    root = '.stApp' * 25
    st.markdown(f'<style>{root} .apri-public-counter{{font-family:Georgia,serif!important;'
                'font-size:12px!important;font-weight:400!important;line-height:1.5!important;'
                'color:#65716b!important;text-align:center!important;margin:16px 0 8px!important;'
                'padding:0!important;background:transparent!important;}}</style>'
                + markup(total, config[3], i18n.get_lang()), unsafe_allow_html=True)
