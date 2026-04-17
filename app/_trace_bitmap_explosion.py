"""Trace the bitmap explosion: count how many NEW bitmap tags get created
during shape compilation via _resolve_bitmap_fills."""
import sys, os, struct, zlib
sys.path.insert(0, os.path.dirname(__file__))

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"

# Full import
from swf_to_n2d import parse_swf, N2DBuilder

with open(OG, "rb") as f:
    raw = f.read()
if raw[:3] == b"CWS":
    raw = raw[:8] + zlib.decompress(raw[8:])

header, tags = parse_swf(raw)
builder = N2DBuilder(header, "fox")
builder.catalog_swf_tags(tags)
builder.frame_scripts = {}
builder.build_all()
n2d = builder.to_n2d_json()
libs = n2d["libraries"]

from collections import Counter
types = Counter(lib.get("type") for lib in libs)
print(f"Library: {len(libs)} items: {dict(types)}")

# Now compile with tracing
from compile_n2d import N2DCompiler
from shape_converter import BitmapFill, parse_next2d_shape_buffer

# Count bitmap fills and track resolution
bitmap_lib_ids = {lib["id"] for lib in libs if lib.get("type") == "bitmap"}
print(f"Bitmap library entries: {len(bitmap_lib_ids)}")

# Manually trace what happens to bitmap fills during shape parsing
total_bmp_fills = 0
fills_with_lib_id = 0
fills_no_lib_id = 0
fills_with_pixel_data = 0

for lib in libs:
    if lib.get("type") != "shape":
        continue
    if lib.get("isFont") or lib.get("isButton") or lib.get("isMorphShape") or lib.get("isBinaryData"):
        continue
    recodes = lib.get("recodes", [])
    if not recodes:
        continue
    try:
        fill_styles, line_styles, sub_paths = parse_next2d_shape_buffer(recodes)
    except Exception as e:
        continue
    
    for fs in fill_styles:
        if isinstance(fs, BitmapFill):
            total_bmp_fills += 1
            if fs.bitmap_lib_id and fs.bitmap_lib_id > 0:
                fills_with_lib_id += 1
            else:
                fills_no_lib_id += 1
            if fs.pixel_data and len(fs.pixel_data) > 4:
                fills_with_pixel_data += 1

print(f"\nBitmap fills in all shapes: {total_bmp_fills}")
print(f"  With bitmap_lib_id: {fills_with_lib_id}")
print(f"  Without bitmap_lib_id: {fills_no_lib_id}")
print(f"  With embedded pixel data (>4 bytes): {fills_with_pixel_data}")

# Now do actual compilation and count bitmap tags
print("\n=== COMPILING ===")
compiler = N2DCompiler(n2d)
swf_out = compiler.compile()
print(f"Output SWF: {len(swf_out)} bytes")

# Count bitmap tags in output
pos = 8
nbits = (swf_out[pos] >> 3) & 0x1F
total_bits = 5 + nbits * 4
pos += (total_bits + 7) // 8
pos += 4
bmp_tag_count = 0
shape_tag_count = 0
while pos < len(swf_out):
    tc = struct.unpack_from("<H", swf_out, pos)[0]
    tt = tc >> 6
    length = tc & 0x3F
    pos += 2
    if length == 0x3F:
        length = struct.unpack_from("<I", swf_out, pos)[0]
        pos += 4
    if tt in (20, 36, 35, 21, 6, 90):
        bmp_tag_count += 1
    if tt in (2, 22, 32, 46, 83):  # DefineShape 1-4, DefineShape
        shape_tag_count += 1
    pos += length
    if tt == 0:
        break

print(f"Bitmap tags in output: {bmp_tag_count} (OG has 627)")
print(f"Shape tags in output: {shape_tag_count}")
print(f"Extra bitmaps: {bmp_tag_count - 627}")
