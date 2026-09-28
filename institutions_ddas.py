"""Source-traceable institutional declarations, separate from household scores."""
import json
from pathlib import Path
import pandas as pd
import streamlit as st


def load_data():
    return json.loads(Path(__file__).with_name('ddas_institutions.json').read_text(encoding='utf-8'))


def render(controls):
    data = load_data()
    rows = data['observations']
    with controls[0]:
        sector = st.selectbox('Secteur', ['Tous les secteurs', 'Éducation', 'Santé', 'CASEC', 'Organisations'], key='inst_ddas_sector')
    matching = [r for r in rows if sector == 'Tous les secteurs' or r['secteur'] == sector]
    labels = list(dict.fromkeys(r['question'] for r in matching))
    options = ['Toutes les questions'] + labels
    if st.session_state.get('inst_ddas_question') not in options:
        st.session_state['inst_ddas_question'] = options[0]
    with controls[1]:
        question = st.selectbox('Question', options, key='inst_ddas_question')
    section = st.selectbox('Section communale', ['Quentin et Beaulieu', 'Quentin', 'Beaulieu'], key='inst_ddas_section')
    st.markdown('### Enquêtes institutionnelles — Quentin et Beaulieu')
    st.caption('9 questionnaires distincts : 2 CASEC, 2 éducation, 2 santé et 3 organisations. Réponses originales en français.')
    st.info('Localisation provisoire : les enquêtes CASEC, éducation et santé sont rattachées à la section nommée dans le fichier reçu, à confirmer par les partenaires. Les organisations indiquent explicitement leur section. Ces déclarations ne modifient pas les scores APRI ni les corrélations entre ménages.')
    selected = [r for r in matching if (section == 'Quentin et Beaulieu' or r['section'] == section) and (question == options[0] or r['question'] == question)]
    st.dataframe(pd.DataFrame([{'Section': r['section'], 'Secteur': r['secteur'], 'Question': r['question'], 'Réponse déclarée': str(r['valeur']), 'Questionnaire': r['questionnaire']} for r in selected]), hide_index=True, use_container_width=True)
    st.caption('Les réponses absentes ne sont pas affichées et ne sont jamais remplacées par zéro. Les nombres sont des déclarations institutionnelles, pas des taux de couverture de la population.')
    with st.expander('Sources et vérifications en cours'):
        st.markdown('''- Chaque questionnaire est compté une seule fois grâce à son identifiant Kobo, même lorsqu’il figure dans plusieurs exports.
- Les deux fichiers santé DDAS reçus contiennent les mêmes valeurs : ils ne constituent pas deux collectes.
- Le rattachement territorial des six questionnaires sectoriels reste à confirmer. Les autres réponses anonymes ne sont pas attribuées par déduction.
- Les périodes mentionnées dans les questions sont conservées ; la date d’envoi d’un export n’est pas la date d’enquête.
- Les champs conditionnels et les libellés répétés doivent être lus avec leur contexte dans le formulaire. Aucun calcul automatique n’est effectué sur ces déclarations.
- Les réponses sur les naissances nécessitent une vérification : des accouchements d’adolescentes sont déclarés alors que le total des accouchements enregistrés est zéro. Les périmètres de recueil peuvent différer.
- Les documents ORE restent disponibles séparément, sans attribution à Blactote ou Dalmette.''')
        st.dataframe(pd.DataFrame([{'Questionnaire': r['questionnaire'], 'Question': r['question'], 'Fichier': r['source'], 'Feuille': r['feuille'], 'Ligne': r['ligne'], 'Colonne': r['colonne'], 'Localisation': r['localisation']} for r in selected]), hide_index=True, use_container_width=True)
