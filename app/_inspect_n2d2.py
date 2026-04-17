import zipfile, io, msgpack
from collections import Counter

with open('converted/fox/project.n2d', 'rb') as f:
    raw = f.read()
zf = zipfile.ZipFile(io.BytesIO(raw))
data = msgpack.unpackb(zf.read('project.msgpack'), raw=False)
libs = data['libraries']

id_to_lib = {}
for l in libs:
    if l:
        id_to_lib[l['id']] = l

tc = Counter(l.get('type','?') for l in libs if l)
print('Type counts:', dict(tc))

morph = [l for l in libs if l and l.get('isMorphShape')]
print('Morph shapes:', len(morph))

# Check shapes for morph/end keys
shapes = [l for l in libs if l and l.get('type') == 'shape']
morph_keys = set()
for s in shapes:
    for k in s.keys():
        if 'morph' in k.lower() or k == 'endRecodes' or k == 'endBounds':
            morph_keys.add(k)
print('Shape keys with morph/end:', morph_keys)

# Show first shape that has endRecodes
for s in shapes:
    if 'endRecodes' in s:
        print('Shape %d has endRecodes, isMorphShape=%s' % (s['id'], s.get('isMorphShape')))
        break

# Count shapes with endRecodes
end_recode_count = sum(1 for s in shapes if 'endRecodes' in s)
print('Shapes with endRecodes:', end_recode_count)

# List 10-frame containers
containers = [l for l in libs if l and l.get('type') == 'container']
c10 = [c for c in containers if c.get('totalFrame') == 10]
print('Containers with 10 frames:', len(c10))

for c in c10[:3]:
    cid = c['id']
    layers = c.get('layers', [])
    print('  Container id=%d name=%s layers=%d' % (cid, c.get('name','?'), len(layers)))
    for li, layer in enumerate(layers):
        chars = layer.get('characters', [])
        print('    Layer[%d] swfDepth=%s mode=%d chars=%d' % (
            li, layer.get('swfDepth', '?'), layer.get('mode', 0), len(chars)))
        for ci, ch in enumerate(chars):
            lid = ch.get('libraryId')
            ref = id_to_lib.get(lid, {})
            lt = ref.get('type', '?')
            is_morph = ref.get('isMorphShape', False)
            has_end = 'endRecodes' in ref
            print('      Char lib=%d type=%s morph=%s hasEnd=%s sf=%d ef=%d' % (
                lid, lt, is_morph, has_end, ch.get('startFrame',0), ch.get('endFrame',0)))
            # Show first 2 places
            places = ch.get('places', [])
            for pi, pl in enumerate(places[:2]):
                print('        place frame=%s depth=%s ratio=%s' % (
                    pl.get('frame','?'), pl.get('depth',0), pl.get('ratio')))
