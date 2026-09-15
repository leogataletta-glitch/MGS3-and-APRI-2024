"""One outcome, descriptive group comparisons, crossed profiles and focused links."""
import itertools
import numpy as np
import pandas as pd
import streamlit as st
import i18n
import croisement_moteur as M
import libelles_enquete as L
from traductions import text as tr
import liens_inference as I


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


def profiles(cat,y,base,dimensions,minimum=30,inference=False):
    registries=[registry(cat,d) for d in dimensions]
    valid=base.copy()
    for _,b in registries:valid &= b
    masks={}
    for combo in itertools.product(*[list(m) for m,_ in registries]):
        mask=valid.copy()
        for name,(m,_) in zip(combo,registries):mask &= m[name]
        masks[' · '.join(combo)]=mask
    rows=proportions(y,valid,masks)
    if inference and not rows.empty:
        results=I.family(y,valid,[masks[k] for k in rows.group],I.section_ids(cat))
        rows=pd.concat([rows.reset_index(drop=True),pd.DataFrame(results)],axis=1)
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
    sections=I.section_ids(cat)
    for question,label,z,v,kind in candidates:
        common=base & v;n=int(common.sum());a=int((common & y).sum());b=int((common & z).sum());both=int((common & y & z).sum())
        if min(a,n-a,b,n-b)<30:continue
        phi=(n*both-a*b)/np.sqrt(float(a*(n-a)*b*(n-b)))
        if abs(phi)>=1-1e-12:continue
        stat=I.test(y[common],z[common],sections[common])
        rows.append(dict(question=question,label=label,kind=kind,phi=phi,n=n,with_pct=100*both/b,without_pct=100*(a-both)/(n-b),with_n=b,without_n=n-b,p=stat['p'],sections=stat['sections'],reason=stat['reason']))
    for row,adjusted in zip(rows,I.holm([r['p'] for r in rows])):row['p_holm']=adjusted
    rows.sort(key=lambda r:abs(r['phi']),reverse=True)
    return rows


def render(cat):
    fr=i18n.get_lang()=='fr'
    def t(a,b):return tr(a if fr else b)
    def stat_columns(frame):
        frame=frame.copy()
        frame['decision']=frame.apply(lambda r: decision(r,t),axis=1)
        return frame.drop(columns=['reason','draws'],errors='ignore').rename(columns={'phi':t('Lien φ','Link φ'),'p':t('p (sections)','p (sections)'),'p_holm':t('p corrigée (Holm)','Adjusted p (Holm)'),'sections':t('Sections','Sections'),'decision':t('Lecture à α = 0,05','Reading at α = 0.05')})
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
    st.caption(t('φ = force et sens du lien. p corrigée ≤ 0,05 = seuil franchi sous les hypothèses du test ; au-delà, preuves insuffisantes, pas preuve d’absence. Les explications et exemples sont dans « Comprendre φ, p et α » en bas.', 'Phi = strength and direction. Adjusted p ≤ 0.05 = threshold met under the test assumptions; otherwise, insufficient evidence, not evidence of absence. See “Understand phi, p and alpha” below for examples and theory.'))
    st.markdown('**'+t('1. Comparer avec une variable','1. Compare with a variable')+'**')
    dim=st.selectbox(t('Comparer selon','Compare by'),list(names),format_func=lambda v:names[v],key='lp_compare')
    gm,gb=registry(cat,dim);rows=proportions(y,base & gb,gm)
    if not rows.empty:
        stats=I.family(y,base & gb,list(gm.values()),I.section_ids(cat))
        bygroup=dict(zip(gm,stats))
        rows=pd.concat([rows.reset_index(drop=True),pd.DataFrame([bygroup[k] for k in rows.group])],axis=1)
        shown=rows.copy();shown['group']=shown.group.map(lambda x:tr(L.modalite(x)))
        st.dataframe(stat_columns(shown).rename(columns={'group':t('Groupe','Group'),'n':t('Réponses valides','Valid answers'),'yes':t('Réponse étudiée','Selected answer'),'percent':t('Part (%)','Share (%)')}).round(4),hide_index=True,use_container_width=True)
        st.bar_chart(shown.set_index('group')[['percent']],horizontal=True)
        st.caption(t('On compare la proportion dans chaque groupe, pas son nombre total. Les groupes de moins de 30 réponses sont fragiles. Pour des catégories comme le paysage, ces proportions sont plus lisibles qu’un nombre arbitraire attribué à chaque catégorie.','Compare the share within each group, not its total size. Groups with fewer than 30 answers are fragile. For categories such as landscape, shares are clearer than assigning arbitrary numbers to categories.'))
    st.caption(t('Chaque test compare un groupe à tous les autres réunis. Holm corrige sur tous les groupes de cette variable. Une comparaison par section ne peut pas être testée avec une seule section par groupe.', 'Each test compares one group with all other groups pooled. Holm covers every group of this variable. Comparing individual sections cannot be tested with only one section per group.'))
    st.markdown('**'+t('2. Quels profils sont les plus concernés ?','2. Which profiles report it most often?')+'**')
    dims=st.multiselect(t('Combiner les caractéristiques','Combine characteristics'),['sexe','paysage','age','richesse'],default=['sexe','paysage'],max_selections=3,format_func=lambda v:names[v],key='lp_dimensions')
    if dims:
        pr,used,small=profiles(cat,y,base,dims,inference=True)
        st.caption(t(f'Classement par proportion, parmi {used} réponses avec un profil complet. {small} petits profils exclus (moins de 30 réponses). Seuil pratique, pas garantie de précision.',f'Ranked by share among {used} answers with complete profiles. {small} small profiles excluded (fewer than 30 answers). This practical threshold does not guarantee precision.'))
        if pr.empty:st.info(t('Pas assez de réponses : retirez une caractéristique.','Too few answers: remove one characteristic.'))
        else:
            pr=pr.copy();pr['group']=pr.group.map(lambda x:' · '.join(tr(L.modalite(v)) for v in x.split(' · ')))
            st.dataframe(stat_columns(pr).rename(columns={'group':t('Profil','Profile'),'n':t('Réponses valides','Valid answers'),'yes':t('Réponse étudiée','Selected answer'),'percent':t('Part (%)','Share (%)')}).round(4),hide_index=True,use_container_width=True)
            top=pr.iloc[0];st.write(t(f'Parmi les profils affichés, « {top.group} » a la proportion observée la plus élevée : {top.percent:.1f} % ({int(top.yes)}/{int(top.n)}).',f'Among displayed profiles, “{top.group}” has the highest observed share: {top.percent:.1f}% ({int(top.yes)}/{int(top.n)}).'))
    st.caption(t('Pour chaque profil : comparaison à tous les autres profils réunis, sur les réponses avec profil complet. Holm inclut tous les profils non vides, même ceux masqués pour petit effectif. Le profil classé premier n’est pas nécessairement différent des autres au seuil retenu.', 'Each profile is compared with all other profiles pooled, using complete profiles. Holm includes all nonempty profiles, even those hidden for small counts. The top-ranked profile is not necessarily different at the selected threshold.'))
    st.markdown('**'+t('3. Quelles autres réponses sont les plus liées ?','3. Which other answers are most closely related?')+'**')
    if st.button(t('Rechercher les liens avec cette réponse','Find links with this answer'),key='lp_find'):
        with st.spinner(t('Calcul des liens et des tests par section…','Computing links and section-based tests…')):
            links=focused_links(cat,qid,y,base)
        if not links:st.info(t('Pas assez de réponses communes pour établir un classement.','Too few shared answers for a ranking.'))
        else:
            display=[]
            for r in links[:15]:
                question=names.get(r['question'],tr(L.question(r['question'])))
                display.append({t('Autre réponse ou variable','Other answer or variable'):question+' — '+tr(L.modalite(r['label'])),t('Lien φ','Link φ'):round(r['phi'],3),t('p (sections)','p (sections)'):r['p'],t('p corrigée (Holm)','Adjusted p (Holm)'):r['p_holm'],t('Lecture à α = 0,05','Reading at α = 0.05'):decision(r,t),t('Sections','Sections'):r['sections'],t('Avec cette réponse (%)','With this answer (%)'):round(r['with_pct'],1),t('Autres réponses (%)','Other answers (%)'):round(r['without_pct'],1),t('Effectif avec','Count with'):r['with_n'],t('Effectif autres','Count others'):r['without_n'],t('Réponses communes','Shared answers'):r['n']})
            st.dataframe(pd.DataFrame(display).round(4),hide_index=True,use_container_width=True)
            st.caption(t(f'Correction de Holm sur les {len(links)} paires admissibles, avant de retenir les 15 premières. {sum(np.isfinite(r["p"]) for r in links)} tests calculables. Seuil α fixé à 0,05.',f'Holm correction across all {len(links)} eligible pairs, before selecting the top 15. {sum(np.isfinite(r["p"]) for r in links)} computable tests. Alpha fixed at 0.05.'))
            st.caption(t(f'Les 15 premiers liens sur {len(links)} paires admissibles. « Avec » et « autres » donnent la fréquence de votre réponse étudiée dans les deux groupes. φ positif : plus fréquente avec l’autre réponse ; négatif : moins fréquente. Classement par |φ|, pas par certitude.',f'Top 15 of {len(links)} eligible pairs. “With” and “other” show how common your selected answer is in each group. Positive phi: more common with the other answer; negative: less common. Ranked by absolute phi, not certainty.'))
    explain_inference(t)
    with st.expander(t('À savoir pour bien lire les résultats','How to read these results')):
        st.write(t('Ces résultats décrivent les répondants de l’enquête, sans pondération ni preuve de cause. Un profil peut être premier par hasard. Les profils sont des groupes croisés, pas un modèle qui isole chaque effet. Les réponses manquantes ne comptent jamais comme « non ». À choix multiples, une réponse non sélectionnée est comparée aux autres réponses valides ; cela ne prouve pas l’absence réelle du phénomène.', 'These results describe surveyed respondents without weighting or proof of causes. A profile may rank first by chance. Profiles are crossed groups, not a model isolating effects. Missing answers never count as no. For multiple-choice questions, an unselected response is compared with other valid answers; this does not prove the phenomenon is absent.'))
        st.write(t('Les liens portent uniquement sur la réponse choisie. Il faut au moins 30 observations de chaque réponse et de son complément dans la base commune. La même question et les réponses parfaitement identiques ou inverses sont exclues. D’autres liens peuvent venir de questions presque identiques. Les effectifs changent selon les réponses disponibles. La correction de Holm limite les faux positifs dans la famille affichée, sous les hypothèses du test. Elle ne couvre pas vos recherches successives sur différentes réponses ; aucun classement des causes n’est présenté.', 'Links concern only the selected answer. Each response and its complement must have at least 30 observations in the shared sample. Same-question and exactly identical or inverse responses are excluded. Similar questions can still create mechanical links. Sample sizes vary with available answers. Holm correction limits false positives within the displayed family under the test assumptions. It does not cover repeated searches across different outcomes; no ranking of causes is presented.'))


def decision(r,t):
    if not np.isfinite(r['p']):
        reasons={'sample':t('effectif insuffisant','insufficient sample'),'sections':t('moins de 8 sections','fewer than 8 sections'),'missing_section':t('section manquante','missing section'),'support':t('réponses concentrées dans trop peu de sections','responses concentrated in too few sections'),'degenerate':t('test instable','unstable test')}
        return t('Non calculable : ','Not computable: ')+reasons.get(r['reason'],r['reason'])
    return t('Seuil franchi — sous hypothèses','Threshold met — under assumptions') if r['p_holm']<=.05 else t('Seuil non franchi','Threshold not met')


def explain_inference(t):
    with st.expander(t('Comprendre φ, p et α : exemples et théorie','Understand phi, p and alpha: examples and theory')):
        st.markdown(t("""
1. **φ (phi) décrit le lien observé**, de −1 à +1. Positif : votre réponse est plus fréquente avec l’autre réponse ; négatif : moins fréquente. Près de zéro : peu d’association binaire observée. **φ = 0,4 ne signifie ni 40 % d’effet ni 40 % de certitude.** Regardez aussi les proportions et les effectifs ; la fréquence des réponses limite les valeurs possibles de φ.
2. **p teste une hypothèse précise : aucun écart de proportion entre les deux groupes.** Sous cette hypothèse et celles du modèle, p mesure la fréquence d’un résultat au moins aussi extrême. **p = 0,03 ne signifie pas qu’il y a 3 % de risque que le lien soit faux.** La p-value ne mesure ni sa force ni sa cause.
3. **α = 0,05 est le seuil de décision fixé avant la lecture.** Il concerne le risque de faux positif à long terme sous les hypothèses du test. Nous le comparons à la p-value corrigée, pas à la p-value brute. Ce n’est pas « 95 % de certitude » pour une ligne.
4. **Pourquoi corriger ?** En cherchant beaucoup de liens, on peut en trouver par hasard. Holm tient compte de toute la famille examinée, y compris les lignes hors du top 15. Cette correction est prudente et ne suppose pas que les tests soient indépendants. Elle ne répare pas un test mal adapté.
5. **Exemple inventé :** φ = 0,40, p = 0,02, p corrigée = 0,20. Un lien est observé, mais il ne franchit pas le seuil après correction. Si la p corrigée était 0,03, le seuil serait franchi sous les hypothèses du test, sans prouver une causalité. **Un seuil non franchi ne prouve pas l’absence de lien.**
""", """
1. **Phi describes the observed association**, from −1 to +1. Positive: your answer is more common with the other answer; negative: less common. Near zero: little observed binary association. **Phi = 0.4 means neither a 40% effect nor 40% certainty.** Also inspect proportions and counts; response prevalence constrains attainable phi values.
2. **p tests a specific hypothesis: no difference in proportions between the two groups.** Under that hypothesis and the model assumptions, p measures how often a result at least as extreme would occur. **p = 0.03 does not mean a 3% chance that the relationship is false.** It measures neither strength nor causation.
3. **Alpha = 0.05 is the decision threshold set before reading results.** It concerns long-run false positives under the test assumptions. We compare it with adjusted p, not raw p. It does not mean “95% certainty” for an individual row.
4. **Why adjust?** Searching many links can find chance results. Holm covers the whole family examined, including rows outside the top 15. It is conservative and does not require independent tests. It cannot repair an unsuitable test.
5. **Made-up example:** phi = 0.40, p = 0.02, adjusted p = 0.20. An association is observed, but it does not meet the corrected threshold. If adjusted p were 0.03, it would meet the threshold under the test assumptions, without proving causation. **Not meeting the threshold does not prove there is no relationship.**
"""))
        st.write(t('Méthode : modèle linéaire non pondéré réponse = constante + autre réponse binaire. Le coefficient est l’écart de proportions ; tester zéro revient ici à tester φ = 0. Wild cluster bootstrap-t sous l’hypothèse nulle, résidus à moyenne constante, poids ±1 communs à toute une section (Rademacher), statistique studentisée avec variance CR1 par section. Toutes les 2^G combinaisons sont parcourues (1 024 pour dix sections), test bilatéral. Cette énumération rend le calcul reproductible, pas le test exact en petit échantillon.',
                   'Method: unweighted linear model, answer = intercept + other binary answer. The coefficient is the proportion difference; testing zero here is equivalent to testing phi = 0. Null-imposed wild cluster bootstrap-t, constant-mean restricted residuals, section-wide ±1 Rademacher weights and CR1 cluster-studentized statistic. All 2^G combinations are enumerated (1,024 for ten sections), two-sided test. Enumeration makes computation reproducible, not exact in small samples.'))
        st.write(t('Conditions : au moins 30 observations pour chaque réponse et son complément, au moins huit sections connues ; chaque réponse et complément doivent apparaître dans au moins quatre sections, sans qu’une section en concentre plus de la moitié. Sinon, le résultat reste descriptif et la p-value est non calculable. Les tests impossibles comptent comme p = 1 dans la correction, mais restent affichés comme indisponibles.',
                   'Requirements: at least 30 observations for each response and its complement and eight known sections; each response and complement must occur in four sections, with no section containing more than half. Otherwise the result stays descriptive and p is unavailable. Untestable comparisons count as p = 1 in the correction but remain displayed as unavailable.'))
        st.warning(t('Dix sections restent peu. Les p-values sont approximatives et supposent des sections indépendantes ; une dépendance spatiale entre elles ou le plan réel de sondage peut invalider cette approximation. Ni pondération de population ni ajustement causal. Avec des centaines de tests et cette résolution limitée, toutes les p-values corrigées peuvent dépasser 0,05 : on ne réduit pas la correction pour obtenir des résultats significatifs.',
                     'Ten sections remain few. P-values are approximate and assume independent sections; spatial dependence or the actual sampling design may invalidate that approximation. No population weighting or causal adjustment. With hundreds of tests and limited resolution, all adjusted p-values may exceed 0.05; the correction is not relaxed to obtain significant findings.'))
        st.markdown('[Wild cluster bootstrap — Stata](https://www.stata.com/manuals/rwildbootstrap.pdf) · [Cluster inference — Cameron & Miller](https://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015.pdf) · [Holm — statsmodels](https://www.statsmodels.org/dev/generated/statsmodels.stats.multitest.multipletests.html)')
