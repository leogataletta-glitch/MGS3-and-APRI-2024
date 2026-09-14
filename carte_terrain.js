/* One terrain map with two camera presets; Leaflet remains the fallback. */
(async function(){
 const fr=L_.legend==='Légende';
 const controls=document.createElement('div');controls.className='boutons';
 const top=document.createElement('button'),tilt=document.createElement('button');
 top.textContent=fr?'Vue de dessus':'Top view';tilt.textContent=fr?'Vue relief':'Relief view';
 top.disabled=tilt.disabled=true;controls.append(top,tilt);
 document.querySelector('#panneau .tete').append(controls);
 const note=document.createElement('div');note.setAttribute('role','status');note.style.cssText='font-size:11px;color:#587264;padding-top:6px';
 note.textContent=fr?'Chargement du relief…':'Loading terrain…';controls.after(note);
 const css=document.createElement('link');css.rel='stylesheet';css.href='https://unpkg.com/maplibre-gl@6.9.0/dist/maplibre-gl.css';document.head.append(css);
 const styles=document.createElement('style');styles.textContent='#carte3d{position:absolute;left:0;top:0;bottom:0;right:302px;border-radius:12px;overflow:hidden;visibility:hidden}.maplibregl-popup-content{font:12px system-ui;color:#234c3e}.maplibregl-ctrl-attrib{font-size:10px}#panneau button[aria-pressed="true"]{background:#dceee3;border-color:#62967c;color:#164a35}@media(max-width:620px){#carte3d{right:0;bottom:240px}}';document.head.append(styles);
 const host=document.createElement('div');host.id='carte3d';document.getElementById('carte').after(host);
 let gl,ready=false,failed=false;
 function fallback(){if(failed)return;failed=true;window.apriTerrain=null;host.remove();if(gl)gl.remove();document.getElementById('carte').style.visibility='';carte.invalidateSize();top.disabled=tilt.disabled=true;note.textContent=fr?'Relief indisponible : la carte 2D reste accessible.':'Terrain unavailable: the 2D map remains available.';}
 const timeout=setTimeout(()=>{if(!ready)fallback();},25000);
 try{
  const m=await import('https://unpkg.com/maplibre-gl@6.9.0/dist/maplibre-gl.mjs');
  if(failed)return;
  const raster=(tiles,attribution,maxzoom=19)=>({type:'raster',tiles:[tiles],tileSize:256,attribution,maxzoom});
  gl=new m.Map({container:host,center:[-74.05,18.33],zoom:9,pitch:0,maxPitch:70,maxZoom:18,canvasContextAttributes:{preserveDrawingBuffer:true},
   style:{version:8,sources:{
    sat:raster('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}','Esri, Maxar, Earthstar Geographics'),
    plan:raster('https://tile.openstreetmap.org/{z}/{x}/{y}.png','© OpenStreetMap'),
    relief:raster('https://a.tile.opentopomap.org/{z}/{x}/{y}.png','© OpenTopoMap, © OpenStreetMap',17),
    dem:{type:'raster-dem',tiles:['https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png'],encoding:'terrarium',tileSize:256,maxzoom:15,attribution:'Terrain © Mapzen / AWS Open Data'}
   },layers:[{id:'background',type:'background',paint:{'background-color':'#e8eef0'}},...['sat','plan','relief'].map(id=>({id,type:'raster',source:id,layout:{visibility:id==='sat'?'visible':'none'}}))],terrain:{source:'dem',exaggeration:1}}});
  gl.addControl(new m.NavigationControl({visualizePitch:true}),'top-left');gl.addControl(new m.ScaleControl({unit:'metric'}),'bottom-left');
  gl.getCanvas().addEventListener('webglcontextlost',fallback);
  const fc=features=>({type:'FeatureCollection',features});
  const feature=(geometry,properties={})=>({type:'Feature',geometry,properties});
  const polygons=items=>fc((items||[]).flatMap(o=>(o.a||[]).filter(a=>a.length>2).map(a=>feature({type:'Polygon',coordinates:[[...a,a[0]]]},o.p))));
  const lines=items=>fc((items||[]).filter(o=>o.l?.length>1).map(o=>feature({type:'LineString',coordinates:o.l},o.p)));
  const pointData=key=>fc((D.entretiens||[]).filter(e=>(e[3]==='Montagne'?'pts_m':'pts_l')===key&&new Set([...sectionsChoisies].map(normaliserSection)).has(normaliserSection(e[2]))).map(e=>feature({type:'Point',coordinates:[e[0],e[1]]},{section:e[2],paysage:e[3],numero:e[4]})));
  const ids={};
  function add(key,data,type,paint){if(!gl.getSource(key))gl.addSource(key,{type:'geojson',data});const id=key+'-'+type;gl.addLayer({id,type,source:key,paint});(ids[key]||=[]).push(id);}
  function sync(){if(!ready||failed)return;for(const k of ['sat','plan','relief'])gl.setLayoutProperty(k,'visibility',fondActif===k?'visible':'none');for(const [k,list]of Object.entries(ids))for(const id of list)gl.setLayoutProperty(id,'visibility',(k==='terre'?fondActif==='sobre':!!ETAT[k])?'visible':'none');gl.getSource('sections').setData(polygons((D.sections||[]).filter(o=>sectionsChoisies.has(o.p.section))));for(const k of ['pts_l','pts_m'])gl.getSource(k).setData(pointData(k));}
  gl.on('load',()=>{
   if(failed)return;
   add('terre',polygons(D.terre),'fill',{'fill-color':'#dce2df'});
   gl.addLayer({id:'ombrage-hillshade',type:'hillshade',source:'dem'});ids.ombrage=['ombrage-hillshade'];
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
   gl.on('click',e=>{const hits=gl.queryRenderedFeatures(e.point,{layers:['pts_l-circle','pts_m-circle','sections-fill','villes-circle']});if(!hits.length)return;const p=hits[0].properties,body=document.createElement('div');body.textContent=p.numero?('n° '+p.numero+' · '+p.section+' · '+p.paysage):(p.section||p.nom||'');new m.Popup().setLngLat(e.lngLat).setDOMContent(body).addTo(gl);});
   ready=true;clearTimeout(timeout);window.apriTerrain=gl;sync();
   host.style.visibility='visible';document.getElementById('carte').style.visibility='hidden';
   gl.fitBounds([[-74.55,17.98],[-73.55,18.68]],{padding:25,duration:0});
   top.disabled=tilt.disabled=false;
   const state=()=>{top.setAttribute('aria-pressed',String(gl.getPitch()<1));tilt.setAttribute('aria-pressed',String(gl.getPitch()>=1));};gl.on('moveend',state);state();
   top.onclick=()=>gl.easeTo({pitch:0,bearing:0,duration:700});
   tilt.onclick=()=>gl.easeTo({pitch:60,duration:900});
   note.textContent=fr?'Inclinez avec le clic droit ; sur mobile, glissez deux doigts.':'Right-drag to tilt; on mobile, drag two fingers.';
   const oldFond=choisirFond,oldToggle=basculer,oldFilter=filtrerSections,oldReset=recadrer;
   choisirFond=k=>{oldFond(k);sync();};basculer=(k,on)=>{oldToggle(k,on);sync();};filtrerSections=()=>{oldFilter();sync();};
   recadrer=()=>{if(failed)return oldReset();gl.fitBounds([[-74.55,17.98],[-73.55,18.68]],{padding:25,pitch:0,bearing:0});};
  });
 }catch(e){clearTimeout(timeout);fallback();}
})();
