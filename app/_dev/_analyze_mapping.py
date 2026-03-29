"""
Analyze the actual charID mapping in compile_n2d.py:
1. Show how original swfCharIds map to new IDs
2. Check if ordering is preserved or randomized
3. Check what reference types exist that need remapping
"""
import json, zipfile, struct, zlib, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

N2D_PATH = 'converted/gameandwatch_cli.n2d'
SWF_PATH = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\gameandwatch.swf'

# Load N2D
with zipfile.ZipFile(N2D_PATH) as zf:
    data = json.loads(zf.read('project.json'))

# Build mapping: swfCharId -> lib info
libs_by_cid = {}
for lib in data['libraries']:
    cid = lib.get('swfCharId')
    if cid is not None:
        libs_by_cid[cid] = lib

# Now compile and check the _orig_to_new_id mapping
import compile_n2d
import importlib
importlib.reload(compile_n2d)

# Create a compiler properly
compiler = compile_n2d.N2DCompiler.__new__(compile_n2d.N2DCompiler)
compiler.n2d_path = N2D_PATH
compiler.shared_dir = '.'
compiler.output_path = 'converted/_test_mapping.swf'
compiler.sdk_path = None
compiler.data = data
compiler.stage = data.get("stage", {})
compiler.libs = data.get("libraries", [])
compiler.id_to_lib = {lib["id"]: lib for lib in compiler.libs}
compiler._next_id = 1
compiler._lib_to_swf_id = {}
compiler._lib_to_char_idx = {}
compiler._char_idx_to_swf_id = {}
compiler._definition_tags = bytearray()

# Run ID assignment
compiler._assign_ids()

print("=== CharID Mapping Analysis ===")
print(f"Total libraries with swfCharId: {len(libs_by_cid)}")
print(f"_orig_to_new_id entries: {len(compiler._orig_to_new_id)}")

# Check how many IDs changed
unchanged = 0
changed = 0
for orig_cid, new_id in sorted(compiler._orig_to_new_id.items()):
    if orig_cid == new_id:
        unchanged += 1
    else:
        changed += 1

print(f"IDs unchanged (orig==new): {unchanged}")
print(f"IDs changed (orig!=new): {changed}")

# Show the first 20 mappings
print(f"\nFirst 20 mappings (orig_cid -> new_id):")
for orig_cid, new_id in sorted(compiler._orig_to_new_id.items())[:20]:
    lib = libs_by_cid.get(orig_cid, {})
    status = "SAME" if orig_cid == new_id else f"CHANGED"
    print(f"  orig={orig_cid:4d} -> new={new_id:4d}  {status}  name={lib.get('name','?')[:30]:30s} type={lib.get('type','?')}")

# Show how many IDs shifted and by how much
shifts = [abs(new - orig) for orig, new in compiler._orig_to_new_id.items() if orig != new]
if shifts:
    print(f"\nID shift stats (for {len(shifts)} changed IDs):")
    print(f"  Min shift: {min(shifts)}")
    print(f"  Max shift: {max(shifts)}")
    print(f"  Mean shift: {sum(shifts)/len(shifts):.1f}")

# Check emission order
print(f"\nEmission order length: {len(compiler._emission_order)}")
print(f"First 10 in emission order: {compiler._emission_order[:10]}")

# Check if emission order matches topological requirements
print(f"\n=== Reference Types That Need Remapping ===")

# Count shapes with bitmap fills
shapes_with_bitmap = sum(1 for lib in data['libraries'] 
                         if lib.get('type') == 'shape' and lib.get('inBitmap'))
print(f"Shapes with bitmap fills: {shapes_with_bitmap}")

# Count morph shapes with bitmap fills
morph_with_bitmap = sum(1 for lib in data['libraries'] 
                        if lib.get('isMorphShape') and lib.get('inBitmap'))
print(f"Morph shapes with bitmap fills: {morph_with_bitmap}")

# Count containers (sprites) with rawTagBody
sprites_with_raw = sum(1 for lib in data['libraries']
                       if lib.get('type') == 'container' and lib.get('rawTagBody'))
print(f"Sprites with rawTagBody: {sprites_with_raw}")

# Count shapes with rawTagBody (these have internal bitmap refs in fill styles)
shapes_with_raw = sum(1 for lib in data['libraries']
                      if lib.get('type') == 'shape' and lib.get('rawTagBody') and not lib.get('isMorphShape'))
print(f"Shapes with rawTagBody: {shapes_with_raw}")

# Count morph shapes with rawTagBody
morph_with_raw = sum(1 for lib in data['libraries']
                     if lib.get('isMorphShape') and lib.get('rawTagBody'))
print(f"Morph shapes with rawTagBody: {morph_with_raw}")

# Fonts with rawTagBody
fonts_with_raw = sum(1 for lib in data['libraries']
                     if lib.get('type') == 'font' and lib.get('rawTagBody'))
print(f"Fonts with rawTagBody: {fonts_with_raw}")

# Text with rawTagBody
texts_with_raw = sum(1 for lib in data['libraries']
                     if lib.get('type') == 'text' and lib.get('rawTagBody'))
print(f"Texts with rawTagBody: {texts_with_raw}")

# Now check: do any shapes have bitmap charID references in their rawTagBody?
# DefineShape fill styles can reference bitmap charIDs
# FillStyle type 0x40 = repeating bitmap, 0x41 = clipped bitmap,
# 0x42 = non-smoothed repeating, 0x43 = non-smoothed clipped
print(f"\n=== Checking shape rawTagBody for bitmap fill refs ===")
bitmap_ref_shapes = 0
for lib in data['libraries']:
    if lib.get('type') != 'shape' or lib.get('isMorphShape'):
        continue
    if not lib.get('rawTagBody'):
        continue
    import base64
    body = base64.b64decode(lib['rawTagBody'])
    # Quick check: does this shape body contain bitmap fill type bytes?
    # Not a thorough parse, but check if inBitmap is set
    if lib.get('inBitmap'):
        bitmap_ref_shapes += 1
        cid = lib.get('swfCharId')
        print(f"  Shape cid={cid} name={lib.get('name','?')}: has bitmap fill refs (rawTagType={lib.get('rawTagType')})")
        if bitmap_ref_shapes >= 10:
            print("  ... (showing first 10)")
            break

# Similarly for morph shapes
print(f"\n=== Checking morph shape rawTagBody for bitmap fill refs ===")
bitmap_ref_morphs = 0
for lib in data['libraries']:
    if not lib.get('isMorphShape'):
        continue
    if not lib.get('rawTagBody'):
        continue
    if lib.get('inBitmap'):
        bitmap_ref_morphs += 1
        cid = lib.get('swfCharId')
        print(f"  MorphShape cid={cid} name={lib.get('name','?')}: has bitmap fill refs")

# Text tags reference font charIDs  
print(f"\n=== Checking text rawTagBody for font refs ===")
for lib in data['libraries']:
    if lib.get('type') != 'text':
        continue
    cid = lib.get('swfCharId')
    print(f"  Text cid={cid} name={lib.get('name','?')}: rawTagType={lib.get('rawTagType')}")
