"""Detailed tag-level comparison of OG vs RT smashville.ssf"""
import struct, zlib, sys
sys.path.insert(0, '.')

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\stage\smashville.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\stage\smashville.ssf"

def read_swf(path):
    with open(path, 'rb') as f:
        data = f.read()
    sig = data[:3]
    if sig == b'CWS':
        header = data[:8]
        data = header[:3].replace(b'CWS', b'FWS') + header[3:8] + zlib.decompress(data[8:])
    return data

def parse_tags(data, offset=0, end=None):
    if end is None:
        end = len(data)
    tags = []
    while offset < end:
        if offset + 2 > end:
            break
        tag_code_and_length = struct.unpack_from('<H', data, offset)[0]
        tag_type = tag_code_and_length >> 6
        length = tag_code_and_length & 0x3F
        offset += 2
        if length == 0x3F:
            if offset + 4 > end:
                break
            length = struct.unpack_from('<I', data, offset)[0]
            offset += 4
        tag_data = data[offset:offset+length]
        tags.append((tag_type, tag_data))
        offset += length
        if tag_type == 0:  # End
            break
    return tags

def parse_rect(data, bit_offset=0):
    byte_idx = bit_offset // 8
    bit_idx = bit_offset % 8
    nbits = 0
    for i in range(5):
        b = (data[byte_idx + (bit_idx + i) // 8] >> (7 - (bit_idx + i) % 8)) & 1
        nbits = (nbits << 1) | b
    total_bits = 5 + nbits * 4
    total_bytes = (total_bits + 7) // 8
    return total_bytes

def skip_header(data):
    """Skip SWF header, return offset to first tag"""
    rect_size = parse_rect(data, 8*8)  # After 8-byte file header
    offset = 8 + rect_size + 2 + 2  # rect + frame_rate(UI16) + frame_count(UI16)
    return offset

TAG_NAMES = {
    0: 'End', 1: 'ShowFrame', 2: 'DefineShape', 4: 'PlaceObject',
    9: 'SetBackgroundColor', 10: 'DefineFont', 11: 'DefineText',
    13: 'DefineFontInfo', 20: 'DefineBitsLossless', 21: 'DefineBitsJPEG2',
    22: 'DefineShape2', 24: 'Protect', 26: 'PlaceObject2',
    28: 'RemoveObject2', 32: 'DefineShape3', 35: 'DefineBitsJPEG3',
    36: 'DefineBitsLossless2', 37: 'DefineEditText', 39: 'DefineSprite',
    43: 'FrameLabel', 46: 'DefineMorphShape', 48: 'DefineFont2',
    56: 'ExportAssets', 65: 'ScriptLimits', 69: 'FileAttributes',
    70: 'PlaceObject3', 73: 'DefineFontAlignZones', 74: 'CSMTextSettings',
    75: 'DefineFont3', 76: 'SymbolClass', 77: 'Metadata',
    78: 'DefineScalingGrid', 82: 'DoABC', 83: 'DefineFontName',
    84: 'DefineFont4', 86: 'DefineSceneAndFrameLabelData',
    87: 'DefineBinaryData', 88: 'DefineFontName2'
}

def tag_name(t):
    return TAG_NAMES.get(t, f'Tag{t}')

def get_char_id(tag_data):
    if len(tag_data) >= 2:
        return struct.unpack_from('<H', tag_data)[0]
    return None

def main():
    og_data = read_swf(OG)
    rt_data = read_swf(RT)
    
    print(f"OG: {len(og_data)} bytes")
    print(f"RT: {len(rt_data)} bytes")
    
    og_start = skip_header(og_data)
    rt_start = skip_header(rt_data)
    
    og_tags = parse_tags(og_data, og_start)
    rt_tags = parse_tags(rt_data, rt_start)
    
    print(f"\nOG root tags: {len(og_tags)}")
    print(f"RT root tags: {len(rt_tags)}")
    
    # Group tags by category
    print("\n=== ROOT TAG SEQUENCE (first 50) ===")
    print(f"{'#':>4} {'OG Tag':>30} {'OG size':>8}  {'RT Tag':>30} {'RT size':>8}  {'Match':>6}")
    for i in range(min(50, max(len(og_tags), len(rt_tags)))):
        og_t = og_tags[i] if i < len(og_tags) else (None, b'')
        rt_t = rt_tags[i] if i < len(rt_tags) else (None, b'')
        og_name = tag_name(og_t[0]) if og_t[0] is not None else '---'
        rt_name = tag_name(rt_t[0]) if rt_t[0] is not None else '---'
        match = '✓' if og_t[0] == rt_t[0] and len(og_t[1]) == len(rt_t[1]) else '✗'
        if og_t[0] == rt_t[0] and og_t[1] == rt_t[1]:
            match = '≡'
        print(f"{i:4d} {og_name:>30} {len(og_t[1]):8d}  {rt_name:>30} {len(rt_t[1]):8d}  {match:>6}")
    
    # Check if there are important order differences
    # Extract just tag types in sequence (exclude DefineShape, DefineSprite etc which have different counts)
    control_tags = {0, 1, 43, 69, 76, 77, 82, 86, 9}  # End, ShowFrame, FrameLabel, FileAttrs, SymbolClass, Metadata, DoABC, SceneFrameLabel, SetBGColor
    
    print("\n=== CONTROL TAG ORDER ===")
    og_control = [(i, t, len(d)) for i, (t, d) in enumerate(og_tags) if t in control_tags]
    rt_control = [(i, t, len(d)) for i, (t, d) in enumerate(rt_tags) if t in control_tags]
    
    print("OG control tags:")
    for idx, t, sz in og_control:
        print(f"  [{idx}] {tag_name(t)} ({sz} bytes)")
    print("RT control tags:")
    for idx, t, sz in rt_control:
        print(f"  [{idx}] {tag_name(t)} ({sz} bytes)")
    
    # SymbolClass comparison
    print("\n=== SYMBOLCLASS DETAILS ===")
    for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
        for t, d in tags:
            if t == 76:  # SymbolClass
                count = struct.unpack_from('<H', d)[0]
                off = 2
                entries = []
                for _ in range(count):
                    cid = struct.unpack_from('<H', d, off)[0]
                    off += 2
                    end = d.index(0, off)
                    name = d[off:end].decode('utf-8', errors='replace')
                    off = end + 1
                    entries.append((cid, name))
                print(f"{label}: {count} entries")
                # Find smashville_bg
                for cid, name in entries:
                    if 'smashville_bg' in name or 'stage_smashville' in name:
                        print(f"  {name} → cid={cid}")
    
    # Find and compare smashville_bg DefineSprite
    print("\n=== DEFINESPRITE COMPARISON: smashville_bg ===")
    
    # First find the char IDs for smashville_bg from SymbolClass
    og_smash_bg_cid = None
    rt_smash_bg_cid = None
    for label, tags, target in [("OG", og_tags, 'og'), ("RT", rt_tags, 'rt')]:
        for t, d in tags:
            if t == 76:
                count = struct.unpack_from('<H', d)[0]
                off = 2
                for _ in range(count):
                    cid = struct.unpack_from('<H', d, off)[0]
                    off += 2
                    end = d.index(0, off)
                    name = d[off:end].decode('utf-8', errors='replace')
                    off = end + 1
                    if name == 'smashville_bg':
                        if target == 'og':
                            og_smash_bg_cid = cid
                        else:
                            rt_smash_bg_cid = cid
    
    print(f"OG smashville_bg cid: {og_smash_bg_cid}")
    print(f"RT smashville_bg cid: {rt_smash_bg_cid}")
    
    # Find the DefineSprite tags
    for label, tags, target_cid in [("OG", og_tags, og_smash_bg_cid), ("RT", rt_tags, rt_smash_bg_cid)]:
        if target_cid is None:
            print(f"  {label}: not found!")
            continue
        for t, d in tags:
            if t == 39:  # DefineSprite
                cid = struct.unpack_from('<H', d)[0]
                if cid == target_cid:
                    frame_count = struct.unpack_from('<H', d, 2)[0]
                    sprite_tags = parse_tags(d, 4)
                    print(f"\n{label} smashville_bg (cid={cid}, frames={frame_count}, {len(sprite_tags)} tags, {len(d)} bytes):")
                    frame = 1
                    for st, sd in sprite_tags:
                        if st == 43:  # FrameLabel
                            lbl = sd[:sd.index(0)].decode() if 0 in sd else sd.decode()
                            print(f"  Frame {frame}: FrameLabel={lbl}")
                        elif st == 1:  # ShowFrame
                            frame += 1
                        elif st == 26 or st == 70:  # PlaceObject2/3
                            flags = sd[0] if st == 26 else None
                            depth_off = 1 if st == 26 else None
                            if st == 70:
                                flags2 = sd[0]
                                flags = sd[1]
                                depth_off = 2
                            depth = struct.unpack_from('<H', sd, depth_off)[0]
                            has_char = (flags >> 1) & 1
                            has_name = (flags >> 5) & 1
                            is_move = flags & 1
                            char_id = None
                            if has_char:
                                char_id = struct.unpack_from('<H', sd, depth_off + 2)[0]
                            print(f"  Frame {frame}: PO depth={depth} char={char_id} move={is_move} name={has_name} [{len(sd)}b]")
                        elif st == 28:  # RemoveObject2
                            depth = struct.unpack_from('<H', sd)[0]
                            print(f"  Frame {frame}: Remove depth={depth}")
                        elif st == 0:
                            pass
                        else:
                            print(f"  Frame {frame}: {tag_name(st)} [{len(sd)}b]")
    
    # Compare FileAttributes
    print("\n=== FILE ATTRIBUTES ===")
    for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
        for t, d in tags:
            if t == 69:
                flags = struct.unpack_from('<I', d)[0]
                print(f"{label}: 0x{flags:08X}")
                print(f"  UseDirectBlit: {bool(flags & 0x40)}")
                print(f"  UseGPU: {bool(flags & 0x20)}")
                print(f"  HasMetadata: {bool(flags & 0x10)}")
                print(f"  ActionScript3: {bool(flags & 0x08)}")
                print(f"  SuppressCrossDomainCaching: {bool(flags & 0x04) if len(d) >= 4 else 'N/A'}")
                print(f"  UseNetwork: {bool(flags & 0x01)}")
    
    # Compare root timeline PlaceObject tags for the main stage sprite
    print("\n=== ROOT TIMELINE PLACEOBJECT DETAILS ===")
    for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
        frame = 1
        print(f"\n{label} root timeline:")
        for t, d in tags:
            if t == 1:
                frame += 1
            elif t in (26, 70):
                if t == 26:
                    flags = d[0]
                    depth = struct.unpack_from('<H', d, 1)[0]
                    off = 3
                elif t == 70:
                    flags2 = d[0]
                    flags = d[1]
                    depth = struct.unpack_from('<H', d, 2)[0]
                    off = 4
                has_char = (flags >> 1) & 1
                has_matrix = (flags >> 2) & 1 
                has_ctrans = (flags >> 3) & 1
                has_ratio = (flags >> 4) & 1
                has_name = (flags >> 5) & 1
                has_clip = (flags >> 6) & 1
                is_move = flags & 1
                char_id = None
                if has_char:
                    char_id = struct.unpack_from('<H', d, off)[0]
                    off += 2
                info = f"depth={depth} char={char_id} move={is_move}"
                if has_matrix:
                    info += " +matrix"
                if has_ctrans:
                    info += " +ctrans"
                if has_ratio:
                    info += " +ratio"
                if has_name:
                    # Parse name
                    name_end = d.index(0, off) if 0 in d[off:] else len(d)
                    name = d[off:name_end].decode('utf-8', errors='replace')
                    info += f" name='{name}'"
                if has_clip:
                    info += " +clipDepth"
                print(f"  Frame {frame}: {tag_name(t)} {info} [{len(d)}b]")
            elif t == 28:
                depth = struct.unpack_from('<H', d)[0]
                print(f"  Frame {frame}: Remove depth={depth}")
    
    # Count shapes by type
    print("\n=== SHAPE TAG TYPES ===")
    for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
        shapes = {}
        for t, d in tags:
            if t in (2, 22, 32, 83):  # DefineShape, DefineShape2, DefineShape3, DefineShape4
                shapes[t] = shapes.get(t, 0) + 1
        print(f"{label}:")
        for t in sorted(shapes):
            print(f"  {tag_name(t)} (tag {t}): {shapes[t]}")
    
    # Count text tags
    print("\n=== TEXT TAG TYPES ===")
    for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
        texts = {}
        for t, d in tags:
            if t in (11, 33, 37):  # DefineText, DefineText2, DefineEditText
                texts[t] = texts.get(t, 0) + 1
            if t in (10, 48, 75, 73, 74, 83, 88):  # Font-related
                texts[t] = texts.get(t, 0) + 1
        print(f"{label}:")
        for t in sorted(texts):
            print(f"  {tag_name(t)} (tag {t}): {texts[t]}")

    # Check SetBackgroundColor
    print("\n=== SET BACKGROUND COLOR ===")
    for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
        for t, d in tags:
            if t == 9:
                if len(d) >= 3:
                    r, g, b = d[0], d[1], d[2]
                    print(f"{label}: RGB({r},{g},{b})")
                    
    # Compare ScriptLimits
    print("\n=== SCRIPT LIMITS ===")
    for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
        for t, d in tags:
            if t == 65:
                max_rec = struct.unpack_from('<H', d, 0)[0]
                timeout = struct.unpack_from('<H', d, 2)[0]
                print(f"{label}: maxRecursion={max_rec}, timeout={timeout}")

    # Compare Metadata
    print("\n=== METADATA ===")
    for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
        for t, d in tags:
            if t == 77:
                meta = d.decode('utf-8', errors='replace').rstrip('\x00')
                print(f"{label}: {meta[:200]}...")

if __name__ == '__main__':
    main()
