"""Show only the first-frame placements of DAir_73 in OG (sprite 1471) and RT (sprite 650)."""
import struct, zlib

def parse_sprite_frames(path, target_sprite_id):
    with open(path, 'rb') as f:
        raw = f.read()
    sig = raw[:3]
    if sig == b'CWS':
        body = zlib.decompress(raw[8:])
        raw = raw[:8] + body
    
    pos = 8
    nbits = (raw[pos] >> 3) & 0x1f
    pos += (5 + nbits * 4 + 7) // 8
    pos += 4

    defs = {}
    while pos < len(raw) - 1:
        hdr = struct.unpack_from('<H', raw, pos)[0]
        tag_type = hdr >> 6
        short_len = hdr & 0x3f
        pos += 2
        if short_len == 0x3f:
            length = struct.unpack_from('<I', raw, pos)[0]
            pos += 4
        else:
            length = short_len
        payload = raw[pos:pos+length]
        
        if tag_type == 0:
            break
        elif tag_type == 36:
            cid = struct.unpack_from('<H', payload)[0]
            w = struct.unpack_from('<H', payload, 3)[0]
            h = struct.unpack_from('<H', payload, 5)[0]
            defs[cid] = (36, f'LL2 {w}x{h}')
        elif tag_type in (32, 46):
            cid = struct.unpack_from('<H', payload)[0]
            defs[cid] = (tag_type, {32:'DS3', 46:'DS4'}[tag_type])
        elif tag_type == 39:
            sid = struct.unpack_from('<H', payload)[0]
            defs[sid] = (39, 'Sprite')
            if sid == target_sprite_id:
                # Parse this sprite frame by frame
                inner_pos = 4
                frame_num = 0
                frame_state = {}  # depth -> char_id
                frames = []
                while inner_pos < length - 1:
                    h2 = struct.unpack_from('<H', payload, inner_pos)[0]
                    t2 = h2 >> 6
                    sl2 = h2 & 0x3f
                    inner_pos += 2
                    if sl2 == 0x3f:
                        l2 = struct.unpack_from('<I', payload, inner_pos)[0]
                        inner_pos += 4
                    else:
                        l2 = sl2
                    p2 = payload[inner_pos:inner_pos+l2]
                    
                    if t2 == 1:  # ShowFrame
                        frames.append(dict(frame_state))
                        frame_num += 1
                    elif t2 == 26 and l2 >= 3:  # PO2
                        fl1 = p2[0]
                        depth = struct.unpack_from('<H', p2, 1)[0]
                        if fl1 & 0x02 and l2 >= 5:
                            ci = struct.unpack_from('<H', p2, 3)[0]
                            frame_state[depth] = (ci, fl1, 0, 26)
                        elif not (fl1 & 0x02):  # move without char = keep charId
                            pass
                    elif t2 == 70 and l2 >= 4:  # PO3
                        fl1 = p2[0]; fl2 = p2[1]
                        depth = struct.unpack_from('<H', p2, 2)[0]
                        p = 4
                        if fl2 & 0x08:  # HasClassName
                            while p < l2 and p2[p] != 0:
                                p += 1
                            p += 1
                        ci = None
                        if fl1 & 0x02 and p + 2 <= l2:
                            ci = struct.unpack_from('<H', p2, p)[0]
                        if ci is not None:
                            frame_state[depth] = (ci, fl1, fl2, 70)
                    elif t2 == 4:  # RemoveObject
                        depth = struct.unpack_from('<H', p2, 2)[0]
                        frame_state.pop(depth, None)
                    elif t2 == 28:  # RemoveObject2
                        if l2 >= 2:
                            depth = struct.unpack_from('<H', p2)[0]
                            frame_state.pop(depth, None)
                    elif t2 == 0:
                        break
                    inner_pos += l2
                return defs, frames
        pos += length
    return defs, []

OG_PATH = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'
RT_PATH = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'

print("=== OG DAir_73 (Sprite 1471) ===")
og_defs, og_frames = parse_sprite_frames(OG_PATH, 1471)
for i, frame in enumerate(og_frames[:5]):  # first 5 frames
    print(f"  Frame {i+1}:")
    for depth in sorted(frame.keys()):
        ci, fl1, fl2, tt = frame[depth]
        def_info = og_defs.get(ci, (0, 'UNKNOWN'))
        has_img = bool(fl2 & 0x10)
        print(f"    depth={depth:<3} charId={ci:<6} {def_info[1]:<20} has_image={has_img} f1={fl1:#04x} f2={fl2:#04x}")

print()
print("=== RT DAir_73 (Sprite 650) ===")
rt_defs, rt_frames = parse_sprite_frames(RT_PATH, 650)
for i, frame in enumerate(rt_frames[:5]):
    print(f"  Frame {i+1}:")
    for depth in sorted(frame.keys()):
        ci, fl1, fl2, tt = frame[depth]
        def_info = rt_defs.get(ci, (0, 'UNKNOWN'))
        has_img = bool(fl2 & 0x10)
        print(f"    depth={depth:<3} charId={ci:<6} {def_info[1]:<20} has_image={has_img} f1={fl1:#04x} f2={fl2:#04x}")
