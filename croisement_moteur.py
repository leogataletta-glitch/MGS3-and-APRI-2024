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

LES INDICATEURS TERRITORIAUX S'AJOUTENT AUX INDICATEURS D'ENQUÊTE. Un indice
de végétation ne se demande pas à un ménage, mais il se mesure sur la section
communale où ce ménage vit, et cette section est connue pour chacun des 1 211
répondants. Un indicateur satellitaire noté sur les dix sections par les
échelles de résilience du référentiel se porte donc sur n'importe quel
sous-groupe : chaque ménage reçoit le score de sa section, et le score du
groupe est la moyenne sur ses membres. Ce n'est PAS une mesure par ménage,
c'est une exposition territoriale — deux groupes ne s'y distinguent que par
là où ils vivent, ce qui est précisément ce qu'on veut lire quand on demande
si les ménages les plus pauvres vivent dans les sections les plus dégradées.

La couverture reste inégale, et `couverture()` la recalcule sur les données du
jour : ces chiffres ne sont pas figés ici.

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
    # LA SEPTIÈME DIMENSION MANQUAIT À L'APPEL. Elle existe partout ailleurs
    # dans la plateforme — le cadre la dessine, l'accueil lui donne sa
    # couleur — mais pas ici : ses indicateurs étaient donc chargés avec un
    # code de dimension vide, et l'agrégation les sautait en silence. Aucun ne
    # portait de score jusqu'ici, si bien que le trou ne se voyait pas ; le
    # premier indicateur culturel noté l'aurait rendu visible en le perdant.
    ("dim7", "VII. CULTURAL, IDENTITY-BASED, AND PSYCHOLOGICAL DIMENSION"),
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

# UN NOMBRE DU RÉFÉRENTIEL PEUT COMMENCER PAR SON POINT. Les barèmes de
# connectivité sont écrits « 1 (.1 to .15) », sans le zéro : le motif exigeait
# un chiffre avant la virgule, si bien que « .15 » se lisait « 15 » et que
# toute l'échelle passait de l'intervalle [0, 1] à l'intervalle [0, 100].
_NUM = r"(-?(?:\d+(?:[.,]\d+)?|[.,]\d+))"


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
    """Le barème publié, « 0 (≤18,9%), 1 (18,9–31,9%), … », en
    [(score, borne basse, borne haute)].

    LES DEUX BORNES SONT GARDÉES, PAS SEULEMENT LA HAUTE. Sur un barème
    croissant, c'est la borne haute qui fait passer au score suivant ; sur un
    barème inversé — « 0 (> 100 m/ha), 1 (90–100 m/ha) » — c'est la borne
    BASSE. Ne garder que le dernier nombre de chaque classe donnait 100 pour
    la classe 0 comme pour la classe 1, deux bornes égales, et la densité de
    lisière se retrouvait notée 10 sur 10 là où elle valait 0.

    LE SIGNE MOINS DU RÉFÉRENTIEL N'EST PAS UN TIRET DU CLAVIER. Les barèmes
    sont écrits avec U+2212, que `_NUM` ne reconnaissait pas : « 0 (-1 to
    -0.8) » se lisait « 0 (1 to 0.8) », et huit barèmes environnementaux se
    retrouvaient avec des bornes positives, donc à l'envers. Le tiret
    demi-cadratin, lui, reste un séparateur d'intervalle et n'est pas touché.
    """
    txt = (txt or "").replace("\u2212", "-")
    corps = txt.split(":", 1)[-1]

    out = []
    # LE RÉFÉRENTIEL NE FERME PAS TOUJOURS SES CLASSES PAR UNE PARENTHÈSE.
    # Cinq barèmes sont écrits en notation d'intervalle mathématique — « 0
    # (≥ 95,0 %], 1 (85,0–95,0 %] » pour l'isolement, « 1[38,96–45,07[ » pour
    # la vaccination — où le crochet dit si la borne est comprise. Le motif
    # d'avant exigeait une parenthèse fermante : il ne trouvait donc AUCUNE
    # fin de classe et avalait tout le barème comme une classe unique allant
    # de la première borne à la dernière. L'échelle rendait alors un seul
    # score, le même pour toute valeur, et rien ne le signalait. Les deux
    # familles de délimiteurs sont donc acceptées à l'ouverture comme à la
    # fermeture ; ce que le crochet dit de l'inclusion des bornes n'est pas
    # lu, la convention du référentiel — la classe dont la borne basse est la
    # plus grande sous la valeur — tranche déjà les cas limites.
    for m in re.finditer(r"(\d+)\s*[(\[]\s*([^()\[\]]*)[)\]\[]", corps):
        # UN BARÈME À DEUX CÔTÉS N'EST PAS UN BARÈME ORDONNÉ, et on ne le
        # devine pas. « 9 (90–95 ou 100–102,5) » note l'écart à une normale
        # dans les deux sens : une seule borne par classe ne peut pas le
        # représenter. LE TEST PORTE SUR LA CLASSE, PAS SUR LA PHRASE : le
        # chercher dans le texte entier écartait cinq barèmes parfaitement
        # ordonnés dont une classe se lit « 5 or less ».
        if re.search(r"\d\s*[-–]\s*\d.*\b(ou|or)\b.*\d\s*[-–]\s*\d",
                     m.group(2), re.I):
            return None
        nums = [float(x.replace(",", ".")) for x in re.findall(_NUM, m.group(2))]
        if nums:
            out.append((int(m.group(1)), min(nums), max(nums)))
    if out:
        return out

    # LES BARÈMES SANS PARENTHÈSES. Une partie du référentiel écrit ses
    # classes autrement — « 0 = 0, 1 > 0–0,40, 2 > 0,40–0,50 » pour l'indice
    # de diversité des cultures, « 0: 0–5 % | 1: >5–15 % » pour les neuf
    # indicateurs culturels. Ce sont les mêmes classes, avec un autre signe
    # entre le score et sa plage, et les déclarer illisibles revenait à dire
    # qu'un barème publié n'existe pas. On exige au moins cinq classes : une
    # échelle décrite en toutes lettres, comme celles de la biodiversité de
    # terrain, ne doit pas être prise pour une suite de nombres.
    for sep in ("|", ";", ","):
        bouts = [b for b in corps.split(sep) if b.strip()]
        libre = []
        for b in bouts:
            m = re.match(r"\s*(\d+)\s*[:=>]+\s*(.+)$", b)
            if not m:
                continue
            nums = [float(x.replace(",", ".")) for x in re.findall(_NUM, m.group(2))]
            if nums:
                libre.append((int(m.group(1)), min(nums), max(nums)))
        if len(libre) >= 5:
            return libre
    return None


def _decroissant(bornes):
    """Le sens du barème, lu sur ses extrêmes et non sur ses deux premières
    classes : deux classes voisines peuvent partager une borne, et la
    comparaison tombait alors du mauvais côté."""
    if not bornes or len(bornes) < 2:
        return False
    a, b = bornes[0], bornes[-1]
    return _h(a) > _h(b)


def _h(b):
    return b[2] if len(b) > 2 else b[1]


def _l(b):
    return b[1]


def _score_de(val, bornes, decroissant):
    """Le score d'une valeur, selon le barème et son sens.

    LA CONVENTION EST CELLE DU RÉFÉRENTIEL, RETROUVÉE SUR SES PROPRES
    CHIFFRES. Les barèmes publiés ne sont ni des partitions parfaites ni des
    intervalles fermés des deux côtés : « 5 (50–60), 6 (60–70) » place 60 dans
    la classe 6, et « 2 (92,5–96,5), 3 (96,8–98,0) » place 96,67 — qui tombe
    dans le trou — dans la classe 2. Les deux se déduisent d'une seule règle :
    on retient la classe dont la BORNE BASSE est la plus haute des bornes
    basses inférieures ou égales à la valeur. Sur un barème inversé, la même
    règle se lit sur la borne haute. Vérifié sur les 1 444 couples
    (valeur, score) déjà publiés dans le fichier : 1 440 concordances.
    """
    if val is None or not bornes:
        return None
    val = float(val)
    if not decroissant:
        for b in reversed(bornes):
            if _l(b) <= val:
                return b[0]
        return bornes[0][0]
    for b in reversed(bornes):
        if _h(b) >= val:
            return b[0]
    return bornes[0][0]


def score_de_ind(ind, val):
    """Le score d'une valeur POUR CET INDICATEUR, barème publié compris.

    LE DRAPEAU « BARÈME INVERSÉ » RETOURNE L'ÉCHELLE. Quatre indicateurs du
    référentiel — pêche destructrice, insécurité alimentaire, violence subie,
    turbidité — ont un barème écrit dans l'ordre contraire à celui de leurs
    scores publiés : 1,65 % de pêche destructrice y vaut 10 sur 10, et non 0.
    La vérification le montre sur les vingt-deux valeurs de chacun. La classe
    lue est donc retranchée du maximum, et cela vaut partout : sans quoi la
    turbidité de l'eau récompenserait l'eau la plus trouble.
    """
    b = ind.get("bornes")
    if not b or val is None:
        return None
    sc = _score_de(val, b, ind.get("decroissant"))
    if sc is None:
        return None
    return (ind["max_score"] - sc) if ind.get("inverse") else sc


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
        decroissant = _decroissant(bornes)
        val = 100.0 * cible.sum() / base.sum()

        # LA VÉRIFICATION. Reproduire la valeur publiée à moins d'un point ET
        # retomber sur le score publié : sans cela, la définition n'est pas
        # celle du référentiel, et la porter sur un sous-groupe donnerait un
        # chiffre faux que rien ne signalerait.
        if abs(val - float(pub)) > 1.0:
            ecartes.append((r, "base"))
            continue
        _spec = {"bornes": bornes, "decroissant": decroissant,
                 "inverse": bool(r.get("bareme_inverse")),
                 "max_score": max(x[0] for x in bornes)}
        if score_de_ind(_spec, val) != \
                (r.get("scores_corriges") or {}).get("Total"):
            ecartes.append((r, "bareme"))
            continue

        indicateurs.append({
            "ligne": r["ligne"], "dim": DIM_DE.get(r["dimension"], ""),
            "nom": r.get("indicateur"), "nom_fr": r.get("indicateur_fr"),
            "poids": r.get("ponderation") or 1, "bornes": bornes,
            "decroissant": decroissant, "inverse": _spec["inverse"],
            "max_score": _spec["max_score"], "base": base, "cible": cible,
            "valeur_pub": float(pub),
            "score_pub": (r.get("scores_corriges") or {}).get("Total"),
        })

    # LES INDICATEURS CALCULÉS PAR UNE RÈGLE. Le taux de surpeuplement n'est
    # coché nulle part : il se déduit de deux questions numériques et d'un
    # critère. Une règle rend exactement ce qu'une modalité rend — une base et
    # une cible — et l'indicateur qui en sort est un indicateur de ménage
    # comme les autres : il se ventile par sexe, par richesse, par section, et
    # il entre dans l'indice avec son poids. Sans ce chemin, un indicateur que
    # l'enquête PORTE était déclaré absent.
    try:
        import indicateurs_regles as _reg
        _rgl = _reg.charger(groupes=groupes, n=n)
        _rvl = _reg.charger_valeurs(groupes=groupes, n=n)
    except Exception:
        _rgl, _rvl = {}, {}
    _par_ligne = {r.get("ligne"): r for r in res}
    # UNE RÈGLE DEVIENT AUSSI UNE QUESTION. Deux lignes sont ajoutées à la
    # matrice — « oui » et « non » — et une entrée au catalogue des
    # questions : l'écran des résultats bruts la ventile alors par section
    # comme n'importe quelle réponse d'enquête, sans une ligne de code de
    # plus. C'est ce qui manquait pour que le surpeuplement se lise là où on
    # le cherche.
    _qs = list(index["questions"])
    _i_max = max([q.get("i", 0) for q in _qs] or [0])
    _sup = []
    for _lg, (_base, _cible) in (_rgl or {}).items():
        _sp = (getattr(_reg, "QUESTIONS", {}) or {}).get(_lg)
        if not _sp:
            continue
        _i_max += 1
        _sup.append(np.asarray(_cible, dtype=bool))
        _sup.append(np.asarray(_base & ~_cible, dtype=bool))
        _qs.append({
            "i": _i_max, "question": _sp["question"],
            "category": _sp["categorie"], "modalites": list(_sp["modalites"]),
            "debut": bits.shape[0] + len(_sup) - 2, "regle": _lg,
        })
        try:
            import libelles_enquete as _lib
            _lib.ajouter("q", _sp["question"], _sp.get("question_en") or "")
            _lib.ajouter("c", _sp["categorie"], _sp.get("categorie_en") or "")
        except Exception:
            pass
    if _sup:
        bits = np.vstack([bits] + _sup)
        index = {**index, "questions": _qs}

    for _lg, (_base, _cible) in (_rgl or {}).items():
        r = _par_ligne.get(_lg)
        if r is None:
            continue
        bornes = _parse_echelle(r.get("echelle"))
        if not bornes:
            continue
        indicateurs.append({
            "ligne": _lg, "dim": DIM_DE.get(r["dimension"], ""),
            "nom": r.get("indicateur"), "nom_fr": r.get("indicateur_fr"),
            "poids": r.get("ponderation") or 1, "bornes": bornes,
            "decroissant": _decroissant(bornes),
            "inverse": bool(r.get("bareme_inverse")),
            "max_score": max(x[0] for x in bornes),
            "base": np.asarray(_base, dtype=bool),
            "cible": np.asarray(_cible, dtype=bool),
            "regle": True,
            "unite": (r.get("unite") or "").strip(),
            "valeur_pub": (r.get("valeurs") or {}).get("Total"),
            "score_pub": (r.get("scores_corriges") or {}).get("Total"),
        })

    # LES RÈGLES À VALEUR. Le score d'un groupe est la MOYENNE de la valeur de
    # ses ménages, notée ensuite par le barème — et non une part de ménages.
    # Confondre les deux ferait lire « 70 % des ménages » là où l'indice de
    # diversité vaut 0,70.
    # UNE RÈGLE PEUT RENDRE DEUX VECTEURS OU TROIS. Deux — base et valeur —
    # et le chiffre du groupe est la moyenne de ses ménages : c'est le cas de
    # la diversité des cultures. Trois — base, valeur et POIDS — et c'est un
    # rapport de totaux : le capital d'élevage perdu par un territoire est la
    # somme des unités animales mortes sur la somme des troupeaux, jamais la
    # moyenne des taux de chaque cour, qui donnerait le même poids à deux
    # chèvres qu'à quarante bovins. Un poids de un partout redonne la
    # moyenne : c'est la même mécanique avec un vecteur de plus.
    # UNE RÈGLE PEUT DÉCLARER QUE SON BARÈME NE LUI CONVIENT PAS. L'autonomie
    # des femmes et la scolarisation des filles se mesurent sur ce que
    # l'enquête porte, mais pas sur ce que le référentiel décrit : leurs
    # barèmes s'appliqueraient sans broncher et produiraient des notes
    # fausses. Le module des règles tient la liste et dit pourquoi ; le moteur
    # la respecte et publie la valeur sans la noter.
    _sans = set(getattr(_reg, "SANS_BAREME", set()) if _rvl else set())
    for _lg, _r in (_rvl or {}).items():
        if _lg in _sans:
            continue
        _base, _val = _r[0], _r[1]
        _pds = _r[2] if len(_r) > 2 else None
        r = _par_ligne.get(_lg)
        if r is None:
            continue
        bornes = _parse_echelle(r.get("echelle"))
        if not bornes:
            continue
        indicateurs.append({
            "ligne": _lg, "dim": DIM_DE.get(r["dimension"], ""),
            "nom": r.get("indicateur"), "nom_fr": r.get("indicateur_fr"),
            "poids": r.get("ponderation") or 1, "bornes": bornes,
            "decroissant": _decroissant(bornes),
            "inverse": bool(r.get("bareme_inverse")),
            "max_score": max(x[0] for x in bornes),
            "base": np.asarray(_base, dtype=bool),
            "valeur_h": np.asarray(_val, dtype=float),
            "poids_h": (None if _pds is None
                        else np.asarray(_pds, dtype=float)),
            "moyenne": True, "regle": True,
            "unite": (r.get("unite") or "").strip(),
            "valeur_pub": (r.get("valeurs") or {}).get("Total"),
            "score_pub": (r.get("scores_corriges") or {}).get("Total"),
        })

    # LES INDICATEURS TERRITORIAUX. Ils sont notés, mais pas sur des ménages :
    # sur des sections. La condition d'admission est donc simple et
    # vérifiable — le référentiel doit rendre un score sur CHACUNE des dix
    # sections. Un indicateur noté seulement au total ne dirait rien d'un
    # sous-groupe et resterait dehors.
    territoriaux = []
    # UN INDICATEUR DÉJÀ RETENU NE SE REPREND PAS PAR L'AUTRE CHEMIN. Le taux
    # de surpeuplement est calculé par une règle sur les ménages ET porte des
    # scores par section dans le fichier : sans ce garde-fou il entrait deux
    # fois, son poids comptait double dans l'indice, et le sélecteur en
    # offrait deux exemplaires dont l'un se disait territorial.
    # ET UNE MESURE DE MÉNAGE NON RETENUE NE DOIT PAS REVENIR PAR LÀ NON
    # PLUS. La scolarisation des filles est calculée par une règle, publiée
    # section par section, et volontairement laissée sans note : le chemin
    # territorial la reprenait, appliquait le barème aux valeurs de section
    # et lui rendait la note que la règle avait refusée. Le test porte
    # désormais sur la FAMILLE de la source — tout ce qui commence par
    # « menage » est une mesure de ménage — et sur la liste des lignes dont
    # le module de règles déclare que le barème ne convient pas.
    _deja = {i["ligne"] for i in indicateurs} | _sans
    for r in res:
        if r.get("ligne") in _deja:
            continue
        if (r.get("source") or "menage").startswith("menage"):
            continue
        sc = dict(r.get("scores_corriges") or r.get("scores") or {})
        vals = r.get("valeurs") or {}

        # LE BARÈME EXISTE, IL SUFFIT DE L'APPLIQUER. Trois indicateurs
        # environnementaux — NDWI, turbidité, et la stabilité de l'eau — ont
        # une mesure par section et une échelle de résilience publiée, mais
        # aucun score : personne ne les avait croisés. On les note ici avec le
        # barème du référentiel, et la même fonction rend exactement les
        # scores publiés des six autres, ce qui vaut vérification.
        ech = r.get("echelle") or ""
        bornes = _parse_echelle(ech)
        # UN BARÈME EN POURCENTAGE NE NOTE PAS DES HECTARES. La surface de
        # mangrove est mesurée en ha et son échelle est une part conservée :
        # lui appliquer le barème rendrait un zéro qui aurait l'air d'un
        # résultat. Elle reste sans score jusqu'à ce que la surface de
        # référence soit posée.
        unite = (r.get("unite") or "").strip()
        compatible = bool(bornes) and not ("%" in ech and unite
                                           and "%" not in unite)
        decroissant = _decroissant(bornes)
        if compatible:
            _spt = {"bornes": bornes, "decroissant": decroissant,
                    "inverse": bool(r.get("bareme_inverse")),
                    "max_score": max(x[0] for x in bornes)}
            for s in SECTIONS:
                if sc.get(s) is None and vals.get(s) is not None:
                    sc[s] = score_de_ind(_spt, float(vals[s]))

        if all(sc.get(s) is None for s in SECTIONS):
            continue
        s_h = np.full(n, np.nan)
        v_h = np.full(n, np.nan)
        for s in SECTIONS:
            m = groupes.get(s)
            if m is None or sc.get(s) is None:
                continue
            s_h[m] = float(sc[s])
            if vals.get(s) is not None:
                v_h[m] = float(vals[s])
        if np.isnan(s_h).all():
            continue
        territoriaux.append({
            "ligne": r["ligne"], "dim": DIM_DE.get(r["dimension"], ""),
            "nom": r.get("indicateur"), "nom_fr": r.get("indicateur_fr"),
            "poids": r.get("ponderation") or 1, "territorial": True,
            "source": r.get("source") or "",
            "unite": (r.get("unite") or "").strip(),
            "score_h": s_h, "valeur_h": v_h,
        })

    return {
        "n": n, "bits": bits, "questions": index["questions"],
        "groupes": groupes, "indicateurs": indicateurs,
        "territoriaux": territoriaux,
        "poids_total": poids_total, "n_scores": len(scores),
        "poids_couvert": (sum(i["poids"] for i in indicateurs)
                          + sum(i["poids"] for i in territoriaux)),
        "ecartes": [(r["ligne"], m) for r, m in ecartes],
    }


def couverture(cat):
    """Part du référentiel que le sous-groupe peut réellement faire bouger,
    globalement et par dimension. C'est le chiffre à écrire à côté du score."""
    par_dim = {}
    for cle, _long in DIMENSIONS:
        par_dim[cle] = (
            sum(i["poids"] for i in cat["indicateurs"] if i["dim"] == cle)
            + sum(i["poids"] for i in (cat.get("territoriaux") or [])
                  if i["dim"] == cle))
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
def valeur_moyenne(ind, base):
    """Le chiffre d'un indicateur à valeur, sur une base déjà masquée.

    UN SEUL ENDROIT POUR CETTE FORMULE. Trois écrans la calculaient — le
    profil, l'explorateur, l'analyse des écarts — et le jour où le poids est
    arrivé, il fallait les corriger tous les trois ou les laisser diverger en
    silence, chacun affichant un chiffre différent pour le même indicateur et
    le même groupe.

    Sans poids, c'est la moyenne des ménages. Avec, c'est la somme des
    valeurs pondérées sur la somme des poids, c'est-à-dire un rapport de
    totaux : le capital d'élevage perdu par un territoire, la part de récolte
    perdue par un ménage.
    """
    v = ind["valeur_h"][base]
    if not v.size:
        return None
    p = ind.get("poids_h")
    if p is None:
        return float(v.mean())
    p = p[base]
    s = float(p.sum())
    return (float(np.dot(v, p) / s) if s > 0 else None)


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
        if ind.get("moyenne"):
            v = valeur_moyenne(ind, base) if nb else None
            out.append({**{k: ind.get(k) for k in
                           ("ligne", "dim", "nom", "nom_fr", "poids",
                            "unite")},
                        "moyenne": True, "n": nb, "valeur": v,
                        "score": (score_de_ind(ind, v) if v is not None
                                  else None)})
            continue
        if nb == 0:
            out.append({**{k: ind.get(k) for k in
                           ("ligne", "dim", "nom", "nom_fr", "poids",
                            "unite")},
                        "n": 0, "valeur": None, "score": None})
            continue
        val = 100.0 * float((ind["cible"] & masque).sum()) / nb
        out.append({**{k: ind.get(k) for k in
                       ("ligne", "dim", "nom", "nom_fr", "poids", "unite")},
                    "n": nb, "valeur": val,
                    "score": score_de_ind(ind, val)})

    # LE SCORE TERRITORIAL EST UNE MOYENNE SUR LES MÉNAGES, PAS SUR LES DIX
    # SECTIONS. La différence n'est pas cosmétique : une moyenne des sections
    # donnerait le même chiffre à tous les groupes, alors qu'un groupe dont
    # les deux tiers vivent à Quentin doit porter le score de Quentin. Ce sont
    # les ménages du groupe qui pondèrent, un par un.
    for ind in cat.get("territoriaux") or []:
        s = ind["score_h"][masque]
        s = s[~np.isnan(s)]
        v = ind["valeur_h"][masque]
        v = v[~np.isnan(v)]
        out.append({**{k: ind.get(k) for k in
                       ("ligne", "dim", "nom", "nom_fr", "poids", "unite")},
                    "territorial": True, "n": int(s.size),
                    "valeur": (float(v.mean()) if v.size else None),
                    "score": (float(s.mean()) if s.size else None)})
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
