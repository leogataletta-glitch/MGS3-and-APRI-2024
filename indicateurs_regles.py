"""Les indicateurs qui se calculent par une RÈGLE sur les réponses, et non
par une modalité cochée.

POURQUOI CE MODULE EXISTE.
Le moteur de croisement construit ses indicateurs à partir des modalités du
questionnaire : « a coché telle réponse » devient un vecteur de 1 211 booléens,
et tout le reste en découle. C'est ce qui rend le croisement instantané, et
c'est aussi ce qui lui interdit certains indicateurs pourtant présents dans
l'enquête. Le taux de surpeuplement en est l'exemple : personne n'a coché
« mon logement est surpeuplé ». La réponse est dans DEUX questions numériques
— combien de personnes, combien de pièces — et dans une règle qui les
combine. Le référentiel la publie, l'enquête la porte, et la plateforme la
déclarait absente.

CE QU'UNE RÈGLE DOIT RENDRE.
Exactement ce qu'une modalité rend : une BASE — les ménages sur lesquels
l'indicateur a un sens, ceux qui ont répondu aux deux questions — et une
CIBLE, ceux qui remplissent le critère. Le reste de la plateforme ne voit
aucune différence : le score se calcule sur n'importe quel sous-groupe, il se
ventile par sexe, par catégorie économique, par section, et il entre dans
l'indice avec son poids.

L'ORDRE DES LIGNES EST LE MÊME QUE CELUI DE LA MATRICE.
`croisement.npz` a été construit depuis ce même CSV, et la concordance est
vérifiée ligne à ligne au chargement : sans elle, un masque calculé ici
désignerait d'autres ménages que ceux du moteur, et l'erreur serait
silencieuse. Si la vérification échoue, aucune règle n'est rendue.
"""

import os
import re

import numpy as np
import pandas as pd

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

COL_SECTION = "Dans quelle section communale reside le repondant ?"
# Les libellés du CSV sont sans accents ; ceux du référentiel les portent.
NORM = {"Anse e Drick": "Anse à Drick", "Debouchette": "Débouchette"}

# LES TROIS COLONNES, DÉSIGNÉES PAR LEUR RANG ET VÉRIFIÉES PAR LEUR INTITULÉ.
# Le rang seul casserait à la première colonne insérée ; l'intitulé seul
# casserait à la première correction d'orthographe. Les deux ensemble tiennent.
COLS = {
    "adultes": (13, "adultes vivent dans votre foyer"),
    "enfants": (40, "enfants avez-vous"),
    "pieces": (226, "pieces votre logement"),
    "agriculture": (521, "pratiquez-vous, vous meme, l'agriculture"),
    # LES VINGT-TROIS COLONNES DE CULTURE, une par espèce, prises comme un
    # bloc : leur intitulé est le nom de la culture, il n'y a donc rien à
    # reconnaître dans le texte. La colonne « ne souhaite pas répondre » est
    # hors du bloc, volontairement.
    "cultures": (523, 546),
    "peche": (793, "pratiquez vous, vous meme, la peche"),
}

# LE MODULE ÉLEVAGE : quatre effectifs et quatre mortalités, dans le même
# bloc du questionnaire et dans le même ordre. Le rapprochement se vérifie de
# lui-même — 452 ménages sur 455 qui déclarent un effectif de volailles
# déclarent aussi sa mortalité. Les colonnes « Taille elevage » du module
# agricole, plus haut dans le questionnaire, ne se recoupent qu'à moitié avec
# ces mortalités : ce sont deux modules différents, et les mélanger ferait
# diviser les morts d'un troupeau par l'effectif d'un autre.
CHEPTEL = {
    "volailles": (907, 915, "volailles possedez-vous"),
    "porcins": (908, 916, "porcins possedez-vous"),
    "caprins": (909, 917, "caprins possedez-vous"),
    "bovins": (910, 918, "bovins possedez-vous"),
}

# LES UNITÉS ANIMALES DU RÉFÉRENTIEL, telles qu'il les écrit : bovin adulte
# 1 UA, équidé 0,8, porcin 0,2, caprin et ovin 0,1. IL N'EN DONNE PAS POUR LA
# VOLAILLE, et c'est le seul coefficient ajouté ici : 0,01, l'unité de bétail
# tropical usuelle de la FAO. Le choix n'est pas neutre — la volaille est
# l'animal le plus nombreux et le plus perdu — et le taux est donc publié
# aussi sans elle, pour que l'effet du coefficient se voie.
UA = {"volailles": 0.01, "porcins": 0.2, "caprins": 0.1, "bovins": 1.0}

# LES DEUX BLOCS AGRICOLES, quarante colonnes chacun, une par culture, dans le
# même ordre : le rendement de la dernière campagne, puis la part perdue. La
# concordance est vérifiée nom à nom au chargement — à une faute de frappe
# près, « Babane » pour « Banane », qui est la même culture à la même place.
RENDEMENTS = (604, 644)
PERTES = (752, 792)

# LES VINGT-SEPT COLONNES D'ESPÈCES PÊCHÉES. La cellule ne dit pas combien on
# en prend mais OÙ on la prend : « Plateau » ou « Grand fond ». Une seule
# question porte donc les deux indicateurs de pêche du référentiel, le nombre
# d'espèces et l'exclusivité du plateau.
ESPECES = (816, 843)

# LES HUIT COLONNES DE MODE DE RÈGLEMENT, une par type de conflit. La cellule
# porte la voie empruntée — tribunal, médiation d'un proche, police, CASEC,
# responsable religieux, ONG — et rien d'autre : le questionnaire ne code
# aucune issue violente.
MODES_CONFLIT = (419, 427)

# LES TREIZE CANAUX DE PARTICIPATION COLLECTIVE, tels que la métrique de la
# ligne 98 les énumère : travail communautaire, associations, groupes
# religieux, groupes d'épargne, réseaux informels.
CANAUX = (
    (374, "contribue financierement", "oui"),
    (375, "nettoyage ou d'entretien", "oui"),
    (376, "comite de gestion communautaire", "oui"),
    (377, "organisation communautaire de base", "oui"),
    (391, "corvee agricole", "oui"),
    (393, "groupe de l'eglise", "freq"),
    (394, "association de quartier", "freq"),
    (395, "ocb/association", "freq"),
    (396, "groupe d'amis", "freq"),
    (397, "groupe politique", "freq"),
    (398, "mutuelle d'epargne", "oui"),
)
AIDE_RECUE = (380, 381, 382)
AIDE_RENDUE = (386, 387, 388)
# En deçà, l'absence de « oui » ne prouve rien : c'est une non-réponse.
CANAUX_MIN = 8

# LA FENÊTRE D'ÂGE DE LA LIGNE 94, posée ici et non dans le référentiel, qui
# écrit « quinze ans et plus ». Voir la fonction pour le raisonnement.
AGE_FILLES = (15, 24)

PIECES_MAX = 15
SEUIL_PERS_PIECE = 3.0

# Les classes de rendement, en kg, prises à leur milieu ; les deux classes
# ouvertes sont prises à une valeur voisine de leur borne.
CLASSES_KG = {"-de50": 25.0, "50-100": 75.0, "100-250": 175.0,
              "250-500": 375.0, "500-750": 625.0, "750-1000": 875.0,
              "+de1000": 1250.0}
# Les classes de perte, en pourcentage. Les valeurs pleines sont des nombres.
CLASSES_PERTE = {"-de10": 5.0, "+de90": 95.0}


def _colonne(df, cle):
    rang, motif = COLS[cle]
    if rang < len(df.columns) and motif.lower() in df.columns[rang].lower():
        return df.columns[rang]
    for c in df.columns:
        if motif.lower() in c.lower():
            return c
    return None


def _lire():
    p = os.path.join(DATA, "donnees_anonymisees.csv")
    if not os.path.exists(p):
        return None
    return pd.read_csv(p, low_memory=False)


def _surpeuplement(df):
    """SDG 11.1.1 : plus de trois personnes par pièce habitable.

    LE CRITÈRE EST CELUI D'ONU-HABITAT, pas un seuil choisi ici : un logement
    offre une surface habitable suffisante si pas plus de trois personnes ne
    partagent une même pièce. La superficie, elle, n'est pas demandée dans
    l'enquête, et c'est justement pourquoi la règle des personnes par pièce
    existe — elle a été écrite pour les enquêtes qui ne mesurent pas les
    mètres carrés.

    DEUX RÉSERVES, ET ELLES VONT DANS LE MÊME SENS. La question sur les
    enfants compte ceux « à charge dans ET en dehors du foyer » : un ménage
    dont un enfant vit ailleurs est donc compté trop grand, et le taux obtenu
    est un MAJORANT. Un logement déclaré à plus de quinze pièces est écarté
    comme faute de saisie — il y en a un, à deux cents pièces.
    """
    ca, ce, cp = (_colonne(df, k) for k in ("adultes", "enfants", "pieces"))
    if not (ca and cp):
        return None
    ad = pd.to_numeric(df[ca], errors="coerce")
    en = (pd.to_numeric(df[ce], errors="coerce") if ce
          else pd.Series(0, index=df.index))
    pc = pd.to_numeric(df[cp], errors="coerce")
    pc = pc.where((pc >= 1) & (pc <= PIECES_MAX))
    taille = ad.fillna(0) + en.fillna(0)
    base = (pc.notna() & ad.notna() & (taille > 0)).to_numpy()
    ratio = (taille / pc).to_numpy(dtype=float)
    cible = base & (ratio > SEUIL_PERS_PIECE)
    return base, cible


def _diversite_cultures(df):
    """CDI = 1 − Σ pᵢ², la diversité de Simpson des cultures d'un ménage.

    LES PARTS SONT ÉGALES ENTRE CULTURES, ET C'EST UNE APPROXIMATION QU'IL
    FAUT DIRE. La formule du référentiel demande la part de chaque culture, et
    l'enquête a bien posé la superficie dédiée à chacune — mais le jeu de
    données rend ces superficies en classes dont le libellé est corrompu :
    « e » y apparaît 1 716 fois sur 3 442 réponses, à côté de « 1/16 », « 1 »
    et « + de 3 ». Un « e » seul est ce qui reste d'un libellé fait de
    fractions et d'un « à » ; on ne peut pas deviner laquelle. Faute de
    pondérer, chaque culture reçoit une part égale, si bien que le CDI vaut
    1 − 1/n pour un ménage cultivant n espèces. C'est la richesse spécifique,
    pas l'équitabilité : deux ménages cultivant les quatre mêmes espèces
    obtiennent le même indice, que l'un consacre 90 % de sa terre au maïs ou
    non. Le jour où le libellé des classes de surface est retrouvé, la même
    fonction pondère et l'indice devient celui du référentiel.

    LA BASE, CE SONT LES CULTIVATEURS. Un ménage qui ne cultive pas n'a pas un
    indice de diversité nul, il n'en a pas : le compter à zéro ferait baisser
    la note d'une section pêcheuse pour une raison qui n'a rien d'agricole.
    """
    c_agri = _colonne(df, "agriculture")
    if not c_agri:
        return None
    debut, fin = COLS["cultures"]
    if fin > len(df.columns):
        return None
    noms = list(df.columns[debut:fin])
    pres = df[noms].notna() & (df[noms].astype(str) != "?")
    n = pres.sum(axis=1).to_numpy()
    agri = (df[c_agri].astype(str) == "Oui").to_numpy()
    base = agri & (n > 0)
    val = np.where(n > 0, 1.0 - 1.0 / np.maximum(n, 1), 0.0)
    return base, val


def _col_rang(df, rang, motif):
    """Une colonne désignée par son rang et vérifiée par son intitulé."""
    if rang < len(df.columns) and motif.lower() in df.columns[rang].lower():
        return df.columns[rang]
    return None


def _nom_culture(c):
    """Le nom d'une culture, sans le suffixe que l'export ajoute aux
    colonnes homonymes : « Banane.7 » et « Banane » sont la même culture."""
    return re.sub(r"\.\d+$", "", str(c)).strip()


def _perte_cheptel(df):
    """Ligne 83 : capital d'élevage perdu en douze mois, en unités animales.

    LE TROUPEAU DE DÉPART SE DÉDUIT, IL N'EST PAS DEMANDÉ. L'enquête donne
    l'effectif d'aujourd'hui et le nombre de morts de l'année : le troupeau
    d'il y a un an valait donc l'effectif actuel plus les morts, et le
    troupeau MOYEN de l'année — ce que le référentiel demande au
    dénominateur — vaut l'effectif actuel plus la moitié des morts. C'est la
    convention démographique ordinaire, et elle explique pourquoi un ménage
    peut déclarer vingt volailles mortes et cinq vivantes sans se contredire :
    il en avait vingt-cinq.

    DEUX RÉSERVES QUI NE TIRENT PAS DANS LE MÊME SENS, et il faut le dire.
    Les naissances de l'année gonflent l'effectif actuel sans être comptées
    au départ, ce qui fait paraître le taux de perte plus BAS qu'il n'est ;
    les ventes et les abattages de l'année réduisent l'effectif actuel sans
    être des pertes, ce qui le fait paraître plus HAUT. L'enquête ne demande
    ni les unes ni les autres, et aucune correction n'est inventée ici.

    LE TAUX D'UN GROUPE EST UN RAPPORT DE TOTAUX, PAS UNE MOYENNE DE TAUX. Un
    ménage qui perd une chèvre sur deux perd 50 % de son troupeau ; moyenner
    ce chiffre avec les 2,5 % d'un éleveur de quarante bovins donnerait 26 %,
    qui ne décrit le capital perdu de personne. Le poids rendu par cette
    fonction est donc le troupeau moyen du ménage, en unités animales, et
    c'est lui qui pondère.
    """
    num = np.zeros(len(df))
    den = np.zeros(len(df))
    vu = np.zeros(len(df), dtype=bool)
    for esp, (r_eff, r_mort, motif) in CHEPTEL.items():
        c_e = _col_rang(df, r_eff, motif)
        c_m = _col_rang(df, r_mort, "mortalite dans votre elevage")
        if not (c_e and c_m):
            continue
        eff = pd.to_numeric(df[c_e], errors="coerce")
        mor = pd.to_numeric(df[c_m], errors="coerce")
        ok = (eff.notna() & mor.notna() & (eff >= 0) & (mor >= 0)).to_numpy()
        e = eff.fillna(0).to_numpy(dtype=float)
        m = mor.fillna(0).to_numpy(dtype=float)
        u = UA[esp]
        num += np.where(ok, m * u, 0.0)
        den += np.where(ok, (e + m / 2.0) * u, 0.0)
        vu |= ok
    base = vu & (den > 0)
    val = np.zeros(len(df))
    np.divide(100.0 * num, den, out=val, where=den > 0)
    return base, np.clip(val, 0.0, 100.0), den


def _perte_cheptel_sans_volaille(df):
    """Le même taux, volaille exclue — la mesure de contrôle du coefficient."""
    garde = {k: v for k, v in CHEPTEL.items() if k != "volailles"}
    sauve = dict(CHEPTEL)
    try:
        CHEPTEL.clear()
        CHEPTEL.update(garde)
        return _perte_cheptel(df)
    finally:
        CHEPTEL.clear()
        CHEPTEL.update(sauve)


def _pertes_agricoles(df):
    """Ligne 84 : part de la production agricole perdue, pondérée par la
    production.

    LES DEUX BLOCS SE RÉPONDENT CULTURE PAR CULTURE. Quarante colonnes de
    rendement, quarante colonnes de perte, dans le même ordre : le maïs d'un
    ménage a donc son rendement et sa perte, et l'un pondère l'autre. C'est
    ce qui manquait pour que la ligne soit calculable — une moyenne simple
    des pourcentages mettrait la tomate d'un carré de jardin au même rang que
    le maïs de toute la parcelle.

    LES DEUX SONT DONNÉS EN CLASSES, ET C'EST LA LIMITE. Le rendement est
    une tranche en kilos, prise ici à son milieu ; les deux tranches ouvertes,
    « moins de 50 » et « plus de 1000 », sont prises près de leur borne. La
    perte est une tranche en pour cent, également prise à son milieu pour
    « moins de 10 » et « plus de 90 ». Le chiffre obtenu est donc juste au
    rang près, pas au point de pourcentage près.

    LE RENDEMENT DÉCLARÉ EST CE QUI A ÉTÉ RÉCOLTÉ, PAS CE QUI AURAIT PU
    L'ÊTRE. Pondérer par lui donne donc un peu moins de poids aux cultures
    les plus abîmées, celles dont il reste justement peu : le taux publié est
    à ce titre un MINORANT modéré.
    """
    y0, y1 = RENDEMENTS
    p0, p1 = PERTES
    if p1 > len(df.columns):
        return None
    cy = list(df.columns[y0:y1])
    cp = list(df.columns[p0:p1])
    if len(cy) != len(cp):
        return None
    # La concordance des deux blocs, nom à nom : sans elle, la perte d'une
    # culture pondérerait le rendement d'une autre.
    for a, b in zip(cy, cp):
        na, nb = _nom_culture(a), _nom_culture(b)
        if na != nb and {na, nb} != {"Babane", "Banane"}:
            return None

    def _kg(s):
        t = s.astype(str).str.strip()
        v = t.map(CLASSES_KG)
        return v.where(v.notna(), pd.to_numeric(t, errors="coerce"))

    def _pct(s):
        t = s.astype(str).str.strip()
        v = t.map(CLASSES_PERTE)
        return v.where(v.notna(), pd.to_numeric(t, errors="coerce"))

    num = np.zeros(len(df))
    den = np.zeros(len(df))
    for a, b in zip(cy, cp):
        kg = _kg(df[a]).to_numpy(dtype=float)
        pc = _pct(df[b]).to_numpy(dtype=float)
        ok = np.isfinite(kg) & np.isfinite(pc) & (kg > 0)
        num += np.where(ok, np.clip(pc, 0, 100) * kg, 0.0)
        den += np.where(ok, kg, 0.0)
    base = den > 0
    val = np.zeros(len(df))
    np.divide(num, den, out=val, where=base)
    return base, np.clip(val, 0.0, 100.0), den


def _especes(df):
    """Le tableau des espèces pêchées : (noms de colonne, noms d'espèce)."""
    e0, e1 = ESPECES
    if e1 > len(df.columns):
        return None
    cols = list(df.columns[e0:e1])
    return cols, [_nom_culture(c) for c in cols]


def _biodiversite_pechee(df):
    """Ligne 86 : nombre d'espèces distinctes pêchées par le ménage.

    ON COMPTE DES NOMS, PAS DES COLONNES. Le questionnaire porte deux fois
    « Bonite » — deux appellations locales que l'export a fondues en une
    seule sous deux numéros — et compter les colonnes donnerait une espèce de
    trop à qui coche les deux. La colonne « Autre » compte pour UNE espèce :
    elle en cache peut-être plusieurs, ce qui fait du compte un MINORANT.

    LA BASE, CE SONT LES PÊCHEURS QUI ONT RÉPONDU. Soixante-quinze ménages
    sur les soixante-dix-huit qui se déclarent pêcheurs ont situé au moins une
    espèce ; les trois autres n'ont pas rempli le tableau. Un non-pêcheur n'a
    pas zéro espèce, il n'a pas la question — le compter à zéro écraserait la
    note d'une section agricole pour une raison qui n'a rien de halieutique.
    """
    t = _especes(df)
    if not t:
        return None
    cols, noms = t
    vus = [set() for _ in range(len(df))]
    for c, nom in zip(cols, noms):
        rempli = df[c].notna().to_numpy()
        for i in np.flatnonzero(rempli):
            vus[i].add(nom)
    val = np.array([float(len(s)) for s in vus])
    base = val > 0
    return base, val


def _pecheurs_plateau(df):
    """Ligne 87 : pêcheurs opérant exclusivement sur le plateau.

    LA RÉPONSE EST DÉJÀ DANS LA CELLULE. Le tableau des espèces ne demande pas
    combien on en prend mais OÙ : chaque cellule remplie vaut « Plateau » ou
    « Grand fond ». Un pêcheur est exclusif du plateau si aucune de ses
    espèces ne vient du grand fond. Rien à déduire, rien à modéliser.

    LE BARÈME NOTE À L'ENVERS, ET C'EST VOULU. Une flotte confinée au plateau
    est une flotte qui appuie toute sa pression sur le récif, faute de moyen
    d'aller plus loin : le référentiel donne donc 0 à une côte dont 95 % des
    pêcheurs ne sortent pas du plateau, et 10 à celle dont ils en sortent.
    """
    t = _especes(df)
    if not t:
        return None
    cols, _ = t
    plateau = np.zeros(len(df), dtype=int)
    grand = np.zeros(len(df), dtype=int)
    for c in cols:
        v = df[c].astype(str).str.strip()
        plateau += (v == "Plateau").to_numpy().astype(int)
        grand += (v == "Grand fond").to_numpy().astype(int)
    base = (plateau + grand) > 0
    cible = base & (grand == 0)
    return base, cible


def _oui(df, rang, motif):
    c = _col_rang(df, rang, motif)
    if c is None:
        return None
    return (df[c].astype(str).str.strip() == "Oui").to_numpy()


def _coche(df, rang, motif):
    c = _col_rang(df, rang, motif)
    if c is None:
        return None
    return (pd.to_numeric(df[c], errors="coerce") == 1).to_numpy()


def _frequente(df, rang, motif):
    """Un groupe fréquenté : n'importe quelle réponse sauf « Jamais »."""
    c = _col_rang(df, rang, motif)
    if c is None:
        return None
    v = df[c].astype(str).str.strip()
    return (df[c].notna() & (v != "Jamais")).to_numpy()


def _repondu(df, rang, motif):
    c = _col_rang(df, rang, motif)
    return None if c is None else df[c].notna().to_numpy()


def _conflits_resolus(df):
    """Ligne 97 : conflits portés devant un mode de règlement pacifique.

    LE DÉNOMINATEUR EXISTE, ET C'EST CE QUI DÉBLOQUE LA LIGNE. On lisait
    auparavant que le taux vaudrait 100 % par construction, faute de modalité
    codant un conflit non résolu. C'est vrai du seul tableau des modes de
    règlement — mais le dénominateur n'est pas ce tableau, c'est la question
    d'avant : « avez-vous été impliqué dans un conflit ». Soixante et onze
    ménages disent oui ; soixante-quatre ont renseigné un mode, sept aucun.
    Le taux se calcule donc, et il ne vaut pas 100 %.

    TOUTES LES MODALITÉS RELEVÉES SONT PACIFIQUES, ET LE RÉFÉRENTIEL LES
    NOMME. Sa métrique dit « dialogue, médiation ou intervention d'autorités
    reconnues » : la médiation d'un proche est le dialogue, le tribunal, la
    police, le CASEC et le responsable religieux sont des autorités
    reconnues, l'ONG un tiers reconnu. Aucune modalité ne code une réponse
    violente — c'est une limite du questionnaire, pas une propriété du
    territoire.

    CE QUE LE CHIFFRE EST VRAIMENT : UN MAJORANT. La question demande
    « comment avez-vous cherché OU CHERCHEZ-VOUS à résoudre ce conflit » :
    une cellule remplie dit qu'une voie a été empruntée, pas que le conflit
    est réglé. Et les sept sans mode peuvent être des conflits sans issue
    comme des non-réponses ; les compter au dénominateur est le choix
    prudent, l'inverse ramènerait mécaniquement le taux à 100 %.

    LA BASE EST PETITE : soixante et onze conflits pour tout le territoire,
    de deux à quinze par section. La plateforme pâlit d'elle-même ce qui
    repose sur moins de vingt répondants.
    """
    c_conf = _col_rang(df, 407, "implique(e) dans un conflit")
    if c_conf is None:
        return None
    base = (df[c_conf].astype(str).str.strip() == "Oui").to_numpy()
    d0, d1 = MODES_CONFLIT
    if d1 > len(df.columns):
        return None
    mode = df[df.columns[d0:d1]].notna().any(axis=1).to_numpy()
    return base, base & mode


def _isolement(df):
    """Ligne 98 : personnes n'ayant pris part à aucune activité collective.

    LE CROISEMENT INDIVIDUEL EST EXACTEMENT CE QUE FAIT CETTE PLATEFORME. On
    lisait auparavant que l'isolement, défini par la conjonction de dix
    questions, ne pouvait pas être reproduit ; c'est pourtant l'opération que
    le moteur fait à chaque requête. Treize canaux sont donc lus ensemble, et
    ils recouvrent un à un ce que la métrique énumère : le travail
    communautaire, les associations, les groupes religieux, les groupes
    d'épargne et les réseaux sociaux informels.

    UNE ABSENCE DE RÉPONSE N'EST PAS UN ISOLEMENT. Un ménage qui n'a répondu
    qu'à trois canaux sur treize serait déclaré isolé par un simple « aucun
    oui ». La base exige donc au moins huit canaux renseignés ; six ménages
    sur mille deux cent onze en manquent.

    LES FENÊTRES DE TEMPS NE SONT PAS TOUTES CELLE DU RÉFÉRENTIEL, et les
    écarts se compensent en partie. La corvée agricole est bien sur douze
    mois ; le nettoyage d'espace public demande « avez-vous DÉJÀ pris part »,
    donc une fenêtre plus large, ce qui compte comme participant quelqu'un
    qui ne l'a pas fait cette année et ABAISSE le taux d'isolement ; l'aide
    reçue et rendue portent sur six mois, fenêtre plus courte, ce qui le
    RELÈVE. Les adhésions — comité, OCB, mutuelle — sont lues au présent.
    """
    part = np.zeros(len(df), dtype=bool)
    nrep = np.zeros(len(df), dtype=int)
    for rang, motif, genre in CANAUX:
        f = {"oui": _oui, "coche": _coche, "freq": _frequente}[genre]
        v = f(df, rang, motif)
        r = _repondu(df, rang, motif)
        if v is None or r is None:
            continue
        part |= (v & r)
        nrep += r.astype(int)
    # Les trois canaux d'entraide sont des cases à cocher d'une même
    # question : on les prend en bloc, un « oui » à l'une suffit.
    for rangs, motif in ((AIDE_RECUE, "aide/service de la part"),
                         (AIDE_RENDUE, "rendu un service/aide")):
        r = _repondu(df, rangs[0], motif)
        if r is None:
            continue
        v = np.zeros(len(df), dtype=bool)
        for g in rangs:
            c = _coche(df, g, motif)
            if c is not None:
                v |= c
        part |= (v & r)
        nrep += r.astype(int)
    base = nrep >= CANAUX_MIN
    return base, base & ~part


def _autonomie_femmes(df):
    """Ligne 92 : indice d'autonomie des femmes, sur les volets disponibles.

    QUATRE VOLETS SUR SEPT, ET C'EST POURQUOI LA LIGNE RESTE SANS NOTE. Le
    référentiel compose l'indice de sept proxys binaires ; l'enquête en porte
    quatre — la génération de revenu, la capacité d'emprunter de petits
    montants, les interactions sociales, la participation à des groupes
    communautaires. Trois manquent : l'autonomie sur les dépenses courantes,
    la liberté de mouvement, et l'absence de crainte à exprimer un
    désaccord. Un indice sur quatre volets ne se pose pas sur un barème qui
    en attend sept : il plafonnerait à quatre, et toutes les sections
    seraient notées basses pour une raison qui tient au questionnaire et non
    au territoire. La valeur est donc publiée, la note ne l'est pas.

    LA MESURE RESTE UTILE TELLE QUELLE : elle compare les sections entre
    elles sur les mêmes quatre volets, ce que le barème ne fait pas mieux.

    UN CINQUIÈME VOLET EST DISPONIBLE ET N'EST PAS RETENU ICI : les biens
    détenus en son propre nom. C'est un proxy d'autonomie classique, mais le
    référentiel ne le nomme pas parmi les sept, et compléter la liste de
    quelqu'un d'autre n'est pas notre travail. Le chiffre est calculé à côté
    pour que le choix puisse être fait en connaissance de cause.
    """
    c_sexe = _col_rang(df, 11, "sexe du repondant")
    if c_sexe is None:
        return None
    femme = (df[c_sexe].astype(str).str.strip() == "Femme").to_numpy()

    def _un(rangs, genre="oui"):
        f = {"oui": _oui, "coche": _coche, "freq": _frequente}[genre]
        v = np.zeros(len(df), dtype=bool)
        for rang, motif in rangs:
            x = f(df, rang, motif)
            if x is not None:
                v |= x
        return v

    # 1. Génération de revenu : salariée, journalière ou à son compte.
    v1 = _un([(480, "contrat de longue duree"), (481, "contrat de courte"),
              (482, "journalier sans contrat"), (483, "auto-entrepreneur")])
    r1 = _repondu(df, 483, "auto-entrepreneur")
    # 2. Emprunter de petits montants : mutuelle d'épargne ou compte propre.
    v2 = (_un([(398, "mutuelle d'epargne")])
          | _un([(487, "banque commerciale"), (488, "caisse populaire"),
                 (489, "muso"), (490, "compte dans une institution")],
                "coche"))
    r2 = _repondu(df, 398, "mutuelle d'epargne")
    # 3. Interactions sociales : un confident, ou un groupe d'amis.
    c433 = _repondu(df, 433, "soucis avec quelqu'un de confiance")
    non_conf = _coche(df, 438, "soucis avec quelqu'un de confiance")
    v3 = ((c433 & ~non_conf) if (c433 is not None and non_conf is not None)
          else np.zeros(len(df), dtype=bool))
    v3 = v3 | _un([(396, "groupe d'amis")], "freq")
    r3 = c433
    # 4. Participation à des groupes communautaires.
    v4 = (_un([(377, "organisation communautaire de base"),
               (376, "comite de gestion communautaire")])
          | _un([(393, "groupe de l'eglise"),
                 (394, "association de quartier"),
                 (395, "ocb/association"),
                 (397, "groupe politique")], "freq"))
    r4 = _repondu(df, 377, "organisation communautaire de base")

    if any(x is None for x in (r1, r2, r3, r4)):
        return None
    base = femme & r1 & r2 & r3 & r4
    val = ((v1 & r1).astype(float) + (v2 & r2).astype(float)
           + (v3 & r3).astype(float) + (v4 & r4).astype(float))
    return base, val


def _filles_scolarisees(df):
    """Ligne 94 : femmes de quinze à vingt-quatre ans encore à l'école.

    DEUX ÉCARTS AVEC LA DÉFINITION DU RÉFÉRENTIEL, ET ILS TIRENT EN SENS
    CONTRAIRE — c'est pourquoi la ligne est mesurée et non notée.

    LA POPULATION N'EST PAS LA BONNE. Le référentiel veut les filles de
    quinze ans et plus du ménage ; l'enquête ne décrit les enfants ni par
    sexe ni par âge — deux colonnes seulement, scolarisés et non scolarisés.
    La seule personne dont on connaisse à la fois le sexe, l'âge et la
    scolarité est LA RÉPONDANTE. On mesure donc les répondantes, pas les
    filles du ménage, et une répondante de vingt ans n'est pas tirée au sort
    parmi les jeunes femmes de sa section : elle a été retenue parce qu'elle
    représentait son foyer, ce qui n'est pas la même chose.

    LA BORNE HAUTE EST POSÉE ICI, PAS DANS LE RÉFÉRENTIEL, qui écrit
    « quinze ans et plus ». Prise à la lettre, cette borne met au
    dénominateur des femmes de soixante ans dont personne n'attend qu'elles
    soient scolarisées, et le taux tombe à 10,6 % — un chiffre qui ne dit
    rien de la scolarisation des filles. Vingt-quatre ans est la borne
    ordinaire de l'enseignement secondaire et supérieur ; elle est écrite ici
    et non cachée.

    LE NUMÉRATEUR EST PLUS LARGE QUE LE BARÈME : « encore à l'école », sans
    distinguer le niveau, alors que le référentiel demande le secondaire ou
    le supérieur. Le redoublement étant massif, une partie de ces jeunes
    femmes est encore au fondamental, et le chiffre est donc un MAJORANT sur
    ce point pendant qu'il est un minorant sur l'âge.

    CE QUI RENDRAIT LA LIGNE EXACTE : un tableau des membres du ménage avec
    sexe, âge et niveau scolaire — un bloc de questions dans la prochaine
    vague, rien de plus.
    """
    c_sexe = _col_rang(df, 11, "sexe du repondant")
    c_age = _col_rang(df, 12, "ge du repondant")
    if c_sexe is None or c_age is None:
        return None
    femme = (df[c_sexe].astype(str).str.strip() == "Femme").to_numpy()
    age = pd.to_numeric(df[c_age], errors="coerce")
    dans = age.between(*AGE_FILLES).to_numpy()
    ecole = _coche(df, 428, "je suis encore a l'ecole")
    rep = _repondu(df, 428, "je suis encore a l'ecole")
    if ecole is None or rep is None:
        return None
    base = femme & dans & rep
    # EN POUR CENT, PAS EN FRACTION. Le barème du référentiel est écrit en
    # pourcentage : rendre 0,344 là où il attend 34,4 le ferait tomber dans
    # la classe la plus basse et noter zéro une section où une jeune femme
    # sur trois est scolarisée.
    return base, (base & ecole).astype(float) * 100.0


# ligne du référentiel -> la règle qui la calcule
REGLES = {9: _surpeuplement, 87: _pecheurs_plateau,
          97: _conflits_resolus, 98: _isolement}

# LES RÈGLES QUI RENDENT UNE VALEUR PAR MÉNAGE, et non une appartenance. Le
# surpeuplement est un OUI ou un NON ; la diversité des cultures est un nombre
# entre zéro et un, et le score d'un groupe est la moyenne de ces nombres,
# notée ensuite par le barème. Les deux familles se ventilent pareil.
# LES RÈGLES À VALEUR. Deux d'entre elles n'entrent dans aucun score et c'est
# voulu : le barème de l'autonomie des femmes attend sept volets et l'enquête
# en porte quatre, celui de la scolarisation des filles attend une population
# que l'enquête ne décrit pas. Le moteur les écarte de lui-même — leurs
# barèmes ne se posent pas sur ce qu'on mesure — et leurs valeurs sont
# publiées telles quelles, sous une note qui dit ce qui manque.
REGLES_VALEUR = {53: _diversite_cultures, 86: _biodiversite_pechee,
                 92: _autonomie_femmes, 94: _filles_scolarisees}

# LES RÈGLES À POIDS : celles dont le chiffre d'un groupe est un RAPPORT DE
# TOTAUX et non une moyenne de rapports. Elles rendent trois vecteurs — base,
# valeur du ménage, poids du ménage — et le groupe vaut la somme des valeurs
# pondérées divisée par la somme des poids. Quand le poids vaut un partout,
# la formule redonne exactement la moyenne : c'est la même mécanique, avec un
# vecteur de plus.
#
# POURQUOI CETTE FAMILLE EXISTE. Le capital d'élevage perdu par un territoire
# est la somme des unités animales mortes divisée par la somme des troupeaux,
# pas la moyenne des taux de chaque cour. La perte agricole d'un ménage est
# de même la perte de sa récolte entière, donc la perte de chaque culture
# pondérée par ce que cette culture pèse dans sa récolte. Les deux lignes que
# le référentiel écrit avec le mot « total » demandent ce calcul-là.
REGLES_POIDS = {83: _perte_cheptel, 84: _pertes_agricoles}

# LES RÈGLES QUI SE MESURENT MAIS NE SE NOTENT PAS, et pourquoi chacune.
#
#   92, l'autonomie des femmes : le barème compose sept volets, l'enquête en
#       porte quatre. Un indice sur quatre plafonne à quatre et noterait
#       basses toutes les sections pour une raison qui tient au questionnaire.
#   94, la scolarisation des filles : le barème veut les filles du ménage,
#       l'enquête ne décrit les enfants ni par sexe ni par âge ; on mesure les
#       répondantes de quinze à vingt-quatre ans, qui ne sont pas la même
#       population.
#
# LE MOTEUR DOIT L'APPRENDRE ICI, ET NON LE DEVINER. Le barème de la ligne 94
# se lit parfaitement et s'appliquerait tout seul : rien dans le fichier de
# résultats ne dit qu'il ne CORRESPOND PAS à ce qu'on mesure. C'est la règle
# qui le sait, c'est donc la règle qui le déclare.
SANS_BAREME = {92, 94}

# LES HUIT INDICES COMPOSITES DE LA DIMENSION VII, décrits dans `indices_vii`.
# Ce ne sont pas des taux mais des COMPTES DE VOLETS, et c'est pour cela
# qu'ils vivent dans leur propre module : chacun tient dans un tableau de sept
# ou huit détecteurs, et ce tableau est l'objet à lire quand on veut savoir ce
# que l'indice mesure vraiment.
try:
    import indices_vii as _vii
except Exception:
    _vii = None


def _indice_vii(ligne):
    def f(df):
        d = _vii.construire(df)
        return d.get(ligne)
    return f


if _vii is not None:
    for _lg in _vii.VOLETS:
        REGLES_VALEUR[_lg] = _indice_vii(_lg)
    # Une ligne à qui il manque un volet ne se note pas : son indice plafonne
    # sous le maximum du barème. Le tableau le dit sans qu'il faille lire les
    # données.
    SANS_BAREME |= {lg for lg, i in _vii.inventaire().items()
                    if not i["complet"]}


def _verifier_indices(df):
    """Un volet peut manquer À L'EXÉCUTION et non seulement au tableau.

    Un détecteur rend `None` quand la colonne qu'il désigne n'est plus celle
    qu'il attendait — questionnaire modifié, colonne insérée. L'indice perd
    alors un volet en silence, et une ligne réputée complète se retrouverait
    notée sur un barème trop large. On revérifie donc sur les données du jour,
    et toute ligne qui n'atteint plus le maximum de son barème rejoint les
    lignes sans note.
    """
    if _vii is None:
        return
    mx = _vii.maximum_atteignable(df)
    for lg, i in _vii.inventaire().items():
        if mx.get(lg, 0) < i["attendus"]:
            SANS_BAREME.add(lg)

# CE QU'UNE RÈGLE DEVIENT DANS LES RÉSULTATS BRUTS : une question de plus,
# avec ses deux réponses. Elle n'a pas été posée sur le terrain, et le
# libellé le dit — « calculé » est dans son intitulé. Tout le reste de
# l'écran des résultats bruts fonctionne alors sans rien savoir d'elle : la
# ventilation par section, le graphique, le tableau, le téléchargement.
QUESTIONS = {
    9: {
        "categorie": "Logement (calculé)",
        "categorie_en": "Housing (computed)",
        "question": "Logement surpeuplé : plus de trois personnes par pièce",
        "question_en": "Overcrowded dwelling: more than three people per "
                       "room",
        "modalites": ["Oui", "Non"],
    },
    97: {
        "categorie": "Conflits (calculé)",
        "categorie_en": "Conflicts (computed)",
        "question": "Conflit porté devant un mode de règlement pacifique "
                    "(dialogue, médiation, autorité reconnue)",
        "question_en": "Conflict taken to a peaceful settlement route "
                       "(dialogue, mediation, recognised authority)",
        "modalites": ["Oui", "Non"],
    },
    98: {
        "categorie": "Vie collective (calculé)",
        "categorie_en": "Collective life (computed)",
        "question": "Isolé : aucune participation à une activité ou un "
                    "groupe collectif",
        "question_en": "Isolated: no participation in any collective "
                       "activity or group",
        "modalites": ["Oui", "Non"],
    },
    87: {
        "categorie": "Pêche (calculé)",
        "categorie_en": "Fishing (computed)",
        "question": "Pêcheur exclusif du plateau : aucune espèce déclarée "
                    "au grand fond",
        "question_en": "Shelf-only fisher: no species reported from deep "
                       "water",
        "modalites": ["Oui", "Non"],
    },
}


def charger(groupes=None, n=None):
    """Les règles calculées, prêtes à être posées à côté des autres
    indicateurs : {ligne: (base, cible)}.

    `groupes` sert à la vérification d'ordre : si les sections vues dans le
    CSV ne sont pas celles du moteur, ligne à ligne, on ne rend rien.
    """
    df = _lire()
    if df is None:
        return {}
    if n is not None and len(df) != n:
        return {}
    if groupes and COL_SECTION in df.columns:
        vu = df[COL_SECTION].map(lambda x: NORM.get(x, x)).to_numpy()
        for nom, m in groupes.items():
            if nom in ("Homme", "Femme"):
                continue
            if m is None or not m.any() or nom not in set(vu):
                continue
            if not (vu[m] == nom).all():
                return {}
    out = {}
    for ligne, f in REGLES.items():
        r = f(df)
        if r and r[0].any():
            out[ligne] = r
    return out


def charger_valeurs(groupes=None, n=None):
    """Les règles à valeur : {ligne: (base, valeur par ménage)}.

    LES RÈGLES À POIDS ENTRENT PAR LA MÊME PORTE, avec un troisième vecteur.
    Le moteur reconnaît la famille au nombre d'éléments rendus : deux, c'est
    une moyenne ; trois, c'est un rapport de totaux.
    """
    df = _lire()
    if df is None or (n is not None and len(df) != n):
        return {}
    # LA VÉRIFICATION PASSE AVANT LE CHARGEMENT, et il le faut : le moteur lit
    # `SANS_BAREME` après cet appel, et c'est là que se décide si un indice
    # composite amputé peut être noté.
    _verifier_indices(df)
    out = {}
    for ligne, f in list(REGLES_VALEUR.items()) + list(REGLES_POIDS.items()):
        r = f(df)
        if r and r[0].any():
            out[ligne] = r
    return out


def _valeur_groupe(r, m):
    """Le chiffre d'un sous-groupe pour une règle à valeur ou à poids."""
    base = r[0] & m
    if not base.sum():
        return None
    val = np.asarray(r[1], dtype=float)
    if len(r) > 2:
        p = np.asarray(r[2], dtype=float)[base]
        v = val[base]
        return (float(np.dot(v, p) / p.sum()) if p.sum() > 0 else None)
    return float(val[base].mean())


def valeurs_par_groupe(groupes):
    """La valeur publiée de chaque règle, pour chaque découpage du fichier de
    résultats : {ligne: {groupe: valeur}}.

    ELLES SONT ÉCRITES DANS `resultats.json` PAR LA MÊME RÈGLE QUI SERT AU
    MOTEUR. C'est la seule façon d'éviter que la page de dimension et l'écran
    des scores affichent deux chiffres différents pour le même indicateur et
    le même groupe.
    """
    df = _lire()
    if df is None:
        return {}
    out = {}
    tout = np.ones(len(df), dtype=bool)
    for ligne, f in list(REGLES_VALEUR.items()) + list(REGLES_POIDS.items()):
        r = f(df)
        if not r:
            continue
        vals = {}
        for nom, m in groupes.items():
            v = _valeur_groupe(r, m)
            if v is not None:
                vals[nom] = round(v, 4)
        v = _valeur_groupe(r, tout)
        if v is not None:
            vals["Total"] = round(v, 4)
        out[ligne] = vals
    for ligne, f in REGLES.items():
        r = f(df)
        if not r:
            continue
        base, cible = r
        vals = {}
        for nom, m in groupes.items():
            b = base & m
            if b.sum():
                vals[nom] = round(100.0 * float((cible & m).sum())
                                  / float(b.sum()), 2)
        vals["Total"] = round(100.0 * float(cible.sum())
                              / float(base.sum()), 2)
        out[ligne] = vals
    return out
