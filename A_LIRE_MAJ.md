# Correctif — la page Méthodologie plantait

## Ce qui s'est passé

`methodologie_page.py` appelait `map_render.bulle_notion()`, une fonction qui
existe dans la dernière version de `map_render.py` mais **pas dans celle qui est
en ligne**. Le fichier `map_render.py` du dépôt est resté sur une version
antérieure, d'où l'`AttributeError`.

L'onglet **Indice de résilience** appelle la même fonction : il serait tombé sur
la même erreur au premier clic.

## Les 8 fichiers à mettre sur GitHub **dans le même commit**

| Fichier | Où | État |
|---|---|---|
| `app.py` | racine | remplacé |
| `i18n.py` | racine | remplacé |
| `map_render.py` | racine | **remplacé — c'est lui qui manquait** |
| `methodologie_page.py` | racine | nouveau (corrigé) |
| `telechargements_page.py` | racine | nouveau |
| `data/methodologie.json` | `data/` | nouveau |
| `data/resultats.json` | `data/` | remplacé |
| `assets.py` | racine | à pousser **seulement si tu ne l'as pas déjà fait** |

Si tu as un doute sur un fichier, pousse-le : les versions livrées ici forment
un ensemble cohérent et testé.

## Deux corrections dans ce lot

1. **`map_render.py` à jour** — il apporte `bulle_notion()`, `styles_bulle()`,
   l'échelle de couleurs APRI en 11 classes et les cartouches de chiffres.
2. **`methodologie_page.py` ne peut plus faire tomber l'application** — si une
   fonction de `map_render` manque, la page affiche le terme sans sa bulle au
   lieu de planter. Un fichier oublié ne coûtera plus qu'une infobulle.

## Rappel du contenu de la mise à jour

- Haïti dans le titre, dans la page et dans l'onglet du navigateur.
- Logo PNUE agrandi (96 → 168 px).
- Cinq onglets aux intitulés techniques : Résultats descriptifs · Indice de
  résilience (IRLA / APRI) · Analyse croisée · Méthodologie d'enquête ·
  Téléchargement des données.
- Onglet **Méthodologie** : sept sections tirées de la note de cadrage IRLA,
  bilingues, avec sommaire et bulles de définition.
- Onglet **Téléchargement** : six jeux de données, chacun avec un titre
  explicite, la description de son contenu et son poids ; classeurs fabriqués à
  la demande, avec une feuille « Lisez-moi ».

## Un point à valider — trois barèmes remis à l'endroit

Lignes **88 (pêche destructrice)**, **93 (violences subies)** et **108
(insécurité alimentaire sévère)** : le barème publié attribue le score 10 à la
situation la **plus dégradée**. La ventilation par sous-population appliquait
déjà la correction, la carte par section non — les deux divergeaient.

J'ai retenu la version corrigée partout : 10 désigne toujours la situation la
plus favorable. Le score issu du barème publié reste dans `resultats.json` sous
`scores_bareme_publie`. La dimension VI (humaine) passe d'environ 0,7 à environ
5 au niveau des sections. Dis-moi si tu préfères l'inverse.

## Rappel

Dépôt **privé**, mot de passe dans `APP_PASSWORD` (Secrets Streamlit Cloud),
aucun fichier téléchargeable ne contient de nom, téléphone, nom d'enquêteur,
coordonnées GPS précises ni nom de localité.
