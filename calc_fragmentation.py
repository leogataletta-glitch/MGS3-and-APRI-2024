"""Les sept indicateurs de fragmentation, calculés depuis ESA WorldCover 2021.

UNE SEULE CHAÎNE REMPLIT LE BLOC ENTIER. Le pré-traitement — découpe par
section, passage en mètres, définition de l'habitat — est le même pour les
sept ; ce qui change est la statistique lue à la fin.

CHOIX À DOCUMENTER, ils sont tous ici et nulle part ailleurs :
  · HABITAT = arbres (10) + arbustes (20) + zones humides herbacées (90)
    + mangrove (95). La prairie (30) est EXCLUE : elle couvre la moitié du
    territoire et elle est ici du pâturage dégradé — la compter en habitat
    rendrait toutes les sections connectées par construction.
  · PROFONDEUR DE LISIÈRE = 100 m. C'est la valeur usuelle en forêt
    tropicale fragmentée ; le CORE est l'habitat au-delà de cette distance
    de toute non-habitat.
  · d* = 1 000 m, distance de dispersion de référence, et d*/2 = 500 m.
    C'EST LE SEUL PARAMÈTRE BIOLOGIQUE, il doit être fixé par guilde avant
    publication. Il est écrit dans le fichier de sortie pour être relu.
  · p_ij = exp(-k d_ij) avec k tel que p = 0,5 à d = d*.
  · Distances de bord à bord, euclidiennes, en mètres (UTM 18N).
"""
import json, os, sys
import numpy as np
import rasterio
import croisement_moteur as M
from rasterio.warp import reproject, Resampling, calculate_default_transform
from rasterio import features
from scipy import ndimage
from scipy.spatial import cKDTree
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path

ICI = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ICI, 'data')
# LA TUILE N'EST PAS DANS LE DÉPÔT : trente-cinq mégaoctets de couverture du
# sol pour un calcul qui tourne une fois. Elle est téléchargée au besoin.
TUILE = ('https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/'
         'ESA_WorldCover_10m_2021_v200_N18W075_Map.tif')
TIF = os.path.join(DATA, 'ESA_WorldCover_10m_2021_v200_N18W075_Map.tif')
GEO = os.path.join(DATA, 'sections_communales.geojson')

HABITAT = (10, 20, 90, 95)
LISIERE_M = 100.0
D_ETOILE = 1000.0
RES = 10.0            # mètres par pixel après reprojection
AIRE_PX = RES * RES / 10000.0   # ha par pixel
MIN_PATCH_PX = 10     # 0,1 ha : en dessous, un pixel isolé n'est pas une tache
MAX_NOEUDS = 400


def _grille_utm(src, geom):
    """La section, en UTM 18N à 10 m : (tableau de classes, transform, masque)."""
    xs = [c[0] for c in _pts(geom)]
    ys = [c[1] for c in _pts(geom)]
    marge = 0.01
    w = rasterio.windows.from_bounds(min(xs) - marge, min(ys) - marge,
                                     max(xs) + marge, max(ys) + marge,
                                     src.transform)
    a = src.read(1, window=w)
    tr = src.window_transform(w)
    dst_crs = 'EPSG:32618'
    dst_tr, dw, dh = calculate_default_transform(
        src.crs, dst_crs, a.shape[1], a.shape[0],
        *rasterio.windows.bounds(w, src.transform), resolution=RES)
    out = np.zeros((dh, dw), dtype=a.dtype)
    reproject(a, out, src_transform=tr, src_crs=src.crs,
              dst_transform=dst_tr, dst_crs=dst_crs,
              resampling=Resampling.nearest)
    from rasterio.warp import transform_geom
    g_utm = transform_geom(src.crs, dst_crs, geom)
    masque = features.geometry_mask([g_utm], out_shape=out.shape,
                                    transform=dst_tr, invert=True)
    return out, masque


def _pts(geom):
    s = []
    def walk(c):
        if isinstance(c[0], (int, float)):
            s.append(c)
        else:
            for k in c:
                walk(k)
    walk(geom['coordinates'])
    return s


def _distances(etiq, ids):
    """Matrice des distances bord à bord entre taches, en mètres."""
    n = len(ids)
    D = np.full((n, n), np.inf)
    np.fill_diagonal(D, 0.0)
    bords = []
    for k in ids:
        m = (etiq == k)
        # les pixels de bordure suffisent : l'intérieur ne peut pas être le
        # plus proche voisin d'une autre tache
        b = m & ~ndimage.binary_erosion(m)
        yy, xx = np.nonzero(b if b.any() else m)
        pts = np.column_stack([xx, yy]).astype(float) * RES
        if len(pts) > 4000:                      # échantillonnage du contour
            pas = int(np.ceil(len(pts) / 4000))
            pts = pts[::pas]
        bords.append(pts)
    arbres = [cKDTree(p) for p in bords]
    for i in range(n):
        for j in range(i + 1, n):
            d = arbres[i].query(bords[j], k=1)[0].min()
            D[i, j] = D[j, i] = float(d)
    return D


def _iic(aires, D, seuil, aire_paysage):
    n = len(aires)
    if n == 0:
        return 0.0
    lien = (D <= seuil).astype(float)
    np.fill_diagonal(lien, 0.0)
    g = csr_matrix(np.where(lien > 0, 1.0, 0.0))
    nl = shortest_path(g, method='D', unweighted=True)
    nl[np.isinf(nl)] = np.inf
    np.fill_diagonal(nl, 0.0)
    num = 0.0
    for i in range(n):
        for j in range(n):
            if np.isinf(nl[i, j]):
                continue
            num += aires[i] * aires[j] / (1.0 + nl[i, j])
    return num / (aire_paysage ** 2)


def _pc(aires, D, d_seuil, aire_paysage):
    n = len(aires)
    if n == 0:
        return 0.0
    k = np.log(2.0) / d_seuil          # p = 0,5 à d = d_seuil
    P = np.exp(-k * D)
    np.fill_diagonal(P, 1.0)
    # chemin de probabilité maximale : plus court chemin sur -ln p
    W = -np.log(np.maximum(P, 1e-300))
    np.fill_diagonal(W, 0.0)
    L = shortest_path(csr_matrix(W), method='D')
    Pmax = np.exp(-L)
    num = float((np.outer(aires, aires) * Pmax).sum())
    return num / (aire_paysage ** 2)


def section(src, feat):
    nom = feat['properties'].get('section')
    cls, masque = _grille_utm(src, feat['geometry'])
    dans = masque
    aire_sec_ha = float(dans.sum()) * AIRE_PX
    hab = np.isin(cls, HABITAT) & dans
    aire_hab_ha = float(hab.sum()) * AIRE_PX

    # --- densité de lisière : transitions habitat / non-habitat, 4 voisins.
    # La bordure de la section n'est PAS comptée comme lisière : au-delà, on
    # ne sait pas ce qu'il y a, et la compter pénaliserait les petites
    # sections pour leur seule forme.
    tr = 0
    for ax, dec in ((0, 1), (1, 1)):
        a = np.roll(hab, dec, axis=ax)
        v = np.roll(dans, dec, axis=ax)
        ok = dans & v
        tr += int((ok & (hab != a)).sum())
    lisiere_m = tr * RES
    dens_lisiere = lisiere_m / aire_sec_ha if aire_sec_ha else 0.0

    # --- CORE : habitat à plus de 100 m de toute non-habitat.
    rayon = int(round(LISIERE_M / RES))
    st = np.zeros((2 * rayon + 1, 2 * rayon + 1), bool)
    yy, xx = np.ogrid[-rayon:rayon + 1, -rayon:rayon + 1]
    st[(yy * yy + xx * xx) <= rayon * rayon] = True
    core = ndimage.binary_erosion(hab, structure=st, border_value=0)
    aire_core_ha = float(core.sum()) * AIRE_PX
    core_pct = 100.0 * aire_core_ha / aire_sec_ha if aire_sec_ha else 0.0

    # --- MOVE : l'habitat non-CORE qui sert encore au déplacement, c'est-à-
    # dire celui qui appartient à une tache portant du CORE, ou qui se trouve
    # à moins de 100 m d'une telle tache. Le reste est de la poussière
    # d'habitat : ni reproduction, ni corridor.
    etiq, nb = ndimage.label(hab, structure=np.ones((3, 3), int))
    porte_core = set(np.unique(etiq[core])) - {0}
    avec_core = np.isin(etiq, list(porte_core)) if porte_core else np.zeros_like(hab)
    proche = ndimage.binary_dilation(avec_core, structure=st) & hab
    move = (proche | avec_core) & ~core & hab
    ratio_cm = ((aire_core_ha + float(move.sum()) * AIRE_PX) / aire_hab_ha
                if aire_hab_ha else 0.0)

    # --- graphe des taches
    tailles = ndimage.sum(np.ones_like(etiq), etiq, range(1, nb + 1))
    ids = [i + 1 for i, t in enumerate(tailles) if t >= MIN_PATCH_PX]
    ids.sort(key=lambda k: -tailles[k - 1])
    tronque = len(ids) > MAX_NOEUDS
    ids = ids[:MAX_NOEUDS]
    aires = np.array([tailles[k - 1] * AIRE_PX for k in ids])
    couvert = 100.0 * aires.sum() / aire_hab_ha if aire_hab_ha else 0.0
    D = _distances(etiq, ids) if ids else np.zeros((0, 0))

    r = {
        "section": nom,
        "aire_section_ha": round(aire_sec_ha, 1),
        "aire_habitat_ha": round(aire_hab_ha, 1),
        "habitat_pct": round(100.0 * aire_hab_ha / aire_sec_ha, 2) if aire_sec_ha else 0,
        "taches": len(ids), "taches_total": int(nb), "tronque": tronque,
        "part_habitat_dans_graphe_pct": round(couvert, 1),
        "densite_lisiere_m_ha": round(dens_lisiere, 2),
        "core_ha": round(aire_core_ha, 1),
        "core_pct": round(core_pct, 2),
        "move_ha": round(float(move.sum()) * AIRE_PX, 1),
        "ratio_core_move": round(ratio_cm, 4),
        "iic": round(_iic(aires, D, 20.0, aire_sec_ha), 5),
        "iic_d": round(_iic(aires, D, D_ETOILE, aire_sec_ha), 5),
        "pc_d": round(_pc(aires, D, D_ETOILE, aire_sec_ha), 5),
        "pc_d2": round(_pc(aires, D, D_ETOILE / 2.0, aire_sec_ha), 5),
    }
    return r


def _tuile():
    if not os.path.exists(TIF):
        import urllib.request
        print('telechargement de la tuile WorldCover...', flush=True)
        urllib.request.urlretrieve(TUILE, TIF)
    return TIF


def calculer():
    g = json.load(open(GEO, encoding='utf-8'))
    src = rasterio.open(_tuile())
    out = {"parametres": {
        "source": "ESA WorldCover 2021 v200, 10 m",
        "habitat_classes": list(HABITAT),
        "prairie_exclue": True,
        "profondeur_lisiere_m": LISIERE_M,
        "d_etoile_m": D_ETOILE,
        "p_a_d_etoile": 0.5,
        "resolution_m": RES,
        "crs_metrique": "EPSG:32618",
        "min_tache_ha": MIN_PATCH_PX * AIRE_PX,
        "max_noeuds": MAX_NOEUDS,
    }, "sections": {}}
    for f in g['features']:
        r = section(src, f)
        out['sections'][r['section']] = r
        print(json.dumps(r, ensure_ascii=False), flush=True)
    json.dump(out, open(os.path.join(DATA, 'fragmentation.json'), 'w',
                        encoding='utf-8'), ensure_ascii=False, indent=1)
    return out


# ----------------------------------------------------------------------
# DEUXIÈME TEMPS : ÉCRIRE LE RÉSULTAT DANS LE RÉFÉRENTIEL
# ----------------------------------------------------------------------
# ligne du référentiel -> clé calculée
CORRESP = {
    64: ("pc_d", "Probabilité, 0–1"),
    65: ("pc_d2", "Probabilité, 0–1"),
    66: ("iic", "Indice, 0–1"),
    67: ("iic_d", "Indice, 0–1"),
    68: ("densite_lisiere_m_ha", "m/ha"),
    69: ("ratio_core_move", "Ratio, 0–1"),
    70: ("core_pct", "%"),
}

NOTE_FR = ("Calculé sur ESA WorldCover 2021 (10 m). Habitat = arbres, "
           "arbustes, zones humides herbacées, mangrove ; prairie exclue "
           "(pâturage dégradé). Lisière : 100 m. d* = 1 000 m, p = 0,5 à d*. "
           "Distances de bord à bord, UTM 18N. Taches ≥ 0,1 ha.")
NOTE_EN = ("Computed on ESA WorldCover 2021 (10 m). Habitat = tree cover, "
           "shrubland, herbaceous wetland, mangrove; grassland excluded "
           "(degraded pasture). Edge depth: 100 m. d* = 1,000 m, p = 0.5 at "
           "d*. Edge-to-edge distances, UTM 18N. Patches >= 0.1 ha.")

def injecter():
    frag = json.load(open(os.path.join(DATA, 'fragmentation.json'),
                          encoding='utf-8'))
    secs = frag['sections']
    res = os.path.join(DATA, 'resultats.json')
    d = json.load(open(res, encoding='utf-8'))
    par_ligne = {r['ligne']: r for r in d}
    aires = {s: v['aire_section_ha'] for s, v in secs.items()}
    tot_aire = sum(aires.values())

    for lg, (cle, unite) in CORRESP.items():
        r = par_ligne[lg]
        bornes = M._parse_echelle(r.get('echelle'))
        spec = {"bornes": bornes, "decroissant": M._decroissant(bornes),
                "inverse": bool(r.get('bareme_inverse')),
                "max_score": max(x[0] for x in bornes)}
        vals, scores = {}, {}
        for s in M.SECTIONS:
            v = secs[s][cle]
            vals[s] = round(float(v), 4)
            scores[s] = M.score_de_ind(spec, float(v))
        # LE TOTAL EST LA MOYENNE PONDÉRÉE PAR LA SURFACE DES SECTIONS, pas
        # la moyenne des dix chiffres : une section de six mille hectares ne
        # pèse pas comme une de mille quatre cents.
        v_tot = sum(vals[s] * aires[s] for s in M.SECTIONS) / tot_aire
        vals['Total'] = round(v_tot, 4)
        scores['Total'] = M.score_de_ind(spec, v_tot)
        # LES REGISTRES SOCIAUX PORTENT LE MÊME CHIFFRE QUE LE TOTAL, comme
        # les autres indicateurs satellitaires du fichier : la mesure est
        # territoriale, elle ne varie pas selon le répondant. Le moteur, lui,
        # la porte ménage par ménage à travers sa section.
        for g in ('Homme', 'Femme', 'Cat A', 'Cat B', 'Cat C', '<25',
                  '25-39', '40-59', '60+', 'Littoral', 'Montagne'):
            if g in (r.get('valeurs') or {}):
                vals[g] = vals['Total']
                scores[g] = scores['Total']
        r['valeurs'] = {**(r.get('valeurs') or {}), **vals}
        r['scores'] = {**(r.get('scores') or {}), **scores}
        r['scores_corriges'] = {**(r.get('scores_corriges') or {}), **scores}
        r['unite'] = unite
        r['source'] = 'satellite'
        r['calculable'] = 'oui'
        r['bareme_absent'] = False
        r['note'] = NOTE_FR
        r['note_en'] = NOTE_EN
        print(lg, r['indicateur'][:38], '|', unite, '|',
              {s: (vals[s], scores[s]) for s in ('Quentin', 'Trichet')},
              '| Total', vals['Total'], scores['Total'])

    json.dump(d, open(res, 'w', encoding='utf-8'), ensure_ascii=False,
              indent=1)
    print('ecrit', res)


if __name__ == '__main__':
    calculer()
    injecter()
