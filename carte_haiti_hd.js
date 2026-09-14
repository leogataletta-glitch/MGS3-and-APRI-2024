/* CNIGS / HaitiData / World Bank 2014–2016, DOI 10.5069/G9GX48R8.
   Read public tiled GeoTIFF ranges; reproject UTM 18N into display tiles.
   Original imagery: 25 cm. Bare-earth terrain: 1.5 m. Not current imagery. */
async function preparerHaitiHD(m){
 const index=__HD_INDEX__,fr=L_.legend==='Légende',base='https://opentopography.s3.sdsc.edu/raster/Haiti_16/';
 const box=document.createElement('div');box.style.cssText='padding:8px 10px;font:11px system-ui;color:#365b49;border-bottom:1px solid #edf1ee';document.getElementById('liste').prepend(box);
 box.textContent=fr?'Chargement des données détaillées…':'Loading detailed data…';
 function script(src){return new Promise((resolve,reject)=>{const e=document.createElement('script');e.src=src;e.onload=resolve;e.onerror=reject;document.head.append(e);});}
 try{
  await Promise.all([script('https://cdn.jsdelivr.net/npm/geotiff@2.1.3/dist-browser/geotiff.js'),script('https://cdn.jsdelivr.net/npm/proj4@2.12.1/dist/proj4.js')]);
  const projection=proj4('EPSG:4326','+proj=utm +zone=18 +datum=WGS84 +units=m +no_defs'),files=new Map();
  const pool=new GeoTIFF.Pool(2);
  const open=row=>{const key=row[0];if(!files.has(key)){if(files.size>24)files.delete(files.keys().next().value);files.set(key,GeoTIFF.fromUrl(base+key,{allowFullFile:false,blockSize:65536,cacheSize:32}));}return files.get(key);};
  const lng=(x,z)=>x/2**z*360-180,lat=(y,z)=>Math.atan(Math.sinh(Math.PI*(1-2*y/2**z)))*180/Math.PI;
  const png=async canvas=>(await new Promise(r=>canvas.toBlob(r,'image/png'))).arrayBuffer();
  const transparent=()=>{const c=document.createElement('canvas');c.width=c.height=256;return c;};
  async function fallback(z,x,y){const url='https://s3.amazonaws.com/elevation-tiles-prod/terrarium/'+z+'/'+x+'/'+y+'.png';const r=await fetch(url);if(!r.ok)throw Error('Terrain fallback unavailable');const bitmap=await createImageBitmap(await r.blob());const c=transparent();c.getContext('2d').drawImage(bitmap,0,0,256,256);bitmap.close();return c;}
  let busy=0;const queue=[];let finished=0,readFailures=0;
  async function limited(task,signal){if(busy>=4)await new Promise(r=>queue.push(r));busy++;try{if(signal?.aborted)throw new DOMException('Aborted','AbortError');return await task();}finally{busy--;queue.pop()?.();}}
  const tiles=new Map();
  const check=signal=>{if(signal?.aborted)throw new DOMException('Aborted','AbortError');};
  async function render(kind,z,x,y,signal){
   check(signal);
   const terrain=kind==='be',canvas=terrain?await fallback(Math.min(z,15),Math.floor(x/2**Math.max(0,z-15)),Math.floor(y/2**Math.max(0,z-15))):transparent();
   // At high zoom use the matching crop of the fallback parent tile.
   if(terrain&&z>15){const parent=transparent();parent.getContext('2d').drawImage(canvas,0,0);const f=2**(z-15),s=256/f;canvas.getContext('2d').drawImage(parent,(x%f)*s,(y%f)*s,s,s,0,0,256,256);}
   if(z<(terrain?14:15))return png(canvas);
   const coords=new Float64Array(256*256*2);let minX=Infinity,minY=Infinity,maxX=-Infinity,maxY=-Infinity;
   for(let iy=0;iy<256;iy++)for(let ix=0;ix<256;ix++){const p=projection.forward([lng(x+(ix+.5)/256,z),lat(y+(iy+.5)/256,z)]),n=(iy*256+ix)*2;coords[n]=p[0];coords[n+1]=p[1];minX=Math.min(minX,p[0]);maxX=Math.max(maxX,p[0]);minY=Math.min(minY,p[1]);maxY=Math.max(maxY,p[1]);}
   const rows=index[kind].filter(r=>r[1]<maxX&&r[3]>minX&&r[2]<maxY&&r[4]>minY),ctx=canvas.getContext('2d'),pixels=ctx.getImageData(0,0,256,256),a=pixels.data;
   for(const row of rows){
    check(signal);
    try{
     const tiff=await open(row),image=await tiff.getImage(),origin=image.getOrigin(),res=image.getResolution();
     const left=Math.max(minX,row[1]),right=Math.min(maxX,row[3]),bottom=Math.max(minY,row[2]),top=Math.min(maxY,row[4]);
     const sx=Math.max(0,Math.floor((left-origin[0])/res[0])),sy=Math.max(0,Math.floor((top-origin[1])/res[1])),ex=Math.min(image.getWidth(),Math.ceil((right-origin[0])/res[0])),ey=Math.min(image.getHeight(),Math.ceil((bottom-origin[1])/res[1]));
     if(ex<=sx||ey<=sy)continue;
     const bbox=[origin[0]+sx*res[0],origin[1]+ey*res[1],origin[0]+ex*res[0],origin[1]+sy*res[1]];
     const w=Math.min(520,ex-sx),h=Math.min(520,ey-sy);
     const raster=await tiff.readRasters({bbox,width:w,height:h,samples:terrain?[0]:[0,1,2],interleave:true,resampleMethod:terrain?'bilinear':'nearest',pool});
     check(signal);
     for(let n=0;n<65536;n++){const px=coords[n*2],py=coords[n*2+1];if(px<left||px>=right||py<bottom||py>=top)continue;const ix=Math.min(w-1,Math.max(0,Math.floor((px-bbox[0])/(bbox[2]-bbox[0])*w))),iy=Math.min(h-1,Math.max(0,Math.floor((bbox[3]-py)/(bbox[3]-bbox[1])*h))),j=iy*w+ix,k=n*4;
      if(terrain){const height=raster[j];if(!Number.isFinite(height)||height<=0)continue;const v=Math.round((height+32768)*256);a[k]=(v>>>16)&255;a[k+1]=(v>>>8)&255;a[k+2]=v&255;a[k+3]=255;}
      else{const q=j*3;if(!raster[q]&&!raster[q+1]&&!raster[q+2])continue;a[k]=raster[q];a[k+1]=raster[q+1];a[k+2]=raster[q+2];a[k+3]=255;}
     }
    }catch(error){if(error.name==='AbortError')throw error;readFailures++;console.warn('Haiti HD tile unavailable',row[0],error.message);}
   }
   ctx.putImageData(pixels,0,0);return png(canvas);
  }
  m.addProtocol('aprihd',async (request,controller)=>{const [kind,z,x,y]=request.url.replace('aprihd://','').split('/');
   const key=request.url;let data=tiles.get(key);
   if(data){tiles.delete(key);tiles.set(key,data);}else{
    const failuresBefore=readFailures;
    data=await limited(()=>render(kind,+z,+x,+y,controller.signal),controller.signal);
    check(controller.signal);
    if(readFailures===failuresBefore){tiles.set(key,data);if(tiles.size>48)tiles.delete(tiles.keys().next().value);}
   }
   finished++;if(kind==='op')box.dataset.loaded=finished;
   return {data:await createImageBitmap(new Blob([data],{type:'image/png'}),{colorSpaceConversion:'none'})};
  });
  return gl=>{
  const credit='HaitiData / CNIGS / World Bank · 2014–2016 · OpenTopography';
  gl.addSource('haiti-aerial',{type:'raster',tiles:['aprihd://op/{z}/{x}/{y}'],tileSize:256,minzoom:15,maxzoom:20,bounds:[-74.55,17.98,-73.2,19.2],attribution:credit});
  gl.addLayer({id:'haiti-aerial',type:'raster',source:'haiti-aerial',minzoom:15,paint:{'raster-fade-duration':150}},'white-ocean');
  const label=fr?'Photos aériennes 2014–2016 · 25 cm':'Aerial photos 2014–2016 · 25 cm';
  GROUPES.push({titre:'HD',lignes:[{cle:'haiti_hd',titre:label,sym:{type:'tuile'}}]});ETAT.haiti_hd=true;
  box.textContent='';const toggle=document.createElement('input');toggle.type='checkbox';toggle.checked=true;const lab=document.createElement('label');lab.append(toggle,document.createTextNode(' '+label));box.append(lab);
  const aerialVisibility=()=>{ETAT.haiti_hd=toggle.checked&&fondActif==='sat';gl.setLayoutProperty('haiti-aerial','visibility',ETAT.haiti_hd?'visible':'none');};toggle.onchange=aerialVisibility;const oldFondHD=choisirFond;choisirFond=k=>{oldFondHD(k);aerialVisibility();};aerialVisibility();
  const hint=document.createElement('div');hint.style.marginTop='5px';hint.textContent=fr?'Zoomez pour voir les photos. Relief détaillé : 1,5 m, selon couverture.':'Zoom in to see photos. Detailed terrain: 1.5 m, where available.';box.append(hint);const hintText=hint.textContent;gl.on('dataloading',e=>{if(e.sourceId==='haiti-aerial'||e.sourceId==='dem')hint.textContent=fr?'Chargement des détails…':'Loading details…';});gl.on('idle',()=>{hint.textContent=readFailures?(fr?'Certains fichiers sont indisponibles ; le fond habituel complète la vue.':'Some files are unavailable; the standard basemap fills the view.'):hintText;});
  const link=document.createElement('a');link.textContent=fr?'Source et date des données':'Data source and date';link.href='https://doi.org/10.5069/G9GX48R8';link.target='_blank';link.rel='noopener';box.append(link);
  };
 }catch(error){box.textContent=fr?'Données détaillées indisponibles ; fond habituel conservé.':'Detailed data unavailable; standard basemap retained.';console.warn(error);}
}
