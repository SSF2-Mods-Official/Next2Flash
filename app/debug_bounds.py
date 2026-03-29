"""
debug_bounds.py — Compare parsed_bounds from recodes vs SWF header bounds for each shape.
Find shapes where _compute_bounds gives significantly different results.
"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__))

from swf_to_n2d import parse_swf, parse_define_shape_bounds
TAG_DEFINE_SHAPE = 2; TAG_DEFINE_SHAPE2 = 22; TAG_DEFINE_SHAPE3 = 32; TAG_DEFINE_SHAPE4 = 83
from swf_shape_to_recodes import parse_define_shape_to_recodes, _compute_bounds

SWF_PATH = r"C:\Users\glwex\AppData\Local\Temp\MicrosoftEdgeDownloads\b2655a24-55f5-4204-84a5-87bd47832f87\project.swf"

with open(SWF_PATH, 'rb') as f:
    data = f.read()

header, tags = parse_swf(data)
print(f"Tags: {len(tags)}  Stage: {header['width']} x {header['height']}")
print()

SHAPE_TAGS = {TAG_DEFINE_SHAPE, TAG_DEFINE_SHAPE2, TAG_DEFINE_SHAPE3, TAG_DEFINE_SHAPE4}

print(f"{'cid':>6}  {'header W':>10}  {'header H':>10}  {'parsed W':>12}  {'parsed H':>12}  {'MISMATCH?'}")
print("-"*75)

mismatches = []
for tag in tags:
    if tag.tag_type not in SHAPE_TAGS:
        continue
    body = tag.data          # full tag data (includes 2-byte charId)
    body_after = tag.data[2:]  # body after charId
    cid, hdr_bounds = parse_define_shape_bounds(body)
    hdr_w = hdr_bounds['xMax'] - hdr_bounds['xMin']
    hdr_h = hdr_bounds['yMax'] - hdr_bounds['yMin']

    try:
        recodes, parsed_bounds, _ = parse_define_shape_to_recodes(tag.tag_type, body_after, {})
        p_w = parsed_bounds['xMax'] - parsed_bounds['xMin']
        p_h = parsed_bounds['yMax'] - parsed_bounds['yMin']
    except Exception as e:
        print(f"  cid={cid}: ERROR {e}")
        continue

    # Flag big differences or huge parsed bounds
    flag = ''
    if p_w > 1000 or p_h > 1000:
        flag = '  *** HUGE PARSED BOUNDS'
    elif abs(p_w - hdr_w) > 50 or abs(p_h - hdr_h) > 50:
        flag = '  *** MISMATCH'

    if flag:
        mismatches.append((cid, hdr_w, hdr_h, p_w, p_h, 
                           parsed_bounds['xMin'], parsed_bounds['xMax'],
                           parsed_bounds['yMin'], parsed_bounds['yMax'],
                           flag))
        print(f"  cid={cid:4d}  hdr=({hdr_w:.1f} x {hdr_h:.1f})  parsed=({p_w:.1f} x {p_h:.1f}){flag}")

print()
print(f"Total mismatches/huge: {len(mismatches)}")
if mismatches:
    print("\nDetailed (parsed bounds):")
    for row in mismatches[:20]:
        cid, hw, hh, pw, ph, pxmn, pxmx, pymn, pymx, flag = row
        print(f"  cid={cid}: parsed xMin={pxmn:.2f} xMax={pxmx:.2f} yMin={pymn:.2f} yMax={pymx:.2f}  W={pw:.1f} H={ph:.1f}{flag}")
