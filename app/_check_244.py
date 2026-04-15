"""Check how many 244x244 bitmaps exist in the N2D."""
import struct, zlib, zipfile, io, base64, msgpack

n2d_path = 'test_swfs/lloyd.n2d'
with zipfile.ZipFile(n2d_path) as zf:
    with zf.open('project.msgpack') as f:
        project = msgpack.unpack(f, raw=False)

libs = project.get('libraries', [])
count = 0
for lib in libs:
    if isinstance(lib, dict) and lib.get('type') == 'bitmap':
        if lib.get('width') == 244 and lib.get('height') == 244:
            count += 1
            cid = lib.get('swfCharId')
            tag = lib.get('rawTagType')
            print(f"  CID={cid} rawTagType={tag}")
print(f"Total 244x244 bitmaps: {count}")
