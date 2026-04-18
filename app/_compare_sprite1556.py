"""Compare ALL tags in Sprite 1556 between OG and RT to find every difference."""
import struct, zlib

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

def parse_inner_list(inner_data):
    result = []
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
        result.append((tag_type, body, frame))
        if tag_type == 1: frame += 1
        elif tag_type == 0: break
        off += tag_len
    return result

def get_sprite_inner(swf_tags, swf_data, cid):
    for (t, o, l) in swf_tags:
        if t == 39 and l >= 4 and struct.unpack_from('<H', swf_data, o)[0] == cid:
            return swf_data[o+4:o+l]
    return None

TAG_NAMES = {
    0: 'End', 1: 'ShowFrame', 4: 'PlaceObject', 5: 'RemoveObject',
    18: 'SoundStreamHead', 19: 'SoundStreamBlock', 26: 'PlaceObject2',
    28: 'RemoveObject2', 36: 'DefineBitsLossless2', 43: 'FrameLabel',
    45: 'SoundStreamBlock', 70: 'PlaceObject3'
}

og_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'
rt_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'
og_tags, og_data = read_swf_tags(og_path)
rt_tags, rt_data = read_swf_tags(rt_path)

# Compare ALL inner tags of Sprite 1556
og_inner = get_sprite_inner(og_tags, og_data, 1556)
rt_inner = get_sprite_inner(rt_tags, rt_data, 1556)

og_1556 = parse_inner_list(og_inner)
rt_1556 = parse_inner_list(rt_inner)

print(f'Sprite 1556: OG tags={len(og_1556)}, RT tags={len(rt_1556)}')
print(f'Inner lengths: OG={len(og_inner)}, RT={len(rt_inner)}')

# Count by tag type
from collections import Counter
og_tc = Counter(t for (t, b, f) in og_1556)
rt_tc = Counter(t for (t, b, f) in rt_1556)
all_types = sorted(set(og_tc) | set(rt_tc))
for tp in all_types:
    name = TAG_NAMES.get(tp, f'type{tp}')
    og_cnt = og_tc.get(tp, 0)
    rt_cnt = rt_tc.get(tp, 0)
    differs = ' <-- DIFFER' if og_cnt != rt_cnt else ''
    print(f'  {name}({tp}): OG={og_cnt} RT={rt_cnt}{differs}')

# Find frames that differ
# Compare all tags at the same frame
from collections import defaultdict

def group_by_frame(tags):
    by_frame = defaultdict(list)
    for (t, b, f) in tags:
        by_frame[f].append((t, b))
    return by_frame

og_by_frame = group_by_frame(og_1556)
rt_by_frame = group_by_frame(rt_1556)

all_frames = sorted(set(og_by_frame) | set(rt_by_frame))
diffs_found = 0
for frame in all_frames:
    og_frame_tags = og_by_frame.get(frame, [])
    rt_frame_tags = rt_by_frame.get(frame, [])
    
    # Compare tag types and bodies
    if [(t, b) for (t, b) in og_frame_tags if t not in (1,)] != [(t, b) for (t, b) in rt_frame_tags if t not in (1,)]:
        if diffs_found < 10:
            print(f'\n=== Frame {frame} DIFFERS ===')
            for (t, b) in og_frame_tags:
                if t != 1:  # skip ShowFrame
                    name = TAG_NAMES.get(t, f'type{t}')
                    print(f'  OG: {name}({t}) len={len(b)} hex={b[:12].hex()}')
            for (t, b) in rt_frame_tags:
                if t != 1:
                    name = TAG_NAMES.get(t, f'type{t}')
                    print(f'  RT: {name}({t}) len={len(b)} hex={b[:12].hex()}')
        diffs_found += 1

print(f'\nTotal frames with differences: {diffs_found}')

# Also check: are all SoundStream heights different, and does OG have SoundStreamHead?
print('\n=== Sound tags in Sprite 1556 ===')
og_sound = [(t, b, f) for (t, b, f) in og_1556 if t in (18, 19, 45)]
rt_sound = [(t, b, f) for (t, b, f) in rt_1556 if t in (18, 19, 45)]
print(f'OG sound tags: {[(t, f) for t, b, f in og_sound[:5]]}')
print(f'RT sound tags: {[(t, f) for t, b, f in rt_sound[:5]]}')

# Check the root-level PlaceObject2 body for charID=1556 to find instance name 
print('\n=== Root PO2 body for charID=1556 (full bytes) ===')
for (t, o, l) in og_tags:
    if t == 26 and l >= 5:  # PlaceObject2
        body = og_data[o:o+l]
        flags = body[0]
        if (flags >> 1) & 1:  # has_char
            depth = struct.unpack_from('<H', body, 1)[0]
            cid = struct.unpack_from('<H', body, 3)[0]
            if cid == 1556:
                print(f'OG PO2 charID=1556 depth={depth} full_body={body.hex()}')
                # Try to parse the name
                has_matrix = (flags >> 2) & 1
                has_name = (flags >> 5) & 1
                print(f'  flags={flags:#04x} has_matrix={has_matrix} has_name={has_name}')
                break

for (t, o, l) in rt_tags:
    if t == 26 and l >= 5:
        body = rt_data[o:o+l]
        flags = body[0]
        if (flags >> 1) & 1:
            depth = struct.unpack_from('<H', body, 1)[0]
            cid = struct.unpack_from('<H', body, 3)[0]
            if cid == 1556:
                print(f'RT PO2 charID=1556 depth={depth} full_body={body.hex()}')
                break
