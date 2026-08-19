# « Le territoire » — deux cartes, rien d'autre

## Deux fichiers, MÊME commit

| Fichier | |
|---|---|
| `territoire_page.py` | la page complète : titre, grande carte, vignette |
| `app.py` | appelle cette page ; les livraisons récentes passent dans « Données » |

## Ce que contient la page, désormais

**La grande carte** — les dix sections communales avec leurs limites, chacune
nommée, colorées par département, les limites départementales en tirets,
Jérémie et Les Cayes en repères. Au survol, chaque section donne sa commune et
son département.

**La vignette de localisation** — Haïti en entier, la zone d'étude en vert
cerclée de pointillés, à l'extrême sud-ouest du pays.

Et c'est tout. La page tient sur un écran.

## Ce qui en est sorti, et où c'est parti

| Ce qui a quitté la page | Où le trouver |
|---|---|
| Les trois chiffres de périmètre | le pied de la colonne de gauche les porte déjà |
| Les quatre résultats saillants | *Analyse des résultats*, dimension par dimension |
| La carte des scores par section | *Analyse des résultats* et *Profils territoriaux* |
| Les accès rapides | la colonne de gauche, en permanence |
| Les livraisons récentes | **déplacées dans « Données »**, avec les jeux de données |

Aucune de ces informations n'a été supprimée du site : elles ont été renvoyées
là où on les attend. Les livraisons récentes sont le seul bloc qui n'avait pas
d'autre foyer — elles sont maintenant à la suite des téléchargements, ce qui
est cohérent : c'est là qu'on vient voir ce qui est disponible, donc ce qui
vient d'arriver.

## La règle écrite dans le fichier

Pas de score, pas d'indicateur, pas de pourcentage, pas de classement, pas même
un effectif sur cette page. Une carte qui porte des couleurs de résultat répond
à « combien » avant d'avoir répondu à « où », et le lecteur qui cherchait
simplement à se situer repart avec un chiffre qu'il n'a pas demandé.

Les seuls textes restants sont les deux légendes sous les cartes. Une carte
sans légende se regarde mais ne se lit pas — dites-moi si vous les voulez
également retirées.

## Un fichier devenu inutile

`accueil_page.py` n'est plus importé par `app.py`. Il peut rester dans le dépôt
sans effet, ou être supprimé : il ne sert plus rien.

## Vérifié

- **60 rendus** — 10 pages × 3 combinaisons de filtres × 2 langues — zéro
  exception, zéro clé de traduction brute ;
- page ouverte au navigateur : hauteur totale 1 199 px, soit un écran, les deux
  cartes et rien d'autre ;
- les livraisons récentes retrouvées au bas de « Données ».
