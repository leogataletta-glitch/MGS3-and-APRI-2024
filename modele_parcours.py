"""A three-step explanation of the measurement framework."""
import json
from pathlib import Path
import streamlit.components.v1 as components
from publication_web import tr
from traductions import text


def render(attributes, dimensions, sources):
    copy = {
        'hide_steps': True,
        'steps': [tr(x) for x in [
            ('3 capacités', '3 capacities', '3 capacidades', '3 kapasite'),
            ('7 dimensions', '7 dimensions', '7 dimensiones', '7 dimansyon'),
            ('4 sources', '4 sources', '4 fuentes', '4 sous')]],
        'titles': [tr(x) for x in [
            ('Que mesure-t-on ?', 'What do we measure?', '¿Qué medimos?', 'Kisa nou mezire?'),
            ('Dans quels domaines ?', 'In which areas?', '¿En qué ámbitos?', 'Nan ki domèn?'),
            ('Avec quelles données ?', 'Using which data?', '¿Con qué datos?', 'Avèk ki done?')]],
        'intro': [tr(x) for x in [
            ('Nous mesurons trois capacités de résilience : anticiper les chocs, absorber leurs effets et s’adapter durablement.',
             'We measure three resilience capacities: anticipating shocks, absorbing their effects and adapting over time.',
             'Medimos tres capacidades de resiliencia: anticipar los impactos, absorber sus efectos y adaptarse de forma duradera.',
             'Nou mezire twa kapasite rezilyans: antisipe chòk yo, absòbe efè yo epi adapte sou lontan.'),
            ('Des indicateurs nous aident à mesurer ces capacités dans sept dimensions du paysage et de la société qui y vit.',
             'Indicators help us measure these capacities across seven dimensions of the landscape and the society living within it.',
             'Los indicadores nos ayudan a medir estas capacidades en siete dimensiones del paisaje y de la sociedad que lo habita.',
             'Endikatè yo ede nou mezire kapasite sa yo nan sèt dimansyon peyizaj la ak sosyete ki viv ladan l.'),
            ('Pour renseigner ces indicateurs, nous mobilisons quatre sources de données complémentaires.',
             'Four complementary data sources provide the information needed for these indicators.',
             'Cuatro fuentes de datos complementarias aportan la información necesaria para estos indicadores.',
             'Kat sous done ki konplete youn lòt bay enfòmasyon pou endikatè sa yo.')]],
        'summary': '',
        'resume': tr(('Reprendre', 'Resume', 'Reanudar', 'Reprann')),
        'pause': tr(('Pause', 'Pause', 'Pausa', 'Poz')),
        'next': tr(('Suivant', 'Next', 'Siguiente', 'Swivan')),
        'previous': tr(('Précédent', 'Previous', 'Anterior', 'Anvan')),
        'attributes': [[text(a), text(b)] for a, b in attributes],
        'dimensions': [text(d) for d in dimensions],
        'sources': [[text(a), text(b)] for a, b in sources],
    }
    payload = json.dumps(copy, ensure_ascii=False).replace('<', '\\u003c')
    html = Path(__file__).with_name('modele_parcours.html').read_text(encoding='utf-8')
    components.html(html.replace('__CONTENT__', payload), height=540, scrolling=True)


def render_feedback(stages, summary=None):
    copy = {
        'steps': [str(i + 1) for i in range(len(stages))],
        'titles': [text(t) for t, x, e in stages],
        'intro': [text(x) for t, x, e in stages],
        'slides': [[text(e)] for t, x, e in stages],
        'summary': '',
        'previous': tr(('Précédent', 'Previous', 'Anterior', 'Anvan')),
        'next': tr(('Suivant', 'Next', 'Siguiente', 'Swivan')),
        'pause': tr(('Pause', 'Pause', 'Pausa', 'Poz')),
        'resume': tr(('Reprendre', 'Resume', 'Reanudar', 'Reprann')),
    }
    payload = json.dumps(copy, ensure_ascii=False).replace('<', '\\u003c')
    html = Path(__file__).with_name('modele_parcours.html').read_text(encoding='utf-8')
    components.html(html.replace('__CONTENT__', payload), height=540, scrolling=True)
