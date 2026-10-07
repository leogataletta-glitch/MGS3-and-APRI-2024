import sys,os,json
sys.path.insert(0,'/tmp/work'); os.chdir('/tmp/work')
import streamlit as st
lang=sys.argv[1]
import i18n
try: i18n.set_lang(lang)
except Exception as e: print('set_lang',e)
st.session_state['lang']=lang
print('lang',i18n.get_lang())
import carte_localisation as cl
d=cl._couches()
# privacy: no household-level points online. Round to ~1 km grid, drop ids, dedupe.
seen=set(); pts=[]
for e in d.get('entretiens',[]):
    k=(round(e[0],2),round(e[1],2),e[2],e[3])
    if k in seen: continue
    seen.add(k); pts.append([k[0],k[1],e[2],e[3],''])
print('points',len(d.get('entretiens',[])),'->',len(pts))
d['entretiens']=pts
h=cl._locale_html(cl.html(d))
open(sys.argv[2],'w').write(h); print(len(h))
