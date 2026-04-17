"""Inspect N2D container data for sprites that differ in the compiled output.
Focus on OG sprite CID 78 (10-frame morph) to understand what to_publish receives."""
import sys, os, struct, zlib, json
sys.path.insert(0, os.path.dirname(__file__))

try:
    import msgpack
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'msgpack'])
    import msgpack

def load_n2d(path):
    import zipfile, io
    with open(path, 'rb') as f:
        raw = f.read()
    if raw[:2] == b'PK':
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            if 'project.msgpack' in zf.namelist():
                return msgpack.unpackb(zf.read('project.msgpack'), raw=False)
            return json.loads(zf.read('project.json'))
    import zlib
    decompressed = zlib.decompress(raw)
    return json.loads(decompressed.decode('utf-8'))

def parse_swf_all(path):
    with open(path, 'rb') as f:
        sig = f.read(3); f.read(1); f.read(4); rest = f.read()
    if sig == b'CWS': rest = zlib.decompress(rest)
    nbits = rest[0] >> 3; rect_bytes = (5 + 4 * nbits + 7) // 8
    offset = rect_bytes + 4; tags = []
    while offset < len(rest):
        if offset + 2 > len(rest): break
        tc = struct.unpack_from('<H', rest, offset)[0]; offset += 2
        tag_type = tc >> 6; length = tc & 0x3F
        if length == 0x3F:
            length = struct.unpack_from('<I', rest, offset)[0]; offset += 4
        data = rest[offset:offset + length]; offset += length
        tags.append((tag_type, data))
        if tag_type == 0: break
    return tags

def get_sprite_frame_count(data):
    fc = 0
    offset = 0
    while offset < len(data):
        if offset + 2 > len(data): break
        tc = struct.unpack_from('<H', data, offset)[0]; offset += 2
        tag_type = tc >> 6; length = tc & 0x3F
        if length == 0x3F:
            length = struct.unpack_from('<I', data, offset)[0]; offset += 4
        offset += length
        if tag_type == 1: fc += 1
        if tag_type == 0: break
    return fc

def main():
    n2d_path = r"converted\fox\project.n2d"
    og_path = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"
    
    n2d = load_n2d(n2d_path)
    
    # Top-level keys
    print(f"Top-level keys: {sorted(n2d.keys())}")
    
    libs = n2d.get("libs", n2d.get("library", []))
    print(f"libs count: {len(libs)}")
    if libs and isinstance(libs[0], dict):
        print(f"First lib keys: {sorted(libs[0].keys())}")
        print(f"First lib: id={libs[0].get('id')}, type={libs[0].get('type')}")
    elif libs:
        print(f"First lib type: {type(libs[0])}")
        if isinstance(libs[0], (list, tuple)) and libs[0]:
            print(f"First lib[0] type: {type(libs[0][0])}")
    
    # Check if there's a different structure
    for k in sorted(n2d.keys()):
        v = n2d[k]
        if isinstance(v, list):
            print(f"  {k}: list[{len(v)}]")
        elif isinstance(v, dict):
            print(f"  {k}: dict keys={sorted(v.keys())[:5]}...")
        else:
            print(f"  {k}: {type(v).__name__} = {str(v)[:80]}")
    
    # Find morph shapes
    morph_ids = set()
    for lib in libs:
        if lib.get("isMorphShape"):
            morph_ids.add(lib["id"])
    print(f"Total morph shapes in N2D: {len(morph_ids)}")
    if morph_ids:
        for mid in sorted(morph_ids)[:10]:
            ml = id_to_lib[mid]
            print(f"  MorphShape lib_id={mid} name={ml.get('name','?')}")
    
    # Parse OG to find sprite CID=78 frame count
    og_tags = parse_swf_all(og_path)
    og_sprite_info = {}
    for t, d in og_tags:
        if t == 39 and len(d) >= 4:
            cid = struct.unpack_from('<H', d, 0)[0]
            fc = get_sprite_frame_count(d[4:])
            og_sprite_info[cid] = fc
    
    print(f"\nOG sprite cid=78 has {og_sprite_info.get(78, '?')} frames")
    
    # Find N2D containers with 10 frames (matching OG 78)
    print("\n=== N2D Containers with 10 frames (matching OG cid=78) ===")
    for cid, lib in containers:
        tf = lib.get("totalFrame", 0)
        if tf != 10: continue
        layers = lib.get("layers", [])
        print(f"\nContainer lib_id={cid} name={lib.get('name','?')} totalFrame={tf}")
        print(f"  Layers: {len(layers)}")
        for li, layer in enumerate(layers):
            chars = layer.get("characters", [])
            mode = layer.get("mode", 0)
            swf_d = layer.get("swfDepth", "?")
            disable = layer.get("disable", False)
            print(f"  Layer[{li}] mode={mode} swfDepth={swf_d} disable={disable} chars={len(chars)}")
            for ci, ch in enumerate(chars):
                lib_id = ch.get("libraryId")
                sf = ch.get("startFrame")
                ef = ch.get("endFrame")
                name = ch.get("name", "")
                is_morph = lib_id in morph_ids
                ref_type = id_to_lib.get(lib_id, {}).get("type", "?")
                places = ch.get("places", [])
                n_places = len(places)
                print(f"    Char[{ci}] lib_id={lib_id} type={ref_type} morph={is_morph} "
                      f"sf={sf} ef={ef} name='{name}' places={n_places}")
                # Show first few places
                for pi, pl in enumerate(places[:3]):
                    ratio = pl.get("ratio")
                    ct = pl.get("colorTransform")
                    f = pl.get("frame", "?")
                    depth = pl.get("depth", 0)
                    has_ct = ct is not None and ct != [1,1,1,1,0,0,0,0]
                    print(f"      place[{pi}] frame={f} depth={depth} ratio={ratio} hasCT={has_ct}")
                if n_places > 3:
                    print(f"      ...and {n_places-3} more places")
    
    # Also look at a few 1-frame containers to check missing layers issue
    print("\n\n=== First 3 N2D Containers with 1 frame ===")
    count = 0
    for cid, lib in containers:
        tf = lib.get("totalFrame", 0)
        if tf != 1: continue
        layers = lib.get("layers", [])
        total_chars = sum(len(l.get("characters", [])) for l in layers)
        if total_chars <= 1: continue  # skip trivial
        print(f"\nContainer lib_id={cid} name={lib.get('name','?')} totalFrame={tf}")
        print(f"  Layers: {len(layers)} total_chars={total_chars}")
        for li, layer in enumerate(layers):
            chars = layer.get("characters", [])
            mode = layer.get("mode", 0)
            swf_d = layer.get("swfDepth", "?")
            print(f"  Layer[{li}] mode={mode} swfDepth={swf_d} chars={len(chars)}")
            for ci, ch in enumerate(chars):
                lib_id = ch.get("libraryId")
                ref_type = id_to_lib.get(lib_id, {}).get("type", "?")
                print(f"    Char[{ci}] lib_id={lib_id} type={ref_type} sf={ch.get('startFrame')} ef={ch.get('endFrame')}")
        count += 1
        if count >= 3: break


if __name__ == '__main__':
    main()
