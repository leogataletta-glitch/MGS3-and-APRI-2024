"""Export of the "Correlations" tab (section Analyser les résultats).

Run from the site root:  python3 outils/export_resultats_liens.py   (about 15 min, 2 cores)

Streamlit (correlations_simples.py) works on the household microdata. Here every
outcome the static page offers, ONE question and ONE answer, is precomputed:

  questions.json      the questions, their usable answers, outcome counts, themes
  q/<i>.json          per question, per answer: breakdown by the five profile
                      variables (counts, chi-square, clustered bootstrap test for
                      two-group variables) and the eligible profile associations
                      (counts, raw bootstrap p) from which the page applies Holm on
                      the family the reader selects
  x/<i>.json          per question: crossing with every other question (counts,
                      chi-square, bootstrap test for two-group crossings)
  general.json        the survey-wide ranking (correlations_generales.py): the top
                      ten of every theme x profile variables x combination x
                      ranking criterion the page offers

Privacy: aggregates only; a group of fewer than 5 households is written n = -1
with no count. Test statistics are computed on the full table before suppression.
"""
import hashlib
import itertools
import json
import math
import os
import sys
from multiprocessing import Pool

SITE = os.path.abspath(os.getcwd())
sys.path.insert(0, '/tmp/work')
os.chdir('/tmp/work')

import numpy as np  # noqa: E402
import streamlit as st  # noqa: E402

st.session_state['lang'] = 'fr'
import i18n  # noqa: E402
import croisement_moteur as M  # noqa: E402
import liens_profils as LP  # noqa: E402
import liens_inference as I  # noqa: E402
import croisement_variable as CV  # noqa: E402
import correlations_simples as C  # noqa: E402
import themes_enquete as TH  # noqa: E402
import libelles_enquete as L  # noqa: E402

OUT = os.path.join(SITE, 'data', 'resultats', 'liens')
SEUIL = 5
RAISONS = ['ok', 'sample', 'sections', 'missing_section', 'support', 'degenerate']

cat = M.charger()
N = cat['n']
SEC = I.section_ids(cat)


def en(fn, *a):
    st.session_state['lang'] = 'en'
    try:
        return fn(*a)
    finally:
        st.session_state['lang'] = 'fr'


def ecrire(chemin, obj):
    p = os.path.join(OUT, chemin)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, separators=(',', ':'))
    return os.path.getsize(p)


def r(x, d=4):
    if x is None:
        return None
    x = float(x)
    return None if not math.isfinite(x) else round(x, d)


def pcode(res):
    """Raw bootstrap p as the integer number of draws (p = c / 1024), -1 if none."""
    p = res.get('p')
    if p is None or not np.isfinite(p):
        return -1
    return int(round(p * res.get('draws', 1024)))


# --------------------------------------------------------------- questions
QS = [q for q in cat['questions'] if len(LP.answers(cat, q)[0]) > 1]
ANS = {q['i']: LP.answers(cat, q) for q in QS}
codes = [c for c in [c for c, _, _ in TH.THEMES] + [TH.CALCULE, TH.AUTRES]
         if any(TH.theme_de(q.get('category')) == c for q in QS)]
themes = [{'code': c, 'fr': i18n.DICO[TH.libelle(c)]['fr'], 'en': i18n.DICO[TH.libelle(c)]['en']} for c in codes]

PROFILS = ['sexe', 'paysage', 'age', 'richesse', 'section']
REG = {d: LP.registry(cat, d) for d in PROFILS}
valeurs = {}
for d in PROFILS:
    for v in REG[d][0]:
        valeurs[v] = {'fr': L.modalite(v), 'en': en(L.modalite, v)}

# profile candidates of the ranking, canonical order (all four variables, mixed)
CANDS = list(C.profile_candidates(cat))
cand_meta = [{'d': list(c['dims']), 'l': list(c['labels'])} for c in CANDS]


def khi2(rows):
    s = CV.khi2(rows)
    if s is None:
        return None
    return [r(s['stat'], 3), s['df'], r(s['p'], 5), r(s['v'], 4), 1 if s['faible'] else 0]


def table(y, common, groups):
    """Rows of a crossing, suppression applied, plus what the page needs to say."""
    rows = CV.tableau(y, common, groups)
    n = int(common.sum())
    k = int((y & common).sum())
    out = {'n': n, 'k': k}
    out['g'] = [[g, (rr['n'] if rr['n'] >= SEUIL else -1), (rr['cas'] if rr['n'] >= SEUIL else None)]
                for g in groups for rr in rows if rr['groupe'] == g]
    if len(rows) < 2:
        return out, None
    over = int(sum(int((common & m).sum()) for m in groups.values())) > n
    if over:
        out['over'] = 1
        return out, None
    out['kh'] = khi2(rows)
    if out['kh'] is None:
        return out, None
    if len(rows) == 2:
        z = common & groups[rows[0]['groupe']]
        return out, (y, z, common)
    return out, None


TACHES = []      # (key, y, z, common) bootstrap tests to run


def tester(args):
    key, y, z, common = args
    res = I.test(y[common], z[common], SEC[common])
    return key, r(res['phi'], 5), pcode(res), RAISONS.index(res['reason']) if res['reason'] in RAISONS else 1


def lancer():
    global TACHES
    if not TACHES:
        return {}
    # cheap ones (sample too small) are done inline
    rapides, lents = [], []
    for t in TACHES:
        _k, y, z, c = t
        yy, zz = y[c], z[c]
        n, a, b = int(c.sum()), int(yy.sum()), int(zz.sum())
        (lents if min(a, n - a, b, n - b) >= 30 else rapides).append(t)
    out = {}
    for t in rapides:
        key, phi, pc, rs = tester(t)
        out[key] = (phi, pc, rs)
    with Pool(2) as pool:
        for key, phi, pc, rs in pool.imap_unordered(tester, lents, chunksize=64):
            out[key] = (phi, pc, rs)
    TACHES = []
    return out


# ------------------------------------------------- per question: profile crossings
print('questions', len(QS))
qfichiers = {}
for q in QS:
    masks, base = ANS[q['i']]
    par_rep = []
    for a, y in masks.items():
        ent = {}
        for d in PROFILS:
            gm, gb = REG[d]
            t, test = table(y, base & gb, gm)
            if test:
                TACHES.append(((q['i'], a, d), *test))
            ent[d] = t
        par_rep.append(ent)
    qfichiers[q['i']] = par_rep
res = lancer()
for q in QS:
    for a, ent in zip(ANS[q['i']][0], qfichiers[q['i']]):
        for d in ('sexe', 'paysage'):
            if (q['i'], a, d) in res:
                ent[d]['t'] = list(res[(q['i'], a, d)])
print('profile crossings done')


# ------------------------------------------------- per outcome: profile ranking
def signature(common, z):
    return hashlib.md5(common.tobytes() + z.tobytes()).hexdigest()


lignes_rang = {}      # (qid, answer) -> list of [pid, both, b, sig, key]
for q in QS:
    masks, base = ANS[q['i']]
    for a, y in masks.items():
        k, n = int(y.sum()), int(base.sum())
        if min(k, n - k) < 30:
            continue
        rows, sigs = [], {}
        for pid, it in enumerate(CANDS):
            common = base & it['base']
            z = it['mask'] & common
            nn = int(common.sum()); aa = int((y & common).sum()); bb = int(z.sum())
            both = int((y & z).sum())
            if min(aa, nn - aa, bb, nn - bb) < 30:
                continue
            phi = (nn * both - aa * bb) / np.sqrt(float(aa * (nn - aa) * bb * (nn - bb)))
            if abs(phi) >= 1 - 1e-12:
                continue
            s = signature(common, z)
            first = sigs.setdefault(s, pid)
            rows.append([pid, both, bb, nn, aa, first])
            if first == pid:
                TACHES.append(((q['i'], a, pid), y, z, common))
        lignes_rang[(q['i'], a)] = rows
print('ranking tests', len(TACHES))
res = lancer()
for (qi, a), rows in lignes_rang.items():
    for row in rows:
        _phi, pc, rs = res[(qi, a, row[5])]
        row.append(pc)
        row.append(rs)
print('ranking done')

# ------------------------------------------------- write q/<i>.json
taille = 0
for q in QS:
    out = []
    for a, ent in zip(ANS[q['i']][0], qfichiers[q['i']]):
        rows = lignes_rang.get((q['i'], a))
        if rows is not None:
            # [pid, both, b, n, a, sig, pcount, reason]
            ent = dict(ent, r=rows)
        out.append(ent)
    taille += ecrire(f'q/{q["i"]}.json', out)
print('q files', taille // 1024, 'KB')

# ------------------------------------------------- crossing with another question
taille = 0
xfichiers = {}
for q in QS:
    masks, base = ANS[q['i']]
    par_q2 = {}
    for q2 in QS:
        if q2['i'] == q['i']:
            continue
        g2, b2 = ANS[q2['i']]
        common = base & b2
        if not common.any():
            continue
        ent = []
        for a, y in masks.items():
            t, test = table(y, common, g2)
            if test:
                TACHES.append(((q['i'], q2['i'], a), *test))
            ent.append(t)
        # n and the group sizes are the same for every answer: written once
        par_q2[q2['i']] = ent
    xfichiers[q['i']] = par_q2
print('crossing tests', len(TACHES))
res = lancer()
# Compact layout, per other question q2:
#   [n, g, k, c, extra]  n = households answering both; g = size of each answer group
#   of q2 (in its answer order, 0 = empty, -1 = 1 to 4); k = per answer a of q, the
#   outcome count; c = per answer a, the count in each group (null if suppressed);
#   extra (optional) = {"o":1 multiple-response overlap, "kh":{a:[chi2, df, p, V,
#   weak]} only where a group is suppressed, "p":{a: bootstrap p as a count of the
#   1 024 draws} for two-group crossings where the test is computable, "phi":{a: phi}
#   only where a group is suppressed}.
for q in QS:
    out = {}
    for q2i, ent in xfichiers[q['i']].items():
        noms = list(ANS[q2i][0])
        taille_g = {g[0]: g[1] for g in ent[0]['g']}
        gl = [taille_g.get(v, 0) for v in noms]
        ks, cs, ex = [], [], {}
        for ai, (a, e) in enumerate(zip(ANS[q['i']][0], ent)):
            par = {g[0]: g[2] for g in e['g']}
            ks.append(e['k'])
            cs.append([par.get(v, 0) if taille_g.get(v, 0) != -1 else None for v in noms])
            if e.get('over'):
                ex['o'] = 1
            if e.get('kh') is not None and -1 in gl:
                ex.setdefault('kh', {})[ai] = e['kh']
            if (q['i'], q2i, a) in res:
                phi, pc, rs = res[(q['i'], q2i, a)]
                # the page computes phi from the counts; the bootstrap p is only
                # written when computable (no entry = "not computable")
                if pc >= 0:
                    ex.setdefault('p', {})[ai] = pc
                if -1 in gl and phi is not None:
                    ex.setdefault('phi', {})[ai] = phi
        row = [ent[0]['n'], gl, ks, cs]
        if ex:
            row.append(ex)
        out[q2i] = row
    taille += ecrire(f'x/{q["i"]}.json', out)
print('x files', taille // 1024, 'KB')

# ------------------------------------------------- questions.json
qmeta = []
for q in QS:
    masks, base = ANS[q['i']]
    qmeta.append({'i': q['i'], 'th': TH.theme_de(q.get('category')),
                  'q': {'fr': L.question(q['question']), 'en': en(L.question, q['question'])},
                  'a': [{'v': a, 'fr': L.modalite(a), 'en': en(L.modalite, a), 'k': int(y.sum())}
                        for a, y in masks.items()],
                  'n': int(base.sum())})
print('questions.json', ecrire('questions.json', {
    'themes': themes, 'questions': qmeta, 'profils': PROFILS,
    'groupes': {d: list(REG[d][0]) for d in PROFILS}, 'valeurs': valeurs,
    'candidats': cand_meta}) // 1024, 'KB')

# ------------------------------------------------- the survey-wide ranking
# Same rows as correlations_generales.scan: binary questions keep one answer,
# duplicates removed in canonical order, Holm over the whole family.
glob = []
outcomes = 0
for q in QS:
    masks, base = ANS[q['i']]
    labels = list(masks)
    if len(labels) == 2 and not (masks[labels[0]] & masks[labels[1]]).any():
        labels = ['Oui'] if 'Oui' in labels else labels[:1]
    for a in labels:
        rows = lignes_rang.get((q['i'], a))
        if rows is None:
            continue
        outcomes += 1
        vus = set()
        for pid, both, bb, nn, aa, sig, pc, rs in rows:
            if sig in vus:
                continue
            vus.add(sig)
            phi = (nn * both - aa * bb) / np.sqrt(float(aa * (nn - aa) * bb * (nn - bb)))
            glob.append({'qid': q['i'], 'a': a, 'pid': pid, 'phi': phi, 'n': nn, 'yes': both,
                         'with_n': bb, 'without_n': nn - bb, 'with_pct': 100 * both / bb,
                         'without_pct': 100 * (aa - both) / (nn - bb),
                         'p': (pc / 1024 if pc >= 0 else np.nan), 'rs': rs,
                         'theme': TH.theme_de(q.get('category')),
                         'dims': set(CANDS[pid]['dims'])})
for row, p in zip(glob, I.holm([g['p'] for g in glob])):
    row['p_holm'] = p
print('general rows', len(glob), 'outcomes', outcomes)

DIMS4 = ['sexe', 'paysage', 'age', 'richesse']
CRIT = ['strength', 'raw_low', 'raw_high', 'adjusted_low', 'adjusted_high']


def ordre(rows, crit):
    if crit == 'strength':
        return sorted(rows, key=lambda g: -abs(g['phi']))
    f = 'p_holm' if crit.startswith('adjusted') else 'p'
    sg = -1 if crit.endswith('high') else 1
    return sorted([g for g in rows if np.isfinite(g[f])], key=lambda g: (sg * g[f], -abs(g['phi'])))


idx_ref, ref_rows, combos = {}, [], {}
for th in ['__all__'] + codes:
    rows_th = [g for g in glob if th == '__all__' or g['theme'] == th]
    for size in range(1, 5):
        for ds in itertools.combinations(DIMS4, size):
            sel = set(ds)
            for comb in ('mixed', 'combined'):
                filt = [g for g in rows_th if (g['dims'] == sel if comb == 'combined' else g['dims'] <= sel)]
                for crit in CRIT:
                    rk = ordre(filt, crit)
                    ids = []
                    for g in rk[:10]:
                        key = id(g)
                        if key not in idx_ref:
                            idx_ref[key] = len(ref_rows)
                            ref_rows.append(g)
                        ids.append(idx_ref[key])
                    combos['|'.join([th, ''.join(str(DIMS4.index(d)) for d in ds), comb, crit])] = [len(filt), len(rk), ids]
lignes = [[g['qid'], g['a'], g['pid'], r(g['phi'], 5), g['yes'], g['with_n'], r(g['with_pct'], 3),
           r(g['without_pct'], 3), r(g['p'], 6), r(g['p_holm'], 6), g['rs']] for g in ref_rows]
print('general.json', ecrire('general.json', {'n_rows': len(glob), 'outcomes': outcomes,
                                              'rows': lignes, 'combos': combos}) // 1024, 'KB')
