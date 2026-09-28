"""Interactive views of the same signed, directed causal graph."""
import textwrap
import plotly.graph_objects as go
import streamlit as st
from publication_web import tr

def figure(m, rang, edges, centre, positions, loop=None):
    ids = list(positions)
    points = {n: (x, -y) for n, (x, y) in positions.items()}
    highlighted = set()
    if loop:
        ns = loop['noeuds']
        highlighted = {(ns[i], ns[(i + 1) % len(ns)]) for i in range(len(ns))}
    fig = go.Figure()
    for e in edges:
        a, b = (e['de'], e['vers'])
        if a not in points or b not in points:
            continue
        start, end = (points[a], points[b])
        color = '#28745c' if e['signe'] > 0 else '#a34242'
        sign = '+' if e['signe'] > 0 else '−'
        opacity = 1 if not loop or (a, b) in highlighted else 0.12
        tip = f"{m['noms'].get(a, a)} → {m['noms'].get(b, b)} ({sign})"
        kwargs = dict(x=[start[0], end[0]], y=[start[1], end[1]], mode='lines', line=dict(color=color, width=3 if (a, b) in highlighted else 1.5), opacity=opacity, hoverinfo='skip', showlegend=False)
        mid = tuple((0.4 * x + 0.6 * y for x, y in zip(start, end)))
        fig.add_trace(go.Scatter(**kwargs))
        fig.add_annotation(x=0.94 * end[0] + 0.06 * start[0], y=0.94 * end[1] + 0.06 * start[1], ax=0.84 * end[0] + 0.16 * start[0], ay=0.84 * end[1] + 0.16 * start[1], xref='x', yref='y', axref='x', ayref='y', text='', showarrow=True, arrowhead=2, arrowcolor=color, opacity=opacity)
        fig.add_trace(go.Scatter(x=[mid[0]], y=[mid[1]], mode='text', text=[sign], textfont=dict(color=color, size=14), hovertext=[tip], hoverinfo='text', showlegend=False, opacity=opacity))
    labels = ['<br>'.join(textwrap.wrap(m['noms'].get(n, n), 22)) for n in ids]
    common = dict(x=[points[n][0] for n in ids], y=[points[n][1] for n in ids], mode='markers+text', text=labels, textposition='top center', textfont=dict(family='Georgia', size=12, color='#104b3b'), hovertext=[m['noms'].get(n, n) for n in ids], hoverinfo='text', marker=dict(size=[16 if n == centre else 9 for n in ids], color=['#104b3b' if n == centre else '#9cbbab' for n in ids], line=dict(color='white', width=1)), showlegend=False)
    fig.add_trace(go.Scatter(**common))
    fig.update_layout(height=650, margin=dict(l=30, r=30, t=45, b=30), paper_bgcolor='white', plot_bgcolor='white', font=dict(family='Georgia', color='#104b3b'), showlegend=False)
    fig.update_layout(dragmode='pan', xaxis=dict(visible=False), yaxis=dict(visible=False, scaleanchor='x', scaleratio=1))
    return fig

def render(m, rang, edges, centre, positions, loop=None):
    st.caption(tr(('Molette : zoom · Glisser : déplacer · Double-clic : vue complète.', 'Scroll to zoom · Drag to pan · Double-click to reset the view.', 'Rueda: zoom · Arrastrar: desplazar · Doble clic: vista completa.', 'Wou sourit: zoum · Trennen: deplase · Double klik: wè tout.')))
    st.plotly_chart(figure(m, rang, edges, centre, positions, loop), use_container_width=True, key='causal_explore_2d', config={'scrollZoom': True, 'displayModeBar': True, 'displaylogo': False, 'doubleClick': 'reset', 'toImageButtonOptions': {'format': 'png', 'filename': 'APRI-schema'}})
