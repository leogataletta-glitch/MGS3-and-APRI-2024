/* Horizontal measurements on a sphere; elevation is not accumulated. */
function mesureDistance(points){
 const rad=Math.PI/180,R=6371008.8;let total=0;
 for(let i=1;i<points.length;i++){
  const [x,y]=points[i-1],[u,v]=points[i],a=Math.sin((v-y)*rad/2)**2+Math.cos(y*rad)*Math.cos(v*rad)*Math.sin((u-x)*rad/2)**2;
  total+=2*R*Math.asin(Math.sqrt(Math.min(1,a)));
 }return total;
}
function mesureAire(points){
 if(points.length<3)return 0;
 const rad=Math.PI/180,R=6371008.8;let sum=0;
 for(let i=0;i<points.length;i++){
  const a=points[i],b=points[(i+1)%points.length];let dx=(b[0]-a[0])*rad;
  dx=((dx+Math.PI)%(2*Math.PI)+2*Math.PI)%(2*Math.PI)-Math.PI;
  sum+=dx*(2+Math.sin(a[1]*rad)+Math.sin(b[1]*rad));
 }const area=Math.abs(sum)*R*R/2;return Math.min(area,4*Math.PI*R*R-area);
}
(function(){
 const fr=L_.legend==='Légende';let mode='',points=[],drawing=false,gl=null;
 const box=document.createElement('div');box.style.cssText='padding:8px 10px;border-bottom:1px solid #e3ebe6;font:12px/1.5 system-ui;color:#315d4b';
 const title=document.createElement('strong');title.textContent=fr?'Mesurer sur la carte':'Measure on the map';box.append(title);
 const row=document.createElement('div');row.className='boutons';row.style.flexWrap='wrap';box.append(row);
 const result=document.createElement('div');result.setAttribute('role','status');box.append(result);
 const help=document.createElement('small');help.textContent=fr?'Cliquez pour placer les sommets, puis Terminer. Mesures horizontales approximatives ; le relief n’est pas pris en compte.':'Click to place vertices, then Finish. Approximate horizontal measurements; terrain slopes are not included.';box.append(help);
 document.querySelector('#panneau .tete').after(box);
 const leaf=L.layerGroup().addTo(carte),renderer=L.canvas();
 const fmt=n=>n.toLocaleString(fr?'fr-FR':'en-US',{maximumFractionDigits:2});
 function text(){if(!points.length)return '';
  if(mode==='area')return points.length<3?(fr?'Au moins 3 points':'At least 3 points'):((fr?'Surface : ':'Area: ')+fmt(mesureAire(points))+' m² · '+fmt(mesureAire(points)/10000)+' ha'+(mesureAire(points)>=1e6?' · '+fmt(mesureAire(points)/1e6)+' km²':''));
  const d=mesureDistance(points);return (fr?'Distance : ':'Distance: ')+(d>=1000?fmt(d/1000)+' km':fmt(d)+' m');
 }
 function data(){const features=points.map(p=>({type:'Feature',properties:{},geometry:{type:'Point',coordinates:p}}));
  if(points.length>1)features.push({type:'Feature',properties:{},geometry:{type:'LineString',coordinates:mode==='area'&&points.length>2?[...points,points[0]]:points}});
  if(mode==='area'&&points.length>2)features.push({type:'Feature',properties:{},geometry:{type:'Polygon',coordinates:[[...points,points[0]]]}});
  return {type:'FeatureCollection',features};
 }
 function paint(){result.textContent=text();undo.disabled=!points.length;finish.disabled=!drawing||points.length<(mode==='area'?3:2);
  distance.setAttribute('aria-pressed',String(mode==='distance'));area.setAttribute('aria-pressed',String(mode==='area'));
  if(gl)gl.getSource('measurement')?.setData(data());
  leaf.clearLayers();if(!gl){const coords=points.map(p=>[p[1],p[0]]),style={color:'#ba6522',weight:3,renderer};
   if(points.length>1)(mode==='area'&&points.length>2?L.polygon(coords,{...style,fillOpacity:.15}):L.polyline(coords,style)).addTo(leaf);
   coords.forEach(p=>L.circleMarker(p,{...style,radius:4,fillColor:'white',fillOpacity:1}).addTo(leaf));
  }
 }
 function cursor(){carte.getContainer().style.cursor=drawing?'crosshair':'';if(gl)gl.getCanvas().style.cursor=drawing?'crosshair':'';}
 function button(label,fn){const b=document.createElement('button');b.textContent=label;b.onclick=fn;row.append(b);return b;}
 function start(kind){mode=kind;points=[];drawing=true;carte.closePopup();if(gl)document.querySelectorAll('.maplibregl-popup').forEach(p=>p.remove());cursor();paint();}
 const distance=button(fr?'Distance':'Distance',()=>start('distance'));
 const area=button(fr?'Surface':'Area',()=>start('area'));
 const undo=button(fr?'Annuler le point':'Undo point',()=>{points.pop();paint();});
 const finish=button(fr?'Terminer':'Finish',()=>{drawing=false;cursor();paint();});
 button(fr?'Effacer':'Clear',()=>{points=[];drawing=false;mode='';cursor();paint();});
 function add(p){if(!drawing)return;const last=points.at(-1);if(last&&mesureDistance([last,p])<.01)return;points.push(p);paint();}
 carte.on('click',e=>{if(!gl)add([e.latlng.lng,e.latlng.lat]);});
 carte.on('popupopen',()=>{if(drawing)carte.closePopup();});
 window.apriMeasure={active:()=>drawing,text,install(map){
   gl=map;leaf.clearLayers();gl.addSource('measurement',{type:'geojson',data:data()});
   gl.addLayer({id:'measurement-area',type:'fill',source:'measurement',filter:['==',['geometry-type'],'Polygon'],paint:{'fill-color':'#ba6522','fill-opacity':.15}});
   gl.addLayer({id:'measurement-line',type:'line',source:'measurement',filter:['==',['geometry-type'],'LineString'],paint:{'line-color':'#ba6522','line-width':3}});
   gl.addLayer({id:'measurement-points',type:'circle',source:'measurement',filter:['==',['geometry-type'],'Point'],paint:{'circle-radius':4,'circle-color':'white','circle-stroke-color':'#ba6522','circle-stroke-width':2}});
   gl.on('click',e=>{const p=gl.unproject(e.point);add([p.lng,p.lat]);});cursor();paint();
 }};paint();
})();
