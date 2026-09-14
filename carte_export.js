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
async function exporterCarte(format){
  const status=document.getElementById('exportEtat'),buttons=['jpg','pdf'].map(id=>document.getElementById(id));
  buttons.forEach(b=>b.disabled=true);status.textContent=L_.export_wait;
  try{
    if(document.querySelector('.leaflet-zoom-anim'))throw Error('Map moving');
    const root=document.getElementById('carte'),bounds=root.getBoundingClientRect(),width=Math.round(bounds.width),height=Math.round(bounds.height);
    const active=GROUPES.flatMap(g=>g.lignes).filter(l=>l.fond?l.cle===fondActif:ETAT[l.cle]);
    const selected=[...sectionsChoisies];
    const exportHeight=Math.max(height+52,110+active.length*34+selected.length*20);
    const canvas=document.createElement('canvas');canvas.width=(width+300)*2;canvas.height=exportHeight*2;
    const ctx=canvas.getContext('2d');ctx.scale(2,2);ctx.fillStyle='white';ctx.fillRect(0,0,width+300,exportHeight);
    const panes=[...root.querySelectorAll('.leaflet-pane')].filter(p=>p.classList.contains('leaflet-tile-pane')||p.querySelector(':scope > canvas'));
    panes.sort((a,b)=>(+getComputedStyle(a).zIndex||0)-(+getComputedStyle(b).zIndex||0));
    for(const pane of panes){
      ctx.save();ctx.beginPath();ctx.rect(0,0,width,height);ctx.clip();
      if(pane.classList.contains('leaflet-tile-pane')&&contoursTerre.length){
        ctx.beginPath();contoursTerre.forEach(({anneau})=>{anneau.forEach((c,i)=>{const p=carte.latLngToContainerPoint([c[1],c[0]]);i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y);});ctx.closePath();});ctx.clip();
      }
      for(const el of pane.querySelectorAll('img.leaflet-tile,canvas')){
        const r=el.getBoundingClientRect();if(!r.width||!r.height||r.right<bounds.left||r.left>bounds.right||r.bottom<bounds.top||r.top>bounds.bottom)continue;
        if(el.tagName==='IMG'&&(!el.complete||!el.naturalWidth))throw Error('Tiles incomplete');
        let opacity=1;for(let n=el;n&&n!==root;n=n.parentElement)opacity*=Number(getComputedStyle(n).opacity);
        ctx.globalAlpha=opacity;ctx.drawImage(el,r.left-bounds.left,r.top-bounds.top,r.width,r.height);
      }ctx.restore();
    }
    // Permanent town names are DOM tooltips, not part of Leaflet's canvas.
    ctx.font='bold 12px Arial';ctx.textBaseline='middle';
    root.querySelectorAll('.etq-ville').forEach(el=>{const r=el.getBoundingClientRect(),x=r.left-bounds.left,y=r.top-bounds.top+r.height/2;if(x<0||x>width||y<0||y>height)return;ctx.lineWidth=3;ctx.strokeStyle='white';ctx.strokeText(el.textContent,x,y);ctx.fillStyle='#20382f';ctx.fillText(el.textContent,x,y);});
    const scale=root.querySelector('.leaflet-control-scale-line');
    if(scale){const r=scale.getBoundingClientRect(),w=r.width;ctx.fillStyle='rgba(255,255,255,.94)';ctx.fillRect(12,height-49,w+24,39);ctx.strokeStyle='#243e34';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(22,height-29);ctx.lineTo(22,height-20);ctx.lineTo(22+w,height-20);ctx.lineTo(22+w,height-29);ctx.stroke();ctx.fillStyle='#243e34';ctx.font='12px Arial';ctx.fillText(scale.textContent,24,height-36);}
    ctx.fillStyle='#294b3d';ctx.font='bold 14px Arial';ctx.fillText('APRI · '+L_.section,12,height+18);
    ctx.font='10px Arial';ctx.fillStyle='#546b60';ctx.fillText(root.querySelector('.leaflet-control-attribution')?.textContent||'',12,height+38,width-24);
    // Export a static legend of visible layers, without interactive controls.
    const lx=width+20;let ly=30;ctx.fillStyle='#294b3d';ctx.font='bold 16px Arial';ctx.fillText(L_.legend,lx,ly);ly+=30;
    active.forEach(l=>{const sym=l.sym||{type:'tuile'},c=sym.c||'#9daeb1';ctx.fillStyle=c;ctx.strokeStyle=c;ctx.lineWidth=2;
      if(sym.type==='ligne'){ctx.setLineDash(sym.d?[4,3]:[]);ctx.beginPath();ctx.moveTo(lx,ly);ctx.lineTo(lx+20,ly);ctx.stroke();ctx.setLineDash([]);}
      else if(sym.type==='point'){ctx.beginPath();ctx.arc(lx+10,ly,5,0,Math.PI*2);ctx.fill();}
      else{ctx.globalAlpha=.4;ctx.fillRect(lx,ly-6,20,12);ctx.globalAlpha=1;ctx.strokeRect(lx,ly-6,20,12);}
      ctx.fillStyle='#385348';ctx.font='12px Arial';const words=l.titre.split(' ');let line='',lines=[];words.forEach(w=>{if(ctx.measureText(line+w).width>238){lines.push(line);line='';}line+=w+' ';});lines.push(line);lines.forEach((t,i)=>ctx.fillText(t,lx+30,ly+i*14));ly+=Math.max(28,lines.length*14+8);
    });
    ly+=16;ctx.font='bold 12px Arial';ctx.fillText(L_.section,lx,ly);ly+=23;ctx.font='12px Arial';selected.forEach(name=>{ctx.fillText(name,lx,ly);ly+=20;});
    const blob=format==='pdf'?pdfJpeg(canvas):await new Promise(resolve=>canvas.toBlob(resolve,'image/jpeg',.94));
    if(!blob)throw Error('No image');const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='APRI-carte.'+(format==='pdf'?'pdf':'jpg');a.click();setTimeout(()=>URL.revokeObjectURL(url),30000);status.textContent='';
  }catch(e){status.textContent=L_.export_fail;}
  finally{buttons.forEach(b=>b.disabled=false);}
}
