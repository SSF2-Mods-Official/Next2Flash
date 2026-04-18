"""
Reset scriptsModified in project.n2d by syncing all external .as files
back into the embedded 'source' fields in the N2D's project.msgpack.
This ensures the pipeline uses the raw DoABC passthrough instead of
recompiling from source (which produces a broken build).
"""
import sys, os, zipfile, io, struct, shutil
sys.path.insert(0, r'C:\Users\glwex\Documents\GitHub\Next2Flash\app')
import msgpack

N2D_DIR = r'C:\Users\glwex\Documents\GitHub\Next2Flash\app\converted\blackmage'
N2D_PATH = os.path.join(N2D_DIR, 'project.n2d')

print(f"Loading {N2D_PATH}...")
with open(N2D_PATH, 'rb') as f:
    raw = f.read()

with zipfile.ZipFile(io.BytesIO(raw)) as zf:
    names = zf.namelist()
    print(f"ZIP contents: {names}")
    if 'project.msgpack' in names:
        data = msgpack.unpackb(zf.read('project.msgpack'), raw=False)
        fmt = 'msgpack'
    else:
        import json
        data = json.loads(zf.read('project.json'))
        fmt = 'json'

scripts = data.get('scripts', [])
print(f"Total scripts: {len(scripts)}")

synced = 0
for script in scripts:
    ext = script.get('externalFile', '')
    if not ext:
        continue
    ext_path = os.path.join(N2D_DIR, ext)
    if not os.path.isfile(ext_path):
        continue
    with open(ext_path, 'r', encoding='utf-8') as f:
        new_source = f.read()
    old_source = script.get('source', '')
    if new_source != old_source:
        print(f"  Syncing: {ext}")
        script['source'] = new_source
        synced += 1

print(f"Synced {synced} scripts")

if synced > 0:
    # Backup original
    backup = N2D_PATH + '.bak'
    if not os.path.exists(backup):
        shutil.copy2(N2D_PATH, backup)
        print(f"Backed up to {backup}")

    # Rebuild ZIP
    buf = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(raw), 'r') as zf_in:
        with zipfile.ZipFile(buf, 'w', compression=zipfile.ZIP_DEFLATED) as zf_out:
            for name in zf_in.namelist():
                if name == 'project.msgpack' and fmt == 'msgpack':
                    zf_out.writestr(name, msgpack.packb(data, use_bin_type=True))
                elif name == 'project.json' and fmt == 'json':
                    import json
                    zf_out.writestr(name, json.dumps(data, ensure_ascii=False))
                else:
                    zf_out.writestr(name, zf_in.read(name))

    with open(N2D_PATH, 'wb') as f:
        f.write(buf.getvalue())
    print(f"Written: {N2D_PATH} ({len(buf.getvalue())} bytes)")
else:
    print("Nothing to sync — N2D already matches external files. scriptsModified should be False.")
    # Verify
    data2 = dict(data)
    sm = data2.get('scriptsModified', False)
    print(f"scriptsModified in loaded data: {sm}")
