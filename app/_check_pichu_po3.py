"""Compare PO3 flags at depth 1 in Idle_3 between OG and RT."""
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
    pos = 8; nbits = data[pos] >> 3
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

og = read_swf(OG); rt = read_swf(RT)
og_tags = parse_tags(og, skip_header(og)); rt_tags = parse_tags(rt, skip_header(rt))
og_sym = rt_sym = None
for t, d in og_tags:
    if t == 76: og_sym = parse_symbol_class(d)
for t, d in rt_tags:
    if t == 76: rt_sym = parse_symbol_class(d)

idle_name = [n for n in og_sym if 'Idle_3' in n][0]

og_sprites = {}; rt_sprites = {}
for t, d in og_tags:
    if t in (39, 37):
        cid = struct.unpack_from('<H', d, 0)[0]
        og_sprites[cid] = parse_tags(d, 4)
for t, d in rt_tags:
    if t in (39, 37):
        cid = struct.unpack_from('<H', d, 0)[0]
        rt_sprites[cid] = parse_tags(d, 4)

og_inner = og_sprites[og_sym[idle_name]]
rt_inner = rt_sprites[rt_sym[idle_name]]

# Dump every tag on every frame, showing raw hex for PO3 at depth 1
def dump_frames(inner_tags, label, cid_to_name):
    frame = 0
    for t, d in inner_tags:
        if t == 1:
            frame += 1
            continue
        if t == 70:  # PO3
            flags = d[0]; flags2 = d[1]
            depth = struct.unpack_from('<H', d, 2)[0]
            has_cid = bool(flags & 0x02)
            is_move = bool(flags & 0x01)
            has_className = bool(flags2 & 0x08)
            has_filter = bool(flags2 & 0x01)
            has_blend = bool(flags2 & 0x02)
            has_cache = bool(flags2 & 0x04)
            has_image = bool(flags2 & 0x80)
            
            cid = struct.unpack_from('<H', d, 4)[0] if has_cid else None
            sym = cid_to_name.get(cid, '') if cid else ''
            
            # Try to read className string if present
            className = ''
            if has_className:
                # className comes before CID in PO3 when HasImage or HasClassName
                # Actually in SWF spec: after flags+depth, if HasClassName or (HasImage && HasCharacter), className string
                pass
            
            if depth == 1 or frame < 3:
                print(f"  [{label}] Frame {frame+1} PO3 depth={depth} flags=0x{flags:02x} flags2=0x{flags2:02x} is_move={is_move} cid={cid}({sym}) hasClassName={has_className} raw={d[:20].hex()}")
        
        elif t == 26:  # PO2
            flags = d[0]
            depth = struct.unpack_from('<H', d, 1)[0]
            has_cid = bool(flags & 0x02)
            is_move = bool(flags & 0x01)
            cid = struct.unpack_from('<H', d, 3)[0] if has_cid else None
            sym = cid_to_name.get(cid, '') if cid else ''
            if depth == 1:
                print(f"  [{label}] Frame {frame+1} PO2 depth={depth} flags=0x{flags:02x} is_move={is_move} cid={cid}({sym})")
        
        elif t == 28:
            depth = struct.unpack_from('<H', d, 0)[0]
            if depth == 1:
                print(f"  [{label}] Frame {frame+1} RemoveObject2 depth={depth}")

og_cid_to_name = {v: k for k, v in og_sym.items()}
rt_cid_to_name = {v: k for k, v in rt_sym.items()}

print("=== OG depth=1 PlaceObject tags ===")
dump_frames(og_inner, "OG", og_cid_to_name)

print("\n=== RT depth=1 PlaceObject tags ===")
dump_frames(rt_inner, "RT", rt_cid_to_name)
