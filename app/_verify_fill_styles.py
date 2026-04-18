"""
Parse the actual FillStyle bytes from DefineShape3 bodies to verify 
whether they truly contain bitmap fill references to specific CIDs.
Proper SWF fill style parsing (not just byte search).
"""
import struct, zlib

OG_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"
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

def get_sym(data):
    off = skip_hdr(data); sym = {}
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

def parse_matrix_bytes(data, off):
    """Skip a SWF MATRIX starting at byte offset off, return new offset."""
    # Convert to bit-level and back
    bits = []
    # Read enough bytes for any matrix
    bit_off = off * 8
    
    def read_bit(bo):
        return (data[bo//8] >> (7 - bo%8)) & 1
    
    def read_bits(bo, n):
        val = 0
        for i in range(n):
            val = (val << 1) | read_bit(bo + i)
        return val
    
    def read_sbits(bo, n):
        val = read_bits(bo, n)
        if val >= (1 << (n-1)):
            val -= (1 << n)
        return val
    
    b = bit_off
    has_scale = read_bit(b); b += 1
    if has_scale:
        ns = read_bits(b, 5); b += 5
        b += 2 * ns
    has_rot = read_bit(b); b += 1
    if has_rot:
        nr = read_bits(b, 5); b += 5
        b += 2 * nr
    nt = read_bits(b, 5); b += 5
    b += 2 * nt
    # Align to byte
    if b % 8 != 0: b += (8 - b%8)
    return b // 8

def get_fill_bitmap_cids(tag_data, tag_type):
    """Parse a DefineShape* body and return a list of all bitmap CIDs in fill styles.
    tag_type: 2=DefineShape, 22=DefineShape2, 32=DefineShape3, 83=DefineShape4
    Returns list of (fill_type_byte, bitmap_cid)
    """
    bitmaps = []
    
    # tag_data starts with CharId (2) + ShapeBounds (rect, variable)
    # We need to skip the bounds to find the fill style array
    off = 2  # skip cid
    
    # Parse bounds RECT
    # RECT is bit-packed: 5-bit Nbits, then 4 signed fields
    # We just need to skip it
    bit_off = off * 8
    def rb(bo): return (tag_data[bo//8] >> (7 - bo%8)) & 1
    def rbits(bo, n):
        v=0
        for i in range(n): v=(v<<1)|rb(bo+i)
        return v
    nbits = rbits(bit_off, 5); bit_off += 5
    bit_off += 4 * nbits  # 4 fields of nbits each
    if bit_off % 8 != 0: bit_off += 8 - bit_off%8
    off = bit_off // 8
    
    # For DefineShape4, there's an EdgeBounds too (another RECT)
    if tag_type == 83:
        bit_off2 = off * 8
        nbits2 = rbits(bit_off2, 5); bit_off2 += 5
        bit_off2 += 4 * nbits2
        if bit_off2 % 8 != 0: bit_off2 += 8 - bit_off2%8
        off = bit_off2 // 8
        # Then 2 reserved bits
        off += 1  # just skip the flags byte
    
    # FillStyleArray
    if off >= len(tag_data): return bitmaps
    count = tag_data[off]; off += 1
    if count == 0xFF and off + 2 <= len(tag_data):
        count = struct.unpack_from('<H', tag_data, off)[0]; off += 2
    
    for i in range(count):
        if off >= len(tag_data): break
        fill_type = tag_data[off]; off += 1
        
        # FillStyle
        if fill_type == 0x00:  # Solid fill
            # RGBA (DefineShape3) or RGB (DefineShape/2)
            if tag_type == 32 or tag_type == 83:
                off += 4  # RGBA
            else:
                off += 3  # RGB
        elif fill_type in (0x10, 0x12, 0x13):  # Linear/Radial gradient
            # MATRIX + GRADIENT
            off = parse_matrix_bytes(tag_data, off)
            # Linear/Radial gradient: SpreadMode(2) + InterpolationMode(2) + NumGradients(4) bits
            # then NumGradients * (ratio:UI8 + color:RGBA)
            nmask = tag_data[off] & 0x0F
            ngrads = nmask
            off += 1
            for _ in range(ngrads):
                off += 5  # UI8 ratio + RGBA
        elif fill_type in (0x40, 0x41, 0x42, 0x43):  # Bitmap fill
            # BitmapId UI16 + MATRIX
            if off + 2 <= len(tag_data):
                bmp_cid = struct.unpack_from('<H', tag_data, off)[0]
                bitmaps.append((fill_type, bmp_cid))
            off += 2
            off = parse_matrix_bytes(tag_data, off)
        else:
            # Unknown fill type — stop parsing
            break
    
    return bitmaps

for label, path, shape_cids_to_check, target_bmp_cids in [
    ('OG', OG_PATH, [651, 669], [1002, 1003]),
    ('RT', RT_PATH, [521, 1006], [637, 638]),
]:
    data = read_swf(path)
    sym = get_sym(data)
    cid_to_name = {v:k for k,v in sym.items()}
    
    print(f"\n[{label}] Parsing fill styles of candidate DefineShape3 tags:")
    
    off = skip_hdr(data)
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        d=data[off:off+ln]; off+=ln
        if tt in (2,22,32,83) and len(d)>=2:
            cid=struct.unpack_from('<H',d,0)[0]
            if cid in shape_cids_to_check:
                nm = cid_to_name.get(cid,'<anon>')
                try:
                    fills = get_fill_bitmap_cids(d, tt)
                    bitmap_fills = [(ft,bc) for ft,bc in fills if bc in target_bmp_cids]
                    all_bitmap_fills = fills
                    print(f"  DefineShape cid={cid}[{nm}] TT={tt}:")
                    print(f"    ALL fill styles: {fills[:10]}")
                    print(f"    Target bitmap fills: {bitmap_fills}")
                    if not bitmap_fills:
                        print(f"    *** FALSE POSITIVE — no actual reference to target bitmaps ***")
                    else:
                        print(f"    *** REAL reference to target bitmaps ***")
                except Exception as e:
                    print(f"  DefineShape cid={cid}[{nm}] TT={tt}: PARSE ERROR: {e}")
        if tt==0: break
