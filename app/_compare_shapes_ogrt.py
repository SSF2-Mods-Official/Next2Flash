"""Compare DefineShape3 tags in OG vs fresh RT byte-by-byte.
OG has 125 DefineShape3 tags. RT has 853. 
Check if the 125 OG DefineShape3 shapes survive roundtrip identically."""
import sys, os, struct, zlib, tempfile
sys.path.insert(0, os.path.dirname(__file__))

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"

def read_swf(path):
    with open(path, "rb") as f:
        data = f.read()
    if data[:3] == b"CWS":
        data = data[:8] + zlib.decompress(data[8:])
    return data

def iter_tags(data):
    pos = 8
    nbits = (data[pos] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    pos += (total_bits + 7) // 8
    pos += 4
    while pos < len(data):
        tc = struct.unpack_from("<H", data, pos)[0]
        tt = tc >> 6
        length = tc & 0x3F
        pos += 2
        if length == 0x3F:
            length = struct.unpack_from("<I", data, pos)[0]
            pos += 4
        body = data[pos:pos+length]
        yield tt, body
        pos += length
        if tt == 0:
            break

# Import and compile fresh
from swf_to_n2d import parse_swf, N2DBuilder, save_n2d
from compile_n2d import N2DCompiler

raw = read_swf(OG)
header, tags = parse_swf(raw)
builder = N2DBuilder(header, "fox")
builder.catalog_swf_tags(tags)
builder.frame_scripts = {}
builder.build_all()
n2d = builder.to_n2d_json()

tmp = tempfile.mkdtemp()
n2d_path = os.path.join(tmp, "fox.n2d")
out_path = os.path.join(tmp, "fox_rt.ssf")
save_n2d(n2d, n2d_path)

compiler = N2DCompiler(n2d_path, tmp, out_path)
compiler.compile()
with open(out_path, "rb") as f:
    rt_data = f.read()
if rt_data[:3] == b"CWS":
    rt_data = rt_data[:8] + zlib.decompress(rt_data[8:])

# Collect all shape-like tags by charId
def get_shape_tags(data):
    """Return dict: charId -> (tag_type, body_without_charId)"""
    shapes = {}
    for tt, body in iter_tags(data):
        if tt in (2, 22, 32, 46, 83):  # DefineShape 1-4
            if len(body) >= 2:
                cid = struct.unpack_from("<H", body, 0)[0]
                shapes[cid] = (tt, body[2:])
    return shapes

og_shapes = get_shape_tags(raw)
rt_shapes = get_shape_tags(rt_data)

print(f"OG shapes: {len(og_shapes)}")
print(f"RT shapes: {len(rt_shapes)}")

# The charIds differ, so match by emission order (index)
og_ordered = sorted(og_shapes.items())
rt_ordered = sorted(rt_shapes.items())

# Also collect SymbolClass to try name-matching
og_symclass = {}
rt_symclass = {}
for tt, body in iter_tags(raw):
    if tt == 76:
        count = struct.unpack_from("<H", body, 0)[0]
        p = 2
        for _ in range(count):
            cid = struct.unpack_from("<H", body, p)[0]
            p += 2
            end = body.index(0, p)
            name = body[p:end].decode("utf-8", errors="replace")
            p = end + 1
            og_symclass[cid] = name
for tt, body in iter_tags(rt_data):
    if tt == 76:
        count = struct.unpack_from("<H", body, 0)[0]
        p = 2
        for _ in range(count):
            cid = struct.unpack_from("<H", body, p)[0]
            p += 2
            end = body.index(0, p)
            name = body[p:end].decode("utf-8", errors="replace")
            p = end + 1
            rt_symclass[cid] = name

# Match shapes by SymbolClass name
og_name_to_shape = {}
for cid, (tt, body) in og_shapes.items():
    name = og_symclass.get(cid)
    if name:
        og_name_to_shape[name] = (cid, tt, body)

rt_name_to_shape = {}
for cid, (tt, body) in rt_shapes.items():
    name = rt_symclass.get(cid)
    if name:
        rt_name_to_shape[name] = (cid, tt, body)

# Compare shapes that have matching SymbolClass names
matched_names = set(og_name_to_shape.keys()) & set(rt_name_to_shape.keys())
print(f"\nShapes with matching SymbolClass names: {len(matched_names)}")

identical = 0
type_diff = 0
body_diff = 0
size_diffs = []

for name in sorted(matched_names):
    og_cid, og_tt, og_body = og_name_to_shape[name]
    rt_cid, rt_tt, rt_body = rt_name_to_shape[name]
    
    if og_tt == rt_tt == 32:  # Both DefineShape3
        if og_body == rt_body:
            identical += 1
        else:
            body_diff += 1
            if len(size_diffs) < 10:
                size_diffs.append((name, og_cid, rt_cid, len(og_body), len(rt_body)))
    elif og_tt != rt_tt:
        type_diff += 1

print(f"Both DefineShape3 & identical body: {identical}")
print(f"Both DefineShape3 & different body: {body_diff}")
print(f"Different tag types: {type_diff}")

if size_diffs:
    print(f"\nSample body differences (DefineShape3→DefineShape3):")
    for name, ogc, rtc, ogs, rts in size_diffs:
        print(f"  {name}: OG cid={ogc} {ogs}B, RT cid={rtc} {rts}B, diff={rts-ogs:+d}B")

# Check shapes without SymbolClass names — match by position
og_unnamed = [(cid, tt, body) for cid, (tt, body) in og_ordered if cid not in og_symclass]
rt_unnamed = [(cid, tt, body) for cid, (tt, body) in rt_ordered if cid not in rt_symclass]
print(f"\nUnnamed shapes: OG={len(og_unnamed)}, RT={len(rt_unnamed)}")

# Overall body size comparison
og_total = sum(len(body) for _, (_, body) in og_shapes.items())
rt_total = sum(len(body) for _, (_, body) in rt_shapes.items())
print(f"\nTotal shape body bytes: OG={og_total:,}, RT={rt_total:,}, diff={rt_total-og_total:+,}")

# Check bitmap dimensions in both SWFs
def get_bitmap_dims(data):
    """Return dict: charId -> (tag_type, width, height, body_size)"""
    bitmaps = {}
    for tt, body in iter_tags(data):
        if tt == 36:  # DefineBitsLossless2
            cid = struct.unpack_from("<H", body, 0)[0]
            w = struct.unpack_from("<H", body, 3)[0]
            h = struct.unpack_from("<H", body, 5)[0]
            bitmaps[cid] = (tt, w, h, len(body))
        elif tt == 35:  # DefineBitsJPEG3
            cid = struct.unpack_from("<H", body, 0)[0]
            bitmaps[cid] = (tt, 0, 0, len(body))  # dimensions need JPEG decode
    return bitmaps

og_bmps = get_bitmap_dims(raw)
rt_bmps = get_bitmap_dims(rt_data)

# Match by sorted position
og_bmp_list = sorted(og_bmps.items())
rt_bmp_list = sorted(rt_bmps.items())

dim_mismatches = 0
for i in range(min(len(og_bmp_list), len(rt_bmp_list))):
    og_cid, (og_tt, og_w, og_h, og_sz) = og_bmp_list[i]
    rt_cid, (rt_tt, rt_w, rt_h, rt_sz) = rt_bmp_list[i]
    if og_tt == rt_tt == 36:
        if og_w != rt_w or og_h != rt_h:
            dim_mismatches += 1
            print(f"  BMP DIM MISMATCH #{i}: OG cid={og_cid} {og_w}x{og_h} vs RT cid={rt_cid} {rt_w}x{rt_h}")

print(f"\nBitmap dimension mismatches (Lossless2 vs Lossless2): {dim_mismatches}")

import shutil
shutil.rmtree(tmp, ignore_errors=True)
