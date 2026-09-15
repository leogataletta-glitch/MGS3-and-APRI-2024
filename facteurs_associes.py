"""Exploratory adjusted household associations, conditional on communal section.
No causal estimates, territorial pseudo-replication, imputation or automatic selection.
"""
import numpy as np
import pandas as pd
import streamlit as st
import i18n
import croisement_moteur as M
import libelles_enquete as L
from traductions import text as tr


def candidates(cat):
    from relations_resultats import substantive
    out = []
    for q in cat['questions']:
        if not 2 <= len(q['modalites']) <= 12:
            continue
        masks = [cat['bits'][q['debut'] + j] for j in range(len(q['modalites']))]
        count = np.sum(masks, axis=0)
        labels = [j for j, label in enumerate(q['modalites']) if substantive(label)
                  and not any(w in M._norm(label) for w in ('sais pas', 'sans objet', 'inconnu', 'manquant'))]
        if len(labels) < 2:
            continue
        valid = np.logical_or.reduce([masks[j] for j in labels])
        unknown = [masks[j] for j in range(len(masks)) if j not in labels]
        if unknown:
            valid &= ~np.logical_or.reduce(unknown)
        if 'unique' in M._norm(q.get('note', '')):
            valid &= count == 1
        for j in labels:
            y = masks[j] & valid
            if min(y.sum(), (valid & ~y).sum()) < 30:
                continue
            out.append(dict(key=f'q{q["i"]}:{j}', source=f'q{q["i"]}',
                            question=q['question'], label=q['modalites'][j], y=y, valid=valid))
    return out


def section_ids(cat):
    ids = np.full(cat['n'], -1)
    counts = np.zeros(cat['n'], int)
    for j, name in enumerate(M.SECTIONS):
        mask = cat['groupes'].get(name, np.zeros(cat['n'], bool))
        ids[mask] = j
        counts += mask
    ids[counts != 1] = -1
    return ids


def estimate(y, X, groups, draws=1500):
    """Within-section OLS; section pairs bootstrap and leave-one-section-out.

    Binary regressors: slopes are adjusted percentage-point differences. Bootstrap
    quantiles describe exploratory uncertainty, not guaranteed 95% coverage with G=10.
    """
    y, X = np.asarray(y, float), np.asarray(X, float)
    keys = np.unique(groups)
    n, p = X.shape
    if len(keys) < 6 or n < max(100, 30 * (p + 1)):
        raise ValueError('sample')
    if min(y.sum(), n-y.sum()) < 30 or any(min(v.sum(), n-v.sum()) < 30 for v in X.T):
        raise ValueError('rare')
    if any(sum(np.unique(v[groups == g]).size == 2 for g in keys) < 4 for v in X.T):
        raise ValueError('variation')
    if sum(np.unique(y[groups == g]).size == 2 for g in keys) < 4:
        raise ValueError('variation')
    xc, yc = X.copy(), y.copy()
    for g in keys:
        ix = groups == g
        xc[ix] -= X[ix].mean(axis=0)
        yc[ix] -= y[ix].mean()
    if np.linalg.matrix_rank(xc) < p or np.linalg.cond(xc) > 30:
        raise ValueError('collinear')
    if any(np.array_equal(v, y) or np.array_equal(v, 1-y) for v in X.T):
        raise ValueError('duplicate')
    A = np.array([xc[groups == g].T @ xc[groups == g] for g in keys])
    b = np.array([xc[groups == g].T @ yc[groups == g] for g in keys])
    def solve(a, b):
        if np.linalg.matrix_rank(a) < p or np.linalg.cond(a) > 900:
            return None
        return np.linalg.solve(a, b)
    beta = solve(A.sum(axis=0), b.sum(axis=0))
    loo = [solve(A.sum(axis=0)-a, b.sum(axis=0)-v) for a, v in zip(A, b)]
    rng = np.random.default_rng(2024)
    boots = []
    for _ in range(draws):
        ix = rng.integers(0, len(keys), len(keys))
        fit = solve(A[ix].sum(axis=0), b[ix].sum(axis=0))
        if fit is not None:
            boots.append(fit)
    good_loo = [v for v in loo if v is not None]
    if len(boots) < .9 * draws or len(good_loo) != len(keys):
        raise ValueError('unstable')
    boots, loo = np.array(boots), np.array(good_loo)
    return dict(beta=beta*100, low=np.percentile(boots,2.5,axis=0)*100,
                high=np.percentile(boots,97.5,axis=0)*100,
                loo_low=loo.min(axis=0)*100, loo_high=loo.max(axis=0)*100,
                same_sign=np.mean(np.sign(loo)==np.sign(beta),axis=0),
                bootstrap_valid=len(boots), sections=len(keys), n=n,
                crude=np.array([y[v==1].mean()-y[v==0].mean() for v in X.T])*100)


@st.cache_data(show_spinner=False)
def run(y, X, groups):
    return estimate(y, X, groups)


def render(cat):
    fr = i18n.get_lang() == 'fr'
    def t(a,b): return tr(a if fr else b)
    from relations_guide import render_steps
    render_steps('facteurs', fr)
    with st.expander(t('Ce que cette analyse permet de dire', 'What this analysis can tell us')):
        st.write(t('Le modèle compare les ménages d’une même section communale, en tenant compte simultanément des facteurs choisis. Chaque modalité est comparée à son absence parmi les réponses valides de sa question. Un coefficient de +10 signifie un écart ajusté de +10 points de pourcentage, pas une hausse de 10 %. Le choix des facteurs doit être motivé avant de lire les résultats : ne retenez pas uniquement ceux qui donnent un grand coefficient.',
                   'The model compares households within the same communal section while adjusting for the selected factors. Each response category is compared with its absence among valid answers to that question. A +10 coefficient means an adjusted difference of +10 percentage points, not a 10% increase. Choose factors on substantive grounds before inspecting results, not because they produce large coefficients.'))
        st.write(t('Les causes non mesurées, les erreurs de réponse et la causalité inverse restent possibles. Un facteur calculé à partir du phénomène étudié ne doit pas servir à l’expliquer. Les scores territoriaux ne sont pas recopiés sur les ménages pour augmenter artificiellement l’effectif.',
                   'Unmeasured factors, reporting errors and reverse causality remain possible. Do not use a factor derived from the outcome to explain that outcome. Territorial scores are not replicated across households to inflate the sample size.'))
    if not cat:
        st.info(t('Réponses individuelles indisponibles.', 'Individual responses unavailable.')); return
    fs = candidates(cat)
    bykey = {f['key']: f for f in fs}
    def label(k):
        f=bykey[k]
        return tr(L.question(f['question'])) + ' — ' + tr(L.modalite(f['label']))
    target = st.selectbox(t('Phénomène : réponse à étudier', 'Outcome: response to study'), list(bykey),
                          index=None, format_func=label, key='factors_target',
                          placeholder=t('Rechercher une question ou une réponse…', 'Search for a question or response…'))
    if target is None:
        st.info(t('Choisissez un phénomène mesuré dans l’enquête ménage, puis jusqu’à trois facteurs à tester ensemble.',
                  'Choose an outcome measured in the household survey, then up to three factors to test together.'))
    else:
        outcome = bykey[target]
        options = [f['key'] for f in fs if f['source'] != outcome['source']]
        key='factors_predictors_'+target
        picked = st.multiselect(t('Facteurs à tester ensemble (trois maximum)', 'Factors to test together (up to three)'),
                                options, format_func=label, max_selections=3, key=key)
        st.caption(t('Chaque facteur signifie « cette réponse » contre « les autres réponses valides ». Une seule modalité par question dans le modèle. Pour les choix multiples, « non » signifie non sélectionné parmi les personnes ayant répondu ; une absence de réponse n’est jamais un non.',
                     'Each factor means this response versus the other valid responses. One response category per question in the model. For multiple-choice questions, no means not selected among respondents who answered; a missing answer never means no.'))
        if picked and st.button(t('Calculer les associations ajustées', 'Calculate adjusted associations'), key='factors_run'):
            chosen = [bykey[k] for k in picked]
            if len({f['source'] for f in chosen}) != len(chosen):
                st.warning(t('Choisissez des facteurs issus de questions différentes.', 'Choose factors from different questions.')); return
            groups = section_ids(cat)
            valid = outcome['valid'].copy() & (groups >= 0)
            audit = [(t('Réponses valides au phénomène', 'Valid outcome responses'), int(valid.sum()))]
            for f in chosen:
                valid &= f['valid']
                audit.append((label(f['key']), int(valid.sum())))
            y = outcome['y'][valid].astype(float)
            X = np.column_stack([f['y'][valid] for f in chosen]).astype(float)
            try:
                result = run(y, X, groups[valid])
            except ValueError as err:
                messages = {
                    'sample': ('Effectif insuffisant : au moins 100 ménages complets et 6 sections sont nécessaires.', 'Insufficient sample: at least 100 complete households and 6 sections are required.'),
                    'rare': ('Une réponse ou son complément compte moins de 30 ménages dans l’échantillon commun.', 'A response or its complement has fewer than 30 households in the common sample.'),
                    'variation': ('Le phénomène ou un facteur varie dans moins de quatre sections : comparaison ajustée non estimable avec assez de soutien.', 'The outcome or a factor varies in fewer than four sections: insufficient within-section support.'),
                    'collinear': ('Facteurs redondants ou presque identiques : choisissez une autre combinaison.', 'Redundant or nearly identical factors: choose another combination.'),
                    'duplicate': ('Un facteur reproduit exactement le phénomène ou son inverse : comparaison circulaire exclue.', 'A factor exactly reproduces the outcome or its complement: circular comparison excluded.'),
                    'unstable': ('Le modèle devient non estimable au retrait ou au rééchantillonnage des sections. Réduisez le nombre de facteurs.', 'The model becomes unidentifiable when sections are omitted or resampled. Reduce the number of factors.')}
                st.warning(t(*messages.get(str(err), messages['unstable'])))
            else:
                st.write(t(f"{result['n']} ménages analysés sur {cat['n']} ; {cat['n']-result['n']} exclus ; {result['sections']} sections. Réponse étudiée : {int(y.sum())}/{len(y)} ({y.mean()*100:.1f} %).",
                           f"{result['n']} of {cat['n']} households analysed; {cat['n']-result['n']} excluded; {result['sections']} sections. Outcome response: {int(y.sum())}/{len(y)} ({y.mean()*100:.1f}%)."))
                rows=[]
                for j,k in enumerate(picked):
                    rows.append({t('Facteur (oui / autres réponses)', 'Factor (yes / other responses)'):label(k),
                                 t('Écart brut (points)', 'Unadjusted difference (pp)'):result['crude'][j],
                                 t('Écart ajusté (points)', 'Adjusted difference (pp)'):result['beta'][j],
                                 t('Borne basse bootstrap', 'Bootstrap lower bound'):result['low'][j],
                                 t('Borne haute bootstrap', 'Bootstrap upper bound'):result['high'][j],
                                 t('Minimum sans une section', 'Minimum omitting one section'):result['loo_low'][j],
                                 t('Maximum sans une section', 'Maximum omitting one section'):result['loo_high'][j],
                                 t('Signe conservé', 'Sign retained'):f"{result['same_sign'][j]*100:.0f}%"})
                order=np.argsort(-np.abs(result['beta']))
                st.dataframe(pd.DataFrame([rows[j] for j in order]).round(2), hide_index=True, use_container_width=True)
                st.caption(t('Classement limité aux facteurs choisis, par amplitude absolue de l’écart ajusté. Ce n’est ni un classement des causes ni une importance universelle. « Signe conservé » : proportion des retraits d’une section qui gardent le même sens.',
                             'Ranking covers selected factors only, by absolute adjusted difference. It is not a ranking of causes or universal importance. “Sign retained”: share of leave-one-section-out fits retaining the same direction.'))
                j=int(order[0]);lo,hi=result['low'][j],result['high'][j]
                st.write(t(f"Pour « {label(picked[j])} », l’écart ajusté est de {result['beta'][j]:+.1f} points, à facteurs choisis et section pris en compte. L’intervalle exploratoire va de {lo:+.1f} à {hi:+.1f} points.",
                           f"For “{label(picked[j])}”, the adjusted difference is {result['beta'][j]:+.1f} pp, accounting for selected factors and section. The exploratory interval runs from {lo:+.1f} to {hi:+.1f} pp."))
                st.warning(t('Les bornes sont les quantiles 2,5 % et 97,5 % de 1 500 rééchantillonnages de sections entières. Avec dix sections au maximum, elles sont fragiles : pas de garantie de couverture à 95 %, pas de test de significativité ni de preuve causale. Le retrait d’une section mesure une sensibilité, pas un intervalle de confiance.',
                             'Bounds are the 2.5th and 97.5th percentiles of 1,500 whole-section resamples. With at most ten sections they are fragile: no guaranteed 95% coverage, significance claim or causal proof. Omitting one section measures sensitivity, not a confidence interval.'))
            with st.expander(t('Échantillon et méthode', 'Sample and method')):
                st.dataframe(pd.DataFrame(audit,columns=[t('Étape', 'Step'),t('Ménages restants', 'Remaining households')]), hide_index=True)
                st.write(t('Cas complets uniquement, sans imputation : réponses manquantes, inconnues, refusées, non applicables ou contradictoires pour une question unique exclues. Les questions conditionnelles restent limitées aux personnes ayant fourni une réponse valide ; vérifiez leur population de référence avant interprétation. Modèle linéaire de probabilité par moindres carrés, avec effets fixes de section (centrage intra-section). Estimation non pondérée, limitée aux répondants analysés ; aucune extrapolation à Haïti. Les écarts ne sont pas des probabilités prédites.',
                           'Complete cases only, without imputation: missing, unknown, refused, inapplicable or conflicting answers excluded. Conditional questions retain only people with a valid answer; check their reference population before interpreting results. Unweighted linear probability model fitted by least squares with section fixed effects (within-section centering). Estimates concern analysed respondents, not all Haiti. Differences are not predicted probabilities.'))
                st.markdown('[Cameron & Miller — Cluster-robust inference](https://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015.pdf)')
    with st.expander(t('Et la perte de couvert arboré ?', 'What about tree-cover loss?')):
        st.write(t('Ce modèle porte sur les ménages. La perte de couvert arboré exige une étude spatiale séparée : périodes comparables, cellules avec et sans perte, couvert initial, facteurs antérieurs aux pertes et dépendance spatiale. Les dix sections ne deviennent pas 1 211 observations forestières. Aucune cause de déforestation n’est estimée dans cet onglet.',
                   'This model concerns households. Tree-cover loss requires a separate spatial study: comparable periods, cells with and without loss, baseline cover, predictors preceding losses and spatial dependence. Ten sections do not become 1,211 forest observations. This tab does not estimate causes of deforestation.'))
