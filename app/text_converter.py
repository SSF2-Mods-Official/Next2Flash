"""
TextField Converter — Translates Next2D ITextFieldCharacter to SWF DefineEditText.
"""

from __future__ import annotations

import io
import logging
import struct
from typing import Optional

log = logging.getLogger(__name__)

from swf_writer import (
    BitWriter,
    TAG_DEFINE_EDIT_TEXT,
    build_tag,
    twips,
    write_rect,
)


def build_define_edit_text(
    char_id: int,
    tf: dict,
) -> bytes:
    """
    Build a DefineEditText (tag 37) from a Next2D ITextFieldCharacter dict.

    SWF DefineEditText fields reference:
    https://open-flash.github.io/mirrors/swf-spec-19.pdf  §p.197
    """
    log.debug("build_define_edit_text: char_id=%d font=%s size=%s", char_id, tf.get('font'), tf.get('size'))
    bounds = tf.get("bounds", {})
    xmin = twips(bounds.get("xMin", 0))
    xmax = twips(bounds.get("xMax", 200))
    ymin = twips(bounds.get("yMin", 0))
    ymax = twips(bounds.get("yMax", 30))

    text = tf.get("text", "")
    font_name = tf.get("font", "Arial")
    font_size = tf.get("size", 12)
    color_int = int(tf.get("color", 0))
    align = tf.get("align", "left")         # "left" | "center" | "right"
    leading = tf.get("leading", 0)
    letter_spacing = tf.get("letterSpacing", 0)
    left_margin = tf.get("leftMargin", 0)
    right_margin = tf.get("rightMargin", 0)
    font_type = tf.get("fontType", 0)       # 0=normal, 1=bold, 2=italic, 3=bold+italic
    auto_size_val = tf.get("autoSize", 0)    # 0=none, 1=autoSize, 2=autoFontSize
    input_type = tf.get("inputType", "static")  # "input" | "static" | "dynamic"
    multiline = tf.get("multiline", False)
    word_wrap = tf.get("wordWrap", False)
    border = tf.get("border", False)
    scroll = tf.get("scroll", False)
    thickness = tf.get("thickness", 0)
    thickness_color = tf.get("thicknessColor", 0)

    # ── Flags ──
    has_text = len(text) > 0
    has_text_color = True
    has_max_length = False
    has_font = True
    has_font_class = False
    auto_size = auto_size_val > 0
    has_layout = True
    no_select = (input_type == "static")
    read_only = (input_type != "input")
    html = False
    use_outlines = True
    was_static = (input_type == "static")
    password = False

    # Color RGBA
    r = (color_int >> 16) & 0xFF
    g = (color_int >> 8) & 0xFF
    b = color_int & 0xFF
    a = 255

    # Alignment
    align_map = {"left": 0, "right": 1, "center": 2, "justify": 3}
    align_val = align_map.get(align, 0)

    # ── Build body ──
    body = io.BytesIO()
    body.write(struct.pack("<H", char_id))

    # Bounds RECT
    body.write(write_rect(xmin, xmax, ymin, ymax))

    # Flags (2 bytes, big-endian-ish within each byte per SWF spec)
    flags1 = 0
    if has_text:         flags1 |= 0x80
    if word_wrap:        flags1 |= 0x40
    if multiline:        flags1 |= 0x20
    if password:         flags1 |= 0x10
    if read_only:        flags1 |= 0x08
    if has_text_color:   flags1 |= 0x04
    if has_max_length:   flags1 |= 0x02
    if has_font:         flags1 |= 0x01

    flags2 = 0
    if has_font_class:   flags2 |= 0x80
    if auto_size:        flags2 |= 0x40
    if has_layout:       flags2 |= 0x20
    if no_select:        flags2 |= 0x10
    if border:           flags2 |= 0x08
    if was_static:       flags2 |= 0x04
    if html:             flags2 |= 0x02
    if use_outlines:     flags2 |= 0x01

    body.write(struct.pack("<BB", flags1, flags2))

    # FontID (UI16) — we'll use char_id + 1000 as a font ID placeholder
    if has_font:
        body.write(struct.pack("<H", 0))  # FontID = 0 (use device font)

    # FontHeight (UI16) in twips
    if has_font:
        body.write(struct.pack("<H", twips(font_size)))

    # TextColor RGBA
    if has_text_color:
        body.write(struct.pack("<BBBB", r, g, b, a))

    # MaxLength
    if has_max_length:
        body.write(struct.pack("<H", 0))

    # Layout
    if has_layout:
        body.write(struct.pack("<B", align_val))
        body.write(struct.pack("<H", twips(left_margin)))
        body.write(struct.pack("<H", twips(right_margin)))
        body.write(struct.pack("<H", 0))  # indent
        body.write(struct.pack("<h", twips(leading)))  # signed

    # VariableName (always empty string)
    body.write(b"\x00")

    # InitialText
    if has_text:
        body.write(text.encode("utf-8") + b"\x00")

    return build_tag(TAG_DEFINE_EDIT_TEXT, body.getvalue())
