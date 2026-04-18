"""
Find WHERE DefineShape3 cids 521 (RT) and 1006 (RT) are placed in the SWF hierarchy.
Also find WHERE DefineShape3 cids 651 (OG) and 669 (OG) are placed.

This checks if OG's shapes are INSIDE the scythe animation sprite while
RT's shapes might be placed elsewhere (and thus Flash doesn't keep BitmapData alive).
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

def find_placements_of_shape(data, shape_cids, sym_rev):
    """Find all DefineSprite/root placements of the given shape cids.
    Returns dict: shape_cid -> list of (container_cid, container_name, depth, frame_num)
    """
    results = {c: [] for c in shape_cids}
    
    def scan_timeline(body, container_cid, container_name):
        """Scan a timeline (root or sprite body) for PO2/PO3 placements of target shapes."""
        off = 0
        frame = 0
        while off < len(body):
            if off+2 > len(body): break
            hdr=struct.unpack_from('<H',body,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
            if ln==0x3F: ln=struct.unpack_from('<I',body,off)[0]; off+=4
            d=body[off:off+ln]; off+=ln
            
            if tt == 1:
                frame += 1
            elif tt == 26:  # PO2
                flags = d[0]
                has_char = bool(flags & 0x02)
                if has_char and len(d) >= 5:
                    depth = struct.unpack_from('<H',d,1)[0]
                    cid = struct.unpack_from('<H',d,3)[0]
                    if cid in shape_cids:
                        results[cid].append((container_cid, container_name, depth, frame))
            elif tt == 70:  # PO3
                if len(d) >= 4:
                    f1=d[0]; f2=d[1]; depth=struct.unpack_from('<H',d,2)[0]
                    has_char=bool(f1&0x02); has_img=bool(f2&0x10); has_cls=bool(f2&0x08)
                    off2=4
                    # If has_img and has_char (but not has_cls), no className string
                    # (based on our earlier analysis)
                    if has_char and off2+2<=len(d):
                        cid=struct.unpack_from('<H',d,off2)[0]
                        if cid in shape_cids:
                            results[cid].append((container_cid, container_name, depth, frame))
            if tt == 0: break
    
    # Scan root timeline
    off = skip_hdr(data)
    root_body = b''
    all_sprites = {}  # cid -> body bytes
    
    off = skip_hdr(data)
    root_tags = []
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off2=off+2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off2)[0]; off2+=4
        d=data[off2:off2+ln]
        root_tags.append((tt, d))
        off = off2+ln
        if tt==39 and len(d)>=4:
            spr_cid=struct.unpack_from('<H',d,0)[0]
            all_sprites[spr_cid] = d[4:]
        if tt==0: break
    
    # Build root body
    root_body = b''.join(struct.pack('<H', (tt<<6)|(min(len(d),0x3F))) + 
                         (struct.pack('<I',len(d)) if len(d)>=0x3f else b'') + d 
                         for tt,d in root_tags)
    
    # Scan root
    for tt, d in root_tags:
        if tt == 26:
            flags=d[0]; has_char=bool(flags&0x02)
            if has_char and len(d)>=5:
                depth=struct.unpack_from('<H',d,1)[0]; cid=struct.unpack_from('<H',d,3)[0]
                if cid in shape_cids: results[cid].append((0, 'ROOT', depth, -1))
        elif tt == 70:
            if len(d)>=4:
                f1=d[0]; f2=d[1]; depth=struct.unpack_from('<H',d,2)[0]
                has_char=bool(f1&0x02); has_img=bool(f2&0x10)
                off2=4
                if has_char and off2+2<=len(d):
                    cid=struct.unpack_from('<H',d,off2)[0]
                    if cid in shape_cids: results[cid].append((0, 'ROOT', depth, -1))
    
    # Scan all sprites
    for spr_cid, body in all_sprites.items():
        nm = sym_rev.get(spr_cid, '<anon>')
        scan_timeline(body, spr_cid, nm)
    
    return results

for label, path, shape_to_check, dair_cid in [
    ('OG', OG_PATH, [651, 669], 1471),
    ('RT', RT_PATH, [521, 1006], 650),
]:
    data = read_swf(path)
    sym = get_sym(data)
    cid_to_name = {v:k for k,v in sym.items()}
    
    print(f"\n[{label}] Finding placements of shape cids: {shape_to_check}")
    print(f"  (These are DefineShape3 wrappers for bm_dairScythe / bm_dairScytheBlade)")
    print(f"  DAir_73 cid = {dair_cid}")
    
    results = find_placements_of_shape(data, shape_to_check, cid_to_name)
    
    for cid in shape_to_check:
        bmp_nm = '<unknown>'
        for bn, bc in sym.items():
            if (label=='OG' and cid==651) or (label=='RT' and cid==521):
                bmp_nm = 'bm_dairScythe'
            elif (label=='OG' and cid==669) or (label=='RT' and cid==1006):
                bmp_nm = 'bm_dairScytheBlade'
        
        hits = results[cid]
        print(f"\n  DefineShape3 cid={cid} (for {bmp_nm}):")
        if not hits:
            print("    *** NEVER PLACED! ***")
        else:
            # Group by container
            containers = {}
            for container_cid, container_name, depth, frame in hits:
                containers.setdefault(container_cid, []).append((container_name, depth, frame))
            for ccid, placements in sorted(containers.items()):
                nm = placements[0][0]
                frames = [f for _,_,f in placements]
                depths = list(set(d for _,d,_ in placements))
                print(f"    Container cid={ccid}[{nm[:50]}] at depths={depths} frames={frames[:5]}{'...' if len(frames)>5 else ''}")
                # Check if this container is inside DAir_73
                if ccid == dair_cid:
                    print(f"    *** IN DAIR_73 DIRECTLY ***")
    
    # Also find where 1279 (OG) / 63 (RT) = scythe-wrapper sub-sprite is placed
    # We know DAir_73 in OG has sub-sprites [304, 1279, 1469, 1470]
    # and in RT has [63, 66, 639, 640]
    print(f"\n  Checking if shapes are inside DAir_73 sub-sprites:")
    dair_body_off = skip_hdr(data)
    dair_body = None
    off2 = skip_hdr(data)
    while off2 < len(data):
        hdr=struct.unpack_from('<H',data,off2)[0]; tt=hdr>>6; ln=hdr&0x3F; off2+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off2)[0]; off2+=4
        d=data[off2:off2+ln]; off2+=ln
        if tt==39 and len(d)>=4 and struct.unpack_from('<H',d,0)[0]==dair_cid:
            dair_body = d[4:]
            break
        if tt==0: break
    
    if dair_body:
        # Scan DAir_73's direct timeline
        off_d = 0; frame=0
        print(f"  Direct PO2 placements of shapes in DAir_73:")
        while off_d < len(dair_body):
            if off_d+2>len(dair_body): break
            hdr=struct.unpack_from('<H',dair_body,off_d)[0]; tt=hdr>>6; ln=hdr&0x3F; off_d+=2
            if ln==0x3F: ln=struct.unpack_from('<I',dair_body,off_d)[0]; off_d+=4
            d=dair_body[off_d:off_d+ln]; off_d+=ln
            if tt==1: frame+=1
            elif tt==26 and len(d)>=5:
                flags=d[0]; has_char=bool(flags&0x02)
                if has_char:
                    depth=struct.unpack_from('<H',d,1)[0]; cid=struct.unpack_from('<H',d,3)[0]
                    if cid in shape_to_check:
                        print(f"    Frame {frame}: PO2 cid={cid} at depth={depth}")
            if tt==0: break
