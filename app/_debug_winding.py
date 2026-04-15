"""Check winding direction vs fill0/fill1 assignment in original shapes."""
from swf_binary_io import BitReader
import struct

path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf'
with open(path, 'rb') as f:
    data = f.read()

br = BitReader(data, 8)
nb = br.read_ub(5)
for _ in range(4): br.read_sb(nb)
br.align()
br.read_ui8(); br.read_ui8(); br.read_ui16()
pos = br.byte_pos

results = []

while pos < len(data):
    if pos + 2 > len(data): break
    hdr = struct.unpack_from('<H', data, pos)[0]
    tag_type = hdr >> 6
    tag_len = hdr & 0x3F
    if tag_len == 0x3F:
        tag_len = struct.unpack_from('<I', data, pos+2)[0]
        body_start = pos + 6
    else:
        body_start = pos + 2
    
    if tag_type in (2, 22, 32, 83):
        body = data[body_start:body_start+tag_len]
        try:
            br2 = BitReader(body, 0)
            cid = br2.read_ui16()
            nb2 = br2.read_ub(5)
            for _ in range(4): br2.read_sb(nb2)
            br2.align()
            
            if tag_type == 83:
                nb3 = br2.read_ub(5)
                for _ in range(4): br2.read_sb(nb3)
                br2.align()
                br2.read_ub(5); br2.read_ub(1); br2.read_ub(1); br2.read_ub(1)
            
            nfills = br2.read_ui8()
            if nfills == 0xFF: nfills = br2.read_ui16()
            for i in range(nfills):
                ft = br2.read_ui8()
                if ft == 0x00:
                    cnt = 4 if tag_type in (32, 83) else 3
                    for _ in range(cnt): br2.read_ui8()
                elif ft in (0x40, 0x41, 0x42, 0x43):
                    br2.read_ui16()
                    br2.align()
                    hs = br2.read_ub(1)
                    if hs:
                        n = br2.read_ub(5); br2.read_sb(n); br2.read_sb(n)
                    hr = br2.read_ub(1)
                    if hr:
                        n = br2.read_ub(5); br2.read_sb(n); br2.read_sb(n)
                    tn = br2.read_ub(5); br2.read_sb(tn); br2.read_sb(tn)
                    br2.align()
                elif ft in (0x10, 0x12, 0x13):
                    br2.align()
                    hs = br2.read_ub(1)
                    if hs:
                        n = br2.read_ub(5); br2.read_sb(n); br2.read_sb(n)
                    hr = br2.read_ub(1)
                    if hr:
                        n = br2.read_ub(5); br2.read_sb(n); br2.read_sb(n)
                    tn = br2.read_ub(5); br2.read_sb(tn); br2.read_sb(tn)
                    br2.align()
                    nc = br2.read_ui8()
                    for _ in range(nc):
                        br2.read_ui8()
                        cnt = 4 if tag_type in (32, 83) else 3
                        for _ in range(cnt): br2.read_ui8()
                    br2.read_ub(2); br2.read_ub(2)
                    if ft == 0x13: br2.read_ui16()
            
            nlines = br2.read_ui8()
            if nlines == 0xFF: nlines = br2.read_ui16()
            if tag_type == 83:
                pass  # complex LINESTYLE2, skip shape record scan
            elif tag_type in (32,):
                for _ in range(nlines):
                    br2.read_ui16()
                    for _ in range(4): br2.read_ui8()
            else:
                for _ in range(nlines):
                    br2.read_ui16()
                    for _ in range(3): br2.read_ui8()
            
            if tag_type == 83:
                pos = body_start + tag_len
                if tag_type == 0: break
                continue
            
            br2.align()
            nfb = br2.read_ub(4)
            nlb = br2.read_ub(4)
            
            # Track all sub-paths with their fill assignments and vertices
            sub_paths = []
            current_verts = []
            current_f0 = 0
            current_f1 = 0
            cx, cy = 0, 0
            
            rec_count = 0
            while rec_count < 2000:
                is_edge = br2.read_ub(1)
                if is_edge:
                    straight = br2.read_ub(1)
                    nbits = br2.read_ub(4) + 2
                    if straight:
                        gen = br2.read_ub(1)
                        if gen:
                            dx = br2.read_sb(nbits)
                            dy = br2.read_sb(nbits)
                        else:
                            vert = br2.read_ub(1)
                            if vert:
                                dx = 0; dy = br2.read_sb(nbits)
                            else:
                                dx = br2.read_sb(nbits); dy = 0
                    else:
                        cdx = br2.read_sb(nbits)
                        cdy = br2.read_sb(nbits)
                        adx = br2.read_sb(nbits)
                        ady = br2.read_sb(nbits)
                        dx = cdx + adx
                        dy = cdy + ady
                    cx += dx; cy += dy
                    current_verts.append((cx, cy))
                else:
                    flags = br2.read_ub(5)
                    if flags == 0:
                        if current_verts:
                            sub_paths.append((current_f0, current_f1, list(current_verts)))
                        break
                    if flags & 1:
                        # New moveTo = new sub-path
                        if current_verts:
                            sub_paths.append((current_f0, current_f1, list(current_verts)))
                            current_verts = []
                        mb = br2.read_ub(5)
                        cx = br2.read_sb(mb)
                        cy = br2.read_sb(mb)
                        current_verts.append((cx, cy))
                    if flags & 2:
                        f0 = br2.read_ub(nfb)
                        current_f0 = f0
                    if flags & 4:
                        f1 = br2.read_ub(nfb)
                        current_f1 = f1
                    if flags & 8:
                        br2.read_ub(nlb)
                    if flags & 0x10:
                        break
                rec_count += 1
            
            # Compute signed area for each sub-path
            for f0, f1, verts in sub_paths:
                if len(verts) < 3:
                    continue
                n = len(verts)
                area = 0
                for i in range(n):
                    j = (i + 1) % n
                    area += verts[i][0] * verts[j][1]
                    area -= verts[j][0] * verts[i][1]
                area /= 2
                winding = "CW" if area > 0 else "CCW"
                fill_type = "f0" if f0 > 0 and f1 == 0 else "f1" if f1 > 0 and f0 == 0 else f"f0={f0},f1={f1}"
                results.append((cid, tag_type, fill_type, winding, area))
        except Exception as e:
            pass
    
    pos = body_start + tag_len
    if tag_type == 0: break

# Print summary
from collections import Counter
combos = Counter()
for cid, tt, ft, wind, area in results:
    combos[(ft, wind)] += 1

print("Fill assignment + winding direction combinations:")
for (ft, wind), cnt in combos.most_common():
    print(f"  {ft} + {wind}: {cnt}")

# Print specific examples
print("\nExamples of fill0 usage:")
for cid, tt, ft, wind, area in results:
    if "f0" in ft and cid in (235, 236):
        print(f"  cid={cid} tag={tt} {ft} {wind} area={area:.0f}")
