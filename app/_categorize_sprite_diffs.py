"""
Categorize all sprite timeline differences between OG and RT.
Focus on patterns that could prevent AS3 from detecting animation completion:
  - Missing/wrong depth assignments
  - Missing/wrong names (AS3 uses getChildByName)
  - Missing hasRatio (morph shape interpolation)
  - Extra/missing layers
  - Wrong PO2 flags
"""
import sys, os, struct, zlib
from collections import defaultdict, Counter

def parse_swf_all(path):
    with open(path, 'rb') as f:
        sig = f.read(3)
        f.read(1)  # version
        f.read(4)  # file_len
        rest = f.read()
    if sig == b'CWS':
        rest = zlib.decompress(rest)
    nbits = rest[0] >> 3
    rect_bytes = (5 + 4 * nbits + 7) // 8
    offset = rect_bytes + 4
    tags = []
    while offset < len(rest):
        if offset + 2 > len(rest): break
        tc = struct.unpack_from('<H', rest, offset)[0]; offset += 2
        tag_type = tc >> 6; length = tc & 0x3F
        if length == 0x3F:
            length = struct.unpack_from('<I', rest, offset)[0]; offset += 4
        data = rest[offset:offset + length]; offset += length
        tags.append((tag_type, data))
        if tag_type == 0: break
    return tags

def parse_sprite_inner(body):
    offset = 0; tags = []
    while offset < len(body):
        if offset + 2 > len(body): break
        tc = struct.unpack_from('<H', body, offset)[0]; offset += 2
        tag_type = tc >> 6; length = tc & 0x3F
        if length == 0x3F:
            if offset + 4 > len(body): break
            length = struct.unpack_from('<I', body, offset)[0]; offset += 4
        data = body[offset:offset + length]; offset += length
        tags.append((tag_type, data))
        if tag_type == 0: break
    return tags

def get_fingerprint(inner_tags):
    fc = 0; labels = []
    for t, d in inner_tags:
        if t == 1: fc += 1
        elif t == 43:
            n = d.find(0)
            labels.append((fc+1, d[:n].decode('utf-8','replace') if n >= 0 else d.decode('utf-8','replace')))
    return (fc, tuple(labels))

def parse_po2(data):
    if len(data) < 3: return {}
    flags = data[0]; depth = struct.unpack_from('<H', data, 1)[0]
    r = {'flags': flags, 'depth': depth, 'move': bool(flags & 0x01),
         'hasChar': bool(flags & 0x02), 'hasMatrix': bool(flags & 0x04),
         'hasCxform': bool(flags & 0x08), 'hasRatio': bool(flags & 0x10),
         'hasName': bool(flags & 0x20), 'hasClipDepth': bool(flags & 0x40)}
    off = 3
    if flags & 0x02:
        if off + 2 <= len(data): r['charId'] = struct.unpack_from('<H', data, off)[0]
    return r

def parse_po3(data):
    if len(data) < 4: return {}
    flags = struct.unpack_from('<H', data, 0)[0]
    depth = struct.unpack_from('<H', data, 2)[0]
    r = {'flags': flags & 0xFF, 'flags2': (flags >> 8) & 0xFF, 'depth': depth,
         'move': bool(flags & 0x01), 'hasChar': bool(flags & 0x02),
         'hasMatrix': bool(flags & 0x04), 'hasCxform': bool(flags & 0x08),
         'hasRatio': bool(flags & 0x10), 'hasName': bool(flags & 0x20),
         'hasClipDepth': bool(flags & 0x40),
         'hasFilters': bool(flags & 0x100), 'hasBlendMode': bool(flags & 0x200)}
    off = 4
    if flags & 0x02:
        if off + 2 <= len(data): r['charId'] = struct.unpack_from('<H', data, off)[0]
    return r

def analyze_frame_tags(inner_tags):
    """Build per-frame tag analysis."""
    frames = []; current = []; frame_num = 1
    for tag_type, data in inner_tags:
        if tag_type == 1:
            frames.append((frame_num, current)); current = []; frame_num += 1
        elif tag_type == 0: pass
        else: current.append((tag_type, data))
    return frames

def get_frame_po_summary(frame_tags):
    """Get sorted list of (depth, po_info) for a frame."""
    pos = []
    for t, d in frame_tags:
        if t == 26: pos.append(parse_po2(d))
        elif t == 70: pos.append(parse_po3(d))
    return sorted(pos, key=lambda p: p.get('depth', 0))

def main():
    og_path = sys.argv[1]
    rt_path = sys.argv[2]
    
    og_tags = parse_swf_all(og_path)
    rt_tags = parse_swf_all(rt_path)
    
    og_sprites = {}
    for t, d in og_tags:
        if t == 39 and len(d) >= 4:
            cid = struct.unpack_from('<H', d, 0)[0]
            og_sprites[cid] = parse_sprite_inner(d[4:])
    
    rt_sprites = {}
    for t, d in rt_tags:
        if t == 39 and len(d) >= 4:
            cid = struct.unpack_from('<H', d, 0)[0]
            rt_sprites[cid] = parse_sprite_inner(d[4:])
    
    # Match by fingerprint
    og_by_fp = {}
    for cid, inner in og_sprites.items():
        fp = get_fingerprint(inner)
        og_by_fp.setdefault(fp, []).append((cid, inner))
    rt_by_fp = {}
    for cid, inner in rt_sprites.items():
        fp = get_fingerprint(inner)
        rt_by_fp.setdefault(fp, []).append((cid, inner))
    
    # Categorize differences
    categories = Counter()
    details = defaultdict(list)

    for fp, og_list in og_by_fp.items():
        rt_list = rt_by_fp.get(fp, [])
        if not rt_list: continue
        
        for idx, (og_cid, og_inner) in enumerate(og_list):
            if idx >= len(rt_list): continue
            rt_cid, rt_inner = rt_list[idx]
            
            og_frames = analyze_frame_tags(og_inner)
            rt_frames = analyze_frame_tags(rt_inner)
            if len(og_frames) != len(rt_frames): continue
            
            sprite_issues = set()
            
            for fi in range(len(og_frames)):
                og_fn, og_tags_f = og_frames[fi]
                rt_fn, rt_tags_f = rt_frames[fi]
                
                # Count tag types
                og_tc = Counter(t for t, _ in og_tags_f)
                rt_tc = Counter(t for t, _ in rt_tags_f)
                
                # RO2 differences
                og_ro2 = [struct.unpack_from('<H', d, 0)[0] for t, d in og_tags_f if t == 28 and len(d) >= 2]
                rt_ro2 = [struct.unpack_from('<H', d, 0)[0] for t, d in rt_tags_f if t == 28 and len(d) >= 2]
                if sorted(og_ro2) != sorted(rt_ro2):
                    sprite_issues.add('wrong_ro2')
                
                # PO summary
                og_pos = get_frame_po_summary(og_tags_f)
                rt_pos = get_frame_po_summary(rt_tags_f)
                
                if len(og_pos) != len(rt_pos):
                    if len(og_pos) > len(rt_pos):
                        sprite_issues.add('missing_layers')
                    else:
                        sprite_issues.add('extra_layers')
                
                og_depths = set(p['depth'] for p in og_pos)
                rt_depths = set(p['depth'] for p in rt_pos)
                if og_depths != rt_depths:
                    sprite_issues.add('wrong_depths')
                
                # Flag differences (match by index since depths may differ)
                for oi, (op, rp) in enumerate(zip(og_pos, rt_pos)):
                    if op.get('hasRatio') and not rp.get('hasRatio'):
                        sprite_issues.add('missing_ratio')
                    if not op.get('hasRatio') and rp.get('hasRatio'):
                        sprite_issues.add('extra_ratio')
                    if op.get('hasCxform') and not rp.get('hasCxform'):
                        sprite_issues.add('missing_cxform')
                    if not op.get('hasCxform') and rp.get('hasCxform'):
                        sprite_issues.add('extra_cxform')
                    if op.get('hasName') and not rp.get('hasName'):
                        sprite_issues.add('missing_name')
                    if not op.get('hasName') and rp.get('hasName'):
                        sprite_issues.add('extra_name')
                    if op.get('hasChar') != rp.get('hasChar'):
                        sprite_issues.add('wrong_hasChar')
                    if op.get('move') != rp.get('move'):
                        sprite_issues.add('wrong_move_flag')
            
            if sprite_issues:
                for cat in sprite_issues:
                    categories[cat] += 1
                details[frozenset(sprite_issues)].append(
                    (og_cid, rt_cid, fp[0], len(fp[1]))
                )
    
    print("=== ISSUE CATEGORIES (how many sprites have each issue) ===")
    for cat, count in categories.most_common():
        print(f"  {cat}: {count} sprites")
    
    print(f"\n=== ISSUE COMBINATIONS ===")
    for combo, sprites in sorted(details.items(), key=lambda x: -len(x[1])):
        print(f"\n  {set(combo)} ({len(sprites)} sprites):")
        for og_cid, rt_cid, fc, nl in sprites[:5]:
            print(f"    OG={og_cid} RT={rt_cid} ({fc} frames, {nl} labels)")
        if len(sprites) > 5:
            print(f"    ...and {len(sprites)-5} more")
    
    # Deep dive: pick one 10-frame morph sprite and show frame-by-frame detail
    print("\n\n=== DEEP DIVE: First differing sprite with missing_layers ===")
    for fp, og_list in og_by_fp.items():
        rt_list = rt_by_fp.get(fp, [])
        if not rt_list: continue
        og_cid, og_inner = og_list[0]
        rt_cid, rt_inner = rt_list[0]
        og_frames = analyze_frame_tags(og_inner)
        rt_frames = analyze_frame_tags(rt_inner)
        if len(og_frames) != len(rt_frames): continue
        
        has_diff = False
        for fi in range(len(og_frames)):
            og_pos = get_frame_po_summary(og_frames[fi][1])
            rt_pos = get_frame_po_summary(rt_frames[fi][1])
            if len(og_pos) != len(rt_pos):
                has_diff = True
                break
        
        if not has_diff: continue
        
        print(f"OG cid={og_cid}, RT cid={rt_cid}, {fp[0]} frames")
        for fi in range(len(og_frames)):
            og_fn, og_ftags = og_frames[fi]
            rt_fn, rt_ftags = rt_frames[fi]
            
            og_ro2 = [struct.unpack_from('<H', d, 0)[0] for t, d in og_ftags if t == 28 and len(d) >= 2]
            rt_ro2 = [struct.unpack_from('<H', d, 0)[0] for t, d in rt_ftags if t == 28 and len(d) >= 2]
            
            og_pos = get_frame_po_summary(og_ftags)
            rt_pos = get_frame_po_summary(rt_ftags)
            
            def po_str(p):
                parts = [f"d={p['depth']}"]
                if p.get('hasChar'): parts.append(f"c={p.get('charId','?')}")
                if p.get('move'): parts.append('move')
                if p.get('hasMatrix'): parts.append('mtx')
                if p.get('hasCxform'): parts.append('cx')
                if p.get('hasRatio'): parts.append('ratio')
                if p.get('hasName'): parts.append('name')
                return ','.join(parts)
            
            print(f"\n  Frame {og_fn}:")
            if og_ro2: print(f"    OG RO2: {og_ro2}")
            if rt_ro2: print(f"    RT RO2: {rt_ro2}")
            for po in og_pos:
                print(f"    OG PO: {po_str(po)}")
            for po in rt_pos:
                print(f"    RT PO: {po_str(po)}")
        
        break  # Just one deep dive


if __name__ == '__main__':
    main()
