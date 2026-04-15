"""Deep dive into the most size-divergent shapes to understand what's happening."""
import struct, zlib, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swf_binary_io import BitReader

def iter_tags(path):
    with open(path, 'rb') as f:
        sig = f.read(3); f.read(1)
        flen = struct.unpack('<I', f.read(4))[0]; rest = f.read()
    if sig == b'CWS':
        rest = zlib.decompress(rest)
    nbits = (rest[0] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    pos = rect_bytes + 4
    while pos < len(rest):
        tc = struct.unpack_from('<H', rest, pos)[0]; pos += 2
        tt = tc >> 6; ll = tc & 0x3F
        if ll == 0x3F:
            ll = struct.unpack_from('<I', rest, pos)[0]; pos += 4
        body = rest[pos:pos+ll]; pos += ll
        yield tt, body

def parse_shape_header(body, tag_type):
    """Parse shape tag header: bounds, fill count, line count, edge count."""
    cid = struct.unpack_from('<H', body, 0)[0]
    br = BitReader(body, 2)
    
    # ShapeBounds
    nb = br.read_ub(5)
    xmin = br.read_sb(nb); xmax = br.read_sb(nb)
    ymin = br.read_sb(nb); ymax = br.read_sb(nb)
    br.align()
    bounds = (xmin, ymin, xmax, ymax)
    
    # DefineShape4 has edge bounds + flags
    if tag_type == 83:
        nb2 = br.read_ub(5)
        for _ in range(4): br.read_sb(nb2)
        br.align()
        br.read_ui8()  # flags
    
    # Fill styles
    try:
        fc = br.read_ui8()
        if fc == 0xFF:
            fc = br.read_ui16()
        # Skip fill style bodies
        for _ in range(fc):
            ft = br.read_ui8()
            if ft == 0x00:
                br.byte_pos += 4 if tag_type in (2, 22) else 4  # RGB or RGBA
                if tag_type in (32, 83): br.byte_pos += 0  # wait, need to check
                # DefineShape: RGB (3 bytes), DefineShape2: RGB, DefineShape3/4: RGBA (4 bytes)
                if tag_type in (2, 22):
                    pass  # already counted 4 -- but actually its 3 for RGB
                # This is getting complex. Let me just count edges differently.
                return {'cid': cid, 'bounds': bounds, 'fills': fc, 'tag': tag_type, 'size': len(body)}
            else:
                return {'cid': cid, 'bounds': bounds, 'fills': fc, 'tag': tag_type, 'size': len(body)}
    except:
        return {'cid': cid, 'bounds': bounds, 'fills': '?', 'tag': tag_type, 'size': len(body)}

def get_shape_list(path):
    shapes = []
    for tt, body in iter_tags(path):
        if tt in (2, 22, 32, 83):
            info = parse_shape_header(body, tt)
            if info is not None:
                info['body'] = body
                shapes.append(info)
    return shapes

orig = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf"
rt = os.path.join(os.path.dirname(__file__), "test_swfs", "lloyd_rt.swf")

orig_list = get_shape_list(orig)
rt_list = get_shape_list(rt)

# Build lookup by bounds for matching (bounds in twips should be preserved)
from collections import defaultdict

orig_by_bounds = defaultdict(list)
for i, s in enumerate(orig_list):
    orig_by_bounds[s['bounds']].append((i, s))

rt_by_bounds = defaultdict(list)
for i, s in enumerate(rt_list):
    rt_by_bounds[s['bounds']].append((i, s))

# Match shapes by bounds
matched = 0
unmatched_orig = []
size_issues = []

for bounds, orig_items in orig_by_bounds.items():
    rt_items = rt_by_bounds.get(bounds, [])
    if len(rt_items) == 0:
        for oi, os_ in orig_items:
            unmatched_orig.append(os_)
    elif len(orig_items) == 1 and len(rt_items) == 1:
        oi, os_ = orig_items[0]
        ri, rs_ = rt_items[0]
        o_size = os_['size']
        r_size = rs_['size']
        if abs(o_size - r_size) > max(o_size * 0.1, 20):
            size_issues.append((os_, rs_, o_size, r_size))
        matched += 1
    else:
        matched += min(len(orig_items), len(rt_items))

# Show unmatched
print(f"Bounds-matched: {matched}")
print(f"Unmatched original: {len(unmatched_orig)}")
print(f"Significant size differences: {len(size_issues)}")

if unmatched_orig:
    print(f"\nUnmatched original shapes (bounds not found in roundtrip):")
    for s in unmatched_orig[:20]:
        print(f"  cid={s['cid']:5d} tag={s['tag']} bounds={s['bounds']} size={s['size']}")

if size_issues:
    size_issues.sort(key=lambda x: -(x[3]/max(x[2],1)))
    print(f"\nBiggest size blowups (matched by bounds):")
    for os_, rs_, o_size, r_size in size_issues[:20]:
        ratio = r_size / max(o_size, 1)
        print(f"  orig cid={os_['cid']:5d} tag={os_['tag']} -> rt cid={rs_['cid']:5d} tag={rs_['tag']}  {o_size:6d} -> {r_size:6d} bytes ({ratio:.1f}x)  bounds={os_['bounds']}")

# Check how many unique bounds we have
print(f"\nUnique bounds: orig={len(orig_by_bounds)} rt={len(rt_by_bounds)}")
common = set(orig_by_bounds.keys()) & set(rt_by_bounds.keys())
print(f"Common bounds: {len(common)}")
