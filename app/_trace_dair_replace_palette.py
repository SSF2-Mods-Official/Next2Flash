"""
Trace all bitmaps visited by replacePalette for DAir_73 (Sprite 650 in RT).
recursion=2: visits depths of DAir_73, then their children, then one more level.
"""
import struct, zlib

RT=r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'
with open(RT,'rb') as f: raw=f.read()
if raw[:3]==b'CWS': raw=raw[:8]+zlib.decompress(raw[8:])
pos=8; nb=(raw[pos]>>3)&0x1f; pos+=(5+nb*4+7)//8+4

# Parse all tags
tags = {}  # charID -> (tagType, payload)
while pos<len(raw)-1:
    hdr=struct.unpack_from('<H',raw,pos)[0]; tt=hdr>>6; sl=hdr&0x3f; pos+=2
    if sl==0x3f: l=struct.unpack_from('<I',raw,pos)[0]; pos+=4
    else: l=sl
    pay=raw[pos:pos+l]
    if tt==0: break
    if tt in (36, 20, 39, 32, 26, 70):  # LL2, LL, Sprite, DS3, PO2, PO3
        if l>=2:
            cid=struct.unpack_from('<H',pay)[0]
            tags[cid]=(tt,pay)
    pos+=l

def parse_sprite_frame1(cid):
    """Parse the first frame of a DefineSprite, returning list of (depth, charID, is_bitmap)."""
    if cid not in tags: return []
    tt, pay = tags[cid]
    if tt != 39: return []
    # Parse DefineSprite: charID(2) + frameCount(2) + [frame tags]
    pos = 4
    children = {}  # depth -> (charID, has_image)
    while pos < len(pay)-1:
        hdr=struct.unpack_from('<H',pay,pos)[0]; st=hdr>>6; sl=hdr&0x3f; pos+=2
        if sl==0x3f: sl2=struct.unpack_from('<I',pay,pos)[0]; pos+=4
        else: sl2=sl
        spay=pay[pos:pos+sl2]
        if st==0: break  # End
        if st==1: break  # ShowFrame - end of frame 1
        if st==26 and sl2>=3:  # PlaceObject2
            flags=spay[0]; depth=struct.unpack_from('<H',spay,1)[0]
            has_char=(flags>>1)&1; has_id=(flags>>2)&1
            if has_char or has_id:
                ci=struct.unpack_from('<H',spay,3)[0] if len(spay)>=5 else 0
                children[depth]=(ci,True)
        elif st==70 and sl2>=4:  # PlaceObject3
            flags=struct.unpack_from('<H',spay)[0]; depth=struct.unpack_from('<H',spay,2)[0]
            has_char=(flags>>1)&1
            ptr=4
            if has_char and sl2>=6: ci=struct.unpack_from('<H',spay,ptr)[0]; ptr+=2; children[depth]=(ci,True)
        pos+=sl2
    return [(d,cid,tags.get(cid,(0,b''))[0] in (36,20)) for d,(cid,_) in sorted(children.items())]

def trace_replace_palette(sprite_cid, recursion, level=0, visited=None):
    if visited is None: visited=set()
    if sprite_cid in visited: return
    visited.add(sprite_cid)
    children = parse_sprite_frame1(sprite_cid)
    indent="  "*level
    for depth, child_cid, is_bitmap in children:
        if is_bitmap:
            tt, pay = tags.get(child_cid, (0,b''))
            if tt==36 and len(pay)>=7:
                fmt=pay[2]; w=struct.unpack_from('<H',pay,3)[0]; h=struct.unpack_from('<H',pay,5)[0]
                try:
                    dec=zlib.decompress(pay[7:]); valid=(len(dec)==w*h*4)
                except: dec=b''; valid=False
                print(f"{indent}BITMAP depth={depth} charID={child_cid} {w}x{h} valid={valid}")
        else:
            tt = tags.get(child_cid, (0,))[0]
            print(f"{indent}Sprite depth={depth} charID={child_cid} tag={tt} recur={recursion>0}")
            if recursion>0 and tt==39:
                trace_replace_palette(child_cid, recursion-1, level+1, visited)

print("=== replacePalette traversal of DAir_73 (Sprite 1471) recursion=2 ===")
trace_replace_palette(1471, 2)
