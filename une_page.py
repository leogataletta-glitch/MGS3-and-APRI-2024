"""APRI sur une seule page : les rubriques s'enchaînent et se lisent en défilant.

Le menu du haut ne change plus de page ; il fait défiler jusqu'à la rubrique.
Chaque rubrique est un fragment Streamlit : un réglage fait dans l'une ne
recalcule qu'elle.
"""
import json
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


def rendre(rendre_section):
    for mode in ORDRE:
        with st.container(key=f"sec_{mode}"):
            st.markdown(f'<div id="apri-sec-{mode}" class="apri-ancre"></div>',
                        unsafe_allow_html=True)
            _rubrique(rendre_section, mode)
    _styles()
    _script()


def _styles():
    r = "#root " + ".stApp" * 100
    css = f"""
    {r} .apri-ancre{{scroll-margin-top:78px;height:0;}}
    /* L'ACCUEIL N'EST PLUS UN ÉCRAN FIXE : il devient la première rubrique. */
    {r} .st-key-zone_page .st-key-photo_home_hero{{position:relative!important;inset:auto!important;width:auto!important;height:100svh!important;min-height:100svh!important;z-index:auto!important;}}
    /* LA BARRE DU HAUT RESTE COLLÉE ET SOMBRE PARTOUT. */
    {r} div[data-testid='stColumn']:has(.st-key-zone_nav){{position:sticky!important;top:0!important;z-index:999!important;background:#123746!important;}}
    {r} .st-key-zone_nav button p,{r} .st-key-zone_nav button span{{color:white!important;}}
    {r} .st-key-zone_nav button[kind='primary']{{background:transparent!important;background-color:transparent!important;box-shadow:none!important;}}
    /* Le titre de chaque rubrique se voit en défilant. */
    {r} .st-key-zone_page [class*='st-key-sec_'] h1.apri-page-title,
    {r} .st-key-zone_page [class*='st-key-sec_'] h1.apri-page-title span{{font-size:26px!important;font-weight:650!important;color:#123746!important;line-height:1.25!important;}}
    {r} .st-key-zone_page [class*='st-key-sec_'] h1.apri-page-title{{margin:4px 0 10px!important;text-align:left!important;}}
    {r} .st-key-zone_page [class*='st-key-sec_'] h1.apri-page-title span{{text-align:left!important;}}
    {r} .st-key-zone_page [class*='st-key-sec_'] [data-testid='stElementContainer']:has(.apri-page-heading){{display:block!important;}}
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
    """
    st.markdown("<style>" + css + "</style>", unsafe_allow_html=True)


def _script():
    cible = st.session_state.pop(CLE_CIBLE, None)
    nonce = st.session_state.get("_apri_defil_n", 0) + 1
    st.session_state["_apri_defil_n"] = nonce
    js = """
const w=window.parent,d=w.document,ordre=__ORDRE__,cible=__CIBLE__;
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
 let n=0;
 const aller=()=>{
  const a=d.querySelector('.st-key-sec_'+cible);
  const sc=d.querySelector('[data-testid="stAppViewContainer"]');
  if(a&&sc){
   // Sous la barre du haut (ou le menu mobile), jamais derrière.
   let bas=0;
   d.querySelectorAll('div[data-testid="stColumn"]:has(.st-key-zone_nav),.st-key-menu_mobile').forEach(h=>{const r=h.getBoundingClientRect();if(r.height>0&&r.top<5)bas=Math.max(bas,r.bottom);});
   const dy=a.getBoundingClientRect().top-bas;
   if(Math.abs(dy)>2)sc.scrollBy({top:dy,behavior:n>0?'auto':'smooth'});
  }
  if(n++<12)w.setTimeout(aller,n<3?400:900);
 };
 // Les rubriques du dessus finissent de se dessiner : on recale quelques fois.
 w.setTimeout(aller,250);
 const stop=()=>{n=99;};
 d.addEventListener('wheel',stop,{once:true,passive:true});
 d.addEventListener('touchstart',stop,{once:true,passive:true});
}
"""
    js = js.replace("__ORDRE__", json.dumps(ORDRE)).replace("__CIBLE__", json.dumps(cible))
    components.html(f"<script>/*{nonce}*/{js}</script>", height=0)
