"""
Check two things:
1. Whether ANY bitmaps placed inside DAir_73 (and its sub-sprites) are NOT SymbolClass-linked in RT
2. Full inner-tag dump of the anonymous scythe sub-sprites (cid=639/640 in RT, cid=1469/1470 in OG)
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
        r.append((tt,d[off:off+ln],off)); off+=ln
        if tt==0: break
    return r

def parse_tags_simple(data_bytes):
    off=0; r=[]
    while off < len(data_bytes):
        if off+2 > len(data_bytes): break
        hdr = struct.unpack_from('<H',data_bytes,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data_bytes,off)[0]; off+=4
        r.append((tt,data_bytes[off:off+ln])); off+=ln
        if tt==0: break
    return r

def analyze(path, label):
    data = read_swf(path)
    tags_list = parse_tags(data)
    sprites = {}; sym = {}; bitmaps_cids = set()
    for tt,d,_ in tags_list:
        if tt in (35,36,20) and len(d)>=2:
            cid=struct.unpack_from('<H',d,0)[0]; bitmaps_cids.add(cid)
        elif tt==39 and len(d)>=4:
            cid=struct.unpack_from('<H',d,0)[0]
            sprites[cid]=d[4:]  # inner bytes
        elif tt==76:
            num=struct.unpack_from('<H',d,0)[0]; o=2
            for _ in range(num):
                c=struct.unpack_from('<H',d,o)[0]; o+=2
                ne=d.index(b'\x00',o); sym[d[o:ne].decode('utf-8','r')]=c; o=ne+1

    cid_to_name = {v:k for k,v in sym.items()}
    sym_cids = set(sym.values())

    # Find DAir_73
    dair_cid = sym.get('blackmage_fla.DAir_73')
    dair_bytes = sprites.get(dair_cid, b'')

    # Collect all charIds placed in DAir_73 with has_img=True
    placed_with_img = []
    placed_sprites = []
    inner_tags = parse_tags_simple(dair_bytes)
    for tt, d in inner_tags:
        if tt == 70 and len(d) >= 6:  # PO3
            flags2 = d[1]
            has_img = bool(flags2 & 0x10)
            has_char = bool(d[0] & 0x02)
            if has_char:
                cid = struct.unpack_from('<H', d, 4)[0]
                name = cid_to_name.get(cid, '<anon>')
                if has_img:
                    placed_with_img.append((cid, name))
                else:
                    placed_sprites.append((cid, name, 'PO3-no-img'))
        elif tt == 26 and len(d) >= 5:  # PO2
            has_char = bool(d[0] & 0x02)
            if has_char:
                cid = struct.unpack_from('<H', d, 3)[0]
                name = cid_to_name.get(cid, '<anon>')
                if cid in bitmaps_cids:
                    placed_with_img.append((cid, name))
                else:
                    placed_sprites.append((cid, name, 'PO2'))

    print(f'\n[{label}] DAir_73 cid={dair_cid}')
    print('Bitmaps placed with has_img=True (or PO2 pointing to bitmap cid):')
    for cid, name in placed_with_img:
        in_sym = '✓SYM' if cid in sym_cids else '✗ANON'
        print(f'  cid={cid} {name:40s} {in_sym}')

    # Now find the anonymous scythe-type sub-sprites and dump their inner tags
    # Find all unique sprite-cids placed in DAir_73 that are NOT SymbolClass
    anon_sprite_cids = set()
    for tt, d in inner_tags:
        if tt in (26, 70) and len(d) >= (5 if tt==26 else 6):
            has_char = bool(d[0] & 0x02)
            if has_char:
                cid = struct.unpack_from('<H', d, 3 if tt==26 else 4)[0]
                if cid not in sym_cids and cid in sprites:
                    anon_sprite_cids.add(cid)

    print(f'\nAnonymous sub-sprites in DAir_73: {sorted(anon_sprite_cids)}')
    for cid in sorted(anon_sprite_cids):
        spr_bytes = sprites[cid]
        spr_tags = parse_tags_simple(spr_bytes)
        print(f'\n  --- Sprite cid={cid} inner tags ({len(spr_tags)} tags):')
        for tt, d in spr_tags:
            if tt == 1: print(f'    ShowFrame')
            elif tt == 28: print(f'    RemoveObject2(depth={struct.unpack_from("<H",d,0)[0]})')
            elif tt == 26:
                has_char = bool(d[0] & 0x02); move = bool(d[0] & 0x01)
                depth = struct.unpack_from('<H',d,1)[0]
                cid2 = struct.unpack_from('<H',d,3)[0] if has_char else None
                name2 = cid_to_name.get(cid2,'anon') if cid2 else ''
                sym_flag = '✓SYM' if cid2 in sym_cids else '✗ANON' if cid2 else ''
                print(f'    PO2(depth={depth}, move={move}, cid={cid2}[{name2}]) {sym_flag}')
            elif tt == 70:
                flags2 = d[1] if len(d)>1 else 0
                has_img = bool(flags2 & 0x10)
                has_char = bool(d[0] & 0x02)
                depth = struct.unpack_from('<H',d,2)[0] if len(d)>=4 else '?'
                cid2 = struct.unpack_from('<H',d,4)[0] if has_char and len(d)>=6 else None
                name2 = cid_to_name.get(cid2,'anon') if cid2 else ''
                sym_flag = '✓SYM' if cid2 in sym_cids else '✗ANON' if cid2 else ''
                print(f'    PO3(depth={depth}, has_img={has_img}, cid={cid2}[{name2}]) {sym_flag}')
            elif tt == 43:
                null = d.index(b'\x00') if b'\x00' in d else len(d)
                print(f'    FrameLabel({d[:null].decode("utf-8","r")})')
            elif tt == 0:
                print(f'    End')
            else:
                print(f'    Tag{tt}(len={len(d)})')

analyze(OG, 'OG')
analyze(RT, 'RT')
