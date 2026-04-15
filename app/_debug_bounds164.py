"""Debug bounds computation for CID 164 DefineText."""
import struct, zlib
from swf_binary_io import BitReader
from swf_to_n2d import read_rect, read_matrix

# Parse original SWF
data = open(r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf", 'rb').read()
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

# Find DefineText tag for CID 164
while pos < len(data) - 2:
    tag_hdr = struct.unpack_from('<H', data, pos)[0]
    tag_type = tag_hdr >> 6
    tag_len = tag_hdr & 0x3f
    pos += 2
    if tag_len == 0x3f:
        tag_len = struct.unpack_from('<I', data, pos)[0]
        pos += 4
    if tag_type in (11, 33):
        cid = struct.unpack_from('<H', data, pos)[0]
        if cid == 164:
            tag_data = data[pos:pos+tag_len]
            br2 = BitReader(tag_data, 2)  # skip charID (2 bytes)
            bounds = read_rect(br2)
            br2.align()
            print(f"DefineText CID 164 bounds (twips): {bounds}")
            print(f"  Width (px): {(bounds['xMax'] - bounds['xMin'])/20}")
            print(f"  Height (px): {(bounds['yMax'] - bounds['yMin'])/20}")
            
            # Parse matrix
            mat = read_matrix(br2)
            br2.align()
            print(f"Matrix: {mat}")
            
            # Parse glyph/advance bits
            glyph_bits = br2.read_ui8()
            advance_bits = br2.read_ui8()
            print(f"GlyphBits={glyph_bits}, AdvanceBits={advance_bits}")
            
            # Parse text records
            total_advance = 0
            max_x = 0
            current_x = 0
            all_advances = []
            while True:
                flags = br2.read_ui8()
                if flags == 0:
                    break
                has_font = bool(flags & 0x08)
                has_color = bool(flags & 0x04)
                has_y_off = bool(flags & 0x02)
                has_x_off = bool(flags & 0x01)
                if has_font:
                    fid = br2.read_ui16()
                if has_color:
                    br2.read_ui8(); br2.read_ui8(); br2.read_ui8()
                    if tag_type == 33:
                        br2.read_ui8()
                if has_y_off:
                    y = br2.read_si16()
                    print(f"  Y offset: {y}")
                if has_x_off:
                    current_x = br2.read_si16()
                    total_advance = 0
                    print(f"  X offset: {current_x}")
                if has_font:
                    h = br2.read_ui16()
                    print(f"  Font: id={fid}, height={h}")
                gc = br2.read_ui8()
                print(f"  {gc} glyphs:")
                for _ in range(gc):
                    gi = br2.read_ub(glyph_bits)
                    ga = br2.read_sb(advance_bits)
                    total_advance += ga
                    all_advances.append(ga)
                br2.align()
                record_end = current_x + total_advance
                if record_end > max_x:
                    max_x = record_end
            
            print(f"\nTotal advance sum: {sum(all_advances)} twips = {sum(all_advances)/20} px")
            print(f"max_x: {max_x} twips = {max_x/20} px")
            print(f"current_x start: measured above")
            print(f"Individual advances: {all_advances}")
            break
    pos += tag_len
