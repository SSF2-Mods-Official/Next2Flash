"""
Search the N2D project for the stance MC and find what sprites contain bm_dairHand.
Also look at what Sprite 1556 actually contains.
"""
import struct, zlib, json
from collections import defaultdict, Counter

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

rt_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'
rt_tags, rt_data = read_swf_tags(rt_path)

SHOW_FRAME = 1
END_TAG = 0

def parse_sprite_inner(inner_data):
    """Parse DefineSprite inner tags (AFTER charID+frameCount)."""
    tags = []
    off = 0
    frame = 0
    while off < len(inner_data):
        if off + 2 > len(inner_data): break
        tw = struct.unpack_from('<H', inner_data, off)[0]
        tag_type = tw >> 6
        tag_len = tw & 0x3f
        off += 2
        if tag_len == 63:
            if off + 4 > len(inner_data): break
            tag_len = struct.unpack_from('<i', inner_data, off)[0]
            if tag_len < 0: break
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

def extract_placements(inner_tags):
    """(frame, depth, charID) for all PO/PO2/PO3 that place a char."""
    placements = []
    for (tt, body, frame) in inner_tags:
        if tt == 4 and len(body) >= 4:  # PlaceObject: charID(2)+depth(2)
            cid = struct.unpack_from('<H', body)[0]
            depth = struct.unpack_from('<H', body, 2)[0]
            placements.append((frame, depth, cid))
        elif tt == 26 and len(body) >= 5:  # PlaceObject2
            flags = struct.unpack_from('<H', body)[0]
            has_char = (flags >> 1) & 1
            depth = struct.unpack_from('<H', body, 2)[0]
            if has_char:
                cid = struct.unpack_from('<H', body, 4)[0]
                placements.append((frame, depth, cid))
        elif tt == 70 and len(body) >= 6:  # PlaceObject3: flags1(1)+flags2(1)+depth(2)+charID(2)
            flags1 = body[0]
            has_char = (flags1 >> 1) & 1
            depth = struct.unpack_from('<H', body, 2)[0]
            if has_char:
                cid = struct.unpack_from('<H', body, 4)[0]
                placements.append((frame, depth, cid))
    return placements

# Build correct: sprite_charID -> set of placed charIDs
print('Building RT sprite children map...')
rt_children = {}  # charID -> set of placed charIDs (all frames)
rt_by_cid = {}    # charID -> (inner_tags, placements)
for (t, o, l) in rt_tags:
    if t == 39 and l >= 4:
        cid = struct.unpack_from('<H', rt_data, o)[0]
        # DefineSprite body: charID(2) + frameCount(2) + inner_tags
        inner = rt_data[o+4:o+l]  # skip charID+frameCount
        inner_tags = parse_sprite_inner(inner)
        placements = extract_placements(inner_tags)
        rt_children[cid] = set(c for (f, d, c) in placements)
        rt_by_cid[cid] = (inner_tags, placements)

# Build parent map
rt_parents = defaultdict(set)
for parent, kids in rt_children.items():
    for kid in kids:
        rt_parents[kid].add(parent)

print(f'Total sprites: {len(rt_children)}')

# Follow ancestry of charID=1001 (bm_dairHand)
def trace_ancestry(cid, parents_map, depth=0, visited=None):
    if visited is None:
        visited = set()
    if cid in visited or depth > 8:
        return
    visited.add(cid)
    print(f'{"  " * depth}charID={cid}')
    for p in sorted(parents_map.get(cid, [])):
        trace_ancestry(p, parents_map, depth+1, visited)

print('\n=== RT Ancestry of charID=1001 (bm_dairHand) ===')
trace_ancestry(1001, rt_parents)

# Show Sprite 1471 placements
print('\n=== Sprite 1471 placements (first 10 frames) ===')
if 1471 in rt_by_cid:
    inner_tags, placements = rt_by_cid[1471]
    for f, d, c in placements[:10]:
        print(f'  frame={f} depth={d} charID={c}')

# What does Sprite 1556 actually place?
print('\n=== Sprite 1556 placed charIDs (unique) ===')
if 1556 in rt_children:
    print(sorted(rt_children[1556])[:20])

# Check if there's a FrameLabel "attack" in ancestors of 1001
print('\n=== Frame labels in Sprite 1471 ===')
if 1471 in rt_by_cid:
    inner_tags, _ = rt_by_cid[1471]
    for (tt, body, frame) in inner_tags:
        if tt == 43:  # FrameLabel
            label = body.rstrip(b'\x00').decode('latin-1', errors='replace')
            print(f'  frame={frame} label="{label}"')

print('\n=== Frame labels in Sprite 1556 ===')
if 1556 in rt_by_cid:
    inner_tags, _ = rt_by_cid[1556]
    for (tt, body, frame) in inner_tags:
        if tt == 43:  # FrameLabel
            label = body.rstrip(b'\x00').decode('latin-1', errors='replace')
            print(f'  frame={frame} label="{label}"')
    # Also show what charIDs are placed when and at what depths
    all_placements = [(f,d,c) for (tt, body, f) in inner_tags for _ in ['x'] if False]
    if 1471 in rt_children[1556]:
        places_1471 = [(f, d) for (f, d, c) in rt_by_cid[1556][1] if c == 1471]
        print(f'  charID=1471 placed at: {places_1471[:10]}')
