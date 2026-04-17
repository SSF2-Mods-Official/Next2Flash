"""Quick cross-check: compile ALL fox child sprites and compare RO2 counts with OG."""
import sys, os, struct, zlib
sys.path.insert(0, os.path.dirname(__file__))

from swf_to_n2d import parse_swf, validate_swf_sprites, N2DBuilder
from compile_n2d import to_publish, build_timeline_tags

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"

# Parse OG for reference RO2 counts
with open(OG, 'rb') as f:
    og_raw = f.read()
if og_raw[:3] == b'CWS':
    og_data = og_raw[:8] + zlib.decompress(og_raw[8:])
else:
    og_data = og_raw

# Scan OG sprites
def parse_og_sprites(data):
    pos = 8
    nbits = (data[pos] >> 3) & 0x1F
    rect_bits = 5 + nbits * 4
    rect_bytes = (rect_bits + 7) // 8
    pos += rect_bytes + 4
    sprites = {}
    while pos < len(data):
        if pos + 2 > len(data): break
        code_and_len = struct.unpack_from('<H', data, pos)[0]
        tt = code_and_len >> 6
        tl = code_and_len & 0x3F
        pos += 2
        if tl == 0x3F:
            tl = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        ts = pos
        pos += tl
        if tt == 0: break
        if tt == 39:
            sid = struct.unpack_from('<H', data, ts)[0]
            fc = struct.unpack_from('<H', data, ts + 2)[0]
            # Count RO2 inside this sprite
            ipos = ts + 4
            iend = ts + tl
            ro2 = 0
            while ipos < iend:
                ic = struct.unpack_from('<H', data, ipos)[0]
                itt = ic >> 6
                itl = ic & 0x3F
                ipos += 2
                if itl == 0x3F:
                    itl = struct.unpack_from('<I', data, ipos)[0]
                    ipos += 4
                ipos += itl
                if itt == 28: ro2 += 1
                if itt == 0: break
            sprites[sid] = ro2
    return sprites

og_sprites = parse_og_sprites(og_data)

# Import to N2D
header, tags = parse_swf(og_raw)
validate_swf_sprites(tags)
builder = N2DBuilder(header, name="fox")
builder.catalog_swf_tags(tags)
builder.frame_scripts = {}
builder.build_all()
builder.build_main_timeline(tags)
n2d = builder.to_n2d_json()

libs = n2d.get("libraries", [])
lib_to_char_idx = {}
for i, lib in enumerate(libs):
    if lib:
        lib_to_char_idx[lib["id"]] = i
id_to_lib = {lib["id"]: lib for lib in libs if lib}
char_id_map = {}
for i, lib in enumerate(libs):
    if lib:
        char_id_map[i] = lib.get("swfCharId", i + 1)

# Compile each container and compare RO2
match = 0
diff = 0
diffs = []
for lib in libs:
    if not lib or lib.get("type") != "container":
        continue
    swf_id = lib.get("swfCharId")
    if swf_id is None:
        continue
    og_ro2 = og_sprites.get(swf_id, None)
    if og_ro2 is None:
        continue
    
    tp = to_publish(lib, lib_to_char_idx, id_to_lib)
    total_frames = lib.get("totalFrame") or 1
    labels = lib.get("labels", [])
    try:
        timeline_bytes = build_timeline_tags(total_frames, tp, labels, [], char_id_map)
    except Exception:
        continue
    
    # Count RO2
    rt_ro2 = 0
    p = 0
    while p < len(timeline_bytes):
        tc = struct.unpack_from('<H', timeline_bytes, p)[0]
        tt = tc >> 6
        tl = tc & 0x3F
        p += 2
        if tl == 0x3F:
            tl = struct.unpack_from('<I', timeline_bytes, p)[0]
            p += 4
        p += tl
        if tt == 28: rt_ro2 += 1
    
    if rt_ro2 == og_ro2:
        match += 1
    else:
        diff += 1
        diffs.append((lib.get('name', '?'), swf_id, og_ro2, rt_ro2))

print(f"RO2 comparison across all {match + diff} containers:")
print(f"  Matching: {match}")
print(f"  Different: {diff}")
if diffs:
    for name, sid, og, rt in diffs[:20]:
        print(f"    {name:<40} OG_RO2={og:>3} RT_RO2={rt:>3} (diff={rt-og:+d})")
