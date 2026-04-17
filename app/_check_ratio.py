"""Quick check: does the N2D data for fox depth-7 characters have ratio values?"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))

from swf_to_n2d import parse_swf, validate_swf_sprites, N2DBuilder

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"
with open(OG, 'rb') as f:
    swf_data = f.read()
header, tags = parse_swf(swf_data)
validate_swf_sprites(tags)
builder = N2DBuilder(header, name="fox")
builder.catalog_swf_tags(tags)
builder.frame_scripts = {}
builder.build_all()
builder.build_main_timeline(tags)
n2d = builder.to_n2d_json()

# Find the fox container (lib with 84 character spans at a single depth)
fox_lib = None
for lib in n2d.get("libraries", []):
    if lib.get("type") != "container":
        continue
    for layer in lib.get("layers", []):
        chars = layer.get("characters", [])
        if len(chars) > 80 and layer.get('swfDepth') == 7:
            fox_lib = lib
            print(f"Fox container: id={lib['id']}, name='{lib.get('name')}'")
            print(f"  Layer swfDepth=7 has {len(chars)} character spans")
            
            # Check ratio in places
            ratios_found = 0
            ratios_missing = 0
            for ci, ch in enumerate(chars[:10]):
                places = ch.get('places', [])
                for pi, p in enumerate(places):
                    ratio = p.get('ratio')
                    if ratio is not None:
                        ratios_found += 1
                        if ci < 5:
                            print(f"  char[{ci}] place[{pi}]: frame={p.get('frame')}, ratio={ratio}")
                    else:
                        ratios_missing += 1
                        if ci < 5:
                            print(f"  char[{ci}] place[{pi}]: frame={p.get('frame')}, ratio=MISSING")
            
            # Check all characters
            all_rf = 0
            all_rm = 0
            for ch in chars:
                for p in ch.get('places', []):
                    if p.get('ratio') is not None:
                        all_rf += 1
                    else:
                        all_rm += 1
            print(f"\n  Total depth-7 places with ratio: {all_rf}")
            print(f"  Total depth-7 places without ratio: {all_rm}")
            break
    if fox_lib:
        break

if not fox_lib:
    print("ERROR: Could not find fox container!")
