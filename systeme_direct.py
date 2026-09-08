"""Le système en marche : le schéma du premier onglet, mais qui bouge.

CE QUE CET ÉCRAN AJOUTE AUX QUATRE AUTRES.
Le premier onglet dessine le système et s'arrête là : des pastilles, des
flèches signées, une image fixe. Le quatrième pose une poussée et donne le
résultat une fois tout distribué. Le cinquième range la même propagation en
colonnes de relais. Aucun des trois ne montre le mouvement lui-même — et
c'est pourtant le mouvement qui explique ce qu'est une boucle : on ne
comprend pas qu'un effet revienne sur son point de départ en lisant un
tableau, on le comprend en voyant l'onde repasser par là.

Ici, le schéma est CELUI DU PREMIER ONGLET — mêmes pastilles, mêmes
positions, mêmes flèches, même variable centrale et même périmètre, pris
dans le même état de session. On pose une variation sur une variable, on
appuie sur Lecture, et des billes partent le long des flèches : vertes quand
elles portent une amélioration, rouges quand elles portent une dégradation,
grosses quand elles portent beaucoup. Quand une bille arrive, la variable
qu'elle atteint monte ou descend, sa jauge se déplace, son chiffre change.
Le relais suivant repart de là.

DEUX NIVEAUX, ET UN SEUL MOT POUR CHACUN. Une poussée est UNE ONDE DE CHOC :
elle traverse le système entier, revient par les boucles et se stabilise.
Ce que compte l'écran, ce sont les RELAIS qui la composent — un tour de
transmission de proche en proche. Les deux portaient le même nom, « vague »,
et l'on ne savait plus si le compteur disait le choc ou son pas.

TOUT SE CALCULE DANS LE NAVIGATEUR, ET C'EST OBLIGATOIRE.
Une animation à soixante images par seconde ne peut pas faire un aller-retour
serveur par image. Le module envoie donc une fois le sous-graphe affiché —
positions comprises, poids déjà mis à l'échelle par le moteur — et le
navigateur fait tourner la récurrence relais_{k+1} = A · relais_k, exactement
celle que `boucles_moteur` résout d'un bloc par inversion.

CE QUE L'ÉCRAN NE DIT PAS.
Le rang d'un relais est un ordre de transmission, pas un calendrier : rien
ici ne dit qu'un relais dure un mois ou dix ans. Et la propagation s'arrête
au bord du périmètre dessiné : ce qui sort du schéma n'est pas suivi, ce
qui est le
prix à payer pour que l'onde reste visible sur une image lisible. La taille
du périmètre se règle dans le premier onglet, et l'effet total, lui, se lit
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
    # DEUX NIVEAUX, DEUX MOTS. Une poussée est une ONDE DE CHOC : elle
    # traverse le système entier et revient par les boucles. Ce que compte
    # l'écran, ce sont les RELAIS qui la composent. Les deux portaient le
    # même nom — « vague » — et l'on ne savait plus si le compteur disait le
    # choc ou son pas. Un rang de relais n'est pas non plus une durée, et
    # c'est l'autre contresens que la phrase ferme.
    "sd_vague_x": {
        "en": "One push is one shock wave: it spreads through the whole "
              "system, comes back through the loops, and settles. What is "
              "counted here are the relays inside it. At each relay, every "
              "variable that has just moved passes its change to its direct "
              "neighbours, and those pass it on at the next relay. The shock "
              "wave dies out when there is nothing left worth passing on, "
              "and when a loop closes it comes back to the variable it "
              "started from. A relay is an order of transmission, not a "
              "length of time. You can cap the number of relays, or let the "
              "shock wave run until it settles.",
        "fr": "Une poussée est une onde de choc : elle traverse tout le "
              "système, revient par les boucles, puis se stabilise. Ce qui "
              "est compté ici, ce sont les relais qui la composent. À chaque "
              "relais, chaque variable qui vient de bouger transmet son "
              "changement à ses voisines directes, qui le transmettront au "
              "relais suivant. L'onde s'éteint quand il n'y a plus rien qui "
              "vaille d'être transmis, et quand une boucle se referme elle "
              "revient sur la variable de départ. Un relais est un ordre de "
              "transmission, pas une durée. Vous pouvez borner le nombre de "
              "relais, ou laisser l'onde aller jusqu'à sa stabilisation."},
    # LE RASSEMBLEMENT. Une fois l'onde stabilisée, le schéma a fait son
    # travail : il a montré le chemin. Ce qu'on veut garder tient en cinq ou
    # six variables — les mieux reliées et les plus retraversées — et les
    # trente autres pastilles, avec leurs quatre-vingt-douze flèches, ne font
    # plus que les cacher. Elles s'alignent donc à gauche, avec leur compte,
    # et le reste du dessin s'efface. Le mouvement est ce qui fait le lien
    # entre les deux images : sans lui, on croirait à un autre écran.
    "sd_ess": {"en": "Keep the essentials", "fr": "Ne garder que l'essentiel"},
    "sd_ess_non": {"en": "Show the whole diagram",
                   "fr": "Revoir le schéma entier"},
    "sd_ess_t": {"en": "What the run singled out",
                 "fr": "Ce que la course a désigné"},
    "sd_nb": {"en": "Relays", "fr": "Relais"},
    "sd_nb_auto": {"en": "until it settles", "fr": "jusqu'à stabilisation"},
    "sd_var": {"en": "Variable pushed", "fr": "Variable poussée"},
    "sd_ampleur": {"en": "Change applied", "fr": "Changement appliqué"},
    "sd_lire": {"en": "Play", "fr": "Lecture"},
    "sd_pause": {"en": "Pause", "fr": "Pause"},
    "sd_pas": {"en": "One relay", "fr": "Un relais"},
    "sd_raz": {"en": "Reset", "fr": "Remise à zéro"},
    "sd_vitesse": {"en": "Speed", "fr": "Vitesse"},
    "sd_vague": {"en": "Relay", "fr": "Relais"},
    "sd_distrib": {"en": "of the effect already distributed",
                   "fr": "de l'effet déjà distribué"},
    "sd_leg_h": {"en": "carries an improvement",
                 "fr": "porte une amélioration"},
    "sd_leg_b": {"en": "carries a degradation",
                 "fr": "porte une dégradation"},
    "sd_leg_e": {"en": "score out of 10, and how far it has moved",
                 "fr": "score sur 10, et de combien il a bougé"},
    "sd_fin": {"en": "The shock wave has settled: everything it could move "
                     "has moved.",
               "fr": "L'onde de choc s'est stabilisée : tout ce qu'elle "
                     "pouvait déplacer a bougé."},
    "sd_retour": {"en": "The shock came back to its starting variable at "
                        "relay {k}: this system is a loop, not a chain.",
                  "fr": "Le choc est revenu sur sa variable de départ au "
                        "relais {k} : ce système est une boucle, pas une "
                        "chaîne."},
    "sd_non_mesure": {"en": "not measured", "fr": "non mesurée"},
    "sd_delai": {"en": "Time per relay", "fr": "Délai par relais"},
    "sd_delai_non": {"en": "not set", "fr": "non posé"},
    "sd_mois": {"en": "months", "fr": "mois"},
    "sd_ans": {"en": "years", "fr": "ans"},
    "sd_temps_x": {
        "en": "The delay is yours, not the model's: nothing in the framework "
              "says how long one relay takes. Set it and the relay counter "
              "reads as a rough horizon.",
        "fr": "Le délai est le vôtre, pas celui du modèle : rien dans le "
              "cadre ne dit combien de temps dure un relais. Une fois posé, "
              "le compteur de relais se lit comme un horizon approché."},
    "sd_bilan": {"en": "Once the shock wave has settled",
                 "fr": "Une fois l'onde de choc stabilisée"},
    # DEUX QUESTIONS, ET AUCUNE NE PORTE SUR LA VARIABLE POUSSÉE ELLE-MÊME.
    # Le tableau comptait les liens de chaque pastille, si bien que la
    # variable centrale — la mieux reliée par construction, c'est elle qui a
    # défini le périmètre — arrivait toujours en tête de son propre bilan.
    # On ne veut pas savoir qu'elle est au centre : on veut savoir qui la
    # tient, et sur qui elle pèse, pour aller agir là.
    "sd_connect": {"en": "What influences {v} most",
                   "fr": "Ce qui influence le plus {v}"},
    "sd_connect_x": {
        "en": "effect on the pushed variable of a +1 rise in each of them, "
              "inside this perimeter, loops included",
        "fr": "effet sur la variable poussée d'une hausse de +1 chez "
              "chacune, dans ce périmètre, boucles comprises"},
    # « Ce que Accès à l'eau influence le plus » : l'élision manquait et
    # aucune règle générale ne la pose sur un nom de variable quelconque. La
    # tournure passive contourne le problème dans les deux langues.
    "sd_passages": {"en": "The ones most influenced by {v}",
                    "fr": "Les plus influencées par {v}"},
    "sd_passages_x": {
        "en": "how far this run moved them, once the shock wave had settled",
        "fr": "de combien cette course les a déplacées, une fois l'onde "
              "stabilisée"},
    "sd_vagues_n": {"en": "relays", "fr": "relais"},
    # QUATRE CLASSEMENTS, QUATRE QUESTIONS QUI NE SE CONFONDENT PAS. Ce qui
    # touche la variable regardée n'est pas ce qui remue le reste du système ;
    # être dans beaucoup de boucles n'est pas recevoir beaucoup de relais.
    # Chacun a sa colonne, avec sa définition dessous.
    "sd_mul": {"en": "Biggest multiplier on the rest of the system",
               "fr": "Plus fort effet démultiplicateur sur le reste du "
                     "système"},
    "sd_mul_x": {
        "en": "total movement produced everywhere else by a +1 rise in each "
              "of them, loops included",
        "fr": "mouvement total produit partout ailleurs par une hausse de +1 "
              "chez chacune, boucles comprises"},
    "sd_bcl": {"en": "Most caught up in loops",
               "fr": "Les plus prises dans des boucles"},
    "sd_bcl_x": {
        "en": "loops running through them inside this perimeter, reinforcing "
              "and balancing; being in both is what makes a tipping lever",
        "fr": "boucles qui passent par elles dans ce périmètre, renforçantes "
              "et équilibrantes ; être dans les deux fait un levier de "
              "basculement"},
    "sd_vag_t": {"en": "Most crossed by the shock wave",
                 "fr": "Les plus retraversées par l'onde"},
    "sd_vag_x": {
        "en": "relays that moved them: more than one means a loop brought "
              "the shock back onto them",
        "fr": "relais qui les ont déplacées : au-delà d'un, c'est une boucle "
              "qui a ramené le choc sur elles"},
    # DEUX LETTRES PLUTÔT QUE DEUX MOTS : la colonne des boucles affiche
    # « 4 R · 2 B » et non « 4 renforçantes · 2 équilibrantes », qui ne tient
    # pas sur une ligne. La légende du premier onglet donne les deux noms en
    # entier ; ici on compte, on ne définit pas.
    "sd_bcl_r": {"en": "R", "fr": "R"},
    "sd_bcl_b": {"en": "B", "fr": "B"},
    # UN PÉRIMÈTRE ÉTROIT PEUT NE CONTENIR AUCUNE BOUCLE ENTIÈRE : la colonne
    # le dit plutôt que de rester vide, sinon on croit à une panne.
    "sd_bcl_vide": {
        "en": "no complete loop inside this perimeter — ask for more "
              "variables in the first tab",
        "fr": "aucune boucle entière dans ce périmètre — demandez plus de "
              "variables dans le premier onglet"},
    "sd_leg_j": {"en": "the ones that influence it most",
                 "fr": "celles qui l'influencent le plus"},
    "sd_leg_c": {"en": "the ones it influences most",
                 "fr": "celles qu'elle influence le plus"},
    "sd_liens_n": {"en": "links", "fr": "liens"},
    "sd_perim": {
        "en": "The shock wave is followed inside the drawn perimeter only: "
              "what leaves the picture is not tracked. Change the central "
              "variable or ask for more variables in the first tab to widen "
              "it.",
        "fr": "L'onde n'est suivie qu'à l'intérieur du périmètre dessiné : "
              "ce qui sort de l'image n'est pas suivi. La variable centrale "
              "et le nombre de variables se règlent dans le premier "
              "onglet."},
    "sd_court": {
        "en": "This perimeter has no outgoing link to follow: ask for more "
              "variables in the first tab.",
        "fr": "Ce périmètre n'a aucun lien à suivre : demandez plus de "
              "variables dans le premier onglet."},
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


def _donnees(m, centre, n):
    """Le sous-graphe affiché, positions et poids compris, prêt pour le JS.

    LES POIDS SONT CEUX DU MOTEUR, DÉJÀ MIS À L'ÉCHELLE. Le graphe brut a un
    rayon spectral proche de 1 : propagé tel quel, une poussée de deux points
    en produirait quinze ailleurs. La mise à l'échelle appartient au moteur ;
    on la lui demande plutôt que de la refaire ici.
    """
    rang, aretes = SX._voisinage(m, centre, n)
    pos, larg, haut = SX._positions(rang, centre)
    etat = M.etat_courant(m["g"], m["par_ligne"], "Total")
    A, ids, idx = m["A"], m["ids"], m["idx"]

    # COMBIEN DE BOUCLES PASSENT PAR CHAQUE VARIABLE, DANS CE PÉRIMÈTRE. Le
    # décompte se fait ici : le navigateur reçoit un sous-graphe, pas
    # l'énumération des cycles, et la refaire en JavaScript à chaque affichage
    # coûterait plus cher que de l'envoyer toute faite. Seules les boucles
    # entièrement contenues dans le dessin sont comptées : en annoncer une
    # dont la moitié est hors cadre serait invérifiable à l'œil.
    dedans = set(pos)
    bcl = {i: [0, 0] for i in pos}
    for b in m["boucles"]:
        if not set(b["noeuds"]) <= dedans:
            continue
        for i in b["noeuds"]:
            bcl[i][0 if b["type"] == "renforcante" else 1] += 1

    noeuds = []
    for n in sorted(pos, key=lambda i: m["noms"].get(i, i)):
        x, y = pos[n]
        v = etat.get(n)
        noeuds.append({"id": n, "nom": m["noms"].get(n, n),
                       "lig": _lignes(m["noms"].get(n, n)),
                       "x": round(x, 1), "y": round(y, 1),
                       "s": None if v is None else round(float(v), 2),
                       "r": rang.get(n, 9), "c": n == centre,
                       "br": bcl[n][0], "bb": bcl[n][1]})
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
  #kt{font-size:11px;color:#6b7590;font-variant-numeric:tabular-nums}
  #fin{display:flex;gap:14px;flex-wrap:wrap;margin:6px 0 2px}
  .fb{flex:1 1 300px;border:1px solid #e3eaf3;border-radius:12px;
    padding:10px 14px;background:#fbfcfd}
  .fh{font-size:10px;font-weight:700;letter-spacing:.07em;
    text-transform:uppercase;color:#2a6b3f;margin-bottom:6px}
  .fx{font-size:10.5px;color:#8a93a5;margin-top:6px;line-height:1.45}
  .fl{display:flex;justify-content:space-between;gap:12px;font-size:12px;
    color:#3c4761;padding:2px 0}
  .fl b{font-variant-numeric:tabular-nums;color:#101728;white-space:nowrap}
  text{font-family:Inter,system-ui,sans-serif}
  /* LE JAUNE DIT LA STRUCTURE, LE CLIGNOTEMENT DIT LE PARCOURS. Deux
     propriétés différentes, deux signaux différents : le halo ne bouge pas
     parce que la connectivité ne dépend pas de la course, le clignotement
     n'apparaît qu'à la fin parce qu'il compte ce que la course a fait. */
  .lum{filter:drop-shadow(0 0 4px #f0b73f) drop-shadow(0 0 9px rgba(240,183,63,.75))}
  /* LE GLISSEMENT DES PASTILLES ET L'EFFACEMENT DU RESTE. Une seconde, en
     décélération : assez lent pour qu'on suive une pastille des yeux depuis
     sa place dans le système jusqu'à sa ligne, assez court pour qu'on
     n'attende pas. */
  .nd{transition:transform .95s cubic-bezier(.4,0,.2,1),opacity .55s ease}
  .det{transition:opacity .4s ease .55s}
  #gl{transition:opacity .5s ease}
  @keyframes cli{0%,100%{opacity:1}50%{opacity:.12}}
  .cli{animation:cli 1.05s ease-in-out infinite}
</style></head><body><div id="tout">
<div id="barre">
  <div class="ch"><label>__L_VAR__</label>
    <select id="src"></select></div>
  <div class="ch"><label>__L_AMP__ · <span id="ampv">+1,0</span></label>
    <input id="amp" type="range" min="-10" max="10" step="0.5" value="1"
           style="width:190px"></div>
  <button id="lire" class="p">__L_LIRE__</button>
  <button id="pas">__L_PAS__</button>
  <button id="raz">__L_RAZ__</button>
  <button id="ess" hidden>__L_ESS__</button>
  <div class="ch"><label>__L_VIT__</label>
    <select id="vit">
      <option value="1.7">0,5×</option>
      <option value="1" selected>1×</option>
      <option value="0.55">2×</option>
      <option value="0.3">4×</option>
    </select></div>
  <div class="ch"><label>__L_NB__</label>
    <select id="nv">
      <option value="0" selected>__L_NBA__</option>
      <option value="3">3</option>
      <option value="5">5</option>
      <option value="10">10</option>
      <option value="20">20</option>
      <option value="40">40</option>
    </select></div>
  <div class="ch"><label>__L_DEL__</label>
    <select id="dl" title="__L_TPS__">
      <option value="0" selected>__L_DEL0__</option>
      <option value="1">1 __L_MOIS__</option>
      <option value="3">3 __L_MOIS__</option>
      <option value="6">6 __L_MOIS__</option>
      <option value="12">12 __L_MOIS__</option>
    </select></div>
  <div id="compteur"><div id="kl">__L_VAGUE__</div>
    <div id="kv">0</div><div id="kd">0 % __L_DIS__</div>
    <div id="kt"></div></div>
</div>
<div id="scene"><svg id="g" preserveAspectRatio="xMidYMid meet"></svg></div>
<div id="mot"></div>
<div id="fin" hidden>
  <div class="fb"><div class="fh" id="hc">__L_CON__</div><div id="fc"></div>
    <div class="fx">__L_CONX__</div></div>
  <div class="fb"><div class="fh" id="hp">__L_PAS2__</div><div id="fp"></div>
    <div class="fx">__L_PASX__</div></div>
  <div class="fb"><div class="fh">__L_MUL__</div><div id="fm"></div>
    <div class="fx">__L_MULX__</div></div>
  <div class="fb"><div class="fh">__L_BCL__</div><div id="fb"></div>
    <div class="fx">__L_BCLX__</div></div>
  <div class="fb"><div class="fh">__L_VAG__</div><div id="fvg"></div>
    <div class="fx">__L_VAGX__</div></div>
</div>
<div id="bas">
  <span class="lg"><span class="pt" style="background:#1a8a4f"></span>
    __L_LH__</span>
  <span class="lg"><span class="pt" style="background:#c33a24"></span>
    __L_LB__</span>
  <span class="lg"><span style="display:inline-block;width:26px;height:5px;
    border-radius:3px;background:#cfe0d6"></span> __L_LE__</span>
  <span class="lg" id="lgj" hidden><span class="pt lum"
    style="background:#f0b73f"></span> __L_LJ__</span>
  <span class="lg"><span class="pt cli" style="background:#2a6b3f"></span>
    __L_LC__</span>
</div>
</div>
<script>
const D = __DONNEES__, L = __LIBELLES__;
const NO = D.noeuds, LI = D.liens;
const IX = {}; NO.forEach((n,i)=>IX[n.id]=i);
/* Sous deux millièmes de point sur dix, l'onde ne déplace plus rien de
   lisible ; le seuil est bas pour qu'une grosse poussée puisse courir loin. */
const SEUIL = 0.002;
const KMAX = 80;
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
gLiens.setAttribute("id", "gl");
svg.appendChild(gLiens); svg.appendChild(gNoeuds); svg.appendChild(gBilles);
/* L'INTITULÉ DU REGROUPEMENT, muet tant que le schéma est entier. */
const ttl = el("text",{id:"ttl", x:D.vb[0]+52, y:D.vb[1]+34,
  "font-size":"12", "font-weight":"700", "letter-spacing":"1.4",
  fill:"#6b7590", opacity:"0"});
ttl.textContent = (L.ess_t || "").toUpperCase();
svg.appendChild(ttl);

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
  const g = el("g", {"class": "nd"});
  const r = el("rect",{x:n.x-76, y:n.y-h/2, width:152, height:h, rx:9,
    fill: n.c ? APRI : (n.r===1 ? "#eef3f0" : "#f6f8fb"),
    stroke: n.c ? APRI : "#dbe3ec", "stroke-width":"1"});
  g.appendChild(r);
  /* L'anneau du clignotement est dessiné par-dessus la pastille et reste
     invisible tant qu'il n'a rien à dire : faire clignoter la pastille
     elle-même effacerait le chiffre une fois sur deux. */
  const an = el("rect",{x:n.x-79, y:n.y-h/2-3, width:158, height:h+6, rx:11,
    fill:"none", stroke:"#2a6b3f", "stroke-width":"2.4", opacity:"0"});
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
  /* LE DÉTAIL VOYAGE AVEC SA PASTILLE. Écrit dans le même groupe, à droite
     du cadre, il suit la translation sans qu'on ait à le replacer ; il reste
     transparent tant que le schéma est entier, où il ferait trente lignes de
     chiffres par-dessus les flèches. */
  const dt = el("text",{x:n.x+88, y:n.y+4, "font-size":"11.5",
    "text-anchor":"start", fill:"#3c4761", opacity:"0", "class":"det"});
  g.appendChild(dt);
  g.appendChild(an);
  gNoeuds.appendChild(g);
  return {n, rect:r, jauge:jv, val, anneau:an, det:dt, grp:g, h, yb};
});

/* ---------- LE HALO JAUNE : LES VARIABLES LES PLUS CONNECTÉES ------------
   IL N'APPARAÎT QU'UNE FOIS LE SYSTÈME LANCÉ. La connectivité est bien une
   propriété du périmètre et non de la poussée, mais posée à l'ouverture elle
   désignait trois pastilles avant qu'on ait vu quoi que ce soit bouger : on
   lisait un verdict avant la démonstration, et le dessin s'ouvrait avec un
   accent qu'aucune image ne justifiait encore. Il vient donc avec le bilan,
   quand l'onde s'est stabilisée ou qu'on l'a bornée, et il repart avec lui à
   la remise à zéro. Sa ligne de légende suit — une légende pour un signe
   absent est une devinette.

   Trois pastilles au plus, pour que le signal reste un signal. */
function poserHalo(on){
  /* CE NE SONT PLUS LES MIEUX RELIÉES, MAIS CELLES QUI TIENNENT LA VARIABLE
     POUSSÉE. Compter les flèches désignait la variable centrale elle-même,
     qui a défini le périmètre : un halo sur le sujet de la question. */
  const cles = new Set(on ? amont.slice(0, 3).map(x => x.i) : []);
  vues.forEach((u,i)=>{
    if (cles.has(i)) u.rect.classList.add("lum");
    else u.rect.classList.remove("lum");
  });
  const lg = document.getElementById("lgj");
  if (lg) lg.hidden = !cles.size;
}

/* ---------- QUI TIENT LA VARIABLE POUSSÉE ------------------------------
   Pour chaque autre variable du périmètre, on pousse +1 dessus et on lit ce
   qui arrive à la variable regardée, boucles comprises. C'est la question
   qu'on se pose vraiment devant un système : non pas « laquelle a le plus de
   flèches », qui désigne toujours la variable centrale puisque c'est elle
   qui a défini le périmètre, mais « sur laquelle appuyer pour que celle-ci
   bouge ». Le calcul est le même que celui de la course, mené depuis chaque
   point de départ possible ; à quinze ou trente variables, il tient en
   quelques millisecondes. */
/* La même poussée répond en réalité à DEUX questions, et il serait absurde de
   refaire le calcul pour la seconde : ce qui arrive à la variable regardée
   (v) et ce que la poussée remue partout ailleurs (p, somme des déplacements
   absolus reçus par toutes les autres). La première désigne où appuyer pour
   celle-ci ; la seconde désigne où appuyer pour le système. Elles ne donnent
   presque jamais la même tête de liste, et c'est tout l'intérêt. */
function influenceVers(cible){
  const j0 = IX[cible];
  const out = [];
  for (let j = 0; j < NO.length; j++){
    if (j === j0) continue;
    let v = new Float64Array(NO.length);
    const c = new Float64Array(NO.length);
    v[j] = 1;
    for (let t = 0; t < KMAX; t++){
      const nx = new Float64Array(NO.length);
      let bouge = 0;
      for (const l of LI) nx[IX[l.vers]] += l.w * v[IX[l.de]];
      for (let m = 0; m < NO.length; m++){ c[m] += nx[m]; bouge += Math.abs(nx[m]); }
      v = nx;
      if (bouge < SEUIL) break;
    }
    /* LE MOUVEMENT TOTAL EXCLUT LA POUSSÉE ELLE-MÊME : ce qu'une boucle lui
       renvoie à elle n'est pas de l'effet sur le reste du système. */
    let p = 0;
    for (let m = 0; m < NO.length; m++) if (m !== j) p += Math.abs(c[m]);
    out.push({n: NO[j], i: j, v: c[j0], p: p});
  }
  return out;
}

/* Les deux classements tirés de cette table, chacun avec son seuil de
   lisibilité : en dessous de quatre millièmes, le chiffre affiché serait
   « 0,00 » et la ligne ne dirait rien. */
function classeVers(t){ return t.filter(x => Math.abs(x.v) > 0.004)
                              .sort((a, b) => Math.abs(b.v) - Math.abs(a.v)); }
function classeSysteme(t){ return t.filter(x => x.p > 0.004)
                                 .sort((a, b) => b.p - a.p); }

/* ---------- LE RASSEMBLEMENT : LE SCHÉMA SE RÉDUIT À SA CONCLUSION ------
   Les variables que la course a désignées — les mieux reliées du périmètre
   et les plus retraversées par l'onde — glissent en colonne à gauche, avec
   leur compte à droite ; toutes les autres pastilles et toutes les flèches
   s'effacent. On garde ainsi l'image du système ET sa conclusion dans le
   même cadre, reliées par un mouvement plutôt que par un renvoi.

   ELLES GARDENT LEUR PASTILLE, leur jauge et leur chiffre : c'est ce qui
   permet de reconnaître celle qu'on suivait des yeux. Une liste réécrite,
   elle, aurait obligé à la retrouver par son nom. */
let regroupe = false;
/* Les cinq variables qui tiennent le plus la variable poussée, recalculées
   à chaque bilan : le halo et le regroupement les réutilisent plutôt que de
   refaire le même calcul chacun de leur côté. */
let amont = [];

function _elus(){
  /* Trois qui la tiennent, trois qu'elle déplace, la variable poussée
     exclue : c'est la conclusion de la course, pas son point de départ. */
  const j0 = IX[src];
  const av = NO.map((n, i) => ({i, v: Math.abs(cum[i])}))
               .filter(x => x.i !== j0 && x.v > 0.004)
               .sort((a, b) => b.v - a.v).slice(0, 3).map(x => x.i);
  const am = amont.slice(0, 3).map(x => x.i);
  const vus = new Set();
  const out = [];
  for (const i of [...am, ...av]) if (!vus.has(i)){ vus.add(i); out.push(i); }
  return out;
}

function rassembler(on){
  regroupe = !!on;
  const elus = on ? _elus() : [];
  const dedans = new Set(elus);
  const x0 = D.vb[0], y0 = D.vb[1], h = D.vb[3];
  /* La colonne est centrée en hauteur : une liste de trois collée en haut
     d'un cadre taillé pour trente laisserait le bas vide. */
  const pas = 74, haut = Math.max(1, elus.length) * pas;
  const depart = y0 + Math.max(30, (h - haut) / 2);
  vues.forEach((u, i) => {
    const g = u.grp;
    if (!on){
      g.style.transform = "";
      g.style.opacity = "";
      u.det.setAttribute("opacity", "0");
      return;
    }
    if (!dedans.has(i)){ g.style.opacity = "0"; return; }
    const rang = elus.indexOf(i);
    const cx = x0 + 128, cy = depart + rang * pas + pas / 2;
    g.style.opacity = "1";
    g.style.transform = `translate(${(cx - u.n.x).toFixed(1)}px,`
                      + `${(cy - u.n.y).toFixed(1)}px)`;
    const e = cum[i];
    const vers = (amont.find(x => x.i === i) || {}).v;
    /* Deux nombres, et deux sens : ce qu'elle fait à la variable poussée
       quand on la monte de +1, et ce que la course vient de lui faire. */
    const bouts = [];
    if (vers !== undefined) bouts.push("→ " + fmt(vers, 2));
    /* « 0 relais » sur une variable située en amont ne dit rien : l'onde est
       partie dans l'autre sens, elle ne l'a jamais traversée. */
    if (passages[i] > 0) bouts.push(passages[i] + " " + L.vagues);
    /* fmt() pose déjà le signe sur les valeurs à deux décimales : le
       redoubler donnait « ++0,27 ». */
    if (Math.abs(e) > 0.005) bouts.push(fmt(e, 2));
    u.det.textContent = bouts.join("  ·  ");
    u.det.setAttribute("opacity", "1");
  });
  const gl = document.getElementById("gl");
  if (gl) gl.style.opacity = on ? "0" : "1";
  const t = document.getElementById("ttl");
  if (t) t.setAttribute("opacity", on ? "1" : "0");
  const b = document.getElementById("ess");
  b.textContent = on ? L.ess_non : L.ess;
}

/* ---------- l'état de la propagation ----------------------------------- */
let src = D.centre, amp = 1, vitesse = 1, delai = 0, vmax = 0;
let vague = new Float64Array(NO.length);
let cum = new Float64Array(NO.length);
let total = 1, k = 0, joue = false, anim = null, retour = 0;
/* Combien de relais ont déplacé chaque nœud : au-delà d'un, c'est une
   boucle qui a ramené l'onde dessus. */
let passages = new Int32Array(NO.length);

/* Le degré de chaque nœud DANS LE PÉRIMÈTRE DESSINÉ, entrant plus sortant.
   C'est le nombre de liens qu'on voit à l'écran, pas celui du graphe entier :
   annoncer un degré qui ne se compte pas sur l'image serait invérifiable. */
const DEG = new Int32Array(NO.length);
for (const l of LI){ DEG[IX[l.de]] += 1; DEG[IX[l.vers]] += 1; }

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

function horizon(){
  const e = document.getElementById("kt");
  if (!delai || !k){ e.textContent = ""; return; }
  const mois = k*delai;
  e.textContent = mois < 24 ? "≈ " + mois + " " + L.mois
    : "≈ " + (mois/12).toFixed(1).replace(".", "__VIRG__") + " " + L.ans;
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
  /* LE COMPTEUR DIT LA BORNE QUAND IL Y EN A UNE : « 3 / 5 » se lit comme
     une course qui a un terme, « 3 » comme une course qui n'en a pas. */
  document.getElementById("kv").textContent = vmax ? (k + " / " + vmax) : k;
  document.getElementById("kd").textContent =
    Math.round(100*Math.min(1, total ? d/total : 0)) + " % " + L.dis;
  horizon();
}

/* ---------- ce qu'on lit une fois l'onde éteinte ------------------------ */
function bilan(montrer){
  const e = document.getElementById("fin");
  /* LE HALO DORÉ APPARTIENT AU BILAN. Il marque les variables les plus
     connectées du périmètre : une propriété de la structure, vraie avant la
     course comme après. Mais posé à l'ouverture il désignait trois pastilles
     avant qu'on ait rien vu bouger, et allumé dès le premier relais il
     annonçait sa conclusion au milieu de la démonstration. Il arrive donc
     avec le reste du bilan, quand l'onde s'est éteinte ou qu'on l'a bornée,
     et il repart avec lui à la remise à zéro. */
  if (!montrer || !k){
    e.hidden = true;
    poserHalo(false);
    vues.forEach(u => { u.anneau.setAttribute("opacity", 0);
                        u.anneau.classList.remove("cli"); });
    return;
  }
  /* LA VARIABLE POUSSÉE NE FIGURE DANS AUCUN DES DEUX TABLEAUX. Elle est
     le sujet de la question, pas une réponse : dire qu'elle est la mieux
     reliée du périmètre qu'elle a elle-même défini n'apprend rien, et dire
     qu'elle a beaucoup bougé revient à relire la valeur qu'on vient de lui
     imposer. */
  const nom = (NO[IX[src]] || {}).nom || "";
  const table = influenceVers(src);
  amont = classeVers(table).slice(0, 5);
  const aval = NO.map((n, i) => ({n, i, v: cum[i]}))
                 .filter(x => x.n.id !== src && Math.abs(x.v) > 0.004)
                 .sort((a, b) => Math.abs(b.v) - Math.abs(a.v)).slice(0, 5);
  poserHalo(true);
  const ligne = x => '<div class="fl"><span>' + x.n.nom
    + '</span><b style="color:' + (x.v > 0 ? VERT : ROUGE) + '">'
    + fmt(x.v, 2) + '</b></div>';
  /* Les trois autres colonnes ne portent pas un déplacement signé mais une
     grandeur : un volume de mouvement, un nombre de boucles, un nombre de
     relais. Elles restent donc en encre neutre, sans vert ni rouge, qui
     laisseraient croire à une direction. */
  const lignen = (n, txt) => '<div class="fl"><span>' + n.nom
    + '</span><b>' + txt + '</b></div>';
  /* LES TROIS PLUS INFLUENCÉES CLIGNOTENT SUR LE SCHÉMA. Le tableau les
     nomme, le clignotement les montre : lire un nom ne dit pas où il est
     dans le dessin. */
  const chef = new Set(aval.slice(0, 3).map(x => x.n.id));
  vues.forEach(u => {
    const on = chef.has(u.n.id);
    u.anneau.setAttribute("opacity", on ? 1 : 0);
    u.anneau.classList.toggle("cli", on);
  });
  document.getElementById("hc").textContent = L.con.replace("{v}", nom);
  document.getElementById("hp").textContent = L.pas.replace("{v}", nom);
  document.getElementById("fc").innerHTML = amont.map(ligne).join("");
  document.getElementById("fp").innerHTML = aval.map(ligne).join("");

  /* 3. L'EFFET DÉMULTIPLICATEUR. La variable poussée y a sa place, elle :
     la question n'est plus « qui la tient » mais « qui remue le système »,
     et elle est un candidat comme un autre. On la garde donc dans le
     classement, où elle se situe parfois loin de la première place. */
  const mul = classeSysteme(table).slice(0, 5);
  const mag = v => v.toFixed(2).replace(".", "__VIRG__");
  document.getElementById("fm").innerHTML =
    mul.map(x => lignen(x.n, mag(x.p))).join("");

  /* 4. LES BOUCLES. Compté sur la structure du périmètre, pas sur la course :
     une variable est prise dans ses boucles avant qu'on ait rien poussé. Les
     deux nombres sont donnés séparément parce qu'une variable qui siège dans
     les deux familles est un point de bascule, ce qu'une somme cacherait. */
  const bcl = NO.map((n, i) => ({n, i, r: n.br || 0, b: n.bb || 0}))
                .filter(x => x.r + x.b > 0)
                .sort((a, b) => (b.r + b.b) - (a.r + a.b)
                                || (b.r * b.b) - (a.r * a.b)).slice(0, 5);
  document.getElementById("fb").innerHTML = bcl.length
    ? bcl.map(x => lignen(x.n, x.r + " " + L.bcl_r + " · " + x.b + " " + L.bcl_b)).join("")
    : '<div class="fl"><span>' + L.bcl_vide + '</span><b></b></div>';

  /* 5. LES RELAIS REÇUS. Là c'est bien la course qui parle : au-delà d'un
     relais, une boucle a ramené le choc sur la variable. */
  const vg = NO.map((n, i) => ({n, i, p: passages[i]}))
               .filter(x => x.n.id !== src && x.p > 0)
               .sort((a, b) => b.p - a.p).slice(0, 5);
  document.getElementById("fvg").innerHTML =
    vg.map(x => lignen(x.n, x.p + " " + L.vagues)).join("");
  e.hidden = false;
}

function remise(){
  arret();
  k = 0; retour = 0;
  cum = new Float64Array(NO.length);
  vague = new Float64Array(NO.length);
  passages = new Int32Array(NO.length);
  vague[IX[src]] = amp;
  total = totalAbsolu(src, amp) || 1;
  gBilles.innerHTML = "";
  traits.forEach(p => { p.setAttribute("opacity", .34);
                        p.setAttribute("stroke-width", 1.5); });
  document.getElementById("mot").textContent = "";
  rassembler(false);
  const be = document.getElementById("ess");
  if (be) be.hidden = true;
  bilan(false);
  peindre();
}

/* ---------- un relais : les billes partent, puis les scores bougent ---- */
function vaguesuivante(apres){
  const flux = LI.map(l => l.w * vague[IX[l.de]]);
  const suivante = new Float64Array(NO.length);
  LI.forEach((l,i) => { suivante[IX[l.vers]] += flux[i]; });
  let bouge = 0;
  for (let j=0;j<NO.length;j++) bouge += Math.abs(suivante[j]);
  if (bouge < SEUIL){
    document.getElementById("mot").textContent = L.fin;
    arret(); fini(); if (apres) apres(false); return;
  }
  k += 1;
  for (let j=0;j<NO.length;j++)
    if (Math.abs(suivante[j]) > SEUIL) passages[j] += 1;
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

/* LA FIN DE COURSE, EN UN SEUL ENDROIT. L'onde s'éteint d'elle-même ou
   atteint la borne : dans les deux cas le bilan se peint, le bouton du
   regroupement apparaît, et le schéma se réduit de lui-même une seconde
   plus tard. Un pas manuel, lui, ne déclenche rien : on est en train de
   regarder le chemin, ce n'est pas le moment de l'effacer. */
function fini(){
  bilan(true);
  const b = document.getElementById("ess");
  if (b) b.hidden = false;
  setTimeout(() => { if (!regroupe && !joue) rassembler(true); }, 900);
}

function arret(){
  joue = false;
  if (anim){ cancelAnimationFrame(anim); anim = null; }
  document.getElementById("lire").textContent = L.lire;
  document.getElementById("lire").classList.add("p");
}
function boucler(ok){
  if (!joue) return;
  /* TROIS FAÇONS DE S'ARRÊTER : l'onde s'éteint d'elle-même, elle atteint la
     borne demandée, ou elle touche le plafond de sécurité. La borne est un
     réglage de lecture — on veut voir ce que trois relais font, pas trente —
     et non une propriété du système. */
  if (!ok || k >= KMAX || (vmax && k >= vmax)){ arret(); fini(); return; }
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
document.getElementById("nv").onchange = e => {
  vmax = parseInt(e.target.value, 10) || 0;
  peindre();
};
document.getElementById("dl").onchange = e => {
  delai = parseFloat(e.target.value) || 0; horizon();
};
document.getElementById("raz").onclick = remise;
document.getElementById("ess").onclick = () => { rassembler(!regroupe); };
document.getElementById("pas").onclick = () => {
  if (regroupe) rassembler(false);
  arret(); bilan(false); vaguesuivante(v => bilan(true));
};
document.getElementById("lire").onclick = () => {
  if (joue){ arret(); return; }
  if (anim) return;
  /* On ne fait pas courir une onde sur un schéma réduit à six pastilles :
     reprendre la lecture, c'est vouloir revoir le chemin. */
  if (regroupe) rassembler(false);
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
           "dis": T("sd_distrib"), "mois": T("sd_mois"), "ans": T("sd_ans"),
           "liens": T("sd_liens_n"), "vagues": T("sd_vagues_n"),
           "con": T("sd_connect"), "pas": T("sd_passages"),
           "bcl_r": T("sd_bcl_r"), "bcl_b": T("sd_bcl_b"),
           "bcl_vide": T("sd_bcl_vide"),
           "ess": T("sd_ess"), "ess_non": T("sd_ess_non"),
           "ess_t": T("sd_ess_t")}
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
            .replace("__L_LE__", _e(T("sd_leg_e")))
            .replace("__L_DEL0__", _e(T("sd_delai_non")))
            .replace("__L_DEL__", _e(T("sd_delai")))
            .replace("__L_MOIS__", _e(T("sd_mois")))
            .replace("__L_TPS__", _e(T("sd_temps_x")))
            .replace("__L_CONX__", _e(T("sd_connect_x")))
            .replace("__L_CON__", _e(T("sd_connect")))
            .replace("__L_PASX__", _e(T("sd_passages_x")))
            .replace("__L_PAS2__", _e(T("sd_passages")))
            .replace("__L_MUL__", _e(T("sd_mul")))
            .replace("__L_MULX__", _e(T("sd_mul_x")))
            .replace("__L_BCL__", _e(T("sd_bcl")))
            .replace("__L_BCLX__", _e(T("sd_bcl_x")))
            .replace("__L_VAG__", _e(T("sd_vag_t")))
            .replace("__L_VAGX__", _e(T("sd_vag_x")))
            .replace("__L_ESS__", _e(T("sd_ess")))
            .replace("__L_NB__", _e(T("sd_nb")))
            .replace("__L_NBA__", _e(T("sd_nb_auto")))
            .replace("__L_LJ__", _e(T("sd_leg_j")))
            .replace("__L_LC__", _e(T("sd_leg_c"))))


def render():
    """Le schéma du premier onglet, mais qui tourne."""
    lang = i18n.get_lang()
    m = SX._modele(lang)
    st.markdown(SX.STYLE, unsafe_allow_html=True)
    s = SX._systeme(m, "d")
    d = _donnees(m, s["centre"], s["n"])
    if not d["liens"]:
        st.info(T("sd_court"))
        return

    st.markdown(
        f'<div style="background:#fff;border:1px solid #e3eaf3;border-left:5px '
        f'solid {VERT_APRI};border-radius:14px;padding:12px 16px;'
        f'font-size:14px;color:{ENCRE2};line-height:1.6;margin:2px 0 8px;'
        f'max-width:96ch">{T("sd_intro")}'
        # LA DÉFINITION D'UNE VAGUE VIENT AVEC LE MODE D'EMPLOI, dans le même
        # cadre et détachée par un filet : c'est la clé de lecture de tout ce
        # qui suit — le compteur, le bouton d'un pas, le tableau des
        # retraversées et le délai par relais comptent tous des vagues.
        f'<div style="margin-top:10px;padding-top:10px;'
        f'border-top:1px solid #eef2f7;color:{ENCRE3}">'
        f'{T("sd_vague_x")}</div>'
        f'</div>', unsafe_allow_html=True)

    # LA HAUTEUR SUIT LE DESSIN. Un périmètre de quatre pastilles n'a pas
    # besoin de neuf cents pixels, et un périmètre de vingt-six ne tient pas
    # dans six cents : l'iframe est taillée sur le rapport de la boîte.
    haut = int(max(560, min(940, 1180 * d["vb"][3] / max(d["vb"][2], 1) + 210)))
    components.html(_html(d, lang), height=haut, scrolling=False)
    st.caption(T("sd_perim"))
