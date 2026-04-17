"""Compare OG vs RT smashville.ssf — look for troublesome differences."""
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
    """Parse SymbolClass tag → {charId: className}"""
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

TAG_NAMES = {
    0: 'End', 1: 'ShowFrame', 4: 'PlaceObject', 5: 'RemoveObject',
    9: 'SetBackgroundColor', 12: 'DoAction', 26: 'PlaceObject2',
    28: 'RemoveObject2', 39: 'DefineSprite', 43: 'FrameLabel',
    69: 'FileAttributes', 70: 'PlaceObject3', 76: 'SymbolClass',
    82: 'DoABC', 86: 'DefineSceneAndFrameLabelData',
}

def analyze_file(label, path):
    with open(path, 'rb') as f:
        raw = f.read()
    print(f"\n{'='*60}")
    print(f"  {label}: {os.path.basename(path)} ({len(raw):,} bytes)")
    print(f"{'='*60}")
    
    data = decompress_swf(raw)
    print(f"  Decompressed: {len(data):,} bytes")
    
    # Header
    version = data[3]
    offset = get_offset(data)
    fps_raw = struct.unpack_from('<H', data, offset - 4)[0]
    fps = fps_raw >> 8
    frame_count = struct.unpack_from('<H', data, offset - 2)[0]
    print(f"  SWF version: {version}, FPS: {fps}, Frames: {frame_count}")
    
    tags = parse_tags(data, offset)
    
    # Count tag types
    tag_counts = {}
    for tt, td in tags:
        tag_counts[tt] = tag_counts.get(tt, 0) + 1
    print(f"  Total tags: {len(tags)}")
    for tt in sorted(tag_counts):
        nm = TAG_NAMES.get(tt, f'Tag{tt}')
        print(f"    {nm}({tt}): {tag_counts[tt]}")
    
    # SymbolClass
    symbols = {}
    for tt, td in tags:
        if tt == 76:
            symbols.update(parse_symbol_class(td))
    
    # Root timeline labels
    root_labels = []
    frame = 0
    for tt, td in tags:
        if tt == 43:
            lbl = parse_frame_label(td)
            root_labels.append((frame + 1, lbl))
        elif tt == 1:
            frame += 1
    
    print(f"\n  Root timeline labels: {root_labels}")
    print(f"  SymbolClass entries: {len(symbols)}")
    for cid, name in sorted(symbols.items()):
        print(f"    {cid}: {name}")
    
    # Sprites — find ones with labels related to time of day
    sprites = {}
    for tt, td in tags:
        if tt == 39:
            cid = struct.unpack_from('<H', td, 0)[0]
            fc = struct.unpack_from('<H', td, 2)[0]
            inner = parse_tags(td, 4)
            sprites[cid] = (fc, inner)
    
    print(f"\n  DefineSprite count: {len(sprites)}")
    
    # Find sprites with 'day'/'night'/'decide' labels
    for cid, (fc, inner) in sorted(sprites.items()):
        labels = []
        f = 0
        for itt, itd in inner:
            if itt == 43:
                lbl = parse_frame_label(itd)
                labels.append((f + 1, lbl))
            elif itt == 1:
                f += 1
        
        has_time = any(kw in lbl.lower() for _, lbl in labels 
                      for kw in ['day', 'night', 'decide', 'dusk', 'dawn', 'time', 'morning', 'evening', 'sunset'])
        if has_time or len(labels) > 3:
            sym_name = symbols.get(cid, '?')
            print(f"\n  Sprite cid={cid} ({sym_name}): {fc} frames, {len(inner)} tags")
            print(f"    Labels: {labels}")
    
    return data, tags, sprites, symbols

og_data, og_tags, og_sprites, og_symbols = analyze_file("OG", OG)
rt_data, rt_tags, rt_sprites, rt_symbols = analyze_file("RT", RT)

# Build reverse maps: symbol name → charId
og_sym_to_cid = {v: k for k, v in og_symbols.items()}
rt_sym_to_cid = {v: k for k, v in rt_symbols.items()}

# Compare sprites that exist in both by symbol name
print(f"\n\n{'='*60}")
print("  COMPARISON: Sprites with label differences")
print(f"{'='*60}")

for sym_name in sorted(set(og_sym_to_cid.keys()) & set(rt_sym_to_cid.keys())):
    og_cid = og_sym_to_cid[sym_name]
    rt_cid = rt_sym_to_cid[sym_name]
    
    if og_cid not in og_sprites or rt_cid not in rt_sprites:
        continue
    
    og_fc, og_inner = og_sprites[og_cid]
    rt_fc, rt_inner = rt_sprites[rt_cid]
    
    # Get labels
    def get_labels(inner):
        labels = []
        f = 0
        for tt, td in inner:
            if tt == 43:
                labels.append((f + 1, parse_frame_label(td)))
            elif tt == 1:
                f += 1
        return labels
    
    og_labels = get_labels(og_inner)
    rt_labels = get_labels(rt_inner)
    
    if og_labels != rt_labels or og_fc != rt_fc:
        print(f"\n  {sym_name}:")
        print(f"    OG: {og_fc} frames, labels={og_labels}")
        print(f"    RT: {rt_fc} frames, labels={rt_labels}")
        if og_fc != rt_fc:
            print(f"    *** FRAME COUNT MISMATCH: {og_fc} vs {rt_fc} ***")
