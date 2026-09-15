"""Explain the two observation levels supported by the relationship tools."""

from traductions import text as _locale_text
import streamlit as st


def render(fr):
    render_steps('relations', fr)
    with st.expander(_locale_text('Deux niveaux de comparaison : répondants et territoires' if fr else 'Two comparison levels: respondents and territories'), expanded=False):
        st.markdown(_locale_text('''
**Entre réponses individuelles.** « Comparer deux variables » permet, par exemple, de comparer la proportion de cultivateurs de riz parmi les agriculteurs interrogés sur le littoral et en montagne. On peut aussi comparer une réponse selon le sexe, la tranche d’âge, la strate de richesse ou une autre réponse au questionnaire. Le résultat est une proportion et, pour deux groupes, un écart en points de pourcentage. Il ne s’agit pas d’un coefficient de corrélation entre catégories auxquelles on aurait attribué des nombres arbitraires.

**Entre indicateurs territoriaux.** Le classement compare les valeurs de deux indicateurs dans les mêmes sections communales : les sections les mieux placées sur le premier le sont-elles aussi sur le second ? Chaque section constitue une observation. Les scores APRI ne sont pas des scores individuels : on ne les répète pas pour chaque ménage afin de gonfler artificiellement l’effectif.

**Entre un indicateur et une variable d’enquête.** Pour chaque section, on calcule la proportion de réponses valides correspondant à une modalité, puis on la rapproche de l’indicateur de cette section. On peut ainsi explorer le lien entre un indicateur disponible et la part de répondants déclarant cultiver du riz. Cela décrit une association entre territoires, pas nécessairement entre personnes.
''' if fr else '''
**Between individual answers.** “Compare two variables” can compare, for example, the share of rice growers among surveyed farmers in coastal and mountain areas. An answer can also be compared by sex, age group, wealth stratum or another questionnaire answer. Results are proportions and, for two groups, percentage-point differences, not correlations between arbitrary numeric codes assigned to categories.

**Between territorial indicators.** The ranking compares two indicators across the same communal sections: do sections ranking high on one also rank high on the other? Each section is one observation. APRI scores are not individual scores; they are not repeated for every household to artificially inflate the sample size.

**Between an indicator and a survey variable.** Within each section, the tool computes the share of valid answers selecting a response, then compares it with that section’s indicator. For example, it can explore an available indicator against the share reporting rice cultivation. This describes an association between territories, not necessarily between people.
'''))
    with st.expander(_locale_text('Lire le classement et juger la solidité d’un lien' if fr else 'Read the ranking and assess a relationship')):
        st.write(_locale_text('Le classement « Associations entre répondants » utilise φ (phi) pour deux réponses binaires et présente les proportions observées dans les mêmes répondants. Le classement « Corrélations entre sections » utilise ρ de Spearman. Ce sont deux analyses distinctes : leurs effectifs et leurs coefficients ne doivent pas être mélangés.' if fr else '“Respondent associations” uses phi for two binary answers and shows observed proportions among the same respondents. “Section correlations” uses Spearman rho. These are separate analyses: their sample sizes and coefficients must not be combined.'))
        st.markdown(_locale_text('''
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
'''))
    with st.expander(_locale_text('Ce que ces résultats ne permettent pas d’affirmer' if fr else 'What these results cannot establish')):
        st.write(
            _locale_text('L’enquête est une observation à un moment donné : elle ne permet pas, seule, de mesurer un changement dans le temps ou l’effet d’une intervention. Dire « le littoral cause la culture du riz » irait au-delà des résultats : irrigation, sols, revenus ou accès au marché pourraient expliquer le lien. Les filtres permettent d’examiner des sous-groupes mais ne constituent pas un ajustement multivarié. Les dix sections peuvent aussi partager des conditions géographiques : elles ne sont pas nécessairement indépendantes. Enfin, chercher parmi des milliers de paires fait apparaître des corrélations fortes par hasard. L’outil ne fournit donc ni classement de causes ni résultats statistiquement confirmés. Il faut confronter les pistes au terrain, aux définitions des indicateurs et, si possible, à d’autres observations.'
            if fr else
            'This survey is a snapshot: alone, it cannot measure change over time or intervention effects. “Coastal location causes rice cultivation” would go beyond the findings: irrigation, soils, income or market access could explain the relationship. Filters inspect subgroups but are not multivariable adjustment. The ten sections can share geographic conditions and are not necessarily independent. Searching thousands of pairs can also produce strong correlations by chance. The tool therefore ranks neither causes nor statistically confirmed findings. Check these leads against field knowledge, indicator definitions and, where possible, additional observations.'))


def render_steps(mode, fr):
    """Plain-language entry point; numerical examples are explicitly fictional."""
    def t(a, b): return _locale_text(a if fr else b)
    if mode == 'relations':
        st.markdown('**' + t('1. Repérer un lien : regarder deux choses à la fois',
                             '1. Spot a relationship: look at two things at a time') + '**')
        st.markdown(t("""
1. **Choisissez deux choses à comparer.** Par exemple, le type de toilettes et la source d’eau des ménages. Ou choisissez un classement pour repérer des paires à examiner.
2. **Regardez qui répond quoi.** Exemple inventé : 60 ménages sur 100 utilisent un certain type de toilettes dans un groupe, contre 40 sur 100 dans l’autre. L’écart est de **20 points de pourcentage**.
3. **Posez une question, sans conclure trop vite.** Ces réponses vont-elles ensemble ? Le lien pourrait aussi venir du lieu de résidence ou d’autres différences entre les groupes. Ici, on ne tient pas compte de plusieurs facteurs à la fois.
4. **Vérifiez sur qui porte le résultat.** « Variables ↔ variables » compare les réponses des ménages. Les vues avec des indicateurs comparent des sections communales : au maximum dix territoires, pas 1 211 ménages indépendants.
""", """
1. **Choose two things to compare.** For example, household toilet type and drinking water source. Or use a ranking to find pairs worth examining.
2. **Look at who answered what.** Made-up example: 60 out of 100 households use a particular toilet type in one group, versus 40 out of 100 in the other. That is a **20-percentage-point difference**.
3. **Ask a question without jumping to a conclusion.** Do these answers occur together? Location or other differences between groups might also account for the relationship. This tool does not account for several factors at once.
4. **Check who the result describes.** “Variables ↔ variables” compares household answers. Views involving indicators compare communal sections: at most ten territories, not 1,211 independent households.
"""))
        st.info(t('La suite, si vous avez une hypothèse sur les ménages : ouvrez « Facteurs associés » pour tester plusieurs facteurs ensemble. Une forte relation repérée ici reste une piste, même si elle arrive en tête du classement.',
                  'Next, if you have a household-level hypothesis: open “Associated factors” to test several factors together. A strong relationship here remains a lead, even when it tops the ranking.'))
    else:
        st.markdown('**' + t('2. Approfondir un lien : tenir compte de plusieurs choses ensemble',
                             '2. Examine a relationship: account for several things together') + '**')
        st.markdown(t("""
1. **Choisissez la réponse que vous voulez comprendre.** Par exemple : « utiliser des latrines sans dalle ». Le modèle distingue les ménages qui donnent cette réponse des autres répondants à la même question.
2. **Choisissez jusqu’à trois facteurs.** Par exemple une source d’eau et une source de revenu. Choisissez-les parce qu’ils ont un sens pour votre question, pas seulement parce qu’un classement les place en premier.
3. **Cliquez sur « Calculer ».** Le modèle utilise les ménages ayant répondu aux questions retenues. Il compare les réponses à l’intérieur des mêmes sections communales et tient compte des autres facteurs choisis.
4. **Comparez l’écart brut et l’écart ajusté.** Exemple inventé : un écart de 20 points devient 5 points après ajustement. Le lien est plus faible une fois ces différences prises en compte ; cela ne prouve pas ce qui le cause. Un écart peut aussi augmenter ou changer de sens.
5. **Regardez si le résultat tient.** Un intervalle large, qui traverse zéro, ou un changement de signe quand on retire une section invite à la prudence. Le classement concerne seulement vos facteurs choisis : ce n’est pas la liste de toutes les causes.
""", """
1. **Choose the answer you want to understand.** For example: “uses a pit latrine without a slab”. The model distinguishes households giving this answer from other respondents to the same question.
2. **Choose up to three factors.** For example, a water source and an income source. Choose them because they make sense for your question, not just because a ranking puts them first.
3. **Click “Calculate”.** The model uses households that answered the selected questions. It compares responses within the same communal sections while accounting for the other selected factors.
4. **Compare the unadjusted and adjusted differences.** Made-up example: a 20-point difference becomes 5 points after adjustment. The relationship is weaker once these differences are accounted for; that does not prove its cause. A difference can also grow or change direction.
5. **Check whether the result holds up.** A wide interval, an interval crossing zero, or a sign change when a section is removed calls for caution. The ranking covers only your selected factors; it is not a list of all causes.
"""))
        st.info(t('Cet onglet porte uniquement sur les réponses des ménages. Il n’ajuste que les facteurs choisis et la section : les autres différences restent possibles. Il ne sert pas à estimer les causes de la déforestation.',
                  'This tab uses household answers only. It adjusts only for selected factors and section; other differences can remain. It does not estimate the causes of deforestation.'))
    with st.expander(t('Pourquoi deux onglets ? Font-ils doublon ?', 'Why two tabs? Do they duplicate each other?')):
        st.write(t('Ils utilisent parfois les mêmes réponses, mais font deux travaux différents. Relations = explorer des paires et décrire ce qui va ensemble. Facteurs associés = examiner un phénomène précis avec plusieurs facteurs simultanément. Vous pouvez commencer directement par le second si vous avez déjà une hypothèse.',
                   'They sometimes use the same answers, but do different jobs. Relationships explores pairs and describes what occurs together. Associated factors examines one specific outcome with several factors simultaneously. You can start directly with the second if you already have a hypothesis.'))
        st.write(t('Le seul recouvrement est l’écart brut : il sert de point de comparaison avant l’ajustement. Il ne sera identique dans les deux onglets que si la réponse, les groupes et les ménages retenus sont les mêmes. Ajouter un facteur avec des réponses manquantes peut changer l’échantillon. Les coefficients phi ou Spearman du premier onglet ne se comparent pas directement aux points de pourcentage du second.',
                   'The overlap is the unadjusted difference: it provides a starting point before adjustment. It matches across tabs only when the answer, groups and included households are identical. Adding a factor with missing answers can change the sample. Phi or Spearman coefficients in the first tab cannot be directly compared with percentage points in the second.'))
        st.write(t('Dans les deux cas, une association n’est pas une preuve de cause. Chercher beaucoup de combinaisons peut faire apparaître un lien par hasard ; les exemples de 60 %, 40 %, 20 et 5 points ci-dessus sont inventés pour expliquer la lecture.',
                   'In both tools, an association is not proof of a cause. Searching many combinations can find a relationship by chance; the 60%, 40%, 20-point and 5-point examples above are made up to explain how to read results.'))
