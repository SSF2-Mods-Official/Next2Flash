"""Compare regular (non-morph) shapes between original lloyd.ssf and roundtrip.

Strategy: Parse every DefineShape(1/2/3/4) tag from both SWFs, compare
edge records ordinal-by-ordinal. Focus on edge coordinates and fill/line
assignment to find which shapes differ.
"""
import struct, zlib, os, sys

def iter_tags(path):
    """Yield (tag_type, tag_body) for each tag in an SWF."""
    with open(path, 'rb') as f:
        sig = f.read(3)
        f.read(1)
        flen = struct.unpack('<I', f.read(4))[0]
        rest = f.read()
    if sig == b'CWS':
        rest = zlib.decompress(rest)
    nbits = (rest[0] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    pos = rect_bytes + 4
    while pos < len(rest):
        tc = struct.unpack_from('<H', rest, pos)[0]
        pos += 2
        tt = tc >> 6
        ll = tc & 0x3F
        if ll == 0x3F:
            ll = struct.unpack_from('<I', rest, pos)[0]
            pos += 4
        body = rest[pos:pos+ll]
        pos += ll
        yield tt, body

def get_shapes(path):
    """Return dict of {charId: (tag_type, body_bytes)} for all shape tags."""
    shapes = {}
    for tt, body in iter_tags(path):
        if tt in (2, 22, 32, 83):  # DefineShape 1-4
            cid = struct.unpack_from('<H', body, 0)[0]
            shapes[cid] = (tt, body)
    return shapes

def shape_body_hash(body):
    """Quick hash of shape body for fast comparison."""
    import hashlib
    return hashlib.md5(body).hexdigest()[:12]

orig = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf"
rt = os.path.join(os.path.dirname(__file__), "test_swfs", "lloyd_rt.swf")

print("Loading shapes...")
orig_shapes = get_shapes(orig)
rt_shapes = get_shapes(rt)
print(f"Original: {len(orig_shapes)} shapes")
print(f"Roundtrip: {len(rt_shapes)} shapes")

# Since char IDs don't match, we need to compare by ordinal.
# Collect shapes in order of appearance.
def get_shape_list(path):
    shapes = []
    for tt, body in iter_tags(path):
        if tt in (2, 22, 32, 83):
            cid = struct.unpack_from('<H', body, 0)[0]
            shapes.append((cid, tt, body))
    return shapes

orig_list = get_shape_list(orig)
rt_list = get_shape_list(rt)

print(f"\nOriginal shape count: {len(orig_list)}")
print(f"Roundtrip shape count: {len(rt_list)}")

# Quick body comparison - how many are byte-identical (ignoring charId and tag type)?
# Compare body after the charId (2 bytes) since charIds differ
same = 0
diff = 0
size_diffs = []
for i in range(min(len(orig_list), len(rt_list))):
    o_cid, o_tt, o_body = orig_list[i]
    r_cid, r_tt, r_body = rt_list[i]
    # Skip charId (first 2 bytes)
    if o_body[2:] == r_body[2:]:
        same += 1
    else:
        diff += 1
        o_size = len(o_body)
        r_size = len(r_body)
        pct = abs(o_size - r_size) / max(o_size, 1) * 100
        size_diffs.append((i, o_cid, r_cid, o_tt, r_tt, o_size, r_size, pct))

print(f"\nOrdinal comparison (body after charId):")
print(f"  Identical: {same}")
print(f"  Different: {diff}")

# Show the different ones sorted by size difference
if size_diffs:
    size_diffs.sort(key=lambda x: -x[7])  # sort by pct diff
    print(f"\nTop 30 most different shapes (by size):")
    print(f"  {'Idx':>4} {'O_CID':>6} {'R_CID':>6} {'O_Tag':>5} {'R_Tag':>5} {'O_Size':>7} {'R_Size':>7} {'Diff%':>6}")
    for idx, o_cid, r_cid, o_tt, r_tt, o_size, r_size, pct in size_diffs[:30]:
        print(f"  {idx:4d} {o_cid:6d} {r_cid:6d} {o_tt:5d} {r_tt:5d} {o_size:7d} {r_size:7d} {pct:5.1f}%")

# Tag type distribution
from collections import Counter
orig_tags = Counter(tt for _, tt, _ in orig_list)
rt_tags = Counter(tt for _, tt, _ in rt_list)
print(f"\nTag type distribution:")
print(f"  Original:  {dict(orig_tags)}")
print(f"  Roundtrip: {dict(rt_tags)}")

# Check tag type changes
tag_changes = Counter()
for i in range(min(len(orig_list), len(rt_list))):
    o_tt = orig_list[i][1]
    r_tt = rt_list[i][1]
    if o_tt != r_tt:
        tag_changes[(o_tt, r_tt)] += 1
if tag_changes:
    print(f"\nTag type changes: {dict(tag_changes)}")
