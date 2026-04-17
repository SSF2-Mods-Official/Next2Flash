"""Compare DECODED pixel data between OG bitmaps and our compiled RT bitmaps.

The OG uses format 3 (palette) for 512/625 bitmaps.
Our RT always uses format 5 (32-bit ARGB).
This script decodes BOTH to RGBA and compares pixel values.
Also checks for double-premultiplication issues.
"""
import sys, struct, zlib, os
sys.path.insert(0, os.path.dirname(__file__))

from swf_parser import parse_swf
from swf_to_n2d import decode_lossless_to_rgba

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"

TAG_DEFINE_BITS_LOSSLESS = 20
TAG_DEFINE_BITS_LOSSLESS2 = 36

def parse_bitmaps(swf_path):
    """Parse all bitmap tags → dict of {charId: (tag_type, width, height, rgba_bytes)}"""
    with open(swf_path, 'rb') as f:
        data = f.read()
    tags = parse_swf(data)
    bitmaps = {}
    for t in tags:
        if t.tag_type in (TAG_DEFINE_BITS_LOSSLESS, TAG_DEFINE_BITS_LOSSLESS2):
            cid = struct.unpack_from('<H', t.data, 0)[0]
            body = t.data[2:]
            fmt = body[0]
            w = struct.unpack_from('<H', body, 1)[0]
            h = struct.unpack_from('<H', body, 3)[0]
            dw, dh, rgba = decode_lossless_to_rgba(t.tag_type, body)
            bitmaps[cid] = (t.tag_type, fmt, w, h, dw, dh, rgba)
    return bitmaps

print("Parsing OG bitmaps...")
og_bitmaps = parse_bitmaps(OG)

# Count formats
fmt3_count = sum(1 for v in og_bitmaps.values() if v[1] == 3)
fmt5_count = sum(1 for v in og_bitmaps.values() if v[1] == 5)
print(f"OG: {len(og_bitmaps)} bitmaps, format3={fmt3_count}, format5={fmt5_count}")

# Check: for format 3 bitmaps, does the decoded RGBA have correct size?
bad_size = 0
good_size = 0
for cid, (tt, fmt, w, h, dw, dh, rgba) in og_bitmaps.items():
    expected_bytes = dw * dh * 4
    actual_bytes = len(rgba)
    if expected_bytes != actual_bytes:
        if bad_size < 5:
            print(f"  BAD SIZE: cid={cid} fmt={fmt} dims={dw}x{dh} expected={expected_bytes} actual={actual_bytes}")
        bad_size += 1
    else:
        good_size += 1
print(f"Size check: {good_size} OK, {bad_size} BAD")

# Now: round-trip test. Take OG decoded RGBA, re-encode as LL2 format 5, decode again.
# If pixels don't match, we have a premultiply round-trip issue.
from bitmap_converter import build_define_bits_lossless2

print("\nRound-trip test (decode OG → encode as LL2 fmt5 → decode back)...")
mismatch_count = 0
exact_match = 0
total_tested = 0
worst_diff = 0
worst_cid = None

for cid, (tt, fmt, w, h, dw, dh, rgba) in sorted(og_bitmaps.items()):
    if not rgba or dw == 0 or dh == 0:
        continue
    total_tested += 1
    
    # Re-encode: RGBA → LL2 tag
    tag_bytes = build_define_bits_lossless2(9999, dw, dh, rgba)
    
    # Parse the tag we just built to extract the body
    # Tag header: short form (tag_type<<6 | len) or long form
    tag_code_and_len = struct.unpack_from('<H', tag_bytes, 0)[0]
    tag_code = tag_code_and_len >> 6
    tag_len = tag_code_and_len & 0x3F
    if tag_len == 0x3F:
        tag_len = struct.unpack_from('<I', tag_bytes, 2)[0]
        body_start = 6
    else:
        body_start = 2
    
    rt_body = tag_bytes[body_start:]
    rt_cid = struct.unpack_from('<H', rt_body, 0)[0]
    rt_body_after_cid = rt_body[2:]
    rt_fmt = rt_body_after_cid[0]
    
    # Decode back
    dw2, dh2, rgba2 = decode_lossless_to_rgba(TAG_DEFINE_BITS_LOSSLESS2, rt_body_after_cid)
    
    if dw2 != dw or dh2 != dh:
        print(f"  DIM MISMATCH: cid={cid} orig={dw}x{dh} rt={dw2}x{dh2}")
        mismatch_count += 1
        continue
    
    if len(rgba) != len(rgba2):
        print(f"  LEN MISMATCH: cid={cid} orig_len={len(rgba)} rt_len={len(rgba2)}")
        mismatch_count += 1
        continue
    
    # Compare pixels
    max_diff = 0
    diff_channels = 0
    total_channels = len(rgba)
    for i in range(len(rgba)):
        d = abs(rgba[i] - rgba2[i])
        if d > 0:
            diff_channels += 1
        if d > max_diff:
            max_diff = d
    
    if max_diff == 0:
        exact_match += 1
    else:
        mismatch_count += 1
        pct = 100.0 * diff_channels / total_channels
        if max_diff > worst_diff:
            worst_diff = max_diff
            worst_cid = cid
        if mismatch_count <= 10:
            print(f"  PIXEL DIFF: cid={cid} fmt={fmt} {dw}x{dh} max_diff={max_diff} "
                  f"diff_channels={diff_channels}/{total_channels} ({pct:.1f}%)")

print(f"\nResults: {total_tested} tested, {exact_match} exact, {mismatch_count} mismatched")
print(f"Worst diff: {worst_diff} at cid={worst_cid}")

# Extra: check which alpha values exist in format 3 bitmaps
print("\nAlpha value analysis for format 3 bitmaps:")
has_partial_alpha = 0
all_binary_alpha = 0
for cid, (tt, fmt, w, h, dw, dh, rgba) in og_bitmaps.items():
    if fmt != 3 or not rgba:
        continue
    alphas = set(rgba[3::4])
    partial = alphas - {0, 255}
    if partial:
        has_partial_alpha += 1
        if has_partial_alpha <= 3:
            print(f"  cid={cid}: unique alphas = {sorted(alphas)}")
    else:
        all_binary_alpha += 1
print(f"Format 3 bitmaps: {all_binary_alpha} binary alpha, {has_partial_alpha} with partial alpha")
