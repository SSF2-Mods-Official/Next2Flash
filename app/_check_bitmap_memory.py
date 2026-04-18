import struct, zlib

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

for label, path in [('OG', og_p), ('RT', rt_p)]:
    tags = parse_all_tags(path)
    total_jpeg3_compressed = 0
    total_ll2_compressed = 0
    total_ll2_uncompressed = 0
    jpeg3_count = 0
    ll2_count = 0
    
    for t, b in tags:
        if t == 35:  # JPEG3
            jpeg3_count += 1
            # body: 2 charID + 4 alphaDataOffset + JPEG data + alpha data
            if len(b) > 6:
                alpha_off = struct.unpack_from('<I', b, 2)[0]
                total_jpeg3_compressed += len(b) - 6  # tag body minus header
        elif t == 36:  # LL2
            ll2_count += 1
            total_ll2_compressed += len(b)
            if len(b) > 7:
                compressed_data = b[7:]
                try:
                    unc = zlib.decompress(compressed_data)
                    total_ll2_uncompressed += len(unc)
                except:
                    total_ll2_uncompressed += len(compressed_data)
    
    print(f'{label}:')
    print(f'  JPEG3: count={jpeg3_count}, total_tag_body={total_jpeg3_compressed:,} bytes')
    print(f'  LL2:   count={ll2_count}, total_compressed={total_ll2_compressed:,} bytes, total_uncompressed={total_ll2_uncompressed:,} bytes')
    total_pixel_mem = total_ll2_uncompressed  # uncompressed pixel data = raw memory use
    print(f'  Total bitmap pixel memory (uncompressed LL2): ~{total_pixel_mem:,} bytes = ~{total_pixel_mem//1024//1024} MB')
    print()
