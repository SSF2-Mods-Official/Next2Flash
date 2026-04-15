"""Compare masks in OG vs RT SWF sprites — check clip_depth (masks) propagation."""
import struct, zlib, io
from swf_binary_io import BitReader

OG_PATH = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf'
RT_PATH = 'test_swfs/lloyd_rt.swf'

def read_swf(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:3] == b'CWS':
        flen = struct.unpack_from('<I', data, 4)[0]
        body = zlib.decompress(data[8:])
        data = b'FWS' + data[3:8] + body[:flen-8]
    elif data[:3] == b'ZWS':
        import lzma
        flen = struct.unpack_from('<I', data, 4)[0]
        body = lzma.decompress(data[12:])
        data = b'FWS' + data[3:8] + body[:flen-8]
    return data

def parse_tags(data, start_pos):
    pos = start_pos
    tags = []
    while pos < len(data):
        if pos + 2 > len(data): break
        hdr = struct.unpack_from('<H', data, pos)[0]
        tt = hdr >> 6
        tl = hdr & 0x3F
        if tl == 0x3F:
            tl = struct.unpack_from('<I', data, pos+2)[0]
            body_start = pos + 6
        else:
            body_start = pos + 2
        body = data[body_start:body_start+tl]
        tags.append((tt, body))
        pos = body_start + tl
        if tt == 0: break
    return tags

def parse_swf_header(data):
    br = BitReader(data, 8)
    nb = br.read_ub(5)
    for _ in range(4): br.read_sb(nb)
    br.align()
    br.read_ui8(); br.read_ui8(); br.read_ui16()
    return br.byte_pos

def parse_po(tag_type, body):
    """Parse PlaceObject2/3 — extract depth, charId, clipDepth."""
    br = BitReader(body, 0)
    if tag_type == 26:
        has_clip_actions = br.read_ub(1)
        has_clip_depth = br.read_ub(1)
        has_name = br.read_ub(1)
        has_ratio = br.read_ub(1)
        has_cx = br.read_ub(1)
        has_matrix = br.read_ub(1)
        has_char = br.read_ub(1)
        is_move = br.read_ub(1)
        depth = br.read_ui16()
    elif tag_type == 70:
        has_clip_actions = br.read_ub(1)
        has_clip_depth = br.read_ub(1)
        has_name = br.read_ub(1)
        has_ratio = br.read_ub(1)
        has_cx = br.read_ub(1)
        has_matrix = br.read_ub(1)
        has_char = br.read_ub(1)
        is_move = br.read_ub(1)
        _r = br.read_ub(1); _o = br.read_ub(1)
        _vis = br.read_ub(1); _img = br.read_ub(1)
        has_class = br.read_ub(1); _cab = br.read_ub(1)
        _bm = br.read_ub(1); _fl = br.read_ub(1)
        depth = br.read_ui16()
        if has_class:
            while br.read_ui8() != 0: pass
    else:
        return None
    
    char_id = None
    if has_char:
        char_id = br.read_ui16()
    
    # Skip matrix
    if has_matrix:
        if br.read_ub(1):  # has_scale
            nb2 = br.read_ub(5)
            br.read_sb(nb2); br.read_sb(nb2)
        if br.read_ub(1):  # has_rotate
            nb2 = br.read_ub(5)
            br.read_sb(nb2); br.read_sb(nb2)
        nb2 = br.read_ub(5)
        br.read_sb(nb2); br.read_sb(nb2)
        br.align()
    
    # Skip colorTransform
    if has_cx:
        has_add = br.read_ub(1)
        has_mult = br.read_ub(1)
        nb = br.read_ub(4)
        if has_mult:
            for _ in range(4): br.read_sb(nb)
        if has_add:
            for _ in range(4): br.read_sb(nb)
        br.align()
    
    if has_ratio:
        br.read_ui16()
    if has_name:
        while br.read_ui8() != 0: pass
    
    clip_depth = None
    if has_clip_depth:
        clip_depth = br.read_ui16()
    
    return {
        'depth': depth, 'char_id': char_id, 'clip_depth': clip_depth,
        'is_move': is_move, 'tag_type': tag_type,
    }

def analyze_sprites(data, start_pos, label):
    tags = parse_tags(data, start_pos)
    sprites = {}
    for tt, body in tags:
        if tt == 39:
            cid = struct.unpack_from('<H', body, 0)[0]
            inner = parse_tags(body, 4)
            sprites[cid] = inner
    
    # Count sprites with masks
    mask_sprites = {}
    for cid, inner in sorted(sprites.items()):
        has_mask = False
        frame = 1
        for tt, body in inner:
            if tt in (26, 70):
                po = parse_po(tt, body)
                if po and po['clip_depth'] is not None:
                    has_mask = True
                    if cid not in mask_sprites:
                        mask_sprites[cid] = []
                    mask_sprites[cid].append((frame, po))
            elif tt == 1:
                frame += 1
    
    print(f"\n=== {label}: {len(sprites)} sprites, {len(mask_sprites)} with masks ===")
    for cid, entries in sorted(mask_sprites.items()):
        places_str = ', '.join(
            f"f{f}:d{po['depth']}->cd{po['clip_depth']}(cid={po['char_id']})"
            for f, po in entries
        )
        print(f"  Sprite {cid}: {places_str}")
    
    return sprites, mask_sprites

og_data = read_swf(OG_PATH)
og_start = parse_swf_header(og_data)
og_sprites, og_masks = analyze_sprites(og_data, og_start, "ORIGINAL")

rt_data = read_swf(RT_PATH)
rt_start = parse_swf_header(rt_data)
rt_sprites, rt_masks = analyze_sprites(rt_data, rt_start, "ROUNDTRIP")
