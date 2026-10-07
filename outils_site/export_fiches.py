"""Export of the "Fiches d'intervention / Intervention Profiles" section.

Run from the site root:  python3 outils/export_fiches.py
Reads the Streamlit repo in /tmp/work (read only) and writes data/fiches/*.json.

What is written (no survey microdata, only the causal model, the framework
scores already published and the drafted texts):
  data/fiches/fiches.json   texts (fr/en), levers, drafted profiles with their
                            computed figures, the target list, the search corpus,
                            the "recommendations for the future" block.
  data/fiches/cibles.json   for every target the UI offers (themes, dimensions,
                            the 128 framework lines): the levers that move it,
                            sorted, the levers working against it, the
                            integrated packages and the state of the line.
"""
import json
import logging
import os
import sys
import warnings

SITE = os.path.abspath(os.getcwd())
OUT = os.path.join(SITE, "data", "fiches")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, "/tmp/work")
os.chdir("/tmp/work")
warnings.filterwarnings("ignore")
logging.disable(logging.WARNING)

import streamlit as st  # noqa: E402

st.session_state["lang"] = "fr"
import boucles_moteur as M  # noqa: E402
import environnement_cadre as EC  # noqa: E402
import i18n  # noqa: E402
import interventions_page as I  # noqa: E402

logging.disable(logging.WARNING)


def r4(x, d=4):
    return None if x is None else round(float(x), d)


def deux(f):
    """Call f() in French then English, return {'fr':..., 'en':...}."""
    out = {}
    for l in ("fr", "en"):
        st.session_state["lang"] = l
        out[l] = f()
    st.session_state["lang"] = "fr"
    return out


graphe, par_ligne = I._charger()
lst_boucles = M.boucles(graphe)
fiches = I.calculer(graphe, par_ligne, lst_boucles)
par_id = {n["id"]: n for n in graphe["noeuds"]}
par_levier = {f["levier"]: f for f in fiches}
acts, props = I._activites(), I._propositions()


def nom_ligne(r):
    return {"fr": r.get("indicateur_fr") or r.get("indicateur", ""),
            "en": r.get("indicateur", "")}


# ---------------------------------------------------------------- texts
textes = {k: {"fr": v.get("fr"), "en": v.get("en")} for k, v in I.TEXTES.items()}
for k in ("dim1", "dim2", "dim3", "dim4", "dim5", "dim6", "dim7", "d_bouton",
          "env_v_terrain", "env_unite", "env_s0", "env_s10"):
    textes[k] = deux(lambda k=k: I.T(k))

# ---------------------------------------------------------------- levers
leviers = {}
for n in graphe["noeuds"]:
    nid = n["id"]
    leviers[nid] = {"fr": n.get("fr"), "en": n.get("en"), "dim": n.get("dim"),
                    "ligne": n.get("ligne"),
                    "prop": props.get(nid) or None,
                    "act": acts.get(nid) or None}

# order of the search corpus: Python iterates set(acts) | set(props); we keep
# the file order (ties between equal scores are the only thing it affects)
corpus = []
for nid in list(acts) + [p for p in props if p not in acts]:
    if nid in par_id and nid not in corpus:
        corpus.append(nid)

# ---------------------------------------------------------------- drafted profiles
fiches_out = []
for f in fiches:
    d = f["dec"]
    fiches_out.append({
        "id": f["id"], "levier": f["levier"], "cat": f["cat"],
        "meadows": f["meadows"], "faisabilite": f["faisabilite"],
        "horizon": f["horizon"], "cible": f["cible"],
        "mobilisation": f["mobilisation"], "delta": r4(f["delta"], 6),
        "part_couverte": r4(f["part_couverte"], 6), "depart": r4(f["depart"]),
        "boucles": f["boucles"], "renforcantes": f["renforcantes"],
        "equilibrantes": f["equilibrantes"], "bascule": f["bascule"],
        "dec": {"somme": r4(d["somme"], 6), "poids_total": r4(d["poids_total"], 6),
                "part_directe": r4(d["part_directe"], 6),
                "plafond": any(x["apres"] >= 9.999 for x in d["lignes"]),
                "lignes": [{"ligne": x["ligne"], "nom": nom_ligne(x["r"]),
                            "p": r4(x["p"]), "avant": r4(x["avant"]),
                            "apres": r4(x["apres"]), "ct": r4(x["ct"], 6)}
                           for x in d["lignes"][:8]]},
        "suivi": [{"ligne": r["ligne"], "nom": nom_ligne(r), "d": r4(dd)}
                  for _n, r, dd in f["suivi"]],
    })

# ---------------------------------------------------------------- targets
opts = deux(lambda: I._cibles(graphe, par_ligne))
codes = [c for c, _l in opts["fr"]]
libs_en = dict(opts["en"])
cibles_liste = [{"c": c, "fr": l, "en": libs_en[c]} for c, l in opts["fr"]]
ordre_en = [codes.index(c) for c, _l in opts["en"]]

tous = I._effets_leviers()
ligne_noeud = I._ligne_noeud(graphe)
resultats = {}
for cible in codes:
    out = {}
    if cible.startswith("l:"):
        lg = int(cible[2:])
        r = par_ligne.get(lg) or {}
        sc = (r.get("scores_corriges") or r.get("scores") or {}).get("Total")
        va = (r.get("valeurs") or {}).get("Total")
        un = "%" if (r.get("metrique") or "").strip().startswith(
            ("Households (%)", "Population (%)")) else ""
        out["etat"] = {"sc": r4(sc), "va": r4(va), "un": un,
                       "poids": r4(r.get("ponderation") or 0),
                       "hors": not ligne_noeud.get(lg)}
        nid = ligne_noeud.get(lg)
        if nid and (acts.get(nid) or props.get(nid)):
            out["direct"] = nid
    if cible.startswith("t:"):
        out["vars"] = [v for v in I.THEME_VARS.get(cible[2:], []) if v in par_id]
    cle_cible = cible[2:] if cible.startswith("n:") else None
    lot = []
    for lev, effets in tous.items():
        if lev == cle_cible:
            continue
        d_c = I._effet_sur(cible, effets, par_id, graphe, levier=lev)
        if abs(d_c) <= M.SEUIL_NUL:
            continue
        f = par_levier.get(lev)
        n = par_id.get(lev)
        if n is None:
            continue
        lot.append({"id": lev, "noeud": n, "fiche": f, "effet": d_c,
                    "cat": (f["cat"] if f else I.CAT_DE_DIM.get(n.get("dim") or "", "structurel"))})
    lot.sort(key=lambda x: -x["effet"])
    out["lot"] = [[x["id"], r4(x["effet"], 5), x["cat"]] for x in lot]
    if lot:
        paq = I._paquets(cible, lot, graphe, par_ligne, lst_boucles, par_id)
        out["paquets"] = [
            {"code": p["code"], "cases": [c["id"] for c in p["cases"]], "vide": p["vide"],
             **({} if p["vide"] else {"ensemble": r4(p["ensemble"], 5),
                                      "indice": r4(p["indice"], 6),
                                      "touchees": p["touchees"],
                                      "separees": p["separees"]})}
            for p in paq]
    resultats[cible] = out

# ---------------------------------------------------------------- the future
futur = {}
for l in ("fr", "en"):
    c = EC._contenu(l) or {}
    futur[l] = {"intro": (c.get("intro") or {}).get("menages", ""),
                "menages": c.get("menages") or [],
                "bareme": (c.get("intro") or {}).get("bareme", ""),
                "terrain": [{"nom": e["nom"], "unite": e["unite"], "s0": e["s0"],
                             "s10": e["s10"]} for e in (c.get("terrain") or [])]}

# ---------------------------------------------------------------- plans
dossier = "/tmp/work/data/plans"
plans = sorted(f for f in os.listdir(dossier) if not f.startswith(".")) \
    if os.path.isdir(dossier) else []

doc = {"textes": textes, "leviers": leviers, "corpus": corpus,
       "fiches": fiches_out, "cibles": cibles_liste, "ordre_en": ordre_en,
       "cat_de_dim": I.CAT_DE_DIM, "seuil_nul": M.SEUIL_NUL,
       "futur": futur, "plans": plans}
with open(os.path.join(OUT, "fiches.json"), "w", encoding="utf-8") as fh:
    json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
with open(os.path.join(OUT, "cibles.json"), "w", encoding="utf-8") as fh:
    json.dump(resultats, fh, ensure_ascii=False, separators=(",", ":"))
for n in ("fiches.json", "cibles.json"):
    print(n, os.path.getsize(os.path.join(OUT, n)) // 1024, "KB")
