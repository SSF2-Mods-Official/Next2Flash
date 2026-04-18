import msgpack, struct, zlib, sys, zipfile, io

with open('converted/blackmage/project.n2d','rb') as f:
    raw = f.read()
with zipfile.ZipFile(io.BytesIO(raw)) as zf:
    doc = msgpack.unpackb(zf.read('project.msgpack'), raw=False)
libs = doc.get('library', [])

# Find dair bitmaps
dair_libs = [l for l in libs if 'dair' in l.get('name','').lower() and l.get('type')=='bitmap']
print('=== Dair bitmap libs ===')
for l in dair_libs:
    print(f"  id={l['id']} name={l.get('name')} symbol={l.get('symbol')} w={l.get('width')} h={l.get('height')}")

# ALL bitmaps with symbol set
with_sym = [l for l in libs if l.get('type')=='bitmap' and l.get('symbol')]
print(f'\n=== ALL bitmaps with symbol ({len(with_sym)} total) ===')
for l in with_sym[:10]:
    print(f"  id={l['id']} name={l.get('name')} symbol={l.get('symbol')}")

# Check RT SWF SymbolClass for LL2 bitmaps
RT = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'
with open(RT, 'rb') as f:
    raw = f.read()
if raw[:3] == b'CWS':
    raw = raw[:8] + zlib.decompress(raw[8:])
pos = 8
nb = (raw[pos] >> 3) & 0x1f
pos += (5 + nb * 4 + 7) // 8 + 4
ll2_ids = set()
sc_entries = []
while pos < len(raw)-1:
    hdr = struct.unpack_from('<H', raw, pos)[0]
    tt = hdr >> 6
    sl = hdr & 0x3f
    pos += 2
    if sl == 0x3f:
        l = struct.unpack_from('<I', raw, pos)[0]
        pos += 4
    else:
        l = sl
    pay = raw[pos:pos+l]
    if tt == 0:
        break
    if tt == 36 and l >= 7:
        ll2_ids.add(struct.unpack_from('<H', pay)[0])
    if tt == 76 and l >= 2:  # SymbolClass tag
        n = struct.unpack_from('<H', pay)[0]
        p = 2
        for _ in range(n):
            cid = struct.unpack_from('<H', pay, p)[0]
            p += 2
            end = pay.index(0, p)
            name = pay[p:end].decode('utf-8')
            p = end + 1
            sc_entries.append((cid, name))
    pos += l

ll2_sym = [(cid, name) for cid, name in sc_entries if cid in ll2_ids]
print(f'\n=== RT SWF SymbolClass entries for LL2 bitmaps: {len(ll2_sym)} ===')
for cid, name in ll2_sym[:20]:
    print(f"  charID={cid} -> {name}")

print(f'\nTotal RT SymbolClass entries: {len(sc_entries)}')
print(f'Total RT LL2 bitmaps: {len(ll2_ids)}')
# Check specifically for charIDs 637-650
print('\nSymbolClass entries for charIDs 637-650:')
for cid, name in sc_entries:
    if 637 <= cid <= 650:
        print(f"  charID={cid} -> {name}")
