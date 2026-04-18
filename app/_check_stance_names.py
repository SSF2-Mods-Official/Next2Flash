"""
Extract EXACT instance names from PO2/PO3 tags in the black_mage timeline for
the 'a_air_down' label. Specifically: which depth has instance name 'stance'?
"""
import struct, zlib
from io import BytesIO

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

def get_sprite_bytes(data, target_cid):
    off = skip_hdr(data)
    while off < len(data):
        hdr=struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        d=data[off:off+ln]; off+=ln
        if tt==39 and len(d)>=4 and struct.unpack_from('<H',d,0)[0]==target_cid:
            return d[4:]
        if tt==0: break
    return None

def get_sym(data):
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
    return sym

def parse_po2_name(d):
    """Parse PO2 tag data to extract instance name if HasName bit is set."""
    if len(d) < 2: return None, None, None
    flags = d[0]
    has_char = bool(flags & 0x02)
    has_move = bool(flags & 0x01)
    has_matrix = bool(flags & 0x04)
    has_cxform = bool(flags & 0x08)
    has_ratio = bool(flags & 0x10)
    has_name = bool(flags & 0x20)
    depth = struct.unpack_from('<H', d, 1)[0]
    off = 3
    cid = None
    if has_char and off+2 <= len(d):
        cid = struct.unpack_from('<H', d, off)[0]; off += 2
    # Skip matrix (SWF MATRIX is variable-length, can't skip easily without parsing)
    # Just return flags, depth, cid and whether has_name is set
    return depth, cid, has_name, has_move

def parse_po3_name(d):
    """Parse PO3 tag data to extract instance name (more complex due to extra flags)."""
    if len(d) < 4: return None, None, None, None
    flags1 = d[0]; flags2 = d[1]
    has_char = bool(flags1 & 0x02)
    has_move = bool(flags1 & 0x01)
    has_name = bool(flags2 & 0x02)
    depth = struct.unpack_from('<H', d, 2)[0]
    cid = None
    if has_char and len(d) >= 6:
        cid = struct.unpack_from('<H', d, 4)[0]
    return depth, cid, has_name, has_move

for label, path, main_cid in [('OG', OG_PATH, 1556), ('RT', RT_PATH, 873)]:
    data = read_swf(path)
    sym = get_sym(data)
    cid_to_name = {v:k for k,v in sym.items()}
    
    spr = get_sprite_bytes(data, main_cid)
    if not spr: continue
    
    # Walk through and find tags near 'a_air_down' label
    # Track ALL PO2/PO3 tags that place something AT THE TIME of 'a_air_down' label
    off = 0
    in_aairdown = False
    tags_before_sf = []
    current_label = None
    
    while off < len(spr):
        if off+2 > len(spr): break
        hdr=struct.unpack_from('<H',spr,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',spr,off)[0]; off+=4
        d=spr[off:off+ln]; off+=ln
        
        if tt==43:
            null = d.index(b'\x00') if b'\x00' in d else len(d)
            current_label = d[:null].decode('utf-8','r')
            if current_label == 'a_air_down':
                tags_before_sf = []  # reset
                in_aairdown = True
            else:
                in_aairdown = False
        elif in_aairdown and tt in (26, 70):
            tags_before_sf.append((tt, d))
        elif in_aairdown and tt==1:
            # ShowFrame - stop collecting
            break
        if tt==0: break
    
    print(f"\n[{label}] Tags in 'a_air_down' frame before ShowFrame ({len(tags_before_sf)} tags):")
    for tt, d in tags_before_sf:
        if tt == 26:
            depth, cid, has_name, has_move = parse_po2_name(d)
            nm = cid_to_name.get(cid, '<anon>') if cid else ''
            print(f"  PO2 depth={depth} cid={cid}[{nm}] has_name={has_name} has_move={has_move}")
        elif tt == 70:
            depth, cid, has_name, has_move = parse_po3_name(d)
            nm = cid_to_name.get(cid, '<anon>') if cid else ''
            has_img = bool(d[1] & 0x10) if len(d)>1 else False
            print(f"  PO3 depth={depth} cid={cid}[{nm}] has_name={has_name} has_move={has_move} has_img={has_img}")
    
    # Also find ALL tags in the entire black_mage timeline that place the STANCE at depth=7
    # and check if they have instance names
    print(f"\n[{label}] ALL PO2/PO3 tags at depth=7 in black_mage timeline (first 10):")
    off = 0
    count = 0
    while off < len(spr) and count < 10:
        if off+2 > len(spr): break
        hdr=struct.unpack_from('<H',spr,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',spr,off)[0]; off+=4
        d=spr[off:off+ln]; off+=ln
        if tt == 26:
            depth, cid, has_name, has_move = parse_po2_name(d)
            if depth == 7 and cid:
                nm = cid_to_name.get(cid, '<anon>')
                print(f"  PO2 depth=7 cid={cid}[{nm}] has_name={has_name}")
                count += 1
        if tt==0: break
