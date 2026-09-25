"""Institutional declarations awaiting geographic attribution.

This view deliberately has no connection to household data or score engines.
"""
import json
from pathlib import Path

import pandas as pd
import streamlit as st


def load_data():
    return json.loads(Path(__file__).with_name('ore_institutions.json').read_text(encoding='utf-8'))


STATUS = {
    'transcrit': 'Réponse transcrite', 'declaration': 'Déclaration institutionnelle',
    'lecture_a_confirmer': 'Lecture à confirmer', 'contradiction': 'Réponse contradictoire',
    'indetermine': 'Indéterminé', 'non_renseigne': 'Non renseigné',
    'non_enregistre': 'Non enregistré',
}


def display_value(row):
    value = row['valeur']
    if value is None:
        return STATUS[row['statut']]
    if isinstance(value, bool):
        return 'Oui' if value else 'Non'
    if isinstance(value, list):
        return ' ; '.join(value)
    return str(value) + (f" {row['unite']}" if row.get('unite') else '')


def render(controls):
    data = load_data()
    rows = data['observations']
    themes = list(dict.fromkeys(r['theme'] for r in rows))
    with controls[0]:
        theme = st.selectbox('Thème', ['Tous les thèmes'] + themes, key='inst_ore_theme')
    matching = [r for r in rows if theme == 'Tous les thèmes' or r['theme'] == theme]
    lookup = {r['id']: r for r in matching}
    options = ['all'] + list(lookup)
    if st.session_state.get('inst_ore_question') not in options:
        st.session_state['inst_ore_question'] = 'all'
    with controls[1]:
        question = st.selectbox('Question', options, key='inst_ore_question',
                                format_func=lambda key: 'Toutes les questions' if key == 'all' else lookup[key]['libelle'])

    st.markdown('### ORE — section communale à confirmer')
    st.caption('Résultats provisoires · 3 questionnaires · Éducation, santé et CASEC')
    st.info('Le territoire couvert n’est pas encore identifié : ces déclarations ne sont attribuées ni à Blactote ni à Dalmette. Elles ne modifient pas les scores APRI et ne sont pas utilisées dans les corrélations entre ménages.')
    st.caption('Transcription des réponses originales en français. Le formulaire porte la référence MGS3_09/2024 ; la date de collecte reste à confirmer. Les années explicitement mentionnées dans les questions sont conservées.')

    selected = matching if question == 'all' else [lookup[question]]
    if question != 'all':
        row = selected[0]
        st.markdown(f"#### {row['libelle']}")
        st.write(display_value(row))
        st.caption(f"{row['source']} · page {row['page']} · {STATUS[row['statut']]}")
        if row.get('note'):
            st.info(row['note'])
    else:
        st.dataframe(pd.DataFrame([{
            'Question': r['libelle'], 'Réponse': display_value(r),
            'Statut': STATUS[r['statut']],
            'Période': str(r['periode']) if r.get('periode') else 'À confirmer / non précisée',
            'Source': f"{r['source']} · p. {r['page']}",
            'Précision': r.get('note', ''),
        } for r in selected]), hide_index=True, use_container_width=True)

    derived = [d for d in data['indicateurs_derives'] if d['source_id'] in {r['id'] for r in selected}]
    if derived:
        with st.expander('Équipements scolaires : effectifs et proportions'):
            st.caption('Proportions provisoires : nombre d’écoles équipées ÷ nombre d’écoles du même niveau × 100. Dénominateurs déclarés : 6 écoles primaires, 2 secondaires. Le périmètre commun aux réponses reste à valider. Un résultat de 50 % au secondaire représente une école sur deux.')
            st.dataframe(pd.DataFrame([{'Service': d['libelle'],
                'Écoles': f"{d['numerateur']} / {d['denominateur']}",
                'Part (%)': d['pourcentage']} for d in derived]), hide_index=True, use_container_width=True)

    with st.expander('Comprendre les données et les vérifications en cours'):
        st.markdown('''- **Un blanc n’est pas un zéro.** « Non renseigné », « indéterminé » et « non enregistré » restent distincts.
- **Une déclaration n’est pas un recensement exhaustif.** « Aucun cas enregistré » ne signifie pas forcément « aucun cas dans la population ».
- **300 cas de malaria déclarés en 2023 est un effectif**, pas un taux d’incidence : la population et le périmètre du recueil ne sont pas connus.
- **Les réponses ambiguës sont exclues des calculs** : cantine secondaire, prise en charge des addictions, COUC/COUL et existence de l’abri d’urgence. Le nom de l’organisme de crédit reste à confirmer.
- **Les trois questionnaires portent sur des secteurs différents.** Ils ne représentent pas trois territoires et ne peuvent pas être transformés en observations individuelles de ménages.
- **La présence des services de santé doit être clarifiée** : le CASEC indique une institution technique de santé non représentée, tandis que le questionnaire santé décrit un dispensaire. Les définitions ou périmètres peuvent différer.
- **La saisie est une sélection structurée des réponses des 25 pages**, pas une transcription exhaustive de tous les champs conditionnels vides.
''')
        st.caption('Sources : District Scolaire.pdf (3 pages), Ministere de la Sante.pdf (11 pages), CASEC.pdf (11 pages), transmis le 25 septembre 2026. Chaque observation renvoie à sa page source. Les scans ne sont pas proposés au téléchargement.')
