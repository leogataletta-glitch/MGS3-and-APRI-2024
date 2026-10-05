"""Published study summaries; no household joins or changes to APRI scores.

Source: PNUE MGS3, Biodiversité et résilience paysagère, Volet 1,
October 2026. Values are transcribed, not recomputed from individual records.
"""
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from publication_web import tr

BASE = Path(__file__).parent
PDF = BASE / 'bio_rapport_2026.pdf'


def t(fr, en, es, ht):
    return tr((fr, en, es, ht))


def source(pages):
    st.caption(t('Source : rapport PNUE MGS3, volet 1, octobre 2026',
                 'Source: PNUE MGS3 report, Part 1, October 2026',
                 'Fuente: informe PNUE MGS3, parte 1, octubre de 2026',
                 'Sous: rapò PNUE MGS3, pati 1, oktòb 2026') + ' · p. ' + pages)


def scope():
    st.caption(t('Résultats transcrits du rapport · octobre 2025–mars 2026 · Sites étudiés, pas l’ensemble des dix sections communales. Aucun score territorial n’est ajouté.',
                 'Results transcribed from the report · October 2025–March 2026 · Surveyed sites, not all ten communal sections. No territorial score is added.',
                 'Resultados transcritos del informe · octubre de 2025–marzo de 2026 · Sitios estudiados, no las diez secciones comunales completas. No se añade ninguna puntuación territorial.',
                 'Rezilta ki soti nan rapò a · oktòb 2025–mas 2026 · Sit etidye yo, pa tout dis seksyon kominal yo. Pa gen nòt teritoryal ki ajoute.'))


def chart(labels, values, ylabel, title, key):
    fig = go.Figure(go.Bar(x=labels, y=values, marker_color='#28745c',
                          text=[str(v) for v in values], textposition='outside',
                          hovertemplate='%{x}<br>%{y}<extra></extra>'))
    fig.update_layout(template='plotly_white', height=340,
                      font=dict(family='Source Sans 3, Arial, sans-serif', size=13, color='#34483f'),
                      title=dict(text=title, font=dict(size=15)),
                      margin=dict(t=55, b=40, l=55, r=20), showlegend=False,
                      yaxis=dict(title=ylabel, range=[0, max(values)*1.23]),
                      xaxis=dict(title=None), paper_bgcolor='white', plot_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True, key=key,
                    config={'displaylogo': False, 'scrollZoom': False})


def metrics(items):
    for col, (name, value) in zip(st.columns(len(items)), items):
        col.metric(name, value)


def render(controls):
    groups = {
        'pollinisateurs': t('Pollinisateurs', 'Pollinators', 'Polinizadores', 'Polinizatè'),
        'odonates': t('Libellules et demoiselles', 'Dragonflies and damselflies', 'Libélulas y caballitos del diablo', 'Libèl ak demwazèl'),
    }
    views = {
        'results': t('Résultats', 'Results', 'Resultados', 'Rezilta'),
        'indicators': t('Lien avec les indicateurs APRI', 'Link to APRI indicators', 'Relación con los indicadores APRI', 'Lyen ak endikatè APRI yo'),
        'report': t('Rapport complet et figures', 'Full report and figures', 'Informe completo y figuras', 'Rapò konplè ak figi yo'),
    }
    with controls[0]:
        group = st.selectbox(t('Groupe étudié', 'Study group', 'Grupo estudiado', 'Gwoup etidye'), list(groups),
                             format_func=groups.get, key='bio_group')
    with controls[1]:
        view = st.selectbox(t('Afficher', 'Show', 'Mostrar', 'Montre'), list(views),
                            format_func=views.get, key='bio_view')
    st.subheader(groups[group])
    scope()
    if view == 'report':
        report(group)
    elif view == 'indicators':
        indicators()
    elif group == 'pollinisateurs':
        pollinators()
    else:
        odonates()


def pollinators():
    st.write('Port-Salut · Roche-à-Bateau · Beaumont · Arniquet')
    metrics([(t('Individus capturés', 'Individuals captured', 'Individuos capturados', 'Endividi kaptire'), '373'),
             (t('Taxons recensés', 'Taxa recorded', 'Taxones registrados', 'Takson anrejistre'), '30'),
             (t('Unités de terrain', 'Field units', 'Unidades de campo', 'Inite sou teren'), '12'),
             (t('Relevés', 'Surveys', 'Muestreos', 'Releve'), '48')])
    st.caption(t('12 unités suivies 4 fois : 48 relevés, pas 48 sites indépendants. Un taxon est un groupe identifié ; il ne correspond pas nécessairement à une espèce confirmée.',
                 '12 units sampled 4 times: 48 surveys, not 48 independent sites. A taxon is an identified group, not necessarily a confirmed species.',
                 '12 unidades muestreadas 4 veces: 48 muestreos, no 48 sitios independientes. Un taxón es un grupo identificado, no necesariamente una especie confirmada.',
                 '12 inite etidye 4 fwa: 48 releve, pa 48 sit endepandan. Yon takson se yon gwoup idantifye, li pa nesesèman yon espès konfime.'))
    source('19–24, 27')
    st.write(t('Dans les secteurs les plus transformés par les activités humaines, les captures sont moins abondantes et comportent moins de taxons. Il s’agit d’une comparaison entre secteurs, pas d’une baisse observée au fil des années.',
               'The more human-modified sectors have fewer captures and fewer taxa. This is a comparison between sectors, not a decline measured over years.',
               'En los sectores más transformados por la actividad humana hay menos capturas y menos taxones. Es una comparación entre sectores, no una disminución medida a lo largo de los años.',
               'Nan sektè aktivite moun plis transfòme yo, gen mwens kaptire ak mwens takson. Se yon konparezon ant sektè, pa yon bès mezire sou plizyè ane.'))
    levels = [t('Faible', 'Low', 'Baja', 'Ba'), t('Intermédiaire', 'Intermediate', 'Intermedia', 'Mwayen'), t('Forte', 'High', 'Alta', 'Wo')]
    measures = {
        'abundance': t('Abondance des captures', 'Capture abundance', 'Abundancia de capturas', 'Kantite kaptire'),
        'richness': t('Nombre de taxons', 'Number of taxa', 'Número de taxones', 'Kantite takson'),
    }
    measure = st.selectbox(t('Mesure', 'Measure', 'Medida', 'Mezi'), list(measures),
                           format_func=measures.get, key='bio_poll_measure')
    vals = [12.71, 6.77, 3.33] if measure == 'abundance' else [4.03, 2.27, 1.45]
    chart(levels, vals, t('Moyenne estimée par le modèle', 'Model-estimated mean', 'Media estimada por el modelo', 'Mwayèn modèl la estime'),
          t('Selon le niveau d’anthropisation', 'By degree of human modification', 'Según el grado de transformación humana', 'Selon nivo transfòmasyon moun fè'), 'bio_poll_chart')
    st.caption(t('Moyennes ajustées publiées, distinctes des moyennes brutes. Les intervalles de confiance à 95 % sont visibles dans les figures originales 2 et 3 du rapport ; ils ne sont pas reconstruits ici.',
                 'Published adjusted means, distinct from raw averages. The 95% confidence intervals are shown in original report figures 2 and 3; they are not reconstructed here.',
                 'Medias ajustadas publicadas, distintas de las medias brutas. Los intervalos de confianza del 95 % están en las figuras originales 2 y 3; no se reconstruyen aquí.',
                 'Mwayèn ajiste ki nan rapò a, diferan ak mwayèn brit yo. Entèval konfyans 95% yo nan figi orijinal 2 ak 3; nou pa rekonstrui yo isit la.'))
    source('28–30, figures 2–3')
    with st.expander(t('Comprendre les résultats et leurs limites', 'Understand results and limits', 'Entender los resultados y sus límites', 'Konprann rezilta yo ak limit yo')):
        st.write(t('Les tests du rapport indiquent une association avec le gradient : p = 9,12 × 10⁻¹³ pour l’abondance ; p = 3,64 × 10⁻¹⁴ pour la richesse. Une petite valeur de p n’indique ni la taille de l’effet, ni une preuve de causalité. Plusieurs caractéristiques des habitats varient ensemble.',
                   'Report tests show an association with the gradient: p = 9.12 × 10⁻¹³ for abundance; p = 3.64 × 10⁻¹⁴ for richness. A small p-value is neither an effect size nor proof of causality. Several habitat characteristics vary together.',
                   'Los tests del informe indican una asociación con el gradiente: p = 9,12 × 10⁻¹³ para abundancia y p = 3,64 × 10⁻¹⁴ para riqueza. Una p pequeña no mide el tamaño del efecto ni demuestra causalidad. Varias características del hábitat varían juntas.',
                   'Tès rapò a montre yon asosyasyon ak gradyan an: p = 9,12 × 10⁻¹³ pou abondans; p = 3,64 × 10⁻¹⁴ pou richès. Yon ti valè p pa mezire gwosè efè a ni pwouve koz. Plizyè karakteristik abita yo varye ansanm.'))
        st.write(t('Les pièges-bols donnent une vue partielle des insectes présents. Les captures ne mesurent pas directement la pollinisation des cultures, les rendements ou la capacité du paysage à récupérer après un choc.',
                   'Pan traps provide a partial view of insects present. Captures do not directly measure crop pollination, yields or landscape recovery after a shock.',
                   'Las trampas dan una visión parcial de los insectos presentes. Las capturas no miden directamente la polinización de cultivos, el rendimiento ni la recuperación del paisaje tras una perturbación.',
                   'Pyèj yo bay yon pati nan imaj ensèk ki prezan yo. Kaptire yo pa mezire dirèkteman polinizasyon rekòt, rannman oswa rekiperasyon peyizaj apre yon chòk.'))
        source('35, 40–41, 82, 85–86')


def odonates():
    st.write('Port-Salut · Roche-à-Bateau · Beaumont · Roseaux')
    metrics([(t('Individus recensés', 'Individuals recorded', 'Individuos registrados', 'Endividi anrejistre'), '1 652'),
             (t('Espèces', 'Species', 'Especies', 'Espès'), '35'),
             (t('Stations', 'Stations', 'Estaciones', 'Estasyon'), '40'),
             (t('Relevés', 'Surveys', 'Muestreos', 'Releve'), '120')])
    st.caption(t('40 stations suivies 3 fois dans 4 cours d’eau. Les relevés répétés ne sont pas des stations supplémentaires.',
                 '40 stations sampled 3 times in 4 watercourses. Repeated surveys are not additional stations.',
                 '40 estaciones muestreadas 3 veces en 4 cursos de agua. Los muestreos repetidos no son estaciones adicionales.',
                 '40 estasyon etidye 3 fwa nan 4 kou dlo. Releve repete yo pa lòt estasyon.'))
    source('47–50, 61')
    chart(['Beaumont', 'Port-Salut', 'Roseaux', 'Roche-à-Bateau'], [5.13, 4.43, 3.80, 3.63],
          t('Espèces par relevé (moyenne)', 'Species per survey (mean)', 'Especies por muestreo (media)', 'Espès pa releve (mwayèn)'),
          t('Richesse observée dans les sites étudiés', 'Observed richness at surveyed sites', 'Riqueza observada en los sitios estudiados', 'Richès obsève nan sit etidye yo'), 'bio_od_chart')
    st.caption(t('Moyennes descriptives publiées, pas le nombre total d’espèces de chaque commune ni un classement des sections. Le test global de l’effet du site sur la richesse donne p = 0,0528 : il ne franchit pas le seuil de 0,05 retenu dans le rapport.',
                 'Published descriptive means, not total species counts for each municipality or a ranking of communal sections. The global site test for richness gives p = 0.0528, above the report’s 0.05 threshold.',
                 'Medias descriptivas publicadas, no el total de especies de cada municipio ni una clasificación de secciones. El test global del sitio sobre la riqueza da p = 0,0528, por encima del umbral de 0,05 del informe.',
                 'Mwayèn deskriptif ki nan rapò a, pa total espès nan chak komin ni yon klasman seksyon yo. Tès global sit la sou richès bay p = 0,0528, pi wo pase limit 0,05 rapò a.'))
    source('62–63')
    st.write(t('Des sites avec moins d’espèces peuvent abriter des espèces différentes et contribuer à la diversité du paysage. Préserver plusieurs types de milieux peut donc compter autant que protéger seulement les sites les plus riches.',
               'Sites with fewer species may host different species and contribute to landscape diversity. Protecting several habitat types can therefore matter alongside protecting the richest sites.',
               'Los sitios con menos especies pueden albergar especies distintas y contribuir a la diversidad del paisaje. Conservar varios tipos de hábitats también importa, además de proteger los sitios más ricos.',
               'Sit ki gen mwens espès ka gen lòt espès ki kontribye nan divèsite peyizaj la. Pwoteje plizyè kalite abita enpòtan tou, ansanm ak sit ki pi rich yo.'))
    st.caption(t('78,19 % des différences de composition entre stations correspondent au remplacement d’espèces. Ce chiffre ne signifie pas que 78,19 % des espèces ont disparu. Il ne mesure pas une évolution dans le temps.',
                 '78.19% of compositional dissimilarity between stations is attributed to species replacement. This does not mean 78.19% of species have disappeared, and does not measure change over time.',
                 'El 78,19 % de la disimilitud entre estaciones corresponde al reemplazo de especies. No significa que haya desaparecido el 78,19 % de las especies ni mide una evolución temporal.',
                 '78,19% diferans konpozisyon ant estasyon yo soti nan ranplasman espès. Sa pa vle di 78,19% espès yo disparèt, ni yon chanjman sou tan.'))
    source('66, 83–85')
    with st.expander(t('Comprendre les résultats et leurs limites', 'Understand results and limits', 'Entender los resultados y sus límites', 'Konprann rezilta yo ak limit yo')):
        st.write(t('Seuls les adultes ont été inventoriés. Leur présence ne prouve pas qu’ils se reproduisent sur place et ne mesure pas directement la potabilité de l’eau. Le gradient amont–aval n’a pas le même sens écologique dans tous les cours d’eau. Trois campagnes ne décrivent pas toute la saisonnalité annuelle.',
                   'Only adults were surveyed. Their presence does not prove local breeding or directly measure drinking-water safety. Upstream–downstream position has different ecological meanings across watercourses. Three campaigns do not describe full annual seasonality.',
                   'Solo se muestrearon adultos. Su presencia no demuestra reproducción local ni mide directamente la potabilidad del agua. El gradiente aguas arriba–abajo no tiene el mismo significado ecológico en todos los ríos. Tres campañas no describen toda la estacionalidad anual.',
                   'Se granmoun yo sèlman ki te etidye. Prezans yo pa pwouve repwodiksyon sou plas ni mezire si dlo a potab. Pozisyon amon–aval pa gen menm sans ekolojik nan tout kou dlo yo. Twa kanpay pa dekri tout sezon nan ane a.'))
        source('49, 83–86')


def indicators():
    rows = [
        ('47', t('Richesse spécifique', 'Species richness', 'Riqueza de especies', 'Richès espès'),
         t('30 taxons de pollinisateurs ; 35 espèces d’odonates, sur l’ensemble des sites de chaque étude.', '30 pollinator taxa; 35 odonate species across all sites in each study.', '30 taxones de polinizadores; 35 especies de odonatos en el conjunto de sitios de cada estudio.', '30 takson polinizatè; 35 espès odonat sou tout sit chak etid.'), '27, 61'),
        ('48', 'Simpson (1−D)',
         t('Pollinisateurs : moyenne publiée 0,479 sous le nom « Simpson ». Vérifier la convention avant de l’assimiler à 1−D. Ne pas inverser une moyenne de Hill q2 pour obtenir une moyenne de Simpson.', 'Pollinators: published mean 0.479 labelled “Simpson”. Verify the convention before treating it as 1−D. Do not invert a mean Hill q2 to derive a mean Simpson value.', 'Polinizadores: media publicada 0,479 bajo “Simpson”. Verificar la convención antes de usarla como 1−D. No invertir la media de Hill q2 para obtener la media de Simpson.', 'Polinizatè: mwayèn 0,479 ki rele “Simpson”. Verifye konvansyon an anvan itilize li kòm 1−D. Pa envèse mwayèn Hill q2 pou jwenn mwayèn Simpson.'), '28, 62'),
        ('49', 'Shannon (H′)',
         t('Moyennes publiées : pollinisateurs 0,818 ; odonates 1,30. Périmètres et protocoles différents : ne pas les comparer comme des scores équivalents.', 'Published means: pollinators 0.818; odonates 1.30. Different coverage and protocols: not directly comparable scores.', 'Medias publicadas: polinizadores 0,818; odonatos 1,30. Coberturas y protocolos distintos: no son puntuaciones directamente comparables.', 'Mwayèn pibliye: polinizatè 0,818; odonat 1,30. Zòn ak pwotokòl diferan: se pa nòt dirèkteman konparab.'), '28, 62'),
    ]
    st.dataframe(pd.DataFrame(rows, columns=['APRI', t('Indicateur', 'Indicator', 'Indicador', 'Endikatè'),
        t('Résultat disponible à l’échelle de l’étude', 'Available study-level result', 'Resultado disponible a escala del estudio', 'Rezilta disponib nan nivo etid la'), 'Pages']), hide_index=True, use_container_width=True)
    st.info(t('Score par section non disponible. Il faut les relevés et coordonnées des stations, puis vérifier les règles de regroupement et les barèmes. Le rapport ne contient pas le volet oiseaux et ne complète pas à lui seul les diversités fonctionnelle et phylogénétique.',
              'Section-level scores are unavailable. Station records and coordinates are needed, followed by checks of aggregation rules and scoring thresholds. The report has no bird component and cannot by itself complete functional or phylogenetic diversity indicators.',
              'No hay puntuaciones por sección. Se necesitan los registros y coordenadas de las estaciones y verificar la agregación y los umbrales. El informe no incluye aves ni completa por sí solo la diversidad funcional o filogenética.',
              'Nòt pa seksyon pa disponib. Nou bezwen releve ak kowòdone estasyon yo, epi verifye fason pou regwoupe yo ak echèl nòt yo. Rapò a pa gen pati zwazo epi li pa sifi pou divèsite fonksyonèl oswa filojenetik.'))


def indicator_notice(number):
    if int(number or 0) not in (47, 48, 49):
        return
    with st.expander(t('Nouveaux résultats de biodiversité disponibles', 'New biodiversity results available', 'Nuevos resultados de biodiversidad disponibles', 'Nouvo rezilta divèsite biyolojik disponib')):
        scope()
        indicators()
        if st.button(t('Voir les résultats de biodiversité', 'View biodiversity results', 'Ver los resultados de biodiversidad', 'Gade rezilta divèsite biyolojik yo'), key='bio_from_indicator'):
            from publication_web import go
            st.session_state['ra_source'] = 'biodiversite'
            st.session_state['ra_vue'] = 'brut'
            go('dimensions')
            st.rerun()


def report(group):
    st.write(t('Rapport PNUE MGS3 · Biodiversité et résilience paysagère · Volet 1 · Octobre 2026 · 97 pages · Français',
               'PNUE MGS3 report · Biodiversity and landscape resilience · Part 1 · October 2026 · 97 pages · French',
               'Informe PNUE MGS3 · Biodiversidad y resiliencia del paisaje · Parte 1 · Octubre de 2026 · 97 páginas · Francés',
               'Rapò PNUE MGS3 · Divèsite biyolojik ak rezilyans peyizaj · Pati 1 · Oktòb 2026 · 97 paj · Franse'))
    st.caption(t('Figures originales : pollinisateurs, p. 29–35 ; odonates, p. 65–69. Les barres d’incertitude et les légendes originales sont conservées dans le document.',
                 'Original figures: pollinators, pp. 29–35; odonates, pp. 65–69. Original uncertainty bars and captions are preserved in the document.',
                 'Figuras originales: polinizadores, pp. 29–35; odonatos, pp. 65–69. El documento conserva las barras de incertidumbre y los pies originales.',
                 'Figi orijinal: polinizatè, paj 29–35; odonat, paj 65–69. Dokiman an konsève ba ensètitid yo ak lejann orijinal yo.'))
    data = PDF.read_bytes()
    st.download_button('PDF ↓', data, file_name=PDF.name, mime='application/pdf', key='bio_pdf_download')
    st.pdf(data, height=680, key='bio_report_reader')

    import pdf_navigation
    pdf_navigation.render("bio_report_reader")
