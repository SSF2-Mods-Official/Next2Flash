"""Deep comparison of bitmap dimensions and companion shapes between OG and RT blackmage."""
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

def parse_lossless2(d):
    """Parse DefineBitsLossless2: cid, format, width, height"""
    cid = struct.unpack_from('<H', d, 0)[0]
    fmt = d[2]
    w = struct.unpack_from('<H', d, 3)[0]
    h = struct.unpack_from('<H', d, 5)[0]
    return cid, fmt, w, h

def parse_jpeg3(d):
    """Parse DefineBitsJPEG3: cid, and try to get dimensions from JPEG header"""
    cid = struct.unpack_from('<H', d, 0)[0]
    alpha_off = struct.unpack_from('<I', d, 2)[0]
    jpeg_data = d[6:6+alpha_off]
    # Try to find JPEG SOF marker for dimensions
    w, h = 0, 0
    i = 0
    while i < len(jpeg_data) - 9:
        if jpeg_data[i] == 0xFF:
            marker = jpeg_data[i+1]
            if marker in (0xC0, 0xC1, 0xC2):  # SOF0, SOF1, SOF2
                h = struct.unpack_from('>H', jpeg_data, i+5)[0]
                w = struct.unpack_from('>H', jpeg_data, i+7)[0]
                break
            elif marker == 0xD8 or marker == 0xD9 or marker == 0x00:
                i += 2
            else:
                if i + 3 < len(jpeg_data):
                    seg_len = struct.unpack_from('>H', jpeg_data, i+2)[0]
                    i += 2 + seg_len
                else:
                    i += 2
        else:
            i += 1
    return cid, w, h

def parse_shape_bitmap_fills(d, tag_type):
    """Parse a DefineShape tag and return list of bitmap character IDs used in fills."""
    bitmap_cids = []
    cid = struct.unpack_from('<H', d, 0)[0]
    
    # Skip CID (2 bytes) + RECT (bounds)
    off_bits = 16  # start after CID in bits
    # Parse RECT
    byte_i = 2
    nbits_byte = d[byte_i]
    nbits = nbits_byte >> 3  # top 5 bits
    rect_bits = 5 + nbits * 4
    off_bits = 16 + rect_bits
    byte_off = (off_bits + 7) // 8 + 2  # back to byte offset from start of d
    
    if byte_off >= len(d):
        return cid, bitmap_cids
    
    # For DefineShape4 (tag 83), there's an extra EdgeBounds RECT + flags
    if tag_type == 83:
        # Skip EdgeBounds RECT
        nbits2 = d[byte_off] >> 3
        rect2_bytes = (5 + nbits2 * 4 + 7) // 8
        byte_off += rect2_bytes
        byte_off += 1  # Skip flags byte
    
    # Now at fill styles
    if byte_off >= len(d):
        return cid, bitmap_cids
    
    fill_count = d[byte_off]; byte_off += 1
    if fill_count == 0xFF:
        fill_count = struct.unpack_from('<H', d, byte_off)[0]; byte_off += 2
    
    for _ in range(fill_count):
        if byte_off >= len(d):
            break
        fill_type = d[byte_off]; byte_off += 1
        
        if fill_type == 0x00:
            # Solid fill
            if tag_type in (32, 83):  # Shape3/Shape4 have RGBA
                byte_off += 4
            else:
                byte_off += 3  # RGB
        elif fill_type in (0x10, 0x12, 0x13):
            # Gradient fill
            byte_off += 6*4  # MATRIX (approximate max)
            # This is wrong but we just need a rough parse for bitmap fills
            # Skip for now
            break
        elif fill_type in (0x40, 0x41, 0x42, 0x43):
            # Bitmap fill
            if byte_off + 1 < len(d):
                bitmap_cid = struct.unpack_from('<H', d, byte_off)[0]
                bitmap_cids.append(bitmap_cid)
            byte_off += 2  # bitmap character ID
            byte_off += 6*4  # MATRIX (approximate)
            break  # rough parse, stop here
        else:
            break  # Unknown fill type
    
    return cid, bitmap_cids

def main():
    og_data = read_swf(OG)
    rt_data = read_swf(RT)
    
    og_tags = parse_tags(og_data, skip_header(og_data))
    rt_tags = parse_tags(rt_data, skip_header(rt_data))
    
    # Parse ALL bitmap dimensions
    print("=== OG BITMAP DIMENSIONS ===")
    og_bitmaps = {}
    for t, d in og_tags:
        if t == 36:  # DefineBitsLossless2
            cid, fmt, w, h = parse_lossless2(d)
            og_bitmaps[cid] = (w, h, fmt, 'lossless2')
        elif t == 35:  # DefineBitsJPEG3
            cid, w, h = parse_jpeg3(d)
            og_bitmaps[cid] = (w, h, 0, 'jpeg3')
        elif t == 20:  # DefineBitsLossless
            cid, fmt, w, h = parse_lossless2(d)
            og_bitmaps[cid] = (w, h, fmt, 'lossless')
    
    rt_bitmaps = {}
    for t, d in rt_tags:
        if t == 36:
            cid, fmt, w, h = parse_lossless2(d)
            rt_bitmaps[cid] = (w, h, fmt, 'lossless2')
        elif t == 35:
            cid, w, h = parse_jpeg3(d)
            rt_bitmaps[cid] = (w, h, 0, 'jpeg3')
        elif t == 20:
            cid, fmt, w, h = parse_lossless2(d)
            rt_bitmaps[cid] = (w, h, fmt, 'lossless')
    
    # Show dimension statistics
    og_dims = [(w, h) for w, h, f, t in og_bitmaps.values()]
    rt_dims = [(w, h) for w, h, f, t in rt_bitmaps.values()]
    
    print(f"OG: {len(og_bitmaps)} bitmaps")
    print(f"  Min dims: {min(w for w,h in og_dims)}x{min(h for w,h in og_dims)}")
    print(f"  Max dims: {max(w for w,h in og_dims)}x{max(h for w,h in og_dims)}")
    
    # Check for 0x0 bitmaps
    og_zero = [(cid, w, h) for cid, (w, h, f, t) in og_bitmaps.items() if w == 0 or h == 0]
    if og_zero:
        print(f"  ⚠ 0-dimension bitmaps: {og_zero[:10]}")
    
    print(f"\nRT: {len(rt_bitmaps)} bitmaps")
    print(f"  Min dims: {min(w for w,h in rt_dims)}x{min(h for w,h in rt_dims)}")
    print(f"  Max dims: {max(w for w,h in rt_dims)}x{max(h for w,h in rt_dims)}")

    rt_zero = [(cid, w, h) for cid, (w, h, f, t) in rt_bitmaps.items() if w == 0 or h == 0]
    if rt_zero:
        print(f"  ⚠ 0-dimension bitmaps: {rt_zero[:10]}")
    
    # Check for very large bitmaps (> 8191 or pixel count > 16M)
    og_large = [(cid, w, h) for cid, (w, h, f, t) in og_bitmaps.items() if w > 8191 or h > 8191 or w*h > 16777215]
    rt_large = [(cid, w, h) for cid, (w, h, f, t) in rt_bitmaps.items() if w > 8191 or h > 8191 or w*h > 16777215]
    if og_large:
        print(f"\nOG oversized bitmaps: {og_large[:10]}")
    if rt_large:
        print(f"\nRT oversized bitmaps: {rt_large[:10]}")
    
    # Compare dimensions for bitmaps that exist in both
    # Since CIDs are different, let's compare by ordered index
    og_bitmap_order = sorted(og_bitmaps.items())
    rt_bitmap_order = sorted(rt_bitmaps.items())
    
    print(f"\n=== BITMAP FORMAT BREAKDOWN ===")
    for label, bitmaps in [("OG", og_bitmaps), ("RT", rt_bitmaps)]:
        fmt_counts = {}
        for cid, (w, h, f, t) in bitmaps.items():
            fmt_counts[t] = fmt_counts.get(t, 0) + 1
        print(f"{label}: {fmt_counts}")
    
    # Check for dimension mismatches by sorted order
    print(f"\n=== DIMENSION COMPARISON (by sorted order) ===")
    mismatches = 0
    if len(og_bitmap_order) == len(rt_bitmap_order):
        for i, ((og_cid, (og_w, og_h, og_f, og_t)), (rt_cid, (rt_w, rt_h, rt_f, rt_t))) in enumerate(zip(og_bitmap_order, rt_bitmap_order)):
            if og_w != rt_w or og_h != rt_h:
                if mismatches < 20:
                    print(f"  #{i}: OG cid={og_cid} {og_w}x{og_h} ({og_t}) vs RT cid={rt_cid} {rt_w}x{rt_h} ({rt_t})")
                mismatches += 1
        print(f"Total dimension mismatches: {mismatches} / {len(og_bitmap_order)}")
    else:
        print(f"  Different bitmap counts, can't compare by order: OG={len(og_bitmap_order)} RT={len(rt_bitmap_order)}")
    
    # Check which shapes reference bitmaps
    print(f"\n=== SHAPES REFERENCING BITMAPS ===")
    for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
        shape_to_bitmap = {}
        for t, d in tags:
            if t in (2, 22, 32, 83):
                cid, bitmap_cids = parse_shape_bitmap_fills(d, t)
                if bitmap_cids:
                    shape_to_bitmap[cid] = bitmap_cids
        print(f"{label}: {len(shape_to_bitmap)} shapes reference bitmaps")
        # Show first 10
        items = sorted(shape_to_bitmap.items())
        for shape_cid, bmp_cids in items[:10]:
            print(f"  Shape cid={shape_cid} → Bitmap cids={bmp_cids}")
        if len(items) > 10:
            print(f"  ... {len(items) - 10} more")

    # Check PlaceObject2/3 tags inside DefineSprite to see what's placed
    # Focus on bitmap placements
    print(f"\n=== PLACEMENT ANALYSIS IN SPRITES ===")
    for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
        # Collect all bitmap CIDs and all shape CIDs that wrap bitmaps
        bitmap_cids = set()
        for t, d in tags:
            if t in (20, 35, 36):
                cid = struct.unpack_from('<H', d, 0)[0]
                bitmap_cids.add(cid)
        
        # Collect shape → bitmap mapping
        shape_to_bitmap = {}
        for t, d in tags:
            if t in (2, 22, 32, 83):
                cid, bmp_cids = parse_shape_bitmap_fills(d, t)
                if bmp_cids:
                    shape_to_bitmap[cid] = bmp_cids
        
        bitmap_shape_cids = set(shape_to_bitmap.keys())
        
        # Check inside sprites
        sprites_placing_bitmap_shapes = 0
        sprites_total = 0
        for t, d in tags:
            if t != 39: continue
            sprites_total += 1
            if len(d) < 4: continue
            sprite_cid = struct.unpack_from('<H', d, 0)[0]
            inner_tags = parse_tags(d, 4)
            for it, id_ in inner_tags:
                if it in (26, 70):  # PlaceObject2/3
                    # Try to read character ID
                    if it == 26:
                        flags = id_[0] if id_ else 0
                        has_char = flags & 0x02
                        off = 3 if has_char else 0
                        if has_char and len(id_) >= 5:
                            placed_cid = struct.unpack_from('<H', id_, 3)[0]
                            if placed_cid in bitmap_shape_cids:
                                sprites_placing_bitmap_shapes += 1
                                break
                    elif it == 70:
                        flags = id_[0] if id_ else 0
                        flags2 = id_[1] if len(id_) > 1 else 0
                        has_char = flags & 0x02
                        has_image = flags2 & 0x10
                        if has_char and len(id_) >= 6:
                            placed_cid = struct.unpack_from('<H', id_, 4)[0]
                            if placed_cid in bitmap_shape_cids or placed_cid in bitmap_cids:
                                sprites_placing_bitmap_shapes += 1
                                break
        
        print(f"{label}: {sprites_placing_bitmap_shapes} sprites place bitmap shapes out of {sprites_total}")

if __name__ == '__main__':
    main()
