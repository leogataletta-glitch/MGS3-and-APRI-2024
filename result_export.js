/* Export the visible Leaflet viewport; geographic scale and attribution are
   drawn into the image, so both remain present in JPEG and PDF. */
function pdfJpeg(canvas) {
  const jpeg=Uint8Array.from(atob(canvas.toDataURL('image/jpeg',.94).split(',')[1]),c=>c.charCodeAt(0));
  const enc=new TextEncoder(), chunks=[], offsets=[0];let length=0;
  const put=s=>{const b=typeof s==='string'?enc.encode(s):s;chunks.push(b);length+=b.length;};
  const w=842,h=842*canvas.height/canvas.width;
  put('%PDF-1.4\n');
  function obj(n,s){offsets[n]=length;put(n+' 0 obj\n'+s+'\nendobj\n');}
  obj(1,'<< /Type /Catalog /Pages 2 0 R >>');
  obj(2,'<< /Type /Pages /Kids [3 0 R] /Count 1 >>');
  obj(3,`<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${w} ${h}] /Resources << /XObject << /Im0 4 0 R >> >> /Contents 5 0 R >>`);
  offsets[4]=length;put(`4 0 obj\n<< /Type /XObject /Subtype /Image /Width ${canvas.width} /Height ${canvas.height} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ${jpeg.length} >>\nstream\n`);put(jpeg);put('\nendstream\nendobj\n');
  const stream=`q ${w} 0 0 ${h} 0 0 cm /Im0 Do Q`;
  obj(5,`<< /Length ${enc.encode(stream).length} >>\nstream\n${stream}\nendstream`);
  const xref=length;put('xref\n0 6\n0000000000 65535 f \n');
  offsets.slice(1).forEach(o=>put(String(o).padStart(10,'0')+' 00000 n \n'));
  put(`trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF`);
  return new Blob(chunks,{type:'application/pdf'});
}

(function(){
const P=window.parent,D=P.document,fr=__FR__;
if(P.__apriExportObserver)P.__apriExportObserver.disconnect();
const seen=new WeakSet();let pending=false;
function download(blob,ext){const url=URL.createObjectURL(blob),a=D.createElement('a');a.href=url;a.download='APRI-resultat.'+ext;a.click();setTimeout(()=>URL.revokeObjectURL(url),30000);}
async function capture(el){
  const doc=el.ownerDocument,win=doc.defaultView;
  const svg=el.matches('svg')?el:el.querySelector('svg');
  const source=el.matches('canvas')?el:el.querySelector('canvas');
  if(svg){
    const rect=svg.getBoundingClientRect(),clone=svg.cloneNode(true),orig=[svg,...svg.querySelectorAll('*')],copies=[clone,...clone.querySelectorAll('*')];
    orig.forEach((node,i)=>{const cs=win.getComputedStyle(node);['font-family','font-size','font-weight','font-style','fill','stroke','stroke-width','opacity','text-anchor','dominant-baseline'].forEach(k=>copies[i].style.setProperty(k,cs.getPropertyValue(k)));});
    clone.setAttribute('xmlns','http://www.w3.org/2000/svg');clone.setAttribute('width',rect.width);clone.setAttribute('height',rect.height);
    const url=URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(clone)],{type:'image/svg+xml;charset=utf-8'}));
    try{const img=new Image();await new Promise((r,j)=>{img.onload=r;img.onerror=j;img.src=url;});const c=D.createElement('canvas');c.width=Math.ceil(rect.width*2);c.height=Math.ceil(rect.height*2);const ctx=c.getContext('2d');ctx.fillStyle='white';ctx.fillRect(0,0,c.width,c.height);ctx.drawImage(img,0,0,c.width,c.height);return c;}finally{URL.revokeObjectURL(url);}
  }
  if(source){const c=D.createElement('canvas');c.width=source.width;c.height=source.height;const ctx=c.getContext('2d');ctx.fillStyle='white';ctx.fillRect(0,0,c.width,c.height);ctx.drawImage(source,0,0);return c;}
  if(el.matches('img')){const c=D.createElement('canvas');c.width=el.naturalWidth;c.height=el.naturalHeight;c.getContext('2d').drawImage(el,0,0);return c;}
  throw Error('No visual');
}
function toolbar(el,table=false){
 if(seen.has(el)||!el.parentNode||el.nextElementSibling?.classList.contains('apri-export-tools'))return;seen.add(el);
 const doc=el.ownerDocument,bar=doc.createElement('div');bar.className='apri-export-tools';bar.setAttribute('data-html2canvas-ignore','true');bar.style.cssText='display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 16px;align-items:center';
 const status=doc.createElement('span');status.setAttribute('role','status');status.style.cssText='font:12px Arial;color:#526e60';
 (table?['csv']:['jpeg','pdf']).forEach(fmt=>{const b=doc.createElement('button');b.type='button';b.textContent=(fr?'Télécharger ':'Download ')+fmt.toUpperCase()+' ↓';b.style.cssText='font:13px Arial;color:#245f49;background:#f1f7f3;border:1px solid #b9d0c1;border-radius:6px;padding:8px 12px;cursor:pointer';b.onclick=async()=>{b.disabled=true;status.textContent=fr?'Préparation…':'Preparing…';try{
 if(table){const csv=[...el.querySelectorAll('tr')].map(row=>[...row.querySelectorAll('th,td')].map(c=>'"'+c.innerText.replaceAll('"','""')+'"').join(';')).join('\r\n');download(new Blob(['\ufeff'+csv],{type:'text/csv;charset=utf-8'}),'csv');}
 else{const canvas=await capture(el);const blob=fmt==='pdf'?pdfJpeg(canvas):await new Promise(r=>canvas.toBlob(r,'image/jpeg',.94));if(!blob)throw Error('No image');download(blob,fmt==='jpeg'?'jpg':'pdf');}
 status.textContent='';}catch(e){status.textContent=fr?'Téléchargement indisponible pour ce rendu.':'Download unavailable for this rendering.';}finally{b.disabled=false;}};bar.appendChild(b);});bar.appendChild(status);
 const anchor=el.namespaceURI==='http://www.w3.org/2000/svg'?el.closest('svg'):el;anchor.parentNode.insertBefore(bar,anchor.nextSibling);
}
function scan(doc,root){
 if(!root)return;
 if(doc.getElementById('carte')&&doc.getElementById('jpg'))return;
 root.querySelectorAll('svg,canvas,img,table').forEach(el=>{
   if(el.closest('.apri-export-tools,.st-key-zone_nav,.leaflet-container,button,[role="button"]'))return;
   const r=el.getBoundingClientRect();if(r.width<180||r.height<80)return;
   if(el.matches('svg')&&el.parentElement.closest('svg'))return;
   if(el.matches('img')&&!el.closest('[data-testid="stImage"]'))return;
   toolbar(el,el.matches('table'));
 });
 root.querySelectorAll('iframe').forEach(f=>{try{if(f.contentDocument?.body)scan(f.contentDocument,f.contentDocument.body);}catch(e){}});
}
function schedule(){if(pending)return;pending=true;P.setTimeout(()=>{pending=false;scan(D,D.querySelector('.st-key-zone_page'));},400);}
P.__apriExportObserver=new P.MutationObserver(schedule);P.__apriExportObserver.observe(D.body,{childList:true,subtree:true});schedule();
// Embedded result frames finish loading independently of Streamlit's DOM.
P.setTimeout(schedule,1800);P.setTimeout(schedule,4000);
})();
