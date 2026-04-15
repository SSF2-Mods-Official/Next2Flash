"""Verify all 26 lloyd morphs produce identical binary after roundtrip."""
import struct, zlib, os, sys, io
sys.path.insert(0, '.')
import msgpack, zipfile
from shape_converter import (
    parse_next2d_shape_buffer, build_define_morph_shape, build_define_morph_shape2
)

lloyd = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf"
n2d_path = "test_swfs/lloyd_rt.n2d"

# Ensure N2D exists
if not os.path.exists(n2d_path):
    os.system(f'python swf_to_n2d.py "{lloyd}" "{n2d_path}" >NUL 2>&1')

# Parse original SWF morphs
def get_morphs_from_swf(path):
    with open(path, 'rb') as f:
        sig = f.read(3)
        f.read(1)
        struct.unpack('<I', f.read(4))
        rest = f.read()
    if sig == b'CWS':
        rest = zlib.decompress(rest)
    nbits = (rest[0] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    pos = rect_bytes + 4
    morphs = {}
    while pos < len(rest):
        tc = struct.unpack_from('<H', rest, pos)[0]
        pos += 2
        tt = tc >> 6
        ll = tc & 0x3F
        if ll == 0x3F:
            ll = struct.unpack_from('<I', rest, pos)[0]
            pos += 4
        body = rest[pos:pos+ll]
        if tt in (46, 84) and ll >= 2:
            cid = struct.unpack_from('<H', body, 0)[0]
            morphs[cid] = (tt, body)
        pos += ll
        if tt == 0:
            break
    return morphs

orig_morphs = get_morphs_from_swf(lloyd)
print(f"Original: {len(orig_morphs)} morph tags")

# Load N2D
with zipfile.ZipFile(n2d_path, 'r') as zf:
    data = msgpack.unpackb(zf.read('project.msgpack'), raw=False)

libs = data.get('libraries', [])
n2d_morphs = [l for l in libs if l.get('isMorphShape')]
print(f"N2D: {len(n2d_morphs)} morph shapes")

# For each N2D morph, rebuild and compare to original
identical = 0
different = 0
errors = 0

for morph in n2d_morphs:
    cid = morph['swfCharId']
    raw_tag_type = morph.get('rawTagType', 46)
    start_recodes = morph.get('recodes', [])
    end_recodes = morph.get('endRecodes', [])
    start_bounds = morph.get('bounds')
    end_bounds = morph.get('endBounds')

    if cid not in orig_morphs:
        print(f"  charId={cid}: NOT FOUND in original SWF")
        errors += 1
        continue

    orig_tt, orig_body = orig_morphs[cid]

    try:
        s_fills, s_lines, s_paths = parse_next2d_shape_buffer(start_recodes) if start_recodes else ([], [], [])
        e_fills, e_lines, e_paths = parse_next2d_shape_buffer(end_recodes) if end_recodes else ([], [], [])

        if raw_tag_type == 84:
            rebuilt = build_define_morph_shape2(cid, s_fills, s_lines, s_paths, start_bounds,
                                               e_fills, e_lines, e_paths, end_bounds)
        else:
            rebuilt = build_define_morph_shape(cid, s_fills, s_lines, s_paths, start_bounds,
                                              e_fills, e_lines, e_paths, end_bounds)

        # Extract body from rebuilt tag
        tc = struct.unpack_from('<H', bytes(rebuilt), 0)[0]
        ll = tc & 0x3F
        hdr_len = 6 if ll == 0x3F else 2
        rebuilt_body = bytes(rebuilt[hdr_len:])
        rebuilt_tt = tc >> 6

        if rebuilt_body == orig_body:
            identical += 1
        else:
            different += 1
            diffs = sum(1 for i in range(min(len(orig_body), len(rebuilt_body))) if orig_body[i] != rebuilt_body[i])
            print(f"  charId={cid}: DIFF orig={len(orig_body)}b rebuilt={len(rebuilt_body)}b diffbytes={diffs} tag={orig_tt}->{rebuilt_tt}")
    except Exception as e:
        print(f"  charId={cid}: ERROR {e}")
        errors += 1

print(f"\n{'='*50}")
print(f"RESULTS: {identical} identical, {different} different, {errors} errors out of {len(n2d_morphs)}")
