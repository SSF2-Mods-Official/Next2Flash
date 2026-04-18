"""
Use the correct fill style parser to check which LL2 bitmaps truly have
NO DefineShape references (and would be 'PO3+HasImage only').
Compare OG vs RT.

Also verify parser correctness by checking a shape we KNOW references a bitmap.
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

def skip_matrix_bits(bit_off, data):
    def rb(bo): return (data[bo//8] >> (7-bo%8)) & 1
    def rbits(bo, n):
        v = 0
        for i in range(n): v = (v<<1) | rb(bo+i)
        return v
    b = bit_off
    hs = rb(b); b += 1
    if hs:
        ns = rbits(b,5); b += 5; b += 2*ns
    hr = rb(b); b += 1
    if hr:
        nr = rbits(b,5); b += 5; b += 2*nr
    nt = rbits(b,5); b += 5; b += 2*nt
    if b%8: b += 8-b%8
    return b

def skip_rect_bits(bit_off, data):
    def rb(bo): return (data[bo//8] >> (7-bo%8)) & 1
    def rbits(bo, n):
        v=0
        for i in range(n): v=(v<<1)|rb(bo+i)
        return v
    b = bit_off
    nb = rbits(b,5); b += 5; b += 4*nb
    if b%8: b += 8-b%8
    return b

def get_bitmap_fill_cids_from_shape(tag_data, tag_type):
    """Parse DefineShape*/DefineMorphShape* body, return list of bitmap CIDs in fill styles."""
    results = []
    
    # Skip CID
    off = 2
    
    # Skip ShapeBounds (RECT bit-packed)
    bit_off = off*8
    bit_off = skip_rect_bits(bit_off, tag_data)
    off = bit_off//8
    
    # DefineShape4: also has EdgeBounds RECT + 2 flag bytes
    if tag_type == 83:
        bit_off = off*8
        bit_off = skip_rect_bits(bit_off, tag_data)
        off = bit_off//8 + 1  # skip flags byte
    
    if off >= len(tag_data): return results
    
    # FillStyleArray count
    count = tag_data[off]; off += 1
    if count == 0xFF and off+2 <= len(tag_data):
        count = struct.unpack_from('<H', tag_data, off)[0]; off += 2
    
    for i in range(count):
        if off >= len(tag_data): break
        ft = tag_data[off]; off += 1
        if ft == 0x00:  # Solid
            off += 4 if tag_type in (32,83) else 3
        elif ft in (0x10, 0x12, 0x13):  # Gradient
            bit_off = off*8
            bit_off = skip_matrix_bits(bit_off, tag_data)
            off = bit_off//8
            if off >= len(tag_data): break
            ng = tag_data[off] & 0x0F; off += 1
            for _ in range(ng):
                off += 5  # ratio + RGBA
        elif ft in (0x40, 0x41, 0x42, 0x43):  # Bitmap fill
            if off+2 > len(tag_data): break
            bmp_cid = struct.unpack_from('<H', tag_data, off)[0]
            results.append(bmp_cid)
            off += 2
            bit_off = off*8
            bit_off = skip_matrix_bits(bit_off, tag_data)
            off = bit_off//8
        else:
            break  # unknown
    
    return results

def build_fill_index(data):
    """Build bitmap_cid -> [shape_cids] from ALL shape tags in file."""
    index = {}  # bitmap_cid -> set of shape_cids
    off = skip_hdr(data)
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        d=data[off:off+ln]; off+=ln
        if tt in (2,22,32,83) and len(d)>=2:
            shape_cid = struct.unpack_from('<H',d,0)[0]
            try:
                bmp_cids = get_bitmap_fill_cids_from_shape(d, tt)
                for bc in bmp_cids:
                    index.setdefault(bc, set()).add(shape_cid)
            except Exception:
                pass
        if tt==0: break
    return index

print("Building fill indices (this may take a moment)...")

for label, path in [('OG', OG_PATH), ('RT', RT_PATH)]:
    data = read_swf(path)
    sym = get_sym(data)
    cid_to_name = {v:k for k,v in sym.items()}
    
    fill_index = build_fill_index(data)
    
    # Get all LL2 bitmap cids
    all_ll2 = set()
    off = skip_hdr(data)
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        d=data[off:off+ln]; off+=ln
        if tt==36 and len(d)>=2:
            all_ll2.add(struct.unpack_from('<H',d,0)[0])
        if tt==0: break
    
    with_shape = {c for c in all_ll2 if c in fill_index}
    without_shape = {c for c in all_ll2 if c not in fill_index}
    
    print(f"\n[{label}] Total LL2: {len(all_ll2)}")
    print(f"  With real DefineShape fill references: {len(with_shape)}")
    print(f"  WITHOUT any DefineShape fill reference (PO3-only): {len(without_shape)}")
    
    # List some PO3-only bitmaps
    po3_only_names = [cid_to_name.get(c,'<anon>') for c in list(without_shape)[:15]]
    print(f"  Sample PO3-only bitmaps: {po3_only_names}")
    
    # Specifically check dair bitmaps
    dair_bitmaps = [(k,v) for k,v in sym.items() if 'dair' in k.lower() or 'scythe' in k.lower()]
    print(f"\n  DAir-related bitmaps:")
    for nm, cid in sorted(dair_bitmaps):
        in_shape = cid in fill_index
        shapes = list(fill_index.get(cid, []))
        print(f"    cid={cid} [{nm}]: has_shape={in_shape} shapes={shapes[:5]}")
    
    # Common PO3-only names between OG and RT
    if label == 'RT':
        data_og = read_swf(OG_PATH)
        sym_og = get_sym(data_og)
        fill_idx_og = build_fill_index(data_og)
        all_ll2_og = set()
        off_og = skip_hdr(data_og)
        while off_og < len(data_og):
            hdr=struct.unpack_from('<H',data_og,off_og)[0]; tt=hdr>>6; ln=hdr&0x3F; off_og+=2
            if ln==0x3F: ln=struct.unpack_from('<I',data_og,off_og)[0]; off_og+=4
            d=data_og[off_og:off_og+ln]; off_og+=ln
            if tt==36 and len(d)>=2:
                all_ll2_og.add(struct.unpack_from('<H',d,0)[0])
            if tt==0: break
        
        po3_only_og_names = {sym_og.get(c,'<anon>') for c in all_ll2_og if c not in fill_idx_og}
        po3_only_rt_names = {sym.get(c,'<anon>') for c in all_ll2 if c not in fill_index}
        
        only_in_rt = po3_only_rt_names - po3_only_og_names
        only_in_og = po3_only_og_names - po3_only_rt_names
        only_in_both = po3_only_rt_names & po3_only_og_names
        
        print(f"\n  Comparison OG vs RT PO3-only bitmaps (by name):")
        print(f"    PO3-only in BOTH OG and RT: {len(only_in_both)}")
        print(f"    PO3-only in OG but NOT RT: {len(only_in_og)}")
        print(f"    PO3-only in RT but NOT OG: {len(only_in_rt)} ← NEW in RT")
        if only_in_rt:
            print(f"    Sample names PO3-only NEW in RT: {list(only_in_rt)[:20]}")
