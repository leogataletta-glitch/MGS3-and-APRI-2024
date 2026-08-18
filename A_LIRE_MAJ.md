# Mise à jour — bandeau nettoyé, et deux sous-onglets par dimension

## 1. Plus rien d'écrit sous le bandeau

Le titre « APRI — Observatoire de la résilience des paysages » répétait mot
pour mot ce que la colonne de gauche affiche en permanence, à quinze
centimètres de là. Il est retiré : la page d'accueil commence maintenant par le
premier fait — 10 sections, 2 départements, 1 211 ménages — au lieu de se
présenter une deuxième fois.

Le rappel du filtre part avec, **mais seulement quand aucun filtre n'est
posé**. « Dix sections communales, tous les répondants » ne disait rien que la
ligne de périmètre ne dise trois centimètres plus bas. Dès qu'un filtre est
réellement choisi, la pastille revient — c'est le seul cas où l'oublier fait
mal lire un chiffre.

## 2. Deux sous-onglets sous chaque dimension

**« Les questions posées, et les réponses »**, puis **« Indicateurs de
résilience »**. Les questions d'abord, volontairement : un score sur dix est un
résultat de calcul, et qui arrive sur une dimension veut d'abord savoir ce
qu'on a demandé aux ménages. L'indicateur se comprend mieux quand on a lu la
question dont il sort.

Chaque question s'affiche avec son intitulé exact, sa note (réponse unique ou
multiple) et la répartition des réponses en barres horizontales — pourcentage
et effectif. **Le filtre de la colonne de gauche s'y applique** : choisir
Dumont recalcule toutes les répartitions sur les 122 ménages de Dumont, sans
attente, parce que le cache porte déjà chaque section, chaque paysage et chaque
sous-population.

### Comment une question est rattachée à une dimension

C'est le point délicat, et l'écran le dit lui-même. Deux niveaux :

**Lien certain** — la question alimente un indicateur de cette dimension. Ce
n'est pas une opinion : `resultats.json` porte, pour chaque indicateur, le
texte de la question dont il est tiré. Ces questions affichent une pastille
avec le numéro de ligne (`L4`, `L31`…). Il y en a 39 sur l'ensemble des six
dimensions.

**Rattachement thématique** — la question appartient au même module du
questionnaire qu'une question du premier groupe. J'ai construit le tableau
module → dimension en comptant, pour chaque module, les dimensions des
indicateurs qui y puisent ; puis je l'ai complété à la main pour les modules
dont aucun indicateur ne se sert encore. **C'est un choix éditorial**, il est
annoncé comme tel en bas de l'onglet, et deux cas méritent votre avis :

- **« Sécurité alimentaire »** arrivait à égalité entre la dimension physique
  et la dimension humaine. Je l'ai rangée dans la dimension économique, dont
  l'intitulé la nomme explicitement.
- **La dimension environnementale** n'a qu'une question à lien certain : elle
  est mesurée par satellite, pas par questionnaire. Je lui ai rattaché les
  modules où le ménage décrit la pression qu'il exerce sur le milieu ou celle
  qu'il subit — irrigation, intrants, arbres fruitiers plantés, causes de perte
  de récolte. Discutable ; dites-moi si vous voyez les choses autrement.

### Un module = un volet repliable

La dimension économique porte à elle seule plus de trois cents questions : les
batteries par culture et par espèce pêchée, une question par culture. Déroulées
d'un bloc, elles noieraient les dix questions qui comptent. Chaque module est
donc un volet ; **ceux qui contiennent une question reliée à un indicateur
s'ouvrent d'office**, les autres attendent qu'on les demande.

### Deux choses à savoir

Les **intitulés des questions et des modalités restent en français** même en
version anglaise : ce sont les libellés du questionnaire de terrain, pas des
textes d'interface. Les traduire reviendrait à réécrire ce qui a été demandé
aux ménages.

Le **détail environnemental** (les onze indicateurs satellitaires) et les
**fiches d'organisations de base** se trouvent désormais dans le sous-onglet
« Indicateurs de résilience » de leur dimension. Avant les sous-onglets ils
étaient rendus après la page ; ils seraient tombés hors des deux onglets.

## L'envoi

**Cinq fichiers, un seul commit.** `app.py` refuse de démarrer si `i18n.py`
n'est pas à la version `2026-08-18-questions`.

| Fichier | Ce qui change |
|---|---|
| `questions_dimension.py` | **fichier nouveau** — l'onglet des questions |
| `dimension_page.py` | les deux sous-onglets |
| `app.py` | bandeau nettoyé, complément passé au bon onglet |
| `i18n.py` | 11 clés nouvelles, version `2026-08-18-questions` |
| `accueil_page.py` | titre retiré sous le bandeau |

## Vérifié

- 22 modules compilent ; **48 rendus complets** — 6 pages × 4 combinaisons de
  filtres × 2 langues — **zéro exception, zéro message d'erreur** ;
- 793 clés de traduction, aucun doublon, toutes avec un `fr` et un `en` ;
- aucune clé brute affichée, dans les deux langues ;
- **les 42 modules du questionnaire sont rattachés**, aucun oublié, aucun
  module déclaré qui n'existe pas dans les données ;
- rendu réel dans le navigateur : les deux sous-onglets, les volets par module,
  les barres avec pourcentage et effectif.
