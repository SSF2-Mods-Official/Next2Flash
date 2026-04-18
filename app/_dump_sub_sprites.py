"""Dump contents of sub-sprites 63, 66, 639 in RT to find any bitmap references."""
import struct, zlib

RT_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"

def read_swf(p):
    d = open(p,'rb').read()
    if d[:3]==b'CWS': d = b'FWS'+d[3:8]+zlib.decompress(d[8:])
    return d
def prb(d,bo=0):
    bi=bo//8; bi2=bo%8; nb=0
    for i in range(5): nb=(nb<<1)|((d[bi+(bi2+i)//8]>>(7-(bi2+i)%8))&1)
    return 5+nb*4
def skip_hdr(d): return 8+(prb(d,64)+7)//8+4

data = read_swf(RT_PATH)
root_start = skip_hdr(data)

# Get all char types and sprite bodies
char_types = {}; sprite_bodies = {}; sym_class = {}

off = root_start
while off < len(data):
    if off+2 > len(data): break
    hdr = struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
    if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
    body = data[off:off+ln]
    if tt == 76:
        count = struct.unpack_from('<H', body, 0)[0]; off2=2
        for _ in range(count):
            cid=struct.unpack_from('<H',body,off2)[0]; off2+=2
            end=body.index(b'\x00',off2); name=body[off2:end].decode('utf-8','replace'); off2=end+1
            sym_class[name]=cid; sym_class[cid]=name
    if len(body) >= 2:
        cid = struct.unpack_from('<H', body, 0)[0]
        char_types[cid] = tt
        if tt == 39: sprite_bodies[cid] = body
    off += ln
    if tt == 0: break

def dump_sprite_placements(cid, label, max_frames=2):
    body = sprite_bodies.get(cid)
    if not body:
        print(f"\n{label} (charId={cid}): NOT FOUND")
        return
    fc = struct.unpack_from('<H', body, 2)[0]
    print(f"\n{label} (charId={cid}) sym='{sym_class.get(cid,'?')}': {fc} frames")
    sub_off=4; frame_num=0
    while sub_off < len(body):
        if sub_off+2 > len(body): break
        shdr=struct.unpack_from('<H',body,sub_off)[0]; stt=shdr>>6; sln=shdr&0x3F; sub_off+=2
        if sln==0x3F: sln=struct.unpack_from('<I',body,sub_off)[0]; sub_off+=4
        sub_body=body[sub_off:sub_off+sln]
        
        if stt==1:
            frame_num+=1
            if frame_num>max_frames: break
        elif stt in (70,26):
            is_po3 = stt==70
            if is_po3 and len(sub_body)>=4:
                f1=sub_body[0]; f2=sub_body[1]; depth=struct.unpack_from('<H',sub_body,2)[0]
                has_char=bool(f1&0x02); has_image=bool(f2&0x10)
                cid2=None; o=4
                if has_char and len(sub_body)>=6: cid2=struct.unpack_from('<H',sub_body,4)[0]; o=6
                cname=sym_class.get(cid2,'') if cid2 else ''
                ctt=char_types.get(cid2,'?') if cid2 else '?'
                print(f"  [frame {frame_num+1}] PO3 d={depth} char={cid2}({cname}) TT={ctt} has_image={has_image}")
            elif not is_po3 and len(sub_body)>=3:
                flags=sub_body[0]; depth=struct.unpack_from('<H',sub_body,1)[0]
                has_char=bool(flags&0x02); cid2=None
                if has_char and len(sub_body)>=5: cid2=struct.unpack_from('<H',sub_body,3)[0]
                cname=sym_class.get(cid2,'') if cid2 else ''
                ctt=char_types.get(cid2,'?') if cid2 else '?'
                print(f"  [frame {frame_num+1}] PO2 d={depth} char={cid2}({cname}) TT={ctt}")
        elif stt==0: break
        sub_off+=sln

dump_sprite_placements(63, "CollisonBox_6")
dump_sprite_placements(66, "Sprite_66 (itemBox)")
dump_sprite_placements(639, "Sprite_639 (scythe)")
