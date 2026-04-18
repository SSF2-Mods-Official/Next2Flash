import struct, zlib

RT_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"
OG_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"

def read_swf(p):
    d = open(p,'rb').read()
    if d[:3]==b'CWS': d = b'FWS'+d[3:8]+zlib.decompress(d[8:])
    return d

def prb(d,bo=0):
    bi=bo//8; bi2=bo%8; nb=0
    for i in range(5): nb=(nb<<1)|((d[bi+(bi2+i)//8]>>(7-(bi2+i)%8))&1)
    return 5+nb*4

def skip_hdr(d): return 8+(prb(d,64)+7)//8+4

for label, path in [('OG', OG_PATH), ('RT', RT_PATH)]:
    data = read_swf(path)
    off = skip_hdr(data)
    sprites_cids = set()
    idx = 0
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        d=data[off:off+ln]; off+=ln; idx+=1
        if tt==39 and len(d)>=4: sprites_cids.add(struct.unpack_from('<H',d,0)[0])
        if tt==0: break
    
    # Also find PO2 cids
    off = skip_hdr(data)
    po_cids = []
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        d=data[off:off+ln]; off+=ln
        if tt==26 and len(d)>=5:
            has_char = bool(d[0]&0x02)
            if has_char: po_cids.append(struct.unpack_from('<H',d,3)[0])
        if tt==1: break
        if tt==0: break
    
    print(f"[{label}] DefineSprite cids count: {len(sprites_cids)}, range: {min(sprites_cids)}-{max(sprites_cids)}")
    print(f"  Root PO2 cids (before first ShowFrame): {po_cids}")
    for cid in po_cids:
        found = cid in sprites_cids
        print(f"  cid={cid}: in sprites={found}")
