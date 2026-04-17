"""
Deep comparison of DefineSprite inner timelines between OG and RT fox SWFs.
Focus on stance MCs — compare tag-by-tag per frame.
"""
import struct, zlib

def parse_swf(path):
    with open(path, 'rb') as f:
        sig = f.read(3)
        ver = struct.unpack('<B', f.read(1))[0]
        length = struct.unpack_from('<I', f.read(4))[0]
        rest = f.read()
    if sig == b'CWS':
        rest = zlib.decompress(rest)
    nbits = (rest[0] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    data = rest[rect_bytes + 4:]  # skip rect + framerate + framecount
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
        body = data[pos:pos+length]
        yield tt, body
        pos += length
        if tt == 0: break

def get_sprites(data):
    sprites = {}
    for tt, body in iter_tags(data):
        if tt == 39:  # DefineSprite
            cid = struct.unpack_from('<H', body, 0)[0]
            fc = struct.unpack_from('<H', body, 2)[0]
            sprites[cid] = {'frame_count': fc, 'inner': body[4:]}
    return sprites

def get_symbol_class(data):
    mapping = {}
    for tt, body in iter_tags(data):
        if tt == 76:
            count = struct.unpack_from('<H', body, 0)[0]
            off = 2
            for _ in range(count):
                cid = struct.unpack_from('<H', body, off)[0]
                off += 2
                end = body.index(b'\x00', off)
                name = body[off:end].decode('utf-8', errors='replace')
                off = end + 1
                mapping[cid] = name
    return mapping

def timeline_to_frames(inner):
    """Split inner data into per-frame tag lists."""
    frames = []
    cur = []
    for tt, body in iter_tags(inner):
        if tt == 0: break
        if tt == 1:  # ShowFrame
            frames.append(cur)
            cur = []
        else:
            cur.append((tt, body))
    return frames

def po_summary(tt, body):
    """One-line summary of a PlaceObject tag."""
    if tt == 26:
        flags = body[0]
        depth = struct.unpack_from('<H', body, 1)[0]
        off = 3
        cid = None
        if flags & 0x02:
            cid = struct.unpack_from('<H', body, off)[0]
            off += 2
        return f"PO2 d={depth} f=0x{flags:02x} c={cid} [{len(body)}B]"
    elif tt == 70:
        flags = body[0]
        flags2 = body[1] if len(body) > 1 else 0
        depth = struct.unpack_from('<H', body, 2)[0] if len(body) > 3 else 0
        off = 4
        cid = None
        if flags & 0x02:
            cid = struct.unpack_from('<H', body, off)[0]
            off += 2
        return f"PO3 d={depth} f=0x{flags:02x}/0x{flags2:02x} c={cid} [{len(body)}B]"
    elif tt == 28:
        depth = struct.unpack_from('<H', body, 0)[0]
        return f"Remove d={depth}"
    elif tt == 43:
        end = body.index(b'\x00') if b'\x00' in body else len(body)
        label = body[:end].decode('utf-8', errors='replace')
        return f"Label '{label}'"
    else:
        return f"Tag{tt} [{len(body)}B]"

def main():
    og_path = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"
    rt_path = r"C:\Users\glwex\Documents\GitHub\Next2Flash\app\fox_fresh.swf"
    
    og_data = parse_swf(og_path)
    rt_data = parse_swf(rt_path)
    
    og_sprites = get_sprites(og_data)
    rt_sprites = get_sprites(rt_data)
    og_sym = get_symbol_class(og_data)
    rt_sym = get_symbol_class(rt_data)
    
    og_cls2cid = {v: k for k, v in og_sym.items()}
    rt_cls2cid = {v: k for k, v in rt_sym.items()}
    
    # Compare stance MCs
    targets = sorted([c for c in og_cls2cid if 'fox_fla.fox_' in c])
    
    total_diffs = 0
    for cls in targets:
        og_cid = og_cls2cid[cls]
        rt_cid = rt_cls2cid.get(cls)
        if rt_cid is None:
            print(f"[{cls}] MISSING from RT")
            continue
        if og_cid not in og_sprites or rt_cid not in rt_sprites:
            continue
        
        og_frames = timeline_to_frames(og_sprites[og_cid]['inner'])
        rt_frames = timeline_to_frames(rt_sprites[rt_cid]['inner'])
        
        if len(og_frames) != len(rt_frames):
            print(f"[{cls}] FRAME COUNT: OG={len(og_frames)} RT={len(rt_frames)}")
            total_diffs += 1
            continue
        
        sprite_diffs = 0
        for fi in range(len(og_frames)):
            og_tags = og_frames[fi]
            rt_tags = rt_frames[fi]
            
            if len(og_tags) != len(rt_tags):
                print(f"  [{cls}] F{fi+1}: tag count OG={len(og_tags)} RT={len(rt_tags)}")
                for i, (t, b) in enumerate(og_tags):
                    print(f"    OG[{i}]: {po_summary(t, b)}")
                for i, (t, b) in enumerate(rt_tags):
                    print(f"    RT[{i}]: {po_summary(t, b)}")
                sprite_diffs += 1
                continue
            
            for ti in range(len(og_tags)):
                ott, ob = og_tags[ti]
                rtt, rb = rt_tags[ti]
                
                if ott != rtt:
                    print(f"  [{cls}] F{fi+1}[{ti}]: type OG={ott} RT={rtt}")
                    sprite_diffs += 1
                elif ob != rb:
                    # Same tag type, different bytes
                    print(f"  [{cls}] F{fi+1}[{ti}]: {po_summary(ott, ob)}")
                    print(f"    vs RT:               {po_summary(rtt, rb)}")
                    sprite_diffs += 1
        
        if sprite_diffs:
            total_diffs += sprite_diffs
        # else: sprite matches
    
    print(f"\n=== Total: {total_diffs} differences across {len(targets)} stance MCs ===")

if __name__ == '__main__':
    main()
