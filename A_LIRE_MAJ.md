# Refonte APRI — structure par dimension et nouvelle ergonomie

## Les 9 fichiers à mettre sur GitHub **dans le même commit**

| Fichier | Où | État |
|---|---|---|
| `app.py` | racine | remplacé |
| `i18n.py` | racine | remplacé |
| `accueil_page.py` | racine | **nouveau** |
| `dimension_page.py` | racine | **nouveau** |
| `synthese_page.py` | racine | **nouveau** |
| `environnement_page.py` | racine | remplacé |
| `ocb_page.py` | racine | remplacé |
| `croisement_page.py` | racine | remplacé |
| `A_LIRE_MAJ.md` | — | pour toi, pas pour le dépôt |

`i18n.py` passe en version **`2026-08-17-ergonomie`**.

Aucune donnée ne change : c'est une refonte de structure et de présentation.

---

## 1 · Une barre latérale sombre, comme la maquette

La navigation quitte la page et passe dans une **colonne verte fixe** à
gauche : logo APRI en haut, entrées groupées, langue en bas.

**Explorer les données** — Vue d'ensemble
**Les six dimensions** — I. Physique · II. Institutions · III. Environnement ·
IV. Économie · V. Social · VI. Humain
**Lire et agir** — Synthèse par groupe ou localité · Fiches actions
**Vérifier et télécharger** — Méthodologie · Téléchargements

Onze entrées en pavés occupaient un écran entier avant le premier chiffre. En
colonne, elles tiennent sans rien pousser vers le bas, et **l'onglet courant
reste visible où qu'on soit dans la page** — ce qu'un menu en haut de page perd
dès qu'on fait défiler.

Le bandeau principal est réduit de moitié et ne répète plus le titre : l'identité
APRI est portée par la colonne, la répéter volait un tiers d'écran.

**La septième dimension n'a pas d'entrée** — culturelle, identitaire et
psychologique, elle n'a aucun indicateur calculé. Elle reste listée dans la
méthodologie : une absence ne doit pas passer pour une inexistence.

---

## 2 · Une vraie page d'accueil

Le site s'ouvre dessus. Elle répond en un écran à « de quoi parle ce site, sur
quel territoire, avec quelles données, et qu'est-ce que ça donne ».

**Cinq tuiles de périmètre** — 10 sections communales, 2 départements,
**66 indicateurs calculés sur 128**, 1 211 ménages enquêtés, et le score APRI
d'ensemble : **4,54 / 10**.

**Quatre chiffres saillants**, choisis parce qu'ils commandent le reste :
72,8 % ont accès à une eau de boisson améliorée · 31,9 % à un assainissement
géré en sécurité · **17,3 % à l'électricité** · 60,4 % vivent une insécurité
alimentaire.

**Le classement des dix sections** en barres, et la même chose en carte à côté.
Trichet en tête à 5,41, Mouline en dernier à 4,09 — mais **l'écart dépasse à
peine un point sur dix**. Aucune section ne va bien ici, et la distance entre
elles compte moins que le niveau qu'elles partagent. C'est écrit sous le
graphique.

**Par où commencer** — quatre pistes de lecture vers les onglets qui comptent.

### Rien n'est écrit en dur

Tous les chiffres de cette page sont relus du fichier de résultats. Une page
d'accueil avec des nombres figés devient fausse à la première mise à jour, et
personne ne s'en aperçoit — c'est le pire défaut possible pour une vitrine.

---

## 3 · Six onglets de dimension, bâtis sur un seul module

Chacun montre le score pondéré de sa dimension, la part du cadre réellement
couverte, la carte des dix sections, le tableau de tous ses indicateurs triés
du score le plus bas, et — c'est le point de la refonte — **d'où vient chaque
chiffre**.

Chaque indicateur s'ouvre et donne la **question d'enquête** qui l'alimente,
mot pour mot et avec ses modalités, ou le **capteur satellitaire**, ou le
**registre** qui le débloquerait ; puis le barème publié et la note de méthode
avec ses réserves.

Un score sans sa source est un chiffre qu'on ne peut ni vérifier ni contester.

| Dimension | Score | Couverture |
|---|---:|---:|
| IV · Économie et sécurité alimentaire | 5,51 | 63 % |
| III · Environnement et écologie | 5,45 | 44 % |
| V · Social et communautaire | 5,18 | 54 % |
| II · Institutions et gouvernance | 4,83 | **93 %** |
| I · Physique et infrastructures | 2,93 | 63 % |
| VI · Humain | **1,40** | 31 % |

**Les indicateurs non calculés sont exclus de la moyenne, jamais comptés comme
des zéros.** Les assimiler à zéro punirait le territoire pour une lacune du
dispositif de mesure. La part couverte est affichée juste à côté — c'est elle
qui dit ce que vaut la moyenne. Le 1,40 de la dimension humaine repose sur
quatre indicateurs seulement.

L'onglet III prolonge sa page avec le détail satellitaire en onze indicateurs ;
l'onglet V avec les fiches des organisations de base.

---

## 4 · Synthèse par groupe ou localité

Un sélecteur : une **section communale** ou un **groupe** — femmes, hommes,
tranches d'âge, catégories socio-économiques. Puis un **graphique en haltères**
— point creux pour l'ensemble, point plein pour la cible, et le trait entre les
deux qui *est* l'écart — et les douze indicateurs où la cible décroche le plus,
puis les douze où elle est au-dessus.

**Deux précautions inscrites dans le module.** En lecture par groupe, seuls les
indicateurs d'enquête sont retenus : la forêt et la pluie ne varient pas selon
le sexe du répondant, les afficher avec un écart nul laisserait croire à une
égalité mesurée là où il n'y a qu'une absence de ventilation. Et l'écart n'est
jamais coloré en bien ou en mal — sur « ménages utilisant le charbon », être
au-dessus de la moyenne est mauvais, sur « accès à l'électricité » c'est bon.

---

## 5 · Ce qui a bougé de place

| Avant | Maintenant |
|---|---|
| Résultats descriptifs | dissous : chaque question vit sous l'indicateur qu'elle alimente |
| Croisement des questions | conservé, dans la méthodologie, en exploration libre |
| Indicateurs de résilience | dissous dans les six onglets de dimension |
| Résultats saillants | dissous dans l'accueil et la synthèse |
| Données environnementales | devenu l'onglet de la dimension III |
| Organisations de base | dans la dimension V |
| Pistes d'action | devenu « Fiches actions » |

**Rien n'a été supprimé.** Le croisement libre en particulier reste accessible :
une fonction qui marchait ne se supprime pas au motif qu'on a réorganisé la
façade.

---

## Ce qui reste à faire

**Les fiches actions** sont encore l'ancien contenu « pistes » — sept
hypothèses avec leurs chiffres, leurs acteurs et leurs risques. Elles marchent
mais ne sont pas rattachées aux dimensions ni aux sections. Dis-moi si tu veux
une fiche par dimension faible, ou une fiche par section avec ses trois
priorités.

**Les filtres actifs de la maquette** (le bloc « Département / Paysage / Sexe /
Âge » avec ses croix) ne sont pas encore là : ils supposent un filtrage
transversal de toutes les pages, ce qui est un chantier en soi. Aujourd'hui
chaque page a son propre sélecteur. Dis-moi si tu veux que je les remonte en
filtres globaux dans la barre latérale.
