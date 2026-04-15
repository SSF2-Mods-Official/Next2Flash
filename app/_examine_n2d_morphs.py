"""Find morph shapes in N2D project.msgpack and dump their recodes."""
import zipfile, msgpack, os, sys, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

n2d = "test_swfs/lloyd_rt.n2d"

with zipfile.ZipFile(n2d, 'r') as z:
    with z.open('project.msgpack') as f:
        raw = f.read()

data = msgpack.unpackb(raw, raw=False)

# Explore 'libraries' structure
libs = data.get('libraries', [])
print(f"Libraries: {type(libs).__name__}")
if isinstance(libs, list):
    print(f"  count: {len(libs)}")
    for i, lib in enumerate(libs[:3]):
        if isinstance(lib, dict):
            print(f"  lib[{i}] keys: {sorted(lib.keys())[:20]}")
            items = lib.get('items', lib.get('characters', lib.get('definitions', [])))
            if isinstance(items, list):
                print(f"    items: {len(items)}")
                morph_count = 0
                for j, item in enumerate(items):
                    if isinstance(item, dict):
                        item_type = item.get('type', item.get('tagType', item.get('characterType', '')))
                        raw_tag = item.get('rawTagType', '')
                        if 'morph' in str(item_type).lower() or raw_tag in (46, 84, '46', '84'):
                            morph_count += 1
                            if morph_count <= 3:
                                print(f"    morph item[{j}]: type={item_type} rawTagType={raw_tag}")
                                print(f"      keys: {sorted(item.keys())}")
                                for rk in ['recodes', 'endRecodes', 'startRecodes', 'shapeBounds', 'edgeBounds']:
                                    if rk in item:
                                        val = item[rk]
                                        if isinstance(val, bytes):
                                            print(f"      {rk}: bytes len={len(val)} hex={val[:40].hex()}")
                                        elif isinstance(val, list):
                                            print(f"      {rk}: list len={len(val)} first_few={val[:5]}")
                                        else:
                                            print(f"      {rk}: {type(val).__name__} = {str(val)[:100]}")
                print(f"    Total morphs: {morph_count}")
elif isinstance(libs, dict):
    print(f"  keys: {sorted(libs.keys())[:20]}")

# Also check rootTimelineDefIds
rtd = data.get('rootTimelineDefIds', [])
print(f"\nrootTimelineDefIds: {type(rtd).__name__} len={len(rtd) if hasattr(rtd, '__len__') else '?'}")
