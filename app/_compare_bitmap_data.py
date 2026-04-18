"""Compare specific bitmap tags between OG and RT SWF byte-by-byte."""
import struct, zlib

og_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'
rt_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'

def parse_swf_tags(path):
    """Return dict of charID -> (tag_type, format, w, h, decompressed_pixels) for bitmap tags."""
    with open(path, 'rb') as f:
        raw = f.read()
    
    pos = 8
    nbits = (raw[pos] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    pos += rect_bytes + 4
    
    bitmaps = {}
    while pos < len(raw):
        if pos + 2 > len(raw):
            break
        tag_code_and_length = struct.unpack_from('<H', raw, pos)[0]
        tag_type = tag_code_and_length >> 6
        tag_length = tag_code_and_length & 0x3F
        pos += 2
        if tag_length == 0x3F:
            tag_length = struct.unpack_from('<I', raw, pos)[0]
            pos += 4
        tag_start = pos
        
        if tag_type in (20, 36) and tag_length >= 7:
            char_id = struct.unpack_from('<H', raw, tag_start)[0]
            fmt = raw[tag_start + 2]
            w = struct.unpack_from('<H', raw, tag_start + 3)[0]
            h = struct.unpack_from('<H', raw, tag_start + 5)[0]
            
            if fmt == 5:
                compressed = raw[tag_start + 7:tag_start + tag_length]
                pixels = zlib.decompress(compressed)
            elif fmt == 3:
                ct_size = raw[tag_start + 7] + 1
                compressed = raw[tag_start + 8:tag_start + tag_length]
                pixels = zlib.decompress(compressed)
            else:
                pixels = b''
            
            bitmaps[char_id] = (tag_type, fmt, w, h, pixels)
        
        if tag_type == 0:
            break
        pos = tag_start + tag_length
    
    return bitmaps

print("Parsing OG SWF...")
og_bitmaps = parse_swf_tags(og_path)
print(f"  {len(og_bitmaps)} bitmaps")

print("Parsing RT SWF...")
rt_bitmaps = parse_swf_tags(rt_path)
print(f"  {len(rt_bitmaps)} bitmaps")

# Need to find matching bitmaps between OG and RT
# They have different char IDs, so we need to match by content/dimensions
# Let's map by (w, h, pixel_count) — but multiple bitmaps can share dims

# Actually, let's check if ANY RT format-5 bitmap has pixel data that 
# violates premultiplication (R>A, G>A, or B>A for any pixel)
print("\n--- Checking RT bitmaps for premultiplication violations ---")
violations = 0
violation_bitmaps = []
for char_id in sorted(rt_bitmaps.keys()):
    tag_type, fmt, w, h, pixels = rt_bitmaps[char_id]
    if fmt != 5:
        continue
    # Format 5: ARGB, 4 bytes per pixel
    for i in range(0, len(pixels), 4):
        a = pixels[i]
        r = pixels[i+1]
        g = pixels[i+2]
        b = pixels[i+3]
        if r > a or g > a or b > a:
            violations += 1
            if len(violation_bitmaps) < 20 and char_id not in [v[0] for v in violation_bitmaps]:
                violation_bitmaps.append((char_id, w, h, i//4, a, r, g, b))
            break  # One violation per bitmap is enough to report

print(f"Bitmaps with premultiplication violations: {violations}")
for v in violation_bitmaps:
    cid, w, h, px_idx, a, r, g, b = v
    print(f"  charID={cid} {w}x{h}: pixel[{px_idx}] A={a} R={r} G={g} B={b}")

# Also check OG format-5 bitmaps for comparison
print("\n--- Checking OG bitmaps for premultiplication violations ---")
og_violations = 0
for char_id in sorted(og_bitmaps.keys()):
    tag_type, fmt, w, h, pixels = og_bitmaps[char_id]
    if fmt != 5:
        continue
    for i in range(0, len(pixels), 4):
        a = pixels[i]
        r = pixels[i+1]
        g = pixels[i+2]
        b = pixels[i+3]
        if r > a or g > a or b > a:
            og_violations += 1
            break

print(f"OG bitmaps with premultiplication violations: {og_violations}")

# Check OG format-3 bitmaps — how do they look?
print("\n--- OG format-3 bitmaps ---")
fmt3_count = 0
for char_id in sorted(og_bitmaps.keys()):
    tag_type, fmt, w, h, pixels = og_bitmaps[char_id]
    if fmt == 3:
        fmt3_count += 1
        if fmt3_count <= 3:
            # Parse color table
            # For tag 36 format 3: RGBA palette entries
            ct_entry_size = 4 if tag_type == 36 else 3
            ct_bytes = 0  # Already in decompressed data
            print(f"  charID={char_id} {w}x{h} tag={tag_type} pixels_len={len(pixels)}")

print(f"Total format-3: {fmt3_count}")
