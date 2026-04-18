"""
Check:
1. OG DefineMorphShape tags for dair bitmap references
2. Inner tags of sub-sprite 1279 (OG) and 66 (RT) -- the 4th sub-sprite in DAir_73
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

data_og = read_swf(OG_PATH)
data_rt = read_swf(RT_PATH)
sym_og = get_sym(data_og)
sym_rt = get_sym(data_rt)
cid_to_og = {v:k for k,v in sym_og.items()}
cid_to_rt = {v:k for k,v in sym_rt.items()}

dair_bmp_cids_og = {c for nm,c in sym_og.items() if 'dair' in nm.lower() or 'scythe' in nm.lower()}
dair_bmp_cids_rt = {c for nm,c in sym_rt.items() if 'dair' in nm.lower() or 'scythe' in nm.lower()}
# Also add by numeric: bm_dair0-7, bm_dairHand, bm_dairScythe, bm_dairScytheBlade

print("=== 1. Check OG DefineMorphShape (TT=46) for dair bitmap references ===")
print(f"Dair bitmap cids in OG: {sorted(dair_bmp_cids_og)}")

off = skip_hdr(data_og)
morph_count = 0
morph_with_dair = []
while off < len(data_og):
    hdr=struct.unpack_from('<H',data_og,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
    if ln==0x3F: ln=struct.unpack_from('<I',data_og,off)[0]; off+=4
    d=data_og[off:off+ln]; off+=ln
    if tt == 46:  # DefineMorphShape
        morph_count += 1
        cid = struct.unpack_from('<H',d,0)[0]
        # Check if any dair bitmap cid bytes appear in the body
        found = []
        for dc in dair_bmp_cids_og:
            cb = struct.pack('<H', dc)
            if cb in d[2:]:
                found.append(dc)
        if found:
            morph_with_dair.append((cid, cid_to_og.get(cid,'<anon>'), found))
        else:
            print(f"  MorphShape cid={cid}[{cid_to_og.get(cid,'<anon>')}]: no dair refs")
    if tt==0: break

print(f"\nTotal DefineMorphShape in OG: {morph_count}")
if morph_with_dair:
    print(f"Morph shapes WITH dair bitmap refs:")
    for cid, nm, bitmaps in morph_with_dair:
        print(f"  cid={cid}[{nm}]: dair bitmaps {bitmaps}")
else:
    print("NO morph shapes reference dair bitmaps => morph-to-LL2 conversion NOT the cause")

print("\n=== 2. Inner tags of sub-sprite 1279 (OG) and 66 (RT) ===")
for label, data, sc_cid, sym_rev in [
    ('OG', data_og, 1279, cid_to_og),
    ('RT', data_rt, 66, cid_to_rt),
]:
    nm = sym_rev.get(sc_cid, '<anon>')
    print(f"\n[{label}] Sub-sprite cid={sc_cid}[{nm}]:")
    spr = get_sprite_bytes(data, sc_cid)
    if not spr:
        print("  NOT FOUND")
        continue
    print(f"  Total body bytes: {len(spr)}")
    
    off = 0; cnt = 0; frame = 0
    while off < len(spr) and cnt < 60:
        if off+2>len(spr): break
        hdr=struct.unpack_from('<H',spr,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',spr,off)[0]; off+=4
        d=spr[off:off+ln]; off+=ln
        
        if tt == 1:
            frame += 1
            print(f"  ShowFrame -> frame {frame}")
        elif tt == 0:
            print(f"  End")
            break
        elif tt == 43:  # FrameLabel
            ne=d.index(b'\x00'); lbl=d[:ne].decode('utf-8','r')
            print(f"  FrameLabel '{lbl}'")
        elif tt == 26:  # PO2
            flags=d[0]; depth=struct.unpack_from('<H',d,1)[0]
            has_char=bool(flags&0x02); has_name=bool(flags&0x20)
            cid=None
            if has_char and len(d)>=5: cid=struct.unpack_from('<H',d,3)[0]
            nm2=sym_rev.get(cid,'<anon>') if cid else ''
            print(f"  PO2 depth={depth} cid={cid}[{nm2[:35]}] name={has_name}")
        elif tt == 70:  # PO3
            if len(d)>=4:
                f1=d[0]; f2=d[1]; depth=struct.unpack_from('<H',d,2)[0]
                has_char=bool(f1&0x02); has_img=bool(f2&0x10); has_cls=bool(f2&0x08)
                off2=4
                # Try without ClassName first
                cid=None
                if has_char and off2+2<=len(d): cid=struct.unpack_from('<H',d,off2)[0]
                nm2=sym_rev.get(cid,'<anon>') if cid else ''
                print(f"  PO3 depth={depth} cid={cid}[{nm2[:30]}] HasImg={has_img} HasCls={has_cls}")
        elif tt == 36:  # LL2 inside sprite (unusual but check)
            cid=struct.unpack_from('<H',d,0)[0]
            print(f"  !! EMBEDDED LL2 cid={cid}[{sym_rev.get(cid,'<anon>')}] !!")
        elif tt == 28:  # Remove2
            depth=struct.unpack_from('<H',d,0)[0]
            print(f"  Remove2 depth={depth}")
        else:
            print(f"  TT={tt} len={ln}")
        cnt += 1
