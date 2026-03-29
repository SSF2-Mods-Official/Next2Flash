"""Inspect shape recodes from the test N2D file."""
import json, zlib
from urllib.parse import unquote

data = open('_test_gameandwatch.n2d', 'rb').read()
inflated = zlib.decompress(data)
j = json.loads(unquote(inflated.decode('ascii')))

# Find shapes with bitmap fills (recode value 13 = BITMAP_FILL)
BFILL = 13
found = 0
for lib in j['libraries']:
    if lib.get('type') != 'shape':
        continue
    rec = lib.get('recodes', [])
    if not rec:
        continue
    for i, v in enumerate(rec):
        if v == BFILL and i + 1 < len(rec):
            print(f"Shape id={lib['id']}, inBitmap={lib.get('inBitmap', False)}")
            print(f"  recode[{i}:{i+6}] = {rec[i:i+6]}")
            found += 1
            break
    if found >= 5:
        break

# Also check if any shapes have inBitmap=true
inbmp_count = sum(1 for lib in j['libraries'] if lib.get('type') == 'shape' and lib.get('inBitmap'))
print(f"\nShapes with inBitmap=true: {inbmp_count}")
print(f"Total shapes: {sum(1 for lib in j['libraries'] if lib.get('type') == 'shape')}")
