"""Check rawTagType distribution and compare with OG SWF bitmap tags."""
import msgpack, zipfile, struct, io
from collections import Counter

# Load N2D data
with zipfile.ZipFile(r'converted\blackmage\project.n2d') as zf:
    for name in zf.namelist():
        if name.endswith('.msgpack'):
            data = msgpack.unpackb(zf.read(name), raw=False)
            break

libs = data.get('libraries', [])
bitmaps = [l for l in libs if l.get('type') == 'bitmap']

tag_type_counter = Counter()
for b in bitmaps:
    tt = b.get('rawTagType', 'MISSING')
    tag_type_counter[tt] += 1

print("N2D rawTagType distribution:")
for tt, count in sorted(tag_type_counter.items()):
    tag_name = {20: 'DefineBitsLossless', 36: 'DefineBitsLossless2', 
                35: 'DefineBitsJPEG3', 6: 'DefineBits', 21: 'DefineBitsJPEG2'}.get(tt, str(tt))
    print(f"  Tag type {tt} ({tag_name}): {count}")

# Also check imageType field
img_type_counter = Counter()
for b in bitmaps:
    it = b.get('imageType', 'MISSING')
    img_type_counter[it] += 1
print(f"\nimageType distribution: {dict(img_type_counter)}")

# Now parse the OG SWF to check actual tag types and bitmap formats
og_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'
try:
    with open(og_path, 'rb') as f:
        sig = f.read(3)
        ver = struct.unpack('<B', f.read(1))[0]
        file_len = struct.unpack('<I', f.read(1 + 3)[:4])[0]
        # Skip RECT
        f.seek(0)
        raw = f.read()

    # Parse past header: sig(3) + ver(1) + len(4) + RECT + frame_rate(2) + frame_count(2)
    pos = 8
    # Read RECT: first byte has Nbits in top 5 bits
    nbits = (raw[pos] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    pos += rect_bytes
    pos += 2 + 2  # frame_rate + frame_count

    og_tag_types = Counter()
    og_bitmap_formats = Counter()
    og_bitmap_dims = {}
    bitmap_tags = {20, 36, 35, 6, 21, 8, 45}
    
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
        
        if tag_type in bitmap_tags:
            og_tag_types[tag_type] += 1
            if tag_type in (20, 36) and tag_length >= 7:
                char_id = struct.unpack_from('<H', raw, tag_start)[0]
                fmt = raw[tag_start + 2]
                w = struct.unpack_from('<H', raw, tag_start + 3)[0]
                h = struct.unpack_from('<H', raw, tag_start + 5)[0]
                og_bitmap_formats[(tag_type, fmt)] += 1
                og_bitmap_dims[char_id] = (tag_type, fmt, w, h)
            elif tag_type == 35 and tag_length >= 6:
                char_id = struct.unpack_from('<H', raw, tag_start)[0]
                og_bitmap_formats[(35, 'jpeg')] += 1
        
        if tag_type == 0:
            break
        pos = tag_start + tag_length

    print("\n--- OG SWF bitmap tag types ---")
    for tt, count in sorted(og_tag_types.items()):
        tag_name = {20: 'DefineBitsLossless', 36: 'DefineBitsLossless2', 
                    35: 'DefineBitsJPEG3', 6: 'DefineBits', 21: 'DefineBitsJPEG2',
                    8: 'JPEGTables', 45: 'DefineBitsLossless2'}.get(tt, str(tt))
        print(f"  Tag {tt} ({tag_name}): {count}")
    
    print("\n--- OG bitmap format breakdown ---")
    for (tt, fmt), count in sorted(og_bitmap_formats.items()):
        tag_name = {20: 'Lossless', 36: 'Lossless2', 35: 'JPEG3'}.get(tt, str(tt))
        print(f"  Tag {tt} ({tag_name}) format {fmt}: {count}")

except Exception as e:
    print(f"Error reading OG: {e}")
