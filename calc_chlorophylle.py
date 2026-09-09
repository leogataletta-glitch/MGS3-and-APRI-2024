"""La concentration en chlorophylle-a devant chaque section communale.

CE QUE MESURE LA LIGNE 61. La chlorophylle-a est le pigment du
phytoplancton : sa concentration dans l'eau côtière est le témoin le plus
direct d'un apport de nutriments venu de la terre — engrais lessivés, eaux
usées, sédiments arrachés aux versants. Le référentiel la note à l'envers,
et c'est la bonne façon : plus il y en a, plus le milieu est déséquilibré,
plus le score est bas.

LA SOURCE. NOAA CoastWatch, `nesdisVHNSQchlaMonthly` : VIIRS SNPP, algorithme
OCI, composites mensuels à 4 km, de janvier 2012 à juillet 2026. C'est un
service ouvert, sans compte, interrogé ici par ERDDAP. Sentinel-3 OLCI aurait
donné 300 m — quatorze fois mieux le long d'une côte étroite — mais son accès
demande un compte Copernicus que la plateforme n'a pas.

LA BANDE CÔTIÈRE D'UNE SECTION. Une section communale est un morceau de
terre ; la chlorophylle est dans l'eau. On attribue donc à chaque section les
mailles de mer situées à moins de cinq kilomètres de son territoire. Cinq
kilomètres, parce que la maille en fait quatre : plus court ne retiendrait
rien, plus long irait chercher le large, dont la chlorophylle n'a plus rien à
voir avec ce que la section déverse. Deux sections voisines peuvent partager
une maille, et elles la partagent : la mer devant Tiburon ne se découpe pas
en parcelles.

TROIS RÉSERVES, ET ELLES VONT TOUTES DANS LE MÊME SENS.
  1. À quatre kilomètres, la première maille de mer est à cheval sur la côte.
     Les algorithmes de couleur de l'eau sont calibrés pour le large ; près du
     rivage, le fond clair, les sédiments en suspension et la matière
     organique dissoute sont lus comme du pigment. La valeur obtenue est donc
     un MAJORANT, et le score un MINORANT.
  2. Les composites mensuels perdent les mailles couvertes de nuages. La
     saison des pluies — celle où le lessivage est le plus fort — est donc
     sous-représentée dans la moyenne.
  3. Le référentiel ne dit pas sur quelle période moyenner. On prend les cinq
     dernières années complètes, et la série entière depuis 2012 est calculée
     à côté pour que l'écart soit visible plutôt que caché.
"""
import glob
import json
import math
import os
import urllib.request

import numpy as np
import pandas as pd

ICI = os.path.dirname(os.path.abspath(__file__))
GEO = os.path.join(ICI, "data", "sections_communales.geojson")
SORTIE = os.path.join(ICI, "data", "chlorophylle.json")

SERVEUR = ("https://coastwatch.pfeg.noaa.gov/erddap/griddap/"
           "nesdisVHNSQchlaMonthly.csv")
BOITE = (17.90, 18.65, -74.60, -73.70)   # lat min, lat max, lon min, lon max
DEBUT, FIN = "2012-01-15", "2026-07-01"

# Le rayon de la bande côtière, en mètres. La maille VIIRS fait 4 km.
RAYON = 5000.0
# Les cinq dernières années complètes de la série, et les cinq premières.
# La seconde fenêtre ne sert pas à noter : elle sert à voir si le chiffre noté
# est un état ou une dérive.
FENETRE = (2021, 2025)
FENETRE_DEBUT = (2012, 2016)


# ----------------------------------------------------------------- géométrie

def _anneaux(geom):
    """Tous les anneaux d'un polygone ou multipolygone, à plat."""
    c = geom["coordinates"]
    if geom["type"] == "Polygon":
        return [np.asarray(a, dtype=float) for a in c]
    out = []
    for poly in c:
        out += [np.asarray(a, dtype=float) for a in poly]
    return out


def _metrique(lat0, lon0):
    """Une projection locale suffisante : la Grand'Anse tient dans 80 km."""
    kx = 111320.0 * math.cos(math.radians(lat0))
    ky = 110540.0
    return lambda lon, lat: ((lon - lon0) * kx, (lat - lat0) * ky)


def _dans(px, py, anneau):
    """Point dans un anneau, par la règle du rayon (ray casting)."""
    x, y = anneau[:, 0], anneau[:, 1]
    x1, y1 = np.roll(x, -1), np.roll(y, -1)
    coupe = ((y > py) != (y1 > py))
    with np.errstate(divide="ignore", invalid="ignore"):
        xi = x + (py - y) * (x1 - x) / np.where(y1 - y == 0, np.nan, y1 - y)
    return bool(np.nansum(coupe & (px < xi)) % 2)


def _d_segments(px, py, anneau):
    """Distance d'un point au bord d'un anneau."""
    a = anneau[:-1] if np.allclose(anneau[0], anneau[-1]) else anneau
    b = np.roll(a, -1, axis=0)
    ab = b - a
    ap = np.array([px, py]) - a
    ll = np.sum(ab * ab, axis=1)
    t = np.clip(np.sum(ap * ab, axis=1) / np.where(ll == 0, 1e-9, ll), 0, 1)
    proj = a + t[:, None] * ab
    d = np.hypot(proj[:, 0] - px, proj[:, 1] - py)
    return float(d.min())


def _distance(px, py, anneaux):
    """Zéro si le point est dans la section, sinon la distance à son bord."""
    for an in anneaux:
        if _dans(px, py, an):
            return 0.0
    return min(_d_segments(px, py, an) for an in anneaux)


# ------------------------------------------------------------------ données

def _telecharger(dossier):
    """Les composites mensuels, une requête par année, en cache sur disque."""
    os.makedirs(dossier, exist_ok=True)
    la0, la1, lo0, lo1 = BOITE
    for an in range(2012, 2027):
        p = os.path.join(dossier, f"chl_{an}.csv")
        if os.path.exists(p) and os.path.getsize(p) > 1000:
            continue
        d0 = f"{an}-01-15" if an > 2012 else DEBUT
        d1 = f"{an}-12-31" if an < 2026 else FIN
        u = (f"{SERVEUR}?chlor_a[({d0}T00:00:00Z):1:({d1}T00:00:00Z)]"
             f"[(0.0)][({la0}):1:({la1})][({lo0}):1:({lo1})]")
        try:
            urllib.request.urlretrieve(u, p)
        except Exception as e:
            print("  ", an, "indisponible :", e)


def _lire(dossier):
    ds = []
    for p in sorted(glob.glob(os.path.join(dossier, "chl_*.csv"))):
        try:
            d = pd.read_csv(p, skiprows=[1])
        except Exception:
            continue
        if len(d) and "chlor_a" in d.columns:
            ds.append(d)
    d = pd.concat(ds, ignore_index=True)
    d["time"] = pd.to_datetime(d["time"], utc=True)
    d["annee"] = d["time"].dt.year
    return d.dropna(subset=["chlor_a"])


# ------------------------------------------------------------------- calcul

def calculer(dossier):
    _telecharger(dossier)
    obs = _lire(dossier)
    sections = json.load(open(GEO, encoding="utf-8"))["features"]

    lat0 = (BOITE[0] + BOITE[1]) / 2.0
    lon0 = (BOITE[2] + BOITE[3]) / 2.0
    proj = _metrique(lat0, lon0)

    # LES MAILLES DE MER : celles qui ont porté au moins une fois une valeur.
    # Une maille de terre n'en porte jamais, l'algorithme ne s'y applique pas ;
    # c'est donc le masque océan le plus sûr, et il vient de la donnée
    # elle-même plutôt que d'une couche de côte d'une autre résolution.
    mailles = (obs.groupby(["latitude", "longitude"])["chlor_a"]
               .count().reset_index())
    mailles = mailles[mailles["chlor_a"] >= 12]
    print(f"mailles de mer retenues : {len(mailles)}")

    mx, my = proj(mailles["longitude"].to_numpy(),
                  mailles["latitude"].to_numpy())

    def _mesures(sel):
        """Les chiffres d'une sélection de mailles.

        LA MOYENNE EST PRISE PAR MAILLE PUIS ENTRE MAILLES. L'inverse
        donnerait plus de poids aux mailles les mieux dégagées de nuages,
        c'est-à-dire au large, et ferait baisser la valeur côtière.
        """
        rec = sel[sel["annee"].between(*FENETRE)]
        deb = sel[sel["annee"].between(*FENETRE_DEBUT)]
        pm = rec.groupby(["latitude", "longitude"])["chlor_a"].mean()
        pd_ = deb.groupby(["latitude", "longitude"])["chlor_a"].mean()
        pt = sel.groupby(["latitude", "longitude"])["chlor_a"].mean()
        v, v0 = float(pm.mean()), float(pd_.mean())
        mois = rec.copy()
        mois["m"] = mois["time"].dt.month
        par_mois = mois.groupby("m")["chlor_a"].mean()
        pluie = float(par_mois.reindex([5, 6, 7, 8, 9, 10]).mean())
        seche = float(par_mois.reindex([12, 1, 2, 3, 4]).mean())
        return {
            "chl_a": round(v, 3),
            "chl_a_mediane": round(float(pm.median()), 3),
            "chl_a_max_maille": round(float(pm.max()), 3),
            "chl_a_serie": round(float(pt.mean()), 3),
            "chl_a_debut": round(v0, 3),
            "chl_a_evolution_pct": round(100.0 * (v - v0) / v0, 1),
            "chl_a_saison_pluies": round(pluie, 3),
            "chl_a_saison_seche": round(seche, 3),
            "mois_utiles": int(rec["time"].nunique()),
        }

    resultat, union = {}, set()
    for f in sections:
        nom = f["properties"]["section"]
        ans = []
        for a in _anneaux(f["geometry"]):
            x, y = proj(a[:, 0], a[:, 1])
            ans.append(np.column_stack([x, y]))

        d = np.array([_distance(mx[i], my[i], ans) for i in range(len(mx))])
        pris = d <= RAYON
        # UNE SECTION SANS MER N'A PAS UNE CHLOROPHYLLE NULLE, ELLE N'EN A
        # PAS. Beaumont est à l'intérieur des terres ; lui mettre un zéro lui
        # donnerait la meilleure note du barème pour une raison qui n'a rien
        # d'écologique.
        if not pris.any():
            resultat[nom] = {}
            print(f"{nom:<14} aucune maille de mer à moins de "
                  f"{RAYON/1000:.0f} km — section intérieure")
            continue

        cles = set(zip(mailles["latitude"].to_numpy()[pris],
                       mailles["longitude"].to_numpy()[pris]))
        union |= cles
        sel = obs[[(la, lo) in cles for la, lo
                   in zip(obs["latitude"], obs["longitude"])]]
        r = _mesures(sel)
        r["mailles"] = int(pris.sum())
        r["distance_min_km"] = round(float(d[pris].min()) / 1000.0, 2)
        resultat[nom] = r
        print(f"{nom:<14} {r['chl_a']:>7.3f} mg/m3   "
              f"(2012-2016 : {r['chl_a_debut']:.3f}, "
              f"{r['chl_a_evolution_pct']:+.1f} %)   "
              f"{r['mailles']} mailles, {r['mois_utiles']} mois")

    # LE TOTAL N'EST PAS UNE MOYENNE DES SECTIONS. Les bandes côtières se
    # recouvrent : moyenner les sections compterait deux fois la mer que deux
    # voisines partagent. On repart des mailles, chacune une seule fois.
    tout = obs[[(la, lo) in union for la, lo
                in zip(obs["latitude"], obs["longitude"])]]
    total = _mesures(tout)
    total["mailles"] = len(union)
    print(f"{'TOTAL':<14} {total['chl_a']:>7.3f} mg/m3   "
          f"(2012-2016 : {total['chl_a_debut']:.3f}, "
          f"{total['chl_a_evolution_pct']:+.1f} %)   "
          f"{total['mailles']} mailles")
    return resultat, total


if __name__ == "__main__":
    import sys
    dossier = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ICI, "_chl")
    res, total = calculer(dossier)
    with open(SORTIE, "w", encoding="utf-8") as f:
        json.dump({"sections": res, "total": total,
                   "source": "NOAA CoastWatch ERDDAP nesdisVHNSQchlaMonthly "
                             "(VIIRS SNPP, OCI, 4 km, mensuel)",
                   "fenetre": list(FENETRE),
                   "fenetre_debut": list(FENETRE_DEBUT),
                   "rayon_m": RAYON, "resolution_m": 4000},
                  f, ensure_ascii=False, indent=1)
    print("écrit :", SORTIE)
