"""
Categorize all PlaceObject differences between OG and RT fox SWFs.
"""
import struct, zlib, re
from collections import Counter

def parse_swf(path):
    with open(path, 'rb') as f:
        sig = f.read(3)
        ver = struct.unpack('<B', f.read(1))[0]
        length = struct.unpack_from('<I', f.read(4))[0]
        rest = f.read()
    if sig == b'CWS':
        rest = zlib.decompress(rest)
    nbits = (rest[0] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    return rest[rect_bytes + 4:]

def iter_tags(data):
    pos = 0
    while pos < len(data):
        if pos + 2 > len(data): break
        h = struct.unpack_from('<H', data, pos)[0]
        pos += 2
        tt = h >> 6
        length = h & 0x3F
        if length == 0x3F:
            length = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        body = data[pos:pos+length]
        yield tt, body
        pos += length
        if tt == 0: break

def get_sprites(data):
    sprites = {}
    for tt, body in iter_tags(data):
        if tt == 39:
            cid = struct.unpack_from('<H', body, 0)[0]
            sprites[cid] = body[4:]
    return sprites

def get_symbol_class(data):
    mapping = {}
    for tt, body in iter_tags(data):
        if tt == 76:
            count = struct.unpack_from('<H', body, 0)[0]
            off = 2
            for _ in range(count):
                cid = struct.unpack_from('<H', body, off)[0]
                off += 2
                end = body.index(b'\x00', off)
                name = body[off:end].decode('utf-8', errors='replace')
                off = end + 1
                mapping[cid] = name
    return mapping

def timeline_to_frames(inner):
    frames = []
    cur = []
    for tt, body in iter_tags(inner):
        if tt == 0: break
        if tt == 1:
            frames.append(cur)
            cur = []
        else:
            cur.append((tt, body))
    return frames

def categorize_diff(ott, ob, rtt, rb):
    """Categorize a tag difference."""
    if ott != rtt:
        return "tag_type_mismatch"
    if ott not in (26, 70):
        if ott == 28:  # Remove - check if same depths in different order
            return "remove_order"
        if ott == 43:  # FrameLabel
            return "label_diff"
        return f"tag{ott}_diff"
    
    # PlaceObject comparison
    if ott == 26:
        of, rf = ob[0], rb[0]
    else:
        of, rf = ob[0], rb[0]
    
    od = struct.unpack_from('<H', ob, 1 if ott==26 else 2)[0]
    rd = struct.unpack_from('<H', rb, 1 if ott==26 else 2)[0]
    
    if od != rd:
        return "depth_mismatch"
    
    # Check CID
    o_off = 3 if ott == 26 else 4
    r_off = 3 if rtt == 26 else 4
    ocid = struct.unpack_from('<H', ob, o_off)[0] if (of & 0x02) else None
    rcid = struct.unpack_from('<H', rb, r_off)[0] if (rf & 0x02) else None
    
    # Categorize flag differences
    flag_diff = of ^ rf
    
    if flag_diff == 0:
        # Same flags, must be data differences (CID or matrix values)
        if ocid != rcid and len(ob) == len(rb):
            return "cid_only"
        return "data_diff"
    
    categories = []
    if flag_diff & 0x04:
        if rf & 0x04:
            categories.append("added_HasMatrix")
        else:
            categories.append("removed_HasMatrix")
    if flag_diff & 0x10:
        if of & 0x10:
            categories.append("lost_HasRatio")
        else:
            categories.append("gained_HasRatio")
    if flag_diff & 0x08:
        categories.append("HasCxform_diff")
    if flag_diff & 0x20:
        categories.append("HasName_diff")
    if flag_diff & 0x01:
        categories.append("Move_diff")
    if flag_diff & 0x02:
        categories.append("HasChar_diff")
    
    return "+".join(categories) if categories else f"flags_0x{of:02x}_to_0x{rf:02x}"

def main():
    og_data = parse_swf(r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf")
    rt_data = parse_swf(r"C:\Users\glwex\Documents\GitHub\Next2Flash\app\fox_fresh.swf")
    
    og_sprites = get_sprites(og_data)
    rt_sprites = get_sprites(rt_data)
    og_sym = get_symbol_class(og_data)
    rt_sym = get_symbol_class(rt_data)
    
    og_cls2cid = {v: k for k, v in og_sym.items()}
    rt_cls2cid = {v: k for k, v in rt_sym.items()}
    
    targets = sorted([c for c in og_cls2cid if 'fox_fla.fox_' in c])
    
    cat_counter = Counter()
    
    for cls in targets:
        og_cid = og_cls2cid[cls]
        rt_cid = rt_cls2cid.get(cls)
        if rt_cid is None or og_cid not in og_sprites or rt_cid not in rt_sprites:
            continue
        
        og_frames = timeline_to_frames(og_sprites[og_cid])
        rt_frames = timeline_to_frames(rt_sprites[rt_cid])
        
        if len(og_frames) != len(rt_frames):
            cat_counter["frame_count_mismatch"] += 1
            continue
        
        for fi in range(len(og_frames)):
            og_tags = og_frames[fi]
            rt_tags = rt_frames[fi]
            
            if len(og_tags) != len(rt_tags):
                cat_counter["tag_count_mismatch"] += 1
                continue
            
            for ti in range(len(og_tags)):
                ott, ob = og_tags[ti]
                rtt, rb = rt_tags[ti]
                if ob != rb or ott != rtt:
                    cat = categorize_diff(ott, ob, rtt, rb)
                    cat_counter[cat] += 1
    
    print("=== Difference Categories (across all fox stance MCs) ===")
    for cat, count in cat_counter.most_common():
        print(f"  {cat:40s}  {count:5d}")
    print(f"\n  {'TOTAL':40s}  {sum(cat_counter.values()):5d}")

if __name__ == '__main__':
    main()
