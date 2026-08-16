# Mise à jour — nouvel onglet « Données environnementales »

## Les 5 fichiers à mettre sur GitHub **dans le même commit**

| Fichier | Où | État |
|---|---|---|
| `app.py` | racine | remplacé |
| `i18n.py` | racine | **remplacé — c'est celui qui manquait** |
| `environnement_page.py` | racine | **nouveau** |
| `data/foret.json` | `data/` | **nouveau** |
| `data/saillants.json` | `data/` | remplacé |

`i18n.py` passe en version **`2026-08-16-environnement2`**.

Si ces fichiers de la livraison précédente ne sont pas encore poussés, ajoute-les
au même commit : `saillants_page.py`, `resilience_page.py`,
`data/resultats.json`, `data/ventilation.json`.

Toujours **pas** de `satellite\` ni de `pipeline\` sur GitHub.

---

## Pourquoi le bandeau rouge s'affichait

`app.py` était à jour, `i18n.py` non — il était resté sur
`2026-08-16-saillants-pistes`. Le garde-fou a fait exactement son travail.

---

## Le nouvel onglet, en cinq blocs

**1 · Les chiffres clés** — 10 713 ha boisés en 2000, 1 373 perdus, −0,54 %/an,
et le taux hors choc à −0,15 %/an posé juste à côté.

**2 · Année par année, 2001-2025.** C'est le bloc qui compte. Le graphique montre
une silhouette plate sur vingt-cinq ans, sauf une barre rouge en 2016 qui écrase
tout le reste : 686 hectares, l'ouragan Matthew. Un chiffre de déforestation lu
sans ce graphique décrirait un défrichement continu qui, pour la plupart des
sections, n'a pas eu lieu.

**3 · La carte**, avec six lectures au choix : couvert 2000, couvert 2025, part
du couvert perdue, taux annuel, taux hors choc, et part de la perte imputable à
2016-2018 — celle-ci sépare les sections frappées par la tempête de celles qui
se déboisent en continu.

**4 · Le tableau par section**, trié de la baisse la plus forte. La colonne du
choc est teintée : rouge pâle au-dessus de 60 %, bleu pâle en dessous de 20 %.
Barbois, Trichet, Anse à Drick, Mouline et Beaulieu sont en rouge — c'est la
tempête. Blactote est en bleu — c'est du défrichement continu. Ces sections ont
des taux voisins et n'appellent pas la même réponse.

**5 · Ce qui manque encore.** Les 36 indicateurs environnementaux non calculés,
regroupés par source, pour que la liste se lise comme un plan de travail :

- **Sentinel-2 / Landsat** — 4 indicateurs (NDVI, NDMI, NDWI, turbidité)
- **MODIS** — 3 (santé de la végétation, température de surface, TCI)
- **CHIRPS** — 4 (indices pluviométriques, SPI, aridité)
- **Carte d'occupation du sol** — 13 (fragmentation, connectivité, érosion)
- **Inventaires de terrain** — 6 (diversité des espèces)
- **Registres et atlas** — 5 (aires protégées, mangrove, herbiers)
- **Enquête ménage** — 1 (indice de diversité culturale : aucune donnée
  nouvelle nécessaire, calculable dès maintenant)

Un tableau de bord qui n'affiche que ce qu'il possède laisse croire que le reste
n'existe pas. Celui-ci dit ce qui manque et d'où ça viendrait.

---

## Détails de mise en forme

Le graphique annuel est un rendu dédié : une série temporelle se lit
horizontalement, les barres horizontales du reste de l'application conviennent à
un classement, pas à une chronologie.

Les surfaces sont affichées en entiers avec espace de millier, les taux à deux
décimales — à un dixième près, −0,5 et −0,54 se confondent alors qu'ils ne sont
pas dans la même classe de score.

## Prochaine étape

**CHIRPS**, pour les quatre indicateurs pluviométriques. Même mécanique
qu'aujourd'hui : un script Earth Engine avec tes polygones dedans, un export
CSV, une chaîne d'intégration. Et aucun arbitrage comparable au seuil de couvert
forestier.
