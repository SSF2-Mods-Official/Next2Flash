"""
Check tag emission order for key cids in RT SWF.
Key question: are DefineShape3 wrappers (521, 1006) emitted BEFORE 
the sub-sprites (639, 640) and DAir_73 (650)?
"""
import struct, zlib

RT_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"
OG_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"

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
    
    if label == 'OG':
        key_cids = {
            1002: 'bm_dairScythe',
            1003: 'bm_dairScytheBlade', 
            651: 'DS3_for_dairScythe',
            669: 'DS3_for_blade',
            1469: 'sub_sprite_scythe_multi',
            1470: 'sub_sprite_scythe_blade',
            1471: 'DAir_73',
        }
    else:
        key_cids = {
            637: 'bm_dairScythe',
            638: 'bm_dairScytheBlade',
            521: 'DS3_for_dairScythe',
            1006: 'DS3_for_blade',
            639: 'sub_sprite_scythe_multi',
            640: 'sub_sprite_scythe_blade',
            650: 'DAir_73',
        }
    
    print(f"\n[{label}] Tag order for key cids:")
    
    # Find sequential position of each key cid
    tag_positions = {}  # cid -> (seq_index, tag_type)
    off = skip_hdr(data)
    seq = 0
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        d=data[off:off+ln]; off+=ln
        if tt in (2,22,32,33,36,39,46,83,84,20) and len(d)>=2:
            cid=struct.unpack_from('<H',d,0)[0]
            if cid in key_cids:
                tag_positions[cid] = (seq, tt)
        seq += 1
        if tt==0: break
    
    for cid in sorted(key_cids.keys()):
        pos_info = tag_positions.get(cid, ('NOT FOUND', '?'))
        nm = key_cids[cid]
        sym_nm = cid_to_name.get(cid, '<anon>')
        tt_names = {36:'LL2', 32:'DefineShape3', 39:'DefineSprite', 2:'DefineShape', 83:'DefineShape4'}
        tt_name = tt_names.get(pos_info[1], f'TT={pos_info[1]}') if len(pos_info)==2 else '?'
        print(f"  pos={pos_info[0]:4d} {tt_name:15s} cid={cid:5d}  [{sym_nm[:45] or nm}]")
    
    print()
    # Check: are shapes 521/1006 before sub-sprites 639/640?
    if label == 'RT':
        shape521 = tag_positions.get(521, (None, None))
        shape1006 = tag_positions.get(1006, (None, None))
        sub639 = tag_positions.get(639, (None, None))
        sub640 = tag_positions.get(640, (None, None))
        dair650 = tag_positions.get(650, (None, None))
        
        print(f"  DS3 521 (bm_dairScythe wrapper) at pos={shape521[0]}")
        print(f"  DS3 1006 (bm_dairBlade wrapper) at pos={shape1006[0]}")
        print(f"  SubSprite 639 (uses bm_dairScythe+Blade via PO3) at pos={sub639[0]}")
        print(f"  SubSprite 640 (uses bm_dairScytheBlade via PO3) at pos={sub640[0]}")
        print(f"  DAir_73 650 at pos={dair650[0]}")
        
        if shape521[0] and sub639[0]:
            print(f"\n  521 before 639? {shape521[0] < sub639[0]}")
        if shape1006[0] and sub639[0]:
            print(f"  1006 before 639? {shape1006[0] < sub639[0]}")
        if shape1006[0] and sub640[0]:
            print(f"  1006 before 640? {shape1006[0] < sub640[0]}")
    
    if label == 'OG':
        shape651 = tag_positions.get(651, (None, None))
        shape669 = tag_positions.get(669, (None, None))
        sub1469 = tag_positions.get(1469, (None, None))
        sub1470 = tag_positions.get(1470, (None, None))
        dair1471 = tag_positions.get(1471, (None, None))
        
        print(f"  DS3 651 (bm_dairScythe wrapper) at pos={shape651[0]}")
        print(f"  DS3 669 (bm_dairBlade wrapper) at pos={shape669[0]}")
        print(f"  SubSprite 1469 at pos={sub1469[0]}")
        print(f"  SubSprite 1470 at pos={sub1470[0]}")
        print(f"  DAir_73 1471 at pos={dair1471[0]}")
        
        if shape651[0] and sub1469[0]:
            print(f"\n  651 before 1469? {shape651[0] < sub1469[0]}")
        if shape669[0] and sub1469[0]:
            print(f"  669 before 1469? {shape669[0] < sub1469[0]}")
