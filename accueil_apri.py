"""Accueil — comprendre APRI en quatre écrans.

POURQUOI UN PARCOURS ET PAS UNE PAGE

Le site ouvrait sur le cadre méthodologique : avant d'apprendre quoi que ce
soit du territoire, on apprenait comment on le mesure. C'est l'ordre d'un
rapport, pas celui d'un tableau de bord. Cette page prend la première place et
pose les quatre questions dans l'ordre où on se les pose :

    Où ?  ›  Qu'a-t-on mesuré ?  ›  Qu'a-t-on trouvé ?  ›  Que faire ?

Un écran à la fois, avec un bouton pour avancer. Le pari est simple : quatre
petites pages qu'on parcourt valent mieux qu'une grande qu'on saute.

TOUS LES CHIFFRES SONT CALCULÉS. L'indice, l'amplitude entre sections, les
scores de dimension, les indicateurs les plus coûteux, l'effet du portefeuille
d'actions : rien n'est écrit en dur. Une page d'accueil qui annonce un chiffre
faux est pire qu'une page d'accueil absente, parce qu'on la croit.

L'AMPLITUDE EST CALCULÉE SUR UNE BASE COMMUNE, ET C'EST LA SEULE FAÇON HONNÊTE.
Comparer Trichet à Quentin sur les 66 indicateurs scorés serait injuste : deux
sections n'ont pas de valeur pour neuf d'entre eux, et leur indice porterait
alors sur un référentiel plus étroit. On ne retient donc, pour ce classement,
que les 57 indicateurs renseignés POUR LES DIX sections. L'indice global
publié, lui, reste celui du référentiel entier — les deux chiffres diffèrent,
et la page le dit plutôt que de les confondre.
"""

import json
import os

import streamlit as st

import i18n
import icones
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"
VERT, BLEU, AMBRE, ROUGE, GRIS = ("#1a8a4f", "#2166ac", "#d1730c",
                                  "#c33a24", "#8a93a5")

SECTIONS = ["Anse à Drick", "Barbois", "Dumont", "Débouchette", "Mouline",
            "Quentin", "Beaulieu", "Blactote", "Dalmette", "Trichet"]
DIM_CLE = {
    "I. PHYSICAL AND INFRASTRUCTURAL DIMENSION": "dim1",
    "II. INSTITUTIONAL, TECHNOLOGICAL, AND GOVERNANCE  DIMENSION": "dim2",
    "III.  ENVIRONMENTAL AND ECOLOGICAL DIMENSION": "dim3",
    "IV. ECONOMIC, LIVELIHOODS, AND FOOD SECURITY DIMENSION": "dim4",
    "V. SOCIAL AND COMMUNITY DIMENSION": "dim5",
    "VI. HUMAN DIMENSION": "dim6",
    "VII. CULTURAL, IDENTITY-BASED, AND PSYCHOLOGICAL DIMENSION": "dim7",
}
TEINTES = {"dim1": "#d1730c", "dim2": "#2166ac", "dim3": "#1a8a4f",
           "dim4": "#a02c8f", "dim5": "#0f8fa8", "dim6": "#c33a24",
           "dim7": "#7048b6"}

ETAPES = ("po_e1", "po_e2", "po_e3", "po_e4")

TEXTES = {
    "mode_portail": {"en": "Home", "fr": "Accueil"},
    "po_titre": {"en": "Landscape resilience observatory",
                 "fr": "Observatoire de la résilience des paysages"},
    "po_sous": {"en": "Sud and Grand'Anse, Haiti — survey 2024",
                "fr": "Sud et Grand'Anse, Haïti — enquête 2024"},
    "po_e1": {"en": "Where?", "fr": "Où ?"},
    "po_e2": {"en": "What was measured?", "fr": "Qu'a-t-on mesuré ?"},
    "po_e3": {"en": "What was found?", "fr": "Qu'a-t-on trouvé ?"},
    "po_e4": {"en": "What can be done?", "fr": "Que faire ?"},
    "po_suivant": {"en": "Next", "fr": "Suivant"},
    "po_precedent": {"en": "Back", "fr": "Précédent"},
    "po_etape": {"en": "Step {n} of 4", "fr": "Étape {n} sur 4"},

    # ---------------- écran 1
    "po_1_t": {"en": "Ten communal sections in Haiti's Greater South",
               "fr": "Dix sections communales dans le Grand Sud d'Haïti"},
    "po_1_x": {
        "en": "A mountain landscape and a coastal one, across two departments. "
              "Households were drawn at random within strata, from a "
              "georeferenced building base — so that areas without a reliable "
              "administrative register are covered too.",
        "fr": "Un paysage de montagne et un paysage littoral, sur deux "
              "départements. Les ménages ont été tirés au sort dans des "
              "strates, à partir d'une base de bâtiments géoréférencés — pour "
              "que les zones sans registre administratif fiable soient "
              "couvertes aussi."},
    "po_1_c1": {"en": "households surveyed", "fr": "ménages enquêtés"},
    "po_1_c2": {"en": "communal sections", "fr": "sections communales"},
    "po_1_c3": {"en": "departments", "fr": "départements"},
    "po_1_c3x": {"en": "Sud and Grand'Anse", "fr": "Sud et Grand'Anse"},
    "po_1_carte": {"en": "The surveyed area, in the far south-west of the "
                         "country.",
                   "fr": "La zone enquêtée, à l'extrême sud-ouest du pays."},

    # ---------------- écran 2
    "po_2_t": {"en": "Resilience, in one number between 0 and 10",
               "fr": "La résilience, en un nombre entre 0 et 10"},
    "po_2_x": {
        "en": "APRI reads a territory as a system: its capacity to anticipate, "
              "absorb and adapt — measured **before** a shock, not after it. "
              "It is not a damage report and not a forecast.",
        "fr": "APRI lit un territoire comme un système : sa capacité à "
              "anticiper, absorber et s'adapter — mesurée **avant** le choc, "
              "pas après. Ce n'est ni un relevé de dégâts ni une prévision."},
    "po_2_a1": {"en": "Anticipate", "fr": "Anticiper"},
    "po_2_a1x": {"en": "see it coming and prepare",
                 "fr": "le voir venir et s'y préparer"},
    "po_2_a2": {"en": "Absorb", "fr": "Absorber"},
    "po_2_a2x": {"en": "take the hit without breaking",
                 "fr": "encaisser sans se rompre"},
    "po_2_a3": {"en": "Adapt", "fr": "S'adapter"},
    "po_2_a3x": {"en": "change rather than go back",
                 "fr": "changer plutôt que revenir en arrière"},
    "po_2_f1": {"en": "attributes", "fr": "attributs"},
    "po_2_f2": {"en": "dimensions", "fr": "dimensions"},
    "po_2_f3": {"en": "indicators", "fr": "indicateurs"},
    "po_2_f3x": {"en": "{f} scored to date", "fr": "{f} scorés à ce jour"},
    "po_2_f4": {"en": "one score", "fr": "un score"},
    "po_2_src": {"en": "Three sources, because one would leave a blind spot",
                 "fr": "Trois sources, parce qu'une seule laisserait un angle mort"},
    "po_2_s1": {"en": "Household survey", "fr": "Enquête ménage"},
    "po_2_s1x": {"en": "what families live through",
                 "fr": "ce que vivent les familles"},
    "po_2_s2": {"en": "Satellite imagery", "fr": "Imagerie satellitaire"},
    "po_2_s2x": {"en": "what no questionnaire sees",
                 "fr": "ce qu'aucun questionnaire ne voit"},
    "po_2_s3": {"en": "Community assessment", "fr": "Évaluation communautaire"},
    "po_2_s3x": {"en": "what holds the territory together",
                 "fr": "ce qui tient le territoire"},

    # ---------------- écran 3
    "po_3_t": {"en": "4.54 out of 10 — and what that hides",
               "fr": "4,54 sur 10 — et ce que cela cache"},
    "po_3_idx": {"en": "Overall index", "fr": "Indice global"},
    "po_3_idx_x": {"en": "weighted mean of the {n} scored indicators",
                   "fr": "moyenne pondérée des {n} indicateurs scorés"},
    "po_3_amp_t": {"en": "One average, ten very different places",
                   "fr": "Une moyenne, dix situations très différentes"},
    "po_3_amp": {
        "en": "Between the best-placed section and the least well placed, "
              "**{d} points of spread** — a third of the distance already "
              "covered. An average alone would have hidden it.",
        "fr": "Entre la section la mieux placée et la moins bien placée, "
              "**{d} points d'écart** — le tiers du chemin déjà parcouru. La "
              "moyenne seule l'aurait masqué."},
    "po_3_haut": {"en": "Best placed", "fr": "La mieux placée"},
    "po_3_bas": {"en": "Least well placed", "fr": "La moins bien placée"},
    "po_3_base": {
        "en": "Sections are compared on the {n} indicators available for all "
              "ten of them — not on the full framework, which two sections do "
              "not cover entirely. This is why these figures differ slightly "
              "from the published index.",
        "fr": "Les sections sont comparées sur les {n} indicateurs disponibles "
              "pour les dix — pas sur le référentiel entier, que deux sections "
              "ne couvrent pas complètement. C'est pourquoi ces chiffres "
              "diffèrent un peu de l'indice publié."},
    "po_3_rep_t": {"en": "4.54 is not a middling territory — it is a "
                         "territory of extremes",
                   "fr": "4,54 n'est pas un territoire moyen — c'est un "
                         "territoire d'extrêmes"},
    "po_3_rep": {
        "en": "Spread the {n} scored indicators across the scale and the "
              "average dissolves: **{bas} % of the framework's weight sits at "
              "2 out of 10 or below**, while {haut} % sits at 9 or 10. Almost "
              "nothing is in the middle. An average of 4.54 describes no "
              "single indicator — it is the resultant of two opposite blocks, "
              "and that is what makes it actionable: the low block is a list "
              "of things to build.",
        "fr": "Étalez les {n} indicateurs scorés sur l'échelle et la moyenne "
              "se dissout : **{bas} % du poids du référentiel est à 2 sur 10 "
              "ou moins**, quand {haut} % est à 9 ou 10. Presque rien n'est au "
              "milieu. Une moyenne de 4,54 ne décrit aucun indicateur — c'est "
              "la résultante de deux blocs opposés, et c'est ce qui la rend "
              "utile : le bloc du bas est une liste de choses à construire."},
    "po_3_rep_ax": {"en": "share of the framework's weight",
                    "fr": "part du poids du référentiel"},
    "po_3_pay_t": {"en": "And two landscapes that do not hold up alike",
                   "fr": "Et deux paysages qui ne tiennent pas pareil"},
    "po_3_littoral": {"en": "Coastal", "fr": "Littoral"},
    "po_3_montagne": {"en": "Mountain", "fr": "Montagne"},
    "po_3_dims": {"en": "Where it holds, and where it does not",
                  "fr": "Où ça tient, et où ça ne tient pas"},
    "po_3_faits": {"en": "Three findings that carry the most weight",
                   "fr": "Trois constats qui pèsent le plus lourd"},
    "po_3_dim7": {"en": "The seventh dimension — cultural and psychological — "
                        "has no computed indicator yet. It is shown at zero "
                        "coverage rather than hidden.",
                  "fr": "La septième dimension — culturelle et psychologique — "
                        "n'a encore aucun indicateur calculé. Elle est montrée "
                        "à couverture nulle plutôt que masquée."},

    # ---------------- écran 4
    "po_4_t": {"en": "Eight sheets, and what they would move",
               "fr": "Huit fiches, et ce qu'elles déplaceraient"},
    "po_4_x": {
        "en": "Each sheet acts on one lever of the causal model. Simulated "
              "together, the eight move the index from {a} to {b}. It is a "
              "modelled effect, not a promise — but it ranks what to do first.",
        "fr": "Chaque fiche agit sur un levier du modèle causal. Simulées "
              "ensemble, les huit portent l'indice de {a} à {b}. C'est un "
              "effet modélisé, pas une promesse — mais il dit par quoi "
              "commencer."},
    "po_4_gain": {"en": "Modelled gain", "fr": "Gain modélisé"},
    "po_4_lot": {
        "en": "**{n} of the {t} sheets carry {p} % of that gain** — the ones "
              "that are both feasible and short-term. If the decision is about "
              "sequencing rather than scope, this is the sentence to keep.",
        "fr": "**{n} des {t} fiches portent {p} % de ce gain** — celles qui "
              "sont à la fois faisables et à court terme. Si la décision porte "
              "sur un séquencement plutôt qu'un périmètre, c'est la phrase à "
              "retenir."},
    "po_4_portes": {"en": "Where to go from here", "fr": "Par où continuer"},
    "po_4_p1": {"en": "The donor briefing — findings and responses in full",
                "fr": "La note aux bailleurs — constats et réponses en entier"},
    "po_4_p2": {"en": "Intervention profiles — one sheet per lever",
                "fr": "Les fiches d'intervention — une fiche par levier"},
    "po_4_p3": {"en": "Results analysis — dimension by dimension",
                "fr": "L'analyse des résultats — dimension par dimension"},
    "po_4_p4": {"en": "The territory — where all this takes place",
                "fr": "Le territoire — où tout cela se passe"},
    "po_absent": {"en": "Result files missing.",
                  "fr": "Les fichiers de résultats sont absents."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)

STYLE = """
<style>
  .po-pas  { display:flex; gap:0; align-items:stretch; margin:16px 0 6px;
             border-bottom:1px solid #e6ecf4; }
  .po-p    { flex:1 1 0; padding:9px 4px 11px; text-align:center;
             font-size:13px; font-weight:600; color:#a7b0be;
             border-bottom:3px solid transparent; }
  .po-p b  { display:block; font-size:11px; letter-spacing:.09em;
             text-transform:uppercase; font-weight:700; margin-bottom:2px; }
  .po-p.on { color:#101728; border-bottom-color:#1c6349; }
  .po-p.vu { color:#3c4761; }
  .po-h    { font-size:25px; font-weight:700; color:#101728;
             letter-spacing:-.02em; margin:14px 0 6px; line-height:1.2; }
  .po-x    { font-size:15.5px; color:#3c4761; line-height:1.65; margin:0;
             max-width:82ch; text-align:left !important; }
  .po-g    { display:flex; gap:14px; flex-wrap:wrap; margin-top:16px; }
  .po-c    { flex:1 1 200px; min-width:180px; background:#fff;
             border:1px solid #e3eaf3; border-radius:14px; padding:16px 18px;
             box-shadow:0 1px 2px rgba(16,23,40,.05); }
  .po-n    { font-size:34px; font-weight:700; color:#101728; line-height:1;
             letter-spacing:-.03em; font-variant-numeric:tabular-nums; }
  .po-l    { font-size:13.5px; font-weight:600; color:#3c4761; margin-top:6px;
             text-align:left !important; }
  .po-s    { font-size:12px; color:#8a93a5; margin-top:2px;
             text-align:left !important; }
  .po-i    { width:34px; height:34px; border-radius:10px; display:flex;
             align-items:center; justify-content:center; margin-bottom:10px; }
  .po-flux { display:flex; align-items:stretch; gap:4px; flex-wrap:wrap;
             margin-top:14px; }
  .po-f    { flex:1 1 140px; min-width:125px; text-align:center;
             padding:14px 10px; border:1px solid #e3eaf3; border-radius:13px;
             background:#fff; }
  .po-f .po-n { font-size:27px; }
  .po-f .po-l, .po-f .po-s { text-align:center !important; }
  .po-ch   { align-self:center; color:#c3ccda; font-size:20px; flex:0 0 auto; }
  .po-j    { height:16px; background:#eef2f7; border-radius:8px;
             position:relative; margin:10px 0 4px; overflow:hidden; }
  .po-jr   { position:absolute; left:0; top:0; height:100%; border-radius:8px; }
  .po-bar  { display:grid; grid-template-columns:minmax(150px,2.2fr) 4fr 54px;
             gap:11px; align-items:center; padding:7px 0;
             border-bottom:1px solid #f0f4f9; }
  .po-bp   { height:13px; background:#f1f4f9; border-radius:5px; }
  .po-bf   { height:100%; border-radius:5px; }
  .po-nom  { font-size:13.5px; font-weight:600; color:#101728;
             text-align:left !important; }
  .po-val  { font-size:13.5px; font-weight:700; text-align:right;
             font-variant-numeric:tabular-nums; }
  .po-duel { display:grid; grid-template-columns:1fr auto 1fr; gap:16px;
             align-items:center; }
  .po-lab  { font-size:11px; letter-spacing:.09em; text-transform:uppercase;
             font-weight:700; color:#8a93a5; margin:22px 0 6px; }
  /* Trois chiffres à côté d'une carte : à 200 px de base ils passaient en
     deux lignes, dont une seule carte esseulée. */
  .po-serre .po-c { flex:1 1 140px; min-width:130px; padding:14px 15px; }
  .po-serre .po-n { font-size:27px; }
</style>
"""


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _gras(t):
    out, morceaux = [], _e(t).split("**")
    for i, m in enumerate(morceaux):
        out.append(f"<b>{m}</b>" if i % 2 else m)
    return "".join(out)


def _f(v, dec=2, signe=False):
    if v is None:
        return "—"
    s = f"{v:+.{dec}f}" if signe else f"{v:.{dec}f}"
    return s.replace(".", ",") if i18n.get_lang() == "fr" else s


def _trouver(nom):
    for c in (os.path.join(DATA, nom), os.path.join(APP_DIR, nom)):
        if os.path.exists(c):
            return c
    return None


@st.cache_data(show_spinner=False)
def _mesures(lang):
    """Tout ce que la page affiche de chiffré, en une lecture.

    `lang` n'est pas décoratif : les noms d'indicateurs changent avec la
    langue, et sans lui le cache figerait la première langue affichée.
    """
    p = _trouver("resultats.json")
    if not p:
        return None
    with open(p, encoding="utf-8") as f:
        res = json.load(f)
    res = res["indicateurs"] if isinstance(res, dict) and "indicateurs" in res \
        else res
    scores = [r for r in res
              if (r.get("scores_corriges") or {}).get("Total") is not None]

    def moyenne(cle, lst):
        n = d = 0.0
        for r in lst:
            v = (r.get("scores_corriges") or {}).get(cle)
            if v is None:
                continue
            p_ = r.get("ponderation") or 1
            n += p_ * float(v)
            d += p_
        return (n / d) if d else None

    # base commune : les indicateurs renseignés POUR LES DIX sections
    commun = [r for r in scores
              if all((r.get("scores_corriges") or {}).get(s) is not None
                     for s in SECTIONS)]
    par_section = {s: moyenne(s, commun) for s in SECTIONS}
    ordre = sorted(par_section.items(), key=lambda kv: -(kv[1] or 0))

    # dimensions : score pondéré et poids, sur tout le référentiel
    dims = {}
    for r in res:
        cle = DIM_CLE.get(r.get("dimension") or "")
        if not cle:
            continue
        e = dims.setdefault(cle, {"num": 0.0, "den": 0.0, "n": 0, "faits": 0})
        e["n"] += 1
        v = (r.get("scores_corriges") or {}).get("Total")
        if v is not None:
            e["faits"] += 1
            p_ = r.get("ponderation") or 1
            e["num"] += p_ * float(v)
            e["den"] += p_
    for e in dims.values():
        e["score"] = (e["num"] / e["den"]) if e["den"] else None

    # les trois indicateurs qui coûtent le plus à l'indice
    def nom(r):
        if lang == "fr" and r.get("indicateur_fr"):
            return r["indicateur_fr"]
        return r.get("indicateur", "")

    couteux = sorted(
        scores,
        key=lambda r: -((r.get("ponderation") or 1)
                        * (10 - float(r["scores_corriges"]["Total"]))))[:3]
    faits = [{"nom": nom(r),
              "score": float(r["scores_corriges"]["Total"]),
              "valeur": (r.get("valeurs") or {}).get("Total"),
              "unite": (r.get("unite") or "").strip()
                       or ("%" if "%" in (r.get("metrique") or "") else ""),
              "dim": DIM_CLE.get(r.get("dimension") or "")}
             for r in couteux]

    # LA DISTRIBUTION SUR L'ÉCHELLE, EN PART DE POIDS ET NON EN NOMBRE.
    # Compter les indicateurs traiterait un indicateur pesant 4,6 comme un
    # indicateur pesant 1 ; c'est le poids qui fait la moyenne, c'est donc le
    # poids qu'il faut étaler.
    poids_total = sum((r.get("ponderation") or 1) for r in scores) or 1
    bandes = []
    for a_, b_, lab in ((0, 2, "0–2"), (3, 4, "3–4"), (5, 6, "5–6"),
                        (7, 8, "7–8"), (9, 10, "9–10")):
        g = [r for r in scores
             if a_ <= float(r["scores_corriges"]["Total"]) <= b_]
        bandes.append({"lab": lab, "n": len(g),
                       "part": sum((r.get("ponderation") or 1)
                                   for r in g) / poids_total * 100,
                       "milieu": (a_ + b_) / 2})

    paysages = {p_: moyenne(p_, scores) for p_ in ("Littoral", "Montagne")}

    bases = [int((r.get("n") or {}).get("Total") or 0) for r in scores]
    bases = [b for b in bases if b]
    p_idx = _trouver("croisement_index.json")
    menages = None
    if p_idx:
        try:
            with open(p_idx, encoding="utf-8") as f:
                menages = int(json.load(f).get("n") or 0)
        except Exception:
            menages = None
    if not menages and bases:
        menages = max(set(bases), key=bases.count)

    return {"indice": moyenne("Total", scores), "n_scores": len(scores),
            "n_commun": len(commun), "sections": ordre, "dims": dims,
            "faits": faits, "menages": menages, "bandes": bandes,
            "paysages": paysages}


@st.cache_data(show_spinner=False)
def _actions():
    """L'effet du portefeuille, emprunté au moteur des fiches d'intervention.

    Importé ici et pas en tête de module : si le graphe causal manque, la page
    d'accueil doit continuer de s'afficher sans lui.
    """
    try:
        import note_bailleurs
        t = note_bailleurs._tout()
        if not t:
            return None
        return {"delta": t["portefeuille"]["delta"],
                "n": len(t["fiches"]),
                "lot1": len(t["lot1"]["ids"]),
                "part_lot1": (t["lot1"]["eff"]["delta"] / t["portefeuille"]["delta"]
                              * 100) if t["portefeuille"]["delta"] else 0}
    except Exception:
        return None


def _icone(nom, couleur):
    return (f'<div class="po-i" style="background:{couleur}17;color:{couleur}">'
            + icones.svg(nom, couleur=couleur, taille=19) + '</div>')


def _carte(icone, couleur, valeur, libelle, sous=""):
    return ('<div class="po-c">' + _icone(icone, couleur)
            + f'<div class="po-n">{_e(valeur)}</div>'
            + f'<div class="po-l">{_e(libelle)}</div>'
            + (f'<div class="po-s">{_e(sous)}</div>' if sous else "")
            + '</div>')


def _aller(mode):
    st.session_state["app_mode"] = mode


def _bouger(delta):
    st.session_state["portail_etape"] = max(
        1, min(4, st.session_state.get("portail_etape", 1) + delta))


def _poser(n):
    st.session_state["portail_etape"] = n


# --------------------------------------------------------------- les écrans
def _ecran_1(m):
    st.markdown(f'<div class="po-h">{_e(T("po_1_t"))}</div>'
                f'<p class="po-x">{_e(T("po_1_x"))}</p>',
                unsafe_allow_html=True)
    g, d = st.columns([1.45, 1], gap="large")
    with g:
        st.markdown(
            '<div class="po-g po-serre">'
            + _carte("personnes", BLEU,
                     f'{m["menages"]:,}'.replace(",", " ") if m["menages"] else "—",
                     T("po_1_c1"))
            + _carte("carte", VERT, str(len(SECTIONS)), T("po_1_c2"))
            + _carte("epingle", AMBRE, "2", T("po_1_c3"), T("po_1_c3x"))
            + '</div>', unsafe_allow_html=True)
    with d:
        try:
            import territoire_page
            v = territoire_page._vignette(territoire_page._geo(), 300, 300)
            if v:
                st.markdown(v, unsafe_allow_html=True)
                st.caption(T("po_1_carte"))
        except Exception:
            pass


def _ecran_2(m):
    st.markdown(f'<div class="po-h">{_e(T("po_2_t"))}</div>'
                f'<p class="po-x">{_gras(T("po_2_x"))}</p>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="po-g">' + "".join(
            _carte(ic, c, T(k), T(k + "x"))
            for k, ic, c in (("po_2_a1", "loupe", BLEU),
                             ("po_2_a2", "bouclier", AMBRE),
                             ("po_2_a3", "rafraichir", VERT)))
        + '</div>', unsafe_allow_html=True)

    n_ind = sum(e["n"] for e in m["dims"].values())
    cases = [("3", T("po_2_f1"), ""),
             (str(len(m["dims"])), T("po_2_f2"), ""),
             (str(n_ind), T("po_2_f3"), T("po_2_f3x", f=m["n_scores"])),
             ("0–10", T("po_2_f4"), "")]
    blocs = []
    for i, (v, lab, sous) in enumerate(cases):
        if i:
            blocs.append('<div class="po-ch">&rsaquo;</div>')
        blocs.append(f'<div class="po-f"><div class="po-n">{_e(v)}</div>'
                     f'<div class="po-l">{_e(lab)}</div>'
                     + (f'<div class="po-s">{_e(sous)}</div>' if sous else "")
                     + '</div>')
    st.markdown('<div class="po-flux">' + "".join(blocs) + '</div>',
                unsafe_allow_html=True)

    st.markdown(f'<div class="po-lab">{_e(T("po_2_src"))}</div>'
                '<div class="po-g" style="margin-top:0">' + "".join(
                    _carte(ic, c, T(k), T(k + "x"))
                    for k, ic, c in (("po_2_s1", "personnes", BLEU),
                                     ("po_2_s2", "carte", VERT),
                                     ("po_2_s3", "maison", AMBRE)))
                + '</div>', unsafe_allow_html=True)


def _couleur(v):
    return ROUGE if v < 3.5 else (AMBRE if v < 5 else VERT)


def _ecran_3(m):
    idx = m["indice"] or 0
    haut, bas = m["sections"][0], m["sections"][-1]
    ecart = (haut[1] or 0) - (bas[1] or 0)

    st.markdown(f'<div class="po-h">{_e(T("po_3_t"))}</div>',
                unsafe_allow_html=True)
    st.markdown(
        f'<div class="po-c" style="max-width:none">'
        f'<div class="po-l" style="font-size:11px;letter-spacing:.09em;'
        f'text-transform:uppercase;color:#8a93a5;margin:0">'
        f'{_e(T("po_3_idx"))}</div>'
        f'<div class="po-n" style="font-size:46px;color:{_couleur(idx)}">'
        f'{_f(idx)}<span style="font-size:20px;color:#8a93a5"> / 10</span></div>'
        f'<div class="po-j"><div class="po-jr" style="width:{idx * 10:.1f}%;'
        f'background:{_couleur(idx)}"></div></div>'
        f'<div class="po-s">{_e(T("po_3_idx_x", n=m["n_scores"]))}</div>'
        f'</div>', unsafe_allow_html=True)

    # LA DISTRIBUTION, JUSTE SOUS LA MOYENNE. C'est la contextualisation qui
    # manquait le plus : un indice composite sans distribution se lit comme un
    # niveau homogène, et celui-ci ne l'est pas du tout.
    st.markdown(f'<div class="po-lab">{_e(T("po_3_rep_t"))}</div>',
                unsafe_allow_html=True)
    pmax = max((b_["part"] for b_ in m["bandes"]), default=1) or 1
    cols = st.columns(len(m["bandes"]), gap="small")
    for col, b_ in zip(cols, m["bandes"]):
        with col:
            st.markdown(
                f'<div style="text-align:center">'
                f'<div style="height:96px;display:flex;align-items:flex-end;'
                f'justify-content:center">'
                f'<div style="width:100%;height:{max(b_["part"] / pmax * 100, 3):.0f}%;'
                f'background:{_couleur(b_["milieu"])};border-radius:5px 5px 0 0"'
                f' title="{_e(b_["lab"])} — {_f(b_["part"], 1)} %"></div></div>'
                f'<div style="border-top:1px solid #e6ecf4;padding-top:5px;'
                f'font-size:13px;font-weight:700;color:{ENCRE}">'
                f'{_f(b_["part"], 0)} %</div>'
                f'<div style="font-size:11.5px;color:{ENCRE3}">'
                f'{_e(b_["lab"])} / 10</div></div>', unsafe_allow_html=True)
    st.caption(T("po_3_rep_ax"))
    # NOMS EXPLICITES, ET C'EST UN BOGUE QUI L'A IMPOSÉ : `bas` et `haut`
    # désignaient déjà, dix lignes plus haut, les deux sections extrêmes. Les
    # réutiliser pour des parts de poids écrasait les tuples et la page tombait
    # sur « cannot unpack non-iterable float ».
    part_bas = sum(b_["part"] for b_ in m["bandes"] if b_["milieu"] <= 2)
    part_haut = sum(b_["part"] for b_ in m["bandes"] if b_["milieu"] >= 9)
    st.markdown(f'<p class="po-x" style="margin-top:8px">'
                f'{_gras(T("po_3_rep", n=m["n_scores"], bas=_f(part_bas, 0), haut=_f(part_haut, 0)))}</p>',
                unsafe_allow_html=True)

    st.markdown(f'<div class="po-lab">{_e(T("po_3_amp_t"))}</div>'
                f'<p class="po-x">{_gras(T("po_3_amp", d=_f(ecart)))}</p>',
                unsafe_allow_html=True)
    g, mid, d = st.columns([1, 0.25, 1], vertical_alignment="center")
    for col, (nom, val), lab, coul in ((g, haut, T("po_3_haut"), VERT),
                                       (d, bas, T("po_3_bas"), ROUGE)):
        with col:
            st.markdown(
                f'<div class="po-c" style="border-top:3px solid {coul}">'
                f'<div class="po-s" style="margin:0">{_e(lab)}</div>'
                f'<div class="po-n" style="font-size:26px;margin-top:4px">'
                f'{_e(nom)}</div>'
                f'<div class="po-l" style="color:{coul};font-size:19px;'
                f'font-weight:700">{_f(val)} / 10</div></div>',
                unsafe_allow_html=True)
    with mid:
        st.markdown(f'<div style="text-align:center;font-size:13px;'
                    f'font-weight:700;color:{ENCRE3}">{_f(ecart)} pts</div>',
                    unsafe_allow_html=True)
    st.caption(T("po_3_base", n=m["n_commun"]))

    if m["paysages"].get("Littoral") and m["paysages"].get("Montagne"):
        st.markdown(
            f'<div class="po-lab">{_e(T("po_3_pay_t"))}</div>'
            '<div class="po-g" style="margin-top:0">' + "".join(
                f'<div class="po-c" style="flex:1 1 200px">'
                f'<div class="po-s" style="margin:0">{_e(lab)}</div>'
                f'<div class="po-n" style="font-size:29px;color:'
                f'{_couleur(m["paysages"][cle])}">{_f(m["paysages"][cle])}'
                f'<span style="font-size:15px;color:#8a93a5"> / 10</span>'
                f'</div></div>'
                for cle, lab in (("Littoral", T("po_3_littoral")),
                                 ("Montagne", T("po_3_montagne"))))
            + '</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="po-lab">{_e(T("po_3_dims"))}</div>',
                unsafe_allow_html=True)
    lignes = []
    for cle in ("dim1", "dim2", "dim3", "dim4", "dim5", "dim6", "dim7"):
        e = m["dims"].get(cle)
        if not e:
            continue
        v = e["score"]
        lignes.append(
            f'<div class="po-bar"><div class="po-nom">{_e(T(cle))}</div>'
            f'<div class="po-bp"><div class="po-bf" style="width:'
            f'{(v or 0) * 10:.1f}%;background:{TEINTES[cle]}"></div></div>'
            f'<div class="po-val" style="color:{ENCRE2}">'
            f'{_f(v, 1) if v is not None else "—"}</div></div>')
    st.markdown("".join(lignes), unsafe_allow_html=True)
    st.caption(T("po_3_dim7"))

    st.markdown(f'<div class="po-lab">{_e(T("po_3_faits"))}</div>'
                '<div class="po-g" style="margin-top:0">' + "".join(
                    f'<div class="po-c" style="border-left:3px solid '
                    f'{TEINTES.get(x["dim"], GRIS)}">'
                    f'<div class="po-n" style="font-size:27px;color:'
                    f'{_couleur(x["score"])}">'
                    f'{_f(x["valeur"], 1) if isinstance(x["valeur"], (int, float)) else "—"}'
                    f'<span style="font-size:15px;color:#8a93a5"> '
                    f'{_e(x["unite"])}</span></div>'
                    f'<div class="po-l">{_e(x["nom"])}</div>'
                    f'<div class="po-s">{_f(x["score"], 0)} / 10</div></div>'
                    for x in m["faits"])
                + '</div>', unsafe_allow_html=True)


def _ecran_4(m):
    a = _actions()
    st.markdown(f'<div class="po-h">{_e(T("po_4_t"))}</div>',
                unsafe_allow_html=True)
    if a:
        avant = m["indice"] or 0
        apres = avant + a["delta"]
        st.markdown(f'<p class="po-x">'
                    f'{_e(T("po_4_x", a=_f(avant), b=_f(apres)))}</p>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="po-flux">'
            f'<div class="po-f"><div class="po-n">{_f(avant)}</div>'
            f'<div class="po-l">{_e(T("po_3_idx"))}</div></div>'
            f'<div class="po-ch">&rsaquo;</div>'
            f'<div class="po-f" style="border-color:#cfe6da">'
            f'<div class="po-n" style="color:{VERT}">'
            f'{_f(a["delta"], 3, signe=True)}</div>'
            f'<div class="po-l">{_e(T("po_4_gain"))}</div></div>'
            f'<div class="po-ch">&rsaquo;</div>'
            f'<div class="po-f"><div class="po-n">{_f(apres)}</div>'
            f'<div class="po-l">{_e(T("po_3_idx"))}</div></div>'
            '</div>', unsafe_allow_html=True)
        st.markdown(f'<p class="po-x" style="margin-top:14px">'
                    f'{_gras(T("po_4_lot", n=a["lot1"], t=a["n"], p=_f(a["part_lot1"], 0)))}</p>',
                    unsafe_allow_html=True)

    st.markdown(f'<div class="po-lab">{_e(T("po_4_portes"))}</div>',
                unsafe_allow_html=True)
    portes = [("po_4_p1", "bailleurs"), ("po_4_p2", "actions"),
              ("po_4_p3", "dimensions"), ("po_4_p4", "accueil")]
    for i in range(0, len(portes), 2):
        cols = st.columns(2, gap="medium")
        for col, (cle, mode) in zip(cols, portes[i:i + 2]):
            with col:
                st.button(T(cle), key=f"po_porte_{mode}",
                          on_click=_aller, args=(mode,),
                          use_container_width=True)


# ----------------------------------------------------------------- la page
def render():
    st.markdown(STYLE, unsafe_allow_html=True)
    st.session_state.setdefault("portail_etape", 1)
    n = st.session_state["portail_etape"]

    st.markdown(
        f'<h2 style="font-size:27px;font-weight:700;color:{ENCRE};'
        f'letter-spacing:-.02em;margin:2px 0 0">{_e(T("po_titre"))}</h2>'
        f'<p style="font-size:12.5px;color:{ENCRE3};letter-spacing:.06em;'
        f'text-transform:uppercase;margin:2px 0 0;font-weight:600">'
        f'{_e(T("po_sous"))}</p>', unsafe_allow_html=True)

    # LES QUATRE BOUTONS SONT LA BARRE D'ÉTAPES, et on peut sauter directement
    # à l'un d'eux : un parcours qui ne se parcourt que dans l'ordre est une
    # prison, pas un guide. Le numéro est dans le libellé — un bandeau
    # décoratif au-dessus des mêmes quatre mots faisait doublon.
    cols = st.columns(4)
    for i, (col, cle) in enumerate(zip(cols, ETAPES), 1):
        with col:
            st.button(f"{i} · {T(cle)}", key=f"po_pas_{i}",
                      on_click=_poser, args=(i,), use_container_width=True,
                      type="primary" if i == n else "secondary")

    m = _mesures(i18n.get_lang())
    if not m:
        st.info(T("po_absent"))
        return

    with st.container(border=True):
        (_ecran_1, _ecran_2, _ecran_3, _ecran_4)[n - 1](m)

    g, _milieu, d = st.columns([1.6, 4, 1.6])
    with g:
        if n > 1:
            st.button("← " + T("po_precedent"), key="po_prec",
                      on_click=_bouger, args=(-1,), use_container_width=True)
    with d:
        if n < 4:
            st.button(T("po_suivant") + " →", key="po_suiv",
                      on_click=_bouger, args=(1,), use_container_width=True,
                      type="primary")
