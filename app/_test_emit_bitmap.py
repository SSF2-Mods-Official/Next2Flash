"""Test: emit one bitmap and count resulting tags."""
import sys, struct
sys.path.insert(0, '.')
from compile_n2d import load_n2d, N2DCompiler, build_bitmap_fill_shape

n2d_path = r'converted\blackmage\project.n2d'
data, project_dir = load_n2d(n2d_path)

libs = data.get('libraries', [])
bitmaps = [l for l in libs if l.get('type') == 'bitmap']
print(f"Total bitmaps: {len(bitmaps)}")

# Create a minimal compiler to test _emit_bitmap
comp = N2DCompiler.__new__(N2DCompiler)
comp._project_dir = project_dir
comp._definition_tags = bytearray()
comp._next_id = 2000
comp._emission_order = []
comp._deferred_lib_ids = []
comp._lib_to_swf_id = {}
comp.id_to_lib = {}
comp.libs = []
comp._font_aux_tags = {}
comp._bitmap_char_ids = set()
comp._bitmap_content_cache = {}
import logging
comp.log = logging.getLogger('test')

# Test with first 3 bitmaps
for lib in bitmaps[:3]:
    lid = lib['id']
    swf_id = 100 + lid
    comp._lib_to_swf_id[lid] = swf_id
    comp._definition_tags = bytearray()
    before = len(comp._definition_tags)
    comp._emit_bitmap(lib)
    result = bytes(comp._definition_tags)
    # Parse tags
    off = 0; tags = []
    while off < len(result):
        hdr = struct.unpack_from('<H', result, off)[0]; tt = hdr >> 6; ln = hdr & 0x3F; off += 2
        if ln == 63: ln = struct.unpack_from('<I', result, off)[0]; off += 4
        tags.append((tt, ln)); off += ln
    print(f"\nLib '{lib.get('name','?')}' (id={lid}, swfId={swf_id}):")
    print(f"  Emitted bytes: {len(result)}")
    for t, l in tags:
        name = {36: 'LL2', 32: 'DefShape3', 0: 'End'}.get(t, f'TT={t}')
        print(f"  Tag: {name} (TT={t}), len={l}")
    if len(tags) != 2:
        print(f"  ** WARNING: Expected 2 tags (LL2 + DefShape3), got {len(tags)}")
