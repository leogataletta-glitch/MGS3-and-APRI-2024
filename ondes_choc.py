"""Ondes de choc — la propagation vague par vague, et non plus d'un bloc.

CE QUE CETTE PAGE AJOUTE À « BOUCLES DE RÉTROACTION »

L'autre onglet répond à « où finit-on ? » : il pose une variation sur un nœud
et affiche l'effet TOTAL, une fois tout distribué. C'est le bon chiffre pour
décider, et c'est un chiffre sans temps — on ne voit ni par où l'effet est
passé, ni combien de relais il a fallu, ni ce qui revient au point de départ.

Celui-ci répond à « comment y arrive-t-on ? ». Le choc part d'un nœud, atteint
ses voisins directs à la première vague, les voisins de ses voisins à la
deuxième, et ainsi de suite jusqu'à extinction. On voit l'onde traverser le
système, colonne après colonne, et l'on voit le moment où elle revient sur ses
pas : c'est là que le système cesse d'être une chaîne et devient une boucle.

LA MÉCANIQUE EST CELLE DU MOTEUR, PAS UNE AUTRE

    vague₀ = le choc posé
    vague_{k+1} = A · vague_k
    effet cumulé après K vagues = Σ_{k=1..K} vague_k

`boucles_moteur` résout la somme complète par inversion — (I − A)⁻¹ · e₀ − e₀ —
et c'est exactement la limite de cette suite. Les deux disent donc la même
chose ; la page affiche d'ailleurs, à chaque vague, la PART de l'effet total
déjà distribuée. Quand elle atteint 99 %, l'onde est éteinte. C'est aussi la
démonstration visible de ce que dit le moteur : une troncature à trois vagues
laisserait un tiers de l'effet dans la nature.

TOUT SE CALCULE DANS LE NAVIGATEUR, ET C'EST DÉLIBÉRÉ

Quarante-cinq nœuds, soixante-six arêtes : un produit matrice-vecteur coûte
quelques microsecondes. Passer par le serveur à chaque vague ferait clignoter
la page une fois par seconde et rendrait l'animation impossible. Le module
envoie donc le graphe une fois, mis à l'échelle par le moteur — la mise à
l'échelle reste au seul endroit qui doit la connaître — et le navigateur fait
tourner l'onde.

CE QUE LA PAGE NE DIT PAS

Ce n'est pas une prévision. Les forces sont posées par le cadre IRLA et la
littérature, pas estimées sur l'enquête ; le rang des vagues n'est pas un
calendrier — rien ici ne dit qu'une vague dure un mois ou dix ans. C'est
l'ordre des relais, pas leur durée.
"""

import json

import streamlit as st
import streamlit.components.v1 as components

import boucles_moteur as M
import i18n
from i18n import T

ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"
BORD, GRILLE = "#e3eaf3", "#eef2f7"
HAUSSE, BAISSE, NEUTRE = "#1a8a4f", "#c33a24", "#c8d0dc"

# Une teinte par dimension, pour la pastille du nœud seulement. Elle dit à
# quelle famille appartient le nœud ; elle ne code aucune grandeur — la
# grandeur, c'est le remplissage vert ou rouge.
COUL_DIM = {"dim1": "#2166ac", "dim2": "#6a51a3", "dim3": "#1a8a4f",
            "dim4": "#d1730c", "dim5": "#b5451f", "dim6": "#0f7b8a"}

TEXTES = {
    "oc_titre": {"en": "Shock waves", "fr": "Ondes de choc"},
    "oc_sous": {"en": "How a shock travels through the system, wave by wave",
                "fr": "Comment un choc traverse le système, vague par vague"},
    "oc_intro": {
        "en": "Pick a node, set the shock, and press play. Wave 1 is the "
              "direct neighbours, wave 2 their neighbours, and so on until "
              "the wave dies out. The share of the total effect already "
              "distributed is shown at each step: this is the same "
              "propagation as the feedback-loop tab, shown in slow motion "
              "instead of all at once.",
        "fr": "Choisissez un nœud, réglez le choc, appuyez sur lecture. La "
              "vague 1, ce sont les voisins directs ; la vague 2, leurs "
              "voisins ; et ainsi de suite jusqu'à extinction. La part de "
              "l'effet total déjà distribuée est affichée à chaque pas : "
              "c'est la propagation de l'onglet des boucles, montrée au "
              "ralenti au lieu d'être donnée d'un bloc."},
    "oc_avert": {
        "en": "Wave rank is an order of relays, not a calendar. Nothing here "
              "says a wave takes a month or a decade. The link strengths come "
              "from the IRLA framework and the literature, not from the "
              "survey: this is a scenario, not a forecast.",
        "fr": "Le rang d'une vague est un ordre de relais, pas un calendrier. "
              "Rien ici ne dit qu'une vague dure un mois ou dix ans. Les "
              "forces des liens viennent du cadre IRLA et de la littérature, "
              "pas de l'enquête : c'est un scénario, pas une prévision."},

    # --- commandes
    "oc_noeud": {"en": "Shocked node", "fr": "Nœud choqué"},
    "oc_ampleur": {"en": "Shock", "fr": "Choc"},
    "oc_points": {"en": "points", "fr": "points"},
    "oc_lire": {"en": "Play", "fr": "Lecture"},
    "oc_pause": {"en": "Pause", "fr": "Pause"},
    "oc_pas": {"en": "Step", "fr": "Pas à pas"},
    "oc_zero": {"en": "Reset", "fr": "Revenir au départ"},
    "oc_vague": {"en": "Wave", "fr": "Vague"},
    "oc_distribue": {"en": "of the total effect distributed",
                     "fr": "de l'effet total distribué"},

    # --- lecture
    "oc_depart": {"en": "Shock", "fr": "Choc"},
    "oc_col": {"en": "wave", "fr": "vague"},
    "oc_col_plus": {"en": "wave 6 and beyond", "fr": "vague 6 et au-delà"},
    "oc_hors": {
        "en": "{n} of the {t} nodes are never reached by this shock: no "
              "chain of links leads from it to them.",
        "fr": "{n} des {t} nœuds ne sont jamais atteints par ce choc : "
              "aucune chaîne de liens n'y mène."},
    "oc_retour_t": {"en": "The wave comes back", "fr": "La vague revient"},
    "oc_retour": {
        "en": "At wave {k} the shock reaches its own starting node again, "
              "{sens} it. The system is not a chain here, it is a loop.",
        "fr": "À la vague {k}, le choc atteint de nouveau son point de "
              "départ, et il l'{sens}. Le système n'est pas une chaîne ici, "
              "c'est une boucle."},
    "oc_amplifie": {"en": "amplifying", "fr": "amplifie"},
    "oc_attenue": {"en": "damping", "fr": "atténue"},
    "oc_sans_retour": {
        "en": "No wave comes back to the starting node: from here the model "
              "is a chain, not a loop.",
        "fr": "Aucune vague ne revient au point de départ : vu d'ici, le "
              "modèle est une chaîne, pas une boucle."},
    "oc_mouv_t": {"en": "Moved most on this wave",
                  "fr": "Ce que cette vague déplace le plus"},
    "oc_cumul_t": {"en": "Cumulative effect so far",
                   "fr": "Effet cumulé à ce stade"},
    "oc_rien": {"en": "Nothing moves any more: the wave is spent.",
                "fr": "Plus rien ne bouge : l'onde est éteinte."},
    "oc_leg_h": {"en": "improves", "fr": "améliore"},
    "oc_leg_b": {"en": "degrades", "fr": "dégrade"},
    "oc_leg_r": {"en": "return edge (loop)", "fr": "lien de retour (boucle)"},
    "oc_unite": {"en": "points of score (0–10)", "fr": "points de score (0-10)"},
    "oc_absent": {"en": "Causal graph unavailable.",
                  "fr": "Le graphe causal n'est pas disponible."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


@st.cache_data(show_spinner=False)
def _graphe(lang):
    """Le graphe prêt pour le navigateur, dans la langue demandée.

    LA LANGUE EST UN ARGUMENT DE CACHE, ET CE N'EST PAS DÉCORATIF : une
    fonction cachée qui lirait la langue à l'intérieur figerait à jamais la
    première affichée, et l'anglais s'installerait au milieu de la page
    française sans que rien ne le signale.

    Les forces sont celles du moteur, MISES À L'ÉCHELLE PAR LUI. Le graphe brut
    a un rayon spectral de 0,98 : propagé tel quel, une variation de deux
    points en produirait quinze ailleurs. La mise à l'échelle appartient au
    moteur, pas à l'affichage ; on la lui demande plutôt que de la refaire.
    """
    g = M.charger()
    if not g or not g.get("noeuds"):
        return None
    A, ids, idx = M.matrice(g)
    noeuds = [{"id": n["id"], "nom": n.get(lang) or n.get("fr") or n["id"],
               "dim": n.get("dim", "")} for n in g["noeuds"]]
    aretes = []
    for a in g["aretes"]:
        if a["de"] in idx and a["vers"] in idx:
            aretes.append({"de": a["de"], "vers": a["vers"],
                           "w": round(float(A[idx[a["vers"]], idx[a["de"]]]),
                                      6)})
    return {"noeuds": noeuds, "aretes": aretes,
            "dims": {d: T(d) for d in sorted(COUL_DIM)}}


# Le nœud de départ par défaut : le couvert forestier. C'est le nœud dont le
# site raconte déjà l'histoire — 71 % de la perte de vingt-cinq ans en trois
# ans — et c'est le meilleur exemple d'un choc qui ne s'arrête pas aux arbres.
DEPART = "foret"

GABARIT = r"""<!doctype html><html><head><meta charset="utf-8">
<style>
 *{box-sizing:border-box}
 body{margin:0;font-family:Inter,system-ui,-apple-system,'Segoe UI',sans-serif;
      color:#101728;background:#fff}
 .barre{display:flex;flex-wrap:wrap;align-items:center;gap:14px;
        border:1px solid #e3eaf3;border-radius:14px;padding:11px 14px;
        background:#fbfcfe}
 .ch{display:flex;flex-direction:column;gap:3px}
 .lb{font-size:10.5px;font-weight:700;letter-spacing:.07em;color:#6b7590;
     text-transform:uppercase}
 select,input[type=range]{font:inherit}
 select{font-size:13.5px;padding:5px 8px;border:1px solid #d7e0ec;
        border-radius:9px;background:#fff;color:#101728;max-width:270px}
 input[type=range]{width:190px;accent-color:#1c6349}
 .bt{font-size:13px;font-weight:700;padding:7px 14px;border-radius:9px;
     border:1px solid #d7e0ec;background:#fff;color:#3c4761;cursor:pointer}
 .bt:hover{border-color:#b6d8c6}
 .bt.p{background:#1c6349;border-color:#1c6349;color:#fff}
 .cpt{margin-left:auto;text-align:right}
 .cpt b{font-size:22px;font-variant-numeric:tabular-nums}
 .cpt span{font-size:11.5px;color:#6b7590}
 .jauge{height:5px;width:170px;background:#eef2f7;border-radius:3px;
        overflow:hidden;margin-top:5px}
 .jauge i{display:block;height:100%;background:#1c6349;width:0;
          transition:width .35s ease}
 svg{display:block;width:100%;height:auto}
 .col-t{font:700 10.5px Inter,system-ui,sans-serif;fill:#6b7590;
        letter-spacing:.07em;text-transform:uppercase}
 .nd-l{font:600 11px Inter,system-ui,sans-serif;fill:#101728}
 .nd-v{font:700 11px Inter,system-ui,sans-serif;fill:#3c4761;
       font-variant-numeric:tabular-nums}
 .ar{fill:none;stroke:#dde5ee;stroke-width:1.4}
 .ar.on{stroke-width:2.6;stroke-dasharray:7 6;
        animation:file .85s linear infinite}
 .ar.rt{stroke-dasharray:3 4}
 @keyframes file{to{stroke-dashoffset:-26}}
 .bas{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:12px}
 .bloc{border:1px solid #e3eaf3;border-radius:14px;padding:12px 14px}
 .bloc h4{margin:0 0 8px;font-size:11px;letter-spacing:.07em;color:#6b7590;
          text-transform:uppercase}
 .li{display:flex;align-items:center;gap:9px;padding:3px 0;font-size:13px}
 .li i{width:8px;height:8px;border-radius:50%;flex:none}
 .li b{margin-left:auto;font-variant-numeric:tabular-nums;font-size:12.5px}
 .note{font-size:12.5px;color:#6b7590;line-height:1.5;margin:9px 2px 0}
 .ret{border-left:4px solid #b5451f;background:#fdf6f3;border-radius:0 10px
      10px 0;padding:9px 13px;font-size:13.5px;color:#3c4761;margin-top:10px}
 .ret b{color:#b5451f}
 .leg{display:flex;gap:18px;flex-wrap:wrap;font-size:12px;color:#6b7590;
      margin:9px 2px 0;align-items:center;line-height:1}
 .leg>span{display:inline-flex;align-items:center;gap:5px;white-space:nowrap}
 .leg i{display:inline-block;width:11px;height:11px;border-radius:3px;
        margin-right:5px;vertical-align:-1px}
</style></head><body>
<div class="barre">
  <div class="ch"><span class="lb">__L_NOEUD__</span>
    <select id="src"></select></div>
  <div class="ch"><span class="lb">__L_AMPLEUR__ · <b id="av"></b></span>
    <input type="range" id="amp" min="-3" max="3" step="0.5" value="-2"></div>
  <button class="bt p" id="play">__L_LIRE__</button>
  <button class="bt" id="pas">__L_PAS__</button>
  <button class="bt" id="zero">__L_ZERO__</button>
  <div class="cpt"><b id="kk">0</b> <span>· __L_VAGUE__</span>
    <div class="jauge"><i id="jg"></i></div>
    <span id="pc">0 % __L_DISTRIB__</span></div>
</div>
<svg id="g" viewBox="0 0 1180 640" role="img"></svg>
<div class="leg">
  <span><i style="background:#1a8a4f"></i>__L_LEGH__</span>
  <span><i style="background:#c33a24"></i>__L_LEGB__</span>
  <span><svg width="26" height="8"><line x1="1" y1="4" x2="25" y2="4"
     stroke="#dde5ee" stroke-width="2" stroke-dasharray="3 4"/></svg>
     __L_LEGR__</span>
  <span>__L_UNITE__</span>
</div>
<div id="ret"></div>
<p class="note" id="hors"></p>
<div class="bas">
  <div class="bloc"><h4>__L_MOUV__</h4><div id="mouv"></div></div>
  <div class="bloc"><h4>__L_CUMUL__</h4><div id="cumul"></div></div>
</div>
<script>
const D = __DONNEES__, L = __LIBELLES__, CD = __COUL_DIM__;
const N = D.noeuds, E = D.aretes;
const IDX = {}; N.forEach((n,i)=>IDX[n.id]=i);
const NN = N.length;
const HAUSSE = "#1a8a4f", BAISSE = "#c33a24", NEUTRE = "#c8d0dc";
const SEUIL = 0.02;               /* sous 0,02 point, on ne dessine rien */
const KMAX = 24;                  /* au-delà, la vague est éteinte */

/* ---------- la propagation, vague par vague ---------------------------- */
function vagues(src, amp){
  let w = new Float64Array(NN);
  w[IDX[src]] = amp;
  const out = [w];                /* vague 0 : le choc posé lui-même */
  for (let k=0; k<KMAX; k++){
    const nx = new Float64Array(NN);
    for (const e of E) nx[IDX[e.vers]] += e.w * w[IDX[e.de]];
    out.push(nx); w = nx;
  }
  return out;
}
/* L'effet total EXCLUT le choc posé : c'est l'effet propagé, celui que le
   moteur renvoie. La somme des vagues 1..KMAX en est la limite. */
function total(vg){
  const t = new Float64Array(NN);
  for (let k=1; k<vg.length; k++) for (let i=0;i<NN;i++) t[i]+=vg[k][i];
  return t;
}
function somme_abs(v){ let s=0; for (const x of v) s+=Math.abs(x); return s; }

/* ---------- les colonnes : rang de PREMIÈRE arrivée --------------------- */
function profondeurs(src){
  const d = {}; d[src]=0; const f=[src];
  while (f.length){
    const u=f.shift();
    for (const e of E) if (e.de===u && !(e.vers in d)){ d[e.vers]=d[u]+1; f.push(e.vers); }
  }
  return d;
}

/* ---------- état ------------------------------------------------------- */
let src = "__DEPART__", amp = -2, k = 0, vg = null, tot = null, prof = null,
    ordre = null, minuteur = null;

function preparer(){
  vg = vagues(src, amp);
  tot = total(vg);
  prof = profondeurs(src);
  /* L'ORDRE VERTICAL EST FIXÉ UNE FOIS, sur l'effet final. S'il suivait la
     vague courante, les nœuds sauteraient d'une ligne à l'autre à chaque pas
     et l'œil perdrait celui qu'il suivait. */
  ordre = {};
  Object.keys(prof).forEach(id=>{
    const c = Math.min(prof[id], 6);
    (ordre[c] = ordre[c] || []).push(id);
  });
  Object.keys(ordre).forEach(c=>ordre[c].sort(
    (a,b)=>Math.abs(tot[IDX[b]])-Math.abs(tot[IDX[a]])));
  k = 0;
  dessiner();
}

function cumul(jusqu){
  const c = new Float64Array(NN);
  for (let j=1; j<=jusqu && j<vg.length; j++)
    for (let i=0;i<NN;i++) c[i]+=vg[j][i];
  return c;
}

/* ---------- le dessin --------------------------------------------------- */
const LARG=1180, MG_G=16, MG_H=42, BOITE_L=168, BOITE_H=25;
let HAUT = 560;   /* recalculée à chaque changement de nœud : voir positions() */

function positions(){
  /* LA HAUTEUR SUIT LA COLONNE LA PLUS CHARGÉE. Une hauteur fixe laissait un
     tiers de blanc quand le choc n'atteignait que six nœuds, et serrait les
     boîtes quand il en atteignait douze. */
  const cols = Object.keys(ordre).map(Number).sort((a,b)=>a-b);
  const plein = Math.max(...cols.map(c=>ordre[c].length), 1);
  /* Le pas vertical se resserre quand une colonne est chargée — jusqu'à 27 px,
     en dessous les boîtes se toucheraient — et la hauteur totale reste sous
     640 px : au-delà, l'onde ne tient plus dans un écran et l'on perd de vue
     la colonne de départ en regardant la dernière. */
  const PH = Math.max(27, Math.min(42, (640 - MG_H - 78) / plein));
  HAUT = Math.max(300, MG_H + plein*PH + 78);
  const pas = cols.length>1 ? (LARG-MG_G*2-BOITE_L)/(cols.length-1) : 0;
  const pos = {};
  cols.forEach((c,i)=>{
    const ids = ordre[c], x = MG_G + i*pas;
    const y0 = MG_H + ((plein - ids.length) * PH) / 2;
    ids.forEach((id,j)=>{ pos[id] = {x, y: y0 + j*PH, c}; });
  });
  return {pos, cols, pas};
}

function dessiner(){
  const {pos, cols, pas} = positions();
  const cum = cumul(k), vk = vg[k] || new Float64Array(NN);
  const s = [];

  /* en-tête de colonne */
  cols.forEach((c,i)=>{
    const x = MG_G + i*pas + BOITE_L/2;
    const lib = c===0 ? L.depart : (c>=6 ? L.col_plus : L.col+" "+c);
    s.push(`<text class="col-t" x="${x}" y="22" text-anchor="middle">${lib}</text>`);
  });

  /* arêtes : celles qui portent la vague courante sont animées */
  for (const e of E){
    const a = pos[e.de], b = pos[e.vers];
    if (!a || !b) continue;
    const flux = (vg[k-1] ? vg[k-1][IDX[e.de]] : 0) * e.w;
    const on = k>0 && Math.abs(flux) > SEUIL;
    const retour = b.c <= a.c;
    const x1 = a.x + BOITE_L, y1 = a.y + BOITE_H/2;
    const x2 = b.x, y2 = b.y + BOITE_H/2;
    let d;
    if (retour){
      /* un lien qui remonte est une boucle : on le fait passer par le bas,
         hors du faisceau, pour qu'il se voie au lieu de se confondre */
      const my = Math.max(y1,y2) + 34 + (a.c-b.c)*6;
      d = `M${a.x} ${y1} C${a.x-40} ${my} ${x2+BOITE_L+40} ${my} ${x2+BOITE_L} ${y2}`;
    } else {
      const mx = (x1+x2)/2;
      d = `M${x1} ${y1} C${mx} ${y1} ${mx} ${y2} ${x2} ${y2}`;
    }
    const coul = on ? (flux>0?HAUSSE:BAISSE) : "#dde5ee";
    s.push(`<path class="ar${on?" on":""}${retour?" rt":""}" d="${d}" `+
           `stroke="${coul}"><title>${nom(e.de)} → ${nom(e.vers)}</title></path>`);
  }

  /* nœuds */
  for (const id in pos){
    const p = pos[id], v = cum[IDX[id]] + (id===src ? amp : 0);
    const bouge = Math.abs(vk[IDX[id]]) > SEUIL;
    const t = Math.min(1, Math.abs(v)/2.2);
    const fond = Math.abs(v) < SEUIL ? "#f7f9fc"
               : (v>0 ? teinte(HAUSSE, t) : teinte(BAISSE, t));
    const bord = Math.abs(v) < SEUIL ? "#e3eaf3" : (v>0?HAUSSE:BAISSE);
    s.push(`<g><title>${nom(id)} : ${sig(v)}</title>`+
      `<rect x="${p.x}" y="${p.y}" width="${BOITE_L}" height="${BOITE_H}" `+
      `rx="7" fill="${fond}" stroke="${bord}" stroke-width="${bouge?2:1}"/>`+
      `<rect x="${p.x}" y="${p.y}" width="3.5" height="${BOITE_H}" rx="2" `+
      `fill="${CD[noeud(id).dim]||"#9aa4b5"}"/>`+
      `<text class="nd-l" x="${p.x+10}" y="${p.y+16}">`+
      `${court(nom(id), Math.abs(v)<SEUIL ? 22 : 16)}</text>`+
      `<text class="nd-v" x="${p.x+BOITE_L-8}" y="${p.y+16}" `+
      `text-anchor="end">${Math.abs(v)<SEUIL?"":sig(v)}</text></g>`);
  }

  const g = document.getElementById("g");
  g.setAttribute("viewBox", `0 0 ${LARG} ${HAUT}`);
  g.innerHTML = s.join("");
  document.getElementById("kk").textContent = k;
  const part = somme_abs(tot) ? somme_abs(cum)/somme_abs(tot) : 0;
  document.getElementById("jg").style.width = (part*100).toFixed(0)+"%";
  document.getElementById("pc").textContent =
    (part*100).toFixed(0)+" % "+L.distrib;
  panneaux(cum, vk);
}

function teinte(hex, t){
  const r=parseInt(hex.slice(1,3),16), g=parseInt(hex.slice(3,5),16),
        b=parseInt(hex.slice(5,7),16), m=0.12+0.62*t;
  const f=x=>Math.round(255-(255-x)*m);
  return `rgb(${f(r)},${f(g)},${f(b)})`;
}
function noeud(id){ return N[IDX[id]]; }
function nom(id){ return noeud(id).nom; }
/* LA TRONCATURE DÉPEND DE LA PLACE RESTANTE : un nœud qui porte une valeur
   n'a plus toute la boîte pour son nom, et les deux se chevauchaient. */
function court(s, n){ return s.length>n ? s.slice(0,n-1)+"…" : s; }
function sig(v){ return (v>0?"+":"−")+Math.abs(v).toFixed(2); }

function panneaux(cum, vk){
  const mouv = [...Array(NN).keys()]
    .filter(i=>Math.abs(vk[i])>SEUIL && N[i].id!==src)
    .sort((a,b)=>Math.abs(vk[b])-Math.abs(vk[a])).slice(0,6);
  document.getElementById("mouv").innerHTML = mouv.length
    ? mouv.map(i=>ligne(N[i], vk[i])).join("")
    : `<p class="note" style="margin:0">${k===0?"":L.rien}</p>`;

  const cu = [...Array(NN).keys()]
    .filter(i=>Math.abs(cum[i])>SEUIL && N[i].id!==src)
    .sort((a,b)=>Math.abs(cum[b])-Math.abs(cum[a])).slice(0,6);
  document.getElementById("cumul").innerHTML =
    cu.map(i=>ligne(N[i], cum[i])).join("") || `<p class="note" style="margin:0">—</p>`;

  /* le retour de boucle : la première vague ≥ 2 qui atteint le point de départ */
  let kr = 0;
  for (let j=2; j<vg.length; j++)
    if (Math.abs(vg[j][IDX[src]]) > SEUIL){ kr = j; break; }
  const meme = kr && (vg[kr][IDX[src]] * amp > 0);
  document.getElementById("ret").innerHTML = kr
    ? `<div class="ret"><b>${L.retour_t}.</b> ` +
      L.retour.replace("{k}", kr)
              .replace("{sens}", meme ? L.amplifie : L.attenue) + `</div>`
    : `<p class="note">${L.sans_retour}</p>`;

  const atteints = Object.keys(prof).length;
  document.getElementById("hors").textContent = atteints < NN
    ? L.hors.replace("{n}", NN-atteints).replace("{t}", NN) : "";
}

function ligne(n, v){
  return `<div class="li"><i style="background:${v>0?HAUSSE:BAISSE}"></i>`+
         `<span>${n.nom}</span><b style="color:${v>0?HAUSSE:BAISSE}">`+
         `${sig(v)}</b></div>`;
}

/* ---------- commandes --------------------------------------------------- */
const sel = document.getElementById("src");
N.slice().sort((a,b)=>a.nom.localeCompare(b.nom)).forEach(n=>{
  const o=document.createElement("option"); o.value=n.id; o.textContent=n.nom;
  sel.appendChild(o);
});
sel.value = src;
sel.onchange = ()=>{ src = sel.value; arreter(); preparer(); };
const rg = document.getElementById("amp");
function majAmp(){ document.getElementById("av").textContent =
  (amp>0?"+":"−")+Math.abs(amp).toFixed(1); }
rg.oninput = ()=>{ amp = parseFloat(rg.value) || 0; majAmp();
                   const kk=k; preparer(); k=kk; dessiner(); };
document.getElementById("pas").onclick = ()=>{ arreter(); avancer(); };
document.getElementById("zero").onclick = ()=>{ arreter(); k=0; dessiner(); };
const bp = document.getElementById("play");
bp.onclick = ()=>{ if (minuteur) arreter(); else lancer(); };

function avancer(){
  /* on s'arrête quand la vague ne déplace plus rien : inutile de compter
     jusqu'à vingt-quatre pour regarder des zéros défiler */
  if (k>=KMAX || (k>0 && somme_abs(vg[k])<SEUIL/2)){ k=0; dessiner(); return; }
  k++; dessiner();
}
function lancer(){ bp.textContent = L.pause; bp.classList.remove("p");
                   minuteur = setInterval(avancer, 1250); avancer(); }
function arreter(){ if (minuteur) clearInterval(minuteur); minuteur=null;
                    bp.textContent = L.lire; bp.classList.add("p"); }

majAmp(); preparer();
</script></body></html>"""


def _html(d, lang):
    lib = {
        "depart": T("oc_depart"), "col": T("oc_col"),
        "col_plus": T("oc_col_plus"), "distrib": T("oc_distribue"),
        "retour_t": T("oc_retour_t"), "retour": T("oc_retour"),
        "amplifie": T("oc_amplifie"), "attenue": T("oc_attenue"),
        "sans_retour": T("oc_sans_retour"), "hors": T("oc_hors"),
        "rien": T("oc_rien"), "lire": T("oc_lire"), "pause": T("oc_pause"),
    }
    depart = DEPART if any(n["id"] == DEPART for n in d["noeuds"]) \
        else d["noeuds"][0]["id"]
    return (GABARIT
            .replace("__DONNEES__", json.dumps(d, ensure_ascii=False,
                                               separators=(",", ":")))
            .replace("__LIBELLES__", json.dumps(lib, ensure_ascii=False))
            .replace("__COUL_DIM__", json.dumps(COUL_DIM))
            .replace("__DEPART__", depart)
            .replace("__L_NOEUD__", _e(T("oc_noeud")))
            .replace("__L_AMPLEUR__", _e(T("oc_ampleur")))
            .replace("__L_LIRE__", _e(T("oc_lire")))
            .replace("__L_PAS__", _e(T("oc_pas")))
            .replace("__L_ZERO__", _e(T("oc_zero")))
            .replace("__L_VAGUE__", _e(T("oc_vague")))
            .replace("__L_DISTRIB__", _e(T("oc_distribue")))
            .replace("__L_MOUV__", _e(T("oc_mouv_t")))
            .replace("__L_CUMUL__", _e(T("oc_cumul_t")))
            .replace("__L_LEGH__", _e(T("oc_leg_h")))
            .replace("__L_LEGB__", _e(T("oc_leg_b")))
            .replace("__L_LEGR__", _e(T("oc_leg_r")))
            .replace("__L_UNITE__", _e(T("oc_unite"))))


def render(entete=True):
    lang = i18n.get_lang()
    d = _graphe(lang)
    if not d:
        st.info(T("oc_absent"))
        return

    if entete:
        st.markdown(
            f'<h2 style="font-size:27px;font-weight:700;color:{ENCRE};'
            f'letter-spacing:-.02em;margin:2px 0 0">{_e(T("oc_titre"))}</h2>'
            f'<p style="font-size:12.5px;color:{ENCRE3};letter-spacing:.06em;'
            f'text-transform:uppercase;margin:2px 0 0;font-weight:600">'
            f'{_e(T("oc_sous"))}</p>', unsafe_allow_html=True)

    st.markdown(
        f'<div style="background:#fff;border:1px solid {BORD};border-left:5px '
        f'solid #1a6b52;border-radius:14px;padding:13px 17px;font-size:15.5px;'
        f'color:{ENCRE2};line-height:1.6;margin:10px 0 8px;max-width:96ch;'
        f'text-align:left">{T("oc_intro")}</div>', unsafe_allow_html=True)

    # LA HAUTEUR EST FIXE ET GÉNÉREUSE. Une iframe trop courte coupe le panneau
    # du bas sans rien dire ; personne ne devine qu'il faut faire défiler à
    # l'intérieur d'un cadre qui n'a pas de barre.
    components.html(_html(d, lang), height=1010, scrolling=False)
    st.caption(T("oc_avert"))
