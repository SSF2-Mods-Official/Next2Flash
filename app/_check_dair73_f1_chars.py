"""Find DAir_73 layers with bitmap chars at frame 1."""
import sys
sys.path.insert(0, '.')
from compile_n2d import load_n2d

N2D_PATH = r'converted\blackmage\project.n2d'
data, project_dir = load_n2d(N2D_PATH)

libs = data.get('libraries', [])
id_to_lib = {l['id']: l for l in libs}

dair = next((l for l in libs if l.get('name') == 'DAir_73'), None)

for li, layer in enumerate(dair.get('layers', [])):
    lname = layer.get('name', f'layer{li}')
    swf_depth = layer.get('swfDepth', None)
    for char in layer.get('characters', []):
        startf = char.get('startFrame', -1)
        endf = char.get('endFrame', -1)
        lib_id = char.get('libraryId', None)
        char_name = char.get('name', '')
        lib = id_to_lib.get(lib_id, {})
        lib_type = lib.get('type', '?')
        lib_name = lib.get('name', '?')
        # Check if frame 1 (index 0) is within range
        on_frame1 = (startf <= 1 <= endf) if startf != -1 else False
        if on_frame1 or lib_type == 'bitmap':
            print(f"Layer {li}({lname}) depth={swf_depth}: char '{char_name}' libId={lib_id}({lib_name}/{lib_type}) frames {startf}-{endf} on_f1={on_frame1}")
            if on_frame1 and lib_type == 'bitmap':
                places = char.get('places', [])
                print(f"  place data: {places[:2]}")  # first 2 places
