import json, zipfile

with zipfile.ZipFile('converted/gameandwatch_cli.n2d') as zf:
    data = json.loads(zf.read('project.json'))

# Check if lib_id == swfCharId
mismatch = 0
for lib in data['libraries']:
    lid = lib['id']
    cid = lib.get('swfCharId')
    if cid is not None and lid != cid:
        mismatch += 1
print(f"Libraries where id != swfCharId: {mismatch}")

# Show the actual problem: same original charIDs mapped to different lib IDs?
by_cid = {}
for lib in data['libraries']:
    cid = lib.get('swfCharId')
    if cid is not None:
        by_cid.setdefault(cid, []).append(lib)
dups = {k: v for k, v in by_cid.items() if len(v) > 1}
print(f"Duplicate swfCharIds: {len(dups)}")

# Check specific: what is at swfCharId=271 in the N2D?
for cid in [271, 367, 425, 481, 494]:
    libs = by_cid.get(cid, [])
    for lib in libs:
        print(f"  swfCharId={cid}: lib_id={lib['id']}, name={lib.get('name','?')}, type={lib.get('type')}, rawTagType={lib.get('rawTagType','?')}")

# Now check what the ORIGINAL SWF has at these charIDs
import struct, zlib
with open(r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\gameandwatch.swf', 'rb') as f:
    raw = f.read()
if raw[:3] == b'CWS': raw = raw[:8] + zlib.decompress(raw[8:])
offset = 8
first_byte = raw[8]
nbits = first_byte >> 3
total_rect_bits = 5 + nbits * 4
offset = 8 + (total_rect_bits + 7) // 8 + 4
tag_names = {2:'DefineShape',6:'DefineBits',10:'DefineFont',11:'DefineText',14:'DefineSound',
    20:'DefineBitsLossless',21:'DefineBitsJPEG2',22:'DefineShape2',
    32:'DefineShape3',33:'DefineBitsJPEG3',34:'DefineBitsLossless2',35:'DefineBitsJPEG4',
    36:'DefineMorphShape',37:'DefineFont2',39:'DefineSprite',46:'DefineMorphShape2',
    48:'DefineFont3',83:'DefineShape4',88:'DefineFontName'}
defines = {}
while offset < len(raw):
    tc = struct.unpack_from('<H', raw, offset)[0]
    tt = tc >> 6; tl = tc & 0x3f; offset += 2
    if tl == 0x3f: tl = struct.unpack_from('<I', raw, offset)[0]; offset += 4
    # Get charID from define tags
    define_tags = {2,6,10,11,14,20,21,22,32,33,34,35,36,37,39,46,48,83,88}
    if tt in define_tags and tl >= 2:
        cid = struct.unpack_from('<H', raw, offset)[0]
        defines[cid] = tag_names.get(tt, f'Tag{tt}')
    offset += tl
    if tt == 0: break

print(f"\nOriginal SWF defines: {len(defines)} charIDs")
for cid in [271, 367, 425, 481, 494]:
    print(f"  orig cid={cid}: {defines.get(cid, 'NOT FOUND')}")
