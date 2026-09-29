"""Plain-language walkthrough, using the shared seven-second presentation."""
from publication_web import tr
from modele_parcours import render_feedback


def render():
    stages = [
        (('1. Des résultats bruts', '1. Raw results', '1. Resultados brutos', '1. Rezilta brit'),
         ('Les données arrivent en pourcentages, en durées ou en quantités. On ne peut pas les additionner directement pour mesurer la résilience.',
          'Data arrive as percentages, durations or quantities. We cannot simply add them to measure resilience.',
          'Los datos llegan como porcentajes, tiempos o cantidades. No podemos sumarlos directamente para medir la resiliencia.',
          'Done yo vini an pousantaj, dire oswa kantite. Nou pa ka jis ajoute yo pou mezire rezilyans.'),
         ('Il faut une échelle commune : de 0 à 10.', 'We need a common scale: 0 to 10.', 'Necesitamos una escala común: de 0 a 10.', 'Nou bezwen yon echèl komen: 0 rive 10.')),
        (('2. Normaliser avec une référence', '2. Normalise against a reference', '2. Normalizar con una referencia', '2. Nòmalize avèk yon referans'),
         ('Si une distribution de référence fiable existe, on situe le résultat parmi ces valeurs. Des seuils par quantiles lui attribuent un score.',
          'When a reliable reference distribution exists, we locate the result within it. Quantile thresholds assign a score.',
          'Si existe una distribución de referencia fiable, situamos el resultado en ella. Los umbrales por cuantiles asignan una puntuación.',
          'Lè gen yon distribisyon referans ki fyab, nou mete rezilta a ladan l. Papòt kantil yo bay yon nòt.'),
         ('Méthode 1 · Se comparer à une distribution de référence.', 'Method 1 · Compare with a reference distribution.', 'Método 1 · Comparar con una distribución de referencia.', 'Metòd 1 · Konpare ak yon distribisyon referans.')),
        (('3. Normaliser avec des repères locaux', '3. Normalise using local benchmarks', '3. Normalizar con referencias locales', '3. Nòmalize ak repè lokal'),
         ('Sans référence comparative robuste, on définit une situation critique et une situation optimale. Neuf classes intermédiaires complètent les onze niveaux de 0 à 10.',
          'Without a robust comparative reference, we define critical and optimal situations. Nine intermediate classes complete the eleven levels from 0 to 10.',
          'Sin una referencia comparativa sólida, definimos una situación crítica y una óptima. Nueve clases intermedias completan los once niveles de 0 a 10.',
          'San yon referans konparatif solid, nou defini yon sitiyasyon kritik ak yon sitiyasyon optimal. Nèf klas entèmedyè konplete onz nivo soti 0 rive 10.'),
         ('Méthode 2 · Situer le résultat entre deux repères locaux.', 'Method 2 · Locate the result between two local benchmarks.', 'Método 2 · Situar el resultado entre dos referencias locales.', 'Metòd 2 · Mete rezilta a ant de repè lokal.')),
        (('4. Pondérer par jugement d’experts', '4. Apply expert weights', '4. Ponderar mediante juicio experto', '4. Bay pwa selon jijman ekspè'),
         ('Les indicateurs n’ont pas tous la même importance dans le cadre. Un groupe d’experts attribue à chacun un poids, utilisé lors de leur combinaison.',
          'Indicators do not all have the same importance in the framework. Experts assign each a weight used when combining them.',
          'Los indicadores no tienen todos la misma importancia en el marco. Los expertos asignan a cada uno un peso para combinarlos.',
          'Endikatè yo pa tout gen menm enpòtans nan kad la. Ekspè yo bay chak yon pwa pou konbine yo.'),
         ('Le poids exprime une importance, pas un résultat mesuré.', 'A weight expresses importance, not a measured result.', 'El peso expresa importancia, no un resultado medido.', 'Pwa a eksprime enpòtans, li pa yon rezilta mezire.')),
        (('5. Combiner les scores', '5. Combine the scores', '5. Combinar las puntuaciones', '5. Konbine nòt yo'),
         ('On obtient un score par indicateur, puis des moyennes pondérées par dimension et pour l’ensemble. Les indicateurs sans score sont exclus du calcul, pas comptés comme zéro.',
          'We obtain an indicator score, then weighted averages by dimension and overall. Indicators without scores are excluded, not counted as zero.',
          'Obtenemos una puntuación por indicador y promedios ponderados por dimensión y para el conjunto. Los indicadores sin puntuación se excluyen, no cuentan como cero.',
          'Nou jwenn yon nòt pou chak endikatè, apre sa mwayèn pondéré pou chak dimansyon ak pou tout ansanm. Endikatè san nòt yo pa antre nan kalkil la, yo pa konte kòm zewo.'),
         ('Somme des (scores × poids) ÷ somme des poids retenus.', 'Sum of (scores × weights) ÷ sum of included weights.', 'Suma de (puntuaciones × pesos) ÷ suma de los pesos incluidos.', 'Sòm (nòt × pwa) ÷ sòm pwa ki antre yo.')),
        (('6. Lire le résultat', '6. Interpret the result', '6. Interpretar el resultado', '6. Entèprete rezilta a'),
         ('Le barème permet aussi de lire une valeur brute sur l’échelle de résilience. On conserve la valeur mesurée et son unité, à côté du score : plus le score est élevé, plus la situation est jugée favorable dans ce cadre.',
          'The benchmark also lets us interpret a raw value on the resilience scale. We retain the measurement and its unit alongside the score: higher scores indicate conditions judged more favourable in this framework.',
          'El baremo también permite interpretar un valor bruto en la escala de resiliencia. Conservamos el valor y su unidad junto a la puntuación: una puntuación mayor indica una situación considerada más favorable en este marco.',
          'Barèm nan pèmèt nou li yon valè brit sou echèl rezilyans lan tou. Nou kenbe valè mezire a ak inite li bò kote nòt la: yon nòt pi wo endike yon sitiyasyon ki konsidere pi favorab nan kad sa a.'),
         ('Valeur brute → barème → score de résilience.', 'Raw value → benchmark → resilience score.', 'Valor bruto → baremo → puntuación de resiliencia.', 'Valè brit → barèm → nòt rezilyans.')),
    ]
    render_feedback([tuple(tr(part) for part in stage) for stage in stages], summary=tr((
        'Données brutes → normalisation → pondération → scores par indicateur, par dimension et global.',
        'Raw data → normalisation → weighting → indicator, dimension and overall scores.',
        'Datos brutos → normalización → ponderación → puntuaciones por indicador, dimensión y global.',
        'Done brit → nòmalizasyon → pondérasyon → nòt endikatè, dimansyon ak nòt global.')))
