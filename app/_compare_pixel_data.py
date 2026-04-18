"""Compare LL2 pixel data for bm_dair0 between OG and RT."""
import struct, zlib

OG_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"
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

def extract_ll2(data, target_cid):
    off = skip_hdr(data)
    while off < len(data):
        hdr = struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        body = data[off:off+ln]
        if tt == 36 and len(body) >= 7:
            cid = struct.unpack_from('<H', body, 0)[0]
            if cid == target_cid:
                fmt = body[2]
                w = struct.unpack_from('<H', body, 3)[0]
                h = struct.unpack_from('<H', body, 5)[0]
                compressed = bytes(body[7:])
                return fmt, w, h, compressed
        off += ln
        if tt == 0: break
    return None

og_data = read_swf(OG_PATH)
rt_data = read_swf(RT_PATH)

# bm_dair0: OG cid=1004, RT cid=642
og_ll2 = extract_ll2(og_data, 1004)
rt_ll2 = extract_ll2(rt_data, 642)

for label, result in [("OG bm_dair0(1004)", og_ll2), ("RT bm_dair0(642)", rt_ll2)]:
    if result:
        fmt, w, h, comp = result
        try:
            decomp = zlib.decompress(comp)
            expected = w * h * 4
            print(f"{label}: fmt={fmt} {w}x{h}, compressed={len(comp)}, decompressed={len(decomp)}, expected={expected}, {'OK' if len(decomp)==expected else 'SIZE MISMATCH!'}")
            # Show first 16 bytes of decompressed (ARGB values of top-left pixels)
            print(f"  First pixel bytes (ARGB): {decomp[:16].hex()}")
        except Exception as e:
            print(f"{label}: decompress error: {e}")
    else:
        print(f"{label}: NOT FOUND")

# Also check bm_dairHand (5x5)
og_hand = extract_ll2(og_data, 1001)
rt_hand = extract_ll2(rt_data, 641)
print()
for label, result in [("OG bm_dairHand(1001)", og_hand), ("RT bm_dairHand(641)", rt_hand)]:
    if result:
        fmt, w, h, comp = result
        decomp = zlib.decompress(comp)
        print(f"{label}: fmt={fmt} {w}x{h}, compressed={len(comp)}, decompressed={len(decomp)}, expected={w*h*4}")
        print(f"  All pixels ARGB: {decomp.hex()[:200]}")
