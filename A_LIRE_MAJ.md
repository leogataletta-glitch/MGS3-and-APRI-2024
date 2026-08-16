# Mise à jour — la pluie passe à la campagne agricole

## Les 6 fichiers à mettre sur GitHub **dans le même commit**

| Fichier | Où | État |
|---|---|---|
| `app.py` | racine | remplacé |
| `i18n.py` | racine | remplacé |
| `environnement_page.py` | racine | remplacé |
| `data/resultats.json` | `data/` | remplacé |
| `data/ventilation.json` | `data/` | remplacé |
| `data/pluie_saison.json` | `data/` | **nouveau** |

`i18n.py` passe en version **`2026-08-16-saison`**.

---

## Le résultat, en une phrase

Sur l'année civile, le Grand Sud reçoit **96 % de sa pluie normale**. Sur la
campagne de printemps, il en reçoit **83 %**. Même satellite, même normale,
même période — diagnostic inverse.

L'écart vient de la saison cyclonique. Une tempête d'octobre reconstitue le
cumul annuel après la récolte, sans rien reconstituer dans les champs.
Additionner mars-mai avec septembre-novembre fabrique une année moyenne que
personne n'a vécue.

Cela tranche un désaccord qui traînait depuis le début : **48,7 % des ménages
citent la sécheresse** comme première cause de baisse des rendements. Sur la
donnée annuelle, cette perception paraissait démentie par le satellite. Sur la
donnée saisonnière, elle est confirmée. Les ménages avaient raison ; c'est la
fenêtre de calcul qui avait tort.

---

## 1 · Les quatre indicateurs passent sur mars-avril-mai

Aucun barème IRLA ne fixe de période d'accumulation — le choix nous revenait.

| Section | Campagne normale | 5 dernières | Part | 43 | 44 | 45 | 46 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Trichet | 274 mm | 272 | 99 % | 3 | 5 | 10 | 10 |
| Barbois | 294 | 270 | 92 % | 3 | 5 | 9 | 10 |
| Anse à Drick | 290 | 257 | 88 % | 2 | 5 | 8 | 10 |
| Mouline | 590 | 498 | 85 % | 2 | 5 | 8 | 9 |
| Débouchette | 218 | 182 | 84 % | 2 | 5 | 8 | 10 |
| Quentin | 250 | 203 | 81 % | 2 | 5 | 8 | 6 |
| Dalmette | 256 | 205 | 80 % | 2 | 4 | 8 | 6 |
| Blactote | 254 | 194 | 76 % | 2 | 4 | 7 | 5 |
| Beaulieu | 206 | 151 | 73 % | 2 | 4 | 7 | 7 |
| Dumont | 193 | 140 | 73 % | 1 | 4 | 7 | 9 |

**La réserve que je t'avais signalée est levée.** Sur l'annuel, l'aridité
anormale valait 5 partout et le SPI 10 partout : deux indicateurs pesant 4,8 %
de l'indice sans distinguer aucun territoire. Sur la campagne, les quatre
discriminent. La contribution pluviométrique va maintenant de 43 à 67 points
pondérés selon les sections, contre un quasi-plat auparavant.

Tu n'as donc plus la décision à prendre sur le retrait des lignes 44 et 46.

### Le score final baisse de 0,08 point

| | avant | après |
|---|---:|---:|
| Ensemble | 4,46 | **4,38** |
| Plus forte baisse — Blactote | 4,32 | 4,15 |
| Seule hausse — Trichet | 5,08 | 5,10 |

56 indicateurs scorés sur 128, inchangé. La baisse est faible parce que quatre
indicateurs sur cinquante-six pèsent peu ; elle est réelle parce qu'elle
corrige une surestimation.

### Une décision de méthode à connaître

**Le SPI est évalué sur la pire des cinq dernières campagnes, pas sur leur
moyenne.** Ce n'est pas un choix d'opportunité : le barème publié du SPI ne
gradue que la sécheresse, de −2,0 à −1,0, et une moyenne de cinq ans n'atteint
pratiquement jamais ce domaine — elle lisse par construction ce que le barème
est fait de mesurer. Sur la moyenne, les dix sections obtenaient 10. Sur la
pire campagne, elles obtiennent de 5 à 10, et l'écart correspond à un fait
réel : la sécheresse de 2021 a frappé la Grand'Anse bien plus durement que le
Sud.

La résilience se mesure d'ailleurs à la mauvaise année. Un territoire dont les
campagnes sont bonnes en moyenne mais qui perd tout une année sur cinq n'est
pas résilient, il est chanceux quatre ans sur cinq.

Les lignes 43, 44 et 45 restent sur la moyenne des cinq campagnes : elles
répondent à « comment va le territoire en ce moment », et une moyenne est le
bon outil pour cela.

Si tu préfères revenir à la moyenne pour le SPI aussi :
`python compute_pluie_saisonniere.py <csv1> <csv2> --moyenne-spi`

---

## 2 · Un bloc « La campagne agricole » dans l'onglet environnemental

C'est le bloc 7 ; l'ancien bloc 7 (ce qui manque encore) devient le 8.

Quatre chiffres clés par section — campagne normale, cinq dernières campagnes,
date d'installation de la saison, jours à 50 mm et plus — puis la série
mars-mai de 1981 à 2025 en barres divergentes autour de la normale, puis un
tableau des dix sections.

### Trois grandeurs nouvelles, non scorées

Séquences sèches, pluies extrêmes et date d'installation **ne portent aucun
score et n'entrent pas dans l'indice**. Elles sont absentes de la table IRLA,
et y ajouter des indicateurs maison rendrait l'indice incomparable avec les
autres applications du cadre. Elles sont descriptives — et c'est là leur
valeur, elles disent ce que la moyenne cache.

**Ce qu'elles disent, justement :**

**Les pluies extrêmes augmentent partout.** Sans une seule exception sur dix
sections. Blactote passe de 1,5 à 2,7 jours à 50 mm et plus par an entre
1981-2000 et 2006-2025, Quentin de 1,8 à 2,9, Beaulieu de 1,7 à 2,6. Sur un
territoire qui a perdu **12,8 % de son couvert forestier** depuis 2000 et où
**76,2 % des ménages** ne sont pas sûrs de conserver leur parcelle l'an
prochain — donc n'aménagent pas la pente — c'est le signal le plus inquiétant
du lot. Pas la sécheresse seule, mais la sécheresse **et** l'averse.

**Les séquences sèches de printemps s'allongent dans huit sections sur dix.**
Quentin passe de 22,3 à 26,9 jours consécutifs sans pluie pendant la campagne.
Vingt-sept jours sans pluie au milieu de mars-mai, sur un territoire où 52 %
des ménages n'ont aucune source d'irrigation, décide d'une récolte.

**La date d'installation ne se déplace pas nettement** — quelques jours dans un
sens ou dans l'autre selon les sections, rien de systématique. Mais le compte
des campagnes **sans départ net** est éloquent : 16 sur 45 à Dumont, 14 à
Débouchette, 12 à Beaulieu. Une campagne sur trois y est semée sans que la
saison se soit franchement installée. Ce n'est pas une donnée manquante, c'est
une agriculture qui parie.

Définition retenue pour l'installation, celle du CILSS/AGRHYMET : première
décade à partir du 1er mars recevant 25 mm, suivie d'une décade à 20 mm. La
seconde condition écarte les averses isolées qui font germer puis laissent
périr — le faux départ, qui coûte au ménage une semence entière.

---

## Ce qui reste

**32 indicateurs environnementaux** non calculés. Le plus accessible ensuite :
MODIS pour la température de surface (lignes 36, 41, 42), ou Sentinel-2 pour
les indices de végétation (33, 34, 35, 63).

Je peux aussi ajouter les données satellitaires au bloc **Téléchargements** —
forêt, pluie annuelle, pluie saisonnière — si tu le veux. Dis-le-moi.
