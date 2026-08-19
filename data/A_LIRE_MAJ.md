# Un onglet « Résilience environnementale » dans le cadre de résilience

## Trois fichiers, MÊME commit

| Fichier | Où | |
|---|---|---|
| `environnement_cadre.py` | **racine** | **nouveau** — l'onglet entier |
| `cadre_page.py` | **racine** | modifié — la page devient deux onglets |
| `cadre_environnement.json` | **`data/`** | **nouveau** — la note de cadrage, extraite |

> **Si la page ne change pas après l'envoi**, c'est que `cadre_page.py` n'est
> pas monté : c'est lui qui porte à la fois la refonte en trois strates de la
> livraison précédente **et** les deux onglets. Vérifiez sa date sur GitHub.

## Ce que contient l'onglet

Il suit la même logique de strates que le reste de la page.

**Comprendre.** Quatre cartes — ce qui est mesuré, les trois sources, ce que
valent 0 et 10 ici, et ce qui est calculé à ce jour. Puis le protocole en
quatre chiffres : **6 indicateurs de terrain › 33 satellitaires › 32 côtiers et
hydro › 5 proxys d'enquête**. Tous comptés dans le document, pas saisis à la
main.

**Explorer.** Les trois sources, chacune avec le texte de la note :

- **les relevés de terrain** et les trois taxons — odonates, oiseaux,
  pollinisateurs — avec le paragraphe qui explique pourquoi chacun est un bon
  proxy, et la note sur les transects d'anthropisation ;
- **l'imagerie satellitaire**, avec ses quatre familles chiffrées : végétation
  11, fragmentation 10, connectivité 12, littoral 25 ;
- **l'enquête ménage** et ses cinq familles de proxys.

Puis, **face à face, ce que la plateforme calcule et ce qu'elle ne calcule
pas** : 17 indicateurs environnementaux scorés d'un côté, 21 décrits mais
absents de l'autre. Les deux listes sont lues dans `resultats.json`, pas
écrites.

**Approfondir.** Sept volets fermés, qui contiennent la note en entier :

| Volet | |
|---|---|
| Relevés de terrain | les 6 indicateurs, leur unité d'observation, et **le scénario du 0 face au scénario du 10** pour chacun des trois taxons |
| Végétation et productivité | 11 indicateurs, ce qu'ils mesurent, le lien avec la résilience, les seuils |
| Fragmentation du paysage | 10 indicateurs |
| Connectivité | 12 indicateurs |
| Résilience côtière | les 6 familles — turbidité, mangroves, herbiers, récifs, dynamique littorale, indices intégrés — avec leur contexte haïtien et le verdict de faisabilité |
| Pressions, hydrologie et climat | le paragraphe de pression et les 7 indicateurs hydro-climatiques |
| Proxys d'enquête ménage | les cinq familles, en entier |

## Trois décisions à contester si elles ne vous vont pas

**Les seuils restent en français dans l'interface anglaise.** Un seuil traduit
n'est plus le seuil du document source, et cette page est une annexe de
méthode : on doit pouvoir la citer. Une mention le dit à l'écran. Si vous
voulez la traduction, elle se fait, mais elle devient votre texte et non plus
la note.

**Le contenu est dans un JSON, pas dans le code.** La note évoluera ; ce sera
alors `data/cadre_environnement.json` à remplacer, sans toucher au module.

**La page dit ce qui n'est pas fait.** Le protocole décrit six indicateurs de
terrain ; zéro est calculé, faute de relevés. C'est écrit en toutes lettres
dans la carte « ce qui est calculé à ce jour ». Une annexe de méthode qui
laisserait croire que le dispositif est complet se retournerait contre lui à
la première question d'un évaluateur.

## Un défaut corrigé en route

La liste « calculés / pas encore calculés » s'affichait **en anglais dans la
page française**. La fonction lisait la langue à l'intérieur d'un calcul mis en
cache : la première langue affichée figeait les noms pour l'autre. La langue
est devenue un argument de la fonction, donc une clé de cache.

## Vérifié

- **66 rendus** — 11 pages × 3 combinaisons de filtres × 2 langues — zéro
  exception, zéro clé de traduction brute ;
- onglet ouvert au navigateur dans les deux langues : les deux onglets
  répondent, les sept volets sont fermés à l'ouverture, les listes sont dans
  la bonne langue, et les comptes affichés correspondent au document
  (6 · 33 · 32 · 5) et au fichier de résultats (17 · 21).
