"""
Raw hex dump of sub-sprite inner tags for OG cids 1469, 1470.
"""
import struct, zlib

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

data = read_swf(OG_PATH)
sym = get_sym(data)
cid_to_name = {v:k for k,v in sym.items()}

for sc in [1469, 1470]:
    spr = get_sprite_bytes(data, sc)
    nm = cid_to_name.get(sc, '<anon>')
    print(f"\n[OG] Sub-sprite cid={sc}[{nm}] (first 200 bytes of body):")
    print(f"  Total body bytes: {len(spr)}")
    print("  First 200 bytes hex:")
    for i in range(0, min(200, len(spr)), 16):
        row = spr[i:i+16]
        hex_str = ' '.join(f'{b:02x}' for b in row)
        asc = ''.join(chr(b) if 32<=b<127 else '.' for b in row)
        print(f"  {i:4d}: {hex_str:<48s}  {asc}")
    
    # Parse raw tags without fancy logic
    off = 0; cnt = 0
    print("\n  Raw tag sequence:")
    while off < len(spr) and cnt < 20:
        if off+2>len(spr): break
        hdr=struct.unpack_from('<H',spr,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',spr,off)[0]; off+=4
        d=spr[off:off+ln]; off+=ln
        hex_preview = ' '.join(f'{b:02x}' for b in d[:20])
        print(f"    TT={tt:3d} len={ln:5d}  data: {hex_preview}")
        cnt += 1
        if tt==0: break
