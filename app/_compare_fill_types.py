"""Compare shapes using N2D CID mapping to correctly match original ↔ roundtrip shapes."""
import struct, sys, os, zlib, zipfile, msgpack
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swf_binary_io import BitReader

ORIG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf"
RT = "test_swfs/lloyd_rt.swf"
N2D = "test_swfs/lloyd.n2d"

SHAPE_TAG_IDS = {2, 22, 32, 83}

def read_swf_data(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:3] == b'CWS':
        data = data[:8] + zlib.decompress(data[8:])
    elif data[:3] == b'ZWS':
        import lzma
        data = data[:8] + lzma.decompress(data[12:])
    return data

def parse_tags_by_cid(data):
    """Parse SWF and return dict of CID → (tag_type, body) for shape tags."""
    pos = 8
    nbits = (data[pos] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    pos += (total_bits + 7) // 8 + 4
    shapes = {}
    while pos < len(data) - 1:
        hdr = struct.unpack_from('<H', data, pos)[0]
        tag_type = hdr >> 6
        length = hdr & 0x3F
        pos += 2
        if length == 0x3F:
            length = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        body = data[pos:pos+length]
        if tag_type in SHAPE_TAG_IDS and len(body) >= 2:
            cid = struct.unpack_from('<H', body, 0)[0]
            shapes[cid] = (tag_type, body)
        pos += length
        if tag_type == 0: break
    return shapes

def parse_fill_type(body, tag_type):
    """Get fill type byte for the first bitmap fill, or 'solid'/'gradient'."""
    try:
        br = BitReader(body, 0)
        br.read_ui16()  # CID
        nb = br.read_ub(5)
        for _ in range(4): br.read_sb(nb)
        br.align()
        if tag_type == 83:
            nb2 = br.read_ub(5)
            for _ in range(4): br.read_sb(nb2)
            br.align()
            br.read_ub(8)
        nfills = br.read_ui8()
        if nfills == 0xFF: nfills = br.read_ui16()
        use_rgba = tag_type in (32, 83)
        fills = []
        for _ in range(nfills):
            ft = br.read_ui8()
            fills.append(ft)
            if ft == 0x00:
                br.read_ui8(); br.read_ui8(); br.read_ui8()
                if use_rgba: br.read_ui8()
            elif ft in (0x10, 0x12, 0x13):
                return nfills, fills, 'gradient'
            elif ft in (0x40, 0x41, 0x42, 0x43):
                br.read_ui16()
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
                return nfills, fills, f'unknown_{ft:#x}'
        return nfills, fills, 'ok'
    except Exception as e:
        return -1, [], f'error: {e}'

# Load N2D to build the CID mapping
with zipfile.ZipFile(N2D) as z:
    with z.open("project.msgpack") as mf:
        project = msgpack.unpack(mf, raw=False)
libs = project.get('libraries', [])

# Build mapping: original swfCharId → N2D lib id → roundtrip swfCharId
# We need to simulate the char ID allocation
from compile_n2d import N2DCompiler
import io as _io
compiler = N2DCompiler.__new__(N2DCompiler)
# Minimal setup for ID allocation
compiler._next_char_id = 1
compiler._lib_to_swf_id = {}
compiler._swf_id_to_lib = {}

# Actually, let me just load the lloyd.n2d properly
# The simplest approach: parse both SWFs, then for each N2D shape lib entry,
# find it by original CID in original SWF, and by looking for the RT CID.

# Load both SWFs
orig_shapes = parse_tags_by_cid(read_swf_data(ORIG))
rt_shapes = parse_tags_by_cid(read_swf_data(RT))

# For each shape in N2D, get swfCharId and match to original
# For roundtrip match, we need to know the new CID assigned.
# compile_n2d assigns CIDs sequentially. Let's find them by matching shape properties.

# Simpler approach: just compare the fill type bytes for all RT shapes' fill types
# and count how many match expected values

# Check all RT shapes
print(f"Original: {len(orig_shapes)} shapes")
print(f"Roundtrip: {len(rt_shapes)} shapes")

# Collect all shapes in RT by index order (emission order)
rt_data = read_swf_data(RT)
pos = 8
nbits = (rt_data[pos] >> 3) & 0x1F
total_bits = 5 + nbits * 4
pos += (total_bits + 7) // 8 + 4
rt_ordered = []
while pos < len(rt_data) - 1:
    hdr = struct.unpack_from('<H', rt_data, pos)[0]
    tag_type = hdr >> 6
    length = hdr & 0x3F
    pos += 2
    if length == 0x3F:
        length = struct.unpack_from('<I', rt_data, pos)[0]
        pos += 4
    body = rt_data[pos:pos+length]
    if tag_type in SHAPE_TAG_IDS and len(body) >= 2:
        cid = struct.unpack_from('<H', body, 0)[0]
        rt_ordered.append((tag_type, cid, body))
    pos += length
    if tag_type == 0: break

# For each N2D shape, find its bitmap fill properties, 
# then check the corresponding RT shape
n2d_shapes = [lib for lib in libs if lib.get('type') == 'shape' and not lib.get('endRecodes')]

# We need the RT CID for each N2D shape
# compile_n2d.py allocates CIDs sequentially. Let me trace the allocation order.
# Actually, the simplest approach: count bitmap filled shapes in RT and check their fill types

bitmap_ft_counts = {0x40: 0, 0x41: 0, 0x42: 0, 0x43: 0}
solid_count = 0
gradient_count = 0

for tag_type, cid, body in rt_ordered:
    nfills, fills, status = parse_fill_type(body, tag_type)
    bmp_fills = [f for f in fills if f in (0x40, 0x41, 0x42, 0x43)]
    solid_fills = [f for f in fills if f == 0x00]
    grad_fills = [f for f in fills if f in (0x10, 0x12, 0x13)]
    
    for f in bmp_fills:
        bitmap_ft_counts[f] += 1
    if solid_fills: solid_count += 1
    if 'gradient' in status: gradient_count += 1

print(f"\nRoundtrip bitmap fill type distribution:")
print(f"  0x40 (repeating, smoothed):    {bitmap_ft_counts[0x40]}")
print(f"  0x41 (clipped, smoothed):      {bitmap_ft_counts[0x41]}")
print(f"  0x42 (repeating, non-smoothed): {bitmap_ft_counts[0x42]}")
print(f"  0x43 (clipped, non-smoothed):  {bitmap_ft_counts[0x43]}")
print(f"  solid fills: {solid_count}")
print(f"  gradient fills: {gradient_count}")

# Same for original
orig_ft_counts = {0x40: 0, 0x41: 0, 0x42: 0, 0x43: 0}
o_solid = 0
o_gradient = 0
for cid, (tag_type, body) in orig_shapes.items():
    nfills, fills, status = parse_fill_type(body, tag_type)
    bmp_fills = [f for f in fills if f in (0x40, 0x41, 0x42, 0x43)]
    solid_fills = [f for f in fills if f == 0x00]
    for f in bmp_fills:
        orig_ft_counts[f] += 1
    if solid_fills: o_solid += 1
    if 'gradient' in status: o_gradient += 1

print(f"\nOriginal bitmap fill type distribution:")
print(f"  0x40 (repeating, smoothed):    {orig_ft_counts[0x40]}")
print(f"  0x41 (clipped, smoothed):      {orig_ft_counts[0x41]}")
print(f"  0x42 (repeating, non-smoothed): {orig_ft_counts[0x42]}")
print(f"  0x43 (clipped, non-smoothed):  {orig_ft_counts[0x43]}")
print(f"  solid fills: {o_solid}")
print(f"  gradient fills: {o_gradient}")

# Check: every 0x41 in original should produce 0x41 in RT, etc.
# Total bitmap fills should match (minus dummy fills)
print(f"\nOriginal total bitmap fills: {sum(orig_ft_counts.values())}")
print(f"Roundtrip total bitmap fills: {sum(bitmap_ft_counts.values())}")
