#!/usr/bin/env python3
"""
Diagnose text issues in menu_characters.ssf roundtrip.
Compares original vs roundtripped DefineEditText tags and PlaceObject positioning.
"""
import os, struct, sys, tempfile, zlib, json

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, APP_DIR)

import swf_to_n2d
import compile_n2d

def parse_swf(data):
    magic = data[:3]
    if magic == b'CWS':
        data = data[:8] + zlib.decompress(data[8:])
    elif magic == b'ZWS':
        import lzma
        data = data[:8] + lzma.decompress(data[12:])
    nbits = (data[8] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_end = 8 + (total_bits + 7) // 8
    pos = rect_end + 4
    tags = []
    while pos < len(data):
        if pos + 2 > len(data): break
        h = struct.unpack_from('<H', data, pos)[0]
        tt = h >> 6; ln = h & 0x3F; hdr = 2
        if ln == 0x3F:
            if pos + 6 > len(data): break
            ln = struct.unpack_from('<I', data, pos + 2)[0]; hdr = 6
        body = data[pos + hdr: pos + hdr + ln]
        tags.append((tt, body))
        pos += hdr + ln
        if tt == 0: break
    return tags

def skip_rect(buf, off):
    nbits = (buf[off] >> 3) & 0x1f
    total = 5 + nbits * 4
    return off + (total + 7) // 8

def parse_edit_text(body):
    """Parse DefineEditText body into a dict of key fields."""
    if len(body) < 6: return None
    cid = struct.unpack_from('<H', body, 0)[0]
    b = body[2:]  # after charID
    off = skip_rect(b, 0)
    
    flags1 = b[off]; off += 1
    flags2 = b[off]; off += 1
    
    has_font = bool(flags1 & 0x01)
    has_max_length = bool(flags1 & 0x02)
    has_color = bool(flags1 & 0x04)
    read_only = bool(flags1 & 0x08)
    password = bool(flags1 & 0x10)
    multiline = bool(flags1 & 0x20)
    word_wrap = bool(flags1 & 0x40)
    has_text = bool(flags1 & 0x80)
    
    use_outlines = bool(flags2 & 0x01)
    html = bool(flags2 & 0x02)
    was_static = bool(flags2 & 0x04)
    border = bool(flags2 & 0x08)
    no_select = bool(flags2 & 0x10)
    has_layout = bool(flags2 & 0x20)
    auto_size = bool(flags2 & 0x40)
    has_font_class = bool(flags2 & 0x80)
    
    font_id = None
    text_height = None
    if has_font:
        font_id = b[off] | (b[off+1] << 8); off += 2
        text_height = b[off] | (b[off+1] << 8); off += 2
    
    color = None
    if has_color:
        color = (b[off], b[off+1], b[off+2], b[off+3])
        off += 4
    
    max_length = None
    if has_max_length:
        max_length = b[off] | (b[off+1] << 8); off += 2
    
    align = indent = leading = left_margin = right_margin = None
    if has_layout:
        align = b[off]; off += 1
        left_margin = struct.unpack_from('<H', b, off)[0]; off += 2
        right_margin = struct.unpack_from('<H', b, off)[0]; off += 2
        indent = struct.unpack_from('<H', b, off)[0]; off += 2
        leading = struct.unpack_from('<h', b, off)[0]; off += 2
    
    # Variable name (null-terminated)
    var_end = b.index(0, off) if 0 in b[off:] else len(b)
    var_name = b[off:var_end].decode('utf-8', errors='replace')
    off = var_end + 1
    
    text = None
    if has_text and off < len(b):
        txt_end = b.index(0, off) if 0 in b[off:] else len(b)
        text = b[off:txt_end].decode('utf-8', errors='replace')
        off = txt_end + 1
    
    return {
        'charId': cid,
        'flags1': flags1, 'flags2': flags2,
        'hasFont': has_font, 'hasText': has_text, 'html': html,
        'hasColor': has_color, 'hasLayout': has_layout,
        'multiline': multiline, 'wordWrap': word_wrap,
        'readOnly': read_only, 'border': border,
        'noSelect': no_select, 'autoSize': auto_size,
        'fontId': font_id, 'textHeight': text_height,
        'color': color, 'maxLength': max_length,
        'variableName': var_name,
        'text': text,
        'align': align,
        'bodyLen': len(body),
    }

def parse_place_object(tt, body):
    """Extract key fields from PlaceObject2/3."""
    if tt == 26 and len(body) >= 3:
        flags = body[0]
        depth = struct.unpack_from('<H', body, 1)[0]
        char_id = struct.unpack_from('<H', body, 3)[0] if (flags & 0x02) else None
        # Name
        name = None
        if flags & 0x20:
            off = 3
            if flags & 0x02: off += 2
            if flags & 0x04:  # matrix - skip it
                # can't easily skip matrix, so get name from raw scan
                pass
            # Scan for name - it's after matrix and cxform
            # Just extract what we can
        return {'depth': depth, 'charId': char_id, 'flags': flags}
    elif tt == 70 and len(body) >= 4:
        flags1 = body[0]; flags2 = body[1]
        depth = struct.unpack_from('<H', body, 2)[0]
        char_id = struct.unpack_from('<H', body, 4)[0] if (flags1 & 0x02) else None
        return {'depth': depth, 'charId': char_id, 'flags1': flags1, 'flags2': flags2}
    return None

def roundtrip_file(swf_path):
    """Roundtrip and return both tags."""
    with open(swf_path, 'rb') as f:
        orig_data = f.read()
    
    with tempfile.TemporaryDirectory(prefix='diag_') as tmp:
        n2d_path = os.path.join(tmp, 'project.n2d')
        rt_path = os.path.join(tmp, 'rt.swf')
        
        header, tags = swf_to_n2d.parse_swf(orig_data)
        builder = swf_to_n2d.N2DBuilder(header, name='test')
        builder.catalog_swf_tags(tags)
        try:
            scripts, frame_scripts = swf_to_n2d.decompile_all_scripts(builder.global_raw_tags)
            builder.frame_scripts = frame_scripts
            if scripts: builder.scripts.extend(scripts)
        except: pass
        builder.build_all()
        builder.build_main_timeline(tags)
        builder._embed_bitmap_data_in_recodes()
        n2d = builder.to_n2d_json()
        swf_to_n2d.save_n2d(n2d, n2d_path)
        
        compiler = compile_n2d.N2DCompiler(n2d_path, tmp, rt_path, sdk_path=None)
        compiler.compile()
        
        with open(rt_path, 'rb') as f:
            rt_data = f.read()
    
    return parse_swf(orig_data), parse_swf(rt_data)

# ── Main ──

swf_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src",
    r"Super Smash Flash 2 Beta v1.4.0.1\data\menu\menu_characters.ssf")

print(f"Analyzing: {swf_path}")
print()

with open(swf_path, 'rb') as f:
    orig_data = f.read()

orig_tags = parse_swf(orig_data)

# Count text-related tags
edit_texts_orig = [(tt, body) for tt, body in orig_tags if tt == 37]
texts_orig = [(tt, body) for tt, body in orig_tags if tt in (11, 33)]

print(f"Original SWF: {len(orig_tags)} tags total")
print(f"  DefineEditText (37): {len(edit_texts_orig)}")
print(f"  DefineText/2 (11/33): {len(texts_orig)}")
print()

# Parse all EditText fields from original
print("=== DefineEditText in ORIGINAL ===")
html_count = 0
has_text_count = 0
for tt, body in edit_texts_orig:
    info = parse_edit_text(body)
    if info:
        if info['html']: html_count += 1
        if info['hasText']: has_text_count += 1
        flags_str = []
        if info['html']: flags_str.append('HTML')
        if info['hasText']: flags_str.append('HasText')
        if info['multiline']: flags_str.append('Multiline')
        if info['wordWrap']: flags_str.append('WordWrap')
        if info['readOnly']: flags_str.append('ReadOnly')
        text_preview = (info['text'] or '')[:80]
        var_preview = info['variableName'][:40] if info['variableName'] else ''
        print(f"  cid={info['charId']:4d}  [{','.join(flags_str):30s}]  "
              f"var={var_preview!r:20s}  text={text_preview!r}")

print(f"\n  Summary: {html_count} HTML, {has_text_count} have text, "
      f"{len(edit_texts_orig)} total")

# Now roundtrip
print("\n\n=== ROUNDTRIPPING ===")
orig_tags, rt_tags = roundtrip_file(swf_path)

edit_texts_rt = [(tt, body) for tt, body in rt_tags if tt == 37]
texts_rt = [(tt, body) for tt, body in rt_tags if tt in (11, 33)]

print(f"\nRoundtripped SWF: {len(rt_tags)} tags total")
print(f"  DefineEditText (37): {len(edit_texts_rt)}")
print(f"  DefineText/2 (11/33): {len(texts_rt)}")

# Compare flags
print("\n=== DefineEditText in ROUNDTRIPPED ===")
rt_html_count = 0
rt_has_text_count = 0
for tt, body in edit_texts_rt:
    info = parse_edit_text(body)
    if info:
        if info['html']: rt_html_count += 1
        if info['hasText']: rt_has_text_count += 1
        flags_str = []
        if info['html']: flags_str.append('HTML')
        if info['hasText']: flags_str.append('HasText')
        if info['multiline']: flags_str.append('Multiline')
        if info['wordWrap']: flags_str.append('WordWrap')
        if info['readOnly']: flags_str.append('ReadOnly')
        text_preview = (info['text'] or '')[:80]
        var_preview = info['variableName'][:40] if info['variableName'] else ''
        print(f"  cid={info['charId']:4d}  [{','.join(flags_str):30s}]  "
              f"var={var_preview!r:20s}  text={text_preview!r}")

print(f"\n  Summary: {rt_html_count} HTML, {rt_has_text_count} have text, "
      f"{len(edit_texts_rt)} total")

# Compare byte-for-byte
print("\n\n=== BYTE COMPARISON (body after charID) ===")
orig_bodies = sorted(body[2:] for tt, body in orig_tags if tt == 37)
rt_bodies = sorted(body[2:] for tt, body in rt_tags if tt == 37)
mismatches = 0
for i, (ob, rb) in enumerate(zip(orig_bodies, rt_bodies)):
    if ob != rb:
        mismatches += 1
        if mismatches <= 5:
            print(f"  EditText #{i}: MISMATCH  orig={len(ob)}B  rt={len(rb)}B")
            # Find first diff
            for j in range(min(len(ob), len(rb))):
                if ob[j] != rb[j]:
                    print(f"    First diff at byte {j}: orig=0x{ob[j]:02X} rt=0x{rb[j]:02X}")
                    break
print(f"\n  {mismatches}/{len(orig_bodies)} EditText bodies differ")

# Check DefineText bodies too
print("\n=== DefineText/Text2 BYTE COMPARISON ===")
for tag_type in (11, 33):
    orig_t = sorted(body[2:] for tt, body in orig_tags if tt == tag_type)
    rt_t = sorted(body[2:] for tt, body in rt_tags if tt == tag_type)
    if not orig_t and not rt_t: continue
    mm = sum(1 for ob, rb in zip(orig_t, rt_t) if ob != rb)
    extra = abs(len(orig_t) - len(rt_t))
    print(f"  Tag {tag_type}: orig={len(orig_t)}, rt={len(rt_t)}, mismatches={mm}, extra={extra}")
