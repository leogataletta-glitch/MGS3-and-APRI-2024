"""Export of the "Resilience scores" and "Compare" tabs (section Analyser les résultats).

Run from the site root:  python3 outils/export_resultats_scores.py

What Streamlit computes on the household microdata for any filter combination is
precomputed here as aggregates on a finite grid of population masks:

  section   : all | one of the 10 communal sections                        (11)
  landscape : all | Littoral | Montagne                                      (3)
  sex       : all | Homme | Femme                                            (3)
  age       : any non-empty subset of the 4 age bands                        (15)
  wealth    : any non-empty subset of the 3 economic categories              (7)

= 10 395 masks. Every group the screens can draw (a breakdown cell intersected with
the population filters, a comparison profile) is one of these masks, so the browser
only looks values up. The one simplification against Streamlit: the population
filter on communal sections takes one section (or all), not an arbitrary union of
sections, because 1 023 section subsets would multiply the grid by 93.

Privacy: aggregates only. Any value computed on fewer than 5 households is
suppressed (written as null, with n = -1 meaning "1 to 4").
"""
import json
import os
import re
import sys

SITE = os.path.abspath(os.getcwd())
sys.path.insert(0, '/tmp/work')
os.chdir('/tmp/work')

import numpy as np  # noqa: E402
import streamlit as st  # noqa: E402

st.session_state['lang'] = 'fr'
import i18n  # noqa: E402
import croisement_moteur as M  # noqa: E402
import explorateur as E  # noqa: E402
import libelles_enquete as L  # noqa: E402
import map_render  # noqa: E402

OUT = os.path.join(SITE, 'data', 'resultats')
SEUIL = 5


def lang(l):
    st.session_state['lang'] = l


def both(fn):
    out = {}
    for l in ('fr', 'en'):
        lang(l)
        out[l] = fn()
    lang('fr')
    return out


def ecrire(chemin, obj):
    p = os.path.join(OUT, chemin)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, separators=(',', ':'))
    return os.path.getsize(p)


def r4(x, d=4):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), d)


cat = M.charger()
N = cat['n']
G = cat['groupes']

# ---------------------------------------------------------------- the mask grid
SECTIONS = list(M.SECTIONS)
SECS = [None] + SECTIONS                                  # 11
PAYS = [None, 'Littoral', 'Montagne']                     # 3
SEXES = [None, 'Homme', 'Femme']                          # 3
AGES = ['<25', '25-39', '40-59', '60+']                   # bitmask 1..15
RICH = ['Cat A', 'Cat B', 'Cat C']                        # bitmask 1..7
TOUT = np.ones(N, dtype=bool)
NMASQ = 11 * 3 * 3 * 15 * 7


def masque_union(vals, bits):
    m = np.zeros(N, dtype=bool)
    for j, v in enumerate(vals):
        if bits & (1 << j):
            m |= G[v]
    return m


def idx(sec, pay, sx, ab, rb):
    return ((((sec * 3 + pay) * 3 + sx) * 15 + (ab - 1)) * 7) + (rb - 1)


MASQUES = []
for sec in SECS:
    m0 = TOUT if sec is None else G[sec]
    for pay in PAYS:
        ml = m0 if pay is None else m0 & G[pay]
        for sx in SEXES:
            ms = ml if sx is None else ml & G[sx]
            for ab in range(1, 16):
                ma = ms & masque_union(AGES, ab)
                for rb in range(1, 8):
                    MASQUES.append(ma & masque_union(RICH, rb))
assert len(MASQUES) == NMASQ and idx(10, 2, 2, 15, 7) == NMASQ - 1

# ------------------------------------------------------------------ indicators
INDS = list(cat['indicateurs']) + list(cat.get('territoriaux') or [])
DIMS = [c for c, _l in M.DIMENSIONS]

# the scores of every target on every mask, in one pass of the engine
n_masque = []
dim_s = {d: [] for d in DIMS}
ind_s = [[] for _ in INDS]
ind_n = [[] for _ in INDS]
ind_r = [[] for _ in INDS]
for m in MASQUES:
    nb = int(m.sum())
    n_masque.append(nb if nb >= SEUIL or nb == 0 else -1)
    if nb < SEUIL:
        for d in DIMS:
            dim_s[d].append(None)
        for k in range(len(INDS)):
            ind_s[k].append(None)
            ind_n[k].append(0 if nb == 0 else -1)
            ind_r[k].append(None)
        continue
    lignes = M.profil(cat, m)
    ag = M.agreger(lignes)
    for d in DIMS:
        dim_s[d].append(r4(ag['dimensions'].get(d), 4))
    for k, it in enumerate(lignes):
        n = int(it['n'])
        if n < SEUIL:
            ind_s[k].append(None)
            ind_n[k].append(0 if n == 0 else -1)
            ind_r[k].append(None)
        else:
            ind_s[k].append(r4(it['score'], 4))
            ind_n[k].append(n)
            ind_r[k].append(r4(it['valeur'], 5 if INDS[k].get('ligne') == 53 else 2))

# The arrays only hold the masks of 5 households or more (meta 'n_masque' says
# which): the others are suppressed for every target anyway.
VALIDES = [i for i, nb in enumerate(n_masque) if nb >= SEUIL]


def compact(arr):
    return [arr[i] for i in VALIDES]


taille = 0
for d in DIMS:
    taille += ecrire(f'scores/cibles/d_{d}.json', {'s': compact(dim_s[d])})
for k in range(len(INDS)):
    taille += ecrire(f'scores/cibles/i_{k}.json', {'s': compact(ind_s[k]), 'n': compact(ind_n[k]),
                                                    'r': compact(ind_r[k])})
print('targets', len(DIMS) + len(INDS), 'files,', taille // 1024, 'KB')

# ---------------------------------------------------------------------- meta
poids_ref, nb_ref = E._poids_referentiel()
couv = M.couverture(cat)['poids']
dims_meta = []
for d in DIMS:
    men = [i for i in cat['indicateurs'] if i['dim'] == d]
    terr = [i for i in (cat.get('territoriaux') or []) if i['dim'] == d]
    pt = sum(i['poids'] for i in terr)
    pm = sum(i['poids'] for i in men)
    tot = poids_ref.get(d, 0.0)
    dims_meta.append({
        'code': d, 'nom': both(lambda: i18n.T(d)),
        'n_ind': len(men) + len(terr),
        'n_terr': len(terr),
        'part_terr': (100.0 * pt / (pt + pm)) if (pt + pm) else 0.0,
        'n_ref': nb_ref.get(d, 0),
        'couv': (100.0 * couv.get(d, 0.0) / tot) if tot else None,
    })

inds_meta = []
for k, ind in enumerate(INDS):
    unite = ind.get('unite') or ('' if ind.get('moyenne') or ind.get('territorial') else '%')
    inds_meta.append({'id': k, 'dim': ind['dim'],
                      'nom': {'fr': ind.get('nom_fr') or ind.get('nom'),
                              'en': ind.get('nom') or ind.get('nom_fr')},
                      'terr': bool(ind.get('territorial')), 'unite': unite,
                      'dec': 4 if ind.get('ligne') == 53 else 2})

CLES_LIB = {"Homme": "hommes", "Femme": "femmes", "Cat A": "cat_a",
            "Cat B": "cat_b", "Cat C": "cat_c", "<25": "age_25",
            "25-39": "age_25_39", "40-59": "age_40_59", "60+": "age_60",
            "Littoral": "pay_Littoral", "Montagne": "pay_Montagne"}
valeurs = {v: both(lambda v=v: i18n.T(c)) for v, c in CLES_LIB.items()}
for s in SECTIONS:
    valeurs[s] = {'fr': s, 'en': s}

textes = {c: {'fr': v.get('fr'), 'en': v.get('en')} for c, v in E.TEXTES.items()}
for c in ('moins_de', 'et_plus', 'intervalle', 'base_carte', 'km'):
    textes[c] = {'fr': i18n.DICO[c]['fr'], 'en': i18n.DICO[c]['en']}

meta = {
    'n': N, 'seuil': SEUIL,
    'grille': {'secs': SECS, 'pays': PAYS, 'sexes': SEXES, 'ages': AGES, 'rich': RICH},
    'registres': {a: list(dict(M.REGISTRES)[a]) for a in ('section', 'sexe', 'age', 'richesse', 'paysage')},
    'valeurs': valeurs,
    'n_masque': n_masque,
    'dims': dims_meta,
    'inds': inds_meta,
    'textes': textes,
    'n_fragile': E.N_FRAGILE,
}
print('meta', ecrire('scores/meta.json', meta) // 1024, 'KB')

# ------------------------------------------------------------------ the map
# Rendered once by the Streamlit map engine with a recognisable dummy value per
# section; the browser recolours the paths and rewrites the labels.
FACT = {s: v for s, v in zip(SECTIONS, [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 0.5])}
TXT = {map_render.fmt_val(v): s for s, v in FACT.items()}
svg, _T, mode = map_render.render_map_svg(FACT, {s: 1 for s in FACT}, [2, 4, 6],
                                          height=560, polarity='neutre', unite='')


def _path(mo):
    tete, titre = mo.group(1), mo.group(2)
    nom = titre.split(' — ')[0]
    i = SECTIONS.index(nom)
    tete = re.sub(r'fill="[^"]*"', 'fill="#e1e0d9"', tete)
    tete = tete.replace('<path ', '<path data-s="%d" ' % i, 1)
    return tete + '<title data-s="%d">%s</title></path>' % (i, nom)


svg = re.sub(r'(<path class="sec"[^>]*>)<title>([^<]*)</title></path>', _path, svg)


def _pv(mo):
    i = SECTIONS.index(TXT[mo.group(2)])
    return f'<text class="pv" data-v="{i}"{mo.group(1)}></text>'


svg = re.sub(r'<text class="pv"([^>]*)>([^<]*)</text>', _pv, svg)


def _pn(mo):
    t = mo.group(2)
    nom = t.split(' · ')[0]
    i = SECTIONS.index(nom)
    return f'<text class="pn" data-n="{i}"{mo.group(1)}></text>'


svg = re.sub(r'<text class="pn"([^>]*)>([^<]*)</text>', _pn, svg)
assert svg.count('data-s="') == 20 and svg.count('data-n="') == 10, (svg.count('data-s="'), svg.count('data-n="'))
svg = re.sub(r'\s*\n\s*', '\n', svg)
print('map', mode, ecrire('scores/carte.json', {'svg': svg, 'rampe': [c for c, _i in map_render.RAMP_NEUTRAL]}) // 1024, 'KB')

# ------------------------------------------------- comparer: survey answers
# A comparison profile is one value (or all) in each register: 11 x 3 x 3 x 5 x 4 masks.
PROFILS = []
for sec in range(11):
    for pay in range(3):
        for si in range(3):
            for ai in range(5):          # 0 = all ages, 1..4 = one band
                for ri in range(4):      # 0 = all, 1..3 = one category
                    ab = 15 if ai == 0 else 1 << (ai - 1)
                    rb = 7 if ri == 0 else 1 << (ri - 1)
                    PROFILS.append(idx(sec, pay, si, ab, rb))
assert len(PROFILS) == 1980

qmeta = []
taille = 0
bits = cat['bits']
for q in cat['questions']:
    mods = q['modalites']
    rep = np.zeros(N, dtype=bool)
    for j in range(len(mods)):
        rep |= bits[q['debut'] + j]
    ns, ks = [], [[] for _ in mods]
    for pi in PROFILS:
        m = MASQUES[pi] & rep
        nb = int(m.sum())
        if nb < SEUIL:
            ns.append(0 if nb == 0 else -1)
            continue
        ns.append(nb)       # k is written for these profiles only, in order
        for j in range(len(mods)):
            ks[j].append(int((bits[q['debut'] + j] & m).sum()))
    taille += ecrire(f'comparer/q/{q["i"]}.json', {'n': ns, 'k': ks})
    lib = both(lambda q=q: L.libelle(q, avec_module=True))
    qmeta.append({'i': q['i'], 'lib': lib,
                  'mods': [{'v': m, 'fr': m, 'en': both(lambda m=m: L.modalite(m))['en']} for m in mods]})
print('comparer questions', len(qmeta), 'files,', taille // 1024, 'KB')
print('comparer meta', ecrire('comparer/questions.json', {'profils': PROFILS, 'questions': qmeta}) // 1024, 'KB')
