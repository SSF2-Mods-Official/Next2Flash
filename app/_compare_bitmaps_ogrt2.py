"""Find the 2 OG JPEG3 bitmaps in RT by dimensions, and analyze bitmap explosion."""
import struct, zlib, io
from collections import defaultdict

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\fox.ssf"

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
        tag_code_and_len = struct.unpack_from("<H", data, pos)[0]
        tag_type = tag_code_and_len >> 6
        length = tag_code_and_len & 0x3F
        pos += 2
        if length == 0x3F:
            length = struct.unpack_from("<I", data, pos)[0]
            pos += 4
        body = data[pos:pos+length]
        yield tag_type, body
        pos += length
        if tag_type == 0:
            break

def get_lossless2_dims(body):
    """Get (charId, w, h, format, decompressed_size) from tag 36 body"""
    cid = struct.unpack_from("<H", body, 0)[0]
    fmt = body[2]
    w = struct.unpack_from("<H", body, 3)[0]
    h = struct.unpack_from("<H", body, 5)[0]
    try:
        raw = zlib.decompress(body[7:])
        dsize = len(raw)
    except:
        dsize = -1
    return cid, w, h, fmt, dsize

def get_jpeg3_info(body):
    """Get (charId, w, h, alpha_off) from tag 35 body"""
    cid = struct.unpack_from("<H", body, 0)[0]
    alpha_off = struct.unpack_from("<I", body, 2)[0]
    jpeg_data = body[6:6+alpha_off]
    if jpeg_data[:4] == b'\xff\xd9\xff\xd8':
        jpeg_data = jpeg_data[4:]
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(jpeg_data))
        w, h = img.size
    except:
        w, h = 0, 0
    return cid, w, h, alpha_off

print("Loading OG...")
og_data = read_swf(OG)
print("Loading RT...")
rt_data = read_swf(RT)

# Collect all bitmaps from both
og_bitmaps = []  # (tag_type, charId, w, h, body_size, body)
rt_bitmaps = []

for tt, body in iter_tags(og_data):
    if tt == 36:
        cid, w, h, fmt, ds = get_lossless2_dims(body)
        og_bitmaps.append((tt, cid, w, h, len(body), body))
    elif tt == 35:
        cid, w, h, ao = get_jpeg3_info(body)
        og_bitmaps.append((tt, cid, w, h, len(body), body))
    elif tt == 20:
        cid = struct.unpack_from("<H", body, 0)[0]
        og_bitmaps.append((tt, cid, 0, 0, len(body), body))

for tt, body in iter_tags(rt_data):
    if tt == 36:
        cid, w, h, fmt, ds = get_lossless2_dims(body)
        rt_bitmaps.append((tt, cid, w, h, len(body), body))
    elif tt == 35:
        cid, w, h, ao = get_jpeg3_info(body)
        rt_bitmaps.append((tt, cid, w, h, len(body), body))
    elif tt == 20:
        cid = struct.unpack_from("<H", body, 0)[0]
        rt_bitmaps.append((tt, cid, 0, 0, len(body), body))

print(f"OG bitmaps: {len(og_bitmaps)}")
print(f"RT bitmaps: {len(rt_bitmaps)}")

# Find the 2 JPEG3 bitmaps in OG
print("\n=== OG JPEG3 BITMAPS ===")
jpeg3_og = [(tt, cid, w, h, sz, body) for tt, cid, w, h, sz, body in og_bitmaps if tt == 35]
for tt, cid, w, h, sz, body in jpeg3_og:
    print(f"  charId={cid}, {w}x{h}, bodySize={sz}B")
    # Find ALL RT bitmaps with same dimensions
    matches = [(tt2, cid2, w2, h2, sz2) for tt2, cid2, w2, h2, sz2, _ in rt_bitmaps if w2 == w and h2 == h]
    print(f"  RT matches by dimension: {len(matches)}")
    for tt2, cid2, w2, h2, sz2 in matches:
        print(f"    RT charId={cid2}, {w2}x{h2}, bodySize={sz2}B (tag={tt2})")

# Analyze the bitmap explosion: what are all the RT dimension distributions?
print(f"\n=== BITMAP EXPLOSION ANALYSIS ===")
og_dims = defaultdict(int)
rt_dims = defaultdict(int)
for tt, cid, w, h, sz, _ in og_bitmaps:
    og_dims[(w,h)] += 1
for tt, cid, w, h, sz, _ in rt_bitmaps:
    rt_dims[(w,h)] += 1

# Find dimensions that only exist in RT (the extra bitmaps)
rt_only_dims = {}
for dim, count in rt_dims.items():
    og_count = og_dims.get(dim, 0)
    if count > og_count:
        rt_only_dims[dim] = (count, og_count, count - og_count)

print(f"Unique dimensions in OG: {len(og_dims)}")
print(f"Unique dimensions in RT: {len(rt_dims)}")
print(f"Dimensions with MORE in RT: {len(rt_only_dims)}")

total_extra = sum(v[2] for v in rt_only_dims.values())
print(f"Total extra bitmaps from dimension analysis: ~{total_extra}")

# Now match OG↔RT by SymbolClass if possible
print(f"\n=== SYMBOLCLASS BITMAP MATCHING ===")
og_symclass = {}
rt_symclass = {}
for tt, body in iter_tags(og_data):
    if tt == 76:  # SymbolClass
        count = struct.unpack_from("<H", body, 0)[0]
        pos = 2
        for _ in range(count):
            cid = struct.unpack_from("<H", body, pos)[0]
            pos += 2
            end = body.index(0, pos)
            name = body[pos:end].decode("utf-8", errors="replace")
            pos = end + 1
            og_symclass[cid] = name
for tt, body in iter_tags(rt_data):
    if tt == 76:
        count = struct.unpack_from("<H", body, 0)[0]
        pos = 2
        for _ in range(count):
            cid = struct.unpack_from("<H", body, pos)[0]
            pos += 2
            end = body.index(0, pos)
            name = body[pos:end].decode("utf-8", errors="replace")
            pos = end + 1
            rt_symclass[cid] = name

# Reverse: name → charId
og_name_to_cid = {v: k for k, v in og_symclass.items()}
rt_name_to_cid = {v: k for k, v in rt_symclass.items()}

# Check which OG bitmaps have SymbolClass names
og_bitmap_cids = {cid for _, cid, _, _, _, _ in og_bitmaps}
rt_bitmap_cids = {cid for _, cid, _, _, _, _ in rt_bitmaps}

og_named_bitmaps = og_bitmap_cids & set(og_symclass.keys())
rt_named_bitmaps = rt_bitmap_cids & set(rt_symclass.keys())
print(f"OG bitmaps with SymbolClass names: {len(og_named_bitmaps)}")
print(f"RT bitmaps with SymbolClass names: {len(rt_named_bitmaps)}")

# The JPEG3 bitmaps - do they have symbol names?
for tt, cid, w, h, sz, body in jpeg3_og:
    name = og_symclass.get(cid, "(none)")
    print(f"\n  OG JPEG3 charId={cid} name='{name}' {w}x{h}")
    if name != "(none)" and name in rt_name_to_cid:
        rt_cid = rt_name_to_cid[name]
        rt_match = [(tt2, cid2, w2, h2, sz2) for tt2, cid2, w2, h2, sz2, _ in rt_bitmaps if cid2 == rt_cid]
        for tt2, cid2, w2, h2, sz2 in rt_match:
            print(f"  RT match by name: charId={cid2} {w2}x{h2} bodySize={sz2}B tag={tt2}")
            if w != w2 or h != h2:
                print(f"  *** DIMENSION MISMATCH: OG {w}x{h} vs RT {w2}x{h2}")

# Full pixel-level compare for OG lossless2 vs RT lossless2 for first few bitmaps
# Match by dimension signature (w,h pair unique enough?)
print(f"\n=== LOSSLESS2 BODY-LEVEL COMPARISON (sample) ===")
# Build RT lookup: (w,h) → list of bodies
rt_by_dim = defaultdict(list)
for tt, cid, w, h, sz, body in rt_bitmaps:
    rt_by_dim[(w,h)].append((cid, body))

matched = 0
body_identical = 0
body_different = 0
sample_diffs = []
for tt, cid, w, h, sz, body in og_bitmaps:
    if tt != 36:
        continue
    candidates = rt_by_dim.get((w,h), [])
    if len(candidates) == 1:
        # Unique dimension match
        rt_cid, rt_body = candidates[0]
        matched += 1
        # Compare raw Lossless2 body (skip charId which differs)
        if body[2:] == rt_body[2:]:
            body_identical += 1
        else:
            body_different += 1
            if len(sample_diffs) < 5:
                # Find where they differ
                og_raw = zlib.decompress(body[7:])
                rt_raw = zlib.decompress(rt_body[7:])
                if len(og_raw) == len(rt_raw):
                    ndiff = sum(1 for a, b in zip(og_raw, rt_raw) if a != b)
                    sample_diffs.append((cid, rt_cid, w, h, len(og_raw), ndiff))
                else:
                    sample_diffs.append((cid, rt_cid, w, h, len(og_raw), f"len_diff:{len(og_raw)} vs {len(rt_raw)}"))

print(f"Uniquely matched by dimension: {matched}")
print(f"  Body identical (minus charId): {body_identical}")
print(f"  Body different: {body_different}")
for ogc, rtc, w, h, rawlen, ndiff in sample_diffs:
    print(f"    OG cid={ogc} → RT cid={rtc} {w}x{h}: {ndiff} bytes differ out of {rawlen}")
