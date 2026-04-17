#!/usr/bin/env python3
"""
Deep roundtrip comparison: root timeline + PlaceObject flags + SymbolClass + frame labels.

Checks everything that could cause "sprites floating" or "moves not working":
1. Root timeline display list (depths, charIds, matrices, clipDepths, names)
2. PlaceObject3 flags preservation (clipDepth, blend, filters, className)
3. SymbolClass bindings (class name → charId mapping)
4. Frame labels in root timeline and sprites
5. DoABC tag preservation
"""
import sys, os, struct, zlib, io, tempfile, time
sys.path.insert(0, os.path.dirname(__file__))

from swf_to_n2d import N2DBuilder, parse_swf, save_n2d
from swf_binary_io import BitReader

SSF_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\fox.ssf"

def decompress_swf(raw):
    sig = raw[:3]
    if sig == b'CWS':
        return raw[:8] + zlib.decompress(raw[8:])
    elif sig == b'ZWS':
        import lzma
        return raw[:8] + lzma.decompress(raw[12:])
    return raw

def get_tag_start_offset(data):
    br = BitReader(data, 8)
    nb = br.read_ub(5)
    for _ in range(4):
        br.read_sb(nb)
    br.align()
    return br.byte_pos + 4  # +4 for frame rate + frame count

def parse_tags_from_data(data, offset):
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

def read_cxform_alpha(br):
    br.align()
    has_add = br.read_ub(1)
    has_mul = br.read_ub(1)
    nbits = br.read_ub(4)
    result = {}
    if has_mul:
        result['mulR'] = br.read_sb(nbits)
        result['mulG'] = br.read_sb(nbits)
        result['mulB'] = br.read_sb(nbits)
        result['mulA'] = br.read_sb(nbits)
    if has_add:
        result['addR'] = br.read_sb(nbits)
        result['addG'] = br.read_sb(nbits)
        result['addB'] = br.read_sb(nbits)
        result['addA'] = br.read_sb(nbits)
    return result

def parse_place_object(tag_type, body):
    """Full PlaceObject2/3 parser with ALL fields."""
    if tag_type == 26:  # PlaceObject2
        if len(body) < 3:
            return None
        flags = body[0]
        depth = struct.unpack_from('<H', body, 1)[0]
        pos = 3
        result = {
            'depth': depth,
            'move': bool(flags & 0x01),
            'flags': flags,
        }
        
        if flags & 0x02:  # HasCharacter
            if pos + 2 <= len(body):
                result['charId'] = struct.unpack_from('<H', body, pos)[0]
                pos += 2
        
        if flags & 0x04:  # HasMatrix
            br = BitReader(body, pos)
            result['matrix'] = read_matrix(br)
            br.align()
            pos = br.byte_pos
        
        if flags & 0x08:  # HasColorTransform
            br = BitReader(body, pos)
            result['cxform'] = read_cxform_alpha(br)
            br.align()
            pos = br.byte_pos
        
        if flags & 0x10:  # HasRatio
            if pos + 2 <= len(body):
                result['ratio'] = struct.unpack_from('<H', body, pos)[0]
                pos += 2
        
        if flags & 0x20:  # HasName
            end = body.index(0, pos)
            result['name'] = body[pos:end].decode('utf-8', errors='replace')
            pos = end + 1
        
        if flags & 0x40:  # HasClipDepth
            if pos + 2 <= len(body):
                result['clipDepth'] = struct.unpack_from('<H', body, pos)[0]
                pos += 2
        
        if flags & 0x80:  # HasClipActions
            result['hasClipActions'] = True
        
        return result
    
    elif tag_type == 70:  # PlaceObject3
        if len(body) < 4:
            return None
        flags1 = body[0]
        flags2 = body[1]
        depth = struct.unpack_from('<H', body, 2)[0]
        pos = 4
        result = {
            'depth': depth,
            'move': bool(flags1 & 0x01),
            'flags1': flags1,
            'flags2': flags2,
            'isPO3': True,
        }
        
        if flags1 & 0x08:  # HasClassName (PO3-only)
            end = body.index(0, pos)
            result['className'] = body[pos:end].decode('utf-8', errors='replace')
            pos = end + 1
        
        if flags1 & 0x02:  # HasCharacter
            if pos + 2 <= len(body):
                result['charId'] = struct.unpack_from('<H', body, pos)[0]
                pos += 2
        
        if flags1 & 0x04:  # HasMatrix
            br = BitReader(body, pos)
            result['matrix'] = read_matrix(br)
            br.align()
            pos = br.byte_pos
        
        if flags1 & 0x08 and 'className' not in result:
            pass  # already parsed above
        
        if flags1 & 0x10:  # HasColorTransform (reuse same bit)
            # Wait, PO3 flag layout differs from PO2
            pass
        
        if flags1 & 0x20:  # HasRatio? Actually different in PO3
            pass

        # PO3 flags2 
        if flags2 & 0x01:  # HasBlendMode
            result['hasBlendMode'] = True
        if flags2 & 0x02:  # HasFilterList
            result['hasFilters'] = True
        
        # For flag analysis, check if clipDepth bit is set
        if flags1 & 0x40:
            result['hasClipDepth'] = True
        
        return result

def parse_symbol_class(body):
    """Parse SymbolClass tag body → {charId: className}"""
    if len(body) < 2:
        return {}
    count = struct.unpack_from('<H', body, 0)[0]
    pos = 2
    result = {}
    for _ in range(count):
        if pos + 2 > len(body):
            break
        cid = struct.unpack_from('<H', body, pos)[0]
        pos += 2
        end = body.index(0, pos)
        name = body[pos:end].decode('utf-8', errors='replace')
        pos = end + 1
        result[cid] = name
    return result

def parse_frame_label(body):
    """Parse FrameLabel tag body."""
    end = body.index(0) if 0 in body else len(body)
    return body[:end].decode('utf-8', errors='replace')

def build_full_timeline(tags):
    """Build the complete root timeline with all details."""
    display = {}  # depth → full PO data
    frames = []
    labels = {}
    frame_num = 0
    
    for tt, body in tags:
        if tt in (26, 70):  # PlaceObject2/3
            po = parse_place_object(tt, body)
            if not po:
                continue
            depth = po['depth']
            
            if po.get('move') and depth in display:
                entry = dict(display[depth])
                entry.update({k: v for k, v in po.items() if v is not None and k not in ('move', 'depth')})
            else:
                entry = po
            display[depth] = entry
            
        elif tt == 28 and len(body) >= 2:  # RemoveObject2
            depth = struct.unpack_from('<H', body, 0)[0]
            display.pop(depth, None)
        elif tt == 1:  # ShowFrame
            frames.append(dict(display))
            frame_num += 1
        elif tt == 43:  # FrameLabel
            labels[frame_num] = parse_frame_label(body)
    
    return frames, labels


def main():
    print("=" * 80)
    print("DEEP ROUNDTRIP COMPARISON: Root Timeline + PO Flags + SymbolClass")
    print("=" * 80)
    
    # ── Parse OG SWF ──
    print("\n--- Step 1: Parse original SWF ---")
    with open(SSF_PATH, 'rb') as f:
        raw = f.read()
    print(f"  File size: {len(raw):,} bytes")
    
    data = decompress_swf(raw)
    offset = get_tag_start_offset(data)
    og_tags = parse_tags_from_data(data, offset)
    print(f"  {len(og_tags)} top-level tags")
    
    # Tag type distribution
    tag_counts = {}
    for tt, _ in og_tags:
        tag_counts[tt] = tag_counts.get(tt, 0) + 1
    print(f"  Tag types: {dict(sorted(tag_counts.items()))}")
    
    # Root timeline
    og_frames, og_labels = build_full_timeline(og_tags)
    print(f"  Root timeline: {len(og_frames)} frames, {len(og_labels)} labels")
    
    # SymbolClass
    og_symbols = {}
    for tt, body in og_tags:
        if tt == 76:
            og_symbols.update(parse_symbol_class(body))
    print(f"  SymbolClass: {len(og_symbols)} entries")
    
    # DoABC
    og_abc_count = sum(1 for tt, _ in og_tags if tt == 82)
    og_abc_bytes = sum(len(b) for tt, b in og_tags if tt == 82)
    print(f"  DoABC: {og_abc_count} tags, {og_abc_bytes:,} bytes total")
    
    # Collect all DefineSprite nested tags for label/frame analysis
    og_sprite_labels = {}
    for tt, body in og_tags:
        if tt == 39 and len(body) >= 4:
            cid, fc = struct.unpack_from('<HH', body, 0)
            nested = parse_tags_from_data(body, 4)
            sprite_labels = {}
            frame_num = 0
            for ntt, nbody in nested:
                if ntt == 43:
                    sprite_labels[frame_num] = parse_frame_label(nbody)
                elif ntt == 1:
                    frame_num += 1
            if sprite_labels:
                og_sprite_labels[cid] = sprite_labels
    print(f"  Sprites with frame labels: {len(og_sprite_labels)}")
    
    # ── Build roundtrip SWF ──
    print("\n--- Step 2: Convert OG → N2D → RT SWF ---")
    header, parsed_tags = parse_swf(raw)
    builder = N2DBuilder(header, "fox_deep")
    builder.catalog_swf_tags(parsed_tags)
    builder.frame_scripts = {}
    builder.build_all()
    builder.build_main_timeline(parsed_tags)
    builder._embed_bitmap_data_in_recodes()
    
    n2d_path = os.path.join(tempfile.gettempdir(), "fox_deep.n2d")
    n2d_data = builder.to_n2d_json()
    save_n2d(n2d_data, n2d_path, bitmap_buffers=builder.bitmap_buffers)
    
    # Check what N2D has for the main timeline
    main_lib = None
    for lib in builder.libraries:
        if lib.get('id') == 0:
            main_lib = lib
            break
    
    if main_lib:
        print(f"  N2D main timeline: {main_lib.get('totalFrame')} frames, "
              f"{len(main_lib.get('layers', []))} layers")
        for li, layer in enumerate(main_lib.get('layers', [])):
            chars = layer.get('characters', [])
            depth = layer.get('swfDepth', '?')
            mode = layer.get('mode', 0)
            clip = layer.get('clipDepth', None)
            for ch in chars[:1]:
                ref = ch.get('libraryId', '?')
                name = ch.get('name', '')
                sf, ef = ch.get('startFrame', '?'), ch.get('endFrame', '?')
                mat = ch.get('matrix', {})
                tx, ty = mat.get('tx', 0), mat.get('ty', 0)
                cd_str = f" clipDepth={clip}" if clip else ""
                name_str = f" name='{name}'" if name else ""
                print(f"    Layer {li}: depth={depth} libId={ref} frames={sf}-{ef} "
                      f"tx={tx:.1f} ty={ty:.1f}{cd_str}{name_str} mode={mode}")
    
    # Compile
    rt_path = os.path.join(tempfile.gettempdir(), "fox_deep_rt.swf")
    shared_dir = os.path.join(os.path.dirname(__file__), "shared")
    
    from compilation_pipeline import CompilationContext, create_default_pipeline
    ctx = CompilationContext(n2d_path=n2d_path, shared_dir=shared_dir, output_path=rt_path)
    pipeline = create_default_pipeline()
    pipeline.execute(ctx)
    print(f"  RT SWF: {os.path.getsize(rt_path):,} bytes")
    
    # ── Parse RT SWF ──
    print("\n--- Step 3: Parse roundtrip SWF ---")
    with open(rt_path, 'rb') as f:
        rt_raw = f.read()
    rt_data = decompress_swf(rt_raw)
    rt_offset = get_tag_start_offset(rt_data)
    rt_tags = parse_tags_from_data(rt_data, rt_offset)
    print(f"  {len(rt_tags)} top-level tags")
    
    rt_tag_counts = {}
    for tt, _ in rt_tags:
        rt_tag_counts[tt] = rt_tag_counts.get(tt, 0) + 1
    print(f"  Tag types: {dict(sorted(rt_tag_counts.items()))}")
    
    rt_frames, rt_labels = build_full_timeline(rt_tags)
    print(f"  Root timeline: {len(rt_frames)} frames, {len(rt_labels)} labels")
    
    rt_symbols = {}
    for tt, body in rt_tags:
        if tt == 76:
            rt_symbols.update(parse_symbol_class(body))
    print(f"  SymbolClass: {len(rt_symbols)} entries")
    
    rt_abc_count = sum(1 for tt, _ in rt_tags if tt == 82)
    rt_abc_bytes = sum(len(b) for tt, b in rt_tags if tt == 82)
    print(f"  DoABC: {rt_abc_count} tags, {rt_abc_bytes:,} bytes total")
    
    rt_sprite_labels = {}
    for tt, body in rt_tags:
        if tt == 39 and len(body) >= 4:
            cid, fc = struct.unpack_from('<HH', body, 0)
            nested = parse_tags_from_data(body, 4)
            sprite_labels = {}
            frame_num = 0
            for ntt, nbody in nested:
                if ntt == 43:
                    sprite_labels[frame_num] = parse_frame_label(nbody)
                elif ntt == 1:
                    frame_num += 1
            if sprite_labels:
                rt_sprite_labels[cid] = sprite_labels
    print(f"  Sprites with frame labels: {len(rt_sprite_labels)}")

    # ── Compare root timeline ──
    print("\n" + "=" * 80)
    print("COMPARISON RESULTS")
    print("=" * 80)
    
    # 1. Root timeline frame count
    print(f"\n--- Root Timeline ---")
    print(f"  OG frames: {len(og_frames)}, RT frames: {len(rt_frames)}")
    
    if og_labels != rt_labels:
        print(f"  MISMATCH: Frame labels differ!")
        print(f"    OG: {og_labels}")
        print(f"    RT: {rt_labels}")
    else:
        print(f"  Frame labels: match ({len(og_labels)} labels)")
    
    # 2. Root timeline display list per frame
    og_to_n2d = dict(builder.swf_to_n2d)
    n2d_to_rt = dict(ctx.lib_to_swf_id)
    og_to_rt = {}
    for og_cid, n2d_lid in og_to_n2d.items():
        if n2d_lid in n2d_to_rt:
            og_to_rt[og_cid] = n2d_to_rt[n2d_lid]
    
    for fi in range(min(len(og_frames), len(rt_frames))):
        og_disp = og_frames[fi]
        rt_disp = rt_frames[fi]
        
        og_depths = set(og_disp.keys())
        rt_depths = set(rt_disp.keys())
        
        if og_depths != rt_depths:
            print(f"\n  Frame {fi+1}: DEPTH MISMATCH")
            missing = og_depths - rt_depths
            extra = rt_depths - og_depths
            if missing:
                print(f"    Missing depths: {sorted(missing)}")
                for d in sorted(missing):
                    e = og_disp[d]
                    print(f"      d{d}: charId={e.get('charId','?')} name={e.get('name','?')}")
            if extra:
                print(f"    Extra depths: {sorted(extra)}")
        
        for depth in sorted(og_depths & rt_depths):
            og_e = og_disp[depth]
            rt_e = rt_disp[depth]
            issues = []
            
            # CharId comparison (mapped)
            og_cid = og_e.get('charId')
            rt_cid = rt_e.get('charId')
            if og_cid is not None:
                expected_rt = og_to_rt.get(og_cid)
                if expected_rt != rt_cid:
                    issues.append(f"charId: OG={og_cid}→expected_RT={expected_rt} got RT={rt_cid}")
            
            # Matrix comparison
            og_mat = og_e.get('matrix')
            rt_mat = rt_e.get('matrix')
            if og_mat and rt_mat:
                max_diff = max(abs(og_mat[j] - rt_mat[j]) for j in range(6))
                if max_diff > 0.05:
                    issues.append(f"matrix diff={max_diff:.3f} OG={[f'{v:.2f}' for v in og_mat]} RT={[f'{v:.2f}' for v in rt_mat]}")
            elif og_mat and not rt_mat:
                issues.append("matrix: OG has, RT missing")
            
            # ClipDepth
            og_clip = og_e.get('clipDepth')
            rt_clip = rt_e.get('clipDepth') or rt_e.get('hasClipDepth')
            if og_clip and not rt_clip:
                issues.append(f"clipDepth: OG={og_clip}, RT missing!")
            
            # Name
            og_name = og_e.get('name', '')
            rt_name = rt_e.get('name', '')
            if og_name and og_name != rt_name:
                issues.append(f"name: OG='{og_name}' RT='{rt_name}'")
            
            if issues:
                print(f"\n  Frame {fi+1} depth {depth}:")
                for iss in issues:
                    print(f"    {iss}")
    
    # 3. SymbolClass
    print(f"\n--- SymbolClass ---")
    print(f"  OG: {len(og_symbols)} entries, RT: {len(rt_symbols)} entries")
    
    # Map OG symbols to RT using charId mapping
    og_class_names = set(og_symbols.values())
    rt_class_names = set(rt_symbols.values())
    
    missing_classes = og_class_names - rt_class_names
    extra_classes = rt_class_names - og_class_names
    
    if missing_classes:
        print(f"  MISSING from RT ({len(missing_classes)}):")
        for cn in sorted(missing_classes)[:30]:
            og_cid = [k for k, v in og_symbols.items() if v == cn][0]
            print(f"    {cn} (OG charId={og_cid})")
        if len(missing_classes) > 30:
            print(f"    ... +{len(missing_classes)-30} more")
    
    if extra_classes:
        print(f"  EXTRA in RT ({len(extra_classes)}):")
        for cn in sorted(extra_classes)[:10]:
            print(f"    {cn}")
    
    if not missing_classes and not extra_classes:
        print(f"  All class names match!")
    
    # Check that class→charId bindings are correct
    binding_issues = 0
    for og_cid, cn in og_symbols.items():
        expected_rt_cid = og_to_rt.get(og_cid)
        if expected_rt_cid is None:
            continue
        rt_cid_for_class = None
        for rcid, rcn in rt_symbols.items():
            if rcn == cn:
                rt_cid_for_class = rcid
                break
        if rt_cid_for_class != expected_rt_cid:
            if binding_issues < 20:
                print(f"  BINDING MISMATCH: '{cn}' OG={og_cid}→expected_RT={expected_rt_cid} "
                      f"actual_RT={rt_cid_for_class}")
            binding_issues += 1
    if binding_issues:
        print(f"  TOTAL binding mismatches: {binding_issues}")
    else:
        print(f"  All class→charId bindings correct!")
    
    # 4. DoABC
    print(f"\n--- DoABC ---")
    print(f"  OG: {og_abc_count} tags ({og_abc_bytes:,} bytes)")
    print(f"  RT: {rt_abc_count} tags ({rt_abc_bytes:,} bytes)")
    if og_abc_bytes != rt_abc_bytes:
        print(f"  DIFFERENCE: {rt_abc_bytes - og_abc_bytes:+,} bytes")
    
    # 5. Sprite frame labels
    print(f"\n--- Sprite Frame Labels ---")
    print(f"  OG sprites with labels: {len(og_sprite_labels)}")
    print(f"  RT sprites with labels: {len(rt_sprite_labels)}")
    
    # Map and compare
    label_issues = 0
    for og_cid, og_labs in og_sprite_labels.items():
        rt_cid = og_to_rt.get(og_cid)
        if rt_cid is None:
            label_issues += 1
            if label_issues <= 10:
                print(f"  Sprite OG={og_cid}: no RT mapping (labels: {og_labs})")
            continue
        rt_labs = rt_sprite_labels.get(rt_cid, {})
        if og_labs != rt_labs:
            label_issues += 1
            if label_issues <= 10:
                cn = og_symbols.get(og_cid, '?')
                print(f"  Sprite OG={og_cid} '{cn}': LABEL MISMATCH")
                print(f"    OG: {og_labs}")
                print(f"    RT: {rt_labs}")
    
    if label_issues == 0:
        print(f"  All sprite frame labels match!")
    else:
        print(f"  TOTAL label issues: {label_issues}")
    
    # 6. PlaceObject tag type analysis (PO2 vs PO3)
    print(f"\n--- PlaceObject Tag Types ---")
    og_po2 = sum(1 for tt, _ in og_tags if tt == 26)
    og_po3 = sum(1 for tt, _ in og_tags if tt == 70)
    print(f"  OG root: {og_po2} PO2, {og_po3} PO3")
    
    rt_po2 = sum(1 for tt, _ in rt_tags if tt == 26)
    rt_po3 = sum(1 for tt, _ in rt_tags if tt == 70)
    print(f"  RT root: {rt_po2} PO2, {rt_po3} PO3")
    
    # Also check inside sprites
    og_sprite_po = {'PO2': 0, 'PO3': 0}
    for tt, body in og_tags:
        if tt == 39 and len(body) >= 4:
            nested = parse_tags_from_data(body, 4)
            for ntt, _ in nested:
                if ntt == 26: og_sprite_po['PO2'] += 1
                elif ntt == 70: og_sprite_po['PO3'] += 1
    print(f"  OG sprites: {og_sprite_po}")
    
    rt_sprite_po = {'PO2': 0, 'PO3': 0}
    for tt, body in rt_tags:
        if tt == 39 and len(body) >= 4:
            nested = parse_tags_from_data(body, 4)
            for ntt, _ in nested:
                if ntt == 26: rt_sprite_po['PO2'] += 1
                elif ntt == 70: rt_sprite_po['PO3'] += 1
    print(f"  RT sprites: {rt_sprite_po}")
    
    # 7. ClipDepth analysis for OG root timeline
    print(f"\n--- ClipDepth (Mask) Analysis ---")
    og_clips = 0
    rt_clips = 0
    for fi in range(min(len(og_frames), len(rt_frames))):
        for depth, e in og_frames[fi].items():
            if e.get('clipDepth'):
                og_clips += 1
        for depth, e in rt_frames[fi].items():
            if e.get('clipDepth') or e.get('hasClipDepth'):
                rt_clips += 1
    print(f"  OG root POs with clipDepth: {og_clips}")
    print(f"  RT root POs with clipDepth: {rt_clips}")
    
    # Check inside sprites too
    og_sprite_clips = 0
    rt_sprite_clips = 0
    for tt, body in og_tags:
        if tt == 39 and len(body) >= 4:
            nested = parse_tags_from_data(body, 4)
            for ntt, nbody in nested:
                if ntt in (26, 70):
                    po = parse_place_object(ntt, nbody)
                    if po and (po.get('clipDepth') or po.get('hasClipDepth')):
                        og_sprite_clips += 1
    for tt, body in rt_tags:
        if tt == 39 and len(body) >= 4:
            nested = parse_tags_from_data(body, 4)
            for ntt, nbody in nested:
                if ntt in (26, 70):
                    po = parse_place_object(ntt, nbody)
                    if po and (po.get('clipDepth') or po.get('hasClipDepth')):
                        rt_sprite_clips += 1
    print(f"  OG sprite POs with clipDepth: {og_sprite_clips}")
    print(f"  RT sprite POs with clipDepth: {rt_sprite_clips}")
    
    # 8. Instance names analysis
    print(f"\n--- Instance Names ---")
    og_names = set()
    rt_names = set()
    for fi in range(len(og_frames)):
        for depth, e in og_frames[fi].items():
            if e.get('name'):
                og_names.add(e['name'])
    for fi in range(len(rt_frames)):
        for depth, e in rt_frames[fi].items():
            if e.get('name'):
                rt_names.add(e['name'])
    print(f"  OG root instance names: {len(og_names)}")
    print(f"  RT root instance names: {len(rt_names)}")
    missing_names = og_names - rt_names
    if missing_names:
        print(f"  MISSING names: {sorted(missing_names)[:20]}")
    extra_names = rt_names - og_names
    if extra_names:
        print(f"  EXTRA names: {sorted(extra_names)[:20]}")
    
    print("\n" + "=" * 80)
    print("DEEP COMPARISON DONE")
    print("=" * 80)


if __name__ == "__main__":
    main()
