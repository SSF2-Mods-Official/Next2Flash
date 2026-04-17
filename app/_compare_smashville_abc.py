"""Check DoABC and smashville_bg content details."""
import sys, os, struct, zlib
sys.path.insert(0, os.path.dirname(__file__))
from swf_binary_io import BitReader

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\stage\smashville.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\stage\smashville.ssf"

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
    tags = []
    while offset < len(data):
        if offset + 2 > len(data): break
        tag_code_and_length = struct.unpack_from('<H', data, offset)[0]
        tag_type = tag_code_and_length >> 6
        tag_length = tag_code_and_length & 0x3F
        offset += 2
        if tag_length == 0x3F:
            if offset + 4 > len(data): break
            tag_length = struct.unpack_from('<I', data, offset)[0]
            offset += 4
        tag_data = data[offset:offset + tag_length]
        tags.append((tag_type, tag_data))
        offset += tag_length
        if tag_type == 0: break
    return tags

def parse_symbol_class(tag_data):
    result = {}
    off = 0
    count = struct.unpack_from('<H', tag_data, off)[0]
    off += 2
    for _ in range(count):
        cid = struct.unpack_from('<H', tag_data, off)[0]
        off += 2
        end = tag_data.index(0, off)
        name = tag_data[off:end].decode('utf-8', errors='replace')
        off = end + 1
        result[cid] = name
    return result

def load_swf(path):
    with open(path, 'rb') as f:
        raw = f.read()
    data = decompress_swf(raw)
    offset = get_offset(data)
    tags = parse_tags(data, offset)
    symbols = {}
    for tt, td in tags:
        if tt == 76:
            symbols.update(parse_symbol_class(td))
    return data, tags, symbols

print("Loading...")
og_data, og_tags, og_symbols = load_swf(OG)
rt_data, rt_tags, rt_symbols = load_swf(RT)

# 1. Compare DoABC
print("\n=== DoABC COMPARISON ===")
og_abc = None
rt_abc = None
for tt, td in og_tags:
    if tt == 82: og_abc = td
for tt, td in rt_tags:
    if tt == 82: rt_abc = td

if og_abc and rt_abc:
    print(f"OG DoABC: {len(og_abc)} bytes")
    print(f"RT DoABC: {len(rt_abc)} bytes")
    if og_abc == rt_abc:
        print("DoABC: IDENTICAL ✓")
    else:
        print("DoABC: DIFFERENT ✗")
        # Find first difference
        for i in range(min(len(og_abc), len(rt_abc))):
            if og_abc[i] != rt_abc[i]:
                print(f"  First diff at byte {i}: OG=0x{og_abc[i]:02x} RT=0x{rt_abc[i]:02x}")
                print(f"  OG context: {og_abc[max(0,i-8):i+8].hex()}")
                print(f"  RT context: {rt_abc[max(0,i-8):i+8].hex()}")
                break

# 2. Check DefineSceneAndFrameLabelData
print("\n=== DefineSceneAndFrameLabelData ===")
og_scene = None
rt_scene = None
for tt, td in og_tags:
    if tt == 86: og_scene = td
for tt, td in rt_tags:
    if tt == 86: rt_scene = td
if og_scene and rt_scene:
    if og_scene == rt_scene:
        print("SceneLabel: IDENTICAL ✓")
    else:
        print(f"SceneLabel: DIFFERENT ✗ (OG: {len(og_scene)}B, RT: {len(rt_scene)}B)")

# 3. Compare smashville_bg content frame by frame (charId → shape/bitmap type)
print("\n=== smashville_bg: Placed charIds per frame ===")
og_sym_to_cid = {v: k for k, v in og_symbols.items()}
rt_sym_to_cid = {v: k for k, v in rt_symbols.items()}

# Build char_id → tag_type map for all definitions
def get_def_types(tags):
    """Map charId → tag type for all definition tags."""
    defs = {}
    for tt, td in tags:
        if tt in (2, 22, 32, 36, 37, 46, 83, 84, 20, 21, 6, 14, 24):  # DefineShape variants, bitmaps, etc
            if len(td) >= 2:
                cid = struct.unpack_from('<H', td, 0)[0]
                defs[cid] = tt
        elif tt == 39:  # DefineSprite
            if len(td) >= 2:
                cid = struct.unpack_from('<H', td, 0)[0]
                defs[cid] = 39
    return defs

og_defs = get_def_types(og_tags)
rt_defs = get_def_types(rt_tags)

def dump_sprite_frames(label, tags, symbols, defs, sprite_cid):
    """Dump frame-by-frame content of a sprite."""
    inner = None
    for tt, td in tags:
        if tt == 39:
            cid = struct.unpack_from('<H', td, 0)[0]
            if cid == sprite_cid:
                inner = parse_tags(td, 4)
                break
    if not inner:
        print(f"  {label}: sprite cid={sprite_cid} NOT FOUND")
        return
    
    frame = 0
    display = {}  # depth → (char_id, name)
    
    TAG_TYPE_NAMES = {2:'Shape', 22:'ShapeWithStyle', 32:'Shape3', 36:'BitsLossless2', 
                      37:'EditText', 39:'Sprite', 20:'BitsLossless', 21:'BitsJPEG', 
                      46:'MorphShape2', 83:'DefFontName', 6:'DefineBits', 14:'Sound', 24:'DefFont'}
    
    for tt, td in inner:
        if tt == 1:  # ShowFrame
            frame += 1
        elif tt == 28:  # RemoveObject2
            depth = struct.unpack_from('<H', td, 0)[0]
            display.pop(depth, None)
        elif tt == 26:  # PO2
            flags = td[0]
            depth = struct.unpack_from('<H', td, 1)[0]
            cid = None
            if flags & 0x02:
                cid = struct.unpack_from('<H', td, 3)[0]
            name = None
            # Parse name is complex — skip for now, just track char_id
            if cid is not None:
                sym = symbols.get(cid, f"def:{TAG_TYPE_NAMES.get(defs.get(cid, 0), f'tag{defs.get(cid, 0)}')}#{cid}")
                display[depth] = (cid, sym)
        elif tt == 70:  # PO3
            flags_w = struct.unpack_from('<H', td, 0)[0]
            depth = struct.unpack_from('<H', td, 2)[0]
            cid = None
            off = 4
            if flags_w & 0x800:  # className
                end = td.index(0, off)
                off = end + 1
            if flags_w & 0x02:
                cid = struct.unpack_from('<H', td, off)[0]
            if cid is not None:
                sym = symbols.get(cid, f"def:{TAG_TYPE_NAMES.get(defs.get(cid, 0), f'tag{defs.get(cid, 0)}')}#{cid}")
                display[depth] = (cid, sym)
        elif tt == 43:  # FrameLabel
            end = td.index(0)
            lbl = td[:end].decode('utf-8', errors='replace')
            print(f"  {label} frame {frame+1} [{lbl}]:")
            # Print current display list
            for d in sorted(display.keys()):
                cid, sym = display[d]
                print(f"    depth {d}: {sym}")

# smashville_bg
og_bg_cid = og_sym_to_cid.get('smashville_bg')
rt_bg_cid = rt_sym_to_cid.get('smashville_bg')
print(f"\nOG smashville_bg (cid={og_bg_cid}):")
dump_sprite_frames("OG", og_tags, og_symbols, og_defs, og_bg_cid)
print(f"\nRT smashville_bg (cid={rt_bg_cid}):")
dump_sprite_frames("RT", rt_tags, rt_symbols, rt_defs, rt_bg_cid)

# 4. Check SymbolClass order — is it different?
print("\n=== SymbolClass ORDER ===")
def get_symbol_order(tags):
    for tt, td in tags:
        if tt == 76:
            result = []
            off = 0
            count = struct.unpack_from('<H', td, off)[0]
            off += 2
            for _ in range(count):
                cid = struct.unpack_from('<H', td, off)[0]
                off += 2
                end = td.index(0, off)
                name = td[off:end].decode('utf-8', errors='replace')
                off = end + 1
                result.append((cid, name))
            return result
    return []

og_order = get_symbol_order(og_tags)
rt_order = get_symbol_order(rt_tags)
print(f"OG: {len(og_order)} entries, RT: {len(rt_order)} entries")
# Compare class name order
og_names = [n for _, n in og_order]
rt_names = [n for _, n in rt_order]
if og_names == rt_names:
    print("SymbolClass order: IDENTICAL ✓")
else:
    print("SymbolClass order: DIFFERENT ✗")
    for i, (og_n, rt_n) in enumerate(zip(og_names, rt_names)):
        if og_n != rt_n:
            print(f"  First diff at index {i}: OG={og_n} RT={rt_n}")
            break

# 5. Check if FileAttributes differ
print("\n=== FileAttributes ===")
og_fa = None
rt_fa = None
for tt, td in og_tags:
    if tt == 69: og_fa = td
for tt, td in rt_tags:
    if tt == 69: rt_fa = td
if og_fa and rt_fa:
    if og_fa == rt_fa:
        print("FileAttributes: IDENTICAL ✓")
    else:
        print(f"FileAttributes: DIFFERENT ✗")
        print(f"  OG: {og_fa.hex()}")
        print(f"  RT: {rt_fa.hex()}")
