#!/usr/bin/env python3
"""Quick check: does fox.ssf N2D data have a library ID=0 (main container)?"""
import sys, os, tempfile
sys.path.insert(0, os.path.dirname(__file__))

from swf_to_n2d import N2DBuilder, parse_swf, save_n2d
from compile_n2d import load_n2d

SSF = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\fox.ssf"

with open(SSF, 'rb') as f:
    raw = f.read()

header, tags = parse_swf(raw)
builder = N2DBuilder(header, "fox")
builder.catalog_swf_tags(tags)
builder.frame_scripts = {}
builder.build_all()
builder.build_main_timeline(tags)  # THIS WAS MISSING!
builder._embed_bitmap_data_in_recodes()
n2d = builder.to_n2d_json()

libs = n2d.get("libraries", [])
print(f"Total libraries: {len(libs)}")
has_id0 = any(lib["id"] == 0 for lib in libs)
print(f"Has library id=0: {has_id0}")
if has_id0:
    main = [lib for lib in libs if lib["id"] == 0][0]
    print(f"Main type: {main.get('type')}")
    print(f"Main layers: {len(main.get('layers', []))}")
    print(f"Main totalFrame: {main.get('totalFrame')}")
    n_chars = sum(len(l.get("characters", [])) for l in main.get("layers", []))
    print(f"Main total characters: {n_chars}")

# Now save and reload to check it survives the cycle
n2d_path = os.path.join(tempfile.gettempdir(), "fox_id0_check.n2d")
save_n2d(n2d, n2d_path, bitmap_buffers=builder.bitmap_buffers)
print(f"\nSaved to: {n2d_path}")

data2, _ = load_n2d(n2d_path)
libs2 = data2.get("libraries", [])
has_id0_2 = any(lib["id"] == 0 for lib in libs2)
print(f"After reload - Total libraries: {len(libs2)}")
print(f"After reload - Has library id=0: {has_id0_2}")
if has_id0_2:
    main2 = [lib for lib in libs2 if lib["id"] == 0][0]
    print(f"After reload - Main type: {main2.get('type')}")
    print(f"After reload - Main layers: {len(main2.get('layers', []))}")
    print(f"After reload - Main totalFrame: {main2.get('totalFrame')}")
    n_chars2 = sum(len(l.get("characters", [])) for l in main2.get("layers", []))
    print(f"After reload - Main total characters: {n_chars2}")

# Now do the full compile and check for the warning
print("\n--- Full compile test ---")
from compilation_pipeline import CompilationContext, create_default_pipeline
rt_path = os.path.join(tempfile.gettempdir(), "fox_id0_rt.swf")
shared_dir = os.path.join(os.path.dirname(__file__), "shared")
ctx = CompilationContext(n2d_path=n2d_path, shared_dir=shared_dir, output_path=rt_path)
pipeline = create_default_pipeline()
pipeline.execute(ctx)

# Check id_to_lib in ctx
print(f"\nctx.id_to_lib has id=0: {0 in ctx.id_to_lib}")
print(f"RT SWF size: {os.path.getsize(rt_path):,} bytes")
