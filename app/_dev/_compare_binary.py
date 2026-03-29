"""Compare two SWF files binary-wise to see what changed."""
import struct, zlib

def decompress(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:3] == b'CWS':
        data = data[:8] + zlib.decompress(data[8:])
    return data

def walk_tags(data):
    offset = 8
    nbits = data[8] >> 3
    total_bits = 5 + nbits * 4
    offset = 8 + (total_bits + 7) // 8 + 4
    tags = []
    while offset < len(data):
        tc = struct.unpack_from('<H', data, offset)[0]
        tt = tc >> 6; tl = tc & 0x3f; hs = 2
        if tl == 0x3f:
            tl = struct.unpack_from('<I', data, offset + 2)[0]; hs = 6
        tags.append((tt, offset, hs, tl, data[offset:offset+hs+tl]))
        offset += hs + tl
        if tt == 0: break
    return tags

TAG_NAMES = {
    2:'DefineShape', 6:'DefineBits', 11:'DefineText', 14:'DefineSound',
    20:'DefineBitsLossless', 21:'DefineBitsJPEG2', 22:'DefineShape2',
    32:'DefineShape3', 33:'DefineText2', 35:'DefineBitsJPEG3',
    36:'DefineBitsLossless2', 37:'DefineEditText',
    39:'DefineSprite', 46:'DefineMorphShape', 48:'DefineFont3',
    75:'DefineFont3', 83:'DefineShape4', 84:'DefineMorphShape2',
}

old = decompress('converted/gameandwatch_cli2.swf')
new = decompress('converted/cli3.swf')

old_tags = walk_tags(old)
new_tags = walk_tags(new)

print(f"Old tags: {len(old_tags)}, New tags: {len(new_tags)}")

if len(old_tags) != len(new_tags):
    print("TAG COUNT MISMATCH!")
else:
    diffs = 0
    for i, (ot, nt) in enumerate(zip(old_tags, new_tags)):
        o_tt, o_off, o_hs, o_tl, o_bytes = ot
        n_tt, n_off, n_hs, n_tl, n_bytes = nt
        if o_bytes != n_bytes:
            diffs += 1
            tname = TAG_NAMES.get(o_tt, f'Tag{o_tt}')
            if o_tl >= 2:
                o_cid = struct.unpack_from('<H', o_bytes, o_hs)[0]
                n_cid = struct.unpack_from('<H', n_bytes, n_hs)[0]
                cid_info = f" cid={o_cid}->{n_cid}"
            else:
                cid_info = ""
            # Find differing byte positions
            diff_count = sum(1 for a, b in zip(o_bytes, n_bytes) if a != b)
            print(f"  Tag {i}: {tname}{cid_info} - {diff_count} bytes differ (len={o_tl})")
    print(f"\nTotal tags with differences: {diffs} / {len(old_tags)}")
