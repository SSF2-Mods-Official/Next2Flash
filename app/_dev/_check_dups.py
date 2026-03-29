"""Check if the original SWF has any charIDs defined more than once (redefined)."""
import struct, zlib

SWF_PATH = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\gameandwatch.swf'

tag_names = {
    2:'DefineShape', 6:'DefineBits', 10:'DefineFont', 11:'DefineText',
    14:'DefineSound', 20:'DefineBitsLossless', 21:'DefineBitsJPEG2',
    22:'DefineShape2', 32:'DefineShape3', 33:'DefineBitsJPEG3',
    34:'DefineBitsLossless2', 35:'DefineBitsJPEG4',
    36:'DefineMorphShape', 37:'DefineFont2', 39:'DefineSprite',
    46:'DefineMorphShape2', 48:'DefineFont3', 83:'DefineShape4',
    88:'DefineFontName',
}
define_tags = set(tag_names.keys())

with open(SWF_PATH, 'rb') as f:
    raw = f.read()
if raw[:3] == b'CWS':
    raw = raw[:8] + zlib.decompress(raw[8:])

# Skip header
offset = 8
nbits = raw[8] >> 3
total_rect_bits = 5 + nbits * 4
offset = 8 + (total_rect_bits + 7) // 8 + 4

# Walk all tags, record each definition with its order
definitions = {}  # cid -> list of (order, tag_type)
order = 0
while offset < len(raw):
    tc = struct.unpack_from('<H', raw, offset)[0]
    tt = tc >> 6; tl = tc & 0x3f; offset += 2
    if tl == 0x3f:
        tl = struct.unpack_from('<I', raw, offset)[0]; offset += 4
    if tt in define_tags and tl >= 2:
        cid = struct.unpack_from('<H', raw, offset)[0]
        definitions.setdefault(cid, []).append((order, tt))
    offset += tl
    order += 1
    if tt == 0:
        break

# Find duplicates
dups = {k: v for k, v in definitions.items() if len(v) > 1}
print(f"Total charIDs: {len(definitions)}")
print(f"CharIDs defined more than once: {len(dups)}")
for cid, defs in sorted(dups.items()):
    types = [(tag_names.get(tt, f'Tag{tt}'), tt) for _, tt in defs]
    print(f"  cid={cid}: {types}")

# Check the specific problematic IDs from debug analysis
print("\n--- Specific problematic charIDs ---")
for cid in [271, 326, 367, 411, 425, 481, 494]:
    defs = definitions.get(cid, [])
    for order_idx, tt in defs:
        print(f"  cid={cid}: tag_order={order_idx}, type={tag_names.get(tt, f'Tag{tt}')} (tt={tt})")
