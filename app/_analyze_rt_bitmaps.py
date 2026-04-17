"""
Investigate the 1506-bitmap explosion in the RT file.
Check for duplicates, 0-dimension bitmaps, oversized bitmaps, etc.
"""
import sys, os, struct, zlib, hashlib

sys.path.insert(0, os.path.dirname(__file__))
from swf_to_n2d import decode_lossless_to_rgba

TAG_LL = 20
TAG_LL2 = 36

def parse_swf_tags(path):
    with open(path, 'rb') as f:
        sig = f.read(3)
        version = struct.unpack('<B', f.read(1))[0]
        file_len = struct.unpack('<I', f.read(4))[0]
        rest = f.read()
    if sig == b'CWS':
        rest = zlib.decompress(rest)
    nbits = rest[0] >> 3
    rect_bytes = (5 + 4 * nbits + 7) // 8
    offset = rect_bytes + 4
    while offset < len(rest):
        if offset + 2 > len(rest):
            break
        tc = struct.unpack_from('<H', rest, offset)[0]
        offset += 2
        tag_type = tc >> 6
        length = tc & 0x3F
        if length == 0x3F:
            length = struct.unpack_from('<I', rest, offset)[0]
            offset += 4
        data = rest[offset:offset + length]
        offset += length
        if tag_type == 0:
            break
        yield tag_type, data

def main():
    rt_path = sys.argv[1]
    print(f"Analyzing: {rt_path}")
    print(f"File size: {os.path.getsize(rt_path):,} bytes")

    bitmaps = []
    all_tags = []
    for tag_type, data in parse_swf_tags(rt_path):
        all_tags.append((tag_type, len(data)))
        if tag_type in (TAG_LL, TAG_LL2) and len(data) >= 7:
            cid = struct.unpack_from('<H', data, 0)[0]
            body = data[2:]
            fmt = body[0]
            w = struct.unpack_from('<H', body, 1)[0]
            h = struct.unpack_from('<H', body, 3)[0]
            bitmaps.append((cid, tag_type, fmt, w, h, len(data)))

    print(f"\nTotal tags: {len(all_tags)}")
    print(f"Bitmap tags: {len(bitmaps)}")

    # Check for 0-dimension bitmaps
    zero_dim = [(cid, w, h) for cid, _, _, w, h, _ in bitmaps if w == 0 or h == 0]
    print(f"\nZero-dimension bitmaps: {len(zero_dim)}")
    for cid, w, h in zero_dim[:10]:
        print(f"  cid={cid}: {w}x{h}")

    # Check for oversized bitmaps (Flash limit ~8191)
    oversized = [(cid, w, h) for cid, _, _, w, h, _ in bitmaps if w > 4096 or h > 4096]
    print(f"Oversized bitmaps (>4096): {len(oversized)}")

    # Check for duplicate charIDs
    cid_counts = {}
    for cid, _, _, w, h, _ in bitmaps:
        cid_counts[cid] = cid_counts.get(cid, 0) + 1
    dupes = {k: v for k, v in cid_counts.items() if v > 1}
    print(f"\nDuplicate charIDs: {len(dupes)}")
    for cid, count in sorted(dupes.items())[:10]:
        print(f"  cid={cid}: appears {count}x")

    # Dimension distribution
    dims = {}
    for cid, _, _, w, h, _ in bitmaps:
        dims[(w, h)] = dims.get((w, h), 0) + 1
    print(f"\nUnique dimensions: {len(dims)}")
    # Sort by count desc
    for (w, h), count in sorted(dims.items(), key=lambda x: -x[1])[:15]:
        print(f"  {w}x{h}: {count} bitmaps")

    # Check pixel content duplicates
    print("\nChecking pixel content duplicates...")
    pixel_hashes = {}
    for cid, tag_type, fmt, w, h, _ in bitmaps:
        body = None
        for tt, data in parse_swf_tags(rt_path):
            if tt == tag_type and len(data) >= 7:
                c = struct.unpack_from('<H', data, 0)[0]
                if c == cid:
                    body = data[2:]
                    break
        if body:
            _, _, rgba = decode_lossless_to_rgba(tag_type, body)
            if rgba:
                h = hashlib.md5(rgba).hexdigest()
                if h not in pixel_hashes:
                    pixel_hashes[h] = []
                pixel_hashes[h].append(cid)

    total_unique = len(pixel_hashes)
    total_dupes = sum(1 for v in pixel_hashes.values() if len(v) > 1)
    print(f"  Unique pixel content: {total_unique}")
    print(f"  Pixel-duplicate groups: {total_dupes}")

    # CharID range
    cids = [cid for cid, _, _, _, _, _ in bitmaps]
    print(f"\nCharID range: {min(cids)} to {max(cids)}")
    print(f"CharID gaps: {max(cids) - min(cids) + 1 - len(set(cids))}")

if __name__ == '__main__':
    main()
