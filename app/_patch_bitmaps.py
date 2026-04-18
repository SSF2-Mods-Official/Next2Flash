"""
Fix bitmap tags in RT SWF by replacing re-encoded bitmap bodies with
original OG bodies (matched by charID). This is a diagnostic/fix tool.

If the resulting SWF doesn't crash, we know the re-encoding was the problem.
"""
import struct, zlib, sys, os

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"
OUTPUT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"

def read_swf(path):
    with open(path, 'rb') as f:
        data = f.read()
    sig = data[:3]
    ver = data[3]
    file_len = struct.unpack_from('<I', data, 4)[0]
    if sig == b'CWS':
        body = zlib.decompress(data[8:])
    elif sig == b'ZWS':
        import lzma
        body = lzma.decompress(data[12:])
    else:
        body = data[8:]
    return sig, ver, file_len, body

def parse_rect(body, offset=0):
    first = body[offset]
    nbits = first >> 3
    total_bits = 5 + nbits * 4
    total_bytes = (total_bits + 7) // 8
    return total_bytes

def extract_bitmap_bodies(body):
    """Extract all LL2 (tag 36) and JPEG3 (tag 35) tag bodies by charID."""
    rect_bytes = parse_rect(body)
    pos = rect_bytes + 4  # skip RECT + fps(2) + frame_count(2)
    
    bitmaps = {}  # charID → (tag_type, full_body_bytes)
    
    while pos < len(body):
        if pos + 2 > len(body):
            break
        tag_code_and_len = struct.unpack_from('<H', body, pos)[0]
        tag_type = tag_code_and_len >> 6
        tag_len = tag_code_and_len & 0x3F
        header_size = 2
        if tag_len == 0x3F:
            if pos + 6 > len(body):
                break
            tag_len = struct.unpack_from('<I', body, pos + 2)[0]
            header_size = 6
        
        tag_body_start = pos + header_size
        tag_body = body[tag_body_start:tag_body_start + tag_len]
        
        if tag_type in (35, 36) and len(tag_body) >= 2:
            cid = struct.unpack_from('<H', tag_body, 0)[0]
            # Store the body AFTER charID
            bitmaps[cid] = (tag_type, tag_body[2:])
        
        pos = tag_body_start + tag_len
        if tag_type == 0:
            break
    
    return bitmaps

def patch_rt_bitmaps(rt_body, og_bitmaps):
    """Replace RT bitmap tag bodies with OG bodies (matched by charID).
    Returns the patched body bytes."""
    rect_bytes = parse_rect(rt_body)
    pos = rect_bytes + 4
    
    result = bytearray(rt_body[:pos])  # header (RECT + fps + frame_count)
    
    replaced = 0
    kept = 0
    mismatched_type = 0
    
    while pos < len(rt_body):
        if pos + 2 > len(rt_body):
            result.extend(rt_body[pos:])
            break
        tag_code_and_len = struct.unpack_from('<H', rt_body, pos)[0]
        tag_type = tag_code_and_len >> 6
        tag_len = tag_code_and_len & 0x3F
        header_size = 2
        is_long = (tag_len == 0x3F)
        if is_long:
            if pos + 6 > len(rt_body):
                result.extend(rt_body[pos:])
                break
            tag_len = struct.unpack_from('<I', rt_body, pos + 2)[0]
            header_size = 6
        
        tag_body_start = pos + header_size
        tag_body = rt_body[tag_body_start:tag_body_start + tag_len]
        
        if tag_type in (35, 36) and len(tag_body) >= 2:
            cid = struct.unpack_from('<H', tag_body, 0)[0]
            
            if cid in og_bitmaps:
                og_type, og_body_after_cid = og_bitmaps[cid]
                
                if og_type == tag_type:
                    # Same tag type — replace body with OG body
                    new_body = struct.pack('<H', cid) + og_body_after_cid
                    new_len = len(new_body)
                    
                    # Always use long tag header for safety
                    new_header = struct.pack('<H', (tag_type << 6) | 0x3F)
                    new_header += struct.pack('<I', new_len)
                    result.extend(new_header)
                    result.extend(new_body)
                    replaced += 1
                    pos = tag_body_start + tag_len
                    if tag_type == 0:
                        break
                    continue
                else:
                    # Tag type mismatch (e.g., OG is LL2 but RT is JPEG3 or vice versa)
                    # In this case, use the OG tag type and body
                    new_body = struct.pack('<H', cid) + og_body_after_cid
                    new_len = len(new_body)
                    new_header = struct.pack('<H', (og_type << 6) | 0x3F)
                    new_header += struct.pack('<I', new_len)
                    result.extend(new_header)
                    result.extend(new_body)
                    mismatched_type += 1
                    replaced += 1
                    pos = tag_body_start + tag_len
                    if tag_type == 0:
                        break
                    continue
            else:
                kept += 1
        
        # Copy original tag as-is
        result.extend(rt_body[pos:tag_body_start + tag_len])
        pos = tag_body_start + tag_len
        if tag_type == 0:
            break
    
    print(f"  Replaced: {replaced} bitmap tags with OG bodies")
    print(f"  Kept (no OG match): {kept}")
    print(f"  Type mismatches (used OG type): {mismatched_type}")
    
    return bytes(result)

def main():
    print(f"Reading OG: {OG}")
    og_sig, og_ver, og_fl, og_body = read_swf(OG)
    print(f"  {og_sig.decode()} v{og_ver}, {og_fl} bytes")
    
    og_bitmaps = extract_bitmap_bodies(og_body)
    print(f"  Extracted {len(og_bitmaps)} bitmap bodies")
    
    # Show LL2 vs JPEG3 counts
    ll2_count = sum(1 for t, _ in og_bitmaps.values() if t == 36)
    jpeg3_count = sum(1 for t, _ in og_bitmaps.values() if t == 35)
    print(f"  LL2: {ll2_count}, JPEG3: {jpeg3_count}")
    
    print(f"\nReading RT: {RT}")
    rt_sig, rt_ver, rt_fl, rt_body = read_swf(RT)
    print(f"  {rt_sig.decode()} v{rt_ver}, {rt_fl} bytes")
    
    print(f"\nPatching RT bitmaps with OG bodies...")
    patched_body = patch_rt_bitmaps(rt_body, og_bitmaps)
    
    # Rebuild SWF file
    file_length = 8 + len(patched_body)
    header = rt_sig + struct.pack('<BI', rt_ver, file_length)
    patched_swf = header + patched_body
    
    # Write output
    print(f"\nWriting patched SWF: {OUTPUT}")
    print(f"  Size: {len(patched_swf)} bytes (was {rt_fl})")
    with open(OUTPUT, 'wb') as f:
        f.write(patched_swf)
    
    print("\nDone! Test the patched SWF to see if Error #2015 is fixed.")
    print("If it works, the issue is in bitmap re-encoding.")
    print("If it still crashes, the issue is elsewhere (sprite structure, etc.)")

if __name__ == '__main__':
    main()
