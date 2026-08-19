# La carte des paysages pilotes est retirée

## Un seul fichier

| Fichier | Où |
|---|---|
| `territoire_page.py` | racine du dépôt |

**Et un fichier à NE PAS envoyer :** `carte_paysages.jpg`. Si vous l'avez déjà
mis dans `data/`, il ne casse rien — plus personne ne l'appelle — mais vous
pouvez le supprimer du dépôt.

Les six autres fichiers de la livraison précédente restent valables :
`carte_localisation.py`, `carte_localisation.json`, `leaflet.js`,
`leaflet.css`, `carte_entretiens.jpg`.

## Ce qui reste sur la page « Le territoire »

1. **La carte interactive** et ses treize couches ;
2. **la vignette Haïti**, qui situe la zone dans le pays ;
3. **la carte des points d'entretien**, avec sa légende refaite.

## Pourquoi celle-là ne tenait pas

À l'impression, une carte régionale se lit sur une feuille A3 : le trait fin
des aires protégées, les numéros, le dégradé du relief, tout y est lisible.
Ramenée à 1 100 pixels de large dans une page web, la même carte perd
exactement ce qui faisait sa valeur — le liseré des aires protégées devient un
halo, les numéros deviennent des taches, et la moitié du cadre est occupée par
la mer.

Ce qu'elle apportait n'est pas perdu : les aires protégées sont une couche de
la carte interactive, qu'on allume et qu'on interroge, et le relief y est une
couche d'ombrage. La carte des entretiens, elle, reste : son sujet — des points
serrés sur un fond de relief — supporte la réduction, parce qu'on y regarde des
amas, pas des traits.

## Vérifié

- **66 rendus** — 11 pages × 3 combinaisons de filtres × 2 langues — zéro
  exception ;
- page ouverte au navigateur : la carte retirée, les trois autres en place,
  hauteur de page ramenée de 3 322 à 2 341 pixels.
