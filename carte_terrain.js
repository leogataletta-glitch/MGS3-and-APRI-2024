/* One terrain map with two camera presets; Leaflet remains the fallback. */
(async function(){
 // Forward ordinary wheel gestures from the embedded map to its page shell.
 // Ctrl+wheel retains map zoom; the layer panel keeps its own scrolling.
 carte.scrollWheelZoom.disable();
 document.addEventListener('wheel',e=>{
  if(e.target.closest('#panneau'))return;
  const zoom=e.ctrlKey||e.metaKey;
  if(window.apriTerrain){if(zoom)window.apriTerrain.scrollZoom.enable();else window.apriTerrain.scrollZoom.disable();}
  if(zoom){carte.scrollWheelZoom.enable();return;}
  carte.scrollWheelZoom.disable();
  window.parent.postMessage({type:'apri-map-wheel',dy:e.deltaY,dx:e.deltaX,mode:e.deltaMode},'*');
 },{capture:true,passive:true});
 const fr=L_.legend==='Légende';
 const controls=document.createElement('div');controls.className='boutons';
 const top=document.createElement('button'),tilt=document.createElement('button'),atlas=document.createElement('button');
 top.textContent=fr?'Vue de dessus':'Top view';tilt.textContent=fr?'Vue relief':'Relief view';
 atlas.textContent=fr?'Style atlas 2D':'2D atlas style';
 top.disabled=tilt.disabled=atlas.disabled=true;controls.append(top,tilt,atlas);
 document.querySelector('#panneau .tete').append(controls);
 const note=document.createElement('div');note.setAttribute('role','status');note.style.cssText='font-size:11px;color:#587082;padding-top:6px';
 note.textContent=fr?'Chargement du relief…':'Loading terrain…';controls.after(note);
 const css=document.createElement('link');css.rel='stylesheet';css.href='https://unpkg.com/maplibre-gl@6.9.0/dist/maplibre-gl.css';document.head.append(css);
 const styles=document.createElement('style');styles.textContent='#carte3d{position:absolute;left:0;top:0;bottom:0;right:0;border-radius:0;overflow:hidden;visibility:hidden}.maplibregl-popup-content{font:12px system-ui;color:#234c3e}.maplibregl-ctrl-attrib{font-size:10px}#panneau button[aria-pressed="true"]{background:#dcebf7;border-color:#6c9fbe;color:#173e59}@media(max-width:620px){#carte,#carte3d{right:0;bottom:50%}#panneau{height:48%;overflow-y:auto}#panneau .tete{flex-shrink:0}#liste{overflow:visible;flex:none}}';document.head.append(styles);
 const host=document.createElement('div');host.id='carte3d';document.getElementById('carte').after(host);
 // Streamlit's initial iframe height is only a fallback: fill the viewport.
 try{
  const frame=window.frameElement;
  if(frame){
   const parentWindow=window.parent,main=frame.closest('[data-testid="stMain"]');
   let resizeFrame;
   const fitHeight=()=>{cancelAnimationFrame(resizeFrame);resizeFrame=requestAnimationFrame(()=>{
    const rect=frame.getBoundingClientRect(),scale=rect.height/frame.offsetHeight||1;
    // On the single scrolling page the map is one screen among others: a fixed
    // height that leaves room for its title, whatever its current position.
    const unePage=parentWindow.document.querySelector('.st-key-sec_accueil');
    const height=unePage?Math.max(420,Math.round((parentWindow.innerHeight-240)/scale)):Math.max(480,Math.round((parentWindow.innerHeight-Math.max(0,rect.top))/scale));
    if(Math.abs(frame.offsetHeight-height)>1)frame.style.setProperty('height',height+'px','important');
   });};
   parentWindow.addEventListener('resize',fitHeight);main?.addEventListener('scroll',fitHeight,{passive:true});fitHeight();
   const observer=new ResizeObserver(fitHeight);observer.observe(parentWindow.document.documentElement);
   window.addEventListener('pagehide',()=>{parentWindow.removeEventListener('resize',fitHeight);main?.removeEventListener('scroll',fitHeight);observer.disconnect();cancelAnimationFrame(resizeFrame);},{once:true});
  }
 }catch(error){/* Cross-origin embedding retains the initial usable height. */}
 const polish=document.createElement('style');polish.textContent=`
 #panneau{font-family:system-ui,sans-serif;color:#294658}
 #panneau .ligne .lib{font-size:13px;line-height:1.4}#panneau .ligne{min-height:30px}
 #panneau button{font-size:12px;min-height:30px}#panneau .titre{color:#34566e;font-size:12px}
 #panneau input[type=checkbox],#panneau input[type=radio]{accent-color:#397fa3;width:15px;height:15px}
 #panneau :focus-visible{outline:2px solid #397fa3;outline-offset:3px}
 .map-camera{margin-top:10px;padding:9px 10px;border-radius:9px;background:#edf4f9}
 .map-camera summary{font-size:12px;font-weight:600;cursor:pointer;color:#2c5875}
 .map-explore{display:block;margin:6px 8px 12px;font-size:12px;font-weight:600;color:#315970}
 .map-explore select{display:block;margin-top:7px;padding:9px;width:100%;border:1px solid #d1e0ec;border-radius:8px;background:white;color:#28485e;font:13px system-ui}
 #liste{scrollbar-width:thin;scrollbar-color:#b5c8d8 transparent}
 .maplibregl-popup-content{border-radius:10px;padding:14px;box-shadow:0 4px 18px #234c3e22}
 `;document.head.append(polish);
 let gl,ready=false,failed=false;
 function fallback(){if(failed)return;failed=true;window.apriTerrain=null;host.remove();if(gl)gl.remove();document.getElementById('carte').style.visibility='visible';document.getElementById('map-loading')?.remove();carte.invalidateSize();top.disabled=tilt.disabled=true;note.textContent=fr?'Relief indisponible : la carte 2D reste accessible.':'Terrain unavailable: the 2D map remains available.';}
 const timeout=setTimeout(()=>{if(!ready)fallback();},25000);
 try{
  const m=await import('https://unpkg.com/maplibre-gl@6.9.0/dist/maplibre-gl.mjs');
  if(failed)return;
  const installerHD=await preparerHaitiHD(m);
  if(failed)return;
  const raster=(tiles,attribution,maxzoom=19)=>({type:'raster',tiles:[tiles],tileSize:256,attribution,maxzoom});
  gl=new m.Map({container:host,center:[-74.05,18.33],zoom:9,pitch:0,maxPitch:80,maxZoom:21,dragRotate:true,pitchWithRotate:true,canvasContextAttributes:{preserveDrawingBuffer:true},
   style:{version:8,sources:{
    sat:raster('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}','Esri, Maxar, Earthstar Geographics',17),
    plan:raster('https://tile.openstreetmap.org/{z}/{x}/{y}.png','© OpenStreetMap'),
    relief:raster('https://a.tile.opentopomap.org/{z}/{x}/{y}.png','© OpenTopoMap, © OpenStreetMap',17),
    dem:{type:'raster-dem',tiles:[installerHD?'aprihd://be/{z}/{x}/{y}':'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png'],encoding:'terrarium',tileSize:256,maxzoom:installerHD?17:15,attribution:'Terrain © Mapzen / AWS Open Data'}
   },layers:[{id:'background',type:'background',paint:{'background-color':'#edf4f9'}},...['sat','plan','relief'].map(id=>({id,type:'raster',source:id,layout:{visibility:id==='sat'?'visible':'none'}}))],terrain:{source:'dem',exaggeration:1}}});
  gl.scrollZoom.disable();
  gl.addControl(new m.NavigationControl({visualizePitch:true}),'top-left');gl.addControl(new m.ScaleControl({unit:'metric'}),'bottom-left');
  gl.getCanvas().addEventListener('webglcontextlost',fallback);
  const mapResize=new ResizeObserver(()=>{gl.resize();carte.invalidateSize();});mapResize.observe(host);
  window.addEventListener('pagehide',()=>mapResize.disconnect(),{once:true});
  const fc=features=>({type:'FeatureCollection',features});
  const feature=(geometry,properties={})=>({type:'Feature',geometry,properties});
  const polygons=items=>fc((items||[]).flatMap(o=>o.geometry?[feature(o.geometry,o.p)]:(o.a||[]).filter(a=>a.length>2).map(a=>feature({type:'Polygon',coordinates:[[...a,a[0]]]},o.p))));
  const lines=items=>fc((items||[]).filter(o=>o.l?.length>1).map(o=>feature({type:'LineString',coordinates:o.l},o.p)));
  const pointData=key=>fc((D.entretiens||[]).filter(e=>(e[3]==='Montagne'?'pts_m':'pts_l')===key&&new Set([...sectionsChoisies].map(normaliserSection)).has(normaliserSection(e[2]))).map(e=>feature({type:'Point',coordinates:[e[0],e[1]]},{section:e[2],paysage:e[3],numero:e[4]})));
  const ids={};
  function add(key,data,type,paint){if(!gl.getSource(key))gl.addSource(key,{type:'geojson',data,...(key==='ap'?{attribution:'Protected areas © UNEP-WCMC / IUCN · 08/2026'}:{})});const id=key+'-'+type;gl.addLayer({id,type,source:key,paint});(ids[key]||=[]).push(id);}
  function sync(){if(!ready||failed)return;for(const k of ['sat','plan','relief'])gl.setLayoutProperty(k,'visibility',fondActif===k?'visible':'none');for(const [k,list]of Object.entries(ids))for(const id of list)gl.setLayoutProperty(id,'visibility',(k==='terre'?fondActif==='sobre':!!ETAT[k])?'visible':'none');gl.getSource('sections').setData(polygons((D.sections||[]).filter(o=>sectionsChoisies.has(o.p.section))));for(const k of ['pts_l','pts_m'])gl.getSource(k).setData(pointData(k));}
  gl.on('load',()=>{
   if(failed)return;
   add('terre',polygons(D.terre),'fill',{'fill-color':'#dce2df'});
   gl.addLayer({id:'ombrage-hillshade',type:'hillshade',source:'dem',paint:{'hillshade-exaggeration':.15}});ids.ombrage=['ombrage-hillshade'];
   for(const [id,service] of [['bathy-relief','GEBCO_basemap_NCEI'],['bathy-contours','GEBCO_contours']]){
    gl.addSource(id,raster('https://tiles.arcgis.com/tiles/C8EMgrsFcRFL6LrL/arcgis/rest/services/'+service+'/MapServer/tile/{z}/{y}/{x}','GEBCO / NOAA NCEI',10));
    gl.addLayer({id,type:'raster',source:id,layout:{visibility:'none'}});
   }
   ids.bathy=['bathy-relief','bathy-contours'];
   // D.terre contains local study contours, not a complete global coastline.
   // Never use it to mask the basemap: that hides entire regions on zoom-out.
   for(const [k,source]of Object.entries({paysage:'paysage_ga',paysage_sud:'paysage_sud',ap:'aires_protegees',sections:'sections',deps:'departements',pays:'pays'})){
    const color=C[k]||C.paysage;
    if(['paysage','paysage_sud','ap','sections'].includes(k))add(k,polygons(D[source]),'fill',{'fill-color':color,'fill-opacity':k==='sections'?.25:.08});
    add(k,polygons(D[source]),'line',{'line-color':k==='sections'?'#ffffff':color,'line-width':1.7,...(['deps','paysage','paysage_sud'].includes(k)?{'line-dasharray':[4,3]}:{})});
   }
   for(const [k,source]of [['riv','rivieres'],['rp','routes_p']])add(k,lines(D[source]),'line',{'line-color':C[k],'line-width':k==='rp'?2.4:1.3});
   for(const k of ['pts_l','pts_m'])add(k,pointData(k),'circle',{'circle-radius':3.4,'circle-color':C[k],'circle-stroke-color':'white','circle-stroke-width':1});
   add('villes',fc((D.villes||[]).map(v=>feature({type:'Point',coordinates:v.pt},{nom:v.p.Nom}))),'circle',{'circle-radius':5,'circle-color':C.villes,'circle-stroke-color':'white','circle-stroke-width':2});
   // Labels use local system fonts through DOM markers, avoiding a glyph service.
   const labels=(D.villes||[]).map(v=>{const el=document.createElement('span');el.textContent=v.p.Nom;el.className='etq-ville';el.style.paddingLeft='18px';return new m.Marker({element:el,anchor:'left'}).setLngLat(v.pt).addTo(gl);});
   gl.on('render',()=>labels.forEach(x=>x.getElement().style.display=ETAT.villes?'':'none'));
   gl.on('click',e=>{if(window.apriMeasure?.active())return;const hits=gl.queryRenderedFeatures(e.point,{layers:['pts_l-circle','pts_m-circle','sections-fill','villes-circle','ap-fill']});if(!hits.length)return;const p=hits[0].properties;if(hits[0].layer.id==='ap-fill'){new m.Popup({maxWidth:'340px'}).setLngLat(e.lngLat).setHTML(protectedPopup(p)).addTo(gl);return;}const body=document.createElement('div');body.textContent=p.numero?('n° '+p.numero+' · '+p.section+' · '+p.paysage):(p.section||p.nom||'');new m.Popup().setLngLat(e.lngLat).setDOMContent(body).addTo(gl);});
   ready=true;clearTimeout(timeout);window.apriTerrain=gl;sync();window.apriMeasure?.install(gl);
   // Reveal only after the configured camera and layers have rendered.
   gl.once('render',()=>{
    if(failed)return;
    host.style.visibility='visible';
    document.getElementById('map-loading')?.remove();
   });
   gl.fitBounds([[-74.55,17.98],[-73.55,18.68]],{padding:{top:25,bottom:25,left:25,right:window.innerWidth>620?311:25},duration:0});
   top.disabled=tilt.disabled=false;
   const state=()=>{top.setAttribute('aria-pressed',String(gl.getPitch()<1));tilt.setAttribute('aria-pressed',String(gl.getPitch()>=1));};gl.on('moveend',state);state();
   top.onclick=()=>gl.easeTo({pitch:0,bearing:0,duration:700});
   tilt.onclick=()=>gl.easeTo({pitch:60,duration:900});
   const detail=document.createElement('details');detail.className='map-camera';
   const summary=document.createElement('summary');summary.textContent=fr?'Réglages du relief':'Terrain settings';detail.append(summary);controls.after(detail);detail.append(note);
   const compass=document.createElement('div');compass.style.cssText='margin-top:10px;font-size:12px;color:#315970';
   const compassTitle=document.createElement('div');compassTitle.textContent=fr?'Orientation · en haut de la carte':'Orientation · top of the map';
   const compassButtons=document.createElement('div');compassButtons.className='boutons';
   const directions=(fr?['Nord','Est','Sud','Ouest']:['North','East','South','West']).map((name,i)=>{
    const button=document.createElement('button');button.textContent=name;button.setAttribute('aria-label',fr?name+' en haut':name+' at top');
    button.onclick=()=>gl.easeTo({bearing:i*90,duration:550});compassButtons.append(button);return button;
   });
   compass.append(compassTitle,compassButtons);controls.after(compass);
   note.textContent='';
   function slider(label,min,max,step,value,format,change){
    const box=document.createElement('label');box.style.cssText='display:block;font-size:11px;color:#36566f;margin-top:9px';
    const text=document.createElement('span'),out=document.createElement('output'),input=document.createElement('input');
    text.textContent=label+' ';out.textContent=format(value);input.type='range';input.min=min;input.max=max;input.step=step;input.value=value;input.setAttribute('aria-label',label);input.style.cssText='display:block;width:100%;accent-color:#397fa3;cursor:ew-resize';
    input.oninput=()=>{out.textContent=format(+input.value);change(+input.value);};box.append(text,out,input);note.before(box);return {input,out,format};
   }
   const angle=slider(fr?'Inclinaison':'Tilt',0,80,1,0,v=>Math.round(v)+'°',v=>{gl.stop();gl.setPitch(v);});
   gl.on('pitch',()=>{angle.input.value=gl.getPitch();angle.out.textContent=angle.format(gl.getPitch());});
   const rotation=slider(fr?'Rotation':'Rotation',0,359,1,0,v=>Math.round(v)+'°',v=>{gl.stop();gl.setBearing(v);});
   const syncRotation=()=>{const bearing=(gl.getBearing()%360+360)%360;rotation.input.value=Math.round(bearing)%360;rotation.out.textContent=rotation.format(bearing%360);directions.forEach((button,i)=>button.setAttribute('aria-pressed',String(Math.abs(((bearing-i*90+540)%360)-180)<.5)));};
   gl.on('rotate',syncRotation);syncRotation();
   tilt.addEventListener('click',()=>{detail.open=true;});
   if(installerHD)installerHD(gl);
   // The original 2D look: satellite imagery softened by Esri hillshade.
   gl.addSource('atlas-shade',{type:'raster',tiles:['https://server.arcgisonline.com/ArcGIS/rest/services/Elevation/World_Hillshade/MapServer/tile/{z}/{y}/{x}'],tileSize:256,maxzoom:16,attribution:'Esri'});
   gl.addLayer({id:'atlas-shade',type:'raster',source:'atlas-shade',layout:{visibility:'none'},paint:{'raster-opacity':.5}},'ombrage-hillshade');
   let atlasOn=false;
   const atlasState=on=>{atlasOn=on;atlas.setAttribute('aria-pressed',String(on));gl.setLayoutProperty('atlas-shade','visibility',on&&ETAT.ombrage?'visible':'none');gl.setLayoutProperty('ombrage-hillshade','visibility',!on&&ETAT.ombrage?'visible':'none');};
   atlas.disabled=false;atlasState(false);
   atlas.onclick=()=>{choisirFond('sat');const radio=document.querySelector('input[name="fond"][value="sat"]');if(radio)radio.checked=true;ETAT.ombrage=true;basculer('ombrage',true);const shade=document.querySelector('input[data-cle="ombrage"]');if(shade)shade.checked=true;atlasState(true);gl.easeTo({pitch:0,bearing:0,duration:700});};
   top.addEventListener('click',()=>atlasState(false));tilt.addEventListener('click',()=>atlasState(false));
   const oldFond=choisirFond,oldToggle=basculer,oldFilter=filtrerSections,oldReset=recadrer;
   choisirFond=k=>{oldFond(k);sync();atlasState(false);};basculer=(k,on)=>{oldToggle(k,on);sync();atlasState(atlasOn);};filtrerSections=()=>{oldFilter();sync();atlasState(atlasOn);};
   recadrer=()=>{if(failed)return oldReset();gl.fitBounds([[-74.55,17.98],[-73.55,18.68]],{padding:{top:25,bottom:25,left:25,right:window.innerWidth>620?311:25},pitch:0,bearing:0});};
  });
 }catch(e){clearTimeout(timeout);fallback();}
})();
