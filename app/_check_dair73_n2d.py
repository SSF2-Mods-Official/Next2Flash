"""Check N2D representation of DAir_73 container."""
import sys
sys.path.insert(0, '.')
from compile_n2d import load_n2d

N2D_PATH = r'converted\blackmage\project.n2d'
data, project_dir = load_n2d(N2D_PATH)

libs = data.get('libraries', [])
for lib in libs:
    if 'DAir_73' in lib.get('name', '') or lib.get('name', '') == 'DAir_73':
        print(f"Found: name={lib.get('name')}, id={lib.get('id')}, type={lib.get('type')}")
        keys = [k for k in lib if k not in ('name', 'id', 'type')]
        print(f"  Keys: {keys}")
        for k in keys:
            v = lib[k]
            if isinstance(v, (str, bytes)) and len(str(v)) > 100:
                print(f"  {k}: {str(v)[:80]}...")
            elif isinstance(v, list):
                print(f"  {k}: list[{len(v)}]")
                if k == 'frames' and v:
                    print(f"    Frame 0 keys: {list(v[0].keys()) if isinstance(v[0], dict) else type(v[0])}")
                    if isinstance(v[0], dict) and 'placements' in v[0]:
                        print(f"    Frame 0 placements[0]: {v[0]['placements'][0] if v[0]['placements'] else 'empty'}")
            else:
                print(f"  {k}: {v}")
        break
