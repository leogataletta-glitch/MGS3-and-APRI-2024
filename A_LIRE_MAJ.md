# La barre « Share / Deploy / ⋮ » est supprimée

## Envoyez `app.py`. C'est tout ce qu'il faut pour ça.

Vous aviez raison de vous agacer : je l'avais rendue **transparente**, pas
supprimée. Le fond disparaissait, le texte restait — et il se posait par-dessus
le logo du PNUE. Elle est maintenant **retirée de la mise en page**.

Ce que j'ai retiré : `Share`, `Deploy`, l'étoile, le menu ⋮, le widget d'état,
la barre colorée de chargement en haut de fenêtre, et le pied « Made with
Streamlit ». Ce sont les commandes de l'atelier Streamlit, pas du site.

**Visés sous tous leurs noms.** Streamlit renomme ces éléments d'une version à
l'autre ; n'en cibler qu'un revient à voir la barre revenir au prochain
déploiement. Les onze sélecteurs connus sont listés, et vérifiés dans le
navigateur : les cinq éléments sont soit absents du DOM, soit à
`display: none`, hauteur nulle.

**Ce qui n'est pas touché** : le bouton `«` de repli de la colonne de gauche. Il
appartient à la barre latérale, pas à cet en-tête, et il reste utile.

---

## Un fichier en plus, facultatif : `.streamlit/config.toml`

**La correction de `app.py` suffit** — je l'ai vérifié en démarrant le site
sans ce fichier, la barre reste absente. Le `config.toml` est une seconde
serrure, plus quelques réglages utiles :

- `toolbarMode = "minimal"` — le réglage officiel de Streamlit. Il agit avant
  même que la page ne s'affiche, là où la feuille de style agit après coup :
  avec les deux, la barre ne peut plus apparaître même une fraction de seconde
  au chargement.
- `showErrorDetails = false` — plus de trace Python à l'écran pour un
  visiteur. Une erreur technique dans un tableau de bord institutionnel
  n'aide personne et inquiète tout le monde.
- **thème clair imposé** — sans cela, un visiteur dont le système est en mode
  sombre voit Streamlit inverser les fonds, et les cartes comme les graphiques,
  dessinés sur blanc, deviennent illisibles. Celui-là vaut la peine.

**Pour l'envoyer sur GitHub**, comme c'est un fichier dans un sous-dossier :
`Add file` → `Create new file`, puis tapez comme nom de fichier
`.streamlit/config.toml` — GitHub crée le dossier tout seul dès que vous tapez
la barre oblique. Collez-y le contenu, `Commit`.

Si cela vous ennuie, sautez-le : `app.py` seul règle le problème que vous
signaliez.

---

## L'envoi

| Fichier | |
|---|---|
| `app.py` | **la correction** — barre d'outils supprimée |
| `.streamlit/config.toml` | facultatif — seconde serrure + thème clair imposé |

Et, si ce n'est pas encore fait, les quatre fichiers de la mise à jour
précédente, qui apportent les sous-onglets par dimension :
`questions_dimension.py` (nouveau), `dimension_page.py`, `accueil_page.py`,
`i18n.py`.

## Vérifié

- barre d'outils : les cinq éléments absents ou à hauteur nulle, **avec et
  sans** `config.toml` ;
- capture d'écran du navigateur relue : le logo du PNUE est seul en haut à
  droite, plus rien ne se superpose ;
- 48 rendus complets — 6 pages × 4 combinaisons de filtres × 2 langues —
  **zéro exception, zéro message d'erreur** ;
- le bouton de repli de la colonne de gauche fonctionne toujours.
