"""Show details of tag_type_mismatch differences."""
import struct, zlib

def parse_swf(path):
    with open(path, 'rb') as f:
        sig = f.read(3)
        f.read(1)
        f.read(4)
        rest = f.read()
    if sig == b'CWS': rest = zlib.decompress(rest)
    nbits = (rest[0] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    return rest[rect_bytes + 4:]

def iter_tags(data):
    pos = 0
    while pos < len(data):
        if pos + 2 > len(data): break
        h = struct.unpack_from('<H', data, pos)[0]
        pos += 2
        tt = h >> 6; length = h & 0x3F
        if length == 0x3F:
            length = struct.unpack_from('<I', data, pos)[0]; pos += 4
        body = data[pos:pos+length]; yield tt, body; pos += length
        if tt == 0: break

def get_sprites(data):
    sprites = {}
    for tt, body in iter_tags(data):
        if tt == 39:
            cid = struct.unpack_from('<H', body, 0)[0]
            sprites[cid] = body[4:]
    return sprites

def get_symbol_class(data):
    m = {}
    for tt, body in iter_tags(data):
        if tt == 76:
            count = struct.unpack_from('<H', body, 0)[0]; off = 2
            for _ in range(count):
                cid = struct.unpack_from('<H', body, off)[0]; off += 2
                end = body.index(b'\x00', off)
                m[cid] = body[off:end].decode('utf-8', errors='replace'); off = end + 1
    return m

def timeline_to_frames(inner):
    frames = []; cur = []
    for tt, body in iter_tags(inner):
        if tt == 0: break
        if tt == 1: frames.append(cur); cur = []
        else: cur.append((tt, body))
    return frames

TAG_NAMES = {0:'End',1:'ShowFrame',26:'PO2',70:'PO3',28:'Remove',43:'FrameLabel',45:'SoundStreamHead2',46:'SoundStreamBlock',19:'SoundStreamHead'}

def main():
    og_data = parse_swf(r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf")
    rt_data = parse_swf(r"C:\Users\glwex\Documents\GitHub\Next2Flash\app\fox_fresh.swf")
    og_sprites = get_sprites(og_data)
    rt_sprites = get_sprites(rt_data)
    og_sym = get_symbol_class(og_data)
    rt_sym = get_symbol_class(rt_data)
    og_c2c = {v:k for k,v in og_sym.items()}
    rt_c2c = {v:k for k,v in rt_sym.items()}
    
    targets = sorted([c for c in og_c2c if 'fox_fla.fox_' in c])
    
    for cls in targets:
        og_cid = og_c2c[cls]
        rt_cid = rt_c2c.get(cls)
        if rt_cid is None or og_cid not in og_sprites or rt_cid not in rt_sprites:
            continue
        og_frames = timeline_to_frames(og_sprites[og_cid])
        rt_frames = timeline_to_frames(rt_sprites[rt_cid])
        if len(og_frames) != len(rt_frames):
            continue
        for fi in range(len(og_frames)):
            if len(og_frames[fi]) != len(rt_frames[fi]):
                print(f"[{cls}] F{fi+1}: OG has {len(og_frames[fi])} tags, RT has {len(rt_frames[fi])}")
                for i, (t,b) in enumerate(og_frames[fi]):
                    print(f"  OG[{i}]: {TAG_NAMES.get(t, f'Tag{t}')} [{len(b)}B]")
                for i, (t,b) in enumerate(rt_frames[fi]):
                    print(f"  RT[{i}]: {TAG_NAMES.get(t, f'Tag{t}')} [{len(b)}B]")
                continue
            for ti in range(len(og_frames[fi])):
                ott, ob = og_frames[fi][ti]
                rtt, rb = rt_frames[fi][ti]
                if ott != rtt:
                    print(f"[{cls}] F{fi+1}[{ti}]: OG={TAG_NAMES.get(ott, f'Tag{ott}')}[{len(ob)}B] RT={TAG_NAMES.get(rtt, f'Tag{rtt}')}[{len(rb)}B]")

if __name__ == '__main__':
    main()
