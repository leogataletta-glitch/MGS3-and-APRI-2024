"""Les indices composites du référentiel : huit lignes, huit compteurs.

CE QUE LE RÉFÉRENTIEL DEMANDE, ET CE QUE LA PLATEFORME EN FAISAIT.
Les huit lignes 119 à 126 ne sont pas des pourcentages. Chacune est un INDICE
COMPOSÉ DE VOLETS BINAIRES : le ménage satisfait ou non chacun des sept ou
huit volets que la métrique énumère, on les compte, et le barème note ce
compte — « 0(0) 1(1) 2(2) 3(3) 4(3,5) 5(4) … 10(8) », c'est-à-dire un score
sur dix pour un indice de zéro à huit. Les demi-valeurs du barème s'expliquent
d'elles-mêmes : le chiffre d'un groupe est la MOYENNE des indices de ses
ménages, et une moyenne n'est pas entière.

La plateforme, elle, publiait pour chacune la part de ménages ayant répondu
oui à UNE SEULE question — « compte voter aux prochaines élections », 77,6 % —
sous un barème qui attend un compte de zéro à huit. Le chiffre n'était pas
imprécis, il était d'une autre nature, et c'est pourquoi ces lignes portaient
« barème absent » : personne ne pouvait poser un barème de comptes sur un
pourcentage.

CE QUE FAIT CE MODULE. Il reconstruit le compte, volet par volet, à partir des
questions que l'enquête porte vraiment. Chaque volet nommé par le référentiel
est ici une ligne du tableau : soit un détecteur qui rend un booléen par
ménage, soit `None`, et `None` veut dire que l'enquête ne pose pas la
question. L'inventaire est donc lisible d'un coup d'œil, et il est publié avec
le résultat.

QUAND ON NOTE ET QUAND ON NE NOTE PAS. Une ligne dont tous les volets sont
disponibles se note : son indice va bien de zéro au maximum que le barème
attend. Une ligne à laquelle il manque des volets ne se note PAS, et pour une
raison mécanique et non par prudence : son indice plafonne sous le maximum du
barème, si bien qu'un ménage exemplaire y serait noté comme un ménage moyen.
La valeur est publiée quand même — elle compare les sections entre elles sur
les mêmes volets, ce que le barème ne fait pas mieux — et la liste des volets
manquants dit exactement quelles questions ajouter.

LES VOLETS QUI APPROCHENT SANS COÏNCIDER SONT MARQUÉS. Certains détecteurs ne
mesurent pas tout à fait le volet nommé : posséder un acte de naissance n'est
pas « avoir engagé une démarche administrative », c'est en être le résultat.
Ces volets portent un astérisque dans l'inventaire, et la note le dit.
"""

import numpy as np
import pandas as pd

# ------------------------------------------------------------- détecteurs


def _col(df, rang, motif):
    """La colonne à ce rang, si son intitulé le confirme. Sinon rien.

    LA DÉFAILLANCE EST SILENCIEUSE ET C'EST VOULU : si le questionnaire
    change, le volet disparaît de l'inventaire au lieu de désigner la
    mauvaise colonne. Un indice amputé se voit, un indice faux non.
    """
    if rang < len(df.columns) and motif.lower() in df.columns[rang].lower():
        return df.columns[rang]
    return None


def oui(rang, motif, valeur="Oui"):
    def f(df):
        c = _col(df, rang, motif)
        if c is None:
            return None
        return (df[c].astype(str).str.strip() == valeur).to_numpy()
    return f


def coche(rang, motif):
    def f(df):
        c = _col(df, rang, motif)
        if c is None:
            return None
        return (pd.to_numeric(df[c], errors="coerce") == 1).to_numpy()
    return f


def frequente(rang, motif):
    """Un groupe fréquenté : toute réponse sauf « Jamais »."""
    def f(df):
        c = _col(df, rang, motif)
        if c is None:
            return None
        v = df[c].astype(str).str.strip()
        return (df[c].notna() & (v != "Jamais")).to_numpy()
    return f


def positif(rang, motif):
    def f(df):
        c = _col(df, rang, motif)
        if c is None:
            return None
        return (pd.to_numeric(df[c], errors="coerce").fillna(0) > 0).to_numpy()
    return f


def parmi(rang, motif, valeurs):
    def f(df):
        c = _col(df, rang, motif)
        if c is None:
            return None
        return df[c].astype(str).str.strip().isin(valeurs).to_numpy()
    return f


def bloc_positif(debut, fin):
    """Au moins une colonne numérique strictement positive dans le bloc."""
    def f(df):
        if fin > len(df.columns):
            return None
        b = df[df.columns[debut:fin]].apply(pd.to_numeric, errors="coerce")
        return (b.fillna(0) > 0).any(axis=1).to_numpy()
    return f


def bloc_valeur(rangs, motif, valeurs):
    """Au moins une de ces colonnes portant l'une de ces réponses."""
    def f(df):
        if _col(df, rangs[0], motif) is None:
            return None
        v = np.zeros(len(df), dtype=bool)
        for r in rangs:
            if r < len(df.columns):
                v |= (df[df.columns[r]].astype(str).str.strip()
                      .isin(valeurs).to_numpy())
        return v
    return f


def bloc_classe(debut, fin, nuls=("Aucun",)):
    """Au moins une colonne du bloc portant une classe non nulle.

    LES QUANTITÉS D'ARBRES SONT DES TRANCHES, PAS DES NOMBRES : « 1 et 10 »,
    « 10 et 25 », « Entre 25 et 50 », « 100 et plus », et « Aucun ». Les lire
    comme des nombres rendait zéro partout et le volet disparaissait sans que
    rien ne le dise.
    """
    def f(df):
        if fin > len(df.columns):
            return None
        v = np.zeros(len(df), dtype=bool)
        for c in df.columns[debut:fin]:
            s = df[c].astype(str).str.strip()
            v |= (df[c].notna() & ~s.isin(nuls)).to_numpy()
        return v
    return f


def bloc_coche(rangs, motif):
    """Au moins une case cochée parmi celles-ci."""
    def f(df):
        c0 = _col(df, rangs[0], motif)
        if c0 is None:
            return None
        v = np.zeros(len(df), dtype=bool)
        for r in rangs:
            if r < len(df.columns):
                v |= (pd.to_numeric(df[df.columns[r]],
                                    errors="coerce") == 1).to_numpy()
        return v
    return f


def bloc_parmi(debut, fin, valeurs):
    """Au moins une cellule du bloc portant l'une de ces valeurs."""
    def f(df):
        if fin > len(df.columns):
            return None
        v = np.zeros(len(df), dtype=bool)
        for c in df.columns[debut:fin]:
            v |= df[c].astype(str).str.strip().isin(valeurs).to_numpy()
        return v
    return f


def texte(rang, motif, mots, contre=()):
    """Une réponse libre reclassée par mots-clés, français et créole.

    LES DEUX LANGUES SONT DANS LA MÊME COLONNE, et c'est le terrain qui en
    décide : « fumier », « fimye », « frimye » et « f8mye » désignent la même
    chose. Les mots-clés sont donc écrits sans accent et cherchés dans une
    chaîne elle-même mise à plat.
    """
    def f(df):
        c = _col(df, rang, motif)
        if c is None:
            return None
        s = (df[c].astype(str)
             .str.normalize("NFKD").str.encode("ascii", "ignore")
             .str.decode("ascii").str.lower())
        v = np.zeros(len(df), dtype=bool)
        for m in mots:
            v |= s.str.contains(m, regex=True, na=False).to_numpy()
        for m in contre:
            v &= ~s.str.contains(m, regex=True, na=False).to_numpy()
        return v & df[c].notna().to_numpy()
    return f


def ou(*fs):
    """Un volet satisfait par l'un ou l'autre de plusieurs signes."""
    def f(df):
        v = None
        for g in fs:
            x = g(df)
            if x is None:
                continue
            v = x if v is None else (v | x)
        return v
    return f


# ------------------------------------------------------- les mots du terrain

# Les pratiques agricoles traditionnelles, telles qu'elles sont écrites dans
# la réponse libre sur l'entretien de la fertilité — fumure, jachère,
# compost, paillage, rotation, ouvrages de conservation.
MOTS_FERTILITE = (r"fimye", r"fumier", r"frimye", r"f8mye", r"fumure",
                  r"jacher", r"zacher", r"sacher", r"repoz", r"po?ze",
                  r"repo\b", r"orepo", r"konpes", r"konpos", r"compost",
                  r"pail", r"pay\b", r"mulch", r"m[ui]r?ching",
                  r"rotasyon", r"rotation", r"wotasyon", r"asolman",
                  r"ranp", r"rampe", r"konsevasyon", r"conservation")
# Ce qui, dans la même colonne, dit qu'aucune pratique n'est appliquée.
MOTS_RIEN = (r"^anyen", r"^rien", r"^aucun", r"^ras$", r"^okenn",
             r"pa fe anyen", r"pa mete anyen", r"n'ai rien fait")

# Les engins de pêche que l'enquête distingue des engins introduits : la
# nasse, la ligne, la senne et la folle sont des techniques anciennes ; le
# compresseur et le DCP ne le sont pas.
PECHE_TRAD = (797, 798, 802, 803)

# Les matériaux de construction locaux : paille, terre, clissade, vétiver.
MATERIAUX_LOCAUX = (228, 229, 233, 237)

# Les cinq pièces d'état civil : en posséder une atteste d'une démarche
# administrative menée à son terme.
PAPIERS = (453, 454, 455, 456, 457)

AIDE_RECUE = (380, 381, 382)
AIDE_RENDUE = (386, 387, 388)


# ------------------------------------------------------------- l'inventaire
#
# Pour chaque ligne : le nombre de volets que le barème attend, puis un volet
# par entrée — son nom, son détecteur, et un drapeau disant si le détecteur
# coïncide avec le volet nommé ou s'en approche seulement.
#
# `None` comme détecteur veut dire : l'enquête ne pose pas cette question.

VOLETS = {
    119: {
        "attendus": 8,
        "volets": [
            ("participation aux dernières élections",
             oui(372, "vote aux dernieres elections"), True),
            ("démarches administratives menées à terme",
             bloc_valeur(PAPIERS, "acte de naissance",
                         ["Oui, je l'ai", "Demarches en cours"]), False),
            ("enfants scolarisés",
             positif(350, "enfants de plus de 6 ans scolarises"), True),
            ("arbres fruitiers plantés",
             bloc_classe(573, 590), True),
            ("intention de bâtir ou d'améliorer le logement", None, True),
            ("participation à des travaux collectifs d'intérêt général",
             ou(oui(375, "nettoyage ou d'entretien"),
                oui(391, "corvee agricole"),
                oui(374, "contribue financierement")), True),
            ("intention de rester dans la communauté",
             oui(476, "partir definitivement", "Non"), False),
            ("intention de créer ou de développer une activité économique "
             "locale", None, True),
        ],
    },
    120: {
        "attendus": 8,
        "volets": [
            ("existence d'espaces communautaires inclusifs",
             oui(367, "reunion communautaire"), False),
            ("règles coutumières sur l'usage des ressources naturelles",
             oui(368, "regle communautaire"), False),
            ("rituels et cérémonies liés à l'identité communautaire",
             None, True),
            ("règles locales encadrant la pêche ou l'usage des terres",
             None, True),
            ("codes de conduite dans le rapport à la nature", None, True),
            ("transmission de l'histoire locale et de la mémoire collective",
             None, True),
            ("références territoriales partagées",
             oui(5, "originaire de cette section"), False),
            ("participation active aux activités communautaires",
             ou(oui(375, "nettoyage ou d'entretien"),
                oui(391, "corvee agricole"),
                oui(377, "organisation communautaire de base")), True),
        ],
    },
    121: {
        "attendus": 7,
        "volets": [
            ("connaissance des plantes médicinales", None, True),
            ("techniques de conservation des aliments", None, True),
            ("pratiques agricoles et halieutiques traditionnelles",
             ou(texte(594, "fertilite de vos sols", MOTS_FERTILITE,
                      MOTS_RIEN),
                bloc_coche(PECHE_TRAD, "techniques de peche")), True),
            ("anticipation des aléas climatiques et environnementaux",
             None, True),
            ("navigation et lecture du milieu", None, True),
            ("construction en matériaux locaux",
             bloc_coche(MATERIAUX_LOCAUX, "materiaux de votre maison"), True),
            ("savoir-faire artisanal et sa transmission",
             coche(69, "artisanat"), False),
        ],
    },
    122: {
        "attendus": 6,
        "volets": [
            ("capacité perçue d'agir après une perte financière", None, True),
            ("capacité perçue d'agir face aux maladies des cultures",
             None, True),
            ("capacité perçue d'agir face aux aléas climatiques",
             ou(oui(362, "exercice de simulation"),
                parmi(361, "pris en compte le message",
                      ["Je leai compris et leai pris en compte"])), False),
            ("capacité perçue d'agir après un vol ou une mauvaise récolte",
             None, True),
            ("disposition à modifier ses pratiques", None, True),
            ("disposition à se déplacer pour améliorer ses conditions",
             None, True),
        ],
    },
    123: {
        "attendus": 8,
        "volets": [
            ("aide, travail ou nourriture reçus de la communauté",
             bloc_coche(AIDE_RECUE, "aide/service de la part"), True),
            ("aide, travail ou nourriture rendus à la communauté",
             bloc_coche(AIDE_RENDUE, "rendu un service/aide"), True),
            ("recours à un appui hors du ménage",
             parmi(518, "obtenir un credit",
                   ["Un proche dans la communaute",
                    "Un proche en dehors de la communaute",
                    "Mutuelle solidarite"]), True),
            ("participation à un groupe d'entraide ou de travail collectif",
             ou(oui(391, "corvee agricole"),
                oui(398, "mutuelle d'epargne")), True),
            ("arrangements collectifs pour l'école ou les soins",
             positif(451, "cantine scolaire"), False),
            ("contribution aux activités de la communauté",
             ou(oui(374, "contribue financierement"),
                oui(375, "nettoyage ou d'entretien")), True),
            ("résolution collective des problèmes",
             ou(oui(368, "regle communautaire"),
                oui(376, "comite de gestion communautaire")), True),
            ("appui hors du ménage en cas de souci",
             ou(coche(435, "soucis avec quelqu'un de confiance"),
                coche(436, "soucis avec quelqu'un de confiance"),
                coche(437, "soucis avec quelqu'un de confiance"),
                coche(434, "soucis avec quelqu'un de confiance")), True),
        ],
    },
    124: {
        "attendus": 6,
        "volets": [
            ("participation à une action civique",
             ou(oui(371, "manifestation publique ou une greve"),
                oui(368, "regle communautaire")), True),
            ("connaissance des droits fondamentaux", None, True),
            ("connaissance des mécanismes légaux", None, True),
            ("connaissance des institutions d'appui juridique", None, True),
            ("expérience d'une plainte ou d'une réclamation",
             bloc_parmi(419, 427, ["Tribunal", "Police", "Casec"]), True),
            ("lien avec une organisation de défense des droits",
             oui(377, "organisation communautaire de base"), False),
        ],
    },
    125: {
        "attendus": 8,
        "volets": [
            ("accueil perçu des nouveaux arrivants",
             oui(401, "nouveaux arrivants", "Non"), True),
            ("accès à des réseaux sociaux",
             ou(bloc_coche(AIDE_RECUE, "aide/service de la part"),
                bloc_coche(AIDE_RENDUE, "rendu un service/aide")), True),
            ("absence de discrimination", None, True),
            ("traitement équitable par les institutions",
             oui(352, "pot de vin", "Non"), False),
            ("hébergement de personnes déplacées",
             positif(458, "fuyant des zones d'insecurite"), True),
            ("accès à un appui économique",
             ou(oui(502, "transferts de fonds"),
                bloc_coche(AIDE_RECUE, "aide/service de la part")), True),
            ("accès aux services de base",
             parmi(342, "infrastructure de sante",
                   ["Moins de 15 minutes", "Entre 15 minutes et 30 minutes",
                    "Entre 30 minutes et 45 minutes",
                    "Entre 45 minutes et 1 heure"]), False),
            ("accès aux services éducatifs",
             parmi(344, "section primaire", ["Moins de 15 min", "Entre 15 et 30 min",
                             "Entre 30 min et 1h"]), False),
        ],
    },
    126: {
        "attendus": 6,
        "volets": [
            ("rôle des pratiques spirituelles dans le soutien moral",
             coche(434, "soucis avec quelqu'un de confiance"), True),
            ("solidarité portée par la pratique religieuse",
             frequente(393, "groupe de l'eglise"), True),
            ("coexistence pacifique entre croyances", None, True),
            ("respect du vivant fondé sur la croyance", None, True),
            ("recours à la croyance face à l'adversité", None, True),
            ("refus du fatalisme", None, True),
        ],
    },
}


# ---------------------------------------------------------------- calcul

def inventaire():
    """Ce que chaque ligne attend, ce qu'elle a, ce qui lui manque."""
    out = {}
    for ligne, spec in VOLETS.items():
        dispo = [(n, exact) for n, f, exact in spec["volets"] if f is not None]
        absents = [n for n, f, _ in spec["volets"] if f is None]
        out[ligne] = {
            "attendus": spec["attendus"],
            "disponibles": [n for n, _ in dispo],
            "approchants": [n for n, e in dispo if not e],
            "absents": absents,
            "complet": not absents,
        }
    return out


def construire(df):
    """{ligne: (base, indice)} — l'indice est le compte de volets satisfaits.

    LA BASE EST TOUT L'ÉCHANTILLON, ET C'EST JUSTE ICI. Un volet non
    satisfait vaut zéro, pas « inconnu » : ne pas avoir voté, ne pas avoir
    planté d'arbre, ne pas être membre d'un comité sont des réponses, et le
    ménage qui les cumule a bien un indice de zéro. C'est ce qui distingue un
    indice composite d'un taux, où l'absence de réponse retire du
    dénominateur.
    """
    out = {}
    for ligne, spec in VOLETS.items():
        n = np.zeros(len(df))
        pris = 0
        for _nom, f, _exact in spec["volets"]:
            if f is None:
                continue
            v = f(df)
            if v is None:
                continue
            n += np.asarray(v, dtype=float)
            pris += 1
        if not pris:
            continue
        out[ligne] = (np.ones(len(df), dtype=bool), n)
    return out


def maximum_atteignable(df):
    """Le plus haut indice qu'un ménage puisse atteindre, ligne par ligne.

    C'est le nombre de volets réellement détectés, et c'est lui qu'il faut
    comparer au maximum du barème pour savoir si la ligne peut être notée.
    """
    out = {}
    for ligne, spec in VOLETS.items():
        out[ligne] = sum(1 for _n, f, _e in spec["volets"]
                         if f is not None and f(df) is not None)
    return out


def _fmt(liste):
    return ", ".join(liste)


def resume(df, lang="fr"):
    """La phrase d'inventaire à écrire dans la note de chaque ligne."""
    inv = inventaire()
    mx = maximum_atteignable(df)
    out = {}
    for ligne, i in inv.items():
        d, a, ap = i["disponibles"], i["absents"], i["approchants"]
        if lang == "fr":
            t = (f"L'indice compte {len(d)} volets sur les {i['attendus']} "
                 f"que le barème attend. PRÉSENTS : {_fmt(d)}.")
            if ap:
                t += (f" DONT {len(ap)} QUI APPROCHENT SANS COÏNCIDER : "
                      f"{_fmt(ap)}.")
            if a:
                t += (f" ABSENTS DE L'ENQUÊTE : {_fmt(a)}. L'indice plafonne "
                      f"donc à {mx.get(ligne, len(d))} au lieu de "
                      f"{i['attendus']}, et la ligne n'est pas notée : un "
                      f"ménage satisfaisant TOUS les volets disponibles y "
                      f"serait noté comme un ménage moyen. La valeur est "
                      f"publiée telle quelle, elle compare les sections entre "
                      f"elles sur les mêmes volets.")
            else:
                t += (" Aucun volet ne manque : l'indice va bien de zéro au "
                      "maximum du barème, et la ligne est notée.")
        else:
            t = (f"The index counts {len(d)} parts out of the "
                 f"{i['attendus']} the scale expects. PRESENT: {_fmt(d)}.")
            if ap:
                t += (f" OF WHICH {len(ap)} COME CLOSE WITHOUT MATCHING: "
                      f"{_fmt(ap)}.")
            if a:
                t += (f" ABSENT FROM THE SURVEY: {_fmt(a)}. The index "
                      f"therefore tops out at {mx.get(ligne, len(d))} instead "
                      f"of {i['attendus']}, and the line is not scored: a "
                      f"household satisfying EVERY available part would be "
                      f"marked as an average one. The value is published as "
                      f"it stands, comparing sections on the same parts.")
            else:
                t += (" No part is missing: the index runs from zero to the "
                      "scale's maximum, and the line is scored.")
        out[ligne] = t
    return out


def notables(df):
    """Les lignes dont l'indice atteint le maximum du barème."""
    mx = maximum_atteignable(df)
    return {lg for lg, spec in VOLETS.items()
            if mx.get(lg, 0) >= spec["attendus"]}


if __name__ == "__main__":
    import os
    ici = os.path.dirname(os.path.abspath(__file__))
    d = pd.read_csv(os.path.join(ici, "data", "donnees_anonymisees.csv"),
                    low_memory=False)
    inv = inventaire()
    mx = maximum_atteignable(d)
    ind = construire(d)
    sec = d[d.columns[3]]
    print(f"{'ligne':>5} {'volets':>8} {'attendus':>9} {'indice moyen':>13}"
          f"   note ?")
    for lg in sorted(VOLETS):
        base, v = ind[lg]
        print(f"{lg:>5} {mx[lg]:>8} {inv[lg]['attendus']:>9} "
              f"{v[base].mean():>13.3f}   "
              f"{'OUI' if mx[lg] >= inv[lg]['attendus'] else 'non'}")
    print()
    for lg in sorted(VOLETS):
        base, v = ind[lg]
        par = pd.DataFrame({"s": sec, "v": v}).groupby("s")["v"].mean()
        print(f"{lg} : " + "  ".join(f"{k[:9]} {x:.2f}"
                                     for k, x in par.items()))
