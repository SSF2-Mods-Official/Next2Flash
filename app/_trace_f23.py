#!/usr/bin/env python3
"""Trace the exact data for sprite 1140, depth=1, frame 23 move-only PO."""
import sys, os, struct, zlib, tempfile, json
sys.path.insert(0, os.path.dirname(__file__))
from swf_to_n2d import N2DBuilder, parse_swf, save_n2d
from compile_n2d import to_publish, _compute_total_frames, build_timeline_tags

SSF_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\fox.ssf"

with open(SSF_PATH, 'rb') as f:
    raw = f.read()

header, tags = parse_swf(raw)
builder = N2DBuilder(header, "fox")
builder.catalog_swf_tags(tags)
builder.frame_scripts = {}
builder.build_all()
builder.build_main_timeline(tags)
builder._embed_bitmap_data_in_recodes()

# Find the N2D lib for OG sprite 1140
n2d_lid = builder.swf_to_n2d.get(1140)
n2d_lib = None
for lib in builder.libraries:
    if lib.get('id') == n2d_lid:
        n2d_lib = lib
        break

print(f"N2D lib id={n2d_lid}, name='{n2d_lib.get('name')}'")
print(f"totalFrame={n2d_lib.get('totalFrame')}")

# Find the layer at swfDepth ~1 and the character span covering frame 23
layers = n2d_lib.get('layers', [])
for li, layer in enumerate(layers):
    depth = layer.get('swfDepth')
    chars = layer.get('characters', [])
    for ci, ch in enumerate(chars):
        sf = ch.get('startFrame', 1)
        ef = ch.get('endFrame', 1)
        # Does this span cover frame 23?
        if sf <= 23 and ef > 23 and depth == 1:
            print(f"\n=== Layer {li} depth={depth} char [{ci}] libId={ch.get('libraryId')} frames={sf}-{ef} ===")
            places = ch.get('places', [])
            print(f"  {len(places)} places:")
            for pi, pl in enumerate(places):
                mat = pl.get('matrix', [])
                frame = pl.get('frame')
                print(f"  [{pi}] frame={frame} matrix=[{', '.join(f'{v:.2f}' for v in mat[:6])}]")
            
            # Also check if there's a place at frame 23
            has_f23 = any(pl.get('frame') == 23 for pl in places)
            print(f"  Has place at frame 23: {has_f23}")
            
            # Check all frames 20-27
            for f in range(20, 28):
                has = any(pl.get('frame') == f for pl in places)
                if has:
                    pl_f = [pl for pl in places if pl.get('frame') == f][0]
                    print(f"  Frame {f}: matrix=[{', '.join(f'{v:.2f}' for v in pl_f.get('matrix', [])[:6])}]")

# Now trace through to_publish
print("\n=== to_publish trace ===")
# Build the char_idx mapping
id_to_lib = {lib['id']: lib for lib in builder.libraries}
lib_to_char_idx = {}
char_idx = 0
lib_to_char_idx[0] = char_idx
char_idx += 1
for lib in builder.libraries:
    if lib['id'] == 0 or lib.get('type') == 'folder':
        continue
    lib_to_char_idx[lib['id']] = char_idx
    char_idx += 1

tp = to_publish(n2d_lib, lib_to_char_idx, id_to_lib)
po_list = tp.get('placeObjects', [])
print(f"Total placeObjects: {len(po_list)}")

# Find which POs correspond to depth=1, around frame 23
# The pmap tells us per-frame-per-depth which PO index to use
# We need to check the actual timeline emission
# Let's look at the dictionary to find charIdx for the referenced libs
for li, layer in enumerate(layers):
    depth = layer.get('swfDepth')
    if depth != 1:
        continue
    chars = layer.get('characters', [])
    for ci, ch in enumerate(chars):
        sf = ch.get('startFrame', 1)
        ef = ch.get('endFrame', 1)
        if sf <= 23 and ef > 23:
            ref_lid = ch.get('libraryId')
            ref_cidx = lib_to_char_idx.get(ref_lid, '??')
            print(f"  Depth=1 frame 23: libId={ref_lid} char_idx={ref_cidx}")
            
            # Check the places array for matrix changes
            places = ch.get('places', [])
            print(f"  places frames: {[pl.get('frame') for pl in places]}")

# Trace what build_timeline_tags would emit for frames 22 and 23
print("\n=== build_timeline_tags PO emission for frames 20-25 ===")
# Check pmap — the frame→depth→po_idx mapping
# We need to look inside to_publish for pmap
# Let's reimplement the relevant check
from compile_n2d import _has_exact_place

for layer_data in layers:
    depth = layer_data.get('swfDepth')
    if depth != 1:
        continue
    for ch in layer_data.get('characters', []):
        sf = ch.get('startFrame', 1)
        ef = ch.get('endFrame', 1)
        if sf <= 23 and ef > 23:
            places = ch.get('places', [])
            for f in range(20, 28):
                if f < sf or f >= ef:
                    continue
                has_exact = _has_exact_place(places, f)
                # Which place would be active?
                active_place = None
                for pl in reversed(places):
                    if pl.get('frame', 1) <= f:
                        active_place = pl
                        break
                mat = active_place.get('matrix', []) if active_place else []
                mat_str = f"[{', '.join(f'{v:.2f}' for v in mat[:6])}]" if mat else "[]"
                print(f"  Frame {f}: has_exact_place={has_exact} active_mat={mat_str}")
