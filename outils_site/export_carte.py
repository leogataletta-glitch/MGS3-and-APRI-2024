import sys,os,json,math,random
sys.path.insert(0,'/tmp/work'); os.chdir('/tmp/work')
import streamlit as st
lang=sys.argv[1]; st.session_state['lang']=lang
import carte_localisation as cl
d=cl._couches()
# One point per household, as before, but displaced at random by 150 to 400 m
# (fixed seed), staying inside its communal section when the original was:
# the map looks the same, no published point is a real household location.
def dedans(x,y,anneau):
    c=False; n=len(anneau)
    for i in range(n):
        x1,y1=anneau[i]; x2,y2=anneau[(i+1)%n]
        if (y1>y)!=(y2>y) and x < (x2-x1)*(y-y1)/(y2-y1)+x1: c=not c
    return c
poly={}
for s in d['sections']: poly.setdefault(s['p']['section'],[]).extend(s['a'])
def dans_section(x,y,sec): return any(dedans(x,y,r) for r in poly.get(sec,[]))
rng=random.Random(2024)
pts=[]
for e in d['entretiens']:
    x,y,sec=e[0],e[1],e[2]; garde=dans_section(x,y,sec); ok=None
    for _ in range(40):
        dist=rng.uniform(150,400); ang=rng.uniform(0,2*math.pi)
        nx=x+dist*math.cos(ang)/(111320*math.cos(math.radians(y))); ny=y+dist*math.sin(ang)/110540
        if not garde or dans_section(nx,ny,sec): ok=(nx,ny); break
    if ok is None: ok=(round(x,2),round(y,2))
    pts.append([round(ok[0],4),round(ok[1],4),sec,e[3],''])
print('points',len(pts))
d['entretiens']=pts
h=cl._locale_html(cl.html(d))
a="  if(frame){\n   const parentWindow=window.parent,main"
assert a in h; h=h.replace(a,"  if(frame&&!frame.hasAttribute('data-statique')){\n   const parentWindow=window.parent,main")
b="'<b>n° '+(e[4]||'')+'</b><br>'"
assert b in h; h=h.replace(b,"(e[4]?'<b>n° '+e[4]+'</b><br>':'')")
open(sys.argv[2],'w').write(h); print(len(h))
