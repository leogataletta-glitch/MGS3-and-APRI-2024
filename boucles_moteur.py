"""Le moteur du graphe causal : propagation, boucles, indice global.

SÉPARÉ DE L'AFFICHAGE À DESSEIN. Ce fichier ne dessine rien ; il calcule. On
peut donc le relire, le contester et le corriger sans toucher à une seule
balise, et c'est le seul endroit où se trouve la mécanique du modèle.

CE QUE FAIT LA PROPAGATION, EXACTEMENT

Le graphe est une matrice A où A[v, u] = signe × force de la relation u → v.
On pose une variation initiale sur un nœud, puis on la propage par vagues :

    vague₀ = variation initiale
    vague_{k+1} = A · vague_k
    effet total = Σ vagues  =  (I − A)⁻¹ · vague₀ − vague₀

C'est la série de Neumann, et elle est RÉSOLUE EXACTEMENT plutôt que tronquée.
La version tronquée à douze vagues convenait tant que le rayon spectral valait
0,746 ; l'ajout du sous-système de la déforestation l'a porté à 0,98, et il
restait alors 81 % de l'effet non distribué — des chiffres faux, sans que rien
ne le signale. Une inversion de matrice 45×45 coûte moins qu'un battement de
cil et donne la somme complète.

Le rayon spectral reste surveillé pour deux raisons : au-delà de 1 la série n'a
plus de somme et le modèle s'emballe ; au-dessus de 0,9 il est très bouclé —
une petite hausse de force suffirait à le faire basculer. `diagnostic()` rend
les deux, et l'interface les affiche.

Le passage par les boucles est donc pris en compte sans réglage particulier :
une boucle renforçante amplifie la vague suivante, une boucle équilibrante la
retourne. C'est tout le mécanisme, et il tient en trois lignes.

CE QUE CE MOTEUR N'EST PAS

Ce n'est pas un modèle estimé sur les données. Les forces sont posées par le
cadre IRLA et par la littérature, pas ajustées sur l'enquête. Les résultats
sont des scénarios exploratoires : ils disent ce que le modèle implique, pas ce
que le terrain fera. Les associations réellement observées entre sections
communales sont calculées à part, portées par le champ `rho` de chaque arête,
et ne servent JAMAIS au calcul — elles sont là pour être comparées au modèle,
y compris quand elles le contredisent.
"""

import json
import os

import networkx as nx
import numpy as np

APP_DIR = os.path.dirname(os.path.abspath(__file__))
GRAPHE = os.path.join(APP_DIR, "data", "graphe_causal.json")

SECTIONS = ["Anse à Drick", "Barbois", "Dumont", "Débouchette", "Mouline",
            "Quentin", "Beaulieu", "Blactote", "Dalmette", "Trichet"]

SEUIL_NUL = 0.05     # sous 0,05 point sur 10, l'effet est dit négligeable
TENDU = 0.90         # au-delà, le système est fortement bouclé : on le dit

# MISE À L'ÉCHELLE DES FORCES — un choix de modélisation, pas un réglage.
#
# Les forces posées à dire d'expert donnent au graphe complet un rayon spectral
# de 0,98 : le système est presque à la limite de l'emballement, et une hausse
# de deux points sur un levier en produisait quinze sur un autre. Sur une
# échelle qui s'arrête à dix, c'est absurde.
#
# Ce n'est pas un défaut d'affichage. Un diagramme de boucles causales est un
# outil QUALITATIF : ses flèches disent un sens et un ordre de grandeur relatif,
# jamais une amplitude mesurée. On ramène donc l'ensemble des forces par un
# facteur unique, de sorte que le rayon spectral vaille RAYON_CIBLE.
#
# Ce que cela préserve : le signe de chaque effet, la structure des boucles,
# et l'ORDRE des indicateurs les plus touchés — tout ce que l'outil prétend
# montrer. Ce que cela abandonne : l'idée qu'un effet simulé serait un nombre
# de points crédible. Il ne l'était pas.
RAYON_CIBLE = 0.60


def charger(chemin=None):
    with open(chemin or GRAPHE, encoding="utf-8") as f:
        return json.load(f)


def matrice(graphe, brute=False):
    """A[v, u] = signe × force de u → v, et l'ordre stable des nœuds.

    `brute=True` rend la matrice des forces telles qu'elles sont écrites dans
    le fichier — c'est celle qu'il faut pour diagnostiquer le modèle. Par
    défaut la matrice est mise à l'échelle (voir RAYON_CIBLE) : c'est celle
    qui sert à propager.
    """
    ids = [n["id"] for n in graphe["noeuds"]]
    idx = {v: i for i, v in enumerate(ids)}
    A = np.zeros((len(ids), len(ids)))
    for e in graphe["aretes"]:
        A[idx[e["vers"]], idx[e["de"]]] = e["signe"] * e["force"]
    if not brute and len(ids):
        rayon = float(max(abs(np.linalg.eigvals(A))))
        if rayon > RAYON_CIBLE:
            A = A * (RAYON_CIBLE / rayon)
    return A, ids, idx


def diagnostic(graphe):
    """Le modèle converge-t-il ? À vérifier, pas à supposer.

    Si quelqu'un renforce une arête et fait passer le rayon spectral au-dessus
    de 1, la propagation part à l'infini et les chiffres deviennent absurdes
    sans prévenir. L'interface affiche ce diagnostic.
    """
    A, ids, _ = matrice(graphe, brute=True)
    rayon = float(max(abs(np.linalg.eigvals(A)))) if len(ids) else 0.0
    return {"rayon": rayon, "converge": rayon < 1, "tendu": rayon >= TENDU,
            "facteur": (RAYON_CIBLE / rayon) if rayon > RAYON_CIBLE else 1.0,
            "cible": RAYON_CIBLE,
            "noeuds": len(ids), "aretes": len(graphe["aretes"])}


def propager(graphe, variations):
    """Effet total sur chaque nœud, en points de score (échelle 0-10).

    `variations` : {id du nœud : variation posée}. L'effet rendu EXCLUT la
    variation posée elle-même sur les nœuds pilotés — c'est l'effet propagé,
    ce que l'utilisateur veut lire. La variation posée reste disponible dans
    `variations` pour l'affichage.
    """
    A, ids, idx = matrice(graphe)
    e0 = np.zeros(len(ids))
    for cle, v in (variations or {}).items():
        if cle in idx:
            e0[idx[cle]] = v
    I = np.eye(len(ids))
    try:
        total = np.linalg.solve(I - A, e0) - e0
    except np.linalg.LinAlgError:
        # (I − A) singulière : le modèle est exactement à la limite. On
        # retombe sur la somme tronquée, qui reste définie, et le diagnostic
        # affiché à l'écran dit au lecteur de s'en méfier.
        vague, total = e0.copy(), np.zeros(len(ids))
        for _ in range(200):
            vague = A.dot(vague)
            total += vague
    return {ids[i]: float(total[i]) for i in range(len(ids))}


def etat_courant(graphe, scores_par_ligne, cible="Total"):
    """Score de départ de chaque nœud mesuré, sous la cible demandée.

    Un nœud non mesuré — l'état de santé, la capacité de travail — n'a pas de
    score : il rend None, et l'interface le montre comme tel plutôt que
    d'inventer une valeur de départ.
    """
    etat = {}
    for n in graphe["noeuds"]:
        lg = n.get("ligne")
        r = scores_par_ligne.get(lg) if lg else None
        sc = (r.get("scores_corriges") or {}).get(cible) if r else None
        etat[n["id"]] = float(sc) if sc is not None else None
    return etat


def apres(etat, effets, variations):
    """État simulé, borné à l'échelle 0-10 — un score n'existe pas au-delà."""
    out = {}
    for cle, v in etat.items():
        if v is None:
            out[cle] = None
            continue
        out[cle] = max(0.0, min(10.0, v + effets.get(cle, 0.0)
                                + (variations or {}).get(cle, 0.0)))
    return out


def direction(delta):
    """↑ / ↓ / → selon le seuil de négligeabilité."""
    if delta > SEUIL_NUL:
        return "hausse"
    if delta < -SEUIL_NUL:
        return "baisse"
    return "nul"


def boucles(graphe):
    """Les boucles du graphe, classées renforçante / équilibrante.

    Le signe d'une boucle est le PRODUIT des signes de ses arêtes : pair de
    liens négatifs → renforçante, impair → équilibrante. C'est la définition
    de la dynamique des systèmes, pas une convention d'affichage.

    Triées par longueur puis par force, la force d'une boucle étant le produit
    de celles de ses arêtes — c'est ce qui décide de son poids réel dans la
    propagation.
    """
    D = nx.DiGraph()
    for n in graphe["noeuds"]:
        D.add_node(n["id"])
    for e in graphe["aretes"]:
        D.add_edge(e["de"], e["vers"], signe=e["signe"], force=e["force"])
    out = []
    for cycle in nx.simple_cycles(D):
        signe, force = 1, 1.0
        for i, u in enumerate(cycle):
            v = cycle[(i + 1) % len(cycle)]
            signe *= D[u][v]["signe"]
            force *= D[u][v]["force"]
        out.append({"noeuds": cycle,
                    "type": "renforcante" if signe > 0 else "equilibrante",
                    "force": force, "n": len(cycle)})
    return sorted(out, key=lambda b: (b["n"], -b["force"]))


def aretes_de_boucle(boucle):
    """Les couples (de, vers) d'une boucle, pour l'isoler à l'écran."""
    c = boucle["noeuds"]
    return {(c[i], c[(i + 1) % len(c)]) for i in range(len(c))}


def effet_indice(graphe, effets, variations, scores_par_ligne):
    """Effet sur l'indice global, et la part de l'indice réellement touchée.

    LES DEUX CHIFFRES COMPTENT. L'effet seul se lirait comme une variation de
    l'indice complet, alors que le graphe ne couvre qu'une partie des
    indicateurs scorés : le reste ne bouge pas, faute de relation posée. On
    rend donc aussi la part de poids couverte, pour que l'interface puisse
    l'écrire à côté.
    """
    poids_total = sum((r.get("ponderation") or 1) for r in
                      scores_par_ligne.values()
                      if (r.get("scores_corriges") or {}).get("Total")
                      is not None)
    num, poids_couvert = 0.0, 0.0
    for n in graphe["noeuds"]:
        lg = n.get("ligne")
        r = scores_par_ligne.get(lg) if lg else None
        if not r or (r.get("scores_corriges") or {}).get("Total") is None:
            continue
        p = r.get("ponderation") or 1
        avant = float(r["scores_corriges"]["Total"])
        d = effets.get(n["id"], 0.0) + (variations or {}).get(n["id"], 0.0)
        num += p * (max(0.0, min(10.0, avant + d)) - avant)
        poids_couvert += p
    return {"delta": (num / poids_total) if poids_total else 0.0,
            "part_couverte": (poids_couvert / poids_total) if poids_total
            else 0.0}


def desaccords(graphe):
    """Relations où l'association observée contredit le signe du modèle.

    Ce n'est pas une anomalie à cacher : c'est le meilleur rappel qu'une
    relation posée par un cadre théorique n'est pas une relation démontrée sur
    ce territoire. Sur dix sections communales, une corrélation n'a de toute
    façon presque aucune puissance — elle ne réfute pas le modèle, elle invite
    à en discuter en atelier.
    """
    out = []
    for e in graphe["aretes"]:
        rho = e.get("rho")
        if rho is not None and rho * e["signe"] < -0.3:
            out.append(e)
    return sorted(out, key=lambda e: e["rho"] * e["signe"])

def sous_type(boucle, sens):
    """R+ / R− / B+ / B−, selon la typologie du complément méthodologique.

    « Positive » ne veut pas dire « bonne ». Le mot dit que les variables
    bougent dans le même sens ; c'est le SENS DU DÉPART qui décide si la
    spirale est vertueuse ou vicieuse. Une boucle renforçante poussée à la
    hausse est une spirale vertueuse (R+) ; la MÊME boucle poussée à la baisse
    est une spirale vicieuse (R−).

    C'est pour cela que le sous-type est calculé ici avec `sens`, et non porté
    par la boucle elle-même : il n'appartient pas au graphe, il appartient au
    scénario qu'on est en train de jouer.
    """
    lettre = "R" if boucle["type"] == "renforcante" else "B"
    return lettre + ("+" if sens >= 0 else "−")


def leviers(graphe, lst_boucles=None):
    """Les points où une petite modification produit un grand changement.

    Trois critères, tirés du complément méthodologique, et tous calculés :

      · le DEGRÉ — un nœud très connecté participe à beaucoup de chemins ;
      · le NOMBRE DE BOUCLES auxquelles il appartient — il a un effet
        multiplicateur, pas seulement en cascade ;
      · l'APPARTENANCE À DES BOUCLES DE SENS OPPOSÉ — c'est le critère décisif.
        Un nœud présent à la fois dans une boucle renforçante et dans une
        boucle équilibrante est un point de bascule : c'est là qu'on peut
        faire passer le système d'une dynamique dégradante à une dynamique de
        résilience.
    """
    lst = lst_boucles if lst_boucles is not None else boucles(graphe)
    D = nx.DiGraph()
    for n in graphe["noeuds"]:
        D.add_node(n["id"])
    for e in graphe["aretes"]:
        D.add_edge(e["de"], e["vers"])
    out = []
    for n in graphe["noeuds"]:
        cle = n["id"]
        dedans = [b for b in lst if cle in b["noeuds"]]
        renf = sum(1 for b in dedans if b["type"] == "renforcante")
        equi = len(dedans) - renf
        out.append({
            "id": cle,
            "entrant": D.in_degree(cle), "sortant": D.out_degree(cle),
            "degre": D.in_degree(cle) + D.out_degree(cle),
            "boucles": len(dedans), "renforcantes": renf, "equilibrantes": equi,
            "bascule": renf > 0 and equi > 0,
            "poids_boucles": sum(b["force"] for b in dedans),
        })
    # Le nœud de bascule passe devant : c'est le critère qui compte le plus.
    return sorted(out, key=lambda x: (not x["bascule"], -x["boucles"],
                                      -x["degre"]))


def boucles_dominantes(graphe, lst_boucles=None, top=6):
    """Les relations partagées par le plus de boucles.

    Ce sont les croisements du système : agir sur une de ces relations touche
    plusieurs sous-systèmes à la fois. Le complément méthodologique les appelle
    des leviers de basculement, et c'est là qu'il faut chercher comment
    transformer une boucle dégradante en boucle régulatrice.
    """
    lst = lst_boucles if lst_boucles is not None else boucles(graphe)
    compte = {}
    for b in lst:
        for arc in aretes_de_boucle(b):
            e = compte.setdefault(arc, {"n": 0, "renf": 0, "equi": 0})
            e["n"] += 1
            e["renf" if b["type"] == "renforcante" else "equi"] += 1
    lignes = [{"de": k[0], "vers": k[1], **v} for k, v in compte.items()]
    return sorted(lignes, key=lambda x: -x["n"])[:top]
