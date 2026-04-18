"""
Find which DefineSprite tags differ between OG and RT SWF, and trace
the parent chain of bm_dairHand (charID=1001) in both.
"""
import struct, zlib
from collections import defaultdict
import hashlib

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

og_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'
rt_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'
og_tags, og_data = read_swf_tags(og_path)
rt_tags, rt_data = read_swf_tags(rt_path)

# Build charID -> tag content map for DefineSprite (tag 39) in both
def get_sprites(tags, data):
    sprites = {}
    for (t, o, l) in tags:
        if t == 39 and l >= 4:
            cid = struct.unpack_from('<H', data, o)[0]
            content = data[o:o+l]
            sprites[cid] = content
    return sprites

og_sprites = get_sprites(og_tags, og_data)
rt_sprites = get_sprites(rt_tags, rt_data)

all_sprite_cids = sorted(set(og_sprites) | set(rt_sprites))

# Find sprites that:
# a) exist in both but differ
# b) exist only in OG
# c) exist only in RT
differ = []
only_og = []
only_rt = []
for cid in all_sprite_cids:
    if cid in og_sprites and cid in rt_sprites:
        if og_sprites[cid] != rt_sprites[cid]:
            differ.append(cid)
    elif cid in og_sprites:
        only_og.append(cid)
    else:
        only_rt.append(cid)

print(f'DefineSprite count: OG={len(og_sprites)} RT={len(rt_sprites)}')
print(f'Differ: {len(differ)} sprites')
print(f'Only in OG: {only_og}')
print(f'Only in RT: {only_rt}')
print(f'First 20 differing: {differ[:20]}')

# Now find which sprites reference charID=1001 (bm_dairHand)
def find_references_in_sprite(sprite_data):
    """Parse the inner tags of a DefineSprite and find all charIDs referenced in PlaceObject tags."""
    refs = set()
    # Inner tags start at offset 4 (charID=2 bytes + frame_count=2 bytes)
    off = 4
    while off < len(sprite_data):
        if off + 2 > len(sprite_data): break
        tw = struct.unpack_from('<H', sprite_data, off)[0]
        tag_type = tw >> 6
        tag_len = tw & 0x3f
        off += 2
        if tag_len == 63:
            if off + 4 > len(sprite_data): break
            tag_len = struct.unpack_from('<i', sprite_data, off)[0]
            off += 4
        body_start = off
        # PlaceObject (tag 4): charID at bytes 0-1
        if tag_type == 4 and tag_len >= 2:
            cid = struct.unpack_from('<H', sprite_data, body_start)[0]
            refs.add(cid)
        # PlaceObject2 (tag 26): hasCharacter flag
        elif tag_type == 26 and tag_len >= 3:
            flags = struct.unpack_from('<H', sprite_data, body_start)[0]
            has_char = (flags >> 1) & 1  # bit 1 = hasCharacter
            if has_char and tag_len >= 5:
                cid = struct.unpack_from('<H', sprite_data, body_start + 3)[0]
                refs.add(cid)
        # PlaceObject3 (tag 70): hasCharacter flag
        elif tag_type == 70 and tag_len >= 4:
            flags1 = struct.unpack_from('<B', sprite_data, body_start)[0]
            flags2 = struct.unpack_from('<B', sprite_data, body_start + 1)[0]
            has_char = (flags1 >> 1) & 1
            if has_char:
                depth = struct.unpack_from('<H', sprite_data, body_start + 2)[0]
                if tag_len >= 6:
                    cid = struct.unpack_from('<H', sprite_data, body_start + 4)[0]
                    refs.add(cid)
        off += tag_len
    return refs

# Find which sprites contain charID=1001 directly
sprites_with_1001 = []
for cid, content in og_sprites.items():
    refs = find_references_in_sprite(content[2:])  # skip charID
    if 1001 in refs:
        sprites_with_1001.append(cid)
print(f'\nSprites directly referencing charID=1001: {sprites_with_1001}')

# Build reverse map: for each sprite S, find sprites that contain S
def build_parent_map(sprites):
    parent_map = defaultdict(set)
    for parent_cid, content in sprites.items():
        refs = find_references_in_sprite(content[2:])
        for ref in refs:
            parent_map[ref].add(parent_cid)
    return parent_map

og_parents = build_parent_map(og_sprites)
rt_parents = build_parent_map(rt_sprites)

# Trace ancestry of charID=1001
def get_ancestors(cid, parents, depth=0, max_depth=6):
    if depth > max_depth:
        return [f'  (depth limit)']
    ancs = []
    for parent in sorted(parents.get(cid, [])):
        ancs.append(f'  {"  " * depth}charID={parent}')
        ancs.extend(get_ancestors(parent, parents, depth+1, max_depth))
    return ancs

print('\nOG ancestry of charID=1001:')
print('\n'.join(['  charID=1001'] + get_ancestors(1001, og_parents)[:20]))
print('\nRT ancestry of charID=1001:')
print('\n'.join(['  charID=1001'] + get_ancestors(1001, rt_parents)[:20]))

# Also check if charID=1471 differs between OG and RT
if 1471 in og_sprites and 1471 in rt_sprites:
    same_1471 = og_sprites[1471] == rt_sprites[1471]
    print(f'\nCharID=1471 sprite: OG len={len(og_sprites[1471])} RT len={len(rt_sprites[1471])} identical={same_1471}')
    if not same_1471:
        print('  DIFFERS - first 20 byte diff:')
        s1 = og_sprites[1471]
        s2 = rt_sprites[1471]
        for i in range(min(len(s1), len(s2))):
            if s1[i] != s2[i]:
                print(f'  Offset {i}: OG=0x{s1[i]:02x} RT=0x{s2[i]:02x}')
                if i > 5: break

# Show first 5 differing sprites details
print(f'\nFirst 5 differing sprites:')
for cid in differ[:5]:
    ogl = len(og_sprites[cid])
    rtl = len(rt_sprites[cid])
    print(f'  charID={cid}: OG len={ogl} RT len={rtl}')
    is_parent_of_1001 = cid in og_parents.get(1001, set()) or cid in rt_parents.get(1001, set())
    print(f'    is direct parent of 1001: {is_parent_of_1001}')
