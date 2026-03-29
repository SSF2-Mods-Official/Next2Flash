import json, zipfile

with zipfile.ZipFile('converted/gameandwatch_cli.n2d') as zf:
    data = json.loads(zf.read('project.json'))

has_cid = sum(1 for lib in data['libraries'] if lib.get('swfCharId') is not None)
total = len(data['libraries'])
print(f'Libraries with swfCharId: {has_cid} / {total}')

orig_cids = set()
for lib in data['libraries']:
    c = lib.get('swfCharId')
    if c is not None:
        orig_cids.add(c)
print(f'Unique original charIDs: {len(orig_cids)}')
print(f'Range: {min(orig_cids)} to {max(orig_cids)}')
# Gaps?
expected = set(range(min(orig_cids), max(orig_cids) + 1))
missing = expected - orig_cids
print(f'Missing from range: {len(missing)} IDs')
if missing:
    for m in sorted(missing)[:30]:
        print(f'  original charID {m} has no library entry')

no_cid = [lib for lib in data['libraries'] if lib.get('swfCharId') is None]
print(f'\nLibraries WITHOUT swfCharId: {len(no_cid)}')
for lib in no_cid[:15]:
    print(f"  id={lib['id']} name={lib.get('name','?')} type={lib.get('type')}")
