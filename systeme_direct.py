"""Le système en marche : le schéma du premier onglet, mais qui bouge.

CE QUE CET ÉCRAN AJOUTE AUX QUATRE AUTRES.
Le premier onglet dessine le système et s'arrête là : des pastilles, des
flèches signées, une image fixe. Le quatrième pose une poussée et donne le
résultat une fois tout distribué. Le cinquième range la même propagation en
colonnes de vagues. Aucun des trois ne montre le mouvement lui-même — et
c'est pourtant le mouvement qui explique ce qu'est une boucle : on ne
comprend pas qu'un effet revienne sur son point de départ en lisant un
tableau, on le comprend en voyant l'onde repasser par là.

Ici, le schéma est CELUI DU PREMIER ONGLET — mêmes pastilles, mêmes
positions, mêmes flèches, même variable centrale et même profondeur, prises
dans le même état de session. On pose une variation sur une variable, on
appuie sur Lecture, et des billes partent le long des flèches : vertes quand
elles portent une amélioration, rouges quand elles portent une dégradation,
grosses quand elles portent beaucoup. Quand une bille arrive, la variable
qu'elle atteint monte ou descend, sa jauge se déplace, son chiffre change.
La vague suivante repart de là.

TOUT SE CALCULE DANS LE NAVIGATEUR, ET C'EST OBLIGATOIRE.
Une animation à soixante images par seconde ne peut pas faire un aller-retour
serveur par image. Le module envoie donc une fois le sous-graphe affiché —
positions comprises, poids déjà mis à l'échelle par le moteur — et le
navigateur fait tourner la récurrence vague_{k+1} = A · vague_k, exactement
celle que `boucles_moteur` résout d'un bloc par inversion.

CE QUE L'ÉCRAN NE DIT PAS.
Le rang d'une vague est un ordre de relais, pas un calendrier : rien ici ne
dit qu'une vague dure un mois ou dix ans. Et la propagation s'arrête au bord
du périmètre dessiné : ce qui sort du schéma n'est pas suivi, ce qui est le
prix à payer pour que l'onde reste visible sur une image lisible. La
profondeur se règle dans le premier onglet, et l'effet total, lui, se lit
dans « Tester des interventions ».
"""

import json
import math

import streamlit as st
import streamlit.components.v1 as components

import boucles_moteur as M
import i18n
import systeme_complexe as SX
from i18n import T

ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"
VERT_APRI, VERT, ROUGE, GRIS = "#2a6b3f", "#1a8a4f", "#c33a24", "#8a93a5"
BORD = "#dbe3ec"

TEXTES = {
    "sd_intro": {
        "en": "This is the system from the first tab, running. Pick a "
              "variable, set how much it moves, and press play: the change "
              "travels along the arrows, and every variable it reaches rises "
              "or falls in front of you. Green carries an improvement, red a "
              "degradation, and the bigger the ball the more it carries.",
        "fr": "C'est le système du premier onglet, en marche. Choisissez une "
              "variable, réglez de combien elle bouge, et appuyez sur "
              "Lecture : le changement voyage le long des flèches, et chaque "
              "variable atteinte monte ou descend sous vos yeux. Le vert "
              "porte une amélioration, le rouge une dégradation, et plus la "
              "bille est grosse plus elle porte."},
    "sd_var": {"en": "Variable pushed", "fr": "Variable poussée"},
    "sd_ampleur": {"en": "Change applied", "fr": "Changement appliqué"},
    "sd_lire": {"en": "Play", "fr": "Lecture"},
    "sd_pause": {"en": "Pause", "fr": "Pause"},
    "sd_pas": {"en": "One wave", "fr": "Une vague"},
    "sd_raz": {"en": "Reset", "fr": "Remise à zéro"},
    "sd_vitesse": {"en": "Speed", "fr": "Vitesse"},
    "sd_vague": {"en": "Wave", "fr": "Vague"},
    "sd_distrib": {"en": "of the effect already distributed",
                   "fr": "de l'effet déjà distribué"},
    "sd_leg_h": {"en": "carries an improvement",
                 "fr": "porte une amélioration"},
    "sd_leg_b": {"en": "carries a degradation",
                 "fr": "porte une dégradation"},
    "sd_leg_e": {"en": "score out of 10, and how far it has moved",
                 "fr": "score sur 10, et de combien il a bougé"},
    "sd_fin": {"en": "The wave has died out: everything it could move has "
                     "moved.",
               "fr": "La vague s'est éteinte : tout ce qu'elle pouvait "
                     "déplacer a bougé."},
    "sd_retour": {"en": "The wave came back to its starting variable at wave "
                        "{k}: this system is a loop, not a chain.",
                  "fr": "La vague est revenue sur sa variable de départ à la "
                        "vague {k} : ce système est une boucle, pas une "
                        "chaîne."},
    "sd_non_mesure": {"en": "not measured", "fr": "non mesurée"},
    "sd_perim": {
        "en": "The wave is followed inside the drawn perimeter only: what "
              "leaves the picture is not tracked. Change the central "
              "variable or the depth in the first tab to widen it. The "
              "rank of a wave is an order of relays, not a calendar.",
        "fr": "L'onde n'est suivie qu'à l'intérieur du périmètre dessiné : "
              "ce qui sort de l'image n'est pas suivi. La variable centrale "
              "et la profondeur se règlent dans le premier onglet. Le rang "
              "d'une vague est un ordre de relais, pas un calendrier."},
    "sd_court": {
        "en": "This perimeter has no outgoing link to follow: raise the "
              "depth in the first tab.",
        "fr": "Ce périmètre n'a aucun lien à suivre : augmentez la "
              "profondeur dans le premier onglet."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _lignes(nom, larg=17, maxi=2):
    """Le libellé coupé en lignes courtes, comme dans le schéma fixe."""
    mots, ligne, out = nom.split(), "", []
    for w in mots:
        if len(ligne + " " + w) > larg and ligne:
            out.append(ligne)
            ligne = w
        else:
            ligne = (ligne + " " + w).strip()
    out.append(ligne)
    if len(out) > maxi:
        out = out[:maxi]
        out[-1] = out[-1][:larg - 1] + "…"
    return out


def _donnees(m, centre, prof):
    """Le sous-graphe affiché, positions et poids compris, prêt pour le JS.

    LES POIDS SONT CEUX DU MOTEUR, DÉJÀ MIS À L'ÉCHELLE. Le graphe brut a un
    rayon spectral proche de 1 : propagé tel quel, une poussée de deux points
    en produirait quinze ailleurs. La mise à l'échelle appartient au moteur ;
    on la lui demande plutôt que de la refaire ici.
    """
    rang, aretes = SX._voisinage(m, centre, prof)
    pos, larg, haut = SX._positions(rang, centre)
    etat = M.etat_courant(m["g"], m["par_ligne"], "Total")
    A, ids, idx = m["A"], m["ids"], m["idx"]

    noeuds = []
    for n in sorted(pos, key=lambda i: m["noms"].get(i, i)):
        x, y = pos[n]
        v = etat.get(n)
        noeuds.append({"id": n, "nom": m["noms"].get(n, n),
                       "lig": _lignes(m["noms"].get(n, n)),
                       "x": round(x, 1), "y": round(y, 1),
                       "s": None if v is None else round(float(v), 2),
                       "r": rang.get(n, 9), "c": n == centre})
    liens = []
    for a in aretes:
        de, vers = a["de"], a["vers"]
        if de not in pos or vers not in pos or de not in idx or vers not in idx:
            continue
        liens.append({"de": de, "vers": vers,
                      "w": round(float(A[idx[vers], idx[de]]), 6),
                      "sg": int(a.get("signe") or 1)})
    xs = [n["x"] for n in noeuds]
    ys = [n["y"] for n in noeuds]
    vb = [min(xs) - 100, min(ys) - 48,
          max(max(xs) - min(xs) + 200, 320), max(max(ys) - min(ys) + 96, 220)]
    return {"noeuds": noeuds, "liens": liens, "vb": vb,
            "centre": centre, "larg": larg, "haut": haut}


# ===================================================================== le HTML
# LE GABARIT EST UNE CHAÎNE, PAS UN f-string : il est plein d'accolades JS, et
# les doubler toutes rendrait le code illisible pour gagner zéro.
GABARIT = r"""<!doctype html><html><head><meta charset="utf-8">
<style>
  html,body{height:100%;margin:0;font-family:Inter,system-ui,-apple-system,
    "Segoe UI",sans-serif;color:#101728;background:#fff}
  #tout{display:flex;flex-direction:column;height:100%}
  #barre{display:flex;align-items:center;gap:14px;flex-wrap:wrap;
    padding:11px 14px;border:1px solid #e3eaf3;border-radius:13px;
    background:#f8fafc}
  .ch{display:flex;flex-direction:column;gap:3px}
  .ch label{font-size:10px;font-weight:700;letter-spacing:.07em;
    text-transform:uppercase;color:#6b7590}
  select,input[type=range]{font:inherit;font-size:13px}
  select{padding:5px 7px;border:1px solid #dbe3ec;border-radius:8px;
    background:#fff;color:#101728;max-width:280px}
  button{font:inherit;font-size:13px;font-weight:700;padding:7px 15px;
    border-radius:9px;border:1px solid #dbe3ec;background:#fff;
    color:#3c4761;cursor:pointer}
  button.p{background:#2a6b3f;border-color:#2a6b3f;color:#fff}
  button:hover{filter:brightness(.97)}
  #compteur{margin-left:auto;text-align:right;line-height:1.25}
  #kv{font-size:23px;font-weight:800;font-variant-numeric:tabular-nums}
  #kl{font-size:10px;font-weight:700;letter-spacing:.07em;
    text-transform:uppercase;color:#6b7590}
  #kd{font-size:11.5px;color:#6b7590;font-variant-numeric:tabular-nums}
  #scene{flex:1;min-height:0;position:relative}
  svg{width:100%;height:100%;display:block}
  #bas{display:flex;align-items:center;gap:18px;flex-wrap:wrap;
    padding:7px 3px 0;font-size:11.5px;color:#6b7590}
  .lg{display:flex;align-items:center;gap:6px}
  .pt{width:11px;height:11px;border-radius:50%}
  #mot{font-size:12.5px;color:#3c4761;min-height:17px;padding:3px 3px 0}
  text{font-family:Inter,system-ui,sans-serif}
</style></head><body><div id="tout">
<div id="barre">
  <div class="ch"><label>__L_VAR__</label>
    <select id="src"></select></div>
  <div class="ch"><label>__L_AMP__ · <span id="ampv">+1,0</span></label>
    <input id="amp" type="range" min="-3" max="3" step="0.5" value="1"
           style="width:150px"></div>
  <button id="lire" class="p">__L_LIRE__</button>
  <button id="pas">__L_PAS__</button>
  <button id="raz">__L_RAZ__</button>
  <div class="ch"><label>__L_VIT__</label>
    <select id="vit">
      <option value="1.7">0,5×</option>
      <option value="1" selected>1×</option>
      <option value="0.55">2×</option>
    </select></div>
  <div id="compteur"><div id="kl">__L_VAGUE__</div>
    <div id="kv">0</div><div id="kd">0 % __L_DIS__</div></div>
</div>
<div id="scene"><svg id="g" preserveAspectRatio="xMidYMid meet"></svg></div>
<div id="mot"></div>
<div id="bas">
  <span class="lg"><span class="pt" style="background:#1a8a4f"></span>
    __L_LH__</span>
  <span class="lg"><span class="pt" style="background:#c33a24"></span>
    __L_LB__</span>
  <span class="lg"><span style="display:inline-block;width:26px;height:5px;
    border-radius:3px;background:#cfe0d6"></span> __L_LE__</span>
</div>
</div>
<script>
const D = __DONNEES__, L = __LIBELLES__;
const NO = D.noeuds, LI = D.liens;
const IX = {}; NO.forEach((n,i)=>IX[n.id]=i);
const SEUIL = 0.004;          /* sous 4 millièmes de point, plus rien ne bouge */
const KMAX = 40;
const VERT = "#1a8a4f", ROUGE = "#c33a24", APRI = "#2a6b3f";

/* ---------- la géométrie, celle du schéma fixe ------------------------- */
function bords(a, b){
  const dx = b.x-a.x, dy = b.y-a.y, d = Math.hypot(dx,dy) || 1;
  const rx = 40/d, ry = 22/d;
  const x1 = a.x+dx*rx, y1 = a.y+dy*ry, x2 = b.x-dx*rx, y2 = b.y-dy*ry;
  return {x1,y1,x2,y2,
          mx:(x1+x2)/2-dy*0.09, my:(y1+y2)/2+dx*0.09};
}
const NS = "http://www.w3.org/2000/svg";
function el(n, at){ const e = document.createElementNS(NS,n);
  for (const k in at) e.setAttribute(k, at[k]); return e; }

/* ---------- le dessin, une fois ---------------------------------------- */
const svg = document.getElementById("g");
svg.setAttribute("viewBox", D.vb.join(" "));
const defs = el("defs");
for (const [id,c] of [["fv",VERT],["fr",ROUGE]]){
  const mk = el("marker",{id:id,viewBox:"0 0 10 10",refX:"9",refY:"5",
    markerWidth:"5",markerHeight:"5",orient:"auto-start-reverse"});
  mk.appendChild(el("path",{d:"M0,1 L9,5 L0,9 z",fill:c}));
  defs.appendChild(mk);
}
svg.appendChild(defs);
const gLiens = el("g"), gBilles = el("g"), gNoeuds = el("g");
svg.appendChild(gLiens); svg.appendChild(gNoeuds); svg.appendChild(gBilles);

const traits = LI.map(l => {
  const a = NO[IX[l.de]], b = NO[IX[l.vers]], g = bords(a,b);
  const p = el("path",{d:`M${g.x1},${g.y1} Q${g.mx},${g.my} ${g.x2},${g.y2}`,
    fill:"none", stroke: l.sg>0?VERT:ROUGE, "stroke-width":"1.5",
    opacity:"0.34", "marker-end":`url(#${l.sg>0?"fv":"fr"})`});
  gLiens.appendChild(p);
  const t = el("text",{x:g.mx, y:g.my, "font-size":"12","font-weight":"700",
    fill: l.sg>0?VERT:ROUGE, opacity:"0.34","text-anchor":"middle"});
  t.textContent = l.sg>0 ? "+" : "−";
  gLiens.appendChild(t);
  return p;
});

/* Les pastilles : le libellé, le score courant, une jauge sur 10. */
const vues = NO.map(n => {
  const h = 15 + 13*n.lig.length + 19;
  const g = el("g");
  const r = el("rect",{x:n.x-76, y:n.y-h/2, width:152, height:h, rx:9,
    fill: n.c ? APRI : (n.r===1 ? "#eef3f0" : "#f6f8fb"),
    stroke: n.c ? APRI : "#dbe3ec", "stroke-width":"1"});
  g.appendChild(r);
  let y0 = n.y - h/2 + 14;
  n.lig.forEach((t,i)=>{
    const e = el("text",{x:n.x, y:y0+i*13, "font-size":"10.5",
      "text-anchor":"middle", fill: n.c ? "#fff" : "#101728",
      "font-weight": n.c ? 700 : 400});
    e.textContent = t; g.appendChild(e);
  });
  const yb = n.y - h/2 + 15 + 13*n.lig.length;
  const jf = el("rect",{x:n.x-56, y:yb, width:112, height:5, rx:2.5,
    fill: n.c ? "rgba(255,255,255,.28)" : "#e6ebf2"});
  const jv = el("rect",{x:n.x-56, y:yb, width:0, height:5, rx:2.5,
    fill: n.c ? "#cfe8d8" : "#b9d3c2"});
  g.appendChild(jf); g.appendChild(jv);
  const val = el("text",{x:n.x, y:yb+15, "font-size":"10.5",
    "text-anchor":"middle", "font-weight":"700",
    fill: n.c ? "#fff" : "#3c4761"});
  g.appendChild(val);
  gNoeuds.appendChild(g);
  return {n, rect:r, jauge:jv, val, h, yb};
});

/* ---------- l'état de la propagation ----------------------------------- */
let src = D.centre, amp = 1, vitesse = 1;
let vague = new Float64Array(NO.length);
let cum = new Float64Array(NO.length);
let total = 1, k = 0, joue = false, anim = null, retour = 0;

function totalAbsolu(depart, a){
  let v = new Float64Array(NO.length), c = new Float64Array(NO.length);
  v[IX[depart]] = a;
  for (let i=0;i<200;i++){
    const nv = new Float64Array(NO.length);
    for (const l of LI) nv[IX[l.vers]] += l.w * v[IX[l.de]];
    let s = 0;
    for (let j=0;j<NO.length;j++){ c[j] += nv[j]; s += Math.abs(nv[j]); }
    v = nv;
    if (s < 1e-9) break;
  }
  let t = 0; for (let j=0;j<NO.length;j++) t += Math.abs(c[j]);
  return t;
}

function fmt(v, d){
  const s = (v>=0 && d ? "+" : "") + v.toFixed(d ? 2 : 1);
  return s.replace(".", "__VIRG__");
}

function peindre(){
  for (const u of vues){
    const i = IX[u.n.id];
    const bouge = cum[i] + (u.n.id === src ? amp : 0);
    const base = u.n.s;
    if (base === null){
      u.val.textContent = Math.abs(bouge) < SEUIL ? L.nm : fmt(bouge, 1);
      u.jauge.setAttribute("width", 0);
    } else {
      const v = Math.max(0, Math.min(10, base + bouge));
      u.jauge.setAttribute("width", 112*v/10);
      u.val.textContent = fmt(v, 0) + (Math.abs(bouge) < SEUIL
        ? "" : "  " + fmt(bouge, 1));
    }
    const c = Math.abs(bouge) < SEUIL ? null : (bouge > 0 ? VERT : ROUGE);
    u.val.setAttribute("fill", c ? (u.n.c ? "#fff" : c)
                                 : (u.n.c ? "#fff" : "#3c4761"));
    u.jauge.setAttribute("fill", c ? c : (u.n.c ? "#cfe8d8" : "#b9d3c2"));
    u.rect.setAttribute("stroke", c && !u.n.c ? c : (u.n.c ? APRI : "#dbe3ec"));
    u.rect.setAttribute("stroke-width", c && !u.n.c ? 1.8 : 1);
  }
  let d = 0; for (let j=0;j<NO.length;j++) d += Math.abs(cum[j]);
  document.getElementById("kv").textContent = k;
  document.getElementById("kd").textContent =
    Math.round(100*Math.min(1, total ? d/total : 0)) + " % " + L.dis;
}

function remise(){
  arret();
  k = 0; retour = 0;
  cum = new Float64Array(NO.length);
  vague = new Float64Array(NO.length);
  vague[IX[src]] = amp;
  total = totalAbsolu(src, amp) || 1;
  gBilles.innerHTML = "";
  traits.forEach(p => { p.setAttribute("opacity", .34);
                        p.setAttribute("stroke-width", 1.5); });
  document.getElementById("mot").textContent = "";
  peindre();
}

/* ---------- une vague : les billes partent, puis les scores bougent ---- */
function vaguesuivante(apres){
  const flux = LI.map(l => l.w * vague[IX[l.de]]);
  const suivante = new Float64Array(NO.length);
  LI.forEach((l,i) => { suivante[IX[l.vers]] += flux[i]; });
  let bouge = 0;
  for (let j=0;j<NO.length;j++) bouge += Math.abs(suivante[j]);
  if (bouge < SEUIL){
    document.getElementById("mot").textContent = L.fin;
    arret(); if (apres) apres(false); return;
  }
  k += 1;
  const duree = 950*vitesse, part = 0.82;
  const actifs = [];
  LI.forEach((l,i) => {
    if (Math.abs(flux[i]) < SEUIL/3) return;
    actifs.push(i);
    const p = traits[i];
    p.setAttribute("opacity", 1);
    p.setAttribute("stroke-width", 1.5 + 3.2*Math.min(1, Math.abs(flux[i])/1.2));
    const b = el("circle",{r: 3.2 + 4.4*Math.min(1, Math.abs(flux[i])/1.2),
      fill: flux[i] > 0 ? VERT : ROUGE, opacity:"0.95"});
    gBilles.appendChild(b);
    actifs[actifs.length-1] = {i, p, b, l: p.getTotalLength()};
  });
  const t0 = performance.now();
  const avant = cum.slice();
  function pas(t){
    const u = Math.min(1, (t - t0)/duree);
    const uv = Math.min(1, u/part);
    for (const a of actifs){
      const pt = a.p.getPointAtLength(a.l*uv);
      a.b.setAttribute("cx", pt.x); a.b.setAttribute("cy", pt.y);
      a.b.setAttribute("opacity", uv > 0.97 ? 0 : 0.95);
    }
    const ua = u <= part ? 0 : (u - part)/(1 - part);
    for (let j=0;j<NO.length;j++) cum[j] = avant[j] + suivante[j]*ua;
    peindre();
    if (u < 1){ anim = requestAnimationFrame(pas); return; }
    gBilles.innerHTML = "";
    traits.forEach(p => { p.setAttribute("opacity", .34);
                          p.setAttribute("stroke-width", 1.5); });
    if (!retour && k >= 2 && Math.abs(suivante[IX[src]]) > SEUIL){
      retour = k;
      document.getElementById("mot").textContent =
        L.ret.replace("{k}", k);
    }
    vague = suivante;
    anim = null;
    if (apres) apres(true);
  }
  anim = requestAnimationFrame(pas);
}

function arret(){
  joue = false;
  if (anim){ cancelAnimationFrame(anim); anim = null; }
  document.getElementById("lire").textContent = L.lire;
  document.getElementById("lire").classList.add("p");
}
function boucler(ok){
  if (!joue) return;
  if (!ok || k >= KMAX){ arret(); return; }
  setTimeout(()=>{ if (joue) vaguesuivante(boucler); }, 120*vitesse);
}

/* ---------- les commandes ---------------------------------------------- */
const sel = document.getElementById("src");
NO.slice().sort((a,b)=>a.nom.localeCompare(b.nom)).forEach(n => {
  const o = document.createElement("option");
  o.value = n.id; o.textContent = n.nom; sel.appendChild(o);
});
sel.value = src;
sel.onchange = () => { src = sel.value; remise(); };
const ia = document.getElementById("amp");
ia.oninput = () => {
  amp = parseFloat(ia.value) || 0;
  document.getElementById("ampv").textContent = fmt(amp, 1);
  remise();
};
document.getElementById("vit").onchange = e => { vitesse = parseFloat(e.target.value); };
document.getElementById("raz").onclick = remise;
document.getElementById("pas").onclick = () => { arret(); vaguesuivante(null); };
document.getElementById("lire").onclick = () => {
  if (joue){ arret(); return; }
  if (anim) return;
  joue = true;
  document.getElementById("lire").textContent = L.pause;
  document.getElementById("lire").classList.remove("p");
  vaguesuivante(boucler);
};

document.getElementById("ampv").textContent = fmt(amp, 1);
remise();
</script></body></html>"""


def _html(d, lang):
    lib = {"lire": T("sd_lire"), "pause": T("sd_pause"), "fin": T("sd_fin"),
           "ret": T("sd_retour"), "nm": T("sd_non_mesure"),
           "dis": T("sd_distrib")}
    return (GABARIT
            .replace("__DONNEES__", json.dumps(d, ensure_ascii=False,
                                               separators=(",", ":")))
            .replace("__LIBELLES__", json.dumps(lib, ensure_ascii=False))
            .replace("__VIRG__", "," if lang == "fr" else ".")
            .replace("__L_VAR__", _e(T("sd_var")))
            .replace("__L_AMP__", _e(T("sd_ampleur")))
            .replace("__L_LIRE__", _e(T("sd_lire")))
            .replace("__L_PAS__", _e(T("sd_pas")))
            .replace("__L_RAZ__", _e(T("sd_raz")))
            .replace("__L_VIT__", _e(T("sd_vitesse")))
            .replace("__L_VAGUE__", _e(T("sd_vague")))
            .replace("__L_DIS__", _e(T("sd_distrib")))
            .replace("__L_LH__", _e(T("sd_leg_h")))
            .replace("__L_LB__", _e(T("sd_leg_b")))
            .replace("__L_LE__", _e(T("sd_leg_e"))))


def render():
    """Le schéma du premier onglet, mais qui tourne."""
    lang = i18n.get_lang()
    m = SX._modele(lang)
    st.markdown(SX.STYLE, unsafe_allow_html=True)
    s = SX._systeme(m, "d")
    d = _donnees(m, s["centre"], s["prof"])
    if not d["liens"]:
        st.info(T("sd_court"))
        return

    st.markdown(
        f'<div style="background:#fff;border:1px solid #e3eaf3;border-left:5px '
        f'solid {VERT_APRI};border-radius:14px;padding:12px 16px;'
        f'font-size:14px;color:{ENCRE2};line-height:1.6;margin:2px 0 8px;'
        f'max-width:96ch">{T("sd_intro")}</div>', unsafe_allow_html=True)

    # LA HAUTEUR SUIT LE DESSIN. Un périmètre de quatre pastilles n'a pas
    # besoin de neuf cents pixels, et un périmètre de vingt-six ne tient pas
    # dans six cents : l'iframe est taillée sur le rapport de la boîte.
    haut = int(max(560, min(940, 1180 * d["vb"][3] / max(d["vb"][2], 1) + 210)))
    components.html(_html(d, lang), height=haut, scrolling=False)
    st.caption(T("sd_perim"))
