"""Build the publishable copy of the static site.

Folders holding many small JSON files are packed into bundles of about 1 MB
(data/paquets/<n>.json, each an object {path: content}) and indexed in
data/paquets.json, which apri.donnees() reads. Fewer files to publish, the same
paths for the code. Usage: python3 outils/empaqueter.py <destination>
"""
import json, os, shutil, sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.abspath(sys.argv[1])
SEUIL_FICHIERS = 20          # a folder with more JSON files than this is packed
TAILLE = 1_000_000           # target bundle size in bytes
IGNORER = {'outils', 'BRIEF.md', '__pycache__'}

if os.path.exists(DEST):
    shutil.rmtree(DEST)
os.makedirs(DEST)

a_packer = []
for d, sous, fichiers in os.walk(os.path.join(RACINE, 'data')):
    js = sorted(f for f in fichiers if f.endswith('.json'))
    if len(js) > SEUIL_FICHIERS:
        a_packer.append((d, js))
packes = {os.path.join(d, f) for d, js in a_packer for f in js}

for d, sous, fichiers in os.walk(RACINE):
    rel = os.path.relpath(d, RACINE)
    if rel.split(os.sep)[0] in IGNORER:
        sous[:] = []
        continue
    for f in fichiers:
        src = os.path.join(d, f)
        if src in packes or f in IGNORER or (rel == '.' and f.endswith('.md')):
            continue
        cible = os.path.join(DEST, rel, f)
        os.makedirs(os.path.dirname(cible), exist_ok=True)
        shutil.copy2(src, cible)

index, n, lot, taille = {}, 0, {}, 0
os.makedirs(os.path.join(DEST, 'data', 'paquets'))

def vider():
    global n, lot, taille
    if lot:
        with open(os.path.join(DEST, 'data', 'paquets', f'{n}.json'), 'w', encoding='utf-8') as fh:
            json.dump(lot, fh, ensure_ascii=False, separators=(',', ':'))
        n += 1
        lot, taille = {}, 0

for d, js in a_packer:
    for f in js:
        src = os.path.join(d, f)
        chemin = os.path.relpath(src, RACINE).replace(os.sep, '/')
        t = os.path.getsize(src)
        if lot and taille + t > TAILLE:
            vider()
        with open(src, encoding='utf-8') as fh:
            lot[chemin] = json.load(fh)
        index[chemin] = n
        taille += t
    vider()   # never mix folders in one bundle

with open(os.path.join(DEST, 'data', 'paquets.json'), 'w', encoding='utf-8') as fh:
    json.dump(index, fh, separators=(',', ':'))
total = sum(len(fs) for _, _, fs in os.walk(DEST))
print(f'{len(index)} files packed into {n} bundles; {total} files to publish')
