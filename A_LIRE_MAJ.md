# « Cadre de résilience » — trois strates au lieu d'un mur

## Un seul fichier

| Fichier | Où |
|---|---|
| `cadre_page.py` | racine du dépôt |

## Le principe

**Strate 1 — comprendre en trente secondes.** Quatre cartes, un schéma, trois
attributs, trois sources. Rien à lire d'affilée.

**Strate 2 — explorer.** Les sept dimensions avec leur poids réel et leur
couverture, puis la chaîne de calcul en quatre étapes.

**Strate 3 — approfondir.** Six volets **fermés par défaut**.

## Strate 1

**Les quatre cartes de tête** répondent aux quatre questions dans l'ordre où on
les pose :

| | |
|---|---|
| Ce que mesure APRI | la capacité à anticiper, absorber, s'adapter |
| Ce que l'indice saisit | les capacités détenues **avant** le choc, sur 7 dimensions |
| Comment il est mesuré | un score 0–10, 128 indicateurs, trois sources |
| **Ce qu'il ne mesure PAS** | ni les dommages après coup, ni une prévision |

La quatrième est traitée comme les trois autres — carte pleine, même taille —
et non en note de bas de page. Une limite qu'on lit après coup n'a jamais
empêché personne de se tromper. Elle porte un fond légèrement gris pour qu'on
voie d'un coup d'œil qu'elle dit le contraire des trois autres.

**« APRI en un coup d'œil »** : `3 attributs › 7 dimensions › 128 indicateurs ›
score 0–10`. Les quatre chiffres sont **comptés dans `resultats.json`**, pas
écrits à la main : 7 parce que le référentiel compte sept dimensions, 128 parce
qu'il liste 128 indicateurs, 66 scorés à ce jour. Si un indicateur est calculé
demain, le schéma le dit de lui-même.

**Les trois attributs** — Anticiper, Absorber, S'adapter — sont maintenant
trois cartes égales avec icône et une phrase chacune, au lieu de trois filets
de couleur.

**« Comment l'indice est construit »** : Enquête ménage › Données géospatiales
› Évaluation communautaire, chacune avec sa phrase et son chiffre — 1 211
questionnaires, 25 ans d'imagerie, 34 organisations recensées. Les deux
chiffres d'effectif sont lus dans les fichiers.

## Strate 3 — ce qui est replié, et où c'est passé

| Volet | Ce qu'il contient |
|---|---|
| Pourquoi APRI ? | le point de départ et la portée, les deux paragraphes du récit |
| Que mesure exactement APRI ? | le paragraphe « ce que mesure l'indice » + les trois cartouches (résilience générale, ex ante, échelle 0–10) |
| Sources de données et méthodologie | le paragraphe de construction + le plan de sondage complet : 4 chiffres clés, 4 critères de stratification, la note de tirage |
| Ce qu'APRI ne peut pas dire | les quatre limites — circularité, absence de validation empirique, mesure statique, cadrage et non prévision |
| Le second volet — boucles causales | les 4 étapes, la lecture d'une boucle, le schéma R/B, le piège du « positif » |
| Le document méthodologique complet | inchangé |

**Rien n'a été supprimé.** Chaque paragraphe, chaque chiffre et chaque schéma
de l'ancienne page est encore là — un cran plus bas. Le seul changement de
fond est que le récit d'origine, qui ouvrait la page sur quatre paragraphes,
est réparti dans les trois premiers volets selon ce qu'il explique.

## Vérifié

- **66 rendus** — 11 pages × 3 combinaisons de filtres × 2 langues — zéro
  exception, zéro clé de traduction brute ;
- page ouverte au navigateur, en français et en anglais : les quatre cartes
  tiennent sur une seule rangée (elles débordaient de douze pixels à leur
  première taille), les six volets sont fermés à l'ouverture, la hauteur de
  page passe de 4 300 à 2 764 pixels.
