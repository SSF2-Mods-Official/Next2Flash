"""Trace specific shapes through the N2D pipeline to find where inaccuracy enters."""
import struct, zlib, os, sys, zipfile, msgpack
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

def read_rect(br):
    nb = br.read_ub(5)
    vals = [br.read_sb(nb) for _ in range(4)]
    br.align()
    return tuple(vals)

def get_all_shape_bounds(path):
    """Get {charId: (tag, bounds, size)} for all shapes."""
    result = {}
    for tt, body in iter_tags(path):
        if tt in (2, 22, 32, 83):
            cid = struct.unpack_from('<H', body, 0)[0]
            br = BitReader(body, 2)
            bounds = read_rect(br)
            result[cid] = (tt, bounds, len(body))
    return result

orig = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf"
rt = os.path.join(os.path.dirname(__file__), "test_swfs", "lloyd_rt.swf")
n2d = os.path.join(os.path.dirname(__file__), "test_swfs", "lloyd.n2d")

# Get original and roundtrip shapes
orig_shapes = get_all_shape_bounds(orig)
rt_shapes = get_all_shape_bounds(rt)

# Load N2D to get the mapping
with zipfile.ZipFile(n2d) as z:
    with z.open("project.msgpack") as f:
        proj = msgpack.unpack(f, raw=False)

libs = proj.get("libraries", [])

# Find shapes in N2D that have swfCharId matching original
shapes_in_n2d = []
for lib in libs:
    if lib.get("type") == "shape" and "endRecodes" not in lib:
        swf_cid = lib.get("swfCharId", lib.get("characterId", -1))
        recodes = lib.get("recodes", [])
        bounds = lib.get("bounds", {})
        shapes_in_n2d.append({
            'name': lib.get('name', '?'),
            'id': lib.get('id', -1),
            'swfCharId': swf_cid,
            'recode_len': len(recodes),
            'bounds': bounds,
        })

# Check how many original shapes have entries in N2D
n2d_swf_cids = {s['swfCharId'] for s in shapes_in_n2d}
orig_cids_in_n2d = set(orig_shapes.keys()) & n2d_swf_cids
print(f"Original shapes: {len(orig_shapes)}")
print(f"Roundtrip shapes: {len(rt_shapes)}")
print(f"N2D regular shapes: {len(shapes_in_n2d)}")
print(f"Original CIDs found in N2D: {len(orig_cids_in_n2d)}")
print(f"Not in N2D: {sorted(set(orig_shapes.keys()) - n2d_swf_cids)[:20]}")

# For shapes with same swfCharId, compare original bounds to N2D bounds
print("\n=== Shapes with bounds differences (orig vs N2D) ===")
n2d_by_swfcid = {s['swfCharId']: s for s in shapes_in_n2d}
for cid in sorted(orig_cids_in_n2d):
    o_tt, o_bounds, o_size = orig_shapes[cid]
    n = n2d_by_swfcid[cid]
    n_bounds = n['bounds']
    # N2D bounds are in pixels (twips/20), original in twips
    if isinstance(n_bounds, dict):
        n_twips = (
            round(n_bounds.get('xMin', 0) * 20),
            round(n_bounds.get('yMin', 0) * 20),
            round(n_bounds.get('xMax', 0) * 20),
            round(n_bounds.get('yMax', 0) * 20),
        )
    elif isinstance(n_bounds, (list, tuple)) and len(n_bounds) == 4:
        n_twips = tuple(round(v * 20) for v in n_bounds)
    else:
        n_twips = (0, 0, 0, 0)
    
    # Check if bounds match within tolerance
    if any(abs(a - b) > 1 for a, b in zip(o_bounds, n_twips)):
        print(f"  cid={cid:5d} orig_bounds={o_bounds} n2d_bounds_twips={n_twips}")
