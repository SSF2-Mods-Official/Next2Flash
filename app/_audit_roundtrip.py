#!/usr/bin/env python3
"""
Comprehensive roundtrip diagnostic: find ALL real data loss.
Checks:
1. Dropped move-only POs where matrix ACTUALLY differs
2. SymbolClass completeness
3. Frame label completeness
4. Root timeline content
5. File header comparison
"""
import sys, os, struct, zlib, tempfile
sys.path.insert(0, os.path.dirname(__file__))
from swf_binary_io import BitReader
from swf_to_n2d import N2DBuilder, parse_swf, save_n2d

SSF_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\fox.ssf"

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

def parse_po2(body):
    if len(body) < 3: return None
    flags = body[0]
    depth = struct.unpack_from('<H', body, 1)[0]
    pos = 3
    r = {'depth': depth, 'move': bool(flags & 0x01)}
    if flags & 0x02:
        if pos + 2 <= len(body):
            r['charId'] = struct.unpack_from('<H', body, pos)[0]; pos += 2
    if flags & 0x04:
        br = BitReader(body, pos)
        r['matrix'] = read_mat(br)
    return r

def parse_po3(body):
    if len(body) < 4: return None
    flags1 = body[0]; flags2 = body[1]
    depth = struct.unpack_from('<H', body, 2)[0]; pos = 4
    r = {'depth': depth, 'move': bool(flags1 & 0x01)}
    if flags1 & 0x08:  # HasClassName
        while pos < len(body) and body[pos] != 0: pos += 1
        pos += 1
    if flags1 & 0x02:
        if pos + 2 <= len(body):
            r['charId'] = struct.unpack_from('<H', body, pos)[0]; pos += 2
    if flags1 & 0x04:
        br = BitReader(body, pos)
        r['matrix'] = read_mat(br)
    return r

def build_display_timeline(nested_tags):
    """Build cumulative per-frame display list from nested sprite tags."""
    display = {}  # depth → {charId, matrix}
    frames = []  # list of per-frame snapshots
    labels = []
    frame_idx = 0
    for tt, body in nested_tags:
        if tt in (26, 70):
            po = parse_po2(body) if tt == 26 else parse_po3(body)
            if not po: continue
            d = po['depth']
            if po.get('move') and d in display:
                entry = dict(display[d])
            else:
                entry = {}
            if 'charId' in po: entry['charId'] = po['charId']
            if 'matrix' in po: entry['matrix'] = po['matrix']
            display[d] = entry
        elif tt == 28 and len(body) >= 2:
            display.pop(struct.unpack_from('<H', body, 0)[0], None)
        elif tt == 43:
            end = body.index(0) if 0 in body else len(body)
            labels.append((frame_idx, body[:end].decode('utf-8', errors='replace')))
        elif tt == 1:
            frames.append({d: dict(e) for d, e in display.items()})
            frame_idx += 1
    return frames, labels

def parse_symbol_class(body):
    """Parse SymbolClass tag → {charId: className}"""
    if len(body) < 2: return {}
    count = struct.unpack_from('<H', body, 0)[0]
    pos = 2
    result = {}
    for _ in range(count):
        if pos + 2 > len(body): break
        cid = struct.unpack_from('<H', body, pos)[0]; pos += 2
        end = body.index(0, pos) if 0 in body[pos:] else len(body)
        name = body[pos:end].decode('utf-8', errors='replace')
        pos = end + 1
        result[cid] = name
    return result


def main():
    with open(SSF_PATH, 'rb') as f: raw = f.read()

    # === Build RT ===
    header, tags = parse_swf(raw)
    builder = N2DBuilder(header, "fox")
    builder.catalog_swf_tags(tags)
    builder.frame_scripts = {}
    builder.build_all()
    builder.build_main_timeline(tags)
    builder._embed_bitmap_data_in_recodes()

    n2d_path = os.path.join(tempfile.gettempdir(), "fox_comp.n2d")
    n2d = builder.to_n2d_json()
    save_n2d(n2d, n2d_path, bitmap_buffers=builder.bitmap_buffers)

    rt_path = os.path.join(tempfile.gettempdir(), "fox_comp_rt.swf")
    shared_dir = os.path.join(os.path.dirname(__file__), 'shared')
    from compilation_pipeline import CompilationContext, create_default_pipeline
    ctx = CompilationContext(n2d_path=n2d_path, shared_dir=shared_dir, output_path=rt_path)
    pipeline = create_default_pipeline()
    pipeline.execute(ctx)

    og_to_n2d = dict(builder.swf_to_n2d)
    n2d_to_rt = dict(ctx.lib_to_swf_id)
    og_to_rt = {}
    for oc, nl in og_to_n2d.items():
        if nl in n2d_to_rt: og_to_rt[oc] = n2d_to_rt[nl]

    # === Parse both SWFs ===
    og_data = decompress_swf(raw)
    og_tags = parse_tags_raw(og_data, get_offset(og_data))

    with open(rt_path, 'rb') as f: rt_raw = f.read()
    rt_data = decompress_swf(rt_raw)
    rt_tags = parse_tags_raw(rt_data, get_offset(rt_data))

    print("=" * 80)
    print("COMPREHENSIVE ROUNDTRIP DATA LOSS AUDIT")
    print("=" * 80)

    # === 1. SWF Header ===
    print("\n--- 1. SWF Header ---")
    og_ver = og_data[3]
    rt_ver = rt_data[3]
    og_len = struct.unpack_from('<I', og_data, 4)[0]
    rt_len = struct.unpack_from('<I', rt_data, 4)[0]
    print(f"  OG: version={og_ver}, declared_len={og_len:,}, actual_len={len(og_data):,}, compressed={raw[:3]}")
    print(f"  RT: version={rt_ver}, declared_len={rt_len:,}, actual_len={len(rt_data):,}, compressed={rt_raw[:3]}")

    # === 2. Tag inventory ===
    print("\n--- 2. Tag type inventory ---")
    og_counts = {}
    rt_counts = {}
    for tt, _ in og_tags: og_counts[tt] = og_counts.get(tt, 0) + 1
    for tt, _ in rt_tags: rt_counts[tt] = rt_counts.get(tt, 0) + 1
    all_tt = sorted(set(og_counts) | set(rt_counts))
    TAG_NAMES = {0:'End', 1:'ShowFrame', 4:'PlaceObject', 9:'SetBackgroundColor',
                 22:'DefineShape2', 26:'PlaceObject2', 28:'RemoveObject2', 32:'DefineShape3',
                 36:'DefineBitsLossless2', 39:'DefineSprite', 43:'FrameLabel', 46:'DefineMorphShape',
                 48:'DefineFont2', 69:'FileAttributes', 70:'PlaceObject3', 75:'DefineFont3',
                 76:'SymbolClass', 82:'DoABC', 83:'DefineShape4', 84:'DefineMorphShape2',
                 86:'DefineSceneAndFrameLabel', 87:'DefineBinaryData',
                 14:'DefineSound', 15:'StartSound', 21:'DefineBitsJPEG2',
                 35:'DefineBitsJPEG3', 6:'DefineBits', 20:'DefineBitsLossless',
                 2:'DefineShape', 11:'DefineText', 37:'DefineEditText',
                 56:'ExportAssets', 88:'DefineFontName'}
    diffs = []
    for tt in all_tt:
        og_c = og_counts.get(tt, 0)
        rt_c = rt_counts.get(tt, 0)
        name = TAG_NAMES.get(tt, f'Tag{tt}')
        if og_c != rt_c:
            diffs.append(f"  {name}({tt}): OG={og_c} RT={rt_c} (diff={rt_c-og_c:+d})")
    if diffs:
        print("  Differences:")
        for d in diffs: print(d)
    else:
        print("  All tag counts match!")

    # === 3. SymbolClass ===
    print("\n--- 3. SymbolClass ---")
    og_symbols = {}
    rt_symbols = {}
    for tt, body in og_tags:
        if tt == 76: og_symbols.update(parse_symbol_class(body))
    for tt, body in rt_tags:
        if tt == 76: rt_symbols.update(parse_symbol_class(body))
    print(f"  OG: {len(og_symbols)} symbols, RT: {len(rt_symbols)} symbols")

    # Map OG symbols to RT and check class names
    missing_classes = []
    wrong_classes = []
    for og_cid, og_cls in og_symbols.items():
        if og_cid == 0:
            # Root class
            rt_cls = rt_symbols.get(0, '')
            if og_cls != rt_cls:
                wrong_classes.append(f"  Root class: OG='{og_cls}' RT='{rt_cls}'")
            continue
        rt_cid = og_to_rt.get(og_cid)
        if rt_cid is None:
            missing_classes.append(f"  OG cid={og_cid} class='{og_cls}' — no RT mapping")
            continue
        rt_cls = rt_symbols.get(rt_cid, '')
        if og_cls != rt_cls:
            wrong_classes.append(f"  OG cid={og_cid} RT cid={rt_cid}: OG='{og_cls}' RT='{rt_cls}'")
    
    if missing_classes:
        print(f"  {len(missing_classes)} missing symbols:")
        for m in missing_classes[:10]: print(m)
    if wrong_classes:
        print(f"  {len(wrong_classes)} class name mismatches:")
        for w in wrong_classes[:10]: print(w)
    if not missing_classes and not wrong_classes:
        print("  All SymbolClass entries match!")

    # === 4. Sprite-level display list comparison (FULL) ===
    print("\n--- 4. Full sprite display list comparison ---")
    # Build OG sprites
    og_sprites = {}
    for tt, body in og_tags:
        if tt == 39 and len(body) >= 4:
            cid = struct.unpack_from('<HH', body, 0)[0]
            fc = struct.unpack_from('<HH', body, 0)[1]
            nested = parse_tags_raw(body, 4)
            frames, labels = build_display_timeline(nested)
            og_sprites[cid] = (fc, frames, labels)
    # Build RT sprites
    rt_sprites = {}
    for tt, body in rt_tags:
        if tt == 39 and len(body) >= 4:
            cid = struct.unpack_from('<HH', body, 0)[0]
            fc = struct.unpack_from('<HH', body, 0)[1]
            nested = parse_tags_raw(body, 4)
            frames, labels = build_display_timeline(nested)
            rt_sprites[cid] = (fc, frames, labels)

    real_matrix_diffs = 0
    real_depth_diffs = 0
    real_charid_diffs = 0
    real_label_diffs = 0
    sprites_with_issues = []

    for og_cid in sorted(og_sprites.keys()):
        rt_cid = og_to_rt.get(og_cid)
        if rt_cid is None or rt_cid not in rt_sprites:
            continue
        og_fc, og_frames, og_labels = og_sprites[og_cid]
        rt_fc, rt_frames, rt_labels = rt_sprites[rt_cid]
        issues = []

        if og_fc != rt_fc:
            issues.append(f"Frame count: OG={og_fc} RT={rt_fc}")

        # Compare frame labels
        og_label_set = set(og_labels)
        rt_label_set = set(rt_labels)
        if og_label_set != rt_label_set:
            missing_labels = og_label_set - rt_label_set
            extra_labels = rt_label_set - og_label_set
            for fl, ln in sorted(missing_labels):
                issues.append(f"Missing label: frame {fl+1} '{ln}'")
                real_label_diffs += 1
            for fl, ln in sorted(extra_labels):
                issues.append(f"Extra label: frame {fl+1} '{ln}'")

        # Compare per-frame display lists
        max_f = max(len(og_frames), len(rt_frames))
        for f in range(max_f):
            og_d = og_frames[f] if f < len(og_frames) else {}
            rt_d = rt_frames[f] if f < len(rt_frames) else {}
            
            og_depths = set(og_d.keys())
            rt_depths = set(rt_d.keys())
            
            missing = og_depths - rt_depths
            if missing:
                for md in sorted(missing):
                    issues.append(f"Frame {f+1}: missing depth {md} (charId={og_d[md].get('charId','?')})")
                    real_depth_diffs += 1
            
            for d in og_depths & rt_depths:
                og_e = og_d[d]
                rt_e = rt_d[d]
                
                # Map OG charId to RT
                og_char = og_e.get('charId')
                expected_rt_char = og_to_rt.get(og_char) if og_char else None
                rt_char = rt_e.get('charId')
                if expected_rt_char is not None and rt_char is not None and expected_rt_char != rt_char:
                    issues.append(f"Frame {f+1} d{d}: charId OG={og_char}->RT_expected={expected_rt_char} actual={rt_char}")
                    real_charid_diffs += 1
                
                og_mat = og_e.get('matrix', [1,0,0,1,0,0])
                rt_mat = rt_e.get('matrix', [1,0,0,1,0,0])
                if og_mat and rt_mat:
                    max_diff = max(abs(og_mat[j]-rt_mat[j]) for j in range(min(len(og_mat),len(rt_mat))))
                    if max_diff > 0.05:
                        issues.append(f"Frame {f+1} d{d}: matrix diff={max_diff:.3f} OG=[{og_mat[4]:.2f},{og_mat[5]:.2f}] RT=[{rt_mat[4]:.2f},{rt_mat[5]:.2f}]")
                        real_matrix_diffs += 1
        
        if issues:
            n2d_lid = og_to_n2d.get(og_cid, '?')
            name = '?'
            for lib in builder.libraries:
                if lib.get('id') == n2d_lid:
                    name = lib.get('name', '?')
                    break
            sprites_with_issues.append((og_cid, name, issues))

    print(f"  Compared {len(og_sprites)} sprites")
    print(f"  REAL matrix mismatches: {real_matrix_diffs}")
    print(f"  REAL missing depths: {real_depth_diffs}")
    print(f"  REAL charId mismatches: {real_charid_diffs}")
    print(f"  REAL label mismatches: {real_label_diffs}")
    print(f"  Sprites with issues: {len(sprites_with_issues)}")

    for og_cid, name, issues in sprites_with_issues[:15]:
        print(f"\n  Sprite OG={og_cid} '{name}':")
        for iss in issues[:8]:
            print(f"    {iss}")
        if len(issues) > 8:
            print(f"    ... +{len(issues)-8} more")

    # === 5. Root timeline comparison ===
    print("\n--- 5. Root timeline ---")
    # OG root: tags that are PlaceObject/RemoveObject/ShowFrame at top level (not inside DefineSprite)
    og_root_frames, og_root_labels = build_display_timeline(og_tags)
    rt_root_frames, rt_root_labels = build_display_timeline(rt_tags)
    print(f"  OG root: {len(og_root_frames)} frames, {len(og_root_labels)} labels")
    print(f"  RT root: {len(rt_root_frames)} frames, {len(rt_root_labels)} labels")
    
    if og_root_labels != rt_root_labels:
        print(f"  Label diff: OG={og_root_labels} RT={rt_root_labels}")
    
    for f in range(max(len(og_root_frames), len(rt_root_frames))):
        og_d = og_root_frames[f] if f < len(og_root_frames) else {}
        rt_d = rt_root_frames[f] if f < len(rt_root_frames) else {}
        og_depths = set(og_d.keys())
        rt_depths = set(rt_d.keys())
        if og_depths != rt_depths:
            print(f"  Frame {f+1}: OG depths={sorted(og_depths)} RT depths={sorted(rt_depths)}")
            for md in og_depths - rt_depths:
                print(f"    Missing depth {md}: charId={og_d[md].get('charId','?')}")
            for ed in rt_depths - og_depths:
                print(f"    Extra depth {ed}: charId={rt_d[ed].get('charId','?')}")
        else:
            for d in og_depths:
                og_char = og_d[d].get('charId')
                expected = og_to_rt.get(og_char) if og_char else None
                rt_char = rt_d[d].get('charId')
                if expected and rt_char and expected != rt_char:
                    print(f"  Frame {f+1} d{d}: charId expected={expected} got={rt_char}")
                og_mat = og_d[d].get('matrix', [1,0,0,1,0,0])
                rt_mat = rt_d[d].get('matrix', [1,0,0,1,0,0])
                max_diff = max(abs(og_mat[j]-rt_mat[j]) for j in range(min(len(og_mat),len(rt_mat))))
                if max_diff > 0.05:
                    print(f"  Frame {f+1} d{d}: matrix diff={max_diff:.3f}")

    # === 6. DoABC comparison ===
    print("\n--- 6. DoABC (AS3 bytecode) ---")
    og_abc = [body for tt, body in og_tags if tt == 82]
    rt_abc = [body for tt, body in rt_tags if tt == 82]
    print(f"  OG: {len(og_abc)} DoABC tags, total {sum(len(b) for b in og_abc):,} bytes")
    print(f"  RT: {len(rt_abc)} DoABC tags, total {sum(len(b) for b in rt_abc):,} bytes")
    if og_abc and rt_abc:
        if og_abc[0] == rt_abc[0]:
            print("  DoABC content: IDENTICAL (raw passthrough)")
        else:
            print("  DoABC content: DIFFERENT!")
            # Check if it's just a flag or prefix difference
            for i in range(min(len(og_abc[0]), len(rt_abc[0]))):
                if og_abc[0][i] != rt_abc[0][i]:
                    print(f"    First difference at byte {i}: OG=0x{og_abc[0][i]:02x} RT=0x{rt_abc[0][i]:02x}")
                    break

    # === 7. Sound tags ===
    print("\n--- 7. Sound tags ---")
    og_sounds = [(tt, body) for tt, body in og_tags if tt == 14]
    rt_sounds = [(tt, body) for tt, body in rt_tags if tt == 14]
    print(f"  OG: {len(og_sounds)} DefineSound, RT: {len(rt_sounds)} DefineSound")
    og_starts = [(tt, body) for tt, body in og_tags if tt == 15]
    rt_starts = [(tt, body) for tt, body in rt_tags if tt == 15]
    print(f"  OG: {len(og_starts)} StartSound, RT: {len(rt_starts)} StartSound")

    print("\n" + "=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
