/* One terrain map with two camera presets; Leaflet remains the fallback. */
(async function(){
 const fr=L_.legend==='Légende';
 const controls=document.createElement('div');controls.className='boutons';
 const top=document.createElement('button'),tilt=document.createElement('button'),atlas=document.createElement('button');
 top.textContent=fr?'Vue de dessus':'Top view';tilt.textContent=fr?'Vue relief':'Relief view';
 atlas.textContent=fr?'Style atlas 2D':'2D atlas style';
 top.disabled=tilt.disabled=atlas.disabled=true;controls.append(top,tilt,atlas);
 document.querySelector('#panneau .tete').append(controls);
 const note=document.createElement('div');note.setAttribute('role','status');note.style.cssText='font-size:11px;color:#587264;padding-top:6px';
 note.textContent=fr?'Chargement du relief…':'Loading terrain…';controls.after(note);
 const css=document.createElement('link');css.rel='stylesheet';css.href='https://unpkg.com/maplibre-gl@6.9.0/dist/maplibre-gl.css';document.head.append(css);
 const styles=document.createElement('style');styles.textContent='#carte3d{position:absolute;left:0;top:0;bottom:0;right:302px;border-radius:12px;overflow:hidden;visibility:hidden}.maplibregl-popup-content{font:12px system-ui;color:#234c3e}.maplibregl-ctrl-attrib{font-size:10px}#panneau button[aria-pressed="true"]{background:#dceee3;border-color:#62967c;color:#164a35}@media(max-width:620px){#carte,#carte3d{right:0;bottom:50%}#panneau{height:48%;overflow-y:auto}#panneau .tete{flex-shrink:0}#liste{overflow:visible;flex:none}}';document.head.append(styles);
 const host=document.createElement('div');host.id='carte3d';document.getElementById('carte').after(host);
 // Streamlit's initial iframe height is only a fallback: fill the viewport.
 try{
  const frame=window.frameElement;
  if(frame){
   const parentWindow=window.parent,main=frame.closest('[data-testid="stMain"]');
   let resizeFrame;
   const fitHeight=()=>{cancelAnimationFrame(resizeFrame);resizeFrame=requestAnimationFrame(()=>{
    const rect=frame.getBoundingClientRect(),scale=rect.height/frame.offsetHeight||1;
    const height=Math.max(480,Math.round((parentWindow.innerHeight-Math.max(0,rect.top)-12)/scale));
    if(Math.abs(frame.offsetHeight-height)>1)frame.style.setProperty('height',height+'px','important');
   });};
   parentWindow.addEventListener('resize',fitHeight);main?.addEventListener('scroll',fitHeight,{passive:true});fitHeight();
   const observer=new ResizeObserver(fitHeight);observer.observe(parentWindow.document.documentElement);
   window.addEventListener('pagehide',()=>{parentWindow.removeEventListener('resize',fitHeight);main?.removeEventListener('scroll',fitHeight);observer.disconnect();cancelAnimationFrame(resizeFrame);},{once:true});
  }
 }catch(error){/* Cross-origin embedding retains the initial usable height. */}
 const polish=document.createElement('style');polish.textContent=`
 #panneau{font-family:system-ui,sans-serif;color:#294d40}
 #panneau .ligne .lib{font-size:13px;line-height:1.4}#panneau .ligne{min-height:30px}
 #panneau button{font-size:12px;min-height:30px}#panneau .titre{color:#345e4d;font-size:12px}
 #panneau input[type=checkbox],#panneau input[type=radio]{accent-color:#27694e;width:15px;height:15px}
 #panneau :focus-visible{outline:2px solid #27694e;outline-offset:3px}
 .map-camera{margin-top:10px;padding:9px 10px;border-radius:9px;background:#f3f7f4}
 .map-camera summary{font-size:12px;font-weight:600;cursor:pointer;color:#2c604b}
 .map-explore{display:block;margin:6px 8px 12px;font-size:12px;font-weight:600;color:#315d4a}
 .map-explore select{display:block;margin-top:7px;padding:9px;width:100%;border:1px solid #d8e5dc;border-radius:8px;background:white;color:#284c3e;font:13px system-ui}
 #liste{scrollbar-width:thin;scrollbar-color:#b5c9bc transparent}
 .maplibregl-popup-content{border-radius:10px;padding:14px;box-shadow:0 4px 18px #234c3e22}
 `;document.head.append(polish);
 let gl,ready=false,failed=false;
 function fallback(){if(failed)return;failed=true;window.apriTerrain=null;host.remove();if(gl)gl.remove();document.getElementById('carte').style.visibility='';carte.invalidateSize();top.disabled=tilt.disabled=true;note.textContent=fr?'Relief indisponible : la carte 2D reste accessible.':'Terrain unavailable: the 2D map remains available.';}
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
   },layers:[{id:'background',type:'background',paint:{'background-color':'#ffffff'}},...['sat','plan','relief'].map(id=>({id,type:'raster',source:id,layout:{visibility:id==='sat'?'visible':'none'}}))],terrain:{source:'dem',exaggeration:1}}});
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
   // White outside the same land contours used by the 2D map. This layer
   // sits above imagery/hillshade but below the study layers, and is also
   // captured by JPEG/PDF exports directly from the WebGL canvas.
   const ring=a=>{const r=a.map(p=>p.slice());if(r[0][0]!==r.at(-1)[0]||r[0][1]!==r.at(-1)[1])r.push(r[0].slice());return r;};
   const coast=(D.terre||[]).flatMap(o=>o.a||[]).filter(a=>a.length>2).map(ring);
   gl.addSource('white-ocean',{type:'geojson',data:fc([feature({type:'Polygon',coordinates:[[[ -180,-85],[180,-85],[180,85],[-180,85],[-180,-85]],...coast]})])});
   gl.addLayer({id:'white-ocean',type:'fill',source:'white-ocean',paint:{'fill-color':'#ffffff','fill-opacity':1,'fill-antialias':false}});
   // Feather the land into the white page; keep study overlays above the fade.
   // Render in WebGL so the same soft coastline appears in JPEG/PDF exports.
   gl.addSource('coast-fade',{type:'geojson',data:fc([feature({type:'MultiLineString',coordinates:coast})])});
   gl.addLayer({id:'coast-fade',type:'line',source:'coast-fade',layout:{'line-join':'round','line-cap':'round'},paint:{'line-color':'#ffffff','line-width':12,'line-blur':12,'line-opacity':1}});
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
   gl.on('click',e=>{const hits=gl.queryRenderedFeatures(e.point,{layers:['pts_l-circle','pts_m-circle','sections-fill','villes-circle','ap-fill']});if(!hits.length)return;const p=hits[0].properties;if(hits[0].layer.id==='ap-fill'){new m.Popup({maxWidth:'340px'}).setLngLat(e.lngLat).setHTML(protectedPopup(p)).addTo(gl);return;}const body=document.createElement('div');body.textContent=p.numero?('n° '+p.numero+' · '+p.section+' · '+p.paysage):(p.section||p.nom||'');new m.Popup().setLngLat(e.lngLat).setDOMContent(body).addTo(gl);});
   ready=true;clearTimeout(timeout);window.apriTerrain=gl;sync();
   const positionBox=document.createElement('div');positionBox.setAttribute('role','group');positionBox.setAttribute('aria-label',fr?'Position sur la carte':'Map position');
   positionBox.style.cssText='margin:8px 10px;padding:11px;background:#f3f7f4;border-radius:9px;font:12px/1.6 system-ui;color:#315d4a;font-variant-numeric:tabular-nums';
   const place=document.createElement('strong'),altitude=document.createElement('div'),coordinates=document.createElement('div');
   place.textContent=fr?'Survolez la carte':'Move over the map';altitude.textContent=fr?'Altitude estimée : —':'Estimated elevation: —';coordinates.textContent='WGS84 · —';positionBox.append(place,altitude,coordinates);document.getElementById('liste').prepend(positionBox);
   const contains=(ring,x,y)=>{let inside=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[i],b=ring[j];if((a[1]>y)!==(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])inside=!inside;}return inside;};
   const within=(item,x,y)=>(item.a||[]).some(ring=>contains(ring,x,y));
   let pointer=null,pointerFrame;
   const updatePosition=()=>{if(!pointer||failed)return;const ll=gl.unproject(pointer),x=ll.lng,y=ll.lat;
    const section=(D.sections||[]).find(item=>within(item,x,y));
    place.textContent=section?section.p.section:(fr?'Hors des sections étudiées':'Outside surveyed sections');
    const onLand=(D.terre||[]).some(item=>within(item,x,y));
    const value=onLand?gl.queryTerrainElevation(ll):null,ratio=gl.getTerrain()?.exaggeration||1;
    altitude.textContent=(fr?'Altitude estimée : ':'Estimated elevation: ')+(value!=null&&Number.isFinite(value)?'≈ '+Math.round(value/ratio).toLocaleString(fr?'fr-FR':'en-US')+' m':'—');
    coordinates.textContent='WGS84 · Lat '+y.toFixed(5)+'° · Lon '+x.toFixed(5)+'°';
   };
   const track=e=>{pointer=e.point;cancelAnimationFrame(pointerFrame);pointerFrame=requestAnimationFrame(updatePosition);};
   gl.on('mousemove',track);gl.on('click',track);gl.on('moveend',updatePosition);gl.on('idle',updatePosition);
   gl.getCanvas().addEventListener('mouseleave',()=>{pointer=null;cancelAnimationFrame(pointerFrame);place.textContent=fr?'Survolez la carte':'Move over the map';altitude.textContent=fr?'Altitude estimée : —':'Estimated elevation: —';coordinates.textContent='WGS84 · —';});
   host.style.visibility='visible';document.getElementById('carte').style.visibility='hidden';
   gl.fitBounds([[-74.55,17.98],[-73.55,18.68]],{padding:25,duration:0});
   top.disabled=tilt.disabled=false;
   const state=()=>{top.setAttribute('aria-pressed',String(gl.getPitch()<1));tilt.setAttribute('aria-pressed',String(gl.getPitch()>=1));};gl.on('moveend',state);state();
   top.onclick=()=>gl.easeTo({pitch:0,bearing:0,duration:700});
   tilt.onclick=()=>gl.easeTo({pitch:60,duration:900});
   // Move to a territory without changing the user's visible layers.
   const explore=document.createElement('label');explore.className='map-explore';
   explore.textContent=fr?'Aller à une section':'Go to a section';
   const destination=document.createElement('select');destination.setAttribute('aria-label',explore.textContent);
   const placeholder=new Option(fr?'Choisir une section…':'Choose a section…','');destination.add(placeholder);
   [...new Set((D.sections||[]).map(o=>o.p.section))].sort().forEach(name=>destination.add(new Option(name,name)));
   destination.onchange=()=>{if(!destination.value)return;const points=(D.sections||[]).filter(o=>o.p.section===destination.value).flatMap(o=>(o.a||[]).flat());if(!points.length)return;const bounds=points.reduce((b,p)=>b.extend(p),new m.LngLatBounds(points[0],points[0]));gl.fitBounds(bounds,{padding:55,maxZoom:15,duration:1000});};
   explore.append(destination);document.getElementById('liste').prepend(explore);
   const detail=document.createElement('details');detail.className='map-camera';
   const summary=document.createElement('summary');summary.textContent=fr?'Réglages du relief':'Terrain settings';detail.append(summary);controls.after(detail);detail.append(note);
   const compass=document.createElement('div');compass.style.cssText='margin-top:10px;font-size:12px;color:#315d4a';
   const compassTitle=document.createElement('div');compassTitle.textContent=fr?'Orientation · en haut de la carte':'Orientation · top of the map';
   const compassButtons=document.createElement('div');compassButtons.className='boutons';
   const directions=(fr?['Nord','Est','Sud','Ouest']:['North','East','South','West']).map((name,i)=>{
    const button=document.createElement('button');button.textContent=name;button.setAttribute('aria-label',fr?name+' en haut':name+' at top');
    button.onclick=()=>gl.easeTo({bearing:i*90,duration:550});compassButtons.append(button);return button;
   });
   compass.append(compassTitle,compassButtons);controls.after(compass);
   note.textContent=fr?'Maintenez le clic droit et glissez verticalement pour incliner, horizontalement pour tourner.':'Hold the right mouse button: drag vertically to tilt, horizontally to rotate.';
   function slider(label,min,max,step,value,format,change){
    const box=document.createElement('label');box.style.cssText='display:block;font-size:11px;color:#365b49;margin-top:9px';
    const text=document.createElement('span'),out=document.createElement('output'),input=document.createElement('input');
    text.textContent=label+' ';out.textContent=format(value);input.type='range';input.min=min;input.max=max;input.step=step;input.value=value;input.setAttribute('aria-label',label);input.style.cssText='display:block;width:100%;accent-color:#27694e;cursor:ew-resize';
    input.oninput=()=>{out.textContent=format(+input.value);change(+input.value);};box.append(text,out,input);note.before(box);return {input,out,format};
   }
   const angle=slider(fr?'Inclinaison':'Tilt',0,80,1,0,v=>Math.round(v)+'°',v=>{gl.stop();gl.setPitch(v);});
   gl.on('pitch',()=>{angle.input.value=gl.getPitch();angle.out.textContent=angle.format(gl.getPitch());});
   const rotation=slider(fr?'Rotation':'Rotation',0,359,1,0,v=>Math.round(v)+'°',v=>{gl.stop();gl.setBearing(v);});
   const syncRotation=()=>{const bearing=(gl.getBearing()%360+360)%360;rotation.input.value=Math.round(bearing)%360;rotation.out.textContent=rotation.format(bearing%360);directions.forEach((button,i)=>button.setAttribute('aria-pressed',String(Math.abs(((bearing-i*90+540)%360)-180)<.5)));};
   gl.on('rotate',syncRotation);syncRotation();
   tilt.addEventListener('click',()=>{detail.open=true;});
   slider(fr?'Hauteur du relief':'Relief height',1,3,.1,1,v=>'×'+v.toFixed(1),v=>gl.setTerrain({source:'dem',exaggeration:v}));
   const ratio=document.createElement('div');ratio.style.cssText='font-size:10px;color:#6c7c73;margin-top:4px';ratio.textContent=fr?'×1 : sans exagération · ×2 : hauteurs doublées':'×1: no exaggeration · ×2: doubled heights';note.before(ratio);
   if(installerHD)installerHD(gl);
   // The original 2D look: satellite imagery softened by Esri hillshade.
   gl.addSource('atlas-shade',{type:'raster',tiles:['https://server.arcgisonline.com/ArcGIS/rest/services/Elevation/World_Hillshade/MapServer/tile/{z}/{y}/{x}'],tileSize:256,maxzoom:16,attribution:'Esri'});
   gl.addLayer({id:'atlas-shade',type:'raster',source:'atlas-shade',layout:{visibility:'none'},paint:{'raster-opacity':.5}},'white-ocean');
   let atlasOn=false;
   const atlasState=on=>{atlasOn=on;atlas.setAttribute('aria-pressed',String(on));gl.setLayoutProperty('atlas-shade','visibility',on&&ETAT.ombrage?'visible':'none');gl.setLayoutProperty('ombrage-hillshade','visibility',!on&&ETAT.ombrage?'visible':'none');};
   atlas.disabled=false;atlasState(false);
   atlas.onclick=()=>{choisirFond('sat');const radio=document.querySelector('input[name="fond"][value="sat"]');if(radio)radio.checked=true;ETAT.ombrage=true;basculer('ombrage',true);const shade=document.querySelector('input[data-cle="ombrage"]');if(shade)shade.checked=true;atlasState(true);gl.easeTo({pitch:0,bearing:0,duration:700});};
   top.addEventListener('click',()=>atlasState(false));tilt.addEventListener('click',()=>atlasState(false));
   const oldFond=choisirFond,oldToggle=basculer,oldFilter=filtrerSections,oldReset=recadrer;
   choisirFond=k=>{oldFond(k);sync();atlasState(false);};basculer=(k,on)=>{oldToggle(k,on);sync();atlasState(atlasOn);};filtrerSections=()=>{oldFilter();sync();atlasState(atlasOn);};
   recadrer=()=>{if(failed)return oldReset();gl.fitBounds([[-74.55,17.98],[-73.55,18.68]],{padding:25,pitch:0,bearing:0});};
  });
 }catch(e){clearTimeout(timeout);fallback();}
})();
