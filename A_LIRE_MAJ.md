# « Le territoire » — une carte interactive à couches, et les deux cartes QGIS

## Les fichiers à envoyer sur GitHub, TOUS DANS LE MÊME COMMIT

| Fichier | Où | |
|---|---|---|
| `carte_localisation.py` | **racine** | **nouveau** — la carte interactive et son gestionnaire de couches |
| `territoire_page.py` | **racine** | modifié — appelle la carte, puis les deux cartes QGIS |
| `carte_localisation.json` | **`data/`** | **nouveau** — toutes les couches vectorielles, 528 ko |
| `leaflet.js` | **`data/`** | **nouveau** — le moteur de carte, 144 ko |
| `leaflet.css` | **`data/`** | **nouveau** — sa feuille de style, 15 ko |
| `carte_paysages.jpg` | **`data/`** | **nouveau** — la carte des paysages pilotes, nettoyée |
| `carte_entretiens.jpg` | **`data/`** | **nouveau** — la carte des points d'entretien |

`app.py` n'a pas changé depuis la livraison précédente. Si vous ne l'avez pas
encore envoyé avec `note_bailleurs.py`, faites-le maintenant.

> Les cinq fichiers de `data/` sont des binaires ou de gros JSON : sur GitHub,
> ouvrez le dossier `data`, « Add file → Upload files », et déposez-les
> ensemble. Le glisser-déposer accepte les cinq d'un coup.

## Ce que fait la carte interactive

Un fond de carte au choix — **plan, topographique, satellite, sobre** — et
**treize couches** qu'on allume et éteint une par une depuis le panneau de
droite, groupées en catégories repliables :

| Groupe | Couches |
|---|---|
| Territoires étudiés | sections communales étudiées (10), paysage pilote de la Grand'Anse, villes-repères |
| Points d'entretien | paysage littoral (530), paysage montagne (665) |
| Limites administratives | départements (3), communes (12), limites nationales |
| Infrastructure | routes principales (310), routes secondaires (486) |
| Relief et environnement | ombrage du relief, cours d'eau (351), aires protégées (9) |

**Tout afficher**, **Tout masquer** et **Emprise initiale** sont en haut du
panneau. Chaque objet est cliquable : un point d'entretien donne son numéro, sa
section et son paysage ; une section donne sa commune et son département ; une
commune, une aire protégée, une ville donnent leur nom.

**Les 1 195 points d'entretien sont les positions exactes de l'échantillon
tiré**, séparés en deux couches pour qu'on puisse comparer littoral et
montagne en éteignant l'une des deux. Leur popup ne porte que le numéro
d'ordre, la section et le paysage : les fichiers d'échantillon ne contiennent
ni nom, ni téléphone, ni enquêteur, et rien de tel n'est embarqué dans la page.

Aucun score, aucun indicateur, aucun pourcentage sur cette carte. Les couleurs
y désignent des familles d'objets, jamais des valeurs.

## Trois décisions techniques qui se voient

**Leaflet voyage avec le site.** Il est d'usage de l'appeler sur un CDN ; ici
il est dans `data/`. Une connexion haïtienne peut atteindre le serveur de
l'application sans atteindre `unpkg.com`, et une carte dont le moteur manque
n'affiche rien du tout, pas même un fond. 160 ko, une fois. Si les deux
fichiers manquaient du dépôt, le code retombe automatiquement sur le CDN.

**Les routes de desserte locale ne sont pas une couche vectorielle.** Elles
sont des milliers, elles auraient pesé trois mégaoctets, et le fond de plan
OpenStreetMap les affiche déjà. Ce sont les routes principales et secondaires
qui sont embarquées, parce qu'on veut pouvoir les éteindre et les interroger.

**L'ombrage du relief est en tuiles, pas en vecteur.** Il se lit à toutes les
échelles et ne pèse rien dans la page.

## Les deux cartes QGIS, sous la carte interactive

Elles portaient leur légende à l'intérieur de l'image : vingt-deux pastilles
d'altitude sur deux colonnes, seize aires protégées en petit corps, le tout
posé sur la mer. À l'écran, ces panneaux tombaient à 40 % de leur taille
d'impression et devenaient illisibles.

Ils ont donc été **effacés de l'image** — la mer sous eux était unie, elle a
été reconstituée pixel par pixel — et **refaits en HTML**, où ils suivent la
largeur de la page. Trois changements de fond, pas seulement de taille :

- les **seize aires protégées** passent d'une colonne de seize lignes à quatre
  colonnes de quatre : on les balaie du regard au lieu de les lire ;
- l'**échelle d'altitude** passe de vingt-deux pastilles à **un dégradé
  continu** avec cinq repères chiffrés. Vingt-deux paliers de 150 m ne se
  distinguent pas à l'œil, et personne ne cherche « entre 1 350 et 1 500 » ;
  ce qu'on veut savoir, c'est où est la montagne. Les dix-huit teintes du
  dégradé sont relevées sur la légende de la carte elle-même ;
- les **symboles** tiennent sur une rangée, avec leur figuré exact : trait
  tireté pour les départements, cercle blanc pour la capitale, carré plein
  pour les points d'entretien.

Le cartouche « PAYSAGES PILOTES DU GRAND SUD » est resté sur l'image : il est
posé sur un morceau de côte et d'île, et l'effacer aurait demandé d'inventer
du terrain.

## D'où viennent les données

De vos propres couches, dans `Layers de la carte relief haïti` : sections
étudiées, communes, aires protégées, paysage pilote, villes, et les dix-neuf
fichiers `PS_<paysage>_<section>_CSV.csv` de l'échantillon. Les routes et les
cours d'eau viennent d'OpenStreetMap, emprise du Grand Sud. Tout est en WGS 84.

Deux réserves honnêtes : la couche des aires protégées ne contient que **neuf
polygones valides** (les autres enregistrements sont vides dans le fichier) —
les seize aires numérotées de la carte imprimée viennent d'ailleurs, et je ne
les ai pas retrouvées en vectoriel ; et le **paysage pilote du Sud** n'a pas
de fichier dans le dossier, seul celui de la Grand'Anse s'y trouve. Si vous me
donnez ces deux couches, elles s'ajoutent en dix minutes.

## Vérifié

- **66 rendus** — 11 pages × 3 combinaisons de filtres × 2 langues — zéro
  exception ;
- carte ouverte au navigateur : les treize couches s'allument et s'éteignent,
  les comptes affichés correspondent aux objets chargés (530 + 665 = 1 195
  points), les popups répondent, l'emprise se rétablit ;
- les deux images vérifiées après nettoyage : la mer est continue là où la
  légende était posée.
