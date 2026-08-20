# Une porte sur chaque écran de l'accueil

## Un seul fichier — À LA RACINE

| Fichier | Où le déposer |
|---|---|
| `accueil_apri.py` | **racine du dépôt** — modifié |

---

## Ce qui manquait

L'écran 1 de l'accueil dit **où** : dix sections, deux départements, la
vignette d'Haïti. Puis il s'arrêtait là. Le détail — les dix sections
dessinées, les deux paysages pilotes, les 1 195 points d'entretien, les
routes, le relief — est dans « Le territoire », et rien ne conduisait
directement de l'un à l'autre. Il fallait traverser les quatre écrans du
parcours pour trouver une porte, ou repartir dans le menu de gauche.

**Chaque écran a maintenant sa sortie**, sous son contenu :

| Écran | Porte |
|---|---|
| 1 · Où ? | Ouvrir la carte interactive du territoire |
| 2 · Qu'a-t-on mesuré ? | Le cadre de résilience en détail |
| 3 · Qu'a-t-on trouvé ? | Les résultats, dimension par dimension |
| 4 · Que faire ? | les quatre portes qui existaient déjà |

Le bouton n'occupe pas toute la largeur, et c'est voulu : un bouton pleine
largeur se lit comme l'action principale de l'écran, or l'action principale
reste d'avancer dans le parcours. C'est une sortie latérale, elle en a la
taille.

---

## Un défaut du harnais, corrigé au passage

Le harnais de test rendait les écrans 2, 3 et 4 du parcours — **jamais le
premier**. C'est précisément celui qui porte la carte du territoire et sa
nouvelle porte : la seule chose ajoutée aujourd'hui aurait échappé au test.
Les quatre écrans sont maintenant parcourus, et une quatrième combinaison de
filtres a été ajoutée pour que la rotation les couvre tous.

**88 rendus** au lieu de 66, zéro exception, zéro clé de traduction brute.

## Vérifié aussi

- ouvert au navigateur : le bouton de l'écran 1 conduit bien à « Le
  territoire », carte interactive chargée, aucune erreur au journal.

---

# Une seule police pour tout le site

## Trois fichiers de plus, MÊME commit — À LA RACINE

| Fichier | Où le déposer |
|---|---|
| `app.py` | **racine** — modifié |
| `map_render.py` | **racine** — modifié |
| `ocb_page.py` | **racine** — modifié |

Les titres étaient en **Outfit**, une géométrique aux formes rondes, et le
corps en **Inter**. Deux dessins qui se répondaient mal : le contraste attirait
l'œil sur la police plutôt que sur le chiffre, et donnait au site un air de
page produit.

**Inter porte maintenant tout** — titres, corps, cartouches, cartes,
graphiques. Ses chiffres sont tabulaires, donc les colonnes s'alignent ; ses
formes sont neutres. Un observatoire n'a pas à avoir de voix typographique.

Une seule famille à télécharger au lieu de deux : la page s'ouvre aussi un peu
plus vite sur une connexion lente.

*Si vous préférez autre chose, c'est un mot à changer : **IBM Plex Sans** est
plus institutionnelle et un peu technique, **Source Sans 3** est la plus
discrète des quatre, très proche d'un rapport imprimé. La comparaison est dans
la conversation.*
