"""
Compare the raw (compressed) LL2 bytes for charID=1001 between OG and RT.
Also scan the main timeline (not DefineSprites) for any HasImage placements.
Also check whether ALL PO3+HasImage placements reference only LL2 charIDs in RT.
"""
import struct, zlib

RT = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'
OG = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'

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
        tag_pos = pos
        pos += 2
        if sl == 0x3f:
            l = struct.unpack_from('<I', raw, pos)[0]; pos += 4
        else:
            l = sl
        pay = raw[pos:pos+l]
        if tt == 0: break
        tags.append((tt, tag_pos, l, pay))
        pos += l
    return tags

print("=== Compare raw LL2 tag for charID=1001 ===")
for path, label in [(RT, "RT"), (OG, "OG")]:
    tags = parse_swf(path)
    for tt, tpos, l, pay in tags:
        if tt == 36 and l >= 2 and struct.unpack_from('<H', pay)[0] == 1001:
            print(f"{label}: tag at byte {tpos}, payload {l} bytes: {pay[:20].hex()}...")
            print(f"  format={pay[2]}, w={struct.unpack_from('<H', pay, 3)[0]}, h={struct.unpack_from('<H', pay, 5)[0]}")
            print(f"  zlib bytes ({len(pay[7:])}): {pay[7:].hex()}")
            break

print("\n\n=== RT: Main timeline HasImage PO3 placements (NOT inside DefineSprites) ===")
rt_tags = parse_swf(RT)
# Collect known LL2 charIDs in RT
rt_ll2_cids = set()
rt_sprite_cids = set()
for tt, tpos, l, pay in rt_tags:
    if tt == 36 and l >= 2:
        rt_ll2_cids.add(struct.unpack_from('<H', pay)[0])
    elif tt == 39 and l >= 2:
        rt_sprite_cids.add(struct.unpack_from('<H', pay)[0])

print(f"RT has {len(rt_ll2_cids)} unique LL2 charIDs and {len(rt_sprite_cids)} sprite charIDs")

main_timeline_hasimage = []
for tt, tpos, l, pay in rt_tags:
    if tt == 70 and l >= 6:  # PO3
        flags = struct.unpack_from('<H', pay)[0]
        depth = struct.unpack_from('<H', pay, 2)[0]
        has_char = (flags >> 1) & 1
        has_image = (flags >> 12) & 1
        if has_image and has_char:
            cid = struct.unpack_from('<H', pay, 4)[0]
            cid_type = 'LL2' if cid in rt_ll2_cids else ('Sprite' if cid in rt_sprite_cids else 'Unknown')
            if cid_type != 'LL2':
                print(f"  PO3 at byte {tpos}: depth={depth}, charID={cid} ({cid_type}), HasImage=True -- NON-LL2 WITH HASIMAGE!")
                main_timeline_hasimage.append((tpos, depth, cid, cid_type))

if not main_timeline_hasimage:
    print("  ALL PO3+HasImage placements reference LL2 charIDs (correct)" )
else:
    print(f"\n  WARNING: {len(main_timeline_hasimage)} non-LL2 PO3+HasImage placements found!")

# Check if any DS3 in RT references charID=1001 as a bitmap fill
print("\n\n=== RT: Any DS3 shape with bitmap fill referencing dair charIDs? ===")
from io import BytesIO

def read_ui8(data, pos): return data[pos], pos+1
def read_ui16(data, pos): return struct.unpack_from('<H', data, pos)[0], pos+2
def read_si16(data, pos): return struct.unpack_from('<h', data, pos)[0], pos+2

DAIR_BITMAPS = {994, 995, 996, 997, 998, 999, 1000, 1001, 1002, 1003, 1004}

for tt, tpos, l, pay in rt_tags:
    if tt == 32 and l >= 2:  # DefineShape3
        ds3_cid = struct.unpack_from('<H', pay)[0]
        # Quick scan for any DAIR charID appearing in the payload
        for i in range(2, l - 1):
            val = struct.unpack_from('<H', pay, i)[0]
            if val in DAIR_BITMAPS:
                print(f"  DS3 charID={ds3_cid} at byte {tpos} may reference dair charID={val}!")
                break
