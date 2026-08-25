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
              "different value: that variable is then held, and the gap it "
              "creates travels through the model. Press play and each "
              "variable rises or falls according to what its neighbours do to "
              "it, until everything settles.",
        "fr": "Chaque variable porte un niveau sur dix, celui mesuré par "
              "l'enquête là où il existe. Cliquez dans une barre pour lui "
              "imposer une autre valeur : la variable est alors tenue, et "
              "l'écart qu'elle crée circule dans le modèle. Appuyez sur "
              "lecture et chaque variable monte ou descend selon ce que ses "
              "voisines lui font, jusqu'à stabilisation."},
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
    "sy_aide": {"en": "click in the bar to impose a value",
                "fr": "cliquez dans la barre pour imposer une valeur"},
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
 .li{display:grid;grid-template-columns:1fr 96px 46px;gap:8px;
     align-items:center;padding:2px 0}
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
 .lg{display:flex;gap:16px;flex-wrap:wrap;font-size:11.5px;color:#6b7590;
     margin-top:10px;align-items:center}
 .lg i{display:inline-block;width:10px;height:10px;border-radius:2px;
       margin-right:5px;vertical-align:-1px}
</style></head><body>
<div class="barre">
  <button class="bt p" id="play">__L_LIRE__</button>
  <button class="bt" id="pas">__L_PAS__</button>
  <button class="bt" id="zero">__L_ZERO__</button>
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
        `<div class="dl" id="dl${i}"></div></div></div>`).join("")+
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
      k = 0; d = d0(); dprec = new Float64Array(NN);
      dessiner();
    });
  });
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
  const e = document.getElementById("etat");
  if (!Object.keys(tenu).length) e.textContent = L.repos;
  else if (k > 0 && bouge < SEUIL){ e.textContent = L.stable; arreter(); }
  else e.textContent = "";
}

const bp = document.getElementById("play");
bp.onclick = ()=>{ minuteur ? arreter() : lancer(); };
document.getElementById("pas").onclick = ()=>{ arreter(); avancer(); };
document.getElementById("zero").onclick = ()=>{
  arreter(); for (const id in tenu) delete tenu[id];
  k = 0; d = new Float64Array(NN); dprec = new Float64Array(NN); dessiner(); };
function lancer(){ bp.textContent = L.pause; bp.classList.remove("p");
                   minuteur = setInterval(avancer, 780); avancer(); }
function arreter(){ if (minuteur) clearInterval(minuteur); minuteur = null;
                    bp.textContent = L.lire; bp.classList.add("p"); }

construire(); dessiner();
</script></body></html>"""


def _html(d, lang):
    lib = {"lire": T("sy_lire"), "pause": T("sy_pause"),
           "stable": T("sy_stable"), "repos": T("sy_repos"),
           "non_mesure": T("sy_non_mesure"), "moy": T("sy_moyenne")}
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
