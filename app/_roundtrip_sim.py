"""
Simulate roundtrip for shapes 183, 185, 188, 306:
1. Parse original SWF → recodes (what import produces)
2. Show N2D stored recodes
3. Re-parse recodes → fill_styles, line_styles, sub_paths
4. Re-build shape SWF tag bytes
5. Compare original tag bytes vs rebuilt tag bytes
"""
import struct, sys, os, io, zipfile, msgpack

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swf_shape_to_recodes import parse_define_shape_to_recodes
from shape_converter import parse_next2d_shape_buffer, build_define_shape3, build_define_shape4

ORIG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf"
N2D  = "test_swfs/lloyd.n2d"
OUT  = "_roundtrip_sim_output.txt"
TARGET_CIDS = [183, 185, 188, 306]

SHAPE_TAG_IDS = {2, 22, 32, 83}

def read_swf_data(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:3] == b'CWS':
        import zlib
        data = data[:8] + zlib.decompress(data[8:])
    elif data[:3] == b'ZWS':
        import lzma
        data = data[:8] + lzma.decompress(data[12:])
    return data

def parse_tags(data):
    pos = 8
    nbits = (data[pos] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    pos += rect_bytes + 4

    tags = []
    while pos < len(data) - 1:
        tag_code_and_length = struct.unpack_from('<H', data, pos)[0]
        tag_type = tag_code_and_length >> 6
        length = tag_code_and_length & 0x3F
        pos += 2
        if length == 0x3F:
            length = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        body = data[pos:pos+length]
        cid = None
        if tag_type in SHAPE_TAG_IDS and len(body) >= 2:
            cid = struct.unpack_from('<H', body, 0)[0]
        tags.append((tag_type, cid, body))
        pos += length
        if tag_type == 0:
            break
    return tags

f = open(OUT, 'w')

# Parse original SWF
orig_data = read_swf_data(ORIG)
orig_tags = parse_tags(orig_data)
orig_shapes = {}
for tag_type, cid, body in orig_tags:
    if tag_type in SHAPE_TAG_IDS and cid is not None:
        if cid not in orig_shapes:
            orig_shapes[cid] = (tag_type, body)

# Parse N2D
with zipfile.ZipFile(N2D) as z:
    with z.open("project.msgpack") as mf:
        project = msgpack.unpack(mf, raw=False)

libs = project.get('libraries', [])
n2d_by_cid = {}
for lib in libs:
    if lib.get('type') == 'shape' and not lib.get('endRecodes'):
        cid = lib.get('swfCharId')
        if cid is not None:
            n2d_by_cid[cid] = lib

for cid in TARGET_CIDS:
    f.write(f"\n{'='*70}\n")
    f.write(f"  SHAPE CID {cid}\n")
    f.write(f"{'='*70}\n\n")

    # --- Step 1: Original SWF shape ---
    if cid not in orig_shapes:
        f.write(f"  NOT FOUND in original SWF\n\n")
        continue
    o_tag_type, o_body = orig_shapes[cid]
    f.write(f"  ORIGINAL: tag={o_tag_type}, size={len(o_body)} bytes\n")
    f.write(f"  ORIGINAL hex: {o_body.hex()}\n\n")

    # --- Step 2: Parse original shape to recodes (what the importer does) ---
    try:
        # parse_define_shape_to_recodes expects body AFTER 2-byte charId
        body_after_cid = o_body[2:]
        import_result = parse_define_shape_to_recodes(o_tag_type, body_after_cid)
        # Returns (recodes, bounds, has_bitmap_fill) tuple
        if isinstance(import_result, tuple):
            import_recodes = import_result[0]
            import_bounds = import_result[1]
        else:
            import_recodes = import_result.get("recodes", [])
            import_bounds = import_result.get("bounds", {})
        raw_tag_type = import_result.get("rawTagType", o_tag_type)
        f.write(f"  IMPORT: bounds={import_bounds}, rawTagType={raw_tag_type}\n")
        f.write(f"  IMPORT recodes ({len(import_recodes)} items): {import_recodes}\n\n")
    except Exception as e:
        f.write(f"  IMPORT PARSE ERROR: {e}\n\n")
        import_recodes = None

    # --- Step 3: N2D stored recodes ---
    if cid in n2d_by_cid:
        n2d_lib = n2d_by_cid[cid]
        n2d_recodes = n2d_lib.get("recodes", [])
        n2d_bounds = n2d_lib.get("bounds", {})
        n2d_raw_tag = n2d_lib.get("rawTagType")
        f.write(f"  N2D: bounds={n2d_bounds}, rawTagType={n2d_raw_tag}\n")
        f.write(f"  N2D recodes ({len(n2d_recodes)} items): {n2d_recodes}\n\n")

        # --- Step 4: Compare import recodes vs N2D recodes ---
        if import_recodes is not None:
            if import_recodes == n2d_recodes:
                f.write(f"  IMPORT vs N2D: IDENTICAL\n")
            else:
                f.write(f"  IMPORT vs N2D: DIFFER\n")
                f.write(f"    Import len={len(import_recodes)}, N2D len={len(n2d_recodes)}\n")
                # Find first difference
                for i in range(min(len(import_recodes), len(n2d_recodes))):
                    if import_recodes[i] != n2d_recodes[i]:
                        f.write(f"    First diff at index {i}: import={import_recodes[i]}, n2d={n2d_recodes[i]}\n")
                        break

        # --- Step 5: Rebuild shape from N2D recodes ---
        f.write(f"\n  --- REBUILD from N2D recodes ---\n")
        try:
            fill_styles, line_styles, sub_paths = parse_next2d_shape_buffer(n2d_recodes)
            f.write(f"  Parsed: fills={len(fill_styles)}, lines={len(line_styles)}, paths={len(sub_paths)}\n")
            for i, sp in enumerate(sub_paths):
                f.write(f"    path[{i}]: fill_idx={sp.fill_style_idx}, line_idx={sp.line_style_idx}, "
                        f"start=({sp.start_x},{sp.start_y}), edges={len(sp.edges)}\n")
                for j, e in enumerate(sp.edges):
                    f.write(f"      edge[{j}]: {type(e).__name__}")
                    if hasattr(e, 'x') and hasattr(e, 'y') and not hasattr(e, 'cx'):
                        f.write(f" ({e.x},{e.y})")
                    elif hasattr(e, 'cx'):
                        f.write(f" ctrl=({e.cx},{e.cy}) anc=({e.x},{e.y})")
                    f.write("\n")

            # Build DefineShape3
            tag_bytes_3 = build_define_shape3(999, fill_styles, line_styles, sub_paths, n2d_bounds)
            f.write(f"\n  Rebuilt DefineShape3: {len(tag_bytes_3)} bytes\n")
            f.write(f"  Rebuilt hex: {tag_bytes_3.hex()}\n")

            # Compare to original
            # Strip tag header from rebuilt (first 6 bytes: tag code+length, or 2 bytes short form)
            # The original body starts after the tag header
            f.write(f"\n  ORIGINAL body size: {len(o_body)} bytes\n")
            f.write(f"  REBUILT tag size: {len(tag_bytes_3)} bytes\n")

        except Exception as e:
            import traceback
            f.write(f"  REBUILD ERROR: {e}\n")
            traceback.print_exc(file=f)
    else:
        f.write(f"  NOT FOUND in N2D\n\n")

f.close()
print(f"Done. Output: {OUT} ({os.path.getsize(OUT)} bytes)")
