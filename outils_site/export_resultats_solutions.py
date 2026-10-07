"""Export of the tab "Variables les plus alarmantes / Most alarming variables"
(section Analyser les résultats, tab "solutions"): analyse_ecarts.render_alarmes.

Run from the site root:  python3 outils/export_resultats_solutions.py
Reads /tmp/work (read only), writes data/resultats/solutions/*.json.

Streamlit computes on household microdata for any profile built from five
optional registers (communal section, landscape, sex, age group, economic
category). The set is finite (11 x 3 x 3 x 5 x 4 = 1980 profiles), so every
profile is precomputed here as aggregates only:
  for the group: number of households; per indicator: score, value (share or
  mean), number of households in its base; for the rest of the cohort: score.
Privacy: a profile with fewer than 5 households is stored as {"n": "<5"} with
nothing else; an indicator whose base in the group has fewer than 5
households is stored as null (not shown); a rest-of-cohort score resting on
fewer than 5 households is stored as null.
One file per communal section choice (plus "tous"), keyed by
"paysage|sexe|age|richesse" ("" = all).
"""
import itertools
import json
import logging
import os
import sys
import warnings

SITE = os.path.abspath(os.getcwd())
OUT = os.path.join(SITE, "data", "resultats", "solutions")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, "/tmp/work")
os.chdir("/tmp/work")
warnings.filterwarnings("ignore")
logging.disable(logging.WARNING)

import numpy as np  # noqa: E402
import streamlit as st  # noqa: E402

st.session_state["lang"] = "fr"
import analyse_ecarts as A  # noqa: E402
import croisement_resultats as CR  # noqa: E402
import i18n  # noqa: E402

logging.disable(logging.WARNING)
SEUIL = 5


def deux(f):
    out = {}
    for l in ("fr", "en"):
        st.session_state["lang"] = l
        out[l] = f()
    st.session_state["lang"] = "fr"
    return out


cat = CR._catalogue()
inds = cat["indicateurs"]
N = cat["n"]

# ---- registers (in the order of the selectboxes), with labels
axes = []
for axe, lab in A.AXES:
    vals = [v for v in A._VALEURS.get(axe, []) if cat["groupes"].get(v) is not None]
    axes.append({"axe": axe, "lib": deux(lambda lab=lab: A.T(lab)),
                 "valeurs": [{"v": v, **deux(lambda v=v: A._lib(v))} for v in vals]})

meta = {
    "n_min": A.N_MIN, "seuil": SEUIL, "n_total": N,
    "axes": axes,
    "indicateurs": [{"ligne": i.get("ligne"), "fr": i.get("nom_fr") or i.get("nom"),
                     "en": i.get("nom") or i.get("nom_fr"), "moyenne": bool(i.get("moyenne"))}
                    for i in inds],
    "textes": {k: {"fr": v.get("fr"), "en": v.get("en")} for k, v in A.TEXTES.items()
               if k.startswith("al_") or k in ("ec_rien", "ec_fragile")},
}


def r(x, d=4):
    return None if x is None else round(float(x), d)


def mesures(masque, reste):
    lignes = []
    for ind in inds:
        m = A._mesure(ind, masque)
        if m["score"] is None:
            lignes.append(0)          # not computable (Streamlit skips it)
            continue
        if m["n"] < SEUIL:
            lignes.append(None)       # suppressed: fewer than 5 households
            continue
        x = [r(m["score"]), r(m["valeur"]), m["n"]]
        if reste is not None:
            a = A._mesure(ind, reste)
            x.append(r(a["score"]) if a["score"] is not None and a["n"] >= SEUIL else None)
        lignes.append(x)
    return lignes


g = cat["groupes"]
choix = [[None] + [v["v"] for v in ax["valeurs"]] for ax in axes]
par_section = {}
nb = 0
for combo in itertools.product(*choix):
    masque = np.ones(N, dtype=bool)
    actifs = [v for v in combo if v is not None]
    for v in actifs:
        masque &= g[v]
    n_g = int(masque.sum())
    sec = combo[0] or ""
    cle = "|".join(v or "" for v in combo[1:])
    if n_g == 0:
        e = {"n": 0}
    elif n_g < SEUIL:
        e = {"n": "<5"}
    else:
        reste = (~masque) if actifs else None
        e = {"n": n_g, "i": mesures(masque, reste)}
        if reste is not None:
            n_r = int(reste.sum())
            e["nr"] = n_r if n_r >= SEUIL else "<5"
    par_section.setdefault(sec, {})[cle] = e
    nb += 1

fichiers = {}
for k, (sec, d) in enumerate(par_section.items()):
    nom = "tous" if not sec else "s%02d" % k
    fichiers[sec] = nom
    with open(os.path.join(OUT, nom + ".json"), "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, separators=(",", ":"))
meta["fichiers"] = fichiers
with open(os.path.join(OUT, "meta.json"), "w", encoding="utf-8") as fh:
    json.dump(meta, fh, ensure_ascii=False, separators=(",", ":"))
print(nb, "profiles")
for f in sorted(os.listdir(OUT)):
    print(f, os.path.getsize(os.path.join(OUT, f)) // 1024, "KB")
