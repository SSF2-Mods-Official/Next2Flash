"""
H3: Compare bitmap fill type bytes (smooth/clipped flags) in DefineShape3
between OG and RT blackmage.ssf.

SWF fill types:
  0x40 = repeating + smooth
  0x41 = clipped + smooth      <- bilinear filtering (blurry on pixel art)
  0x42 = repeating + non-smooth
  0x43 = clipped + non-smooth  <- pixel-perfect (expected for character art)
"""
import struct, zlib, sys
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

def parse_shape_fills(d, tag_type):
    """
    Returns list of (fill_type_byte, bitmap_charId) for all bitmap fills in shape.
    """
    if len(d) < 4: return [], struct.unpack_from('<H', d, 0)[0] if len(d) >= 2 else 0
    cid = struct.unpack_from('<H', d, 0)[0]

    bit_off = 16  # skip cid
    rect_bits = parse_rect_bits(d, bit_off)
    byte_off = (bit_off + rect_bits + 7) // 8

    if tag_type == 83:  # DefineShape4
        if byte_off >= len(d): return [], cid
        nb2 = d[byte_off] >> 3
        byte_off += (5 + nb2 * 4 + 7) // 8
        byte_off += 1  # flags

    if byte_off >= len(d): return [], cid

    fill_count = d[byte_off]; byte_off += 1
    if fill_count == 0xFF:
        if byte_off + 1 >= len(d): return [], cid
        fill_count = struct.unpack_from('<H', d, byte_off)[0]; byte_off += 2

    bitmap_fills = []
    for _ in range(fill_count):
        if byte_off >= len(d): break
        fill_type = d[byte_off]; byte_off += 1

        if fill_type == 0x00:
            byte_off += 4 if tag_type in (32, 83) else 3  # RGBA or RGB
        elif fill_type in (0x10, 0x12, 0x13, 0x14):
            # Gradient fill — variable length, too complex to skip perfectly
            break
        elif fill_type in (0x40, 0x41, 0x42, 0x43):
            if byte_off + 1 < len(d):
                bmp_cid = struct.unpack_from('<H', d, byte_off)[0]
                bitmap_fills.append((fill_type, bmp_cid))
            break  # rough parse — stop after first bitmap fill
        else:
            break

    return bitmap_fills, cid

def collect_shape_fills(swf_data):
    """Returns {shape_charId: [(fill_type, bitmap_cid), ...]} for all shapes."""
    result = {}
    for tt, d in parse_tags(swf_data):
        if tt in (2, 22, 32, 83):
            fills, cid = parse_shape_fills(d, tt)
            if fills:
                result[cid] = fills
    return result

def collect_sym_class(swf_data):
    sym = {}
    for tt, d in parse_tags(swf_data):
        if tt == 76:
            num = struct.unpack_from('<H', d, 0)[0]; off = 2
            for _ in range(num):
                c = struct.unpack_from('<H', d, off)[0]; off += 2
                ne = d.index(b'\x00', off)
                sym[d[off:ne].decode('utf-8','replace')] = c
                off = ne + 1
    return sym

og_data = read_swf(OG)
rt_data = read_swf(RT)

og_fills = collect_shape_fills(og_data)
rt_fills = collect_shape_fills(rt_data)
og_sym = collect_sym_class(og_data)
rt_sym = collect_sym_class(rt_data)

rt_cid_to_name = {v: k for k, v in rt_sym.items()}
og_name_to_cid = og_sym  # name -> charId

print(f"OG shapes with bitmap fills: {len(og_fills)}")
print(f"RT shapes with bitmap fills: {len(rt_fills)}")

# Summarize fill type distribution
from collections import Counter
og_fill_dist = Counter()
rt_fill_dist = Counter()

for cid, fills in og_fills.items():
    for ft, _ in fills:
        og_fill_dist[ft] += 1
for cid, fills in rt_fills.items():
    for ft, _ in fills:
        rt_fill_dist[ft] += 1

fill_names = {
    0x40: 'repeating+smooth',
    0x41: 'clipped+smooth',
    0x42: 'repeating+NON-smooth',
    0x43: 'clipped+NON-smooth'
}
print("\n=== Fill Type Distribution ===")
for ft in (0x40, 0x41, 0x42, 0x43):
    og_c = og_fill_dist.get(ft, 0)
    rt_c = rt_fill_dist.get(ft, 0)
    match = '✓' if og_c == rt_c else '✗ MISMATCH'
    print(f"  0x{ft:02X} ({fill_names[ft]:30s}): OG={og_c:5d}  RT={rt_c:5d}  {match}")

# Per-shape comparison for shapes that appear in SymbolClass (named shapes)
# These are the most visible ones
print("\n=== Named shapes with fill type differences ===")
mismatches = 0
for rt_cid, fills in rt_fills.items():
    name = rt_cid_to_name.get(rt_cid)
    if name is None:
        continue
    og_cid = og_name_to_cid.get(name)
    if og_cid is None:
        continue
    og_shape_fills = og_fills.get(og_cid, [])
    if not og_shape_fills:
        continue
    # Compare first fill type
    for i, (rt_ft, _) in enumerate(fills):
        if i < len(og_shape_fills):
            og_ft, _ = og_shape_fills[i]
            if og_ft != rt_ft:
                print(f"  MISMATCH [{name}]  OG=0x{og_ft:02X} ({fill_names.get(og_ft,'?')})  "
                      f"RT=0x{rt_ft:02X} ({fill_names.get(rt_ft,'?')})")
                mismatches += 1

if mismatches == 0:
    print("  No mismatches in named shapes.")

# Summary: are any shapes smooth in RT that were non-smooth in OG?
smooth_in_rt_not_og = 0
for rt_cid, fills in rt_fills.items():
    name = rt_cid_to_name.get(rt_cid)
    if name is None: continue
    og_cid = og_name_to_cid.get(name)
    if og_cid is None: continue
    og_shape_fills = og_fills.get(og_cid, [])
    for i, (rt_ft, _) in enumerate(fills):
        rt_smooth = rt_ft in (0x40, 0x41)
        if i < len(og_shape_fills):
            og_ft, _ = og_shape_fills[i]
            og_smooth = og_ft in (0x40, 0x41)
            if rt_smooth and not og_smooth:
                smooth_in_rt_not_og += 1

print(f"\nShapes that are smooth in RT but non-smooth in OG: {smooth_in_rt_not_og}")
if smooth_in_rt_not_og > 0:
    print("  --> H3 CONFIRMED: RT renders these bitmaps blurry, OG was pixel-perfect.")
else:
    print("  --> H3 RULED OUT: No smoothing mismatch in named shapes.")
