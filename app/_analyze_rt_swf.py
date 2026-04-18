"""Compile blackmage and analyze the RT SWF for issues."""
import sys, struct, zlib, io
from collections import Counter, defaultdict

rt_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'
og_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'

# Now parse the RT SWF
with open(rt_path, 'rb') as f:
    raw = f.read()

sig = raw[:3]
ver = raw[3]
file_len = struct.unpack_from('<I', raw, 4)[0]
print(f"SWF: sig={sig} ver={ver} len={file_len}")

# Parse past header
pos = 8
nbits = (raw[pos] >> 3) & 0x1F
total_bits = 5 + nbits * 4
rect_bytes = (total_bits + 7) // 8
pos += rect_bytes
pos += 4  # frame_rate(2) + frame_count(2)

# Parse all tags
defined_ids = set()  # char IDs from definition tags
placed_ids = set()   # char IDs from PlaceObject tags
duplicate_ids = []
forward_refs = []
bitmap_tags = []
all_tags = []

definition_tag_types = {2, 22, 32, 46, 20, 36, 35, 6, 21, 11, 14, 37, 39, 75, 73, 91, 87, 88, 76, 82, 45, 90}

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
    
    all_tags.append((tag_type, tag_length))
    
    # Check bitmap tags
    if tag_type in (20, 36) and tag_length >= 7:
        char_id = struct.unpack_from('<H', raw, tag_start)[0]
        fmt = raw[tag_start + 2]
        w = struct.unpack_from('<H', raw, tag_start + 3)[0]
        h = struct.unpack_from('<H', raw, tag_start + 5)[0]
        
        # Get compressed data
        header_size = 7
        if fmt == 3:
            header_size += 1  # color table size byte
        compressed = raw[tag_start + header_size:tag_start + tag_length]
        
        try:
            decompressed = zlib.decompress(compressed)
            if fmt == 5:
                expected = w * h * 4
            elif fmt == 3:
                ct_size = raw[tag_start + 7] + 1 if fmt == 3 else 0
                ct_bytes = ct_size * (4 if tag_type == 36 else 3)
                row_stride = (w + 3) & ~3  # padded to 4 bytes
                expected = ct_bytes + row_stride * h
            else:
                expected = -1
            
            status = 'OK' if len(decompressed) == expected else f'SIZE_MISMATCH(got={len(decompressed)} exp={expected})'
        except Exception as e:
            status = f'ZLIB_ERROR({e})'
            decompressed = b''
        
        bitmap_tags.append({
            'char_id': char_id, 'tag_type': tag_type, 'fmt': fmt,
            'w': w, 'h': h, 'status': status, 'data_len': len(decompressed)
        })
        
        if char_id in defined_ids:
            duplicate_ids.append(('bitmap_redef', char_id, tag_type))
        defined_ids.add(char_id)
    
    elif tag_type == 35 and tag_length >= 6:  # DefineBitsJPEG3
        char_id = struct.unpack_from('<H', raw, tag_start)[0]
        bitmap_tags.append({
            'char_id': char_id, 'tag_type': tag_type, 'fmt': 'jpeg',
            'w': 0, 'h': 0, 'status': 'JPEG3', 'data_len': tag_length
        })
        if char_id in defined_ids:
            duplicate_ids.append(('jpeg3_redef', char_id, tag_type))
        defined_ids.add(char_id)
    
    # Check definition tags (shapes, sprites, etc.)
    elif tag_type in (2, 22, 32, 46):  # DefineShape*
        char_id = struct.unpack_from('<H', raw, tag_start)[0]
        if char_id in defined_ids:
            duplicate_ids.append(('shape_redef', char_id, tag_type))
        defined_ids.add(char_id)
    
    elif tag_type == 39:  # DefineSprite
        sprite_id = struct.unpack_from('<H', raw, tag_start)[0]
        if sprite_id in defined_ids:
            duplicate_ids.append(('sprite_redef', sprite_id, tag_type))
        defined_ids.add(sprite_id)
    
    # Check PlaceObject tags for forward references
    elif tag_type == 70:  # PlaceObject3
        flags = struct.unpack_from('<H', raw, tag_start)[0]
        # depth = struct.unpack_from('<H', raw, tag_start + 2)[0]
        has_char = (flags >> 1) & 1
        has_matrix = (flags >> 2) & 1
        has_image = (flags >> 12) & 1
        
        if has_char:
            ref_id = struct.unpack_from('<H', raw, tag_start + 4)[0]
            if ref_id not in defined_ids:
                forward_refs.append(('PO3', ref_id, has_image))
            placed_ids.add(ref_id)
    
    if tag_type == 0:
        break
    pos = tag_start + tag_length

print(f"\n--- RT SWF Summary ---")
print(f"Total tags: {len(all_tags)}")
print(f"Bitmap definition tags: {len(bitmap_tags)}")
print(f"Defined char IDs: {len(defined_ids)}")
print(f"Placed char IDs: {len(placed_ids)}")
print(f"Duplicate char IDs: {len(duplicate_ids)}")
if duplicate_ids:
    for dtype, cid, tt in duplicate_ids[:20]:
        print(f"  DUP: {dtype} id={cid} tag_type={tt}")

print(f"Forward references: {len(forward_refs)}")
if forward_refs:
    for ptype, ref_id, has_img in forward_refs[:20]:
        print(f"  FORWARD: {ptype} id={ref_id} hasImage={has_img}")

# Check bitmap status
status_counter = Counter(b['status'] for b in bitmap_tags)
print(f"\nBitmap tag status:")
for status, count in status_counter.items():
    print(f"  {status}: {count}")

fmt_counter = Counter(b['fmt'] for b in bitmap_tags)
print(f"\nBitmap formats: {dict(fmt_counter)}")

# Check for any 0-dimension bitmaps
bad_dims = [b for b in bitmap_tags if b['fmt'] != 'jpeg' and (b['w'] == 0 or b['h'] == 0)]
if bad_dims:
    print(f"\nWARNING: {len(bad_dims)} bitmaps with 0 dimensions!")
    for b in bad_dims[:10]:
        print(f"  id={b['char_id']} {b['w']}x{b['h']} fmt={b['fmt']}")
else:
    print(f"\nNo 0-dimension bitmaps")
