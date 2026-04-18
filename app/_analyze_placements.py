"""Compare PlaceObject3+HasImage placements between OG and RT blackmage.
Focus on what characters are placed with HasImage and whether they
reference valid bitmap definitions."""
import struct, zlib, sys, os

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"

def read_swf(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:3] == b'CWS':
        data = b'FWS' + data[3:8] + zlib.decompress(data[8:])
    return data

def parse_tags(data, offset, end=None):
    if end is None: end = len(data)
    tags = []
    while offset < end:
        if offset + 2 > end: break
        hdr = struct.unpack_from('<H', data, offset)[0]
        tt = hdr >> 6; length = hdr & 0x3F; offset += 2
        if length == 0x3F:
            length = struct.unpack_from('<I', data, offset)[0]; offset += 4
        td = data[offset:offset+length]; tags.append((tt, td)); offset += length
        if tt == 0: break
    return tags

def parse_rect(data, bit_off=0):
    byte_i = bit_off // 8; bit_i = bit_off % 8
    nbits = 0
    for i in range(5):
        nbits = (nbits << 1) | ((data[byte_i + (bit_i+i)//8] >> (7-(bit_i+i)%8)) & 1)
    return (5 + nbits * 4 + 7) // 8

def skip_header(data):
    return 8 + parse_rect(data, 64) + 4

def parse_po3(d):
    """Parse PlaceObject3 flags and character ID."""
    if len(d) < 4:
        return None
    flags1 = d[0]
    flags2 = d[1]
    depth = struct.unpack_from('<H', d, 2)[0]
    
    has_clip_actions = flags1 & 0x80
    has_clip_depth = flags1 & 0x40
    has_name = flags1 & 0x20
    has_ratio = flags1 & 0x10
    has_cxform = flags1 & 0x08
    has_matrix = flags1 & 0x04
    has_char = flags1 & 0x02
    is_move = flags1 & 0x01
    
    has_filter = flags2 & 0x01
    has_blend = flags2 & 0x02
    has_cache = flags2 & 0x04
    has_image = flags2 & 0x10
    has_class_name = flags2 & 0x08
    
    char_id = None
    off = 4
    
    # ClassName comes before CharacterId in PO3
    if has_class_name:
        end = d.index(0, off)
        off = end + 1
    
    if has_char:
        char_id = struct.unpack_from('<H', d, off)[0]
        off += 2
    
    return {
        'depth': depth,
        'char_id': char_id,
        'is_move': bool(is_move),
        'has_image': bool(has_image),
        'has_char': bool(has_char),
        'has_matrix': bool(has_matrix),
        'has_cxform': bool(has_cxform),
        'has_name': bool(has_name),
        'has_blend': bool(has_blend),
        'has_filter': bool(has_filter),
    }

def parse_po2(d):
    """Parse PlaceObject2 flags and character ID."""
    if len(d) < 3:
        return None
    flags = d[0]
    depth = struct.unpack_from('<H', d, 1)[0]
    
    has_char = flags & 0x02
    is_move = flags & 0x01
    
    char_id = None
    if has_char:
        char_id = struct.unpack_from('<H', d, 3)[0]
    
    return {
        'depth': depth,
        'char_id': char_id,
        'is_move': bool(is_move),
        'has_image': False,
        'has_char': bool(has_char),
    }

def analyze_sprites(tags, label):
    """Analyze all sprite timelines for bitmap placements."""
    # Collect character type info
    char_types = {}  # cid → type
    bitmap_cids = set()
    shape_cids = set()
    sprite_cids = set()
    
    for t, d in tags:
        if t in (20, 35, 36):  # DefineBitsLossless, JPEG3, Lossless2
            cid = struct.unpack_from('<H', d, 0)[0]
            char_types[cid] = 'bitmap'
            bitmap_cids.add(cid)
        elif t in (2, 22, 32, 83):  # DefineShape variants
            cid = struct.unpack_from('<H', d, 0)[0]
            char_types[cid] = 'shape'
            shape_cids.add(cid)
        elif t == 39:  # DefineSprite
            cid = struct.unpack_from('<H', d, 0)[0]
            char_types[cid] = 'sprite'
            sprite_cids.add(cid)
    
    # Analyze PlaceObject tags in main timeline + all sprites
    all_places = []
    
    # Main timeline
    for t, d in tags:
        if t == 70:
            info = parse_po3(d)
            if info:
                info['context'] = 'main'
                all_places.append(info)
        elif t == 26:
            info = parse_po2(d)
            if info:
                info['context'] = 'main'
                all_places.append(info)
    
    # Inside sprites
    for t, d in tags:
        if t != 39: continue
        if len(d) < 4: continue
        sprite_cid = struct.unpack_from('<H', d, 0)[0]
        inner = parse_tags(d, 4)
        for it, id_ in inner:
            if it == 70:
                info = parse_po3(id_)
                if info:
                    info['context'] = f'sprite_{sprite_cid}'
                    all_places.append(info)
            elif it == 26:
                info = parse_po2(id_)
                if info:
                    info['context'] = f'sprite_{sprite_cid}'
                    all_places.append(info)
    
    # Count placements by type
    bitmap_places = [p for p in all_places if p.get('char_id') and p['char_id'] in bitmap_cids]
    shape_places = [p for p in all_places if p.get('char_id') and p['char_id'] in shape_cids]
    sprite_places = [p for p in all_places if p.get('char_id') and p['char_id'] in sprite_cids]
    unknown_places = [p for p in all_places if p.get('char_id') and p['char_id'] not in char_types]
    has_image_places = [p for p in all_places if p.get('has_image')]
    
    print(f"\n{label} PLACEMENT ANALYSIS:")
    print(f"  Total placements: {len(all_places)}")
    print(f"  Bitmap placements: {len(bitmap_places)} (direct bitmap refs)")
    print(f"  Shape placements: {len(shape_places)}")
    print(f"  Sprite placements: {len(sprite_places)}")
    print(f"  Unknown char placements: {len(unknown_places)}")
    print(f"  HasImage placements: {len(has_image_places)}")
    
    # Show HasImage details
    if has_image_places:
        print(f"\n  HasImage placement details (first 20):")
        for p in has_image_places[:20]:
            cid = p['char_id']
            ctype = char_types.get(cid, 'UNKNOWN')
            print(f"    depth={p['depth']} char={cid} type={ctype} move={p['is_move']} ctx={p['context']}")
    
    # Show bitmap placements WITHOUT HasImage
    bitmap_no_image = [p for p in bitmap_places if not p.get('has_image')]
    if bitmap_no_image:
        print(f"\n  ⚠ Bitmap placements WITHOUT HasImage: {len(bitmap_no_image)}")
        for p in bitmap_no_image[:10]:
            print(f"    depth={p['depth']} char={p['char_id']} move={p['is_move']} ctx={p['context']}")
    
    # Show non-bitmap placements WITH HasImage
    non_bitmap_has_image = [p for p in has_image_places if p.get('char_id') not in bitmap_cids]
    if non_bitmap_has_image:
        print(f"\n  ⚠ Non-bitmap placements WITH HasImage: {len(non_bitmap_has_image)}")
        for p in non_bitmap_has_image[:10]:
            cid = p['char_id']
            ctype = char_types.get(cid, 'UNKNOWN')
            print(f"    depth={p['depth']} char={cid} type={ctype} move={p['is_move']} ctx={p['context']}")
    
    return bitmap_cids, shape_cids, sprite_cids

def main():
    og_data = read_swf(OG)
    rt_data = read_swf(RT)
    og_tags = parse_tags(og_data, skip_header(og_data))
    rt_tags = parse_tags(rt_data, skip_header(rt_data))
    
    print("=== OG ===")
    og_bmps, og_shapes, og_sprites = analyze_sprites(og_tags, "OG")
    print("\n\n=== RT ===")
    rt_bmps, rt_shapes, rt_sprites = analyze_sprites(rt_tags, "RT")

if __name__ == '__main__':
    main()
