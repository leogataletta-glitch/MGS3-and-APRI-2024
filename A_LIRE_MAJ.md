# La langue passe dans le bandeau

## Envoyez `app.py`. Un seul fichier.

**Français** et **English** côte à côte en haut à gauche, précédés d'un globe.
La langue courante porte la pastille verte, l'autre s'éclaircit au survol. Un
clic, et tout le site bascule.

Le menu déroulant du bas de la colonne de gauche disparaît — pour deux choix,
il fallait ouvrir, viser, choisir, alors que deux mots se lisent et se
cliquent d'un seul geste. Le titre « LANGUE » de la colonne part avec lui.

Le bandeau porte donc maintenant **la langue à gauche, le logo du PNUE à
droite**, et rien entre les deux.

## Deux détails de fabrication

**Le globe est dessiné en SVG**, pas en émoji. L'émoji 🌐 change de dessin et
de couleur selon le système d'exploitation, et rendait la barre bariolée sur
Windows. Le tracé suit la couleur du texte et reste discret.

**La langue est lue avant le premier mot affiché.** Le bouton n'écrit que dans
l'état de session ; Streamlit relance le script derrière, si bien que la
traduction est déjà en place quand la première ligne se dessine. Aucun
scintillement, aucun texte à moitié traduit.

## Un point à décider

La langue par défaut, au tout premier chargement, reste **l'anglais** — c'était
déjà le cas avec le menu déroulant, je n'ai rien changé. Si vous préférez que
le site s'ouvre en français, dites-le : c'est un mot à changer dans `i18n.py`.

## Vérifié

- capture d'écran du navigateur relue, puis **clic réel sur « Français »** :
  la colonne, le bandeau et toute la page basculent ;
- 48 rendus complets — 6 pages × 4 combinaisons de filtres × 2 langues —
  **zéro exception, zéro message d'erreur** ;
- aucune clé de traduction brute affichée, dans les deux langues ;
- la barre d'outils de Streamlit reste absente, le bandeau touche le haut de
  la fenêtre.

---

*Si les fichiers des mises à jour précédentes ne sont pas encore en ligne, ils
restent à envoyer : `questions_dimension.py` (nouveau), `dimension_page.py`,
`accueil_page.py`, `i18n.py` — ce sont eux qui apportent les deux sous-onglets
sous chaque dimension.*
