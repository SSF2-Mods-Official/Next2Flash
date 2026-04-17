"""Compare fox main MC stance placement between OG and RT SWF at the tag level.

For each frame of the main fox MC, shows:
- What children are placed (instance name, depth, characterId)
- Frame labels
- Whether "stance" child exists and its characterId
- Frame counts of referenced stance sprites
"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__))
from swf_to_n2d import parse_swf

OG_SWF = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"
RT_SWF = r"C:\Users\glwex\Documents\GitHub\Next2Flash\app\fox_fresh.swf"

TAG_DEFINESPRITE = 39
TAG_PLACEOBJECT2 = 26
TAG_PLACEOBJECT3 = 70
TAG_REMOVEOBJECT2 = 28
TAG_SHOWFRAME = 1
TAG_FRAMELABEL = 43
TAG_END = 0
TAG_SYMBOLCLASS = 76


def parse_place_object(tag_type, data):
    """Parse PlaceObject2/3 to extract placement info."""
    if not data:
        return None
    
    pos = 0
    if tag_type == TAG_PLACEOBJECT2:
        flags = data[pos]; pos += 1
        has_clip_actions = bool(flags & 0x80)
        has_clip_depth = bool(flags & 0x40)
        has_name = bool(flags & 0x20)
        has_ratio = bool(flags & 0x10)
        has_color_transform = bool(flags & 0x08)
        has_matrix = bool(flags & 0x04)
        has_character = bool(flags & 0x02)
        flag_move = bool(flags & 0x01)
        
        depth = struct.unpack_from('<H', data, pos)[0]; pos += 2
        
        character_id = None
        if has_character:
            character_id = struct.unpack_from('<H', data, pos)[0]; pos += 2
        
        # Skip matrix
        if has_matrix:
            from swf_to_n2d import BitReader
            br = BitReader(data, pos)
            if br.read_bits(1):  # has scale
                n = br.read_bits(5)
                br.read_sbits(n)
                br.read_sbits(n)
            if br.read_bits(1):  # has rotate
                n = br.read_bits(5)
                br.read_sbits(n)
                br.read_sbits(n)
            n = br.read_bits(5)
            br.read_sbits(n)
            br.read_sbits(n)
            pos = br.byte_pos
        
        # Skip color transform
        if has_color_transform:
            from swf_to_n2d import BitReader
            br = BitReader(data, pos)
            has_add = br.read_bits(1)
            has_mult = br.read_bits(1)
            nbits = br.read_bits(4)
            if has_mult:
                for _ in range(4):
                    br.read_sbits(nbits)
            if has_add:
                for _ in range(4):
                    br.read_sbits(nbits)
            pos = br.byte_pos
        
        if has_ratio:
            pos += 2
        
        name = None
        if has_name:
            end = data.index(0, pos)
            name = data[pos:end].decode('utf-8', errors='replace')
            pos = end + 1
        
        return {
            'depth': depth,
            'character_id': character_id,
            'name': name,
            'move': flag_move,
            'has_matrix': has_matrix,
            'has_color_transform': has_color_transform,
        }
    
    elif tag_type == TAG_PLACEOBJECT3:
        flags1 = data[pos]; pos += 1
        flags2 = data[pos]; pos += 1
        
        has_clip_actions = bool(flags1 & 0x80)
        has_clip_depth = bool(flags1 & 0x40)
        has_name = bool(flags1 & 0x20)
        has_ratio = bool(flags1 & 0x10)
        has_color_transform = bool(flags1 & 0x08)
        has_matrix = bool(flags1 & 0x04)
        has_character = bool(flags1 & 0x02)
        flag_move = bool(flags1 & 0x01)
        
        has_filter_list = bool(flags2 & 0x01)
        has_blend_mode = bool(flags2 & 0x02)
        has_cache_as_bitmap = bool(flags2 & 0x04)
        has_class_name = bool(flags2 & 0x08)
        has_image = bool(flags2 & 0x10)
        has_visible = bool(flags2 & 0x20)
        
        depth = struct.unpack_from('<H', data, pos)[0]; pos += 2
        
        # class name (before character id in PO3)
        class_name = None
        if has_class_name or (has_image and has_character):
            end = data.index(0, pos)
            class_name = data[pos:end].decode('utf-8', errors='replace')
            pos = end + 1
        
        character_id = None
        if has_character:
            character_id = struct.unpack_from('<H', data, pos)[0]; pos += 2
        
        # Skip matrix
        if has_matrix:
            from swf_to_n2d import BitReader
            br = BitReader(data, pos)
            if br.read_bits(1):
                n = br.read_bits(5)
                br.read_sbits(n)
                br.read_sbits(n)
            if br.read_bits(1):
                n = br.read_bits(5)
                br.read_sbits(n)
                br.read_sbits(n)
            n = br.read_bits(5)
            br.read_sbits(n)
            br.read_sbits(n)
            pos = br.byte_pos
        
        # Skip color transform
        if has_color_transform:
            from swf_to_n2d import BitReader
            br = BitReader(data, pos)
            has_add = br.read_bits(1)
            has_mult = br.read_bits(1)
            nbits = br.read_bits(4)
            if has_mult:
                for _ in range(4):
                    br.read_sbits(nbits)
            if has_add:
                for _ in range(4):
                    br.read_sbits(nbits)
            pos = br.byte_pos
        
        if has_ratio:
            pos += 2
        
        name = None
        if has_name:
            end = data.index(0, pos)
            name = data[pos:end].decode('utf-8', errors='replace')
            pos = end + 1
        
        return {
            'depth': depth,
            'character_id': character_id,
            'name': name,
            'class_name': class_name,
            'move': flag_move,
            'has_matrix': has_matrix,
            'has_color_transform': has_color_transform,
        }
    
    return None


def get_sprite_tags(swf_tags, sprite_char_id):
    """Get inner tags of a DefineSprite by character ID."""
    for tag_type, data in swf_tags:
        if tag_type == TAG_DEFINESPRITE and len(data) >= 4:
            cid = struct.unpack_from('<H', data, 0)[0]
            if cid == sprite_char_id:
                # Parse inner tags
                frame_count = struct.unpack_from('<H', data, 2)[0]
                inner_tags = []
                pos = 4
                while pos < len(data):
                    if pos + 2 > len(data):
                        break
                    tag_code_and_len = struct.unpack_from('<H', data, pos)[0]
                    inner_type = tag_code_and_len >> 6
                    inner_len = tag_code_and_len & 0x3F
                    pos += 2
                    if inner_len == 0x3F:
                        if pos + 4 > len(data):
                            break
                        inner_len = struct.unpack_from('<I', data, pos)[0]
                        pos += 4
                    inner_data = data[pos:pos+inner_len]
                    pos += inner_len
                    inner_tags.append((inner_type, inner_data))
                    if inner_type == TAG_END:
                        break
                return frame_count, inner_tags
    return None, None


def get_symbol_class(swf_tags):
    """Get SymbolClass mapping: char_id → class_name."""
    for tag_type, data in swf_tags:
        if tag_type == TAG_SYMBOLCLASS and len(data) >= 2:
            num = struct.unpack_from('<H', data, 0)[0]
            pos = 2
            mapping = {}
            for _ in range(num):
                cid = struct.unpack_from('<H', data, pos)[0]; pos += 2
                end = data.index(0, pos)
                name = data[pos:end].decode('utf-8', errors='replace')
                pos = end + 1
                mapping[cid] = name
            return mapping
    return {}


def analyze_fox_mc(swf_path, label="SWF"):
    """Analyze the fox MC's per-frame stance structure."""
    print(f"\n{'='*60}")
    print(f"Analyzing: {label}")
    print(f"File: {swf_path}")
    print(f"{'='*60}")
    
    with open(swf_path, 'rb') as f:
        swf_data = f.read()
    
    header, tags_raw = parse_swf(swf_data)
    
    # Convert to (type, data) tuples
    tags = []
    for t in tags_raw:
        tags.append((t.tag_type, t.data))
    
    # Get symbol class mapping
    sym_map = get_symbol_class(tags)
    rev_sym = {v: k for k, v in sym_map.items()}
    
    # Find the main fox sprite ID
    fox_cid = rev_sym.get('fox')
    if fox_cid is None:
        print("ERROR: 'fox' not found in SymbolClass!")
        return None
    
    print(f"\nMain fox MC: charId={fox_cid}")
    
    # Get fox MC inner tags
    frame_count, inner_tags = get_sprite_tags(tags, fox_cid)
    if inner_tags is None:
        print("ERROR: fox sprite not found!")
        return None
    
    print(f"Frame count: {frame_count}")
    
    # Build per-frame data
    frames = []
    current_frame = {'placements': {}, 'removes': [], 'label': None, 'raw_tags': []}
    
    for tt, td in inner_tags:
        if tt == TAG_SHOWFRAME:
            frames.append(current_frame)
            current_frame = {'placements': {}, 'removes': [], 'label': None, 'raw_tags': []}
        elif tt in (TAG_PLACEOBJECT2, TAG_PLACEOBJECT3):
            po = parse_place_object(tt, td)
            if po:
                current_frame['placements'][po['depth']] = po
                current_frame['raw_tags'].append(('PO', po))
        elif tt == TAG_REMOVEOBJECT2:
            if len(td) >= 2:
                depth = struct.unpack_from('<H', td, 0)[0]
                current_frame['removes'].append(depth)
                current_frame['raw_tags'].append(('RO', depth))
        elif tt == TAG_FRAMELABEL:
            end = td.index(0)
            label_name = td[:end].decode('utf-8', errors='replace')
            current_frame['label'] = label_name
        elif tt == TAG_END:
            break
    
    # Build display list state per frame
    display_list = {}  # depth → placement info
    frame_data = []
    
    for i, frame in enumerate(frames):
        if frame['label']:
            pass  # labels tracked per frame
        
        # Apply removes
        for depth in frame['removes']:
            display_list.pop(depth, None)
        
        # Apply placements
        for depth, po in frame['placements'].items():
            if po['move'] and not po['character_id']:
                # Move only — keep existing character_id
                if depth in display_list:
                    existing = display_list[depth].copy()
                    existing.update({k: v for k, v in po.items() if v is not None and k != 'character_id'})
                    display_list[depth] = existing
                else:
                    display_list[depth] = po
            else:
                display_list[depth] = po
        
        # Record frame state
        stance_info = None
        for depth, info in sorted(display_list.items()):
            if info.get('name') == 'stance':
                stance_info = info
        
        frame_data.append({
            'frame_num': i + 1,
            'label': frame['label'],
            'stance': stance_info,
            'display_list': dict(display_list),
            'num_children': len(display_list),
        })
    
    # Build sprite frame count map
    sprite_frames = {}
    for tag_type, data in tags:
        if tag_type == TAG_DEFINESPRITE and len(data) >= 4:
            cid = struct.unpack_from('<H', data, 0)[0]
            fc = struct.unpack_from('<H', data, 2)[0]
            sprite_frames[cid] = fc
    
    # Print results
    print(f"\nTotal frames: {len(frame_data)}")
    print(f"\n{'Frame':>5} {'Label':<20} {'#Kids':>5} {'Stance Depth':>12} {'Stance CID':>10} {'Stance Class':>35} {'Stance Frames':>13}")
    print("-" * 110)
    
    for fd in frame_data:
        stance = fd['stance']
        if stance:
            scid = stance.get('character_id', '?')
            sclass = sym_map.get(scid, '?') if isinstance(scid, int) else '?'
            sframes = sprite_frames.get(scid, '?') if isinstance(scid, int) else '?'
            sdepth = stance.get('depth', '?')
        else:
            scid = '-'
            sclass = '-'
            sframes = '-'
            sdepth = '-'
        
        label = fd['label'] or ''
        print(f"{fd['frame_num']:>5} {label:<20} {fd['num_children']:>5} {str(sdepth):>12} {str(scid):>10} {str(sclass):>35} {str(sframes):>13}")
    
    return frame_data, sym_map, sprite_frames


def compare():
    og_data, og_sym, og_sframes = analyze_fox_mc(OG_SWF, "ORIGINAL")
    rt_data, rt_sym, rt_sframes = analyze_fox_mc(RT_SWF, "ROUND-TRIP")
    
    if og_data is None or rt_data is None:
        return
    
    print(f"\n{'='*60}")
    print("COMPARISON")
    print(f"{'='*60}")
    
    if len(og_data) != len(rt_data):
        print(f"FRAME COUNT MISMATCH: OG={len(og_data)} RT={len(rt_data)}")
    
    diffs = 0
    for i in range(min(len(og_data), len(rt_data))):
        og_f = og_data[i]
        rt_f = rt_data[i]
        
        issues = []
        
        if og_f['label'] != rt_f['label']:
            issues.append(f"LABEL: OG='{og_f['label']}' RT='{rt_f['label']}'")
        
        og_s = og_f['stance']
        rt_s = rt_f['stance']
        
        if og_s and not rt_s:
            issues.append("STANCE: missing in RT")
        elif not og_s and rt_s:
            issues.append("STANCE: extra in RT")
        elif og_s and rt_s:
            if og_s.get('depth') != rt_s.get('depth'):
                issues.append(f"STANCE DEPTH: OG={og_s['depth']} RT={rt_s['depth']}")
            
            og_cid = og_s.get('character_id')
            rt_cid = rt_s.get('character_id')
            
            # Compare by class name (CIDs may differ)
            og_class = og_sym.get(og_cid, '?') if og_cid else None
            rt_class = rt_sym.get(rt_cid, '?') if rt_cid else None
            
            if og_class != rt_class:
                issues.append(f"STANCE CLASS: OG='{og_class}' RT='{rt_class}'")
            
            # Compare frame counts
            og_fc = og_sframes.get(og_cid, '?') if og_cid else None
            rt_fc = rt_sframes.get(rt_cid, '?') if rt_cid else None
            if og_fc != rt_fc:
                issues.append(f"STANCE FRAMES: OG={og_fc} RT={rt_fc}")
        
        if og_f['num_children'] != rt_f['num_children']:
            issues.append(f"CHILDREN: OG={og_f['num_children']} RT={rt_f['num_children']}")
        
        if issues:
            diffs += 1
            label = og_f['label'] or ''
            print(f"\nFrame {i+1} ({label}):")
            for iss in issues:
                print(f"  - {iss}")
    
    if diffs == 0:
        print("\nNo differences found in fox MC stance structure!")
    else:
        print(f"\n{diffs} frames with differences")


if __name__ == '__main__':
    compare()
