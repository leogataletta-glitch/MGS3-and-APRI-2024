"""One outcome, descriptive group comparisons, crossed profiles and focused links."""
import itertools
import numpy as np
import pandas as pd
import streamlit as st
import i18n
import croisement_moteur as M
import libelles_enquete as L
from traductions import text as tr


def answers(cat, q):
    from relations_resultats import substantive
    masks = {m:cat['bits'][q['debut']+j].copy() for j,m in enumerate(q['modalites'])}
    good = {m:v for m,v in masks.items() if substantive(m) and not any(x in M._norm(m) for x in ('sais pas','sans objet','inconnu','manquant'))}
    base = np.logical_or.reduce(list(good.values())) if good else np.zeros(cat['n'],bool)
    bad = [v for m,v in masks.items() if m not in good]
    if bad: base &= ~np.logical_or.reduce(bad)
    if 'unique' in M._norm(q.get('note','')): base &= np.sum(list(masks.values()),axis=0)==1
    if M._norm(q['question']) == 'cultures pratiquees':
        ag = next((a for a in cat['questions'] if M._norm(a['question'])=='pratique personnellement l agriculture'),None)
        if ag:
            am,ab=answers(cat,ag);base &= ab & am.get('Oui',np.zeros(cat['n'],bool))
        else: base[:]=False
    return {m:v & base for m,v in good.items()},base


def registry(cat,key):
    masks={v:cat['groupes'].get(v,np.zeros(cat['n'],bool)) for v in dict(M.REGISTRES)[key]}
    base=np.sum(list(masks.values()),axis=0)==1
    return {k:v & base for k,v in masks.items()},base


def proportions(y,base,groups):
    rows=[]
    for name,mask in groups.items():
        v=base & mask;n=int(v.sum());k=int((v & y).sum())
        if n: rows.append(dict(group=name,n=n,yes=k,percent=100*k/n))
    return pd.DataFrame(rows,columns=['group','n','yes','percent'])


def profiles(cat,y,base,dimensions,minimum=30):
    registries=[registry(cat,d) for d in dimensions]
    valid=base.copy()
    for _,b in registries:valid &= b
    masks={}
    for combo in itertools.product(*[list(m) for m,_ in registries]):
        mask=valid.copy()
        for name,(m,_) in zip(combo,registries):mask &= m[name]
        masks[' · '.join(combo)]=mask
    rows=proportions(y,valid,masks)
    return rows[rows.n>=minimum].sort_values(['percent','n'],ascending=False),int(valid.sum()),int((rows.n<minimum).sum())


def focused_links(cat,qid,y,base):
    target=next(q for q in cat['questions'] if q['i']==qid)
    candidates=[]
    for q in cat['questions']:
        if q['i']==qid or M._norm(q['question'])==M._norm(target['question']):continue
        masks,v=answers(cat,q)
        labels=list(masks)
        if len(labels)==2 and not (masks[labels[0]] & masks[labels[1]]).any():labels=['Oui'] if 'Oui' in masks else labels[:1]
        for label in labels:candidates.append((q['question'],label,masks[label],v,'question'))
    for key,_ in M.REGISTRES:
        if key=='section':continue
        masks,v=registry(cat,key)
        labels=list(masks)
        if len(labels)==2:labels=labels[:1]
        for label in labels:candidates.append((key,label,masks[label],v,'profile'))
    rows=[]
    for question,label,z,v,kind in candidates:
        common=base & v;n=int(common.sum());a=int((common & y).sum());b=int((common & z).sum());both=int((common & y & z).sum())
        if min(a,n-a,b,n-b)<30:continue
        phi=(n*both-a*b)/np.sqrt(float(a*(n-a)*b*(n-b)))
        if abs(phi)>=1-1e-12:continue
        rows.append(dict(question=question,label=label,kind=kind,phi=phi,n=n,with_pct=100*both/b,without_pct=100*(a-both)/(n-b),with_n=b,without_n=n-b))
    rows.sort(key=lambda r:abs(r['phi']),reverse=True)
    return rows


def render(cat):
    fr=i18n.get_lang()=='fr'
    def t(a,b):return tr(a if fr else b)
    names={'paysage':t('Paysage','Landscape'),'sexe':t('Sexe du répondant','Respondent sex'),'age':t('Âge du répondant','Respondent age'),'richesse':t('Strate économique','Economic stratum'),'section':t('Section communale','Communal section')}
    if not cat:st.info(t('Données indisponibles.','Data unavailable.'));return
    st.caption(t('Choisissez une réponse : voyez où elle est fréquente, chez quels profils et avec quelles autres réponses elle va ensemble.','Choose an answer: see where it is common, which profiles report it and which other answers go with it.'))
    qs={q['i']:q for q in cat['questions'] if len(q['modalites'])>1}
    cols=st.columns([2,1])
    with cols[0]:qid=st.selectbox(t('Question à explorer','Question to explore'),list(qs),index=None,format_func=lambda k:tr(L.question(qs[k]['question'])),key='lp_question',placeholder=t('Rechercher : toilettes, cultures…','Search: toilets, crops…'))
    if qid is None:return
    masks,base=answers(cat,qs[qid])
    if not masks:st.info(t('Aucune réponse exploitable.','No usable answers.'));return
    with cols[1]:label=st.selectbox(t('Réponse étudiée','Answer of interest'),list(masks),format_func=lambda v:tr(L.modalite(v)),key=f'lp_answer_{qid}')
    y=masks[label];n=int(base.sum());k=int(y.sum())
    st.write(t(f'{k} réponses sur {n} réponses valides ({100*k/n:.1f} %).' if n else 'Aucune réponse valide.',f'{k} of {n} valid responses ({100*k/n:.1f}%).' if n else 'No valid answers.'))
    st.caption(t('Les cultures sont étudiées parmi les répondants déclarant pratiquer l’agriculture. Sexe et âge décrivent le répondant : pour une question sur le ménage, ce n’est pas une mesure individuelle de chaque femme ou enfant.','Crops are studied among respondents reporting practising agriculture. Sex and age describe the respondent; household answers do not measure each woman or child individually.'))
    st.markdown('**'+t('1. Comparer avec une variable','1. Compare with a variable')+'**')
    dim=st.selectbox(t('Comparer selon','Compare by'),list(names),format_func=lambda v:names[v],key='lp_compare')
    gm,gb=registry(cat,dim);rows=proportions(y,base & gb,gm)
    if not rows.empty:
        shown=rows.copy();shown['group']=shown.group.map(lambda x:tr(L.modalite(x)))
        st.dataframe(shown.rename(columns={'group':t('Groupe','Group'),'n':t('Réponses valides','Valid answers'),'yes':t('Réponse étudiée','Selected answer'),'percent':t('Part (%)','Share (%)')}).round(1),hide_index=True,use_container_width=True)
        st.bar_chart(shown.set_index('group')[['percent']],horizontal=True)
        st.caption(t('On compare la proportion dans chaque groupe, pas son nombre total. Les groupes de moins de 30 réponses sont fragiles. Pour des catégories comme le paysage, ces proportions sont plus lisibles qu’un nombre arbitraire attribué à chaque catégorie.','Compare the share within each group, not its total size. Groups with fewer than 30 answers are fragile. For categories such as landscape, shares are clearer than assigning arbitrary numbers to categories.'))
    st.markdown('**'+t('2. Quels profils sont les plus concernés ?','2. Which profiles report it most often?')+'**')
    dims=st.multiselect(t('Combiner les caractéristiques','Combine characteristics'),['sexe','paysage','age','richesse'],default=['sexe','paysage'],max_selections=3,format_func=lambda v:names[v],key='lp_dimensions')
    if dims:
        pr,used,small=profiles(cat,y,base,dims)
        st.caption(t(f'Classement par proportion, parmi {used} réponses avec un profil complet. {small} petits profils exclus (moins de 30 réponses). Seuil pratique, pas garantie de précision.',f'Ranked by share among {used} answers with complete profiles. {small} small profiles excluded (fewer than 30 answers). This practical threshold does not guarantee precision.'))
        if pr.empty:st.info(t('Pas assez de réponses : retirez une caractéristique.','Too few answers: remove one characteristic.'))
        else:
            pr=pr.copy();pr['group']=pr.group.map(lambda x:' · '.join(tr(L.modalite(v)) for v in x.split(' · ')))
            st.dataframe(pr.rename(columns={'group':t('Profil','Profile'),'n':t('Réponses valides','Valid answers'),'yes':t('Réponse étudiée','Selected answer'),'percent':t('Part (%)','Share (%)')}).round(1),hide_index=True,use_container_width=True)
            top=pr.iloc[0];st.write(t(f'Parmi les profils affichés, « {top.group} » a la proportion observée la plus élevée : {top.percent:.1f} % ({int(top.yes)}/{int(top.n)}).',f'Among displayed profiles, “{top.group}” has the highest observed share: {top.percent:.1f}% ({int(top.yes)}/{int(top.n)}).'))
    st.markdown('**'+t('3. Quelles autres réponses sont les plus liées ?','3. Which other answers are most closely related?')+'**')
    if st.button(t('Rechercher les liens avec cette réponse','Find links with this answer'),key='lp_find'):
        links=focused_links(cat,qid,y,base)
        if not links:st.info(t('Pas assez de réponses communes pour établir un classement.','Too few shared answers for a ranking.'))
        else:
            display=[]
            for r in links[:15]:
                question=names.get(r['question'],tr(L.question(r['question'])))
                display.append({t('Autre réponse ou variable','Other answer or variable'):question+' — '+tr(L.modalite(r['label'])),t('Lien φ','Link φ'):round(r['phi'],3),t('Avec cette réponse (%)','With this answer (%)'):round(r['with_pct'],1),t('Autres réponses (%)','Other answers (%)'):round(r['without_pct'],1),t('Effectif avec','Count with'):r['with_n'],t('Effectif autres','Count others'):r['without_n'],t('Réponses communes','Shared answers'):r['n']})
            st.dataframe(pd.DataFrame(display),hide_index=True,use_container_width=True)
            st.caption(t(f'Les 15 premiers liens sur {len(links)} paires admissibles. « Avec » et « autres » donnent la fréquence de votre réponse étudiée dans les deux groupes. φ positif : plus fréquente avec l’autre réponse ; négatif : moins fréquente. Classement par |φ|, pas par certitude.',f'Top 15 of {len(links)} eligible pairs. “With” and “other” show how common your selected answer is in each group. Positive phi: more common with the other answer; negative: less common. Ranked by absolute phi, not certainty.'))
    with st.expander(t('À savoir pour bien lire les résultats','How to read these results')):
        st.write(t('Ces résultats décrivent les répondants de l’enquête, sans pondération ni preuve de cause. Un profil peut être premier par hasard. Les profils sont des groupes croisés, pas un modèle qui isole chaque effet. Les réponses manquantes ne comptent jamais comme « non ». À choix multiples, une réponse non sélectionnée est comparée aux autres réponses valides ; cela ne prouve pas l’absence réelle du phénomène.', 'These results describe surveyed respondents without weighting or proof of causes. A profile may rank first by chance. Profiles are crossed groups, not a model isolating effects. Missing answers never count as no. For multiple-choice questions, an unselected response is compared with other valid answers; this does not prove the phenomenon is absent.'))
        st.write(t('Les liens portent uniquement sur la réponse choisie. Il faut au moins 30 observations de chaque réponse et de son complément dans la base commune. La même question et les réponses parfaitement identiques ou inverses sont exclues. D’autres liens peuvent venir de questions presque identiques. Les effectifs changent selon les réponses disponibles. Chercher beaucoup de liens favorise les coïncidences ; ni test de significativité, ni classement des causes n’est présenté.', 'Links concern only the selected answer. Each response and its complement must have at least 30 observations in the shared sample. Same-question and exactly identical or inverse responses are excluded. Similar questions can still create mechanical links. Sample sizes vary with available answers. Searching many links favours coincidences; no significance test or ranking of causes is presented.'))
