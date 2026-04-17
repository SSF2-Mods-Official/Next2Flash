"""Compare the fox main MC's DefineSprite tag data between OG and RT SWFs.

Instead of manually parsing PlaceObject, uses the existing swf_to_n2d 
infrastructure to extract and compare sprite data.
"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__))
from swf_to_n2d import parse_swf

OG_SWF = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"
RT_SWF = r"C:\Users\glwex\Documents\GitHub\Next2Flash\app\fox_fresh.swf"

TAG_DEFINESPRITE = 39
TAG_SYMBOLCLASS = 76
TAG_SHOWFRAME = 1
TAG_FRAMELABEL = 43
TAG_END = 0
TAG_PLACEOBJECT2 = 26
TAG_PLACEOBJECT3 = 70
TAG_REMOVEOBJECT2 = 28


def get_swf_tags(swf_path):
    """Parse SWF and return list of (tag_type, data) tuples."""
    with open(swf_path, 'rb') as f:
        swf_data = f.read()
    header, tags_raw = parse_swf(swf_data)
    return [(t.tag_type, t.data) for t in tags_raw]


def get_symbol_class(tags):
    result = {}
    for tt, td in tags:
        if tt == TAG_SYMBOLCLASS and len(td) >= 2:
            num = struct.unpack_from('<H', td, 0)[0]
            pos = 2
            for _ in range(num):
                cid = struct.unpack_from('<H', td, pos)[0]; pos += 2
                end = td.index(0, pos)
                name = td[pos:end].decode('utf-8', errors='replace')
                pos = end + 1
                result[cid] = name
                result[name] = cid
    return result


def get_sprite_inner_tags(tags, sprite_cid):
    """Get inner tags as list of (type, data) from a DefineSprite."""
    for tt, td in tags:
        if tt == TAG_DEFINESPRITE and len(td) >= 4:
            cid = struct.unpack_from('<H', td, 0)[0]
            if cid != sprite_cid:
                continue
            fc = struct.unpack_from('<H', td, 2)[0]
            inner = []
            pos = 4
            while pos < len(td):
                if pos + 2 > len(td):
                    break
                tag_code_and_len = struct.unpack_from('<H', td, pos)[0]
                inner_type = tag_code_and_len >> 6
                inner_len = tag_code_and_len & 0x3F
                pos += 2
                if inner_len == 0x3F:
                    if pos + 4 > len(td):
                        break
                    inner_len = struct.unpack_from('<I', td, pos)[0]
                    pos += 4
                inner_data = td[pos:pos+inner_len]
                pos += inner_len
                inner.append((inner_type, inner_data))
                if inner_type == TAG_END:
                    break
            return fc, inner
    return None, None


def basic_place_object_info(tag_type, data):
    """Get just the depth, character_id, and name from a PlaceObject2/3."""
    if not data:
        return None
    pos = 0
    if tag_type == TAG_PLACEOBJECT2:
        flags = data[pos]; pos += 1
        has_name = bool(flags & 0x20)
        has_ratio = bool(flags & 0x10)
        has_color_transform = bool(flags & 0x08)
        has_matrix = bool(flags & 0x04)
        has_character = bool(flags & 0x02)
        flag_move = bool(flags & 0x01)
        depth = struct.unpack_from('<H', data, pos)[0]; pos += 2
        character_id = struct.unpack_from('<H', data, pos)[0] if has_character else None
        # We can't easily get the name without skipping matrix and cxform, 
        # so return what we have
        return {'depth': depth, 'cid': character_id, 'move': flag_move, 'tag_type': 'PO2', 'raw_len': len(data)}
    elif tag_type == TAG_PLACEOBJECT3:
        flags1 = data[pos]; pos += 1
        flags2 = data[pos]; pos += 1
        has_name = bool(flags1 & 0x20)
        has_character = bool(flags1 & 0x02)
        flag_move = bool(flags1 & 0x01)
        has_class_name = bool(flags2 & 0x08)
        has_image = bool(flags2 & 0x10)
        depth = struct.unpack_from('<H', data, pos)[0]; pos += 2
        if has_class_name or (has_image and has_character):
            end = data.index(0, pos)
            pos = end + 1
        character_id = struct.unpack_from('<H', data, pos)[0] if has_character else None
        return {'depth': depth, 'cid': character_id, 'move': flag_move, 'tag_type': 'PO3', 'raw_len': len(data)}
    return None


def analyze_sprite_frames(inner_tags, sym_map=None):
    """Group inner tags by frame, show tag types per frame."""
    frames = []
    current = {'label': None, 'tags': []}
    for tt, td in inner_tags:
        if tt == TAG_SHOWFRAME:
            frames.append(current)
            current = {'label': None, 'tags': []}
        elif tt == TAG_FRAMELABEL:
            end = td.index(0)
            current['label'] = td[:end].decode('utf-8', errors='replace')
        elif tt in (TAG_PLACEOBJECT2, TAG_PLACEOBJECT3):
            info = basic_place_object_info(tt, td)
            if info:
                class_name = sym_map.get(info['cid'], '') if sym_map and info['cid'] else ''
                current['tags'].append(f"{'MOVE' if info['move'] and not info['cid'] else 'PLACE'}@d{info['depth']}(cid={info['cid']}) {class_name}")
            else:
                current['tags'].append(f"PO?")
        elif tt == TAG_REMOVEOBJECT2 and len(td) >= 2:
            depth = struct.unpack_from('<H', td, 0)[0]
            current['tags'].append(f"REMOVE@d{depth}")
        elif tt == TAG_END:
            break
        else:
            current['tags'].append(f"tag{tt}({len(td)}b)")
    return frames


def main():
    print("Loading SWFs...")
    og_tags = get_swf_tags(OG_SWF)
    rt_tags = get_swf_tags(RT_SWF)
    
    og_sym = get_symbol_class(og_tags)
    rt_sym = get_symbol_class(rt_tags)
    
    fox_og_cid = og_sym.get('fox')
    fox_rt_cid = rt_sym.get('fox')
    print(f"OG fox charId={fox_og_cid}, RT fox charId={fox_rt_cid}")
    
    # Get fox MC inner tags
    og_fc, og_inner = get_sprite_inner_tags(og_tags, fox_og_cid)
    rt_fc, rt_inner = get_sprite_inner_tags(rt_tags, fox_rt_cid)
    print(f"OG frame count: {og_fc}, RT frame count: {rt_fc}")
    print(f"OG inner tag count: {len(og_inner)}, RT inner tag count: {len(rt_inner)}")
    
    # Compare inner tags byte-for-byte
    if len(og_inner) != len(rt_inner):
        print(f"DIFFERENT number of inner tags! OG={len(og_inner)} RT={len(rt_inner)}")
    
    # Compare tag by tag
    max_tags = max(len(og_inner), len(rt_inner))
    diffs = 0
    for i in range(max_tags):
        og_tt = og_inner[i][0] if i < len(og_inner) else None
        og_td = og_inner[i][1] if i < len(og_inner) else None
        rt_tt = rt_inner[i][0] if i < len(rt_inner) else None
        rt_td = rt_inner[i][1] if i < len(rt_inner) else None
        
        if og_tt != rt_tt or og_td != rt_td:
            diffs += 1
            if diffs <= 20:
                og_info = f"type={og_tt} len={len(og_td) if og_td else 0}"
                rt_info = f"type={rt_tt} len={len(rt_td) if rt_td else 0}"
                print(f"  Tag #{i}: OG({og_info}) vs RT({rt_info})")
                if og_tt != rt_tt:
                    print(f"    TAG TYPE DIFFERS!")
                elif og_td != rt_td:
                    # Find first byte difference
                    for b in range(min(len(og_td), len(rt_td))):
                        if og_td[b] != rt_td[b]:
                            print(f"    First byte diff at offset {b}: OG=0x{og_td[b]:02x} RT=0x{rt_td[b]:02x}")
                            # Show context
                            og_context = og_td[max(0,b-2):b+5].hex()
                            rt_context = rt_td[max(0,b-2):b+5].hex()
                            print(f"    OG bytes: {og_context}")
                            print(f"    RT bytes: {rt_context}")
                            break
                    if len(og_td) != len(rt_td):
                        print(f"    Length differs: OG={len(og_td)} RT={len(rt_td)}")
    
    if diffs == 0:
        print("\nFox MC inner tags are IDENTICAL between OG and RT!")
    else:
        print(f"\n{diffs} differing inner tags")
    
    # Now analyze per-frame structure
    print(f"\n{'='*60}")
    print("OG Fox MC per-frame structure:")
    print(f"{'='*60}")
    og_frames = analyze_sprite_frames(og_inner, og_sym)
    for i, f in enumerate(og_frames[:5]):  # first 5 frames
        label = f"[{f['label']}]" if f['label'] else ""
        print(f"  Frame {i+1} {label}: {', '.join(f['tags'][:5])}")
    
    print(f"\n{'='*60}")
    print("RT Fox MC per-frame structure:")
    print(f"{'='*60}")
    rt_frames = analyze_sprite_frames(rt_inner, rt_sym)
    for i, f in enumerate(rt_frames[:5]):  # first 5 frames
        label = f"[{f['label']}]" if f['label'] else ""
        print(f"  Frame {i+1} {label}: {', '.join(f['tags'][:5])}")
    
    # Count frames with stance placements
    print(f"\nOG frames: {len(og_frames)}, RT frames: {len(rt_frames)}")
    
    # Compare frame labels
    for i in range(min(len(og_frames), len(rt_frames))):
        og_label = og_frames[i]['label']
        rt_label = rt_frames[i]['label']
        if og_label != rt_label:
            print(f"  Label diff frame {i+1}: OG='{og_label}' RT='{rt_label}'")
    
    # Per-frame tag comparison
    print(f"\nPer-frame tag differences:")
    frame_diffs = 0
    for i in range(min(len(og_frames), len(rt_frames))):
        og_f = og_frames[i]
        rt_f = rt_frames[i]
        if og_f['tags'] != rt_f['tags']:
            frame_diffs += 1
            if frame_diffs <= 10:
                label = og_f['label'] or ''
                print(f"\n  Frame {i+1} [{label}]:")
                print(f"    OG: {og_f['tags']}")
                print(f"    RT: {rt_f['tags']}")
    
    if frame_diffs == 0:
        print("  None! Per-frame structure is identical.")
    else:
        print(f"\n  {frame_diffs} frames with different tags")


if __name__ == '__main__':
    main()
