"""
Directly dump inner tags of the anonymous sub-sprites inside DAir_73.
See how bitmaps (LL2 cids) are placed — via PO2, PO3+HasImage, or something else.
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

def dump_inner_tags(spr, label, sym_rev):
    """Print first 30 inner tags to understand structure."""
    off = 0; cnt = 0
    while off < len(spr) and cnt < 40:
        if off+2>len(spr): break
        hdr=struct.unpack_from('<H',spr,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',spr,off)[0]; off+=4
        d=spr[off:off+ln]; off+=ln
        
        tag_info = f"  TT={tt:2d} len={ln:4d}"
        
        if tt == 36:  # DefineBitsLossless2
            cid = struct.unpack_from('<H',d,0)[0]
            fmt = d[2] if len(d)>2 else '?'
            w = struct.unpack_from('<H',d,3)[0] if len(d)>4 else '?'
            h = struct.unpack_from('<H',d,5)[0] if len(d)>6 else '?'
            nm = sym_rev.get(cid,'<anon>')
            tag_info += f"  [LL2]  cid={cid} fmt={fmt} {w}x{h} [{nm[:40]}]"
        elif tt == 26:  # PO2
            flags = d[0]; depth=struct.unpack_from('<H',d,1)[0]
            has_move=bool(flags&1); has_char=bool(flags&2); has_name=bool(flags&0x20)
            cid = None
            if has_char and len(d)>=5:
                cid = struct.unpack_from('<H',d,3)[0]
            nm = sym_rev.get(cid,'<anon>') if cid else ''
            tag_info += f"  [PO2]  depth={depth} cid={cid}[{nm[:30]}] move={has_move} name={has_name}"
        elif tt == 70:  # PO3
            if len(d)>=4:
                f1=d[0]; f2=d[1]
                depth=struct.unpack_from('<H',d,2)[0]
                has_char=bool(f1&0x02); has_img=bool(f2&0x10); has_name=bool(f1&0x20)
                has_classname=bool(f2&0x08)
                off2=4
                if has_classname or (has_img and has_char):
                    ne=d.index(b'\x00',off2); cls=d[off2:ne].decode('utf-8','r'); off2=ne+1
                else:
                    cls='(none)'
                cid=None
                if has_char and off2+2<=len(d):
                    cid=struct.unpack_from('<H',d,off2)[0]
                nm = sym_rev.get(cid,'<anon>') if cid else ''
                tag_info += f"  [PO3]  depth={depth} cid={cid}[{nm[:25]}] HasImg={has_img} cls='{cls}' name={has_name}"
        elif tt == 1:
            tag_info += "  [ShowFrame]"
        elif tt == 0:
            tag_info += "  [End]"
        elif tt == 43:  # FrameLabel
            ne=d.index(b'\x00'); lbl=d[:ne].decode('utf-8','r')
            tag_info += f"  [FrameLabel] '{lbl}'"
        elif tt == 39:  # DefineSprite
            cid=struct.unpack_from('<H',d,0)[0]; nm=sym_rev.get(cid,'<anon>')
            tag_info += f"  [DefineSprite] cid={cid}[{nm[:30]}]"
        elif tt == 2:  # DefineShape
            cid=struct.unpack_from('<H',d,0)[0]; nm=sym_rev.get(cid,'<anon>')
            tag_info += f"  [DefineShape] cid={cid}[{nm[:30]}]"
        elif tt == 32:  # DefineShape3
            cid=struct.unpack_from('<H',d,0)[0]; nm=sym_rev.get(cid,'<anon>')
            tag_info += f"  [DefineShape3] cid={cid}[{nm[:30]}]"
        elif tt == 83:  # DefineShape4
            cid=struct.unpack_from('<H',d,0)[0]; nm=sym_rev.get(cid,'<anon>')
            tag_info += f"  [DefineShape4] cid={cid}[{nm[:30]}]"
        elif tt == 45:  # ImportAssets
            tag_info += "  [ImportAssets]"
        elif tt == 28:  # RemoveObject2
            depth=struct.unpack_from('<H',d,0)[0]
            tag_info += f"  [Remove2] depth={depth}"
        
        print(tag_info)
        cnt += 1
        if tt == 0: break

for label, path, sub_cids in [
    ('OG', OG_PATH, [1469, 1470]),
    ('RT', RT_PATH, [639, 640]),
]:
    data = read_swf(path)
    sym = get_sym(data)
    cid_to_name = {v:k for k,v in sym.items()}
    
    for sc in sub_cids:
        nm = cid_to_name.get(sc, '<anon>')
        print(f"\n[{label}] Sub-sprite cid={sc}[{nm}] inner tags:")
        spr = get_sprite_bytes(data, sc)
        if not spr: print("  NOT FOUND"); continue
        dump_inner_tags(spr, label, cid_to_name)
