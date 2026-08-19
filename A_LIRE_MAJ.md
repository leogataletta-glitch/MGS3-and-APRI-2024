# Les radars sont revenus — et une erreur de ma part à signaler

## Envoyez ces trois fichiers dans le MÊME commit

| Fichier | |
|---|---|
| `radar_page.py` | **nouveau** — le profil en radar |
| `dimension_page.py` | le radar de la dimension, entre les chiffres et la carte |
| `synthese_page.py` | le radar des six dimensions, en tête de page |

`radar.py`, qui dessine la figure, est déjà en ligne — il n'a pas changé.

## Ce qui s'était passé

Vous avez raison : les radars existaient, et ils ont disparu. Le code n'avait
pas été supprimé — il vivait dans `resilience_page.py`, une page devenue
**inaccessible** quand la navigation a été refondue. Le module était toujours
importé par `app.py`, mais plus jamais appelé. C'est pire qu'une suppression :
rien ne le signalait.

## Ce qui revient, et en mieux

**Deux niveaux de lecture**, comme dans le cadre APRI :

- **les six dimensions** — un axe par dimension, chaque axe portant la moyenne
  pondérée de ses indicateurs scorés ;
- **les indicateurs d'une dimension** — un axe par indicateur, pour voir ce
  qu'une moyenne cache.

**Trois registres de comparaison**, et c'est l'ajout qui manquait — l'ancien
radar ne comparait que des sections communales :

- **sections communales** — où l'action se décide ;
- **paysages** — littoral contre montagne ;
- **groupes de répondants** — femmes et hommes, tranches d'âge, catégories
  économiques.

Trois profils superposés au plus, échelle **fixe de 0 à 10** sur tous les axes :
c'est la condition pour que deux profils se comparent honnêtement. Sous chaque
figure, le tableau des valeurs exactes au centième — l'œil lit mal un rayon, et
deux séries proches sont indiscernables sur le dessin.

**Où ils se trouvent :**

- dans **Analyse des résultats**, sur chaque dimension, entre les quatre
  chiffres clés et la carte — il compare cette dimension entre sections, entre
  paysages ou entre groupes ;
- dans **Profils territoriaux et sociaux**, en tête, avec les deux niveaux et
  les trois registres.

**Deux honnêtetés écrites à l'écran.** L'aire du polygone ne veut rien dire —
elle dépend de l'ordre des axes, qui vient du cadre et non des données ; on
compare des rayons. Et en comparaison par groupe, les indicateurs satellitaires
portent la même valeur pour tous les groupes : c'est une propriété de la source,
pas une égalité mesurée.

Un plafond de douze axes s'applique au niveau des indicateurs — la dimension
environnementale en compte dix-sept, et à dix-sept sommets les libellés se
chevauchent. Le radar garde les douze plus bas **et l'écrit** : « cette
dimension compte 17 indicateurs scorés ; le radar montre les 12 plus bas ».

## L'erreur que je dois vous signaler

En vérifiant ce lot, j'ai découvert que **mon banc de test était faux depuis
plusieurs livraisons**. Il posait la page à afficher dans une clé de session
nommée `mode`, alors que l'application lit `app_mode` ; et la langue dans
`lang` au lieu de `choix_langue`. Résultat : mes « 42 rendus, 7 pages × 3
filtres × 2 langues » rendaient **quarante-deux fois la page d'accueil, en
français**. La couverture que je vous ai annoncée n'existait pas.

Ce que cela ne remet pas en cause : les captures d'écran, elles, étaient
réelles — j'ouvrais bien les pages dans un navigateur, et c'est ainsi que les
défauts d'affichage ont été trouvés et corrigés.

Le banc est réparé. Passé sur l'état actuel du code, avec les bonnes clés :
**42 rendus, 7 pages × 3 combinaisons de filtres × 2 langues, trois dimensions
différentes — zéro exception, zéro clé de traduction brute.** Plus quatorze
scénarios ciblés sur les radars : trois sections superposées, deux groupes,
deux paysages, le niveau indicateurs, une sélection vide, dans les deux
langues — tous passent.

Je vous le dis parce qu'une vérification qu'on croit faite est plus dangereuse
qu'une vérification qu'on sait absente.
