"""
Find all frame labels in the black_mage main sprite (cid=873 in RT).
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

def get_sprite_data(data, target_cid):
    off = skip_hdr(data)
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        d=data[off:off+ln]; off+=ln
        if tt==39 and len(d)>=4:
            if struct.unpack_from('<H',d,0)[0] == target_cid:
                return d[4:]
        if tt==0: break
    return None

def get_labels(spr_bytes):
    labels = []
    off = 0
    while off < len(spr_bytes):
        if off+2 > len(spr_bytes): break
        hdr=struct.unpack_from('<H',spr_bytes,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',spr_bytes,off)[0]; off+=4
        d=spr_bytes[off:off+ln]; off+=ln
        if tt==43:
            null = d.index(b'\x00') if b'\x00' in d else len(d)
            labels.append(d[:null].decode('utf-8','r'))
        if tt==0: break
    return labels

def get_depth1_placed_per_label(spr_bytes, cid_to_name):
    """For each frame label, record what cid is at depth=1 (the stance)."""
    labels_depth1 = {}
    depth_state = {}
    current_label = None
    off = 0
    while off < len(spr_bytes):
        if off+2 > len(spr_bytes): break
        hdr=struct.unpack_from('<H',spr_bytes,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',spr_bytes,off)[0]; off+=4
        d=spr_bytes[off:off+ln]; off+=ln
        if tt==43:
            null = d.index(b'\x00') if b'\x00' in d else len(d)
            current_label = d[:null].decode('utf-8','r')
        elif tt==70 and len(d)>=4:
            flags1=d[0]; flags2=d[1] if len(d)>1 else 0
            has_char=bool(flags1&0x02); has_move=bool(flags1&0x01)
            depth=struct.unpack_from('<H',d,2)[0]
            cid=struct.unpack_from('<H',d,4)[0] if (has_char and len(d)>=6) else None
            if cid: depth_state[depth] = cid
            elif not has_move: depth_state.pop(depth, None)
        elif tt==26 and len(d)>=3:
            flags=d[0]; has_char=bool(flags&0x02); has_move=bool(flags&0x01)
            depth=struct.unpack_from('<H',d,1)[0]
            cid=struct.unpack_from('<H',d,3)[0] if (has_char and len(d)>=5) else None
            if cid: depth_state[depth] = cid
            elif not has_move: depth_state.pop(depth, None)
        elif tt==28 and len(d)>=2:
            depth_state.pop(struct.unpack_from('<H',d,0)[0], None)
        elif tt==1:  # ShowFrame
            if current_label:
                labels_depth1[current_label] = depth_state.get(1)  # what's at depth 1
        if tt==0: break
    return labels_depth1

for lbl, path, main_cid in [('OG', OG_PATH, 1556), ('RT', RT_PATH, 873)]:
    data = read_swf(path)
    off = skip_hdr(data)
    sym = {}
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
    cid_to_name = {v:k for k,v in sym.items()}
    
    spr = get_sprite_data(data, main_cid)
    if not spr:
        print(f"[{lbl}] main sprite cid={main_cid} not found!")
        continue
    
    all_labels = get_labels(spr)
    print(f"\n[{lbl}] main sprite cid={main_cid}, total labels: {len(all_labels)}")
    print(f"  First 10 labels: {all_labels[:10]}")
    print(f"  'dair' in labels: {'dair' in all_labels}")
    
    d1 = get_depth1_placed_per_label(spr, cid_to_name)
    if 'dair' in d1:
        d1_cid = d1['dair']
        d1_name = cid_to_name.get(d1_cid, '<anon>') if d1_cid else 'none'
        print(f"  At 'dair' label, depth=1 cid={d1_cid} [{d1_name}]")
    else:
        print(f"  'dair' NOT found as frame label!")
        # Show what labels look like for attack frames
        attack_labels = [l for l in all_labels if 'air' in l.lower() or 'atk' in l.lower() or 'attack' in l.lower()]
        print(f"  Air/attack labels: {attack_labels[:10]}")
