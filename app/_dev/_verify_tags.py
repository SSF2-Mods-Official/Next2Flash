"""Verify SWF tag constants and check the REAL type assignments in the original SWF.
Official SWF spec tag IDs:
  20=DefineBitsLossless, 34=DefineBitsLossless2(!), 36=DefineBitsLossless2(Adobe)
  Actually need to confirm from multiple sources.
"""
import struct, zlib

SWF_PATH = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\gameandwatch.swf'

# Correct SWF tag IDs per Adobe SWF File Format Specification Version 19:
CORRECT_TAG_NAMES = {
    0:'End', 1:'ShowFrame', 2:'DefineShape', 4:'PlaceObject',
    5:'RemoveObject', 6:'DefineBits', 7:'DefineButton', 8:'JPEGTables',
    9:'SetBackgroundColor', 10:'DefineFont', 11:'DefineText',
    12:'DoAction', 13:'DefineFontInfo', 14:'DefineSound', 15:'StartSound',
    20:'DefineBitsLossless', 21:'DefineBitsJPEG2', 22:'DefineShape2',
    24:'Protect', 26:'PlaceObject2', 28:'RemoveObject2',
    32:'DefineShape3', 33:'DefineText2', 34:'DefineButton2',
    35:'DefineBitsJPEG3', 36:'DefineBitsLossless2', 37:'DefineEditText',
    39:'DefineSprite', 43:'FrameLabel', 46:'DefineMorphShape',
    48:'DefineFont2', 56:'ExportAssets', 57:'ImportAssets',
    69:'FileAttributes', 70:'PlaceObject3', 72:'DoABC',
    73:'DefineFontAlignZones', 74:'CSMTextSettings',
    75:'DefineFont3', 76:'SymbolClass', 82:'DoABC2',
    83:'DefineShape4', 84:'DefineMorphShape2', 86:'DefineSceneAndFrameLabelData',
    88:'DefineFontName', 89:'StartSound2', 90:'DefineBitsJPEG4',
}

with open(SWF_PATH, 'rb') as f:
    raw = f.read()
if raw[:3] == b'CWS':
    raw = raw[:8] + zlib.decompress(raw[8:])

offset = 8
nbits = raw[8] >> 3
total_rect_bits = 5 + nbits * 4
offset = 8 + (total_rect_bits + 7) // 8 + 4

# Count tag types used in this SWF
tag_type_counts = {}
tag_type_cids = {}
while offset < len(raw):
    tc = struct.unpack_from('<H', raw, offset)[0]
    tt = tc >> 6; tl = tc & 0x3f; offset += 2
    if tl == 0x3f:
        tl = struct.unpack_from('<I', raw, offset)[0]; offset += 4
    tag_type_counts[tt] = tag_type_counts.get(tt, 0) + 1
    # For define tags, get charID
    define_tags = {2,6,10,11,14,20,21,22,32,33,35,36,37,39,46,48,75,83,84,90}
    if tt in define_tags and tl >= 2:
        cid = struct.unpack_from('<H', raw, offset)[0]
        tag_type_cids.setdefault(tt, []).append(cid)
    offset += tl
    if tt == 0: break

print("=== Tag types present in original gameandwatch.swf ===")
for tt in sorted(tag_type_counts.keys()):
    name = CORRECT_TAG_NAMES.get(tt, f'Unknown')
    count = tag_type_counts[tt]
    cids = tag_type_cids.get(tt, [])
    cid_info = f"  charIDs: first 5 = {cids[:5]}" if cids else ""
    print(f"  Tag {tt:3d} ({name:30s}): {count:4d} occurrences{cid_info}")

# Show what the swf_to_n2d.py constants map to
print("\n=== swf_to_n2d.py TAG constants vs SWF spec ===")
swf_to_n2d_constants = {
    'TAG_DEFINE_BITS_LOSSLESS': 20,
    'TAG_DEFINE_BITS_LOSSLESS2': 36,
    'TAG_DEFINE_BITS_JPEG3': 35,
    'TAG_DEFINE_BITS_JPEG4': 90,
    'TAG_DEFINE_MORPH_SHAPE': 46,
    'TAG_DEFINE_MORPH_SHAPE2': 84,
    'TAG_DEFINE_TEXT2': 33,
    'TAG_DEFINE_EDIT_TEXT': 37,
}
for name, val in sorted(swf_to_n2d_constants.items(), key=lambda x: x[1]):
    spec = CORRECT_TAG_NAMES.get(val, 'UNKNOWN')
    match = "OK" if name.replace('TAG_','').replace('_','').lower() in spec.replace('_','').lower() or True else "MISMATCH"
    print(f"  {name:35s} = {val:3d}  →  SWF spec says: {spec}")

# Now check: are there ANY tag 46 (DefineMorphShape) entries?
if 46 in tag_type_cids:
    print(f"\n=== DefineMorphShape (tag 46) charIDs ===")
    print(f"  Count: {len(tag_type_cids[46])}")
    print(f"  First 10: {tag_type_cids[46][:10]}")
else:
    print(f"\nNo DefineMorphShape (tag 46) entries found!")

# Check tag 36 (DefineBitsLossless2)
if 36 in tag_type_cids:
    print(f"\n=== DefineBitsLossless2 (tag 36) charIDs ===")
    print(f"  Count: {len(tag_type_cids[36])}")
    print(f"  First 10: {tag_type_cids[36][:10]}")
    # Is cid=271 in here?
    if 271 in tag_type_cids[36]:
        print(f"  cid=271 IS in DefineBitsLossless2 tags")
    else:
        print(f"  cid=271 NOT in DefineBitsLossless2 tags")
