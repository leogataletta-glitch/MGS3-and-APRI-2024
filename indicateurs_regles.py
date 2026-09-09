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
}

PIECES_MAX = 15
SEUIL_PERS_PIECE = 3.0


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


# ligne du référentiel -> (fonction, sens du barème lu sur les bornes)
REGLES = {9: _surpeuplement}


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
