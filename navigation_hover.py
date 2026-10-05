"""Desktop hover navigation; native popovers retain touch and keyboard behavior."""
import streamlit.components.v1 as components


def render():
    components.html("""<script>
const d=window.parent.document;
if(!d.__apriHoverNavigation){
 d.__apriHoverNavigation=true;
 let active=null,timer=null;
 const desktop=()=>window.parent.matchMedia('(min-width:1001px) and (hover:hover) and (pointer:fine)').matches;
 const trigger=t=>t.closest('.st-key-zone_nav [data-testid="stPopover"]>button');
 const panel=()=>d.querySelector('#stFloatingOverlayPortal [data-testid="stPopoverBody"]:has([class*="st-key-nav_"])');
 const cancel=()=>{clearTimeout(timer);timer=null;};
 d.addEventListener('pointerover',e=>{
  if(!desktop()||e.pointerType!=='mouse')return;
  const b=trigger(e.target),p=panel();
  if(p&&p.contains(e.target)){cancel();return;}
  if(!b||b.closest('[class*="st-key-navigation_language"]'))return;
  cancel();
  if(active!==b){if(active&&active.getAttribute('aria-expanded')==='true')active.click();active=b;}
  if(b.getAttribute('aria-expanded')!=='true')b.click();
 });
 d.addEventListener('pointerout',e=>{
  if(!desktop()||e.pointerType!=='mouse'||!active)return;
  const p=panel(),to=e.relatedTarget;
  if(to&&(active.contains(to)||(p&&p.contains(to))))return;
  if(!active.contains(e.target)&&!(p&&p.contains(e.target)))return;
  cancel();timer=setTimeout(()=>{
   const current=panel();
   if(active.matches(':hover')||(current&&current.matches(':hover')))return;
   if(current&&current.contains(d.activeElement)&&d.activeElement.matches(':focus-visible'))return;
   if(active.isConnected&&active.getAttribute('aria-expanded')==='true')active.click();
   active=null;
  },180);
 });
}
</script>""",height=0)
