"""Check CID 164 text bounds and letterSpacing in the N2D."""
import msgpack, zipfile
z = zipfile.ZipFile('test_swfs/lloyd.n2d')
d = msgpack.unpackb(z.read('project.msgpack'), raw=False)
# Find the library key
for k in d.keys():
    if 'lib' in k.lower():
        print('Key:', k)
libs = d.get('library') or d.get('lib') or d.get('libraries') or []
if not libs:
    # Try to find it
    for k, v in d.items():
        if isinstance(v, list) and len(v) > 100:
            libs = v
            print(f'Using key: {k} ({len(v)} items)')
            break

for lib in libs:
    if lib.get('id') == 164:
        print('bounds:', lib.get('bounds'))
        print('originBounds:', lib.get('originBounds'))
        print('letterSpacing:', lib.get('letterSpacing'))
        print('text:', repr(lib.get('text')))
        print('font:', lib.get('font'))
        print('size:', lib.get('size'))
        print('autoSize:', lib.get('autoSize'))
        break
