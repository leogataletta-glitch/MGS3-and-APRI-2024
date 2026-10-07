#!/usr/bin/env python3
"""Estimate the links of the feedback-loop model on the APRI household panel.

RUN THIS LOCALLY, on the team's computer, never on the public site.
It reads the PRIVATE household files of survey round 1 and round 2, and writes
ONLY link-level results (one coefficient, its 95 % confidence interval, the
number of households and the matching strength class per link) to
data/boucles/estimations.json. No household-level value, identifier, name,
locality or GPS point is ever written.

Method (cross-lagged panel path model)
--------------------------------------
For every model variable V that is the effect of at least one testable link:

    V(round 2) = a + b_V * V(round 1) + sum over causes U of  c_UV * U(round 1) + e

* Each variable is first centred within its communal section (section fixed
  effects: households are only compared with their neighbours), then
  standardised (mean 0, sd 1) with the round-1 standard deviation.
* c_UV, the standardised cross-lagged path, is the estimated strength of the
  link U -> V once V's own past is held constant. It reads like a correlation
  and is mapped to the five strength classes with the |r| thresholds of the
  "How to read this model" tab: 0.10, 0.24, 0.37, 0.51.
* The equations together form a recursive path model (a structural equation
  model with observed variables). Engine, in order of preference:
  semopy (if installed) -> statsmodels OLS with HC1 robust errors -> numpy
  OLS with HC1 robust errors (always available).

A link is "testable" when both its ends are measured household by household
(see COLONNES below). Variables measured from satellites (forest, rain,
moisture, vegetation) are the same for all households of a section and are
absorbed by the section fixed effects: they cannot be estimated here.

Usage
-----
    python3 outils/estimer_panel.py --demo
        runs on a small synthetic panel (made-up households), prints the
        recovered links next to the true ones, and writes the result to a
        temporary file (not into the site).

    python3 outils/estimer_panel.py --vague1 R1.csv --vague2 R2.csv
        the real run. Writes data/boucles/estimations.json in the site.

Options: --sortie PATH (other output file), --min-menages N (default 100).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import sys
import tempfile

import numpy as np
import pandas as pd

# =====================================================================
# ======================  CONFIGURATION: EDIT HERE  ===================
# =====================================================================
# One row per household and per round, in two CSV files (round 1, round 2),
# already prepared with the APRI indicator pipeline: one column per model
# variable, coded so that a HIGHER value means MORE resilience (the same
# orientation as the model). Binary indicators (0/1) and scores both work.

ID_MENAGE = "id_menage"        # household code, identical in both rounds
SECTION = "section"            # communal section (for fixed effects)
SEPARATEUR = None              # None: guess ; or , automatically

# model variable id  ->  column name in BOTH round files.
# Put None (or delete the line) for a variable the survey does not measure.
COLONNES: dict[str, str | None] = {
    # I. Physical and infrastructural
    "eau":         "ind_eau",          # access to drinking water (line 4)
    "assain":      "ind_assain",       # safely managed sanitation (line 3)
    "elec":        "ind_elec",         # access to electricity (line 5)
    "cuisson":     "ind_cuisson",      # clean cooking fuels (line 6)
    "sante_acces": "ind_sante_acces",  # health facility within 30 min (line 15)
    "ecole":       "ind_ecole",        # primary school within 30 min (line 16)
    "abris":       "ind_abris",        # operational emergency shelters (line 14)
    "logement":    "ind_logement",     # housing structural quality (line 10)
    "mobile":      "ind_mobile",       # mobile network coverage (line 7)
    # II. Institutions and governance
    "alerte":      "ind_alerte",       # access to early warning (line 22)
    "comites":     "ind_comites",      # local disaster risk committees (line 28)
    "prepa":       "ind_prepa",        # participation in preparedness (line 23)
    "services":    "ind_services",     # satisfaction with public services (line 30)
    "etat_civil":  "ind_etat_civil",   # births registered (line 24)
    # IV. Economy and food security
    "emploi":      "ind_emploi",       # employment rate (line 76)
    "revenu":      "ind_revenu",       # income above the threshold (line 78)
    "reserve":     "ind_reserve",      # income reserve (line 81)
    "transferts":  "ind_transferts",   # remittance coverage (line 79)
    "compte":      "ind_compte",       # financial account (line 72)
    "foncier":     "ind_foncier",      # land tenure security (line 74)
    # V. Social and community
    "entraide":    "ind_entraide",     # bonding social capital (line 95)
    "passerelle":  "ind_passerelle",   # bridging social capital (line 96)
    "ocb":         "ind_ocb",          # membership of an organisation (line 27)
    "securite":    "ind_securite",     # sense of safety (line 90)
    # VI. Human
    "alimentaire": "ind_alimentaire",  # food security (line 108)
    "education":   "ind_education",    # primary education completed (line 107)
    "identite":    "ind_identite",     # national identity card (line 103)
    # Not measured household by household (keep None):
    # satellite: foret, pluie, aridite, vegetation
    # unmeasured: sante, travail, temps_eau, prod_agri, erosion, ...
}
MIN_MENAGES = 100              # below this, a link is not reported
# =====================================================================

ICI = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(ICI)
MODELE = os.path.join(SITE, "data", "boucles", "modele.json")
SORTIE = os.path.join(SITE, "data", "boucles", "estimations.json")
SEUILS_R = [0.10, 0.24, 0.37, 0.51]   # |r| class boundaries (= d 0.2, 0.5, 0.8, 1.2)
NOMS_CLASSES = ["très faible", "faible", "moyenne", "forte", "très forte"]


def classe_de_r(r: float) -> int:
    return 1 + sum(abs(r) >= s for s in SEUILS_R)


def classe_de_force(f: float) -> int:
    f = abs(f)
    for k, hi in enumerate([0.275, 0.425, 0.575, 0.725], start=1):
        if f < hi:
            return k
    return 5


# ---------------------------------------------------------------- data
def lire_modele():
    with open(MODELE, encoding="utf-8") as f:
        g = json.load(f)["graphe"]
    aretes = [a for a in g["aretes"] if not (a["de"] == "eau" and a["vers"] == "abris")]
    return g["noeuds"], aretes


def liens_testables(aretes, colonnes):
    ok = {k for k, v in colonnes.items() if v}
    return [a for a in aretes if a["de"] in ok and a["vers"] in ok]


def lire_vague(chemin):
    sep = SEPARATEUR
    if sep is None:
        with open(chemin, encoding="utf-8-sig") as f:
            tete = f.readline()
        sep = ";" if tete.count(";") >= tete.count(",") else ","
    return pd.read_csv(chemin, sep=sep, encoding="utf-8-sig", low_memory=False)


def panel(v1: pd.DataFrame, v2: pd.DataFrame, variables):
    """households present in both rounds; columns X_1 and X_2 per variable"""
    cols = [COLONNES[v] for v in variables]
    manq = [c for c in cols + [ID_MENAGE, SECTION] if c not in v1.columns or c not in v2.columns]
    if manq:
        sys.exit("Colonnes absentes d'un des deux fichiers / missing columns: " + ", ".join(manq))
    a = v1[[ID_MENAGE, SECTION] + cols].rename(columns={COLONNES[v]: v + "_1" for v in variables})
    b = v2[[ID_MENAGE] + cols].rename(columns={COLONNES[v]: v + "_2" for v in variables})
    p = a.merge(b, on=ID_MENAGE, how="inner")
    for c in p.columns:
        if c not in (ID_MENAGE, SECTION):
            p[c] = pd.to_numeric(p[c], errors="coerce")
    return p


def preparer(p: pd.DataFrame, variables):
    """section fixed effects (within-section centring), then standardise on round-1 sd"""
    q = p.copy()
    for v in variables:
        for r in ("_1", "_2"):
            c = v + r
            q[c] = q[c] - q.groupby(SECTION)[c].transform("mean")
        sd = q[v + "_1"].std()
        if not sd or not np.isfinite(sd):
            sd = q[v + "_2"].std() or 1.0
        for r in ("_1", "_2"):
            q[v + r] = q[v + r] / sd
    return q


# ---------------------------------------------------------------- engines
def _p_normal(z):
    return math.erfc(abs(z) / math.sqrt(2))


def ols_hc1(y: np.ndarray, X: np.ndarray):
    n, k = X.shape
    XtX_inv = np.linalg.pinv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    e = y - X @ beta
    meat = (X * e[:, None] ** 2).T @ X
    V = XtX_inv @ meat @ XtX_inv * n / max(n - k, 1)
    return beta, np.sqrt(np.clip(np.diag(V), 0, None))


def estimer_equation(d: pd.DataFrame, cible: str, causes: list[str], moteur: str):
    """returns {cause: (coef, se)} and n for V_2 ~ V_1 + causes_1"""
    cols = [cible + "_2", cible + "_1"] + [c + "_1" for c in causes]
    x = d[cols].dropna()
    n = len(x)
    if n < MIN_MENAGES:
        return None, n
    if moteur == "semopy":
        import semopy
        desc = f"{cible}_2 ~ " + " + ".join(cols[1:])
        mod = semopy.Model(desc)
        mod.fit(x)
        tab = mod.inspect()
        out = {}
        for c in causes:
            r = tab[(tab["lval"] == cible + "_2") & (tab["op"] == "~") & (tab["rval"] == c + "_1")].iloc[0]
            out[c] = (float(r["Estimate"]), float(r["Std. Err"]))
        return out, n
    y = x[cols[0]].to_numpy(float)
    X = np.column_stack([np.ones(n)] + [x[c].to_numpy(float) for c in cols[1:]])
    if moteur == "statsmodels":
        import statsmodels.api as sm
        res = sm.OLS(y, X).fit(cov_type="HC1")
        beta, se = np.asarray(res.params), np.asarray(res.bse)
    else:
        beta, se = ols_hc1(y, X)
    return {c: (float(beta[2 + i]), float(se[2 + i])) for i, c in enumerate(causes)}, n


def choisir_moteur():
    for m in ("semopy", "statsmodels"):
        try:
            __import__(m)
            return m
        except Exception:
            pass
    return "numpy"


# ---------------------------------------------------------------- main
def estimer(p: pd.DataFrame, liens, moteur: str):
    variables = sorted({a["de"] for a in liens} | {a["vers"] for a in liens})
    d = preparer(p, variables)
    par_cible: dict[str, list[str]] = {}
    for a in liens:
        par_cible.setdefault(a["vers"], []).append(a["de"])
    resultats = []
    for cible, causes in sorted(par_cible.items()):
        try:
            est, n = estimer_equation(d, cible, causes, moteur)
        except Exception as e:  # a failing engine falls back to numpy for this equation
            print(f"  {moteur} a échoué pour {cible} ({e}); numpy utilisé", file=sys.stderr)
            est, n = estimer_equation(d, cible, causes, "numpy")
        for c in causes:
            a = next(x for x in liens if x["de"] == c and x["vers"] == cible)
            ligne = {"de": c, "vers": cible, "n": int(n),
                     "classe_modele": classe_de_force(a["force"]), "signe_modele": a["signe"]}
            if est is None:
                ligne.update({"coef": None, "statut": f"moins de {MIN_MENAGES} ménages"})
            else:
                b, se = est[c]
                lo, hi = b - 1.96 * se, b + 1.96 * se
                cl, cl_lo, cl_hi = classe_de_r(b), classe_de_r(lo), classe_de_r(hi)
                exclut0 = lo > 0 or hi < 0
                # decision rule of the "How to read this model" tab
                if exclut0 and np.sign(b) != np.sign(a["signe"]):
                    statut = "signe contraire au modèle : à discuter"
                elif lo <= 0 <= hi:
                    statut = "non significatif : garder l'avis d'experts"
                elif abs(cl_lo - cl_hi) <= 1:
                    statut = "intervalle étroit : la classe mesurée remplace la classe d'experts"
                else:
                    statut = "intervalle large : garder l'avis d'experts"
                ligne.update({"coef": round(b, 4), "ic95": [round(lo, 4), round(hi, 4)],
                              "p": round(_p_normal(b / se) if se else 0.0, 5),
                              "classe_estimee": cl if exclut0 else 1,
                              "classes_ic": [min(cl_lo, cl_hi), max(cl_lo, cl_hi)] if exclut0 else None,
                              "statut": statut})
            resultats.append(ligne)
    return resultats


def ecrire(resultats, n_panel, moteur, chemin, demo, testables, total):
    # privacy guard: only link-level fields, nothing per household
    autorises = {"de", "vers", "n", "coef", "ic95", "p", "classe_estimee", "classes_ic",
                 "classe_modele", "signe_modele", "statut"}
    for r in resultats:
        assert set(r) <= autorises, "champ non autorisé dans la sortie"
        assert r["n"] >= MIN_MENAGES or r["coef"] is None
    out = {
        "genere": dt.date.today().isoformat(),
        "demo": bool(demo),
        "methode": "modèle de pistes croisé et décalé (panel 2 vagues), effets fixes de section, "
                   "coefficients standardisés, IC 95 % robustes (HC1)",
        "moteur": moteur,
        "n_menages_panel": int(n_panel),
        "min_menages": MIN_MENAGES,
        "seuils_r": SEUILS_R,
        "liens_testables": testables,
        "liens_total": total,
        "liens": resultats,
    }
    os.makedirs(os.path.dirname(os.path.abspath(chemin)), exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    return chemin


def donnees_demo(liens, n=800, sections=10, graine=2026):
    """a synthetic two-round panel generated FROM the model's own links,
    so that the script can be checked: the estimates should recover them"""
    rng = np.random.default_rng(graine)
    variables = sorted({a["de"] for a in liens} | {a["vers"] for a in liens})
    idx = {v: i for i, v in enumerate(variables)}
    W = np.zeros((len(variables), len(variables)))
    for a in liens:
        W[idx[a["vers"]], idx[a["de"]]] = a["signe"] * a["force"] * 0.35   # true lagged effects
    sec = rng.integers(0, sections, n)
    effet_sec = rng.normal(0, 0.5, (sections, len(variables)))
    x1 = rng.normal(0, 1, (n, len(variables))) + effet_sec[sec]
    x2 = 0.5 * x1 + x1 @ W.T + rng.normal(0, 0.8, (n, len(variables))) + effet_sec[sec]
    ids = [f"M{i:04d}" for i in range(n)]
    v1 = pd.DataFrame(x1, columns=[COLONNES[v] for v in variables]); v1[ID_MENAGE] = ids; v1[SECTION] = sec
    v2 = pd.DataFrame(x2, columns=[COLONNES[v] for v in variables]); v2[ID_MENAGE] = ids; v2[SECTION] = sec
    keep = rng.random(n) > 0.15            # 15 % attrition in round 2
    return v1, v2[keep], W, idx


def main():
    global MIN_MENAGES
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--vague1"); ap.add_argument("--vague2")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--sortie")
    ap.add_argument("--min-menages", type=int, default=MIN_MENAGES)
    a = ap.parse_args()
    MIN_MENAGES = a.min_menages

    _, aretes = lire_modele()
    liens = liens_testables(aretes, COLONNES)
    moteur = choisir_moteur()
    print(f"{len(liens)} liens testables sur {len(aretes)} ; moteur : {moteur}")

    if a.demo:
        v1, v2, W, idx = donnees_demo(liens)
        sortie = a.sortie or os.path.join(tempfile.gettempdir(), "apri_estimations_demo.json")
    else:
        if not (a.vague1 and a.vague2):
            ap.error("--vague1 et --vague2 sont requis (ou --demo)")
        v1, v2 = lire_vague(a.vague1), lire_vague(a.vague2)
        sortie = a.sortie or SORTIE

    variables = sorted({x["de"] for x in liens} | {x["vers"] for x in liens})
    p = panel(v1, v2, variables)
    print(f"{len(p)} ménages présents aux deux vagues")
    res = estimer(p, liens, moteur)
    chemin = ecrire(res, len(p), moteur, sortie, a.demo, len(liens), len(aretes))
    print("écrit :", chemin)

    if a.demo:   # check: does the estimate recover the true (standardised) sign and order?
        ok = sum(1 for r in res if r["coef"] is not None and np.sign(r["coef"]) == r["signe_modele"])
        print(f"signe retrouvé pour {ok} liens sur {len(res)}")
        print(f"{'lien':45s} {'vrai':>6s} {'estimé':>7s}  IC95")
        for r in sorted(res, key=lambda r: -abs(W[idx[r['vers']], idx[r['de']]]))[:12]:
            vrai = W[idx[r["vers"]], idx[r["de"]]]
            print(f"{r['de'] + ' -> ' + r['vers']:45s} {vrai:6.3f} {r['coef']:7.3f}  [{r['ic95'][0]:.3f}, {r['ic95'][1]:.3f}]  {r['statut']}")


if __name__ == "__main__":
    main()
