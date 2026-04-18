"""
Compare pixel data of stance-layer bitmaps between OG and RT blackmage.ssf.

For format-5 bitmaps (32-bit premultiplied ARGB), the roundtrip should be
pixel-identical IF all pixels have alpha=255 (fully opaque).

This script cross-references OG and RT bitmaps by position in the stance
sprite (same depth/frame placement), decodes both, and compares pixels.
"""
import struct, zlib, sys, hashlib
sys.path.insert(0, '.')

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"

def read_swf(path):
    d = open(path, 'rb').read()
    if d[:3] == b'CWS': d = b'FWS' + d[3:8] + zlib.decompress(d[8:])
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
        if ln == 0x3F: ln = struct.unpack_from('<I', d, offset)[0]; offset += 4
        tags.append((tt, d[offset:offset+ln])); offset += ln
        if tt == 0: break
    return tags

def build_inventory(tags):
    bitmaps = {}  # charId -> (tag_type, raw_body)
    sprites = {}  # charId -> [(placed_cid, depth, frame), ...]
    sym_class = {}
    for tt, d in tags:
        if tt in (35, 36, 20) and len(d) >= 2:
            cid = struct.unpack_from('<H', d, 0)[0]
            bitmaps[cid] = (tt, d)
        elif tt == 39 and len(d) >= 4:
            cid = struct.unpack_from('<H', d, 0)[0]
            inner = parse_tags(d, 4, len(d))
            plc = []; frame = 0
            for itt, id_ in inner:
                if itt == 1: frame += 1
                elif itt == 26 and len(id_) >= 5 and (id_[0] & 0x02):
                    plc.append((struct.unpack_from('<H', id_, 3)[0],
                                struct.unpack_from('<H', id_, 1)[0], frame))
                elif itt == 70 and len(id_) >= 6 and (id_[0] & 0x02):
                    plc.append((struct.unpack_from('<H', id_, 4)[0],
                                struct.unpack_from('<H', id_, 2)[0], frame))
            sprites[cid] = plc
        elif tt == 76:
            num = struct.unpack_from('<H', d, 0)[0]; off = 2
            for _ in range(num):
                c = struct.unpack_from('<H', d, off)[0]; off += 2
                ne = d.index(b'\x00', off); sym_class[d[off:ne].decode('utf-8','replace')] = c
                off = ne + 1
    return bitmaps, sprites, sym_class

def decode_ll2_pixels(d):
    """Decode DefineBitsLossless2 body -> raw premultiplied ARGB bytes."""
    if len(d) < 7: return None, 0, 0, 0
    cid = struct.unpack_from('<H', d, 0)[0]
    fmt = d[2]
    w = struct.unpack_from('<H', d, 3)[0]
    h = struct.unpack_from('<H', d, 5)[0]
    raw = zlib.decompress(d[7:])
    return raw, cid, w, h, fmt

def pixel_md5(raw):
    return hashlib.md5(raw).hexdigest()[:12]

og_data = read_swf(OG)
rt_data = read_swf(RT)

og_bitmaps, og_sprites, og_sym = build_inventory(parse_tags(og_data))
rt_bitmaps, rt_sprites, rt_sym = build_inventory(parse_tags(rt_data))

og_main = og_sym.get('black_mage')
rt_main = rt_sym.get('black_mage')
print(f"OG main cid: {og_main}, RT main cid: {rt_main}")

# Get all (depth1_sprite_cid, depth, frame) → bitmap_cid mappings
# Key: (depth1_slot_placement_frame, depth2_depth, depth2_frame) → bitmap content

# Build a structural map: for each stance animation frame sequence, get the bitmap sequence
def get_depth2_bitmap_sequence(main_cid, sprites, bitmaps, label):
    # Returns list of (depth1_cid, depth2_cid) pairs
    seq = []
    if main_cid not in sprites:
        print(f"  [{label}] main cid not in sprites")
        return seq
    d0_placements = sprites[main_cid]
    # Get unique depth1 sprite cids
    d1_cids = sorted({cid for (cid, depth, frame) in d0_placements if cid in sprites})
    for d1_cid in d1_cids:
        for (cid2, depth2, frame2) in sprites[d1_cid]:
            if cid2 in bitmaps:
                seq.append((d1_cid, cid2))
    return seq

og_seq = get_depth2_bitmap_sequence(og_main, og_sprites, og_bitmaps, "OG")
rt_seq = get_depth2_bitmap_sequence(rt_main, rt_sprites, rt_bitmaps, "RT")

print(f"\nOG stance bitmap placements: {len(og_seq)}")
print(f"RT stance bitmap placements: {len(rt_seq)}")

# The OG and RT charIds differ (different compilation), so we can't match by charId.
# Instead, match by (depth1 sprite position, bitmap position within that sprite).
# Build: d1_cid (by index in sorted order) -> [(d2_cid, ...)]

def build_d1_map(seq):
    d = {}
    for d1_cid, d2_cid in seq:
        d.setdefault(d1_cid, []).append(d2_cid)
    return d

og_map = build_d1_map(og_seq)
rt_map = build_d1_map(rt_seq)

# Align depth-1 sprites by SymbolClass name instead of sorted charId order
# Build reverse SymbolClass: charId -> name
og_cid_to_name = {v: k for k, v in og_sym.items()}
rt_cid_to_name = {v: k for k, v in rt_sym.items()}
rt_name_to_cid = rt_sym  # name -> charId

og_d1_sorted = sorted(og_map.keys())
rt_d1_sorted = sorted(rt_map.keys())

print(f"\nOG depth1 sprites: {len(og_d1_sorted)}")
print(f"RT depth1 sprites: {len(rt_d1_sorted)}")

# Compare bitmaps by matched SymbolClass name
total = 0; identical = 0; different = 0; partial_alpha = 0; unmatched = 0
sample_diffs = []

for og_d1 in og_d1_sorted:
    name = og_cid_to_name.get(og_d1)
    if name is None:
        unmatched += 1
        continue
    rt_d1 = rt_name_to_cid.get(name)
    if rt_d1 is None or rt_d1 not in rt_map:
        unmatched += 1
        continue

    og_bmp_list = og_map[og_d1]
    rt_bmp_list = rt_map[rt_d1]
    if len(og_bmp_list) != len(rt_bmp_list):
        continue

    for j, (og_bcid, rt_bcid) in enumerate(zip(og_bmp_list, rt_bmp_list)):
        og_tt, og_bd = og_bitmaps[og_bcid]
        rt_tt, rt_bd = rt_bitmaps[rt_bcid]
        total += 1

        if og_tt != 36:
            continue  # only compare LL2

        # Decode OG
        og_raw, _, og_w, og_h, og_fmt = decode_ll2_pixels(og_bd)
        rt_raw, _, rt_w, rt_h, rt_fmt = decode_ll2_pixels(rt_bd)

        if og_w != rt_w or og_h != rt_h:
            different += 1
            if len(sample_diffs) < 3:
                sample_diffs.append(f"  [{name}] dim mismatch: OG cid={og_bcid} {og_w}x{og_h} vs RT cid={rt_bcid} {rt_w}x{rt_h}")
            continue

        if og_fmt == 5 and rt_fmt == 5:
            if og_raw == rt_raw:
                identical += 1
            else:
                different += 1
                if len(sample_diffs) < 5:
                    nb = sum(a != b for a, b in zip(og_raw, rt_raw))
                    has_partial = any(og_raw[i] < 254 for i in range(0, min(len(og_raw), 4096), 4))
                    if has_partial:
                        partial_alpha += 1
                    sample_diffs.append(
                        f"  [{name}] OG cid={og_bcid} {og_w}x{og_h}: "
                        f"{nb}/{len(og_raw)} bytes differ, partial_alpha={has_partial}"
                    )

print(f"\n=== Pixel comparison (format-5 vs format-5, SymbolClass-aligned) ===")
print(f"  Total compared: {total}")
print(f"  Pixel-identical: {identical}")
print(f"  Different:       {different}")
print(f"  Unmatched sprites: {unmatched}")
print(f"  With partial alpha (A<255): {partial_alpha}")
if sample_diffs:
    print("\n  Sample diffs:")
    for s in sample_diffs:
        print(s)
if identical == total and total > 0:
    print("\n  All stance bitmaps pixel-IDENTICAL in OG vs RT.")
    print("  --> Palette swap should work IF the AS3 code sees them.")
elif different > 0:
    print(f"\n  {different} stance bitmaps have different pixels.")
    print("  --> These would cause threshold('==') misses for changed pixels.")
