# Dimension environnementale — ce qui reste

**17 indicateurs calculés sur 38**, soit **44 % du poids** de la dimension
(39,7 points sur 90,0). Il reste **21 indicateurs, 50,3 points**.

---

## Ce qui est fait

| Bloc | Lignes | Source |
|---|---|---|
| Végétation, saison sèche | 33, 34, 37, 38, 39, 40 | Sentinel-2 |
| Thermique et santé du couvert | 36, 41, 42 | MODIS, 25 ans |
| Pluie, campagne de printemps | 43, 44, 45, 46 | CHIRPS, 45 ans |
| Couvert forestier | 54 | Hansen, 25 ans |
| Aires protégées | 55, 56 | WDPA |
| Macroplastiques | 62 | enquête ménage |

---

## Ce qui reste, classé par ce que ça demande

### A · Modélisable dès maintenant, aucune donnée nouvelle — 2 indicateurs, 6,8 pts

| Ligne | Indicateur | Poids |
|---|---|---:|
| 59 | Érosion et perte de sols | **3,42** |
| 60 | Terres dégradées (ODD 15.3.1) | **3,42** |

**Ce sont les deux plus lourds indicateurs environnementaux du cadre**, à
égalité avec la richesse spécifique. Et les cinq facteurs de RUSLE sont déjà
disponibles, dont deux sur ton disque :

| Facteur | Source | État |
|---|---|---|
| R — érosivité des pluies | CHIRPS journalier | **déjà exporté** |
| K — érodibilité du sol | SoilGrids 250 m | dans Earth Engine |
| LS — pente et longueur de versant | NASADEM 30 m | dans Earth Engine |
| C — couvert végétal | FVC Sentinel-2 | **déjà calculé** |
| P — pratiques antiérosives | enquête ménage | à caler |

La ligne 60 suit la même logique via la méthode Trends.Earth : occupation du
sol, productivité primaire, carbone organique du sol.

**C'est le morceau qui manque au récit.** Le tableau de bord établit
aujourd'hui trois faits séparés — le couvert recule de 12,8 %, les averses à
50 mm augmentent dans les dix sections, 76 % des ménages ne sont pas sûrs de
garder leur parcelle et n'aménagent donc pas la pente. RUSLE les relie en une
chaîne causale chiffrée, en tonnes par hectare et par an.

### B · Un export de plus — 1 indicateur, 2,25 pts

| Ligne | Indicateur | Ce qu'il faut |
|---|---|---|
| 57 | Superficie de mangrove | une seconde date |

La surface est connue — 183 ha au total, dont 126 à Dalmette — mais le barème
demande un taux de conservation, donc deux dates. Global Mangrove Watch couvre
1996 à 2020 et le donnerait.

### C · Mesurer la mer au large, et non l'eau dans le polygone — 3 indicateurs, 6,3 pts

| Ligne | Indicateur | Poids |
|---|---|---:|
| 61 | Concentration en chlorophylle-a | 2,25 |
| 63 | Turbidité de l'eau (NDTI) | 1,78 |
| 58 | Superficie d'herbiers marins | 2,33 |

**J'ai fait une erreur de cadrage sur ces indicateurs, et elle est réparable.**
J'ai mesuré l'eau à l'intérieur du polygone terrestre de chaque section, où
elle occupe moins de 1 % de la surface — d'où les quatre pixels de Quentin et
le renoncement à scorer la turbidité.

Or ces trois indicateurs portent sur le **milieu marin**, qui est *au large* de
la section, pas dedans. En définissant une bande maritime d'un ou deux
kilomètres devant chaque section côtière, on obtient des milliers de pixels
d'eau au lieu de quelques dizaines, et Sentinel-3 OLCI donne la chlorophylle-a
à 300 m.

Trois sections portent de la mangrove, donc au moins trois sont côtières. Le
script dirait lesquelles le sont vraiment.

**Ce serait aussi la bonne fenêtre pour la turbidité** : en septembre-octobre,
pendant la saison cyclonique, quand l'érosion arrive effectivement dans l'eau —
et non en mars, où l'on n'observe qu'une eau claire parce qu'il n'a pas plu.

### D · Un projet cartographique — 7 indicateurs, 15,3 pts

| Lignes | Indicateurs |
|---|---|
| 64, 65 | Connectivité fonctionnelle et à faible mobilité |
| 66, 67 | Connectivité structurelle, libre et contrainte |
| 68 | Densité de lisières |
| 69, 70 | Rapport CORE + MOVE, surface CORE totale |

Il faut d'abord une **carte d'occupation du sol** du territoire. ESA WorldCover
à 10 m existe et couvre Haïti. Ensuite l'analyse en graphe demande un outil
dédié — Conefor pour la connectivité, GUIDOS/MSPA pour la segmentation
morphologique, Fragstats pour les lisières.

C'est faisable, mais c'est un projet en soi : une semaine, pas un après-midi.
La grille de déforestation à 300 m qu'on a déjà donne une première idée de la
fragmentation, sans la mesurer.

### E · Sans raccourci satellitaire — 6 indicateurs, 14,6 pts

| Lignes | Indicateurs |
|---|---|
| 47 | Richesse spécifique — **3,42, le plus lourd de la dimension** |
| 48, 49 | Simpson, Shannon |
| 50, 51, 52 | Diversité phylogénétique, abondance relative, diversité fonctionnelle |

**Il n'y a pas de raccourci.** GBIF existe pour Haïti, mais ses occurrences
reflètent l'effort d'observation et non la biodiversité réelle : scorer
là-dessus produirait un classement des endroits où des naturalistes sont
passés. Ces six indicateurs demandent des transects de terrain, à inscrire au
protocole de la prochaine mission.

### F · Renoncés pour raison de mesure — 2 indicateurs, 4,5 pts

| Ligne | Indicateur | Motif |
|---|---|---|
| 35 | Stabilité des eaux de surface | eau < 1 % de chaque section ; Dalmette varie d'un facteur 20, c'est un estran |
| 53 | Indice de diversité des cultures | calculable depuis l'enquête, mais c'est un indice de Simpson et non un pourcentage — le barème demande une conversion |

La 53 est en fait à portée : elle ne demande aucune donnée nouvelle, seulement
une décision sur la conversion du barème. Dis-le-moi et je la calcule.

---

## L'ordre que je recommande

1. **RUSLE et terres dégradées** (59, 60) — les deux plus lourds indicateurs
   modélisables, les ingrédients sont là, et c'est ce qui ferme le récit.
2. **La bande maritime** (61, 63, 58) — répare une erreur de cadrage, et donne
   la turbidité à la bonne saison.
3. **La diversité des cultures** (53) — une décision, pas un calcul.
4. **La mangrove** (57) — un export.
5. **La connectivité** (64 à 70) — un projet.
6. **La biodiversité** (47 à 52) — une mission de terrain.

Les cinq premiers points mèneraient la dimension environnementale de 44 % à
**environ 70 %** de son poids couvert.
