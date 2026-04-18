"""Dump sub-sprite structure for dair in RT, verify bitmap charIDs exist in dict."""
import struct, zlib
from collections import defaultdict

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

def parse_tags(data, start_off, end_off=None):
    """Parse SWF tags from start_off to end_off (or end of data), yield (tt, body, abs_off)."""
    off = start_off
    if end_off is None: end_off = len(data)
    while off < end_off:
        if off+2 > end_off: break
        hdr = struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; hdr_sz=2; off+=2
        if ln==0x3F:
            if off+4 > end_off: break
            ln=struct.unpack_from('<I',data,off)[0]; off+=4; hdr_sz=6
        body = data[off:off+ln]
        yield tt, body, off-hdr_sz, ln
        off+=ln
        if tt==0: break

data = read_swf(RT_PATH)
root_start = skip_hdr(data)

# Collect all defined character IDs and their types
char_types = {}  # charId → tag type
sprite_tags = {}  # charId → (abs_off, body)

# Also collect name→charId from SymbolClass
sym_class = {}

for tt, body, abs_off, ln in parse_tags(data, root_start):
    cid = None
    if tt in (2, 22, 32, 46, 83):  # DefineShape, DefineShape2/3/4, DefineShape4+morph
        if len(body) >= 2: cid = struct.unpack_from('<H', body, 0)[0]
    elif tt in (36, 20, 21, 35):  # DefineBitsLossless2/1, JPEG
        if len(body) >= 2: cid = struct.unpack_from('<H', body, 0)[0]
    elif tt == 39:  # DefineSprite
        if len(body) >= 2: cid = struct.unpack_from('<H', body, 0)[0]
        if cid is not None: sprite_tags[cid] = (abs_off, body)
    if cid is not None:
        char_types[cid] = tt

# Find bm_dair* by SymbolClass
for tt, body, abs_off, ln in parse_tags(data, root_start):
    if tt == 76:  # SymbolClass
        count = struct.unpack_from('<H', body, 0)[0]
        off2 = 2
        for _ in range(count):
            cid = struct.unpack_from('<H', body, off2)[0]; off2 += 2
            end_str = body.index(b'\x00', off2)
            name = body[off2:end_str].decode('utf-8', errors='replace'); off2 = end_str+1
            sym_class[name] = cid
            sym_class[cid] = name
        break

# Find blackmage root sprite
root_cid = sym_class.get('black_mage', None)
print(f"root sprite charId: {root_cid}")

# Find dair bitmaps
dair_names = [n for n in sym_class if isinstance(n, str) and 'dair' in n.lower()]
print(f"\nDair-related exports: {sorted(dair_names)}")
for n in sorted(dair_names):
    cid = sym_class[n]
    tt = char_types.get(cid, 'MISSING')
    print(f"  {n}: charId={cid}, type={tt}")

# Find parent sprite of dair bitmaps by scanning all sprite sub-tags
print(f"\nScanning sprites for dair bitmaps...")
dair_cids = {sym_class[n] for n in dair_names if n in sym_class}
print(f"  Dair charIds: {sorted(dair_cids)}")

# Scan all sprites for PO3 with hasCharacter pointing to dair cids
for sprite_cid, (abs_off, body) in sprite_tags.items():
    frame_count = struct.unpack_from('<H', body, 0)[0]
    sub_start = 4  # skip charId(2) + frameCount(2)
    found = []
    sub_off = sub_start
    while sub_off < len(body):
        if sub_off+2 > len(body): break
        shdr = struct.unpack_from('<H', body, sub_off)[0]; stt=shdr>>6; sln=shdr&0x3F; sh_sz=2; sub_off+=2
        if sln==0x3F:
            sln=struct.unpack_from('<I', body, sub_off)[0]; sub_off+=4; sh_sz=6
        sub_body = body[sub_off:sub_off+sln]
        if stt == 70 and len(sub_body) >= 6:  # PO3
            flags = struct.unpack_from('<H', sub_body, 0)[0]
            if flags & 0x02:  # has character
                depth = struct.unpack_from('<H', sub_body, 2)[0]
                ref_cid = struct.unpack_from('<H', sub_body, 4)[0]
                if ref_cid in dair_cids:
                    found.append((depth, ref_cid, sym_class.get(ref_cid, '?')))
        elif stt == 26 and len(sub_body) >= 5:  # PO2
            flags = sub_body[0]
            if flags & 0x02:
                depth = struct.unpack_from('<H', sub_body, 1)[0]
                ref_cid = struct.unpack_from('<H', sub_body, 3)[0]
                if ref_cid in dair_cids:
                    found.append((depth, ref_cid, sym_class.get(ref_cid, '?')))
        sub_off += sln
        if stt == 0: break
    if found:
        sname = sym_class.get(sprite_cid, f'<noname>')
        stype = char_types.get(sprite_cid, 'MISSING')
        print(f"\n  Sprite charId={sprite_cid} ({sname}) TT={stype}:")
        for depth, cid, name in found:
            exists = 'OK' if cid in char_types else 'MISSING'
            print(f"    depth={depth} → charId={cid} ({name}) → {exists}")
