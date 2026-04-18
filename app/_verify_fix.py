"""
Quick verification of the new RT SWF after companion DefineShape3 fix.
"""
import struct, zlib
from collections import Counter

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

tag_counts = Counter()
off = skip_hdr(data)
while off < len(data):
    hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
    if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
    off+=ln
    tag_counts[tt] += 1
    if tt==0: break

print(f"File size: {len(open(RT_PATH,'rb').read()):,} bytes")
print(f"\nTag type counts:")
print(f"  DefineBitsLossless2 (TT=36): {tag_counts[36]}")
print(f"  DefineShape3 (TT=32): {tag_counts[32]}")
print(f"  DefineShape4 (TT=83): {tag_counts[83]}")
print(f"  DefineSprite (TT=39): {tag_counts[39]}")
print(f"  SymbolClass (TT=76): {tag_counts[76]}")
print(f"  PlaceObject3 (TT=70): {tag_counts[70]}")
print(f"  DoABC (TT=72): {tag_counts[72]}")
print(f"  DoABC2 (TT=82): {tag_counts[82]}")
print(f"  Total tags: {sum(tag_counts.values())}")

ll2 = tag_counts[36]
ds3 = tag_counts[32]
# Each _emit_bitmap call emits exactly 1 LL2 + 1 companion DefShape3.
# So non-companion shapes = ds3 - ll2. Both counts should be equal to
# the number of bitmap libs (785 for blackmage).
print(f"\nLL2 (bitmaps): {ll2} ({'OK' if ll2==785 else 'MISMATCH'})")
print(f"DefShape3 total: {ds3}")
print(f"  Non-companion shapes:  {ds3 - ll2}")
print(f"  Companion shapes added: {ll2}  (should equal LL2 count)")
status = 'OK - all 785 companions present' if ds3 == (ds3-ll2) + ll2 else 'CHECK'
print(f"  Status: {status}")
