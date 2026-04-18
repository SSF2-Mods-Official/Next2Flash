"""
Find which bitmaps in the RT SWF are NOT SymbolClass-linked (anonymous bitmaps).
Then check if any of these anonymous bitmaps are placed inside animations that
get accessed during updatePaletteSwap (m_sprite.stance or charHead recursion).
"""
import struct, zlib, sys
sys.path.insert(0, '.')

RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"
OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"

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

def parse_sprite_inner(b):
    r = []
    off = 0
    while off < len(b):
        if off+2 > len(b): break
        hdr = struct.unpack_from('<H',b,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',b,off)[0]; off+=4
        r.append((tt,b[off:off+ln])); off+=ln
        if tt==0: break
    return r

for label, path in [('OG', OG), ('RT', RT)]:
    data = read_swf(path)
    tags = parse_tags(data)
    sym = {}; bitmaps = set(); sprites = {}
    for tt, d in tags:
        if tt in (35,36,20) and len(d)>=2:
            bitmaps.add(struct.unpack_from('<H',d,0)[0])
        elif tt==39 and len(d)>=4:
            cid=struct.unpack_from('<H',d,0)[0]; sprites[cid]=d[4:]
        elif tt==76:
            num=struct.unpack_from('<H',d,0)[0]; o=2
            for _ in range(num):
                c=struct.unpack_from('<H',d,o)[0]; o+=2
                ne=d.index(b'\x00',o); sym[d[o:ne].decode('utf-8','r')]=c; o=ne+1
    
    cid_to_name = {v:k for k,v in sym.items()}
    sym_cids = set(sym.values())
    anon_bitmaps = bitmaps - sym_cids
    
    print(f"\n[{label}] Total bitmaps: {len(bitmaps)}, SymbolClass: {len(bitmaps & sym_cids)}, Anonymous: {len(anon_bitmaps)}")
    
    # For each anonymous bitmap, find which sprites reference it
    # (to check if any come from charHead or similar portrait/PA sprites)
    anon_referenced_by = {}  # anon_cid -> list of parent sprite cids
    for spr_cid, spr_bytes in sprites.items():
        inner = parse_sprite_inner(spr_bytes)
        for tt, d in inner:
            if tt == 70 and len(d)>=6:  # PO3
                has_char = bool(d[0] & 0x02)
                has_img = bool(d[1] & 0x10)
                if has_char and has_img:
                    cid2 = struct.unpack_from('<H',d,4)[0]
                    if cid2 in anon_bitmaps:
                        anon_referenced_by.setdefault(cid2, set()).add(spr_cid)
    
    if anon_bitmaps:
        print(f"  Anonymous bitmaps (first 20):")
        for cid in sorted(anon_bitmaps)[:20]:
            parents = anon_referenced_by.get(cid, set())
            parent_names = [cid_to_name.get(p, f'anon_{p}') for p in parents]
            print(f"    cid={cid} (used in: {parent_names})")
        if len(anon_bitmaps) > 20:
            print(f"    ... and {len(anon_bitmaps)-20} more")
    else:
        print(f"  No anonymous bitmaps!")
    
    # Also check: for OG, how many bitmaps have NO SymbolClass entry?
    # (to compare with RT)
    print(f"  Sample anon bitmap cids: {sorted(anon_bitmaps)[:10]}")
