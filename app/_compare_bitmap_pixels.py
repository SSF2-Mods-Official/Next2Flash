"""Check if bitmap bodies differ only in compression or in actual pixel data.
OG LL2 -> decode ARGB -> vs RT LL2 -> decode ARGB pixel comparison."""
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

from swf_to_n2d import parse_swf, N2DBuilder, save_n2d
from compile_n2d import N2DCompiler
from compilation_pipeline import create_default_pipeline, CompilationContext

raw = read_swf(OG)
header, tags = parse_swf(raw)
builder = N2DBuilder(header, "fox")
builder.catalog_swf_tags(tags)
builder.frame_scripts = {}
builder.build_all()
n2d = builder.to_n2d_json()

og_swf_to_n2d = dict(builder.swf_to_n2d)
n2d_to_og_swf = {v: k for k, v in og_swf_to_n2d.items()}

tmp = tempfile.mkdtemp()
n2d_path = os.path.join(tmp, "fox.n2d")
out_path = os.path.join(tmp, "fox_rt.ssf")
save_n2d(n2d, n2d_path)

ctx = CompilationContext(n2d_path=n2d_path, shared_dir=tmp, output_path=out_path, sdk_path=None)
pipeline = create_default_pipeline()
pipeline.execute(ctx)

rt_n2d_to_swf = dict(ctx.lib_to_swf_id)

# Collect LL2 tags
og_ll2 = {}
for tt, body in iter_tags(raw):
    if tt == 36:
        cid = struct.unpack_from("<H", body, 0)[0]
        og_ll2[cid] = body

rt_swf = read_swf(out_path)
rt_ll2 = {}
for tt, body in iter_tags(rt_swf):
    if tt == 36:
        cid = struct.unpack_from("<H", body, 0)[0]
        rt_ll2[cid] = body

libs = n2d["libraries"]
bmp_libs = [lib for lib in libs if lib.get("type") == "bitmap"]

# Compare decompressed ARGB pixel data
pixel_identical = 0
pixel_different = 0
compressed_identical = 0
max_pixel_diff = 0
worst_bmp = None
sample_diffs = []

for lib in bmp_libs:
    n2d_id = lib["id"]
    og_swf_id = n2d_to_og_swf.get(n2d_id)
    rt_swf_id = rt_n2d_to_swf.get(n2d_id)
    
    if not og_swf_id or og_swf_id not in og_ll2:
        continue
    if not rt_swf_id or rt_swf_id not in rt_ll2:
        continue
    
    og_body = og_ll2[og_swf_id]
    rt_body = rt_ll2[rt_swf_id]
    
    # Check dimensions
    og_w = struct.unpack_from("<H", og_body, 3)[0]
    og_h = struct.unpack_from("<H", og_body, 5)[0]
    rt_w = struct.unpack_from("<H", rt_body, 3)[0]
    rt_h = struct.unpack_from("<H", rt_body, 5)[0]
    
    if og_w != rt_w or og_h != rt_h:
        print(f"DIM MISMATCH: lib={n2d_id} OG={og_w}x{og_h} RT={rt_w}x{rt_h}")
        continue
    
    # Decompress and compare raw ARGB pixels
    og_fmt = og_body[2]
    rt_fmt = rt_body[2]
    og_off = 8 if og_fmt == 3 else 7  # format 3 has extra colorTableSize byte
    rt_off = 8 if rt_fmt == 3 else 7
    try:
        og_raw = zlib.decompress(og_body[og_off:])
        rt_raw = zlib.decompress(rt_body[rt_off:])
    except zlib.error as e:
        print(f"Decompression error: lib={n2d_id} og_fmt={og_fmt} rt_fmt={rt_fmt}: {e}")
        continue
    
    if og_raw == rt_raw:
        pixel_identical += 1
        if og_body[7:] == rt_body[7:]:
            compressed_identical += 1
    else:
        pixel_different += 1
        # Find max diff per channel
        max_d = 0
        diff_channels = 0
        for j in range(min(len(og_raw), len(rt_raw))):
            d = abs(og_raw[j] - rt_raw[j])
            if d > 0:
                diff_channels += 1
            if d > max_d:
                max_d = d
        if max_d > max_pixel_diff:
            max_pixel_diff = max_d
            worst_bmp = (n2d_id, og_w, og_h, max_d, diff_channels, len(og_raw))
        if len(sample_diffs) < 5:
            sample_diffs.append((n2d_id, og_w, og_h, max_d, diff_channels, len(og_raw)))

print(f"\nBitmap pixel comparison (LL2 vs LL2):")
print(f"  Pixel-identical: {pixel_identical}")
print(f"  Pixel-different: {pixel_different}")
print(f"  Compressed-identical: {compressed_identical}")
print(f"  Max per-channel diff: {max_pixel_diff}")

if worst_bmp:
    nid, w, h, md, dc, totb = worst_bmp
    print(f"\n  Worst bitmap: lib={nid} {w}x{h}, max channel diff={md}, "
          f"differing channels={dc}/{totb} ({100*dc/totb:.1f}%)")

if sample_diffs:
    print(f"\n  Sample diffs:")
    for nid, w, h, md, dc, totb in sample_diffs:
        print(f"    lib={nid} {w}x{h}: max_diff={md}, diff_channels={dc}/{totb} ({100*dc/totb:.1f}%)")

import shutil
shutil.rmtree(tmp, ignore_errors=True)
