"""Compare pichu Idle_3 sprite OG vs RT to find frame26 crash cause."""
import struct, zlib, io

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\pichu.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\pichu.ssf"

def read_swf(path):
    with open(path, 'rb') as f:
        data = f.read()
    sig = data[:3]
    if sig in (b'CWS', b'ZWS'):
        data = data[:8] + zlib.decompress(data[8:])
    return data

def parse_tags(data, offset=0):
    tags = []
    pos = offset
    while pos < len(data):
        if pos + 2 > len(data): break
        tag_code_and_length = struct.unpack_from('<H', data, pos)[0]
        tag_type = tag_code_and_length >> 6
        length = tag_code_and_length & 0x3F
        pos += 2
        if length == 0x3F:
            if pos + 4 > len(data): break
            length = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        tag_data = data[pos:pos+length]
        tags.append((tag_type, tag_data))
        pos += length
        if tag_type == 0: break
    return tags

def skip_header(data):
    pos = 8
    nbits = data[pos] >> 3
    total_bits = 5 + nbits * 4
    total_bytes = (total_bits + 7) // 8
    pos += total_bytes
    pos += 4
    return pos

def parse_symbol_class(data):
    pos = 0
    count = struct.unpack_from('<H', data, pos)[0]; pos += 2
    symbols = {}
    for _ in range(count):
        cid = struct.unpack_from('<H', data, pos)[0]; pos += 2
        end = data.index(0, pos)
        name = data[pos:end].decode('utf-8'); pos = end + 1
        symbols[name] = cid
    return symbols

def parse_po2(data):
    """Parse PlaceObject2 fields."""
    flags = data[0]
    pos = 1
    depth = struct.unpack_from('<H', data, pos)[0]; pos += 2
    result = {'flags': flags, 'depth': depth}
    
    has_clip_actions = bool(flags & 0x80)
    has_clip_depth = bool(flags & 0x40)
    has_name = bool(flags & 0x20)
    has_ratio = bool(flags & 0x10)
    has_cxform = bool(flags & 0x08)
    has_matrix = bool(flags & 0x04)
    has_cid = bool(flags & 0x02)
    is_move = bool(flags & 0x01)
    
    result['is_move'] = is_move
    
    if has_cid:
        result['cid'] = struct.unpack_from('<H', data, pos)[0]; pos += 2
    if has_matrix:
        result['has_matrix'] = True
    if has_cxform:
        result['has_cxform'] = True
    if has_ratio:
        # need to skip matrix to find ratio position - just note it exists
        result['has_ratio'] = True
    if has_name:
        result['has_name'] = True
    if has_clip_depth:
        result['has_clip_depth'] = True
    
    return result

def parse_sprite(data):
    cid = struct.unpack_from('<H', data, 0)[0]
    frame_count = struct.unpack_from('<H', data, 2)[0]
    inner_tags = parse_tags(data, 4)
    return cid, frame_count, inner_tags

def split_frames(tags):
    frames = []
    cur = []
    for t, d in tags:
        cur.append((t, d))
        if t == 1:  # ShowFrame
            frames.append(cur)
            cur = []
    return frames

TAG_NAMES = {
    0:'End', 1:'ShowFrame', 26:'PO2', 28:'RemoveObject2', 
    70:'PO3', 45:'SSH2', 46:'SSBlock', 43:'FrameLabel',
    5:'RemoveObject', 4:'PlaceObject'
}

og = read_swf(OG)
rt = read_swf(RT)
print(f"OG size: {len(og)}, RT size: {len(rt)}")

og_start = skip_header(og)
rt_start = skip_header(rt)
og_tags = parse_tags(og, og_start)
rt_tags = parse_tags(rt, rt_start)

og_sym = rt_sym = None
for t, d in og_tags:
    if t == 76: og_sym = parse_symbol_class(d)
for t, d in rt_tags:
    if t == 76: rt_sym = parse_symbol_class(d)

# Find Idle_3
idle3_name = None
for name in og_sym:
    if 'Idle_3' in name:
        idle3_name = name
        og_cid_idle = og_sym[name]
        rt_cid_idle = rt_sym.get(name, None)
        print(f"Found: {name} OG_CID={og_cid_idle} RT_CID={rt_cid_idle}")

# Parse all sprites
og_sprites = {}
rt_sprites = {}
for t, d in og_tags:
    if t in (39, 37):
        cid, fc, inner = parse_sprite(d)
        og_sprites[cid] = (fc, inner, t)
for t, d in rt_tags:
    if t in (39, 37):
        cid, fc, inner = parse_sprite(d)
        rt_sprites[cid] = (fc, inner, t)

# Reverse lookup: CID -> symbol name
og_cid_to_name = {v: k for k, v in og_sym.items()}
rt_cid_to_name = {v: k for k, v in rt_sym.items()}

if idle3_name:
    og_cid = og_sym[idle3_name]
    rt_cid = rt_sym[idle3_name]
    
    og_found = og_cid in og_sprites
    rt_found = rt_cid in rt_sprites
    print(f"OG sprite found: {og_found}, RT sprite found: {rt_found}")
    
    if og_found and rt_found:
        og_fc, og_inner, og_tt = og_sprites[og_cid]
        rt_fc, rt_inner, rt_tt = rt_sprites[rt_cid]
        print(f"OG: tag_type={og_tt} frame_count={og_fc} inner_tags={len(og_inner)}")
        print(f"RT: tag_type={rt_tt} frame_count={rt_fc} inner_tags={len(rt_inner)}")
        
        og_frames = split_frames(og_inner)
        rt_frames = split_frames(rt_inner)
        print(f"OG actual frames: {len(og_frames)}, RT actual frames: {len(rt_frames)}")
        
        # Compare all frames, focusing around frame 26
        for fi in range(min(len(og_frames), len(rt_frames))):
            og_f = og_frames[fi]
            rt_f = rt_frames[fi]
            
            # Check for differences
            og_non_sf = [(t, d) for t, d in og_f if t != 1]
            rt_non_sf = [(t, d) for t, d in rt_f if t != 1]
            
            if len(og_non_sf) != len(rt_non_sf):
                print(f"\n=== Frame {fi+1}: TAG COUNT DIFFERS ===")
                print(f"  OG: {len(og_non_sf)} tags, RT: {len(rt_non_sf)} tags")
                for t, d in og_f:
                    tn = TAG_NAMES.get(t, f'Tag{t}')
                    extra = ""
                    if t in (26, 70):
                        po = parse_po2(d)
                        extra = f" depth={po['depth']} cid={po.get('cid','?')} move={po['is_move']}"
                    elif t == 28:
                        dp = struct.unpack_from('<H', d, 0)[0]
                        extra = f" depth={dp}"
                    print(f"  OG: {tn}({len(d)}B){extra}")
                for t, d in rt_f:
                    tn = TAG_NAMES.get(t, f'Tag{t}')
                    extra = ""
                    if t in (26, 70):
                        po = parse_po2(d)
                        extra = f" depth={po['depth']} cid={po.get('cid','?')} move={po['is_move']}"
                    elif t == 28:
                        dp = struct.unpack_from('<H', d, 0)[0]
                        extra = f" depth={dp}"
                    print(f"  RT: {tn}({len(d)}B){extra}")
            elif fi >= 24 and fi <= 27:  # Print frames around 26 even if same count
                print(f"\n=== Frame {fi+1}: same tag count ({len(og_non_sf)}) ===")
                for i, ((ot, od), (rtt, rtd)) in enumerate(zip(og_f, rt_f)):
                    otn = TAG_NAMES.get(ot, f'Tag{ot}')
                    rtn = TAG_NAMES.get(rtt, f'Tag{rtt}')
                    match = "OK" if od == rtd else "DIFF"
                    extra = ""
                    if ot in (26, 70):
                        po = parse_po2(od)
                        extra = f" depth={po['depth']} cid={po.get('cid','?')} move={po['is_move']}"
                    print(f"  [{i}] {otn}({len(od)}B) vs {rtn}({len(rtd)}B) {match}{extra}")
        
        if len(og_frames) != len(rt_frames):
            print(f"\nFRAME COUNT MISMATCH: OG={len(og_frames)} RT={len(rt_frames)}")
    elif not rt_found:
        print(f"RT sprite CID {rt_cid} NOT FOUND in RT sprites!")
        print(f"RT sprite CIDs near {rt_cid}: {sorted([c for c in rt_sprites if abs(c-rt_cid) < 20])}")

# Also check: what CIDs does frame26 of Idle_3 reference?
# Parse the frame script to understand what it accesses
print("\n\n=== Checking what Idle_3 frame 26 accesses ===")
if og_found:
    og_f26 = og_frames[25] if len(og_frames) >= 26 else []
    print("OG frame 26 PlaceObjects:")
    for t, d in og_f26:
        if t in (26, 70):
            po = parse_po2(d)
            cid = po.get('cid', None)
            name_str = ""
            if cid and cid in og_cid_to_name:
                name_str = f" ({og_cid_to_name[cid]})"
            print(f"  depth={po['depth']} cid={cid}{name_str} move={po['is_move']} flags=0x{po['flags']:02x}")
        elif t == 28:
            dp = struct.unpack_from('<H', d, 0)[0]
            print(f"  RemoveObject2 depth={dp}")

if rt_found:
    rt_f26 = rt_frames[25] if len(rt_frames) >= 26 else []
    print("RT frame 26 PlaceObjects:")
    for t, d in rt_f26:
        if t in (26, 70):
            po = parse_po2(d)
            cid = po.get('cid', None)
            name_str = ""
            if cid and cid in rt_cid_to_name:
                name_str = f" ({rt_cid_to_name[cid]})"
            print(f"  depth={po['depth']} cid={cid}{name_str} move={po['is_move']} flags=0x{po['flags']:02x}")
        elif t == 28:
            dp = struct.unpack_from('<H', d, 0)[0]
            print(f"  RemoveObject2 depth={dp}")
