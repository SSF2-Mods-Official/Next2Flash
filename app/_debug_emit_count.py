"""Add print to _emit_bitmap to count actual calls, then recompile and count."""
import sys, os
sys.path.insert(0, '.')

# Patch compile_n2d._emit_bitmap to log calls
import compile_n2d as cn

_orig_emit_bitmap = cn.N2DCompiler._emit_bitmap
_call_log = {'external': 0, 'buffer': 0, 'total': 0, 'no_tag': 0}

def _patched_emit_bitmap(self, lib):
    _call_log['total'] += 1
    swf_id = self._lib_to_swf_id[lib["id"]]
    if self._project_dir and lib.get("externalFile"):
        tag_bytes = cn._load_external_bitmap(self._project_dir, lib, swf_id)
        if tag_bytes:
            _call_log['external'] += 1
            self._definition_tags.extend(tag_bytes)
            _w = lib.get("width", 1); _h = lib.get("height", 1)
            shape_id = self._alloc_id()
            self._definition_tags.extend(cn.build_bitmap_fill_shape(shape_id, swf_id, _w, _h))
            return
        else:
            _call_log['no_tag'] += 1
    else:
        _call_log['buffer'] += 1

cn.N2DCompiler._emit_bitmap = _patched_emit_bitmap

# Now run compilation
from export_n2d import export_swf
import msgpack, gzip

n2d_path = r'converted\blackmage\project.n2d'
with open(n2d_path, 'rb') as f:
    data = msgpack.unpackb(gzip.decompress(f.read()), raw=False)

from compile_n2d import load_n2d
data, project_dir = load_n2d(n2d_path)

from compilation_pipeline import CompilationContext, compile_n2d_to_swf
ctx = CompilationContext(n2d_path=n2d_path, 
                          shared_dir=r'converted\blackmage\scripts',
                          output_path='_test_count.swf')
ctx.data = data
ctx.project_dir = project_dir

compile_n2d_to_swf(ctx)

print(f"_emit_bitmap call stats: {_call_log}")
