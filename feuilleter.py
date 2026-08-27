"""Feuilleter : le site se tourne page à page au lieu de se dérouler.

CE QUE FAIT CE MODULE, ET POURQUOI IL EST ÉCRIT COMME ÇA
========================================================

La demande est simple à énoncer : à 100 % de zoom, tout ce qu'on voit doit
tenir dans l'écran, et ce qui dépasse va à l'écran suivant. Partout.

Trois manières de la satisfaire, deux mauvaises :

1. DÉCOUPER CHAQUE PAGE À LA MAIN. Il faudrait rouvrir les quarante modules
   de l'application, décider où couper, et recommencer à chaque ajout de
   contenu. Pire : un découpage figé est calé sur une hauteur d'écran, donc
   il redéfile sur un portable et laisse du blanc sur un grand moniteur. Le
   travail serait à refaire pour chaque taille d'écran, ce qui est absurde.

2. FIXER LA HAUTEUR DES BLOCS EN CSS. Le contenu déborderait ou serait rogné,
   et un tableau coupé au milieu d'une ligne est pire qu'un défilement.

3. MESURER, PUIS RÉPARTIR. C'est ce qui est fait ici. Au chargement, on mesure
   la hauteur réelle de chaque bloc de premier niveau, on les empile jusqu'à
   remplir l'écran, et on recommence un écran plus loin. La répartition est
   donc juste sur l'écran qui la regarde, quel qu'il soit, et se refait toute
   seule quand on redimensionne la fenêtre.

COMMENT LE SCRIPT ATTEINT LA PAGE
=================================

Streamlit n'exécute pas les <script> insérés par st.markdown : ils arrivent
dans le DOM par dangerouslySetInnerHTML, que le navigateur n'évalue pas. Le
seul point d'entrée est st.components.v1.html, qui crée une iframe de même
origine ; de là, window.parent.document est accessible et le script travaille
sur la vraie page. Si un jour cet accès est fermé, le try/catch laisse la page
telle quelle : elle redéfile, mais rien n'est cassé.

CE QUI SURVIT AUX RÉEXÉCUTIONS
==============================

Streamlit reconstruit le DOM à chaque interaction. Deux précautions :

  — la barre de navigation est en position fixe et rattachée au <body>, hors
    de portée de React, qui ne gère que le conteneur du bloc principal ;
  — un MutationObserver surveille ce conteneur et relance la répartition dès
    que son contenu change, sans quoi une réexécution ramènerait tout le
    contenu d'un coup.

Le numéro d'écran vit dans sessionStorage, indexé par page et par langue : on
revient donc sur l'écran qu'on lisait, et pas au début, après avoir bougé un
curseur.

CE QUE ÇA NE PEUT PAS FAIRE
===========================

Un bloc plus haut que l'écran ne peut pas être coupé : un schéma, une carte,
un tableau de quarante lignes sont des objets d'un seul tenant. Ceux-là
occupent un écran à eux seuls, et cet écran-là défile. C'est la seule
exception, et elle est visible : la barre du bas le signale.
"""

import streamlit as st
import streamlit.components.v1 as components

import i18n
from i18n import T

TEXTES = {
    "fe_prec": {"en": "Previous", "fr": "Précédent"},
    "fe_suiv": {"en": "Next", "fr": "Suivant"},
    "fe_de": {"en": "of", "fr": "sur"},
    "fe_long": {"en": "this screen scrolls: one block is taller than the "
                      "window",
                "fr": "cet écran défile : un bloc est plus haut que la "
                      "fenêtre"},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)


# LA MARGE DE SÉCURITÉ, EN PIXELS. Les hauteurs mesurées bougent d'un ou deux
# pixels selon la police effectivement chargée et l'arrondi du navigateur ;
# sans ce coussin, un écran calculé au pixel près déborde d'un cheveu, et un
# cheveu suffit à faire apparaître la barre de défilement.
COUSSIN = 14

_GABARIT = """
<script>
(function () {
  var P;
  try { P = window.parent; if (!P || !P.document) return; } catch (e) { return; }
  var D = P.document;

  var CLE   = @@CLE@@;
  var MOTS  = @@MOTS@@;
  var COUSS = @@COUSSIN@@;

  P.__feuilletCle = CLE;
  P.__feuilletMots = MOTS;

  /* ---------------------------------------------------------------- style */
  if (!D.getElementById('feuillet-style')) {
    var s = D.createElement('style');
    s.id = 'feuillet-style';
    s.textContent = [
      '@keyframes feuilletFondu {',
      '  from { opacity:0; transform:translateY(7px); }',
      '  to   { opacity:1; transform:none; } }',
      '.feuillet-entre { animation:feuilletFondu .34s cubic-bezier(.22,.61,.36,1) both; }',
      '#feuillet-barre {',
      '  position:fixed; bottom:0; z-index:999990;',
      '  display:flex; align-items:center; gap:14px;',
      '  padding:9px 26px 10px; box-sizing:border-box;',
      '  background:rgba(255,255,255,.94); backdrop-filter:blur(6px);',
      '  border-top:1px solid #eef2f7;',
      '  font-family:inherit; }',
      '#feuillet-barre .fb-t { font-size:12.5px; color:#3c4761; font-weight:600;',
      '  white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }',
      '#feuillet-barre .fb-p { display:flex; gap:6px; margin-left:auto; }',
      '#feuillet-barre .fb-p i { display:block; width:24px; height:2px;',
      '  border-radius:1px; background:#e3e9f1; cursor:pointer;',
      '  transition:background .25s; }',
      '#feuillet-barre .fb-p i.on { background:#1a8a4f; }',
      '#feuillet-barre .fb-n { font-size:11.5px; color:#9aa4b5;',
      '  font-variant-numeric:tabular-nums; white-space:nowrap; }',
      '#feuillet-barre button {',
      '  background:none; border:1px solid #e3e9f1; border-radius:7px;',
      '  color:#3c4761; font-size:12.5px; font-weight:600; padding:5px 13px;',
      '  cursor:pointer; white-space:nowrap; font-family:inherit;',
      '  transition:border-color .2s, color .2s; }',
      '#feuillet-barre button:hover:not(:disabled) {',
      '  border-color:#1a8a4f; color:#1a8a4f; }',
      '#feuillet-barre button:disabled { color:#c8cfda; border-color:#f2f5f9;',
      '  cursor:default; }',
      '#feuillet-barre .fb-av { font-size:11px; color:#b98b2e; white-space:nowrap; }',
      '@media (max-width:900px){ #feuillet-barre .fb-t{display:none} }'
    ].join('\\n');
    D.head.appendChild(s);
  }

  /* ------------------------------------------------- les pièces de la page */
  function conteneur() {
    return D.querySelector('[data-testid="stMainBlockContainer"]');
  }
  function pile() {
    var c = conteneur();
    if (!c) return null;
    return c.querySelector(':scope > [data-testid="stVerticalBlock"]');
  }

  /* LA BARRE. Rattachée au <body> et en position fixe : React ne gère que le
     conteneur du bloc principal, donc une barre posée ailleurs survit aux
     réexécutions au lieu d'être balayée à chaque interaction. */
  function barre() {
    var b = D.getElementById('feuillet-barre');
    if (!b) {
      b = D.createElement('div');
      b.id = 'feuillet-barre';
      b.innerHTML =
        '<button type="button" data-f="prec"></button>' +
        '<button type="button" data-f="suiv"></button>' +
        '<span class="fb-t"></span>' +
        '<span class="fb-av"></span>' +
        '<span class="fb-p"></span>' +
        '<span class="fb-n"></span>';
      D.body.appendChild(b);
    }
    /* LE GESTIONNAIRE EST RÉASSIGNÉ À CHAQUE INSTANCE, PAR PROPRIÉTÉ.
       Streamlit recrée l'iframe du composant à chaque réexécution : une
       nouvelle instance du script démarre, avec sa propre répartition en
       écrans. La barre, elle, n'est créée qu'une fois. Un addEventListener
       posé à la création resterait donc branché sur la toute première
       instance — les boutons recevaient bien le clic, et ne faisaient rien.
       L'affectation de `onclick` remplace au lieu d'empiler : c'est toujours
       l'instance la plus récente qui répond, et jamais deux à la fois. */
    b.onclick = function (ev) {
      var t = ev.target.closest('[data-f]');
      if (t) { aller(t.getAttribute('data-f') === 'prec' ? -1 : 1); return; }
      var q = ev.target.closest('.fb-p i');
      if (q) { poser(parseInt(q.getAttribute('data-k'), 10)); }
    };
    return b;
  }

  /* --------------------------------------------------------- la mémoire */
  function cleMem() { return 'feuillet:' + (P.__feuilletCle || '?'); }
  function lire() {
    try { return parseInt(P.sessionStorage.getItem(cleMem()) || '0', 10) || 0; }
    catch (e) { return 0; }
  }
  function ecrire(k) {
    try { P.sessionStorage.setItem(cleMem(), String(k)); } catch (e) {}
  }

  /* ------------------------------------------------------- la répartition */
  var groupes = [];

  /* LA LISTE DES ÉLÉMENTS TOUCHÉS EST PARTAGÉE ENTRE LES INSTANCES.
     Une nouvelle instance du script démarre à chaque réexécution de la page.
     Si chacune tenait sa propre liste, elle serait incapable de réafficher ce
     que la précédente avait masqué : les blocs cachés par l'instance d'avant
     restaient invisibles pour toujours, et le récit du premier chapitre du
     rapport s'arrêtait au bout de deux lignes. La liste vit donc sur la page,
     pas dans l'instance. */
  if (!P.__feuilletTouches) P.__feuilletTouches = [];

  /* LE REMBOURRAGE BAS DE STREAMLIT EST RENDU INUTILE PAR LA BARRE. Le
     conteneur principal réserve cent soixante pixels sous le contenu pour
     que le dernier élément ne colle pas au bord. Avec une barre fixe posée
     là, cet espace ne sert plus à rien — mais il continue de compter dans la
     hauteur défilable, et l'écran redéfilait de cent pixels alors que son
     contenu tenait. */
  function degarnir() {
    var c = conteneur();
    if (c && c.style.paddingBottom !== '10px') c.style.paddingBottom = '10px';
  }

  /* TOUT SE MESURE DANS LE REPÈRE DE LA MISE EN PAGE, PAS DANS CELUI DE L'ŒIL.
     L'application applique un `zoom` de 0,88 à toute la zone de contenu.
     getBoundingClientRect rend alors des pixels VISUELS, déjà rétrécis, tandis
     que le navigateur décide d'afficher une barre de défilement en comparant
     scrollHeight et clientHeight, qui sont en pixels de MISE EN PAGE. Mélanger
     les deux donne un calcul juste à l'œil et faux pour le navigateur : le
     contenu semblait tenir, et la page défilait quand même de quatre-vingts
     pixels. offsetHeight travaille dans le bon repère ; c'est lui qu'on prend,
     et la hauteur de la barre, qui est hors de la zone zoomée, est convertie. */
  function facteurZoom() {
    var sc = D.querySelector('section.stMain');
    if (!sc) return 1;
    var z = parseFloat(P.getComputedStyle(sc).zoom);
    return (z && z > 0.1) ? z : 1;
  }

  function hauteurDispo() {
    var c = conteneur();
    var sc = D.querySelector('section.stMain');
    if (!c || !sc) return 0;
    var cs = P.getComputedStyle(c);
    var z = facteurZoom();
    var bar = D.getElementById('feuillet-barre');
    var hb = bar ? bar.getBoundingClientRect().height : 46;
    return sc.clientHeight
           - parseFloat(cs.paddingTop || 0)
           - parseFloat(cs.paddingBottom || 0)
           - hb / z
           - COUSS / z;
  }

  /* LA MESURE SE FAIT TOUJOURS SUR LA HAUTEUR NATURELLE. Un bloc déjà réduit
     par un passage précédent mesurerait sa hauteur réduite, la répartition
     suivante le croirait plus petit qu'il n'est, et le rapetissement
     s'accumulerait à chaque réexécution jusqu'à l'illisible. */
  function mesurer(el) {
    if (el.style.zoom) el.style.zoom = '';
    var cs = P.getComputedStyle(el);
    return el.offsetHeight + parseFloat(cs.marginTop || 0) +
                             parseFloat(cs.marginBottom || 0);
  }

  /* LE PLANCHER DE RÉDUCTION. En dessous, on cesse de réduire et on laisse
     l'écran défiler : un schéma à 40 % est vu en entier mais ne se lit plus,
     et un contenu illisible n'est pas un contenu vu. */
  var PLANCHER = 0.55;

  /* Ajuste un groupe à la hauteur disponible. Le zoom est utilisé plutôt
     qu'une transformation : `transform` ne change pas la place occupée dans
     la mise en page, les blocs se chevaucheraient ; `zoom` la change. */
  function ajuster(grp, dispo) {
    var h = 0, i;
    for (i = 0; i < grp.length; i++) h += mesurer(grp[i]);
    var f = h > dispo ? dispo / h : 1;
    if (f >= 1 || f < PLANCHER) {
      for (i = 0; i < grp.length; i++) grp[i].style.zoom = '';
      return f < PLANCHER ? 0 : 1;
    }
    f = f * 0.995;
    for (i = 0; i < grp.length; i++) grp[i].style.zoom = f;
    return f;
  }

  /* Les éléments qu'on garde visibles sur tous les écrans d'une même page :
     aujourd'hui les barres d'onglets, seules commandes qui perdraient leur
     sens si elles disparaissaient au premier tour de page. */
  var perpetuels = [];

  function barreOnglets(el) {
    return el.querySelector('[data-baseweb="tab-list"]');
  }

  /* Le contenu réellement empilable d'un bloc : la pile d'éléments de l'onglet
     ouvert s'il s'agit d'onglets, la pile interne sinon. Rend null quand le
     bloc n'a rien à donner — un schéma, une image, un tableau : ceux-là sont
     insécables pour de bon, et c'est la réduction qui les prend en charge. */
  /* LE PANNEAU OUVERT, PAS LE PREMIER VENU. Streamlit garde en place les
     panneaux des onglets fermés ; le premier trouvé est souvent l'un d'eux.
     Ses éléments mesurent alors zéro, la répartition les croit gratuits, les
     entasse tous sur un écran, et c'est le panneau réellement affiché — jamais
     découpé — qui déborde de trois cents pixels sur chaque écran. On ne
     retient donc que le panneau qui occupe vraiment de la place. */
  function panneauOuvert(el) {
    var tous = el.querySelectorAll(':scope > [data-baseweb="tab-panel"], '
             + ':scope > * > [data-baseweb="tab-panel"]');
    for (var i = 0; i < tous.length; i++) {
      if (tous[i].offsetParent !== null && tous[i].offsetHeight > 2) {
        return tous[i];
      }
    }
    return null;
  }

  /* LA DESCENTE SE FAIT ENFANT PAR ENFANT, JAMAIS PAR RECHERCHE PROFONDE.
     La première version cherchait le premier `stVerticalBlock` du sous-arbre.
     Sur le rapport aux bailleurs, elle atterrissait quatre niveaux plus bas,
     et tout ce qui se trouvait au-dessus dans la même branche n'appartenait
     alors à aucun écran : ces blocs-là n'étaient jamais masqués, restaient
     affichés en permanence, et la page débordait de deux mille pixels quel
     que soit le feuillet. On ne traverse donc plus que des enveloppes à
     enfant unique, et on s'arrête à la première fratrie rencontrée : rien ne
     peut être sauté. */
  function pileInterne(el) {
    var cur = el, garde = 0;
    while (cur && garde++ < 8) {
      var pan = panneauOuvert(cur);
      if (pan && pan !== cur) { cur = pan; continue; }
      var enf = [].slice.call(cur.children).filter(function (c) {
        return c.nodeType === 1 && c.tagName !== 'STYLE' &&
               c.tagName !== 'SCRIPT';
      });
      if (enf.length > 1) return enf;
      if (enf.length === 1) { cur = enf[0]; continue; }
      return null;
    }
    return null;
  }

  function eclater(vb, dispo, prof) {
    prof = prof || 0;
    var sortie = [];
    var kids = [].slice.call(vb.children);
    for (var i = 0; i < kids.length; i++) {
      var el = kids[i];
      var h = mesurer(el);
      /* LA PROFONDEUR MONTE JUSQU'À SIX. Le rapport aux bailleurs empile un
         conteneur encadré, puis des colonnes, puis des blocs internes : à
         trois niveaux on s'arrêtait avant d'avoir atteint le contenu, et la
         page débordait de deux mille pixels alors qu'elle était découpable.
         Six niveaux couvrent les imbrications réellement présentes ; au-delà,
         on tombe sur des éléments de mise en forme qu'il ne sert à rien de
         séparer. */
      if (h <= dispo || prof >= 6) { sortie.push(el); continue; }
      var bo = barreOnglets(el);
      var dedans = pileInterne(el);
      if (!dedans) { sortie.push(el); continue; }
      if (bo) { perpetuels.push(bo); }
      for (var j = 0; j < dedans.length; j++) {
        var f = dedans[j];
        /* un élément qui n'occupe aucune place est dans un panneau fermé :
           le compter reviendrait à croire l'écran vide */
        if (f.offsetParent === null) { continue; }
        if (mesurer(f) <= dispo) { sortie.push(f); }
        else {
          var plus = eclater({ children: [f] }, dispo, prof + 1);
          sortie = sortie.concat(plus.length ? plus : [f]);
        }
      }
    }
    return sortie;
  }

  /* SERRER : ON CONSTATE LE DÉBORDEMENT AU LIEU DE LE PRÉDIRE.
     Prédire la hauteur d'un écran demanderait de connaître tout ce que les
     conteneurs intermédiaires ajoutent : le rembourrage d'un panneau
     d'onglets, la marge d'une colonne, la hauteur propre d'une barre
     d'onglets. À chaque cas oublié, l'écran débordait de quelques dizaines de
     pixels sans qu'on sache lequel. Le navigateur, lui, sait exactement de
     combien il déborde : scrollHeight moins clientHeight. On le lui demande,
     on réduit d'autant, et on redemande. Trois tours suffisent à converger,
     et rien ne reste à deviner. */
  function serrer(grp) {
    var sc = D.querySelector('section.stMain');
    if (!sc || !grp.length) return 1;
    var z = parseFloat(grp[0].style.zoom) || 1;
    var zs = facteurZoom();

    for (var t = 0; t < 3; t++) {
      var trop = sc.scrollHeight - sc.clientHeight;
      if (trop <= 2) return z;

      /* la place réellement occupée, ramenée au repère de la mise en page */
      var pris = 0;
      for (var i = 0; i < grp.length; i++) {
        pris += grp[i].getBoundingClientRect().height;
      }
      pris = pris / zs;
      if (pris <= 1) return 0;

      var f = (pris - trop) / pris;
      if (f <= 0) return 0;
      z = z * f * 0.99;
      if (z < PLANCHER) {
        /* on renonce à réduire, mais pas à faire tenir : on sort de la boucle
           pour laisser le dernier recours borner la hauteur du bloc. Rendre
           la main ici, comme le faisait la première version, laissait la page
           entière défiler alors qu'il restait une solution. */
        for (i = 0; i < grp.length; i++) grp[i].style.zoom = '';
        z = 0;
        break;
      }
      for (i = 0; i < grp.length; i++) grp[i].style.zoom = z;
    }
    if (sc.scrollHeight - sc.clientHeight <= 2) return z;

    /* DERNIER RECOURS : LE BLOC DÉFILE, PAS LA PAGE. Une carte, un très long
       tableau, restent plus hauts que l'écran même réduits au plancher — et
       les réduire davantage les rendrait illisibles, ce qui trahirait la
       demande au lieu de la servir. On borne alors la hauteur du bloc et on
       lui donne son propre défilement : la page, elle, ne bouge plus d'un
       pixel, et la barre du bas dit ce qui se passe. Pour une carte, c'est
       même le comportement attendu : on s'y déplace déjà à la souris. */
    var reste = sc.clientHeight - (sc.scrollHeight - hauteurGroupe(grp));
    if (reste > 160) {
      for (i = 0; i < grp.length; i++) {
        grp[i].style.maxHeight = Math.floor(reste / grp.length) + 'px';
        grp[i].style.overflowY = 'auto';
      }
    }
    return 0;
  }

  function hauteurGroupe(grp) {
    var h = 0, zs = facteurZoom();
    for (var i = 0; i < grp.length; i++) {
      h += grp[i].getBoundingClientRect().height;
    }
    return h / zs;
  }

  function repartir() {
    var vb = pile();
    if (!vb) { groupes = []; return; }
    var dispo = hauteurDispo();
    if (dispo < 120) { groupes = []; return; }

    /* ON DESCEND DANS LES BLOCS TROP HAUTS AU LIEU DE LES SUBIR. Un jeu
       d'onglets est, vu du premier niveau, un bloc unique : sa barre
       d'onglets et tout le contenu de l'onglet ouvert ne font qu'un. Traité
       comme insécable, il occupait un écran entier et débordait de deux mille
       pixels. On remplace donc un bloc trop haut par ses propres éléments,
       en gardant sa barre d'onglets affichée sur tous les écrans : sans
       elle, le lecteur perdrait le moyen de changer d'onglet dès le second
       écran. */
    perpetuels = [];
    var kids = eclater(vb, dispo);

    /* GARDE-FOU : AUCUN CONTENU NE DOIT DISPARAÎTRE.
       Le découpage descend dans les conteneurs pour trouver des morceaux de
       la taille d'un écran. S'il se trompe de branche — un panneau d'onglets
       mal identifié, une enveloppe inattendue — les blocs qu'il n'a pas
       ramassés ne figurent dans aucun écran : ils sont masqués au premier
       affichage et plus rien ne permet d'y accéder. C'est arrivé sur le
       premier chapitre du rapport aux bailleurs, dont le récit s'arrêtait au
       bout de deux lignes. On vérifie donc que les morceaux retenus couvrent
       bien la hauteur de la page ; sinon on renonce au découpage fin et on
       revient aux blocs de premier niveau, quitte à ce que la page défile.
       Une page qui défile se lit ; une page amputée, non. */
    var hAtomes = 0, hPile = mesurer(vb);
    for (var t = 0; t < kids.length; t++) hAtomes += mesurer(kids[t]);
    if (hPile > 40 && hAtomes < hPile * 0.85) {
      perpetuels = [];
      kids = [].slice.call(vb.children);
    }

    /* La place prise par les barres d'onglets est retirée une fois pour
       toutes : elles restent à l'écran quel que soit le feuillet, donc elles
       ne sont pas disponibles pour le contenu. */
    for (var q = 0; q < perpetuels.length; q++) dispo -= mesurer(perpetuels[q]);
    if (dispo < 120) dispo = 120;

    groupes = [];
    var cour = [], h = 0;

    for (var i = 0; i < kids.length; i++) {
      var el = kids[i];
      /* LES BLOCS SANS HAUTEUR SONT DES INJECTEURS DE STYLE. Ils ne comptent
         pas dans le remplissage, et on les laisse toujours affichés : les
         cacher ne coûterait rien mais les compter fausserait tout. */
      var eh = mesurer(el);
      if (eh < 2) { el.setAttribute('data-feuillet', 'toujours'); continue; }
      el.removeAttribute('data-feuillet');
      if (cour.length && h + eh > dispo) { groupes.push(cour); cour = []; h = 0; }
      cour.push(el);
      h += eh;
    }
    if (cour.length) groupes.push(cour);
  }

  function montrer(k) {
    var vb = pile();
    if (!vb || !groupes.length) return;
    k = Math.max(0, Math.min(k, groupes.length - 1));

    for (var g = 0; g < groupes.length; g++) {
      for (var j = 0; j < groupes[g].length; j++) {
        var el = groupes[g][j];
        if (P.__feuilletTouches.indexOf(el) < 0) P.__feuilletTouches.push(el);
        if (g === k) {
          el.style.display = '';
          el.classList.remove('feuillet-entre');
          void el.offsetWidth;              /* redémarre l'animation */
          el.classList.add('feuillet-entre');
        } else {
          el.style.display = 'none';
        }
      }
    }
    var reduit = serrer(groupes[k]);
    ecrire(k);
    peindreBarre(k, reduit);
    var c = conteneur();
    if (c && c.parentElement) c.parentElement.scrollTop = 0;
  }

  function peindreBarre(k, reduit) {
    var b = barre();
    var n = groupes.length;
    var m = P.__feuilletMots || {};

    /* la barre s'aligne sur la zone de contenu, pas sur la fenêtre : sinon
       elle passerait sous le bandeau latéral */
    var c = conteneur();
    var r = c ? c.getBoundingClientRect() : null;
    if (r) { b.style.left = r.left + 'px'; b.style.width = r.width + 'px'; }

    if (n <= 1) { b.style.display = 'none'; return; }
    b.style.display = 'flex';

    var bp = b.querySelector('[data-f="prec"]');
    var bs = b.querySelector('[data-f="suiv"]');
    bp.textContent = '\\u2190 ' + (m.prec || 'Previous');
    bs.textContent = (m.suiv || 'Next') + ' \\u2192';
    bp.disabled = k === 0;
    bs.disabled = k === n - 1;

    var pts = '';
    for (var i = 0; i < n; i++) {
      pts += '<i data-k="' + i + '" class="' + (i === k ? 'on' : '') + '"></i>';
    }
    b.querySelector('.fb-p').innerHTML = pts;
    b.querySelector('.fb-n').textContent = (k + 1) + ' ' + (m.de || '/') + ' ' + n;

    /* l'écran qui défile encore le dit lui-même, plutôt que de laisser croire
       à un bug : c'est le seul cas où la molette reste nécessaire */
    b.querySelector('.fb-av').textContent = (reduit === 0) ? (m.long || '') : '';
    b.querySelector('.fb-t').textContent = '';
  }

  function aller(d) { montrer(lire() + d); }
  function poser(k) { montrer(k); }

  /* ------------------------------------------------------- le rafraîchisseur */
  var minuteur = null;
  function refaire() {
    clearTimeout(minuteur);
    minuteur = setTimeout(function () {
      var vb = pile();
      if (!vb) return;
      degarnir();
      /* ON REMET À PLAT TOUT CE QU'ON A TOUCHÉ, PAS SEULEMENT LE PREMIER
         NIVEAU. Le découpage descend dans les conteneurs : les blocs qu'il
         masque sont souvent profonds. Ne réinitialiser que les enfants
         directs de la pile laissait ces blocs-là masqués pour de bon — si la
         répartition suivante ne les retenait pas comme morceaux, plus rien ne
         les réaffichait, et le récit du premier chapitre s'arrêtait au bout
         de deux lignes sans que rien ne permette d'atteindre la suite. On
         garde donc la trace de chaque élément touché. */
      var touches = P.__feuilletTouches;
      for (var i = 0; i < touches.length; i++) {
        var e0 = touches[i];
        e0.style.display = '';
        e0.style.zoom = '';
        e0.style.maxHeight = '';
        e0.style.overflowY = '';
      }
      P.__feuilletTouches = [];
      var kids = [].slice.call(vb.children);
      for (i = 0; i < kids.length; i++) {
        kids[i].style.display = '';
        kids[i].style.zoom = '';
        kids[i].style.maxHeight = '';
        kids[i].style.overflowY = '';
      }
      repartir();
      montrer(lire());
      verifier();
    }, 120);
  }

  /* LA PAGE N'A PAS FINI DE SE POSER QUAND ON LA MESURE LA PREMIÈRE FOIS.
     Les polices arrivent après le texte, les schémas après leur conteneur :
     une hauteur relevée trop tôt est trop courte, la répartition entasse
     alors un bloc de trop, et l'écran déborde de trois cents pixels. Une
     seconde passe, une fois la mise en page stabilisée, corrige d'elle-même.
     Le compteur borne le nombre de reprises : sans lui, un contenu dont la
     hauteur oscille ferait boucler la vérification indéfiniment. */
  var reprises = 0, calmes = 0;
  function verifier() {
    setTimeout(function () {
      var sc = D.querySelector('section.stMain');
      if (!sc) return;
      var trop = sc.scrollHeight - sc.clientHeight;
      if (trop > 2) {
        /* ça déborde : on refait, et on remet le compteur de calme à zéro */
        calmes = 0;
        if (reprises < 10) { reprises++; P.__feuilletRefaire(); }
        else { reprises = 0; calmes = 0; }
        return;
      }
      /* DEUX CONSTATS CALMES AVANT DE LÂCHER, PAS UN SEUL. Pendant une
         réexécution, la page traverse un instant où tout tient parce que le
         contenu n'est pas encore revenu. Un seul contrôle rassurant suffisait
         à interrompre la surveillance, et ce qui finissait de charger juste
         après débordait sans que personne ne regarde plus. */
      calmes++;
      if (calmes < 2 && reprises < 10) { reprises++; verifier(); }
      else { reprises = 0; calmes = 0; }
      return;
    /* LES REPRISES S'ESPACENT AU LIEU DE SE RÉPÉTER. Six vérifications à
       cadence trop lente mettent vingt secondes à converger, et le lecteur
       voit la page se réajuster sous ses yeux. Les premières reprises sont
       donc rapprochées — c'est là que presque tout se joue — puis la cadence
       se stabilise pour laisser aux pages lourdes, comme le rapport aux
       bailleurs et ses radars, le temps de finir de se poser. Dix reprises
       au plus : passé ce point, la hauteur oscille et refaire n'aide plus. */
    }, [250, 350, 500, 700, 1000, 1400, 1400, 1400, 1400, 1400][Math.min(reprises, 9)]);
  }

  /* LE COMPTEUR DE REPRISES SE REMET À ZÉRO À CHAQUE VRAI CHANGEMENT.
     Sans cela, une page qui épuisait ses dix reprises laissait le compteur au
     plafond : toutes les vérifications suivantes échouaient sur la même
     condition, et plus rien ne se réajustait jamais — c'est ce qui laissait
     le rapport aux bailleurs déborder de deux mille pixels dès qu'on changeait
     de chapitre. Le changement de contenu, lui, est un événement neuf : il a
     droit à son propre budget de reprises. */
  P.__feuilletReset = function () { reprises = 0; calmes = 0; };

  /* l'instance qui vient de démarrer devient l'instance de référence */
  P.__feuilletAller = aller;
  P.__feuilletPoser = poser;
  P.__feuilletRefaire = refaire;

  if (!P.__feuilletInstalle) {
    P.__feuilletInstalle = true;

    var obs = new P.MutationObserver(function () {
      P.__feuilletReset();
      P.__feuilletRefaire();
    });
    /* ON SURVEILLE LA RACINE, PAS LE CONTENEUR DE CONTENU.
       React ne se contente pas de modifier les enfants du conteneur
       principal : il lui arrive de remplacer le conteneur lui-même. Un
       observateur attaché à ce nœud se retrouve alors branché sur un élément
       détaché du document, ne reçoit plus rien, et cesse silencieusement de
       faire son travail — la page débordait dès qu'on changeait de chapitre,
       sans la moindre erreur pour le signaler. Le <body>, lui, ne change
       jamais. Le coût est nul : la répartition est de toute façon différée
       de cent vingt millisecondes, donc une rafale de mutations ne déclenche
       qu'un seul recalcul. */
    var att = setInterval(function () {
      var c = conteneur();
      if (c) {
        clearInterval(att);
        obs.observe(D.body, { childList: true, subtree: true });
        P.__feuilletRefaire();
      }
    }, 200);

    P.addEventListener('resize', function () { P.__feuilletRefaire(); });

    /* les flèches du clavier tournent les pages, à condition de ne pas être
       en train d'écrire dans un champ */
    P.addEventListener('keydown', function (e) {
      var a = D.activeElement;
      if (a && /INPUT|TEXTAREA|SELECT/.test(a.tagName)) return;
      if (e.key === 'ArrowRight' || e.key === 'PageDown') { P.__feuilletAller(1); }
      else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { P.__feuilletAller(-1); }
    });
  } else {
    refaire();
  }

  /* UNE RELANCE DIFFÉRÉE, À CHAQUE PASSAGE DU SCRIPT.
     Le MutationObserver voit bien les réexécutions, mais sur les pages qui
     rechargent beaucoup de contenu d'un coup — le rapport aux bailleurs quand
     on change de chapitre — la répartition qu'il déclenche tombe pendant que
     la page bouge encore, et la chaîne de vérifications n'a pas toujours
     suffi à rattraper le décalage. Une relance franche une seconde après,
     compteurs remis à zéro, met fin au problème pour de bon. Elle coûte un
     recalcul par changement de page ; c'est le prix d'une page qui ne déborde
     jamais. */
  setTimeout(function () {
    try { P.__feuilletReset(); P.__feuilletRefaire(); } catch (e) {}
  }, 1000);
})();
</script>
"""


def activer(cle):
    """À appeler une fois par page, tout en bas du rendu.

    `cle` identifie la page : le numéro d'écran est mémorisé sous ce nom, si
    bien que chaque page se rouvre là où on l'avait laissée, et que passer
    d'une page à l'autre ne fait pas hériter du numéro de la précédente.
    """
    import json

    lang = i18n.get_lang()
    mots = {"prec": T("fe_prec"), "suiv": T("fe_suiv"),
            "de": T("fe_de"), "long": T("fe_long")}
    # LA SUBSTITUTION SE FAIT PAR JETONS, PAS PAR `%`. Le gabarit est du
    # JavaScript commenté en français : un « 40 % » dans un commentaire
    # suffisait à faire échouer le formatage `%`, et le script n'était alors
    # jamais injecté — panne silencieuse, page qui redéfile, aucune erreur
    # visible. Des jetons explicites ne peuvent pas se faire piéger.
    # UN JETON QUI CHANGE À CHAQUE RÉEXÉCUTION. Streamlit ne recrée l'iframe
    # d'un composant que si son contenu a changé ; avec un script identique
    # d'une exécution à l'autre, aucune nouvelle instance ne démarrait, et la
    # relance différée ci-dessous n'avait jamais lieu au moment où elle est
    # justement utile. Le compteur rend chaque rendu unique d'un caractère.
    n = st.session_state.get("_feuillet_tour", 0) + 1
    st.session_state["_feuillet_tour"] = n

    html = (_GABARIT
            .replace("@@CLE@@", json.dumps(f"{cle}:{lang}"))
            .replace("@@MOTS@@", json.dumps(mots, ensure_ascii=False))
            .replace("@@COUSSIN@@", str(COUSSIN))
            + f"\n<!-- {n} -->")
    components.html(html, height=0, width=0)
