"""Investigate charID=304 (placed at depth=10,12 in DAir_73) and compare RT vs OG LL2 256-bytes for charID=1001."""
import struct, zlib

RT = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'
OG = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'

TAG_NAMES = {2: 'DefineShape', 22: 'DefineShape2', 32: 'DefineShape3', 83: 'DefineShape4',
             20: 'DefineBitsLossless', 36: 'DefineBitsLossless2',
             6: 'DefineBitsJPEG', 21: 'DefineBitsJPEG2', 35: 'DefineBitsJPEG3',
             39: 'DefineSprite', 7: 'DefineButton', 26: 'DefineButton2',
             76: 'SymbolClass', 0: 'End'}

def parse_swf(path):
    with open(path, 'rb') as f:
        raw = f.read()
    if raw[:3] == b'CWS':
        raw = raw[:8] + zlib.decompress(raw[8:])
    pos = 8
    nb = (raw[pos] >> 3) & 0x1f
    pos += (5 + nb * 4 + 7) // 8 + 4
    tags = {}
    tag_list = []
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
        tags.setdefault(tt, {})[tag_pos] = (l, pay)
        tag_list.append((tt, tag_pos, l, pay))
        pos += l
    return tags, tag_list, raw

for swf_path, label in [(RT, "RT"), (OG, "OG")]:
    tags, tag_list, raw = parse_swf(swf_path)
    print(f"\n=== {label}: What is charID=304? ===")
    for tt_check in [2, 22, 32, 83, 20, 36, 39, 35, 21]:
        by_pos = tags.get(tt_check, {})
        for tpos, (l, pay) in by_pos.items():
            if l >= 2:
                cid = struct.unpack_from('<H', pay)[0]
                if cid == 304:
                    print(f"  charID=304 is {TAG_NAMES.get(tt_check, f'Tag{tt_check}')} at byte {tpos}")
                    break

    # Verify LL2 for charID=1001 (bm_dairHand) — check the actual zlib data
    print(f"\n{label}: LL2 charID=1001 details:")
    for tpos, (l, pay) in tags.get(36, {}).items():
        if l >= 2 and struct.unpack_from('<H', pay)[0] == 1001:
            cid = struct.unpack_from('<H', pay)[0]
            fmt = pay[2]
            w = struct.unpack_from('<H', pay, 3)[0]
            h = struct.unpack_from('<H', pay, 5)[0]
            zdata = pay[7:]
            print(f"  tagPos={tpos}, tagLen={l}, format={fmt}, w={w}, h={h}, zlibLen={len(zdata)}")
            try:
                decompressed = zlib.decompress(zdata)
                print(f"  zlib decompresses OK: {len(decompressed)} bytes (expected {w*h*4}={w*h*4})")
                print(f"  first 20 raw bytes (hex): {decompressed[:20].hex()}")
            except Exception as e:
                print(f"  zlib FAILED: {e}")
            break

print("\n\n=== Pixel-level comparison RT vs OG for charID=1001 ===")
rt_tags, _, _ = parse_swf(RT)
og_tags, _, _ = parse_swf(OG)

def get_ll2_pixels(tags, cid):
    for tpos, (l, pay) in tags.get(36, {}).items():
        if l >= 2 and struct.unpack_from('<H', pay)[0] == cid:
            zdata = pay[7:]
            return zlib.decompress(zdata)
    return None

rt_pixels = get_ll2_pixels(rt_tags, 1001)
og_pixels = get_ll2_pixels(og_tags, 1001)
if rt_pixels and og_pixels:
    print(f"RT pixels: {len(rt_pixels)} bytes | OG pixels: {len(og_pixels)} bytes")
    print(f"Identical: {rt_pixels == og_pixels}")
    if rt_pixels != og_pixels:
        for i in range(min(len(rt_pixels), len(og_pixels))):
            if rt_pixels[i] != og_pixels[i]:
                print(f"  First diff at byte {i}: RT=0x{rt_pixels[i]:02x} OG=0x{og_pixels[i]:02x}")
                break
else:
    print("(could not find charID=1001 LL2 in one or both SWFs)")
