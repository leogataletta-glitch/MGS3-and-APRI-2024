"""Export of the data behind "Analyser les résultats > Résultats bruts".

Run from the site root:  python3 outils/export_resultats_brut.py

Reads the Streamlit repository in /tmp/work (read only) and writes
data/resultats/brut/*:
  menages.json        question index, themes, axes, interface texts (fr, en)
  q/<i>.json          one file per survey question: respondent counts per
                      answer for the whole sample and for every combination
                      of one to five breakdown criteria (aggregates only,
                      cells under 5 respondents suppressed)
  carte_fr.json/en    map skeleton of the ten communal sections
  satellite.json      satellite measurements by communal section + texts
  institutions.json   institutional declarations (DDAS and ORE)
  bio_rapport_2026.pdf  the published biodiversity report

PRIVACY. No household-level row leaves this script. Every number written for
the household survey is a count of respondents in a cell (a group defined by
section, sex, age group, economic category, landscape) and every cell with
1 to 4 respondents is replaced by -1 ("n < 5").
"""
import itertools
import json
import os
import re
import shutil
import sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SITE, "data", "resultats", "brut")
SRC = "/tmp/work"
sys.path.insert(0, SRC)
os.chdir(SRC)

import logging
logging.disable(logging.WARNING)
import streamlit as st  # noqa: E402

st.session_state["lang"] = "fr"

import numpy as np  # noqa: E402

import i18n  # noqa: E402
import croisement_moteur as M  # noqa: E402
import explorateur as E  # noqa: E402
import themes_enquete  # noqa: E402
import libelles_enquete  # noqa: E402
import map_render  # noqa: E402
import satellite_page as S  # noqa: E402
import environnement_cadre as EC  # noqa: E402
import recherche_questions  # noqa: E402

SEUIL = 5
LANGS = ("fr", "en")


def lang(l):
    st.session_state["lang"] = l


def both(fn):
    out = {}
    for l in LANGS:
        lang(l)
        out[l] = fn()
    lang("fr")
    return out


def ecrire(nom, obj):
    p = os.path.join(OUT, nom)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
    return os.path.getsize(p)


# --------------------------------------------------------------- fake st
class _Ctx:
    def __init__(self, cap, titre=None):
        self.cap, self.titre = cap, titre

    def __enter__(self):
        if self.titre is not None:
            self.cap.blocs.append({"titre": self.titre, "html": ""})
        return self

    def __exit__(self, *a):
        if self.titre is not None:
            self.cap.blocs.append({"titre": None, "html": ""})
        return False


class FauxSt:
    """Records what a Streamlit function writes, as HTML blocks."""

    def __init__(self):
        self.blocs = [{"titre": None, "html": ""}]

    def markdown(self, html, **kw):
        if "<style" in html:
            return
        self.blocs[-1]["html"] += html

    def expander(self, titre, **kw):
        return _Ctx(self, str(titre))

    def container(self, *a, **kw):
        return _Ctx(self)

    def columns(self, spec, **kw):
        n = spec if isinstance(spec, int) else len(spec)
        return [_Ctx(self) for _ in range(n)]

    def __getattr__(self, k):
        return lambda *a, **kw: None

    def propre(self):
        return [b for b in self.blocs if b["html"] or b["titre"]]


# =========================================================== household survey
def export_menages():
    cat = M.charger()
    questions = cat["questions"]
    n = cat["n"]
    axes = [a for a, _l in E.AXES]                       # display order
    valeurs = dict(M.REGISTRES)
    # index of each household on each axis
    idx = {}
    for a in axes:
        v = np.full(n, -1, dtype=np.int64)
        for j, val in enumerate(valeurs[a]):
            v[cat["groupes"][val]] = j
        assert (v >= 0).all(), a
        idx[a] = v

    sous = [()]
    for k in (1, 2, 3, 4, 5):
        sous += list(itertools.combinations(axes, k))    # canonical order

    def cube(bits_q, m):
        rep = np.zeros(n, dtype=bool)
        for j in range(m):
            rep |= bits_q[j]
        out = {}
        for s in sous:
            cle = "|".join(s)
            if s:
                tailles = [len(valeurs[a]) for a in s]
                cell = np.zeros(n, dtype=np.int64)
                for a, t in zip(s, tailles):
                    cell = cell * t + idx[a]
                ncell = int(np.prod(tailles))
            else:
                cell = np.zeros(n, dtype=np.int64)
                ncell = 1
            base = np.bincount(cell[rep], minlength=ncell)
            ks = [np.bincount(cell[bits_q[j] & rep], minlength=ncell)
                  for j in range(m)]
            lignes = []
            for c in range(ncell):
                b = int(base[c])
                if b == 0:
                    continue
                if b < SEUIL:
                    lignes.append([c, -1])
                else:
                    lignes.append([c, b] + [int(k[c]) for k in ks])
            out[cle] = lignes
        return out

    total = 0
    for q in questions:
        m = len(q["modalites"])
        bq = [cat["bits"][q["debut"] + j] for j in range(m)]
        total += ecrire(f"q/{q['i']}.json", {"i": q["i"], "c": cube(bq, m)})

    # ---- index
    cats = {x.get("category") or "" for x in questions}
    codes = themes_enquete.codes_presents(cats)
    par_theme = {}
    for q in questions:
        par_theme.setdefault(themes_enquete.theme_de(q.get("category")), []).append(q)

    def libs_par_theme():
        out = {}
        tous = E._libelles_liste(questions)
        th = {}
        for c, qs in par_theme.items():
            th.update(E._libelles_liste(qs))
        for q in questions:
            out[q["i"]] = {"a": tous[q["i"]], "t": th[q["i"]],
                           "m": E._module_court(q),
                           "mods": [libelles_enquete.modalite(x) for x in q["modalites"]]}
        return out

    L = both(libs_par_theme)
    qs = []
    for q in questions:
        qs.append({
            "i": q["i"], "th": themes_enquete.theme_de(q.get("category")),
            "q": q.get("question") or "", "c": q.get("category") or "",
            "a": {l: L[l][q["i"]]["a"] for l in LANGS},
            "t": {l: L[l][q["i"]]["t"] for l in LANGS},
            "m": {l: L[l][q["i"]]["m"] for l in LANGS},
            "r": {l: L[l][q["i"]]["mods"] for l in LANGS},
        })
    themes = [{"code": c,
               "fr": i18n.DICO[themes_enquete.libelle(c)]["fr"],
               "en": i18n.DICO[themes_enquete.libelle(c)]["en"],
               "dfr": i18n.DICO[themes_enquete.description(c)]["fr"],
               "den": i18n.DICO[themes_enquete.description(c)]["en"]}
              for c in codes]
    lib_val = {}
    for a in axes:
        for v in valeurs[a]:
            lib_val[v] = both(lambda v=v: E._lib(v))
    ax = [{"code": a, "lib": both(lambda c=c: i18n.T(c)),
           "vals": valeurs[a]} for a, c in E.AXES]
    textes = {k: {"fr": v.get("fr"), "en": v.get("en")}
              for k, v in i18n.DICO.items()
              if k.startswith(("ex_", "ra_src_", "moins_de", "intervalle",
                               "et_plus", "base_carte", "km"))
              and isinstance(v, dict)}
    notions = recherche_questions.NOTIONS
    idx_size = ecrire("menages.json", {
        "n": n, "seuil": SEUIL, "fragile": E.N_FRAGILE,
        "axes": ax, "libval": lib_val, "themes": themes, "questions": qs,
        "textes": textes, "notions": notions})
    return total, idx_size, len(questions)


# ================================================================ the map
def export_carte():
    secs = map_render.SECTIONS
    faux = {s: 10.1 + k for k, s in enumerate(secs)}     # "10,1" … "19,1"
    tailles = {}
    for l in LANGS:
        lang(l)
        svg, _t, mode = map_render.render_map_svg(
            faux, {s: 1 for s in secs}, [12, 14, 16], height=560,
            polarity="neutre", unite="%")
        tailles[l] = ecrire(f"carte_{l}.json", {
            "svg": svg, "sections": secs,
            "jetons": {s: map_render.fmt_val(v) + "%" for s, v in faux.items()},
            "ramps": {"neutre": map_render.RAMP_NEUTRAL,
                      "eleve_mauvais": map_render.ramp_for("eleve_mauvais"),
                      "eleve_bon": map_render.ramp_for("eleve_bon")}})
    lang("fr")
    return tailles


# ============================================================== satellite
def export_satellite():
    d = S._charger()
    dispo = [m for m in S.MESURES if d.get(m[3])]
    cats = [c for c in S.CATEGORIES if any(m[0] == c for m in dispo)]
    mesures = []
    for m in dispo:
        cat_, code, cle_lib, fichier, spec, unite, dec, pol = m
        src = d[fichier]
        ans = S._annees(src, spec.split(":")[1]) if spec.startswith("serie:") else []
        annees = list(reversed(ans)) if (ans and not spec.endswith(":delta")) else []
        par_annee = {}
        for a in (annees or [None]):
            vals, _a0, _a1 = S._valeurs(src, spec, a)
            if not vals:
                continue
            ens = (src.get("ensemble") or {}).get(spec) if not spec.startswith("serie:") else None
            moy = ens if ens is not None else (sum(vals.values()) / len(vals))
            par_annee[str(a) if a else "-"] = {
                "vals": vals, "moy": moy,
                "lib": both(lambda: S._libelle(cle_lib, m, src, a))}
        if not par_annee:
            continue
        per = (src or {}).get("periode") or (src or {}).get("periode_annees") or []
        cle_p = "sat_p_" + code
        lecture = ({l: i18n.DICO[cle_p].get(l) for l in LANGS}
                   if cle_p in i18n.DICO else None)
        # the dossier (source, method, scale) captured as HTML
        doss = {}
        vals0 = next(iter(par_annee.values()))["vals"]
        for l in LANGS:
            lang(l)
            f = FauxSt()
            vieux = S.st
            S.st = f
            try:
                S._dossier(m, vals0, unite, dec)
            finally:
                S.st = vieux
            doss[l] = f.propre()
        lang("fr")
        mesures.append({
            "cat": cat_, "code": code, "unite": unite, "dec": dec, "pol": pol,
            "annees": [str(a) for a in annees], "par": par_annee,
            "src": both(lambda: S._source(fichier, src)),
            "a0": per[0] if per else "", "a2": per[-1] if per else "",
            "lecture": lecture, "dossier": doss})
    textes = {k: {"fr": v.get("fr"), "en": v.get("en")}
              for k, v in i18n.DICO.items()
              if k.startswith(("sat_", "env_")) and isinstance(v, dict)
              and not k.startswith(("sat_p_", "sat_m_"))}
    textes["sat_intro_n"] = both(lambda: i18n.T("sat_intro", n=len(S.MESURES)))
    # the protocol (environnement_cadre.render_satellite), captured
    proto = {}
    for l in LANGS:
        lang(l)
        f = FauxSt()
        vieux = EC.st
        EC.st = f
        try:
            EC.render_satellite()
        finally:
            EC.st = vieux
        proto[l] = f.propre()
    lang("fr")
    return ecrire("satellite.json", {"cats": cats, "mesures": mesures,
                                     "textes": textes, "protocole": proto})


# =========================================================== institutions
def export_institutions():
    with open(os.path.join(SRC, "ddas_institutions.json"), encoding="utf-8") as f:
        ddas = json.load(f)
    with open(os.path.join(SRC, "ore_institutions.json"), encoding="utf-8") as f:
        ore = json.load(f)
    garder = ("section", "secteur", "question", "valeur", "questionnaire",
              "source", "feuille", "ligne", "colonne", "localisation")
    dd = [{k: r.get(k) for k in garder} for r in ddas["observations"]]
    og = ("id", "source", "page", "theme", "libelle", "valeur", "unite",
          "statut", "note", "periode")
    oo = [{k: r.get(k) for k in og} for r in ore["observations"]]
    return ecrire("institutions.json", {
        "ddas": dd, "ore": oo, "derives": ore.get("indicateurs_derives") or []})


def main():
    os.makedirs(OUT, exist_ok=True)
    tq, ti, nq = export_menages()
    print(f"menages: {nq} questions, {tq/1e6:.2f} MB of cubes, index {ti/1e3:.0f} kB")
    print("carte:", export_carte())
    print("satellite:", export_satellite())
    print("institutions:", export_institutions())
    shutil.copy(os.path.join(SRC, "bio_rapport_2026.pdf"),
                os.path.join(OUT, "bio_rapport_2026.pdf"))
    print("pdf copied")


if __name__ == "__main__":
    main()
