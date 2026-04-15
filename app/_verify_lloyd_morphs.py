#!/usr/bin/env python3
"""Verify lloyd.ssf morph roundtrip produces non-empty morph tags."""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__))

from swf_binary_io import BitReader

lloyd = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf'
n2d_path = os.path.join(os.path.dirname(__file__), 'test_swfs', 'lloyd.n2d')
rt_path = os.path.join(os.path.dirname(__file__), 'test_swfs', 'lloyd_rt.swf')

print("Importing lloyd.ssf...")
ret = os.system(f'python swf_to_n2d.py "{lloyd}" "{n2d_path}" >NUL 2>&1')
if ret != 0:
    print(f"FAIL: import returned {ret}")
    sys.exit(1)
print(f"Import done → {n2d_path}")

print("Compiling N2D → SWF...")
ret = os.system(f'python compile_n2d.py "{n2d_path}" -o "{rt_path}" --shared . >NUL 2>&1')
if ret != 0:
    print(f"FAIL: compile returned {ret}")
    sys.exit(1)
print(f"Compile done → {rt_path}")

print("\nChecking morph tags in output SWF...")
with open(rt_path, 'rb') as f:
    data = f.read()

rest = data[8:]
if data[:3] in (b'CWS', b'ZWS'):
    import zlib
    rest = zlib.decompress(rest)

br = BitReader(rest, 0)
nbits = br.read_ub(5)
for _ in range(4): br.read_sb(nbits)
br.align()
pos = br.byte_pos + 4

morph_count = 0
morph_ok = 0
while pos < len(rest):
    tc = struct.unpack_from('<H', rest, pos)[0]
    pos += 2
    tt = tc >> 6
    ll = tc & 0x3F
    if ll == 0x3F:
        ll = struct.unpack_from('<I', rest, pos)[0]
        pos += 4
    if tt in (46, 84):
        morph_count += 1
        body = rest[pos:pos+ll]
        cid = struct.unpack_from('<H', body, 0)[0]
        if ll > 20:
            morph_ok += 1
            print(f"  Morph tag={tt} charId={cid} len={ll} OK")
        else:
            print(f"  Morph tag={tt} charId={cid} len={ll} EMPTY!")
    pos += ll
    if tt == 0:
        break

print(f"\nTotal morphs: {morph_count}, non-empty: {morph_ok}")
if morph_ok == morph_count and morph_count > 0:
    print("ALL MORPH SHAPES HAVE CONTENT!")
else:
    print("WARNING: Some morphs are empty!")
