"""
Find which sprites contain charID=1001 (bm_dairHand) and compare them between OG and RT.
Focus on finding the STANCE sprite and comparing its attack frame structure.
"""
import struct, zlib, json
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

PLACE_TAGS = {4, 26, 70}  # PlaceObject, PlaceObject2, PlaceObject3
SHOW_FRAME = 1
END_TAG = 0

def parse_sprite_inner_tags(inner_data):
    """Parse inner tags of a DefineSprite body (AFTER charID+frameCount, i.e. the timeline).
    Returns list of (tag_type, body_bytes, frame_index).
    """
    tags = []
    off = 0
    frame = 0
    while off < len(inner_data):
        if off + 2 > len(inner_data): break
        tw_bytes = inner_data[off:off+2]
        if len(tw_bytes) < 2: break
        tw = struct.unpack_from('<H', tw_bytes)[0]
        tag_type = tw >> 6
        tag_len = tw & 0x3f
        off += 2
        if tag_len == 63:
            if off + 4 > len(inner_data): break
            tag_len = struct.unpack_from('<i', inner_data, off)[0]
            if tag_len < 0 or tag_len > len(inner_data): break
            off += 4
        if off + tag_len > len(inner_data): break
        body = inner_data[off:off+tag_len]
        tags.append((tag_type, body, frame))
        if tag_type == SHOW_FRAME:
            frame += 1
        elif tag_type == END_TAG:
            break
        off += tag_len
    return tags

def get_sprite_children(tags, data):
    """Build map: sprite_charID -> set of referenced charIDs"""
    children = defaultdict(set)
    for (t, o, l) in tags:
        if t == 39 and l >= 4:
            cid = struct.unpack_from('<H', data, o)[0]
            inner = data[o+4:o+l]  # skip charID(2) + frameCount(2)
            for (inner_t, body, frame) in parse_sprite_inner_tags(inner):
                # PlaceObject (tag 4)
                if inner_t == 4 and len(body) >= 2:
                    ref_cid = struct.unpack_from('<H', body)[0]
                    children[cid].add(ref_cid)
                # PlaceObject2 (tag 26)
                elif inner_t == 26 and len(body) >= 4:
                    flags = struct.unpack_from('<H', body)[0]
                    has_char = (flags >> 1) & 1
                    if has_char and len(body) >= 5:
                        ref_cid = struct.unpack_from('<H', body, 3)[0]
                        children[cid].add(ref_cid)
                # PlaceObject3 (tag 70)
                elif inner_t == 70 and len(body) >= 6:
                    flags1 = body[0]
                    has_char = (flags1 >> 1) & 1
                    if has_char and len(body) >= 6:
                        ref_cid = struct.unpack_from('<H', body, 4)[0]
                        children[cid].add(ref_cid)
    return children

og_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'
rt_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'
og_tags, og_data = read_swf_tags(og_path)
rt_tags, rt_data = read_swf_tags(rt_path)

og_children = get_sprite_children(og_tags, og_data)
rt_children = get_sprite_children(rt_tags, rt_data)

def find_ancestors(cid, children_map, max_depth=8):
    """Find all ancestors of cid by BFS"""
    # Invert children map to parent map
    parents = defaultdict(set)
    for parent, kids in children_map.items():
        for kid in kids:
            parents[kid].add(parent)
    
    visited = set()
    queue = [(cid, 0)]
    paths = []
    while queue:
        current, depth = queue.pop(0)
        if depth > max_depth or current in visited:
            continue
        visited.add(current)
        for p in sorted(parents[current]):
            paths.append((depth+1, p))
            queue.append((p, depth+1))
    return paths

print('=== OG parents of charID=1001 ===')
og_paths = find_ancestors(1001, og_children)
for depth, cid in og_paths[:20]:
    print(f'  {"  "*depth}charID={cid}')

print('\n=== RT parents of charID=1001 ===')
rt_paths = find_ancestors(1001, rt_children)
for depth, cid in rt_paths[:20]:
    print(f'  {"  "*depth}charID={cid}')

# Get parent charIDs of 1001
og_direct_parents = set(cid for (d, cid) in og_paths if d == 1)
rt_direct_parents = set(cid for (d, cid) in rt_paths if d == 1)
print(f'\nOG direct parents of 1001: {og_direct_parents}')
print(f'RT direct parents of 1001: {rt_direct_parents}')

# Get grandparents (parents of parents)
def get_sprite_body(tags, data, target_cid):
    for (t, o, l) in tags:
        if t == 39 and l >= 4:
            cid = struct.unpack_from('<H', data, o)[0]
            if cid == target_cid:
                return data[o:o+l]
    return None

# Compare the DIRECT parent sprites of charID=1001
for parent_cid in sorted(og_direct_parents | rt_direct_parents):
    og_body = get_sprite_body(og_tags, og_data, parent_cid)
    rt_body = get_sprite_body(rt_tags, rt_data, parent_cid)
    if og_body and rt_body:
        og_inner = og_body[4:]
        rt_inner = rt_body[4:]
        print(f'\n=== Sprite charID={parent_cid} (direct parent of bm_dairHand) ===')
        print(f'  OG inner_len={len(og_inner)} RT inner_len={len(rt_inner)} identical={og_inner==rt_inner}')
        if og_inner != rt_inner:
            # Show structured comparison of inner tags
            og_inner_tags = parse_sprite_inner_tags(og_inner)
            rt_inner_tags = parse_sprite_inner_tags(rt_inner)
            print(f'  OG inner tags: {len(og_inner_tags)}, RT inner tags: {len(rt_inner_tags)}')
            print('  OG tag types by frame:')
            for tt, body, frame in og_inner_tags[:15]:
                print(f'    frame={frame} type={tt} len={len(body)} body={body[:8].hex()}')
            print('  RT tag types by frame:')
            for tt, body, frame in rt_inner_tags[:15]:
                print(f'    frame={frame} type={tt} len={len(body)} body={body[:8].hex()}')
    elif og_body and not rt_body:
        print(f'\nSprite {parent_cid}: EXISTS in OG but NOT in RT')
    elif not og_body and rt_body:
        print(f'\nSprite {parent_cid}: EXISTS in RT but NOT in OG')
