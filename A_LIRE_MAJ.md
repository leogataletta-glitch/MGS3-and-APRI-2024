# Filtres actifs, barre du haut, dernières livraisons

## Les 7 fichiers à mettre sur GitHub **dans le même commit**

| Fichier | Où | État |
|---|---|---|
| `app.py` | racine | remplacé |
| `i18n.py` | racine | remplacé |
| `filtres.py` | racine | **nouveau** |
| `actualites.py` | racine | **nouveau** |
| `accueil_page.py` | racine | remplacé |
| `dimension_page.py` | racine | remplacé |
| `synthese_page.py` | racine | remplacé |

Version **`2026-08-18-filtres`**.

---

## 1 · Les filtres actifs — et ils marchent vraiment

Le bloc de ta maquette est en bas de la colonne verte : **Section communale**
et **Groupe**, avec les pastilles de ce qui est appliqué et un bouton
Réinitialiser qui s'éteint quand il n'y a rien à réinitialiser.

Ce ne sont pas des filtres décoratifs. **Toutes les pages les lisent.** Choisis
Dumont dans la colonne, passe d'une dimension à l'autre : tu restes sur Dumont.
Avant, chaque page avait son sélecteur et on retombait sur l'ensemble à chaque
changement d'onglet.

### Le croisement section × groupe

Les deux filtres ensemble ne se lisent pas dans le même fichier que chacun pris
seul. `resultats.json` porte les scores par section **ou** par groupe ;
`ventilation.json` porte le croisement. Le module `filtres.py` choisit la bonne
source selon ce qui est demandé — c'est tout l'intérêt d'un module dédié plutôt
que le même branchement recopié dans cinq pages, où il finirait par diverger.

### Ce que le filtre ne peut pas faire, et qui est dit à l'écran

**Un indicateur satellitaire n'a pas de ventilation par sexe.** La forêt, la
pluie et la température ne varient pas selon le répondant. Sous un filtre de
groupe, ces lignes gardent donc leur valeur de section, et une note le signale
sous le tableau — plutôt que d'afficher un chiffre identique en laissant croire
à une égalité mesurée.

---

## 2 · La barre du haut, avec les deux logos

Une barre blanche en tête de contenu : à gauche le PNUE et le nom de la page
courante, au centre **ce sur quoi porte l'affichage**, à droite le logo du
PNUE.

Les deux logos cohabitent sans se disputer la place : **APRI porte le produit**
dans la colonne verte, **le PNUE porte l'institution** en haut de page.

La pastille centrale n'est pas un ornement. Elle dit « Dix sections communales,
tous les répondants » ou « Filtré sur Dumont, Femmes ». **Un chiffre lu sans
savoir qu'un filtre est posé est un chiffre mal lu** — c'est le risque que
crée un filtre global, et c'est le seul moyen honnête de le désamorcer.

---

## 3 · Dernières livraisons

Le panneau « Actualités & Rapports » de ta maquette, en colonne de droite sur
l'accueil, sous la carte. Chez nous ce ne sont pas des nouvelles — un
observatoire n'en produit pas — mais **les livrables** : ce qui vient d'être
calculé, avec une pastille « Nouveau », et un bouton qui mène à l'onglet
concerné.

- Température et santé de la végétation, 25 ans — **Nouveau**
- Six indices de végétation par Sentinel-2 — **Nouveau**
- La pluie passe à la campagne agricole — **Nouveau**
- Méthode, barèmes et réserves
- Télécharger les données

**Chaque entrée pointe vers un onglet réel du site**, jamais vers une page qui
n'existe pas : une liste de ressources qui mène à des impasses détruit la
confiance plus sûrement qu'une liste courte.

---

## 4 · Un bogue que j'ai trouvé en vérifiant

La barre du haut affiche le nom de la page courante, mais elle était dessinée
**avant** que l'état de navigation soit initialisé. Streamlit lève alors une
erreur qui masque toute la page — et cela ne se serait vu qu'au premier
chargement, sur une session neuve, donc chez toi et pas chez moi. L'ordre est
corrigé.

---

## Ce qui reste

Les filtres de ta maquette comptent aussi **Paysage**, **Niveau de richesse**
et **Accès à l'eau**. Je n'ai mis que section et groupe, parce que ce sont les
deux seules ventilations que portent les fichiers de résultats. Les trois
autres supposeraient de recalculer les scores sur des sous-populations qui
n'existent pas encore dans les données — faisable, mais c'est un passage par
le pipeline, pas un réglage d'affichage. Dis-moi si tu les veux.
