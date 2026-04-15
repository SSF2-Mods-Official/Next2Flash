"""Trace test7 roundtrip: recodes -> sub-paths -> SWF."""
import msgpack, zipfile
from shape_converter import parse_next2d_shape_buffer, MoveToEdge, LineToEdge, CurveToEdge

with zipfile.ZipFile('test_swfs/test7_two_fills.n2d') as zf:
    raw = zf.read('project.msgpack')
proj = msgpack.unpackb(raw, raw=False)

for lib in proj['libraries']:
    if lib.get('type') != 'shape':
        continue
    rec = lib.get('recodes', [])
    if not rec:
        continue
    name = lib.get('name', '?')
    print(f"Shape {name} recodes ({len(rec)} items):")
    for i, v in enumerate(rec):
        print(f"  [{i}] {v}")
    print()
    fills, lines, paths = parse_next2d_shape_buffer(rec)
    print(f"Parsed: fills={len(fills)} lines={len(lines)} paths={len(paths)}")
    for pi, p in enumerate(paths):
        print(f"  Path[{pi}]: fill={p.fill_style_idx} line={p.line_style_idx} start=({p.start_x},{p.start_y}) edges={len(p.edges)}")
        for ei, e in enumerate(p.edges):
            if isinstance(e, MoveToEdge):
                print(f"    [{ei}] MOVE ({e.x},{e.y})")
            elif isinstance(e, LineToEdge):
                print(f"    [{ei}] LINE ({e.x},{e.y})")
            elif isinstance(e, CurveToEdge):
                print(f"    [{ei}] CURVE c=({e.cx},{e.cy}) a=({e.ax},{e.ay})")
