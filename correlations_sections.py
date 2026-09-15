"""Exploratory pairwise Spearman associations at communal-section level."""
import json
import numpy as np
import pandas as pd
import streamlit as st
import croisement_moteur as M
import i18n


def rank_pairs(frame, metadata, minimum=8):
    rows = []
    keys = list(frame)
    indicators = [k for k in keys if metadata[k]['kind'] == 'indicator']
    arrays = {k: frame[k].to_numpy(dtype=float) for k in keys}
    ranks = {}
    def normalized(key, mask):
        cache_key = (key, mask.tobytes())
        if cache_key not in ranks:
            r = pd.Series(arrays[key][mask]).rank().to_numpy()
            r = r - r.mean()
            length = np.linalg.norm(r)
            ranks[cache_key] = r / length if length else None
        return ranks[cache_key]
    for i, a in enumerate(indicators):
        for b in keys:
            if a == b or (b in indicators and indicators.index(b) <= i):
                continue
            if metadata[a]['question'] and metadata[a]['question'] == metadata[b]['question']:
                continue
            valid = np.isfinite(arrays[a]) & np.isfinite(arrays[b])
            if valid.sum() < minimum:
                continue
            x, y = normalized(a, valid), normalized(b, valid)
            if x is None or y is None:
                continue
            rho = float(np.clip(x @ y, -1, 1))
            rows.append(dict(a=a, b=b, rho=rho, strength=abs(rho), n=int(valid.sum()),
                             type='indicators' if b in indicators else 'variables'))
    return pd.DataFrame(rows).sort_values('strength', ascending=False) if rows else pd.DataFrame()


def sensitivity(frame, a, b):
    pair = frame[[a, b]].dropna()
    values = []
    for section in pair.index:
        reduced = pair.drop(section)
        if reduced[a].nunique() > 1 and reduced[b].nunique() > 1:
            values.append(reduced[a].rank().corr(reduced[b].rank()))
    return (min(values), max(values)) if values else (np.nan, np.nan)


def build_frame(cat, results, measure, minimum_n):
    from relations_resultats import question_masks
    sections = list(M.SECTIONS)
    columns, meta = {}, {}
    for r in results:
        values = r.get(measure) or {}
        key = 'i:' + str(r['ligne'])
        x = pd.to_numeric(pd.Series({s: values.get(s) for s in sections}), errors='coerce')
        x = x.replace([np.inf, -np.inf], np.nan)
        if x.notna().sum() < 8 or x.nunique() < 3:
            continue
        columns[key] = x
        meta[key] = dict(kind='indicator', label=r['indicateur'],
                         question=M._norm(r.get('question') or ''), note=r.get('note') or '')
    for q in cat['questions']:
        masks, base = question_masks(cat, q)
        for label, mask in masks.items():
            values = {}
            for s in sections:
                eligible = cat['groupes'].get(s, np.zeros(cat['n'], bool)) & base
                n = int(eligible.sum())
                values[s] = 100 * int((eligible & mask).sum()) / n if n >= minimum_n else np.nan
            x = pd.Series(values)
            if x.notna().sum() < 8 or x.nunique() < 2:
                continue
            key = f'q:{q["i"]}:{label}'
            columns[key] = x
            meta[key] = dict(kind='variable', label=q['question'] + ' — ' + label,
                             question=M._norm(q['question']), note=f'Proportion (%); minimum n={minimum_n}')
    return pd.DataFrame(columns, index=sections), meta


def render(cat, fixed_mode=None):
    fr = i18n.get_lang() == 'fr'
    t = lambda a, b: a if fr else b
    st.subheader(t('Les associations les plus fortes', 'Strongest associations'))
    st.caption(t('Unité : section communale (10 au maximum). Classement exploratoire par |ρ de Spearman|, sans preuve de causalité ni test de significativité. Une association entre sections ne décrit pas nécessairement les ménages.',
                 'Unit: communal section (at most 10). Exploratory ranking by absolute Spearman rho, without causal claims or significance tests. Section associations do not necessarily describe households.'))
    measure = st.radio(t('Mesure des indicateurs', 'Indicator measure'), ['valeurs', 'scores_corriges'],
        format_func=lambda x: t('Valeurs brutes', 'Raw values') if x == 'valeurs' else t('Scores de résilience', 'Resilience scores'), horizontal=True, key='corr_measure')
    minimum_n = st.slider(t('Réponses valides minimum par section pour les variables', 'Minimum valid responses per section for survey variables'), 10, 100, 30, 10)
    path = M._trouver('resultats.json')
    if not path:
        st.info(t('Résultats indisponibles.', 'Results unavailable.'))
        return
    with open(path, encoding='utf-8') as f:
        results = json.load(f)
    if isinstance(results, dict):
        results = results['indicateurs']
    frame, meta = build_frame(cat, results, measure, minimum_n)
    mode = fixed_mode or st.radio(t('Relations recherchées', 'Relationship types'), ['all', 'indicators', 'variables'],
        format_func=lambda x: {'all':t('Toutes', 'All'), 'indicators':t('Indicateur ↔ indicateur', 'Indicator ↔ indicator'), 'variables':t('Indicateur ↔ variable', 'Indicator ↔ variable')}[x], horizontal=True)
    focus = st.selectbox(t('Centrer sur un indicateur', 'Focus on an indicator'),
                        [None] + [k for k in frame if meta[k]['kind'] == 'indicator'],
                        format_func=lambda k: t('Tous', 'All') if k is None else meta[k]['label'])
    if not st.toggle(t('Afficher le classement', 'Show ranking'), key='corr_show'):
        return
    with st.spinner(t('Comparaison des sections…', 'Comparing sections…')):
        # Limit computation to requested pairs; the ranking remains reproducible.
        ranked = rank_pairs(frame, meta)
    if ranked.empty:
        st.info(t('Pas assez de données comparables (au moins 8 sections).', 'Insufficient comparable data (at least 8 sections).'))
        return
    if mode != 'all':
        ranked = ranked[ranked.type == mode]
    if focus:
        ranked = ranked[(ranked.a == focus) | (ranked.b == focus)]
    st.caption(t(f'{len(ranked)} paires comparées. Les liens provenant de la même question sont exclus. Les données manquantes ne sont pas remplacées par zéro.',
                 f'{len(ranked)} pairs compared. Links from the same source question are excluded. Missing data are not replaced with zero.'))
    if ranked.empty:
        st.info(t('Aucune paire pour cette sélection.', 'No pairs for this selection.'))
        return
    ranked = ranked.copy()
    ranked['low'] = np.nan
    ranked['high'] = np.nan
    for idx, row in ranked.head(20).iterrows():
        ranked.loc[idx, ['low', 'high']] = sensitivity(frame, row.a, row.b)
    export = ranked.assign(indicator=ranked.a.map(lambda k:meta[k]['label']),
                           compared=ranked.b.map(lambda k:meta[k]['label']))
    export['definition_check'] = np.where(export.strength >= .999999,
        t('Lien parfait : vérifier définition/source commune', 'Perfect link: check shared definition/source'),
        t('Association exploratoire', 'Exploratory association'))
    st.caption(t('Les liens parfaits sont signalés : ils peuvent provenir de la définition des mesures ou d’une question source non identifiée. Ils ne constituent pas automatiquement une découverte indépendante.',
                 'Perfect links are flagged: they may arise from measure definitions or an unidentified source question. They are not automatically independent discoveries.'))
    st.dataframe(export[['indicator', 'compared', 'rho', 'n', 'low', 'high', 'definition_check']].head(20).rename(columns={
        'indicator':t('Indicateur','Indicator'), 'compared':t('Comparé à','Compared with'),
        'n':t('Sections','Sections'), 'low':'ρ min (−1 section)', 'high':'ρ max (−1 section)'}), hide_index=True, use_container_width=True)
    st.caption(t('Sensibilité calculée pour les 20 premières paires uniquement. ρ positif : les deux mesures augmentent ensemble ; négatif : elles évoluent en sens opposés. Les bornes −1 section montrent la sensibilité au retrait de chaque section, pas un intervalle de confiance. Parmi beaucoup de paires, de fortes corrélations peuvent apparaître par hasard. Des définitions proches peuvent aussi créer des liens mécaniques.',
                 'Sensitivity is computed for the top 20 pairs only. Positive rho: both measures increase together; negative: opposite directions. Leave-one-section bounds show sensitivity, not confidence intervals. Searching many pairs can find strong correlations by chance. Related definitions can also create mechanical links.'))
    st.download_button(t('Télécharger le classement CSV', 'Download ranking CSV'), export.to_csv(index=False).encode('utf-8-sig'), 'correlations_sections.csv', 'text/csv')
    selected = st.selectbox(t('Examiner une association', 'Inspect an association'), list(ranked.head(20).index),
        format_func=lambda idx: meta[ranked.loc[idx, 'a']]['label'] + ' ↔ ' + meta[ranked.loc[idx, 'b']]['label'])
    best = ranked.loc[selected]
    detail = frame[[best.a, best.b]].dropna().rename(columns={best.a:'X', best.b:'Y'})
    st.markdown('**' + t('Association sélectionnée', 'Selected association') + '**')
    st.write(meta[best.a]['label'] + ' ↔ ' + meta[best.b]['label'])
    st.scatter_chart(detail, x='X', y='Y')
    st.dataframe(detail.rename_axis(t('Section communale', 'Communal section')), use_container_width=True)
    st.download_button(t('Télécharger les points CSV', 'Download points CSV'), detail.to_csv().encode('utf-8-sig'), 'correlation_points.csv', 'text/csv')
    with st.expander(t('Sources et limites', 'Sources and limitations')):
        st.write(meta[best.a]['note'])
        st.write(meta[best.b]['note'])
        st.write(t('Valeurs et scores du même fichier de résultats que le moteur APRI. Variables : parts de réponses valides recalculées par section. Aucune pondération, aucun ajustement spatial, aucun score individuel reconstruit. Les coefficients portent seulement sur les sections disposant des deux mesures.',
                   'Values and scores use the APRI engine results file. Variables are valid-response shares recomputed by section. No weighting, spatial adjustment or reconstructed individual scores. Coefficients use only sections with both measures.'))

