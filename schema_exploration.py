"""Static-style causal diagram with draggable nodes and SVG pan/zoom."""
import json
from pathlib import Path
import streamlit.components.v1 as components
from publication_web import tr


def render(m, rang, edges, centre, positions, loop=None):
    data = dict(nodes=[dict(id=n, label=m['noms'].get(n,n), x=x, y=y,
                           rank=rang.get(n,9), central=n==centre)
                       for n,(x,y) in positions.items()], edges=edges, loop=loop)
    labels = dict(hint=tr(('Déplacez un cadre : les flèches suivent · Molette : zoom · Glissez le fond : déplacer le schéma.',
                          'Drag a box: arrows follow · Scroll: zoom · Drag the background: pan.',
                          'Arrastre un cuadro: las flechas siguen · Rueda: zoom · Arrastre el fondo: desplazar.',
                          'Trennen yon bwat: flèch yo swiv · Wou sourit: zoum · Trennen fon an: deplase.')),
                  reset=tr(('Réinitialiser','Reset','Restablecer','Reyinisyalize')))
    payload=json.dumps(dict(data=data,labels=labels),ensure_ascii=False).replace('<','\\u003c')
    html=Path(__file__).with_name('schema_interactif.html').read_text(encoding='utf-8')
    components.html(html.replace('__PAYLOAD__',payload),height=650,scrolling=False)
