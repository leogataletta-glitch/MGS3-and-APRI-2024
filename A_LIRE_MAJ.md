# Envoyez `app.py`. Un seul fichier, et le message rouge disparaît.

## Mon erreur

J'avais posé le principe la semaine dernière — **un module qui apporte une
fonction apporte ses textes** — et je ne l'ai pas appliqué à `app.py`
lui-même. Les six noms de rubrique et les six lignes de carte vivaient dans
`i18n.py` seul. Résultat : `i18n.py` reste en arrière, et la page s'arrête,
alors que le fichier réellement neuf était `app.py`.

C'est la troisième fois que ce fichier bloque le site. Cette fois la cause est
traitée à la racine, pas le symptôme.

## Ce qui change dans `app.py`

Il porte désormais ses propres intitulés, avec **deux traitements différents**,
et la distinction compte :

- les clés **nouvelles** — les six lignes de carte — sont posées en
  `setdefault` : un `i18n.py` à jour reste maître ;
- les clés **renommées** — les six rubriques — sont **écrasées**. Un
  `setdefault` ne servirait à rien : la clé existe déjà dans l'ancien fichier,
  avec l'ancien nom, et c'est précisément celui-là qu'il faut remplacer.

`i18n.py` garde les mêmes valeurs et son rôle de catalogue complet. Il n'est
simplement plus indispensable au fonctionnement.

## Vérifié pour de vrai, pas en principe

J'ai rejoué votre situation exacte : `i18n.py` remis à la version précédente,
les six lignes de carte retirées, les rubriques rendues à leurs anciens noms
(« Les six dimensions », « Méthodologie d'enquête »). Résultat :

- **zéro erreur, page entièrement rendue** ;
- la colonne affiche bien **« Cadre de résilience »** et **« Analyse des
  résultats »** — les nouveaux noms, imposés par `app.py` ;
- les six cartes de dimension s'affichent avec leur intitulé et leur ligne
  descriptive.

Autrement dit : même si `i18n.py` n'arrive jamais sur GitHub, le site est
correct.

## L'envoi

| Fichier | |
|---|---|
| **`app.py`** | **la correction** — indispensable |
| `i18n.py` | facultatif désormais — le catalogue complet, si l'envoi passe |

Le reste de la mise à jour précédente est déjà en ligne : c'est bien le
nouvel `app.py` qui affiche ce message, et `cadre_page.py` a dû arriver aussi,
sans quoi le site n'aurait pas démarré du tout.

## Vérifications

- 48 rendus complets — 6 pages × 4 combinaisons de filtres × 2 langues —
  **zéro exception, zéro message d'erreur** ;
- aucune clé de traduction brute affichée, dans les deux langues ;
- le scénario du `i18n.py` en retard rejoué, avec le résultat ci-dessus.
