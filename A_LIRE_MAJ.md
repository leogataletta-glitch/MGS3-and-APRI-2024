# Analyse détaillée — ajoutée EN TÊTE de « Analyse des résultats »

## Deux fichiers, MÊME commit

| Fichier | |
|---|---|
| `questions_resultats.py` | **nouveau** — les deux nouvelles sections |
| `dimension_page.py` | les appelle avant l'existant |

Il s'appuie aussi sur `croisement_moteur.py`, livré au lot précédent : si ce
dernier n'est pas encore poussé, envoyez-le avec.

**Rien n'a été retiré, remplacé ni réorganisé.** Les onglets *Indicateurs* et
*Résultats du questionnaire*, la carte, les quatre chiffres clés, le radar,
l'accordéon et le tableau comparatif sont intacts, à leur place, sous les
nouvelles sections.

## Ce qui s'ajoute, dans l'ordre demandé

**1 · Résultats des questions — effectifs absolus.** Une ligne par question de
la dimension : question · réponse de référence · effectif · part · meilleur
groupe · pire groupe · meilleure localité · pire localité. Un filtre de
population au-dessus — tous les répondants, sexe, classe d'âge, groupe
socio-économique, paysage, localité — et une recherche.

**2 · Comparaison visuelle.** Une question au choix, la ou les réponses
comparées, et des barres classées par groupe **ou** par localité, avec le trait
pointillé de l'ensemble et les deux extrémités en vert et rouge.

**3 · Indicateurs de résilience.** Indicateur · dimension · source/questions ·
pondération · score · meilleur groupe · pire groupe · meilleure localité · pire
localité. La colonne source nomme la question d'enquête dont l'indicateur est
tiré — c'est la traçabilité entre les deux tableaux.

**4 · Filtres, y compris combinés.** Un interrupteur « combiner plusieurs
filtres » ouvre cinq sélecteurs simultanés : femmes + montagne + Cat C.

**5 · Comparaison Groupe / Localité** pour un indicateur, en barres.

## Trois choses que je dois signaler

**« Meilleur » suppose un sens, et je ne l'invente pas.** Un pourcentage élevé
n'est pas une bonne nouvelle en soi : *80 % cuisinent au charbon* est mauvais,
*80 % ont l'eau améliorée* est bon. Le sens n'est connu que là où la question
**alimente un indicateur**, qui porte son barème. Ces lignes-là disent
« meilleur » et « pire », en vert et rouge. Les autres portent un **○** et
leurs colonnes se lisent « plus haut / plus bas », en encre neutre. Deviner le
sens des autres aurait donné un tableau qui a l'air complet et se trompe une
fois sur deux.

**Un défaut trouvé et corrigé en route.** La première version affichait
« Trichet 123,3 % » sur la source d'eau de boisson. Plusieurs questions
acceptent plusieurs réponses — un foyer peut cocher deux sources améliorées —
et additionner les effectifs des modalités le compte deux fois. Les parts sont
maintenant calculées par **union exacte** sur les bits de `croisement.npz` :
chaque foyer est compté une fois. Contrôle passé sur cent parts, plus aucune
au-dessus de 100 %.

**Les scores combinés sont recalculés, et c'est écrit.** Aucun fichier ne porte
le score de « femmes × montagne × Cat C » : le référentiel publie
vingt-deux découpages, pas leurs croisements. Sous une combinaison, les scores
sont donc recalculés par le moteur de croisement — possible pour les 25
indicateurs dont la définition se reproduit exactement, soit 37 % du poids du
référentiel — et un avertissement le dit au-dessus du tableau. Sans
combinaison, les scores affichés sont **ceux publiés**, non recalculés.

## Vérifié

- **54 rendus** — 9 pages × 3 combinaisons de filtres × 2 langues — zéro
  exception, zéro clé de traduction brute ;
- les six dimensions ouvertes une à une dans les deux langues : deux d'entre
  elles tombaient au premier essai, sur une question sans indicateur associé —
  corrigé, la garde précède maintenant l'accès ;
- page ouverte au navigateur : les deux tableaux, la traçabilité
  « alimente la ligne N », les repères ○, et les barres par groupe et par
  localité.
