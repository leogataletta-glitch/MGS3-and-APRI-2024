"""Survey-wide question-answer/profile associations, with one global Holm family."""
import hashlib
import gzip
import json
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import correlations_simples as C
import liens_profils as LP
import liens_inference as I
import themes_enquete as T
import i18n
import libelles_enquete as L
from traductions import text as tr


def scan(cat, progress=None):
    items=list(C.profile_candidates(cat));rows=[];questions=cat['questions'];outcomes=0
    for j,q in enumerate(questions):
        masks,base=LP.answers(cat,q);labels=list(masks)
        # A binary question and its complement carry the same association.
        if len(labels)==2 and not (masks[labels[0]] & masks[labels[1]]).any():
            labels=['Oui'] if 'Oui' in labels else labels[:1]
        for label in labels:
            y=masks[label]
            if min(int(y.sum()),int((base & ~y).sum()))<30:continue
            outcomes+=1
            family=C.rank_family(cat,y,base,items)
            for r in family:r.update(qid=q['i'],question=q['question'],answer=label,theme=T.theme_de(q.get('category')))
            rows.extend(family)
        if progress:progress((j+1)/len(questions))
    # Replace per-outcome adjustments: every eligible pair belongs to this family.
    for r,p in zip(rows,I.holm([r['p'] for r in rows])):r['p_holm']=p
    return rows,outcomes


def fingerprint(cat):
    h=hashlib.sha256(b'global-associations-v1')
    h.update(json.dumps(cat['questions'],sort_keys=True,ensure_ascii=False,default=str).encode())
    h.update(np.ascontiguousarray(cat['bits']).tobytes())
    for key,value in sorted(cat['groupes'].items()):
        h.update(key.encode());h.update(np.ascontiguousarray(value).tobytes())
    for module in (C,LP,I,T):h.update(Path(module.__file__).read_bytes().replace(b'\r\n',b'\n'))
    h.update(Path(__file__).read_bytes().replace(b'\r\n',b'\n'))
    return h.hexdigest()


def snapshot(cat):
    path=Path(__file__).with_name('correlations_generales_cache.json.gz')
    try:
        with gzip.open(path,'rt',encoding='utf-8') as f:data=json.load(f)
        if data['fingerprint']!=fingerprint(cat):return None
        for r in data['rows']:
            for key in ('p','p_holm'):
                if r[key] is None:r[key]=np.nan
        return data['rows'],data['outcomes']
    except (OSError,ValueError,KeyError,TypeError):return None


@st.cache_data(show_spinner=False,max_entries=2)
def cached_scan(cat):
    existing=snapshot(cat)
    if existing is not None:return existing
    bar=st.progress(0,text='Calcul / Computing…')
    try:return scan(cat,lambda value:bar.progress(value,text=f'Calcul / Computing… {value:.0%}'))
    finally:bar.empty()


def filter_rows(rows,theme,dims,combined=False):
    selected=set(dims)
    return [r for r in rows if (theme=='__all__' or r['theme']==theme) and (set(r['dims'])==selected if combined else set(r['dims']).issubset(selected))]


def ordered(rows,criterion):
    if criterion=='strength':return sorted(rows,key=lambda r:-abs(r['phi']))
    field='p_holm' if criterion.startswith('adjusted') else 'p'
    sign=-1 if criterion.endswith('high') else 1
    return sorted([r for r in rows if np.isfinite(r[field])],key=lambda r:(sign*r[field],-abs(r['phi'])))


def render(cat,t):
    st.caption(t('Recherche générale : chaque réponse exploitable de l’enquête est comparée aux profils de sexe, paysage, âge et niveau économique, seuls et combinés.','Overall search: every usable survey answer is compared with profiles of sex, landscape, age and economic level, alone and combined.'))
    st.caption(t('Il s’agit de liens entre réponses et profils, pas entre deux indicateurs. Les cumuls personnalisés de questions restent dans « Choisir un cas précis ».','These are answer–profile associations, not links between two indicators. Custom combinations of questions remain in “Choose a specific outcome”.'))
    names={'sexe':t('Sexe','Sex'),'paysage':t('Paysage','Landscape'),'age':t('Âge','Age'),'richesse':t('Niveau économique','Economic level')}
    cols=st.columns([1,2,1])
    present={T.theme_de(q.get('category')) for q in cat['questions']}
    codes=[c for c in [c for c,_,_ in T.THEMES]+[T.CALCULE,T.AUTRES] if c in present]
    with cols[0]:theme=st.selectbox(t('Thème des questions','Question theme'),['__all__']+codes,format_func=lambda v:t('Tous les thèmes','All themes') if v=='__all__' else tr(i18n.T(T.libelle(v))),key='global_theme')
    with cols[1]:dims=st.multiselect(t('Variables de profil','Profile variables'),list(names),default=list(names),format_func=lambda v:names[v],key='global_dims')
    with cols[2]:combination=st.selectbox(t('Combiner','Combine'),['mixed','combined'],format_func=lambda v:t('Seules et combinées','Individual and combined') if v=='mixed' else t('Toutes ensemble uniquement','All together only'),key='global_combination')
    criterion=st.selectbox(t('Classer les associations par','Rank associations by'),['strength','raw_low','raw_high','adjusted_low','adjusted_high'],format_func=lambda v:{'strength':t('|φ| le plus élevé — lien le plus fort','Highest |phi| — strongest association'),'raw_low':t('p brute la plus faible','Lowest raw p'),'raw_high':t('p brute la plus élevée — pas un lien plus solide','Highest raw p — not stronger evidence'),'adjusted_low':t('p corrigée (Holm) la plus faible','Lowest adjusted p (Holm)'),'adjusted_high':t('p corrigée (Holm) la plus élevée','Highest adjusted p (Holm)')}[v],key='global_order')
    if not dims:st.info(t('Choisissez au moins une variable de profil.','Choose at least one profile variable.'));return
    if st.button(t('Explorer toute l’enquête','Explore the whole survey'),key='global_compute'):
        with st.spinner(t('Calcul général, puis classement… Le premier calcul peut prendre plusieurs minutes.','Computing the overall search, then ranking… The first run may take several minutes.')):
            st.session_state.global_associations=cached_scan(cat)
    result=st.session_state.get('global_associations')
    if result is None:return
    rows,outcomes=result;filtered=filter_rows(rows,theme,dims,combination=='combined');ranking=ordered(filtered,criterion)
    st.markdown('**'+t('Les 10 premières associations selon votre classement','Top 10 associations for your ranking')+'**')
    st.caption(t(f'{outcomes} réponses étudiées ; {len(rows)} associations admissibles dans toute l’enquête. {len(filtered)} correspondent à vos filtres ; {len(ranking)} peuvent être classées avec ce critère.',f'{outcomes} answers examined; {len(rows)} eligible associations across the survey. {len(filtered)} match your filters; {len(ranking)} can be ranked with this criterion.'))
    data=[]
    for j,r in enumerate(ranking[:10],1):
        frequency=t('Plus fréquent','More common') if r['phi']>0 else t('Moins fréquent','Less common') if r['phi']<0 else t('Même fréquence','Same frequency')
        data.append({t('Rang','Rank'):j,t('Question','Question'):tr(L.question(r['question'])),t('Réponse','Answer'):tr(L.modalite(r['answer'])),t('Profil','Profile'):' · '.join(tr(L.modalite(v)) for v in r['labels']),'φ':round(r['phi'],3),t('p brute','Raw p'):r['p'],t('p corrigée (Holm)','Adjusted p (Holm)'):r['p_holm'],t('Interprétation de φ','Interpretation of phi'):t(f"{frequency} : {r['with_pct']:.1f}% ({r['yes']}/{r['with_n']}), contre {r['without_pct']:.1f}% chez les autres.",f"{frequency}: {r['with_pct']:.1f}% ({r['yes']}/{r['with_n']}), versus {r['without_pct']:.1f}% among others."),t('Interprétation de p corrigée','Adjusted p interpretation'):LP.decision(r,t)})
    if data:st.dataframe(pd.DataFrame(data).round(4),hide_index=True,use_container_width=True)
    else:st.info(t('Aucune association calculable avec ces filtres et ce tri.','No calculable association for these filters and ranking.'))
    st.markdown(t('**|φ| élevé = lien observé fort. p faible = davantage d’éléments contre l’absence de lien, sous les hypothèses du test. p élevée ≠ meilleur lien.** La décision à 0,05 utilise p corrigée, même lorsque vous triez par p brute. Une association ne prouve pas une cause.', '**High |phi| = strong observed association. Low p = more evidence against no association under the test assumptions. High p ≠ a better association.** The 0.05 decision uses adjusted p even when sorting by raw p. Association does not prove causation.'))
    with st.expander(t('Méthode du classement général','Overall ranking methodology')):
        st.write(t('Holm porte sur toutes les associations admissibles de toute l’enquête avant les filtres et le top 10. Changer le thème, les variables ou le tri ne réduit pas la correction. Les p non calculables comptent comme 1 pour la correction mais restent indisponibles et sont exclues des tris par p. À égalité de p, on trie par |φ| décroissant ; une égalité ne crée pas une différence statistique.', 'Holm covers all eligible associations across the whole survey before filters and the top ten. Changing themes, variables or ranking does not reduce adjustment. Uncomputable p-values enter adjustment as 1 but remain unavailable and are excluded from p rankings. Tied p-values are ordered by decreasing |phi|; a tie does not create a statistical difference.'))
        st.write(t('Chaque réponse est étudiée séparément, contre les autres réponses valides. Pour une question binaire, une seule réponse représente les deux réponses complémentaires. Les combinaisons de réponses ou de questions personnalisées ne sont pas énumérées automatiquement. Minimum 30 observations à chaque niveau du cas et du profil ; doublons de profils et liens identiques ou inverses du cas exclus. Les valeurs manquantes sont exclues ; les cultures sont limitées aux agriculteurs déclarés.', 'Each answer is examined separately against other valid responses. For binary questions, one answer represents both complementary answers. Custom answer or question combinations are not automatically enumerated. At least 30 observations at each level of outcome and profile; duplicate profiles and outcomes identical or inverse to the target excluded. Missing values are excluded; crops are restricted to self-reported farmers.'))
        st.write(t('φ décrit un lien binaire, pas un effet causal. p vient d’un wild cluster bootstrap-t par section ; dix sections restent peu et leur indépendance est une hypothèse. Tests approximatifs et exploratoires, sans pondération de population ni ajustement mutuel des facteurs. Le nombre de comparaisons peut conduire à des p corrigées toutes élevées. Les profils se chevauchent et des questions proches peuvent produire des résultats semblables.', 'Phi describes a binary association, not a causal effect. p comes from a section-level wild cluster bootstrap-t; ten sections remain few and independence is an assumption. Tests are approximate and exploratory, without population weighting or mutual adjustment of factors. Many comparisons may produce uniformly high adjusted p-values. Profiles overlap and related questions can produce similar results.'))
        st.markdown('[Wild cluster bootstrap — Stata](https://www.stata.com/manuals/rwildbootstrap.pdf)')
