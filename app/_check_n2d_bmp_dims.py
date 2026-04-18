"""Check N2D bitmaps for dimension vs buffer size mismatches."""
import sys, base64
sys.path.insert(0, '.')
from compile_n2d import load_n2d

proj, _ = load_n2d(r'C:\Users\glwex\Documents\GitHub\Next2Flash\app\converted\blackmage')
libs = proj.get('libraries', [])
print(f'libraries count: {len(libs)}')

# Show structure of first few
for i, e in enumerate(libs[:3]):
    print(f'  libs[{i}] type={type(e).__name__}', repr(e)[:120] if not isinstance(e,dict) else str(list(e.keys())[:8]))

# Flatten and find bitmaps
all_bmps = []
for e in libs:
    if isinstance(e, dict) and e.get('type') == 'bitmap':
        all_bmps.append(e)

print(f'\nTotal bitmap entries: {len(all_bmps)}')

bad = []
for e in all_bmps:
    name = e.get('name', '?')
    w = e.get('width', 0)
    h = e.get('height', 0)
    buf = e.get('buffer', '')
    if isinstance(buf, str) and buf.startswith('b64:'):
        pb = base64.b64decode(buf[4:])
    elif isinstance(buf, (bytes, bytearray)):
        pb = bytes(buf)
    else:
        pb = b''
    exp = w * h * 4
    if exp != len(pb):
        bad.append(f'{name}: {w}x{h} exp={exp} got={len(pb)}')

print(f'Mismatches: {len(bad)}')
for b in bad:
    print(f'  {b}')
if not bad:
    print('All buffer sizes OK')
