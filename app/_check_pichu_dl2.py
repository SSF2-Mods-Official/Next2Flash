"""Properly parse PO2 and PO3 in pichu Idle_3 and compare display lists."""
import struct, zlib

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\pichu.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\pichu.ssf"

def read_swf(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:3] in (b'CWS', b'ZWS'):
        data = data[:8] + zlib.decompress(data[8:])
    return data

def parse_tags(data, offset=0):
    tags = []; pos = offset
    while pos < len(data):
        if pos + 2 > len(data): break
        h = struct.unpack_from('<H', data, pos)[0]
        tt = h >> 6; length = h & 0x3F; pos += 2
        if length == 0x3F:
            length = struct.unpack_from('<I', data, pos)[0]; pos += 4
        tags.append((tt, data[pos:pos+length]))
        pos += length
        if tt == 0: break
    return tags

def skip_header(data):
    pos = 8
    nbits = data[pos] >> 3
    pos += (5 + nbits * 4 + 7) // 8 + 4
    return pos

def parse_symbol_class(data):
    pos = 0; count = struct.unpack_from('<H', data, pos)[0]; pos += 2
    symbols = {}
    for _ in range(count):
        cid = struct.unpack_from('<H', data, pos)[0]; pos += 2
        end = data.index(0, pos)
        symbols[data[pos:end].decode('utf-8')] = cid; pos = end + 1
    return symbols

def read_matrix(data, bit_pos):
    """Read SWF matrix from bit stream. Returns new bit_pos."""
    has_scale = (data[bit_pos >> 3] >> (7 - (bit_pos & 7))) & 1
    bit_pos += 1
    if has_scale:
        nbits = 0
        for i in range(5):
            nbits = (nbits << 1) | ((data[(bit_pos + i) >> 3] >> (7 - ((bit_pos + i) & 7))) & 1)
        bit_pos += 5
        bit_pos += nbits * 2  # scaleX, scaleY
    has_rotate = (data[bit_pos >> 3] >> (7 - (bit_pos & 7))) & 1
    bit_pos += 1
    if has_rotate:
        nbits = 0
        for i in range(5):
            nbits = (nbits << 1) | ((data[(bit_pos + i) >> 3] >> (7 - ((bit_pos + i) & 7))) & 1)
        bit_pos += 5
        bit_pos += nbits * 2  # rotateSkew0, rotateSkew1
    nbits = 0
    for i in range(5):
        nbits = (nbits << 1) | ((data[(bit_pos + i) >> 3] >> (7 - ((bit_pos + i) & 7))) & 1)
    bit_pos += 5
    bit_pos += nbits * 2  # translateX, translateY
    return (bit_pos + 7) & ~7  # align to byte

def read_cxform_alpha(data, bit_pos):
    """Read SWF CXFORMWITHALPHA from bit stream."""
    has_add = (data[bit_pos >> 3] >> (7 - (bit_pos & 7))) & 1; bit_pos += 1
    has_mult = (data[bit_pos >> 3] >> (7 - (bit_pos & 7))) & 1; bit_pos += 1
    nbits = 0
    for i in range(4):
        nbits = (nbits << 1) | ((data[(bit_pos + i) >> 3] >> (7 - ((bit_pos + i) & 7))) & 1)
    bit_pos += 4
    if has_mult: bit_pos += nbits * 4
    if has_add: bit_pos += nbits * 4
    return (bit_pos + 7) & ~7

def parse_place_object(tag_type, data):
    """Parse PO2 (26) or PO3 (70) properly."""
    flags = data[0]; pos = 1
    flags2 = 0
    if tag_type == 70:
        flags2 = data[1]; pos = 2
    
    depth = struct.unpack_from('<H', data, pos)[0]; pos += 2
    
    r = {
        'flags': flags, 'flags2': flags2, 'depth': depth,
        'is_move': bool(flags & 0x01),
        'has_cid': bool(flags & 0x02),
        'has_matrix': bool(flags & 0x04),
        'has_cxform': bool(flags & 0x08),
        'has_ratio': bool(flags & 0x10),
        'has_name': bool(flags & 0x20),
        'has_clip_depth': bool(flags & 0x40),
        'has_clip_actions': bool(flags & 0x80),
    }
    if tag_type == 70:
        r['has_filter_list'] = bool(flags2 & 0x01)
        r['has_blend_mode'] = bool(flags2 & 0x02)
    
    if flags & 0x02:
        r['cid'] = struct.unpack_from('<H', data, pos)[0]; pos += 2
    
    if flags & 0x04:  # has matrix
        bit_pos = pos * 8
        byte_pos = read_matrix(data, bit_pos) >> 3
        pos = byte_pos
    
    if flags & 0x08:  # has cxform
        bit_pos = pos * 8
        byte_pos = read_cxform_alpha(data, bit_pos) >> 3
        pos = byte_pos
    
    if flags & 0x10:  # has ratio
        r['ratio'] = struct.unpack_from('<H', data, pos)[0]; pos += 2
    
    if flags & 0x20:  # has name
        end = data.index(0, pos)
        r['name'] = data[pos:end].decode('utf-8', errors='replace')
        pos = end + 1
    
    if flags & 0x40:  # has clip depth
        r['clip_depth'] = struct.unpack_from('<H', data, pos)[0]; pos += 2
    
    return r

og = read_swf(OG); rt = read_swf(RT)
og_tags = parse_tags(og, skip_header(og)); rt_tags = parse_tags(rt, skip_header(rt))
og_sym = rt_sym = None
for t, d in og_tags:
    if t == 76: og_sym = parse_symbol_class(d)
for t, d in rt_tags:
    if t == 76: rt_sym = parse_symbol_class(d)

idle_name = [n for n in og_sym if 'Idle_3' in n][0]
print("Symbol:", idle_name)
og_cid_to_name = {v: k for k, v in og_sym.items()}
rt_cid_to_name = {v: k for k, v in rt_sym.items()}

og_sprites = {}; rt_sprites = {}
for t, d in og_tags:
    if t in (39, 37):
        cid = struct.unpack_from('<H', d, 0)[0]
        og_sprites[cid] = parse_tags(d, 4)
for t, d in rt_tags:
    if t in (39, 37):
        cid = struct.unpack_from('<H', d, 0)[0]
        rt_sprites[cid] = parse_tags(d, 4)

og_idle_cid = og_sym[idle_name]
rt_idle_cid = rt_sym[idle_name]

# Build display lists with full parsing
def build_dl_full(inner_tags):
    dl = {}  # depth -> {cid, name, ...}
    frames = []
    for t, d in inner_tags:
        if t in (26, 70):
            po = parse_place_object(t, d)
            depth = po['depth']
            if po['is_move']:
                if depth in dl:
                    for k, v in po.items():
                        if k not in ('is_move', 'flags', 'flags2'):
                            dl[depth][k] = v
                else:
                    dl[depth] = po.copy()
            else:
                dl[depth] = po.copy()
        elif t == 28:
            depth = struct.unpack_from('<H', d, 0)[0]
            dl.pop(depth, None)
        elif t == 1:
            frames.append({d: dict(v) for d, v in dl.items()})
    return frames

og_dl = build_dl_full(og_sprites[og_idle_cid])
rt_dl = build_dl_full(rt_sprites[rt_idle_cid])
print(f"Frames: OG={len(og_dl)}, RT={len(rt_dl)}")

# Show display list at frame 26 (index 25) with names
print("\n=== OG Display List at Frame 26 ===")
for depth in sorted(og_dl[25]):
    e = og_dl[25][depth]
    cid = e.get('cid', '?')
    name = e.get('name', '')
    sym = og_cid_to_name.get(cid, '') if isinstance(cid, int) else ''
    print(f"  depth={depth}: cid={cid} name='{name}' sym='{sym}' ratio={e.get('ratio','')}")

print("\n=== RT Display List at Frame 26 ===")
for depth in sorted(rt_dl[25]):
    e = rt_dl[25][depth]
    cid = e.get('cid', '?')
    name = e.get('name', '')
    sym = rt_cid_to_name.get(cid, '') if isinstance(cid, int) else ''
    print(f"  depth={depth}: cid={cid} name='{name}' sym='{sym}' ratio={e.get('ratio','')}")

# Compare depths
og_depths = set(og_dl[25].keys())
rt_depths = set(rt_dl[25].keys())
print(f"\nOnly in OG: {sorted(og_depths - rt_depths)}")
print(f"Only in RT: {sorted(rt_depths - og_depths)}")

# Show differences at common depths
for d in sorted(og_depths & rt_depths):
    og_e = og_dl[25][d]
    rt_e = rt_dl[25][d]
    og_sym_name = og_cid_to_name.get(og_e.get('cid'), '')
    rt_sym_name = rt_cid_to_name.get(rt_e.get('cid'), '')
    if og_sym_name != rt_sym_name:
        print(f"  Depth {d} CID MISMATCH: OG={og_sym_name}({og_e.get('cid')}) vs RT={rt_sym_name}({rt_e.get('cid')})")
    og_name = og_e.get('name', '')
    rt_name = rt_e.get('name', '')
    if og_name != rt_name:
        print(f"  Depth {d} NAME MISMATCH: OG='{og_name}' vs RT='{rt_name}'")

# Also show frame 1 (initial placement) to see named children
print("\n=== OG Display List at Frame 1 ===")
for depth in sorted(og_dl[0]):
    e = og_dl[0][depth]
    cid = e.get('cid', '?')
    name = e.get('name', '')
    sym = og_cid_to_name.get(cid, '') if isinstance(cid, int) else ''
    clip = e.get('clip_depth', '')
    print(f"  depth={depth}: cid={cid} name='{name}' sym='{sym}' clip_depth={clip}")

print("\n=== RT Display List at Frame 1 ===")
for depth in sorted(rt_dl[0]):
    e = rt_dl[0][depth]
    cid = e.get('cid', '?')
    name = e.get('name', '')
    sym = rt_cid_to_name.get(cid, '') if isinstance(cid, int) else ''
    clip = e.get('clip_depth', '')
    print(f"  depth={depth}: cid={cid} name='{name}' sym='{sym}' clip_depth={clip}")
