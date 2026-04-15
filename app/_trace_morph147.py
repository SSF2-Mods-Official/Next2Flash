"""
Trace morph shape #147 through the full pipeline:
1. Original SWF binary → parse edges
2. N2D stored recodes (start + end)  
3. Recodes → parse_next2d_shape_buffer → sub_paths
4. Sub_paths → _encode_morph_shape_edges → binary
5. Compare original binary with roundtrip binary
"""
import zipfile, msgpack, os, sys, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swf_binary_io import BitReader
from swf_constants import ShapeCommand

n2d = "test_swfs/lloyd_rt.n2d"

# Load N2D
with zipfile.ZipFile(n2d, 'r') as z:
    with z.open('project.msgpack') as f:
        raw = f.read()
data = msgpack.unpackb(raw, raw=False)

# Find MorphShape_147
for lib in data['libraries']:
    if isinstance(lib, dict) and lib.get('name', '') == 'MorphShape_147':
        morph = lib
        break
else:
    print("MorphShape_147 not found!")
    sys.exit(1)

print(f"=== MorphShape_147 ===")
print(f"rawTagType: {morph['rawTagType']}")
print(f"swfCharId: {morph['swfCharId']}")
print(f"isMorphShape: {morph['isMorphShape']}")
print(f"bounds: {morph['bounds']}")
print(f"endBounds: {morph['endBounds']}")

# Decode recodes
start_recodes = morph['recodes']
end_recodes = morph['endRecodes']

if isinstance(start_recodes, bytes):
    print(f"\nStart recodes: {len(start_recodes)} bytes")
    print(f"  hex: {start_recodes[:80].hex()}")
elif isinstance(start_recodes, str):
    import base64
    start_recodes = base64.b64decode(start_recodes)
    print(f"\nStart recodes: {len(start_recodes)} bytes (was base64)")
    print(f"  hex: {start_recodes[:80].hex()}")

if isinstance(end_recodes, bytes):
    print(f"\nEnd recodes: {len(end_recodes)} bytes")
    print(f"  hex: {end_recodes[:80].hex()}")
elif isinstance(end_recodes, str):
    import base64
    end_recodes = base64.b64decode(end_recodes)
    print(f"\nEnd recodes: {len(end_recodes)} bytes (was base64)")
    print(f"  hex: {end_recodes[:80].hex()}")

# Parse recodes to see what operations they contain
# Recodes format: sequence of opcodes with packed data
# Let's look at the opcode constants from swf_shape_to_recodes.py

# Build reverse map
opcode_names = {}
for name in dir(SHAPE_OPCODES):
    if not name.startswith('_'):
        val = getattr(SHAPE_OPCODES, name)
        if isinstance(val, int):
            opcode_names[val] = name

print(f"\nOpcode map: {opcode_names}")

def decode_recodes(data, label):
    """Decode a recodes byte buffer into human-readable operations."""
    print(f"\n--- {label} ---")
    pos = 0
    records = []
    while pos < len(data):
        if pos >= len(data):
            break
        opcode = data[pos]
        pos += 1
        name = opcode_names.get(opcode, f'UNKNOWN_0x{opcode:02X}')
        
        if opcode == getattr(SHAPE_OPCODES, 'MOVE_TO', -1):
            if pos + 8 <= len(data):
                x = struct.unpack_from('<i', data, pos)[0]
                y = struct.unpack_from('<i', data, pos+4)[0]
                pos += 8
                records.append(f"MOVE_TO({x}, {y})")
            else:
                records.append(f"MOVE_TO(truncated)")
                break
        elif opcode == getattr(SHAPE_OPCODES, 'LINE_TO', -1):
            if pos + 8 <= len(data):
                x = struct.unpack_from('<i', data, pos)[0]
                y = struct.unpack_from('<i', data, pos+4)[0]
                pos += 8
                records.append(f"LINE_TO({x}, {y})")
            else:
                records.append(f"LINE_TO(truncated)")
                break
        elif opcode == getattr(SHAPE_OPCODES, 'CURVE_TO', -1):
            if pos + 16 <= len(data):
                cx = struct.unpack_from('<i', data, pos)[0]
                cy = struct.unpack_from('<i', data, pos+4)[0]
                ax = struct.unpack_from('<i', data, pos+8)[0]
                ay = struct.unpack_from('<i', data, pos+12)[0]
                pos += 16
                records.append(f"CURVE_TO(ctrl={cx},{cy} anchor={ax},{ay})")
            else:
                records.append(f"CURVE_TO(truncated)")
                break
        elif opcode == getattr(SHAPE_OPCODES, 'FILL_STYLE', -1) or name == 'FILL_STYLE':
            # Fill style index - varies based on format
            # Try reading as uint16
            if pos + 1 <= len(data):
                # Could be 1 byte or 2 bytes depending on format
                idx = data[pos]
                pos += 1
                records.append(f"FILL_STYLE({idx})")
            else:
                records.append(f"FILL_STYLE(truncated)")
                break
        elif opcode == getattr(SHAPE_OPCODES, 'LINE_STYLE', -1) or name == 'LINE_STYLE':
            if pos + 1 <= len(data):
                idx = data[pos]
                pos += 1
                records.append(f"LINE_STYLE({idx})")
            else:
                records.append(f"LINE_STYLE(truncated)")
                break
        elif opcode == getattr(SHAPE_OPCODES, 'END_SHAPE', -1) or name == 'END_SHAPE':
            records.append(f"END_SHAPE")
            break
        elif name.startswith('FILL_STYLE'):
            # Might be a complex fill style with more data
            records.append(f"{name}")
        else:
            records.append(f"{name} (opcode={opcode})")
            # Unknown size, try to continue
    
    for r in records:
        print(f"  {r}")
    return records

decode_recodes(start_recodes, "Start Recodes")
decode_recodes(end_recodes, "End Recodes")

# Now let's also trace what parse_next2d_shape_buffer does with these recodes
print("\n\n=== TRACING parse_next2d_shape_buffer ===")
from shape_converter import parse_next2d_shape_buffer
fill_styles_start, line_styles_start, sub_paths_start = parse_next2d_shape_buffer(start_recodes)
print(f"Start: {len(fill_styles_start)} fills, {len(line_styles_start)} lines, {len(sub_paths_start)} sub_paths")
for i, sp in enumerate(sub_paths_start):
    print(f"  subpath[{i}]: fill={sp.fill_style_idx} line={sp.line_style_idx} edges={len(sp.edges)}")
    for j, e in enumerate(sp.edges[:5]):
        print(f"    edge[{j}]: type={type(e).__name__} {e}")
    if len(sp.edges) > 5:
        print(f"    ... ({len(sp.edges)} total)")

fill_styles_end, line_styles_end, sub_paths_end = parse_next2d_shape_buffer(end_recodes)
print(f"\nEnd: {len(fill_styles_end)} fills, {len(line_styles_end)} lines, {len(sub_paths_end)} sub_paths")
for i, sp in enumerate(sub_paths_end):
    print(f"  subpath[{i}]: fill={sp.fill_style_idx} line={sp.line_style_idx} edges={len(sp.edges)}")
    for j, e in enumerate(sp.edges[:5]):
        print(f"    edge[{j}]: type={type(e).__name__} {e}")
    if len(sp.edges) > 5:
        print(f"    ... ({len(sp.edges)} total)")
