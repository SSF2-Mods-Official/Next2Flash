"""Compare the fox sprite's PlaceObject instance names between OG and RT.
Focus on 'stance' instance which is critical for frame script execution."""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__))

from as3_decompiler.swf_reader import iter_tags

OG_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"
RT_PATH = r"C:\Users\glwex\Documents\GitHub\Next2Flash\app\fox_fresh.swf"


def find_fox_sprite_id(path):
    """Find the charId for 'fox' class via SymbolClass."""
    for tag_code, tag_data in iter_tags(path):
        if tag_code == 76:  # SymbolClass
            count = struct.unpack_from('<H', tag_data, 0)[0]
            pos = 2
            for _ in range(count):
                cid = struct.unpack_from('<H', tag_data, pos)[0]
                pos += 2
                null_idx = tag_data.find(b'\x00', pos)
                name = tag_data[pos:null_idx].decode('utf-8', errors='replace')
                pos = null_idx + 1
                if name == 'fox':
                    return cid
    return None


def parse_sprite_inner_tags(sprite_body):
    """Parse inner tags of a DefineSprite and return frame-by-frame info."""
    inner = sprite_body[4:]  # skip spriteId + frameCount
    pos = 0
    frames = []
    current_frame_tags = []
    current_frame = 0
    
    while pos < len(inner):
        if pos + 2 > len(inner):
            break
        tag_and_len = struct.unpack_from('<H', inner, pos)[0]
        code = tag_and_len >> 6
        length = tag_and_len & 0x3F
        pos += 2
        if length == 0x3F:
            if pos + 4 > len(inner):
                break
            length = struct.unpack_from('<I', inner, pos)[0]
            pos += 4
        body = inner[pos:pos + length]
        pos += length
        
        if code == 0:  # End
            break
        elif code == 1:  # ShowFrame
            frames.append((current_frame, current_frame_tags))
            current_frame += 1
            current_frame_tags = []
        elif code in (4, 26, 70):  # PlaceObject, PlaceObject2, PlaceObject3
            info = parse_place_object(code, body)
            current_frame_tags.append(('place', info))
        elif code in (5, 28):  # RemoveObject, RemoveObject2
            if code == 5 and len(body) >= 4:
                depth = struct.unpack_from('<H', body, 2)[0]
            elif code == 28 and len(body) >= 2:
                depth = struct.unpack_from('<H', body, 0)[0]
            else:
                depth = -1
            current_frame_tags.append(('remove', {'depth': depth}))
        elif code == 43:  # FrameLabel
            null_idx = body.find(b'\x00')
            label = body[:null_idx].decode('utf-8', errors='replace') if null_idx >= 0 else ''
            current_frame_tags.append(('label', label))
    
    return frames


def parse_place_object(code, body):
    """Parse PlaceObject2/3 flags and extract key fields."""
    info = {}
    if code == 4:  # PlaceObject (ancient, unlikely)
        return info

    pos = 0
    if code == 70:  # PlaceObject3
        if len(body) < 4:
            return info
        flags = struct.unpack_from('<H', body, 0)[0]  # 16-bit flags
        pos = 2
        # PlaceObject3 has 16-bit flags
        has_clip_actions = (flags >> 0) & 1
        has_clip_depth = (flags >> 1) & 1
        has_name = (flags >> 2) & 1
        has_ratio = (flags >> 3) & 1
        has_color_transform = (flags >> 4) & 1
        has_matrix = (flags >> 5) & 1
        has_character = (flags >> 6) & 1
        has_move = (flags >> 7) & 1
        # Byte 2 flags
        has_opaque_bg = (flags >> 8) & 1
        has_visible = (flags >> 9) & 1
        has_image = (flags >> 10) & 1
        has_class_name = (flags >> 11) & 1
        has_cache_as_bitmap = (flags >> 12) & 1
        has_blend_mode = (flags >> 13) & 1
        has_filter_list = (flags >> 14) & 1
    else:  # PlaceObject2
        if len(body) < 3:
            return info
        flags = body[0]
        pos = 1
        has_clip_actions = (flags >> 7) & 1
        has_clip_depth = (flags >> 6) & 1
        has_name = (flags >> 5) & 1
        has_ratio = (flags >> 4) & 1
        has_color_transform = (flags >> 3) & 1
        has_matrix = (flags >> 2) & 1
        has_character = (flags >> 1) & 1
        has_move = flags & 1
        has_class_name = 0
        has_blend_mode = 0
        has_filter_list = 0
        has_cache_as_bitmap = 0
        has_visible = 0
        has_opaque_bg = 0
        has_image = 0

    info['has_move'] = bool(has_move)

    # Depth
    if pos + 2 > len(body):
        return info
    depth = struct.unpack_from('<H', body, pos)[0]
    info['depth'] = depth
    pos += 2

    # ClassName (PO3 only)
    if has_class_name:
        null_idx = body.find(b'\x00', pos)
        if null_idx >= 0:
            info['className'] = body[pos:null_idx].decode('utf-8', errors='replace')
            pos = null_idx + 1

    # CharacterID
    if has_character:
        if pos + 2 <= len(body):
            info['charId'] = struct.unpack_from('<H', body, pos)[0]
            pos += 2

    # Matrix (variable length - skip it by parsing MATRIX record)
    if has_matrix:
        pos = skip_matrix(body, pos)

    # ColorTransform
    if has_color_transform:
        pos = skip_cxform_with_alpha(body, pos)

    # Ratio
    if has_ratio:
        if pos + 2 <= len(body):
            info['ratio'] = struct.unpack_from('<H', body, pos)[0]
            pos += 2

    # Name
    if has_name:
        null_idx = body.find(b'\x00', pos)
        if null_idx >= 0:
            info['name'] = body[pos:null_idx].decode('utf-8', errors='replace')
            pos = null_idx + 1

    # ClipDepth
    if has_clip_depth:
        if pos + 2 <= len(body):
            info['clipDepth'] = struct.unpack_from('<H', body, pos)[0]
            pos += 2

    return info


def skip_matrix(data, pos):
    """Skip a MATRIX record (bit-packed)."""
    if pos >= len(data):
        return pos
    bit_pos = pos * 8
    
    # HasScale
    has_scale = read_bits(data, bit_pos, 1)
    bit_pos += 1
    if has_scale:
        n_scale_bits = read_bits(data, bit_pos, 5)
        bit_pos += 5
        bit_pos += n_scale_bits * 2  # ScaleX + ScaleY
    
    # HasRotate
    has_rotate = read_bits(data, bit_pos, 1)
    bit_pos += 1
    if has_rotate:
        n_rotate_bits = read_bits(data, bit_pos, 5)
        bit_pos += 5
        bit_pos += n_rotate_bits * 2  # RotateSkew0 + RotateSkew1
    
    # Translate
    n_translate_bits = read_bits(data, bit_pos, 5)
    bit_pos += 5
    bit_pos += n_translate_bits * 2  # TranslateX + TranslateY
    
    return (bit_pos + 7) // 8  # Round up to byte boundary


def skip_cxform_with_alpha(data, pos):
    """Skip a CXFORMWITHALPHA record (bit-packed)."""
    if pos >= len(data):
        return pos
    bit_pos = pos * 8
    
    has_add = read_bits(data, bit_pos, 1)
    bit_pos += 1
    has_mult = read_bits(data, bit_pos, 1)
    bit_pos += 1
    n_bits = read_bits(data, bit_pos, 4)
    bit_pos += 4
    
    if has_mult:
        bit_pos += n_bits * 4  # R, G, B, A multiply
    if has_add:
        bit_pos += n_bits * 4  # R, G, B, A add
    
    return (bit_pos + 7) // 8


def read_bits(data, bit_offset, count):
    """Read `count` bits from data starting at bit_offset."""
    result = 0
    for i in range(count):
        byte_idx = (bit_offset + i) // 8
        bit_idx = 7 - ((bit_offset + i) % 8)
        if byte_idx < len(data):
            result = (result << 1) | ((data[byte_idx] >> bit_idx) & 1)
    return result


def get_fox_sprite_body(path, fox_id):
    """Get the raw DefineSprite body for the fox sprite."""
    for tag_code, tag_data in iter_tags(path):
        if tag_code == 39:  # DefineSprite
            sprite_id = struct.unpack_from('<H', tag_data, 0)[0]
            if sprite_id == fox_id:
                return tag_data
    return None


def dump_fox_frames(path, label):
    """Dump the fox sprite's frame-by-frame PlaceObject info."""
    fox_id = find_fox_sprite_id(path)
    if fox_id is None:
        print(f"  {label}: 'fox' sprite not found in SymbolClass!")
        return None
    print(f"  {label}: fox charId = {fox_id}")
    
    body = get_fox_sprite_body(path, fox_id)
    if body is None:
        print(f"  {label}: fox DefineSprite not found!")
        return None
    
    frame_count = struct.unpack_from('<H', body, 2)[0]
    print(f"  {label}: {frame_count} frames")
    
    frames = parse_sprite_inner_tags(body)
    return frames


def main():
    print("=== FOX SPRITE INSTANCE NAME COMPARISON ===\n")
    
    print("OG:", OG_PATH)
    og_frames = dump_fox_frames(OG_PATH, "OG")
    
    print("\nRT:", RT_PATH)
    rt_frames = dump_fox_frames(RT_PATH, "RT")
    
    if og_frames is None or rt_frames is None:
        return
    
    print(f"\nOG frame count: {len(og_frames)}, RT frame count: {len(rt_frames)}")
    
    # Compare frame by frame - focus on instance names
    max_frames = max(len(og_frames), len(rt_frames))
    
    diffs = 0
    for i in range(max_frames):
        og_f = og_frames[i] if i < len(og_frames) else None
        rt_f = rt_frames[i] if i < len(rt_frames) else None
        
        if og_f is None or rt_f is None:
            print(f"\n  Frame {i+1}: {'MISSING IN OG' if og_f is None else 'MISSING IN RT'}")
            diffs += 1
            continue
        
        og_frame_idx, og_tags = og_f
        rt_frame_idx, rt_tags = rt_f
        
        # Extract instance names from place tags
        og_names = {}
        for tag_type, info in og_tags:
            if tag_type == 'place' and 'name' in info:
                og_names[info.get('depth', -1)] = info['name']
        
        rt_names = {}
        for tag_type, info in rt_tags:
            if tag_type == 'place' and 'name' in info:
                rt_names[info.get('depth', -1)] = info['name']
        
        # Check for 'stance' specifically
        og_stance = [d for d, n in og_names.items() if n == 'stance']
        rt_stance = [d for d, n in rt_names.items() if n == 'stance']
        
        # Compare place tags
        og_places = [(info.get('depth'), info.get('charId'), info.get('name'), info.get('has_move'))
                     for tag_type, info in og_tags if tag_type == 'place']
        rt_places = [(info.get('depth'), info.get('charId'), info.get('name'), info.get('has_move'))
                     for tag_type, info in rt_tags if tag_type == 'place']
        
        og_removes = [info.get('depth') for tag_type, info in og_tags if tag_type == 'remove']
        rt_removes = [info.get('depth') for tag_type, info in rt_tags if tag_type == 'remove']
        
        og_labels = [l for tag_type, l in og_tags if tag_type == 'label']
        rt_labels = [l for tag_type, l in rt_tags if tag_type == 'label']
        
        # Check for differences
        has_diff = False
        
        if og_labels != rt_labels:
            has_diff = True
        
        # Compare names (ignoring charIds which differ)
        og_name_set = {(d, n) for d, n in og_names.items()}
        rt_name_set = {(d, n) for d, n in rt_names.items()}
        if og_name_set != rt_name_set:
            has_diff = True
        
        # Compare remove operations
        if sorted(og_removes) != sorted(rt_removes):
            has_diff = True
        
        # Compare place count / depth structure  
        og_place_depths = sorted(set(d for d, c, n, m in og_places))
        rt_place_depths = sorted(set(d for d, c, n, m in rt_places))
        if og_place_depths != rt_place_depths:
            has_diff = True
            
        if has_diff:
            diffs += 1
            print(f"\n  Frame {i+1} (0-indexed: {i}):")
            if og_labels or rt_labels:
                print(f"    Labels: OG={og_labels} RT={rt_labels}")
            if og_places or rt_places:
                for d, c, n, m in og_places:
                    rt_match = [x for x in rt_places if x[0] == d]
                    marker = ""
                    if not rt_match:
                        marker = " *** NOT IN RT"
                    elif rt_match[0][2] != n:
                        marker = f" *** RT name={rt_match[0][2]}"
                    print(f"    OG Place: depth={d} charId={c} name={n} move={m}{marker}")
                for d, c, n, m in rt_places:
                    og_match = [x for x in og_places if x[0] == d]
                    if not og_match:
                        print(f"    RT Place: depth={d} charId={c} name={n} move={m} *** NOT IN OG")
            if og_removes or rt_removes:
                if sorted(og_removes) != sorted(rt_removes):
                    print(f"    Removes: OG={sorted(og_removes)} RT={sorted(rt_removes)}")
    
    print(f"\n=== SUMMARY: {diffs} frames with differences out of {max_frames} ===")


if __name__ == '__main__':
    main()
