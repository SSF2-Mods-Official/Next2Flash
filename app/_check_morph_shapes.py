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

# Find all DefineMorphShape (46) in OG  
print("=== OG DefineMorphShape (type=46) charIDs ===")
morph_cids_og = []
for i, (t, b) in enumerate(og_tags):
    if t == 46:
        cid = struct.unpack_from('<H', b, 0)[0]
        morph_cids_og.append(cid)
        print(f'  idx={i} charID={cid} len={len(b)}')

# Find all DefineMorphShape2 (84) in OG
print("\n=== OG DefineMorphShape2 (type=84) charIDs ===")
for i, (t, b) in enumerate(og_tags):
    if t == 84:
        cid = struct.unpack_from('<H', b, 0)[0]
        print(f'  idx={i} charID={cid} len={len(b)}')

# Find all DefineMorphShape2 (84) in RT (there should be 19)
print("\n=== RT DefineMorphShape2 (type=84) charIDs ===")
for i, (t, b) in enumerate(rt_tags):
    if t == 84:
        cid = struct.unpack_from('<H', b, 0)[0]
        print(f'  idx={i} charID={cid} len={len(b)}')

# Now: find which sprites use these morph shape charIDs
# by scanning Sprite 1471, 1556 and their children
# First collect all charIDs placed inside each sprite
def get_sprite_placements(tags, sprite_cid):
    """Find all charIDs placed inside a sprite."""
    # First find the DefineSprite tag
    in_sprite = False
    depth = 0
    placements = []
    for t, b in tags:
        if t == 39:  # DefineSprite
            cid = struct.unpack_from('<H', b, 0)[0]
            if cid == sprite_cid:
                # Parse inner tags
                inner_off = 4  # skip charID and frameCount
                while inner_off < len(b)-1:
                    rec = struct.unpack_from('<H', b, inner_off)[0]
                    tt = rec >> 6
                    tl = rec & 0x3f
                    if tl == 0x3f:
                        tl = struct.unpack_from('<I', b, inner_off+2)[0]
                        tb_off = inner_off + 6
                        inner_off += 6
                    else:
                        tb_off = inner_off + 2
                        inner_off += 2
                    tb = b[tb_off:tb_off+tl]
                    if tt == 26:  # PO2
                        flags = tb[0]
                        if flags & 0x02:  # HasCharacter
                            # depth is at bytes 1-2, charID at 3-4
                            dep = struct.unpack_from('<H', tb, 1)[0]
                            placed_cid = struct.unpack_from('<H', tb, 3)[0]
                            placements.append(placed_cid)
                    inner_off += tl
                return placements
    return placements

dair_placements = get_sprite_placements(og_tags, 1471)
print(f"\n=== Sprite 1471 (dair) placements in OG: {sorted(set(dair_placements))} ===")

morph_cids_set = set(morph_cids_og)
for cid in dair_placements:
    if cid in morph_cids_set:
        print(f"  !! Morph shape {cid} is placed in dair sprite 1471!")
