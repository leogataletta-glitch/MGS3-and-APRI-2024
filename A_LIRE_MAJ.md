# Mise à jour — les quatre indices Sentinel-2 sont calculés

## Les 6 fichiers à mettre sur GitHub **dans le même commit**

| Fichier | Où | État |
|---|---|---|
| `app.py` | racine | remplacé |
| `i18n.py` | racine | remplacé |
| `environnement_page.py` | racine | remplacé |
| `data/resultats.json` | `data/` | remplacé |
| `data/ventilation.json` | `data/` | remplacé |
| `data/indices_vegetation.json` | `data/` | **nouveau** |

`i18n.py` passe en version **`2026-08-16-ndvi`**.

---

## Le résultat, sans détour

L'export a bien marché : sept saisons sèches, 40 à 47 images par saison, dix
sections. **Mais seuls deux des quatre indicateurs méritent d'entrer dans
l'indice.** Je ne les ai pas tous scorés, et je dois t'expliquer pourquoi —
c'est une décision que tu peux renverser, mais pas sans la connaître.

| Ligne | Indicateur | Statut | Score d'ensemble |
|---|---|---|---|
| 33 | Végétation en saison sèche (NDVI) | **scoré** | 10 |
| 34 | Humidité végétation et sols (NDMI) | **scoré** | 10 |
| 35 | Eaux de surface (NDWI) | calculé, **non scoré** | — |
| 63 | Turbidité (NDTI) | calculé, **non scoré** | — |

**57 indicateurs scorés sur 128.** Le score d'ensemble monte de **4,38 à 4,57**,
gain réparti de +0,12 (Quentin) à +0,24 (Blactote).

---

## 1 · Ce que le NDVI et le NDMI disent

**Le couvert de saison sèche ne s'est pas dégradé entre 2019 et 2025.** Il a
même légèrement progressé partout sauf à Quentin (−1,1 % de NDVI). C'est un
résultat, pas une absence de résultat : sur un territoire qui perd sa forêt,
l'infrastructure verte permanente — celle qui reste verte en mars, arbres et
haies — tient.

| Section | NDVI | NDMI | | Section | NDVI | NDMI |
|---|---:|---:|---|---|---:|---:|
| Blactote | +6,0 % | +41,9 % | | Dalmette | +4,9 % | +15,0 % |
| Beaulieu | +5,4 % | +66,3 % | | Débouchette | +4,1 % | +6,0 % |
| Barbois | +5,1 % | +22,2 % | | Trichet | +2,6 % | +1,2 % |
| Anse à Drick | +4,3 % | +20,9 % | | Dumont | +1,9 % | +3,8 % |
| Mouline | +1,1 % | −2,0 % | | **Quentin** | **−1,1 %** | **−16,1 %** |

**Quentin est la seule section qui recule sur les deux.** C'est aussi celle dont
la séquence sèche de printemps s'est le plus allongée (22 → 27 jours). Deux
sources indépendantes, même section, même direction : c'est le signal le plus
solide de cette livraison.

**2021 est le creux du NDVI dans 7 sections sur 10** — la même année que la
pire campagne de printemps identifiée par CHIRPS. Le satellite optique et le
satellite pluviométrique désignent la même année sans se parler.

### Trois réserves, écrites dans la note de chaque ligne

**La référence est courte.** Sentinel-2 niveau 2A commence en 2017 et les
premières années sont pauvres en images sous les tropiques. Trois saisons de
référence là où une climatologie en demanderait trente : ces indicateurs disent
un changement récent, pas une tendance longue.

**2021 est dans la fenêtre de référence.** C'est l'année de sécheresse. La
référence est donc tirée vers le bas et les variations calculées sont un peu
plus favorables qu'elles ne devraient. Sur sept ans, aucune découpe ne fait
mieux.

**Le NDMI amplifie.** Ses valeurs tournent autour de 0,08 : un écart absolu
minuscule devient une variation relative énorme — le +66 % de Beaulieu
correspond à un passage de 0,03 à 0,05. Le *sens* est juste, l'*ampleur* est un
effet de dénominateur. J'ai calculé à côté la variation sur l'indice remis à
l'échelle [0, 1], qui ramène ce +66 % à +2,4 % ; elle est dans le fichier de
données sous `var_ndmi_stab`.

---

## 2 · Pourquoi je n'ai pas scoré le NDWI ni le NDTI

**L'eau couvre moins de 1 % de chaque section.** Une moyenne de NDWI sur le
polygone est donc un signal de *terre*, pas d'eau. J'ai remplacé la métrique
par la bonne — la **surface effectivement classée en eau** et sa variation, car
« stabilité des eaux de surface » se mesure en étendue.

Mais même ainsi, seules **5 sections sur 10** atteignent deux hectares d'eau,
en dessous desquels une moyenne ne porte que sur quelques pixels de bord de
rivière. Quentin en a 4 pixels. Mouline, 19.

Et parmi les cinq mesurables, **Dalmette voit sa surface en eau varier d'un
facteur 20 entre 2019 et 2020** — 0,15 % puis 2,87 %. Aucun phénomène
hydrologique n'explique cela ; la classification seule suffit à le produire.

| Section | eau (ha) | pixels | rapport max/min |
|---|---:|---:|---:|
| Dalmette | 25,6 | 640 | **×19,5** |
| Blactote | 9,7 | 241 | ×1,1 |
| Barbois | 8,4 | 211 | ×1,3 |
| Trichet | 6,7 | 168 | ×1,4 |
| Débouchette | 2,2 | 54 | ×1,6 |

Les quatre autres sont **stables à ±20 % près** — c'est un résultat en soi, les
eaux de surface ne se rétractent pas. Mais un indicateur calculable sur quatre
sections, qui les place toutes au même score, ajouterait du poids à l'indice
sans distinguer aucun territoire. C'est exactement le reproche que tu m'avais
fait pour l'aridité annuelle. Je ne le refais pas.

**Le NDTI cumule trois problèmes.** Même contrainte de pixels ; les cinq
sections mesurables donnent toutes une valeur entre −0,14 et −0,04, donc le même
score ; et **le barème publié est inversé** — il attribue 10 à une turbidité
supérieure à 0,7 et 0 à une eau limpide, alors qu'une eau chargée de sédiments
signale une érosion en amont. Corriger un barème pour obtenir un score plat sur
la moitié du territoire ne se justifie pas.

**Ce que le NDTI dit quand même** : les cinq valeurs sont **négatives**, le vert
domine le rouge, l'eau détectée est claire. Cohérent avec le moment de l'année —
l'érosion arrive avec les averses, pas en mars. Pour la voir, il faudrait
mesurer la turbidité en septembre-octobre, pas en saison sèche. C'est faisable,
dis-le-moi si tu le veux.

Les deux lignes restent donc listées dans l'onglet **Lacunes**, avec le motif
écrit en toutes lettres. Leur valeur est affichée dans leur onglet.

---

## 3 · Dans l'application

Les quatre onglets NDVI, NDMI, NDWI et NDTI sont maintenant remplis : trois
chiffres clés (référence, récent, variation), la série des sept saisons sèches
avec la référence en pointillés, et le tableau des dix sections trié de la plus
dégradée. L'onglet NDWI affiche la **surface en eau** et non le NDWI moyen, pour
la raison ci-dessus.

L'interprétation de chaque indice — ce qu'il mesure, comment le lire ici, ce
dont il faut se méfier — reste affichée au-dessus des chiffres.

---

## Ce qui reste

**30 indicateurs environnementaux** non calculés au lieu de 32. Le plus
accessible ensuite : MODIS pour la température de surface (lignes 36, 41, 42).
