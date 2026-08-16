# Ce qui manque au cadre IRLA, et par quoi continuer

## D'abord le constat, en une ligne

L'indice couvre aujourd'hui **45 % du poids total du cadre** — 136,7 points de
pondération sur 301,1, soit 58 indicateurs calculés sur 128.

Mais la couverture est très inégale, et c'est là qu'est le vrai problème.

| Dimension | Indicateurs | Poids couvert | Couverture |
|---|---:|---:|---:|
| II · Institutionnelle, technologique, gouvernance | 16 / 17 | 37,4 / 40,3 | **93 %** |
| I · Physique et infrastructurelle | 10 / 16 | 29,9 / 47,8 | 63 % |
| IV · Économique, moyens d'existence, sécurité alimentaire | 11 / 17 | 22,0 / 34,6 | 63 % |
| V · Sociale et communautaire | 9 / 16 | 18,7 / 34,7 | 54 % |
| VI · Humaine | 4 / 15 | 9,8 / 31,7 | 31 % |
| III · Environnementale et écologique | 8 / 38 | 18,8 / 90,0 | 21 % |
| **VII · Culturelle, identitaire, psychologique** | **0 / 9** | **0 / 22,0** | **0 %** |

**Une dimension entière de tes sept est absente de l'indice.** Ce n'est pas la
température qui manque le plus — c'est la dimension VII, et elle est déjà
presque à portée.

---

## Le classement par ce que ça coûte

| Bloc | Ind. | Poids | Couverture atteinte |
|---|---:|---:|---:|
| **A · Enquête déjà cartographiée** — aucune donnée nouvelle | 13 | 31,1 | 45 % → **56 %** |
| **B · Sentinel-2, mêmes images, deux bandes de plus** | 4 | 9,6 | → 59 % |
| **C · MODIS — température et santé de la végétation** | 3 | 7,2 | → 61 % |
| **D · Aires protégées et mangroves** — simple intersection | 3 | 6,4 | → 63 % |
| **E · Érosion modélisée (RUSLE)** | 2 | 6,8 | → 66 % |
| F · Connectivité et fragmentation du paysage | 7 | 15,3 | → 71 % |
| G · Inventaires écologiques de terrain | 6 | 14,6 | → 76 % |
| H · Registres administratifs (santé, PEV, police, BRH) | 13 | 26,3 | → 84 % |

---

## A · Le plus rentable, et de loin : 13 indicateurs sans une donnée nouvelle

Neuf des treize sont **toute la dimension VII**. La correspondance avec une
question de l'enquête a déjà été établie pour chacun — elle est écrite dans la
note de l'indicateur. Il ne manque que le calcul.

| Ligne | Indicateur | Question de l'enquête utilisée |
|---|---|---|
| 118 | Conscience environnementale | recyclage / réutilisation des déchets |
| 119 | Confiance en l'avenir | intention de voter aux prochaines élections |
| 120 | Appartenance et identité communautaires | participation à une réunion communautaire |
| 121 | Savoirs et pratiques traditionnels | maintien traditionnel de la fertilité des sols |
| 122 | Adaptation plutôt que résignation | prise en compte effective de l'alerte reçue |
| 123 | Cohésion, entraide et collaboration | participation à une corvée agricole |
| 124 | Conscience des droits et participation civique | participation à une action civique |
| 125 | Accueil et intégration des déplacés | les nouveaux arrivants ne sont pas vus comme un danger |
| 126 | Ancrage spirituel et croyances | fréquence de participation à un groupe d'église |

Plus quatre autres, hors dimension VII :

| Ligne | Indicateur | État |
|---|---|---|
| 17 | Collecte et gestion des déchets solides (ODD 11.6.1) | **correspondance exacte** |
| 99 | Isolement psychosocial | **correspondance exacte** |
| 100 | Maternité adolescente | bornes d'âge légèrement discordantes |
| 53 | Indice de diversité des cultures (CDI) | calculable, mais c'est un indice de Simpson et non un pourcentage — le barème demande une conversion |

### La décision que ça t'impose, et je ne vais pas la prendre à ta place

**Les 17 et 99 sont des correspondances exactes** : rien ne s'oppose à les
calculer, je peux le faire tout de suite.

**Les neuf de la dimension VII sont des proxys à une seule composante.** Ton
cadre définit par exemple « appartenance et identité communautaires » sur huit
composantes — rituels, règles coutumières, transmission de l'histoire locale.
L'enquête n'en couvre qu'une : la participation à une réunion. Même chose pour
les savoirs traditionnels, où plantes médicinales, conservation des aliments et
savoirs de navigation manquent.

C'est pour ça qu'ils n'ont pas été calculés. Deux options :

- **Les scorer en proxy**, en marquant chaque ligne « approximation à une
  composante » et en affichant lesquelles manquent. L'indice gagne une
  dimension entière et 22 points de poids ; il gagne aussi une fragilité
  documentée.
- **Ne pas les scorer**, et les afficher comme grandeurs descriptives, comme on
  vient de le faire pour le NDWI et le NDTI. La dimension VII reste à zéro dans
  le score mais visible dans le tableau de bord.

Mon avis : **les scorer**, parce qu'une dimension à zéro pèse plus lourd sur la
validité du composite qu'une dimension approximée et signalée. Un indice qui
ignore le culturel dit implicitement qu'il vaut zéro. Mais c'est ton cadre, et
ce choix se défend dans les deux sens.

Une troisième voie existe : **ajouter les questions manquantes à la prochaine
vague d'enquête**. Je peux te préparer le lot de questions à ajouter, calé sur
les composantes que ton article définit — une quinzaine de questions
fermeraient proprement la dimension VII.

---

## B · Quatre indicateurs de plus sans relancer d'imagerie

L37 EVI, L38 SAVI, L39 VARI, L40 FVC se calculent **sur les images Sentinel-2
déjà exportées**. Il suffit d'ajouter la bande bleue (B2) au script existant :

- **EVI** corrige l'effet de l'atmosphère et de l'arrière-plan du sol, et ne
  sature pas comme le NDVI au-delà de 0,8 — utile ici, où Mouline et Trichet
  frôlent la saturation ;
- **SAVI** corrige l'effet du sol nu, ce qui compte sur un territoire à couvert
  ouvert ;
- **VARI** n'utilise que le visible ;
- **FVC** se dérive du NDVI, c'est la fraction de sol effectivement couverte.

Le même export, une bande de plus. C'est le meilleur rapport travail / résultat
après le bloc A.

---

## C · Ta question : les températures — oui, et c'est du solide

**MODIS débloque trois indicateurs d'un seul script**, et surtout avec
**25 ans de profondeur** (2000-2025), là où Sentinel-2 n'en offre que sept.

| Ligne | Indicateur | Source |
|---|---|---|
| 41 | Anomalie saisonnière de température de surface (LST) | MOD11A2, 1 km, 8 jours |
| 42 | Indice de condition thermique (TCI) | même série |
| 36 | Indice de santé de la végétation (VHI) | TCI + VCI dérivé de MOD13Q1 |

Le VHI est le plus intéressant des trois : c'est la moitié thermique combinée à
la moitié végétation, et **il se calcule sur 25 ans**. Il donnerait au volet
végétation la profondeur historique qui manque au NDVI Sentinel — dont je t'ai
signalé que la référence tenait sur trois saisons seulement.

La résolution est de 1 km pour le thermique. Sur des sections de 14 à 60 km²,
c'est grossier mais utilisable — comparable à CHIRPS, et la même réserve
s'appliquera : bon pour comparer des années, moins pour comparer deux sections
voisines.

**C'est le prochain script que je te recommande**, après le bloc A.

---

## D · Ta seconde question : l'évapotranspiration

**Elle n'est pas un indicateur de ton cadre.** J'ai vérifié les 128 lignes :
aucune ne porte sur l'ET, l'ETP ou le bilan hydrique. La calculer n'ajouterait
donc rien au score.

Cela dit, elle vaudrait le détour pour deux raisons, et à titre **descriptif**,
comme les séquences sèches :

**Elle donnerait le vrai indice d'aridité.** Ta ligne 44 s'appelle « indice
d'aridité anormale », mais son barème porte sur l'écart de pluie à la normale —
c'est une anomalie pluviométrique, pas une aridité au sens de l'UNEP, qui est le
rapport précipitations / évapotranspiration potentielle. Avec MOD16A2 (ET et
ETP, 500 m, 8 jours, 2001→), on obtiendrait le P/ETP réel. Il ne remplacerait
pas la ligne 44 — le barème est ce qu'il est — mais il dirait si le Grand Sud
est en train de basculer de sub-humide vers semi-aride, ce que la pluie seule ne
dit pas.

**Elle boucle le bilan hydrique.** Tu sais maintenant que la campagne de
printemps reçoit 83 % de sa normale. L'ETP dirait combien de cette pluie repart
dans l'atmosphère avant d'atteindre la racine. Deux campagnes à 200 mm ne se
valent pas si l'une évapore 150 mm et l'autre 100.

Mon conseil : **après MODIS thermique**, dans le même script — MOD11 et MOD16
sont deux collections du même capteur, et un seul export peut porter les deux.

---

## E · L'érosion, le chaînon qui manque à ton récit

Le tableau de bord raconte déjà : le couvert recule de 12,8 %, les pluies à
50 mm augmentent dans les dix sections, 76 % des ménages ne sont pas sûrs de
garder leur parcelle donc n'aménagent pas la pente. **Il manque la conséquence.**

La ligne 59 (érosion et perte de sols, t/ha/an) se modélise par RUSLE, et tous
les ingrédients sont déjà disponibles :

| Facteur | Source | État |
|---|---|---|
| R — érosivité des pluies | CHIRPS journalier | **déjà exporté** |
| K — érodibilité du sol | SoilGrids 250 m | dans Earth Engine |
| LS — pente et longueur de versant | NASADEM 30 m | dans Earth Engine |
| C — couvert végétal | NDVI Sentinel-2 | **déjà exporté** |
| P — pratiques antiérosives | enquête ménage | à caler |

C'est le seul bloc qui transforme trois constats séparés en une chaîne causale
chiffrée. Il demande une vraie journée de travail, pas un script de dix lignes,
mais c'est celui qui donnerait le plus de force au rapport.

La ligne 60 (terres dégradées, ODD 15.3.1) suit la même logique via
Trends.Earth — occupation du sol, productivité primaire, carbone organique.

---

## F, G, H · Ce qui demande plus

**Connectivité et fragmentation** (7 indicateurs, lignes 64 à 70) : il faut
d'abord une carte d'occupation du sol du territoire. ESA WorldCover à 10 m
existe et couvre Haïti ; ensuite l'analyse en graphe demande un outil dédié
(Conefor, GUIDOS). Faisable, mais c'est un projet en soi.

**Inventaires écologiques** (6 indicateurs, lignes 47 à 52 — richesse
spécifique, Shannon, Simpson, diversité fonctionnelle) : **il n'y a pas de
raccourci satellitaire.** GBIF existe pour Haïti mais ses occurrences reflètent
l'effort d'observation, pas la biodiversité réelle — les scorer là-dessus
produirait un classement des endroits où des naturalistes sont passés. Ces six
indicateurs demandent des transects de terrain. À intégrer au protocole de la
prochaine mission, pas à bricoler.

**Registres administratifs** (13 indicateurs, dimension VI surtout) : mortalité
néonatale et maternelle, densité de médecins, couverture vaccinale. Rien de tout
cela ne se déduit de l'enquête ménage. Ce sont des demandes à faire au MSPP, au
PEV et à l'IHSI. **Tu as déjà quatre formulaires institutionnels en attente
d'attribution de section communale** — le district scolaire et le ministère de
la santé pourraient en porter une partie. C'est la première chose à débloquer
côté terrain.

---

## Ce que je te propose comme ordre

1. **Les lignes 17 et 99** — correspondances exactes, je les calcule tout de
   suite si tu me dis oui.
2. **La dimension VII en proxy** — dès que tu as tranché.
3. **EVI, SAVI, VARI, FVC** — une bande de plus au script Sentinel existant.
4. **MODIS thermique + évapotranspiration** — un script, 3 indicateurs scorés et
   le vrai indice d'aridité en prime, sur 25 ans.
5. **Aires protégées et mangroves** — une intersection WDPA, rapide.
6. **RUSLE** — le morceau de force.

Les blocs F, G et H ne se règlent pas depuis un bureau : ils demandent
respectivement un projet cartographique, une mission de terrain, et des
démarches administratives.
