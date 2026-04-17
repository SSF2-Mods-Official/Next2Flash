"""
Deep compare ALL sprites between OG and RT SWFs.
Match sprites by frame count + frame labels (since charIDs differ).
Report any timeline differences: missing/extra tags, different PO2 flags, etc.
"""
import sys, os, struct, zlib
from collections import defaultdict

def parse_swf_all(path):
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

def parse_sprite_inner(body):
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

def get_sprite_fingerprint(inner_tags):
    """Build a fingerprint: (frame_count, tuple_of_labels)."""
    frame_count = 0
    labels = []
    for tag_type, data in inner_tags:
        if tag_type == 1:
            frame_count += 1
        elif tag_type == 43:
            null_pos = data.find(0)
            label = data[:null_pos].decode('utf-8', errors='replace') if null_pos >= 0 else data.decode('utf-8', errors='replace')
            labels.append((frame_count + 1, label))
    return (frame_count, tuple(labels))

def analyze_frames(inner_tags):
    """Break inner tags into per-frame tag lists."""
    frames = []
    current = []
    for tag_type, data in inner_tags:
        if tag_type == 1:  # ShowFrame
            frames.append(current)
            current = []
        elif tag_type == 0:  # End
            pass
        else:
            current.append((tag_type, data))
    return frames

TAG_NAMES = {
    1: 'ShowFrame', 26: 'PlaceObject2', 28: 'RemoveObject2',
    43: 'FrameLabel', 45: 'SoundStreamHead2', 19: 'SoundStreamBlock',
    70: 'PlaceObject3', 0: 'End', 12: 'DoAction',
}

def tag_summary(tag_type, data):
    name = TAG_NAMES.get(tag_type, f'Tag{tag_type}')
    if tag_type == 26:  # PO2
        flags = data[0] if data else 0
        depth = struct.unpack_from('<H', data, 1)[0] if len(data) >= 3 else 0
        parts = [f'd={depth}']
        off = 3
        if flags & 0x02:
            cid = struct.unpack_from('<H', data, off)[0] if off + 2 <= len(data) else '?'
            parts.append(f'c={cid}')
            off += 2
        if flags & 0x01: parts.append('move')
        if flags & 0x04: parts.append('mtx')
        if flags & 0x08: parts.append('cx')
        if flags & 0x10: parts.append('ratio')
        if flags & 0x20: parts.append('name')
        return f'PO2({",".join(parts)})'
    elif tag_type == 70:  # PO3
        if len(data) < 4:
            return 'PO3(?)'
        flags = struct.unpack_from('<H', data, 0)[0]
        depth = struct.unpack_from('<H', data, 2)[0]
        parts = [f'd={depth}']
        off = 4
        if flags & 0x02:
            cid = struct.unpack_from('<H', data, off)[0] if off + 2 <= len(data) else '?'
            parts.append(f'c={cid}')
            off += 2
        if flags & 0x01: parts.append('move')
        if flags & 0x04: parts.append('mtx')
        if flags & 0x08: parts.append('cx')
        if flags & 0x10: parts.append('ratio')
        if flags & 0x20: parts.append('name')
        return f'PO3({",".join(parts)})'
    elif tag_type == 28:  # RO2
        depth = struct.unpack_from('<H', data, 0)[0] if len(data) >= 2 else '?'
        return f'RO2(d={depth})'
    elif tag_type == 43:
        null_pos = data.find(0)
        label = data[:null_pos].decode('utf-8', errors='replace') if null_pos >= 0 else '?'
        return f'Label({label})'
    return name

def compare_frame_tags(og_frame_tags, rt_frame_tags, frame_num):
    """Compare tag lists for a single frame. Returns list of difference strings."""
    diffs = []
    
    # Normalize: remove SoundStreamBlock (tag 19) — those may differ in content
    og_filtered = [(t, d) for t, d in og_frame_tags if t != 19]
    rt_filtered = [(t, d) for t, d in rt_frame_tags if t != 19]
    
    if len(og_filtered) != len(rt_filtered):
        og_summary = [tag_summary(t, d) for t, d in og_filtered]
        rt_summary = [tag_summary(t, d) for t, d in rt_filtered]
        diffs.append(f"tag count: OG={len(og_filtered)} RT={len(rt_filtered)}")
        diffs.append(f"  OG: {og_summary}")
        diffs.append(f"  RT: {rt_summary}")
        return diffs
    
    for i, ((og_t, og_d), (rt_t, rt_d)) in enumerate(zip(og_filtered, rt_filtered)):
        if og_t != rt_t:
            diffs.append(f"  tag[{i}]: OG={tag_summary(og_t, og_d)} RT={tag_summary(rt_t, rt_d)}")
            continue
        
        # Same tag type — compare structural content (not charIDs or binary data)
        if og_t == 26:  # PO2
            og_flags = og_d[0] if og_d else 0
            rt_flags = rt_d[0] if rt_d else 0
            og_depth = struct.unpack_from('<H', og_d, 1)[0] if len(og_d) >= 3 else 0
            rt_depth = struct.unpack_from('<H', rt_d, 1)[0] if len(rt_d) >= 3 else 0
            if og_flags != rt_flags:
                diffs.append(f"  PO2 flags: OG=0x{og_flags:02x} RT=0x{rt_flags:02x} "
                           f"({tag_summary(og_t, og_d)} vs {tag_summary(rt_t, rt_d)})")
            if og_depth != rt_depth:
                diffs.append(f"  PO2 depth: OG={og_depth} RT={rt_depth}")
        elif og_t == 70:  # PO3
            og_flags = struct.unpack_from('<H', og_d, 0)[0] if len(og_d) >= 2 else 0
            rt_flags = struct.unpack_from('<H', rt_d, 0)[0] if len(rt_d) >= 2 else 0
            if og_flags != rt_flags:
                diffs.append(f"  PO3 flags: OG=0x{og_flags:04x} RT=0x{rt_flags:04x}")
        elif og_t == 28:  # RO2
            og_depth = struct.unpack_from('<H', og_d, 0)[0] if len(og_d) >= 2 else 0
            rt_depth = struct.unpack_from('<H', rt_d, 0)[0] if len(rt_d) >= 2 else 0
            if og_depth != rt_depth:
                diffs.append(f"  RO2 depth: OG={og_depth} RT={rt_depth}")
        elif og_t == 43:  # FrameLabel
            if og_d != rt_d:
                diffs.append(f"  Label differs")
    
    return diffs


def main():
    og_path = sys.argv[1]
    rt_path = sys.argv[2]
    
    og_tags = parse_swf_all(og_path)
    rt_tags = parse_swf_all(rt_path)
    
    # Collect all sprites
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
    
    print(f"OG sprites: {len(og_sprites)}, RT sprites: {len(rt_sprites)}")
    
    # Match by fingerprint
    og_by_fp = {}
    for cid, inner in og_sprites.items():
        fp = get_sprite_fingerprint(inner)
        if fp not in og_by_fp:
            og_by_fp[fp] = []
        og_by_fp[fp].append((cid, inner))
    
    rt_by_fp = {}
    for cid, inner in rt_sprites.items():
        fp = get_sprite_fingerprint(inner)
        if fp not in rt_by_fp:
            rt_by_fp[fp] = []
        rt_by_fp[fp].append((cid, inner))
    
    matched = 0
    unmatched_og = 0
    diff_count = 0
    total_frame_diffs = 0
    
    for fp, og_list in og_by_fp.items():
        rt_list = rt_by_fp.get(fp, [])
        if not rt_list:
            unmatched_og += len(og_list)
            for cid, _ in og_list:
                print(f"UNMATCHED OG sprite cid={cid} fp=({fp[0]} frames, {len(fp[1])} labels)")
            continue
        
        # Match by index (same order)
        for idx, (og_cid, og_inner) in enumerate(og_list):
            if idx >= len(rt_list):
                unmatched_og += 1
                continue
            rt_cid, rt_inner = rt_list[idx]
            matched += 1
            
            og_frames = analyze_frames(og_inner)
            rt_frames = analyze_frames(rt_inner)
            
            if len(og_frames) != len(rt_frames):
                print(f"FRAME COUNT MISMATCH: OG cid={og_cid}({len(og_frames)}f) vs RT cid={rt_cid}({len(rt_frames)}f)")
                diff_count += 1
                continue
            
            sprite_diffs = []
            for fi in range(len(og_frames)):
                frame_diffs = compare_frame_tags(og_frames[fi], rt_frames[fi], fi + 1)
                if frame_diffs:
                    sprite_diffs.append((fi + 1, frame_diffs))
            
            if sprite_diffs:
                diff_count += 1
                total_frame_diffs += len(sprite_diffs)
                labels = [l[1] for l in fp[1]]
                label_str = f" labels={labels}" if labels else ""
                print(f"\nSPRITE DIFF: OG={og_cid} RT={rt_cid} ({fp[0]} frames{label_str})")
                for fi, diffs in sprite_diffs[:10]:
                    print(f"  Frame {fi}:")
                    for d in diffs:
                        print(f"    {d}")
                if len(sprite_diffs) > 10:
                    print(f"  ...and {len(sprite_diffs)-10} more frame diffs")
    
    print(f"\n=== SUMMARY ===")
    print(f"Matched: {matched}, Unmatched OG: {unmatched_og}")
    print(f"Sprites with diffs: {diff_count}")
    print(f"Total frame diffs: {total_frame_diffs}")


if __name__ == '__main__':
    main()
