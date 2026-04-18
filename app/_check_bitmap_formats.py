"""
Check LL2 format (format 3 palette vs format 5 ARGB) for dair bitmaps in OG and RT.
Also check ALL LL2 bitmaps to see if OG uses format 3 and RT converts to format 5.
"""
import struct, zlib
from collections import Counter

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

def get_sym(data):
    off = skip_hdr(data); sym = {}
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        d=data[off:off+ln]; off+=ln
        if tt==76:
            num=struct.unpack_from('<H',d,0)[0]; o=2
            for _ in range(num):
                c=struct.unpack_from('<H',d,o)[0]; o+=2
                ne=d.index(b'\x00',o); sym[d[o:ne].decode('utf-8','r')]=c; o=ne+1
        if tt==0: break
    return sym

for label, path in [('OG', OG_PATH), ('RT', RT_PATH)]:
    data = read_swf(path)
    sym = get_sym(data)
    cid_to_name = {v:k for k,v in sym.items()}
    
    # Count formats for ALL LL2 bitmaps
    format_counts = Counter()
    dair_formats = {}
    
    off = skip_hdr(data)
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        d=data[off:off+ln]; off+=ln
        if tt==36 and len(d)>=8:
            cid=struct.unpack_from('<H',d,0)[0]
            fmt=d[2]
            w=struct.unpack_from('<H',d,3)[0]
            h=struct.unpack_from('<H',d,5)[0]
            format_counts[fmt] += 1
            nm=cid_to_name.get(cid,'')
            if 'dair' in nm.lower() or 'scythe' in nm.lower():
                dair_formats[cid] = (fmt, w, h, nm)
        if tt==0: break
    
    print(f"\n[{label}] LL2 format distribution:")
    for fmt, count in sorted(format_counts.items()):
        fmt_names = {3: 'format-3 (palette/8-bit)', 5: 'format-5 (32-bit ARGB)'}
        print(f"  Format {fmt} ({fmt_names.get(fmt, 'unknown')}): {count} bitmaps")
    
    print(f"\n[{label}] DAir/Scythe bitmap formats:")
    for cid in sorted(dair_formats.keys()):
        fmt, w, h, nm = dair_formats[cid]
        print(f"  cid={cid} [{nm}]: format={fmt} ({w}x{h})")
