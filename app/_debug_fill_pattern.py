"""Dump ALL StyleChange records from original shape 235 to see fill0/fill1 pattern."""
from swf_binary_io import BitReader
import struct

path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf'
with open(path, 'rb') as f:
    data = f.read()

br_f = BitReader(data, 8)
nb = br_f.read_ub(5)
for _ in range(4): br_f.read_sb(nb)
br_f.align()
br_f.read_ui8(); br_f.read_ui8(); br_f.read_ui16()
pos = br_f.byte_pos

while pos < len(data):
    if pos + 2 > len(data): break
    hdr = struct.unpack_from('<H', data, pos)[0]
    tt = hdr >> 6
    tl = hdr & 0x3F
    if tl == 0x3F:
        tl = struct.unpack_from('<I', data, pos+2)[0]
        bs = pos + 6
    else:
        bs = pos + 2
    if tt == 2:
        body = data[bs:bs+tl]
        ocid = struct.unpack_from('<H', body, 0)[0]
        if ocid == 235:
            br2 = BitReader(body, 0)
            br2.read_ui16()
            nb2 = br2.read_ub(5)
            for _ in range(4): br2.read_sb(nb2)
            br2.align()
            nfills = br2.read_ui8()
            for i in range(nfills):
                ft = br2.read_ui8()
                if ft == 0x00:
                    for _ in range(3): br2.read_ui8()
            nlines = br2.read_ui8()
            for _ in range(nlines):
                br2.read_ui16()
                for _ in range(3): br2.read_ui8()
            br2.align()
            nfb = br2.read_ub(4)
            nlb = br2.read_ub(4)
            
            cur_f0 = 0
            cur_f1 = 0
            cx, cy = 0, 0
            edge_idx = 0
            style_changes = []
            
            while True:
                is_edge = br2.read_ub(1)
                if is_edge:
                    straight = br2.read_ub(1)
                    nbits = br2.read_ub(4) + 2
                    if straight:
                        gen = br2.read_ub(1)
                        if gen:
                            dx = br2.read_sb(nbits); dy = br2.read_sb(nbits)
                        else:
                            vert = br2.read_ub(1)
                            if vert:
                                dx = 0; dy = br2.read_sb(nbits)
                            else:
                                dx = br2.read_sb(nbits); dy = 0
                    else:
                        cdx = br2.read_sb(nbits); cdy = br2.read_sb(nbits)
                        adx = br2.read_sb(nbits); ady = br2.read_sb(nbits)
                        dx = cdx + adx; dy = cdy + ady
                    cx += dx; cy += dy
                    edge_idx += 1
                else:
                    flags = br2.read_ub(5)
                    if flags == 0:
                        break
                    mx = my = None
                    f0_set = f1_set = None
                    if flags & 1:
                        mb = br2.read_ub(5)
                        cx = br2.read_sb(mb)
                        cy = br2.read_sb(mb)
                        mx, my = cx/20, cy/20
                    if flags & 2:
                        cur_f0 = br2.read_ub(nfb)
                        f0_set = cur_f0
                    if flags & 4:
                        cur_f1 = br2.read_ub(nfb)
                        f1_set = cur_f1
                    if flags & 8:
                        br2.read_ub(nlb)
                    parts = [f"@edge{edge_idx}"]
                    if mx is not None:
                        parts.append(f"move=({mx:.2f},{my:.2f})")
                    if f0_set is not None:
                        parts.append(f"fill0={f0_set}")
                    if f1_set is not None:
                        parts.append(f"fill1={f1_set}")
                    parts.append(f"[active: f0={cur_f0} f1={cur_f1}]")
                    style_changes.append(" ".join(parts))
                    if flags & 0x10:
                        print("NEW STYLES!")
                        break
            
            print(f"Shape cid=235: {edge_idx} edges, {len(style_changes)} StyleChange records:")
            for sc in style_changes:
                print(f"  {sc}")
            break
    pos = bs + tl
    if tt == 0: break
