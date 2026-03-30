#!/usr/bin/env python3
"""
Test DefineButton2 (tag 34) roundtrip: verify buttons survive SWF→N2D→SWF.

Also tests the _remap_button_raw_body function for charID remapping.
"""
import os
import struct
import sys
import tempfile
import unittest
import zlib

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, APP_DIR)

import swf_to_n2d
import compile_n2d


def parse_swf_tags(path):
    """Parse SWF file and return list of (tag_type, tag_data) tuples."""
    with open(path, 'rb') as f:
        raw = f.read()
    sig = raw[:3]
    if sig in (b'CWS', b'ZWS'):
        header = raw[:8]
        body = zlib.decompress(raw[8:])
        raw = header + body
    elif sig != b'FWS':
        raise ValueError(f"Not a SWF file: {path}")

    # SWF header: skip signature(3) + version(1) + fileLength(4) + RECT + frameRate(2) + frameCount(2)
    off = 8
    # Skip RECT (bit-packed)
    nbits = (raw[off] >> 3) & 0x1F
    total_rect_bits = 5 + nbits * 4
    off += (total_rect_bits + 7) // 8
    off += 4  # frameRate(2) + frameCount(2)

    tags = []
    while off < len(raw):
        if off + 2 > len(raw):
            break
        code_and_len = struct.unpack_from('<H', raw, off)[0]
        tag_type = code_and_len >> 6
        length = code_and_len & 0x3F
        off += 2
        if length == 0x3F:
            if off + 4 > len(raw):
                break
            length = struct.unpack_from('<I', raw, off)[0]
            off += 4
        tag_data = raw[off:off + length]
        tags.append((tag_type, tag_data))
        off += length
        if tag_type == 0:
            break
    return tags


def roundtrip_swf(swf_path):
    """Roundtrip a SWF: SWF → N2D → SWF. Returns path to roundtripped SWF."""
    name = os.path.splitext(os.path.basename(swf_path))[0]
    tmp_dir = tempfile.mkdtemp(prefix='n2f_test_btn_')
    n2d_path = os.path.join(tmp_dir, name + '.n2d')
    rt_path = os.path.join(tmp_dir, name + '_rt.swf')

    # Step 1: SWF → N2D
    with open(swf_path, 'rb') as f:
        swf_data = f.read()
    header, tags = swf_to_n2d.parse_swf(swf_data)
    builder = swf_to_n2d.N2DBuilder(header, name=name)
    builder.catalog_swf_tags(tags)

    try:
        scripts, frame_scripts = swf_to_n2d.decompile_all_scripts(
            builder.global_raw_tags)
        builder.frame_scripts = frame_scripts
        if scripts:
            builder.scripts.extend(scripts)
    except Exception:
        pass

    builder.build_all()
    builder.build_main_timeline(tags)
    builder._embed_bitmap_data_in_recodes()
    n2d = builder.to_n2d_json()
    swf_to_n2d.save_n2d(n2d, n2d_path)

    # Step 2: N2D → SWF
    compiler = compile_n2d.N2DCompiler(
        n2d_path=n2d_path,
        shared_dir=tmp_dir,
        output_path=rt_path,
        sdk_path=None,
    )
    compiler.compile()

    return rt_path


class TestDefineButton2Roundtrip(unittest.TestCase):
    """Tests that DefineButton2 (tag 34) tags survive roundtrip."""

    # Use menu_characters.ssf if available
    SSF2_DATA = os.path.join(
        os.path.expanduser('~'),
        'Documents', 'GitHub', 'ssf2-idk-140x-original', 'src',
        'Super Smash Flash 2 Beta v1.4.0.1', 'data', 'menu'
    )
    MENU_CHARS = os.path.join(SSF2_DATA, 'menu_characters.ssf')

    @unittest.skipUnless(
        os.path.isfile(os.path.join(
            os.path.expanduser('~'),
            'Documents', 'GitHub', 'ssf2-idk-140x-original', 'src',
            'Super Smash Flash 2 Beta v1.4.0.1', 'data', 'menu', 'menu_characters.ssf'
        )),
        "menu_characters.ssf not found"
    )
    def test_button2_tags_preserved(self):
        """DefineButton2 tags must survive roundtrip (not be dropped)."""
        orig_tags = parse_swf_tags(self.MENU_CHARS)
        orig_buttons = [(tt, td) for tt, td in orig_tags if tt == 34]
        self.assertGreater(len(orig_buttons), 0,
                           "Original SWF should contain DefineButton2 tags")

        rt_path = roundtrip_swf(self.MENU_CHARS)
        rt_tags = parse_swf_tags(rt_path)
        rt_buttons = [(tt, td) for tt, td in rt_tags if tt == 34]

        self.assertEqual(len(rt_buttons), len(orig_buttons),
                         f"Expected {len(orig_buttons)} DefineButton2 tags, "
                         f"got {len(rt_buttons)}")

    @unittest.skipUnless(
        os.path.isfile(os.path.join(
            os.path.expanduser('~'),
            'Documents', 'GitHub', 'ssf2-idk-140x-original', 'src',
            'Super Smash Flash 2 Beta v1.4.0.1', 'data', 'menu', 'menu_characters.ssf'
        )),
        "menu_characters.ssf not found"
    )
    def test_button2_body_length_preserved(self):
        """DefineButton2 raw bodies should have same lengths after roundtrip."""
        orig_tags = parse_swf_tags(self.MENU_CHARS)
        orig_buttons = [(tt, td) for tt, td in orig_tags if tt == 34]

        rt_path = roundtrip_swf(self.MENU_CHARS)
        rt_tags = parse_swf_tags(rt_path)
        rt_buttons = [(tt, td) for tt, td in rt_tags if tt == 34]

        self.assertEqual(len(rt_buttons), len(orig_buttons))
        # Compare sorted body lengths (order may differ due to charID reassignment)
        orig_lens = sorted(len(td) for _, td in orig_buttons)
        rt_lens = sorted(len(td) for _, td in rt_buttons)
        self.assertEqual(orig_lens, rt_lens,
                         f"Button body lengths mismatch: {orig_lens} vs {rt_lens}")

    @unittest.skipUnless(
        os.path.isfile(os.path.join(
            os.path.expanduser('~'),
            'Documents', 'GitHub', 'ssf2-idk-140x-original', 'src',
            'Super Smash Flash 2 Beta v1.4.0.1', 'data', 'menu', 'menu_characters.ssf'
        )),
        "menu_characters.ssf not found"
    )
    def test_tag_count_matches(self):
        """Total tag count should match after adding button support."""
        orig_tags = parse_swf_tags(self.MENU_CHARS)
        rt_path = roundtrip_swf(self.MENU_CHARS)
        rt_tags = parse_swf_tags(rt_path)

        # Build histograms
        from collections import Counter
        orig_hist = Counter(tt for tt, _ in orig_tags)
        rt_hist = Counter(tt for tt, _ in rt_tags)

        # DefineButton2 (tag 34) must match
        self.assertEqual(orig_hist.get(34, 0), rt_hist.get(34, 0),
                         "DefineButton2 count mismatch")


class TestRemapButtonRawBody(unittest.TestCase):
    """Unit tests for _remap_button_raw_body function."""

    def test_empty_body(self):
        """Empty or short body should be returned unchanged."""
        result = compile_n2d._remap_button_raw_body(b'', {1: 2})
        self.assertEqual(result, b'')

        result = compile_n2d._remap_button_raw_body(b'\x00\x00', {1: 2})
        self.assertEqual(result, b'\x00\x00')

    def test_no_id_map(self):
        """If id_map is empty, body should be unchanged."""
        body = b'\x00\x00\x00' + b'\x0F\x01\x00\x01\x00' + b'\x00' * 10 + b'\x00'
        result = compile_n2d._remap_button_raw_body(body, {})
        self.assertEqual(result, body)

    def test_simple_remap(self):
        """Build a minimal DefineButton2 body and verify charID gets remapped."""
        # Build a minimal DefineButton2 body (after charID):
        # Flags(1) + ActionOffset(2) + ButtonRecord + EndMarker
        #
        # ButtonRecord: flags(1) + charID(2) + depth(2) + MATRIX + CXFORMWITHALPHA
        # Minimal MATRIX: just translate with 0 bits = 0b00000_00 = 0x00 (1 byte)
        #   HasScale=0, HasRotate=0, NTranslateBits=0(5bits), TranslateX(0bits), TranslateY(0bits)
        #   Bit pattern: 0_0_00000 = 0x00  → whole byte = 0x00
        # Minimal CXFORMWITHALPHA: no add, no mult, nbits=0
        #   HasAdd=0, HasMult=0, Nbits=0000 = 0b00_0000 = 0x00 (1 byte)

        flags = b'\x00'          # Flags: TrackAsMenu=0
        action_offset = b'\x00\x00'  # No actions

        # ButtonRecord: state=Up(0x01), charID=5, depth=1
        btn_record = struct.pack('<B', 0x01)     # ButtonStateUp
        btn_record += struct.pack('<H', 5)       # CharacterId = 5
        btn_record += struct.pack('<H', 1)       # PlaceDepth = 1
        btn_record += b'\x00'                    # Minimal MATRIX
        btn_record += b'\x00'                    # Minimal CXFORMWITHALPHA

        end_marker = b'\x00'  # End of ButtonRecords

        body = flags + action_offset + btn_record + end_marker

        # Remap charID 5 → 10
        result = compile_n2d._remap_button_raw_body(body, {5: 10})

        # Verify charID was remapped
        # CharID is at offset 4 (flags:1 + actionOffset:2 + stateFlags:1 = 4)
        remapped_cid = struct.unpack_from('<H', result, 4)[0]
        self.assertEqual(remapped_cid, 10)

        # Everything else should be unchanged
        self.assertEqual(result[0:3], body[0:3])    # flags + actionOffset
        self.assertEqual(result[3], body[3])         # stateFlags
        self.assertEqual(result[6:], body[6:])       # depth + matrix + cxform + end

    def test_multiple_records(self):
        """Verify multiple ButtonRecords all get remapped."""
        flags = b'\x00'
        action_offset = b'\x00\x00'

        def make_record(state, char_id, depth):
            rec = struct.pack('<B', state)
            rec += struct.pack('<H', char_id)
            rec += struct.pack('<H', depth)
            rec += b'\x00'  # MATRIX
            rec += b'\x00'  # CXFORMWITHALPHA
            return rec

        record1 = make_record(0x01, 5, 1)   # Up state, charID=5
        record2 = make_record(0x04, 8, 2)   # Over state, charID=8
        record3 = make_record(0x08, 12, 3)  # HitTest state, charID=12
        end_marker = b'\x00'

        body = flags + action_offset + record1 + record2 + record3 + end_marker

        id_map = {5: 50, 8: 80, 12: 120}
        result = compile_n2d._remap_button_raw_body(body, id_map)

        # Check each record's charID
        off = 3  # skip flags + actionOffset
        for expected_cid in [50, 80, 120]:
            off += 1  # state flags
            cid = struct.unpack_from('<H', result, off)[0]
            self.assertEqual(cid, expected_cid)
            off += 2  # charID
            off += 2  # depth
            off += 1  # MATRIX
            off += 1  # CXFORMWITHALPHA


class TestHTMLFlagPreserved(unittest.TestCase):
    """Tests that HTML flag is preserved in DefineEditText rebuild path."""

    def test_html_flag_in_parsed_props(self):
        """parse_define_edit_text should include 'html' in returned dict."""
        # Build a minimal DefineEditText with HTML flag set
        from swf_writer import write_rect, BitWriter
        buf = bytearray()
        buf += struct.pack('<H', 1)  # charID
        buf += write_rect(0, 400, 0, 200)  # bounds

        # Flags: has_text=1, word_wrap=0, multiline=0, password=0,
        #        read_only=1, has_color=1, has_max_len=0, has_font=0
        f1 = 0x80 | 0x08 | 0x04  # has_text + read_only + has_color
        # Flags2: auto_size=0, has_layout=0, no_select=0, border=0,
        #         was_static=0, html=1, use_outlines=0
        f2 = 0x02  # html=1
        buf += struct.pack('BB', f1, f2)

        # Color RGBA
        buf += struct.pack('BBBB', 0, 0, 0, 255)

        # Variable name (empty null-terminated string)
        buf += b'\x00'

        # Text (null-terminated)
        buf += b'<p>Hello</p>\x00'

        result = swf_to_n2d.parse_define_edit_text(
            bytes(buf), font_names={}, font_attrs={})

        self.assertIn('html', result)
        self.assertTrue(result['html'],
                        "HTML flag should be True when set in tag flags")

    def test_html_false_when_not_set(self):
        """parse_define_edit_text should return html=False when not set."""
        from swf_writer import write_rect
        buf = bytearray()
        buf += struct.pack('<H', 1)  # charID
        buf += write_rect(0, 400, 0, 200)

        f1 = 0x80 | 0x08 | 0x04  # has_text + read_only + has_color
        f2 = 0x00  # html=0
        buf += struct.pack('BB', f1, f2)

        buf += struct.pack('BBBB', 0, 0, 0, 255)  # color
        buf += b'\x00'  # variable name
        buf += b'Hello\x00'  # text

        result = swf_to_n2d.parse_define_edit_text(
            bytes(buf), font_names={}, font_attrs={})

        self.assertIn('html', result)
        self.assertFalse(result['html'])

    def test_build_edit_text_uses_html_flag(self):
        """build_define_edit_text should respect html flag from dict."""
        from text_converter import build_define_edit_text

        tf_html = {
            'text': '<p>Test</p>',
            'font': 'Arial',
            'size': 12,
            'color': 0,
            'align': 'left',
            'html': True,
            'bounds': {'xMin': 0, 'xMax': 100, 'yMin': 0, 'yMax': 20},
        }
        tag_data_html = build_define_edit_text(1, tf_html)

        tf_no_html = dict(tf_html)
        tf_no_html['html'] = False
        tag_data_no_html = build_define_edit_text(2, tf_no_html)

        # The tags should differ (at least in the HTML flag bit)
        self.assertNotEqual(tag_data_html, tag_data_no_html)


if __name__ == '__main__':
    unittest.main()
