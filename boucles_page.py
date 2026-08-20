"""Boucles de rétroaction — l'exploration systémique du cadre IRLA.

LE SECOND VOLET DU CADRE. L'indice composite cartographie les capacités ; il ne
dit pas comment elles s'entretiennent l'une l'autre. C'est le rôle de l'analyse
causale : poser les relations, les faire tourner, et regarder ce que le système
fait de lui-même. La page rend cela manipulable — on pousse un levier, on voit
où l'onde va.

CE QUE L'INTERFACE DOIT EMPÊCHER

Qu'on lise une simulation comme une prédiction. Trois dispositifs s'y emploient,
et aucun n'est une note de bas de page :

  · chaque relation porte son NIVEAU DE JUSTIFICATION — documentée, théorique,
    empirique, hypothèse de modélisation — visible au survol de la flèche et
    listé en clair dans le tableau des relations ;
  · l'ASSOCIATION RÉELLEMENT OBSERVÉE entre sections communales est affichée à
    côté de la relation du modèle, dans un registre séparé, y compris — surtout
    — quand elle la contredit. Quatre relations sur les dix-neuf testables
    s'observent avec le signe contraire, et la page le dit ;
  · les nœuds NON MESURÉS par l'enquête — l'état de santé, la capacité de
    travail — sont dessinés en tirets et ne reçoivent jamais de valeur de
    départ inventée.

LE CLIC SUR LE RÉSEAU passe par un paramètre d'URL plutôt que par un composant
sur mesure : chaque nœud est un lien `?levier=…` que Streamlit relit au
rechargement. C'est natif, court, et cela survit aux versions.
"""

import json
import math
import os

import streamlit as st
import streamlit.components.v1 as components

import boucles_moteur as M
import cadre_page
import i18n
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

# Diverging : deux pôles et un gris neutre au milieu — jamais un arc-en-ciel,
# jamais une teinte au point neutre. Les deux pôles sont pris dans la palette
# déjà validée du site.
HAUSSE, BAISSE, NUL = "#1a8a4f", "#c33a24", "#9aa4b5"
ALERTE = "#d1730c"
ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"

JUST_COULEUR = {"documentee": "#1a8a4f", "empirique": "#2166ac",
                "theorique": "#7048b6", "hypothese": "#d1730c"}

TEXTES = {
    "bcl_titre": {"en": "Feedback Loops", "fr": "Boucles de rétroaction"},
    "bcl_sous_titre": {
        "en": "Explore how the indicators hold each other up",
        "fr": "Explorer comment les indicateurs se tiennent les uns les autres"},
    "bcl_avertissement": {
        "en": "**These are exploratory scenarios, not predictions.** The "
              "relations below come from the IRLA framework and from the "
              "literature — they are not estimated on the survey. Moving a "
              "lever shows what the model implies, never what the territory "
              "will do. Observed associations between communal sections are "
              "shown separately, and four of them run against the model.",
        "fr": "**Ce sont des scénarios exploratoires, pas des prédictions.** "
              "Les relations ci-dessous viennent du cadre IRLA et de la "
              "littérature — elles ne sont pas estimées sur l'enquête. "
              "Déplacer un levier montre ce que le modèle implique, jamais ce "
              "que le territoire fera. Les associations observées entre "
              "sections communales sont montrées à part, et quatre d'entre "
              "elles vont contre le modèle."},
    # ---- le point de départ : les indicateurs les plus alarmants
    "bcl_alarme": {"en": "Start from the most alarming indicators",
                   "fr": "Partir des indicateurs les plus alarmants"},
    "bcl_alarme_note": {
        "en": "The lowest-scored lines of the framework, heaviest weight "
              "first. This is where the exploration should begin: a loop is "
              "worth following when it passes through what is actually "
              "failing. Click one to make it the lever.",
        "fr": "Les lignes du référentiel les plus basses, à pondération "
              "décroissante. C'est de là que l'exploration doit partir : une "
              "boucle mérite d'être suivie quand elle passe par ce qui est "
              "réellement en défaut. Cliquez-en une pour en faire le levier."},
    "bcl_alarme_hors": {
        "en": "Alarming and **outside the model** — the graph poses no "
              "relation for these, so no loop can reach them. They are named "
              "here rather than left out in silence:",
        "fr": "Alarmants et **hors du modèle** — le graphe ne pose aucune "
              "relation pour eux, aucune boucle ne peut donc les atteindre. "
              "Ils sont nommés ici plutôt que passés sous silence :"},
    "bcl_alarme_actif": {"en": "current lever", "fr": "levier actuel"},
    "bcl_poids_court": {"en": "weight", "fr": "pond."},
    "bcl_levier": {"en": "Lever — the indicator you act on",
                   "fr": "Levier — l'indicateur sur lequel on agit"},
    "bcl_variation": {"en": "Change applied, in points out of 10",
                      "fr": "Variation appliquée, en points sur 10"},
    "bcl_isoler": {"en": "Isolate a loop", "fr": "Isoler une boucle"},
    "bcl_aucune": {"en": "Show the whole network", "fr": "Voir tout le réseau"},
    "bcl_reseau": {"en": "The network", "fr": "Le réseau"},
    "bcl_reseau_note": {
        "en": "One node per indicator, one arrow per relation of the model. "
              "Dashed nodes are variables the survey does not measure — they "
              "carry the chain but have no score. Colour shows the simulated "
              "direction of change; the lever has a blue ring. Click a node to "
              "make it the lever.",
        "fr": "Un nœud par indicateur, une flèche par relation du modèle. Les "
              "nœuds en tirets sont des variables que l'enquête ne mesure "
              "pas — elles portent la chaîne mais n'ont pas de score. La "
              "couleur donne le sens du changement simulé ; le levier porte un "
              "anneau bleu. Cliquez un nœud pour en faire le levier."},
    "bcl_effets": {"en": "Simulated effects", "fr": "Effets simulés"},
    "bcl_effets_vide": {
        "en": "Move the slider to apply a change and see it propagate.",
        "fr": "Déplacez le curseur pour appliquer une variation et la voir se "
              "propager."},
    "bcl_col_ind": {"en": "Indicator", "fr": "Indicateur"},
    "bcl_col_avant": {"en": "Current", "fr": "Situation actuelle"},
    "bcl_col_apres": {"en": "Scenario", "fr": "Scénario simulé"},
    "bcl_col_delta": {"en": "Change", "fr": "Variation"},
    "bcl_non_mesure": {"en": "not measured", "fr": "non mesuré"},
    "bcl_indice": {"en": "Effect on the overall APRI score",
                   "fr": "Effet sur l'indice APRI d'ensemble"},
    "bcl_indice_note": {
        "en": "The graph covers {part} % of the scored framework by weight. "
              "The rest of the index does not move — no relation is posed for "
              "it, which is not the same as no relation existing.",
        "fr": "Le graphe couvre {part} % du poids du référentiel scoré. Le "
              "reste de l'indice ne bouge pas — aucune relation n'y est "
              "posée, ce qui n'est pas la même chose qu'une absence de "
              "relation."},
    "bcl_boucles": {"en": "The loops in the model",
                    "fr": "Les boucles du modèle"},
    "bcl_boucles_note": {
        "en": "A loop's sign is the product of the signs of its arrows: an "
              "even number of negative links makes it reinforcing, an odd "
              "number balancing. Strength is the product of the strengths — "
              "it decides how much the loop actually weighs.",
        "fr": "Le signe d'une boucle est le produit des signes de ses "
              "flèches : un nombre pair de liens négatifs la rend "
              "renforçante, un nombre impair l'équilibre. La force est le "
              "produit des forces — c'est elle qui décide du poids réel de la "
              "boucle."},
    "bcl_renforcante": {"en": "Reinforcing", "fr": "Renforçante"},
    "bcl_equilibrante": {"en": "Balancing", "fr": "Équilibrante"},
    "bcl_force": {"en": "strength", "fr": "force"},
    "bcl_relations": {"en": "Every relation, and what justifies it",
                      "fr": "Chaque relation, et ce qui la justifie"},
    "bcl_j_documentee": {"en": "Documented", "fr": "Documentée"},
    "bcl_j_documentee_x": {"en": "Established in the literature",
                           "fr": "Établie dans la littérature"},
    "bcl_j_theorique": {"en": "Theoretical", "fr": "Théorique"},
    "bcl_j_theorique_x": {"en": "Derived from the IRLA framework",
                          "fr": "Dérivée du cadre IRLA"},
    "bcl_j_empirique": {"en": "Empirical", "fr": "Empirique"},
    "bcl_j_empirique_x": {"en": "Supported by an observation in this survey",
                          "fr": "Appuyée par une observation de cette enquête"},
    "bcl_j_hypothese": {"en": "Modelling assumption",
                        "fr": "Hypothèse de modélisation"},
    "bcl_j_hypothese_x": {"en": "Posed by the model, to be discussed in "
                                "workshop",
                          "fr": "Posée par le modèle, à discuter en atelier"},
    "bcl_obs": {"en": "Observed between sections",
                "fr": "Observé entre sections"},
    "bcl_obs_note": {
        "en": "Spearman correlation of the two indicators' scores across the "
              "ten communal sections. TEN POINTS IS ALMOST NO STATISTICAL "
              "POWER: this column neither proves nor refutes a relation of "
              "the model. It never enters the simulation — it is there to be "
              "compared, and argued with.",
        "fr": "Corrélation de Spearman entre les scores des deux indicateurs "
              "sur les dix sections communales. DIX POINTS, C'EST PRESQUE "
              "AUCUNE PUISSANCE STATISTIQUE : cette colonne ne prouve ni ne "
              "réfute une relation du modèle. Elle n'entre jamais dans la "
              "simulation — elle est là pour être comparée, et discutée."},
    "bcl_desaccord": {
        "en": "Runs against the model — worth putting on the workshop table",
        "fr": "Va contre le modèle — à porter sur la table de l'atelier"},
    "bcl_desaccords_t": {
        "en": "{n} relations are observed with the opposite sign",
        "fr": "{n} relations s'observent avec le signe contraire"},
    "bcl_diag": {
        "en": "Model diagnostic — {noeuds} nodes, {aretes} relations, raw "
              "spectral radius {rayon}, rescaled to {cible}. Above 1 the "
              "system would run away; near 1 it is so heavily looped that a "
              "small change in one strength would tip it.",
        "fr": "Diagnostic du modèle — {noeuds} nœuds, {aretes} relations, "
              "rayon spectral brut {rayon}, ramené à {cible}. Au-dessus de 1 "
              "le système s'emballerait ; proche de 1 il est si fortement "
              "bouclé qu'une petite hausse de force le ferait basculer."},
    "bcl_polarite": {
        "en": "Polarity, Sterman's convention: **+** the two variables move "
              "the same way, **−** they move opposite ways. A loop with an "
              "even number of − links is reinforcing (R), an odd number "
              "balancing (B).",
        "fr": "Polarité, convention de Sterman : **+** les deux variables "
              "changent dans le même sens, **−** en sens opposé. Une boucle "
              "avec un nombre pair de liens − est renforçante (R), un nombre "
              "impair équilibrante (B)."},
    "bcl_sens_note": {
        "en": "**« Positive » does not mean « good ».** The same reinforcing "
              "loop is a virtuous spiral pushed upward (R+) and a vicious one "
              "pushed downward (R−). The sub-type below follows the direction "
              "of the change you applied.",
        "fr": "**« Positive » ne veut pas dire « bonne ».** La même boucle "
              "renforçante est une spirale vertueuse poussée à la hausse (R+) "
              "et vicieuse poussée à la baisse (R−). Le sous-type ci-dessous "
              "suit le sens de la variation que vous avez appliquée."},
    "bcl_leviers": {"en": "Where to act — structural levers",
                    "fr": "Où agir — les leviers structuraux"},
    "bcl_leviers_note": {
        "en": "Highly connected nodes that sit in many loops carry a "
              "multiplier effect. The decisive criterion is belonging to "
              "loops of OPPOSITE sign: such a node can tip the system from a "
              "degrading dynamic into a resilience one.",
        "fr": "Un nœud très connecté, présent dans beaucoup de boucles, a un "
              "effet multiplicateur. Le critère décisif est l'appartenance à "
              "des boucles de SENS OPPOSÉ : un tel nœud peut faire basculer "
              "le système d'une dynamique dégradante vers une dynamique de "
              "résilience."},
    "bcl_bascule": {"en": "tipping lever", "fr": "levier de basculement"},
    "bcl_col_degre": {"en": "Links", "fr": "Liens"},
    "bcl_col_boucles": {"en": "Loops (R / B)", "fr": "Boucles (R / B)"},
    "bcl_dominantes": {"en": "Dominant relations — where loops cross",
                       "fr": "Relations dominantes — là où les boucles se croisent"},
    "bcl_dominantes_note": {
        "en": "Acting on one of these relations touches several sub-systems "
              "at once. This is where to look for how to turn a degrading "
              "loop into a regulating one.",
        "fr": "Agir sur une de ces relations touche plusieurs sous-systèmes à "
              "la fois. C'est là qu'il faut chercher comment transformer une "
              "boucle dégradante en boucle régulatrice."},
    "bcl_dans": {"en": "in {n} loops", "fr": "dans {n} boucles"},
    "bcl_meadows": {"en": "Levels of intervention, after Meadows",
                    "fr": "Niveaux de levier, d'après Meadows"},
    "bcl_m1": {"en": "**Adjust a flow** — change a parameter directly: cut "
                     "household fuelwood use by introducing alternatives",
               "fr": "**Ajuster un flux** — modifier un paramètre : réduire "
                     "la consommation de bois par ménage en introduisant des "
                     "alternatives"},
    "bcl_m2": {"en": "**Break or strengthen a loop** — microcredit for clean "
                     "cooking equipment breaks the poverty–charcoal link",
               "fr": "**Casser ou renforcer une boucle** — un microcrédit "
                     "pour s'équiper en cuisson propre casse le lien "
                     "pauvreté–charbon"},
    "bcl_m3": {"en": "**Change the information flows** — monitoring, "
                     "participatory diagnosis, awareness campaigns",
               "fr": "**Modifier les flux d'information** — suivi, diagnostic "
                     "participatif, campagnes de sensibilisation"},
    "bcl_m4": {"en": "**Change the rules** — ban on burning, payments for "
                     "ecosystem services",
               "fr": "**Changer les règles** — interdiction du brûlis, "
                     "paiements pour services écosystémiques"},
    "bcl_boucles_top": {
        "en": "The {n} strongest loops of the {tot} the model contains, "
              "sorted by strength.",
        "fr": "Les {n} boucles les plus fortes des {tot} que contient le "
              "modèle, triées par force."},
    "bcl_echelle": {
        "en": "Forces are relative orders of magnitude, not measured "
              "amplitudes: they are rescaled by {facteur} so the system stays "
              "damped. Read the sign and the ranking of the affected "
              "indicators, not the number of points.",
        "fr": "Les forces sont des ordres de grandeur relatifs, pas des "
              "amplitudes mesurées : elles sont ramenées d'un facteur "
              "{facteur} pour que le système reste amorti. Lisez le sens et "
              "le classement des indicateurs touchés, pas le nombre de "
              "points."},
    "bcl_diverge": {
        "en": "The model no longer converges — a relation has been made too "
              "strong. The figures below are not usable.",
        "fr": "Le modèle ne converge plus — une relation a été rendue trop "
              "forte. Les chiffres ci-dessous ne sont pas exploitables."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _fmt(v, dec=1, signe=False):
    if v is None:
        return "—"
    s = f"{v:+.{dec}f}" if signe else f"{v:.{dec}f}"
    return s.replace(".", ",")


@st.cache_data(show_spinner=False)
def _charger():
    g = M.charger()
    p = os.path.join(DATA, "resultats.json")
    res = None
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            res = json.load(f)
        res = res["indicateurs"] if isinstance(res, dict) \
            and "indicateurs" in res else res
    return g, {r["ligne"]: r for r in (res or [])}


def _libelle(n):
    return n["fr"] if i18n.get_lang() == "fr" else n["en"]


def _nom_indic(r):
    if i18n.get_lang() == "fr" and r.get("indicateur_fr"):
        return r["indicateur_fr"]
    return r.get("indicateur", "")


def alarmants(graphe, par_ligne, combien=8):
    """Les indicateurs de résilience les plus alarmants, et lesquels le graphe
    sait atteindre.

    L'EXPLORATION DOIT PARTIR DE LÀ. Une boucle n'a d'intérêt que si elle passe
    par ce qui est réellement en défaut ; commencer par un levier confortable
    donne une jolie cascade et aucune décision. On classe donc les lignes
    scorées par score croissant, puis par pondération décroissante — à score
    égal, celle qui pèse le plus dans l'indice passe devant.

    Deux listes sont rendues, et la seconde compte autant que la première :
    les indicateurs alarmants que le graphe NE COUVRE PAS. Aucune boucle ne
    peut les atteindre, et le taire donnerait l'illusion que le modèle voit
    tout le territoire.
    """
    noeud_de = {n["ligne"]: n for n in graphe["noeuds"] if n.get("ligne")}
    lignes = []
    for lg, r in par_ligne.items():
        s = (r.get("scores_corriges") or {}).get("Total")
        if s is None:
            continue
        lignes.append({"ligne": lg, "r": r, "score": float(s),
                       "poids": r.get("ponderation") or 1,
                       "noeud": noeud_de.get(lg)})
    lignes.sort(key=lambda x: (x["score"], -x["poids"]))
    dedans = [x for x in lignes if x["noeud"]][:combien]
    plafond = dedans[-1]["score"] if dedans else 0
    dehors = [x for x in lignes if not x["noeud"] and x["score"] <= plafond]
    return dedans, dehors[:6]


def _ref(e):
    return e["ref_fr"] if i18n.get_lang() == "fr" else e["ref_en"]


# --------------------------------------------------------------- le réseau
LARGEUR, HAUTEUR = 1180, 660
COLONNES = ["dim1", "dim2", "dim3", "dim4", "dim5", "dim6"]


def _positions(graphe):
    """Une colonne par dimension, les nœuds empilés dedans.

    Un placement par force donnerait un joli nuage illisible : on ne saurait
    plus à quelle dimension appartient un nœud, qui est justement ce que le
    lecteur cherche. Les colonnes rendent la lecture prévisible — et le
    placement est déterministe, donc le schéma ne bouge pas d'un affichage à
    l'autre.
    """
    par_col = {c: [] for c in COLONNES}
    for n in graphe["noeuds"]:
        par_col.setdefault(n["dim"], []).append(n)
    pos, marge_x, marge_y = {}, 108, 54
    pas_x = (LARGEUR - 2 * marge_x) / (len(COLONNES) - 1)
    for i, col in enumerate(COLONNES):
        noeuds = par_col.get(col, [])
        if not noeuds:
            continue
        x = marge_x + i * pas_x
        haut = HAUTEUR - 2 * marge_y
        pas_y = haut / max(len(noeuds) - 1, 1) if len(noeuds) > 1 else 0
        depart = marge_y if len(noeuds) > 1 else HAUTEUR / 2
        for j, n in enumerate(noeuds):
            pos[n["id"]] = (x, depart + j * pas_y)
    return pos


def _svg(graphe, pos, effets, variations, levier, aretes_visibles):
    par_id = {n["id"]: n for n in graphe["noeuds"]}
    parts = [
        f'<svg viewBox="0 0 {LARGEUR} {HAUTEUR}" width="100%" '
        f'style="max-width:{LARGEUR}px;display:block;background:#fff" '
        f'font-family="Inter,system-ui,sans-serif">',
        '<defs>',
        '<marker id="fl" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M0 0 L10 5 L0 10 z" fill="#b6c0d0"/></marker>',
        '<marker id="fl-on" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M0 0 L10 5 L0 10 z" fill="#14508f"/></marker>',
        '</defs>']

    for e in graphe["aretes"]:
        if e["de"] not in pos or e["vers"] not in pos:
            continue
        actif = (e["de"], e["vers"]) in aretes_visibles if aretes_visibles \
            else True
        if aretes_visibles and not actif:
            continue
        x1, y1 = pos[e["de"]]
        x2, y2 = pos[e["vers"]]
        # Courbe : deux nœuds de la même colonne se relient par un arc, sinon
        # une bézière douce. Des droites se superposeraient à l'identique.
        dx, dy = x2 - x1, y2 - y1
        courbure = 0.22 if abs(dx) > 1 else 0.55
        cx = (x1 + x2) / 2 - dy * courbure
        cy = (y1 + y2) / 2 + dx * courbure
        coul = "#14508f" if aretes_visibles else "#ccd5e2"
        larg = 1.0 + 1.6 * e["force"]
        titre = (f'{_libelle(par_id[e["de"]])} → {_libelle(par_id[e["vers"]])}'
                 f'  ·  {T("bcl_j_" + e["just"])}'
                 f'  ·  {_ref(e)}')
        parts.append(
            f'<path d="M{x1:.1f},{y1:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}" '
            f'fill="none" stroke="{coul}" stroke-width="{larg:.1f}" '
            f'stroke-dasharray="{"5 4" if e["just"] == "hypothese" else ""}" '
            f'marker-end="url(#{"fl-on" if aretes_visibles else "fl"})" '
            f'opacity="{0.95 if aretes_visibles else 0.55}">'
            f'<title>{_e(titre)}</title></path>')
        # La POLARITÉ, convention de Sterman : le signe est posé au tiers de
        # la courbe, côté départ, là où l'œil suit la flèche. Sans lui, on ne
        # peut pas lire le sens d'une boucle — c'est le produit des signes qui
        # la classe.
        if aretes_visibles or e["signe"] < 0:
            px = 0.25 * x1 + 0.5 * cx + 0.25 * x2
            py = 0.25 * y1 + 0.5 * cy + 0.25 * y2
            pol = "+" if e["signe"] > 0 else "−"
            pc = "#14508f" if aretes_visibles else BAISSE
            parts.append(
                f'<circle cx="{px:.1f}" cy="{py:.1f}" r="7" fill="#fff" '
                f'stroke="{pc}" stroke-width="1.2" opacity=".95"/>'
                f'<text x="{px:.1f}" y="{py + 4:.1f}" text-anchor="middle" '
                f'font-size="12" font-weight="700" fill="{pc}">{pol}</text>')

    for n in graphe["noeuds"]:
        if n["id"] not in pos:
            continue
        if aretes_visibles and not any(n["id"] in a for a in aretes_visibles):
            continue
        x, y = pos[n["id"]]
        d = effets.get(n["id"], 0.0) + (variations or {}).get(n["id"], 0.0)
        sens = M.direction(d)
        fond = {"hausse": HAUSSE, "baisse": BAISSE, "nul": NUL}[sens]
        opac = 0.18 if sens == "nul" else min(0.30 + abs(d) / 4.0, 0.95)
        mesure = n.get("ligne") is not None
        r = 15 if mesure else 13
        lib = _libelle(n)
        titre = lib + (f' · L{n["ligne"]}' if mesure
                       else f' · {T("bcl_non_mesure")}')
        if abs(d) > M.SEUIL_NUL:
            titre += f'  ·  {_fmt(d, 2, True)}'
        parts.append(f'<a href="?levier={n["id"]}" target="_top">')
        parts.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fond}" '
            f'fill-opacity="{opac:.2f}" stroke="{fond}" stroke-width="2" '
            f'stroke-dasharray="{"" if mesure else "4 3"}">'
            f'<title>{_e(titre)}</title></circle>')
        if n["id"] == levier:
            parts.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r + 6}" fill="none" '
                f'stroke="#14508f" stroke-width="2.5"/>')
        if abs(d) > M.SEUIL_NUL:
            fleche = "↑" if d > 0 else "↓"
            parts.append(
                f'<text x="{x:.1f}" y="{y + 4.5:.1f}" text-anchor="middle" '
                f'font-size="14" font-weight="700" fill="{fond}">{fleche}</text>')
        # Le libellé est écrit à côté de chaque nœud : la couleur ne porte
        # jamais l'identité à elle seule.
        mots, ligne, lignes = lib.split(), "", []
        for m in mots:
            if len(ligne) + len(m) > 17:
                lignes.append(ligne)
                ligne = m
            else:
                ligne = (ligne + " " + m).strip()
        lignes.append(ligne)
        for k, ln in enumerate(lignes[:2]):
            parts.append(
                f'<text x="{x:.1f}" y="{y + r + 13 + k * 11:.1f}" '
                f'text-anchor="middle" font-size="9.5" fill="{ENCRE2}">'
                f'{_e(ln)}</text>')
        parts.append('</a>')

    parts.append('</svg>')
    return "".join(parts)


def _legende():
    items = [(HAUSSE, "↑", T("bcl_col_delta") + " +"), (BAISSE, "↓", "−"),
             (NUL, "→", "≈ 0")]
    puces = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:6px;'
        f'margin-right:16px"><span style="width:13px;height:13px;'
        f'border-radius:50%;background:{c};opacity:.45;border:2px solid {c}">'
        f'</span><span style="font-size:12px;color:{ENCRE2}">{f} {lab}</span>'
        f'</span>' for c, f, lab in items)
    return (f'<div style="margin:0 0 8px">{puces}'
            f'<span style="display:inline-flex;align-items:center;gap:6px">'
            f'<span style="width:13px;height:13px;border-radius:50%;'
            f'border:2px dashed {ENCRE3}"></span>'
            f'<span style="font-size:12px;color:{ENCRE2}">'
            f'{_e(T("bcl_non_mesure"))}</span></span></div>')


# ------------------------------------------------------------------- page
# Rechargement forcé : Streamlit Cloud avait gardé en mémoire la version
# précédente de ce module après le commit qui lui a donné son paramètre
# `entete`. Le script principal, lui, était à jour — il appelait donc
# `render(entete=False)` sur une fonction qui ne le connaissait pas. Un
# commit qui touche ce fichier relance le processus et rend les deux
# cohérents.
def render(entete=True):
    graphe, par_ligne = _charger()
    diag = M.diagnostic(graphe)
    par_id = {n["id"]: n for n in graphe["noeuds"]}

    if entete:
        st.markdown(
            f'<h2 style="font-size:27px;font-weight:700;color:{ENCRE};'
            f'letter-spacing:-.02em;margin:2px 0 0">{T("bcl_titre")}</h2>'
            f'<p style="font-size:12.5px;color:{ENCRE3};letter-spacing:.06em;'
            f'text-transform:uppercase;margin:2px 0 0;font-weight:600">'
            f'{T("bcl_sous_titre")}</p>', unsafe_allow_html=True)

    # L'avertissement est en tête, pas en pied : il conditionne la lecture de
    # tout ce qui suit.
    st.info(T("bcl_avertissement"))
    if not diag["converge"]:
        st.error(T("bcl_diverge"))

    # ---- le clic sur un nœud arrive par l'URL
    ids = [n["id"] for n in graphe["noeuds"]]
    clic = st.query_params.get("levier")
    if clic in ids:
        st.session_state["bcl_levier"] = clic
        del st.query_params["levier"]
    # ---- ON PART DES INDICATEURS LES PLUS ALARMANTS, pas d'un levier
    # confortable. Le bloc est rendu AVANT les contrôles, pour que le clic
    # puisse fixer le levier avant que le menu déroulant ne soit instancié.
    dedans, dehors = alarmants(graphe, par_ligne)
    st.session_state.setdefault(
        "bcl_levier", dedans[0]["noeud"]["id"] if dedans else "eau")
    if st.session_state["bcl_levier"] not in ids:
        st.session_state["bcl_levier"] = ids[0]

    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("bcl_alarme")}</div>',
                    unsafe_allow_html=True)
        st.caption(T("bcl_alarme_note"))
        cols = st.columns(4)
        for i, x in enumerate(dedans):
            with cols[i % 4]:
                actif = x["noeud"]["id"] == st.session_state["bcl_levier"]
                st.markdown(
                    f'<div style="font-size:11px;font-weight:800;'
                    f'color:{BAISSE if x["score"] <= 2 else ALERTE};'
                    f'font-variant-numeric:tabular-nums">'
                    f'{_fmt(x["score"], 0)}/10 '
                    f'<span style="color:{ENCRE3};font-weight:600">· L'
                    f'{x["ligne"]} · {_e(T("bcl_poids_court"))} '
                    f'{_fmt(x["poids"], 2)}</span></div>',
                    unsafe_allow_html=True)
                if st.button(_nom_indic(x["r"]), key=f"alarme_{x['ligne']}",
                             use_container_width=True,
                             type="primary" if actif else "secondary"):
                    st.session_state["bcl_levier"] = x["noeud"]["id"]
                    st.rerun()
        if dehors:
            st.markdown(
                T("bcl_alarme_hors") + " " + " · ".join(
                    f'L{x["ligne"]} {_nom_indic(x["r"])} '
                    f'({_fmt(x["score"], 0)}/10)' for x in dehors))

    mesures = [n for n in graphe["noeuds"] if n.get("ligne") is not None]
    c1, c2, c3 = st.columns([2.2, 2.2, 2])
    with c1:
        st.selectbox(T("bcl_levier"), [n["id"] for n in mesures],
                     format_func=lambda i: _libelle(par_id[i]),
                     key="bcl_levier")
    with c2:
        delta = st.slider(T("bcl_variation"), -3.0, 3.0, 1.0, 0.5,
                          key="bcl_delta")
    # Trente-huit boucles dans un menu déroulant seraient illisibles. On
    # propose les douze plus fortes — la force étant le produit des forces de
    # leurs arêtes, c'est bien celles qui pèsent — et on dit combien il y en a
    # en tout plutôt que de faire disparaître les autres en silence.
    toutes_boucles = M.boucles(graphe)
    lst_boucles = sorted(toutes_boucles, key=lambda b: -b["force"])[:12]
    with c3:
        choix = st.selectbox(
            T("bcl_isoler"), [-1] + list(range(len(lst_boucles))),
            format_func=lambda k: (
                T("bcl_aucune") if k < 0 else
                f'{T("bcl_" + lst_boucles[k]["type"])} · '
                + " → ".join(_libelle(par_id[x])
                             for x in lst_boucles[k]["noeuds"][:3]) + "…"),
            key="bcl_boucle")

    levier = st.session_state["bcl_levier"]
    variations = {levier: float(delta)}
    effets = M.propager(graphe, variations)
    etat = M.etat_courant(graphe, par_ligne)
    etat_ap = M.apres(etat, effets, variations)
    isolees = (M.aretes_de_boucle(lst_boucles[choix]) if choix >= 0 else None)

    # ------------------------------------------------------------ le réseau
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("bcl_reseau")}</div>',
                    unsafe_allow_html=True)
        st.caption(T("bcl_reseau_note"))
        st.markdown(T("bcl_polarite"))
        pos = _positions(graphe)
        components.html(
            '<div style="font-family:Inter,system-ui,sans-serif">'
            + _legende()
            + _svg(graphe, pos, effets, variations, levier, isolees)
            + '</div>', height=HAUTEUR + 66, scrolling=False)

    # ------------------------------------------------- effets et comparaison
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("bcl_effets")}</div>',
                    unsafe_allow_html=True)
        touches = sorted(
            ((k, effets.get(k, 0.0) + variations.get(k, 0.0))
             for k in ids
             if abs(effets.get(k, 0.0) + variations.get(k, 0.0)) > M.SEUIL_NUL),
            key=lambda x: -abs(x[1]))
        if not touches:
            st.caption(T("bcl_effets_vide"))
        else:
            lignes = [
                f'<div style="display:grid;grid-template-columns:'
                f'minmax(150px,3fr) 90px 90px 96px;gap:12px;padding:0 0 6px;'
                f'font-size:11px;letter-spacing:.09em;text-transform:uppercase;'
                f'color:#8a93a5;font-weight:700">'
                f'<div>{_e(T("bcl_col_ind"))}</div>'
                f'<div style="text-align:right">{_e(T("bcl_col_avant"))}</div>'
                f'<div style="text-align:right">{_e(T("bcl_col_apres"))}</div>'
                f'<div style="text-align:right">{_e(T("bcl_col_delta"))}</div>'
                f'</div>']
            for cle, d in touches:
                n = par_id[cle]
                coul = HAUSSE if d > 0 else BAISSE
                fl = "↑" if d > 0 else "↓"
                av = _fmt(etat.get(cle)) if etat.get(cle) is not None \
                    else f'<span style="color:{ENCRE3};font-size:12px">' \
                         f'{_e(T("bcl_non_mesure"))}</span>'
                ap = _fmt(etat_ap.get(cle)) if etat_ap.get(cle) is not None \
                    else "—"
                lignes.append(
                    f'<div style="display:grid;grid-template-columns:'
                    f'minmax(150px,3fr) 90px 90px 96px;gap:12px;'
                    f'align-items:center;padding:7px 0;'
                    f'border-bottom:1px solid #eef2f7">'
                    f'<div style="font-size:13.5px;color:{ENCRE};'
                    f'font-weight:600">{_e(_libelle(n))}'
                    + (f'<span style="color:{ENCRE3};font-weight:400"> · '
                       f'L{n["ligne"]}</span>' if n.get("ligne") else '')
                    + f'{" ◆" if cle == levier else ""}</div>'
                    f'<div style="text-align:right;font-size:13.5px;'
                    f'color:{ENCRE2};font-variant-numeric:tabular-nums">{av}</div>'
                    f'<div style="text-align:right;font-size:13.5px;'
                    f'font-weight:600;color:{ENCRE};'
                    f'font-variant-numeric:tabular-nums">{ap}</div>'
                    f'<div style="text-align:right;font-size:13.5px;'
                    f'font-weight:700;color:{coul};'
                    f'font-variant-numeric:tabular-nums">{fl} '
                    f'{_fmt(d, 2, True)}</div></div>')
            st.markdown("".join(lignes), unsafe_allow_html=True)

        ei = M.effet_indice(graphe, effets, variations, par_ligne)
        coul = HAUSSE if ei["delta"] > 0 else (BAISSE if ei["delta"] < 0
                                               else ENCRE3)
        st.markdown(
            f'<div style="display:flex;align-items:baseline;gap:12px;'
            f'margin-top:14px;padding-top:12px;border-top:1px solid #e3eaf3">'
            f'<div style="font-size:14px;font-weight:600;color:{ENCRE}">'
            f'{_e(T("bcl_indice"))}</div>'
            f'<div style="font-size:26px;font-weight:700;color:{coul};'
            f'font-variant-numeric:tabular-nums">'
            f'{_fmt(ei["delta"], 3, True)}</div>'
            f'<div style="font-size:13px;color:{ENCRE3}">/ 10</div></div>',
            unsafe_allow_html=True)
        st.caption(T("bcl_indice_note",
                     part=f'{100 * ei["part_couverte"]:.0f}'))
        st.caption(T("bcl_echelle", facteur=_fmt(diag["facteur"], 2)))

    # ------------------------------------------------------------ les boucles
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("bcl_boucles")}</div>',
                    unsafe_allow_html=True)
        st.caption(T("bcl_boucles_note"))
        st.caption(T("bcl_boucles_top", n=len(lst_boucles),
                     tot=len(toutes_boucles)))
        st.markdown(T("bcl_sens_note"))
        cartes = []
        for k, b in enumerate(lst_boucles):
            renf = b["type"] == "renforcante"
            c = HAUSSE if renf else "#d1730c"
            st_b = M.sous_type(b, delta)
            chemin = " → ".join(_libelle(par_id[x]) for x in b["noeuds"])
            chemin += " → " + _libelle(par_id[b["noeuds"][0]])
            cartes.append(
                f'<div style="border:1px solid #e3eaf3;border-left:4px solid '
                f'{c};border-radius:12px;padding:12px 15px;margin:9px 0;'
                f'background:{"#f7fbf8" if k == choix else "#fff"}">'
                f'<div style="display:flex;gap:10px;align-items:baseline;'
                f'flex-wrap:wrap">'
                f'<span style="display:inline-flex;align-items:center;'
                f'justify-content:center;width:26px;height:20px;'
                f'border-radius:6px;background:{c};color:#fff;font-size:11.5px;'
                f'font-weight:700">{_e(st_b)}</span>'
                f'<span style="font-size:12px;font-weight:700;color:{c};'
                f'letter-spacing:.05em;text-transform:uppercase">'
                f'{_e(T("bcl_" + b["type"]))}</span>'
                f'<span style="font-size:12px;color:{ENCRE3}">'
                f'{b["n"]} · {_e(T("bcl_force"))} {_fmt(b["force"], 2)}</span>'
                f'</div>'
                f'<div style="font-size:13.5px;color:{ENCRE2};line-height:1.55;'
                f'margin-top:5px">{_e(chemin)}</div></div>')
        st.markdown("".join(cartes), unsafe_allow_html=True)

    # ------------------------------------------------------- où agir
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("bcl_leviers")}</div>',
                    unsafe_allow_html=True)
        st.caption(T("bcl_leviers_note"))
        lv = [x for x in M.leviers(graphe, toutes_boucles)
              if x["boucles"] > 0][:8]
        lignes = [
            f'<div style="display:grid;grid-template-columns:'
            f'minmax(170px,3fr) 70px 120px 150px;gap:12px;padding:0 0 6px;'
            f'font-size:11px;letter-spacing:.09em;text-transform:uppercase;'
            f'color:#8a93a5;font-weight:700">'
            f'<div>{_e(T("bcl_col_ind"))}</div>'
            f'<div style="text-align:right">{_e(T("bcl_col_degre"))}</div>'
            f'<div style="text-align:right">{_e(T("bcl_col_boucles"))}</div>'
            f'<div></div></div>']
        for x in lv:
            n = par_id[x["id"]]
            lignes.append(
                f'<div style="display:grid;grid-template-columns:'
                f'minmax(170px,3fr) 70px 120px 150px;gap:12px;'
                f'align-items:center;padding:7px 0;'
                f'border-bottom:1px solid #eef2f7">'
                f'<div style="font-size:13.5px;font-weight:600;color:{ENCRE}">'
                f'{_e(_libelle(n))}</div>'
                f'<div style="text-align:right;font-size:13px;color:{ENCRE2};'
                f'font-variant-numeric:tabular-nums">{x["degre"]}</div>'
                f'<div style="text-align:right;font-size:13px;color:{ENCRE2};'
                f'font-variant-numeric:tabular-nums">{x["boucles"]} '
                f'<span style="color:{ENCRE3}">({x["renforcantes"]} / '
                f'{x["equilibrantes"]})</span></div>'
                + (f'<div><span style="font-size:11px;font-weight:700;'
                   f'background:#fdf3e3;color:#a8560a;border-radius:999px;'
                   f'padding:3px 10px">{_e(T("bcl_bascule"))}</span></div>'
                   if x["bascule"] else '<div></div>')
                + '</div>')
        st.markdown("".join(lignes), unsafe_allow_html=True)

        st.markdown(
            f'<div class="titre-bloc" style="margin-top:18px">'
            f'{T("bcl_dominantes")}</div>', unsafe_allow_html=True)
        st.caption(T("bcl_dominantes_note"))
        dom = "".join(
            f'<div style="display:flex;gap:12px;align-items:baseline;'
            f'padding:7px 0;border-bottom:1px solid #eef2f7">'
            f'<div style="font-size:13.5px;font-weight:600;color:{ENCRE};'
            f'flex:1 1 auto">{_e(_libelle(par_id[d["de"]]))} → '
            f'{_e(_libelle(par_id[d["vers"]]))}</div>'
            f'<div style="font-size:12.5px;color:{ENCRE3};white-space:nowrap">'
            f'{_e(T("bcl_dans", n=d["n"]))} '
            f'<span style="color:{HAUSSE}">R{d["renf"]}</span> / '
            f'<span style="color:#d1730c">B{d["equi"]}</span></div></div>'
            for d in M.boucles_dominantes(graphe, toutes_boucles))
        st.markdown(dom, unsafe_allow_html=True)

        st.markdown(
            f'<div class="titre-bloc" style="margin-top:18px">'
            f'{T("bcl_meadows")}</div>', unsafe_allow_html=True)
        st.markdown(
            "".join(f'<div style="font-size:14px;color:{ENCRE2};'
                    f'line-height:1.6;padding:4px 0 4px 16px;position:relative">'
                    f'<span style="position:absolute;left:0;color:#c3ccda">'
                    f'{i + 1}.</span> {T(k)}</div>'
                    for i, k in enumerate(("bcl_m1", "bcl_m2", "bcl_m3",
                                           "bcl_m4"))),
            unsafe_allow_html=True)

    # ------------------------------- les relations et leur justification
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("bcl_relations")}</div>',
                    unsafe_allow_html=True)
        leg = "".join(
            f'<span style="display:inline-flex;align-items:center;gap:6px;'
            f'margin:0 16px 6px 0"><span style="width:9px;height:9px;'
            f'border-radius:2px;background:{JUST_COULEUR[j]}"></span>'
            f'<span style="font-size:12.5px;color:{ENCRE2}">'
            f'<b>{_e(T("bcl_j_" + j))}</b> — {_e(T("bcl_j_" + j + "_x"))}'
            f'</span></span>'
            for j in ("documentee", "empirique", "theorique", "hypothese"))
        st.markdown(f'<div style="margin:2px 0 12px">{leg}</div>',
                    unsafe_allow_html=True)

        desac = M.desaccords(graphe)
        if desac:
            st.warning(T("bcl_desaccords_t", n=len(desac)))
        st.caption(T("bcl_obs_note"))

        lignes = []
        for e in sorted(graphe["aretes"],
                        key=lambda x: (x["just"], -x["force"])):
            c = JUST_COULEUR[e["just"]]
            rho = e.get("rho")
            contre = rho is not None and rho * e["signe"] < -0.3
            obs = ("—" if rho is None else _fmt(rho, 2, True))
            lignes.append(
                f'<div style="display:grid;grid-template-columns:'
                f'9px minmax(210px,2.4fr) 3fr 74px;gap:11px;align-items:center;'
                f'padding:8px 0;border-bottom:1px solid #eef2f7">'
                f'<div style="width:8px;height:8px;border-radius:2px;'
                f'background:{c}"></div>'
                f'<div style="font-size:13.5px;color:{ENCRE};font-weight:600;'
                f'line-height:1.35">{_e(_libelle(par_id[e["de"]]))} '
                f'<span style="color:{ENCRE3};font-weight:400">'
                f'{"→" if e["signe"] > 0 else "⊣"}</span> '
                f'{_e(_libelle(par_id[e["vers"]]))}</div>'
                f'<div style="font-size:12.5px;color:{ENCRE2};line-height:1.45">'
                f'{_e(_ref(e))}'
                + (f'<div style="color:{BAISSE};font-weight:600;'
                   f'margin-top:2px">⚠ {_e(T("bcl_desaccord"))}</div>'
                   if contre else '')
                + f'</div>'
                f'<div style="text-align:right;font-size:13px;'
                f'font-variant-numeric:tabular-nums;'
                f'color:{BAISSE if contre else ENCRE2};'
                f'font-weight:{"700" if contre else "400"}">{obs}</div>'
                f'</div>')
        st.markdown(
            f'<div style="display:grid;grid-template-columns:'
            f'9px minmax(210px,2.4fr) 3fr 74px;gap:11px;padding:0 0 6px;'
            f'font-size:11px;letter-spacing:.09em;text-transform:uppercase;'
            f'color:#8a93a5;font-weight:700"><div></div>'
            f'<div>{_e(T("bcl_relations"))}</div><div></div>'
            f'<div style="text-align:right">{_e(T("bcl_obs"))}</div></div>'
            + "".join(lignes), unsafe_allow_html=True)

    st.caption(T("bcl_diag", noeuds=diag["noeuds"], aretes=diag["aretes"],
                 rayon=_fmt(diag["rayon"], 2),
                 cible=_fmt(diag["cible"], 2)))
