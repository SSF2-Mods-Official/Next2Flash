"""Output the _orig_to_new_id mapping as JSON to stdout for cross-process comparison."""
import json, zipfile, sys, os, copy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

N2D_PATH = 'converted/gameandwatch_cli.n2d'
with zipfile.ZipFile(N2D_PATH) as zf:
    data = json.loads(zf.read('project.json'))

import compile_n2d
c = compile_n2d.N2DCompiler.__new__(compile_n2d.N2DCompiler)
c.n2d_path = N2D_PATH
c.shared_dir = '.'
c.output_path = 'converted/_test.swf'
c.sdk_path = None
c.data = copy.deepcopy(data)
c.stage = c.data.get("stage", {})
c.libs = c.data.get("libraries", [])
c.id_to_lib = {lib["id"]: lib for lib in c.libs}
c._next_id = 1
c._lib_to_swf_id = {}
c._lib_to_char_idx = {}
c._char_idx_to_swf_id = {}
c._definition_tags = bytearray()
c._assign_ids()

# Output mapping sorted by key
print(json.dumps({str(k): v for k, v in sorted(c._orig_to_new_id.items())}))
