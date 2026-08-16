# Mise à jour — neuf indicateurs environnementaux de plus

## Les 8 fichiers à mettre sur GitHub **dans le même commit**

| Fichier | Où | État |
|---|---|---|
| `app.py` | racine | remplacé |
| `i18n.py` | racine | remplacé |
| `environnement_page.py` | racine | remplacé |
| `data/resultats.json` | `data/` | remplacé |
| `data/ventilation.json` | `data/` | remplacé |
| `data/indices_vegetation.json` | `data/` | remplacé |
| `data/thermique.json` | `data/` | **nouveau** |
| `data/aires_protegees.json` | `data/` | **nouveau** |

`i18n.py` passe en version **`2026-08-16-modis`**.

---

## Le bilan

**66 indicateurs scorés sur 128.** La dimension environnementale passe de
**21 % à 44 %** de son poids couvert ; l'ensemble du cadre de 45 % à **52 %**.

| Ligne | Indicateur | Scores obtenus |
|---|---|---|
| 37 | EVI — végétation améliorée | 4 à 7 |
| 38 | SAVI — ajusté au sol | 5 à 9 |
| 39 | VARI — résistant à l'atmosphère | **0 à 8** |
| 40 | FVC — fraction de couverture | 4 à 6 |
| 36 | VHI — santé de la végétation | 5 à 8 |
| 41 | LST — anomalie de température | 8 à 10 |
| 42 | TCI — condition thermique | 5 à 7 |
| 55 | AP marines et côtières | 0 partout |
| 56 | AP terrestres | 0 partout |
| 57 | Mangrove | non scoré |

**Tous discriminent.** C'était le but : les quatre indices de végétation se
notent sur leur **niveau** et non sur une variation, contrairement au NDVI et au
NDMI qui donnaient 9 ou 10 partout. Le VARI étale les dix sections sur neuf de
ses dix tranches — aucun autre indicateur du tableau de bord ne sépare aussi
nettement ces territoires.

Le score d'ensemble ne bouge presque pas — **4,57 → 4,61** — parce que les
gains de la végétation compensent les zéros des aires protégées. Mais la
dispersion entre sections, elle, augmente nettement.

---

## 1 · Quentin est le point faible, et ce n'est plus une impression

| | EVI | SAVI | VARI | FVC | VHI |
|---|---:|---:|---:|---:|---:|
| **Quentin** | **4** | **5** | **0** | **4** | 6 |
| Mouline | 7 | 9 | 7 | 6 | 5 |
| Trichet | 6 | 8 | 8 | 6 | 7 |

Quentin est dernier ou avant-dernier sur les quatre indices de végétation.
C'est la même section qui reculait déjà sur le NDVI et le NDMI, la seule des
dix, et celle dont la séquence sèche de printemps s'est le plus allongée — de
22 à 27 jours consécutifs sans pluie.

**Quatre mesures indépendantes, un seul territoire désigné.** Si une
intervention doit être priorisée quelque part, la donnée dit où.

---

## 2 · La température a baissé, et l'explication n'est pas climatique

La surface s'est **refroidie** en saison sèche dans neuf sections sur dix, de
1,5 % à 4,5 %. Contre-intuitif — et il faut le dire avant que quelqu'un d'autre
ne le lise de travers.

L'explication probable est biologique, pas climatique : **une surface plus verte
évapore davantage et chauffe moins**. Les indices de végétation montrent
précisément un reverdissement sur la même période. La température de surface
suit le couvert ; ce n'est pas un thermomètre du climat, et cet indicateur ne
doit pas être présenté comme une mesure du réchauffement — il y faudrait la
température de l'air, pas celle de la peau du sol.

Mouline fait exception : c'est la seule section qui se réchauffe (+0,57 %), et
c'est aussi la plus humide et la plus froide en absolu.

**Un avertissement sur le barème de la 41.** Il gradue l'anomalie **en
pourcentage**, ce qui n'a de sens qu'une fois l'unité fixée : +15 % valent
+4,3 °C en Celsius et +45 K en Kelvin. J'ai calculé en Celsius, seule lecture
qui rende les tranches plausibles. C'est écrit dans la note de l'indicateur.

---

## 3 · L'indice d'aridité — et une section semi-aride

Hors cadre IRLA, donc non scoré, mais c'est peut-être le chiffre le plus
parlant de la livraison. Le vrai indice d'aridité au sens de l'UNEP, P/ETP :

| Section | P/ETP | Classe |
|---|---:|---|
| Mouline | 1,03 | humide |
| Anse à Drick, Barbois | 0,65 | subhumide sec |
| Trichet | 0,60 | subhumide sec |
| Quentin, Dalmette | 0,54 | subhumide sec |
| Blactote | 0,53 | subhumide sec |
| Beaulieu | 0,51 | subhumide sec |
| Débouchette | 0,50 | subhumide sec |
| **Dumont** | **0,46** | **semi-aride** |

**Dumont est déjà semi-aride**, et six sections sont à moins de 0,05 de le
devenir. C'est ce que la pluie seule ne pouvait pas dire : Débouchette reçoit
1 005 mm par an, ce qui paraît confortable, mais son évapotranspiration
potentielle en réclame 1 897. Le déficit n'est pas dans le ciel, il est dans le
bilan.

Réserve : MOD16 ne couvre que les dernières années de la série dans le
catalogue Earth Engine. Ce chiffre décrit l'état actuel, pas une tendance.

---

## 4 · Aucune aire protégée. Nulle part.

Aucune aire de la base WDPA — celle du PNUE-WCMC, référence officielle des ODD
14.5 et 15.1 — ne touche aucune des dix sections. Les lignes 55 et 56 reçoivent
donc **0 pour les dix**.

Un score plat invite d'ordinaire à renoncer à l'indicateur, comme on l'a fait
pour les eaux de surface. **Ici c'est l'inverse** : le zéro n'est pas une
incertitude de mesure, c'est un fait, et c'est précisément ce que le cadre
demande de mesurer. Dix territoires sans aucune protection formelle, sur une
côte en érosion — cela se score.

### La mangrove résout une énigme

Trois sections portent de la mangrove : **Dalmette 126 ha**, Trichet 55 ha,
Blactote 2 ha.

Dalmette est aussi la seule section dont la surface en eau détectée variait d'un
facteur vingt d'une année sur l'autre — l'anomalie qui m'avait fait renoncer à
scorer la ligne 35. Les deux faits se tiennent : **une mangrove est un milieu
intertidal**, sa signature dans le NDWI suit la marée et la saison. L'anomalie
n'était pas un défaut du capteur, c'était un estran.

La ligne 57 reste non scorée : son barème demande un pourcentage, donc deux
dates, et la couche officielle ne donne que l'année 2000. Global Mangrove Watch
(1996-2020) permettrait de la scorer — dis-moi si tu veux que je la cherche.

---

## 5 · L'onglet est réorganisé

Onze indicateurs feraient onze onglets, illisibles sur une rangée. Ils sont
donc groupés par milieu, et le **nom de l'indicateur devient une pastille** à
l'intérieur du groupe :

**Couverture forestière · Déforestation · Végétation · Eau · Température ·
Aires protégées · Précipitations · Sécheresse · Fiche par section · Lacunes**

- **Végétation** : NDVI · NDMI · EVI · SAVI · VARI · FVC
- **Eau** : NDWI · NDTI
- **Température** : VHI · LST · TCI

Chaque indicateur garde ses trois encarts — ce qu'il mesure, comment le lire
ici, ce dont il faut se méfier — et l'affichage distingue maintenant les deux
modes de notation : un indicateur noté sur une **variation** met en avant
l'écart entre deux périodes, un indicateur noté sur un **niveau** met en avant
sa valeur actuelle et le score qu'elle obtient. Afficher une variation pour le
second induirait en erreur, ce n'est pas ce que lit le barème.

---

## Ce qui reste dans l'environnemental

**21 indicateurs** non calculés au lieu de 30. Ce qui subsiste :

- **7 lignes de connectivité et fragmentation** (64 à 70) — demandent une carte
  d'occupation du sol et une analyse en graphe. Un projet en soi.
- **6 lignes de biodiversité** (47 à 52) — aucun raccourci satellitaire, il
  faut des transects de terrain.
- **RUSLE, érosion et terres dégradées** (59, 60) — modélisable, tous les
  ingrédients sont là, une vraie journée de travail.
- **35, 57, 63** — renoncées ou en attente d'une seconde date.
- **Chlorophylle-a, herbiers marins** (61, 58) — même problème de pixels d'eau
  que le NDTI.

Le prochain morceau qui en vaut la peine reste **RUSLE** : c'est lui qui
transformerait trois constats séparés — couvert qui recule, averses qui
s'intensifient, pentes non aménagées — en une chaîne causale chiffrée.
