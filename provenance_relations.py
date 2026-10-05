"""Explicit evidence provenance, independent of simulation strength."""
from urllib.parse import urlparse

TEXT = {
 'fr': dict(documented='Source publiée citée', theory='Hypothèse théorique', calculated='Association calculée', absent='Association non calculable', strength='Force choisie (hypothèse)', source='Source', detail='Ce que rapporte la source', limits='Limites / réserves', select='Examiner un lien', intro='Les flèches représentent des mécanismes supposés. Une source citée ne valide pas la force numérique. Toutes les forces de cette simulation sont choisies dans un barème, puis atténuées pour stabiliser le calcul ; elles ne sont pas estimées sur notre enquête.', caution='La corrélation décrit une association entre sections, pas un effet causal. Elle ne commande pas la simulation. Des périodes et des niveaux de mesure différents peuvent limiter la comparaison.', chosen='La valeur ci-dessus est un paramètre du modèle, pas le coefficient mesuré dans la publication.', legend='D : source citée · H : hypothèse · Sélectionnez un lien pour voir sa source et sa force.', no_source='Aucune source publiée renseignée pour ce lien.'),
 'en': dict(documented='Published source cited', theory='Theoretical hypothesis', calculated='Calculated association', absent='Association unavailable', strength='Chosen strength (hypothesis)', source='Source', detail='What the source reports', limits='Limitations / reservations', select='Inspect a link', intro='Arrows represent assumed mechanisms. A cited source does not validate the numerical strength. All simulation strengths are chosen from a scale and then damped to stabilize the calculation; they are not estimated from our survey.', caution='Correlation describes an association between sections, not a causal effect. It does not drive the simulation. Different periods and measurement levels may limit comparison.', chosen='The value above is a model parameter, not the coefficient measured in the publication.', legend='D: source cited · H: hypothesis · Select a link to inspect its source and strength.', no_source='No published source recorded for this link.'),
 'es': dict(documented='Fuente publicada citada', theory='Hipótesis teórica', calculated='Asociación calculada', absent='Asociación no calculable', strength='Fuerza elegida (hipótesis)', source='Fuente', detail='Qué indica la fuente', limits='Límites / reservas', select='Examinar un vínculo', intro='Las flechas representan mecanismos supuestos. Una fuente citada no valida la fuerza numérica. Todas las fuerzas se eligen en una escala y se atenúan para estabilizar el cálculo; no se estiman con nuestra encuesta.', caution='La correlación describe una asociación entre secciones, no un efecto causal. No determina la simulación. Las diferencias de períodos y escalas pueden limitar la comparación.', chosen='Este valor es un parámetro del modelo, no el coeficiente medido en la publicación.', legend='D: fuente citada · H: hipótesis · Seleccione un vínculo para ver la fuente y la fuerza.', no_source='No hay fuente publicada registrada para este vínculo.'),
 'ht': dict(documented='Sous piblikasyon site', theory='Ipotèz teyorik', calculated='Asosyasyon kalkile', absent='Asosyasyon pa ka kalkile', strength='Fòs chwazi (ipotèz)', source='Sous', detail='Sa sous la rapòte', limits='Limit / rezèv', select='Egzamine yon lyen', intro='Flèch yo reprezante mekanis nou sipoze. Yon sous site pa valide fòs nimerik la. Tout fòs yo chwazi nan yon echèl epi diminye pou estabilize kalkil la; yo pa estime apati ankèt nou an.', caution='Korelasyon an dekri yon asosyasyon ant seksyon yo, pa yon efè kozatif. Li pa dirije similasyon an. Diferans nan peryòd ak nivo mezi ka limite konparezon an.', chosen='Valè sa a se yon paramèt modèl la, se pa koyefisyan piblikasyon an mezire.', legend='D: sous site · H: ipotèz · Chwazi yon lyen pou wè sous li ak fòs li.', no_source='Pa gen sous piblikasyon anrejistre pou lyen sa a.')
}

def labels(lang):
    return TEXT.get(lang, TEXT['en'])

def describe(edge, lang='en', association=None):
    t=labels(lang); src=edge.get('src') or {}; url=src.get('url') or ''
    if urlparse(url).scheme not in ('http','https'): url=''
    # A citation is evidence provenance, never proof of an estimated strength.
    published=bool(url)
    def local(key):
        return edge.get(key+'_'+lang) or edge.get(key+'_en') or edge.get(key+'_fr') or ''
    return dict(origin=t['documented'] if published else t['theory'], code='D' if published else 'H',
                strength_label=t['strength'], strength=edge.get('force'),
                association=association, association_label=t['calculated'] if association else t['absent'],
                citation=local('cite') or src.get('titre') or t['no_source'], url=url,
                finding=src.get('effet') if lang=='fr' else local('ref'),
                limits=local('reserve'), geography=src.get('geo') if lang=='fr' else src.get('geo_en') or src.get('geo'),
                caution=t['caution'], chosen=t['chosen'])
