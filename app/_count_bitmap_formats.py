"""Count how many OG bitmaps use format 3 (palette) vs format 5 (ARGB)."""
import struct, zlib

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"

with open(OG, "rb") as f:
    raw = f.read()
if raw[:3] == b"CWS":
    raw = raw[:8] + zlib.decompress(raw[8:])

pos = 8
nbits = (raw[pos] >> 3) & 0x1F
total_bits = 5 + nbits * 4
pos += (total_bits + 7) // 8
pos += 4

fmt_counts = {}
fmt3_sizes = []

while pos < len(raw):
    tc = struct.unpack_from("<H", raw, pos)[0]
    tt = tc >> 6
    length = tc & 0x3F
    pos += 2
    if length == 0x3F:
        length = struct.unpack_from("<I", raw, pos)[0]
        pos += 4
    body = raw[pos:pos+length]
    
    if tt == 36:  # DefineBitsLossless2
        cid = struct.unpack_from("<H", body, 0)[0]
        fmt = body[2]
        w = struct.unpack_from("<H", body, 3)[0]
        h = struct.unpack_from("<H", body, 5)[0]
        fmt_counts[fmt] = fmt_counts.get(fmt, 0) + 1
        if fmt == 3:
            ct_size = body[7] + 1
            fmt3_sizes.append((cid, w, h, ct_size))
    
    if tt == 20:  # DefineBitsLossless (no alpha)
        cid = struct.unpack_from("<H", body, 0)[0]
        fmt = body[2]
        w = struct.unpack_from("<H", body, 3)[0]
        h = struct.unpack_from("<H", body, 5)[0]
        fmt_counts[f"LL1_fmt{fmt}"] = fmt_counts.get(f"LL1_fmt{fmt}", 0) + 1
    
    pos += length
    if tt == 0:
        break

print("DefineBitsLossless2 format distribution:")
for fmt, count in sorted(fmt_counts.items()):
    name = {3: "8-bit palette", 4: "15-bit RGB", 5: "32-bit ARGB"}.get(fmt, str(fmt))
    print(f"  Format {fmt} ({name}): {count}")

print(f"\nFormat 3 (palette) bitmaps: {len(fmt3_sizes)}")
if fmt3_sizes:
    print(f"  Samples:")
    for cid, w, h, ct in fmt3_sizes[:10]:
        print(f"    charId={cid} {w}x{h} colors={ct}")
    if len(fmt3_sizes) > 10:
        print(f"  ... and {len(fmt3_sizes) - 10} more")
