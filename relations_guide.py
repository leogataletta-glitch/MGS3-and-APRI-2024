"""Explain the two observation levels supported by the relationship tools."""
import streamlit as st


def render(fr):
    st.markdown('### ' + ('Que peut-on apprendre avec cette base ?' if fr else 'What can this dataset tell us?'))
    st.write(
        'La base permet de repérer des pratiques qui vont ensemble, des différences entre groupes de répondants et des liens entre caractéristiques des sections communales. Ces résultats servent à formuler des hypothèses et à orienter les enquêtes et les décisions ; ils ne démontrent pas, à eux seuls, pourquoi une situation se produit.'
        if fr else
        'The dataset can reveal practices that occur together, differences between respondent groups and relationships between communal-section characteristics. These findings help develop hypotheses and guide further investigation and decisions; alone, they do not establish why something happens.')
    with st.expander('Deux niveaux de comparaison : répondants et territoires' if fr else 'Two comparison levels: respondents and territories', expanded=True):
        st.markdown('''
**Entre réponses individuelles.** « Comparer deux variables » permet, par exemple, de comparer la proportion de cultivateurs de riz parmi les agriculteurs interrogés sur le littoral et en montagne. On peut aussi comparer une réponse selon le sexe, la tranche d’âge, la strate de richesse ou une autre réponse au questionnaire. Le résultat est une proportion et, pour deux groupes, un écart en points de pourcentage. Il ne s’agit pas d’un coefficient de corrélation entre catégories auxquelles on aurait attribué des nombres arbitraires.

**Entre indicateurs territoriaux.** Le classement compare les valeurs de deux indicateurs dans les mêmes sections communales : les sections les mieux placées sur le premier le sont-elles aussi sur le second ? Chaque section constitue une observation. Les scores APRI ne sont pas des scores individuels : on ne les répète pas pour chaque ménage afin de gonfler artificiellement l’effectif.

**Entre un indicateur et une variable d’enquête.** Pour chaque section, on calcule la proportion de réponses valides correspondant à une modalité, puis on la rapproche de l’indicateur de cette section. On peut ainsi explorer le lien entre un indicateur disponible et la part de répondants déclarant cultiver du riz. Cela décrit une association entre territoires, pas nécessairement entre personnes.
''' if fr else '''
**Between individual answers.** “Compare two variables” can compare, for example, the share of rice growers among surveyed farmers in coastal and mountain areas. An answer can also be compared by sex, age group, wealth stratum or another questionnaire answer. Results are proportions and, for two groups, percentage-point differences, not correlations between arbitrary numeric codes assigned to categories.

**Between territorial indicators.** The ranking compares two indicators across the same communal sections: do sections ranking high on one also rank high on the other? Each section is one observation. APRI scores are not individual scores; they are not repeated for every household to artificially inflate the sample size.

**Between an indicator and a survey variable.** Within each section, the tool computes the share of valid answers selecting a response, then compares it with that section’s indicator. For example, it can explore an available indicator against the share reporting rice cultivation. This describes an association between territories, not necessarily between people.
''')
    with st.expander('Lire le classement et juger la solidité d’un lien' if fr else 'Read the ranking and assess a relationship'):
        st.write('Le classement « Associations entre répondants » utilise φ (phi) pour deux réponses binaires et présente les proportions observées dans les mêmes répondants. Le classement « Corrélations entre sections » utilise ρ de Spearman. Ce sont deux analyses distinctes : leurs effectifs et leurs coefficients ne doivent pas être mélangés.' if fr else '“Respondent associations” uses phi for two binary answers and shows observed proportions among the same respondents. “Section correlations” uses Spearman rho. These are separate analyses: their sample sizes and coefficients must not be combined.')
        st.markdown('''
Le classement utilise **ρ de Spearman**, qui compare les rangs des sections. Il va de −1 à +1 : un signe positif indique que les deux mesures tendent à augmenter ensemble ; un signe négatif qu’elles évoluent en sens opposés. Une valeur proche de zéro indique peu de relation monotone, mais n’exclut pas une relation plus complexe. **ρ = 0,8 ne signifie ni « 80 % d’impact », ni « 80 % de certitude ».**

Les valeurs brutes décrivent directement les phénomènes. Les scores de résilience décrivent leur position sur le barème : une valeur brute élevée peut être défavorable, alors qu’un score élevé représente une meilleure résilience. Le passage en classes de scores crée des égalités et peut modifier la corrélation. L’unité propre à chaque indicateur reste à consulter dans sa fiche.

Le classement exige au moins **8 sections communes sur 10**. Pour les proportions d’enquête, il exige par défaut au moins **30 réponses valides par section**, seuil réglable. Ce ne sont pas des garanties de représentativité ou de précision. Les absences, refus et questions non posées ne deviennent jamais des réponses « non » ; seuls les répondants admissibles à la question doivent être comparés. Les effectifs peuvent donc différer d’une paire à l’autre.

Pour les vingt premières paires, les colonnes « −1 section » montrent comment ρ varie quand on retire successivement chaque section. Un changement de signe révèle un lien particulièrement sensible. Ces bornes ne sont pas un intervalle de confiance. Le graphique permet d’examiner les points et d’identifier une section qui porte presque tout le résultat.

Les liens issus de la même question source sont écartés automatiquement lorsqu’elle est identifiée. D’autres liens mécaniques peuvent subsister : indicateurs partageant une définition, un dénominateur ou des composantes. Une forte corrélation peut alors refléter la construction des mesures plutôt qu’un mécanisme du paysage.
''' if fr else '''
The ranking uses **Spearman’s rho**, comparing section ranks. It ranges from −1 to +1: positive values mean the measures tend to increase together; negative values mean opposite directions. Near zero means little monotonic relationship, but does not rule out a more complex one. **Rho = 0.8 means neither “80% impact” nor “80% certainty”.**

Raw values describe phenomena directly. Resilience scores describe their position on the reference scale: a high raw value can be adverse, while a high score represents greater resilience. Score classes introduce ties and can change the correlation. Consult each indicator’s description for its unit.

Ranking requires at least **8 shared sections out of 10**. Survey proportions require at least **30 valid answers per section** by default, adjustable by the user. These thresholds do not guarantee representativeness or precision. Missing, refused and skipped answers never become “no”; comparisons must use respondents eligible for the question. Sample sizes can differ between pairs.

For the top twenty pairs, “−1 section” columns show how rho changes when each section is omitted in turn. A sign change indicates particular sensitivity. These bounds are not confidence intervals. Inspect the plot to identify sections that dominate the result.

Pairs from the same identified source question are excluded automatically. Other mechanical links can remain between measures sharing definitions, denominators or components. Strong correlations can therefore reflect how measures are constructed rather than a landscape mechanism.
''')
    with st.expander('Ce que ces résultats ne permettent pas d’affirmer' if fr else 'What these results cannot establish'):
        st.write(
            'L’enquête est une observation à un moment donné : elle ne permet pas, seule, de mesurer un changement dans le temps ou l’effet d’une intervention. Dire « le littoral cause la culture du riz » irait au-delà des résultats : irrigation, sols, revenus ou accès au marché pourraient expliquer le lien. Les filtres permettent d’examiner des sous-groupes mais ne constituent pas un ajustement multivarié. Les dix sections peuvent aussi partager des conditions géographiques : elles ne sont pas nécessairement indépendantes. Enfin, chercher parmi des milliers de paires fait apparaître des corrélations fortes par hasard. L’outil ne fournit donc ni classement de causes ni résultats statistiquement confirmés. Il faut confronter les pistes au terrain, aux définitions des indicateurs et, si possible, à d’autres observations.'
            if fr else
            'This survey is a snapshot: alone, it cannot measure change over time or intervention effects. “Coastal location causes rice cultivation” would go beyond the findings: irrigation, soils, income or market access could explain the relationship. Filters inspect subgroups but are not multivariable adjustment. The ten sections can share geographic conditions and are not necessarily independent. Searching thousands of pairs can also produce strong correlations by chance. The tool therefore ranks neither causes nor statistically confirmed findings. Check these leads against field knowledge, indicator definitions and, where possible, additional observations.')
