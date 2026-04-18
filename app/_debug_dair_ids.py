import sys, struct, zlib
sys.path.insert(0, r'C:\Users\glwex\Documents\GitHub\Next2Flash\app')
from compile_n2d import load_n2d

N2D = r'C:\Users\glwex\Documents\GitHub\Next2Flash\app\converted\blackmage\project.n2d'
data, pdir = load_n2d(N2D)

print("=== Libraries with 'dair' in name ===")
dair_libs = []
for lib in data.get('libraries', []):
    name = lib.get('name', '')
    if 'dair' in name.lower():
        t = lib.get('type', '?')
        cid = lib.get('char_id', lib.get('id', '?'))
        print(f"  {name!r:40s}  type={t!r}  id={cid}")
        dair_libs.append(lib)

print()
print("=== Sprites/animations referencing dair bitmaps ===")
for lib in data.get('libraries', []):
    name = lib.get('name', '')
    if 'dair' in name.lower() and lib.get('type') in ('sprite', 'movieclip', 'animation'):
        print(f"\nSprite: {name!r}")
        for item in lib.get('frames', [lib]):
            for layer in item.get('layers', []):
                for obj in layer.get('objects', []):
                    ref = obj.get('lib_name', obj.get('char_name', ''))
                    if ref:
                        print(f"    -> {ref!r}")
