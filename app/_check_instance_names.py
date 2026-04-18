"""
Parse the actual instance name string from PO2 tags at depth=7 in black_mage.
We need to read past the matrix/cxform/ratio to find the name string.
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

def read_matrix_bits(data, bit_off):
    """Skip over a SWF MATRIX and return new bit offset."""
    # HasScaleFlag
    bi = bit_off // 8; bmod = bit_off % 8
    has_scale = (data[bi] >> (7 - bmod)) & 1
    bit_off += 1
    if has_scale:
        # NScaleBits (5 bits)
        n = 0
        for i in range(5):
            bi2 = (bit_off + i) // 8; bmod2 = (bit_off + i) % 8
            n = (n << 1) | ((data[bi2] >> (7 - bmod2)) & 1)
        bit_off += 5 + 2 * n  # ScaleX + ScaleY
    # HasRotateFlag
    bi = bit_off // 8; bmod = bit_off % 8
    has_rot = (data[bi] >> (7 - bmod)) & 1
    bit_off += 1
    if has_rot:
        n = 0
        for i in range(5):
            bi2 = (bit_off + i) // 8; bmod2 = (bit_off + i) % 8
            n = (n << 1) | ((data[bi2] >> (7 - bmod2)) & 1)
        bit_off += 5 + 2 * n
    # NTranslateBits (5 bits)
    n = 0
    for i in range(5):
        bi2 = (bit_off + i) // 8; bmod2 = (bit_off + i) % 8
        n = (n << 1) | ((data[bi2] >> (7 - bmod2)) & 1)
    bit_off += 5 + 2 * n  # TranslateX + TranslateY
    # Align to byte
    if bit_off % 8 != 0:
        bit_off += (8 - bit_off % 8)
    return bit_off // 8

def read_cxform_rgba_bytes(data, off):
    """Skip CXFORMWITHALPHA at byte offset. Returns new offset."""
    # CXFORMWITHALPHA: first byte has flags in high nibble
    if off >= len(data): return off
    b = data[off]
    # Bits 7,6,5,4 of first byte (partially): HasAddTerms, HasMultTerms, NbitsHigh...
    # Actually SWF CXFORMWITHALPHA is a bitfield
    # Bit 7 (MSB of first byte after alignment): HasAddTerms
    # Bit 6: HasMultTerms
    # Bits 5-2: Nbits (4 bits)
    # Then mult/add terms
    has_add = (b >> 7) & 1
    has_mult = (b >> 6) & 1
    nbits = ((b >> 2) & 0xF)
    import math
    bit_off_start_bits = off * 8 + 8  # after first byte
    nterms = (4 if has_mult else 0) + (4 if has_add else 0)
    total_bits = 8 + nterms * nbits
    total_bits_aligned = total_bits + (8 - total_bits % 8) % 8
    return off + total_bits_aligned // 8

def parse_po2_full(d):
    """Parse PO2 tag and return (depth, cid, name) or best effort."""
    if len(d) < 3: return None, None, None
    flags = d[0]
    has_move = bool(flags & 0x01)
    has_char = bool(flags & 0x02)
    has_matrix = bool(flags & 0x04)
    has_cxform = bool(flags & 0x08)
    has_ratio = bool(flags & 0x10)
    has_name = bool(flags & 0x20)
    
    depth = struct.unpack_from('<H', d, 1)[0]
    off = 3
    cid = None
    if has_char and off+2 <= len(d):
        cid = struct.unpack_from('<H', d, off)[0]; off += 2
    
    if has_matrix:
        try:
            off = read_matrix_bits(d, off * 8) # returns byte offset
        except:
            return depth, cid, '?'
    
    if has_cxform:
        try:
            off = read_cxform_rgba_bytes(d, off)
        except:
            return depth, cid, '?'
    
    if has_ratio:
        off += 2  # UI16 ratio
    
    if has_name and off < len(d):
        try:
            null = d.index(b'\x00', off)
            name = d[off:null].decode('utf-8', 'r')
            return depth, cid, name
        except:
            return depth, cid, 'decode_error'
    
    return depth, cid, None

def get_sprite_bytes(data, target_cid):
    off = skip_hdr(data)
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        d=data[off:off+ln]; off+=ln
        if tt==39 and len(d)>=4 and struct.unpack_from('<H',d,0)[0]==target_cid:
            return d[4:]
        if tt==0: break
    return None

def get_sym(data):
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
    return sym

for label, path, main_cid in [('OG', OG_PATH, 1556), ('RT', RT_PATH, 873)]:
    data = read_swf(path)
    sym = get_sym(data)
    cid_to_name = {v:k for k,v in sym.items()}
    
    spr = get_sprite_bytes(data, main_cid)
    if not spr: continue
    
    # Find the PO2 that places DAir_73 and get its name
    dair_cid = sym.get('blackmage_fla.DAir_73')
    
    print(f"\n[{label}] Checking PO2 instance names at depth=7 in black_mage cid={main_cid}:")
    print(f"  DAir_73 cid={dair_cid}")
    
    off = 0
    count = 0
    while off < len(spr) and count < 15:
        if off+2 > len(spr): break
        hdr=struct.unpack_from('<H',spr,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',spr,off)[0]; off+=4
        d=spr[off:off+ln]; off+=ln
        if tt == 26:
            depth, cid, name = parse_po2_full(d)
            if depth == 7 and cid:
                nm = cid_to_name.get(cid, '<anon>')
                print(f"  PO2 depth=7 cid={cid}[{nm}] name='{name}'")
                count += 1
        if tt == 0: break
    
    # Also check depths 1, 3, 5
    print(f"\n  PO2 instance names at depths 1,3,5 (first 3 each):")
    for tgt_depth in [1, 3, 5]:
        off = 0
        count2 = 0
        while off < len(spr) and count2 < 3:
            if off+2 > len(spr): break
            hdr=struct.unpack_from('<H',spr,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
            if ln==0x3F: ln=struct.unpack_from('<I',spr,off)[0]; off+=4
            d=spr[off:off+ln]; off+=ln
            if tt == 26:
                depth, cid, name = parse_po2_full(d)
                if depth == tgt_depth and cid:
                    nm = cid_to_name.get(cid, '<anon>')
                    print(f"  PO2 depth={tgt_depth} cid={cid}[{nm}] name='{name}'")
                    count2 += 1
            if tt == 0: break
