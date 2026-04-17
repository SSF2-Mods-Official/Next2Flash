"""Compare inner tags of specific stance MCs between OG and RT SWFs.

Analyzes fox_entrance_17 and fox_combo_36 -- the entrance and jab combo
stance MovieClips that are directly involved in the looping issue.
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

TAG_NAMES = {
    0: "End", 1: "ShowFrame", 2: "DefineShape", 4: "PlaceObject",
    5: "RemoveObject", 22: "DefineShape2", 26: "PlaceObject2",
    28: "RemoveObject2", 32: "DefineShape3", 39: "DefineSprite",
    43: "FrameLabel", 45: "SoundStreamHead2", 46: "SoundStreamBlock",
    70: "PlaceObject3", 83: "DefineShape4",
}


def get_swf_tags(swf_path):
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


def parse_sprite_inner(tags, sprite_cid):
    """Get inner tags from DefineSprite."""
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


def decode_po_flags(tag_type, data):
    """Decode PlaceObject2/3 flags and fields."""
    if not data:
        return None
    pos = 0
    result = {}
    
    if tag_type == TAG_PLACEOBJECT2:
        flags = data[pos]; pos += 1
        result['flags_byte'] = f"0x{flags:02x}"
        result['has_clip_actions'] = bool(flags & 0x80)
        result['has_clip_depth'] = bool(flags & 0x40)
        result['has_name'] = bool(flags & 0x20)
        result['has_ratio'] = bool(flags & 0x10)
        result['has_cxform'] = bool(flags & 0x08)
        result['has_matrix'] = bool(flags & 0x04)
        result['has_character'] = bool(flags & 0x02)
        result['is_move'] = bool(flags & 0x01)
        result['depth'] = struct.unpack_from('<H', data, pos)[0]; pos += 2
        if result['has_character']:
            result['cid'] = struct.unpack_from('<H', data, pos)[0]; pos += 2
        result['tag_type'] = 'PO2'
        result['total_len'] = len(data)

    elif tag_type == TAG_PLACEOBJECT3:
        flags1 = data[pos]; pos += 1
        flags2 = data[pos]; pos += 1
        result['flags_bytes'] = f"0x{flags1:02x} 0x{flags2:02x}"
        result['has_clip_actions'] = bool(flags1 & 0x80)
        result['has_clip_depth'] = bool(flags1 & 0x40)
        result['has_name'] = bool(flags1 & 0x20)
        result['has_ratio'] = bool(flags1 & 0x10)
        result['has_cxform'] = bool(flags1 & 0x08)
        result['has_matrix'] = bool(flags1 & 0x04)
        result['has_character'] = bool(flags1 & 0x02)
        result['is_move'] = bool(flags1 & 0x01)
        result['has_filter'] = bool(flags2 & 0x01)
        result['has_blend'] = bool(flags2 & 0x02)
        result['has_cache_bitmap'] = bool(flags2 & 0x04)
        result['depth'] = struct.unpack_from('<H', data, pos)[0]; pos += 2
        if result['has_character']:
            result['cid'] = struct.unpack_from('<H', data, pos)[0]; pos += 2
        result['tag_type'] = 'PO3'
        result['total_len'] = len(data)

    return result


def describe_tag(tt, td, sym_map=None):
    """Human-readable description of a tag."""
    name = TAG_NAMES.get(tt, f"tag{tt}")
    
    if tt in (TAG_PLACEOBJECT2, TAG_PLACEOBJECT3):
        po = decode_po_flags(tt, td)
        if po:
            cid = po.get('cid', None)
            cname = sym_map.get(cid, '') if sym_map and cid else ''
            flags = []
            if po.get('is_move'): flags.append('MOVE')
            if po.get('has_character'): flags.append(f'cid={cid}')
            if po.get('has_matrix'): flags.append('MAT')
            if po.get('has_cxform'): flags.append('CX')
            if po.get('has_name'): flags.append('NAME')
            if po.get('has_ratio'): flags.append('RATIO')
            if po.get('has_clip_depth'): flags.append('CLIP')
            if po.get('has_filter'): flags.append('FILTER')
            if po.get('has_blend'): flags.append('BLEND')
            return f"{name}(d={po['depth']} {' '.join(flags)} {cname}) [{len(td)}b]"
    
    if tt == TAG_REMOVEOBJECT2 and len(td) >= 2:
        depth = struct.unpack_from('<H', td, 0)[0]
        return f"RemoveObject2(d={depth})"
    
    if tt == TAG_FRAMELABEL:
        label = td[:td.index(0)].decode('utf-8', errors='replace')
        return f"FrameLabel({label})"
    
    if tt == TAG_SHOWFRAME:
        return "ShowFrame"
    
    if tt == TAG_END:
        return "End"
    
    return f"{name}({len(td)}b)"


def compare_stance(class_name, og_tags, rt_tags, og_sym, rt_sym):
    """Compare a specific stance MC between OG and RT."""
    og_cid = og_sym.get(class_name)
    rt_cid = rt_sym.get(class_name)
    
    if og_cid is None:
        print(f"  {class_name}: NOT FOUND in OG SymbolClass")
        return
    if rt_cid is None:
        print(f"  {class_name}: NOT FOUND in RT SymbolClass")
        return
    
    og_fc, og_inner = parse_sprite_inner(og_tags, og_cid)
    rt_fc, rt_inner = parse_sprite_inner(rt_tags, rt_cid)
    
    if og_inner is None or rt_inner is None:
        print(f"  {class_name}: sprite not found (OG cid={og_cid}, RT cid={rt_cid})")
        return
    
    print(f"\n{'='*70}")
    print(f"  {class_name}")
    print(f"  OG: cid={og_cid} frames={og_fc} tags={len(og_inner)}")
    print(f"  RT: cid={rt_cid} frames={rt_fc} tags={len(rt_inner)}")
    print(f"{'='*70}")
    
    # Group by frame
    def group_by_frame(inner_tags, sym_map):
        frames = []
        current = []
        for tt, td in inner_tags:
            if tt == TAG_SHOWFRAME:
                frames.append(current)
                current = []
            elif tt == TAG_END:
                break
            else:
                current.append(describe_tag(tt, td, sym_map))
        return frames
    
    og_frames = group_by_frame(og_inner, og_sym)
    rt_frames = group_by_frame(rt_inner, rt_sym)
    
    max_f = max(len(og_frames), len(rt_frames))
    diff_count = 0
    
    for i in range(max_f):
        og_f = og_frames[i] if i < len(og_frames) else []
        rt_f = rt_frames[i] if i < len(rt_frames) else []
        
        # Normalize: replace CIDs with class names for comparison
        # (CIDs differ between OG/RT but class names should match)
        # We already include class names in the description, so just compare strings
        
        if og_f != rt_f:
            diff_count += 1
            print(f"\n  Frame {i+1}:")
            # Show side by side
            max_tags = max(len(og_f), len(rt_f))
            for j in range(max_tags):
                og_t = og_f[j] if j < len(og_f) else "---"
                rt_t = rt_f[j] if j < len(rt_f) else "---"
                marker = " !!" if og_t != rt_t else "   "
                print(f"    {marker} OG: {og_t}")
                print(f"        RT: {rt_t}")
    
    if diff_count == 0:
        print("  IDENTICAL!")
    else:
        print(f"\n  {diff_count}/{max_f} frames differ")


def main():
    print("Loading SWFs...")
    og_tags = get_swf_tags(OG_SWF)
    rt_tags = get_swf_tags(RT_SWF)
    og_sym = get_symbol_class(og_tags)
    rt_sym = get_symbol_class(rt_tags)
    
    # Compare key stance MCs
    targets = [
        "fox_fla.fox_entrance_17",
        "fox_fla.fox_combo_36",
        "fox_fla.fox_idle_14",
        "fox_fla.fox_DashA_37",
    ]
    
    for name in targets:
        compare_stance(name, og_tags, rt_tags, og_sym, rt_sym)


if __name__ == '__main__':
    main()
