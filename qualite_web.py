"""Accessible shared information, without making unverified legal claims."""
import streamlit as st
import i18n
from a_propos_page import COURRIEL

TEXT={
'fr':('Données, confidentialité et utilisation','À propos des données','Les résultats proviennent notamment de l’enquête ménage de 2024. Les effectifs valides peuvent varier selon les questions. Une corrélation décrit une association et ne démontre pas une cause. Les simulations pédagogiques ne sont pas des prévisions.','Confidentialité','Ne transmettez pas de noms, coordonnées GPS, numéros de téléphone ou réponses individuelles dans un message de signalement. Pour une demande concernant les données, contactez l’équipe APRI. Les données individuelles sont accessibles uniquement sur demande après validation.','Réutilisation','Avant de réutiliser un résultat, vérifiez sa source, sa date, ses unités, ses limites et les droits applicables à la source. Citez APRI et la source concernée. Les logos ne constituent pas une autorisation de réutilisation.','Technique et accessibilité','Cette application fonctionne sur Streamlit Community Cloud. Le suivi d’usage facultatif de Streamlit est désactivé dans la configuration de l’application ; cela ne couvre pas les journaux et services propres à l’hébergeur ou aux fournisseurs de cartes. Signalez un problème d’accès ou de lecture en précisant la page, la langue et votre appareil.'),
'en':('Data, privacy and use','About the data','Results draw in particular on the 2024 household survey. Valid sample sizes may vary by question. Correlation describes an association and does not prove causation. Educational simulations are not forecasts.','Privacy','Do not include names, GPS coordinates, phone numbers or individual responses in an issue report. Contact the APRI team about data requests. Individual data are available only on request after approval.','Reuse','Before reusing a result, check its source, date, units, limitations and the rights applying to the source. Credit APRI and the relevant source. Logos do not grant permission to reuse content.','Technology and accessibility','This application runs on Streamlit Community Cloud. Optional Streamlit usage telemetry is disabled in the application configuration; this does not cover the hosting provider’s or map providers’ own logs and services. Report access or readability issues with the page, language and device you used.'),
'es':('Datos, privacidad y uso','Sobre los datos','Los resultados proceden, en particular, de la encuesta de hogares de 2024. El número de respuestas válidas puede variar según la pregunta. Una correlación describe una asociación y no demuestra una causa. Las simulaciones educativas no son predicciones.','Privacidad','No incluya nombres, coordenadas GPS, teléfonos ni respuestas individuales al comunicar un problema. Contacte al equipo APRI para consultas sobre los datos. Los datos individuales están disponibles únicamente previa solicitud y aprobación.','Reutilización','Antes de reutilizar un resultado, compruebe su fuente, fecha, unidades, límites y derechos aplicables. Cite APRI y la fuente correspondiente. Los logotipos no otorgan autorización de reutilización.','Tecnología y accesibilidad','Esta aplicación utiliza Streamlit Community Cloud. La telemetría opcional de Streamlit está desactivada en la configuración; esto no abarca los registros y servicios del proveedor de alojamiento ni de los proveedores de mapas. Para comunicar problemas de acceso o lectura, indique página, idioma y dispositivo.'),
'ht':('Done, vi prive ak itilizasyon','Sou done yo','Rezilta yo soti sitou nan ankèt sou kay ki te fèt an 2024. Kantite repons valab ka varye selon kesyon an. Yon korelasyon montre yon relasyon; li pa pwouve yon kòz. Similasyon edikatif yo pa prediksyon.','Vi prive','Pa mete non, kowòdone GPS, nimewo telefòn oswa repons endividyèl lè w ap rapòte yon pwoblèm. Kontakte ekip APRI pou demann sou done yo. Done endividyèl yo disponib sèlman sou demann apre apwobasyon.','Reyitilizasyon','Anvan w itilize yon rezilta ankò, verifye sous li, dat li, inite li, limit li ak dwa ki aplike yo. Site APRI ak sous la. Logo yo pa bay otorizasyon pou reyitilize kontni an.','Teknoloji ak aksesibilite','Aplikasyon sa a sèvi ak Streamlit Community Cloud. Swivi itilizasyon opsyonèl Streamlit la dezaktive nan konfigirasyon aplikasyon an; sa pa kouvri jounal ak sèvis founisè ebèjman oswa kat yo. Pou rapòte yon pwoblèm aksè oswa lekti, presize paj la, lang lan ak aparèy ou a.')}


def appliquer():
    st.markdown('''<style>
    .stApp.stApp.stApp :is(button,a,input,textarea,select,[role="combobox"],summary):focus-visible{outline:3px solid #146044!important;outline-offset:3px!important;}
    @media(prefers-reduced-motion:reduce){.stApp *, .stApp *::before,.stApp *::after{animation:none!important;transition:none!important;scroll-behavior:auto!important;}}
    @media(max-width:600px){.stApp .st-key-zone_page [data-testid="stHorizontalBlock"]{flex-wrap:wrap;} .stApp .st-key-zone_page [data-testid="stColumn"]{min-width:min(100%,240px)!important;}}
    .stApp .st-key-apri_information{margin-top:24px;}
    </style>''',unsafe_allow_html=True)


def informations():
    txt=TEXT.get(i18n.get_lang(),TEXT['en'])
    with st.container(key='apri_information'):
        with st.expander(txt[0]):
            st.write('Programme des Nations Unies pour l’environnement (PNUE)' if i18n.get_lang() == 'fr' else 'United Nations Environment Programme (UNEP)')
            for j in (1,3,5,7):
                st.markdown('**'+txt[j]+'**');st.write(txt[j+1])
            st.markdown(f'[Contact APRI](mailto:{COURRIEL})')
            st.write({
                'fr': 'Audience : les statistiques natives de Streamlit Community Cloud sont utilisées pour consulter la fréquentation. Elles sont distinctes de la télémétrie facultative désactivée dans l’application. Aucun traceur publicitaire supplémentaire n’a été ajouté.',
                'en': 'Audience: native Streamlit Community Cloud analytics are used to review visits. They are separate from optional application telemetry, which is disabled. No additional advertising tracker has been added.',
                'es': 'Audiencia: se utilizan las estadísticas nativas de Streamlit Community Cloud para consultar las visitas. Son distintas de la telemetría opcional desactivada en la aplicación. No se ha añadido ningún rastreador publicitario adicional.',
                'ht': 'Odyans: estatistik Streamlit Community Cloud yo sèvi pou gade kantite vizit. Yo diferan ak swivi opsyonèl aplikasyon an ki dezaktive. Pa gen lòt zouti swivi piblisite ki ajoute.',
            }.get(i18n.get_lang(), 'Native analytics: Streamlit Community Cloud.'))
            import compteur_visites
            if compteur_visites.configuration() is not None:
                st.write({
                    'fr': 'Le compteur public compte les sessions depuis son activation, pas les personnes uniques. Le serveur transmet une opération de comptage à CounterAPI, sans transmettre vos réponses, votre adresse IP ou votre identité. Aucun cookie ni script de ce service n’est ajouté à votre navigateur. Le total peut être retardé ou incomplet en cas de panne.',
                    'en': 'The public counter counts sessions since activation, not unique people. The server sends a count operation to CounterAPI without forwarding your answers, IP address or identity. No cookie or script from this service is added to your browser. The total may be delayed or incomplete during outages.',
                    'es': 'El contador público cuenta sesiones desde su activación, no personas únicas. El servidor envía una operación a CounterAPI sin transmitir sus respuestas, dirección IP o identidad. No se añade ninguna cookie ni script del servicio al navegador. El total puede retrasarse o quedar incompleto durante una interrupción.',
                    'ht': 'Kontè piblik la konte sesyon depi aktivasyon li, pa moun inik. Sèvè a voye yon operasyon kontaj bay CounterAPI san li pa voye repons ou, adrès IP ou oswa idantite ou. Pa gen bonbon ni script sèvis sa a ki ajoute nan navigatè ou. Total la ka anreta oswa enkonplè lè gen yon pann.',
                }.get(i18n.get_lang(), compteur_visites.LABELS['en'][3]))


ACCESS = {
 'fr': ('Base individuelle des ménages', 'Accès sur demande après validation. Indiquez votre organisme, l’objectif de votre étude et les données nécessaires. La demande ne vaut pas autorisation d’accès.', 'Demander un accès'),
 'en': ('Individual household dataset', 'Access on request after approval. Describe your organisation, study purpose and the data needed. Submitting a request does not grant access.', 'Request access'),
 'es': ('Base individual de hogares', 'Acceso previa solicitud y aprobación. Indique su organización, el objetivo del estudio y los datos necesarios. La solicitud no constituye una autorización de acceso.', 'Solicitar acceso'),
 'ht': ('Baz done endividyèl kay yo', 'Aksè sou demann apre apwobasyon. Bay òganizasyon ou, objektif etid la ak done ou bezwen yo. Voye yon demann pa bay otorizasyon aksè.', 'Mande aksè'),
}

def demande_donnees():
    title, description, button = ACCESS.get(i18n.get_lang(), ACCESS['en'])
    st.markdown('**' + title + '**')
    st.write(description)
    st.link_button(button, f'mailto:{COURRIEL}?subject=APRI%20-%20Data%20access%20request')
