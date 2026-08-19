# Fiche synthèse — résilience des paysages

## Deux fichiers, MÊME commit

| Fichier | |
|---|---|
| `fiche_paysages.py` | **nouveau** — la fiche |
| `app.py` | l'onglet dans la colonne de gauche |

Elle s'appuie sur `croisement_moteur.py`, livré précédemment : s'il n'est pas
encore poussé, envoyez-le avec. **Rien n'a été supprimé ni modifié ailleurs.**

## Ce que contient la fiche

**1 · Les deux paysages, d'ensemble** — les deux scores face à face, l'écart au
milieu, celui qui est en tête marqué comme tel, puis les six dimensions en
barres avec l'écart en points colorié au profit du paysage qu'il avantage.

> Littoral **4,87** · Montagne **4,30** · écart **0,57**

**2 · Ce qui les sépare le plus** — tous les indicateurs classés par ampleur
d'écart : Rang · Indicateur · Dimension · Littoral · Montagne · Écart · Paysage
le plus favorable. Un curseur règle la profondeur du classement, et un
diagramme divergent montre les mêmes écarts d'un coup — vers la gauche la
montagne, vers la droite le littoral.

Les écarts se lisent **sur le score sur dix**, pas sur la valeur brute : un
score se compare d'un indicateur à l'autre, un pourcentage de ménages ne se
compare pas à un hectare de forêt.

**3 · Le paysage comme système social** — le croisement paysage × découpage
social, au choix : groupe socio-économique, sexe, classe d'âge ou localité.
Paysage · Groupe · Répondants · Indice · Rang · Niveau de vulnérabilité.

**4 · Les deux extrémités** et **5 · la matrice des profils** — le groupe le
plus vulnérable et le plus résilient, calculés, puis la matrice à trois lignes
(le plus vulnérable / intermédiaire / le plus résilient) par colonne de paysage.
Les scores proches gardent leur rang : aucune différence n'est forcée.

**6 · Ce qu'il faut retenir** — cinq phrases **composées à partir des chiffres
du jour**, pas écrites d'avance. Elles répondent aux cinq questions posées :
quel paysage est en tête, quelles variables les séparent le plus, quel groupe
est le plus vulnérable, lequel s'en sort le mieux, et s'il existe un groupe
pénalisé par un paysage en particulier.

Sur les données actuelles, la dernière conclusion tombe du bon côté de la
nuance : l'écart littoral–montagne est du même ordre pour les trois catégories
socio-économiques, ce qui **désigne un effet de paysage plutôt qu'un effet
social**. La fiche l'écrit ainsi plutôt que de forcer un « groupe
particulièrement pénalisé » qui n'existe pas dans ces chiffres.

## Le point de méthode, écrit aussi dans la fiche

**Deux sources de scores, et il faut savoir laquelle on lit.**

- Le **paysage seul** est un découpage publié : le référentiel donne le score
  de chaque indicateur pour le littoral et pour la montagne, sur les 66
  indicateurs scorés. Les blocs 1 et 2 n'y recalculent rien.
- Le **paysage croisé avec un groupe** — « montagne × catégorie A » — n'existe
  dans aucun fichier : le référentiel publie vingt-deux découpages, pas leurs
  croisements. Les blocs 3 à 5 sont donc recalculés par le moteur de
  croisement, avec la même méthode, sur les 25 indicateurs dont la définition
  se reproduit exactement — 37 % du poids du référentiel.

Les deux échelles ne se comparent donc pas entre elles, et la fiche le dit là
où elles se touchent ; chacune se compare parfaitement avec elle-même, ce qui
est tout ce qu'un classement demande.

Un exemple de ce que cela change : le score d'ensemble publié du littoral est
4,87, tandis que l'indice partiel de « littoral × catégorie C » vaut 4,61. Ces
deux nombres ne se soustraient pas.

## Vérifié

- **60 rendus** — 10 pages × 3 combinaisons de filtres × 2 langues — zéro
  exception, zéro clé de traduction brute ;
- les quatre découpages du bloc 3 joués dans les deux langues ;
- page ouverte au navigateur : le duel, les dimensions, le classement des
  écarts, le diagramme divergent, la table croisée, les deux extrémités, la
  matrice et les enseignements.
