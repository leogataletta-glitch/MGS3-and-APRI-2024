"""La carte interactive du « Territoire » — un gestionnaire de couches.

CE QU'ELLE EST, ET CE QU'ELLE N'EST PAS

Elle répond à « où », et à rien d'autre. Aucun score, aucun classement, aucun
pourcentage, aucun indicateur de résilience n'y entre — pas même en couleur de
remplissage. Une carte qui teinte les sections selon un résultat répond à
« combien » avant qu'on ait fini de se situer, et le lecteur venu chercher un
lieu repart avec un chiffre qu'il n'a pas demandé. Les couleurs employées ici
sont des couleurs d'identité (une par famille de couches), jamais des couleurs
de valeur.

POURQUOI LEAFLET ÉCRIT À LA MAIN PLUTÔT QU'UNE BIBLIOTHÈQUE STREAMLIT

`folium` et `streamlit-folium` feraient la moitié du travail, mais ajouteraient
deux dépendances à installer sur Streamlit Cloud à chaque démarrage — et leur
gestionnaire de couches est une liste plate, sans catégories, sans « tout
afficher », sans compte d'objets. Ici, la page fabrique un document HTML
autonome : Leaflet vient d'un CDN, chargé par le navigateur du lecteur, et le
reste — panneau de couches, groupes repliables, popups, retour à l'emprise —
tient dans ce fichier. Rien à installer côté serveur.

LE PANNEAU EST LA LÉGENDE, ET LA LÉGENDE EST LE PANNEAU

C'était la demande, et c'est aussi la bonne façon de faire : une légende qui
décrit une couche qu'on ne peut pas éteindre oblige à lire ce qu'on ne veut pas
voir. Chaque ligne du panneau porte son symbole, son intitulé, son compte
d'objets, et commande exactement une couche de la carte.

LES POINTS D'ENTRETIEN

Ce sont les 1 195 points de l'échantillon tiré, tels qu'ils ont été relevés sur
le terrain. Leur popup ne porte que le numéro d'ordre, la section et le
paysage : ni nom, ni téléphone, ni enquêteur — ces colonnes n'existent pas dans
les fichiers d'échantillon, et rien de tel n'est embarqué dans la page.
"""

import json
import os

import streamlit as st
import streamlit.components.v1 as components

import i18n
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

TEXTES = {
    "cl_titre": {"en": "Interactive location map",
                 "fr": "Carte de localisation interactive"},
    "cl_note": {
        "en": "Every layer can be switched on or off from the panel on the "
              "right. Scroll to zoom, drag to pan, and the button returns to "
              "the initial extent.",
        "fr": "Chaque couche s'allume et s'éteint depuis le panneau de droite. "
              "La molette zoome, le glissement déplace, et le bouton revient "
              "à l'emprise initiale."},
    "cl_absent": {"en": "Map layer file missing (data/carte_localisation.json).",
                  "fr": "Le fichier des couches est absent "
                        "(data/carte_localisation.json)."},

    # --- panneau
    "cl_couches": {"en": "Layers", "fr": "Couches"},
    "cl_tout": {"en": "Show all", "fr": "Tout afficher"},
    "cl_rien": {"en": "Hide all", "fr": "Tout masquer"},
    "cl_emprise": {"en": "Initial extent", "fr": "Emprise initiale"},
    "cl_g_fond": {"en": "Base map", "fr": "Fond de carte"},
    "cl_g_limites": {"en": "Administrative boundaries",
                     "fr": "Limites administratives"},
    "cl_g_relief": {"en": "Relief and environment",
                    "fr": "Relief et environnement"},
    "cl_g_infra": {"en": "Infrastructure", "fr": "Infrastructure"},
    "cl_g_etude": {"en": "Studied territories", "fr": "Territoires étudiés"},
    "cl_g_points": {"en": "Interview points", "fr": "Points d'entretien"},

    # --- fonds
    "cl_f_plan": {"en": "Street map", "fr": "Plan"},
    "cl_f_relief": {"en": "Topographic", "fr": "Topographique"},
    "cl_f_sat": {"en": "Satellite", "fr": "Satellite"},
    "cl_f_sobre": {"en": "Plain", "fr": "Sobre"},

    # --- couches
    "cl_pays": {"en": "National boundary", "fr": "Limites nationales"},
    "cl_deps": {"en": "Departments", "fr": "Départements"},
    "cl_communes": {"en": "Communes", "fr": "Communes"},
    "cl_ombrage": {"en": "Hillshade", "fr": "Ombrage du relief"},
    "cl_ap": {"en": "Protected areas", "fr": "Aires protégées"},
    "cl_riv": {"en": "Rivers", "fr": "Cours d'eau"},
    "cl_rp": {"en": "Main roads", "fr": "Routes principales"},
    "cl_rs": {"en": "Secondary roads", "fr": "Routes secondaires"},
    "cl_paysage": {"en": "Grand'Anse pilot landscape",
                   "fr": "Paysage pilote de la Grand'Anse"},
    "cl_sections": {"en": "Communal sections surveyed",
                    "fr": "Sections communales étudiées"},
    "cl_villes": {"en": "Reference towns", "fr": "Villes-repères"},
    "cl_pts_l": {"en": "Coastal landscape", "fr": "Paysage littoral"},
    "cl_pts_m": {"en": "Mountain landscape", "fr": "Paysage montagne"},

    # --- popups
    "cl_pop_point": {"en": "Interview point", "fr": "Point d'entretien"},
    "cl_pop_section": {"en": "Communal section", "fr": "Section communale"},
    "cl_pop_commune": {"en": "Commune", "fr": "Commune"},
    "cl_pop_dep": {"en": "Department", "fr": "Département"},
    "cl_pop_pays": {"en": "Landscape", "fr": "Paysage"},
    "cl_pop_ap": {"en": "Protected area", "fr": "Aire protégée"},
    "cl_pop_ville": {"en": "Town", "fr": "Ville"},

    # --- pied
    "cl_source": {
        "en": "Boundaries, protected areas and sample: UNEP Haiti GIS layers "
              "(WGS 84). Roads and rivers: OpenStreetMap. Local service roads "
              "are not a vector layer here — the street base map already "
              "carries them. Relief: Esri hillshade tiles.",
        "fr": "Limites, aires protégées et échantillon : couches SIG du PNUE "
              "Haïti (WGS 84). Routes et cours d'eau : OpenStreetMap. Les "
              "routes de desserte locale ne sont pas une couche vectorielle "
              "ici — le fond de plan les porte déjà. Relief : tuiles "
              "d'ombrage Esri."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)

# Les couleurs sont des couleurs D'IDENTITÉ : une famille de couches, une
# teinte. Aucune ne code une valeur — c'est la règle de la page.
COULEURS = {
    "pays": "#6b7590",
    "deps": "#3c4761",
    "communes": "#9aa4b5",
    "ap": "#1f8f5f",
    "riv": "#2a78d6",
    "rp": "#c1521f",
    "rs": "#d98b57",
    "paysage": "#7048b6",
    "sections": "#1c6349",
    "villes": "#101728",
    "pts_l": "#1f6fbf",
    "pts_m": "#a4531f",
}


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


@st.cache_data(show_spinner=False)
def _couches():
    p = os.path.join(DATA, "carte_localisation.json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def _leaflet():
    """Leaflet, embarqué dans le dépôt plutôt qu'appelé sur un CDN.

    DEUX RAISONS, DONT UNE QUI COMPTE VRAIMENT. La petite : je ne peux pas
    vérifier une carte dont la bibliothèque ne se charge pas dans mon
    navigateur de test. La grande : ce site se consulte depuis Haïti, où une
    connexion peut atteindre le serveur de l'application sans atteindre
    unpkg.com — et une carte dont le moteur manque n'affiche rien du tout,
    pas même un fond. Les 160 ko voyagent donc avec la page. Si les deux
    fichiers venaient à manquer du dépôt, on retombe sur le CDN : mieux vaut
    une carte qui dépend d'un tiers qu'une page blanche.
    """
    js = os.path.join(DATA, "leaflet.js")
    css = os.path.join(DATA, "leaflet.css")
    if os.path.exists(js) and os.path.exists(css):
        with open(css, encoding="utf-8") as f:
            c = f.read()
        with open(js, encoding="utf-8") as f:
            j = f.read()
        return f"<style>{c}</style>\n<script>{j}</script>"
    return ('<link rel="stylesheet" '
            'href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>\n'
            '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js">'
            '</script>')


GABARIT = r"""<!DOCTYPE html><html><head><meta charset="utf-8">
__LEAFLET__
<style>
 html,body{margin:0;padding:0;height:100%;font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif}
 #carte{position:absolute;inset:0;border-radius:12px}
 .leaflet-container{background:#dfe9f2;border-radius:12px;font-family:inherit}
 /* --- le panneau de couches ------------------------------------------- */
 #panneau{position:absolute;top:10px;right:10px;bottom:10px;width:264px;
   background:rgba(255,255,255,.96);border:1px solid #dbe3ec;border-radius:12px;
   box-shadow:0 6px 24px rgba(16,23,40,.16);z-index:1000;display:flex;
   flex-direction:column;overflow:hidden}
 #panneau .tete{padding:10px 12px 8px;border-bottom:1px solid #eef2f7}
 #panneau .titre{font-size:10.5px;font-weight:700;letter-spacing:.1em;
   text-transform:uppercase;color:#6b7590}
 #panneau .boutons{display:flex;gap:6px;margin-top:8px;flex-wrap:wrap}
 #panneau button{font:inherit;font-size:11px;font-weight:600;color:#3c4761;
   background:#f2f6fa;border:1px solid #dbe3ec;border-radius:999px;
   padding:4px 10px;cursor:pointer}
 #panneau button:hover{background:#e9f3ee;border-color:#bcdccb;color:#101728}
 #liste{overflow-y:auto;padding:6px 4px 10px;flex:1}
 .groupe{margin:2px 0 0}
 .groupe > .entete{display:flex;align-items:center;gap:6px;cursor:pointer;
   padding:7px 10px 5px;font-size:10.5px;font-weight:700;letter-spacing:.07em;
   text-transform:uppercase;color:#8a93a5;user-select:none}
 .groupe > .entete:hover{color:#3c4761}
 .fleche{transition:transform .15s ease;font-size:9px;color:#9aa4b5}
 .groupe.ferme .fleche{transform:rotate(-90deg)}
 .groupe.ferme .corps{display:none}
 .ligne{display:flex;align-items:center;gap:8px;padding:4px 10px;
   border-radius:7px;cursor:pointer}
 .ligne:hover{background:#f4f8f6}
 .ligne input{margin:0;accent-color:#1c6349;cursor:pointer}
 .ligne .lib{font-size:12.5px;color:#3c4761;flex:1;line-height:1.25}
 .ligne .nb{font-size:10.5px;color:#9aa4b5;font-variant-numeric:tabular-nums}
 .sym{width:20px;height:12px;flex:0 0 20px;display:inline-block}
 .sym i{display:block;width:100%;height:100%}
 .leaflet-popup-content{margin:10px 12px;font-size:12.5px;color:#3c4761}
 .leaflet-popup-content b{color:#101728}
 .pop-t{font-size:10px;letter-spacing:.08em;text-transform:uppercase;
   color:#8a93a5;font-weight:700;display:block;margin-bottom:2px}
 @media(max-width:820px){#panneau{width:210px}}
</style></head><body>
<div id="carte"></div>
<div id="panneau">
  <div class="tete">
    <div class="titre">__T_COUCHES__</div>
    <div class="boutons">
      <button onclick="tout(true)">__T_TOUT__</button>
      <button onclick="tout(false)">__T_RIEN__</button>
      <button onclick="recadrer()">__T_EMPRISE__</button>
    </div>
  </div>
  <div id="liste"></div>
</div>
<script>
const D = __DONNEES__;
const C = __COULEURS__;
const L_ = __LIBELLES__;

const carte = L.map('carte', {zoomControl:true, preferCanvas:true,
                              attributionControl:true});
const EMPRISE = [[17.98,-74.55],[18.68,-73.55]];
function recadrer(){ carte.fitBounds(EMPRISE, {padding:[12,12]}); }
recadrer();

/* ---- fonds de carte : un seul à la fois ------------------------------- */
const FONDS = {
  plan:  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',
          {maxZoom:19, attribution:'© OpenStreetMap'}),
  relief:L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
          {maxZoom:17, attribution:'© OpenTopoMap, © OpenStreetMap'}),
  sat:   L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
          {maxZoom:19, attribution:'Esri, Maxar, Earthstar Geographics'}),
  sobre: L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
          {maxZoom:19, attribution:'© OpenStreetMap, © CARTO'})
};
let fondActif = 'plan';
FONDS.plan.addTo(carte);
function choisirFond(k){
  if (k === fondActif) return;
  carte.removeLayer(FONDS[fondActif]);
  fondActif = k;
  FONDS[k].addTo(carte).bringToBack();
}

/* ---- fabrication des couches vectorielles ----------------------------- */
function pop(titre, corps){ return '<span class="pop-t">'+titre+'</span>'+corps; }

function polys(items, cle, opt, popup){
  const g = L.layerGroup();
  (items||[]).forEach(function(o){
    (o.a||[]).forEach(function(anneau){
      const p = L.polygon(anneau.map(c => [c[1], c[0]]), opt);
      if (popup) { const h = popup(o.p); if (h) p.bindPopup(h); }
      g.addLayer(p);
    });
  });
  return g;
}
function lignes(items, opt, popup){
  const g = L.layerGroup();
  (items||[]).forEach(function(o){
    const p = L.polyline((o.l||[]).map(c => [c[1], c[0]]), opt);
    if (popup) { const h = popup(o.p); if (h) p.bindPopup(h); }
    g.addLayer(p);
  });
  return g;
}

const COUCHES = {};

COUCHES.pays = polys(D.pays, 'pays',
  {color:C.pays, weight:1.6, fill:false, opacity:.9});
COUCHES.deps = polys(D.departements, 'deps',
  {color:C.deps, weight:1.8, dashArray:'7 5', fill:false, opacity:.95},
  p => p && p.nom ? pop(L_.dep, '<b>'+p.nom+'</b>') : null);
COUCHES.communes = polys(D.communes, 'communes',
  {color:C.communes, weight:1.1, fill:false, opacity:.95},
  p => p && p.NAME ? pop(L_.commune, '<b>'+p.NAME+'</b>') : null);
COUCHES.ap = polys(D.aires_protegees, 'ap',
  {color:C.ap, weight:1.6, fillColor:C.ap, fillOpacity:.16},
  p => p && p.Name ? pop(L_.ap, '<b>'+p.Name+'</b>') : null);
COUCHES.riv = lignes(D.rivieres, {color:C.riv, weight:1.3, opacity:.75});
COUCHES.rp = lignes(D.routes_p, {color:C.rp, weight:2.4, opacity:.9});
COUCHES.rs = lignes(D.routes_s, {color:C.rs, weight:1.5, opacity:.85});
COUCHES.paysage = polys(D.paysage_ga, 'paysage',
  {color:C.paysage, weight:2, dashArray:'4 4', fillColor:C.paysage,
   fillOpacity:.08},
  p => pop(L_.paysage_t, '<b>' + L_.paysage + '</b>'));
COUCHES.sections = polys(D.sections, 'sections',
  {color:'#ffffff', weight:1.6, fillColor:C.sections, fillOpacity:.34},
  function(p){
    if (!p || !p.section) return null;
    return pop(L_.section, '<b>'+p.section+'</b><br>'+
      (p.commune||'') + (p.departement ? ' · ' + p.departement : ''));
  });

COUCHES.villes = L.layerGroup();
(D.villes||[]).forEach(function(v){
  const m = L.circleMarker([v.pt[1], v.pt[0]],
    {radius:5, color:'#ffffff', weight:2, fillColor:C.villes, fillOpacity:1});
  m.bindPopup(pop(L_.ville, '<b>'+(v.p.Nom||'')+'</b>'));
  m.bindTooltip(v.p.Nom||'', {permanent:true, direction:'right',
                              className:'etq-ville', offset:[6,0]});
  COUCHES.villes.addLayer(m);
});

/* Les points d'entretien : DEUX couches, une par paysage, pour qu'on puisse
   comparer littoral et montagne en éteignant l'un des deux. */
COUCHES.pts_l = L.layerGroup();
COUCHES.pts_m = L.layerGroup();
(D.entretiens||[]).forEach(function(e){
  const mont = (e[3] === 'Montagne');
  const m = L.circleMarker([e[1], e[0]], {
    radius:3.4, weight:1, color:'#ffffff', opacity:.9,
    fillColor: mont ? C.pts_m : C.pts_l, fillOpacity:.95});
  m.bindPopup(pop(L_.point, '<b>n° '+(e[4]||'')+'</b><br>'+e[2]+
                  '<br><span style="color:#8a93a5">'+e[3]+'</span>'));
  (mont ? COUCHES.pts_m : COUCHES.pts_l).addLayer(m);
});

/* L'ombrage est une couche de tuiles, pas un vecteur : le relief se lit à
   toutes les échelles et ne pèse rien dans la page. */
COUCHES.ombrage = L.tileLayer(
  'https://server.arcgisonline.com/ArcGIS/rest/services/Elevation/World_Hillshade/MapServer/tile/{z}/{y}/{x}',
  {maxZoom:16, opacity:.5, attribution:'Esri'});

/* ---- le panneau ------------------------------------------------------- */
const GROUPES = __GROUPES__;
const ETAT = {};

function symbole(s){
  if (s.type === 'ligne')
    return '<i style="border-top:'+(s.w||2)+'px '+(s.d?'dashed':'solid')+' '+
           s.c+';margin-top:5px"></i>';
  if (s.type === 'point')
    return '<i style="width:9px;height:9px;border-radius:50%;background:'+s.c+
           ';border:1.5px solid #fff;box-shadow:0 0 0 1px '+s.c+
           '55;margin:1px auto"></i>';
  if (s.type === 'tuile')
    return '<i style="background:linear-gradient(135deg,#8d99a6,#e8edf2);'+
           'border-radius:3px"></i>';
  return '<i style="background:'+s.c+'2e;border:1.5px '+(s.d?'dashed':'solid')+
         ' '+s.c+';border-radius:3px"></i>';
}

function construire(){
  const hote = document.getElementById('liste');
  GROUPES.forEach(function(g, ig){
    const div = document.createElement('div');
    div.className = 'groupe' + (g.ferme ? ' ferme' : '');
    let h = '<div class="entete" onclick="this.parentNode.classList.toggle(\'ferme\')">'+
            '<span class="fleche">▼</span>'+g.titre+'</div><div class="corps">';
    g.lignes.forEach(function(l){
      if (l.fond){
        h += '<label class="ligne"><input type="radio" name="fond" value="'+
             l.cle+'"'+(l.on?' checked':'')+' onchange="choisirFond(this.value)">'+
             '<span class="sym">'+symbole(l.sym||{type:'tuile'})+'</span>'+
             '<span class="lib">'+l.titre+'</span></label>';
      } else {
        h += '<label class="ligne"><input type="checkbox" data-cle="'+l.cle+'"'+
             (l.on?' checked':'')+' onchange="basculer(this.dataset.cle,this.checked)">'+
             '<span class="sym">'+symbole(l.sym)+'</span>'+
             '<span class="lib">'+l.titre+'</span>'+
             (l.nb ? '<span class="nb">'+l.nb+'</span>' : '')+'</label>';
      }
    });
    hote.appendChild(div);
    div.innerHTML = h + '</div>';
  });
}

function basculer(cle, on){
  const c = COUCHES[cle];
  if (!c) return;
  ETAT[cle] = on;
  if (on) { carte.addLayer(c); reordonner(); } else { carte.removeLayer(c); }
}

/* L'ORDRE DE SUPERPOSITION EST REFAIT À CHAQUE ALLUMAGE. Leaflet empile les
   couches dans l'ordre où on les ajoute : sans cela, rallumer les communes
   après les points d'entretien couvrait les points d'un aplat. */
const ORDRE = ['ombrage','paysage','ap','sections','communes','deps','pays',
               'riv','rs','rp','pts_l','pts_m','villes'];
function reordonner(){
  ORDRE.forEach(function(k){
    const c = COUCHES[k];
    if (c && carte.hasLayer(c) && c.bringToFront) c.bringToFront();
    else if (c && carte.hasLayer(c) && c.eachLayer)
      c.eachLayer(function(x){ if (x.bringToFront) x.bringToFront(); });
  });
}

function tout(on){
  document.querySelectorAll('#liste input[type=checkbox]').forEach(function(i){
    i.checked = on; basculer(i.dataset.cle, on);
  });
}

construire();
GROUPES.forEach(function(g){ g.lignes.forEach(function(l){
  if (!l.fond && l.on) basculer(l.cle, true); }); });
L.control.scale({imperial:false, position:'bottomleft'}).addTo(carte);
</script>
<style>.etq-ville{background:none;border:none;box-shadow:none;color:#101728;
 font-weight:700;font-size:11.5px;text-shadow:0 0 3px #fff,0 0 3px #fff,
 0 0 3px #fff;padding:0}</style>
</body></html>
"""


def _groupes(d):
    """Le contenu du panneau : chaque ligne commande exactement une couche."""
    n = lambda k: len(d.get(k) or [])
    litt = sum(1 for e in d.get("entretiens") or [] if e[3] != "Montagne")
    mont = sum(1 for e in d.get("entretiens") or [] if e[3] == "Montagne")
    return [
        {"titre": T("cl_g_fond"), "ferme": False, "lignes": [
            {"cle": "plan", "titre": T("cl_f_plan"), "fond": True, "on": True},
            {"cle": "relief", "titre": T("cl_f_relief"), "fond": True},
            {"cle": "sat", "titre": T("cl_f_sat"), "fond": True},
            {"cle": "sobre", "titre": T("cl_f_sobre"), "fond": True},
        ]},
        {"titre": T("cl_g_etude"), "ferme": False, "lignes": [
            {"cle": "sections", "titre": T("cl_sections"), "on": True,
             "nb": n("sections"),
             "sym": {"type": "poly", "c": COULEURS["sections"]}},
            {"cle": "paysage", "titre": T("cl_paysage"), "nb": n("paysage_ga"),
             "sym": {"type": "poly", "c": COULEURS["paysage"], "d": True}},
            {"cle": "villes", "titre": T("cl_villes"), "on": True,
             "nb": n("villes"),
             "sym": {"type": "point", "c": COULEURS["villes"]}},
        ]},
        {"titre": T("cl_g_points"), "ferme": False, "lignes": [
            {"cle": "pts_l", "titre": T("cl_pts_l"), "on": True, "nb": litt,
             "sym": {"type": "point", "c": COULEURS["pts_l"]}},
            {"cle": "pts_m", "titre": T("cl_pts_m"), "on": True, "nb": mont,
             "sym": {"type": "point", "c": COULEURS["pts_m"]}},
        ]},
        {"titre": T("cl_g_limites"), "ferme": False, "lignes": [
            {"cle": "deps", "titre": T("cl_deps"), "on": True, "nb": n("departements"),
             "sym": {"type": "ligne", "c": COULEURS["deps"], "d": True}},
            {"cle": "communes", "titre": T("cl_communes"), "nb": n("communes"),
             "sym": {"type": "ligne", "c": COULEURS["communes"], "w": 1}},
            {"cle": "pays", "titre": T("cl_pays"), "nb": n("pays"),
             "sym": {"type": "ligne", "c": COULEURS["pays"]}},
        ]},
        {"titre": T("cl_g_infra"), "ferme": False, "lignes": [
            {"cle": "rp", "titre": T("cl_rp"), "on": True, "nb": n("routes_p"),
             "sym": {"type": "ligne", "c": COULEURS["rp"], "w": 3}},
            {"cle": "rs", "titre": T("cl_rs"), "nb": n("routes_s"),
             "sym": {"type": "ligne", "c": COULEURS["rs"]}},
        ]},
        {"titre": T("cl_g_relief"), "ferme": False, "lignes": [
            {"cle": "ombrage", "titre": T("cl_ombrage"),
             "sym": {"type": "tuile"}},
            {"cle": "riv", "titre": T("cl_riv"), "nb": n("rivieres"),
             "sym": {"type": "ligne", "c": COULEURS["riv"], "w": 1.5}},
            {"cle": "ap", "titre": T("cl_ap"), "nb": n("aires_protegees"),
             "sym": {"type": "poly", "c": COULEURS["ap"]}},
        ]},
    ]


def html(d):
    libelles = {
        "dep": T("cl_pop_dep"), "commune": T("cl_pop_commune"),
        "ap": T("cl_pop_ap"), "ville": T("cl_pop_ville"),
        "section": T("cl_pop_section"), "point": T("cl_pop_point"),
        "paysage": T("cl_paysage"), "paysage_t": T("cl_g_etude"),
    }
    return (GABARIT
            .replace("__LEAFLET__", _leaflet())
            .replace("__DONNEES__", json.dumps(d, ensure_ascii=False,
                                               separators=(",", ":")))
            .replace("__COULEURS__", json.dumps(COULEURS))
            .replace("__LIBELLES__", json.dumps(libelles, ensure_ascii=False))
            .replace("__GROUPES__", json.dumps(_groupes(d), ensure_ascii=False))
            .replace("__T_COUCHES__", _e(T("cl_couches")))
            .replace("__T_TOUT__", _e(T("cl_tout")))
            .replace("__T_RIEN__", _e(T("cl_rien")))
            .replace("__T_EMPRISE__", _e(T("cl_emprise"))))


def render(hauteur=660):
    d = _couches()
    if not d:
        st.info(T("cl_absent"))
        return
    st.markdown(f'<div class="titre-bloc">{_e(T("cl_titre"))}</div>',
                unsafe_allow_html=True)
    components.html(html(d), height=hauteur, scrolling=False)
    # LA SOURCE EST SOUS LA CARTE, PAS DANS LE PANNEAU. Elle y occupait un
    # cinquième de la hauteur du panneau — de la place prise à la liste des
    # couches, qui est ce qu'on vient y chercher — et personne ne lit une
    # source pendant qu'il cherche une case à cocher.
    st.caption(T("cl_note") + "  \n" + T("cl_source"))
