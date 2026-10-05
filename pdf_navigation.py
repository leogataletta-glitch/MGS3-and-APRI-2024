"""Visible scrolling controls for the native, virtualized PDF reader."""
import json
import streamlit.components.v1 as components
from publication_web import tr


def render(reader_key="cad_methodology_reader"):
    labels = [tr(("Monter dans le document", "Scroll document up", "Subir en el documento", "Monte nan dokiman an")),
              tr(("Descendre dans le document", "Scroll document down", "Bajar en el documento", "Desann nan dokiman an"))]
    components.html('''<script>
    const labels = LABELS;
    let attempts = 0;
    function attach() {
      const host = parent.document.querySelector('.st-key-READER_KEY [data-testid="stBidiComponentIsolated"]');
      const root = host && host.shadowRoot;
      const scroller = root && root.querySelector('[data-testid="pdf-content"]');
      if (!scroller) { if (++attempts < 100) setTimeout(attach, 150); return; }
      if (root.querySelector('#apri-pdf-navigation')) return;
      const style = document.createElement('style');
      style.textContent = `
        [data-testid="pdf-content"]{overflow-y:scroll!important;scrollbar-width:auto!important;scrollbar-color:#28745c #e7eeea!important;scrollbar-gutter:stable;overscroll-behavior:contain;}
        [data-testid="pdf-content"]::-webkit-scrollbar{width:14px!important;display:block!important;}
        [data-testid="pdf-content"]::-webkit-scrollbar-track{background:#e7eeea;}
        [data-testid="pdf-content"]::-webkit-scrollbar-thumb{background:#28745c;border:3px solid #e7eeea;border-radius:8px;}
        #apri-pdf-navigation{position:absolute;top:8px;left:8px;z-index:5;display:flex;gap:6px;background:white;padding:5px;border:1px solid #d4dfd8;border-radius:8px;}
        #apri-pdf-navigation button{width:38px;height:38px;background:white;border:1px solid #d4dfd8;border-radius:5px;color:#174e3d;font-size:22px;cursor:pointer;}
        #apri-pdf-navigation button:focus-visible{outline:2px solid #28745c;outline-offset:2px;}
      `;
      root.append(style);
      scroller.tabIndex = 0;
      const bar = document.createElement('nav');
      bar.id = 'apri-pdf-navigation';
      labels.forEach((label, i) => {
        const button = document.createElement('button');
        button.textContent = i ? '↓' : '↑';
        button.title = label;
        button.setAttribute('aria-label', label);
        button.onclick = () => scroller.scrollBy({top:(i ? 1 : -1)*scroller.clientHeight*0.9,behavior:'smooth'});
        bar.append(button);
      });
      root.querySelector('[data-testid="pdf-container"]').append(bar);
    }
    attach();
    </script>'''.replace('LABELS', json.dumps(labels, ensure_ascii=False)).replace('READER_KEY', reader_key), height=0)
