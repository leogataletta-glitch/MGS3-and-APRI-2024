"""L'érosion des sols et les terres dégradées, par section communale.

RUSLE : A = R × K × LS × C × P, en tonnes par hectare et par an.
Chaque facteur vient d'une source ouverte, et chacun porte sa réserve.

  R  érosivité des pluies, de CHIRPS 1981-2024 par la relation de Renard et
     Freimund (1994). Une érosivité déduite d'un cumul annuel est une
     approximation : la vraie formule demande l'intensité en trente minutes,
     que seul un pluviographe donne, et il n'y en a pas ici.
  K  érodibilité du sol, de SoilGrids 250 m par l'équation EPIC de Williams
     (1995), à partir des teneurs en sable, limon, argile et carbone.
  LS pente et longueur de pente, du MNT Copernicus 30 m. La longueur de pente
     est prise égale à la maille : sans routage d'écoulement, c'est la
     convention régionale, et elle SOUS-ESTIME l'érosion sur les longs
     versants — ce qui est le cas de la Grand'Anse.
  C  couvert végétal, de la couverture du sol ESA WorldCover 2021 à 10 m,
     une valeur par classe.
  P  pratiques antiérosives : 1, faute de donnée. Là où il y a des murets ou
     des haies vives, l'érosion réelle est plus faible que ce calcul.
"""
import json, math, os
import numpy as np
import rasterio
from rasterio import features
from rasterio.warp import reproject, Resampling, transform_bounds

ICI = os.path.dirname(os.path.abspath(__file__))
GEO = '/home/claude/project/streamlit_app/data/sections_communales.geojson'
WC = os.path.join(ICI, 'wc2021.tif')
DEM_T = ['N18_00_W074_00', 'N18_00_W075_00']
CHIRPS = ('/vsicurl/https://data.chc.ucsb.edu/products/CHIRPS-2.0/'
          'global_annual/tifs/chirps-v2.0.1981-2024.44yrs.tif')
SG = ('/vsicurl/https://files.isric.org/soilgrids/latest/data/'
      '{p}/{p}_0-5cm_mean.vrt')
RES = 30.0
CRS_M = 'EPSG:32618'

# C par classe WorldCover : arbres, arbustes, prairie, cultures, bâti, nu,
# neige, eau, zone humide, mangrove, mousse.
C_CLASSE = {10: 0.003, 20: 0.01, 30: 0.05, 40: 0.25, 50: 0.0, 60: 0.5,
            70: 0.0, 80: 0.0, 90: 0.01, 95: 0.005, 100: 0.05}


def _pts(g):
    s = []
    def w(c):
        if isinstance(c[0], (int, float)):
            s.append(c)
        else:
            for k in c:
                w(k)
    w(g['coordinates'])
    return s


def _grille(src, bounds_ll, dst_tr, w, h, resampling=Resampling.bilinear,
            dtype='float32'):
    """Rééchantillonne une source quelconque sur notre grille métrique."""
    out = np.zeros((h, w), dtype=dtype)
    reproject(rasterio.band(src, 1), out,
              dst_transform=dst_tr, dst_crs=CRS_M,
              resampling=resampling)
    return out


def _R(p_mm):
    """Érosivité annuelle, Renard & Freimund (1994)."""
    return np.where(p_mm < 850.0,
                    0.0483 * np.power(np.maximum(p_mm, 1), 1.610),
                    587.8 - 1.219 * p_mm + 0.004105 * p_mm * p_mm)


def _K(sand, silt, clay, soc):
    """Érodibilité, Williams (1995) — EPIC. Entrées en %, carbone en %."""
    sn = 1.0 - sand / 100.0
    f_csand = 0.2 + 0.3 * np.exp(-0.0256 * sand * (1 - silt / 100.0))
    f_clsi = np.power(silt / np.maximum(clay + silt, 1e-6), 0.3)
    f_orgc = 1.0 - (0.0256 * soc) / (soc + np.exp(3.72 - 2.95 * soc))
    f_hisand = 1.0 - (0.7 * sn) / (sn + np.exp(-5.51 + 22.9 * sn))
    k = f_csand * f_clsi * f_orgc * f_hisand
    return np.clip(k, 0.0, 0.7) * 0.1317      # US -> SI (t ha h / ha MJ mm)


def _LS(dem, res):
    """Pente et longueur de pente, formule de Wischmeier et Smith."""
    gy, gx = np.gradient(dem.astype('float64'), res, res)
    pente = np.arctan(np.hypot(gx, gy))          # radians
    s = np.sin(pente)
    m = np.where(s < 0.01, 0.2, np.where(s < 0.035, 0.3,
                np.where(s < 0.05, 0.4, 0.5)))
    L = np.power(res / 22.13, m)
    S = 65.41 * s * s + 4.56 * s + 0.065
    return np.clip(L * S, 0, 100), np.degrees(pente)


def main():
    g = json.load(open(GEO, encoding='utf-8'))
    xs = [p[0] for f in g['features'] for p in _pts(f['geometry'])]
    ys = [p[1] for f in g['features'] for p in _pts(f['geometry'])]
    b_ll = (min(xs) - .02, min(ys) - .02, max(xs) + .02, max(ys) + .02)
    b_m = transform_bounds('EPSG:4326', CRS_M, *b_ll)
    w = int((b_m[2] - b_m[0]) / RES) + 1
    h = int((b_m[3] - b_m[1]) / RES) + 1
    tr = rasterio.transform.from_origin(b_m[0], b_m[3], RES, RES)
    print('grille', w, 'x', h, 'a', RES, 'm')

    print('MNT...', flush=True)
    dem = np.zeros((h, w), 'float32')
    for t in DEM_T:
        u = (f'/vsicurl/https://copernicus-dem-30m.s3.amazonaws.com/'
             f'Copernicus_DSM_COG_10_{t}_DEM/Copernicus_DSM_COG_10_{t}_DEM.tif')
        with rasterio.open(u) as s:
            part = np.zeros((h, w), 'float32')
            reproject(rasterio.band(s, 1), part, dst_transform=tr,
                      dst_crs=CRS_M, resampling=Resampling.bilinear)
        dem = np.where(part > 0, part, dem)
    print('  altitude', float(np.nanmin(dem)), 'a', float(np.nanmax(dem)))

    print('pluie...', flush=True)
    with rasterio.open(CHIRPS) as s:
        pl = np.zeros((h, w), 'float32')
        reproject(rasterio.band(s, 1), pl, dst_transform=tr, dst_crs=CRS_M,
                  resampling=Resampling.bilinear)
    pl = np.where(pl > 0, pl, np.nan)
    print('  pluie annuelle', np.nanpercentile(pl, [5, 50, 95]).round(0))

    print('sol...', flush=True)
    sol = {}
    for p, ech in (('sand', 10.0), ('silt', 10.0), ('clay', 10.0),
                   ('soc', 100.0)):
        with rasterio.open(SG.format(p=p)) as s:
            a = np.zeros((h, w), 'float32')
            reproject(rasterio.band(s, 1), a, dst_transform=tr, dst_crs=CRS_M,
                      resampling=Resampling.bilinear)
        sol[p] = np.where(a > 0, a / ech, np.nan)   # g/kg -> %, dg/kg -> %
        print(' ', p, np.nanpercentile(sol[p], [5, 50, 95]).round(2))

    print('couverture...', flush=True)
    with rasterio.open(WC) as s:
        cls = np.zeros((h, w), 'uint8')
        reproject(rasterio.band(s, 1), cls, dst_transform=tr, dst_crs=CRS_M,
                  resampling=Resampling.mode)
    C = np.full((h, w), 0.05, 'float32')
    for k, v in C_CLASSE.items():
        C[cls == k] = v

    R = _R(pl)
    K = _K(sol['sand'], sol['silt'], sol['clay'], sol['soc'])
    LS, pente = _LS(dem, RES)
    A = R * K * LS * C            # P = 1
    A = np.where(np.isfinite(A), A, np.nan)
    print('R', np.nanpercentile(R, [50]).round(0), '| K',
          np.nanpercentile(K, [50]).round(3), '| LS',
          np.nanpercentile(LS, [50, 95]).round(2), '| A med',
          round(float(np.nanmedian(A)), 1))

    out = {}
    for f in g['features']:
        nom = f['properties']['section']
        m = features.geometry_mask([f['geometry']], out_shape=(h, w),
                                   transform=tr, invert=True)
        # LA GÉOMÉTRIE EST EN DEGRÉS, LA GRILLE EN MÈTRES : il faut projeter
        # le polygone avant de le rasteriser.
        from rasterio.warp import transform_geom
        gm = transform_geom('EPSG:4326', CRS_M, f['geometry'])
        m = features.geometry_mask([gm], out_shape=(h, w), transform=tr,
                                   invert=True)
        a = A[m]
        a = a[np.isfinite(a)]
        p_ = pente[m]
        if not a.size:
            continue
        out[nom] = {
            'erosion_t_ha_an': round(float(np.nanmean(a)), 1),
            'erosion_mediane': round(float(np.nanmedian(a)), 1),
            'part_sup_10': round(100.0 * float((a > 10).mean()), 1),
            'part_sup_50': round(100.0 * float((a > 50).mean()), 1),
            'pente_moy_deg': round(float(np.nanmean(p_)), 1),
            'pluie_mm': round(float(np.nanmean(pl[m])), 0),
            'K_moy': round(float(np.nanmean(K[m])), 3),
        }
        print(f"{nom:14s}", out[nom])
    json.dump({'parametres': {
        'modele': 'RUSLE, A = R x K x LS x C x P',
        'R': 'CHIRPS 1981-2024, Renard & Freimund 1994',
        'K': 'SoilGrids 250 m, Williams 1995 (EPIC)',
        'LS': 'Copernicus DEM 30 m, Wischmeier & Smith, longueur = maille',
        'C': 'ESA WorldCover 2021, une valeur par classe',
        'P': 1, 'resolution_m': RES},
        'sections': out}, open(os.path.join(ICI, 'erosion.json'), 'w',
                               encoding='utf-8'), ensure_ascii=False, indent=1)


main()
