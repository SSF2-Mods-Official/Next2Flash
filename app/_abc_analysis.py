#!/usr/bin/env python3
"""
Investigate AS3 symbol binding: compare ABC class names with SymbolClass entries.
Check:
1. Does SymbolClass provide all symbols that ABC references?
2. Are SymbolClass entries in the right position in the SWF tag stream?
3. Are there class names in ABC that don't appear in SymbolClass?
4. Compare OG vs RT tag ordering.
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

def extract_abc_strings(abc_body):
    """Extract string constants from DoABC tag body.
    
    DoABC tag format: flags(UI32) + name(NULL-terminated) + ABC bytecode
    ABC bytecode starts with: minor_version(UI16) + major_version(UI16)
    then constant pool: int_count, uint_count, double_count, string_count...
    """
    # Skip DoABC header (flags + null-terminated name)
    if len(abc_body) < 4: return []
    pos = 4  # skip flags
    # Skip name (null-terminated string)
    while pos < len(abc_body) and abc_body[pos] != 0:
        pos += 1
    pos += 1  # skip null terminator
    
    # Now at ABC bytecode
    if pos + 4 > len(abc_body): return []
    minor = struct.unpack_from('<H', abc_body, pos)[0]; pos += 2
    major = struct.unpack_from('<H', abc_body, pos)[0]; pos += 2
    
    # Read integer constant pool (skip)
    int_count, pos = read_u30(abc_body, pos)
    for _ in range(max(0, int_count - 1)):
        _, pos = read_s32(abc_body, pos)
    
    # Read uint constant pool (skip)
    uint_count, pos = read_u30(abc_body, pos)
    for _ in range(max(0, uint_count - 1)):
        _, pos = read_u30(abc_body, pos)
    
    # Read double constant pool (skip)
    double_count, pos = read_u30(abc_body, pos)
    pos += max(0, double_count - 1) * 8
    
    # Read string constant pool (THIS IS WHAT WE WANT)
    string_count, pos = read_u30(abc_body, pos)
    strings = ['']  # index 0 is empty string
    for _ in range(max(0, string_count - 1)):
        slen, pos = read_u30(abc_body, pos)
        s = abc_body[pos:pos+slen].decode('utf-8', errors='replace')
        strings.append(s)
        pos += slen
    
    return strings

def read_u30(data, pos):
    """Read variable-length encoded U30 from ABC bytecode."""
    result = 0
    shift = 0
    for i in range(5):
        if pos >= len(data): return result, pos
        b = data[pos]; pos += 1
        result |= (b & 0x7F) << shift
        shift += 7
        if not (b & 0x80):
            break
    return result, pos

def read_s32(data, pos):
    """Read variable-length encoded S32 from ABC bytecode."""
    result = 0
    shift = 0
    for i in range(5):
        if pos >= len(data): return result, pos
        b = data[pos]; pos += 1
        result |= (b & 0x7F) << shift
        shift += 7
        if not (b & 0x80):
            break
    # Sign extend
    if shift < 32 and (result & (1 << (shift - 1))):
        result |= -(1 << shift)
    return result, pos


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
    
    n2d_path = os.path.join(tempfile.gettempdir(), "fox_abc.n2d")
    n2d = builder.to_n2d_json()
    save_n2d(n2d, n2d_path, bitmap_buffers=builder.bitmap_buffers)
    
    rt_path = os.path.join(tempfile.gettempdir(), "fox_abc_rt.swf")
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
    print("AS3 SYMBOL BINDING ANALYSIS")
    print("=" * 80)
    
    # === 1. SymbolClass comparison ===
    print("\n--- 1. SymbolClass ---")
    og_symbols = {}
    rt_symbols = {}
    for tt, body in og_tags:
        if tt == 76: og_symbols.update(parse_symbol_class(body))
    for tt, body in rt_tags:
        if tt == 76: rt_symbols.update(parse_symbol_class(body))
    
    og_names = set(og_symbols.values())
    rt_names = set(rt_symbols.values())
    
    print(f"  OG: {len(og_symbols)} entries ({len(og_names)} unique names)")
    print(f"  RT: {len(rt_symbols)} entries ({len(rt_names)} unique names)")
    
    missing_names = og_names - rt_names
    extra_names = rt_names - og_names
    if missing_names:
        print(f"  MISSING from RT: {len(missing_names)}")
        for n in sorted(missing_names)[:20]:
            print(f"    '{n}'")
    if extra_names:
        print(f"  EXTRA in RT: {len(extra_names)}")
        for n in sorted(extra_names)[:20]:
            print(f"    '{n}'")
    if not missing_names and not extra_names:
        print("  Names match perfectly!")
    
    # === 2. Tag ordering comparison ===
    print("\n--- 2. Tag ordering (SymbolClass position) ---")
    TAG_NAMES = {0:'End', 1:'ShowFrame', 9:'SetBgColor', 26:'PO2', 28:'RO2', 
                 32:'DefShape3', 36:'DefBitsLL2', 39:'DefSprite', 43:'FrameLabel',
                 69:'FileAttrib', 70:'PO3', 75:'DefFont3', 76:'SymbolClass',
                 82:'DoABC', 83:'DefShape4', 84:'DefMorph2', 86:'SceneLabel',
                 88:'DefFontName', 14:'DefSound', 35:'DefBitsJPEG3'}
    
    def tag_summary(tags_list, label):
        print(f"\n  {label} tag stream (high-level):")
        # Show positions of key tags
        sym_positions = []
        abc_positions = []
        last_def_position = -1
        for i, (tt, body) in enumerate(tags_list):
            if tt == 76:
                sym_positions.append(i)
            elif tt == 82:
                abc_positions.append(i)
            elif tt in (39, 32, 83, 36, 84, 35, 14, 75):
                last_def_position = i
        
        print(f"    SymbolClass at position(s): {sym_positions}")
        print(f"    DoABC at position(s): {abc_positions}")
        print(f"    Last definition tag at position: {last_def_position}")
        print(f"    Total tags: {len(tags_list)}")
        
        # Show a window around SymbolClass
        for sp in sym_positions:
            print(f"\n    Tags around SymbolClass (pos {sp}):")
            for j in range(max(0, sp-3), min(len(tags_list), sp+4)):
                tt2, body2 = tags_list[j]
                name = TAG_NAMES.get(tt2, f'Tag{tt2}')
                extra = ""
                if tt2 == 39 and len(body2) >= 4:
                    cid, fc = struct.unpack_from('<HH', body2, 0)
                    extra = f" (cid={cid}, {fc}f)"
                elif tt2 == 76:
                    syms = parse_symbol_class(body2)
                    extra = f" ({len(syms)} entries)"
                elif tt2 == 82:
                    extra = f" ({len(body2)} bytes)"
                marker = " <<<" if j == sp else ""
                print(f"      [{j}] {name}{extra}{marker}")
    
    tag_summary(og_tags, "OG")
    tag_summary(rt_tags, "RT")
    
    # === 3. ABC string analysis ===
    print("\n--- 3. ABC class references ---")
    og_abc_body = None
    rt_abc_body = None
    for tt, body in og_tags:
        if tt == 82: og_abc_body = body; break
    for tt, body in rt_tags:
        if tt == 82: rt_abc_body = body; break
    
    if og_abc_body:
        og_strings = extract_abc_strings(og_abc_body)
        print(f"  ABC string pool: {len(og_strings)} strings")
        
        # Find strings that look like symbol class names
        symbol_like = [s for s in og_strings if s.startswith('symbol') or 
                       s.startswith('fox_') or s.startswith('Fox')]
        print(f"  Symbol-like strings in ABC: {len(symbol_like)}")
        for s in sorted(symbol_like)[:30]:
            in_og_sym = s in og_names
            in_rt_sym = s in rt_names
            status = "OK" if in_og_sym and in_rt_sym else ("MISSING" if in_og_sym and not in_rt_sym else "NOT_IN_SYM")
            print(f"    '{s}' — {status}")
    
    # === 4. Check if symbol names are class-name-compatible ===
    print("\n--- 4. Full SymbolClass name list (OG) ---")
    for cid in sorted(og_symbols.keys()):
        name = og_symbols[cid]
        rt_has = name in rt_names
        print(f"  charId={cid:5d} → '{name}'" + ("" if rt_has else " *** MISSING IN RT"))
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
