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


def profile_candidates(cat, dims=None, combination='mixed'):
    dims=list(['sexe','paysage','age','richesse'] if dims is None else dims)
    if not dims:return
    regs={d:LP.registry(cat,d) for d in dims}
    for size in (range(1,len(dims)+1) if combination=='mixed' else [len(dims)]):
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
    names={'sexe':t('Sexe','Sex'),'paysage':t('Paysage','Landscape'),'age':t('Âge','Age'),'richesse':t('Niveau économique','Economic level')}
    filters=st.columns([2,1,1])
    with filters[0]:dims=st.multiselect(t('Variables de profil','Profile variables'),list(names),default=list(names),format_func=lambda d:names[d],key='profile_dimensions')
    with filters[1]:combination=st.selectbox(t('Combiner les variables','Combine variables'),['mixed','combined'],format_func=lambda v:t('Mixte : seules et combinées','Mixed: individual and combined') if v=='mixed' else t('Toutes ensemble uniquement','All together only'),key='profile_combination')
    with filters[2]:direction=st.selectbox(t('Classement de φ','Phi ranking'),['mixed','positive','negative'],format_func=lambda v:{'mixed':t('Mixte : 10 hauts + 10 bas','Mixed: 10 highest + 10 lowest'),'positive':t('10 φ les plus positifs','10 most positive phi'),'negative':t('10 φ les plus négatifs','10 most negative phi')}[v],key='profile_direction')
    st.caption(t('Exemple : sexe + paysage → « toutes ensemble » compare les profils comme femme · montagne ; « mixte » inclut aussi sexe seul et paysage seul. Haut/bas décrit la fréquence du cas choisi, pas une valeur bonne ou mauvaise.', 'Example: sex + landscape → “all together” compares profiles such as woman · mountain; “mixed” also includes sex alone and landscape alone. High/low describes the selected outcome frequency, not a good or bad value.'))
    if not dims:
        st.info(t('Choisissez au moins une variable de profil.','Choose at least one profile variable.'));return
    signature=(tuple((qid,tuple(labels)) for qid,labels in conditions),mode,tuple(sorted(dims)),combination)
    if st.button(t('Afficher les profils associés','Show associated profiles'),key='outcome_compute'):
        with st.spinner(t('Comparaison des profils…','Comparing profiles…')):
            profiles=rank_family(cat,y,base,profile_candidates(cat,dims,combination))
        st.session_state.outcome_profile_results=(signature,profiles)
    result=st.session_state.get('outcome_profile_results')
    if not result or result[0]!=signature:return
    _,profiles=result
    def name(r):
        label=' · '.join(tr(L.modalite(v)) for v in r['labels'])
        return tr(L.question(r['question']))+' — '+label if r['question'] else label
    st.caption(t('p est corrigée par Holm sur tous les profils admissibles de votre sélection, positifs et négatifs, avant le top 10. Changer seulement le sens du classement ne change pas cette correction.', 'p is Holm-adjusted across all eligible profiles in your selection, positive and negative, before the top ten. Changing only the ranking direction does not change this adjustment.'))
    def show_side(positive):
        rows=sorted([r for r in profiles if r['phi']>0] if positive else [r for r in profiles if r['phi']<0],key=lambda r:-r['phi'] if positive else r['phi'])
        title=t('Les 10 profils les plus associés à une fréquence élevée du cas','The 10 profiles most associated with a higher outcome frequency') if positive else t('Les 10 profils les plus associés à une fréquence faible du cas','The 10 profiles most associated with a lower outcome frequency')
        st.markdown('**'+title+'**')
        data=[]
        for j,r in enumerate(rows[:10],1):
            prefix=t('Cas plus fréquent','Outcome more common') if positive else t('Cas moins fréquent','Outcome less common')
            reading=t(f"{prefix} : {r['with_pct']:.1f} % ({r['yes']}/{r['with_n']}), contre {r['without_pct']:.1f} % chez les autres.",f"{prefix}: {r['with_pct']:.1f}% ({r['yes']}/{r['with_n']}), versus {r['without_pct']:.1f}% among others.")
            data.append({t('Rang','Rank'):j,t('Profil','Profile'):name(r),'φ':round(r['phi'],3),t('Interprétation de φ','Interpretation of phi'):reading,t('p corrigée (Holm)','Adjusted p (Holm)'):r['p_holm'],t('Interprétation de p','Interpretation of p'):LP.decision(r,t)})
        if data:st.dataframe(pd.DataFrame(data).round(4),hide_index=True,use_container_width=True)
        else:st.info(t('Aucun profil calculable dans ce sens.','No calculable profile in this direction.'))
        if len(rows)<10:st.caption(t(f'{len(rows)} profils admissibles dans ce sens : la liste contient moins de dix lignes.',f'{len(rows)} eligible profiles in this direction: fewer than ten rows are available.'))
    if direction in ('mixed','positive'):show_side(True)
    if direction in ('mixed','negative'):show_side(False)
    st.markdown(t('**φ = force et sens du lien.** Positif : cas plus fréquent dans le profil ; négatif : moins fréquent. Plus |φ| est proche de 1, plus le lien binaire est fort ; près de 0, il est faible. φ = 0,3 ne signifie pas 30 % de risque.', '**Phi = strength and direction of the association.** Positive: outcome more common in the profile; negative: less common. The closer |phi| is to 1, the stronger the binary association; near 0 means a weak one. Phi = 0.3 does not mean 30% risk.'))
    st.markdown(t('**p corrigée = lecture statistique après recherche de nombreux profils.** À 0,05 ou moins, le lien franchit le seuil sous les hypothèses du test. Au-delà, les données ne suffisent pas à le confirmer : cela ne prouve pas son absence. Une petite p ne mesure pas la force du lien et ne prouve pas une cause.', '**Adjusted p = statistical evidence after searching many profiles.** At 0.05 or below, the association meets the threshold under the test assumptions. Above it, the data do not suffice to confirm it: this does not prove its absence. A small p measures neither association strength nor causation.'))
    with st.expander(t('Méthode et limites','Method and limitations')):
        st.write(t(f'{len(profiles)} profils examinés, y compris les liens négatifs, dans la correction de Holm. Les profils se chevauchent. La correction couvre cette recherche, pas vos recherches successives. Des p corrigées identiques sur plusieurs lignes sont possibles, même si les φ diffèrent.', f'{len(profiles)} profiles, including negative associations, enter the Holm adjustment. Profiles overlap. Adjustment covers this search, not repeated searches. Adjusted p-values can be identical across rows even when phi differs.'))
        st.write(t('Au moins 30 observations pour chaque niveau du cas et du profil. Les doublons exacts et les profils identiques ou inverses du cas sont exclus. Les réponses manquantes ne sont jamais comptées comme non. Les cultures sont limitées aux répondants déclarant pratiquer l’agriculture. Les effectifs peuvent varier selon les caractéristiques disponibles.', 'At least 30 observations at each level of the outcome and profile. Exact duplicates and profiles identical or inverse to the outcome are excluded. Missing responses never count as no. Crops are restricted to respondents reporting farming. Sample sizes may vary with available characteristics.'))
        st.write(t('La p-value teste l’absence d’écart de proportion : sous cette hypothèse et celles du modèle, elle mesure la fréquence de résultats au moins aussi extrêmes. Ce n’est pas la probabilité que le lien soit faux. Test bilatéral wild cluster bootstrap-t, regroupé par section, puis correction de Holm. Les tests non calculables comptent comme p = 1 dans la correction mais restent affichés comme indisponibles.', 'The p-value tests no difference in proportions: under that hypothesis and model assumptions, it measures the frequency of results at least as extreme. It is not the probability that the association is false. Two-sided wild cluster bootstrap-t grouped by section, then Holm adjustment. Uncomputable tests enter adjustment as p = 1 but remain displayed as unavailable.'))
        st.write(t('Dix sections restent peu : ces tests sont approximatifs et supposent des sections indépendantes. Pas de pondération de population ni d’ajustement des profils entre eux. Les résultats restent exploratoires et ne démontrent pas des causes.', 'Ten sections remain few: these tests are approximate and assume independent sections. No population weighting or adjustment between profiles. Results remain exploratory and do not demonstrate causes.'))
        st.markdown('[Wild cluster bootstrap — Stata](https://www.stata.com/manuals/rwildbootstrap.pdf)')
