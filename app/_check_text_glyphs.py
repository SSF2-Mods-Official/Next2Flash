"""Decode the actual glyph data from DefineText CID 164 to understand spacing."""
import struct, zlib, base64, zipfile, msgpack
from swf_binary_io import BitReader

# Load N2D to get rawTagBody
with zipfile.ZipFile('test_swfs/lloyd.n2d') as zf:
    with zf.open('project.msgpack') as f:
        project = msgpack.unpack(f, raw=False)

text_lib = None
for lib in project.get('libraries', []):
    if isinstance(lib, dict) and lib.get('type') == 'text' and lib.get('swfCharId') == 164:
        text_lib = lib
        break

raw_body = base64.b64decode(text_lib['rawTagBody'])
print(f"rawTagBody: {len(raw_body)} bytes")

# Parse DefineText (tag 11) binary — rawTagBody does NOT include charId
# So we parse from the beginning which is the bounds rect
br = BitReader(raw_body, 0)

# Bounds RECT
nb = br.read_ub(5)
xmin = br.read_sb(nb)
xmax = br.read_sb(nb)
ymin = br.read_sb(nb)
ymax = br.read_sb(nb)
br.align()
print(f"Bounds: xmin={xmin} xmax={xmax} ymin={ymin} ymax={ymax}")

# Matrix
has_scale = br.read_ub(1)
if has_scale:
    nb2 = br.read_ub(5)
    sx = br.read_sb(nb2)
    sy = br.read_sb(nb2)
    print(f"Scale: {sx}/{65536} {sy}/{65536}")
has_rotate = br.read_ub(1)
if has_rotate:
    nb2 = br.read_ub(5)
    r0 = br.read_sb(nb2)
    r1 = br.read_sb(nb2)
nb2 = br.read_ub(5)
tx = br.read_sb(nb2)
ty = br.read_sb(nb2)
print(f"Translate: {tx/20.0}, {ty/20.0}")
br.align()

glyph_bits = br.read_ui8()
advance_bits = br.read_ui8()
print(f"GlyphBits={glyph_bits} AdvanceBits={advance_bits}")

# Now load font code tables from the OG SWF
from swf_to_n2d import parse_swf, TAG_DEFINE_FONT2, TAG_DEFINE_FONT3

OG_PATH = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf'
with open(OG_PATH, 'rb') as f:
    swf_data = f.read()

header, tags = parse_swf(swf_data)

# Find fonts and build code tables
font_code_tables = {}
for tag in tags:
    if tag.tag_type in (48, 75):  # DefineFont2/DefineFont3
        fbr = BitReader(tag.data, 0)
        fid = fbr.read_ui16()
        flags = fbr.read_ui8()
        has_layout = bool(flags & 0x80)
        shift_jis = bool(flags & 0x40)
        small_text = bool(flags & 0x20)
        ansi = bool(flags & 0x10)
        wide_offsets = bool(flags & 0x08)
        wide_codes = bool(flags & 0x04)
        italic = bool(flags & 0x02)
        bold = bool(flags & 0x01)
        _lang = fbr.read_ui8()
        name_len = fbr.read_ui8()
        name = fbr.data[fbr.byte_pos:fbr.byte_pos+name_len]
        fbr.byte_pos += name_len
        try:
            fname = name.rstrip(b'\x00').decode('latin-1')
        except:
            fname = '???'
        num_glyphs = fbr.read_ui16()
        # Skip offset table
        if wide_offsets:
            fbr.byte_pos += (num_glyphs + 1) * 4
        else:
            fbr.byte_pos += (num_glyphs + 1) * 2
        # Skip glyph shapes
        # Actually the offsets tell us where glyph shapes end
        # But we need to get to the code table...
        # Simpler: use swf_to_n2d's font parsing
        pass

# Use the full importer to get font code tables
from swf_to_n2d import N2DBuilder
builder = N2DBuilder.__new__(N2DBuilder)
builder.font_code_tables = {}
builder.font_names = {}
builder.font_attrs = {}

# Parse font tags
for tag in tags:
    if tag.tag_type in (48, 75):
        fbr = BitReader(tag.data, 0)
        fid = fbr.read_ui16()
        print(f"\nFont CID {fid}:")
        # Use the actual font parser
        from swf_to_n2d import parse_define_font3_code_table, parse_define_font3_name
        from swf_to_n2d import parse_define_font2_code_table, parse_define_font2_name
        if tag.tag_type == 75:  # DefineFont3
            fid, code_table = parse_define_font3_code_table(tag.data)
            _, font_name, is_bold, is_italic = parse_define_font3_name(tag.data)
        else:  # DefineFont2
            fid, code_table = parse_define_font2_code_table(tag.data)
            _, font_name, is_bold, is_italic = parse_define_font2_name(tag.data)
        font_code_tables[fid] = code_table
        print(f"  Name: {font_name}, Bold: {is_bold}, Italic: {is_italic}")
        print(f"  Code table ({len(code_table)} glyphs): {code_table[:30]}...")

# Now re-parse the text records with proper code tables
print(f"\n\n=== Parsing DefineText CID 164 glyph records ===")
br2 = BitReader(raw_body, 0)
# Skip bounds
nb = br2.read_ub(5)
for _ in range(4): br2.read_sb(nb)
br2.align()
# Skip matrix
has_s = br2.read_ub(1)
if has_s:
    nb2 = br2.read_ub(5)
    br2.read_sb(nb2); br2.read_sb(nb2)
has_r = br2.read_ub(1)
if has_r:
    nb2 = br2.read_ub(5)
    br2.read_sb(nb2); br2.read_sb(nb2)
nb2 = br2.read_ub(5)
br2.read_sb(nb2); br2.read_sb(nb2)
br2.align()
gb = br2.read_ui8()
ab = br2.read_ui8()

current_font_id = None
record_num = 0
while True:
    flags = br2.read_ui8()
    if flags == 0:
        break
    
    has_font = bool(flags & 0x08)
    has_color = bool(flags & 0x04)
    has_y = bool(flags & 0x02)
    has_x = bool(flags & 0x01)
    
    if has_font:
        current_font_id = br2.read_ui16()
    if has_color:
        r = br2.read_ui8(); g = br2.read_ui8(); b = br2.read_ui8()
        # Tag 11 = no alpha
    if has_y:
        y_off = br2.read_si16()
    else:
        y_off = None
    if has_x:
        x_off = br2.read_si16()
    else:
        x_off = None
    if has_font:
        height = br2.read_ui16()
    else:
        height = None
    
    glyph_count = br2.read_ui8()
    glyphs = []
    for _ in range(glyph_count):
        gi = br2.read_ub(gb)
        ga = br2.read_sb(ab)
        ct = font_code_tables.get(current_font_id, [])
        ch = ct[gi] if gi < len(ct) else '?'
        glyphs.append((gi, ga, ch))
    br2.align()
    
    record_num += 1
    print(f"  Record {record_num}: font={current_font_id} height={height} x_off={x_off} y_off={y_off}")
    for gi, ga, ch in glyphs:
        print(f"    glyph[{gi}]='{ch}' advance={ga}")
