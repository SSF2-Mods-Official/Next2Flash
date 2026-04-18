"""Read N2D msgpack and find rawTagType for charID=1001."""
import zipfile, msgpack, struct

with zipfile.ZipFile('converted/blackmage/project.n2d', 'r') as zf:
    with zf.open('project.msgpack') as f:
        raw = f.read()

print(f'Msgpack size: {len(raw):,}')
data = msgpack.unpackb(raw, raw=False, strict_map_key=False)
print(f'Top-level keys: {list(data.keys())[:10] if isinstance(data, dict) else type(data)}')

if isinstance(data, dict):
    libs = data.get('libraries', [])
    print(f'Library count: {len(libs)}')
    
    # Find library with swfCharId=1001
    bm1001 = None
    for lib in libs:
        if isinstance(lib, dict):
            if lib.get('swfCharId') == 1001:
                bm1001 = lib
                break
    
    if bm1001:
        print(f'\nFound library with swfCharId=1001:')
        for k, v in bm1001.items():
            if k == 'pixelData':
                if isinstance(v, (bytes, bytearray)):
                    print(f'  {k}: {len(v)} bytes, first_20={v[:20].hex()}')
                else:
                    print(f'  {k}: type={type(v)}, str={str(v)[:80]}')
            elif k == 'rawTagBody':
                if v:
                    vb = v if isinstance(v, (bytes, bytearray)) else str(v)
                    print(f'  {k}: len={len(vb)}, first_20={vb[:20].hex() if isinstance(vb, (bytes, bytearray)) else str(vb)[:50]}')
                else:
                    print(f'  {k}: {v}')
            else:
                print(f'  {k}: {v}')
    else:
        # Try by id
        for lib in libs[:5]:
            if isinstance(lib, dict):
                print(f'Sample lib: id={lib.get("id")}, swfCharId={lib.get("swfCharId")}, type={lib.get("type")}, rawTagType={lib.get("rawTagType")}')
