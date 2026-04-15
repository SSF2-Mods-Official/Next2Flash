"""Examine morph shape data in N2D file."""
import msgpack, zipfile

with zipfile.ZipFile('lloyd_roundtrip.n2d') as zf:
    raw = zf.read('project.msgpack')
proj = msgpack.unpackb(raw, raw=False)

morphs = [lib for lib in proj['libraries'] if lib.get('isMorphShape')]
print(f'Total morph shapes: {len(morphs)}')
for m in morphs[:5]:
    name = m.get('name', '?')
    mid = m.get('id', '?')
    print(f'\n  name={name} id={mid}')
    print(f'    keys: {sorted(m.keys())}')
    rec = m.get('recodes', [])
    print(f'    recodes length: {len(rec)}')
    if rec:
        print(f'    first 10 recodes: {rec[:10]}')
    print(f'    bounds: {m.get("bounds")}')
    start = m.get('startRecodes')
    end_rec = m.get('endRecodes')
    print(f'    startRecodes: {len(start) if start else "None"}')
    print(f'    endRecodes: {len(end_rec) if end_rec else "None"}')
    morph_fills = m.get('morphFills')
    morph_lines = m.get('morphLines')
    print(f'    morphFills: {type(morph_fills).__name__ if morph_fills is not None else "None"} len={len(morph_fills) if morph_fills else 0}')
    print(f'    morphLines: {type(morph_lines).__name__ if morph_lines is not None else "None"} len={len(morph_lines) if morph_lines else 0}')
    raw_body = m.get('rawTagBody')
    print(f'    rawTagBody: {"present len=" + str(len(raw_body)) if raw_body else "None"}')
    raw_type = m.get('rawTagType')
    print(f'    rawTagType: {raw_type}')
    end_bounds = m.get('endBounds')
    print(f'    endBounds: {end_bounds}')
