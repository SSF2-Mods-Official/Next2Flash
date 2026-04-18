import struct, zlib
from collections import Counter

def parse_all_tags(path):
    data = open(path,'rb').read()
    sig = data[:3]
    if sig == b'CWS':
        data = b'FWS' + data[3:8] + zlib.decompress(data[8:])
    off = 8
    nb = (data[off] >> 3) & 0x1f
    off += ((5 + 4*nb) + 7) // 8
    off += 4
    tags = []
    while off < len(data)-1:
        rec = struct.unpack_from('<H', data, off)[0]
        tag_type = rec >> 6
        tag_len = rec & 0x3f
        if tag_len == 0x3f:
            tag_len = struct.unpack_from('<I', data, off+2)[0]
            body_off = off + 6
            off += 6
        else:
            body_off = off + 2
            off += 2
        body = data[body_off:body_off+tag_len]
        tags.append((tag_type, body))
        off += tag_len
    return tags

# Definition tags: types that register a new charID
DEF_TYPES = {2, 4, 6, 7, 10, 11, 13, 14, 20, 21, 22, 26, 32, 33, 35, 36, 37, 39, 46, 75, 78, 83, 84, 87, 88, 90}
# Types that DON'T have charID as first field
NO_CHARID_FIRST = {26, 4}  # PlaceObject2, PlaceObject

og_p = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'
rt_swf = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'

for label, path in [('OG', og_p), ('RT', rt_swf)]:
    tags = parse_all_tags(path)
    charId_defs = Counter()  # charID -> count of definitions
    for t, b in tags:
        if t in DEF_TYPES and t not in NO_CHARID_FIRST and len(b) >= 2:
            cid = struct.unpack_from('<H', b, 0)[0]
            charId_defs[cid] += 1
    
    dups = [(cid, cnt) for cid, cnt in charId_defs.items() if cnt > 1]
    print(f'{label}: {len(charId_defs)} unique charIDs defined, {len(dups)} duplicates')
    if dups:
        print(f'  Duplicate charIDs: {sorted(dups)[:20]}')
    
    # Check specifically charID=1001
    cid_1001 = charId_defs.get(1001, 0)
    print(f'  charID=1001 defined {cid_1001} time(s)')

# Also check: are there any bitmaps with small dimensions (<=8x8) that might have pool issues?
print("\n=== Small LL2 bitmaps (w<=8 or h<=8) in OG vs RT ===")
for label, path in [('OG', og_p), ('RT', rt_swf)]:
    tags = parse_all_tags(path)
    small = []
    for t, b in tags:
        if t == 36 and len(b) >= 7:
            cid = struct.unpack_from('<H', b, 0)[0]
            w = struct.unpack_from('<H', b, 3)[0]
            h = struct.unpack_from('<H', b, 5)[0]
            if w <= 8 or h <= 8:
                small.append((cid, w, h))
    print(f'{label}: {len(small)} LL2 bitmaps with w<=8 or h<=8:')
    for cid, w, h in sorted(small)[:20]:
        print(f'  charID={cid} {w}x{h}')
