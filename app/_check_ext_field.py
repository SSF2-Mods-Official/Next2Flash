"""Check externalFile field in N2D bitmap entries."""
import msgpack, zipfile

with zipfile.ZipFile(r'converted\blackmage\project.n2d') as zf:
    for name in zf.namelist():
        if name.endswith('.msgpack'):
            data = msgpack.unpackb(zf.read(name), raw=False)
            break

libs = data.get('libraries', [])
bitmaps = [l for l in libs if l.get('type') == 'bitmap']

# Check a few for externalFile field
for b in bitmaps[:5]:
    bid = b["id"]
    bname = b.get("name", "?")
    ext = b.get("externalFile", "NOT SET")
    has_buf = "buffer" in b
    buf_size = len(b.get("buffer", b"")) if has_buf else 0
    print(f"id={bid} name={bname} externalFile={ext} hasBuffer={has_buf} bufSize={buf_size}")

# Count how many have externalFile set
has_ext = sum(1 for b in bitmaps if b.get("externalFile"))
has_buf = sum(1 for b in bitmaps if b.get("buffer"))
print(f"\nHas externalFile: {has_ext}/{len(bitmaps)}")
print(f"Has buffer: {has_buf}/{len(bitmaps)}")

# Check all keys present in bitmap entries
all_keys = set()
for b in bitmaps:
    all_keys.update(b.keys())
print(f"\nAll bitmap keys: {sorted(all_keys)}")
