import struct, zlib
from collections import Counter

def parse_all_tags(path):
    data = open(path,'rb').read()
    sig = data[:3]
    if sig == b'CWS':
        data = b'FWS' + data[3:8] + zlib.decompress(data[8:])
    off = 8
    nb = (data[off] >> 3) & 0x1f
    off += ((5 + 4*nb) + 7) // 8
    off += 4
    tags = []
    while off < len(data)-1:
        rec = struct.unpack_from('<H', data, off)[0]
        tag_type = rec >> 6
        tag_len = rec & 0x3f
        if tag_len == 0x3f:
            tag_len = struct.unpack_from('<I', data, off+2)[0]
            body_off = off + 6
            off += 6
        else:
            body_off = off + 2
            off += 2
        body = data[body_off:body_off+tag_len]
        tags.append((tag_type, body))
        off += tag_len
    return tags

og_p = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'
rt_p = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'

print("=== LL2 bitmap FORMAT distribution ===")
for label, path in [('OG', og_p), ('RT', rt_p)]:
    tags = parse_all_tags(path)
    fmt_counter = Counter()
    for t, b in tags:
        if t == 36 and len(b) >= 3:  # LL2
            fmt = b[2]
            fmt_counter[fmt] += 1
    print(f'{label}: LL2 format distribution: {dict(sorted(fmt_counter.items()))}')
    # format 3 = indexed 8-bit (1 byte/pixel + 1024-byte color table)
    # format 4 = RGB15 (2 bytes/pixel)
    # format 5 = ARGB32 (4 bytes/pixel)
    total_decoded = 0
    for t, b in tags:
        if t == 36 and len(b) >= 7:
            fmt = b[2]
            w = struct.unpack_from('<H', b, 3)[0]
            h = struct.unpack_from('<H', b, 5)[0]
            if fmt == 3:
                total_decoded += 1024 + w * h  # color table + 1 byte/pixel
            elif fmt == 4:
                total_decoded += w * h * 2
            elif fmt == 5:
                total_decoded += w * h * 4
    print(f'  Expected decoded memory (all LL2): {total_decoded:,} bytes = {total_decoded//1024//1024} MB')

# Check a few specific LL2 bitmaps in OG to see their format
print("\n=== Sample OG LL2 bitmap formats ===")
og_tags = parse_all_tags(og_p)
rt_tags = parse_all_tags(rt_p)
for i, (t, b) in enumerate(og_tags):
    if t == 36 and len(b) >= 7:
        cid = struct.unpack_from('<H', b, 0)[0]
        fmt = b[2]
        w = struct.unpack_from('<H', b, 3)[0]
        h = struct.unpack_from('<H', b, 5)[0]
        if i < 800 and i % 50 == 0:
            print(f'  idx={i} charID={cid} fmt={fmt} {w}x{h} tag_len={len(b)}')
