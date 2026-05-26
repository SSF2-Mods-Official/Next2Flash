"""Quick test: convert bomberman.ssf fonts to TTF."""
import sys, os, base64, struct, tempfile
sys.path.insert(0, os.path.dirname(__file__))

from swf_to_n2d import parse_swf, N2DBuilder
from swf_font_to_ttf import swf_font_to_ttf, _parse_define_font3_full

# Set N2F_TEST_SWF env var or replace this path with your local SWF file
SSF = os.environ.get('N2F_TEST_SWF', r'\path\to\your.swf')
with open(SSF, 'rb') as f:
    data = f.read()
header, tags = parse_swf(data)
builder = N2DBuilder(header, name='test')
builder.catalog_swf_tags(tags)

for cid, (tt, body) in builder.raw_tag_data.items():
    if builder.char_types.get(cid) == 'font':
        info = _parse_define_font3_full(body, tt)
        print(f"Font cid={cid}: name={info['font_name']}, glyphs={info['num_glyphs']}, "
              f"codes={len(info['code_table'])}, has_layout={info['has_layout']}, "
              f"ascent={info['ascent']}, descent={info['descent']}")
        print(f"  code_table: {[chr(c) for c in info['code_table'][:30]]}")
        print(f"  advances: {info['advance_table'][:10]}")
        shapes = info['glyph_shapes']
        non_empty = sum(1 for s in shapes if s)
        print(f"  shapes: {len(shapes)} total, {non_empty} non-empty")
        if shapes and shapes[0]:
            print(f"  glyph[0] sample: {shapes[0][0][:3]}...")

        try:
            ttf_bytes = swf_font_to_ttf(body, tt)
            ttf_path = os.path.join(tempfile.gettempdir(), f"swf_font_{cid}.ttf")
            with open(ttf_path, 'wb') as f:
                f.write(ttf_bytes)
            print(f"  TTF: {len(ttf_bytes)} bytes -> {ttf_path}")
            
            # Validate the TTF
            from fontTools.ttLib import TTFont
            font_obj = TTFont(ttf_path)
            cmap = font_obj.getBestCmap()
            print(f"  cmap entries: {len(cmap)}")
            glyf = font_obj['glyf']
            non_empty_glyphs = 0
            for gname in font_obj.getGlyphOrder():
                g = glyf[gname]
                if hasattr(g, 'numberOfContours') and g.numberOfContours > 0:
                    non_empty_glyphs += 1
            print(f"  non-empty glyphs in TTF: {non_empty_glyphs}")

        except Exception as e:
            print(f"  TTF ERROR: {e}")
            import traceback
            traceback.print_exc()
        print()
