# Mise à jour — les organisations communautaires (OCB) entrent dans le tableau de bord

## Les 7 fichiers à mettre sur GitHub **dans le même commit**

| Fichier | Où | État |
|---|---|---|
| `app.py` | racine | remplacé |
| `i18n.py` | racine | remplacé |
| `ocb_page.py` | racine | **nouveau** |
| `telechargements_page.py` | racine | remplacé |
| `data/ocb.json` | `data/` | **nouveau** |
| `data/resultats.json` | `data/` | remplacé |
| `data/ventilation.json` | `data/` | remplacé |

Les sept vont ensemble : les scores de `resultats.json` et de `ventilation.json`
comptent désormais les indicateurs OCB, et un commit partiel afficherait des
scores incohérents d'un onglet à l'autre.

## Ce qui change

**Un 6e onglet, « Tissu associatif ».** Les 34 fiches d'organisations, avec les
chiffres clés, une carte à dix indicateurs au choix, le classement de tous les
indicateurs, et la table des organisations filtrable par section.

**Dix nouveaux indicateurs dans l'indice**, rattachés aux dimensions II
(institutionnelle et gouvernance) et V (sociale et communautaire) :

| Ligne | Indicateur | Toutes organisations |
|---|---|---|
| 201 | Engagées dans un partenariat | 73,5 % |
| 202 | Contribuant à des initiatives privées ou de la société civile | 73,5 % |
| 203 | En relation avec les autorités communales | 55,9 % |
| 204 | Rendant compte à une institution extérieure | 50,0 % |
| 205 | Disposant d'une cartographie des acteurs | 25,9 % |
| 206 | Ayant reçu un appui extérieur | 72,7 % |
| 207 | Reliées à des ONG internationales | 48,1 % |
| 208 | Comptant une femme à un poste de direction | 91,2 % |
| 209 | Comptant un jeune de 18-30 ans à la direction | 64,7 % |
| 210 | Densité d'organisations recensées | 34 au total |

**Un 7e téléchargement**, avec les 34 fiches et les indicateurs par section.

## Trois choix de méthode, à valider

**1. Les indicateurs OCB pèsent dans le score final.** C'est ce que tu as
demandé. Le score final par section bouge en conséquence :

| Section | Avant | Après |
|---|---|---|
| Anse à Drick | 3,69 | 4,31 |
| Barbois | 4,21 | 5,04 |
| Dumont | 4,26 | 4,95 |
| Débouchette | 3,69 | 3,71 |
| Mouline | 3,32 | 3,48 |
| Quentin | 3,13 | 4,04 |
| Beaulieu | 4,25 | 3,88 |
| Blactote | 4,04 | 3,95 |
| Dalmette | 4,23 | 4,13 |
| Trichet | 4,78 | 5,04 |

Le biais que je signalais est réel et visible : Blactote et Dalmette n'ayant
aucune organisation recensée, leur score repose sur **42 indicateurs contre 51**
pour les autres sections. Un bandeau orange le dit en haut de l'onglet. À noter
que la densité, elle, vaut bien zéro pour ces deux sections — c'est une mesure,
pas une absence de mesure — et elle tire leur score vers le bas.

**2. Pondération.** Ces indicateurs ne figurent pas dans la table théorique IRLA,
donc aucune pondération n'est publiée pour eux. Je leur ai attribué la
pondération **moyenne de leur dimension d'accueil** — 2,37 pour la dimension II,
2,17 pour la dimension V. Autrement dit : ni plus ni moins importants que ce que
la théorie place déjà dans ces dimensions.

**3. Barème.** Faute de barème comparatif international, j'ai retenu une échelle
linéaire par décile : 0-10 % vaut 0, 90-100 % vaut 10. C'est lisible et ça ne
prétend rien d'autre qu'une proportion. À remplacer si un barème de référence
apparaît.

## Ce que j'ai vérifié

Les dix indicateurs ont été recomptés directement sur le fichier Excel source,
indépendamment du code de calcul : **zéro écart**. Les six onglets ont été testés
dans les deux langues.

Le **nom de la localité n'est présent dans aucun fichier déployé** — c'est une
donnée identifiante, traitée comme le nom du répondant de l'enquête ménage. En
revanche, le nom des organisations est conservé : ce sont des institutions, pas
des personnes. Deux d'entre elles portent un nom de lieu dans leur raison sociale
(« …coordonnée de Belance », « …de Roche-à-Bateau ») ; dis-moi si tu préfères
que je masque aussi les noms d'organisations.

## Ce qui reste en attente

Les trois formulaires CASEC, district scolaire et santé attendent toujours
l'attribution des sections communales. Ce sont eux qui portent la mortalité
maternelle et néonatale, la densité de personnel soignant, les homicides et
l'eau dans les écoles — une vingtaine d'indicateurs aujourd'hui vides.

## Rappel

Dépôt **privé**, mot de passe dans `APP_PASSWORD`, aucun identifiant direct dans
les fichiers téléchargeables.
