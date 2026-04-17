#!/usr/bin/env python3
"""
Final focused comparison: check header, every sprite's move flag pattern,
and specifically test if any sprites have wrong frame ranges.
"""
import sys, os, struct, zlib, tempfile
sys.path.insert(0, os.path.dirname(__file__))
from swf_binary_io import BitReader
from swf_to_n2d import N2DBuilder, parse_swf, save_n2d

SSF_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\fox.ssf"

def decompress_swf(raw):
    sig = raw[:3]
    if sig == b'CWS':
        return raw[:8] + zlib.decompress(raw[8:])
    return raw

def parse_header(data):
    """Parse full SWF header."""
    version = data[3]
    file_len = struct.unpack_from('<I', data, 4)[0]
    br = BitReader(data, 8)
    nb = br.read_ub(5)
    xmin = br.read_sb(nb) / 20.0
    xmax = br.read_sb(nb) / 20.0
    ymin = br.read_sb(nb) / 20.0
    ymax = br.read_sb(nb) / 20.0
    br.align()
    fps_frac = data[br.byte_pos]
    fps_int = data[br.byte_pos + 1]
    fps = fps_int + fps_frac / 256.0
    frame_count = struct.unpack_from('<H', data, br.byte_pos + 2)[0]
    return {
        'version': version,
        'file_len': file_len,
        'rect': (xmin, xmax, ymin, ymax),
        'fps': fps,
        'frameCount': frame_count,
        'tag_offset': br.byte_pos + 4,
    }

def parse_tags(data, offset):
    tags = []
    pos = offset
    while pos < len(data):
        if pos + 2 > len(data): break
        tcl = struct.unpack_from('<H', data, pos)[0]
        tt = tcl >> 6; tl = tcl & 0x3F; pos += 2
        if tl == 0x3F:
            if pos + 4 > len(data): break
            tl = struct.unpack_from('<I', data, pos)[0]; pos += 4
        body = data[pos:pos+tl]; tags.append((tt, body)); pos += tl
        if tt == 0: break
    return tags

def read_matrix(br):
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

def parse_po2(body):
    if len(body) < 3: return None
    flags = body[0]
    depth = struct.unpack_from('<H', body, 1)[0]
    pos = 3
    r = {'depth': depth, 'move': bool(flags & 0x01)}
    if flags & 0x02:
        r['charId'] = struct.unpack_from('<H', body, pos)[0]; pos += 2
    if flags & 0x04:
        br = BitReader(body, pos); r['matrix'] = read_matrix(br)
    return r

def parse_po3(body):
    if len(body) < 4: return None
    f1 = body[0]; f2 = body[1]
    depth = struct.unpack_from('<H', body, 2)[0]
    pos = 4
    r = {'depth': depth, 'move': bool(f1 & 0x01)}
    if f1 & 0x08:  # className - skip it
        while pos < len(body) and body[pos] != 0: pos += 1
        pos += 1
    if f1 & 0x02:
        if pos + 2 <= len(body):
            r['charId'] = struct.unpack_from('<H', body, pos)[0]; pos += 2
    if f1 & 0x04:
        br = BitReader(body, pos); r['matrix'] = read_matrix(br)
    return r

def get_sprite_po_sequence(nested_tags):
    """Get exact sequence of PO operations per frame for a sprite."""
    frames = []
    current_ops = []
    for tt, body in nested_tags:
        if tt == 26:
            po = parse_po2(body)
            if po: current_ops.append(po)
        elif tt == 70:
            po = parse_po3(body)
            if po: current_ops.append(po)
        elif tt == 28 and len(body) >= 2:
            depth = struct.unpack_from('<H', body, 0)[0]
            current_ops.append({'remove': True, 'depth': depth})
        elif tt == 1:
            frames.append(current_ops)
            current_ops = []
    return frames

def main():
    with open(SSF_PATH, 'rb') as f:
        raw = f.read()
    print("=" * 80)
    print("SWF HEADER + MOVE FLAG COMPARISON")
    print("=" * 80)
    
    # OG
    og_data = decompress_swf(raw)
    og_hdr = parse_header(og_data)
    og_tags = parse_tags(og_data, og_hdr['tag_offset'])
    
    # Roundtrip
    header, parsed = parse_swf(raw)
    builder = N2DBuilder(header, "fox")
    builder.catalog_swf_tags(parsed)
    builder.frame_scripts = {}
    builder.build_all()
    builder.build_main_timeline(parsed)
    builder._embed_bitmap_data_in_recodes()
    
    n2d_path = os.path.join(tempfile.gettempdir(), "fox_final.n2d")
    n2d = builder.to_n2d_json()
    save_n2d(n2d, n2d_path, bitmap_buffers=builder.bitmap_buffers)
    
    rt_path = os.path.join(tempfile.gettempdir(), "fox_final_rt.swf")
    shared_dir = os.path.join(os.path.dirname(__file__), "shared")
    from compilation_pipeline import CompilationContext, create_default_pipeline
    ctx = CompilationContext(n2d_path=n2d_path, shared_dir=shared_dir, output_path=rt_path)
    pipeline = create_default_pipeline()
    pipeline.execute(ctx)
    
    with open(rt_path, 'rb') as f:
        rt_raw = f.read()
    rt_data = decompress_swf(rt_raw)
    rt_hdr = parse_header(rt_data)
    rt_tags = parse_tags(rt_data, rt_hdr['tag_offset'])
    
    # Header compare
    print(f"\n--- SWF Header ---")
    for key in ['version', 'file_len', 'rect', 'fps', 'frameCount']:
        og_v = og_hdr[key]
        rt_v = rt_hdr[key]
        match = "OK" if og_v == rt_v else "MISMATCH!"
        print(f"  {key}: OG={og_v} RT={rt_v} [{match}]")
    
    # Build OG→RT charId map
    og_to_n2d = dict(builder.swf_to_n2d)
    n2d_to_rt = dict(ctx.lib_to_swf_id)
    og_to_rt = {}
    for og_cid, n2d_lid in og_to_n2d.items():
        if n2d_lid in n2d_to_rt:
            og_to_rt[og_cid] = n2d_to_rt[n2d_lid]
    
    # Compare sprite PO sequences (move flags, charIds, removes)
    print(f"\n--- Sprite PlaceObject Sequence Comparison ---")
    
    og_sprites = {}
    for tt, body in og_tags:
        if tt == 39 and len(body) >= 4:
            cid, fc = struct.unpack_from('<HH', body, 0)
            nested = parse_tags(body, 4)
            og_sprites[cid] = (fc, get_sprite_po_sequence(nested))
    
    rt_sprites = {}
    for tt, body in rt_tags:
        if tt == 39 and len(body) >= 4:
            cid, fc = struct.unpack_from('<HH', body, 0)
            nested = parse_tags(body, 4)
            rt_sprites[cid] = (fc, get_sprite_po_sequence(nested))
    
    move_flag_mismatches = 0
    remove_mismatches = 0
    depth_mismatches = 0
    char_mismatches = 0
    sprites_with_issues = 0
    
    for og_cid in sorted(og_sprites.keys()):
        rt_cid = og_to_rt.get(og_cid)
        if rt_cid is None or rt_cid not in rt_sprites:
            continue
        
        og_fc, og_seq = og_sprites[og_cid]
        rt_fc, rt_seq = rt_sprites[rt_cid]
        
        issues = []
        
        for fi in range(min(len(og_seq), len(rt_seq))):
            og_ops = og_seq[fi]
            rt_ops = rt_seq[fi]
            
            # Separate removes and places
            og_removes = sorted([op['depth'] for op in og_ops if op.get('remove')])
            rt_removes = sorted([op['depth'] for op in rt_ops if op.get('remove')])
            og_places = [op for op in og_ops if not op.get('remove')]
            rt_places = [op for op in rt_ops if not op.get('remove')]
            
            if og_removes != rt_removes:
                issues.append(f"F{fi+1}: removes OG={og_removes} RT={rt_removes}")
                remove_mismatches += 1
            
            # Compare places by depth
            og_by_depth = {op['depth']: op for op in og_places}
            rt_by_depth = {op['depth']: op for op in rt_places}
            
            og_d = set(og_by_depth.keys())
            rt_d = set(rt_by_depth.keys())
            
            if og_d != rt_d:
                missing = og_d - rt_d
                extra = rt_d - og_d
                if missing:
                    issues.append(f"F{fi+1}: missing PO depths {sorted(missing)}")
                    depth_mismatches += len(missing)
                if extra:
                    issues.append(f"F{fi+1}: extra PO depths {sorted(extra)}")
                    depth_mismatches += len(extra)
            
            for d in og_d & rt_d:
                og_op = og_by_depth[d]
                rt_op = rt_by_depth[d]
                
                if og_op.get('move') != rt_op.get('move'):
                    issues.append(f"F{fi+1} d{d}: move flag OG={og_op.get('move')} RT={rt_op.get('move')}")
                    move_flag_mismatches += 1
                
                og_char = og_op.get('charId')
                rt_char = rt_op.get('charId')
                if og_char is not None:
                    expected = og_to_rt.get(og_char)
                    if expected != rt_char:
                        issues.append(f"F{fi+1} d{d}: charId OG={og_char} expected={expected} RT={rt_char}")
                        char_mismatches += 1
                elif rt_char is not None:
                    # RT has charId but OG doesn't (move-only in OG, place+char in RT)
                    issues.append(f"F{fi+1} d{d}: OG no charId, RT={rt_char}")
                    char_mismatches += 1
        
        # Check if OG has more frames with ops
        if len(og_seq) != len(rt_seq):
            issues.append(f"Different frame op counts: OG={len(og_seq)} RT={len(rt_seq)}")
        
        if issues:
            sprites_with_issues += 1
            if sprites_with_issues <= 15:
                n2d_lid = og_to_n2d.get(og_cid, '?')
                name = '?'
                for lib in builder.libraries:
                    if lib.get('id') == n2d_lid:
                        name = lib.get('name', '?')
                        break
                print(f"\n  Sprite OG={og_cid} RT={rt_cid} '{name}' ({og_fc}f):")
                for iss in issues[:10]:
                    print(f"    {iss}")
                if len(issues) > 10:
                    print(f"    ... +{len(issues)-10} more")
    
    print(f"\n  SUMMARY:")
    print(f"    Sprites with issues: {sprites_with_issues} / {len(og_sprites)}")
    print(f"    Move flag mismatches: {move_flag_mismatches}")
    print(f"    Remove mismatches: {remove_mismatches}")
    print(f"    Depth mismatches: {depth_mismatches}")
    print(f"    CharId mismatches: {char_mismatches}")
    print(f"\n  {'='*80}")

if __name__ == "__main__":
    main()
