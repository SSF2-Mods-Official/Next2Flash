"""Verify charID=1001 LL2 pixel data identity + analyze Sprite 1556 parent structure."""
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

og_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'
rt_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'
og_tags, og_data = read_swf_tags(og_path)
rt_tags, rt_data = read_swf_tags(rt_path)

# === Verify charID=1001 pixel data ===
for label, tags, data in [('OG', og_tags, og_data), ('RT', rt_tags, rt_data)]:
    for (t, o, l) in tags:
        if t == 36 and l >= 7:
            cid = struct.unpack_from('<H', data, o)[0]
            if cid == 1001:
                body = data[o:o+l]
                cid_f, fmt, w, h = struct.unpack_from('<HBHH', body)
                compressed = body[7:]
                decompressed = zlib.decompress(compressed)
                print(f'{label} charID=1001: w={w} h={h} fmt={fmt} compressed_len={len(compressed)} decompressed_len={len(decompressed)}')
                print(f'  Expected decompressed: {w*h*4}')
                print(f'  Decompressed hex: {decompressed[:20].hex()}')
                print(f'  Valid: {len(decompressed) == w*h*4}')

# === Compare OG vs RT pixel data for charID=1001 ===
def get_bm(tags, data, cid_target):
    for (t, o, l) in tags:
        if t == 36 and l >= 7:
            cid = struct.unpack_from('<H', data, o)[0]
            if cid == cid_target:
                body = data[o:o+l]
                return body
    return None

og_bm = get_bm(og_tags, og_data, 1001)
rt_bm = get_bm(rt_tags, rt_data, 1001)
og_px = zlib.decompress(og_bm[7:])
rt_px = zlib.decompress(rt_bm[7:])
print(f'\nPixel data identical: {og_px == rt_px}')
if og_px != rt_px:
    print(f'OG: {og_px.hex()}')
    print(f'RT: {rt_px.hex()}')

# === Analyze Sprite 1556 (grandparent of bm_dairHand) ===
SHOW_FRAME = 1
END_TAG = 0

def parse_sprite_inner_tags(inner_data):
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
            raw = struct.unpack_from('<i', inner_data, off)[0]
            tag_len = raw
            if tag_len < 0 or off + 4 + tag_len > len(inner_data) + 100:
                break
            off += 4
        if tag_len < 0 or off + tag_len > len(inner_data):
            break
        body = inner_data[off:off+tag_len]
        tags.append((tag_type, body, frame))
        if tag_type == SHOW_FRAME:
            frame += 1
        elif tag_type == END_TAG:
            break
        off += tag_len
    return tags

def get_sprite_inner(tags, data, cid):
    for (t, o, l) in tags:
        if t == 39 and l >= 4:
            c = struct.unpack_from('<H', data, o)[0]
            if c == cid:
                return data[o+4:o+l]
    return None

def get_place_charids(inner_tags):
    """Get all (frame, depth, charID) placements from inner tags."""
    placements = []
    for (tt, body, frame) in inner_tags:
        if tt == 4 and len(body) >= 4:  # PlaceObject
            cid = struct.unpack_from('<H', body)[0]
            depth = struct.unpack_from('<H', body, 2)[0]
            placements.append((frame, depth, cid))
        elif tt == 26 and len(body) >= 4:  # PlaceObject2
            flags = struct.unpack_from('<H', body)[0]
            has_char = (flags >> 1) & 1
            depth = struct.unpack_from('<H', body, 2)[0]
            if has_char and len(body) >= 5:
                cid = struct.unpack_from('<H', body, 4)[0]
                placements.append((frame, depth, cid))
        elif tt == 70 and len(body) >= 6:  # PlaceObject3
            flags1 = body[0]
            has_char = (flags1 >> 1) & 1
            depth = struct.unpack_from('<H', body, 2)[0]
            if has_char and len(body) >= 6:
                cid = struct.unpack_from('<H', body, 4)[0]
                placements.append((frame, depth, cid))
    return placements

print('\n=== Sprite 1556 (grandparent of bm_dairHand) ===')
og_1556 = get_sprite_inner(og_tags, og_data, 1556)
rt_1556 = get_sprite_inner(rt_tags, rt_data, 1556)
if og_1556 and rt_1556:
    print(f'OG len={len(og_1556)} RT len={len(rt_1556)} identical={og_1556==rt_1556}')
    og_1556_tags = parse_sprite_inner_tags(og_1556)
    rt_1556_tags = parse_sprite_inner_tags(rt_1556)
    og_places = get_place_charids(og_1556_tags)
    rt_places = get_place_charids(rt_1556_tags)
    # Find where charID=1471 is placed
    og_1471_frames = [(f, d) for (f, d, c) in og_places if c == 1471]
    rt_1471_frames = [(f, d) for (f, d, c) in rt_places if c == 1471]
    print(f'OG: charID=1471 placed at frames/depths: {og_1471_frames[:10]}')
    print(f'RT: charID=1471 placed at frames/depths: {rt_1471_frames[:10]}')
    print(f'OG total placements: {len(og_places)}, RT: {len(rt_places)}')
    print(f'OG total frames: {max((f for f,d,c in og_places), default=0)+1}')
    print(f'RT total frames: {max((f for f,d,c in rt_places), default=0)+1}')

# How many frames in each parent sprite
print('\n=== Frame count comparison for key sprites ===')
for cid in [1471, 1556]:
    og_inner = get_sprite_inner(og_tags, og_data, cid)
    rt_inner = get_sprite_inner(rt_tags, rt_data, cid)
    if og_inner and rt_inner:
        og_fc = struct.unpack_from('<H', og_inner[:2])[0] if len(og_inner) >= 2 else '?'
        rt_fc = struct.unpack_from('<H', rt_inner[:2])[0] if len(rt_inner) >= 2 else '?'
        print(f'Sprite {cid}: OG frameCount={og_fc} RT frameCount={rt_fc}')
