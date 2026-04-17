"""Check SymbolClass associations for fox child sprites and inner sprite structure."""
import struct, sys, os, zlib

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\fox.ssf"

def read_swf(path):
    with open(path, 'rb') as f:
        data = f.read()
    sig = data[:3]
    if sig == b'CWS':
        data = data[:8] + zlib.decompress(data[8:])
    elif sig == b'ZWS':
        import lzma
        data = data[:8] + lzma.decompress(data[12:])
    return data

def scan_all(data):
    """Extract all top-level tags, sprites, and SymbolClass."""
    pos = 8
    nbits = (data[pos] >> 3) & 0x1F
    rect_bits = 5 + nbits * 4
    rect_bytes = (rect_bits + 7) // 8
    pos += rect_bytes + 4
    
    sprites = {}  # charId → (frameCount, inner_tags_raw)
    symbol_class = {}  # charId → name
    symbol_name_to_id = {}  # name → charId
    
    while pos < len(data):
        if pos + 2 > len(data):
            break
        code_and_len = struct.unpack_from('<H', data, pos)[0]
        tag_type = code_and_len >> 6
        tag_len = code_and_len & 0x3F
        pos += 2
        if tag_len == 0x3F:
            tag_len = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        tag_start = pos
        pos += tag_len
        if tag_type == 0:
            break
        
        if tag_type == 39:  # DefineSprite
            sprite_id = struct.unpack_from('<H', data, tag_start)[0]
            frame_count = struct.unpack_from('<H', data, tag_start + 2)[0]
            sprites[sprite_id] = (frame_count, data[tag_start + 4:tag_start + tag_len])
        
        elif tag_type == 76:  # SymbolClass
            body = data[tag_start:tag_start + tag_len]
            count = struct.unpack_from('<H', body, 0)[0]
            off = 2
            for _ in range(count):
                cid = struct.unpack_from('<H', body, off)[0]
                off += 2
                end = body.index(0, off)
                name = body[off:end].decode('utf-8', errors='replace')
                off = end + 1
                symbol_class[cid] = name
                symbol_name_to_id[name] = cid
    
    return sprites, symbol_class, symbol_name_to_id

def parse_inner_tags(raw_data):
    tags = []
    pos = 0
    while pos < len(raw_data):
        if pos + 2 > len(raw_data):
            break
        code_and_len = struct.unpack_from('<H', raw_data, pos)[0]
        tag_type = code_and_len >> 6
        tag_len = code_and_len & 0x3F
        pos += 2
        if tag_len == 0x3F:
            if pos + 4 > len(raw_data):
                break
            tag_len = struct.unpack_from('<I', raw_data, pos)[0]
            pos += 4
        tag_data = raw_data[pos:pos + tag_len]
        tags.append((tag_type, tag_data))
        pos += tag_len
        if tag_type == 0:
            break
    return tags

def find_fox_sprite(sprites, symbol_class):
    """Find the main fox sprite by looking for one with 'stand' label and 80+ frames."""
    for sid, (fc, raw) in sprites.items():
        if fc < 50:
            continue
        inner = parse_inner_tags(raw)
        for tt, td in inner:
            if tt == 43:  # FrameLabel
                lbl = td[:td.index(0)].decode('utf-8', errors='replace') if 0 in td else ''
                if lbl == 'stand':
                    name = symbol_class.get(sid, '(unnamed)')
                    return sid, fc, inner, name
    return None, None, None, None

def get_depth7_children(inner_tags):
    """Get all unique charIds placed at depth 7."""
    children = []
    frame = 0
    for tt, td in inner_tags:
        if tt == 1:  # ShowFrame
            frame += 1
        elif tt == 26:  # PO2
            flags = td[0]
            depth = struct.unpack_from('<H', td, 1)[0]
            if depth == 7 and (flags & 0x02):  # hasChar
                cid = struct.unpack_from('<H', td, 3)[0]
                # Get name
                name = None
                if flags & 0x20:  # hasName
                    off = 3 + 2  # past flags+depth+charId
                    # skip matrix if present
                    if flags & 0x04:
                        # need to parse MATRIX... complex. Just look for first null byte after some offset
                        pass
                # Get frame label from surrounding tags
                children.append((frame, cid))
    return children

def get_frame_labels(inner_tags):
    """Get frame→label mapping."""
    labels = {}
    frame = 0
    for tt, td in inner_tags:
        if tt == 1:
            frame += 1
        elif tt == 43:
            lbl = td[:td.index(0)].decode('utf-8', errors='replace') if 0 in td else ''
            labels[frame] = lbl
    return labels

print("=== Loading ===")
og_data = read_swf(OG)
rt_data = read_swf(RT)

og_sprites, og_sym, og_sym_name = scan_all(og_data)
rt_sprites, rt_sym, rt_sym_name = scan_all(rt_data)

print(f"  OG: {len(og_sprites)} sprites, {len(og_sym)} SymbolClass entries")
print(f"  RT: {len(rt_sprites)} sprites, {len(rt_sym)} SymbolClass entries")

# Find fox
og_fox_id, og_fox_fc, og_fox_tags, og_fox_name = find_fox_sprite(og_sprites, og_sym)
rt_fox_id, rt_fox_fc, rt_fox_tags, rt_fox_name = find_fox_sprite(rt_sprites, rt_sym)
print(f"\n  OG fox: id={og_fox_id}, frames={og_fox_fc}, symbol='{og_fox_name}'")
print(f"  RT fox: id={rt_fox_id}, frames={rt_fox_fc}, symbol='{rt_fox_name}'")

# Get children at depth 7
og_children = get_depth7_children(og_fox_tags)
rt_children = get_depth7_children(rt_fox_tags)
og_labels = get_frame_labels(og_fox_tags)
rt_labels = get_frame_labels(rt_fox_tags)

# Check SymbolClass for ALL children
print(f"\n=== SymbolClass associations for depth-7 children ===")
print(f"{'Frame':>5} {'Label':<22} {'OG_cid':>7} {'OG_sym':<35} {'RT_cid':>7} {'RT_sym':<35}")

og_child_idx = {}
for frame, cid in og_children:
    if cid not in og_child_idx:
        og_child_idx[cid] = frame
rt_child_idx = {}
for frame, cid in rt_children:
    if cid not in rt_child_idx:
        rt_child_idx[cid] = frame

# Build frame→childId maps
og_frame_child = {}
for frame, cid in og_children:
    og_frame_child[frame] = cid
rt_frame_child = {}
for frame, cid in rt_children:
    rt_frame_child[frame] = cid

og_has_sym = 0
rt_has_sym = 0
og_missing_sym = 0
rt_missing_sym = 0
sym_mismatches = []

all_frames = sorted(set(list(og_frame_child.keys()) + list(rt_frame_child.keys())))
for frame in all_frames:
    og_cid = og_frame_child.get(frame)
    rt_cid = rt_frame_child.get(frame)
    og_name = og_sym.get(og_cid, '') if og_cid else ''
    rt_name = rt_sym.get(rt_cid, '') if rt_cid else ''
    label = og_labels.get(frame, rt_labels.get(frame, ''))
    
    if og_cid and og_name:
        og_has_sym += 1
    elif og_cid:
        og_missing_sym += 1
    if rt_cid and rt_name:
        rt_has_sym += 1
    elif rt_cid:
        rt_missing_sym += 1
    
    # Check if OG has symbol but RT doesn't or vice versa
    has_mismatch = bool(og_name) != bool(rt_name) or og_name != rt_name
    if has_mismatch:
        sym_mismatches.append(frame)
    
    # Print all with labels or with mismatches
    if label or has_mismatch:
        flag = '!!' if has_mismatch else '  '
        print(f"{flag}{frame:>3} {label:<22} {og_cid or '-':>7} {og_name or '(none)':<35} {rt_cid or '-':>7} {rt_name or '(none)':<35}")

print(f"\n  OG: {og_has_sym} children with SymbolClass, {og_missing_sym} without")
print(f"  RT: {rt_has_sym} children with SymbolClass, {rt_missing_sym} without")
print(f"  Symbol mismatches: {len(sym_mismatches)}")

# Check ALL SymbolClass entries to see which ones map to sprites vs other types
print(f"\n=== SymbolClass name comparison ===")
og_names = set(og_sym.values())
rt_names = set(rt_sym.values())
only_og = og_names - rt_names
only_rt = rt_names - og_names
common = og_names & rt_names
print(f"  Common names: {len(common)}")
print(f"  Only in OG: {len(only_og)}")
if only_og:
    for n in sorted(only_og)[:20]:
        print(f"    {n}")
print(f"  Only in RT: {len(only_rt)}")
if only_rt:
    for n in sorted(only_rt)[:20]:
        print(f"    {n}")

# Check the 'a' attack child in more detail
print(f"\n=== 'a' attack child deep dive ===")
og_a_frame = None
rt_a_frame = None
for f in all_frames:
    if og_labels.get(f) == 'a':
        og_a_frame = f
    if rt_labels.get(f) == 'a':
        rt_a_frame = f

if og_a_frame is not None and rt_a_frame is not None:
    og_a_cid = og_frame_child.get(og_a_frame)
    rt_a_cid = rt_frame_child.get(rt_a_frame)
    og_a_sym = og_sym.get(og_a_cid, '(none)')
    rt_a_sym = rt_sym.get(rt_a_cid, '(none)')
    print(f"  OG 'a': charId={og_a_cid}, symbol='{og_a_sym}'")
    print(f"  RT 'a': charId={rt_a_cid}, symbol='{rt_a_sym}'")
    
    # Get child sprite data
    og_a_fc, og_a_raw = og_sprites.get(og_a_cid, (0, b''))
    rt_a_fc, rt_a_raw = rt_sprites.get(rt_a_cid, (0, b''))
    og_a_inner = parse_inner_tags(og_a_raw)
    rt_a_inner = parse_inner_tags(rt_a_raw)
    
    # Get frame labels of the 'a' child
    og_a_labels = get_frame_labels(og_a_inner)
    rt_a_labels = get_frame_labels(rt_a_inner)
    print(f"  OG 'a' labels: {og_a_labels}")
    print(f"  RT 'a' labels: {rt_a_labels}")
    
    # Check if the 'a' child has any children with SymbolClass
    og_a_children = set()
    rt_a_children = set()
    for tt, td in og_a_inner:
        if tt == 26 and len(td) >= 5:
            flags = td[0]
            if flags & 0x02:
                cid = struct.unpack_from('<H', td, 3)[0]
                og_a_children.add(cid)
    for tt, td in rt_a_inner:
        if tt == 26 and len(td) >= 5:
            flags = td[0]
            if flags & 0x02:
                cid = struct.unpack_from('<H', td, 3)[0]
                rt_a_children.add(cid)
    
    og_a_children_with_sym = [c for c in og_a_children if c in og_sym]
    rt_a_children_with_sym = [c for c in rt_a_children if c in rt_sym]
    print(f"  OG 'a' inner children: {len(og_a_children)} total, {len(og_a_children_with_sym)} with SymbolClass")
    print(f"  RT 'a' inner children: {len(rt_a_children)} total, {len(rt_a_children_with_sym)} with SymbolClass")
    
    if og_a_children_with_sym:
        for c in sorted(og_a_children_with_sym):
            print(f"    OG: charId={c} → '{og_sym[c]}'")
    if rt_a_children_with_sym:
        for c in sorted(rt_a_children_with_sym):
            print(f"    RT: charId={c} → '{rt_sym[c]}'")

# Also: read raw PO2 at frame 14 (attack) depth 7 to see the exact ratio value  
print(f"\n=== Raw PO2 bytes at 'a' frame depth 7 ===")
frame = 0
for tt, td in og_fox_tags:
    if tt == 1:
        frame += 1
    elif tt == 26 and frame == og_a_frame:
        flags = td[0]
        depth = struct.unpack_from('<H', td, 1)[0]
        if depth == 7:
            print(f"  OG PO2: {td[:30].hex()} ({len(td)}B)")
            print(f"    flags=0x{flags:02x} depth={depth}")
            off = 3
            if flags & 0x02:
                cid = struct.unpack_from('<H', td, off)[0]
                print(f"    charId={cid}")
                off += 2
            # Parse matrix (bit-aligned)
            if flags & 0x04:
                # Matrix parsing is complex, just show raw bytes
                print(f"    matrix starts at offset {off}")
            break

frame = 0
for tt, td in rt_fox_tags:
    if tt == 1:
        frame += 1
    elif tt == 26 and frame == rt_a_frame:
        flags = td[0]
        depth = struct.unpack_from('<H', td, 1)[0]
        if depth == 7:
            print(f"  RT PO2: {td[:30].hex()} ({len(td)}B)")
            print(f"    flags=0x{flags:02x} depth={depth}")
            off = 3
            if flags & 0x02:
                cid = struct.unpack_from('<H', td, off)[0]
                print(f"    charId={cid}")
                off += 2
            break
