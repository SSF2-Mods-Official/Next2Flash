"""Examine lloyd N2D file to find morph shape data."""
import zipfile, json, msgpack, os, sys, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

n2d = "test_swfs/lloyd_rt.n2d"

with zipfile.ZipFile(n2d, 'r') as z:
    print("Files in N2D:")
    for info in z.infolist():
        print(f"  {info.filename} ({info.file_size} bytes)")
    
    # Read the main manifest/data
    for name in z.namelist():
        if name.endswith('.json'):
            with z.open(name) as f:
                data = json.load(f)
                if isinstance(data, dict):
                    print(f"\n{name} keys: {sorted(data.keys())[:30]}")
                    # Look for morph-related keys
                    for k, v in data.items():
                        if 'morph' in k.lower() or 'shape' in k.lower():
                            print(f"  {k}: type={type(v).__name__}", f"len={len(v)}" if hasattr(v, '__len__') else "")
        elif name.endswith('.msgpack'):
            with z.open(name) as f:
                raw = f.read()
                data = msgpack.unpackb(raw, raw=False)
                if isinstance(data, dict):
                    print(f"\n{name} keys: {sorted(data.keys())[:30]}")
                elif isinstance(data, list):
                    print(f"\n{name}: list of {len(data)} items")

    # Look for the main data file
    for name in z.namelist():
        if name in ('data.json', 'main.json', 'data.msgpack', 'main.msgpack'):
            with z.open(name) as f:
                raw = f.read()
            if name.endswith('.json'):
                data = json.loads(raw)
            else:
                data = msgpack.unpackb(raw, raw=False)
            
            if isinstance(data, dict):
                # Look for characters/dictionary
                for k in ['characters', 'dictionary', 'tags', 'sprites', 'library']:
                    if k in data:
                        items = data[k]
                        print(f"\n{name}/{k}: {type(items).__name__} len={len(items) if hasattr(items, '__len__') else '?'}")
                        if isinstance(items, dict):
                            # Find morph shapes
                            morph_count = 0
                            for cid, char in items.items():
                                if isinstance(char, dict):
                                    ctype = char.get('type', char.get('tagType', ''))
                                    if 'morph' in str(ctype).lower():
                                        morph_count += 1
                                        if morph_count <= 3:
                                            print(f"  charId={cid}: type={ctype}")
                                            print(f"    keys: {sorted(char.keys())[:15]}")
                                            # Show recodes info
                                            for rk in ['recodes', 'startRecodes', 'endRecodes', 'start_recodes', 'end_recodes']:
                                                if rk in char:
                                                    val = char[rk]
                                                    if isinstance(val, (bytes, str)):
                                                        print(f"    {rk}: {len(val)} bytes")
                                                    elif isinstance(val, list):
                                                        print(f"    {rk}: list of {len(val)} items, first={val[0] if val else 'empty'}")
                            print(f"  Total morph shapes: {morph_count}")
                        elif isinstance(items, list):
                            morph_count = 0
                            for char in items:
                                if isinstance(char, dict):
                                    ctype = char.get('type', char.get('tagType', ''))
                                    if 'morph' in str(ctype).lower():
                                        morph_count += 1
                                        if morph_count <= 3:
                                            print(f"  morph: type={ctype}")
                                            print(f"    keys: {sorted(char.keys())[:15]}")
                            print(f"  Total morph shapes: {morph_count}")
