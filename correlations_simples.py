"""A single indicator and two transparent section-level Spearman rankings."""
import itertools
import json
import numpy as np
import pandas as pd
import streamlit as st
import croisement_moteur as M
import i18n
from traductions import text as tr


def rho(x,y):
    a=pd.Series(x).rank().to_numpy(float);b=pd.Series(y).rank().to_numpy(float)
    a-=a.mean();b-=b.mean();d=np.linalg.norm(a)*np.linalg.norm(b)
    return float(np.clip(a@b/d,-1,1)) if d else np.nan


def compare(x,y):
    valid=np.isfinite(x)&np.isfinite(y);a=x[valid];b=y[valid]
    if len(a)<8:return None
    r=rho(a,b)
    if not np.isfinite(r):return None
    loo=[rho(np.delete(a,j),np.delete(b,j)) for j in range(len(a))]
    finite=[v for v in loo if np.isfinite(v)]
    return dict(rho=r,n=len(a),low=min(finite) if finite else np.nan,high=max(finite) if finite else np.nan,stable=len(finite)==len(a) and all(np.sign(v)==np.sign(r) for v in finite))


def load():
    path=M._trouver('resultats.json')
    if not path:return []
    with open(path,encoding='utf-8') as f:data=json.load(f)
    if isinstance(data,dict):data=data['indicateurs']
    rows=[]
    for r in data:
        v=pd.to_numeric(pd.Series([(r.get('valeurs') or {}).get(s) for s in M.SECTIONS]),errors='coerce').to_numpy(float)
        if np.isfinite(v).sum()>=8 and len(np.unique(v[np.isfinite(v)]))>=2:rows.append(dict(record=r,values=v))
    return rows


def profile_vectors(cat):
    from liens_profils import registry
    dimensions=['sexe','paysage','age','richesse'];regs={k:registry(cat,k) for k in dimensions}
    result=[];seen=set()
    for size in (1,2,3):
        for dims in itertools.combinations(dimensions,size):
            base=np.ones(cat['n'],bool)
            for d in dims:base &= regs[d][1]
            for labels in itertools.product(*[list(regs[d][0]) for d in dims]):
                mask=base.copy()
                for d,l in zip(dims,labels):mask &= regs[d][0][l]
                if min(int(mask.sum()),int((base & ~mask).sum()))<30:continue
                signature=mask.tobytes()+base.tobytes();inverse=(base & ~mask).tobytes()+base.tobytes()
                if signature in seen or inverse in seen:continue
                seen.add(signature)
                values=[];counts=[]
                for section in M.SECTIONS:
                    eligible=base & cat['groupes'].get(section,np.zeros(cat['n'],bool));n=int(eligible.sum());k=int((eligible & mask).sum())
                    values.append(100*k/n if n>=30 else np.nan);counts.append((k,n))
                result.append(dict(labels=labels,dims=dims,values=np.array(values),counts=counts,total=int(mask.sum())))
    return result


def rankings(selected,indicators,cat):
    target=selected['record'];x=selected['values'];other=[];profiles=[]
    for entry in indicators:
        r=entry['record']
        if r['ligne']==target['ligne']:continue
        if target.get('question') and M._norm(target['question'])==M._norm(r.get('question') or ''):continue
        stat=compare(x,entry['values'])
        if stat:other.append(dict(**stat,label=r['indicateur'],values=entry['values'],record=r))
    for profile in profile_vectors(cat):
        stat=compare(x,profile['values'])
        if stat:profiles.append(dict(**stat,**profile))
    for rows in (other,profiles):rows.sort(key=lambda r:-abs(r['rho']))
    return other,profiles


def render(cat):
    fr=i18n.get_lang()=='fr'
    def t(a,b):return tr(a if fr else b)
    entries=load()
    if not entries or not cat:st.info(t('Données insuffisantes.','Insufficient data.'));return
    byid={e['record']['ligne']:e for e in entries}
    st.caption(t('Choisissez un indicateur : deux listes de 10 corrélations, calculées entre les sections communales.','Choose an indicator: two top-10 correlation lists, calculated across communal sections.'))
    selected=st.selectbox(t('Indicateur à explorer','Indicator to explore'),list(byid),index=None,format_func=lambda k:tr(byid[k]['record']['indicateur']),placeholder=t('Rechercher un indicateur…','Search for an indicator…'),key='simple_correlation_indicator')
    if selected is None:return
    entry=byid[selected]
    st.caption(t('Valeurs brutes des indicateurs, pas scores sur 10. + : les deux mesures augmentent ensemble ; − : elles évoluent en sens inverse. Plus |ρ| est proche de 1, plus le lien de rang est fort.','Raw indicator values, not 0–10 scores. +: both measures rise together; −: opposite directions. The closer |rho| is to 1, the stronger the rank relationship.'))
    with st.spinner(t('Calcul des deux listes…','Calculating both lists…')):indicators,profiles=rankings(entry,entries,cat)
    def profile_name(r):return ' · '.join(tr({'Homme':t('Homme','Man'),'Femme':t('Femme','Woman'),'Montagne':t('Montagne','Mountain'),'Littoral':t('Littoral','Coastal')}.get(v,v)) for v in r['labels'])
    def table(rows,profile=False):
        records=[]
        for j,r in enumerate(rows[:10],1):
            records.append({t('Rang','Rank'):j,t('Profil' if profile else 'Indicateur','Profile' if profile else 'Indicator'):profile_name(r) if profile else tr(r['label']),t('Corrélation ρ','Correlation ρ'):round(r['rho'],2),t('Sens du lien','Direction'):t('Même sens','Same direction') if r['rho']>0 else t('Sens inverse','Opposite direction') if r['rho']<0 else t('Pas de lien de rang','No rank relationship'),t('Sections','Sections'):r['n'],t('Au retrait d’une section','Omitting one section'):t('Sens conservé','Direction retained') if r['stable'] else t('Sens fragile','Fragile direction')})
        if records:st.dataframe(pd.DataFrame(records),hide_index=True,use_container_width=True)
        else:st.info(t('Pas assez de données comparables pour cette liste.','Not enough comparable data for this list.'))
    st.markdown('**'+t('Les 10 indicateurs les plus corrélés','The 10 most correlated indicators')+'**');table(indicators)
    st.markdown('**'+t('Les 10 profils ou combinaisons les plus corrélés','The 10 most correlated profiles or combinations')+'**')
    st.caption(t('Sexe, paysage, âge, catégorie économique — seuls ou combinés jusqu’à trois caractéristiques. On corrèle l’indicateur avec la part de ce profil dans chaque section. Ce n’est pas le taux du phénomène chez ce profil.','Sex, landscape, age and economic category — alone or combined up to three characteristics. The indicator is correlated with each profile’s share within each section. This is not the outcome rate within that profile.'))
    table(profiles,True)
    with st.expander(t('Lire un lien et voir les chiffres utilisés','Read a relationship and see the underlying values')):
        options=[('i',j) for j in range(min(10,len(indicators)))]+[('p',j) for j in range(min(10,len(profiles)))]
        if options:
            choice=st.selectbox(t('Lien à examiner','Relationship to inspect'),options,format_func=lambda k:tr(indicators[k[1]]['label']) if k[0]=='i' else profile_name(profiles[k[1]]))
            r=(indicators if choice[0]=='i' else profiles)[choice[1]]
            label=tr(r['label']) if choice[0]=='i' else t('Part du profil (%)','Profile share (%)')
            frame=pd.DataFrame({t('Section','Section'):M.SECTIONS,t('Indicateur choisi — valeur brute','Selected indicator — raw value'):entry['values'],label:r['values']})
            if choice[0]=='p':frame[t('Répondants du profil / base valide','Profile respondents / valid base')]=[f'{k}/{n}' for k,n in r['counts']]
            st.dataframe(frame,hide_index=True,use_container_width=True)
            st.write(t(f"ρ = {r['rho']:+.2f} sur {r['n']} sections ; de {r['low']:+.2f} à {r['high']:+.2f} quand on retire une section. Cette plage mesure la sensibilité, pas un intervalle de confiance.",f"rho = {r['rho']:+.2f} across {r['n']} sections; {r['low']:+.2f} to {r['high']:+.2f} when omitting one section. This range measures sensitivity, not a confidence interval."))
            if choice[0]=='p':st.write(t('Lecture : dans les sections où ce profil est plus représenté dans l’enquête, la valeur de l’indicateur tend à être plus élevée (ρ positif) ou plus basse (ρ négatif). Cela ne dit pas que les personnes de ce profil sont les plus touchées.','Reading: sections where this profile is more represented in the survey tend to have higher (positive rho) or lower (negative rho) indicator values. This does not mean individuals in that profile are most affected.'))
    with st.expander(t('Méthode et limites','Method and limitations')):
        st.write(t(f'{len(indicators)} autres indicateurs et {len(profiles)} profils comparables examinés. Les listes retiennent les dix premiers par |ρ de Spearman|, avec au moins huit sections communes. Les égalités sont traitées par rang moyen. S’il reste moins de dix liens calculables, la liste est plus courte.',f'{len(indicators)} other indicators and {len(profiles)} comparable profiles examined. Lists show the top ten by absolute Spearman rho, with at least eight shared sections. Ties use average ranks. Fewer than ten calculable links yield a shorter list.'))
        st.write(t('Chaque section compte une fois. Les indicateurs issus de la même question que l’indicateur choisi sont exclus. Les profils identiques ou strictement complémentaires sont dédoublonnés. Minimum 30 répondants dans le profil et hors profil, et 30 réponses valides par section pour sa proportion. Les profils constants entre sections ne sont pas corrélables. Les proportions décrivent l’échantillon, pas nécessairement la population : le plan de sondage peut limiter leur variation.', 'Each section counts once. Indicators sharing the selected indicator’s source question are excluded. Identical or exactly complementary profiles are deduplicated. At least 30 respondents in and outside a profile, and 30 valid answers per section for its share. Profiles constant across sections cannot be correlated. Shares describe the sample, not necessarily the population; sampling design can constrain variation.'))
        st.write(t('Ici ρ de Spearman remplace φ, réservé aux deux réponses binaires de l’ancien écran. Holm était une correction de p-value, pas un coefficient de corrélation. Ces nouveaux classements territoriaux restent exploratoires : dix sections, recherche de nombreux liens et proximité géographique ne permettent pas de présenter ces listes comme des découvertes confirmées. Aucune p-value de l’ancien test ménage n’est réutilisée. Une corrélation parfaite peut venir de définitions proches ; corrélation ne signifie pas cause.', 'Here Spearman rho replaces phi, which described two binary answers in the old screen. Holm corrected p-values; it was not a correlation coefficient. These territorial rankings remain exploratory: ten sections, many searched relationships and geographic proximity prevent treating them as confirmed discoveries. No p-value from the old household test is reused. Perfect correlations can result from related definitions; correlation does not imply causation.'))
        st.write(tr(entry['record'].get('metrique') or ''))
        if entry['record'].get('note'):st.caption(tr(entry['record']['note']))
