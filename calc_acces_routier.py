"""SDG 9.1.1 : part de la population à moins de 2 km d'une route praticable
en toute saison, section communale par section communale.

MÉTHODE, celle de la Banque mondiale et de ReCAP pour l'indice d'accès rural :
un réseau routier, un raster de population, un tampon de 2 km, et le rapport
des deux. Ce qui se discute n'est pas le calcul, c'est le mot « praticable » :
il est donc calculé trois fois, sur trois définitions, et les trois chiffres
sont rendus côte à côte.
"""
import json, math
import numpy as np
import rasterio
from rasterio import features
from scipy.spatial import cKDTree

GEO = '/home/claude/project/streamlit_app/data/sections_communales.geojson'
POP = 'hti_pop_unc.tif'
OSM = 'osm_roads.json'
SEUIL_M = 2000.0
PAS_M = 100.0            # densification le long des voies

# --- les trois definitions de « praticable en toute saison »
DUR = {'paved','asphalt','concrete','concrete:plates','paving_stones','sett',
       'cobblestone','chipseal','metal','compacted'}
MOU = {'unpaved','dirt','ground','earth','mud','sand','grass','gravel',
       'fine_gravel','pebblestone','rock','woodchips'}

def classe(tags, variante):
    h = tags.get('highway'); s = (tags.get('surface') or '').lower()
    sm = (tags.get('smoothness') or '').lower()
    if h in ('path','footway','steps','corridor','pedestrian','cycleway',
             'bridleway','construction','proposed','platform','elevator'):
        return False
    if variante == 'stricte':
        if h in ('motorway','trunk','primary','secondary','tertiary',
                 'motorway_link','trunk_link','primary_link','secondary_link',
                 'tertiary_link'):
            return s not in MOU
        return s in DUR
    if variante == 'standard':
        if h in ('motorway','trunk','primary','secondary','tertiary',
                 'motorway_link','trunk_link','primary_link','secondary_link',
                 'tertiary_link'):
            return s not in MOU
        if h in ('unclassified','residential','living_street','road'):
            # sans étiquette de surface, une voie de desserte est comptée :
            # c'est le choix de la Banque mondiale quand la condition n'est
            # pas renseignée, et il est explicite.
            return s not in MOU and sm not in ('bad','very_bad','horrible',
                                               'very_horrible','impassable')
        if h in ('track','service'):
            return s in DUR
        return False
    # permissive : tout ce qui est carrossable, quelle que soit la surface
    return h in ('motorway','trunk','primary','secondary','tertiary',
                 'unclassified','residential','living_street','road','track',
                 'service','motorway_link','trunk_link','primary_link',
                 'secondary_link','tertiary_link')


def _pts(geom):
    s=[]
    def w(c):
        if isinstance(c[0], (int,float)): s.append(c)
        else:
            for k in c: w(k)
    w(geom['coordinates']); return s


def main():
    g = json.load(open(GEO, encoding='utf-8'))
    osm = json.load(open(OSM, encoding='utf-8'))['elements']
    src = rasterio.open(POP)

    # projection locale en metres, exacte a mieux que 0,1 % sur l'etendue
    lat0 = 18.27
    KY = 110900.0
    KX = 111320.0 * math.cos(math.radians(lat0))
    P = lambda lon, lat: (lon * KX, lat * KY)

    res = {}
    reseaux = {}
    for var in ('stricte', 'standard', 'permissive'):
        pts, km = [], 0.0
        for e in osm:
            if e.get('type') != 'way' or not e.get('geometry'): continue
            if not classe(e.get('tags') or {}, var): continue
            xy = [P(p['lon'], p['lat']) for p in e['geometry']]
            for i in range(len(xy)-1):
                x0,y0 = xy[i]; x1,y1 = xy[i+1]
                d = math.hypot(x1-x0, y1-y0); km += d/1000.0
                n = max(1, int(d // PAS_M))
                for k in range(n):
                    t = k/n
                    pts.append((x0+(x1-x0)*t, y0+(y1-y0)*t))
            pts.append(xy[-1])
        reseaux[var] = (cKDTree(np.array(pts)), km, len(pts))
        print(f'{var:11s} {km:8.0f} km de reseau, {len(pts):7d} points')

    for f in g['features']:
        nom = f['properties']['section']
        xs=[p[0] for p in _pts(f['geometry'])]; ys=[p[1] for p in _pts(f['geometry'])]
        w = rasterio.windows.from_bounds(min(xs),min(ys),max(xs),max(ys), src.transform)
        a = src.read(1, window=w)
        tr = src.window_transform(w)
        a = np.where(a == src.nodata, 0.0, a)
        msk = features.geometry_mask([f['geometry']], out_shape=a.shape,
                                     transform=tr, invert=True)
        yy, xx = np.nonzero(msk & (a > 0))
        if not len(yy):
            res[nom] = None; continue
        lon, lat = rasterio.transform.xy(tr, yy, xx)
        pop = a[yy, xx].astype(float)
        XY = np.column_stack([np.array(lon)*KX, np.array(lat)*KY])
        ligne = {'pop': float(pop.sum())}
        for var,(tree,_km,_n) in reseaux.items():
            d,_ = tree.query(XY, k=1)
            ligne[var] = 100.0*float(pop[d <= SEUIL_M].sum())/float(pop.sum())
        res[nom] = ligne
        print(f"{nom:14s} pop {ligne['pop']:8.0f} | stricte {ligne['stricte']:5.1f} "
              f"| standard {ligne['standard']:5.1f} | permissive {ligne['permissive']:5.1f}")

    tot = sum(v['pop'] for v in res.values() if v)
    ens = {var: sum(v[var]*v['pop'] for v in res.values() if v)/tot
           for var in ('stricte','standard','permissive')}
    print('ENSEMBLE      pop %8.0f | stricte %5.1f | standard %5.1f | permissive %5.1f'
          % (tot, ens['stricte'], ens['standard'], ens['permissive']))
    json.dump({'sections': res, 'ensemble': ens,
               'reseau_km': {v: reseaux[v][1] for v in reseaux}},
              open('rai_unc.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)

main()
