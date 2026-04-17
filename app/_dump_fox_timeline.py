"""Dump main fox MC timeline structure to compare OG vs RT"""
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

def get_symbol_class(data):
    sc = {}
    for tt, td in iter_tags(data):
        if tt == 76:
            num = struct.unpack_from('<H', td, 0)[0]
            off = 2
            for _ in range(num):
                cid = struct.unpack_from('<H', td, off)[0]
                off += 2
                end = td.index(0, off)
                name = td[off:end].decode('utf-8')
                off = end + 1
                sc[name] = cid
                sc[cid] = name
    return sc

def read_bits(data, bit_offset, count):
    """Read `count` bits starting at `bit_offset` from data bytes."""
    val = 0
    for i in range(count):
        byte_idx = (bit_offset + i) // 8
        bit_idx = 7 - ((bit_offset + i) % 8)
        val = (val << 1) | ((data[byte_idx] >> bit_idx) & 1)
    return val

def skip_matrix(data, off_bytes):
    """Skip MATRIX record, return new byte offset."""
    bit_off = off_bytes * 8
    has_scale = read_bits(data, bit_off, 1); bit_off += 1
    if has_scale:
        nscale = read_bits(data, bit_off, 5); bit_off += 5
        bit_off += nscale * 2  # scaleX and scaleY
    has_rotate = read_bits(data, bit_off, 1); bit_off += 1
    if has_rotate:
        nrot = read_bits(data, bit_off, 5); bit_off += 5
        bit_off += nrot * 2
    ntrans = read_bits(data, bit_off, 5); bit_off += 5
    bit_off += ntrans * 2
    return (bit_off + 7) // 8

def skip_cxform_alpha(data, off_bytes):
    """Skip CXFORMWITHALPHA, return new byte offset."""
    bit_off = off_bytes * 8
    has_add = read_bits(data, bit_off, 1); bit_off += 1
    has_mult = read_bits(data, bit_off, 1); bit_off += 1
    nbits = read_bits(data, bit_off, 4); bit_off += 4
    if has_mult:
        bit_off += nbits * 4
    if has_add:
        bit_off += nbits * 4
    return (bit_off + 7) // 8

def decode_place2(td):
    """Decode PlaceObject2 tag, return dict with depth, cid, name."""
    flags = td[0]
    off = 1
    depth = struct.unpack_from('<H', td, off)[0]; off += 2
    cid = None; name = None
    if flags & 0x02:  # HasCharacter
        cid = struct.unpack_from('<H', td, off)[0]; off += 2
    if flags & 0x04:  # HasMatrix
        off = skip_matrix(td, off)
    if flags & 0x08:  # HasColorTransform
        off = skip_cxform_alpha(td, off)
    if flags & 0x10:  # HasRatio
        off += 2
    if flags & 0x20:  # HasName
        end = td.index(0, off)
        name = td[off:end].decode('utf-8')
        off = end + 1
    return {'depth': depth, 'cid': cid, 'name': name, 'flags': flags}

def dump_fox_timeline(label, path):
    data = parse_swf(path)
    sc = get_symbol_class(data)
    fox_cid = sc.get('fox')
    print(f'\n=== {label}: fox CID={fox_cid} ===')
    
    for tt, td in iter_tags(data):
        if tt == 39:
            cid = struct.unpack_from('<H', td, 0)[0]
            if cid == fox_cid:
                fc = struct.unpack_from('<H', td, 2)[0]
                print(f'DefineSprite: {fc} frames')
                inner = td[4:]
                frame = 0
                for itt, itd in iter_tags(inner):
                    if itt == 1:
                        frame += 1
                    elif itt == 43:  # FrameLabel
                        end = itd.index(0)
                        name = itd[:end].decode('utf-8')
                        print(f'  F{frame:2d} LABEL: "{name}"')
                    elif itt == 26:  # PlaceObject2
                        info = decode_place2(itd)
                        cid_name = sc.get(info['cid'], '?') if info['cid'] else ''
                        name_str = f' name="{info["name"]}"' if info['name'] else ''
                        cid_str = f' CID={info["cid"]}({cid_name})' if info['cid'] else ''
                        print(f'  F{frame:2d} Place depth={info["depth"]}{cid_str}{name_str}')
                    elif itt == 28:  # RemoveObject2
                        d = struct.unpack_from('<H', itd, 0)[0]
                        print(f'  F{frame:2d} Remove depth={d}')
                break

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\Next2Flash\app\fox_fresh.swf"

dump_fox_timeline("OG", OG)
dump_fox_timeline("RT", RT)
