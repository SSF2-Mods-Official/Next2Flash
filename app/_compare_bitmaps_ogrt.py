"""Compare bitmap tags between OG and RT fox.ssf — identify corrupt/different bitmaps."""
import struct, zlib, sys, io
from collections import defaultdict

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\fox.ssf"

BITMAP_TAGS = {6: "DefineBits", 20: "DefineBitsLossless", 21: "DefineBitsJPEG2",
               35: "DefineBitsJPEG3", 36: "DefineBitsLossless2", 90: "DefineBitsJPEG4"}

def read_swf(path):
    with open(path, "rb") as f:
        data = f.read()
    sig = data[:3]
    if sig == b"CWS":
        data = data[:8] + zlib.decompress(data[8:])
    elif sig == b"ZWS":
        import lzma
        data = data[:8] + lzma.decompress(data[12:])
    return data

def iter_tags(data):
    pos = 8  # skip header
    # skip rect + frame info
    nbits = (data[pos] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    pos += (total_bits + 7) // 8
    pos += 4  # frame rate + frame count
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

def decode_lossless2(body):
    """Decode DefineBitsLossless2 tag body → (charId, w, h, format, pixel_count, raw_argb)"""
    char_id = struct.unpack_from("<H", body, 0)[0]
    bmp_format = body[2]
    w = struct.unpack_from("<H", body, 3)[0]
    h = struct.unpack_from("<H", body, 5)[0]
    compressed = body[7:]
    try:
        raw = zlib.decompress(compressed)
    except:
        raw = b""
    return char_id, w, h, bmp_format, len(raw), raw

def decode_lossless(body):
    """Decode DefineBitsLossless tag body"""
    char_id = struct.unpack_from("<H", body, 0)[0]
    bmp_format = body[2]
    w = struct.unpack_from("<H", body, 3)[0]
    h = struct.unpack_from("<H", body, 5)[0]
    compressed = body[7:] if bmp_format != 3 else body[8:]  # format 3 has colorTableSize
    return char_id, w, h, bmp_format, 0, b""

def decode_jpeg3(body):
    """Decode DefineBitsJPEG3 tag body → (charId, w, h, jpeg_len, alpha_len)"""
    char_id = struct.unpack_from("<H", body, 0)[0]
    alpha_off = struct.unpack_from("<I", body, 2)[0]
    jpeg_data = body[6:6+alpha_off]
    alpha_compressed = body[6+alpha_off:]
    # Get dimensions from JPEG
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(jpeg_data))
        w, h = img.size
    except:
        w, h = 0, 0
    alpha_len = len(alpha_compressed)
    return char_id, w, h, len(jpeg_data), alpha_len

def get_bitmaps(data):
    """Return dict: charId → (tag_type, tag_name, body, width, height)"""
    bitmaps = {}
    for tag_type, body in iter_tags(data):
        if tag_type in BITMAP_TAGS:
            char_id = struct.unpack_from("<H", body, 0)[0]
            if tag_type in (20, 36):
                cid, w, h, fmt, plen, raw = decode_lossless2(body) if tag_type == 36 else decode_lossless(body)
                bitmaps[char_id] = (tag_type, BITMAP_TAGS[tag_type], body, w, h)
            elif tag_type == 35:
                cid, w, h, jlen, alen = decode_jpeg3(body)
                bitmaps[char_id] = (tag_type, BITMAP_TAGS[tag_type], body, w, h)
            else:
                bitmaps[char_id] = (tag_type, BITMAP_TAGS[tag_type], body, 0, 0)
    return bitmaps

print("Loading OG...")
og_data = read_swf(OG)
print("Loading RT...")
rt_data = read_swf(RT)

og_bitmaps = get_bitmaps(og_data)
rt_bitmaps = get_bitmaps(rt_data)

print(f"\nOG bitmap count: {len(og_bitmaps)}")
print(f"RT bitmap count: {len(rt_bitmaps)}")

# Summary by tag type
og_types = defaultdict(int)
rt_types = defaultdict(int)
for cid, (tt, tn, body, w, h) in og_bitmaps.items():
    og_types[tn] += 1
for cid, (tt, tn, body, w, h) in rt_bitmaps.items():
    rt_types[tn] += 1

print(f"\nOG tag types: {dict(og_types)}")
print(f"RT tag types: {dict(rt_types)}")

# Find type changes
type_changes = defaultdict(int)
size_diffs = []
for cid in sorted(og_bitmaps.keys()):
    if cid not in rt_bitmaps:
        continue
    og_tt, og_tn, og_body, og_w, og_h = og_bitmaps[cid]
    # RT uses different charIds due to id reassignment, so match by index
    pass

# Since charIds are reassigned, let's match by position order
og_ordered = sorted(og_bitmaps.items())
rt_ordered = sorted(rt_bitmaps.items())

print(f"\nOG bitmap IDs: first={og_ordered[0][0]}, last={og_ordered[-1][0]}")
print(f"RT bitmap IDs: first={rt_ordered[0][0]}, last={rt_ordered[-1][0]}")

count = min(len(og_ordered), len(rt_ordered))
type_change_list = []
dim_mismatches = []
size_changes = []

for i in range(count):
    og_cid, (og_tt, og_tn, og_body, og_w, og_h) = og_ordered[i]
    rt_cid, (rt_tt, rt_tn, rt_body, rt_w, rt_h) = rt_ordered[i]
    
    if og_tt != rt_tt:
        type_change_list.append((i, og_cid, rt_cid, og_tn, rt_tn, og_w, og_h))
    
    # Compare dimensions for lossless tags
    if rt_tt == 36:
        _, rt_w2, rt_h2, rt_fmt, rt_plen, rt_raw = decode_lossless2(rt_body)
        expected_pixels = rt_w2 * rt_h2 * 4
        if rt_plen != expected_pixels and rt_plen > 0:
            dim_mismatches.append((i, rt_cid, rt_w2, rt_h2, rt_plen, expected_pixels))
    
    size_ratio = len(rt_body) / len(og_body) if len(og_body) > 0 else 999
    if size_ratio > 3.0 or size_ratio < 0.3:
        size_changes.append((i, og_cid, rt_cid, len(og_body), len(rt_body), size_ratio, og_tn, rt_tn))

print(f"\n=== TAG TYPE CHANGES ({len(type_change_list)}) ===")
for idx, og_cid, rt_cid, og_tn, rt_tn, w, h in type_change_list:
    print(f"  #{idx}: OG charId={og_cid} {og_tn} → RT charId={rt_cid} {rt_tn}  ({w}x{h})")

print(f"\n=== DIMENSION/PIXEL COUNT MISMATCHES ({len(dim_mismatches)}) ===")
for idx, cid, w, h, actual, expected in dim_mismatches:
    print(f"  #{idx}: RT charId={cid} {w}x{h} pixels={actual}B expected={expected}B  diff={actual-expected}B")

print(f"\n=== BIG SIZE CHANGES (>3x or <0.3x) ({len(size_changes)}) ===")
for idx, og_cid, rt_cid, og_sz, rt_sz, ratio, og_tn, rt_tn in size_changes[:20]:
    print(f"  #{idx}: OG cid={og_cid} {og_tn} {og_sz}B → RT cid={rt_cid} {rt_tn} {rt_sz}B  ({ratio:.1f}x)")

# Now do a pixel-level comparison for the JPEG3→Lossless2 conversions
if type_change_list:
    print(f"\n=== PIXEL COMPARISON FOR TYPE-CHANGED BITMAPS ===")
    from PIL import Image
    for idx, og_cid, rt_cid, og_tn, rt_tn, w, h in type_change_list:
        og_body = og_ordered[idx][1][2]
        rt_body = rt_ordered[idx][1][2]
        
        # Decode OG JPEG3
        if og_tn == "DefineBitsJPEG3":
            alpha_off = struct.unpack_from("<I", og_body, 2)[0]
            jpeg_data = og_body[6:6+alpha_off]
            alpha_compressed = og_body[6+alpha_off:]
            # Strip erroneous header
            if jpeg_data[:4] == b'\xff\xd9\xff\xd8':
                jpeg_data = jpeg_data[4:]
            img = Image.open(io.BytesIO(jpeg_data)).convert("RGBA")
            og_w, og_h = img.size
            og_pixels = bytearray(img.tobytes())
            # Apply alpha
            try:
                alpha_data = zlib.decompress(alpha_compressed)
                for p in range(og_w * og_h):
                    if p < len(alpha_data):
                        og_pixels[p*4 + 3] = alpha_data[p]
            except:
                pass
            print(f"\n  OG #{idx} cid={og_cid}: JPEG3 {og_w}x{og_h}, alpha={len(alpha_compressed)}B compressed")
        
        # Decode RT Lossless2
        if rt_tn == "DefineBitsLossless2":
            _, rt_w, rt_h, rt_fmt, rt_plen, rt_raw = decode_lossless2(rt_body)
            # Convert ARGB→RGBA for comparison  
            rt_pixels = bytearray(rt_plen)
            for p in range(0, rt_plen, 4):
                a = rt_raw[p]
                # Un-premultiply
                if a == 0:
                    rt_pixels[p:p+4] = b'\x00\x00\x00\x00'
                elif a == 255:
                    rt_pixels[p] = rt_raw[p+1]
                    rt_pixels[p+1] = rt_raw[p+2]
                    rt_pixels[p+2] = rt_raw[p+3]
                    rt_pixels[p+3] = 255
                else:
                    rt_pixels[p] = min(255, (rt_raw[p+1] * 255 + a//2) // a)
                    rt_pixels[p+1] = min(255, (rt_raw[p+2] * 255 + a//2) // a)
                    rt_pixels[p+2] = min(255, (rt_raw[p+3] * 255 + a//2) // a)
                    rt_pixels[p+3] = a
            print(f"  RT #{idx} cid={rt_cid}: Lossless2 {rt_w}x{rt_h}, format={rt_fmt}, decompressed={rt_plen}B")
            
            if og_w == rt_w and og_h == rt_h:
                # Compare pixel by pixel
                max_diff = 0
                diff_count = 0
                for p in range(min(len(og_pixels), len(rt_pixels))):
                    d = abs(og_pixels[p] - rt_pixels[p])
                    if d > 0:
                        diff_count += 1
                    if d > max_diff:
                        max_diff = d
                total = og_w * og_h * 4
                print(f"  Pixel diff: {diff_count}/{total} channels differ, max_diff={max_diff}")
            else:
                print(f"  DIMENSION MISMATCH: OG={og_w}x{og_h} RT={rt_w}x{rt_h}")
