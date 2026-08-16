# Mise à jour — les précipitations entrent dans l'indice

## Les 6 fichiers à mettre sur GitHub **dans le même commit**

| Fichier | Où | État |
|---|---|---|
| `app.py` | racine | remplacé |
| `i18n.py` | racine | remplacé |
| `environnement_page.py` | racine | remplacé |
| `data/resultats.json` | `data/` | remplacé |
| `data/ventilation.json` | `data/` | remplacé |
| `data/pluie.json` | `data/` | **nouveau** |

`i18n.py` passe en version **`2026-08-16-pluie`**.

---

## 1 · Les précipitations — quatre indicateurs de plus

CHIRPS, 1981-2025, moyenne sur chaque section. **56 indicateurs scorés sur
128** désormais.

| Ligne | Indicateur | Ensemble | Score |
|---|---|---|---|
| 43 | Indice de condition pluviométrique (PCI) | 27,5 | 2 |
| 44 | Indice d'aridité anormale | −0,04 | 5 |
| 45 | Rapport à la normale | 96,0 % | 10 |
| 46 | Indice de précipitation standardisé (SPI) | +0,04 | 10 |

Le score final monte de **+0,12 à +0,24 point** selon les sections.

### Trois décisions de méthode

**La normale est la moyenne 1991-2020**, période de référence recommandée par
l'Organisation météorologique mondiale.

**L'évaluation porte sur la moyenne des cinq dernières années**, pas sur 2025
seule. Les métriques parlent de conditions « courantes », mais scorer quatre
indicateurs sur une seule année les ferait bondir ou chuter ensemble pour des
raisons qui ne disent rien de la capacité du territoire. J'ai calculé les deux :
sur cette série, l'écart est d'un point sur le seul PCI. Le choix est donc peu
coûteux aujourd'hui et plus robuste demain. Un seul indicateur à changer dans le
script pour revenir à l'année seule.

**Le SPI est ajusté sur une loi gamma**, comme le veut la définition de McKee :
les cumuls annuels ne suivent pas une loi normale, et un simple écart type
surestimerait la rareté des années sèches.

### Une réserve que je dois signaler

**Deux des quatre indicateurs donnent le même score aux dix sections.** L'aridité
anormale vaut 5 partout, le SPI vaut 10 partout. Ils ajoutent du poids à l'indice
— 7,3 % au total pour les quatre — sans distinguer les territoires entre eux.

C'est logique : à 5,5 km de résolution, dix sections voisines reçoivent
sensiblement la même pluie. Ces indicateurs disent quelque chose du **Grand Sud
face à son propre passé**, pas de Trichet face à Dumont. Ils gardent tout leur
sens pour suivre l'évolution dans le temps ; ils n'en ont aucun pour classer les
sections. À toi de voir si tu les conserves dans le score final ou si tu les
sors, comme on l'avait envisagé pour les OCB.

### Ce que la série révèle

**2005 est une année hors norme** : 2 251 mm à Anse à Drick contre 1 229 de
normale. La saison cyclonique 2005 est celle de Dennis, Emily et Wilma. Elle
étire tellement l'étendue historique que toutes les années ordinaires se
retrouvent dans le tiers bas du PCI — c'est pourquoi cet indicateur affiche 2 ou
3 partout alors que la pluie est normale.

**2015 est l'année la plus sèche** de la série, 810 mm. À rapprocher de
l'enquête : **48,7 % des ménages citent la sécheresse** comme première cause de
baisse des rendements. La série CHIRPS permet maintenant de confronter cette
perception à ce que la pluie a réellement fait.

---

## 2 · Un bloc « Précipitations » dans l'onglet environnemental

Cumul annuel de 1981 à 2025 pour la section choisie, avec la normale tracée en
pointillés. Les barres sont **ocre sous la normale, bleues au-dessus** : ce qui
compte n'est pas la pluie mais l'écart à l'ordinaire — 2 000 mm est peu à
Mouline et considérable à Dumont.

Quatre chiffres clés au-dessus : normale, moyenne récente, année la plus sèche,
année la plus humide.

---

## 3 · La grille de déforestation — script corrigé

L'export n'a produit que **20 cellules et 1,2 hectare** au lieu de 1 373, toutes
concentrées sur quatre kilomètres carrés. En cause : `reproject()`, qui force le
calcul à une échelle fixe et limitait l'échantillonnage à une seule tuile.

Le script construit désormais une **vraie grille de polygones** et agrège dedans.
Plus lent, mais le résultat couvre le territoire entier et se vérifie contre le
total connu.

**À relancer** : `satellite\gee_grille_deforestation.js`, version corrigée sur
ton bureau. Avant de lancer l'export, regarde la console : elle affiche le
nombre de cellules retenues. **Quelques milliers, c'est le signe que ça marche.**
Quelques dizaines, non — préviens-moi.

---

## Ce qui reste

**32 indicateurs environnementaux** non calculés, contre 36 avant. Le bloc 6 de
l'onglet les liste par source. Le plus accessible ensuite : MODIS pour la
température de surface, ou Sentinel-2 pour les indices de végétation.
