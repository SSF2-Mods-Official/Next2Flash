"""Search all libraries for morph shapes by examining their 'type' field and nested structures."""
import zipfile, msgpack, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

n2d = "test_swfs/lloyd_rt.n2d"

with zipfile.ZipFile(n2d, 'r') as z:
    with z.open('project.msgpack') as f:
        raw = f.read()

data = msgpack.unpackb(raw, raw=False)
libs = data.get('libraries', [])

# Check library types
type_counts = {}
for lib in libs:
    if isinstance(lib, dict):
        t = lib.get('type', 'unknown')
        type_counts[t] = type_counts.get(t, 0) + 1

print("Library types:", type_counts)

# Find morph-type libraries
morph_libs = []
for i, lib in enumerate(libs):
    if isinstance(lib, dict):
        t = lib.get('type', '')
        name = lib.get('name', '')
        if 'morph' in str(t).lower() or 'morph' in str(name).lower():
            morph_libs.append((i, lib))
        # Also check rawTagType
        rtt = lib.get('rawTagType', '')
        if rtt in (46, 84):
            morph_libs.append((i, lib))

print(f"\nLibraries with 'morph' in type/name or rawTagType 46/84: {len(morph_libs)}")
for i, lib in morph_libs[:5]:
    print(f"  lib[{i}]: type={lib.get('type', '')} name={lib.get('name', '')} rawTagType={lib.get('rawTagType', '')}")
    print(f"    keys: {sorted(lib.keys())}")

# Check all unique library key sets to find morph shapes
key_patterns = {}
for lib in libs:
    if isinstance(lib, dict):
        ks = frozenset(lib.keys())
        if ks not in key_patterns:
            key_patterns[ks] = {'count': 0, 'example_type': lib.get('type', ''), 'example_name': lib.get('name', '')}
        key_patterns[ks]['count'] += 1

print(f"\nUnique key patterns ({len(key_patterns)}):")
for ks, info in sorted(key_patterns.items(), key=lambda x: -x[1]['count']):
    keys_list = sorted(ks)
    print(f"  {info['count']}x: type={info['example_type']} keys={keys_list}")

# Search for 'recodes' or 'endRecodes' anywhere in the data
def find_key_recursive(obj, target_key, path="", depth=0, max_depth=5, results=None):
    if results is None:
        results = []
    if depth > max_depth:
        return results
    if isinstance(obj, dict):
        for k, v in obj.items():
            if target_key in str(k).lower():
                results.append((f"{path}.{k}", type(v).__name__, len(v) if hasattr(v, '__len__') else '?'))
            find_key_recursive(v, target_key, f"{path}.{k}", depth+1, max_depth, results)
    elif isinstance(obj, list) and depth < 3:
        for i, item in enumerate(obj[:5]):  # Only check first 5 items
            find_key_recursive(item, target_key, f"{path}[{i}]", depth+1, max_depth, results)
    return results

print("\nSearching for 'recode' in data structure...")
results = find_key_recursive(data, 'recode')
print(f"Found {len(results)} matches:")
for path, typ, length in results[:10]:
    print(f"  {path}: {typ} len={length}")

print("\nSearching for 'endrecodes' in data structure...")
results2 = find_key_recursive(data, 'endrecodes')
print(f"Found {len(results2)} matches:")
for path, typ, length in results2[:10]:
    print(f"  {path}: {typ} len={length}")

# Check what 'shape' type libraries look like
print("\n\nChecking 'shape' type libraries...")
shape_count = 0
for i, lib in enumerate(libs):
    if isinstance(lib, dict) and lib.get('type', '') in ('shape', 'morphShape', 'MorphShape'):
        shape_count += 1
        if shape_count <= 3:
            print(f"  lib[{i}]: type={lib.get('type', '')} keys={sorted(lib.keys())}")
            for k in ['recodes', 'endRecodes']:
                if k in lib:
                    val = lib[k]
                    if isinstance(val, bytes):
                        print(f"    {k}: bytes({len(val)}) hex={val[:30].hex()}")
print(f"  Total: {shape_count}")
