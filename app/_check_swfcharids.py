import msgpack, zipfile, io
from collections import Counter

with open('converted/blackmage/project.n2d','rb') as f: raw=f.read()
with zipfile.ZipFile(io.BytesIO(raw)) as zf:
    doc = msgpack.unpackb(zf.read('project.msgpack'), raw=False)
libs = doc.get('libraries', [])
non_folder = [l for l in libs if l.get('type') != 'folder' and l.get('id',0) != 0]
swf_ids = [l.get('swfCharId') for l in non_folder if l.get('swfCharId')]
print(f'Total non-folder libs: {len(non_folder)}')
print(f'Libs with swfCharId: {len(swf_ids)}')
print(f'Max swfCharId: {max(swf_ids) if swf_ids else 0}')
print(f'Min swfCharId: {min(swf_ids) if swf_ids else 0}')
cnt = Counter(swf_ids)
dupes = [(cid, c) for cid, c in cnt.items() if c > 1]
print(f'Duplicate swfCharIds: {len(dupes)}')
if dupes:
    for cid, c in dupes[:5]:
        print(f'  charID={cid} count={c}')
no_swf = [l for l in non_folder if not l.get('swfCharId')]
print(f'Libs without swfCharId: {len(no_swf)}')
for l in no_swf[:5]:
    lid = l.get('id')
    ltype = l.get('type')
    lname = l.get('name')
    print(f'  id={lid} type={ltype} name={lname}')
