# « Vue d'ensemble » devient « Le territoire »

## Quatre fichiers, MÊME commit

| Fichier | |
|---|---|
| `territoire_page.py` | **nouveau** — les deux cartes et la liste des sections |
| `accueil_page.py` | la page refaite : cartes, chiffres, plus de filtres, plus de récit |
| `cadre_page.py` | reçoit le récit APRI, entier, en tête |
| `app.py` | ordre de la colonne, nouveau libellé, page d'entrée |

## Ce qui change

**La colonne commence par « Cadre de résilience », puis « Le territoire ».**
On dit d'abord ce qu'on mesure, ensuite où on l'a mesuré, et les résultats
suivent. C'est aussi la page d'entrée du site désormais.

**La barre de filtres a disparu de cette page.** Vous aviez raison : une page
qui présente un périmètre n'a rien à filtrer, et le filtre servait à
restreindre des chiffres de cadrage — c'est-à-dire à contredire le propos. Les
filtres restent partout où ils commandent une analyse.

**Le récit APRI est parti dans « Cadre de résilience », entier.** Les quatre
paragraphes — origine, ce que mesure l'indice, comment il est construit, ce
qu'il ne prétend pas dire — ouvrent maintenant la page où l'on vient chercher
la méthode. Rien n'est perdu, rien n'est raccourci ; c'est un déplacement.

**Deux cartes nouvelles, et elles ne font pas le même travail :**

- **la vignette** situe — Haïti en entier, la zone enquêtée en vert cerclée de
  pointillés, à l'extrême sud-ouest du pays. Sa seule question est « où ? » ;
  elle ne porte ni valeur ni échelle de couleur ;
- **la carte de situation** nomme — les dix sections, chacune avec son nom,
  colorées par département, les limites départementales en tirets, Jérémie et
  Les Cayes en repères. Sa question est « laquelle ? ». Au survol, chaque
  section donne sa commune et son département.

La carte des scores reste plus bas, séparée : elle répond à « combien », et une
carte qui répond à trois questions à la fois n'en répond bien à aucune.

**Une liste section par section** remplace le pavé de prose : section, commune,
département, paysage, ménages enquêtés. Les accès rapides et les chiffres
saillants restent.

## Deux détails de fabrication

**Les étiquettes se désempilent toutes seules.** Cinq sections se touchent dans
le coin sud-est ; posés à leur centre, deux noms devenaient illisibles. Les
étiquettes sont maintenant parcourues du nord au sud et décalées vers le bas
quand elles tomberaient sur la précédente — un décalage vertical se lit encore
comme « ce nom appartient à cette tache », ce qui n'est plus vrai d'un décalage
latéral.

**La projection est faite dans le module**, équirectangulaire avec la longitude
corrigée du cosinus de la latitude moyenne. À cette échelle et sous cette
latitude la déformation est invisible, et cela évite d'embarquer une
bibliothèque cartographique pour tracer deux contours.

## Vérifié

- **60 rendus** — 10 pages × 3 combinaisons de filtres × 2 langues — zéro
  exception, zéro clé de traduction brute ;
- page ouverte au navigateur : la vignette, la carte nommée avec ses dix
  étiquettes toutes lisibles, la liste des sections, et le récit APRI retrouvé
  en tête du Cadre de résilience.
