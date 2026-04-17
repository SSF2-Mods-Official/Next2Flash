#!/usr/bin/env python3
"""Check sprite 1140 (fox_specialU_50) depth issue on frame 23."""
import sys, os, struct, zlib, tempfile
sys.path.insert(0, os.path.dirname(__file__))
from swf_binary_io import BitReader
from swf_to_n2d import N2DBuilder, parse_swf, save_n2d, parse_place_object2, parse_place_object3

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

def parse_tags(data, offset):
    tags = []; pos = offset
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

def dump_sprite_ops(tags_data, sprite_cid, around_frame=23, context=3):
    """Find a DefineSprite tag and dump PO operations around a target frame."""
    for tt, body in tags_data:
        if tt != 39 or len(body) < 4: continue
        cid, fc = struct.unpack_from('<HH', body, 0)
        if cid != sprite_cid: continue
        
        nested = parse_tags(body, 4)
        frame = 0
        frame_ops = {}
        current = []
        
        for ntt, nbody in nested:
            if ntt == 26:
                po = parse_place_object2(nbody)
                current.append(('PO2', po))
            elif ntt == 70:
                po = parse_place_object3(nbody)
                current.append(('PO3', po))
            elif ntt == 28 and len(nbody) >= 2:
                depth = struct.unpack_from('<H', nbody, 0)[0]
                current.append(('REMOVE', {'depth': depth}))
            elif ntt == 43:
                end = nbody.index(0) if 0 in nbody else len(nbody)
                current.append(('LABEL', nbody[:end].decode('utf-8', errors='replace')))
            elif ntt == 1:
                frame_ops[frame] = current
                current = []
                frame += 1
        
        print(f"  Sprite charId={cid}, {fc} frames declared, {frame} ShowFrames")
        for f in range(max(0, around_frame - context), min(frame, around_frame + context + 1)):
            ops = frame_ops.get(f, [])
            print(f"\n  Frame {f+1} (idx {f}): {len(ops)} ops")
            for op_type, op_data in ops:
                if op_type in ('PO2', 'PO3'):
                    d = op_data.get('depth', '?')
                    m = op_data.get('move', False)
                    cid_val = op_data.get('charId')
                    mat = op_data.get('matrix')
                    tx = mat[4] if mat and len(mat) > 4 else '?'
                    ty = mat[5] if mat and len(mat) > 5 else '?'
                    print(f"    {op_type}: depth={d} move={m} charId={cid_val} tx={tx} ty={ty}")
                elif op_type == 'REMOVE':
                    print(f"    REMOVE: depth={op_data['depth']}")
                elif op_type == 'LABEL':
                    print(f"    LABEL: '{op_data}'")


def main():
    with open(SSF_PATH, 'rb') as f: raw = f.read()
    
    # OG
    og_data = decompress_swf(raw)
    offset = get_offset(og_data)
    og_tags = parse_tags(og_data, offset)
    
    # RT
    header, parsed = parse_swf(raw)
    builder = N2DBuilder(header, "fox")
    builder.catalog_swf_tags(parsed)
    builder.frame_scripts = {}
    builder.build_all()
    builder.build_main_timeline(parsed)
    builder._embed_bitmap_data_in_recodes()
    
    n2d_path = os.path.join(tempfile.gettempdir(), "fox_s1140.n2d")
    n2d = builder.to_n2d_json()
    save_n2d(n2d, n2d_path, bitmap_buffers=builder.bitmap_buffers)
    
    rt_path = os.path.join(tempfile.gettempdir(), "fox_s1140_rt.swf")
    shared_dir = os.path.join(os.path.dirname(__file__), "shared")
    from compilation_pipeline import CompilationContext, create_default_pipeline
    ctx = CompilationContext(n2d_path=n2d_path, shared_dir=shared_dir, output_path=rt_path)
    pipeline = create_default_pipeline()
    pipeline.execute(ctx)
    
    with open(rt_path, 'rb') as f: rt_raw = f.read()
    rt_data = decompress_swf(rt_raw)
    rt_offset = get_offset(rt_data)
    rt_tags = parse_tags(rt_data, rt_offset)
    
    # Map OG 1140 to RT
    og_to_n2d = dict(builder.swf_to_n2d)
    n2d_to_rt = dict(ctx.lib_to_swf_id)
    og_to_rt = {}
    for oc, nl in og_to_n2d.items():
        if nl in n2d_to_rt: og_to_rt[oc] = n2d_to_rt[nl]
    
    rt_cid = og_to_rt.get(1140)
    
    print("=" * 80)
    print(f"SPRITE 1140 (fox_specialU_50) DEEP DIVE — RT charId = {rt_cid}")
    print("=" * 80)
    
    # Also check the N2D representation
    n2d_lid = og_to_n2d.get(1140)
    n2d_lib = None
    for lib in builder.libraries:
        if lib.get('id') == n2d_lid:
            n2d_lib = lib
            break
    
    if n2d_lib:
        layers = n2d_lib.get('layers', [])
        print(f"\n  N2D lib {n2d_lid}: {len(layers)} layers, totalFrame={n2d_lib.get('totalFrame')}")
        for li, layer in enumerate(layers):
            depth = layer.get('swfDepth', '?')
            chars = layer.get('characters', [])
            mode = layer.get('mode', 0)
            print(f"    Layer {li} depth={depth} mode={mode}: {len(chars)} characters")
            for ci, ch in enumerate(chars):
                sf = ch.get('startFrame', '?')
                ef = ch.get('endFrame', '?')
                ref = ch.get('libraryId', '?')
                name = ch.get('name', '')
                print(f"      [{ci}] libId={ref} frames={sf}-{ef} name='{name}'")
    
    print(f"\n--- OG sprite 1140 around frame 23 ---")
    dump_sprite_ops(og_tags, 1140, around_frame=22)  # 0-indexed
    
    print(f"\n--- RT sprite {rt_cid} around frame 23 ---")
    dump_sprite_ops(rt_tags, rt_cid, around_frame=22)
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
