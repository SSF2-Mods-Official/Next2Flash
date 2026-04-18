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
rt_swf = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'

og_tags = parse_all_tags(og_p)
rt_tags = parse_all_tags(rt_swf)

# Examine tag index 639
og_t, og_b = og_tags[639]
rt_t, rt_b = rt_tags[639]
og_cid = struct.unpack_from('<H', og_b, 0)[0]
rt_cid = struct.unpack_from('<H', rt_b, 0)[0]
print(f'idx=639: OG type={og_t} len={len(og_b)} shape_charID={og_cid}')
print(f'idx=639: RT type={rt_t} len={len(rt_b)} shape_charID={rt_cid}')
print(f'Bodies match: {og_b == rt_b}')

# Check context around position 1006 in RT body
pos = 1006
if len(rt_b) > pos+8:
    print(f'RT body around pos 1006: {rt_b[pos-4:pos+8].hex()}')
    print(f'Byte before (fill type?): 0x{rt_b[1005]:02x}')
if len(og_b) > pos:
    print(f'OG body around pos 1006: {og_b[pos-4:pos+8].hex()}')
else:
    print(f'OG body too short (len={len(og_b)}) for pos 1006')

# Find where they first differ
for i in range(min(len(og_b), len(rt_b))):
    if og_b[i] != rt_b[i]:
        print(f'First diff at byte {i}: OG=0x{og_b[i]:02x} RT=0x{rt_b[i]:02x}')
        print(f'  Context OG: {og_b[max(0,i-4):i+8].hex()}')
        print(f'  Context RT: {rt_b[max(0,i-4):i+8].hex()}')
        break

# Also: scan all shapes in OG vs RT for 0xe903 pattern  
SHAPE_TYPES = {2, 22, 32, 83}
print("\n=== All shapes containing 0xe903 (possible charID=1001 bitmap fill) ===")
for label, tags in [('OG', og_tags), ('RT', rt_tags)]:
    for i, (t, b) in enumerate(tags):
        if t in SHAPE_TYPES:
            pos = b.find(b'\xe9\x03')
            while pos >= 0:
                cid = struct.unpack_from('<H', b, 0)[0]
                prev_byte = b[pos-1] if pos > 0 else 0
                print(f'{label} idx={i} shape_cid={cid} found_at={pos} prev_byte=0x{prev_byte:02x}')
                pos = b.find(b'\xe9\x03', pos+1)
