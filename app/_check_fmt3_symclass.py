"""Check whether OG format=3 bitmaps overlap with SymbolClass-linked BitmapData subclasses."""
import struct, zlib

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

og_p = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'
rt_p = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'

og_tags = parse_all_tags(og_p)
rt_tags = parse_all_tags(rt_p)

# Get SymbolClass entries from OG
symclass_map = {}  # charID -> name
for t, b in og_tags:
    if t == 76:  # SymbolClass
        count = struct.unpack_from('<H', b, 0)[0]
        off = 2
        for _ in range(count):
            cid = struct.unpack_from('<H', b, off)[0]
            off += 2
            null_pos = b.find(b'\x00', off)
            name = b[off:null_pos].decode('utf-8', errors='replace')
            off = null_pos + 1
            symclass_map[cid] = name

bm_linked = set(cid for cid, name in symclass_map.items() if name.startswith('bm_'))
print(f"Total SymbolClass entries: {len(symclass_map)}")
print(f"bm_* linked charIDs: {len(bm_linked)}")

# Get format of each LL2 bitmap in OG
og_fmt3_cids = set()
og_fmt5_cids = set()
for t, b in og_tags:
    if t == 36 and len(b) >= 3:
        cid = struct.unpack_from('<H', b, 0)[0]
        fmt = b[2]
        if fmt == 3:
            og_fmt3_cids.add(cid)
        elif fmt == 5:
            og_fmt5_cids.add(cid)

# Check overlap
fmt3_with_symclass = og_fmt3_cids & bm_linked
fmt3_without_symclass = og_fmt3_cids - bm_linked
fmt5_with_symclass = og_fmt5_cids & bm_linked
fmt5_without_symclass = og_fmt5_cids - bm_linked

print(f"\nOG format=3 LL2 bitmaps: {len(og_fmt3_cids)}")
print(f"  WITH bm_* SymbolClass link: {len(fmt3_with_symclass)}")
print(f"  WITHOUT bm_* SymbolClass link: {len(fmt3_without_symclass)}")
print(f"\nOG format=5 LL2 bitmaps: {len(og_fmt5_cids)}")
print(f"  WITH bm_* SymbolClass link: {len(fmt5_with_symclass)}")
print(f"  WITHOUT bm_* SymbolClass link: {len(fmt5_without_symclass)}")

if fmt3_with_symclass:
    print(f"\n!! format=3 + bm_* link charIDs (sample): {sorted(fmt3_with_symclass)[:10]}")
    for cid in sorted(fmt3_with_symclass)[:5]:
        print(f"  charID={cid} -> {symclass_map[cid]}")

# Now check RT
print("\n=== RT format check ===")
rt_fmt3_cids = set()
rt_fmt5_cids = set()
for t, b in rt_tags:
    if t == 36 and len(b) >= 3:
        cid = struct.unpack_from('<H', b, 0)[0]
        fmt = b[2]
        if fmt == 3:
            rt_fmt3_cids.add(cid)
        elif fmt == 5:
            rt_fmt5_cids.add(cid)

rt_fmt3_linked = rt_fmt3_cids & bm_linked
rt_fmt5_linked = rt_fmt5_cids & bm_linked
print(f"RT format=3: {len(rt_fmt3_cids)} ({len(rt_fmt3_linked)} bm_*-linked)")
print(f"RT format=5: {len(rt_fmt5_cids)} ({len(rt_fmt5_linked)} bm_*-linked)")

# How many bm_*-linked bitmaps changed format between OG and RT?
switched = (og_fmt5_cids & bm_linked) & rt_fmt3_cids
print(f"\nbm_*-linked bitmaps switched from OG format=5 to RT format=3: {len(switched)}")
if switched:
    print(f"  Sample: {sorted(switched)[:10]}")
    for cid in sorted(switched)[:5]:
        print(f"  charID={cid} -> {symclass_map[cid]}")
