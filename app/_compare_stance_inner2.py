"""
Compare inner tags of fox_combo_36 stance MC between OG and RT.
Check PlaceObject children, instance names, depths, etc.
"""
import struct, zlib

def parse_swf(path):
    with open(path, 'rb') as f:
        sig = f.read(3)
        ver = struct.unpack('<B', f.read(1))[0]
        length = struct.unpack_from('<I', f.read(4))[0]
        rest = f.read()
    if sig == b'CWS': rest = zlib.decompress(rest)
    data = rest
    nbits = (data[0] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    data = data[rect_bytes:]
    data = data[4:]
    return data

def iter_tags(data):
    pos = 0
    while pos < len(data):
        if pos + 2 > len(data): break
        h = struct.unpack_from('<H', data, pos)[0]
        pos += 2
        tt = h >> 6
        length = h & 0x3F
        if length == 0x3F:
            length = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        td = data[pos:pos+length]
        yield tt, td
        pos += length
        if tt == 0: break

def read_bits(data, bit_offset, count):
    val = 0
    for i in range(count):
        byte_idx = (bit_offset + i) // 8
        bit_idx = 7 - ((bit_offset + i) % 8)
        if byte_idx < len(data):
            val = (val << 1) | ((data[byte_idx] >> bit_idx) & 1)
    return val

def read_sbits(data, bit_offset, count):
    val = read_bits(data, bit_offset, count)
    if val >= (1 << (count - 1)):
        val -= (1 << count)
    return val

def skip_matrix(data, off_bytes):
    bit_off = off_bytes * 8
    has_scale = read_bits(data, bit_off, 1); bit_off += 1
    if has_scale:
        nscale = read_bits(data, bit_off, 5); bit_off += 5
        bit_off += nscale * 2
    has_rotate = read_bits(data, bit_off, 1); bit_off += 1
    if has_rotate:
        nrot = read_bits(data, bit_off, 5); bit_off += 5
        bit_off += nrot * 2
    ntrans = read_bits(data, bit_off, 5); bit_off += 5
    bit_off += ntrans * 2
    return (bit_off + 7) // 8

def skip_cxform_alpha(data, off_bytes):
    bit_off = off_bytes * 8
    has_add = read_bits(data, bit_off, 1); bit_off += 1
    has_mult = read_bits(data, bit_off, 1); bit_off += 1
    nbits_cx = read_bits(data, bit_off, 4); bit_off += 4
    if has_mult: bit_off += nbits_cx * 4
    if has_add: bit_off += nbits_cx * 4
    return (bit_off + 7) // 8

def decode_place2(td):
    flags = td[0]; off = 1
    depth = struct.unpack_from('<H', td, off)[0]; off += 2
    cid = None; name = None; ratio = None; clip_depth = None
    if flags & 0x02: cid = struct.unpack_from('<H', td, off)[0]; off += 2
    if flags & 0x04: off = skip_matrix(td, off)
    if flags & 0x08: off = skip_cxform_alpha(td, off)
    if flags & 0x10: ratio = struct.unpack_from('<H', td, off)[0]; off += 2
    if flags & 0x20:
        end = td.index(0, off)
        name = td[off:end].decode('utf-8'); off = end + 1
    if flags & 0x40: clip_depth = struct.unpack_from('<H', td, off)[0]; off += 2
    return {'depth': depth, 'cid': cid, 'name': name, 'ratio': ratio, 'clip_depth': clip_depth, 'flags': flags}

TAG_NAMES = {
    0: 'End', 1: 'ShowFrame', 2: 'DefineShape', 4: 'PlaceObject',
    5: 'RemoveObject', 6: 'DefineBits', 20: 'DefineBitsLossless',
    21: 'DefineBitsJPEG2', 22: 'DefineShape2', 26: 'PlaceObject2',
    28: 'RemoveObject2', 32: 'DefineShape3', 36: 'DefineBitsLossless2',
    39: 'DefineSprite', 43: 'FrameLabel', 46: 'DefineMorphShape',
    56: 'ExportAssets', 69: 'FileAttributes', 70: 'PlaceObject3',
    76: 'SymbolClass', 77: 'Metadata', 78: 'DefineScalingGrid',
    82: 'DoABC2', 83: 'DefineShape4', 86: 'DefineSceneAndFrameData',
    91: 'DefineMorphShape2'
}

def get_sprites_and_sc(data):
    sprites = {}; sc = {}; sc_rev = {}
    for tt, td in iter_tags(data):
        if tt == 39:
            cid = struct.unpack_from('<H', td, 0)[0]
            fc = struct.unpack_from('<H', td, 2)[0]
            sprites[cid] = (fc, td[4:])
        if tt == 76:
            num = struct.unpack_from('<H', td, 0)[0]; off = 2
            for _ in range(num):
                c = struct.unpack_from('<H', td, off)[0]; off += 2
                end = td.index(0, off)
                n = td[off:end].decode('utf-8'); off = end + 1
                sc[n] = c; sc_rev[c] = n
    return sprites, sc, sc_rev

def dump_sprite_inner(label, inner_data, sc_rev):
    """Dump the inner timeline of a sprite."""
    lines = []
    frame = 0
    for tt, td in iter_tags(inner_data):
        tname = TAG_NAMES.get(tt, f'Tag{tt}')
        if tt == 1:
            lines.append(f"  F{frame:2d} ShowFrame")
            frame += 1
        elif tt == 43:
            end = td.index(0)
            name = td[:end].decode('utf-8')
            lines.append(f"  F{frame:2d} FrameLabel: \"{name}\"")
        elif tt == 26:
            info = decode_place2(td)
            cname = sc_rev.get(info['cid'], '?') if info['cid'] else ''
            extras = []
            if info['name']: extras.append(f'name="{info["name"]}"')
            if info['ratio'] is not None: extras.append(f'ratio={info["ratio"]}')
            if info['clip_depth'] is not None: extras.append(f'clipDepth={info["clip_depth"]}')
            cid_s = f' CID={info["cid"]}({cname})' if info['cid'] else ''
            lines.append(f"  F{frame:2d} Place depth={info['depth']}{cid_s} {' '.join(extras)} flags=0x{info['flags']:02x}")
        elif tt == 28:
            d = struct.unpack_from('<H', td, 0)[0]
            lines.append(f"  F{frame:2d} Remove depth={d}")
        elif tt == 0:
            lines.append(f"  F{frame:2d} End")
        else:
            lines.append(f"  F{frame:2d} {tname}({tt}) len={len(td)}")
    return lines

# Compare specific stance MCs
OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\Next2Flash\app\fox_fresh.swf"

og_data = parse_swf(OG)
rt_data = parse_swf(RT)

og_sprites, og_sc, og_scr = get_sprites_and_sc(og_data)
rt_sprites, rt_sc, rt_scr = get_sprites_and_sc(rt_data)

stances_to_check = [
    'fox_fla.fox_combo_36',
    'fox_fla.fox_DashA_37', 
    'fox_fla.fox_tiltS_38',
    'fox_fla.fox_idle_14',
]

for sname in stances_to_check:
    og_cid = og_sc.get(sname)
    rt_cid = rt_sc.get(sname)
    if not og_cid or not rt_cid:
        print(f"\n{sname}: missing (OG={og_cid}, RT={rt_cid})")
        continue
    
    og_fc, og_inner = og_sprites[og_cid]
    rt_fc, rt_inner = rt_sprites[rt_cid]
    
    print(f"\n=== {sname} (OG CID={og_cid}, RT CID={rt_cid}) ===")
    print(f"Frames: OG={og_fc}, RT={rt_fc}")
    
    og_lines = dump_sprite_inner("OG", og_inner, og_scr)
    rt_lines = dump_sprite_inner("RT", rt_inner, rt_scr)
    
    # Print side by side or show diffs
    max_len = max(len(og_lines), len(rt_lines))
    diffs = 0
    for i in range(max_len):
        og_l = og_lines[i] if i < len(og_lines) else "<missing>"
        rt_l = rt_lines[i] if i < len(rt_lines) else "<missing>"
        # Normalize CID numbers for comparison
        # Compare structurally (ignore CID values, compare names)
        import re
        og_norm = re.sub(r'CID=\d+\(', 'CID=X(', og_l)
        rt_norm = re.sub(r'CID=\d+\(', 'CID=X(', rt_l)
        if og_norm != rt_norm:
            diffs += 1
            print(f"  DIFF line {i}:")
            print(f"    OG: {og_l}")
            print(f"    RT: {rt_l}")
    
    if diffs == 0:
        print(f"  Structurally IDENTICAL ({len(og_lines)} inner tags)")
    else:
        print(f"  {diffs} structural differences out of {max_len} lines")
