"""
Diagnose the bitmap re-encoding bug.

Takes OG bitmap tags, runs them through the exact same decode→encode cycle
used by the N2D pipeline, and compares the results byte-by-byte.

This will reveal:
1. Whether premultiplication round-trip corrupts pixel values
2. Whether zlib recompression alone causes structural differences
3. Which specific bitmaps are affected
"""
import struct, zlib, sys, os, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from swf_to_n2d import decode_lossless_to_rgba, TAG_DEFINE_BITS_LOSSLESS2
from bitmap_converter import build_define_bits_lossless2

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"

def read_swf(path):
    with open(path, 'rb') as f:
        data = f.read()
    sig = data[:3]
    if sig == b'CWS':
        body = zlib.decompress(data[8:])
    elif sig == b'FWS':
        body = data[8:]
    return body

def parse_rect(body):
    first = body[0]
    nbits = first >> 3
    total_bits = 5 + nbits * 4
    return (total_bits + 7) // 8

def extract_bitmap_tags(body):
    """Extract all LL2 tag bodies by charID."""
    pos = parse_rect(body) + 4  # RECT + fps(2) + frame_count(2)
    bitmaps = {}
    while pos < len(body):
        if pos + 2 > len(body): break
        tcl = struct.unpack_from('<H', body, pos)[0]
        tt = tcl >> 6
        tl = tcl & 0x3F
        hs = 2
        if tl == 0x3F:
            tl = struct.unpack_from('<I', body, pos + 2)[0]
            hs = 6
        tb = body[pos+hs:pos+hs+tl]
        if tt == 36 and len(tb) >= 2:  # LL2
            cid = struct.unpack_from('<H', tb, 0)[0]
            bitmaps[cid] = tb[2:]  # body after charID
        pos += hs + tl
        if tt == 0: break
    return bitmaps

def decompress_ll2(body_after_cid):
    """Decompress LL2 tag body → (format, width, height, decompressed_data)"""
    fmt = body_after_cid[0]
    w = struct.unpack_from('<H', body_after_cid, 1)[0]
    h = struct.unpack_from('<H', body_after_cid, 3)[0]
    if fmt == 3:
        cts = body_after_cid[5] + 1
        compressed = body_after_cid[6:]
        decompressed = zlib.decompress(compressed)
        return fmt, w, h, cts, decompressed
    elif fmt == 5:
        compressed = body_after_cid[5:]
        decompressed = zlib.decompress(compressed)
        return fmt, w, h, 0, decompressed
    return fmt, w, h, 0, b''

def main():
    print("Loading OG SWF...")
    body = read_swf(OG)
    og_bitmaps = extract_bitmap_tags(body)
    print(f"  {len(og_bitmaps)} bitmap tags")
    
    # Categorize
    fmt3_bitmaps = {}
    fmt5_bitmaps = {}
    for cid, bdata in og_bitmaps.items():
        fmt = bdata[0]
        if fmt == 3:
            fmt3_bitmaps[cid] = bdata
        elif fmt == 5:
            fmt5_bitmaps[cid] = bdata
    print(f"  fmt=3: {len(fmt3_bitmaps)}, fmt=5: {len(fmt5_bitmaps)}")
    
    # Test round-trip for format=5 bitmaps (the ones linked to BitmapData subclasses)
    print(f"\n=== FORMAT=5 ROUND-TRIP TEST ===")
    
    pixel_mismatch = 0
    pixel_match = 0
    zlib_diff = 0
    total = 0
    worst_diffs = []
    
    for cid in sorted(fmt5_bitmaps.keys()):
        bdata = fmt5_bitmaps[cid]
        total += 1
        
        # Step 1: Decode OG tag → RGBA (mimics import)
        w, h, rgba = decode_lossless_to_rgba(TAG_DEFINE_BITS_LOSSLESS2, bdata)
        if not rgba:
            continue
        
        # Step 2: Re-encode RGBA → LL2 tag (mimics export)
        re_encoded_tag = build_define_bits_lossless2(cid, w, h, rgba)
        
        # Step 3: Extract the body after tag header
        # Tag format: short/long header + charID(2) + body
        tcl = struct.unpack_from('<H', re_encoded_tag, 0)[0]
        tl = tcl & 0x3F
        if tl == 0x3F:
            re_body = re_encoded_tag[8:]  # 2 (tag code) + 4 (length) + 2 (charID)
        else:
            re_body = re_encoded_tag[4:]  # 2 (tag code) + 2 (charID)
        
        # Step 4: Decompress both and compare pixel data
        og_fmt, _, _, _, og_decomp = decompress_ll2(bdata)
        re_fmt, _, _, _, re_decomp = decompress_ll2(re_body)
        
        if og_decomp == re_decomp:
            pixel_match += 1
        else:
            pixel_mismatch += 1
            # Count differing bytes
            min_len = min(len(og_decomp), len(re_decomp))
            diff_bytes = sum(1 for i in range(min_len) if og_decomp[i] != re_decomp[i])
            diff_bytes += abs(len(og_decomp) - len(re_decomp))
            
            # Find max per-byte difference
            max_diff = 0
            max_diff_pos = -1
            for i in range(min_len):
                d = abs(og_decomp[i] - re_decomp[i])
                if d > max_diff:
                    max_diff = d
                    max_diff_pos = i
            
            worst_diffs.append((cid, w, h, diff_bytes, min_len, max_diff, max_diff_pos))
            
            if len(worst_diffs) <= 5 or max_diff > 2:
                print(f"  charID={cid} ({w}x{h}): {diff_bytes}/{min_len} bytes differ, max_diff={max_diff} at pos={max_diff_pos}")
                # Show context around worst diff
                if max_diff_pos >= 0:
                    # ARGB format: each pixel is 4 bytes (A, R, G, B)
                    pixel_idx = max_diff_pos // 4
                    channel = max_diff_pos % 4
                    channel_names = ['A', 'R', 'G', 'B']
                    p = pixel_idx * 4
                    if p + 4 <= min_len:
                        print(f"    Pixel {pixel_idx} channel {channel_names[channel]}:")
                        print(f"      OG:  A={og_decomp[p]:3d} R={og_decomp[p+1]:3d} G={og_decomp[p+2]:3d} B={og_decomp[p+3]:3d}")
                        print(f"      RT:  A={re_decomp[p]:3d} R={re_decomp[p+1]:3d} G={re_decomp[p+2]:3d} B={re_decomp[p+3]:3d}")
                        # Check premultiplication
                        a_og = og_decomp[p]
                        if 0 < a_og < 255:
                            print(f"    Partial alpha={a_og} - premultiplication round-trip error")
    
    print(f"\n  === SUMMARY (format=5) ===")
    print(f"  Total: {total}")
    print(f"  Pixel-identical after round-trip: {pixel_match}")
    print(f"  Pixel DIFFERS after round-trip: {pixel_mismatch}")
    
    if worst_diffs:
        worst_diffs.sort(key=lambda x: x[3], reverse=True)
        print(f"\n  Top 10 worst diffs:")
        for cid, w, h, db, ml, md, mdp in worst_diffs[:10]:
            pct = 100.0 * db / ml if ml else 0
            print(f"    charID={cid} ({w}x{h}): {db}/{ml} bytes ({pct:.1f}%), max_diff={md}")
    
    # Now check: what if we just use zlib level 9 like OG probably does?
    print(f"\n=== ZLIB COMPRESSION LEVEL TEST (charID=1001) ===")
    if 1001 in fmt5_bitmaps:
        bdata = fmt5_bitmaps[1001]
        og_fmt, w, h, _, og_decomp = decompress_ll2(bdata)
        print(f"  OG decompressed: {len(og_decomp)} bytes")
        
        # Try different zlib levels
        for level in range(1, 10):
            compressed = zlib.compress(og_decomp, level)
            og_compressed = bdata[5:]  # skip format(1) + w(2) + h(2)
            print(f"  zlib level {level}: {len(compressed)} bytes (OG compressed: {len(og_compressed)})")
            if compressed == og_compressed:
                print(f"    *** EXACT MATCH at level {level} ***")
    
    # Test: what if we skip un-premultiply → re-premultiply?
    print(f"\n=== PREMULTIPLICATION ANALYSIS ===")
    partial_alpha_bitmaps = []
    for cid in sorted(fmt5_bitmaps.keys()):
        bdata = fmt5_bitmaps[cid]
        fmt, w, h, _, decomp = decompress_ll2(bdata)
        if not decomp:
            continue
        # Check for partial alpha pixels (0 < A < 255)
        has_partial = False
        partial_count = 0
        for i in range(0, len(decomp), 4):
            a = decomp[i]  # ARGB: first byte is A
            if 0 < a < 255:
                has_partial = True
                partial_count += 1
        if has_partial:
            partial_alpha_bitmaps.append((cid, w, h, partial_count, len(decomp) // 4))
    
    print(f"  Bitmaps with partial alpha: {len(partial_alpha_bitmaps)}/{len(fmt5_bitmaps)}")
    for cid, w, h, pc, tp in partial_alpha_bitmaps[:20]:
        pct = 100.0 * pc / tp if tp else 0
        print(f"    charID={cid} ({w}x{h}): {pc}/{tp} pixels ({pct:.1f}%) have partial alpha")
    
    # Cross-reference: are ALL pixel-differing bitmaps ones with partial alpha?
    partial_cids = {cid for cid, _, _, _, _ in partial_alpha_bitmaps}
    mismatch_cids = {cid for cid, _, _, _, _, _, _ in worst_diffs}
    
    mismatch_without_partial = mismatch_cids - partial_cids
    partial_without_mismatch = partial_cids - mismatch_cids
    
    print(f"\n  Mismatch bitmaps WITHOUT partial alpha: {len(mismatch_without_partial)}")
    if mismatch_without_partial:
        print(f"    {sorted(mismatch_without_partial)[:20]}")
    print(f"  Partial alpha bitmaps WITHOUT mismatch: {len(partial_without_mismatch)}")

if __name__ == '__main__':
    main()
