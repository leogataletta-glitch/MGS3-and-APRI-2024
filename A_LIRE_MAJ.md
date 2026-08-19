# « Note aux bailleurs » — une page de restitution, entièrement calculée

## Deux fichiers, MÊME commit

| Fichier | |
|---|---|
| `note_bailleurs.py` | **nouveau** — la page entière, ses textes FR/EN, ses calculs |
| `app.py` | l'entrée « Note aux bailleurs » dans la colonne de gauche, après *Fiches d'intervention* |

Le fichier `i18n.py` n'a pas à être renvoyé : la page porte ses propres textes,
comme les modules récents.

## Ce que contient la page

**Quatre chiffres en tête** — 1 211 ménages sur 10 sections, l'indice global
4,54 / 10, les 15 indicateurs à 0 ou 1 sur 10 (21 % du poids du référentiel),
et l'effet modélisé du portefeuille complet : +0,335.

**1 · Ce que l'enquête établit — six constats.** Un par dimension, et *aucun
n'est choisi à la main* : pour chaque dimension, l'indicateur qui coûte le plus
à l'indice, c'est-à-dire sa pondération multipliée par les points qui lui
manquent sur dix. Chaque carte donne la valeur mesurée, la part non couverte,
le score, la part de l'écart total, la localité et le groupe les plus touchés,
la base de réponses, et l'explication de ce que compte exactement l'indicateur.

Ce que la règle donne aujourd'hui : électricité (17,3 %), participation à la
préparation aux catastrophes (4,6 %), macroplastiques, population sous 50 % du
revenu médian, capital social d'entraide, insécurité alimentaire (60,4 %).

> **Pourquoi une règle par dimension, et pas le classement brut ?** Le
> classement brut plaçait quatre constats sur six dans la même dimension —
> eau, électricité, assainissement, santé. Une note qui ne parle que de cela
> laisse croire que le reste va bien.

**2 · Ce que nous proposons — les huit fiches**, classées par l'effet que le
modèle causal leur donne sur l'indice. Chacune indique son effet, son horizon,
sa faisabilité, le levier et sa cible (« 4,0 → 6,5 / 10 »), les acteurs, et à
quel constat elle répond — directement, ou par la dimension.

**3 · Ce que le portefeuille complet déplace** — 4,54 → 4,87. Avec, dites en
toutes lettres, les trois limites : le gain vaut 6,1 % des points qui manquent
à l'indice ; la propagation n'atteint que 51 % du poids du référentiel ; et le
constat n° 5, le capital social d'entraide, n'est traité par aucune fiche.

**4 · Si le budget n'en couvre qu'une partie.** Le premier lot, ce sont les
fiches à la fois de faisabilité haute et d'horizon court — eau, carte
d'identité, comités de gestion des risques. **Trois fiches sur huit portent
64 % du gain modélisé du portefeuille.** C'est la phrase de la page.

**5 · Ce que cette note ne promet pas.** Cinq réserves : un effet simulé n'est
pas un impact évalué ; la cible de chaque levier est une hypothèse ; la
dimension environnementale est satellitaire et ne bouge pas dans l'horizon
annoncé ; la septième dimension n'a aucun indicateur ; les horizons qualifient
la nature du changement, pas un calendrier.

## Deux points où le calcul a corrigé ce que j'allais écrire

**« 2 700 ménages ».** Prendre la plus grande base du référentiel donnait
2 700, parce que certains indicateurs se comptent en personnes du foyer et non
en foyers. Le chiffre juste — 1 211 — est lu dans l'index des croisements,
c'est-à-dire l'effectif de l'enquête elle-même.

**« Le portefeuille déplace moins que la somme de ses fiches ».** C'est le cas
ordinaire, et je l'avais écrit d'avance. Le calcul dit l'inverse ici : les huit
effets s'additionnent *exactement*, parce que les huit leviers atteignent des
indicateurs disjoints. La page affiche donc l'une ou l'autre phrase selon ce
que le calcul trouve — et changera d'elle-même le jour où un levier sera
ajouté au graphe.

## Vérifié

- **66 rendus** — 11 pages × 3 combinaisons de filtres × 2 langues — zéro
  exception, zéro clé de traduction brute ;
- page ouverte au navigateur dans les deux langues : les quatre chiffres des
  cartes tiennent sur une ligne, les six constats, les huit fiches et les cinq
  réserves s'affichent en entier ;
- les chiffres de la page recoupent ceux des *Fiches d'intervention* : mêmes
  effets, même classement, même indice de départ (4,54).
