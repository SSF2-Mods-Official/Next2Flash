"""Check DAir_73 N2D frame 1 placements in detail."""
import sys
sys.path.insert(0, '.')
from compile_n2d import load_n2d

N2D_PATH = r'converted\blackmage\project.n2d'
data, project_dir = load_n2d(N2D_PATH)

libs = data.get('libraries', [])
id_to_lib = {l['id']: l for l in libs}

dair = next((l for l in libs if l.get('name') == 'DAir_73'), None)
assert dair, "DAir_73 not found"

print(f"DAir_73: {dair.get('totalFrame')} frames, {len(dair.get('layers', []))} layers")

# Find placements at frame 1 (index 0)
for li, layer in enumerate(dair.get('layers', [])):
    lname = layer.get('name', f'layer{li}')
    frames = layer.get('frames', [])
    for frame in frames:
        frame_idx = frame.get('index', -1)
        if frame_idx == 0:  # frame 1 = index 0
            placements = frame.get('placements', [])
            for p in placements:
                cid = p.get('libId', p.get('charId', None))
                pname = p.get('name', None)
                pdepth = p.get('depth', None)
                ptype = p.get('type', None)
                lib = id_to_lib.get(cid, {})
                lib_type = lib.get('type', '?')
                lib_name = lib.get('name', '?')
                # Check for PO type / hasImage
                is_bitmap = lib_type == 'bitmap'
                print(f"  Layer {li}({lname}), frame_idx={frame_idx}: depth={pdepth}, type={ptype}, libId={cid}({lib_name}/{lib_type}), name='{pname}'")
                # Print all placement keys for bitmaps
                if is_bitmap:
                    other_keys = {k: v for k, v in p.items() if k not in ('libId', 'charId', 'depth', 'name', 'type')}
                    print(f"    Extra placement fields: {other_keys}")
