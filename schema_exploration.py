"""Static-style causal diagram with draggable nodes and SVG pan/zoom."""
import json
from pathlib import Path
import streamlit.components.v1 as components
from publication_web import tr
import i18n
from provenance_relations import describe, labels as provenance_labels


def causal_layout(ids, edges, centre):
    """Directed reachability within the displayed graph, with cycles separated."""
    def reach(reverse=False):
        distances = {centre: 0}
        todo = [centre]
        for n in todo:
            for e in edges:
                a, b = (e['vers'], e['de']) if reverse else (e['de'], e['vers'])
                if a == n and b not in distances:
                    distances[b] = distances[n] + 1
                    todo.append(b)
        return distances
    upstream, downstream = reach(True), reach()
    groups = {'causes': [], 'effects': [], 'feedback': [], 'other': []}
    for n in ids:
        if n == centre: continue
        kind = ('feedback' if n in upstream and n in downstream else
                'causes' if n in upstream else 'effects' if n in downstream else 'other')
        groups[kind].append(n)
    positions = {centre: (0, 0)}
    for kind in ('causes', 'effects'):
        ds = upstream if kind == 'causes' else downstream
        levels = {}
        for n in groups[kind]: levels.setdefault(ds[n], []).append(n)
        for depth, ns in levels.items():
            for i, n in enumerate(ns):
                positions[n] = ((i - (len(ns)-1)/2)*190, (1 if kind=='causes' else -1)*(140*depth + (i//5)*90))
    extent = max([abs(x) for x,y in positions.values()] + [190]) + 230
    for kind, direction in (('feedback',1), ('other',-1)):
        ns = groups[kind]
        for i,n in enumerate(ns): positions[n] = (direction*extent, (i-(len(ns)-1)/2)*85)
    return positions, groups


def render(m, rang, edges, centre, positions, loop=None):
    from systeme_complexe import _correlation
    edges = [dict(e, evidence=describe(e, i18n.get_lang(), _correlation(m, e['de'], e['vers']))) for e in edges]
    data = dict(nodes=[dict(id=n, label=m['noms'].get(n,n), x=x, y=y,
                           rank=rang.get(n,9), central=n==centre)
                       for n,(x,y) in positions.items()], edges=edges, loop=loop)
    labels = dict(reset=tr(('Réinitialiser','Reset','Restablecer','Reyinisyalize')),
                  causes=tr(('Causes possibles · racines','Possible causes · roots','Posibles causas · raíces','Kòz posib · rasin')),
                  effects=tr(('Conséquences possibles · branches','Possible consequences · branches','Posibles consecuencias · ramas','Konsekans posib · branch')),
                  feedback=tr(('Rétroactions · les deux sens','Feedback · both directions','Retroacciones · ambos sentidos','Retwoaksyon · toude sans')),
                  other=tr(('Autres liens du modèle','Other model links','Otros vínculos del modelo','Lòt lyen modèl la')))
    positions, groups = causal_layout(list(positions), edges, centre)
    for node in data['nodes']:
        node['x'], node['y'] = positions[node['id']]
    data['groups'] = groups
    labels.update(provenance_labels(i18n.get_lang()))
    payload=json.dumps(dict(data=data,labels=labels),ensure_ascii=False).replace('<','\\u003c')
    html=Path(__file__).with_name('schema_interactif.html').read_text(encoding='utf-8')
    components.html(html.replace('__PAYLOAD__',payload),height=900,scrolling=True)
