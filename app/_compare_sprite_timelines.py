"""
Compare OG vs RT fox sprite timelines in detail.
Focus on: frame counts, RO2/PO2 patterns, frame labels, character placements.
Specifically look at attack animation frames to find looping cause.
"""
import sys, os, struct, zlib
from collections import defaultdict

def parse_swf_all(path):
    """Parse SWF and return all tags with their binary data."""
    with open(path, 'rb') as f:
        sig = f.read(3)
        version = struct.unpack('<B', f.read(1))[0]
        file_len = struct.unpack('<I', f.read(4))[0]
        rest = f.read()
    if sig == b'CWS':
        rest = zlib.decompress(rest)
    nbits = rest[0] >> 3
    rect_bytes = (5 + 4 * nbits + 7) // 8
    offset = rect_bytes + 4
    tags = []
    while offset < len(rest):
        if offset + 2 > len(rest):
            break
        tc = struct.unpack_from('<H', rest, offset)[0]
        offset += 2
        tag_type = tc >> 6
        length = tc & 0x3F
        if length == 0x3F:
            length = struct.unpack_from('<I', rest, offset)[0]
            offset += 4
        data = rest[offset:offset + length]
        offset += length
        tags.append((tag_type, data))
        if tag_type == 0:
            break
    return tags


def parse_sprite_inner_tags(body):
    """Parse inner tags of a DefineSprite body (after charId + frameCount)."""
    offset = 0
    tags = []
    while offset < len(body):
        if offset + 2 > len(body):
            break
        tc = struct.unpack_from('<H', body, offset)[0]
        offset += 2
        tag_type = tc >> 6
        length = tc & 0x3F
        if length == 0x3F:
            if offset + 4 > len(body):
                break
            length = struct.unpack_from('<I', body, offset)[0]
            offset += 4
        data = body[offset:offset + length]
        offset += length
        tags.append((tag_type, data))
        if tag_type == 0:
            break
    return tags


def parse_po2(data):
    """Parse PlaceObject2 tag: flags, depth, charId, matrix info."""
    if len(data) < 3:
        return {}
    flags = data[0]
    depth = struct.unpack_from('<H', data, 1)[0]
    result = {'flags': flags, 'depth': depth, 'move': bool(flags & 0x01)}
    off = 3
    if flags & 0x02:  # HasCharacter
        if off + 2 <= len(data):
            result['charId'] = struct.unpack_from('<H', data, off)[0]
            off += 2
    if flags & 0x04:  # HasMatrix
        result['hasMatrix'] = True
    if flags & 0x08:  # HasColorTransform
        result['hasCxform'] = True
    if flags & 0x10:  # HasRatio
        result['hasRatio'] = True
    if flags & 0x20:  # HasName
        result['hasName'] = True
    if flags & 0x40:  # HasClipDepth
        result['hasClipDepth'] = True
    if flags & 0x80:  # HasClipActions
        result['hasClipActions'] = True
    return result


def parse_po3(data):
    """Parse PlaceObject3 tag: 2-byte flags, depth, charId."""
    if len(data) < 4:
        return {}
    flags = struct.unpack_from('<H', data, 0)[0]
    depth = struct.unpack_from('<H', data, 2)[0]
    result = {'flags': flags, 'depth': depth, 'move': bool(flags & 0x01)}
    off = 4
    if flags & 0x02:  # HasCharacter
        if off + 2 <= len(data):
            result['charId'] = struct.unpack_from('<H', data, off)[0]
            off += 2
    if flags & 0x04:
        result['hasMatrix'] = True
    if flags & 0x08:
        result['hasCxform'] = True
    if flags & 0x10:
        result['hasRatio'] = True
    if flags & 0x20:
        result['hasName'] = True
    if flags & 0x40:
        result['hasClipDepth'] = True
    if flags & 0x80:
        result['hasClipActions'] = True
    if flags & 0x100:
        result['hasFilters'] = True
    if flags & 0x200:
        result['hasBlendMode'] = True
    return result


def parse_frame_label(data):
    """Parse FrameLabel tag."""
    null_pos = data.find(0)
    if null_pos >= 0:
        return data[:null_pos].decode('utf-8', errors='replace')
    return data.decode('utf-8', errors='replace')


def analyze_sprite(inner_tags, sprite_id):
    """Analyze a sprite's inner tags frame by frame."""
    frames = []
    current_frame = {'label': None, 'po2': [], 'po3': [], 'ro2': [], 'other': []}
    frame_num = 1
    
    for tag_type, data in inner_tags:
        if tag_type == 1:  # ShowFrame
            current_frame['num'] = frame_num
            frames.append(current_frame)
            frame_num += 1
            current_frame = {'label': None, 'po2': [], 'po3': [], 'ro2': [], 'other': []}
        elif tag_type == 43:  # FrameLabel
            current_frame['label'] = parse_frame_label(data)
        elif tag_type == 26:  # PlaceObject2
            current_frame['po2'].append(parse_po2(data))
        elif tag_type == 70:  # PlaceObject3
            current_frame['po3'].append(parse_po3(data))
        elif tag_type == 28:  # RemoveObject2
            if len(data) >= 2:
                depth = struct.unpack_from('<H', data, 0)[0]
                current_frame['ro2'].append(depth)
        elif tag_type == 0:  # End
            pass
        elif tag_type == 45:  # SoundStreamHead2
            pass
        elif tag_type == 19:  # SoundStreamBlock 
            pass
        else:
            current_frame['other'].append(tag_type)
    
    return frames


def find_fox_sprite(tags):
    """Find the main fox character sprite (largest frame count)."""
    sprites = {}
    for tag_type, data in tags:
        if tag_type == 39 and len(data) >= 4:  # DefineSprite
            char_id = struct.unpack_from('<H', data, 0)[0]
            frame_count = struct.unpack_from('<H', data, 2)[0]
            inner = parse_sprite_inner_tags(data[4:])
            sprites[char_id] = {
                'frameCount': frame_count,
                'innerTagCount': len(inner),
                'inner': inner,
            }
    
    # Find the sprite with the most frames (likely the main character)
    if sprites:
        main_cid = max(sprites, key=lambda k: sprites[k]['frameCount'])
        return main_cid, sprites[main_cid], sprites
    return None, None, sprites


def main():
    og_path = sys.argv[1]
    rt_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"=== OG: {og_path} ===")
    og_tags = parse_swf_all(og_path)
    og_main_cid, og_main, og_sprites = find_fox_sprite(og_tags)
    
    if og_main:
        print(f"Main sprite charId={og_main_cid}, frames={og_main['frameCount']}, "
              f"inner tags={og_main['innerTagCount']}")
        og_frames = analyze_sprite(og_main['inner'], og_main_cid)
        
        # Find frame labels
        labels = [(f['num'], f['label']) for f in og_frames if f['label']]
        print(f"Frame labels ({len(labels)}):")
        for num, label in labels[:30]:
            print(f"  frame {num}: '{label}'")
        if len(labels) > 30:
            print(f"  ...and {len(labels)-30} more")
        
        # Frame summary
        print(f"\nTotal analyzed frames: {len(og_frames)}")
        
        # Look at a few attack frames
        attack_labels = [l for l in labels if 'attack' in l[1].lower() or 'Attack' in l[1]]
        if attack_labels:
            print(f"\nAttack-related labels:")
            for num, label in attack_labels[:20]:
                print(f"  frame {num}: '{label}'")
        
        # Show depth activity for first few frames
        print(f"\nFirst 5 frames detail:")
        for f in og_frames[:5]:
            label_str = f" label='{f['label']}'" if f['label'] else ""
            print(f"  Frame {f['num']}{label_str}:")
            for ro in f['ro2']:
                print(f"    RO2 depth={ro}")
            for po in f['po2']:
                cid_str = f" charId={po.get('charId', '?')}" if 'charId' in po else ""
                flags = []
                if po.get('move'): flags.append('move')
                if po.get('hasMatrix'): flags.append('matrix')
                if po.get('hasCxform'): flags.append('cxform')
                if po.get('hasName'): flags.append('name')
                if po.get('hasRatio'): flags.append('ratio')
                print(f"    PO2 depth={po['depth']}{cid_str} [{','.join(flags)}]")
            for po in f['po3']:
                cid_str = f" charId={po.get('charId', '?')}" if 'charId' in po else ""
                flags = []
                if po.get('move'): flags.append('move')
                if po.get('hasMatrix'): flags.append('matrix')
                if po.get('hasCxform'): flags.append('cxform')
                if po.get('hasName'): flags.append('name')
                if po.get('hasRatio'): flags.append('ratio')
                if po.get('hasFilters'): flags.append('filters')
                if po.get('hasBlendMode'): flags.append('blend')
                print(f"    PO3 depth={po['depth']}{cid_str} [{','.join(flags)}]")
    
    print(f"\nTotal sprites: {len(og_sprites)}")
    # Frame count distribution
    fc_dist = defaultdict(int)
    for cid, sp in og_sprites.items():
        fc_dist[sp['frameCount']] += 1
    print("Frame count distribution:")
    for fc, count in sorted(fc_dist.items(), reverse=True)[:15]:
        print(f"  {fc} frames: {count} sprites")
    
    if not rt_path:
        return
    
    # === Compare with RT ===
    print(f"\n\n=== RT: {rt_path} ===")
    rt_tags = parse_swf_all(rt_path)
    rt_main_cid, rt_main, rt_sprites = find_fox_sprite(rt_tags)
    
    if not rt_main:
        print("No main sprite found in RT!")
        return
    
    print(f"Main sprite charId={rt_main_cid}, frames={rt_main['frameCount']}, "
          f"inner tags={rt_main['innerTagCount']}")
    rt_frames = analyze_sprite(rt_main['inner'], rt_main_cid)
    
    rt_labels = [(f['num'], f['label']) for f in rt_frames if f['label']]
    print(f"Frame labels ({len(rt_labels)}):")
    for num, label in rt_labels[:30]:
        print(f"  frame {num}: '{label}'")
    
    # Compare frame counts
    print(f"\n=== COMPARISON ===")
    print(f"OG frames: {len(og_frames)}, RT frames: {len(rt_frames)}")
    print(f"OG labels: {len(labels)}, RT labels: {len(rt_labels)}")
    
    # Compare labels
    og_label_set = set(l[1] for l in labels)
    rt_label_set = set(l[1] for l in rt_labels)
    missing = og_label_set - rt_label_set
    extra = rt_label_set - og_label_set
    if missing:
        print(f"Labels in OG but NOT in RT: {missing}")
    if extra:
        print(f"Labels in RT but NOT in OG: {extra}")
    
    # Compare frame-by-frame for first N frames and any attack frames
    print(f"\n=== Frame-by-frame comparison (first 10 + attack frames) ===")
    check_frames = list(range(min(10, len(og_frames))))
    # Add attack frame indices
    for i, f in enumerate(og_frames):
        if f.get('label') and ('attack' in f['label'].lower() or 'Attack' in f['label']):
            for j in range(max(0, i-1), min(len(og_frames), i+5)):
                if j not in check_frames:
                    check_frames.append(j)
    check_frames.sort()
    
    for idx in check_frames:
        if idx >= len(og_frames) or idx >= len(rt_frames):
            break
        og_f = og_frames[idx]
        rt_f = rt_frames[idx]
        
        # Compare
        diffs = []
        if og_f.get('label') != rt_f.get('label'):
            diffs.append(f"label: OG='{og_f.get('label')}' RT='{rt_f.get('label')}'")
        if len(og_f['ro2']) != len(rt_f['ro2']):
            diffs.append(f"RO2 count: OG={len(og_f['ro2'])} RT={len(rt_f['ro2'])}")
        og_po_count = len(og_f['po2']) + len(og_f['po3'])
        rt_po_count = len(rt_f['po2']) + len(rt_f['po3'])
        if og_po_count != rt_po_count:
            diffs.append(f"PO count: OG={og_po_count} RT={rt_po_count}")
        
        # Check PO2 details
        og_po_all = og_f['po2'] + og_f['po3']
        rt_po_all = rt_f['po2'] + rt_f['po3']
        
        # Compare by depth
        og_by_depth = {po['depth']: po for po in og_po_all}
        rt_by_depth = {po['depth']: po for po in rt_po_all}
        
        for depth in sorted(set(list(og_by_depth.keys()) + list(rt_by_depth.keys()))):
            og_po = og_by_depth.get(depth)
            rt_po = rt_by_depth.get(depth)
            if og_po and not rt_po:
                diffs.append(f"  depth={depth}: OG has PO, RT missing")
            elif rt_po and not og_po:
                diffs.append(f"  depth={depth}: RT has PO, OG missing")
            elif og_po and rt_po:
                if og_po.get('move') != rt_po.get('move'):
                    diffs.append(f"  depth={depth}: move OG={og_po.get('move')} RT={rt_po.get('move')}")
                og_cid = og_po.get('charId')
                rt_cid = rt_po.get('charId')
                # charIds will differ (renumbered), but presence should match
                if (og_cid is not None) != (rt_cid is not None):
                    diffs.append(f"  depth={depth}: hasChar OG={og_cid is not None} RT={rt_cid is not None}")
        
        if diffs:
            label_str = f" '{og_f.get('label')}'" if og_f.get('label') else ""
            print(f"Frame {idx+1}{label_str}: DIFFERS")
            for d in diffs:
                print(f"  {d}")


if __name__ == '__main__':
    main()
