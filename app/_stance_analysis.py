"""
Check where and when Sprite 1471 (containing bm_dairHand) appears in Sprite 1556 (stance).
Compare OG vs RT frame mappings. Also check what's DIFFERENT in Sprite 1556 OG vs RT.
"""
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

def parse_inner(inner_data):
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
        if tag_type == 1:  # ShowFrame
            frame += 1
        elif tag_type == 0:  # End
            break
        off += tag_len
    return tags

def get_sprite_inner_tags(swf_tags, swf_data, target_cid):
    for (t, o, l) in swf_tags:
        if t == 39 and l >= 4:
            cid = struct.unpack_from('<H', swf_data, o)[0]
            if cid == target_cid:
                inner = swf_data[o+4:o+l]
                return parse_inner(inner)
    return []

og_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'
rt_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'
og_tags, og_data = read_swf_tags(og_path)
rt_tags, rt_data = read_swf_tags(rt_path)

def get_label_at_frame(inner_tags, target_frame):
    labels = {}
    for (tt, body, frame) in inner_tags:
        if tt == 43 and body:
            labels[frame] = body.rstrip(b'\x00').decode('latin-1', errors='replace')
    # Find label for target_frame or before it
    best = None
    for f, l in sorted(labels.items()):
        if f <= target_frame:
            best = l
    return best

# Get Sprite 1556 inner tags for both
og_1556_tags = get_sprite_inner_tags(og_tags, og_data, 1556)
rt_1556_tags = get_sprite_inner_tags(rt_tags, rt_data, 1556)

print(f'Sprite 1556: OG inner tag count={len(og_1556_tags)}, RT inner tag count={len(rt_1556_tags)}')

# Find all frames in stance that contain/remove Sprite 1471
def get_depth_history(inner_tags, target_depth=None, target_cid=None):
    """Track display at specific depth over frames.
    Returns list of (frame, event, depth, cid) where event is 'place' or 'remove'
    """
    history = []
    for (tt, body, frame) in inner_tags:
        if tt == 4 and len(body) >= 4:  # PlaceObject
            cid = struct.unpack_from('<H', body)[0]
            depth = struct.unpack_from('<H', body, 2)[0]
            if (target_depth is None or depth == target_depth) and (target_cid is None or cid == target_cid):
                history.append((frame, 'place', depth, cid))
        elif tt == 26 and len(body) >= 3:  # PlaceObject2
            flags = body[0]
            has_char = (flags >> 1) & 1
            is_move = flags & 1
            depth = struct.unpack_from('<H', body, 1)[0]
            if has_char and len(body) >= 5:
                cid = struct.unpack_from('<H', body, 3)[0]
                if (target_depth is None or depth == target_depth) and (target_cid is None or cid == target_cid):
                    event = 'move' if is_move else 'place'
                    history.append((frame, event, depth, cid))
            elif is_move and not has_char:
                if target_depth is None or depth == target_depth:
                    history.append((frame, 'move_nochar', depth, None))
        elif tt == 70 and len(body) >= 4:  # PlaceObject3
            flags1 = body[0]
            has_char = (flags1 >> 1) & 1
            is_move = flags1 & 1
            depth = struct.unpack_from('<H', body, 2)[0]
            if has_char and len(body) >= 6:
                cid = struct.unpack_from('<H', body, 4)[0]
                if (target_depth is None or depth == target_depth) and (target_cid is None or cid == target_cid):
                    event = 'move' if is_move else 'place'
                    history.append((frame, event, depth, cid))
        elif tt == 28 and len(body) >= 2:  # RemoveObject2
            depth = struct.unpack_from('<H', body)[0]
            if target_depth is None or depth == target_depth:
                history.append((frame, 'remove', depth, None))
        elif tt == 5 and len(body) >= 4:  # RemoveObject
            cid = struct.unpack_from('<H', body)[0]
            depth = struct.unpack_from('<H', body, 2)[0]
            if (target_depth is None or depth == target_depth) and (target_cid is None or cid == target_cid):
                history.append((frame, 'remove', depth, cid))
    return history

# Find history of charID=1471 in Sprite 1556
og_1471_history = get_depth_history(og_1556_tags, target_cid=1471)
rt_1471_history = get_depth_history(rt_1556_tags, target_cid=1471)

print('\n=== OG: Sprite 1471 placement history in Sprite 1556 ===')
for (f, ev, d, c) in og_1471_history:
    lbl = get_label_at_frame(og_1556_tags, f)
    print(f'  frame={f}({lbl}) event={ev} depth={d} charID={c}')

print('\n=== RT: Sprite 1471 placement history in Sprite 1556 ===')
for (f, ev, d, c) in rt_1471_history:
    lbl = get_label_at_frame(rt_1556_tags, f)
    print(f'  frame={f}({lbl}) event={ev} depth={d} charID={c}')

# Show what Sprite 1556 places at the a_air_down frame (33)
print('\n=== Sprite 1556 frame 33 (a_air_down) placements: OG vs RT ===')
for label, tags in [('OG', og_1556_tags), ('RT', rt_1556_tags)]:
    places_f33 = [(tt, body, f) for (tt, body, f) in tags if f == 33 and tt in (4, 26, 70, 28, 5)]
    print(f'{label}:')
    for (tt, body, f) in places_f33:
        if tt == 26 and len(body) >= 3:
            flags = body[0]
            has_char = (flags >> 1) & 1
            depth = struct.unpack_from('<H', body, 1)[0]
            cid = struct.unpack_from('<H', body, 3)[0] if has_char and len(body) >= 5 else None
            print(f'  PO2 depth={depth} charID={cid} flags={flags:#04x}')
        elif tt == 70 and len(body) >= 4:
            flags1 = body[0]
            has_char = (flags1 >> 1) & 1
            depth = struct.unpack_from('<H', body, 2)[0]
            cid = struct.unpack_from('<H', body, 4)[0] if has_char and len(body) >= 6 else None
            print(f'  PO3 depth={depth} charID={cid} flags1={flags1:#04x}')
        elif tt == 28 and len(body) >= 2:
            depth = struct.unpack_from('<H', body)[0]
            print(f'  RemoveObject2 depth={depth}')
        elif tt == 4 and len(body) >= 4:
            cid = struct.unpack_from('<H', body)[0]
            depth = struct.unpack_from('<H', body, 2)[0]
            print(f'  PO depth={depth} charID={cid}')

# Show ALL unique charIDs placed in OG vs RT Sprite 1556 frames 31-35
print('\n=== Sprite 1556 frames 31-35: charIDs placed (OG) ===')
labels_og = {}
for (tt, body, frame) in og_1556_tags:
    if tt == 43 and body:
        labels_og[frame] = body.rstrip(b'\x00').decode('latin-1', errors='replace')

for target_frame in range(31, 36):
    lbl = labels_og.get(target_frame, '')
    placements = []
    for (tt, body, f) in og_1556_tags:
        if f != target_frame: continue
        if tt == 26 and len(body) >= 3:
            flags = body[0]; has_char = (flags >> 1) & 1
            depth = struct.unpack_from('<H', body, 1)[0]
            cid = struct.unpack_from('<H', body, 3)[0] if has_char and len(body) >= 5 else None
            placements.append(f'PO2 d={depth} c={cid}')
        elif tt == 70 and len(body) >= 4:
            flags1 = body[0]; has_char = (flags1 >> 1) & 1
            depth = struct.unpack_from('<H', body, 2)[0]
            cid = struct.unpack_from('<H', body, 4)[0] if has_char and len(body) >= 6 else None
            placements.append(f'PO3 d={depth} c={cid}')
        elif tt == 28 and len(body) >= 2:
            depth = struct.unpack_from('<H', body)[0]
            placements.append(f'RO2 d={depth}')
    print(f'  OG frame {target_frame}({lbl}): {placements}')

print('\n=== Sprite 1556 frames 31-35: charIDs placed (RT) ===')
labels_rt = {}
for (tt, body, frame) in rt_1556_tags:
    if tt == 43 and body:
        labels_rt[frame] = body.rstrip(b'\x00').decode('latin-1', errors='replace')

for target_frame in range(31, 36):
    lbl = labels_rt.get(target_frame, '')
    placements = []
    for (tt, body, f) in rt_1556_tags:
        if f != target_frame: continue
        if tt == 26 and len(body) >= 3:
            flags = body[0]; has_char = (flags >> 1) & 1
            depth = struct.unpack_from('<H', body, 1)[0]
            cid = struct.unpack_from('<H', body, 3)[0] if has_char and len(body) >= 5 else None
            placements.append(f'PO2 d={depth} c={cid}')
        elif tt == 70 and len(body) >= 4:
            flags1 = body[0]; has_char = (flags1 >> 1) & 1
            depth = struct.unpack_from('<H', body, 2)[0]
            cid = struct.unpack_from('<H', body, 4)[0] if has_char and len(body) >= 6 else None
            placements.append(f'PO3 d={depth} c={cid}')
        elif tt == 28 and len(body) >= 2:
            depth = struct.unpack_from('<H', body)[0]
            placements.append(f'RO2 d={depth}')
    print(f'  RT frame {target_frame}({lbl}): {placements}')
