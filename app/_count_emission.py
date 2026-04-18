"""Diagnostic: count how many bitmaps are in emission_order vs total bitmap libs."""
import sys, os
sys.path.insert(0, '.')
from compile_n2d import load_n2d, N2DCompiler
from compilation_pipeline import CompilationContext, AllocateCharIDsStage, ParseRawTagsStage

n2d_path = r'converted\blackmage\project.n2d'
data, project_dir = load_n2d(n2d_path)

# Create context and run alloc stage
ctx = CompilationContext(n2d_path=n2d_path, shared_dir=r'converted\blackmage\scripts',
                          output_path='test_out.swf')
ctx.data = data
ctx.project_dir = project_dir
ctx.libs = data.get('libraries', [])
ctx.id_to_lib = {l['id']: l for l in ctx.libs}

# Run alloc stage
stage = AllocateCharIDsStage()
stage.execute(ctx)

# Count bitmaps in emission_order
bitmap_libs_set = {l['id'] for l in ctx.libs if l.get('type') == 'bitmap'}
bitmaps_in_emission = [lid for lid in ctx.emission_order if lid in bitmap_libs_set]
deferred_bitmaps = [lid for lid in ctx.deferred_lib_ids if lid in bitmap_libs_set]

print(f"Total bitmap libs: {len(bitmap_libs_set)}")
print(f"Bitmaps in emission_order: {len(bitmaps_in_emission)}")
print(f"Bitmaps in deferred_lib_ids: {len(deferred_bitmaps)}")
print(f"Total covered: {len(set(bitmaps_in_emission) | set(deferred_bitmaps))}")
missing = bitmap_libs_set - set(bitmaps_in_emission) - set(deferred_bitmaps)
print(f"Bitmaps MISSING from both: {len(missing)}")
if missing:
    print(f"  Sample missing lib ids: {list(missing)[:10]}")
