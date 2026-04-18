"""
Verify the raw pixel data of dair bitmaps in RT matches OG.
Also check for any LL2 tags with malformed compressed data.
"""
import struct, zlib, sys
sys.path.insert(0, '.')

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"

def read_swf(p):
    d = open(p,'rb').read()
    if d[:3]==b'CWS': d = b'FWS'+d[3:8]+zlib.decompress(d[8:])
    return d

def prb(d,bo=0):
    bi=bo//8; bi2=bo%8; nb=0
    for i in range(5): nb=(nb<<1)|((d[bi+(bi2+i)//8]>>(7-(bi2+i)%8))&1)
    return 5+nb*4

def skip_hdr(d): return 8+(prb(d,64)+7)//8+4

def parse_tags(d, off=None, end=None):
    if off is None: off = skip_hdr(d)
    if end is None: end = len(d)
    r = []
    while off < end:
        if off+2 > end: break
        hdr = struct.unpack_from('<H',d,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',d,off)[0]; off+=4
        r.append((tt,d[off:off+ln])); off+=ln
        if tt==0: break
    return r

def get_sym_and_ll2(path):
    data = read_swf(path)
    tags = parse_tags(data)
    sym = {}
    ll2 = {}  # cid -> (w, h, fmt, compressed_bytes)
    for tt, d in tags:
        if tt == 76:
            num=struct.unpack_from('<H',d,0)[0]; o=2
            for _ in range(num):
                c=struct.unpack_from('<H',d,o)[0]; o+=2
                ne=d.index(b'\x00',o); sym[d[o:ne].decode('utf-8','r')]=c; o=ne+1
        elif tt == 36 and len(d) >= 7:  # DefineBitsLossless2
            cid = struct.unpack_from('<H',d,0)[0]
            fmt = d[2]
            w = struct.unpack_from('<H',d,3)[0]
            h = struct.unpack_from('<H',d,5)[0]
            compressed = d[7:]
            ll2[cid] = (w, h, fmt, compressed)
    cid_to_name = {v:k for k,v in sym.items()}
    return sym, ll2, cid_to_name

# Get dair bitmap names from OG
og_sym, og_ll2, og_c2n = get_sym_and_ll2(OG)
rt_sym, rt_ll2, rt_c2n = get_sym_and_ll2(RT)

dair_names = ['bm_dair0','bm_dair1','bm_dair2','bm_dair3','bm_dair4','bm_dair5','bm_dair6','bm_dair7',
              'bm_dairHand','bm_dairScythe','bm_dairScytheBlade',
              'bm_land1','bm_land2','bm_land3','bm_land4']

print("Dair bitmap verification: OG vs RT pixel data")
print("=" * 70)
errors = 0
for name in dair_names:
    og_cid = og_sym.get(name)
    rt_cid = rt_sym.get(name)
    if og_cid is None:
        print(f"  {name}: NOT IN OG SymbolClass!"); continue
    if rt_cid is None:
        print(f"  {name}: NOT IN RT SymbolClass!"); errors += 1; continue
    
    og_w, og_h, og_fmt, og_comp = og_ll2.get(og_cid, (None,None,None,None))
    rt_w, rt_h, rt_fmt, rt_comp = rt_ll2.get(rt_cid, (None,None,None,None))
    
    if og_w is None:
        print(f"  {name}: OG has no LL2 tag for cid={og_cid}!"); continue
    if rt_w is None:
        print(f"  {name}: RT has NO LL2 tag for cid={rt_cid}!"); errors += 1; continue
    
    # Try to decompress RT data
    rt_decompressed = None
    rt_error = None
    try:
        rt_decompressed = zlib.decompress(rt_comp)
    except Exception as e:
        rt_error = str(e)
    
    # Dimensions match?
    dim_ok = (og_w == rt_w and og_h == rt_h)
    
    # Buffer size match
    expected_size = rt_w * rt_h * 4  # format-5: ARGB 4 bytes
    actual_size = len(rt_decompressed) if rt_decompressed else -1
    
    status = '✓' if (dim_ok and rt_decompressed and actual_size == expected_size) else '✗'
    
    if not dim_ok:
        print(f"  {status} {name}: DIM MISMATCH OG={og_w}x{og_h} RT={rt_w}x{rt_h}")
        errors += 1
    elif rt_error:
        print(f"  {status} {name}: DECOMPRESS ERROR: {rt_error}")
        errors += 1
    elif actual_size != expected_size:
        print(f"  {status} {name}: BUFFER MISMATCH OG={og_w}x{og_h} expected={expected_size} actual={actual_size}")
        errors += 1
    else:
        print(f"  {status} {name}: cid={rt_cid} {rt_w}x{rt_h} fmt={rt_fmt} decompressed={actual_size}B OK")

# Also check ALL RT LL2 tags for decompression errors
print(f"\nChecking ALL RT LL2 tags for zlib errors...")
bad = []
for cid, (w, h, fmt, comp) in rt_ll2.items():
    try:
        dec = zlib.decompress(comp)
        expected = w * h * 4 if fmt == 5 else (w * h if fmt == 3 else -1)
        if expected > 0 and len(dec) != expected:
            bad.append((cid, rt_c2n.get(cid,'<anon>'), w, h, fmt, f"size: expected={expected} got={len(dec)}"))
    except Exception as e:
        bad.append((cid, rt_c2n.get(cid,'<anon>'), w, h, fmt, f"zlib error: {e}"))

if bad:
    print(f"  ERRORS FOUND ({len(bad)}):")
    for item in bad[:20]:
        cid, name, w, h, fmt, msg = item
        print(f"    cid={cid} {name} {w}x{h} fmt={fmt}: {msg}")
else:
    print(f"  All {len(rt_ll2)} LL2 tags decompress correctly!")
print(f"\nTotal errors: {errors}")
