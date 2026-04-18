import struct, zlib

RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"
data = open(RT,'rb').read()
if data[:3]==b'CWS': data = b'FWS'+data[3:8]+zlib.decompress(data[8:])

def prb(d,bo=0):
    bi=bo//8; bi2=bo%8; nb=0
    for i in range(5): nb=(nb<<1)|((d[bi+(bi2+i)//8]>>(7-(bi2+i)%8))&1)
    return 5+nb*4

off=8+(prb(data,64)+7)//8+4
tags = []
while off < len(data):
    hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
    if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
    tags.append((tt,data[off:off+ln])); off+=ln
    if tt==0: break

print(f'Total root tags: {len(tags)}')
# Find PlaceObject tags  
po_tags = [(i,tt,d) for i,(tt,d) in enumerate(tags) if tt in (26,70)]
print(f'PlaceObject tags: {len(po_tags)}')
for i,tt,d in po_tags[:10]:
    if tt==26 and len(d)>=5:
        has_char = bool(d[0]&0x02)
        depth = struct.unpack_from('<H',d,1)[0]
        cid = struct.unpack_from('<H',d,3)[0] if has_char else None
        print(f'  [{i}] PO2 depth={depth} cid={cid}')
    elif tt==70 and len(d)>=6:
        has_char = bool(d[0]&0x02)
        depth = struct.unpack_from('<H',d,2)[0]
        cid = struct.unpack_from('<H',d,4)[0] if has_char else None
        print(f'  [{i}] PO3 depth={depth} cid={cid}')
