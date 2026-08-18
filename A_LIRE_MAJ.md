# À faire maintenant : renvoyer `i18n.py`

Le message rouge dit vrai. Il manque sur GitHub la dernière version de
`i18n.py` — celle qui contient la clé `a_lieu`, utilisée par le nouveau bloc de
marque de la colonne de gauche. Sans elle, « Sud et Grand'Anse, Haïti »
s'afficherait sous la forme `a_lieu`.

**Envoyez `i18n.py` depuis `MAJ_resilience`** (233 829 octets, daté
d'aujourd'hui). C'est le seul fichier réellement manquant.

Renvoyez aussi `app.py` : il porte la correction ci-dessous.

---

## Pourquoi ce message revenait tout le temps — et pourquoi il ne reviendra plus

Le garde-fou comparait une **date** : `i18n.VERSION` contre la date attendue
par `app.py`. Au moindre écart, il arrêtait le site. C'était trop strict. Une
mise à jour qui ne touchait qu'à la mise en page bloquait tout l'affichage
alors que rien n'était cassé, et vous envoyait renvoyer un fichier de 230 ko
sans raison. Ce faux positif vous a coûté plus de temps que la panne qu'il
prévient — cinq fois.

Il vérifie désormais **la présence des clés**, pas la date. Le défaut à
attraper est précis : une clé appelée par le code manque du dictionnaire, et
son *nom* s'affiche à la place du texte. C'est exactement cela qui est testé,
sur les 21 clés introduites par les mises à jour récentes.

Conséquence pratique :

| Situation | Avant | Maintenant |
|---|---|---|
| `i18n.py` d'une version antérieure, mais toutes les clés présentes | site bloqué | **rien, le site fonctionne** |
| une clé réellement absente | site bloqué | site bloqué, avec le **nom des clés manquantes** |
| tout à jour | site fonctionne | site fonctionne |

Les trois cas ont été rejoués pour de vrai — vieux fichier, fichier amputé de
deux clés, fichier à jour — et se comportent comme le tableau l'annonce. Dans
le cas amputé, le message nomme maintenant les clés en cause : plus besoin de
deviner quel fichier renvoyer.

**Aujourd'hui le message est justifié** : `a_lieu` manque vraiment sur GitHub.
C'est la dernière fois qu'il se déclenche pour une simple différence de date.

---

## Rappel du design livré

Le ruban vert plein cadre, les onglets en pastilles, le logo du PNUE en réserve
à droite, le bloc de marque sur deux niveaux et le bandeau à 300 px — tout cela
est dans `app.py` et `assets.py`, déjà en ligne d'après le message d'erreur
(c'est le nouveau `app.py` qui l'affiche).

## L'envoi

| Fichier | Pourquoi |
|---|---|
| `i18n.py` | **manquant en ligne** — c'est la cause du message rouge |
| `app.py` | garde-fou corrigé |
| `assets.py` | par sécurité, s'il n'était pas passé |

Sur GitHub : `Add file` → `Upload files`, les trois ensemble, un seul
`Commit changes`.

## Vérifié

- 96 rendus complets — 12 pages × 4 combinaisons de filtres × 2 langues —
  **zéro exception, zéro message d'erreur** ;
- 782 clés de traduction, aucun doublon, toutes avec un `fr` et un `en` ;
- aucune clé brute affichée, dans les deux langues ;
- les trois comportements du garde-fou rejoués un par un.
