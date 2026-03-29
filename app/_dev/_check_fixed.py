"""Check font tags in fixed output."""
import struct
from collections import Counter

def parse_tags(path):
    raw = open(path, 'rb').read()
    nbits = (raw[8] >> 3) & 0x1f
    total_bits = 5 + nbits * 4
    rect_end = 8 + (total_bits + 7) // 8
    tag_start = rect_end + 4
    tags = []
    i = tag_start
    while i < len(raw):
        if i + 2 > len(raw): break
        h = struct.unpack_from('<H', raw, i)[0]
        tt = h >> 6; ln = h & 0x3f; hdr = 2
        if ln == 0x3f:
            ln = struct.unpack_from('<I', raw, i+2)[0]; hdr = 6
        tags.append((tt, raw[i+hdr:i+hdr+ln]))
        i += hdr + ln
        if tt == 0: break
    return tags

TAG_NAMES = {73: 'FontAlignZones', 74: 'CSMTextSettings', 75: 'DefineFont3', 88: 'DefineFontName'}

print('=== FIXED OUTPUT ===')
for tt, body in parse_tags('_roundtrip_fixed.swf'):
    if tt in (73, 74, 75, 88) and len(body) >= 2:
        cid = struct.unpack_from('<H', body, 0)[0]
        print(f'  {TAG_NAMES.get(tt, f"tag{tt}")} charId={cid} len={len(body)}')

print()
print('=== ORIGINAL ===')
for tt, body in parse_tags(r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\gameandwatch.ssf'):
    if tt in (73, 74, 75, 88) and len(body) >= 2:
        cid = struct.unpack_from('<H', body, 0)[0]
        print(f'  {TAG_NAMES.get(tt, f"tag{tt}")} charId={cid} len={len(body)}')

print()
fixed_counts = Counter(tt for tt, _ in parse_tags('_roundtrip_fixed.swf'))
orig_counts = Counter(tt for tt, _ in parse_tags(r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\gameandwatch.ssf'))
all_types = set(fixed_counts.keys()) | set(orig_counts.keys())
print('Tag count differences (orig vs fixed):')
has_diffs = False
for tt in sorted(all_types):
    fc = fixed_counts.get(tt, 0)
    oc = orig_counts.get(tt, 0)
    if fc != oc:
        print(f'  tag{tt}: orig={oc} fixed={fc}')
        has_diffs = True
if not has_diffs:
    print('  None! All tag counts match.')
print(f'Orig total: {sum(orig_counts.values())}, Fixed total: {sum(fixed_counts.values())}')
print(f'Orig size: 1065151, Fixed size: {open("_roundtrip_fixed.swf","rb").seek(0,2) or open("_roundtrip_fixed.swf","rb").seek(0,2)}')
import os
print(f'Fixed file size: {os.path.getsize("_roundtrip_fixed.swf")}')
