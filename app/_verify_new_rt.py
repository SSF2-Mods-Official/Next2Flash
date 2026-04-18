import struct, zlib

RT = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'
with open(RT, 'rb') as f:
    raw = f.read()
if raw[:3] == b'CWS':
    raw = raw[:8] + zlib.decompress(raw[8:])
pos = 8
nb = (raw[pos] >> 3) & 0x1f
pos += (5 + nb * 4 + 7) // 8 + 4

ll2 = {}
sc_entries = []
ds3_cids = []
sprites = {}

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
        cid = struct.unpack_from('<H', pay)[0]
        w = struct.unpack_from('<H', pay, 3)[0]
        h = struct.unpack_from('<H', pay, 5)[0]
        ll2[cid] = (w, h)
    if tt == 32 and l >= 2:
        cid = struct.unpack_from('<H', pay)[0]
        ds3_cids.append(cid)
    if tt == 39 and l >= 4:
        cid = struct.unpack_from('<H', pay)[0]
        sprites[cid] = l
    if tt == 76 and l >= 2:
        n = struct.unpack_from('<H', pay)[0]
        p = 2
        for _ in range(n):
            cid = struct.unpack_from('<H', pay, p)[0]
            p += 2
            end = pay.index(0, p)
            name = pay[p:end].decode()
            p = end + 1
            sc_entries.append((cid, name))
    pos += l

# Check dair SymbolClass entries
print('=== NEW RT SymbolClass for dair bitmaps ===')
for cid, name in sorted(sc_entries):
    if 994 <= cid <= 1010 or 'dair' in name.lower():
        print(f'  charID={cid} -> {name}')

# Check LL2 charIDs for dair bitmaps
print()
r1001 = ll2.get(1001)
r1004 = ll2.get(1004)
r641 = ll2.get(641)
r642 = ll2.get(642)
print(f'LL2 1001 (bm_dairHand): {r1001}')
print(f'LL2 1004 (bm_dair0): {r1004}')
print(f'LL2 641 (old): {r641}')
print(f'LL2 642 (old): {r642}')

print()
print(f'Total LL2: {len(ll2)}, Total DS3: {len(ds3_cids)}, Total Sprites: {len(sprites)}')

# Check DAir_73 sprite charID (should be 1471 now matching OG)
dair73_sc = [(cid, name) for cid, name in sc_entries if 'DAir_73' in name]
print(f'DAir_73 SymbolClass: {dair73_sc}')
