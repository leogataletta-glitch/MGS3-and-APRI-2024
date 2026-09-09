"""La surface d'herbiers marins devant chaque section communale.

CE QUE DEMANDE LA LIGNE 58, ET CE QU'ON PEUT LUI DONNER. Le référentiel note
l'herbier en POURCENTAGE DE SA SURFACE HISTORIQUE : il faut donc deux dates,
celle d'aujourd'hui et celle d'avant. La cartographie disponible n'en a
qu'une. On mesure donc la surface, on ne mesure pas le taux de conservation,
et la ligne reste sans score — exactement comme la mangrove de la ligne 57 et
pour exactement la même raison. Publier un chiffre en hectares là où le
barème attend un pourcentage produirait un zéro qui aurait l'air d'un
résultat.

LA SOURCE. Allen Coral Atlas, couche benthique mondiale : classification
supervisée d'images Planet Dove à 10 m, calibrée sur des relevés de terrain,
millésime 2020-2021. Elle est servie ici par le WFS public de l'atlas, sans
compte, ce qui n'était pas évident : le téléchargement des jeux complets en
demande un, le service cartographique non.

CE QUE LA CLASSE « SEAGRASS » RECOUVRE. L'atlas classe le fond peu profond en
cinq benthos — corail et algues, herbier, sable, roche, microalgues. La
classe herbier est la plus difficile des cinq à séparer : sur un fond sombre,
un herbier clairsemé et une algueraie se ressemblent, et l'atlas lui-même
publie pour cette classe la précision la plus basse. Le chiffre situe un
ordre de grandeur et un rang entre sections ; il ne remplace pas un transect.

LA PROFONDEUR EST UNE LIMITE DURE. La cartographie satellitaire du fond
s'arrête où la lumière ne revient plus, autour de quinze mètres en eau
claire, bien moins dans une eau chargée. Un herbier plus profond existe et
n'est pas ici. C'est encore un MINORANT.

L'ATTRIBUTION À UNE SECTION. Même règle que pour la chlorophylle : un
polygone d'herbier revient à une section si son centre est à moins de cinq
kilomètres de son territoire. Deux sections voisines peuvent compter le même
herbier, et le total du territoire ne compte chaque polygone qu'une fois.
"""
import json
import os
import time
import urllib.parse
import urllib.request

import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
GEO = os.path.join(ICI, "data", "sections_communales.geojson")
SORTIE = os.path.join(ICI, "data", "herbiers.json")

WFS = "https://allencoralatlas.org/geoserver/wfs"
COUCHE = "coral-atlas:benthic_data_verbose"
PAGE = 4000
RAYON = 5000.0

from calc_chlorophylle import _anneaux, _distance, _metrique  # noqa: E402


def _page(bbox):
    """Une tuile du WFS. Le filtre CQL prend la boîte en lat, lon.

    ON NE PAGINE PAS, ON DÉCOUPE. La couche benthique de l'atlas n'a pas de
    clé primaire, et GeoServer refuse alors de servir la page suivante d'un
    résultat : « cannot do natural order without a primary key ». Trier sur la
    surface pour contourner rendrait un ordre non strict, donc des doublons et
    des oublis entre pages. Découper la zone en tuiles assez petites pour
    tenir dans une seule réponse évite le problème plutôt que de le ruser, et
    la vérification est immédiate : si une tuile revient pleine, on la coupe
    en quatre.
    """
    la0, lo0, la1, lo1 = bbox
    q = {
        "service": "WFS", "version": "2.0.0", "request": "GetFeature",
        "typeName": COUCHE, "outputFormat": "application/json",
        "count": PAGE,
        "CQL_FILTER": f"BBOX(geom,{la0},{lo0},{la1},{lo1})",
    }
    u = WFS + "?" + urllib.parse.urlencode(q)
    # LE SERVEUR REFUSE UN CLIENT SANS NOM. urllib s'annonce « Python-urllib »
    # et reçoit un 403 ; un agent ordinaire passe.
    rq = urllib.request.Request(u, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppliqueIRLA/1.0",
        "Accept": "application/json"})
    for essai in range(4):
        try:
            with urllib.request.urlopen(rq, timeout=180) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if essai == 3:
                raise
            print("   ", e, "— nouvelle tentative")
            time.sleep(5 * (essai + 1))


def _tuile(bbox, feats, profondeur=0):
    """Une tuile, coupée en quatre tant qu'elle déborde de la réponse."""
    d = _page(bbox)
    f = d.get("features") or []
    if len(f) >= PAGE and profondeur < 5:
        la0, lo0, la1, lo1 = bbox
        lam, lom = (la0 + la1) / 2, (lo0 + lo1) / 2
        for b in ((la0, lo0, lam, lom), (la0, lom, lam, lo1),
                  (lam, lo0, la1, lom), (lam, lom, la1, lo1)):
            _tuile(b, feats, profondeur + 1)
        return
    feats += f


def _moissonner(bbox, cache, tuiles_utiles):
    """Tous les polygones benthiques des tuiles utiles, en cache sur disque."""
    if os.path.exists(cache):
        return json.load(open(cache, encoding="utf-8"))
    feats = []
    for i, b in enumerate(tuiles_utiles, 1):
        avant = len(feats)
        _tuile(b, feats)
        print(f"   tuile {i}/{len(tuiles_utiles)} : "
              f"{len(feats) - avant:>5} polygones  (total {len(feats)})")
    json.dump(feats, open(cache, "w", encoding="utf-8"))
    return feats


def _centre(geom):
    """Le centre du polygone, suffisant : une maille fait dix mètres."""
    c = geom["coordinates"]
    pts = []

    def marche(x):
        if isinstance(x[0], (int, float)):
            pts.append(x)
        else:
            for k in x:
                marche(k)

    marche(c)
    a = np.asarray(pts, dtype=float)
    return float(a[:, 0].mean()), float(a[:, 1].mean())


def _utiles(sections, proj, pas=0.05):
    """Les tuiles qui touchent la bande côtière d'au moins une section.

    Interroger toute la boîte reviendrait à moissonner la côte nord de la
    presqu'île, qui n'appartient à aucune des dix sections.
    """
    anneaux = []
    for f in sections:
        for a in _anneaux(f["geometry"]):
            x, y = proj(a[:, 0], a[:, 1])
            anneaux.append(np.column_stack([x, y]))
    out = []
    la = 17.90
    while la < 18.65 - 1e-9:
        lo = -74.60
        while lo < -73.70 - 1e-9:
            cx, cy = proj(lo + pas / 2, la + pas / 2)
            # La demi-diagonale de la tuile, pour ne rater aucun bord.
            marge = RAYON + 0.75 * pas * 111320.0
            if min(_distance(cx, cy, [a]) for a in anneaux) <= marge:
                out.append((round(la, 4), round(lo, 4),
                            round(la + pas, 4), round(lo + pas, 4)))
            lo += pas
        la += pas
    return out


def calculer(cache):
    sections = json.load(open(GEO, encoding="utf-8"))["features"]
    proj0 = _metrique(18.275, -74.15)
    tuiles = _utiles(sections, proj0)
    print(f"moisson du WFS Allen Coral Atlas : {len(tuiles)} tuiles utiles")
    feats = _moissonner(None, cache, tuiles)
    herbiers = [f for f in feats
                if (f["properties"].get("class_name") or "") == "Seagrass"]
    print(f"{len(feats)} polygones benthiques, dont {len(herbiers)} herbiers")

    proj = _metrique(18.275, -74.15)
    cx, cy, aire = [], [], []
    for f in herbiers:
        lo, la = _centre(f["geometry"])
        x, y = proj(lo, la)
        cx.append(x)
        cy.append(y)
        aire.append(float(f["properties"].get("area_sqkm") or 0.0) * 100.0)
    cx, cy, aire = np.array(cx), np.array(cy), np.array(aire)

    out, deja = {}, np.zeros(len(aire), dtype=bool)
    for f in sections:
        nom = f["properties"]["section"]
        ans = []
        for a in _anneaux(f["geometry"]):
            x, y = proj(a[:, 0], a[:, 1])
            ans.append(np.column_stack([x, y]))
        d = np.array([_distance(cx[i], cy[i], ans) for i in range(len(cx))])
        pris = d <= RAYON
        deja |= pris
        # UNE SECTION SANS MER N'A PAS ZÉRO HECTARE D'HERBIER, ELLE N'EN A
        # PAS LA QUESTION. Beaumont est à l'intérieur des terres : lui écrire
        # un zéro la ferait figurer au bas d'un classement auquel elle
        # n'appartient pas.
        if not pris.any():
            out[nom] = {}
            print(f"{nom:<14}         — section intérieure")
            continue
        out[nom] = {
            "surface_ha": round(float(aire[pris].sum()), 2),
            "polygones": int(pris.sum()),
            "surface_moy_m2": round(float(aire[pris].mean()) * 10000.0, 0),
        }
        print(f"{nom:<14} {out[nom]['surface_ha']:>9.2f} ha  "
              f"({out[nom]['polygones']} polygones)")
    total = round(float(aire[deja].sum()), 2)
    print(f"{'TOTAL':<14} {total:>9.2f} ha (chaque polygone compté une fois)")
    return out, total


if __name__ == "__main__":
    import sys
    cache = (sys.argv[1] if len(sys.argv) > 1
             else os.path.join(ICI, "_aca_benthique.json"))
    out, total = calculer(cache)
    # LE TOTAL EST HORS DES SECTIONS, ET C'EST NÉCESSAIRE. Rangé parmi elles,
    # il devenait une onzième section sur la carte et dans le classement.
    json.dump({"sections": out, "total": {"surface_ha": total},
               "source": "Allen Coral Atlas, couche benthique 10 m "
                         "(Planet Dove, millésime 2020-2021), WFS public",
               "rayon_m": RAYON},
              open(SORTIE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("écrit :", SORTIE)
