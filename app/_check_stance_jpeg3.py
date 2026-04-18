"""
Check which of the 728 stance-layer bitmaps (at depth-2 in the black_mage sprite)
were originally DefineBitsJPEG3 (tag 35) in the OG.

JPEG3 bitmaps are decoded via PIL JPEG → RGBA and then re-encoded as DefineBitsLossless2.
JPEG artifacts mean the pixel values in the RT may differ from OG, causing threshold("==") to miss.
"""
import struct, zlib, sys
sys.path.insert(0, '.')

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"

def read_swf(path):
    with open(path, 'rb') as f:
        d = f.read()
    if d[:3] == b'CWS':
        d = b'FWS' + d[3:8] + zlib.decompress(d[8:])
    return d

def parse_rect_bits(d, bit_off=0):
    byte_i = bit_off // 8; bit_i = bit_off % 8
    nb = 0
    for i in range(5):
        nb = (nb << 1) | ((d[byte_i + (bit_i + i)//8] >> (7 - (bit_i + i) % 8)) & 1)
    return 5 + nb * 4

def skip_header(d):
    return 8 + (parse_rect_bits(d, 64) + 7) // 8 + 4

def parse_tags(d, offset=None, end=None):
    if offset is None: offset = skip_header(d)
    if end is None: end = len(d)
    tags = []
    while offset < end:
        if offset + 2 > end: break
        hdr = struct.unpack_from('<H', d, offset)[0]
        tt = hdr >> 6; ln = hdr & 0x3F; offset += 2
        if ln == 0x3F:
            ln = struct.unpack_from('<I', d, offset)[0]; offset += 4
        tags.append((tt, d[offset:offset+ln]))
        offset += ln
        if tt == 0: break
    return tags

def build_inventory(tags):
    """Map charId -> tag type for bitmaps, charId -> placements for sprites."""
    bitmaps = {}   # charId -> tag_type_int
    sprites = {}   # charId -> [(placed_cid, frame), ...]
    sym_class = {}

    for tt, d in tags:
        if tt in (35, 36, 20):
            cid = struct.unpack_from('<H', d, 0)[0]
            bitmaps[cid] = tt
        elif tt == 39:
            cid = struct.unpack_from('<H', d, 0)[0]
            inner = parse_tags(d, offset=4, end=len(d))
            placements = []
            frame = 0
            for itt, id_ in inner:
                if itt == 1: frame += 1
                elif itt == 26:  # PlaceObject2: flags(1) + depth(2) + charId?(2)
                    flags = id_[0]
                    has_char = bool(flags & 0x02)
                    if has_char and len(id_) >= 5:
                        cid2 = struct.unpack_from('<H', id_, 3)[0]
                        placements.append(cid2)
                elif itt == 70:  # PlaceObject3: flags1(1)+flags2(1)+depth(2)+charId?(2)
                    flags1 = id_[0]
                    has_char = bool(flags1 & 0x02)
                    if has_char and len(id_) >= 6:
                        cid2 = struct.unpack_from('<H', id_, 4)[0]
                        placements.append(cid2)
            sprites[cid] = placements
        elif tt == 76:
            num = struct.unpack_from('<H', d, 0)[0]; off = 2
            for _ in range(num):
                c = struct.unpack_from('<H', d, off)[0]; off += 2
                ne = d.index(b'\x00', off)
                sym_class[d[off:ne].decode('utf-8','replace')] = c
                off = ne + 1

    return bitmaps, sprites, sym_class

og_data = read_swf(OG)
og_tags = parse_tags(og_data)
bitmaps, sprites, sym_class = build_inventory(og_tags)

# Find main sprite
main_cid = sym_class.get('black_mage')
print(f"Main sprite cid: {main_cid}  (black_mage)")

# Walk depth0 -> depth1 -> depth2 to get all stance-layer bitmap charIds
depth0_cids = set(sprites.get(main_cid, []))
depth2_bitmap_cids = set()
depth2_sprite_cids = set()
for sp_cid in depth0_cids:
    if sp_cid in sprites:
        for cid2 in sprites[sp_cid]:
            if cid2 in bitmaps:
                depth2_bitmap_cids.add(cid2)
            elif cid2 in sprites:
                depth2_sprite_cids.add(cid2)

print(f"\nDepth-2 bitmap charIds (stance layer): {len(depth2_bitmap_cids)}")

# Separate by tag type
jpeg3_ids = [cid for cid in depth2_bitmap_cids if bitmaps[cid] == 35]
ll2_ids   = [cid for cid in depth2_bitmap_cids if bitmaps[cid] == 36]
ll1_ids   = [cid for cid in depth2_bitmap_cids if bitmaps[cid] == 20]

print(f"  DefineBitsLossless2 (tag 36): {len(ll2_ids)}")
print(f"  DefineBitsJPEG3     (tag 35): {len(jpeg3_ids)}")
print(f"  DefineBitsLossless  (tag 20): {len(ll1_ids)}")

if jpeg3_ids:
    print(f"\n  JPEG3 bitmap charIds in stance sprites: {sorted(jpeg3_ids)}")
    print("\n  --> These bitmaps undergo JPEG decode -> Lossless2 re-encode in RT.")
    print("  --> If any palette-swap colors come from these bitmaps, threshold('==') will MISS.")
else:
    print("\n  No JPEG3 bitmaps in stance sprites. JPEG3->Lossless2 is NOT the palette-swap problem.")

# Also show the LL2 format breakdown (format-3 vs format-5)
print("\n=== Format breakdown of depth-2 LL2 bitmaps ===")
fmt3_count = 0; fmt5_count = 0
for tt, d in og_tags:
    if tt == 36 and len(d) >= 4:
        cid = struct.unpack_from('<H', d, 0)[0]
        if cid in ll2_ids:
            fmt = d[2]
            if fmt == 3: fmt3_count += 1
            elif fmt == 5: fmt5_count += 1

print(f"  Format-3 (palette/colormapped): {fmt3_count}")
print(f"  Format-5 (32-bit ARGB direct):  {fmt5_count}")
if fmt3_count:
    print("\n  --> Format-3 bitmaps are decoded to RGBA (palette index lookup) then re-encoded")
    print("      as format-5. If the premultiply step introduces rounding, threshold may miss.")
