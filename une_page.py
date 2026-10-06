"""APRI sur une seule page : les rubriques s'enchaînent et se lisent en défilant.

Le menu du haut ne change plus de page ; il fait défiler jusqu'à la rubrique.
Chaque rubrique est un fragment Streamlit : un réglage fait dans l'une ne
recalcule qu'elle.
"""
import base64
import html
import json
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

ORDRE = ["portail", "accueil", "methodologie", "dimensions", "boucles",
         "actions", "donnees", "apropos", "contact"]
CLE_CIBLE = "apri_defiler_vers"


def actif(mode):
    return mode in ORDRE


def demander_defilement(page):
    """Le prochain affichage amènera la rubrique `page` en haut de l'écran."""
    st.session_state[CLE_CIBLE] = page


@st.fragment
def _rubrique(rendre_section, mode):
    rendre_section(mode)


@st.cache_data(show_spinner=False)
def _fond_b64():
    chemin = Path(__file__).parent / "data" / "fond_apri.jpg"
    try:
        return base64.b64encode(chemin.read_bytes()).decode()
    except OSError:
        return ""


def rendre(rendre_section, libelles=None):
    libelles = libelles or {}
    for mode in ORDRE:
        with st.container(key=f"sec_{mode}"):
            st.markdown(f'<div id="apri-sec-{mode}" class="apri-ancre"></div>',
                        unsafe_allow_html=True)
            if mode == "portail":
                _rubrique(rendre_section, mode)
                continue
            # LE TITRE SE POSE SUR LA PHOTO, le contenu sur une carte claire.
            st.markdown(f'<div class="apri-sec-titre">{html.escape(libelles.get(mode, ""))}</div>',
                        unsafe_allow_html=True)
            with st.container(key=f"carte_{mode}"):
                _rubrique(rendre_section, mode)
    _styles()
    _script(libelles)


def _styles():
    r = "#root " + ".stApp" * 100
    css = f"""
    {r} .apri-ancre{{scroll-margin-top:78px;height:0;}}
    /* L'ACCUEIL N'EST PLUS UN ÉCRAN FIXE : il devient la première rubrique. */
    {r} .st-key-zone_page .st-key-photo_home_hero{{position:relative!important;inset:auto!important;width:auto!important;height:100svh!important;min-height:100svh!important;z-index:auto!important;}}
    /* LA BARRE DU HAUT RESTE COLLÉE ET SOMBRE PARTOUT. */
    {r} div[data-testid='stColumn']:has(.st-key-zone_nav){{position:sticky!important;top:0!important;z-index:999!important;background:rgba(10,34,46,.28)!important;backdrop-filter:blur(14px) saturate(140%);-webkit-backdrop-filter:blur(14px) saturate(140%);border-bottom:1px solid rgba(255,255,255,.14)!important;}}
    {r} div[data-testid='stColumn']:has(.st-key-zone_nav) .st-key-zone_nav{{background:transparent!important;}}
    /* LA BARRE FLOTTE SUR LA PAGE : le contenu passe dessous, la photo aussi. */
    @media(min-width:1001px){{
     {r} div[data-testid='stColumn']:has(.st-key-zone_nav){{margin-bottom:-71px!important;}}
     {r} .st-key-zone_page [class*='st-key-sec_']:not(.st-key-sec_portail){{padding-top:115px!important;}}
    }}
    {r} .st-key-zone_nav button p,{r} .st-key-zone_nav button span{{color:white!important;}}
    {r} .st-key-zone_nav button[kind='primary']{{background:transparent!important;background-color:transparent!important;box-shadow:none!important;}}
    /* Le titre de chaque rubrique se voit en défilant. */
    {r} .st-key-zone_page [class*='st-key-sec_'] h1.apri-page-title,
    {r} .st-key-zone_page [class*='st-key-sec_'] h1.apri-page-title span{{font-size:26px!important;font-weight:650!important;color:#123746!important;line-height:1.25!important;}}
    {r} .st-key-zone_page [class*='st-key-sec_'] h1.apri-page-title{{margin:4px 0 10px!important;text-align:left!important;}}
    {r} .st-key-zone_page [class*='st-key-sec_'] h1.apri-page-title span{{text-align:left!important;}}
    /* La carte ne déborde jamais sur la rubrique suivante. */
    {r} .st-key-zone_page .st-key-sec_accueil{{overflow:hidden!important;}}
    {r} .st-key-zone_nav .apri-actif button{{background:#397FA3!important;}}
    /* Les rubriques se suivent sur le fond clair des pages intérieures. */
    {r} [data-testid='stAppViewContainer'],{r} [data-testid='stMain'],
    {r} div[data-testid='stColumn']:has(.st-key-zone_page),{r} [data-testid='stMainBlockContainer']{{background:#eef3f6!important;}}
    {r} .st-key-zone_page > div > [data-testid='stLayoutWrapper']:has(> [class*='st-key-sec_']){{margin:0!important;}}
    {r} .st-key-zone_page{{background:#eef3f6!important;}}
    {r} .st-key-zone_page [class*='st-key-sec_']:not(.st-key-sec_portail){{background:#eef3f6!important;padding:28px 36px 40px!important;border-top:1px solid #d5e0e6;box-sizing:border-box!important;}}
    {r} .st-key-zone_page .st-key-sec_portail{{background:#173e4c!important;}}
    /* LA PHOTO DE L'ACCUEIL RESTE EN FOND, fixe, sous un voile bleu nuit. */
    {r} [data-testid='stAppViewContainer']{{background:linear-gradient(rgba(10,34,46,.66),rgba(10,34,46,.66)),url('data:image/jpeg;base64,__FOND__') center/cover fixed #173e4c!important;}}
    {r} [data-testid='stMain'],{r} [data-testid='stMainBlockContainer'],
    {r} div[data-testid='stColumn']:has(.st-key-zone_page),{r} .st-key-zone_page{{background:transparent!important;}}
    {r} .st-key-zone_page [class*='st-key-sec_']:not(.st-key-sec_portail){{background:transparent!important;border-top:0!important;padding:44px 56px 56px!important;}}
    {r} .apri-sec-titre{{font:650 30px/1.2 Inter,Arial,sans-serif!important;color:#fff!important;letter-spacing:.2px;margin:0 0 6px;text-shadow:0 2px 14px rgba(0,0,0,.35);}}
    {r} .st-key-zone_page [class*='st-key-carte_']{{background:rgba(255,255,255,.93)!important;backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);border-radius:16px!important;padding:24px 28px!important;box-shadow:0 18px 50px rgba(0,0,0,.28)!important;box-sizing:border-box!important;}}
    {r} .st-key-zone_page .st-key-carte_accueil{{padding:10px!important;overflow:hidden!important;}}
    {r} .st-key-zone_page [class*='st-key-carte_'] [data-testid='stElementContainer']:has(.apri-page-heading){{display:none!important;}}
    {r} .st-key-zone_page .st-key-pied_page{{background:rgba(255,255,255,.93)!important;border-radius:16px!important;margin:0 56px 48px!important;padding:14px 22px!important;width:auto!important;box-sizing:border-box!important;}}
    {r} .st-key-zone_page .st-key-pied_page [data-testid='stExpander'] details{{background:transparent!important;}}
    /* PAGE PAR PAGE : chaque rubrique occupe au moins un écran sous la barre. */
    @media(min-width:1001px){{
     {r} .st-key-zone_page [class*='st-key-sec_']:not(.st-key-sec_portail){{min-height:100dvh!important;}}
     {r} .st-key-zone_page .st-key-sec_portail .st-key-photo_home_hero{{height:100dvh!important;min-height:100dvh!important;}}
    }}
    """
    st.markdown("<style>" + css.replace("__FOND__", _fond_b64()) + "</style>", unsafe_allow_html=True)


def _script(libelles):
    cible = st.session_state.pop(CLE_CIBLE, None)
    nonce = st.session_state.get("_apri_defil_n", 0) + 1
    st.session_state["_apri_defil_n"] = nonce
    js = """
const w=window.parent,d=w.document,ordre=__ORDRE__,cible=__CIBLE__;
// Hauteur de ce qui couvre le haut de l'écran. La barre flottante (marge
// négative) ne compte pas : les rubriques glissent dessous.
function hautBarre(){let b=0;d.querySelectorAll('div[data-testid="stColumn"]:has(.st-key-zone_nav),.st-key-menu_mobile').forEach(h=>{const r=h.getBoundingClientRect();if(r.height>0&&r.top<5&&parseFloat(w.getComputedStyle(h).marginBottom)>=0)b=Math.max(b,r.bottom);});return b;}
// Le menu suit la lecture : la rubrique qui occupe le haut de l'écran s'allume.
const navs={};
ordre.forEach(m=>{navs[m]=d.querySelector('.st-key-nav_'+m)||d.querySelector('.st-key-top_menu_'+m);});
if(d.__apriSpy)d.__apriSpy.disconnect();
const visibles=new Map();
d.__apriSpy=new w.IntersectionObserver(es=>{
 es.forEach(e=>visibles.set(e.target.dataset.m,e.isIntersecting?e.boundingClientRect.top:null));
 let best=null,bt=1e9;
 ordre.forEach(m=>{const t=visibles.get(m);if(t!==null&&t!==undefined&&Math.abs(t)<bt){bt=Math.abs(t);best=m;}});
 if(!best)return;
 ordre.forEach(m=>{const n=d.querySelector('.st-key-nav_'+m)||d.querySelector('.st-key-top_menu_'+m);if(n)n.classList.toggle('apri-actif',m===best);});
},{rootMargin:'-80px 0px -55% 0px'});
ordre.forEach(m=>{const s=d.querySelector('.st-key-sec_'+m);if(s){s.dataset.m=m;d.__apriSpy.observe(s);}});
if(cible){
 let n=0,attendu=null;
 const sc=d.querySelector('[data-testid="stAppViewContainer"]');
 const aller=()=>{
  const a=d.querySelector('.st-key-sec_'+cible);
  if(!a||!sc)return;
  // Le lecteur a bougé la page lui-même (molette, tactile, même au-dessus
  // d'une carte ou d'un schéma) : on le laisse faire.
  if(attendu!==null&&Math.abs(sc.scrollTop-attendu)>40)return;
  let bas=0;
  bas=hautBarre();
  const dy=a.getBoundingClientRect().top-bas;
  if(Math.abs(dy)>2)sc.scrollTop=sc.scrollTop+dy;
  attendu=sc.scrollTop;
  // Les rubriques du dessus finissent de se dessiner : on recale quelques fois.
  if(n++<8)w.setTimeout(aller,n<3?400:800);
 };
 w.setTimeout(aller,250);
}

// ---------------------------------------------------------------- page par page
// Un coup de molette = une rubrique. Une rubrique plus haute que l'écran se lit
// d'abord normalement jusqu'à son bas ; le coup suivant passe à la suivante.
const sc=d.querySelector('[data-testid="stAppViewContainer"]');
if(d.__apriSnapOff)d.__apriSnapOff();
const large=()=>w.matchMedia('(min-width:1001px) and (pointer:fine)').matches;
const reduit=()=>w.matchMedia('(prefers-reduced-motion:reduce)').matches;
const haut=hautBarre;
const rubriques=()=>ordre.map(m=>d.querySelector('.st-key-sec_'+m)).filter(Boolean);
const courante=()=>{const hb=haut();let k=0;rubriques().forEach((s,i)=>{if(s.getBoundingClientRect().top<=hb+6)k=i;});return k;};
let anim=false,calme=0,frame=null;
const glisser=(dy,ms)=>{
 if(!sc)return;
 if(frame)w.cancelAnimationFrame(frame);
 const de=sc.scrollTop,t0=w.performance.now(),dur=reduit()?1:ms;
 anim=true;
 const pas=t=>{const k=Math.min(1,(t-t0)/dur),e=k<.5?4*k*k*k:1-Math.pow(-2*k+2,3)/2;
  sc.scrollTop=de+dy*e;
  if(k<1)frame=w.requestAnimationFrame(pas);else{anim=false;frame=null;calme=Date.now()+260;}};
 frame=w.requestAnimationFrame(pas);
};
const allerA=(i,fin)=>{
 const l=rubriques();if(i<0||i>=l.length)return;
 const s=l[i],r=s.getBoundingClientRect(),hb=haut(),vh=w.innerHeight;
 // En remontant vers une rubrique plus haute que l'écran, on arrive sur son bas.
 const dy=(fin&&r.height>vh-hb)?r.bottom-vh:r.top-hb;
 glisser(dy,720);
 d.__apriPoints&&d.__apriPoints(i);
};
d.__apriAllerA=allerA;
const exclus='input,textarea,select,[role="combobox"],[role="listbox"],[role="dialog"],[data-testid="stPopoverBody"],.maplibregl-map,.leaflet-container,.js-plotly-plot,canvas,.st-key-zone_nav';
const molette=e=>{
 if(!large()||e.ctrlKey||e.metaKey||Math.abs(e.deltaX)>Math.abs(e.deltaY))return;
 if(e.target.closest&&e.target.closest(exclus))return;
 const now=Date.now();
 // Pendant le glissé, et tant que l'inertie du pavé tactile continue, on absorbe.
 if(anim||now<calme){e.preventDefault();if(!anim)calme=now+160;return;}
 const dir=Math.sign(e.deltaY);if(!dir)return;
 const l=rubriques(),i=courante(),s=l[i];if(!s)return;
 const r=s.getBoundingClientRect(),hb=haut(),vh=w.innerHeight;
 const px=Math.abs(e.deltaY)*(e.deltaMode===1?16:e.deltaMode===2?vh:1);
 if(dir>0){
  const reste=r.bottom-vh;
  if(reste>60){if(reste<=px){e.preventDefault();sc.scrollTop+=reste;calme=now+200;}return;}
  if(i+1<l.length){e.preventDefault();allerA(i+1,false);}
 }else{
  const reste=hb-r.top;
  if(reste>60){if(reste<=px){e.preventDefault();sc.scrollTop-=reste;calme=now+200;}return;}
  if(i>0){e.preventDefault();allerA(i-1,true);}
 }
};
const clavier=e=>{
 if(!large()||e.target.closest&&e.target.closest('input,textarea,select,[role="combobox"],[contenteditable]'))return;
 if(e.key!=='PageDown'&&e.key!=='PageUp')return;
 e.preventDefault();const i=courante();allerA(e.key==='PageDown'?i+1:i-1,e.key==='PageUp');
};
d.addEventListener('wheel',molette,{passive:false,capture:true});
d.addEventListener('keydown',clavier,true);
// Les points à droite : un par rubrique, celui de la rubrique lue est plein.
let pts=d.getElementById('apri-points');if(pts)pts.remove();
pts=d.createElement('nav');pts.id='apri-points';pts.setAttribute('aria-label','Sections');
ordre.forEach((m,i)=>{const b=d.createElement('button');b.type='button';b.dataset.i=i;b.setAttribute('aria-label',libelles[m]||m);b.innerHTML='<span>'+(libelles[m]||m)+'</span>';b.addEventListener('click',()=>allerA(i,false));pts.appendChild(b);});
d.body.appendChild(pts);
d.__apriPoints=k=>pts.querySelectorAll('button').forEach((b,i)=>b.classList.toggle('on',i===k));
const suivre=()=>{if(!anim)d.__apriPoints(courante());};
sc&&sc.addEventListener('scroll',suivre,{passive:true});suivre();
if(!d.getElementById('apri-points-style')){const st=d.createElement('style');st.id='apri-points-style';st.textContent=`
#apri-points{position:fixed;right:18px;top:50%;transform:translateY(-50%);z-index:1001;display:flex;flex-direction:column;gap:12px;}
#apri-points button{position:relative;width:11px;height:11px;padding:0;border-radius:50%;border:1.5px solid #397FA3;background:rgba(255,255,255,.75);cursor:pointer;transition:transform .2s,background .2s;}
#apri-points button.on{background:#397FA3;transform:scale(1.3);}
#apri-points button:hover{transform:scale(1.3);}
#apri-points button span{position:absolute;right:20px;top:50%;transform:translateY(-50%);white-space:nowrap;font:500 12px/1 Inter,Arial,sans-serif;color:#fff;background:#123746;padding:5px 9px;border-radius:6px;opacity:0;pointer-events:none;transition:opacity .15s;}
#apri-points button:hover span,#apri-points button:focus-visible span{opacity:1;}
@media(max-width:1000px),(pointer:coarse){#apri-points{display:none;}}`;d.head.appendChild(st);}
d.__apriSnapOff=()=>{d.removeEventListener('wheel',molette,true);d.removeEventListener('keydown',clavier,true);sc&&sc.removeEventListener('scroll',suivre);};
"""
    js = js.replace("__ORDRE__", json.dumps(ORDRE)).replace("__CIBLE__", json.dumps(cible))
    js = js.replace("const w=window.parent,d=w.document,", "const libelles=" + json.dumps(libelles, ensure_ascii=False) + ";\nconst w=window.parent,d=w.document,")
    components.html(f"<script>/*{nonce}*/{js}</script>", height=0)
