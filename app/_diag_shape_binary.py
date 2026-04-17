#!/usr/bin/env python3
"""
Binary-level shape tag comparison: OG SWF vs roundtrip SWF.
Compares DefineShape, fill styles, line styles, edge data, and bitmap fill matrices.
Also compares all-frame display lists (not just frame 1).
"""
import sys, os, struct, io, tempfile, zlib
sys.path.insert(0, os.path.dirname(__file__))

from swf_to_n2d import N2DBuilder, parse_swf, save_n2d, decompile_all_scripts
from compile_n2d import N2DCompiler
from swf_binary_io import BitReader

SSF_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\fox.ssf"

def read_swf_bytes(path):
    with open(path, 'rb') as f:
        return f.read()

def parse_tags_raw(swf_data):
    """Parse raw SWF and return list of (tag_type, tag_body_bytes)."""
    # Decompress SWF
    sig = swf_data[0:3]
    if sig == b'CWS':
        body = zlib.decompress(swf_data[8:])
        data = swf_data[:8] + body
    elif sig == b'ZWS':
        import lzma
        body = lzma.decompress(swf_data[12:])
        data = swf_data[:8] + body
    else:
        data = swf_data
    
    # Skip SWF header: signature(3) + version(1) + fileLength(4)
    # Then RECT + frameRate(2) + frameCount(2)
    br = BitReader(data, 8)
    nbits = br.read_ub(5)
    for _ in range(4):
        br.read_sb(nbits)
    br.align()
    pos = br.byte_pos + 4  # skip frameRate + frameCount

    tags = []
    while pos < len(data):
        if pos + 2 > len(data):
            break
        tag_code_and_length = struct.unpack_from('<H', data, pos)[0]
        tag_type = tag_code_and_length >> 6
        length = tag_code_and_length & 0x3F
        pos += 2
        if length == 0x3F:
            if pos + 4 > len(data):
                break
            length = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        body = data[pos:pos+length]
        tags.append((tag_type, body))
        pos += length
        if tag_type == 0:
            break
    return tags

def extract_define_shapes(tags):
    """Extract DefineShape tags: {charId: (tag_type, body)}"""
    shapes = {}
    for tt, body in tags:
        if tt in (2, 22, 32, 83):  # DefineShape, DefineShape2, DefineShape3, DefineShape4
            if len(body) >= 2:
                cid = struct.unpack_from('<H', body, 0)[0]
                shapes[cid] = (tt, body)
    return shapes

def extract_define_sprites(tags):
    """Extract DefineSprite → {charId: (frameCount, nested_tags)}"""
    sprites = {}
    for tt, body in tags:
        if tt == 39 and len(body) >= 4:
            cid, fc = struct.unpack_from('<HH', body, 0)
            # Parse nested tags
            pos = 4
            nested = []
            while pos < len(body):
                if pos + 2 > len(body):
                    break
                tcl = struct.unpack_from('<H', body, pos)[0]
                nttype = tcl >> 6
                nlength = tcl & 0x3F
                pos += 2
                if nlength == 0x3F:
                    if pos + 4 > len(body):
                        break
                    nlength = struct.unpack_from('<I', body, pos)[0]
                    pos += 4
                nbody = body[pos:pos+nlength]
                nested.append((nttype, nbody))
                pos += nlength
                if nttype == 0:
                    break
            sprites[cid] = (fc, nested)
    return sprites

def parse_place_object2(body):
    """Parse PlaceObject2 tag body → dict with depth, charId, matrix, etc."""
    if len(body) < 3:
        return {}
    flags = body[0]
    depth = struct.unpack_from('<H', body, 1)[0]
    pos = 3
    result = {'depth': depth, 'flags': flags}

    if flags & 0x02:  # HasCharacter
        if pos + 2 <= len(body):
            result['charId'] = struct.unpack_from('<H', body, pos)[0]
            pos += 2

    if flags & 0x04:  # HasMatrix
        br = BitReader(body, pos)
        br.align()
        mat = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        if br.read_ub(1):  # HasScale
            n = br.read_ub(5)
            mat[0] = br.read_sb(n) / 65536.0
            mat[3] = br.read_sb(n) / 65536.0
        if br.read_ub(1):  # HasRotate
            n = br.read_ub(5)
            mat[1] = br.read_sb(n) / 65536.0
            mat[2] = br.read_sb(n) / 65536.0
        n = br.read_ub(5)
        mat[4] = br.read_sb(n) / 20.0
        mat[5] = br.read_sb(n) / 20.0
        result['matrix'] = mat

    return result

def parse_fill_styles_from_shape(body, tag_type):
    """Parse fill style array from a DefineShape body. Returns list of (fill_type, details)."""
    if len(body) < 4:
        return []
    # Skip shapeId(2) + RECT
    br = BitReader(body, 2)
    nbits = br.read_ub(5)
    for _ in range(4):
        br.read_sb(nbits)
    br.align()
    
    # DefineShape4 has extra EdgeBounds RECT + flags byte
    if tag_type == 83:
        nbits2 = br.read_ub(5)
        for _ in range(4):
            br.read_sb(nbits2)
        br.align()
        _ = br.read_ui8()  # flags byte
    
    # Fill style array
    count = br.read_ui8()
    if count == 0xFF:
        count = br.read_ui8() | (br.read_ui8() << 8)
    
    fills = []
    for _ in range(count):
        ftype = br.read_ui8()
        if ftype == 0x00:  # Solid
            if tag_type in (32, 83):
                r, g, b, a = br.read_ui8(), br.read_ui8(), br.read_ui8(), br.read_ui8()
                fills.append(('solid', (r, g, b, a)))
            else:
                r, g, b = br.read_ui8(), br.read_ui8(), br.read_ui8()
                fills.append(('solid', (r, g, b, 255)))
        elif ftype in (0x10, 0x12, 0x13):  # Gradient
            # Read matrix
            br.align()
            mat = _read_matrix_from_br(br)
            # Read gradient records
            spread_interp_count = br.read_ui8()
            num_grad = spread_interp_count & 0x0F
            for _ in range(num_grad):
                br.read_ui8()  # ratio
                if tag_type in (32, 83):
                    br.read_ui8(); br.read_ui8(); br.read_ui8(); br.read_ui8()
                else:
                    br.read_ui8(); br.read_ui8(); br.read_ui8()
            if ftype == 0x13:  # focal
                br.read_ui8(); br.read_ui8()  # fixed8
            fills.append(('gradient', {'type': ftype, 'matrix': mat, 'stops': num_grad}))
        elif ftype in (0x40, 0x41, 0x42, 0x43):  # Bitmap fill
            bmp_id = br.read_ui8() | (br.read_ui8() << 8)
            br.align()
            mat = _read_matrix_from_br(br)
            fills.append(('bitmap', {
                'fillType': ftype,
                'bitmapId': bmp_id,
                'matrix': mat,
                'repeat': ftype in (0x40, 0x42),
                'smooth': ftype in (0x40, 0x41),
            }))
        else:
            fills.append(('unknown', ftype))
            break  # Can't parse further
    
    return fills

def _read_matrix_from_br(br):
    br.align()
    mat = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
    if br.read_ub(1):  # HasScale
        n = br.read_ub(5)
        mat[0] = br.read_sb(n) / 65536.0
        mat[3] = br.read_sb(n) / 65536.0
    if br.read_ub(1):  # HasRotate
        n = br.read_ub(5)
        mat[1] = br.read_sb(n) / 65536.0
        mat[2] = br.read_sb(n) / 65536.0
    n = br.read_ub(5)
    mat[4] = br.read_sb(n) / 20.0
    mat[5] = br.read_sb(n) / 20.0
    return mat

def compare_shape_tags(og_shapes, rt_shapes, max_compare=50):
    """Compare shape tags between original and roundtrip."""
    print(f"\n  OG shapes: {len(og_shapes)}, RT shapes: {len(rt_shapes)}")
    
    # Find matching char IDs
    common = set(og_shapes.keys()) & set(rt_shapes.keys())
    og_only = set(og_shapes.keys()) - set(rt_shapes.keys())
    rt_only = set(rt_shapes.keys()) - set(og_shapes.keys())
    
    if og_only:
        print(f"  Shapes only in OG ({len(og_only)}): {sorted(og_only)[:20]}...")
    if rt_only:
        print(f"  Shapes only in RT ({len(rt_only)}): {sorted(rt_only)[:20]}...")
    
    # Compare tag types
    type_changes = 0
    size_diffs = []
    bitmap_fill_diffs = []
    fill_count_diffs = []
    
    for cid in sorted(common)[:max_compare]:
        og_type, og_body = og_shapes[cid]
        rt_type, rt_body = rt_shapes[cid]
        
        if og_type != rt_type:
            type_changes += 1
            if type_changes <= 10:
                print(f"  charId={cid}: tag type changed {og_type} → {rt_type}")
        
        size_diff = len(rt_body) - len(og_body)
        if abs(size_diff) > 0:
            size_diffs.append((cid, len(og_body), len(rt_body), size_diff))
        
        # Compare fill styles
        try:
            og_fills = parse_fill_styles_from_shape(og_body, og_type)
            rt_fills = parse_fill_styles_from_shape(rt_body, rt_type)
            
            if len(og_fills) != len(rt_fills):
                fill_count_diffs.append((cid, len(og_fills), len(rt_fills)))
            else:
                # Compare bitmap fills specifically
                for fi, (of, rf) in enumerate(zip(og_fills, rt_fills)):
                    if of[0] == 'bitmap' and rf[0] == 'bitmap':
                        og_mat = of[1]['matrix']
                        rt_mat = rf[1]['matrix']
                        max_diff = max(abs(og_mat[j] - rt_mat[j]) for j in range(6))
                        if max_diff > 0.01:
                            bitmap_fill_diffs.append((cid, fi, og_mat, rt_mat, max_diff))
                    elif of[0] != rf[0]:
                        fill_count_diffs.append((cid, f"type mismatch: {of[0]} vs {rf[0]}", ""))
        except Exception as e:
            pass  # Skip shapes we can't parse
    
    print(f"\n  Tag type changes: {type_changes}")
    
    if size_diffs:
        total_bigger = sum(1 for _, _, _, d in size_diffs if d > 0)
        total_smaller = sum(1 for _, _, _, d in size_diffs if d < 0)
        avg_diff = sum(abs(d) for _, _, _, d in size_diffs) / len(size_diffs)
        print(f"  Size differences: {len(size_diffs)} shapes differ (avg |diff|={avg_diff:.1f}B, {total_bigger} bigger, {total_smaller} smaller)")
        # Show a few examples
        for cid, og_sz, rt_sz, diff in sorted(size_diffs, key=lambda x: -abs(x[3]))[:5]:
            print(f"    charId={cid}: OG={og_sz}B → RT={rt_sz}B ({'+' if diff>0 else ''}{diff}B)")
    else:
        print(f"  All shape sizes identical!")
    
    if fill_count_diffs:
        print(f"\n  Fill count mismatches: {len(fill_count_diffs)}")
        for cid, oc, rc in fill_count_diffs[:10]:
            print(f"    charId={cid}: OG={oc} fills → RT={rc} fills")
    else:
        print(f"  All fill counts match!")
    
    if bitmap_fill_diffs:
        print(f"\n  Bitmap fill matrix differences: {len(bitmap_fill_diffs)}")
        for cid, fi, og_mat, rt_mat, max_diff in bitmap_fill_diffs[:10]:
            print(f"    charId={cid} fill#{fi}: max_diff={max_diff:.6f}")
            print(f"      OG: [{', '.join(f'{v:.4f}' for v in og_mat)}]")
            print(f"      RT: [{', '.join(f'{v:.4f}' for v in rt_mat)}]")
    else:
        print(f"  All bitmap fill matrices match!")

def compare_all_frame_display_lists(og_sprites, rt_sprites, max_sprites=30):
    """Compare display lists across ALL frames, not just frame 1."""
    print(f"\n--- All-frame display list comparison ---")
    
    common = set(og_sprites.keys()) & set(rt_sprites.keys())
    total_frame_mismatches = 0
    total_matrix_diffs = 0
    total_char_diffs = 0
    total_depth_diffs = 0
    
    for cid in sorted(common)[:max_sprites]:
        og_fc, og_tags = og_sprites[cid]
        rt_fc, rt_tags = rt_sprites[cid]
        
        # Build per-frame display lists for OG
        og_display = build_display_lists(og_tags)
        rt_display = build_display_lists(rt_tags)
        
        max_frame = max(len(og_display), len(rt_display))
        sprite_issues = []
        
        for f in range(max_frame):
            og_frame = og_display[f] if f < len(og_display) else {}
            rt_frame = rt_display[f] if f < len(rt_display) else {}
            
            if set(og_frame.keys()) != set(rt_frame.keys()):
                sprite_issues.append(f"  Frame {f+1}: depth mismatch OG={sorted(og_frame.keys())} RT={sorted(rt_frame.keys())}")
                total_depth_diffs += 1
                continue
            
            for depth in og_frame:
                if depth not in rt_frame:
                    continue
                og_entry = og_frame[depth]
                rt_entry = rt_frame[depth]
                
                if og_entry.get('charId') != rt_entry.get('charId'):
                    sprite_issues.append(f"  Frame {f+1} depth {depth}: charId OG={og_entry.get('charId')} RT={rt_entry.get('charId')}")
                    total_char_diffs += 1
                
                og_mat = og_entry.get('matrix', [1,0,0,1,0,0])
                rt_mat = rt_entry.get('matrix', [1,0,0,1,0,0])
                if og_mat and rt_mat:
                    max_diff = max(abs(og_mat[j] - rt_mat[j]) for j in range(min(len(og_mat), len(rt_mat))))
                    if max_diff > 0.01:
                        sprite_issues.append(f"  Frame {f+1} depth {depth}: matrix diff={max_diff:.4f}")
                        total_matrix_diffs += 1
        
        if sprite_issues:
            total_frame_mismatches += 1
            print(f"\n  Sprite charId={cid} ({og_fc} frames):")
            for iss in sprite_issues[:10]:
                print(f"    {iss}")
            if len(sprite_issues) > 10:
                print(f"    ... +{len(sprite_issues)-10} more issues")
    
    print(f"\n  Summary: {total_frame_mismatches} sprites with issues, "
          f"{total_depth_diffs} depth mismatches, "
          f"{total_char_diffs} charId mismatches, "
          f"{total_matrix_diffs} matrix diffs")

def build_display_lists(tags):
    """Build per-frame display list from sprite's nested tags."""
    display = {}  # depth → {charId, matrix}
    frames = [{}]
    
    for tt, body in tags:
        if tt == 26:  # PlaceObject2
            po = parse_place_object2(body)
            depth = po.get('depth', 0)
            flags = po.get('flags', 0)
            
            if flags & 0x01:  # HasMove
                if depth in display:
                    entry = dict(display[depth])
                else:
                    entry = {}
            else:
                entry = {}
            
            if 'charId' in po:
                entry['charId'] = po['charId']
            if 'matrix' in po:
                entry['matrix'] = po['matrix']
            display[depth] = entry
            
        elif tt == 70:  # PlaceObject3
            if len(body) < 4:
                continue
            flags1 = body[0]
            flags2 = body[1]
            depth = struct.unpack_from('<H', body, 2)[0]
            pos = 4
            entry = {}
            
            if flags1 & 0x01:  # HasMove
                if depth in display:
                    entry = dict(display[depth])
            
            if flags1 & 0x08:  # HasClassName
                while pos < len(body) and body[pos] != 0:
                    pos += 1
                pos += 1
            
            if flags1 & 0x02:  # HasCharacter
                if pos + 2 <= len(body):
                    entry['charId'] = struct.unpack_from('<H', body, pos)[0]
                    pos += 2
            
            if flags1 & 0x04:  # HasMatrix
                br = BitReader(body, pos)
                mat = _read_matrix_from_br(br)
                entry['matrix'] = mat
            
            display[depth] = entry
            
        elif tt == 28:  # RemoveObject2
            if len(body) >= 2:
                depth = struct.unpack_from('<H', body, 0)[0]
                display.pop(depth, None)
        elif tt == 1:  # ShowFrame
            frames.append(dict(display))
    
    return frames

def main():
    print("=" * 80)
    print("BINARY-LEVEL SHAPE + DISPLAY LIST DIAGNOSTIC")
    print("=" * 80)
    
    swf_data = read_swf_bytes(SSF_PATH)
    print(f"Source: {SSF_PATH} ({len(swf_data)} bytes)")
    
    # Step 1: Parse OG SWF raw tags
    print("\n--- Step 1: Parsing OG SWF tags ---")
    og_tags = parse_tags_raw(swf_data)
    og_shapes = extract_define_shapes(og_tags)
    og_sprites = extract_define_sprites(og_tags)
    print(f"  OG: {len(og_tags)} tags, {len(og_shapes)} shapes, {len(og_sprites)} sprites")
    
    # Count shape tag types
    og_shape_types = {}
    for cid, (tt, _) in og_shapes.items():
        og_shape_types[tt] = og_shape_types.get(tt, 0) + 1
    print(f"  OG shape tag types: {og_shape_types}")
    
    # Step 2: Convert to N2D
    print("\n--- Step 2: SWF → N2D conversion ---")
    n2d_path = os.path.join(tempfile.gettempdir(), "fox_diag2.n2d")
    header, tags = parse_swf(swf_data)
    builder = N2DBuilder(header, "fox_diag")
    builder.catalog_swf_tags(tags)
    builder.frame_scripts = {}
    builder.build_all()
    builder._embed_bitmap_data_in_recodes()
    n2d_data = builder.to_n2d_json()
    save_n2d(n2d_data, n2d_path, bitmap_buffers=builder.bitmap_buffers)
    print(f"  Written: {n2d_path}")
    
    # Step 3: Compile N2D → SWF
    print("\n--- Step 3: N2D → SWF compilation ---")
    rt_path = os.path.join(tempfile.gettempdir(), "fox_diag2_rt.swf")
    shared_dir = os.path.join(os.path.dirname(__file__), 'shared')
    compiler = N2DCompiler(n2d_path, shared_dir, rt_path)
    compiler.compile()
    print(f"  Compiled: {rt_path}")
    
    # Step 4: Parse RT SWF raw tags
    print("\n--- Step 4: Parsing RT SWF tags ---")
    rt_data = read_swf_bytes(rt_path)
    rt_tags = parse_tags_raw(rt_data)
    rt_shapes = extract_define_shapes(rt_tags)
    rt_sprites = extract_define_sprites(rt_tags)
    print(f"  RT: {len(rt_tags)} tags, {len(rt_shapes)} shapes, {len(rt_sprites)} sprites")
    
    rt_shape_types = {}
    for cid, (tt, _) in rt_shapes.items():
        rt_shape_types[tt] = rt_shape_types.get(tt, 0) + 1
    print(f"  RT shape tag types: {rt_shape_types}")
    
    # Step 5: Compare shapes
    print("\n--- Step 5: Shape tag comparison ---")
    compare_shape_tags(og_shapes, rt_shapes, max_compare=200)
    
    # Step 6: Deep bitmap fill matrix analysis
    print("\n--- Step 6: Bitmap fill matrix deep analysis ---")
    sample_count = 0
    mismatch_count = 0
    for cid in sorted(set(og_shapes.keys()) & set(rt_shapes.keys()))[:100]:
        og_type, og_body = og_shapes[cid]
        rt_type, rt_body = rt_shapes[cid]
        try:
            og_fills = parse_fill_styles_from_shape(og_body, og_type)
            rt_fills = parse_fill_styles_from_shape(rt_body, rt_type)
            for fi in range(min(len(og_fills), len(rt_fills))):
                of, rf = og_fills[fi], rt_fills[fi]
                if of[0] == 'bitmap' and rf[0] == 'bitmap':
                    sample_count += 1
                    og_mat = of[1]['matrix']
                    rt_mat = rf[1]['matrix']
                    max_diff = max(abs(og_mat[j] - rt_mat[j]) for j in range(6))
                    if max_diff > 0.001:
                        mismatch_count += 1
                        if mismatch_count <= 10:
                            print(f"  charId={cid} fill#{fi} max_diff={max_diff:.6f}")
                            print(f"    OG: [{', '.join(f'{v:.6f}' for v in og_mat)}]")
                            print(f"    RT: [{', '.join(f'{v:.6f}' for v in rt_mat)}]")
        except:
            pass
    print(f"  Checked {sample_count} bitmap fills, {mismatch_count} mismatches")
    
    # Step 7: All-frame display list comparison
    print("\n--- Step 7: All-frame display list comparison ---")
    compare_all_frame_display_lists(og_sprites, rt_sprites, max_sprites=50)
    
    # Step 8: Check for bitmaps that are DefineShape-wrapped in OG but separate in RT
    print("\n--- Step 8: Bitmap wrapping analysis ---")
    # Count DefineBitsLossless2 (tag 36) and DefineBitsJPEG (tag 6,21,35) in both
    og_bitmaps = sum(1 for tt, _ in og_tags if tt in (6, 21, 35, 36, 20))
    rt_bitmaps = sum(1 for tt, _ in rt_tags if tt in (6, 21, 35, 36, 20))
    print(f"  OG bitmap definition tags: {og_bitmaps}")
    print(f"  RT bitmap definition tags: {rt_bitmaps}")
    
    # Count PlaceObject3 with has_image flag
    og_po3_image = 0
    rt_po3_image = 0
    for tt, body in og_tags:
        if tt == 70 and len(body) >= 2 and (body[1] & 0x10):
            og_po3_image += 1
    for tt, body in rt_tags:
        if tt == 70 and len(body) >= 2 and (body[1] & 0x10):
            rt_po3_image += 1
    print(f"  OG PlaceObject3 with has_image: {og_po3_image}")
    print(f"  RT PlaceObject3 with has_image: {rt_po3_image}")
    
    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
