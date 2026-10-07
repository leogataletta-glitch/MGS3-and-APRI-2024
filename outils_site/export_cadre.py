"""Export the data of the "Cadre de résilience" section (cadre_page.py) to data/cadre/.

Run from the site root:  python3 outils/export_cadre.py
Everything is aggregate (whole-sample values per indicator, per dimension);
no household-level record is written.
"""
import sys, os, json, shutil
SITE = os.path.abspath(os.getcwd())
OUT = os.path.join(SITE, 'data', 'cadre')
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, '/tmp/work'); os.chdir('/tmp/work')

import streamlit as st
st.session_state['lang'] = 'fr'
import i18n
import cadre_page as cp
import modele_parcours, score_parcours, reforestation_demo
import biodiversite_page as bio

LANGS = ('fr', 'en')


def lang(l):
    st.session_state['lang'] = l


# --- captured iframe documents (modele_parcours / reforestation) ------------
captured = []
modele_parcours.components.html = lambda html, **kw: captured.append(html)


def capture(fn):
    captured.clear(); fn(); return captured[-1]


# --- biodiversity notice (indicators 47-49), recorded from its st calls -----
class Rec:
    def __init__(self): self.out = []
    def caption(self, t): self.out.append(['caption', t])
    def info(self, t): self.out.append(['info', t])
    def dataframe(self, df, **kw): self.out.append(['table', [list(df.columns)] + df.values.tolist()])


tous = None
out = {'langs': {}, 'textes': {}, 'dims': cp.ORDRE}
for l in LANGS:
    lang(l)
    T = i18n.T
    tx = {k: T(k) for k in cp.TEXTES}
    for k in cp.ORDRE + ['e_absent']:
        tx[k] = T(k)
    out['textes'][l] = tx
    st.cache_data.clear()
    ref = cp._referentiel()
    par_ligne, graphe = cp._causal()
    for x in ref:
        k = x['ligne']
        x.setdefault('src', {})
        x.setdefault('pourquoi', {})
        x.setdefault('refs', {})
        x['src'][l] = cp._meta_source(x, l)
        x['pourquoi'][l] = [t for t, r in cp._meta_pourquoi(x, par_ligne, graphe, l)]
        x['refs'][l] = cp._references_fiche(x, l)
    if tous is None:
        tous = ref
    else:
        by = {x['ligne']: x for x in ref}
        for x in tous:
            y = by[x['ligne']]
            for f in ('src', 'pourquoi', 'refs'):
                x[f][l] = y[f][l]
    # parcours iframes
    attrs = [(T(k + "_t"), T(k)) for k in ("cad_a1", "cad_a2", "cad_a3")]
    dims = [T(k) for k in cp.ORDRE]
    srcs = [(T("cad_so" + str(i) + "_t"), T("cad_so" + str(i) + "_x")) for i in range(1, 5)]
    out['langs'][l] = {
        'mesure': capture(lambda: modele_parcours.render(attrs, dims, srcs)),
        'boucles': capture(lambda: modele_parcours.render_feedback(
            [(T(k + "_t"), T(k + "_x"), T(k + "_e")) for k in ("cad_b1", "cad_b2", "cad_b3", "cad_b4")])),
        'score': capture(score_parcours.render),
        'reboiser': reforestation_demo.document(l == 'fr'),
    }
    r = Rec(); bio.st = r
    bio.scope(); bio.indicators()
    out['langs'][l]['bio'] = {
        'titre': bio.t('Nouveaux résultats de biodiversité disponibles', 'New biodiversity results available', '', ''),
        'bouton': bio.t('Voir les résultats de biodiversité', 'View biodiversity results', '', ''),
        'blocs': r.out}

# indicators: aggregate values only (whole-sample "Total")
inds = []
for x in tous:
    par = cp._bandes(x['echelle'])
    ec = None
    if par:
        bas, haut = par[min(par)], par[max(par)]
        def _n(t):
            v = [float(s.replace(',', '.')) for s in cp._RE_NOMBRE.findall(t)]
            return sum(v) / len(v) if v else None
        a, b = _n(bas), _n(haut)
        ec = {'unite': 'pct' if '%' in bas + haut else 'val',
              'sens': None if a is None or b is None else ('inv' if a > b else 'cro')}
    x['bandes'] = [[k, par[k]] for k in sorted(par)] if par else []
    x['ec'] = ec
    inds.append(x)
out['indicateurs'] = inds
st.cache_data.clear()
out['stats'] = cp._stats()
out['score_dim'] = {d: cp._score_dimension(d) for d in cp.ORDRE}
m, ns = cp._menages()
out['menages'], out['n_sections'], out['min_section'] = m, ns, cp.MIN_SECTION
out['echelle'] = list(cp._ECHELLE)

with open(os.path.join(OUT, 'cadre.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
shutil.copyfile('/tmp/work/IRLA_UNEP_V4.pdf', os.path.join(OUT, 'IRLA_UNEP_V4.pdf'))
print('indicateurs', len(inds), 'menages', m, 'sections', ns,
      'json', os.path.getsize(os.path.join(OUT, 'cadre.json')))
