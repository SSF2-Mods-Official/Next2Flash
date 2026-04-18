"""
Dump ALL placements in Sprite 1471 (DAir_73) from OG and RT.
For each depth: show tag type (PO2/PO3), charID, has_image flag, move flag.
This reveals if RT is setting has_image=1 on bitmaps that OG doesn't.
"""
import struct, zlib

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"

TARGET_SPRITE = 1471  # DAir_73
LL2_TAG  = 36
JPEG3_TAG = 35

def read_swf(path):
    d = open(path, 'rb').read()
    if d[:3] == b'CWS': d = d[:8] + zlib.decompress(d[8:])
    return d

def iter_tags(data):
    pos = 8
    nb = (data[pos] >> 3) & 0x1F
    pos += (5 + nb * 4 + 7) // 8 + 4
    while pos + 1 < len(data):
        hdr = struct.unpack_from('<H', data, pos)[0]; tt = hdr >> 6; sl = hdr & 0x3f; pos += 2
        if sl == 0x3F: l = struct.unpack_from('<I', data, pos)[0]; pos += 4
        else: l = sl
        pay = data[pos:pos + l]
        if tt == 0: break
        yield tt, pay
        pos += l

def iter_sprite(payload):
    pos = 4
    while pos + 1 < len(payload):
        hdr = struct.unpack_from('<H', payload, pos)[0]; tt = hdr >> 6; sl = hdr & 0x3f; pos += 2
        if sl == 0x3F: l = struct.unpack_from('<I', payload, pos)[0]; pos += 4
        else: l = sl
        sp = payload[pos:pos + l]
        if tt == 0: break
        yield tt, sp
        pos += l

def get_bitmap_ids(data):
    ids = set()
    for tt, pay in iter_tags(data):
        if tt in (LL2_TAG, JPEG3_TAG) and len(pay) >= 2:
            ids.add(struct.unpack_from('<H', pay)[0])
    return ids

def dump_dair73_first_frame(data, label):
    """Find Sprite 1471 and dump ALL placements in frame 1 with their has_image flags."""
    bitmap_ids = get_bitmap_ids(data)
    
    sprite_pay = None
    for tt, pay in iter_tags(data):
        if tt == 39 and len(pay) >= 4:
            cid = struct.unpack_from('<H', pay)[0]
            if cid == TARGET_SPRITE:
                sprite_pay = pay
                break
    
    if sprite_pay is None:
        print(f"  [{label}] Sprite {TARGET_SPRITE} NOT FOUND")
        return
    
    frame = 1
    placements = {}  # depth -> {'tag', 'cid', 'has_image', 'move', 'is_bitmap'}
    
    print(f"\n  [{label}] Sprite {TARGET_SPRITE} (DAir_73) — ALL placements in ALL frames:")
    print(f"  {'Frame':>5}  {'Depth':>5}  {'Tag':>4}  {'CharID':>7}  {'HasImg':>6}  {'Move':>4}  {'IsBitmap':>8}")
    print(f"  {'-'*5}  {'-'*5}  {'-'*4}  {'-'*7}  {'-'*6}  {'-'*4}  {'-'*8}")
    
    for stt, sp in iter_sprite(sprite_pay):
        if stt == 1:  # ShowFrame
            frame += 1
        
        elif stt == 70 and len(sp) >= 4:  # PO3
            flags1 = sp[0]; flags2 = sp[1]
            depth  = struct.unpack_from('<H', sp, 2)[0]
            has_char = (flags1 >> 1) & 1
            has_image = (flags2 >> 4) & 1
            is_move  = flags1 & 1
            cid = None
            if has_char and len(sp) >= 6:
                cid = struct.unpack_from('<H', sp, 4)[0]
            is_bmp = (cid in bitmap_ids) if cid else False
            tag_str = f"PO3"
            if cid:
                print(f"  {frame:>5}  {depth:>5}  {tag_str:>4}  {cid:>7}  {has_image:>6}  {int(is_move):>4}  {str(is_bmp):>8}")
            else:
                print(f"  {frame:>5}  {depth:>5}  {tag_str:>4}  {'(none)':>7}  {has_image:>6}  {int(is_move):>4}  {str(is_bmp):>8}")
        
        elif stt == 26 and len(sp) >= 3:  # PO2
            flags = sp[0]
            has_char = (flags >> 1) & 1
            is_move  = flags & 1
            depth = struct.unpack_from('<H', sp, 1)[0]
            cid = None
            if has_char and len(sp) >= 5:
                cid = struct.unpack_from('<H', sp, 3)[0]
            is_bmp = (cid in bitmap_ids) if cid else False
            tag_str = "PO2"
            if cid:
                print(f"  {frame:>5}  {depth:>5}  {tag_str:>4}  {cid:>7}  {'N/A':>6}  {int(is_move):>4}  {str(is_bmp):>8}")
            else:
                # move-only PO2 with no char
                pass  # skip move-only updates to reduce noise
        
        elif stt == 28:  # RemoveObject2
            if len(sp) >= 2:
                depth = struct.unpack_from('<H', sp)[0]
                print(f"  {frame:>5}  {depth:>5}  {'RO2':>4}  {'':>7}  {'':>6}  {'':>4}")
    
    print()

print("=" * 72)
print("DAir_73 (Sprite 1471) placement analysis — OG vs RT")
print("=" * 72)

og_data = read_swf(OG)
rt_data = read_swf(RT)

dump_dair73_first_frame(og_data, 'OG')
dump_dair73_first_frame(rt_data, 'RT')

print("Done.")
