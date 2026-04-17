"""Test to_publish for container 78 (10-frame morph sprite) and compare output with OG."""
import sys, os, struct, zlib, zipfile, io
sys.path.insert(0, os.path.dirname(__file__))

import msgpack
from compile_n2d import to_publish, _compute_total_frames

def load_n2d(path):
    with open(path, 'rb') as f:
        raw = f.read()
    if raw[:2] == b'PK':
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            if 'project.msgpack' in zf.namelist():
                return msgpack.unpackb(zf.read('project.msgpack'), raw=False)
    raise ValueError("Cannot load")

def main():
    n2d = load_n2d('converted/fox/project.n2d')
    libs = n2d['libraries']
    id_to_lib = {}
    for l in libs:
        if l:
            id_to_lib[l['id']] = l
    
    # Build lib_to_char_idx (maps lib_id → index in character array)
    # The compiler assigns sequential IDs - for testing, just use lib_id
    lib_to_char_idx = {}
    idx = 0
    for l in libs:
        if l:
            lib_to_char_idx[l['id']] = idx
            idx += 1
    
    # Get container 78
    container = id_to_lib[78]
    print("Container 78: name=%s totalFrame=%s" % (container.get('name'), container.get('totalFrame')))
    
    # Call to_publish
    tp = to_publish(container, lib_to_char_idx, id_to_lib)
    
    dictionary = tp['dictionary']
    controller = tp['controller']
    place_map = tp['placeMap']
    place_objects = tp['placeObjects']
    depth_keys = tp.get('depthKeys')
    
    print("\nDictionary (%d entries):" % len(dictionary))
    for i, d in enumerate(dictionary):
        print("  [%d] char_idx=%d name='%s' sf=%d ef=%d clipDepth=%d reinstated=%s" % (
            i, d['characterId'], d.get('name',''), d['startFrame'], d['endFrame'],
            d.get('clipDepth', 0), d.get('reinstated', False)))
    
    print("\nPlaceObjects (%d entries):" % len(place_objects))
    for i, po in enumerate(place_objects):
        mat = po.get('matrix')
        ct = po.get('colorTransform')
        ratio = po.get('ratio')
        has_ct = ct is not None
        print("  [%d] ratio=%s hasCT=%s blend=%s" % (i, ratio, has_ct, po.get('blendMode')))
    
    total_frames = container.get('totalFrame') or _compute_total_frames(container)
    print("\nTotal frames:", total_frames)
    
    print("\nFrame-by-frame timeline:")
    for frame in range(1, total_frames + 1):
        ctrl_f = controller[frame] if frame < len(controller) and controller[frame] is not None else None
        pm_f = place_map[frame] if frame < len(place_map) and place_map[frame] is not None else None
        dk_f = None
        if depth_keys and frame < len(depth_keys):
            dk_f = depth_keys[frame]
        
        if ctrl_f:
            print("\n  Frame %d:" % frame)
            for slot, (dict_idx, po_idx) in enumerate(zip(ctrl_f, pm_f)):
                d = dictionary[dict_idx]
                po = place_objects[po_idx]
                depth = dk_f[slot] + 1 if dk_f and slot < len(dk_f) else slot + 1
                ratio = po.get('ratio')
                has_ct = po.get('colorTransform') is not None
                char_idx = d['characterId']
                lib_id = None
                for lid, cidx in lib_to_char_idx.items():
                    if cidx == char_idx:
                        lib_id = lid
                        break
                print("    depth=%d dict[%d](lib=%s sf=%d-ef=%d) po[%d](ratio=%s hasCT=%s)" % (
                    depth, dict_idx, lib_id, d['startFrame'], d['endFrame'],
                    po_idx, ratio, has_ct))
        else:
            print("\n  Frame %d: empty" % frame)

if __name__ == '__main__':
    main()
