"""Illustrative feedback system; no fitted coefficients or survey scores."""

from traductions import text as _locale_text
import json


def document(fr=True):
    words = {
        "title": _locale_text("Reboiser : agir sur tout le système" if fr else "Reforestation: act on the whole system"),
        "intro": _locale_text("Réglez les leviers, puis lancez les vagues. Les effets sur la forêt arrivent avec retard." if fr else "Adjust the levers, then start the waves. Forest recovery takes time."),
        "note": _locale_text("Simulation pédagogique : niveaux relatifs, sans prévision locale ni lien avec les scores IRLA. Chaque vague représente une étape, pas une année." if fr else "Educational simulation: relative levels, not a local forecast or IRLA scores. Each wave is a step, not a year."),
        "controls": ["Plantation", "Revenus alternatifs", "Alternatives au bois-énergie", "Gestion des animaux en divagation"] if fr else ["Tree planting", "Alternative livelihoods", "Alternatives to fuelwood", "Management of roaming livestock"],
        "nodes": ["Revenus des ménages", "Prélèvements de bois", "Pression des animaux", "Survie des jeunes arbres", "Couvert forestier", "Sols et ressources"] if fr else ["Household income", "Wood harvesting", "Livestock pressure", "Young tree survival", "Forest cover", "Soils and resources"],
        "alone": _locale_text("Planter seul" if fr else "Planting alone"), "together": _locale_text("Agir ensemble" if fr else "Combined action"),
        "play": _locale_text("Lancer les vagues" if fr else "Start waves"), "pause": "Pause", "step": _locale_text("Une vague" if fr else "One wave"), "reset": _locale_text("Recommencer" if fr else "Reset"),
        "wave": _locale_text("Vague" if fr else "Wave"), "chart": _locale_text("Évolution du couvert forestier · niveau relatif / 100" if fr else "Forest cover over time · relative level / 100"),
        "legend": _locale_text("+ : évolue dans le même sens · − : évolue en sens inverse · pointillés : effet retardé" if fr else "+: moves in the same direction · −: moves in the opposite direction · dashed: delayed effect"),
        "loops": ["Revenus → moins de prélèvements → arbres → sols → revenus : une boucle qui peut renforcer la restauration.", "La plantation augmente les jeunes arbres ; le bois-énergie et les animaux peuvent annuler ce gain.", "À mesure que la forêt se reconstitue, le bois disponible peut relancer les prélèvements : un frein à surveiller."] if fr else ["Income → less harvesting → trees → soils → income: a loop that can reinforce recovery.", "Planting adds young trees; fuelwood harvesting and livestock can cancel that gain.", "As forests recover, available wood can encourage harvesting again: a balancing pressure to watch."],
    }
    return HTML.replace("__WORDS__", json.dumps(words, ensure_ascii=False)).replace("__LANG__", "fr" if fr else "en")


HTML = r'''<!doctype html><html lang="__LANG__"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{box-sizing:border-box}body{margin:0;color:#284d43;font:13px/1.45 Georgia,serif}h2{font-size:18px;margin:0 0 5px}p{margin:5px 0 15px;color:#657b73}.shell{background:#f5f9f6;border-radius:14px;padding:16px;max-width:1100px;margin:0 auto}.layout{display:grid;grid-template-columns:210px 1fr;gap:16px}.controls{background:white;padding:12px;border-radius:12px}label{display:block;margin:10px 0 3px;font-weight:600;font-size:12px}input{width:100%;accent-color:#48896d}output{float:right;color:#527667;font-weight:400}.buttons{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}button{font:inherit;font-size:12px;border:1px solid #bad2c4;background:white;border-radius:8px;padding:6px 10px;color:#245f49;cursor:pointer}button:hover,button:focus-visible{background:#dfede4}button.primary{background:#36775b;color:white}.graph{width:100%;height:auto;max-height:300px;display:block}.node rect{fill:white;stroke:#cbddd2}.node text{fill:#315c4b;font-size:13px}.node .value{font-size:20px;font-weight:700}.edge{fill:none;stroke:#91b2a1;stroke-width:2}.minus{stroke:#c39765}.delayed{stroke-dasharray:6 5}.sign{font-size:19px;fill:#496e5b}.pulse{fill:#276f52}.pulse.negative{fill:#b3783a}.track{fill:none;stroke:#38795b;stroke-width:3}.baseline{fill:none;stroke:#cddbd3;stroke-width:1}#plot{width:100%;height:80px}.note{font-size:12px;margin-top:18px}.legend{font-size:12px}.loops{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:12px}.loops div{font-size:12px;border-top:3px solid #a0bfae;padding-top:10px}#status{font-size:13px;font-weight:600}button:disabled{opacity:.5;cursor:default}@media(max-width:700px){.layout{grid-template-columns:1fr}.shell{padding:14px}.controls{display:grid;grid-template-columns:1fr 1fr;gap:0 18px}.presets{grid-column:1/-1}.loops{grid-template-columns:1fr}}
</style><div class="shell"><h2 id="title"></h2><p id="intro"></p><div class="layout"><div class="controls"><div class="presets buttons"><button id="alone"></button><button id="together"></button></div><div id="sliders"></div></div><div><svg class="graph" viewBox="0 0 740 370" role="img" aria-label="Feedback system"><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10" fill="#91b2a1"/></marker></defs><g id="edges"></g><g id="nodes"></g></svg><div class="legend" id="legend"></div><div class="buttons"><button class="primary" id="play"></button><button id="step"></button><button id="reset"></button><span id="status" aria-live="polite"></span></div><div id="chart"></div><svg id="plot" viewBox="0 0 700 110" role="img"><path class="baseline" d="M30 10V90H690"/><text x="0" y="16" fill="#73877d" font-size="11">100</text><text x="14" y="93" fill="#73877d" font-size="11">0</text><path id="history" class="track"/></svg></div></div><div class="loops" id="loops"></div><p class="note" id="note"></p></div>
<script>
const W=__WORDS__;
for(const id of ['title','intro','note','alone','together','play','step','reset','legend','chart'])document.getElementById(id).textContent=W[id];
document.getElementById('loops').innerHTML=W.loops.map(t=>`<div>${t}</div>`).join('');
const sliders=document.getElementById('sliders');
W.controls.forEach((t,i)=>{sliders.insertAdjacentHTML('beforeend',`<label for="s${i}">${t}<output id="o${i}">0</output></label><input id="s${i}" type="range" min="0" max="100" value="0">`);document.getElementById('s'+i).oninput=e=>{document.getElementById('o'+i).value=e.target.value;};});
const positions=[[15,18],[280,18],[540,18],[280,155],[540,280],[15,280]];
const connections=[['M195 55H280','−',230,45],['M370 92V155','−',380,126],['M630 92Q625 195 460 192','−',542,158],['M460 195Q525 195 575 280','+',514,238],['M540 315H195','+',350,305],['M100 280V92','+',110,190],['M720 280Q755 45 460 48','+',615,110]];
const ns='http://www.w3.org/2000/svg';
connections.forEach(([d,s,x,y],i)=>{document.getElementById('edges').insertAdjacentHTML('beforeend',`<path id="e${i}" class="edge ${s==='−'?'minus':''} ${i>=3?'delayed':''}" d="${d}" marker-end="url(#arrow)"/><text class="sign" x="${x}" y="${y}">${s}</text>`);});
positions.forEach(([x,y],i)=>{document.getElementById('nodes').insertAdjacentHTML('beforeend',`<g class="node" transform="translate(${x} ${y})"><rect width="180" height="74" rx="12"/><text x="90" y="24" text-anchor="middle">${W.nodes[i]}</text><text class="value" id="n${i}" x="90" y="56" text-anchor="middle"></text></g>`);});
let state,history,wave,timer=null;
const clamp=x=>Math.max(0,Math.min(100,x));
function advance(v,u){
 // Relative toy stocks. All updates read the previous state: feedback has delay.
 const [income,wood,animals,survival,forest,soil]=v;
 const [plant,jobs,energy,herding]=u;
 return [clamp(income+.23*(15+.52*jobs+.30*soil-income)),
 clamp(wood+.32*((70-.55*income+.22*forest)*(1-.009*energy)-wood)),
 clamp(animals+.4*(75*(1-.009*herding)-animals)),
 clamp(survival+.38*(Math.max(0,25+.6*plant-.65*wood-.65*animals)-survival)),
 clamp(forest+.09*survival*(1-forest/100)-.035*wood-.025*animals),
 clamp(soil+.12*(forest-soil))];
}
function draw(){state.forEach((n,i)=>document.getElementById('n'+i).textContent=Math.round(n));document.getElementById('status').textContent=W.wave+' '+wave+' / 40';document.getElementById('history').setAttribute('d',history.map((n,i)=>(i?'L':'M')+(30+i*16.5)+' '+(90-n*.8)).join(' '));document.getElementById('step').disabled=wave>=40;document.getElementById('play').disabled=wave>=40;}
function stop(){clearInterval(timer);timer=null;document.getElementById('play').textContent=W.play;}
function tick(){if(wave>=40){stop();return;}state=advance(state,[0,1,2,3].map(i=>+document.getElementById('s'+i).value));wave++;history.push(state[4]);draw();if(!matchMedia('(prefers-reduced-motion: reduce)').matches){connections.forEach((c,i)=>{const circle=document.createElementNS(ns,'circle');circle.setAttribute('r','4');circle.setAttribute('class','pulse '+(c[1]==='−'?'negative':''));const motion=document.createElementNS(ns,'animateMotion');motion.setAttribute('path',c[0]);motion.setAttribute('dur','1.1s');motion.setAttribute('begin','indefinite');circle.appendChild(motion);document.getElementById('edges').appendChild(circle);motion.beginElement();setTimeout(()=>circle.remove(),1150);});}if(wave>=40)stop();}
function reset(){stop();state=[30,60,75,10,30,30];history=[30];wave=0;draw();}
function preset(values){values.forEach((v,i)=>{document.getElementById('s'+i).value=v;document.getElementById('o'+i).value=v;});reset();}
document.getElementById('alone').onclick=()=>preset([85,0,0,0]);document.getElementById('together').onclick=()=>preset([85,80,80,80]);document.getElementById('reset').onclick=reset;document.getElementById('step').onclick=()=>{stop();tick();};document.getElementById('play').onclick=()=>{if(timer){stop();return;}document.getElementById('play').textContent=W.pause;tick();if(wave<40)timer=setInterval(tick,1400);};preset([85,0,0,0]);
</script></html>'''
