"""
Search ALL DefineSprite tags for one that contains a 'dair' FrameLabel.
That's the main character MC.
"""
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

def sprite_has_label(spr_bytes, label):
    off = 0
    while off < len(spr_bytes):
        if off+2 > len(spr_bytes): break
        hdr=struct.unpack_from('<H',spr_bytes,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',spr_bytes,off)[0]; off+=4
        d=spr_bytes[off:off+ln]; off+=ln
        if tt==43:  # FrameLabel
            null = d.index(b'\x00') if b'\x00' in d else len(d)
            if d[:null].decode('utf-8','r') == label:
                return True
        if tt==0: break
    return False

def get_labels(spr_bytes):
    labels = []
    off = 0
    while off < len(spr_bytes):
        if off+2 > len(spr_bytes): break
        hdr=struct.unpack_from('<H',spr_bytes,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',spr_bytes,off)[0]; off+=4
        d=spr_bytes[off:off+ln]; off+=ln
        if tt==43:
            null = d.index(b'\x00') if b'\x00' in d else len(d)
            labels.append(d[:null].decode('utf-8','r'))
        if tt==0: break
    return labels

for label, path in [('OG', OG_PATH), ('RT', RT_PATH)]:
    data = read_swf(path)
    off = skip_hdr(data)
    sym = {}
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
    cid_to_name = {v:k for k,v in sym.items()}
    
    # Now search all DefineSprites for dair label
    off = skip_hdr(data)
    found_sprites = []
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        d=data[off:off+ln]; off+=ln
        if tt==39 and len(d)>=4:
            cid = struct.unpack_from('<H',d,0)[0]
            inner = d[4:]
            if sprite_has_label(inner, 'dair'):
                labels = get_labels(inner)
                name = cid_to_name.get(cid, '<anon>')
                found_sprites.append((cid, name, len(labels)))
        if tt==0: break
    
    print(f"\n[{label}] DefineSprite tags containing 'dair' frame label:")
    for cid, name, nlabels in found_sprites:
        print(f"  cid={cid} [{name}] labels={nlabels}")
    
    # Also: find DefineSprite containing 'stand' or 'idle' label (should be main char MC)
    off = skip_hdr(data)
    stand_sprites = []
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        d=data[off:off+ln]; off+=ln
        if tt==39 and len(d)>=4:
            cid = struct.unpack_from('<H',d,0)[0]
            inner = d[4:]
            if sprite_has_label(inner, 'stand'):
                name = cid_to_name.get(cid, '<anon>')
                stand_sprites.append((cid, name))
        if tt==0: break
    print(f"  DefineSprites with 'stand' label: {stand_sprites[:5]}")
