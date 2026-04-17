"""Compare OG vs RT fox.ssf PlaceObject2 flags/data at depth 7 in the fox sprite."""
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

def parse_tags(data, offset, end):
    tags = []
    pos = offset
    while pos < end:
        if pos + 2 > end:
            break
        code_and_len = struct.unpack_from('<H', data, pos)[0]
        tag_type = code_and_len >> 6
        tag_len = code_and_len & 0x3F
        pos += 2
        if tag_len == 0x3F:
            if pos + 4 > end:
                break
            tag_len = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        tag_data = data[pos:pos + tag_len]
        tags.append((tag_type, tag_data))
        pos += tag_len
        if tag_type == 0:
            break
    return tags

def find_sprite_by_id(data, target_id):
    """Find DefineSprite with the given ID."""
    pos = 8  # skip header
    # Skip past the SWF rect+framerate+framecount
    nbits = (data[pos] >> 3) & 0x1F
    rect_bits = 5 + nbits * 4
    rect_bytes = (rect_bits + 7) // 8
    pos += rect_bytes + 4  # rect + frameRate(2) + frameCount(2)
    
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
            if sprite_id == target_id:
                frame_count = struct.unpack_from('<H', data, tag_start + 2)[0]
                inner_tags = parse_tags(data, tag_start + 4, tag_start + tag_len)
                return sprite_id, frame_count, inner_tags
    return None

def find_symbol_class(data):
    """Find SymbolClass tag and return {name: charId} mapping."""
    pos = 8
    nbits = (data[pos] >> 3) & 0x1F
    rect_bits = 5 + nbits * 4
    rect_bytes = (rect_bits + 7) // 8
    pos += rect_bytes + 4
    
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
        if tag_type == 76:  # SymbolClass
            body = data[tag_start:tag_start + tag_len]
            count = struct.unpack_from('<H', body, 0)[0]
            off = 2
            result = {}
            for _ in range(count):
                cid = struct.unpack_from('<H', body, off)[0]
                off += 2
                end = body.index(0, off)
                name = body[off:end].decode('utf-8', errors='replace')
                off = end + 1
                result[name] = cid
            return result
    return {}

def parse_po2(tag_data):
    """Parse a PlaceObject2 tag body."""
    if len(tag_data) < 3:
        return {}
    flags = tag_data[0]
    depth = struct.unpack_from('<H', tag_data, 1)[0]
    result = {'flags': flags, 'depth': depth, 'move': bool(flags & 0x01),
              'hasChar': bool(flags & 0x02), 'hasMatrix': bool(flags & 0x04),
              'hasCxform': bool(flags & 0x08), 'hasRatio': bool(flags & 0x10),
              'hasName': bool(flags & 0x20), 'hasClipDepth': bool(flags & 0x40),
              'hasClipActions': bool(flags & 0x80)}
    off = 3
    if flags & 0x02:  # hasChar
        result['charId'] = struct.unpack_from('<H', tag_data, off)[0]
        off += 2
    # Skip matrix for now
    return result

# Actually, SWF PO2 flag bits may be different. Let me check by looking at OG data.
# OG has flags=0x36 = 0b00110110
# If bit layout is: move(0) char(1) matrix(2) cxform(3) ratio(4) name(5) clip(6) clipAct(7)
# 0x36 = bits 1,2,4,5 → hasChar, hasMatrix, hasRatio, hasName
# But OG should have cxform too (the diagnostic showed hasCxform)
# Let me try another bit layout:
# If 0x36 = bits 1,2,4,5 and the OG had hasColorTransform...
# Let me just dump raw and figure it out from the data

def analyze_fox_sprite(label, data):
    sym = find_symbol_class(data)
    fox_name = None
    fox_id = None
    for name, cid in sym.items():
        if 'fox' in name.lower() and '.' not in name:
            fox_name = name
            fox_id = cid
            break
    if fox_id is None:
        # Try finding the biggest sprite
        for name, cid in sym.items():
            if name == 'fox':
                fox_id = cid
                fox_name = name
                break
    
    # Actually let's search for the sprite that contains 'stand' frame label
    # by iterating all sprites
    pos = 8
    nbits = (data[pos] >> 3) & 0x1F
    rect_bits = 5 + nbits * 4
    rect_bytes = (rect_bits + 7) // 8
    pos += rect_bytes + 4
    
    all_sprites = {}
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
            inner_tags = parse_tags(data, tag_start + 4, tag_start + tag_len)
            all_sprites[sprite_id] = (frame_count, inner_tags)
    
    # Find the fox sprite (has 'stand' label and lots of frames)
    fox_sprite_id = None
    for sid, (fc, itags) in all_sprites.items():
        for tt, td in itags:
            if tt == 43:  # FrameLabel
                lbl = td[:td.index(0)].decode('utf-8', errors='replace') if 0 in td else td.decode('utf-8', errors='replace')
                if lbl == 'stand':
                    if fc > 50:
                        fox_sprite_id = sid
                        break
        if fox_sprite_id:
            break
    
    if not fox_sprite_id:
        print(f"  [{label}] Could not find fox sprite!")
        return None, None
    
    fc, inner_tags = all_sprites[fox_sprite_id]
    print(f"  [{label}] Fox sprite ID={fox_sprite_id}, frameCount={fc}, innerTags={len(inner_tags)}")
    
    # Walk frame by frame
    frame = 0
    frames = {}
    cur_frame_tags = []
    for tt, td in inner_tags:
        if tt == 1:  # ShowFrame
            frames[frame] = cur_frame_tags
            cur_frame_tags = []
            frame += 1
        elif tt == 0:  # End
            break
        else:
            cur_frame_tags.append((tt, td))
    
    # Analyze each frame's PO2 for depth 7
    depth7_frames = {}
    for f_idx, f_tags in sorted(frames.items()):
        f_info = {'label': None, 'ro2': [], 'po2': [], 'other': []}
        for tt, td in f_tags:
            if tt == 43:  # FrameLabel
                lbl = td[:td.index(0)].decode('utf-8', errors='replace') if 0 in td else ''
                f_info['label'] = lbl
            elif tt == 28:  # RemoveObject2
                depth = struct.unpack_from('<H', td, 0)[0]
                f_info['ro2'].append(depth)
            elif tt == 26:  # PlaceObject2
                po = parse_po2(td)
                f_info['po2'].append(po)
            elif tt == 70:  # PlaceObject3
                # PO3 has 2 flag bytes
                if len(td) >= 4:
                    flags1 = td[0]
                    flags2 = td[1]
                    depth = struct.unpack_from('<H', td, 2)[0]
                    po = {'flags': flags1, 'flags2': flags2, 'depth': depth,
                           'move': bool(flags1 & 0x01), 'hasChar': bool(flags1 & 0x02),
                           'hasMatrix': bool(flags1 & 0x04), 'type': 'PO3',
                           'hasName': bool(flags1 & 0x20), 'size': len(td)}
                    off = 4
                    if flags1 & 0x02:
                        po['charId'] = struct.unpack_from('<H', td, off)[0]
                        off += 2
                    f_info['po2'].append(po)
            else:
                f_info['other'].append(tt)
        depth7_frames[f_idx] = f_info
    
    return depth7_frames, all_sprites

print("=== Loading SWF files ===")
og_data = read_swf(OG)
rt_data = read_swf(RT)
print(f"  OG: {len(og_data):,} bytes")
print(f"  RT: {len(rt_data):,} bytes")

print()
print("=== Analyzing fox sprite ===")
og_frames, og_sprites = analyze_fox_sprite("OG", og_data)
rt_frames, rt_sprites = analyze_fox_sprite("RT", rt_data)

if not og_frames or not rt_frames:
    sys.exit(1)

print()
print("=== Frame-by-frame comparison of depth-7 PO2 ===")
print(f"{'Frame':>5} {'Label':<20} {'OG_RO2':>6} {'RT_RO2':>6} {'OG_PO2_flags':<15} {'RT_PO2_flags':<15} {'OG_name':>8} {'RT_name':>8} {'OG_cx':>5} {'RT_cx':>5} {'OG_char':>8} {'RT_char':>8} {'Match':>5}")

mismatches = []
for f_idx in sorted(set(list(og_frames.keys()) + list(rt_frames.keys()))):
    og_f = og_frames.get(f_idx, {'label': None, 'ro2': [], 'po2': [], 'other': []})
    rt_f = rt_frames.get(f_idx, {'label': None, 'ro2': [], 'po2': [], 'other': []})
    
    label = og_f['label'] or rt_f['label'] or ''
    og_ro2_d7 = sum(1 for d in og_f['ro2'] if d == 7)
    rt_ro2_d7 = sum(1 for d in rt_f['ro2'] if d == 7)
    
    og_po2_d7 = [p for p in og_f['po2'] if p.get('depth') == 7]
    rt_po2_d7 = [p for p in rt_f['po2'] if p.get('depth') == 7]
    
    og_flags = f"0x{og_po2_d7[0]['flags']:02x}" if og_po2_d7 else '-'
    rt_flags = f"0x{rt_po2_d7[0]['flags']:02x}" if rt_po2_d7 else '-'
    
    og_name = 'Y' if og_po2_d7 and og_po2_d7[0].get('hasName') else 'N'
    rt_name = 'Y' if rt_po2_d7 and rt_po2_d7[0].get('hasName') else 'N'
    
    og_cx = 'Y' if og_po2_d7 and og_po2_d7[0].get('hasCxform') else 'N'
    rt_cx = 'Y' if rt_po2_d7 and rt_po2_d7[0].get('hasCxform') else 'N'
    
    og_char = str(og_po2_d7[0].get('charId', '?')) if og_po2_d7 else '-'
    rt_char = str(rt_po2_d7[0].get('charId', '?')) if rt_po2_d7 else '-'
    
    og_move = og_po2_d7[0].get('move', False) if og_po2_d7 else False
    rt_move = rt_po2_d7[0].get('move', False) if rt_po2_d7 else False
    
    match = 'OK' if (og_ro2_d7 == rt_ro2_d7 and og_name == rt_name and 
                     og_move == rt_move) else 'DIFF'
    
    if match == 'DIFF' or (label and f_idx < 30):
        print(f"{f_idx:>5} {label:<20} {og_ro2_d7:>6} {rt_ro2_d7:>6} {og_flags:<15} {rt_flags:<15} {og_name:>8} {rt_name:>8} {og_cx:>5} {rt_cx:>5} {og_char:>8} {rt_char:>8} {match:>5}")
    if match == 'DIFF':
        mismatches.append(f_idx)

# Count totals
og_ro2_total = sum(sum(1 for d in f['ro2'] if d == 7) for f in og_frames.values())
rt_ro2_total = sum(sum(1 for d in f['ro2'] if d == 7) for f in rt_frames.values())
og_po2_d7_total = sum(len([p for p in f['po2'] if p.get('depth') == 7]) for f in og_frames.values())
rt_po2_d7_total = sum(len([p for p in f['po2'] if p.get('depth') == 7]) for f in rt_frames.values())

print()
print(f"  Totals: OG RO2@d7={og_ro2_total}, RT RO2@d7={rt_ro2_total}")
print(f"  Totals: OG PO2@d7={og_po2_d7_total}, RT PO2@d7={rt_po2_d7_total}")
print(f"  Mismatches: {len(mismatches)} frames")

# Now check child sprite frame counts
print()
print("=== Child sprite comparison (charId placed at depth 7) ===")
og_child_ids = set()
rt_child_ids = set()
for f_idx, f in og_frames.items():
    for po in f['po2']:
        if po.get('depth') == 7 and 'charId' in po:
            og_child_ids.add(po['charId'])
for f_idx, f in rt_frames.items():
    for po in f['po2']:
        if po.get('depth') == 7 and 'charId' in po:
            rt_child_ids.add(po['charId'])

print(f"  OG: {len(og_child_ids)} unique child sprites at depth 7")
print(f"  RT: {len(rt_child_ids)} unique child sprites at depth 7")

# Compare frame counts of first few children (the 'stand' sprite)
print()
print("=== First 10 child sprites at depth 7 - frame counts ===")
og_children_by_frame = []
for f_idx in sorted(og_frames.keys()):
    for po in og_frames[f_idx]['po2']:
        if po.get('depth') == 7 and 'charId' in po:
            label = og_frames[f_idx].get('label', '')
            if not og_children_by_frame or og_children_by_frame[-1][0] != po['charId']:
                og_children_by_frame.append((po['charId'], f_idx, label))

rt_children_by_frame = []
for f_idx in sorted(rt_frames.keys()):
    for po in rt_frames[f_idx]['po2']:
        if po.get('depth') == 7 and 'charId' in po:
            label = rt_frames[f_idx].get('label', '')
            if not rt_children_by_frame or rt_children_by_frame[-1][0] != po['charId']:
                rt_children_by_frame.append((po['charId'], f_idx, label))

print(f"{'Frame':<6} {'Label':<20} {'OG_charId':>10} {'OG_frames':>10} {'RT_charId':>10} {'RT_frames':>10} {'Match':>6}")
for i in range(min(15, len(og_children_by_frame), len(rt_children_by_frame))):
    og_cid, og_f, og_lbl = og_children_by_frame[i]
    rt_cid, rt_f, rt_lbl = rt_children_by_frame[i]
    
    og_fc = og_sprites.get(og_cid, (0, []))[0]
    rt_fc = rt_sprites.get(rt_cid, (0, []))[0]
    
    label = og_lbl or rt_lbl
    match = 'OK' if og_fc == rt_fc else 'DIFF'
    print(f"{og_f:<6} {label:<20} {og_cid:>10} {og_fc:>10} {rt_cid:>10} {rt_fc:>10} {match:>6}")

# Check the 'a' (attack) child specifically
print()
print("=== 'a' (attack) child sprite deep comparison ===")
og_a_cid = None
rt_a_cid = None
for cid, f_idx, lbl in og_children_by_frame:
    if lbl == 'a':
        og_a_cid = cid
        break
for cid, f_idx, lbl in rt_children_by_frame:
    if lbl == 'a':
        rt_a_cid = cid
        break

if og_a_cid and rt_a_cid:
    og_a_fc, og_a_tags = og_sprites.get(og_a_cid, (0, []))
    rt_a_fc, rt_a_tags = rt_sprites.get(rt_a_cid, (0, []))
    
    print(f"  OG 'a' child: charId={og_a_cid}, frameCount={og_a_fc}, inner_tags={len(og_a_tags)}")
    print(f"  RT 'a' child: charId={rt_a_cid}, frameCount={rt_a_fc}, inner_tags={len(rt_a_tags)}")
    
    # Tag type breakdown
    og_tag_types = {}
    rt_tag_types = {}
    for tt, td in og_a_tags:
        og_tag_types[tt] = og_tag_types.get(tt, 0) + 1
    for tt, td in rt_a_tags:
        rt_tag_types[tt] = rt_tag_types.get(tt, 0) + 1
    
    all_types = sorted(set(list(og_tag_types.keys()) + list(rt_tag_types.keys())))
    print(f"  Tag type breakdown:")
    tag_names = {0: 'End', 1: 'ShowFrame', 26: 'PlaceObject2', 28: 'RemoveObject2',
                 43: 'FrameLabel', 70: 'PlaceObject3', 39: 'DefineSprite',
                 15: 'StartSound', 18: 'SoundStreamHead', 45: 'SoundStreamHead2',
                 19: 'SoundStreamBlock', 12: 'DoAction'}
    for tt in all_types:
        og_c = og_tag_types.get(tt, 0)
        rt_c = rt_tag_types.get(tt, 0)
        name = tag_names.get(tt, f'Tag{tt}')
        match = '  ' if og_c == rt_c else '!!'
        print(f"    {match} {name:>20} ({tt:>3}): OG={og_c:>4}, RT={rt_c:>4}")

# Check ALL child sprites for frame count differences  
print()
print("=== Frame count comparison across ALL child sprites ===")
fc_match = 0
fc_diff = 0
fc_diff_list = []
for i in range(min(len(og_children_by_frame), len(rt_children_by_frame))):
    og_cid, og_f, og_lbl = og_children_by_frame[i]
    rt_cid, rt_f, rt_lbl = rt_children_by_frame[i]
    og_fc = og_sprites.get(og_cid, (0, []))[0]
    rt_fc = rt_sprites.get(rt_cid, (0, []))[0]
    if og_fc == rt_fc:
        fc_match += 1
    else:
        fc_diff += 1
        lbl = og_lbl or rt_lbl
        fc_diff_list.append((lbl, og_fc, rt_fc))

print(f"  Frame count matches: {fc_match}")
print(f"  Frame count diffs: {fc_diff}")
if fc_diff_list:
    for lbl, ofc, rfc in fc_diff_list[:20]:
        print(f"    {lbl:<25}: OG={ofc}, RT={rfc}")
