import zipfile, msgpack

with zipfile.ZipFile('test_swfs/lloyd.n2d') as z:
    with z.open('project.msgpack') as f:
        p = msgpack.unpack(f, raw=False)

# N2D stores shapes in libraries array - each entry is a library element
# The structure might be: libraries[i] has layers/etc, and shapes are separate items
# Let's find shape entries across all libraries
all_entries = []
for lib in p.get('libraries', []):
    all_entries.append(lib)

# But shapes might be in a flat list? Check library structure
print(f"Number of libraries: {len(p.get('libraries', []))}")
print(f"First library keys: {list(p['libraries'][0].keys())}")

# Check if there's a separate shapes/symbols list
# In compile_n2d, it iterates over libraries and checks type
libs = p.get('libraries', [])
shapes = [l for l in libs if l.get('type') == 'shape' and not l.get('endRecodes')]
print(f'Total shapes: {len(shapes)}')

# Check swfCharId values
cids = [l.get('swfCharId') for l in shapes]
none_count = cids.count(None)
print(f'None swfCharId: {none_count}')
print(f'Non-None swfCharId: {len(cids) - none_count}')

# Show first 15
for s in shapes[:15]:
    print(f"  id={s.get('id')}, swfCharId={s.get('swfCharId')}, name={s.get('name','?')}, recodes_len={len(s.get('recodes',[]))}")

# Look for any with swfCharId between 100-400
print("\nShapes with swfCharId 100-400:")
for s in shapes:
    cid = s.get('swfCharId')
    if cid is not None and 100 <= cid <= 400:
        print(f"  id={s.get('id')}, swfCharId={cid}, name={s.get('name','?')}")

# Check if any N2D entries have swfCharId matching our targets
print("\nAll N2D entries (any type) with swfCharId in {183, 185, 188, 306}:")
for l in libs:
    cid = l.get('swfCharId')
    if cid in (183, 185, 188, 306):
        print(f"  id={l.get('id')}, swfCharId={cid}, type={l.get('type')}, name={l.get('name','?')}")
