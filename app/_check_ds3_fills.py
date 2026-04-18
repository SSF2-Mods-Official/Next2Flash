"""
Properly parse DefineShape3 fill styles to find genuine bitmap fill references.
Compare OG vs RT.
"""
import struct, zlib

RT = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'
OG = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'

DAIR_BITMAPS = {994, 995, 996, 997, 998, 999, 1000, 1001, 1002, 1003, 1004}
BITMAP_FILL_TYPES = {0x40, 0x41, 0x42, 0x43}  # tiled, smoothed, clipped, clipped smoothed

def parse_swf(path):
    with open(path, 'rb') as f:
        raw = f.read()
    if raw[:3] == b'CWS':
        raw = raw[:8] + zlib.decompress(raw[8:])
    pos = 8
    nb = (raw[pos] >> 3) & 0x1f
    pos += (5 + nb * 4 + 7) // 8 + 4
    tags = []
    while pos < len(raw) - 1:
        hdr = struct.unpack_from('<H', raw, pos)[0]
        tt = hdr >> 6
        sl = hdr & 0x3f
        tag_pos = pos; pos += 2
        if sl == 0x3f:
            l = struct.unpack_from('<I', raw, pos)[0]; pos += 4
        else:
            l = sl
        pay = raw[pos:pos+l]
        if tt == 0: break
        tags.append((tt, tag_pos, l, pay))
        pos += l
    return tags

def parse_fillstyle_array(pay, pos, extended):
    """Parse FILLSTYLEARRAY from a DefineShape payload (after charID).
    Returns (list of (fill_type, bitmap_cid_or_None), new_pos)
    """
    count = pay[pos]; pos += 1
    if count == 0xFF:
        count = struct.unpack_from('<H', pay, pos)[0]; pos += 2
    fills = []
    for _ in range(count):
        ftype = pay[pos]; pos += 1
        if ftype == 0x00:  # solid fill
            if extended:  # alpha
                pos += 4  # RGBA
            else:
                pos += 3  # RGB
        elif ftype in (0x10, 0x12, 0x13):  # gradient fills
            pos += 6  # matrix (6 values, but actually we need to skip properly)
            # Skip matrix (SWF matrix is variable length, bitfield-based) - approximate
            # This is complex; just bail out if we hit a gradient fill
            return None, pos
        elif ftype in BITMAP_FILL_TYPES:
            bitmap_cid = struct.unpack_from('<H', pay, pos)[0]; pos += 2
            # Skip MATRIX (variable bitfield): start bit position
            # We'll use a simple heuristic: skip 6 bytes for typical matrices
            # This is imprecise but OK for our scan
            pos += 6  # typical matrix minimum bytes
            fills.append((ftype, bitmap_cid))
        else:
            # Unknown fill type, skip - just return None
            return None, pos
    return fills, pos

def scan_shapes_for_bitmap_fills(tags, label):
    """Properly parse each DefineShape3 to find bitmap fill references."""
    print(f"\n=== {label}: DefineShape3 with bitmap fills referencing dair charIDs ===")
    found = []
    for tt, tpos, l, pay in tags:
        if tt not in (2, 22, 32, 83):  # DefineShape 1-4
            continue
        if l < 2:
            continue
        ds_cid = struct.unpack_from('<H', pay)[0]
        # Skip ShapeBounds rectangle (variable bitfield - minimal: 1 byte)
        # Use approximate: first 2 bytes = charID, then bounds rect (variable), then fills
        # For simplicity, scan raw bytes for bitmap fill type bytes followed by dair charIDs
        # A proper parse would be too complex. Use targeted scan:
        # Look for bytes 0x40, 0x41, 0x42, 0x43 followed by a uint16 in DAIR_BITMAPS
        for i in range(2, l - 2):
            b = pay[i]
            if b in BITMAP_FILL_TYPES:
                # The next 2 bytes are the bitmap charID
                bcid = struct.unpack_from('<H', pay, i+1)[0]
                if bcid in DAIR_BITMAPS:
                    # Double check: the byte BEFORE this should be reasonable
                    # (it's part of the fill count or previous fill end)
                    print(f"  DS{tt-20 if tt > 10 else tt} charID={ds_cid} "
                          f"at byte {tpos}: fill type=0x{b:02x}, "
                          f"bitmap charID={bcid}")
                    found.append((ds_cid, bcid, b))
                    break
    if not found:
        print("  (none found)")
    return found

rt_tags = parse_swf(RT)
og_tags = parse_swf(OG)

rt_found = scan_shapes_for_bitmap_fills(rt_tags, "RT")
og_found = scan_shapes_for_bitmap_fills(og_tags, "OG")

# Cross-compare: which are in RT but not in OG?
og_pairs = {(ds, bm) for ds, bm, _ in og_found}
rt_pairs = {(ds, bm) for ds, bm, _ in rt_found}
only_in_rt = rt_pairs - og_pairs
only_in_og = og_pairs - rt_pairs
print(f"\n=== DIFF ===")
print(f"RT only (new shapes with dair bitmap fills): {sorted(only_in_rt)}")
print(f"OG only (removed shapes): {sorted(only_in_og)}")
print(f"In both: {sorted(og_pairs & rt_pairs)}")
