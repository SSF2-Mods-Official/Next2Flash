"""Find the extra tag and validate bitmap/font data in roundtrip SWF."""
import struct, zlib

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

TAG_NAMES = {0:'End',1:'ShowFrame',2:'DefineShape',9:'SetBgColor',
    14:'DefineSound',20:'DefineBitsLossless',21:'DefineBitsJPEG2',
    22:'DefineShape2',24:'Protect',26:'PlaceObject2',28:'RemoveObject2',
    32:'DefineShape3',35:'DefineBitsJPEG3',36:'DefineBitsLossless2',
    39:'DefineSprite',43:'FrameLabel',45:'SoundStreamHead2',46:'MorphShape',
    48:'DefineFont2',69:'FileAttributes',70:'PlaceObject3',72:'DoABC',
    73:'FontAlignZones',74:'CSMTextSettings',75:'DefineFont3',
    76:'SymbolClass',82:'DoABC2',83:'DefineShape4',84:'MorphShape2',
    86:'SceneFrameLabel',87:'DefineBinaryData',88:'DefineFontName'}

print("=== ROUNDTRIP TAG TYPE COUNTS ===")
rt = parse_tags('_roundtrip_test.swf')
from collections import Counter
rt_counts = Counter(tt for tt, _ in rt)
for tt, count in sorted(rt_counts.items()):
    name = TAG_NAMES.get(tt, f'tag{tt}')
    print(f"  {name}(type={tt}): {count}")

print("\n=== ORIGINAL TAG TYPE COUNTS ===")
orig = parse_tags(r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\gameandwatch.ssf')
orig_counts = Counter(tt for tt, _ in orig)
for tt, count in sorted(orig_counts.items()):
    name = TAG_NAMES.get(tt, f'tag{tt}')
    print(f"  {name}(type={tt}): {count}")

print("\n=== COUNT DIFFERENCES ===")
all_types = set(rt_counts.keys()) | set(orig_counts.keys())
for tt in sorted(all_types):
    rc = rt_counts.get(tt, 0)
    oc = orig_counts.get(tt, 0)
    if rc != oc:
        name = TAG_NAMES.get(tt, f'tag{tt}')
        print(f"  {name}(type={tt}): orig={oc} rt={rc} delta={rc-oc}")

# Validate ALL DefineBitsLossless2 in roundtrip
print("\n=== BITMAP VALIDATION (roundtrip) ===")
bitmap_errors = 0
for tt, body in rt:
    if tt in (20, 36) and len(body) >= 7:  # DefineBitsLossless, DefineBitsLossless2
        cid = struct.unpack_from('<H', body, 0)[0]
        fmt = body[2]
        w = struct.unpack_from('<H', body, 3)[0]
        h = struct.unpack_from('<H', body, 5)[0]
        zdata = body[7:] if fmt != 3 else body[8:]  # fmt 3 has colorTableSize byte
        if fmt not in (3, 4, 5):
            print(f"  charId={cid}: INVALID format={fmt} width={w} height={h}")
            bitmap_errors += 1
        else:
            try:
                decompressed = zlib.decompress(zdata)
                expected = w * h * 4 if fmt == 5 else -1  # fmt 3/4 varies
                if fmt == 5 and len(decompressed) != expected:
                    print(f"  charId={cid}: decompressed={len(decompressed)} expected={expected} (fmt={fmt} {w}x{h})")
                    bitmap_errors += 1
            except Exception as e:
                print(f"  charId={cid}: ZLIB ERROR: {e} (fmt={fmt} {w}x{h})")
                bitmap_errors += 1
print(f"Bitmap validation errors: {bitmap_errors}")

# Font and text tags in roundtrip
print("\n=== FONT/TEXT TAGS (roundtrip) ===")
for tt, body in rt:
    if tt in (73, 74, 75, 88) and len(body) >= 2:
        cid = struct.unpack_from('<H', body, 0)[0]
        name = TAG_NAMES.get(tt, f'tag{tt}')
        print(f"  {name} charId={cid} len={len(body)}")

print("\n=== FONT/TEXT TAGS (original) ===")
for tt, body in orig:
    if tt in (73, 74, 75, 88) and len(body) >= 2:
        cid = struct.unpack_from('<H', body, 0)[0]
        name = TAG_NAMES.get(tt, f'tag{tt}')
        print(f"  {name} charId={cid} len={len(body)}")
