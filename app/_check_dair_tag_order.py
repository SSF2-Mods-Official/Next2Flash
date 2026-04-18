"""
Check tag definition ORDER in RT SWF for dair-related cids.
A DefineBitsLossless2 must appear BEFORE any DefineSprite that uses it.
"""
import struct, zlib, sys
sys.path.insert(0, '.')

RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"
OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"

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
    idx = 0
    while off < end:
        if off+2 > end: break
        hdr = struct.unpack_from('<H',d,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',d,off)[0]; off+=4
        r.append((idx, tt, d[off:off+ln])); off+=ln; idx+=1
        if tt==0: break
    return r

def analyze_order(path, label):
    data = read_swf(path)
    tags = parse_tags(data)
    
    # Build: for each cid, record its definition index
    def_index = {}  # cid -> (index, tag_type, description)
    sym = {}
    
    for idx, tt, d in tags:
        if tt in (35, 36, 20) and len(d) >= 2:  # DefineBits, DefineBitsLossless2, DefineBitsJPEG2
            cid = struct.unpack_from('<H',d,0)[0]
            def_index[cid] = (idx, tt, 'BMP')
        elif tt == 39 and len(d) >= 4:  # DefineSprite
            cid = struct.unpack_from('<H',d,0)[0]
            def_index[cid] = (idx, tt, 'SPR')
        elif tt == 2 and len(d) >= 2:  # DefineShape
            cid = struct.unpack_from('<H',d,0)[0]
            def_index[cid] = (idx, tt, 'SHP')
        elif tt in (22, 32, 46) and len(d) >= 2:  # DefineShape2,3,4
            cid = struct.unpack_from('<H',d,0)[0]
            def_index[cid] = (idx, tt, f'SHP{tt}')
        elif tt == 76:
            num=struct.unpack_from('<H',d,0)[0]; o=2
            for _ in range(num):
                c=struct.unpack_from('<H',d,o)[0]; o+=2
                ne=d.index(b'\x00',o); sym[d[o:ne].decode('utf-8','r')]=c; o=ne+1
    
    cid_to_name = {v:k for k,v in sym.items()}
    
    # Check: for DAir_73 and its sub-sprites, do all referenced cids have earlier definition?
    # Find DAir_73 cid
    dair_cid = sym.get('blackmage_fla.DAir_73')
    
    def get_cids_in_sprite(cid, tags_list, def_idx):
        """Get all cids referenced by a DefineSprite's inner tags"""
        spr_tag = None
        for idx, tt, d in tags_list:
            if tt == 39 and len(d) >= 4:
                c = struct.unpack_from('<H',d,0)[0]
                if c == cid:
                    spr_tag = d[4:]
                    break
        if not spr_tag:
            return []
        # Parse inner tags
        referenced = []
        off = 0
        while off < len(spr_tag):
            if off+2 > len(spr_tag): break
            hdr = struct.unpack_from('<H',spr_tag,off)[0]; tt2=hdr>>6; ln2=hdr&0x3F; off+=2
            if ln2==0x3F: ln2=struct.unpack_from('<I',spr_tag,off)[0]; off+=4
            inner_d = spr_tag[off:off+ln2]; off+=ln2
            if tt2 in (26, 70) and len(inner_d)>= (5 if tt2==26 else 6):
                has_char = bool(inner_d[0] & 0x02)
                if has_char:
                    c2 = struct.unpack_from('<H',inner_d, 3 if tt2==26 else 4)[0]
                    referenced.append(c2)
            if tt2 == 0: break
        return referenced
    
    print(f"\n[{label}] Tag order check for DAir_73 (cid={dair_cid})")
    print("=" * 60)
    
    dair_def_idx = def_index.get(dair_cid, (None, None, None))[0]
    print(f"  DAir_73 defined at tag index: {dair_def_idx}")
    
    # Get all cids directly in DAir_73
    direct_refs = get_cids_in_sprite(dair_cid, tags, def_index)
    print(f"\n  Direct references in DAir_73:")
    for c in sorted(set(direct_refs)):
        c_info = def_index.get(c)
        name = cid_to_name.get(c, '<anon>')
        if c_info:
            c_def_idx, c_tt, c_type = c_info
            order_ok = c_def_idx < dair_def_idx
            flag = '✓' if order_ok else '✗ OUT-OF-ORDER!'
            print(f"    {flag} cid={c} [{name}] {c_type} defined at tag #{c_def_idx} (DAir_73 at #{dair_def_idx})")
        else:
            print(f"    ? cid={c} [{name}] NOT DEFINED!")
    
    # Also check sub-sprites of DAir_73
    for c in sorted(set(direct_refs)):
        c_info = def_index.get(c)
        if c_info and c_info[1] == 39:  # It's a sprite (DefineSprite)
            sub_refs = get_cids_in_sprite(c, tags, def_index)
            sub_def_idx = c_info[0]
            name = cid_to_name.get(c, '<anon>')
            print(f"\n  Sub-sprite cid={c} [{name}] defined at tag #{sub_def_idx}:")
            for c2 in sorted(set(sub_refs)):
                c2_info = def_index.get(c2)
                name2 = cid_to_name.get(c2, '<anon>')
                if c2_info:
                    c2_def_idx, c2_tt, c2_type = c2_info
                    order_ok = c2_def_idx < sub_def_idx
                    flag = '✓' if order_ok else '✗ OUT-OF-ORDER!'
                    print(f"    {flag} cid={c2} [{name2}] {c2_type} defined at tag #{c2_def_idx} (sub-sprite at #{sub_def_idx})")
                else:
                    print(f"    ? cid={c2} [{name2}] NOT DEFINED!")

analyze_order(OG, 'OG')
analyze_order(RT, 'RT')
