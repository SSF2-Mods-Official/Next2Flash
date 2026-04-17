"""Deep compare OG vs RT smashville — instance names, RemoveObject2, PO flags."""
import sys, os, struct, zlib
sys.path.insert(0, os.path.dirname(__file__))
from swf_binary_io import BitReader

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\stage\smashville.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\stage\smashville.ssf"

def decompress_swf(raw):
    sig = raw[:3]
    if sig == b'CWS': return raw[:8] + zlib.decompress(raw[8:])
    return raw

def get_offset(data):
    br = BitReader(data, 8)
    nb = br.read_ub(5)
    for _ in range(4): br.read_sb(nb)
    br.align()
    return br.byte_pos + 4

def parse_tags(data, offset):
    tags = []
    while offset < len(data):
        if offset + 2 > len(data): break
        tag_code_and_length = struct.unpack_from('<H', data, offset)[0]
        tag_type = tag_code_and_length >> 6
        tag_length = tag_code_and_length & 0x3F
        offset += 2
        if tag_length == 0x3F:
            if offset + 4 > len(data): break
            tag_length = struct.unpack_from('<I', data, offset)[0]
            offset += 4
        tag_data = data[offset:offset + tag_length]
        tags.append((tag_type, tag_data))
        offset += tag_length
        if tag_type == 0: break
    return tags

def parse_symbol_class(tag_data):
    result = {}
    off = 0
    count = struct.unpack_from('<H', tag_data, off)[0]
    off += 2
    for _ in range(count):
        cid = struct.unpack_from('<H', tag_data, off)[0]
        off += 2
        end = tag_data.index(0, off)
        name = tag_data[off:end].decode('utf-8', errors='replace')
        off = end + 1
        result[cid] = name
    return result

def parse_frame_label(tag_data):
    end = tag_data.index(0)
    return tag_data[:end].decode('utf-8', errors='replace')

def parse_po2(data):
    """Parse PlaceObject2 — returns dict with flags, depth, char_id, name, etc."""
    if len(data) < 3: return {}
    flags = data[0]
    depth = struct.unpack_from('<H', data, 1)[0]
    off = 3
    result = {'flags': flags, 'depth': depth, 'is_move': bool(flags & 0x01),
              'has_cid': bool(flags & 0x02), 'has_matrix': bool(flags & 0x04),
              'has_cx': bool(flags & 0x08), 'has_ratio': bool(flags & 0x10),
              'has_name': bool(flags & 0x20), 'has_clip': bool(flags & 0x40)}
    if flags & 0x02:  # HasCharacter
        result['char_id'] = struct.unpack_from('<H', data, off)[0]
        off += 2
    if flags & 0x04:  # HasMatrix — skip it
        br = BitReader(data, off)
        # ScaleX/Y
        has_scale = br.read_ub(1)
        if has_scale:
            nb = br.read_ub(5)
            br.read_sb(nb)
            br.read_sb(nb)
        has_rotate = br.read_ub(1)
        if has_rotate:
            nb = br.read_ub(5)
            br.read_sb(nb)
            br.read_sb(nb)
        nb = br.read_ub(5)
        br.read_sb(nb)
        br.read_sb(nb)
        br.align()
        off = br.byte_pos
    if flags & 0x08:  # HasColorTransform — skip
        br = BitReader(data, off)
        has_add = br.read_ub(1)
        has_mult = br.read_ub(1)
        nb = br.read_ub(4)
        n = 0
        if has_mult: n += 4
        if has_add: n += 4
        for _ in range(n):
            br.read_sb(nb)
        br.align()
        off = br.byte_pos
    if flags & 0x10:  # HasRatio
        result['ratio'] = struct.unpack_from('<H', data, off)[0]
        off += 2
    if flags & 0x20:  # HasName
        end = data.index(0, off)
        result['name'] = data[off:end].decode('utf-8', errors='replace')
        off = end + 1
    if flags & 0x40:  # HasClipDepth
        result['clip_depth'] = struct.unpack_from('<H', data, off)[0]
        off += 2
    return result

def parse_po3(data):
    """Parse PlaceObject3 — returns dict with flags, depth, char_id, name, etc."""
    if len(data) < 4: return {}
    flags = struct.unpack_from('<H', data, 0)[0]
    depth = struct.unpack_from('<H', data, 2)[0]
    off = 4
    result = {'flags': flags, 'depth': depth, 'is_move': bool(flags & 0x01),
              'has_cid': bool(flags & 0x02), 'has_matrix': bool(flags & 0x04),
              'has_cx': bool(flags & 0x08), 'has_ratio': bool(flags & 0x10),
              'has_name': bool(flags & 0x20), 'has_clip': bool(flags & 0x40),
              'has_filters': bool(flags & 0x100), 'has_blend': bool(flags & 0x200)}
    # Skip className if present (bit 11)
    if flags & 0x800:
        end = data.index(0, off)
        result['className'] = data[off:end].decode('utf-8', errors='replace')
        off = end + 1
    if flags & 0x02:
        result['char_id'] = struct.unpack_from('<H', data, off)[0]
        off += 2
    if flags & 0x04:
        br = BitReader(data, off)
        has_scale = br.read_ub(1)
        if has_scale:
            nb = br.read_ub(5)
            br.read_sb(nb)
            br.read_sb(nb)
        has_rotate = br.read_ub(1)
        if has_rotate:
            nb = br.read_ub(5)
            br.read_sb(nb)
            br.read_sb(nb)
        nb = br.read_ub(5)
        br.read_sb(nb)
        br.read_sb(nb)
        br.align()
        off = br.byte_pos
    if flags & 0x08:
        br = BitReader(data, off)
        has_add = br.read_ub(1)
        has_mult = br.read_ub(1)
        nb = br.read_ub(4)
        n = 0
        if has_mult: n += 4
        if has_add: n += 4
        for _ in range(n):
            br.read_sb(nb)
        br.align()
        off = br.byte_pos
    if flags & 0x10:
        result['ratio'] = struct.unpack_from('<H', data, off)[0]
        off += 2
    if flags & 0x20:
        end = data.index(0, off)
        result['name'] = data[off:end].decode('utf-8', errors='replace')
        off = end + 1
    if flags & 0x40:
        result['clip_depth'] = struct.unpack_from('<H', data, off)[0]
        off += 2
    return result

def analyze_sprite(inner_tags, symbols):
    """Analyze a sprite's inner tags — frame by frame."""
    frames = []
    cur_frame = {'removes': [], 'places': [], 'label': None, 'action': False}
    
    for tag_type, tag_data in inner_tags:
        if tag_type == 1:  # ShowFrame
            frames.append(cur_frame)
            cur_frame = {'removes': [], 'places': [], 'label': None, 'action': False}
        elif tag_type == 28:  # RemoveObject2
            depth = struct.unpack_from('<H', tag_data, 0)[0]
            cur_frame['removes'].append(depth)
        elif tag_type == 26:  # PlaceObject2
            po = parse_po2(tag_data)
            sym = symbols.get(po.get('char_id'), '?')
            po['symbol'] = sym
            cur_frame['places'].append(po)
        elif tag_type == 70:  # PlaceObject3
            po = parse_po3(tag_data)
            sym = symbols.get(po.get('char_id'), '?')
            po['symbol'] = sym
            cur_frame['places'].append(po)
        elif tag_type == 43:  # FrameLabel
            cur_frame['label'] = parse_frame_label(tag_data)
        elif tag_type == 12:  # DoAction
            cur_frame['action'] = True
    return frames

def load_file(path):
    with open(path, 'rb') as f:
        raw = f.read()
    data = decompress_swf(raw)
    offset = get_offset(data)
    tags = parse_tags(data, offset)
    symbols = {}
    for tt, td in tags:
        if tt == 76:
            symbols.update(parse_symbol_class(td))
    sprites = {}
    for tt, td in tags:
        if tt == 39:
            cid = struct.unpack_from('<H', td, 0)[0]
            fc = struct.unpack_from('<H', td, 2)[0]
            inner = parse_tags(td, 4)
            sprites[cid] = (fc, inner)
    return tags, symbols, sprites

print("Loading OG...")
og_tags, og_symbols, og_sprites = load_file(OG)
print("Loading RT...")
rt_tags, rt_symbols, rt_sprites = load_file(RT)

# Reverse maps
og_sym_to_cid = {v: k for k, v in og_symbols.items()}
rt_sym_to_cid = {v: k for k, v in rt_symbols.items()}

# ── Compare key sprites ──
KEY_SPRITES = [
    'stage_smashville',
    'smashville_bg',
    'smashville_fla.smashvilleStage_10',
    'smashville_fla.SmashvilleLighting_47',
    'smashville_fla.svforegroundmc_45',
    'smashville_fla.smashvillePlatformForeground_46',
    'smashville_fla.smashvillePlatformBack_37',
    'smashville_fla.Smashville_mainGround_24',
]

for sym_name in KEY_SPRITES:
    og_cid = og_sym_to_cid.get(sym_name)
    rt_cid = rt_sym_to_cid.get(sym_name)
    if og_cid is None or rt_cid is None:
        print(f"\n{sym_name}: MISSING (OG={og_cid}, RT={rt_cid})")
        continue
    if og_cid not in og_sprites or rt_cid not in rt_sprites:
        print(f"\n{sym_name}: NOT A SPRITE")
        continue
    
    og_fc, og_inner = og_sprites[og_cid]
    rt_fc, rt_inner = rt_sprites[rt_cid]
    
    og_frames = analyze_sprite(og_inner, og_symbols)
    rt_frames = analyze_sprite(rt_inner, rt_symbols)
    
    print(f"\n{'='*60}")
    print(f"  {sym_name} (OG cid={og_cid}, RT cid={rt_cid})")
    print(f"  OG: {og_fc} frames ({len(og_frames)} ShowFrames), {len(og_inner)} tags")
    print(f"  RT: {rt_fc} frames ({len(rt_frames)} ShowFrames), {len(rt_inner)} tags")
    print(f"{'='*60}")
    
    # Compare frame by frame
    max_f = max(len(og_frames), len(rt_frames))
    diffs = 0
    for f_idx in range(max_f):
        og_f = og_frames[f_idx] if f_idx < len(og_frames) else None
        rt_f = rt_frames[f_idx] if f_idx < len(rt_frames) else None
        
        if og_f is None or rt_f is None:
            print(f"  Frame {f_idx+1}: MISSING in {'RT' if og_f else 'OG'}")
            diffs += 1
            continue
        
        # Compare labels
        if og_f['label'] != rt_f['label']:
            print(f"  Frame {f_idx+1}: LABEL DIFF: OG={og_f['label']!r} RT={rt_f['label']!r}")
            diffs += 1
        
        # Compare removes
        if sorted(og_f['removes']) != sorted(rt_f['removes']):
            print(f"  Frame {f_idx+1}: REMOVES DIFF:")
            print(f"    OG removes: {sorted(og_f['removes'])}")
            print(f"    RT removes: {sorted(rt_f['removes'])}")
            diffs += 1
        
        # Compare places (by depth)
        og_by_depth = {p['depth']: p for p in og_f['places']}
        rt_by_depth = {p['depth']: p for p in rt_f['places']}
        
        all_depths = sorted(set(og_by_depth.keys()) | set(rt_by_depth.keys()))
        for d in all_depths:
            og_p = og_by_depth.get(d)
            rt_p = rt_by_depth.get(d)
            
            if og_p is None:
                print(f"  Frame {f_idx+1} depth {d}: EXTRA in RT: is_move={rt_p.get('is_move')} cid={rt_p.get('char_id')} name={rt_p.get('name')!r} sym={rt_p.get('symbol')}")
                diffs += 1
                continue
            if rt_p is None:
                print(f"  Frame {f_idx+1} depth {d}: MISSING in RT: is_move={og_p.get('is_move')} cid={og_p.get('char_id')} name={og_p.get('name')!r} sym={og_p.get('symbol')}")
                diffs += 1
                continue
            
            # Compare key properties
            diff_parts = []
            if og_p.get('is_move') != rt_p.get('is_move'):
                diff_parts.append(f"is_move: OG={og_p.get('is_move')} RT={rt_p.get('is_move')}")
            if og_p.get('name') != rt_p.get('name'):
                diff_parts.append(f"name: OG={og_p.get('name')!r} RT={rt_p.get('name')!r}")
            if og_p.get('symbol') != rt_p.get('symbol'):
                # Symbols can differ in name but map to same semantics — check char ids resolve to same symbol
                diff_parts.append(f"symbol: OG={og_p.get('symbol')} RT={rt_p.get('symbol')}")
            if og_p.get('has_clip') != rt_p.get('has_clip') or og_p.get('clip_depth') != rt_p.get('clip_depth'):
                diff_parts.append(f"clipDepth: OG={og_p.get('clip_depth')} RT={rt_p.get('clip_depth')}")
            
            if diff_parts:
                print(f"  Frame {f_idx+1} depth {d}: {'; '.join(diff_parts)}")
                diffs += 1
    
    if diffs == 0:
        print("  No structural differences found!")
    else:
        print(f"\n  Total differences: {diffs}")

# ── Also compare root timeline ──
print(f"\n{'='*60}")
print("  ROOT TIMELINE COMPARISON")
print(f"{'='*60}")
og_root_frames = analyze_sprite(og_tags, og_symbols)
rt_root_frames = analyze_sprite(rt_tags, rt_symbols)
print(f"  OG: {len(og_root_frames)} frames")
print(f"  RT: {len(rt_root_frames)} frames")

for f_idx in range(max(len(og_root_frames), len(rt_root_frames))):
    og_f = og_root_frames[f_idx] if f_idx < len(og_root_frames) else None
    rt_f = rt_root_frames[f_idx] if f_idx < len(rt_root_frames) else None
    if og_f is None or rt_f is None:
        print(f"  Frame {f_idx+1}: MISSING in {'RT' if og_f else 'OG'}")
        continue
    
    print(f"\n  Frame {f_idx+1}:")
    print(f"    OG: {len(og_f['places'])} places, {len(og_f['removes'])} removes, label={og_f['label']!r}")
    print(f"    RT: {len(rt_f['places'])} places, {len(rt_f['removes'])} removes, label={rt_f['label']!r}")
    
    for p in og_f['places']:
        print(f"    OG place: depth={p['depth']} is_move={p.get('is_move')} cid={p.get('char_id')} name={p.get('name')!r} sym={p.get('symbol')} clip={p.get('clip_depth')}")
    for p in rt_f['places']:
        print(f"    RT place: depth={p['depth']} is_move={p.get('is_move')} cid={p.get('char_id')} name={p.get('name')!r} sym={p.get('symbol')} clip={p.get('clip_depth')}")
