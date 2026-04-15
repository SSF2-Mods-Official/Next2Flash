"""Compare ALL shapes between original lloyd.ssf and lloyd_rt.swf.
Identify categories of differences to understand what's fixed and what remains."""
import struct, sys, os, zlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swf_binary_io import BitReader

ORIG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf"
RT   = "test_swfs/lloyd_rt.swf"

SHAPE_TAG_IDS = {2, 22, 32, 83}

def read_swf_data(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:3] == b'CWS':
        flen = struct.unpack_from('<I', data, 4)[0]
        data = data[:8] + zlib.decompress(data[8:])
    elif data[:3] == b'ZWS':
        import lzma
        flen = struct.unpack_from('<I', data, 4)[0]
        data = data[:8] + lzma.decompress(data[12:])
    return data

def parse_tags(data):
    pos = 8
    nbits = (data[pos] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    pos += rect_bytes + 4
    tags = []
    while pos < len(data) - 1:
        hdr = struct.unpack_from('<H', data, pos)[0]
        tag_type = hdr >> 6
        length = hdr & 0x3F
        pos += 2
        if length == 0x3F:
            length = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        body = data[pos:pos+length]
        tags.append((tag_type, body))
        pos += length
        if tag_type == 0: break
    return tags

def parse_shape_header(body, tag_type):
    """Parse shape header and return fill info."""
    try:
        br = BitReader(body, 0)
        cid = br.read_ui16()
        
        # Bounds RECT
        nb = br.read_ub(5)
        for _ in range(4): br.read_sb(nb)
        br.align()
        
        # DefineShape4 extras
        if tag_type == 83:
            nb2 = br.read_ub(5)
            for _ in range(4): br.read_sb(nb2)
            br.align()
            br.read_ub(8)  # flags
        
        # Fill styles
        use_rgba = tag_type in (32, 83)
        nfills = br.read_ui8()
        if nfills == 0xFF: nfills = br.read_ui16()
        
        fill_types = []
        for _ in range(nfills):
            ft = br.read_ui8()
            fill_types.append(ft)
            if ft == 0x00:  # Solid
                br.read_ui8(); br.read_ui8(); br.read_ui8()
                if use_rgba: br.read_ui8()
            elif ft in (0x10, 0x12, 0x13):  # Gradient
                return cid, nfills, fill_types, -1, 'gradient_skip'
            elif ft in (0x40, 0x41, 0x42, 0x43):  # Bitmap
                br.read_ui16()  # bitmapId
                # Matrix
                br.align()
                hs = br.read_ub(1)
                if hs:
                    n = br.read_ub(5); br.read_sb(n); br.read_sb(n)
                hr = br.read_ub(1)
                if hr:
                    n = br.read_ub(5); br.read_sb(n); br.read_sb(n)
                tn = br.read_ub(5); br.read_sb(tn); br.read_sb(tn)
                br.align()
            else:
                return cid, nfills, fill_types, -1, f'unknown_fill_{ft:#x}'
        
        # Line styles
        nlines = br.read_ui8()
        if nlines == 0xFF: nlines = br.read_ui16()
        
        return cid, nfills, fill_types, nlines, 'ok'
    except Exception as e:
        try:
            return cid, -1, [], -1, f'parse_error: {e}'
        except:
            return -1, -1, [], -1, f'parse_error: {e}'

# Load both SWFs
orig_data = read_swf_data(ORIG)
rt_data = read_swf_data(RT)

orig_tags = parse_tags(orig_data)
rt_tags = parse_tags(rt_data)

orig_shapes = [(tt, b) for tt, b in orig_tags if tt in SHAPE_TAG_IDS]
rt_shapes = [(tt, b) for tt, b in rt_tags if tt in SHAPE_TAG_IDS]

# Separate morphs (46, 84) vs regular  - wait, 46/84 not in SHAPE_TAG_IDS
# Let's also check morph shapes
morph_types = {46, 84}
orig_morphs = [(tt, b) for tt, b in orig_tags if tt in morph_types]
rt_morphs = [(tt, b) for tt, b in rt_tags if tt in morph_types]

print(f"Original: {len(orig_shapes)} regular shapes, {len(orig_morphs)} morph shapes")
print(f"Roundtrip: {len(rt_shapes)} regular shapes, {len(rt_morphs)} morph shapes")
print()

# Categorize differences
categories = {
    'identical': [],
    'tag_upgrade_only': [],  # Different tag type but same fills/edges
    'fill_count_diff': [],
    'fill_type_diff': [],
    'size_diff_minor': [],   # <10 bytes diff
    'size_diff_major': [],   # >10 bytes diff
    'parse_error': [],
    'gradient': [],
}

n = min(len(orig_shapes), len(rt_shapes))
for i in range(n):
    o_tt, o_body = orig_shapes[i]
    r_tt, r_body = rt_shapes[i]
    
    o_cid, o_nf, o_ft, o_nl, o_status = parse_shape_header(o_body, o_tt)
    r_cid, r_nf, r_ft, r_nl, r_status = parse_shape_header(r_body, r_tt)
    
    info = f"shape[{i}] orig_cid={o_cid} tag={o_tt}->{r_tt} size={len(o_body)}->{len(r_body)}"
    
    if o_body == r_body:
        categories['identical'].append(info)
        continue
    
    if 'error' in o_status or 'error' in r_status:
        categories['parse_error'].append(f"{info} ({o_status}/{r_status})")
        continue
    
    if 'gradient' in o_status or 'gradient' in r_status:
        categories['gradient'].append(info)
        continue
    
    # Check if fills match
    if o_nf != r_nf:
        categories['fill_count_diff'].append(f"{info} fills={o_nf}->{r_nf} types={o_ft}->{r_ft}")
        continue
    
    if o_ft != r_ft:
        categories['fill_type_diff'].append(f"{info} types={o_ft}->{r_ft}")
        continue
    
    # Same fills, but different body
    size_diff = abs(len(o_body) - len(r_body))
    if size_diff <= 10:
        categories['tag_upgrade_only'].append(info)
    else:
        categories['size_diff_major'].append(f"{info} diff={size_diff}")

print("="*70)
print("SHAPE COMPARISON SUMMARY")
print("="*70)
for cat, items in categories.items():
    print(f"\n{cat}: {len(items)}")
    for item in items[:10]:
        print(f"  {item}")
    if len(items) > 10:
        print(f"  ... and {len(items)-10} more")

# Specifically check fill type bytes for all bitmap-filled shapes
print("\n" + "="*70)
print("BITMAP FILL TYPE CHECK (all shapes with bitmap fills)")
print("="*70)
bmp_diffs = 0
bmp_ok = 0
for i in range(n):
    o_tt, o_body = orig_shapes[i]
    r_tt, r_body = rt_shapes[i]
    
    o_cid, o_nf, o_ft, o_nl, o_status = parse_shape_header(o_body, o_tt)
    r_cid, r_nf, r_ft, r_nl, r_status = parse_shape_header(r_body, r_tt)
    
    # Check bitmap fill types
    o_bmp = [f for f in o_ft if f in (0x40, 0x41, 0x42, 0x43)]
    r_bmp = [f for f in r_ft if f in (0x40, 0x41, 0x42, 0x43)]
    
    if o_bmp or r_bmp:
        # Find "real" bitmap fills (ignore dummy bitmapId=65535 fills)
        # Original may have dummy + real, roundtrip just has real
        # So compare the non-dummy fill types
        if o_bmp and r_bmp:
            # The last bitmap fill in original is the "real" one
            o_real = o_bmp[-1]
            r_real = r_bmp[-1] if r_bmp else None
            if o_real == r_real:
                bmp_ok += 1
            else:
                bmp_diffs += 1
                print(f"  MISMATCH shape[{i}] cid={o_cid}: orig={o_real:#x} rt={r_real:#x}")
        elif not r_bmp:
            print(f"  MISSING shape[{i}] cid={o_cid}: orig has bitmap fills {[f'{f:#x}' for f in o_bmp]}, rt has none")

print(f"\nBitmap fill types: {bmp_ok} matching, {bmp_diffs} mismatched")
