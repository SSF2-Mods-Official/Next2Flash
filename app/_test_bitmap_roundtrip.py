"""
Diagnostic: Isolate bitmap corruption to decode→encode vs N2D storage.

For each DefineBitsLossless/2 bitmap in the OG SWF:
  1. Decode original tag → RGBA pixels (step A)
  2. Re-encode RGBA → new DefineBitsLossless2 tag
  3. Decode new tag → RGBA pixels (step B)
  4. Compare A vs B pixel-by-pixel
  5. Also test base64 round-trip: RGBA → b64 → bytes → compare
  6. Also test _decode_raw_body path

This tells us whether corruption is in decode/encode or in storage.
"""
import sys, os, struct, zlib, base64

sys.path.insert(0, os.path.dirname(__file__))

from swf_to_n2d import decode_lossless_to_rgba
from bitmap_converter import build_define_bits_lossless2
from swf_writer import TAG_DEFINE_BITS_LOSSLESS2

# ── Parse SWF tags ──────────────────────────────────────────────────
def parse_swf_tags(path):
    """Yield (tag_type, tag_data_bytes) from a SWF file."""
    with open(path, 'rb') as f:
        sig = f.read(3)
        if sig not in (b'FWS', b'CWS', b'ZWS'):
            raise ValueError(f"Not a SWF: {sig}")
        version = struct.unpack('<B', f.read(1))[0]
        file_len = struct.unpack('<I', f.read(4))[0]
        rest = f.read()
    if sig == b'CWS':
        rest = zlib.decompress(rest)
    elif sig == b'ZWS':
        import lzma
        rest = lzma.decompress(rest)
    # Skip RECT header (variable length)
    # RECT: Nbits(5 bits) then 4 × Nbits-bit fields
    nbits = rest[0] >> 3
    rect_bits = 5 + 4 * nbits
    rect_bytes = (rect_bits + 7) // 8
    offset = rect_bytes + 4  # RECT + FrameRate(2) + FrameCount(2)
    # Parse tag records
    while offset < len(rest):
        if offset + 2 > len(rest):
            break
        tag_code_and_len = struct.unpack_from('<H', rest, offset)[0]
        offset += 2
        tag_type = tag_code_and_len >> 6
        length = tag_code_and_len & 0x3F
        if length == 0x3F:
            if offset + 4 > len(rest):
                break
            length = struct.unpack_from('<I', rest, offset)[0]
            offset += 4
        data = rest[offset:offset + length]
        offset += length
        if tag_type == 0:  # End
            break
        yield tag_type, data


def decode_new_tag(tag_bytes):
    """Decode a freshly-built DefineBitsLossless2 tag → (w, h, rgba)."""
    # tag_bytes = tag header + body
    # Parse tag header
    off = 0
    tc = struct.unpack_from('<H', tag_bytes, off)[0]
    off += 2
    ttype = tc >> 6
    tlen = tc & 0x3F
    if tlen == 0x3F:
        tlen = struct.unpack_from('<I', tag_bytes, off)[0]
        off += 4
    body = tag_bytes[off:off + tlen]
    # body: charId(2) + format(1) + width(2) + height(2) + compressed
    # body_after_char_id = body[2:]
    return decode_lossless_to_rgba(TAG_DEFINE_BITS_LOSSLESS2, body[2:])


def compare_pixels(rgba_a, rgba_b, w, h):
    """Compare two RGBA buffers. Return (matching_pixels, total_pixels, max_diff, diff_channels)."""
    total = w * h
    matching = 0
    max_diff = 0
    diff_channels = 0
    for i in range(total):
        off = i * 4
        ra, ga, ba, aa = rgba_a[off], rgba_a[off+1], rgba_a[off+2], rgba_a[off+3]
        rb, gb, bb, ab = rgba_b[off], rgba_b[off+1], rgba_b[off+2], rgba_b[off+3]
        if ra == rb and ga == gb and ba == bb and aa == ab:
            matching += 1
        else:
            for ca, cb in [(ra,rb),(ga,gb),(ba,bb),(aa,ab)]:
                d = abs(ca - cb)
                if d > 0:
                    diff_channels += 1
                    max_diff = max(max_diff, d)
    return matching, total, max_diff, diff_channels


def main():
    if len(sys.argv) < 2:
        print("Usage: python _test_bitmap_roundtrip.py <path_to_og_swf>")
        sys.exit(1)

    swf_path = sys.argv[1]
    print(f"Reading: {swf_path}")

    # Collect all DefineBitsLossless/2 tags
    TAG_LL = 20
    TAG_LL2 = 36
    bitmaps = []
    for tag_type, data in parse_swf_tags(swf_path):
        if tag_type in (TAG_LL, TAG_LL2) and len(data) >= 7:
            char_id = struct.unpack_from('<H', data, 0)[0]
            body_after_cid = data[2:]
            fmt = body_after_cid[0]
            bitmaps.append((char_id, tag_type, fmt, body_after_cid))

    print(f"Found {len(bitmaps)} lossless bitmaps")
    fmt3_count = sum(1 for _, _, f, _ in bitmaps if f == 3)
    fmt5_count = sum(1 for _, _, f, _ in bitmaps if f == 5)
    print(f"  Format 3 (palette): {fmt3_count}")
    print(f"  Format 5 (32-bit):  {fmt5_count}")

    # ── Test 1: Decode → Encode → Decode round-trip ─────────────
    print("\n=== TEST 1: Decode → Encode → Decode ===")
    test1_pass = 0
    test1_fail = 0
    test1_errors = []

    for char_id, tag_type, fmt, body in bitmaps:
        w, h, rgba_a = decode_lossless_to_rgba(tag_type, body)
        if not rgba_a or w == 0 or h == 0:
            continue

        # Re-encode to DefineBitsLossless2
        new_tag = build_define_bits_lossless2(9999, w, h, rgba_a)
        # Decode the new tag
        w2, h2, rgba_b = decode_new_tag(new_tag)

        if w != w2 or h != h2:
            test1_fail += 1
            test1_errors.append(f"  cid={char_id} fmt={fmt}: dims mismatch {w}x{h} vs {w2}x{h2}")
            continue

        if rgba_a == rgba_b:
            test1_pass += 1
        else:
            # The re-encoded tag is format 5 (ARGB premultiplied then demultiplied)
            # Premultiply round-trip can lose precision for partially transparent pixels
            matching, total, max_diff, diff_ch = compare_pixels(rgba_a, rgba_b, w, h)
            pct = matching / total * 100
            if max_diff <= 1:
                # Rounding error from premultiply → demultiply
                test1_pass += 1
            else:
                test1_fail += 1
                test1_errors.append(
                    f"  cid={char_id} fmt={fmt} {w}x{h}: "
                    f"{total-matching}/{total} pixels differ, max_diff={max_diff}, diff_channels={diff_ch}"
                )

    print(f"  PASS: {test1_pass}  FAIL: {test1_fail}")
    for e in test1_errors[:20]:
        print(e)
    if len(test1_errors) > 20:
        print(f"  ...and {len(test1_errors)-20} more")

    # ── Test 2: Base64 round-trip ────────────────────────────────
    print("\n=== TEST 2: Base64 round-trip (RGBA → b64 → bytes) ===")
    test2_pass = 0
    test2_fail = 0

    for char_id, tag_type, fmt, body in bitmaps:
        w, h, rgba = decode_lossless_to_rgba(tag_type, body)
        if not rgba:
            continue
        # Simulate the N2D storage path: RGBA → b64 → decode
        b64_str = 'b64:' + base64.b64encode(rgba).decode('ascii')
        restored = base64.b64decode(b64_str[4:])
        if rgba == restored:
            test2_pass += 1
        else:
            test2_fail += 1
            if test2_fail <= 5:
                print(f"  FAIL cid={char_id}: len {len(rgba)} vs {len(restored)}")

    print(f"  PASS: {test2_pass}  FAIL: {test2_fail}")

    # ── Test 3: Full pipeline (decode → b64 → _decode_raw_body → encode → decode) ──
    print("\n=== TEST 3: Full N2D pipeline simulation ===")
    from compile_n2d import _decode_raw_body
    test3_pass = 0
    test3_fail = 0
    test3_errors = []

    for char_id, tag_type, fmt, body in bitmaps:
        w, h, rgba_a = decode_lossless_to_rgba(tag_type, body)
        if not rgba_a or w == 0:
            continue
        # Step 1: Store as b64 (what swf_to_n2d does)
        b64_str = 'b64:' + base64.b64encode(rgba_a).decode('ascii')
        # Step 2: Decode as compiler does
        pixel_data = _decode_raw_body(b64_str)
        # Step 3: Build new tag
        new_tag = build_define_bits_lossless2(9999, w, h, pixel_data)
        # Step 4: Decode new tag
        w2, h2, rgba_b = decode_new_tag(new_tag)

        if w != w2 or h != h2:
            test3_fail += 1
            continue

        if rgba_a == rgba_b:
            test3_pass += 1
        else:
            matching, total, max_diff, diff_ch = compare_pixels(rgba_a, rgba_b, w, h)
            if max_diff <= 1:
                test3_pass += 1
            else:
                test3_fail += 1
                test3_errors.append(
                    f"  cid={char_id} fmt={fmt} {w}x{h}: "
                    f"{total-matching}/{total} diff, max={max_diff}"
                )

    print(f"  PASS: {test3_pass}  FAIL: {test3_fail}")
    for e in test3_errors[:20]:
        print(e)

    # ── Test 4: Compare RT SWF bitmaps against OG directly ──────
    # If a second argument is given, compare OG vs RT bitmaps
    if len(sys.argv) >= 3:
        rt_path = sys.argv[2]
        print(f"\n=== TEST 4: OG vs RT bitmap comparison ===")
        print(f"RT: {rt_path}")
        rt_bitmaps = {}
        for tag_type, data in parse_swf_tags(rt_path):
            if tag_type in (TAG_LL, TAG_LL2) and len(data) >= 7:
                cid = struct.unpack_from('<H', data, 0)[0]
                rt_bitmaps[cid] = (tag_type, data[2:])

        # Build OG cid→rgba map
        og_by_dims = {}  # (w,h,pixel_hash) → rgba for matching
        og_list = []
        for char_id, tag_type, fmt, body in bitmaps:
            w, h, rgba = decode_lossless_to_rgba(tag_type, body)
            if rgba and w > 0:
                og_list.append((char_id, w, h, rgba))

        # RT bitmaps have different charIDs, so match by index order
        rt_list = []
        for cid in sorted(rt_bitmaps.keys()):
            tt, body = rt_bitmaps[cid]
            w, h, rgba = decode_lossless_to_rgba(tt, body)
            if rgba and w > 0:
                rt_list.append((cid, w, h, rgba))

        print(f"  OG bitmaps: {len(og_list)}, RT bitmaps: {len(rt_list)}")

        # Try matching by dimensions + pixel content
        matched = 0
        mismatched = 0
        for i, (og_cid, ow, oh, og_rgba) in enumerate(og_list):
            # Find RT bitmap with same dims
            best_match = None
            for j, (rt_cid, rw, rh, rt_rgba) in enumerate(rt_list):
                if rw == ow and rh == oh:
                    if og_rgba == rt_rgba:
                        best_match = ('exact', rt_cid)
                        break
            if best_match:
                matched += 1
            else:
                # Find closest by dims
                for j, (rt_cid, rw, rh, rt_rgba) in enumerate(rt_list):
                    if rw == ow and rh == oh:
                        m, t, md, dc = compare_pixels(og_rgba, rt_rgba, ow, oh)
                        if mismatched < 5:
                            print(f"  OG cid={og_cid} vs RT cid={rt_cid} {ow}x{oh}: "
                                  f"{t-m}/{t} pixels differ, max_diff={md}")
                        mismatched += 1
                        break

        print(f"  Exact matches: {matched}, Mismatches: {mismatched}")


if __name__ == '__main__':
    main()
