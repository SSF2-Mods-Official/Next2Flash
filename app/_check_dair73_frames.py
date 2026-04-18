"""Check all frames of DAir_73 (Sprite 1471) in RT SWF for RemoveObject and PO3/PO2 at all depths."""
import struct, zlib

RT = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'
OG = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'

def parse_swf(path):
    with open(path, 'rb') as f:
        raw = f.read()
    if raw[:3] == b'CWS':
        raw = raw[:8] + zlib.decompress(raw[8:])
    pos = 8
    nb = (raw[pos] >> 3) & 0x1f
    pos += (5 + nb * 4 + 7) // 8 + 4
    tags = {}
    while pos < len(raw) - 1:
        hdr = struct.unpack_from('<H', raw, pos)[0]
        tt = hdr >> 6
        sl = hdr & 0x3f
        pos += 2
        if sl == 0x3f:
            l = struct.unpack_from('<I', raw, pos)[0]
            pos += 4
        else:
            l = sl
        pay = raw[pos:pos+l]
        if tt == 0:
            break
        tags.setdefault(tt, []).append(pay)
        pos += l
    return tags


def dump_sprite(tags, sprite_id, label):
    sprites = {struct.unpack_from('<H', p)[0]: p for p in tags.get(39, [])}
    if sprite_id not in sprites:
        print(f"Sprite {sprite_id} NOT FOUND in {label}")
        return
    pay = sprites[sprite_id]
    frame_count = struct.unpack_from('<H', pay, 2)[0]
    print(f"\n=== {label}: Sprite {sprite_id} (DAir_73) frameCount={frame_count} ===")
    sp_pos = 4
    frame = 1
    print(f"[Frame 1]")
    while sp_pos < len(pay) - 1:
        hdr = struct.unpack_from('<H', pay, sp_pos)[0]
        st = hdr >> 6
        ssl = hdr & 0x3f
        sp_pos += 2
        if ssl == 0x3f:
            sl2 = struct.unpack_from('<I', pay, sp_pos)[0]
            sp_pos += 4
        else:
            sl2 = ssl
        spay = pay[sp_pos:sp_pos+sl2]
        if st == 0:
            break
        if st == 1:  # ShowFrame
            frame += 1
            print(f"[Frame {frame}]")
        elif st == 28 and sl2 >= 2:  # RemoveObject2
            depth = struct.unpack_from('<H', spay)[0]
            print(f"  RemoveObject2 depth={depth}")
        elif st == 5 and sl2 >= 4:  # RemoveObject (type 5)
            depth = struct.unpack_from('<H', spay, 2)[0]
            print(f"  RemoveObject  depth={depth}")
        elif st == 70:  # PlaceObject3
            if sl2 >= 4:
                flags = struct.unpack_from('<H', spay)[0]
                depth = struct.unpack_from('<H', spay, 2)[0]
                has_char = (flags >> 1) & 1
                has_image_flag = (flags >> 12) & 1
                is_move = flags & 1
                cid_str = ''
                if has_char and sl2 >= 6:
                    cid = struct.unpack_from('<H', spay, 4)[0]
                    cid_str = f' charID={cid}'
                print(f"  PO3 depth={depth}{cid_str} has_image={has_image_flag} move={is_move}")
        elif st == 26:  # PlaceObject2
            if sl2 >= 3:
                flags = spay[0]
                depth = struct.unpack_from('<H', spay, 1)[0]
                has_char = (flags >> 1) & 1
                cid_str = ''
                if has_char and sl2 >= 5:
                    cid = struct.unpack_from('<H', spay, 3)[0]
                    cid_str = f' charID={cid}'
                print(f"  PO2 depth={depth}{cid_str}")
        sp_pos += sl2


rt_tags = parse_swf(RT)
og_tags = parse_swf(OG)

dump_sprite(rt_tags, 1471, "RT")
dump_sprite(og_tags, 1471, "OG")

# Also check which sprites reference charID 1001 in OG
print("\n\n=== OG sprites referencing charID=1001 (bm_dairHand) ===")
for sp in og_tags.get(39, []):
    sid = struct.unpack_from('<H', sp)[0]
    sp_pos = 4
    while sp_pos < len(sp) - 1:
        hdr = struct.unpack_from('<H', sp, sp_pos)[0]
        st = hdr >> 6; ssl = hdr & 0x3f; sp_pos += 2
        if ssl == 0x3f:
            sl2 = struct.unpack_from('<I', sp, sp_pos)[0]; sp_pos += 4
        else:
            sl2 = ssl
        spay = sp[sp_pos:sp_pos+sl2]
        if st == 0: break
        if st in (26, 70) and sl2 >= 6:
            flags_byte = struct.unpack_from('<H', spay)[0] if st == 70 else (spay[0] | 0)
            if st == 70:
                has_char = (flags_byte >> 1) & 1
                cid_off = 4
            else:  # PO2
                has_char = (spay[0] >> 1) & 1
                cid_off = 3
            if has_char and sl2 >= cid_off + 2:
                cid2 = struct.unpack_from('<H', spay, cid_off)[0]
                if cid2 == 1001:
                    print(f"  Sprite {sid}")
                    break
        sp_pos += sl2
