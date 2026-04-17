"""Compare OG shapes vs RT shapes using N2D library as the bridge.
For each N2D shape library entry, find its OG SWF charId and RT SWF charId,
then compare the tag bodies."""
import sys, os, struct, zlib, tempfile, io
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

# Import
from swf_to_n2d import parse_swf, N2DBuilder, save_n2d

raw = read_swf(OG)
header, tags = parse_swf(raw)
builder = N2DBuilder(header, "fox")
builder.catalog_swf_tags(tags)
builder.frame_scripts = {}
builder.build_all()
n2d = builder.to_n2d_json()

# The N2DBuilder has swf_to_n2d mapping: OG SWF charId -> N2D lib id
og_swf_to_n2d = dict(builder.swf_to_n2d)  # {og_swf_char_id: n2d_lib_id}
n2d_to_og_swf = {v: k for k, v in og_swf_to_n2d.items()}

print(f"OG SWF chars mapped: {len(og_swf_to_n2d)}")

# Save and compile
tmp = tempfile.mkdtemp()
n2d_path = os.path.join(tmp, "fox.n2d")
out_path = os.path.join(tmp, "fox_rt.ssf")
save_n2d(n2d, n2d_path)

# We need to capture the RT lib_to_swf_id mapping from the compiler
from compile_n2d import N2DCompiler
from compilation_pipeline import create_default_pipeline, CompilationContext

ctx = CompilationContext(
    n2d_path=n2d_path,
    shared_dir=tmp,
    output_path=out_path,
    sdk_path=None
)
pipeline = create_default_pipeline()
pipeline.execute(ctx)

# Read the RT mapping
rt_n2d_to_swf = dict(ctx.lib_to_swf_id)  # {n2d_lib_id: rt_swf_char_id}

print(f"RT N2D->SWF mapped: {len(rt_n2d_to_swf)}")

# Collect OG and RT shape tags by charId
og_shapes = {}
for tt, body in iter_tags(raw):
    if tt in (2, 22, 32, 46, 83) and len(body) >= 2:
        cid = struct.unpack_from("<H", body, 0)[0]
        og_shapes[cid] = (tt, body)

rt_data = read_swf(out_path)
rt_shapes = {}
for tt, body in iter_tags(rt_data):
    if tt in (2, 22, 32, 46, 83) and len(body) >= 2:
        cid = struct.unpack_from("<H", body, 0)[0]
        rt_shapes[cid] = (tt, body)

# Also get bitmap tags
og_bmps = {}
for tt, body in iter_tags(raw):
    if tt in (20, 35, 36):
        cid = struct.unpack_from("<H", body, 0)[0]
        og_bmps[cid] = (tt, body)

rt_bmps = {}
for tt, body in iter_tags(rt_data):
    if tt in (20, 35, 36):
        cid = struct.unpack_from("<H", body, 0)[0]
        rt_bmps[cid] = (tt, body)

# Now compare each N2D shape library entry
libs = n2d["libraries"]
shape_libs = [lib for lib in libs if lib.get("type") == "shape" 
              and not lib.get("isFont") and not lib.get("isButton") 
              and not lib.get("isMorphShape") and not lib.get("isBinaryData")]

print(f"\nComparing {len(shape_libs)} shape library entries...")

TAG_NAMES = {2: "DS1", 22: "DS2", 32: "DS3", 46: "DMS", 83: "DS4"}

identical = 0
upgraded_identical = 0  # same body after type upgrade
type_upgraded = 0
body_different = 0
missing_og = 0
missing_rt = 0
size_diffs = []

for lib in shape_libs:
    n2d_id = lib["id"]
    og_swf_id = n2d_to_og_swf.get(n2d_id)
    rt_swf_id = rt_n2d_to_swf.get(n2d_id)
    
    if not og_swf_id or og_swf_id not in og_shapes:
        missing_og += 1
        continue
    if not rt_swf_id or rt_swf_id not in rt_shapes:
        missing_rt += 1
        continue
    
    og_tt, og_body = og_shapes[og_swf_id]
    rt_tt, rt_body = rt_shapes[rt_swf_id]
    
    # Strip charId for comparison (first 2 bytes)
    og_data = og_body[2:]
    rt_data_inner = rt_body[2:]
    
    if og_tt == rt_tt:
        if og_data == rt_data_inner:
            identical += 1
        else:
            body_different += 1
            if len(size_diffs) < 20:
                size_diffs.append((n2d_id, lib.get("name", "?"), og_swf_id, rt_swf_id,
                                   TAG_NAMES.get(og_tt, str(og_tt)), 
                                   TAG_NAMES.get(rt_tt, str(rt_tt)),
                                   len(og_data), len(rt_data_inner)))
    else:
        type_upgraded += 1

print(f"\nResults:")
print(f"  Same type, identical body: {identical}")
print(f"  Same type, different body: {body_different}")
print(f"  Type upgraded (expected): {type_upgraded}")
print(f"  Missing in OG: {missing_og}")
print(f"  Missing in RT: {missing_rt}")

if size_diffs:
    print(f"\nBody differences (same tag type):")
    for nid, name, ogid, rtid, ogtt, rttt, ogs, rts in size_diffs:
        print(f"  lib={nid} '{name}': OG swfId={ogid}({ogtt}) {ogs}B vs RT swfId={rtid}({rttt}) {rts}B  diff={rts-ogs:+d}B")

# Bitmap comparison using N2D mapping
bmp_libs = [lib for lib in libs if lib.get("type") == "bitmap"]
print(f"\nComparing {len(bmp_libs)} bitmap library entries...")

bmp_identical = 0
bmp_type_changed = 0
bmp_body_diff = 0
bmp_dim_mismatch = 0

for lib in bmp_libs:
    n2d_id = lib["id"]
    og_swf_id = n2d_to_og_swf.get(n2d_id)
    rt_swf_id = rt_n2d_to_swf.get(n2d_id)
    
    if not og_swf_id or og_swf_id not in og_bmps:
        continue
    if not rt_swf_id or rt_swf_id not in rt_bmps:
        continue
    
    og_tt, og_body = og_bmps[og_swf_id]
    rt_tt, rt_body = rt_bmps[rt_swf_id]
    
    if og_tt != rt_tt:
        bmp_type_changed += 1
        # Check dimension match for JPEG3->Lossless2
        if og_tt == 35 and rt_tt == 36:
            # Get RT dims
            rt_w = struct.unpack_from("<H", rt_body, 3)[0]
            rt_h = struct.unpack_from("<H", rt_body, 5)[0]
            # Get OG JPEG dims
            alpha_off = struct.unpack_from("<I", og_body, 2)[0]
            jpeg_data = og_body[6:6+alpha_off]
            if jpeg_data[:4] == b'\xff\xd9\xff\xd8':
                jpeg_data = jpeg_data[4:]
            from PIL import Image
            img = Image.open(io.BytesIO(jpeg_data))
            og_w, og_h = img.size
            if og_w != rt_w or og_h != rt_h:
                print(f"  JPEG3->LL2 DIM MISMATCH: lib={n2d_id} '{lib.get('name','')}' OG={og_w}x{og_h} RT={rt_w}x{rt_h}")
                bmp_dim_mismatch += 1
            else:
                print(f"  JPEG3->LL2 dims match: lib={n2d_id} {og_w}x{og_h}")
    elif og_tt == rt_tt == 36:
        if og_body[2:] == rt_body[2:]:  # skip charId
            bmp_identical += 1
        else:
            bmp_body_diff += 1

print(f"\nBitmap results:")
print(f"  Same type, identical: {bmp_identical}")
print(f"  Same type, body differs: {bmp_body_diff}")
print(f"  Type changed (JPEG3->LL2): {bmp_type_changed}")
print(f"  Dimension mismatches: {bmp_dim_mismatch}")

import shutil
shutil.rmtree(tmp, ignore_errors=True)
