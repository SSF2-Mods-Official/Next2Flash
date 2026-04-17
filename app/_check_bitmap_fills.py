"""Check how bitmap fills look in N2D shape recodes — do they have proper bitmapId refs?"""
import sys, os, json, struct, zlib, base64, io
sys.path.insert(0, os.path.dirname(__file__))

# Import the N2D from the fox.ssf
OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"

from swf_to_n2d import swf_file_to_n2d
print("Importing fox.ssf...")
result = swf_file_to_n2d(OG, decode_bitmaps=True)
libs = result["library"]

# Find shapes with bitmap fills in their recodes
BITMAP_FILL = 3  # CMD_BITMAP_FILL from shape_converter
shapes_with_bitmaps = []
total_bmp_fills = 0
resolved_fills = 0
unresolved_fills = 0

for lib in libs:
    if lib.get("type") != "shape":
        continue
    recodes = lib.get("recodes", [])
    if not recodes:
        continue
    # Scan for CMD_BITMAP_FILL
    i = 0
    bmp_fills_in_shape = []
    while i < len(recodes):
        val = recodes[i]
        if isinstance(val, bool):
            break
        cmd = int(val)
        i += 1
        if cmd == BITMAP_FILL:
            # The next value should be the bitmap ref
            if i < len(recodes):
                bmp_ref = recodes[i]
                bmp_fills_in_shape.append((i, bmp_ref, type(bmp_ref).__name__))
                total_bmp_fills += 1
                if isinstance(bmp_ref, (int, float)) and bmp_ref > 0:
                    resolved_fills += 1
                elif isinstance(bmp_ref, dict) and bmp_ref.get("bitmapId", 0) > 0:
                    resolved_fills += 1
                else:
                    unresolved_fills += 1
            # Skip the rest of bitmap fill params
            # Rich format: bmp_ref, matrix, repeat, smooth
            if i < len(recodes) and isinstance(recodes[i], (int, float, dict)):
                i += 1  # bmp_ref
                if i < len(recodes) and isinstance(recodes[i], list):
                    i += 1  # matrix
                if i < len(recodes):
                    i += 1  # repeat
                if i < len(recodes):
                    i += 1  # smooth
    
    if bmp_fills_in_shape:
        shapes_with_bitmaps.append((lib["id"], lib.get("name", "?"), bmp_fills_in_shape))

print(f"\nShapes with bitmap fills: {len(shapes_with_bitmaps)}")
print(f"Total bitmap fills: {total_bmp_fills}")
print(f"With valid bitmapId: {resolved_fills}")
print(f"Without bitmapId: {unresolved_fills}")

# Show first 10 examples
print(f"\nFirst 10 shapes with bitmap fills:")
for lib_id, name, fills in shapes_with_bitmaps[:10]:
    print(f"  Shape id={lib_id} '{name}':")
    for pos, ref, reftype in fills:
        if isinstance(ref, dict):
            print(f"    pos={pos}: dict with bitmapId={ref.get('bitmapId',0)}, w={ref.get('width',0)}, h={ref.get('height',0)}, buf_len={len(ref.get('buffer',''))}")
        elif isinstance(ref, (int, float)):
            print(f"    pos={pos}: int ref={int(ref)} (N2D lib ID)")
        else:
            print(f"    pos={pos}: {reftype} value={ref}")

# Check: are these bitmapId refs valid library IDs?
lib_ids = {lib["id"] for lib in libs}
bitmap_lib_ids = {lib["id"] for lib in libs if lib.get("type") == "bitmap"}
print(f"\nTotal library IDs: {len(lib_ids)}")
print(f"Bitmap library IDs: {len(bitmap_lib_ids)}")

# Check which bitmap refs actually resolve
unresolvable = []
for lib_id, name, fills in shapes_with_bitmaps:
    for pos, ref, reftype in fills:
        bmp_id = 0
        if isinstance(ref, (int, float)):
            bmp_id = int(ref)
        elif isinstance(ref, dict):
            bmp_id = ref.get("bitmapId", 0)
        if bmp_id and bmp_id not in bitmap_lib_ids:
            unresolvable.append((lib_id, name, pos, bmp_id))

print(f"Bitmap refs that DON'T resolve to bitmap lib IDs: {len(unresolvable)}")
if unresolvable:
    for lid, name, pos, bid in unresolvable[:10]:
        # Check if it resolves to ANY lib type
        matching_lib = [l for l in libs if l["id"] == bid]
        if matching_lib:
            print(f"  Shape id={lid} refs bitmapId={bid} → lib type='{matching_lib[0].get('type','?')}' name='{matching_lib[0].get('name','?')}'")
        else:
            print(f"  Shape id={lid} refs bitmapId={bid} → NOT FOUND in library!")
