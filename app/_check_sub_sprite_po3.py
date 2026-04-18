"""
Dump inner tags of RT sub-sprites 639, 640 and parse the PO3 HasImage data.
Also check cids 1002/1003 in OG SymbolClass.
"""
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

def get_sym(data):
    off = skip_hdr(data); sym = {}
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        d=data[off:off+ln]; off+=ln
        if tt==76:
            num=struct.unpack_from('<H',d,0)[0]; o=2
            for _ in range(num):
                c=struct.unpack_from('<H',d,o)[0]; o+=2
                ne=d.index(b'\x00',o); sym[d[o:ne].decode('utf-8','r')]=c; o=ne+1
        if tt==0: break
    return sym

def get_sprite_bytes(data, target_cid):
    off = skip_hdr(data)
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        d=data[off:off+ln]; off+=ln
        if tt==39 and len(d)>=4 and struct.unpack_from('<H',d,0)[0]==target_cid:
            return d[4:]
        if tt==0: break
    return None

for label, path, sub_cids, bmp_cids in [
    ('OG', OG_PATH, [1469, 1470], [1002, 1003]),
    ('RT', RT_PATH, [639, 640], []),
]:
    data = read_swf(path)
    sym = get_sym(data)
    cid_to_name = {v:k for k,v in sym.items()}
    
    if label == 'OG':
        print("[OG] SymbolClass entries for likely bitmap cids:")
        for c in bmp_cids:
            print(f"  cid={c} [{cid_to_name.get(c, '<NOT IN SYMCLASS>')}]")
            
    # Check top-level tag type for each cid
    print(f"\n[{label}] Top-level tag types for bitmap cids in sub-sprites:")
    off = skip_hdr(data)
    tag_type_map = {}
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        d=data[off:off+ln]; off+=ln
        if tt in (2,20,22,32,33,36,39,46,83,84) and ln>=2:
            cid = struct.unpack_from('<H',d,0)[0]
            tag_type_map[cid] = tt
        if tt==0: break
    
    for sc in sub_cids:
        nm = cid_to_name.get(sc, '<anon>')
        print(f"\n[{label}] Sub-sprite cid={sc}[{nm}] inner tags:")
        spr = get_sprite_bytes(data, sc)
        if not spr: print("  NOT FOUND"); continue
        
        off = 0
        while off < len(spr):
            if off+2>len(spr): break
            hdr=struct.unpack_from('<H',spr,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
            if ln==0x3F: ln=struct.unpack_from('<I',spr,off)[0]; off+=4
            d=spr[off:off+ln]; off+=ln
            
            raw_hex = ' '.join(f'{b:02x}' for b in d[:20])
            print(f"  TT={tt:3d} len={ln:5d}  raw: {raw_hex}")
            
            if tt == 70 and len(d)>=4:
                f1=d[0]; f2=d[1]
                depth=struct.unpack_from('<H',d,2)[0]
                has_char=bool(f1&0x02); has_matrix=bool(f1&0x04)
                has_img=bool(f2&0x10); has_cls=bool(f2&0x08)
                has_name=bool(f1&0x20)
                print(f"    → depth={depth} HasChar={has_char} HasImg={has_img} HasCls={has_cls} HasMatrix={has_matrix} HasName={has_name}")
                # Parse: ClassName if HasCls or (HasImg and HasChar)
                off2 = 4
                cls = None
                # Try WITHOUT ClassName first (HasCls=False, treat HasImg/HasChar as no-ClassName)
                if has_char and off2+2<=len(d):
                    cid_candidate = struct.unpack_from('<H',d,off2)[0]
                    cid_type = tag_type_map.get(cid_candidate, '?')
                    nm_c = cid_to_name.get(cid_candidate, '<anon>')
                    print(f"    → [WITHOUT ClassName] CharId={cid_candidate} [{nm_c[:40]}] tag_type={cid_type}")
                # Try WITH ClassName (check if bytes before CharId form a valid string)
                if len(d) > 4 and d[4] != 0x00:
                    # Try to read a string
                    try:
                        ne = d.index(b'\x00', 4)
                        cls_str = d[4:ne].decode('utf-8', 'replace')
                        nc = ne+1
                        if nc+2<=len(d):
                            cid2 = struct.unpack_from('<H',d,nc)[0]
                            cid_type = tag_type_map.get(cid2, '?')
                            nm2 = cid_to_name.get(cid2, '<anon>')
                            print(f"    → [WITH ClassName='{cls_str}'] CharId={cid2} [{nm2[:40]}] tag_type={cid_type}")
                    except: pass
            if tt == 0: break
