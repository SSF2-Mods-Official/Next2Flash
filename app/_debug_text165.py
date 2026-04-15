"""Compare sprite CID 165 (original) vs equivalent RT sprite for text placement."""
import struct, zlib, io, sys
from swf_binary_io import BitReader

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
    """Parse tags from a byte buffer starting at start_pos."""
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

def read_rect(br):
    nb = br.read_ub(5)
    vals = [br.read_sb(nb) for _ in range(4)]
    return vals  # xmin, xmax, ymin, ymax

def read_matrix(br):
    has_scale = br.read_ub(1)
    sx, sy = 1.0, 1.0
    if has_scale:
        nb = br.read_ub(5)
        sx = br.read_sb(nb) / 65536.0
        sy = br.read_sb(nb) / 65536.0
    has_rotate = br.read_ub(1)
    r0, r1 = 0.0, 0.0
    if has_rotate:
        nb = br.read_ub(5)
        r0 = br.read_sb(nb) / 65536.0
        r1 = br.read_sb(nb) / 65536.0
    nb = br.read_ub(5)
    tx = br.read_sb(nb) / 20.0
    ty = br.read_sb(nb) / 20.0
    return {'sx': sx, 'sy': sy, 'r0': r0, 'r1': r1, 'tx': tx, 'ty': ty}

def read_cxform(br, with_alpha):
    has_add = br.read_ub(1)
    has_mult = br.read_ub(1)
    nb = br.read_ub(4)
    mult = [1.0]*4
    add = [0]*4
    if has_mult:
        for i in range(3 if not with_alpha else 4):
            mult[i] = br.read_sb(nb) / 256.0
    if has_add:
        for i in range(3 if not with_alpha else 4):
            add[i] = br.read_sb(nb)
    return {'mult': mult, 'add': add}

def parse_place_object(tag_type, body):
    """Parse PlaceObject2 (26) or PlaceObject3 (70)."""
    br = BitReader(body, 0)
    
    if tag_type == 26:  # PlaceObject2
        has_clip_actions = br.read_ub(1)
        has_clip_depth = br.read_ub(1)
        has_name = br.read_ub(1)
        has_ratio = br.read_ub(1)
        has_color_transform = br.read_ub(1)
        has_matrix = br.read_ub(1)
        has_character = br.read_ub(1)
        flag_move = br.read_ub(1)
        depth = br.read_ui16()
    elif tag_type == 70:  # PlaceObject3
        has_clip_actions = br.read_ub(1)
        has_clip_depth = br.read_ub(1)
        has_name = br.read_ub(1)
        has_ratio = br.read_ub(1)
        has_color_transform = br.read_ub(1)
        has_matrix = br.read_ub(1)
        has_character = br.read_ub(1)
        flag_move = br.read_ub(1)
        # PO3 extra flags
        _reserved = br.read_ub(1)
        _opaque_bg = br.read_ub(1)
        has_visible = br.read_ub(1)
        has_image = br.read_ub(1)
        has_class_name = br.read_ub(1)
        has_cache_as_bitmap = br.read_ub(1)
        has_blend_mode = br.read_ub(1)
        has_filter_list = br.read_ub(1)
        depth = br.read_ui16()
    else:
        return None

    result = {'tag_type': tag_type, 'depth': depth, 'move': flag_move}
    
    if tag_type == 70 and has_class_name:
        # Read null-terminated string
        s = b''
        while True:
            c = br.read_ui8()
            if c == 0: break
            s += bytes([c])
        result['class_name'] = s.decode('utf-8', errors='replace')
    
    if has_character:
        result['char_id'] = br.read_ui16()
    if has_matrix:
        result['matrix'] = read_matrix(br)
    if has_color_transform:
        result['cxform'] = read_cxform(br, True)
    if has_ratio:
        result['ratio'] = br.read_ui16()
    if has_name:
        s = b''
        while True:
            c = br.read_ui8()
            if c == 0: break
            s += bytes([c])
        result['name'] = s.decode('utf-8', errors='replace')
    if has_clip_depth:
        result['clip_depth'] = br.read_ui16()
    
    if tag_type == 70:
        if has_filter_list:
            result['has_filters'] = True
            try:
                from swf_to_n2d import read_filter_list as _rfl
                result['filters_parsed'] = _rfl(br)
            except Exception:
                result['filters_parsed'] = 'PARSE_ERROR'
        try:
            if has_blend_mode:
                result['blend_mode'] = br.read_ui8()
            if has_cache_as_bitmap:
                result['cache_as_bitmap'] = br.read_ui8()
            if has_visible:
                result['visible'] = br.read_ui8()
        except Exception:
            pass
    
    return result

def parse_define_text_bounds(body):
    """Parse DefineText/DefineText2 to extract bounds rect."""
    br = BitReader(body, 0)
    cid = br.read_ui16()
    bounds = read_rect(br)
    br.align()
    matrix = read_matrix(br)
    br.align()
    return cid, bounds, matrix

def find_sprites_and_texts(data, start_pos):
    """Find all DefineSprite and DefineText tags."""
    tags = parse_tags(data, start_pos)
    sprites = {}  # cid -> list of inner tags
    texts = {}    # cid -> (tag_type, bounds, matrix)
    edit_texts = {} # cid -> tag_type
    
    for tt, body in tags:
        if tt == 39:  # DefineSprite
            sprite_cid = struct.unpack_from('<H', body, 0)[0]
            frame_count = struct.unpack_from('<H', body, 2)[0]
            inner_tags = parse_tags(body, 4)
            sprites[sprite_cid] = inner_tags
        elif tt in (11, 33):  # DefineText, DefineText2
            try:
                cid, bounds, matrix = parse_define_text_bounds(body)
                texts[cid] = (tt, bounds, matrix)
            except:
                pass
        elif tt == 37:  # DefineEditText
            cid = struct.unpack_from('<H', body, 0)[0]
            edit_texts[cid] = tt
    
    return sprites, texts, edit_texts

# Parse original SWF
print("=== ORIGINAL SWF ===")
orig_data = read_swf(r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf')
orig_start = parse_swf_header(orig_data)
orig_sprites, orig_texts, orig_edit_texts = find_sprites_and_texts(orig_data, orig_start)

# Info about CID 164 (text)
if 164 in orig_texts:
    tt, bounds, matrix = orig_texts[164]
    print(f"DefineText CID 164: tag={tt} bounds={bounds} matrix={matrix}")
elif 164 in orig_edit_texts:
    print(f"DefineEditText CID 164: tag={orig_edit_texts[164]}")
else:
    print("CID 164 not found as text!")

# Info about sprite CID 165
if 165 in orig_sprites:
    print(f"\nSprite CID 165 inner tags:")
    for tt, body in orig_sprites[165]:
        if tt in (26, 70):
            po = parse_place_object(tt, body)
            if po:
                print(f"  {po}")
        elif tt == 1:
            print(f"  ShowFrame")
        elif tt == 0:
            print(f"  End")
        else:
            print(f"  Tag {tt} len={len(body)}")

# Parse RT SWF
print("\n\n=== ROUNDTRIP SWF ===")
rt_data = read_swf('test_swfs/lloyd_rt.swf')
rt_start = parse_swf_header(rt_data)
rt_sprites, rt_texts, rt_edit_texts = find_sprites_and_texts(rt_data, rt_start)

# Find the RT sprite equivalent to CID 165 
# From the screenshot, RT sprite CID 322 has frame 1 with PlaceObject2 at depths 2,3,6,7
# matching the original's depths 2,3,6,7
print("\nAll RT text characters:")
for cid, (tt, bounds, matrix) in sorted(rt_texts.items()):
    print(f"  DefineText CID {cid}: tag={tt} bounds={bounds} matrix={matrix}")
for cid, tt in sorted(rt_edit_texts.items()):
    print(f"  DefineEditText CID {cid}: tag={tt}")

# Find RT sprite that places at depths 2,3,6,7 like the original 165
print("\nSearching for RT sprite with depths 2,3,6,7...")
for sprite_cid, inner_tags in sorted(rt_sprites.items()):
    depths = set()
    places = []
    for tt, body in inner_tags:
        if tt in (26, 70):
            po = parse_place_object(tt, body)
            if po and 'depth' in po:
                depths.add(po['depth'])
                places.append(po)
    if depths == {2, 3, 6, 7}:
        print(f"\n  RT Sprite CID {sprite_cid} (matching depths):")
        for po in places:
            print(f"    {po}")

# Also look specifically for a sprite that references the text char at depth 7
print("\nRT sprites that reference a text char at depth 7:")
text_cids = set(rt_texts.keys()) | set(rt_edit_texts.keys())
for sprite_cid, inner_tags in sorted(rt_sprites.items()):
    for tt, body in inner_tags:
        if tt in (26, 70):
            po = parse_place_object(tt, body)
            if po and po.get('depth') == 7 and po.get('char_id') in text_cids:
                print(f"  Sprite CID {sprite_cid}: places text CID {po['char_id']} at depth 7")
                print(f"    Full PO: {po}")
