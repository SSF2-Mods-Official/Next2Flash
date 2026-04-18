"""Check what tag type OG dair bitmaps use (LL2 or JPEG3)."""
import struct, zlib
def read_swf(p):
    d = open(p,'rb').read()
    if d[:3]==b'CWS': d = b'FWS'+d[3:8]+zlib.decompress(d[8:])
    return d
def prb(d,bo=0):
    bi=bo//8; bi2=bo%8; nb=0
    for i in range(5): nb=(nb<<1)|((d[bi+(bi2+i)//8]>>(7-(bi2+i)%8))&1)
    return 5+nb*4
def skip_hdr(d): return 8+(prb(d,64)+7)//8+4

OG=r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'
data=read_swf(OG)
# Dair bitmap cids in OG
dair_og = {1001:'bm_dairHand', 1002:'bm_dairScythe', 1003:'bm_dairScytheBlade', 1004:'bm_dair0'}
off=skip_hdr(data)
tag_names_map={20:'DefineBits',21:'DefineBitsJPEG2',35:'DefineBitsJPEG3',36:'DefineBitsLossless2',6:'DefineBitsLossless',37:'DefineBitsLossless'}
while off<len(data):
    hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
    if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
    body=data[off:off+ln]
    if len(body)>=2:
        cid=struct.unpack_from('<H',body,0)[0]
        if cid in dair_og:
            name=dair_og[cid]
            tname = tag_names_map.get(tt, str(tt))
            if tt==36 and len(body)>=7:
                fmt=body[2]; w=struct.unpack_from('<H',body,3)[0]; h=struct.unpack_from('<H',body,5)[0]
                print(f'OG {name}(cid={cid}): TT={tt}({tname}) fmt={fmt} {w}x{h}')
            elif tt==35 and len(body)>=6:
                print(f'OG {name}(cid={cid}): TT={tt}({tname}) size={ln}')
            else:
                print(f'OG {name}(cid={cid}): TT={tt}({tname}) size={ln}')
    off+=ln
    if tt==0: break
