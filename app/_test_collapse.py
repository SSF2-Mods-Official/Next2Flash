"""Test the fill_merge collapse for morph shapes."""
import zipfile, msgpack, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shape_converter import parse_next2d_shape_buffer, _morph_collapse_fill_merge, _encode_morph_shape_edges

n2d = "test_swfs/lloyd_rt.n2d"
with zipfile.ZipFile(n2d, 'r') as z:
    with z.open('project.msgpack') as f:
        raw = f.read()
data = msgpack.unpackb(raw, raw=False)

for lib in data['libraries']:
    if isinstance(lib, dict) and lib.get('name') == 'MorphShape_147':
        sr = lib['recodes']
        er = lib['endRecodes']
        break

sf, sl, sp = parse_next2d_shape_buffer(sr)
ef, el, ep = parse_next2d_shape_buffer(er)
print(f"Before collapse: start={len(sp)} paths, end={len(ep)} paths")
for i, p in enumerate(sp):
    print(f"  start[{i}]: fill={p.fill_style_idx} line={p.line_style_idx} edges={len(p.edges)}")
for i, p in enumerate(ep):
    print(f"  end[{i}]: fill={p.fill_style_idx} line={p.line_style_idx} edges={len(p.edges)}")

sp2, sc = _morph_collapse_fill_merge(sp)
ep2, ec = _morph_collapse_fill_merge(ep)
print(f"\nAfter collapse: start={len(sp2)} paths (collapsed={sc}), end={len(ep2)} paths (collapsed={ec})")
for i, p in enumerate(sp2):
    print(f"  start[{i}]: fill={p.fill_style_idx} line={p.line_style_idx} edges={len(p.edges)} fill0={p._morph_use_fill0}")
for i, p in enumerate(ep2):
    print(f"  end[{i}]: fill={p.fill_style_idx} line={p.line_style_idx} edges={len(p.edges)} fill0={p._morph_use_fill0}")

# Encode
start_bits = _encode_morph_shape_edges(sf, sl, sp2)
end_bits = _encode_morph_shape_edges(ef, el, ep2, is_end_state=True)
print(f"\nEncoded: start={len(start_bits)} bytes, end={len(end_bits)} bytes")

# Check start edges header
fb = start_bits[0] >> 4
lb = start_bits[0] & 0x0F
print(f"Start header: fill_bits={fb} line_bits={lb}")

# Check first StyleChange flags
# After 8 bits of header, the first record should be a StyleChange
from swf_binary_io import BitReader
br = BitReader(start_bits, 0)
br.read_ub(4)  # fill_bits
br.read_ub(4)  # line_bits
tf = br.read_ub(1)  # type flag
flags = br.read_ub(5)
print(f"First record: type_flag={tf} flags=0b{flags:05b}")
has_move = flags & 0x01
has_fill0 = (flags >> 1) & 1
has_fill1 = (flags >> 2) & 1
has_line = (flags >> 3) & 1
print(f"  has_move={has_move} has_fill0={has_fill0} has_fill1={has_fill1} has_line={has_line}")

# Check end edges
efb = end_bits[0] >> 4
elb = end_bits[0] & 0x0F
print(f"\nEnd header: fill_bits={efb} line_bits={elb}")
