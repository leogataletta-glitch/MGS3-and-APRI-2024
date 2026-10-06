"""Conservative wheel navigation between main sections."""
import json
import streamlit as st
import streamlit.components.v1 as components
from apri_logo_refined import LOGO


def identity(unep):
    """Une seule signature : le symbole APRI, son nom, un filet, puis le PNUE.

    LES DEUX LOGOS NE SE CONCURRENCENT PLUS. Ils étaient posés côte à côte, à
    des hauteurs et des styles différents. Le symbole APRI (sans le mot, déjà
    écrit à côté) et le logo du PNUE sont maintenant alignés sur la même
    hauteur et séparés par un filet fin, comme une signature institutionnelle.
    """
    from apri_marque import MARQUE
    from publication_web import tr
    sous = tr(("Observatoire de la résilience", "Resilience Observatory",
               "Observatorio de la resiliencia", "Obsèvatwa rezilyans"))
    return ('<div class="apri-lockup">'
            '<img class="apri-lockup-mark" alt="" src="data:image/png;base64,' + MARQUE + '">'
            '<span class="apri-lockup-txt"><span class="apri-lockup-nom">APRI</span>'
            '<span class="apri-lockup-sous">' + sous + '</span></span>'
            '<span class="apri-lockup-filet" aria-hidden="true"></span>'
            '<img class="apri-lockup-unep" alt="UN Environment Programme" src="data:image/png;base64,' + unep + '">'
            '</div>')


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
    ''' + root + ''' .st-key-zone_nav>div:has(.apri-lockup){margin-right:auto!important;}
    ''' + root + ''' .apri-lockup{display:flex;align-items:center;gap:12px;height:52px;position:relative;top:-6px;}
    ''' + root + ''' .apri-lockup img{filter:none!important;background:transparent!important;object-fit:contain;}
    ''' + root + ''' .apri-lockup .apri-lockup-mark{height:38px!important;width:auto!important;}
    ''' + root + ''' .apri-lockup-txt{display:flex;flex-direction:column;justify-content:center;line-height:1;}
    ''' + root + ''' .apri-lockup-nom{font:700 19px/1 Inter,Arial,sans-serif!important;letter-spacing:2.5px;color:#fff!important;}
    ''' + root + ''' .apri-lockup-sous{font:400 10.5px/1.2 Inter,Arial,sans-serif!important;letter-spacing:.4px;color:rgba(255,255,255,.78)!important;margin-top:4px;white-space:nowrap;}
    ''' + root + ''' .apri-lockup-filet{width:1px;height:34px;background:rgba(255,255,255,.35);margin:0 6px;}
    ''' + root + ''' .apri-lockup .apri-lockup-unep{height:36px!important;width:auto!important;opacity:.92;}
    @media(max-width:1180px){''' + root + ''' .apri-lockup-sous{display:none;}}
    </style>''', unsafe_allow_html=True)
    header = '#root ' + '.stApp' * 95
    st.markdown('<style>' + header + " [data-testid='stColumn']:has(.st-key-zone_nav){background:#123746!important;border-bottom:1px solid #ffffff22!important;}" + header + " .st-key-zone_nav{background:transparent!important;}" + header + " .st-key-zone_nav button{background:transparent!important;color:white!important;}" + header + " .st-key-zone_nav button[kind='primary']{background:#397FA3!important;}" + '</style>', unsafe_allow_html=True)
    if current not in order:
        return
    st.markdown('<style>@keyframes apri_reveal_' + current + '{from{opacity:0}to{opacity:1}} .st-key-zone_page{animation:apri_reveal_' + current + ' .45s ease-out;} @media(prefers-reduced-motion:reduce){.st-key-zone_page{animation:none!important}}</style>', unsafe_allow_html=True)
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
 if(d.__apriOutgoing){d.__apriOutgoing.cancel();d.__apriOutgoing=null;}
 d.querySelectorAll('[data-testid="stAppViewContainer"],[data-testid="stMain"]').forEach(n=>n.scrollTop=0);
 if(d.scrollingElement)d.scrollingElement.scrollTop=0;
}
let direction=0,total=0,count=0,last=0,edgeSince=0,locked=false;
const start=Date.now();
const reset=()=>{total=0;count=0;edgeSince=0;};
const handler=e=>{
 if(locked||Date.now()-start<900||e.ctrlKey||e.metaKey||Math.abs(e.deltaX)>Math.abs(e.deltaY))return;
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
 if(scroller!==d.scrollingElement&&!scroller.matches('[data-testid="stAppViewContainer"],[data-testid="stMain"]')&&!scroller.querySelector('.st-key-zone_page')){reset();return;}
 const dir=Math.sign(e.deltaY),now=Date.now();
 if(!dir)return;
 const edge=e.fromMap||page==='portail'||(dir>0?scroller.scrollTop+scroller.clientHeight>=scroller.scrollHeight-6:scroller.scrollTop<=6);
 if(!edge){reset();return;}
 if(dir!==direction||now-last>900){reset();direction=dir;}
 last=now;
 if(!edgeSince)edgeSince=now;
 // Require sustained intent at an edge; do not cancel ordinary scrolling.
 count++;total+=Math.min(Math.abs(e.deltaY)*(e.deltaMode===1?16:1),120);
 if(count<2||total<180)return;
 const b=d.querySelector('.st-key-wheel_'+(dir>0?'next':'previous')+' button');
 if(b&&!b.disabled){
  locked=true;
  const content=d.querySelector('.st-key-zone_page');
  if(content&&!w.matchMedia('(prefers-reduced-motion:reduce)').matches)d.__apriOutgoing=content.animate([{opacity:1},{opacity:0}],{duration:220,easing:'ease-in',fill:'forwards'});
  w.setTimeout(()=>b.click(),220);
 }else reset();
};
d.addEventListener('wheel',handler,{passive:true,capture:true});
const receive=e=>{
 if(e.data?.type!=='apri-map-wheel'||page!=='accueil')return;
 const frame=Array.from(d.querySelectorAll('.st-key-zone_page iframe')).find(f=>f.contentWindow===e.source);
 if(!frame||!Number.isFinite(e.data.dy)||!Number.isFinite(e.data.dx))return;
 handler({target:frame.parentElement,deltaY:e.data.dy,deltaX:e.data.dx,deltaMode:e.data.mode,fromMap:true});
};
w.addEventListener('message',receive);
// Embedded explanatory content must also hand off scrolling at its own edges.
const bridges=new Map();
const connect=()=>d.querySelectorAll('.st-key-zone_page iframe').forEach(frame=>{
 try{
  const fd=frame.contentDocument;
  if(!fd||fd.querySelector('#carte')||bridges.get(frame)?.doc===fd)return;
  const fn=e=>{
   if(e.ctrlKey||e.metaKey||e.target.closest('input,textarea,select,button,[role="combobox"],canvas'))return;
   let n=e.target;
   while(n&&n!==fd.documentElement){
    if(/auto|scroll/.test(frame.contentWindow.getComputedStyle(n).overflowY)&&n.scrollHeight>n.clientHeight+4){
     if(e.deltaY>0?n.scrollTop+n.clientHeight<n.scrollHeight-4:n.scrollTop>4)return;
    }n=n.parentElement;
   }
   const inner=fd.scrollingElement;
   if(inner&&(e.deltaY>0?inner.scrollTop+inner.clientHeight<inner.scrollHeight-4:inner.scrollTop>4))return;
   const outer=d.querySelector('[data-testid="stAppViewContainer"]');
   if(outer&&(e.deltaY>0?outer.scrollTop+outer.clientHeight<outer.scrollHeight-6:outer.scrollTop>6))outer.scrollTop+=e.deltaY;
   else handler({target:frame.parentElement,deltaY:e.deltaY,deltaX:e.deltaX,deltaMode:e.deltaMode});
  };
  fd.addEventListener('wheel',fn,{passive:true,capture:true});bridges.set(frame,{doc:fd,fn});
 }catch(error){/* Cross-origin documents retain native scrolling. */}
});
const bridgeTimer=w.setInterval(connect,800);connect();
d.__apriWheelCleanup=()=>{d.removeEventListener('wheel',handler,true);w.removeEventListener('message',receive);w.clearInterval(bridgeTimer);bridges.forEach(({doc,fn})=>doc.removeEventListener('wheel',fn,true));};
'''
