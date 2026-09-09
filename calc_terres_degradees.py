"""Terres dégradées (SDG 15.3.1) : la part de la section touchée par au moins
un processus de dégradation, calculée pixel par pixel.

LA RÈGLE OFFICIELLE EST « ONE OUT, ALL OUT » : une surface est dégradée si un
seul des sous-indicateurs le dit. Le référentiel en nomme trois — état de la
végétation, risque d'érosion, productivité. Deux sont calculables ici, pixel
par pixel, et le troisième ne l'est pas :

  · RISQUE D'ÉROSION : perte de sol supérieure à la tolérance usuelle de
    10 t/ha/an, prise sur la grille RUSLE déjà calculée ;
  · COUVERT ARBORÉ PERDU depuis 2000, de Hansen/UMD à 30 m ;
  · PRODUCTIVITÉ : la dynamique de productivité des terres demande une série
    temporelle de NDVI par pixel sur quinze ans. Elle n'est pas calculée ici,
    et son absence tire le chiffre VERS LE BAS : ce résultat est un
    MINORANT de la dégradation.

C'est donc une approximation documentée du 15.3.1, pas le 15.3.1 de
Trends.Earth. La différence est nommée dans la note de l'indicateur.
"""
import json, os
import numpy as np
import rasterio
from rasterio import features
from rasterio.warp import reproject, Resampling, transform_bounds, transform_geom

ICI = os.path.dirname(os.path.abspath(__file__))
GEO = '/home/claude/project/streamlit_app/data/sections_communales.geojson'
HANSEN = ('/vsicurl/https://storage.googleapis.com/earthenginepartners-hansen/'
          'GFC-2023-v1.11/Hansen_GFC-2023-v1.11_{c}_20N_080W.tif')
RES = 30.0
CRS_M = 'EPSG:32618'
TOLERANCE = 10.0     # t/ha/an, seuil de tolérance usuel

def _pts(g):
    s=[]
    def w(c):
        if isinstance(c[0],(int,float)): s.append(c)
        else:
            for k in c: w(k)
    w(g['coordinates']); return s

# on recalcule la grille A du RUSLE en la relisant du script precedent
exec(open(os.path.join(ICI,'rusle.py')).read().split('def main()')[0])

def main():
    g = json.load(open(GEO, encoding='utf-8'))
    xs=[p[0] for f in g['features'] for p in _pts(f['geometry'])]
    ys=[p[1] for f in g['features'] for p in _pts(f['geometry'])]
    b_ll=(min(xs)-.02, min(ys)-.02, max(xs)+.02, max(ys)+.02)
    b_m=transform_bounds('EPSG:4326', CRS_M, *b_ll)
    w=int((b_m[2]-b_m[0])/RES)+1; h=int((b_m[3]-b_m[1])/RES)+1
    tr=rasterio.transform.from_origin(b_m[0], b_m[3], RES, RES)

    def grille(u, resamp=Resampling.bilinear, dt='float32'):
        a=np.zeros((h,w), dt)
        with rasterio.open(u) as s:
            reproject(rasterio.band(s,1), a, dst_transform=tr, dst_crs=CRS_M,
                      resampling=resamp)
        return a

    print('MNT + pluie + sol + couverture...', flush=True)
    dem=np.zeros((h,w),'float32')
    for t in DEM_T:
        u=(f'/vsicurl/https://copernicus-dem-30m.s3.amazonaws.com/'
           f'Copernicus_DSM_COG_10_{t}_DEM/Copernicus_DSM_COG_10_{t}_DEM.tif')
        part=grille(u)
        dem=np.where(part>0, part, dem)
    pl=grille(CHIRPS); pl=np.where(pl>0, pl, np.nan)
    sol={}
    for p,ech in (('sand',10.),('silt',10.),('clay',10.),('soc',100.)):
        a=grille(SG.format(p=p)); sol[p]=np.where(a>0, a/ech, np.nan)
    cls=grille(WC, Resampling.mode, 'uint8')
    C=np.full((h,w),0.05,'float32')
    for k,v in C_CLASSE.items(): C[cls==k]=v
    A=_R(pl)*_K(sol['sand'],sol['silt'],sol['clay'],sol['soc'])*_LS(dem,RES)[0]*C

    print('perte de couvert arbore, Hansen...', flush=True)
    perte=grille(HANSEN.format(c='lossyear'), Resampling.max, 'uint8')
    couvert=grille(HANSEN.format(c='treecover2000'), Resampling.bilinear)
    # UNE PERTE NE COMPTE QUE LA OU IL Y AVAIT UNE FORET : le seuil de 30 %
    # de couvert en 2000 est celui qu'utilise deja la plateforme.
    perdu = (perte > 0) & (couvert >= 30)
    print('  pixels perdus', int(perdu.sum()))

    out={}
    for f in g['features']:
        nom=f['properties']['section']
        gm=transform_geom('EPSG:4326', CRS_M, f['geometry'])
        m=features.geometry_mask([gm], out_shape=(h,w), transform=tr, invert=True)
        a=A[m]; ok=np.isfinite(a)
        ero = np.zeros(m.sum(), bool); ero[ok] = a[ok] > TOLERANCE
        pf = perdu[m]
        deg = ero | pf
        out[nom]={
            'degrade_pct': round(100.0*float(deg.mean()),1),
            'erosion_sup_tolerance_pct': round(100.0*float(ero.mean()),1),
            'couvert_perdu_pct': round(100.0*float(pf.mean()),1),
        }
        print(f"{nom:14s}", out[nom])
    json.dump({'parametres':{
        'regle':'one out all out sur les processus calculables',
        'tolerance_erosion_t_ha_an': TOLERANCE,
        'couvert_perdu':'Hansen/UMD GFC 2023 v1.11, seuil 30 % de couvert en 2000',
        'productivite':'non calculee, le resultat est un minorant',
        'resolution_m': RES},
        'sections': out},
        open(os.path.join(ICI,'degradation.json'),'w',encoding='utf-8'),
        ensure_ascii=False, indent=1)

main()
