"""Check what DefineFont tags exist in the RT SWF and what fonts DefineEditText references."""
import struct, zlib
from swf_binary_io import BitReader
from swf_to_n2d import read_rect

data = open('test_swfs/lloyd_rt.swf', 'rb').read()
if data[:3] == b'CWS':
    body = zlib.decompress(data[8:])
    data = data[:8] + body

pos = 8
br = BitReader(data[pos:])
nbits = br.read_ub(5)
for _ in range(4): br.read_sb(nbits)
br.align()
pos += br.byte_pos
pos += 4

fonts = {}  # cid -> info
edit_texts = {}  # cid -> info

while pos < len(data) - 2:
    tag_hdr = struct.unpack_from('<H', data, pos)[0]
    tag_type = tag_hdr >> 6
    tag_len = tag_hdr & 0x3f
    pos += 2
    if tag_len == 0x3f:
        tag_len = struct.unpack_from('<I', data, pos)[0]
        pos += 4

    tag_data = data[pos:pos+tag_len]

    # DefineFont2 (48) / DefineFont3 (75)
    if tag_type in (48, 75):
        cid = struct.unpack_from('<H', tag_data, 0)[0]
        # Parse flags
        flags = tag_data[2] if len(tag_data) > 2 else 0
        has_layout = bool(flags & 0x80)
        is_shift_jis = bool(flags & 0x40)
        is_small = bool(flags & 0x20)
        is_ansi = bool(flags & 0x10)
        wide_offsets = bool(flags & 0x08)
        wide_codes = bool(flags & 0x04)
        is_italic = bool(flags & 0x02)
        is_bold = bool(flags & 0x01)
        lang = tag_data[3] if len(tag_data) > 3 else 0
        name_len = tag_data[4] if len(tag_data) > 4 else 0
        name = tag_data[5:5+name_len].decode('latin-1', errors='replace').rstrip('\x00')
        num_glyphs = struct.unpack_from('<H', tag_data, 5+name_len)[0] if len(tag_data) > 5+name_len+1 else 0
        fonts[cid] = {
            'tag': tag_type, 'name': name, 'glyphs': num_glyphs,
            'bold': is_bold, 'italic': is_italic, 'size': tag_len
        }

    # DefineEditText (37)
    if tag_type == 37:
        cid = struct.unpack_from('<H', tag_data, 0)[0]
        br2 = BitReader(tag_data, 2)
        bounds = read_rect(br2)
        br2.align()
        flags1 = br2.read_ui8()
        flags2 = br2.read_ui8()
        has_font = bool(flags1 & 0x01)
        has_text_color = bool(flags1 & 0x04)
        has_max_length = bool(flags1 & 0x02)
        has_text = bool(flags1 & 0x80)
        word_wrap = bool(flags1 & 0x40)
        multiline = bool(flags1 & 0x20)
        has_layout = bool(flags2 & 0x20)
        html = bool(flags2 & 0x02)
        use_outlines = bool(flags2 & 0x01)

        font_id = 0
        font_height = 0
        if has_font:
            font_id = br2.read_ui16()
            font_height = br2.read_ui16()

        info = {
            'bounds': bounds, 'font_id': font_id,
            'font_height_twips': font_height,
            'font_height_px': font_height/20.0,
            'html': html, 'use_outlines': use_outlines,
            'has_font': has_font
        }

        # Read color if present
        if has_text_color:
            r = br2.read_ui8(); g = br2.read_ui8()
            b_ = br2.read_ui8(); a = br2.read_ui8()
            info['color'] = f'#{r:02x}{g:02x}{b_:02x} a={a}'

        # Skip to text
        if has_max_length:
            br2.read_ui16()
        if has_layout:
            br2.read_ui8()  # align
            br2.read_ui16(); br2.read_ui16()  # margins
            br2.read_ui16()  # indent
            br2.read_si16()  # leading

        # Variable name
        br2.align()
        var_name = br2.read_string()
        text_val = ''
        if has_text:
            text_val = br2.read_string()
        info['text'] = text_val
        edit_texts[cid] = info

print("=== DefineFont tags ===")
for cid, f in sorted(fonts.items()):
    print(f"  CID {cid}: tag={f['tag']} name='{f['name']}' glyphs={f['glyphs']} bold={f['bold']} italic={f['italic']} size={f['size']}b")

print(f"\n=== DefineEditText tags ({len(edit_texts)}) ===")
for cid, et in sorted(edit_texts.items()):
    font_info = fonts.get(et['font_id'], {})
    font_name = font_info.get('name', '???')
    print(f"  CID {cid}: font_id={et['font_id']} ('{font_name}') "
          f"size={et['font_height_px']}px html={et['html']} outlines={et['use_outlines']}")
    print(f"    text='{et['text']}'")
    print(f"    bounds={et['bounds']}")
    if 'color' in et:
        print(f"    color={et['color']}")
