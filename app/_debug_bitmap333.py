"""Deep dive into bitmap lib=333 (18x22) — why is it 96.6% different?"""
import sys, os, struct, zlib
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

from swf_to_n2d import parse_swf, N2DBuilder

raw = read_swf(OG)
header, tags = parse_swf(raw)
builder = N2DBuilder(header, "fox")
builder.catalog_swf_tags(tags)
builder.frame_scripts = {}
builder.build_all()
n2d = builder.to_n2d_json()

og_swf_to_n2d = dict(builder.swf_to_n2d)
n2d_to_og_swf = {v: k for k, v in og_swf_to_n2d.items()}

# Find lib 333
libs = n2d["libraries"]
lib333 = [l for l in libs if l["id"] == 333][0]
print(f"Library entry 333:")
print(f"  type: {lib333.get('type')}")
print(f"  name: {lib333.get('name')}")
print(f"  width: {lib333.get('width')}")
print(f"  height: {lib333.get('height')}")
print(f"  buffer length: {len(lib333.get('buffer', ''))}")

og_swf_id = n2d_to_og_swf[333]
print(f"  OG SWF charId: {og_swf_id}")

# Get OG tag
for tt, body in iter_tags(raw):
    if tt == 36 and struct.unpack_from("<H", body, 0)[0] == og_swf_id:
        print(f"\nOG tag:")
        fmt = body[2]
        w = struct.unpack_from("<H", body, 3)[0]
        h = struct.unpack_from("<H", body, 5)[0]
        off = 8 if fmt == 3 else 7
        og_raw = zlib.decompress(body[off:])
        print(f"  Format: {fmt}")
        print(f"  Dimensions: {w}x{h}")
        print(f"  Compressed size: {len(body[off:])}")
        print(f"  Decompressed size: {len(og_raw)}")
        print(f"  Expected size (ARGB): {w * h * 4}")
        
        # Show first few pixels (ARGB)
        print(f"  First 10 pixels (ARGB):")
        for p in range(min(10, w * h)):
            a = og_raw[p*4]
            r = og_raw[p*4+1]
            g = og_raw[p*4+2]
            b = og_raw[p*4+3]
            print(f"    [{p}] A={a:3d} R={r:3d} G={g:3d} B={b:3d}")
        break

# Now check what the N2D buffer contains
buf = lib333.get("buffer", "")
if isinstance(buf, str):
    import base64
    try:
        pixel_data = base64.b64decode(buf)
    except:
        pixel_data = bytes(ord(c) for c in buf)
elif isinstance(buf, (bytes, bytearray)):
    pixel_data = bytes(buf)
else:
    pixel_data = bytes(buf)

print(f"\nN2D buffer:")
print(f"  Raw buffer length: {len(pixel_data)}")
n2d_w = lib333.get("width", 1)
n2d_h = lib333.get("height", 1)
print(f"  Expected RGBA size: {n2d_w * n2d_h * 4}")

# Show first few pixels (RGBA)
print(f"  First 10 pixels (RGBA):")
for p in range(min(10, n2d_w * n2d_h)):
    if p * 4 + 3 < len(pixel_data):
        r = pixel_data[p*4]
        g = pixel_data[p*4+1]
        b = pixel_data[p*4+2]
        a = pixel_data[p*4+3]
        print(f"    [{p}] R={r:3d} G={g:3d} B={b:3d} A={a:3d}")

# Now re-encode using our bitmap_converter
from bitmap_converter import build_define_bits_lossless2
tag_bytes = build_define_bits_lossless2(999, n2d_w, n2d_h, pixel_data)

# Parse the tag we just built
tag_header = struct.unpack_from("<H", tag_bytes, 0)[0]
tag_type = tag_header >> 6
tag_len_short = tag_header & 0x3F
if tag_len_short == 0x3F:
    tag_len = struct.unpack_from("<I", tag_bytes, 2)[0]
    body_start = 6
else:
    tag_len = tag_len_short
    body_start = 2

rt_body = tag_bytes[body_start:]
rt_fmt = rt_body[2]
rt_w = struct.unpack_from("<H", rt_body, 3)[0]
rt_h = struct.unpack_from("<H", rt_body, 5)[0]
rt_off = 8 if rt_fmt == 3 else 7
rt_raw = zlib.decompress(rt_body[rt_off:])

print(f"\nRT tag (rebuilt):")
print(f"  Format: {rt_fmt}")
print(f"  Dimensions: {rt_w}x{rt_h}")
print(f"  Decompressed size: {len(rt_raw)}")

# Show first few pixels (ARGB — should be premultiplied)
print(f"  First 10 pixels (ARGB premultiplied):")
for p in range(min(10, rt_w * rt_h)):
    a = rt_raw[p*4]
    r = rt_raw[p*4+1]
    g = rt_raw[p*4+2]
    b = rt_raw[p*4+3]
    print(f"    [{p}] A={a:3d} R={r:3d} G={g:3d} B={b:3d}")

# Pixel-by-pixel comparison
print(f"\nPixel comparison (first 10):")
for p in range(min(10, min(len(og_raw)//4, len(rt_raw)//4))):
    oa, ora, oga, oba = og_raw[p*4], og_raw[p*4+1], og_raw[p*4+2], og_raw[p*4+3]
    ra, rr, rg, rb = rt_raw[p*4], rt_raw[p*4+1], rt_raw[p*4+2], rt_raw[p*4+3]
    match = "OK" if oa == ra and ora == rr and oga == rg and oba == rb else "DIFF"
    print(f"  [{p}] OG: A={oa:3d} R={ora:3d} G={oga:3d} B={oba:3d}  "
          f"RT: A={ra:3d} R={rr:3d} G={rg:3d} B={rb:3d}  {match}")

# Check if OG format is actually format 3 (palette)
for tt, body in iter_tags(raw):
    if tt == 36 and struct.unpack_from("<H", body, 0)[0] == og_swf_id:
        fmt = body[2]
        if fmt == 3:
            ct_size = body[7] + 1  # color table entries
            print(f"\n*** OG uses FORMAT 3 (palette) with {ct_size} colors!")
            print(f"  After palette: pixel indices, not ARGB")
            # Decode palette
            palette_data = zlib.decompress(body[8:])
            print(f"  Decompressed palette+indices: {len(palette_data)} bytes")
            print(f"  First 5 palette entries (ARGB):")
            for c in range(min(5, ct_size)):
                pa, pr, pg, pb = palette_data[c*4], palette_data[c*4+1], palette_data[c*4+2], palette_data[c*4+3]
                print(f"    [{c}] A={pa} R={pr} G={pg} B={pb}")
        elif fmt == 5:
            print(f"\n  OG uses FORMAT 5 (32-bit ARGB)")
        break
