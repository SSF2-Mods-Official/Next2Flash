#!/usr/bin/env python3
"""Check what tags come AFTER SymbolClass in both OG and RT SWFs.
Also check: does the root timeline have definition tags interleaved?
This is critical for AVM2 initialization."""
import sys, os, struct, zlib
sys.path.insert(0, os.path.dirname(__file__))
from swf_binary_io import BitReader
from swf_to_n2d import N2DBuilder, parse_swf, save_n2d
import tempfile

SSF_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\fox.ssf"

TAG_NAMES = {0:'End', 1:'ShowFrame', 4:'PlaceObject', 9:'SetBgColor', 
             22:'DefShape2', 26:'PO2', 28:'RO2', 32:'DefShape3',
             36:'DefBitsLL2', 39:'DefSprite', 43:'FrameLabel',
             69:'FileAttrib', 70:'PO3', 73:'DefineFontAlignZones',
             75:'DefFont3', 76:'SymbolClass', 82:'DoABC', 
             83:'DefShape4', 84:'DefMorph2', 86:'SceneLabel',
             87:'DefineBinaryData', 88:'DefineFontName',
             14:'DefSound', 15:'StartSound', 35:'DefBitsJPEG3',
             2:'DefShape', 11:'DefText', 37:'DefEditText',
             56:'ExportAssets', 20:'DefBitsLL', 21:'DefBitsJPEG2',
             48:'DefFont2'}

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

def parse_symbol_class(body):
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

def dump_tag_stream(tags, label, start=0, end=None):
    if end is None: end = len(tags)
    print(f"\n  === {label} tags [{start}..{end-1}] ===")
    for i in range(start, min(end, len(tags))):
        tt, body = tags[i]
        name = TAG_NAMES.get(tt, f'Tag{tt}')
        extra = ""
        if tt == 39 and len(body) >= 4:
            cid, fc = struct.unpack_from('<HH', body, 0)
            extra = f" (cid={cid}, {fc} frames)"
        elif tt in (32, 83, 22, 2, 84) and len(body) >= 2:
            cid = struct.unpack_from('<H', body, 0)[0]
            extra = f" (cid={cid}, {len(body)} bytes)"
        elif tt in (36, 35, 20, 21) and len(body) >= 2:
            cid = struct.unpack_from('<H', body, 0)[0]
            extra = f" (cid={cid}, {len(body)} bytes)"
        elif tt == 76:
            syms = parse_symbol_class(body)
            extra = f" ({len(syms)} entries)"
        elif tt == 82:
            extra = f" ({len(body)} bytes)"
        elif tt == 75 and len(body) >= 2:
            cid = struct.unpack_from('<H', body, 0)[0]
            extra = f" (cid={cid})"
        elif tt == 73 and len(body) >= 2:
            cid = struct.unpack_from('<H', body, 0)[0]
            extra = f" (font cid={cid})"
        elif tt == 88 and len(body) >= 2:
            cid = struct.unpack_from('<H', body, 0)[0]
            extra = f" (font cid={cid})"
        elif tt == 14 and len(body) >= 2:
            cid = struct.unpack_from('<H', body, 0)[0]
            extra = f" (cid={cid})"
        elif tt == 26 and len(body) >= 3:
            flags = body[0]
            depth = struct.unpack_from('<H', body, 1)[0]
            pos = 3; char = None
            if flags & 0x02 and pos+2 <= len(body):
                char = struct.unpack_from('<H', body, pos)[0]
            extra = f" (depth={depth}, charId={char}, move={bool(flags&1)})"
        elif tt == 28 and len(body) >= 2:
            depth = struct.unpack_from('<H', body, 0)[0]
            extra = f" (depth={depth})"
        elif tt == 43:
            end_str = body.index(0) if 0 in body else len(body)
            extra = f" ('{body[:end_str].decode('utf-8', errors='replace')}')"
        print(f"    [{i:4d}] {name}{extra}")


def main():
    with open(SSF_PATH, 'rb') as f: raw = f.read()
    
    # Build RT
    header, tags = parse_swf(raw)
    builder = N2DBuilder(header, "fox")
    builder.catalog_swf_tags(tags)
    builder.frame_scripts = {}
    builder.build_all()
    builder.build_main_timeline(tags)
    builder._embed_bitmap_data_in_recodes()
    n2d_path = os.path.join(tempfile.gettempdir(), "fox_order.n2d")
    n2d = builder.to_n2d_json()
    save_n2d(n2d, n2d_path, bitmap_buffers=builder.bitmap_buffers)
    rt_path = os.path.join(tempfile.gettempdir(), "fox_order_rt.swf")
    shared_dir = os.path.join(os.path.dirname(__file__), 'shared')
    from compilation_pipeline import CompilationContext, create_default_pipeline
    ctx = CompilationContext(n2d_path=n2d_path, shared_dir=shared_dir, output_path=rt_path)
    pipeline = create_default_pipeline()
    pipeline.execute(ctx)
    with open(rt_path, 'rb') as f: rt_raw = f.read()
    
    og_data = decompress_swf(raw)
    og_tags = parse_tags_raw(og_data, get_offset(og_data))
    rt_data = decompress_swf(rt_raw)
    rt_tags = parse_tags_raw(rt_data, get_offset(rt_data))
    
    print("=" * 80)
    print("TAG ORDERING ANALYSIS: ROOT TIMELINE STRUCTURE")
    print("=" * 80)
    
    # Find SymbolClass position and show everything from there to end
    og_sym_pos = next(i for i, (tt, _) in enumerate(og_tags) if tt == 76)
    rt_sym_pos = next(i for i, (tt, _) in enumerate(rt_tags) if tt == 76)
    
    # Show from first definition block start through the end
    # In OG, show the root timeline section  
    print("\n--- OG: Root timeline (tags around and after DoABC/SymbolClass) ---")
    # Show from a few tags before first root PO2/ShowFrame
    dump_tag_stream(og_tags, "OG full", max(0, og_sym_pos - 5), len(og_tags))
    
    print("\n--- RT: Root timeline (tags around and after DoABC/SymbolClass) ---")
    dump_tag_stream(rt_tags, "RT full", max(0, rt_sym_pos - 5), len(rt_tags))
    
    # Also show the FIRST few tags to compare file structure
    print("\n--- OG: First 20 tags ---")
    dump_tag_stream(og_tags, "OG start", 0, 20)
    print("\n--- RT: First 20 tags ---")
    dump_tag_stream(rt_tags, "RT start", 0, 20)
    
    # Check: are root timeline PO tags placing the same charIDs?
    print("\n--- Root timeline PO charId comparison ---")
    og_to_n2d = dict(builder.swf_to_n2d)
    n2d_to_rt = dict(ctx.lib_to_swf_id)
    og_to_rt = {}
    for oc, nl in og_to_n2d.items():
        if nl in n2d_to_rt: og_to_rt[oc] = n2d_to_rt[nl]
    
    # Collect root PO tags (outside sprites)
    og_root_po = [(i, tt, body) for i, (tt, body) in enumerate(og_tags) if tt in (26, 70)]
    rt_root_po = [(i, tt, body) for i, (tt, body) in enumerate(rt_tags) if tt in (26, 70)]
    
    print(f"  OG root PO tags: {len(og_root_po)}")
    print(f"  RT root PO tags: {len(rt_root_po)}")
    
    for idx, (pos, tt, body) in enumerate(og_root_po[:30]):
        flags = body[0]
        depth = struct.unpack_from('<H', body, 1)[0]
        p = 3; char = None
        if flags & 0x02 and p+2 <= len(body):
            char = struct.unpack_from('<H', body, p)[0]
        expected_rt = og_to_rt.get(char) if char else None
        
        # Find corresponding RT PO
        if idx < len(rt_root_po):
            rpos, rtt, rbody = rt_root_po[idx]
            rflags = rbody[0]
            rdepth = struct.unpack_from('<H', rbody, 1)[0]
            rp = 3; rchar = None
            if rflags & 0x02 and rp+2 <= len(rbody):
                rchar = struct.unpack_from('<H', rbody, rp)[0]
            
            match = "OK" if expected_rt == rchar else f"MISMATCH (expected {expected_rt})"
            if depth != rdepth:
                match += f" DEPTH_DIFF(OG={depth} RT={rdepth})"
            print(f"  PO[{idx}] OG: d={depth} cid={char} | RT: d={rdepth} cid={rchar} | {match}")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
