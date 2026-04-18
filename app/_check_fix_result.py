import struct, zlib, base64

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

og_tags = parse_all_tags(og_p)
rt_tags = parse_all_tags(rt_p)

print("=== charID=1001 (bm_dairHand) LL2 in OG vs RT ===")
for label, tags in [('OG', og_tags), ('RT', rt_tags)]:
    for t, b in tags:
        if t == 36:
            cid = struct.unpack_from('<H', b, 0)[0]
            if cid == 1001:
                fmt = b[2]
                w = struct.unpack_from('<H', b, 3)[0]
                h = struct.unpack_from('<H', b, 5)[0]
                print(f'{label}: charID={cid} fmt={fmt} {w}x{h} tag_len={len(b)}')
                if fmt == 3:
                    color_table_size = b[7] + 1
                    dec = zlib.decompress(b[8:])
                    palette = dec[:color_table_size*4]
                    row_stride = (w + 3) & ~3
                    indices_data = dec[color_table_size*4:]
                    print(f'  Palette: {color_table_size} colors, palette hex: {palette.hex()}')
                    rgba_pixels = bytearray()
                    for y in range(h):
                        for x in range(w):
                            idx = indices_data[y * row_stride + x]
                            rgba_pixels.extend(palette[idx*4:idx*4+4])
                    print(f'  Reconstructed RGBA b64: {base64.b64encode(bytes(rgba_pixels)).decode()}')
                elif fmt == 5:
                    dec = zlib.decompress(b[7:])
                    # un-premultiply ARGB -> RGBA
                    rgba_pixels = bytearray()
                    for i in range(0, min(len(dec), w*h*4), 4):
                        a = dec[i]; r = dec[i+1]; g = dec[i+2]; bl = dec[i+3]
                        if a == 0:
                            rgba_pixels.extend([0,0,0,0])
                        elif a == 255:
                            rgba_pixels.extend([r,g,bl,255])
                        else:
                            rgba_pixels.extend([min(255,(r*255+a//2)//a), min(255,(g*255+a//2)//a), min(255,(bl*255+a//2)//a), a])
                    print(f'  Decoded RGBA b64: {base64.b64encode(bytes(rgba_pixels)).decode()}')

# Pool estimate
print("\n=== Pool estimate (format=3 ~ 1 byte/pixel, format=5 ~ 4 bytes/pixel) ===")
og_pool = sum(
    (256*4 + struct.unpack_from('<H',b,3)[0]*struct.unpack_from('<H',b,5)[0]) if b[2]==3
    else struct.unpack_from('<H',b,3)[0]*struct.unpack_from('<H',b,5)[0]*4
    for t,b in og_tags if t==36 and len(b)>=7
)
rt_pool = sum(
    (256*4 + struct.unpack_from('<H',b,3)[0]*struct.unpack_from('<H',b,5)[0]) if b[2]==3
    else struct.unpack_from('<H',b,3)[0]*struct.unpack_from('<H',b,5)[0]*4
    for t,b in rt_tags if t==36 and len(b)>=7
)
print(f'OG pool estimate: {og_pool:,} bytes = {og_pool//1024//1024} MB')
print(f'RT pool estimate (after fix): {rt_pool:,} bytes = {rt_pool//1024//1024} MB')

print("\n=== charID=1178 (bm_ftiltHand) LL2 format in RT ===")
for t, b in rt_tags:
    if t == 36:
        cid = struct.unpack_from('<H', b, 0)[0]
        if cid == 1178:
            fmt = b[2]
            w = struct.unpack_from('<H', b, 3)[0]
            h = struct.unpack_from('<H', b, 5)[0]
            print(f'RT: charID={cid} fmt={fmt} {w}x{h} tag_len={len(b)}')
