# Aires protégées — provenance et contrôle

Récupération : 14 septembre 2026. Source géométrique : service officiel UNEP-WCMC, couche WDPA_poly_latest, édition août 2026 selon le copyright du service (ne pas confondre avec la date septembre 2026 de la page pays).

- Service : https://data-gis.unep-wcmc.org/server/rest/services/ProtectedSites/The_World_Database_of_Protected_Areas/FeatureServer/1
- Requête : /query?where=iso3%3D%27HTI%27&outFields=*&outSR=4326&f=geojson
- Citation : UNEP-WCMC et IUCN (2026), Protected Planet, WDPA, août 2026. https://doi.org/10.34892/6fwd-af11
- Référence nationale consultée : https://anap.gouv.ht/documents/Liste_des_APs.pdf (dates de désignation allant jusqu’en 2017 ; aucune date explicite de mise à jour du document).
- Conditions : https://www.protectedplanet.net/en/legal ; conserver l’attribution, ne pas présenter les données comme du domaine public.

## Contrôles

27 sites uniques pour Haïti ; tous portent le statut fournisseur State Verified et metadataid 1640. Ce statut est celui de la base, pas une nouvelle certification de notre part. Les géométries GeoJSON sont en WGS84, longitude/latitude, sans découpage au littoral (les espaces marins sont conservés). Les polygones multiples et leurs anneaux intérieurs restent intacts.

Validation Shapely : deux auto-intersections (Deux Mamelles 555643722, Fort Royal 555720401). make_valid a séparé les parties polygonales des artefacts linéaires de superficie nulle. Différence de superficie plane inférieure à 1e-10 degré carré, sans déplacement manuel du contour. Les 27 géométries résultantes sont valides et non vides. Le fichier original est conservé dans outputs/protected-areas/haiti-wdpca.geojson ; son empreinte SHA256 figure dans le GeoJSON intégré.

## Rapprochement ANAP

Voir protected_areas_audit.json : correspondances de noms et superficies, réserves et corrections techniques, site par site. Il ne s’agit pas d’une validation juridique des contours : le PDF fournit un inventaire, pas des polygones.

Écarts majeurs : Macaya (87,26 km² ANAP, 99,02 km² déclarés WDPA, 131,36 km² géométriques WDPA) ; Port Salut–Aquin ne peut pas être assimilé au seul Port-Salut ; Grande Colline figure dans l’ANAP mais pas comme site distinct parmi ces 27 polygones. Les désignations de 2021 ne peuvent pas être contrôlées à partir de cette ancienne liste. Aucun ancien contour ni découpage inventé n’a été réintroduit pour combler les différences.

## Intégration

carte_localisation._couches remplace systématiquement l’ancienne couche par protected_areas_wdpa.geojson ; en cas d’absence du nouveau fichier, la couche est vide, sans retour à l’ancien jeu rejeté. Les popups 2D/3D affichent source, édition, statut et réserves. La légende et les exports portent WDPA 08/2026. Les scores de résilience ne sont pas recalculés par cette correction cartographique.
