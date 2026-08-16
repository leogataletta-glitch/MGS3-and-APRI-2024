# Mise à jour — l'onglet environnemental passe en sous-onglets

## Les 3 fichiers à mettre sur GitHub **dans le même commit**

| Fichier | Où | État |
|---|---|---|
| `app.py` | racine | remplacé |
| `i18n.py` | racine | remplacé |
| `environnement_page.py` | racine | remplacé |

`i18n.py` passe en version **`2026-08-16-onglets`**.

Aucun fichier de données ne change cette fois — seulement la présentation.

---

## 1 · Un sélecteur en tête, six sous-onglets

En haut de l'onglet, un seul menu : **Territoire affiché**. On choisit
« Ensemble des 10 sections » ou une section, et **tous les sous-onglets
suivent**. Plus besoin de rechoisir la section dans chaque bloc.

Les six sous-onglets :

| Sous-onglet | Ce qu'il contient |
|---|---|
| **Couverture forestière** | chiffres clés, chronologie 2001-2025, carte, tableau des dix |
| **Déforestation** | la grille de 300 m, curseur d'année |
| **Précipitations** | cumul annuel, normale, tableau des dix |
| **Sécheresse** | campagne de printemps, SPI, séquences sèches, installation |
| **Fiche par section** | tout ce que le satellite dit d'une section, sur une page |
| **Lacunes** | les indicateurs non calculés, groupés par source |

### Deux points de conception

**Les cartes gardent toujours les dix polygones**, même quand une section est
choisie. Une tache de déforestation se lit par rapport à ce qui l'entoure ;
isolée, elle ne dit plus rien. Ce sont les *points* de la grille qui se
restreignent à la section, pas le fond de carte.

**Quand une section est choisie, un rang s'affiche** sous chaque chiffre clé du
couvert forestier. Un taux de −0,51 %/an ne dit pas tout seul si la section est
parmi les plus atteintes ou parmi les plus épargnées ; « 5e sur 10 » le dit.

En vue d'ensemble, précipitations et sécheresse affichent la **moyenne non
pondérée des dix sections** — pondérer par la surface dirait le territoire
plutôt que l'échantillon, et mélangerait deux lectures.

---

## 2 · La fiche par section

Le sous-onglet réunit sur une page, pour la section choisie :

- **Couvert forestier** — forêt 2000, forêt 2025, perte, taux annuel, part due
  à Matthew, avec le rang parmi les dix
- **Où la perte est tombée** — nombre de cellules touchées, pire année, cellule
  la plus atteinte
- **Pluie, année civile** — normale, années récentes, extrêmes
- **Campagne de printemps** — normale, récent, date d'installation, campagnes
  sans départ net, séquence sèche, jours à 50 mm
- **Les indicateurs environnementaux scorés** pour cette section, avec leur
  valeur et leur note sur 10

En vue d'ensemble, la fiche affiche à la place un **tableau récapitulatif des
dix sections**, tous thèmes confondus — forêt, pluie, campagne, pluies
extrêmes.

---

## 3 · NDVI, NDMI, NDWI, NDTI — le script est prêt, il reste à le lancer

Tu m'as demandé de faire apparaître les quatre indices de végétation et d'eau.
Ils correspondent à quatre lignes de l'indice restées vides :

| Ligne | Indicateur | Ce que ça mesure |
|---|---|---|
| 33 | Stabilité de la végétation en saison sèche (**NDVI**) | vigueur du couvert : ce qui reste vert quand il ne pleut plus |
| 34 | Humidité de la végétation et des sols (**NDMI**) | eau contenue dans la plante et le sol — chute **avant** le NDVI, c'est un signal précoce |
| 35 | Stabilité des eaux de surface (**NDWI**) | eau libre : sources, mares, cours d'eau qui tiennent en saison sèche |
| 63 | Turbidité de l'eau (**NDTI**) | charge en sédiments — ce que l'érosion emporte des versants vers l'eau |

**Ce sont eux qui ferment la boucle.** Le tableau de bord montre aujourd'hui une
forêt qui recule, une campagne de printemps à 83 % de sa normale et des averses
qui s'intensifient. Le NDMI dira si le sol s'assèche vraiment entre deux
saisons ; le NDTI dira si l'érosion attendue arrive bien dans l'eau. Perception
déclarée, pluie mesurée, et maintenant état du sol : trois sources
indépendantes sur la même question.

### La saison sèche est calculée, pas supposée

J'ai pris les 45 ans de CHIRPS déjà exportés pour trouver le trimestre le plus
sec. C'est **janvier-février-mars**, 120 mm au total, loin devant les autres :

```
jan  40   fév  42   mar  38   avr  89   mai 141   jun  89
jul  84   aoû 134   sep 164   oct 202   nov 105   déc  43
```

C'est aussi le moment le plus utile à observer : la végétation y est à son plus
stressé, juste avant les semis de printemps. Ce qui reste vert en mars est ce
qui tient sans pluie.

### Ce que tu dois faire

1. Ouvre `satellite\gee_indices_vegetation.js` sur ton bureau, copie tout.
2. Sur https://code.earthengine.google.com, efface l'éditeur, colle, **Run**.
3. Regarde la console : elle affiche le **nombre d'images retenues** par saison
   sèche. Quelques dizaines par an, c'est bon. Moins de cinq une année donnée,
   dis-le-moi — cette saison-là sera trop nuageuse pour être fiable.
4. Onglet **Tasks** → **Run** sur `IRLA_indices_vegetation`.
5. Envoie-moi `indices_vegetation_sections.csv`.

Une carte NDVI s'affiche aussi dans l'aperçu, tu verras tout de suite où le
couvert tient et où il a lâché.

### Une réserve que je dois signaler d'avance

Sentinel-2 niveau 2A commence en 2017, et les premières années sont maigres en
images exploitables sous les tropiques. La période de référence sera donc
courte — trois saisons sèches — là où une climatologie en demanderait trente.
**Ces quatre indicateurs diront un changement récent, pas une tendance
longue.** C'est une limite de la source, pas du calcul ; elle sera écrite dans
la note de chaque indicateur, comme pour la résolution de CHIRPS.

---

## Ce qui reste après ça

**28 indicateurs environnementaux** non calculés au lieu de 32. Ensuite, le
plus accessible : MODIS pour la température de surface (lignes 36, 41, 42).
