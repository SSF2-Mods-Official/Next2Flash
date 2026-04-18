"""Parse SymbolClass tag in both OG and RT, verify dair bitmap mappings."""
import struct, zlib

RT = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'
OG = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'

DAIR_CIDS = {994, 995, 996, 997, 998, 999, 1000, 1001, 1002, 1003, 1004}

def parse_swf_symbolclass(path, label):
    with open(path, 'rb') as f:
        raw = f.read()
    if raw[:3] == b'CWS':
        raw = raw[:8] + zlib.decompress(raw[8:])
    pos = 8
    nb = (raw[pos] >> 3) & 0x1f
    pos += (5 + nb * 4 + 7) // 8 + 4

    while pos < len(raw) - 1:
        hdr = struct.unpack_from('<H', raw, pos)[0]
        tt = hdr >> 6; sl = hdr & 0x3f; pos += 2
        if sl == 0x3f:
            l = struct.unpack_from('<I', raw, pos)[0]; pos += 4
        else:
            l = sl
        pay = raw[pos:pos+l]
        if tt == 0: break
        if tt == 76:  # SymbolClass
            count = struct.unpack_from('<H', pay)[0]
            sc_pos = 2
            print(f"\n=== {label}: SymbolClass ({count} entries) ===")
            dair_entries = {}
            for _ in range(count):
                cid = struct.unpack_from('<H', pay, sc_pos)[0]; sc_pos += 2
                end = pay.index(b'\x00', sc_pos)
                name = pay[sc_pos:end].decode('utf-8', errors='replace')
                sc_pos = end + 1
                if cid in DAIR_CIDS or 'dair' in name.lower() or 'hand' in name.lower():
                    dair_entries[cid] = name
                    print(f"  charID={cid} -> '{name}'")
            print(f"  Total matching: {len(dair_entries)}")
        pos += l

parse_swf_symbolclass(RT, "RT")
parse_swf_symbolclass(OG, "OG")

# Also: compare raw SymbolClass bytes
print("\n\n=== Raw SymbolClass comparison ===")
for path, label in [(RT, "RT"), (OG, "OG")]:
    with open(path, 'rb') as f:
        raw = f.read()
    if raw[:3] == b'CWS':
        raw = raw[:8] + zlib.decompress(raw[8:])
    pos = 8
    nb = (raw[pos] >> 3) & 0x1f
    pos += (5 + nb * 4 + 7) // 8 + 4
    while pos < len(raw) - 1:
        hdr = struct.unpack_from('<H', raw, pos)[0]
        tt = hdr >> 6; sl = hdr & 0x3f; pos += 2
        if sl == 0x3f:
            l = struct.unpack_from('<I', raw, pos)[0]; pos += 4
        else:
            l = sl
        pay = raw[pos:pos+l]
        if tt == 0: break
        if tt == 76:
            print(f"{label}: SymbolClass len={l}, first 30 bytes: {pay[:30].hex()}")
        pos += l
