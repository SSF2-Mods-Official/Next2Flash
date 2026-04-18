"""
Check: in DAir_73's own timeline, are bm_dair0 and bm_dairHand placed 
via PO2 (no HasImage) or PO3+HasImage?
Compare OG vs RT.
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

for label, path, DAIR_CID, BM_CIDS in [
    ('OG', OG_PATH, 1471, {994,995,996,997,998,999,1000,1001,1002,1003,1004}),
    ('RT', RT_PATH, 650, {637,638,641,642,643,644,645,646,647,648,649}),
]:
    data = read_swf(path)
    sym = get_sym(data)
    cid_to_name = {v:k for k,v in sym.items()}
    
    spr = get_sprite_bytes(data, DAIR_CID)
    if not spr: continue
    
    # Find ALL PO2/PO3 placements of dair bitmaps in DAir_73's own timeline
    print(f"\n[{label}] DAir_73 (cid={DAIR_CID}) bitmap placements in own timeline:")
    
    off = 0
    frame = 0
    found = {}  # cid -> (first_frame, tag_type, has_image, depth)
    
    while off < len(spr):
        if off+2>len(spr): break
        hdr=struct.unpack_from('<H',spr,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',spr,off)[0]; off+=4
        d=spr[off:off+ln]; off+=ln
        
        if tt==1: frame+=1
        elif tt==26:  # PO2
            flags=d[0]; depth=struct.unpack_from('<H',d,1)[0]
            has_char=bool(flags&0x02)
            if has_char and len(d)>=5:
                cid=struct.unpack_from('<H',d,3)[0]
                if cid in BM_CIDS and cid not in found:
                    found[cid] = (frame+1, 'PO2', False, depth)
                    # Show raw bytes
                    raw = ' '.join(f'{x:02x}' for x in d[:10])
                    print(f"  Frame {frame+1}: PO2 depth={depth} cid={cid}[{cid_to_name.get(cid,'')}] raw={raw}")
        elif tt==70:  # PO3
            if len(d)>=4:
                f1=d[0]; f2=d[1]; depth=struct.unpack_from('<H',d,2)[0]
                has_char=bool(f1&0x02); has_img=bool(f2&0x10); has_cls=bool(f2&0x08)
                # Parse WITHOUT className (we know from analysis HasClassName=False here)
                cid=None
                if has_char and 4+2<=len(d):
                    cid=struct.unpack_from('<H',d,4)[0]
                if cid in BM_CIDS:
                    if cid not in found:
                        found[cid] = (frame+1, 'PO3', has_img, depth)
                    raw = ' '.join(f'{x:02x}' for x in d[:10])
                    print(f"  Frame {frame+1}: PO3 depth={depth} cid={cid}[{cid_to_name.get(cid,'')}] HasImg={has_img} raw={raw}")
        if tt==0: break
    
    print(f"\n  Summary of first placements:")
    for cid in sorted(found.keys()):
        fr, tt_nm, has_img, depth = found[cid]
        nm = cid_to_name.get(cid,'')
        print(f"    cid={cid}[{nm}]: frame={fr} via {tt_nm} depth={depth} HasImage={has_img}")
