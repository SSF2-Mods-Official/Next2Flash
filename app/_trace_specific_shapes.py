"""Trace specific shapes (306, 183, 185, 188) through import→N2D→export pipeline.

For each target shape:
1. Parse original SWF edge records 
2. Find in N2D (recodes)
3. Parse roundtrip SWF edge records
4. Compare all three stages
"""
import struct, zlib, os, sys, zipfile, msgpack
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swf_binary_io import BitReader

TARGET_CIDS = [306, 183, 185, 188]

def read_swf(path):
    with open(path, 'rb') as f:
        sig = f.read(3); f.read(1)
        struct.unpack('<I', f.read(4))[0]; rest = f.read()
    if sig == b'CWS':
        rest = zlib.decompress(rest)
    nbits = (rest[0] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    pos = rect_bytes + 4
    tags = []
    while pos < len(rest):
        tc = struct.unpack_from('<H', rest, pos)[0]; pos += 2
        tt = tc >> 6; ll = tc & 0x3F
        if ll == 0x3F:
            ll = struct.unpack_from('<I', rest, pos)[0]; pos += 4
        body = rest[pos:pos+ll]; pos += ll
        tags.append((tt, body))
    return tags

def read_rect(br):
    nb = br.read_ub(5)
    vals = [br.read_sb(nb) for _ in range(4)]
    br.align()
    return vals  # xmin, xmax, ymin, ymax

def dump_shape_edges(body, tag_type, label=""):
    """Parse and dump all edge records from a shape tag body."""
    cid = struct.unpack_from('<H', body, 0)[0]
    br = BitReader(body, 2)
    
    bounds = read_rect(br)
    print(f"  Bounds: xmin={bounds[0]} xmax={bounds[1]} ymin={bounds[2]} ymax={bounds[3]}")
    
    if tag_type == 83:
        ebounds = read_rect(br)
        print(f"  EdgeBounds: {ebounds}")
        flags = br.read_ui8()
        print(f"  Flags: 0x{flags:02X}")
    
    # Fill styles
    fc = br.read_ui8()
    if fc == 0xFF:
        fc = br.read_ui16()
    
    fills = []
    for fi in range(fc):
        ft = br.read_ui8()
        if ft == 0x00:
            cs = 3 if tag_type in (2, 22) else 4
            color = body[br.byte_pos:br.byte_pos+cs]
            br.byte_pos += cs
            fills.append(f"solid({','.join(str(b) for b in color)})")
        elif ft in (0x10, 0x12, 0x13):
            # Matrix
            hs = br.read_ub(1)
            if hs:
                nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
            hr = br.read_ub(1)
            if hr:
                nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
            nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
            br.align()
            if ft == 0x13:
                # Focal gradient
                spread_interp = br.read_ui8()
                ng = spread_interp & 0x0F  # wrong but let's try
                # Actually, the format is: SpreadMode(2) InterpolationMode(2) NumGradients(4) 
                # packed in 1 byte... no wait. GRADIENT record:
                # SpreadMode: UB[2], InterpolationMode: UB[2], NumGradients: UB[4]
                # But we already read a byte... this is the packed byte
                ng = spread_interp & 0x0F
                cs = 3 if tag_type in (2, 22) else 4
                br.byte_pos += ng * (1 + cs)
                br.byte_pos += 2  # fixed8 focal point
                fills.append(f"focalGradient({ng}stops)")
            else:
                ng = br.read_ui8()
                cs = 3 if tag_type in (2, 22) else 4
                br.byte_pos += ng * (1 + cs)
                fills.append(f"gradient({ng}stops)")
        elif ft in (0x40, 0x41, 0x42, 0x43):
            bid = struct.unpack_from('<H', body, br.byte_pos)[0]
            br.byte_pos += 2
            hs = br.read_ub(1)
            if hs:
                nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
            hr = br.read_ub(1)
            if hr:
                nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
            nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
            br.align()
            fills.append(f"bitmap({bid},type=0x{ft:02X})")
        else:
            fills.append(f"UNKNOWN(0x{ft:02X})")
            return  # can't continue
    
    print(f"  Fills({fc}): {fills}")
    
    # Line styles
    lc = br.read_ui8()
    if lc == 0xFF:
        lc = br.read_ui16()
    
    lines = []
    if tag_type in (2, 22):
        for _ in range(lc):
            w = struct.unpack_from('<H', body, br.byte_pos)[0]; br.byte_pos += 2
            c = body[br.byte_pos:br.byte_pos+3]; br.byte_pos += 3
            lines.append(f"w={w} rgb({c[0]},{c[1]},{c[2]})")
    elif tag_type == 32:
        for _ in range(lc):
            w = struct.unpack_from('<H', body, br.byte_pos)[0]; br.byte_pos += 2
            c = body[br.byte_pos:br.byte_pos+4]; br.byte_pos += 4
            lines.append(f"w={w} rgba({c[0]},{c[1]},{c[2]},{c[3]})")
    else:  # 83
        for _ in range(lc):
            w = struct.unpack_from('<H', body, br.byte_pos)[0]; br.byte_pos += 2
            flags = struct.unpack_from('<H', body, br.byte_pos)[0]; br.byte_pos += 2
            join = (flags >> 2) & 3
            has_fill = (flags >> 4) & 1
            if join == 2:
                br.byte_pos += 2
            if has_fill:
                # Skip fill style for line
                lft = br.read_ui8()
                if lft == 0x00:
                    br.byte_pos += 4
                else:
                    lines.append(f"w={w} fillLine(COMPLEX)")
                    return
            else:
                c = body[br.byte_pos:br.byte_pos+4]; br.byte_pos += 4
                lines.append(f"w={w} rgba({c[0]},{c[1]},{c[2]},{c[3]})")
    
    print(f"  Lines({lc}): {lines}")
    
    # Shape records
    sfb = br.read_ub(4)
    slb = br.read_ub(4)
    print(f"  NumFillBits={sfb} NumLineBits={slb}")
    
    records = []
    cur_x, cur_y = 0, 0
    while True:
        tf = br.read_ub(1)
        if tf == 1:
            sf = br.read_ub(1)
            if sf:
                nb = br.read_ub(4) + 2
                gf = br.read_ub(1)
                if gf:
                    dx = br.read_sb(nb); dy = br.read_sb(nb)
                    cur_x += dx; cur_y += dy
                    records.append(f"Line({dx},{dy}) -> ({cur_x},{cur_y})")
                else:
                    vl = br.read_ub(1)
                    if vl:
                        dy = br.read_sb(nb)
                        cur_y += dy
                        records.append(f"LineV({dy}) -> ({cur_x},{cur_y})")
                    else:
                        dx = br.read_sb(nb)
                        cur_x += dx
                        records.append(f"LineH({dx}) -> ({cur_x},{cur_y})")
            else:
                nb = br.read_ub(4) + 2
                cdx = br.read_sb(nb); cdy = br.read_sb(nb)
                adx = br.read_sb(nb); ady = br.read_sb(nb)
                cx = cur_x + cdx; cy = cur_y + cdy
                ax = cx + adx; ay = cy + ady
                records.append(f"Curve ctrl=({cx},{cy}) anc=({ax},{ay})")
                cur_x = ax; cur_y = ay
        else:
            flags = br.read_ub(5)
            if flags == 0:
                records.append("END")
                break
            has_move = flags & 1
            has_f0 = (flags >> 1) & 1
            has_f1 = (flags >> 2) & 1
            has_ln = (flags >> 3) & 1
            has_new = (flags >> 4) & 1
            
            parts = ["SC"]
            if has_move:
                mb = br.read_ub(5)
                mx = br.read_sb(mb); my = br.read_sb(mb)
                cur_x = mx; cur_y = my
                parts.append(f"M({mx},{my})")
            if has_f0:
                f0v = br.read_ub(sfb)
                parts.append(f"f0={f0v}")
            if has_f1:
                f1v = br.read_ub(sfb)
                parts.append(f"f1={f1v}")
            if has_ln:
                lnv = br.read_ub(slb)
                parts.append(f"ln={lnv}")
            if has_new:
                parts.append("NEW_STYLES!")
                # Read new styles
                nfc = br.read_ui8()
                if nfc == 0xFF: nfc = br.read_ui16()
                for _ in range(nfc):
                    nft = br.read_ui8()
                    if nft == 0x00:
                        cs = 4 if tag_type in (32, 83) else 3
                        br.byte_pos += cs
                    elif nft in (0x10, 0x12):
                        hs = br.read_ub(1)
                        if hs:
                            nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                        hr = br.read_ub(1)
                        if hr:
                            nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                        nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                        br.align()
                        ng = br.read_ui8()
                        cs = 4 if tag_type in (32, 83) else 3
                        br.byte_pos += ng * (1 + cs)
                    elif nft in (0x40, 0x41, 0x42, 0x43):
                        br.byte_pos += 2
                        hs = br.read_ub(1)
                        if hs:
                            nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                        hr = br.read_ub(1)
                        if hr:
                            nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                        nb2 = br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                        br.align()
                    else:
                        parts.append(f"UNKNOWN_FILL(0x{nft:02X})")
                        records.append(" ".join(parts))
                        return records
                parts.append(f"fills={nfc}")
                nlc = br.read_ui8()
                if nlc == 0xFF: nlc = br.read_ui16()
                if tag_type in (2, 22):
                    br.byte_pos += nlc * 5
                elif tag_type == 32:
                    br.byte_pos += nlc * 6
                else:
                    for _ in range(nlc):
                        br.byte_pos += 2
                        lf = struct.unpack_from('<H', body, br.byte_pos)[0]; br.byte_pos += 2
                        jn = (lf >> 2) & 3
                        hf = (lf >> 4) & 1
                        if jn == 2: br.byte_pos += 2
                        if hf:
                            # skip fill style
                            pass
                        else:
                            br.byte_pos += 4
                parts.append(f"lines={nlc}")
                sfb = br.read_ub(4)
                slb = br.read_ub(4)
                parts.append(f"fb={sfb} lb={slb}")
            
            records.append(" ".join(parts))
    
    return records


# Parse original SWF
orig = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf"
rt = os.path.join(os.path.dirname(__file__), "test_swfs", "lloyd_rt.swf")
n2d_path = os.path.join(os.path.dirname(__file__), "test_swfs", "lloyd.n2d")

orig_tags = read_swf(orig)
rt_tags = read_swf(rt)

# Collect shape tags by charId
orig_shapes = {}
for tt, body in orig_tags:
    if tt in (2, 22, 32, 83):
        cid = struct.unpack_from('<H', body, 0)[0]
        orig_shapes[cid] = (tt, body)

rt_shapes = {}
for tt, body in rt_tags:
    if tt in (2, 22, 32, 83):
        cid = struct.unpack_from('<H', body, 0)[0]
        rt_shapes[cid] = (tt, body)

# Load N2D
with zipfile.ZipFile(n2d_path) as z:
    with z.open("project.msgpack") as f:
        proj = msgpack.unpack(f, raw=False)

libs = proj.get("libraries", [])
n2d_by_swfcid = {}
for lib in libs:
    if lib.get("type") == "shape" and "endRecodes" not in lib:
        swf_cid = lib.get("swfCharId", -1)
        n2d_by_swfcid[swf_cid] = lib

# We need to find what roundtrip charId corresponds to each original charId.
# The compile_n2d assigns IDs. The N2D lib has an 'id' field, and the compile
# maps that to a new charId. Let's find the mapping by looking at N2D ids
# and checking what order they're emitted.
# Actually, let's just enumerate N2D shapes in library order and match to RT
# shapes in definition order.
n2d_shape_libs = [(lib.get("swfCharId", -1), lib) for lib in libs if lib.get("type") == "shape" and "endRecodes" not in lib]
rt_shape_list = []
for tt, body in rt_tags:
    if tt in (2, 22, 32, 83):
        cid = struct.unpack_from('<H', body, 0)[0]
        rt_shape_list.append((cid, tt, body))

# Build mapping: swfCharId -> rt_charId
# N2D shapes are defined in library order. The compile defines them in dependency order.
# Since all regular shapes have no deps, they're defined in N2D order.
# But bitmaps come first... let me check by looking at rt shape count vs n2d shape count.
print(f"N2D shapes: {len(n2d_shape_libs)}, RT shapes: {len(rt_shape_list)}")
# Morph shapes are separate, so regular shapes should match.

# Let me use a simpler approach: match by recodes content.
# Parse recodes from N2D → get edge structure → match to RT by structure.
# OR: just use compile_n2d in debug mode to get the mapping.
# Simplest: add verbose output to compile_n2d... no, let me just match by ordinal.

# The N2D has 211 shapes (including 2 extra?), RT has 209. Some are morph shapes counted differently.
# Let me just find the mapping empirically by matching shapes with unique bounds.

from swf_binary_io import BitReader as BR

def get_bounds(body, tag_type):
    br = BR(body, 2)
    nb = br.read_ub(5)
    return tuple(br.read_sb(nb) for _ in range(4))

# Build bounds -> cid mapping for RT
rt_bounds_to_cid = {}
for cid, tt, body in rt_shape_list:
    b = get_bounds(body, tt)
    if b not in rt_bounds_to_cid:
        rt_bounds_to_cid[b] = []
    rt_bounds_to_cid[b].append(cid)

# For target shapes, find RT match by N2D bounds
for target_cid in TARGET_CIDS:
    print(f"\n{'='*80}")
    print(f"SHAPE CharID={target_cid}")
    print(f"{'='*80}")
    
    if target_cid not in orig_shapes:
        print(f"  NOT FOUND in original SWF!")
        continue
    
    o_tt, o_body = orig_shapes[target_cid]
    print(f"\n--- ORIGINAL (tag={o_tt}, {len(o_body)} bytes) ---")
    o_recs = dump_shape_edges(o_body, o_tt)
    if o_recs:
        for r in o_recs:
            print(f"    {r}")
    
    # Find in N2D
    if target_cid in n2d_by_swfcid:
        n2d_lib = n2d_by_swfcid[target_cid]
        recodes = n2d_lib.get("recodes", [])
        print(f"\n--- N2D (name={n2d_lib.get('name')}, id={n2d_lib.get('id')}, recodes={len(recodes)}) ---")
        # Print recodes as opcode names
        from swf_shape_to_recodes import ShapeCommand
        i = 0
        while i < len(recodes):
            cmd = recodes[i]
            if not isinstance(cmd, (int, float)):
                print(f"    [{i}] RAW_DATA: {cmd}")
                i += 1
                continue
            cmd = int(cmd)
            cmd_name = ShapeCommand(cmd).name if cmd < 20 else f"UNK({cmd})"
            if cmd == ShapeCommand.MOVE_TO:
                print(f"    [{i}] MOVE_TO {recodes[i+1]:.2f},{recodes[i+2]:.2f}")
                i += 3
            elif cmd == ShapeCommand.CURVE_TO:
                print(f"    [{i}] CURVE_TO ctrl=({recodes[i+1]:.2f},{recodes[i+2]:.2f}) anc=({recodes[i+3]:.2f},{recodes[i+4]:.2f})")
                i += 5
            elif cmd == ShapeCommand.LINE_TO:
                print(f"    [{i}] LINE_TO {recodes[i+1]:.2f},{recodes[i+2]:.2f}")
                i += 3
            elif cmd == ShapeCommand.FILL_STYLE:
                print(f"    [{i}] FILL_STYLE idx={int(recodes[i+1])}")
                i += 2
            elif cmd == ShapeCommand.STROKE_STYLE:
                print(f"    [{i}] STROKE_STYLE idx={int(recodes[i+1])}")
                i += 2
            elif cmd == ShapeCommand.END_FILL:
                print(f"    [{i}] END_FILL")
                i += 1
            elif cmd == ShapeCommand.END_STROKE:
                print(f"    [{i}] END_STROKE")
                i += 1
            elif cmd == ShapeCommand.BEGIN_PATH:
                print(f"    [{i}] BEGIN_PATH")
                i += 1
            elif cmd == ShapeCommand.GRADIENT_FILL:
                print(f"    [{i}] GRADIENT_FILL idx={int(recodes[i+1])}")
                i += 2
            elif cmd == ShapeCommand.CLOSE_PATH:
                print(f"    [{i}] CLOSE_PATH")
                i += 1
            elif cmd == ShapeCommand.BITMAP_FILL:
                val = recodes[i+1]
                if isinstance(val, dict):
                    print(f"    [{i}] BITMAP_FILL {val}")
                else:
                    print(f"    [{i}] BITMAP_FILL idx={int(val)}")
                i += 2
            else:
                print(f"    [{i}] {cmd_name}")
                i += 1
    else:
        print(f"\n--- N2D: NOT FOUND ---")
    
    # Find in RT by bounds matching
    o_bounds = get_bounds(o_body, o_tt)
    # SWF RECT: xmin, xmax, ymin, ymax
    # The export recalculates bounds from edge coordinates, so they might differ.
    # Let me try to find by N2D id mapping instead.
    # Actually, let's just look through all RT shapes for a reasonable match.
    # We know N2D has the id, and compile assigns sequential charIds.
    print(f"\n  Original bounds (twips): {o_bounds}")
    
    # Try to find RT shape by bounds
    if o_bounds in rt_bounds_to_cid:
        for r_cid in rt_bounds_to_cid[o_bounds]:
            r_tt, r_body = rt_shapes[r_cid]
            print(f"\n--- ROUNDTRIP cid={r_cid} (tag={r_tt}, {len(r_body)} bytes) ---")
            r_recs = dump_shape_edges(r_body, r_tt)
            if r_recs:
                for r in r_recs:
                    print(f"    {r}")
    else:
        print(f"  No RT shape found with matching bounds!")
        # Try finding close bounds
        print(f"  Searching by N2D bounds...")
        if target_cid in n2d_by_swfcid:
            n_bounds = n2d_by_swfcid[target_cid].get("bounds", {})
            if isinstance(n_bounds, dict):
                n_twips = (
                    round(n_bounds.get('xMin', 0) * 20),
                    round(n_bounds.get('yMin', 0) * 20),
                    round(n_bounds.get('xMax', 0) * 20),
                    round(n_bounds.get('yMax', 0) * 20),
                )
                # SWF RECT order: xmin, xmax, ymin, ymax
                search = (n_twips[0], n_twips[2], n_twips[1], n_twips[3])
                print(f"  N2D bounds (twips, reordered): {search}")
                if search in rt_bounds_to_cid:
                    for r_cid in rt_bounds_to_cid[search]:
                        r_tt, r_body = rt_shapes[r_cid]
                        print(f"\n--- ROUNDTRIP cid={r_cid} (tag={r_tt}, {len(r_body)} bytes) ---")
                        r_recs = dump_shape_edges(r_body, r_tt)
                        if r_recs:
                            for r in r_recs:
                                print(f"    {r}")
