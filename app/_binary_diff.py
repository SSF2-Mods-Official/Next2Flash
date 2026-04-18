"""Exhaustive binary comparison of EVERYTHING related to charID=1001 and its hierarchy."""
import struct, zlib

def parse_swf(path):
    data = open(path, 'rb').read()
    sig = data[:3]
    if sig == b'CWS':
        data = b'FWS' + data[3:8] + zlib.decompress(data[8:])
    off = 8
    nb = (data[off] >> 3) & 0x1f
    off += ((5 + 4*nb) + 7) // 8
    off += 4
    tags = []
    while off < len(data) - 1:
        rec = struct.unpack_from('<H', data, off)[0]
        tag_type = rec >> 6
        tag_len = rec & 0x3f
        if tag_len == 0x3f:
            tag_len = struct.unpack_from('<I', data, off + 2)[0]
            body_off = off + 6
            off += 6
        else:
            body_off = off + 2
            off += 2
        body = data[body_off:body_off + tag_len]
        tags.append((tag_type, body))
        off += tag_len
    return data, tags

OG = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'
RT = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'

og_data, og_tags = parse_swf(OG)
rt_data, rt_tags = parse_swf(RT)

print("=" * 60)
print("1. SWF HEADERS")
print("=" * 60)
print(f"OG sig={og_data[:3]} ver={og_data[3]} len={struct.unpack_from('<I', og_data, 4)[0]}")
print(f"RT sig={rt_data[:3]} ver={rt_data[3]} len={struct.unpack_from('<I', rt_data, 4)[0]}")

# Compare header RECT
og_nb = (og_data[8] >> 3) & 0x1f
rt_nb = (rt_data[8] >> 3) & 0x1f
og_rect_bytes = ((5 + 4 * og_nb) + 7) // 8
rt_rect_bytes = ((5 + 4 * rt_nb) + 7) // 8
print(f"OG rect: {og_data[8:8+og_rect_bytes].hex()}")
print(f"RT rect: {rt_data[8:8+rt_rect_bytes].hex()}")
og_fps_off = 8 + og_rect_bytes
rt_fps_off = 8 + rt_rect_bytes
print(f"OG fps+frames: {og_data[og_fps_off:og_fps_off+4].hex()}")
print(f"RT fps+frames: {rt_data[rt_fps_off:rt_fps_off+4].hex()}")

print("\n" + "=" * 60)
print("2. charID=1001 LL2 TAG — FULL BINARY COMPARISON")
print("=" * 60)
for label, tags in [('OG', og_tags), ('RT', rt_tags)]:
    for t, b in tags:
        if t == 36:
            cid = struct.unpack_from('<H', b, 0)[0]
            if cid == 1001:
                print(f"\n{label} LL2 tag body ({len(b)} bytes):")
                print(f"  Full hex: {b.hex()}")
                # Decompress
                compressed = b[7:]
                dec = zlib.decompress(compressed)
                print(f"  Compressed: {len(compressed)} bytes → decompressed: {len(dec)} bytes")
                print(f"  Decompressed hex: {dec.hex()}")

# Direct comparison
og_1001 = None
rt_1001 = None
for t, b in og_tags:
    if t == 36 and struct.unpack_from('<H', b, 0)[0] == 1001:
        og_1001 = b
for t, b in rt_tags:
    if t == 36 and struct.unpack_from('<H', b, 0)[0] == 1001:
        rt_1001 = b
if og_1001 and rt_1001:
    print(f"\nLL2 tag body IDENTICAL: {og_1001 == rt_1001}")
    if og_1001 != rt_1001:
        for i in range(min(len(og_1001), len(rt_1001))):
            if og_1001[i] != rt_1001[i]:
                print(f"  First diff at byte {i}: OG=0x{og_1001[i]:02x} RT=0x{rt_1001[i]:02x}")
                break

print("\n" + "=" * 60)
print("3. DefineSprite 1471 (DAir_73) — FULL BINARY COMPARISON")
print("=" * 60)
og_1471 = None
rt_1471 = None
for t, b in og_tags:
    if t == 39 and len(b) >= 2 and struct.unpack_from('<H', b, 0)[0] == 1471:
        og_1471 = b
for t, b in rt_tags:
    if t == 39 and len(b) >= 2 and struct.unpack_from('<H', b, 0)[0] == 1471:
        rt_1471 = b

if og_1471 and rt_1471:
    print(f"OG Sprite 1471: {len(og_1471)} bytes")
    print(f"RT Sprite 1471: {len(rt_1471)} bytes")
    print(f"IDENTICAL: {og_1471 == rt_1471}")
    if og_1471 != rt_1471:
        for i in range(min(len(og_1471), len(rt_1471))):
            if og_1471[i] != rt_1471[i]:
                print(f"  First diff at byte {i}: OG=0x{og_1471[i]:02x} RT=0x{rt_1471[i]:02x}")
                print(f"  OG context: ...{og_1471[max(0,i-8):i+8].hex()}...")
                print(f"  RT context: ...{rt_1471[max(0,i-8):i+8].hex()}...")
                break

print("\n" + "=" * 60)
print("4. DefineSprite 1556 (black_mage) — SIZE COMPARISON")
print("=" * 60)
og_1556 = None
rt_1556 = None
for t, b in og_tags:
    if t == 39 and len(b) >= 2 and struct.unpack_from('<H', b, 0)[0] == 1556:
        og_1556 = b
for t, b in rt_tags:
    if t == 39 and len(b) >= 2 and struct.unpack_from('<H', b, 0)[0] == 1556:
        rt_1556 = b
if og_1556 and rt_1556:
    print(f"OG Sprite 1556: {len(og_1556)} bytes")
    print(f"RT Sprite 1556: {len(rt_1556)} bytes")
    print(f"IDENTICAL: {og_1556 == rt_1556}")

print("\n" + "=" * 60)
print("5. ALL LL2 TAGS — BYTE-IDENTICAL COUNT")
print("=" * 60)
og_ll2 = {}
rt_ll2 = {}
for t, b in og_tags:
    if t == 36 and len(b) >= 2:
        cid = struct.unpack_from('<H', b, 0)[0]
        og_ll2[cid] = b
for t, b in rt_tags:
    if t == 36 and len(b) >= 2:
        cid = struct.unpack_from('<H', b, 0)[0]
        rt_ll2[cid] = b

identical = 0
diff_bodies = []
for cid in sorted(og_ll2):
    if cid in rt_ll2:
        if og_ll2[cid] == rt_ll2[cid]:
            identical += 1
        else:
            diff_bodies.append(cid)
print(f"Byte-identical LL2 tags: {identical} / {len(og_ll2)}")
print(f"Different LL2 tags: {len(diff_bodies)}")
if diff_bodies:
    print(f"  charIDs with different bodies: {diff_bodies[:20]}...")
    # Check if DECODED is the same for the different ones
    decoded_same = 0
    decoded_diff = []
    for cid in diff_bodies:
        og_b = og_ll2[cid]
        rt_b = rt_ll2[cid]
        og_dec = zlib.decompress(og_b[7:])
        rt_dec = zlib.decompress(rt_b[7:])
        if og_dec == rt_dec:
            decoded_same += 1
        else:
            decoded_diff.append((cid, len(og_dec), len(rt_dec)))
    print(f"  Of those, decoded ARGB identical: {decoded_same}")
    print(f"  Decoded ARGB DIFFERENT: {len(decoded_diff)}")
    for cid, ol, rl in decoded_diff[:10]:
        print(f"    charID={cid}: OG decoded={ol} bytes, RT decoded={rl} bytes")
        og_b = og_ll2[cid]
        rt_b = rt_ll2[cid]
        og_fmt = og_b[2]
        rt_fmt = rt_b[2]
        og_w = struct.unpack_from('<H', og_b, 3)[0]
        rt_w = struct.unpack_from('<H', rt_b, 3)[0]
        og_h = struct.unpack_from('<H', og_b, 5)[0]
        rt_h = struct.unpack_from('<H', rt_b, 5)[0]
        print(f"      OG: fmt={og_fmt} {og_w}x{og_h}  RT: fmt={rt_fmt} {rt_w}x{rt_h}")

print("\n" + "=" * 60)
print("6. SymbolClass TAG — BYTE-IDENTICAL CHECK")
print("=" * 60)
og_sym = None
rt_sym = None
for t, b in og_tags:
    if t == 76:
        og_sym = b
for t, b in rt_tags:
    if t == 76:
        rt_sym = b
if og_sym and rt_sym:
    print(f"OG SymbolClass: {len(og_sym)} bytes")
    print(f"RT SymbolClass: {len(rt_sym)} bytes")
    print(f"IDENTICAL: {og_sym == rt_sym}")
    if og_sym != rt_sym:
        for i in range(min(len(og_sym), len(rt_sym))):
            if og_sym[i] != rt_sym[i]:
                print(f"  First diff at byte {i}: OG=0x{og_sym[i]:02x} RT=0x{rt_sym[i]:02x}")
                break

print("\n" + "=" * 60)
print("7. DoABC TAG — BYTE-IDENTICAL CHECK")
print("=" * 60)
og_abc = None
rt_abc = None
for t, b in og_tags:
    if t == 82:
        og_abc = b
for t, b in rt_tags:
    if t == 82:
        rt_abc = b
if og_abc and rt_abc:
    print(f"OG DoABC: {len(og_abc)} bytes")
    print(f"RT DoABC: {len(rt_abc)} bytes")
    print(f"IDENTICAL: {og_abc == rt_abc}")
