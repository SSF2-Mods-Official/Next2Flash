"""Check if reinstated flags survive import→export for pichu Idle_3 depth 1."""
import sys, os, json, struct, zlib, time

sys.path.insert(0, os.path.dirname(__file__))
from swf_to_n2d import parse_swf, N2DBuilder, decompile_all_scripts

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\pichu.ssf"

with open(OG, 'rb') as f:
    swf_data = f.read()
header, tags = parse_swf(swf_data)
builder = N2DBuilder(header, name="pichu")
builder.catalog_swf_tags(tags)
scripts, frame_scripts = decompile_all_scripts(builder.global_raw_tags)
builder.frame_scripts = frame_scripts
builder.build_all()
builder.build_main_timeline(tags)
n2d_data = builder.to_n2d_json()

# Find Idle_3 in the library
library = n2d_data.get("libraries", [])  # Note: 'libraries' not 'library'
print(f"Library items: {len(library)}")
idle3 = None
for item in library:
    name = item.get("name", "")
    scn = item.get("symbolClassName", "")
    if "Idle_3" in name or "Idle_3" in scn:
        idle3 = item
        break

if not idle3:
    # Try looking in nested containers
    for item in library:
        sym = item.get("symbol", "")
        nm = item.get("name", "")
        tp = item.get("type", "")
        if "Idle" in sym or "Idle" in nm:
            print(f"  Found: name={nm}, symbol={sym}, type={tp}")
        # Also check symbolClassName
        scn = item.get("symbolClassName", "")
        if "Idle" in scn:
            print(f"  Found via symbolClassName: name={nm}, scn={scn}")
            idle3 = item

if idle3:
    print(f"Found Idle_3: name={idle3.get('name')}, symbol={idle3.get('symbol')}")
    print(f"  Keys: {list(idle3.keys())}")
    layers = idle3.get("layers", [])
    print(f"  Layers: {len(layers)}")
    
    total_reinstated = 0
    total_chars = 0
    for layer in layers:
        swf_depth = layer.get("swfDepth")
        chars = layer.get("characters", [])
        for ch in chars:
            total_chars += 1
            reinstated = ch.get("reinstated", False)
            if reinstated:
                total_reinstated += 1
            lib_id = ch.get("libraryId")
            sf = ch.get("startFrame")
            ef = ch.get("endFrame")
            name = ch.get("name", "")
            if swf_depth == 1:
                lib_name = ""
                for lib_item in library:
                    if lib_item.get("id") == lib_id:
                        lib_name = lib_item.get("name", "")
                        break
                print(f"  depth={swf_depth} frames={sf}-{ef} libId={lib_id} libName={lib_name!r} name={name!r} reinstated={reinstated}")
    print(f"\nSummary: {total_chars} total character spans, {total_reinstated} with reinstated=True")
else:
    # Debug: show what the library items look like
    containers = [item for item in library if item.get("type") == "container"]
    print(f"Total library items: {len(library)}, containers: {len(containers)}")
    if containers:
        sample = containers[0]
        print(f"Sample container keys: {list(sample.keys())}")
        tl = sample.get("timeline")
        if tl:
            print(f"  timeline keys: {list(tl.keys())}")
        else:
            print(f"  NO timeline key. Full keys: {list(sample.keys())}")
            # Maybe timeline is nested differently
            for k, v in sample.items():
                if isinstance(v, dict):
                    print(f"    {k}: dict with keys {list(v.keys())[:10]}")
                elif isinstance(v, list):
                    print(f"    {k}: list of {len(v)} items")
                else:
                    print(f"    {k}: {type(v).__name__} = {str(v)[:80]}")
    else:
        # Check types
        types = {}
        for item in library:
            t = item.get("type", "NO_TYPE")
            types[t] = types.get(t, 0) + 1
        print(f"Library types: {types}")
        if library:
            print(f"Sample item keys: {list(library[0].keys())}")
            for k, v in library[0].items():
                print(f"  {k}: {type(v).__name__} = {str(v)[:100]}")
