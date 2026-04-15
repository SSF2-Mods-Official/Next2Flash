"""Trace test7 fill bucket construction step by step."""
from swf_binary_io import BitReader
import struct, copy

with open('test_swfs/test7_two_fills.swf', 'rb') as f:
    data = f.read()

br = BitReader(data, 8)
nb = br.read_ub(5)
for _ in range(4): br.read_sb(nb)
br.align()
br.read_ui8(); br.read_ui8(); br.read_ui16()
pos = br.byte_pos

while pos < len(data):
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
        break
    pos = bs + tl

br2 = BitReader(body, 0)
cid = br2.read_ui16()
nb2 = br2.read_ub(5)
for _ in range(4): br2.read_sb(nb2)
br2.align()

nfills = br2.read_ui8()
print(f'NumFills: {nfills}')
for i in range(nfills):
    ft = br2.read_ui8()
    r = br2.read_ui8(); g = br2.read_ui8(); b = br2.read_ui8()
    print(f'  Fill[{i}]: type={ft} RGB({r},{g},{b})')

nlines = br2.read_ui8()
br2.align()
fill_bits = br2.read_ub(4)
line_bits = br2.read_ub(4)
print(f'FillBits={fill_bits} LineBits={line_bits}')

cur_x = cur_y = 0
prev_x = prev_y = 0
cur_fill0 = cur_fill1 = 0
edge_group = 0

fill0_buckets = {}
fill1_buckets = {}

rec = 0
while True:
    tf = br2.read_ub(1)
    if tf == 1:
        straight = br2.read_ub(1)
        nbits = br2.read_ub(4) + 2
        if straight:
            gen = br2.read_ub(1)
            if gen:
                dx = br2.read_sb(nbits); dy = br2.read_sb(nbits)
            else:
                vert = br2.read_ub(1)
                dx = 0 if vert else br2.read_sb(nbits)
                dy = br2.read_sb(nbits) if vert else 0
            ax = cur_x + dx; ay = cur_y + dy
            cur_x, cur_y = ax, ay
            edge = {'AnchorX': ax/20, 'AnchorY': ay/20, 'isCurved': False}
        else:
            cdx = br2.read_sb(nbits); cdy = br2.read_sb(nbits)
            adx = br2.read_sb(nbits); ady = br2.read_sb(nbits)
            cx = cur_x + cdx; cy = cur_y + cdy
            ax = cx + adx; ay = cy + ady
            cur_x, cur_y = ax, ay
            edge = {'AnchorX': ax/20, 'AnchorY': ay/20, 'isCurved': True,
                     'ControlX': cx/20, 'ControlY': cy/20}

        if cur_fill0:
            idx = cur_fill0 - 1
            if idx not in fill0_buckets: fill0_buckets[idx] = {}
            if edge_group not in fill0_buckets[idx]:
                fill0_buckets[idx][edge_group] = {
                    'startX': prev_x/20, 'startY': prev_y/20,
                    'endX': 0, 'endY': 0, 'cache': []
                }
            fill0_buckets[idx][edge_group]['cache'].append(copy.deepcopy(edge))
            fill0_buckets[idx][edge_group]['endX'] = edge['AnchorX']
            fill0_buckets[idx][edge_group]['endY'] = edge['AnchorY']
        if cur_fill1:
            idx = cur_fill1 - 1
            if idx not in fill1_buckets: fill1_buckets[idx] = {}
            if edge_group not in fill1_buckets[idx]:
                fill1_buckets[idx][edge_group] = {
                    'startX': prev_x/20, 'startY': prev_y/20,
                    'endX': 0, 'endY': 0, 'cache': []
                }
            fill1_buckets[idx][edge_group]['cache'].append(copy.deepcopy(edge))
            fill1_buckets[idx][edge_group]['endX'] = edge['AnchorX']
            fill1_buckets[idx][edge_group]['endY'] = edge['AnchorY']

        print(f'  Edge[{rec}]: -> ({cur_x/20},{cur_y/20}) f0={cur_fill0} f1={cur_fill1}')
    else:
        flags = br2.read_ub(5)
        if flags == 0:
            print(f'  EndShape')
            break
        edge_group += 1
        if flags & 1:
            mb = br2.read_ub(5)
            cur_x = br2.read_sb(mb)
            cur_y = br2.read_sb(mb)
        prev_x, prev_y = cur_x, cur_y
        if flags & 2: cur_fill0 = br2.read_ub(fill_bits)
        if flags & 4: cur_fill1 = br2.read_ub(fill_bits)
        if flags & 8: br2.read_ub(line_bits)
        print(f'  StyleChange[{rec}]: move=({cur_x/20},{cur_y/20}) f0={cur_fill0} f1={cur_fill1} prevXY=({prev_x/20},{prev_y/20})')
    rec += 1

print()
print('=== Fill0 buckets (before reverse/merge) ===')
for idx, grps in sorted(fill0_buckets.items()):
    for eg, seg in sorted(grps.items()):
        print(f'  style={idx} eg={eg}: start=({seg["startX"]},{seg["startY"]}) end=({seg["endX"]},{seg["endY"]})')
        for e in seg['cache']:
            print(f'    -> ({e["AnchorX"]},{e["AnchorY"]})')

print()
print('=== Fill1 buckets (before reverse/merge) ===')
for idx, grps in sorted(fill1_buckets.items()):
    for eg, seg in sorted(grps.items()):
        print(f'  style={idx} eg={eg}: start=({seg["startX"]},{seg["startY"]}) end=({seg["endX"]},{seg["endY"]})')
        for e in seg['cache']:
            print(f'    -> ({e["AnchorX"]},{e["AnchorY"]})')

# Now simulate _fill_reverse
print()
print('=== After _fill_reverse (fill0 edges reversed) ===')
for idx, grps in sorted(fill0_buckets.items()):
    for eg, seg in sorted(grps.items()):
        # Reverse: swap start/end, reverse cache, fix anchors
        new_start = (seg['endX'], seg['endY'])
        new_end = (seg['startX'], seg['startY'])
        rev_cache = list(reversed(seg['cache']))
        # Recalc anchors: after reversal, each edge's anchor becomes previous edge's start
        # In the actual code, the anchors point to where you came FROM
        # For straight edges: reversed edge goes from old end to old start
        edges = seg['cache']
        new_edges = []
        for i in range(len(edges)-1, -1, -1):
            e = edges[i]
            if i == 0:
                new_anchor = (seg['startX'], seg['startY'])
            else:
                new_anchor = (edges[i-1]['AnchorX'], edges[i-1]['AnchorY'])
            new_e = {'AnchorX': new_anchor[0], 'AnchorY': new_anchor[1], 'isCurved': e.get('isCurved', False)}
            new_edges.append(new_e)
        
        print(f'  style={idx} eg={eg}: start=({new_start[0]},{new_start[1]}) end=({new_end[0]},{new_end[1]})')
        for e in new_edges:
            print(f'    -> ({e["AnchorX"]},{e["AnchorY"]})')

# Now simulate _coordinate_adjustment for fill1 buckets  
print()
print('=== _coordinate_adjustment simulation for fill1 ===')
for idx, grps in sorted(fill1_buckets.items()):
    sorted_grps = sorted(grps.items())
    for i, (eg, seg) in enumerate(sorted_grps):
        print(f'  style={idx} eg={eg}: start=({seg["startX"]},{seg["startY"]})')
        # The coordinate_adjustment chains segments by matching end to next start
        for e in seg['cache']:
            print(f'    -> ({e["AnchorX"]},{e["AnchorY"]})')

# Also run the actual recodes to compare
print()
print('=== Actual recodes from swf_shape_to_recodes ===')
from swf_shape_to_recodes import parse_define_shape_to_recodes
recodes = parse_define_shape_to_recodes(2, body[2:], {})
print(f'Total recode values: {len(recodes)}')
i = 0
while i < len(recodes):
    cmd = recodes[i]
    if cmd == 9:  # beginPath
        fill = recodes[i+1]
        x = recodes[i+2]
        y = recodes[i+3]
        print(f'  beginPath fill={fill} move=({x},{y})')
        i += 4
    elif cmd == 2:  # lineTo
        print(f'  lineTo({recodes[i+1]},{recodes[i+2]})')
        i += 3
    elif cmd == 3:  # curveTo
        print(f'  curveTo({recodes[i+1]},{recodes[i+2]},{recodes[i+3]},{recodes[i+4]})')
        i += 5
    elif cmd == 4:  # closePath / endFill
        print(f'  endFill')
        i += 1
    elif cmd == 1:  # moveTo
        print(f'  moveTo({recodes[i+1]},{recodes[i+2]})')
        i += 3
    else:
        print(f'  unknown cmd={cmd} at pos={i}')
        i += 1
