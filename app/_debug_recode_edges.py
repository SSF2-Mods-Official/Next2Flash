"""Compare recode edges vs roundtrip SWF edges for Shape 235."""
import msgpack, zipfile, struct
from shape_converter import parse_next2d_shape_buffer, SolidFill, SubPath, MoveToEdge, LineToEdge, CurveToEdge
from swf_binary_io import BitReader

# Load recodes
with zipfile.ZipFile('lloyd_roundtrip.n2d') as zf:
    raw = zf.read('project.msgpack')
proj = msgpack.unpackb(raw, raw=False)

shapes = [lib for lib in proj['libraries'] if lib.get('type') == 'shape']
target_shape = None
for sh in shapes:
    if sh.get('name') == 'Shape_235':
        target_shape = sh
        break

rec = target_shape['recodes']
fills, lines, paths = parse_next2d_shape_buffer(rec)
sp = paths[0]

print("=== RECODE SUB-PATH ===")
print(f"start: ({sp.start_x:.2f}, {sp.start_y:.2f})")
move_count = 0
line_count = 0
curve_count = 0
for e in sp.edges[:40]:
    if isinstance(e, MoveToEdge):
        print(f"  MOVE ({e.x:.2f}, {e.y:.2f})")
        move_count += 1
    elif isinstance(e, LineToEdge):
        print(f"  LINE ({e.x:.2f}, {e.y:.2f})")
        line_count += 1
    elif isinstance(e, CurveToEdge):
        print(f"  CURVE c=({e.cx:.2f},{e.cy:.2f}) a=({e.ax:.2f},{e.ay:.2f})")
        curve_count += 1

total = len(sp.edges)
for e in sp.edges[40:]:
    if isinstance(e, MoveToEdge): move_count += 1
    elif isinstance(e, LineToEdge): line_count += 1
    elif isinstance(e, CurveToEdge): curve_count += 1

print(f"\nTotal edges: {total} (moves={move_count}, lines={line_count}, curves={curve_count})")

# Also check ALL shapes for total sub-paths and moves
print("\n=== ALL SHAPES SUMMARY ===")
total_shapes = 0
shapes_with_moves = 0
max_moves = 0
for sh in shapes:
    rec = sh.get('recodes', [])
    if not rec: continue
    try:
        fills, lines, paths = parse_next2d_shape_buffer(rec)
    except:
        continue
    total_shapes += 1
    for p in paths:
        mc = sum(1 for e in p.edges if isinstance(e, MoveToEdge))
        if mc > 0:
            shapes_with_moves += 1
            max_moves = max(max_moves, mc)
            if mc > 5:
                print(f"  {sh.get('name','?')}: {mc} MoveToEdges in path with {len(p.edges)} edges")
            break

print(f"Total shapes: {total_shapes}, shapes with MoveToEdge in paths: {shapes_with_moves}")
print(f"Max MoveToEdges in a single path: {max_moves}")
