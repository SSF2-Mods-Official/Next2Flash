"""
Trace MorphShape_147 through the full pipeline.
"""
import zipfile, msgpack, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swf_constants import ShapeCommand
from shape_converter import parse_next2d_shape_buffer

n2d = "test_swfs/lloyd_rt.n2d"

with zipfile.ZipFile(n2d, 'r') as z:
    with z.open('project.msgpack') as f:
        raw = f.read()
data = msgpack.unpackb(raw, raw=False)

# Find MorphShape_147 
for lib in data['libraries']:
    if isinstance(lib, dict) and lib.get('name') == 'MorphShape_147':
        morph = lib
        break

start_recodes = morph['recodes']
end_recodes = morph['endRecodes']

# Decode recodes manually
CMD_NAMES = {v: k for k, v in ShapeCommand.__members__.items()}

def decode_recodes_list(buf, label):
    print(f"\n=== {label} ({len(buf)} entries) ===")
    i = 0
    while i < len(buf):
        val = buf[i]
        if isinstance(val, bool):
            print(f"  [{i}] bool: {val}")
            i += 1
            continue
        cmd = int(val)
        name = CMD_NAMES.get(cmd, f'?{cmd}')
        
        if cmd == ShapeCommand.MOVE_TO:
            x, y = buf[i+1], buf[i+2]
            print(f"  [{i}] MOVE_TO({x}, {y}) [twips: {x*20:.0f}, {y*20:.0f}]")
            i += 3
        elif cmd == ShapeCommand.CURVE_TO:
            cx, cy, ax, ay = buf[i+1], buf[i+2], buf[i+3], buf[i+4]
            print(f"  [{i}] CURVE_TO(ctrl={cx},{cy} anch={ax},{ay})")
            i += 5
        elif cmd == ShapeCommand.LINE_TO:
            x, y = buf[i+1], buf[i+2]
            print(f"  [{i}] LINE_TO({x}, {y})")
            i += 3
        elif cmd == ShapeCommand.FILL_STYLE:
            r, g, b, a = int(buf[i+1]), int(buf[i+2]), int(buf[i+3]), int(buf[i+4])
            print(f"  [{i}] FILL_STYLE rgba=({r},{g},{b},{a})")
            i += 5
        elif cmd == ShapeCommand.GRADIENT_FILL:
            print(f"  [{i}] GRADIENT_FILL")
            # Variable length - just print raw values until next recognizable command
            i += 1
            while i < len(buf):
                v = buf[i]
                if isinstance(v, (int, float)) and not isinstance(v, bool) and int(v) in CMD_NAMES and int(v) < 15:
                    # Might be next command - but could also be data
                    # Let's just dump
                    break
                print(f"    [{i}] {repr(v)}")
                i += 1
        elif cmd == ShapeCommand.STROKE_STYLE:
            thickness = buf[i+1]
            cap = buf[i+2]
            join = buf[i+3]
            miter = buf[i+4]
            r, g, b, a = int(buf[i+5]), int(buf[i+6]), int(buf[i+7]), int(buf[i+8])
            print(f"  [{i}] STROKE_STYLE width={thickness} cap={cap} join={join} miter={miter} rgba=({r},{g},{b},{a})")
            i += 9
        elif cmd == ShapeCommand.END_FILL:
            print(f"  [{i}] END_FILL")
            i += 1
        elif cmd == ShapeCommand.END_STROKE:
            print(f"  [{i}] END_STROKE")
            i += 1
        elif cmd == ShapeCommand.BEGIN_PATH:
            print(f"  [{i}] BEGIN_PATH")
            i += 1
        elif cmd == ShapeCommand.CLOSE_PATH:
            print(f"  [{i}] CLOSE_PATH")
            i += 1
        elif cmd == ShapeCommand.GRADIENT_STROKE:
            print(f"  [{i}] GRADIENT_STROKE")
            i += 1
            # Skip variable data
            while i < len(buf):
                v = buf[i]
                if isinstance(v, (int, float)) and not isinstance(v, bool) and int(v) in CMD_NAMES and int(v) < 15:
                    break
                print(f"    [{i}] {repr(v)}")
                i += 1
        elif cmd == ShapeCommand.BITMAP_FILL:
            print(f"  [{i}] BITMAP_FILL")
            i += 1
        else:
            print(f"  [{i}] {name}({cmd})")
            i += 1

decode_recodes_list(start_recodes, "Start Recodes")
decode_recodes_list(end_recodes, "End Recodes")

# Now trace through parse_next2d_shape_buffer
print("\n\n=== parse_next2d_shape_buffer(start_recodes) ===")
fills_s, lines_s, paths_s = parse_next2d_shape_buffer(start_recodes)
print(f"fills: {len(fills_s)}, lines: {len(lines_s)}, sub_paths: {len(paths_s)}")
for i, sp in enumerate(paths_s):
    print(f"  subpath[{i}]: fill_idx={sp.fill_style_idx} line_idx={sp.line_style_idx} edges={len(sp.edges)}")
    for j, e in enumerate(sp.edges):
        ename = type(e).__name__
        if hasattr(e, 'sx'):
            print(f"    edge[{j}]: {ename} start=({e.sx},{e.sy}) end=({e.ex},{e.ey})", end="")
        elif hasattr(e, 'x'):
            print(f"    edge[{j}]: {ename} pos=({e.x},{e.y})", end="")
        else:
            print(f"    edge[{j}]: {ename} {vars(e)}", end="")
        if hasattr(e, 'cx'):
            print(f" ctrl=({e.cx},{e.cy})", end="")
        print()

print("\n=== parse_next2d_shape_buffer(end_recodes) ===")
fills_e, lines_e, paths_e = parse_next2d_shape_buffer(end_recodes)
print(f"fills: {len(fills_e)}, lines: {len(lines_e)}, sub_paths: {len(paths_e)}")
for i, sp in enumerate(paths_e):
    print(f"  subpath[{i}]: fill_idx={sp.fill_style_idx} line_idx={sp.line_style_idx} edges={len(sp.edges)}")
    for j, e in enumerate(sp.edges):
        ename = type(e).__name__
        if hasattr(e, 'sx'):
            print(f"    edge[{j}]: {ename} start=({e.sx},{e.sy}) end=({e.ex},{e.ey})", end="")
        elif hasattr(e, 'x'):
            print(f"    edge[{j}]: {ename} pos=({e.x},{e.y})", end="")
        else:
            print(f"    edge[{j}]: {ename} {vars(e)}", end="")
        if hasattr(e, 'cx'):
            print(f" ctrl=({e.cx},{e.cy})", end="")
        print()

# Check edge count match
total_start = sum(len(sp.edges) for sp in paths_s)
total_end = sum(len(sp.edges) for sp in paths_e)
print(f"\nTotal start edges: {total_start}")
print(f"Total end edges: {total_end}")
if total_start != total_end:
    print(f"*** EDGE COUNT MISMATCH ***")

# Now actually encode with _encode_morph_shape_edges and inspect the binary
print("\n\n=== ENCODING START EDGES ===")
from shape_converter import _encode_morph_shape_edges
start_bits = _encode_morph_shape_edges(fills_s, lines_s, paths_s, is_end_state=False)
print(f"Start edges binary: {len(start_bits)} bytes")
print(f"  hex: {start_bits.hex()}")

# Parse back the start edges to check what we wrote
br_s = BitReader(start_bits, 0)
sfb = br_s.read_ub(4)
slb = br_s.read_ub(4)
print(f"  fill_bits={sfb} line_bits={slb}")
record_count = 0
while True:
    tf = br_s.read_ub(1)
    if tf == 0:
        flags = br_s.read_ub(5)
        if flags == 0:
            print(f"  EndShape after {record_count} records")
            break
        desc = "  SC:"
        if flags & 0x01:
            mb = br_s.read_ub(5)
            mx = br_s.read_sb(mb)
            my = br_s.read_sb(mb)
            desc += f" mv=({mx},{my})"
        if flags & 0x02:
            f0 = br_s.read_ub(sfb)
            desc += f" f0={f0}"
        if flags & 0x04:
            f1 = br_s.read_ub(sfb)
            desc += f" f1={f1}"
        if flags & 0x08:
            ln = br_s.read_ub(slb)
            desc += f" ln={ln}"
        if flags & 0x10:
            desc += " newStyles"
        print(desc)
    else:
        st = br_s.read_ub(1)
        if st:
            nb = br_s.read_ub(4) + 2
            gf = br_s.read_ub(1)
            if gf: 
                dx = br_s.read_sb(nb); dy = br_s.read_sb(nb)
            else:
                vl = br_s.read_ub(1)
                if vl: dy = br_s.read_sb(nb); dx = 0
                else: dx = br_s.read_sb(nb); dy = 0
        else:
            nb = br_s.read_ub(4) + 2
            br_s.read_sb(nb); br_s.read_sb(nb); br_s.read_sb(nb); br_s.read_sb(nb)
        record_count += 1

print("\n=== ENCODING END EDGES ===")
end_bits = _encode_morph_shape_edges(fills_e, lines_e, paths_e, is_end_state=True)
print(f"End edges binary: {len(end_bits)} bytes")
print(f"  hex: {end_bits.hex()}")

br_e = BitReader(end_bits, 0)
efb = br_e.read_ub(4)
elb = br_e.read_ub(4)
print(f"  fill_bits={efb} line_bits={elb}")
record_count_e = 0
while True:
    tf = br_e.read_ub(1)
    if tf == 0:
        flags = br_e.read_ub(5)
        if flags == 0:
            print(f"  EndShape after {record_count_e} records")
            break
        desc = "  SC:"
        if flags & 0x01:
            mb = br_e.read_ub(5)
            mx = br_e.read_sb(mb)
            my = br_e.read_sb(mb)
            desc += f" mv=({mx},{my})"
        if flags & 0x02:
            f0 = br_e.read_ub(efb)
            desc += f" f0={f0}"
        if flags & 0x04:
            f1 = br_e.read_ub(efb)
            desc += f" f1={f1}"
        if flags & 0x08:
            ln = br_e.read_ub(elb)
            desc += f" ln={ln}"
        if flags & 0x10:
            desc += " newStyles"
        print(desc)
    else:
        st = br_e.read_ub(1)
        if st:
            nb = br_e.read_ub(4) + 2
            gf = br_e.read_ub(1)
            if gf:
                dx = br_e.read_sb(nb); dy = br_e.read_sb(nb)
            else:
                vl = br_e.read_ub(1)
                if vl: dy = br_e.read_sb(nb); dx = 0
                else: dx = br_e.read_sb(nb); dy = 0
        else:
            nb = br_e.read_ub(4) + 2
            br_e.read_sb(nb); br_e.read_sb(nb); br_e.read_sb(nb); br_e.read_sb(nb)
        record_count_e += 1

print(f"\nStart edge records: {record_count}")
print(f"End edge records: {record_count_e}")
if record_count != record_count_e:
    print("*** EDGE RECORD COUNT MISMATCH BETWEEN START AND END ***")
print(f"\nTotal start edges: {total_start}")
print(f"Total end edges: {total_end}")
if total_start != total_end:
    print(f"*** EDGE COUNT MISMATCH ***")
