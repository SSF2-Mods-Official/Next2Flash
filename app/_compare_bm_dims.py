"""
Compare ALL bitmap dimensions between OG and RT.
If any RT bitmaps are larger, the VRAM pool might overflow, causing bm_dairHand to fail.
"""
import struct, zlib
from collections import Counter

def read_swf_tags(path):
    with open(path, 'rb') as f:
        data = f.read()
    sig = data[:3]
    if sig == b'CWS':
        body = zlib.decompress(data[8:])
        data = data[:8] + body
    off = 8
    nbits = (data[off] >> 3) & 0x1f
    total_bits = 5 + nbits * 4
    off += (total_bits + 7) // 8
    off += 4
    tags = []
    while off < len(data):
        if off + 2 > len(data): break
        tw = struct.unpack_from('<H', data, off)[0]
        tag_type = tw >> 6
        tag_len = tw & 0x3f
        off += 2
        if tag_len == 63:
            tag_len = struct.unpack_from('<i', data, off)[0]
            off += 4
        tags.append((tag_type, off, tag_len))
        off += tag_len
    return tags, data

og_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'
rt_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'
og_tags, og_data = read_swf_tags(og_path)
rt_tags, rt_data = read_swf_tags(rt_path)

def get_all_bitmaps(tags, data):
    bitmaps = {}
    for (t, o, l) in tags:
        if t == 36 and l >= 7:  # LL2
            body = data[o:o+l]
            cid, fmt, w, h = struct.unpack_from('<HBHH', body)
            bitmaps[cid] = ('LL2', w, h, w*h)
        elif t == 35 and l >= 6:  # JPEG3 (charID + 4-byte offset + JPEG data + alpha)
            cid = struct.unpack_from('<H', data, o)[0]
            # For JPEG3, we'd need to decode JPEG to get dimensions
            # Just use tag length as proxy
            bitmaps[cid] = ('JPEG3', 0, 0, l)
    return bitmaps

og_bm = get_all_bitmaps(og_tags, og_data)
rt_bm = get_all_bitmaps(rt_tags, rt_data)

# Total pixel area comparison for LL2 bitmaps
og_ll2_area = sum(w*h for (tp, w, h, area) in og_bm.values() if tp == 'LL2')
rt_ll2_area = sum(w*h for (tp, w, h, area) in rt_bm.values() if tp == 'LL2')
print(f'OG total LL2 pixel area: {og_ll2_area:,}')
print(f'RT total LL2 pixel area: {rt_ll2_area:,}')
print(f'Difference: {rt_ll2_area - og_ll2_area:+,}')

# Find LL2 bitmaps with different dimensions between OG and RT
print('\n=== LL2 bitmaps with different dimensions ===')
common_cids = set(og_bm) & set(rt_bm)
for cid in sorted(common_cids):
    og_tp, og_w, og_h, _ = og_bm[cid]
    rt_tp, rt_w, rt_h, _ = rt_bm[cid]
    if og_tp == 'LL2' and rt_tp == 'LL2' and (og_w != rt_w or og_h != rt_h):
        print(f'  charID={cid}: OG={og_w}x{og_h} RT={rt_w}x{rt_h}')

# Find LL2 bitmaps in RT that are not in OG (or vice versa)
only_og = set(og_bm) - set(rt_bm)
only_rt = set(rt_bm) - set(og_bm)
print(f'\nOnly in OG: {sorted(only_og)[:10]}')
print(f'Only in RT: {sorted(only_rt)[:10]}')

# Top 10 largest LL2 bitmaps in RT
print('\n=== Top 10 largest LL2 bitmaps by area in RT ===')
rt_ll2_sorted = sorted([(w*h, cid, w, h) for cid, (tp, w, h, area) in rt_bm.items() if tp == 'LL2'], reverse=True)
for area, cid, w, h in rt_ll2_sorted[:10]:
    og_info = og_bm.get(cid, ('?', 0, 0, 0))
    og_area = og_info[1] * og_info[2] if og_info[0] == 'LL2' else 0
    print(f'  charID={cid}: RT={w}x{h}={area} OG={og_info[1]}x{og_info[2]}={og_area}')

# What are the JPEG3 charIDs in RT? Do any have SymbolClass entries?
print('\n=== JPEG3 charIDs in RT ===')
rt_jpeg3_cids = sorted([cid for cid, (tp, w, h, a) in rt_bm.items() if tp == 'JPEG3'])
print(f'JPEG3 count: {len(rt_jpeg3_cids)}')
print(f'JPEG3 charIDs (first 20): {rt_jpeg3_cids[:20]}')

# Parse SymbolClass to find which JPEG3 charIDs have class linkages  
for (t, o, l) in og_tags:
    if t == 76:  # SymbolClass
        body = og_data[o:o+l]
        count = struct.unpack_from('<H', body)[0]
        off = 2
        jpeg3_with_class = []
        for _ in range(count):
            if off + 2 > len(body): break
            cid = struct.unpack_from('<H', body, off)[0]
            off += 2
            name_start = off
            while off < len(body) and body[off] != 0:
                off += 1
            name = body[name_start:off].decode('latin-1', errors='replace')
            off += 1
            if cid in rt_jpeg3_cids:
                jpeg3_with_class.append((cid, name))
        print(f'\nJPEG3 charIDs with SymbolClass entries: {jpeg3_with_class[:20]}')
        
        # Full SymbolClass list for reference
        off = 2
        all_entries = []
        for _ in range(count):
            if off + 2 > len(body): break
            cid = struct.unpack_from('<H', body, off)[0]
            off += 2
            name_start = off
            while off < len(body) and body[off] != 0:
                off += 1
            name = body[name_start:off].decode('latin-1', errors='replace')
            off += 1
            all_entries.append((cid, name))
        print(f'\nTotal SymbolClass entries: {len(all_entries)}')
        bm_entries = [(cid, name) for cid, name in all_entries if name.startswith('bm_') or 'bitmap' in name.lower()]
        print(f'Bitmap class entries (bm_*): {len(bm_entries)}')
        print(f'First 10: {bm_entries[:10]}')
        break
