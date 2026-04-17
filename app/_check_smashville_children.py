"""Check stage_smashville children and their instance names in detail."""
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

def parse_po_name(tag_type, tag_data):
    """Extract depth, char_id, instance name from PlaceObject2/3."""
    if tag_type == 26:  # PO2
        flags = tag_data[0]
        depth = struct.unpack_from('<H', tag_data, 1)[0]
        off = 3
        cid = None
        if flags & 0x02:
            cid = struct.unpack_from('<H', tag_data, off)[0]
            off += 2
        if flags & 0x04:  # matrix
            br = BitReader(tag_data, off)
            if br.read_ub(1): nb = br.read_ub(5); br.read_sb(nb); br.read_sb(nb)
            if br.read_ub(1): nb = br.read_ub(5); br.read_sb(nb); br.read_sb(nb)
            nb = br.read_ub(5); br.read_sb(nb); br.read_sb(nb); br.align()
            off = br.byte_pos
        if flags & 0x08:  # cxform
            br = BitReader(tag_data, off)
            ha = br.read_ub(1); hm = br.read_ub(1); nb = br.read_ub(4)
            n = (4 if hm else 0) + (4 if ha else 0)
            for _ in range(n): br.read_sb(nb)
            br.align(); off = br.byte_pos
        if flags & 0x10: off += 2  # ratio
        name = None
        if flags & 0x20:
            end = tag_data.index(0, off)
            name = tag_data[off:end].decode('utf-8', errors='replace')
        clip = None
        if flags & 0x40:
            if name:
                end2 = tag_data.index(0, off)
                off = end2 + 1
            clip = struct.unpack_from('<H', tag_data, off)[0] if flags & 0x40 else None
        return depth, cid, name, bool(flags & 0x01), clip
    elif tag_type == 70:  # PO3
        flags = struct.unpack_from('<H', tag_data, 0)[0]
        depth = struct.unpack_from('<H', tag_data, 2)[0]
        off = 4
        if flags & 0x800:  # className
            end = tag_data.index(0, off); off = end + 1
        cid = None
        if flags & 0x02:
            cid = struct.unpack_from('<H', tag_data, off)[0]; off += 2
        if flags & 0x04:  # matrix
            br = BitReader(tag_data, off)
            if br.read_ub(1): nb = br.read_ub(5); br.read_sb(nb); br.read_sb(nb)
            if br.read_ub(1): nb = br.read_ub(5); br.read_sb(nb); br.read_sb(nb)
            nb = br.read_ub(5); br.read_sb(nb); br.read_sb(nb); br.align()
            off = br.byte_pos
        if flags & 0x08:  # cxform
            br = BitReader(tag_data, off)
            ha = br.read_ub(1); hm = br.read_ub(1); nb = br.read_ub(4)
            n = (4 if hm else 0) + (4 if ha else 0)
            for _ in range(n): br.read_sb(nb)
            br.align(); off = br.byte_pos
        if flags & 0x10: off += 2  # ratio
        name = None
        if flags & 0x20:
            end = tag_data.index(0, off)
            name = tag_data[off:end].decode('utf-8', errors='replace')
        clip = None
        # TODO: parse clip depth after name
        return depth, cid, name, bool(flags & 0x01), clip
    return None, None, None, None, None

def dump_all_places(label, tags, symbols, sprite_symbol):
    """Find sprite by symbol name and dump ALL its PlaceObject tags."""
    sym_to_cid = {v: k for k, v in symbols.items()}
    target_cid = sym_to_cid.get(sprite_symbol)
    if target_cid is None:
        print(f"  {label}: {sprite_symbol} NOT in SymbolClass")
        return
    
    inner = None
    for tt, td in tags:
        if tt == 39:
            cid = struct.unpack_from('<H', td, 0)[0]
            if cid == target_cid:
                fc = struct.unpack_from('<H', td, 2)[0]
                inner = parse_tags(td, 4)
                print(f"  {label}: {sprite_symbol} cid={target_cid}, {fc} frames, {len(inner)} inner tags")
                break
    
    if not inner:
        print(f"  {label}: sprite cid={target_cid} NOT FOUND as DefineSprite")
        return
    
    frame = 0
    for tt, td in inner:
        if tt == 1:
            frame += 1
        elif tt in (26, 70):
            depth, cid, name, is_move, clip = parse_po_name(tt, td)
            sym = symbols.get(cid, f'?#{cid}') if cid else '?'
            tag_name = 'PO2' if tt == 26 else 'PO3'
            print(f"    frame {frame+1}: {tag_name} depth={depth} cid={cid} name={name!r} "
                  f"is_move={is_move} sym={sym}")
        elif tt == 28:
            depth = struct.unpack_from('<H', td, 0)[0]
            print(f"    frame {frame+1}: RemoveObject2 depth={depth}")
        elif tt == 43:
            lbl = td[:td.index(0)].decode('utf-8', errors='replace')
            print(f"    frame {frame+1}: FrameLabel {lbl!r}")

print("=== stage_smashville children ===")
for path in [OG, RT]:
    label = "OG" if path == OG else "RT"
    with open(path, 'rb') as f:
        raw = f.read()
    data = decompress_swf(raw)
    offset = get_offset(data)
    tags = parse_tags(data, offset)
    symbols = {}
    for tt, td in tags:
        if tt == 76:
            symbols.update(parse_symbol_class(td))
    print(f"\n--- {label} ---")
    dump_all_places(label, tags, symbols, 'stage_smashville')

# Also dump smashvilleStage_10 children
print("\n\n=== smashvilleStage_10 frame 1 children ===")
for path in [OG, RT]:
    label = "OG" if path == OG else "RT"
    with open(path, 'rb') as f:
        raw = f.read()
    data = decompress_swf(raw)
    offset = get_offset(data)
    tags = parse_tags(data, offset)
    symbols = {}
    for tt, td in tags:
        if tt == 76:
            symbols.update(parse_symbol_class(td))
    print(f"\n--- {label} ---")
    dump_all_places(label, tags, symbols, 'smashville_fla.smashvilleStage_10')

# Check for font definitions
print("\n\n=== Font definitions ===")
for path in [OG, RT]:
    label = "OG" if path == OG else "RT"
    with open(path, 'rb') as f:
        raw = f.read()
    data = decompress_swf(raw)
    offset = get_offset(data)
    tags = parse_tags(data, offset)
    print(f"\n--- {label} ---")
    font_cids = set()
    for tt, td in tags:
        if tt in (10, 48, 75):  # DefineFont, DefineFont2, DefineFont3
            cid = struct.unpack_from('<H', td, 0)[0]
            font_cids.add(cid)
            print(f"  DefineFont(tag{tt}) cid={cid}")
        elif tt == 37:  # DefineEditText
            cid = struct.unpack_from('<H', td, 0)[0]
            # Parse font ID from DefineEditText
            # Bounds: skip RECT
            br = BitReader(td, 2)
            nb = br.read_ub(5)
            for _ in range(4): br.read_sb(nb)
            br.align()
            off = br.byte_pos
            flags = struct.unpack_from('<H', td, off)[0]
            off += 2
            has_font = bool(flags & 0x01)
            has_max_length = bool(flags & 0x02)
            has_color = bool(flags & 0x04)
            readonly = bool(flags & 0x08)
            password = bool(flags & 0x10)
            multiline = bool(flags & 0x20)
            wordwrap = bool(flags & 0x40)
            has_text = bool(flags & 0x80)
            out_lines = bool(flags & 0x100)
            html = bool(flags & 0x200)
            was_static = bool(flags & 0x400)
            border = bool(flags & 0x800)
            no_select = bool(flags & 0x1000)
            has_layout = bool(flags & 0x2000)
            auto_size = bool(flags & 0x4000)
            has_font_class = bool(flags & 0x8000)
            
            font_id = None
            if has_font:
                font_id = struct.unpack_from('<H', td, off)[0]
                off += 2
            
            print(f"  DefineEditText cid={cid} fontId={font_id} has_font={has_font} "
                  f"(font exists: {font_id in font_cids if font_id else 'N/A'})")
