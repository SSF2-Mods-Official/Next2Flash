"""
Scan ALL sprite bodies in both RT and OG for PO3+HasImage placements referencing non-LL2 charIDs.
This catches any HasImage placement pointing to a DefineShape or DefineSprite (invalid).
"""
import struct, zlib

RT = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'
OG = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'

def parse_swf_full(path):
    with open(path, 'rb') as f:
        raw = f.read()
    if raw[:3] == b'CWS':
        raw = raw[:8] + zlib.decompress(raw[8:])
    pos = 8
    nb = (raw[pos] >> 3) & 0x1f
    pos += (5 + nb * 4 + 7) // 8 + 4

    ll2_cids = set()
    sprites = {}  # cid -> payload bytes

    while pos < len(raw) - 1:
        hdr = struct.unpack_from('<H', raw, pos)[0]
        tt = hdr >> 6; sl = hdr & 0x3f; pos += 2
        if sl == 0x3f:
            l = struct.unpack_from('<I', raw, pos)[0]; pos += 4
        else:
            l = sl
        pay = raw[pos:pos+l]
        if tt == 0: break
        if tt == 36 and l >= 2:
            ll2_cids.add(struct.unpack_from('<H', pay)[0])
        elif tt == 39 and l >= 4:
            cid = struct.unpack_from('<H', pay)[0]
            sprites[cid] = pay
        pos += l
    return ll2_cids, sprites

def scan_sprite_for_hasimage(sprite_cid, pay, ll2_cids, issues):
    """Scan a sprite's inner tags for PO3+HasImage with non-LL2 charID."""
    sp_pos = 4  # skip charID + frameCount
    while sp_pos < len(pay) - 1:
        hdr = struct.unpack_from('<H', pay, sp_pos)[0]
        st = hdr >> 6; ssl = hdr & 0x3f; sp_pos += 2
        if ssl == 0x3f:
            sl2 = struct.unpack_from('<I', pay, sp_pos)[0]; sp_pos += 4
        else:
            sl2 = ssl
        spay = pay[sp_pos:sp_pos+sl2]
        if st == 0: break
        if st == 70 and sl2 >= 6:  # PO3
            flags = struct.unpack_from('<H', spay)[0]
            depth = struct.unpack_from('<H', spay, 2)[0]
            has_char = (flags >> 1) & 1
            has_image = (flags >> 12) & 1
            if has_image and has_char:
                cid = struct.unpack_from('<H', spay, 4)[0]
                if cid not in ll2_cids:
                    issues.append((sprite_cid, depth, cid))
        sp_pos += sl2

for swf_path, label in [(RT, "RT"), (OG, "OG")]:
    ll2_cids, sprites = parse_swf_full(swf_path)
    print(f"\n=== {label}: PO3+HasImage pointing to non-LL2 charIDs ===")
    issues = []
    for sid, pay in sprites.items():
        scan_sprite_for_hasimage(sid, pay, ll2_cids, issues)
    if issues:
        for sprite_cid, depth, cid in sorted(set(issues)):
            print(f"  Sprite {sprite_cid}: depth={depth} -> charID={cid} (non-LL2!) HAS_IMAGE=True")
    else:
        print("  None found (all HasImage placements reference LL2 charIDs)")

print("\n\nDone.")
