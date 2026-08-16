# Mise à jour — la couverture forestière entre dans l'indice

## Les 6 fichiers à mettre sur GitHub **dans le même commit**

| Fichier | Où | État |
|---|---|---|
| `app.py` | racine | remplacé |
| `i18n.py` | racine | remplacé |
| `saillants_page.py` | racine | remplacé |
| `data/resultats.json` | `data/` | remplacé |
| `data/ventilation.json` | `data/` | remplacé |
| `data/saillants.json` | `data/` | remplacé |

> `i18n.py` passe en version `2026-08-16-foret2`.

Si `resilience_page.py` n'est pas encore poussé depuis la livraison précédente,
ajoute-le : il porte la correction d'unité (« des ménages » n'a pas de sens sous
un taux de déboisement).

---

## Le résultat

L'indicateur **54, « Taux de changement du couvert forestier »**, était vide.
Il est maintenant calculé, cartographié, et compte dans le score final.

| Section | Forêt 2000 | Perte | Taux/an | Score | Dont 2016-18 |
|---|---|---|---|---|---|
| Barbois | 1 008 ha | 224 ha | −0,99 % | 4 | 92 % |
| Trichet | 783 ha | 131 ha | −0,72 % | 5 | **99 %** |
| Dalmette | 609 ha | 98 ha | −0,68 % | 5 | **2 %** |
| Mouline | 4 776 ha | 663 ha | −0,59 % | 5 | 74 % |
| Débouchette | 240 ha | 31 ha | −0,52 % | 5 | 60 % |
| Dumont | 339 ha | 43 ha | −0,51 % | 5 | 40 % |
| Beaulieu | 521 ha | 54 ha | −0,43 % | 6 | 68 % |
| Anse à Drick | 749 ha | 68 ha | −0,37 % | 6 | 79 % |
| Quentin | 648 ha | 25 ha | −0,15 % | 7 | 62 % |
| Blactote | 1 039 ha | 38 ha | −0,14 % | 7 | **4 %** |
| **Ensemble** | **10 713 ha** | **1 373 ha** | **−0,54 %** | **5** | **71 %** |

## Ce que la donnée dit, et qui n'était pas prévu

**71 % de la perte forestière de vingt-cinq ans tombe en 2016-2018** — l'ouragan
Matthew et ses suites. Sur la seule année 2016 : 686 hectares, la moitié du
total. Hors ce choc, le taux passe de **−0,54 à −0,15 % par an**.

Et le contraste entre sections est le vrai résultat :

- **Trichet perd 99 % de sa forêt à la tempête** et quasiment rien au
  défrichement. Son taux chronique est de −0,00 % par an.
- **Dalmette et Blactote, à peine touchées par Matthew** (2 % et 4 %), perdent du
  couvert régulièrement, année après année. Dalmette est à −0,66 % par an de
  déboisement chronique — le plus élevé du lot.

Ces deux situations ont des scores voisins et n'appellent pas la même réponse.
L'une relève de la reconstruction post-cyclone, l'autre d'une pression continue
sur la ressource — celle que le charbon de bois alimente, et que l'enquête
ménage documente par ailleurs.

Le taux retenu pour le score est **celui qui inclut le cyclone** : la forêt a
réellement été perdue. Mais le taux hors choc figure dans `foret.json`, dans la
note de l'indicateur, et dans le nouveau constat.

## Un neuvième constat dans l'onglet Constats saillants

Il porte ce résultat, avec le contraste Trichet / Dalmette.

## Une correction dans la fiche par profil

Le vert et le rouge des pastilles d'écart suggéraient « bonne » et « mauvaise »
nouvelle. Résultat : un meilleur accès à l'électricité s'affichait en rouge. La
pastille est désormais **neutre** — elle donne la direction et l'ampleur de
l'écart, pas son interprétation, que l'application n'est pas en mesure de
connaître pour toutes les figures.

## Les réserves, à porter dans toute publication

**Hansen mesure une perte de couvert arboré, pas une déforestation au sens
juridique.** Ce constat le montre de façon spectaculaire : la moitié de la
« déforestation » du territoire est un ouragan.

**Le gain n'est renseigné que jusqu'en 2012.** Le taux net est donc prudent : la
repousse post-Matthew, considérable sur un territoire tropical, n'est pas vue.
C'est la limite la plus gênante ici, et elle joue dans le sens du pessimisme.

**Seuil de couvert retenu : 30 %.** À aligner sur la définition du projet si elle
existe. Changer ce seuil change tous les chiffres du tableau ci-dessus.

## Prochaine étape possible

**CHIRPS** pour les indices de précipitation (lignes 43, 45, 46) : série
pluviométrique longue, calcul direct, et aucun arbitrage comparable au seuil de
couvert. Le même script Earth Engine, adapté.
