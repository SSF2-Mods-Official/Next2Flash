"""Check for edge-case bitmap dimensions in the N2D."""
import msgpack, zipfile, base64

n2d_path = r'converted\blackmage\project.n2d'
with zipfile.ZipFile(n2d_path) as zf:
    for name in zf.namelist():
        if name.endswith('.msgpack'):
            data = msgpack.unpackb(zf.read(name), raw=False)
            break

libs = data.get('libraries', [])
bitmaps = [l for l in libs if l.get('type') == 'bitmap']

print(f"Total bitmaps: {len(bitmaps)}")

# Check for zero/missing/problematic dimensions
bad_count = 0
for b in bitmaps:
    bid = b["id"]
    bname = b.get("name", "?")
    w = b.get("width")
    h = b.get("height")
    buf = b.get("buffer", b"")
    
    if w is None or h is None or w == 0 or h == 0:
        print(f"BAD DIMS: id={bid} name={bname} w={w} h={h}")
        bad_count += 1
    elif w < 0 or h < 0:
        print(f"NEGATIVE DIMS: id={bid} name={bname} w={w} h={h}")
        bad_count += 1
    else:
        # Check buffer size
        if isinstance(buf, str):
            if buf.startswith('b64:'):
                raw = base64.b64decode(buf[4:])
            else:
                raw = buf.encode('latin-1')
        elif isinstance(buf, bytes):
            raw = buf
        else:
            raw = b""
        
        expected = w * h * 4
        if len(raw) > 0 and len(raw) != expected:
            print(f"SIZE MISMATCH: id={bid} name={bname} w={w} h={h} buf={len(raw)} expected={expected}")
            bad_count += 1

print(f"\nBad bitmaps: {bad_count}")

# Check dimension distribution
from collections import Counter
dim_counter = Counter()
for b in bitmaps:
    w = b.get("width", 0)
    h = b.get("height", 0)
    dim_counter[(w, h)] += 1

# Show smallest dimensions
print("\n--- Smallest bitmaps (by area) ---")
sorted_dims = sorted(dim_counter.items(), key=lambda x: x[0][0] * x[0][1])
for (w, h), count in sorted_dims[:20]:
    print(f"  {w}x{h}: {count} bitmaps")

# Check containers for which bitmaps are placed
containers = [l for l in libs if l.get('type') == 'container']
bitmap_by_id = {l['id']: l for l in bitmaps}

direct_placed_bids = set()
for lib in containers:
    for layer in lib.get('layers', []):
        for char in layer.get('characters', []):
            ref = char.get('libraryId')
            if ref in bitmap_by_id:
                direct_placed_bids.add(ref)

print(f"\n--- Direct-placed bitmaps: {len(direct_placed_bids)} ---")
print("Dimension distribution of direct-placed bitmaps:")
placed_dim_counter = Counter()
for bid in direct_placed_bids:
    b = bitmap_by_id[bid]
    w = b.get("width", 0)
    h = b.get("height", 0)
    placed_dim_counter[(w, h)] += 1

sorted_placed = sorted(placed_dim_counter.items(), key=lambda x: x[0][0] * x[0][1])
for (w, h), count in sorted_placed[:20]:
    print(f"  {w}x{h}: {count} bitmaps")

# Check if any have external files that don't exist
import os
ext_dir = r'converted\blackmage\library'
missing_ext = 0
for b in bitmaps:
    bname = b.get("name", "")
    ext_path = os.path.join(ext_dir, bname + ".png")
    if not os.path.exists(ext_path):
        # Try without extension
        ext_path2 = os.path.join(ext_dir, bname)
        if not os.path.exists(ext_path2):
            missing_ext += 1
            if missing_ext <= 5:
                print(f"NO EXT FILE: id={b['id']} name={bname}")

print(f"\nMissing external files: {missing_ext} / {len(bitmaps)}")
