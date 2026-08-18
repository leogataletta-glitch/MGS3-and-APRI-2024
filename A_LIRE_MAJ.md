# Results Analysis — nouvelle architecture d'interface

## Envoyez ces cinq fichiers dans le MÊME commit

| Fichier | |
|---|---|
| `app.py` | la colonne de gauche ne porte plus les filtres |
| `filtres.py` | la barre de filtres dans la page |
| `dimension_page.py` | dimension → description → filtres → liste d'indicateurs |
| `questions_dimension.py` | intitulés professionnels, tout replié, recherche |
| `synthese_page.py` | reprend la barre de filtres, puisqu'elle lit les filtres |

Les cinq ensemble : `app.py` n'appelle plus le panneau latéral, et
`dimension_page.py` appelle une fonction qui n'existe que dans le nouveau
`filtres.py`.

## Ce qui a changé

**Les filtres ont quitté la marge.** Ils sont dans la page, sous le titre et la
description de la dimension, en une bande horizontale : *Section communale ·
Paysage · Groupe · Réinitialiser*. Un filtre posé dans la colonne de gauche est
un filtre qu'on oublie — il agit sur des chiffres situés à quarante centimètres
de lui, et rien à l'écran ne relie les deux. Ici il est juste au-dessus du
résultat qu'il commande.

L'état reste commun à toute la plateforme : le choix vous suit d'une rubrique à
l'autre, et la pastille du bandeau haut continue de rappeler ce qui est filtré.

**La colonne de gauche ne fait plus que naviguer** — Vue d'ensemble, Cadre de
résilience, Analyse des résultats, Boucles de rétroaction, Profils territoriaux
et sociaux, Fiches d'intervention, Données.

**Plus rien ne se déroule tout seul.** La page est maintenant :

    dimension → description → filtres → liste d'indicateurs → détail

La liste d'indicateurs est compacte et **entièrement fermée**. Chaque ligne
porte le nom de l'indicateur et son score — *Achèvement de l'éducation primaire
(adultes) · 0,0 / 10* — et rien d'autre tant qu'on ne l'ouvre pas. Les
indicateurs sont classés **du score le plus bas** : un tableau de bord de
résilience se lit par ce qui manque.

À l'ouverture d'un indicateur : score, valeur mesurée, poids, source, sa
définition, la question d'enquête mot pour mot avec ses modalités, le barème,
la base, **la dispersion entre les dix sections communales** en barres, et **la
répartition des réponses** quand l'indicateur sort d'une question de ménage.

Un **champ de recherche** est posé au-dessus de la liste, dans les deux onglets.

**Les deux niveaux sont maintenant distingués, et dits.** L'onglet
*Indicateurs* vient en premier — c'est le produit de la plateforme. L'onglet
*Résultats du questionnaire* vient ensuite, et il s'ouvre sur un avertissement
en toutes lettres : *ce sont des réponses brutes, pas des indicateurs de
résilience ; un module de questionnaire n'est pas un indicateur du
référentiel*. C'était l'ambiguïté principale de l'ancienne page.

**Les codes du questionnaire ont disparu de l'écran.** « AQ. PROFIL DU
RÉPONDANT » devient *Profil du répondant*, « AF. COMPOSITION DU FOYER » devient
*Composition du foyer*. Les quarante-deux modules ont un intitulé analytique en
français et en anglais ; les codes restent les clés en base, comme vous le
demandiez. Un module qui échapperait au tableau ne fait pas réapparaître son
code : le préfixe est retiré et la casse rétablie automatiquement.

Les modules du questionnaire sont eux aussi **tous fermés** — ils s'ouvraient
auparavant dès qu'ils contenaient une question reliée à un indicateur, ce qui
déroulait des dizaines de graphiques d'un coup. Chaque volet fermé indique le
nombre de questions et, par une flèche, combien d'entre elles alimentent un
indicateur.

## Rien n'a été retiré

Le tableau comparatif de tous les indicateurs de la dimension existe toujours :
il ferme la marche, replié, pour qui veut tout voir d'un coup ou copier des
chiffres. L'ancien bloc « la source, ligne à ligne » n'a pas été supprimé — son
contenu est passé dans le volet de l'indicateur concerné, là où on le cherche.
Les quatre chiffres clés et la carte par section communale restent à leur
place, avant la liste.

## Vérifié

- **42 rendus complets** — 7 pages × 3 combinaisons de filtres × 2 langues,
  avec trois dimensions différentes — zéro exception, zéro clé de traduction
  brute ;
- **aucun code de questionnaire dans le texte rendu**, contrôlé par expression
  régulière sur les deux langues ;
- les 42 modules présents dans le cache ont bien un intitulé propre ;
- pages ouvertes dans le navigateur, en français et en anglais : la bande de
  filtres, les deux onglets, la liste fermée, un indicateur ouvert avec sa
  question, son barème, sa base et sa dispersion entre sections.
