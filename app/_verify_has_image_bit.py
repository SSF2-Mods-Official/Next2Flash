"""Verify PlaceFlagHasImage (bit 4 of flags2 = 0x1000 in 16-bit) for dair bitmaps in RT."""
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

def parse_tags(data, start_off, end_off=None):
    off = start_off
    if end_off is None: end_off = len(data)
    while off < end_off:
        if off+2 > end_off: break
        hdr = struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; hdr_sz=2; off+=2
        if ln==0x3F:
            ln=struct.unpack_from('<I',data,off)[0]; off+=4; hdr_sz=6
        body = data[off:off+ln]
        yield tt, body, off-hdr_sz, ln
        off+=ln
        if tt==0: break

# Get SymbolClass
sym_class = {}
char_types = {}
sprite_bodies = {}
for tt, body, abs_off, ln in parse_tags(data, root_start):
    if tt == 76:
        count = struct.unpack_from('<H', body, 0)[0]
        off2 = 2
        for _ in range(count):
            cid = struct.unpack_from('<H', body, off2)[0]; off2 += 2
            end_str = body.index(b'\x00', off2)
            name = body[off2:end_str].decode('utf-8', errors='replace'); off2 = end_str+1
            sym_class[name] = cid; sym_class[cid] = name
    if len(body) >= 2:
        cid = struct.unpack_from('<H', body, 0)[0]
        char_types[cid] = tt
        if tt == 39:
            sprite_bodies[cid] = body

dair73_cid = sym_class.get('blackmage_fla.DAir_73')
print(f"DAir_73 charId: {dair73_cid}")

# Dair bitmap charIds
dair_bitmap_cids = {sym_class[n]: n for n in sym_class if isinstance(n, str) and 'bm_dair' in n.lower()}
print(f"Dair bitmap cids: {dair_bitmap_cids}")

body = sprite_bodies.get(dair73_cid, b'')
sub_off = 4
frame_num = 0
print(f"\n--- DAir_73 frame 1 PO3 tags with bitmap placements ---")
while sub_off < len(body):
    if sub_off+2 > len(body): break
    shdr = struct.unpack_from('<H', body, sub_off)[0]; stt=shdr>>6; sln=shdr&0x3F; sh_sz=2; sub_off+=2
    if sln==0x3F:
        sln=struct.unpack_from('<I', body, sub_off)[0]; sub_off+=4; sh_sz=6
    sub_body = body[sub_off:sub_off+sln]
    
    if stt == 1:  # ShowFrame
        frame_num += 1
        if frame_num >= 2:
            print("(end of frame 1)")
            break
    elif stt == 70 and len(sub_body) >= 6:  # PO3
        flags16 = struct.unpack_from('<H', sub_body, 0)[0]
        flags1 = flags16 & 0xFF
        flags2 = (flags16 >> 8) & 0xFF
        depth = struct.unpack_from('<H', sub_body, 2)[0]
        has_char = bool(flags1 & 0x02)
        has_image = bool(flags2 & 0x10)  # bit 4 of flags2
        cid = struct.unpack_from('<H', sub_body, 4)[0] if has_char else None
        cname = sym_class.get(cid, '') if cid else ''
        is_dair_bmp = cid in dair_bitmap_cids if cid else False
        if has_char:
            print(f"  PO3 depth={depth} charId={cid}({cname}) has_image={has_image} flags1=0x{flags1:02X} flags2=0x{flags2:02X}" + (" ← DAIR BITMAP" if is_dair_bmp else ""))
    
    sub_off += sln
    if stt == 0: break
