"""
trace_cid445.py — Dump recodes for cid=445 and trace _compute_bounds step by step
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from swf_to_n2d import parse_swf, parse_define_shape_bounds
from swf_shape_to_recodes import (
    parse_define_shape_to_recodes, _compute_bounds,
    MOVE_TO, LINE_TO, CURVE_TO, FILL_STYLE, STROKE_STYLE,
    END_FILL, END_STROKE, BEGIN_PATH, GRADIENT_FILL, GRADIENT_STROKE,
    CLOSE_PATH, BITMAP_FILL, BITMAP_STROKE,
)

TAG_DEFINE_SHAPE = 2; TAG_DEFINE_SHAPE2 = 22; TAG_DEFINE_SHAPE3 = 32; TAG_DEFINE_SHAPE4 = 83
SHAPE_TAGS = {TAG_DEFINE_SHAPE, TAG_DEFINE_SHAPE2, TAG_DEFINE_SHAPE3, TAG_DEFINE_SHAPE4}

TARGET_CID = 445

SWF_PATH = r"C:\Users\glwex\AppData\Local\Temp\MicrosoftEdgeDownloads\b2655a24-55f5-4204-84a5-87bd47832f87\project.swf"
with open(SWF_PATH, 'rb') as f:
    data = f.read()
header, tags = parse_swf(data)

for tag in tags:
    if tag.tag_type not in SHAPE_TAGS:
        continue
    cid = int.from_bytes(tag.data[:2], 'little')
    if cid != TARGET_CID:
        continue

    print(f"Found cid={cid}, tag_type={tag.tag_type}, data_len={len(tag.data)}")
    _, hdr = parse_define_shape_bounds(tag.data)
    print(f"Header bounds: xMin={hdr['xMin']:.2f} xMax={hdr['xMax']:.2f} yMin={hdr['yMin']:.2f} yMax={hdr['yMax']:.2f}")
    print()

    recodes, parsed_bounds, has_bmp = parse_define_shape_to_recodes(tag.tag_type, tag.data[2:], {})

    CMD_NAMES = {
        MOVE_TO:'MOVE_TO', LINE_TO:'LINE_TO', CURVE_TO:'CURVE_TO',
        FILL_STYLE:'FILL_STYLE', STROKE_STYLE:'STROKE_STYLE',
        END_FILL:'END_FILL', END_STROKE:'END_STROKE', BEGIN_PATH:'BEGIN_PATH',
        GRADIENT_FILL:'GRADIENT_FILL', GRADIENT_STROKE:'GRADIENT_STROKE',
        CLOSE_PATH:'CLOSE_PATH', BITMAP_FILL:'BITMAP_FILL', BITMAP_STROKE:'BITMAP_STROKE',
    }

    print(f"Recodes ({len(recodes)} elements):")
    i = 0
    n = len(recodes)
    while i < n:
        c = recodes[i]
        if isinstance(c, bool):
            print(f"  [{i}] bool({c})")
            i += 1
        elif isinstance(c, int) and c in CMD_NAMES:
            name = CMD_NAMES[c]
            if c in (MOVE_TO, LINE_TO):
                x = recodes[i+1] if i+1 < n else '?'
                y = recodes[i+2] if i+2 < n else '?'
                print(f"  [{i}] {name}  x={x}  y={y}")
                i += 3
            elif c == CURVE_TO:
                print(f"  [{i}] {name}  ctrl=({recodes[i+1]},{recodes[i+2]})  anchor=({recodes[i+3]},{recodes[i+4]})")
                i += 5
            elif c == FILL_STYLE:
                print(f"  [{i}] {name}  rgba=({recodes[i+1]},{recodes[i+2]},{recodes[i+3]},{recodes[i+4]})")
                i += 6  # includes END_FILL
            elif c == GRADIENT_FILL:
                print(f"  [{i}] {name}  type={recodes[i+1]}  stops=[{len(recodes[i+2])} stops]  mtx={recodes[i+3]}  spread={recodes[i+4]}  interp={recodes[i+5]}  focal={recodes[i+6]}")
                i += 7
            elif c == GRADIENT_STROKE:
                print(f"  [{i}] {name}  w={recodes[i+1]}  cap={recodes[i+2]}  join={recodes[i+3]}  miter={recodes[i+4]}  type={recodes[i+5]}  stops=[...]  mtx={recodes[i+7]}  spread={recodes[i+8]}")
                i += 11
            elif c == STROKE_STYLE:
                print(f"  [{i}] {name}  w={recodes[i+1]}  cap={recodes[i+2]}  join={recodes[i+3]}  miter={recodes[i+4]}  rgba=({recodes[i+5]},{recodes[i+6]},{recodes[i+7]},{recodes[i+8]})")
                i += 11  # includes END_STROKE
            elif c in (BITMAP_FILL, BITMAP_STROKE):
                if c == BITMAP_FILL:
                    print(f"  [{i}] BITMAP_FILL  bmp_id={recodes[i+1]}  mtx={recodes[i+2]}  repeat={recodes[i+3]}  smooth={recodes[i+4]}")
                    i += 5
                else:
                    print(f"  [{i}] BITMAP_STROKE  w={recodes[i+1]}  cap={recodes[i+2]}  join={recodes[i+3]}  miter={recodes[i+4]}  bmp_id={recodes[i+5]}  mtx={recodes[i+6]}  repeat={recodes[i+7]}  smooth={recodes[i+8]}")
                    i += 9
            elif c in (BEGIN_PATH, END_FILL, END_STROKE, CLOSE_PATH):
                print(f"  [{i}] {name}")
                i += 1
            else:
                print(f"  [{i}] {name}")
                i += 1
        else:
            print(f"  [{i}] RAW: {repr(c)[:80]}")
            i += 1

    print()
    print(f"parsed_bounds: {parsed_bounds}")
    break
