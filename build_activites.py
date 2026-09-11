#!/usr/bin/env python3
"""Écrit data/activites_leviers.json : des idées d'activité par levier.

CE SONT DES IDÉES, PAS UN PLAN. Le modèle causal dit sur quoi appuyer ; il ne
dit pas comment. Ces listes donnent la matière d'un atelier : quatre pistes
par levier, assez concrètes pour qu'on puisse les refuser, assez courtes pour
qu'on en discute. Elles vivent dans `data/`, hors du code, pour être relues et
corrigées par qui n'écrit pas de Python.
"""
import json
import os

A = {
"eau": (
 ["Réhabiliter les points d'eau cassés avant d'en créer de nouveaux, avec un réparateur formé et outillé par section",
  "Capter et protéger les sources de tête de bassin, avec périmètre de protection négocié avec les riverains",
  "Comité d'usagers par point d'eau, cotisation mensuelle et caisse d'entretien tenue localement",
  "Traitement à domicile, chlore ou filtre céramique, là où la source reste éloignée ou douteuse"],
 ["Repair broken water points before building new ones, with a trained, equipped local repairer in each section",
  "Capture and protect headwater springs, with a protection perimeter negotiated with neighbouring users",
  "A user committee per water point, a monthly contribution and a locally held maintenance fund",
  "Household treatment, chlorine or ceramic filter, where the source stays distant or doubtful"]),
"assain": (
 ["Assainissement piloté par la communauté, section par section, plutôt que distribution de latrines",
  "Dalles et fosses ventilées produites localement par des maçons formés, vendues à prix subventionné",
  "Traitement des boues de vidange, sans lequel les latrines déplacent le problème au lieu de le régler",
  "Blocs sanitaires séparés filles et garçons dans les écoles, avec eau et point de lavage des mains"],
 ["Community-led total sanitation, section by section, rather than latrine handouts",
  "Slabs and ventilated pits produced locally by trained masons and sold at a subsidised price",
  "Faecal sludge treatment, without which latrines move the problem instead of solving it",
  "Separate sanitation blocks for girls and boys in schools, with water and a handwashing point"]),
"elec": (
 ["Kits solaires domestiques en location-vente, avec service après-vente tenu par un technicien de la section",
  "Mini-réseau solaire pour les bourgs où la densité le justifie, avec tarif social et compteurs prépayés",
  "Éclairage solaire des écoles et des centres de santé en priorité, avant les usages domestiques",
  "Atelier local de réparation de batteries et d'onduleurs, pour que la panne ne soit pas la fin du service"]),
"cuisson": (
 ["Réchauds améliorés à deux niveaux de rendement, avec mesure de la consommation de combustible avant et après",
  "Filière de charbon écologique accompagnée : fours de carbonisation, séchage, contrôle de qualité",
  "Kits gaz de démarrage là où un point de distribution existe déjà à moins d'une heure",
  "Reconversion négociée des producteurs de charbon avant toute restriction, jamais après"],
 ["Improved stoves at two efficiency levels, with household fuel consumption metered before and after",
  "A supported eco-charcoal supply chain: carbonisation kilns, drying, quality control",
  "LPG starter kits where a distribution point already exists within an hour",
  "A negotiated conversion pathway for charcoal producers before any restriction, never after"]),
"sante_acces": (
 ["Cliniques mobiles mensuelles sur les sections les plus éloignées, avec calendrier affiché et tenu",
  "Agents de santé communautaires polyvalents, dotés et supervisés, dans chaque localité",
  "Transport d'urgence conventionné, moto-ambulance ou brancard motorisé, avec caisse de solidarité",
  "Stock tampon de médicaments essentiels au niveau de la section, pour éviter le déplacement inutile"]),
"ecole": (
 ["Salles de classe implantées selon la distance à pied réelle, pas selon le terrain disponible",
  "Classes satellites ou multigrades dans les localités isolées, avec enseignant logé sur place",
  "Transport scolaire collectif, à pied encadré ou à dos d'animal, sur les trajets les plus longs",
  "Cantine scolaire adossée à la production locale, qui rend le trajet quotidien payant pour la famille"]),
"abris": (
 ["Diagnostic technique des abris existants avant toute construction neuve, avec liste de réparations chiffrée",
  "Un gestionnaire d'abri formé et nommé par abri, avec exercice annuel d'ouverture",
  "Équipement minimal prépositionné : eau, latrines, éclairage, séparation des espaces",
  "Convention d'usage avec l'école ou l'église qui sert d'abri, signée avant la saison cyclonique"]),
"logement": (
 ["Formation des maçons locaux aux techniques para-cycloniques et para-sismiques, avec chantier école",
  "Kits de renforcement ciblés : ancrage de toiture, chaînage, contreventement, plutôt que reconstruction",
  "Subvention conditionnée à l'inspection d'un technicien, versée en deux fois",
  "Filière locale de matériaux, blocs et bois traité, pour que le coût du renforcement reste tenable"]),
"mobile": (
 ["Négociation avec les opérateurs d'un pylône mutualisé sur les sections non couvertes",
  "Répéteurs solaires communautaires sur les points hauts, entretenus par un comité",
  "Points de recharge solaire payants dans les bourgs, qui rendent le téléphone utilisable",
  "Numéros courts gratuits pour l'alerte et l'urgence, négociés avec les opérateurs"]),
"alerte": (
 ["Chaîne d'alerte à double canal, SMS et radio locale, doublée d'un relais humain par localité",
  "Cloches, sirènes manuelles ou mégaphones là où le réseau ne passe pas",
  "Message d'alerte rédigé en créole, court, testé auprès des habitants avant diffusion",
  "Exercice d'alerte annuel avant la saison cyclonique, avec mesure du délai réel de diffusion"]),
"comites": (
 ["Un comité de gestion des risques par section, recruté dans les organisations déjà debout",
  "Dotation minimale : brancard, cordes, lampes, trousse, registre, et un lieu pour les ranger",
  "Simulation annuelle d'évacuation avec les écoles et les centres de santé",
  "Convention avec la protection civile départementale, pour que le comité existe administrativement"]),
"prepa": (
 ["Plan familial de préparation, une page, élaboré en séance de quartier",
  "Cartographie participative des zones inondables et des chemins d'évacuation, affichée en public",
  "Stock familial de première nécessité constitué progressivement, avec liste et calendrier",
  "Formation aux premiers secours d'un référent par groupe de dix ménages"]),
"services": (
 ["Tableau de bord public des services de la commune, mis à jour et affiché à la mairie",
  "Boîte à doléances et réponse écrite obligatoire sous trente jours",
  "Budget participatif sur une part identifiée des investissements communaux",
  "Rencontre trimestrielle entre la mairie, les CASEC et les organisations de base"]),
"etat_civil": (
 ["Campagnes mobiles d'enregistrement des naissances dans les sections éloignées",
  "Gratuité et déclaration groupée à la maternité et au centre de santé",
  "Régularisation rétroactive des enfants non déclarés, par jugement supplétif accompagné",
  "Registre numérisé au niveau communal, pour que l'acte se retrouve sans se déplacer"]),
"foret": (
 ["Plantation liée à une alternative de cuisson et à un accord foncier signé avant le premier plant",
  "Régénération naturelle assistée, moins chère et plus robuste que la plantation sur les parcelles pentues",
  "Agroforesterie à revenus courts, café, cacao, fruitiers, pour que l'arbre paie avant d'être coupé",
  "Suivi de survie à deux ans, section par section, plutôt que comptage des plants mis en terre"]),
"pluie": (
 ["Impluviums et citernes familiales, pour découpler l'usage domestique de la pluie de l'année",
  "Retenues collinaires et seuils en pierre sèche qui gardent l'eau dans le bassin",
  "Calendrier cultural ajusté aux relevés de pluie de la station la plus proche",
  "Information saisonnière traduite et diffusée aux producteurs avant les semis"]),
"aridite": (
 ["Paillage et couverture permanente du sol, la mesure la moins chère contre l'évaporation",
  "Haies vives et brise-vent sur les parcelles exposées",
  "Irrigation d'appoint au goutte-à-goutte sur les cultures de rente à forte valeur",
  "Choix variétal tolérant au déficit hydrique, avec multiplication locale de semences"]),
"vegetation": (
 ["Mise en défens temporaire des parcelles les plus dégradées, avec compensation des usagers",
  "Reprise des ravines par fascines et plantations, de l'amont vers l'aval",
  "Contrôle de la divagation du bétail par convention locale plutôt que par interdiction",
  "Suivi NDVI de saison sèche par section, pour voir si la mesure prend"]),
"emploi": (
 ["Chantiers à haute intensité de main-d'œuvre sur les travaux de conservation des sols",
  "Apprentissage rémunéré chez les artisans de la commune, avec certification à la sortie",
  "Appui à la transformation locale, séchage, conditionnement, qui crée l'emploi sur place",
  "Travaux publics saisonniers calés sur la soudure, pas sur le calendrier administratif"]),
"revenu": (
 ["Diversification vers des cultures de rente à cycle court, avec débouché contractualisé avant plantation",
  "Groupements de commercialisation, pour sortir du prix bord champ imposé",
  "Transformation et stockage, qui déplacent la vente hors du pic de récolte",
  "Filets sociaux productifs ciblés sur les ménages sous le seuil, avec sortie programmée"]),
"reserve": (
 ["Groupes d'épargne et de crédit villageois, à cycle annuel et distribution visible",
  "Épargne mobile, pour que la réserve ne soit pas un stock visible et empruntable",
  "Assurance indicielle climatique testée sur une section pilote",
  "Grenier ou stock communautaire de soudure, géré par un comité et reconstitué chaque récolte"]),
"transferts": (
 ["Points de retrait dans les bourgs, pour supprimer le déplacement et son coût",
  "Réduction des frais par accord avec les opérateurs de transfert",
  "Information de la diaspora sur les besoins du territoire, via les organisations de base",
  "Orientation d'une part des transferts vers l'investissement productif, par produit dédié"]),
"compte": (
 ["Ouverture de compte mobile groupée, adossée à la campagne de carte d'identité",
  "Agents bancaires de proximité chez les commerçants, pour dépôt et retrait sans déplacement",
  "Éducation financière courte, deux séances, adossée aux groupes d'épargne existants",
  "Paiement des salaires de chantier sur compte mobile, qui crée l'usage en même temps que le compte"]),
"foncier": (
 ["Inventaire foncier participatif, parcelle par parcelle, validé en assemblée de section",
  "Reconnaissance des droits d'usage et du fermage par convention locale écrite",
  "Médiation foncière outillée, avec un médiateur formé par commune",
  "Sécurisation prioritaire des parcelles visées par un investissement, avant l'investissement"]),
"entraide": (
 ["Appui aux formes existantes d'entraide de travail, konbit et escouades, plutôt qu'aux structures nouvelles",
  "Caisses de solidarité de quartier, avec règle de sortie écrite",
  "Groupes de femmes autour de l'épargne, de la transformation et de la garde d'enfants",
  "Reconnaissance publique des pratiques d'entraide dans les projets, qui les rend visibles"]),
"passerelle": (
 ["Mise en réseau des organisations de sections voisines autour d'un enjeu commun",
  "Voyages d'échange entre producteurs, avec restitution obligatoire",
  "Plateforme communale réunissant organisations, mairie et services déconcentrés",
  "Représentation des sections isolées dans les instances où se décident les investissements"]),
"ocb": (
 ["Diagnostic organisationnel des OCB existantes, avant toute création nouvelle",
  "Appui à la gouvernance : statuts, assemblée annuelle, comptes tenus et présentés",
  "Subvention de fonctionnement modeste mais pluriannuelle, plutôt que financement par projet",
  "Accompagnement à l'enregistrement légal, qui conditionne l'accès aux financements"]),
"securite": (
 ["Médiation communautaire des conflits, en appui aux modes de règlement déjà pratiqués",
  "Éclairage des points de passage et des marchés",
  "Comités mixtes de sécurité au niveau de la section, avec les notables et les jeunes",
  "Suivi du sentiment de sécurité par enquête courte, pour mesurer plutôt que supposer"]),
"alimentaire": (
 ["Jardins de case et cultures maraîchères de contre-saison, ciblés sur les mois de soudure",
  "Cantines scolaires approvisionnées localement, qui retirent un repas de la charge du ménage",
  "Conservation et transformation après récolte, pour réduire les pertes",
  "Distribution ciblée pendant la soudure, avec critère de ciblage discuté publiquement"]),
"education": (
 ["Cours de rattrapage et classes passerelles pour les enfants déscolarisés",
  "Alphabétisation des adultes adossée aux groupes d'épargne et aux organisations",
  "Subvention des frais de scolarité versée à l'école, pas au ménage, contre présence constatée",
  "Suivi de l'achèvement du cycle plutôt que de l'inscription"]),
"identite": (
 ["Campagnes mobiles d'obtention de la carte d'identité, couplées à l'état civil",
  "Prise en charge des frais et du transport pour les ménages les plus pauvres",
  "Accompagnement juridique des cas sans acte de naissance",
  "Recensement des personnes sans pièce par les organisations de base, avant la campagne"]),
"sante": (
 ["Paquet de soins essentiels gratuit au niveau de la section, avec dotation garantie",
  "Prévention du paludisme et des maladies hydriques, moustiquaires et traitement de l'eau",
  "Suivi nutritionnel des enfants de moins de cinq ans par les agents communautaires",
  "Santé maternelle : consultations prénatales décentralisées et transport d'urgence"]),
"travail": (
 ["Réduction de la charge de la corvée d'eau, qui rend du temps de travail productif",
  "Équipement de traction et de transport partagé, loué par le groupement",
  "Prévention des accidents agricoles, équipement de protection et formation",
  "Prise en charge des maladies chroniques, premier motif d'arrêt de travail"]),
"temps_eau": (
 ["Rapprocher le point d'eau, la seule mesure qui rende des heures par jour et par ménage",
  "Citernes de toiture, qui suppriment le trajet une partie de l'année",
  "Pompes et transport d'eau motorisé mutualisés sur les trajets les plus longs",
  "Partage de la corvée dans le ménage, abordé dans les séances communautaires"]),
"prod_agri": (
 ["Semences de qualité multipliées localement, avec contrôle par les producteurs",
  "Fertilisation organique, compost et fumier, plutôt qu'intrants importés",
  "Appui-conseil de proximité par des paysans relais formés",
  "Accès à l'eau d'appoint sur les parcelles à plus fort potentiel"]),
"erosion": (
 ["Rampes vivantes, murs secs et fascines sur les parcelles en pente, chantiers collectifs",
  "Traitement des ravines de l'amont vers l'aval, jamais l'inverse",
  "Bandes enherbées et cultures en courbes de niveau",
  "Entretien annuel programmé et financé, sans lequel l'ouvrage ne passe pas trois saisons"]),
"pression_bois": (
 ["Alternative de cuisson d'abord : c'est la demande, pas l'offre, qui tient la coupe",
  "Bois-énergie de plantation dédiée, à croissance rapide, hors des massifs",
  "Meules améliorées, qui donnent plus de charbon par arbre coupé",
  "Convention locale d'usage du bois, négociée, avec contrepartie visible"]),
"abondance_bois": (
 ["Plantations à vocation énergétique séparées des plantations de protection",
  "Gestion de la régénération naturelle par rotation entre parcelles",
  "Inventaire de la ressource sur pied, pour que le prélèvement se discute sur des chiffres",
  "Valorisation des résidus agricoles en combustible, briquettes et balles compressées"]),
"agro_durable": (
 ["Compostage et fumure organique, avec démonstration sur parcelle de paysan",
  "Associations et rotations culturales, contre la monoculture sur brûlis",
  "Couverture permanente du sol et travail minimal",
  "Champs écoles paysans, une saison complète, plutôt que formations ponctuelles"]),
"fertilite": (
 ["Amendement organique systématique avant tout engrais minéral",
  "Légumineuses en rotation et en association, pour l'azote",
  "Analyse de sol simple par section, pour cibler l'amendement",
  "Arrêt du brûlis par alternative de préparation du sol, pas par interdiction seule"]),
"infiltration": (
 ["Seuils, banquettes et fossés d'infiltration en tête de bassin",
  "Reboisement des zones de recharge identifiées, en priorité sur les plantations de plaine",
  "Mares et retenues collinaires, qui stockent et rechargent",
  "Suppression des obstacles au lit des ravines, avec entretien programmé"]),
"biodiv": (
 ["Mise en défens de zones refuges, choisies avec les habitants et compensées",
  "Haies vives et corridors entre les fragments boisés",
  "Suivi participatif des oiseaux et des pollinisateurs, avec les écoles",
  "Encadrement du prélèvement des espèces sous pression, par convention locale"]),
"controle": (
 ["Agents forestiers dotés en moyens de déplacement, sans quoi le contrôle n'existe pas",
  "Convention locale de gestion, avec surveillance confiée aux organisations de base",
  "Traçabilité du charbon aux points de passage, plutôt que contrôle à la coupe",
  "Sanction graduée et négociée, adossée à une alternative offerte au producteur"]),
"sensib": (
 ["Émissions de radio locale en créole, régulières, animées par des habitants",
  "Clubs environnement dans les écoles, avec pépinière et suivi de plantation",
  "Restitution publique des résultats de l'enquête, section par section",
  "Visites de parcelles réussies chez un voisin, plus convaincantes qu'un atelier"]),
"ancrage": (
 ["Emploi local saisonnier, qui retient la main-d'œuvre jeune pendant la soudure",
  "Services de base dans les sections, pour que rester ne soit pas un renoncement",
  "Appui aux jeunes qui s'installent en agriculture, accès à la terre et à l'équipement",
  "Connexion des sections isolées, route et réseau, qui réduit le coût de rester"]),
"rentabilite_charbon": (
 ["Alternatives de revenu pour les producteurs, avant toute mesure de restriction",
  "Filière de charbon écologique mieux payée à la qualité, qui déplace l'effort vers le rendement",
  "Taxation à la sortie du territoire plutôt qu'à la coupe, plus simple à tenir",
  "Suivi du prix du charbon au marché, pour savoir si la mesure produit un effet"]),
"feux": (
 ["Alternatives de préparation du sol au brûlis, avec démonstration comparée",
  "Pare-feux et calendrier de brûlage négocié, là où le brûlis ne peut pas cesser d'un coup",
  "Brigades villageoises d'intervention, équipées du minimum",
  "Convention locale sur le feu, avec règle de responsabilité écrite"]),
"pression_demo": (
 ["Intensification sur les parcelles existantes plutôt qu'ouverture de nouvelles terres",
  "Accès à la terre pour les jeunes par fermage sécurisé, qui évite le défrichement",
  "Activités non agricoles en milieu rural, pour desserrer la demande de terre",
  "Planification de l'usage des sols à l'échelle de la section, discutée en assemblée"]),
}

EN = {
"elec": ["Home solar kits on lease-to-own, with after-sales service held by a technician in the section",
  "A solar mini-grid for the larger settlements, with a social tariff and prepaid meters",
  "Solar lighting for schools and health centres first, before domestic uses",
  "A local battery and inverter repair workshop, so a breakdown is not the end of the service"],
"sante_acces": ["Monthly mobile clinics in the most distant sections, with a posted schedule that is kept",
  "Multi-skilled community health workers, equipped and supervised, in every locality",
  "Contracted emergency transport, motorcycle ambulance or motorised stretcher, with a solidarity fund",
  "A buffer stock of essential medicines at section level, to avoid pointless travel"],
"ecole": ["Classrooms sited by actual walking distance, not by land availability",
  "Satellite or multigrade classes in isolated localities, with the teacher housed on site",
  "Collective school transport, supervised walking or animal transport, on the longest routes",
  "A school canteen supplied locally, which makes the daily walk worth it for the family"],
"abris": ["A technical survey of existing shelters before any new construction, with a costed repair list",
  "One trained, named shelter manager per shelter, with an annual opening drill",
  "Minimum equipment prepositioned: water, latrines, lighting, separated spaces",
  "A use agreement with the school or church that serves as shelter, signed before the cyclone season"],
"logement": ["Training local masons in cyclone- and earthquake-resistant technique, on a demonstration site",
  "Targeted strengthening kits: roof anchoring, ring beams, bracing, rather than reconstruction",
  "A subsidy conditional on a technician's inspection, paid in two instalments",
  "A local materials chain, blocks and treated timber, to keep strengthening affordable"],
"mobile": ["Negotiating a shared mast with the operators for the uncovered sections",
  "Community solar repeaters on high points, maintained by a committee",
  "Paid solar charging points in the larger settlements, which make the phone usable",
  "Free short numbers for warning and emergency, negotiated with the operators"],
"alerte": ["A two-channel warning chain, SMS and local radio, backed by a human relay in each locality",
  "Bells, hand sirens or megaphones where the network does not reach",
  "A warning message written in Creole, short, tested with residents before broadcast",
  "An annual drill before the cyclone season, measuring the real time to reach people"],
"comites": ["One disaster risk committee per section, recruited from the organisations already standing",
  "A minimum kit: stretcher, ropes, lamps, first aid, register, and somewhere to keep them",
  "An annual evacuation simulation with the schools and health centres",
  "An agreement with departmental civil protection, so the committee exists administratively"],
"prepa": ["A one-page family preparedness plan, drawn up in neighbourhood sessions",
  "Participatory mapping of flood-prone areas and evacuation routes, posted publicly",
  "A family emergency stock built up gradually, with a list and a schedule",
  "First-aid training for one focal point per ten households"],
"services": ["A public dashboard of municipal services, updated and posted at the town hall",
  "A complaints box with a written reply required within thirty days",
  "Participatory budgeting on an identified share of municipal investment",
  "A quarterly meeting between the town hall, the CASECs and the grassroots organisations"],
"etat_civil": ["Mobile birth registration campaigns in the distant sections",
  "Free, grouped declaration at the maternity ward and the health centre",
  "Retroactive registration of undeclared children, through supported court rulings",
  "A digitised register at communal level, so a certificate can be found without travelling"],
"foret": ["Planting tied to a cooking-fuel alternative and to a tenure agreement signed before the first seedling",
  "Assisted natural regeneration, cheaper and more robust than planting on steep plots",
  "Agroforestry with short-cycle returns, coffee, cocoa, fruit, so the tree pays before it is cut",
  "Two-year survival monitoring, section by section, rather than counting seedlings planted"],
"pluie": ["Rainwater harvesting and family cisterns, to decouple domestic use from the year's rainfall",
  "Hillside retention and dry-stone sills that keep water in the catchment",
  "A cropping calendar adjusted to the records of the nearest rain gauge",
  "Seasonal forecasts translated and delivered to producers before sowing"],
"aridite": ["Mulching and permanent soil cover, the cheapest measure against evaporation",
  "Live hedges and windbreaks on exposed plots",
  "Supplementary drip irrigation on high-value cash crops",
  "Drought-tolerant varieties, with local seed multiplication"],
"vegetation": ["Temporary set-aside of the most degraded plots, with users compensated",
  "Gully treatment by fascines and planting, working from upstream down",
  "Managing free-ranging livestock by local agreement rather than by ban",
  "Dry-season NDVI monitoring by section, to see whether the measure holds"],
"emploi": ["Labour-intensive works on soil conservation",
  "Paid apprenticeship with local artisans, with certification on completion",
  "Support to local processing, drying and packaging, which creates work on the spot",
  "Seasonal public works timed to the lean season, not to the administrative calendar"],
"revenu": ["Diversification into short-cycle cash crops, with an outlet contracted before planting",
  "Marketing groups, to escape the farm-gate price imposed by buyers",
  "Processing and storage, which move the sale away from the harvest peak",
  "Productive safety nets targeted on households below the threshold, with a planned exit"],
"reserve": ["Village savings and loan groups, on an annual cycle with a visible share-out",
  "Mobile savings, so the reserve is not a visible, borrowable stock",
  "Index-based climate insurance piloted in one section",
  "A community lean-season granary, managed by a committee and refilled each harvest"],
"transferts": ["Withdrawal points in the larger settlements, removing the journey and its cost",
  "Lower fees, negotiated with the transfer operators",
  "Informing the diaspora of territorial needs through the grassroots organisations",
  "Channelling part of remittances into productive investment through a dedicated product"],
"compte": ["Grouped mobile account opening, attached to the identity card campaign",
  "Banking agents at local shops, for deposit and withdrawal without travel",
  "Short financial education, two sessions, attached to existing savings groups",
  "Paying works wages into mobile accounts, which creates the use along with the account"],
"foncier": ["Participatory land inventory, plot by plot, validated in a section assembly",
  "Recognition of use rights and tenancy through a written local agreement",
  "Equipped land mediation, with one trained mediator per commune",
  "Securing first the plots an investment targets, before the investment"],
"entraide": ["Support to existing labour-sharing forms, konbit and work squads, rather than new structures",
  "Neighbourhood solidarity funds, with a written exit rule",
  "Women's groups around savings, processing and childcare",
  "Public recognition of mutual-aid practices in projects, which makes them visible"],
"passerelle": ["Networking the organisations of neighbouring sections around a shared issue",
  "Farmer exchange visits, with a mandatory report back",
  "A communal platform bringing together organisations, the town hall and deconcentrated services",
  "Representation of isolated sections where investment decisions are made"],
"ocb": ["An organisational assessment of existing CBOs before creating any new one",
  "Governance support: statutes, annual assembly, accounts kept and presented",
  "A modest but multi-year running grant, rather than project-by-project funding",
  "Support with legal registration, which conditions access to funding"],
"securite": ["Community mediation of disputes, building on the settlement practices already used",
  "Lighting of crossing points and markets",
  "Mixed security committees at section level, with elders and young people",
  "Tracking the sense of safety through a short survey, to measure rather than assume"],
"alimentaire": ["Home gardens and off-season vegetable growing, targeted on the lean months",
  "School canteens supplied locally, taking one meal off the household",
  "Post-harvest storage and processing, to cut losses",
  "Targeted lean-season distribution, with the targeting criterion discussed publicly"],
"education": ["Catch-up classes and bridging classes for out-of-school children",
  "Adult literacy attached to savings groups and organisations",
  "School fees paid to the school, not the household, against verified attendance",
  "Monitoring completion of the cycle rather than enrolment"],
"identite": ["Mobile identity card campaigns, coupled with civil registration",
  "Fees and transport covered for the poorest households",
  "Legal support for cases with no birth certificate",
  "Grassroots organisations listing people without papers, ahead of the campaign"],
"sante": ["A free essential care package at section level, with a guaranteed supply",
  "Malaria and waterborne disease prevention, nets and water treatment",
  "Nutritional follow-up of under-fives by community health workers",
  "Maternal health: decentralised antenatal consultations and emergency transport"],
"travail": ["Cutting the water-collection burden, which returns productive hours",
  "Shared draught and transport equipment, rented out by the group",
  "Farm accident prevention, protective equipment and training",
  "Management of chronic illness, the leading reason for stopping work"],
"temps_eau": ["Bringing the water point closer, the only measure that returns hours per household per day",
  "Roof cisterns, which remove the journey for part of the year",
  "Shared pumps and motorised water transport on the longest routes",
  "Sharing the water chore within the household, addressed in community sessions"],
"prod_agri": ["Quality seed multiplied locally, with producer-led control",
  "Organic fertilisation, compost and manure, rather than imported inputs",
  "Local advisory support by trained farmer relays",
  "Access to supplementary water on the highest-potential plots"],
"erosion": ["Live barriers, dry walls and fascines on sloping plots, as collective works",
  "Gully treatment from upstream down, never the reverse",
  "Grass strips and contour cropping",
  "Scheduled and funded annual maintenance, without which the structure does not last three seasons"],
"pression_bois": ["The cooking alternative first: it is demand, not supply, that drives cutting",
  "Fuelwood from dedicated fast-growing plantations, away from the remaining stands",
  "Improved kilns, which yield more charcoal per tree cut",
  "A negotiated local agreement on wood use, with a visible counterpart"],
"abondance_bois": ["Energy plantations kept separate from protection plantations",
  "Managing natural regeneration by rotation between plots",
  "An inventory of the standing resource, so offtake is discussed against figures",
  "Turning crop residues into fuel, briquettes and compressed husks"],
"agro_durable": ["Composting and organic manuring, demonstrated on a farmer's own plot",
  "Intercropping and rotation, against slash-and-burn monocropping",
  "Permanent soil cover and minimum tillage",
  "Farmer field schools over a full season, rather than one-off training"],
"fertilite": ["Organic amendment systematically before any mineral fertiliser",
  "Legumes in rotation and intercropping, for nitrogen",
  "Simple soil analysis per section, to target the amendment",
  "Ending burning through an alternative way to prepare the soil, not by prohibition alone"],
"infiltration": ["Sills, bunds and infiltration ditches in the headwaters",
  "Replanting the identified recharge zones, ahead of lowland plantations",
  "Ponds and hillside reservoirs, which store and recharge",
  "Clearing obstructions from gully beds, with scheduled maintenance"],
"biodiv": ["Refuge areas set aside, chosen with residents and compensated",
  "Live hedges and corridors between the remaining wooded fragments",
  "Participatory bird and pollinator monitoring, with the schools",
  "Regulating the harvest of species under pressure, through local agreement"],
"controle": ["Forest officers given the means to move, without which enforcement does not exist",
  "A local management agreement, with surveillance entrusted to grassroots organisations",
  "Charcoal traceability at transit points, rather than control at the point of cutting",
  "Graduated, negotiated sanctions, backed by an alternative offered to the producer"],
"sensib": ["Regular local radio programmes in Creole, hosted by residents",
  "Environment clubs in schools, with a nursery and planting follow-up",
  "Public restitution of the survey results, section by section",
  "Visits to a neighbour's successful plot, more convincing than a workshop"],
"ancrage": ["Seasonal local employment, which holds young labour through the lean season",
  "Basic services in the sections, so that staying is not a sacrifice",
  "Support to young people settling in farming, access to land and equipment",
  "Connecting isolated sections, road and network, which lowers the cost of staying"],
"rentabilite_charbon": ["Income alternatives for producers, before any restrictive measure",
  "An eco-charcoal chain better paid for quality, which shifts effort towards yield",
  "Taxation on leaving the territory rather than at the point of cutting, easier to enforce",
  "Tracking the charcoal price at market, to know whether the measure is working"],
"feux": ["Alternatives to burning for soil preparation, with a side-by-side demonstration",
  "Firebreaks and a negotiated burning calendar, where burning cannot stop at once",
  "Village response brigades, with minimum equipment",
  "A local fire agreement, with a written rule of responsibility"],
"pression_demo": ["Intensifying on existing plots rather than opening new land",
  "Access to land for young people through secured tenancy, which avoids clearing",
  "Non-farm activities in rural areas, to ease the demand for land",
  "Land-use planning at section level, discussed in assembly"],
}

out = {}
for k, v in A.items():
    # UNE ENTRÉE PEUT ÊTRE ÉCRITE DE DEUX FAÇONS : un couple (français,
    # anglais) quand les deux tiennent côte à côte, ou la seule liste
    # française quand l'anglais est plus loin, dans EN. Distinguer les deux
    # sur le type évite de recopier la moitié du fichier.
    if isinstance(v, tuple):
        fr, en = v[0], (v[1] if len(v) > 1 else EN.get(k))
    else:
        fr, en = v, EN.get(k)
    if en is None:
        raise SystemExit("pas de version anglaise pour " + k)
    if len(fr) != len(en):
        raise SystemExit("longueurs différentes pour " + k)
    out[k] = {"fr": fr, "en": en}

manquants = [k for k in EN if k not in out]
if manquants:
    raise SystemExit("clés anglaises orphelines : " + ", ".join(manquants))

graphe = json.load(open(os.path.join("data", "graphe_causal.json"),
                        encoding="utf-8"))
connus = {n["id"] for n in graphe["noeuds"]}
absents = sorted(connus - set(out))
sup = sorted(set(out) - connus)
print("leviers couverts :", len(out), "/", len(connus))
if absents:
    raise SystemExit("leviers sans activités : " + ", ".join(absents))
if sup:
    raise SystemExit("activités sans levier : " + ", ".join(sup))

chemin = os.path.join("data", "activites_leviers.json")
with open(chemin, "w", encoding="utf-8") as f:
    json.dump({"activites": out}, f, ensure_ascii=False, indent=1)
print("écrit", chemin, os.path.getsize(chemin), "octets")
