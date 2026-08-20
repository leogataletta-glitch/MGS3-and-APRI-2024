# Les boucles causales, révisées — et un barème pour les forces

## Cinq fichiers — ATTENTION À L'EMPLACEMENT

| Fichier | Où le déposer |
|---|---|
| `graphe_causal.json` | **dans `data/`** — modifié |
| `ondes_choc.py` | **racine** — modifié |
| `boucles_page.py` | **racine** — modifié |
| `app.py` | **racine** — modifié |
| `A_LIRE_MAJ.md` | **racine** |

---

## 1. Le défaut que vous avez vu, mesuré

« Accès à l'électricité » avait **une seule** arête sortante : vers
l'achèvement du primaire. La première vague d'un choc sur l'électricité était
donc l'école, et rien d'autre. Ni l'information, ni la sécurité, ni le revenu.

Ce n'était pas un choix de modélisation, c'était une lacune, et elle touchait
**dix nœuds** : assainissement, téléphonie, logement, foncier, pluie, état
civil, école, centre de santé, électricité, abris. Les vagues n'avaient donc
aucune structure de niveau, parce que le graphe n'en avait pas : vingt-quatre
des soixante-six liens étaient concentrés sur le sous-système de la
déforestation.

**Seize liens de premier ordre ont été ajoutés** — le graphe passe de 66 à 82
arêtes. La première vague depuis l'électricité est maintenant :

| Lien | Force | Classe |
|---|---|---|
| électricité → accès aux messages d'alerte | 0,50 | documentée |
| électricité → sentiment de sécurité | 0,50 | documentée |
| électricité → revenu au-dessus du seuil | 0,50 | documentée |
| électricité → achèvement du primaire | 0,35 | documentée |

L'électricité a aussi reçu une **entrée** — la qualité du service public —
sans laquelle elle restait une source pure, que rien dans le modèle ne pouvait
faire bouger.

---

## 2. Le barème : pourquoi 0,50 et pas 0,30

Cinq échelons nommés, et un plafond par classe de connaissance. La classe dit
d'où vient le savoir, l'échelon dit combien on lui accorde.

| Échelon | Critère |
|---|---|
| **0,20** | lien plausible, mécanisme indirect, aucune mesure |
| **0,35** | mécanisme direct, mais effet faible ou très dépendant du contexte |
| **0,50** | effet régulièrement observé, ampleur moyenne, plusieurs contextes |
| **0,65** | mécanisme direct, sources convergentes, effet de premier ordre |
| **0,80** | relation structurelle : l'un est la condition de l'autre |

| Classe | Plafond |
|---|---|
| structurelle · empirique | 0,80 |
| documentée | 0,65 |
| théorique | 0,50 |
| hypothèse | 0,20 |

**Règle de placement**, appliquée sans exception : échelon haut de la classe si
le mécanisme est direct et de premier ordre, échelon bas s'il est médié ou
très variable.

Le barème a immédiatement révélé **trois valeurs incohérentes** dans l'ancien
modèle — 0,70 et 0,80 avec la mention « théorique », c'est-à-dire au-dessus du
plafond de leur propre classe. Elles ne sont pas théoriques : l'une des deux
grandeurs est la condition de l'autre. D'où une cinquième classe,
**structurelle**, et trois relations à 0,80 : emploi → revenu, couvert →
ressource ligneuse, réseau mobile → alerte.

Dans l'autre sens, les six **hypothèses** sont descendues à 0,20. Les laisser à
0,35 revenait à leur accorder le bénéfice du doute.

---

## 3. Un résultat que je ne cherchais pas : le modèle est à la limite

Le rayon spectral du graphe brut vaut **0,987**. Au-dessus de 1, la propagation
n'a plus de somme : un choc s'amplifie indéfiniment.

On en est à un centième. Et ce n'est pas théorique : avec les hypothèses
laissées à 0,35, ces mêmes trois relations structurelles à 0,80 donnaient
**1,007**, donc un modèle qui diverge. Le système est très bouclé, et une seule
force relevée d'un échelon peut le faire basculer.

Le moteur propage sur une matrice remise à l'échelle — le calcul reste défini
quoi qu'il arrive — mais le diagnostic affiché à l'écran dit « fortement
bouclé », et il a raison.

---

## 4. Ce que l'écran montre maintenant

Sous le graphique des ondes, un nouveau panneau : **« Les liens que cette vague
emprunte »**. À chaque pas, les cinq liens qui portent le plus, avec pour
chacun sa force, sa classe et la phrase qui la justifie. La question « d'où
sort ce 0,50 » se pose au moment où l'on voit la vague passer : la réponse est
maintenant à cet endroit-là.

Le barème complet est dans un volet replié sous le graphique, **« D'où viennent
les forces »**, et le survol d'une flèche donne la même information.

## Vérifié

- **88 rendus** — 11 pages × 4 combinaisons × 2 langues, les quatre écrans de
  l'accueil et les deux vues des boucles — zéro exception ;
- le harnais a d'ailleurs attrapé une erreur que la révision venait
  d'introduire : la classe « structurelle » manquait dans la légende de
  l'onglet d'analyse, et la page tombait dès qu'un filtre était posé ;
- les quatre vagues ouvertes au navigateur dans les deux langues, panneau des
  liens compris, aucune erreur au journal ;
- effet du portefeuille recalculé sur le nouveau graphe : **+0,347** au lieu de
  +0,335. Les chiffres de la note aux bailleurs et de l'accueil bougent en
  conséquence — c'est normal, le modèle a changé.
