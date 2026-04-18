"""Dump the complete structure of DAir_73 in the RT SWF, frame 1."""
import struct, zlib

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

data = read_swf(RT_PATH)
root_start = skip_hdr(data)

def parse_tags(data, start_off, end_off=None):
    off = start_off
    if end_off is None: end_off = len(data)
    while off < end_off:
        if off+2 > end_off: break
        hdr = struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; hdr_sz=2; off+=2
        if ln==0x3F:
            ln=struct.unpack_from('<I',data,off)[0]; off+=4; hdr_sz=6
        body = data[off:off+ln]
        yield tt, body, off-hdr_sz, ln
        off+=ln
        if tt==0: break

# Collect character types
char_types = {}
sym_class = {}
sprite_bodies = {}

for tt, body, abs_off, ln in parse_tags(data, root_start):
    if tt == 76:  # SymbolClass
        count = struct.unpack_from('<H', body, 0)[0]
        off2 = 2
        for _ in range(count):
            cid = struct.unpack_from('<H', body, off2)[0]; off2 += 2
            end_str = body.index(b'\x00', off2)
            name = body[off2:end_str].decode('utf-8', errors='replace'); off2 = end_str+1
            sym_class[name] = cid; sym_class[cid] = name
    if len(body) >= 2:
        cid = struct.unpack_from('<H', body, 0)[0]
        char_types[cid] = tt
        if tt == 39:
            sprite_bodies[cid] = body

dair73_cid = sym_class.get('blackmage_fla.DAir_73', None)
print(f"DAir_73 charId: {dair73_cid}")

if dair73_cid and dair73_cid in sprite_bodies:
    body = sprite_bodies[dair73_cid]
    # Parse the sprite body: charId(2) + frameCount(2) + sub-tags
    frame_count = struct.unpack_from('<H', body, 2)[0]
    print(f"Frame count: {frame_count}")
    
    sub_off = 4
    frame_num = 0
    print(f"\n--- FRAME 1 tags (complete) ---")
    
    while sub_off < len(body):
        if sub_off+2 > len(body): break
        shdr = struct.unpack_from('<H', body, sub_off)[0]; stt=shdr>>6; sln=shdr&0x3F; sh_sz=2; sub_off+=2
        if sln==0x3F:
            sln=struct.unpack_from('<I', body, sub_off)[0]; sub_off+=4; sh_sz=6
        sub_body = body[sub_off:sub_off+sln]
        
        if stt == 1:  # ShowFrame
            frame_num += 1
            print(f"--- ShowFrame (frame {frame_num}) ---")
            if frame_num >= 2:
                print("(stopping at frame 2)")
                break
        elif stt == 70:  # PO3
            if len(sub_body) >= 4:
                flags = struct.unpack_from('<H', sub_body, 0)[0]
                depth = struct.unpack_from('<H', sub_body, 2)[0]
                has_char = bool(flags & 0x02)
                has_name = bool(flags & 0x20)
                has_image = bool(flags & 0x0100)  # bit 8 in flags16
                cid = None
                offset = 4
                if has_char and len(sub_body) >= 6:
                    cid = struct.unpack_from('<H', sub_body, offset)[0]
                    offset += 2
                char_type = char_types.get(cid, 'UNKNOWN') if cid else None
                char_name = sym_class.get(cid, '') if cid else ''
                print(f"  PO3 depth={depth:2} has_char={has_char} has_image={has_image} has_name={has_name}", end='')
                if cid: print(f" → charId={cid} ({char_name}) TT={char_type}", end='')
                print()
        elif stt == 26:  # PO2
            if len(sub_body) >= 3:
                flags = sub_body[0]
                depth = struct.unpack_from('<H', sub_body, 1)[0]
                has_char = bool(flags & 0x02)
                has_name = bool(flags & 0x20)
                cid = None
                if has_char and len(sub_body) >= 5:
                    cid = struct.unpack_from('<H', sub_body, 3)[0]
                char_type = char_types.get(cid, 'UNKNOWN') if cid else None
                char_name = sym_class.get(cid, '') if cid else ''
                print(f"  PO2 depth={depth:2} has_char={has_char} has_name={has_name}", end='')
                if cid: print(f" → charId={cid} ({char_name}) TT={char_type}", end='')
                print()
        elif stt == 4:  # PlaceObject1
            print(f"  PO1 (legacy)")
        elif stt == 5:  # RemoveObject
            cid = struct.unpack_from('<H', sub_body, 0)[0]
            depth = struct.unpack_from('<H', sub_body, 2)[0]
            print(f"  RemoveObject charId={cid} depth={depth}")
        elif stt == 28:  # RemoveObject2
            depth = struct.unpack_from('<H', sub_body, 0)[0]
            print(f"  RemoveObject2 depth={depth}")
        elif stt == 0:
            print("  End")
        else:
            print(f"  TT={stt} len={sln}")
        sub_off += sln
        if stt == 0: break
