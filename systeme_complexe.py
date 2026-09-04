"""Les boucles de rétroaction, en cinq écrans qui sont un seul parcours.

CE QU'EST « UN SYSTÈME » ICI, ET POURQUOI IL A DEUX COORDONNÉES.
Un système complexe n'est pas seulement un morceau de graphe : c'est un
morceau de graphe REGARDÉ SUR UNE POPULATION. « L'accès à l'éducation » n'est
pas une question ; « l'accès à l'éducation pour les femmes » en est une, et
« les latrines en montagne » en est une autre. Le graphe des relations ne
change pas d'une population à l'autre — ce qui change, c'est l'état de départ
de chaque variable, donc le point d'où part toute simulation.

Un système se définit donc par trois choses, et une seule fois :

    · la variable centrale — celle que les résultats ont désignée comme
      critique ;
    · la population regardée — l'ensemble, un sexe, une tranche d'âge, une
      catégorie économique, un paysage, une section communale ;
    · la profondeur — jusqu'à combien de relations de distance on va.

Ces trois choses sont retenues, et les cinq onglets travaillent dessus. Le
premier le construit, le deuxième justifie ses relations, le troisième cherche
où appuyer, le quatrième appuie, le cinquième regarde ce que ça fait vague
après vague. Refaire la sélection à chaque onglet en ferait cinq outils
séparés ; c'est un seul.

CE QUE LE MODULE NE FAIT PAS, ET LE DIT.
Il ne présente jamais une corrélation comme une preuve de causalité. Les
corrélations calculables ici le sont sur dix sections communales : c'est un
indice, pas un test, et le seuil au-delà duquel une corrélation sur dix points
cesse d'être du hasard est écrit à côté d'elle. Là où l'une des deux variables
n'est pas mesurée, il est dit que la corrélation n'est pas calculable — plutôt
que d'afficher un chiffre qui n'existe pas.
"""

import math

import numpy as np
import streamlit as st

import boucles_moteur as M
import i18n
from i18n import T

ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"
VERT_APRI, VERT, ROUGE, GRIS = "#2a6b3f", "#1a8a4f", "#c33a24", "#8a93a5"
AMBRE, BLEU = "#c9821f", "#2f6f9f"

# Les populations sur lesquelles un système peut être regardé. Ce sont
# exactement les colonnes de `scores_corriges` : rien n'est inventé, et une
# population absente du référentiel n'est pas proposée.
POPULATIONS = [
    ("Total", "sx_p_total"), ("Femme", "femmes"), ("Homme", "hommes"),
    ("<25", "age_25"), ("25-39", "age_25_39"), ("40-59", "age_40_59"),
    ("60+", "age_60"), ("Cat A", "cat_a"), ("Cat B", "cat_b"),
    ("Cat C", "cat_c"), ("Littoral", "pay_Littoral"),
    ("Montagne", "pay_Montagne"),
]
SECTIONS = M.SECTIONS

# UNE CORRÉLATION SUR DIX POINTS N'EST PAS UN TEST. Valeur critique du rho de
# Spearman à n = 10, bilatéral, 5 % : au-dessous, la corrélation ne se
# distingue pas du hasard. Elle est écrite à côté de chaque coefficient plutôt
# que laissée à deviner.
RHO_CRITIQUE_10 = 0.648
# Au-delà de ce nombre de nœuds, un schéma de boucle causale cesse d'être
# lisible : on le dit et on propose de réduire la profondeur.
NOEUDS_LISIBLES = 26

TEXTES = {
    "sx_p_total": {"en": "Everyone", "fr": "Tout le monde"},
    "sx_sec": {"en": "Communal section", "fr": "Section communale"},

    # ---------------------------------------------------- onglet 1
    "sx_o1": {"en": "Build a Causal System",
              "fr": "Construire un système causal"},
    "sx_o2": {"en": "Explore Relationships",
              "fr": "Explorer les relations"},
    "sx_o3": {"en": "Identify Key Levers",
              "fr": "Identifier les leviers"},
    "sx_o4": {"en": "Test Interventions",
              "fr": "Tester des interventions"},
    "sx_o5": {"en": "See System-Wide Impacts",
              "fr": "Voir les impacts sur tout le système"},
    "sx_c_rel": {"en": "Relation", "fr": "Relation"},
    "sx_c_src": {"en": "Where the strength comes from",
                 "fr": "D'où vient la force"},
    "sx_c_accord": {"en": "Reading", "fr": "Lecture"},
    "sx_o6": {"en": "Run the System Live",
              "fr": "Faire tourner le système en direct"},
    "sx_centre": {"en": "Central variable", "fr": "Variable centrale"},
    "sx_prof": {"en": "Depth", "fr": "Profondeur"},
    "sx_prof_x": {
        "en": "Depth 1 keeps only what touches the central variable "
              "directly. Each further step adds the variables that touch "
              "those, and the system stops being a star and starts being a "
              "system: that is where the loops appear.",
        "fr": "La profondeur 1 ne garde que ce qui touche directement la "
              "variable centrale. Chaque pas de plus ajoute ce qui touche "
              "celles-là, et le schéma cesse d'être une étoile pour devenir "
              "un système : c'est là que les boucles apparaissent."},
    "sx_non_mesure": {"en": "not measured", "fr": "non mesurée"},
    "sx_non_mesure_x": {
        "en": "This variable carries no measured score: it exists in the "
              "model as a mechanism, not as a result. It can be pushed in a "
              "simulation, but it has no baseline to compare against.",
        "fr": "Cette variable ne porte aucun score mesuré : elle existe dans "
              "le modèle comme mécanisme, pas comme résultat. Elle peut être "
              "poussée dans une simulation, mais elle n'a pas d'état de "
              "départ auquel se comparer."},
    "sx_compte": {
        "en": "{n} variables and {a} relations at depth {p}, of the {tn} "
              "variables and {ta} relations of the whole model.",
        "fr": "{n} variables et {a} relations à la profondeur {p}, sur les "
              "{tn} variables et {ta} relations du modèle entier."},
    "sx_trop": {
        "en": "At this depth the diagram carries {n} variables and stops "
              "being readable. It is drawn anyway; reduce the depth to read "
              "it.",
        "fr": "À cette profondeur le schéma porte {n} variables et cesse "
              "d'être lisible. Il est tout de même dessiné ; réduisez la "
              "profondeur pour le lire."},
    "sx_boucles_c": {"en": "The loops running through the central variable",
                     "fr": "Les boucles qui passent par la variable centrale"},
    "sx_boucles_0": {
        "en": "No loop runs through this variable at this depth: what "
              "happens to it does not come back to it. Either it is an entry "
              "point of the system, or the depth is too short.",
        "fr": "Aucune boucle ne passe par cette variable à cette profondeur : "
              "ce qui lui arrive ne lui revient pas. Ou bien elle est une "
              "entrée du système, ou bien la profondeur est trop courte."},
    "sx_r": {"en": "Reinforcing", "fr": "Renforçante"},
    "sx_b": {"en": "Balancing", "fr": "Équilibrante"},
    "sx_r_x": {
        "en": "A reinforcing loop amplifies what enters it — in both "
              "directions: it makes a gain grow and it makes a collapse "
              "deepen. A balancing loop pushes back towards where it was.",
        "fr": "Une boucle renforçante amplifie ce qui y entre — dans les deux "
              "sens : elle fait grandir un gain et elle creuse un "
              "effondrement. Une boucle équilibrante ramène vers le point de "
              "départ."},
    "sx_legende": {
        "en": "An arrow means: when the first variable rises, the second "
              "tends to rise (+, green) or to fall (−, red), everything else "
              "held equal.",
        "fr": "Une flèche se lit : quand la première variable monte, la "
              "seconde tend à monter (+, vert) ou à baisser (−, rouge), "
              "toutes choses égales par ailleurs."},

    # ---------------------------------------------------- onglet 2
    "sx_t2": {"en": "Every relation of the system, and what backs it",
              "fr": "Chaque relation du système, et ce qui la fonde"},
    "sx_x2": {
        "en": "The observed correlation, the strength posed in the model, and "
              "the source that strength comes from. A correlation is never a "
              "proof of causation.",
        "fr": "La corrélation observée, la force posée dans le modèle, et la "
              "source d'où sort cette force. Une corrélation n'est jamais une "
              "preuve de causalité."},
    "sx_rel": {"en": "Relation", "fr": "Relation"},
    "sx_correl": {"en": "Correlation across the 10 sections",
                  "fr": "Corrélation sur les 10 sections"},
    "sx_correl_non": {"en": "not computable", "fr": "non calculable"},
    "sx_correl_x": {
        "en": "Spearman rank correlation across the ten communal sections. "
              "Ten points is very few: below |ρ| = {c} a correlation cannot "
              "be told apart from chance at the 5 % level. It says whether "
              "the two measurements move together across the territory — "
              "never which one moves the other.",
        "fr": "Corrélation des rangs de Spearman sur les dix sections "
              "communales. Dix points, c'est très peu : sous |ρ| = {c} une "
              "corrélation ne se distingue pas du hasard au seuil de 5 %. "
              "Elle dit si les deux mesures évoluent ensemble à travers le "
              "territoire — jamais laquelle déplace l'autre."},
    "sx_faible": {"en": "below the threshold", "fr": "sous le seuil"},
    "sx_accord": {"en": "same direction as the model",
                  "fr": "même sens que le modèle"},
    "sx_desaccord": {"en": "opposite direction to the model",
                     "fr": "sens opposé au modèle"},
    "sx_preuve": {"en": "Level of evidence", "fr": "Niveau de preuve"},
    "sx_force": {"en": "Strength in the model", "fr": "Force dans le modèle"},
    "sx_reserve": {"en": "Reservation", "fr": "Réserve"},
    "sx_conteste": {
        "en": "Part of the literature contradicts the direction used here.",
        "fr": "Une partie de la littérature contredit le sens retenu ici."},
    "sx_filtre_p": {"en": "Keep only", "fr": "Ne garder que"},
    "sx_p_toutes": {"en": "All levels of evidence",
                    "fr": "Tous les niveaux de preuve"},
    "sx_rel_0": {"en": "No relation in this system matches the filter.",
                 "fr": "Aucune relation de ce système ne passe le filtre."},
    "sx_bilan_p": {
        "en": "{e} empirical · {d} documented · {s} structural · {t} "
              "theoretical · {h} hypothesis — and {c} contested.",
        "fr": "{e} empiriques · {d} documentées · {s} structurelles · {t} "
              "théoriques · {h} hypothèses — et {c} contestées."},

    # ---------------------------------------------------- onglet 3
    "sx_t3": {"en": "Where to push, and which loops carry the push",
              "fr": "Où appuyer, et quelles boucles portent l'appui"},
    "sx_x3": {
        "en": "The most connected variable is not automatically the best "
              "lever. What matters is how much of the system actually moves "
              "when the variable moves — which is a propagation, not a "
              "degree count. The two are shown together, because a variable "
              "that scores high on both is a lever worth arguing for.",
        "fr": "La variable la plus connectée n'est pas automatiquement le "
              "meilleur levier. Ce qui compte est la part du système qui "
              "bouge réellement quand elle bouge — et c'est une propagation, "
              "pas un compte de flèches. Les deux sont montrés ensemble, "
              "parce qu'une variable haute sur les deux est un levier qu'on "
              "peut défendre."},
    "sx_col_var": {"en": "Variable", "fr": "Variable"},
    "sx_col_deg": {"en": "Connections", "fr": "Connexions"},
    "sx_col_bcl": {"en": "Loops", "fr": "Boucles"},
    "sx_col_porte": {"en": "Reach of a +1 push",
                     "fr": "Portée d'une poussée de +1"},
    "sx_col_porte_x": {
        "en": "The total movement a one-point push on this variable produces "
              "everywhere else, in points out of 10 added up across all the "
              "variables it reaches. It is the propagation the model "
              "computes, not a count of arrows.",
        "fr": "Le mouvement total qu'une poussée d'un point sur cette "
              "variable produit partout ailleurs, en points sur 10 "
              "additionnés sur toutes les variables atteintes. C'est la "
              "propagation calculée par le modèle, pas un compte de flèches."},
    "sx_bascule": {"en": "pivot", "fr": "bascule"},
    "sx_bascule_x": {
        "en": "A pivot sits in reinforcing and balancing loops at once: "
              "pushed one way it runs away, pushed the other it is absorbed. "
              "It is the most useful place to act and the least forgiving.",
        "fr": "Une bascule est à la fois dans des boucles renforçantes et "
              "équilibrantes : poussée d'un côté elle s'emballe, de l'autre "
              "elle est absorbée. C'est l'endroit le plus utile où agir, et "
              "le moins indulgent."},
    "sx_dom": {"en": "The relations that carry the most loops",
               "fr": "Les relations qui portent le plus de boucles"},
    "sx_dom_x": {
        "en": "These arrows belong to the greatest number of loops at once: "
              "cut one and several loops stop turning together. They are the "
              "structural joints of the system.",
        "fr": "Ces flèches appartiennent au plus grand nombre de boucles à la "
              "fois : en couper une arrête plusieurs boucles ensemble. Ce "
              "sont les articulations du système."},
    "sx_dom_n": {"en": "in {n} loops — {r} reinforcing, {b} balancing",
                 "fr": "dans {n} boucles — {r} renforçantes, {b} "
                       "équilibrantes"},

    # ---------------------------------------------------- onglet 4
    "sx_t4": {"en": "Push several variables at once, and see the system move",
              "fr": "Pousser plusieurs variables à la fois, et voir le "
                    "système bouger"},
    "sx_x4": {
        "en": "The pushes add up: the central variable and any lever can be "
              "moved together, which is what a real intervention does. What "
              "is drawn is the difference between where the system starts and "
              "where it settles once every relation has been followed to the "
              "end.",
        "fr": "Les poussées se cumulent : la variable centrale et n'importe "
              "quel levier peuvent être déplacés ensemble, ce qui est "
              "exactement ce que fait une intervention réelle. Ce qui est "
              "dessiné est l'écart entre le point de départ du système et "
              "celui où il se pose une fois toutes les relations suivies "
              "jusqu'au bout."},
    "sx_pousser": {"en": "Variables to push", "fr": "Variables à pousser"},
    "sx_pousser_0": {
        "en": "Pick at least one variable to push. Nothing is simulated until "
              "you do.",
        "fr": "Choisissez au moins une variable à pousser. Rien n'est simulé "
              "avant."},
    "sx_remise": {"en": "Reset the scenario", "fr": "Remettre le scénario à zéro"},
    "sx_dep": {"en": "Baseline", "fr": "Départ"},
    "sx_pousse": {"en": "Push", "fr": "Poussée"},
    "sx_indirect": {"en": "Indirect", "fr": "Indirect"},
    "sx_arrivee": {"en": "New balance", "fr": "Nouvel équilibre"},
    "sx_col_eff": {"en": "Total effect", "fr": "Effet total"},
    "sx_rien_bouge": {
        "en": "Nothing else in the system moves by more than {s} points: "
              "this push does not travel.",
        "fr": "Rien d'autre dans le système ne bouge de plus de {s} points : "
              "cette poussée ne voyage pas."},
    "sx_indice": {"en": "Effect on the overall resilience index",
                  "fr": "Effet sur l'indice de résilience global"},
    "sx_couvert": {
        "en": "The model reaches {p} % of the weight of the index; the rest "
              "of the indicators are outside the causal graph and do not "
              "move.",
        "fr": "Le modèle atteint {p} % du poids de l'indice ; les autres "
              "indicateurs sont hors du graphe causal et ne bougent pas."},
    "sx_borne": {
        "en": "Scores are held between 0 and 10: a variable already at 9 "
              "cannot gain three points, and the table shows what it can "
              "actually gain.",
        "fr": "Les scores sont tenus entre 0 et 10 : une variable déjà à 9 ne "
              "peut pas gagner trois points, et le tableau montre ce qu'elle "
              "peut réellement gagner."},

    # ---------------------------------------------------- onglet 5
    "sx_t5": {"en": "Wave after wave, and what the loops add",
              "fr": "Vague après vague, et ce que les boucles ajoutent"},
    "sx_x5": {
        "en": "An intervention does not stop at what it touches. The first "
              "wave is what the pushed variables move directly; the second is "
              "what those move in turn; and a variable that sits in a "
              "reinforcing loop keeps receiving on every later wave, because "
              "the effect comes back to it. The columns below separate those "
              "waves instead of showing one lump.",
        "fr": "Une intervention ne s'arrête pas à ce qu'elle touche. La "
              "première vague est ce que les variables poussées déplacent "
              "directement ; la deuxième est ce que celles-là déplacent à "
              "leur tour ; et une variable prise dans une boucle renforçante "
              "continue de recevoir à chaque vague suivante, parce que "
              "l'effet lui revient. Les colonnes ci-dessous séparent ces "
              "vagues au lieu d'en montrer la somme."},
    "sx_v_dep": {"en": "Start", "fr": "Départ"},
    "sx_v_pousse": {"en": "Pushed by", "fr": "Poussée de"},
    "sx_v1": {"en": "Wave 1", "fr": "Vague 1"},
    "sx_v2": {"en": "Wave 2", "fr": "Vague 2"},
    "sx_v3": {"en": "Waves 3+", "fr": "Vagues 3+"},
    "sx_v_tot": {"en": "Cumulative", "fr": "Cumulé"},
    "sx_v_sens": {"en": "Direction", "fr": "Sens"},
    "sx_v_par": {"en": "Mainly through", "fr": "Principalement par"},
    "sx_hausse": {"en": "up", "fr": "hausse"},
    "sx_baisse": {"en": "down", "fr": "baisse"},
    "sx_nul": {"en": "flat", "fr": "nul"},
    "sx_conv": {
        "en": "Waves stop being counted when the whole wave moves less than "
              "{s} points, or after {k} waves — whichever comes first. "
              "Without such a rule a reinforcing loop would go round for "
              "ever, and the number printed would depend on when the "
              "computation was stopped rather than on the system.",
        "fr": "Les vagues cessent d'être comptées quand la vague entière "
              "déplace moins de {s} points, ou après {k} vagues — le premier "
              "des deux. Sans cette règle une boucle renforçante tournerait "
              "indéfiniment, et le chiffre affiché dépendrait du moment où "
              "l'on a arrêté le calcul plutôt que du système."},
    "sx_conv_fait": {
        "en": "Converged after {k} waves: the following waves together move "
              "less than {s} points.",
        "fr": "Convergé après {k} vagues : les vagues suivantes déplacent "
              "ensemble moins de {s} points."},
    "sx_conv_non": {
        "en": "Still moving after {k} waves. The model is scaled down so it "
              "converges; read the cumulative column as an order of "
              "magnitude, not as a forecast.",
        "fr": "Bouge encore après {k} vagues. Le modèle est mis à l'échelle "
              "pour converger ; lisez la colonne cumulée comme un ordre de "
              "grandeur, pas comme une prévision."},
    "sx_echelle": {
        "en": "The relation strengths are scaled by {f} so that the "
              "propagation converges: as written, the graph amplifies "
              "(spectral radius {r}). Every number here carries that scaling, "
              "and it is stated rather than hidden.",
        "fr": "Les forces des relations sont multipliées par {f} pour que la "
              "propagation converge : telles qu'elles sont écrites, le graphe "
              "amplifie (rayon spectral {r}). Tous les chiffres portent cette "
              "mise à l'échelle, et elle est dite plutôt que cachée."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)

STYLE = """
<style>
  .sx-lab { font-size:10.5px; font-weight:700; letter-spacing:.09em;
       text-transform:uppercase; color:#8a93a5; margin:10px 0 2px; }
  .sx-note { font-size:11.5px; color:#8a93a5; line-height:1.55;
       margin:8px 0 0; text-align:left !important; max-width:98ch; }
  .sx-tab { width:100%; border-collapse:collapse; margin-top:12px; }
  .sx-tab th { font-size:10.5px; font-weight:700; letter-spacing:.09em;
       text-transform:uppercase; color:#8a93a5; text-align:left;
       padding:0 9px 7px 0; border-bottom:1px solid #e9eef4; }
  .sx-tab th.n, .sx-tab td.n { text-align:right;
       font-variant-numeric:tabular-nums; }
  .sx-tab td { font-size:12.5px; color:#3c4761; padding:7px 9px 7px 0;
       border-bottom:1px solid #f2f5f9; vertical-align:top; }
  .sx-tab td.v { font-weight:700; color:#101728; }
  .sx-kpi { display:flex; gap:14px; flex-wrap:wrap; margin:6px 0 10px; }
  .sx-k { flex:1 1 170px; background:#fff; border:1px solid #e3eaf3;
       border-radius:12px; padding:12px 15px; }
  .sx-k-l { font-size:10.5px; font-weight:700; letter-spacing:.08em;
       text-transform:uppercase; color:#8a93a5; }
  .sx-k-v { font-size:23px; font-weight:700; color:#101728; line-height:1.1;
       margin-top:4px; font-variant-numeric:tabular-nums; }
  .sx-k-s { font-size:11px; color:#8a93a5; margin-top:3px; }
  .sx-carte { border:1px solid #e3eaf3; border-radius:12px; padding:13px 16px;
       margin:9px 0; background:#fff; }
  .sx-badge { display:inline-block; font-size:10px; font-weight:700;
       letter-spacing:.06em; text-transform:uppercase; border-radius:20px;
       padding:1px 9px; margin-right:7px; white-space:nowrap; }
  .sx-chem { font-size:12px; color:#3c4761; line-height:1.7; }
  .sx-fl { color:#8a93a5; padding:0 4px; }
</style>
"""


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _f(v, dec=2, signe=False):
    if v is None:
        return "—"
    s = f"{v:+.{dec}f}" if signe else f"{v:.{dec}f}"
    return s.replace(".", ",") if i18n.get_lang() == "fr" else s


def _nom(n):
    lang = i18n.get_lang()
    return n.get(lang) or n.get("fr") or n.get("en") or n["id"]


@st.cache_data(show_spinner=False)
def _modele(lang):
    """Le graphe, sa matrice mise à l'échelle, ses boucles et le référentiel.

    TOUT EST CALCULÉ UNE FOIS POUR LES CINQ ONGLETS. L'énumération des cycles
    est la seule opération coûteuse du module ; la refaire à chaque onglet
    ferait payer cinq fois le même travail pour le même résultat.
    """
    import json
    import os
    g = M.charger()
    A, ids, idx = M.matrice(g)
    noms = {n["id"]: _nom(n) for n in g["noeuds"]}
    par_id = {n["id"]: n for n in g["noeuds"]}
    aretes = {(a["de"], a["vers"]): a for a in g["aretes"]}
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data",
                     "resultats.json")
    res = []
    try:
        with open(p, encoding="utf-8") as f:
            res = json.load(f)
        res = res["indicateurs"] if isinstance(res, dict) else res
    except Exception:
        res = []
    par_ligne = {r["ligne"]: r for r in res}
    lst = M.boucles(g)
    return {"g": g, "A": A, "ids": ids, "idx": idx, "noms": noms,
            "par_id": par_id, "aretes": aretes, "par_ligne": par_ligne,
            "boucles": lst, "diag": M.diagnostic(g),
            "leviers": M.leviers(g, lst)}


# ============================================================ l'état partagé
def _systeme(m, cle):
    """Les trois coordonnées du système, retenues d'un onglet à l'autre.

    LE CHOIX SE FAIT UNE FOIS. Les cinq onglets lisent la même clé de session ;
    changer la variable centrale dans le premier la change partout, et c'est
    ce qui fait de la section un parcours et non cinq outils.
    """
    ids = sorted(m["ids"], key=lambda i: m["noms"][i])
    centre = st.session_state.get("bcl_centre")
    if centre not in ids:
        centre = ids[0]
        st.session_state["bcl_centre"] = centre
    pop = st.session_state.get("bcl_pop", "Total")
    if pop not in [p for p, _l in POPULATIONS] + list(SECTIONS):
        pop = "Total"
    if "bcl_prof" not in st.session_state:
        # LA PROFONDEUR 2 EST LE DÉFAUT, ET C'EST UN CHOIX DE FOND : à la
        # profondeur 1 un système n'a jamais de boucle — une étoile ne boucle
        # pas — et la section s'ouvrirait donc sur « aucune boucle ».
        st.session_state["bcl_prof"] = 2
    prof = int(st.session_state["bcl_prof"])
    return {"centre": centre, "pop": pop, "prof": prof, "ids": ids}


def _rappel(m, s):
    """Le bandeau qui redit, sur chaque onglet, quel système on regarde.

    LA POPULATION N'Y FIGURE PLUS, puisqu'elle ne se choisit plus : rappeler
    « échantillon complet » sur chaque onglet ne rappelait rien.
    """
    st.markdown(
        f'<p class="sx-note" style="margin:0 0 10px"><b>'
        f'{_e(m["noms"][s["centre"]])}</b> · '
        f'{_e(T("sx_prof"))} {s["prof"]}</p>', unsafe_allow_html=True)


def _voisinage(m, centre, prof):
    """Les nœuds à `prof` relations ou moins du centre, et leur rang.

    ON REMONTE ET ON DESCEND. Un système autour de la déforestation qui ne
    garderait que ce que la déforestation influence laisserait dehors ce qui
    la cause — et c'est précisément là qu'on veut intervenir. Les deux sens
    comptent donc pour la distance.
    """
    voisins = {}
    for (de, vers) in m["aretes"]:
        voisins.setdefault(de, set()).add(vers)
        voisins.setdefault(vers, set()).add(de)
    rang = {centre: 0}
    front = [centre]
    for r in range(1, prof + 1):
        suiv = []
        for x in front:
            for y in voisins.get(x, ()):
                if y not in rang:
                    rang[y] = r
                    suiv.append(y)
        front = suiv
    dedans = set(rang)
    aretes = [a for (de, vers), a in m["aretes"].items()
              if de in dedans and vers in dedans]
    return rang, aretes


def _boucles_de(m, centre, dedans=None):
    """Les boucles passant par le centre, entièrement contenues dans le
    système si un périmètre est donné."""
    out = []
    for b in m["boucles"]:
        if centre not in b["noeuds"]:
            continue
        if dedans is not None and not set(b["noeuds"]) <= dedans:
            continue
        out.append(b)
    return out


# ============================================================ le schéma (CLD)
def _positions(rang, centre):
    """Une couronne par rang : le centre au milieu, les autres autour.

    LE RANG EST UNE DISTANCE, ET LE DESSIN LE DIT. Un placement par force
    donnerait un joli nuage où l'on ne sait plus ce qui touche le centre ; des
    couronnes rendent la profondeur lisible d'un coup d'œil — première
    couronne : ce qui le touche ; deuxième : ce qui touche celles-là.
    """
    LARG, HAUT = 1120, 700
    cx, cy = LARG / 2, HAUT / 2
    rayons = {0: 0, 1: 150, 2: 268, 3: 340}
    pos = {centre: (cx, cy)}
    for r in sorted({v for v in rang.values() if v > 0}):
        cases = sorted([n for n, v in rang.items() if v == r])
        R = rayons.get(r, 340 + 40 * (r - 3))
        # Un décalage d'un demi-pas par couronne évite que les nœuds du rang 2
        # se cachent derrière ceux du rang 1 sur le même rayon.
        d = math.pi / max(len(cases), 1) if r % 2 == 0 else 0
        for i, n in enumerate(cases):
            a = 2 * math.pi * i / max(len(cases), 1) - math.pi / 2 + d
            pos[n] = (cx + R * math.cos(a) * 1.42, cy + R * math.sin(a))
    return pos, LARG, HAUT


def _svg_cld(m, rang, aretes, centre, boucle=None):
    """Le schéma de boucle causale : flèches signées, boucle isolée en gras."""
    pos, LARG, HAUT = _positions(rang, centre)
    en_boucle = set()
    if boucle:
        n = boucle["noeuds"]
        en_boucle = {(n[i], n[(i + 1) % len(n)]) for i in range(len(n))}
    parts = []
    for a in aretes:
        de, vers = a["de"], a["vers"]
        if de not in pos or vers not in pos:
            continue
        x1, y1 = pos[de]
        x2, y2 = pos[vers]
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy) or 1
        # On s'arrête au bord de la pastille, sinon la flèche se perd dessous.
        rx, ry = 40 / d, 22 / d
        x1b, y1b = x1 + dx * rx, y1 + dy * ry
        x2b, y2b = x2 - dx * rx, y2 - dy * ry
        mx, my = (x1b + x2b) / 2 - dy * 0.09, (y1b + y2b) / 2 + dx * 0.09
        vif = (de, vers) in en_boucle
        coul = VERT if a["signe"] > 0 else ROUGE
        op = 1 if (vif or not boucle) else 0.16
        ep = 2.6 if vif else (0.8 + 1.9 * float(a.get("force") or 0.5))
        parts.append(
            f'<path d="M{x1b:.0f},{y1b:.0f} Q{mx:.0f},{my:.0f} '
            f'{x2b:.0f},{y2b:.0f}" fill="none" stroke="{coul}" '
            f'stroke-width="{ep:.1f}" opacity="{op}" '
            f'marker-end="url(#f{"v" if a["signe"] > 0 else "r"})"/>'
            f'<text x="{mx:.0f}" y="{my:.0f}" font-size="13" '
            f'font-weight="700" fill="{coul}" opacity="{op}" '
            f'text-anchor="middle">{"+" if a["signe"] > 0 else "−"}</text>')
    for n, (x, y) in pos.items():
        r = rang.get(n, 9)
        est_c = n == centre
        dans = (not boucle) or (n in (boucle["noeuds"] if boucle else []))
        op = 1 if dans else 0.3
        fond = VERT_APRI if est_c else ("#eef3f0" if r == 1 else "#f4f6f9")
        encre = "#fff" if est_c else ENCRE
        lib = m["noms"].get(n, n)
        mots, ligne, lignes = lib.split(), "", []
        for w in mots:
            if len(ligne + " " + w) > 17 and ligne:
                lignes.append(ligne)
                ligne = w
            else:
                ligne = (ligne + " " + w).strip()
        lignes.append(ligne)
        lignes = lignes[:3]
        h = 15 + 13 * len(lignes)
        parts.append(
            f'<rect x="{x - 76:.0f}" y="{y - h / 2:.0f}" width="152" '
            f'height="{h}" rx="9" fill="{fond}" stroke="'
            f'{VERT_APRI if est_c else "#dbe3ec"}" opacity="{op}"/>')
        y0 = y - h / 2 + 15
        for i, l in enumerate(lignes):
            parts.append(
                f'<text x="{x:.0f}" y="{y0 + i * 13:.0f}" font-size="10.5" '
                f'text-anchor="middle" fill="{encre}" opacity="{op}" '
                f'font-weight="{700 if est_c else 400}">{_e(l)}</text>')
    fleches = (
        f'<defs>'
        f'<marker id="fv" viewBox="0 0 10 10" refX="9" refY="5" '
        f'markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
        f'<path d="M0,1 L9,5 L0,9 z" fill="{VERT}"/></marker>'
        f'<marker id="fr" viewBox="0 0 10 10" refX="9" refY="5" '
        f'markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
        f'<path d="M0,1 L9,5 L0,9 z" fill="{ROUGE}"/></marker></defs>')
    # LA BOÎTE ÉPOUSE LE CONTENU, ELLE N'EST PAS FIXE. À la profondeur 1 un
    # système tient dans quatre pastilles ; une boîte taillée pour trente
    # laissait six cents pixels de blanc autour d'elles, et il fallait faire
    # défiler pour trouver la suite de la page.
    xs = [x for x, _y in pos.values()]
    ys = [y for _x, y in pos.values()]
    x0, x1 = min(xs) - 96, max(xs) + 96
    y0, y1 = min(ys) - 42, max(ys) + 42
    larg, haut = max(x1 - x0, 320), max(y1 - y0, 200)
    return (f'<svg viewBox="{x0:.0f} {y0:.0f} {larg:.0f} {haut:.0f}" '
            f'width="100%" style="max-width:{min(larg, LARG):.0f}px;'
            f'display:block;margin:4px auto" '
            f'role="img" font-family="Inter,system-ui,sans-serif">'
            + fleches + "".join(parts) + '</svg>')


def _lib_boucle(m, b):
    """Le libellé d'une boucle : son type, sa longueur, son chemin abrégé."""
    tete = T("sx_r") if b["type"] == "renforcante" else T("sx_b")
    chemin = " → ".join(m["noms"].get(x, x) for x in b["noeuds"][:4])
    return f'{tete} · {b["n"]} · {chemin}' + (" …" if b["n"] > 4 else "")


# ================================================================= onglet 1
def render_construire():
    m = _modele(i18n.get_lang())
    st.markdown(STYLE, unsafe_allow_html=True)
    # NI TITRE NI CHAPEAU : l'onglet du haut dit déjà où l'on est, et la
    # phrase d'introduction expliquait surtout le menu de population qui vient
    # d'être retiré.
    s = _systeme(m, "c")

    # LE CHOIX DE POPULATION A ÉTÉ RETIRÉ D'ICI. Le graphe causal est le même
    # pour tout le monde — ce sont ses états qui changent d'un groupe à
    # l'autre, et cette lecture-là se fait dans les écrans d'écarts, qui
    # savent croiser deux registres et écarter les effectifs trop minces. Un
    # menu de plus au-dessus du système laissait croire que la structure des
    # causes se redessinait par sexe ou par section, ce qui n'est pas le cas.
    # `_systeme` retombe sur « Total », qui était déjà son défaut.
    c1, c3 = st.columns([2.4, 0.8])
    with c1:
        st.selectbox(T("sx_centre"), s["ids"], key="bcl_centre",
                     format_func=lambda i: m["noms"][i])
    with c3:
        st.selectbox(T("sx_prof"), [1, 2, 3], key="bcl_prof")
    s = _systeme(m, "c")

    etat = M.etat_courant(m["g"], m["par_ligne"], s["pop"])
    v = etat.get(s["centre"])
    rang, aretes = _voisinage(m, s["centre"], s["prof"])
    bcls = _boucles_de(m, s["centre"], set(rang))

    # LES TROIS COMPTEURS SONT PARTIS. Le score de départ, la taille du
    # périmètre et le décompte des boucles répétaient en chiffres ce que le
    # schéma montre déjà — et le schéma est ce qu'on vient voir. Le score
    # manquant continue d'être signalé, lui, parce qu'il change la lecture du
    # dessin.
    if v is None:
        st.info(T("sx_non_mesure_x"))

    isoler = None
    if bcls:
        choix = st.selectbox(
            T("sx_boucles_c"), [None] + list(range(len(bcls))),
            key="bcl_iso",
            format_func=lambda i: "—" if i is None else _lib_boucle(m, bcls[i]))
        isoler = bcls[choix] if choix is not None else None

    if len(rang) > NOEUDS_LISIBLES:
        st.warning(T("sx_trop", n=len(rang)))
    st.markdown(_svg_cld(m, rang, aretes, s["centre"], isoler),
                unsafe_allow_html=True)
    compte = T("sx_compte", n=len(rang), a=len(aretes), p=s["prof"],
               tn=len(m["ids"]), ta=len(m["aretes"]))
    st.markdown(f'<p class="sx-note">{_e(T("sx_legende"))}</p>'
                f'<p class="sx-note">{_e(T("sx_prof_x"))}</p>'
                f'<p class="sx-note">{_e(compte)}</p>',
                unsafe_allow_html=True)
    if not bcls:
        st.info(T("sx_boucles_0"))
    else:
        st.markdown(f'<p class="sx-note">{_e(T("sx_r_x"))}</p>',
                    unsafe_allow_html=True)


# ================================================================= onglet 2
def _spearman(xs, ys):
    """Le rho de Spearman, rangs moyens sur les ex æquo."""
    def rangs(v):
        ordre = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(ordre):
            j = i
            while j + 1 < len(ordre) and v[ordre[j + 1]] == v[ordre[i]]:
                j += 1
            moy = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[ordre[k]] = moy
            i = j + 1
        return r
    a, b = np.array(rangs(xs)), np.array(rangs(ys))
    if a.std() == 0 or b.std() == 0:
        return None
    return float(np.corrcoef(a, b)[0, 1])


def _correlation(m, n1, n2):
    """La corrélation des deux variables à travers les dix sections.

    ELLE SE CALCULE SUR LES VALEURS BRUTES, PAS SUR LES SCORES. Les scores
    sont des classes entières de 0 à 10 : deux sections séparées de quinze
    points de pourcentage peuvent tomber dans la même classe, et la
    corrélation des classes écrase justement ce qu'on cherche à voir.

    ELLE EST ORIENTÉE DANS LE SENS DE LA RÉSILIENCE. Un indicateur dont la
    valeur haute vaut un mauvais score — la part de ménages en insécurité
    alimentaire — est retourné avant le calcul : sans cela, deux variables qui
    vont ensemble dans le bon sens sortiraient anticorrélées, pour une raison
    de convention d'écriture et non de terrain.
    """
    l1 = (m["par_id"].get(n1) or {}).get("ligne")
    l2 = (m["par_id"].get(n2) or {}).get("ligne")
    r1, r2 = m["par_ligne"].get(l1), m["par_ligne"].get(l2)
    if not r1 or not r2:
        return None
    v1, v2 = r1.get("valeurs") or {}, r2.get("valeurs") or {}
    xs, ys = [], []
    for sec in SECTIONS:
        a, b = v1.get(sec), v2.get(sec)
        if a is None or b is None:
            continue
        xs.append(float(a))
        ys.append(float(b))
    if len(xs) < 8:
        return None
    rho = _spearman(xs, ys)
    if rho is None:
        return None
    for r, s in ((r1, xs), (r2, ys)):
        if "bas" in str(r.get("sens") or "").lower().split("=")[-1]:
            rho = -rho
    return {"rho": rho, "n": len(xs)}


def _classe(m, a):
    j = a.get("just") or "hypothese"
    for c in (m["g"].get("bareme") or {}).get("classes", []):
        if c.get("cle") == j:
            return c.get(i18n.get_lang()) or c.get("fr") or j
    return j


def _classe_courte(m, a):
    """« Empirique », et non la phrase entière qui la définit.

    La définition de la classe est la même sur les vingt-trois lignes : la
    répéter en pleine largeur, c'est vingt-trois fois la même phrase à lire.
    Le mot suffit dans une colonne ; la définition reste dans le menu de
    filtre, où elle sert à choisir.
    """
    return _classe(m, a).split(" — ")[0].split(" - ")[0].strip()


def _table_relations(m, aretes, lang):
    """Une ligne par relation : sa corrélation, sa force, d'où sort le nombre.

    UN TABLEAU PLUTÔT QU'UNE PILE DE FICHES. Chaque relation occupait une
    carte de six lignes — mécanisme, réserve, citation — et il fallait faire
    défiler vingt-trois cartes pour comparer deux coefficients. Ce qui se
    compare se met en colonnes ; le mécanisme et la réserve, eux, ne se
    comparent pas : ils restent attachés à la ligne, en infobulle, pour qui
    conteste un chiffre précis.
    """
    r = [f'<table class="sx-tab"><thead><tr>'
         f'<th>{_e(T("sx_c_rel"))}</th>'
         f'<th class="n">{_e(T("sx_correl"))}</th>'
         f'<th>{_e(T("sx_c_accord"))}</th>'
         f'<th class="n">{_e(T("sx_force"))}</th>'
         f'<th>{_e(T("sx_preuve"))}</th>'
         f'<th>{_e(T("sx_c_src"))}</th></tr></thead><tbody>']
    for a in aretes:
        co = _correlation(m, a["de"], a["vers"])
        if co is None:
            rho, n_co, mot, coul = "—", "", T("sx_correl_non"), GRIS
        else:
            fort = abs(co["rho"]) >= RHO_CRITIQUE_10
            meme = (co["rho"] > 0) == (a["signe"] > 0)
            rho = _f(co["rho"], 2)
            n_co = f' <span style="color:{GRIS};font-size:11px">'\
                   f'n&nbsp;=&nbsp;{co["n"]}</span>'
            mot = (T("sx_accord") if meme else T("sx_desaccord")) if fort \
                else T("sx_faible")
            coul = (ENCRE if meme else ROUGE) if fort else GRIS
        fleche = "→" if a["signe"] > 0 else "⊣"
        coul_f = VERT if a["signe"] > 0 else ROUGE
        src = a.get("src") or {}
        url = src.get("url")
        cite = a.get(f"cite_{lang}") or a.get("cite_fr") or "—"
        ref = a.get(f"ref_{lang}") or a.get("ref_fr") or ""
        res = a.get(f"reserve_{lang}") or a.get("reserve_fr") or ""
        bulle = " · ".join(x for x in (ref, res) if x)
        lien = (f' <a href="{_e(url)}" target="_blank" '
                f'style="color:{BLEU};text-decoration:none">↗</a>'
                if url else "")
        alerte = (f' <span style="color:{ROUGE}" title="'
                  f'{_e(T("sx_conteste"))}">⚠</span>'
                  if a.get("conteste") else "")
        r.append(
            f'<tr title="{_e(bulle)}">'
            f'<td class="v" style="min-width:230px;text-align:left">'
            f'{_e(m["noms"].get(a["de"], a["de"]))} '
            f'<span style="color:{coul_f};font-weight:700">{fleche}</span> '
            f'{_e(m["noms"].get(a["vers"], a["vers"]))}{alerte}</td>'
            f'<td class="n" style="color:{coul};font-weight:700;'
            f'white-space:nowrap">{rho}{n_co}</td>'
            f'<td style="color:{coul};font-size:11.5px;'
            f'text-align:left;white-space:nowrap">{_e(mot)}</td>'
            f'<td class="n v">{_f(a.get("force"), 2)}</td>'
            f'<td style="font-size:11.5px;text-align:left">'
            f'{_e(_classe_courte(m, a))}</td>'
            f'<td style="font-size:11px;color:{GRIS};line-height:1.45;'
            f'text-align:left;max-width:330px" title="{_e(cite)}">'
            f'<span style="display:-webkit-box;-webkit-line-clamp:2;'
            f'-webkit-box-orient:vertical;overflow:hidden">{_e(cite)}</span>'
            f'{lien}</td></tr>')
    r.append("</tbody></table>")
    return "".join(r)


def render_relations():
    m = _modele(i18n.get_lang())
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown(f'<div class="titre-bloc">{_e(T("sx_t2"))}</div>',
                unsafe_allow_html=True)
    s = _systeme(m, "r")
    _rappel(m, s)
    st.markdown(f'<p class="sx-note" style="margin:0 0 8px">'
                f'{_e(T("sx_x2"))}</p>', unsafe_allow_html=True)

    rang, aretes = _voisinage(m, s["centre"], s["prof"])
    classes = sorted({a.get("just") or "hypothese" for a in aretes})
    lib_c = {c: _classe(m, {"just": c}) for c in classes}
    choix = st.multiselect(T("sx_filtre_p"), classes, default=classes,
                           key="sx_f_preuve",
                           format_func=lambda c: lib_c[c])
    gardees = [a for a in aretes
               if (a.get("just") or "hypothese") in choix]
    cpt = {c: sum(1 for a in aretes if (a.get("just") or "hypothese") == c)
           for c in ("empirique", "documentee", "structurel", "theorique",
                     "hypothese")}
    bilan = T("sx_bilan_p", e=cpt["empirique"], d=cpt["documentee"],
              s=cpt["structurel"], t=cpt["theorique"], h=cpt["hypothese"],
              c=sum(1 for a in aretes if a.get("conteste")))
    st.markdown(f'<p class="sx-note" style="margin:2px 0 0">{_e(bilan)}</p>',
                unsafe_allow_html=True)
    if not gardees:
        st.info(T("sx_rel_0"))
        return

    lang = i18n.get_lang()
    # Les relations touchant le centre d'abord : c'est autour d'elles que la
    # discussion se tient.
    gardees.sort(key=lambda a: (s["centre"] not in (a["de"], a["vers"]),
                                -(a.get("force") or 0)))
    st.markdown(_table_relations(m, gardees, lang), unsafe_allow_html=True)
    st.markdown(f'<p class="sx-note">'
                f'{_e(T("sx_correl_x", c=_f(RHO_CRITIQUE_10, 2)))}</p>',
                unsafe_allow_html=True)


# ================================================================= onglet 3
def render_leviers():
    m = _modele(i18n.get_lang())
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown(f'<div class="titre-bloc">{_e(T("sx_t3"))}</div>',
                unsafe_allow_html=True)
    s = _systeme(m, "l")
    _rappel(m, s)
    st.markdown(f'<p class="sx-note" style="margin:0 0 6px">'
                f'{_e(T("sx_x3"))}</p>', unsafe_allow_html=True)

    rang, _a = _voisinage(m, s["centre"], s["prof"])
    dedans = set(rang)
    # LA PORTÉE EST UNE PROPAGATION, PAS UN DEGRÉ. C'est le seul chiffre qui
    # répond à « si je bouge ça, qu'est-ce qui bouge » ; le degré répond à
    # « combien de flèches y a-t-il », ce qui n'est pas la même question.
    lignes = []
    for lv in m["leviers"]:
        if lv["id"] not in dedans:
            continue
        eff = M.propager(m["g"], {lv["id"]: 1.0})
        portee = sum(abs(v) for k, v in eff.items() if k != lv["id"])
        lignes.append({**lv, "portee": portee,
                       "nom": m["noms"].get(lv["id"], lv["id"])})
    if not lignes:
        st.info(T("sx_boucles_0"))
        return
    lignes.sort(key=lambda x: -x["portee"])

    r = ['<table class="sx-tab"><thead><tr>'
         f'<th>{_e(T("sx_col_var"))}</th>'
         f'<th class="n">{_e(T("sx_col_porte"))}</th>'
         f'<th class="n">{_e(T("sx_col_deg"))}</th>'
         f'<th class="n">{_e(T("sx_col_bcl"))}</th>'
         '</tr></thead><tbody>']
    for x in lignes[:14]:
        bas = (f' <span class="sx-badge" style="color:{AMBRE};'
               f'border:1px solid {AMBRE}55">{_e(T("sx_bascule"))}</span>'
               if x.get("bascule") else "")
        r.append(f'<tr><td>{_e(x["nom"])}{bas}</td>'
                 f'<td class="n v">{_f(x["portee"], 2)}</td>'
                 f'<td class="n">{x["degre"]}</td>'
                 f'<td class="n">{x["boucles"]} '
                 f'<span style="color:{GRIS}">({x["renforcantes"]}R / '
                 f'{x["equilibrantes"]}B)</span></td></tr>')
    r.append('</tbody></table>')
    st.markdown("".join(r), unsafe_allow_html=True)
    st.markdown(f'<p class="sx-note">{_e(T("sx_col_porte_x"))}</p>'
                f'<p class="sx-note">{_e(T("sx_bascule_x"))}</p>',
                unsafe_allow_html=True)

    dom = [d for d in M.boucles_dominantes(m["g"], m["boucles"], top=8)
           if d["de"] in dedans and d["vers"] in dedans]
    if dom:
        st.markdown(f'<div class="titre-bloc" style="margin-top:22px">'
                    f'{_e(T("sx_dom"))}</div>'
                    f'<p class="sx-note" style="margin:0 0 6px">'
                    f'{_e(T("sx_dom_x"))}</p>', unsafe_allow_html=True)
        for d in dom:
            a = m["aretes"].get((d["de"], d["vers"])) or {}
            coul = VERT if (a.get("signe", 1) > 0) else ROUGE
            fl = "→" if a.get("signe", 1) > 0 else "⊣"
            st.markdown(
                f'<div class="sx-carte" style="padding:9px 14px">'
                f'<span style="font-size:12.5px;color:{ENCRE}">'
                f'{_e(m["noms"].get(d["de"], d["de"]))} '
                f'<b style="color:{coul}">{fl}</b> '
                f'{_e(m["noms"].get(d["vers"], d["vers"]))}</span>'
                f'<span style="float:right;font-size:11.5px;color:{GRIS}">'
                f'{_e(T("sx_dom_n", n=d["n"], r=d["renf"], b=d["equi"]))}'
                f'</span></div>', unsafe_allow_html=True)


# ================================================================= onglet 4
def _scenario(m, s, dedans):
    """Les poussées posées par l'utilisateur, cumulables et remises à zéro.

    ELLES S'ADDITIONNENT, ET C'EST TOUT L'INTÉRÊT. Une intervention réelle ne
    pousse pas une variable : elle en pousse trois, et l'effet de l'ensemble
    n'est pas la somme des effets pris un à un dès qu'une boucle relie deux
    d'entre elles. C'est exactement ce que le calcul fait ici.
    """
    dispo = sorted(dedans, key=lambda i: m["noms"][i])
    # LA REMISE À ZÉRO SE FAIT ICI, AVANT LE WIDGET, ET NON DANS LE BOUTON.
    # Streamlit refuse qu'on écrive la clé d'un widget déjà dessiné dans le
    # même passage : le bouton, qui vient après le menu, ne peut donc que
    # poser un drapeau et relancer la page — c'est au tour suivant, avant que
    # le menu ne renaisse, que les choix se vident.
    if st.session_state.pop("sx_raz_demande", False):
        for k in [x for x in st.session_state if str(x).startswith("sx_d_")]:
            del st.session_state[k]
        st.session_state["sx_pousse_v"] = []
    # UNE VARIABLE SORTIE DU PÉRIMÈTRE NE PEUT PAS RESTER SÉLECTIONNÉE. En
    # réduisant la profondeur, on rétrécit la liste des options ; une valeur
    # retenue qui n'y figure plus fait tomber le menu. On la retire d'abord.
    if "sx_pousse_v" in st.session_state:
        garde = [x for x in st.session_state["sx_pousse_v"] if x in dispo]
        if garde != list(st.session_state["sx_pousse_v"]):
            st.session_state["sx_pousse_v"] = garde
        opt = {}
    else:
        opt = {"default": [s["centre"]] if s["centre"] in dispo else []}
    choisies = st.multiselect(
        T("sx_pousser"), dispo, key="sx_pousse_v",
        format_func=lambda i: m["noms"][i], **opt)
    variations = {}
    if choisies:
        cols = st.columns(min(len(choisies), 3))
        for i, n in enumerate(choisies):
            with cols[i % len(cols)]:
                variations[n] = st.slider(
                    m["noms"][n], -3.0, 3.0,
                    float(st.session_state.get(f"sx_d_{n}", 1.0)), 0.5,
                    key=f"sx_d_{n}")
    return {k: v for k, v in variations.items() if abs(v) > 1e-9}


def render_simuler():
    m = _modele(i18n.get_lang())
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown(f'<div class="titre-bloc">{_e(T("sx_t4"))}</div>',
                unsafe_allow_html=True)
    s = _systeme(m, "s")
    _rappel(m, s)
    st.markdown(f'<p class="sx-note" style="margin:0 0 8px">'
                f'{_e(T("sx_x4"))}</p>', unsafe_allow_html=True)

    rang, _a = _voisinage(m, s["centre"], s["prof"])
    variations = _scenario(m, s, set(rang))
    if st.button(T("sx_remise"), key="sx_raz"):
        st.session_state["sx_raz_demande"] = True
        st.rerun()
    if not variations:
        st.info(T("sx_pousser_0"))
        return

    etat = M.etat_courant(m["g"], m["par_ligne"], s["pop"])
    effets = M.propager(m["g"], variations)
    arrivee = M.apres(etat, effets, variations)
    ind = M.effet_indice(m["g"], effets, variations, m["par_ligne"])

    resume = " · ".join(f'{m["noms"][k]} {_f(v, 1, True)}'
                        for k, v in variations.items())
    couvert = T("sx_couvert", p=round(100 * ind["part_couverte"]))
    st.markdown(
        '<div class="sx-kpi">'
        f'<div class="sx-k"><div class="sx-k-l">{_e(T("sx_indice"))}</div>'
        f'<div class="sx-k-v" style="color:'
        f'{VERT if ind["delta"] >= 0 else ROUGE}">'
        f'{_f(ind["delta"], 3, True)}</div>'
        f'<div class="sx-k-s">{_e(couvert)}</div></div>'
        f'<div class="sx-k"><div class="sx-k-l">{_e(T("sx_pousse"))}</div>'
        f'<div class="sx-k-v">{len(variations)}</div>'
        f'<div class="sx-k-s">{_e(resume[:80])}</div></div></div>',
        unsafe_allow_html=True)

    bouge = sorted(
        [(k, v) for k, v in effets.items()
         if k not in variations and abs(v) >= M.SEUIL_NUL],
        key=lambda kv: -abs(kv[1]))
    if not bouge:
        st.info(T("sx_rien_bouge", s=_f(M.SEUIL_NUL, 2)))
        return

    r = ['<table class="sx-tab"><thead><tr>'
         f'<th>{_e(T("sx_col_var"))}</th>'
         f'<th class="n">{_e(T("sx_dep"))}</th>'
         f'<th class="n">{_e(T("sx_pousse"))}</th>'
         f'<th class="n">{_e(T("sx_indirect"))}</th>'
         f'<th class="n">{_e(T("sx_arrivee"))}</th>'
         '</tr></thead><tbody>']
    for k, v in list(variations.items()) + bouge:
        d0 = etat.get(k)
        pousse = variations.get(k)
        ind_v = effets.get(k, 0.0)
        fin = arrivee.get(k)
        coul = VERT if (pousse or 0) + ind_v >= 0 else ROUGE
        r.append(f'<tr><td>{_e(m["noms"].get(k, k))}</td>'
                 f'<td class="n">{_f(d0, 1)}</td>'
                 f'<td class="n">{_f(pousse, 1, True) if pousse else "—"}</td>'
                 f'<td class="n" style="color:{coul}">'
                 f'{_f(ind_v, 2, True)}</td>'
                 f'<td class="n v">{_f(fin, 1)}</td></tr>')
    r.append('</tbody></table>')
    st.markdown("".join(r), unsafe_allow_html=True)
    st.markdown(f'<p class="sx-note">{_e(T("sx_borne"))}</p>',
                unsafe_allow_html=True)
    _note_echelle(m)


def _note_echelle(m):
    d = m["diag"]
    if d.get("facteur") and abs(d["facteur"] - 1) > 1e-6:
        note = T("sx_echelle", f=_f(d["facteur"], 3), r=_f(d["rayon"], 3))
        st.markdown(f'<p class="sx-note">{_e(note)}</p>',
                    unsafe_allow_html=True)


# ================================================================= onglet 5
VAGUES_MAX = 12
SEUIL_VAGUE = 0.01


def _vagues(m, variations):
    """La décomposition vague par vague, avec une règle d'arrêt écrite.

    LA RÈGLE D'ARRÊT EST LA MOITIÉ DU RÉSULTAT. Une boucle renforçante renvoie
    l'effet à son point de départ, qui le renvoie de nouveau : sans critère, on
    tourne indéfiniment et le chiffre affiché ne dit plus que le moment où l'on
    a arrêté de compter. On s'arrête donc quand une vague entière déplace moins
    de {SEUIL_VAGUE} point, ou à la douzième — et on dit lequel des deux est
    arrivé.

    LE TOTAL N'EST PAS LA SOMME DES VAGUES CALCULÉES : c'est la solution exacte
    de la série, obtenue en résolvant (I − A)·x = e₀. Les vagues servent à voir
    par où l'effet passe ; le total, lui, ne dépend d'aucune troncature.
    """
    A, ids, idx = m["A"], m["ids"], m["idx"]
    e0 = np.zeros(len(ids))
    for k, v in variations.items():
        if k in idx:
            e0[idx[k]] = v
    vagues, cour = [], e0.copy()
    converge, k_arret = False, VAGUES_MAX
    for k in range(VAGUES_MAX):
        cour = A @ cour
        vagues.append(cour.copy())
        if float(np.abs(cour).sum()) < SEUIL_VAGUE:
            converge, k_arret = True, k + 1
            break
    total = M.propager(m["g"], variations)
    return vagues, total, converge, k_arret


def _par_qui(m, cible, variations):
    """Les deux relations entrantes qui portent le plus de l'effet reçu."""
    A, idx, ids = m["A"], m["idx"], m["ids"]
    eff = M.propager(m["g"], variations)
    j = idx.get(cible)
    if j is None:
        return ""
    contribs = []
    for de, vers in m["aretes"]:
        if vers != cible or de not in idx:
            continue
        amont = eff.get(de, 0.0) + variations.get(de, 0.0)
        contribs.append((abs(A[j, idx[de]] * amont), de))
    contribs.sort(reverse=True)
    return ", ".join(m["noms"].get(d, d) for _v, d in contribs[:2])


def render_vagues():
    m = _modele(i18n.get_lang())
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown(f'<div class="titre-bloc">{_e(T("sx_t5"))}</div>',
                unsafe_allow_html=True)
    s = _systeme(m, "v")
    _rappel(m, s)
    st.markdown(f'<p class="sx-note" style="margin:0 0 8px">'
                f'{_e(T("sx_x5"))}</p>', unsafe_allow_html=True)

    # LE SCÉNARIO EST CELUI DE L'ONGLET PRÉCÉDENT. Le redemander ici ferait
    # deux scénarios pour une seule intervention, et le tableau récapitulatif
    # ne récapitulerait plus rien.
    rang, _a = _voisinage(m, s["centre"], s["prof"])
    variations = {}
    for n in st.session_state.get("sx_pousse_v", []) or []:
        v = st.session_state.get(f"sx_d_{n}")
        if v:
            variations[n] = float(v)
    if not variations:
        variations = {s["centre"]: 1.0}

    resume = " · ".join(f'{m["noms"].get(k, k)} {_f(v, 1, True)}'
                        for k, v in variations.items())
    st.markdown(f'<p class="sx-note" style="margin:0 0 6px"><b>'
                f'{_e(T("sx_pousse"))}</b> · {_e(resume)}</p>',
                unsafe_allow_html=True)

    vagues, total, converge, k = _vagues(m, variations)
    etat = M.etat_courant(m["g"], m["par_ligne"], s["pop"])
    idx = m["idx"]

    lignes = []
    for n in m["ids"]:
        j = idx[n]
        v1 = float(vagues[0][j]) if len(vagues) > 0 else 0.0
        v2 = float(vagues[1][j]) if len(vagues) > 1 else 0.0
        v3 = float(sum(v[j] for v in vagues[2:]))
        tot = float(total.get(n, 0.0))
        if n not in variations and abs(tot) < M.SEUIL_NUL:
            continue
        lignes.append({"id": n, "nom": m["noms"].get(n, n),
                       "dep": etat.get(n), "pousse": variations.get(n),
                       "v1": v1, "v2": v2, "v3": v3, "tot": tot})
    lignes.sort(key=lambda x: (x["id"] not in variations, -abs(x["tot"])))

    r = ['<table class="sx-tab"><thead><tr>'
         f'<th>{_e(T("sx_col_var"))}</th>'
         f'<th class="n">{_e(T("sx_v_dep"))}</th>'
         f'<th class="n">{_e(T("sx_v_pousse"))}</th>'
         f'<th class="n">{_e(T("sx_v1"))}</th>'
         f'<th class="n">{_e(T("sx_v2"))}</th>'
         f'<th class="n">{_e(T("sx_v3"))}</th>'
         f'<th class="n">{_e(T("sx_v_tot"))}</th>'
         f'<th>{_e(T("sx_v_sens"))}</th>'
         f'<th>{_e(T("sx_v_par"))}</th></tr></thead><tbody>']
    for x in lignes[:24]:
        sens = M.direction(x["tot"])
        coul = {"hausse": VERT, "baisse": ROUGE}.get(sens, GRIS)
        par = "" if x["id"] in variations else _par_qui(m, x["id"], variations)
        r.append(
            f'<tr><td>{_e(x["nom"])}</td>'
            f'<td class="n">{_f(x["dep"], 1)}</td>'
            f'<td class="n">'
            f'{_f(x["pousse"], 1, True) if x["pousse"] else "—"}</td>'
            f'<td class="n">{_f(x["v1"], 2, True)}</td>'
            f'<td class="n">{_f(x["v2"], 2, True)}</td>'
            f'<td class="n">{_f(x["v3"], 2, True)}</td>'
            f'<td class="n v" style="color:{coul}">'
            f'{_f(x["tot"], 2, True)}</td>'
            f'<td style="color:{coul};font-size:11.5px">'
            f'{_e(T("sx_" + sens))}</td>'
            f'<td style="color:{GRIS};font-size:11.5px">{_e(par)}</td></tr>')
    r.append('</tbody></table>')
    st.markdown("".join(r), unsafe_allow_html=True)

    fin = (T("sx_conv_fait", k=k, s=_f(SEUIL_VAGUE, 2)) if converge
           else T("sx_conv_non", k=VAGUES_MAX))
    regle = T("sx_conv", s=_f(SEUIL_VAGUE, 2), k=VAGUES_MAX)
    st.markdown(f'<p class="sx-note">{_e(fin)}</p>'
                f'<p class="sx-note">{_e(regle)}</p>',
                unsafe_allow_html=True)
    _note_echelle(m)
