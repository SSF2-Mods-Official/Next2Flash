"""Trace bitmap explosion — simpler approach using existing _verify_compile.py pattern."""
import sys, os, struct, zlib, tempfile
sys.path.insert(0, os.path.dirname(__file__))

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"

from swf_to_n2d import parse_swf, N2DBuilder, save_n2d
from compile_n2d import N2DCompiler

# Import
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

# Save to temp, compile
tmp = tempfile.mkdtemp()
n2d_path = os.path.join(tmp, "fox.n2d")
out_path = os.path.join(tmp, "fox_rt.ssf")
save_n2d(n2d, n2d_path)
print(f"Saved N2D: {os.path.getsize(n2d_path)} bytes")

# Compile
compiler = N2DCompiler(n2d_path, tmp, out_path)
compiler.compile()

with open(out_path, "rb") as f:
    rt_data = f.read()
print(f"Compiled SWF: {len(rt_data)} bytes")

# Count tags in OG vs RT
def count_tags(data):
    if data[:3] == b"CWS":
        data = data[:8] + zlib.decompress(data[8:])
    pos = 8
    nbits = (data[pos] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    pos += (total_bits + 7) // 8
    pos += 4
    counts = {}
    while pos < len(data):
        tc = struct.unpack_from("<H", data, pos)[0]
        tt = tc >> 6
        length = tc & 0x3F
        pos += 2
        if length == 0x3F:
            length = struct.unpack_from("<I", data, pos)[0]
            pos += 4
        counts[tt] = counts.get(tt, 0) + 1
        pos += length
        if tt == 0:
            break
    return counts

TAG_NAMES = {
    2: "DefineShape", 6: "DefineBits", 20: "DefineBitsLossless",
    21: "DefineBitsJPEG2", 22: "DefineShape2", 32: "DefineShape3",
    35: "DefineBitsJPEG3", 36: "DefineBitsLossless2", 39: "DefineSprite",
    46: "DefineShape4", 76: "SymbolClass", 82: "DoABC",
    83: "DefineShape4b", 90: "DefineBitsJPEG4"
}

og_counts = count_tags(raw)
rt_counts = count_tags(rt_data)

# Bitmap tags specifically
BMP_TAGS = {6, 20, 21, 35, 36, 90}
SHAPE_TAGS = {2, 22, 32, 46, 83}

og_bmps = sum(og_counts.get(t, 0) for t in BMP_TAGS)
rt_bmps = sum(rt_counts.get(t, 0) for t in BMP_TAGS)
og_shapes = sum(og_counts.get(t, 0) for t in SHAPE_TAGS)
rt_shapes = sum(rt_counts.get(t, 0) for t in SHAPE_TAGS)

print(f"\n=== TAG COUNTS ===")
print(f"{'Tag':<30} {'OG':>6} {'RT':>6} {'Diff':>6}")
print("-" * 50)
all_tags = sorted(set(og_counts.keys()) | set(rt_counts.keys()))
for t in all_tags:
    og_c = og_counts.get(t, 0)
    rt_c = rt_counts.get(t, 0)
    name = TAG_NAMES.get(t, f"Tag {t}")
    if og_c != rt_c:
        print(f"{name:<30} {og_c:>6} {rt_c:>6} {rt_c-og_c:>+6} ***")
    else:
        print(f"{name:<30} {og_c:>6} {rt_c:>6}")

print(f"\nTotal bitmaps: OG={og_bmps}, RT={rt_bmps}, diff={rt_bmps-og_bmps}")
print(f"Total shapes: OG={og_shapes}, RT={rt_shapes}, diff={rt_shapes-og_shapes}")

# Cleanup
import shutil
shutil.rmtree(tmp, ignore_errors=True)
