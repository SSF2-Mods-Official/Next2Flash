"""Build Shape 235 from recodes and compare bytes with original SWF."""
import msgpack, zipfile, struct
from shape_converter import parse_next2d_shape_buffer, build_define_shape3, SolidFill, SubPath, MoveToEdge, LineToEdge, CurveToEdge
from swf_binary_io import BitReader

# --- Load recodes ---
with zipfile.ZipFile('lloyd_roundtrip.n2d') as zf:
    raw = zf.read('project.msgpack')
proj = msgpack.unpackb(raw, raw=False)
shapes = [lib for lib in proj['libraries'] if lib.get('type') == 'shape']
target = next(sh for sh in shapes if sh.get('name') == 'Shape_235')
rec = target['recodes']
bounds = target.get('bounds')

fills, lines, paths = parse_next2d_shape_buffer(rec)
print(f"Recodes: fills={len(fills)} lines={len(lines)} paths={len(paths)}")
for i, p in enumerate(paths):
    moves = sum(1 for e in p.edges if isinstance(e, MoveToEdge))
    lines_c = sum(1 for e in p.edges if isinstance(e, LineToEdge))
    curves = sum(1 for e in p.edges if isinstance(e, CurveToEdge))
    print(f"  Path[{i}]: fill={p.fill_style_idx} line={p.line_style_idx} total={len(p.edges)} moves={moves} lines={lines_c} curves={curves}")

# --- Build shape tag ---
tag_bytes = build_define_shape3(288, fills, lines, paths, bounds)

# --- Parse the tag back to verify ---
print(f"\nBuilt tag: {len(tag_bytes)} bytes")
hdr = struct.unpack_from('<H', tag_bytes, 0)[0]
tag_type = hdr >> 6
tag_len = hdr & 0x3F
if tag_len == 0x3F:
    tag_len = struct.unpack_from('<I', tag_bytes, 2)[0]
    body = tag_bytes[6:]
else:
    body = tag_bytes[2:]
print(f"Tag type: {tag_type}, body length: {len(body)}")

# Parse shape records from built tag
br = BitReader(body, 0)
cid = br.read_ui16()
print(f"CharId: {cid}")
nb = br.read_ub(5)
xmin = br.read_sb(nb); xmax = br.read_sb(nb)
ymin = br.read_sb(nb); ymax = br.read_sb(nb)
br.align()
print(f"Bounds: ({xmin},{ymin})-({xmax},{ymax}) twips = ({xmin/20:.2f},{ymin/20:.2f})-({xmax/20:.2f},{ymax/20:.2f}) px")

nfills = br.read_ui8()
if nfills == 0xFF: nfills = br.read_ui16()
print(f"NumFills: {nfills}")
for i in range(nfills):
    ft = br.read_ui8()
    if ft == 0x00:
        r = br.read_ui8(); g = br.read_ui8(); b = br.read_ui8(); a = br.read_ui8()
        print(f"  Fill[{i+1}]: Solid RGBA({r},{g},{b},{a})")
    elif ft in (0x40, 0x41, 0x42, 0x43):
        bid = br.read_ui16()
        print(f"  Fill[{i+1}]: Bitmap type={ft:#x} bitmapId={bid}")
        # Skip matrix
        br.align()
        hs = br.read_ub(1)
        if hs:
            n = br.read_ub(5); br.read_sb(n); br.read_sb(n)
        hr = br.read_ub(1)
        if hr:
            n = br.read_ub(5); br.read_sb(n); br.read_sb(n)
        tn = br.read_ub(5); br.read_sb(tn); br.read_sb(tn)
        br.align()

nlines = br.read_ui8()
if nlines == 0xFF: nlines = br.read_ui16()
print(f"NumLines: {nlines}")

br.align()
nfb = br.read_ub(4)
nlb = br.read_ub(4)
print(f"NumFillBits={nfb} NumLineBits={nlb}")

# Count shape records
move_records = 0
edge_straight = 0
edge_curved = 0
fill0_used = False
fill1_used = False
rec_count = 0
while rec_count < 5000:
    is_edge = br.read_ub(1)
    if is_edge:
        straight = br.read_ub(1)
        nbits = br.read_ub(4) + 2
        if straight:
            edge_straight += 1
            gen = br.read_ub(1)
            if gen:
                br.read_sb(nbits); br.read_sb(nbits)
            else:
                br.read_ub(1)
                br.read_sb(nbits)
        else:
            edge_curved += 1
            br.read_sb(nbits); br.read_sb(nbits)
            br.read_sb(nbits); br.read_sb(nbits)
    else:
        flags = br.read_ub(5)
        if flags == 0:
            break
        if flags & 1:
            mb = br.read_ub(5)
            br.read_sb(mb); br.read_sb(mb)
            move_records += 1
        if flags & 2:
            f0 = br.read_ub(nfb)
            if f0 > 0: fill0_used = True
        if flags & 4:
            f1 = br.read_ub(nfb)
            if f1 > 0: fill1_used = True
        if flags & 8:
            br.read_ub(nlb)
        if flags & 0x10:
            print("  NEW STYLES found!")
            break
    rec_count += 1

print(f"\nShape records: {rec_count} total")
print(f"  StyleChange with move: {move_records}")
print(f"  Straight edges: {edge_straight}")
print(f"  Curved edges: {edge_curved}")
print(f"  Fill0 used: {fill0_used}")
print(f"  Fill1 used: {fill1_used}")

# --- Now load original shape 235 from SWF and count ---
print("\n=== ORIGINAL SHAPE 235 ===")
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
            print(f"Tag type: {tt}, body length: {len(body)}")
            br2 = BitReader(body, 0)
            br2.read_ui16()
            nb2 = br2.read_ub(5)
            xmin = br2.read_sb(nb2); xmax = br2.read_sb(nb2)
            ymin = br2.read_sb(nb2); ymax = br2.read_sb(nb2)
            br2.align()
            print(f"Bounds: ({xmin},{ymin})-({xmax},{ymax}) twips")
            nfills = br2.read_ui8()
            if nfills == 0xFF: nfills = br2.read_ui16()
            print(f"NumFills: {nfills}")
            for i in range(nfills):
                ft = br2.read_ui8()
                if ft == 0x00:
                    r = br2.read_ui8(); g = br2.read_ui8(); b = br2.read_ui8()
                    print(f"  Fill[{i+1}]: Solid RGB({r},{g},{b})")
            nlines = br2.read_ui8()
            print(f"NumLines: {nlines}")
            br2.align()
            nfb2 = br2.read_ub(4)
            nlb2 = br2.read_ub(4)
            print(f"NumFillBits={nfb2} NumLineBits={nlb2}")
            
            o_move = 0; o_straight = 0; o_curved = 0
            o_f0 = False; o_f1 = False
            rc = 0
            while rc < 5000:
                is_edge = br2.read_ub(1)
                if is_edge:
                    straight = br2.read_ub(1)
                    nbits = br2.read_ub(4) + 2
                    if straight:
                        o_straight += 1
                        gen = br2.read_ub(1)
                        if gen:
                            br2.read_sb(nbits); br2.read_sb(nbits)
                        else:
                            br2.read_ub(1)
                            br2.read_sb(nbits)
                    else:
                        o_curved += 1
                        br2.read_sb(nbits); br2.read_sb(nbits)
                        br2.read_sb(nbits); br2.read_sb(nbits)
                else:
                    flags = br2.read_ub(5)
                    if flags == 0:
                        break
                    if flags & 1:
                        mb = br2.read_ub(5)
                        br2.read_sb(mb); br2.read_sb(mb)
                        o_move += 1
                    if flags & 2:
                        f0 = br2.read_ub(nfb2)
                        if f0 > 0: o_f0 = True
                    if flags & 4:
                        f1 = br2.read_ub(nfb2)
                        if f1 > 0: o_f1 = True
                    if flags & 8:
                        br2.read_ub(nlb2)
                    if flags & 0x10:
                        print("  NEW STYLES found!")
                        break
                rc += 1
            
            print(f"\nShape records: {rc} total")
            print(f"  StyleChange with move: {o_move}")
            print(f"  Straight edges: {o_straight}")
            print(f"  Curved edges: {o_curved}")
            print(f"  Fill0 used: {o_f0}")
            print(f"  Fill1 used: {o_f1}")
            break
    pos = bs + tl
    if tt == 0: break
