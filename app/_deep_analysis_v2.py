"""
Properly analyze the RT SWF with correct PO2 parsing.
Check for multiple placements of charID=1001, OG vs RT stance frame labels,
and compare stance MC structure.
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

SHOW_FRAME = 1
END_TAG = 0

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
        if tag_type == SHOW_FRAME:
            frame += 1
        elif tag_type == END_TAG:
            break
        off += tag_len
    return tags

# CORRECT PlaceObject2 parsing: flags=1 byte, depth=uint16, [charID=uint16]
def extract_placements_correct(inner_tags):
    placements = []
    for (tt, body, frame) in inner_tags:
        if tt == 4 and len(body) >= 4:   # PlaceObject: charID(2)+depth(2)
            cid = struct.unpack_from('<H', body)[0]
            depth = struct.unpack_from('<H', body, 2)[0]
            placements.append((frame, depth, cid))
        elif tt == 26 and len(body) >= 3:  # PlaceObject2: flags(1)+depth(2)+[charID(2)]
            flags = body[0]
            has_char = (flags >> 1) & 1
            depth = struct.unpack_from('<H', body, 1)[0]
            if has_char and len(body) >= 5:
                cid = struct.unpack_from('<H', body, 3)[0]
                placements.append((frame, depth, cid))
        elif tt == 70 and len(body) >= 4:  # PlaceObject3: flags1(1)+flags2(1)+depth(2)+[charID(2)]
            flags1 = body[0]
            has_char = (flags1 >> 1) & 1
            depth = struct.unpack_from('<H', body, 2)[0]
            if has_char and len(body) >= 6:
                cid = struct.unpack_from('<H', body, 4)[0]
                placements.append((frame, depth, cid))
    return placements

og_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'
rt_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'
og_tags, og_data = read_swf_tags(og_path)
rt_tags, rt_data = read_swf_tags(rt_path)

def build_sprite_map(swf_tags, swf_data):
    sprites = {}
    for (t, o, l) in swf_tags:
        if t == 39 and l >= 4:
            cid = struct.unpack_from('<H', swf_data, o)[0]
            frame_count = struct.unpack_from('<H', swf_data, o+2)[0]
            inner = swf_data[o+4:o+l]
            inner_tags = parse_inner(inner)
            placements = extract_placements_correct(inner_tags)
            labels = {}
            for (tt, body, frame) in inner_tags:
                if tt == 43 and body:  # FrameLabel
                    label = body.rstrip(b'\x00').decode('latin-1', errors='replace')
                    labels[label] = frame
            sprites[cid] = {
                'frame_count': frame_count,
                'placements': placements,
                'labels': labels,
                'inner_len': len(inner),
            }
    return sprites

print('Building sprite maps...')
og_sprites = build_sprite_map(og_tags, og_data)
rt_sprites = build_sprite_map(rt_tags, rt_data)

# Build proper ancestry
def build_parent_map(sprites):
    parents = defaultdict(set)
    for parent_cid, info in sprites.items():
        for (f, d, cid) in info['placements']:
            parents[cid].add(parent_cid)
    return parents

og_parents = build_parent_map(og_sprites)
rt_parents = build_parent_map(rt_sprites)

# Find where charID=1001 appears
print('\n=== OG: all sprites placing charID=1001 ===')
for parent_cid, info in sorted(og_sprites.items()):
    places_1001 = [(f, d) for (f, d, c) in info['placements'] if c == 1001]
    if places_1001:
        labels_rev = {v: k for k, v in info['labels'].items()}
        for (f, d) in places_1001:
            label = labels_rev.get(f, f'frame{f}')
            print(f'  Sprite {parent_cid}: frame={f}({label}) depth={d}')

print('\n=== RT: all sprites placing charID=1001 ===')
for parent_cid, info in sorted(rt_sprites.items()):
    places_1001 = [(f, d) for (f, d, c) in info['placements'] if c == 1001]
    if places_1001:
        labels_rev = {v: k for k, v in info['labels'].items()}
        for (f, d) in places_1001:
            label = labels_rev.get(f, f'frame{f}')
            print(f'  Sprite {parent_cid}: frame={f}({label}) depth={d}')

# Check Sprite 1471 more carefully
print('\n=== Sprite 1471 placements - frame 0 ===')
for (f, d, c) in og_sprites.get(1471, {}).get('placements', []):
    if f == 0:
        print(f'  OG: depth={d} charID={c}')
for (f, d, c) in rt_sprites.get(1471, {}).get('placements', []):
    if f == 0:
        print(f'  RT: depth={d} charID={c}')

# Find what places Sprite 1471 in each SWF
print('\n=== Which sprites contain Sprite 1471 ===')
print('OG parents of 1471:', sorted(og_parents.get(1471, [])))
print('RT parents of 1471:', sorted(rt_parents.get(1471, [])))

# Trace full ancestry of 1001 in OG
def trace_full(cid, parents, depth=0, visited=None):
    if visited is None: visited = set()
    if cid in visited or depth > 8: return []
    visited.add(cid)
    result = [(depth, cid)]
    for p in sorted(parents.get(cid, [])):
        result.extend(trace_full(p, parents, depth+1, visited))
    return result

print('\n=== OG ancestry of charID=1001 ===')
for d, c in trace_full(1001, og_parents):
    print(f'  {"  "*d}charID={c} labels={list(og_sprites.get(c, {}).get("labels", {}).keys())[:5]}')

print('\n=== RT ancestry of charID=1001 ===')
for d, c in trace_full(1001, rt_parents):
    print(f'  {"  "*d}charID={c} labels={list(rt_sprites.get(c, {}).get("labels", {}).keys())[:5]}')

# Check if OG Sprite 1556 has "attack" label
print('\n=== Stance (Sprite 1556) labels comparison ===')
if 1556 in og_sprites:
    og_labels = sorted(og_sprites[1556]['labels'].items(), key=lambda x: x[1])
    print(f'OG Sprite 1556 labels ({len(og_labels)}): {[l for l, f in og_labels[:20]]}')
if 1556 in rt_sprites:
    rt_labels = sorted(rt_sprites[1556]['labels'].items(), key=lambda x: x[1])
    print(f'RT Sprite 1556 labels ({len(rt_labels)}): {[l for l, f in rt_labels[:20]]}')
    print('"attack" in RT labels:', "attack" in rt_sprites[1556]['labels'])
if 1556 in og_sprites:
    print('"attack" in OG labels:', "attack" in og_sprites[1556]['labels'])
