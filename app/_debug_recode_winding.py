"""Analyze recode sub-path winding vs original fill0/fill1."""
import msgpack, zipfile
from shape_converter import parse_next2d_shape_buffer, SolidFill, SubPath, MoveToEdge, LineToEdge, CurveToEdge

with zipfile.ZipFile('lloyd_roundtrip.n2d') as zf:
    raw = zf.read('project.msgpack')
proj = msgpack.unpackb(raw, raw=False)

shapes = [lib for lib in proj['libraries'] if lib.get('type') == 'shape']

def signed_area(sp):
    """Compute signed area of sub-path. + = CW (screen), - = CCW."""
    verts = [(sp.start_x, sp.start_y)]
    cx, cy = sp.start_x, sp.start_y
    for e in sp.edges:
        if isinstance(e, MoveToEdge):
            cx, cy = e.x, e.y
        elif isinstance(e, LineToEdge):
            cx, cy = e.x, e.y
        elif isinstance(e, CurveToEdge):
            cx, cy = e.ax, e.ay
        verts.append((cx, cy))
    n = len(verts)
    area = 0
    for i in range(n):
        j = (i + 1) % n
        area += verts[i][0] * verts[j][1]
        area -= verts[j][0] * verts[i][1]
    return area / 2

# Find shape that has solid 34,34,34 fill with many paths
for sh in shapes:
    rec = sh.get('recodes', [])
    if not rec:
        continue
    fills, lines, paths = parse_next2d_shape_buffer(rec)
    if not fills:
        continue
    f = fills[0]
    if isinstance(f, SolidFill) and f.r == 34 and f.g == 34 and f.b == 34:
        print(f"Shape: name={sh.get('name','?')} id={sh.get('id','?')}")
        print(f"  fills={len(fills)} lines={len(lines)} paths={len(paths)}")
        total_area = 0
        for i, p in enumerate(paths):
            a = signed_area(p)
            total_area += a
            wind = "CW" if a > 0 else "CCW"
            print(f"  Path[{i}]: fill={p.fill_style_idx} line={p.line_style_idx} edges={len(p.edges)} area={a:.0f} {wind}")
        print(f"  Total signed area: {total_area:.0f} ({'CW' if total_area > 0 else 'CCW'})")
        print()

# Also check a bitmap fill shape
for sh in shapes[:10]:
    rec = sh.get('recodes', [])
    if not rec:
        continue
    fills, lines, paths = parse_next2d_shape_buffer(rec)
    if fills and hasattr(fills[0], 'bitmap_char_id'):
        total_area = 0
        for p in paths:
            total_area += signed_area(p)
        wind = "CW" if total_area > 0 else "CCW"
        print(f"Bitmap shape: name={sh.get('name','?')} paths={len(paths)} total_area={total_area:.0f} {wind}")
        break
