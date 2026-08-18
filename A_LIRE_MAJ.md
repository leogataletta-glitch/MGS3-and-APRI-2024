# Correctif — menu, et la vraie cause de l'affichage cassé

## 2 fichiers à mettre sur GitHub **dans le même commit**

| Fichier | Où |
|---|---|
| `app.py` | racine |
| `i18n.py` | racine |

Version **`2026-08-18-menu`**.

---

## 1 · D'abord la cause : ce n'était pas la mise en page

Sur ta capture, plusieurs entrées s'affichent `mode_accueil`, `a_accroche`,
`mode_synthese`, `nav_general`. **Ce sont des noms de clés, pas des libellés
manquants** : le `i18n.py` déployé n'est pas celui livré avec la refonte.
D'autres entrées s'affichent correctement (« Survey methodology », « Data
downloads ») parce que ces clés-là existaient déjà avant.

Le garde-fou affichait bien son message rouge, mais **l'application continuait
de se dessiner en dessous**. Résultat : une page à moitié juste, qu'on prend
pour un défaut de mise en page. J'ai corrigé ça — en cas de version
discordante, l'application **s'arrête maintenant franchement** sur le message
et n'affiche plus rien d'autre. Une page vide sous un message clair est plus
honnête qu'une page à moitié juste.

Donc : pousse bien les **deux** fichiers ensemble. Si tu vois le message rouge,
c'est que l'un des deux n'est pas passé.

---

## 2 · Les six dimensions redeviennent des onglets

Tu as raison, elles n'avaient rien à faire en colonne. Elles forment une
famille homogène qu'on parcourt en comparant, et **une rangée d'onglets se
parcourt du regard alors qu'une liste verticale se lit ligne à ligne**.

La colonne ne garde donc que six entrées :

**Vue d'ensemble · Les six dimensions · Synthèse par groupe ou localité ·
Fiches actions · Méthodologie · Téléchargements**

L'entrée « Les six dimensions » ouvre une page qui porte les six onglets, comme
avant la refonte.

---

## 3 · Le menu, corrigé sur trois points

**L'alignement.** Le bouton de Streamlit centre son contenu par défaut, et il
le fait à trois niveaux imbriqués — c'est pour ça qu'un libellé sur deux lignes
se retrouvait indenté au premier rang et collé au bord au second. Il faut
forcer l'alignement à gauche sur le bouton *et* sur ses deux conteneurs
internes, sinon l'un des trois reprend la main. C'est fait.

**La taille.** 15,5 px au lieu de 14,5, hauteur minimale de 46 px, colonne
élargie à 310 px, logo à 54 px et « APRI » à 30 px. Un menu se vise au curseur
sans regarder : il lui faut une cible franche.

**Le survol.** Le fond s'éclaircit et le texte passe au blanc pur au passage de
la souris ; l'entrée active en vert plein s'éclaircit aussi. Sans retour au
survol, rien ne distingue une ligne cliquable d'un simple titre — c'était le
défaut le plus gênant.

---

## Ce qui reste en attente

Le bloc **« Filtres actifs »** de ta maquette (Département / Paysage / Sexe /
Âge avec leurs croix) suppose un filtrage transversal de toutes les pages.
Aujourd'hui chaque page a son propre sélecteur. Dis-moi si tu veux que je les
remonte en filtres globaux — il faut que je reprenne chaque page pour qu'elle
les écoute, c'est un chantier à part entière.
