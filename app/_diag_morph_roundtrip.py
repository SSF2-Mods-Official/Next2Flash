#!/usr/bin/env python3
"""Diagnostic: morph shape roundtrip — trace fill0/fill1 through import→export."""
import sys, os, struct, io
sys.path.insert(0, os.path.dirname(__file__))

from swf_shape_to_recodes import parse_define_morph_shape_to_recodes
from shape_converter import (
    parse_next2d_shape_buffer, build_define_morph_shape,
    _encode_morph_shape_edges
)
from swf_binary_io import BitReader

def read_swf_tags(path):
    """Read SWF and yield (tag_type, body) for each tag."""
    with open(path, 'rb') as f:
        data = f.read()
    sig = data[:3]
    rest = data[8:]
    if sig in (b'CWS', b'ZWS'):
        import zlib
        rest = zlib.decompress(rest)
    # Skip RECT properly
    br = BitReader(rest, 0)
    nbits = br.read_ub(5)
    for _ in range(4):
        br.read_sb(nbits)
    br.align()
    pos = br.byte_pos + 4  # skip frame_rate(2) + frame_count(2)
    while pos < len(rest):
        tag_code_and_len = struct.unpack_from('<H', rest, pos)[0]
        pos += 2
        tag_type = tag_code_and_len >> 6
        length = tag_code_and_len & 0x3F
        if length == 0x3F:
            length = struct.unpack_from('<I', rest, pos)[0]
            pos += 4
        body = rest[pos:pos+length]
        pos += length
        yield tag_type, body
        if tag_type == 0:
            break

def check_encoded_fill_usage(label, data):
    """Parse encoded shape record bytes to check fill0/fill1 usage."""
    br2 = BitReader(data, 0)
    fb = br2.read_ub(4)
    lb = br2.read_ub(4)
    print(f"  {label}: fill_bits={fb}, line_bits={lb}")
    while br2.remaining > 6:
        tf = br2.read_ub(1)
        if tf == 1:
            st2 = br2.read_ub(1)
            nbe = br2.read_ub(4) + 2
            if st2:
                gen = br2.read_ub(1)
                if gen:
                    br2.read_sb(nbe); br2.read_sb(nbe)
                else:
                    br2.read_ub(1); br2.read_sb(nbe)
            else:
                br2.read_sb(nbe); br2.read_sb(nbe)
                br2.read_sb(nbe); br2.read_sb(nbe)
        else:
            flags = br2.read_ub(5)
            if flags == 0:
                break
            has_move = flags & 1
            has_f0 = (flags >> 1) & 1
            has_f1 = (flags >> 2) & 1
            has_line = (flags >> 3) & 1
            if has_move:
                mb = br2.read_ub(5)
                br2.read_sb(mb); br2.read_sb(mb)
            if has_f0:
                f0v = br2.read_ub(fb) if fb else 0
                print(f"    {label} StyleChange: fill0={f0v}")
            if has_f1:
                f1v = br2.read_ub(fb) if fb else 0
                print(f"    {label} StyleChange: fill1={f1v}")
            if has_line:
                br2.read_ub(lb)

def diagnose_morph_swf(swf_path):
    print(f"=== Diagnosing morph roundtrip: {swf_path} ===\n")
    
    for tag_type, body in read_swf_tags(swf_path):
        if tag_type not in (46, 84):
            continue
        char_id = struct.unpack_from('<H', body, 0)[0]
        body_after_id = body[2:]
        print(f"Found tag {tag_type} (DefineMorphShape{'2' if tag_type==84 else ''}), charId={char_id}")
        
        # === STEP 1: Import to N2D recodes ===
        print("\n--- Step 1: Import SWF → N2D recodes ---")
        start_recodes, start_bounds, end_recodes, end_bounds, has_bmp = \
            parse_define_morph_shape_to_recodes(tag_type, body_after_id, {})
        
        print(f"  start_recodes: {len(start_recodes)} entries")
        print(f"    First 30: {start_recodes[:30]}")
        print(f"  end_recodes: {len(end_recodes)} entries")
        print(f"    First 30: {end_recodes[:30]}")
        print(f"  start_bounds: {start_bounds}")
        print(f"  end_bounds: {end_bounds}")
        
        # === STEP 2: Parse recodes for export ===
        print("\n--- Step 2: Parse recodes for export ---")
        s_fills, s_lines, s_paths = parse_next2d_shape_buffer(start_recodes)
        e_fills, e_lines, e_paths = parse_next2d_shape_buffer(end_recodes)
        
        print(f"  s_fills: {len(s_fills)}, s_lines: {len(s_lines)}, s_paths: {len(s_paths)}")
        for i, sp in enumerate(s_paths):
            print(f"    s_path[{i}]: fill_idx={sp.fill_style_idx}, line_idx={sp.line_style_idx}, "
                  f"start=({sp.start_x},{sp.start_y}), edges={len(sp.edges)}")
        
        print(f"  e_fills: {len(e_fills)}, e_lines: {len(e_lines)}, e_paths: {len(e_paths)}")
        for i, sp in enumerate(e_paths):
            print(f"    e_path[{i}]: fill_idx={sp.fill_style_idx}, line_idx={sp.line_style_idx}, "
                  f"start=({sp.start_x},{sp.start_y}), edges={len(sp.edges)}")
        
        # === STEP 3: Encode morph edges and check fill0/fill1 ===
        print("\n--- Step 3: Encode morph edges (current code) ---")
        start_edge_bytes = _encode_morph_shape_edges(s_fills, s_lines, s_paths)
        end_edge_bytes = _encode_morph_shape_edges(e_fills, e_lines, e_paths)
        
        check_encoded_fill_usage("Start", start_edge_bytes)
        check_encoded_fill_usage("End", end_edge_bytes)
        
        # === DIAGNOSIS ===
        print("\n--- DIAGNOSIS ---")
        print("Regular _encode_shape_records uses: has_fill1 = sp.fill_style_idx > 0 (fill1, flag 0x04)")
        print("Morph _encode_morph_shape_edges uses: has_fill0 = sp.fill_style_idx > 0 (fill0, flag 0x02)")
        print("Since fill_merge converts all edges to fill1 convention,")
        print("writing them as fill0 puts fills on the WRONG side → shapes appear empty!")
        print("FIX: Change morph encoder to use fill1 instead of fill0.")

if __name__ == '__main__':
    swf_path = sys.argv[1] if len(sys.argv) > 1 else 'test_swfs/test10_morph.swf'
    if not os.path.exists(swf_path):
        print(f"SWF not found: {swf_path}")
        print("Run: python make_test_swfs.py")
        sys.exit(1)
    diagnose_morph_swf(swf_path)
