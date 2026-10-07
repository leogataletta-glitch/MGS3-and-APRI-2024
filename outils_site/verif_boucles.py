"""Reference outputs of the Python engine, for the JavaScript port check.

python3 outils/verif_boucles.py <out.json>   (cwd = site root)
then: node outils/verif_boucles.mjs <out.json>
Runs the Streamlit functions (boucles_moteur, systeme_complexe, schema_exploration,
systeme_direct, systeme_page) on many inputs and stores their results.
"""
import json, os, sys, itertools, random
OUTP = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else 'verif_boucles_ref.json')
sys.path.insert(0, '/tmp/work'); os.chdir('/tmp/work')
import streamlit as st
st.session_state['lang'] = 'fr'
import numpy as np
import boucles_moteur as M
import systeme_complexe as SX
import systeme_direct as SD
import systeme_page as SP
import schema_exploration as SE

ref = {}
for lang in ('fr', 'en'):
    st.session_state['lang'] = lang
    SX._modele.clear()
    m = SX._modele(lang)
    R = ref[lang] = {}
    R['ids'] = m['ids']
    R['diag'] = m['diag']
    R['boucles'] = [[b['noeuds'], b['type'], b['force']] for b in m['boucles']]
    R['leviers'] = m['leviers']
    R['dominantes'] = M.boucles_dominantes(m['g'], m['boucles'], top=8)
    R['A'] = m['A'].tolist()
    # neighbourhoods, layouts, loops through the centre, levers table
    R['systemes'] = []
    for c in m['ids']:
        for n in SX.TAILLES:
            rang, aretes = SX._voisinage(m, c, n)
            pos = SX._positions(rang, c)[0]
            lay, groups = SE.causal_layout(list(pos), aretes, c)
            bcls = SX._boucles_de(m, c, set(rang))
            lev = []
            for lv in m['leviers']:
                if lv['id'] not in rang: continue
                eff = M.propager(m['g'], {lv['id']: 1.0})
                lev.append([lv['id'], sum(abs(v) for k, v in eff.items() if k != lv['id'])])
            lev.sort(key=lambda x: -x[1])
            R['systemes'].append({'c': c, 'n': n, 'rang': list(rang.items()),
                'aretes': [[a['de'], a['vers']] for a in aretes],
                'pos': {k: list(v) for k, v in pos.items()},
                'lay': {k: list(v) for k, v in lay.items()}, 'groups': groups,
                'bcls': [b['noeuds'] for b in bcls], 'lev': lev[:14]})
    R['direct'] = [SD._donnees(m, c, n) for c in ('eau', 'foret', 'revenu', 'prod_agri', 'sante', 'cuisson') for n in (5, 10, 20, 30)]
    R['regler'] = SP._systeme.__wrapped__(lang) if hasattr(SP._systeme, '__wrapped__') else SP._systeme(lang)
    R['regler'].pop('dims', None)
    R['correl'] = {a + '|' + b: SX._correlation(m, a, b) for a in m['ids'] for b in m['ids'] if a != b}

# scenarios (French names for par_qui)
st.session_state['lang'] = 'fr'
SX._modele.clear()
m = SX._modele('fr')
rnd = random.Random(7)
scen = [{i: 1.0} for i in m['ids']]
scen += [{'eau': 2.0, 'foret': -1.5}, {'revenu': 3.0, 'cuisson': 1.0, 'ocb': -2.0},
         {'prod_agri': -3.0}, {'foret': 0.5, 'pression_bois': 0.5, 'controle': 3.0, 'sante': -1.0}]
for _ in range(20):
    k = rnd.randint(1, 4)
    scen.append({i: rnd.choice([-3, -2.5, -2, -1.5, -1, -0.5, 0.5, 1, 1.5, 2, 2.5, 3]) for i in rnd.sample(m['ids'], k)})
ref['scen'] = []
for v in scen:
    eff = M.propager(m['g'], v)
    out = {'v': v, 'eff': eff, 'ind': M.effet_indice(m['g'], eff, v, m['par_ligne'])}
    out['etat'] = {p: M.etat_courant(m['g'], m['par_ligne'], p) for p, _l in SX.POPULATIONS}
    out['apres'] = {p: M.apres(out['etat'][p], eff, v) for p in ('Total', 'Femme', 'Cat A', 'Montagne')}
    vg, tot, conv, k = SX._vagues(m, v)
    out['vagues'] = [x.tolist() for x in vg]; out['conv'] = conv; out['k'] = k
    out['parqui'] = {i: SX._par_qui(m, i, v) for i in m['ids'] if i not in v}
    ref['scen'].append(out)

# ---- Monte Carlo reference (independent numpy implementation, own RNG):
# strengths drawn uniformly within their class, stability target in [0.5, 0.8],
# exact eigenvalues, exact inverse. The JS draws use another generator, so the
# comparison is statistical (shares of draws), the class-centre model is exact.
CLASSES = [(0.20, 0.125, 0.275), (0.35, 0.275, 0.425), (0.50, 0.425, 0.575), (0.65, 0.575, 0.725), (0.80, 0.725, 0.875)]
def classe(f):
    f = abs(f)
    for c in CLASSES:
        if f < c[2]: return c
    return CLASSES[-1]
g = M.charger()
ids = [n['id'] for n in g['noeuds']]; idx = {v: i for i, v in enumerate(ids)}; N = len(ids)
def matrice_forces(forces, cible):
    A = np.zeros((N, N))
    for e, fo in zip(g['aretes'], forces):
        A[idx[e['vers']], idx[e['de']]] = e['signe'] * fo
    r = float(max(abs(np.linalg.eigvals(A))))
    if r > cible: A = A * (cible / r)
    return A, r
def portees(A):
    T = np.linalg.inv(np.eye(N) - A)
    return np.abs(T).sum(axis=0) - np.abs(np.diag(T))
Ac, rc = matrice_forces([classe(e['force'])[0] for e in g['aretes']], 0.6)
ref['centrales'] = {'A': Ac.tolist(), 'rayon': rc, 'portee': portees(Ac).tolist()}
rng = np.random.default_rng(7)
ND = 2000
rangs = np.zeros((ND, N), dtype=int)
for d in range(ND):
    forces = [rng.uniform(classe(e['force'])[1], classe(e['force'])[2]) for e in g['aretes']]
    A, _ = matrice_forces(forces, rng.uniform(0.5, 0.8))
    p = portees(A)
    ordre = np.argsort(-p, kind='stable')
    rangs[d, ordre] = np.arange(1, N + 1)
ref['mc'] = {'ids': ids, 'n': ND, 'p_top3': (rangs <= 3).mean(axis=0).tolist(),
             'rang_med': np.median(rangs, axis=0).tolist()}

with open(OUTP, 'w') as f:
    json.dump(ref, f, ensure_ascii=False)
print('ok', OUTP)
