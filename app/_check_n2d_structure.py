import msgpack, zipfile, io
from collections import Counter

with open('converted/blackmage/project.n2d','rb') as f: raw=f.read()
with zipfile.ZipFile(io.BytesIO(raw)) as zf:
    doc = msgpack.unpackb(zf.read('project.msgpack'), raw=False)
libs = doc.get('library', [])
types = Counter(l.get('type') for l in libs)
print('Lib types:', dict(types))
print('Total libs:', len(libs))
dair_libs = [l for l in libs if 'dair' in (l.get('name') or '').lower()]
print('Libs with dair in name:', len(dair_libs))
for l in dair_libs[:3]:
    t = l.get('type')
    i = l.get('id')
    keys = list(l.keys())[:8]
    print(f'  type={t} id={i} keys={keys}')

# Check for any lib that has symbol set
with_sym = [l for l in libs if l.get('symbol')]
print('Libs with symbol:', len(with_sym))
for l in with_sym[:5]:
    print(f'  type={l.get("type")} id={l.get("id")} sym={l.get("symbol")}')

# Check top-level doc keys
print('Doc keys:', list(doc.keys()))
