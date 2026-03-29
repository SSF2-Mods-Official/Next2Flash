"""Run _assign_ids() twice to check if the mapping is deterministic."""
import json, zipfile, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

N2D_PATH = 'converted/gameandwatch_cli.n2d'
with zipfile.ZipFile(N2D_PATH) as zf:
    data = json.loads(zf.read('project.json'))

import compile_n2d, importlib, copy
importlib.reload(compile_n2d)

results = []
for run in range(3):
    c = compile_n2d.N2DCompiler.__new__(compile_n2d.N2DCompiler)
    c.n2d_path = N2D_PATH
    c.shared_dir = '.'
    c.output_path = f'converted/_test_det{run}.swf'
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
    results.append(dict(c._orig_to_new_id))

# Compare all runs
match_01 = results[0] == results[1]
match_02 = results[0] == results[2]
print(f"Run 0 == Run 1: {match_01}")
print(f"Run 0 == Run 2: {match_02}")

if not match_01:
    diffs = [(k, results[0][k], results[1][k]) for k in results[0] if results[0][k] != results[1][k]]
    print(f"Differences between run 0 and 1: {len(diffs)}")
    for k, v0, v1 in diffs[:10]:
        print(f"  orig={k}: run0={v0}, run1={v1}")
else:
    print("All 3 runs produced identical ID mappings (deterministic within same process)")

# Also check: emission order
orders = []
for run in range(3):
    c = compile_n2d.N2DCompiler.__new__(compile_n2d.N2DCompiler)
    c.n2d_path = N2D_PATH
    c.shared_dir = '.'
    c.output_path = f'converted/_test_det{run}.swf'
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
    orders.append(list(c._emission_order))

print(f"\nEmission order run 0 == run 1: {orders[0] == orders[1]}")
print(f"Emission order run 0 == run 2: {orders[0] == orders[2]}")
