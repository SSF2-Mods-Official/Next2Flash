#!/usr/bin/env python3
"""Deep compare: PO2 charIds INSIDE the 'fox' sprite and other key sprites.
If internal PO2 charIds point to wrong children, Fox stays in idle."""
import sys, os, struct, zlib
sys.path.insert(0, os.path.dirname(__file__))
from swf_binary_io import BitReader
from swf_to_n2d import N2DBuilder, parse_swf, save_n2d

SSF_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\fox.ssf"

TAG_NAMES = {0:'End', 1:'ShowFrame', 26:'PO2', 28:'RO2', 43:'FrameLabel', 70:'PO3'}

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

def parse_tags_raw(data, offset):
    tags = []; pos = offset
    while pos < len(data):
        if pos + 2 > len(data): break
        tcl = struct.unpack_from('<H', data, pos)[0]
        tt = tcl >> 6; tl = tcl & 0x3F; pos += 2
        if tl == 0x3F:
            tl = struct.unpack_from('<I', data, pos)[0]; pos += 4
        body = data[pos:pos+tl]; tags.append((tt, body)); pos += tl
        if tt == 0: break
    return tags

def parse_sprite_tags(body):
    fc = struct.unpack_from('<H', body, 2)[0]
    pos = 4; stags = []
    while pos < len(body):
        if pos + 2 > len(body): break
        tcl = struct.unpack_from('<H', body, pos)[0]
        stt = tcl >> 6; stl = tcl & 0x3F; pos += 2
        if stl == 0x3F:
            stl = struct.unpack_from('<I', body, pos)[0]; pos += 4
        sbody = body[pos:pos+stl]
        stags.append((stt, sbody)); pos += stl
        if stt == 0: break
    return fc, stags

def parse_po2(body):
    """Parse PlaceObject2 to extract flags, depth, charId, matrix, etc."""
    if len(body) < 3: return {}
    flags = body[0]
    depth = struct.unpack_from('<H', body, 1)[0]
    pos = 3
    result = {'flags': flags, 'depth': depth, 'move': bool(flags & 1)}
    
    if flags & 0x02:  # hasChar
        if pos + 2 <= len(body):
            result['charId'] = struct.unpack_from('<H', body, pos)[0]
            pos += 2
    
    if flags & 0x04:  # hasMatrix
        br = BitReader(body, pos)
        has_scale = br.read_ub(1)
        if has_scale:
            nb = br.read_ub(5)
            result['scaleX'] = br.read_fb(nb)
            result['scaleY'] = br.read_fb(nb)
        has_rotate = br.read_ub(1)
        if has_rotate:
            nb = br.read_ub(5)
            result['rotateSkew0'] = br.read_fb(nb)
            result['rotateSkew1'] = br.read_fb(nb)
        nb = br.read_ub(5)
        result['tx'] = br.read_sb(nb) / 20.0
        result['ty'] = br.read_sb(nb) / 20.0
    
    return result

def parse_symbol_class(body):
    if len(body) < 2: return {}
    count = struct.unpack_from('<H', body, 0)[0]
    pos = 2; result = {}
    for _ in range(count):
        if pos + 2 > len(body): break
        cid = struct.unpack_from('<H', body, pos)[0]; pos += 2
        end = body.index(0, pos) if 0 in body[pos:] else len(body)
        name = body[pos:end].decode('utf-8', errors='replace')
        pos = end + 1
        result[cid] = name
    return result


def main():
    import tempfile
    
    with open(SSF_PATH, 'rb') as f: og_raw = f.read()
    
    header, tags = parse_swf(og_raw)
    builder = N2DBuilder(header, "fox")
    builder.catalog_swf_tags(tags)
    builder.frame_scripts = {}
    builder.build_all()
    builder.build_main_timeline(tags)
    builder._embed_bitmap_data_in_recodes()
    n2d_path = os.path.join(tempfile.gettempdir(), "fox_podeep.n2d")
    n2d = builder.to_n2d_json()
    save_n2d(n2d, n2d_path, bitmap_buffers=builder.bitmap_buffers)
    rt_path = os.path.join(tempfile.gettempdir(), "fox_podeep_rt.swf")
    shared_dir = os.path.join(os.path.dirname(__file__), 'shared')
    from compilation_pipeline import CompilationContext, create_default_pipeline
    ctx = CompilationContext(n2d_path=n2d_path, shared_dir=shared_dir, output_path=rt_path)
    pipeline = create_default_pipeline()
    pipeline.execute(ctx)
    with open(rt_path, 'rb') as f: rt_raw = f.read()
    
    og_data = decompress_swf(og_raw)
    rt_data = decompress_swf(rt_raw)
    og_tags = parse_tags_raw(og_data, get_offset(og_data))
    rt_tags = parse_tags_raw(rt_data, get_offset(rt_data))
    
    # Build charId mapping
    og_to_n2d = dict(builder.swf_to_n2d)
    n2d_to_rt = dict(ctx.lib_to_swf_id)
    og_to_rt = {}
    for oc, nl in og_to_n2d.items():
        if nl in n2d_to_rt: og_to_rt[oc] = n2d_to_rt[nl]
    
    # Get SymbolClass for name lookup
    og_sym = {}
    rt_sym = {}
    for tt, body in og_tags:
        if tt == 76: og_sym = parse_symbol_class(body)
    for tt, body in rt_tags:
        if tt == 76: rt_sym = parse_symbol_class(body)
    og_sym_rev = {v: k for k, v in og_sym.items()}  # name -> cid
    
    # Collect all sprites by charId
    og_sprites = {}
    rt_sprites = {}
    for tt, body in og_tags:
        if tt == 39 and len(body) >= 4:
            cid = struct.unpack_from('<H', body, 0)[0]
            og_sprites[cid] = body
    for tt, body in rt_tags:
        if tt == 39 and len(body) >= 4:
            cid = struct.unpack_from('<H', body, 0)[0]
            rt_sprites[cid] = body
    
    print("=" * 80)
    print("DEEP PO2 CHARID COMPARISON INSIDE SPRITES")
    print("=" * 80)
    
    # Compare ALL sprites that have SymbolClass names
    total_po_checked = 0
    total_mismatches = 0
    problem_sprites = []
    
    for og_cid, name in sorted(og_sym.items()):
        if og_cid == 0: continue  # skip root 'Main'
        if og_cid not in og_sprites: continue  # not a sprite (shape, bitmap, etc.)
        
        rt_cid = og_to_rt.get(og_cid)
        if rt_cid is None:
            print(f"  WARNING: No RT mapping for OG cid={og_cid} ({name})")
            continue
        if rt_cid not in rt_sprites:
            print(f"  WARNING: RT cid={rt_cid} not found in sprites for {name}")
            continue
        
        og_fc, og_stags = parse_sprite_tags(og_sprites[og_cid])
        rt_fc, rt_stags = parse_sprite_tags(rt_sprites[rt_cid])
        
        # Extract PO2 tags with charIds
        og_pos = []
        for stt, sbody in og_stags:
            if stt == 26:
                po = parse_po2(sbody)
                if 'charId' in po:
                    og_pos.append(po)
        
        rt_pos = []
        for stt, sbody in rt_stags:
            if stt == 26:
                po = parse_po2(sbody)
                if 'charId' in po:
                    rt_pos.append(po)
        
        if len(og_pos) != len(rt_pos):
            print(f"  DIFF PO COUNT: {name} OG={len(og_pos)} RT={len(rt_pos)}")
            problem_sprites.append(name)
            continue
        
        sprite_problems = []
        for j, (opo, rpo) in enumerate(zip(og_pos, rt_pos)):
            expected_rt = og_to_rt.get(opo['charId'])
            actual_rt = rpo['charId']
            total_po_checked += 1
            
            if expected_rt != actual_rt:
                total_mismatches += 1
                sprite_problems.append(
                    f"    PO[{j}] depth={opo['depth']}: "
                    f"OG cid={opo['charId']}→expected RT={expected_rt}, got RT={actual_rt}"
                )
        
        if sprite_problems:
            print(f"\n  SPRITE: {name} (OG={og_cid}, RT={rt_cid})")
            for p in sprite_problems[:20]:
                print(p)
            if len(sprite_problems) > 20:
                print(f"    ... and {len(sprite_problems) - 20} more")
            problem_sprites.append(name)
    
    print(f"\n--- SUMMARY ---")
    print(f"  Total POs checked: {total_po_checked}")
    print(f"  Mismatches: {total_mismatches}")
    print(f"  Problem sprites: {len(problem_sprites)}")
    if problem_sprites:
        for ps in problem_sprites:
            print(f"    - {ps}")
    
    # Also compare the 'fox' sprite PO2s in detail
    fox_og_cid = og_sym_rev.get('fox')
    if fox_og_cid and fox_og_cid in og_sprites:
        fox_rt_cid = og_to_rt[fox_og_cid]
        og_fc, og_stags = parse_sprite_tags(og_sprites[fox_og_cid])
        rt_fc, rt_stags = parse_sprite_tags(rt_sprites[fox_rt_cid])
        
        print(f"\n--- FOX SPRITE DETAIL ---")
        print(f"  OG cid={fox_og_cid}, RT cid={fox_rt_cid}, frames={og_fc}")
        
        frame = 0
        og_idx = 0
        for stt, sbody in og_stags:
            if stt == 1:
                frame += 1
                continue
            if stt == 43:
                label = sbody[:sbody.index(0)].decode('utf-8','replace') if 0 in sbody else '?'
                print(f"  Frame {frame}: label='{label}'")
            if stt == 26:
                po = parse_po2(sbody)
                if 'charId' in po:
                    child_name = og_sym.get(po['charId'], '(no symclass)')
                    expected_rt = og_to_rt.get(po['charId'], '?')
                    # Find corresponding RT PO
                    print(f"    PO2 depth={po['depth']} charId={po['charId']}→{child_name} "
                          f"(expected RT: {expected_rt})")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
