"""Check DAir_73 N2D layer structure in detail."""
import sys
sys.path.insert(0, '.')
from compile_n2d import load_n2d

N2D_PATH = r'converted\blackmage\project.n2d'
data, project_dir = load_n2d(N2D_PATH)

libs = data.get('libraries', [])
id_to_lib = {l['id']: l for l in libs}

dair = next((l for l in libs if l.get('name') == 'DAir_73'), None)

layers = dair.get('layers', [])
print(f"DAir_73: {dair.get('totalFrame')} frames, {len(layers)} layers")

for li, layer in enumerate(layers[:3]):  # first 3 layers
    lname = layer.get('name', f'layer{li}')
    keys = list(layer.keys())
    print(f"\nLayer {li} ({lname}) keys: {keys}")
    for k in keys:
        v = layer[k]
        if isinstance(v, list):
            print(f"  {k}: list[{len(v)}]")
            if v:
                item0 = v[0]
                if isinstance(item0, dict):
                    print(f"    item[0] keys: {list(item0.keys())}")
                    print(f"    item[0]: {item0}")
                else:
                    print(f"    item[0]: {item0} (type={type(item0).__name__})")
        elif isinstance(v, (str, bytes)) and len(str(v)) > 80:
            print(f"  {k}: {str(v)[:80]}...")
        else:
            print(f"  {k}: {repr(v)}")
