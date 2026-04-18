"""
Full inner-tag comparison of DAir_73 in OG vs RT blackmage.ssf.
Shows every RO2, PO2, PO3, frameLabel, ShowFrame tag.
Focuses on whether the placement/removal sequences match.
"""
import struct, zlib, sys
sys.path.insert(0, '.')

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"

def read_swf(p):
    d = open(p,'rb').read()
    if d[:3]==b'CWS': d = b'FWS'+d[3:8]+zlib.decompress(d[8:])
    return d

def prb(d,bo=0):
    bi=bo//8; bi2=bo%8; nb=0
    for i in range(5): nb=(nb<<1)|((d[bi+(bi2+i)//8]>>(7-(bi2+i)%8))&1)
    return 5+nb*4

def skip_hdr(d): return 8+(prb(d,64)+7)//8+4

def parse_tags(d, off=None, end=None):
    if off is None: off = skip_hdr(d)
    if end is None: end = len(d)
    r = []
    while off < end:
        if off+2 > end: break
        hdr = struct.unpack_from('<H',d,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',d,off)[0]; off+=4
        r.append((tt,d[off:off+ln])); off+=ln
        if tt==0: break
    return r

def describe_tag(tt, d, cid_to_name):
    if tt == 1:   return 'ShowFrame'
    if tt == 28:  # RO2
        depth = struct.unpack_from('<H',d,0)[0] if len(d)>=2 else '?'
        return f'RemoveObject2(depth={depth})'
    if tt == 26:  # PO2
        flags = d[0]; has_char = bool(flags&0x02); has_move = bool(flags&0x01)
        depth = struct.unpack_from('<H',d,1)[0] if len(d)>=3 else '?'
        cid = struct.unpack_from('<H',d,3)[0] if has_char and len(d)>=5 else None
        name = cid_to_name.get(cid,'anon') if cid else ''
        return f'PlaceObject2(depth={depth}, move={has_move}, cid={cid}[{name}])'
    if tt == 70:  # PO3
        flags1=d[0]; flags2=d[1] if len(d)>1 else 0
        has_char = bool(flags1&0x02); has_img = bool(flags2&0x10)
        depth = struct.unpack_from('<H',d,2)[0] if len(d)>=4 else '?'
        cid = struct.unpack_from('<H',d,4)[0] if has_char and len(d)>=6 else None
        name = cid_to_name.get(cid,'anon') if cid else ''
        return f'PlaceObject3(depth={depth}, has_img={has_img}, cid={cid}[{name}])'
    if tt == 43:  # FrameLabel
        null = d.index(b'\x00') if b'\x00' in d else len(d)
        return f'FrameLabel({d[:null].decode("utf-8","r")})'
    return f'Tag{tt}(len={len(d)})'

for label, path in [('OG', OG), ('RT', RT)]:
    data = read_swf(path)
    tags_list = parse_tags(data)
    bitmaps = {}; sprites = {}; sym = {}
    for tt,d in tags_list:
        if tt in (35,36,20) and len(d)>=2:
            cid=struct.unpack_from('<H',d,0)[0]; bitmaps[cid]=True
        elif tt==39 and len(d)>=4:
            cid=struct.unpack_from('<H',d,0)[0]
            sprites[cid]=parse_tags(d,4,len(d))
        elif tt==76:
            num=struct.unpack_from('<H',d,0)[0]; o=2
            for _ in range(num):
                c=struct.unpack_from('<H',d,o)[0]; o+=2
                ne=d.index(b'\x00',o); sym[d[o:ne].decode('utf-8','r')]=c; o=ne+1

    cid_to_name = {v:k for k,v in sym.items()}
    dair_cid = sym.get('blackmage_fla.DAir_73')
    inner = sprites.get(dair_cid, [])

    print(f'\n[{label}] DAir_73 cid={dair_cid}, inner tags: {len(inner)}')
    print('='*60)
    for tt, d in inner:
        desc = describe_tag(tt, d, cid_to_name)
        print(f'  {desc}')
