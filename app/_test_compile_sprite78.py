"""Compile container 78 to SWF tags using the real compile pipeline, 
then parse the resulting sprite and compare with OG."""
import sys, os, struct, zlib, zipfile, io
sys.path.insert(0, os.path.dirname(__file__))

import msgpack
from compile_n2d import to_publish, _compute_total_frames, build_timeline_tags, N2DCompiler

def load_n2d(path):
    with open(path, 'rb') as f:
        raw = f.read()
    if raw[:2] == b'PK':
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            if 'project.msgpack' in zf.namelist():
                return msgpack.unpackb(zf.read('project.msgpack'), raw=False)
    raise ValueError("Cannot load")

def parse_sprite_tags(body):
    offset = 0; tags = []
    while offset < len(body):
        if offset + 2 > len(body): break
        tc = struct.unpack_from('<H', body, offset)[0]; offset += 2
        tag_type = tc >> 6; length = tc & 0x3F
        if length == 0x3F:
            length = struct.unpack_from('<I', body, offset)[0]; offset += 4
        data = body[offset:offset + length]; offset += length
        tags.append((tag_type, data))
        if tag_type == 0: break
    return tags

def parse_po2(data):
    if len(data) < 3: return {}
    flags = data[0]; depth = struct.unpack_from('<H', data, 1)[0]
    r = {'flags': flags, 'depth': depth, 'move': bool(flags & 0x01),
         'hasChar': bool(flags & 0x02), 'hasMatrix': bool(flags & 0x04),
         'hasCxform': bool(flags & 0x08), 'hasRatio': bool(flags & 0x10),
         'hasName': bool(flags & 0x20)}
    off = 3
    if flags & 0x02:
        if off + 2 <= len(data): r['charId'] = struct.unpack_from('<H', data, off)[0]
    return r

def parse_po3(data):
    if len(data) < 4: return {}
    flags = struct.unpack_from('<H', data, 0)[0]; depth = struct.unpack_from('<H', data, 2)[0]
    r = {'flags': flags & 0xFF, 'depth': depth, 'move': bool(flags & 0x01),
         'hasChar': bool(flags & 0x02), 'hasMatrix': bool(flags & 0x04),
         'hasCxform': bool(flags & 0x08), 'hasRatio': bool(flags & 0x10),
         'hasName': bool(flags & 0x20)}
    off = 4
    if flags & 0x02:
        if off + 2 <= len(data): r['charId'] = struct.unpack_from('<H', data, off)[0]
    return r

def po_str(p):
    parts = ['d=%d' % p['depth']]
    if p.get('hasChar'): parts.append('c=%s' % p.get('charId','?'))
    if p.get('move'): parts.append('move')
    if p.get('hasMatrix'): parts.append('mtx')
    if p.get('hasCxform'): parts.append('cx')
    if p.get('hasRatio'): parts.append('ratio')
    if p.get('hasName'): parts.append('name')
    return ','.join(parts)

def main():
    og_path = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"
    n2d_path = 'converted/fox/project.n2d'
    
    # Load N2D
    n2d = load_n2d(n2d_path)
    libs = n2d['libraries']
    id_to_lib = {l['id']: l for l in libs if l}
    
    # Build simple char_id_map: char_array_idx → SWF char ID
    # For this test, just use char_idx + 1 as SWF char ID
    char_id_map = {}
    idx = 0
    for l in libs:
        if l:
            char_id_map[idx] = idx + 1
            idx += 1
    
    # Build lib_to_char_idx 
    lib_to_char_idx = {}
    idx = 0
    for l in libs:
        if l:
            lib_to_char_idx[l['id']] = idx
            idx += 1
    
    # Get container 78
    container = id_to_lib[78]
    
    # Call to_publish (same as _emit_container does)
    tp = to_publish(container, lib_to_char_idx, id_to_lib)
    total_frames = container.get("totalFrame") or _compute_total_frames(container)
    labels = container.get("labels", [])
    actions = container.get("actions", [])
    
    # Build timeline tags 
    inner_bytes = build_timeline_tags(
        total_frames, tp, labels, actions, char_id_map,
        bitmap_char_ids=set(),
    )
    
    # Parse the output
    print("\n=== RT compiled sprite for container 78 ===")
    inner_tags = parse_sprite_tags(inner_bytes)
    frame_num = 0
    for tag_type, data in inner_tags:
        if tag_type == 1:
            frame_num += 1
            print("  --- ShowFrame %d ---" % frame_num)
        elif tag_type == 26:
            po = parse_po2(data)
            print("  PO2: %s" % po_str(po))
        elif tag_type == 70:
            po = parse_po3(data)
            print("  PO3: %s" % po_str(po))
        elif tag_type == 28:
            depth = struct.unpack_from('<H', data, 0)[0]
            print("  RO2: depth=%d" % depth)
        elif tag_type == 0:
            print("  END")
    
    # Parse OG sprite cid=78
    print("\n=== OG sprite cid=78 ===")
    with open(og_path, 'rb') as f:
        sig = f.read(3); f.read(1); f.read(4); rest = f.read()
    if sig == b'CWS': rest = zlib.decompress(rest)
    nbits = rest[0] >> 3; rect_bytes = (5 + 4 * nbits + 7) // 8
    offset = rect_bytes + 4
    while offset < len(rest):
        if offset + 2 > len(rest): break
        tc = struct.unpack_from('<H', rest, offset)[0]; offset += 2
        tag_type = tc >> 6; length = tc & 0x3F
        if length == 0x3F:
            length = struct.unpack_from('<I', rest, offset)[0]; offset += 4
        data = rest[offset:offset + length]; offset += length
        if tag_type == 39 and len(data) >= 4:
            cid = struct.unpack_from('<H', data, 0)[0]
            if cid == 78:
                sprite_tags = parse_sprite_tags(data[4:])
                fn = 0
                for t, d in sprite_tags:
                    if t == 1:
                        fn += 1
                        print("  --- ShowFrame %d ---" % fn)
                    elif t == 26:
                        po = parse_po2(d)
                        print("  PO2: %s" % po_str(po))
                    elif t == 70:
                        po = parse_po3(d)
                        print("  PO3: %s" % po_str(po))
                    elif t == 28:
                        depth = struct.unpack_from('<H', d, 0)[0]
                        print("  RO2: depth=%d" % depth)
                    elif t == 0:
                        print("  END")
                break
        if tag_type == 0: break

if __name__ == '__main__':
    main()
