"""Quick roundtrip of pichu.ssf to check RemoveObject2 emission."""
import sys, os, tempfile
sys.path.insert(0, os.path.dirname(__file__))
from swf_to_n2d import parse_swf, N2DBuilder, save_n2d, decompile_all_scripts
from compilation_pipeline import CompilationContext, create_default_pipeline

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\pichu.ssf"
OUT = os.path.join(tempfile.gettempdir(), "pichu_rt_test.ssf")

print("1. Importing pichu.ssf...")
with open(OG, 'rb') as f:
    swf_data = f.read()
header, tags = parse_swf(swf_data)
builder = N2DBuilder(header, name="pichu")
builder.catalog_swf_tags(tags)
scripts, frame_scripts = decompile_all_scripts(builder.global_raw_tags)
builder.frame_scripts = frame_scripts
builder.build_all()
builder.build_main_timeline(tags)
n2d = builder.to_n2d_json()

# Save temp n2d
n2d_path = os.path.join(tempfile.gettempdir(), "pichu_test.n2d")
save_n2d(n2d, n2d_path)
print(f"  Saved n2d: {n2d_path}")

print("2. Exporting back to SWF...")
ctx = CompilationContext(n2d_path, "", OUT)
pipeline = create_default_pipeline()
pipeline.execute(ctx)
print(f"  Saved SWF: {OUT}")
print("Done — check [DBG] lines above for is_move decisions")
