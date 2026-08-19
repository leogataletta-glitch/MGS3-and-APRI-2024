# La photo, et le vert de la colonne

## Un seul fichier

| Fichier | |
|---|---|
| `app.py` | la photo réservée au cadre de résilience, et le vert de la colonne désaturé |

Rien d'autre à renvoyer : les deux changements tiennent dans ce fichier.

## La photo

Elle ne s'affiche plus que sur **Cadre de résilience**, la page d'entrée. Partout
ailleurs, la page commence directement par son titre.

Ce que cela rend : 300 pixels en tête de chaque page, soit un tiers d'écran. Sur
*Analyse des résultats*, les six cartes de dimension sont maintenant visibles
sans faire défiler ; sur *Note aux bailleurs*, les quatre chiffres et le premier
constat le sont aussi.

## Le vert

Il est **désaturé, pas éclairci** — même teinte, même profondeur, mais 30 % de
saturation au lieu de 54 %.

| | avant | après |
|---|---|---|
| Haut de la colonne | `#123c30` | `#203c35` |
| Bas de la colonne | `#0d2f26` | `#192e29` |
| Pastille de l'onglet actif | `#63c493` | `#7cc0a0` |

La pastille suit le fond, et il fallait qu'elle le suive : sur un vert adouci,
l'ancien vert vif de l'entrée active serait devenu la seule couleur franche de
l'écran — on aurait déplacé le problème d'un centimètre.

La colonne se détache toujours nettement du contenu blanc ; elle ne lui prend
plus le regard.

## Vérifié

- **66 rendus** — 11 pages × 3 combinaisons de filtres × 2 langues — zéro
  exception ;
- au navigateur : la photo présente sur le cadre de résilience, absente du
  territoire, de l'analyse des résultats et de la note aux bailleurs ; le filet
  sous les six onglets de dimension toujours en place.
