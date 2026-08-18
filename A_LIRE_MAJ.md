# Correction — `i18n.py` ne peut plus bloquer une page complète

## Envoyez ces quatre fichiers. `i18n.py` n'est plus indispensable.

| Fichier | |
|---|---|
| `questions_dimension.py` | **nouveau** — l'onglet des questions, **et ses textes** |
| `dimension_page.py` | les deux sous-onglets |
| `app.py` | bandeau nettoyé, contrôle assoupli |
| `accueil_page.py` | titre retiré sous le bandeau |
| *(`i18n.py`)* | *facultatif désormais — le catalogue complet, si l'envoi passe* |

---

## Ce qui n'allait pas, et ce que j'ai changé

Deux fois de suite, la mise à jour est arrivée en ligne sans son `i18n.py`, et
le site s'est arrêté sur « il manque des clés de traduction » — alors que le
seul fichier réellement neuf était `questions_dimension.py`. J'ai d'abord
corrigé le message, puis le contrôle. Ni l'un ni l'autre ne s'attaquait à la
cause : **une page complète dépendait d'un autre fichier pour ses propres
mots.**

Les fichiers sont poussés à la main, un par un. En oublier un est normal.
C'est l'architecture qui doit y survivre, pas vous qui devez être infaillible.

**Un module qui apporte une fonction apporte désormais ses textes.**
`questions_dimension.py` porte ses onze libellés dans un dictionnaire `TEXTES`,
versé dans le catalogue commun à l'import — et seulement si la clé n'y est pas
déjà, de sorte qu'un `i18n.py` à jour reste maître. Les mêmes clés restent dans
`i18n.py`, qui garde son rôle de catalogue complet, mais elles n'y sont plus
indispensables au fonctionnement.

**Vérifié pour de vrai**, pas en principe : j'ai rejoué votre situation exacte
— `i18n.py` resté à la version `ruban`, les onze clés retirées, tous les autres
fichiers à jour. Résultat : **411 blocs rendus, aucune erreur, l'onglet des
questions parfaitement lisible.**

C'est la règle à suivre pour toute fonction nouvelle. Elle est écrite en
commentaire dans les deux fichiers concernés, pour qu'on ne l'oublie pas.

---

## Rappel de ce que contient cette mise à jour

**Plus rien d'écrit sous le bandeau de l'accueil.** Le titre « APRI —
Observatoire de la résilience des paysages » répétait la colonne de gauche à
quinze centimètres de là. Le rappel du filtre ne s'affiche plus que lorsqu'un
filtre est réellement posé.

**Deux sous-onglets sous chaque dimension** — « Les questions posées, et les
réponses », puis « Indicateurs de résilience ». Chaque question avec son
intitulé exact, sa note, et la répartition en barres : pourcentage et effectif.
Le filtre de la colonne s'y applique instantanément.

**Le rattachement des questions**, à deux niveaux, dit à l'écran : le *lien
certain* (39 questions dont un indicateur est explicitement tiré, avec la
pastille du numéro de ligne) et le *rattachement thématique* par module de
questionnaire, qui est un choix éditorial. Deux cas méritent votre avis : la
sécurité alimentaire, rangée dans la dimension économique après une égalité
dans le calcul automatique ; et la dimension environnementale, à laquelle j'ai
rattaché irrigation, intrants, arbres fruitiers et causes de perte de récolte,
faute de questions d'enquête qui la mesurent directement.

---

## Vérifié

- 22 modules compilent ; **48 rendus complets** — 6 pages × 4 combinaisons de
  filtres × 2 langues — **zéro exception, zéro message d'erreur** ;
- 793 clés de traduction, aucun doublon, toutes avec un `fr` et un `en` ;
- aucune clé brute affichée, dans les deux langues ;
- **le scénario du `i18n.py` en retard rejoué** : la page se rend entièrement ;
- les 42 modules du questionnaire tous rattachés, aucun oublié.
