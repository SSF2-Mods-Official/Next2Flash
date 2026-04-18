"""
Find DefineSprite(cid=1311) in the RT SWF root timeline.
Also check: does the OG main sprite have PO2 with 'stance' instance names?
We need to find how 'stance' is named in the main sprite.
"""
import struct, zlib, sys

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

def find_sprite_by_cid(data, target_cid):
    off = skip_hdr(data)
    idx = 0
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        d=data[off:off+ln]; off+=ln; idx+=1
        if tt==39 and len(d)>=4:
            cid = struct.unpack_from('<H',d,0)[0]
            if cid == target_cid:
                return idx, d
        if tt==0: break
    return None, None

for label, path in [('OG', OG_PATH), ('RT', RT_PATH)]:
    data = read_swf(path)
    
    # Find all root PO2s AFTER ShowFrame (these are the actual placements)
    off = skip_hdr(data)
    after_sf = False
    root_po2s = []
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        d=data[off:off+ln]; off+=ln
        if tt==1: after_sf=True
        if after_sf and tt==26 and len(d)>=5:
            has_char = bool(d[0]&0x02)
            if has_char:
                cid = struct.unpack_from('<H',d,3)[0]
                root_po2s.append(cid)
        if tt==0: break
    
    print(f"\n[{label}] Root PO2s (after ShowFrame): {root_po2s[:5]}...")
    
    # Find the main character sprite (first root placement = main sprite)
    main_cid = root_po2s[0] if root_po2s else None
    print(f"  Main cid: {main_cid}")
    
    if main_cid:
        idx, spr_d = find_sprite_by_cid(data, main_cid)
        if spr_d is not None:
            print(f"  Found DefineSprite({main_cid}) at tag index {idx}, inner bytes={len(spr_d)-4}")
            # Find "stance" label in inner tags and what's placed there
            inner = spr_d[4:]  # skip cid + frame_count
            off2 = 0
            depth_state = {}
            current_dair_snap = None
            
            while off2 < len(inner):
                if off2+2 > len(inner): break
                hdr=struct.unpack_from('<H',inner,off2)[0]; tt2=hdr>>6; ln2=hdr&0x3F; off2+=2
                if ln2==0x3F: ln2=struct.unpack_from('<I',inner,off2)[0]; off2+=4
                d2=inner[off2:off2+ln2]; off2+=ln2
                
                if tt2==43:  # FrameLabel
                    null = d2.index(b'\x00') if b'\x00' in d2 else len(d2)
                    lbl = d2[:null].decode('utf-8','r')
                    if lbl == 'dair':
                        current_dair_snap = dict(depth_state)
                elif tt2==70 and len(d2)>=4:  # PO3
                    flags1=d2[0]; flags2=d2[1] if len(d2)>1 else 0
                    has_char=bool(flags1&0x02); has_move=bool(flags1&0x01)
                    has_name=bool(flags2&0x02)
                    depth=struct.unpack_from('<H',d2,2)[0]
                    cid=struct.unpack_from('<H',d2,4)[0] if (has_char and len(d2)>=6) else None
                    if cid: depth_state[depth] = (cid, has_name, d2)
                    elif not has_move: depth_state.pop(depth, None)
                elif tt2==26 and len(d2)>=3:  # PO2
                    flags=d2[0]; has_char=bool(flags&0x02); has_move=bool(flags&0x01)
                    has_name=bool(flags&0x20)
                    depth=struct.unpack_from('<H',d2,1)[0]
                    cid=struct.unpack_from('<H',d2,3)[0] if (has_char and len(d2)>=5) else None
                    if cid: depth_state[depth] = (cid, has_name, d2)
                    elif not has_move: depth_state.pop(depth, None)
                elif tt2==28 and len(d2)>=2:  # RO2
                    depth=struct.unpack_from('<H',d2,0)[0]
                    depth_state.pop(depth, None)
                if tt2==0: break
            
            if current_dair_snap:
                print(f"  Depths at 'dair' label: {len(current_dair_snap)}")
                for dep in sorted(current_dair_snap.keys()):
                    cid, has_name, d2 = current_dair_snap[dep]
                    print(f"    depth={dep}: cid={cid} has_name={has_name}")
            else:
                print(f"  'dair' label not found in main sprite {main_cid}")
        else:
            print(f"  DefineSprite({main_cid}) NOT FOUND in root timeline!")
            
            # Check what tag type defines cid=main_cid
            off = skip_hdr(data)
            while off < len(data):
                hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
                if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
                d=data[off:off+ln]; off+=ln
                if len(d)>=2:
                    cid = struct.unpack_from('<H',d,0)[0]
                    if cid == main_cid:
                        print(f"  cid={main_cid} found as Tag type {tt}!")
                if tt==0: break
