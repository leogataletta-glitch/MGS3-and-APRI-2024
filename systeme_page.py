"""Le système en marche — toutes les variables à la fois, et ce qu'elles se font.

CE QUE CETTE VUE REMPLACE
=========================

Un schéma de réseau : quarante-cinq boîtes et quatre-vingt-deux flèches sur une
même image. Il montrait la structure et rien d'autre — impossible d'y lire ce
qui monte, ce qui descend, ni pourquoi. Une carte du câblage, là où l'on
voulait voir la machine tourner.

CE QU'ELLE MONTRE À LA PLACE
============================

Les quarante-cinq variables, chacune avec son niveau sur dix. On clique dans la
barre d'une variable pour lui donner la valeur qu'on veut, on appuie sur
lecture, et le système se met en marche : chaque variable monte ou descend
selon ce que ses voisines lui font, jusqu'à ce que tout se stabilise.

Ce n'est plus « je teste un choc et je regarde l'onde ». C'est « je pose un
état, et je regarde le système le digérer ».

LA MÉCANIQUE, ET POURQUOI L'ÉTAT MESURÉ EST UN ÉQUILIBRE
========================================================

Le graphe ne dit rien des niveaux : il dit ce qu'un ÉCART sur une variable
produit ailleurs. L'état mesuré par l'enquête est donc pris comme référence, et
le modèle est au repos tant qu'on n'y touche pas — ce qui est la seule lecture
honnête : le territoire observé est, par construction, ce que le modèle
considère comme son point de fonctionnement.

Dès qu'une valeur est imposée, un écart apparaît et se propage :

    écart_0      = ce que l'utilisateur impose
    écart_{t+1}  = écart_0 + A · écart_t

La suite converge vers (I − A)⁻¹ · écart_0, c'est-à-dire exactement l'effet
total que calcule `boucles_moteur`. Les deux vues du modèle ne peuvent donc pas
diverger : celle-ci montre le chemin, l'autre donne le point d'arrivée.

CE QUE LE TEMPS N'EST PAS
=========================

Un pas n'est pas une année. C'est un tour de propagation : le temps qu'il faut
pour qu'un écart traverse une relation. Le modèle ne connaît pas les délais
réels — une coupe de forêt met des années à se voir sur les sols, un choc de
revenu se voit en semaines — et il serait malhonnête de faire croire le
contraire en mettant des dates sous les pas.
"""

import json
import os

import streamlit as st
import streamlit.components.v1 as components

import boucles_moteur as M
import i18n
from i18n import T

ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"
BORD = "#e3eaf3"
HAUSSE, BAISSE = "#1a8a4f", "#c33a24"

COUL_DIM = {"dim1": "#2166ac", "dim2": "#6a51a3", "dim3": "#1a8a4f",
            "dim4": "#d1730c", "dim5": "#b5451f", "dim6": "#0f7b8a"}

TEXTES = {
    "sy_titre": {"en": "The system running", "fr": "Le système en marche"},
    "sy_sous": {"en": "Set a value, press play, watch the system digest it",
                "fr": "Posez une valeur, appuyez sur lecture, regardez le "
                      "système la digérer"},
    "sy_intro": {
        "en": "Every variable holds a level out of ten, the one measured by "
              "the survey where it exists. Click inside a bar to impose a "
              "different value: that variable is then held, the gap it "
              "creates travels through the model at once, and each other "
              "variable rises or falls according to what its neighbours do to "
              "it, until everything settles. What moved, and by how much, is "
              "named under the bars. Play and pause let you take the "
              "propagation back round by round.",
        "fr": "Chaque variable porte un niveau sur dix, celui mesuré par "
              "l'enquête là où il existe. Cliquez dans une barre pour lui "
              "imposer une autre valeur : la variable est alors tenue, "
              "l'écart qu'elle crée circule aussitôt dans le modèle, et "
              "chaque autre variable monte ou descend selon ce que ses "
              "voisines lui font, jusqu'à stabilisation. Ce qui a bougé, et "
              "de combien, est nommé sous les barres. Lecture et pause "
              "servent à reprendre la propagation tour par tour."},
    "sy_avert": {
        "en": "A step is a round of propagation, not a year. The model knows "
              "the order of the relays, not their duration: forest loss takes "
              "years to show up in soils, an income shock shows up in weeks, "
              "and nothing here distinguishes the two.",
        "fr": "Un pas est un tour de propagation, pas une année. Le modèle "
              "connaît l'ordre des relais, pas leur durée : une coupe de "
              "forêt met des années à se voir sur les sols, un choc de revenu "
              "se voit en semaines, et rien ici ne distingue les deux."},

    "sy_lire": {"en": "Play", "fr": "Lecture"},
    "sy_pause": {"en": "Pause", "fr": "Pause"},
    "sy_pas": {"en": "Step", "fr": "Pas à pas"},
    "sy_zero": {"en": "Back to the measured state",
                "fr": "Revenir à l'état mesuré"},
    "sy_tour": {"en": "round", "fr": "tour"},
    "sy_tenues": {"en": "held variables", "fr": "variables tenues"},
    "sy_monte": {"en": "rising", "fr": "en hausse"},
    "sy_baisse": {"en": "falling", "fr": "en baisse"},
    "sy_stable": {"en": "The system has settled: nothing moves any more.",
                  "fr": "Le système s'est stabilisé : plus rien ne bouge."},
    "sy_repos": {
        "en": "At rest. The measured state is the model's operating point, "
              "impose a value somewhere to set it in motion.",
        "fr": "Au repos. L'état mesuré est le point de fonctionnement du "
              "modèle, imposez une valeur quelque part pour le mettre en "
              "mouvement."},
    "sy_moyenne": {"en": "Mean of the measured variables",
                   "fr": "Moyenne des variables mesurées"},
    "sy_libere": {"en": "release", "fr": "libérer"},
    "sy_tenue": {"en": "held", "fr": "tenue"},
    "sy_non_mesure": {"en": "not measured, starts at 5",
                      "fr": "non mesurée, part de 5"},
    "sy_repere": {"en": "measured state (reference mark)",
                  "fr": "état mesuré (le repère)"},
    "sy_depart": {"en": "at the measured state", "fr": "au départ"},
    "sy_aide": {"en": "− and + set a level by half a point; the system starts "
                      "on its own",
                "fr": "− et + règlent le niveau par demi-point ; le système "
                      "part tout seul"},
    "sy_moins": {"en": "half a point lower", "fr": "un demi-point de moins"},
    "sy_plus": {"en": "half a point higher", "fr": "un demi-point de plus"},
    # LE MODE D'EMPLOI, EN GRAND ET DANS LA BARRE. Il était écrit sous les
    # quarante-cinq barres, en gris de onze pixels : on appuyait sur Lecture
    # sans rien avoir tenu, le compteur montait, rien ne bougeait, et l'on
    # concluait que l'écran était cassé. Tant qu'aucune variable n'est tenue,
    # les deux boutons de course sont éteints et la consigne prend leur
    # place : il n'y a rien d'autre à faire que de poser une valeur.
    "sy_amorce": {
        "en": "Every variable carries its measured level. Change any of them "
              "with − and +, or click inside a bar to set a level in one go: "
              "that variable is then held there, and the system starts on its "
              "own. Several can be held at once.",
        "fr": "Chaque variable porte son niveau mesuré. Changez celui que vous "
              "voulez avec − et +, ou cliquez dans une barre pour y poser un "
              "niveau d'un coup : la variable est alors tenue là, et le "
              "système part tout seul. On peut en tenir plusieurs à la fois."},
    # CE QUE ÇA DÉPLACE, ÉCRIT NOIR SUR BLANC. Quarante-cinq barres réparties
    # en trois colonnes : quand onze d'entre elles bougeaient de trois
    # dixièmes, il fallait les chercher pour s'en apercevoir, et l'on
    # concluait que rien ne s'était passé. La bande nomme les variables qui
    # ont le plus bougé, celle qu'on tient exclue — son mouvement est imposé,
    # ce n'est pas une répercussion.
    "sy_bilan": {"en": "What this moves", "fr": "Ce que cela déplace"},
    "sy_bilan_0": {
        "en": "Nothing else moves: within this model, no relation carries "
              "this variable's change any further.",
        "fr": "Rien d'autre ne bouge : dans ce modèle, aucune relation ne "
              "porte plus loin le changement de cette variable."},
    "sy_absent": {"en": "Causal graph unavailable.",
                  "fr": "Le graphe causal n'est pas disponible."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")


@st.cache_data(show_spinner=False)
def _systeme(lang):
    """Nœuds, niveaux de départ et arêtes mises à l'échelle.

    LA LANGUE EST UN ARGUMENT DE CACHE — une fonction cachée qui lirait la
    langue à l'intérieur figerait à jamais la première affichée, et l'anglais
    s'installerait au milieu de la page française sans que rien ne le signale.

    LE MODULE CHARGE SES PROPRES RÉSULTATS. Il pourrait les recevoir de la page
    qui l'appelle, mais il serait alors inutilisable ailleurs, et une page qui
    ne peut être appelée que d'un seul endroit finit par y être fondue.
    """
    g = M.charger()
    if not g or not g.get("noeuds"):
        return None
    A, ids, idx = M.matrice(g)
    p = os.path.join(DATA, "resultats.json")
    res = []
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            res = json.load(f)
        res = res["indicateurs"] if isinstance(res, dict) \
            and "indicateurs" in res else res
    etat = M.etat_courant(g, {r["ligne"]: r for r in (res or [])
                              if r.get("ligne") is not None})

    noeuds = []
    for n in g["noeuds"]:
        v = etat.get(n["id"])
        noeuds.append({
            "id": n["id"],
            "nom": n.get(lang) or n.get("fr") or n["id"],
            "dim": n.get("dim", ""),
            # NON MESURÉE ≠ NULLE. L'état de santé, la capacité de travail, la
            # pression sur le bois n'ont pas de score dans le référentiel. Les
            # mettre à zéro dirait « c'est catastrophique » ; les mettre au
            # milieu dit « on ne sait pas », et la vue le marque.
            "v": round(float(v), 2) if v is not None else 5.0,
            "mesure": v is not None,
        })
    aretes = [{"de": a["de"], "vers": a["vers"],
               "w": round(float(A[idx[a["vers"]], idx[a["de"]]]), 6),
               "f": a.get("force"), "j": a.get("just", "")}
              for a in g["aretes"] if a["de"] in idx and a["vers"] in idx]
    return {"noeuds": noeuds, "aretes": aretes,
            "dims": {d: T(d) for d in sorted(COUL_DIM)}}


GABARIT = r"""<!doctype html><html><head><meta charset="utf-8">
<style>
 *{box-sizing:border-box}
 body{margin:0;font-family:Inter,system-ui,-apple-system,sans-serif;
      color:#101728;background:#fff}
 .barre{display:flex;flex-wrap:wrap;align-items:center;gap:12px;
        border:1px solid #e3eaf3;border-radius:14px;padding:11px 14px;
        background:#fbfcfe;margin-bottom:13px}
 .bt{font-size:12px;font-weight:700;padding:7px 14px;border-radius:9px;
     border:1px solid #d7e0ec;background:#fff;color:#3c4761;cursor:pointer}
 .bt:hover{border-color:#b6d8c6}
 .bt.p{background:#1c6349;border-color:#1c6349;color:#fff}
 /* UN BOUTON QUI NE PEUT RIEN FAIRE LE DIT. Éteint, il n'invite pas au clic,
    et la consigne à côté explique ce qui manque. */
 .bt[disabled]{opacity:.42;cursor:not-allowed;background:#fff;
    border-color:#e3eaf3;color:#8a93a5}
 #amorce{font-size:12.5px;color:#1a4d3a;background:#eef4f0;
    border:1px solid #cfe0d6;border-radius:9px;padding:7px 12px;
    line-height:1.4;max-width:46ch}
 /* LA BARRE SE SIGNALE SOUS LE POINTEUR : sans cela, rien ne dit qu'un
    rectangle gris de quinze pixels est le lieu du geste. */
 .ba:hover{outline:2px solid #b6d8c6;outline-offset:1px}
 .cpt{display:flex;gap:20px;margin-left:auto;align-items:baseline}
 .cpt div{text-align:right}
 .cpt b{font-size:16px;font-variant-numeric:tabular-nums}
 .cpt span{font-size:10.5px;color:#6b7590;letter-spacing:.06em;
           text-transform:uppercase;font-weight:700;display:block}
 .cols{display:grid;grid-template-columns:1fr 1fr 1fr;gap:0 22px}
 .grp{break-inside:avoid;margin-bottom:9px}
 .grp h4{margin:10px 0 4px;font-size:10.5px;letter-spacing:.07em;
         text-transform:uppercase;color:#6b7590;display:flex;
         align-items:center;gap:6px}
 .grp h4 i{width:8px;height:8px;border-radius:2px;flex:none}
 .li{display:grid;grid-template-columns:1fr 74px 44px 42px;gap:7px;
     align-items:center;padding:2px 0}
 /* MOINS ET PLUS, SUR CHAQUE LIGNE. Viser un dixième dans une barre de
    soixante-quatorze pixels demandait une précision que personne n'a, et
    surtout rien n'annonçait qu'un rectangle gris était réglable. Deux boutons
    par demi-point disent le geste et le rendent exact ; la barre reste
    cliquable pour poser un niveau d'un coup, loin de la valeur mesurée. */
 .pm{display:flex;gap:3px}
 .pm button{width:19px;height:17px;line-height:1;padding:0;font-size:12px;
    font-weight:700;border:1px solid #d7e0ec;background:#fff;color:#3c4761;
    border-radius:5px;cursor:pointer}
 .pm button:hover{border-color:#1c6349;color:#1c6349;background:#f2f8f4}
 .nm{font-size:11px;color:#3c4761;white-space:nowrap;overflow:hidden;
     text-overflow:ellipsis}
 .nm.t{font-weight:700;color:#101728}
 .ba{position:relative;height:15px;border-radius:4px;background:#eef2f7;
     cursor:pointer;overflow:hidden}
 .ba .f{position:absolute;left:0;top:0;bottom:0;border-radius:4px;
        transition:width .35s ease}
 .ba .r{position:absolute;top:-1px;bottom:-1px;width:2px;background:#9aa4b5}
 .ba.t{outline:2px solid #1c6349;outline-offset:1px}
 .vl{font-size:11px;font-variant-numeric:tabular-nums;text-align:right;
     font-weight:700}
 .dl{font-size:10.5px;font-variant-numeric:tabular-nums;color:#6b7590}
 .note{font-size:11px;color:#6b7590;margin:12px 2px 0;line-height:1.5}
 /* LA BANDE DE BILAN : ce que la variable tenue déplace, nommé. Elle
    n'apparaît que lorsqu'il y a quelque chose à nommer, sans quoi elle
    laisserait un cadre vide sous le tableau. */
 .bil{border:1px solid #e3eaf3;border-left:4px solid #1c6349;border-radius:12px;
      padding:10px 14px;margin-top:14px;background:#fbfcfe}
 .bil h5{margin:0 0 7px;font-size:10.5px;letter-spacing:.09em;
         text-transform:uppercase;color:#1a4d3a;font-weight:700}
 .bil .rg{display:flex;flex-wrap:wrap;gap:8px 18px}
 .bil .it{font-size:12.5px;color:#3c4761}
 .bil .it b{font-variant-numeric:tabular-nums;margin-left:6px}
 .bil p{margin:0;font-size:12px;color:#6b7590}
 .lg{display:flex;gap:16px;flex-wrap:wrap;font-size:11.5px;color:#6b7590;
     margin-top:10px;align-items:center}
 .lg i{display:inline-block;width:10px;height:10px;border-radius:2px;
       margin-right:5px;vertical-align:-1px}
</style></head><body>
<div class="barre">
  <button class="bt p" id="play" disabled>__L_LIRE__</button>
  <button class="bt" id="pas" disabled>__L_PAS__</button>
  <button class="bt" id="zero">__L_ZERO__</button>
  <div id="amorce">__L_AMORCE__</div>
  <div class="cpt">
    <div><b id="kk">0</b><span>__L_TOUR__</span></div>
    <div><b id="nt">0</b><span>__L_TENUES__</span></div>
    <div><b id="nh" style="color:#1a8a4f">0</b><span>__L_MONTE__</span></div>
    <div><b id="nb" style="color:#c33a24">0</b><span>__L_BAISSE__</span></div>
    <div><b id="mo">—</b><span id="mos">__L_MOY__</span></div>
  </div>
</div>
<div class="cols" id="cols"></div>
<div class="lg">
  <span><i style="background:#1a8a4f"></i>__L_MONTE__</span>
  <span><i style="background:#c33a24"></i>__L_BAISSE__</span>
  <span><svg width="14" height="12"><rect x="6" y="0" width="2" height="12"
    fill="#9aa4b5"/></svg> __L_REPERE__</span>
  <span>__L_AIDE__</span>
</div>
<div id="bilan"></div>
<p class="note" id="etat"></p>
<script>
const D = __DONNEES__, L = __LIBELLES__, CD = __COUL_DIM__;
const N = D.noeuds, E = D.aretes;
const IDX = {}; N.forEach((n,i)=>IDX[n.id]=i);
const NN = N.length;
const HAUSSE="#1a8a4f", BAISSE="#c33a24";
const SEUIL = 0.005;      /* sous ce pas, le système est dit stabilisé */

const base = N.map(n=>n.v);          /* l'état mesuré : la référence */
const MOY0 = (()=>{ let s=0,c=0; N.forEach((n,i)=>{ if(n.mesure){s+=base[i];c++;} });
                    return c ? s/c : 0; })();
const tenu = {};                     /* id -> valeur imposée */
let d = new Float64Array(NN);        /* écart courant à la référence */
let dprec = new Float64Array(NN);
let k = 0, minuteur = null;

function d0(){
  const v = new Float64Array(NN);
  for (const id in tenu) v[IDX[id]] = tenu[id] - base[IDX[id]];
  return v;
}
/* écart_{t+1} = écart_0 + A · écart_t : les valeurs imposées restent
   imposées, le reste est ce que le modèle en fait. */
function avancer(){
  const z = d0(), nx = new Float64Array(z);
  for (const e of E) nx[IDX[e.vers]] += e.w * d[IDX[e.de]];
  dprec = d; d = nx; k++;
  dessiner();
}
function borne(x){ return Math.max(0, Math.min(10, x)); }
function niveau(i){ return borne(base[i] + d[i]); }

function construire(){
  const dims = [...new Set(N.map(n=>n.dim))].sort();
  const parCol = [[],[],[]];
  dims.forEach((dim,i)=>parCol[i % 3].push(dim));
  const html = parCol.map(cols=>'<div>'+cols.map(dim=>{
    const liste = N.map((n,i)=>({n,i})).filter(x=>x.n.dim===dim);
    return `<div class="grp"><h4><i style="background:${CD[dim]||'#9aa4b5'}">`+
      `</i>${(D.dims||{})[dim]||dim}</h4>`+
      liste.map(({n,i})=>
        `<div class="li" id="li${i}">`+
        `<div class="nm" id="nm${i}" title="${n.nom}${n.mesure?'':' · '+L.non_mesure}">`+
        `${n.nom}</div>`+
        `<div class="ba" id="ba${i}" data-i="${i}">`+
        `<div class="f" id="fi${i}"></div><div class="r" id="re${i}"></div></div>`+
        `<div><div class="vl" id="vl${i}"></div>`+
        `<div class="dl" id="dl${i}"></div></div>`+
        `<div class="pm"><button data-i="${i}" data-p="-0.5" `+
        `title="${L.moins}">−</button>`+
        `<button data-i="${i}" data-p="0.5" title="${L.plus}">+</button></div>`+
        `</div>`).join("")+
      `</div>`;
  }).join("")+'</div>').join("");
  document.getElementById("cols").innerHTML = html;
  document.querySelectorAll(".ba").forEach(b=>{
    b.addEventListener("click", ev=>{
      const i = +b.dataset.i, r = b.getBoundingClientRect();
      const v = Math.round((ev.clientX - r.left) / r.width * 20) / 2;
      const id = N[i].id;
      /* un deuxième clic au même endroit libère la variable */
      if (tenu[id] !== undefined && Math.abs(tenu[id] - v) < 0.26) delete tenu[id];
      else tenu[id] = borne(v);
      relancer();
    });
  });
  /* LE RÉGLAGE PAR DEMI-POINT PART DE LÀ OÙ EN EST LA VARIABLE : de la valeur
     déjà imposée si elle en porte une, sinon de sa valeur mesurée. Revenir
     exactement sur la mesure libère la variable — sans quoi « je remets comme
     avant » laisserait une variable tenue à sa propre valeur, ce qui n'est pas
     la même chose que de ne pas la tenir : elle serait alors bloquée là et ne
     recevrait plus rien du système. */
  document.querySelectorAll(".pm button").forEach(b=>{
    b.addEventListener("click", ()=>{
      const i = +b.dataset.i, id = N[i].id;
      const dep = tenu[id] !== undefined ? tenu[id] : base[i];
      const v = borne(Math.round((dep + (+b.dataset.p)) * 2) / 2);
      if (Math.abs(v - base[i]) < 0.001) delete tenu[id];
      else tenu[id] = v;
      relancer();
    });
  });
}

/* LE SYSTÈME PART TOUT SEUL. Il fallait poser une valeur PUIS trouver le
   bouton Lecture ; entre les deux, on voyait une seule barre bouger, et l'on
   concluait qu'il ne se passait rien. Poser une valeur EST la demande de
   propagation. Lecture et Pause restent, pour reprendre la main sur une
   propagation qu'on veut suivre pas à pas. */
function relancer(){
  k = 0; d = d0(); dprec = new Float64Array(NN);
  dessiner();
  arreter();
  if (Object.keys(tenu).length) lancer();
}

function dessiner(){
  let nh = 0, nb = 0, somme = 0, cnt = 0, bouge = 0;
  N.forEach((n,i)=>{
    const v = niveau(i), ecart = v - base[i];
    const pas = Math.abs(d[i] - dprec[i]);
    bouge = Math.max(bouge, pas);
    if (ecart > 0.05) nh++; else if (ecart < -0.05) nb++;
    if (n.mesure){ somme += v; cnt++; }
    const coul = Math.abs(ecart) < 0.05 ? "#c8d0dc" : (ecart>0?HAUSSE:BAISSE);
    document.getElementById("fi"+i).style.width = (v*10)+"%";
    document.getElementById("fi"+i).style.background = coul;
    document.getElementById("re"+i).style.left = (base[i]*10)+"%";
    document.getElementById("vl"+i).textContent = v.toFixed(1).replace(".",",");
    document.getElementById("vl"+i).style.color =
      Math.abs(ecart) < 0.05 ? "#3c4761" : coul;
    const dl = document.getElementById("dl"+i);
    dl.textContent = Math.abs(ecart) < 0.05 ? (n.mesure ? "" : "?")
      : (ecart>0?"+":"−") + Math.abs(ecart).toFixed(2).replace(".",",");
    dl.style.color = Math.abs(ecart) < 0.05 ? "#9aa4b5" : coul;
    const t = tenu[N[i].id] !== undefined;
    document.getElementById("ba"+i).classList.toggle("t", t);
    document.getElementById("nm"+i).classList.toggle("t", t);
  });
  document.getElementById("kk").textContent = k;
  document.getElementById("nt").textContent = Object.keys(tenu).length;
  document.getElementById("nh").textContent = nh;
  document.getElementById("nb").textContent = nb;
  /* LA MOYENNE SEULE NE DIT RIEN : c'est son écart au départ qui compte, et
     il est écrit sous elle plutôt que laissé à calculer de tête. */
  document.getElementById("mo").textContent =
    cnt ? (somme/cnt).toFixed(2).replace(".",",") : "—";
  const dm = cnt ? somme/cnt - MOY0 : 0;
  document.getElementById("mos").innerHTML = L.moy +
    (Math.abs(dm) > 0.005
      ? ` · <b style="font-size:11px;color:${dm>0?HAUSSE:BAISSE}">`+
        `${dm>0?"+":"−"}${Math.abs(dm).toFixed(2).replace(".",",")}</b>`
      : "");
  /* CE QUE ÇA DÉPLACE, NOMMÉ : les huit plus gros écarts, la variable tenue
     exclue. Son propre mouvement est imposé et n'apprend rien ; ce qu'on
     veut lire, c'est ce que le modèle en a fait ailleurs. */
  const bil = document.getElementById("bilan");
  if (!Object.keys(tenu).length){ bil.innerHTML = ""; }
  else {
    const bouges = N.map((n,i)=>({n, e: niveau(i) - base[i]}))
      .filter(x => tenu[x.n.id] === undefined && Math.abs(x.e) >= 0.05)
      .sort((a,b)=>Math.abs(b.e) - Math.abs(a.e)).slice(0, 8);
    bil.className = "bil";
    bil.innerHTML = "<h5>" + L.bilan + "</h5>" + (bouges.length
      ? '<div class="rg">' + bouges.map(x =>
          '<span class="it">' + x.n.nom +
          '<b style="color:' + (x.e > 0 ? HAUSSE : BAISSE) + '">' +
          (x.e > 0 ? "+" : "−") +
          Math.abs(x.e).toFixed(2).replace(".", ",") + "</b></span>").join("")
        + "</div>"
      : "<p>" + L.bilan0 + "</p>");
  }
  /* LES DEUX BOUTONS DE COURSE NE S'ALLUMENT QUE S'IL Y A QUELQUE CHOSE À
     PROPAGER. Sans variable tenue, l'écart de départ est nul : la course
     tourne à vide, le compteur monte et le dessin ne bouge pas d'un pixel. */
  const rien = !Object.keys(tenu).length;
  document.getElementById("play").disabled = rien;
  document.getElementById("pas").disabled = rien;
  document.getElementById("amorce").style.display = rien ? "" : "none";
  const e = document.getElementById("etat");
  if (rien) e.textContent = L.repos;
  else if (k > 0 && bouge < SEUIL){ e.textContent = L.stable; arreter(); }
  else e.textContent = "";
}

const bp = document.getElementById("play");
bp.onclick = ()=>{ if (!Object.keys(tenu).length) return;
                   minuteur ? arreter() : lancer(); };
document.getElementById("pas").onclick = ()=>{
  if (!Object.keys(tenu).length) return;
  arreter(); avancer(); };
document.getElementById("zero").onclick = ()=>{
  arreter(); for (const id in tenu) delete tenu[id];
  k = 0; d = new Float64Array(NN); dprec = new Float64Array(NN); dessiner(); };
function lancer(){ if (!Object.keys(tenu).length) return;
                   bp.textContent = L.pause; bp.classList.remove("p");
                   minuteur = setInterval(avancer, 780); avancer(); }
function arreter(){ if (minuteur) clearInterval(minuteur); minuteur = null;
                    bp.textContent = L.lire; bp.classList.add("p"); }

construire(); dessiner();
</script></body></html>"""


def _html(d, lang):
    lib = {"lire": T("sy_lire"), "pause": T("sy_pause"),
           "stable": T("sy_stable"), "repos": T("sy_repos"),
           "non_mesure": T("sy_non_mesure"), "moy": T("sy_moyenne"),
           "bilan": T("sy_bilan"), "bilan0": T("sy_bilan_0"),
           "moins": T("sy_moins"), "plus": T("sy_plus")}
    return (GABARIT
            .replace("__DONNEES__", json.dumps(d, ensure_ascii=False,
                                               separators=(",", ":")))
            .replace("__LIBELLES__", json.dumps(lib, ensure_ascii=False))
            .replace("__COUL_DIM__", json.dumps(COUL_DIM))
            .replace("__L_LIRE__", _e(T("sy_lire")))
            .replace("__L_PAS__", _e(T("sy_pas")))
            .replace("__L_ZERO__", _e(T("sy_zero")))
            .replace("__L_TOUR__", _e(T("sy_tour")))
            .replace("__L_TENUES__", _e(T("sy_tenues")))
            .replace("__L_MONTE__", _e(T("sy_monte")))
            .replace("__L_BAISSE__", _e(T("sy_baisse")))
            .replace("__L_MOY__", _e(T("sy_moyenne")))
            .replace("__L_REPERE__", _e(T("sy_repere")))
            .replace("__L_AMORCE__", _e(T("sy_amorce")))
            .replace("__L_AIDE__", _e(T("sy_aide"))))


def render(entete=True):
    lang = i18n.get_lang()
    d = _systeme(lang)
    if not d:
        st.info(T("sy_absent"))
        return

    if entete:
        st.markdown(
            f'<h2 style="font-size:21.5px;font-weight:700;color:{ENCRE};'
            f'letter-spacing:-.02em;margin:2px 0 0">{_e(T("sy_titre"))}</h2>'
            f'<p style="font-size:11.5px;color:{ENCRE3};letter-spacing:.06em;'
            f'text-transform:uppercase;margin:2px 0 0;font-weight:600">'
            f'{_e(T("sy_sous"))}</p>', unsafe_allow_html=True)

    st.markdown(
        f'<div style="background:#fff;border:1px solid {BORD};border-left:5px '
        f'solid #1a6b52;border-radius:14px;padding:13px 17px;font-size:14.5px;'
        f'color:{ENCRE2};line-height:1.6;margin:10px 0 8px;max-width:96ch;'
        f'text-align:left">{T("sy_intro")}</div>', unsafe_allow_html=True)

    components.html(_html(d, lang), height=880, scrolling=False)
    st.caption(T("sy_avert"))
