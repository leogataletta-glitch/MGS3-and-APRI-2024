# Outil de boucles de rétroaction causale

Une septième rubrique, **Boucles de rétroaction**, placée après Analyse des
résultats. C'est le second volet du cadre IRLA : l'indice cartographie les
capacités, les boucles disent comment elles se tiennent l'une l'autre.

## L'outil

**Un réseau de 45 nœuds et 66 relations.** On choisit un levier, on déplace un
curseur, et l'onde se propage. Les indicateurs touchés s'allument en vert ou en
rouge avec ↑ ↓ →, le levier porte un anneau bleu. **Un clic sur un nœud du
réseau en fait le levier.**

**Les 38 boucles sont détectées automatiquement**, classées renforçantes (R) ou
équilibrantes (B), triées par force. On peut en isoler une pour la lire seule.

Toutes les boucles de votre document s'y retrouvent : charbon de bois,
agriculture extensive et brûlis, érosion-productivité, hydrologique,
liquidité-pauvreté, biodiversité ; et les stabilisatrices — régénération
naturelle, démographique, socio-cognitive, énergétique.

**Les leviers sont calculés**, selon vos trois critères : degré, nombre de
boucles, et surtout appartenance à des boucles de **sens opposé**. Le classement
retrouve vos exemples sans qu'on le lui souffle — la **productivité agricole**
et les **liquidités** arrivent en tête des leviers de basculement, et la
relation dominante est **pression sur le bois → couvert forestier**, présente
dans 26 boucles. Les quatre niveaux d'intervention de Meadows sont rappelés.

## Ce que j'ai ajouté à la page Cadre

Un bloc **« Le second volet — les diagrammes de boucles causales »** : la
méthode en quatre étapes (variable symptôme → enchaînements circulaires →
leviers → fiche d'action), la règle de lecture des polarités, le schéma R / B
d'après Sterman, et **le piège** — « positive » ne veut pas dire « bonne ».

Ce dernier point est traité partout : le sous-type affiché sur chaque boucle
(**R+, R−, B+, B−**) suit **le sens de la variation que vous appliquez**, parce
qu'une même boucle renforçante est vertueuse à la hausse et vicieuse à la
baisse. Ce n'est pas une propriété du graphe, c'est une propriété du scénario.

## Trois décisions que je dois vous signaler

**1. Des nœuds que l'enquête ne mesure pas.** Votre chaîne d'exemple passe par
la santé et la capacité de travail — l'enquête ne les mesure pas. Plutôt que de
casser la chaîne ou de faire semblant, j'ai ajouté 14 variables latentes
(santé, capacité de travail, fertilité des sols, pression sur le bois…). Elles
sont **dessinées en tirets** et n'ont jamais de valeur de départ inventée. Elles
montrent aussi où l'enquête est aveugle.

**2. Les forces sont mises à l'échelle, et c'est assumé.** Avec le
sous-système déforestation, le graphe atteint un rayon spectral de 0,98 : le
système est presque à l'emballement, et une hausse de deux points sur un levier
en produisait quinze sur un autre — absurde sur une échelle qui s'arrête à dix.
Les forces sont donc ramenées d'un facteur unique (0,61). **Cela préserve le
signe des effets, la structure des boucles et le classement des indicateurs
touchés ; cela abandonne l'idée qu'un effet simulé serait un nombre de points
crédible.** Il ne l'était pas. Un diagramme de boucles causales est un outil
qualitatif.

**3. Le sens de « productivité → couvert forestier ».** J'avais posé un lien
négatif (l'extension agricole grignote la forêt). Votre document tranche dans
l'autre sens : c'est la **faible** productivité qui pousse au défrichement. J'ai
suivi le document — ce qui rend la boucle érosion renforçante, comme vous
l'écrivez. Les deux mécanismes existent dans la littérature ; celui-ci est
maintenant celui du modèle.

## Le garde-fou d'interprétation

Trois dispositifs, aucun n'est une note de bas de page :

- **le niveau de justification** de chaque relation — documentée (38),
  théorique (21), hypothèse de modélisation (6), empirique (1) — visible au
  survol de la flèche et listé en clair ;
- **l'association réellement observée** entre les dix sections communales,
  affichée dans une colonne séparée. Elle n'entre **jamais** dans le calcul. Et
  la page dit franchement que **quatre relations s'observent avec le signe
  contraire au modèle** — sur dix sections, une corrélation n'a presque aucune
  puissance, elle ne réfute rien, mais elle mérite d'arriver sur la table de
  l'atelier ;
- **l'avertissement en tête de page**, pas en pied : ce sont des scénarios
  exploratoires, pas des prédictions.

## L'envoi

**Cinq fichiers, un seul commit.**

| Fichier | |
|---|---|
| `boucles_page.py` | **nouveau** — l'interface et ses textes |
| `boucles_moteur.py` | **nouveau** — le calcul, séparé de l'affichage |
| `data/graphe_causal.json` | **nouveau** — le modèle : 45 nœuds, 66 relations |
| `app.py` | la septième rubrique |
| `cadre_page.py` | le bloc théorie sur les boucles causales |

`data/graphe_causal.json` va dans le dossier `data`, à côté de `resultats.json`.

**Le modèle est un fichier relisible.** Chaque relation y porte son signe, sa
force, son niveau de justification et sa source en clair. C'est fait pour être
corrigé en atelier avec les acteurs — c'est exactement l'usage que décrit votre
document.

## Vérifié

- 25 modules compilent ; **42 rendus complets** — 7 pages × 3 combinaisons de
  filtres × 2 langues — **zéro exception, zéro message d'erreur** ;
- aucune clé de traduction brute affichée, dans les deux langues ;
- le graphe : aucun nœud orphelin, propagation convergente, diagnostic affiché
  à l'écran ;
- captures d'écran relues : le réseau, les effets, les boucles, les leviers, le
  bloc théorie.

## Ce qui reste ouvert

Vous écrivez que chaque levier doit faire l'objet d'une **fiche d'action** —
objectif, activités, acteurs, horizon, indicateurs de performance. C'est
exactement ce que devrait devenir la rubrique **Fiches d'intervention**, qui
porte encore l'ancien contenu « pistes ». Les leviers sont maintenant calculés :
il ne manque que de les relier aux fiches. C'est la suite naturelle, dites-moi
si je la prends.
