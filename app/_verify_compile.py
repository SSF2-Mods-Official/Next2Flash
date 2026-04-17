"""Compile fox sprite from fresh N2D import and verify ratio + RO2 in output."""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__))

from swf_to_n2d import parse_swf, validate_swf_sprites, N2DBuilder
from compile_n2d import to_publish, build_timeline_tags

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"

# Import to N2D
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

# Find fox container
fox_lib = None
for lib in n2d.get("libraries", []):
    if lib.get("type") == "container" and lib.get("name") == "fox":
        fox_lib = lib
        break

if not fox_lib:
    for lib in n2d.get("libraries", []):
        if lib.get("type") != "container":
            continue
        for layer in lib.get("layers", []):
            if layer.get('swfDepth') == 7 and len(layer.get("characters", [])) > 80:
                fox_lib = lib
                break
        if fox_lib:
            break

libs = n2d.get("libraries", [])
lib_to_char_idx = {}
for i, lib in enumerate(libs):
    if lib:
        lib_to_char_idx[lib["id"]] = i
id_to_lib = {lib["id"]: lib for lib in libs if lib}

# Compile fox sprite timeline
tp = to_publish(fox_lib, lib_to_char_idx, id_to_lib)
total_frames = fox_lib.get("totalFrame") or 98
labels = fox_lib.get("labels", [])
actions = fox_lib.get("actions", [])

char_id_map = {}
for i, lib in enumerate(libs):
    if lib:
        char_id_map[i] = lib.get("swfCharId", i + 1)

timeline_bytes = build_timeline_tags(
    total_frames, tp, labels, actions, char_id_map,
    bitmap_char_ids=None,
)

# Parse compiled output - check fox MC PO2 at depth 7
print("=== Compiled fox sprite timeline analysis ===")
pos = 0
frame = 0
ro2_total = 0
po2_with_ratio = 0
po2_without_ratio = 0

while pos < len(timeline_bytes):
    tag_code_and_length = struct.unpack_from('<H', timeline_bytes, pos)[0]
    tag_type = tag_code_and_length >> 6
    tag_len = tag_code_and_length & 0x3F
    pos += 2
    if tag_len == 0x3F:
        tag_len = struct.unpack_from('<I', timeline_bytes, pos)[0]
        pos += 4
    tag_body = timeline_bytes[pos:pos + tag_len]
    pos += tag_len
    
    if tag_type == 1:  # ShowFrame
        frame += 1
    elif tag_type == 28:  # RO2
        depth = struct.unpack_from('<H', tag_body, 0)[0]
        if depth == 7:
            ro2_total += 1
    elif tag_type == 26:  # PO2
        flags = tag_body[0]
        depth = struct.unpack_from('<H', tag_body, 1)[0]
        if depth == 7:
            has_ratio = bool(flags & 0x10)
            has_name = bool(flags & 0x20)
            has_char = bool(flags & 0x02)
            has_cxform = bool(flags & 0x08)
            
            if has_ratio:
                po2_with_ratio += 1
            else:
                po2_without_ratio += 1
            
            if frame <= 5 or frame == 14:
                # Extract ratio value if present
                off = 3
                char_id = None
                if has_char:
                    char_id = struct.unpack_from('<H', tag_body, off)[0]
                    off += 2
                # Skip matrix (bit-encoded) - find ratio after it
                # Actually we need to parse the matrix to find the ratio position
                ratio_val = None
                if has_ratio:
                    # The ratio comes after charId + matrix + optional cxform
                    # We'll read the raw bytes to find it
                    # Matrix is bit-encoded, hard to skip. Let's just search for known values.
                    pass
                
                print(f"  Frame {frame:>2}: PO2 depth=7 flags=0x{flags:02x} char={char_id} "
                      f"ratio={'Y' if has_ratio else 'N'} name={'Y' if has_name else 'N'} "
                      f"cxform={'Y' if has_cxform else 'N'} ({tag_len}B)")

print(f"\n  Fox MC depth 7 summary:")
print(f"    RO2: {ro2_total}")
print(f"    PO2 with ratio: {po2_with_ratio}")
print(f"    PO2 without ratio: {po2_without_ratio}")

# Now check a child sprite - find the 'a' attack child
print("\n=== Checking 'a' attack child sprite ===")
# Find the child sprite placed at frame 14 (label 'a')
# We need to identify what charId is placed at depth 7 on frame 14
pos = 0
frame = 0
a_child_char_idx = None
while pos < len(timeline_bytes):
    tag_code_and_length = struct.unpack_from('<H', timeline_bytes, pos)[0]
    tag_type = tag_code_and_length >> 6
    tag_len = tag_code_and_length & 0x3F
    pos += 2
    if tag_len == 0x3F:
        tag_len = struct.unpack_from('<I', timeline_bytes, pos)[0]
        pos += 4
    tag_body = timeline_bytes[pos:pos + tag_len]
    pos += tag_len
    if tag_type == 1:
        frame += 1
    elif tag_type == 26 and frame == 14:
        flags = tag_body[0]
        depth = struct.unpack_from('<H', tag_body, 1)[0]
        if depth == 7 and (flags & 0x02):
            a_child_char_idx = struct.unpack_from('<H', tag_body, 3)[0]
            break

# Find the library for this character
if a_child_char_idx:
    # char_id_map maps char_array_idx → swf_char_id
    # We need the reverse: swf_char_id → lib
    swf_id_to_lib = {}
    for i, lib in enumerate(libs):
        if lib:
            swf_id = lib.get("swfCharId", i + 1)
            swf_id_to_lib[swf_id] = lib
    # Also check char_id_map
    for char_arr_idx, swf_id in char_id_map.items():
        if swf_id == a_child_char_idx:
            a_lib = libs[char_arr_idx]
            print(f"  'a' child: compiled charId={a_child_char_idx}, lib name='{a_lib.get('name','?')}', "
                  f"symbolName='{a_lib.get('symbolName','?')}'")
            
            # Compile this child sprite and check its RO2 count
            if a_lib.get("type") == "container":
                a_tp = to_publish(a_lib, lib_to_char_idx, id_to_lib)
                a_total = a_lib.get("totalFrame") or 41
                a_labels = a_lib.get("labels", [])
                a_timeline = build_timeline_tags(
                    a_total, a_tp, a_labels, [], char_id_map)
                
                # Count tags
                a_pos = 0
                a_ro2 = 0
                a_po2 = 0
                a_sf = 0
                while a_pos < len(a_timeline):
                    tc = struct.unpack_from('<H', a_timeline, a_pos)[0]
                    tt = tc >> 6
                    tl = tc & 0x3F
                    a_pos += 2
                    if tl == 0x3F:
                        tl = struct.unpack_from('<I', a_timeline, a_pos)[0]
                        a_pos += 4
                    a_pos += tl
                    if tt == 28: a_ro2 += 1
                    elif tt == 26: a_po2 += 1
                    elif tt == 1: a_sf += 1
                
                print(f"  'a' child compiled: RO2={a_ro2} PO2={a_po2} ShowFrame={a_sf}")
                print(f"  OG 'a' child had: RO2=17 PO2=159 ShowFrame=41")
                
                # Check reinstated in the 'a' child
                found_reinstated = 0
                total_chars = 0
                for layer in a_lib.get("layers", []):
                    for ch in layer.get("characters", []):
                        total_chars += 1
                        if ch.get("reinstated"):
                            found_reinstated += 1
                print(f"  'a' child chars: {total_chars} total, {found_reinstated} reinstated")
            break

# Now strip reinstated from fox and recompile to see how it affects child sprites
print("\n=== What if reinstated is preserved? (revert to reinstated-based logic) ===")
print("  Current fix: always RO2 for char swaps -> fox got correct 84 RO2")
print("  But child sprites get EXTRA RO2 (42 vs OG 17)")
print()
print("  If we revert to reinstated-based logic:")
print("    fox MC depth 7: 81 reinstated + 3 non-reinstated (depth-empty) RO2 = 84")  
print("    child sprites: only reinstated=True char swaps get RO2 -> matches OG")
print()
print("  Risk: if reinstated gets lost through web editor, fox MC loses RO2 again")
print("  Mitigation: server.py now preserves reinstated in _merge_editor_into_disk")
