#!/usr/bin/env python3
"""Compare ALL tag types between OG and RT SWFs.
Check for missing tags, header differences, DefineBinaryData, ExportAssets, etc."""
import sys, os, struct, zlib
sys.path.insert(0, os.path.dirname(__file__))
from swf_binary_io import BitReader
from swf_to_n2d import N2DBuilder, parse_swf, save_n2d

SSF_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\fox.ssf"

TAG_NAMES = {0:'End', 1:'ShowFrame', 2:'DefShape', 4:'PlaceObject', 5:'RemoveObject',
             6:'DefineBitsJPEG', 9:'SetBgColor', 10:'DefineFont', 11:'DefText',
             14:'DefSound', 15:'StartSound', 18:'SoundStreamHead', 19:'SoundStreamBlock',
             20:'DefBitsLL', 21:'DefBitsJPEG2', 22:'DefShape2', 24:'Protect',
             26:'PO2', 28:'RO2', 32:'DefShape3', 35:'DefBitsJPEG3', 36:'DefBitsLL2',
             37:'DefEditText', 39:'DefSprite', 43:'FrameLabel', 45:'SoundStreamHead2',
             46:'DefineMorphShape', 48:'DefFont2', 56:'ExportAssets',
             69:'FileAttrib', 70:'PO3', 73:'DefineFontAlignZones',
             75:'DefFont3', 76:'SymbolClass', 77:'Metadata', 82:'DoABC', 83:'DefShape4',
             84:'DefMorph2', 86:'SceneLabel', 87:'DefineBinaryData', 88:'DefineFontName',
             89:'StartSound2', 91:'DefBitsJPEG4'}

def decompress_swf(raw):
    sig = raw[:3]
    if sig == b'CWS': return raw[:8] + zlib.decompress(raw[8:])
    return raw

def get_offset(data):
    br = BitReader(data, 8)
    nb = br.read_ub(5)
    for _ in range(4): br.read_sb(nb)
    br.align()
    return br.byte_pos + 4  # +4 for frame rate + frame count

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

def parse_header(data):
    """Parse SWF header fields"""
    sig = data[:3].decode('ascii', errors='replace')
    version = data[3]
    file_len = struct.unpack_from('<I', data, 4)[0]
    
    br = BitReader(data, 8)
    nb = br.read_ub(5)
    xmin = br.read_sb(nb)
    xmax = br.read_sb(nb)
    ymin = br.read_sb(nb)
    ymax = br.read_sb(nb)
    br.align()
    
    # After RECT: frame rate (fixed 8.8) and frame count
    pos = br.byte_pos
    frame_rate_raw = struct.unpack_from('<H', data, pos)[0]
    frame_rate = frame_rate_raw / 256.0
    frame_count = struct.unpack_from('<H', data, pos + 2)[0]
    
    return {
        'sig': sig, 'version': version, 'file_len': file_len,
        'rect': (xmin, xmax, ymin, ymax),
        'frame_rate': frame_rate, 'frame_count': frame_count
    }

def main():
    import tempfile
    
    with open(SSF_PATH, 'rb') as f: og_raw = f.read()
    
    # Build RT
    header, tags = parse_swf(og_raw)
    builder = N2DBuilder(header, "fox")
    builder.catalog_swf_tags(tags)
    builder.frame_scripts = {}
    builder.build_all()
    builder.build_main_timeline(tags)
    builder._embed_bitmap_data_in_recodes()
    n2d_path = os.path.join(tempfile.gettempdir(), "fox_header.n2d")
    n2d = builder.to_n2d_json()
    save_n2d(n2d, n2d_path, bitmap_buffers=builder.bitmap_buffers)
    rt_path = os.path.join(tempfile.gettempdir(), "fox_header_rt.swf")
    shared_dir = os.path.join(os.path.dirname(__file__), 'shared')
    from compilation_pipeline import CompilationContext, create_default_pipeline
    ctx = CompilationContext(n2d_path=n2d_path, shared_dir=shared_dir, output_path=rt_path)
    pipeline = create_default_pipeline()
    pipeline.execute(ctx)
    with open(rt_path, 'rb') as f: rt_raw = f.read()
    
    og_data = decompress_swf(og_raw)
    rt_data = decompress_swf(rt_raw)
    
    print("=" * 80)
    print("COMPREHENSIVE SWF COMPARISON")
    print("=" * 80)
    
    # 1. Header comparison
    og_hdr = parse_header(og_data)
    rt_hdr = parse_header(rt_data)
    print("\n--- SWF HEADER ---")
    for key in og_hdr:
        match = "OK" if og_hdr[key] == rt_hdr[key] else "MISMATCH!"
        print(f"  {key:15s}: OG={og_hdr[key]}  RT={rt_hdr[key]}  [{match}]")
    
    # 2. Tag type census
    og_tags = parse_tags_raw(og_data, get_offset(og_data))
    rt_tags = parse_tags_raw(rt_data, get_offset(rt_data))
    
    from collections import Counter
    og_counts = Counter(tt for tt, _ in og_tags)
    rt_counts = Counter(tt for tt, _ in rt_tags)
    
    all_types = sorted(set(og_counts) | set(rt_counts))
    print(f"\n--- TAG TYPE CENSUS (OG: {len(og_tags)} tags, RT: {len(rt_tags)} tags) ---")
    for tt in all_types:
        oc, rc = og_counts.get(tt, 0), rt_counts.get(tt, 0)
        name = TAG_NAMES.get(tt, f'Tag{tt}')
        status = "OK" if oc == rc else "DIFF!"
        print(f"  {name:25s} (type {tt:3d}): OG={oc:5d}  RT={rc:5d}  [{status}]")
    
    # 3. Check for DefineBinaryData
    og_bdata = [(i, body) for i, (tt, body) in enumerate(og_tags) if tt == 87]
    rt_bdata = [(i, body) for i, (tt, body) in enumerate(rt_tags) if tt == 87]
    print(f"\n--- DefineBinaryData ---")
    print(f"  OG: {len(og_bdata)} tags")
    print(f"  RT: {len(rt_bdata)} tags")
    for pos, body in og_bdata[:10]:
        cid = struct.unpack_from('<H', body, 0)[0] if len(body) >= 2 else '?'
        print(f"    OG [{pos}] cid={cid}, {len(body)} bytes")
    for pos, body in rt_bdata[:10]:
        cid = struct.unpack_from('<H', body, 0)[0] if len(body) >= 2 else '?'
        print(f"    RT [{pos}] cid={cid}, {len(body)} bytes")
    
    # 4. ExportAssets check
    og_export = [(i, body) for i, (tt, body) in enumerate(og_tags) if tt == 56]
    rt_export = [(i, body) for i, (tt, body) in enumerate(rt_tags) if tt == 56]
    print(f"\n--- ExportAssets ---")
    print(f"  OG: {len(og_export)} tags")
    print(f"  RT: {len(rt_export)} tags")
    
    # 5. Check SWF compression type
    print(f"\n--- Compression ---")
    print(f"  OG: {og_raw[:3]} ({len(og_raw)} bytes compressed, {len(og_data)} decompressed)")
    print(f"  RT: {rt_raw[:3]} ({len(rt_raw)} bytes compressed, {len(rt_data)} decompressed)")
    
    # 6. Check all sprite (DefSprite) frame counts
    from collections import defaultdict
    og_sprite_frames = {}
    rt_sprite_frames = {}
    for i, (tt, body) in enumerate(og_tags):
        if tt == 39 and len(body) >= 4:
            cid, fc = struct.unpack_from('<HH', body, 0)
            og_sprite_frames[cid] = fc
    for i, (tt, body) in enumerate(rt_tags):
        if tt == 39 and len(body) >= 4:
            cid, fc = struct.unpack_from('<HH', body, 0)
            rt_sprite_frames[cid] = fc
    
    # Map OG sprite CIDs to RT CIDs via the mapping
    og_to_n2d = dict(builder.swf_to_n2d)
    n2d_to_rt = dict(ctx.lib_to_swf_id)
    
    print(f"\n--- Sprite Frame Count Comparison ---")
    frame_mismatches = 0
    for og_cid, og_fc in sorted(og_sprite_frames.items()):
        n2d_id = og_to_n2d.get(og_cid)
        if n2d_id is None: continue
        rt_cid = n2d_to_rt.get(n2d_id)
        if rt_cid is None: continue
        rt_fc = rt_sprite_frames.get(rt_cid)
        if rt_fc is None: continue
        if og_fc != rt_fc:
            frame_mismatches += 1
            print(f"  MISMATCH: OG cid={og_cid}({og_fc}fr) -> RT cid={rt_cid}({rt_fc}fr)")
    if frame_mismatches == 0:
        print(f"  All {len(og_sprite_frames)} sprites match frame counts!")
    else:
        print(f"  {frame_mismatches} mismatches out of {len(og_sprite_frames)} sprites")
    
    # 7. Check sprite internal tag structures for the main fox sprite
    # Find the fox sprite (charId 843 in OG = SymbolClass "fox")
    print(f"\n--- Fox Main Sprite (SymbolClass 'fox') Internal Structure ---")
    # Get the DefSprite body for charId 843
    fox_og_body = None
    for tt, body in og_tags:
        if tt == 39 and len(body) >= 4:
            cid = struct.unpack_from('<H', body, 0)[0]
            if cid == 843:
                fox_og_body = body
                break
    
    fox_rt_cid = n2d_to_rt.get(og_to_n2d.get(843))
    fox_rt_body = None
    for tt, body in rt_tags:
        if tt == 39 and len(body) >= 4:
            cid = struct.unpack_from('<H', body, 0)[0]
            if cid == fox_rt_cid:
                fox_rt_body = body
                break
    
    if fox_og_body and fox_rt_body:
        print(f"  OG fox: cid=843, body={len(fox_og_body)} bytes")
        print(f"  RT fox: cid={fox_rt_cid}, body={len(fox_rt_body)} bytes")
        
        # Parse internal tags
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
        
        og_fc, og_stags = parse_sprite_tags(fox_og_body)
        rt_fc, rt_stags = parse_sprite_tags(fox_rt_body)
        
        print(f"  OG frames: {og_fc}, internal tags: {len(og_stags)}")
        print(f"  RT frames: {rt_fc}, internal tags: {len(rt_stags)}")
        
        # Count internal tag types
        og_sc = Counter(tt for tt, _ in og_stags)
        rt_sc = Counter(tt for tt, _ in rt_stags)
        for stt in sorted(set(og_sc) | set(rt_sc)):
            name = TAG_NAMES.get(stt, f'Tag{stt}')
            oi, ri = og_sc.get(stt, 0), rt_sc.get(stt, 0)
            status = "OK" if oi == ri else "DIFF!"
            print(f"    {name:20s}: OG={oi:3d}  RT={ri:3d}  [{status}]")
        
        # Check first few ShowFrame positions
        og_sfs = [i for i, (tt, _) in enumerate(og_stags) if tt == 1]
        rt_sfs = [i for i, (tt, _) in enumerate(rt_stags) if tt == 1]
        print(f"  OG ShowFrame positions: {og_sfs[:10]}...")
        print(f"  RT ShowFrame positions: {rt_sfs[:10]}...")
        
        # Check frame labels
        og_labels = [(i, body[:body.index(0)].decode('utf-8','replace') if 0 in body else '<no-null>') 
                     for i, (tt, body) in enumerate(og_stags) if tt == 43]
        rt_labels = [(i, body[:body.index(0)].decode('utf-8','replace') if 0 in body else '<no-null>') 
                     for i, (tt, body) in enumerate(rt_stags) if tt == 43]
        print(f"  OG labels ({len(og_labels)}): {og_labels[:10]}")
        print(f"  RT labels ({len(rt_labels)}): {rt_labels[:10]}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
