"""
Check: in OG, do bitmap cids 1002 (bm_dairScythe) and 1003 (bm_dairScytheBlade)
appear as fill references in ANY DefineShape/DefineShape3/DefineShape4 tag?

In RT, do the equivalent cids 637 (bm_dairScythe) and 638 (bm_dairScytheBlade)
appear in any shape tags?

This tests whether OG bitmaps are referenced by shapes (creating persistent BitmapData)
while RT bitmaps are ONLY referenced via PO3+HasImage (potentially causing disposal).
"""
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

def find_bitmap_in_shapes(data, target_cids):
    """Scan ALL DefineShape*/DefineMorphShape* tags for fill references to target_cids.
    Returns dict: bitmap_cid -> list of (tag_type, shape_cid) that reference it.
    """
    results = {c: [] for c in target_cids}
    off = skip_hdr(data)
    sym = get_sym(data)
    cid_to_name = {v:k for k,v in sym.items()}
    
    offset_map = {}  # will store SymbolClass info
    
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        d=data[off:off+ln]; off+=ln
        
        if tt in (2, 22, 32, 33, 46, 83, 84) and len(d) >= 2:
            # DefineShape, DefineShape2, DefineShape3, DefineText2, DefineMorphShape, DefineShape4, DefineMorphShape2
            if tt in (2, 22, 32, 83):  # shape tags
                shape_cid = struct.unpack_from('<H',d,0)[0]
                body = d[2:]  # rest of tag body
                for target_cid in target_cids:
                    cid_bytes = struct.pack('<H', target_cid)
                    if cid_bytes in body:
                        results[target_cid].append((tt, shape_cid, cid_to_name.get(shape_cid, '<anon>')))
        
        if tt == 0: break
    return results

print("=" * 70)
print("OG: Checking if bm_dairScythe (1002) and bm_dairScytheBlade (1003)")
print("    appear as fill references in any DefineShape tags")
print("=" * 70)

data_og = read_swf(OG_PATH)
sym_og = get_sym(data_og)
cid_to_og = {v:k for k,v in sym_og.items()}

results_og = find_bitmap_in_shapes(data_og, [1002, 1003])
for cid, hits in results_og.items():
    nm = cid_to_og.get(cid, '<anon>')
    print(f"\nOG cid={cid} [{nm}]:")
    if hits:
        for tt, shape_cid, shape_nm in hits:
            print(f"  Referenced in DefineShape tt={tt} cid={shape_cid} [{shape_nm[:50]}]")
    else:
        print("  *** NO DefineShape references! (Only PO3+HasImage) ***")

print("\n" + "=" * 70)
print("RT: Checking if bm_dairScythe (637) and bm_dairScytheBlade (638)")
print("    appear as fill references in any DefineShape tags")
print("=" * 70)

data_rt = read_swf(RT_PATH)
sym_rt = get_sym(data_rt)
cid_to_rt = {v:k for k,v in sym_rt.items()}

results_rt = find_bitmap_in_shapes(data_rt, [637, 638])
for cid, hits in results_rt.items():
    nm = cid_to_rt.get(cid, '<anon>')
    print(f"\nRT cid={cid} [{nm}]:")
    if hits:
        for tt, shape_cid, shape_nm in hits:
            print(f"  Referenced in DefineShape tt={tt} cid={shape_cid} [{shape_nm[:50]}]")
    else:
        print("  *** NO DefineShape references! (Only PO3+HasImage) ***")

print("\n" + "=" * 70)
print("Now checking ALL 785 LL2 bitmaps: which ones lack DefineShape references?")
print("=" * 70)

# Check all LL2 bitmaps in OG: which have shape references vs not
all_ll2_og = set()
off = skip_hdr(data_og)
while off < len(data_og):
    hdr=struct.unpack_from('<H',data_og,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
    if ln==0x3F: ln=struct.unpack_from('<I',data_og,off)[0]; off+=4
    d=data_og[off:off+ln]; off+=ln
    if tt==36 and len(d)>=2:
        all_ll2_og.add(struct.unpack_from('<H',d,0)[0])
    if tt==0: break

results_all_og = find_bitmap_in_shapes(data_og, all_ll2_og)
no_shape_og = {c for c,hits in results_all_og.items() if not hits}
has_shape_og = {c for c,hits in results_all_og.items() if hits}

print(f"\nOG: Total LL2 bitmaps = {len(all_ll2_og)}")
print(f"  With DefineShape references: {len(has_shape_og)}")
print(f"  WITHOUT DefineShape references (PO3+HasImage only): {len(no_shape_og)}")

# Check RT
all_ll2_rt = set()
off = skip_hdr(data_rt)
while off < len(data_rt):
    hdr=struct.unpack_from('<H',data_rt,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
    if ln==0x3F: ln=struct.unpack_from('<I',data_rt,off)[0]; off+=4
    d=data_rt[off:off+ln]; off+=ln
    if tt==36 and len(d)>=2:
        all_ll2_rt.add(struct.unpack_from('<H',d,0)[0])
    if tt==0: break

results_all_rt = find_bitmap_in_shapes(data_rt, all_ll2_rt)
no_shape_rt = {c for c,hits in results_all_rt.items() if not hits}
has_shape_rt = {c for c,hits in results_all_rt.items() if hits}

print(f"\nRT: Total LL2 bitmaps = {len(all_ll2_rt)}")
print(f"  With DefineShape references: {len(has_shape_rt)}")
print(f"  WITHOUT DefineShape references (PO3+HasImage only): {len(no_shape_rt)}")

# Key comparison: are the "no shape" bitmaps in OG the SAME as in RT (by name)?
og_no_shape_names = {cid_to_og.get(c,'<anon>') for c in no_shape_og}
rt_no_shape_names = {cid_to_rt.get(c,'<anon>') for c in no_shape_rt}

print(f"\nOG bitmaps without shape refs (sample): {list(og_no_shape_names)[:10]}")
print(f"RT bitmaps without shape refs (sample): {list(rt_no_shape_names)[:10]}")

bm_dair_scythe_og = sym_og.get('bm_dairScythe')
bm_dair_blade_og = sym_og.get('bm_dairScytheBlade')
bm_dair_scythe_rt = sym_rt.get('bm_dairScythe')
bm_dair_blade_rt = sym_rt.get('bm_dairScytheBlade')

print(f"\nOG bm_dairScythe (cid={bm_dair_scythe_og}) has shapes: {bm_dair_scythe_og not in no_shape_og}")
print(f"OG bm_dairScytheBlade (cid={bm_dair_blade_og}) has shapes: {bm_dair_blade_og not in no_shape_og}")
print(f"RT bm_dairScythe (cid={bm_dair_scythe_rt}) has shapes: {bm_dair_scythe_rt not in no_shape_rt}")
print(f"RT bm_dairScytheBlade (cid={bm_dair_blade_rt}) has shapes: {bm_dair_blade_rt not in no_shape_rt}")
