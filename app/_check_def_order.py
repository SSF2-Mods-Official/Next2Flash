"""Check whether sprite 639 (scythe) is at root level or deferred inside another sprite."""
import sys, struct, zlib
sys.path.insert(0, '.')

RT_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"

def read_swf(p):
    d = open(p,'rb').read()
    if d[:3]==b'CWS': d = b'FWS'+d[3:8]+zlib.decompress(d[8:])
    return d

def prb(d,bo=0):
    bi=bo//8; bi2=bo%8; nb=0
    for i in range(5): nb=(nb<<1)|((d[bi+(bi2+i)//8]>>(7-(bi2+i)%8))&1)
    return 5+nb*4

def skip_hdr(d): return 8+(prb(d,64)+7)//8+4

data = read_swf(RT_PATH)
root_start = skip_hdr(data)

# Check if sprite 639 is in the root-level tag stream
target_cids = {637, 638, 639, 640, 641, 642}
found_at_root = {}

off = root_start
while off < len(data):
    if off+2 > len(data): break
    hdr = struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; hdr_sz=2; off+=2
    if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4; hdr_sz=6
    body = data[off:off+ln]
    if len(body) >= 2:
        cid = struct.unpack_from('<H', body, 0)[0]
        if cid in target_cids:
            found_at_root[cid] = (tt, off-hdr_sz)
            print(f"Root-level TT={tt} charId={cid} at byte offset {off-hdr_sz}")
    off += ln
    if tt == 0: break

print(f"\nBitmaps/sprites found at root level: {sorted(found_at_root.keys())}")
missing = target_cids - set(found_at_root.keys())
if missing:
    print(f"NOT found at root level: {sorted(missing)}")
    print("These might be nested inside another sprite body!")

# Also check ordering: bitmap defs should come BEFORE sprite defs
print(f"\nOrdering check:")
for cid in sorted(target_cids):
    if cid in found_at_root:
        tt, offset = found_at_root[cid]
        name = {637: 'bm_dairScythe', 638: 'bm_dairScytheBlade', 639: 'sprite_639', 
                640: 'sprite_640', 641: 'bm_dairHand', 642: 'bm_dair0'}.get(cid, str(cid))
        print(f"  {name} (charId={cid}, TT={tt}) at offset {offset}")
