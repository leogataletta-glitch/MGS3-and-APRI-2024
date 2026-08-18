# Mise à jour — le ruban vert, la charte APRI

## Ce qui change à l'écran

**Un ruban vert plein cadre en haut de page**, dans le même vert que la colonne
de gauche : les deux ne font plus qu'un encadrement, et le contenu blanc s'y
pose comme une feuille. Il porte les **onglets en pastilles** — l'onglet courant
en vert clair, les autres qui s'éclaircissent au survol — et, à droite, le
**logo du PNUE en réserve**, blanc sur le vert.

Ce logo blanc est une image nouvelle : la version d'origine est cyan sur fond
blanc, et posée telle quelle sur le vert elle aurait fait une étiquette collée.
Je l'ai détourée et passée en blanc, le tracé anticrénelé conservé.

**Deux chemins vers les mêmes pages, et c'est voulu.** La colonne de gauche se
lit ligne à ligne quand on cherche ; le ruban se parcourt du regard quand on
sait déjà où l'on va. Les deux listes sont construites à partir d'une **source
unique** dans le code, pour qu'elles ne puissent jamais diverger — c'est le
seul vrai risque de ce genre de doublon.

**Le bloc de marque** de la colonne suit la charte : l'emblème à 58 px, APRI en
34 px, le filet vert, puis l'accroche sur deux niveaux — *Observatoire de la
résilience des paysages* en vert clair, *Sud et Grand'Anse, Haïti* en blanc.

**Le bandeau de paysage** passe à 300 px et déborde comme le ruban, sans liseré
blanc entre les deux.

## Trois points techniques, si un jour ça bouge

**La pleine largeur.** Le contenu du site reste borné à 1240 px — une ligne qui
court sur 1900 px ne se lit pas. Le ruban, lui, doit toucher les deux bords :
sa largeur est `calc(100vw - 310px)`, où 310 px est la largeur fixe de la
colonne de gauche. Si un jour vous changez cette largeur, **changez les deux
valeurs ensemble**, sinon le ruban dépasse à droite et le logo du PNUE sort de
l'écran.

**Streamlit ne sait pas encadrer une rangée de boutons.** Chaque appel à
`st.markdown` vit dans son propre conteneur : une balise ouverte dans l'un et
fermée dans le suivant ne s'emboîte jamais. On glisse donc une ancre invisible
dans la rangée, et le CSS habille la rangée **qui la contient**, via `:has()`.

**L'en-tête de Streamlit** est rendu transparent et sans hauteur pour que le
ruban touche le haut de la fenêtre. Son bouton de menu reste cliquable
au-dessus ; le logo du PNUE garde 44 px de dégagement à droite pour ne pas
passer dessous.

## Deux suppressions

Le **nom de la page** n'apparaît plus sous le bandeau : le ruban le montre déjà
en pastille verte et chaque page le répète en titre. Trois fois le même mot
dans les cent premiers pixels, c'était deux fois de trop. Il ne reste que le
rappel du filtre actif — un chiffre lu sans savoir qu'un filtre est posé est un
chiffre mal lu.

Le **logo du PNUE en pied de colonne** disparaît, puisqu'il est maintenant en
haut à droite. La mention institutionnelle en toutes lettres reste.

## L'envoi

**Trois fichiers, un seul commit.** `app.py` refuse de démarrer si `i18n.py`
n'est pas à la version `2026-08-18-ruban`.

| Fichier | Ce qui change |
|---|---|
| `app.py` | le ruban, les onglets, le bloc de marque, le bandeau |
| `assets.py` | `LOGO_UNEP_BLANC`, le logo du PNUE en réserve |
| `i18n.py` | la clé `a_lieu`, version `2026-08-18-ruban` |

Sur GitHub : `Add file` → `Upload files`, les trois, un seul `Commit changes`.

## Vérifié

- 21 modules compilent ; **96 rendus complets** — 12 pages × 4 combinaisons de
  filtres × 2 langues — **zéro exception** ;
- **782 clés** de traduction, aucun doublon, toutes avec un `fr` et un `en` ;
- aucune clé brute affichée, dans les deux langues ;
- navigation testée dans le navigateur : cliquer un onglet du ruban change bien
  de page, et la colonne de gauche suit — les deux restent d'accord.
