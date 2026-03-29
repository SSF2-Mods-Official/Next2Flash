"""
trace_parse445.py — instrument the parsing loop for cid=445 to find coordinate corruption
"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__))

from swf_to_n2d import parse_swf
from swf_shape_to_recodes import (
    _BitReader, _read_fill_style_array, _read_line_style_array,
    _add_fill_edge, _add_line_edge, _flush, _stacks_to_recodes, _compute_bounds,
)

TAG_DEFINE_SHAPE3 = 32

SWF_PATH = r"C:\Users\glwex\AppData\Local\Temp\MicrosoftEdgeDownloads\b2655a24-55f5-4204-84a5-87bd47832f87\project.swf"
with open(SWF_PATH, 'rb') as f:
    data = f.read()

header, tags = parse_swf(data)

TARGET_CID = 445
for tag in tags:
    if tag.tag_type != TAG_DEFINE_SHAPE3:
        continue
    cid = int.from_bytes(tag.data[:2], 'little')
    if cid != TARGET_CID:
        continue

    body = tag.data[2:]
    br = _BitReader(body, 0)
    tag_type = tag.tag_type

    # Skip shape bounds RECT
    nbits = br.read_ub(5)
    for _ in range(4):
        br.read_sb(nbits)
    print(f"After RECT: byte_pos={br.byte_pos}, bit_pos={br.bit_pos}")

    fill_styles = _read_fill_style_array(br, tag_type)
    print(f"After fill_styles ({len(fill_styles)} fills): byte_pos={br.byte_pos}, bit_pos={br.bit_pos}")
    for i, f in enumerate(fill_styles):
        print(f"  fill[{i}]: fillStyleType={f['fillStyleType']}")

    line_styles = _read_line_style_array(br, tag_type)
    print(f"After line_styles ({len(line_styles)} lines): byte_pos={br.byte_pos}, bit_pos={br.bit_pos}")
    for i, l in enumerate(line_styles):
        print(f"  line[{i}]: Width={l.get('Width')}")

    nb = br.read_ui8()
    fill_bits = nb >> 4
    line_bits = nb & 0x0F
    print(f"NumFillBits={fill_bits}, NumLineBits={line_bits}, byte_pos={br.byte_pos}")

    cur_x = cur_y = 0
    prev_x = prev_y = 0
    edge_prev_x = edge_prev_y = 0
    cur_fill0 = cur_fill1 = cur_line = 0
    fill0_buckets = {}; fill1_buckets = {}; line_buckets = {}
    stacks = []; edge_group = 0
    edge_count = 0; record_count = 0

    while br.remaining > 0 and record_count < 5000:
        type_flag = br.read_ub(1)
        if type_flag == 1:
            # Edge record
            straight = br.read_ub(1)
            nbits_e = br.read_ub(4) + 2
            if straight:
                gen = br.read_ub(1)
                if gen:
                    dx = br.read_sb(nbits_e); dy = br.read_sb(nbits_e)
                else:
                    vert = br.read_ub(1)
                    dx = 0 if vert else br.read_sb(nbits_e)
                    dy = br.read_sb(nbits_e) if vert else 0
                ax = cur_x + dx; ay = cur_y + dy
                cur_x, cur_y = ax, ay
                edge = {'isCurved': False, 'ControlX': 0.0, 'ControlY': 0.0,
                        'AnchorX': ax / 20.0, 'AnchorY': ay / 20.0}
            else:
                cdx = br.read_sb(nbits_e); cdy = br.read_sb(nbits_e)
                adx = br.read_sb(nbits_e); ady = br.read_sb(nbits_e)
                cx = cur_x + cdx; cy = cur_y + cdy
                ax = cx + adx; ay = cy + ady
                cur_x, cur_y = ax, ay
                edge = {'isCurved': True, 'ControlX': cx / 20.0, 'ControlY': cy / 20.0,
                        'AnchorX': ax / 20.0, 'AnchorY': ay / 20.0}

            if cur_fill0:
                _add_fill_edge(fill0_buckets, cur_fill0 - 1, edge_group, fill_styles,
                               prev_x / 20.0, prev_y / 20.0, edge)
            if cur_fill1:
                _add_fill_edge(fill1_buckets, cur_fill1 - 1, edge_group, fill_styles,
                               prev_x / 20.0, prev_y / 20.0, edge)
            if cur_line:
                from_x = edge_prev_x / 20.0
                from_y = edge_prev_y / 20.0
                # Check for huge coordinates
                if abs(from_x) > 1000 or abs(from_y) > 1000:
                    print(f"\n*** HUGE LINE COORD at edge_count={edge_count}: from=({from_x:.2f},{from_y:.2f})  anchor=({edge['AnchorX']:.2f},{edge['AnchorY']:.2f})")
                    print(f"    cur_x={cur_x} cur_y={cur_y}  byte_pos={br.byte_pos}  bit_pos={br.bit_pos}")
                _add_line_edge(line_buckets, cur_line - 1, line_styles,
                               from_x, from_y, edge)
            edge_prev_x, edge_prev_y = cur_x, cur_y
            edge_count += 1
        else:
            flags = br.read_ub(5)
            if flags == 0:
                _flush(stacks, fill0_buckets, fill1_buckets, line_buckets)
                br.align()
                break
            edge_group += 1
            has_new  = (flags >> 4) & 1
            has_line = (flags >> 3) & 1
            has_fill1 = (flags >> 2) & 1
            has_fill0 = (flags >> 1) & 1
            has_move = flags & 1
            print(f"\n[RECORD {record_count}] flags={flags:#07b}  has_new={has_new} has_line={has_line} has_fill1={has_fill1} has_fill0={has_fill0} has_move={has_move}  byte_pos={br.byte_pos}  bit_pos={br.bit_pos}")

            if has_new:
                _flush(stacks, fill0_buckets, fill1_buckets, line_buckets)
                cur_x = cur_y = 0
                fill0_buckets = {}; fill1_buckets = {}; line_buckets = {}

            if has_move:
                mb = br.read_ub(5)
                cur_x = br.read_sb(mb)
                cur_y = br.read_sb(mb)
                print(f"  MOVE: mb={mb} cur_x={cur_x} cur_y={cur_y}  (pixels: {cur_x/20:.2f}, {cur_y/20:.2f})")

            prev_x, prev_y = cur_x, cur_y
            edge_prev_x, edge_prev_y = cur_x, cur_y

            if has_fill0:
                cur_fill0 = br.read_ub(fill_bits)
                print(f"  fill0={cur_fill0}")
            if has_fill1:
                cur_fill1 = br.read_ub(fill_bits)
                print(f"  fill1={cur_fill1}")
            if has_line:
                cur_line = br.read_ub(line_bits)
                print(f"  line={cur_line}")
                if abs(cur_x / 20.0) > 1000 or abs(cur_y / 20.0) > 1000:
                    print(f"  *** HUGE POSITION WHEN LINE CHANGED: cur_x={cur_x/20:.2f} cur_y={cur_y/20:.2f}")

            if has_new:
                bp_before = br.byte_pos
                fill_styles = _read_fill_style_array(br, tag_type)
                print(f"  New fill_styles ({len(fill_styles)}), byte_pos={br.byte_pos} (was {bp_before})")
                bp_before = br.byte_pos
                line_styles = _read_line_style_array(br, tag_type)
                print(f"  New line_styles ({len(line_styles)}), byte_pos={br.byte_pos} (was {bp_before})")
                for i, l in enumerate(line_styles):
                    print(f"    line[{i}]: Width={l.get('Width')}")
                nb = br.read_ui8()
                fill_bits = nb >> 4; line_bits = nb & 0x0F
                print(f"  NumFillBits={fill_bits}, NumLineBits={line_bits}, byte_pos={br.byte_pos}")

        record_count += 1

    print(f"\nTotal edges: {edge_count}, records: {record_count}, stacks: {len(stacks)}")
    recodes, parsed_bounds, _ = _stacks_to_recodes(stacks, {})
    print(f"Bounds: {parsed_bounds}")
    break
