"""Trace test7 recodes from the fixed SWF."""
from swf_shape_to_recodes import parse_define_shape_to_recodes
from swf_binary_io import BitReader
import struct

with open('test_swfs/test7_two_fills.swf', 'rb') as f:
    data = f.read()

# Skip SWF header to find tags
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

# Parse recodes
body_after_id = body[2:]
recodes_list, bounds, has_bmp = parse_define_shape_to_recodes(2, body_after_id, {})
print("Recodes produced:")
for v in recodes_list:
    print(f"  {v}")

print()
print("Decoded (manually):")
# Just print the raw values showing enum names
for idx, v in enumerate(recodes_list):
    n = v.name if hasattr(v, 'name') else repr(v)
    print(f"  [{idx}] {n}")

# Now also parse the recodes back to SubPaths (as the encoder does)
print()
print("=== SubPaths from parse_next2d_shape_buffer ===")
from shape_converter import parse_next2d_shape_buffer
sub_paths = parse_next2d_shape_buffer(recodes_list)
for i, sp in enumerate(sub_paths):
    print(f"SubPath[{i}]: {type(sp).__name__}")
    if hasattr(sp, 'fill_style_idx'):
        print(f"  fill_idx={sp.fill_style_idx}, line_idx={sp.line_style_idx}")
        for rec in sp.records:
            print(f"  {rec}")
    else:
        print(f"  {sp}")
