"""Compare OG vs RT DAir_73 frame 1 PO3 tags for dair bitmaps, and check if OG has hasImage."""
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
    if end_off is None: end_off = len(data)
    while off < end_off:
        if off+2 > end_off: break
        hdr = struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; hdr_sz=2; off+=2
        if ln==0x3F:
            ln=struct.unpack_from('<I',data,off)[0]; off+=4; hdr_sz=6
        body = data[off:off+ln]
        yield tt, body, off-hdr_sz, ln
        off+=ln
        if tt==0: break

def analyze_swf(path, label):
    data = read_swf(path)
    root_start = skip_hdr(data)
    sym_class = {}
    char_types = {}
    sprite_bodies = {}
    for tt, body, abs_off, ln in parse_tags(data, root_start):
        if tt == 76:
            count = struct.unpack_from('<H', body, 0)[0]
            off2 = 2
            for _ in range(count):
                cid = struct.unpack_from('<H', body, off2)[0]; off2 += 2
                end_str = body.index(b'\x00', off2)
                name = body[off2:end_str].decode('utf-8', errors='replace'); off2 = end_str+1
                sym_class[name] = cid; sym_class[cid] = name
        if len(body) >= 2:
            cid = struct.unpack_from('<H', body, 0)[0]
            char_types[cid] = tt
            if tt == 39:
                sprite_bodies[cid] = body

    dair73_cid = sym_class.get('blackmage_fla.DAir_73')
    print(f"\n{'='*50}")
    print(f"{label}: DAir_73 charId={dair73_cid}")

    # Dair bitmap names
    dair_bitmap_cids = {sym_class[n]: n for n in sym_class if isinstance(n, str) and 'bm_dair' in n.lower()}
    print(f"Dair bitmaps: {sorted((v,k) for k,v in dair_bitmap_cids.items())}")

    body = sprite_bodies.get(dair73_cid, b'')
    sub_off = 4; frame_num = 0
    print(f"\nFrame 1 PO3/PO2 tags:")
    while sub_off < len(body):
        if sub_off+2 > len(body): break
        shdr = struct.unpack_from('<H', body, sub_off)[0]; stt=shdr>>6; sln=shdr&0x3F; sh_sz=2; sub_off+=2
        if sln==0x3F:
            sln=struct.unpack_from('<I', body, sub_off)[0]; sub_off+=4; sh_sz=6
        sub_body = body[sub_off:sub_off+sln]
        
        if stt == 1:
            frame_num += 1
            if frame_num >= 2: print("(end)"); break
        elif stt == 70 and len(sub_body) >= 4:  # PO3
            flags1 = sub_body[0]; flags2 = sub_body[1]
            depth = struct.unpack_from('<H', sub_body, 2)[0]
            has_char = bool(flags1 & 0x02); has_image = bool(flags2 & 0x10)
            has_matrix = bool(flags1 & 0x04); has_ct = bool(flags1 & 0x08)
            has_name = bool(flags1 & 0x20); has_ratio = bool(flags1 & 0x10)
            offset = 4
            cid = None
            if has_char and len(sub_body) >= offset+2:
                cid = struct.unpack_from('<H', sub_body, offset)[0]; offset += 2
            cname = sym_class.get(cid, '') if cid else ''
            is_dair = cid in dair_bitmap_cids if cid else False
            print(f"  PO3 d={depth} char={cid}({cname}) has_image={has_image} has_matrix={has_matrix} has_ct={has_ct} has_name={has_name} f1=0x{flags1:02X} f2=0x{flags2:02X}" + (" ←DAIRL" if is_dair else ""))
        elif stt == 26 and len(sub_body) >= 3:  # PO2
            flags = sub_body[0]; depth = struct.unpack_from('<H', sub_body, 1)[0]
            has_char = bool(flags & 0x02); has_name = bool(flags & 0x20)
            cid = None; offset = 3
            if has_char and len(sub_body) >= 5:
                cid = struct.unpack_from('<H', sub_body, 3)[0]; offset = 5
            cname = sym_class.get(cid, '') if cid else ''
            print(f"  PO2 d={depth} char={cid}({cname}) has_name={has_name} flags=0x{flags:02X}")
        
        sub_off += sln
        if stt == 0: break

analyze_swf(OG_PATH, "OG")
analyze_swf(RT_PATH, "RT")
