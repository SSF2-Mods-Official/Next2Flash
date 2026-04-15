"""Compare shape edge structure: original SWF vs roundtrip, matched by N2D swfCharId.

For each shape, compare: edge count, fill count, line count, total size.
Identify shapes with significant structural differences.
"""
import struct, zlib, os, sys, zipfile, msgpack
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swf_binary_io import BitReader

def iter_tags(path):
    with open(path, 'rb') as f:
        sig = f.read(3); f.read(1)
        struct.unpack('<I', f.read(4))[0]; rest = f.read()
    if sig == b'CWS':
        rest = zlib.decompress(rest)
    nbits = (rest[0] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    pos = rect_bytes + 4
    idx = 0
    while pos < len(rest):
        tc = struct.unpack_from('<H', rest, pos)[0]; pos += 2
        tt = tc >> 6; ll = tc & 0x3F
        if ll == 0x3F:
            ll = struct.unpack_from('<I', rest, pos)[0]; pos += 4
        body = rest[pos:pos+ll]; pos += ll
        yield idx, tt, body
        idx += 1

def count_shape_parts(body, tag_type):
    """Count fills, lines, edges, style-changes in a shape tag."""
    cid = struct.unpack_from('<H', body, 0)[0]
    br = BitReader(body, 2)
    
    # Skip shape bounds
    nb = br.read_ub(5)
    for _ in range(4): br.read_sb(nb)
    br.align()
    
    if tag_type == 83:
        # Skip edge bounds + flags
        nb2 = br.read_ub(5)
        for _ in range(4): br.read_sb(nb2)
        br.align()
        br.read_ui8()
    
    # Count fill styles
    try:
        fc = br.read_ui8()
        if fc == 0xFF:
            fc = br.read_ui16()
        
        # Skip fill style bodies (rough - just count)
        for _ in range(fc):
            ft = br.read_ui8()
            if ft == 0x00:
                # Solid: RGB (tag 2,22) or RGBA (tag 32,83)
                br.byte_pos += 3 if tag_type in (2, 22) else 4
            elif ft in (0x10, 0x12, 0x13):
                # Gradient
                hs = br.read_ub(1)
                if hs:
                    nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                hr = br.read_ub(1)
                if hr:
                    nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                br.align()
                sp = br.read_ui8() if ft == 0x13 else 0  # spreadMode+interpolation+numGradients packed
                if ft == 0x13:
                    # FocalGradient
                    ng = sp & 0x0F  # Wait, this is wrong. Let me just bail out for complex fills
                    raise ValueError("complex gradient")
                ng = br.read_ui8()
                # Each gradient record: ratio(1) + color(3 or 4)
                cs = 3 if tag_type in (2, 22) else 4
                br.byte_pos += ng * (1 + cs)
            elif ft in (0x40, 0x41, 0x42, 0x43):
                br.byte_pos += 2  # bitmap ID
                hs = br.read_ub(1)
                if hs:
                    nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                hr = br.read_ub(1)
                if hr:
                    nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                br.align()
            else:
                raise ValueError(f"unknown fill 0x{ft:02X}")
        
        # Count line styles
        lc = br.read_ui8()
        if lc == 0xFF:
            lc = br.read_ui16()
        
        if tag_type in (2, 22):
            br.byte_pos += lc * (2 + 3)  # width + RGB
        elif tag_type == 32:
            br.byte_pos += lc * (2 + 4)  # width + RGBA
        else:
            # DefineShape4 - LineStyle2
            for _ in range(lc):
                br.byte_pos += 2  # width
                flags = struct.unpack_from('<H', body, br.byte_pos)[0]
                br.byte_pos += 2
                join = (flags >> 2) & 3
                has_fill = (flags >> 4) & 1
                if join == 2:
                    br.byte_pos += 2
                if has_fill:
                    raise ValueError("linestyle2 with fill")
                else:
                    br.byte_pos += 4  # RGBA
        
        # Edge records
        sfb = br.read_ub(4)
        slb = br.read_ub(4)
        
        edges = 0
        style_changes = 0
        new_styles = 0
        while True:
            tf = br.read_ub(1)
            if tf == 1:
                sf = br.read_ub(1)
                if sf:
                    nb = br.read_ub(4) + 2
                    gf = br.read_ub(1)
                    if gf:
                        br.read_sb(nb); br.read_sb(nb)
                    else:
                        br.read_ub(1); br.read_sb(nb)
                else:
                    nb = br.read_ub(4) + 2
                    br.read_sb(nb); br.read_sb(nb); br.read_sb(nb); br.read_sb(nb)
                edges += 1
            else:
                flags = br.read_ub(5)
                if flags == 0:
                    break
                has_move = flags & 1
                has_f0 = (flags >> 1) & 1
                has_f1 = (flags >> 2) & 1
                has_ln = (flags >> 3) & 1
                has_new = (flags >> 4) & 1
                if has_move:
                    mb = br.read_ub(5)
                    br.read_sb(mb); br.read_sb(mb)
                if has_f0:
                    br.read_ub(sfb)
                if has_f1:
                    br.read_ub(sfb)
                if has_ln:
                    br.read_ub(slb)
                if has_new:
                    new_styles += 1
                    # New style array - need to read fill styles + line styles
                    nfc = br.read_ui8()
                    if nfc == 0xFF:
                        nfc = br.read_ui16()
                    # Skip them... this is getting complex. Just bail.
                    raise ValueError("new styles in shape")
                style_changes += 1
        
        return {
            'cid': cid, 'tag': tag_type, 'fills': fc, 'lines': lc,
            'edges': edges, 'style_changes': style_changes, 'size': len(body)
        }
    except Exception as e:
        return {
            'cid': cid, 'tag': tag_type, 'size': len(body),
            'error': str(e)
        }

# Load N2D to get charId mapping
n2d_path = os.path.join(os.path.dirname(__file__), "test_swfs", "lloyd.n2d")
with zipfile.ZipFile(n2d_path) as z:
    with z.open("project.msgpack") as f:
        proj = msgpack.unpack(f, raw=False)

libs = proj.get("libraries", [])

# Get the compile-time char ID assignment order (from compile_n2d.py)
# We need to know which original swfCharId maps to which roundtrip charId.
# The N2D stores swfCharId for reference. The compile assigns new sequential IDs.
# For now, just map by swfCharId.

n2d_shapes = {}  # swfCharId -> n2d_id
for lib in libs:
    if lib.get("type") == "shape" and "endRecodes" not in lib:
        swf_cid = lib.get("swfCharId", lib.get("characterId", -1))
        n2d_shapes[swf_cid] = lib.get("id", -1)

orig = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf"
rt = os.path.join(os.path.dirname(__file__), "test_swfs", "lloyd_rt.swf")

# Parse all shapes
orig_by_cid = {}
for idx, tt, body in iter_tags(orig):
    if tt in (2, 22, 32, 83):
        info = count_shape_parts(body, tt)
        orig_by_cid[info['cid']] = info

rt_by_cid = {}
for idx, tt, body in iter_tags(rt):
    if tt in (2, 22, 32, 83):
        info = count_shape_parts(body, tt)
        rt_by_cid[info['cid']] = info

# We need to match: for each original shape (by swfCharId), find the corresponding
# roundtrip shape. The compile_n2d assigns new IDs, so we need the mapping.
# Let me just read compile output to infer it, or compare by ordinal in definition order.

# Actually, let's use a different approach: match by N2D library order since that's the
# definition order in the output SWF.
# Collect shapes in definition order from both SWFs
orig_shapes_ordered = []
for idx, tt, body in iter_tags(orig):
    if tt in (2, 22, 32, 83):
        cid = struct.unpack_from('<H', body, 0)[0]
        orig_shapes_ordered.append((cid, count_shape_parts(body, tt)))

rt_shapes_ordered = []
for idx, tt, body in iter_tags(rt):
    if tt in (2, 22, 32, 83):
        cid = struct.unpack_from('<H', body, 0)[0]
        rt_shapes_ordered.append((cid, count_shape_parts(body, tt)))

# Match N2D shapes to rt shapes by getting the n2d order
n2d_ordered = []  # (swfCharId, n2d_id)
for lib in libs:
    if lib.get("type") == "shape" and "endRecodes" not in lib:
        n2d_ordered.append((lib.get("swfCharId", -1), lib.get("id", -1)))

# The roundtrip shapes should be in the same order as N2D definition order
# N2D shapes are defined in library order
print(f"Original shapes: {len(orig_shapes_ordered)}")
print(f"Roundtrip shapes: {len(rt_shapes_ordered)}")
print(f"N2D shapes: {len(n2d_ordered)}")

# Let's just compare orig vs rt by ordinal and flag differences
print(f"\n{'='*80}")
print(f"Shape comparison (ordinal matching)")
print(f"{'='*80}")

different = []
errored = []
for i in range(min(len(orig_shapes_ordered), len(rt_shapes_ordered))):
    o_cid, o = orig_shapes_ordered[i]
    r_cid, r = rt_shapes_ordered[i]
    
    if 'error' in o or 'error' in r:
        errored.append((i, o_cid, r_cid, o.get('error', ''), r.get('error', '')))
        continue
    
    # Compare structure
    diffs = []
    if o.get('fills') != r.get('fills'):
        diffs.append(f"fills: {o['fills']}->{r['fills']}")
    if o.get('lines') != r.get('lines'):
        diffs.append(f"lines: {o['lines']}->{r['lines']}")
    if o.get('edges') != r.get('edges'):
        diffs.append(f"edges: {o['edges']}->{r['edges']}")
    if o.get('style_changes') != r.get('style_changes'):
        diffs.append(f"SC: {o['style_changes']}->{r['style_changes']}")
    
    size_ratio = r['size'] / max(o['size'], 1)
    
    if diffs:
        different.append((i, o_cid, r_cid, o, r, diffs, size_ratio))

print(f"\nStructurally different: {len(different)}")
print(f"Parse errors: {len(errored)}")
print(f"Same structure: {len(orig_shapes_ordered) - len(different) - len(errored)}")

# Show different shapes sorted by impact
different.sort(key=lambda x: -abs(x[5][0].split('->')[1].split(')')[0] if 'edges' in x[5][0] else '0'))

print(f"\nDifferent shapes (edge/fill/line count differs):")
for i, o_cid, r_cid, o, r, diffs, ratio in different[:40]:
    d_str = ", ".join(diffs)
    print(f"  [{i:3d}] orig cid={o_cid:5d} tag={o['tag']} -> rt cid={r_cid:5d} tag={r['tag']}  size {o['size']:5d}->{r['size']:5d} ({ratio:.1f}x)  {d_str}")

if errored:
    print(f"\nShapes with parse errors:")
    for i, o_cid, r_cid, o_err, r_err in errored[:20]:
        err_str = f"orig:{o_err}" if o_err else f"rt:{r_err}"
        print(f"  [{i:3d}] orig cid={o_cid:5d} -> rt cid={r_cid:5d}  {err_str}")
