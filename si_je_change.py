"""Si je change une chose : qu'est-ce qui bouge, de combien, et par où.

POURQUOI CETTE PAGE EXISTE ALORS QUE LES BOUCLES SONT DÉJÀ LÀ
=============================================================

Le site savait déjà propager un choc. Il montrait la vague qui se disperse, et
il montrait le système en marche. Ce qu'il ne faisait pas, et c'est le reproche
auquel cette page répond, c'est EXPLIQUER LE CHIFFRE. Un lecteur voyait
« +0,75 » à côté du revenu sans jamais savoir d'où venaient ces soixante-quinze
centièmes, par quel chemin ils arrivaient, ni ce qu'il fallait en penser.

Cette page ne montre donc pas seulement le résultat, elle montre le calcul.
Pour chaque variable qui bouge, elle dit :

    COMBIEN     l'effet total, en points de l'échelle 0-10 ;
    QUAND       à quel tour de propagation il arrive, et comment il se répartit
                entre les tours ;
    PAR OÙ      la chaîne de liens qui porte l'essentiel de l'effet ;
    SUR QUOI    la force de chaque lien de cette chaîne, sa classe de preuve,
                et la source qui la justifie.

CE QU'EST UN DEGRÉ, ET POURQUOI CE SEUIL-LÀ
===========================================

Dire « effet fort » sans dire fort par rapport à quoi ne veut rien dire. Les
seuils de cette page sont calés sur l'échelle des scores, qui va de 0 à 10 et
dont les barèmes publiés avancent le plus souvent par pas d'un point. Un effet
d'un point entier déplace donc la variable d'un cran de son propre barème :
c'est le seuil au-dessus duquel on peut dire qu'un niveau a changé. En dessous,
les degrés se lisent comme des fractions de ce cran. Le plancher, lui, n'est
pas choisi ici : c'est celui du moteur, qui tient pour négligeable tout ce qui
reste sous cinq centièmes de point.

CE QUE LA PAGE NE DIT PAS
=========================

Le modèle causal est une construction d'expert, pas une estimation faite sur
cette enquête. Les forces viennent d'un barème publié, chaque lien porte sa
classe de preuve et sa source, et la page les affiche plutôt que de les cacher
derrière un résultat. Elle ne prédit pas ce qui arriverait sur le terrain : elle
dit ce que le modèle implique, ce qui est autre chose et doit se lire comme tel.
"""

import numpy as np
import streamlit as st

import boucles_moteur as M
import i18n
from i18n import T

ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"
BORD = "#e6ecf4"
VERT, BLEU, AMBRE, ROUGE, GRIS = ("#1a8a4f", "#2166ac", "#d1730c",
                                  "#c33a24", "#9aa4b5")

# LES TOURS AFFICHÉS. Au-delà du sixième, ce qui reste est sous le seuil de
# négligeabilité pour tous les chocs que la page permet de poser ; le reliquat
# est tout de même compté et montré en bloc, pour que la somme tombe juste.
TOURS = 6

# LA PROFONDEUR DE RECHERCHE DES CHEMINS. Quatre liens suffisent : au-delà, le
# produit des forces tombe sous le seuil de négligeabilité, et un chemin qu'on
# ne peut pas suivre des yeux n'explique plus rien.
PROFONDEUR = 4

# LES DEGRÉS, CALÉS SUR L'ÉCHELLE DES SCORES. Voir le module.
DEGRES = ((1.0, "sc_d1", ROUGE),
          (0.5, "sc_d2", AMBRE),
          (0.2, "sc_d3", BLEU),
          (M.SEUIL_NUL, "sc_d4", GRIS))

TEXTES = {
    "mode_levier": {"en": "If I change one thing",
                    "fr": "Si je change une chose"},
    "sc_titre": {"en": "Move one variable, and see what follows",
                 "fr": "Bougez une variable, et voyez ce qui suit"},
    "sc_intro": {
        "en": "Pick a variable, decide how much it moves, and the page lists "
              "everything the model moves with it. For each one it says how "
              "much, at which round of propagation, through which chain of "
              "links, and on what evidence each of those links rests.",
        "fr": "Choisissez une variable, décidez de combien elle bouge, et la "
              "page énumère tout ce que le modèle fait bouger avec elle. Pour "
              "chacune elle dit de combien, à quel tour de propagation, par "
              "quelle chaîne de liens, et sur quoi repose chacun de ces "
              "liens."},
    "sc_quoi": {"en": "Which variable do you move?",
                "fr": "Quelle variable bougez-vous ?"},
    "sc_combien": {"en": "By how much, in points out of ten",
                   "fr": "De combien, en points sur dix"},
    "sc_pose": {"en": "You are moving {n} by {d} points.",
                "fr": "Vous bougez {n} de {d} points."},
    "sc_rien": {"en": "Nothing moves: this variable has no outgoing link in "
                      "the model.",
                "fr": "Rien ne bouge : cette variable n'a aucun lien sortant "
                      "dans le modèle."},
    "sc_nul": {"en": "Set a change other than zero to see what follows.",
               "fr": "Posez un changement autre que zéro pour voir ce qui "
                     "suit."},

    # ---- le tableau
    "sc_liste_t": {"en": "What moves, and by how much",
                   "fr": "Ce qui bouge, et de combien"},
    "sc_liste_x": {
        "en": "{k} of the {n} variables in the model move by more than the "
              "negligibility floor. The rest are left out rather than listed "
              "at zero.",
        "fr": "{k} des {n} variables du modèle bougent de plus que le "
              "plancher de négligeabilité. Les autres sont laissées de côté "
              "plutôt qu'alignées à zéro."},
    "sc_col_var": {"en": "Variable", "fr": "Variable"},
    "sc_col_eff": {"en": "Effect", "fr": "Effet"},
    "sc_col_deg": {"en": "Degree", "fr": "Degré"},
    "sc_col_tour": {"en": "Arrives at", "fr": "Arrive au"},
    "sc_tour": {"en": "round {k}", "fr": "tour {k}"},

    # ---- les degrés
    "sc_deg_t": {"en": "What the degrees mean, and why those thresholds",
                 "fr": "Ce que valent les degrés, et pourquoi ces seuils"},
    "sc_deg_x": {
        "en": "Saying \"strong\" without saying strong against what "
              "means nothing. These thresholds are set on the score scale, "
              "which runs from 0 to 10 and whose published rubrics most often "
              "advance one point at a time. An effect of a full point "
              "therefore moves the variable up one notch of its own rubric.",
        "fr": "Dire « fort » sans dire fort par rapport à quoi ne veut rien "
              "dire. Ces seuils sont calés sur l'échelle des scores, qui va "
              "de 0 à 10 et dont les barèmes publiés avancent le plus souvent "
              "par pas d'un point. Un effet d'un point entier déplace donc la "
              "variable d'un cran de son propre barème."},
    "sc_d1": {"en": "changes the level", "fr": "change le niveau"},
    "sc_d1_x": {"en": "one full point or more: one notch of the rubric",
                "fr": "un point entier ou plus : un cran du barème"},
    "sc_d2": {"en": "clear", "fr": "net"},
    "sc_d2_x": {"en": "half a notch to a notch", "fr": "d'un demi-cran à un cran"},
    "sc_d3": {"en": "moderate", "fr": "modéré"},
    "sc_d3_x": {"en": "a fifth to a half of a notch",
                "fr": "d'un cinquième à un demi-cran"},
    "sc_d4": {"en": "faint", "fr": "faible"},
    "sc_d4_x": {"en": "visible, but under a fifth of a notch",
                "fr": "visible, mais sous un cinquième de cran"},
    "sc_d5": {"en": "negligible", "fr": "négligeable"},
    "sc_d5_x": {"en": "under {s} point, the engine's own floor",
                "fr": "sous {s} point, le plancher du moteur lui-même"},

    # ---- l'explication d'un chiffre
    "sc_pourquoi_t": {"en": "Where that figure comes from",
                      "fr": "D'où vient ce chiffre"},
    "sc_cible": {"en": "Explain the effect on", "fr": "Expliquer l'effet sur"},
    "sc_tours_t": {"en": "How the effect arrives, round by round",
                   "fr": "Comment l'effet arrive, tour par tour"},
    "sc_tours_x": {
        "en": "The model propagates in rounds. Round 1 is what a direct link "
              "carries; round 2 is what the neighbours of the neighbours "
              "carry, and so on. Adding them up gives the total.",
        "fr": "Le modèle propage par tours. Le tour 1, c'est ce que porte un "
              "lien direct ; le tour 2, ce que portent les voisins des "
              "voisins, et ainsi de suite. Leur somme fait le total."},
    "sc_reste": {"en": "rounds {k} and beyond", "fr": "tours {k} et au-delà"},
    "sc_total": {"en": "total", "fr": "total"},
    "sc_chemin_t": {"en": "The chain that carries the most",
                    "fr": "La chaîne qui en porte le plus"},
    "sc_chemin_x": {
        "en": "Of all the routes from one to the other, this is the one whose "
              "product of forces is largest. It is not the only route, which "
              "is why it accounts for {p} of the total rather than all of it.",
        "fr": "De tous les chemins qui vont de l'une à l'autre, voici celui "
              "dont le produit des forces est le plus grand. Ce n'est pas le "
              "seul, et c'est pourquoi il porte {p} du total et non la "
              "totalité."},
    "sc_calcul": {"en": "The arithmetic of that chain",
                  "fr": "Le calcul de cette chaîne"},
    "sc_aucun": {"en": "No chain of four links or fewer joins the two: the "
                       "effect arrives by longer routes, or by several at "
                       "once.",
                 "fr": "Aucune chaîne de quatre liens ou moins ne relie les "
                       "deux : l'effet arrive par des chemins plus longs, ou "
                       "par plusieurs à la fois."},
    "sc_lien_force": {"en": "force", "fr": "force"},
    "sc_lien_sur": {"en": "Rests on", "fr": "Repose sur"},
    "sc_geo": {"en": "Context of the study: {g}.",
               "fr": "Contexte de l'étude : {g}."},
    "sc_type": {"en": "Type of evidence: {t}.",
                "fr": "Type de preuve : {t}."},
    "sc_avec_force": {"en": "with a strength of {f}",
                      "fr": "avec une force de {f}"},
    "sc_classee": {"en": "and a class of evidence of {c}",
                   "fr": "et une classe de preuve « {c} »"},
    "sc_ouvrir": {"en": "open the source", "fr": "ouvrir la source"},
    "sc_reserve": {"en": "Caveat.", "fr": "Réserve :"},
    "sc_conteste": {
        "en": "The source contradicts the direction of this arrow. It is "
              "flagged rather than silently flipped: turning an arrow round "
              "is a modelling decision, not a correction.",
        "fr": "La source contredit le sens de cette flèche. Elle est signalée "
              "plutôt que retournée en silence : retourner une flèche est une "
              "décision de modélisation, pas une correction."},
    "sc_sans_src": {
        "en": "No verifiable source was found for this link. It is kept, "
              "capped, and says so.",
        "fr": "Aucune source vérifiable n'a été trouvée pour ce lien. Il est "
              "conservé, plafonné, et le dit."},
    "sc_preuves_t": {"en": "How these links were checked",
                     "fr": "Comment ces liens ont été vérifiés"},
    "sc_preuves_x": {
        "en": "Each of the {t} links in the model was searched on the web, "
              "its source opened and read, and its effect size recorded. "
              "{v} carry a source that was actually opened. {s} carry none, "
              "and say so. And on {c} of them the source contradicts the "
              "direction of the arrow: those are flagged where they appear, "
              "not quietly turned round.",
        "fr": "Chacun des {t} liens du modèle a été cherché sur le web, sa "
              "source ouverte et lue, et sa taille d'effet relevée. {v} "
              "portent une source réellement ouverte. {s} n'en portent "
              "aucune, et le disent. Et sur {c} d'entre eux la source "
              "contredit le sens de la flèche : ceux-là sont signalés là où "
              "ils apparaissent, pas retournés en douce."},
    "sc_renforce": {"en": "raises", "fr": "renforce"},
    "sc_diminue": {"en": "lowers", "fr": "diminue"},

    # ---- les forces
    "sc_bareme_t": {"en": "Where the forces themselves come from",
                    "fr": "D'où viennent les forces elles-mêmes"},
    "sc_bareme_x": {
        "en": "Every link carries a force between 0 and 1, taken from a "
              "published five-rung rubric, and a class of evidence that caps "
              "how high that force may go. A link nobody has measured cannot "
              "be given the weight of one that has been.",
        "fr": "Chaque lien porte une force entre 0 et 1, prise sur un barème "
              "publié à cinq échelons, et une classe de preuve qui plafonne "
              "la force qu'on a le droit de lui donner. Un lien que personne "
              "n'a mesuré ne peut pas recevoir le poids d'un lien mesuré."},
    "sc_ech": {"en": "The five rungs", "fr": "Les cinq échelons"},
    "sc_cls": {"en": "The classes, and their ceiling",
               "fr": "Les classes, et leur plafond"},
    "sc_plafond": {"en": "ceiling {v}", "fr": "plafond {v}"},

    # ---- l'avertissement
    "sc_mise_t": {"en": "One caution, stated rather than hidden",
                  "fr": "Une réserve, dite plutôt que cachée"},
    "sc_mise_x": {
        "en": "Written as they stand, the forces give the graph a spectral "
              "radius of {r}, which is to say the system sits at the edge of "
              "runaway: two points on one lever would produce fifteen on "
              "another, which is absurd on a scale that stops at ten. Every "
              "force is therefore scaled by {f} before propagating. The "
              "ranking of what moves is unchanged; the amounts are readable. "
              "And the model remains an expert construction, not an estimate "
              "made on this survey.",
        "fr": "Écrites telles quelles, les forces donnent au graphe un rayon "
              "spectral de {r}, autrement dit le système se tient au bord de "
              "l'emballement : deux points sur un levier en produiraient "
              "quinze sur un autre, ce qui est absurde sur une échelle qui "
              "s'arrête à dix. Toutes les forces sont donc mises à l'échelle "
              "de {f} avant de propager. Le classement de ce qui bouge ne "
              "change pas ; les montants deviennent lisibles. Et le modèle "
              "reste une construction d'expert, pas une estimation faite sur "
              "cette enquête."},

    # ---- la pagination
    "sc_pg_prec": {"en": "Previous", "fr": "Précédent"},
    "sc_pg_suiv": {"en": "Next", "fr": "Suivant"},
    "sc_pg_de": {"en": "{a} of {b}", "fr": "{a} sur {b}"},
    "sc_pg_fin": {"en": "End of the page.", "fr": "Fin de la page."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _f(v, dec=2, signe=False):
    if v is None:
        return "—"
    s = f"{float(v):+.{dec}f}" if signe else f"{float(v):.{dec}f}"
    return s.replace(".", ",") if i18n.get_lang() != "en" else s


STYLE = """
<style>
  .sc-h   { font-size:16.5px; font-weight:700; color:#101728;
            letter-spacing:-.015em; margin:22px 0 5px; }
  .sc-x   { font-size:13.5px; color:#3c4761; line-height:1.62; margin:0 0 8px;
            max-width:88ch; }
  .sc-lab { font-size:10.5px; letter-spacing:.1em; text-transform:uppercase;
            color:#8a93a5; font-weight:700; margin:18px 0 7px; }
  /* le tableau de ce qui bouge */
  /* LA RANGÉE EST BORNÉE EN LARGEUR. Sur toute la largeur du contenu, la
     première colonne en `1fr` avalait l'espace libre et le nom se retrouvait
     à trente centimètres de son propre chiffre : l'œil ne faisait plus le
     lien entre les deux. */
  .sc-r   { display:grid; grid-template-columns:1fr 74px 150px 118px 78px;
            gap:11px; align-items:center; padding:7px 0; max-width:880px;
            border-top:1px solid #eef2f7; font-size:13px; }
  .sc-r:first-child { border-top:none; }
  .sc-r .nm { color:#101728; font-weight:600; }
  .sc-r .vv { font-variant-numeric:tabular-nums; font-weight:700;
              text-align:right; }
  .sc-r .ba { height:8px; border-radius:4px; background:#eef2f7;
              overflow:hidden; }
  .sc-r .ba i { display:block; height:100%; border-radius:4px; }
  .sc-r .dg { font-size:11.5px; font-weight:700; }
  .sc-r .tr { font-size:11.5px; color:#8a93a5; text-align:right; }
  .sc-th  { font-size:10px; letter-spacing:.07em; text-transform:uppercase;
            color:#8a93a5; font-weight:700; border-top:none !important; }
  .sc-th span:not(:first-child) { text-align:right; }
  /* la légende des degrés */
  .sc-dg  { display:grid; grid-template-columns:repeat(5,1fr); gap:9px;
            margin-top:8px; }
  .sc-dc  { border:1px solid #eaeff6; border-top:3px solid var(--c);
            border-radius:11px; padding:10px 12px 12px; background:#fff; }
  .sc-dc b{ display:block; font-size:12.5px; color:var(--c); font-weight:700; }
  .sc-dc i{ display:block; font-style:normal; font-size:15px; font-weight:800;
            color:#101728; margin:5px 0 4px;
            font-variant-numeric:tabular-nums; }
  .sc-dc span { font-size:11px; color:#6b7590; line-height:1.4; }
  /* les tours */
  .sc-t   { display:grid; grid-template-columns:96px 1fr 74px; gap:11px;
            align-items:center; padding:5px 0; font-size:12.5px;
            max-width:880px; }
  .sc-t b { color:#3c4761; font-weight:600; }
  .sc-t .ba { height:9px; border-radius:5px; background:#eef2f7;
              overflow:hidden; }
  .sc-t .ba i { display:block; height:100%; border-radius:5px; }
  .sc-t .vv { font-variant-numeric:tabular-nums; font-weight:700;
              text-align:right; color:#101728; }
  .sc-tot { border-top:1px solid #e6ecf4; margin-top:5px; padding-top:8px; }
  /* la chaîne */
  .sc-ch  { display:flex; flex-wrap:wrap; align-items:stretch; gap:7px;
            margin:9px 0 4px; }
  .sc-n   { border:1px solid #e3eaf3; border-radius:11px; padding:8px 12px;
            background:#fff; font-size:12.5px; font-weight:600;
            color:#101728; display:flex; align-items:center; }
  .sc-l   { display:flex; flex-direction:column; justify-content:center;
            align-items:center; min-width:76px; }
  .sc-l b { font-size:11px; font-weight:800; font-variant-numeric:tabular-nums; }
  .sc-l s { text-decoration:none; font-size:9.5px; letter-spacing:.06em;
            text-transform:uppercase; color:#8a93a5; font-weight:700; }
  .sc-l u { text-decoration:none; display:block; height:2px; width:100%;
            border-radius:2px; margin:3px 0; }
  .sc-src { font-size:11.5px; color:#6b7590; line-height:1.55;
            border-left:2px solid #e3eaf3; padding:1px 0 1px 11px;
            margin:4px 0 0; }
  .sc-p    { font-size:13px; color:#3c4761; line-height:1.7; margin:0 0 11px;
             max-width:92ch; border-left:2px solid #e3eaf3; padding-left:13px; }
  .sc-p b  { color:#101728; font-weight:600; }
  .sc-cit  { color:#101728; font-weight:500; }
  .sc-ref  { color:#8a93a5; font-size:11px; line-height:1.5; }
  .sc-a    { color:#2166ac; text-decoration:none;
             border-bottom:1px solid #cfdcec; }
  .sc-res  { color:#8a93a5; font-size:11px; font-style:italic;
             line-height:1.5; }
  .sc-att  { color:#c33a24; font-weight:700; font-size:11.5px; }
  .sc-cal { max-width:880px; font-size:13px; color:#101728; background:#f7f9fc;
            border:1px solid #eef2f7; border-radius:11px;
            padding:11px 14px; margin-top:9px;
            font-variant-numeric:tabular-nums; line-height:1.7;
            text-align:left !important; }
  /* le barème */
  .sc-b   { display:grid; grid-template-columns:56px 1fr; gap:11px;
            max-width:880px;
            align-items:baseline; padding:5px 0;
            border-top:1px solid #f2f5fa; font-size:12.5px; }
  .sc-b b { font-variant-numeric:tabular-nums; font-weight:800;
            color:#101728; }
  .sc-b span { color:#3c4761; line-height:1.5; }
  /* ---------------------------------------------------------- LA PAGINATION
     Le contenu ne se déroule plus, il se tourne. Chaque écran est un
     conteneur Streamlit dont la CLÉ change avec le numéro de page : le nœud
     du DOM est donc neuf à chaque tour, et l'animation rejoue d'elle-même.
     Sans ce changement de clé, React réutiliserait le même nœud et le fondu
     ne se verrait qu'une fois. */
  @keyframes scFondu {
    from { opacity:0; transform:translateY(6px); }
    to   { opacity:1; transform:none; }
  }
  div[class*="st-key-sc_ecran_"] { animation:scFondu .34s cubic-bezier(.22,.61,.36,1) both; }
  /* le pied de page : titre de l'écran à gauche, les deux flèches à droite */
  /* LE PIED TIENT SUR UNE SEULE RANGÉE. Les traits de position étaient
     d'abord sur leur propre ligne, sous le titre ; le bloc des boutons, qui
     est un conteneur Streamlit distinct, remontait par-dessus et les coupait
     en deux. Rangés dans la même rangée que le titre, ils ne peuvent plus
     être recouverts. */
  .sc-pied { display:flex; align-items:center; gap:16px; margin:26px 0 11px;
             padding-top:13px; border-top:1px solid #eef2f7; }
  .sc-pied .ti { font-size:12.5px; color:#3c4761; font-weight:600; }
  .sc-pied .nb { font-size:11.5px; color:#9aa4b5;
                 font-variant-numeric:tabular-nums; letter-spacing:.03em; }
  /* les traits de position, sobres : un trait plein pour l'écran courant */
  .sc-puces { display:flex; gap:6px; margin-left:auto; }
  .sc-puces i { display:block; width:26px; height:2px; border-radius:1px;
                background:#e3e9f1; transition:background .25s; }
  .sc-puces i.on { background:#1a8a4f; }
  /* les boutons de tour de page : du texte, pas des pavés */
  /* LES DÉCLARATIONS SONT FORCÉES. Le thème global de l'application impose
     aux boutons une taille de police et une hauteur minimale plus fortes en
     spécificité que ce sélecteur ; sans !important, les deux flèches se
     dessinaient en pavés de quatre-vingts pixels de haut. */
  div[class*="st-key-sc_nav_"] .stButton > button {
      background:none !important; border:1px solid #e3e9f1 !important;
      border-radius:7px !important; color:#3c4761 !important;
      font-size:12.5px !important; font-weight:600 !important;
      padding:6px 14px !important; min-height:0 !important;
      height:auto !important; line-height:1.25 !important;
      box-shadow:none !important; white-space:nowrap;
      transition:border-color .2s, color .2s; }
  div[class*="st-key-sc_nav_"] .stButton > button p {
      font-size:12.5px !important; font-weight:600 !important;
      line-height:1.25 !important; margin:0 !important; }
  div[class*="st-key-sc_nav_"] .stButton > button:hover:not(:disabled),
  div[class*="st-key-sc_nav_"] .stButton > button:hover:not(:disabled) p {
      border-color:#1a8a4f !important; color:#1a8a4f !important; }
  div[class*="st-key-sc_nav_"] .stButton > button:disabled,
  div[class*="st-key-sc_nav_"] .stButton > button:disabled p {
      color:#c3cad6 !important; border-color:#f1f4f8 !important; }
  @media (max-width:900px){
    .sc-dg{grid-template-columns:repeat(2,1fr)}
    .sc-r{grid-template-columns:1fr 62px 96px}
    .sc-r .dg,.sc-r .tr{display:none}
  }
</style>
"""


# ------------------------------------------------------------------ le calcul
@st.cache_data(show_spinner=False)
def _modele(lang):
    """Le graphe, sa matrice mise à l'échelle, et de quoi lire ses liens."""
    g = M.charger()
    if not g or not g.get("noeuds"):
        return None
    A, ids, idx = M.matrice(g)
    noms = {n["id"]: (n.get(lang) or n.get("fr") or n["id"])
            for n in g["noeuds"]}
    # les arêtes, indexées par couple, pour retrouver force, classe et source
    aretes = {}
    for e in g["aretes"]:
        aretes[(e["de"], e["vers"])] = {
            "signe": e["signe"], "force": e["force"], "just": e.get("just"),
            "ref": e.get("ref_" + lang) or e.get("ref_fr"),
            "src": e.get("src"),
            "reserve": e.get("reserve_" + lang) or e.get("reserve_fr"),
            "cite": e.get("cite_" + lang) or e.get("cite_fr"),
            "conteste": bool(e.get("conteste"))}
    sortants = {}
    for (u, v) in aretes:
        sortants.setdefault(u, []).append(v)
    return {"g": g, "A": A, "ids": ids, "idx": idx, "noms": noms,
            "aretes": aretes, "sortants": sortants,
            "diag": M.diagnostic(g), "bareme": g.get("bareme") or {},
            "preuves": g.get("preuves") or {}}


def _propager(m, source, delta):
    """L'effet total, et sa décomposition tour par tour.

    LA DÉCOMPOSITION EST LE CŒUR DE LA PAGE. L'effet total se calcule d'un
    coup en résolvant (I − A)x = e₀, mais un résultat obtenu d'un coup
    n'explique rien. La même quantité est donc aussi obtenue comme une somme
    de tours : A·e₀ au premier, A²·e₀ au deuxième, et ainsi de suite. Les deux
    voies donnent le même nombre, et la seconde dit par où il passe.
    """
    A, ids, idx = m["A"], m["ids"], m["idx"]
    e0 = np.zeros(len(ids))
    e0[idx[source]] = float(delta)
    total = np.linalg.solve(np.eye(len(ids)) - A, e0) - e0

    tours, v, cumul = [], e0.copy(), np.zeros(len(ids))
    for _ in range(TOURS):
        v = A.dot(v)
        cumul += v
        tours.append(v.copy())
    reste = total - cumul
    return total, tours, reste


def _degre(v):
    """Le degré d'un effet, et sa couleur. Les seuils sont dans DEGRES."""
    a = abs(v)
    for seuil, cle, coul in DEGRES:
        if a >= seuil:
            return cle, coul
    return "sc_d5", GRIS


def _chemins(m, source, cible):
    """Le chemin de force maximale entre deux nœuds, s'il en existe un court.

    On cherche le produit des forces le plus grand, pas le chemin le plus
    court : un chemin de trois liens forts porte davantage qu'un lien faible
    en direct, et c'est bien celui-là qu'il faut montrer pour expliquer.
    """
    A, idx = m["A"], m["idx"]
    meilleur = {"produit": 0.0, "chemin": None}

    def marcher(courant, chemin, produit):
        if len(chemin) > PROFONDEUR:
            return
        for suivant in m["sortants"].get(courant, []):
            if suivant in chemin:
                continue
            p = produit * A[idx[suivant], idx[courant]]
            if abs(p) < 1e-6:
                continue
            if suivant == cible:
                if abs(p) > abs(meilleur["produit"]):
                    meilleur["produit"] = p
                    meilleur["chemin"] = chemin + [suivant]
            elif len(chemin) < PROFONDEUR:
                marcher(suivant, chemin + [suivant], p)

    marcher(source, [source], 1.0)
    return meilleur


# ------------------------------------------------------------------ l'affichage
def _tableau(m, total, tours, source, calcule_seulement=False):
    """Tout ce qui bouge, trié par ampleur, avec son degré et son tour.

    `calcule_seulement` sert au sommaire de la pagination : il faut savoir
    combien de variables bougent pour décider du nombre d'écrans, et cela
    avant d'avoir choisi lequel afficher. Sans ce drapeau, le tableau se
    dessinerait deux fois, ou en haut d'un écran auquel il n'appartient pas.
    """
    ids = m["ids"]
    lignes = []
    for i, nid in enumerate(ids):
        if nid == source or abs(total[i]) < M.SEUIL_NUL:
            continue
        # LE TOUR D'ARRIVÉE, C'EST LE PREMIER OÙ LA VARIABLE BOUGE VRAIMENT.
        # Un tour qui n'apporte qu'un millième n'est pas une arrivée, c'est
        # un arrondi ; on retient le premier tour qui dépasse le plancher.
        tour = next((k + 1 for k, v in enumerate(tours)
                     if abs(v[i]) >= M.SEUIL_NUL / 4), None)
        lignes.append({"id": nid, "nom": m["noms"][nid],
                       "eff": float(total[i]), "tour": tour})
    lignes.sort(key=lambda x: -abs(x["eff"]))
    if not lignes or calcule_seulement:
        return lignes

    maxi = max(abs(x["eff"]) for x in lignes)
    st.markdown(
        f'<div class="sc-r sc-th"><span>{_e(T("sc_col_var"))}</span>'
        f'<span>{_e(T("sc_col_eff"))}</span><span></span>'
        f'<span>{_e(T("sc_col_deg"))}</span>'
        f'<span>{_e(T("sc_col_tour"))}</span></div>', unsafe_allow_html=True)
    for x in lignes:
        cle, coul = _degre(x["eff"])
        st.markdown(
            f'<div class="sc-r"><span class="nm">{_e(x["nom"])}</span>'
            f'<span class="vv" style="color:{coul}">{_f(x["eff"], 2, True)}</span>'
            f'<span class="ba"><i style="width:{abs(x["eff"]) / maxi * 100:.0f}%;'
            f'background:{coul}"></i></span>'
            f'<span class="dg" style="color:{coul}">{_e(T(cle))}</span>'
            f'<span class="tr">'
            f'{_e(T("sc_tour", k=x["tour"])) if x["tour"] else "—"}</span>'
            f'</div>', unsafe_allow_html=True)
    return lignes


def _legende_degres():
    seuils = [f'≥ {_f(s, 2)}' for s, _, _ in DEGRES]
    cases = []
    for (seuil, cle, coul), lib in zip(DEGRES, seuils):
        cases.append(
            f'<div class="sc-dc" style="--c:{coul}">'
            f'<b>{_e(T(cle))}</b><i>{_e(lib)}</i>'
            f'<span>{_e(T(cle + "_x"))}</span></div>')
    cases.append(
        f'<div class="sc-dc" style="--c:{GRIS}">'
        f'<b>{_e(T("sc_d5"))}</b><i>&lt; {_f(M.SEUIL_NUL, 2)}</i>'
        f'<span>{_e(T("sc_d5_x", s=_f(M.SEUIL_NUL, 2)))}</span></div>')
    st.markdown('<div class="sc-dg">' + "".join(cases) + '</div>',
                unsafe_allow_html=True)


def _tours(m, total, tours, reste, i):
    """Le même chiffre, obtenu comme une somme de tours."""
    vals = [(k + 1, float(v[i])) for k, v in enumerate(tours)]
    vals = [(k, v) for k, v in vals if abs(v) >= M.SEUIL_NUL / 8]
    r = float(reste[i])
    maxi = max([abs(v) for _, v in vals] + [abs(r), 1e-6])
    lignes = []
    for k, v in vals:
        c = VERT if v > 0 else ROUGE
        lignes.append(
            f'<div class="sc-t"><b>{_e(T("sc_tour", k=k))}</b>'
            f'<span class="ba"><i style="width:{abs(v) / maxi * 100:.0f}%;'
            f'background:{c}"></i></span>'
            f'<span class="vv">{_f(v, 3, True)}</span></div>')
    if abs(r) >= M.SEUIL_NUL / 8:
        c = VERT if r > 0 else ROUGE
        lignes.append(
            f'<div class="sc-t"><b>{_e(T("sc_reste", k=TOURS + 1))}</b>'
            f'<span class="ba"><i style="width:{abs(r) / maxi * 100:.0f}%;'
            f'background:{c}"></i></span>'
            f'<span class="vv">{_f(r, 3, True)}</span></div>')
    lignes.append(
        f'<div class="sc-t sc-tot"><b>{_e(T("sc_total"))}</b><span></span>'
        f'<span class="vv">{_f(float(total[i]), 3, True)}</span></div>')
    st.markdown("".join(lignes), unsafe_allow_html=True)


def _chaine(m, chemin, produit, delta, total_cible):
    """La chaîne dominante, lien par lien, avec sa preuve et son calcul."""
    morceaux, calcul = [], [_f(delta, 2, True)]
    for a, b in zip(chemin, chemin[1:]):
        e = m["aretes"][(a, b)]
        coul = VERT if e["signe"] > 0 else ROUGE
        morceaux.append(f'<div class="sc-n">{_e(m["noms"][a])}</div>')
        morceaux.append(
            f'<div class="sc-l"><s>{_e(T("sc_lien_force"))}</s>'
            f'<u style="background:{coul}"></u>'
            f'<b style="color:{coul}">'
            f'{"+" if e["signe"] > 0 else "−"}{_f(e["force"], 2)}</b>'
            f'</div>')
        calcul.append(f'{"×" if e["signe"] > 0 else "× −"}'
                      f'{_f(e["force"], 2)}')
    morceaux.append(f'<div class="sc-n">{_e(m["noms"][chemin[-1]])}</div>')
    st.markdown('<div class="sc-ch">' + "".join(morceaux) + '</div>',
                unsafe_allow_html=True)

    # LES SOURCES, SOUS LA CHAÎNE, ET EN TEXTE SUIVI.
    #
    # UN CHIFFRE SANS SA RÉFÉRENCE EST UN CHIFFRE POSÉ D'AUTORITÉ. Chaque
    # taille d'effet est donc suivie, dans la même phrase, du nom de l'auteur,
    # de l'année et du titre de la publication. La référence n'est pas reléguée
    # dans une ligne de métadonnées en petits caractères sous le paragraphe :
    # elle est à l'endroit exact où le lecteur lit le nombre, parce que c'est
    # là qu'il se demande d'où il sort.
    #
    # Le bloc se lit comme un paragraphe, pas comme une fiche. Ce que le lien
    # affirme, sur quoi cela repose, dans quel contexte l'étude a été faite,
    # et ce qui limite la portée du résultat : quatre choses qui s'enchaînent,
    # dans l'ordre où l'on se pose les questions.
    st.markdown(f'<div class="sc-lab">{_e(T("sc_lien_sur"))}</div>',
                unsafe_allow_html=True)
    for a, b in zip(chemin, chemin[1:]):
        e = m["aretes"][(a, b)]
        src = e.get("src") or {}
        verbe = T("sc_renforce") if e["signe"] > 0 else T("sc_diminue")
        cls = T("bcl_j_" + str(e["just"])) if e.get("just") else ""

        t = [f'<p class="sc-p"><b>{_e(m["noms"][a])}</b> {_e(verbe)} '
             f'<b>{_e(m["noms"][b])}</b>, '
             f'{_e(T("sc_avec_force", f=_f(e["force"], 2)))}']
        if cls:
            t.append(f' {_e(T("sc_classee", c=cls.lower()))}')
        t.append('.')

        if e.get("conteste"):
            t.append(f' <span class="sc-att">{_e(T("sc_conteste"))}</span>')

        if e.get("ref"):
            t.append(f' {_e(e["ref"])}')
        if e.get("cite"):
            t.append(f' <span class="sc-cit">({_e(e["cite"])}'
                     + (f', <a href="{src["url"]}" target="_blank" class="sc-a">'
                        f'{_e(T("sc_ouvrir"))}</a>' if src.get("url") else "")
                     + ')</span>')
        elif not src:
            t.append(f' <span class="sc-att">{_e(T("sc_sans_src"))}</span>')

        # Le contexte et le type de preuve existent dans les deux langues :
        # en anglais, servir la version française laisserait une phrase
        # bilingue au milieu du paragraphe.
        lg = i18n.get_lang()
        geo = (src.get("geo_en") if lg == "en" else None) or src.get("geo")
        typ = (src.get("type_en") if lg == "en" else None) or src.get("type")
        detail = []
        if geo:
            detail.append(T("sc_geo", g=geo))
        if typ:
            detail.append(T("sc_type", t=typ))
        if detail:
            t.append(' ' + _e(" ".join(detail)))
        if e.get("reserve"):
            t.append(f' <span class="sc-res">{_e(T("sc_reserve"))} '
                     f'{_e(e["reserve"])}</span>')
        t.append('</p>')
        st.markdown("".join(t), unsafe_allow_html=True)

    # LE CALCUL, ÉCRIT. La mise à l'échelle est rappelée à sa place dans la
    # multiplication : sans elle, le produit affiché ne tomberait pas sur le
    # chiffre du tableau, et le lecteur aurait raison de ne pas nous croire.
    fac = m["diag"]["facteur"]
    n = len(chemin) - 1
    st.markdown(
        f'<div class="sc-cal">{" ".join(calcul)} '
        f'× {_f(fac, 3)}<sup>{n}</sup> = '
        f'<b>{_f(produit * delta, 3, True)}</b><br>'
        f'<span style="color:{ENCRE3};font-size:12px">'
        f'{_e(T("sc_chemin_x", p=_f(abs(produit * delta / total_cible) * 100, 0) + " %"))}'
        f'</span></div>', unsafe_allow_html=True)


def _bareme(m):
    b = m["bareme"]
    lang = i18n.get_lang()
    if b.get("echelons"):
        st.markdown(f'<div class="sc-lab">{_e(T("sc_ech"))}</div>',
                    unsafe_allow_html=True)
        st.markdown("".join(
            f'<div class="sc-b"><b>{_f(e["v"], 2)}</b>'
            f'<span>{_e(e.get(lang) or e.get("fr"))}</span></div>'
            for e in b["echelons"]), unsafe_allow_html=True)
    if b.get("classes"):
        st.markdown(f'<div class="sc-lab">{_e(T("sc_cls"))}</div>',
                    unsafe_allow_html=True)
        st.markdown("".join(
            f'<div class="sc-b"><b>{_e(T("sc_plafond", v=_f(c["max"], 2)))}'
            f'</b><span>{_e(c.get(lang) or c.get("fr"))}</span></div>'
            for c in b["classes"]), unsafe_allow_html=True)


# ------------------------------------------------------------------ la page
def _pied(page, titres, cle):
    """Le pied de page : où l'on est, et les deux flèches pour tourner.

    LE NUMÉRO D'ÉCRAN VIT DANS session_state, PAS DANS UNE VARIABLE. Streamlit
    réexécute le module entier à chaque clic ; une variable locale serait
    remise à zéro avant même d'avoir servi. La clé porte la langue, sans quoi
    passer du français à l'anglais ramènerait le lecteur au premier écran.
    """
    n = len(titres)
    st.markdown(
        f'<div class="sc-pied"><span class="ti">{_e(titres[page])}</span>'
        '<span class="sc-puces">'
        + "".join(f'<i class="{"on" if k == page else ""}"></i>'
                  for k in range(n))
        + '</span>'
        f'<span class="nb">{_e(T("sc_pg_de", a=page + 1, b=n))}</span>'
        '</div>', unsafe_allow_html=True)

    with st.container(key=f"sc_nav_{cle}"):
        g, d, _ = st.columns([1, 1, 7], gap="small")
        with g:
            if st.button(f'← {T("sc_pg_prec")}', key=f"sc_prec_{cle}",
                         disabled=page == 0, use_container_width=True):
                st.session_state[cle] = page - 1
                st.rerun()
        with d:
            if st.button(f'{T("sc_pg_suiv")} →', key=f"sc_suiv_{cle}",
                         disabled=page >= n - 1, use_container_width=True):
                st.session_state[cle] = page + 1
                st.rerun()


def render(entete=True):
    """La page, tournée écran par écran plutôt que déroulée.

    POURQUOI PAGINER PLUTÔT QUE DÉROULER. La page dit quatre choses de nature
    différente : ce qui bouge, ce que valent les degrés, d'où vient un chiffre
    donné, et sur quoi tout cela repose. Déroulées à la file, elles obligeaient
    le lecteur à descendre pour retrouver le tableau qu'il venait de quitter.
    Tournées, chacune tient sur un écran et se lit pour elle-même.

    LES COMMANDES RESTENT SUR LE PREMIER ÉCRAN. Les remettre sur chaque écran
    aurait chargé la page de ce qu'elle cherche justement à alléger : on choisit
    sa variable, puis on lit ce qui suit.
    """
    st.markdown(STYLE, unsafe_allow_html=True)
    lang = i18n.get_lang()
    m = _modele(lang)
    if not m:
        st.info(T("bcl_absent") if "bcl_absent" in i18n.DICO else "—")
        return

    if entete:
        st.title(T("mode_levier"))

    cle = f"sc_ecran_{lang}"
    page = int(st.session_state.get(cle, 0))

    # --- les commandes, une fois pour toutes, au-dessus de la pagination
    choix = sorted(m["ids"], key=lambda i_: m["noms"][i_])
    g, d = st.columns([1.4, 1], gap="large")
    with g:
        source = st.selectbox(T("sc_quoi"), choix,
                              index=choix.index("elec") if "elec" in choix else 0,
                              format_func=lambda i_: m["noms"][i_],
                              key=f"sc_src_{lang}")
    with d:
        delta = st.slider(T("sc_combien"), -3.0, 3.0, 2.0, 0.5,
                          key=f"sc_delta_{lang}")

    if not m["sortants"].get(source):
        st.info(T("sc_rien"))
        return
    if abs(delta) < 1e-9:
        st.info(T("sc_nul"))
        return

    total, tours, reste = _propager(m, source, delta)
    lignes = _tableau(m, total, tours, source, calcule_seulement=True)

    # LE SOMMAIRE DES ÉCRANS. Quand rien ne bouge assez pour être listé, les
    # deux écrans qui expliquent un chiffre n'ont plus d'objet : on les retire
    # plutôt que d'afficher deux pages vides que le lecteur devra tourner.
    titres = [T("sc_liste_t"), T("sc_deg_t")]
    if lignes:
        titres += [T("sc_pourquoi_t"), T("sc_bareme_t")]
    page = max(0, min(page, len(titres) - 1))

    with st.container(key=f"sc_ecran_{lang}_{page}"):
        if page == 0:
            _ecran_liste(m, total, tours, source, delta, lignes)
        elif page == 1:
            _ecran_degres()
        elif page == 2:
            _ecran_pourquoi(m, total, tours, reste, source, delta, lignes,
                            lang)
        else:
            _ecran_forces(m)

    _pied(page, titres, cle)


def _ecran_liste(m, total, tours, source, delta, lignes):
    """Écran 1 — ce qui bouge, et de combien."""
    st.markdown(f'<div class="sc-h">{_e(T("sc_titre"))}</div>'
                f'<p class="sc-x">{_e(T("sc_intro"))}</p>',
                unsafe_allow_html=True)
    st.caption(T("sc_pose", n=m["noms"][source], d=_f(delta, 1, True)))
    _tableau(m, total, tours, source)
    st.markdown(f'<p class="sc-x" style="margin-top:8px">'
                f'{_e(T("sc_liste_x", k=len(lignes), n=len(m["ids"])))}</p>',
                unsafe_allow_html=True)


def _ecran_degres():
    """Écran 2 — ce que valent les degrés, et pourquoi ces seuils."""
    st.markdown(f'<div class="sc-h">{_e(T("sc_deg_t"))}</div>'
                f'<p class="sc-x">{_e(T("sc_deg_x"))}</p>',
                unsafe_allow_html=True)
    _legende_degres()


def _ecran_pourquoi(m, total, tours, reste, source, delta, lignes, lang):
    """Écran 3 — d'où vient un chiffre : les tours, la chaîne, la source."""
    st.markdown(f'<div class="sc-h">{_e(T("sc_pourquoi_t"))}</div>',
                unsafe_allow_html=True)
    cibles = [x["id"] for x in lignes]
    cible = st.selectbox(T("sc_cible"), cibles,
                         format_func=lambda i_: m["noms"][i_],
                         key=f"sc_cible_{lang}_{source}")
    i = m["idx"][cible]

    st.markdown(f'<div class="sc-lab">{_e(T("sc_tours_t"))}</div>'
                f'<p class="sc-x">{_e(T("sc_tours_x"))}</p>',
                unsafe_allow_html=True)
    _tours(m, total, tours, reste, i)

    st.markdown(f'<div class="sc-lab">{_e(T("sc_chemin_t"))}</div>',
                unsafe_allow_html=True)
    meilleur = _chemins(m, source, cible)
    if meilleur["chemin"]:
        _chaine(m, meilleur["chemin"], meilleur["produit"], delta,
                float(total[i]))
    else:
        st.markdown(f'<p class="sc-x">{_e(T("sc_aucun"))}</p>',
                    unsafe_allow_html=True)


def _ecran_forces(m):
    """Écran 4 — comment les liens ont été vérifiés, et ce que vaut le tout."""
    pr = m["preuves"]
    if pr:
        st.markdown(
            f'<div class="sc-h">{_e(T("sc_preuves_t"))}</div>'
            f'<p class="sc-x">{_e(T("sc_preuves_x", t=len(m["aretes"]), v=pr.get("n_verifiees"), s=pr.get("n_sans_source"), c=pr.get("n_contestees")))}</p>',
            unsafe_allow_html=True)

    st.markdown(f'<div class="sc-h">{_e(T("sc_bareme_t"))}</div>'
                f'<p class="sc-x">{_e(T("sc_bareme_x"))}</p>',
                unsafe_allow_html=True)
    _bareme(m)

    st.markdown(f'<div class="sc-h">{_e(T("sc_mise_t"))}</div>'
                f'<p class="sc-x">{_e(T("sc_mise_x", r=_f(m["diag"]["rayon"], 2), f=_f(m["diag"]["facteur"], 2)))}</p>',
                unsafe_allow_html=True)
