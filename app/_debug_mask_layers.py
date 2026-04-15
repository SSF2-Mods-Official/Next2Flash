"""Debug mask layer modes in the N2D for sprites that had masks in the original SWF."""
import msgpack, zipfile

z = zipfile.ZipFile('test_swfs/lloyd.n2d')
d = msgpack.unpackb(z.read('project.msgpack'), raw=False)
libs = d['libraries']

# From earlier analysis: original SWF sprite CID 308 had masks
# Find the container lib entry corresponding to original CID 308
for lib in libs:
    if lib.get('type') != 'container':
        continue
    cid = lib.get('swfCharId')
    if cid not in (308, 1649):
        continue
    
    print(f"\n=== Container id={lib['id']} swfCharId={cid} name={lib.get('name','')} ===")
    layers = lib.get('layers', [])
    print(f"  {len(layers)} layers")
    for i, layer in enumerate(layers):
        mode = layer.get('mode', 0)
        mode_names = {0: 'NORMAL', 1: 'MASK', 2: 'MASK_IN', 3: 'GUIDE'}
        depth = layer.get('swfDepth', '?')
        mask_id = layer.get('maskLayerId', None)
        name = layer.get('name', '')
        disable = layer.get('disable', False)
        chars = layer.get('characters', [])
        char_ids = [c.get('libraryId') for c in chars]
        
        print(f"  Layer {i}: mode={mode}({mode_names.get(mode,'?')}) "
              f"swfDepth={depth} maskLayerId={mask_id} "
              f"disable={disable} name='{name}' "
              f"chars={char_ids}")
        
        # Also check clipDepth on characters
        for c in chars:
            cd = c.get('clipDepth', None)
            sf = c.get('startFrame', 0)
            ef = c.get('endFrame', 0)
            if cd:
                print(f"    char libraryId={c.get('libraryId')} clipDepth={cd} frames={sf}-{ef}")
