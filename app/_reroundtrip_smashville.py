"""Re-roundtrip smashville.ssf with current code and compare with existing RT."""
import sys, os, tempfile
sys.path.insert(0, os.path.dirname(__file__))
from swf_to_n2d import parse_swf, N2DBuilder, save_n2d, decompile_all_scripts
from compilation_pipeline import CompilationContext, create_default_pipeline

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\stage\smashville.ssf"
EXISTING_RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\stage\smashville.ssf"
NEW_RT = os.path.join(tempfile.gettempdir(), "smashville_new_rt.ssf")

print("1. Importing OG smashville.ssf...")
with open(OG, 'rb') as f:
    swf_data = f.read()
header, tags = parse_swf(swf_data)
builder = N2DBuilder(header, name="smashville")
builder.catalog_swf_tags(tags)
scripts, frame_scripts = decompile_all_scripts(builder.global_raw_tags)
builder.frame_scripts = frame_scripts
builder.build_all()
builder.build_main_timeline(tags)
n2d = builder.to_n2d_json()

n2d_path = os.path.join(tempfile.gettempdir(), "smashville_test.n2d")
save_n2d(n2d, n2d_path)
print(f"  Saved n2d: {n2d_path}")

print("2. Exporting to SWF...")
ctx = CompilationContext(n2d_path, "", NEW_RT)
pipeline = create_default_pipeline()
pipeline.execute(ctx)
print(f"  Saved: {NEW_RT}")

# Compare sizes
print(f"\n3. File sizes:")
print(f"  OG:          {os.path.getsize(OG):,} bytes")
print(f"  Existing RT: {os.path.getsize(EXISTING_RT):,} bytes")
print(f"  New RT:      {os.path.getsize(NEW_RT):,} bytes")

# Binary compare
with open(EXISTING_RT, 'rb') as f:
    existing_bytes = f.read()
with open(NEW_RT, 'rb') as f:
    new_bytes = f.read()

if existing_bytes == new_bytes:
    print("\n  Existing RT and New RT are IDENTICAL")
else:
    print(f"\n  Existing RT and New RT DIFFER")
    print(f"  Existing: {len(existing_bytes):,} bytes")
    print(f"  New:      {len(new_bytes):,} bytes")
