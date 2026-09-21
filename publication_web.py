"""Public navigation, usage information and optional public session counter."""
import streamlit as st
import i18n
from pathlib import Path
from a_propos_page import COURRIEL

BASE_URL = 'https://enquete-menage-2024-4a9hs29btbw94pnrtxbe7a.streamlit.app/'
PAGES = {
    'portail': ('Accueil', 'Home', 'Inicio', 'Akèy'),
    'methodologie': ('Cadre de résilience', 'Resilience framework', 'Marco de resiliencia', 'Kad rezilyans'),
    'accueil': ('Le territoire', 'The territory', 'El territorio', 'Teritwa a'),
    'dimensions': ('Analyse des résultats', 'Results analysis', 'Análisis de resultados', 'Analiz rezilta yo'),
    'boucles': ('Boucles de rétroaction', 'Feedback loops', 'Bucles de retroalimentación', 'Bouk retwoaksyon'),
    'actions': ('Profils d’intervention', 'Intervention profiles', 'Perfiles de intervención', 'Pwofil entèvansyon'),
    'donnees': ('Données', 'Data', 'Datos', 'Done'),
    'apropos': ('À propos', 'About APRI', 'Acerca de APRI', 'Sou APRI'),
    'contact': ('Nous contacter', 'Contact us', 'Contacto', 'Kontakte nou'),
    'cgu': ('Conditions d’utilisation', 'Terms of use', 'Condiciones de uso', 'Kondisyon itilizasyon'),
}

def tr(values):
    return values[{'fr': 0, 'en': 1, 'es': 2, 'ht': 3}.get(i18n.get_lang(), 1)]

def resolve_page(values):
    """Only known, singular page names are accepted; never execute a URL value."""
    if not values:
        return 'portail'
    return values[0] if len(values) == 1 and values[0] in PAGES else 'introuvable'

def initialise():
    values = st.query_params.get_all('page')
    signature = tuple(values)
    if st.session_state.get('_public_url_seen') != signature:
        st.session_state['app_mode'] = resolve_page(values)
        st.session_state['_public_url_seen'] = signature

def go(page):
    if page not in PAGES:
        raise ValueError('Unknown APRI page')
    st.session_state['app_mode'] = page
    st.query_params['page'] = page
    st.session_state['_public_url_seen'] = (page,)

def sync():
    page = st.session_state.get('app_mode', 'portail')
    if page in PAGES and st.query_params.get_all('page') != [page]:
        st.query_params['page'] = page
        st.session_state['_public_url_seen'] = (page,)

TERMS = {
 'fr': [
  ('Objet', 'APRI présente les paysages, les résultats d’enquête et les indicateurs de résilience en Haïti. La plateforme est portée par le Programme des Nations Unies pour l’environnement (PNUE).'),
  ('Bien utiliser les résultats', 'Lisez la source, la date, l’effectif et la méthode avant d’utiliser un résultat. Une association statistique ne démontre pas une causalité. Les simulations sont pédagogiques et ne constituent pas des prévisions. Les données et méthodes peuvent être corrigées ou mises à jour.'),
  ('Données individuelles', 'L’accès aux données individuelles se fait sur demande après validation. Envoyer une demande ne donne pas automatiquement accès aux fichiers. Ne tentez pas d’identifier les ménages ni de contourner les restrictions d’accès.'),
  ('Réutilisation et références', 'Citez APRI, la source et la date de consultation. Vérifiez les droits propres à chaque donnée, document, image et logiciel avant réutilisation. La présence d’un téléchargement ne constitue pas une licence générale. Les logos ne doivent pas laisser croire à un soutien institutionnel non accordé.'),
  ('Contact et services externes', 'Pour signaler une erreur ou demander un accès, contactez l’équipe APRI. Ne joignez pas de données personnelles de ménages. Les liens externes et l’hébergement relèvent aussi des règles de leurs fournisseurs.'),
 ],
 'en': [
  ('Purpose', 'APRI presents landscapes, survey findings and resilience indicators in Haiti. The platform is led by the United Nations Environment Programme (UNEP).'),
  ('Using the results', 'Read the source, date, sample size and method before using a result. Statistical association does not demonstrate causation. Simulations are educational, not forecasts. Data and methods may be corrected or updated.'),
  ('Individual data', 'Access to individual data requires a request and approval. A request does not automatically grant access to files. Do not attempt to identify households or bypass access restrictions.'),
  ('Reuse and references', 'Credit APRI and the source, and record the access date. Check the rights applying to each dataset, document, image and software before reuse. A download does not grant a general licence. Logos must not imply institutional endorsement that has not been granted.'),
  ('Contact and external services', 'Contact the APRI team to report an error or request access. Do not attach household personal data. External links and hosting are also subject to their providers’ rules.'),
 ],
 'es': [
  ('Objeto', 'APRI presenta paisajes, resultados de encuestas e indicadores de resiliencia en Haití. La plataforma está impulsada por el Programa de las Naciones Unidas para el Medio Ambiente (PNUMA/UNEP).'),
  ('Uso de los resultados', 'Consulte la fuente, fecha, tamaño de muestra y método antes de utilizar un resultado. Una asociación estadística no demuestra causalidad. Las simulaciones son educativas, no predicciones. Los datos y métodos pueden corregirse o actualizarse.'),
  ('Datos individuales', 'El acceso a los datos individuales requiere solicitud y aprobación. Una solicitud no concede acceso automático. No intente identificar a los hogares ni eludir las restricciones de acceso.'),
  ('Reutilización y referencias', 'Cite APRI, la fuente y la fecha de consulta. Compruebe los derechos de cada conjunto de datos, documento, imagen y programa antes de reutilizarlos. Una descarga no otorga una licencia general. Los logotipos no deben sugerir un respaldo institucional no concedido.'),
  ('Contacto y servicios externos', 'Contacte al equipo APRI para comunicar errores o solicitar acceso. No adjunte datos personales de hogares. Los enlaces externos y el alojamiento también están sujetos a las reglas de sus proveedores.'),
 ],
 'ht': [
  ('Objektif', 'APRI prezante peyizaj, rezilta ankèt ak endikatè rezilyans ann Ayiti. Pwogram Nasyonzini pou Anviwònman an (UNEP) pote platfòm la.'),
  ('Itilize rezilta yo', 'Li sous la, dat la, kantite repons yo ak metòd la anvan w itilize yon rezilta. Yon relasyon estatistik pa pwouve yon kòz. Similasyon yo se zouti edikatif, se pa prediksyon. Done ak metòd yo ka korije oswa mete ajou.'),
  ('Done endividyèl', 'Aksè ak done endividyèl mande yon demann ak yon apwobasyon. Yon demann pa bay aksè otomatik ak fichye yo. Pa eseye idantifye kay yo ni kontoune restriksyon aksè yo.'),
  ('Reyitilizasyon ak referans', 'Site APRI, sous la ak dat konsiltasyon an. Verifye dwa ki aplike pou chak done, dokiman, imaj ak lojisyèl anvan w reyitilize yo. Yon telechajman pa bay yon lisans jeneral. Pa sèvi ak logo yo pou fè kwè gen yon sipò enstitisyonèl yo pa bay.'),
  ('Kontak ak sèvis ekstèn', 'Kontakte ekip APRI pou rapòte yon erè oswa mande aksè. Pa mete done pèsonèl kay yo nan mesaj la. Lyen ekstèn ak sèvis ebèjman yo gen règ founisè pa yo tou.'),
 ],
}

def terms():
    st.caption(tr(('Mise à jour : 21 septembre 2026', 'Updated: 21 September 2026', 'Actualización: 21 de septiembre de 2026', 'Mizajou: 21 septanm 2026')))
    for heading, text in TERMS.get(i18n.get_lang(), TERMS['en']):
        st.markdown('**' + heading + '**')
        st.write(text)
    st.markdown(tr((
      'Référence institutionnelle : [conditions d’utilisation du PNUE](https://www.unep.org/terms-use). Ces indications pratiques ne remplacent pas les conditions institutionnelles ni les droits propres aux sources.',
      'Institutional reference: [UNEP terms of use](https://www.unep.org/terms-use). This practical guidance does not replace institutional terms or source-specific rights.',
      'Referencia institucional: [condiciones de uso del PNUMA](https://www.unep.org/terms-use). Estas indicaciones prácticas no sustituyen las condiciones institucionales ni los derechos de cada fuente.',
      'Referans enstitisyonèl: [kondisyon itilizasyon UNEP](https://www.unep.org/terms-use). Konsèy pratik sa yo pa ranplase kondisyon enstitisyonèl yo ni dwa ki aplike pou chak sous.')))
    st.markdown(f'[Contact APRI](mailto:{COURRIEL})')

def footer():
    with st.expander(tr(PAGES['cgu'])):
        terms()
    with st.expander(tr(('Plan du site', 'Site map', 'Mapa del sitio', 'Plan sit la'))):
        for page, titles in PAGES.items():
            st.button(tr(titles), key='sitemap_' + page, on_click=go, args=(page,))
        st.link_button('Sitemap XML', BASE_URL + '~/+/app/static/sitemap.xml')
    with st.expander(tr(('Partager APRI', 'Share APRI', 'Compartir APRI', 'Pataje APRI'))):
        lang = i18n.get_lang() if i18n.get_lang() in TERMS else 'en'
        asset = Path(__file__).parent / 'static' / f'apri-partage-{lang}.png'
        if asset.is_file():
            st.image(str(asset), caption=tr(('Visuel pour accompagner votre publication', 'Image to accompany your post', 'Imagen para acompañar su publicación', 'Imaj pou akonpaye piblikasyon ou')), width=600)
            st.download_button('PNG ↓', asset.read_bytes(), file_name=asset.name, mime='image/png', key='share_image')
        st.markdown(f'[APRI]({BASE_URL})')

def not_found():
    st.subheader(tr(('Page introuvable', 'Page not found', 'Página no encontrada', 'Paj la pa jwenn')))
    st.write(tr(('Ce lien ne correspond à aucune page APRI. Vous pouvez revenir à l’accueil ou consulter les résultats.', 'This link does not match an APRI page. Return home or explore the results.', 'Este enlace no corresponde a una página APRI. Vuelva al inicio o explore los resultados.', 'Lyen sa a pa koresponn ak yon paj APRI. Retounen nan akèy la oswa gade rezilta yo.')))
    st.button(tr(PAGES['portail']), on_click=go, args=('portail',), type='primary')
    st.button(tr(PAGES['dimensions']), on_click=go, args=('dimensions',))
