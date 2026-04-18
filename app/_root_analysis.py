"""
Analyze the ROOT TIMELINE of OG vs RT SWF.
Find what charIDs are placed at root level, and check all non-DefineSprite Define tags
that might wrap charID=1556.
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

og_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'
rt_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'
og_tags, og_data = read_swf_tags(og_path)
rt_tags, rt_data = read_swf_tags(rt_path)

# Find root-level PlaceObject tags (not inside DefineSprite)
# These are tags in the main SWF timeline

TAG_NAMES = {
    1: 'ShowFrame', 0: 'End', 4: 'PlaceObject', 5: 'RemoveObject',
    9: 'SetBackgroundColor', 26: 'PlaceObject2', 28: 'RemoveObject2',
    39: 'DefineSprite', 43: 'FrameLabel', 70: 'PlaceObject3',
    82: 'DoABC', 76: 'SymbolClass', 86: 'SceneLabel'
}

print('=== OG Root Timeline PlaceObject tags ===')
for (t, o, l) in og_tags:
    if t in (4, 26, 70):
        body = og_data[o:o+l]
        if t == 4 and l >= 4:
            cid = struct.unpack_from('<H', body)[0]
            depth = struct.unpack_from('<H', body, 2)[0]
            print(f'  PlaceObject: charID={cid} depth={depth}')
        elif t == 26 and l >= 3:
            flags = body[0]
            has_char = (flags >> 1) & 1
            depth = struct.unpack_from('<H', body, 1)[0]
            cid = struct.unpack_from('<H', body, 3)[0] if has_char and l >= 5 else None
            name = None
            if (flags >> 5) & 1 and l >= 5:  # HasName
                # Name comes after charID
                name_off = 3 + (2 if has_char else 0)
                # Actually HasMatrix bit also moves the offset...
                pass  # too complex for simple parse
            print(f'  PlaceObject2: charID={cid} depth={depth} flags={flags:#04x}')
        elif t == 70 and l >= 4:
            flags1 = body[0]
            has_char = (flags1 >> 1) & 1
            depth = struct.unpack_from('<H', body, 2)[0]
            cid = struct.unpack_from('<H', body, 4)[0] if has_char and l >= 6 else None
            print(f'  PlaceObject3: charID={cid} depth={depth} flags1={flags1:#04x}')

print('\n=== RT Root Timeline PlaceObject tags ===')
for (t, o, l) in rt_tags:
    if t in (4, 26, 70):
        body = rt_data[o:o+l]
        if t == 4 and l >= 4:
            cid = struct.unpack_from('<H', body)[0]
            depth = struct.unpack_from('<H', body, 2)[0]
            print(f'  PlaceObject: charID={cid} depth={depth}')
        elif t == 26 and l >= 3:
            flags = body[0]
            has_char = (flags >> 1) & 1
            depth = struct.unpack_from('<H', body, 1)[0]
            cid = struct.unpack_from('<H', body, 3)[0] if has_char and l >= 5 else None
            print(f'  PlaceObject2: charID={cid} depth={depth} flags={flags:#04x}')
        elif t == 70 and l >= 4:
            flags1 = body[0]
            has_char = (flags1 >> 1) & 1
            depth = struct.unpack_from('<H', body, 2)[0]
            cid = struct.unpack_from('<H', body, 4)[0] if has_char and l >= 6 else None
            print(f'  PlaceObject3: charID={cid} depth={depth} flags1={flags1:#04x}')

# Find if there's a DefineSprite that places charID=1556
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
        if tag_type == 1: frame += 1
        elif tag_type == 0: break
        off += tag_len
    return tags

def find_sprite_placing(swf_tags, swf_data, target_cid):
    """Find all DefineSprites that place target_cid."""
    results = []
    for (t, o, l) in swf_tags:
        if t == 39 and l >= 4:
            parent_cid = struct.unpack_from('<H', swf_data, o)[0]
            inner = swf_data[o+4:o+l]
            inner_tags = parse_inner(inner)
            for (tt, body, frame) in inner_tags:
                placed_cid = None
                if tt == 4 and len(body) >= 4:
                    placed_cid = struct.unpack_from('<H', body)[0]
                elif tt == 26 and len(body) >= 5:
                    flags = body[0]; has_char = (flags >> 1) & 1
                    if has_char:
                        placed_cid = struct.unpack_from('<H', body, 3)[0]
                elif tt == 70 and len(body) >= 6:
                    flags1 = body[0]; has_char = (flags1 >> 1) & 1
                    if has_char:
                        placed_cid = struct.unpack_from('<H', body, 4)[0]
                if placed_cid == target_cid:
                    results.append((parent_cid, frame, tt))
    return results

print('\n=== Who places charID=1556 (stance) in OG? ===')
og_places_1556 = find_sprite_placing(og_tags, og_data, 1556)
for parent, frame, tt in og_places_1556:
    print(f'  Parent charID={parent} at frame={frame} via tag_type={tt}')

print('\n=== Who places charID=1556 in RT? ===')
rt_places_1556 = find_sprite_placing(rt_tags, rt_data, 1556)
for parent, frame, tt in rt_places_1556:
    print(f'  Parent charID={parent} at frame={frame} via tag_type={tt}')

# What's the root/main character sprite charID?
# It should be the charID placed in the root timeline
print('\n=== All DefineSprite charIDs in OG ===')
og_sprite_cids = sorted([struct.unpack_from('<H', og_data, o)[0] for (t, o, l) in og_tags if t == 39 and l >= 2])
print(f'Min: {min(og_sprite_cids)}, Max: {max(og_sprite_cids)}, Count: {len(og_sprite_cids)}')
print(f'Last 10: {og_sprite_cids[-10:]}')

# Find SymbolClass entries for charIDs near 1556
for (t, o, l) in og_tags:
    if t == 76:  # SymbolClass
        body = og_data[o:o+l]
        count = struct.unpack_from('<H', body)[0]
        off = 2
        print(f'\n=== SymbolClass entries for charIDs near 1556 (OG) ===')
        for _ in range(count):
            if off + 2 > len(body): break
            cid = struct.unpack_from('<H', body, off)[0]
            off += 2
            # Read null-terminated name
            name_start = off
            while off < len(body) and body[off] != 0:
                off += 1
            name = body[name_start:off].decode('latin-1', errors='replace')
            off += 1  # skip null
            if 1550 <= cid <= 1580 or 'dair' in name.lower() or cid == 0:
                print(f'  charID={cid}: "{name}"')
        break
