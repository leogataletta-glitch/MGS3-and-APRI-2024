"""Export the data behind the "Boucles de rétroaction / Feedback Loops" section.

Writes, relative to the site root:
  data/boucles/modele.json   the causal graph (as boucles_moteur.charger() returns it),
                             its scale, and the AGGREGATE scores of the indicators the
                             graph uses (scores 0-10 per population, raw values per
                             communal section for the Spearman cross-check)
  data/boucles/textes.json   every visible string of the six tabs, in fr and en

Nothing household-level is written: the graph engine only ever reads aggregate
scores from data/resultats.json. Any score whose population has fewer than five
households is dropped (none exist at present).

Run: python3 outils/export_boucles.py   (cwd = site root)
"""
import json
import os
import sys

SITE = os.path.abspath(os.getcwd())
SRC = '/tmp/work'
sys.path.insert(0, SRC)
os.chdir(SRC)

import streamlit as st  # noqa: E402
st.session_state['lang'] = 'fr'

import boucles_moteur as M  # noqa: E402
import i18n  # noqa: E402
import systeme_complexe as SX  # noqa: E402
import systeme_direct as SD  # noqa: E402
import systeme_page as SP  # noqa: E402
import provenance_relations as PR  # noqa: E402
import schema_exploration as SE  # noqa: E402

OUT = os.path.join(SITE, 'data', 'boucles')
os.makedirs(OUT, exist_ok=True)


def ecrire(nom, obj):
    p = os.path.join(OUT, nom)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, separators=(',', ':'))
    print(nom, os.path.getsize(p), 'octets')


# ------------------------------------------------------------------ the model
g = M.charger()
with open(os.path.join(SRC, 'data', 'resultats.json'), encoding='utf-8') as f:
    res = json.load(f)
res = res['indicateurs'] if isinstance(res, dict) else res
par_ligne = {r['ligne']: r for r in res}

# effet_indice() divides by the weight of every scored indicator, not only those
# in the graph: that single number is all the browser needs from the other 90.
poids_total = sum((r.get('ponderation') or 1) for r in par_ligne.values()
                  if (r.get('scores_corriges') or {}).get('Total') is not None)

indicateurs = {}
for n in g['noeuds']:
    lg = n.get('ligne')
    r = par_ligne.get(lg) if lg else None
    if not r:
        continue
    eff = r.get('n') or {}
    sc = {}
    for pop, v in (r.get('scores_corriges') or {}).items():
        if v is None:
            continue
        if isinstance(eff.get(pop), (int, float)) and eff[pop] < 5:
            continue   # privacy: n < 5
        sc[pop] = v
    vals = {s: r['valeurs'][s] for s in M.SECTIONS
            if (r.get('valeurs') or {}).get(s) is not None
            and not (isinstance(eff.get(s), (int, float)) and eff[s] < 5)}
    indicateurs[str(lg)] = {'sens': r.get('sens'), 'ponderation': r.get('ponderation'),
                            'scores_corriges': sc, 'valeurs': vals}

diag = M.diagnostic(g)
modele = {
    'graphe': g,
    'indicateurs': indicateurs,
    'poids_total': poids_total,
    'sections': M.SECTIONS,
    'populations': [p for p, _l in SX.POPULATIONS],
    'constantes': {'RAYON_CIBLE': M.RAYON_CIBLE, 'SEUIL_NUL': M.SEUIL_NUL,
                   'TENDU': M.TENDU, 'BOUCLE_MAX': M.BOUCLE_MAX,
                   'BOUCLES_MAX': M.BOUCLES_MAX,
                   'RHO_CRITIQUE_10': SX.RHO_CRITIQUE_10,
                   'NOEUDS_LISIBLES': SX.NOEUDS_LISIBLES, 'TAILLES': SX.TAILLES,
                   'VAGUES_MAX': SX.VAGUES_MAX, 'SEUIL_VAGUE': SX.SEUIL_VAGUE},
    # reference only: the browser recomputes the spectral radius itself and the
    # check page compares the two
    'controle': {'rayon': diag['rayon'], 'facteur': diag['facteur']},
    'couleurs_dim': SP.COUL_DIM,
}
ecrire('modele.json', modele)

# ------------------------------------------------------------------ the texts
textes = {}
for d in (SX.TEXTES, SD.TEXTES, SP.TEXTES):
    for k, v in d.items():
        textes[k] = {'fr': v.get('fr'), 'en': v.get('en')}
for k in ('dim1', 'dim2', 'dim3', 'dim4', 'dim5', 'dim6'):
    textes[k] = {'fr': i18n.DICO[k]['fr'], 'en': i18n.DICO[k]['en']}


# the diagram labels live inline in schema_exploration.render(): capture them
class _Capture:
    payload = None


def _faux_html(html, **kw):
    i = html.index('const {data,labels}=') + len('const {data,labels}=')
    j = html.index(', svg=document', i)
    _Capture.payload = json.loads(html[i:j].replace('\\u003c', '<'))


SE.components.html = _faux_html
schema = {}
m = SX._modele('fr')
for lang in ('fr', 'en'):
    st.session_state['lang'] = lang
    rang, aretes = SX._voisinage(m, m['ids'][0], 5)
    SE.render(m, rang, aretes, m['ids'][0], SX._positions(rang, m['ids'][0])[0])
    schema[lang] = _Capture.payload['labels']
textes['_schema'] = schema
textes['_provenance'] = {'fr': PR.labels('fr'), 'en': PR.labels('en')}
ecrire('textes.json', textes)
