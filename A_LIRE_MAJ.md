# Fiches d'intervention — désormais construites sur les leviers des boucles

## Envoyez ces deux fichiers

| Fichier | |
|---|---|
| `interventions_page.py` | **nouveau** — les fiches et leurs textes |
| `app.py` | l'onglet pointe vers les nouvelles fiches |

## Ce qui change

Les fiches ne sont plus écrites à côté de l'analyse : **elles en descendent**.
Chaque fiche agit sur un levier du graphe causal, et tout le reste est calculé
par le moteur des boucles :

- **l'effet simulé sur l'indice** — on pousse le levier de deux points et on
  laisse la propagation traverser le graphe ;
- **les indicateurs de suivi** — les lignes du référentiel que la simulation
  déplace le plus. Ils ne sont pas inventés pour la fiche : ce sont des
  indicateurs **déjà mesurés**, donc le suivi est outillé le jour où l'action
  démarre ;
- **les boucles traversées**, et combien sont renforçantes, combien
  équilibrantes ;
- **le classement des fiches**, par effet décroissant.

Changez une relation dans le modèle, et les fiches se réordonnent d'elles-mêmes.

Huit fiches : cuisson propre, agroforesterie et fertilité, eau, inclusion
financière, alerte et comités, foncier, contrôle forestier, état civil. Chacune
porte son objectif, ses activités, ses acteurs, sa faisabilité, son **niveau
d'intervention d'après Meadows**, et **la boucle qu'il s'agit de retourner**.

## Le résultat qui mérite votre attention

Le calcul fait apparaître une tension que je n'avais pas anticipée, et qui est
maintenant écrite en tête de page :

**Les fiches à effet immédiat ne sont pas les leviers de basculement.**

L'eau, le foncier et l'alerte déplacent le plus l'indice — mais appartiennent à
peu de boucles, ou à aucune. Leur effet est direct et **borné**.

Les pratiques agricoles conservatrices et le contrôle forestier le déplacent
dix fois moins — et ce sont les **deux seules fiches présentes dans des boucles
des deux sens**, donc les deux seules capables de retourner une dynamique
dégradante en dynamique régulatrice.

Un programme a besoin des deux : les premières pour montrer des résultats dans
la saison, les secondes pour changer ce que le système se fait à lui-même.
C'est exactement la distinction que fait votre document entre ajuster un flux
et casser une boucle — sauf qu'ici elle sort du calcul, pas d'une intuition.

## Deux choix que je dois signaler

**Seuls des leviers actionnables portent une fiche.** L'aridité et l'état de la
végétation arrivent en tête du classement des effets, mais on ne monte pas un
projet « sur l'aridité » : ce sont des états résultants. Les fiches agissent sur
ce qui se décide — un équipement, une pratique, une règle, un flux
d'information.

**Le classement n'est pas une priorisation.** Il suit l'effet simulé, pas la
faisabilité ni la priorité politique. La faisabilité est affichée à côté de
chaque fiche ; c'est l'atelier qui tranche. Le modèle propose.

Les anciennes pistes sont gardées, repliées en bas de page.

## Vérifié

- **42 rendus complets** — 7 pages × 3 combinaisons de filtres × 2 langues —
  zéro exception, zéro message d'erreur ;
- aucune clé de traduction brute affichée, dans les deux langues ;
- page ouverte dans le navigateur : le récapitulatif, les huit fiches, les
  indicateurs de suivi et les pastilles de basculement ;
- les textes de la page voyagent dans `interventions_page.py`, selon la règle
  des trois pannes précédentes.

## La suite possible

Chaque fiche pourrait porter un **effet par section communale** plutôt qu'un
effet national : le moteur sait déjà le faire, il suffit de brancher le filtre
de la colonne de gauche. Une fiche « cuisson propre » n'a pas la même portée à
Quentin qu'à Dalmette. Dites-moi si cela vous intéresse.
