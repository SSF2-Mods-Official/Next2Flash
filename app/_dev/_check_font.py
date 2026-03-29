"""Check font library data in N2D."""
import json, zlib, urllib.parse

import zipfile
with zipfile.ZipFile('_roundtrip_test.n2d', 'r') as zf:
    d = json.loads(zf.read('project.json'))

# Font libraries
fonts = [l for l in d['libraries'] if l.get('isFont')]
print(f"Font libraries: {len(fonts)}")
for f in fonts:
    keys = [k for k in f.keys() if k not in ('recodes', 'buffer', 'rawTagBody', 'fontData')]
    print(f"  id={f['id']}, type={f['type']}, name={f.get('name','?')}")
    print(f"  symbol={f.get('symbol','?')}")
    print(f"  fontAuxTags count={len(f.get('fontAuxTags',[]))}")
    print(f"  keys={keys}")
    if f.get('fontAuxTags'):
        for fa in f['fontAuxTags']:
            print(f"    aux: tagType={fa['tagType']}, bodyLen={len(fa['body'])}")

# rawGlobalTags
raw_gt = d.get('rawGlobalTags', [])
print(f"\nrawGlobalTags: {len(raw_gt)} entries")
for rgt in raw_gt:
    tt = rgt['tagType']
    TAG_NAMES = {72:'DoABC',73:'FontAlignZones',74:'CSMTextSettings',
        76:'SymbolClass',82:'DoABC2',86:'SceneFrameLabel',88:'DefineFontName',
        24:'Protect',45:'SoundStreamHead2'}
    name = TAG_NAMES.get(tt, f'tag{tt}')
    print(f"  {name}(type={tt}), bodyLen={len(rgt['body'])}")

# Find text libraries
texts = [l for l in d['libraries'] if l['type'] == 'text']
print(f"\nText libraries: {len(texts)}")
for t in texts[:5]:
    print(f"  id={t['id']}, name={t.get('name','?')}")
