"""Compare OG vs RT blackmage.ssf — focus on bitmap handling and shapes with bitmap fills."""
import struct, zlib, sys, os
sys.path.insert(0, '.')

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"

def read_swf(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:3] == b'CWS':
        data = b'FWS' + data[3:8] + zlib.decompress(data[8:])
    return data

def parse_tags(data, offset, end=None):
    if end is None: end = len(data)
    tags = []
    while offset < end:
        if offset + 2 > end: break
        hdr = struct.unpack_from('<H', data, offset)[0]
        tt = hdr >> 6; length = hdr & 0x3F; offset += 2
        if length == 0x3F:
            length = struct.unpack_from('<I', data, offset)[0]; offset += 4
        td = data[offset:offset+length]; tags.append((tt, td)); offset += length
        if tt == 0: break
    return tags

def parse_rect(data, bit_off=0):
    byte_i = bit_off // 8; bit_i = bit_off % 8
    nbits = 0
    for i in range(5):
        nbits = (nbits << 1) | ((data[byte_i + (bit_i+i)//8] >> (7-(bit_i+i)%8)) & 1)
    return (5 + nbits * 4 + 7) // 8

def skip_header(data):
    return 8 + parse_rect(data, 64) + 4

TAG_NAMES = {
    0: 'End', 1: 'ShowFrame', 2: 'DefineShape', 4: 'PlaceObject',
    9: 'SetBGColor', 11: 'DefineText', 20: 'DefineBitsLossless',
    22: 'DefineShape2', 26: 'PlaceObject2', 28: 'RemoveObject2',
    32: 'DefineShape3', 35: 'DefineBitsJPEG3', 36: 'DefineBitsLossless2',
    37: 'DefineEditText', 39: 'DefineSprite', 43: 'FrameLabel',
    46: 'DefineMorphShape', 69: 'FileAttributes', 70: 'PlaceObject3',
    75: 'DefineFont3', 76: 'SymbolClass', 82: 'DoABC',
    86: 'DefineSceneAndFrameLabel', 87: 'DefineBinaryData',
}

def tag_name(t):
    return TAG_NAMES.get(t, f'Tag{t}')

def main():
    og_data = read_swf(OG)
    rt_data = read_swf(RT)
    
    og_tags = parse_tags(og_data, skip_header(og_data))
    rt_tags = parse_tags(rt_data, skip_header(rt_data))
    
    print(f"OG: {os.path.getsize(OG):,} bytes on disk, {len(og_data):,} uncompressed, {len(og_tags)} tags")
    print(f"RT: {os.path.getsize(RT):,} bytes on disk, {len(rt_data):,} uncompressed, {len(rt_tags)} tags")
    
    # Count tag types
    print("\n=== TAG TYPE COUNTS ===")
    og_counts = {}
    rt_counts = {}
    for t, d in og_tags:
        og_counts[t] = og_counts.get(t, 0) + 1
    for t, d in rt_tags:
        rt_counts[t] = rt_counts.get(t, 0) + 1
    
    all_types = sorted(set(list(og_counts.keys()) + list(rt_counts.keys())))
    for t in all_types:
        og_c = og_counts.get(t, 0)
        rt_c = rt_counts.get(t, 0)
        match = '✓' if og_c == rt_c else '✗'
        print(f"  {tag_name(t):>30} (tag {t:3d}): OG={og_c:5d}  RT={rt_c:5d}  {match}")
    
    # Compare bitmap counts and sizes
    print("\n=== BITMAP TAGS ===")
    og_bitmaps = {}
    rt_bitmaps = {}
    for t, d in og_tags:
        if t in (20, 36, 35):  # DefineBitsLossless, DefineBitsLossless2, DefineBitsJPEG3
            cid = struct.unpack_from('<H', d)[0]
            og_bitmaps[cid] = (t, len(d))
    for t, d in rt_tags:
        if t in (20, 36, 35):
            cid = struct.unpack_from('<H', d)[0]
            rt_bitmaps[cid] = (t, len(d))
    
    print(f"OG bitmap count: {len(og_bitmaps)}")
    print(f"RT bitmap count: {len(rt_bitmaps)}")
    
    # Check for bitmap shapes (DefineShape with bitmap fill)
    # In OG, each bitmap typically has a companion DefineShape that wraps it
    # The pattern is: DefineBitsLossless2(cid=X) + DefineShape(cid=X+1, bitmap fill referencing X)
    
    # Count shapes that reference bitmaps in their fill styles
    print("\n=== SHAPE-BITMAP RELATIONSHIP ===")
    
    def count_bitmap_fill_shapes(tags):
        """Count shapes that have bitmap fills (fill type 0x40-0x43)."""
        bitmap_shapes = 0
        non_bitmap_shapes = 0
        for t, d in tags:
            if t not in (2, 22, 32, 83):  # DefineShape variants
                continue
            # Quick scan for bitmap fill type bytes
            has_bitmap = False
            # This is a rough heuristic - look for fill type 0x40-0x43
            for i in range(4, min(len(d), 200)):
                if d[i] in (0x40, 0x41, 0x42, 0x43):
                    has_bitmap = True
                    break
            if has_bitmap:
                bitmap_shapes += 1
            else:
                non_bitmap_shapes += 1
        return bitmap_shapes, non_bitmap_shapes
    
    og_bmp_shapes, og_other_shapes = count_bitmap_fill_shapes(og_tags)
    rt_bmp_shapes, rt_other_shapes = count_bitmap_fill_shapes(rt_tags)
    print(f"OG: {og_bmp_shapes} bitmap-fill shapes, {og_other_shapes} other shapes")
    print(f"RT: {rt_bmp_shapes} bitmap-fill shapes, {rt_other_shapes} other shapes")
    
    # Check SymbolClass entries 
    print("\n=== SYMBOLCLASS ===")
    for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
        for t, d in tags:
            if t == 76:
                count = struct.unpack_from('<H', d)[0]
                off = 2
                entries = []
                for _ in range(count):
                    cid = struct.unpack_from('<H', d, off)[0]; off += 2
                    end = d.index(0, off)
                    name = d[off:end].decode('utf-8', errors='replace')
                    off = end + 1
                    entries.append((cid, name))
                print(f"{label}: {count} entries")
                # Show first 20
                for cid, name in entries[:20]:
                    print(f"  cid={cid:5d}: {name}")
                if len(entries) > 20:
                    print(f"  ... {len(entries) - 20} more")

    # Check if OG has a pattern of DefineBitsLossless2 followed by DefineShape
    print("\n=== OG BITMAP+SHAPE PAIRS (first 20) ===")
    prev_bitmap_cid = None
    pair_count = 0
    for t, d in og_tags:
        if t in (20, 36):  # DefineBitsLossless/2
            prev_bitmap_cid = struct.unpack_from('<H', d)[0]
        elif t in (2, 22, 32) and prev_bitmap_cid is not None:
            shape_cid = struct.unpack_from('<H', d)[0]
            if pair_count < 20:
                print(f"  Bitmap cid={prev_bitmap_cid} → Shape cid={shape_cid} (tag {t}, {len(d)}b)")
            pair_count += 1
            prev_bitmap_cid = None
        else:
            prev_bitmap_cid = None
    print(f"Total bitmap+shape pairs: {pair_count}")
    
    print("\n=== RT BITMAP+SHAPE PAIRS (first 20) ===")
    prev_bitmap_cid = None
    pair_count = 0
    for t, d in rt_tags:
        if t in (20, 36):
            prev_bitmap_cid = struct.unpack_from('<H', d)[0]
        elif t in (2, 22, 32) and prev_bitmap_cid is not None:
            shape_cid = struct.unpack_from('<H', d)[0]
            if pair_count < 20:
                print(f"  Bitmap cid={prev_bitmap_cid} → Shape cid={shape_cid} (tag {t}, {len(d)}b)")
            pair_count += 1
            prev_bitmap_cid = None
        else:
            prev_bitmap_cid = None
    print(f"Total bitmap+shape pairs: {pair_count}")

    # Check how bitmaps are placed inside sprites
    # The palette swap code looks for Bitmap children inside MovieClips
    # In SWF, a Bitmap display object comes from placing a DefineShape with bitmap fill
    # that has the special "HasImage" flag in PlaceObject3
    
    # Count PlaceObject3 with HasImage flag
    print("\n=== PLACEOBJECT3 WITH HasImage FLAG ===")
    for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
        has_image_count = 0
        po3_count = 0
        # Check in all sprites too
        for t, d in tags:
            if t == 70:  # PlaceObject3
                po3_count += 1
                if len(d) >= 2:
                    flags2 = d[0]
                    if flags2 & 0x10:  # HasImage bit
                        has_image_count += 1
            elif t == 39:  # DefineSprite - check nested tags
                if len(d) >= 4:
                    inner_tags = parse_tags(d, 4)
                    for it, id_ in inner_tags:
                        if it == 70:
                            po3_count += 1
                            if len(id_) >= 2:
                                flags2 = id_[0]
                                if flags2 & 0x10:
                                    has_image_count += 1
        print(f"{label}: {has_image_count} PlaceObject3 with HasImage, {po3_count} total PO3")

    # Find the stance sprite and check what's inside
    # Character sprites typically have nested structure with bitmap children
    # Let's find the main character sprite's SymbolClass name
    print("\n=== LOOKING FOR CHARACTER STANCE SPRITES ===")
    for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
        sym_by_cid = {}
        for t, d in tags:
            if t == 76:
                count = struct.unpack_from('<H', d)[0]; off = 2
                for _ in range(count):
                    cid = struct.unpack_from('<H', d, off)[0]; off += 2
                    end = d.index(0, off)
                    name = d[off:end].decode('utf-8', errors='replace')
                    off = end + 1
                    sym_by_cid[cid] = name
        
        # Find sprites that contain bitmaps (PlaceObject referencing bitmap shapes)
        # Check a few sprites for their children
        stance_sprites = []
        for cid, name in sym_by_cid.items():
            if 'stance' in name.lower() or 'blackmage' == name.lower() or name == 'blackmage':
                stance_sprites.append((cid, name))
        
        if stance_sprites:
            print(f"\n{label} stance-related sprites:")
            for cid, name in stance_sprites:
                print(f"  cid={cid}: {name}")
        
        # Find the root symbol (cid=0 class association)
        root_class = sym_by_cid.get(0, '(none)')
        print(f"{label} root class: {root_class}")

if __name__ == '__main__':
    main()
