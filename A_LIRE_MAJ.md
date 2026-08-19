# « Croisement des résultats » — le moteur d'exploration

## Trois fichiers, MÊME commit

| Fichier | |
|---|---|
| `croisement_moteur.py` | **nouveau** — le calcul |
| `croisement_resultats.py` | **nouveau** — la page |
| `app.py` | l'onglet dans la colonne de gauche |

## Ce qui a rendu la chose possible

Le dépôt contenait déjà `croisement.npz` : pour chacune des **2 702 modalités
de réponse des 483 questions**, l'appartenance des 1 211 répondants, en bits.
Une intersection est donc un ET binaire sur un vecteur de 1 211 booléens —
**0,1 milliseconde** pour une requête à trois conditions, 3 ms pour le profil
complet. Des effectifs agrégés n'auraient rien permis : on ne déduit pas d'un
« 40 % sans latrine » et d'un « 30 % sans eau » combien de foyers cumulent les
deux, cela dépend entièrement de leur recouvrement.

**Rien n'est codé question par question.** Le catalogue est lu du fichier
d'index. Ajoutez une question à l'enquête, régénérez l'index, elle apparaît
dans les listes sans qu'une ligne de code change.

## Ce que fait la page

**Zone 1 — construire le profil.** Des conditions empilables (huit au plus),
chacune : une variable — les cinq registres de segmentation puis les 483
questions — un sens *est / n'est pas*, et une ou plusieurs valeurs (combinées
en OU à l'intérieur de la condition). Les conditions se combinent en ET ou en
OU, se retirent une à une, et chacune affiche son effectif isolé. Un
interrupteur ouvre un **groupe B** en vis-à-vis.

**Zone 2 — ce qu'est ce groupe.** Effectif, part de l'échantillon, indice
partiel de résilience, écart à l'ensemble. Puis les dimensions en barres —
groupe contre ensemble, ou groupe A contre groupe B — la carte par section
communale avec quatre lectures au choix (nombre, part du groupe, part de la
section, indice), le tableau territorial, et le détail indicateur par
indicateur avec l'écart à l'ensemble.

**Zone 3 — A contre B**, dimension par dimension, avec la différence signée.

**Les suggestions** ajoutent en un clic un registre absent de la requête, posé
sur sa valeur la plus fréquente.

## Un résultat que le calcul donne gratuitement

Sous chaque cumul, l'outil écrit ce que le profil pèserait **si les conditions
étaient indépendantes** — le produit des taux — à côté de l'observé. Trois
privations cumulées (sans latrine améliorée, sans eau améliorée, sans
électricité) concernent **303 répondants, 25,0 %** de l'échantillon, très
au-dessus du produit des taux. C'est cet écart qui dit qu'on tient un profil,
et non trois problèmes séparés.

## Le point sur lequel je dois être précis : le score de résilience

**Il n'existe pas de score APRI par répondant.** Les scores sont calculés
indicateur par indicateur sur une population : « 31,9 % des ménages ont un
assainissement amélioré » devient un 2 sur 10 par le barème publié. Pour noter
un sous-groupe, il faut recalculer chaque indicateur sur lui, puis appliquer le
même barème.

Je ne l'ai pas fait sur parole. Pour chaque indicateur d'enquête, la valeur est
recalculée sur l'échantillon **entier** et comparée à la valeur publiée :

- si elle tombe à moins d'un point **et** que le barème rend le score publié,
  l'indicateur est retenu — sa définition est reproduite, on peut donc la
  porter sur n'importe quel sous-ensemble ;
- sinon il est écarté. Les écarts viennent de bases restreintes (un indicateur
  calculé sur les seuls agriculteurs, ou les seuls ménages avec enfants) ou de
  ratios qui ne sont pas des parts de ménages. Deviner ces bases aurait produit
  des chiffres faux que rien n'aurait signalés.

**25 indicateurs sur 66 passent le test, soit 37 % du poids du référentiel**,
et les 25 reproduisent exactement leur score publié. La couverture est très
inégale et la page l'affiche : 85 % du poids de la dimension physique, 44 % de
l'institutionnelle, 36 % de l'économique, 39 % de l'humaine, 25 % de la
sociale, et **rien de l'environnementale** — le couvert forestier et la pluie
sont mesurés par satellite et ne varient pas selon le répondant.

C'est donc un **indice partiel**, écrit comme tel à l'écran. Il se compare d'un
groupe à l'autre — les deux côtés sont calculés sur les mêmes indicateurs — et
il ne se compare pas au score APRI publié. Sur l'échantillon entier il vaut
3,32 ; les femmes en montagne cumulant les trois privations tombent à 2,66.

## Vérifié

- les 25 indicateurs retenus reproduisent **exactement** le score publié sur
  l'échantillon entier (contrôle automatique au chargement du moteur) ;
- scénario réel joué de bout en bout dans les deux langues, avec et sans groupe
  B : trois privations cumulées + segmentation par sexe ;
- page ouverte au navigateur : constructeur, indicateurs de tête, barres par
  dimension, carte à quatre lectures et tableau territorial.

`croisement_page.py`, l'ancien outil de croisement rangé dans le document
méthodologique, n'a pas été touché : il continue de fonctionner.
