"""Pairwise-complete binary response associations; no invented ordinal codes."""
import numpy as np
import pandas as pd
from html import escape
import streamlit as st
import i18n
import croisement_moteur as M


def features(cat):
    from relations_resultats import question_masks
    output = []
    agri = next((q for q in cat['questions'] if M._norm(q['question']) == 'pratique personnellement l agriculture'), None)
    farmers = None
    if agri:
        answers, _ = question_masks(cat, agri)
        farmers = answers.get('Oui')
    for q in cat['questions']:
        masks, base = question_masks(cat, q)
        if len(masks) < 2:
            continue
        if M._norm(q['question']) == 'cultures pratiquees':
            if farmers is None:
                continue
            base = base & farmers
        # For exclusive binary questions one response completely specifies the pair.
        labels = list(masks)
        if len(labels) == 2 and not (masks[labels[0]] & masks[labels[1]]).any():
            labels = ['Oui'] if 'Oui' in masks else labels[:1]
        for label in labels:
            output.append(dict(key=f'q:{q["i"]}:{label}', source=f'q:{q["i"]}',
                question=q['question'], label=label, y=masks[label] & base, valid=base,
                crop=M._norm(q['question']) == 'cultures pratiquees'))
    for name, groups in M.REGISTRES:
        if name == 'section':
            continue
        masks = [cat['groupes'].get(g, np.zeros(cat['n'], bool)) for g in groups]
        base = np.sum(masks, axis=0) == 1
        labels = ['Montagne'] if name == 'paysage' else groups[:1] if len(groups) == 2 else groups
        for label in labels:
            output.append(dict(key='g:'+label, source='g:'+name, question=name,
                label=label, y=cat['groupes'][label] & base, valid=base, crop=False))
    return output


def rank(features, population, minimum=30, focus=None, kind='all'):
    if not features:
        return pd.DataFrame()
    y = np.array([f['y'] & f['valid'] & population for f in features], dtype=float)
    v = np.array([f['valid'] & population for f in features], dtype=float)
    both, positive, count = y @ y.T, y @ v.T, v @ v.T
    denom = np.sqrt(positive * (count-positive) * positive.T * (count-positive.T))
    phi = np.divide(count*both-positive*positive.T, denom, out=np.zeros_like(count), where=denom>0)
    eligible = np.triu(np.ones(count.shape, bool), 1)
    eligible &= (positive >= minimum) & (positive.T >= minimum)
    eligible &= (count-positive >= minimum) & (count-positive.T >= minimum)
    ii, jj = np.where(eligible)
    rows = []
    for a, b in zip(ii, jj):
        fa, fb = features[a], features[b]
        if fa['source'] == fb['source'] or M._norm(fa['question']) == M._norm(fb['question']):
            continue
        if focus is not None and fa['source'] != focus and fb['source'] != focus:
            continue
        if kind == 'landscape' and fa['source'] != 'g:paysage' and fb['source'] != 'g:paysage':
            continue
        # Exact duplicates/complements can reflect repeated questionnaire fields.
        if abs(phi[a, b]) >= 1-1e-12:
            continue
        n, x, z, k = count[a,b], positive[a,b], positive[b,a], both[a,b]
        rows.append(dict(a=int(a), b=int(b), phi=float(phi[a,b]), strength=abs(float(phi[a,b])),
                         n=int(n), both=int(k), a_only=int(x-k), b_only=int(z-k), neither=int(n-x-z+k)))
    return pd.DataFrame(rows).sort_values('strength', ascending=False) if rows else pd.DataFrame()


def detail(cat, a, b, population):
    valid = population & a['valid'] & b['valid']
    rows = []
    for present in (True, False):
        group = valid & (b['y'] if present else ~b['y'])
        n, k = int(group.sum()), int((group & a['y']).sum())
        rows.append(dict(group=present, n=n, yes=k, percent=100*k/n if n else np.nan))
    sections = []
    for s in M.SECTIONS:
        mask = valid & cat['groupes'].get(s, np.zeros(cat['n'], bool))
        sections.append([int((mask & b['y'] & a['y']).sum()), int((mask & b['y']).sum()),
                         int((mask & ~b['y'] & a['y']).sum()), int((mask & ~b['y']).sum())])
    counts = np.array(sections)
    # Sensitivity, not a confidence interval: omit each section in turn.
    estimates = []
    totals = np.array([rows[0]['yes'],rows[0]['n'],rows[1]['yes'],rows[1]['n']])
    for c in counts:
        if c[1]+c[3] == 0:
            continue
        k1,n1,k0,n0 = totals-c
        if n1 and n0:
            estimates.append(100*(k1/n1-k0/n0))
    return pd.DataFrame(rows), (min(estimates),max(estimates)) if estimates else None


def render(cat):
    fr = i18n.get_lang() == 'fr'
    t = lambda a,b:a if fr else b
    st.subheader(t('Associations entre réponses individuelles', 'Associations between individual answers'))
    st.write(t('Chaque observation est un répondant. Le classement utilise le coefficient φ (phi) entre deux réponses présentes/absentes parmi les réponses valides : de −1 à +1, classé par valeur absolue. « Absente » signifie une autre réponse valide, jamais une non-réponse.',
               'Each observation is a respondent. Ranking uses phi between two selected responses (present/absent among valid answers), from −1 to +1, sorted by absolute value. Absent means another valid answer, never missing data.'))
    fs = features(cat)
    names = {f['source']: f['question'] for f in fs}
    kind = st.selectbox(t('Rechercher', 'Search'), ['all', 'landscape'], format_func=lambda x: t('Toutes les associations', 'All associations') if x == 'all' else t('Avec le paysage', 'With landscape'))
    focus = st.selectbox(t('Question à explorer','Question to explore'),[None]+list(names),
                         format_func=lambda x:t('Toutes les questions','All questions') if x is None else names[x])
    population = np.ones(cat['n'],bool)
    from relations_resultats import question_masks
    with st.expander(t('Limiter à un sous-groupe (comparaison descriptive)','Restrict to a subgroup (descriptive comparison)')):
        lookup = {q['i']:q for q in cat['questions']}
        fq = st.selectbox(t('Question de filtre','Filter question'),[None]+list(lookup),format_func=lambda x:t('Aucune','None') if x is None else lookup[x]['question'],key='assoc_filter')
        if fq is not None:
            masks,_ = question_masks(cat,lookup[fq])
            chosen = st.multiselect(t('Réponses retenues','Included answers'),list(masks),key=f'assoc_filter_{fq}')
            if not chosen:
                st.info(t('Choisissez une réponse pour ce filtre.','Choose an answer for this filter.'))
                return
            population &= np.logical_or.reduce([masks[x] for x in chosen])
    minimum = st.slider(t('Effectif minimum de chaque modalité et de son complément','Minimum count for each response and its complement'),10,100,30,10)
    st.caption(t('Pour les cultures pratiquées, seuls les répondants déclarant pratiquer personnellement l’agriculture sont inclus. Les refus et réponses inconnues sont exclus pour chaque paire. Les questions identiques et les réponses parfaitement identiques ou complémentaires sont écartées du classement.',
                 'Crop comparisons include only respondents reporting personally practising agriculture. Refusals and unknown answers are excluded pairwise. Same-question pairs and exactly identical or complementary answers are excluded from ranking.'))
    if not st.toggle(t('Afficher les associations','Show associations'),key='assoc_show'):
        return
    with st.spinner(t('Calcul des associations…','Calculating associations…')):
        ranked = rank(fs,population,minimum,focus,kind)
    if ranked.empty:
        st.info(t('Aucune paire admissible pour ces critères.','No eligible pairs for these criteria.'))
        return
    label = lambda i:fs[i]['question']+' — '+fs[i]['label']
    export = ranked.assign(response_a=ranked.a.map(label),response_b=ranked.b.map(label))
    st.caption(t(f'{len(ranked):,} paires admissibles. Classement exploratoire non pondéré ; aucune significativité statistique n’est affirmée.',
                 f'{len(ranked):,} eligible pairs. Exploratory unweighted ranking; no statistical significance is claimed.'))
    st.dataframe(export[['response_a','response_b','phi','n']].head(30),hide_index=True,use_container_width=True)
    selected = st.selectbox(t('Examiner une association','Inspect an association'),list(ranked.head(30).index),format_func=lambda k:label(ranked.loc[k,'a'])+' ↔ '+label(ranked.loc[k,'b']))
    row = ranked.loc[selected]
    a,b = fs[int(row.a)],fs[int(row.b)]
    if a['source']=='g:paysage':
        a,b=b,a
    rows,bounds = detail(cat,a,b,population)
    valid_n = int(rows.n.sum())
    st.caption(t(f'{valid_n} réponses appariées sur {int(population.sum())} répondants dans la sélection. Les autres sont exclus faute de réponse valide aux deux variables ou parce qu’ils ne sont pas admissibles à la question.',
                 f'{valid_n} paired answers out of {int(population.sum())} selected respondents. Others lack valid answers to both variables or are ineligible for the question.'))
    yes,other = rows.iloc[0],rows.iloc[1]
    other_label=t('Autres réponses valides','Other valid answers')
    st.markdown('**'+a['question']+' — '+a['label']+'**')
    st.write(t(f'Parmi les répondants « {b["label"]} » ({b["question"]}) : {yes.percent:.1f} % ({int(yes.yes)}/{int(yes.n)}), contre {other.percent:.1f} % ({int(other.yes)}/{int(other.n)}) parmi les autres réponses valides. Écart : {yes.percent-other.percent:+.1f} points.',
               f'Among respondents selecting “{b["label"]}” ({b["question"]}): {yes.percent:.1f}% ({int(yes.yes)}/{int(yes.n)}), versus {other.percent:.1f}% ({int(other.yes)}/{int(other.n)}) for other valid answers. Difference: {yes.percent-other.percent:+.1f} percentage points.'))
    if other.percent:
        st.write(t(f'Rapport de proportions : {yes.percent/other.percent:.2f}.',f'Prevalence ratio: {yes.percent/other.percent:.2f}.'))
    else:
        st.caption(t('Rapport non calculable : proportion de référence nulle.','Ratio undefined: reference proportion is zero.'))
    bars = rows.assign(group=[b['label'],other_label]).set_index('group')[['percent']]
    st.bar_chart(bars,horizontal=True)
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="240"><rect width="100%" height="100%" fill="white"/>'
    svg += f'<text x="20" y="28" font-family="Arial" font-size="14">{escape(a["question"][:95])}</text>'
    svg += f'<text x="20" y="50" font-family="Arial" font-size="13">{escape(a["label"][:95])} · {escape(b["question"][:60])}</text>'
    for j, (name, data) in enumerate(zip([b['label'],other_label], [yes,other])):
        yy = 88 + j*60
        svg += f'<text x="20" y="{yy}" font-family="Arial" font-size="13">{escape(name[:35])}</text><rect x="300" y="{yy-17}" width="{data.percent*4.5:.2f}" height="24" fill="#43866b"/><text x="765" y="{yy}" font-family="Arial" font-size="13">{data.percent:.1f}% ({int(data.yes)}/{int(data.n)})</text>'
    svg += '<text x="20" y="218" font-family="Arial" font-size="12">APRI · descriptive · 0–100% · valid paired responses · unweighted</text></svg>'
    st.download_button(t('Télécharger le graphique SVG','Download chart SVG'),svg,'association.svg','image/svg+xml')
    if bounds:
        st.caption(t(f'Écart après retrait successif d’une section : {bounds[0]:+.1f} à {bounds[1]:+.1f} points. Analyse de sensibilité, pas un intervalle de confiance.',
                     f'Difference after omitting each section: {bounds[0]:+.1f} to {bounds[1]:+.1f} points. Sensitivity analysis, not a confidence interval.'))
    st.write(t('Ces chiffres décrivent les personnes interrogées. Ils ne démontrent pas que le paysage ou un accès cause l’autre réponse. Richesse, âge, irrigation ou localisation peuvent expliquer une association. Le filtre de sous-groupe n’est pas un ajustement multivarié. Les réponses eau/toilettes sont celles du questionnaire, pas automatiquement les indicateurs normalisés d’accès sûr.',
               'These figures describe surveyed respondents. They do not show that landscape or one service causes another response. Wealth, age, irrigation or location may explain an association. Subgroup filtering is not multivariable adjustment. Water/toilet responses are questionnaire categories, not automatically standardized safely managed access indicators.'))
    st.caption(t('Rechercher beaucoup de paires favorise les associations fortuites. Avant de qualifier un lien de confirmé, il faut une analyse tenant compte des sections, des strates, des éventuels poids d’enquête et des comparaisons multiples. Aucun test naïf supposant tous les répondants indépendants n’est appliqué ici.',
                 'Searching many pairs favors chance findings. Confirmatory inference requires accounting for sections, strata, any sampling weights and multiple comparisons. No naive test treating all respondents as independent is applied here.'))
    export['population_n']=int(population.sum())
    export['minimum_margin_n']=minimum
    export['method']='Pairwise-complete binary phi; unweighted descriptive; no significance test'
    st.download_button(t('Télécharger le classement CSV','Download ranking CSV'),export.to_csv(index=False).encode('utf-8-sig'),'associations_individuelles.csv','text/csv')
    st.download_button(t('Télécharger les proportions CSV','Download proportions CSV'),rows.assign(question_a=a['question'],response_a=a['label'],question_b=b['question'],response_b=b['label']).to_csv(index=False).encode('utf-8-sig'),'association_detail.csv','text/csv')
