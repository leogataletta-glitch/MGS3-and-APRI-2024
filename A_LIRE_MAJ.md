# Correction — `networkx` manquait au déploiement

## Envoyez ces deux fichiers

| Fichier | |
|---|---|
| **`boucles_moteur.py`** | **la correction** — la dépendance est supprimée |
| `requirements.txt` | `numpy` y est maintenant écrit noir sur blanc |

Les fichiers de la livraison précédente restent nécessaires s'ils ne sont pas
encore en ligne : `boucles_page.py`, `graphe_causal.json` (dans le dossier
`data`), `app.py`, `cadre_page.py`.

## Mon erreur

J'ai vérifié que `networkx` était disponible **dans mon environnement de
travail**, et j'en ai conclu qu'il le serait au déploiement. Il n'était pas dans
`requirements.txt` : Streamlit Cloud ne l'a donc jamais installé, et le site est
tombé au premier import.

## Ce que j'ai fait, et pourquoi pas l'inverse

Ajouter `networkx` aux dépendances aurait marché. J'ai préféré **supprimer la
dépendance** : elle ne servait qu'à une chose — énumérer les cycles du graphe —
et cela tient en vingt lignes. Installer un paquet entier pour une seule
fonction, et surtout ajouter un fichier de plus à ne pas oublier d'envoyer,
coûtait plus cher que de l'écrire.

L'énumération part de chaque nœud et n'explore que les nœuds d'indice supérieur
au départ : chaque boucle n'est ainsi trouvée qu'une fois, à partir de son plus
petit indice.

## Une deuxième erreur, trouvée en vérifiant

J'avais posé une borne de longueur à dix nœuds par boucle. **Elle coupait six
boucles** de onze à treize nœuds : l'algorithme était juste, la borne était trop
basse, et la liste sortait incomplète sans le dire — les compteurs de leviers
s'en trouvaient faussés.

Je ne l'ai vu qu'en **comparant ma sortie à celle de la bibliothèque de
référence**, ensemble d'arêtes contre ensemble d'arêtes. La borne est passée à
seize : les **38 boucles** sont retrouvées, exactement les mêmes, sans doublon
ni cycle en trop, en une milliseconde.

Le drapeau de troncature reste en place : le jour où quelqu'un densifiera le
modèle au point de heurter ces bornes, la liste le dira au lieu de mentir par
omission.

## Vérifié

- `networkx` n'apparaît plus nulle part dans le code ;
- **énumération identique à la référence**, ensemble par ensemble : 38 boucles,
  27 renforçantes, 11 équilibrantes ;
- **42 rendus complets** — 7 pages × 3 combinaisons de filtres × 2 langues —
  zéro exception, zéro message d'erreur ;
- page ouverte dans le navigateur : aucune exception à l'écran, les boucles
  s'affichent avec leur sous-type R+ / B−.

## Ce qui reste à surveiller

`numpy` est utilisé par le moteur. Il arrive de toute façon avec `pandas`, donc
le site tournait déjà — mais il est désormais déclaré explicitement, ce qui
évite de dépendre d'un effet de bord.
