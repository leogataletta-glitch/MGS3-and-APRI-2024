# Les doublons retirés, et un outil d'ondes de choc

## Huit fichiers, MÊME commit — TOUS À LA RACINE

| Fichier | Où le déposer |
|---|---|
| `ondes_choc.py` | **racine** — **nouveau** |
| `app.py` | **racine** — modifié |
| `boucles_page.py` | **racine** — modifié |
| `environnement_page.py` | **racine** — modifié |
| `trajectoires.py` | **racine** — modifié |
| `synthese_page.py` | **racine** — modifié |
| `fiche_paysages.py` | **racine** — modifié |
| `radar_accueil.py` | **racine** — modifié |

Rien dans `data/`. Un fichier est **supprimé** du dépôt : `croisement_page.py`.

---

## 1. L'outil d'ondes de choc

Dans « Boucles de rétroaction », un sélecteur en tête ouvre deux lectures du
même modèle : **Ondes de choc** et **Boucles, leviers, effet total** (l'ancienne
page, intacte).

On choisit un nœud, on règle le choc entre −3 et +3 points, on appuie sur
lecture. Le choc part du nœud et traverse le système par vagues : les voisins
directs, puis leurs voisins, jusqu'à extinction. Les colonnes sont les rangs
d'arrivée, les liens qui portent la vague en cours s'animent, les nœuds se
teintent selon le sens et l'ampleur de l'effet cumulé.

Trois choses que cette vue dit, et que l'ancienne ne pouvait pas dire :

**La part de l'effet déjà distribuée**, à chaque pas. Sur le couvert forestier,
la vague 3 n'a distribué que 79 % de l'effet total. C'est la démonstration
visible de ce que dit le moteur : une propagation tronquée à trois vagues
laisse un cinquième de l'effet dans la nature.

**Le retour de boucle, daté.** Un choc de −2 sur le couvert forestier revient
sur le couvert forestier **à la vague 2, et il l'amplifie**. À cet endroit, le
système n'est pas une chaîne : c'est une boucle qui creuse.

**Ce que le choc n'atteint pas.** Vingt des quarante-cinq nœuds ne sont jamais
touchés par un choc forestier : aucune chaîne de liens n'y mène. La page
l'écrit, au lieu de laisser croire que tout tient à tout.

Tout le calcul se fait dans le navigateur — quarante-cinq nœuds, un produit
matrice-vecteur par vague. Passer par le serveur ferait clignoter la page une
fois par seconde et l'animation serait impossible. La mécanique reste celle de
`boucles_moteur`, mise à l'échelle par lui : les deux vues ne peuvent pas
diverger.

*Le rang d'une vague est un ordre de relais, pas un calendrier — la page le dit
sous le graphique.*

---

## 2. Les doublons

**Le croisement en double est supprimé.** « Croiser des questions », enfoui dans
le volet méthodologique, était un sous-ensemble strict de « Croisement des
résultats » : mêmes 483 questions, même carte par section, même ventilation.
Le nouveau fait tout cela **et** le profil de résilience du sous-groupe, la
comparaison de deux groupes et l'effectif attendu sous indépendance. Rien n'est
perdu.

**La chronologie forestière n'a plus qu'un seul dessin.** L'onglet
Environnement et la rubrique Trajectoires traçaient la même série, sur le même
fichier, avec deux implémentations — et elles avaient déjà divergé : la marge
d'axe corrigée d'un côté restait fausse de l'autre. L'onglet appelle désormais
le dessin de Trajectoires.

*Après lecture du code, je retire ce que je vous disais des trois autres
courbes : ce ne sont pas des doublons.* La pluie de l'onglet Environnement est
un encodage **divergent** autour de la normale, ocre en dessous, bleu au-dessus ;
Trajectoires en fait une ligne. Ce sont deux messages différents sur la même
donnée. Et le graphique des indices sert onze indicateurs, pas deux. Les
supprimer aurait appauvri l'explorateur sans rien gagner.

**Le menu passe de treize à onze entrées.** « Diagramme radar » et « Fiche
synthèse — paysages » comparaient des profils, ce que fait déjà « Profils
territoriaux et sociaux » — qui propose justement les sections, les groupes
**et** les deux paysages comme découpages. Ils en sont devenus les deux autres
onglets : *Par territoire ou par groupe*, *Littoral contre montagne*,
*Diagramme radar*. Aucun contenu n'est retiré ; on cesse de proposer trois
portes vers la même pièce.

Et l'outil d'ondes de choc n'a pas ajouté de douzième entrée : il est allé là
où il a un sens, dans les boucles.

---

## Vérifié

- **66 rendus** — 11 pages × 3 combinaisons × 2 langues, dont les quatre écrans
  de l'accueil et **les deux vues des boucles** — zéro exception, zéro clé de
  traduction brute ;
- le harnais teste maintenant les deux vues des boucles : ne rendre que celle
  par défaut aurait laissé l'autre sans filet, exactement le défaut qui avait
  laissé passer l'erreur du troisième écran de l'accueil ;
- l'outil ouvert au navigateur dans les deux langues : animation, pas à pas,
  changement de nœud, changement d'amplitude, aucune erreur au journal ;
- chiffres recoupés avec `boucles_moteur` : la somme des vagues converge bien
  vers l'effet total qu'il calcule par inversion.
