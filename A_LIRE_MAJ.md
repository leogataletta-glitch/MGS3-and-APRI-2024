# Mise à jour — deux nouveaux onglets : constats saillants et pistes d'action

## Les 7 fichiers à mettre sur GitHub **dans le même commit**

| Fichier | Où | État |
|---|---|---|
| `app.py` | racine | remplacé |
| `i18n.py` | racine | remplacé |
| `saillants_page.py` | racine | **nouveau** |
| `pistes_page.py` | racine | **nouveau** |
| `ocb_page.py` | racine | remplacé |
| `data/saillants.json` | `data/` | **nouveau** |
| `data/pistes.json` | `data/` | **nouveau** |

> `i18n.py` passe en version `2026-08-16-saillants-pistes`. `app.py` la vérifie
> au démarrage : si l'un des deux manque, un bandeau rouge le dit.

Le tableau de bord compte désormais **huit onglets**, disposés en deux rangées
de quatre. La disposition s'adapte toute seule au nombre d'onglets.

---

## 1 · Onglet « Constats saillants »

Trois niveaux de lecture, du plus synthétique au plus brut.

**Les quatre chiffres les plus durs**, en tête : participation à la préparation
aux catastrophes **4,6 %**, accès à l'électricité **17,3 %**, insécurité
alimentaire sévère **60,4 %**, achèvement du primaire chez les adultes
**16,5 %**. Ce sont les quatre plus bas scores de l'indice, pas une sélection.

**Huit constats thématiques**, chacun avec un texte qui relie les chiffres entre
eux : alimentation, énergie, préparation aux catastrophes, eau et assainissement,
éducation, capital social, économie, agriculture.

Le plus net : **le Grand Sud est frappé par les cyclones et ne s'y prépare pas**.
95 % n'ont jamais fait d'exercice de simulation, 90 % n'ont reçu aucune
formation, 83 % ignorent où se mettre à l'abri. Mais l'alerte, elle, fonctionne —
la moitié a reçu un message radio au dernier cyclone et trois quarts d'entre eux
l'ont compris et pris en compte. La partie coûteuse marche déjà ; c'est l'aval
qui manque.

**Une fiche par profil ou par section communale.** Tu choisis « Femmes »,
« Moins de 25 ans », « Catégorie A » ou une section, et tu obtiens les mêmes
chiffres avec **l'écart à la moyenne d'ensemble** — parce qu'un chiffre seul ne
dit rien. Quelques écarts qui ressortent :

- **Catégorie A** : 76,6 % ont sauté un repas, contre 51,4 % en catégorie C.
- **Montagne** : 72,2 % ont sauté un repas, contre 60,2 % sur le littoral.
- **Femmes** : 69,4 % ont sauté un repas contre 64,4 % des hommes ; 4,0 % ont
  participé à une action de préparation contre 5,2 % des hommes.

**La liste automatique**, en bas : tous les indicateurs scorés du plus bas au
plus haut, plus les réponses qui concernent au moins 60 % des ménages. Aucun tri
éditorial — si les données changent, la liste suit.

Tous les chiffres sont **recalculés** par `pipeline/compute_saillants.py` depuis
le cache d'enquête. Aucun n'est écrit en dur, et chaque figure nomme la question
et les modalités dont elle est tirée.

---

## 2 · Onglet « Pistes d'action »

Cadré comme tu l'as choisi : **hypothèses de travail pour l'atelier, pas
recommandations**. L'article est explicite et je m'y tiens — les points de levier
se construisent en atelier participatif à partir de diagrammes causaux, et
chacun devient une fiche d'action. Un bandeau orange le dit en tête de page.

Sept pistes, chacune avec le format de la fiche d'action de l'article : le
raisonnement, **les chiffres d'enquête qui la motivent** (repris automatiquement
de l'onglet Constats), **les acteurs** que cela mobiliserait, et **ce qui
pourrait mal tourner**.

Ce dernier point n'est pas décoratif : l'article avertit qu'une intervention
isolée déplace la vulnérabilité au lieu de la réduire. Restreindre le charbon
sans remplacer le revenu retire un moyen de subsistance aux plus pauvres. Des
exercices de simulation sans abris en état apprennent aux gens à se rendre
quelque part qui ne peut pas les recevoir.

La septième piste porte sur l'évaluation elle-même : sur 128 indicateurs, 51
sont scorés, et les autres manquent pour des raisons réparables — imagerie
satellitaire jamais calculée, formulaires institutionnels sans identifiant de
section, dénominateurs de population absents.

---

## 3 · Fiche OCB — le bloc « mission » retiré

Tu as raison, l'enquête ne demande nulle part sa mission à une organisation. Le
bloc est supprimé. Les domaines couverts par les partenariats ont rejoint la
partie « avec qui elle travaille », où ils sont à leur place.

**Sur ta question « tu n'as rien d'autre ? »** : j'ai vérifié colonne par
colonne. Le questionnaire OCB compte 37 colonnes de fond, et la fiche les
utilise **toutes**. Il n'y a ni date de création, ni nombre de membres, ni
budget, ni liste d'activités — le formulaire ne les demande pas. Pour des fiches
plus riches, il faut ajouter ces questions au questionnaire.

---

## Rappel

Dépôt **privé**, mot de passe dans `APP_PASSWORD`, aucun identifiant direct dans
les fichiers téléchargeables.
