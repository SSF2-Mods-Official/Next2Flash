#!/usr/bin/env python3
"""
Mapped roundtrip diagnostic: uses N2D library ID mapping to properly compare
OG SWF charIds with RT SWF charIds.

Focus areas:
1. Sprite (MovieClip) display lists: are all layers preserved?
2. Bitmap fill matrices within shapes: do they roundtrip accurately?
3. Identify specific sprites/shapes where data is lost.
"""
import sys, os, struct, io, tempfile, zlib, time
sys.path.insert(0, os.path.dirname(__file__))

from swf_to_n2d import (
    N2DBuilder, parse_swf, save_n2d, parse_tags,
)
from compile_n2d import N2DCompiler
from swf_binary_io import BitReader

SSF_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\fox.ssf"

def parse_tags_from_data(data, offset):
    """Parse SWF tags from raw decompressed bytes."""
    tags = []
    pos = offset
    while pos < len(data):
        if pos + 2 > len(data):
            break
        tcl = struct.unpack_from('<H', data, pos)[0]
        tt = tcl >> 6
        tl = tcl & 0x3F
        pos += 2
        if tl == 0x3F:
            if pos + 4 > len(data):
                break
            tl = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        body = data[pos:pos+tl]
        tags.append((tt, body))
        pos += tl
        if tt == 0:
            break
    return tags

def decompress_swf(raw):
    sig = raw[:3]
    if sig == b'CWS':
        return raw[:8] + zlib.decompress(raw[8:])
    elif sig == b'ZWS':
        import lzma
        return raw[:8] + lzma.decompress(raw[12:])
    return raw

def get_tag_start_offset(data):
    """Get offset to first tag after SWF header."""
    br = BitReader(data, 8)
    nb = br.read_ub(5)
    for _ in range(4):
        br.read_sb(nb)
    br.align()
    return br.byte_pos + 4

def extract_sprites_display(tags):
    """Extract DefineSprite display lists: {charId: (frameCount, per_frame_display)}"""
    sprites = {}
    for tt, body in tags:
        if tt == 39 and len(body) >= 4:
            cid, fc = struct.unpack_from('<HH', body, 0)
            nested = parse_tags_from_data(body, 4)
            frames = build_sprite_display(nested)
            sprites[cid] = (fc, frames)
    return sprites

def build_sprite_display(nested_tags):
    """Build per-frame display lists from sprite nested tags."""
    display = {}  # depth → {charId, matrix}
    frames = []
    
    for tt, body in nested_tags:
        if tt in (26, 70):  # PlaceObject2/3
            po = parse_po(tt, body)
            if not po:
                continue
            depth = po['depth']
            
            if po.get('move') and depth in display:
                entry = dict(display[depth])
            else:
                entry = {}
            
            if 'charId' in po:
                entry['charId'] = po['charId']
            if 'matrix' in po:
                entry['matrix'] = po['matrix']
            display[depth] = entry
            
        elif tt == 28 and len(body) >= 2:  # RemoveObject2
            depth = struct.unpack_from('<H', body, 0)[0]
            display.pop(depth, None)
        elif tt == 1:  # ShowFrame
            frames.append(dict(display))
    
    return frames

def parse_po(tag_type, body):
    """Parse PlaceObject2 or PlaceObject3."""
    if tag_type == 26:
        if len(body) < 3:
            return None
        flags = body[0]
        depth = struct.unpack_from('<H', body, 1)[0]
        pos = 3
        result = {'depth': depth, 'move': bool(flags & 0x01)}
        
        if flags & 0x02:  # HasCharacter
            if pos + 2 <= len(body):
                result['charId'] = struct.unpack_from('<H', body, pos)[0]
                pos += 2
        
        if flags & 0x04:  # HasMatrix
            br = BitReader(body, pos)
            result['matrix'] = read_mat(br)
        
        return result
        
    elif tag_type == 70:
        if len(body) < 4:
            return None
        flags1 = body[0]
        flags2 = body[1]
        depth = struct.unpack_from('<H', body, 2)[0]
        pos = 4
        result = {'depth': depth, 'move': bool(flags1 & 0x01)}
        
        if flags1 & 0x08:  # HasClassName
            while pos < len(body) and body[pos] != 0:
                pos += 1
            pos += 1
        
        if flags1 & 0x02:  # HasCharacter
            if pos + 2 <= len(body):
                result['charId'] = struct.unpack_from('<H', body, pos)[0]
                pos += 2
        
        if flags1 & 0x04:  # HasMatrix
            br = BitReader(body, pos)
            result['matrix'] = read_mat(br)
        
        return result

def read_mat(br):
    br.align()
    mat = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
    if br.read_ub(1):
        n = br.read_ub(5)
        mat[0] = br.read_sb(n) / 65536.0
        mat[3] = br.read_sb(n) / 65536.0
    if br.read_ub(1):
        n = br.read_ub(5)
        mat[1] = br.read_sb(n) / 65536.0
        mat[2] = br.read_sb(n) / 65536.0
    n = br.read_ub(5)
    mat[4] = br.read_sb(n) / 20.0
    mat[5] = br.read_sb(n) / 20.0
    return mat

def extract_shapes_with_fills(tags):
    """Extract shapes with bitmap fill info: {charId: (tag_type, fills)}"""
    shapes = {}
    for tt, body in tags:
        if tt in (2, 22, 32, 83) and len(body) >= 2:
            cid = struct.unpack_from('<H', body, 0)[0]
            try:
                fills = parse_fills(body, tt)
            except:
                fills = []
            shapes[cid] = (tt, fills)
    return shapes

def parse_fills(body, tag_type):
    """Parse fill style array from DefineShape body."""
    br = BitReader(body, 2)
    nb = br.read_ub(5)
    for _ in range(4):
        br.read_sb(nb)
    br.align()
    
    if tag_type == 83:  # DefineShape4
        nb2 = br.read_ub(5)
        for _ in range(4):
            br.read_sb(nb2)
        br.align()
        br.read_ui8()  # flags
    
    count = br.read_ui8()
    if count == 0xFF:
        count = br.read_ui8() | (br.read_ui8() << 8)
    
    fills = []
    for _ in range(count):
        ftype = br.read_ui8()
        if ftype == 0x00:  # Solid
            if tag_type in (32, 83):
                fills.append(('solid', (br.read_ui8(), br.read_ui8(), br.read_ui8(), br.read_ui8())))
            else:
                fills.append(('solid', (br.read_ui8(), br.read_ui8(), br.read_ui8())))
        elif ftype in (0x10, 0x12, 0x13):  # Gradient
            mat = read_mat(br)
            si_count_byte = br.read_ui8()
            num_grad = si_count_byte & 0x0F
            for _ in range(num_grad):
                br.read_ui8()
                if tag_type in (32, 83):
                    br.read_ui8(); br.read_ui8(); br.read_ui8(); br.read_ui8()
                else:
                    br.read_ui8(); br.read_ui8(); br.read_ui8()
            if ftype == 0x13:
                br.read_ui8(); br.read_ui8()
            fills.append(('gradient', mat))
        elif ftype in (0x40, 0x41, 0x42, 0x43):  # Bitmap
            bmp_id = br.read_ui8() | (br.read_ui8() << 8)
            mat = read_mat(br)
            fills.append(('bitmap', {'bmpId': bmp_id, 'matrix': mat, 'type': ftype}))
        else:
            fills.append(('unknown', ftype))
            break
    
    return fills


def main():
    print("=" * 80)
    print("MAPPED ROUNDTRIP DIAGNOSTIC")
    print("=" * 80)
    
    with open(SSF_PATH, 'rb') as f:
        raw = f.read()
    
    # Parse OG SWF
    print("\n--- Step 1: Parse OG SWF ---")
    data = decompress_swf(raw)
    offset = get_tag_start_offset(data)
    og_raw_tags = parse_tags_from_data(data, offset)
    og_sprites = extract_sprites_display(og_raw_tags)
    og_shapes = extract_shapes_with_fills(og_raw_tags)
    print(f"  {len(og_sprites)} sprites, {len(og_shapes)} shapes")
    
    # Convert to N2D and get mappings
    print("\n--- Step 2: Convert to N2D ---")
    header, tags = parse_swf(raw)
    builder = N2DBuilder(header, "fox_diag")
    builder.catalog_swf_tags(tags)
    builder.frame_scripts = {}
    builder.build_all()
    builder._embed_bitmap_data_in_recodes()
    
    # The critical mapping: OG swf charId → N2D library ID
    og_to_n2d = dict(builder.swf_to_n2d)  # swf_charId → n2d_libId
    print(f"  OG→N2D mapping: {len(og_to_n2d)} entries")
    
    n2d_path = os.path.join(tempfile.gettempdir(), "fox_diag3.n2d")
    n2d_data = builder.to_n2d_json()
    save_n2d(n2d_data, n2d_path, bitmap_buffers=builder.bitmap_buffers)
    print(f"  Saved: {n2d_path}")
    
    # Get N2D container data for analysis
    containers = [lib for lib in builder.libraries if lib.get("type") == "container"]
    print(f"  {len(containers)} containers in N2D")
    
    # Compile to SWF
    print("\n--- Step 3: Compile N2D → SWF ---")
    rt_path = os.path.join(tempfile.gettempdir(), "fox_diag3_rt.swf")
    shared_dir = os.path.join(os.path.dirname(__file__), 'shared')

    from compilation_pipeline import CompilationContext, create_default_pipeline
    ctx = CompilationContext(
        n2d_path=n2d_path,
        shared_dir=shared_dir,
        output_path=rt_path,
    )
    pipeline = create_default_pipeline()
    pipeline.execute(ctx)
    
    # The critical mapping: N2D library ID → RT swf charId
    n2d_to_rt = dict(ctx.lib_to_swf_id)
    print(f"  N2D→RT mapping: {len(n2d_to_rt)} entries")
    
    # Build OG charId → RT charId mapping
    og_to_rt = {}
    for og_cid, n2d_lid in og_to_n2d.items():
        if n2d_lid in n2d_to_rt:
            og_to_rt[og_cid] = n2d_to_rt[n2d_lid]
    print(f"  OG→RT mapping: {len(og_to_rt)} entries")
    
    # Parse RT SWF
    print("\n--- Step 4: Parse RT SWF ---")
    with open(rt_path, 'rb') as f:
        rt_raw = f.read()
    rt_data = decompress_swf(rt_raw)
    rt_offset = get_tag_start_offset(rt_data)
    rt_raw_tags = parse_tags_from_data(rt_data, rt_offset)
    rt_sprites = extract_sprites_display(rt_raw_tags)
    rt_shapes = extract_shapes_with_fills(rt_raw_tags)
    print(f"  {len(rt_sprites)} sprites, {len(rt_shapes)} shapes")
    
    # Step 5: Compare sprites with proper ID mapping
    print("\n--- Step 5: Sprite display list comparison (mapped) ---")
    sprite_issues = 0
    total_depth_miss = 0
    total_char_miss = 0
    total_matrix_miss = 0
    
    for og_cid in sorted(og_sprites.keys()):
        rt_cid = og_to_rt.get(og_cid)
        if rt_cid is None or rt_cid not in rt_sprites:
            continue
        
        og_fc, og_frames = og_sprites[og_cid]
        rt_fc, rt_frames = rt_sprites[rt_cid]
        
        issues = []
        
        if og_fc != rt_fc:
            issues.append(f"Frame count: OG={og_fc} RT={rt_fc}")
        
        max_f = max(len(og_frames), len(rt_frames))
        for f in range(max_f):
            og_disp = og_frames[f] if f < len(og_frames) else {}
            rt_disp = rt_frames[f] if f < len(rt_frames) else {}
            
            # Map OG charIds to RT charIds for comparison
            og_mapped = {}
            for depth, entry in og_disp.items():
                mapped_entry = dict(entry)
                if 'charId' in entry:
                    mapped_entry['rt_charId'] = og_to_rt.get(entry['charId'])
                og_mapped[depth] = mapped_entry
            
            og_depths = set(og_mapped.keys())
            rt_depths = set(rt_disp.keys())
            
            if og_depths != rt_depths:
                missing = og_depths - rt_depths
                extra = rt_depths - og_depths
                if missing:
                    issues.append(f"Frame {f+1}: missing depths {sorted(missing)} (OG depths={sorted(og_depths)} RT depths={sorted(rt_depths)})")
                    total_depth_miss += len(missing)
                if extra:
                    issues.append(f"Frame {f+1}: extra depths {sorted(extra)}")
            
            for depth in og_depths & rt_depths:
                og_e = og_mapped[depth]
                rt_e = rt_disp[depth]
                
                og_mapped_cid = og_e.get('rt_charId')
                rt_char = rt_e.get('charId')
                if og_mapped_cid is not None and rt_char is not None and og_mapped_cid != rt_char:
                    issues.append(f"Frame {f+1} d{depth}: charId expected RT={og_mapped_cid} got {rt_char}")
                    total_char_miss += 1
                
                og_mat = og_e.get('matrix', [1,0,0,1,0,0])
                rt_mat = rt_e.get('matrix', [1,0,0,1,0,0])
                if og_mat and rt_mat:
                    max_diff = max(abs(og_mat[j]-rt_mat[j]) for j in range(min(len(og_mat),len(rt_mat))))
                    if max_diff > 0.05:
                        issues.append(f"Frame {f+1} d{depth}: matrix diff={max_diff:.3f}")
                        total_matrix_miss += 1
        
        if issues:
            sprite_issues += 1
            # Find name from N2D
            n2d_lid = og_to_n2d.get(og_cid, '?')
            name = '?'
            for lib in builder.libraries:
                if lib.get('id') == n2d_lid:
                    name = lib.get('name', '?')
                    break
            
            print(f"\n  Sprite OG={og_cid} RT={rt_cid} n2d={n2d_lid} name='{name}' "
                  f"(OG {og_fc}f, RT {rt_fc}f):")
            for iss in issues[:15]:
                print(f"    {iss}")
            if len(issues) > 15:
                print(f"    ... +{len(issues)-15} more")
    
    print(f"\n  TOTAL: {sprite_issues} sprites with issues, "
          f"{total_depth_miss} missing depths, "
          f"{total_char_miss} charId mismatches, "
          f"{total_matrix_miss} matrix mismatches")
    
    # Step 6: Compare shapes (bitmap fills) with proper ID mapping
    print("\n--- Step 6: Bitmap fill comparison (mapped) ---")
    bmp_total = 0
    bmp_mismatch = 0
    
    for og_cid in sorted(og_shapes.keys()):
        rt_cid = og_to_rt.get(og_cid)
        if rt_cid is None or rt_cid not in rt_shapes:
            continue
        
        og_tt, og_fills = og_shapes[og_cid]
        rt_tt, rt_fills = rt_shapes[rt_cid]
        
        og_bmps = [f for f in og_fills if f[0] == 'bitmap']
        rt_bmps = [f for f in rt_fills if f[0] == 'bitmap']
        
        for i in range(min(len(og_bmps), len(rt_bmps))):
            bmp_total += 1
            og_mat = og_bmps[i][1]['matrix']
            rt_mat = rt_bmps[i][1]['matrix']
            max_diff = max(abs(og_mat[j]-rt_mat[j]) for j in range(6))
            if max_diff > 0.01:
                bmp_mismatch += 1
                if bmp_mismatch <= 20:
                    name = '?'
                    n2d_lid = og_to_n2d.get(og_cid, '?')
                    for lib in builder.libraries:
                        if lib.get('id') == n2d_lid:
                            name = lib.get('name', '?')
                            break
                    print(f"  Shape OG={og_cid} RT={rt_cid} name='{name}' fill#{i}:")
                    print(f"    OG: [{', '.join(f'{v:.4f}' for v in og_mat)}]")
                    print(f"    RT: [{', '.join(f'{v:.4f}' for v in rt_mat)}]")
                    print(f"    diff={max_diff:.4f}")
        
        if len(og_bmps) != len(rt_bmps):
            bmp_mismatch += 1
            if bmp_mismatch <= 20:
                print(f"  Shape OG={og_cid} RT={rt_cid}: fill count OG={len(og_bmps)} RT={len(rt_bmps)}")
    
    print(f"\n  Checked {bmp_total} bitmap fills, {bmp_mismatch} with issues")
    
    # Step 7: Investigate specific charId resolution failures
    print("\n--- Step 7: Detailed charId resolution investigation ---")
    
    # For each broken sprite, trace the charId through the mapping chain
    broken_sprites = [
        (698, "landmasterLaser_146"),
        (1277, "fox_landmasterstart_finalform2_142"),
        (1348, "fox_fspec_effect"),
    ]
    
    for og_cid, name in broken_sprites:
        rt_cid = og_to_rt.get(og_cid)
        if rt_cid is None or rt_cid not in rt_sprites:
            print(f"\n  Sprite OG={og_cid} '{name}': not in RT sprites")
            continue
        
        n2d_lid = og_to_n2d.get(og_cid)
        n2d_lib = None
        for lib in builder.libraries:
            if lib.get('id') == n2d_lid:
                n2d_lib = lib
                break
        
        if not n2d_lib:
            print(f"  Sprite OG={og_cid} '{name}': N2D lib {n2d_lid} not found")
            continue
        
        print(f"\n  Sprite OG={og_cid} → N2D={n2d_lid} → RT={rt_cid} '{name}'")
        
        _, og_frames = og_sprites[og_cid]
        _, rt_frames = rt_sprites[rt_cid]
        
        # Show N2D layers and trace each character's ID chain
        layers = n2d_lib.get('layers', [])
        for li, layer in enumerate(layers):
            depth = layer.get('swfDepth', '?')
            chars = layer.get('characters', [])
            print(f"    Layer {li}: swfDepth={depth} mode={layer.get('mode', 0)}")
            
            for ci, ch in enumerate(chars[:5]):
                ref_lid = ch.get('libraryId', 0)
                sf, ef = ch.get('startFrame'), ch.get('endFrame')
                
                # Trace through mapping chain
                char_idx = ctx.lib_to_char_idx.get(ref_lid, '??')
                swf_cid = ctx.char_idx_to_swf_id.get(char_idx, '??') if isinstance(char_idx, int) else '??'
                expected_rt = n2d_to_rt.get(ref_lid, '??')
                
                # What the OG SWF had at this depth
                og_frame_cid = None
                if og_frames and sf-1 < len(og_frames):
                    for d, entry in og_frames[sf-1].items():
                        if d == depth:
                            og_frame_cid = entry.get('charId')
                
                print(f"      Char {ci}: libId={ref_lid} frames={sf}-{ef}")
                print(f"        chain: lib_to_char_idx[{ref_lid}]={char_idx} "
                      f"char_idx_to_swf_id[{char_idx}]={swf_cid} "
                      f"expected_rt(n2d_to_rt[{ref_lid}])={expected_rt}")
                print(f"        OG depth {depth} charId={og_frame_cid}")
                
                if swf_cid != expected_rt and swf_cid != '??':
                    print(f"        *** MISMATCH: timeline resolves to {swf_cid} but should be {expected_rt}")
                    # What library does swf_cid=513 correspond to?
                    for nlid, nsid in n2d_to_rt.items():
                        if nsid == swf_cid:
                            # Find what type
                            for lib in builder.libraries:
                                if lib.get('id') == nlid:
                                    print(f"        *** RT charId {swf_cid} actually maps to N2D lib {nlid} type={lib.get('type')} name='{lib.get('name','?')}'")
                                    break
                            break
    
    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
