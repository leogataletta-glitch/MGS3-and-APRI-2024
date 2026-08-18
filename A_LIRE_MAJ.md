# Trois corrections — à pousser dans le MÊME commit

| Fichier | |
|---|---|
| `interventions_page.py` | anciennes pistes supprimées · activités et indicateurs de performance rendus visibles |
| `boucles_page.py` | l'exploration part des indicateurs les plus alarmants |
| `app.py` | ne charge plus les anciennes pistes |

**Les trois ensemble.** `app.py` n'importe plus `pistes_page` et appelle les
fiches sans argument : envoyé seul, il ne casserait rien, mais envoyer
`interventions_page.py` seul laisserait l'ancien `app.py` continuer à demander
les anciennes pistes. J'ai prévu le coup — la nouvelle page accepte l'argument
et l'ignore — mais le plus simple reste de pousser les trois d'un bloc.

## 1 · Anciennes pistes de travail — supprimées

Le volet replié du bas est retiré, et l'import qui l'alimentait aussi.

## 2 · Activités techniques / sociales et indicateurs de performance

**Ils étaient déjà là, mais illisibles** — un petit label gris en capitales au
milieu de la fiche, qui se perdait entre les paragraphes. C'est ma faute : le
protocole demande ces blocs, les afficher discrètement revient à ne pas les
afficher.

Ils portent maintenant :

- **deux encadrés côte à côte**, ⚙ *Activités techniques* en bleu et ◍
  *Activités sociales* en turquoise, avec filet de couleur et titre lisible ;
- **un encadré vert « ◎ Indicateurs de performance »** avec l'objectif de score
  en gros caractères — **+2,5 pt**, **+2,0 pt**, **+1,5 pt** selon la fiche —
  suivi du point de départ mesuré et du point visé : *4,0 / 10 → 6,5 / 10*.

Une précision utile : si vous regardez la plateforme en ligne, elle affiche
encore la version précédente tant que `interventions_page.py` n'est pas poussé
sur GitHub. Ce que je décris est dans le fichier que je viens de déposer.

## 3 · Les boucles partent maintenant des indicateurs les plus alarmants

Vous avez raison, et c'était l'erreur de conception de la page : elle
s'ouvrait sur l'eau, un levier confortable. Une boucle ne mérite d'être suivie
que si elle passe par ce qui est réellement en défaut.

En tête de la page, avant tout contrôle, un bloc **« Partir des indicateurs les
plus alarmants »** : les huit lignes les plus basses du référentiel, classées
par score croissant puis par pondération décroissante — à score égal, celle qui
pèse le plus dans l'indice passe devant. Chacune est un bouton qui devient le
levier ; le levier par défaut n'est plus l'eau mais **la sécurité alimentaire
(L108, 0/10, pondération 3,61)**, la ligne la plus alarmante que le graphe
sache atteindre.

Les huit : sécurité alimentaire (0/10) · électricité (0/10) · participation à
la préparation aux catastrophes (0/10) · achèvement du primaire (0/10) ·
comités locaux de gestion des risques (1/10) · capital social d'entraide
(1/10) · population sous 50 % du revenu médian (1/10) · combustibles propres
(1/10).

**Et ce que le modèle ne sait pas atteindre est nommé**, sous les huit boutons
plutôt que passé sous silence : macroplastiques en milieu marin (0/10),
couverture des aires protégées marines et côtières (0/10), couverture des aires
protégées terrestres (0/10), participation à la gouvernance locale (1/10).
Quatre indicateurs au plus bas pour lesquels le graphe ne pose aucune relation
— aucune boucle ne peut donc les traverser. C'est une limite du modèle causal,
pas une bonne nouvelle sur ces indicateurs.

## Vérifié

- **42 rendus complets** — 7 pages × 3 combinaisons de filtres × 2 langues —
  zéro exception, zéro clé de traduction brute ;
- pages ouvertes dans le navigateur : le bloc des alarmants avec son levier
  actif en bleu, les deux encadrés d'activités, l'encadré vert des indicateurs
  de performance ;
- le classement des alarmants recoupé directement sur `resultats.json`.
