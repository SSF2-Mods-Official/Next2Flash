"""Walk full DAir_73 sub-sprite hierarchy in OG and RT."""
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
def parse_tags(d,off=None,end=None):
    if off is None: off=skip_hdr(d)
    if end is None: end=len(d)
    r=[]
    while off<end:
        if off+2>end: break
        hdr=struct.unpack_from('<H',d,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',d,off)[0]; off+=4
        r.append((tt,d[off:off+ln])); off+=ln
        if tt==0: break
    return r

for label, path in [('OG', OG), ('RT', RT)]:
    data = read_swf(path)
    bitmaps = {}; sprites = {}; sym = {}; shapes = {}
    for tt, d in parse_tags(data):
        if tt in (35, 36, 20) and len(d) >= 6:
            cid = struct.unpack_from('<H', d, 0)[0]
            w, h = struct.unpack_from('<HH', d, 3) if tt == 36 else (0, 0)
            bitmaps[cid] = (tt, w, h)
        elif tt in (2, 22, 32, 83) and len(d) >= 2:
            cid = struct.unpack_from('<H', d, 0)[0]; shapes[cid] = True
        elif tt == 39 and len(d) >= 4:
            cid = struct.unpack_from('<H', d, 0)[0]
            inner = parse_tags(d, 4, len(d)); pl = []
            for itt, id_ in inner:
                if itt == 26 and len(id_) >= 5 and (id_[0] & 0x02):
                    pl.append(struct.unpack_from('<H', id_, 3)[0])
                elif itt == 70 and len(id_) >= 6 and (id_[0] & 0x02):
                    pl.append(struct.unpack_from('<H', id_, 4)[0])
            sprites[cid] = pl
        elif tt == 76:
            num = struct.unpack_from('<H', d, 0)[0]; o = 2
            for _ in range(num):
                c = struct.unpack_from('<H', d, o)[0]; o += 2
                ne = d.index(b'\x00', o)
                sym[d[o:ne].decode('utf-8', 'r')] = c; o = ne + 1

    cid_to_name = {v: k for k, v in sym.items()}
    dair_cid = sym.get('blackmage_fla.DAir_73')
    print(f'\n[{label}] DAir_73 cid={dair_cid}')

    def walk(cid, depth, prefix=''):
        cat = 'bmp' if cid in bitmaps else ('spr' if cid in sprites else ('shp' if cid in shapes else '???'))
        name = cid_to_name.get(cid, '')
        if cat == 'bmp':
            tt2, w, h = bitmaps[cid]
            in_sym = 'SYM' if cid in cid_to_name else 'ANON'
            print(f'{prefix}{cat} cid={cid} {w}x{h} tag={tt2} {in_sym} [{name}]')
        else:
            print(f'{prefix}{cat} cid={cid} [{name}]')
        if cat == 'spr' and depth < 4:
            children = sorted(set(sprites[cid]))
            for c in children:
                walk(c, depth + 1, prefix + '  ')

    walk(dair_cid, 0)
