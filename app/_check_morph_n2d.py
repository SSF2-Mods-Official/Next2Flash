"""Check morph shape data in N2D file."""
import msgpack, json, sys

with open('test_swfs/test10_morph.n2d', 'rb') as f:
    raw = f.read()

# The N2D format may have multiple msgpack objects
import io
unpacker = msgpack.Unpacker(io.BytesIO(raw), raw=False)
objects = []
for obj in unpacker:
    objects.append(obj)
    if len(objects) > 10:
        break

print(f"Found {len(objects)} top-level msgpack objects")
for i, obj in enumerate(objects):
    t = type(obj).__name__
    if isinstance(obj, dict):
        print(f"  [{i}] dict keys: {list(obj.keys())[:20]}")
        if 'libraries' in obj:
            for lib in obj['libraries']:
                lt = lib.get('type', '')
                print(f"    Library: type={lt}")
                for key in ('recodes', 'endRecodes', 'bounds', 'endBounds'):
                    val = lib.get(key)
                    if val is not None:
                        if isinstance(val, list):
                            print(f"      {key}: {len(val)} items = {val[:20]}")
                        else:
                            print(f"      {key}: {val}")
    elif isinstance(obj, list):
        print(f"  [{i}] list len={len(obj)}")
        if len(obj) < 50:
            print(f"    {obj}")
    else:
        print(f"  [{i}] {t}: {repr(obj)[:100]}")
