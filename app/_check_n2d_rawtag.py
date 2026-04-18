import zipfile, io, json
try:
    import msgpack
    HAS_MSGPACK = True
except ImportError:
    HAS_MSGPACK = False

n2d = r'C:\Users\glwex\Documents\GitHub\Next2Flash\app\converted\blackmage\project.n2d'
with open(n2d,'rb') as f: raw = f.read()
with zipfile.ZipFile(io.BytesIO(raw)) as zf:
    names = zf.namelist()
    print("ZIP entries:", names)
    if 'project.msgpack' in names and HAS_MSGPACK:
        data = msgpack.unpackb(zf.read('project.msgpack'), raw=False)
    elif 'project.json' in names:
        data = json.loads(zf.read('project.json'))
    else:
        print("No project.json or project.msgpack found")
        raise SystemExit

libs = data.get('libraries') or data.get('library', [])
bitmap_libs = [l for l in libs if l.get('type') == 'bitmap']
print(f"Total bitmap libs: {len(bitmap_libs)}")

jpeg_libs = [l for l in bitmap_libs if l.get('rawTagType') in (6, 21, 35, 90)]
ll2_libs  = [l for l in bitmap_libs if l.get('rawTagType') == 36]
missing   = [l for l in bitmap_libs if 'rawTagType' not in l]
print(f"JPEG-family (rawTagType 6/21/35/90): {len(jpeg_libs)}")
print(f"LL2 (rawTagType 36): {len(ll2_libs)}")
print(f"Missing rawTagType field: {len(missing)}")

if jpeg_libs:
    s = jpeg_libs[0]
    print("Sample JPEG lib:", s.get('name'), "rawTagType=", s.get('rawTagType'), "swfCharId=", s.get('swfCharId'))
