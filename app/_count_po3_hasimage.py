"""Count how many sprites in RT place bitmaps via PO3+HasImage (flags2&0x10)."""
import struct, zlib

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

data = read_swf(RT_PATH)
root_start = skip_hdr(data)

sym_class = {}; char_types = {}
off = root_start
sprite_info = {}  # sprite_cid → list of bitmap placements

while off < len(data):
    if off+2 > len(data): break
    hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
    if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
    body=data[off:off+ln]
    if tt == 76:
        count=struct.unpack_from('<H',body,0)[0]; off2=2
        for _ in range(count):
            cid=struct.unpack_from('<H',body,off2)[0]; off2+=2
            end=body.index(b'\x00',off2); name=body[off2:end].decode('utf-8','replace'); off2=end+1
            sym_class[name]=cid; sym_class[cid]=name
    if len(body)>=2:
        cid=struct.unpack_from('<H',body,0)[0]; char_types[cid]=tt
        if tt==39:
            # Scan sprite body for PO3 with has_image
            bmp_places = []
            sub_off=4
            while sub_off<len(body):
                if sub_off+2>len(body): break
                shdr=struct.unpack_from('<H',body,sub_off)[0]; stt=shdr>>6; sln=shdr&0x3F; sub_off+=2
                if sln==0x3F: sln=struct.unpack_from('<I',body,sub_off)[0]; sub_off+=4
                sub_body=body[sub_off:sub_off+sln]
                if stt==70 and len(sub_body)>=6:
                    f1=sub_body[0]; f2=sub_body[1]
                    if (f1&0x02) and (f2&0x10):  # has_char AND has_image
                        ref_cid=struct.unpack_from('<H',sub_body,4)[0]
                        if char_types.get(ref_cid)==36:  # LL2 bitmap
                            bmp_places.append(ref_cid)
                sub_off+=sln
                if stt==0: break
            if bmp_places:
                sprite_info[cid] = bmp_places
    off+=ln
    if tt==0: break

print(f"Sprites with PO3+HasImage LL2 bitmap placements: {len(sprite_info)}")
for cid, bitmaps in sorted(sprite_info.items()):
    name = sym_class.get(cid, f'<sprite_{cid}>')
    bnames = [sym_class.get(b, str(b)) for b in bitmaps[:5]]
    print(f"  Sprite {cid} ({name}): {len(bitmaps)} distinct bitmaps: {bnames[:3]}{'...' if len(bitmaps)>3 else ''}")
