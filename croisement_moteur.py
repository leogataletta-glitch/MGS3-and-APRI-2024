"""Le moteur du croisement des résultats — calcul seul, aucun affichage.

CE QU'IL PERMET

Poser une requête quelconque sur les réponses individuelles — « sans latrine
ET sans eau améliorée ET sans électricité ET femme ET montagne » — et obtenir
l'effectif, la part de l'échantillon, la répartition par section communale, et
le profil de résilience du sous-groupe ainsi défini.

COMMENT, ET POURQUOI C'EST POSSIBLE

`croisement.npz` porte, pour chacune des 2 702 modalités de réponse des 483
questions, l'appartenance des 1 211 répondants, en bits. Une intersection est
donc un ET binaire sur un vecteur de 1 211 booléens : quelques microsecondes.
Des effectifs agrégés ne permettraient rien de tel — on ne déduit pas d'un
« 40 % sans latrine » et d'un « 30 % sans eau » combien de foyers cumulent les
deux, puisque cela dépend entièrement de leur recouvrement.

Le catalogue est lu du fichier : AUCUNE QUESTION N'EST CODÉE ICI. Ajoutez une
question à l'enquête, régénérez l'index, elle apparaît dans l'outil.

=========================================================================
LE SCORE DE RÉSILIENCE D'UN SOUS-GROUPE — CE QUI EST FAIT, ET CE QUI NE
PEUT PAS L'ÊTRE
=========================================================================

Il n'existe PAS de score de résilience par répondant. Les scores APRI sont
calculés indicateur par indicateur, sur une population : « 31,9 % des ménages
ont un assainissement amélioré » devient un 2 sur 10 par le barème publié. Pour
noter un sous-groupe, il faut donc recalculer la valeur de chaque indicateur
SUR CE SOUS-GROUPE, puis lui appliquer le même barème.

C'est faisable, mais seulement là où la définition de l'indicateur est
reproductible à partir des réponses individuelles. J'ai donc procédé par
VÉRIFICATION plutôt que par confiance : pour chaque indicateur d'enquête, la
valeur est recalculée sur l'échantillon ENTIER et comparée à la valeur publiée.

  · si elle tombe à moins d'un point ET que le barème rend le score publié,
    l'indicateur est RETENU : sa définition est reproduite, on peut donc la
    porter sur n'importe quel sous-ensemble ;
  · sinon il est ÉCARTÉ. Les écarts viennent de bases restreintes — un
    indicateur calculé sur les seuls agriculteurs, ou sur les seuls ménages
    ayant des enfants — ou de ratios qui ne sont pas des parts de ménages.
    Deviner ces bases produirait des chiffres faux que rien ne signalerait.

Il reste 25 indicateurs, 57,4 points de pondération sur 155,4 — 37 % du
référentiel, et cinq dimensions sur six. La couverture est très inégale : 85 %
du poids de la dimension physique, 44 % de l'institutionnelle, et RIEN de
l'environnementale — couvert forestier, pluie et température sont mesurés par
satellite et ne varient pas selon le répondant. Ces chiffres ne sont pas figés
ici : `couverture()` les recalcule sur les données du jour.

CE QUE CET INDICE EST, ET N'EST PAS. C'est un INDICE PARTIEL. Il se compare
d'un groupe à l'autre — les deux côtés sont calculés sur les mêmes
indicateurs — et il ne se compare PAS au score APRI publié, qui en compte 66.
`couverture()` rend la part exacte, et l'interface l'écrit à côté du chiffre.
"""

import json
import os
import re
import unicodedata

import numpy as np

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

SECTIONS = ["Anse à Drick", "Barbois", "Dumont", "Débouchette", "Mouline",
            "Quentin", "Beaulieu", "Blactote", "Dalmette", "Trichet"]

DIMENSIONS = [
    ("dim1", "I. PHYSICAL AND INFRASTRUCTURAL DIMENSION"),
    ("dim2", "II. INSTITUTIONAL, TECHNOLOGICAL, AND GOVERNANCE  DIMENSION"),
    ("dim3", "III.  ENVIRONMENTAL AND ECOLOGICAL DIMENSION"),
    ("dim4", "IV. ECONOMIC, LIVELIHOODS, AND FOOD SECURITY DIMENSION"),
    ("dim5", "V. SOCIAL AND COMMUNITY DIMENSION"),
    ("dim6", "VI. HUMAN DIMENSION"),
]
DIM_DE = {long: court for court, long in DIMENSIONS}

# Les registres de segmentation, tels qu'ils existent dans l'index. Ils ne sont
# pas inventés ici : ce sont les groupes déjà portés par le fichier, et si un
# groupe y était ajouté demain il apparaîtrait de lui-même.
REGISTRES = [
    ("sexe", ["Homme", "Femme"]),
    ("age", ["<25", "25-39", "40-59", "60+"]),
    ("richesse", ["Cat A", "Cat B", "Cat C"]),
    ("paysage", ["Littoral", "Montagne"]),
    ("section", SECTIONS),
]

# Sous ce seuil, un pourcentage calculé sur le sous-groupe n'a plus de sens
# statistique utile. On ne bloque pas, on le dit.
N_FRAGILE = 30

_NUM = r"(-?\d+(?:[.,]\d+)?)"


def _norm(s):
    """Comparaison de libellés insensible aux accents, à la casse et à la
    ponctuation : les mêmes chaînes ne sont pas écrites à l'identique dans le
    fichier de résultats et dans l'index des questions."""
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore")
    s = s.decode()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s.lower())).strip()


def _trouver(nom):
    for c in (os.path.join(DATA, nom), os.path.join(APP_DIR, nom)):
        if os.path.exists(c):
            return c
    return None


def _parse_echelle(txt):
    """Le barème publié, « 0(≤18,9%), 1(18,9–31,9%), … », en [(score, borne)].

    On garde la BORNE HAUTE de chaque classe : c'est elle qui décide du
    passage au score suivant. Le dernier couple sert de valeur par défaut.
    """
    out = []
    for m in re.finditer(r"(\d+)\s*\(\s*([^)]*)\)", (txt or "").split(":", 1)[-1]):
        nums = [float(x.replace(",", ".")) for x in re.findall(_NUM, m.group(2))]
        if nums:
            out.append((int(m.group(1)), nums[-1]))
    return out or None


def _score_de(val, bornes, decroissant):
    """Le score d'une valeur, selon le barème et son sens.

    Un barème dont les bornes descendent est un barème inversé — une valeur
    haute y vaut un score bas. Le sens est LU sur les bornes plutôt que sur un
    champ déclaratif : c'est la donnée elle-même qui décide.
    """
    if val is None or not bornes:
        return None
    if not decroissant:
        for sc, hi in bornes[:-1]:
            if val <= hi:
                return sc
        return bornes[-1][0]
    for sc, hi in bornes[:-1]:
        if val >= hi:
            return sc
    return bornes[-1][0]


def charger():
    """Le catalogue complet, prêt à l'emploi. À mettre en cache par la page."""
    ci, cn, rs = (_trouver("croisement_index.json"), _trouver("croisement.npz"),
                  _trouver("resultats.json"))
    if not ci or not cn:
        return None
    with open(ci, encoding="utf-8") as f:
        index = json.load(f)
    z = np.load(cn)
    n = int(z["n"][0])
    bits = np.unpackbits(z["bits"], axis=1)[:, :n].astype(bool)
    grp = np.unpackbits(z["groupes"], axis=1)[:, :n].astype(bool)
    groupes = {nom: grp[k] for k, nom in enumerate(index["groupes"])}

    res = []
    if rs:
        with open(rs, encoding="utf-8") as f:
            res = json.load(f)
        res = res["indicateurs"] if isinstance(res, dict) \
            and "indicateurs" in res else res

    qmap = {_norm(q["question"]): q for q in index["questions"]}
    indicateurs, ecartes = [], []
    scores = [r for r in res
              if (r.get("scores_corriges") or {}).get("Total") is not None]
    poids_total = sum((r.get("ponderation") or 1) for r in scores)

    for r in res:
        if (r.get("scores_corriges") or {}).get("Total") is None:
            continue
        if (r.get("source") or "menage") != "menage":
            ecartes.append((r, "source"))
            continue
        mods = [m.strip() for m in (r.get("modalites") or "").split(" + ")
                if m.strip()]
        q = qmap.get(_norm(r.get("question")))
        if not mods or not q:
            ecartes.append((r, "definition"))
            continue
        labs = {_norm(m): i for i, m in enumerate(q["modalites"])}
        if any(_norm(m) not in labs for m in mods):
            ecartes.append((r, "definition"))
            continue

        # La BASE d'un indicateur est l'ensemble des répondants qui ont
        # répondu à la question, et non l'échantillon entier : c'est ainsi que
        # les valeurs publiées sont calculées, et sans cela un tiers des
        # indicateurs tombait à côté.
        base = np.zeros(n, dtype=bool)
        for j in range(len(q["modalites"])):
            base |= bits[q["debut"] + j]
        cible = np.zeros(n, dtype=bool)
        for m in mods:
            cible |= bits[q["debut"] + labs[_norm(m)]]

        bornes = _parse_echelle(r.get("echelle"))
        pub = (r.get("valeurs") or {}).get("Total")
        if not bornes or pub is None or not base.any():
            ecartes.append((r, "bareme"))
            continue
        decroissant = len(bornes) > 1 and bornes[0][1] > bornes[1][1]
        val = 100.0 * cible.sum() / base.sum()

        # LA VÉRIFICATION. Reproduire la valeur publiée à moins d'un point ET
        # retomber sur le score publié : sans cela, la définition n'est pas
        # celle du référentiel, et la porter sur un sous-groupe donnerait un
        # chiffre faux que rien ne signalerait.
        if abs(val - float(pub)) > 1.0:
            ecartes.append((r, "base"))
            continue
        if _score_de(val, bornes, decroissant) != \
                (r.get("scores_corriges") or {}).get("Total"):
            ecartes.append((r, "bareme"))
            continue

        indicateurs.append({
            "ligne": r["ligne"], "dim": DIM_DE.get(r["dimension"], ""),
            "nom": r.get("indicateur"), "nom_fr": r.get("indicateur_fr"),
            "poids": r.get("ponderation") or 1, "bornes": bornes,
            "decroissant": decroissant, "base": base, "cible": cible,
            "valeur_pub": float(pub),
            "score_pub": (r.get("scores_corriges") or {}).get("Total"),
        })

    return {
        "n": n, "bits": bits, "questions": index["questions"],
        "groupes": groupes, "indicateurs": indicateurs,
        "poids_total": poids_total, "n_scores": len(scores),
        "poids_couvert": sum(i["poids"] for i in indicateurs),
        "ecartes": [(r["ligne"], m) for r, m in ecartes],
    }


def couverture(cat):
    """Part du référentiel que le sous-groupe peut réellement faire bouger,
    globalement et par dimension. C'est le chiffre à écrire à côté du score."""
    par_dim = {}
    for cle, _long in DIMENSIONS:
        p = sum(i["poids"] for i in cat["indicateurs"] if i["dim"] == cle)
        par_dim[cle] = p
    return {"global": (cat["poids_couvert"] / cat["poids_total"]
                       if cat["poids_total"] else 0.0),
            "poids": par_dim}


# --------------------------------------------------------------- la requête
def masque_question(cat, qi, modalites, negation=False):
    """Les répondants ayant coché au moins une des modalités listées.

    La négation porte sur les RÉPONDANTS À LA QUESTION, pas sur l'échantillon
    entier : « n'a pas de latrine améliorée » ne doit pas embarquer les foyers
    qui n'ont pas répondu à la question de l'assainissement, dont on ne sait
    rien. C'est la différence entre « a répondu autre chose » et « on ignore ».
    """
    q = next((x for x in cat["questions"] if x["i"] == qi), None)
    if not q:
        return np.zeros(cat["n"], dtype=bool)
    m = np.zeros(cat["n"], dtype=bool)
    for lab in modalites:
        if lab in q["modalites"]:
            m |= cat["bits"][q["debut"] + q["modalites"].index(lab)]
    if not negation:
        return m
    base = np.zeros(cat["n"], dtype=bool)
    for j in range(len(q["modalites"])):
        base |= cat["bits"][q["debut"] + j]
    return base & ~m


def evaluer(cat, clauses, liaison="ET"):
    """Le masque du groupe. `clauses` est une liste de dictionnaires :

        {"type": "question", "qi": 12, "modalites": [...], "non": False}
        {"type": "groupe",   "valeurs": ["Femme"]}          # OU interne

    Une clause de segmentation à plusieurs valeurs est un OU — « Femme ou
    Homme » n'a pas de sens en ET, personne n'est les deux.
    """
    masques = []
    for c in clauses:
        if c.get("type") == "groupe":
            vals = [v for v in c.get("valeurs", []) if v in cat["groupes"]]
            if not vals:
                continue
            m = np.zeros(cat["n"], dtype=bool)
            for v in vals:
                m |= cat["groupes"][v]
            if c.get("non"):
                m = ~m
            masques.append(m)
        else:
            if not c.get("modalites"):
                continue
            masques.append(masque_question(cat, c["qi"], c["modalites"],
                                           c.get("non", False)))
    if not masques:
        return np.ones(cat["n"], dtype=bool), 0
    total = masques[0].copy()
    for m in masques[1:]:
        total = (total & m) if liaison == "ET" else (total | m)
    return total, len(masques)


# ------------------------------------------------------- profil de résilience
def profil(cat, masque):
    """Valeur, score et poids de chaque indicateur retenu, sur ce masque.

    Un indicateur dont la base est vide dans le sous-groupe — personne n'a
    répondu à cette question parmi les retenus — est rendu à None plutôt que
    forcé à zéro : une absence de mesure n'est pas une mesure nulle.
    """
    out = []
    for ind in cat["indicateurs"]:
        base = ind["base"] & masque
        nb = int(base.sum())
        if nb == 0:
            out.append({**{k: ind[k] for k in
                           ("ligne", "dim", "nom", "nom_fr", "poids")},
                        "n": 0, "valeur": None, "score": None})
            continue
        val = 100.0 * float((ind["cible"] & masque).sum()) / nb
        out.append({**{k: ind[k] for k in
                       ("ligne", "dim", "nom", "nom_fr", "poids")},
                    "n": nb, "valeur": val,
                    "score": _score_de(val, ind["bornes"], ind["decroissant"])})
    return out


def agreger(lignes):
    """Score par dimension et score d'ensemble — moyenne pondérée.

    Les indicateurs non mesurables sur le groupe sortent du dénominateur,
    jamais comptés comme des zéros. C'est la règle du reste de la plateforme,
    et elle doit le rester : deux moyennes calculées différemment sur le même
    site finiraient par ne plus concorder.
    """
    par_dim, num, den = {}, 0.0, 0.0
    for cle, _long in DIMENSIONS:
        n_, d_ = 0.0, 0.0
        for l in lignes:
            if l["dim"] != cle or l["score"] is None:
                continue
            n_ += l["poids"] * l["score"]
            d_ += l["poids"]
        par_dim[cle] = (n_ / d_) if d_ else None
        num += n_
        den += d_
    return {"dimensions": par_dim, "global": (num / den) if den else None,
            "poids": den}


def par_section(cat, masque):
    """La distribution territoriale du groupe.

    Trois lectures, et elles ne disent pas la même chose : combien de membres
    du groupe vivent dans la section, quelle part de la section le groupe
    représente — c'est celle-là qui dit où le phénomène est intense — et le
    score partiel du groupe dans cette section.
    """
    n_grp = int(masque.sum())
    out = []
    for s in SECTIONS:
        sec = cat["groupes"].get(s)
        if sec is None:
            continue
        m = masque & sec
        nb, n_sec = int(m.sum()), int(sec.sum())
        sc = agreger(profil(cat, m))["global"] if nb >= 1 else None
        out.append({"section": s, "n": nb, "n_section": n_sec,
                    "part_groupe": (nb / n_grp) if n_grp else 0.0,
                    "part_section": (nb / n_sec) if n_sec else 0.0,
                    "score": sc})
    return out


def suggestions(cat, clauses):
    """Ce qu'il resterait intéressant d'ajouter, d'après ce qui est déjà posé.

    Une suggestion n'est utile que si elle n'est pas déjà là : on propose les
    registres de segmentation absents de la requête, dans l'ordre où ils
    éclairent le plus souvent un profil de vulnérabilité.
    """
    poses = set()
    for c in clauses:
        if c.get("type") == "groupe":
            for v in c.get("valeurs", []):
                for nom, vals in REGISTRES:
                    if v in vals:
                        poses.add(nom)
    return [nom for nom, _ in REGISTRES if nom not in poses]
