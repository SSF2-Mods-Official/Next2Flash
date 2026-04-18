"""Compare SymbolClass entries between OG and RT SWF."""
import struct

og_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'
rt_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'

def parse_swf_symbol_class(path):
    with open(path, 'rb') as f:
        raw = f.read()
    
    pos = 8
    nbits = (raw[pos] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    pos += rect_bytes + 4
    
    while pos < len(raw):
        tag_code_and_length = struct.unpack_from('<H', raw, pos)[0]
        tag_type = tag_code_and_length >> 6
        tag_length = tag_code_and_length & 0x3F
        pos += 2
        if tag_length == 0x3F:
            tag_length = struct.unpack_from('<I', raw, pos)[0]
            pos += 4
        tag_start = pos
        
        if tag_type == 76:  # SymbolClass
            count = struct.unpack_from('<H', raw, tag_start)[0]
            p = 2
            entries = []
            for _ in range(count):
                cid = struct.unpack_from('<H', raw[tag_start:], p)[0]
                p += 2
                name_end = raw[tag_start:].index(0, p)
                name = raw[tag_start + p:tag_start + name_end].decode('utf-8', errors='replace')
                p = name_end - tag_start + 1
                entries.append((cid, name))
            return entries
        
        if tag_type == 0:
            break
        pos = tag_start + tag_length
    return []

og_symbols = parse_swf_symbol_class(og_path)
rt_symbols = parse_swf_symbol_class(rt_path)

print(f"OG: {len(og_symbols)} symbols")
print(f"RT: {len(rt_symbols)} symbols")

og_names = {name for _, name in og_symbols}
rt_names = {name for _, name in rt_symbols}

only_in_og = og_names - rt_names
only_in_rt = rt_names - og_names

if only_in_og:
    print(f"\nOnly in OG: {len(only_in_og)}")
    for n in sorted(only_in_og):
        print(f"  {n}")

if only_in_rt:
    print(f"\nOnly in RT: {len(only_in_rt)}")
    for n in sorted(only_in_rt):
        print(f"  {n}")

if not only_in_og and not only_in_rt:
    print("\nAll symbol names match!")
    
# Also check: are there bitmap char IDs in the SymbolClass?
# Parse bitmap char IDs from both SWFs
def parse_bitmap_char_ids(path):
    with open(path, 'rb') as f:
        raw = f.read()
    pos = 8
    nbits = (raw[pos] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    pos += rect_bytes + 4
    
    bitmap_ids = set()
    while pos < len(raw):
        tag_code_and_length = struct.unpack_from('<H', raw, pos)[0]
        tag_type = tag_code_and_length >> 6
        tag_length = tag_code_and_length & 0x3F
        pos += 2
        if tag_length == 0x3F:
            tag_length = struct.unpack_from('<I', raw, pos)[0]
            pos += 4
        tag_start = pos
        if tag_type in (20, 36, 35) and tag_length >= 2:
            cid = struct.unpack_from('<H', raw, tag_start)[0]
            bitmap_ids.add(cid)
        if tag_type == 0:
            break
        pos = tag_start + tag_length
    return bitmap_ids

og_bitmap_ids = parse_bitmap_char_ids(og_path)
rt_bitmap_ids = parse_bitmap_char_ids(rt_path)

# Check if any bitmap char IDs are in the SymbolClass
og_sym_bitmap = {name for cid, name in og_symbols if cid in og_bitmap_ids}
rt_sym_bitmap = {name for cid, name in rt_symbols if cid in rt_bitmap_ids}

print(f"\nOG symbols mapped to bitmaps: {len(og_sym_bitmap)}")
for n in sorted(og_sym_bitmap)[:10]:
    print(f"  {n}")
print(f"RT symbols mapped to bitmaps: {len(rt_sym_bitmap)}")
for n in sorted(rt_sym_bitmap)[:10]:
    print(f"  {n}")
