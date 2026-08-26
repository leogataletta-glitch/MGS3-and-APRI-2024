# Mise à jour — les sources du modèle causal

26 août 2026

Cette livraison répond à une seule demande : **citer la source à chaque fois
qu'un facteur chiffré est donné**, avec le nom de l'auteur, l'année et le titre
de la publication, et le dire en texte suivi plutôt qu'en fiche technique.

---

## Où va chaque fichier

| Fichier | Destination dans le dépôt |
|---|---|
| `graphe_causal.json` | **dans `data/`** — remplace `data/graphe_causal.json` |
| `si_je_change.py` | **à la racine** |
| `boucles_page.py` | **à la racine** |
| `boucles_moteur.py` | **à la racine** |
| `SOURCES_MODELE_CAUSAL.md` | **à la racine** (document de référence, l'application ne le lit pas) |

Les quatre premiers vont ensemble : `si_je_change.py` et `boucles_page.py`
lisent des champs que seul le nouveau `graphe_causal.json` contient. Il faut
donc les pousser **dans le même commit**, sinon l'application affiche une page
vide le temps que le second arrive.

Attention à `graphe_causal.json` : la page d'ajout de fichier de GitHub est liée
au dossier où l'on se trouve. Pour qu'il atterrisse dans `data/` et non à la
racine, il faut ouvrir `.../upload/main/data` et non `.../upload/main`.

---

## Ce qui a changé

### Les 82 liens portent maintenant une source réellement ouverte

Chacun des 82 liens du modèle a été cherché sur le web, sa source ouverte et
lue, sa taille d'effet relevée. **79 portent une source vérifiée. 3 n'en portent
aucune, et le disent** plutôt que d'en inventer une.

Cinq d'entre elles ont été rouvertes au hasard après coup pour contrôle : les
cinq correspondaient exactement à ce qui est écrit.

### Chaque chiffre est suivi de sa référence, dans la phrase

Le bloc « Repose sur » de l'onglet *Si je change une chose* n'est plus une fiche
de métadonnées mais un paragraphe qui se lit. La citation vient juste après le
chiffre qu'elle justifie, sous la forme demandée :

> **Accès à l'électricité** renforce **Revenu au-dessus du seuil**, avec une
> force de 0,50 et une classe de preuve « documentée ». La revue de la BID
> trouve une hausse moyenne du revenu des ménages électrifiés d'environ 30 %,
> médiane 18 %, mais huit études sur vingt-quatre ne trouvent aucun effet.
> (JIMENEZ MORI (2017), « Development Effects of Rural Electrification »,
> Banque interaméricaine de développement (note de politique), ouvrir la
> source) Contexte de l'étude : … Type de preuve : rapport institutionnel.
> *Réserve : …*

Le lien « ouvrir la source » ouvre l'URL réelle dans un nouvel onglet.

### Les forces ne sont plus les miennes

39 forces sur 82 ont changé, ajustées sur ce que la source mesure vraiment. Le
barème est publié dans la page, à cinq échelons :

| Force | Ce qu'elle veut dire |
|---|---|
| 0,20 | lien plausible, mécanisme indirect, aucune mesure |
| 0,35 | mécanisme direct, mais effet faible ou très dépendant du contexte |
| 0,50 | effet régulièrement observé, d'ampleur moyenne, dans plusieurs contextes |
| 0,65 | mécanisme direct, sources convergentes, effet de premier ordre |
| 0,80 | relation structurelle : l'un est une condition ou une composante de l'autre |

Répartition obtenue : 4 liens à 0,20 · 16 à 0,35 · 32 à 0,50 · 26 à 0,65 ·
4 à 0,80.

La classe de preuve plafonne la force qu'on a le droit de donner : un lien que
personne n'a mesuré ne peut pas recevoir le poids d'un lien mesuré. Classes
obtenues : 55 empiriques · 20 documentées · 3 structurelles · 2 théoriques ·
2 hypothèses.

Les colonnes `rho` et `p` ont été retirées. Elles étaient calculées sur les
moyennes de dix sections communales, soit dix points : deux seulement étaient
significatives, plusieurs avaient le signe contraire à la flèche, et le seul
lien classé « empirique » affichait rho = −0,01 avec p = 0,98. Elles donnaient
une apparence de mesure là où il n'y en avait pas.

### 8 liens dont la source contredit la flèche

Ils sont signalés en rouge là où ils apparaissent, pas retournés en douce.
Retourner une flèche est une décision de modélisation, elle t'appartient.

| Lien | Ce que trouve la source |
|---|---|
| Compte financier → Revenu | DUPAS et al. (2016) : ouvrir un compte n'augmente pas le revenu du travail |
| Sentiment de sécurité → Capital de passerelle | BAUER et al. (2016) : la violence renforce le lien interne, pas celui vers l'extérieur |
| Productivité agricole → Pratiques conservatrices | GOULART et al. (2023) : plus de rendement, plus de déforestation |
| Productivité agricole → Couvert forestier | GOULART et al. (2023) : effet Jevons, signe inverse |
| Productivité agricole → Maintien sur place | SADIDDIN et al. (2019) : l'insécurité alimentaire fait vouloir partir |
| Accès à l'électricité → Sentiment de sécurité | AEVARSDOTTIR et al. (2017) : effet nul mesuré |
| Couverture mobile → Revenu | AKER et FAFCHAMPS (2014) : pas d'effet sur les prix reçus |
| Sécurité foncière → Maintien sur place | DE JANVRY et al. (2015) : la certification fait PARTIR davantage |

Le détail complet, réserve par réserve, est dans `SOURCES_MODELE_CAUSAL.md`.

### Le modèle est maintenant bilingue jusqu'au bout

Le contexte de l'étude, le type de preuve et la réserve méthodologique
existaient seulement en français : en anglais, le paragraphe basculait au milieu
d'une phrase. Les trois champs ont une version anglaise (`geo_en`, `type_en`,
`reserve_en`), et les noms d'éditeurs institutionnels sont donnés dans la langue
de lecture — « Banque mondiale » en français, « World Bank » en anglais.

### Un avertissement devenu honnête

Écrites telles quelles, les nouvelles forces donnent au graphe un rayon spectral
de 1,10 : le système se tiendrait au bord de l'emballement, ce qui est absurde
sur une échelle qui s'arrête à dix. Les forces sont donc mises à l'échelle de
0,55 avant de propager. Le classement de ce qui bouge ne change pas, les
montants deviennent lisibles, et la page le dit à voix haute.

Le message correspondant est passé d'une erreur rouge (« chiffres non
exploitables ») à un avertissement : c'est une propriété du modèle, pas une
panne.

---

## L'ergonomie de « Si je change une chose » : on tourne les pages

Le contenu ne se déroule plus, il se tourne. La page est découpée en quatre
écrans, chacun tenant sur une hauteur d'écran :

1. **Ce qui bouge, et de combien** — les commandes et le tableau.
2. **Ce que valent les degrés** — les cinq seuils et ce qu'ils veulent dire.
3. **D'où vient ce chiffre** — les tours, la chaîne, la source.
4. **D'où viennent les forces** — le barème, les classes, la réserve.

En bas : le titre de l'écran, quatre traits de position dont un seul est plein,
le compteur, et deux flèches. Au changement d'écran, le contenu entre par un
fondu de 340 ms avec un léger glissement vers le haut. Techniquement, la clé du
conteneur Streamlit change avec le numéro d'écran, donc le nœud du DOM est neuf
et l'animation rejoue d'elle-même ; sans ce changement de clé, React réutilise
le même nœud et le fondu ne se voit qu'une fois.

Les commandes (quelle variable, de combien) restent au-dessus de la pagination,
visibles sur les quatre écrans : les répéter aurait chargé la page de ce qu'elle
cherche à alléger.

**Une réserve.** Les écrans 1 et 2 tiennent exactement sur une hauteur d'écran.
Les écrans 3 et 4 dépassent d'environ 180 et 280 pixels sur un écran de
1000 pixels de haut : le paragraphe des sources et le barème à cinq échelons
sont longs par nature. Il faudrait les couper en deux écrans de plus pour
supprimer tout défilement. Dis-moi si tu veux que j'y aille.

**C'est un essai, sur une seule page.** Si la mécanique te plaît, elle se
transpose aux autres pages longues (Rapport donateur, Boucles de rétroaction,
Analyse des résultats), et le code de pagination peut monter dans `app.py` pour
servir à tout le site.

---

## Ce qui reste ouvert, et qui demande ta décision

1. **Les 8 flèches contredites.** Faut-il en retourner certaines ? Elles sont
   laissées en place avec leur drapeau rouge.
2. **Le `graphe_causal.json` traîné à la racine du dépôt.** Rien ne le lit —
   l'application lit `data/graphe_causal.json` — mais il contredit désormais le
   modèle en service. Dis un mot et je le supprime.

---

## Vérifications passées avant livraison

- 104 rendus (13 pages × 4 combinaisons de filtres × 2 langues) : 0 problème.
- Les 395 champs de source réaccentués : après suppression des accents, chacun
  est strictement identique à l'original — donc rien d'autre que les accents n'a
  bougé.
- Les 82 réserves traduites : tous les chiffres, intervalles de confiance et
  tailles d'échantillon conservés à l'identique.
- Les 79 contextes d'étude traduits : idem, contrôle chiffre par chiffre.
- Copies d'écran des deux langues sur la page *Si je change une chose*.
