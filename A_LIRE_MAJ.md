# Mise à jour — logo, page d'accueil, histoire d'APRI

## D'abord : un chiffre faux qu'il faut que vous sachiez

La tuile « Ménages enquêtés » de l'accueil affichait **2 700**. C'est faux.

Ce nombre venait d'un `max()` sur les effectifs de toutes les lignes du
référentiel, et le maximum tombait sur la **ligne 24, enregistrement des
naissances**, qui compte des **enfants**, pas des ménages. Le vrai chiffre est
**1 211 questionnaires** — dont 1 206 rattachés à une section communale — ce
que le reste du site annonçait déjà correctement partout ailleurs.

Vous m'avez écrit « plus de 2 000 foyers interrogés » : c'était mon erreur que
vous repreniez. La page affiche maintenant **1 211**, et le calcul est borné
par les effectifs par section — une ligne qui déclare nettement plus qu'eux ne
compte pas des ménages et sort du calcul. C'est écrit dans le code, pour que
personne n'y remette un `max()` dans six mois.

---

## Les quatre corrections demandées

**1. Le logo de la colonne de gauche.** Le fichier d'origine est un
verrouillage complet — l'emblème *plus* le mot « IRLA/APRI » — et il était
écrasé dans un carré blanc de 54 px : le sigle y devenait une bouillie de six
pixels de haut. J'ai découpé **l'emblème seul**, détouré en disque, et je le
pose directement sur le vert, sans carte blanche. Le nom reste du texte, avec
le filet vert de la charte. C'est du texte, donc c'est net à toutes les
tailles et cela suit la langue de l'interface.

**2. Plus aucun logo hors de la colonne de gauche.** Retiré des **neuf pages**
qui en portaient un en tête. Le logo du PNUE, qui était à droite de la barre
du haut, **descend au pied de la colonne**, sous le sélecteur de langue, à côté
de la mention institutionnelle. Les deux marques sont donc réunies au même
endroit, visibles en permanence, et le contenu n'en porte plus aucune.

**3. Les cinq tuiles de l'accueil sont supprimées.** Vous aviez raison : trois
d'entre elles n'apprenaient rien. Il reste **une ligne** — 10 sections
communales · 2 départements · 1 211 ménages enquêtés — suivie de la
**localisation** : les départements du Sud et de la Grand'Anse, dans le Grand
Sud d'Haïti, de la plaine littorale à l'intérieur montagneux, chaque section
enquêtée en entier avec une cible d'au moins 120 ménages.

**4. L'histoire d'APRI**, en quatre paragraphes, à la place du bloc « Le projet
APRI en bref » :

- **Le point de départ** — l'ouragan Melissa d'octobre 2025 : Haïti, qui n'a
  reçu que plusieurs jours de pluie, a compté 43 décès, autant que la Jamaïque
  touchée de plein fouet, quand la République dominicaine, sous des pluies
  comparables, en comptait un seul. Ce ne sont pas les aléas qui décident des
  pertes, mais l'état du territoire qui les reçoit.
- **Ce que mesure l'indice** — la résilience générale, sept dimensions, des
  capacités détenues *avant* le choc.
- **Comment il est construit** — les trois sources : enquête ménage stratifiée,
  vingt-cinq ans d'imagerie satellitaire, recensement des OCB.
- **Ce qu'il ne prétend pas dire** — la circularité de tout indice composite,
  l'absence de validation après choc réel, et la couverture réelle : 66 des
  128 lignes calculées à ce jour.

Ce dernier paragraphe n'est pas une précaution de style. C'est ce qui empêche
qu'un score soit cité comme une prévision dans une réunion où vous ne serez
pas.

---

## Deux défauts trouvés en vérifiant, corrigés au passage

**Le sous-titre des pages de dimension était encore faux.** J'avais renommé la
clé la semaine dernière, mais en lui laissant le texte de la page de
téléchargement : les pages de dimension affichaient donc toujours « Jeux de
données anonymisés ». C'était exactement ce que montrait votre capture
d'écran, et ma correction précédente ne l'avait pas réglé. Elles annoncent
maintenant « Résultats par section communale, et la source de chaque chiffre »,
et la synthèse a enfin son propre sous-titre.

**« Mouline » se coupait en « Moulin / e »** dans le cartouche « section la
moins bien placée ». Le rétrécissement automatique ne se déclenchait qu'à
partir de onze caractères, ce qui suffit sur la carte mais pas dans une
colonne quatre fois plus étroite. Le palier descend à sept.

---

## L'envoi

**Onze fichiers, un seul commit.** `app.py` refuse de démarrer si `i18n.py`
n'est pas à la version `2026-08-18-histoire` — c'est ce garde-fou qui vous
évite une page à moitié cassée.

| Fichier | Ce qui change |
|---|---|
| `assets.py` | l'emblème détouré, nouvelle image `EMBLEME_APRI` |
| `app.py` | marque de la colonne, logo PNUE en pied, plus de logo en barre du haut |
| `i18n.py` | 15 clés nouvelles, 3 corrigées, version `2026-08-18-histoire` |
| `accueil_page.py` | ligne de périmètre, localisation, histoire d'APRI |
| `map_render.py` | palier de rétrécissement à sept caractères |
| `synthese_page.py` | logo retiré, sous-titre propre |
| `dimension_page.py` | sous-titre corrigé |
| `methodologie_page.py`, `ocb_page.py`, `pistes_page.py`, `resilience_page.py`, `saillants_page.py`, `telechargements_page.py`, `environnement_page.py` | logo retiré de l'en-tête |

Sur GitHub : `Add file` → `Upload files`, glissez tout, un seul
`Commit changes`. Streamlit Cloud redéploie en une à deux minutes.

---

## Ce qui a été vérifié

- 21 modules compilent ; **96 rendus complets** de l'application — 12 pages ×
  4 combinaisons de filtres × 2 langues — **zéro exception** ;
- **781 clés** de traduction, aucun doublon, toutes avec un `fr` et un `en` ;
- **aucune clé brute** affichée à l'écran, dans les deux langues ;
- captures d'écran réelles du navigateur relues une par une : marque de la
  colonne, pied de colonne, accueil, page de dimension ;
- `i18n.VERSION` = `app.I18N_ATTENDU` = `2026-08-18-histoire`.

---

## Ce qui reste ouvert

- Les **fiches actions** portent encore l'ancien contenu « pistes ».
- Trois **fiches institutionnelles** (CASEC, école, santé) attendent leur
  section communale.
- **Dimension VII** : décision à prendre sur ses neuf proxys à composante
  unique.
- **Environnement** : érosion RUSLE (L59/L60), tampon marin au large pour
  L58/L61/L63, seconde date de mangrove pour L57.

*Le dépôt reste privé, le mot de passe se règle dans les Secrets de Streamlit
Cloud, et le jeu de données en ligne garde ses colonnes identifiantes vidées.*
