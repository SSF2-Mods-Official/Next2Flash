"""Check fonts in RT SWF and whether DefineEditText references them."""
import struct, zlib

data = open('test_swfs/lloyd_rt.swf', 'rb').read()
if data[:3] == b'CWS':
    body = zlib.decompress(data[8:])
    data = data[:8] + body

# Skip header 
from swf_binary_io import BitReader
pos = 8
br = BitReader(data[pos:])
nbits = br.read_ub(5)
for _ in range(4): br.read_sb(nbits)
br.align()
pos += br.byte_pos
pos += 4

fonts = {}
edit_texts = []

while pos < len(data) - 2:
    tag_hdr = struct.unpack_from('<H', data, pos)[0]
    tag_type = tag_hdr >> 6
    tag_len = tag_hdr & 0x3f
    pos += 2
    if tag_len == 0x3f:
        tag_len = struct.unpack_from('<I', data, pos)[0]
        pos += 4
    td = data[pos:pos+tag_len]
    
    if tag_type in (48, 75) and len(td) > 6:
        cid = struct.unpack_from('<H', td, 0)[0]
        name_len = td[4]
        name = td[5:5+name_len].decode('latin-1', errors='replace').rstrip('\x00')
        ng = struct.unpack_from('<H', td, 5+name_len)[0] if len(td) > 5+name_len+1 else 0
        flags = td[2]
        fonts[cid] = {'name': name, 'glyphs': ng, 'tag': tag_type,
                       'bold': bool(flags & 1), 'italic': bool(flags & 2)}

    if tag_type == 37 and len(td) > 4:
        cid = struct.unpack_from('<H', td, 0)[0]
        # Find font_id: after bounds rect + 2 flag bytes
        # Just search for the text content
        text = ''
        # Text is null-terminated at end of tag
        if td[-1] == 0 and len(td) > 10:
            # Find second-to-last null
            end = len(td) - 1
            start = td.rfind(b'\x00', 0, end)
            if start >= 0:
                text = td[start+1:end].decode('utf-8', errors='replace')
        
        # Get font_id from bytes after flags (rough: skip bounds + 2 flag bytes)
        # Flags1 bit 0 = hasFont; if so, fontID is next UI16
        # Parse bounds rect to find where flags start
        br2 = BitReader(td, 2)
        nbits2 = br2.read_ub(5)
        for _ in range(4): br2.read_sb(nbits2)
        br2.align()
        f1 = br2.read_ui8()
        f2 = br2.read_ui8()
        font_id = 0
        font_h = 0
        if f1 & 0x01:  # hasFont
            font_id = br2.read_ui16()
            font_h = br2.read_ui16()
        edit_texts.append({'cid': cid, 'font_id': font_id, 'font_h': font_h,
                          'text': text, 'html': bool(f2 & 0x02),
                          'outlines': bool(f2 & 0x01)})
    pos += tag_len

print("=== DefineFont tags ===")
for cid, f in sorted(fonts.items()):
    print(f"  CID {cid}: tag={f['tag']} name='{f['name']}' glyphs={f['glyphs']} bold={f['bold']} italic={f['italic']}")

print(f"\n=== DefineEditText tags ({len(edit_texts)}) ===")
for et in edit_texts:
    fn = fonts.get(et['font_id'], {}).get('name', 'NOT_FOUND')
    fg = fonts.get(et['font_id'], {}).get('glyphs', '?')
    print(f"  CID {et['cid']}: font={et['font_id']}('{fn}' {fg}gl) "
          f"h={et['font_h']/20:.1f}px html={et['html']} outlines={et['outlines']}")
    print(f"    text='{et['text']}'")
