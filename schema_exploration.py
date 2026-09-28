"""Interactive views of the same signed, directed causal graph."""
import math
import textwrap
import plotly.graph_objects as go
import streamlit as st
from publication_web import tr


def figure(m, rang, edges, centre, positions, spatial=False, loop=None):
    ids = list(positions)
    if spatial:
        points = {centre: (0., 0., 0.)}
        for rank in sorted(set(rang.values())):
            nodes = sorted(n for n in ids if n != centre and rang[n] == rank)
            for i, n in enumerate(nodes):
                z = 1 - 2 * (i + .5) / len(nodes)
                angle = i * math.pi * (3 - math.sqrt(5))
                radius = max(1, rank)
                points[n] = (radius * math.sqrt(1-z*z) * math.cos(angle), radius * math.sqrt(1-z*z) * math.sin(angle), radius*z)
    else:
        points = {n: (x, -y) for n, (x,y) in positions.items()}
    highlighted = set()
    if loop:
        ns = loop['noeuds']
        highlighted = {(ns[i], ns[(i+1)%len(ns)]) for i in range(len(ns))}
    fig = go.Figure()
    if spatial:
        radius = max(1, max(rang.values(), default=1))
        angles = [2*math.pi*i/100 for i in range(101)]
        for plane in range(3):
            coords = [[0., 0., 0.] for _ in angles]
            for xyz, angle in zip(coords, angles):
                xyz[plane] = radius*math.cos(angle)
                xyz[(plane+1)%3] = radius*math.sin(angle)
            fig.add_trace(go.Scatter3d(x=[v[0] for v in coords], y=[v[1] for v in coords], z=[v[2] for v in coords], mode='lines', line=dict(color='#dce8e0',width=1), hoverinfo='skip', showlegend=False))
    for e in edges:
        a,b = e['de'],e['vers']
        if a not in points or b not in points: continue
        start,end = points[a],points[b]
        color = '#28745c' if e['signe'] > 0 else '#a34242'
        sign = '+' if e['signe'] > 0 else '−'
        opacity = 1 if not loop or (a,b) in highlighted else .12
        tip = f"{m['noms'].get(a,a)} → {m['noms'].get(b,b)} ({sign})"
        kwargs = dict(x=[start[0],end[0]],y=[start[1],end[1]],mode='lines',line=dict(color=color,width=3 if (a,b) in highlighted else 1.5),opacity=opacity,hoverinfo='skip',showlegend=False)
        mid = tuple(.4*x+.6*y for x,y in zip(start,end))
        if spatial:
            fig.add_trace(go.Scatter3d(**kwargs,z=[start[2],end[2]]))
            delta = [end[k]-start[k] for k in range(3)]
            norm = math.sqrt(sum(v*v for v in delta)) or 1
            arrow = [end[k]-.09*delta[k]/norm for k in range(3)]
            fig.add_trace(go.Cone(x=[arrow[0]],y=[arrow[1]],z=[arrow[2]],u=[delta[0]/norm],v=[delta[1]/norm],w=[delta[2]/norm],sizemode='absolute',sizeref=.12,anchor='tip',colorscale=[[0,color],[1,color]],showscale=False,opacity=opacity,hoverinfo='skip'))
            fig.add_trace(go.Scatter3d(x=[mid[0]],y=[mid[1]],z=[mid[2]],mode='text',text=[sign],textfont=dict(color=color,size=14),hovertext=[tip],hoverinfo='text',showlegend=False,opacity=opacity))
        else:
            fig.add_trace(go.Scatter(**kwargs))
            fig.add_annotation(x=.94*end[0]+.06*start[0],y=.94*end[1]+.06*start[1],ax=.84*end[0]+.16*start[0],ay=.84*end[1]+.16*start[1],xref='x',yref='y',axref='x',ayref='y',text='',showarrow=True,arrowhead=2,arrowcolor=color,opacity=opacity)
            fig.add_trace(go.Scatter(x=[mid[0]],y=[mid[1]],mode='text',text=[sign],textfont=dict(color=color,size=14),hovertext=[tip],hoverinfo='text',showlegend=False,opacity=opacity))
    labels = ['<br>'.join(textwrap.wrap(m['noms'].get(n,n),22)) for n in ids]
    common=dict(x=[points[n][0] for n in ids],y=[points[n][1] for n in ids],mode='markers+text',text=labels,textposition='top center',textfont=dict(family='Georgia',size=12,color='#104b3b'),hovertext=[m['noms'].get(n,n) for n in ids],hoverinfo='text',marker=dict(size=[16 if n==centre else 9 for n in ids],color=['#104b3b' if n==centre else '#9cbbab' for n in ids],line=dict(color='white',width=1)),showlegend=False)
    fig.add_trace(go.Scatter3d(**common,z=[points[n][2] for n in ids]) if spatial else go.Scatter(**common))
    fig.update_layout(height=650,margin=dict(l=30,r=30,t=45,b=30),paper_bgcolor='white',plot_bgcolor='white',font=dict(family='Georgia',color='#104b3b'),showlegend=False)
    if spatial:
        axis=dict(visible=False)
        camera=dict(eye=dict(x=1.6,y=1.6,z=1.2))
        fig.update_layout(scene=dict(xaxis=axis,yaxis=axis,zaxis=axis,aspectmode='data',camera=camera,dragmode='orbit'),updatemenus=[dict(type='buttons',direction='right',x=0,y=1.1,buttons=[dict(label=label,method='relayout',args=[{'scene.camera':dict(eye=dict(x=v,y=v,z=v*.75))}]) for label,v in [('+',.8),('−',2.6),(tr(('Recentrer','Reset view','Centrar','Re santre')),1.6)]])])
    else:
        fig.update_layout(dragmode='pan',xaxis=dict(visible=False),yaxis=dict(visible=False,scaleanchor='x',scaleratio=1))
    return fig


def render(m,rang,edges,centre,positions,loop=None):
    spatial = st.radio(tr(('Vue du schéma','Diagram view','Vista del esquema','Vizyalizasyon dyagram')),['3D','2D'],horizontal=True,key='causal_graph_view') == '3D'
    st.caption(tr(('Molette ou pincement : zoom · Glisser : rotation en 3D, déplacement en 2D · Survoler : nom complet. La position en 3D est une disposition visuelle, pas une mesure. Les flèches et leurs signes restent ceux du modèle.', 'Scroll or pinch to zoom · Drag to rotate in 3D or pan in 2D · Hover for full names. The 3D position is a visual layout, not a measurement. Arrows and signs retain the model relationships.', 'Rueda o pellizco: zoom · Arrastrar: girar en 3D o desplazar en 2D · Pasar el cursor: nombre completo. La posición 3D es visual, no una medida. Se conservan las flechas y los signos del modelo.', 'Wou sourit oswa pense: zoum · Trennen: vire an 3D, deplase an 2D. Pozisyon 3D a se yon dispozisyon vizyèl, se pa yon mezi. Flèch ak siy yo rete menm jan nan modèl la.')))
    st.plotly_chart(figure(m,rang,edges,centre,positions,spatial,loop),use_container_width=True,key='causal_explore_'+str(spatial),config={'scrollZoom':True,'displayModeBar':True,'displaylogo':False,'toImageButtonOptions':{'format':'png','filename':'APRI-schema'}})
