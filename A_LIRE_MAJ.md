# « Le système en marche » — le schéma encombré remplacé

## Trois fichiers — TOUS À LA RACINE

| Fichier | Où le déposer |
|---|---|
| `systeme_page.py` | **racine** — **nouveau** |
| `app.py` | **racine** — modifié |
| `boucles_page.py` | **racine** — modifié |

---

## Ce qui remplace le schéma

Quarante-cinq boîtes et quatre-vingt-deux flèches sur une seule image : on y
lisait la **structure** — utile une fois — et jamais ce qui monte ni ce qui
descend. Une carte du câblage, là où vous vouliez voir la machine tourner.

« Boucles de rétroaction » a donc maintenant **trois vues** :

1. **Ondes de choc** — un choc, vague par vague ;
2. **Le système en marche** — *nouveau* ;
3. **Boucles, leviers, effet total** — l'analyse, inchangée. Le schéma de
   réseau y reste, mais **replié** : il n'est plus la première chose à
   regarder.

## Comment la nouvelle vue fonctionne

Les quarante-cinq variables sont là, groupées par dimension, chacune avec son
niveau sur dix — celui mesuré par l'enquête là où il existe, un repère gris
marquant ce point de départ sur chaque barre.

**Vous cliquez dans une barre** pour imposer une valeur : la variable est alors
*tenue* (son nom passe en gras, sa barre s'encadre). Un deuxième clic au même
endroit la libère.

**Vous appuyez sur lecture.** Chaque variable monte ou descend selon ce que ses
voisines lui font, tour après tour, jusqu'à ce que le système se stabilise —
et il le dit quand c'est fait. En haut : le tour courant, le nombre de
variables tenues, combien montent, combien baissent, et la moyenne des
variables mesurées avec son écart au départ.

Exemple, l'électricité portée de 0 à 8 : au sixième tour, 23 variables en
hausse, une en baisse, et la moyenne du modèle passe de 3,96 à 4,25. Ce qui
bouge le plus, dans l'ordre : le revenu (+2,96), l'accès aux messages d'alerte
et le sentiment de sécurité (+2,46 chacun), l'achèvement du primaire (+1,73),
la sécurité alimentaire (+1,17).

## Pourquoi l'état mesuré est un point d'équilibre

Le graphe ne dit rien des niveaux : il dit ce qu'un **écart** produit ailleurs.
L'état mesuré est donc la référence, et le modèle est au repos tant qu'on n'y
touche pas. C'est la seule lecture honnête : le territoire observé est, par
construction, le point de fonctionnement du modèle.

Dès qu'une valeur est imposée :

```
écart₀     = ce que vous imposez
écart_{t+1} = écart₀ + A · écart_t
```

La suite converge vers `(I − A)⁻¹ · écart₀`, c'est-à-dire **exactement l'effet
total** que calcule le moteur des boucles. Les trois vues ne peuvent donc pas
diverger : la première montre le chemin d'un choc, la deuxième l'état du
système entier, la troisième le point d'arrivée.

**Un pas n'est pas une année.** C'est un tour de propagation. Le modèle connaît
l'ordre des relais, pas leur durée — une coupe de forêt met des années à se
voir sur les sols, un choc de revenu se voit en semaines — et la page le dit
sous le tableau plutôt que de laisser croire à un calendrier.

## Vérifié

- **88 rendus** — 11 pages × 4 combinaisons × 2 langues, les quatre écrans de
  l'accueil et **les trois vues des boucles** — zéro exception ;
- ouvert au navigateur dans les deux langues : lecture, pas à pas, retour à
  l'état mesuré, clic dans une barre, libération d'une variable tenue ; aucune
  erreur au journal ;
- recoupé avec le moteur : après stabilisation, les écarts obtenus sont ceux
  que `boucles_moteur.propager` calcule par inversion.
