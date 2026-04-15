"""Check text library entry in N2D for the Falcon's Crest text."""
import zipfile, msgpack, json

with zipfile.ZipFile('test_swfs/lloyd.n2d') as zf:
    with zf.open('project.msgpack') as f:
        project = msgpack.unpack(f, raw=False)

for lib in project.get('libraries', []):
    if isinstance(lib, dict) and lib.get('type') == 'text':
        # Print all text entries 
        print(f"\n=== Text lib id={lib.get('id')} swfCharId={lib.get('swfCharId')} name={lib.get('name')} ===")
        for k, v in sorted(lib.items()):
            if k in ('rawTagBody', 'buffer'):
                print(f"  {k}: <{len(str(v))} chars>")
            else:
                print(f"  {k}: {v}")
