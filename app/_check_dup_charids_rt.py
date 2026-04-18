import struct, zlib
from collections import defaultdict

def read_swf_tags(path):
    with open(path, 'rb') as f:
        data = f.read()
    sig = data[:3]
    if sig == b'CWS':
        body = zlib.decompress(data[8:])
        data = data[:8] + body
    off = 8
    nbits = (data[off] >> 3) & 0x1f
    total_bits = 5 + nbits * 4
    off += (total_bits + 7) // 8
    off += 4
    tags = []
    while off < len(data):
        if off + 2 > len(data): break
        tw = struct.unpack_from('<H', data, off)[0]
        tag_type = tw >> 6
        tag_len = tw & 0x3f
        off += 2
        if tag_len == 63:
            tag_len = struct.unpack_from('<i', data, off)[0]
            off += 4
        tags.append((tag_type, off, tag_len))
        off += tag_len
    return tags, data

DEFINE_TAG_TYPES = {2, 20, 21, 32, 83, 84, 36, 35, 6, 90, 39, 78, 46, 73, 37, 26, 56, 75, 88, 89}
tag_names = {
    36: 'LL2', 35: 'JPEG3', 20: 'LL1', 21: 'JPEG2', 6: 'JPEG',
    39: 'DefineSprite', 2: 'DefShape1', 32: 'DefShape3', 83: 'DefShape4',
    46: 'DefShape2', 84: 'MorphShape2', 74: 'DefineFont2', 78: 'DefineFont3'
}

og = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'
rt = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'
og_tags, og_data = read_swf_tags(og)
rt_tags, rt_data = read_swf_tags(rt)

# Find all define tags grouped by charID in RT
rt_by_cid = defaultdict(list)
for idx, (t, o, l) in enumerate(rt_tags):
    if t in DEFINE_TAG_TYPES and l >= 2:
        cid = struct.unpack_from('<H', rt_data, o)[0]
        rt_by_cid[cid].append((idx, t, l))

dup_cids = [262, 518, 774, 1030, 1302, 1558]
print('=== DUPLICATE charID details in RT SWF ===')
for cid in dup_cids:
    print(f'charID={cid}:')
    for idx, t, l in rt_by_cid[cid]:
        tname = tag_names.get(t, f'type{t}')
        # Show first bytes of the tag body
        body = rt_data[rt_tags[idx][1]:rt_tags[idx][1]+min(l, 12)]
        import binascii
        print(f'  tag_index={idx} type={tname}({t}) len={l} body_start={binascii.hexlify(body).decode()}')
    # check OG
    og_by_cid = [(t, l) for (t, o, l) in og_tags if t in DEFINE_TAG_TYPES and l >= 2 and struct.unpack_from('<H', og_data, o)[0] == cid]
    print(f'  OG has: {[(tag_names.get(t, f"type{t}"), l) for t, l in og_by_cid]}')

print()
print('=== Check around charID=1001 - what are 994-1010 in RT? ===')
dair_range = range(994, 1011)
for cid in dair_range:
    if cid in rt_by_cid:
        for idx, t, l in rt_by_cid[cid]:
            tname = tag_names.get(t, f'type{t}')
            if t == 36:
                body = rt_data[rt_tags[idx][1]:rt_tags[idx][1]+7]
                cid_f, fmt, w, h = struct.unpack_from('<HBHH', body)
                print(f'  RT charID={cid}: {tname}({t}) w={w} h={h}')
            else:
                print(f'  RT charID={cid}: {tname}({t}) len={l}')

print()
print('=== Tag order: where does charID=1001 LL2 appear vs Sprite 1471 and its parents? ===')
# Find position of LL2 charID=1001, DefineSprite=1471
key_positions = {}
for idx, (t, o, l) in enumerate(rt_tags):
    if t in DEFINE_TAG_TYPES and l >= 2:
        cid = struct.unpack_from('<H', rt_data, o)[0]
        if cid == 1001:
            key_positions[f'charID=1001 (LL2)'] = idx
        if cid == 1471:
            key_positions[f'charID=1471 (Sprite)'] = idx
for k, v in sorted(key_positions.items(), key=lambda x: x[1]):
    print(f'  tag_index={v}: {k}')
