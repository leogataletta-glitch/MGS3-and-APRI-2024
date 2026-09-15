"""Respondent-level descriptive associations; never impute skipped answers."""
import re
from html import escape
import numpy as np
import pandas as pd
import streamlit as st
import i18n
import libelles_enquete as L
import croisement_moteur as M


def substantive(label):
    v = M._norm(label)
    return not any(x in v for x in ('ne sait pas', 'ne souhaite pas', 'non precise',
                                    'non reponse', 'sans reponse', 'non renseigne',
                                    'not applicable', 'non applicable', 'refus'))


def question_masks(cat, q):
    """Unknown/refusal-only records stay outside the denominator."""
    masks = {m: cat['bits'][q['debut'] + j].copy()
             for j, m in enumerate(q['modalites']) if substantive(m)}
    base = np.logical_or.reduce(list(masks.values())) if masks else np.zeros(cat['n'], bool)
    return masks, base


def cluster_interval(y, sections):
    """Percentile bootstrap of entire sections, not individual respondents.

    Conditional within each displayed group; no CI for the difference or p-value.
    Fewer than four represented sections: only descriptive point estimates.
    """
    keys = np.unique(sections)
    if len(keys) < 4 or '' in keys:
        return None, None
    counts = np.array([np.sum(sections == k) for k in keys])
    successes = np.array([np.sum(y[sections == k]) for k in keys])
    rng = np.random.default_rng(2024)
    draws = rng.integers(0, len(keys), size=(2000, len(keys)))
    estimates = successes[draws].sum(axis=1) / counts[draws].sum(axis=1) * 100
    lo, hi = np.percentile(estimates, [2.5, 97.5])
    return float(lo), float(hi)


def analyse(cat, target, target_base, groups, population):
    section = np.full(cat['n'], '', dtype=object)
    membership = np.zeros(cat['n'], int)
    for name in M.SECTIONS:
        mask = cat['groupes'].get(name, np.zeros(cat['n'], bool))
        section[mask] = name
        membership += mask
    section[membership != 1] = ''
    # An exclusive comparison: conflicting group answers are excluded, not duplicated.
    group_count = sum((m.astype(int) for m in groups.values()), np.zeros(cat['n'], int))
    valid = population & target_base & (group_count == 1)
    rows = []
    for name, mask in groups.items():
        eligible = valid & mask
        n = int(eligible.sum())
        k = int((eligible & target).sum())
        if not n:
            continue
        lo, hi = cluster_interval(target[eligible], section[eligible])
        rows.append(dict(group=name, n=n, yes=k, percent=100*k/n,
                         low=lo, high=hi, sections=len(set(section[eligible]) - {''})))
    return pd.DataFrame(rows), dict(population=int(population.sum()), used=int(valid.sum()),
        missing_target=int((population & ~target_base).sum()),
        missing_group=int((population & target_base & (group_count == 0)).sum()),
        conflicting_group=int((population & target_base & (group_count > 1)).sum()))


def chart_svg(rows, title):
    width, height = 900, 105 + 64 * len(rows)
    pieces = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
              '<rect width="100%" height="100%" fill="white"/>',
              f'<text x="20" y="27" font-family="Arial" font-size="15" fill="#245442">{escape(title[:105])}</text>',
              '<g font-family="Arial" font-size="10" fill="#718076"><text x="270" y="43">0%</text><text x="485" y="43">50%</text><text x="695" y="43">100%</text></g>']
    for i, r in enumerate(rows.to_dict('records')):
        y = 61 + i*64
        pieces += [f'<text x="20" y="{y}" font-family="Arial" font-size="13" fill="#3c5147">{escape(str(r["group"])[:34])}</text>',
                   f'<rect x="270" y="{y-13}" width="450" height="20" rx="5" fill="#eff3ef"/>',
                   f'<rect x="270" y="{y-13}" width="{r["percent"]*4.5:.2f}" height="20" rx="5" fill="#72a38d"/>',
                   f'<text x="735" y="{y+1}" font-family="Arial" font-size="13" fill="#245442">{r["percent"]:.1f}% · {r["yes"]}/{r["n"]}</text>']
        if pd.notna(r['low']) and pd.notna(r['high']):
            a, b = 270+r['low']*4.5, 270+r['high']*4.5
            pieces.append(f'<path d="M{a},{y-3}H{b}M{a},{y-8}V{y+2}M{b},{y-8}V{y+2}" stroke="#244d42" stroke-width="2"/>')
    pieces.append(f'<text x="20" y="{height-14}" font-family="Arial" font-size="11" fill="#718076">APRI · descriptive association · section bootstrap 95% · unweighted</text></svg>')
    return ''.join(pieces)


def render(cat):
    fr = i18n.get_lang() == 'fr'
    t = lambda a,b: a if fr else b
    if not cat:
        st.info(t('Les réponses individuelles ne sont pas disponibles.', 'Individual responses are unavailable.'))
        return
    import relations_guide
    relations_guide.render(fr)
    view = st.radio(t('Explorer les relations', 'Explore relationships'), ['manual', 'individual', 'indicators', 'mixed'],
        format_func=lambda k: {'manual':t('Comparaison détaillée','Detailed comparison'), 'individual':t('Variables ↔ variables','Variables ↔ variables'), 'indicators':t('Indicateurs ↔ indicateurs','Indicators ↔ indicators'), 'mixed':t('Indicateurs ↔ variables','Indicators ↔ variables')}[k], horizontal=True)
    if view == 'individual':
        import associations_individuelles
        associations_individuelles.render(cat)
        return
    if view in ('indicators', 'mixed'):
        import correlations_sections
        correlations_sections.render(cat, fixed_mode='indicators' if view == 'indicators' else 'variables')
        return
    questions = [q for q in cat['questions'] if len(q['modalites']) > 1]
    lookup = {q['i']: q for q in questions}
    rice = next((q['i'] for q in questions if 'Riz' in q['modalites'] and M._norm(q['question']) == 'cultures pratiquees'), questions[0]['i'])
    st.caption(t('Comparez des réponses observées. Une association ne démontre pas un effet causal.',
                 'Compare observed answers. An association does not establish a causal effect.'))
    left, right = st.columns(2)
    with left:
        qid = st.selectbox(t('Variable à expliquer', 'Outcome variable'), list(lookup),
            index=list(lookup).index(rice), format_func=lambda k: L.libelle(lookup[k]), key='rel_y')
    registers = dict(M.REGISTRES)
    options = ['g:'+k for k in registers] + ['q:'+str(k) for k in lookup]
    reg_names = dict(paysage=t('Paysage','Landscape'), sexe=t('Sexe','Sex'), age=t('Tranche d’âge','Age group'),
                     richesse=t('Strate de richesse','Wealth stratum'), section=t('Section communale','Communal section'))
    with right:
        x = st.selectbox(t('Variable de comparaison','Comparison variable'), options,
            index=options.index('g:paysage'), format_func=lambda k: reg_names[k[2:]] if k.startswith('g:') else L.libelle(lookup[int(k[2:])]), key='rel_x')
    q = lookup[qid]
    masks, base = question_masks(cat, q)
    if not masks:
        st.info(t('Aucune réponse exploitable.', 'No usable answers.'))
        return
    target_name = st.selectbox(t('Réponse étudiée','Answer of interest'), list(masks),
        index=list(masks).index('Riz') if 'Riz' in masks else 0, key=f'rel_mod_{qid}')
    population = np.ones(cat['n'], bool)
    farmers = False
    chosen = []
    agricult = next((a for a in questions if M._norm(a['question']) == 'pratique personnellement l agriculture'), None)
    if agricult:
        farmers = st.toggle(t('Seulement les répondants pratiquant l’agriculture','Only respondents practising agriculture'),
                            value=qid == rice, key=f'rel_agri_{qid}')
        if farmers:
            ag, _ = question_masks(cat, agricult)
            population &= ag.get('Oui', np.zeros(cat['n'], bool))
    # An optional stratification lets users inspect e.g. irrigation categories without claiming adjustment.
    with st.expander(t('Restreindre à une réponse ou un sous-groupe','Restrict to an answer or subgroup')):
        fqid = st.selectbox(t('Question de filtre','Filter question'), [None]+list(lookup),
                            format_func=lambda k: t('Aucun filtre','No filter') if k is None else L.libelle(lookup[k]), key='rel_fq')
        if fqid is not None:
            fm, _ = question_masks(cat, lookup[fqid])
            chosen = st.multiselect(t('Réponses retenues (au moins une)','Included answers (at least one)'), list(fm), key=f'rel_fm_{fqid}')
            if not chosen:
                st.info(t('Choisissez une réponse pour appliquer ce filtre.','Choose an answer to apply this filter.'))
                return
            population &= np.logical_or.reduce([fm[m] for m in chosen])
    if x.startswith('g:'):
        groups = {v:cat['groupes'].get(v,np.zeros(cat['n'],bool)) for v in registers[x[2:]]}
    else:
        xq = lookup[int(x[2:])]
        if xq['i'] == qid:
            st.info(t('Choisissez deux variables différentes.','Choose two different variables.'))
            return
        xm, xb = question_masks(cat, xq)
        overlaps = sum((m.astype(int) for m in xm.values()), np.zeros(cat['n'],int)) > 1
        if overlaps.any():
            if not xm:
                return
            xm_name = st.selectbox(t('Réponse de comparaison','Comparison answer'), list(xm),key=f'rel_xm_{xq["i"]}')
            groups = {xm_name:xm[xm_name], t('Autres réponses valides','Other valid answers'):xb & ~xm[xm_name]}
        else:
            groups = xm
    rows, counts = analyse(cat,masks[target_name],base,groups,population)
    st.caption(t(f'{counts["used"]} répondants analysés sur {counts["population"]} dans la population retenue. ',
                 f'{counts["used"]} respondents analysed out of {counts["population"]} in the selected population. ')+
        t(f'Exclus : {counts["missing_target"]} sans réponse exploitable à la question étudiée ; {counts["missing_group"]} sans groupe ; {counts["conflicting_group"]} groupes contradictoires.',
          f'Excluded: {counts["missing_target"]} without a usable outcome; {counts["missing_group"]} without a group; {counts["conflicting_group"]} conflicting groups.'))
    if rows.empty:
        st.info(t('Aucune observation comparable avec ces choix.','No comparable observations for these selections.'))
        return
    st.caption(t('Dénominateur : réponses valides à la question, dans chaque groupe. Non-réponse, refus et question non posée ne valent jamais « non ».',
                 'Denominator: valid answers to the question in each group. Missing, refused and skipped answers never count as “no”.'))
    svg = chart_svg(rows, f'{q["question"]} · {target_name}')
    import streamlit.components.v1 as components
    components.html('<div style="width:100%;overflow:auto">'+svg.replace('width="900"', 'style="width:100%;min-width:600px"')+'</div>', height=115+64*len(rows), scrolling=True)
    if len(rows) == 2:
        a,b = rows.iloc[0], rows.iloc[1]
        st.markdown(t(f'**{a["group"]} : {a.percent:.1f} %**, contre **{b["group"]} : {b.percent:.1f} %**. Écart observé : **{a.percent-b.percent:+.1f} points**.',
                      f'**{a["group"]}: {a.percent:.1f}%**, versus **{b["group"]}: {b.percent:.1f}%**. Observed difference: **{a.percent-b.percent:+.1f} percentage points**.'))
    if (rows.n < 30).any():
        st.info(t('Certains groupes ont moins de 30 répondants : leurs résultats sont fragiles.','Some groups have fewer than 30 respondents: interpret them cautiously.'))
    st.caption(t('Traits : intervalle exploratoire à 95 %, obtenu en rééchantillonnant les sections communales entières (2 000 tirages). Aucun intervalle si moins de 4 sections ou section inconnue. Avec seulement 10 sections dans l’enquête, ces intervalles restent approximatifs.',
                 'Lines: exploratory 95% interval from resampling whole communal sections (2,000 draws). No interval with fewer than 4 sections or unknown sections. With only 10 sections in the survey, intervals remain approximate.'))
    with st.expander(t('Méthode et tableau des effectifs','Method and counts')):
        st.dataframe(rows,hide_index=True,use_container_width=True)
        st.write(t('Analyse descriptive non pondérée des personnes interrogées, pas une estimation représentative de toute la population. Aucun test de significativité ni modèle causal. Les filtres permettent de regarder un sous-groupe, sans constituer un ajustement multivarié. Le catalogue fournit des catégories et des tranches : elles ne sont pas converties en valeurs numériques fictives.',
                   'Unweighted descriptive analysis of surveyed respondents, not a representative population estimate. No significance test or causal model. Filters inspect subgroups; they are not multivariable adjustment. The catalogue contains categories and ranges: these are not converted into invented numeric values.'))
        st.write(t('Question source : ','Source question: ')+q['question'])
        st.caption(t('Les effectifs ci-dessus sont recalculés ; les anciens effectifs dans les notes du questionnaire ne sont pas utilisés.',
                     'Counts above are recomputed; old counts in questionnaire notes are not used.'))
    export = rows.assign(question=q['question'],response=target_name,comparison=x,
        agriculture_only=farmers, filter_question=lookup[fqid]['question'] if fqid is not None else '',
        filter_answers=' | '.join(chosen), population_n=counts['population'],
        missing_outcome=counts['missing_target'],missing_group=counts['missing_group'],
        conflicting_group=counts['conflicting_group'],
        method='Unweighted; section bootstrap 2000 draws, 95%; descriptive, no causal interpretation')
    a,b=st.columns(2)
    a.download_button(t('Télécharger les résultats CSV','Download results CSV'),export.to_csv(index=False).encode('utf-8-sig'),'relations.csv','text/csv',key='rel_csv')
    b.download_button(t('Télécharger le graphique SVG','Download chart SVG'),svg,'relations.svg','image/svg+xml',key='rel_svg')
