# Restructuration — six rubriques, cadre visuel, onglets de dimension

## Les six rubriques

| Ordre | Français | English |
|---|---|---|
| 1 | Vue d'ensemble | Overview |
| 2 | **Cadre de résilience** | **Resilience Framework** |
| 3 | Analyse des résultats | Results Analysis |
| 4 | Profils territoriaux et sociaux | Territorial and Social Profiles |
| 5 | Fiches d'intervention | Intervention Profiles |
| 6 | Données | Data |

**L'ordre suit la lecture, pas la fabrication** : on découvre le territoire, on
apprend ce qu'on mesure et comment, on lit les résultats par dimension, on
compare territoires et groupes, on passe à l'action ; les données brutes ferment
la marche pour qui veut refaire les calculs. Le cadre est donc remonté en
deuxième position.

---

## Cadre de résilience — une page qui se regarde

L'ancienne page de méthodologie était sept blocs de texte. Personne ne lit sept
blocs de texte sur un tableau de bord. Elle est remplacée par six schémas :

- **trois cartouches d'ouverture** — résilience générale / capacités détenues
  avant le choc / échelle 0-10 ;
- **le cadre AAA** — anticiper, absorber, s'adapter, une ligne chacun ;
- **les sept dimensions et leur poids** — une ligne par dimension : poids dans
  l'indice en barre, part en pourcentage, couverture en barre, indicateurs
  calculés sur total. On voit d'un coup que l'environnement pèse 29,9 % de
  l'indice et n'est couvert qu'à 44 %, quand les institutions pèsent 13,4 %
  couverts à 93 % ;
- **la chaîne de calcul** — métrique › barème › pondération › agrégation ;
- **le plan de sondage** — quatre chiffres clés et les quatre strates ;
- **les limites** — circularité, absence de validation empirique, mesure
  statique, cadrage et non prévision.

**Le document méthodologique complet n'est pas perdu** : il est en bas de page,
dans un volet replié, avec l'outil de croisement libre.

**Tous les chiffres de cette page sont calculés** depuis `resultats.json`.
Aucun poids, aucune couverture n'est écrit en dur : si un indicateur est calculé
demain, la page le dit d'elle-même. Une page de méthode qui annonce des poids
faux est pire qu'une page absente, parce qu'on la croit.

---

## Analyse des résultats — six cartes rectangulaires

Les six dimensions sont désormais des **cartes** : nom en gras, une ligne
disant ce qu'on y trouve, la carte courante en aplat bleu plein, les autres
blanches avec une ombre qui se renforce au survol. Deux rangées de trois.

Deux gains, pas un seul :

- la cible est franche, on vise sans chercher ;
- **seule la dimension demandée est calculée.** Les anciens onglets Streamlit
  rendaient les six pages à chaque affichage, y compris les trois cents
  questions de la dimension économique : sept secondes pour en montrer une.

Chaque dimension garde ses deux sous-onglets — les questions posées, puis les
indicateurs de résilience.

---

## Les couleurs ont été validées, pas choisies à l'œil

Les sept teintes de dimension passent les cinq contrôles d'un validateur de
palette : bande de clarté, plancher de saturation, séparation des paires
**voisines** en vision déficiente (deutéranopie, protanopie, tritanopie),
plancher en vision normale, contraste sur le fond. L'ancienne palette échouait
trois de ces cinq contrôles — deux dimensions voisines y étaient
indistinguables pour un lecteur protanope.

L'ordre des teintes n'est donc pas sémantique : il est contraint par ces
voisinages, puisque les dimensions se lisent toujours de I à VII. Seul le vert
de l'environnement est un choix de sens, et il a été gardé. Les pastilles ne
servent jamais seules : le nom de la dimension les accompagne toujours.

La palette est définie **une seule fois**, dans `cadre_page.py`, et importée
par les deux autres modules — deux palettes recopiées finissent toujours par
diverger.

---

## L'envoi

**Cinq fichiers, un seul commit.**

| Fichier | |
|---|---|
| `cadre_page.py` | **nouveau** — la page Cadre de résilience et ses textes |
| `app.py` | rubriques renommées et réordonnées, cartes de dimension |
| `i18n.py` | les six intitulés, les six lignes de carte |
| `dimension_page.py` | palette validée |
| `questions_dimension.py` | palette validée |

## Vérifié

- 23 modules compilent ; **48 rendus complets** — 6 pages × 4 combinaisons de
  filtres × 2 langues — **zéro exception, zéro message d'erreur** ;
- 799 clés de traduction, aucun doublon ; aucune collision entre les textes
  portés par les modules ;
- aucune clé brute affichée, dans les deux langues ;
- palette repassée au validateur : **cinq contrôles sur cinq** ;
- captures d'écran relues en français et en anglais : les six rubriques, la
  page Cadre entière, les cartes de dimension.

---

## Ce qui reste ouvert

Vous demandez une hiérarchie visuelle nette et l'ordre **indicateurs clés →
graphiques → cartes → comparaisons → tableaux**. Les pages de dimension le
suivent déjà en partie (quatre chiffres, puis carte, puis indicateurs). Deux
pages n'ont pas encore été retravaillées dans cet esprit :

- **Profils territoriaux et sociaux** — la comparaison entre territoires et
  groupes ; c'est là que le gain serait le plus visible ;
- **Fiches d'intervention** — elles portent encore l'ancien contenu « pistes »,
  sans lien avec une dimension ni une section.

Dites-moi par laquelle continuer.
