"""Compare OG sprite-1469 vs RT sprite-639 (scythe sub-sprites)."""
import struct, zlib

OG_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"
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

def parse_tags(data, start_off, end_off=None):
    off = start_off
    while off < (end_off or len(data)):
        if off+2 > len(data): break
        hdr = struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; hdr_sz=2; off+=2
        if ln==0x3F:
            ln=struct.unpack_from('<I',data,off)[0]; off+=4; hdr_sz=6
        body = data[off:off+ln]
        yield tt, body; off+=ln
        if tt==0: break

def dump_sprite(data, sprite_cid, sym_class, label):
    # Find sprite body
    sprite_body = None
    for tt, body in parse_tags(data, skip_hdr(data)):
        if tt == 39 and len(body) >= 2:
            cid = struct.unpack_from('<H', body, 0)[0]
            if cid == sprite_cid:
                sprite_body = body; break
    if not sprite_body:
        print(f"  Sprite {sprite_cid} not found!"); return
    
    frame_count = struct.unpack_from('<H', sprite_body, 2)[0]
    print(f"\n{label} sprite {sprite_cid}: {frame_count} frames")
    
    sub_off = 4; frame_num = 0
    while sub_off < len(sprite_body):
        if sub_off+2 > len(sprite_body): break
        shdr = struct.unpack_from('<H', sprite_body, sub_off)[0]; stt=shdr>>6; sln=shdr&0x3F
        sub_off+=2
        if sln==0x3F: sln=struct.unpack_from('<I', sprite_body, sub_off)[0]; sub_off+=4
        sub_body = sprite_body[sub_off:sub_off+sln]
        
        if stt == 1:
            frame_num += 1
            print(f"  -- ShowFrame (frame {frame_num}) --")
            if frame_num >= 3: print("  (stopping at frame 3)"); break
        elif stt == 70 and len(sub_body) >= 4:
            flags1=sub_body[0]; flags2=sub_body[1]
            depth = struct.unpack_from('<H', sub_body, 2)[0]
            has_char=bool(flags1&0x02); has_image=bool(flags2&0x10)
            has_matrix=bool(flags1&0x04); has_ct=bool(flags1&0x08)
            cid=None; off2=4
            if has_char and len(sub_body)>=6: cid=struct.unpack_from('<H',sub_body,4)[0]; off2=6
            cname = sym_class.get(cid,'') if cid else ''
            print(f"  PO3 d={depth} char={cid}({cname}) has_image={has_image} has_matrix={has_matrix} has_ct={has_ct} f1=0x{flags1:02X} f2=0x{flags2:02X}")
        elif stt == 26 and len(sub_body) >= 3:
            flags=sub_body[0]; depth=struct.unpack_from('<H',sub_body,1)[0]
            has_char=bool(flags&0x02); cid=None
            if has_char and len(sub_body)>=5: cid=struct.unpack_from('<H',sub_body,3)[0]
            cname = sym_class.get(cid,'') if cid else ''
            print(f"  PO2 d={depth} char={cid}({cname}) flags=0x{flags:02X}")
        elif stt == 45:
            print(f"  SoundStreamHead2 len={sln}")
        elif stt == 47:
            print(f"  SoundStreamBlock len={sln}")
        elif stt == 0:
            print(f"  End")
        else:
            print(f"  TT={stt} len={sln}")
        sub_off += sln
        if stt == 0: break

def get_sym(path):
    data = read_swf(path)
    sym = {}
    for tt, body in parse_tags(data, skip_hdr(data)):
        if tt == 76:
            count = struct.unpack_from('<H', body, 0)[0]; off2=2
            for _ in range(count):
                cid=struct.unpack_from('<H',body,off2)[0]; off2+=2
                end=body.index(b'\x00',off2)
                name=body[off2:end].decode('utf-8','replace'); off2=end+1
                sym[name]=cid; sym[cid]=name
            break
    return sym

og_data = read_swf(OG_PATH); rt_data = read_swf(RT_PATH)
og_sym = get_sym(OG_PATH); rt_sym = get_sym(RT_PATH)

dump_sprite(og_data, 1469, og_sym, "OG")
dump_sprite(rt_data, 639, rt_sym, "RT")
