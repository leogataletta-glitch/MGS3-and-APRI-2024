"""Conservative wheel navigation between main sections."""
import json
import streamlit as st
import streamlit.components.v1 as components
from apri_logo_refined import LOGO


def identity(unep):
    return '<div class="apri-new-identity"><span class="apri-color-mark"><img alt="APRI" src="data:image/png;base64,' + LOGO + '"><img class="apri-white-word" aria-hidden="true" alt="" src="data:image/png;base64,' + LOGO + '"></span><img alt="UN Environment Programme" src="data:image/png;base64,' + unep + '"></div>'


def render(current, order, go):
    root = '#root ' + '.stApp' * 90
    st.markdown('<style>' + root + ''' .apri-new-identity{display:flex;align-items:center;gap:18px;height:52px;}
    ''' + root + ''' .apri-new-identity img{height:52px;width:auto;object-fit:contain;filter:none;background:transparent;}
    ''' + root + ''' .apri-new-identity>img{height:38px;}
    ''' + root + ''' .apri-color-mark{position:relative;display:block;width:52px;height:52px;}
    ''' + root + ''' .apri-color-mark img{position:absolute;inset:0;width:52px;height:52px;}
    ''' + root + ''' .apri-color-mark .apri-white-word{clip-path:inset(78% 0 0 0);filter:brightness(0) invert(1);}
    ''' + root + ''' .st-key-zone_nav>div:has(.apri-new-identity){margin-right:auto!important;}
    ''' + root + ''' [data-testid="stColumn"]:has(.st-key-zone_nav){position:sticky!important;top:0!important;z-index:999!important;}
    .st-key-wheel_previous,.st-key-wheel_next{display:none!important;}
    </style>''', unsafe_allow_html=True)
    if current not in order:
        return
    index = order.index(current)
    for key, offset in [('previous', -1), ('next', 1)]:
        target = index + offset
        st.button(key, key='wheel_' + key, disabled=not 0 <= target < len(order),
                  on_click=go, args=(order[target] if 0 <= target < len(order) else current,))
    components.html('<script>const page=' + json.dumps(current) + ';' + SCRIPT + '</script>', height=0)


SCRIPT = r'''
const w=window.parent,d=w.document;
if(d.__apriWheelCleanup)d.__apriWheelCleanup();
if(d.__apriWheelPage!==page){
 d.__apriWheelPage=page;
 d.querySelectorAll('[data-testid="stAppViewContainer"],[data-testid="stMain"]').forEach(n=>n.scrollTop=0);
 if(d.scrollingElement)d.scrollingElement.scrollTop=0;
}
let direction=0,total=0,count=0,last=0,edgeSince=0,locked=false;
const start=Date.now();
const reset=()=>{total=0;count=0;edgeSince=0;};
const handler=e=>{
 if(locked||Date.now()-start<1800||e.ctrlKey||e.metaKey||Math.abs(e.deltaX)>Math.abs(e.deltaY))return;
 if(!w.matchMedia('(min-width:1001px) and (pointer:fine)').matches)return;
 const t=e.target;
 if(t.closest('input,textarea,select,button,[role="combobox"],[role="listbox"],[role="dialog"],[data-testid="stPopoverBody"],.st-key-zone_nav,.maplibregl-map,.leaflet-container,.js-plotly-plot,canvas,iframe')){reset();return;}
 let node=t,scroller=null;
 while(node&&node!==d.documentElement){
  const style=w.getComputedStyle(node);
  if(/auto|scroll/.test(style.overflowY)&&node.scrollHeight>node.clientHeight+4){scroller=node;break;}
  node=node.parentElement;
 }
 scroller=scroller||d.scrollingElement;
 if(scroller!==d.scrollingElement&&!scroller.matches('[data-testid="stAppViewContainer"],[data-testid="stMain"]')){reset();return;}
 const dir=Math.sign(e.deltaY),now=Date.now();
 if(!dir)return;
 const edge=dir>0?scroller.scrollTop+scroller.clientHeight>=scroller.scrollHeight-3:scroller.scrollTop<=3;
 if(!edge){reset();return;}
 if(dir!==direction||now-last>550){reset();direction=dir;}
 last=now;
 if(!edgeSince){edgeSince=now;return;}
 // Require sustained intent at an edge; do not cancel ordinary scrolling.
 count++;total+=Math.min(Math.abs(e.deltaY)*(e.deltaMode===1?16:1),120);
 if(now-edgeSince<700||count<7||total<700)return;
 const b=d.querySelector('.st-key-wheel_'+(dir>0?'next':'previous')+' button');
 if(b&&!b.disabled){locked=true;b.click();}else reset();
};
d.addEventListener('wheel',handler,{passive:true});
d.__apriWheelCleanup=()=>d.removeEventListener('wheel',handler);
'''
