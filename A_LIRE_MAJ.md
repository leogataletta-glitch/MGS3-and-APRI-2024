# Onglet « Diagramme radar de résilience » — et la liste complète à pousser

## Où sont les fichiers

Tous dans **`C:\Users\LEO_f\Desktop\MAJ_resilience\`**. Rien ailleurs.

## Ce qui vient d'être ajouté

Une **entrée à part entière dans la colonne de gauche**, entre « Analyse des
résultats » et « Boucles de rétroaction », avec sa propre icône : un hexagone,
ses rayons et un polygone intérieur — l'icône montre la figure que la rubrique
produit.

La page porte le radar pour lui-même : les deux niveaux (les six dimensions,
ou les indicateurs d'une dimension), les trois registres de comparaison
(sections communales, paysages, groupes de répondants), trois profils
superposés au plus, et le tableau des valeurs exactes.

Elle porte aussi le **mode d'emploi** qui n'avait sa place ni dans une page de
dimension ni dans les profils territoriaux : lire la forme et non l'aire,
pourquoi l'échelle reste fixe de 0 à 10, pourquoi trois profils au maximum, et
ce que le radar ne peut pas montrer — les indicateurs satellitaires n'ont pas
de ventilation par répondant, donc comparés par groupe ils portent la même
valeur pour tous, ce qui est une propriété de la source et non une égalité
mesurée.

La figure reste également là où elle commente autre chose : dans « Analyse des
résultats » pour la dimension ouverte, et dans « Profils territoriaux et
sociaux ». C'est le même moteur — `radar_page.py` — pour les trois vues.

## LA LISTE COMPLÈTE À POUSSER

Vous ne voyiez pas les radars parce que plusieurs livraisons se sont
accumulées. Voici tout ce qui, dans le dossier, doit se retrouver sur GitHub.
**Poussez le tout en un seul commit** — ces fichiers s'appellent les uns les
autres.

| Fichier | |
|---|---|
| `app.py` | navigation, onglet radar, ergonomie de la maquette |
| `icones.py` | **nouveau** — le jeu d'icônes, importé par trois fichiers |
| `filtres.py` | la barre de filtres dans la page |
| `accueil_page.py` | la page d'accueil refaite |
| `dimension_page.py` | filtres en page, indicateurs en accordéon fermé, radar |
| `questions_dimension.py` | intitulés professionnels, modules repliés, recherche |
| `synthese_page.py` | barre de filtres et radar des six dimensions |
| `radar_page.py` | **nouveau** — le moteur du radar |
| `radar_accueil.py` | **nouveau** — la rubrique radar |
| `interventions_page.py` | les fiches selon le protocole |
| `boucles_page.py` | l'exploration part des indicateurs les plus alarmants |

Trois de ces fichiers sont **nouveaux** : s'ils manquent, l'application ne
démarre pas du tout — `app.py` importe `icones` et `radar_accueil`,
`dimension_page` et `synthese_page` importent `radar_page`.

`pistes_page.py` n'est plus importé par personne ; il peut rester dans le
dépôt, il ne sera simplement plus chargé.

## Comment vérifier en dix secondes que le lot est bien passé

Sur le site, après déploiement :

1. la colonne de gauche affiche **huit entrées**, dont « Diagramme radar de
   résilience » en quatrième position ;
2. la page d'accueil montre **trois cartes** avec une pastille d'icône, et non
   trois chiffres sur une ligne ;
3. dans « Analyse des résultats », les filtres sont **dans la page** sous la
   description de la dimension, et la liste d'indicateurs est **fermée**.

Si l'un des trois manque, c'est que le fichier correspondant n'est pas parti.

## Vérifié

- **48 rendus complets** — 8 pages × 3 combinaisons de filtres × 2 langues,
  trois dimensions différentes — zéro exception, zéro clé de traduction brute,
  avec le banc de test corrigé (voir la note de la livraison précédente : il
  utilisait de mauvaises clés de session et ne rendait que la page d'accueil) ;
- page ouverte dans le navigateur : l'onglet apparaît avec son icône, la
  pastille active le désigne, et le radar des six dimensions s'affiche avec ses
  sélecteurs.
