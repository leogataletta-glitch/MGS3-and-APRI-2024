"""Les agences bancaires et distributeurs, par section communale.

CE QUE DEMANDE LA LIGNE 73, ET CE QU'ELLE NE DEMANDE PAS. L'ODD 8.10.1 compte
des AGENCES DE BANQUE COMMERCIALE ET DES DISTRIBUTEURS POUR CENT MILLE
ADULTES : c'est une statistique d'infrastructure, pas une question posée aux
ménages. Ce que l'enquête sait — qui possède un compte — est l'ODD 8.10.2, et
c'est déjà la ligne 72 du référentiel, calculée depuis les réponses. Les deux
lignes ne mesurent pas la même chose et ne se remplacent pas : l'une dit si
les gens ont un compte, l'autre s'il existe un guichet là où ils vivent.

LA SOURCE. OpenStreetMap, extrait Overpass sur toute la presqu'île du Sud :
amenity=bank, amenity=atm, amenity=bureau_de_change, amenity=money_transfer,
office=financial. C'est la seule source ouverte qui donne la POSITION des
guichets ; la BRH publie des effectifs nationaux, pas des points.

CE QUE VAUT UNE ABSENCE DANS OPENSTREETMAP, ET COMMENT ON LE VÉRIFIE. Un
zéro peut vouloir dire « il n'y a rien » ou « personne ne l'a cartographié »,
et les deux se ressemblent. Deux contrôles sont donc faits ici plutôt que
supposés. Le premier porte sur l'échelle : la base ne recense pas seulement
les agences des Cayes et de Jérémie, elle en porte à Camp-Perrin et à Aquin,
des bourgs de la taille de ceux dont dépendent nos sections — la
cartographie descend donc à ce niveau. Le second porte sur nos sections
elles-mêmes : on y compte les points d'intérêt ordinaires — commerces,
écoles, pharmacies, marchés, lieux de culte — et on publie ce compte à côté
du résultat. S'il était nul, le zéro financier ne vaudrait rien.

CE QU'EN DIT LE CONTRÔLE. Soixante-dix-huit points d'intérêt sont
cartographiés dans les dix sections, de un à Quentin à vingt-six à Barbois :
la carte n'y est pas vierge, mais elle est mince, et le zéro financier doit
se lire pour ce qu'il est — une absence probable, appuyée sur une
cartographie ténue, et non une absence certifiée par un recensement.

CE QUE LE ZÉRO NE DIT PAS. Il ne dit pas qu'il n'y a pas de vie financière :
trois cent soixante-neuf ménages de l'enquête sont membres d'une mutuelle
d'épargne ou d'une banque communautaire, et c'est vers une mutuelle de
solidarité que trois cent cinquante se tourneraient pour un crédit. Ces
structures ne sont ni des agences de banque commerciale ni des
distributeurs : elles ne comptent pas dans le 8.10.1, et c'est le barème qui
en décide, pas nous.

LA DISTANCE AU GUICHET LE PLUS PROCHE est calculée à côté, sans barème. Elle
ne fait pas partie de l'indicateur, mais c'est elle qui distingue les dix
sections, là où le compte les met toutes à zéro.
"""
import json
import os
import urllib.parse
import urllib.request

import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
GEO = os.path.join(ICI, "data", "sections_communales.geojson")
ACCES = os.path.join(ICI, "data", "acces_routier.json")
SORTIE = os.path.join(ICI, "data", "services_financiers.json")

OVERPASS = "https://overpass.kumi.systems/api/interpreter"
BOITE = (17.9, -74.7, 18.7, -73.6)

# LA PART DES ADULTES DANS LA POPULATION. L'ODD rapporte à cent mille
# ADULTES, et WorldPop donne une population totale. La part retenue est celle
# des quinze ans et plus en Haïti, 65 %, telle que la publie la division
# population des Nations unies. Elle ne change rien au classement — le
# numérateur est nul partout — mais elle rend le chiffre lisible tel quel.
PART_ADULTES = 0.65

REQUETE = """[out:json][timeout:180];
(
  nwr["amenity"="bank"]({la0},{lo0},{la1},{lo1});
  nwr["amenity"="atm"]({la0},{lo0},{la1},{lo1});
  nwr["amenity"="bureau_de_change"]({la0},{lo0},{la1},{lo1});
  nwr["amenity"="money_transfer"]({la0},{lo0},{la1},{lo1});
  nwr["office"="financial"]({la0},{lo0},{la1},{lo1});
);
out center tags;"""

# LA REQUÊTE DE CONTRÔLE : tout ce qu'une carte de bourg porte d'ordinaire.
# Elle ne sert pas à l'indicateur, elle sert à savoir si son zéro veut dire
# quelque chose.
REQUETE_POI = """[out:json][timeout:180];
(
  nwr["shop"]({la0},{lo0},{la1},{lo1});
  nwr["amenity"~"^(pharmacy|school|restaurant|fuel|marketplace|cafe|bar|"""\
    """clinic|hospital|police|post_office|townhall|place_of_worship)$"]"""\
    """({la0},{lo0},{la1},{lo1});
);
out center tags;"""

# CE QUI COMPTE DANS LE 8.10.1 ET CE QUI N'Y COMPTE PAS. L'indicateur nomme
# les agences de banque commerciale et les distributeurs. Un bureau de
# transfert d'argent n'est ni l'un ni l'autre : il est relevé, affiché à
# part, et laissé hors du compte noté.
NOTES = {"bank", "atm"}

from calc_chlorophylle import _anneaux, _distance, _metrique  # noqa: E402


def _telecharger(cache, requete=None):
    if os.path.exists(cache):
        return json.load(open(cache, encoding="utf-8"))
    la0, lo0, la1, lo1 = BOITE
    q = (requete or REQUETE).format(la0=la0, lo0=lo0, la1=la1, lo1=lo1)
    rq = urllib.request.Request(
        OVERPASS, data=urllib.parse.urlencode({"data": q}).encode(),
        headers={"User-Agent": "AppliqueIRLA/1.0"})
    with urllib.request.urlopen(rq, timeout=300) as r:
        d = json.loads(r.read().decode("utf-8"))
    json.dump(d, open(cache, "w", encoding="utf-8"))
    return d


def _points(d):
    out = []
    for x in d.get("elements") or []:
        t = x.get("tags") or {}
        lat = x.get("lat") or (x.get("center") or {}).get("lat")
        lon = x.get("lon") or (x.get("center") or {}).get("lon")
        if lat is None or lon is None:
            continue
        genre = t.get("amenity") or ("financial" if t.get("office") ==
                                     "financial" else None)
        out.append({"lat": float(lat), "lon": float(lon),
                    "genre": genre or "autre",
                    "nom": t.get("name") or ""})
    return out


def calculer(cache, cache_poi=None):
    d = _telecharger(cache)
    pts = _points(d)
    notes = [p for p in pts if p["genre"] in NOTES]
    print(f"{len(pts)} points financiers relevés, dont {len(notes)} "
          f"agences ou distributeurs")
    poi = []
    if cache_poi:
        try:
            poi = _points(_telecharger(cache_poi, REQUETE_POI))
        except Exception as e:
            print("   contrôle cartographique indisponible :", e)

    sections = json.load(open(GEO, encoding="utf-8"))["features"]
    pop = {k: v.get("pop") for k, v in
           (json.load(open(ACCES, encoding="utf-8")).get("sections") or
            {}).items()}

    proj = _metrique(18.275, -74.15)
    px, py = ([], [])
    for p in notes:
        x, y = proj(p["lon"], p["lat"])
        px.append(x)
        py.append(y)
    ax, ay = ([], [])
    for p in pts:
        x, y = proj(p["lon"], p["lat"])
        ax.append(x)
        ay.append(y)
    qx, qy = ([], [])
    for p in poi:
        x, y = proj(p["lon"], p["lat"])
        qx.append(x)
        qy.append(y)

    out = {}
    for f in sections:
        nom = f["properties"]["section"]
        ans = []
        for a in _anneaux(f["geometry"]):
            x, y = proj(a[:, 0], a[:, 1])
            ans.append(np.column_stack([x, y]))
        dedans = sum(1 for i in range(len(px))
                     if _distance(px[i], py[i], ans) == 0.0)
        dn = min(_distance(px[i], py[i], ans) for i in range(len(px)))
        da = min(_distance(ax[i], ay[i], ans) for i in range(len(ax)))
        adultes = (pop.get(nom) or 0) * PART_ADULTES
        n_poi = sum(1 for i in range(len(qx))
                    if _distance(qx[i], qy[i], ans) == 0.0)
        out[nom] = {
            "guichets": int(dedans),
            "guichets_p100k": (round(1e5 * dedans / adultes, 2)
                               if adultes else None),
            "adultes_estimes": int(round(adultes)),
            "dist_guichet_km": round(dn / 1000.0, 1),
            "dist_point_financier_km": round(da / 1000.0, 1),
            "poi_cartographies": int(n_poi),
        }
        print(f"{nom:<14} {dedans} guichet(s), "
              f"le plus proche à {out[nom]['dist_guichet_km']:.1f} km, "
              f"{out[nom]['adultes_estimes']} adultes, "
              f"{n_poi} POI de contrôle")

    tot_ad = sum(v["adultes_estimes"] for v in out.values())
    tot_g = sum(v["guichets"] for v in out.values())
    total = {"guichets": tot_g, "adultes_estimes": tot_ad,
             "guichets_p100k": round(1e5 * tot_g / tot_ad, 2) if tot_ad else 0,
             "poi_cartographies": sum(v["poi_cartographies"]
                                      for v in out.values()),
             "dist_guichet_km": round(
                 float(np.mean([v["dist_guichet_km"] for v in out.values()])),
                 1)}
    print(f"{'TOTAL':<14} {tot_g} guichet(s) pour {tot_ad} adultes = "
          f"{total['guichets_p100k']} pour 100 000 ; "
          f"{total['poi_cartographies']} POI de contrôle dans les dix "
          f"sections")
    return out, total, pts


if __name__ == "__main__":
    import sys
    cache = (sys.argv[1] if len(sys.argv) > 1
             else os.path.join(ICI, "_osm_finance.json"))
    cache_poi = (sys.argv[2] if len(sys.argv) > 2
                 else os.path.join(ICI, "_osm_poi.json"))
    out, total, pts = calculer(cache, cache_poi)
    json.dump({
        "sections": out, "total": total,
        "source": "OpenStreetMap, extrait Overpass, presqu'île du Sud",
        "part_adultes": PART_ADULTES,
        "comptes": sorted({p["genre"] for p in pts}),
        "releve": [{"genre": p["genre"], "nom": p["nom"],
                    "lat": round(p["lat"], 5), "lon": round(p["lon"], 5)}
                   for p in pts],
    }, open(SORTIE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("écrit :", SORTIE)
