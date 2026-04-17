"""Diagnostic: test decode_lossless_to_rgba on format 3 bitmaps directly."""
import sys, os, struct, zlib, json, base64
sys.path.insert(0, os.path.dirname(__file__))

from swf_to_n2d import decode_lossless_to_rgba

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"

# Parse SWF tags
with open(OG, 'rb') as f:
    raw = f.read()
sig = raw[:3]
if sig == b'CWS':
    data = raw[:8] + zlib.decompress(raw[8:])
elif sig == b'FWS':
    data = raw
else:
    print("Unknown SWF sig"); sys.exit(1)

pos = 8
fmt3_bitmaps = []
while pos < len(data):
    tag_code_and_len = struct.unpack_from('<H', data, pos)[0]
    tag_type = tag_code_and_len >> 6
    length = tag_code_and_len & 0x3F
    pos += 2
    if length == 0x3F:
        length = struct.unpack_from('<I', data, pos)[0]
        pos += 4
    body = data[pos:pos+length]
    pos += length
    
    if tag_type in (20, 36) and len(body) >= 7:
        char_id = struct.unpack_from('<H', body, 0)[0]
        body_after_cid = body[2:]
        fmt = body_after_cid[0]
        w = struct.unpack_from('<H', body_after_cid, 1)[0]
        h = struct.unpack_from('<H', body_after_cid, 3)[0]
        if fmt == 3:
            fmt3_bitmaps.append((char_id, tag_type, body_after_cid, w, h))
    if tag_type == 0:
        break

print(f"Found {len(fmt3_bitmaps)} format 3 bitmaps in OG SWF")

# Test decode on first few
errors = 0
for cid, tt, body_ac, w, h in fmt3_bitmaps[:10]:
    expected_len = w * h * 4
    dw, dh, rgba = decode_lossless_to_rgba(tt, body_ac)
    actual_len = len(rgba)
    status = "OK" if actual_len == expected_len else "MISMATCH"
    if status == "MISMATCH":
        errors += 1
    print(f"  charId={cid}, tag={tt}, {w}x{h}, expected={expected_len}, got={actual_len} [{status}]")

# Also check the N2D file to see if buffer matches decode output
N2D = r"C:\Users\glwex\Documents\GitHub\Next2Flash\fox.n2d"
if os.path.exists(N2D):
    with open(N2D, 'r') as f:
        n2d = json.load(f)
    
    # Build swfCharId -> n2d entry mapping
    lib = n2d.get('library', {})
    cid_to_n2d = {}
    for lid, entry in lib.items():
        scid = entry.get('swfCharId')
        if scid is not None:
            cid_to_n2d[scid] = (lid, entry)
    
    print(f"\nComparing decode output vs N2D buffer for first 10 format 3 bitmaps:")
    for cid, tt, body_ac, w, h in fmt3_bitmaps[:10]:
        dw, dh, rgba = decode_lossless_to_rgba(tt, body_ac)
        
        if cid in cid_to_n2d:
            lid, entry = cid_to_n2d[cid]
            buf = entry.get('buffer', '')
            if buf.startswith('b64:'):
                n2d_bytes = base64.b64decode(buf[4:])
                match = "MATCH" if n2d_bytes == rgba else f"DIFFER (n2d={len(n2d_bytes)}, decode={len(rgba)})"
                print(f"  charId={cid} -> lid={lid}: {match}")
                if n2d_bytes != rgba and len(n2d_bytes) > 0 and len(rgba) > 0:
                    # Show first differing byte
                    for i in range(min(len(n2d_bytes), len(rgba))):
                        if n2d_bytes[i] != rgba[i]:
                            print(f"    First diff at byte {i}: n2d={n2d_bytes[i]}, decode={rgba[i]}")
                            break
            else:
                print(f"  charId={cid} -> lid={lid}: NO BUFFER")
        else:
            print(f"  charId={cid}: NOT FOUND in N2D")

# Summary: check ALL format 3 bitmaps
print(f"\nChecking ALL {len(fmt3_bitmaps)} format 3 bitmaps:")
size_ok = 0
size_bad = 0
for cid, tt, body_ac, w, h in fmt3_bitmaps:
    dw, dh, rgba = decode_lossless_to_rgba(tt, body_ac)
    expected = w * h * 4
    if len(rgba) == expected:
        size_ok += 1
    else:
        size_bad += 1
        if size_bad <= 3:
            print(f"  BAD: charId={cid}, {w}x{h}, expected={expected}, got={len(rgba)}")
print(f"  Size OK: {size_ok}, Size BAD: {size_bad}")
