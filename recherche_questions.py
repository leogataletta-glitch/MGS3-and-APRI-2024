"""Trouver les questions qui répondent à ce qui intéresse le lecteur.

Le lecteur écrit en quelques mots ce qu'il cherche (« l'eau des familles de
pêcheurs », « pertes après un cyclone »). On classe les 487 questions de
l'enquête par proximité avec cette demande : mots en commun (sans accents,
ramenés à leur racine), fragments de mots pour les fautes de frappe, et un
petit dictionnaire de notions voisines en français, anglais, espagnol et
créole, pour que « argent » trouve aussi « revenus », « crédit » et
« épargne ». Tout se calcule ici, sans service extérieur ni coût.
"""
import math
import re
import unicodedata
from collections import Counter

import numpy as np

# Notions voisines : un mot de la demande appelle tous ceux de son groupe.
NOTIONS = [
    "eau water agua dlo potable boire puits source citerne riviere",
    "assainissement sanitation toilette latrine douche hygiene saneamiento",
    "energie energy electricite courant lampe solaire charbon bois cuisson combustible",
    "dechet waste ordure poubelle residuo",
    "logement maison habitat toit mur sol housing house casa kay",
    "argent money revenu income salaire gain dinero lajan epargne savings credit pret dette emprunt banque",
    "emploi travail job work employment trabajo travay",
    "terre foncier land titre propriete fermage metayage",
    "agriculture culture champ jardin recolte harvest crop farming semis plantation rendement yield",
    "mais maize corn haricot pois bean riz rice manioc igname banane plantain patate sorgho petitmil",
    "arbre fruitier mangue avocat cocotier fruit tree",
    "engrais fertilizer intrant pesticide herbicide insecticide fongicide",
    "irrigation arrosage canal",
    "perte loss degat secheresse drought inondation flood maladie ravageur",
    "elevage livestock betail animal vache boeuf chevre cabri cochon porc poule volaille mouton cheval ane",
    "peche fishing poisson fish pecheur fisher bateau barque canot filet nasse ligne mer",
    "nourriture food alimentation repas manger faim hunger comida manje securite",
    "sante health clinique hopital dispensaire malade maladie soin",
    "ecole school education enfant eleve scolarisation",
    "entraide solidarite groupe association cooperative participation confiance conflit voisin communaute",
    "cyclone ouragan hurricane tempete storm seisme tremblement earthquake catastrophe disaster alea hazard risque alerte",
    "migration depart partir emigrer diaspora transfert remittance destination ville etranger",
    "femme woman genre gender chef menage household",
    "enfant child jeune age personne membre",
    "distance marche marche route temps acces",
    "telephone portable phone mobile reseau",
    "foret forest arbre tree reboisement reforestation deforestation bois charbon pepiniere agroforesterie bosque",
    "erosion sol soil terrasse ravine glissement conservation",
    "biodiversite biodiversity espece species conservation aire protegee mangrove corail recif herbier faune flore",
    "climat climate changement adaptation resilience",
    "plastique dechet pollution macroplastique",
    "gouvernance governance institution autorite mairie casec comite",
]


def _norm(t):
    t = unicodedata.normalize("NFD", str(t).lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]+", " ", t)


def _racines(t):
    return [m[:5] for m in _norm(t).split() if len(m) >= 3]


_GROUPES = [set(_racines(g)) for g in NOTIONS]


def _etendre(racines):
    out = Counter(racines)
    for r in set(racines):
        for g in _GROUPES:
            if r in g:
                for v in g:
                    out[v] += 0.45
    return out


def _trigrammes(t):
    t = " " + _norm(t) + " "
    return Counter(t[i:i + 3] for i in range(len(t) - 2))


def _cos(a, b):
    if not a or not b:
        return 0.0
    num = sum(v * b.get(k, 0) for k, v in a.items())
    return num / (math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values())))


def classer(documents, requete, n=10):
    """documents : {identifiant: texte}. Rend [(identifiant, score)] du plus proche au moins proche."""
    if not requete or not requete.strip():
        return []
    q_mots = _etendre(_racines(requete))
    q_tri = _trigrammes(requete)
    # Pondération inverse de la fréquence : « agriculture », présent partout
    # dans un thème, compte moins qu'un mot rare comme « citerne ».
    docs = {k: Counter(_racines(v)) for k, v in documents.items()}
    nd = len(docs) or 1
    df = Counter()
    for c in docs.values():
        df.update(set(c))
    idf = {w: math.log(1 + nd / (1 + df[w])) for w in df}
    resultats = []
    for k, c in docs.items():
        mots = sum(min(q_mots[w], 1.0) * idf.get(w, 0) for w in q_mots if w in c)
        tri = _cos(q_tri, _trigrammes(documents[k]))
        score = mots + 1.5 * tri
        if score > 0.35:
            resultats.append((k, score))
    resultats.sort(key=lambda x: -x[1])
    return resultats[:n]
