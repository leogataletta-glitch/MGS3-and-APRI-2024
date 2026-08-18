"""Fiches d'intervention — ce qu'on fait des leviers que les boucles désignent.

CETTE PAGE N'EST PAS ÉCRITE À CÔTÉ DE L'ANALYSE, ELLE EN DESCEND.

Chaque fiche part d'un levier du graphe causal. Ce n'est pas une figure de
style : l'effet attendu, les indicateurs de suivi, les boucles visées et le
classement des fiches sont TOUS calculés par le moteur des boucles. Changez une
relation dans le modèle, et les fiches se réordonnent d'elles-mêmes.

CE QUE CHAQUE FICHE PORTE, ET D'OÙ CELA VIENT

  · l'EFFET SIMULÉ sur l'indice d'ensemble — propagation d'une hausse de deux
    points du levier dans tout le graphe ;
  · les INDICATEURS DE SUIVI — les indicateurs du référentiel que la
    propagation touche le plus. Ils ne sont pas inventés pour la fiche : ce
    sont des lignes déjà mesurées, donc le suivi est outillé le jour où
    l'action démarre ;
  · les BOUCLES TRAVERSÉES, et surtout combien sont renforçantes et combien
    équilibrantes — un levier présent dans les deux est un point de bascule ;
  · le NIVEAU D'INTERVENTION, d'après Meadows : ajuster un flux, casser ou
    renforcer une boucle, changer les flux d'information, changer les règles.
    Plus le niveau est élevé, plus l'effet est structurel — et plus il est
    difficile.

CE QUE LE CLASSEMENT NE DIT PAS

L'ordre des fiches suit l'effet simulé, pas la priorité politique. Un effet
modélisé fort sur un levier infaisable vaut moins qu'un effet modeste sur un
levier qu'on sait mettre en œuvre : la faisabilité est donc affichée à côté, et
c'est à l'atelier de trancher. Le modèle propose, il ne décide pas.
"""

import json
import os

import streamlit as st

import boucles_moteur as M
import i18n
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"
HAUSSE, ALERTE, BAISSE = "#1a8a4f", "#d1730c", "#c33a24"
NIVEAU_COULEUR = {1: "#2166ac", 2: "#1a8a4f", 3: "#0f8fa8", 4: "#7048b6"}

# ---------------------------------------------------------------------------
# LES FICHES. Le levier est l'identifiant d'un nœud du graphe causal : c'est
# lui qui fait le lien avec l'analyse des boucles, et tout le reste — effet,
# indicateurs, boucles — en est déduit.
#
# Seuls des leviers ACTIONNABLES portent une fiche. L'aridité et l'état de la
# végétation arrivent haut dans le classement des effets, mais on ne monte pas
# un projet « sur l'aridité » : ce sont des états résultants. Les fiches
# agissent sur ce que l'on peut décider — un équipement, une pratique, une
# règle, un flux d'information.
# ---------------------------------------------------------------------------
FICHES = [
    {"id": "cuisson", "levier": "cuisson", "meadows": 2, "faisabilite": "moyenne"},
    {"id": "agro", "levier": "agro_durable", "meadows": 2, "faisabilite": "moyenne"},
    {"id": "eau", "levier": "eau", "meadows": 1, "faisabilite": "haute"},
    {"id": "finance", "levier": "compte", "meadows": 2, "faisabilite": "moyenne"},
    {"id": "alerte", "levier": "comites", "meadows": 3, "faisabilite": "haute"},
    {"id": "foncier", "levier": "foncier", "meadows": 4, "faisabilite": "faible"},
    {"id": "controle", "levier": "controle", "meadows": 4, "faisabilite": "faible"},
    {"id": "etat_civil", "levier": "etat_civil", "meadows": 1,
     "faisabilite": "haute"},
]

TEXTES = {
    "int_titre": {"en": "Intervention Profiles", "fr": "Fiches d'intervention"},
    "int_sous_titre": {
        "en": "Action sheets built from the levers the loops identify",
        "fr": "Des fiches d'action construites sur les leviers que les boucles "
              "désignent"},
    "int_intro": {
        "en": "Each sheet acts on one lever of the causal graph. Expected "
              "effect, monitoring indicators and ranking are computed by the "
              "loop model — change a relation and the sheets reorder "
              "themselves. **The ranking follows the simulated effect, not "
              "political priority:** a strong modelled effect on an "
              "unfeasible lever is worth less than a modest one you can "
              "actually deliver. Feasibility is shown alongside; the workshop "
              "decides.",
        "fr": "Chaque fiche agit sur un levier du graphe causal. L'effet "
              "attendu, les indicateurs de suivi et le classement sont "
              "calculés par le modèle des boucles — changez une relation, les "
              "fiches se réordonnent. **Le classement suit l'effet simulé, "
              "pas la priorité politique :** un effet modélisé fort sur un "
              "levier infaisable vaut moins qu'un effet modeste sur un levier "
              "qu'on sait mettre en œuvre. La faisabilité est affichée à "
              "côté ; c'est l'atelier qui tranche."},
    "int_tension": {
        "en": "**The strongest immediate effect is not the strongest lever.** "
              "Water, tenure and early warning move the index most in the "
              "simulation, but sit in few loops or none: their effect is "
              "direct and bounded. Conservation farming and forest "
              "enforcement move it little, yet they are the two **tipping "
              "levers** — the only sheets that sit in loops of both signs, "
              "and so the only ones that can turn a degrading dynamic into a "
              "regulating one. A programme needs both: the first to show "
              "results within a season, the second to change what the system "
              "does to itself.",
        "fr": "**L'effet immédiat le plus fort n'est pas le levier le plus "
              "fort.** L'eau, le foncier et l'alerte déplacent le plus "
              "l'indice dans la simulation, mais appartiennent à peu de "
              "boucles ou à aucune : leur effet est direct et borné. Les "
              "pratiques agricoles conservatrices et le contrôle forestier le "
              "déplacent peu, et ce sont pourtant les deux **leviers de "
              "basculement** — les seules fiches présentes dans des boucles "
              "des deux sens, donc les seules capables de retourner une "
              "dynamique dégradante en dynamique régulatrice. Un programme a "
              "besoin des deux : les premières pour montrer des résultats "
              "dans la saison, les secondes pour changer ce que le système "
              "se fait à lui-même."},
    "int_recap": {"en": "The eight sheets at a glance",
                  "fr": "Les huit fiches d'un coup d'œil"},
    "int_c_fiche": {"en": "Sheet", "fr": "Fiche"},
    "int_c_effet": {"en": "Effect", "fr": "Effet"},
    "int_c_niveau": {"en": "Level", "fr": "Niveau"},
    "int_c_portee": {"en": "Structural reach", "fr": "Portée structurelle"},
    "int_effet": {"en": "Simulated effect on the overall score",
                  "fr": "Effet simulé sur l'indice d'ensemble"},
    "int_effet_note": {
        "en": "For a two-point rise of the lever, propagated through the whole "
              "graph. An exploratory scenario of the model, not a forecast.",
        "fr": "Pour une hausse de deux points du levier, propagée dans tout le "
              "graphe. Un scénario exploratoire du modèle, pas une prévision."},
    "int_depart": {"en": "Lever, current score", "fr": "Levier, score actuel"},
    "int_boucles": {"en": "Loops crossed", "fr": "Boucles traversées"},
    "int_bascule": {
        "en": "Tipping lever — sits in loops of both signs",
        "fr": "Levier de basculement — présent dans des boucles des deux sens"},
    "int_objectif": {"en": "Objective", "fr": "Objectif"},
    "int_activites": {"en": "Activities", "fr": "Activités"},
    "int_acteurs": {"en": "Key actors", "fr": "Acteurs clés"},
    "int_horizon": {"en": "Horizon", "fr": "Horizon"},
    "int_suivi": {"en": "Monitoring indicators",
                  "fr": "Indicateurs de suivi"},
    "int_suivi_note": {
        "en": "The framework lines the simulation moves most. They are already "
              "measured, so the monitoring is tooled the day the action "
              "starts.",
        "fr": "Les lignes du référentiel que la simulation déplace le plus. "
              "Elles sont déjà mesurées : le suivi est outillé le jour où "
              "l'action démarre."},
    "int_boucle_visee": {"en": "The loop this seeks to turn",
                         "fr": "La boucle qu'il s'agit de retourner"},
    "int_faisabilite": {"en": "Feasibility", "fr": "Faisabilité"},
    "int_f_haute": {"en": "high", "fr": "haute"},
    "int_f_moyenne": {"en": "medium", "fr": "moyenne"},
    "int_f_faible": {"en": "low", "fr": "faible"},
    "int_niveau": {"en": "Level of intervention", "fr": "Niveau d'intervention"},
    "int_n1": {"en": "Adjust a flow", "fr": "Ajuster un flux"},
    "int_n2": {"en": "Break or strengthen a loop",
               "fr": "Casser ou renforcer une boucle"},
    "int_n3": {"en": "Change the information flows",
               "fr": "Modifier les flux d'information"},
    "int_n4": {"en": "Change the rules", "fr": "Changer les règles"},
    "int_n_note": {
        "en": "After Meadows: the higher the level, the more structural the "
              "effect — and the harder to obtain.",
        "fr": "D'après Meadows : plus le niveau est élevé, plus l'effet est "
              "structurel — et plus il est difficile à obtenir."},
    "int_ancien": {"en": "Earlier working notes", "fr": "Anciennes pistes de travail"},
    "int_ancien_note": {
        "en": "The working hypotheses written before the causal analysis, kept "
              "for the record.",
        "fr": "Les hypothèses de travail écrites avant l'analyse causale, "
              "gardées pour mémoire."},

    # ---------------- les huit fiches
    "int_cuisson_t": {"en": "Break the poverty–charcoal link",
                      "fr": "Casser le lien pauvreté–charbon"},
    "int_cuisson_o": {
        "en": "Take households off fuelwood, which is the first driver of "
              "cover loss and the entry point of the strongest reinforcing "
              "loop in the model.",
        "fr": "Sortir les ménages du bois-énergie, premier moteur du recul du "
              "couvert et porte d'entrée de la boucle renforçante la plus "
              "forte du modèle."},
    "int_cuisson_a": {
        "en": "Microcredit for clean cooking equipment · a supported "
              "eco-charcoal supply chain · improved stoves distributed through "
              "community organisations · price signal on unsustainable "
              "charcoal",
        "fr": "Microcrédit pour l'équipement de cuisson propre · filière de "
              "charbon écologique accompagnée · réchauds améliorés distribués "
              "par les organisations de base · signal-prix sur le charbon non "
              "durable"},
    "int_cuisson_ac": {
        "en": "Ministry of Environment · microfinance institutions · "
              "community-based organisations · charcoal producers",
        "fr": "Ministère de l'Environnement · institutions de microfinance · "
              "organisations de base · producteurs de charbon"},
    "int_cuisson_b": {
        "en": "Cover loss → wood scarcity → higher price → cutting becomes "
              "profitable → more cutting. An alternative fuel cuts the loop at "
              "its demand end.",
        "fr": "Recul du couvert → raréfaction → hausse du prix → la coupe "
              "devient rentable → coupe accrue. Une énergie alternative coupe "
              "la boucle du côté de la demande."},

    "int_agro_t": {"en": "Fertility without fire",
                   "fr": "La fertilité sans le feu"},
    "int_agro_o": {
        "en": "Replace slash-and-burn with practices that build soil, so that "
              "yields stop depending on opening new plots.",
        "fr": "Remplacer le brûlis par des pratiques qui construisent le sol, "
              "pour que le rendement cesse de dépendre de l'ouverture de "
              "nouvelles parcelles."},
    "int_agro_a": {
        "en": "Composting and green manure · live hedges and agroforestry on "
              "slopes · farmer field schools · a burning ban that comes with "
              "an alternative, never alone",
        "fr": "Compostage et engrais verts · haies vives et agroforesterie sur "
              "pente · champs-écoles paysans · interdiction du brûlis assortie "
              "d'une alternative, jamais seule"},
    "int_agro_ac": {
        "en": "Ministry of Agriculture · farmer organisations · CASEC · "
              "agricultural extension services",
        "fr": "Ministère de l'Agriculture · organisations paysannes · CASEC · "
              "services de vulgarisation agricole"},
    "int_agro_b": {
        "en": "Burning costs fertility → yields fall → new plots are opened by "
              "fire. Building soil turns the spiral the other way.",
        "fr": "Le brûlis coûte de la fertilité → les rendements chutent → on "
              "ouvre de nouvelles parcelles par le feu. Construire le sol "
              "retourne la spirale."},

    "int_eau_t": {"en": "Water, and the time it frees",
                  "fr": "L'eau, et le temps qu'elle libère"},
    "int_eau_o": {
        "en": "Improve access to drinking water — the model's shortest path to "
              "health, and through it to the capacity to work.",
        "fr": "Améliorer l'accès à l'eau de boisson — le chemin le plus court "
              "du modèle vers la santé, et par elle vers la capacité de "
              "travail."},
    "int_eau_a": {
        "en": "Improved and protected water points close to dwellings · "
              "community management committees with a maintenance fund · "
              "household treatment where the source stays distant",
        "fr": "Points d'eau améliorés et protégés à proximité des habitations · "
              "comités de gestion communautaire avec fonds d'entretien · "
              "traitement à domicile là où la source reste éloignée"},
    "int_eau_ac": {
        "en": "DINEPA · communal authorities · water user committees · NGOs",
        "fr": "DINEPA · autorités communales · comités d'usagers de l'eau · ONG"},
    "int_eau_b": {
        "en": "Water → health → capacity to work → employment → income → "
              "access to services → water. The loop closes back on itself.",
        "fr": "Eau → santé → capacité de travail → emploi → revenu → accès aux "
              "services → eau. La boucle se referme sur elle-même."},

    "int_finance_t": {"en": "A financial account, and what it unlocks",
                      "fr": "Un compte, et ce qu'il débloque"},
    "int_finance_o": {
        "en": "Give households a place to hold a reserve, so that a shock "
              "stops being paid for by cutting trees or skipping meals.",
        "fr": "Donner aux ménages un endroit où tenir une réserve, pour qu'un "
              "choc cesse de se payer en arbres coupés ou en repas sautés."},
    "int_finance_a": {
        "en": "Mobile accounts opened on the strength of the national identity "
              "card · formalised tontines · productive microcredit tied to the "
              "clean cooking sheet · financial literacy through community "
              "organisations",
        "fr": "Comptes mobiles ouverts sur présentation de la carte "
              "d'identité · tontines formalisées · microcrédit productif "
              "articulé à la fiche cuisson propre · éducation financière par "
              "les organisations de base"},
    "int_finance_ac": {
        "en": "Central bank · microfinance institutions · mobile operators · "
              "community-based organisations",
        "fr": "Banque centrale · institutions de microfinance · opérateurs "
              "mobiles · organisations de base"},
    "int_finance_b": {
        "en": "Income → account → income. A short reinforcing loop, which "
              "spins the right way as soon as it is entered.",
        "fr": "Revenu → compte → revenu. Une boucle renforçante courte, qui "
              "tourne dans le bon sens dès qu'on y entre."},

    "int_alerte_t": {"en": "Warning that reaches, and a committee that acts",
                     "fr": "Une alerte qui arrive, un comité qui agit"},
    "int_alerte_o": {
        "en": "Turn a received message into an organised response — the "
              "cheapest lever of the framework, and the one with the shortest "
              "delay.",
        "fr": "Transformer un message reçu en réponse organisée — le levier le "
              "moins coûteux du référentiel, et celui dont le délai est le "
              "plus court."},
    "int_alerte_a": {
        "en": "One local risk committee per communal section, recruited from "
              "existing organisations · two drills a year · radio and SMS "
              "relay · shelters checked before each season",
        "fr": "Un comité local de gestion des risques par section communale, "
              "recruté dans le tissu associatif existant · deux exercices par "
              "an · relais radio et SMS · abris vérifiés avant chaque saison"},
    "int_alerte_ac": {
        "en": "Civil protection · CASEC · community-based organisations · "
              "community radios",
        "fr": "Protection civile · CASEC · organisations de base · radios "
              "communautaires"},
    "int_alerte_b": {
        "en": "This one does not turn a loop: it is a flow of information, "
              "Meadows' third level. Its effect is fast and narrow — which is "
              "exactly what a season of hurricanes demands.",
        "fr": "Celle-ci ne retourne pas une boucle : c'est un flux "
              "d'information, le troisième niveau de Meadows. Son effet est "
              "rapide et étroit — ce que réclame précisément une saison "
              "cyclonique."},

    "int_foncier_t": {"en": "Tenure, and the horizon it opens",
                      "fr": "Le foncier, et l'horizon qu'il ouvre"},
    "int_foncier_o": {
        "en": "Secure land rights so that planting a tree becomes a rational "
              "act — nobody invests in ten years on a plot they may lose next "
              "season.",
        "fr": "Sécuriser les droits fonciers pour que planter un arbre "
              "redevienne un acte rationnel — personne n'investit à dix ans "
              "sur une parcelle qu'il peut perdre à la saison prochaine."},
    "int_foncier_a": {
        "en": "Participatory mapping of customary rights · recognition of "
              "occupancy documents · mediation of disputes at CASEC level · "
              "tenure conditions attached to payments for ecosystem services",
        "fr": "Cartographie participative des droits coutumiers · "
              "reconnaissance des documents d'occupation · médiation des "
              "litiges au niveau du CASEC · conditions foncières attachées aux "
              "paiements pour services écosystémiques"},
    "int_foncier_ac": {
        "en": "ONACA · CASEC · customary authorities · farmer organisations",
        "fr": "ONACA · CASEC · autorités coutumières · organisations paysannes"},
    "int_foncier_b": {
        "en": "Tenure → agricultural productivity → less clearing → cover. "
              "A rule change, Meadows' fourth level: slow, contested, "
              "structural.",
        "fr": "Foncier → productivité agricole → moins de défrichement → "
              "couvert. Un changement de règle, quatrième niveau de Meadows : "
              "lent, disputé, structurel."},

    "int_controle_t": {"en": "Rules for the forest, and who holds them",
                       "fr": "Des règles pour la forêt, et qui les tient"},
    "int_controle_o": {
        "en": "Put a brake on the relation the model finds most dominant — "
              "pressure on fuelwood against forest cover, present in 20 of the "
              "38 loops.",
        "fr": "Poser un frein sur la relation que le modèle trouve la plus "
              "dominante — la pression sur le bois contre le couvert "
              "forestier, présente dans 20 des 38 boucles."},
    "int_controle_a": {
        "en": "Community surveillance paid through payments for ecosystem "
              "services · negotiated rather than imposed sanctions · felling "
              "permits tied to replanting · protection of the remaining "
              "mangrove",
        "fr": "Surveillance communautaire rémunérée par des paiements pour "
              "services écosystémiques · sanctions négociées plutôt "
              "qu'imposées · permis de coupe assortis de replantation · "
              "protection de la mangrove subsistante"},
    "int_controle_ac": {
        "en": "Ministry of Environment · ANAP · CASEC · user associations",
        "fr": "Ministère de l'Environnement · ANAP · CASEC · associations "
              "d'usagers"},
    "int_controle_b": {
        "en": "Enforcement is the only lever that acts directly on the "
              "dominant relation. Alone it displaces the pressure; paired with "
              "the cooking sheet, it removes it.",
        "fr": "Le contrôle est le seul levier qui agisse directement sur la "
              "relation dominante. Seul, il déplace la pression ; associé à la "
              "fiche cuisson, il la supprime."},

    "int_etat_civil_t": {"en": "A birth certificate, and the doors it opens",
                         "fr": "Un acte de naissance, et les portes qu'il ouvre"},
    "int_etat_civil_o": {
        "en": "Register births, which conditions the identity card, which in "
              "turn conditions the account and access to public services.",
        "fr": "Enregistrer les naissances, qui conditionnent la carte "
              "d'identité, qui conditionne à son tour le compte et l'accès aux "
              "services publics."},
    "int_etat_civil_a": {
        "en": "Mobile registration hearings by communal section · late "
              "registration made free · systematic registration at health "
              "facilities and schools",
        "fr": "Audiences foraines d'enregistrement par section communale · "
              "gratuité de l'enregistrement tardif · enregistrement "
              "systématique en centre de santé et à l'école"},
    "int_etat_civil_ac": {
        "en": "ONI · civil registry offices · CASEC · schools and health "
              "facilities",
        "fr": "ONI · officiers d'état civil · CASEC · écoles et centres de "
              "santé"},
    "int_etat_civil_b": {
        "en": "Not a loop but a chain, and a blocked one: without papers, "
              "neither account nor services. Unblocking it costs little and "
              "opens several sheets at once.",
        "fr": "Non pas une boucle mais une chaîne, et elle est bloquée : sans "
              "papiers, ni compte ni services. La débloquer coûte peu et ouvre "
              "plusieurs fiches à la fois."},
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


def calculer(graphe, par_ligne, lst_boucles):
    """Enrichit chaque fiche de ce que le modèle en dit. Rien n'est écrit en
    dur : effet, indicateurs de suivi, boucles, tout est déduit du graphe."""
    par_id = {n["id"]: n for n in graphe["noeuds"]}
    etat = M.etat_courant(graphe, par_ligne)
    out = []
    for f in FICHES:
        cle = f["levier"]
        if cle not in par_id:
            continue
        var = {cle: 2.0}
        eff = M.propager(graphe, var)
        ei = M.effet_indice(graphe, eff, var, par_ligne)
        # Les indicateurs de suivi : les lignes du référentiel les plus
        # déplacées par la simulation. Mesurées, donc suivables.
        suivi = []
        for autre, d in sorted(eff.items(), key=lambda x: -abs(x[1])):
            n = par_id.get(autre)
            if not n or not n.get("ligne") or abs(d) <= M.SEUIL_NUL:
                continue
            r = par_ligne.get(n["ligne"])
            if r:
                suivi.append((n, r, d))
            if len(suivi) >= 4:
                break
        dedans = [b for b in lst_boucles if cle in b["noeuds"]]
        renf = sum(1 for b in dedans if b["type"] == "renforcante")
        out.append({**f, "noeud": par_id[cle], "depart": etat.get(cle),
                    "delta": ei["delta"], "suivi": suivi,
                    "boucles": len(dedans), "renforcantes": renf,
                    "equilibrantes": len(dedans) - renf,
                    "bascule": renf > 0 and len(dedans) - renf > 0})
    return sorted(out, key=lambda x: -x["delta"])


STYLE = """
<style>
  .int-t   { font-size:17.5px; font-weight:700; color:#101728;
             letter-spacing:-.015em; margin:0; line-height:1.3; }
  .int-lab { font-size:11px; letter-spacing:.09em; text-transform:uppercase;
             font-weight:700; color:#8a93a5; margin:14px 0 3px; }
  .int-x   { font-size:14.5px; color:#3c4761; line-height:1.6; margin:0; }
  .int-chip{ display:inline-block; font-size:11.5px; font-weight:700;
             border-radius:999px; padding:3px 11px; margin:0 6px 6px 0; }
  .int-eff { font-size:27px; font-weight:700; letter-spacing:-.03em;
             font-variant-numeric:tabular-nums; line-height:1; }
</style>
"""


def render(anciennes=None):
    graphe, par_ligne = _charger()
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown(
        f'<h2 style="font-size:27px;font-weight:700;color:{ENCRE};'
        f'letter-spacing:-.02em;margin:2px 0 0">{T("int_titre")}</h2>'
        f'<p style="font-size:12.5px;color:{ENCRE3};letter-spacing:.06em;'
        f'text-transform:uppercase;margin:2px 0 0;font-weight:600">'
        f'{T("int_sous_titre")}</p>', unsafe_allow_html=True)
    st.info(T("int_intro"))

    lst_boucles = M.boucles(graphe)
    fiches = calculer(graphe, par_ligne, lst_boucles)

    # LA TENSION EST LE CŒUR DE LA PAGE, pas une nuance de bas de page : les
    # fiches à effet immédiat et les leviers de basculement ne sont pas les
    # mêmes, et un programme qui ne retiendrait que les premières laisserait
    # la structure intacte.
    st.warning(T("int_tension"))

    # Un récapitulatif avant le détail : huit fiches déroulées d'affilée se
    # lisent mal, et le lecteur veut d'abord voir le paysage.
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("int_recap")}</div>',
                    unsafe_allow_html=True)
        emax = max((abs(f["delta"]) for f in fiches), default=1) or 1
        recap = [
            f'<div style="display:grid;grid-template-columns:'
            f'minmax(180px,3fr) 3fr 76px 150px;gap:12px;padding:0 0 6px;'
            f'font-size:11px;letter-spacing:.09em;text-transform:uppercase;'
            f'color:#8a93a5;font-weight:700">'
            f'<div>{_e(T("int_c_fiche"))}</div>'
            f'<div style="grid-column:span 2">{_e(T("int_c_effet"))}</div>'
            f'<div>{_e(T("int_c_portee"))}</div></div>']
        for f in fiches:
            c = NIVEAU_COULEUR[f["meadows"]]
            recap.append(
                f'<div style="display:grid;grid-template-columns:'
                f'minmax(180px,3fr) 3fr 76px 150px;gap:12px;align-items:center;'
                f'padding:7px 0;border-bottom:1px solid #eef2f7">'
                f'<div style="font-size:13.5px;font-weight:600;color:{ENCRE}">'
                f'{_e(T("int_" + f["id"] + "_t"))}</div>'
                f'<div style="background:#f1f4f9;border-radius:5px;height:14px;'
                f'overflow:hidden"><div style="height:100%;border-radius:5px;'
                f'width:{max(100 * f["delta"] / emax, 1):.0f}%;'
                f'background:{HAUSSE}"></div></div>'
                f'<div style="font-size:13px;font-weight:600;color:{ENCRE};'
                f'text-align:right;font-variant-numeric:tabular-nums">'
                f'{_fmt(f["delta"], 3, True)}</div>'
                + (f'<div><span class="int-chip" style="background:#fdf3e3;'
                   f'color:#a8560a;margin:0">{_e(T("int_bascule"))}</span>'
                   f'</div>' if f["bascule"] else
                   f'<div style="font-size:12px;color:{ENCRE3}">'
                   f'{f["boucles"]} {_e(T("int_boucles")).lower()}</div>')
                + '</div>')
        st.markdown("".join(recap), unsafe_allow_html=True)

    for f in fiches:
        with st.container(border=True):
            niv = f["meadows"]
            coul = NIVEAU_COULEUR[niv]
            g, d = st.columns([3.1, 1])
            with g:
                st.markdown(
                    f'<div class="int-t">{_e(T("int_" + f["id"] + "_t"))}</div>'
                    f'<div style="margin-top:8px">'
                    f'<span class="int-chip" style="background:{coul}1a;'
                    f'color:{coul}">{niv} · {_e(T("int_n%d" % niv))}</span>'
                    f'<span class="int-chip" style="background:#f1f4f9;'
                    f'color:{ENCRE2}">{_e(T("int_faisabilite"))} : '
                    f'{_e(T("int_f_" + f["faisabilite"]))}</span>'
                    + (f'<span class="int-chip" style="background:#fdf3e3;'
                       f'color:#a8560a">{_e(T("int_bascule"))}</span>'
                       if f["bascule"] else '')
                    + '</div>', unsafe_allow_html=True)
            with d:
                c = HAUSSE if f["delta"] > 0 else ENCRE3
                st.markdown(
                    f'<div style="text-align:right">'
                    f'<div class="int-eff" style="color:{c}">'
                    f'{_fmt(f["delta"], 3, True)}</div>'
                    f'<div style="font-size:11.5px;color:{ENCRE3};'
                    f'margin-top:3px">{_e(T("int_effet"))}</div></div>',
                    unsafe_allow_html=True)

            st.markdown(
                f'<div class="int-lab">{_e(T("int_objectif"))}</div>'
                f'<p class="int-x">{_e(T("int_" + f["id"] + "_o"))}</p>'
                f'<div class="int-lab">{_e(T("int_activites"))}</div>'
                f'<p class="int-x">{_e(T("int_" + f["id"] + "_a"))}</p>',
                unsafe_allow_html=True)

            ga, dr = st.columns(2)
            with ga:
                st.markdown(
                    f'<div class="int-lab">{_e(T("int_acteurs"))}</div>'
                    f'<p class="int-x" style="font-size:13.5px">'
                    f'{_e(T("int_" + f["id"] + "_ac"))}</p>',
                    unsafe_allow_html=True)
            with dr:
                dep = (_fmt(f["depart"]) + " / 10") if f["depart"] is not None \
                    else "—"
                st.markdown(
                    f'<div class="int-lab">{_e(T("int_depart"))}</div>'
                    f'<p class="int-x" style="font-size:13.5px">'
                    f'{_e(_libelle(f["noeud"]))} — <b>{dep}</b><br>'
                    f'{_e(T("int_boucles"))} : {f["boucles"]} '
                    f'<span style="color:{HAUSSE}">R{f["renforcantes"]}</span> / '
                    f'<span style="color:{ALERTE}">B{f["equilibrantes"]}</span>'
                    f'</p>', unsafe_allow_html=True)

            st.markdown(
                f'<div class="int-lab">{_e(T("int_boucle_visee"))}</div>'
                f'<p class="int-x">{_e(T("int_" + f["id"] + "_b"))}</p>'
                f'<div class="int-lab">{_e(T("int_suivi"))}</div>',
                unsafe_allow_html=True)
            if f["suivi"]:
                st.markdown("".join(
                    f'<div style="display:flex;gap:12px;align-items:baseline;'
                    f'padding:5px 0;border-bottom:1px solid #eef2f7">'
                    f'<div style="flex:1 1 auto;font-size:13.5px;'
                    f'color:{ENCRE}">L{r["ligne"]} · {_e(_nom_indic(r))}</div>'
                    f'<div style="font-size:13px;font-weight:700;'
                    f'color:{HAUSSE if dd > 0 else BAISSE};'
                    f'font-variant-numeric:tabular-nums;white-space:nowrap">'
                    f'{"↑" if dd > 0 else "↓"} {_fmt(dd, 2, True)}</div></div>'
                    for n, r, dd in f["suivi"]), unsafe_allow_html=True)
            st.caption(T("int_suivi_note"))

    st.caption(T("int_effet_note"))
    st.caption(T("int_n_note"))

    if anciennes is not None:
        with st.expander(T("int_ancien")):
            st.caption(T("int_ancien_note"))
            anciennes()
