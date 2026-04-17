#!/usr/bin/env python3
"""Check the landmaster sprite PO difference AND compare shape binary sizes."""
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
    return stags

def po2_info(body):
    flags = body[0]
    depth = struct.unpack_from('<H', body, 1)[0]
    pos = 3; char = None; move = bool(flags & 1)
    if flags & 0x02 and pos + 2 <= len(body):
        char = struct.unpack_from('<H', body, pos)[0]
    return depth, char, move, flags

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
    n2d_path = os.path.join(tempfile.gettempdir(), "fox_lm.n2d")
    n2d = builder.to_n2d_json()
    save_n2d(n2d, n2d_path, bitmap_buffers=builder.bitmap_buffers)
    rt_path = os.path.join(tempfile.gettempdir(), "fox_lm_rt.swf")
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
    
    og_to_n2d = dict(builder.swf_to_n2d)
    n2d_to_rt = dict(ctx.lib_to_swf_id)
    og_to_rt = {}
    for oc, nl in og_to_n2d.items():
        if nl in n2d_to_rt: og_to_rt[oc] = n2d_to_rt[nl]
    
    # Find landmaster sprite
    # OG cid for fox_fla.fox_landmasterstart_finalform2_142
    og_sym = {}
    for tt, body in og_tags:
        if tt == 76:
            count = struct.unpack_from('<H', body, 0)[0]
            pos = 2
            for _ in range(count):
                cid = struct.unpack_from('<H', body, pos)[0]; pos += 2
                end = body.index(0, pos)
                name = body[pos:end].decode('utf-8','replace'); pos = end + 1
                og_sym[cid] = name
    
    lm_og_cid = None
    for cid, name in og_sym.items():
        if 'landmaster' in name.lower():
            lm_og_cid = cid
            print(f"Found: OG cid={cid} = {name}")

    lm_rt_cid = og_to_rt.get(lm_og_cid)
    print(f"RT cid = {lm_rt_cid}")
    
    # Get sprite bodies
    og_body = rt_body = None
    for tt, body in og_tags:
        if tt == 39 and len(body) >= 4:
            cid = struct.unpack_from('<H', body, 0)[0]
            if cid == lm_og_cid: og_body = body
    for tt, body in rt_tags:
        if tt == 39 and len(body) >= 4:
            cid = struct.unpack_from('<H', body, 0)[0]
            if cid == lm_rt_cid: rt_body = body
    
    if not og_body or not rt_body:
        print("ERROR: sprite not found")
        return
    
    og_stags = parse_sprite_tags(og_body)
    rt_stags = parse_sprite_tags(rt_body)
    
    print(f"\nOG internal tags: {len(og_stags)}")
    print(f"RT internal tags: {len(rt_stags)}")
    
    # Compare tag-by-tag
    from collections import Counter
    og_tc = Counter(tt for tt, _ in og_stags)
    rt_tc = Counter(tt for tt, _ in rt_stags)
    for stt in sorted(set(og_tc) | set(rt_tc)):
        name = TAG_NAMES.get(stt, f'Tag{stt}')
        print(f"  {name}: OG={og_tc.get(stt,0)} RT={rt_tc.get(stt,0)}")
    
    # Dump all PO2s frame by frame for both
    print("\n--- OG Landmaster timeline ---")
    frame = 0
    for stt, sbody in og_stags:
        if stt == 1:
            frame += 1
        elif stt == 43:
            label = sbody[:sbody.index(0)].decode('utf-8','replace') if 0 in sbody else '?'
            print(f"  [F{frame}] Label: '{label}'")
        elif stt == 26:
            d, c, m, f_ = po2_info(sbody)
            child_sym = og_sym.get(c, '') if c else ''
            print(f"  [F{frame}] PO2: depth={d} charId={c} move={m} {child_sym}")
        elif stt == 28:
            d = struct.unpack_from('<H', sbody, 0)[0]
            print(f"  [F{frame}] RO2: depth={d}")
    
    print("\n--- RT Landmaster timeline ---")
    rt_sym = {}
    for tt, body in rt_tags:
        if tt == 76:
            count = struct.unpack_from('<H', body, 0)[0]
            pos = 2
            for _ in range(count):
                cid = struct.unpack_from('<H', body, pos)[0]; pos += 2
                end = body.index(0, pos)
                name = body[pos:end].decode('utf-8','replace'); pos = end + 1
                rt_sym[cid] = name
    
    frame = 0
    for stt, sbody in rt_stags:
        if stt == 1:
            frame += 1
        elif stt == 43:
            label = sbody[:sbody.index(0)].decode('utf-8','replace') if 0 in sbody else '?'
            print(f"  [F{frame}] Label: '{label}'")
        elif stt == 26:
            d, c, m, f_ = po2_info(sbody)
            child_sym = rt_sym.get(c, '') if c else ''
            print(f"  [F{frame}] PO2: depth={d} charId={c} move={m} {child_sym}")
        elif stt == 28:
            d = struct.unpack_from('<H', sbody, 0)[0]
            print(f"  [F{frame}] RO2: depth={d}")

if __name__ == "__main__":
    main()
