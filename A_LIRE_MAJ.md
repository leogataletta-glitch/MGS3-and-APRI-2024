# La maquette, appliquée — accueil et colonne de navigation

## Envoyez ces quatre fichiers dans le MÊME commit

| Fichier | |
|---|---|
| `icones.py` | **nouveau** — le jeu d'icônes du site |
| `app.py` | colonne de navigation, pastille de langue |
| `filtres.py` | barre de filtres avec icônes, correction du changement de langue |
| `accueil_page.py` | la page d'accueil refaite sur la maquette |

`app.py`, `filtres.py` et `accueil_page.py` importent tous les trois
`icones.py` : sans lui, l'application ne démarre pas.

**Si la livraison précédente n'est pas encore poussée** (`dimension_page.py`,
`questions_dimension.py`, `synthese_page.py`), poussez tout le dossier d'un
bloc : `filtres.py` et `app.py` sont communs aux deux.

## Ce qui a été repris de la maquette

**La colonne de gauche.** Le titre est *Navigation*. Chaque entrée porte une
icône dessinée — pastilles, bouclier, barres, boucle, personnes, fiche,
téléchargement — au lieu des glyphes typographiques d'avant, qui ne voulaient
rien dire et changeaient d'épaisseur d'une machine à l'autre. L'entrée active
est une **pastille vert clair sur encre foncée** : le vert profond précédent se
confondait avec le fond de la colonne. En bas, *Filtres rapides* avec le bouton
**Réinitialiser les filtres** et, dessous, l'état courant en clair — c'est le
seul raccourci de filtre qui a sa place dans la marge, puisqu'on le cherche
depuis n'importe quelle page.

**Les trois chiffres de tête sont devenus des cartes**, chacune avec sa
pastille d'icône colorée, son nombre en grand et sa précision dessous. Ils
tenaient auparavant sur une ligne, en petit, et se lisaient comme une légende.

**La localisation est un encadré d'information** — fond bleuté, pastille « i » —
et non plus un paragraphe de corps de texte.

**La barre de filtres** est sur la page d'accueil elle aussi, avec une icône
dans chaque sélecteur (maison, montagne, personnes), les intitulés *Section
communale · Paysage · Groupe de répondants*, et la ligne
*« Les résultats se mettent à jour automatiquement selon vos filtres »* avec son
icône de rafraîchissement — pour qu'on ne cherche pas un bouton « appliquer »
qui n'existe pas.

**Deux colonnes en bas** : le récit *Ce qu'est APRI, et d'où cela vient* à
gauche, l'encadré **Accès rapides** à droite — quatre lignes cliquables avec
icône colorée, titre, sous-titre et chevron, qui mènent aux quatre rubriques.

**La langue active** est une pastille bleue et non plus verte : le vert est la
couleur de la navigation, et deux verts différents sur le même écran se
lisaient comme deux états du même objet.

## Deux points de fond, pas de décoration

**Les filtres de l'accueil agissent vraiment.** Afficher une barre de filtres
au-dessus de chiffres qui ne bougent pas serait pire que de ne pas l'afficher.
Le nombre de ménages suit donc la sélection — il est recalculé sur les
effectifs par section et par sous-population de `ventilation.json` — et les
quatre chiffres saillants sont lus sous le filtre courant au lieu du total. La
carte, elle, reste la vue par section communale : c'est sa raison d'être.

**Un bogue corrigé au passage.** En basculant l'anglais vers le français en
cours de session, les trois listes de filtres restaient en anglais jusqu'au
rechargement complet de la page — leurs intitulés étaient rendus sur un widget
dont la clé ne changeait jamais. Le widget affiché porte maintenant une clé
suffixée par la langue, donc il est recréé quand elle change ; la valeur
choisie, elle, reste dans l'état commun et survit au basculement.

## Vérifié

- **42 rendus complets** — 7 pages × 3 combinaisons de filtres × 2 langues —
  zéro exception, zéro clé de traduction brute ;
- page ouverte dans le navigateur, avant et après changement de langue : les
  icônes de navigation, la pastille active, les filtres rapides, les trois
  cartes de chiffres, l'encadré d'information, la barre de filtres et les accès
  rapides ;
- alignement des titres d'accès rapide contrôlé dans le DOM — Streamlit centre
  le contenu de ses boutons à trois niveaux imbriqués, il fallait forcer les
  trois.
