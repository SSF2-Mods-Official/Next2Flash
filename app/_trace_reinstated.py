"""Trace where the reinstated flag gets lost in the fox sprite pipeline."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))

from swf_to_n2d import parse_swf, validate_swf_sprites, N2DBuilder
import time

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"

print("=== Step 1: Import OG fox.ssf to N2D ===")
with open(OG, 'rb') as f:
    swf_data = f.read()
header, tags = parse_swf(swf_data)
validate_swf_sprites(tags)
builder = N2DBuilder(header, name="fox")
builder.catalog_swf_tags(tags)
builder.frame_scripts = {}
builder.build_all()
builder.build_main_timeline(tags)
n2d = builder.to_n2d_json()

# Find the fox sprite container (the one with the most characters at a single depth)
fox_lib = None
for lib in n2d.get("libraries", []):
    if lib.get("type") != "container":
        continue
    for layer in lib.get("layers", []):
        chars = layer.get("characters", [])
        if len(chars) > 50:  # fox has ~85 character spans at depth 7
            fox_lib = lib
            print(f"  Found fox candidate: lib id={lib['id']}, name={lib.get('name','?')}")
            print(f"    Layer '{layer.get('name')}' swfDepth={layer.get('swfDepth')} has {len(chars)} character spans")
            
            # Check reinstated flags
            reinstated_count = sum(1 for c in chars if c.get("reinstated"))
            not_reinstated = sum(1 for c in chars if not c.get("reinstated"))
            print(f"    reinstated=True: {reinstated_count}, reinstated=False/missing: {not_reinstated}")
            
            # Show first 5 character spans
            for i, ch in enumerate(chars[:5]):
                print(f"    char[{i}]: libId={ch.get('libraryId')}, frames={ch.get('startFrame')}-{ch.get('endFrame')}, reinstated={ch.get('reinstated', 'MISSING')}, name='{ch.get('name','')}'")
            if len(chars) > 5:
                print(f"    ... ({len(chars) - 5} more)")
            break

if not fox_lib:
    print("  ERROR: Could not find fox sprite container!")
    sys.exit(1)

print()
print("=== Step 2: Call to_publish on fox container ===")
from compile_n2d import to_publish, build_timeline_tags

# Build lib_to_char_idx map
libs = n2d.get("libraries", [])
lib_to_char_idx = {}
for i, lib in enumerate(libs):
    if lib:
        lib_to_char_idx[lib["id"]] = i

id_to_lib = {lib["id"]: lib for lib in libs if lib}

tp = to_publish(fox_lib, lib_to_char_idx, id_to_lib)

dictionary = tp["dictionary"]
controller = tp["controller"]

# Check reinstated in dictionary
reinstated_dict = sum(1 for d in dictionary if d.get("reinstated"))
not_reinstated_dict = sum(1 for d in dictionary if not d.get("reinstated"))
print(f"  Dictionary entries: {len(dictionary)}")
print(f"    reinstated=True: {reinstated_dict}, reinstated=False: {not_reinstated_dict}")

# Show first 5 dictionary entries
for i, d in enumerate(dictionary[:5]):
    print(f"    dict[{i}]: charId={d.get('characterId')}, name='{d.get('name','')}', reinstated={d.get('reinstated')}, frames={d.get('startFrame')}-{d.get('endFrame')}")

print()
print("=== Step 3: Actually compile and count RO2/PO2 tags ===")

# Build char_id_map
char_id_map = {}
for i, lib in enumerate(libs):
    if lib and lib.get("type") not in (None,):
        char_id_map[i] = lib.get("swfCharId", i + 1)

total_frames = fox_lib.get("totalFrame") or 98
labels = fox_lib.get("labels", [])
actions = fox_lib.get("actions", [])

# Actually call build_timeline_tags to get the output bytes
timeline_bytes = build_timeline_tags(
    total_frames, tp, labels, actions, char_id_map,
    bitmap_char_ids=None,
)

# Parse the output to count RO2 and PO2 tags
import struct

pos = 0
ro2_count = 0
po2_count = 0
po2_move_count = 0
po2_fresh_count = 0
show_frame_count = 0

while pos < len(timeline_bytes):
    tag_code_and_length = struct.unpack_from('<H', timeline_bytes, pos)[0]
    tag_type = tag_code_and_length >> 6
    tag_length = tag_code_and_length & 0x3F
    pos += 2
    if tag_length == 0x3F:
        tag_length = struct.unpack_from('<I', timeline_bytes, pos)[0]
        pos += 4
    
    tag_body = timeline_bytes[pos:pos + tag_length]
    pos += tag_length
    
    if tag_type == 28:  # RemoveObject2
        ro2_count += 1
    elif tag_type == 26:  # PlaceObject2
        po2_count += 1
        if len(tag_body) >= 1:
            flags = tag_body[0]
            is_move = bool(flags & 0x01)
            has_char = bool(flags & 0x02)
            has_matrix = bool(flags & 0x04)
            has_cxform = bool(flags & 0x10)
            has_name = bool(flags & 0x20)
            if is_move:
                po2_move_count += 1
            else:
                po2_fresh_count += 1
            if tag_length <= 20:  # first few depth-7 PO2s
                depth = struct.unpack_from('<H', tag_body, 1)[0]
                if depth == 7 and po2_count <= 5:
                    print(f"  PO2 #{po2_count}: depth={depth} flags=0x{flags:02x} move={is_move} char={has_char} mat={has_matrix} cx={has_cxform} name={has_name} ({tag_length}B)")
    elif tag_type == 1:  # ShowFrame
        show_frame_count += 1

print()
print(f"  RemoveObject2 tags: {ro2_count}")
print(f"  PlaceObject2 tags: {po2_count} (move={po2_move_count}, fresh={po2_fresh_count})")
print(f"  ShowFrame tags: {show_frame_count}")
print()
if ro2_count >= 80:
    print("  SUCCESS: RO2 tags match OG pattern (expected ~84)")
else:
    print(f"  FAILURE: Only {ro2_count} RO2 tags (expected ~84)")

print()
print("=== Step 4: Verify fix works WITHOUT reinstated flag (simulating web editor loss) ===")
import copy
fox_lib_stripped = copy.deepcopy(fox_lib)
for layer in fox_lib_stripped.get("layers", []):
    for ch in layer.get("characters", []):
        ch.pop("reinstated", None)

tp_stripped = to_publish(fox_lib_stripped, lib_to_char_idx, id_to_lib)
timeline_bytes2 = build_timeline_tags(
    total_frames, tp_stripped, labels, actions, char_id_map,
    bitmap_char_ids=None,
)

pos = 0
ro2_count2 = 0
while pos < len(timeline_bytes2):
    tag_code_and_length = struct.unpack_from('<H', timeline_bytes2, pos)[0]
    tag_type = tag_code_and_length >> 6
    tag_length = tag_code_and_length & 0x3F
    pos += 2
    if tag_length == 0x3F:
        tag_length = struct.unpack_from('<I', timeline_bytes2, pos)[0]
        pos += 4
    pos += tag_length
    if tag_type == 28:
        ro2_count2 += 1

if ro2_count2 >= 80:
    print(f"  SUCCESS: {ro2_count2} RO2 tags even WITHOUT reinstated flag!")
    print("  The fix works regardless of web editor flag loss.")
else:
    print(f"  FAILURE: Only {ro2_count2} RO2 tags without reinstated flag")
