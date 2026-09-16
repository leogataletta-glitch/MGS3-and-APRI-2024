"""Explore household outcomes defined by one or more question/answer conditions."""
import itertools
import numpy as np
import pandas as pd
import streamlit as st
import i18n
import croisement_moteur as M
import liens_profils as LP
import liens_inference as I
import themes_enquete as T
import libelles_enquete as L
from traductions import text as tr


def outcome(cat, conditions, mode='all'):
    masks=[];bases=[]
    byid={q['i']:q for q in cat['questions']}
    for qid,labels in conditions:
        answers,base=LP.answers(cat,byid[qid])
        if not labels or any(label not in answers for label in labels):raise ValueError('Choose valid answers')
        masks.append(np.logical_or.reduce([answers[label] for label in labels]));bases.append(base)
    if not masks:raise ValueError('Choose a question')
    # Complete cases for every selected question, for both AND and OR.
    base=np.logical_and.reduce(bases)
    y=(np.logical_and.reduce(masks) if mode=='all' else np.logical_or.reduce(masks)) & base
    return y,base


def candidates(cat, excluded):
    names={M._norm(q['question']) for q in cat['questions'] if q['i'] in excluded}
    for q in cat['questions']:
        if q['i'] in excluded or M._norm(q['question']) in names:continue
        masks,base=LP.answers(cat,q)
        labels=list(masks)
        if len(labels)==2 and not (masks[labels[0]] & masks[labels[1]]).any():labels=['Oui'] if 'Oui' in masks else labels[:1]
        for label in labels:yield dict(question=q['question'],labels=(label,),mask=masks[label],base=base)


def profile_candidates(cat):
    dims=['sexe','paysage','age','richesse'];regs={d:LP.registry(cat,d) for d in dims}
    for size in range(1,5):
        for ds in itertools.combinations(dims,size):
            base=np.logical_and.reduce([regs[d][1] for d in ds])
            for labels in itertools.product(*[list(regs[d][0]) for d in ds]):
                mask=base.copy()
                for d,label in zip(ds,labels):mask &= regs[d][0][label]
                yield dict(question='',labels=labels,mask=mask,base=base)


def rank_family(cat,y,base,items):
    rows=[];seen=set();sections=I.section_ids(cat)
    for item in items:
        common=base & item['base'];z=item['mask'] & common
        n=int(common.sum());a=int((y & common).sum());b=int(z.sum());both=int((y & z).sum())
        if min(a,n-a,b,n-b)<30:continue
        signature=common.tobytes()+z.tobytes()
        if signature in seen:continue
        seen.add(signature)
        phi=(n*both-a*b)/np.sqrt(float(a*(n-a)*b*(n-b)))
        # Exclude tautologies/duplicates of the selected outcome.
        if abs(phi)>=1-1e-12:continue
        stat=I.test(y[common],z[common],sections[common])
        rows.append(dict(question=item['question'],labels=item['labels'],phi=phi,n=n,yes=both,with_n=b,without_n=n-b,with_pct=100*both/b,without_pct=100*(a-both)/(n-b),p=stat['p'],sections=stat['sections'],reason=stat['reason']))
    for r,p in zip(rows,I.holm([r['p'] for r in rows])):r['p_holm']=p
    return sorted(rows,key=lambda r:-abs(r['phi']))


def render(cat):
    fr=i18n.get_lang()=='fr'
    def t(a,b):return tr(a if fr else b)
    if not cat:st.info(t('Données indisponibles.','Data unavailable.'));return
    qs={q['i']:q for q in cat['questions'] if len(LP.answers(cat,q)[0])>1}
    codes=[c for c in [c for c,_,_ in T.THEMES]+[T.CALCULE,T.AUTRES] if any(T.theme_de(q.get('category'))==c for q in qs.values())]
    st.caption(t('Choisissez ce que vous voulez étudier : thème → question → une ou plusieurs réponses.','Choose what to study: theme → question → one or more answers.'))
    count=st.session_state.get('outcome_count',1)
    conditions=[];descriptions=[]
    for j in range(count):
        cols=st.columns([1,2,2]);prefix=f'outcome_{j}'
        with cols[0]:theme=st.selectbox(t('Thème','Theme'),['__all__']+codes,format_func=lambda c:t('Tous les thèmes','All themes') if c=='__all__' else tr(i18n.T(T.libelle(c))),key=prefix+'_theme')
        visible=[k for k,q in qs.items() if theme=='__all__' or T.theme_de(q.get('category'))==theme]
        used={k for k,_ in conditions};visible=[k for k in visible if k not in used]
        if st.session_state.get(prefix+'_question') not in visible:st.session_state[prefix+'_question']=None
        with cols[1]:qid=st.selectbox(t('Question','Question'),visible,index=None,format_func=lambda k:tr(L.question(qs[k]['question'])),placeholder=t('Tapez un mot-clé…','Type a keyword…'),key=prefix+'_question')
        with cols[2]:
            options=list(LP.answers(cat,qs[qid])[0]) if qid is not None else []
            labels=st.multiselect(t('Réponse(s) étudiée(s)','Answer(s) of interest'),options,format_func=lambda v:tr(L.modalite(v)),key=prefix+f'_answers_{qid}',placeholder=t('Choisir une ou plusieurs réponses','Choose one or more answers'),disabled=qid is None)
        if qid is not None and labels:
            conditions.append((qid,labels));descriptions.append(tr(L.question(qs[qid]['question']))+' : '+(' '+t('OU','OR')+' ').join(tr(L.modalite(v)) for v in labels))
    controls=st.columns([1,1,2])
    with controls[0]:
        if st.button(t('+ Ajouter une question','+ Add a question'),key='outcome_add'):
            st.session_state.outcome_count=count+1;st.rerun()
    with controls[1]:
        if count>1 and st.button(t('Retirer la dernière question','Remove last question'),key='outcome_remove'):
            st.session_state.outcome_count=count-1;st.rerun()
    mode='all'
    with controls[2]:
        if count>1:mode=st.selectbox(t('Combiner les questions','Combine questions'),['all','any'],format_func=lambda v:t('Toutes les conditions (ET)','All conditions (AND)') if v=='all' else t('Au moins une condition (OU)','At least one condition (OR)'),key='outcome_mode')
    st.caption(t('Plusieurs réponses d’une question = l’une OU l’autre. Plusieurs questions = ET ou OU, au choix.','Several answers to one question = any selected answer. Several questions = AND or OR, your choice.'))
    if len(conditions)!=count:return
    y,base=outcome(cat,conditions,mode);n=int(base.sum());k=int(y.sum())
    st.write((' **'+t('ET','AND')+'** ' if mode=='all' else ' **'+t('OU','OR')+'** ').join(descriptions))
    st.write(t(f'{k} ménages sur {n} réponses complètes ({100*k/n:.1f} %).' if n else 'Aucune réponse complète.',f'{k} households out of {n} complete responses ({100*k/n:.1f}%).' if n else 'No complete responses.'))
    st.caption(t('Les réponses manquantes à une question sélectionnée sont exclues, même en mode OU. Sexe et âge décrivent le répondant, pas chaque membre du ménage.','Missing responses to any selected question are excluded, including in OR mode. Sex and age describe the respondent, not every household member.'))
    if min(k,n-k)<30:
        st.info(t('Il faut au moins 30 ménages concernés et 30 autres pour établir ces classements. Modifiez la sélection.','At least 30 affected and 30 other households are required for these rankings. Change the selection.'));return
    signature=(tuple((qid,tuple(labels)) for qid,labels in conditions),mode)
    if st.button(t('Afficher les facteurs et profils associés','Show associated factors and profiles'),key='outcome_compute'):
        with st.spinner(t('Comparaison des réponses et des profils…','Comparing answers and profiles…')):
            factors=rank_family(cat,y,base,candidates(cat,{qid for qid,_ in conditions}))
            profiles=rank_family(cat,y,base,profile_candidates(cat))
        st.session_state.outcome_results=(signature,factors,profiles)
    result=st.session_state.get('outcome_results')
    if not result or result[0]!=signature:return
    _,factors,profiles=result
    def name(r):
        label=' · '.join(tr(L.modalite(v)) for v in r['labels'])
        return tr(L.question(r['question']))+' — '+label if r['question'] else label
    def table(rows,profile=False):
        data=[]
        for j,r in enumerate(rows[:10],1):
            data.append({t('Rang','Rank'):j,t('Profil','Profile') if profile else t('Facteur observé','Observed factor'):name(r),'φ':round(r['phi'],3),t('Cas étudié dans ce groupe','Selected outcome in this group'):f"{r['with_pct']:.1f}% ({r['yes']}/{r['with_n']})",t('Chez les autres','Among others'):f"{r['without_pct']:.1f}% (n={r['without_n']})"})
        if data:st.dataframe(pd.DataFrame(data),hide_index=True,use_container_width=True)
        else:st.info(t('Pas assez de liens calculables.','Not enough calculable associations.'))
    st.markdown('**'+t('Les 10 facteurs les plus associés au cas choisi','The 10 factors most associated with the selected outcome')+'**')
    st.caption(t('Autres questions et réponses, classées par force du lien |φ|. + : cas plus fréquent ; − : cas moins fréquent. Ce ne sont pas des causes démontrées.','Other questions and answers, ranked by association strength |phi|. +: outcome more common; −: less common. These are not proven causes.'))
    table(factors)
    st.markdown('**'+t('Les 10 profils les plus associés à une fréquence élevée du cas','The 10 profiles most associated with a higher outcome frequency')+'**')
    positive=sorted([r for r in profiles if r['phi']>0],key=lambda r:-r['phi'])
    st.caption(t('Sexe, paysage, âge et niveau économique, seuls ou combinés. Classement par φ positif ; la proportion concernée est indiquée pour chaque profil.','Sex, landscape, age and economic level, alone or combined. Ranked by positive phi; the affected share is shown for each profile.'))
    table(positive,True)
    with st.expander(t('Tests statistiques : p, correction et effectifs','Statistical tests: p, adjustment and sample sizes')):
        data=[]
        for kind,rows in ((t('Facteur','Factor'),factors[:10]),(t('Profil','Profile'),positive[:10])):
            for r in rows:data.append({t('Type','Type'):kind,t('Lien','Association'):name(r),'φ':r['phi'],'p':r['p'],'p (Holm)':r['p_holm'],t('Sections','Sections'):r['sections'],t('Réponses communes','Shared responses'):r['n'],t('Lecture','Interpretation'):LP.decision(r,t)})
        st.dataframe(pd.DataFrame(data).round(4),hide_index=True,use_container_width=True)
        st.caption(t(f'Holm est calculé avant le top 10 sur {len(factors)} facteurs et, séparément, {len(profiles)} profils (y compris négatifs).',f'Holm is applied before the top 10 across {len(factors)} factors and, separately, {len(profiles)} profiles (including negative associations).'))
    with st.expander(t('Comment lire les résultats, pas à pas','How to read the results, step by step')):
        st.markdown(t('1. **Définir le cas** avec vos réponses, par exemple la défécation à l’air libre.\n2. **Comparer deux groupes** : ceux qui ont l’autre réponse (ou appartiennent au profil), et les autres, sur les mêmes réponses disponibles.\n3. **Lire φ** : de −1 à +1 ; près de zéro, peu de lien binaire. Ce n’est ni un pourcentage ni une probabilité.\n4. **Lire les proportions et effectifs** pour comprendre concrètement le résultat. Les profils peuvent se chevaucher.\n5. **Ouvrir les tests** : p mesure la compatibilité avec l’hypothèse d’absence de lien, sous les hypothèses du test. Holm corrige la recherche de nombreux liens. Une p corrigée ≤ 0,05 franchit le seuil ; sinon, le lien n’est pas confirmé par ce test. Cela ne prouve ni une cause ni une absence de lien.', '1. **Define the outcome** with your answers, for example open defecation.\n2. **Compare two groups**: those with another answer (or in a profile), and others, using shared available responses.\n3. **Read phi**: −1 to +1; near zero means little binary association. It is neither a percentage nor a probability.\n4. **Read proportions and counts** to understand the result. Profiles may overlap.\n5. **Open the tests**: p measures compatibility with no association under test assumptions. Holm adjusts for searching many associations. Adjusted p ≤ 0.05 meets the threshold; otherwise the test does not confirm the association. Neither result proves causation or absence of an association.'))
        st.write(t('Minimum 30 observations de chaque côté pour le cas et le facteur. Même question source, doublons exacts et réponses identiques ou inverses du cas sont exclus. Deux réponses complémentaires d’une question binaire représentent un seul lien. Les questions sélectionnées définissent le cas : elles ne sont pas retestées comme facteurs. Les réponses non cochées sont comparées aux autres réponses valides, jamais aux valeurs manquantes. Les cultures sont limitées aux répondants déclarant pratiquer l’agriculture.', 'At least 30 observations at each level of the outcome and factor. Same-source questions, exact duplicates and outcomes identical or inverse to the target are excluded. Complementary answers to a binary question represent one association. Selected questions define the outcome and are not retested as factors. Unselected answers are compared with other valid responses, never missing values. Crops are restricted to respondents reporting farming.'))
        st.write(t('Tests exploratoires par wild cluster bootstrap-t regroupé par section, avec les conditions d’effectif et de répartition du module statistique. Dix sections restent peu ; p est approximative, suppose des sections indépendantes et peut être indisponible. Holm couvre chaque famille de cette recherche, pas les recherches successives. Les listes sont descriptives, sans pondération de population ni ajustement des facteurs entre eux : elles n’identifient pas des déterminants causaux. Une p corrigée peut être identique sur plusieurs lignes sans que φ le soit.', 'Exploratory wild cluster bootstrap-t tests grouped by section, subject to the statistical module’s sample and support checks. Ten sections remain few; p is approximate, assumes independent sections and may be unavailable. Holm covers each family in this search, not repeated searches. Lists are descriptive, without population weighting or mutual factor adjustment: they do not identify causal determinants. Adjusted p can be identical across rows even when phi differs.'))
        st.markdown('[Wild cluster bootstrap — Stata](https://www.stata.com/manuals/rwildbootstrap.pdf)')
