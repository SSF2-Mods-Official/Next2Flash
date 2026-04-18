"""Check for duplicate charIDs in RT SWF — particularly if any DS3 shape uses the same charID as a bitmap."""
import struct, zlib

RT = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'
OG = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'

DAIR_BITMAPS = {994, 995, 996, 997, 998, 999, 1000, 1001, 1002, 1003, 1004, 1199, 1243, 1244, 1245, 1246}
TAG_NAMES = {2: 'DefineShape', 22: 'DefineShape2', 32: 'DefineShape3', 83: 'DefineShape4',
             20: 'DefineBitsLossless', 36: 'DefineBitsLossless2',
             6: 'DefineBitsJPEG', 21: 'DefineBitsJPEG2', 35: 'DefineBitsJPEG3',
             39: 'DefineSprite', 7: 'DefineButton', 26: 'DefineButton2',
             4: 'PlaceObject', 26: 'PlaceObject2', 70: 'PlaceObject3'}

TARGET_TAGS = {2, 22, 32, 83, 20, 36, 39}  # Tags that define characters with a charID

def analyze_swf(path, label):
    with open(path, 'rb') as f:
        raw = f.read()
    if raw[:3] == b'CWS':
        raw = raw[:8] + zlib.decompress(raw[8:])
    pos = 8
    nb = (raw[pos] >> 3) & 0x1f
    pos += (5 + nb * 4 + 7) // 8 + 4

    by_cid = {}  # charID -> list of (tag_type, position)
    order = []

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
        if tt == 0:
            break
        if tt in TARGET_TAGS and l >= 2:
            cid = struct.unpack_from('<H', pay)[0]
            entry = (tt, tag_pos, cid)
            by_cid.setdefault(cid, []).append(entry)
            order.append(entry)
        pos += l

    print(f"\n=== {label} ===")
    print("Duplicate charIDs (same charID defined by multiple tags):")
    found_dup = False
    for cid, entries in by_cid.items():
        if len(entries) > 1:
            found_dup = True
            for tt, tpos, _ in entries:
                tname = TAG_NAMES.get(tt, f'Tag{tt}')
                print(f"  charID={cid}: {tname} at byte {tpos}")
    if not found_dup:
        print("  (none found)")

    print(f"\nDair bitmap charIDs in {label}:")
    for cid in sorted(DAIR_BITMAPS):
        entries = by_cid.get(cid, [])
        for tt, tpos, _ in entries:
            tname = TAG_NAMES.get(tt, f'Tag{tt}')
            print(f"  charID={cid}: {tname} at byte {tpos}")
        if not entries:
            print(f"  charID={cid}: NOT FOUND")

    # Count tag types
    from collections import Counter
    counts = Counter(tt for tt, _, _ in order)
    print(f"\nTag counts: {dict(sorted((TAG_NAMES.get(k, f'Tag{k}'), v) for k, v in counts.items()))}")
    return by_cid

analyze_swf(RT, "RT")
analyze_swf(OG, "OG")
