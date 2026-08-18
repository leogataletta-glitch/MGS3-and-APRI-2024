# Les mots du bandeau sont supprimés

## Envoyez `app.py`. Un seul fichier.

Le bandeau vert ne porte plus que le **logo du PNUE**. « Overview », « The six
dimensions », « Summary by group or locality », « Action sheets », « Survey
methodology », « Data downloads » : tout est retiré.

C'était une redite, et vous aviez raison de le dire. La colonne de gauche
affiche ces six entrées en permanence, et chaque page répète son nom en titre :
le même mot trois fois dans les cent premiers pixels.

**La navigation vit désormais uniquement dans la colonne de gauche.** Rien
n'est perdu — les six entrées y sont toutes, au même endroit qu'avant.

Retiré aussi : le code des onglets et leur feuille de style, 3 700 caractères
qui ne servaient plus à rien. Un bouton mort dans un fichier finit toujours par
réapparaître à l'écran un jour ou l'autre.

## Ce que le bandeau garde

- le **vert plein cadre**, d'un bord à l'autre, le même que la colonne : les
  deux forment un encadrement et le contenu blanc s'y pose comme une feuille ;
- le **logo du PNUE** en réserve, en haut à droite ;
- le **bandeau de paysage** en dessous, pleine largeur ;
- et, seulement lorsqu'un filtre est réellement posé, la **pastille du filtre
  actif** — un chiffre lu sans savoir qu'un filtre est posé est un chiffre mal
  lu. Sans filtre, rien.

## Vérifié

- capture d'écran du navigateur relue : plus un seul mot dans le bandeau,
  le logo seul en haut à droite, la barre d'outils de Streamlit toujours
  absente ;
- la navigation par la colonne fonctionne — testée au clic, la page change ;
- 48 rendus complets — 6 pages × 4 combinaisons de filtres × 2 langues —
  **zéro exception, zéro message d'erreur** ;
- aucune clé de traduction brute affichée, dans les deux langues.

---

*Si les fichiers des mises à jour précédentes ne sont pas encore en ligne, ils
restent à envoyer : `questions_dimension.py` (nouveau), `dimension_page.py`,
`accueil_page.py`, `i18n.py` — ce sont eux qui apportent les deux sous-onglets
sous chaque dimension.*
