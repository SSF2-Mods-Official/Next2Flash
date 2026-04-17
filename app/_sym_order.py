#!/usr/bin/env python3
"""Compare SymbolClass entry ORDER between OG and RT."""
import sys, os, struct, zlib
sys.path.insert(0, os.path.dirname(__file__))
from swf_binary_io import BitReader
from swf_to_n2d import N2DBuilder, parse_swf, save_n2d

SSF_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"

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

def parse_symbol_class_ordered(body):
    """Parse SymbolClass preserving order."""
    if len(body) < 2: return []
    count = struct.unpack_from('<H', body, 0)[0]
    pos = 2; entries = []
    for i in range(count):
        if pos + 2 > len(body): break
        cid = struct.unpack_from('<H', body, pos)[0]; pos += 2
        end = body.index(0, pos) if 0 in body[pos:] else len(body)
        name = body[pos:end].decode('utf-8', errors='replace')
        pos = end + 1
        entries.append((i, cid, name))
    return entries

def main():
    import tempfile
    
    with open(SSF_PATH, 'rb') as f: og_raw = f.read()
    print(f"OG file: {SSF_PATH} ({len(og_raw)} bytes)")
    
    # Build RT
    header, tags = parse_swf(og_raw)
    builder = N2DBuilder(header, "fox")
    builder.catalog_swf_tags(tags)
    builder.frame_scripts = {}
    builder.build_all()
    builder.build_main_timeline(tags)
    builder._embed_bitmap_data_in_recodes()
    n2d_path = os.path.join(tempfile.gettempdir(), "fox_symorder.n2d")
    n2d = builder.to_n2d_json()
    save_n2d(n2d, n2d_path, bitmap_buffers=builder.bitmap_buffers)
    rt_path = os.path.join(tempfile.gettempdir(), "fox_symorder_rt.swf")
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
    
    # Parse SymbolClass from both
    og_sym_entries = []
    rt_sym_entries = []
    for tt, body in og_tags:
        if tt == 76: og_sym_entries = parse_symbol_class_ordered(body)
    for tt, body in rt_tags:
        if tt == 76: rt_sym_entries = parse_symbol_class_ordered(body)
    
    print(f"\n=== OG SymbolClass: {len(og_sym_entries)} entries ===")
    print(f"  First 5:")
    for i, cid, name in og_sym_entries[:5]:
        print(f"    [{i:3d}] charId={cid:5d}  name={name}")
    print(f"  Last 5:")
    for i, cid, name in og_sym_entries[-5:]:
        print(f"    [{i:3d}] charId={cid:5d}  name={name}")
    
    # Find Main position
    og_main_pos = next((i for i, cid, name in og_sym_entries if name == 'Main'), None)
    print(f"  'Main' at position: {og_main_pos}")
    
    print(f"\n=== RT SymbolClass: {len(rt_sym_entries)} entries ===")
    print(f"  First 5:")
    for i, cid, name in rt_sym_entries[:5]:
        print(f"    [{i:3d}] charId={cid:5d}  name={name}")
    print(f"  Last 5:")
    for i, cid, name in rt_sym_entries[-5:]:
        print(f"    [{i:3d}] charId={cid:5d}  name={name}")
    
    rt_main_pos = next((i for i, cid, name in rt_sym_entries if name == 'Main'), None)
    print(f"  'Main' at position: {rt_main_pos}")
    
    # Check if OG order matches RT order
    og_names = [name for _, _, name in og_sym_entries]
    rt_names = [name for _, _, name in rt_sym_entries]
    
    if og_names == rt_names:
        print("\n  ORDER: IDENTICAL!")
    else:
        print(f"\n  ORDER: DIFFERENT!")
        # Show where they diverge
        for i in range(min(len(og_names), len(rt_names))):
            if og_names[i] != rt_names[i]:
                print(f"  First difference at [{i}]: OG='{og_names[i]}' RT='{rt_names[i]}'")
                break
        
        # Show full comparison
        print(f"\n  === FULL OG ORDER ===")
        for i, cid, name in og_sym_entries:
            print(f"    [{i:3d}] cid={cid:5d} {name}")
        print(f"\n  === FULL RT ORDER ===")
        for i, cid, name in rt_sym_entries:
            print(f"    [{i:3d}] cid={cid:5d} {name}")

if __name__ == "__main__":
    main()
