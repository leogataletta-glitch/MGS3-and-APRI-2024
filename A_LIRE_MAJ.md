# Le bleu est parti : une seule couleur d'accent, le vert

## Un seul fichier

| Fichier | |
|---|---|
| `app.py` | tout tient dans la feuille de style |

## Ce qui change

Tout ce qui **signale un état** — survol, sélection, champ actif — était bleu ;
c'est désormais le vert de la maison. Le bleu venait d'une charte antérieure et
ne se justifiait plus : la colonne de navigation, l'emblème et les pastilles de
filtre sont verts, de sorte qu'un onglet actif en bleu était la seule pièce
d'une autre couleur — l'œil y lisait un autre type d'objet.

| | avant | après |
|---|---|---|
| Carte de dimension active | `#14508f` | `#1c6349` |
| Survol d'une carte de dimension | bordure `#c9d8ea` | `#c3ded0` |
| Sous-onglet sélectionné | dégradé bleu | dégradé vert |
| Survol d'un sous-onglet | fond `#f4f8fc` | `#f2f9f5` |
| Bouton principal | dégradé bleu | dégradé vert |
| Survol de bouton, de liste, de radio | bordure `#b9d3ea` | `#b6d8c6` |
| Langue active, en haut à gauche | `#2f7fd6` | `#1c6349` |
| Pastille de rubrique, filet des encadrés, champ actif | `#1a6bb0` | `#1a6b52` |

**La langue a suivi, elle aussi.** Elle était volontairement bleue pour ne pas
se confondre avec la navigation. C'est la distinction qui a fini par coûter
plus qu'elle ne rapportait : deux couleurs d'accent sur un même écran se lisent
comme deux familles d'objets, et il n'y en a qu'une ici. La position — en haut,
hors de la colonne — suffit à distinguer un choix de langue d'un onglet de page.

## Ce qui reste bleu, et pourquoi

**Les barres des graphiques.** Le bleu y est une couleur de série, pas un état :
dans le comparateur de groupes, le meilleur est vert, le pire est rouge, et les
autres sont bleus — les repeindre en vert ferait passer tout le monde pour le
meilleur. Une couleur qui code une donnée et une couleur qui code un état ne
peuvent pas être la même.

Dites-le-moi si vous voulez tout de même une gamme verte pour les graphiques :
c'est une décision de lecture, pas une contrainte technique.

## Vérifié

- **66 rendus** — 11 pages × 3 combinaisons de filtres × 2 langues — zéro
  exception ;
- au navigateur : survol d'une carte de dimension, onglet actif, pastille de
  rubrique, encadré d'information, bouton de langue — plus une seule pièce de
  chrome bleue.
